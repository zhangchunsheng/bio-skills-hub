---
slug: bio-copy-number-integrated
version: 1.0.1
displayName: "拷贝数变异分析 / Copy number variation analysis"
name: bio-copy-number-integrated
summary: "中文：拷贝数变异分析综合技能，整合 11 个相关专题，覆盖拷贝数变异分析：CNVkit、GATK gCNV、ASCAT、FACETS、GISTIC2、HRD评分、ecDNA解析。 English: Integrated Copy number variation analysis skill covering 11 related topics, including Copy number variation analysis: CNVkit, GATK gCNV, ASCAT, FACETS, GISTIC2, HRD scoring, ecDNA architecture."
description: "中文：这是一个面向拷贝数变异分析的综合生物信息学 Skill，整合当前分类下 11 个相关专题能力。它用于根据研究问题、数据类型和分析阶段，选择合适的方法与工具，规划从输入检查、预处理、核心分析到质量控制、统计解释和结果报告的完整流程。重点覆盖：拷贝数变异分析：CNVkit、GATK gCNV、ASCAT、FACETS、GISTIC2、HRD评分、ecDNA解析。当用户提供相关实验数据、测序结果、表格或研究问题时，它会帮助判断分析目标与前置条件，给出工具选择、关键参数、输入输出、常见失败原因、结果解读和可复现建议。主要工具包括：AmpliconArchitect, ClassifyCNV, DNAcopy。该 Skill 提供分析设计与实施指导，不替代对具体数据质量、生物学背景和最终结论的人工审查。 English: This is an integrated bioinformatics Skill for Copy number variation analysis, combining 11 related topic areas. It helps users choose appropriate methods and tools based on the research question, data type, and analysis stage, and plan an end-to-end workflow from input validation and preprocessing through core analysis, quality control, statistical interpretation, and reporting. It covers Copy number variation analysis: CNVkit, GATK gCNV, ASCAT, FACETS, GISTIC2, HRD scoring, ecDNA architecture. For relevant experimental data, sequencing results, tables, or research questions, it clarifies prerequisites, recommends tools and parameters, describes expected inputs and outputs, explains common failure modes, and supports reproducible analysis. Primary tools include: AmpliconArchitect, ClassifyCNV, DNAcopy. It provides methodological and implementation guidance; final data-quality assessment and biological conclusions still require human review."
---

# copy-number 分类 Skill 整合版

> 本文件整合同一主分类目录下 11 个子目录中的 SKILL.md 内容。
> 各子目录正文按原文保留，并通过标题和边界标记进行区分；源文件中的元数据块未被改写。

---

<!-- BEGIN CATEGORY: copy-number -->

## 子目录：copy-number/allele-specific-copy-number

<!-- BEGIN FILE: copy-number/allele-specific-copy-number/SKILL.md -->
---
name: bio-copy-number-allele-specific-copy-number
description: Infer integer allele-specific copy number, tumor purity, and ploidy from tumor sequencing by jointly modeling read depth (logR) and B-allele frequency (BAF) with ASCAT, Sequenza, FACETS, PURPLE, and PureCN (tumor-only). Covers the purity-ploidy identifiability problem, the diploid-baseline (dipLogR) anchor, major/minor copy number, loss of heterozygosity, sunrise/contour fit diagnostics, and reconciliation of conflicting fits. Use when tumor analysis needs absolute copy number rather than relative log2, when estimating purity and ploidy, calling LOH or copy-neutral LOH, resolving whole-genome doubling, running tumor-only allele-specific calling, or choosing among ASCAT, Sequenza, FACETS, and PureCN.
tool_type: mixed
primary_tool: ascat
---

## Version Compatibility

Reference examples tested with: ASCAT 3.1+, Sequenza 3.0+ (sequenza-utils 3.0+), FACETS 0.6+ (snp-pileup), PureCN 2.6+, R 4.3+, Python 3.10+.

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('ASCAT')` / `'sequenza'` / `'facets'` / `'PureCN'`, then `?function`
- CLI: `sequenza-utils --version`, `snp-pileup --help`

Sequenza 3.0 depends on the `copynumber` Bioconductor package, REMOVED from Bioconductor 3.18+ (2023). Install a maintained fork (`ShixiangWang/copynumber` or `igordot/copynumber`) before Sequenza will load. ASCAT's GC-correction function was renamed across 2.x->3.x (`ascat.GCcorrect` -> `ascat.correctLogR`) — verify against the installed version.

# Allele-Specific Copy Number

**"How many copies of each allele, in what fraction of cells, at what tumor purity"** -> Jointly model read depth and B-allele frequency to fit tumor purity, ploidy, and integer major/minor copy number per segment. Depth alone gives only *relative* copy ratio; depth + BAF gives *absolute* allele-specific copy number. This skill is required whenever the question involves LOH, absolute copy number, purity, ploidy, or whole-genome doubling — CNVkit and GATK somatic CNV cannot answer those.

- R: `ASCAT` (WGS, SNP array), `sequenza` (WES/WGS), `facets` (panel/WES/WGS), `PureCN` (tumor-only panel/WES)
- CLI: `purple` (Hartwig WGS pipeline, with AMBER + COBALT)

## The Identifiability Problem — Why This Is Hard

Purity and ploidy are **not identifiable from depth alone**. The same log-ratio profile is explained equally well by many (purity, ploidy) pairs: a homozygous deletion at 30% purity looks identical to a heterozygous deletion at 60% purity; an entire profile can be reinterpreted at 2x ploidy with halved purity. Every allele-specific caller breaks this degeneracy by adding BAF — allelic imbalance constrains which solution is real. The consequence: the likelihood surface is **multimodal**, the fit can lock onto an integer-multiple of the true ploidy, and a single point estimate must never be trusted without inspecting the fit diagnostic (ASCAT sunrise plot, Sequenza cellularity/ploidy contour, FACETS dipLogR). A documented example: the same tumor scored ploidy 4.27 by FACETS (WGS) and 2.42 by ASCAT (SNP array).

## Caller Taxonomy

| Tool | Input | Segmentation | Best for | Fails when |
|------|-------|--------------|----------|------------|
| ASCAT | SNP array or WGS logR+BAF | ASPCF (allele-specific PCF) | WGS, SNP6, large cohorts | Near-diploid genome with few aberrations cannot anchor purity -> defaults toward purity ~100% |
| Sequenza | Tumor-normal WES/WGS (seqz) | `copynumber` PCF | Exome, accessible install | Picks a near-diploid local optimum; needs manual review of alternative solutions |
| FACETS | Tumor-normal, snp-pileup | Joint logR+BAF CBS | Targeted panels, WES, clinical NGS | `cval` too low -> hyperfragmentation; EM locks onto an integer-multiple ploidy |
| PURPLE | WGS, AMBER+COBALT+SVs | Integrates SV breakpoints | WGS with matched SV calls | Targeted/WES (designed for WGS); needs the Hartwig tool stack |
| PureCN | Tumor-only WES/panel + PoN | Coverage + VCF, normal DB | No matched normal | Sparse hets; small panels; needs a well-built normal database |
| Battenberg | WGS logR+BAF, phased | ASCAT-based clonal + subclonal | Subclonal CN, clonal evolution | Heavy; needs phasing reference — see subclonal-copy-number |

## Decision Tree by Data Type

| Scenario | Recommended caller | Rationale |
|----------|--------------------|-----------|
| Tumor-normal WGS | ASCAT or PURPLE | PURPLE if SV calls available (resolves breakpoints); ASCAT otherwise |
| Tumor-normal WES | Sequenza or FACETS | Both joint logR+BAF; FACETS faster, Sequenza reports alternative solutions |
| Targeted panel (tumor-normal) | FACETS | Designed for panel het density; clinical-NGS standard |
| Tumor-only panel / WES | PureCN | Models a normal database; the standard tumor-only solution |
| SNP array (legacy) | ASCAT | ASCAT was built for SNP arrays |
| Subclonal CN / clonal evolution | Battenberg / TITAN | See subclonal-copy-number |
| Only relative gain/loss needed | CNVkit / GATK | Allele-specific machinery is unnecessary |

## FACETS — Tumor-Normal Allele-Specific CN

**Goal:** Fit purity, ploidy, and integer allele-specific CN for a panel or WES pair.

**Approach:** Pile up read counts at common SNPs with `snp-pileup`, then run the two-pass FACETS workflow — a high-`cval` purity run whose `dipLogR` seeds a low-`cval` sensitivity run for focal events.

```bash
# Step 1: pileup at dbSNP common sites (normal first, then tumor)
snp-pileup -g -q15 -Q20 -P100 -r25,0 dbsnp_common.vcf.gz \
    sample.snp_pileup.csv.gz normal.bam tumor.bam
```

```r
library(facets)
set.seed(1234)                                  # FACETS uses random initialization
rcmat <- readSnpMatrix('sample.snp_pileup.csv.gz')
xx <- preProcSample(rcmat)                      # gbuild default 'hg19'; pass gbuild='hg38' for GRCh38

# Pass 1: purity/ploidy at a coarse cval (panels ~150-300; WGS ~25-100)
oo1 <- procSample(xx, cval = 300)
fit1 <- emcncf(oo1)

# Pass 2: focal sensitivity, seeded by the diploid baseline from pass 1
oo2 <- procSample(xx, cval = 150, dipLogR = oo1$dipLogR)
fit2 <- emcncf(oo2)

cat('purity', fit2$purity, 'ploidy', fit2$ploidy, 'dipLogR', oo2$dipLogR, '\n')
# fit2$cncf has per-segment tcn.em (total CN) and lcn.em (minor CN); lcn.em == 0 -> LOH
plotSample(x = oo2, emfit = fit2)               # ALWAYS inspect this diagnostic plot
```

## Sequenza — Exome Tumor-Normal

**Goal:** Estimate cellularity/ploidy and allele-specific CN from a WES pair, with explicit alternative solutions.

**Approach:** Build a `seqz` file from the BAMs, bin it, then run the extract/fit/results chain; inspect the cellularity/ploidy contour and the reported alternative solutions.

```bash
sequenza-utils bam2seqz -n normal.bam -t tumor.bam --fasta ref.fa \
    -gc hg38.gc50.wig.gz -o sample.seqz.gz
sequenza-utils seqz_binning --seqz sample.seqz.gz -w 50 -o sample.bin.seqz.gz
```

```r
library(sequenza)
seqz <- sequenza.extract('sample.bin.seqz.gz')
CP <- sequenza.fit(seqz)                        # grid search over cellularity x ploidy
sequenza.results(seqz, CP, 'sampleID', out.dir = 'sequenza_out')
# Inspect *_CP_contours.pdf and *_alternative_solutions.txt before accepting the fit.
```

## ASCAT — WGS / SNP Array

**Goal:** Fit purity (rho), ploidy (psi), and allele-specific CN genome-wide.

**Approach:** Load logR/BAF, correct for GC (and optionally replication timing), segment with ASPCF, run the ASCAT fit, and read the sunrise plot.

```r
library(ASCAT)
ascat.bc <- ascat.loadData('Tumor_LogR.txt', 'Tumor_BAF.txt',
                           'Germline_LogR.txt', 'Germline_BAF.txt')
ascat.bc <- ascat.correctLogR(ascat.bc, GCcontentfile = 'GC_G1000.txt',
                              replictimingfile = 'RT_G1000.txt')   # RT optional
ascat.bc <- ascat.aspcf(ascat.bc)
ascat.output <- ascat.runAscat(ascat.bc, gamma = 1)   # gamma=1 for NGS; ~0.55 for arrays
# ascat.output$purity, $ploidy, $goodnessOfFit; $nA / $nB are major/minor CN per segment
# Inspect the sunrise plot: banding at multiples of ploidy signals an ambiguous fit.
```

## PureCN — Tumor-Only

**Goal:** Recover purity, ploidy, allele-specific CN, and LOH without a matched normal.

**Approach:** Build a normal database (PoN) once, then run `runAbsoluteCN` with the tumor coverage and a VCF; PureCN uses the normal DB and a mapping-bias model in place of a matched normal.

```r
library(PureCN)
ret <- runAbsoluteCN(
    tumor.coverage.file = 'tumor_coverage.txt.gz',
    vcf.file = 'tumor.vcf.gz',
    normalDB = readRDS('normalDB.rds'),       # built once from >= ~20 process-matched normals
    genome = 'hg38', sampleid = 'tumor',
    interval.file = 'baits_intervals.txt')
# ret$results[[1]]$purity / $ploidy; createCurationFile() flags fits needing manual review
```

## Failure Modes

### ASCAT defaults to ~100% purity on a near-diploid genome

**Trigger:** A tumor with very few copy-number aberrations and overall ploidy near 2.

**Mechanism:** ASCAT infers purity from the depth/BAF deviation of aberrant segments. With almost no aberrant segments there is nothing to anchor purity against, so the grid search drifts to the boundary.

**Symptom:** Reported purity ~1.0 (or implausibly high) with an almost flat profile; the sunrise plot is nearly featureless.

**Fix:** Treat purity as indeterminate, not 100%. Cross-check with an orthogonal estimate (SNV VAF mode for clonal mutations, pathology estimate). A genuinely quiet genome simply does not support a confident purity call.

### FACETS hyperfragmentation from too-low cval

**Trigger:** `cval` set too low for the data (e.g. panel data run at WGS-scale cval).

**Mechanism:** `cval` is the segmentation critical value; low values let the segmenter split on noise, shattering the profile into spurious micro-segments.

**Symptom:** Hundreds of tiny segments; `tcn.em`/`lcn.em` incoherent with `cnlr.median`; jagged `plotSample` output.

**Fix:** Use cval ~150-300 for panels/WES, ~25-100 for WGS. Run the two-pass workflow (coarse purity run -> dipLogR-seeded sensitivity run). If naive `tcn` and EM `tcn.em` disagree wildly, the fit is bad — re-tune cval.

### Integer-multiple ploidy flip

**Trigger:** Any allele-specific caller on a genome where the diploid baseline is ambiguous (few hets, low purity, or genuine WGD).

**Mechanism:** The likelihood surface has near-equal modes at ploidy P and 2P; the optimizer can select the wrong one, halving or doubling all copy numbers.

**Symptom:** Two callers disagree by a factor of ~2 in ploidy; "balanced" CN states that should be odd come out even (or vice versa); SNV multiplicities inconsistent with the called CN.

**Fix:** Inspect the fit diagnostic (sunrise/contour). Cross-check ploidy against the fraction of the genome at odd vs even CN and against clonal-SNV VAF. Prefer the solution consistent with known biology; if truly ambiguous, report both.

### Sequenza fails to load / picks a near-diploid optimum

**Trigger:** Fresh Sequenza install on Bioconductor 3.18+; or accepting `sequenza.fit`'s point estimate without review.

**Mechanism:** Sequenza depends on `copynumber`, removed from Bioconductor 3.18+. Separately, the LPP grid search can settle on a near-diploid local optimum when a higher-ploidy solution fits comparably.

**Symptom:** `copynumber` not available at load; or a ploidy ~2 call that conflicts with visible large-scale imbalance.

**Fix:** Install a maintained `copynumber` fork. Always inspect `*_CP_contours.pdf` and `*_alternative_solutions.txt`; if a non-diploid alternative fits nearly as well and matches the BAF pattern, prefer it.

### Low-purity death zone

**Trigger:** Tumor purity below ~40% (common in breast, lung adenocarcinoma, melanoma).

**Mechanism:** Allelic imbalance and depth deviation both shrink with purity; below ~40% the signal approaches the noise floor and segmentation fails.

**Symptom:** No confident fit; purity estimate unstable across reruns; flat BAF.

**Fix:** Below ~40% purity, allele-specific calling is unreliable; below ~20% it is not possible with bulk sequencing. Report indeterminate; consider deeper sequencing or microdissection.

## Reconciliation: When Callers Disagree

| Pattern | Likely cause | Action |
|---------|--------------|--------|
| Caller A ploidy ~= 2x caller B | Integer-multiple ploidy flip | Check odd/even CN fraction and SNV multiplicity; pick the biology-consistent fit |
| Purity differs widely, ploidy agrees | One caller hit a boundary on a quiet genome | Trust the caller whose diagnostic plot shows real structure |
| FACETS vs ASCAT integer CN differ | Different segmentation (CBS vs ASPCF) at boundaries | Compare segment edges; arm-level calls usually agree, focal may not |
| Tumor-only (PureCN) vs tumor-normal differ | Tumor-only has weaker purity constraint | Prefer the matched-normal fit when available |

**Operational rule:** Report an allele-specific fit as confident only when (1) the fit diagnostic (sunrise/contour/dipLogR) shows clear, non-degenerate structure, (2) purity is above ~40%, (3) ploidy is consistent with the odd/even CN fraction and with clonal-SNV multiplicity, and (4) for ambiguous cases, the alternative solutions have been reviewed. A bare purity/ploidy number with no diagnostic inspection is not a result.

## Quantitative Thresholds

| Threshold | Value | Source / Rationale |
|-----------|-------|--------------------|
| Purity floor | ~40% reliable; ~20% absolute floor | Below ~40% segmentation fails (Gusnanto 2012; sCNAphase) |
| FACETS cval (panel/WES) | 150-300 | FACETS docs; lower -> hyperfragmentation |
| FACETS cval (WGS) | 25-100 | FACETS docs; scales with marker density |
| ASCAT gamma | 1.0 (NGS); ~0.55 (SNP array) | ASCAT docs; platform-specific logR shrinkage |
| LOH definition | minor CN (lcn) = 0 | Minor allele lost; total CN may still be >= 2 (CN-neutral LOH) |
| PureCN normal DB size | >= ~20 process-matched normals | PureCN docs; mapping-bias and coverage model |
| Het SNP density for stable BAF | thousands genome-wide / hundreds per arm | Sparse hets give noisy allele-fraction segmentation |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| Sequenza: `copynumber` not found | Removed from Bioconductor 3.18+ | Install a maintained `copynumber` fork |
| `ascat.GCcorrect` not found | Renamed in ASCAT 3.x | Use `ascat.correctLogR` |
| FACETS profile shattered | cval too low | Raise cval; two-pass workflow |
| Purity reported ~1.0, flat genome | Near-diploid, unanchored | Report indeterminate; cross-check with SNV VAF |
| All CN halved or doubled vs expectation | Integer-multiple ploidy flip | Inspect fit diagnostic; check SNV multiplicity |
| PureCN unstable tumor-only fit | Sparse hets / weak normal DB | Larger normal DB; deeper sequencing; flag for curation |

## References

- Van Loo P et al 2010. Allele-specific copy number analysis of tumors. PNAS 107:16910 (ASCAT)
- Ross EM et al 2021. Allele-specific multi-sample copy number segmentation in ASCAT. Bioinformatics 37:1909
- Favero F et al 2015. Sequenza: allele-specific copy number and mutation profiles from tumor sequencing data. Ann Oncol 26:64
- Shen R, Seshan VE 2016. FACETS: allele-specific copy number and clonal heterogeneity analysis. Nucleic Acids Res 44:e131
- Riester M et al 2016. PureCN: copy number calling and SNV classification using targeted short read sequencing. Source Code Biol Med 11:13
- Priestley P et al 2019. Pan-cancer whole-genome analyses of metastatic solid tumours (PURPLE). Nature 575:210

## Related Skills

- copy-number/copy-ratio-segmentation - logR normalization and segmentation feeding these callers
- copy-number/subclonal-copy-number - Battenberg/TITAN subclonal CN, whole-genome doubling
- copy-number/hrd-scoring - LOH/LST/TAI scars computed from allele-specific output
- copy-number/cnvkit-analysis - Relative depth-only calling (when allelic resolution is not needed)
- copy-number/gatk-cnv - GATK somatic CNV (relative; no purity/ploidy)
- variant-calling/vcf-basics - SNV VCFs supplying BAF and clonal-mutation cross-checks
<!-- END FILE: copy-number/allele-specific-copy-number/SKILL.md -->

## 子目录：copy-number/cnv-annotation

<!-- BEGIN FILE: copy-number/cnv-annotation/SKILL.md -->
---
name: bio-copy-number-cnv-annotation
description: Annotate copy number variant segments with overlapping genes, dosage-sensitivity scores, cancer driver databases, population frequencies, and clinical-variant content. Covers bedtools/pybedtools interval intersection, AnnotSV comprehensive annotation and ranking, ClinGen haploinsufficiency/triplosensitivity scoring, gnomAD-SV/DGV frequency filtering, COSMIC Cancer Gene Census, and ClinVar overlap. Use when interpreting which genes a CNV affects, distinguishing the driver gene of a focal event from passengers, filtering against population CNVs, separating whole-gene from partial-gene overlap, or preparing CNVs for clinical classification.
tool_type: mixed
primary_tool: bedtools
---

## Version Compatibility

Reference examples tested with: bedtools 2.31+, AnnotSV 3.4+, Python 3.10+ with pybedtools 0.9+, pandas 2.2+, pysam 0.22+; R 4.3+ with clusterProfiler 4.10+.

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `bedtools --version`, `AnnotSV --version`
- Python: `pip show pybedtools pandas pysam`
- R: `packageVersion('clusterProfiler')`

If code throws an error, introspect the installed package and adapt the example. AnnotSV output column names change between major versions — verify against the installed version.

# CNV Annotation

**"Annotate my CNV calls with the genes they affect"** -> Overlap CNV segments with gene models, dosage-sensitivity maps, and clinical databases. The hard part is not the intersection — it is deciding *which* genes matter. A focal amplification overlapping 30 genes usually has one driver (the peak gene); a deletion's consequence depends on whether each gene is dosage-sensitive and whether the whole gene or only part is removed.

- CLI: `bedtools intersect -a cnvs.bed -b genes.bed -wa -wb`; `AnnotSV` for full annotation
- Python: `pybedtools` for interval logic; `pysam` for VCF database queries

## Annotation Strategy — Pick the Database for the Question

| Question | Resource | What it answers |
|----------|----------|-----------------|
| Which genes does this CNV span? | RefSeq/GENCODE gene BED | Raw overlap (not yet consequence) |
| Is loss of this gene damaging? | ClinGen haploinsufficiency (HI) score | Dosage sensitivity to deletion |
| Is gain of this gene damaging? | ClinGen triplosensitivity (TS) score | Dosage sensitivity to duplication |
| Is this CNV common in the population? | gnomAD-SV, DGV, 1000G CNV | Benign-frequency filtering |
| Is this a known recurrent disorder locus? | ClinGen dosage regions, DECIPHER | Genomic-disorder context |
| Is this a cancer driver? | COSMIC Cancer Gene Census, OncoKB | Oncogene vs tumor-suppressor role |
| Is there pathogenic small-variant content? | ClinVar | Coincident SNV/indel pathogenicity |
| One-shot comprehensive annotation + ranking | AnnotSV | Aggregates most of the above |

For constitutional CNV *classification* (assigning pathogenic/VUS/benign), the annotated output feeds the ACMG/ClinGen points framework — see germline-cnv-interpretation. For cohort-level recurrence and driver-peak identification, see recurrent-cnv.

## The Core Distinction: Overlap Is Not Consequence

A CNV overlapping a gene does not necessarily change that gene's dosage in a way that matters. Three refinements separate annotation from interpretation:

1. **Whole-gene vs partial overlap.** A deletion spanning an entire gene removes one copy (clean haploinsufficiency test). A deletion removing only the last two exons creates a truncated allele — a different, often more damaging, consequence. Always record the fraction of each gene covered and whether coding exons or only introns/UTRs are hit.
2. **Dosage sensitivity.** Most genes tolerate single-copy loss. ClinGen HI/TS scores (3 = sufficient evidence for dosage sensitivity, 0 = no evidence, 30 = gene associated with an autosomal-recessive phenotype, 40 = dosage sensitivity unlikely) indicate which genes' loss/gain is actually consequential.
3. **Driver vs passenger in focal events.** A focal amplification carries many genes; the driver is the one under selection, typically at the recurrence peak across a cohort (GISTIC) and a known oncogene. Annotating all 30 genes as "amplified" overstates.

## Gene Overlap with bedtools

**Goal:** Find genes overlapping each CNV segment, recording overlap extent.

**Approach:** Convert segments to BED, intersect with a gene model, keep both feature sets (`-wo` reports the overlap length) so partial vs whole-gene overlap is recoverable.

```bash
# Segments to BED (CNVkit .cns example; columns chrom/start/end/log2)
awk 'NR>1 {print $1"\t"$2"\t"$3"\t"$5}' sample.cns > sample.cnv.bed

