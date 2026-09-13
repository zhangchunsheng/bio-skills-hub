---
slug: bio-tcr-bcr-analysis-integrated
version: 1.0.0
displayName: "TCR/BCR分析 / TCR/BCR repertoire analysis"
name: bio-tcr-bcr-analysis-integrated
summary: >-
  中文：TCR/BCR分析综合技能，整合 6 个相关专题，覆盖TCR/BCR受体组分析：MiXCR组装、VDJtools多样性、Immcantation克隆群、scirpy单细胞整合。 English: Integrated TCR/BCR repertoire analysis skill covering 6 related topics, including TCR/BCR repertoire analysis: MiXCR assembly, VDJtools diversity, Immcantation clonal families, scirpy single-cell integration.
description: >-
  中文：这是一个面向TCR/BCR分析的综合生物信息学 Skill，整合当前分类下 6 个相关专题能力。它用于根据研究问题、数据类型和分析阶段，选择合适的方法与工具，规划从输入检查、预处理、核心分析到质量控制、统计解释和结果报告的完整流程。重点覆盖：TCR/BCR受体组分析：MiXCR组装、VDJtools多样性、Immcantation克隆群、scirpy单细胞整合。当用户提供相关实验数据、测序结果、表格或研究问题时，它会帮助判断分析目标与前置条件，给出工具选择、关键参数、输入输出、常见失败原因、结果解读和可复现建议。主要工具包括：MiXCR, VDJtools, alakazam。该 Skill 提供分析设计与实施指导，不替代对具体数据质量、生物学背景和最终结论的人工审查。
  English: This is an integrated bioinformatics Skill for TCR/BCR repertoire analysis, combining 6 related topic areas. It helps users choose appropriate methods and tools based on the research question, data type, and analysis stage, and plan an end-to-end workflow from input validation and preprocessing through core analysis, quality control, statistical interpretation, and reporting. It covers TCR/BCR repertoire analysis: MiXCR assembly, VDJtools diversity, Immcantation clonal families, scirpy single-cell integration. For relevant experimental data, sequencing results, tables, or research questions, it clarifies prerequisites, recommends tools and parameters, describes expected inputs and outputs, explains common failure modes, and supports reproducible analysis. Primary tools include: MiXCR, VDJtools, alakazam. It provides methodological and implementation guidance; final data-quality assessment and biological conclusions still require human review.
---

# tcr-bcr-analysis 分类 Skill 整合版

> 本文件整合同一主分类目录下 6 个子目录中的 SKILL.md 内容。
> 各子目录正文按原文保留，并通过标题和边界标记进行区分；源文件中的元数据块未被改写。

---

<!-- BEGIN CATEGORY: tcr-bcr-analysis -->

## 子目录：tcr-bcr-analysis/immcantation-analysis

<!-- BEGIN FILE: tcr-bcr-analysis/immcantation-analysis/SKILL.md -->
---
name: bio-tcr-bcr-analysis-immcantation-analysis
description: Reconstructs B-cell clonal families, quantifies somatic hypermutation and selection, and builds antibody lineage trees with the Immcantation R suite (alakazam, shazam, scoper, dowser, tigger) on AIRR-format BCR data. Use when deriving the clonal-clustering threshold from the distToNearest bimodal valley (never a hardcoded 0.15); choosing hierarchicalClones vs spectralClones (vj vs novj) for SHM-diverged repertoires; personalizing the germline with TIGGER before mutation counting; reconstructing D-masked germlines with createGermlines; measuring R/S mutation frequency by CDR and FWR region; testing antigen-driven selection with BASELINe; comparing Hill-number diversity at equal sampling depth; and inferring IgPhyML lineage trees for affinity maturation, class-switch, and ancestral-antibody analysis.
tool_type: r
primary_tool: alakazam
---

## Version Compatibility

Reference examples tested with: alakazam 1.3+, shazam 1.2+, scoper 1.3+, dowser 2.x, tigger 1.1+ (Immcantation R suite), plus IgBLAST, Change-O, and PHYLIP/IgPhyML as external dependencies.

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

Note: `createGermlines` now lives in dowser (not shazam); BASELINe selection uses `calcBaseline`/`groupBaseline` (the old `estimateBaseline` name is gone); mutation R/S classification is set by `regionDefinition`, not a fake `mutationDefinition=MUTATION_SCHEMES$S5F` (that has no `S5F` member); the clonal threshold must come from `findThreshold`, never a literature constant.

# Immcantation Analysis

**"Find the B-cell clones and measure their affinity maturation"** -> partition SHM-diverged sequences into clonal families, quantify somatic hypermutation and selection against a reconstructed germline, and build antibody lineage trees.
- R: `shazam::distToNearest()` + `shazam::findThreshold()` (threshold), `scoper::hierarchicalClones()`/`scoper::spectralClones()` (clones), `dowser::createGermlines()` + `shazam::observedMutations()` (SHM), `shazam::calcBaseline()` (selection), `dowser::getTrees()` (lineage trees)

## The governing principle: the clonal threshold is derived, not assumed

Every downstream number in a BCR analysis -- clone counts, diversity, selection strength, tree topology -- inherits its error from one quantity: the nucleotide-distance cutoff used to group sequences into clonal families. That cutoff is NOT a literature constant. `distToNearest` computes each sequence's Hamming distance to its nearest neighbor within the same V gene, J gene, and junction length; because unrelated rearrangements almost never share V/J plus a near-identical junction by chance while clonally related sequences differ only by SHM, the resulting `dist_nearest` distribution is bimodal. `findThreshold` locates the VALLEY between the clonally-related mode (small distances) and the unrelated mode (large distances). That valley is the per-dataset threshold. A hardcoded `threshold = 0.15` is the exact anti-pattern to avoid: the valley shifts with subject, locus, sequencing depth, and chemistry, and a wrong threshold silently merges independent lineages or shatters one clone into many (Gupta 2015 *Bioinformatics* 31:3356; Nouri 2018 *Bioinformatics* 34:i341).

If the `dist_nearest` histogram is UNIMODAL (no clear valley), a fixed threshold is undefined -- switch to `spectralClones(method="novj")`, whose adaptive local threshold does not require `findThreshold`.

## Why BCR needs a different clonotype definition than TCR

TCR does not hypermutate, so all progeny of a founding T cell share the exact CDR3 nucleotide sequence and exact-CDR3 matching is correct. BCR hypermutates: members of one lineage are NOT identical, so exact-CDR3 shatters a single clone into hundreds of fragments. The field-standard BCR clone groups sequences sharing the same V gene, same J gene, and same junction LENGTH, then clusters within that partition by junction nucleotide distance at the derived threshold. Use nucleotide (not amino-acid) junction distance -- SHM is a nucleotide process and codon degeneracy would blur it.

| Method | How it clusters | Best when | Fails when |
|--------|-----------------|-----------|------------|
| `hierarchicalClones` | Single-linkage on junction Hamming distance within V/J/length partitions, cut at the `findThreshold` value | `dist_nearest` is clearly bimodal; a defensible fixed threshold exists | Unimodal distance histogram (threshold undefined); heavily diverged clones fragment |
| `spectralClones(method="novj")` | Spectral clustering with an adaptive local junction-similarity threshold; no fixed cutoff needed | Unimodal repertoires where no `findThreshold` valley exists | Very small groups (spectral needs several sequences) |
| `spectralClones(method="vj")` | Adds shared V/J SHM (targeting model) to junction homology | SHM-driven within-clone divergence pulls junctions apart; a mutated clone would otherwise be split | Needs `germline_alignment`/`sequence_alignment` and is slower |

Verify current best practice against the SCOPer vignette before committing to a method; the spectral `vj` model is the reason spectral clustering holds diverged clones together where a fixed threshold fragments them.

## Pipeline order (load-bearing)

This order is not interchangeable; getting it wrong silently corrupts mutation and selection counts.

0. TIGGER genotype FIRST. An unrecorded personal germline polymorphism otherwise reads as recurrent SHM at a fixed position -- it inflates mutation and selection counts AND adds spurious junction distance that corrupts `distToNearest`.
1. `createGermlines` (per-sequence) to reconstruct the D-masked germline BEFORE any mutation counting (mutation = observed vs inferred germline).
2. `distToNearest` -> `findThreshold` to derive the threshold.
3. Clonal clustering (`hierarchicalClones`/`spectralClones`).
4. `createGermlines` again per-clone (clone consensus germline), then `observedMutations` with the CDR3/junction MASKED (the D-masked germline handles this; junctional N/P bases have no template).
5. BASELINe selection (`calcBaseline` -> `groupBaseline`) with a codon+motif-aware null -- raw R/S is biased by germline codon structure and SHM hotspot/transition bias, so naive R/S is not selection.
6. Dowser lineage trees.

Immcantation reads and writes one AIRR TSV. Expected columns: `sequence_id`, `v_call`, `j_call`, `junction`, `junction_length`, `sequence_alignment`, `germline_alignment_d_mask`, `clone_id` (plus `locus` and `cell_id` for single-cell). These are lowercase snake_case; legacy UPPERCASE Change-O names (`V_CALL`, `JUNCTION`, `CLONE`) are deprecated and mixing schemas is a silent failure.

## Personalize the germline with TIGGER

**Goal:** Build the subject's own V-gene genotype so germline polymorphisms are not miscounted as somatic mutations.

**Approach:** Detect novel alleles from the mutation-frequency-vs-position signature, infer the personal genotype, and re-call V alleles against it before anything downstream.

```r
library(tigger)

ighv <- readIgFasta('IMGT_Human_IGHV.fasta')             # named vector of germline V alleles
novel <- findNovelAlleles(db, germline_db = ighv, v_call = 'v_call', nproc = 1)
genotype <- inferGenotypeBayesian(db, germline_db = ighv, novel = novel, find_unmutated = TRUE)
gt_seqs <- genotypeFasta(genotype, germline_db = ighv, novel = novel)
db <- reassignAlleles(db, genotype_db = gt_seqs)         # collapse ambiguous calls to alleles the subject carries
```

## Derive the clonal threshold

**Goal:** Obtain the per-dataset nucleotide-distance cutoff that separates clonally related from unrelated sequences.

**Approach:** Compute each sequence's distance to its nearest same-V/J/length neighbor, then find the valley of the bimodal distribution. Inspect the histogram before trusting the value.

```r
library(shazam)

db <- distToNearest(db, sequenceColumn = 'junction', vCallColumn = 'v_call',
                    jCallColumn = 'j_call', model = 'ham', normalize = 'len', nproc = 1)
# Single-cell: add cellIdColumn='cell_id', locusColumn='locus', onlyHeavy=TRUE
#   (light chains lack the junction diversity to define clones alone)

thr_obj <- findThreshold(db$dist_nearest, method = 'density')   # 'gmm' makes the FP/FN tradeoff explicit
threshold <- thr_obj@threshold                                   # S4 slot; NA/unimodal -> use spectralClones('novj')
plot(thr_obj)                                                    # confirm bimodality before proceeding
```

## Cluster sequences into clonal families

**Goal:** Group SHM-diverged sequences descended from one naive B cell into clones.

**Approach:** Cluster within V/J/junction-length partitions at the derived threshold; for single-cell paired data, cluster on heavy chains, then resolve light chains as a separate step.

```r
library(scoper)

results <- hierarchicalClones(db, threshold = threshold, method = 'nt', linkage = 'single')
db <- as.data.frame(results)                       # adds clone_id

# Single-cell paired BCR: cluster on heavy only, then split clones by light-chain V/J.
# The scoper only_heavy/split_light args are DEPRECATED; use dowser::resolveLightChains:
# db <- dowser::resolveLightChains(db)

# Unimodal repertoire (no clear threshold): adaptive, SHM-aware alternative
# db <- as.data.frame(spectralClones(db, method = 'vj',
#     germline = 'germline_alignment', sequence = 'sequence_alignment'))
```

## Reconstruct germline and quantify SHM

**Goal:** Measure somatic hypermutation as replacement (R) and silent (S) frequency by region, the signal of affinity maturation.

**Approach:** Rebuild the D-masked clonal germline, then compare each observed V-region to it. Use frequency (not raw counts) when coverage varies, and restrict to the V segment so the untemplated junction is excluded.

```r
library(dowser)

references <- readIMGT('imgt/human/vdj')           # IMGT-gapped V/D/J reference dir
db <- createGermlines(db, references)              # per-clone germline; adds germline_alignment_d_mask

db <- observedMutations(db, sequenceColumn = 'sequence_alignment',
                        germlineColumn = 'germline_alignment_d_mask',
                        regionDefinition = IMGT_V,             # V only; stops before CDR3/junction
                        frequency = TRUE, nproc = 1)
# Adds mu_freq_cdr_r, mu_freq_cdr_s, mu_freq_fwr_r, mu_freq_fwr_s
# For property-based R/S use mutationDefinition = CHARGE_MUTATIONS (or HYDROPATHY/POLARITY/VOLUME).
# S5F is a TARGETING model (HH_S5F) for selection, NOT a mutationDefinition.
```

## Test for selection (BASELINe)

**Goal:** Decide whether replacement mutations are enriched (positive selection, typically CDR) or depleted (purifying, typically FWR) beyond what SHM alone produces.

**Approach:** Compute the expected R/S per region from the germline under an SHM targeting model, form a posterior over selection strength per sequence, then convolve posteriors within groups. Analyze one representative per clone so shared ancestral mutations are not double-counted.

