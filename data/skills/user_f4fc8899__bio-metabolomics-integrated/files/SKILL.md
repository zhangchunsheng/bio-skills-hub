---
slug: bio-metabolomics-integrated
version: 1.0.1
displayName: "代谢组学 / Metabolomics"
name: bio-metabolomics-integrated
summary: "中文：代谢组学综合技能，整合 9 个相关专题，覆盖代谢组学：LC-MS特征检测、代谢物注释（MSI置信度）、QC漂移校正、差异统计、通路映射。 English: Integrated Metabolomics skill covering 9 related topics, including Metabolomics: LC-MS feature detection, metabolite annotation (MSI confidence), QC/drift correction, differential statistics, pathway mapping."
description: "中文：这是一个面向代谢组学的综合生物信息学 Skill，整合当前分类下 9 个相关专题能力。它用于根据研究问题、数据类型和分析阶段，选择合适的方法与工具，规划从输入检查、预处理、核心分析到质量控制、统计解释和结果报告的完整流程。重点覆盖：代谢组学：LC-MS特征检测、代谢物注释（MSI置信度）、QC漂移校正、差异统计、通路映射。当用户提供相关实验数据、测序结果、表格或研究问题时，它会帮助判断分析目标与前置条件，给出工具选择、关键参数、输入输出、常见失败原因、结果解读和可复现建议。主要工具包括：MetaboAnalystR, isocor, lipidr。该 Skill 提供分析设计与实施指导，不替代对具体数据质量、生物学背景和最终结论的人工审查。 English: This is an integrated bioinformatics Skill for Metabolomics, combining 9 related topic areas. It helps users choose appropriate methods and tools based on the research question, data type, and analysis stage, and plan an end-to-end workflow from input validation and preprocessing through core analysis, quality control, statistical interpretation, and reporting. It covers Metabolomics: LC-MS feature detection, metabolite annotation (MSI confidence), QC/drift correction, differential statistics, pathway mapping. For relevant experimental data, sequencing results, tables, or research questions, it clarifies prerequisites, recommends tools and parameters, describes expected inputs and outputs, explains common failure modes, and supports reproducible analysis. Primary tools include: MetaboAnalystR, isocor, lipidr. It provides methodological and implementation guidance; final data-quality assessment and biological conclusions still require human review."
---

# metabolomics 分类 Skill 整合版

> 本文件整合同一主分类目录下 9 个子目录中的 SKILL.md 内容。
> 各子目录正文按原文保留，并通过标题和边界标记进行区分；源文件中的元数据块未被改写。

---

<!-- BEGIN CATEGORY: metabolomics -->

## 子目录：metabolomics/isotope-tracing

<!-- BEGIN FILE: metabolomics/isotope-tracing/SKILL.md -->
---
name: bio-metabolomics-isotope-tracing
description: Designs and analyzes stable-isotope-resolved metabolomics (SIRM / isotope tracing / fluxomics) experiments that measure metabolic ACTIVITY via 13C/15N/2H tracers, distinct from steady-state pool profiling. Covers tracer choice, isotopologue vs isotopomer, mass-isotopomer distributions (MID), fractional enrichment, the mandatory natural-abundance + tracer-purity correction (IsoCor, AccuCor), and the metabolic/isotopic steady-state vs non-stationary (INST-MFA) distinction. Use when feeding a labeled tracer and interpreting labeling patterns, correcting raw isotopologue intensities, computing or plotting an MID, or deciding tracing vs abundance profiling. For absolute pool concentration and MRM mechanics see metabolomics/targeted-analysis; for constraint-based genome-scale flux (FBA, not empirical tracing) see systems-biology/flux-balance-analysis; for feature detection see metabolomics/xcms-preprocessing; for pathway enrichment that ignores the pool-vs-flux caveat see metabolomics/pathway-mapping.
tool_type: python
primary_tool: isocor
---

## Version Compatibility

Reference examples tested with: isocor 2.2+, numpy 1.26+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Isotope Tracing / Stable-Isotope-Resolved Metabolomics

**"What is this pathway actually doing, not just how much metabolite is there?"** -> Feed a labeled tracer, then measure how label propagates into downstream metabolites as a mass-isotopomer distribution (MID) over time.
- Python: `isocor.mscorrectors.MetaboliteCorrectorFactory().correct()` (IsoCor) for natural-abundance correction
- R: `accucor::natural_abundance_correction()` (AccuCor) for high-resolution correction
- Modeling layer (separate discipline): `INCA`, `13CFLUX2`, `OpenFLUX` for 13C-MFA / INST-MFA flux fitting

## The Single Most Important Insight -- Labeling Reports Flux; Pool Size Does Not

A metabolite's concentration is *how much* is there; its labeling pattern (MID) is *where the carbon came from and how fast it got there*. These are independent measurements and frequently move in OPPOSITE directions: block a downstream-consuming enzyme and the intermediate pool rises (it backs up) while the labeling of downstream products falls (flux through them dropped). Reading the pool alone reports the opposite of the biology. An isotope-tracing experiment therefore answers a fundamentally different question than untargeted or targeted abundance profiling, and its analysis is dominated by two mandatory corrections that fabricate flux if skipped: natural-abundance / tracer-purity correction (raw isotopologue areas are NOT the labeling), and the steady-state assumption (a single MID is a snapshot whose meaning depends on whether labeling has plateaued). Fractional enrichment is concentration-independent (it is a ratio within one pool), which is why it survives the recovery/matrix problems that plague absolute quant -- but it says nothing about amount.

## Core Concepts

| Term | Meaning | Why it matters |
|---|---|---|
| Tracer / tracee | The labeled substrate fed (tracer, e.g. U-13C6-glucose) vs the unlabeled endogenous pool (tracee) | The experiment measures how tracer atoms replace tracee atoms over time |
| Isotopologue | A molecule differing only in number of heavy atoms (M+0, M+1, M+2 ...) | Resolved by MASS; this is what MS measures and what an MID counts |
| Isotopomer | Same number of heavy atoms but at different POSITIONS (e.g. 1-13C vs 6-13C lactate) | Resolved by POSITION; needs NMR or positional tracers, NOT mass spectra alone |
| MID (mass-isotopomer distribution) | The fractional vector of M+0, M+1, ... for one metabolite | The primary readout; its shape encodes which route carbon took |
| Fractional / mean enrichment | Weighted-mean labeled-atom fraction = sum(i * MID_i) / n_atoms | One-number summary of how labeled a pool is; concentration-independent |
| Atom transitions | The map of which substrate carbons land on which product carbons per reaction | Defines the expected MID for each pathway; the basis of flux models |
| Metabolic steady state | Pool sizes constant in time | Required for classical MFA; if pools drift, plateau MIDs do not give fluxes |
| Isotopic steady state | Labeling has equilibrated to a stable plateau | Classical MFA reads fluxes from the plateau; sampling before it is invalid |

## Decision Tree by Scenario

| Goal / situation | Do | Why |
|---|---|---|
| Want amount/concentration, units, biomarker level | Use abundance profiling -> metabolomics/targeted-analysis | Pool size is not flux; tracing cannot give a concentration |
| Want pathway ACTIVITY/route, central carbon metabolism | 13C tracing (U-13C6-glucose, 13C5-glutamine); measure MIDs | Labeling reports flux through the route the carbon took |
| Trace nitrogen handling (transamination, urea, nucleotides) | 15N tracer (e.g. 15N2-glutamine, 15N-ammonia) | N-flux is invisible to a 13C tracer |
| Distinguish two carbon entry points into one pool | Positional / partially-labeled tracer (e.g. 1,2-13C2-glucose) | The M+1 vs M+2 split of products separates PPP from glycolysis |
| Fast-labeling small pools, cultured cells, clear metabolic steady state | Steady-state 13C-MFA from plateau MIDs (INCA, 13CFLUX2) | Plateau labeling + atom transitions -> flux estimates |
| Slow labeling, large pools, autotrophs, primary/quiescent cells | INST-MFA from the labeling TIME COURSE (INCA) | Drops the isotopic-steady-state assumption; fits transient + pool sizes |
| Have raw isotopologue areas (low-res QqQ / high-res Orbitrap) | Natural-abundance + purity correction FIRST (IsoCor / AccuCor) | Uncorrected MID is wrong by construction; see below |
| Want genome-scale predicted flux without a tracer | systems-biology/flux-balance-analysis | FBA is constraint-based prediction, NOT empirical label measurement |

## Natural-Abundance + Tracer-Purity Correction (mandatory)

**Goal:** Turn raw measured isotopologue areas into a true MID that reflects only tracer-derived label.

**Approach:** Even a fully unlabeled molecule shows an M+1, M+2 ladder because ~1.07% of carbon is naturally 13C (plus 15N, 2H, 18O, 34S, and derivatization Si). Build the natural-abundance ladder from the molecular (and derivative) formula, deconvolve it out, then correct for the tracer not being 100% isotopically pure. Feeding uncorrected areas to a flux model is the equivalent of reporting an uncalibrated peak area as a concentration.

```python
import isocor

# corrector knows the formula's natural-abundance ladder and the tracer
corrector = isocor.mscorrectors.MetaboliteCorrectorFactory(
    'C6H12O6', tracer='13C',
    correct_NA_tracer=True,           # also strip the labeled element's own natural abundance
    tracer_purity=[0.01, 0.99])       # [unlabeled, labeled] per-position purity of the tracer

# raw measured areas M+0..M+6 for a partially labeled glucose pool
corrected_area, iso_fraction, residuum, mean_enrichment = corrector.correct(
    [50000., 8000., 12000., 3000., 1500., 6000., 25000.])
# iso_fraction is the corrected MID; mean_enrichment is fractional enrichment
```

High-resolution Orbitrap data resolves 13C from 15N/2H by exact mass, enabling a different (often simpler) correction; AccuCor (R) is tuned for that case:

```r
library(accucor)
# El-MAVEN / MAVEN isotopologue table; Resolution is the instrument resolving power
corrected <- natural_abundance_correction(path = 'elmaven_export.xlsx',
                                          resolution = 100000, purity = 0.99)
```

Pick the corrector by tracer count and resolution: IsoCor handles any tracer at any resolution; AccuCor (single tracer) and AccuCor2 (dual 13C-15N / 13C-2H) target high-res. Verify the chosen tool's current argument names before running -- both APIs drift across versions.

## Computing and Plotting an MID / Fractional Enrichment

**Goal:** Summarize a corrected isotopologue vector as an MID and one fractional-enrichment number, comparably across conditions.

**Approach:** Normalize corrected areas to sum 1 (the MID), then take the atom-weighted mean over isotopologue index divided by the number of tracer atoms.

```python
import numpy as np

corrected = np.array([26000., 2200., 5600., 1200., 500., 2300., 12500.])
mid = corrected / corrected.sum()                              # M+0..M+n fractions
fractional_enrichment = np.sum(np.arange(len(mid)) * mid) / (len(mid) - 1)
# stacked-bar MID per condition is the standard visualization; never plot raw (uncorrected) areas
```

## Steady-State Check (does the labeling number mean anything yet?)

**Goal:** Decide whether a measured MID may be read as flux-informative or is still a kinetic transient.

**Approach:** Sample labeling at several timepoints; isotopic steady state is reached when the MID stops changing (plateau). Only plateau MIDs license classical-MFA flux inference; a rising MID is kinetic data requiring INST-MFA.

```python
import numpy as np

# fractional enrichment per timepoint (minutes) for one metabolite
t = np.array([0, 5, 15, 30, 60, 120])
fe = np.array([0.00, 0.18, 0.31, 0.39, 0.42, 0.43])
reached_plateau = abs(fe[-1] - fe[-2]) < 0.02     # <2% change between last points = plateau
# if not reached_plateau: the pool is still labeling -> use the full time course (INST-MFA), not one point
```

## Per-Method Failure Modes

### Skipping natural-abundance correction
- **Trigger:** Reporting or modeling raw isotopologue areas straight from El-MAVEN / Skyline.
- **Mechanism:** ~1.07% natural 13C (plus 15N, 2H, derivatization Si) creates an M+1/M+2 ladder on every molecule independent of the tracer; raw M+1 is mostly natural abundance for short-chain metabolites.
- **Symptom:** Apparent labeling in unlabeled controls; inflated M+1; flux fits with tight CIs that are simply wrong.
- **Fix:** Always run IsoCor/AccuCor with the correct formula (and derivative formula for GC-MS), tracer element, and tracer purity before any interpretation.

### Assuming steady state when it is not reached
- **Trigger:** Inferring flux from a single early-timepoint MID.
- **Mechanism:** Classical MFA assumes both metabolic AND isotopic steady state; a transient MID encodes kinetics, not the flux plateau.
- **Symptom:** Fluxes that change with sampling time; large residuals; biologically implausible splits.
- **Fix:** Verify plateau across a time course, or switch to INST-MFA (INCA) which fits the transient and estimates pool sizes too.

### Tracer impurity ignored
- **Trigger:** Treating a "U-13C6" tracer as 100% labeled.
- **Mechanism:** Per-position purity is ~99%, so a fraction of tracer molecules carry a 12C, distorting the fully-labeled isotopologue; the error compounds with atom count.
- **Symptom:** Fully-labeled isotopologue (M+n) systematically under-counted; enrichment biased low.
- **Fix:** Supply the measured tracer purity to the corrector (`tracer_purity` / `purity`).

### Pool-size-vs-labeling confound
- **Trigger:** Concluding "flux changed" from a changed pool concentration (or vice versa).
- **Mechanism:** Pool and labeling are independent and can anticorrelate; a rising intermediate can mean LESS downstream flux.
- **Symptom:** Pool-based and label-based conclusions disagree; "activation" that is actually a backup.
- **Fix:** Interpret MID/enrichment for flux and concentration for amount separately; report both, never substitute one for the other.

### Quench/extraction continuing turnover
- **Trigger:** Slow quench between harvest and metabolism arrest.
- **Mechanism:** High-turnover metabolites keep reacting post-harvest, scrambling labeling before extraction.
- **Symptom:** Variable, sample-dependent MIDs; collapsed nucleotide/energy-charge metabolites.
- **Fix:** Fast cold quench (-40 to -80 C aqueous methanol/acetonitrile); standardize and minimize harvest-to-quench time.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|---|---|---|
| 13C natural abundance ~1.07% | IUPAC isotopic composition | Sets the natural-abundance ladder corrected out of every MID |
| Tracer purity ~99% per position | Vendor U-13C specs | Must be supplied to correction; compounds with atom count |
| Isotopic-steady-state = <~2% MID change between timepoints | Convention | Below this, plateau reached; classical MFA licensed |
| Quench at -40 to -80 C aqueous organic | Quenching literature (convention) | Arrests metabolism fast enough for high-turnover pools |
| INST-MFA when labeling is slow / pools large / autotrophic | Cheah & Young 2018 | Isotopic steady state is unreachable in time, so fit the transient |

## Common Errors

| Error / symptom | Cause | Solution |
|---|---|---|
| `correct()` length mismatch in IsoCor | Measurement vector is not n_tracer_atoms + 1 long | Pass M+0..M+n with n = count of tracer-element atoms in the formula |
| Labeling appears in unlabeled control | No natural-abundance correction | Run IsoCor/AccuCor before interpreting |
| M+n isotopologue under-reported | Tracer purity left at 1.0 | Set `tracer_purity` / `purity` to the measured value |
| GC-MS MID still wrong after correction | Derivatization atoms (TMS/TBDMS Si, extra C) omitted | Provide the derivative formula to the corrector |
| Flux estimates shift with sampling time | Isotopic steady state not reached | Use a time course + INST-MFA, not a single MID |
| `ValueError` half-defined resolution in IsoCor | Gave `mz_of_resolution`/`charge` without `resolution` | Provide all high-res parameters together or none |

## References

- Millard P, Delepine B, Guionnet M, Heuillet M, Bellvert F, Letisse F. 2019. IsoCor: isotope correction for high-resolution MS labeling experiments. *Bioinformatics* 35:4484-4487.
- Su X, Lu W, Rabinowitz JD. 2017. Metabolite Spectral Accuracy on Orbitraps. *Analytical Chemistry* 89:5940-5948.
- Clasquin MF, Melamud E, Rabinowitz JD. 2012. LC-MS Data Processing with MAVEN: A Metabolomic Analysis and Visualization Engine. *Current Protocols in Bioinformatics* 37:14.11.1-14.11.23.
- Cheah YE, Young JD. 2018. Isotopically nonstationary metabolic flux analysis (INST-MFA): putting theory into practice. *Current Opinion in Biotechnology* 54:80-87.
- Young JD. 2014. INCA: a computational platform for isotopically non-stationary metabolic flux analysis. *Bioinformatics* 30:1333-1335.
- Antoniewicz MR. 2018. A guide to 13C metabolic flux analysis for the cancer biologist. *Experimental & Molecular Medicine* 50:1-13.

## Related Skills

- metabolomics/targeted-analysis - Absolute pool quantification and MRM/SRM mechanics
- metabolomics/xcms-preprocessing - Upstream LC-MS feature detection
- metabolomics/pathway-mapping - Pathway enrichment that interprets pools, not flux
- systems-biology/flux-balance-analysis - Constraint-based predicted flux, distinct from empirical tracing
<!-- END FILE: metabolomics/isotope-tracing/SKILL.md -->

## 子目录：metabolomics/lipidomics

<!-- BEGIN FILE: metabolomics/lipidomics/SKILL.md -->
---
name: bio-metabolomics-lipidomics
description: Assigns honest lipid annotation levels, designs class-based internal-standard quantification, and runs lipid-aware differential and enrichment analysis with lipidr, guarding against in-source-fragment phantoms, sn-position over-claims, and invalid cross-class quantification. Use when naming or canonicalizing lipid species (shorthand separators, Goslin), deciding shotgun vs RP vs HILIC LC-MS, picking internal standards (SPLASH/EquiSPLASH), interpreting MS-DIAL/LipidSearch output, or comparing lipid classes. For general feature detection see metabolomics/xcms-preprocessing and metabolomics/msdial-preprocessing; for non-lipid annotation confidence see metabolomics/metabolite-annotation; for normalization/QC see metabolomics/normalization-qc; for multivariate stats see metabolomics/statistical-analysis.
tool_type: r
primary_tool: lipidr
---

## Version Compatibility

Reference examples tested with: lipidr 2.16+, pygoslin 2.0+, MS-DIAL 5+