# Intersect; -wo appends the number of overlapping bases
bedtools intersect -a sample.cnv.bed -b gencode.genes.bed -wo > cnv_gene_overlap.txt
```

## Comprehensive Annotation with AnnotSV

**Goal:** Annotate CNVs against genes, dosage maps, population frequency, and clinical databases in one pass, with a built-in pathogenicity ranking.

**Approach:** Export CNVs to VCF or BED and run AnnotSV; it returns a "full" line per gene plus a "split" summary, with an ACMG-aligned rank (1-5).

```bash
AnnotSV \
    -SVinputFile sample.cnv.vcf \
    -genomeBuild GRCh38 \
    -annotationMode both \
    -outputFile sample_annotated.tsv

# Output includes: overlapped genes, ClinGen HI/TS, gnomAD-SV/DGV frequency, OMIM,
# ClinVar, DECIPHER, and an ACMG-class rank per SV.
```

AnnotSV's rank is a useful triage signal, not a final classification — confirm against the ClinGen points framework for clinical reporting.

## Dosage-Sensitivity and Driver Annotation

**Goal:** Tag each affected gene with its dosage sensitivity and, for tumors, its driver role, so passengers can be separated from drivers.

**Approach:** Join the gene-overlap table to the ClinGen dosage map (HI/TS scores) and to the COSMIC Cancer Gene Census; flag CNVs whose direction matches a known mechanism (oncogene amplified, tumor suppressor deleted).

```python
import pandas as pd

def annotate_dosage_and_drivers(overlap_tsv, clingen_dosage, cgc_file):
    '''Tag overlapped genes with ClinGen HI/TS and COSMIC driver role.'''
    cols = ['cnv_chrom', 'cnv_start', 'cnv_end', 'log2',
            'gene_chrom', 'gene_start', 'gene_end', 'gene', 'overlap_bp']
    df = pd.read_csv(overlap_tsv, sep='\t', names=cols)
    df['gene_len'] = df['gene_end'] - df['gene_start']
    df['gene_frac_covered'] = (df['overlap_bp'] / df['gene_len']).clip(upper=1.0)
    df['whole_gene'] = df['gene_frac_covered'] >= 0.99

    dosage = pd.read_csv(clingen_dosage, sep='\t')  # gene, HI_score, TS_score
    df = df.merge(dosage, on='gene', how='left')

    cgc = pd.read_csv(cgc_file, sep='\t')
    role = dict(zip(cgc['Gene Symbol'], cgc['Role in Cancer']))
    df['driver_role'] = df['gene'].map(role)

    # Direction-consistent driver hits: oncogene amplified or TSG deleted.
    df['driver_hit'] = (
        ((df['log2'] > 0.3) & df['driver_role'].fillna('').str.contains('oncogene')) |
        ((df['log2'] < -0.3) & df['driver_role'].fillna('').str.contains('TSG')))
    return df
```

## Population-Frequency Filtering

**Goal:** Remove common, presumed-benign CNVs before clinical interpretation.

**Approach:** Reciprocal-overlap match each CNV against a population SV catalog (gnomAD-SV, DGV); a CNV with high reciprocal overlap to a common population CNV of the same type is likely benign.

```bash
# 50% reciprocal overlap (-f 0.5 -r): same-type, similar-extent population match.
# Reciprocal overlap, not one-sided, prevents a tiny CNV inside a huge population CNV
# (or vice versa) from being wrongly matched.
bedtools intersect -a sample.cnv.bed -b gnomad_sv.bed -f 0.5 -r -wa -wb \
    > cnv_population_match.txt
```

## Pathway Enrichment of Affected Genes

**Goal:** Test whether genes in amplified (or deleted) regions are enriched for pathways.

**Approach:** Extract genes by CNV direction, map to Entrez IDs, run GO/KEGG enrichment. Caveat: CNVs are large and gene-dense, so enrichment is biased toward whatever pathways cluster in CNV-prone genomic regions — interpret as hypothesis-generating.

```r
library(clusterProfiler)
library(org.Hs.eg.db)

amp_genes <- unique(cnv_annot$gene[cnv_annot$log2 > 0.3])
entrez <- na.omit(mapIds(org.Hs.eg.db, keys = amp_genes,
                         keytype = 'SYMBOL', column = 'ENTREZID'))
go_bp <- enrichGO(gene = entrez, OrgDb = org.Hs.eg.db, ont = 'BP',
                  pAdjustMethod = 'BH', qvalueCutoff = 0.05)
```

## Failure Modes

### Genome-build mismatch between CNVs and annotation

**Trigger:** CNV coordinates on GRCh37 intersected with a GRCh38 gene model (or vice versa).

**Mechanism:** Coordinates silently shift; the intersection succeeds and returns wrong genes.

**Symptom:** Implausible gene assignments; a known driver locus annotated with the wrong gene; systematic offset.

**Fix:** Confirm both inputs are the same build. If not, liftOver the CNVs (note that liftOver can split or drop segments across assembly gaps) and verify a known landmark.

### Annotating all overlapped genes as the "affected" genes

**Trigger:** Reporting every gene a focal amplification spans as amplified/driver.

**Mechanism:** Focal events are megabases wide and gene-dense; only the selected gene is the driver.

**Symptom:** A 2 Mb amplicon "amplifies" 40 genes; the report cannot distinguish ERBB2 from its passengers.

**Fix:** For focal events, prioritize the gene at the cohort recurrence peak (GISTIC, see recurrent-cnv) and known drivers (CGC/OncoKB). Report passengers separately or not at all.

### ClinVar CLNSIG parsing errors

**Trigger:** Naive string matching on the ClinVar `CLNSIG` INFO field.

**Mechanism:** `CLNSIG` is multi-valued, mixes terms ("Conflicting_classifications", "Pathogenic/Likely_pathogenic", "Benign/Likely_benign"), and is per-small-variant — not per-CNV. A substring match for "pathogenic" silently captures "Likely_pathogenic" (intended) but a careless match also fires on records that are conflicting or benign once underscores and slashes are involved.

**Symptom:** Benign or conflicting variants reported as pathogenic; CNV flagged on incidental nearby SNVs.

**Fix:** Parse `CLNSIG` against the controlled vocabulary; exclude "Conflicting" and benign terms explicitly. Remember ClinVar SNV/indel pathogenicity does not transfer to a CNV — use it as context, and use ClinVar's own CNV records or ClinGen dosage regions for the CNV itself.

### Equating overlap with consequence

**Trigger:** Treating any gene-overlapping CNV as functionally significant.

**Mechanism:** Most single-copy losses are tolerated; partial overlaps may hit only introns/UTRs.

**Symptom:** Long lists of "affected" dosage-insensitive genes; benign CNVs over-called as significant.

**Fix:** Require dosage evidence (ClinGen HI/TS) and record coding-exon overlap and whole-gene-vs-partial status before calling a gene affected.

## Quantitative Thresholds

| Threshold | Value | Source / Rationale |
|-----------|-------|--------------------|
| Population-CNV reciprocal overlap | >= 50% (`-f 0.5 -r`) | Standard reciprocal-overlap match for benign filtering (convention traces to gnomAD-SV / DGV workflows; Collins RL et al 2020 *Nature* 581:444 uses comparable reciprocal-overlap thresholds for benign-population matching) |
| Common-CNV benign frequency | > 1% population frequency | ACMG/ClinGen: high frequency supports benign |
| ClinGen HI/TS dosage-sensitive | score = 3 | ClinGen: sufficient evidence for dosage sensitivity |
| Whole-gene overlap | >= 99% gene length covered | Distinguishes clean haploinsufficiency from partial/truncating |
| AnnotSV pathogenic ranks | rank 4-5 | AnnotSV ACMG-aligned ranking (1 benign - 5 pathogenic) |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| Wrong genes assigned to a CNV | hg19/hg38 build mismatch | Match builds; liftOver and verify a landmark |
| 40 genes called "amplified" for one amplicon | All overlapped genes reported as drivers | Prioritize recurrence-peak + known-driver genes |
| Benign variants flagged pathogenic | Substring match on ClinVar CLNSIG | Parse the controlled vocabulary explicitly |
| Tiny CNV matched to a huge population CNV | One-sided overlap used for frequency filter | Use reciprocal overlap (`-f 0.5 -r`) |
| AnnotSV columns not found | Column names differ across AnnotSV versions | Check `head` of the output for the installed version |
| Enrichment dominated by gene-dense loci | CNVs span gene clusters | Treat CNV-gene enrichment as hypothesis-generating |

## References

- Geoffroy V et al 2018. AnnotSV: an integrated tool for structural variations annotation. Bioinformatics 34:3572
- Riggs ER et al 2020. Technical standards for the interpretation and reporting of constitutional copy-number variants: ACMG and ClinGen. Genet Med 22:245
- Collins RL et al 2020. A structural variation reference for medical and population genetics (gnomAD-SV). Nature 581:444
- Sondka Z et al 2018. The COSMIC Cancer Gene Census. Nat Rev Cancer 18:696

## Related Skills

- copy-number/germline-cnv-interpretation - ACMG/ClinGen points-based CNV classification
- copy-number/recurrent-cnv - GISTIC2 recurrence peaks and driver-gene identification
- copy-number/cnvkit-analysis - Generates the CNV segments to annotate
- copy-number/cnv-visualization - Visualizing annotated CNVs
- pathway-analysis/go-enrichment - GO/KEGG enrichment methodology and caveats
- genome-intervals/bed-file-basics - BED interval operations
- clinical-databases/clinvar-lookup - Querying ClinVar for variant pathogenicity
<!-- END FILE: copy-number/cnv-annotation/SKILL.md -->

## 子目录：copy-number/cnv-visualization

<!-- BEGIN FILE: copy-number/cnv-visualization/SKILL.md -->
---
name: bio-copy-number-cnv-visualization
description: Visualize copy number profiles, segments, allele-specific tracks, and cohort patterns from CNVkit, GATK, ASCAT, FACETS, Sequenza, and other callers. Covers genome-wide and per-chromosome log2 scatter plots, B-allele-frequency/minor-allele-fraction tracks, ideograms, cohort heatmaps, circos views, and caller-native plots. Use when creating publication CNV figures, choosing which plot answers a given question, diagnosing a wrong diploid baseline visually, displaying loss of heterozygosity, or deciding what depth-only plots cannot reveal.
tool_type: mixed
primary_tool: matplotlib
---

## Version Compatibility

Reference examples tested with: matplotlib 3.8+, pandas 2.2+, numpy 1.26+, seaborn 0.13+, CNVkit 0.9.10+, GATK 4.5+; R 4.3+ with ggplot2 3.5+.

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show matplotlib pandas` then `help(function)` for signatures
- R: `packageVersion('ggplot2')` then `?function_name`
- CLI: `cnvkit.py version`, `gatk --version`

If code throws ImportError, AttributeError, or TypeError, introspect the installed package and adapt the example rather than retrying.

# CNV Visualization

**"Plot my copy number profile"** -> A CNV figure is an argument, not a picture. The plot type, the y-axis quantity, and where the diploid baseline sits all determine what the reader can conclude. The single most important rule: a depth-only log2 plot cannot show loss of heterozygosity, cannot show tumor purity, and silently misleads if the diploid baseline is centered on a non-diploid mode.

- CLI: `cnvkit.py scatter` / `diagram` / `heatmap`; `gatk PlotModeledSegments`
- Python: `matplotlib` for custom genome-wide and allele-specific tracks
- R: `ggplot2`, `karyoploteR` for publication ideograms

## Plot Selection — What Each View Reveals and Hides

| Plot | Answers | Reveals | Cannot show |
|------|---------|---------|-------------|
| Genome-wide log2 scatter + segments | Where are the gains/losses? | Focal vs broad events, noise level | LOH, purity, allele-specific state |
| Per-chromosome scatter | Is this focal event real and where are its boundaries? | Breakpoints, bin support, weight | Absolute CN without purity |
| BAF / minor-allele-fraction track | Is there allelic imbalance / LOH? | CN-neutral LOH, mirrored imbalance | Total copy number alone |
| Combined log2 + BAF (two-panel) | What is the allele-specific state? | Gains vs CN-LOH vs balanced | — (this is the complete view) |
| Cohort heatmap | What is recurrent across samples? | Shared arm/focal events | Per-sample breakpoint detail |
| Ideogram / diagram | Where do events sit relative to cytobands/genes? | Gene-level context | Quantitative amplitude |
| Circos | Genome-wide CNV + SV breakpoints together | CNV-SV co-localization | Fine amplitude detail |
| Caller-native (GATK/ASCAT/FACETS) | Did the caller fit correctly? | Model fit, segment confidence | — (diagnostic, not publication) |

The decision rule: if the biological question involves LOH, allele-specific gain, or whole-genome doubling, a log2-only plot is insufficient — pair it with a BAF track.

## CNVkit Built-in Plots

```bash
cnvkit.py scatter sample.cnr -s sample.cns -o scatter.png            # genome-wide
cnvkit.py scatter sample.cnr -s sample.cns -c chr17 -o chr17.png      # one chromosome
cnvkit.py scatter sample.cnr -s sample.cns -v sample.vcf.gz -o baf.png  # with BAF panel
cnvkit.py diagram sample.cnr -s sample.cns -o diagram.pdf             # ideogram
cnvkit.py heatmap cohort/*.cns -d -o cohort_heatmap.pdf              # cohort, desaturated
```

Passing `-v` with a VCF adds a B-allele-frequency panel — use it whenever LOH matters.

## Genome-Wide log2 Profile with Segments

**Goal:** Render a publication genome-wide CNV profile with colored segments.

**Approach:** Map per-bin log2 to cumulative genomic coordinates, plot bins as faint points, overlay segment medians as colored horizontal lines, mark chromosome boundaries.

