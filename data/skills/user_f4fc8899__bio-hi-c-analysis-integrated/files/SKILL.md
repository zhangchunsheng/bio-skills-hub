---
slug: bio-hi-c-analysis-integrated
version: 1.0.1
displayName: "Hi-C分析 / Hi-C analysis"
name: bio-hi-c-analysis-integrated
summary: "中文：Hi-C分析综合技能，整合 9 个相关专题，覆盖Hi-C分析：read pair处理、cooler矩阵、ICE/KR平衡、A/B compartment、TAD、loop调用。 English: Integrated Hi-C analysis skill covering 9 related topics, including Hi-C analysis: read pair processing, cooler matrices, ICE/KR balancing, A/B compartments, TAD detection, loop calling."
description: "中文：这是一个面向Hi-C分析的综合生物信息学 Skill，整合当前分类下 9 个相关专题能力。它用于根据研究问题、数据类型和分析阶段，选择合适的方法与工具，规划从输入检查、预处理、核心分析到质量控制、统计解释和结果报告的完整流程。重点覆盖：Hi-C分析：read pair处理、cooler矩阵、ICE/KR平衡、A/B compartment、TAD、loop调用。当用户提供相关实验数据、测序结果、表格或研究问题时，它会帮助判断分析目标与前置条件，给出工具选择、关键参数、输入输出、常见失败原因、结果解读和可复现建议。主要工具包括：cooler, cooltools, fithichip。该 Skill 提供分析设计与实施指导，不替代对具体数据质量、生物学背景和最终结论的人工审查。 English: This is an integrated bioinformatics Skill for Hi-C analysis, combining 9 related topic areas. It helps users choose appropriate methods and tools based on the research question, data type, and analysis stage, and plan an end-to-end workflow from input validation and preprocessing through core analysis, quality control, statistical interpretation, and reporting. It covers Hi-C analysis: read pair processing, cooler matrices, ICE/KR balancing, A/B compartments, TAD detection, loop calling. For relevant experimental data, sequencing results, tables, or research questions, it clarifies prerequisites, recommends tools and parameters, describes expected inputs and outputs, explains common failure modes, and supports reproducible analysis. Primary tools include: cooler, cooltools, fithichip. It provides methodological and implementation guidance; final data-quality assessment and biological conclusions still require human review."
---

# hi-c-analysis 分类 Skill 整合版

> 本文件整合同一主分类目录下 9 个子目录中的 SKILL.md 内容。
> 各子目录正文按原文保留，并通过标题和边界标记进行区分；源文件中的元数据块未被改写。

---

<!-- BEGIN CATEGORY: hi-c-analysis -->

## 子目录：hi-c-analysis/compartment-analysis

<!-- BEGIN FILE: hi-c-analysis/compartment-analysis/SKILL.md -->
---
name: bio-hi-c-analysis-compartment-analysis
description: Detects A/B chromatin compartments from balanced Hi-C contact matrices via eigenvector decomposition of the distance-normalized, Pearson-correlated cis matrix with cooltools (eigs_cis), then orients (phases) the compartment eigenvector against a GC or gene-density track so the active (A) sign is not arbitrary. Covers the eigenvector-is-a-choice problem (per-arm view_df to remove the centromere gradient; picking the eigenvector by max correlation with activity, not by eigenvalue), GC phasing with bioframe.frac_gc, resolution choice (100kb-1Mb), saddle plots and saddle_strength for compartmentalization strength, the cohesin-loss-strengthens-compartments result, subcompartments (SNIPER/Calder/dcHiC), and cross-condition compartment switching. Use when calling A/B compartments, computing E1/eigenvectors, phasing the eigenvector, building saddle plots, choosing a compartment resolution, quantifying compartment strength, or comparing compartmentalization across conditions.
tool_type: python
primary_tool: cooltools
---

## Version Compatibility

Reference examples tested with: cooler 0.10+, cooltools 0.7+, bioframe 0.7+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures

cooltools had a major API shift around 0.5 -> 0.7+ (functions standardized on `view_df`/viewframe arguments; `eigs_cis`, `expected_cis`, `saddle` signatures changed). The cooler MUST be balanced before any compartment analysis: `clr.matrix(balance=True)` requires a stored `weight` column. A `.mcool` is multi-resolution -- pass a single-resolution URI (`file.mcool::/resolutions/100000`), not the bare `.mcool`. The `phasing_track` MUST share the cooler's exact binning or phasing silently no-ops. If code throws ImportError, AttributeError, or TypeError, introspect the installed package and adapt the example to match the actual API rather than retrying.

# A/B Compartment Analysis

**"Which regions of my genome are in the active vs inactive compartment?"** -> Distance-normalize the cis matrix, take an eigenvector of its Pearson correlation matrix, then orient it by GC/gene density so positive = A (active) -- but verify the kept eigenvector is the compartment one, not an arm gradient.
- Python: `cooltools.eigs_cis(clr, gc_track, view_df=arms, n_eigs=3, sort_metric='pearsonr')`

## The Single Most Important Modern Insight -- E1 Is a Choice, Not an Output, and Its Sign Is Arbitrary Until Phased

The two most damaging beginner assumptions are "E1 = compartments" and "positive E1 = active." Both are false out of the box, and both fail *silently* -- the pipeline runs, returns a track, and is wrong.

1. **E1 is not guaranteed to be the compartment track.** On a *whole-chromosome* O/E correlation matrix the largest eigenvalue very often belongs to a smooth p-arm-vs-q-arm or centromere-to-telomere GRADIENT, not the plaid A/B checkerboard -- the real compartment signal then lands in E2 or E3. cooltools' own docs concede the first eigenvector "occasionally describes chromosomal arms or translocation blowouts." The compartment eigenvector is the one with the largest |correlation| to an activity track (GC, gene density, H3K27ac), not the one with the largest eigenvalue. The structural fix removes the gradient at the source: run `eigs_cis` per chromosome ARM (a `view_df` split at centromeres, from `bioframe.make_chromarms`), so the arm gradient is never in the within-arm matrix. Set `sort_metric='pearsonr'` so the returned eigenvectors are ordered by GC correlation, not eigenvalue -- otherwise the arm gradient is reported as "E1." A monotonic "compartment track" with no sign flips across a chromosome is the failure signature of a captured arm gradient.

2. **The sign is arbitrary until phased.** Eigenvectors are defined up to sign; the positive lobe is meaningless and can differ per chromosome AND per sample. The eigenvector MUST be oriented with an external active-chromatin track via the `phasing_track` argument so A = positive. GC content is the field default (it needs no extra assay and tracks compartment A; Lieberman-Aiden 2009 *Science* 326:289) -- compute it with `bioframe.frac_gc` at the compartment resolution, exactly matching the cooler's binning. Wrong/weak phasing flips A<->B silently, and every downstream saddle, switch call, and differential result inverts with no error. This is a classic source of irreproducible compartment papers.

3. **Compartments are an equilibrium phenomenon decoupled from TADs/loops.** Compartments = microphase separation of A/B chromatin states (cohesin-independent; survive cohesin loss, Schwarzer 2017 *Nature* 551:51, and CTCF loss, Nora 2017 *Cell* 169:930). TADs/loops = ATP-driven loop extrusion stalled at CTCF. Removing cohesin reinforces compartments while erasing TADs (Schwarzer 2017 reports reinforced compartmentalization on Nipbl loss; Rao 2017 *Cell* 171:305 eliminates all loop domains with compartments retained) -- loop extrusion actively mixes chromatin across compartment boundaries, so removing the extruder lets microphase separation run to completion (Nuebler 2018 *PNAS* 115:E6697). A preserved-or-stronger saddle after a cohesin/Nipbl/RAD21 perturbation is the EXPECTED result, not a bug; compartment-strength and TAD-strength are antagonistic. If a CTCF/cohesin perturbation makes compartments *vanish*, suspect a phasing artifact, not biology.

## Method / Output Taxonomy

| Output | Tool / call | What it is | When |
|--------|-------------|-----------|------|
| A/B eigenvector (E1) | `cooltools.eigs_cis` (cis, per-arm) | leading GC-phased eigenvector of the cis O/E correlation matrix; sign = A/B | standard A/B call, single map, per chromosome arm |
| Genome-wide A/B | `cooltools.eigs_trans` | eigenvector of inter-chromosomal blocks; immune to the cis arm-gradient | whole-genome A/B consensus with deep trans coverage |
| Compartment strength | `cooltools.saddle` + `saddle_strength` | (AA+BB)/(AB+BA) corner ratio of the saddle | comparing compartmentalization across conditions |
| 5-6 subcompartments | SNIPER (Xiong & Ma 2019 *Nat Commun* 10:5069) | autoencoder imputes inter-chr contacts -> MLP classifies A1/A2/B1/B2/B3 at 100kb | deep inter-chr data; Rao-style subcompartments |
| Continuous compartment rank | Calder (Liu 2021 *Nat Commun* 12:2439) | intra-chr divisive hierarchical clustering -> 0-1 multi-scale rank | cross-cell-line repositioning; modest coverage |
| Differential compartments | dcHiC (Chakraborty 2022 *Nat Commun* 13:6827) | quantile-normalized scores + multivariate Mahalanobis distance + significance; solves cross-sample sign flips | >=2 samples, "which bins switch A<->B" |
| Single-cell compartment | scA/B (Tan 2018 Dip-C *Science*) | CpG/activity proxy per locus; do NOT eigendecompose one sparse cell | scHi-C, ~20-50k contacts/cell |

## Decision Tree by Scenario

| Scenario | Recommended | Why |
|----------|-------------|-----|
| Matrix not yet balanced | `cooler balance` first (-> matrix-operations) | unbalanced -> O/E is all-NaN; meaningless eigenvector |
| Standard A/B call, one map | `eigs_cis` per arm at 100kb-1Mb, phase by GC | compartments are chromosome-scale; arms remove the centromere gradient |
| E1 looks monotonic / no sign flips | inspect E2/E3, pick by max |corr| with GC; or split by arm | E1 captured an arm/translocation gradient, not compartments |
| Sign of A/B seems inverted | confirm `phasing_track` is at the cooler's binning | weak/mismatched phasing flips A<->B silently |
| Want compartment STRENGTH | `saddle` + `saddle_strength`, fixed extent across samples | a single eigenvector does not quantify strength |
| Want 5-6 subcompartments | SNIPER or Calder, NOT more eigenvectors | subcompartments need inter-chr ML or hierarchical clustering, not `n_eigs` |
| Two+ conditions, compartment shift | -> hic-differential (dcHiC) | replicate-aware, sign-coherent across the cohort; hand-diffing eigenvectors flips signs |
| Single-cell Hi-C | scA/B (Dip-C), not a per-cell eigenvector | one sparse cell is too noisy to eigendecompose |
| Annotate switched bins with marks | -> chip-seq/chromatin-state-segmentation, chip-seq/peak-annotation | overlay ChromHMM/histone state on compartment calls |
| Render the eigenvector/saddle | -> hic-visualization; export bigWig -> genome-intervals/bigwig-tracks | track/heatmap conventions live there |

## Per-Arm Eigenvector with GC Phasing

**Goal:** Assign each genomic bin to the active (A) or inactive (B) compartment with a non-arbitrary sign, avoiding the centromere arm-gradient artifact.

**Approach:** Build a per-arm `view_df` (split at centromeres) so the arm gradient never enters the matrix; compute a GC-content phasing track at the cooler's exact binning; run `eigs_cis` with the GC track and `sort_metric='pearsonr'` so eigenvectors are ordered by GC correlation; then take the GC-correlated eigenvector as the compartment track.

```python
import cooler
import cooltools
import bioframe

clr = cooler.Cooler('matrix.mcool::/resolutions/100000')   # 100kb: compartments are coarse-scale
chromsizes = clr.chromsizes
cens = bioframe.fetch_centromeres('hg38')
arms = bioframe.make_chromarms(chromsizes, cens)            # per-arm view removes the centromere gradient
arms = arms[arms.chrom.isin(clr.chromnames)].reset_index(drop=True)

genome = bioframe.load_fasta('hg38.fa')                     # FASTA index (.fai) must exist
bins = clr.bins()[:][['chrom', 'start', 'end']]
gc = bioframe.frac_gc(bins, genome)                         # phasing track at the cooler's exact binning

eigvals, eigvecs = cooltools.eigs_cis(clr, gc, view_df=arms, n_eigs=3, sort_metric='pearsonr')
eigvecs['compartment'] = ['A' if e > 0 else 'B' for e in eigvecs['E1']]   # GC-phased: positive E1 = A
```

After phasing, sanity-check that `E1` correlates with `gc['GC']` (sign and magnitude). If the strongest correlation is in `E2`/`E3`, that component -- not `E1` -- is the compartment track; re-derive the call from it.

## Compartment Strength via Saddle Plot

**Goal:** Quantify how strongly the genome demixes into A and B with a single comparable number across conditions.

**Approach:** Compute the distance-decay expected; pass the cooler, the expected, and the *phased* E1 eigenvector to `saddle`, which digitizes E1 into quantile groups internally (via `qrange`) and aggregates O/E into a 2D table of same-vs-cross-compartment interactions; then read `saddle_strength` (the (AA+BB)/(AB+BA) corner ratio) at one fixed extent, applied identically to every sample compared.

```python
N_GROUPS = 38            # quantile groups for digitizing E1; ~30-50 is conventional (cooltools tutorial)
Q_LO, Q_HI = 0.025, 0.975   # trim the extreme 2.5% tails before digitizing to resist outlier bins

expected = cooltools.expected_cis(clr, view_df=arms)        # has the 'balanced.avg' column saddle needs
track = eigvecs[['chrom', 'start', 'end', 'E1']]           # the SAME phased E1 used for the A/B call
interaction_sum, interaction_count = cooltools.saddle(
    clr, expected, track, 'cis', n_bins=N_GROUPS, qrange=(Q_LO, Q_HI), view_df=arms
)
strength = cooltools.api.saddle.saddle_strength(interaction_sum, interaction_count)   # 1D array; lives in cooltools.api.saddle, not top level
EXTENT = N_GROUPS // 5   # read strength at the top/bottom ~20% of bins; pick one extent, use it everywhere
score = strength[EXTENT]
```

`saddle_strength` returns an ARRAY (cumulative corner ratio over increasing extent), not a scalar -- there is no canonical single number, so choose an extent and apply it identically across compared samples. Mismatched `n_bins`, resolution, `qrange`, or extent make strengths incomparable. Remember: a preserved-or-*higher* strength after cohesin/Nipbl/RAD21 loss is the expected result.

## Compare Compartments Across Conditions

**Goal:** Find bins that switch A<->B between two conditions without being fooled by per-sample sign flips.

**Approach:** Do NOT independently phase two eigenvectors and diff them bin-by-bin -- a weak per-chromosome GC correlation can flip the sign in one sample only, manufacturing fake "switches." Use dcHiC, which computes eigenvectors on quantile-normalized scores in a shared framework (sign-coherent across the cohort) and reports a multivariate significance per bin. Route this to hic-differential.

```python
# Hand-diffing is only safe when you have CONFIRMED both eigenvectors are sign-coherent (same arms phased
# to the same GC track with strong correlation). Otherwise use dcHiC -- see hic-differential.
import pandas as pd
merged = eig1.merge(eig2, on=['chrom', 'start', 'end'], suffixes=('_1', '_2'))
merged['switch'] = (merged['E1_1'] > 0) != (merged['E1_2'] > 0)   # only meaningful if both are phased coherently
```

## Per-Method Failure Modes

### Eigenvector captured the arm gradient
**Trigger:** `eigs_cis` run per whole chromosome (no per-arm `view_df`) and/or `sort_metric=None`. **Mechanism:** the largest eigenvalue belongs to the smooth p-vs-q arm / centromere gradient, not the A/B checkerboard. **Symptom:** a monotonic "compartment track" across a chromosome with no sign flips; weak correlation of E1 with GC. **Fix:** run per chromosome arm (`bioframe.make_chromarms`); set `sort_metric='pearsonr'`; pick the eigenvector with the largest |corr| to GC.

### Eigenvector sign not phased
**Trigger:** `eigs_cis` called with `phasing_track=None`. **Mechanism:** the sign of an eigenvector is mathematically arbitrary. **Symptom:** active euchromatin lands in "B"; A/B inverted relative to GC; per-chromosome sign inconsistency. **Fix:** pass a GC (or gene-density / H3K27ac) `phasing_track` so positive E1 = A.

### Phasing track at the wrong binning
**Trigger:** GC/activity track computed at a different resolution than the cooler. **Mechanism:** cooltools aligns the track to the cooler bins; a mismatch yields garbage correlations or a silent no-op. **Symptom:** phasing has no effect, or signs are random. **Fix:** compute the track on `clr.bins()` at the exact compartment resolution.

### Calling compartments at TAD/loop resolution
**Trigger:** `eigs_cis` at 5-25kb. **Mechanism:** compartments are a 100kb-1Mb feature; fine bins are sparse and dominated by TAD/loop structure and noise. **Symptom:** a noisy, jagged E1 that does not correlate with GC. **Fix:** call at 100kb-1Mb (250kb common; up to 1Mb for shallow data).

### Expecting subcompartments from more eigenvectors
**Trigger:** raising `n_eigs` to "get A1/A2/B1/B2/B3". **Mechanism:** Rao's 6 subcompartments came from clustering inter-chromosomal patterns in a 4.9-billion-contact map, not from extra eigenvectors. **Symptom:** higher eigenvectors are noise, not finer biology. **Fix:** use SNIPER (inter-chr ML) or Calder (hierarchical); for differential use dcHiC.

### Hand-diffing independently phased eigenvectors
**Trigger:** subtracting/comparing two per-sample eigenvectors bin-by-bin. **Mechanism:** a weak GC correlation can flip the sign in one sample only. **Symptom:** spurious "compartment switches" concentrated on whole chromosomes/arms. **Fix:** use dcHiC (sign-coherent quantile-normalized framework) -- see hic-differential.

### Saddle strengths not comparable across samples
**Trigger:** different `n_bins`, `qrange`, resolution, or extent between compared saddles. **Mechanism:** `saddle_strength` is an extent-dependent array, not an absolute scalar. **Symptom:** strength differences that track the settings, not the biology. **Fix:** fix `n_bins`, `qrange`, resolution, and the corner extent; apply identically to all samples.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| Compartment resolution 100kb-1Mb (250kb typical) | compartment scale (Lieberman-Aiden 2009) | finer bins mix in TAD/loop structure and sparsity noise; A/B is chromosome-scale |
| Run per chromosome ARM | eigenvector-selection (cooltools docs; Mirny lab) | removes the centromere/arm gradient that otherwise hijacks E1 |
| `sort_metric='pearsonr'` | cooltools default-mismatch | default sorts by eigenvalue, so the arm gradient is reported as E1; pearsonr sorts by GC correlation |
| `n_eigs>=3` and inspect eigenvalues | eigenvector-selection | n_eigs=1 hides the arm-vs-compartment problem; which component is biology is then undeterminable |
| `clip_percentile=99.9` (cooler `eigs_cis` default) | outlier suppression | dense `cis_eig` defaults `clip_percentile=0`; the entry points differ -- do not assume |
| Saddle quantile groups ~30-50; trim 2.5% tails | cooltools tutorial | enough groups to resolve the saddle; tail trim resists outlier bins |
| Saddle strength at a fixed extent (e.g. top/bottom ~20%) | saddle_strength is an array | no canonical scalar; one extent, applied identically across samples |
| Subcompartments require deep inter-chr data | Rao 2014 (4.9B contacts) | shallow maps + extra eigenvectors give noise, not subcompartments |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| `clr.matrix(balance=True)` / O/E all NaN | cooler not balanced | run `cooler balance` / `cooler.balance_cooler` first (-> matrix-operations) |
| Empty / wrong-resolution result on `.mcool` | bare `.mcool` passed | use `file.mcool::/resolutions/<bp>` URI |
| A/B compartments inverted | eigenvector sign unphased or weak phasing | pass a GC/gene-density `phasing_track` at the cooler's binning |
| E1 monotonic, no sign flips | whole-chromosome run captured the arm gradient | run per arm (`make_chromarms`); pick by max |corr| with GC |
| `frac_gc` / empty eigenvector on some chroms | chrom naming mismatch (`chr1` vs `1`) across cooler/FASTA/centromeres | harmonize names; subset the view to `clr.chromnames` |
| `saddle` KeyError on `balanced.avg` | wrong/absent expected table | pass `cooltools.expected_cis(clr, view_df=...)` output and `contact_type='cis'` |
| `AttributeError` on a cooltools function | pre-0.7 vs 0.7+ API change | `help(cooltools.eigs_cis)`; update to the viewframe signature |

## References

- Lieberman-Aiden E, van Berkum NL, et al. 2009. Comprehensive mapping of long-range interactions reveals folding principles of the human genome. *Science* 326:289-293.
- Rao SSP, Huntley MH, et al. 2014. A 3D map of the human genome at kilobase resolution reveals principles of chromatin looping. *Cell* 159:1665-1680.
- Nora EP, Goloborodko A, et al. 2017. Targeted degradation of CTCF decouples local insulation of chromosome domains from genomic compartmentalization. *Cell* 169:930-944.
- Schwarzer W, Abdennur N, et al. 2017. Two independent modes of chromatin organization revealed by cohesin removal. *Nature* 551:51-56.
- Rao SSP, Huang S-C, et al. 2017. Cohesin loss eliminates all loop domains. *Cell* 171:305-320.
- Nuebler J, Fudenberg G, Imakaev M, Abdennur N, Mirny LA. 2018. Chromatin organization by an interplay of loop extrusion and compartmental segregation. *PNAS* 115:E6697-E6706.
- Xiong K, Ma J. 2019. Revealing Hi-C subcompartments by imputing inter-chromosomal chromatin interactions. *Nat Commun* 10:5069.
- Tan L, Xing D, Chang C-H, Li H, Xie XS. 2018. Three-dimensional genome structures of single diploid human cells. *Science* 361(6405):924-928.
- Liu Y, Nanni L, et al. 2021. Systematic inference and comparison of multi-scale chromatin sub-compartments connects spatial organization to cell phenotypes. *Nat Commun* 12:2439.
- Chakraborty A, Wang JG, Ay F. 2022. dcHiC detects differential compartments across multiple Hi-C datasets. *Nat Commun* 13:6827.
- Chen Y, Zhang Y, et al. 2018. Mapping 3D genome organization relative to nuclear compartments using TSA-Seq as a cytological ruler. *J Cell Biol* 217:4025-4048.
- Abdennur N, et al. (Open2C). 2024. Cooltools: enabling high-resolution Hi-C analysis in Python. *PLoS Comput Biol* 20:e1012067.
- Abdennur N, Mirny LA. 2020. Cooler: scalable storage for Hi-C data and other genomically labeled arrays. *Bioinformatics* 36:311-316.

## Related Skills

- matrix-operations - Balancing and distance-normalized expected that compartment calling depends on
- hic-data-io - Load and access the cooler files this skill operates on
- hic-differential - dcHiC differential compartments and cross-condition switching
- tad-detection - The loop-extrusion partner of the two-mechanism framework; antagonistic strength
- hic-visualization - Render the eigenvector track and saddle plot
- chip-seq/chromatin-state-segmentation - Overlay ChromHMM/histone states on A/B compartments
- chip-seq/peak-annotation - Annotate switched bins with TF/histone peaks
- genome-intervals/bigwig-tracks - Export the eigenvector as a bigWig track
- single-cell/scatac-analysis - Single-cell chromatin context for scHi-C compartment work
<!-- END FILE: hi-c-analysis/compartment-analysis/SKILL.md -->

## 子目录：hi-c-analysis/contact-pairs