```r
baseline <- calcBaseline(db, testStatistic = 'focused', regionDefinition = IMGT_V, nproc = 1)
grouped <- groupBaseline(baseline, groupBy = 'sample_id')   # convolves per-sequence PDFs
# testBaseline(grouped, groupBy='sample_id') for significance; sigma>0 = positive selection
```

## Compare diversity at equal depth

**Goal:** Compare clonal diversity across samples without confounding by sequencing depth.

**Approach:** Report a Hill-number profile with uniform resampling to equal N and bootstrap CIs; comparing raw diversity across unequal-depth libraries measures depth, not biology.

```r
library(alakazam)

div <- alphaDiversity(db, group = 'sample_id', clone = 'clone_id',
                      min_q = 0, max_q = 2, step_q = 0.1,      # q=0 richness, q=1 Shannon, q=2 Simpson
                      ci = 0.95, nboot = 200)                  # uniform=TRUE (default) resamples to equal N
plot(div)
```

## Build lineage trees

**Goal:** Reconstruct each clone's antibody lineage to trace affinity maturation, class switching, and ancestral (intermediate) antibodies.

**Approach:** Build clonally-collapsed, germline-rooted trees under IgPhyML's HLP codon model, which encodes SHM's context-dependence, non-reversibility, and known germline root -- assumptions that standard phylogenetics violates.

```r
clones <- formatClones(db, traits = 'c_call', minseq = 3)     # collapse duplicates, attach clonal germline
trees <- getTrees(clones, build = 'igphyml',
                  igphyml = '/usr/local/share/igphyml/src/igphyml', nproc = 1)
plots <- plotTrees(trees)                                     # ggtree, germline-rooted; color tips by trait
# findSwitches(clones, ...) + testSP/testSC reconstruct isotype/tissue switching across bootstrap trees.
# Legacy: alakazam::buildPhylipLineage() (PHYLIP dnapars max-parsimony) still exists but is superseded.
```

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| Clone counts differ wildly from a published study | Hardcoded `threshold = 0.15` instead of the data's valley | Run `distToNearest` -> `findThreshold`; read `@threshold`; inspect the histogram |
| `observedMutations` gives near-zero or nonsensical mutations | Counted before `createGermlines` (no reconstructed germline) | Run `createGermlines` first; compare against `germline_alignment_d_mask` |
| Inflated R mutations concentrated in CDR3 | Junction/CDR3 not masked; junctional N/P bases have no template | Use the D-masked germline and `regionDefinition = IMGT_V` (V only) |
| `MUTATION_SCHEMES$S5F` errors or gives odd R/S | No `S5F` member exists; S5F is a targeting model, not a mutation definition | Drop it (default R/S by AA identity) or use `CHARGE_MUTATIONS`; use `HH_S5F` only as a targeting model |
| `estimateBaseline` not found | Renamed | Use `calcBaseline` then `groupBaseline`/`testBaseline` |
| Recurrent "mutation" at the same position across many sequences | Unrecorded personal germline allele scored as SHM | Run TIGGER (`findNovelAlleles`/`inferGenotypeBayesian`/`reassignAlleles`) before germline reconstruction |
| Diversity differences vanish or invert after resequencing | Compared raw diversity across unequal-depth samples | Use `alphaDiversity` with uniform resampling (default) and bootstrap CIs |
| Same clone appears in two individuals | Pooled clones across subjects with private genotypes | Cluster clones within each subject; treat cross-subject sharing as a separate convergence question |
| Unimodal `dist_nearest` histogram, `findThreshold` returns NA | No clear valley (e.g. low-SHM or shallow repertoire) | Use `spectralClones(method = 'novj')` (adaptive threshold) |

## Related Skills

- mixcr-analysis - Produce AIRR/clonotype input for BCR
- scirpy-analysis - Single-cell BCR integration and handoff
- specificity-annotation - Convergent/public antibody signatures
- phylogenetics/tree-visualization - General lineage-tree plotting concepts
- phylogenetics/modern-tree-inference - Phylogenetic inference background
- workflows/tcr-pipeline - End-to-end orchestration

## References

- Gupta NT, Vander Heiden JA, Uduman M, Gadala-Maria D, Yaari G, Kleinstein SH. Change-O: a toolkit for analyzing large-scale B cell immunoglobulin repertoire sequencing data. *Bioinformatics* 2015, 31(20):3356-3358.
- Vander Heiden JA, Yaari G, Uduman M, Stern JNH, O'Connor KC, Hafler DA, Vigneault F, Kleinstein SH. pRESTO: a toolkit for processing high-throughput sequencing raw reads of lymphocyte receptor repertoires. *Bioinformatics* 2014, 30(13):1930-1932.
- Yaari G, Uduman M, Kleinstein SH. Quantifying selection in high-throughput immunoglobulin sequencing data sets (BASELINe). *Nucleic Acids Research* 2012, 40(17):e134.
- Yaari G, Vander Heiden JA, Uduman M, et al. Models of somatic hypermutation targeting and substitution based on synonymous mutations from high-throughput immunoglobulin sequencing data (S5F). *Frontiers in Immunology* 2013, 4:358.
- Gadala-Maria D, Yaari G, Uduman M, Kleinstein SH. Automated analysis of high-throughput B-cell sequencing data reveals a high frequency of novel immunoglobulin V gene segment alleles (TIGGER). *PNAS* 2015, 112(8):E862-E870.
- Nouri N, Kleinstein SH. A spectral clustering-based method for identifying clones from high-throughput B cell repertoire sequencing data (SCOPer). *Bioinformatics* 2018, 34(13):i341-i349.
- Hoehn KB, Pybus OG, Kleinstein SH. Phylogenetic analysis of migration, differentiation, and class switching in B cells (Dowser). *PLoS Computational Biology* 2022, 18(4):e1009885.
- Hoehn KB, Lunter G, Pybus OG. A phylogenetic codon substitution model for antibody lineages (IgPhyML). *Genetics* 2017, 206(1):417-427.
- Stern JNH, Yaari G, Vander Heiden JA, et al. B cells populating the multiple sclerosis brain mature in the draining cervical lymph nodes. *Science Translational Medicine* 2014, 6(248):248ra107.
<!-- END FILE: tcr-bcr-analysis/immcantation-analysis/SKILL.md -->

## 子目录：tcr-bcr-analysis/mixcr-analysis

<!-- BEGIN FILE: tcr-bcr-analysis/mixcr-analysis/SKILL.md -->
---
name: bio-tcr-bcr-analysis-mixcr-analysis
description: Align V(D)J reads and assemble TCR/BCR clonotypes with MiXCR, driven by a chemistry-matched preset. Use when choosing/auditing the preset for a library (5'RACE/template-switch vs multiplex-primer amplicon -> rigid vs floating boundaries; RNA vs gDNA -> --rna/--dna; bulk vs 10x single-cell; UMI vs no-UMI -> tag pattern and barcode collapse; kit presets Takara/NEBNext/QIAseq/BD/MiLaboratory); assembling clonotypes by CDR3 vs VDJRegion; setting the reads-vs-UMI-vs-cell quantitation denominator; exporting native MiXCR fields vs AIRR rearrangement TSV for downstream Immcantation/scirpy/VDJtools; and running alignment/chain-usage QC. Keywords: MiXCR, analyze, align, refineTagsAndSort, assemblePartial, assemble, assembleCells, exportClones, exportAirr, exportQc, CDR3, V(D)J, clonotype, UMI, cell barcode, 10x VDJ, license.
tool_type: cli
primary_tool: MiXCR
---

## Version Compatibility

Reference examples tested with: MiXCR 4.7+ (Java 17)

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `mixcr --version` (also prints the JVM) then `mixcr <command> --help` to confirm flags

If a command errors with an unknown-flag, unknown-preset, or missing-license message, run
`mixcr <command> --help` and `mixcr exportPreset --preset-name <name>` and adapt rather than retrying.

Note: MiXCR 4.x is a rearchitecture of 3.x. The hand-built `mixcr analyze amplicon`/`analyze shotgun` pipelines are GONE, replaced by `mixcr analyze <preset>`; `correctAndSortTags` became `refineTagsAndSort`; AIRR export moved to a dedicated `mixcr exportAirr`. Current 4.x needs Java 17 and an activated license (see the licensing gate below). Any 3.x tutorial is stale.

# MiXCR Analysis

**"Extract TCR/BCR clonotypes from my sequencing data"** -> align raw reads to V/D/J/C germline, collapse molecules/cells by barcode, and assemble reads into clonotypes keyed on CDR3 + V + J.
- CLI: `mixcr analyze <preset>` runs the whole ordered pipeline; the underlying stages (`align` -> `refineTagsAndSort` -> `assemblePartial`/`extend` -> `assemble` -> `assembleCells` -> `exportClones`/`exportAirr` -> `qc`) can be run by hand for control.

## The governing principle: the preset IS the analysis, and the wrong one fails silently

In MiXCR 4.x there is no default-correct pipeline. Correctness is ~90% preset choice plus library-chemistry match. `mixcr analyze <preset>` expands the preset into an ordered stage list encoding material (RNA vs DNA), 5'/3' alignment-boundary behavior (rigid vs floating), the barcode tag pattern, the assembling feature, and species defaults. The wrong preset does NOT raise an error -- it emits plausible-but-wrong clonotypes: a mismatched RNA/DNA model or boundary model mis-places V/J boundaries and truncates CDR3; a UMI kit run without a tag pattern skips barcode collapse and inflates diversity with PCR/sequencing artifacts. Because the failure is silent, the load-bearing skill is choosing and AUDITING the preset. Dump exactly what a preset does with `mixcr exportPreset --preset-name <name>` (full resolved parameter YAML), and confirm chemistry with `mixcr exportQc align`/`chainUsage` after the run. A clonotype is an analyst choice, not a fact: it is CDR3 (+ V + J) at a chosen boundary (assembling feature), counted in a chosen denominator (reads vs UMIs vs cells) -- every downstream number depends on these.

## Licensing gate (do this first, or every run fails)

MiXCR 4.x refuses to run any analysis command until a license is activated -- the single most common reason a copied 3.x recipe fails today. Academic/non-profit use is free (obtain a key at platforma.bio/getlicense); for-profit use needs a business license. Activate by any one of:
- `mixcr activate-license` then paste the key (interactive).
- Place `mi.license` (or `~/.mi.license`) in `~/`, next to `mixcr.jar`, or next to the executable.
- Set `MI_LICENSE=<key content>` or `MI_LICENSE_FILE=/path/mi.license` (best for HPC/Docker/CI).

MiXCR also validates the key over the internet periodically. On air-gapped or firewalled compute nodes, whitelist IPv4 `75.2.96.100` and `99.83.215.63` (and the corresponding IPv6) or arrange an offline license, or a job silently stalls waiting on egress.

## Preset selection by library type

The preset must match the exact wet-lab chemistry. Inspect the built-in list with `mixcr exportPreset` and the docs; verify current names against `mixcr analyze --help` since MiLaboratories occasionally renames presets between minor releases.

| Library / chemistry | Preset (verified 4.7) | Material | 5' boundary | UMI/barcode | Biology consequence if mismatched |
|---|---|---|---|---|---|
| 5'RACE / template-switch bulk (e.g. SMARTer) | kit preset, or `generic-amplicon`/`-with-umi` with `--rigid-left-alignment-boundary` | `--rna` | RIGID (5' set by template-switch oligo) | kit UMI or `--tag-pattern` | Floating-left on RACE trims real 5' V sequence; missing tag pattern skips UMI collapse |
| Multiplex-primer amplicon (V/J or V/C primers) | kit preset, or `generic-amplicon` with `--floating-left-alignment-boundary` | `--rna` or `--dna` | FLOATING on the primer side | as designed | Rigid boundary counts primer bases as germline mismatch -> wrong V call, truncated CDR3 |
| gDNA multiplex (genomic template) | `--dna` variant preset | `--dna` (include introns) | floating on primer side | usually none | `--rna` on gDNA drops intron-containing alignments; gDNA count approximates cell count |
| Bulk RNA-seq mining (non-targeted) | `rna-seq` | `--rna` | n/a (fragmented) | none | Needs `assemblePartial` x2 + `extend`; judged by absolute yield, not % aligned |
| 10x single-cell V(D)J (TCR+BCR) | `10x-sc-xcr-vdj` | preset-set | preset-set | CELL+UMI (preset) | Missing cell/UMI pattern -> no pairing, fake diversity; count CELLS not reads |
| 10x 5' GEX repertoire mining | `10x-sc-5gex` | preset-set | preset-set | CELL+UMI | Shallow repertoire mined from GEX; not a substitute for enriched VDJ |
| Takara SMARTer human TCR/BCR | `takara-human-rna-tcr-umi-smarter-v2`, `takara-human-rna-bcr-umi-smarter`, `...-smartseq` | `--rna` | RIGID (template-switch) | 12nt UMI (preset) | Uses the correct RACE boundary + UMI pattern automatically |
| NEBNext immune-seq | `neb-human-rna-xcr-umi-nebnext` (`neb-mouse-...`) | `--rna` | preset-set | UMI (preset) | `xcr` = both TCR and BCR in one preset |
| QIAseq immune | `qiagen-human-rna-tcr-umi-qiaseq` (`...-mouse-...`) | `--rna` | preset-set | UMI (preset) | -- |
| BD Rhapsody single-cell | `bd-human-sc-xcr-rhapsody-cdr3`, `bd-sc-xcr-rhapsody-full-length` | preset-set | preset-set | CELL+UMI | full-length variant enables SHM/contig work |
| MiLaboratories kits | `milab-human-rna-tcr-umi-race`, `milab-human-rna-tcr-umi-multiplex`, `milab-human-dna-tcr-multiplex`, ... | per name | per name | per name | name decodes `<vendor>-<species>-<rna/dna>-<chain>-[umi]-<protocol>` |