```python
import pandas as pd
import matplotlib.pyplot as plt

def plot_genome_profile(cnr_file, cns_file, output=None, gain=0.3, loss=-0.3):
    '''Genome-wide log2 scatter with segment overlay.'''
    cnr = pd.read_csv(cnr_file, sep='\t')
    cns = pd.read_csv(cns_file, sep='\t')
    chroms = [f'chr{i}' for i in range(1, 23)] + ['chrX', 'chrY']

    offsets, cum = {}, 0
    for c in chroms:
        sub = cnr[cnr['chromosome'] == c]
        if sub.empty:
            continue
        offsets[c] = cum
        cum += sub['end'].max()

    cnr = cnr[cnr['chromosome'].isin(offsets)].copy()
    cnr['x'] = cnr.apply(lambda r: offsets[r['chromosome']] + r['start'], axis=1)

    fig, ax = plt.subplots(figsize=(16, 4))
    ax.scatter(cnr['x'], cnr['log2'], s=1, c='0.7', alpha=0.5, rasterized=True)
    for _, seg in cns.iterrows():
        if seg['chromosome'] not in offsets:
            continue
        x0 = offsets[seg['chromosome']] + seg['start']
        x1 = offsets[seg['chromosome']] + seg['end']
        color = 'red' if seg['log2'] > gain else 'blue' if seg['log2'] < loss else '0.3'
        ax.hlines(seg['log2'], x0, x1, colors=color, linewidth=2.5)
    for c, x in offsets.items():
        ax.axvline(x, color='0.9', linewidth=0.5)
    ax.axhline(0, color='black', linewidth=0.6)
    ax.set_ylim(-2, 2)
    ax.set_ylabel('log2 copy ratio')
    ax.set_xlabel('genomic position')
    fig.tight_layout()
    if output:
        fig.savefig(output, dpi=200)
    return fig, ax
```

## Combined log2 + B-Allele-Frequency Panel

**Goal:** Show total copy number and allelic imbalance together so CN-neutral LOH and allele-specific gains are visible.

**Approach:** Stack two axes — log2 on top, BAF below. Mirror BAF about 0.5 so allelic imbalance reads as deviation from the center line.

```python
import numpy as np

def plot_log2_baf(cnr_file, baf_df, output=None):
    '''Two-panel plot: log2 copy ratio above, B-allele frequency below.
    baf_df: columns chromosome, position, baf (germline-het sites only).'''
    cnr = pd.read_csv(cnr_file, sep='\t')
    fig, (ax_cn, ax_baf) = plt.subplots(2, 1, figsize=(16, 6), sharex=True)

    ax_cn.scatter(range(len(cnr)), cnr['log2'], s=1, c='0.6', alpha=0.5)
    ax_cn.axhline(0, color='black', linewidth=0.6)
    ax_cn.set_ylabel('log2 ratio')
    ax_cn.set_ylim(-2, 2)

    # Plot BAF and its mirror; a tight band at 0.5 = balanced, split bands = imbalance/LOH
    ax_baf.scatter(range(len(baf_df)), baf_df['baf'], s=2, c='0.4', alpha=0.5)
    ax_baf.scatter(range(len(baf_df)), 1 - baf_df['baf'], s=2, c='0.4', alpha=0.5)
    ax_baf.axhline(0.5, color='black', linewidth=0.6)
    ax_baf.set_ylabel('B-allele frequency')
    ax_baf.set_ylim(0, 1)
    ax_baf.set_xlabel('het SNP index')
    fig.tight_layout()
    if output:
        fig.savefig(output, dpi=200)
    return fig
```

A copy-neutral LOH region shows log2 ~ 0 but BAF splitting away from 0.5 — invisible on any log2-only plot.

## Cohort Heatmap

**Goal:** Show recurrent CNV patterns across a cohort.

**Approach:** Resample every sample's segments onto a common genomic bin grid, stack into a samples-by-bins matrix, render with a diverging colormap centered at zero.

```python
import seaborn as sns

def plot_cohort_heatmap(cns_files, bin_size=1_000_000, output=None):
    '''Recurrent-CNV heatmap across a cohort on a uniform bin grid.'''
    chroms = [f'chr{i}' for i in range(1, 23)]
    columns = []
    for c in chroms:
        columns += [(c, b) for b in range(0, 250_000_000, bin_size)]
    matrix = {}
    for f in cns_files:
        name = f.split('/')[-1].replace('.cns', '')
        cns = pd.read_csv(f, sep='\t')
        row = {}
        for c, b in columns:
            hits = cns[(cns['chromosome'] == c) &
                       (cns['start'] < b + bin_size) & (cns['end'] > b)]
            row[(c, b)] = hits['log2'].mean() if not hits.empty else 0.0
        matrix[name] = row
    df = pd.DataFrame(matrix).T
    fig, ax = plt.subplots(figsize=(14, max(4, 0.3 * len(cns_files))))
    sns.heatmap(df, cmap='RdBu_r', center=0, vmin=-1.5, vmax=1.5,
                xticklabels=False, ax=ax)
    ax.set_xlabel('genomic bin')
    ax.set_ylabel('sample')
    if output:
        fig.savefig(output, dpi=200, bbox_inches='tight')
    return fig
```

## Caller-Native Diagnostic Plots

```bash
# GATK: denoised ratios + modeled segments with allelic info
gatk PlotModeledSegments --denoised-copy-ratios tumor.denoisedCR.tsv \
    --allelic-counts tumor.hets.tsv --segments tumor.modelFinal.seg \
    --sequence-dictionary reference.dict --output-prefix tumor -O plots/
```

ASCAT (`ascat.runAscat` ASPCF and sunrise plots), Sequenza (`sequenza.results` chromosome view and the cellularity/ploidy contour), and FACETS (`plotSample`) emit diagnostic plots — always inspect these to confirm the purity/ploidy fit before trusting downstream calls. They are diagnostic, not publication, figures.

## Failure Modes

### The diploid-baseline centering trap

**Trigger:** Plotting log2 from a hyper-aneuploid or whole-genome-doubled tumor with the y-axis centered on the data median or mode.

**Mechanism:** If most of the genome is at tetraploid baseline, centering on the mode places 4 copies at log2 0. Every true diploid region then appears deleted and the plot tells the opposite story.

**Symptom:** A genome-wide pattern of "loss" (or "gain") inconsistent with the BAF track or with the caller's ploidy estimate.

**Fix:** Anchor the y-axis baseline to the caller's ploidy estimate, not the data mode. Always show a BAF track alongside; if BAF says balanced where log2 says deleted, the centering is wrong.

### log2 axis presented as if it were absolute copy number

**Trigger:** Labeling a log2 y-axis "copy number" or comparing log2 amplitudes across samples of different purity.

**Mechanism:** log2 ratio compresses with decreasing purity — a true CN=4 amplification at 40% purity has roughly half the log2 amplitude of the same event at 80% purity.

**Symptom:** A real amplification looks weaker than a passenger gain in a purer sample; cross-sample amplitude comparisons are meaningless.

**Fix:** For cross-sample or absolute claims, plot integer copy number from a purity-corrected caller, not raw log2. Label log2 axes "log2 copy ratio".

### Cohort heatmap binning erases focal events

**Trigger:** Large uniform bins (e.g. 1-3 Mb) in a cohort heatmap.

**Mechanism:** A focal amplification (e.g. a few hundred kb at MYC or ERBB2) is averaged with flanking neutral sequence and disappears.

**Symptom:** Known recurrent focal drivers absent from the heatmap; only arm-level events visible.

**Fix:** Use a bin size matched to the question — Mb bins for arm-level surveys, gene-centric or GISTIC peak regions for focal drivers. Consider a separate gene-level panel.

## Quantitative Thresholds

| Choice | Value | Rationale |
|--------|-------|-----------|
| log2 y-axis range | -2 to 2 | Covers homozygous loss to ~8-copy gain; clip extreme amplicons separately |
| Gain/loss plot coloring | log2 > 0.3 / < -0.3 | Visual convention (no single primary citation); not a calling threshold (see cnvkit-analysis) |
| Cohort heatmap bin (arm-level) | ~1 Mb | Balances resolution and matrix size |
| Cohort heatmap colormap center | 0 | Diverging map must be zero-centered or gains/losses are not comparable |
| Rasterize scatter points | yes, for > ~50k bins | Keeps vector PDFs openable; segments stay vector |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| Whole genome looks lost or gained | y-axis centered on a non-diploid mode | Anchor baseline to caller ploidy; add a BAF track |
| LOH region not visible | log2-only plot | Add a BAF / minor-allele-fraction panel |
| Focal driver missing from heatmap | Bins too large | Use gene-level or GISTIC-peak bins |
| Giant unopenable PDF | 100k+ vector scatter points | `rasterized=True` on the scatter |
| Chromosomes out of order / overlapping | String-sorted contig names | Explicit chromosome order list |
| Amplitudes incomparable across samples | Plotting raw log2 across mixed purity | Plot purity-corrected integer CN |

## References

- Talevich E et al 2016. CNVkit: genome-wide copy number detection from targeted DNA sequencing. PLoS Comput Biol 12:e1004873
- Van Loo P et al 2010. Allele-specific copy number analysis of tumors. PNAS 107:16910 (BAF interpretation)
- Gel B, Serra E 2017. karyoploteR: an R/Bioconductor package to plot customizable genomes. Bioinformatics 33:3088

## Related Skills

- copy-number/cnvkit-analysis - Generates the .cnr/.cns inputs and built-in plots
- copy-number/gatk-cnv - GATK denoised ratios and modeled-segment plots
- copy-number/allele-specific-copy-number - Source of BAF/MAF tracks and ploidy estimates
- copy-number/recurrent-cnv - Cohort-level recurrence underlying heatmaps
- data-visualization/ggplot2-fundamentals - General publication-figure grammar
- data-visualization/circos-plots - Circular genome layouts for CNV + SV
<!-- END FILE: copy-number/cnv-visualization/SKILL.md -->

## 子目录：copy-number/cnvkit-analysis

<!-- BEGIN FILE: copy-number/cnvkit-analysis/SKILL.md -->
---
name: bio-copy-number-cnvkit-analysis
description: Detect somatic and germline copy number variants from targeted, exome, and whole-genome sequencing with CNVkit, a read-depth caller that combines on-target and off-target (antitarget) coverage. Covers panel-of-normals construction, flat-reference tumor-only calling, hybrid/amplicon/WGS modes, CBS vs HMM segmentation selection, purity-aware integer calling, and reconciliation against GATK and allele-specific callers. Use when calling CNVs from hybrid-capture panels or exomes, deciding whether CNVkit (depth-only) is the right tool versus an allele-specific caller, building a panel of normals, diagnosing flat-reference false positives, or interpreting log2 ratios into copy-number states.
tool_type: cli
primary_tool: cnvkit
---

## Version Compatibility

Reference examples tested with: CNVkit 0.9.10+, samtools 1.19+, bedtools 2.31+, Python 3.10+, R 4.3+ with DNAcopy 1.76+.

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `cnvkit.py version` then `cnvkit.py batch --help` to confirm flags
- Python: `pip show cnvkit` then `python -c "import cnvlib; help(cnvlib.read)"`
- R: `packageVersion('DNAcopy')` (CBS backend)

If a command throws an unrecognized-argument or AttributeError, introspect the installed version and adapt the example rather than retrying. CNVkit segmentation methods (`hmm`, `hmm-tumor`, `hmm-germline`) depend on `pomegranate`; CBS depends on Bioconductor `DNAcopy`.

# CNVkit Copy Number Analysis

**"Detect copy number variants from my exome / panel data"** -> Run a read-depth pipeline: normalize on-target and off-target coverage against a reference, segment the log2-ratio profile, and call gains/losses. CNVkit is a *depth-only* caller — it estimates **relative** copy number and cannot, on its own, resolve tumor purity, ploidy, or allele-specific state. Choosing CNVkit is a decision that the experiment does not require allelic resolution.

- CLI: `cnvkit.py batch tumor.bam --normal normal.bam --targets panel.bed --fasta ref.fa`
- Python API: `cnvlib.read('sample.cnr')` for downstream filtering

## Where CNVkit Sits — Caller Taxonomy

| Caller | Signal used | Output | Purity/ploidy aware | Fails when |
|--------|-------------|--------|---------------------|------------|
| CNVkit | Depth (on + off-target) | Relative log2, threshold-called CN | No (manual `--purity`) | Sample purity < ~40%; hyper-aneuploid genome breaks median centering; balanced events invisible |
| GATK gCNV / somatic CNV | Depth (PCA/tangent denoised) | Copy-ratio segments, +/-/0 call | No (somatic); ploidy prior (germline) | Recurrent CNV in the PoN normalized away; ModelSegments gives no integer ASCN |
| ASCAT / Sequenza / FACETS | Depth + B-allele frequency | Integer allele-specific CN, purity, ploidy | Yes (jointly fit) | Near-diploid genome cannot anchor purity; low het-SNP density |
| ExomeDepth / GATK gCNV (cohort) | Depth across a cohort | Germline CN genotype | Germline ploidy only | < ~30-100 technically matched samples; common CNV |

CNVkit's niche: a fast, single-sample depth caller for hybrid-capture panels and exomes where antitarget reads recover genome-wide resolution. Its limit: it answers "is this region gained or lost relative to baseline" — not "how many absolute copies, on which haplotype, in what fraction of cells." For tumor integer CN, purity, LOH, or whole-genome doubling, escalate to allele-specific-copy-number.

## Decision Tree by Scenario

| Scenario | Recommended CNVkit configuration | Why |
|----------|----------------------------------|-----|
| Hybrid-capture panel or exome, tumor-normal | `batch` hybrid mode, matched normal as reference | Antitargets recover off-target resolution; matched normal cancels capture bias |
| Exome cohort, pooled normals available | Build pooled PoN reference, then `batch --reference` | Pooled reference averages out per-normal noise; 5-20+ normals |
| Amplicon / multiplex-PCR panel | `batch --method amplicon` | No usable off-target reads; antitarget bins are pure noise — must be dropped |
| Whole-genome sequencing | `batch --method wgs` | Genome-wide fixed bins; no target/antitarget split |
| Tumor-only, no normal of any kind | `batch` with flat reference (omit `--normal`) | Last resort; expect GC/capture-bias false positives — see failure mode below |
| FFPE / low-input / impure tumor | Add `--drop-low-coverage`; segment with `hmm-tumor` | FFPE dropout produces zero-coverage bins that CBS reads as deletions |
| Need absolute CN, LOH, purity | Do not use CNVkit alone | Escalate to allele-specific-copy-number (ASCAT/Sequenza/FACETS/PureCN) |

## Core Pipeline — Tumor-Normal Pair

The `batch` command wraps target/antitarget generation, coverage, reference building, fix, and segment:

```bash
cnvkit.py batch tumor.bam \
    --normal normal.bam \
    --targets panel.bed \
    --annotate refFlat.txt \
    --fasta reference.fa \
    --access access-excludes.bed \
    --output-reference reference.cnn \
    --output-dir results/ \
    --drop-low-coverage \
    --diagram --scatter
```

`--access` restricts antitarget bins to mappable, non-gap genome (generate once with `cnvkit.py access reference.fa -o access.bed`). `--drop-low-coverage` is effectively mandatory for tumor, FFPE, or any sample with coverage dropout.

## Panel of Normals — The Reference Determines Call Quality

A reference built from pooled normals is the single largest quality lever. Process is: build the reference from normals once, then run every tumor against it.

```bash
# Build pooled reference from process-matched normals (same capture kit, same lab)
cnvkit.py batch --normal normal*.bam \
    --targets panel.bed --annotate refFlat.txt --fasta reference.fa \
    --access access.bed \
    --output-reference pooled_reference.cnn

# Run each tumor against the pre-built reference
cnvkit.py batch tumor*.bam --reference pooled_reference.cnn \
    --output-dir results/ --drop-low-coverage --scatter --diagram
```

## Step-by-Step Pipeline (Fine-Grained Control)

```bash
cnvkit.py target panel.bed --annotate refFlat.txt --split -o targets.bed
cnvkit.py antitarget panel.bed --access access.bed -o antitargets.bed
cnvkit.py coverage tumor.bam targets.bed -o tumor.targetcoverage.cnn
cnvkit.py coverage tumor.bam antitargets.bed -o tumor.antitargetcoverage.cnn
cnvkit.py reference normal*.{target,antitarget}coverage.cnn --fasta reference.fa -o reference.cnn
cnvkit.py fix tumor.targetcoverage.cnn tumor.antitargetcoverage.cnn reference.cnn -o tumor.cnr
cnvkit.py segment tumor.cnr -o tumor.cns --drop-low-coverage
cnvkit.py call tumor.cns -o tumor.call.cns
```

## Segmentation Method Selection

CNVkit's `segment` step is where the bias-variance trade-off is set. The default CBS is not always correct — see copy-ratio-segmentation for the full algorithm comparison.

```bash
cnvkit.py segment tumor.cnr -m cbs -o tumor.cns          # default; precise on focal events
cnvkit.py segment tumor.cnr -m hmm-tumor -o tumor.cns    # heterogeneous tumor, broad states
cnvkit.py segment tumor.cnr -m hmm-germline -o tumor.cns # germline, priors near diploid
cnvkit.py segment tumor.cnr -m haar -o tumor.cns         # fast, low-depth WGS
```

Rule of thumb: CBS for panels/exomes with adequate depth (precise on small segments); `hmm-tumor` for impure or heterogeneous tumors where CBS over-fragments; `haar` for shallow WGS where CBS recall degrades.

## Purity-Aware Integer Calling

`call` converts segmented log2 ratios to copy-number states. The `clonal` method rescales by tumor purity before rounding to integers — without it, an impure tumor's true CN=4 amplification rounds to CN=3 or CN=2.

```bash
# Threshold method (default): fixed log2 cutpoints, no purity correction
cnvkit.py call tumor.cns -o tumor.call.cns

# Clonal method: rescale by purity, then round to integer CN
cnvkit.py call tumor.cns -m clonal --purity 0.65 --ploidy 2 -o tumor.call.cns

# Overlay B-allele frequency from a SNV VCF (for LOH visualization, NOT joint ASCN)
cnvkit.py call tumor.cns -m clonal --purity 0.65 --vcf tumor.vcf.gz -o tumor.call.cns
```

CNVkit can read BAF from a VCF and report a `baf` column, but it segments log2 and BAF *separately* and does not jointly fit purity from them. For a true joint allele-specific model (ASPCF, FACETS joint segmentation), use allele-specific-copy-number.

## Failure Modes

### Flat reference (tumor-only) — systematic false focal calls

**Trigger:** No `--normal` and no pooled PoN; CNVkit builds a flat reference (uniform log2 0) from the FASTA.

**Mechanism:** A flat reference corrects only GC and (optionally) RepeatMasker content via the FASTA. It cannot correct capture efficiency, which varies 10-100x across probes and is the dominant bias in hybrid capture. Per-probe capture bias is then misread as copy number.

**Symptom:** Recurrent "CNVs" at the same loci across unrelated tumor-only samples; spiky `.cnr` profiles; high MAD; calls concentrated at probe boundaries.

**Fix:** Never rely on a flat reference for clinical or focal calls. Build a pooled PoN from >= 5 process-matched normals. If truly no normal exists, treat tumor-only CNVkit output as hypothesis-generating only and escalate to PureCN (allele-specific-copy-number), which models a normal database explicitly.

### Antitarget bins on amplicon panels — pure noise

**Trigger:** Running default hybrid mode on an amplicon (multiplex-PCR) panel.

**Mechanism:** Amplicon panels produce essentially no off-target reads. Antitarget bins then contain a handful of stray reads, giving wildly variable log2 that the segmenter chases.

**Symptom:** Huge antitarget bin spread; nonsensical genome-wide segments between the targeted genes.

**Fix:** Use `--method amplicon`, which drops antitargets entirely and calls only from on-target bins. Accept that resolution is limited to the targeted genes.

### Low tumor purity — the death zone below ~40%

**Trigger:** Tumor cellularity below ~40% (common in breast, lung adenocarcinoma, melanoma, low-cellularity biopsies).

**Mechanism:** Each somatic CN change is diluted by 2-copy normal DNA. A true single-copy loss at 30% purity produces log2 ~ -0.23 — inside the diploid threshold band.