<!-- BEGIN FILE: hi-c-analysis/contact-pairs/SKILL.md -->
---
name: bio-hi-c-analysis-contact-pairs
description: Turns Hi-C/Micro-C FASTQ into a deduplicated, filtered .pairs file with pairtools and decides whether the library worked. Covers the bwa mem -SP5M / bwa-mem2 / chromap --preset hic alignment idiom (mates mapped as independent single-end reads), pairtools parse vs parse2 and the walks-policy choice (5unique pairwise vs all for Pore-C/Micro-C concatemers), pair-type classification (keep UU and rescued UC), dedup (PCR vs optical/by-tile), select by pair_type/MAPQ/distance, restriction-fragment handling (restrict, Arima dual-enzyme, Micro-C/DNase fragment-free), and allele-specific phasing (pairtools phase to two coolers). The library-QC decision uses % long-range cis as the one-number quality metric, trans as the noise floor, orientation balance as fragment-map-free dangling-end/self-circle QC, and % duplicates as a complexity proxy. Use when processing Hi-C/Micro-C/Omni-C reads into pairs, judging library quality, handling multi-enzyme or restriction-agnostic protocols, or generating allele-specific contacts.
tool_type: cli
primary_tool: pairtools
---

## Version Compatibility

Reference examples tested with: pairtools 1.1+, bwa 0.7.17+ (or bwa-mem2 2.2+), chromap 0.2+, samtools 1.19+, cooler 0.10+

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

pairtools defaults have shifted across releases (e.g. `parse --max-molecule-size` is 750 bp in 1.1.x; `dedup --backend` defaults to scipy). `parse` and `parse2` report DIFFERENT positions by default - confirm `--report-position` before mixing outputs. If a command errors, introspect with `pairtools <subcommand> --help` and adapt rather than retrying.

# Hi-C Contact Pairs

**"Turn my Hi-C reads into clean contacts and tell me if the library worked"** -> Align mates independently through ligation junctions, classify and deduplicate pairs to a 5'-canonical .pairs file, then read the cis/trans and orientation statistics to decide library quality before any matrix is built.
- CLI: `bwa mem -SP5M ref.fa R1.fq R2.fq | pairtools parse -c chrom.sizes | pairtools sort | pairtools dedup | pairtools stats`

## The Single Most Important Modern Insight -- The Read Count Is a Lie Until Pairs Are Classified; Library Quality Is Decided in pairtools, Not in the Aligner

A Hi-C library's *usable signal* is not "reads sequenced" - it is the **uniquely-mapped, deduplicated, long-range cis** contacts. Everything between FASTQ and the matrix exists to strip a *specific* artifact of proximity-ligation chemistry, and the diagnostic ratios from `pairtools stats` reveal whether the experiment succeeded **before** any compute is spent binning it. Three load-bearing consequences:

1. **% long-range cis is the one-number quality metric; trans is the noise floor.** True crosslink-ligation contacts are overwhelmingly cis and distance-decaying. Random ligation between two unrelated molecules in solution is as likely to be trans as cis-far, so **trans% is a direct readout of the spurious-ligation floor**. A good in-situ human library runs cis>=1kb ~50-65%, inter-chromosomal <10%. But these numbers are **genome-size dependent** - a yeast or bacterial genome legitimately has higher expected trans (more inter-chromosomal volume per cis distance). Never apply a human trans threshold to a microbe.

2. **The ligation junction lives INSIDE the read, so a local/split aligner aligning mates independently is required.** A single read often sequences *through* a ligation junction (locus A | locus B within one read). An end-to-end aligner soft-clips or mis-maps it and the contact is lost. `bwa mem -SP5M` aligns R1 and R2 as **independent single-end reads** (`-SP` skips mate rescue and pairing - proper-pair logic would destroy every long-range and trans contact) and marks the **5'-most chimeric segment primary** (`-5`, the anchor for pairtools' 5' convention). The chimera fraction rises with read length, so on 150bp PE and on Micro-C long reads this is a large, real chunk of contacts.

3. **Keep UU AND rescued UC; selecting only UU silently discards every rescued ligation.** A naive `select pair_type=="UU"` throws away the chimeric reads pairtools successfully reconstructed (UC = combined-unique) - a meaningful fraction on long reads. The 4DN standard keeps **UU and UC**.

## Aligner Taxonomy

| Aligner | Role | Hi-C invocation | When |
|---------|------|-----------------|------|
| bwa mem -SP5M | reference standard; local/split alignment reconstructs in-read junctions | `bwa mem -SP5M -t N ref.fa R1 R2` | default; best inter-contig accuracy in benchmarks |
| bwa-mem2 | drop-in faster reimplementation, identical output, same flags | `bwa-mem2 mem -SP5M -t N ref.fa R1 R2` | when speed matters and the larger index fits RAM |
| chromap --preset hic | ultrafast integrated align + dedup + pairs (4DN .pairs out) | `chromap --preset hic -x idx -r ref.fa -1 R1 -2 R2 -o out.pairs` | ~10x faster scans; trades fine walk-policy control for speed |

`-SP5M`, letter by letter: `-S` skip mate rescue; `-P` skip pairing (no proper-pair rescue); together `-SP` align mates as independent single-end reads. `-5` mark the 5'-most split segment primary (anchors the 5' convention). `-M` is legacy compatibility only (secondary flag 256 vs supplementary 2048); pairtools handles either - never agonize over `-M`, never drop `-SP5`.

## Decision Tree by Scenario

| Scenario | Recommended | Why |
|----------|-------------|-----|
| Standard in-situ/Omni-C, FASTQ -> matrix | bwa mem -SP5M -> parse (5unique) -> sort -> dedup -> stats | the 4DN/distiller default; restriction-agnostic |
| Fastest scan, control not critical | chromap --preset hic | integrated align+dedup+pairs ~10x faster |
| Multi-way contacts (Pore-C, MC-3C, Micro-C walks) | `parse --walks-policy all` or `parse2 --expand` | 5unique COLLAPSES concatemers to pairwise silently |
| Micro-C / DNase Hi-C | NO fragment map; do NOT apply a 1kb min-distance cut | sub-1kb (nucleosome ladder) is signal, not artifact |
| Arima / Hi-C 3.0 dual-enzyme, fragment-level | fragment file must encode BOTH motifs (`restrict -f`) | a single-enzyme digest file is silently wrong |
| Repeat-heavy genome / stringent loop anchors | raise `parse --min-mapq 30` | reclassifies borderline reads M, drops repeat false anchors |
| Allele-specific / diploid folding | diploid ref + `-XA` suboptimal hits -> `pairtools phase` -> two coolers | needs the suboptimal-score gap to resolve haplotypes |
| Decide whether to sequence deeper | complexity curve from dup model / preseq lc_extrap | a bare dup% without depth is meaningless |
| Build the matrix from clean pairs | -> hic-data-io (`cooler cload pairs`) | binning happens after classification/dedup |
| Annotate boundary/anchor coordinates | -> genome-intervals/bed-file-basics | pairs are 1-based, half-open conventions differ |

## Align: Mates as Independent Single-End Reads

```bash
bwa index ref.fa                                            # or bwa-mem2 index ref.fa
bwa mem -SP5M -t 16 ref.fa R1.fq.gz R2.fq.gz | \            # -SP: independent SE; -5: 5' segment primary
    samtools view -b -@ 8 - > aligned.bam
# chromap fast path (integrated align + dedup + 4DN pairs, no separate pairtools needed):
# chromap -i -r ref.fa -o idx && \
# chromap --preset hic -x idx -r ref.fa -1 R1.fq.gz -2 R2.fq.gz -o sample.pairs
```

## Parse, Sort, Dedup, Select: the pairtools Core

```bash
# Parse alignments into a 5'-canonical .pairs. min-mapq 1 (default) is permissive: only MAPQ-0 is "multi".
pairtools parse -c chrom.sizes --walks-policy 5unique --min-mapq 1 \
    --add-columns mapq --drop-sam aligned.bam | \
pairtools sort --nproc 8 | \                                # block-sort; flips to upper-triangular (5'-canonical)
pairtools dedup --max-mismatch 3 --mark-dups \              # within 3bp on both sides = duplicate; tag DD
    --output-stats sample.dedup.stats | \
pairtools select '(pair_type=="UU") or (pair_type=="UC")' \ # keep both-unique AND rescued chimeric
    -o sample.valid.pairs.gz
```

Dedup MUST run on a flipped, 5'-canonical file (`sort` does the flip); on a non-canonical file dedup under-collapses and dup% reads falsely low. `--max-molecule-size` (750 bp in 1.1.x) governs single-ligation chimera rescue; `--max-inter-align-gap` (20 bp) sets when a coverage gap becomes a null alignment.

## Library QC: the Decision This Skill Owns

`pairtools stats` is the canonical readout. Read it as a funnel, not a single number.

```bash
pairtools stats --bytile-dups -o sample.stats.tsv sample.valid.pairs.gz
# Key fields: frac_dups; frac_cis; cis_1kb+/cis_20kb+; trans; pair_types; dist_freq orientation FF/FR/RF/RR.
```

- **% long-range cis (cis>=1kb, often cis>=20kb)** = signal quality. **trans = noise floor** (genome-size dependent).
- **Orientation vs distance = fragment-map-free dangling-end/self-circle QC.** Above ~1kb the four orientations FF/FR/RF/RR each converge to ~25% (random, the positive QC signal). A short-range **FR (inward) spike** = dangling ends / undigested / self-ligation; a short-range **RF (outward) spike** = self-circles / religation. The distance where orientations equalize is the **minimum reliable contact distance** - derive the min-distance cut from this plot, do not hardcode 1kb (Micro-C structure lives below 1kb).
- **% duplicates = complexity proxy**, but `--bytile-dups` separates OPTICAL dups (patterned NovaSeq flowcells, same tile, adjacent coordinates) from PCR dups. Only the PCR fraction reflects library complexity; reading total dup% as over-amplification wrongly condemns a good library. A bare dup% without the depth it was measured at is meaningless - use the complexity/yield curve (preseq lc_extrap) to decide whether deeper sequencing buys uniques or duplicates.

Apply the QC-derived distance cut without a fragment map:

```bash
pairtools select '(chrom1!=chrom2) or (abs(pos2-pos1) > 1000)' \   # keep trans + cis beyond the orientation-equalization distance
    -o sample.filtered.pairs.gz sample.valid.pairs.gz
```

## Restriction Fragments: Opt-In, Not Default

Modern pipelines SKIP fragment filtering on purpose - the distance cut + dedup + UU/UC filter + balancing absorb the residual, and a digest file is one genome-specific place to mis-specify the enzyme. `pairtools restrict -f frags.bed` is opt-in for: sub-kb / restriction-fragment-resolution maps, capture-Hi-C / 4C-style fragment analysis, and bench QC where the dangling-end *fraction* is the digestion-efficiency readout.

```bash
cooler digest --out frags.bed chrom.sizes ref.fa DpnII     # single-enzyme: DpnII ^GATC
pairtools restrict -f frags.bed -o restricted.pairs.gz parsed.pairs.gz
```

**Arima dual-enzyme has FOUR junction motifs** (GATCGATC, GANTGATC, GANTANTC, GATCANTC); a single-enzyme (DpnII-only) digest file silently mis-assigns fragments. **Micro-C / DNase Hi-C have NO fragment map** (MNase/DNase cut sequence-nonspecifically) - any tool requiring a restriction file cannot process them, which is exactly why the restriction-agnostic pairtools path became the field default.

## Allele-Specific Contacts: pairtools phase -> Two Coolers

**Goal:** Resolve each contact to maternal vs paternal haplotype for allele-specific 3D folding.

**Approach:** Align to a diploid reference reporting suboptimal hits, so each read carries its best alignment on *both* homologs; `pairtools phase` reads the gap between the two best alignment scores to tag each side resolved-hap1 / resolved-hap2 / non-resolved / multi-mapper - the score gap is what separates a genuinely uninformative read from an actual repeat.

```bash
bcftools consensus -H 1 -f ref.fa phased.vcf.gz > hap1.fa   # build a diploid (two-homolog) reference
bcftools consensus -H 2 -f ref.fa phased.vcf.gz > hap2.fa
bwa mem -SP5M ref_diploid.fa R1.fq R2.fq | \                # report suboptimal hits so both homologs are kept
pairtools parse -c chrom.sizes --add-columns XB,AS,XS | \
pairtools phase --phase-suffixes _hap1 _hap2 --tag-mode XB | \
pairtools sort | pairtools dedup -o phased.pairs.gz
# Then split into hap1/hap2/trans pairs and cload each into a SEPARATE cooler.
```

## Per-Method Failure Modes

### Aligned Hi-C as a normal PE library
**Trigger:** plain `bwa mem` without `-SP`, or proper-pair logic. **Mechanism:** mate rescue forces the shotgun insert model on mates from different loci. **Symptom:** trans% collapses, compartments vanish, sparse map. **Fix:** `bwa mem -SP5M`, mates aligned independently.

### Dropped `-5`
**Trigger:** copying a pre-2016 `-SP` command lacking `-5`. **Mechanism:** the 5'-most chimeric segment is not primary, so pairtools picks an inconsistent anchor. **Symptom:** degraded flip/dedup, smeared loops. **Fix:** always `-SP5M` (or `-SP5`).

### walks-policy 5unique on a multi-way protocol
**Trigger:** Pore-C/MC-3C/Micro-C walks parsed with the default. **Mechanism:** 5unique reports only the two 5'-most alignments, collapsing concatemers to pairwise. **Symptom:** "we found few multi-contacts." **Fix:** `--walks-policy all` or `parse2 --expand`.