For `generic-*` presets `--species <hsa|mmu|...>` is REQUIRED (forgetting it fails or misaligns). `xcr` presets cover TCR and BCR together; single-chain presets (`trb`, `ig`) cover one locus. For gamma-delta (TRG/TRD), use the same generic/kit presets and restrict chains at export with `-c TRG` / `-c TRD` (or a gd-specific kit preset if the wet-lab kit targets gd); note that a gd repertoire is invisible if the library only primed alpha-beta.

## Pipeline stages and where each one fails

`mixcr analyze <preset> R1.fastq.gz R2.fastq.gz out_prefix` runs the ordered stages below; the preset is embedded in the binary `.vdjca`/`.clns` files so hand-run commands only name the preset on `align`.

| Stage | Command | Purpose | Common failure |
|---|---|---|---|
| Align | `mixcr align -p <preset> --species hsa ...` | Reads -> V/D/J/C germline; extract barcodes if tag pattern set | Low alignment rate: wrong species/material/boundaries, untrimmed primers, reads too short to span CDR3 |
| Refine tags | `mixcr refineTagsAndSort` | UMI + cell-barcode error correction and sort | Skipped on a UMI library -> barcode errors become fake clonotypes; memory-heavy (~32 GB on large single-cell) |
| Assemble partial | `mixcr assemblePartial` (run x2) | Overlap fragmented mates that each cover part of CDR3 (RNA-seq/10x) | Needs `align --keep-non-CDR3-alignments` first; on amplicon reads that already span CDR3 it is wasted |
| Extend | `mixcr extend` | Impute unambiguous missing V/J germline ends | Safe for TCR; on BCR can fabricate germline over SHM-mutated ends |
| Assemble | `mixcr assemble` | Collapse alignments into clonotypes by the assembling feature; PCR/error correction, UMI consensus | Wrong assembling feature merges/splits clones; low-quality CDR3 filtered |
| Assemble cells | `mixcr assembleCells` | Single-cell: group per-chain clones by CELL barcode into paired cells | Needs cell tags; barcode contamination -> mispaired cells |
| Export | `mixcr exportClones` / `mixcr exportAirr` | Write clonotype TSV (native or AIRR) | Native field-name mistakes; forgetting `-c/--chains`; not filtering non-productive |
| QC | `mixcr qc`, `mixcr exportQc align`/`chainUsage` | Alignment rate, chain composition, tag coverage | Not run -> silent quality problems pass downstream |

From MiXCR 4.7, presets that do not intrinsically define an assembling feature REQUIRE `--assemble-clonotypes-by <feature>` (e.g. `CDR3`, `VDJRegion`); older tutorials that omit it now error. `CDR3` is the robust default on short reads; `VDJRegion` needs reads/contigs spanning V-through-J and keeps SHM variants separate (useful for BCR full-length).

## The quantitation denominator: reads vs UMIs vs cells

Clonotype abundance is only meaningful relative to the chemistry. Report the right unit or reintroduce the bias the chemistry was meant to remove:
- Non-UMI bulk: abundance = `readCount` (`cloneCount` is an alias). PCR-amplification biased -- not a molecule count.
- UMI bulk: after `refineTagsAndSort`, report `uniqueMoleculeCount` (generic form `uniqueTagCount Molecule`), NOT reads. Reporting reads on a UMI library re-adds the amplification bias the UMIs removed.
- Single-cell: the unit is the CELL (`uniqueTagCount Cell` / cellGroup), not reads or UMIs.

## Export: native MiXCR fields vs AIRR

MiXCR's native export headers are NOT AIRR or VDJtools names. Downstream renaming to a chosen schema is a user-side step; the field names to select from MiXCR are its own.

```bash
mixcr exportClones -c TRB \
    -cloneId -readCount -readFraction -uniqueMoleculeCount \
    -nSeqCDR3 -aaSeqCDR3 -bestVGene -bestJGene -allVHitsWithScore -isProductive VRegion \
    clones.clns clones_TRB.tsv
```

Key native fields: `cloneId`, `readCount`/`readFraction` (aliases `cloneCount`/`cloneFraction`), `uniqueMoleculeCount`, `nSeqCDR3`/`aaSeqCDR3` (CDR3 nt/aa -- the headline fields), `bestVGene`/`bestJGene`/`bestCGene` (gene-level), `bestVHit` (allele-level best), `allVHitsWithScore` (full hit list), `isProductive <feature>`. Filter flags: `-c/--chains TRB`, `-o` (drop out-of-frame), `-t` (drop stops), `--export-productive-clones-only`.

For AIRR-schema interchange (Immcantation, scirpy, any AIRR tool) use the dedicated command, which emits `sequence_id`, `v_call`, `d_call`, `j_call`, `junction`, `junction_aa`, `productive`, `duplicate_count`, `cell_id`:

```bash
mixcr exportAirr clones.clns clones.airr.tsv
```

Field-name traps (do NOT use as MiXCR selectors): `count`/`frequency`/`cdr3_aa`/`vGene` are VDJtools/AIRR conventions, not MiXCR headers. A downstream tool expecting AIRR names should be fed `exportAirr` output, not renamed native output.

## The D-gene caveat: never key or trust the D call in TRB/IGH

Dbeta and Dh segments are short (~12-16 nt) and heavily trimmed at both ends with N-additions between; the surviving germline-matchable D stretch is often 0-5 nt, statistically indistinguishable from random junctional nucleotides. A substantial fraction of TRB rearrangements have no detectable D at all (de Greef & de Boer 2021 *PNAS* 118:e2104367118), and any "longest germline D match" over-calls D by chance. Treat `bestDGene`/`allDHitsWithScore` as unreliable: never use the D call as a clonotype key, never stratify biology by D usage without heavy skepticism, and expect large tool-to-tool D disagreement. Clonotypes are keyed on CDR3 + V + J -- not D. This caveat is TRB- and IGH-specific: the TRD (delta) chain can incorporate one to two D segments in tandem, giving more germline D content than TRB's single heavily-trimmed D, so the D call is more informative for gamma-delta work (the junction is still highly diverse from N-additions).

## QC: match preset to chemistry, catch cross-contamination

```bash
mixcr qc clones.clns
mixcr exportQc align results/*.clns qc_align.pdf
mixcr exportQc chainUsage results/*.clns qc_chainUsage.pdf
```

Read `exportQc align`: targeted amplicon should align high (often >80-90%); a low rate signals wrong species/library/boundaries or untrimmed primers, and "absent CDR3" means reads too short or wrong boundaries. RNA-seq mining legitimately aligns a tiny fraction (only receptor-overlapping reads) -- judge it by absolute clonotype yield, not %. Read `chainUsage`: a TRB library showing appreciable IGH signals cross-contamination or index hopping on patterned flowcells. A huge reads-to-clonotypes drop (millions -> thousands, worse after UMI collapse) is normal; a tiny clone count with high alignment suggests over-aggressive filtering or a wrong assembling feature.

## Common Errors

| Symptom | Cause | Fix |
|---|---|---|
| Every processing command (align/analyze/assemble) refuses to run | No activated license (4.x mandatory for the pipeline; `mixcr --version`/`exportPreset` still work) | `mixcr activate-license` or set `MI_LICENSE_FILE`; whitelist phone-home IPs on firewalled nodes |
| `mixcr analyze amplicon ...` unknown | 3.x command removed in 4.x | Use `mixcr analyze <preset>`; pick a chemistry-matched preset |
| Runs cleanly but clonotypes look wrong (truncated CDR3, odd V calls) | Wrong preset / boundary / material -- silent, no error | Match preset to chemistry; audit with `mixcr exportPreset`; check `exportQc align` |
| Diversity far too high, many near-identical clones | UMI kit run without tag pattern -> no barcode collapse | Use the UMI preset or add `--tag-pattern`; ensure `refineTagsAndSort` ran; report `uniqueMoleculeCount` |
| RNA-seq run yields almost no clonotypes | No `assemblePartial`/`extend`; partials filtered at align | `align --keep-non-CDR3-alignments`, `assemblePartial` twice, then `extend` (or use `rna-seq` preset) |
| `assemble` errors asking for an assembling feature | Preset lacks intrinsic feature (4.7+) | Add `--assemble-clonotypes-by CDR3` (or `VDJRegion`) |
| Downstream AIRR tool rejects the table | Fed native MiXCR headers, not AIRR | Export with `mixcr exportAirr`, not renamed `exportClones` |
| D-gene usage plot looks meaningless / irreproducible | Trusting the near-unassignable D call in TRB/IGH | Drop D from keys and usage; report V/J only |
| `--species` missing on a generic preset | Generic presets require species | Add `--species hsa` (or `mmu`, taxon id) |
| refineTagsAndSort out-of-memory on single-cell | Barcode-heavy step needs large heap | `mixcr -Xmx32g refineTagsAndSort ...` |

## Related Skills

- vdjtools-analysis - Downstream diversity and overlap on bulk clonotypes
- immcantation-analysis - BCR clonal clustering, SHM and lineage from AIRR output
- scirpy-analysis - Single-cell VDJ integration with gene expression
- repertoire-visualization - Plot V/J usage and clonal structure
- specificity-annotation - Antigen-specificity clustering and database lookup
- read-qc/adapter-trimming - Upstream read QC and adapter handling
- workflows/tcr-pipeline - End-to-end orchestration

## References

- Bolotin DA, et al. MiXCR: software for comprehensive adaptive immunity profiling. *Nat Methods* 12:380-381 (2015).
- Bolotin DA, et al. Antigen receptor repertoire profiling from RNA-seq data. *Nat Biotechnol* 35:908-911 (2017).
- de Greef PC, de Boer RJ. TCRbeta rearrangements without a D segment are common, abundant, and public. *PNAS* 118:e2104367118 (2021).
- Vander Heiden JA, et al. AIRR Community standardized representations for annotated immune repertoires. *Front Immunol* 9:2206 (2018).
- MiXCR documentation. https://mixcr.com/mixcr/ (presets, mixins, exportClones/exportAirr, licensing, QC).
<!-- END FILE: tcr-bcr-analysis/mixcr-analysis/SKILL.md -->

## 子目录：tcr-bcr-analysis/repertoire-visualization

<!-- BEGIN FILE: tcr-bcr-analysis/repertoire-visualization/SKILL.md -->
---
name: bio-tcr-bcr-analysis-repertoire-visualization
description: Draws TCR/BCR repertoire figures - V-J chord/circos, CDR3 spectratype, clonal-space stratification, clonal tracking across timepoints, rarefaction/extrapolation curves, overlap heatmaps, and clonotype-similarity networks - and encodes how to read them. Use when choosing between a raw Shannon bar and a rarefaction curve for a diversity comparison; deciding a depth-robust overlap metric (Morisita-Horn) vs a set metric (Jaccard) for a heatmap; setting the distance threshold that defines a clonotype-similarity network; interpreting a Gaussian vs skewed spectratype as polyclonal vs clonally expanded; or laying out clonal-space and clone-tracking plots. Covers VDJtools PlotFancyVJUsage/RarefactionPlot, R circlize and iNEXT, and matplotlib/seaborn recipes.
tool_type: mixed
primary_tool: VDJtools
goal_approach_exempt: true
---

## Version Compatibility

Reference examples tested with: matplotlib 3.8+, seaborn 0.13+, pandas 2.2+, numpy 1.26+; R circlize 0.4+, iNEXT 3.0+; VDJtools 1.2.1+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

Note: matplotlib 3.9 removed `plt.cm.get_cmap(name, N)`; use `plt.get_cmap(name)` and sample it, or `matplotlib.colormaps[name].resampled(N)`. seaborn 0.13 deprecated bare `palette=` without `hue=`; assign `hue=` and `legend=False`.

# Repertoire Visualization

**"Plot my TCR/BCR repertoire"** -> Render V-J usage, CDR3-length spectratype, clonal-space, clonal tracking, diversity/rarefaction, overlap, and similarity-network figures, and read each one correctly.
- CLI: `vdjtools PlotFancyVJUsage`, `vdjtools RarefactionPlot` (delegates plotting to R)
- R: `circlize::chordDiagram` (V-J), `iNEXT::iNEXT` + `ggiNEXT` (rarefaction/extrapolation)
- Python: `matplotlib`/`seaborn` for bespoke figures; `numpy` multinomial resampling for rarefaction; `networkx` + `rapidfuzz` for similarity networks

## The governing principle: every figure inherits two upstream choices

A repertoire figure is only as valid as the numbers behind it, and those numbers depend on two decisions made before any plot is drawn:

1. The clonotype definition. A clonotype = CDR3 (nucleotide OR amino acid) + optionally V and J. Amino-acid CDR3 collapses convergent recombination (many nt rearrangements -> one aa clonotype), inflating apparent sharing and deflating richness; nt CDR3 is more conservative (Venturi et al. 2006 *PNAS* 103:18691). Every count on every axis shifts with this choice, so it must be stated in the figure and held constant across all samples in a comparison.
2. The sequencing depth. Richness, Shannon, clonality, and set-overlap (Jaccard, shared-clonotype counts) are strictly increasing functions of reads sequenced - the rare-clone tail never saturates. Diversity, rarefaction, and overlap figures are comparable across samples ONLY after depth normalization: downsample all samples to a common depth, or read rarefaction curves at a shared x. Comparing raw values across libraries of unequal depth measures sequencing effort, not biology (Chao et al. 2014 *Ecol Monogr* 84:45; Greiff et al. 2015 *Genome Med* 7:49). This caveat governs the diversity, rarefaction, and overlap recipes below.