**Symptom:** Genome looks near-flat; few or no calls; known driver amplifications (e.g. ERBB2, MYC) missed.

**Fix:** CNVkit cannot rescue this. Confirm purity with an allele-specific caller (BAF gives an orthogonal purity estimate). Below ~20% purity, no depth-based caller is reliable — report as indeterminate.

### Hyper-aneuploid / whole-genome-doubled genome — baseline miscalled

**Trigger:** Tumor with >50% of the genome altered, or whole-genome doubling.

**Mechanism:** `call --center median` (or mode) assumes the commonest log2 state is diploid. In a WGD genome the commonest state is tetraploid; centering on it shifts the whole profile and inverts gain/loss calls.

**Symptom:** Genome-wide pattern of calls inconsistent with known biology; "deletions" everywhere or "gains" everywhere.

**Fix:** Do not trust depth-only centering on aneuploid tumors. Anchor the diploid baseline with BAF/SNV data via an allele-specific caller, which estimates absolute ploidy directly.

### FFPE / low-input dropout read as homozygous deletions

**Trigger:** Degraded FFPE DNA or low input; some bins have near-zero coverage.

**Mechanism:** Zero-coverage bins produce extreme negative log2; CBS joins them into spurious homozygous-deletion segments.

**Symptom:** Scattered tiny "CN=0" segments, often at hard-to-capture (high-GC) loci.

**Fix:** Always pass `--drop-low-coverage` to `batch` and `segment`. Inspect MAD; if MAD > 0.5, the sample is too noisy for confident focal calls.

## Reconciliation: When CNVkit Disagrees With Another Caller

| Pattern | Likely cause | Action |
|---------|--------------|--------|
| CNVkit calls focal events GATK misses | GATK PoN/tangent normalization absorbed the event | Trust CNVkit if the event is rare; suspect GATK if PoN contained tumors |
| GATK/ASCAT call broad arm events CNVkit flattens | CNVkit centered on a non-diploid mode | Re-center against an allele-specific ploidy estimate |
| CNVkit and ASCAT disagree on integer CN | CNVkit purity guess wrong, or genome is WGD | Trust ASCAT/FACETS — joint BAF+depth fit resolves purity/ploidy |
| Tumor-only CNVkit calls absent in matched-normal rerun | Germline CNV or capture bias misread as somatic | Re-run with the matched normal; germline CNVs are not somatic events |

**Operational rule for high-confidence reporting:** Treat a CNVkit call as confident only when (1) the reference was a pooled PoN of process-matched normals, (2) sample MAD < 0.5, (3) the segment spans multiple bins with consistent weight, and (4) for any clinically actionable focal event, it is confirmed by an orthogonal caller or by allele-specific data. Depth-only calls on tumors are screening-grade, not definitive.

## Quality Control

```bash
cnvkit.py metrics results/*.cnr -s results/*.cns      # MAD, spread, bivar per sample
cnvkit.py sex results/*.cnr                           # detect sex / sample swaps
cnvkit.py segmetrics tumor.cnr -s tumor.cns --ci --pi --bootstrap 100 -o tumor.segmetrics.cns
cnvkit.py genemetrics tumor.cnr -s tumor.cns -t 0.2 --ci --bootstrap 100 -o tumor.genemetrics.tsv
```

## Quantitative Thresholds

| Threshold | Value | Source / Rationale |
|-----------|-------|--------------------|
| Sample MAD (noise) | < 0.5 acceptable; < 0.3 good | CNVkit docs; MAD is the median absolute deviation of bin log2 |
| Panel of normals size | >= 5; 10-20 preferred | Talevich 2016; pooling averages per-normal capture noise |
| Default call thresholds (log2) | -1.1, -0.25, 0.2, 0.7 | CNVkit `call -t` defaults: CN 0 / 1 / 2 / 3 / 4+ boundaries |
| Purity floor for depth calling | ~40% reliable; ~20% absolute floor | Below ~40% segmentation fails (sCNAphase, Gusnanto 2012) |
| `genemetrics -t` gain/loss | 0.2 (default) | 2^0.2 ~ 15% copy-ratio change; tune up for impure samples |
| Antitarget avg bin size | auto; ~target size x fold-enrichment | CNVkit docs; off-target bins should hold comparable read counts |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| Spiky `.cnr`, recurrent calls across samples | Flat reference; capture bias misread | Build a pooled PoN; never use flat reference for focal calls |
| Antitarget spread huge, nonsense segments | Hybrid mode on an amplicon panel | Use `--method amplicon` |
| Scattered CN=0 micro-segments | FFPE zero-coverage bins | Add `--drop-low-coverage` to `batch` and `segment` |
| Integer CN systematically too low | `call` without `-m clonal --purity` | Supply purity, or use an allele-specific caller |
| Whole genome called gain or loss | Centering on a non-diploid mode (WGD) | Anchor ploidy with BAF; do not depth-center aneuploid tumors |
| `pomegranate` ImportError on HMM | HMM backend not installed | `pip install pomegranate`; or use `-m cbs` |

## References

- Talevich E et al 2016. CNVkit: genome-wide copy number detection from targeted DNA sequencing. PLoS Comput Biol 12:e1004873
- Olshen AB et al 2004. Circular binary segmentation for the analysis of array-based DNA copy number data. Biostatistics 5:557 (CBS)
- Gusnanto A et al 2012. Correcting for cancer genome size and tumour cell content in whole-genome copy number. Bioinformatics 28:40
- Benjamini Y, Speed TP 2012. Summarizing and correcting the GC content bias in high-throughput sequencing. Nucleic Acids Res 40:e72

## Related Skills

- copy-number/copy-ratio-segmentation - CBS vs HMM choice, depth normalization, bias correction
- copy-number/allele-specific-copy-number - ASCAT/Sequenza/FACETS/PureCN for purity, ploidy, integer ASCN
- copy-number/gatk-cnv - GATK depth-based alternative; tangent normalization
- copy-number/cnv-annotation - Gene and clinical annotation of CNV calls
- copy-number/cnv-visualization - Profile plots, segmentation views, cohort heatmaps
- copy-number/recurrent-cnv - GISTIC2 cohort-level recurrent and driver CNV
- alignment-files/bam-statistics - QC of input BAMs before calling
- long-read-sequencing/structural-variants - Complementary breakpoint-resolved SV calling
<!-- END FILE: copy-number/cnvkit-analysis/SKILL.md -->

## 子目录：copy-number/copy-ratio-segmentation

<!-- BEGIN FILE: copy-number/copy-ratio-segmentation/SKILL.md -->
---
name: bio-copy-number-copy-ratio-segmentation
description: Normalize read-depth copy-ratio profiles and segment them into copy-number regions using circular binary segmentation (CBS, DNAcopy), hidden Markov models, HaarSeg, and fused-lasso methods. Covers GC-content, mappability, and replication-timing (wave-artifact) bias correction, panel-of-normals/PCA denoising, diploid-baseline centering, and algorithm selection by sequencing depth and event size. Use when choosing a segmentation algorithm, correcting depth bias, diagnosing oversegmentation or a mis-centered baseline, tuning CBS or HMM parameters, or understanding why a downstream CNV caller produced fragmented or shifted segments.
tool_type: mixed
primary_tool: DNAcopy
---

## Version Compatibility

Reference examples tested with: R 4.3+ with DNAcopy 1.76+, Python 3.10+ with numpy 1.26+, pandas 2.2+; QDNAseq 1.38+ (optional, GC/mappability normalization).

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('DNAcopy')` then `?segment` to confirm arguments
- Python: `pip show numpy pandas`

If code throws an error, introspect the installed package and adapt the example. CBS lives in Bioconductor `DNAcopy`; HMM segmentation is provided by caller-specific backends (CNVkit uses `pomegranate`; HaarSeg has its own R/Python packages).

# Copy-Ratio Segmentation

**"Turn noisy per-bin depth into clean copy-number segments"** -> Two stages, both error-prone. First, normalize the depth profile so the only remaining variation is copy number (not GC, mappability, or replication timing). Second, partition the normalized profile into segments of constant copy number. The segmentation algorithm choice has a *predictable* bias signature, and the diploid-baseline choice can invert every call.

- R: `DNAcopy::segment` (CBS, the reference implementation)
- Python: HMM via `pomegranate`; HaarSeg via `haarseg`
- The output feeds every CNV caller (cnvkit-analysis, gatk-cnv, allele-specific-copy-number)

## Stage 1: Why Depth Is Biased Before It Is Copy Number

Raw read depth confounds copy number with three systematic biases:

| Bias | Cause | Correction |
|------|-------|------------|
| GC content | PCR efficiency and probe hybridization vary with GC | Loess fit of depth vs GC (QDNAseq), or matched normal |
| Mappability | Multi-mapping reads under-counted in repetitive regions | Mappability track filter/weight; exclude low-mappability bins |
| Replication timing | Late-replicating DNA is under-represented — the "wave artifact" | Matched normal or PoN; GC correction alone does NOT remove it |
| Capture efficiency | Per-probe hybridization varies 10-100x (hybrid capture) | Panel of normals — the dominant bias for exomes/panels |

The key postdoc-level point: **GC correction alone is insufficient.** The wave artifact in cancer WGS is driven by replication timing, a biological signal GC normalization cannot flatten. Only a matched normal or a panel of normals removes it. This is why a CNVkit flat reference (GC-only) produces systematic false focal calls and why GATK tangent normalization exists.

## Stage 2: Segmentation Algorithm Taxonomy

| Algorithm | Model | Strength | Fails when |
|-----------|-------|----------|------------|
| CBS (circular binary segmentation) | Recursive t-statistic breakpoint test | High precision; excellent on small focal segments | Low depth (~3x): recall drops to ~42% (worse under over-dispersed counts); ~2 orders slower; fragments across assembly gaps |
| HMM | Hidden CN states, emission + transition | Depth-robust; high recall at low coverage | Less precise on small focal segments (~5 kb: ~76% precision vs CBS ~96%, Poisson model); EM finds only local optima |
| HaarSeg | Wavelet (Haar) multiscale edge detection | Very fast; good for shallow WGS | Less precise breakpoints than CBS; threshold-sensitive |
| Fused lasso (flasso) | L1-penalized piecewise-constant fit | Smooth; tunable sparsity | Penalty hard to set; can over-smooth focal events |
| ASPCF | Allele-specific piecewise-constant fit | Joint logR+BAF segmentation (ASCAT) | Needs BAF; see allele-specific-copy-number |

**Quantitative benchmark (Zhang et al 2024, Brief Bioinform):** the cited precision/recall numbers (CBS ~42% recall at 3x; HMM ~81% recall at 3x; CBS ~96% precision vs HMM ~76% on 5 kb focal segments under a Poisson model) summarise that paper's reported direction of the trade-off. Verify the exact figures against the published tables before quoting them in print; the qualitative trade-off (depth-vs-event-size, CBS-vs-HMM) is robust across recent benchmarks but the precise percentages depend on the simulation model (Poisson vs over-dispersed negative-binomial). There is no universally correct choice.

## Decision Tree

| Scenario | Algorithm | Rationale |
|----------|-----------|-----------|
| Panel / exome, adequate depth, focal events matter | CBS | Precise on small segments |
| Shallow WGS (< ~5x), broad events | HMM or HaarSeg | CBS recall degrades at low depth |
| Heterogeneous / impure tumor | HMM (e.g. CNVkit `hmm-tumor`) | Broader state transitions absorb noise |
| Germline, near-diploid | HMM with diploid-tight priors | Priors stabilize calls near CN=2 |
| Allele-specific (need BAF) | ASPCF / FACETS joint CBS | See allele-specific-copy-number |
| Very large WGS, speed-critical | HaarSeg | Near-linear; CBS is ~100x slower |

## Bias Correction — GC Loess Normalization

**Goal:** Remove GC-content bias from a per-bin depth profile.

**Approach:** Fit a loess curve of depth versus GC content, divide each bin by its fitted value, log2-transform. This corrects GC but not replication timing — use a normal for that.

```python
import numpy as np
import pandas as pd
from statsmodels.nonparametric.smoothers_lowess import lowess

def gc_correct(bins):
    '''GC-correct a per-bin depth profile. bins: columns chrom, start, depth, gc.
    Returns log2 copy ratio relative to the GC-corrected genome median.'''
    df = bins[(bins['depth'] > 0) & bins['gc'].between(0.3, 0.7)].copy()
    fitted = lowess(df['depth'], df['gc'], frac=0.3, return_sorted=False)
    df['corrected'] = df['depth'] / fitted
    df['log2'] = np.log2(df['corrected'] / df['corrected'].median())
    return df
```

For exomes and panels, a panel of normals (per-bin median of normals, or PCA denoising) is preferred over GC-only correction because it also removes capture and replication-timing bias.

## Segmentation — CBS with DNAcopy

**Goal:** Segment a normalized log2 profile into copy-number regions.

**Approach:** Build a CNA object, smooth single-bin outliers, run CBS, then merge adjacent segments whose means differ by less than a noise-scaled threshold (`sdundo`).

```r
library(DNAcopy)

# bins: data frame with chrom, maploc (bin midpoint), log2
cna <- CNA(genomdat = bins$log2, chrom = bins$chrom, maploc = bins$maploc,
           data.type = 'logratio', sampleid = 'tumor')
cna <- smooth.CNA(cna)                          # damp single-bin outliers

# alpha = breakpoint significance; undo.splits='sdundo' merges segments whose means
# are within undo.SD noise standard deviations -- the main guard against oversegmentation.
seg <- segment(cna, alpha = 0.01, undo.splits = 'sdundo', undo.SD = 2,
               verbose = 1)
write.table(seg$output, 'tumor.segments.tsv', sep = '\t',
            quote = FALSE, row.names = FALSE)
```

## Failure Modes

### Oversegmentation / hyperfragmentation

**Trigger:** CBS `alpha` too liberal, `undo.SD` too small, or a noisy (high-MAD) profile; FACETS `cval` too low.

**Mechanism:** The breakpoint test fires on noise; the profile shatters into many tiny segments that do not correspond to real copy-number changes.

**Symptom:** Hundreds of short segments; segment count scales with noise, not biology; downstream integer CN incoherent with per-bin medians.

**Fix:** Raise `alpha` toward 0.01 or stricter, increase `undo.SD` (e.g. 2-3), or denoise the input first (better PoN, drop low-coverage bins). Three signatures (Steele 2022) had to be discarded as oversegmentation artifacts — fragmentation propagates into every downstream analysis, including copy-number signatures.

### The diploid-baseline centering trap

**Trigger:** Centering the log2 profile on its median or mode in a hyper-aneuploid or whole-genome-doubled genome.

**Mechanism:** Centering assumes the commonest log2 value is diploid. In a WGD genome the commonest state is tetraploid; centering on it shifts the whole profile so true diploid regions read as deletions and amplifications read as neutral.

**Symptom:** Genome-wide gain or loss inconsistent with biology; segmentation is fine but every call has the wrong sign.

**Fix:** Do not depth-center aneuploid genomes. Anchor the diploid baseline with BAF/SNV data via an allele-specific caller, which estimates absolute ploidy. GISTIC and most callers require a correctly centered seg file as input.

### CBS recall degrades at low depth

**Trigger:** CBS on shallow data (< ~5x WGS, or low-coverage bins).

**Mechanism:** The two-sample t-statistic loses power when per-bin variance swamps the mean difference; CBS misses real breakpoints (recall ~42% at 3x under a Poisson model, worse under over-dispersed counts), while the segments it does call stay fairly precise.

**Symptom:** Real events absent from the segmentation; recall poor on a genome with known CNVs.

**Fix:** Use HMM (depth-robust, ~81% recall at 3x) or HaarSeg for shallow data; or increase bin size to raise per-bin counts before segmenting.

### CBS fragments across assembly gaps

**Trigger:** CBS run over a profile with centromere/telomere gaps not handled as chromosome breaks.

**Mechanism:** CBS treats gapped data as independent subsets; spurious breakpoints appear at gap edges.

**Symptom:** Segment boundaries clustered at centromeres; tiny artifactual segments flanking gaps.

**Fix:** Segment per chromosome arm, or supply gap-aware chromosome coordinates so CBS does not bridge gaps.

### HMM EM converges to a local optimum

**Trigger:** HMM with poor initial parameters or too few iterations.

**Mechanism:** Baum-Welch EM is not globally optimal; emission/transition parameters can settle in a local optimum, mis-assigning states.

**Symptom:** Reruns give different state assignments; CN states inconsistent with the visible profile.

**Fix:** Use informative priors (diploid-centered for germline, broader for tumor), run multiple initializations, and sanity-check state means against the per-bin distribution.

## Reconciliation: When Segmentations Disagree

| Pattern | Likely cause | Action |
|---------|--------------|--------|
| CBS shatters where HMM gives clean broad segments | Low depth — CBS over-fits noise | Trust HMM; CBS needs more depth |
| HMM misses a focal event CBS finds | HMM window resolution too coarse | Trust CBS for focal; HMM blurs small events |
| Both agree on arms, differ on focal boundaries | Different breakpoint resolution | Arm calls are robust; treat focal boundaries as approximate |
| Segmentation differs run-to-run | HMM local optima, or unfixed random seed | Fix seeds; use multiple HMM initializations |

**Operational rule:** Match the algorithm to depth and event size — CBS for adequate-depth focal work, HMM/HaarSeg for shallow or broad. Confirm the diploid baseline against an allele-specific ploidy estimate before any sign-dependent interpretation. Report arm-level segments with confidence; treat focal boundaries as algorithm-dependent.

## Quantitative Thresholds

| Threshold | Value | Source / Rationale |
|-----------|-------|--------------------|
| CBS `alpha` | 0.01 | DNAcopy default; breakpoint significance |
| CBS `undo.SD` | 2-3 | Merges segments within N noise SD; guards oversegmentation |
| Depth where CBS recall degrades | < ~5x WGS | Zhang 2024; CBS recall falls sharply (HMM is depth-robust) |
| GC range kept for loess | 0.3-0.7 | Extreme-GC bins are unreliable; standard restriction |
| Bin size, shallow WGS CNV | ~500 kb - 1 Mb | Larger bins raise per-bin counts for stable segmentation |
| Sample MAD usable | < 0.5 | Above this, segmentation chases noise regardless of algorithm |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| Hundreds of tiny segments | Oversegmentation (liberal alpha / low cval / noisy input) | Tighten alpha, raise undo.SD, denoise input |
| Whole genome wrong-signed | Baseline centered on a non-diploid mode | Anchor ploidy with BAF; do not depth-center aneuploid genomes |
| Real events missed at low depth | CBS recall degrades | Use HMM/HaarSeg or larger bins |
| Breakpoints clustered at centromeres | CBS bridging assembly gaps | Segment per arm; supply gap-aware coordinates |
| Segmentation not reproducible | HMM local optima / unfixed seed | Fix seeds; multiple initializations |
| Wave artifact remains after GC correction | Replication-timing bias, not GC | Use a matched normal or PoN |

## References

- Olshen AB et al 2004. Circular binary segmentation for the analysis of array-based DNA copy number data. Biostatistics 5:557
- Venkatraman ES, Olshen AB 2007. A faster circular binary segmentation algorithm. Bioinformatics 23:657
- Zhang Y, Liu W, Duan J 2024. On the core segmentation algorithms of copy number variation detection tools. Brief Bioinform 25:bbae022
- Ben-Yaacov E, Eldar YC 2008. A fast and flexible method for the segmentation of aCGH data (HaarSeg). Bioinformatics 24:i139
- Scheinin I et al 2014. DNA copy number analysis of fresh and FFPE specimens by shallow WGS (QDNAseq). Genome Res 24:2022

## Related Skills

- copy-number/cnvkit-analysis - Read-depth caller exposing CBS/HMM/HaarSeg choices
- copy-number/gatk-cnv - Tangent normalization and ModelSegments segmentation
- copy-number/allele-specific-copy-number - ASPCF joint logR+BAF segmentation
- copy-number/recurrent-cnv - Copy-number signatures sensitive to segmentation quality
- copy-number/cnv-visualization - Visual diagnosis of oversegmentation and baseline shift
- genome-intervals/coverage-analysis - Per-bin depth computation upstream of segmentation
<!-- END FILE: copy-number/copy-ratio-segmentation/SKILL.md -->

## 子目录：copy-number/focal-amplification-ecdna

<!-- BEGIN FILE: copy-number/focal-amplification-ecdna/SKILL.md -->
---
name: bio-copy-number-focal-amplification-ecdna
description: Resolve the architecture of focal oncogene amplifications — extrachromosomal DNA (ecDNA), breakage-fusion-bridge (BFB) cycles, homogeneously staining regions (HSR), and linear amplification — from whole-genome sequencing with AmpliconArchitect, the AmpliconSuite pipeline, and AmpliconClassifier. Covers copy-number seed selection, breakpoint-graph reconstruction, balanced-flow optimization, ecDNA classification, and the limits of depth-only amplification calls. Use when a focal amplification needs structural characterization, when distinguishing ecDNA from chromosomal amplification, suspecting ecDNA-driven oncogene amplification or therapy resistance, or selecting copy-number seeds for amplicon reconstruction.
tool_type: cli
primary_tool: AmpliconArchitect
---

## Version Compatibility

Reference examples tested with: AmpliconSuite-pipeline 1.3+, AmpliconArchitect 1.3+, AmpliconClassifier 1.2+, CNVkit 0.9.10+, Python 3.10+, samtools 1.19+.

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `AmpliconSuite-pipeline.py --help`, `amplicon_classifier.py --help`
- AmpliconArchitect needs a `$AA_DATA_REPO` reference download and a Mosek license (free for academic use); confirm both are configured before running

Verify the reference build — AmpliconArchitect was historically hg19-centric; GRCh38 support and data repos exist but the build must be set explicitly and consistently.

# Focal Amplification and ecDNA

**"This oncogene is amplified — but how, structurally"** -> A depth caller reports "high focal amplification" and stops. The biology depends entirely on the *architecture*: extrachromosomal DNA (ecDNA) behaves utterly differently from a chromosomal homogeneously staining region. Resolving architecture needs the breakpoint graph, not depth.

- CLI: `AmpliconSuite-pipeline.py` (end-to-end), `AmpliconArchitect` (graph reconstruction), `AmpliconClassifier` (architecture call)
- Input: WGS BAM plus copy-number seeds (high-CN focal regions)

## Why Architecture Matters — Four Amplicon Classes

| Class | Structure | Behavior | Why it matters |
|-------|-----------|----------|----------------|
| ecDNA | Circular, episomal, no centromere | Hundreds of copies; unequal mitotic segregation; rapid CN adaptation | Drives oncogene overexpression, intratumor heterogeneity, therapy resistance; ~14% of cancers |
| BFB | Chromosomal, fold-back inversions | Stepwise CN gradient toward telomere | Distinct breakpoint signature; bounded amplification |
| HSR | Linear, integrated chromosomally | Stable inheritance | Chromosomal — segregates evenly, unlike ecDNA |
| Linear/simple | Tandem or simple amplification | Modest copy gain | Often passenger-scale; lowest oncogenic concern |

ecDNA is the highest-stakes call: because it lacks a centromere it segregates unequally, so copy number can surge under selection — a structural basis for resistance. Depth alone cannot distinguish ecDNA from an HSR; both look like a high-amplitude focal gain.

## When to Suspect ecDNA

| Signal | Interpretation |
|--------|----------------|
| Very high focal copy number (CN >> 10) at an oncogene | Consistent with ecDNA; not specific |
| Amplicon spanning multiple non-contiguous genomic segments | Suggestive — ecDNA often fuses distal regions |
| Breakpoint graph forms a closed cycle with balanced flow | AmpliconArchitect signature of circular structure |
| Highly variable per-cell copy number (single-cell / FISH) | Hallmark of unequal ecDNA segregation |
| Co-amplified enhancers distal to the oncogene | ecDNA can hijack regulatory elements |

## The AmpliconSuite Workflow

AmpliconArchitect does not call amplifications from scratch — it reconstructs the architecture of the regions it is seeded with. The pipeline is: (1) call copy number and select high-CN focal seeds, (2) AmpliconArchitect builds the breakpoint graph and optimizes a balanced flow, (3) AmpliconClassifier labels each amplicon ecDNA / BFB / HSR / linear.

```bash
# End-to-end: AmpliconSuite-pipeline runs CNVkit seeding, AmpliconArchitect, and
# AmpliconClassifier in sequence.
AmpliconSuite-pipeline.py \
    -s sample_id \
    -t 8 \
    --bam tumor.bam \
    --ref GRCh38 \
    --run_AA --run_AC