The achievable annotation level is fixed by the acquired evidence, not the software: sn-position and double-bond localization require EAD/OzID/PB/UVPD data that routine CID never produces, and class-resolved quantification requires one isotope-labeled internal standard per class. Verify both before trusting a name or a number.

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('lipidr')` then `?function_name` to verify parameters
- Python: `pip show pygoslin` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Lipidomics Analysis

**"Analyze my lipidomics data"** -> Canonicalize names to the resolution level the evidence supports, quantify each class against its own standard, then run class/chain-aware differential and enrichment analysis.
- R: `lipidr::read_skyline()` / `as_lipidomics_experiment()`, `de_analysis()`, `lsea()`
- Nomenclature: `pygoslin` (Python) or `rgoslin` (R) for parsing/canonicalization
- Identification: MS-DIAL 5 (open) or LipidSearch (commercial) upstream

## The Single Most Important Insight -- A Lipid Name Is a Structural-Resolution Claim the Software Usually Overstates

The Liebisch/LIPID MAPS shorthand encodes, in its punctuation, exactly how much structure was measured: `PC 34:1` (space, sum composition) < `PC 16:0_18:1` (underscore, chains known) < `PC 16:0/18:1` (slash, sn-resolved) < `PC 16:0/18:1(9Z)` (double-bond position+geometry). The resolution level is a property of the evidence, not of the string. Tools manufacture overstatement three ways: a formatter that only knows `/`, an in-silico library entry authored at sn-level that a species-level match inherits, and "annotate to the nearest database structure" silently promoting a sum composition to a full structure. sn-position is almost never genuinely measured under CID, so treat every `/` as an unproven `_` until EAD/UVPD/derivatization evidence is in hand. The default rule is: when in doubt, drop a level.

## Structural-Resolution Hierarchy (Separator Semantics)

| Notation | Separator | What was measured | What may NOT be claimed |
|----------|-----------|-------------------|-------------------------|
| `PC 34:1` | space | class + total carbons:double-bonds (accurate mass + isotope + class diagnostic) | the two chains; sn; C=C position |
| `PC 16:0_18:1` | underscore `_` | the two acyl chains (MS/MS acyl losses, RT/ECN-consistent, not an in-source fragment) | which chain is sn-1 vs sn-2 |
| `PC 16:0/18:1` | slash `/` | sn-1/sn-2 assignment (EAD/UVPD/enzymatic - not a CID acyl-loss intensity guess) | C=C position/geometry |
| `PC 16:0/18:1(9Z)` | parentheses | exact double-bond position + cis/trans (OzID/PB/EAD/UVPD) | (full structure) |
| `PC O-34:1` / `PC P-34:1` | `O-` ether / `P-` plasmalogen | ether vs vinyl-ether linkage (diagnostic ion or acid-lability) | a sum composition alone cannot distinguish `P-34:1` from `O-34:2` (vinyl ether = ether + one C=C) |
| `Cer 18:1;O2/16:0` | `;O2` | sphingoid hydroxyl count (old `d18:1`) - measured, not assumed | backbone unsaturation if `d18:1` was a default rather than fragment-confirmed |

Canonicalize every name through Goslin before merging tables or querying LIPID MAPS; never string-match lipid names by hand. Goslin preserves a false `/` faithfully - it is necessary but not sufficient.

## Decision Tree by Question

| Question / situation | Approach | Why |
|----------------------|----------|-----|
| Accurate class-level quantification, high throughput | Shotgun (direct infusion) or HILIC-LC-MS | constant concentration / class bands -> clean ratio to a co-eluting class IS |
| Resolve isobars/isomers, deep low-abundance coverage | RP-LC-MS (± ion mobility) | RT axis adds an identity coordinate; co-elution flags in-source fragments |
| Double-bond position, sn-position, ether/plasmalogen | LC-MS + EAD/OzID/PB/UVPD (± IM) | only these break C=C / glycerol backbone; CID is blind to them |
| Spatial localization | MS-imaging (MS-DIAL 5 spatial mode) | tissue context with predicted-CCS database |
| Need PC acyl chains | negative-mode formate/acetate adduct -> `[M-CH3]-` | `[M+H]+` gives only the m/z 184 head-group ion (class, no chains) |
| Neutral lipids (TG/DG) chains | `[M+NH4]+` adduct | drives neutral-loss-of-fatty-acid fragmentation |
| Suspicious elevated LPC / DG / FA pool | RT co-elution test vs the parent class | an LPC eluting at a PC's RT is an in-source fragment, not biology |
| An apparent odd-chain species (`PC 33:1`) | require MS/MS chain confirmation | usually an in-source fragment or 13C-isotope artifact of an even neighbor |
| Merge names across tools / before a DB lookup | Goslin canonicalization first | abbreviations and separators are tool-specific; hand string-matching corrupts merges |
| Untargeted oxidized-lipid claim | escalate to a targeted, standard-anchored oxylipin panel | untargeted oxidized-lipid IDs are hypotheses; auto-oxidation in the tube fabricates them |

## Load, Normalize, and Run Differential Analysis (lipidr)

**Goal:** Import a quantified lipid table, normalize within class, and find lipids that differ between groups with class/chain-aware output.

**Approach:** Read a Skyline/matrix export into a `LipidomicsExperiment`, attach sample groups, normalize (PQN or class internal standard), then `de_analysis` with an explicit contrast; visualize as a class-faceted volcano.

```r
library(lipidr)

# data_normalized ships with lipidr (PQN-normalized, log2); substitute a real import:
#   d <- read_skyline(list.files(datadir, 'data.csv', full.names = TRUE))
#   d <- add_sample_annotation(d, 'clinical.csv')
#   d <- normalize_pqn(d, measure = 'Area', exclude = 'blank', log = TRUE)
data(data_normalized)

# Contrast references sample-group labels directly; group_col defaults to the first annotation
de_results <- de_analysis(data_normalized, HighFat_water - NormalDiet_water, measure = 'Area')

# logFC.cutoff is on the log2 scale used by limma's topTable inside de_analysis
sig <- significant_molecules(de_results, p.cutoff = 0.05, logFC.cutoff = 1)

plot_results_volcano(de_results, show.labels = FALSE)
```

## Class-Based Internal-Standard Quantification (the non-negotiable)

**Goal:** Convert per-class signal to comparable abundances without baking in class-dependent ionization error.

**Approach:** Ratio each species to a stable-isotope-labeled standard of its OWN class, spiked before extraction so it shares the class's recovery loss; never quantify one class with another class's standard.

```r
# normalize_istd divides each lipid by the internal standard of its matched class.
# Requires one labeled IS per class present in the data (e.g. SPLASH/EquiSPLASH covers ~13 classes).
d_istd <- normalize_istd(data_normalized, measure = 'Area', exclude = 'blank', log = TRUE)

# Class-level summary is only valid WITHIN a class unless per-class response factors were calibrated:
# cross-class molar ratios (e.g. 'PE is 3x PC') carry head-group response bias and are not licensed here.
plot_lipidclass(d_istd, 'sd')
```

## Honest Annotation-Level Assignment (Goslin)

**Goal:** Downgrade any name to the level the evidence supports and verify the claimed level is internally consistent.

**Approach:** Parse with Goslin, read the perceived level, and re-emit at SPECIES (or MOLECULAR_SPECIES) unless sn/C=C evidence exists.

```python
from pygoslin.parser.Parser import LipidParser
from pygoslin.domain.LipidLevel import LipidLevel

parser = LipidParser()
lipid = parser.parse('PC 16:0/18:1')      # a slash-claimed name from a tool export

claimed_level = lipid.lipid.info.level    # LipidLevel enum the string asserts
# Without EAD/UVPD evidence, re-emit at the honest molecular-species level (drops the unproven sn):
honest_name = lipid.get_lipid_string(LipidLevel.MOLECULAR_SPECIES)   # 'PC 16:0_18:1'
sum_name = lipid.get_lipid_string(LipidLevel.SPECIES)                # 'PC 34:1'
```

## Per-Method Failure Modes

### In-source-fragment phantom lyso-/DG-lipidome
- **Trigger:** A labile lipid (PC, TG, plasmalogen) clips an acyl chain in the ESI source before MS1.
- **Mechanism:** The fragment is recorded as an intact precursor; PC->LPC, PE->LPE, TG->DG->MG. The fragment can also be isobaric with a free fatty acid or another class, fabricating phantom signal in several bins; extent is instrument- and tune-dependent.
- **Symptom:** Inflated LPC:PC, DG:TG, or FA pools; an "LPC" eluting at a PC's retention time.
- **Fix:** RT co-elution test (a real LPC elutes at its own ECN position); soften the source (lower in-source CID/transfer energy); treat any large lyso/DG/FA pool as suspect until RT-cleared. Shotgun has no RT axis to run this test - never report elevated lyso-lipids from direct infusion without the in-source-fragment caveat.

### sn-position over-claim
- **Trigger:** A tool exports `/` from CID-only data, or a library back-fills its authored sn arrangement onto a species-level match.
- **Mechanism:** CID acyl-loss intensity bias toward sn-2 is real but small, condition-dependent, and biological samples contain both regioisomers, so the ratio is a blend, not a structure readout.
- **Symptom:** `/`-formatted names with no EAD/UVPD/derivatization evidence file attached.
- **Fix:** Canonicalize through Goslin and re-emit at `MOLECULAR_SPECIES` (`_`); at most state "dominant sn-2 likely X" while reporting `_`.

### Invalid cross-class quantification
- **Trigger:** One global internal standard, or comparing molar abundances across classes after only within-class normalization.
- **Mechanism:** ESI response is head-group-dominated; a PC and a PE at equal moles give signal differing by factors that can exceed an order of magnitude.
- **Symptom:** "Class A is N-fold class B" statements; a single IS used for the whole lipidome.
- **Fix:** One isotope-labeled IS per class; report semi-quantitative within-class unless per-class (and per-adduct) response factors were independently calibrated.

### Ether vs plasmalogen (O-/P-) mis-call
- **Trigger:** Reporting `P-` (plasmalogen) from a sum composition.
- **Mechanism:** `P-34:1` and `O-34:2` share elemental composition (vinyl ether = ether + one C=C); mass cannot distinguish them.
- **Symptom:** Plasmalogen calls with no vinyl-ether diagnostic ion or acid-lability evidence.
- **Fix:** Require a diagnostic fragment or acid-lability test; otherwise report at the level that cannot distinguish them.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| One isotope-labeled IS per lipid class | Köfeler 2021 (good practice); SPLASH/EquiSPLASH | ESI response is head-group-dominated; one global IS miscalibrates every other class |
| EquiSPLASH = 13 deuterated IS at equal 100 µg/mL | Avanti product spec | equimolar comparative use; SPLASH LIPIDOMIX uses unequal physiological concentrations |
| Spike IS before extraction | Köfeler 2021 | only a co-extracted IS corrects class-biased recovery (Folch/Bligh-Dyer/MTBE differ for polar minor classes) |
| MS-DIAL 5 EAD ~14 eV; 96.4% standards delineated, 78.0% sn/OH/C=C correct >1 µM | Takeda 2024 | structural lipidomics yield even with the modern method is incomplete and concentration-dependent |
| ~half of single-software species-level IDs need orthogonal evidence | Köfeler 2021 (Nat Commun) | 510/1108 features, 130/301 PCs & 55/171 TGs violated the ECN/RT model in an audited published set |
| LipidSearch grades: keep A/B/C, drop D | LipidSearch grade definitions | D = mass-only; A = class + all chains = molecular-species level, NOT sn/C=C resolved |
| Shotgun infusion below the aggregation regime | Han/Gross protocol literature | above it lipids aggregate, ESI response goes nonlinear, the IS-ratio assumption collapses |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| `could not find function "read_lipidomes"` | non-existent function name | use `read_skyline()` or `as_lipidomics_experiment()` |
| `plot_enrichment` rejects an `enrich.results` argument | wrong signature | `plot_enrichment(de.results, significant.sets, annotation = 'class', measure = 'logFC')`; get sets from `significant_lipidsets()` |
| `lsea(type = 'chain')` errors | no `type` argument | `lsea` tests class/length/unsat sets automatically; rank with `rank.by = c('logFC','P.Value','adj.P.Val')` |
| `de_results$FDR` is NULL | wrong column name | `de_analysis` returns limma columns: `adj.P.Val`, `P.Value`, `logFC` |
| pygoslin `LipidLevel.MOLECULAR_SUBSPECIES` AttributeError | pre-2.0 enum name | current enum is `SPECIES` / `MOLECULAR_SPECIES` / `SN_POSITION` / `STRUCTURE_DEFINED` / `FULL_STRUCTURE` / `COMPLETE_STRUCTURE` |
| Elevated LPC reported from shotgun data | in-source fragmentation with no RT to flag it | add the in-source-fragment caveat; confirm with LC-MS RT co-elution before claiming lyso biology |

## References

- Liebisch G, Vizcaíno JA, Köfeler H, et al. 2013. Shorthand notation for lipid structures derived from mass spectrometry. *J Lipid Res* 54:1523-1530.
- Liebisch G, Fahy E, Aoki J, et al. 2020. Update on LIPID MAPS classification, nomenclature, and shorthand notation for MS-derived lipid structures. *J Lipid Res* 61:1539-1555.
- Fahy E, Subramaniam S, Brown HA, et al. 2005. A comprehensive classification system for lipids. *J Lipid Res* 46:839-861.
- Kopczynski D, Hoffmann N, Peng B, Ahrends R. 2020. Goslin: A Grammar of Succinct Lipid Nomenclature. *Anal Chem* 92:10957-10960.
- Kind T, Liu KH, Lee DY, et al. 2013. LipidBlast in silico tandem mass spectrometry database for lipid identification. *Nat Methods* 10:755-758.
- Takeda H, Takahashi M, Ikeda K, et al. 2024. MS-DIAL 5 multimodal mass spectrometry data mining unveils lipidome complexities. *Nat Commun* 15:9903.
- Mohamed A, Molendijk J, Hill MM. 2020. lipidr: A Software Tool for Data Mining and Analysis of Lipidomics Datasets. *J Proteome Res* 19:2890-2897.
- Köfeler HC, Eichmann TO, Ahrends R, et al. 2021. Quality control requirements for the correct annotation of lipidomics data. *Nat Commun* 12:4771.
- Köfeler HC, Ahrends R, Baker ES, et al. 2021. Recommendations for good practice in MS-based lipidomics. *J Lipid Res* 62:100138.
- McDonald JG, Ejsing CS, Kopczynski D, et al. 2022. Introducing the Lipidomics Minimal Reporting Checklist. *Nat Metab* 4:1086-1088.
- Matyash V, Liebisch G, Kurzchalia TV, et al. 2008. Lipid extraction by methyl-tert-butyl ether for high-throughput lipidomics. *J Lipid Res* 49:1137-1146.
- Bowden JA, Heckert A, Ulmer CZ, et al. 2017. Harmonizing lipidomics: NIST interlaboratory comparison exercise for lipidomics using SRM 1950-Metabolites in Frozen Human Plasma. *J Lipid Res* 58:2275-2288.

## Related Skills

- metabolomics/xcms-preprocessing - Upstream peak detection and feature extraction
- metabolomics/msdial-preprocessing - MS-DIAL alignment and deconvolution upstream of lipid annotation
- metabolomics/metabolite-annotation - General (non-lipid) annotation and confidence levels
- metabolomics/normalization-qc - Sample normalization and QC framing
- metabolomics/statistical-analysis - Multivariate stats on the lipid abundance matrix
<!-- END FILE: metabolomics/lipidomics/SKILL.md -->

## 子目录：metabolomics/metabolite-annotation

<!-- BEGIN FILE: metabolomics/metabolite-annotation/SKILL.md -->
---
name: bio-metabolomics-metabolite-annotation
description: Turns untargeted LC-MS/MS features (m/z, RT, MS/MS) into confidence-stratified metabolite annotations using spectral-library matching (matchms), in-silico tools (SIRIUS/CSI:FingerID, MetFrag) and molecular networking, and assigns a defensible MSI/Schymanski confidence level to each. Use when naming detected features, scoring MS/MS against a reference library, running SIRIUS, or deciding what confidence level an evidence set actually supports. For upstream feature extraction see metabolomics/xcms-preprocessing and metabolomics/msdial-preprocessing; for downstream enrichment that must respect these levels see metabolomics/pathway-mapping; for lipid-specific structural annotation see metabolomics/lipidomics.
tool_type: mixed
primary_tool: matchms
---

## Version Compatibility

Reference examples tested with: matchms 0.33+, SIRIUS 6.x, MetFrag 2.5+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

Spectral matching needs precursor m/z on every MS/MS spectrum (`add_precursor_mz` filter) or ModifiedCosine silently returns zeros. Level 1 needs an authentic standard run in the same lab under the same method; no software output can substitute for it.

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Metabolite Annotation

**"Annotate my metabolomics features with compound identities"** -> Map each feature's m/z and MS/MS to candidate structures, then attach an explicit confidence level to every name.
- Python: `matchms.calculate_scores()` for library matching (matchms)
- CLI: `sirius ... formulas fingerprints structures canopus` for in-silico formula/structure/class (SIRIUS)

## The Single Most Important Insight -- An Annotation Is a Hypothesis Carrying a Confidence Level, Not an Identification

A metabolite name without a stated MSI/Schymanski level is scientifically incomplete. The inference chain m/z -> formula -> structure -> isomer-resolved identity is three separate lossy steps, each needing its own orthogonal evidence axis. A database hit supplies a name, not evidence: with no MS/MS or RT to back it, it is Schymanski Level 4 (formula) at best, often Level 5 (a feature of interest). A high cosine score ranks candidates; it never proves one. Only an in-house authentic standard, same method, with MS, MS/MS, and RT all matching reaches Level 1 ("identification") -- everything else is an honest hypothesis. The field's recurring sin is laundering Level 2/3 hypotheses into Level-1 prose; the canonical worked example is phenylacetylglutamine being reported as phenylacetylglycine in nearly half of NMR studies (Theodoridis 2023). Assign the lowest level the evidence honestly supports and report which database/version was searched.

## Confidence-Level Taxonomy (MSI and Schymanski)

| Schymanski | MSI | Name | Evidence required |
|---|---|---|---|
| Level 1 | 1 | Confirmed structure | In-house authentic standard, same method: MS + MS/MS + RT all match. The only "identification". |
| Level 2a | 2 | Probable structure (library) | MS/MS matches a reference library spectrum; no in-house standard. |
| Level 2b | 2 | Probable structure (diagnostic) | Diagnostic fragments / RT / ionization consistent with exactly one structure; no reference spectrum. |
| Level 3 | 3 | Tentative candidate(s) | Evidence narrows to a structure class or candidate set but isomers remain unresolved. |
| Level 4 | -- | Unequivocal formula | MS1 accurate mass + isotope pattern + adduct logic assign one formula; no structure. |
| Level 5 | 4 | Exact mass | A feature of interest; nothing assigned. |

Promote one level per orthogonal evidence axis that survives scrutiny; cap at Level 2 unless an in-house standard exists. CSI:FingerID and library matching recover constitution only -- no stereochemistry, so enantiomer/regiochemistry claims cannot come from MS/MS.

## Tool Roles

| Tool | Core idea | Output | Best for |
|---|---|---|---|
| matchms (CosineGreedy / ModifiedCosine / spectral entropy) | Score query MS/MS against library spectra | Ranked library hits + matched-peak count | Level 2a when a library spectrum exists |
| SIRIUS + ZODIAC | Fragmentation trees + isotope pattern, dataset-wide formula re-ranking | Ranked molecular formula | Formula (Level 4); the reliable part of SIRIUS |
| CSI:FingerID + COSMIC | Predict fingerprint, search structure DB, calibrated confidence | Ranked structures + FDR-controllable score | Level 2b/3 structure when COSMIC FDR is set |
| CANOPUS | Predict compound class directly from MS2 | ClassyFire + NPClassifier class | Level 3 class for unknowns; often the most honest output |
| MetFrag | Bond-disconnection scoring of candidate list | Explainable fragment-supported ranks | Transparent, scriptable, custom DBs, RT term |
| FBMN (GNPS2) + MS2Query | Modified-cosine network / ML analogue search | Edges = "related to" | Analogue propagation (Level 3 scaffold hypothesis) |

## Decision Tree: Evidence Available -> Tool -> Achievable Level

| Situation | Do | Achievable level |
|---|---|---|
| In-house authentic standard, same method, MS+MS/MS+RT match | Confirm against standard | Level 1 |
| MS/MS available, library spectrum likely exists | matchms library match (entropy or modified cosine) | Level 2a |
| MS/MS available, no library spectrum | SIRIUS formulas + CSI:FingerID + CANOPUS, or MetFrag | Level 2b/3 (formula Level 4) |
| Need class only / compound absent from all DBs | CANOPUS (class); MSNovelist (de novo SMILES) | Level 3 |
| Find analogues / propagate across a network | FBMN on GNPS2 + MS2Query | Level 3 (scaffold hypothesis) |
| Only MS1 m/z + isotopes + clean adduct | Formula assignment (SIRIUS / seven golden rules) | Level 4 |
| Bare m/z, no orthogonal evidence | Report as a feature | Level 5 |
| Biology hinges on a specific isomer / stereocenter | Demand a standard or orthogonal method (NMR, chiral assay) | MS alone insufficient |

## Match MS/MS Against a Spectral Library

**Goal:** Rank library candidates for each query spectrum and attach the matched-peak count, not just the score.

**Approach:** Harmonize metadata, normalize intensities, add precursor m/z, score with ModifiedCosine (analogue-aware) or spectral entropy (identity), then keep only hits above both a score and a matched-peak floor.

```python
from matchms import calculate_scores
from matchms.filtering import default_filters, normalize_intensities, add_precursor_mz
try:
    from matchms.similarity import ModifiedCosineGreedy as ModifiedCosine  # matchms 0.33+
except ImportError:
    from matchms.similarity import ModifiedCosine          # matchms <= 0.32

def prepare(spectrum):
    spectrum = default_filters(spectrum)
    spectrum = add_precursor_mz(spectrum)  # required for ModifiedCosine or scores are zero
    return normalize_intensities(spectrum)

queries = [prepare(s) for s in queries_raw]
references = [prepare(s) for s in references_raw]

scores = calculate_scores(references, queries, ModifiedCosine(tolerance=0.005))