## Choosing the figure and reading it

| Figure | What it reveals | How to compare correctly |
|--------|-----------------|--------------------------|
| V-J chord/circos | Combinatorial V-J pairing bias within one sample | Descriptive per sample; never compare raw usage across primer sets/platforms (primer bias masquerades as biology) |
| CDR3 spectratype | Clonal structure: Gaussian length distribution = polyclonal/naive, spikes = expansion | Weight by frequency to see expansions; by unique clonotypes to see underlying diversity |
| Clonal-space / proportion | Fraction of repertoire held by rare vs expanded clones | Bin by clone frequency (strata), not raw count; robust to depth if frequency-based |
| Clonal tracking | Expansion/contraction/persistence of clones over time | Downsample timepoints to common depth first; an "absent" clone is often a sampling zero |
| Rarefaction/extrapolation | Diversity comparison done right (interpolate to common depth) | Read all curves at a shared x; extrapolate at most 2-3x observed depth |
| Overlap heatmap | Pairwise repertoire similarity | Use Morisita-Horn (depth-robust) on depth-normalized samples; Jaccard is depth-biased |
| Similarity network | Clusters of related CDR3s (candidate specificity groups) | Structure depends entirely on the distance threshold; state it and test sensitivity |

## V-J usage: chord/circos and heatmap

The chord/circos shows which V and J segments pair, weighted by clonotype count, within one sample.

VDJtools route (delegates plotting to R; requires `RInstall` once):

```bash
vdjtools PlotFancyVJUsage -m metadata.txt output_dir/
```

R with circlize - a V-by-J count matrix becomes a chord diagram:

```r
library(circlize)

plot_vj_chord <- function(clone_df) {
    vj_matrix <- table(clone_df$v_gene, clone_df$j_gene)
    chordDiagram(vj_matrix, transparency = 0.5, annotationTrack = c('grid', 'name'))
}
```

Python heatmap alternative (samples x V gene, or V x J for one sample) avoids a chord dependency and reads more quantitatively for many segments:

```python
import seaborn as sns
import matplotlib.pyplot as plt

def plot_vj_heatmap(clone_df):
    vj = clone_df.pivot_table(index='v_gene', columns='j_gene', values='frequency', aggfunc='sum', fill_value=0)
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.heatmap(vj, cmap='viridis', ax=ax)
    ax.set_title('V-J pairing frequency')
    return fig
```

## CDR3 spectratype: length distribution reveals clonal structure

The spectratype is a histogram of CDR3 length. A roughly Gaussian, bell-shaped distribution indicates a diverse, polyclonal (naive-like) repertoire; skew or discrete spikes at particular lengths indicate clonal expansion(s). The classic immunoscope spectratype (and VDJtools `CalcSpectratype`) bins nucleotide length, where in-frame clones sit 3 nt apart and the periodicity is part of the readout; amino-acid length is a common simplification - state which is plotted. Weighting by read/UMI frequency shows expansions; weighting by unique clonotypes shows the underlying diversity - the two views can look opposite, so label which is plotted.

```python
def plot_spectratype(clone_df, length_col='cdr3_length'):
    fig, ax = plt.subplots(figsize=(9, 5))
    bins = range(clone_df[length_col].min(), clone_df[length_col].max() + 2)
    ax.hist(clone_df[length_col], bins=bins, weights=clone_df['frequency'], color='steelblue')
    ax.set_xlabel('CDR3 length (aa)')
    ax.set_ylabel('Frequency')  # Gaussian = polyclonal; spikes = clonal expansion
    return fig
```

## Clonal-space / proportion: how much repertoire the big clones hold

Bin clones into frequency strata (Rare / Small / Medium / Large / Hyperexpanded) and stack their summed frequency. Because strata are defined on frequency, this view is comparatively depth-robust and shows clonal-space homeostasis at a glance. A treemap of top clones is an alternative when individual dominant clones matter.

```python
import numpy as np

def plot_clonal_space(clone_df, sample_col='sample'):
    # Frequency-based strata (immunarch homeo convention); frequency makes this depth-robust
    edges = [0, 1e-4, 1e-3, 1e-2, 1e-1, 1.0]
    labels = ['Rare', 'Small', 'Medium', 'Large', 'Hyperexpanded']
    clone_df = clone_df.copy()
    clone_df['stratum'] = pd.cut(clone_df['frequency'], bins=edges, labels=labels)
    space = clone_df.groupby([sample_col, 'stratum'], observed=True)['frequency'].sum().unstack(fill_value=0)
    fig, ax = plt.subplots(figsize=(8, 5))
    space[labels].plot(kind='bar', stacked=True, ax=ax, colormap='viridis')
    ax.set_ylabel('Fraction of repertoire')
    return fig
```

## Clonal tracking across timepoints

Track individual clone frequencies over an ordered sample set (vaccination, infection, therapy). A line plot of the top clones, or an alluvial/stream for the same data, shows expansion, contraction, and persistence. Downsample timepoints to a common depth before declaring contraction - a clone scored absent at one timepoint is frequently below the sampling floor, not truly gone.

```python
def plot_clone_tracking(clone_df, top_n=10, clone_col='cdr3_aa', time_col='timepoint'):
    top = clone_df.groupby(clone_col)['frequency'].sum().nlargest(top_n).index
    fig, ax = plt.subplots(figsize=(9, 5))
    for clone in top:
        d = clone_df[clone_df[clone_col] == clone].sort_values(time_col)
        ax.plot(d[time_col], d['frequency'], marker='o', label=clone[:12])
    ax.set_xlabel('Timepoint'); ax.set_ylabel('Clone frequency')
    ax.legend(bbox_to_anchor=(1.02, 1), loc='upper left', fontsize=7)
    return fig
```

## Rarefaction/extrapolation: the correct way to compare diversity

A bare bar of Shannon (or observed richness) across samples of unequal depth is misleading - it plots depth as much as biology. The defensible comparison is a rarefaction/extrapolation curve: interpolate each sample down to (and extrapolate modestly above) a shared depth, then read diversity at a common x. iNEXT computes this for Hill numbers q=0/1/2 with confidence intervals (Hsieh et al. 2016 *Methods Ecol Evol* 7:1451; Chao et al. 2014 *Ecol Monogr* 84:45).

R route (gold standard, gives CIs):

```r
library(iNEXT)

# count_list: named list of per-sample integer clonotype-count vectors
out <- iNEXT(count_list, q = c(0, 1, 2), datatype = 'abundance')
ggiNEXT(out, type = 1)  # diversity vs sample size, read at a common x
```

VDJtools route: `vdjtools RarefactionPlot -m metadata.txt output_dir/`.

Python resampling route (interpolation by multinomial subsampling) when iNEXT is unavailable:

```python
def rarefaction_curve(counts, depths, reps=20, rng=None):
    # Interpolate observed richness by drawing 'm' reads without-replacement-like via multinomial
    rng = rng or np.random.default_rng(0)
    counts = np.asarray(counts, dtype=float)
    p = counts / counts.sum()
    total = int(counts.sum())
    richness = []
    for m in depths:
        if m > total:  # interpolation only; do not extrapolate past observed depth here
            richness.append(np.nan); continue
        obs = [np.count_nonzero(rng.multinomial(m, p)) for _ in range(reps)]
        richness.append(np.mean(obs))
    return richness
```

## Overlap heatmap: pick a depth-robust metric

An N-by-N similarity heatmap summarizes pairwise repertoire overlap. The metric choice is the decision: Morisita-Horn is abundance-weighted and near-invariant to sample size, so it is the default across unequal depths; Jaccard (presence/absence) is dominated by the shallower sample's depth and should not be compared across unequal-depth pairs. Compute the matrix in vdjtools-analysis on depth-normalized samples, then render it here. Label the metric in the title.

```python
def plot_overlap_heatmap(overlap_matrix, metric='Morisita-Horn'):
    fig, ax = plt.subplots(figsize=(7, 6))
    sns.heatmap(overlap_matrix, annot=True, fmt='.2f', cmap='YlOrRd', vmin=0, vmax=1, square=True, ax=ax)
    ax.set_title(f'Repertoire overlap ({metric})')  # state the metric; Jaccard is depth-biased
    return fig
```

## Clonotype-similarity network

Nodes are CDR3s, edges connect sequences within a chosen distance, and clusters are candidate specificity groups. The network structure depends entirely on the threshold: too loose chains distinct clones together, too tight fragments real groups. State the threshold and metric, and test sensitivity before interpreting clusters. Same-length CDR3s with Hamming distance is the conservative default; Levenshtein allows indels.

```python
import networkx as nx
from rapidfuzz.distance import Levenshtein

def build_similarity_network(clone_df, max_norm_dist=0.15, clone_col='cdr3_aa'):
    # normalized_similarity in [0,1]; edge when 1 - similarity <= threshold. Structure is threshold-dependent.
    clones = clone_df[clone_col].unique()
    g = nx.Graph()
    g.add_nodes_from(clones)
    for i, a in enumerate(clones):
        for b in clones[i + 1:]:
            if 1 - Levenshtein.normalized_similarity(a, b) <= max_norm_dist:
                g.add_edge(a, b)
    return g
```

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| Diversity "differs" between groups but tracks library size | Bare Shannon/richness bar across unequal depth | Downsample to common depth or plot rarefaction curves read at a shared x (iNEXT/RarefactionPlot) |
| Overlap heatmap shows huge differences driven by one shallow sample | Jaccard/shared-count on raw, unequal-depth counts | Use Morisita-Horn on depth-normalized samples; label the metric |
| Network clusters change completely on re-run with a new cutoff | Arbitrary distance threshold; single-linkage chaining | Fix and report the metric + threshold; run a sensitivity sweep; prefer Hamming on same-length CDR3s |
| Two figures disagree on sharing/diversity | Built on different clonotype definitions (nt vs aa, +/- V/J) | Hold one clonotype definition constant across all figures in a comparison and state it |
| Spectratype "expansion" vanishes when re-plotted | Switched between frequency-weighted and clonotype-weighted histogram | Choose one weighting per figure and label it (frequency shows expansions) |
| V-usage differences between batches look biological | Multiplex-PCR primer bias | Compare usage only within one protocol, or use UMI/5'RACE data |
| `plt.cm.get_cmap(name, N)` raises AttributeError | Removed in matplotlib 3.9+ | Use `plt.get_cmap(name)` or `matplotlib.colormaps[name].resampled(N)` |

## Related Skills

- vdjtools-analysis - Compute the diversity/overlap inputs (depth-normalized)
- mixcr-analysis - Produce clonotype tables
- scirpy-analysis - Single-cell clonal-expansion overlays
- data-visualization/ggplot2-fundamentals - General ggplot2 grammar
- data-visualization/heatmaps-clustering - Overlap/usage heatmap techniques

## References

- Shugay M, et al. VDJtools: unifying post-analysis of T cell receptor repertoires. *PLoS Comput Biol* 2015; 11(11):e1004503. (PlotFancyVJUsage, RarefactionPlot, overlap metrics.)
- Chao A, Gotelli NJ, Hsieh TC, Sander EL, Ma KH, Colwell RK, Ellison AM. Rarefaction and extrapolation with Hill numbers. *Ecol Monogr* 2014; 84(1):45-67. (Interpolation/extrapolation framework.)
- Hsieh TC, Ma KH, Chao A. iNEXT: an R package for rarefaction and extrapolation of species diversity (Hill numbers). *Methods Ecol Evol* 2016; 7(12):1451-1456. (Rarefaction/extrapolation curves with CIs.)
- Greiff V, et al. A bioinformatic framework for immune repertoire diversity profiling. *Genome Med* 2015; 7:49. (Hill-number diversity profiling of repertoires.)
- Venturi V, et al. Sharing of T cell receptors in antigen-specific responses is driven by convergent recombination. *PNAS* 2006; 103(49):18691-18696. (aa-clonotype sharing inflated by convergence.)
- Chao A. Nonparametric estimation of the number of classes in a population. *Scand J Stat* 1984; 11:265-270. (Chao1 richness estimator.)
<!-- END FILE: tcr-bcr-analysis/repertoire-visualization/SKILL.md -->

## 子目录：tcr-bcr-analysis/scirpy-analysis

<!-- BEGIN FILE: tcr-bcr-analysis/scirpy-analysis/SKILL.md -->
---
name: bio-tcr-bcr-analysis-scirpy-analysis
description: Integrates single-cell paired TCR/BCR (10x VDJ, AIRR, dandelion, BD Rhapsody) with gene expression in an AnnData/MuData object using scirpy - chain-pairing QC, clonotype definition, clonal expansion, diversity, repertoire overlap, V(D)J usage, and VDJdb specificity. Operates on the awkward-array AIRR model (adata.obsm['airr'], accessed via get.airr after pp.index_chains), not legacy per-chain obs columns. Use when deciding clonotype definition for TCR (exact CDR3-nt identity via define_clonotypes) versus BCR (nucleotide distance clustering via define_clonotype_clusters with normalized_hamming plus same_v_gene/same_j_gene, because somatic hypermutation shatters identity clonotypes); tuning receptor_arms (all vs any), dual_ir, and within_group; filtering chain_qc categories (multichain doublets, orphan dropout, extra-VJ dual-TCR) without biasing clonal-expansion and diversity estimates; and overlaying clonality onto the transcriptomic UMAP.
tool_type: python
primary_tool: scirpy
---