# Output: per-amplicon breakpoint graphs, cycles files, and an AmpliconClassifier
# table assigning each amplicon an architecture class.
```

Supplying explicit seeds (recommended when a vetted CNV callset exists):

```bash
# Seeds: a BED of high-copy focal regions (e.g. from cnvkit-analysis), filtered to
# CN above the seed threshold and to focal (not arm-level) size.
AmpliconSuite-pipeline.py -s sample_id -t 8 --bam tumor.bam --ref GRCh38 \
    --cnv_bed focal_seeds.bed --run_AA --run_AC
```

## Failure Modes

### Garbage copy-number seeds produce garbage amplicons

**Trigger:** Seeding AmpliconArchitect with a noisy CNV callset, a flat-reference tumor-only callset, or arm-level segments.

**Mechanism:** AmpliconArchitect reconstructs the architecture of exactly the regions it is seeded with; false high-CN seeds generate spurious amplicons, and arm-level seeds dilute the focal signal.

**Symptom:** Implausible amplicons at no known oncogene; amplicons spanning whole arms; classifier output dominated by low-confidence calls.

**Fix:** Seed only vetted, focal, high-CN regions. Build the CNV callset from a proper panel of normals (see cnvkit-analysis); filter to focal size and CN above the seed threshold before passing to AA.

### Calling ecDNA from depth alone

**Trigger:** Labeling a high-amplitude focal gain "ecDNA" without breakpoint-graph evidence.

**Mechanism:** ecDNA and a chromosomal HSR both present as high focal copy number; only the breakpoint graph (a closed cycle with balanced flow) distinguishes them.

**Symptom:** ecDNA claimed from a CNVkit/GATK profile; no graph, no cycle.

**Fix:** Require AmpliconArchitect graph reconstruction and an AmpliconClassifier ecDNA call. Where feasible, confirm with orthogonal evidence — FISH, single-cell copy number (variable per-cell CN), or optical mapping.

### Genome-build mismatch

**Trigger:** BAM aligned to one build, `--ref` or `$AA_DATA_REPO` set to another.

**Mechanism:** Coordinates and the bundled annotation diverge; breakpoints and genes are mis-assigned.

**Symptom:** Amplicons at wrong loci; AA errors on contig names.

**Fix:** Set `--ref` to match the BAM's build and confirm the corresponding `$AA_DATA_REPO` is installed; AA was historically hg19-centric, so GRCh38 must be explicit.

### Short-read limits on complex amplicon resolution

**Trigger:** Expecting a fully resolved amplicon structure from short-read WGS on a highly rearranged amplicon.

**Mechanism:** Short reads cannot phase long-range structure or traverse repeats; complex amplicons (many junctions, segmental duplications) are only partially reconstructed.

**Symptom:** Fragmented breakpoint graph; ambiguous or "unknown" classifier calls on a clearly amplified locus.

**Fix:** Treat short-read amplicon structure as a hypothesis for the most complex cases; confirm with optical mapping (AmpliconReconstructor) or long-read sequencing.

### Inadequate coverage or FFPE input

**Trigger:** Low-coverage WGS or degraded FFPE DNA.

**Mechanism:** Breakpoint detection needs sufficient discordant/split-read support; FFPE artifacts add false junctions.

**Symptom:** Missing junctions; noisy graph; unstable classification.

**Fix:** Use adequate-coverage WGS (AmpliconArchitect is designed for WGS, not panels/WES); apply FFPE-aware filtering; corroborate junctions across read-pair and split-read evidence.

## Reconciliation

| Pattern | Likely cause | Action |
|---------|--------------|--------|
| Depth caller: "amplification"; AA: ecDNA | Architecture only visible in the graph | Trust AA for architecture; depth gives amplitude only |
| AA ecDNA vs FISH negative | Subclonal ecDNA, or false-positive cycle | Check cell fraction; review graph balanced flow |
| AA "unknown" on a clear amplicon | Complex structure beyond short-read resolution | Escalate to optical mapping / long-read |
| BFB vs ecDNA ambiguous | Fold-back and circular signatures overlap | Inspect CN gradient (BFB) vs closed cycle (ecDNA) |

**Operational rule:** A depth caller establishes *that* a region is amplified and *how much*; it never establishes the architecture. An ecDNA call requires an AmpliconArchitect breakpoint graph with a closed cycle and an AmpliconClassifier ecDNA label, and ideally orthogonal confirmation (FISH, single-cell, optical mapping). Seeds must be vetted focal high-CN regions, not raw or arm-level calls.

## Quantitative Thresholds

| Threshold | Value | Source / Rationale |
|-----------|-------|--------------------|
| ecDNA prevalence | ~14% of cancers | Kim et al 2020; baseline expectation |
| CN seed threshold | CN >= ~4-5 focal | AmpliconSuite seeding; amplicons, not single-copy gains |
| Seed size | focal (sub-arm), not whole-arm | Arm-level seeds dilute focal amplicon signal |
| Assay | whole-genome sequencing | AmpliconArchitect needs genome-wide breakpoint coverage |
| Confirmation for ecDNA | graph cycle + classifier + orthogonal evidence | Depth alone is insufficient |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| Amplicons at no known oncogene | Noisy or arm-level seeds | Seed vetted focal high-CN regions only |
| ecDNA "called" from a CNVkit profile | Depth-only claim, no graph | Run AmpliconArchitect + AmpliconClassifier |
| AA errors on contig names | Build mismatch | Match `--ref` and `$AA_DATA_REPO` to the BAM |
| AA fails to start | Missing Mosek license / data repo | Configure the academic Mosek license and `$AA_DATA_REPO` |
| Fragmented graph on a clear amplicon | Short-read limits / low coverage | Confirm with optical mapping or long reads |
| Classifier output all low-confidence | Coverage too low or FFPE artifacts | Use adequate-coverage WGS; FFPE-aware filtering |

## References

- Turner KM et al 2017. Extrachromosomal oncogene amplification drives tumour evolution and genetic heterogeneity. Nature 543:122
- Deshpande V et al 2019. Exploring the landscape of focal amplifications in cancer using AmpliconArchitect. Nat Commun 10:392
- Kim H et al 2020. Extrachromosomal DNA is associated with oncogene amplification and poor outcome across multiple cancers. Nat Genet 52:891
- Luebeck J et al 2024. AmpliconSuite: an end-to-end workflow for analyzing focal amplifications in cancer genomes. bioRxiv (AmpliconSuite-pipeline)
- Luebeck J et al 2020. AmpliconReconstructor integrates NGS and optical mapping to resolve focal amplifications. Nat Commun 11:4374

## Related Skills

- copy-number/cnvkit-analysis - Generates the copy-number seeds for amplicon reconstruction
- copy-number/recurrent-cnv - Cohort-level recurrent focal amplification (GISTIC2)
- copy-number/allele-specific-copy-number - Absolute copy number of amplified loci
- copy-number/cnv-annotation - Oncogene annotation of amplified regions
- copy-number/subclonal-copy-number - Subclonal dynamics of ecDNA copy number
- long-read-sequencing/structural-variants - Long-read resolution of complex amplicons
<!-- END FILE: copy-number/focal-amplification-ecdna/SKILL.md -->

## 子目录：copy-number/gatk-cnv

<!-- BEGIN FILE: copy-number/gatk-cnv/SKILL.md -->
---
name: bio-copy-number-gatk-cnv
description: Call copy number variants with the GATK best-practices workflows — the somatic CNV pipeline (CollectReadCounts, DenoiseReadCounts with tangent normalization, ModelSegments, CallCopyRatioSegments) and the germline GATK-gCNV pipeline (DetermineGermlineContigPloidy, GermlineCNVCaller cohort/case mode, PostprocessGermlineCNVCalls). Covers panel-of-normals construction, AnnotateIntervals/FilterIntervals, allelic-count integration, and QS-based filtering. Use when integrating CNV calling into a GATK variant pipeline, calling rare germline CNVs from an exome cohort, deciding between the somatic and germline GATK workflows, or diagnosing why tangent normalization removed a real event or why gCNV output has low precision.
tool_type: cli
primary_tool: gatk
---

## Version Compatibility

Reference examples tested with: GATK 4.5+ (gatk4), Python 3.10+ (gcnv conda env), R 4.3+.

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `gatk --version` then `gatk <ToolName> --help` to confirm arguments
- gCNV requires a working `gatkcondaenv` (theano/tensorflow stack) — `gatk` will report if the Python environment is missing

GATK 4.5+ gCNV inference defaults are tuned for whole-exome data; whole-genome runs generally need parameter changes. If a tool reports an unrecognized argument, check the help for that exact GATK version rather than retrying.

# GATK CNV Workflows

**"Call CNVs the GATK way"** -> GATK has two *separate* CNV workflows that share almost no tools. Picking the wrong one is the most common mistake.

- Somatic CNV: `CollectReadCounts` -> `DenoiseReadCounts` -> `ModelSegments` -> `CallCopyRatioSegments`. Tumor copy-ratio segments, optionally allele-aware.
- Germline gCNV: `DetermineGermlineContigPloidy` -> `GermlineCNVCaller` -> `PostprocessGermlineCNVCalls`. Per-sample germline CN genotypes (VCF).

## Critical: What GATK Somatic CNV Does NOT Provide

`ModelSegments` + `CallCopyRatioSegments` produce **copy-ratio segments** and a **minor-allele fraction** per segment, and the "call" is a simple t-test emitting `+` / `-` / `0`. This is **not** integer allele-specific copy number, **not** tumor purity, and **not** ploidy. Practitioners routinely assume parity with ASCAT/FACETS and there is none. For integer allele-specific CN, purity, ploidy, LOH state, or whole-genome-doubling status, use allele-specific-copy-number (ASCAT, Sequenza, FACETS, or PureCN — PureCN can even reuse the GATK `ModelSegments` segmentation as input).

## Somatic vs Germline — Choosing the Workflow

| Question | Somatic CNV | Germline gCNV |
|----------|-------------|---------------|
| Input | One tumor (+ optional matched normal) | A cohort of constitutional samples |
| Output | Copy-ratio segments, +/-/0 call, minor-allele fraction | Integer germline CN genotype VCF per sample |
| Normalization | Tangent (projection onto PoN subspace) | PCA batching + Bayesian read-depth model |
| Cohort needed | PoN of normals for denoising | >= ~100 technically matched samples (cohort mode) |
| Use for | Tumor SCNAs, focal amplifications/deletions | Rare/de novo germline CNVs, NDD/Mendelian cohorts |

## Decision Tree by Scenario

| Scenario | Workflow | Key parameters |
|----------|----------|----------------|
| Tumor-normal WGS/WES, want SCNAs | Somatic, with matched-normal allelic counts | `PreprocessIntervals --bin-length 1000` (WGS) or `0` (WES) |
| Tumor-only somatic CNV | Somatic, no matched-normal allelic counts | Genotype hets in the case sample; expect more no-calls |
| Rare germline CNV, exome cohort >= 100 | gCNV cohort mode | Run `DetermineGermlineContigPloidy` cohort first |
| New sample vs an existing gCNV model | gCNV case mode | Must reuse identical scatter count and interval list |
| Need integer ASCN / purity / ploidy | Neither — escalate | Use allele-specific-copy-number |
| Targeted panel (< few hundred genes) | Prefer CNVkit | GATK interval models are unstable on tiny panels |

## Somatic CNV Pipeline

```bash
# 1. Preprocess and annotate intervals (WES: bin-length 0 = use exome targets as-is)
gatk PreprocessIntervals -R ref.fa -L targets.interval_list \
    --bin-length 0 --interval-merging-rule OVERLAPPING_ONLY -O preprocessed.interval_list
gatk AnnotateIntervals -R ref.fa -L preprocessed.interval_list \
    --interval-merging-rule OVERLAPPING_ONLY -O annotated.tsv     # GC content for FilterIntervals

# 2. Collect read counts (each BAM)
gatk CollectReadCounts -R ref.fa -I sample.bam -L preprocessed.interval_list \
    --interval-merging-rule OVERLAPPING_ONLY -O sample.counts.hdf5

# 3. Build the panel of normals (tangent-normalization basis)
# --minimum-interval-median-percentile 5.0 is the GATK CNV tutorial value (tool default 10.0)
gatk CreateReadCountPanelOfNormals \
    -I normal1.counts.hdf5 -I normal2.counts.hdf5 -I normalN.counts.hdf5 \
    --annotated-intervals annotated.tsv \
    --minimum-interval-median-percentile 5.0 -O cnv.pon.hdf5

# 4. Denoise tumor against the PoN (tangent normalization)
gatk DenoiseReadCounts -I tumor.counts.hdf5 --count-panel-of-normals cnv.pon.hdf5 \
    --standardized-copy-ratios tumor.standardizedCR.tsv \
    --denoised-copy-ratios tumor.denoisedCR.tsv

# 5. Allelic counts at common biallelic SNPs (tumor and matched normal)
gatk CollectAllelicCounts -R ref.fa -I tumor.bam -L common_snps.interval_list \
    -O tumor.allelicCounts.tsv
gatk CollectAllelicCounts -R ref.fa -I normal.bam -L common_snps.interval_list \
    -O normal.allelicCounts.tsv

# 6. Joint segmentation of copy ratio and allele fraction
gatk ModelSegments --denoised-copy-ratios tumor.denoisedCR.tsv \
    --allelic-counts tumor.allelicCounts.tsv \
    --normal-allelic-counts normal.allelicCounts.tsv \
    --output-prefix tumor -O segments/

# 7. Call each segment +/-/0 (simple t-test against the copy-ratio baseline)
gatk CallCopyRatioSegments -I segments/tumor.cr.seg -O segments/tumor.called.seg
```

`AnnotateIntervals` (step 1) and supplying `--annotated-intervals` to the PoN are frequently skipped — they enable explicit GC-bias correction and are recommended.

## Germline gCNV Pipeline

```bash
# 1. Determine contig ploidy across the cohort (karyotype + global depth)
gatk DetermineGermlineContigPloidy -L preprocessed.interval_list \
    --interval-merging-rule OVERLAPPING_ONLY \
    -I sample1.counts.hdf5 -I sampleN.counts.hdf5 \
    --contig-ploidy-priors ploidy_priors.tsv --output-prefix cohort -O ploidy-calls/