# CosineGreedy/ModifiedCosine return a structured array; the field names are
# class-prefixed and version-dependent (e.g. 'ModifiedCosineGreedy_score' in 0.33),
# so derive them from the dtype rather than hard-coding.
for query in queries:
    pairs = scores.scores_by_query(query)
    score_field, match_field = pairs[0][1].dtype.names
    ref, hit = max(pairs, key=lambda pair: pair[1][score_field])
    if hit[score_field] >= 0.7 and hit[match_field] >= 6:  # score floor + peak-count floor (GNPS defaults)
        print(ref.get('compound_name'), hit[score_field], hit[match_field])  # Level 2a candidate
```

## Run SIRIUS for Formula, Structure, and Class

**Goal:** Annotate features that have no library spectrum, reporting formula and class with more trust than top-1 structure.

**Approach:** Run the SIRIUS subcommand chain on one project space; trust ZODIAC-refined formula over CSI:FingerID structure, and only report a structure as confident when a COSMIC FDR threshold is set.

```bash
# SIRIUS 6 is a multi-command pipeline on one line. A free academic account/license
# is required (since v5); log in once, then the project space persists across runs.
# Credential flags vary by version; run `sirius login --help` to confirm (commonly `-u <email>`).
sirius login -u "$SIRIUS_USER"

sirius --input features.mgf --project ./sirius_project \
    formulas --profile orbitrap \
    fingerprints \
    structures --database bio \
    canopus \
    write-summaries --output ./sirius_summary
# Verify exact subcommand spelling with `sirius <command> --help`: formulas/fingerprints/
# structures/canopus changed plural/singular and options between v5 and v6.
# --database (on structures) is a scientific choice: 'bio' raises plausibility but cannot
# return a novel metabolite; 'pubchem' maximizes recall but floods implausible isomers.
```

## Assemble an Evidence-to-Level Call

**Goal:** Collapse a feature's evidence set into a single defensible confidence level.

**Approach:** Start at Level 5 and promote per surviving orthogonal axis; an authentic standard is the only path to Level 1.

```python
def assign_level(evidence):
    if evidence.get('authentic_standard_same_method'):
        return 1
    if evidence.get('library_match') and evidence['library_match']['score'] >= 0.7 and evidence['library_match']['matches'] >= 6:
        return '2a'  # reference library spectrum, no in-house standard
    if evidence.get('diagnostic_fragments') and evidence.get('single_structure_consistent'):
        return '2b'
    if evidence.get('candidate_set') or evidence.get('canopus_class') or evidence.get('network_propagated'):
        return 3  # isomers unresolved, class only, or "related to" an annotated node
    if evidence.get('unambiguous_formula'):
        return 4  # MS1 + isotopes + adduct logic, no structure
    return 5
```

## Per-Method Failure Modes

### Cosine score is not identity
- **Trigger:** Reporting a name because a single high cosine/modified-cosine score came back.
- **Mechanism:** Cosine rewards shared fragment peaks, and fragments are substructures many distinct molecules share; a high score on few peaks aligns with thousands of unrelated compounds.
- **Symptom:** Confident name that an isomer or scaffold-sharing compound would have produced identically.
- **Fix:** Require a matched-peak floor (>=6) alongside the score (>=0.7); prefer spectral entropy for identity; report Level 2a, not Level 1.

### The isomer wall
- **Trigger:** Claiming a specific positional/stereo/regio isomer from MS/MS.
- **Mechanism:** Constitutional isomers frequently fragment identically; enantiomers have near-identical CID spectra; CSI:FingerID is constitution-only.
- **Symptom:** A specific structure reported where multiple isomers fit the data equally.
- **Fix:** Report Level 3 unless RT or CCS breaks the tie (CCS needs ~0.5-0.6% separation); for biology hinging on the isomer, use NMR or a co-eluting standard.

### In-source fragments and adduct cascades corrupt the input
- **Trigger:** Annotating and counting features before collapsing ion families.
- **Mechanism:** In-source fragmentation creates phantom MS1 features; assuming the wrong adduct shifts the neutral mass and corrupts every downstream candidate, producing a confident, internally consistent, wrong answer.
- **Symptom:** Over-counted "compounds", the same molecule named several ways, invented biology.
- **Fix:** Group ion families (CAMERA / Ion Identity Molecular Networking / khipu) before annotation; never quote feature counts as compound counts.

### Database-mapping inflation poisons pathway analysis
- **Trigger:** Feeding all candidate IDs of an ambiguous feature into enrichment.
- **Mechanism:** One ambiguous m/z maps to many compound IDs across different pathways, so a single uncertain feature lights up several pathways (phantom enrichment).
- **Symptom:** Inflated pathway significance traceable to Level-3 features voting as if they were several confirmed compounds.
- **Fix:** Carry annotation uncertainty (candidate sets, levels) into enrichment; prefer mass-level or probabilistic methods that do not multiply ambiguous IDs (see metabolomics/pathway-mapping; mummichog deliberately avoids prior ID).

## Quantitative Thresholds

| Threshold | Source | Rationale |
|---|---|---|
| Cosine/modified-cosine >= 0.7 AND >= 6 matched peaks | GNPS defaults (Wang 2016) | Suppresses promiscuous low-complexity spectra that hairball the network. |
| Spectral entropy >= 0.75 -> FDR < 10% | Li 2021 (natural-products benchmark) | Dataset-dependent, NOT a universal constant; entropy beats dot product for identity. |
| MS1 mass error <= 5 ppm (HRMS) | HRMS convention | Tighter than the 10 ppm older default; pairs with isotope-pattern filter. |
| Isotope-pattern ~2% abundance accuracy | Kind & Fiehn 2006 | Removes >95% of false formula candidates even at 3 ppm -- orthogonal info, not better mass accuracy, fixes formula. |
| COSMIC 0.94 / 0.64 / 0.34 ~ 5 / 10 / 20% FDR | Hoffmann 2022 | Calibrated confidence on CSI:FingerID structures; raw top-1 with no COSMIC is Level 3. |
| Predicted CCS within ~3-5% of measured | AllCCS / IMS benchmarks (Zhou 2020) | Use CCS as a falsifier (rejects candidates), not as positive proof of identity. |

## Common Errors

| Error / symptom | Cause | Solution |
|---|---|---|
| ModifiedCosine scores all zero | Missing precursor m/z on spectra | Apply `add_precursor_mz` filter to both references and queries first. |
| `AttributeError: 'Scores' has no attribute 'scores'` | Indexing `scores.scores[...]` (old tutorials) | Use `scores.scores_by_query(query)` or `scores.to_array(name=...)`. |
| `ValueError: no field of name <X>_score` | Field names are class-prefixed and version-dependent | Read `pair[1].dtype.names` for the score/matches field names rather than hard-coding. |
| `ImportError: cannot import name 'ModifiedCosine'` | Renamed to `ModifiedCosineGreedy` in matchms 0.33 | Try the new name with an ImportError fallback to the old. |
| `sirius formula` not found | v5 used singular subcommands; v6 uses `formulas` | Run `sirius --help`; verify plural/singular per installed version. |
| SIRIUS exits at login | Account/license required since v5 | `sirius login` once with a free academic account before the chain. |
| Pathway enrichment lights up everywhere | Ambiguous features mapped to many DB IDs | Collapse ion families and carry levels into enrichment (metabolomics/pathway-mapping). |

## References

- Sumner LW, et al. 2007. Proposed minimum reporting standards for chemical analysis (CAWG MSI). *Metabolomics* 3:211-221.
- Schymanski EL, Jeon J, Gulde R, Fenner K, Ruff M, Singer HP, Hollender J. 2014. Identifying small molecules via high resolution mass spectrometry: communicating confidence. *Environ Sci Technol* 48:2097-2098.
- Li Y, Kind T, Folz J, Vaniya A, Mehta SS, Fiehn O. 2021. Spectral entropy outperforms MS/MS dot product similarity for small-molecule compound identification. *Nat Methods* 18:1524-1531.
- Dührkop K, Fleischauer M, Ludwig M, Aksenov AA, Melnik AV, Meusel M, Dorrestein PC, Rousu J, Böcker S. 2019. SIRIUS 4: a rapid tool for turning tandem mass spectra into metabolite structure information. *Nat Methods* 16:299-302.
- Dührkop K, Shen H, Meusel M, Rousu J, Böcker S. 2015. Searching molecular structure databases with tandem mass spectra using CSI:FingerID. *PNAS* 112:12580-12585.
- Dührkop K, et al. 2021. Systematic classification of unknown metabolites using high-resolution fragmentation mass spectra (CANOPUS). *Nat Biotechnol* 39:462-471.
- Hoffmann MA, et al. 2022. High-confidence structural annotation of metabolites absent from spectral libraries (COSMIC). *Nat Biotechnol* 40:411-421.
- Ruttkies C, Schymanski EL, Wolf S, Hollender J, Neumann S. 2016. MetFrag relaunched: incorporating strategies beyond in silico fragmentation. *J Cheminform* 8:3.
- Wang M, Carver JJ, Phelan VV, et al. 2016. Sharing and community curation of mass spectrometry data with GNPS. *Nat Biotechnol* 34:828-837.
- Nothias LF, Petras D, Schmid R, et al. 2020. Feature-based molecular networking in the GNPS analysis environment. *Nat Methods* 17:905-908.
- Kind T, Fiehn O. 2006. Metabolomic database annotations via query of elemental compositions: mass accuracy is insufficient even at less than 1 ppm. *BMC Bioinformatics* 7:234.
- Zhou Z, et al. 2020. Ion mobility collision cross-section atlas for known and unknown metabolite annotation in untargeted metabolomics (AllCCS). *Nat Commun* 11:4334.
- Theodoridis G, Gika H, Raftery D, Goodacre R, Plumb RS, Wilson ID. 2023. Ensuring fact-based metabolite identification in LC-MS-based metabolomics. *Anal Chem* 95:3909-3916.
- Huber F, Verhoeven S, Meijer C, et al. 2020. matchms - processing and similarity evaluation of mass spectrometry data. *J Open Source Softw* 5:2411.

## Related Skills

- metabolomics/xcms-preprocessing - Upstream feature extraction (m/z, RT, intensity table)
- metabolomics/msdial-preprocessing - Alternative feature extraction and deconvolution
- metabolomics/pathway-mapping - Downstream enrichment that must respect these confidence levels
- metabolomics/lipidomics - Lipid-specific annotation and structural resolution
- proteomics/spectral-libraries - Related spectral-matching concepts (closed-world peptide search)
<!-- END FILE: metabolomics/metabolite-annotation/SKILL.md -->

## 子目录：metabolomics/msdial-preprocessing

<!-- BEGIN FILE: metabolomics/msdial-preprocessing/SKILL.md -->
---
name: bio-metabolomics-msdial-preprocessing
description: Runs the MS-DIAL preprocessing workflow (peak picking, MS2Dec spectral deconvolution, alignment, gap-filling) and imports the alignment-result table into R or Python with honest filtering. Use when preprocessing LC-MS DDA/DIA (SWATH) raw data with MS-DIAL, deciding MS-DIAL vs XCMS, configuring the MsdialConsoleApp console run, or parsing an MS-DIAL export into a clean feature matrix. For programmatic R peak detection and the feature-table-as-artifact framing see metabolomics/xcms-preprocessing; for lipid annotation mode see metabolomics/lipidomics; for MSI-level confidence honesty see metabolomics/metabolite-annotation; for drift correction and QC see metabolomics/normalization-qc.
tool_type: mixed
primary_tool: msdial
---

## Version Compatibility

Reference examples tested with: MS-DIAL 5.x (LC-MS) / MS-DIAL 4.x (GC-MS), pandas 2.2+, R 4.3+

Before using code patterns, verify installed versions match. If versions differ:
- CLI: run `MsdialConsoleApp` with no arguments to print the current subcommand/flag list
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters
- Python: `pip show pandas` then `help(module.function)` to check signatures

The MS-DIAL GUI runs only on Windows; the console (MsdialConsoleApp) is the cross-platform headless entry. Which build supports a task is itself a constraint: MS-DIAL 5-alpha covers DI-MS, IM-MS, LC-MS, LC-IM-MS but NOT GC-MS - GC-EI stays in the MS-DIAL 4 lineage. If code throws ImportError, AttributeError, or TypeError, introspect the installed package and adapt rather than retrying.

# MS-DIAL Preprocessing

**"Process my LC-MS run with MS-DIAL and give me a feature table"** -> Pick peaks per file, deconvolve chimeric MS/MS into clean component spectra (MS2Dec), align across samples, gap-fill, then import the alignment result and filter it honestly.
- CLI: `MsdialConsoleApp lcmsdda|lcmsdia|gcms -i <in> -o <out> -m <param.txt>`
- R: `read.csv(..., skip = 4, check.names = FALSE)` to parse the alignment export
- Python: `pandas.read_csv(..., skiprows=4)` for the same export

## The Single Most Important Insight -- Preprocessing Software Is Not Neutral

The same raw files through MS-DIAL versus XCMS yield different feature tables and different marker lists. Li 2018 benchmarked five tools on a 1,100-compound standard and found that while feature *detection* was broadly similar, *quantification* and the set of selected discriminating markers differed by tool. A metabolomics "hit" is conditional on (raw data + software + version + every parameter + fill/filter order), not on the raw files alone. MS-DIAL's specific differentiator is **MS2Dec deconvolution**: it reconstructs clean, library-matchable MS/MS spectra from chimeric DDA/DIA fragment data, which is what makes wide-window DIA (SWATH) tractable at all. Report the full processing specification as part of the result, and treat a finding that survives only one pipeline as a candidate, not a result.

## MS-DIAL vs XCMS

| Axis | MS-DIAL | XCMS |
|---|---|---|
| Interface | Windows GUI + cross-platform console | R package (scriptable everywhere) |
| Core differentiator | MS2Dec MS/MS deconvolution (DDA + DIA) | centWave peak picking, full programmatic control |
| Annotation | Built-in (library + MS-FINDER + LipidBlast) | Separate (CAMERA, downstream tools) |
| Lipidomics | Strong (predicted-CCS / EAD structural elucidation in v5) | Manual |
| Reproducibility unit | Param file + GUI choices | Versioned R script |
| Best when | DIA data, lipidomics, GUI workflow, built-in IDs | Scripted pipelines, custom parameters, cohort scale |

Use MS-DIAL when DIA deconvolution or built-in lipid annotation is the point; use metabolomics/xcms-preprocessing for fully scripted, version-pinned cohort processing. The strongest untargeted claims replicate across both.

## Decision Tree by Scenario

| Situation | Do | Why |
|---|---|---|
| LC-MS, top-N MS/MS (DDA) | `lcmsdda` console / GUI LC-MS DDA | Cleaner per-precursor MS2, but intensity-biased, stochastic coverage |
| LC-MS, wide-window MS/MS (DIA / SWATH) | `lcmsdia` (ABF input only) | Complete MS2 coverage; chimeric spectra REQUIRE MS2Dec to be usable |
| GC-EI run | `gcms` (MS-DIAL 4 build), or AMDIS/eRah | EI fragments every co-eluting compound; deconvolution IS detection (see below) |
| Headless / Linux cluster | MsdialConsoleApp with a `-m` param file | GUI is Windows-only; console is the reproducible batch path |
| Lipid-focused study | MS-DIAL + LipidBlast | -> metabolomics/lipidomics for lipid annotation mode |
| Already have an alignment CSV | skip processing, parse + filter | See import + honest-filter sections below |

## Why GC-EI Is Different (and stays in MS-DIAL 4)

In GC-EI, 70 eV ionization fragments every compound reproducibly, so the trace at any retention time is a superposition of fragments from several co-eluting molecules. Naive peak picking conflates them; **deconvolution into component spectra IS the feature-detection step**, then each component is matched against EI+RI libraries (NIST, FiehnLib). Cross-run/cross-lab alignment uses **retention index** (Kovats n-alkanes, or Fiehn FAME markers giving diagnostic m/z 74/87) rather than raw RT, because RT drifts with column aging. MS-DIAL 5-alpha explicitly excludes GC-MS; use the `gcms` token in a MS-DIAL 4 build, or AMDIS/eRah, for GC-EI work.

## Run MS-DIAL Headless (console)

**Goal:** Process a folder of converted spectra into an alignment table without the GUI.

**Approach:** Pick the analysis-type token, point `-i`/`-o`/`-m` at input dir, output dir, and a method (parameter) file; keep `-p` only if the project should reopen in the GUI.

```bash
# DDA LC-MS: accepts netCDF/mzML/ABF. Output is *.msdial in the output dir.
MsdialConsoleApp lcmsdda -i ./LCMS_DDA/ -o ./LCMS_DDA_out/ -m ./Msdial-lcms-dda-Param.txt

# DIA/SWATH LC-MS: accepts ABF ONLY (convert vendor raw -> ABF first). MS2Dec is the point.
MsdialConsoleApp lcmsdia -i ./LCMS_DIA/ -o ./LCMS_DIA_out/ -m ./Msdial-lcms-dia-Param.txt

# GC-EI (MS-DIAL 4 build): retention-index alignment, quant-mass quantification.
MsdialConsoleApp gcms -i ./GCMS/ -o ./GCMS_out/ -m ./Msdial-GCMS-Param.txt -p
```

The parameter file is plain text (one `Key=Value` per line). The `Minimum peak height` key is the direct analog of an intensity floor and is instrument-dependent: the GUI default is tuned for a TOF and is often far too high (or its baseline assumption wrong) for an Orbitrap. Set the alignment reference to a pooled QC, never to file #1 by default.

## Import the Alignment Result into R

**Goal:** Split the MS-DIAL alignment export into a feature-metadata frame and an intensity matrix.

**Approach:** The export carries four header rows above the real column header (sample class / file type / injection order / batch), so skip them; metadata columns precede the per-sample Area columns.

```r
# MS-DIAL alignment export: real column header is on row 5, so skip the first 4 rows.
msdial <- read.csv('AlignResult.txt', sep = '\t', skip = 4, check.names = FALSE)

# Metadata columns appear before the per-sample intensity columns. Common ones:
# 'Alignment ID', 'Average Rt(min)', 'Average Mz', 'Metabolite name', 'Adduct type',
# 'Fill %', 'MS/MS assigned', 'Reference RT', 'Formula', 'Ontology', 'INCHIKEY',
# 'SMILES', 'Annotation tag (VS1.0)'. Sample columns are everything after these.
meta_cols <- c('Alignment ID', 'Average Rt(min)', 'Average Mz', 'Metabolite name',
               'Adduct type', 'Fill %', 'MS/MS assigned', 'Annotation tag (VS1.0)')
meta_cols <- intersect(meta_cols, colnames(msdial))
sample_cols <- setdiff(colnames(msdial), colnames(msdial)[seq_len(max(match(meta_cols, colnames(msdial))))])

feature_info <- msdial[, meta_cols]
intensity <- as.matrix(msdial[, sample_cols])
rownames(intensity) <- msdial[['Alignment ID']]
```

## Import the Alignment Result into Python

**Goal:** Same split, in pandas.

**Approach:** `skiprows=4` to land on the real header; slice metadata vs sample columns by position after the last known metadata column.

```python
import pandas as pd

msdial = pd.read_csv('AlignResult.txt', sep='\t', skiprows=4)
meta_cols = ['Alignment ID', 'Average Rt(min)', 'Average Mz', 'Metabolite name', 'Adduct type', 'Fill %', 'MS/MS assigned', 'Annotation tag (VS1.0)']
meta_cols = [c for c in meta_cols if c in msdial.columns]
last_meta = max(msdial.columns.get_loc(c) for c in meta_cols)
sample_cols = msdial.columns[last_meta + 1:]

feature_info = msdial[meta_cols].copy()
intensity = msdial[sample_cols].set_axis(msdial['Alignment ID']) if False else msdial[sample_cols].copy()
intensity.index = msdial['Alignment ID']
```

## Filter the Table Honestly

**Goal:** Keep features supported by real signal and known confidence, without overtrusting annotation tags.

**Approach:** Filter on Fill% (cross-sample presence), require MS/MS support for any feature called identified, and tie the annotation tag to a real MSI confidence level rather than treating a name as proof.

```r
# Fill% is the fraction of samples with a DETECTED (not gap-filled) peak. Low Fill% means
# the feature exists mostly as gap-filled noise-floor integrals, which fabricate intensity
# (an honest 'below detection' becomes a positive number). 70% is a common floor.
keep_fill <- feature_info[['Fill %']] >= 70

# An annotated name without MS/MS is at best an MSI Level 2/3 putative ID (accurate mass
# only). Require 'MS/MS assigned == TRUE' before trusting any identity downstream.
has_msms <- feature_info[['MS/MS assigned']] == 'TRUE'