## Version Compatibility

Reference examples tested with: scirpy 0.24+, scanpy 1.10+, anndata 0.10+, mudata 0.3+, awkward 2+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

Note: since scirpy 0.13 the AIRR receptor data lives as an awkward array in `adata.obsm['airr']`, NOT in per-chain `adata.obs['IR_VJ_1_*']` columns. Fields are read with `scirpy.get.airr(...)` after `scirpy.pp.index_chains(...)`. Legacy (pre-0.13) objects must be migrated with `scirpy.io.upgrade_schema()`. Paired GEX+AIRR is held in a MuData with modalities `gex` and `airr`; tool/plot functions take the MuData and namespace their output obs columns as `airr:<column>`.

# scirpy Analysis

**"Analyze my single-cell paired TCR/BCR alongside gene expression"** -> Ingest AIRR receptor records, QC chain pairing, define clonotypes, and overlay clonality on the transcriptomic embedding, all in one AnnData/MuData object.
- Python: `scirpy.io.read_10x_vdj()` / `read_airr()` / `from_dandelion()`, `scirpy.pp.index_chains()`, `scirpy.tl.chain_qc()`, `scirpy.tl.define_clonotypes()` (TCR) or `scirpy.tl.define_clonotype_clusters()` (BCR)

## The governing principles

Two choices silently bias every downstream expansion, diversity, and overlap number. State both explicitly whenever reporting a result.

Principle 1 - the clonotype definition is a choice, and TCR and BCR need different ones. TCR does not somatically hypermutate, so all progeny of a founding T cell share the exact CDR3 nucleotide sequence: `tl.define_clonotypes` (implicit `metric='identity', sequence='nt'`) on CDR3-nt plus V and J is correct and defensible. B cells DO hypermutate during affinity maturation, so lineage members are NOT identical - `tl.define_clonotypes` shatters one true BCR lineage into dozens of fake singletons and destroys expansion and diversity estimates (Gupta 2015 *Bioinformatics* 31:3356). BCR requires `tl.define_clonotype_clusters` with a distance metric (`normalized_hamming`), `sequence='nt'` (SHM acts on nucleotides), and `same_v_gene=True, same_j_gene=True` to approximate clonal lineages. Even then scirpy returns clonal CLUSTERS, not germline-rooted phylogenies - hand off to Immcantation/dandelion/Dowser for true lineages, mutation calling, and selection.

Principle 2 - single-cell chain QC is the domain-specific hard part, and blanket filtering biases clonality upward. `tl.chain_qc` labels each cell (single pair, orphan VJ/VDJ, extra VJ/VDJ, two full chains, multichain, ambiguous). Multichain and TCR+BCR-ambiguous cells are likely doublets and are excluded from clonotype definition regardless. But dropping ALL orphan and extra-chain cells is not free: large clones capture both chains more often, so orphans are enriched for singletons, and deleting them preferentially removes small clones - inflating apparent clonal expansion and deflating diversity. Match the filter to the question, and report it.

## Clonotype definition: which function

**Goal:** Pick the clonotyping approach that matches the receptor's biology.

| Question | Function | metric / sequence | Best when | Fails when |
|----------|----------|-------------------|-----------|------------|
| TCR clonal identity | `define_clonotypes` | identity / nt (implicit) | TCR (no SHM); exact founder-lineage identity | Applied to BCR - SHM fragments lineages |
| BCR clonal lineage (approx.) | `define_clonotype_clusters` | normalized_hamming / nt + same_v_gene + same_j_gene | BCR; group SHM-diverged members of one lineage | Threshold not data-derived -> chains/merges clones |
| Convergent/functional TCR clusters | `define_clonotype_clusters` | tcrdist or alignment / aa | Antigen-convergent TCRs (different nt, same specificity) | Interpreted as recombination-event counts |
| Reconcile with bulk beta/heavy-only | `define_clonotype_clusters` | receptor_arms='VDJ' | Matching single-cell to bulk TRB/IGH repertoires | Paired-chain specificity is discarded |

`pp.ir_dist` computes and caches the VJ/VDJ distance matrices; the subsequent `define_*` call MUST use the SAME `metric` and `sequence` or the cached distances silently mismatch the grouping. For BCR the `cutoff` for `normalized_hamming` is a PERCENT distance, not a nucleotide count: `cutoff=15` means 15% mismatch (~85% identity). Set it from the bimodal distance-to-nearest-neighbor histogram (within-clone mode near 0 vs between-clone mode).

## Clustering parameters and their biology

| Parameter | Options | Meaning / when to change |
|-----------|---------|--------------------------|
| `receptor_arms` | all / any / VJ / VDJ | `all` (default): BOTH VJ (alpha/light) and VDJ (beta/heavy) must match - stringent, high specificity. `any` rescues single-arm dropout but can merge distinct clones sharing only a beta (beta convergence is real). `VDJ` mimics bulk beta/heavy-only clonotyping. |
| `dual_ir` | any / primary_only / all | Handles two chains of one arm. ~30% of T cells carry two productive TRA (allelic inclusion, Padovan 1993 *Science* 262:422) - so extra-VJ is real dual-TCR, not junk. `primary_only` uses the highest-UMI chain; `any` links cells sharing any chain; `all` requires both to correspond. |
| `same_v_gene` / `same_j_gene` | False / True | Require identical V (and J) gene, not just CDR3. Two cells can convergently share a CDR3 from different V genes; requiring same V/J enforces common ancestry. Turn ON for BCR lineage stringency. |
| `within_group` | 'receptor_type' (default) / obs col | Never merge clonotypes across this grouping. Default stops a B cell and a T cell joining one clonotype; set to sample/patient to forbid cross-sample clonotypes. |

## Load VDJ and build the joint object

**Goal:** Ingest receptor contigs and pair them with gene expression in one MuData.

**Approach:** `read_10x_vdj` (or `read_airr` / `from_dandelion`) returns an AIRR AnnData; wrap it with the GEX AnnData in a MuData keyed `gex`/`airr`, then index chains before any QC or clonotyping.

```python
import scirpy as ir
import scanpy as sc
import mudata as mu

adata_gex = sc.read_10x_h5('filtered_feature_bc_matrix.h5')
adata_airr = ir.io.read_10x_vdj('filtered_contig_annotations.csv')  # returns an AnnData, does NOT modify in place
# ir.io.read_airr(['tra.tsv', 'trb.tsv'])  # AIRR TSV from dandelion/Immcantation/airrflow
# ir.io.from_dandelion(dandelion_obj)      # round-trip a dandelion Dandelion object
# ir.io.upgrade_schema(legacy_adata)       # migrate a pre-0.13 obs-column object first

mdata = mu.MuData({'gex': adata_gex, 'airr': adata_airr})
ir.pp.index_chains(mdata)  # REQUIRED before QC/clonotyping; builds obsm['chain_indices']
```

## Chain QC and question-aware filtering

**Goal:** Categorize chain pairing and remove doublets without silently biasing clonality.

**Approach:** Run `chain_qc`, always drop multichain and TCR+BCR-ambiguous doublets, and decide orphan/extra retention by the downstream question - keep orphans for pure GEX overlay, drop them only for paired-clonotype/specificity work.

```python
ir.tl.chain_qc(mdata)  # writes obs: airr:receptor_type, airr:receptor_subtype, airr:chain_pairing
print(mdata.obs['airr:chain_pairing'].value_counts())

# Always exclude likely doublets from clonotype definition.
drop = ['multichain']
keep_types = mdata.obs['airr:receptor_type'].isin(['TCR', 'BCR'])  # exclude 'ambiguous' (TCR+BCR doublet)
paired = mdata[keep_types & ~mdata.obs['airr:chain_pairing'].isin(drop)].copy()

# For paired-clonotype/specificity analysis also require a complete receptor (drop orphans),
# but note this preferentially deletes small clones -> inflates expansion, deflates diversity.
complete = paired[paired.obs['airr:chain_pairing'].isin(['single pair', 'extra VJ', 'extra VDJ'])].copy()
```

## Define clonotypes - TCR (identity)

**Goal:** Group T cells sharing an exact CDR3-nucleotide founder rearrangement.

**Approach:** Cache identity distances, then partition; identity on CDR3-nt plus matching arms is the correct TCR clonotype.

```python
ir.pp.ir_dist(complete, metric='identity', sequence='nt', cutoff=0)
ir.tl.define_clonotypes(complete, receptor_arms='all', dual_ir='primary_only')  # writes airr:clone_id
print('TCR clonotypes:', complete.obs['airr:clone_id'].nunique())
```

## Define clonotypes - BCR (distance clusters)

**Goal:** Group SHM-diverged B cells of one lineage that identity clonotyping would shatter.

**Approach:** Use normalized Hamming distance on nucleotides within same-V/same-J partitions - this approximates a clonal lineage; identity clonotyping is WRONG for BCR.

```python
# cutoff=15 is a PERCENT distance for normalized_hamming (15% mismatch ~= 85% identity), NOT 15 nt;
# confirm from the distance-to-nearest-neighbor histogram (bimodal trough).
ir.pp.ir_dist(complete, metric='normalized_hamming', sequence='nt', cutoff=15)
ir.tl.define_clonotype_clusters(
    complete,
    sequence='nt', metric='normalized_hamming',
    receptor_arms='all', dual_ir='any',
    same_v_gene=True, same_j_gene=True,   # enforce common ancestry for lineage-grade clones
)  # writes airr:cc_nt_normalized_hamming (a clonotype-cluster id column)
# For true germline-rooted lineages, SHM, and selection: hand off to immcantation-analysis / dandelion / Dowser.
```

## Clonal expansion and diversity

**Goal:** Quantify how expanded each clone is and how diverse each group's repertoire is.

**Approach:** Bin cells by clone size, then compute per-group diversity - but remember both numbers depend entirely on the QC filter and clonotype definition above, so report them alongside.

```python
# target_col is resolved WITHIN the airr modality, so pass the bare name 'clone_id', not 'airr:clone_id'.
ir.tl.clonal_expansion(mdata, target_col='clone_id')  # bins per cell: singleton / 2 / >= 3 (breakpoints=(1, 2))
ir.pl.clonal_expansion(mdata, target_col='clone_id', groupby='airr:receptor_subtype')

# Alpha diversity per group; groupby names a full mdata.obs column, so it keeps its modality prefix.
ir.tl.alpha_diversity(mdata, groupby='gex:sample', target_col='clone_id', metric='normalized_shannon_entropy')

# Pairwise repertoire sharing (public/expanded clones, trafficking) - depth-sensitive; compare at equal depth.
ir.tl.repertoire_overlap(mdata, groupby='gex:sample', target_col='clone_id')
ir.pl.repertoire_overlap(mdata, groupby='gex:sample')
```

## Overlay clonality on the transcriptome

**Goal:** See which cell states the expanded clones occupy.

**Approach:** Cluster on GEX independently (never on receptor sequence), then color the transcriptomic UMAP by a clonality column pushed into the GEX modality.

```python
# GEX pipeline lives on mdata['gex']: normalize -> HVG -> PCA -> neighbors -> leiden -> umap (see single-cell/clustering).
mdata['gex'].obs['clonal_expansion'] = mdata.obs['airr:clonal_expansion']
sc.pl.umap(mdata['gex'], color='clonal_expansion')

# clonotype_modularity tests whether a clone's cells are more transcriptionally connected than random
# (needs sc.pp.neighbors on the GEX modality first) - distinguishes a coherent functional clone from scatter.
ir.tl.clonotype_modularity(mdata, target_col='clone_id')
```

## Gene usage and specificity

**Goal:** Summarize V(D)J segment usage and annotate antigen specificity.

**Approach:** Plot usage/spectratype directly; for specificity, match receptors against a reference database by sequence distance (not ML prediction).

```python
ir.pl.vdj_usage(mdata, full_combination=False)      # V-D-J segment flow (Sankey/ribbon)
ir.pl.spectratype(mdata, chain='VDJ_1', color='airr:receptor_subtype')  # CDR3-length distribution

# Antigen specificity by sequence match to a reference DB (reuses the ir_dist machinery).
vdjdb = ir.datasets.vdjdb()
ir.tl.ir_query(mdata, vdjdb, metric='identity', sequence='aa')
ir.tl.ir_query_annotate(mdata, vdjdb, include_ref_cols=['antigen.species', 'antigen.epitope'])
# For deeper TCR specificity modelling leave scirpy for tcrdist3 / CoNGA (see specificity-annotation).
```

## Export AIRR

**Goal:** Hand the receptor table to a bulk/interchange tool.

**Approach:** Write the AIRR modality as a standard rearrangement TSV; do NOT reconstruct it from stale per-chain obs columns (they no longer exist).