# 2. FilterIntervals — remove low-mappability / extreme-GC / low-count intervals
gatk FilterIntervals -L preprocessed.interval_list --annotated-intervals annotated.tsv \
    -I sample1.counts.hdf5 -I sampleN.counts.hdf5 \
    --interval-merging-rule OVERLAPPING_ONLY -O filtered.interval_list

# 3. GermlineCNVCaller, cohort mode (builds the model AND calls the cohort)
gatk GermlineCNVCaller --run-mode COHORT -L filtered.interval_list \
    --interval-merging-rule OVERLAPPING_ONLY \
    --contig-ploidy-calls ploidy-calls/cohort-calls \
    -I sample1.counts.hdf5 -I sampleN.counts.hdf5 \
    --output-prefix cohort -O gcnv-calls/

# 4. Post-process per sample into a genotyped VCF
gatk PostprocessGermlineCNVCalls \
    --calls-shard-path gcnv-calls/cohort-calls \
    --model-shard-path gcnv-calls/cohort-model \
    --contig-ploidy-calls ploidy-calls/cohort-calls \
    --sample-index 0 \
    --output-genotyped-intervals sample0.intervals.vcf.gz \
    --output-genotyped-segments sample0.segments.vcf.gz \
    --output-denoised-copy-ratios sample0.denoisedCR.tsv
```

Case mode (`--run-mode CASE`) scores a new sample against the cohort `*-model` shards; it must use the **identical** `filtered.interval_list` and the **same scatter count** as the cohort run, or it fails or produces incomparable calls.

## Failure Modes

### Tangent normalization removes a real CNV

**Trigger:** PoN is small (< ~20 normals) or contains samples that share a recurrent CNV (e.g. a common germline CNV, or a PoN accidentally built from tumors).

**Mechanism:** `DenoiseReadCounts` projects the tumor coverage profile onto the subspace spanned by the PoN's principal components. Any copy-number pattern present in that subspace is treated as "systematic noise" and subtracted. A CNV shared by PoN members is therefore normalized out of the tumor.

**Symptom:** A known event (recurrent amplification/deletion, or a common germline CNV) is absent from `denoisedCR.tsv`; denoised profile is suspiciously flat at that locus.

**Fix:** Build the PoN from >= 20-40 unrelated, tumor-free, process-matched normals. Never put tumors in the PoN. Cross-check against the `standardizedCR.tsv` (pre-tangent) profile — if the event is there but gone after denoising, the PoN ate it.

### Mistaking ModelSegments output for allele-specific integer CN

**Trigger:** Treating `tumor.modelFinal.seg` minor-allele fraction as integer minor copy number, or expecting a purity/ploidy field.

**Mechanism:** GATK somatic CNV models copy ratio and allele fraction but never fits the purity/ploidy grid that converts log-ratio to integer absolute CN.

**Symptom:** No purity/ploidy in any output; "copy number" is continuous log2; LOH is a low minor-allele fraction, not an explicit CN-LOH state.

**Fix:** Accept GATK somatic CNV as a relative caller. For integer ASCN, feed the data to PureCN (`segmentationGATK4` reuses GATK segments), FACETS, ASCAT, or Sequenza — see allele-specific-copy-number.

### FilterIntervals silently drops intervals containing real variants

**Trigger:** Aggressive mappability or segmental-duplication cutoffs in `FilterIntervals`.

**Mechanism:** A minimum mappability > 0 or a maximum segmental-duplication content < 1 excludes intervals overlapping segdups and low-mappability regions — exactly where many disease-relevant CNVs (e.g. recurrent genomic-disorder loci flanked by segdups) live.

**Symptom:** Known recurrent CNVs at segdup-mediated loci are never called; the gene of interest has no intervals in `filtered.interval_list`.

**Fix:** Inspect `filtered.interval_list` for genes of interest before calling. Relax mappability/segdup cutoffs for targeted analyses; for genomic-disorder loci, depth-based callers are inherently limited near segdups — confirm with an orthogonal assay.

### Raw gCNV output has ~22% precision

**Trigger:** Using unfiltered `GermlineCNVCaller` / `PostprocessGermlineCNVCalls` output for association or de novo analysis.

**Mechanism:** gCNV is tuned for high recall (~95% of rare coding CNVs >= 2 exons) at the cost of precision; raw calls are dominated by false positives.

**Symptom:** Implausibly many rare CNVs per sample; de novo CNV rate far above the expected ~0.01-0.02/genome.

**Fix:** Apply the QS (quality score) filter. QS > 100 is a common starting threshold; QS > 1000 reaches ~96% precision. Also apply sample-level filters (call rate, number of CNVs per sample) per Babadi 2023.

### gCNV cohort too small or mismatched

**Trigger:** Cohort mode with < ~100 samples, or a cohort spanning multiple capture kits / library protocols.

**Mechanism:** The Bayesian model needs enough technically similar samples to learn coverage bias; mixed protocols are not separable and the model misattributes batch effects to copy number.

**Symptom:** Unstable calls; many CNVs tracking sequencing batch; model fails to converge.

**Fix:** Use >= 100 process-matched samples per cohort model; split heterogeneous cohorts by capture kit. For < 100 samples, gCNV case mode against an external compatible model, or a cohort caller like ExomeDepth, is more appropriate — see germline-cnv-interpretation.

## Reconciliation: GATK vs Other Callers

| Pattern | Likely cause | Action |
|---------|--------------|--------|
| GATK somatic flat where CNVkit calls a focal event | Tangent normalization absorbed it | Check `standardizedCR.tsv`; rebuild PoN without the event |
| GATK and ASCAT disagree on a "deletion" | GATK has no purity model; the event is subclonal or impure | Trust ASCAT/FACETS integer ASCN |
| gCNV calls a CNV ExomeDepth misses | Different sensitivity profiles; both have poor inter-tool concordance | Require QS filtering + a second caller for rare-CNV claims |
| gCNV CNV count tracks batch | Cohort mixes protocols | Re-batch by capture kit |

**Operational rule:** GATK somatic CNV output is relative copy ratio — report it as gain/loss/neutral, not absolute CN, unless downstream-fit by an allele-specific tool. gCNV calls are reportable only after QS and sample-level filtering, and rare-CNV or de novo claims need orthogonal confirmation.

## Quantitative Thresholds

| Threshold | Value | Source / Rationale |
|-----------|-------|--------------------|
| PoN size (somatic) | >= 20-40 normals | Larger PoN = stabler tangent subspace; small PoN over-fits |
| gCNV cohort size | >= ~100 technically matched | Babadi 2023 Nat Genet; model needs coverage-bias signal |
| gCNV QS for high precision | QS > 1000 -> ~96% precision | Babadi 2023; raw output ~22% precision, ~95% recall |
| `minimum-interval-median-percentile` | 10.0 default; 5.0 in the GATK CNV tutorial | Drops the lowest-coverage intervals from the PoN |
| WGS bin length | ~1000 bp | `PreprocessIntervals --bin-length 1000`; WES uses 0 (targets as-is) |
| Het sites for somatic ModelSegments | >= ~10,000 (WGS) | Sparse hets give noisy minor-allele-fraction segmentation |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| `gatkcondaenv` / theano error in gCNV | gCNV Python env not installed | Install the GATK conda env; gCNV cannot run without it |
| "At least one interval must remain" in FilterIntervals | All intervals filtered out | Relax mappability/GC/count cutoffs; check annotated.tsv |
| Case-mode gCNV fails or gives odd calls | Different scatter count or interval list vs cohort model | Reuse the exact cohort scatter count and `filtered.interval_list` |
| Denoised profile flat at a known event | Tangent normalization removed it | Rebuild PoN larger, tumor-free; inspect standardizedCR |
| ModelSegments has few het sites | SNP interval list misses captured regions | Use a common-SNP list intersected with the capture targets |
| Expecting purity/ploidy in output | Somatic CNV does not estimate them | Use allele-specific-copy-number |

## References

- GATK Best Practices: Somatic copy number variant discovery (CNV). Broad Institute documentation.
- Babadi M et al 2023. GATK-gCNV enables the discovery of rare copy number variants from exome sequencing data. Nat Genet 55:1589
- Gao GF, Oh C, Saksena G, Tabak B, Beroukhim R, Getz G et al 2022. Tangent normalization for somatic copy-number inference in cancer genome analysis. Bioinformatics 38:4677 (Tabak is a middle, not first, author).

## Related Skills

- copy-number/allele-specific-copy-number - Integer ASCN, purity, ploidy (ASCAT/Sequenza/FACETS/PureCN)
- copy-number/copy-ratio-segmentation - Segmentation algorithms and depth normalization theory
- copy-number/cnvkit-analysis - Read-depth CNV calling for panels and exomes
- copy-number/germline-cnv-interpretation - ACMG/ClinGen classification of germline CNV calls
- copy-number/cnv-visualization - Plotting GATK denoised ratios and modeled segments
- copy-number/recurrent-cnv - Cohort-level recurrent and driver CNV
- variant-calling/gatk-variant-calling - GATK SNV/indel pipeline for allelic-count SNP sites
<!-- END FILE: copy-number/gatk-cnv/SKILL.md -->

## 子目录：copy-number/germline-cnv-interpretation

<!-- BEGIN FILE: copy-number/germline-cnv-interpretation/SKILL.md -->
---
name: bio-copy-number-germline-cnv-interpretation
description: Classify constitutional (germline) copy number variants for clinical reporting using the 2019 ACMG/ClinGen technical standards points-based framework, with ClassifyCNV and AnnotSV for semi-automated scoring. Covers the separate copy-number-loss and copy-number-gain rubrics, the five-tier classification, ClinGen haploinsufficiency/triplosensitivity and dosage-sensitive regions, de novo and segregation evidence, and population-frequency benign evidence. Use when assigning pathogenic/likely-pathogenic/VUS/likely-benign/benign to a constitutional CNV, scoring a CNV against ACMG/ClinGen criteria, or distinguishing the automatable evidence from the case-specific evidence requiring manual input.
tool_type: mixed
primary_tool: ClassifyCNV
---

## Version Compatibility

Reference examples tested with: ClassifyCNV 1.1+, AnnotSV 3.4+, Python 3.10+ with pandas 2.2+; bedtools 2.31+.

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `python ClassifyCNV.py --help`, `AnnotSV --version`
- Update the bundled ClinGen/dosage databases — ClassifyCNV ships an `update_clingen.sh`; dosage curation changes, and a stale database silently mis-scores.

This skill is for **constitutional/germline** CNVs only. Somatic tumor CNVs use a different framework (AMP/ASCO/CAP and OncoKB tiers) — do not apply ACMG/ClinGen constitutional scoring to a tumor.

# Germline CNV Interpretation

**"Is this constitutional CNV pathogenic"** -> Apply the 2019 ACMG/ClinGen technical standards: a semiquantitative, points-based rubric that sums evidence into one of five clinical categories. There are two separate rubrics — one for copy-number **loss**, one for copy-number **gain** — because the evidence for deletion and duplication pathogenicity is different. The total score maps to a five-tier classification.

- CLI: `ClassifyCNV` (automates the observed-evidence sections), `AnnotSV` (ACMG-aligned rank)
- Manual: case-specific evidence (de novo status, segregation, prior literature) is scored by the interpreter, not the tool

## The Points Framework

| Total score | Classification |
|-------------|----------------|
| >= 0.99 | Pathogenic |
| 0.90 to 0.98 | Likely pathogenic |
| -0.89 to 0.89 | Variant of uncertain significance (VUS) |
| -0.90 to -0.98 | Likely benign |
| <= -0.99 | Benign |

Evidence is grouped into sections (the loss and gain rubrics each have five). For copy-number **loss**: Section 1 — does the CNV contain protein-coding or functionally important elements; Section 2 — overlap with established haploinsufficient genes/regions (strong positive) or established benign regions (strong negative); Section 3 — number of protein-coding genes; Section 4 — detailed case/literature evidence (case-control, prior probands, phenotype specificity); Section 5 — inheritance (de novo with confirmed parentage is strong positive; inherited from an unaffected parent is negative). The **gain** rubric is structured the same way but keyed to triplosensitivity and the distinct evidence base for duplications.

The decisive postdoc-level point: **a tool can only score the evidence it is given.** ClassifyCNV and AnnotSV automate Sections 1-3 (gene content, dosage-region overlap, population frequency) well; Sections 4-5 (de novo status, segregation, literature) require the interpreter to supply points. An unsupervised tool run therefore systematically lands CNVs in VUS — the absence of family/literature evidence is not neutral, it is unscored.

## Classification Workflow

| Step | Source | Automatable |
|------|--------|-------------|
| Gene content, functional elements | RefSeq/GENCODE | Yes (ClassifyCNV/AnnotSV) |
| Established HI/TS gene & region overlap | ClinGen dosage map | Yes |
| Protein-coding gene count | Gene model | Yes |
| Population frequency (benign evidence) | gnomAD-SV, DGV | Yes |
| Case-control / prior probands / phenotype fit | Literature, DECIPHER, internal DB | Partial — interpreter scores |
| De novo status, segregation | Trio/family data | No — interpreter scores |

## Semi-Automated Scoring with ClassifyCNV

**Goal:** Score the automatable ACMG/ClinGen sections for a set of constitutional CNVs.

**Approach:** Provide CNVs as a BED with an explicit DEL/DUP type; ClassifyCNV applies the 2019 rubric against the bundled ClinGen databases and emits a per-CNV scoresheet.

```bash
# Input BED: chrom, start, end, type  (type = DEL or DUP)
python ClassifyCNV.py \
    --infile constitutional_cnvs.bed \
    --GenomeBuild hg38 \
    --precise \
    --outdir classifycnv_out

# Output Scoresheet.txt: per-CNV total score, classification, and per-criterion points.
```

```python
import pandas as pd

def review_classifycnv(scoresheet):
    '''Flag CNVs whose ACMG class likely changes once case-specific evidence is added.'''
    df = pd.read_csv(scoresheet, sep='\t')
    # VUS CNVs near a tier boundary are the ones where de novo / segregation evidence
    # (Sections 4-5, not scored automatically) would tip the classification.
    df['near_boundary'] = df['Total score'].between(0.60, 0.89) | \
                          df['Total score'].between(-0.89, -0.60)
    df['needs_manual_evidence'] = (df['Classification'] == 'VUS') & df['near_boundary']
    return df
```

## Comprehensive Annotation Cross-Check with AnnotSV

```bash
AnnotSV -SVinputFile constitutional_cnvs.vcf -genomeBuild GRCh38 \
    -annotationMode both -outputFile annotsv_out.tsv
# AnnotSV emits an ACMG-aligned rank (1 benign - 5 pathogenic) per SV; use it to
# cross-check ClassifyCNV, not as a standalone clinical classification.
```

## Failure Modes

### Applying constitutional scoring to a somatic CNV

**Trigger:** Running ACMG/ClinGen germline classification on tumor copy number.

**Mechanism:** The 2019 standards are explicitly constitutional; somatic CNV clinical significance uses the AMP/ASCO/CAP tier system and oncology evidence (therapy, prognosis).

**Symptom:** Tumor amplifications classified as "pathogenic germline variants"; clinically meaningless report.

**Fix:** Confirm the CNV is constitutional (present in germline DNA). For tumors, use somatic oncology frameworks — see clinical-databases/variant-prioritization.

### Treating a tool's VUS as a final answer

**Trigger:** Reporting ClassifyCNV/AnnotSV output verbatim without adding case evidence.

**Mechanism:** Tools score gene content, dosage overlap, and frequency, but not de novo status, segregation, or literature; absent that input the score sits in the VUS band.

**Symptom:** Nearly every novel CNV classified VUS; clinically relevant de novo deletions under-called.

**Fix:** Treat tool output as the Section 1-3 baseline. Add Section 4-5 points from trio data, segregation, DECIPHER, and literature before issuing a classification. A VUS near a tier boundary specifically signals missing case evidence.

### Stale ClinGen dosage database

**Trigger:** Using ClassifyCNV/AnnotSV bundled databases without updating.

**Mechanism:** ClinGen dosage curation is ongoing; HI/TS scores and dosage-sensitive regions change. A stale database scores Section 2 wrong.

**Symptom:** A gene with a newly curated HI score 3 is scored as having no dosage evidence; classification too low.

**Fix:** Run the database update script before a classification batch; record the ClinGen release date in the report.

### Genome-build mismatch

**Trigger:** CNV coordinates and the `--GenomeBuild` argument (or annotation databases) on different builds.

**Mechanism:** Coordinates silently shift; the wrong genes and dosage regions are scored.

**Symptom:** Implausible gene content; a known disorder locus scored as gene-poor.

**Fix:** Confirm CNV coordinates, `--GenomeBuild`, and all databases are the same build; verify a landmark CNV.

### Partial-gene overlap scored as whole-gene loss

**Trigger:** Scoring a deletion that removes only part of a haploinsufficient gene as a full-gene loss.

**Mechanism:** The rubric distinguishes whole-gene loss from partial overlap; a deletion of a few exons may create a truncating allele with different (sometimes greater) impact, scored under different criteria.

**Symptom:** Partial-gene CNVs mis-scored; truncating deletions under- or over-weighted.

**Fix:** Record whether the CNV removes the whole gene or part of it, and which exons; apply the rubric's partial-overlap criteria explicitly.

## Reconciliation

| Pattern | Likely cause | Action |
|---------|--------------|--------|
| ClassifyCNV VUS, AnnotSV rank 4 | Different weighting of the same evidence | Re-derive points manually against the 2019 standard |
| Tool says benign, locus is a known disorder | Stale dosage database or build mismatch | Update databases; verify build |
| Two interpreters disagree on a VUS | Section 4-5 evidence weighted differently | Use the ClinGen calculator; document each criterion |
| De novo deletion still VUS | Section 5 points not added | Add confirmed-de-novo points |

**Operational rule:** A clinical CNV classification is final only when (1) the CNV is confirmed constitutional, (2) databases and builds are current and consistent, (3) the automatable Sections 1-3 are scored by a tool, and (4) the interpreter has scored Sections 4-5 from case-specific evidence. Document each criterion and its points; the ClinGen web calculator is the reference tally.

## Quantitative Thresholds

| Threshold | Value | Source / Rationale |
|-----------|-------|--------------------|
| Pathogenic | total score >= 0.99 | Riggs 2020 ACMG/ClinGen technical standards |
| Likely pathogenic | 0.90 to 0.98 | Riggs 2020 |
| VUS | -0.89 to 0.89 | Riggs 2020 |
| Likely benign | -0.90 to -0.98 | Riggs 2020 |
| Benign | <= -0.99 | Riggs 2020 |
| Established dosage sensitivity | ClinGen HI/TS score = 3 | ClinGen: sufficient evidence |
| Common-CNV benign frequency | high population frequency | Section 2/4 benign evidence |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| Tumor CNVs classified "pathogenic germline" | Constitutional rubric applied to somatic | Use somatic oncology frameworks |
| Almost everything classified VUS | Sections 4-5 not scored | Add de novo/segregation/literature points |
| Known disorder locus scored benign | Stale dosage DB or build mismatch | Update ClinGen databases; check build |
| Wrong genes scored | Build mismatch | Align coordinates, --GenomeBuild, databases |
| Partial-gene deletion mis-scored | Whole-gene assumption | Apply partial-overlap criteria |
| ClassifyCNV vs AnnotSV disagree | Different evidence weighting | Re-derive against the 2019 standard manually |

## References

- Riggs ER et al 2020. Technical standards for the interpretation and reporting of constitutional copy-number variants: a joint consensus recommendation of ACMG and ClinGen. Genet Med 22:245
- Gurbich TA, Ilinsky VV 2020. ClassifyCNV: a tool for clinical annotation of copy-number variants. Sci Rep 10:20375
- Geoffroy V et al 2018. AnnotSV: an integrated tool for structural variations annotation. Bioinformatics 34:3572
- Rehm HL et al 2015 NEJM 372:2235 (ClinGen launch / framework). Dosage-sensitivity curation methodology is in Riggs ER et al 2012 Clin Genet 81:403 (original ClinGen dosage-sensitivity workflow). Current ClinGen Dosage Sensitivity Map: clinicalgenome.org.

## Related Skills

- copy-number/cnv-annotation - Gene, dosage, and database annotation feeding the rubric
- copy-number/gatk-cnv - GATK-gCNV germline CNV calling
- copy-number/cnvkit-analysis - Germline CNV calling from panels/exomes
- clinical-databases/clinvar-lookup - ClinVar CNV records and prior classifications
- clinical-databases/variant-prioritization - Somatic variant tiering (the non-germline path)
- clinical-databases/gnomad-frequencies - Population frequency for benign evidence
<!-- END FILE: copy-number/germline-cnv-interpretation/SKILL.md -->

## 子目录：copy-number/hrd-scoring

<!-- BEGIN FILE: copy-number/hrd-scoring/SKILL.md -->
---
name: bio-copy-number-hrd-scoring
description: Quantify homologous recombination deficiency (HRD) from tumor copy number using the three genomic-scar metrics — loss of heterozygosity (LOH), large-scale state transitions (LST), and telomeric allelic imbalance (TAI) — with scarHRD, and via the whole-genome HRDetect and CHORD models. Covers the genomic instability score, the PARP-inhibitor clinical context, whole-genome-doubling correction, and the scar-versus-state distinction. Use when computing an HRD score for PARP-inhibitor eligibility, deriving LOH/LST/TAI scars from allele-specific copy number, deciding between scar-based and mutational-signature HRD methods, or interpreting an HRD result in a BRCA-reverted or low-purity tumor.
tool_type: mixed
primary_tool: scarHRD
---

## Version Compatibility

Reference examples tested with: R 4.3+ with scarHRD 0.1.1+, sequenza 3.0+ (allele-specific input); HRDetect / CHORD as their respective R packages where whole-genome data is available.

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('scarHRD')` then `?scar_score` to confirm arguments
- scarHRD is GitHub-only (`sztup/scarHRD`); install with `remotes::install_github`