# Annotation tag confidence (do NOT treat a name as an identification). The exact tag
# vocabulary is MS-DIAL-version-dependent, so inspect unique(feature_info[['Annotation tag (VS1.0)']])
# and map the strings the build actually emits rather than hard-coding them:
#   Metabolite / Lipid  with MS/MS  -> MSI Level 2 (spectral library match)
#   Suggested*          mass-only   -> MSI Level 3 (putative, no MS/MS)
#   Unknown                         -> unannotated feature
feature_info$msi_level <- ifelse(feature_info[['Annotation tag (VS1.0)']] %in% c('Metabolite', 'Lipid') & has_msms, 2,
                          ifelse(grepl('^Suggested', feature_info[['Annotation tag (VS1.0)']]), 3, NA))

filtered <- intensity[keep_fill, ]
```

Confidence-level honesty and orthogonal-evidence identification belong to metabolomics/metabolite-annotation; this skill only routes the tag to the right level. Fill% / blank / drift filtering interacts with normalization-qc - process blanks and pooled QCs through the SAME run, then filter the aligned table.

## Per-Method Failure Modes

### DIA processed as DDA (wrong console token)
- **Trigger:** Running SWATH/DIA data through `lcmsdda`.
- **Mechanism:** `lcmsdda` does not deconvolve wide-isolation chimeric MS/MS, so fragments from co-isolated precursors stay mixed.
- **Symptom:** Library matches to the wrong compound; "clean-looking" spectra that fail orthogonal confirmation.
- **Fix:** Use `lcmsdia` (ABF input only); MS2Dec deconvolution is the entire reason to run DIA in MS-DIAL.

### Over-trusting the annotation tag
- **Trigger:** Filtering on `Annotation tag != Unknown` and calling the survivors "identified."
- **Mechanism:** A `Suggested*` tag is an accurate-mass guess with no MS/MS; a named hit without MS/MS is MSI Level 3.
- **Symptom:** A marker list full of confident-sounding names that do not validate against standards.
- **Fix:** Require `MS/MS assigned == TRUE` for any identity claim; map tags to MSI levels (see filtering section) and defer to metabolomics/metabolite-annotation.

### Gap-fill masquerading as measurement
- **Trigger:** Treating low-Fill% features as quantitative.
- **Mechanism:** Gap-filling integrates whatever signal sits in the m/z-RT box even when no peak exists, turning a true below-detection (MNAR, left-censored) value into a positive number.
- **Symptom:** "Significant" features that are mostly gap-filled in one group; shrunken fold-changes for on/off markers.
- **Fix:** Report per-feature filled fraction; gate on Fill%; for inferential stats prefer MNAR-aware imputation over naive fill (see metabolomics/normalization-qc).

### GC-EI run through an LC pipeline / MS-DIAL 5
- **Trigger:** Sending GC-EI data to MS-DIAL 5-alpha or treating it like LC peak-pick-then-group.
- **Mechanism:** MS-DIAL 5-alpha excludes GC-MS; EI needs component deconvolution, not adduct-style peak picking, and RI (not RT) alignment.
- **Symptom:** No GC mode available; or conflated co-eluting compounds and cross-lab RT misalignment.
- **Fix:** Use the `gcms` token in a MS-DIAL 4 build (or AMDIS/eRah); align on Kovats/FAME retention index.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|---|---|---|
| Fill% >= 70% | Common untargeted practice | Below this, the feature is mostly gap-filled noise-floor integrals, not measurements |
| QC CV (RSD) < 20-30% | Broadhurst 2018 | Technical reproducibility floor; drop features noisier than this in pooled QCs |
| D-ratio (sd_QC/sd_sample) < 0.5 | Broadhurst 2018 | Keeps features whose technical variance is well below biological variance |
| Blank filter: sample mean > 3-5x blank mean | Broadhurst 2018 | Removes background/contaminant features present in process blanks |
| ~10x more features than compounds | Mahieu 2017 | One metabolite makes adducts/isotopes/fragments; counting features over-counts hypotheses |

## Common Errors

| Error / symptom | Cause | Solution |
|---|---|---|
| All columns land in one field on import | Header offset wrong; tab-separated export read as CSV | `skip=4` (R) / `skiprows=4` (Python), set `sep='\t'` |
| `lcmsdia` rejects mzML input | DIA mode accepts ABF only | Convert vendor raw to ABF (Reifycs ABF converter) before `lcmsdia` |
| `Annotation tag` column not found | Header changes across versions (e.g. `Annotation tag (VS1.0)`) | Match by prefix / inspect `colnames()`; do not hard-code the suffix |
| No GC-MS option in MS-DIAL 5 | 5-alpha excludes GC-MS | Use a MS-DIAL 4 build's `gcms` token, or AMDIS/eRah |
| Console command not found on Linux | Expecting the GUI executable | The GUI is Windows-only; run `MsdialConsoleApp` (cross-platform) |
| Few features detected | `Minimum peak height` default too high for the instrument | Lower it toward the real baseline; defaults are TOF-tuned |

## References

- Tsugawa H, Cajka T, Kind T, Ma Y, Higgins B, Ikeda K, Kanazawa M, VanderGheynst J, Fiehn O, Arita M. MS-DIAL: data-independent MS/MS deconvolution for comprehensive metabolome analysis. *Nat Methods.* 2015; 12(6):523-526.
- Tsugawa H, Ikeda K, Takahashi M, et al. A lipidome atlas in MS-DIAL 4. *Nat Biotechnol.* 2020; 38(10):1159-1163.
- Takeda H, Takahashi M, Ikeda K, et al. MS-DIAL 5 multimodal mass spectrometry data mining unveils lipidome complexities. *Nat Commun.* 2024; 15:9903.
- Li Z, Lu Y, Guo Y, Cao H, Wang Q, Shui W. Comprehensive evaluation of untargeted metabolomics data processing software in feature detection, quantification and discriminating marker selection. *Anal Chim Acta.* 2018; 1029:50-57.
- Mahieu NG, Patti GJ. Systems-level annotation of a metabolomics data set reduces 25,000 features to fewer than 1,000 unique metabolites. *Anal Chem.* 2017; 89(19):10397-10406.
- Broadhurst D, Goodacre R, Reinke SN, Kuligowski J, Wilson ID, Lewis MR, Dunn WB. Guidelines and considerations for the use of system suitability and quality control samples in mass spectrometry assays applied in untargeted clinical metabolomic studies. *Metabolomics.* 2018; 14(6):72.
- Stein SE. An integrated method for spectrum extraction and compound identification from gas chromatography/mass spectrometry data (AMDIS). *J Am Soc Mass Spectrom.* 1999; 10(8):770-781.

## Related Skills

- metabolomics/xcms-preprocessing - Programmatic R preprocessing and the feature-table-as-artifact framing
- metabolomics/lipidomics - Lipid annotation mode and LipidBlast workflows
- metabolomics/metabolite-annotation - MSI confidence levels and orthogonal-evidence identification
- metabolomics/normalization-qc - Drift correction, QC/CV/D-ratio filtering, MNAR-aware imputation
<!-- END FILE: metabolomics/msdial-preprocessing/SKILL.md -->

## 子目录：metabolomics/normalization-qc

<!-- BEGIN FILE: metabolomics/normalization-qc/SKILL.md -->
---
name: bio-metabolomics-normalization-qc
description: Designs QC, corrects signal drift, removes batch effects, filters features, normalizes samples, and imputes missing values for untargeted LC-MS/GC-MS metabolomics, framing each step as a measurement model that can create or erase biological signal. Use when processing a peak/feature table before statistical analysis, choosing a drift-correction or sample-normalization method, deciding QC RSD vs D-ratio filtering, or handling left-censored missing values. The feature table is produced by metabolomics/xcms-preprocessing or metabolomics/msdial-preprocessing; transformation/scaling for modeling defers to metabolomics/statistical-analysis; cross-study design issues link to experimental-design/batch-design.
tool_type: r
primary_tool: pmp
---

## Version Compatibility

Reference examples tested with: pmp 1.14+, statTarget 1.30+, imputeLCMD 2.1+, missForest 1.5+, sva 3.50+

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters

Valid drift correction requires QC injections that bracket the samples at both ends and sample the drift curve (~1 QC every 5-10 injections); conditioning injections must be excluded. Valid batch correction requires biological groups randomized across batches; a confounded design cannot be rescued by any algorithm.

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Metabolomics Normalization and QC

**"Normalize my metabolomics data and correct for batch effects"** -> Filter junk features by QC quality, correct within-batch drift against injection order, normalize per-sample dilution, and impute by missingness mechanism -- each step verified against held-out QCs, not just QC clustering.
- R drift correction: `QCRSC()` (pmp), `shiftCor()` (statTarget)
- R normalization: `pqn_normalisation()` (pmp)
- R imputation: `mv_imputation()` (pmp), `impute.QRILC()` (imputeLCMD), `missForest()` (missForest)

## The Single Most Important Insight -- Normalization Is a Modeling Decision, Not a Cleanup Step

Every preprocessing step imposes an assumption about where the *unwanted* variance lives; if that assumption is wrong the result is not noisier, it is confidently wrong. Three corollaries reorganize the whole skill. (1) QC-based correction assumes the pooled QC's per-feature drift trajectory *is* the samples' trajectory -- false for subgroup-specific features (the pool dilutes them toward absence) and for features at different abundance in samples vs pool (suppression is concentration-dependent), so correcting them extrapolates from noise. (2) The order/batch/biology confound is information-theoretically unwinnable post hoc: if group is collinear with batch or injection order, no estimator can attribute the shared variance to one source -- it only redistributes it, wrongly. Randomization at the bench is the only real fix. (3) Over-correction is invisible to the metric everyone reports: "QC RSD dropped / QCs cluster tighter" is exactly what a too-flexible model games (a cubic spline threading every QC drives QC RSD to ~0% while raising biological-sample RSD). Validate on held-out QCs and dilution-QC linearity, never on the metric the model optimized.

## The Four Orthogonal Operations (Do Not Conflate)

| Operation | Acts on | Removes | Methods |
|---|---|---|---|
| Drift / signal correction | each feature, within a batch, vs injection order | longitudinal intensity decay/rise (column fouling, sensitivity loss) | QC-RLSC (LOESS), QCRSC (spline), QC-RFSC (RF vs order), SERRF (RF across correlated features) |
| Batch correction | each feature, across batches | step-changes between analytical batches | QC-anchored median/reference alignment; ComBat (reserved, dangerous) |
| Sample normalization | each sample (column) | dilution / total-amount differences | PQN, MSTUS, TIC/sum, median, internal standard |
| Transformation / scaling | each feature (row) | mean-variance dependence; range dominance | log/glog; Pareto/auto -> defers to metabolomics/statistical-analysis |

TIC normalization does not handle drift, and -- because of closure -- can spread one feature's change across all others. Keep the axes separate.

## Pipeline Order (and Why Order Matters)

| # | Step | Why here | Tool |
|---|---|---|---|
| 0 | Exclude conditioning injections | Pre-equilibrium signal warps a LOESS edge and corrupts RSD/blank filters | manual (drop first ~8 QC) |
| 1 | Blank filter -> detection-rate filter | Removes background/contaminant and mostly-absent features before any model trains on them | `filter_peaks_by_blank`, `filter_peaks_by_fraction` (pmp) |
| 2 | Within-batch drift correction | Flattens order-dependent trend per feature before cross-sample comparison | `QCRSC` (pmp), `shiftCor` (statTarget) |
| 3 | QC RSD / D-ratio filter | Drift correction *should* improve RSD; filter after so reproducibility reflects corrected data (report both stages) | `filter_peaks_by_rsd` (pmp), `dratio_filter` (structToolbox) |
| 4 | Between-batch alignment | QC-anchored offsets removed after within-batch drift is flat | median-of-QC / batchCorr |
| 5 | Missing-value imputation | Filter aggressively first, then impute only the sparse residual holes by mechanism | `mv_imputation` (pmp), `impute.QRILC`, `missForest` |
| 6 | Sample normalization | Dilution correction on quality features, after junk removed | `pqn_normalisation` (pmp) |
| 7 | Transformation + scaling | Defers to metabolomics/statistical-analysis | `glog_transformation` (pmp) |

Detection-rate filtering must precede imputation: never impute a feature that is 90% missing, which would fabricate 90% of it.

## Decision Tree -- Sample Normalization by Matrix

| Matrix / situation | Use | Why |
|---|---|---|
| Urine / variable-dilution biofluid | PQN or MSTUS (osmolality/SG if measured) | Dilution varies wildly; PQN's median-quotient isolates the common dilution factor; MSTUS excludes drug/diet xenobiotics that corrupt TIC |
| Plasma / serum | PQN or median (TIC only if no dominant peak) | Volume relatively constant; closure risk lower but still present |
| Tissue / cells | Per measured amount (mass, protein, cell count) at the bench | The confounder (input amount) is known -- more honest than any data-driven post-hoc method |
| Targeted / few analytes | Per-class internal standards | One IS cannot represent all chemical classes/RT regions |
| Global profile genuinely differs between groups | Avoid quantile normalization | It forces all samples to one distribution, erasing real distributional biology |
| Creatinine for urine | Avoid as sole method | Fails under renal impairment / muscle-mass differences (Warrack 2009) |

When >50% of features move coherently (potent drug, gross pathology), the PQN median-quotient measures the biology, not dilution, and subtracts it out -- switch to a measured external quantity and check whether the normalization factor correlates with the phenotype.

## Decision Tree -- Drift Correction Method

| Situation | Do | Why |
|---|---|---|
| Smooth monotonic drift, frequent QCs, small/medium study | QCRSC (spline) or QC-RLSC | Per-feature fit vs order; CV-select span to avoid overfit |
| Non-smooth / multi-pattern drift within a batch | QC-RFSC (statTarget) or batchCorr clusters | RF / cluster-based captures non-monotonic trend |
| Large cohort (>~500), complex multi-source error, want lowest RSD | SERRF | Borrows strength across correlated features (~5% RSD on >800-sample cohorts, Fan 2019) |
| Sparse QCs (<5-6 spanning the batch) | Coarse median-of-QC offset or no within-batch correction | LOESS/spline with too few QCs produces gaps/garbage |
| Feature weak/absent in QCs | Exclude from correction | Correcting it extrapolates from noise |
| No detectable drift in a feature | Do not correct it | Correcting a flat QC trajectory only adds the model's wiggle |
| Run order confounded with biology | Do not drift-correct; fix design or caveat | A smooth function of order absorbs and subtracts the biological trend |

Flexible ML methods (SERRF/RF/adversarial) win on large complex cohorts but are *more* prone to learning-and-removing biology that tracks order/batch. Always confirm QC RSD dropped AND biological-sample RSD did not rise.

## Filter Features by QC Quality (RSD and D-ratio)

**Goal:** Keep only reproducible features whose technical variance is small relative to biological variance.

**Approach:** Compute per-feature QC RSD and the robust D-ratio (technical SD / biological SD), then apply a boolean mask. Lead with D-ratio: CV alone is matrix-blind, scoring a precisely-measured-but-flat feature as good and a noisy-but-biologically-huge feature as bad.

```r
library(matrixStats)

robust_dratio_filter <- function(data, is_qc, dratio_max = 0.5, rsd_max = 0.3) {
    qc <- as.matrix(data[is_qc, ])
    bio <- as.matrix(data[!is_qc, ])
    # MAD-based (robust) form, because MS intensities are right-skewed
    sd_qc <- colMads(qc, na.rm = TRUE)
    sd_bio <- colMads(bio, na.rm = TRUE)
    dratio <- sd_qc / sd_bio
    rsd <- colSds(qc, na.rm = TRUE) / colMeans(qc, na.rm = TRUE)
    keep <- dratio <= dratio_max & rsd <= rsd_max
    keep[is.na(keep)] <- FALSE
    message(sprintf('D-ratio<=%.2f & RSD<=%.0f%%: kept %d / %d features',
                    dratio_max, rsd_max * 100, sum(keep), ncol(data)))
    data[, keep]
}
```

## Correct Within-Batch Drift (QC-RSC)

**Goal:** Flatten per-feature, injection-order-dependent signal drift using the QC trajectory.

**Approach:** Fit a QC-robust smoothing spline of intensity vs injection order per feature, interpolate at every sample position, and divide. pmp's `QCRSC` selects the spline smoothing by leave-one-out CV when `spar=0`, requires `minQC` QCs per batch, and excludes features too weak in QC automatically.

```r
library(pmp)

# df: features in ROWS, samples in COLUMNS (pmp convention)
corrected <- QCRSC(df = feature_matrix, order = injection_order, batch = batch_id,
                   classes = sample_class, spar = 0, log = TRUE,
                   minQC = 5, qc_label = 'QC')
# Verify correction worked on HELD-OUT QCs / dilution linearity, not on QC clustering.
```

statTarget alternative (`MLmethod='QCRFSC'` for RF, `'QCRLSC'` for LOESS; `QCspan=0` auto-GCV span applies to QCRLSC; inputs are two order-aligned CSVs):

```r
library(statTarget)
shiftCor(samPeno = 'meta.csv', samFile = 'peaks.csv', Frule = 0.8,
         MLmethod = 'QCRFSC', ntree = 500, QCspan = 0, degree = 2,
         imputeM = 'KNN', coCV = 30, plot = FALSE)
```

## Normalize Per-Sample Dilution (PQN)

**Goal:** Remove per-sample global intensity differences (dilution, extraction efficiency) without subtracting genuine fold changes.

**Approach:** Build a reference spectrum (median of QCs), compute per-feature sample/reference quotients, take the median quotient as the dilution factor, and divide. The median is robust because it ignores the minority of genuinely-changed features.

```r
library(pmp)
# df: features in ROWS, samples in COLUMNS; reference built from QC samples
normalized <- pqn_normalisation(df = feature_matrix, classes = sample_class,
                                qc_label = 'QC')
```

## Impute by Missingness Mechanism

**Goal:** Fill residual sparse holes with the method matched to *why* the value is missing.

**Approach:** Diagnose the mechanism per feature -- missingness correlated with low abundance is MNAR (left-censored) and needs QRILC/GSimp; sporadic missingness across the abundance range is MAR and needs RF/kNN. Using a MAR method on MNAR zeros pulls the censored group's mean up and erases the on/off signal.

```r
library(imputeLCMD)
library(missForest)

# MNAR / left-censored: random draws from a fitted truncated-normal (features in ROWS)
qrilc_imputed <- impute.QRILC(feature_matrix_features_in_rows, tune.sigma = 1)[[1]]