```python
ir.io.write_airr(mdata['airr'], 'scirpy_airr.tsv')
# Pull specific fields for a custom table with the get accessor, not obs indexing:
junction_vj = ir.get.airr(mdata, 'junction_aa', 'VJ_1')   # pandas Series
with ir.get.airr_context(mdata, 'junction_aa', ['VJ_1', 'VDJ_1']):
    pass  # AIRR fields temporarily materialized into obs for grouping/plotting
```

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| BCR lineages appear as hundreds of singletons; no expansion | Identity `define_clonotypes` used on B cells; SHM makes members non-identical | Use `define_clonotype_clusters` with `metric='normalized_hamming', sequence='nt', same_v_gene=True, same_j_gene=True` |
| `KeyError: 'IR_VJ_1_junction_aa'` / obs receptor columns missing | Pre-0.13 schema assumed; AIRR now lives in `obsm['airr']` | Access via `ir.get.airr(...)` after `pp.index_chains`; migrate legacy objects with `io.upgrade_schema()` |
| Expansion looks high, diversity looks low vs a collaborator | Blanket-filtered all orphan/extra-chain cells, deleting small clones | Keep orphans for GEX overlay; only drop them for paired-clonotype work, and report the filter |
| `define_*` gives grouping that ignores the chosen metric | `pp.ir_dist` metric/sequence differ from the `define_*` call | Match `metric` and `sequence` between `ir_dist` and `define_clonotype_clusters` |
| Clonotype/QC functions error or return nothing | `pp.index_chains` not run before QC/clonotyping | Run `ir.pp.index_chains(mdata)` immediately after building the MuData |
| Real T/B cells look receptor-negative | GEX-only cells (contig dropout) treated as VDJ-negative | Keep GEX-only cells with `NaN` clonotype for cell-state analysis; only drop VDJ-only cells failing GEX QC |
| Spurious shared/secondary chains in a hyperexpanded sample | Ambient VDJ mRNA from a dominant clone mis-assigned to droplets | Start from CellRanger `filtered_contig_annotations` (is_cell/high_confidence/productive), then drop secondary chains with very low UMI support (`duplicate_count`/`consensus_count`, e.g. < 2-3) before clonotyping |
| BCR distance clusters look degraded even with correct settings | CellRanger BCR contigs are not IMGT-numbered and include partial/nonproductive contigs | Reannotate with IgBLAST (dandelion/airrflow) before `define_clonotype_clusters`, or hand off to Immcantation |

## Related Skills

- mixcr-analysis - Process raw single-cell VDJ FASTQ
- immcantation-analysis - Proper BCR clonal lineages and SHM downstream
- specificity-annotation - Antigen-specificity clustering on single-cell clonotypes
- single-cell/data-io - Load and manage the GEX AnnData/MuData
- single-cell/clustering - Cell-state clustering to overlay clonality
- single-cell/doublet-detection - Corroborate multichain doublet calls

## References

- Sturm G, Szabo T, Fotakis G, Haider M, Rieder D, Trajanoski Z, Finotello F. Scirpy: a Scanpy extension for analyzing single-cell T-cell receptor-sequencing data. *Bioinformatics* 2020;36(18):4817-4818. doi:10.1093/bioinformatics/btaa611.
- Suo C, Polanski K, Dann E, et al. Dandelion uses the single-cell adaptive immune receptor repertoire to explore lymphocyte developmental origins. *Nature Biotechnology* 2024;42:40-51. doi:10.1038/s41587-023-01734-7.
- Gupta NT, Vander Heiden JA, Uduman M, Gadala-Maria D, Yaari G, Kleinstein SH. Change-O: a toolkit for analyzing large-scale B cell immunoglobulin repertoire sequencing data. *Bioinformatics* 2015;31(20):3356-3358. doi:10.1093/bioinformatics/btv359.
- Padovan E, Casorati G, Dellabona P, Meyer S, Brockhaus M, Lanzavecchia A. Expression of two T cell receptor alpha chains: dual receptor T cells. *Science* 1993;262:422-424. doi:10.1126/science.8211163.
- Vander Heiden JA, Marquez S, Marthandan N, et al. AIRR Community standardized representations for annotated immune repertoires. *Frontiers in Immunology* 2018;9:2206. doi:10.3389/fimmu.2018.02206.
<!-- END FILE: tcr-bcr-analysis/scirpy-analysis/SKILL.md -->

## 子目录：tcr-bcr-analysis/specificity-annotation

<!-- BEGIN FILE: tcr-bcr-analysis/specificity-annotation/SKILL.md -->
---
name: bio-tcr-bcr-analysis-specificity-annotation
description: Maps TCR/BCR receptor sequences toward candidate antigen specificity and clusters repertoires by shared-specificity signal, while enforcing that a database match or a cluster label is a HYPOTHESIS, not a specificity call. Use when deciding among database annotation (VDJdb/McPAS/IEDB+TCRMatch, requiring V-gene and HLA concordance plus a confidence score) versus sequence clustering (tcrdist3 meta-clonotypes, GLIPH2, GIANA, clusTCR, which find enrichment not per-receptor labels) versus generation-probability nulls (OLGA Pgen, IGoR, SONIA Ppost) for testing public/convergent/shared claims; and when guarding against overclaiming specificity, base-rate false positives from bare CDR3 matches, unpaired beta-only annotation, ML predictor failure on unseen epitopes, and ignored MHC restriction. TCR-focused with a BCR/antibody note (SHM, conformational epitopes, IGHV3-53/3-66 public clonotypes). Keywords CDR3, pMHC, HLA restriction, cross-reactivity, meta-clonotype, Pgen, public clonotype, convergent recombination.
tool_type: mixed
primary_tool: tcrdist3
---

## Version Compatibility

Reference examples tested with: tcrdist3 0.2+, olga 1.2+, pandas 2.0+, numpy 1.24+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

Note: OLGA's CLI entry point is `olga-compute_pgen` (underscore) and its bundled human beta model lives in `default_models/human_T_beta/`. GLIPH2 results are reference-repertoire- and parameter-sensitive; verify the reference set used and rerun with a second method before trusting cluster labels.

# Antigen-Specificity Annotation and Clustering for TCR/BCR Repertoires

**"Which antigens might my receptors recognize?"** -> Annotate CDR3s against curated TCR:pMHC records, keeping only defensible matches.
- Python: `pandas.merge` on VDJdb/McPAS export; IEDB `TCRMatch` for k-mer similarity to characterized receptors

**"Cluster my repertoire into shared-specificity groups."** -> Find sequence neighborhoods enriched for a common specificity.
- Python: `tcrdist.repertoire.TCRrep` (TCRdist neighborhoods / meta-clonotypes), GLIPH2, GIANA, clusTCR

**"Is this shared/public clonotype antigen-driven or just easy to generate?"** -> Test the sharing against a generation-probability null.
- Python/CLI: `olga` (Pgen), IGoR (learn the model), SONIA/soNNia (Ppost = Pgen x Q)

## The governing principle: a match or a cluster is a hypothesis, not a specificity call

Mapping receptor sequence to antigen specificity is largely UNSOLVED in the general case. Every method here does one of three things and none of them proves specificity: (a) it annotates against a biased database, (b) it finds a sequence neighborhood ENRICHED for shared specificity, or (c) it predicts binding only for epitopes seen in training. A VDJdb hit or a GLIPH2 cluster label is therefore a hypothesis with a confidence level, never "this receptor is specific for antigen Y". The entire job of this skill is to stop that overclaim: report annotations and clusters with their confidence, their required concordances (V-gene, HLA), and a generation-probability baseline, and reserve the word "specific" for tetramer/dextramer or functional confirmation.

Why the problem resists a clean solution:
- A TCR recognizes a peptide-MHC complex, not a peptide. Specificity is a property of the TCR:pMHC triple, so the same CDR3 can be specific for different peptides under different HLA. MHC restriction cannot be dropped.
- Massive cross-reactivity: a single TCR can recognize up to ~10^6 peptides (Sewell 2012 *Nat Rev Immunol* 12:669). One-receptor-one-antigen is false by design.
- Specificity is encoded jointly by the paired alpha and beta chains; bulk sequencing gives beta-only and discards the pairing that carries much of the signal.
- Training and database records are dominated by a few immunodominant epitopes (influenza GILGFVFTL, CMV NLVPMVATV, EBV GLCTLVAML, SARS-CoV-2), with heavy HLA-A*02:01 and CD8/MHC-I skew; CD4/MHC-II, gamma-delta TCR, and BCR data are sparse to absent. Any accuracy averaged over epitopes is inflated by the few easy ones, and a gamma-delta or CD4 repertoire will return almost nothing from these databases and models (absence of a hit is uninformative, not evidence of non-specificity).

## Three approaches: pick by the question, then corroborate

| Approach | Tools | What it answers | What it PROVES / does NOT | Best when | Fails when |
|----------|-------|-----------------|---------------------------|-----------|------------|
| Database annotation | VDJdb (score 0-3), McPAS-TCR, IEDB + TCRMatch | Does a curated TCR:pMHC record match this receptor? | A record matches; NOT that the receptor is specific (base-rate false positives) | Donor HLA known, V-gene available, high-confidence entries wanted | Bare CDR3 match, no HLA/V concordance, high-Pgen sequences match by chance |
| Sequence clustering | tcrdist3 meta-clonotypes, GLIPH2, GIANA, clusTCR, iSMART | Which receptors form a shared-specificity neighborhood? | A group is enriched for shared specificity; NOT a per-receptor antigen label | Discovering specificity groups, building reusable features from many receptors | Treating a cluster label as an antigen call; single-tool trust; no reference-null |
| Generation-probability null | OLGA (Pgen), IGoR, SONIA/soNNia (Ppost) | Is this sharing/convergence more than chance generation? | Whether a sequence is expected by recombination; the null for every sharing claim | Any "public"/convergent/shared/expanded-beyond-chance claim | Omitted entirely (the most common gap) -> publicity mistaken for antigen selection |

Default workflow: annotate with confidence and concordance, treat clusters as hypotheses, and attach a Pgen null to any sharing or convergence claim. Run at least two clustering methods and report agreement; benchmarks disagree on tool ranking by dataset and epitope, and there is no accepted gold standard (Meysman 2023 *ImmunoInformatics* 9:100024). Verify current best practice against each tool's latest docs before committing to one.

## Database annotation with the base-rate guardrail

**Goal:** Annotate a bulk beta repertoire against curated TCR:pMHC records without generating a flood of chance matches.

**Approach:** Restrict the database to confidence >= 1, join on CDR3 AND V-gene (never CDR3 alone), then drop matches whose restricting HLA the donor does not carry. A bare CDR3-beta match to a high-Pgen sequence is a base-rate false positive: the number of spurious hits scales with repertoire size x database size x match permissiveness.

```python
import pandas as pd

def annotate_by_db(repertoire, vdjdb, donor_hla, min_confidence=1):
    # repertoire, vdjdb: cdr3_b_aa + v_b_gene (IMGT, e.g. TRBV19*01); vdjdb also antigen_epitope, mhc_a, vdjdb_score
    # vdjdb_score 0-3: 0 = critical info missing, 3 = independently validated; >=1 drops single-observation noise
    db = vdjdb[vdjdb['vdjdb_score'] >= min_confidence]
    hits = repertoire.merge(db, on=['cdr3_b_aa', 'v_b_gene'], how='inner', suffixes=('', '_db'))  # V concordance, not CDR3 alone
    carries_hla = hits['mhc_a'].apply(lambda a: any(a.startswith(h) for h in donor_hla))  # restricting HLA must be present in donor
    hits = hits[carries_hla].copy()
    hits['annotation_confidence'] = 'hypothesis'  # a curated match, not a specificity call
    return hits
```

IEDB ships `TCRMatch` (Chronister 2021 *Front Immunol* 12:640725) for k-mer similarity of a CDR3-beta to characterized receptors: it returns a similarity score, which proves sequence similarity to a known receptor, not binding. Report match counts and an enrichment statistic against a size-matched synthetic/unexposed repertoire, not a binary "specific".

## Sequence clustering as neighborhood discovery

**Goal:** Group receptors into shared-specificity neighborhoods that can be quantified and reused, without mistaking a cluster for an antigen label.

**Approach:** TCRdist scores position-weighted CDR distances using the germline-encoded CDR1/CDR2/CDR2.5 loops (V-gene identity is baked in) plus the CDR3 up-weighted ~3x (Dash 2017 *Nature* 547:89). Build the pairwise beta matrix, then take fixed-radius neighborhoods in TCRdist units. A neighborhood is a meta-clonotype candidate (centroid + radius + optional motif), a testable feature, not a specificity assignment (Mayer-Blackwell 2021 *eLife* 10:e68605).

```python
import numpy as np
from tcrdist.repertoire import TCRrep

def beta_neighborhoods(clone_df, radius=50):
    # clone_df: cdr3_b_aa, v_b_gene, j_b_gene, count (IMGT gene names). organism/chains fix the germline loops used.
    tr = TCRrep(cell_df=clone_df, organism='human', chains=['beta'], db_file='alphabeta_gammadelta_db.tsv')
    # radius in TCRdist units; ~50 is a common meta-clonotype inclusion radius (Mayer-Blackwell 2021), tune per centroid
    neighbors = [set(np.where(row <= radius)[0]) for row in tr.pw_beta]
    return tr, neighbors
```

CDR3-only tools (GLIPH2 Huang 2020 *Nat Biotechnol* 38:1194; GIANA Zhang 2021 *Nat Commun* 12:4699; clusTCR Valkiers 2021 *Bioinformatics* 37:4865; iSMART Zhang 2020 *Clin Cancer Res* 26:1359) scale to millions of CDR3s but ignore the paired chain and often HLA, so they can merge receptors sharing a motif but differing in true restriction. GLIPH2 tends to produce large, low-specificity clusters and its enrichment is sensitive to the reference repertoire and input size; report the reference used and a null-corrected p-value, and prefer tcrdist3 meta-clonotypes as reusable features. For paired single-cell data, CoNGA (Schattgen 2022 *Nat Biotechnol* 40:54) links TCR neighborhoods to gene-expression state rather than to an antigen.