### Mixing parse and parse2 outputs
**Trigger:** combining a parse2 (.pairs, default outer/junction-anchored) file with a parse (5'-anchored) file. **Mechanism:** the two report positions by different conventions. **Symptom:** coordinates shift by the alignment length; dedup under-collapses; loops smear. **Fix:** one parser/convention per project; prefer plain `parse` if walks are not needed.

### Selecting only UU
**Trigger:** `select pair_type=="UU"`. **Mechanism:** discards rescued chimeric (UC) pairs. **Symptom:** lower valid-pair yield, especially on long reads. **Fix:** keep `(pair_type=="UU") or (pair_type=="UC")`.

### Dedup on a non-canonical file
**Trigger:** dedup run before `sort`/flip, or on mixed parse/parse2 positions. **Mechanism:** duplicates are not in canonical coordinates. **Symptom:** dup% reads falsely low - library looks better than it is. **Fix:** `sort` (flips to 5'-canonical) before `dedup`.

### Optical dups read as PCR dups
**Trigger:** total dup% on a patterned flowcell taken as library complexity. **Mechanism:** optical (same-tile) dups inflate apparent PCR rate. **Symptom:** a good library condemned as over-amplified. **Fix:** `--bytile-dups` / `--output-bytile-stats`; judge complexity on the PCR fraction only.

### Fixed 1kb cut on Micro-C
**Trigger:** applying Hi-C's >1kb min-distance cut to Micro-C. **Mechanism:** Micro-C's nucleosome-ladder signal lives below 1kb. **Symptom:** the structure Micro-C exists to capture is erased. **Fix:** derive the cut from the orientation-vs-distance plot per library.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| cis>=1kb ~50-65% of nodup pairs (good in-situ human) | Dovetail/Arima QC guidance (~approx) | long-range cis is the signal; library- and genome-size dependent |
| inter-chromosomal (trans) <10% (clean), 20-30% acceptable | in-situ Hi-C practice | trans is the spurious-ligation floor; NEVER apply to small genomes |
| FF/FR/RF/RR -> ~25% each above ~1kb | random strand combination at true contacts | convergence is the fragment-map-free positive QC signal |
| `parse --min-mapq` 1 default, raise to 30 for stringency | pairtools default | 1 drops only MAPQ-0; 30 removes repeat-driven false anchors |
| `dedup --max-mismatch` 3 bp | pairtools default | tolerates mapping wobble; 0 over-splits, larger over-collapses complexity |
| `parse --max-molecule-size` 750 bp (1.1.x) | pairtools default | bound on single-ligation chimera rescue; revisit for unusual size selection |
| min-distance cut ~1kb (Hi-C), derive from orientation plot | orientation-equalization distance | the cut is protocol-specific; Micro-C signal is sub-1kb |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| trans% high, no compartments | aligned without `-SP` (proper-pair logic) | re-align `bwa mem -SP5M` |
| Few multi-way contacts on Pore-C/Micro-C | default `--walks-policy 5unique` collapsed walks | `--walks-policy all` / `parse2 --expand` |
| Loops smeared, dedup under-collapses | mixed parse/parse2 position conventions | one parser per project; `sort` before `dedup` |
| Valid-pair yield lower than expected | `select` kept only UU | keep UU and UC |
| dup% suspiciously low | dedup ran before `sort`/flip | sort to 5'-canonical first |
| dup% high on NovaSeq, complexity looks bad | optical dups counted as PCR | `--bytile-dups`; judge on PCR fraction |
| Micro-C structure disappears after filtering | fixed 1kb min-distance cut | derive cut from orientation-vs-distance |
| Fragment assignment wrong on Arima data | single-enzyme digest file | encode all four Arima junction motifs |
| `phase` resolves nothing | aligned to a haploid reference | diploid ref + suboptimal (`-XA`) alignments |

## References

- Open2C, Abdennur N, Fudenberg G, Flyamer IM, Galitsyna AA, Goloborodko A, Imakaev M, Venev SV. 2024. Pairtools: from sequencing data to chromosome contacts. *PLoS Comput Biol* 20(5):e1012164.
- Li H. 2013. Aligning sequence reads, clone sequences and assembly contigs with BWA-MEM. arXiv:1303.3997.
- Zhang H, Song L, Wang X, et al. 2021. Fast alignment and preprocessing of chromatin profiles with Chromap. *Nat Commun* 12:6566.
- Durand NC, Shamim MS, Machol I, et al. 2016. Juicer provides a one-click system for analyzing loop-resolution Hi-C experiments. *Cell Syst* 3:95-98.
- Servant N, Varoquaux N, Lajoie BR, et al. 2015. HiC-Pro: an optimized and flexible pipeline for Hi-C data processing. *Genome Biol* 16:259.
- Akgol Oksuz B, Yang L, Abraham S, et al. 2021. Systematic evaluation of chromosome conformation capture assays. *Nat Methods* 18:1046-1055.
- Krietenstein N, Abraham S, Venev SV, et al. 2020. Ultrastructural details of mammalian chromosome architecture (Micro-C). *Mol Cell* 78:554-565.
- Ramani V, Cusanovich DA, Hause RJ, et al. 2016. Mapping 3D genome architecture through in situ DNase Hi-C. *Nat Protoc* 11:2104-2121.
- Abdennur N, Mirny LA. 2020. Cooler: scalable storage for Hi-C data and other genomically labeled arrays. *Bioinformatics* 36:311-316.
- Daley T, Smith AD. 2013. Predicting the molecular complexity of sequencing libraries (preseq). *Nat Methods* 10:325-327.

## Related Skills

- hic-data-io - Bins the deduplicated valid pairs into a .cool/.mcool matrix
- matrix-operations - Balancing and O/E that the binned pairs feed into
- hic-visualization - Render contact maps from the resulting cooler
- read-alignment/bwa-alignment - Aligner upstream; this skill adds the Hi-C `-SP5M` idiom
- alignment-files/duplicate-handling - General duplicate-marking context for the pairtools dedup step
- genome-intervals/bed-file-basics - Coordinate/digest BED handling for restriction fragments and anchors
- genome-assembly/scaffolding - Same Hi-C reads used to order contigs into chromosomes
<!-- END FILE: hi-c-analysis/contact-pairs/SKILL.md -->

## 子目录：hi-c-analysis/hic-data-io

<!-- BEGIN FILE: hi-c-analysis/hic-data-io/SKILL.md -->
---
name: bio-hi-c-analysis-hic-data-io
description: Loads, converts, and manipulates Hi-C contact matrices in cooler format (.cool/.mcool/.scool) and Juicer .hic, using cooler (Python + CLI), hic2cool, and hictk. Covers the single-resolution mcool URI (file.mcool::/resolutions/<bp>), the load-bearing divisive-vs-multiplicative weight-naming rule (KR/VC/VC_SQRT auto-divisive vs cooler's multiplicative weight), what survives .hic<->.cool conversion (FRAG matrices and norm vectors do not), raw-vs-balanced coarsening, the .pairs upper-triangle/chromsize-order contract, and chrom-naming/bin-table provenance. Use when loading a cooler, converting .hic to .mcool, selecting a resolution, building a cooler from pairs or a matrix, coarsening/zoomifying, importing Juicer norm vectors, or debugging all-NaN balanced matrices and chr1-vs-1 empty fetches.
tool_type: mixed
primary_tool: cooler
---

## Version Compatibility

Reference examples tested with: cooler 0.10+, hic2cool 1.0+, hictk 1.0+, bioframe 0.7+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

Two version boundaries change BEHAVIOUR, not just signatures: hic2cool >= 0.5.0 stores Juicer norms un-inverted (divisive); < 0.5.0 inverted them to multiplicative, so two coolers made from one .hic by different hic2cool versions disagree numerically. cooler standardized creation/balance signatures around 0.8-0.10 (`balance_cooler` keyword-only after `clr`; `store=False` default). Record the converter version in provenance.

# Hi-C Data I/O

**"Load my Hi-C contact matrix, convert it, and pull out a region."** -> Open the cooler at one resolution, fetch raw or balanced pixels, and convert across .hic/.cool/.mcool while knowing what does not survive the round trip.
- Python: `cooler.Cooler('file.mcool::/resolutions/10000').matrix(balance=True).fetch('chr1')`
- CLI: `hic2cool convert in.hic out.mcool -r 0` / `hictk convert in.hic out.mcool` / `cooler cload pairs ...`

## The Single Most Important Modern Insight -- cooler Stores Observed Counts; .hic Bakes In Norms, So Conversion Is Never Lossless Both Ways

A `.cool` is a thin, open, HDF5-native *store*: three tables (`chroms`, `bins`, `pixels`) holding raw observed integer counts in an upper-triangle COO layout, plus optional cached `weight` bias columns. Balancing, expected, O/E, eigenvectors -- everything else is computed downstream on demand. Juicer's `.hic` is the opposite philosophy: a sealed binary *deliverable* with all resolutions, precomputed normalization vectors, and expected vectors welded in. Every footgun in this skill descends from that split:

- **Conversion translates between two philosophies, not two encodings.** `.hic -> .cool` loses FRAG (restriction-fragment) matrices (cooler has no FRAG concept) and Juicer's precomputed expected; a norm whose vector is missing arrives as all-NaN. `.cool -> .hic` loses asymmetric matrices, arbitrary extra pixel value columns, and non-Hi-C labeled arrays.
- **The `weight` column NAME is load-bearing.** cooler's own ICE `weight` is applied MULTIPLICATIVELY by `matrix(balance=True)`. Juicer KR/VC norms are DIVISIVE. `Cooler.matrix(divisive_weights=None)` (the default) decides by column name: weights named **KR, VC, or VC_SQRT are auto-treated as divisive**; everything else (including `weight`) is multiplicative. Import a KR vector under the name `weight` and it is applied the wrong way -- garbage, no error.
- **`.mcool` is a container of resolutions, not a matrix.** Every downstream tool wants a single-resolution URI `file.mcool::/resolutions/<bp>`, never the bare `.mcool`. Each resolution is balanced from scratch; the 100kb `weight` is NOT derivable from the 10kb `weight`.

## Format and Tool Taxonomy

| Format / Tool | Role | Mechanism | When |
|---------------|------|-----------|------|
| `.cool` | single-resolution store | HDF5 chroms/bins/pixels, raw counts + optional weight | one resolution; the analysis unit |
| `.mcool` | multi-resolution container | `/resolutions/<bp>/` each a full cooler | HiGlass tilesets; pick a resolution via URI |
| `.scool` | single-cell container | shared bins, `/cells/<name>/pixels` | scHi-C; avoids duplicating the bin table per cell |
| `.hic` (Juicer) | sealed deliverable | binary, all resolutions + baked norm/expected | Juicer/Juicebox ecosystem; BP or FRAG bins |
| `.pairs` (4DN) | upstream contact list | bgzip + pairix index; upper-triangle, flipped | input to `cooler cload`; provenance of the matrix |
| cooler (CLI+Py) | the open standard store/API | pandas/scipy selectors; `cload`/`balance`/`zoomify`/`dump` | the default; cooltools integration |
| hic2cool | .hic -> .cool/.mcool | 4DN-canonical norm handler (>=0.5.0 un-inverted) | importing Juicer norms; BP only |
| hictk | fast cross-format convert/dump | C++; reads .hic v6-9 + cooler, writes .hic v9 + cooler | large files; faster than hic2cool/straw; no FRAG, no asymmetric |

## Decision Tree by Scenario

| Scenario | Recommended | Why |
|----------|-------------|-----|
| Bare `.mcool`, tool errors / wrong scale | append `::/resolutions/<bp>` URI | the .mcool is a container; tools need one resolution |
| `.hic` -> `.mcool`, want Juicer KR/SCALE preserved | `hic2cool convert -r 0` | 4DN-canonical norm handling; keeps divisive names |
| `.hic` -> cooler, large file, speed matters | `hictk convert` | C++, order-of-magnitude faster; but no FRAG |
| `.hic` was FRAG-binned | re-bin from pairs in BP | FRAG does not survive any converter -> contact-pairs |
| Build a cooler from `.pairs` | `cooler cload pairs -c1 -p1 -c2 -p2 sizes.txt:bp` | needs flipped/deduped pairs -> contact-pairs |
| Need lower resolution | `cooler zoomify --balance` (sum RAW, re-ICE) | cannot sum balanced pixels; re-balance per resolution |
| Imported KR/VC norms | keep their original names | the KR/VC/VC_SQRT auto-divisive rule fires only on those names |
| `matrix(balance=True)` raises / all NaN | balance first; NaN rows = masked bins | unbalanced file has no weight; masked bins are expected NaN |
| `fetch('1')` returns empty on a `chr1` file | harmonize chrom naming first | chr1-vs-1 silently zeros every join, no error |
| Balance/normalize for analysis | -> matrix-operations | ICE/KR mechanics, O/E, expected live there |
| Two coolers, compare pixels | confirm bin tables byte-identical | different contigs/order shift every bin_id |
| scHi-C many cells | `cooler.create_scool` (`.scool`) -> single-cell | shared bin table; per-cell pixels |

## Load a Cooler and Select a Resolution

```python
import cooler

cooler.fileops.list_coolers('matrix.mcool')                      # e.g. ['/resolutions/1000', '/resolutions/10000', ...]
clr = cooler.Cooler('matrix.mcool::/resolutions/10000')          # single-resolution URI, never the bare .mcool
clr.binsize, clr.chromnames, clr.info['sum']                     # info is unvalidated metadata, not a guarantee
'weight' in clr.bins().columns                                   # is this resolution balanced?
```

`clr.matrix().fetch(region)` takes a UCSC region string or a bare chrom name; one arg -> symmetric square, two args -> rectangular submatrix (incl. trans). `clr.bins().fetch('chr1')`, `clr.pixels().fetch(region)` slice the tables.

## Fetch Balanced vs Raw Pixels

**Goal:** Pull a chromosome submatrix as a dense array, correctly balanced.

**Approach:** Confirm the file carries a `weight` column, then `matrix(balance=True)`; on a balanced file, all-NaN rows are masked low-coverage bins (correct), not a bug. For Juicer-imported KR/VC/VC_SQRT weights, name them correctly and the divisive auto-rule fires; force it with `divisive_weights=` only if a custom column is misnamed.

```python
balanced = clr.matrix(balance=True).fetch('chr1')                # multiplicative cooler weight
raw = clr.matrix(balance=False).fetch('chr1')                    # observed counts
kr = clr.matrix(balance='KR').fetch('chr1')                      # KR/VC/VC_SQRT auto-treated as divisive by name
sparse = clr.matrix(balance=True, sparse=True).fetch('chr1')     # scipy COO for large chromosomes
```

## Convert .hic to cooler (and Back)

```bash
hic2cool convert in.hic out.mcool -r 0                           # -r 0 = all resolutions -> .mcool; norm vectors un-inverted (>=0.5.0)
hic2cool convert in.hic out.cool -r 10000                        # single resolution -> .cool
hic2cool extract-norms in.hic out.mcool                          # add Juicer norm vectors to an existing matching cooler
hictk convert in.hic out.mcool                                   # fast C++ path; --resolutions to subset (single -> .cool)
hictk convert in.mcool out.hic                                   # cooler -> .hic v9 ONLY; drops asymmetric/extra columns
```

Neither converter reads/writes FRAG-binned matrices; a FRAG `.hic` yields only its BP resolutions. Record the hic2cool version: the 0.5.0 inversion boundary changes weight values.

## Build a Cooler from a Matrix (Vectorized)

**Goal:** Turn an in-memory numpy contact matrix into a cooler without a hand-rolled O(n^2) loop.

**Approach:** Binnify the chromsizes, take only the upper triangle (cooler stores `symmetric_upper`), pull the nonzero coordinates with a single vectorized `np.triu` + `np.nonzero`, and assemble the pixel DataFrame in one shot.

```python
import cooler
import bioframe
import numpy as np
import pandas as pd

chromsizes = bioframe.fetch_chromsizes('hg38')                   # pin the assembly + chrom naming up front
bins = cooler.binnify(chromsizes, 10000)                         # 10kb bins; bin table identity defines pixel comparability

upper = np.triu(matrix)                                          # cooler stores the upper triangle only
i, j = np.nonzero(upper)                                         # vectorized; never loop over all bin pairs
pixels = pd.DataFrame({'bin1_id': i, 'bin2_id': j, 'count': upper[i, j]})
cooler.create_cooler('new.cool', bins, pixels, assembly='hg38', symmetric_upper=True)
```

For pairs, prefer the CLI: `cooler cload pairs -c1 2 -p1 3 -c2 4 -p2 5 chromsizes.txt:10000 in.pairs out.cool` (the pairs must already be flipped/deduped -> contact-pairs).

## Coarsen Correctly (Sum Raw, Re-balance Per Resolution)

**Goal:** Produce a lower-resolution or multi-resolution file whose weights are valid.

**Approach:** Coarsen the RAW counts then re-run ICE at each new resolution; `zoomify` does exactly this. Never sum balanced pixels -- weights are resolution-specific and summed balanced values are silently wrong.

```python
cooler.zoomify_cooler('hires.cool', 'out.mcool', resolutions=[10000, 50000, 100000, 500000], chunksize=10_000_000)
cooler.coarsen_cooler('hires.cool', 'lowres.cool', factor=5, chunksize=10_000_000)   # raw sum; re-balance after
```

```bash
cooler zoomify -r 10000,50000,100000,500000 --balance hires.cool   # raw-coarsen then ICE afresh per level
```

## Export, Merge, and Inspect

```python
cooler.merge_coolers('merged.cool', ['rep1.cool', 'rep2.cool'], mergebuf=20_000_000)   # bin tables MUST match
np.save('chr1.npy', clr.matrix(balance=True).fetch('chr1'))
```

```bash
cooler dump -t pixels --join --balanced in.cool > pixels.tsv      # --balanced requires a balanced file
cooler dump -t bins in.cool > bins.tsv
cooler info in.cool ; cooler ls -l in.mcool
```

## Reference, Blacklist, and Chrom-Naming Provenance

The bin table IS the identity of a cooler. Two coolers are pixel-comparable only if their bin tables are byte-identical: same chroms, same order, same contigs present, same binsize. Dropping `chrM`/scaffolds in one pipeline shifts every `bin_id` and makes pixel comparison nonsense. `chr1` (UCSC) vs `1` (Ensembl) silently zeros every cross-tool join and `fetch('1')` on a `chr`-named file returns nothing with no error -- harmonize naming (and the assembly) across the cooler, the genome FASTA, any phasing/annotation track, and any blacklist BED (genome-intervals/bed-file-basics). `info['genome-assembly']` is unvalidated metadata, not a checksum. The `.pairs` `#chromsize` header ORDER defines the upper-triangle convention and the cooler's `assembly`/chromsizes must match the order used to flip the pairs upstream (contact-pairs), or bin assignment and the triangle disagree.

## Multi-Way and Single-Cell Contacts (Decompose or Defer)

Standard Hi-C is pairwise. Multi-way assays (Pore-C, SPRITE, GAM) record higher-order co-occurrence; the common path is to DECOMPOSE concatemers into pairwise contacts and store them in a normal cooler, deferring true multi-way analysis to assay-specific tools rather than forcing it into the COO model. For single-cell Hi-C, `.scool` shares one bin table across `/cells/<name>/pixels` (`cooler.create_scool`); per-cell sparsity and imputation are a distinct world -> single-cell/scatac-analysis for the single-cell chromatin context.

## Per-Method Failure Modes

### Bare .mcool passed where a single resolution is required
**Trigger:** `cooler.Cooler('f.mcool')` or a cooltools call on the bare `.mcool`. **Mechanism:** an `.mcool` is a group of resolutions, not one matrix. **Symptom:** KeyError, wrong/aggregate resolution, or a tool error. **Fix:** use `f.mcool::/resolutions/<bp>`; list with `cooler.fileops.list_coolers`.

### KR/VC norm imported under the name `weight`
**Trigger:** renaming a divisive Juicer norm to `weight`. **Mechanism:** `divisive_weights=None` treats only KR/VC/VC_SQRT as divisive; `weight` is multiplicative. **Symptom:** balanced values are wrong, no error. **Fix:** keep the original KR/VC/VC_SQRT name, or pass `divisive_weights=True` explicitly.

### hic2cool version mismatch across coolers
**Trigger:** two coolers from one `.hic` made by hic2cool <0.5.0 and >=0.5.0. **Mechanism:** pre-0.5.0 inverted norms to multiplicative; >=0.5.0 keeps them divisive. **Symptom:** the same norm gives different balanced values. **Fix:** regenerate both with one version; record the version in provenance.

### Summed balanced pixels to coarsen
**Trigger:** building a coarse balanced matrix by summing finer balanced values. **Mechanism:** balancing weights are resolution-specific. **Symptom:** plausible-looking but wrong coarse values. **Fix:** sum RAW then re-ICE per resolution (`cooler zoomify --balance`).

### all-NaN balanced matrix
**Trigger:** `matrix(balance=True)` raises or returns all NaN. **Mechanism:** an unbalanced file has no `weight`; or those bins were masked during balancing. **Symptom:** error (unbalanced) or NaN rows/cols (masked). **Fix:** balance first (`cooler balance` / `balance_cooler(..., store=True)`); accept masked-bin NaNs as correct.

### FRAG `.hic` "lost resolution" after conversion
**Trigger:** converting a FRAG-binned `.hic`. **Mechanism:** cooler/hictk/hic2cool have no FRAG concept. **Symptom:** only BP resolutions appear; FRAG matrix missing. **Fix:** re-bin in BP from the pairs.

### chrom-naming mismatch
**Trigger:** cooler is `chr1`, a track/blacklist is `1` (or vice versa). **Mechanism:** chrom names never match. **Symptom:** empty `fetch`, zero overlap, no error. **Fix:** harmonize naming across cooler, FASTA, tracks, blacklist.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| hic2cool >= 0.5.0 (un-inverted norms) | hic2cool README | the 0.5.0 boundary flips divisive-vs-multiplicative storage; pin it |
| Cooler weight named KR/VC/VC_SQRT -> divisive | cooler `divisive_weights` rule | only these names auto-trigger divisive; all else multiplicative |
| `ignore_diags=2` (balance default) | `cooler.balance_cooler` default | drop the main + first diagonal (self/near-diagonal artifacts) before ICE |
| `mad_max=5` (balance default) | `cooler.balance_cooler` default | mask bins >5 MAD from the median coverage marginal |
| `min_nnz=10` (balance default) | `cooler.balance_cooler` default | mask sparse bins with <10 nonzero pixels |
| mcool resolution ladder = integer multiples of base | HiGlass tiling | non-integer-multiple levels break tile aggregation; 4DN uses a nice-number series |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| `clr.matrix(balance=True)` raises / all NaN | unbalanced file, or masked bins | balance first; masked-bin NaN is expected |
| Empty / wrong-resolution result on `.mcool` | bare `.mcool` passed | use `f.mcool::/resolutions/<bp>` |
| Balanced values look wrong, no error | KR/VC norm renamed to `weight` (treated multiplicative) | keep KR/VC/VC_SQRT name or set `divisive_weights=True` |
| Two coolers from one `.hic` disagree | hic2cool 0.5.0 inversion boundary | regenerate with one version; record it |
| `fetch('1')` returns nothing | chr1-vs-1 naming mismatch | harmonize chrom naming across all inputs |
| FRAG resolutions missing after convert | no FRAG concept in cooler | re-bin from pairs in BP |
| Coarse matrix values wrong | summed balanced pixels | sum raw then re-ICE (`zoomify --balance`) |
| `AttributeError` on a cooler function | pre-0.8/0.10 API change | `help(cooler.<fn>)`; `balance_cooler` is keyword-only after `clr` |

## References

- Abdennur N, Mirny LA. 2020. Cooler: scalable storage for Hi-C data and other genomically labeled arrays. *Bioinformatics* 36(1):311-316.
- Open2C, Abdennur N, Abraham S, Fudenberg G, Flyamer IM, Galitsyna AA, et al. 2024. Cooltools: enabling high-resolution Hi-C analysis in Python. *PLoS Comput Biol* 20(5):e1012067.
- Rossini R, Paulsen J. 2024. hictk: blazing fast toolkit to work with .hic and .cool files. *Bioinformatics* 40(7):btae408.
- Durand NC, Shamim MS, Machol I, Rao SSP, Huntley MH, Lander ES, Aiden EL. 2016. Juicer provides a one-click system for analyzing loop-resolution Hi-C experiments. *Cell Syst* 3(1):95-98.
- Imakaev M, Fudenberg G, McCord RP, Naumova N, Goloborodko A, Lajoie BR, Dekker J, Mirny LA. 2012. Iterative correction of Hi-C data reveals hallmarks of chromosome organization. *Nat Methods* 9(10):999-1003.
- Knight PA, Ruiz D. 2013. A fast algorithm for matrix balancing. *IMA J Numer Anal* 33(3):1029-1047.
- Kerpedjiev P, Abdennur N, Lekschas F, et al. 2018. HiGlass: web-based visual exploration and analysis of genome interaction maps. *Genome Biol* 19:125.

## Related Skills

- contact-pairs - Produces the flipped/deduped .pairs that cooler cload bins into a matrix
- matrix-operations - Balancing (ICE/KR), expected, and O/E that operate on the loaded cooler
- hic-visualization - Render the matrices loaded here
- compartment-analysis - Consumes the balanced cooler at compartment resolution
- read-alignment/bwa-alignment - Produces the BAM that pairtools converts to .pairs
- genome-intervals/bed-file-basics - Chrom-naming and BED handling for blacklists/annotation joins
- single-cell/scatac-analysis - Single-cell chromatin context for .scool / scHi-C
<!-- END FILE: hi-c-analysis/hic-data-io/SKILL.md -->

## 子目录：hi-c-analysis/hic-differential

<!-- BEGIN FILE: hi-c-analysis/hic-differential/SKILL.md -->
---
name: bio-hi-c-analysis-hic-differential
description: Compares Hi-C contact maps between conditions across the right scale -- differential bin-pair contacts (multiHiCcompare, diffHic), differential A/B compartments (dcHiC), differential TAD boundaries (delta insulation), and differential loops (diffloop, DiffHiChIP) -- with distance-stratified between-sample normalization, replicate-aware NB-GLM FDR, HiCRep SCC reproducibility gating, and CNV correction for cancer/aneuploid samples. Use when comparing Hi-C between treatment and control, finding differential contacts/compartments/boundaries/loops, normalizing two maps of unequal depth, choosing a replicate-aware test, gating replicates with SCC, or correcting copy-number artifacts before a tumor-vs-normal comparison.
tool_type: python
primary_tool: cooltools
---

## Version Compatibility

Reference examples tested with: cooler 0.10+, cooltools 0.7+, bioframe 0.7+, multiHiCcompare 1.20+, diffHic 1.34+, dcHiC (2022 release), hicrep (Bioconductor) 1.26+, edgeR 4.0+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

Note: cooltools provides the Python feature-extraction parts (expected, eigenvectors, insulation, pileups) but NO turnkey two-condition test -- the differential statistics live in R/Bioconductor (multiHiCcompare, diffHic, dcHiC, hicrep). The `get.scc` signature changed between the TaoYang-dev and current Bioconductor/qunhualilab releases; verify with `?get.scc` before calling. A `.mcool` is multi-resolution: pass a single-resolution URI (`file.mcool::/resolutions/10000`), not the bare file.

# Hi-C Differential Analysis

**"What changed in 3D genome organization between my conditions?"** -> Equalize the two maps with a distance-stratified between-sample normalization, then test at the SCALE of the question (compartment, TAD boundary, loop, or bin-pair) with a replicate-aware method, not pixel-wise log2 subtraction.
- Python (features): `cooltools.expected_cis(clr)`, `cooltools.eigs_cis(clr)`, `cooltools.insulation(clr)`
- R (bin-pair test): `make_hicexp(...) |> cyclic_loess() |> hic_exactTest() |> results()` (multiHiCcompare)
- R (compartments): `Rscript dchicf.r --pcatype cis|select|analyze` (dcHiC)

## The Single Most Important Modern Insight -- balancing makes a matrix self-consistent, NOT cross-comparable

ICE/KR/SCALE balancing equalizes the marginals WITHIN one map (it removes per-bin visibility bias). It says nothing about whether map A and map B are on the same footing. Two balanced maps still differ in (a) total sequencing depth and (b) cis/trans ratio, and a naive `log2(A/B)` is dominated by those two nuisances plus the shared distance-decay P(s) -- with biology buried underneath. "I balanced both, so I can subtract them" is the single most common error in differential Hi-C. The fix is a BETWEEN-sample, DISTANCE-STRATIFIED normalization (multiHiCcompare's cyclic loess on the M-D plot, or diffHic's trended loess offsets) before any difference is interpretable.

The M-D plot is the RNA-seq MA-plot's distance-aware cousin: M = log2(IF1/IF2), but plotted against genomic DISTANCE D instead of mean abundance. The loess fit is done PER distance stratum because both bias and variance depend on distance -- a sparser library loses long-range pairs faster, so the depth bias is itself distance-dependent and a single global size-factor cannot fix it. After normalization M should center on 0 at every D; a residual M-trend at large D means normalization failed at long range. Inspect `MD_hicexp()` -- do not trust the call set blind.

## Differential-Method Taxonomy (scale-matched -- one tool cannot do all four)

| Method | Scale / object | Mechanism | Replicates | When |
|--------|----------------|-----------|------------|------|
| multiHiCcompare | bin-pair contacts | cyclic-loess M-D normalization + edgeR exactTest/GLM | >=2 for FDR | multi-group, joint normalization, covariates |
| diffHic | bin-pair contacts | squareCounts -> trended/CNV loess offsets -> edgeR NB-GLM | >=2 (required) | replicate-rich, CNV correction, full edgeR machinery |
| dcHiC | A/B compartment (Mb) | sign/PC-consistent eigenvectors -> quantile-norm -> Mahalanobis | works at 1, better with reps | quantitative compartment SHIFTS across samples |
| delta insulation | TAD boundary (sub-Mb) | difference of Crane-style insulation scores per condition | reps for significance | boundary strengthening/loss, not bin-pair counts |
| diffloop / DiffHiChIP | loops (anchored) | edgeR NB on anchored counts; IHW by distance (DiffHiChIP) | YES for FDR | Hi-C/HiChIP/ChIA-PET loop sets, long-range power |
| Selfish | regions (n=1) | Gaussian-pyramid self-similarity, distance-controlled | none (descriptive) | replicate-poor 2-map ranking, no honest FDR |
| FIND | bin-pair (n=1) | spatial Poisson process over the 2D neighborhood | none (descriptive) | neighborhood-aware 2-map ranking |
| HiCRep SCC | whole-matrix similarity | stratum-adjusted correlation (NOT a per-feature test) | n/a (pairwise) | replicate QC gate + coarse condition distance |

Using a bin-pair tool (multiHiCcompare/diffHic) to "find compartment changes" is a category error: compartments are an eigenvector property of the whole chromosome, not a sum of independent bin-pairs, so the result is a noisy bin-pair list, not coherent compartment calls. Match the tool to the scale of the question.

## Decision Tree by Scenario

| Scenario | Recommended | Why |
|----------|-------------|-----|
| First question for any comparison | HiCRep SCC (within- vs between-condition) | gate reproducibility before any call |
| Differential contacts, >=2 reps/condition | multiHiCcompare (cyclic_loess + edgeR) or diffHic | distance-stratified norm + replicate-aware FDR |
| Differential contacts, n=1 vs n=1 | Selfish or FIND, DESCRIPTIVE only | no replicates -> no honest FDR |
| Differential A/B compartments | dcHiC (cis -> select -> analyze) | sign-consistent eigenvectors + Mahalanobis shifts |
| Differential TAD boundaries | delta insulation (cooltools insulation per condition) -> stats | boundaries are local insulation depth, not counts |
| Differential loops (Hi-C) | diffloop or DiffHiChIP on per-condition loop calls | anchored count test with distance modeling |
| Differential loops (HiChIP / PLAC) | -> hichip-plac-loops then DiffHiChIP | peak-biased data needs anchored null |
| Tumor vs normal / aneuploid | CNV-correct FIRST (diffHic normalizeCNV / OneD) | CNV masquerades as differential contacts |
| Two maps, unequal depth, quick look | downsample to equal valid pairs, then M-D normalize | depth fix only; still distance-stratify |
| Call the per-condition features in Python | -> compartment-analysis, tad-detection, loop-calling | cooltools extracts; bring to R for the test |
| Annotate the differential anchors/boundaries | -> chip-seq/peak-annotation, genome-intervals/overlap-significance | overlap with TF peaks / enrichment test |

## Replicate QC Gate with HiCRep SCC (do this FIRST)

**Goal:** Decide whether replicates are reproducible enough that a differential call is meaningful at all.

**Approach:** Plain Pearson on Hi-C always looks reproducible -- the shared P(s) decay alone drives r > 0.9 even between unrelated maps. HiCRep's SCC stratifies by distance (removing the decay) and smooths for sparsity, then variance-weights the strata. Compute SCC for within-condition replicate pairs and between-condition pairs; within must clearly exceed between or there is nothing to call.

```r
library(hicrep)

# Current Bioconductor/qunhualilab interface: dat is a 4-column table
# (mid1, mid2, IF_A, IF_B); resol = bin size; max = max distance considered.
# Verify with ?get.scc -- the older TaoYang-dev interface is get.scc(mat1, mat2, resol, h, lbr, ubr).
scc_out <- get.scc(dat_repA_vs_repB, resol = 50000, max = 5000000)
scc_out$scc   # stratum-adjusted correlation coefficient in [-1, 1]
```

A differential claim is only meaningful when within-condition SCC clearly exceeds between-condition SCC. If they overlap, the "differential" signal is replicate noise.

## Differential Bin-Pair Contacts with multiHiCcompare

**Goal:** Find individual bin-pairs whose contact frequency changes between conditions, with a calibrated FDR from replicate variance.

**Approach:** Build a Hi-C experiment from per-replicate sparse upper-triangular tables, normalize jointly across all samples with cyclic loess on the M-D plot, then run edgeR's exact test (2 groups) or GLM (covariates). Filtering on mean abundance happens at `make_hicexp` time -- it is independent of the contrast, so it shrinks the multiple-testing burden without inflating FDR.

```r
library(multiHiCcompare)

# Each replicate is a 4-column sparse table: chr, region1(bp), region2(bp), IF
# chr coded 1-22, 23=X, 24=Y.
hicexp <- make_hicexp(c1_r1, c1_r2, c2_r1, c2_r2,
                      groups = c(0, 0, 1, 1),
                      zero.p = 0.8,                 # drop bin-pairs >80% zero across samples
                      A.min  = 5,                   # drop bin-pairs with low mean IF (independent filter)
                      filter = TRUE,
                      remove.regions = hg19_cyto)   # blacklist centromeres/telomeres
hicexp <- cyclic_loess(hicexp, span = NA)           # span=NA -> GCV chooses the loess span
hicexp <- hic_exactTest(hicexp)                     # 2-group; use hic_glm(hicexp, design) for covariates
res <- results(hicexp)                              # chr, region1, region2, D, logFC, logCPM, p.value, p.adj
sig <- topDirs(hicexp, logfc_cutoff = 1, logcpm_cutoff = 1, p.adj_cutoff = 0.1, return_df = 'pairedbed')
MD_hicexp(hicexp)                                   # diagnostic: M should center on 0 at every D
```

diffHic is the alternative when full edgeR control is wanted: `squareCounts` -> `filterDirect` -> `normOffsets(type='loess')` -> `asDGEList` -> `estimateDisp` -> `glmQLFit` -> `glmQLFTest`. Same NB-GLM engine as edgeR/csaw; requires biological replicates for dispersion.

## Differential A/B Compartments with dcHiC

**Goal:** Detect compartment changes between conditions, including graded shifts that never cross the A/B boundary, with cross-sample-comparable eigenvectors.

**Approach:** Everyone computes PC1, but PC1's sign is arbitrary per chromosome per sample and sometimes the compartment signal is in PC2 -- naive multi-sample comparison silently compares flipped or mismatched axes. dcHiC anchors the sign (GC/gene-density) and selects the correct PC, quantile-normalizes the scores, then uses a multivariate Mahalanobis distance per bin to flag outliers across all samples. Run as a staged CLI; the input file lists `<matrix> <bed> <replicate_prefix> <experiment_prefix>` per replicate (no dashes/dots in prefixes).

```bash
# Staged CLI (dchicf.r). cis = per-sample compartments; select = pick PC per chr;
# analyze = differential PCA (Mahalanobis); viz = IGV-style browser.
Rscript dchicf.r --file input.txt --pcatype cis    --dirovwt T --cthread 2 --pthread 4
Rscript dchicf.r --file input.txt --pcatype select --dirovwt T --genome hg38
Rscript dchicf.r --file input.txt --pcatype analyze --dirovwt T --diffdir cond1_vs_cond2
Rscript dchicf.r --file input.txt --pcatype viz    --diffdir cond1_vs_cond2 --genome hg38
# Differential calls land in DifferentialResult/<diffdir>/fdr_result/ ; optional: --pcatype subcomp (HMM) and dloop.
```

For a quick Python eyeball of compartment switching (NOT a replicate-aware test -- use dcHiC for that), difference the phased E1 from cooltools per condition and flag sign flips. State it as exploratory.

## Differential TAD Boundaries via Delta Insulation

**Goal:** Find boundaries that strengthen, weaken, or appear/disappear between conditions.

**Approach:** Boundary changes are about local insulation DEPTH, not bin-pair counts, so compute the Crane-style insulation score per condition with cooltools at a fixed window, then difference the scores; attach significance with replicate insulation profiles. The window must match the bin size (typically 5-25x the bin).

```python
import cooltools

ins1 = cooltools.insulation(clr1, window_bp=[200000], ignore_diags=2)   # window ~5-25x bin size
ins2 = cooltools.insulation(clr2, window_bp=[200000], ignore_diags=2)
merged = ins1.merge(ins2, on=['chrom', 'start', 'end'], suffixes=('_1', '_2'))
merged['delta_insulation'] = merged['log2_insulation_score_200000_2'] - merged['log2_insulation_score_200000_1']
```

GENOVA and FAN-C also compute the insulation score for differencing; significance is added separately (paired test across replicate insulation tracks).

## CNV Correction Before Cancer Comparisons

**Goal:** Avoid calling copy-number differences as 3D-structure differences in tumor-vs-normal data.

**Approach:** Contact count scales with copy number, and balancing assumes equal visibility -- so ICE on aneuploid data SHIFTS contacts between amplified and deleted regions instead of removing the artifact, lighting up enormous spurious "differential interaction" blocks. Either regress out the marginal (1D) coverage log-ratio as a covariate (diffHic `marginCounts` + `normalizeCNV`, or OneD's 1D GAM), OR call CNV first (HiNT/HiCnv) and interpret rearrangement blocks separately. Never run vanilla balanced-matrix differential on cancer data.

```r
library(diffHic)

margins <- marginCounts(data)              # 1D marginal coverage per bin (a RangedSummarizedExperiment)
nb.off  <- normalizeCNV(data, margins)     # 2D loess on (abundance, marginal log-ratio) -> GLM offsets; matches margins internally
y <- asDGEList(data)
y$offset <- nb.off                         # attach the CNV offsets; asDGEList does not carry them automatically
# then estimateDisp -> glmQLFit -> glmQLFTest as usual
```

## Per-Method Failure Modes

### Naive log2 of two balanced maps
**Trigger:** `log2((mat2+1)/(mat1+1))` on two balanced coolers of different depth. **Mechanism:** balancing is within-map only; depth + cis/trans + P(s) differences dominate. **Symptom:** a smooth distance-dependent gradient in the "differential" map, strongest off-diagonal. **Fix:** distance-stratified between-sample normalization (multiHiCcompare cyclic_loess / diffHic loess offsets) before differencing.

### Pooling distances into one FDR
**Trigger:** one BH correction over all bin-pairs regardless of distance. **Mechanism:** counts and variance span 2-3 orders of magnitude across distance; short-range is high-count/low-variance, long-range is sparse. **Symptom:** almost all hits are short-range; >500 kb changes vanish. **Fix:** distance-stratified testing; IHW weighting by distance (DiffHiChIP) recovers long-range loops.

### No-replicate FDR
**Trigger:** n=1 vs n=1 reported with a p-value/FDR. **Mechanism:** dispersion needs within-condition variability; with n=1 there is none, so any FDR is fabricated. **Symptom:** thousands of "significant" hits that do not replicate. **Fix:** n>=2 (ideally 3) + diffHic/multiHiCcompare; for n=1 use Selfish/FIND DESCRIPTIVELY only.

### Plain Pearson "reproducibility"
**Trigger:** reporting raw matrix Pearson/Spearman as a QC number. **Mechanism:** shared P(s) decay inflates r > 0.9 even between unrelated maps. **Symptom:** everything looks reproducible, including failed libraries. **Fix:** HiCRep SCC (stratum-adjusted); compare within- vs between-condition.

### CNV read as structure
**Trigger:** tumor-vs-normal on vanilla balanced matrices. **Mechanism:** count scales with copy number; balancing worsens it by shifting contacts. **Symptom:** huge block-shaped "differential" regions aligned to known CNVs. **Fix:** CNV-correct (diffHic normalizeCNV / OneD) or call CNV first and interpret separately.

### Wrong scale for the question
**Trigger:** a bin-pair tool used to find "compartment changes". **Mechanism:** compartments are a whole-chromosome eigenvector property, not a sum of bin-pairs. **Symptom:** a scattered bin-pair list with no coherent A/B structure. **Fix:** dcHiC for compartments; delta insulation for boundaries; diffloop for loops.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| Replicates n>=2 (ideally 3) per condition | NB dispersion estimation | within-condition variance is required for an honest FDR |
| Within-condition SCC > between-condition SCC | replicate QC gate | if they overlap, "differential" signal is replicate noise |
| `zero.p = 0.8` (drop >80% zero) | multiHiCcompare default | sparse long-range pairs break NB and waste FDR budget |
| `A.min = 5` mean-IF filter | multiHiCcompare independent filter | filter independent of contrast preserves FDR validity |
| Bin-pair / loop FDR <= 0.1 | genome-wide multiple testing | millions of bin-pairs need FDR control, not raw p |
| Long-range threshold ~500 kb | DiffHiChIP 2025 benchmark | distance-aware IHW recovers >500 kb loops flat tests miss |
| Insulation window 5-25x bin size | insulation-score scale | window much smaller than this is noisy; much larger blurs boundaries |
| Compartment resolution 100kb-1Mb | compartment scale | A/B is chromosome-scale; finer bins mix in TAD/loop structure |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| Differential map is a smooth distance gradient | naive log2 of balanced maps, no between-sample norm | cyclic_loess / diffHic loess offsets first |
| All hits short-range, no long-range | distances pooled into one FDR | distance-stratified test; IHW by distance |
| Thousands of "significant" n=1 hits | no replicates -> no real dispersion | n>=2; Selfish/FIND descriptive for n=1 |
| Block-shaped diff regions over known CNVs | CNV not corrected on cancer data | diffHic normalizeCNV / OneD before testing |
| `get.scc` argument error | TaoYang-dev vs Bioconductor signature skew | `?get.scc`; 4-col `dat` + `resol` + `max` (current) |
| dcHiC fails on prefixes | dashes/dots in replicate/experiment names | use underscores only in prefix columns |
| Compartment call is sign-scrambled | comparing raw PC1 across samples | dcHiC anchors sign + selects the right PC |
| Empty cooltools result | chrom naming mismatch (`chr1` vs `1`) | harmonize names across cooler, fasta, tracks |

## References

- Stansfield JC, Cresswell KG, Dozmorov MG. 2019. multiHiCcompare: joint normalization and comparative analysis of complex Hi-C experiments. *Bioinformatics* 35(17):2916-2923. doi:10.1093/bioinformatics/bty950
- Stansfield JC, Cresswell KG, Vladimirov VI, Dozmorov MG. 2018. HiCcompare: an R-package for joint normalization and comparison of HI-C datasets. *BMC Bioinformatics* 19:279. doi:10.1186/s12859-018-2288-x
- Lun ATL, Smyth GK. 2015. diffHic: a Bioconductor package to detect differential genomic interactions in Hi-C data. *BMC Bioinformatics* 16:258. doi:10.1186/s12859-015-0683-0
- Chakraborty A, Wang JG, Ay F. 2022. dcHiC detects differential compartments across multiple Hi-C datasets. *Nat Commun* 13:6827. doi:10.1038/s41467-022-34626-6
- Roayaei Ardakany A, Ay F, Lonardi S. 2019. Selfish: discovery of differential chromatin interactions via a self-similarity measure. *Bioinformatics* 35(14):i145-i153. doi:10.1093/bioinformatics/btz362
- Djekidel MN, Chen Y, Zhang MQ. 2018. FIND: difFerential chromatin INteractions Detection using a spatial Poisson process. *Genome Res* 28(3):412-422. doi:10.1101/gr.212266.116
- Lareau CA, Aryee MJ. 2018. diffloop: a computational framework for identifying and analyzing differential DNA loops from sequencing data. *Bioinformatics* 34(4):672-674. doi:10.1093/bioinformatics/btx623
- Bhattacharyya S, Salgado Figueroa D, Georgopoulos K, Ay F. 2025. DiffHiChIP: identifying differential chromatin contacts from HiChIP data. *Cell Rep Methods* 5(11):101214. doi:10.1016/j.crmeth.2025.101214
- Yang T, Zhang F, Yardimci GG, Song F, Hardison RC, Noble WS, Yue F, Li Q. 2017. HiCRep: assessing the reproducibility of Hi-C data using a stratum-adjusted correlation coefficient. *Genome Res* 27(11):1939-1949. doi:10.1101/gr.220640.117
- Vidal E, le Dily F, Quilez J, Stadhouders R, Cuartero Y, Graf T, Marti-Renom MA, Beato M, Filion GJ. 2018. OneD: increasing reproducibility of Hi-C samples with abnormal karyotypes. *Nucleic Acids Res* 46(8):e49. doi:10.1093/nar/gky064
- Imakaev M, Fudenberg G, McCord RP, Naumova N, Goloborodko A, Lajoie BR, Dekker J, Mirny LA. 2012. Iterative correction of Hi-C data reveals hallmarks of chromosome organization. *Nat Methods* 9:999-1003. doi:10.1038/nmeth.2148
- Open2C, Abdennur N, et al. 2024. Cooltools: enabling high-resolution Hi-C analysis in Python. *PLoS Comput Biol* 20(5):e1012067. doi:10.1371/journal.pcbi.1012067

## Related Skills

- compartment-analysis - Per-condition A/B eigenvectors that dcHiC differences
- tad-detection - Per-condition insulation scores for delta-insulation boundary tests
- loop-calling - Per-condition loop calls fed to diffloop/DiffHiChIP
- matrix-operations - Balancing and expected/O-E that precede any comparison
- hichip-plac-loops - Peak-anchored loop calls and DiffHiChIP for HiChIP/PLAC-seq
- hic-data-io - Load and convert the cooler files this skill compares
- hic-visualization - Render differential maps and split-view comparisons
- chip-seq/peak-annotation - Annotate differential anchors/boundaries with TF peaks
- genome-intervals/overlap-significance - Permutation test for differential-feature enrichment
- differential-expression/de-results - The edgeR/FDR mental model reused here (MA-plot, independent filtering, IHW)
<!-- END FILE: hi-c-analysis/hic-differential/SKILL.md -->

## 子目录：hi-c-analysis/hic-visualization

<!-- BEGIN FILE: hi-c-analysis/hic-visualization/SKILL.md -->
---
name: bio-hi-c-analysis-hic-visualization
description: Renders Hi-C contact matrices honestly and reproducibly with matplotlib, cooltools, HiCExplorer, pyGenomeTracks, FAN-C, CoolBox, and plotgardener. Covers the raw/ICE-balanced/observed-over-expected transform choice, LogNorm vs symmetric-diverging colormaps with vmax/percentile clipping, resolution-to-feature matching (compartments 100-500kb, TADs 10-40kb, loops 5-10kb), square vs rotated-triangle track-stacking, NaN/white-stripe handling, virtual 4C, APA/saddle/on-diagonal pileups, two-condition side-by-side and log2-ratio maps, and interactive (HiGlass) vs scripted-static publication figures. Use when plotting a contact matrix, choosing a normalization or color scale, building a multi-track Hi-C figure, making a virtual 4C profile, piling up loops/boundaries, or comparing two conditions.
tool_type: python
primary_tool: matplotlib
---

## Version Compatibility

Reference examples tested with: cooler 0.10+, cooltools 0.7+, matplotlib 3.8+, bioframe 0.7+, HiCExplorer 3.7+, pyGenomeTracks 3.9+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

Notes specific to this skill: `.mcool` is multi-resolution -- pass a single-resolution URI (`file.mcool::/resolutions/10000`), never the bare path. A cooler must be balanced (`cooler balance`) before `matrix(balance=True)` returns anything but NaN. `cooltools.pileup` returns a stack of shape `(n_features, D, D)` -- aggregate over `axis=0`. cooltools standardised on `view_df`/`expected_df` arguments around 0.7+; verify with `help(cooltools.pileup)` before chaining.

# Hi-C Visualization

**"Plot my Hi-C contact matrix"** -> Choose a transform (raw / ICE-balanced / observed-over-expected), a matched colormap+norm (LogNorm for counts, symmetric-diverging for O/E and ratios), and a resolution that fits the feature; render as a square map or a rotated triangle for track-stacking, with NaN bins shown explicitly.
- Python: `clr.matrix(balance=True).fetch(region)` then `ax.matshow(m, norm=LogNorm(...), cmap='fall')`
- CLI: `hicPlotMatrix --matrix m.cool --region chr1:50-60Mb --log1p --colorMap fall -o out.png`

## The Single Most Important Modern Insight -- The Colorscale Is Where Hi-C Figures Lie

The same matrix under raw / ICE-balanced / observed-over-expected tells three *different biological stories*, and the choice is not cosmetic -- it decides which biology is legible. A balanced map is still dominated by the polymer distance-decay gradient (the bright diagonal falling off as ~P(s)); it shows TADs but washes out compartments and loops. Dividing by the distance-matched expected and taking `log2(O/E)` with a SYMMETRIC diverging cmap (`coolwarm`/`RdBu_r`, `vmin=-vmax`) removes that gradient and makes the compartment checkerboard and loop corner-dots suddenly visible -- they were always in the data. The corollary is a reviewer's reflex: a "no compartments / no loops" claim plotted on a balanced (not O/E) map is unsupportable. A reviewer-grade figure is one that can be reconstructed from the legend -- it states (1) the normalization (raw / ICE-balanced / O/E / log2-ratio), (2) the color scale (LogNorm vs symmetric-diverging) with its limits or clip percentile, and (3) the bin resolution. If those three are absent, the figure is neither interpretable nor reproducible.

## Transform Taxonomy

| Transform | Norm + cmap | What it shows | When |
|-----------|-------------|---------------|------|
| Raw counts | `LogNorm`, sequential (`fall`) | depth + per-bin coverage bias; white stripes are artifacts | QC sanity check only -- almost never the science figure |
| ICE-balanced | `LogNorm` vmin~1e-4..1e-1, `fall` | TADs + the distance-decay gradient; loops/compartments washed out | the honest "raw structure" map; track-stacking context |
| Observed/Expected | `log2`, symmetric `coolwarm`/`RdBu_r`, `vmin=-vmax` | compartment checkerboard + loop corner-dots | compartments, loops, any focal-enrichment claim |
| log2(cond1/cond2) | symmetric `RdBu_r`, `vmin=-vmax`, white=0 | gained/lost contacts | two conditions (balance + depth-match FIRST) |

## Layout Taxonomy

| Layout | Tool | Mechanism | When |
|--------|------|-----------|------|
| Square map | matplotlib `matshow`/`pcolormesh`, FAN-C `HicPlot2D` | symmetric 2D matrix | matrix itself is the result; inter-region rectangle; difference map |
| Rotated triangle | pyGenomeTracks/HiCExplorer `hic_matrix`, FAN-C `HicPlot`, plotgardener `plotHicTriangle`, CoolBox `style='triangular'` | 45deg shear, keep upper half, diagonal on top | STACKING genome-browser tracks below on a shared x-axis |
| Pileup (APA/saddle/on-diagonal) | `cooltools.pileup`/`saddle`, coolpup.py | average snippets over a feature set | the only honest genome-wide claim from sparse data |
| Virtual 4C | one matrix row, FAN-C `HicSlicePlot` | 1D profile from a viewpoint bin | compare against a real 4C anchor |
| Interactive | HiGlass | multires `.mcool` pan/zoom | exploration -- NOT a reproducible figure |

## Decision Tree by Scenario

| Scenario | Recommended | Why |
|----------|-------------|-----|
| Show compartments / loops | `log2(O/E)`, symmetric `coolwarm`, `vmin=-vmax` | balanced map's gradient hides them |
| Show TADs / domains | balanced `LogNorm`, `fall`, 10-40kb | domain insulation lives at sub-Mb scale |
| Matrix + genes + ChIP + insulation stack | -> data-visualization/genome-tracks (pyGenomeTracks `hic_matrix`) | config = reproducible provenance; library does the shear |
| Quantify compartment strength | saddle plot (phase E1 first) -> compartment-analysis | corners give the single strength number |
| Validate a loop SET genome-wide | APA pileup, `log2(O/E)`, symmetric | one loop is invisible; 10k averaged is solid |
| Compare two conditions | side-by-side same-scale OR log2-ratio | balance + depth-match both FIRST |
| Export eigenvector / insulation as a track | -> genome-intervals/bigwig-tracks | bigWig feeds the track stack |
| Explore to find a region/resolution | HiGlass, then reproduce in a scripted tool | interactive != publication |

## Square Contact Map (Balanced, Log-Scaled, NaN Shown)

**Goal:** Render a balanced cis matrix for one region with honest dynamic range and visible masked bins.

**Approach:** Fetch the balanced matrix at a single-resolution URI, set `vmax` from a high off-diagonal percentile (report it), use `LogNorm`, and explicitly color NaN bins with `set_bad` so masked regions read as gray rather than as "zero contact".

```python
import cooler, numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
import cooltools.lib.plotting   # registers the 'fall' cmap; needs matplotlib < 3.9 with cooltools 0.7.x (else use a stock cmap like 'afmhot_r')

clr = cooler.Cooler('matrix.mcool::/resolutions/10000')
region = ('chr1', 50_000_000, 60_000_000)
m = clr.matrix(balance=True).fetch(region)

vmax = np.nanpercentile(m[m > 0], 99.5)   # report this percentile in the legend
cmap = plt.get_cmap('fall').copy(); cmap.set_bad('lightgray')   # NaN bins shown, not white
fig, ax = plt.subplots(figsize=(7, 7))
im = ax.matshow(m, norm=LogNorm(vmin=vmax * 1e-3, vmax=vmax), cmap=cmap)
fig.colorbar(im, ax=ax, fraction=0.046, label='balanced (ICE)')
```

## Observed/Expected Divergent Map

**Goal:** Make the compartment checkerboard and loop corner-dots legible by removing the polymer distance-decay background.

**Approach:** Compute the cis expected with cooltools, fetch the matched-distance expected per pixel, divide observed by expected and take `log2`, then plot with a symmetric diverging cmap centered at 0 -- asymmetric limits move the white midpoint off zero and make neutral regions read as enriched.

```python
import cooltools, bioframe

view_df = bioframe.make_viewframe(clr.chromsizes)
expected = cooltools.expected_cis(clr, view_df=view_df, nproc=4)

chrom = region[0]
exp_by_diag = expected.query('region1 == @chrom')['balanced.avg'].to_numpy()   # expected per genomic separation
m = clr.matrix(balance=True).fetch(region)
i, j = np.indices(m.shape)
oe_mtx = m / exp_by_diag[np.abs(i - j)]   # divide each pixel by its distance-matched expected

v = 2.0   # symmetric clip; |log2(O/E)| up to ~2 is the usual readable range
fig, ax = plt.subplots(figsize=(7, 7))
im = ax.matshow(np.log2(oe_mtx), cmap='coolwarm', vmin=-v, vmax=v)   # vmin=-vmax mandatory
fig.colorbar(im, ax=ax, fraction=0.046, label='log2(obs/exp)')
```

`expected['balanced.avg']` is the per-diagonal expected; indexing it by `|i-j|` broadcasts it to a full per-pixel expected matrix.

## Rotated Triangle for Track-Stacking

**Goal:** Hang the contact map above aligned genome-browser tracks (genes, ChIP, insulation) on a shared x-axis.

**Approach:** Prefer a library that owns the 45deg shear and the `depth` crop -- pyGenomeTracks/HiCExplorer (`file_type = hic_matrix`), FAN-C, plotgardener, or CoolBox -- because hand-rolling the `Affine2D` shear is where `extent`/`aspect` alignment bugs live. The matplotlib reference below is for a single panel; for a real stack, route to data-visualization/genome-tracks.

```bash
# HiCExplorer / pyGenomeTracks: config-driven, reproducible. depth = how far up the diagonal.
# A 2 Mb TAD needs depth >= ~2_000_000 or it is silently truncated.
hicPlotTADs --tracks tracks.ini --region chr1:50000000-60000000 -o stack.png
```

```python
from matplotlib.transforms import Affine2D
# matplotlib single-panel reference: shear the square map onto the diagonal.
t = Affine2D().rotate_deg(45) + ax.transData
im = ax.pcolormesh(np.log2(oe_mtx), cmap='coolwarm', vmin=-v, vmax=v)
im.set_transform(t)
ax.set_ylim(0, m.shape[0])   # crop the depth; the y-axis is genomic SEPARATION, not a 2nd coordinate
```

## Virtual 4C from a Viewpoint

**Goal:** Extract a 1D contact profile from one viewpoint bin to compare against a real 4C experiment.

**Approach:** Take the viewpoint row from the balanced chromosome matrix; the near-cis distance-decay spike swamps distal signal on a linear axis, so plot on log-y (or mask the +/- few bins around the viewpoint) and say which. Cross-condition profiles must be balanced, depth-matched, and on identical y-axes.

```python
res = clr.binsize
vp_bin = (55_000_000 // res) - (50_000_000 // res)   # viewpoint index within the region
profile = clr.matrix(balance=True).fetch(region)[vp_bin, :]
fig, ax = plt.subplots(figsize=(11, 2.5))
ax.semilogy(np.arange(len(profile)) * res / 1e6 + 50, profile)   # log-y: the near-cis spike lies on linear
ax.axvline(55, color='red', ls='--')
```

## APA Pileup over a Loop Set

**Goal:** Validate a loop call set genome-wide by averaging the contact signal centered on every loop's anchor pair.

**Approach:** Pass BEDPE features and the cis expected to `cooltools.pileup` for an observed/expected stack, average over the feature axis (`axis=0`), and plot `log2` with a symmetric cmap; the center pixel is the loop, the APA score is center / a corner-background patch (Rao 2014 lower-left 3x3 convention).

```python
import pandas as pd
loops = pd.read_csv('loops.bedpe', sep='\t')   # chrom1,start1,end1,chrom2,start2,end2
stack = cooltools.pileup(clr, loops, view_df=view_df, expected_df=expected, flank=100_000)
apa = np.nanmean(stack, axis=0)   # stack is (n_features, D, D) -> average over features
c = apa.shape[0] // 2
apa_score = apa[c, c] / np.nanmean(apa[-3:, :3])   # center / lower-left 3x3 background
fig, ax = plt.subplots(figsize=(5, 5))
im = ax.matshow(np.log2(apa), cmap='coolwarm', vmin=-1, vmax=1)
ax.set_title(f'APA score {apa_score:.2f}')
```

For on-diagonal pileups over CTCF sites, strand-orient before averaging (`stack[mask] = stack[mask][:, ::-1, ::-1]` for `-` strand) or convergent/divergent signals cancel. For HiChIP/PLAC-seq anchored loops, route to loop-calling and the peak-anchored pileup conventions there.

## Two-Condition Comparison

**Goal:** Show a contact change between two conditions without it being a depth/coverage artifact.

**Approach:** Both matrices must be ICE-balanced AND depth-matched (downsample the deeper library to equal valid pairs) BEFORE ratioing. Then either side-by-side panels on an IDENTICAL cmap/norm/vmin/vmax/resolution, or a single `log2(cond1/cond2)` divergent map with symmetric limits and white = no change; grey out very-distal noise-amplified bins.

```python
m1 = clr1.matrix(balance=True).fetch(region)
m2 = clr2.matrix(balance=True).fetch(region)   # clr1, clr2 already depth-equalized upstream
ratio = np.log2((m1 + 1e-5) / (m2 + 1e-5))   # pseudocount tames divide-by-small off-diagonal
fig, ax = plt.subplots(figsize=(7, 7))
im = ax.matshow(ratio, cmap='RdBu_r', vmin=-2, vmax=2)   # symmetric, white=no change
fig.colorbar(im, ax=ax, fraction=0.046, label='log2(cond1/cond2)')
```

Quantitative replicate-aware differential testing (not just a figure) lives in hic-differential.

## Per-Method Failure Modes

### Negative claim on a balanced map
**Trigger:** "no compartments/loops" read off a balanced (not O/E) map. **Mechanism:** the polymer distance-decay gradient dominates balanced data and hides checkerboard/dots. **Symptom:** features absent that O/E would reveal. **Fix:** replot as `log2(O/E)` with a symmetric cmap before making any negative claim.

### Asymmetric divergent limits
**Trigger:** `vmin != -vmax` on an O/E or log2-ratio map. **Mechanism:** zero (no change/enrichment) is no longer the white midpoint. **Symptom:** neutral regions read as enriched or depleted; reviewers flag it. **Fix:** `vmin=-v, vmax=v` (or `TwoSlopeNorm(vcenter=0)`).

### vmax = data max
**Trigger:** letting the heavy-tailed diagonal set vmax. **Mechanism:** a few super-bins are orders of magnitude above the bulk. **Symptom:** the whole map looks empty/dark; over-clipping the other way fabricates structure. **Fix:** vmax = a stated high off-diagonal percentile (95th-99.5th).

### Resolution mismatched to feature
**Trigger:** plotting at whatever the `.mcool` defaults to. **Mechanism:** loops at 100kb are averaged away (oversmoothing); compartments at 5-10kb mix in TAD/loop noise. **Symptom:** vanished dots or a noisy checkerboard. **Fix:** compartments 100-500kb, TADs 10-40kb, loops 5-10kb (Micro-C 1-2kb).

### Interpolated matrix quantified
**Trigger:** `interp_nan`/`adaptive_coarsegrain` (or scHi-C smoothing) then measuring on the result. **Mechanism:** interpolation/imputation fabricates contacts for DISPLAY. **Symptom:** a filled centromere looks like contiguous chromatin; "structure" that is the smoother's prior. **Fix:** fill for display only; quantify on the raw/balanced matrix and disclose the smoother.

### Triangle depth too small
**Trigger:** `depth` < the largest feature. **Mechanism:** the triangle crop truncates separations above `depth`. **Symptom:** a 2 Mb TAD silently cut off. **Fix:** set `depth >= ~feature size`; remember the y-axis is genomic separation.

### Unequal-depth ratio
**Trigger:** `log2(cond1/cond2)` on un-depth-matched or unbalanced maps. **Mechanism:** a global depth difference is a uniform multiplicative offset. **Symptom:** a whole-map color shift read as biology. **Fix:** ICE-balance and downsample to equal valid pairs first.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| Compartment resolution 100-500kb | compartment scale (Lieberman-Aiden 2009) | checkerboard is Mb-scale; finer bins add noise, not detail |
| TAD resolution 10-40kb | domain scale (Dixon 2012) | insulation/boundary structure lives at sub-Mb |
| Loop resolution 5-10kb (Micro-C 1-2kb) | focal-contact scale (Rao 2014) | a loop is a ~10kb focal pixel; coarse bins blur it, too-fine buries it in Poisson noise |
| vmax = 95th-99.5th off-diagonal percentile | heavy-tailed counts | data-max vmax leaves the map dark; report the percentile |
| Divergent limits symmetric `vmin=-vmax` | zero must be the midpoint | asymmetric limits misplace the white neutral point |
| APA flank +/- 100kb | corner-background convention | too small contaminates the corner; too large averages in neighbors |
| APA score = center / lower-left 3x3 | Rao 2014 | standard center-to-background loop enrichment ratio |
| HiGlass zoom levels < ~5x apart | Kerpedjiev 2018 | adjacent resolutions must be close for smooth multires rendering |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| `matrix(balance=True)` all NaN | cooler not balanced | run `cooler balance` / `cooler.balance_cooler` first |
| Empty / wrong-resolution result | bare `.mcool` passed | use `file.mcool::/resolutions/<bp>` |
| White stripes mistaken for "no contact" | NaN bins left at default | `cmap.set_bad('lightgray')` to render masked bins |
| `cmap='fall'` KeyError | colormap not registered | `import cooltools.lib.plotting` first |
| `ImportError` on `import cooltools.lib.plotting` | matplotlib >= 3.9 dropped `register_cmap` (cooltools 0.7.x) | pin matplotlib < 3.9, or use a stock cmap (`'afmhot_r'`) |
| Pileup looks averaged-out / scrambled | wrong nanmean axis | aggregate over `axis=0` (stack is `(n_features, D, D)`) |
| Empty region / no overlap | chrom naming (`chr1` vs `1`) | harmonize names across cooler, BED/BEDPE, fasta |
| `AttributeError` on cooltools fn | pre-0.7 vs 0.7+ API | `help(cooltools.<fn>)`; update to the `view_df`/`expected_df` signature |

## References

- cooler: Abdennur N, Mirny LA. Cooler: scalable storage for Hi-C data and other genomically labeled arrays. *Bioinformatics* 2020;36(1):311-316.
- cooltools: Open2C, Abdennur N, Abraham S, Fudenberg G, et al. Cooltools: enabling high-resolution Hi-C analysis in Python. *PLoS Comput Biol* 2024;20(5):e1012067.
- HiCExplorer: Ramirez F, Bhardwaj V, Arrigoni L, et al. High-resolution TADs reveal DNA sequences underlying genome organization in flies. *Nat Commun* 2018;9(1):189.
- pyGenomeTracks: Lopez-Delisle L, Rabbani L, Wolff J, et al. pyGenomeTracks: reproducible plots for multivariate genomic datasets. *Bioinformatics* 2021;37(3):422-423.
- FAN-C: Kruse K, Hug CB, Vaquerizas JM. FAN-C: a feature-rich framework for the analysis and visualisation of chromosome conformation capture data. *Genome Biol* 2020;21(1):303.
- CoolBox: Xu W, Zhong Q, Lin D, et al. CoolBox: a flexible toolkit for visual analysis of genomics data. *BMC Bioinformatics* 2021;22(1):489.
- plotgardener: Kramer NE, Davis ES, Wenger CD, et al. Plotgardener: cultivating precise multi-panel figures in R. *Bioinformatics* 2022;38(7):2042-2045.
- HiGlass: Kerpedjiev P, Abdennur N, Lekschas F, et al. HiGlass: web-based visual exploration and analysis of genome interaction maps. *Genome Biol* 2018;19(1):125.
- coolpup.py: Flyamer IM, Illingworth RS, Bickmore WA. Coolpup.py: versatile pile-up analysis of Hi-C data. *Bioinformatics* 2020;36(10):2980-2985.
- A/B compartments: Lieberman-Aiden E, van Berkum NL, Williams L, et al. Comprehensive mapping of long-range interactions reveals folding principles of the human genome. *Science* 2009;326(5950):289-293.
- TAD directionality index: Dixon JR, Selvaraj S, Yue F, et al. Topological domains in mammalian genomes identified by analysis of chromatin interactions. *Nature* 2012;485(7398):376-380.
- Loops/HiCCUPS/APA: Rao SSP, Huntley MH, Durand NC, et al. A 3D map of the human genome at kilobase resolution reveals principles of chromatin looping. *Cell* 2014;159(7):1665-1680.

## Related Skills

- hic-data-io - Load the cooler/.mcool files and zoomify for multires HiGlass tilesets
- matrix-operations - Balancing and O/E that the divergent map depends on
- compartment-analysis - Eigenvector phasing behind the saddle plot
- tad-detection - Insulation/boundary tracks stacked under the triangle
- loop-calling - Loop calls and peak-anchored pileup conventions visualized here
- hic-differential - Replicate-aware testing behind the two-condition comparison
- data-visualization/genome-tracks - Config-driven multi-track stacks (pyGenomeTracks hic_matrix)
- genome-intervals/bigwig-tracks - Export eigenvector/insulation as bigWig for the track stack
- data-visualization/heatmaps-clustering - General heatmap color/norm conventions
<!-- END FILE: hi-c-analysis/hic-visualization/SKILL.md -->

## 子目录：hi-c-analysis/hichip-plac-loops

<!-- BEGIN FILE: hi-c-analysis/hichip-plac-loops/SKILL.md -->
---
name: bio-hi-c-analysis-hichip-plac-loops
description: Calls significant loops from protein-directed and targeted 3C assays (HiChIP, PLAC-seq, Capture Hi-C/PCHi-C, ChIA-PET) where the contact background is peak-anchored and coverage-biased, so generic Hi-C loop callers (cooltools dots, Juicer HiCCUPS) use the wrong null. Covers FitHiChIP (config-driven coverage+distance-decay spline regression, peak-to-peak vs peak-to-all foreground, loose vs stringent background, coverage vs ICE bias), MAPS (positive Poisson regression on bias factors for PLAC-seq/HiChIP), hichipper (restriction-site-distance bias model + library QC), CHiCAGO (Delaporte two-component Brownian+technical background for asymmetric bait x other-end Capture Hi-C), the with/without separate-ChIP anchor decision, and differential loops via diffloop. Use when calling loops from HiChIP/PLAC-seq/Capture Hi-C, choosing FitHiChIP/MAPS/CHiCAGO, picking peak-to-all vs peak-to-peak, setting the loop FDR, supplying ChIP peaks as anchors, QCing a HiChIP library, or comparing loops between conditions.
tool_type: mixed
primary_tool: fithichip
---

## Version Compatibility

Reference examples tested with: FitHiChIP 11.0+, MAPS 1.1+, hichipper 0.7+, CHiCAGO 1.20+ (Bioconductor 3.18+), HiC-Pro 3.1+, diffloop 1.18+ (Bioconductor 3.18+).

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `<tool> --version` then `<tool> --help` to confirm flags
- FitHiChIP: read the shipped `configfile` comments; parameter names and defaults change between releases
- R: `packageVersion('diffloop')`/`packageVersion('Chicago')` then `?function` to check signatures

FitHiChIP is driven entirely by a key=value config file passed with `-C`; the loop caller, background, and bias model are set there, not on the command line. MAPS, hichipper, and CHiCAGO each expect a specific upstream format (HiC-Pro valid pairs / .allValidPairs, or HiCUP+capture design files for CHiCAGO). If a tool errors, introspect the installed version's config/help and adapt the example rather than retrying.

# Protein-Directed and Targeted 3C Loop Calling

**"My HiChIP/PLAC-seq/Capture Hi-C has loops anchored at CTCF/H3K27ac/promoters - which contacts are real?"** -> Call loops with a method whose null jointly models the per-anchor coverage bias AND the distance-decay, not the uniform/donut background that generic Hi-C callers assume.
- CLI: `bash FitHiChIP_HiCPro.sh -C config_fithichip` (HiChIP/PLAC-seq); edit and run `run_pipeline.sh` (MAPS; it invokes MAPS.py internally) for PLAC-seq/HiChIP
- R: `runChicago(...)` then PIRs at CHiCAGO score >= 5 (Capture Hi-C/PCHi-C); `quickAssoc()`/`loopAssoc()` (diffloop, differential)

## The Single Most Important Modern Insight -- Generic Hi-C Loop Callers Use the Wrong Null on Peak-Anchored Data

Running `cooltools dots` or Juicer HiCCUPS on HiChIP, PLAC-seq, or Capture Hi-C is a documented error, not a shortcut. Those callers test each pixel against a *local, roughly-uniform* expected background (a donut/expected neighborhood) built for a genome-wide-uniform in-situ Hi-C map. Protein-directed and capture assays violate that assumption in the most consequential way possible: the antibody (or oligo capture) **enriches contacts at the factor's binding sites**, so 1D coverage is wildly non-uniform - an H3K27ac anchor can carry 100x the read depth of a flanking non-peak bin. A donut null reads that coverage spike as contact enrichment and calls a "loop" at every peak. The dedicated callers exist precisely to fix this, and they all share one move: **regress out the per-anchor coverage bias before testing the distance-decayed contact frequency.**

Three load-bearing consequences:

1. **The hard part is 3C statistics, and it lives here; the peak-calling half lives in chip-seq.** FitHiChIP/MAPS/CHiCAGO each fit a *significance model* (spline regression on coverage + genomic distance; positive Poisson regression on bias factors; a two-component Brownian+technical background). That model - not the antibody - is the deliverable. Anchor/peak calling (where the protein binds) is chip-seq's job (-> chip-seq/peak-calling); this skill consumes those peaks and produces FDR-controlled loops.

2. **Protein-targeting buys depth efficiency, so loops are called at far lower total depth than Hi-C.** HiChIP/PLAC-seq concentrate reads onto a small anchored sub-space, needing ~5-10 read pairs per interaction versus ~100-1000 for genome-wide Hi-C (Mumbach 2016: >10x more conformation-informative reads, >100x less input than ChIA-PET). A 100-200M-pair HiChIP library calls loops that would need billions of pairs in Hi-C - but only at the protein's anchors, and only with the right null.

3. **"Peaks from the same data" is a circularity trap.** When no separate ChIP-seq exists, HiChIP-derived peaks (hichipper, HiChIP-Peaks) are used as anchors - but calling peaks and loops from the same reads couples the two error structures. Prefer an independent ChIP-seq peak set as the anchor reference when one exists; if not, use a HiChIP-native peak caller and treat anchor confidence as part of the loop's uncertainty, not a given.

## Method Taxonomy

| Tool | Assay | Null / significance model | Anchors | When |
|------|-------|---------------------------|---------|------|
| FitHiChIP | HiChIP, PLAC-seq, (CHi-C, ChIA-PET) | spline regression of contact count on coverage bias AND genomic distance; loose (peak-to-all) vs stringent (peak-to-peak) background; coverage-bias or ICE-bias regression | ChIP/HiChIP peak file | default; recovers Hi-C/CHi-C/ChIA-PET contacts best (Bhattacharyya 2019); config-driven |
| MAPS | PLAC-seq, HiChIP | zero-truncated (positive) Poisson regression removing effective-fragment/GC/mappability AND ChIP-enrichment bias, then test normalized frequency at anchored bins | AND-set vs XOR-set anchored bins | model-based PLAC-seq/HiChIP, 4DN-adopted; two-step (bias model -> significance) |
| hichipper | HiChIP | background read density modeled as a function of proximity to restriction sites; loop strength + confidence per anchor | self-derived (restriction-aware) | restriction-aware QC + loop calling without separate ChIP; feeds diffloop |
| CHiCAGO | Capture Hi-C, PCHi-C | Delaporte two-component background: Brownian (distance-dependent, NB) + technical (distance-independent, Poisson), fit per bait; report PIRs at score >= 5 | baited fragments (asymmetric bait x other-end) | promoter/region-capture; asymmetric design where dots cannot apply |
| HiChIP-Peaks | HiChIP | peak calling from HiChIP signal (not loop calling) | n/a (produces anchors) | when no separate ChIP exists and anchors must come from HiChIP itself |
| diffloop | any loop set (HiChIP/ChIA-PET) | edgeR-style count test on a union loop set across conditions | from the union set | differential looping between conditions (not a caller) |

## Decision Tree by Scenario

| Scenario | Recommended | Why |
|----------|-------------|-----|
| HiChIP/PLAC-seq, have a separate ChIP-seq peak set | FitHiChIP with `PeakFile=` the ChIP peaks | independent anchors break the peak/loop circularity; FitHiChIP is the default |
| PLAC-seq/HiChIP, prefer a regression-model caller | MAPS | positive Poisson regression explicitly removes ChIP-enrichment bias |
| No separate ChIP; need anchors + library QC fast | hichipper (then FitHiChIP/diffloop) | restriction-aware, self-derives anchors, reports library quality |
| Capture Hi-C / Promoter-Capture Hi-C | CHiCAGO, PIRs at score >= 5 | asymmetric bait x other-end; two-component per-bait background |
| H3K27ac/broad anchors, want sensitivity | FitHiChIP loose (peak-to-all) background | most contacts have at least one peak anchor |
| CTCF/cohesin sharp anchors, want specificity | FitHiChIP stringent (peak-to-peak) background | restricts foreground to peak-peak contacts |
| Compare loops between conditions | -> hic-differential context; quantify with diffloop / FitHiChIP DiffAnalysis | union anchors + count test, not pixel subtraction |
| Generic in-situ Hi-C (no protein/capture) | -> loop-calling (cooltools dots / chromosight) | uniform background is correct there; do NOT use it here |
| Anchors not yet called | -> chip-seq/peak-calling | peak calling is chip-seq's competency; this skill consumes peaks |
| Annotate loop anchors with TFs/genes | -> chip-seq/peak-annotation, atac-seq/enhancer-gene-linking | anchor-to-feature assignment lives there |

## FitHiChIP - Coverage + Distance Spline Regression (default)

**Goal:** Call FDR-controlled loops from a HiChIP/PLAC-seq library whose anchors are defined by an (ideally independent) ChIP-seq peak set.

**Approach:** FitHiChIP reads valid pairs (HiC-Pro format), bins them, fits a spline regression of contact count on BOTH the genomic-distance decay and the per-bin coverage bias, then assigns each candidate contact an FDR. Everything - resolution, foreground type, background, bias model, FDR - is set in a key=value config passed with `-C`; the command line itself takes no analysis parameters.

```bash
# config_fithichip (key=value; comments stripped). Run: bash FitHiChIP_HiCPro.sh -C config_fithichip
ValidPairs=sample.allValidPairs.gz   # HiC-Pro valid pairs (or set Matrix=/Interval= for matrix input)
PeakFile=chipseq_peaks.bed           # anchors; prefer an INDEPENDENT ChIP-seq peak set over HiChIP-derived
ChrSizeFile=hg38.chrom.sizes
OutDir=fithichip_out/
PREFIX=sample
BINSIZE=5000                          # 5kb: standard HiChIP anchor resolution (~2.5kb effective, hichipper)
LowDistThr=20000                      # 20kb floor: below this, contacts are dominated by self-ligation/diagonal
UppDistThr=2000000                    # 2Mb ceiling: loops beyond this are rare and noise-dominated
IntType=3                             # 3=peak-to-all (loose foreground); 1=peak-to-peak (stringent)
UseP2PBackgrnd=0                      # 0=loose (peak-to-all) background; 1=stringent (peak-to-peak) background
BiasType=1                            # 1=coverage-bias regression (default); 2=ICE-bias regression
MergeInt=1                            # merge adjacent significant contacts into one loop (recommended)
QVALUE=0.01                           # FDR cutoff for significant loops
```

`IntType` sets the foreground (which candidate contacts are tested); `UseP2PBackgrnd` sets the background the regression is fit against. The two together encode the loose-vs-stringent choice: peak-to-all foreground + loose background maximizes sensitivity for broad marks (H3K27ac); peak-to-peak foreground + stringent background maximizes specificity for sharp factors (CTCF/cohesin). Output significant loops land under a nested `OutDir/FitHiChIP_Peak2ALL_b<bin>_L<low>_U<upp>/P2Pbckgr_<0|1>/.../` tree, in `<PREFIX>.interactions_FitHiC_Q<QVALUE>.bed` (and `..._MergeNearContacts.bed` when `MergeInt=1`); locate it with `find OutDir -name '*interactions_FitHiC_Q*.bed'`.

## MAPS - Positive Poisson Regression on Bias Factors

**Goal:** Call PLAC-seq/HiChIP loops with an explicit regression model that removes both the generic 3C biases and the ChIP-enrichment bias.

**Approach:** MAPS is a two-step pipeline: first fit a zero-truncated (positive) Poisson regression of observed contact counts on effective-fragment length, GC content, mappability, and ChIP-enrichment per bin; then test each anchored bin-pair's count against the model-normalized expectation, controlling FDR. It distinguishes AND anchors (both ends in a peak) from XOR anchors (one end), reflecting the peak-to-peak vs peak-to-all distinction.

```bash
# MAPS is driven by a COPIED run_pipeline.sh with key=value bash variables, not CLI flags.
# Edit run_pipeline_sample.sh, then run it: ./run_pipeline_sample.sh
bin_size=5000                              # 5kb anchor bin
binning_range=1000000                      # max interaction distance modeled
fdr=2                                       # -log10(FDR) cutoff; 2 means FDR <= 0.01
dataset_name='sample'
macs2_filepath='chipseq_peaks.narrowPeak'  # ChIP/HiChIP anchors
organism='hg38'                            # selects the bundled effective-length/GC/mappability bias track
# run_pipeline.sh runs feather (preprocessing) then MAPS.py (positive Poisson regression) internally
```

The model-based design is MAPS's signature: it does not subtract a local background; it predicts each bin-pair's expected count from the bias covariates and flags positive residuals. FitHiChIP and MAPS disagree substantially on the same data (the literature reports tens-of-thousands-loop differences at matched FDR) - the model assumptions differ, so report which caller and its settings.

## CHiCAGO - Two-Component Background for Capture Hi-C

**Goal:** Call significant promoter-interacting regions (PIRs) from Capture Hi-C / PCHi-C, where oligo capture makes the map asymmetric (baited fragment x any other-end).

**Approach:** CHiCAGO fits a per-bait background with two components - a Brownian (distance-dependent, negative-binomial) term and a technical-noise (distance-independent, Poisson) term, convolved as a Delaporte distribution - then scores each bait-other-end pair as a weighted -log p-value; report other-ends above the conventional score threshold.

```r
# Reference: Chicago 1.20+ (Bioconductor 3.18+) | Verify API if version differs
library(Chicago)

CHICAGO_SCORE <- 5   # conventional PIR threshold (Cairns 2016); soft 3-5 grey zone, >=5 = called
cd <- setExperiment(designDir = 'capture_design/')         # baitmap/rmap/NPB/NBaitsPB/proxOE from the capture design
cd <- readAndMerge(files = c('sample_rep1.chinput', 'sample_rep2.chinput'), cd = cd)
cd <- chicagoPipeline(cd)                                  # fits Brownian+technical background, scores all bait x other-end
exportResults(cd, file.path('chicago_out', 'sample'), format = 'washU_text')   # PIRs at score >= CHICAGO_SCORE
```

Neither cooltools dots nor FitHiChIP's symmetric model applies to Capture Hi-C: the bait-vs-other-end asymmetry and the per-bait normalization are the whole point. The capture design files (`baitmap`, `rmap`, and the precomputed `NPB`/`NBaitsPB`/`proxOE` from `makeDesignFiles.py`) encode which fragments were baited and the distance-binned background normalization.

## Differential Loops with diffloop

**Goal:** Find loops that change strength between conditions, given per-condition loop call sets.

**Approach:** Build a UNION loop set across all samples, count the read pairs supporting each loop per replicate, then run an edgeR-style count test on the union set; there is no "DESeq2 for loops," so the union-then-count workflow is the standard.

```r
# Reference: diffloop 1.18+ (Bioconductor 3.18+) | Verify API if version differs
library(diffloop)

loops <- loopsMake(beddir = 'hichipper_loops/')            # reads the hichipper-preprocessed loop directory
loops <- subsetLoops(loops, loops@rowData$loopWidth >= 20000)   # drop sub-20kb (self-ligation regime)
groups <- c('wt', 'wt', 'ko', 'ko')
loops <- updateLDGroups(loops, groups)
res <- quickAssoc(loops)   # two-group edgeR exact test on the union set; loopAssoc(loops, coef=, design=) for a GLM
```

diffloop pairs naturally with hichipper output. FitHiChIP also ships a differential-analysis script (`DiffAnalysisHiChIP.r`); either way the unit of comparison is a union anchor/loop set, not a per-pixel matrix subtraction (-> hic-differential for the matrix-level framing).

## Per-Method Failure Modes

### Generic dots/HiCCUPS on protein-directed data
**Trigger:** running `cooltools dots` or Juicer HiCCUPS on a HiChIP/PLAC-seq/Capture cooler. **Mechanism:** the donut/local-expected null assumes uniform coverage; antibody/capture enrichment spikes coverage at anchors. **Symptom:** a "loop" at essentially every peak; calls that do not reproduce across replicates. **Fix:** use FitHiChIP/MAPS (HiChIP/PLAC-seq) or CHiCAGO (Capture); they regress out coverage bias.

### Anchors and loops from the same reads (circularity)
**Trigger:** HiChIP-derived peaks used as the FitHiChIP `PeakFile` when a separate ChIP-seq exists. **Mechanism:** peak and loop errors share a source, inflating apparent confidence at high-coverage anchors. **Symptom:** loops concentrate at the strongest coverage peaks regardless of biology. **Fix:** anchor on an independent ChIP-seq peak set; reserve HiChIP-native peaks for when no ChIP exists.

### Wrong foreground/background pair for the mark
**Trigger:** stringent peak-to-peak background on a broad H3K27ac library, or loose on sharp CTCF. **Mechanism:** the foreground/background must match the anchor sharpness. **Symptom:** too few loops (over-stringent on broad marks) or noisy excess (over-loose on sharp factors). **Fix:** loose/peak-to-all for broad marks; stringent/peak-to-peak for CTCF/cohesin.

### CHiCAGO design files mismatched to the capture
**Trigger:** baitmap/rmap or precomputed NPB/NBaitsPB/proxOE built for a different fragmentation or bait set. **Mechanism:** the per-bait background normalization depends on the exact capture design. **Symptom:** absurd scores or empty PIR lists. **Fix:** regenerate design files with `makeDesignFiles.py` from the actual rmap/baitmap.

### Short-range contacts not excluded
**Trigger:** `LowDistThr` left at 0 / no distance floor. **Mechanism:** sub-20kb contacts are dominated by the diagonal, self-ligation, and re-ligation, not loops. **Symptom:** a wall of "loops" hugging the diagonal. **Fix:** set a distance floor (FitHiChIP `LowDistThr=20000`; equivalent in MAPS/CHiCAGO).

### Chromosome-name mismatch across inputs
**Trigger:** `chr1` in the valid pairs vs `1` in the peak/chrom-size file. **Mechanism:** anchors silently fail to intersect the contacts. **Symptom:** few or zero loops, no error. **Fix:** harmonize chromosome naming across valid pairs, PeakFile, and ChrSizeFile.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| Loop resolution 5kb (HiChIP) | hichipper effective ~2.5kb (Lareau & Aryee 2018) | standard HiChIP anchor bin; finer needs more depth, coarser blurs anchors |
| Lower distance floor 20kb | FitHiChIP default; self-ligation/diagonal regime | below ~20kb contacts are dominated by religation/dangling/diagonal, not loops |
| Upper distance ceiling 2Mb | FitHiChIP default | loops beyond ~2Mb are rare and noise-dominated at typical HiChIP depth |
| Loop FDR (q) <= 0.01 | FitHiChIP/MAPS default | genome-wide candidate-contact testing needs strict FDR; 0.05 acceptable for discovery |
| CHiCAGO PIR score >= 5 | Cairns 2016 convention | weighted -log p threshold; 3-5 is a soft grey zone, >=5 is called |
| ~5-10 read pairs per interaction | Mumbach 2016 (HiChIP efficiency) | protein-targeting lets loops be called at far lower depth than Hi-C |
| MAPS/FitHiChIP at 5-10kb, ~100-300M valid pairs | HiChIP depth practice | anchored sub-space is small, so usable loop resolution arrives well below Hi-C billions |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| A loop at every peak; no replicate reproducibility | generic dots/HiCCUPS used on HiChIP/capture | switch to FitHiChIP/MAPS/CHiCAGO |
| FitHiChIP runs but finds almost nothing | over-stringent background on a broad mark, or wrong `PeakFile` | use loose/peak-to-all; verify the peak set matches the antibody |
| FitHiChIP `PeakFile`/`ChrSizeFile` error | missing mandatory config key or wrong path | every mandatory key (`PeakFile`, `ChrSizeFile`, `OutDir`) must be set |
| Few/zero loops, no error | chrom-name mismatch (`chr1` vs `1`) across inputs | harmonize naming across valid pairs, peaks, chrom sizes |
| CHiCAGO empty/absurd PIR list | design files mismatched to the capture | regenerate baitmap/rmap + NPB/NBaitsPB/proxOE with `makeDesignFiles.py` |
| diffloop `loopsMake` reads nothing | wrong bedpe directory or per-sample naming | point `beddir` at the per-sample hichipper loop bedpe files |
| Wall of diagonal-hugging loops | no lower distance threshold | set `LowDistThr` (FitHiChIP) / equivalent distance floor |

## References

- Mumbach MR, Rubin AJ, Flynn RA, Dai C, Khavari PA, Greenleaf WJ, Chang HY. 2016. HiChIP: efficient and sensitive analysis of protein-directed genome architecture. *Nat Methods* 13(11):919-922.
- Fang R, Yu M, Li G, Chee S, Liu T, Schmitt AD, Ren B. 2016. Mapping of long-range chromatin interactions by proximity ligation-assisted ChIP-seq. *Cell Res* 26:1345-1348.
- Bhattacharyya S, Chandra V, Vijayanand P, Ay F. 2019. Identification of significant chromatin contacts from HiChIP data by FitHiChIP. *Nat Commun* 10:4221.
- Juric I, Yu M, Abnousi A, Raviram R, Fang R, Zhao Y, Zhang Y, Qiu Y, Hu M, et al. 2019. MAPS: model-based analysis of long-range chromatin interactions from PLAC-seq and HiChIP experiments. *PLoS Comput Biol* 15(4):e1006982.
- Lareau CA, Aryee MJ. 2018. hichipper: a preprocessing pipeline for calling DNA loops from HiChIP data. *Nat Methods* 15:155-156.
- Cairns J, Freire-Pritchett P, Wingett SW, Varnai C, Dimond A, Plagnol V, Zerbino D, Schoenfelder S, Javierre BM, Osborne C, Fraser P, Spivakov M. 2016. CHiCAGO: robust detection of DNA looping interactions in Capture Hi-C data. *Genome Biol* 17:127.
- Lareau CA, Aryee MJ. 2018. diffloop: a computational framework for identifying and analyzing differential DNA loops from sequencing data. *Bioinformatics* 34(4):672-674.

## Related Skills

- loop-calling - The bulk in-situ Hi-C counterpart (cooltools dots / chromosight); correct null there, wrong null here
- hic-differential - Matrix-level condition comparison framing behind differential loops
- contact-pairs - Produces the valid pairs (HiC-Pro / pairtools) these callers consume
- hic-data-io - Cooler handling of the contact maps upstream of anchored loop calling
- chip-seq/peak-calling - Calls the ChIP-seq peaks used as independent loop anchors
- chip-seq/peak-annotation - Annotate loop anchors with TFs/genes
- atac-seq/enhancer-gene-linking - Enhancer-promoter contacts complement HiChIP/PCHi-C loops
- genome-intervals/overlap-significance - Test loop-anchor enrichment at features against a structured null
<!-- END FILE: hi-c-analysis/hichip-plac-loops/SKILL.md -->

## 子目录：hi-c-analysis/loop-calling

<!-- BEGIN FILE: hi-c-analysis/loop-calling/SKILL.md -->
---
name: bio-hi-c-analysis-loop-calling
description: Detects focal chromatin loops (point interactions / corner-dots) in balanced Hi-C and Micro-C contact maps and aggregates/validates a loop set. Covers de-novo calling with cooltools dots (HiCCUPS-style 4-background local enrichment with lambda-chunked FDR), chromosight (template-correlation), and Mustache (scale-space blob detection); aggregate peak analysis (APA) via cooltools pileup for confirmation; the depth/resolution prerequisite (de-novo needs ~5-10kb resolution = hundreds of millions to billions of valid pairs); consensus across callers and convergent-CTCF support as validation; and differential loops via union anchors plus chromosight quantify. Use when calling chromatin loops or dots from a cooler, deciding whether a map is deep enough to call de-novo vs running APA on known CTCF/cohesin anchors, building an aggregate peak pileup, comparing loops across conditions, or validating loop calls. For HiChIP/PLAC-seq/PCHi-C protein-anchored data use FitHiChIP/MAPS, not dots.
tool_type: mixed
primary_tool: cooltools
---

## Version Compatibility

Reference examples tested with: cooltools 0.7+, cooler 0.10+, bioframe 0.7+, chromosight 1.6+, mustache 1.3+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

The `.cool` must be BALANCED before calling loops -- `dots`/`pileup` read the `weight` column and raw counts are unsupported. An `.mcool` is multi-resolution; pass a single-resolution URI (`file.mcool::/resolutions/10000`), not the bare `.mcool`. cooltools changed signatures around 0.5 -> 0.7 (view_df/expected_value_col conventions); verify `help(cooltools.dots)` for the installed version. The `view_df` passed to `expected_cis` MUST be the same one passed to `dots`/`pileup`.

# Chromatin Loop Calling

**"Where are the focal loops (CTCF/cohesin corner-dots, E-P contacts) in my Hi-C map?"** -> Test each off-diagonal pixel for focal enrichment against its local background (on a balanced, expected-normalized matrix), control FDR, then validate the set by aggregation and orthogonal support.
- Python: `cooltools.dots(clr, expected=cooltools.expected_cis(clr, view_df=arms), view_df=arms)`
- CLI: `chromosight detect --pattern loops --min-dist 20000 --max-dist 2000000 sample.cool::/resolutions/5000 out`

## The Single Most Important Modern Insight -- Loop Calling Is Depth-Limited, Not Algorithm-Limited; the First Question Is "How Deep Is the Map?"

The caller choice is second-order. The dominant variable in whether loops are found at all is sequencing depth / map resolution. Rao 2014 needed ~4.9 BILLION contacts in GM12878 to reach 1kb bins and call ~10,000 loops; robust de-novo calling realistically wants 5-10kb resolution, which is hundreds of millions to billions of valid cis pairs. Below that, every caller returns near-nothing or noise, and tuning the FDR will not rescue it. So the workflow forks on depth before any tool is chosen:

1. **Deep map (>=~500M-1B valid pairs, 5-10kb resolution):** de-novo calling is licensed. Run cooltools `dots` (or chromosight / Mustache), then validate (see below).
2. **Shallow map:** do NOT de-novo call. Run **APA / pileup on a KNOWN anchor set** -- loops imported from a deep reference map, or anchor pairs built from CTCF/cohesin ChIP-seq peaks. This is the single most important practical reframe in the skill: shallow data can still *confirm and quantify* a hypothesized loop set even when it cannot *discover* one.

Two corollaries that follow directly:

**De-novo calling DISCOVERS; APA CONFIRMS -- never conflate them.** APA aggregates many putative loops to surface mean signal no individual loop could pass FDR for. An enriched APA center pixel proves "this SET of pairs is enriched on average"; it does NOT prove any single pair is a loop and it cannot discover new loops. Presenting an APA pileup as evidence that "these loops exist" is the classic abuse. And the APA score is meaningless without a **corner control** -- center pixel divided by an off-diagonal corner block of the flank is the on-vs-off measurement; the bare center value alone says nothing.

**Loops form between convergent CTCF motifs -- biology AND a validation filter.** Loops preferentially link two CTCF motifs in CONVERGENT orientation (Rao 2014 observation; de Wit 2015, Sanborn 2015 extrusion mechanism; proven by CTCF-site inversion experiments that kill or reroute the loop). A called corner-dot whose two anchors carry convergent CTCF motifs is high-confidence; one with no CTCF/anchor support on a shallow map is likely a false positive. Not all loops are CTCF loops (E-P and polycomb loops exist), so convergent-CTCF is a strong positive filter, not a universal requirement.

## Loop-Caller Taxonomy

| Tool | Philosophy | Mechanism | When |
|------|-----------|-----------|------|
| cooltools `dots` | local enrichment (CPU HiCCUPS) | pixel must beat 4 local backgrounds (donut/horizontal/vertical/lower-left); Poisson p; lambda-binned BH-FDR | cooler/.mcool pipelines, the modern default; pure-CPU |
| Juicer HiCCUPS | local enrichment (GPU original) | same 4-kernel model on `.hic`; CUDA-bound | `.hic`/Juicer ecosystem with a GPU available |
| chromosight `detect` | template correlation | Pearson correlation of a loop/border/stripe kernel vs each window | want loops AND borders AND stripes from one engine; Micro-C-friendly |
| Mustache | scale-space blobs | Difference-of-Gaussians across scales; multi-scale catches loops of different sizes | mixed loop sizes, kb-resolution Micro-C, recovers more E-P/ChIA-PET loops |
| SIP | image processing | Gaussian blur + regional-max + watershed | `.hic` image-based alternative |
| cooltools `pileup` (APA) | CONFIRMATION, not discovery | aggregate snippets centered on an anchor set; measure center vs corner | validate/quantify a loop SET; works on shallow maps |

Forcato 2017 (*Nat Methods* 14:679) is the canonical finding that loop callers show LOW pairwise overlap and poor replicate reproducibility -- far worse than TAD callers. Practical consequence: a loop called by only one tool is suspect. Trust comes from consensus across >=2 callers plus orthogonal support (convergent CTCF, ChIA-PET/HiChIP), not from any single tool's list length.

## Decision Tree by Scenario

| Scenario | Recommended | Why |
|----------|-------------|-----|
| Shallow map (tens of M pairs) | APA/pileup on KNOWN anchors (CTCF/cohesin ChIP or reference loops) -- STOP de-novo | callers return noise below ~5-10kb resolution |
| Deep cooler/.mcool, CPU only | `cooltools.dots` (default) | pure-CPU HiCCUPS reimplementation on balanced cooler |
| Deep `.hic` with a GPU | Juicer HiCCUPS | CUDA original built for billion-contact `.hic` scans |
| Mixed loop sizes / kb Micro-C | Mustache | scale-space natively spans loop sizes; sub-5kb-friendly |
| Want stripes/borders too | chromosight (swap `--pattern`) | same template engine; stripes are a SEPARATE class, not loops |
| Validate a call set | `cooltools.pileup` -> APA score vs corner control | aggregate enrichment + visual QC of the dot |
| Confirm anchors are real loops | convergent-CTCF check -> chip-seq/peak-annotation, atac-seq/footprinting | extrusion loops carry convergent CTCF motifs |
| Annotate loop anchors | -> chip-seq/peak-annotation, atac-seq/enhancer-gene-linking | E-P / TF context lives there |
| Anchor-overlap enrichment p-value | -> genome-intervals/overlap-significance | turn an anchor-overlap count into a permutation test |
| Two conditions, loop strength shift | union anchors -> chromosight `quantify` per condition -> test delta (or `diff_mustache`) | NO bin-level DESeq for loops; quantify a fixed coordinate set |
| HiChIP / PLAC-seq / PCHi-C | FitHiChIP / MAPS / HiC-DC+ -> chip-seq/peak-calling | protein-anchored, coverage-biased; HiCCUPS null is wrong |

## De-Novo Loop Calling with cooltools dots

**Goal:** Discover focal loops genome-wide on a deep, balanced map with honest FDR control.

**Approach:** Build chromosome-arm regions, compute the distance-decay expected on those arms, then run `dots` -- which convolves four local-background kernels and runs Benjamini-Hochberg FDR independently within geometrically-spaced lambda-bins of locally-adjusted expected. The arms `view_df` must be identical for `expected_cis` and `dots`.

```python
import cooler, cooltools, bioframe

clr = cooler.Cooler('matrix.mcool::/resolutions/10000')   # 10kb: a realistic de-novo floor; finer needs more depth
arms = bioframe.make_viewframe(clr.chromsizes)   # or cooltools.lib.read_viewframe_from_file('hg38_arms.bed', clr) for per-arm
expected = cooltools.expected_cis(clr, view_df=arms, nproc=4)   # distance-matched background; same view as dots
loops = cooltools.dots(
    clr, expected=expected, view_df=arms,
    max_loci_separation=10_000_000,   # ignore pixels farther than 10Mb from the diagonal
    n_lambda_bins=40, lambda_bin_fdr=0.1,   # FDR run independently per geometric lambda-bin (HiCCUPS default)
    clustering_radius=20_000,   # merge called pixels within 20kb into one loop
    nproc=4,
)
```

**The four backgrounds, and why lower-left is the clever one.** A pixel must beat ALL four local-background kernels, not one. **Donut** = is it a focal enrichment at all. **Horizontal** and **vertical** = is it actually a STRIPE pixel masquerading as a dot (these kernels exist to NOT call architectural stripes as loops). **Lower-left** = is it just a TAD/contact-domain CORNER -- a domain corner is enriched vs the donut but NOT vs its lower-left neighborhood, so requiring the pixel to also beat lower-left separates a genuine point loop from a generic domain corner. Skipping lower-left inflates calls with domain corners.

**Lambda-chunking is why HiCCUPS FDR is honest.** Contact counts span orders of magnitude with genomic distance, so a single genome-wide BH-FDR would be dominated by the high-count near-diagonal regime and over-call. `dots` bins pixels by their locally-adjusted expected into geometrically-spaced lambda-bins (`n_lambda_bins=40`) and runs BH-FDR independently within each (`lambda_bin_fdr=0.1`), so low-count and high-count regimes are each thresholded correctly.

## Template-Matching with chromosight

```bash
# detect: <contact_map> <prefix> are positional and come LAST
chromosight detect --pattern loops --threads 8 \
  --min-dist 20000 --max-dist 2000000 --pearson 0.4 \
  sample.cool::/resolutions/5000 sample_loops
# output: sample_loops.tsv -> chrom1,start1,end1,chrom2,start2,end2,bin1,bin2,score,pvalue,qvalue
```

The score is a Pearson correlation (-1..1) between a loop kernel and each windowed submatrix. The same engine finds borders and stripes by swapping `--pattern` (loops, loops_small, borders, hairpins, centromeres, stripes_left, stripes_right) -- but stripes are a separate feature class, NOT loops. `--pearson` is the correlation cutoff; raise it for fewer, higher-confidence calls.

## Scale-Space with Mustache

```bash
mustache -f sample.mcool -r 5000 -o loops.tsv -pt 0.1 -st 0.88 -norm weight -p 8
# output: BIN1_CHR BIN1_START BIN1_END BIN2_CHR BIN2_START BIN2_END FDR DETECTION_SCALE
```

`-pt` is the FDR/p-value threshold (default 0.1), `-st` the sparsity filter (default 0.88), `-norm weight` for a balanced `.cool` (`KR` for `.hic`). Mustache spans loop sizes natively via Difference-of-Gaussians across scales, which is why it adapts to kb-resolution Micro-C better than fixed-kernel HiCCUPS.

## Aggregate Peak Analysis (APA) -- Confirm, Don't Discover

**Goal:** Quantify whether a loop SET is enriched on average and visually QC the call set (a clean aggregate dot = mostly real; a smeared/absent center = contaminated).

**Approach:** Compute expected, pile up observed/expected snippets centered on each anchor pair, average across the stack, then report the APA score = center pixel divided by an off-diagonal corner-control block. Pass `expected_df` so snippets are O/E and comparable across genomic separations.

```python
import numpy as np
import cooltools

expected = cooltools.expected_cis(clr, view_df=arms, nproc=4)
stack = cooltools.pileup(clr, loops, view_df=arms, expected_df=expected, flank=100_000, nproc=4)   # bedpe two-anchor features
apa = np.nanmean(stack, axis=0)   # pileup returns (n_snippets, D, D); average over axis 0 -> 2D aggregate

center = apa.shape[0] // 2
corner = 3   # 3x3 corner-control block (Rao 2014 lower-left convention)
apa_score = apa[center, center] / np.nanmean(apa[-corner:, :corner])   # center vs lower-left corner; >1 = enriched
```

## Differential Loops -- Union Anchors, Not a Bin-Level Tool

**Goal:** Find loops whose strength changes between conditions.

**Approach:** There is NO DESeq-for-loops. Build a UNION anchor set across conditions, then score each loop's strength per condition at a FIXED coordinate set (`chromosight quantify`, which is purpose-built for this, or APA per condition), then test the strength delta.

```bash
# quantify scores a FIXED coordinate set; arg order: <bed2d> <contact_map> <prefix>
chromosight quantify --pattern loops union_anchors.bed2d condA.cool condA_q
chromosight quantify --pattern loops union_anchors.bed2d condB.cool condB_q
# compare the per-loop score columns; or diff_mustache.py -f1 A -f2 B -pt 0.05 -pt2 0.1 -r 5000 -o diff
```

`diffHic`, `multiHiCcompare`, and `dcHiC` operate on BINS or COMPARTMENTS, not focal loops -- do NOT use them as a loop-differential tool. Cross-reference hic-differential for the bin/compartment regime.

## Per-Method Failure Modes

### De-novo calling on a shallow map
**Trigger:** running `dots`/chromosight/Mustache on tens of millions of pairs or >=25kb bins. **Mechanism:** focal signal is below the noise floor without depth. **Symptom:** zero or a handful of scattered, irreproducible calls. **Fix:** STOP de-novo; run APA on a known anchor set (CTCF/cohesin ChIP or reference loops).

### APA reported without a corner control
**Trigger:** quoting the aggregate center-pixel value as the loop "strength." **Mechanism:** without an off-diagonal corner the number has no on-vs-off baseline. **Symptom:** a "high" APA that reflects distance-decay, not looping. **Fix:** APA score = center / corner-control block (Rao 2014 lower-left convention).

### APA presented as proof loops exist
**Trigger:** showing a pileup to claim "these N loops are real." **Mechanism:** APA surfaces mean enrichment across a SET; it cannot validate any single loop or discover new ones. **Symptom:** confident per-loop claims backed only by an aggregate. **Fix:** treat APA as set-level confirmation; for per-loop confidence use consensus + convergent-CTCF.

### Trusting a single caller's list
**Trigger:** reporting "Mustache found N loops" with no cross-check. **Mechanism:** callers have low pairwise overlap (Forcato 2017). **Symptom:** a list that barely overlaps a second tool or replicate. **Fix:** intersect >=2 callers and require convergent-CTCF / ChIA-PET / HiChIP support.

### Calling domain corners as loops
**Trigger:** a caller without a lower-left background (or a custom kernel set). **Mechanism:** a TAD corner beats the donut but is not a point loop. **Symptom:** "loops" sitting exactly at TAD corners with no anchor support. **Fix:** use `dots` (it beats all four backgrounds); cross-check anchors.

### Calling stripe pixels as dots
**Trigger:** detecting on a map with strong architectural stripes. **Mechanism:** a stripe pixel is enriched vs the donut but lies on a horizontal/vertical band. **Symptom:** "loops" smeared along a row/column. **Fix:** the horizontal/vertical kernels suppress these in `dots`; treat stripes as a separate class (chromosight stripes_*).

### 10kb-tuned kernels on 1kb Micro-C
**Trigger:** default HiCCUPS donut/peak-width on sub-5kb Micro-C. **Mechanism:** kernels are sized for 5-10kb Hi-C. **Symptom:** blurred or missed fine E-P loops. **Fix:** shrink the kernels for sub-5kb, or use Mustache/chromosight which adapt more gracefully.

### Raw (unbalanced) matrix into dots
**Trigger:** `dots` on a cooler with no `weight` column. **Mechanism:** dots requires balancing weights + expected. **Symptom:** error or meaningless output. **Fix:** `cooler balance` first; confirm `clr.matrix(balance=True)` is not all-NaN.

### HiCCUPS-style calling on HiChIP/PLAC-seq
**Trigger:** running `dots` on cohesin/H3K27ac HiChIP or PLAC-seq. **Mechanism:** protein-anchored data is coverage-biased; the Hi-C null is wrong. **Symptom:** distorted FDR, wrong loop counts. **Fix:** use FitHiChIP/MAPS/HiC-DC+ against a protein-anchored background.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| De-novo loop resolution 5-10kb | Rao 2014 depth scaling | ~4.9B contacts reached 1kb / ~10k loops; coarser bins blur anchors, shallow maps cannot resolve them |
| `max_loci_separation` 2-10Mb | loop size distribution | most loops are <2Mb; 10Mb is the cooltools default ceiling on diagonal distance |
| `n_lambda_bins=40`, `lambda_bin_fdr=0.1` | cooltools/HiCCUPS default | geometric lambda-binning + per-bin BH-FDR keeps FDR honest across the count dynamic range |
| `clustering_radius=20_000` | cooltools default | merges adjacent called pixels into one loop call |
| chromosight `--pearson` ~0.4 loops | chromosight default | template-correlation cutoff; raise for higher-confidence, fewer calls |
| Mustache `-pt 0.1`, `-st 0.88` | Mustache defaults | p/FDR threshold and sparsity filter |
| Consensus across >=2 callers | Forcato 2017 low overlap | single-caller lists are unreliable; require intersection or orthogonal support |
| APA score = center / corner block | Rao 2014 | the corner is the on-vs-off control; the bare center is uninterpretable |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| `dots` returns nothing / scattered junk | map too shallow or resolution too coarse | check depth; below ~5-10kb resolution run APA on known anchors instead |
| `clr.matrix(balance=True)` all NaN | cooler not balanced | `cooler balance` / `cooler.balance_cooler` before calling loops |
| `expected`/`dots` shape or view error | different `view_df` for expected vs dots | reuse the same `view_df` (arms) for `expected_cis` and `dots` |
| Empty / wrong-resolution result on `.mcool` | bare `.mcool` passed | use `file.mcool::/resolutions/<bp>` URI |
| Empty result, no error | chrom naming mismatch (`chr1` vs `1`) across cooler/anchors/peaks | harmonize chromosome naming everywhere |
| `AttributeError` on a cooltools function | pre-0.7 vs 0.7+ signature change | `help(cooltools.dots)`; adapt to the installed signature |
| APA center looks high but loops are weak | no corner control / `expected_df` omitted | pass `expected_df` and divide center by a corner block |

## References

- Rao SSP, Huntley MH, Durand NC, et al. 2014. A 3D map of the human genome at kilobase resolution reveals principles of chromatin looping. *Cell* 159(7):1665-1680.
- Open2C, Abdennur N, Abraham S, Fudenberg G, et al. 2024. Cooltools: enabling high-resolution Hi-C analysis in Python. *PLoS Comput Biol* 20(5):e1012067.
- Matthey-Doret C, Baudry L, Breuer A, et al. 2020. Computer vision for pattern detection in chromosome contact maps (chromosight). *Nat Commun* 11:5795.
- Roayaei Ardakany A, Gezer HT, Lonardi S, Ay F. 2020. Mustache: multi-scale detection of chromatin loops from Hi-C and Micro-C maps using scale-space representation. *Genome Biol* 21:256.
- Rowley MJ, Poulet A, Nichols MH, et al. 2020. Analysis of Hi-C data using SIP effectively identifies loops in organisms from C. elegans to mammals. *Genome Res* 30(3):447-458.
- Forcato M, Nicoletti C, Pal K, et al. 2017. Comparison of computational methods for Hi-C data analysis. *Nat Methods* 14:679-685.
- de Wit E, Vos ESM, Holwerda SJB, et al. 2015. CTCF binding polarity determines chromatin looping. *Mol Cell* 60(4):676-684.
- Sanborn AL, Rao SSP, Huang SC, et al. 2015. Chromatin extrusion explains key features of loop and domain formation. *PNAS* 112(47):E6456-E6465.
- Rao SSP, Huang SC, Glenn St Hilaire B, et al. 2017. Cohesin loss eliminates all loop domains. *Cell* 171(2):305-320.
- Haarhuis JHI, van der Weide RH, Blomen VA, et al. 2017. The cohesin release factor WAPL restricts chromatin loop extension. *Cell* 169(4):693-707.
- Schwarzer W, Abdennur N, Goloborodko A, et al. 2017. Two independent modes of chromatin organization revealed by cohesin removal. *Nature* 551:51-56.
- Krietenstein N, Abraham S, Venev SV, et al. 2020. Ultrastructural details of mammalian chromosome architecture (Micro-C). *Mol Cell* 78(3):554-565.
- Hsieh THS, Cattoglio C, Slobodyanyuk E, et al. 2020. Resolving the 3D landscape of transcription-linked mammalian chromatin folding (Micro-C). *Mol Cell* 78(3):539-553.
- Bhattacharyya S, Chandra V, Vijayanand P, Ay F. 2019. Identification of significant chromatin contacts from HiChIP data by FitHiChIP. *Nat Commun* 10:4221.

## Related Skills

- hic-data-io - Load and access the cooler files this skill calls loops on
- matrix-operations - Balancing and expected/O/E that dots and pileup depend on
- hic-visualization - Render called loops and APA pileups on the heatmap
- hic-differential - Bin/compartment-level differential (the regime loops are NOT in)
- tad-detection - TAD corners vs point loops; the lower-left background separates them
- chip-seq/peak-calling - CTCF/cohesin peaks to anchor and validate loops; HiChIP peak context
- chip-seq/peak-annotation - Annotate loop anchors with TF/CTCF peaks
- atac-seq/enhancer-gene-linking - E-P contacts complementing loop calls
- atac-seq/footprinting - TF footprints at loop anchors
- genome-intervals/overlap-significance - Permutation test for anchor/feature enrichment
<!-- END FILE: hi-c-analysis/loop-calling/SKILL.md -->

## 子目录：hi-c-analysis/matrix-operations

<!-- BEGIN FILE: hi-c-analysis/matrix-operations/SKILL.md -->
---
name: bio-hi-c-analysis-matrix-operations
description: Balances Hi-C contact matrices (ICE via cooler.balance_cooler, KR/SCALE/VC context), computes distance-decay expected with cooltools (expected_cis per-diagonal P(s), expected_trans scalar), builds observed/expected (O/E) matrices, and diagnoses polymer state from the P(s) log-derivative. Covers the within-matrix-vs-cross-sample distinction (balancing is NOT a normalizer), the equal-visibility assumption that CNV/aneuploidy violates (use raw counts for copy-number), cis-only balancing, mad_max/blacklist masking before balancing, multiplicative cooler weights vs divisive juicer weights, and the resolution-vs-depth budget. Use when balancing a .cool/.mcool, computing expected or P(s), making O/E matrices for compartments/loops, deciding ICE vs KR vs SCALE, choosing a resolution for a given depth, or troubleshooting NaN/all-NaN balanced matrices; route cross-sample comparison to hic-differential.
tool_type: python
primary_tool: cooler
---

## Version Compatibility

Reference examples tested with: cooler 0.10+, cooltools 0.7+, bioframe 0.7+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

cooltools standardized its API around 0.7 (functions take a `view_df` viewframe; `expected_cis` defaults to `smooth=True, aggregate_smoothed=True`). `.mcool` is multi-resolution: analysis functions take a single-resolution URI (`file.mcool::/resolutions/10000`), never the bare `.mcool`. A matrix must be balanced (a stored `weight` column) before O/E, compartments, insulation, or dots; `clr.matrix(balance=True)` on an unbalanced cooler returns all-NaN.

# Hi-C Matrix Operations

**"Make the pixels of my Hi-C matrix comparable to each other."** -> Balance (remove per-bin coverage bias under equal-visibility), then divide by distance-matched expected (remove the polymer P(s) background) to get O/E.
- Python: `cooler.balance_cooler(clr, cis_only=True, store=True)`, then `cooltools.expected_cis(clr)` and divide observed by per-diagonal expected.

## The Single Most Important Modern Insight -- Balancing Makes ONE Matrix Self-Consistent; It Does NOT Make Two Matrices Comparable

Balancing (ICE/KR) is a *within-matrix* operation: it solves for per-bin bias weights so every bin has equal genome-wide visibility, making a single map internally consistent. It does nothing to relate map A to map B. Two balanced matrices at different sequencing depth still differ in absolute magnitude, dynamic range, and noise floor -- and `rescale_marginals` makes the absolute balanced values arbitrary-scaled anyway. "I balanced both, now I'll subtract/log2-ratio them" is the single most common error in the field: the depth difference is read as biology. Cross-sample comparison requires downsampling to equal valid-pair count, distance-matched O/E, and a replicate-aware differential tool (multiHiCcompare, HiCcompare loess-over-distance, dcHiC) -- route to hic-differential.

Two corollaries that flow from the same equal-visibility model:

1. **CNV silently breaks balancing.** The premise is that every bin *should* make the same number of contacts; any deviation is technical bias. That is true for a diploid uniform-copy genome and FALSE for tumors/aneuploids -- a 3-copy region genuinely contacts ~3x more. ICE forces equal marginals and ERASES that real copy-number, then redistributes it perversely (post-ICE high-copy regions go cis-depleted, trans-enriched; Servant 2018). Use **raw counts** for CNV/SV calling (coverage IS the signal -> copy-number); plain ICE/KR on an aneuploid is a category error (use CNV-aware LOIC/CAIC for 3D structure).
2. **A balanced cis map is still dominated by distance-decay.** The A/B plaid and focal loops are a faint modulation under the P(s) background. Dividing by distance-matched expected (O/E) before eigendecomposition is mandatory, or the top eigenvector is just the decay curve, not compartments.

## Normalization-Method Taxonomy

| Method | What it does | Mechanism | When |
|--------|-------------|-----------|------|
| ICE (cooler native) | true matrix balancing | iterative proportional fitting (Sinkhorn); equalizes all marginals | default; robust, converges on sparse/low-depth where KR fails |
| KR (juicer) | true matrix balancing | Knight-Ruiz Newton solver; SAME fixed point as ICE | fast (few iterations); fails to converge on sparse/high-res maps |
| SCALE (juicer) | true matrix balancing | modern KR-family solver, more robust | juicer's default; converges where KR diverges on sparse maps |
| VC / vanilla coverage | NOT true balancing | single pass: divide by row-coverage * col-coverage (one ICE iteration) | fast robust fallback; leaves residual bias |
| VC_SQRT | NOT true balancing | divide by sqrt of coverage product (gentler than VC) | very sparse data where full balancing overfits |
| LOIC / CAIC (Servant 2018) | CNV-aware balancing | condition on copy-number; LOIC keeps the CN effect, CAIC removes it | aneuploid/tumor genomes (plain ICE is wrong here) |

KR and ICE reach the same balanced map -- choose by **convergence, not quality**: KR is faster but blows up on sparse/low-depth/high-resolution matrices; ICE is the robust default; SCALE is the juicer-side answer when KR fails.

## Decision Tree by Scenario

| Scenario | Recommended | Why |
|----------|-------------|-----|
| Need to balance a diploid map | `cooler.balance_cooler(cis_only=True, store=True)` (ICE) | robust default; cis-only is the analysis convention |
| KR failed to converge (sparse/high-res) | fall back to ICE, or SCALE on the juicer side | same fixed point; ICE/SCALE are the robust solvers |
| Tumor / aneuploid genome, 3D structure | CNV-aware LOIC/CAIC (Servant 2018) | plain ICE erases real copy-number |
| CNV / SV calling from Hi-C | RAW counts (no balancing) | coverage is the signal -> copy-number |
| Compartments at 100kb-1Mb | balance -> `expected_cis` -> O/E -> Pearson -> eigenvector | O/E removes P(s) so the plaid is visible -> compartment-analysis |
| Focal loops / TADs | balance -> `expected_cis` -> O/E | local enrichment needs the distance background removed -> loop-calling, tad-detection |
| P(s) / polymer-state diagnostic | `expected_cis(smooth=True)` -> log-derivative | the derivative reads out loop-extrusion machinery |
| Imported a juicer KR/VC weight column | check `divisive_weights` before applying | cooler weights are multiplicative, juicer's are divisive |
| Compare two conditions | downsample to equal depth, then -> hic-differential | balancing is within-matrix, not a cross-sample normalizer |
| Bare `.mcool` passed and KeyError | use `file.mcool::/resolutions/<bp>` URI | `.mcool` is a container of resolutions |

## Balance a Matrix (ICE)

**Goal:** Remove one-dimensional per-bin coverage bias so every bin has equal genome-wide visibility within this single map.

**Approach:** Mask low-coverage and blacklisted bins FIRST (mad_max on log-marginals + explicit blacklist of centromere/rDNA/unmappable), drop the first two diagonals (ligation chemistry, not 3D contact), then run cis-only ICE; the multiplicative weight vector is stored in the `weight` column.

```python
import cooler

clr = cooler.Cooler('matrix.mcool::/resolutions/10000')
bias, stats = cooler.balance_cooler(clr, cis_only=True, mad_max=5, ignore_diags=2, blacklist=None, store=True)
print('converged:', stats['converged'], 'scale:', stats['scale'])   # stats also reports var, divisive_weights

clr = cooler.Cooler('matrix.mcool::/resolutions/10000')              # re-open to see the stored weights
balanced = clr.matrix(balance=True).fetch('chr1')                    # raw[i,j] * w[i] * w[j]; masked bins -> NaN
```

`cis_only=True` is the convention for compartment/TAD/loop work -- trans signal is weak, noisy ambient ligation that pulls the bias estimates toward trans noise. `ignore_diags=2` drops the main diagonal (self-ligation/dangling ends) and first off-diagonal (undigested/religated fragments): huge untrustworthy counts that would dominate the marginals. `mad_max=5` filters bins whose **log**-marginal is >5 MAD below the median; without it a near-empty unmappable/centromeric bin gets a gigantic weight and ICE diverges. Masking (mad_max + `blacklist`) MUST precede balancing -- balancing cannot rescue a no-signal bin, it amplifies it.

CLI equivalent:

```bash
cooler balance --cis-only --mad-max 5 --ignore-diags 2 matrix.mcool::/resolutions/10000
```

## Expected: cis P(s) Curve and trans Scalar

**Goal:** Build the distance-decay background (the denominator for O/E) and the P(s) curve for diagnostics.

**Approach:** cis expected is a per-diagonal curve (one value per separation s -- this IS P(s)); trans expected is a single scalar per chromosome-pair block (trans contacts are ~distance-independent). cooltools enforces the split with two functions.

```python
import cooltools
import bioframe

clr = cooler.Cooler('matrix.mcool::/resolutions/10000')
view_df = bioframe.make_viewframe(clr.chromsizes)               # whole-chromosome regions; or arms for acrocentric genomes

cvd = cooltools.expected_cis(clr, view_df=view_df, smooth=True, aggregate_smoothed=True, ignore_diags=2)
# columns include: region1, region2, dist, dist_bp, n_valid, count.avg, balanced.avg, balanced.avg.smoothed.agg

trans_exp = cooltools.expected_trans(clr, view_df=view_df)      # one balanced.avg per region1-region2 block
```

`smooth=True` smooths P(s) in log10(distance) space (`smooth_sigma=0.1`). Pre-0.7.0 cooltools errored on raw smoothing (`clr_weight_name=None, smooth=True`, issue #456); that was fixed in 0.7.0, and raw smoothing now returns `count.avg.smoothed`. Regardless of version, balance first: a raw expected still carries per-bin coverage bias, so it is not a clean P(s)/O/E denominator.

## Observed/Expected Matrix

**Goal:** Divide out the polymer distance-decay so enrichment (loops, plaid) stands above the local background.

**Approach:** Map the per-diagonal cis expected (`balanced.avg`, keyed by `dist`) onto a dense balanced matrix by diagonal offset -- vectorized with numpy diagonal indexing, NOT an O(n^2) Python loop.

```python
import numpy as np

def oe_matrix(clr, region, cvd):
    obs = clr.matrix(balance=True).fetch(region)
    chrom = region.split(':')[0] if isinstance(region, str) else region[0]
    exp = cvd[cvd['region1'] == chrom].set_index('dist')['balanced.avg']
    exp_by_dist = exp.reindex(range(obs.shape[0])).to_numpy()              # one expected per separation s
    expected = exp_by_dist[np.abs(np.subtract.outer(np.arange(obs.shape[0]), np.arange(obs.shape[0])))]
    return obs / expected                                                  # NaN where expected is NaN (masked diags)

oe = oe_matrix(clr, 'chr1', cvd)
log_oe = np.log2(oe)                                                        # symmetric around 0 for display
```

cooltools also ships `cooltools.lib.numutils.observed_over_expected(matrix, mask)` (returns a 4-tuple `(OE, dist_bins, sum_pixels, n_pixels)`) for a self-contained dense O/E without a precomputed `cvd`.

## P(s) Log-Derivative -- the Polymer-State Diagnostic

**Goal:** Read out chromatin polymer state and loop-extrusion machinery from the shape of the contact-decay curve.

**Approach:** Take the slope of P(s) in log-log space; a reference slope near -1 over 0.1-1 Mb is the crumpled-globule background, and a loop-extrusion bump (~100kb interphase) appears as a peak in the derivative. Smooth in logspace FIRST or the derivative is pure noise.

```python
agg = cvd[(cvd['region1'] == cvd['region2']) & (cvd['dist'] > 0)].drop_duplicates('dist_bp')
slope = np.gradient(np.log(agg['balanced.avg.smoothed.agg']), np.log(agg['dist_bp']))
# slope ~ -1 over 0.1-1 Mb; a bump toward 0 near ~100kb flags cohesin loop extrusion (flattens on WAPL/RAD21 loss)
```

## Resolution-vs-Depth Budget

The achievable resolution is a function of depth and genome size, not a free choice. Rule of thumb: a bin needs ~**1000 contacts** to be reliably populated, and the number of bins scales as N^2 with the number of genomic bins -- so halving bin size quarters per-bin coverage. Coarse features are cheap, focal features are expensive:

| Feature | Resolution | Approximate depth (human) | Why |
|---------|-----------|---------------------------|-----|
| A/B compartments | 100kb-1Mb | tens of millions of valid pairs | chromosome-scale, few large bins -> cheap |
| TADs / insulation | 10-50kb | hundreds of millions | sub-Mb domains; window 5-25x the bin |
| Loops / dots | <=10kb | billions (Rao 2014 in-situ Hi-C ~ billions) | focal kb-scale pixels; coarse bins blur anchors |

Calling 10kb loops from a shallow library binned at 50kb is not a resolution choice -- there is no signal there. Choose the finest resolution where median per-bin contacts stay near ~1000.

## Per-Method Failure Modes

### Cross-sample subtraction of balanced matrices
**Trigger:** balancing two libraries then log2-ratioing/subtracting. **Mechanism:** balancing is within-matrix; balanced magnitude still scales with depth and `rescale_marginals` makes it arbitrary. **Symptom:** systematic genome-wide "differences" that track sequencing depth. **Fix:** downsample to equal valid pairs, compare O/E, use a replicate-aware tool -> hic-differential.

### Plain ICE on an aneuploid / tumor
**Trigger:** `balance_cooler` on a genome with large copy-number swings. **Mechanism:** equal-visibility forces equal marginals, erasing the real ~CN-fold coverage. **Symptom:** high-copy regions look cis-depleted/trans-enriched (Servant 2018); CNV vanishes. **Fix:** raw counts for CNV calling; LOIC/CAIC for 3D structure.

### Masking after (not before) balancing
**Trigger:** low-coverage centromere/rDNA/unmappable bins left in before ICE. **Mechanism:** a near-empty bin gets a gigantic bias weight. **Symptom:** ICE fails to converge, or stripe artifacts radiate from a few bins. **Fix:** set `mad_max` and pass `blacklist`; masking precedes balancing.

### Eigendecomposition on a balanced (non-O/E) map
**Trigger:** compartment calling skips the expected/O/E step. **Mechanism:** the distance-decay dominates the balanced cis map. **Symptom:** top eigenvector is the P(s) curve, not the A/B plaid. **Fix:** divide by `expected_cis` (O/E) before correlating/eigendecomposing.

### Crossing multiplicative and divisive weights
**Trigger:** applying an imported juicer KR/VC vector as if it were a cooler weight. **Mechanism:** cooler weights are multiplicative (raw*w*w), juicer's are divisive (raw/w/w). **Symptom:** correction inverts -- high-bias bins get MORE extreme; nothing errors. **Fix:** check the weight column's `divisive_weights` attribute before applying.

### O/E from a raw (unbalanced) expected
**Trigger:** computing P(s)/O/E from `expected_cis(clr_weight_name=None)`. **Mechanism:** raw expected still carries per-bin coverage bias, so dividing by it does not cleanly remove the polymer background; pre-0.7.0 cooltools additionally errored on `smooth=True` with raw (issue #456, fixed in 0.7.0). **Symptom:** O/E still shows coverage stripes; on old cooltools, an error demanding balanced data. **Fix:** balance first, then `expected_cis` on the balanced `weight` column.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| `ignore_diags=2` | cooler default; ICE convention | drops self-ligation/dangling (diag 0) + undigested/religated (diag 1); ligation chemistry, not 3D contact |
| `mad_max=5` | cooler default | drops bins >5 MAD below median LOG-marginal; near-empty bins otherwise get exploding weights |
| `min_nnz=10` | cooler default | <10 nonzero pixels per row is too sparse to estimate a bias reliably |
| `tol=1e-5`, `max_iters=200` | cooler defaults | convergence = variance of balanced marginals < tol; non-convergence usually = a masking problem, not a tol problem |
| `smooth_sigma=0.1` | cooltools default | Gaussian std in log10(distance) units for P(s) smoothing |
| ~1000 contacts/bin | depth-budget convention | per-bin coverage floor for a reliably populated bin; bins scale ~N^2 |
| Compartment res 100kb-1Mb | compartment scale | finer bins mix in TAD/loop structure |
| TAD/insulation res 10-50kb | domain scale | sub-Mb domains; window 5-25x the bin |
| Loop res <=10kb (needs ~billions of pairs) | Rao 2014 in-situ Hi-C | focal kb-scale; coarse bins blur loop anchors |
| P(s) slope ~ -1 over 0.1-1 Mb | crumpled/fractal globule | reference background; deviations/derivative read out polymer state |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| `clr.matrix(balance=True)` all NaN | cooler not balanced | run `cooler.balance_cooler(..., store=True)` first |
| Empty / wrong-resolution result on .mcool | bare `.mcool` passed | use `file.mcool::/resolutions/<bp>` URI |
| ICE not converging | low-coverage bins not masked | raise/set `mad_max`, pass `blacklist`; do not just raise `max_iters` |
| `expected_cis(smooth=True)` errors on raw (pre-0.7.0 only) | `clr_weight_name=None` on old cooltools (issue #456, fixed 0.7.0) | upgrade to cooltools 0.7+, or balance first / `smooth=False` |
| O/E enrichment inverted on a tumor | ICE applied to an aneuploid | use raw counts / LOIC/CAIC; equal-visibility is violated |
| Imported weight makes bias worse | divisive juicer weight applied as multiplicative | check `divisive_weights`; reciprocate if needed |
| Cross-condition "difference" tracks depth | subtracting balanced matrices | downsample + O/E + replicate-aware test -> hic-differential |

## References

- Imakaev et al. 2012 *Nat Methods* 9:999-1003 -- ICE iterative correction.
- Knight & Ruiz 2013 *IMA J Numer Anal* 33(3):1029-1047 -- KR matrix-balancing algorithm.
- Rao et al. 2014 *Cell* 159(7):1665-1680 -- in-situ Hi-C, KR norm, VC/VC_SQRT, kilobase loops (depth budget).
- Cournac et al. 2012 *BMC Genomics* 13:436 -- sequential/vanilla-coverage (SCN/VC) normalization.
- Servant et al. 2018 *BMC Bioinformatics* 19:313 -- CNV-aware normalization (LOIC/CAIC); ICE erases copy-number.
- Abdennur & Mirny 2020 *Bioinformatics* 36(1):311-316 -- cooler.
- Open2C, Abdennur et al. 2024 *PLoS Comput Biol* 20(5):e1012067 -- cooltools.
- Open2C, Abdennur et al. 2024 *Bioinformatics* 40(2):btae088 -- bioframe.

## Related Skills

- hic-data-io - Load the cooler files this skill balances; divisive-vs-multiplicative weight naming
- compartment-analysis - Consumes the O/E this skill produces for eigenvector calling
- tad-detection - Insulation needs a cis-balanced matrix
- loop-calling - Dots need balanced + expected as prerequisites
- hic-differential - Cross-sample comparison; the right home for subtracting/ratioing conditions
- hic-visualization - Render balanced/O/E/log matrices
- copy-number/cnv-visualization - Raw-count CNV from Hi-C when balancing would erase copy-number
- genome-intervals/bigwig-tracks - Export the P(s)/expected or eigenvector as a bigWig
<!-- END FILE: hi-c-analysis/matrix-operations/SKILL.md -->

## 子目录：hi-c-analysis/tad-detection

<!-- BEGIN FILE: hi-c-analysis/tad-detection/SKILL.md -->
---
name: bio-hi-c-analysis-tad-detection
description: Detects TAD boundaries from balanced Hi-C contact matrices via the diamond-window insulation score (cooltools insulation) and HiCExplorer hicFindTADs, returning a continuous log2 insulation track, valley-prominence boundary_strength, and Li/Otsu-thresholded is_boundary flags across a list of window sizes. Covers the multi-scale window sweep (sub-TAD to compartment-domain), why the boundary is reproducible but the domain partition is not, cross-condition comparison via differential SCORE not differential partition, and the insulation-vs-compartment orthogonality. Use when calling TADs or domain boundaries, computing insulation scores, choosing a window size, ranking boundary strength, comparing boundaries across conditions, or annotating CTCF-backed boundaries; route domain rendering to hic-visualization and boundary-feature overlap to genome-intervals.
tool_type: mixed
primary_tool: cooltools
---

## Version Compatibility

Reference examples tested with: cooler 0.10+, cooltools 0.7+, bioframe 0.7+, HiCExplorer 3.7+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

cooltools changed its API around 0.5 -> 0.7+ (functions standardized on `view_df`/viewframe arguments; `insulation` returns the `boundary_strength_{W}`/`is_boundary_{W}` columns). A `.cool` MUST be balanced (a stored `weight` column) before insulation; `clr.matrix(balance=True)` on an unbalanced cooler returns all-NaN. A `.mcool` is multi-resolution: pass a single-resolution URI (`file.mcool::/resolutions/10000`), never the bare `.mcool`.

# TAD Detection

**"Where are the reproducible domain boundaries in my Hi-C matrix, and how strong?"** -> Compute the diamond-window insulation score on the balanced matrix, take valley minima as boundaries and their prominence as strength, and report across a LIST of window sizes rather than a single magic scale.
- Python: `cooltools.insulation(clr, [3*res, 5*res, 10*res, 25*res])` then rank by `boundary_strength_{W}`
- CLI: `hicFindTADs -m corrected.cool --outPrefix tads --correctForMultipleTesting fdr` (sweep `--minDepth/--maxDepth/--step`)

## The Single Most Important Modern Insight -- The Boundary Is Real; the Domain Is Mostly an Averaging Artifact

A population Hi-C "TAD" is the ensemble average over a heterogeneous mixture of cell-specific, stochastic domains. Single-cell imaging (Bintu 2018 *Science* 362:eaau1783) shows individual cells DO have sharp domains, but the boundary POSITION varies cell to cell - the population boundary is a *preferred* position, not a wall. Cohesin depletion abolishes population TADs while leaving single-cell domains intact, removing only the preferred-position bias. Three consequences govern every decision in this skill:

1. **"How many TADs are there" is the wrong question.** TAD number and size vary 2-5x across caller, resolution, and normalization, with NO ground truth (Forcato 2017 *Nat Methods* 14:679; Zufferey 2018 *Genome Biol* 19:217). Insulation valleys and directionality-index sign-changes give DIFFERENT boundary sets on the same matrix. The quoted "average TAD size ~880kb" is an artifact of one caller at one resolution - Zufferey explicitly states there is no average TAD size.
2. **The boundary is the reproducible, mechanistic unit.** Strong, CTCF-backed boundaries survive caller and resolution swaps; weak boundaries and exact domain extents do not. Prefer the continuous insulation/boundary-strength track over a hard domain partition for any downstream claim.
3. **The diamond window IS the analysis.** Small window (~3x bin) -> sub-TAD/fine boundaries; large window (~25x bin) -> compartment-scale domains - same matrix, totally different "TADs." Always run a list of windows and report multi-scale; never report a single-window partition as ground truth.

## TAD-Caller Taxonomy

| Method | Role | Mechanism | When |
|--------|------|-----------|------|
| cooltools `insulation` | boundary score + strength | diamond-window valleys; prominence = strength; Li/Otsu threshold | cooler-native pipeline, multi-scale, the modern default |
| HiCExplorer `hicFindTADs` | domains + boundaries + FDR | multi-window TAD-separation score with per-bin multiple-testing | CLI workflow, hierarchical sweep, FDR-controlled boundaries |
| directionality index (DI) | boundary direction | HMM on up/downstream interaction bias (Dixon 2012) | classic comparison, legacy reproducibility, gives a partition |
| Arrowhead (Juicer) | corner-score domains | arrowhead transform on the `.hic`; loop-anchored contact domains | Juicer/.hic ecosystems; calls fewer, sharper domains (Rao 2014, median ~185kb) |
| OnTAD / TADtree / rGMAP | nested/hierarchical | explicitly models meta-TADs > TADs > sub-TADs | when the question is about hierarchy or sub-TAD insulation (An 2019) |
| Stripenn / JOnTADS | stripe-aware | calls asymmetric stripes as first-class objects | when the map shows flames/stripes a flat caller mis-segments |

Insulation/DI/hicFindTADs are blind to stripes (asymmetric one-sided extrusion). Arrowhead "contact domains" are corner-anchored and categorically different from track-based boundaries - do NOT cross-compare their counts naively.

## Decision Tree by Scenario

| Scenario | Recommended | Why |
|----------|-------------|-----|
| Matrix not yet balanced | `cooler balance` / `cooler.balance_cooler` first | unbalanced insulation = coverage-driven garbage valleys |
| Reproducible boundaries, one sample | `insulation` multi-window, rank by `boundary_strength_{W}` | strength is continuous and comparable; partition is brittle |
| "What scale of domain?" | run windows `[3,5,10,25]x` bin; ~10x is the mammalian sweet spot | the window sets sub-TAD vs TAD vs compartment-domain |
| Need FDR-controlled domains | `hicFindTADs` with `--correctForMultipleTesting fdr`, sweep depths | per-bin multiple-testing on the TAD-separation score |
| Hierarchical/nested structure | OnTAD/TADtree (or compare windows) | a flat caller picks ONE level set by its window |
| Asymmetric stripes/flames present | Stripenn/JOnTADS | insulation-only pipelines are blind to stripes |
| Two conditions, boundary change | differential SCORE at matched bins, NOT intersected domain BEDs | partitions are unstable; set-differencing manufactures spurious gain/loss |
| Annotate boundaries with CTCF | -> chip-seq/peak-annotation, genome-intervals/overlap-significance | ~76-85% of boundaries are convergent CTCF + cohesin |
| Overlap boundaries with features | -> genome-intervals/interval-arithmetic | boundary BED set operations live there |
| Render domains on the matrix | -> hic-visualization | the TAD square is a colormap/resolution choice as much as a measurement |

## Insulation Score and Boundaries (multi-scale)

**Goal:** Produce a continuous boundary-strength track and threshold-flagged boundaries at several scales, so the analysis reports where insulation reproducibly dips rather than a single brittle partition.

**Approach:** Run `cooltools.insulation` on the balanced cooler with a LIST of window sizes (3-25x the bin). Each window appends its own `log2_insulation_score_{W}` (valleys = boundaries), `boundary_strength_{W}` (valley prominence - the quantitative, comparable strength), and `is_boundary_{W}` (the prominence passed through a Li histogram threshold). Rank and compare on `boundary_strength`, not on the boolean flag.

```python
import cooler
import cooltools

clr = cooler.Cooler('matrix.mcool::/resolutions/10000')   # single-resolution URI, must be balanced
res = clr.binsize
windows = [3 * res, 5 * res, 10 * res, 25 * res]   # 30k,50k,100k,250k: sub-TAD -> compartment-domain
ins = cooltools.insulation(clr, windows, verbose=True)   # clr_weight_name='weight' default -> needs ICE balancing

strong = ins[ins[f'is_boundary_{10 * res}']]   # 100kb window: ~10x bin, mammalian interphase sweet spot
ranked = ins.dropna(subset=[f'boundary_strength_{10 * res}']).sort_values(f'boundary_strength_{10 * res}', ascending=False)
```

`boundary_strength_{W}` is the scipy-style PROMINENCE of the insulation valley - continuous, quantitative, and comparable across samples; use it for ranking and cross-condition deltas. `is_boundary_{W}` is just that prominence passed through `threshold='Li'` (skimage threshold_li, an Otsu-like histogram split that is MORE PERMISSIVE than Otsu). Because the Li cutoff is fit per dataset, `is_boundary` is dataset-dependent and NOT directly comparable across samples - compare `boundary_strength`, then threshold consistently. `min_frac_valid_pixels` (default 0.66) and `min_dist_bad_bin` gate which bins get a score; sparse/blacklisted regions silently drop boundaries, so inspect `n_valid_pixels_{W}` before trusting a boundary in a low-coverage locus.

## Domains and FDR with hicFindTADs (CLI)

**Goal:** Get an FDR-controlled boundary/domain set from a multi-window TAD-separation score when a CLI workflow or hierarchical depth sweep is preferred.

**Approach:** Feed a CORRECTED (balanced) matrix and sweep the diamond depths (`--minDepth/--maxDepth/--step`); hicFindTADs computes a TAD-separation score at each depth and applies per-bin multiple-testing. The docs explicitly warn to sweep parameters before claiming a TAD count or comparing conditions.

```bash
hicFindTADs -m corrected.cool --outPrefix tads \
    --minDepth 30000 --maxDepth 100000 --step 10000 \
    --correctForMultipleTesting fdr --thresholdComparisons 0.01 --delta 0.01
# minDepth >= ~3x bin, maxDepth <= ~10x range, step >= ~2x bin; --minBoundaryDistance defaults to 4x bin
# outputs: tads_boundaries.bed, tads_domains.bed, tads_score.bedgraph, tads_tad_separation.bm, tads_zscore_matrix.h5
```

## Cross-Condition: Differential SCORE, Never Differential Partition

**Goal:** Decide which boundaries strengthen or weaken between conditions without the spurious gain/loss that comes from intersecting unstable domain calls.

**Approach:** Because partitions are unstable (caller/resolution-dependent), do NOT call TADs in each condition and set-difference the domain BEDs. Instead match resolution AND down-sample to matched valid-pixel depth, compute the bin-matched continuous insulation track at a fixed window, take the per-bin delta of `log2_insulation_score` (or `boundary_strength`), and test against a permutation/replicate null. Report boundary STRENGTHENING/WEAKENING, treating a binary boundary gain/loss as real only when strength crosses threshold robustly across replicates.

```python
ins_wt = cooltools.insulation(clr_wt, [10 * res])
ins_ko = cooltools.insulation(clr_ko, [10 * res])
key = f'log2_insulation_score_{10 * res}'
merged = ins_wt[['chrom', 'start', 'end', key]].merge(ins_ko[['chrom', 'start', 'end', key]], on=['chrom', 'start', 'end'], suffixes=('_wt', '_ko'))
merged['delta'] = merged[f'{key}_ko'] - merged[f'{key}_wt']   # negative = stronger insulation in KO; test vs a permutation null
```

Insulation (loop-extrusion barriers) and A/B compartmentalization (affinity/phase separation) are ORTHOGONAL mechanisms: CTCF degron erases insulation while compartments persist (Nora 2017 *Cell* 169:930); cohesin/RAD21 degron erases TADs+loops while compartments sharpen. Never read a boundary change as a compartment switch - a boundary can sit mid-compartment.

## Per-Method Failure Modes

### Insulation on an unbalanced matrix
**Trigger:** `insulation` on a cooler with no stored `weight` (or `clr_weight_name=None`). **Mechanism:** the diamond sum is dominated by per-bin coverage bias, not topology. **Symptom:** valleys track sequencing depth/blacklist, not domains. **Fix:** `cooler balance` first; keep the default `clr_weight_name='weight'`.

### Single magic window reported as "the TADs"
**Trigger:** calling `insulation` with one `window_bp` and treating its partition as ground truth. **Mechanism:** the window IS the scale dial; one window picks one level of a nested hierarchy. **Symptom:** sub-TAD or compartment-domain structure invisible; "TAD count" irreproducible. **Fix:** sweep `[3,5,10,25]x` bin and report multi-scale; pick the scale that matches the biological question.

### Differential partition (intersecting domain BEDs)
**Trigger:** calling TADs per condition and set-differencing the domain files. **Mechanism:** partitions are unstable, so set differences manufacture changes that are caller noise. **Symptom:** large "gained/lost TAD" lists that do not replicate. **Fix:** differential on the continuous bin-matched insulation/boundary-strength track with a permutation null.

### Window smaller than ~3x bin
**Trigger:** `window_bp < 3 * binsize`. **Mechanism:** the diamond spans too few pixels to average out noise. **Symptom:** dense spurious boundaries, no biological structure. **Fix:** set window >= 3x bin (10x is the mammalian sweet spot).

### Comparing is_boundary across samples
**Trigger:** counting `is_boundary` True in two libraries and subtracting. **Mechanism:** the Li threshold is fit per dataset; depth/strength-distribution differences shift the cutoff. **Symptom:** apparent boundary gain/loss driven by depth, not biology. **Fix:** compare continuous `boundary_strength`, then threshold consistently.

### Boundary dropped in a sparse locus
**Trigger:** a boundary expected in a low-coverage/blacklisted region is missing. **Mechanism:** `min_frac_valid_pixels` (0.66) and `min_dist_bad_bin` gate scoring; sparse diamonds get NaN. **Symptom:** no boundary where the biology predicts one. **Fix:** inspect `n_valid_pixels_{W}`; raise `min_dist_bad_bin` near bad bins or interpret cautiously.

### chrom-name mismatch (chr1 vs 1)
**Trigger:** cooler uses `chr1`, a phasing/annotation track uses `1`. **Mechanism:** chromosomes never match. **Symptom:** empty/zero output, no error. **Fix:** harmonize names across cooler, fasta, and CTCF/feature tracks.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| TAD/insulation resolution 10-40kb | domain scale | sub-Mb domains; bins must resolve boundaries without burning depth |
| Window 3-25x bin (sweep) | Open2C insulation notebook | <3x = noise; 25x = compartment-domain scale; the window is the scale dial |
| ~10x bin single window | mammalian interphase convention | e.g. 100kb window at 10kb bins for interphase TAD boundaries |
| `min_frac_valid_pixels` 0.66 | cooltools default | min valid-pixel fraction in a diamond for the bin to score |
| `threshold='Li'` | cooltools default | permissive (vs Otsu) histogram split; dataset-dependent, NOT cross-sample comparable |
| hicFindTADs depths: minDepth >=3x bin, step >=2x bin | HiCExplorer docs | the diamond depths must straddle real domain sizes; sweep before comparing |
| ~76-85% boundaries are CTCF (convergent) | Rao 2014; Vietri Rudan 2015 | strength scales with CTCF+cohesin occupancy; a sanity anchor, not a filter |
| match resolution + valid-pixel depth before gain/loss | resolution-confound | unequal depth shifts boundaries and merges sub-TADs; a false-positive engine |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| `insulation` output all NaN | cooler not balanced | `cooler balance` / `cooler.balance_cooler` first |
| KeyError on `.mcool` / wrong resolution | bare `.mcool` passed | use `file.mcool::/resolutions/<bp>` URI |
| Dense spurious boundaries | window < ~3x bin | raise `window_bp` to >= 3x bin (10x typical) |
| Boundary counts differ wildly between samples | comparing `is_boundary` (per-dataset Li threshold) | compare continuous `boundary_strength`, threshold consistently |
| Spurious "gained/lost TADs" | differential on intersected domain partitions | differential on the continuous bin-matched score with a null |
| Empty result / missing boundary | chrom naming mismatch or sparse locus | harmonize names; inspect `n_valid_pixels_{W}` |
| `AttributeError` on cooltools call | pre-0.7 vs 0.7+ API change | `help(cooltools.insulation)`; update to the viewframe signature |

## References

- Dixon JR et al. 2012. Topological domains in mammalian genomes identified by analysis of chromatin interactions. *Nature* 485:376-380.
- Nora EP et al. 2012. Spatial partitioning of the regulatory landscape of the X-inactivation centre. *Nature* 485:381-385.
- Crane E et al. 2015. Condensin-driven remodelling of X chromosome topology during dosage compensation. *Nature* 523:240-244. (Introduced the diamond-window insulation score.)
- Rao SSP et al. 2014. A 3D map of the human genome at kilobase resolution reveals principles of chromatin looping. *Cell* 159:1665-1680. (Arrowhead contact domains; convergent CTCF.)
- Fudenberg G et al. 2016. Formation of chromosomal domains by loop extrusion. *Cell Rep* 15:2038-2049.
- Forcato M et al. 2017. Comparison of computational methods for Hi-C data analysis. *Nat Methods* 14:679-685.
- Nora EP et al. 2017. Targeted degradation of CTCF decouples local insulation of chromosome domains from genomic compartmentalization. *Cell* 169:930-944.
- Bintu B et al. 2018. Super-resolution chromatin tracing reveals domains and cooperative interactions in single cells. *Science* 362:eaau1783.
- Vian L et al. 2018. The energetics and physiological impact of cohesin extrusion. *Cell* 173:1165-1178. (Architectural stripes from one-sided extrusion.)
- Zufferey M, Tavernari D, Oricchio E, Ciriello G. 2018. Comparison of computational methods for the identification of topologically associating domains. *Genome Biol* 19:217.
- An L, Yang T, Yang J et al. 2019. OnTAD: hierarchical domain structure reveals the divergence of activity among TADs and boundaries. *Genome Biol* 20:282.
- Lupianez DG et al. 2015. Disruptions of topological chromatin domains cause pathogenic rewiring of gene-enhancer interactions. *Cell* 161:1012-1025.
- Vietri Rudan M, Barrington C, Henderson S et al. 2015. Comparative Hi-C reveals that CTCF underlies evolution of chromosomal domain architecture. *Cell Rep* 10(8):1297-1309.
- Open2C, Abdennur N, Abraham S, Fudenberg G, Flyamer IM, Galitsyna AA et al. 2024. Cooltools: enabling high-resolution Hi-C analysis in Python. *PLoS Comput Biol* 20:e1012067.
- Ramirez F et al. 2018. High-resolution TADs reveal DNA sequences underlying genome organization in cells. *Nat Commun* 9:189. (HiCExplorer.)

## Related Skills

- matrix-operations - Balancing and O/E that insulation scoring depends on
- hic-data-io - Load and access the cooler files this skill operates on
- compartment-analysis - The orthogonal Mb-scale mechanism; a boundary is not a compartment switch
- loop-calling - Convergent-CTCF loops anchor the strongest boundaries; stripes need a stripe-aware caller
- hic-differential - Replicate-aware cross-condition contact comparison
- hic-visualization - Render domains/boundaries on the contact matrix
- chip-seq/peak-annotation - Annotate boundaries with CTCF/cohesin peaks
- genome-intervals/interval-arithmetic - Overlap boundary BEDs with features
- genome-intervals/overlap-significance - Test boundary/CTCF co-localization against a matched null
<!-- END FILE: hi-c-analysis/tad-detection/SKILL.md -->

<!-- END CATEGORY: hi-c-analysis -->