# MAR / sporadic: iterative random-forest prediction (samples in ROWS, features in COLS)
rf_imputed <- missForest(sample_by_feature_matrix, maxiter = 10, ntree = 100)$ximp
```

Half-min imputation collapses the imputed subset's variance to zero, understating SE and inflating false significance -- prefer QRILC/GSimp, which draw a distribution of plausible low values. Re-run key results under >=2 imputation methods; if headline metabolites flip, the finding lives in the imputation.

## Per-Method Failure Modes

### QC-spline / LOESS over-correction
- **Trigger:** Span too small, too few QCs, or a cubic spline using each QC as a lock-point.
- **Mechanism:** The fit threads the QCs perfectly, modeling inter-QC noise as drift and injecting it into samples.
- **Symptom:** QC RSD drops toward 0% while biological-sample RSD rises and the number of significant features explodes.
- **Fix:** CV-select the span, validate on held-out QCs and dilution-QC linearity, compare biological-sample RSD before/after, not just QC RSD.

### Edge extrapolation
- **Trigger:** Samples injected before the first QC or after the last QC.
- **Mechanism:** LOESS/spline interpolate between QCs but extrapolate beyond them, producing unstable correction factors.
- **Fix:** Bracket samples with QCs at both ends; exclude conditioning injections.

### TIC closure artifact
- **Trigger:** One dominant or up-regulated feature under TIC/sum normalization.
- **Mechanism:** The constant-sum constraint forces every other feature's normalized value down, manufacturing apparent coordinated down-regulation (Aitchison closure; spurious negative correlations).
- **Fix:** Use PQN/MSTUS or log-ratios; if "many features moved together," suspect closure from one big mover before believing coordination.

### ComBat under imbalance
- **Trigger:** Biological groups unbalanced across batches.
- **Mechanism:** Empirical-Bayes shrinkage confounds class with batch; under imbalance it can fabricate thousands of false differences or, without the covariate, delete real ones (Nygaard 2016).
- **Fix:** Prefer QC-anchored between-batch alignment (the pool has no group, so it cannot confound). Reserve ComBat for balanced designs and always pass the biological covariate via `mod=`. Randomize so it is never needed.

### Wrong imputation mechanism
- **Trigger:** kNN/RF applied to below-LOD (MNAR) values.
- **Mechanism:** MAR methods borrow abundance from detected samples, pulling the censored group's mean up and shrinking the very difference under test.
- **Fix:** Diagnose mechanism per feature; QRILC/GSimp for left-censored, RF/kNN only for sporadic MAR.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|---|---|---|
| QC RSD <= 20-30% (15% gold) | Dunn 2011; Broadhurst 2018 | Reproducibility floor in the matrix-matched pool; 20% aspirational for LC-MS, 30% common |
| D-ratio <= 0.5 (0.2 excellent), robust/MAD form | Broadhurst 2018 | Technical SD < biological SD -- the honest, matrix-aware filter; MAD form because MS intensities are right-skewed |
| Blank ratio >= 3-5x | community convention (Dunn lineage) | Features below 3-5x blank are dominated by background/carryover, not biology |
| Detection rate >= 50-80% (or 80% within any one group) | statTarget Frule=0.8; pmp filter_peaks_by_fraction | Reliable signal; "within any group" preserves on/off group-specific metabolites |
| Dilution-QC correlation r >= 0.7-0.8 | community convention | Real metabolites scale with dilution; artefacts/in-source ions do not |
| QCs >= 5-10% of injections, ~1 every 5-10 samples | Broadhurst 2018; mQACC 2022 | Must sample the drift curve densely enough to avoid LOESS extrapolation |

Thresholds are conventions, not laws: choose them a priori, report each one, and report how many features each filter removed (mQACC reporting standard).

## Common Errors

| Error / symptom | Cause | Solution |
|---|---|---|
| `could not find function "statTarget"` | No such entry point | Use `shiftCor()` (drift correction) and `statAnalysis()` (post-hoc stats) |
| `mv_imputation` errors on `method='sm'` | Small-value method is `'sv'`, not `'sm'` | Use `method='sv'` (also valid: `knn`, `rf`, `bpca`, `mn`, `md`) |
| QRILC output is malformed | `impute.QRILC` returns a list, not a matrix; expects features in rows | Index `[[1]]`; transpose so features are rows |
| MetaboAnalystR `Normalization` errors | `SanityCheckData(mSet)` not run first | Call `SanityCheckData` -> `ReplaceMin` -> `Normalization` in order |
| Correction made data worse | Span overfit / weak-in-QC features corrected / order confounded with biology | Back off span, exclude weak-in-QC features, check randomization |
| Effect vanished after drift correction | Run order confounded with group; trend absorbed the biology | Check the design; report drift and effect as inseparable if confounded |

## References

- Dunn WB, Broadhurst D, Begley P, et al. 2011. Procedures for large-scale metabolic profiling of serum and plasma using gas chromatography and liquid chromatography coupled to mass spectrometry. *Nature Protocols* 6:1060-1083.
- Broadhurst D, Goodacre R, Reinke SN, et al. 2018. Guidelines and considerations for the use of system suitability and quality control samples in mass spectrometry assays applied in untargeted clinical metabolomic studies. *Metabolomics* 14:72.
- Dieterle F, Ross A, Schlotterbeck G, Senn H. 2006. Probabilistic Quotient Normalization as Robust Method to Account for Dilution of Complex Biological Mixtures. Application in 1H NMR Metabonomics. *Analytical Chemistry* 78:4281-4290.
- Fan S, Kind T, Cajka T, et al. 2019. Systematic Error Removal Using Random Forest for Normalizing Large-Scale Untargeted Lipidomics Data. *Analytical Chemistry* 91:3590-3596.
- Brunius C, Shi L, Landberg R. 2016. Large-scale untargeted LC-MS metabolomics data correction using between-batch feature alignment and cluster-based within-batch signal intensity drift correction. *Metabolomics* 12:173.
- Luan H, Ji F, Chen Y, Cai Z. 2018. statTarget: A streamlined tool for signal drift correction and interpretations of quantitative mass spectrometry-based omics data. *Analytica Chimica Acta* 1036:66-72.
- Wei R, Wang J, Su M, et al. 2018. Missing Value Imputation Approach for Mass Spectrometry-based Metabolomics Data. *Scientific Reports* 8:663.
- Wei R, Wang J, Jia E, et al. 2018. GSimp: A Gibbs sampler based left-censored missing value imputation approach for metabolomics studies. *PLoS Computational Biology* 14:e1005973.
- Stekhoven DJ, Buhlmann P. 2012. MissForest -- non-parametric missing value imputation for mixed-type data. *Bioinformatics* 28:112-118.
- Nygaard V, Rodland EA, Hovig E. 2016. Methods that remove batch effects while retaining group differences may lead to exaggerated confidence in downstream analyses. *Biostatistics* 17:29-39.
- van den Berg RA, Hoefsloot HCJ, Westerhuis JA, et al. 2006. Centering, scaling, and transformations: improving the biological information content of metabolomics data. *BMC Genomics* 7:142.
- Warrack BM, Hnatyshyn S, Ott KH, et al. 2009. Normalization strategies for metabonomic analysis of urine samples. *Journal of Chromatography B* 877:547-552.
- Thonusin C, IglayReger HB, Soni T, et al. 2017. Evaluation of intensity drift correction strategies using MetaboDrift, a normalization tool for multi-batch metabolomics data. *Journal of Chromatography A* 1523:265-274.
- Chamberlain CA, Rubio VY, Garrett TJ. 2019. Impact of matrix effects and ionization efficiency in non-quantitative untargeted metabolomics. *Metabolomics* 15:135.
- Wehrens R, Hageman JA, van Eeuwijk F, et al. 2016. Improved batch correction in untargeted MS-based metabolomics. *Metabolomics* 12:88.

## Related Skills

- metabolomics/xcms-preprocessing - Generates the feature table this skill consumes
- metabolomics/msdial-preprocessing - Alternative feature-table source
- metabolomics/statistical-analysis - Transformation/scaling and downstream multivariate stats
- experimental-design/batch-design - Randomization and design that make correction valid
- differential-expression/batch-correction - ComBat/SVA mechanics shared with transcriptomics
<!-- END FILE: metabolomics/normalization-qc/SKILL.md -->

## 子目录：metabolomics/pathway-mapping

<!-- BEGIN FILE: metabolomics/pathway-mapping/SKILL.md -->
---
name: bio-metabolomics-pathway-mapping
description: Maps metabolomics results to biological pathways via over-representation (ORA), metabolite-set enrichment (MSEA/QEA), mummichog/PSEA on raw m/z peaks, and network-diffusion enrichment (FELLA), with correct background-set construction and honest interpretive ceilings. Use when interpreting differential metabolites or an untargeted LC-MS feature table in pathway context, choosing ORA vs MSEA vs mummichog vs topology, or setting the reference/background set. For annotation confidence levels feeding ORA see metabolomics/metabolite-annotation; for gene-set concepts see pathway-analysis/go-enrichment and pathway-analysis/gsea; for joint gene+metabolite pathways see multi-omics-integration/mofa-integration.
tool_type: r
primary_tool: MetaboAnalystR
---

## Version Compatibility

Reference examples tested with: MetaboAnalystR 4.0+, FELLA 1.22+

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters

The single most important input fact: whether the metabolites are confidently identified (KEGG/HMDB IDs) determines which method is even possible. An untargeted LC-MS feature table with no IDs cannot run ORA; it requires mummichog/PSEA. Verify the input type before choosing a tool.

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Metabolomics Pathway Mapping

**"Map my metabolites to pathways"** -> Test whether a metabolite set or an m/z feature table is statistically enriched for biochemical pathways, given an explicit background.
- Identified compound list -> ORA / MSEA: `CalculateOraScore()` (MetaboAnalystR)
- Raw m/z peak table (no IDs) -> mummichog / PSEA: `PerformPSEA()` (MetaboAnalystR)
- Mechanism (which enzymes/reactions link the hits) -> network diffusion: `runDiffusion()` (FELLA)

## The Single Most Important Modern Insight -- Pathway Enrichment Launders Annotation Uncertainty Into Confident Biology

Enrichment is the one workflow step where uncertainty is structurally destroyed: compounds enter as names with no error bars, and the hypergeometric/permutation machinery cannot represent "this is a 40%-confident guess." A pile of MSI-level-3 tentative annotations emerges as a p-value with three decimals. Wieder 2021 simulated this directly: even a 4% misidentification rate manufactured both false-positive and false-negative pathways across five real datasets, and real untargeted annotation is far worse than 4%. The errors do not average out, because a single wrong hub-adjacent compound (alanine, glutamate, a TCA intermediate) can flip a pathway by itself. No untargeted pathway claim can be stronger than its annotation layer. The honest ceiling is "features consistent with perturbation of pathway X co-varied with phenotype, conditional on the chosen annotations, background, database boundary, and ionization settings" -- never "pathway X is upregulated."

## Two Starting Points -> Method -> Tool

The field's most common category error is conflating identified-compound enrichment with raw-feature activity prediction. They are disjoint entry points.

| Input | Goal / situation | Method | Tool | Key constraint |
|---|---|---|---|---|
| Identified compounds + cutoff | Discrete "significant" hit list | ORA (hypergeometric) | MetaboAnalystR `CalculateOraScore` | Background = compounds the assay could detect, NOT all of KEGG |
| Identified compounds + ranked stat | No natural cutoff; keep magnitude | MSEA / QEA (rank-aware) | MetaboAnalystR `CalculateQeaScore` | Needs a meaningful, complete ranking |
| Raw m/z + RT + per-feature stat, NO IDs | Predict pathway activity, bypass ID | mummichog / GSEA-PSEA | MetaboAnalystR `PerformPSEA` | Background = the FULL feature table (R_all); declare ionization mode |
| Identified compounds | Mechanism: which enzymes/reactions link hits | Network diffusion | FELLA `runDiffusion` | KEGG IDs only; check `getExcluded()` for unmapped |
| Identified compounds | Database coverage is the bottleneck | Chemical-structure clustering | ChemRICH (background-independent) | Sidesteps pathway dark matter |
| Any | Secondary lens only | Topology / "impact" | MetaboAnalystR (MetPA) | Hub artifact; never sole evidence |

Mummichog exists because identification is the rate-limiter: only ~2-10% of untargeted features are ever confidently identified. It predicts network activity directly from the feature table, then the network context retro-prioritizes which annotation was probably right (Li 2013). Its existence is an admission of the annotation bottleneck, not a triumph -- use it knowing systems-level inference is bought with per-metabolite certainty.

## ORA vs MSEA vs Topology vs Mummichog

| Axis | ORA (hypergeometric) | MSEA / GSEA-PSEA | Topology / "Impact" | Mummichog / PSEA |
|---|---|---|---|---|
| Input | Identified list + cutoff | Identified ranked list | Identified list in pathway graphs | Raw m/z + RT + stat, no IDs |
| Null question | More hits than chance? | Set systematically high/low in ranking? | Hits at central (high-betweenness) nodes? | Do mass-matched candidates cluster in pathways beyond a random feature list? |
| Uses magnitude? | No (cutoff discards it) | Yes | Indirectly (enrichment x centrality) | No (cutoff defines the query) |
| Null source | Assay-coverage background | The ranked universe | Curated graph structure | Permutation from the FULL feature table (R_all) |
| Headline failure | Wrong/implicit background | Needs a complete ranking | Hub overemphasis (alanine ~95% case) | Significant-features-only as background |
| Output | Measured enrichment | Measured enrichment | Graph property, not the experiment | PREDICTED activity, not identities |

## ORA on an Identified Compound List

**Goal:** Test whether a list of confidently identified metabolites is over-represented in KEGG/SMPDB pathways, with a defensible background.

**Approach:** Map names/IDs to the internal library, set the pathway library and metabolome filter (the background), then run the hypergeometric score; report mapping coverage alongside p-values.

```r
library(MetaboAnalystR)

# 'pathora' = pathway ORA; 'conc' = concentration-style input
mSet <- InitDataObjects('conc', 'pathora', FALSE)
mSet <- SetOrganism(mSet, 'hsa')

# Confidently identified compounds (MSI level 1-2); names, HMDB, or KEGG IDs
compounds <- c('Pyruvate', 'L-Lactate', 'Citrate', 'Succinate', 'Fumarate', 'L-Alanine')
mSet <- Setup.MapData(mSet, compounds)
mSet <- CrossReferencing(mSet, 'name')          # 'name' | 'hmdb' | 'kegg' | 'pubchem'
mSet <- CreateMappingResultTable(mSet)          # inspect mapping coverage before trusting any p-value

mSet <- SetKEGG.PathLib(mSet, 'hsa', 'current')

# SetMetabolomeFilter(mSet, TRUE) restricts the background to a user-supplied
# reference metabolome (the assay-coverage set). FALSE uses the whole library
# (all of KEGG) -- the inflated default that manufactures false positives.
mSet <- SetMetabolomeFilter(mSet, FALSE)
mSet <- CalculateOraScore(mSet, 'rbc', 'hyperg') # node-importance 'rbc'|'dgr'; test 'hyperg'|'fisher'

ora <- as.data.frame(mSet$analSet$ora.mat)       # columns include Raw p, FDR, Impact, Hits, Total
```

## Mummichog / PSEA on a Raw m/z Peak Table

**Goal:** Predict perturbed pathway activity from an untargeted LC-MS feature table when no compound identities exist.

**Approach:** Declare instrument ppm and ionization mode, load the FULL feature table (m/z + p-value + t-score, optionally RT), set the query-defining p-cutoff, and run PSEA whose permutation null is sampled from R_all.

```r
library(MetaboAnalystR)

mSet <- InitDataObjects('mass_all', 'mummichog', FALSE)
mSet <- SetPeakFormat(mSet, 'mpt')               # 'mpt' = m/z, p-value, t-score; 'mprt' adds RT (use with 'v2')

# ppm and ionization mode are chemistry-specific and mandatory; pos and neg use
# entirely different adduct tables. Mixed data needs a per-feature mode column.
mSet <- UpdateInstrumentParameters(mSet, 5.0, 'negative')

# CRITICAL: peaks.txt must be the ENTIRE feature table, not just significant peaks.
# The permutation null draws random feature lists from this file (R_all); supplying
# only significant features pre-enriches the pool and makes everything significant.
mSet <- Read.PeakListData(mSet, 'peaks.txt')
mSet <- SanityCheckMummichogData(mSet)

mSet <- SetPeakEnrichMethod(mSet, 'mum', 'v2')   # 'mum'|'gsea'|'integ'; 'v2' uses RT/empirical compounds
mSet <- SetMummichogPval(mSet, 0.2)              # query-defining cutoff; default is NOT 0.05 -- document it
mSet <- PerformPSEA(mSet, 'hsa_mfn', 'current', permNum = 1000) # library string encodes organism+network

psea <- mSet$mummi.resmat                         # predicted-active pathways; NOT a metabolite ID list
```

## Network-Diffusion Enrichment (FELLA)

**Goal:** Return the intermediate enzymes, reactions, and modules that mechanistically link the affected metabolites, not just a ranked pathway list.

**Approach:** Build the KEGG knowledge graph once, then per-analysis map KEGG IDs and run heat diffusion; inspect excluded (unmapped) compounds explicitly.

```r
library(FELLA)

# Build once, reuse. buildGraphFromKEGGREST hits the live KEGG API (slow); cache the DB.
graph <- buildGraphFromKEGGREST(organism = 'hsa')
buildDataFromGraph(keggdata.graph = graph, databaseDir = 'fella_hsa', internalDir = FALSE)
fella.data <- loadKEGGdata(databaseDir = 'fella_hsa', internalDir = FALSE)

cpd_ids <- c('C00022', 'C00186', 'C00158', 'C00042', 'C00122', 'C00041') # KEGG compound IDs only
analysis <- defineCompounds(compounds = cpd_ids, data = fella.data)
getExcluded(analysis)                              # compounds that did not map -- report this