## Generation-probability nulls: the rigorous test for "public"/convergent

**Goal:** Decide whether a shared, convergent, or database-matched clonotype is antigen-driven or merely easy to generate.

**Approach:** High-Pgen sequences (few insertions, germline-like, short CDR3) recur across donors and match databases BY CHANCE, so publicity alone is not evidence of selection (Quigley 2010 *PNAS* 107:19414). Compute Pgen with OLGA (Sethna 2019 *Bioinformatics* 35:2974) for every match or shared clonotype and down-weight the high-Pgen ones; a clonotype is evidence of convergent selection only if observed more than its generation probability predicts. SONIA/soNNia add selection (Ppost = Pgen x Q) for a post-selection null.

```python
import os
import olga.load_model as load_model
import olga.generation_probability as generation_probability

def load_beta_pgen_model(model_dir):
    # model_dir = OLGA default_models/human_T_beta with model_params.txt, model_marginals.txt, V/J anchors CSV
    gen_data = load_model.GenomicDataVDJ()
    gen_data.load_igor_genomic_data(os.path.join(model_dir, 'model_params.txt'),
                                    os.path.join(model_dir, 'V_gene_CDR3_anchors.csv'),
                                    os.path.join(model_dir, 'J_gene_CDR3_anchors.csv'))
    gen_model = load_model.GenerativeModelVDJ()
    gen_model.load_and_process_igor_model(os.path.join(model_dir, 'model_marginals.txt'))
    return generation_probability.GenerationProbabilityVDJ(gen_model, gen_data)

def pgen(model, cdr3_b_aa, v_b_gene, j_b_gene):
    return model.compute_aa_CDR3_pgen(cdr3_b_aa, v_b_gene, j_b_gene)  # ~ms/seq; high value => expected by chance, down-weight
```

The CLI equivalent is `olga-compute_pgen --humanTRB CASSLGQAYEQYF` or `olga-compute_pgen --humanTRB -i seqs.tsv -o pgens.tsv`.

## ML binding predictors: interpolate within trained epitopes only

DeepTCR, ERGO-II, NetTCR-2.0, pMTnet, and TITAN predict TCR:epitope binding but interpolate WITHIN epitopes seen in training and collapse toward random on unseen epitopes (Moris 2021 *Brief Bioinform* 22:bbaa318; Grazioli 2022 *Front Immunol* 13:1014256). Published AUCs are inflated by data leakage (same epitope in train and test) and by negative-sampling artifacts, where models separate the negative-generation process rather than binding (Dens 2023 *Nat Mach Intell* 5:1060-1062). Gate any predictor to epitopes well-represented in its training set, never present a per-TCR score for a novel neoantigen as validated, and require leave-epitope-out evaluation with reference negatives. Cross-reference immunoinformatics/tcr-epitope-binding for the predictor details rather than duplicating them here.

## BCR/antibody note

Antibody specificity is harder than TCR: somatic hypermutation makes the functional sequence a moving target away from germline, and most antibody epitopes are conformational, so sequence-only epitope prediction is fundamentally limited and often needs structure. The sequence-level analogue of a public TCR is a convergent public antibody clonotype to a pathogen, e.g. the IGHV3-53/IGHV3-66 clonotype against the SARS-CoV-2 RBD (Robbiani 2020 *Nature* 584:437; Tan 2021 *Nat Commun* 12:4210). As with TCRs, a shared V-gene plus CDRH3 motif across donors is a hypothesis of convergent selection that still needs a Pgen/expected-sharing null and binding confirmation. Cluster BCR clones (shared V, J, junction length + within-partition distance) before any such analysis; see immcantation-analysis.

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| A repertoire reported "specific for antigen Y" from a DB hit or cluster | A curated match or a cluster label treated as ground-truth specificity | Report it as an annotation/hypothesis with confidence; confirm with tetramer/dextramer or functional assay before saying "specific" |
| Many DB matches to many epitopes in a large repertoire | Base-rate false positives from bare CDR3-beta matching to high-Pgen sequences | Require V-gene concordance, require donor HLA carriage, filter to VDJdb score >= 1-2, and attach a Pgen null |
| "Public"/convergent response claimed from sharing across donors | Sharing tested without a generation-probability baseline | Compute OLGA Pgen (or SONIA Ppost); a clonotype is convergent only if observed above its generation expectation |
| Beta-only annotation trusted as full specificity | Bulk data is unpaired; specificity is a paired alpha/beta + HLA property | Down-weight beta-only annotations; use single-cell paired alpha/beta (scirpy) or paired TCRdist where possible |
| ML predictor score believed for a new neoantigen | Predictors fail out-of-distribution on unseen epitopes; benchmark AUCs leak | Gate to well-trained epitopes; use leave-epitope-out validation and reference negatives; treat novel-epitope scores as unreliable |
| Cluster from one tool taken as truth | No gold standard; GLIPH2 clusters are reference- and parameter-sensitive | Run >= 2 methods, report agreement and the reference repertoire, check HLA-concordance and cluster tightness |
| HLA ignored in annotation | Specificity is a TCR:pMHC triple; the same CDR3 differs by restricting HLA | Restrict DB entries to alleles the donor carries; report the restricting HLA with every annotation |

## Related Skills

- mixcr-analysis - Produce clonotype tables to annotate
- scirpy-analysis - Paired single-cell clonotypes for specificity work
- vdjtools-analysis - Public-clonotype context and overlap
- immunoinformatics/tcr-epitope-binding - ML epitope-binding prediction details
- immunoinformatics/mhc-binding-prediction - Upstream pMHC restriction
- immunoinformatics/neoantigen-prediction - Neoantigen-directed specificity

## References

- Dash P, et al. Quantifiable predictive features define epitope-specific T cell receptor repertoires. *Nature* 2017; 547(7661):89-93.
- Glanville J, et al. Identifying specificity groups in the T cell receptor repertoire. *Nature* 2017; 547(7661):94-98.
- Huang H, et al. Analyzing the Mycobacterium tuberculosis immune response by T-cell receptor clustering with GLIPH2 and genome-wide antigen screening. *Nat Biotechnol* 2020; 38:1194-1202.
- Mayer-Blackwell K, et al. TCR meta-clonotypes for biomarker discovery with tcrdist3. *eLife* 2021; 10:e68605.
- Schattgen SA, et al. Integrating T cell receptor sequences and transcriptional profiles by clonotype neighbor graph analysis (CoNGA). *Nat Biotechnol* 2022; 40:54-63.
- Zhang H, et al. Investigation of Antigen-Specific T-Cell Receptor Clusters in Human Cancers (iSMART). *Clin Cancer Res* 2020; 26(6):1359-1371.
- Zhang H, et al. GIANA allows computationally-efficient TCR clustering and multi-disease repertoire classification by isometric transformation. *Nat Commun* 2021; 12:4699.
- Valkiers S, et al. clusTCR: a Python interface for rapid clustering of large sets of CDR3 sequences with unknown antigen specificity. *Bioinformatics* 2021; 37(24):4865-4867.
- Shugay M, et al. VDJdb: a curated database of T-cell receptor sequences with known antigen specificity. *Nucleic Acids Res* 2018; 46(D1):D419-D427.
- Tickotsky N, et al. McPAS-TCR: a manually curated catalogue of pathology-associated T cell receptor sequences. *Bioinformatics* 2017; 33(18):2924-2929.
- Chronister WD, et al. TCRMatch: predicting T-cell receptor specificity based on sequence similarity to previously characterized receptors. *Front Immunol* 2021; 12:640725.
- Marcou Q, Mora T, Walczak AM. High-throughput immune repertoire analysis with IGoR. *Nat Commun* 2018; 9:561.
- Sethna Z, et al. OLGA: fast computation of generation probabilities of B- and T-cell receptor amino acid sequences and motifs. *Bioinformatics* 2019; 35(17):2974-2981.
- Quigley MF, et al. Convergent recombination shapes the clonotypic landscape of the naive T-cell repertoire. *PNAS* 2010; 107:19414-19419.
- Moris P, et al. Current challenges for unseen-epitope TCR interaction prediction and a new perspective derived from image classification. *Brief Bioinform* 2021; 22(4):bbaa318.
- Meysman P, et al. Benchmarking solutions to the T-cell receptor epitope prediction problem (IMMREP22). *ImmunoInformatics* 2023; 9:100024.
- Robbiani DF, et al. Convergent antibody responses to SARS-CoV-2 in convalescent individuals. *Nature* 2020; 584:437-442.
- Tan TJC, et al. Sequence signatures of two public antibody clonotypes that bind SARS-CoV-2 RBD. *Nat Commun* 2021; 12:4210.
- Sewell AK. Why must T cells be cross-reactive? *Nat Rev Immunol* 2012; 12:669-677.
<!-- END FILE: tcr-bcr-analysis/specificity-annotation/SKILL.md -->

## 子目录：tcr-bcr-analysis/vdjtools-analysis

<!-- BEGIN FILE: tcr-bcr-analysis/vdjtools-analysis/SKILL.md -->
---
name: bio-tcr-bcr-analysis-vdjtools-analysis
description: Computes immune-repertoire diversity, clonal structure, overlap, and segment usage from TCR/BCR clonotype tables with VDJtools (immunarch as the modern R alternative). Use when deciding which diversity estimator answers a question (q=0 observed richness/chao1/chaoE, q=1 shannonWienerIndex, q=2 inverseSimpson as a Hill profile); normalizing sequencing depth before any cross-sample claim (DownSample or the resampled CalcDiversityStats table); choosing an overlap metric (depth-robust MorisitaHorn/F2 vs depth-biased Jaccard/public counts) and a clonotype match key (-i nt/aa, +/-V/J); summarizing clonality as 1 - normalizedShannonWienerIndex; reading spectratype and V-J usage under primer bias; interpreting public clonotypes; and choosing VDJtools (stable Java CLI) vs immunarch (active tidy R).
tool_type: cli
primary_tool: VDJtools
---

## Version Compatibility

Reference examples tested with: VDJtools 1.2.1+, Java (JRE 8+), R 4.x with ggplot2/reshape2/gridExtra (for Plot* modules), immunarch 0.9+/1.0+

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `java -jar vdjtools.jar` prints the current routine list; `<routine>` with no args prints its flags
- R: `packageVersion('immunarch')` then `?repDiversity` / `?repOverlap` to confirm `.method` strings

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

Note: routine names are CamelCase and case-sensitive, and the depth-resampling routine is `DownSample` (capital S). Run `RInstall` once so the `Plot*` modules can call R. VDJtools is post-analysis only: it consumes clonotype tables (from MiXCR etc.), not FASTQ.

# VDJtools Analysis

**"Compute diversity and compare my TCR/BCR repertoires"** -> summarize each repertoire's clonal structure, compare samples at equal depth, and quantify overlap.
- CLI: `java -jar vdjtools.jar CalcDiversityStats | CalcPairwiseDistances | TrackClonotypes`
- R alternative: immunarch `repDiversity()`, `repOverlap()`, `repClonality()`

## The governing principle: diversity is sampling-depth-dependent

A repertoire is a sample of an enormous, unevenly expanded clonal population with a long tail of rare clonotypes, so observed richness never saturates: deeper sequencing keeps discovering new clonotypes. Observed richness, Shannon entropy, clonality, Jaccard, and shared-clonotype counts are all functions of read depth. Comparing raw values across libraries of unequal depth measures depth, not biology -- this is the field's single most common and most invalidating error.

The fix is mandatory before any cross-sample claim: bring all samples to a common depth. Two routes:
- `DownSample -x <reads>` every sample to a shared depth, then analyze; or
- read `CalcDiversityStats` at a common depth from its resampled table. `CalcDiversityStats` emits two tables, `diversity.<i>.txt` (original) and `diversity.<i>.resampled.txt` (downsampled to the smallest sample or `-x`). Use the resampled/normalized values for between-sample comparison; the original table is for within-sample description only.

Choosing the normalization depth is itself a decision: downsampling every sample to the cohort minimum discards data and can leave everyone underpowered if one library is tiny. Set the common depth near the cohort's lower quartile, and EXCLUDE (do not drag everyone down to) any sample far below it -- a sample whose rarefaction curve is still steeply climbing well below the chosen depth is under-sampled and cannot support a diversity claim at all. Report the chosen depth and any excluded samples. `PlotQuantileStats` and the rarefaction curves show which samples are safe to include.

Rarefaction makes the problem visible: `RarefactionPlot` draws interpolated + extrapolated diversity-vs-depth curves. Compare samples at a common x, never at curve endpoints of different depth. Extrapolation is reliable only to ~2-3x observed depth and degrades for q=0 (Chao 2014).

## Report a Hill profile, not one number

A single index misleads because indices weight the abundance distribution differently. Report the Hill profile -- effective number of clonotypes at orders q=0, 1, 2 -- whose shape (steep drop from q=0 to q=2 = a few dominant clones over a large rare tail) is the informative object (Greiff 2015 *Genome Med* 7:49; Chao 2014 *Ecol Monogr* 84:45-67). Two repertoires can share richness yet have opposite clonality.

`CalcDiversityStats` emits these columns (each with `_mean`/`_std`); Gini is NOT among them (it is an immunarch option, not a VDJtools output):