scarHRD consumes allele-specific copy number — a Sequenza `.seqz` file or an ASCAT/allele-specific segment table. It cannot run on relative log2 copy ratio.

# HRD Scoring

**"Is this tumor homologous-recombination deficient"** -> HRD leaves characteristic copy-number scars. Three are quantified and summed into an HRD score: loss of heterozygosity (LOH), large-scale state transitions (LST), and telomeric allelic imbalance (TAI). A high score predicts response to platinum chemotherapy and PARP inhibitors. The scar score is a *consequence* of past HR deficiency — which is both its strength (it integrates over tumor history) and its key limitation.

- R: `scarHRD` — the three genomic scars and their sum
- Whole-genome: `HRDetect` (weighted multi-signature model), `CHORD` (random forest)
- Input: allele-specific copy number from Sequenza or ASCAT (see allele-specific-copy-number)

## The Three Genomic Scars

| Scar | Definition | Captures |
|------|------------|----------|
| HRD-LOH | Number of LOH segments > 15 Mb but shorter than a whole chromosome | Large interstitial allelic loss |
| LST | Chromosomal breaks between adjacent segments each >= 10 Mb, separated by < 3 Mb | Large-scale rearrangement burden |
| TAI | Number of subtelomeric regions with allelic imbalance not crossing the centromere | Telomere-bounded allelic imbalance |

The HRD score is the sum of the three (the "genomic instability score", GIS). Each component has a precise size rule — these thresholds (15 Mb, 10 Mb, 3 Mb) are not arbitrary; they were selected to correlate with BRCA1/BRCA2/RAD51C deficiency (Abkevich 2012, Popova 2012, Birkbak 2012).

## Method Selection

| Method | Input | Strength | Fails when |
|--------|-------|----------|------------|
| scarHRD (LOH+LST+TAI) | Allele-specific CN (panel/WES/WGS) | Works on panels; the clinical-assay basis | Low purity; LST not WGD-corrected; relative CN input |
| HRDetect | Whole-genome (SNV sig 3, SV signatures, HRD index, indel microhomology) | Most accurate; integrates substitution + rearrangement signatures | Needs WGS; not applicable to panels/WES |
| CHORD | Whole-genome somatic mutation contexts | Distinguishes BRCA1- vs BRCA2-type deficiency | Needs WGS; somatic calls required |

Decision: for a targeted panel or WES the genomic-scar score (scarHRD-style) is the only option and is the basis of approved companion diagnostics; for whole-genome data, HRDetect or CHORD are more accurate because they add mutational-signature evidence.

## Computing Genomic Scars with scarHRD

**Goal:** Compute LOH, LST, TAI, and the HRD sum from allele-specific copy number.

**Approach:** Run scarHRD on a Sequenza `.seqz` file (or an allele-specific segment table); supply the genome build and ploidy so LST is correctly normalized.

```r
library(scarHRD)

# From a Sequenza .seqz file (allele-specific copy number, with BAF).
hrd <- scar_score('sample.small.seqz.gz',
                  reference = 'grch38',
                  seqz = TRUE)
# hrd is a one-row data frame with columns 'HRD' (LOH), 'Telomeric AI', 'LST', 'HRD-sum'.

# From a pre-computed allele-specific segment table (ASCAT-style: SampleID, Chromosome,
# Start_position, End_position, total_cn, A_cn, B_cn, ploidy):
hrd_seg <- scar_score('sample_allele_specific.txt',
                      reference = 'grch38', seqz = FALSE)
print(hrd_seg)
```

## The Postdoc-Level Caveats

Three points separate a correct HRD interpretation from a naive one:

1. **HRD is a scar, not a current state.** The score reflects HR deficiency that *occurred* during tumor evolution. A tumor that has acquired a BRCA reversion mutation — a real platinum/PARP-inhibitor resistance mechanism — still carries the scars and still scores HRD-high. A high score is not a guarantee of current HR deficiency or of drug response.
2. **LST is ploidy-dependent.** Whole-genome doubling adds breakpoints and inflates the LST count independently of HR status. The score must be computed with the correct ploidy so LST is normalized; an uncorrected WGD tumor can score falsely high.
3. **The score needs allele-specific input.** LOH and TAI are allelic-imbalance metrics — they cannot be derived from total copy number or relative log2. Garbage allele-specific input (low purity, sparse hets) gives a garbage score.

## Failure Modes

### Relative copy number used as input

**Trigger:** Feeding log2 copy ratio or total-CN segments to a scar calculator.

**Mechanism:** LOH and TAI require the minor allele copy number; relative or total CN has no allelic information.

**Symptom:** LOH and TAI near zero regardless of true HRD; nonsensical score.

**Fix:** Use allele-specific copy number from Sequenza or ASCAT (allele-specific-copy-number). The `.seqz` file or an A/B-allele segment table is the correct input.

### LST inflated by uncorrected whole-genome doubling

**Trigger:** Running the scar score without supplying the tumor's ploidy, on a WGD tumor.

**Mechanism:** WGD multiplies segments and breakpoints; LST counts breaks and rises with ploidy independent of HR deficiency.

**Symptom:** A WGD tumor with no BRCA/HR pathway lesion scores HRD-high, driven by LST.

**Fix:** Compute the score with the correct ploidy so LST is normalized. Cross-check a high LST-driven score against HR-pathway gene status and against mutational signature 3.

### Treating a high score as proof of drug response

**Trigger:** Equating HRD-high with current HR deficiency and predicted PARP-inhibitor benefit.

**Mechanism:** The scar persists after HR function is restored (BRCA reversion, other resistance mechanisms); the score integrates over history.

**Symptom:** An HRD-high tumor fails to respond; the score was correct but the tumor is no longer HR-deficient.

**Fix:** Interpret the score as evidence of past HRD. Where possible, integrate current HR-pathway status (BRCA1/2 reversion screening, RAD51 foci assays) before predicting response.

### Low tumor purity

**Trigger:** Computing HRD on a low-purity sample (< ~30-40%).

**Mechanism:** Allele-specific calling fails at low purity (see allele-specific-copy-number); scar counts then derive from an unreliable profile.

**Symptom:** Score unstable across reruns; LOH/TAI near zero on a genome with visible imbalance.

**Fix:** Confirm purity is adequate before scoring; report indeterminate below ~30%.

### Panel HRD score read as a whole-genome score

**Trigger:** Comparing a targeted-panel HRD score directly to a WGS-derived score or to a companion-diagnostic cutoff.

**Mechanism:** Genomic coverage and segment resolution differ; scar counts are not numerically interchangeable across assays.

**Symptom:** A panel score compared to the GIS >= 42 cutoff gives the wrong call.

**Fix:** Use the cutoff validated for the specific assay. Companion-diagnostic thresholds (e.g. Myriad myChoice GIS >= 42) are validated for that assay's design, not portable.

## Reconciliation

| Pattern | Likely cause | Action |
|---------|--------------|--------|
| scarHRD high, HRDetect low | LST-driven score from WGD, not true HRD | Check ploidy correction and signature 3 |
| HRD-high tumor, BRCA wild-type | Other HR lesion, or false-high from WGD/quality | Check RAD51C/PALB2, methylation; verify input |
| HRD-high tumor fails PARP-inhibitor | Scar persists after BRCA reversion | Screen for reversion mutations |
| Panel and WGS scores disagree | Different assay resolution | Use the assay-validated cutoff for each |

**Operational rule:** An HRD score is interpretable only when (1) the input is allele-specific copy number from an adequately pure sample, (2) LST is computed with the correct ploidy, (3) the assay-validated cutoff is used, and (4) the score is read as evidence of *past* HR deficiency, integrated with current HR-pathway status before predicting therapy response.

## Quantitative Thresholds

| Threshold | Value | Source / Rationale |
|-----------|-------|--------------------|
| HRD-LOH segment size | > 15 Mb, < whole chromosome | Abkevich 2012; correlates with BRCA1/2/RAD51C deficiency |
| LST adjacent-segment size | each >= 10 Mb, gap < 3 Mb | Popova 2012 |
| TAI | subtelomeric allelic imbalance not crossing the centromere | Birkbak 2012 |
| Genomic instability score (GIS) cutoff | >= 42 (Myriad myChoice) | Telli 2016; assay-specific, not portable |
| Purity floor for scoring | ~30-40% | Below this, allele-specific input is unreliable |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| LOH/TAI ~0 on an imbalanced genome | Relative/total CN used as input | Use allele-specific CN (Sequenza/ASCAT) |
| BRCA-wild-type tumor scores HRD-high | LST inflated by uncorrected WGD | Supply correct ploidy; check signature 3 |
| HRD-high tumor does not respond | Scar persists after BRCA reversion | Screen for reversion; assay current HR status |
| Score unstable across reruns | Low purity | Confirm purity; report indeterminate if low |
| Panel score fails the GIS >= 42 call | Cross-assay cutoff misuse | Use the assay-validated threshold |
| scarHRD install fails | GitHub-only package | `remotes::install_github('sztup/scarHRD')` |

## References

- Abkevich V et al 2012. Patterns of genomic loss of heterozygosity predict homologous recombination repair defects in epithelial ovarian cancer. Br J Cancer 107:1776
- Popova T et al 2012. Ploidy and large-scale genomic instability consistently identify basal-like breast carcinomas with BRCA1/2 inactivation. Cancer Res 72:5454
- Birkbak NJ et al 2012. Telomeric allelic imbalance indicates defective DNA repair and sensitivity to DNA-damaging agents. Cancer Discov 2:366
- Telli ML et al 2016. Homologous recombination deficiency (HRD) score predicts response to platinum-containing neoadjuvant chemotherapy. Clin Cancer Res 22:3764
- Davies H et al 2017. HRDetect is a predictor of BRCA1 and BRCA2 deficiency based on mutational signatures. Nat Med 23:517
- Sztupinszki Z et al 2018. Migrating the SNP array-based homologous recombination deficiency measures to next generation sequencing data (scarHRD). NPJ Breast Cancer 4:16

## Related Skills

- copy-number/allele-specific-copy-number - Allele-specific copy number input for the scars
- copy-number/subclonal-copy-number - Whole-genome-doubling detection for LST correction
- copy-number/recurrent-cnv - Copy-number signatures, including the HRD-associated signature
- copy-number/cnv-annotation - Annotating HR-pathway gene copy-number status
- clinical-databases/somatic-signatures - SNV mutational signature 3 (HRD substitution signature)
- clinical-databases/variant-prioritization - BRCA1/2 and HR-pathway variant interpretation
<!-- END FILE: copy-number/hrd-scoring/SKILL.md -->

## 子目录：copy-number/recurrent-cnv

<!-- BEGIN FILE: copy-number/recurrent-cnv/SKILL.md -->
---
name: bio-copy-number-recurrent-cnv
description: Identify recurrent and driver copy number alterations across a tumor cohort with GISTIC2 (G-score, Ziggurat deconstruction, focal vs broad/arm-level analysis, q-values from permutation) and quantify copy-number signatures with the Steele 2022 COSMIC framework and the Drews 2022 CINSignatures framework. Covers driver-gene localization from recurrence peaks, distinguishing focal drivers from arm-level passengers, and the caller-sensitivity caveats of copy-number signatures. Use when finding recurrently amplified or deleted regions in a cohort, localizing driver genes, separating focal from broad events, running GISTIC2, or extracting copy-number mutational signatures.
tool_type: mixed
primary_tool: gistic2
---

## Version Compatibility

Reference examples tested with: GISTIC 2.0.23, R 4.3+ with CINSignatureQuantification 1.2+; Python 3.10+ with SigProfilerAssignment 0.1+ (optional, COSMIC CN signatures).

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `gistic2 --help` (GISTIC 2.0 is a MATLAB-compiled binary; needs the MCR runtime)
- R: `packageVersion('CINSignatureQuantification')`
- Python: `pip show SigProfilerAssignment`

GISTIC 2.0 has had no substantive release since ~2017; it is effectively frozen. It runs as a compiled binary against the MATLAB Compiler Runtime — there is no R or Python package. Verify the reference (`-refgene`) `.mat` file matches the genome build.

# Recurrent and Driver Copy Number Alteration

**"Which copy number changes recur across my cohort, and which gene is the driver"** -> A CNV in one tumor is an observation; a CNV recurring across many tumors beyond chance is evidence of selection. GISTIC2 separates recurrent driver events from passengers by modeling a background rate and scoring each locus by how often, and how strongly, it is altered. Copy-number signatures decompose the genome-wide pattern of alterations into the mutational processes that generated them.

- CLI: `gistic2` — cohort-level recurrence, focal vs broad, driver localization
- R: `CINSignatureQuantification` (Drews 2022); Python `SigProfilerAssignment` (Steele 2022 COSMIC)

## How GISTIC2 Works — and Its Limits

GISTIC2 scores each genomic marker with a **G-score** = frequency of alteration x mean amplitude, separately for amplifications and deletions. Significance (**q-value**) comes from permuting events along the genome under the null that all are passengers. **Ziggurat deconstruction** decomposes each sample's profile into the additive arm-level and focal events that produced it, so the background rate is estimated separately for broad and focal alterations — without this, ubiquitous arm-level events swamp the focal signal. A **peel-off** procedure removes the contribution of each significant peak before testing the next, so one strong driver does not mask its neighbors.

Two postdoc-level caveats define how GISTIC2 output must be read:

1. **q-values are cohort-size dependent.** Larger N manufactures more "significant" peaks. A peak list from N=50 and one from N=500 are not comparable; recurrence *frequency* is the portable quantity, not the q-value.
2. **GISTIC2 is only as good as its input segmentation.** Oversegmented seg files produce spurious narrow peaks. The seg file must also be correctly **centered** on diploid — a mis-centered profile (WGD genome centered on tetraploid) inverts every call before GISTIC even runs.

## Decision Tree

| Goal | Approach | Notes |
|------|----------|-------|
| Find recurrent focal drivers in a cohort | GISTIC2, focal analysis, peak regions | Driver = recurrence-peak gene with a known role |
| Quantify arm-level / broad events | GISTIC2 `-broad 1`, arm-level output | `-brlen` sets the focal/broad length cutoff |
| Compare cohorts of different size | Recurrence frequency, not q-value | q-value is not portable across N |
| Characterize mutational processes | Copy-number signatures | Drews CINSignatures or Steele COSMIC CN |
| Localize the gene within a wide peak | GISTIC2 `-genegistic 1` + known drivers | Wide peaks need orthogonal driver evidence |
| Single tumor (no cohort) | GISTIC2 does not apply | Use focal-amplification-ecdna / per-sample annotation |

## Running GISTIC2

```bash
# Segment file: 6 columns -- sample, chrom, start, end, num_markers, seg.mean (log2).
# It MUST be diploid-centered. Pool per-sample segments (e.g. cnvkit.py export seg).
gistic2 \
    -b gistic_output/ \
    -seg cohort.seg \
    -refgene hg38.refgene.mat \
    -genegistic 1 \
    -broad 1 \
    -brlen 0.7 \
    -conf 0.99 \
    -armpeel 1 \
    -savegene 1 \
    -gcm extreme \
    -rx 0
```

Key flags: `-brlen 0.7` sets the focal/broad cutoff at 70% of a chromosome arm; `-conf 0.99` is the peak-boundary confidence — raising it above the 0.75 default yields a wider, more conservative peak with higher confidence the true driver gene lies inside it (the trade-off is more genes per peak); `-armpeel 1` peels arm-level events before focal testing; `-genegistic 1` runs the gene-level test; `-rx 0` keeps sex chromosomes. Output `amp_genes.txt` / `del_genes.txt` and `all_lesions.txt` list peaks, q-values, and genes.

## Copy-Number Signatures

**Goal:** Decompose the genome-wide copy-number pattern into mutational processes (HRD, chromothripsis, tandem duplication, ecDNA, whole-genome doubling).

**Approach:** Two competing 2022 frameworks exist. Steele et al (Nature 2022) defined 21 pan-cancer CN signatures from a 48-channel feature matrix, now in COSMIC; Drews et al (Nature 2022) defined 17 signatures via the CINSignatures feature set. Quantify against one framework consistently; signatures require *absolute* (allele-specific) copy number.

```r
library(CINSignatureQuantification)

# segments: data frame with columns chromosome, start, end, segVal (total CN),
# sample -- absolute copy number from ASCAT/Sequenza/FACETS, NOT relative log2.
res <- quantifyCNSignatures(segments, experimentName = 'cohort',
                            method = 'drews')
activities <- getActivities(res)   # samples x signatures exposure matrix
```

The critical caveat (Steele 2022): three signatures had to be discarded as oversegmentation artifacts and ten were linear combinations needing manual filtering. Signatures are sensitive to the upstream caller — Steele standardizes on ASCAT (SNP6 penalty 70; WGS across the same SNP6 positions) precisely for this reason.

## Failure Modes

### Comparing q-values across cohorts of different size

**Trigger:** Stating that cohort A has "more significant" peaks than cohort B when the cohorts differ in N.

**Mechanism:** GISTIC q-values fall as N rises — the same recurrence frequency clears significance in a larger cohort.

**Symptom:** A larger cohort appears to have more drivers purely because it is larger; peak lists do not replicate.