# 'diffusion' is the recommended default; runHypergeom = plain ORA over the graph,
# runPagerank (lowercase r) = directed random walks. The method string is lowercase.
analysis <- runDiffusion(object = analysis, data = fella.data, approx = 'normality')
results <- generateResultsTable(object = analysis, data = fella.data, method = 'diffusion', threshold = 0.05)
```

## Per-Method Failure Modes

### Wrong background set (the silent controller)
- **Trigger:** ORA run with the full library ("all of KEGG"); mummichog run with only significant features as input.
- **Mechanism:** The background IS the null hypothesis made concrete. The KEGG-human library held ~3,373 compounds vs 286-1,110 actually measurable in real datasets; padding the denominator with undetectable compounds inflates every p-value. For mummichog, the permutation null samples from the input table, so a significant-only input pre-enriches the pool.
- **Symptom:** Many "significant" pathways; few survive once the background is the assay-specific metabolome (Wieder 2021: two of five datasets dropped to ZERO after FDR with the correct background).
- **Fix:** ORA -> `SetMetabolomeFilter(mSet, TRUE)` with the measured-metabolome reference. Mummichog -> supply the entire feature table as `peaks.txt`. State the background in one sentence or the p-values are uninterpretable.

### Annotation laundering
- **Trigger:** ORA/MSEA run on MSI level-3 ("grey zone") tentative annotations as if they were level-1 confirmed.
- **Mechanism:** Enrichment cannot represent annotation confidence; a 4% misidentification rate already manufactures false pathways (Wieder 2021), and the error is not zero-mean because a wrong hub-adjacent compound flips a pathway alone.
- **Symptom:** Confident pathway claims downstream of unconfirmed IDs; results that do not replicate.
- **Fix:** Report the MSI level of the compounds driving the winning pathway; downgrade L3-driven claims to "consistent with." Consider metapone, which down-weights multiply-annotated features (weight inversely proportional to candidate count) instead of discarding the uncertainty.

### Hub-inflated topology / "impact"
- **Trigger:** Reporting MetaboAnalyst Pathway Impact as if it were an effect size.
- **Mechanism:** Impact = sum of relative-betweenness centrality of matched metabolites / sum over all pathway metabolites, computed inside an arbitrary isolated KEGG boundary without removing currency metabolites. A handful of cofactor-like hubs dominate betweenness (Tsouka & Masoodi 2023: L-alanine alone = ~95% of a pathway's total centrality). It is also sign-blind.
- **Symptom:** A pathway "lights up" with high impact because one promiscuous compound was hit by chance; the same hits give different impact in KEGG vs SMPDB.
- **Fix:** Treat impact as a visualization tiebreaker only. Read ORA and topology against each other; a pathway impact-driven by a single hub is a red flag, not a confirmation.

### Pool size is not flux
- **Trigger:** Reporting "pathway X is activated / upregulated" from concentration-based enrichment.
- **Mechanism:** A metabolomics measurement is a steady-state pool size (production minus consumption), not a rate. Pool and flux can move in opposite directions: sildenafil RAISES the cGMP pool while LOWERING flux through it (it inhibits the degrading phosphodiesterase). A falling substrate pool can mean the pathway is MORE active.
- **Symptom:** Causal/activity language ("upregulated pathway") drawn from a concentration snapshot.
- **Fix:** Downgrade to "members of pathway X co-varied with phenotype." Activity claims require stable-isotope-resolved metabolomics (SIRM / 13C metabolic flux analysis), which traces label incorporation over time; concentration-based enrichment generates a flux hypothesis, never tests one.

## Quantitative Thresholds

| Threshold | Value | Source / rationale |
|---|---|---|
| Mummichog query p-cutoff | ~0.2 (NOT 0.05) | The query must be large enough to score; vignette default is looser than 0.05. Document the value used (Li 2013; MetaboAnalystR vignette). |
| Empirical-compound RT window (v2) | ~`max(RT) * 0.02` seconds | Groups co-eluting features into one empirical compound; units are SECONDS (passing minutes mis-groups). |
| Mass tolerance (ppm) | instrument-specific (e.g. 5 ppm HRMS) | Loose ppm worsens multiple-m/z-matching inflation; set to the instrument's real accuracy. |
| FDR | < 0.05 (BH) | Standard, but secondary to a correct background -- with the right background, often zero pathways survive (Wieder 2021). |
| Pathway granularity caveat | -- | Pathway definition moves p by up to 9 orders of magnitude vs ~2 for multiple testing (Karp 2021); prefer cross-database consensus over one library. |
| Mapping coverage | report always | Enrichment computed over 12 of 400 features is a footnote, not a finding (Theme 3). |

## Common Errors

| Error / symptom | Cause | Solution |
|---|---|---|
| Everything is significant in mummichog | Input was significant features only, not R_all | Supply the entire feature table as `peaks.txt` |
| `could not find function "runPageRank"` | Wrong casing | FELLA function is `runPagerank` (lowercase r); method string is `'pagerank'` |
| PSEA maps to the wrong network silently | Wrong library string in `PerformPSEA` | Library encodes organism+network (`hsa_mfn`, `hsa_kegg`, ...); match the organism |
| Garbage candidate compounds | Wrong ionization mode | pos/neg use different adduct tables; set mode in `UpdateInstrumentParameters`; mixed data needs a per-feature mode column |
| Only TCA / amino-acid pathways enriched | Pathway dark matter | Xenobiotics, lipids, novel structures map to no pathway and are dropped; report coverage; consider ChemRICH (structure-based) |
| `'v2'` enrichment errors on RT | No RT column in input | `'v2'`/empirical compounds need RT; use `SetPeakFormat(mSet, 'mprt')` |

## References

- Li S, Park Y, Duraisingham S, Strobel FH, Khan N, Soltow QA, Jones DP, Pulendran B. 2013. Predicting network activity from high throughput metabolomics. *PLoS Comput Biol* 9(7):e1003123.
- Pang Z, Lu Y, Zhou G, Hui F, Xu L, Viau C, Spigelman AF, MacDonald PE, Wishart DS, Li S, Xia J. 2024. MetaboAnalyst 6.0: towards a unified platform for metabolomics data processing, analysis and interpretation. *Nucleic Acids Res* 52(W1):W398-W406.
- Xia J, Wishart DS. 2010. MSEA: a web-based tool to identify biologically meaningful patterns in quantitative metabolomic data. *Nucleic Acids Res* 38(W):W71-W77.
- Picart-Armada S, Fernandez-Albert F, Vinaixa M, Yanes O, Perera-Lluna A. 2018. FELLA: an R package to enrich metabolomics data. *BMC Bioinformatics* 19(1):538.
- Wieder C, Frainay C, Poupin N, Rodriguez-Mier P, Vinson F, Cooke J, Lai RPJ, Bundy JG, Jourdan F, Ebbels T. 2021. Pathway analysis in metabolomics: recommendations for the use of over-representation analysis. *PLOS Comput Biol* 17(9):e1009105.
- Wieder C, Bundy JG, Frainay C, Poupin N, Rodriguez-Mier P, Vinson F, Cooke J, Lai RPJ, Jourdan F, Ebbels TMD. 2022. Avoiding the misuse of pathway analysis tools in environmental metabolomics. *Environ Sci Technol* 56(20):14219-14222.
- Karp PD, Midford PE, Caspi R, Khodursky A. 2021. Pathway size matters: the influence of pathway granularity on over-representation (enrichment analysis) statistics. *BMC Genomics* 22:191.
- Tsouka S, Masoodi M. 2023. Metabolic pathway analysis: advantages and pitfalls for the functional interpretation of metabolomics and lipidomics data. *Biomolecules* 13(2):244.
- Tian L, Yu T. 2022. Metapone: a Bioconductor package for joint pathway testing for untargeted metabolomics data. *Bioinformatics* 38(14):3662-3669.
- Barupal DK, Fiehn O. 2017. Chemical Similarity Enrichment Analysis (ChemRICH) as alternative to biochemical pathway mapping for metabolomic datasets. *Sci Rep* 7:14567.
- Schymanski EL, Jeon J, Gulde R, Fenner K, Ruff M, Singer HP, Hollender J. 2014. Identifying small molecules via high resolution mass spectrometry: communicating confidence. *Environ Sci Technol* 48(4):2097-2098.

## Related Skills

- metabolomics/metabolite-annotation - Annotation confidence levels (MSI) that feed ORA/MSEA and set the interpretive ceiling
- metabolomics/statistical-analysis - Upstream differential testing that produces the significant compound or feature list
- metabolomics/isotope-tracing - Flux versus pool: enrichment infers activity from steady-state abundance, which isotope labeling can contradict
- pathway-analysis/go-enrichment - Gene-set over-representation concepts (the ORA analogue for genes)
- pathway-analysis/gsea - Ranked-list enrichment concepts (the MSEA analogue for genes)
- multi-omics-integration/mofa-integration - Joint gene+metabolite integration and its coverage-asymmetry traps
<!-- END FILE: metabolomics/pathway-mapping/SKILL.md -->

## 子目录：metabolomics/statistical-analysis

<!-- BEGIN FILE: metabolomics/statistical-analysis/SKILL.md -->
---
name: bio-metabolomics-statistical-analysis
description: Decision-grade statistical analysis for metabolomics intensity tables. Covers transformation and scaling (Pareto vs unit-variance as a hidden hypothesis), unsupervised structure (PCA/HCA for QC), permutation-validated PLS-DA/OPLS-DA (R2 vs Q2, double CV, VIP as heuristic), univariate testing (Welch/Mann-Whitney/ANOVA/LMM with covariate adjustment), and dependence-aware multiple testing. Use when testing which metabolites differ, building or validating a discriminant model, choosing a scaling, or correcting many correlated tests. For sample-wise normalization/drift correction see metabolomics/normalization-qc; for ML classifiers and selection-inside-CV leakage see machine-learning/biomarker-discovery and machine-learning/model-validation; for pathway interpretation see metabolomics/pathway-mapping; for design/power/multiplicity regime see experimental-design/multiple-testing.
tool_type: mixed
primary_tool: ropls
---

## Version Compatibility

Reference examples tested with: ropls 1.34+, scipy 1.12+, statsmodels 0.14+, numpy 1.26+, pandas 2.1+, matplotlib 3.8+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Metabolomics Statistical Analysis

**"Tell me which metabolites separate my groups"** -> run an honest univariate test with dependence-aware FDR AND a permutation-validated multivariate model, then reconcile the two.
- R: `ropls::opls()` (PCA/PLS-DA/OPLS-DA + permutation), `wilcox.test()`/`lm()`/`lme4::lmer()`, `p.adjust(method='BH')`
- Python: `scipy.stats.ttest_ind(equal_var=False)`/`mannwhitneyu`, `statsmodels` `multipletests(method='fdr_bh')`, `sklearn.cross_decomposition.PLSRegression` + `permutation_test_score`

## The Single Most Important Modern Insight -- A Score Plot Is a Hypothesis, Not a Result

In metabolomics the regime is p >> n (hundreds-to-thousands of features, tens of samples) with strongly correlated features. In that regime any binary labelling of n points in >= n-1 dimensions is linearly separable with probability 1, so PLS-DA and OPLS-DA produce a clean two-cluster score plot even for randomly assigned labels. A beautiful score plot is the generic output of the algorithm and carries essentially zero information. Only a cross-validated Q2 benchmarked against a permutation null distinguishes signal from geometry (Westerhuis 2008; Ruiz-Perez 2020). Three corollaries reorganize the whole skill: (1) R2 is no evidence (it can be driven to 1 by adding components); only permutation-validated Q2 licenses a claim. (2) Scaling is a hidden hypothesis -- variance-driven methods weight a feature by the variance it is allowed to contribute, so Pareto vs unit-variance hands back a different VIP list and a different biological story (van den Berg 2006). (3) Features are not independent (pathways, adducts, isotopologues), so naive BH-independence is violated and one real signal lights up its whole correlated cluster.

## Transformation and Scaling -- the Decision That Changes Conclusions

Transformation (nonlinear, per value: corrects heteroscedastic multiplicative MS noise and skew) and scaling (linear, per feature: sets relative weight) are distinct. Mean-centering is the universal first step. Choosing not to scale is the strongest prior of all -- it lets the most abundant metabolite drive PC1.

| Method | Per feature j | Effect | Use when |
|--------|---------------|--------|----------|
| Centering | subtract mean | offsets removed, variance unchanged | always (prerequisite for all below) |
| Auto / unit-variance / "standard" | center, / SD_j | every metabolite equal weight | a priori all metabolites equally important; classic default -- but inflates near-LOD noise |
| Pareto | center, / sqrt(SD_j) | between raw and UV | de facto metabolomics/NMR/OPLS-DA default; curbs dominance with less noise inflation than UV |
| Range | center, / (max-min) | abundance dependence removed | clean data, few outliers (outlier-sensitive) |
| Vast | UV x (mean/SD) | up-weights low-CV stable features | focus on robust/reproducible features with prior class info |
| Level | center, / mean_j | relative (% change) | response as relative change (mean noisy at low abundance) |
| Log / log10 | log(x) | multiplicative -> additive | concentrations spanning orders of magnitude (undefined at 0) |
| glog | linear near 0, log for large x | variance-stabilizing | data with zeros / near-LOD values; preferred over plain log (needs transition param) |
| Power (sqrt, cube-root) | x^(1/2) | mild stabilization | mild skew with zeros present |

van den Berg 2006: on real data autoscale and range recovered biologically meaningful loadings; Pareto is the pragmatic middle. Decision rule: transform first (if heteroscedastic -- usually yes for MS), then center, then scale; run at least Pareto AND UV, and if the top-VIP list or conclusion flips, the result is scaling-fragile and must be tempered.

## Decision Tree by Scenario

| Goal / situation | Do | Why |
|------------------|----|----|
| First look, QC, batch/outlier check | PCA on scaled data; color scores by batch/injection order; Hotelling T2 ellipse | Unsupervised -> cannot overfit the grouping; pooled-QC samples must cluster tightly in the center, else analytical variance dominates |
| Which single metabolites differ (2 groups) | Welch t-test (post-transform) or Mann-Whitney; BH FDR; report fold change + CI | Interpretable per-feature effect; FDR-controlled; effect size mandatory in p>>n |
| 2 groups, paired/pre-post | Paired t-test or Wilcoxon signed-rank | Discards within-subject pairing if analyzed unpaired -> underpowered |
| >2 groups | One-way ANOVA (+Tukey) or Kruskal-Wallis (+Dunn) | Match normality assumption |
| Longitudinal / repeated measures | Linear mixed model (random intercept/slope per subject) | Handles unbalanced timepoints, missingness, within-subject correlation |
| Covariate adjustment (age/sex/BMI/batch) | Per-feature linear model `y ~ group + covars` | Human metabolome is dominated by age/sex/BMI -- unadjusted, they masquerade as case/control signal (Thevenot 2015) |
| A discriminant / predictive model | PLS-DA (`orthoI=0`) or OPLS-DA (`predI=1, orthoI=NA`) + permutation + double CV | Supervised; demands full validation (see checklist) |
| Built-in feature selection | sparse PLS-DA `splsda()` (mixOmics) with `tune.splsda` | Selection must be inside CV -> hand off to machine-learning/biomarker-discovery |
| Rank discriminant features | VIP from a permutation-validated model only; corroborate with univariate FDR | VIP > 1 is a heuristic, not a test (see failure modes) |
| Confirm a biomarker | Independent validation cohort | Internal CV does not correct overfitting/forking-paths; discovery performance overestimates external |

## Scaling + PCA

**Goal:** Get the honest unsupervised first look that cannot chase the labels, with QC as the primary data-quality readout.

**Approach:** Transform if heteroscedastic, then PCA with an explicit scaling; inspect QC clustering, batch coloring, and Hotelling T2.

```r
library(ropls)
# scaleC default is "standard" (unit-variance/autoscale), NOT Pareto -- set explicitly
pca <- opls(t(feature_matrix), scaleC = 'pareto', fig.pdfC = 'none', info.txtC = 'none')
scores <- getScoreMN(pca)               # samples x components
getSummaryDF(pca)                       # R2X(cum) per component
# Tight pooled-QC clustering in the center = trustworthy run; QC scatter = analytical variance dominates
```

## Permutation-Validated PLS-DA / OPLS-DA

**Goal:** Decide whether group separation is real, not a geometry artifact, before reading any VIP or S-plot.

**Approach:** Fit with an explicit scaling, raise `permI` far above the default of 20, and read `pQ2`/`pR2Y` -- a model whose true Q2 sits inside the permutation cloud is indistinguishable from chance.

```r
library(ropls)
group <- factor(sample_info$group)
# OPLS-DA: 1 predictive + auto orthogonal; permI default 20 is too few for a reliable pQ2 -> >=1000
oplsda <- opls(t(feature_matrix), group, predI = 1, orthoI = NA,
               scaleC = 'pareto', permI = 1000, crossvalI = 7,
               fig.pdfC = 'none', info.txtC = 'none')
summ <- getSummaryDF(oplsda)            # R2X(cum), R2Y(cum), Q2(cum), pre, ort, pR2Y, pQ2
vip_pred <- getVipVn(oplsda)            # predictive VIP (Galindo-Prieto 2014); orthoL=TRUE for orthogonal
# Claim is licensed only if Q2 high AND pQ2 small. R2Y alone proves nothing.
```

PLS-DA is `orthoI = 0`. OPLS-DA has identical predictive power to PLS-DA -- it is a coordinate rotation, not a better model; the orthogonal block often encodes a confounder (inspect what correlates with it). DQ2 (Westerhuis 2008b) is the discriminant-appropriate figure of merit when Q2 penalizes correct-side over-predictions.

## PLS-DA / OPLS-DA Validation Checklist

1. Report the transformation + scaling used (it changes the loadings, VIPs, and story).
2. Report R2X, R2Y, Q2 and the number of predictive + orthogonal components.
3. Choose the number of components inside CV, not by eye on the training fit.
4. Permutation test (>= 1000) of the full pipeline -> permutation p for Q2 (and R2Y). Permute every step that touched the labels.
5. For honest generalization error use double (cross-model) CV or an untouched test set; single CV that also tuned the model is optimistic.
6. Independent validation cohort for any biomarker claim.
7. Read VIP / S-plot only from a validated model; corroborate with univariate FDR + effect size; report ranking stability across resamples.
8. Put a PCA score plot beside the PLS-DA one -- separation only under supervision is the artifact signature.

## Univariate Testing + Correct FDR

**Goal:** Produce an interpretable, FDR-controlled per-metabolite answer with effect sizes.

**Approach:** Match the test to the design, compute log2 fold change as a difference of group means on transformed data, then apply BH explicitly (defaults are not BH in either language).

```python
import numpy as np
import pandas as pd
from scipy.stats import ttest_ind
from statsmodels.stats.multitest import multipletests

logged = np.log2(intensities.replace(0, np.nan))   # transform before testing
pvals, lfc = [], []
for feat in logged.index:
    a = logged.loc[feat, case].dropna().values
    b = logged.loc[feat, ctrl].dropna().values
    if len(a) >= 3 and len(b) >= 3:
        pvals.append(ttest_ind(a, b, equal_var=False)[1])   # Welch: scipy defaults to Student
        lfc.append(a.mean() - b.mean())                     # geometric-mean ratio on log scale
    else:
        pvals.append(np.nan); lfc.append(np.nan)