| Column | Hill order | Question it answers | Depth-robustness |
|--------|-----------|---------------------|------------------|
| observedDiversity | q=0 | How many distinct clonotypes were seen | Poor -- must downsample |
| chao1 | q=0 | Nonparametric richness lower bound (uses singletons f1, doubletons f2) | Poor; breaks without count data (f2=0) or if rare clones were pre-filtered; PCR error inflates it |
| chaoE | q=0 | Chao richness extrapolated, normalized for cross-sample use | Moderate (VDJtools' preferred richness proxy) |
| efronThisted | q=0 | Efron-Thisted lower-bound total diversity | Poor; a lower bound, not the truth |
| shannonWienerIndex | q=1 | exp(Shannon), effective number weighting by frequency | Moderate |
| normalizedShannonWienerIndex | -- | Pielou evenness H'/ln(S), range 0-1 | Depth-dependent through ln(S) |
| inverseSimpson | q=2 | 1/sum(p^2), dominated by abundant clones | Best -- most depth-robust |
| d50 | -- | Fewest top clones covering 50% of reads | Poor; coarse descriptor |

Default: report q=0 (chaoE or downsampled observedDiversity), q=1 (shannonWienerIndex), and q=2 (inverseSimpson) together. Feed chao1/efronThisted only genuine count data with singletons and doubletons; on non-UMI, non-error-corrected data, PCR/sequencing errors manufacture singletons and inflate them arbitrarily.

## Clonality: the field default and its three flaws

Clonality = 1 - normalizedShannonWienerIndex = 1 - H'/ln(S). It runs 0 (even/polyclonal) to 1 (one clone dominates) and is the near-universal one-number summary because it is bounded and intuitive. State its flaws in any report:
1. Depth-dependent through the ln(S) denominator -- compare clonality only on depth-normalized samples.
2. It discards richness (it is a rescaled evenness): two repertoires with identical clonality can differ 100x in richness.
3. It is dominated by the middle of the abundance distribution, not the top clones a clinician cares about.

Fix: report clonality alongside a q=2 Hill number (inverseSimpson) and a rarefaction curve, never alone.

## Overlap: pick a depth-robust metric and hold the match key fixed

`CalcPairwiseDistances` builds an N x N matrix; `OverlapPair` compares two samples. Any count-of-shared-clonotypes or set index is dominated by the shallower sample's depth: a clone can only be shared if sampled in both, so the shallow sample caps the intersection. Downsample both samples to a common depth first, and prefer abundance-weighted metrics.

| Metric | Basis | Best when | Fails when |
|--------|-------|-----------|------------|
| MorisitaHorn | Abundance, size-normalized | Unequal depth; the default choice | -- (near-invariant to depth; dominated by abundant shared clones) |
| F2 | Sum of per-clonotype geometric-mean frequencies | Frequency-weighted overlap robust to a single dominant shared clone | -- (preferred VDJtools frequency metric) |
| F | Geometric mean of summed shared frequencies | Quick frequency overlap | One large shared clone dominates it |
| R | Pearson of log-frequencies over shared clones only | Concordance of abundances among shared clones | Ignores private clones entirely |
| D | Shared count / geometric-mean diversities | Descriptive | Numerator (shared count) still depth-biased |
| Jaccard | Presence/absence | Equal-depth, denoised samples only | Dominated by the shallower sample's depth |

Overlap magnitude also swings by orders of magnitude with the clonotype match key (`-i`): `nt` (strict, few coincidental shares) vs `aa` (convergent recombination inflates sharing), and whether V/J must match (`ntV`, `ntVJ`, `aaVJ`, ...). Fix one key and hold it constant across every comparison in a study; state it in every figure. `TrackClonotypes` does ordered all-vs-all intersection for time courses -- a clone scoring "absent" at a timepoint is often a sampling zero, so downsample timepoints to common depth before declaring contraction.

An overlap number is only interpretable against a null: some sharing is expected by chance from convergent recombination of high-Pgen clonotypes. To claim overlap EXCEEDS chance, compare the observed statistic to a background of unrelated-donor pairs, or to shuffled/label-permuted repertoires at the same depth, and for public-clonotype claims condition on generation probability (specificity-annotation). Two related individuals or two timepoints from one host will always overlap more than two random donors regardless of biology.

## Public is not antigen-driven

"Public" (a clonotype shared across individuals) is largely an artifact of generation probability, not shared antigen selection. High-Pgen CDR3s -- short, few insertions, near-germline (and fetal-generated) -- are independently produced by many donors, and convergent recombination compounds this at the aa level (Venturi 2006 *PNAS* 103:18691). So a public/shared count is enriched for stochastic high-Pgen sequences, not evidence of a shared response. To argue antigen association, condition on Pgen (OLGA/IGoR) or intersect with an antigen database (`ScanDatabase` against VDJdb; immunarch `dbAnnotate` against VDJdb/McPAS-TCR) -- and even a database hit is a sequence match, not proof of binding. Hand Pgen-aware interpretation off to specificity-annotation.

## Segment usage and spectratype

`CalcSegmentUsage` yields per-sample V/J frequency vectors; `CalcSpectratype` yields the CDR3-length histogram (`PlotFancySpectratype` overlays the top-N clones; `PlotSpectratypeV` stacks by V family; `PlotFancyVJUsage` is the V-J chord plot).
- Spectratype shape: a Gaussian/bell length distribution indicates a diverse polyclonal (naive-like) repertoire; skew or spikes at particular lengths indicate clonal expansion(s). Weighting by reads shows expansions; weighting by unique clonotypes shows underlying diversity.
- Confound: multiplex-PCR primer sets have V-gene-specific amplification bias, so apparent V/J usage differences between platforms or batches are frequently primer artifacts, not biology (Barennes 2021 *Nat Biotechnol* 39:236). Compare usage only within one protocol, or use 5'-RACE/UMI data. Usage vectors are compositional (sum to 1): CLR-transform before PCA and check that PC1 is not just depth/batch.

## VDJtools vs immunarch

Both consume the same clonotype tables; pick by pipeline, not by metric.

| | VDJtools | immunarch |
|--|----------|-----------|
| Language | Java CLI (calls R for plots) | R / tidyverse |
| Maintenance | Stable, low activity (~1.2.1) | Actively maintained (v1.0 adds `airr_*`) |
| Ingestion | `Convert -S <fmt>` | `repLoad()` auto-detects MiXCR/Adaptive/10x/AIRR/VDJtools |
| Plotting | Fixed `Plot*` PDFs | `vis()` returns editable ggplot objects |
| Strengths | Reference F/F2/chaoE + resampled tables; legacy reproducibility; pairs with MiXCR/VDJdb | 10x single-cell, k-mer/motif, publication plots, ML feature matrices |

Prefer VDJtools for CLI/legacy MiXCR pipelines and its exact resampled diversity tables; prefer immunarch for R, single-cell, k-mer/motif, or editable figures. Many groups convert with VDJtools and analyze/plot with immunarch.

Core operations in immunarch (verify `.method` strings on the installed version):

```r
library(immunarch)
data <- repLoad('samples_dir/')                       # metadata + tidy clonotype tables

repDiversity(data$data, .method = 'raref')            # rarefaction/extrapolation curves (the depth control)
repDiversity(data$data, .method = 'hill')             # Hill profile across q
repDiversity(data$data, .method = 'inv.simp')         # q=2, depth-robust
repClonality(data$data, .method = 'homeo')            # clonal-space homeostasis (Rare..Hyperexpanded bins)
repOverlap(data$data, .method = 'morisita')           # depth-robust overlap; 'jaccard'/'public' are depth-biased
geneUsage(data$data[[1]])                             # V/J usage vector
trackClonotypes(data$data, list('Sample1', 1:10))     # longitudinal tracking
dbAnnotate(data$data, vdjdb, 'CDR3.aa', 'cdr3')       # antigen-database annotation
```

## Prepare and normalize (CLI)

Convert upstream output, drop nonfunctional clones, and downsample to a shared depth before any comparison.

```bash
# Import MiXCR clonotypes to VDJtools format (also: -S migec/immunoseq/imgt/vidjil ...)
java -jar vdjtools.jar Convert -S mixcr mixcr_clones.txt converted/

# Keep only functional (in-frame, no-stop) clonotypes for functional-repertoire analysis
java -jar vdjtools.jar FilterNonFunctional -m metadata.txt filtered/

# Optional: remove cross-sample contamination (barcode switching / chimeras) before cross-sample work
java -jar vdjtools.jar Decontaminate -m metadata.txt decontaminated/

# Downsample every sample to a common read depth (capital S; -x/--size = target reads)
java -jar vdjtools.jar DownSample -x 100000 -m metadata.txt downsampled/
```

The metadata file is tab-delimited: a `#file.name  sample.id  <covariate...>` header row, then one row per sample. Most multi-sample routines consume it via `-m`.

## Diversity and overlap (CLI)

```bash
# Diversity: emits diversity.<i>.txt (original) AND diversity.<i>.resampled.txt (depth-normalized)
# Compare across samples using the RESAMPLED table only.
java -jar vdjtools.jar CalcDiversityStats -m metadata.txt diversity/

# Rarefaction curves -- the correct visual for comparing diversity across depths (read at common x)
java -jar vdjtools.jar RarefactionPlot -m metadata.txt rarefaction/

# Pairwise overlap; -i sets the clonotype match key (hold constant study-wide).
# Report MorisitaHorn / F2 columns; treat Jaccard as depth-biased.
java -jar vdjtools.jar CalcPairwiseDistances -i aa -m metadata.txt overlap/
java -jar vdjtools.jar ClusterSamples -e MorisitaHorn overlap/ clustered/

# Longitudinal tracking across an ordered sample set (downsample timepoints first)
java -jar vdjtools.jar TrackClonotypes -m metadata_timecourse.txt tracking/
```

## Parse VDJtools output in Python

```python
import pandas as pd

def load_resampled_diversity(prefix):
    '''Load the depth-normalized diversity table for cross-sample comparison.'''
    return pd.read_csv(f'{prefix}.strict.resampled.txt', sep='\t')

def load_overlap_matrix(path, metric='MorisitaHorn'):
    '''Load one depth-robust overlap metric from the pairwise-distance output.'''
    df = pd.read_csv(path, sep='\t')
    return df.pivot(index='1_sample_id', columns='2_sample_id', values=metric)
```

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| Deeper libraries look 'more diverse' every time | Comparing raw richness/Shannon/clonality across unequal depth -- measuring depth, not biology | `DownSample` to a common depth or read the `.resampled.txt` table; compare rarefaction curves at a common x |
| Overlap flips when samples are swapped or re-sequenced | Jaccard / public counts dominated by the shallower sample's depth | Downsample both, and report MorisitaHorn or F2 |
| Overlap magnitude differs wildly between studies | Different clonotype match key (`-i` aa vs nt, +/-V/J) | Fix one `-i` value and state it in every figure |
| chao1/efronThisted are NaN or absurdly large | Fed frequency-only or rare-clone-filtered data, or PCR errors created singletons | Provide genuine count data (singletons/doubletons); UMI/error-correct first; or use inverseSimpson |
| One clonality number reported as 'the diversity' | Clonality is a rescaled evenness that discards richness and is depth-dependent | Report Hill q=0/1/2 (add inverseSimpson) plus a rarefaction curve |
| 'Public' clones claimed as antigen-specific | Publicity is mostly high-Pgen convergent recombination | Condition on Pgen (OLGA) or intersect VDJdb via `ScanDatabase`; hand off to specificity-annotation |
| V/J usage differs between cohorts by platform | Multiplex-PCR primer bias, not biology | Compare usage only within a protocol; CLR-transform before PCA and check PC1 is not depth/batch |
| `Plot*` routine errors on start | R plotting dependencies missing | Run `java -jar vdjtools.jar RInstall` once |

## Related Skills

- mixcr-analysis - Generate input clonotype tables
- repertoire-visualization - Rarefaction, spectratype and overlap figures
- immcantation-analysis - BCR-aware diversity and clonal analysis
- specificity-annotation - Pgen-aware interpretation of public clonotypes
- experimental-design/sample-size - Sequencing depth and power planning
- workflows/tcr-pipeline - End-to-end orchestration

## References

- Shugay M, et al. VDJtools: unifying post-analysis of T cell receptor repertoires. *PLoS Comput Biol* 2015; 11(11):e1004503.
- Chao A, et al. Rarefaction and extrapolation with Hill numbers: a framework for sampling and estimation in species diversity studies. *Ecol Monogr* 2014; 84(1):45-67.
- Greiff V, et al. A bioinformatic framework for immune repertoire diversity profiling enables detection of immunological status. *Genome Med* 2015; 7:49.
- Chao A. Nonparametric estimation of the number of classes in a population. *Scand J Stat* 1984; 11:265-270.
- Venturi V, et al. Sharing of T cell receptors in antigen-specific responses is driven by convergent recombination. *PNAS* 2006; 103(49):18691-18696.
- Barennes P, et al. Benchmarking of T cell receptor repertoire profiling methods reveals large systematic biases. *Nat Biotechnol* 2021; 39:236-245.
- ImmunoMind Team. immunarch: an R package for painless analysis of T-cell and B-cell immune repertoires. CRAN / immunarch.com (v1.x).
<!-- END FILE: tcr-bcr-analysis/vdjtools-analysis/SKILL.md -->

<!-- END CATEGORY: tcr-bcr-analysis -->