**Fix:** Compare recurrence *frequency* (fraction of samples altered), not q-value, across cohorts. Re-run GISTIC at matched N (subsample) if a significance comparison is unavoidable.

### Oversegmented input produces spurious peaks

**Trigger:** Feeding GISTIC a seg file from a noisy or over-fragmented segmentation.

**Mechanism:** GISTIC interprets every segment edge as a potential focal event boundary; fragmentation creates many narrow false peaks.

**Symptom:** Numerous tiny significant peaks at no known driver; peaks not replicated with a cleaner segmentation.

**Fix:** Quality-control the segmentation first (see copy-ratio-segmentation); merge over-fragmented segments before pooling the cohort seg file.

### Mis-centered seg file inverts everything

**Trigger:** Pooling seg files that are not diploid-centered (e.g. WGD tumors centered on tetraploid).

**Mechanism:** GISTIC assumes seg.mean ~ 0 is diploid; a shifted baseline turns gains into neutral and neutral into losses before any statistics run.

**Symptom:** Amplification and deletion peaks swapped relative to known biology; genome-wide deletion bias.

**Fix:** Center each sample's seg file on its true diploid baseline (anchor with allele-specific ploidy) before pooling. Do not rely on per-sample median centering for aneuploid cohorts.

### Treating a wide GISTIC peak as a single-gene call

**Trigger:** Reporting every gene inside a wide significant peak, or assuming the peak gene is the driver.

**Mechanism:** Peak width reflects breakpoint heterogeneity across the cohort; a wide peak may contain dozens of genes, and the statistical peak need not coincide with the functional driver.

**Symptom:** A multi-gene peak reported as one driver; the named gene is a passenger.

**Fix:** Intersect peaks with known drivers (COSMIC CGC, OncoKB), expression, and dependency data. Raising `-conf` widens the peak (it does not narrow it) — peak width is set by cohort breakpoint heterogeneity, not a tunable. Wide peaks require orthogonal driver evidence — GISTIC localizes, it does not nominate.

### Copy-number signatures from relative copy number

**Trigger:** Running CN signatures on log2 ratios or relative segments.

**Mechanism:** Signature features (segment size, copy-number state, change-point) are defined on absolute copy number; relative input gives meaningless states.

**Symptom:** Implausible signature exposures; ploidy/WGD signatures fire spuriously.

**Fix:** Use absolute allele-specific copy number from ASCAT/Sequenza/FACETS as input. Apply the framework's prescribed caller for the platform.

## Reconciliation

| Pattern | Likely cause | Action |
|---------|--------------|--------|
| GISTIC peak with no known driver | Wide peak, passenger locus, or fragile site | Cross-check expression/dependency; treat as candidate |
| Focal peak inside a broad event | Arm-level event not peeled | Confirm `-armpeel 1`; inspect Ziggurat output |
| Drews vs Steele signatures disagree | Different feature definitions and reference sets | Pick one framework; do not mix exposures |
| Peaks change with segmentation | Input over/under-segmented | Stabilize segmentation; re-run |

**Operational rule:** Report a GISTIC peak as a candidate driver locus only when (1) the input segmentation is QC-passed and diploid-centered, (2) recurrence frequency (not just q-value) is substantial, and (3) the peak contains a gene with independent driver evidence. Signatures are reportable only from absolute CN with a single, platform-matched framework.

## Quantitative Thresholds

| Threshold | Value | Source / Rationale |
|-----------|-------|--------------------|
| GISTIC significance | q < 0.25 | GISTIC2 default residual-q cutoff for peaks |
| Peak-boundary confidence | `-conf 0.99` | Wider, conservative peak; higher confidence the true driver is inside (default 0.75) |
| Focal/broad cutoff | `-brlen 0.7` | Events > 70% of an arm are treated as broad |
| Cohort size for stable peaks | tens to hundreds | Too few samples gives unstable peaks; q is N-dependent |
| CN signatures input | absolute (allele-specific) CN | Steele 2022 / Drews 2022; relative log2 is invalid |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| GISTIC2 will not start | MATLAB Compiler Runtime missing | Install the MCR version GISTIC was built against |
| Amp/del peaks swapped vs biology | Seg file not diploid-centered | Center on true ploidy before pooling |
| Many tiny spurious peaks | Oversegmented input | QC and merge segmentation first |
| `-refgene` errors | Build mismatch (hg19 vs hg38 .mat) | Use the matching reference .mat |
| Implausible signature exposures | Relative CN used as input | Use absolute allele-specific CN |
| Peak lists do not replicate | q-value compared across different N | Compare recurrence frequency |

## References

- Mermel CH et al 2011. GISTIC2.0 facilitates sensitive and confident localization of the targets of focal somatic copy-number alteration in human cancers. Genome Biol 12:R41
- Beroukhim R et al 2010. The landscape of somatic copy-number alteration across human cancers. Nature 463:899
- Steele CD et al 2022. Signatures of copy number alterations in human cancer. Nature 606:984
- Drews RM et al 2022. A pan-cancer compendium of chromosomal instability. Nature 606:976
- Macintyre G et al 2018. Copy number signatures and mutational processes in ovarian carcinoma. Nat Genet 50:1262

## Related Skills

- copy-number/allele-specific-copy-number - Absolute CN input for GISTIC and CN signatures
- copy-number/copy-ratio-segmentation - Segmentation quality controlling GISTIC peaks
- copy-number/cnv-annotation - Annotating GISTIC peaks with genes and driver roles
- copy-number/focal-amplification-ecdna - Resolving the architecture of focal amplicons
- copy-number/cnv-visualization - Cohort heatmaps of recurrent CNV
- pathway-analysis/go-enrichment - Pathway context for recurrently altered genes
<!-- END FILE: copy-number/recurrent-cnv/SKILL.md -->

## 子目录：copy-number/subclonal-copy-number

<!-- BEGIN FILE: copy-number/subclonal-copy-number/SKILL.md -->
---
name: bio-copy-number-subclonal-copy-number
description: Resolve subclonal copy number, whole-genome doubling, and copy-number tumor evolution from bulk sequencing with Battenberg, TITAN, and MEDICC2. Covers clonal versus subclonal copy-number states, haplotype phasing for subclonal resolution, cancer cell fraction, whole-genome-doubling detection and timing relative to mutations, mirrored subclonal allelic imbalance, and copy-number phylogenies. Use when a tumor is heterogeneous and bulk data shows non-integer copy number, when calling subclonal CNAs, detecting or timing whole-genome doubling, reconstructing copy-number evolution, or deciding between Battenberg and TITAN.
tool_type: mixed
primary_tool: battenberg
---

## Version Compatibility

Reference examples tested with: R 4.3+ with Battenberg 2.2.10+ and TitanCNA 1.40+, MEDICC2 1.0+, Python 3.10+; impute2/Beagle phasing reference panels.

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('Battenberg')` / `'TitanCNA')` then `?function`
- CLI: `medicc2 --help`
- Battenberg is GitHub-only (`Wedge-lab/battenberg`) and needs a 1000 Genomes impute/phasing reference and allele-counter; confirm reference data is installed

Battenberg and TITAN both consume allele-specific data (logR + BAF at heterozygous SNPs); they cannot run on relative copy ratio alone.

# Subclonal Copy Number and Tumor Evolution

**"This copy number is non-integer — is it noise, or are there subclones"** -> A tumor is a mixture of cell populations. When a copy-number change is present in only some cancer cells, bulk sequencing averages it into a *non-integer* state. A long non-integer segment is not noise — it is a subclonal copy-number alteration, and resolving it reveals the tumor's clonal architecture.

- R: `Battenberg` (phased clonal + subclonal CN), `TitanCNA` (HMM mixture of cell populations)
- CLI: `medicc2` (whole-genome-doubling-aware copy-number phylogenies)
- Input: allele-specific data — see allele-specific-copy-number for the clonal layer

## Clonal vs Subclonal — What the Tools Output

| Concept | Meaning |
|---------|---------|
| Clonal CNA | Present in all cancer cells; one copy-number state per segment |
| Subclonal CNA | Present in a fraction of cancer cells; the segment needs two states plus a fraction |
| Cancer cell fraction (CCF) | Fraction of cancer cells carrying the event |
| Mirrored subclonal allelic imbalance | Different subclones lose opposite haplotypes of the same region |

Battenberg fits a clonal allele-specific profile (ASCAT internally), then where a segment fits poorly as a single integer state, it models it as a mixture of two states with a subclonal fraction. TITAN uses an HMM whose states span multiple clonal clusters, jointly estimating per-cluster cellular prevalence. Both need haplotype phasing — subclonal allelic imbalance is only resolvable when SNPs are phased.

## Tool Selection

| Tool | Model | Best for | Fails when |
|------|-------|----------|------------|
| Battenberg | Phased clonal fit + per-segment subclonal mixture | WGS, subclonal CN to ~3% of cells, clonal-evolution studies | Low depth/purity; heavy compute; needs phasing reference |
| TITAN | HMM mixture across clonal clusters | WGS/WES, joint CN+LOH+subclonal prevalence, few clusters | Many subclones; cluster number must be chosen and swept |
| MEDICC2 | WGD-aware minimum-event copy-number phylogeny | Multi-sample / multi-region evolution | Single sample (no tree to build) |
| ASCAT/FACETS | Clonal allele-specific only | When subclonal resolution is not needed | Treats subclonal segments as noisy clonal — see allele-specific-copy-number |

## Whole-Genome Doubling — Detection and Timing

Whole-genome doubling (WGD) is a discrete, common (~30% of advanced cancers) evolutionary event, and it must be called explicitly because it changes how every copy number is read.

- **Detection:** A tumor has undergone WGD if more than ~50% of the autosomal genome has a major (more frequent) allele copy number >= 2. WGD tumors have median ploidy ~3.3 versus ~2.1 for non-WGD.
- **Relative vs absolute:** Depth gives *relative* copy number; WGD calling needs *absolute* allele-specific copy number (BAF anchors ploidy). A depth-only profile cannot distinguish a WGD genome from a non-WGD genome — this is the identifiability problem of allele-specific-copy-number in another guise.
- **Timing:** WGD is timeable relative to point mutations. Mutations that arose before WGD are carried at multiple copies (mutation copy number ~2); mutations after WGD sit at one copy. This dates WGD within the tumor's mutational history.

## Calling Subclonal CN with Battenberg

**Goal:** Fit clonal and subclonal allele-specific copy number genome-wide.

**Approach:** Generate phased allele counts against a 1000 Genomes reference, run the Battenberg pipeline; segments that fit poorly as one integer state are split into a two-state subclonal mixture with a cellular fraction.

```r
library(Battenberg)

# Battenberg orchestrates allele counting, phasing, ASCAT clonal fit, and the
# subclonal mixture step. Reference data (1000G impute panel) must be installed.
battenberg(
    samplename          = 'tumour_id',
    normalname          = 'normal_id',
    sample_data_file    = 'tumour.bam',
    normal_data_file    = 'normal.bam',
    ismale              = TRUE,
    imputeinfofile      = 'impute_info.txt',
    g1000prefix         = '1000G_loci/1000genomesloci2012_chr',     # SNP loci data
    g1000allelesprefix  = '1000G_alleles/1000genomesAlleles2012_chr', # SNP alleles (WGS)
    problemloci         = 'probloci.txt',
    gccorrectprefix     = 'GC_correction_hg38_chr',
    repliccorrectprefix = 'RT_correction_hg38_chr',
    genomebuild         = 'hg38',                                   # default is hg19
    nthreads            = 8)
# Output *_subclones.txt: per segment, nMaj1/nMin1 (state 1) + frac1, and nMaj2/nMin2 +
# frac2 when the segment is subclonal (two states).
```

## Calling Subclonal CN with TITAN

**Goal:** Jointly infer copy number, LOH, and the cellular prevalence of clonal clusters.

**Approach:** TITAN needs both allele counts (het SNPs) and corrected read depth. Load the allele counts; correct tumour/normal read depth for GC and mappability bias; overlay the resulting logR onto the het positions and log-transform; filter; then run the EM and sweep the cluster number — model selection picks the best.

```r
library(TitanCNA)

# Allele counts at het SNPs.
data <- loadAlleleCounts('tumour.allelicCounts.tsv', genomeStyle = 'UCSC')

# Read-depth correction is mandatory: correctReadDepth needs tumour + normal coverage
# WIGs and GC + mappability WIGs. genomeStyle MUST match loadAlleleCounts above
# (default 'NCBI' vs 'UCSC') or getPositionOverlap matches no chromosomes and logR is NA.
cnData <- correctReadDepth('tumour.wig', 'normal.wig', 'gc.wig', 'map.wig',
                           genomeStyle = 'UCSC')
data$logR <- log(2 ^ getPositionOverlap(data$chr, data$posn, cnData))
data <- filterData(data, 1:24, minDepth = 10, maxDepth = 200, map = NULL)

params <- loadDefaultParameters(copyNumber = 8, numberClonalClusters = 2,
                                symmetric = TRUE, data = data)
conv <- runEMclonalCN(data, params, maxiter = 20, txnExpLen = 1e15)
results <- viterbiClonalCN(data, conv)
# Sweep numberClonalClusters (1..5) and compare model fit; the S_Dbw validity index
# or the model log-likelihood selects the cluster number.
```

## Failure Modes

### Subclonal call from insufficient depth or purity

**Trigger:** Calling subclonal CN on shallow WGS or a low-purity tumor.

**Mechanism:** A subclonal segment's signal is the clonal deviation scaled by the subclone's cell fraction — already small, and below the noise floor at low depth/purity.

**Symptom:** Many "subclonal" segments with implausibly low fractions; calls not reproducible across reruns or regions.

**Fix:** Battenberg's ~3%-of-cells sensitivity assumes adequate WGS depth and purity. For low-depth or low-purity samples, treat only clonal CN as reliable and report subclonal calls as exploratory.

### Mirrored subclonal allelic imbalance misread

**Trigger:** A region where different subclones lost opposite haplotypes.

**Mechanism:** Bulk BAF averages the two opposite losses toward 0.5, so the region can look balanced (clonal, no LOH) when it is in fact subclonally rearranged on both haplotypes.

**Symptom:** A segment called clonal-balanced that conflicts with multi-region or single-cell data; BAF near 0.5 with an odd logR.

**Fix:** Phasing (Battenberg) is required to detect mirrored subclonal allelic imbalance. Multi-region or single-cell data resolves it definitively; a single bulk sample can miss it.

### WGD not called — every copy number off by a factor

**Trigger:** Interpreting copy number without first establishing WGD status.

**Mechanism:** The likelihood surface has near-equal modes at ploidy P and 2P; missing a WGD halves all copy numbers and mis-times every mutation.

**Symptom:** Copy numbers and mutation copy numbers inconsistent; "subclonal" gains that are actually clonal post-WGD states.

**Fix:** Call WGD explicitly (>50% of autosomes at major CN >= 2) from absolute allele-specific copy number. Cross-check ploidy against the odd/even CN fraction and clonal-SNV multiplicity before any subclonal interpretation.

### Over-interpreting one subclonal segment as a subclone

**Trigger:** Declaring a distinct tumor subclone from a single subclonal copy-number segment.

**Mechanism:** A single segment at an intermediate fraction can arise from segmentation error, a mis-fit clonal state, or genuine subclonality — one segment cannot distinguish these.

**Symptom:** A "subclone" supported by exactly one segment; clonal architecture claims that do not replicate.

**Fix:** Require multiple concordant subclonal segments at a consistent cell fraction, ideally corroborated by SNV-based subclonal reconstruction (cancer cell fraction clustering) and multi-region sampling.

### Single-region sampling misses spatial subclones

**Trigger:** Inferring clonal architecture from one biopsy of a spatially heterogeneous tumor.

**Mechanism:** A subclone confined to an unsampled region is invisible; a single region cannot capture branching evolution.

**Symptom:** Apparently simple clonal architecture contradicted by a second biopsy.

**Fix:** For evolution and architecture claims, use multi-region sampling and a phylogeny method (MEDICC2 for copy-number trees). Single-region subclonal calls describe that region only.

## Reconciliation

| Pattern | Likely cause | Action |
|---------|--------------|--------|
| Battenberg subclonal vs TITAN clonal | Different mixture models; cluster number | Sweep TITAN clusters; compare cell fractions |
| WGD called by one tool, not another | Integer-multiple ploidy ambiguity | Check odd/even CN fraction and SNV multiplicity |
| Many low-fraction subclonal segments | Depth/purity too low | Trust only clonal CN; flag subclonal as exploratory |
| Subclonal CN vs SNV-based CCF disagree | CN and SNV subclones need not coincide | Integrate both; they answer different questions |

**Operational rule:** Report subclonal copy number as confident only when (1) depth and purity support it, (2) WGD status is established from absolute allele-specific CN, (3) multiple concordant segments support a subclone at a consistent fraction, and (4) for evolution claims, multi-region data and a copy-number phylogeny are used. A single subclonal segment is a hypothesis, not a subclone.

## Quantitative Thresholds

| Threshold | Value | Source / Rationale |
|-----------|-------|--------------------|
| Battenberg subclonal sensitivity | ~3% of cells | Nik-Zainal 2012; requires adequate WGS depth/purity |
| WGD definition | > 50% of autosomes at major CN >= 2 | Bielski 2018; the operational WGD call |
| WGD median ploidy | ~3.3 (WGD) vs ~2.1 (non-WGD) | Bielski 2018 pan-cancer |
| Pre-WGD mutation copy number | >= ~1.75 | Pre-doubling mutations carried at multiple copies |
| TITAN clonal clusters | sweep 1-5, select by fit | Few clusters resolvable from one bulk sample |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| Battenberg install/run fails | GitHub-only; missing 1000G reference | Install from GitHub; set up the impute reference |
| Non-integer segments treated as noise | Subclonal CNA not modeled | Use Battenberg/TITAN, not a clonal-only caller |
| All copy numbers half/double expected | WGD not called | Establish WGD from absolute CN; check SNV multiplicity |
| Subclones not reproducible | Low depth/purity, single segment | Require depth, concordant segments, multi-region |
| Balanced region conflicts with other data | Mirrored subclonal allelic imbalance | Use phased (Battenberg) or single-cell data |
| TITAN cluster number arbitrary | Cluster count not swept | Sweep 1-5; select by model fit |

## References

- Nik-Zainal S et al 2012. The life history of 21 breast cancers (Battenberg). Cell 149:994
- Ha G et al 2014. TITAN: inference of copy number architectures in clonal cell populations from tumor whole-genome sequence data. Genome Res 24:1881
- Bielski CM et al 2018. Genome doubling shapes the evolution and prognosis of advanced cancers. Nat Genet 50:1189
- Dewhurst SM et al 2014. Tolerance of whole-genome doubling propagates chromosomal instability. Cancer Discov 4:175
- Kaufmann TL et al 2022. MEDICC2: whole-genome doubling aware copy-number phylogenies for cancer evolution. Genome Biol 23:241

## Related Skills

- copy-number/allele-specific-copy-number - Clonal allele-specific CN, purity, ploidy
- copy-number/copy-ratio-segmentation - Segmentation feeding subclonal callers
- copy-number/hrd-scoring - Whole-genome-doubling correction for LST
- copy-number/recurrent-cnv - Copy-number signatures including WGD and chromothripsis
- copy-number/cnv-visualization - Visualizing subclonal segments and BAF
- variant-calling/vcf-basics - SNV calls for cancer cell fraction and WGD timing
<!-- END FILE: copy-number/subclonal-copy-number/SKILL.md -->

<!-- END CATEGORY: copy-number -->