res = pd.DataFrame({'feature': logged.index, 'log2fc': lfc, 'pval': pvals}).dropna(subset=['pval'])
# statsmodels default is 'hs' (Holm-Sidak); R p.adjust default is 'holm' -- ALWAYS pass BH explicitly
res['padj'] = multipletests(res['pval'], method='fdr_bh')[1]
```

BH controls FDR under independence and PRDS; positively-correlated metabolomics features roughly satisfy PRDS, so BH is valid but conservative -- but closure-induced negative correlations (after total-area/PQN normalization) fall outside the clean case, where a permutation FDR sidesteps the dependence assumptions. The effective number of independent tests is far below the feature count (one compound = many adducts/isotopologues/fragments); use an effective-number-of-tests correction (Peluso 2021) rather than Bonferroni-on-features, and collapse features to compounds before counting "how many metabolites changed."

## Volcano Plot

**Goal:** Show significance and magnitude together for all features.

**Approach:** Plot log2 fold change vs -log10(p), with the FDR cutoff annotated (raw p on the axis is fine only if the FDR line is drawn).

```python
import matplotlib.pyplot as plt
hit = (res['padj'] < 0.05) & (res['log2fc'].abs() > 1)   # 2-fold + FDR 5%
plt.scatter(res['log2fc'], -np.log10(res['pval']), c=np.where(hit, 'firebrick', 'gray'), s=12, alpha=0.6)
plt.axhline(-np.log10(0.05), ls='--'); plt.axvline(1, ls='--'); plt.axvline(-1, ls='--')
plt.xlabel('log2 fold change'); plt.ylabel('-log10(p)')
```

## Per-Method Failure Modes

### Noise separation (the cardinal sin)
- **Trigger:** Reporting a PLS-DA/OPLS-DA score plot as evidence of a group difference.
- **Mechanism:** In p>>n any labelling is linearly separable; the algorithm always finds a covariance-maximizing direction, even for random labels.
- **Symptom:** Clean two-cluster score plot, high R2Y, but Q2 low/negative or inside the permutation cloud; PCA shows no separation.
- **Fix:** Permutation test (>=1000) of the full pipeline; require small pQ2; put the PCA plot beside it.

### VIP misuse
- **Trigger:** Selecting biomarkers by VIP > 1 from a single model fit.
- **Mechanism:** VIPs are normalized so the mean squared VIP = 1 -- roughly half the features exceed 1 by construction; there is no null, no p-value, and the ranking is unstable under resampling in p>>n.
- **Symptom:** Top-20 VIP list reshuffles when the model is re-bootstrapped; VIP-only hits fail to replicate.
- **Fix:** Use VIP only from a permutation-validated model; require univariate FDR + effect-size concordance and resampling stability; use the OPLS-specific VIP so a high orthogonal-block VIP (the confounder) is not credited to disease.

### Naive FDR under correlation
- **Trigger:** BH or Bonferroni applied as if the features were independent.
- **Mechanism:** Pathway co-regulation plus adducts/isotopologues/fragments make features strongly correlated; one signal lights up its whole cluster, and closure (after sample-wise normalization) injects negative correlations.
- **Symptom:** A "200 significant metabolites" list that encodes a handful of independent signals; over-conservative threshold from Bonferroni-on-features.
- **Fix:** Effective-number-of-tests or permutation FDR (Peluso 2021); collapse features to compounds before counting hits; report independent-signal counts.

### Log with zeros / detection-rate confound
- **Trigger:** Half-min (or zero) imputation followed by log, especially when detection rate differs between groups.
- **Mechanism:** "Missing" is left-censored (MNAR); a constant imputed at the LOD then logged spikes the censored region, and a detection-rate difference masquerades as a concentration difference.
- **Symptom:** Fake bimodality; a low-abundance "hit" that is really a difference in how often the metabolite was detected.
- **Fix:** Report per-group detection rates with any low-abundance hit; prefer glog or a left-censored imputer (QRILC/GSimp) over impute-constant-then-log when detection differs (see metabolomics/normalization-qc).

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| Q2 > 0.5 "good" | Triba 2015 (heuristic) | Predictive ability rule-of-thumb; not a hard cutoff -- many published models report Q2 < 0.5; report the value, not a verdict |
| permI >= 1000 | Szymanska 2012 | Q2/DQ2 null distributions are skewed; the ropls default of 20 estimates only the granularity of the grid, not a usable pQ2 |
| pQ2 < 0.05 | Westerhuis 2008 | Fraction of permuted models with Q2 >= true Q2; the actual evidence the separation is real |
| crossvalI = 7 | ropls default | 7-fold CV; for very small n LOO is common but optimistic |
| VIP > 1 | Galindo-Prieto 2014 | Above-average contributor; a ranking heuristic with no error control -- never a standalone selector |
| BH FDR < 0.05 | Benjamini-Hochberg | Expected false-positive proportion among rejections; the metabolomics discovery default |
| \|log2FC\| > 1 | convention | 2-fold; effect-size gate orthogonal to the p-value, mandatory in p>>n |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| Model "significant" yet noise | `permI = 20` (ropls default) | Set `permI >= 1000`; read `pQ2`/`pR2Y` from `getSummaryDF` |
| Wrong scaling shipped silently | `scaleC` default is `"standard"` (UV), not Pareto | Set `scaleC = 'pareto'` (or the intended scaling) explicitly; report it |
| PLS-DA vs OPLS-DA "function not found" | type is set by `orthoI`, not a separate function | `orthoI = 0` -> PLS; `orthoI = NA` -> OPLS; `predI = 1` for 2-class |
| FDR is actually Holm | R `p.adjust` default is `'holm'` (FWER) | Pass `method = 'BH'` |
| FDR is actually Holm-Sidak | statsmodels `multipletests` default is `'hs'` | Pass `method = 'fdr_bh'` |
| Student instead of Welch | scipy `ttest_ind` default `equal_var=True` | Set `equal_var=False` (group variances differ, esp. near LOD) |
| Reversed/unstable fold change | `log2(mean_ratio)` uses arithmetic means | Difference of log-means (geometric-mean ratio), consistent with limma/DESeq2 |
| Optimistic CV error | feature selection done before CV | Re-fit selection inside every fold; see machine-learning/model-validation |
| getVipVn gives orthogonal importance | `orthoL = TRUE` returns orthogonal VIP | Use default (predictive VIP) for discriminant ranking |

## References

- van den Berg RA, Hoefsloot HCJ, Westerhuis JA, Smilde AK, van der Werf MJ. 2006. Centering, scaling, and transformations: improving the biological information content of metabolomics data. *BMC Genomics* 7:142.
- Westerhuis JA, Hoefsloot HCJ, Smit S, Vis DJ, Smilde AK, et al. 2008. Assessment of PLSDA cross validation. *Metabolomics* 4:81-89.
- Westerhuis JA, van Velzen EJJ, Hoefsloot HCJ, Smilde AK. 2008. Discriminant Q2 (DQ2) for improved discrimination in PLSDA models. *Metabolomics* 4:293-296.
- Saccenti E, Hoefsloot HCJ, Smilde AK, Westerhuis JA, Hendriks MMWB. 2014. Reflections on univariate and multivariate analysis of metabolomics data. *Metabolomics* 10:361-374.
- Broadhurst DI, Kell DB. 2006. Statistical strategies for avoiding false discoveries in metabolomics and related experiments. *Metabolomics* 2:171-196.
- Thevenot EA, Roux A, Xu Y, Ezan E, Junot C. 2015. Analysis of the human adult urinary metabolome variations with age, body mass index, and gender by implementing a comprehensive workflow for univariate and OPLS statistical analyses. *J Proteome Res* 14:3322-3335.
- Triba MN, Le Moyec L, Amathieu R, Goossens C, Bouchemal N, et al. 2015. PLS/OPLS models in metabolomics: the impact of permutation of dataset rows on the K-fold cross-validation quality parameters. *Mol BioSyst* 11:13-19.
- Szymanska E, Saccenti E, Smilde AK, Westerhuis JA. 2012. Double-check: validation of diagnostic statistics for PLS-DA models in metabolomics studies. *Metabolomics* 8(Suppl 1):3-16.
- Galindo-Prieto B, Eriksson L, Trygg J. 2014. Variable influence on projection (VIP) for orthogonal projections to latent structures (OPLS). *J Chemometr* 28:623-632.
- Ruiz-Perez D, Guan H, Madhivanan P, Mathee K, Narasimhan G. 2020. So you think you can PLS-DA? *BMC Bioinformatics* 21(Suppl 1):2.
- Peluso A, Glen R, Ebbels TMD. 2021. Multiple-testing correction in metabolome-wide association studies. *BMC Bioinformatics* 22:67.
- Storey JD, Tibshirani R. 2003. Statistical significance for genomewide studies. *Proc Natl Acad Sci USA* 100:9440-9445.

## Related Skills

- metabolomics/normalization-qc - Sample-wise normalization, drift/batch correction, missing-value imputation upstream of testing
- metabolomics/pathway-mapping - Functional interpretation of differential metabolites
- machine-learning/biomarker-discovery - Feature selection inside CV, stability, minimal-optimal vs all-relevant
- machine-learning/model-validation - Leakage taxonomy, nested CV, calibration vs discrimination
- experimental-design/multiple-testing - FDR vs FWER regime, discovery vs confirmatory
- data-visualization/volcano-and-ma-plots - Volcano plot recipes
<!-- END FILE: metabolomics/statistical-analysis/SKILL.md -->

## 子目录：metabolomics/targeted-analysis

<!-- BEGIN FILE: metabolomics/targeted-analysis/SKILL.md -->
---
name: bio-metabolomics-targeted-analysis
description: Designs and validates quantitative targeted metabolomics assays (MRM/SRM on triple-quadrupole, PRM on high-resolution instruments) to report absolute concentrations. Covers the internal-standard strategy (external cal -> global IS -> standard addition -> stable-isotope-labeled IS), weighted calibration judged by back-calculated %RE not R-squared, ion-ratio quantifier/qualifier confirmation, matrix-effect/recovery characterization, and ICH M10 method validation. Use when quantifying a closed panel of known metabolites with units, building or validating an LC-MS/MS assay, choosing an IS or calibration weighting, or judging whether a reported concentration is trustworthy. For untargeted feature detection see metabolomics/xcms-preprocessing; for group statistics see metabolomics/statistical-analysis; for flux/MID/tracing see metabolomics/isotope-tracing.
tool_type: mixed
primary_tool: skyline
---

## Version Compatibility

Reference examples tested with: R 4.3+, ggplot2 3.5+, Skyline 23.1+, pandas 2.2+, numpy 1.26+

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

An absolute concentration requires three inputs the code cannot supply: an authentic reference standard (its certificate-of-analysis purity scales every reported number), a stable-isotope-labeled internal standard that co-elutes with the analyte, and a per-analyte validation record. Without these, the workflow below produces relative peak-area ratios dressed as concentrations.

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Targeted Metabolomics Analysis

**"Quantify these specific metabolites and give me concentrations with units"** -> Fit weighted calibration curves on authentic standards, normalize each analyte to a co-eluting stable-isotope-labeled internal standard, confirm identity by ion ratio, and report concentrations only within the validated range.
- CLI: Skyline builds the small-molecule transition list, integrates peaks, fits weighted calibration, and exports via the Document Grid.
- R / Python: post-export curve fitting, back-calculated %RE checks, IS normalization, ion-ratio confirmation, validation metrics.

## The Single Most Important Modern Insight -- A Concentration Is a Chain of Cancellations, and Matrix Effects Are the Term That Fails to Cancel

Ion suppression is competition for charge and droplet surface in the electrospray source: a co-eluting matrix component (phospholipids late in a reversed-phase gradient, salts at the void) steals ionization from the analyte. Suppression is a property of the co-elution, not of the analyte, so it is retention-time-dependent and lot-dependent. The only mechanism that truly removes it is a stable-isotope-labeled internal standard (SIL-IS) that sits in the identical droplet at the identical instant: the suppression cancels in the analyte/IS area ratio. An IS that elutes even half a minute away samples a different point on the suppression landscape and injects new error rather than removing it. Every other safeguard in this skill -- weighting, ion ratios, validation -- assumes this cancellation is working; the gap between a solvent calibration curve and a matrix-matched curve is a direct readout of how badly the IS is failing.

## Targeted vs Untargeted -- Different Experiments, Not Two Settings

| Axis | Untargeted (discovery) | Targeted (quantification) |
|---|---|---|
| Analyte set | Open -- everything ionizable | Closed -- a panel defined before acquisition |
| Output | Relative fold-change; often putative IDs | Absolute concentration for confirmed analytes |
| Instrument | High-res full-scan / DDA (Orbitrap, QTOF) | Triple-quad SRM/MRM, or high-res PRM |
| Validation | QA/QC framework (Broadhurst, mQACC) | Full bioanalytical validation possible (ICH M10) |
| Question | "What changed?" | "How much is there?" |

Targeted buys sensitivity and absolute quant by spending scope (only what is on the list is seen) and up-front method development. Common pattern: untargeted discovery -> targeted validation of the hits. Feature detection upstream is metabolomics/xcms-preprocessing; this skill begins once the panel and transitions are defined.

## Acquisition Mechanics -- MRM/SRM and PRM

A transition is a precursor-m/z -> product-m/z pair plus a tuned collision energy. On a triple quadrupole, Q1 isolates the precursor, the collision cell fragments it, Q3 isolates one product: the double mass filter is the source of MRM sensitivity. SRM monitors one transition; MRM multiplexes many. Each analyte should carry at least two transitions -- a quantifier (most intense/cleanest, used for concentration) and one or more qualifiers (orthogonal confirmation). PRM replaces Q3 with a high-resolution analyzer that records the full product spectrum in parallel, so transitions are chosen post hoc and isobaric interferences are resolved by exact mass; MRM still wins on absolute sensitivity and very large panels. Dwell time is the signal-accumulation time per transition; cycle time must stay short enough for at least 10-15 points across each chromatographic peak (convention). Scheduled MRM monitors each transition only within a retention-time window so a large panel keeps adequate dwell -- but a peak that drifts out of its window vanishes with no error message, the classic scheduled-MRM failure.

## Decision Tree -- Quant Goal -> IS + Calibration + Validation Depth

| Goal / situation | Internal standard | Calibration | Validation depth | Why |
|---|---|---|---|---|
| Clinical / regulated / PK number | One SIL-IS per analyte (13C/15N) | Multi-level weighted curve, judged by %RE | Full ICH M10 (accuracy, precision, MF, recovery, carryover, stability, ISR) | A number driving a decision must carry its evidence |
| Cross-study quantitative claim | SIL-IS per analyte or per RT/chemical cluster | Multi-level weighted | Accuracy/precision + matrix-factor on QCs | Comparability across runs demands characterized bias |
| Exploratory research, ranking | Few global IS, or per-class | 1/x^2 weighted, low-end %RE checked | Broadhurst/mQACC QC discipline (pooled QC, blanks, RSD filtering) | Relative comparison tolerates residual matrix bias |
| Dirty matrix, isobaric interferences | SIL-IS + high-res | PRM, post-hoc transitions | Selectivity dominated | Exact-mass product resolves co-eluters a unit-resolution Q3 cannot |
| Large standardized panel (600+) | Kit-supplied class IS | Single/limited-point (vendor) | Vendor + bridging study before pooling sites | Kit buys comparability and throughput, not per-analyte full-validation accuracy |
| Carbon source / pathway rate | (tracer, not IS) | -- | -- | Flux question: hand off to metabolomics/isotope-tracing; MID measures rate, not pool size |

The IS rule of thumb: ask how far (in retention time and chemistry) each analyte is from its assigned IS -- that distance is the size of the uncorrected matrix error. 13C/15N at non-exchangeable positions are preferred over deuterium: deuterium causes a small reversed-phase retention shift (the deuterium isotope effect) that can chromatographically separate the IS from its analyte so it stops correcting suppression, and labile deuteriums back-exchange to H. If forced to a deuterated IS, verify co-elution by overlaying analyte and IS chromatograms.

## Calibration and Weighting

| Weighting | When | Effect |
|---|---|---|
| Unweighted (OLS) | Narrow range, near-constant variance | High points dominate; low-end bias on heteroscedastic MS data -- usually wrong |
| 1/x | Moderate range (1-2 orders) | Down-weights high concentrations; restores low-end fit |
| 1/x^2 | Wide range (3+ orders), the common LC-MS default | Aggressively down-weights the top; can over-weight the low end -- still compare, do not reflex |
| Quadratic | Genuine, mechanism-explained curvature (detector saturation) | Never to paper over a bad linear fit |

MS detector response is heteroscedastic -- absolute variance grows with concentration -- so weighting models the variance structure (1/x and 1/x^2 are parametric stand-ins for 1/variance). Select empirically: fit candidate weightings, then pick the one minimizing the sum of absolute back-calculated relative error (%RE) across levels, especially the bottom two or three. R-squared is the wrong instrument: it is dominated by high-leverage top points, so a curve with R-squared 0.999 can be +40% biased at the LLOQ. Use a fitted (non-zero) intercept; forcing the line through the origin re-introduces low-end bias. The blank (matrix only) and zero (matrix + IS) are diagnostic, not calibration points.

### Build a Weighted Calibration Curve With a Back-Calculated %RE Check

**Goal:** Fit a calibration curve on the analyte/IS response ratio and accept it by per-level back-calculation accuracy, not by R-squared.

**Approach:** Fit 1/x^2-weighted linear regression of response ratio on nominal concentration, back-calculate every standard, flag any non-LLOQ level outside +/-15% and the LLOQ outside +/-20%, and set the LLOQ to the lowest passing level.

```r
standards <- data.frame(
  conc = c(1, 5, 10, 25, 50, 100, 250, 500, 1000),
  analyte_area = c(480, 2500, 4900, 12100, 24500, 49000, 121000, 245000, 488000),
  istd_area = c(100000, 98000, 99000, 101000, 100000, 98000, 101000, 99000, 100000)
)
standards$ratio <- standards$analyte_area / standards$istd_area

fit <- lm(ratio ~ conc, data = standards, weights = 1 / standards$conc^2)
standards$back_calc <- (standards$ratio - coef(fit)[1]) / coef(fit)[2]
standards$re_pct <- (standards$back_calc - standards$conc) / standards$conc * 100

# ICH M10: each calibrator within +-15%, +-20% at the LLOQ (lowest level)
tol <- ifelse(standards$conc == min(standards$conc), 20, 15)
standards$pass <- abs(standards$re_pct) <= tol
lloq <- min(standards$conc[standards$pass])
```

### Internal-Standard Normalization

**Goal:** Convert raw analyte area to a matrix-corrected response that the calibration curve maps to concentration.

**Approach:** Divide analyte area by co-eluting SIL-IS area per sample, then invert the same response-ratio calibration; matrix effect and extraction recovery cancel in the ratio.

```r
samples$ratio <- samples$analyte_area / samples$istd_area
samples$conc <- (samples$ratio - coef(fit)[1]) / coef(fit)[2]
samples$conc[samples$conc < lloq] <- NA   # below validated range -> not reportable
```

### Ion-Ratio Confirmation

**Goal:** Guard against quantifying an isobaric co-eluter as the analyte.

**Approach:** Compute the qualifier/quantifier area ratio per sample, compare to the mean calibrator ratio, and flag samples outside the tolerance window -- a drifted ratio means the quantifier peak is partly something else.

```r
cal_ratio <- mean(standards$qualifier_area / standards$quantifier_area)
samples$ion_ratio <- samples$qualifier_area / samples$quantifier_area
# SANTE/2020/12830 uses +-30% relative for LC-MS/MS qualifier/quantifier ratios
samples$id_confirmed <- abs(samples$ion_ratio - cal_ratio) / cal_ratio <= 0.30
```

MRM gives mass selectivity, not identity: two compounds can share a precursor->product transition (many acylcarnitines share m/z 85; lipids share head-group fragments). Identity needs retention time plus the ion ratio plus an authentic standard. Near the LLOQ the qualifier may fall below its own detection limit, so ion-ratio confirmation is usually only enforceable above a few times the LLOQ -- state that limit rather than hiding it. A single-transition method has no defense against isobaric interference and is a documented compromise, not a default.

### LOD and LLOQ

**Goal:** Set the lowest reliably quantifiable concentration from noise and accuracy, not from an extrapolated curve.

**Approach:** Estimate LOD from blank-signal scatter (S/N ~3) and confirm the LLOQ as the lowest calibrator meeting the +/-20% back-calculation and precision criteria; never anchor the curve below the real noise floor to claim sensitivity.

```r
blank_areas <- c(100, 120, 95, 110, 105)
slope <- coef(fit)[2]
lod <- (mean(blank_areas) + 3 * sd(blank_areas)) / slope   # S/N~3 convention
# LLOQ is the lowest calibrator passing +-20% %RE AND precision -- not 10*SD/slope alone
```

## Per-Method Failure Modes

### Matrix suppression unaccounted
- **Trigger:** Neat-solvent calibration, or an IS that does not co-elute with the analyte.
- **Mechanism:** Co-eluting phospholipids/salts suppress analyte ionization; with no co-eluting IS the suppression does not cancel.
- **Symptom:** Solvent and matrix-matched curves disagree; IS-normalized matrix factor far from 1; lot-to-lot drift.
- **Fix:** Co-eluting SIL-IS per analyte; map suppression zones by post-column infusion and move peaks off them; report IS-normalized matrix factor across at least six matrix lots.

### One IS shared across chemically diverse analytes
- **Trigger:** A single global IS used to correct a heterogeneous panel.
- **Mechanism:** The IS corrects suppression and recovery only for analytes co-eluting and chemically near it; distant analytes carry the difference of two suppressions.
- **Symptom:** Excellent CVs but biased group means -- precision (set by the IS correcting injection/drift) and accuracy (set by the per-analyte residual) are decoupled.
- **Fix:** SIL-IS per analyte, or per RT/chemical cluster; treat low CV as no evidence of correctness.

### Unweighted calibration over a wide range
- **Trigger:** OLS fit on heteroscedastic data; acceptance judged by R-squared.
- **Mechanism:** High-concentration points dominate least squares; the low end is fit poorly.
- **Symptom:** R-squared 0.999 yet +30-40% bias at the LLOQ.
- **Fix:** Compare 1/x and 1/x^2, pick by minimizing low-end |%RE|, judge by per-level back-calculation.

### Isotopic crosstalk between analyte and IS
- **Trigger:** IS-analyte mass gap below ~3-4 Da, or high IS:analyte ratio at the LLOQ.
- **Mechanism:** The analyte natural-isotope envelope bleeds into the IS channel (bends the high end, mis-read as saturation); IS isotopic impurity bleeds into the analyte quantifier channel (inflates the low end, biases the LLOQ badly).
- **Symptom:** Non-linear high end; a matrix-blank-plus-IS sample shows signal in the analyte channel.
- **Fix:** Choose an IS mass gap of at least 3-4 Da or a less-abundant SIL isotopologue transition; always run a zero (matrix + IS only) and require its analyte-channel signal below 20% of the LLOQ.

### Pre-analytical degradation
- **Trigger:** Delayed quench, freeze-thaw, slow time-to-freezer.
- **Mechanism:** Metabolism continues post-collection (glycolysis, esterases, redox auto-oxidation); labile metabolites collapse in seconds to minutes.
- **Symptom:** No chromatographic error -- the true value is biased before injection; low/variable adenylate energy charge across samples is the tell that quenching, not biology, drove the numbers.
- **Fix:** Cold (-40 to -80 C) aqueous-organic quench matched to the metabolite, measure freeze-thaw and long-term stability per labile analyte, control collection-to-freeze time as a study variable.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|---|---|---|
| Calibrator back-calc within +/-15% (+/-20% at LLOQ), >=75% of >=6 levels pass | ICH M10 (Step 4, 2022) | Per-level accuracy, not correlation, defines a usable curve |
| QC accuracy +/-15% (+/-20% at LLOQ); precision CV <=15% (<=20% at LLOQ) | ICH M10 | Intra- and inter-day acceptance at >=4 levels |
| IS-normalized matrix factor CV <=15% across >=6 lots | ICH M10 / Matuszewski 2003 | Proof the IS cancels matrix effect; raw MF may be poor while IS-normalized MF ~1 |
| Carryover <=20% of LLOQ (analyte), <=5% (IS) | ICH M10 | Measured in a blank after the ULOQ; concentration-dependent, must be quantified not eyeballed |
| Selectivity: interference at LLOQ <=20% of analyte, <=5% of IS response | ICH M10 | Across >=6 individual matrix lots |
| ISR: >=2/3 of reanalyzed study samples within +/-20% | ICH M10 | Only test that catches incurred-sample-specific problems spiked QCs cannot |
| Ion-ratio tolerance +/-30% relative (LC-MS/MS) | SANTE/2020/12830 | Illustrative codified window; enforce only above a few times the LLOQ |
| >=10-15 points across a chromatographic peak | Convention | Reliable integration; sets the cycle-time ceiling |
| S/N ~3 = LOD, ~5-10 = LLOQ | Convention | Detection vs reliable quantification; LLOQ also bounded by accuracy/precision |

## Common Errors

| Error / symptom | Cause | Solution |
|---|---|---|
| Curve accepted on R-squared, biased at LLOQ | Unweighted heteroscedastic fit | Weight (1/x, 1/x^2); accept by per-level back-calculated %RE |
| Deuterated IS gives lot-dependent ratios | Deuterium isotope effect separates IS from analyte; lost matrix correction | Use 13C/15N at non-exchangeable positions, or verify co-elution explicitly |
| High-end curvature mis-read as detector saturation | Analyte natural isotopes bleed into a too-close IS channel | Widen IS-analyte mass gap to >=3-4 Da; use nonlinear isotopic-crosstalk correction |
| Beautiful CVs, wrong group means | One global IS across diverse analytes -- precision/accuracy decoupled | SIL-IS per analyte or per RT/chemical cluster |
| Low samples after a high sample read high | Concentration-dependent carryover | Inject a blank after the ULOQ, randomize run order, report measured carryover |
| Skyline never ratios analyte to IS | IS not tagged Label Type = heavy and paired to its light analyte | Set Label Type heavy in the transition list; pair by molecule name |
| Validated assay, study numbers still wrong | Pre-analytical degradation (no error message) | Quench fast, measure stability, monitor adenylate energy charge |

## References

- MacLean B, Tomazela DM, Shulman N, Chambers M, Finney GL, Frewen B, Kern R, Tabb DL, Liebler DC, MacCoss MJ. 2010. Skyline: an open source document editor for creating and analyzing targeted proteomics experiments. *Bioinformatics* 26(7):966-968.
- Peterson AC, Russell JD, Bailey DJ, Westphall MS, Coon JJ. 2012. Parallel reaction monitoring for high resolution and high mass accuracy quantitative, targeted proteomics. *Molecular & Cellular Proteomics* 11(11):1475-1488.
- Matuszewski BK, Constanzer ML, Chavez-Eng CM. 2003. Strategies for the assessment of matrix effect in quantitative bioanalytical methods based on HPLC-MS/MS. *Analytical Chemistry* 75(13):3019-3030.
- ICH M10 Bioanalytical Method Validation and Study Sample Analysis. ICH Harmonised Guideline, Step 4, adopted 24 May 2022 (FDA implemented November 2022; EMA effective January 2023).
- Broadhurst D, Goodacre R, Reinke SN, Kuligowski J, Wilson ID, Lewis MR, Dunn WB. 2018. Guidelines and considerations for the use of system suitability and quality control samples in mass spectrometry assays applied in untargeted clinical metabolomic studies. *Metabolomics* 14(6):72.
- Wang S, Cyronak M, Yang E. 2007. Does a stable isotopically labeled internal standard always correct analyte response? A matrix effect study on a LC/MS/MS method for the determination of carvedilol enantiomers in human plasma. *Journal of Pharmaceutical and Biomedical Analysis* 43(2):701-707.
- Teo G, Chew WS, Burla BJ, Herr DR, Tai ES, Wenk MR, Torta F, Choi H. 2020. MRMkit: automated data processing for large-scale targeted metabolomics analysis. *Analytical Chemistry* 92(20):13677-13682.

## Related Skills

- metabolomics/xcms-preprocessing - Upstream feature detection for untargeted discovery before targeted validation
- metabolomics/statistical-analysis - Group comparison and multivariate analysis of quantified concentrations
- metabolomics/isotope-tracing - Stable-isotope tracing and flux (MID), the adjacent discipline this skill hands off to
- metabolomics/normalization-qc - QC-sample-driven drift correction and RSD filtering
- clinical-biostatistics/cdisc-data-handling - Regulated-trial bioanalysis data handling when targeted numbers feed a clinical study
<!-- END FILE: metabolomics/targeted-analysis/SKILL.md -->

## 子目录：metabolomics/xcms-preprocessing

<!-- BEGIN FILE: metabolomics/xcms-preprocessing/SKILL.md -->
---
name: bio-metabolomics-xcms-preprocessing
description: Programmatic untargeted LC-MS feature extraction in R with the modern xcms 4.x MsExperiment/XcmsExperiment API, taking raw mzML to a feature table via CentWave peak detection, retention-time alignment, peak-density correspondence, gap-filling, CAMERA redundancy collapse, and built-in QC feature filtering. Use when converting centroided LC-MS runs into a features-by-samples matrix and deciding centWave/grouping/alignment parameters. For drift correction and QC/CV filtering execution see metabolomics/normalization-qc; for metabolite identification see metabolomics/metabolite-annotation; for the MS-DIAL GUI alternative with MS2Dec deconvolution see metabolomics/msdial-preprocessing; for downstream statistics see metabolomics/statistical-analysis.
tool_type: r
primary_tool: xcms
---

## Version Compatibility

Reference examples tested with: xcms 4.x+ (MsExperiment/XcmsExperiment containers), Spectra 1.12+, CAMERA 1.58+

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('xcms')` then `?CentWaveParam` to verify parameter names and defaults

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

A feature table is only meaningful alongside its full processing specification: which xcms version, every `*Param` value, and the fill/filter ordering. The table is a parameterized hypothesis about which molecules exist, not the data.

# XCMS Untargeted LC-MS Preprocessing

**"Turn my raw LC-MS files into a feature table"** -> Detect chromatographic peaks per file, align retention times across runs, group corresponding peaks into features, fill gaps, then collapse adduct/isotope redundancy.
- R: `readMsExperiment()` -> `findChromPeaks()` -> `adjustRtime()` -> `groupChromPeaks()` -> `fillChromPeaks()` (xcms)

## The Single Most Important Insight -- The Feature Table Is a Model-Dependent Artifact, Not Ground Truth

Every cell in the table is the output of a detection + grouping + filling model with chosen parameters. Two analysts with different centWave/grouping settings produce materially different tables from identical raw files, so "not detected" is a statement about the parameters, not the sample. Three consequences reorganize the whole workflow: (1) preprocessing parameters silently set the detection floor - a compound absent from results may be present in the raw data but excluded by `noise`/`prefilter`/`peakwidth`/`snthresh`; (2) `fillChromPeaks` integrates whatever signal sits in a feature window even when no peak exists, fabricating a positive number where the honest answer is "below detection"; (3) one compound yields 5-15 features (adducts, isotopologues, in-source fragments, multimers), so a 10,000-feature table is plausibly ~1,000 compounds (Mahieu 2017). Report parameters as part of the result, inspect EICs and alignment of every hit, and collapse redundancy before annotation.

## API Generations -- Use Modern, Not Legacy

| Path | Containers | Verbs | Status |
|------|-----------|-------|--------|
| Modern (xcms 4.x) | `MsExperiment` (raw, Spectra backend) / `XcmsExperiment` (result) | `findChromPeaks` / `adjustRtime` / `groupChromPeaks` / `fillChromPeaks` driven by `*Param` objects | Preferred |
| Legacy (xcms <3) | `xcmsSet` / `xcmsRaw` | `findPeaks` / `group` / `retcor` / `fillPeaks`; `readMSData(mode='onDisk')` | Deprecated - do not use in new code |

Parameters are objects, not loose args: `findChromPeaks(data, param = CentWaveParam(...))`, never `findChromPeaks(data, ppm=..., peakwidth=...)`.

## Decision Tree by Scenario

| Situation | Do | Why |
|-----------|----|----|
| High-res centroid (Orbitrap, Q-Exactive, qTOF) | `CentWaveParam` | Wavelet on real mass traces, no fixed binning |
| Low-res / quadrupole / profile-only | `MatchedFilterParam` | Model-peak on binned EICs tolerates poor resolution |
| Profile data of any kind | Centroid first (msconvert vendor peakPicking, or `Spectra::pickPeaks`) | centWave requires centroids; profile input yields garbage mass traces |
| Many shared, well-behaved peaks across samples | `PeakGroupsParam` (after an initial `groupChromPeaks`) | Loess on universal anchor peaks; gentle and fast |
| Few shared peaks / sparse / strong nonlinear drift | `ObiwarpParam` | Full-profile warping needs no prior peaks |
| Cohort with large case/control compositional differences | `ObiwarpParam`, or `PeakGroupsParam` with `subset =` QC indices | Few universal anchors mis-register the condition-specific metabolome |
| New instrument, no parameter priors | AutoTuner / IPO for a starting neighborhood, then verify against EIC FWHM | Optimizers maximize a surrogate, not biology (McLean 2020) |
| GC-EI data | Deconvolution tools, not xcms peak picking -> metabolomics/msdial-preprocessing | Co-elution + universal fragmentation require component separation first |

## Peak Detection

**Goal:** Detect chromatographic peaks in each centroided file.

**Approach:** Build a `CentWaveParam` with `ppm` and `peakwidth` set from the actual instrument and chromatography (see Quantitative Thresholds), then call `findChromPeaks`.

```r
library(xcms)
# spectraFiles: centroided mzML paths; pd: data.frame with one row per file
raw <- readMsExperiment(spectraFiles = mzml_files, sampleData = pd)

# ppm is across-scan centroid scatter (~2-3x measured error), NOT the spec mass accuracy.
# peakwidth is c(min, max) in SECONDS, measured from EIC base-widths of known peaks.
cwp <- CentWaveParam(ppm = 10, peakwidth = c(2, 20), snthresh = 10,
                     prefilter = c(3, 1000), noise = 1000, mzdiff = -0.001,
                     integrate = 1L, mzCenterFun = 'wMean')
xdata <- findChromPeaks(raw, param = cwp)
nrow(chromPeaks(xdata))
```

## Retention-Time Alignment

**Goal:** Remove cross-run RT drift so the same compound lands at the same RT in every sample.

**Approach:** Choose obiwarp (no prior peaks) or peakGroups (anchor-based); align to a pooled QC, never to file #1. Regroup afterward because RTs changed.

```r
# obiwarp: full-profile warping. binSize here is the m/z profile bin (default 1),
# distinct from PeakDensityParam$binSize and MatchedFilterParam$binSize.
xdata <- adjustRtime(xdata, param = ObiwarpParam(binSize = 0.6))

# peakGroups alternative needs an initial correspondence and good universal anchors:
# xdata <- groupChromPeaks(xdata, param = pdp_anchor)
# xdata <- adjustRtime(xdata, param = PeakGroupsParam(minFraction = 0.85, span = 0.4,
#     subset = which(sampleData(xdata)$sample_type == 'QC'), subsetAdjust = 'average'))
plotAdjustedRtime(xdata)
```

## Correspondence (Grouping)

**Goal:** Match peaks across samples into consensus features.

**Approach:** Peak-density grouping in m/z slices; `bw` is the dominant knob and must reflect residual post-alignment RT scatter, not raw peak width.

```r
pdp <- PeakDensityParam(sampleGroups = sampleData(xdata)$sample_group,
                        bw = 5, minFraction = 0.5, minSamples = 1, binSize = 0.025)
xdata <- groupChromPeaks(xdata, param = pdp)
nrow(featureDefinitions(xdata))
```

## Gap-Filling

**Goal:** Integrate signal for features missing a detected peak in some samples.

**Approach:** `fillChromPeaks` with `ChromPeakAreaParam`; treat filled values as imputations, not measurements.

```r
xdata <- fillChromPeaks(xdata, param = ChromPeakAreaParam())
filled <- chromPeakData(xdata)$is_filled   # logical flag; lives in chromPeakData, not chromPeaks
feat <- featureValues(xdata, value = 'into')        # features x samples matrix
defs <- featureDefinitions(xdata)                   # mzmed / rtmed / npeaks per feature
```

## Redundancy Collapse

**Goal:** Group the same compound's adducts/isotopes/fragments back toward compound spectra before annotation.

**Approach:** CAMERA in order groupFWHM -> groupCorr -> findIsotopes -> findAdducts (isotopes before adducts). Correlation grouping needs enough samples to be meaningful and can over- or under-merge - verify against the table size.

```r
library(CAMERA)
xsa <- xsAnnotate(as(xdata, 'xcmsSet'))
xsa <- groupFWHM(xsa, perfwhm = 0.6)
xsa <- groupCorr(xsa)
xsa <- findIsotopes(xsa, mzabs = 0.01, ppm = 10)
xsa <- findAdducts(xsa, polarity = 'positive')
peaklist <- getPeaklist(xsa)
```

## QC Feature Filtering (Preprocessing/QC Bridge)

**Goal:** Drop features that fail conventional QC, operationalizing Broadhurst 2018 inside the xcms object.

**Approach:** `filterFeatures` with `RsdFilter` (CV in QCs), `DratioFilter` (sd_QC/sd_sample), `PercentMissingFilter`, `BlankFlag`. Drift correction and the full QC pipeline live in metabolomics/normalization-qc.

```r
qc <- sampleData(xdata)$sample_group == 'QC'
study <- sampleData(xdata)$sample_group %in% c('Control', 'Treatment')
xdata <- filterFeatures(xdata, filter = RsdFilter(threshold = 0.3, qcIndex = qc))
xdata <- filterFeatures(xdata, filter = DratioFilter(threshold = 0.5, qcIndex = qc, studyIndex = study))
```

## Per-Method Failure Modes

### ppm set to the spec sheet
- **Trigger:** Setting `ppm = 3` because the Orbitrap datasheet says 3 ppm.
- **Mechanism:** centWave `ppm` is across-scan centroid scatter, which exceeds time-averaged mass accuracy; too tight fragments one ion into short ROIs that each fail `prefilter`.
- **Symptom:** Features vanish entirely (not degrade); the better the instrument spec, the worse it looks.
- **Fix:** Set `ppm` to ~2-3x the empirical per-scan centroid scatter, not the datasheet number.

### peakwidth mismatch
- **Trigger:** Copying the default `c(20, 50)` onto modern UHPLC.
- **Mechanism:** Lower bound too high discards sharp 2-5 s peaks; upper bound too low clips broad HILIC/tailing peaks. No warning is emitted.
- **Symptom:** Real peaks silently absent from the table.
- **Fix:** Measure base-width FWHM from 5-10 known EICs; set `peakwidth ~ c(0.5x min, 2x max)`.

### prefilter/noise/snthresh as the trace guillotine
- **Trigger:** Tuning `snthresh` while `prefilter[I]` already kills the trace.
- **Mechanism:** These are three serial gates on the same low-intensity signal; the lowest wins. On high-baseline instruments the default `I=100` may both under-filter noise and kill trace metabolites.
- **Symptom:** Trace metabolites never appear regardless of `snthresh`.
- **Fix:** Lower `prefilter[I]` first for trace work; the lowest gate dominates.

### bw too coarse / alignment-coupled
- **Trigger:** Copying `bw = 30` onto UHPLC, or choosing `bw` independently of alignment quality.
- **Mechanism:** On UHPLC, `bw=30` merges chromatographically resolved co-eluting compounds; with poor alignment a tight `bw` instead splits one compound across features.
- **Symptom:** Averaged-away differences (over-merge) or duplicate split features (under-merge).
- **Fix:** Set `bw` from residual post-alignment RT scatter (often 2-6 s on UHPLC); inspect EICs of merged/split features.

### gap-filling fabricates intensities
- **Trigger:** Feeding a naively filled table straight into a t-test.
- **Mechanism:** Missingness is MNAR (below LOD); filling integrates the noise floor into a positive number, inflating the absent group's mean and shrinking the fold-change being tested.
- **Symptom:** "Significant" features that are mostly filled in one group.
- **Fix:** Track `is_filled`; report per-feature filled fraction; for inference use unfilled values with MNAR-aware imputation (QRILC/GSimp), reserving the fill for dense exploratory PCA.

### skipping redundancy collapse
- **Trigger:** Treating feature count as compound count.
- **Mechanism:** One compound makes 5-15 features (~90% of features are degenerate, Mahieu 2017); correlated adduct "hits" multiply the multiple-testing burden.
- **Symptom:** Inflated dimensionality; clusters of co-significant features that are one molecule.
- **Fix:** Run CAMERA/RAMClustR before annotation; treat collapse as a tunable false-merge/false-split tradeoff with no ground truth.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| `ppm` Orbitrap/Q-Exactive 5-10, qTOF 15-30 | Tautenhahn 2008; instrument physics | ~2-3x measured across-scan centroid scatter, not spec accuracy |
| `peakwidth` UHPLC c(2,20), HPLC c(10,40), HILIC c(10,60) (s) | Smith 2006; chromatography | Must bracket measured EIC base-widths; default c(20,50) wrong for UHPLC |
| Points across peak >= ~6-7 | Zeng 2023 *JASMS* 34:1136 | Below this, peak-area precision degrades non-linearly; an acquisition limit no parameter recovers |
| `prefilter = c(3, I)` | Tautenhahn 2008 | Min 3 consecutive scans above intensity I; I set per instrument baseline |
| Grouping `bw` 2-6 s (UHPLC) | xcms vignette | Default 30 s merges resolved co-eluting compounds on fast chromatography |
| QC CV (RSD) < 0.20-0.30 | Broadhurst 2018 *Metabolomics* 14:72 | Features with high QC variance are unreliable |
| D-ratio < 0.5 | Broadhurst 2018 | Technical variance must sit well below biological |
| Blank flag k ~ 3-5 | Broadhurst 2018 | Test-sample mean must exceed k x blank mean |
| ~1 compound per 5-15 features | Mahieu 2017 *Anal Chem* 89:10397 | ~90% of detected features are adduct/isotope/fragment degeneracy |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| `could not find function "readMSData"` or legacy verbs missing | Using deprecated `xcmsSet`/`readMSData` API on xcms 4.x | Use `readMsExperiment()` + the `findChromPeaks`/`groupChromPeaks` verbs |
| `unused argument (ppm = ...)` in findChromPeaks | Passing loose args instead of a `*Param` object | Wrap in `CentWaveParam(...)` and pass via `param =` |
| Features defined on uncorrected RT | Skipped the regroup after `adjustRtime` | Call `groupChromPeaks` again after alignment |
| Garbage mass traces, almost no peaks | Profile (non-centroid) data fed to centWave | Centroid first (msconvert vendor peakPicking or `Spectra::pickPeaks`) |
| `sampleGroups` length/semantics error | Vector misaligned with sample order or missing | Pass `sampleData(xdata)$group` matching file order; it is mandatory |
| Three different `binSize` defaults confused | obiwarp (m/z, default 1) vs PeakDensity (m/z, 0.25) vs matchedFilter (m/z, 0.1) | Set each in its own `*Param`; they are not the same knob |
| `as(xdata, 'xcmsSet')` fails or warns | CAMERA expects the legacy container | Coerce the `XcmsExperiment` to `xcmsSet` only for CAMERA; keep modern objects upstream |

## References

- Smith CA, Want EJ, O'Maille G, Abagyan R, Siuzdak G. 2006. XCMS: processing mass spectrometry data for metabolite profiling using nonlinear peak alignment, matching, and identification. *Anal Chem* 78:779-787.
- Tautenhahn R, Bottcher C, Neumann S. 2008. Highly sensitive feature detection for high resolution LC/MS (centWave). *BMC Bioinformatics* 9:504.
- Prince JT, Marcotte EM. 2006. Chromatographic alignment of ESI-LC-MS proteomic data sets by ordered bijective interpolated warping. *Anal Chem* 78:6140-6152.
- Lange E, Tautenhahn R, Neumann S, Gropl C. 2008. Critical assessment of alignment procedures for LC-MS proteomics and metabolomics measurements. *BMC Bioinformatics* 9:375.
- Kuhl C, Tautenhahn R, Bottcher C, Larson TR, Neumann S. 2012. CAMERA: an integrated strategy for compound spectra extraction and annotation of LC/MS data sets. *Anal Chem* 84:283-289.
- Myers OD, Sumner SJ, Li S, Barnes S, Du X. 2017. Detailed investigation and comparison of the XCMS and MZmine 2 chromatogram construction and chromatographic peak detection methods. *Anal Chem* 89:8689-8695.
- Mahieu NG, Patti GJ. 2017. Systems-level annotation of a metabolomics data set reduces 25,000 features to fewer than 1,000 unique metabolites. *Anal Chem* 89:10397-10406.
- McLean CM, Kujawinski EB. 2020. AutoTuner: high fidelity and robust parameter selection for metabolomics data processing. *Anal Chem* 92:5724-5732.
- Broadhurst D, Goodacre R, Reinke SN, Kuligowski J, Wilson ID, Lewis MR, Dunn WB. 2018. Guidelines and considerations for the use of system suitability and quality control samples in mass spectrometry assays applied in untargeted clinical metabolomic studies. *Metabolomics* 14:72.
- Zeng W, Bateman KP. 2023. Quantitative LC-MS/MS. 1. Impact of points across a peak on the accuracy and precision of peak area measurements. *J Am Soc Mass Spectrom* 34(6):1136-1144.
- Louail P, Brunius C, Garcia-Aloy M, et al. 2025. xcms in peak form: now anchoring a complete metabolomics data preprocessing and analysis software ecosystem. *Anal Chem* 97:27639-27645.

## Related Skills

- metabolomics/normalization-qc - Drift correction, CV/D-ratio filtering, and feature-table normalization
- metabolomics/metabolite-annotation - Identification of features into named metabolites
- metabolomics/msdial-preprocessing - GUI/MS-DIAL alternative with MS2Dec deconvolution and GC-EI support
- metabolomics/statistical-analysis - Differential and multivariate statistics on the feature table
<!-- END FILE: metabolomics/xcms-preprocessing/SKILL.md -->

<!-- END CATEGORY: metabolomics -->

