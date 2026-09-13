---
slug: bio-proteomics-integrated
version: 1.0.0
displayName: "蛋白质组学 / Proteomics"
name: bio-proteomics-integrated
summary: >-
  中文：蛋白质组学综合技能，整合 9 个相关专题，覆盖蛋白质组学：质谱数据导入、肽段/蛋白鉴定、DIA分析、定量、差异丰度、PTM分析。 English: Integrated Proteomics skill covering 9 related topics, including Proteomics: mass spec data import, peptide/protein ID, DIA analysis, quantification, differential abundance, PTM analysis.
description: >-
  中文：这是一个面向蛋白质组学的综合生物信息学 Skill，整合当前分类下 9 个相关专题能力。它用于根据研究问题、数据类型和分析阶段，选择合适的方法与工具，规划从输入检查、预处理、核心分析到质量控制、统计解释和结果报告的完整流程。重点覆盖：蛋白质组学：质谱数据导入、肽段/蛋白鉴定、DIA分析、定量、差异丰度、PTM分析。当用户提供相关实验数据、测序结果、表格或研究问题时，它会帮助判断分析目标与前置条件，给出工具选择、关键参数、输入输出、常见失败原因、结果解读和可复现建议。主要工具包括：MSstats, MSstatsPTM, diann。该 Skill 提供分析设计与实施指导，不替代对具体数据质量、生物学背景和最终结论的人工审查。
  English: This is an integrated bioinformatics Skill for Proteomics, combining 9 related topic areas. It helps users choose appropriate methods and tools based on the research question, data type, and analysis stage, and plan an end-to-end workflow from input validation and preprocessing through core analysis, quality control, statistical interpretation, and reporting. It covers Proteomics: mass spec data import, peptide/protein ID, DIA analysis, quantification, differential abundance, PTM analysis. For relevant experimental data, sequencing results, tables, or research questions, it clarifies prerequisites, recommends tools and parameters, describes expected inputs and outputs, explains common failure modes, and supports reproducible analysis. Primary tools include: MSstats, MSstatsPTM, diann. It provides methodological and implementation guidance; final data-quality assessment and biological conclusions still require human review.
---

# proteomics 分类 Skill 整合版

> 本文件整合同一主分类目录下 9 个子目录中的 SKILL.md 内容。
> 各子目录正文按原文保留，并通过标题和边界标记进行区分；源文件中的元数据块未被改写。

---

<!-- BEGIN CATEGORY: proteomics -->

## 子目录：proteomics/data-import

<!-- BEGIN FILE: proteomics/data-import/SKILL.md -->
---
name: bio-proteomics-data-import
description: Loads mass-spectrometry data into Python/R and strips the search engine's bookkeeping before any number is trusted -- removes decoys (REV__/Reverse), contaminants (CON__/Potential contaminant), Only-identified-by-site groups, and resolves semicolon razor/leading protein-ID ambiguity in MaxQuant proteinGroups.txt, DIA-NN report.parquet, and mzML/mzXML. Distinguishes Intensity (raw) vs LFQ intensity (MaxLFQ) vs iBAQ, treats a MaxQuant zero as missing (NaN, not log2(-inf)), and inherits the acquisition mode's missingness contract (DDA MNAR vs DIA MCAR). Use when starting an analysis from raw spectra or a search engine output. Downstream normalization and stats are differential-abundance; reporter-ion/MaxLFQ quant is quantification; protein grouping is protein-inference.
tool_type: mixed
primary_tool: pyOpenMS
---

## Version Compatibility

Reference examples tested with: pyOpenMS 3.1+, pandas 2.2+, numpy 1.26+, MSnbase 2.28+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Mass Spectrometry Data Import -- Inheriting the Acquisition Contract and Stripping the Bookkeeping

**"Load my mass spec data into Python"** -> Parse spectra or a search-engine table AND immediately enforce two contracts -- which quant column carries real biology, and which rows are search-engine bookkeeping that must be deleted -- because the same proteinGroups.txt yields different conclusions depending on the column read and the rows kept.
- Python: `pyopenms.MzMLFile().load(path, exp)` for raw spectra; `pandas.read_csv(sep='\t')` for MaxQuant; `pandas.read_parquet` for DIA-NN
- R: `Spectra::Spectra()` / `QFeatures::readQFeatures()` for raw and quantified data (MSnbase still works but is in maintenance mode)

Scope: this skill owns reading spectra/search outputs into memory, deleting decoy/contaminant/site-only rows, picking the correct quant column, and characterizing missingness. Format conversion (RAW -> mzML) -> peptide-identification. MaxLFQ/TMT reporter quant computation -> quantification. Protein-group parsimony -> protein-inference. Normalization and imputation -> differential-abundance and expression-matrix/normalization. OUT OF SCOPE: statistical testing, batch correction, and the actual imputation step (this skill only diagnoses the missingness so the right imputer is chosen later).

## The Single Most Important Modern Insight -- Import Is Where Two Contracts Are Read and Enforced

1. **A "data import" is never just file parsing -- it is the moment the acquisition mode's quantitative contract and its missingness structure are inherited.** DDA selects the top-N most intense precursors per cycle, and which precursors get picked is partly stochastic and abundance-biased, so the same low-abundance peptide is sampled in run A and missed in run B; this manufactures structured, left-censored MNAR missingness. DIA fragments every precursor in every window every cycle, so its (fewer) missing values are closer to MCAR. The catastrophic error this prevents: imputing a DDA matrix with a mean/KNN method that assumes MCAR, which biases low-abundance proteins upward and manufactures false hits. The mode is born at acquisition and inherited at import; the missingness diagnosis made here dictates which imputation is even legitimate downstream.

2. **The search engine's bookkeeping must be stripped before any number is trusted.** A proteinGroups.txt carries decoy rows (`Reverse == '+'`, `REV__` prefix in the ID) from the target-decoy FDR machinery, contaminant rows (`Potential contaminant == '+'`, `CON__` prefix), and Only-identified-by-site rows (the protein has no unmodified-peptide evidence, only a modified site). Keeping any of these leaks non-biological signal into the intensity matrix and inflates IDs. The catastrophic error: reporting differential abundance on a matrix where decoy or keratin rows survived.

3. **The same proteinGroups.txt yields different biology from different columns, and a zero is not a measurement.** `Intensity` is raw summed precursor signal (not normalized, not comparable across samples for ratios). `LFQ intensity` is MaxLFQ-normalized and is the column for between-sample comparison. `iBAQ` is intensity divided by the number of observable tryptic peptides -- a within-sample molar proxy, not a between-sample quant. MaxQuant writes 0 for "not quantified", so log2(0) = -inf; replace 0 -> NaN before any transform. The catastrophic error: log2-transforming raw `Intensity` (or iBAQ) and reading the ratios as biology.

## Tool Taxonomy

| Tool / method | Citation | Mechanism / role | When |
|---|---|---|---|
| pyOpenMS `MzMLFile().load` | Chambers 2012 (ProteoWizard lineage) | Loads mzML/mzXML into an MSExperiment in memory; iterate spectra by MS level | Programmatic access to raw peaks, precursor m/z, isolation windows |
| pandas `read_csv`/`read_parquet` | -- | Tabular ingest of MaxQuant TSV and DIA-NN parquet | All search-engine output tables |
| DIA-NN report | Demichev 2020 | Long-format precursor table; `report.parquet` is the default (1.9+) and the only default (2.0) | DIA quant; pivot on `PG.MaxLFQ` after q-filtering |
| MaxQuant `txt/` outputs | Cox 2014 (MaxLFQ) | `proteinGroups.txt` (group level), `evidence.txt` (per-PSM) | DDA label-free / TMT search results |
| Spectra + QFeatures (R) | -- | Current Bioconductor raw + quantified-feature containers; `readQFeatures`, `aggregateFeatures` | R pipelines; preferred over MSnbase going forward |
| MSnbase `readMSData` (R) | -- | On-disk raw reading; maintenance mode (route OUT to Spectra/QFeatures) | Legacy R code only |
| ThermoRawFileParser / msconvert | Hulstaert 2020 / Chambers 2012 | RAW -> mzML conversion (route OUT) | File conversion is peptide-identification |

## Decision Tree by Scenario

| Scenario | Recommended | Why |
|---|---|---|
| MaxQuant DDA label-free, between-sample comparison | Read `LFQ intensity` columns from proteinGroups.txt | MaxLFQ-normalized; the only MaxQuant column valid for cross-sample ratios |
| MaxQuant, absolute/molar abundance within one sample | Read `iBAQ` columns | iBAQ is a within-sample molar proxy; do not use across samples |
| Need raw uncorrected signal for a custom normalization | Read `Intensity` columns, normalize yourself | `Intensity` is raw summed precursor area, not comparable as-is |
| DIA-NN output (1.9 or 2.0) | `pd.read_parquet('report.parquet')`, filter q-values, pivot `PG.MaxLFQ` | 2.0 dropped the TSV default; q-filter before pivot or low-confidence rows leak in |
| Raw spectra, need peaks/precursor/isolation window | pyOpenMS `MzMLFile().load` | Programmatic peak and isolation-window access for QC and co-isolation reasoning |
| R-based pipeline, quantified features | QFeatures `readQFeatures` + `aggregateFeatures` | Current Bioconductor; MSnbase is maintenance-only |
| Data came from DDA, planning imputation | Diagnose missingness as MNAR -> route to left-censored imputation | DDA top-N sampling makes missingness abundance-dependent |
| Data came from DIA, planning imputation | Treat missingness as closer to MCAR | DIA samples every precursor every cycle |

Default when uncertain: read `LFQ intensity` (MaxQuant) or `PG.MaxLFQ` after q-filtering (DIA-NN), strip Reverse/contaminant/site-only rows, set 0 -> NaN, then diagnose missingness before choosing an imputer.

## Loading mzML/mzXML with pyOpenMS

**Goal:** Parse raw spectra into memory for QC, peak access, and isolation-window reasoning.

**Approach:** Load into an MSExperiment (filled in place), iterate by MS level; `get_peaks()` returns a tuple of (mz, intensity) numpy arrays, and `getPrecursors()` returns a list.

```python
from pyopenms import MSExperiment, MzMLFile

exp = MSExperiment()
MzMLFile().load('sample.mzML', exp)  # fills exp in place; returns None

for spectrum in exp:
    if spectrum.getMSLevel() == 1:
        mz, intensity = spectrum.get_peaks()  # tuple of two numpy arrays
    elif spectrum.getMSLevel() == 2:
        precursor = spectrum.getPrecursors()[0]  # getPrecursors returns a list
        precursor_mz = precursor.getMZ()
        window = precursor.getIsolationWindowLowerOffset() + precursor.getIsolationWindowUpperOffset()
```

## Loading and Cleaning MaxQuant proteinGroups.txt

**Goal:** Get a trustworthy log2 intensity matrix with bookkeeping rows removed and missing values represented as NaN.

**Approach:** Strip Reverse/contaminant/site-only rows, resolve the semicolon protein-ID list to a leading ID, pick `LFQ intensity` columns, set 0 -> NaN, then log2-transform.

```python
import pandas as pd
import numpy as np

pg = pd.read_csv('proteinGroups.txt', sep='\t', low_memory=False)  # mixed-type cols

# Flag columns hold '+' or empty string; all three are proteinGroups-only bookkeeping
mask = (pg.get('Reverse', '') != '+') & (pg.get('Potential contaminant', '') != '+') & (pg.get('Only identified by site', '') != '+')
pg = pg[mask].copy()

# Protein IDs / Majority protein IDs / Gene names are SEMICOLON lists; take the first (leading/razor) entry
pg['leading_protein'] = pg['Protein IDs'].str.split(';').str[0]
pg['leading_gene'] = pg['Gene names'].where(pg['Gene names'].notna(), '').str.split(';').str[0]

lfq_cols = [c for c in pg.columns if c.startswith('LFQ intensity ')]  # MaxLFQ-normalized, between-sample comparable
matrix = pg[['leading_protein', 'leading_gene'] + lfq_cols].copy()
matrix[lfq_cols] = matrix[lfq_cols].replace(0, np.nan)  # MaxQuant writes 0 for missing; log2(0) = -inf
matrix[lfq_cols] = np.log2(matrix[lfq_cols])
```

## Loading DIA-NN report.parquet

**Goal:** Reshape the long DIA-NN report into a confident protein-by-run matrix.

**Approach:** Read the parquet (default since 1.9, only default in 2.0), filter precursor- AND protein-group q-values to 1% FDR BEFORE pivoting on `PG.MaxLFQ`.

```python
import pandas as pd

report = pd.read_parquet('report.parquet')  # report.tsv dropped as default in DIA-NN 2.0
report = report[(report['Q.Value'] <= 0.01) & (report['PG.Q.Value'] <= 0.01)]  # 1% FDR before quant

matrix = report.pivot_table(index='Protein.Group', columns='Run', values='PG.MaxLFQ', aggfunc='first')
```

## Diagnosing the Missingness Contract

**Goal:** Quantify the missing-value pattern so the legitimate imputation class can be chosen downstream.

**Approach:** Count NaN per protein and per sample; relate the pattern to acquisition mode (DDA -> structured MNAR; DIA -> closer to MCAR). A correlation between missingness and mean abundance is the MNAR signature.

```python
import numpy as np

def assess_missingness(matrix, sample_cols):
    miss_per_protein = matrix[sample_cols].isna().sum(axis=1)
    miss_per_sample = matrix[sample_cols].isna().sum(axis=0)
    total_pct = 100 * matrix[sample_cols].isna().sum().sum() / matrix[sample_cols].size
    mean_abund = matrix[sample_cols].mean(axis=1)  # negative corr with missingness => MNAR / left-censored
    mnar_corr = mean_abund.corr(miss_per_protein)
    return {'per_protein': miss_per_protein, 'per_sample': miss_per_sample, 'total_pct': total_pct, 'abundance_missing_corr': mnar_corr}
```

## Per-Method Failure Modes

### MaxQuant wrong quant column

**Trigger:** Reading `Intensity` (raw) or `iBAQ` when between-sample ratios are intended.
**Mechanism:** `Intensity` is un-normalized summed precursor signal; `iBAQ` is a within-sample molar proxy. Neither is comparable across samples the way `LFQ intensity` is.
**Symptom:** Ratios track total loaded protein / sample depth rather than biology; fold changes shift when one sample's loading changes.
**Fix:** Use `LFQ intensity` for cross-sample comparison; if computing custom normalization use `Intensity` and normalize explicitly (expression-matrix/normalization).

### Zero treated as a measurement

**Trigger:** `np.log2` applied directly to a MaxQuant matrix still containing 0.
**Mechanism:** MaxQuant encodes "not quantified" as 0; log2(0) = -inf, which then propagates into means and tests.
**Symptom:** -inf values, NaN means, proteins silently dropped or skewed.
**Fix:** `replace(0, np.nan)` before any transform; then diagnose missingness.

### Bookkeeping rows survive

**Trigger:** Loading proteinGroups.txt without filtering Reverse / Potential contaminant / Only identified by site.
**Mechanism:** Decoys exist only for FDR estimation; contaminants are keratin/trypsin/BSA, not the sample; site-only groups have no unmodified-peptide quant evidence. `Only identified by site` exists only in proteinGroups.txt.
**Symptom:** Inflated protein counts; a "hit" that is a decoy or keratin.
**Fix:** Filter all three flag columns; cross-check with `REV__`/`CON__` ID prefixes when joining to peptide tables. Caveat: do not delete CON__ rows blindly if a contaminant (e.g. keratin) is the protein of interest.

### Razor / leading protein-ID ambiguity ignored

**Trigger:** Treating `Protein IDs` or `Gene names` as an atomic single value.
**Mechanism:** These are semicolon-delimited lists; the first entry is the leading (razor) protein for the group, and `Gene names` can be blank while protein IDs are present.
**Symptom:** Merges fail, NaN gene labels, ambiguous identity downstream.
**Fix:** Split on `;` and take the first entry; guard `Gene names` with `.notna()`. Group parsimony details -> protein-inference.

### Stale DIA-NN parsing

**Trigger:** Reading `report.tsv` on DIA-NN 2.0, or pivoting before q-filtering.
**Mechanism:** 2.0 defaults to (and only defaults to) `report.parquet`; pivoting unfiltered rows includes precursors above 1% FDR.
**Symptom:** FileNotFoundError on report.tsv; or low-confidence quant inflating the matrix.
**Fix:** `pd.read_parquet('report.parquet')`; filter `Q.Value <= 0.01 & PG.Q.Value <= 0.01` before pivoting `PG.MaxLFQ`.

### MNAR imputed as MCAR

**Trigger:** Mean/median/KNN imputation on a DDA matrix.
**Mechanism:** DDA missingness is abundance-dependent (left-censored); MCAR imputers fill missing low values with the central tendency, biasing them upward.
**Symptom:** Low-abundance proteins gain false high values; spurious differential hits.
**Fix:** Diagnose the abundance-missingness correlation here; route DDA to left-censored imputation (downshifted-Gaussian / QRILC / MinProb) in differential-abundance; DIA tolerates standard imputers.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|---|---|---|
| DIA-NN import filter `Q.Value <= 0.01` AND `PG.Q.Value <= 0.01` | Demichev 2020; target-decoy convention | Precursor- and protein-group-level 1% FDR enforced before any quant value is used |
| Peptide/protein FDR 1% (q <= 0.01) | Target-decoy convention | Standard ID confidence at both peptide and protein levels |
| MaxQuant zero -> NaN | MaxQuant output convention | 0 encodes "not quantified"; log2(0) = -inf corrupts every transform |
| Min peptides per protein for quant >= 2 | Community quant practice | Single-peptide ("one-hit-wonder") proteins are ID/quant-unreliable |
| Valid-value filter >= 50-70% per group | Modeling choice (document per study) | Caps imputation burden; the exact cutoff is a study decision, not a universal constant |
| Take FIRST semicolon entry as leading protein/gene | MaxQuant proteinGroups convention | The leading/razor protein is the group identifier; trailing entries are shared-peptide members |

## Common Errors

| Error / symptom | Cause | Solution |
|---|---|---|
| `-inf` values after log2 | Zeros not converted to NaN | `df.replace(0, np.nan)` before `np.log2` |
| `FileNotFoundError: report.tsv` (DIA-NN 2.0) | TSV no longer the default output | `pd.read_parquet('report.parquet')` |
| `KeyError: 'Only identified by site'` | That column exists ONLY in proteinGroups.txt | Use `df.get('Only identified by site', '')` or guard the column lookup |
| Mixed-type / DtypeWarning on MaxQuant load | Wide TSV with mixed column types | `pd.read_csv(..., low_memory=False)` |
| NaN gene labels break a merge | `Gene names` is a semicolon list, sometimes blank | `.where(notna(), '').str.split(';').str[0]` |
| Ratios track loading not biology | Read `Intensity` (raw) instead of `LFQ intensity` | Use `LFQ intensity` for between-sample comparison |
| `get_peaks()` unpacking error | Expecting a 2D array | It returns a tuple `(mz, intensity)` of two numpy arrays |

## References

- Cox J, Hein MY, Luber CA, Paron I, Nagaraj N, Mann M. 2014. Accurate proteome-wide label-free quantification by delayed normalization and maximal peptide ratio extraction, termed MaxLFQ. *Mol Cell Proteomics* 13(9):2513-2526.
- Demichev V, Messner CB, Vernardis SI, Lilley KS, Ralser M. 2020. DIA-NN: neural networks and interference correction enable deep proteome coverage in high throughput. *Nat Methods* 17(1):41-44.
- Chambers MC, Maclean B, Burke R, et al. 2012. A cross-platform toolkit for mass spectrometry and proteomics. *Nat Biotechnol* 30(10):918-920.
- Hulstaert N, Shofstahl J, Sachsenberg T, et al. 2020. ThermoRawFileParser: modular, scalable, and cross-platform RAW file conversion. *J Proteome Res* 19(1):537-542.

## Related Skills

- peptide-identification - search raw spectra and convert vendor RAW to mzML
- quantification - compute MaxLFQ and TMT reporter-ion quantities from imported data
- protein-inference - resolve protein-group parsimony and razor assignment
- differential-abundance - normalize, impute (per the missingness diagnosis), and test
- proteomics-qc - assess run-level identification and quant quality
- dia-analysis - run DIA-NN to produce the report this skill imports
- expression-matrix/normalization - general intensity-matrix normalization patterns
- workflows/proteomics-pipeline - end-to-end pipeline that begins with this import step
<!-- END FILE: proteomics/data-import/SKILL.md -->

## 子目录：proteomics/dia-analysis

<!-- BEGIN FILE: proteomics/dia-analysis/SKILL.md -->
---
name: bio-proteomics-dia-analysis
description: Analyzes data-independent acquisition (DIA) proteomics by scoring reconstructed fragment-chromatogram peak groups against a decoy null with DIA-NN (library-free directDIA, library-based, or deep-learning predicted-library routes), Spectronaut, OpenSWATH, and EncyclopeDIA. Frames the deliverable around q-value LEVEL (precursor/peptide/protein-group) and CONTEXT (run vs experiment-wide/global) rather than a bare "1% FDR", and around the duty-cycle-vs-selectivity acquisition tradeoff (window design, staggered demultiplexing, diaPASEF, narrow-window Astral). Use when identifying and quantifying proteins from DIA mass spectrometry runs and filtering DIA-NN report.parquet/matrix output. Building the spectral library itself is spectral-libraries; normalization and protein roll-up is quantification; statistical testing of the matrix is differential-abundance.
tool_type: cli
primary_tool: diann
---

## Version Compatibility

Reference examples tested with: DIA-NN 1.9+, pandas 2.2+, pyarrow 15+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# DIA Analysis -- Scoring Reconstructed Peak Groups Against a Decoy Null, Filtered at the Right q-Value Context

**"Identify and quantify proteins from my DIA runs"** -> Reconstruct, per candidate peptide, a set of co-eluting fragment extracted-ion chromatograms (XICs) and score whether that peak group is real against a decoy null -- because every wide-isolation-window MS2 is chimeric, so the problem is deconvolution and peak-group scoring, not spectrum matching.
- CLI: `diann --fasta-search` for library-free (directDIA) discovery and quantification
- CLI: `diann --lib predicted.speclib` for the deep-learning predicted-library route (the modern default)
- CLI: `diann --lib experimental.tsv` for an experimental or chromatogram library
- CLI: `OpenSwathWorkflow` + `pyprophet` when explicit run/experiment/global FDR contexts must be auditable

Scope: this skill OWNS running the DIA search engine and FILTERING its output at the correct q-value level and context. Building the library (experimental, chromatogram, predicted) -> spectral-libraries. Normalization, MaxLFQ roll-up, and matrix summarization -> quantification. Statistical testing of the protein matrix -> differential-abundance. Loading raw vendor/mzML data -> data-import. OUT OF SCOPE: DDA spectrum-to-peptide matching (peptide-identification); pathway enrichment of the hit list; acquiring the data (the analyst inherits the window design from the core facility).

## The Single Most Important Modern Insight -- The q-Value Context Is a Study-Design Choice, Not a Default

1. **DIA quantification is peak-group SCORING against a decoy null, not spectrum matching.** Gillet 2012 inverted DDA: instead of asking "what peptide is this spectrum", DIA asks, per library peptide, "does a co-eluting peak group of this peptide's expected fragments exist in the chimeric MS2 stream". Decoys are shuffled or reversed peptide queries scored identically; the q-value is the expected fraction of accepted IDs that are decoy-like false peak groups. The count of "proteins found" is therefore a function of the decoy-calibrated threshold, never a quality metric in itself.

2. **"1% FDR" is meaningless without naming the LEVEL and the CONTEXT -- state both.** LEVEL = precursor vs peptide vs protein-group (filtering precursors at 1% does NOT give proteins at 1%; control both). CONTEXT = run-specific vs experiment-wide vs global (Rosenberger 2017). Naively filtering N runs at per-run 1% inflates the experiment-wide error: 1% per run accumulates false positives across the union, severe at hundreds-to-thousands of runs. For a cross-run matrix, filter on the GLOBAL protein-group q-value, not the per-run one. The column chosen (`Q.Value` vs `Global.PG.Q.Value`) is the decision.

3. **The predicted-library route is now the default recommendation.** Library-based search is sensitive but capped by an ill-matched library (wrong organism/tissue/mods silently limits coverage with no error). Library-free directDIA finds sample-specific content but its larger implicit search space can INFLATE IDs if FDR is not controlled across the two-pass process -- worst on wide-window chimeric data. The compromise the field converged on: predict an in-silico library for the whole FASTA digest (DIA-NN built-in predictor, or Prosit/AlphaPeptDeep) and search against THAT, getting directDIA's "no wet-lab library" with library-based's bounded, better-calibrated search.

## Chimerism, Deconvolution, and the Window Design the Analyst Inherits

DDA picks top-N precursors and fragments each in isolation, so every MS2 is nominally one peptide. DIA abandons selection: the quadrupole steps through wide isolation windows (4-25 Th classically, 2 Th on Astral, mobility-gated on timsTOF) and co-fragments EVERY precursor in each window. Consequence: every DIA MS2 is chimeric, a superposition of fragments from all co-isolated precursors. The engine must deconvolve -- reconstruct each candidate's fragment XICs and score the peak group.

Selectivity is set by isolation-window WIDTH. Narrower window = fewer co-isolated precursors = less chimerism = cleaner XICs = fewer false peak groups. But narrower windows mean MORE windows per cycle -> longer duty cycle -> fewer points across each LC peak -> worse quant precision. The central acquisition tradeoff is duty cycle (sampling speed) vs selectivity (window width). Rule of thumb: aim for >= 6 MS2 points across the FWHM of an LC peak for reliable quant. The analyst INHERITS this design and must not pretend all DIA is equivalent:

- Fixed windows (classic SWATH): 32 x 25 Th. Simple; wastes selectivity because precursor density is non-uniform across m/z.
- Variable windows: widths chosen so each holds roughly equal precursor density (narrow where the proteome is dense ~600-800 m/z). Orbitrap best practice.
- Staggered / overlapping windows + demultiplexing (Amodei 2019): two interleaved patterns offset by half a window; demultiplexing recovers effective windows of half the physical width without halving duty cycle. CRITICAL trap: staggered data MUST be demultiplexed at conversion (`msconvert --filter "demultiplex optimization=overlap_only"`) or every tool sees the wide physical window and the selectivity benefit is silently lost. MSX (randomized window combinations) is largely historical.
- diaPASEF (Meier 2020): on timsTOF the isolation tile rides the m/z-vs-ion-mobility diagonal, so only precursors sharing BOTH m/z AND mobility co-isolate -- the mobility dimension is an orthogonal selectivity filter for free. The engine extracts a 4D peak group (RT x m/z x fragment x mobility).
- Narrow-window Astral (Guzman 2024): >200 Hz MS/MS makes 2-Th windows feasible across the whole range; at 2 Th the MS2 is nearly non-chimeric, which makes library-free directDIA far more trustworthy than it was on 25-Th SWATH.

## Tool Taxonomy

| Tool / method | Citation | Mechanism / role | When |
|---------------|----------|------------------|------|
| DIA-NN | Demichev 2020 | Deep-NN peak-group scoring + interference correction + QuantUMS quant; library-free, predicted, or library-based | Default for high-throughput, large cohorts, diaPASEF, Astral; free, scriptable |
| Spectronaut | Biognosys (commercial) | directDIA+ pipeline with in-app DL prediction; mature GUI/QC | Regulated/clinical work, polished QC, mixed vendors, when licensed |
| OpenSWATH + PyProphet | Rost 2014; Rosenberger 2017 | Classic peptide-centric extraction + semi-supervised scoring with explicit run/experiment/global q-contexts | When auditable FDR-context control is required; library-based ONLY, needs iRT/RT alignment |
| EncyclopeDIA / Walnut | Searle 2018 | Chromatogram-library search (.dlib/.elib) + GPF; Walnut = library-free mode | Building project-specific chromatogram-library depth on Orbitrap |
| FragPipe (MSFragger-DIA / DIA-Umpire) | -- | Spectrum-centric via pseudo-spectra + Philosopher FDR; IonQuant explicit MBR-FDR | Unified DDA+DIA shop in the MSFragger ecosystem |
| Skyline | MacCoss lab | Targeted/visual peak inspection and demultiplexing; not a discovery engine | Manual peak curation, PRM, library curation -- the microscope, not the engine |
| AlphaDIA | Mann lab | Open transformer-based end-to-end Python; AlphaPeptDeep predictions | Cutting-edge open research, Astral, Python-native pipelines |
| Library build | (route OUT) | Experimental/chromatogram/predicted library construction | -> spectral-libraries |
| Stats on the matrix | (route OUT) | Normalization, roll-up, moderated testing | -> quantification, differential-abundance |

Tool leadership moves fast (Astral, AlphaDIA, DIA-NN releases). Confirm the current recommended engine and version for the specific instrument before committing rather than hard-coding "DIA-NN is best".

## Decision Tree by Scenario

| Scenario | Recommended | Why |
|----------|-------------|-----|
| Discovery cohort, no wet-lab library | `diann --fasta-search --gen-spec-lib` (predicted route) then search against it | Bounded, better-calibrated search vs raw directDIA; the modern default |
| Quick single-run discovery, Astral 2-Th data | DIA-NN library-free (directDIA) | Near-non-chimeric MS2 makes directDIA trustworthy |
| Have a deep experimental/chromatogram library | `diann --lib library.tsv` (no `--fasta-search`) | Targeted extraction is most sensitive when the library matches |
| Need auditable run/experiment/global FDR for a regulated submission | OpenSWATH + PyProphet | Explicit q-value contexts per Rosenberger 2017 |
| Building chromatogram-library depth for one project on Orbitrap | EncyclopeDIA (GPF) -> .elib -> DIA-NN | Empirical RT and real fragmentation in the project's own LC |
| Large cohort (hundreds-thousands of runs) | DIA-NN `--reanalyse`, filter on `Global.PG.Q.Value` | Two-pass global FDR controls cross-run error accumulation |
| Staggered/overlapping acquisition | Demultiplex at conversion FIRST, then any engine | Skipping demux silently keeps wide-window interference |
| PTM / peptidoform-resolved work | DIA-NN `--peptidoforms` + matched variable mods | Peptidoform-resolved target-decoy scoring |

Default when uncertain: DIA-NN with the predicted-library route (`--fasta-search --gen-spec-lib --reanalyse`), letting `--mass-acc 0` auto-optimize, then filter `Q.Value <= 0.01 & PG.Q.Value <= 0.01` per run and `Global.PG.Q.Value <= 0.01` for cross-run matrices.

## DIA-NN -- Predicted-Library (directDIA) Route

The default route: digest the FASTA in silico, predict a library, and search the DIA data against it in one command. `--mass-acc 0` lets DIA-NN auto-optimize tolerances per file (do not hard-code ppm from another instrument). `--reanalyse` enables the two-pass global FDR / MBR that controls directDIA double-dipping.

```bash
diann \
    --f sample1.mzML --f sample2.mzML \
    --lib "" --fasta uniprot_human.fasta --fasta-search \
    --gen-spec-lib --predictor \
    --out diann_out/report.parquet \
    --out-lib diann_out/report-lib.tsv \
    --qvalue 0.01 \
    --matrices \
    --mass-acc 0 \
    --reanalyse --smart-profiling \
    --cut K*,R* --missed-cleavages 1 \
    --min-pep-len 7 --max-pep-len 30 \
    --unimod4 --var-mods 1 --var-mod UniMod:35,15.994915,M \
    --threads 8
```

## DIA-NN -- Library-Based Route

Supply an existing library (experimental, chromatogram-derived, or a previously predicted `.speclib`). Omit `--fasta-search`: extraction is targeted to the library content.

```bash
diann \
    --f sample1.mzML --f sample2.mzML \
    --lib spectral_library.tsv \
    --out diann_out/report.parquet \
    --qvalue 0.01 --matrices \
    --mass-acc 0 \
    --reanalyse --smart-profiling \
    --threads 8
```

## DIA-NN Output and Correct Filtering

DIA-NN 1.9+ writes the main report as Apache Parquet (`report.parquet`) by default; 2.0 makes it the only default. Matrices stay TSV. Pipelines hard-coding `report.tsv` silently break or read a stale file -- read parquet. Filter on q-value columns BEFORE pivoting to a matrix.

```
report.parquet          # main report (1.9+ default; was report.tsv pre-1.9)
report.stats.tsv        # per-run statistics
report.pg_matrix.tsv    # protein-group wide matrix
report.pr_matrix.tsv    # precursor wide matrix (verify exact dotting vs installed version)
report.gg_matrix.tsv    # gene-group wide matrix
report-lib.tsv          # generated library (if --gen-spec-lib)
```

```python
import pandas as pd, numpy as np
report = pd.read_parquet('diann_out/report.parquet')  # NOT report.tsv on 1.9+

# Per-run filter: both LEVELS. Add Global.PG.Q.Value for the cross-run matrix.
filt = report[(report['Q.Value'] <= 0.01) &
              (report['PG.Q.Value'] <= 0.01) &
              (report['Global.PG.Q.Value'] <= 0.01)]  # 0.01 = standard 1% FDR

# Pivot to a protein matrix from the filtered long report.
pg = filt.pivot_table(index='Protein.Group', columns='Run', values='PG.MaxLFQ', aggfunc='first')
pg = np.log2(pg.replace(0, np.nan))  # DIA-NN writes 0 for not-quantified; log2(0) = -Inf
```

The `*_matrix.tsv` files apply an EXTRA 5% run-specific protein FDR (DIA-NN default, `--matrix-spec-q`), so the matrix protein count can be lower than the report count. A report-vs-matrix mismatch is EXPECTED, not a bug -- do not panic and do not compare the two counts as if they should match.

## Generating a Predicted Library Outside DIA-NN

DIA-NN's built-in predictor covers the common case. For an external predicted library from FragPipe search results, EasyPQP builds it; FragPipe can also emit a DIA-NN-format library directly.

```bash
# Real easypqp subcommands: library, convert, insilico-library (NOT a convert --format diann).
easypqp library \
    --psmtsv psm.tsv \
    --rt_reference irt.tsv \
    --peptide_fdr_threshold 0.01 \
    --protein_fdr_threshold 0.01 \
    --out library.tsv
# FragPipe's DIA workflow can emit a DIA-NN-format library directly -- prefer that when in FragPipe.
```

## Per-Method Failure Modes

### Library-free (directDIA)
**Trigger:** `--fasta-search` on wide-window (25-Th SWATH) data without two-pass global FDR.
**Mechanism:** building the library from the same data then quantifying it reuses the data twice; the large implicit search space inflates IDs when decoys are not controlled across both passes.
**Symptom:** implausibly high protein counts, poor reproducibility across replicates.
**Fix:** keep `--reanalyse` (two-pass global FDR) ON and filter on `Global.PG.Q.Value`; prefer the predicted-library route on chimeric data.

### Library-based
**Trigger:** library organism/tissue/modifications/gradient do not match the sample.
**Mechanism:** targeted extraction can only find what is in the library; a mismatched library caps coverage with no error.
**Symptom:** low ID counts, conserved-peptide bias (e.g. a human library on a mouse sample finds only conserved peptides).
**Fix:** match the library to the biology (mods especially); regenerate via spectral-libraries or switch to the predicted route.

### Cross-run cohort FDR
**Trigger:** filtering N runs at per-run `Q.Value <= 0.01` and unioning.
**Mechanism:** 1% per run accumulates across the union -> experiment-wide error far above 1%.
**Symptom:** inflated total protein list; irreproducible "hits" in differential testing.
**Fix:** filter on `Global.PG.Q.Value <= 0.01` (and optionally `Lib.PG.Q.Value <= 0.01`) for the matrix.

### Match-between-runs (MBR)
**Trigger:** treating MBR-transferred quant values as equally confident as directly identified ones.
**Mechanism:** transferring an ID by RT/m/z/CCS matching can be a false transfer, especially for low-abundance precursors; MBR has its OWN FDR.
**Symptom:** spurious low-abundance quant filling missing values that should stay missing.
**Fix:** rely on DIA-NN's global/empirical-library q-values (IonQuant uses an explicit MBR-FDR model); do not disable `--reanalyse` then trust per-run counts.

### Staggered acquisition
**Trigger:** running staggered/overlapping data through any engine without demultiplexing.
**Mechanism:** the engine sees the wide physical window, keeping all the interference the staggering was meant to remove.
**Symptom:** noisy directDIA, poor selectivity on data that should be clean.
**Fix:** demultiplex at conversion (`msconvert --filter "demultiplex optimization=overlap_only"`) before search.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| Precursor q-value `<= 0.01` | DIA-NN default (`--qvalue 0.01`) | Standard 1% per-precursor FDR (run context). |
| `Global.PG.Q.Value <= 0.01` | Rosenberger 2017 | Experiment-wide protein-group FDR for cross-run matrices; run-specific PG q-value is NOT enough for a cohort. |
| Matrix run-specific PG filter `0.05` | DIA-NN default (`--matrix-spec-q`) | Extra 5% run-specific protein FDR applied only when building matrices -> report vs matrix count differs (expected). |
| `Lib.(PG.)Q.Value <= 0.01` | Demichev recommendation | For very large cohorts, also filter the global library-pass q-values to keep experiment-wide FDR honest. |
| Points per peak `>= 6` across FWHM | community rule of thumb | Below this, quant precision and peak detection degrade; drives window/cycle design. |
| Mass accuracy auto (`--mass-acc 0`) | DIA-NN | Wrong tolerance silently kills IDs; let DIA-NN auto-calibrate rather than hard-coding ppm from another instrument. |
| Missed cleavages `1` | -- | Trypsin standard; raising it expands the search space and the multiple-testing burden. |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| `FileNotFoundError: report.tsv` or stale data | DIA-NN 1.9+ default is `report.parquet`, not `report.tsv` | Read `report.parquet` (`pd.read_parquet`); request legacy TSV explicitly only if needed |
| Matrix protein count < report count, looks like data loss | Matrices apply an extra 5% run-specific PG filter | Expected; do not compare the two counts as if equal |
| `-Inf` after log2 of the matrix | DIA-NN writes 0 for not-quantified | Convert `0 -> NaN` BEFORE log2/normalization |
| Cohort "hits" do not reproduce | Filtered per-run `Q.Value` only, not global | Filter `Global.PG.Q.Value <= 0.01` for the matrix |
| `easypqp convert --format diann` errors | No such interface; `convert`/`library`/`insilico-library` are the real subcommands | Use `easypqp library` (with `--psmtsv`/`--rt_reference`) or let FragPipe emit a DIA-NN-format library |
| `KeyError: 'report.pr.matrix.tsv'` | Matrix filename dotting varies by version (`pr_matrix` vs `pr.matrix`) | `ls` the output dir after a run and match the installed version's exact names |
| directDIA looks noisy on overlapping-window data | Staggered data not demultiplexed | Demultiplex at conversion before search |

## References

- Gillet LC, Navarro P, Tate S, et al. Targeted data extraction of the MS/MS spectra generated by data-independent acquisition: a new concept for consistent and accurate proteome analysis. *Mol Cell Proteomics* 2012;11(6):O111.016717.
- Rost HL, Rosenberger G, Navarro P, et al. OpenSWATH enables automated, targeted analysis of data-independent acquisition MS data. *Nat Biotechnol* 2014;32(3):219-223.
- Rosenberger G, Bludau I, Schmitt U, et al. Statistical control of peptide and protein error rates in large-scale targeted data-independent acquisition analyses. *Nat Methods* 2017;14(9):921-927.
- Searle BC, Pino LK, Egertson JD, et al. Chromatogram libraries improve peptide detection and quantification by data independent acquisition mass spectrometry. *Nat Commun* 2018;9:5128.
- Demichev V, Messner CB, Vernardis SI, Lilley KS, Ralser M. DIA-NN: neural networks and interference correction enable deep proteome coverage in high throughput. *Nat Methods* 2020;17(1):41-44.
- Meier F, Brunner AD, Frank M, et al. diaPASEF: parallel accumulation-serial fragmentation combined with data-independent acquisition. *Nat Methods* 2020;17(12):1229-1236.
- Amodei D, Egertson J, MacLean BX, et al. Improving precursor selectivity in data-independent acquisition using overlapping windows. *J Am Soc Mass Spectrom* 2019;30(4):669-684.
- Savitski MM, Wilhelm M, Hahne H, Kuster B, Bantscheff M. A scalable approach for protein false discovery rate estimation in large proteomic data sets. *Mol Cell Proteomics* 2015;14(9):2394-2404.
- Guzman UH, Martinez-Val A, Olsen JV, et al. Ultra-fast label-free quantification and comprehensive proteome coverage with narrow-window data-independent acquisition. *Nat Biotechnol* 2024;42:1855-1866.

## Related Skills

- spectral-libraries - Build experimental, chromatogram, or predicted libraries to search against
- quantification - Normalization, MaxLFQ roll-up, and matrix summarization after filtering
- differential-abundance - Moderated statistical testing of the protein matrix
- proteomics-qc - Per-run ID counts, missing-value rates, and acquisition QC
- data-import - Convert and load raw vendor/mzML data before the search
- peptide-identification - DDA spectrum-to-peptide matching (the non-DIA counterpart)
- workflows/proteomics-pipeline - End-to-end DIA-to-differential-abundance orchestration
<!-- END FILE: proteomics/dia-analysis/SKILL.md -->

## 子目录：proteomics/differential-abundance

<!-- BEGIN FILE: proteomics/differential-abundance/SKILL.md -->
---
name: bio-proteomics-differential-abundance
description: Tests for differentially abundant proteins between conditions with limma/DEqMS empirical-Bayes moderation, proDA/msqrob2/MSstats missingness modeling, and Python Welch+BH alternatives. Frames missing values as left-censored MNAR (model, do not impute), makes variance moderation the load-bearing step at n=3-5, and prefers feature/peptide-level testing. Use when identifying proteins with significant abundance changes between experimental groups. Summarization and normalization mechanics are proteomics/quantification; volcano and MA plots are data-visualization/volcano-and-ma-plots; pathway enrichment of the hit list is pathway-analysis/go-enrichment.
tool_type: mixed
primary_tool: limma
---

## Version Compatibility

Reference examples tested with: limma 3.58+, DEqMS 1.20+, proDA 1.20+, ashr 2.2+, pandas 2.2+, scipy 1.12+, statsmodels 0.14+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Differential Protein Abundance -- Moderated Testing on a Log-Intensity Matrix with Honest Missingness

**"Find differentially abundant proteins between my conditions"** -> Moderated statistical testing on a normalized log-intensity matrix, carrying missingness in the likelihood instead of filling it in -- because the missing values are low BECAUSE the protein is low, and imputing them manufactures false positives.
- R: `limma::eBayes(fit, trend=TRUE, robust=TRUE)` for empirical-Bayes moderated t-tests (the protein-level workhorse)
- R: `DEqMS::spectraCounteBayes()` when PSM/peptide counts are available (preferred over limma-trend when quant depth varies)
- R: `proDA::test_diff()` / `msqrob2` / `MSstats` when missing values are extensive (model the dropout, no imputation)
- Python: `scipy.stats.ttest_ind(equal_var=False)` + `statsmodels` BH (large n only; no moderation)

Scope: this skill owns the statistical TEST -- design/contrast construction, variance moderation, missingness handling, multiple-testing correction, minimum-fold-change testing, and fold-change shrinkage. Peptide-to-protein summarization and normalization mechanics -> proteomics/quantification. Volcano/MA plots -> data-visualization/volcano-and-ma-plots. Enrichment of the hit list -> pathway-analysis/go-enrichment. OUT OF SCOPE: how MaxLFQ/TMP/IRS produce the matrix (quantification); how to draw a volcano (data-visualization).

## The Single Most Important Modern Insight -- Model the Missingness, Moderate the Variance, Test at the Feature Level

1. **Missing values in label-free MS are left-censored MNAR -- missing BECAUSE the intensity is low -- and imputing them (especially Perseus/MaxQuant downshift) manufactures SYSTEMATIC false positives.** Downshift draws each missing value from a narrow Gaussian (mean = mu - 1.8*sigma, SD = 0.3*sigma). For an on/off protein (seen in all of group A, missing in all of B) the t-statistic numerator is inflated by construction (mean_B fixed ~1.8 sigma below observed, deterministic) and the denominator is artificially deflated (all imputed B values from one 0.3-sigma Gaussian -> collapsed within-group SD) -> enormous t -> tiny p. Because every on/off protein is treated identically, the false positives are systematic: the volcano-plot "anchor/wing" artifact (rigid near-vertical streaks of pinned points far out on both x-axis sides). The honest statement is "undetected in group B", not "20x lower, p=1e-6". The correct approach is to MODEL the dropout in the likelihood -- proDA (probabilistic dropout), msqrob2, MSstats-AFT -- NOT fill it (Lazar 2016; Ahlmann-Eltze & Anders 2019).
2. **At the n=3-5 replicates proteomics actually uses, per-protein variance has only 2-4 residual df and is unusable raw -- variance moderation is the load-bearing element, not optional.** limma borrows a prior d0 across all proteins so a 4-replicate design tests on ~10 df instead of 6; `trend=TRUE` makes the prior a function of mean intensity (effectively mandatory for label-free, where a single global prior mis-calibrates FDR across the abundance range); `robust=TRUE` Winsorizes outlier variances (Phipson 2016). DEqMS makes the prior a function of PSM/peptide count and generally outperforms limma-trend when quantification depth varies across proteins (Zhu 2020).
3. **Feature/peptide-level modeling beats summarize-then-test.** Summarizing first (one number per protein per run) discards the within-protein between-peptide variance and the correct degrees of freedom: 12 consistent peptides deserve a smaller SE than 12 disagreeing ones, but after summarization both look equally certain, and a protein with 30 observations looks as informative as one with 3. msqrob2/MSstats keep every peptide as a degree of freedom; this is why the same data gives different answers (Goeminne 2016; Sticker 2020; Choi 2014).

## Tool Taxonomy

| Tool / method | Citation | Mechanism / role | When |
|---------------|----------|------------------|------|
| limma | Ritchie 2015; Phipson 2016 | EB moderated t; posterior variance blends a prior d0 with the per-protein estimate; `trend` ties the prior to mean intensity, `robust` Winsorizes outliers | protein-level summaries, small n, the default workhorse |
| DEqMS | Zhu 2020 | prior variance = loess of log-variance vs log2(count); precision follows quantification DEPTH not just intensity | TMT (count=PSM) and label-free DDA (count=peptide); quant depth varies; preferred over limma-trend |
| proDA | Ahlmann-Eltze & Anders 2019 (preprint) | probabilistic dropout: missing = left-censored, integrated under a per-sample sigmoid dropout curve; EB on location and variance; no imputation | label-free DDA with many MNAR missing values, small n, proteins absent in one group |
| msqrob2 | Sticker 2020; Goeminne 2016 | peptide-level robust ridge: Huber M-estimation downweights outlier peptides, ridge shrinks effects from few observations, EB variance moderation | label-free DDA, outlier-peptide / unbalanced-coverage risk; best FDR in hard spike-in regimes |
| MSstats | Choi 2014 | feature-level linear mixed model (group fixed + feature + run/subject random); AFT censored handling for missing | SRM/PRM/DIA, technical replicates, nested/repeated-measures, labeled designs |
| Welch t-test + BH | -- | per-protein two-sample t with `equal_var=False` + Benjamini-Hochberg | large n (>10/group), Python-only; no moderation, unusable at n=3-5 |
| ashr | Stephens 2017 | mixture prior with a point mass at zero; posterior means shrink uncertain effects toward zero | recovering "which proteins truly changed and by how much" (not for GSEA ranking) |
| volcano / MA plot | -- | (route OUT) | visualization -> data-visualization/volcano-and-ma-plots |
| enrichment of hits | -- | (route OUT) | functional interpretation -> pathway-analysis/go-enrichment |

## Decision Tree by Scenario

| Scenario | Recommended | Why |
|----------|-------------|-----|
| Small n (3-5/group), protein-level summary matrix | limma `eBayes(trend=TRUE, robust=TRUE)` | EB borrows variance across proteins; the trend calibrates FDR across abundance |
| PSM/peptide counts available (TMT or label-free DDA) | DEqMS `spectraCounteBayes` | prior keyed on quant depth removes single-PSM false positives limma admits |
| Label-free with many MNAR missing values, on/off proteins | proDA `test_diff` | models the censored dropout; never imputes; correct verdict for "undetected in one group" |
| Outlier-peptide risk, unbalanced peptide coverage | msqrob2 (peptide-level robust ridge) | keeps feature df; Huber downweights bad peptides; best FDR in spike-in benchmarks |
| Technical replicates, nested/repeated-measures, labeled (SRM/PRM/DIA) | MSstats (feature-level mixed model) | random effects capture run/subject structure summarize-then-test discards |
| Batch present | batch as a covariate in the design (`~ batch + condition`) | `removeBatchEffect` is visualization-only; never feed its output to `lmFit` |
| Minimum biologically meaningful fold change | `treat()` + `topTreat()` (or SAM s0) | tests |log2FC|>c against the moderated null; a post-hoc FC+significance double filter inflates FDR |
| Large n (>10/group), Python-only | Welch t-test + BH | variance estimates reliable; no moderation needed at large n |

Default when uncertain: protein-level summary matrix at n=3-5 -> limma `eBayes(trend=TRUE, robust=TRUE)`; if PSM/peptide counts exist, escalate to DEqMS; if missingness is extensive and intensity-dependent, escalate to proDA.

## limma Workflow (R)

**Goal:** Identify differentially abundant proteins using moderated statistics that borrow information across all proteins.

**Approach:** Build the design (batch as a covariate when present), fit the linear model and contrast, apply EB moderation with the intensity trend and robust fitting, then extract BH-corrected results. Never feed `removeBatchEffect` output to `lmFit`.

```r
library(limma)

design <- model.matrix(~0 + condition + batch, data = sample_info)  # batch in the model, not removed first
colnames(design)[1:2] <- levels(factor(sample_info$condition))

fit <- lmFit(protein_matrix, design)
contrast_matrix <- makeContrasts(Treatment - Control, levels = design)
fit2 <- contrasts.fit(fit, contrast_matrix)
fit2 <- eBayes(fit2, trend = TRUE, robust = TRUE)  # trend mandatory for label-free; robust Winsorizes outliers

results <- topTable(fit2, coef = 1, number = Inf, adjust.method = 'BH')
# columns: logFC, AveExpr, t, P.Value, adj.P.Val, B  (adj.P.Val is the BH p; there is no $FDR)
```

### Minimum-fold-change testing

**Goal:** Call proteins whose effect exceeds a biologically meaningful threshold, not merely differ from zero.

**Approach:** Use `treat()` against the moderated null and read `topTreat()`. NEVER `topTable(lfc=...)` nor a post-hoc volcano double filter (`abs(logFC) > 1 & adj.P.Val < 0.05`); conditioning on both the FC and the p-value selects for high-variance nulls (a collider effect) and inflates realized FDR above 50% (Ebrahimpoor & Goeman 2021).

```r
LFC_THRESHOLD <- log2(1.2)  # 1.2-fold floor; treat tests against this null, no double-filter FDR inflation
fit2 <- treat(fit2, lfc = LFC_THRESHOLD)
results <- topTreat(fit2, coef = 1, number = Inf)  # topTreat omits the B column
```

## DEqMS Workflow (R)

**Goal:** Improve on limma by tying each protein's prior variance to its quantification depth -- proteins measured by more PSMs/peptides are more precise.

**Approach:** Run limma through `eBayes`, attach the count vector, then apply DEqMS's count-aware EB. Use PSM count for TMT (quant at MS2) and peptide count for label-free DDA; for multi-batch TMT use the MINIMUM count across batches (the bottleneck batch sets precision).

```r
library(DEqMS)

# fit2 is the limma fit through eBayes (above)
fit2$count <- psm_count_per_protein[rownames(fit2$coefficients)]  # PSM for TMT, peptide for LFQ; min across batches
fit3 <- spectraCounteBayes(fit2)

results <- outputResult(fit3, coef_col = 1)
# adds sca.t, sca.P.Value, sca.adj.pval (the count-adjusted statistics; use these, not the limma columns)
```

## proDA Workflow (R)

**Goal:** Test proteins with extensive MNAR missingness, including on/off proteins, without imputing a single value.

**Approach:** Fit the probabilistic-dropout model directly on the log-intensity matrix; missing values contribute as left-censored observations under a per-sample dropout curve. Then test the contrast against zero.

```r
library(proDA)

fit <- proDA(protein_matrix, design = ~condition, col_data = sample_info,
             reference_level = 'Control')
result_names(fit)  # list testable coefficients first
results <- test_diff(fit, conditionTreatment - conditionControl)
# columns: name, pval, adj_pval, diff (log2FC), t_statistic, se
```

## Python Workflow

**Goal:** Run the full pipeline in Python when no R is available and n is large enough that moderation is unnecessary.

**Approach:** Log2-transform, median-normalize, run per-protein Welch t-tests, apply Benjamini-Hochberg. This has NO variance moderation and should not be used at n=3-5 -- escalate to limma/DEqMS for small n.

```python
import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.multitest import multipletests

def preprocess(intensities):
    log2_data = np.log2(intensities.replace(0, np.nan))  # zeros -> NaN to avoid -inf
    sample_medians = log2_data.median(axis=0)
    return log2_data - sample_medians + sample_medians.median()

def differential_abundance(normalized, case_cols, ctrl_cols):
    rows = []
    for protein in normalized.index:
        case, ctrl = normalized.loc[protein, case_cols].dropna(), normalized.loc[protein, ctrl_cols].dropna()
        if len(case) >= 2 and len(ctrl) >= 2:
            _, pval = stats.ttest_ind(case, ctrl, equal_var=False)  # Welch; scipy defaults to Student's True
            rows.append({'protein': protein, 'log2fc': case.mean() - ctrl.mean(), 'pvalue': pval})
    df = pd.DataFrame(rows)
    df['padj'] = multipletests(df['pvalue'], method='fdr_bh')[1]  # default is Holm-Sidak; pass fdr_bh explicitly
    return df
```

## Fold-Change Reporting

**Goal:** Hand the right effect estimate to the right consumer.

**Approach:** Report the RAW fold change (the best unbiased point estimate) for GSEA/pathway ranking and meta-analysis -- those need the full continuous distribution or FC+SE pairs. Apply shrinkage (ashr) only when recovering "which proteins truly changed and by how much"; it fits a mixture prior with a point mass at zero and shrinks uncertain effects smoothly toward zero. This is preferred over hard-thresholding (zeroing FCs at padj 0.05), which creates an arbitrary step function. No mature Python ashr equivalent exists.

```r
library(ashr)

se <- sqrt(fit2$s2.post) * fit2$stdev.unscaled[, 1]
shrunk <- ash(fit2$coefficients[, 1], se, mixcompdist = 'normal')
shrunken_fc <- shrunk$result$PosteriorMean  # report alongside raw logFC, not as a replacement for GSEA
lfsr <- shrunk$result$lfsr
```

## Per-Method Failure Modes

### Downshift / any imputation feeding a variance-based test
**Trigger:** Perseus/MaxQuant downshift (or MinDet/MinProb/QRILC) fills NAs, then limma/t-test runs on the filled matrix.
**Mechanism:** Imputed values come from one narrow Gaussian -> fabricated low within-group variance + deterministic mean offset -> inflated t.
**Symptom:** Volcano "anchor/wing" -- rigid near-vertical streaks of pinned on/off proteins at high significance; realized FDR far above nominal.
**Fix:** Model the missingness instead (proDA / msqrob2 / MSstats-AFT); report on/off proteins as "undetected in group X".

### kNN imputation on left-censored data
**Trigger:** kNN/mean imputation applied to label-free data with MNAR dropout.
**Mechanism:** Mean-reverting -- pulls a truly-low (missing because low) value UP toward the mean.
**Symptom:** Real down-regulation is compressed; down hits weakened or lost.
**Fix:** Only valid under MCAR/MAR; for MNAR model the dropout. Under uncertainty Lazar 2016 shows the milder MCAR error beats MNAR-imputers slamming random highs to the floor.

### removeBatchEffect before testing
**Trigger:** `removeBatchEffect()` output fed to `lmFit`.
**Mechanism:** Subtracts the fitted batch component with no uncertainty propagation -> understated residual variance, inflated EB df; if batch is confounded with biology it deletes real signal.
**Symptom:** Anticonservative p-values; lost true effects when cases/controls split by batch.
**Fix:** Include batch as a covariate in the SAME model (`~ batch + condition`); use `removeBatchEffect` only for PCA/visualization.

### eBayes(trend=FALSE) on intensity data
**Trigger:** Plain `eBayes` (trend off) on a log-intensity matrix.
**Mechanism:** A single global prior over-shrinks high-abundance and under-shrinks low-abundance proteins.
**Symptom:** Mis-calibrated FDR across the abundance range.
**Fix:** `eBayes(trend = TRUE, robust = TRUE)`; escalate to DEqMS when quant depth varies.

### Wrong DEqMS count column
**Trigger:** Razor+unique counts vs MS2-level PSMs, or total-across-batches vs minimum-across-batches.
**Mechanism:** The variance-vs-count prior is fit on the wrong precision proxy.
**Symptom:** Mis-ranked proteins; the count moderation helps the wrong ones.
**Fix:** PSM count for TMT, peptide count for label-free; minimum count across batches for multi-batch TMT.

### proDA on MCAR missingness
**Trigger:** proDA applied where dropout is random (e.g. a TMT channel lost at random), not detection-limited.
**Mechanism:** The left-censored dropout model is mis-specified.
**Symptom:** Biased estimates; the model fits a dropout curve that does not exist.
**Fix:** proDA needs intensity-dependent missingness; for MCAR use limma/DEqMS on the observed values.

### FC + significance double filter
**Trigger:** `abs(logFC) > 1 & adj.P.Val < 0.05` applied after the test.
**Mechanism:** |logFC| is large for a true effect OR a large SE; filtering on both the FC and the p (both depend on SE) selects high-variance nulls (collider effect).
**Symptom:** Realized FDR above 50% at nominal 5% (Ebrahimpoor & Goeman 2021).
**Fix:** `treat()`+`topTreat()` or SAM s0, which sit inside the statistic before selection.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| n=3-5 replicates -> 2-4 residual df | -- | raw per-protein variance unusable; moderation is mandatory, not optional |
| limma adds prior d0 (~4) df | Ritchie 2015 | a 4-replicate design tests on ~10 df vs 6; the borrowed df is the benefit |
| downshift mean = mu - 1.8*sigma, SD = 0.3*sigma | Perseus default | 1.8 places imputed mass ~3.6th percentile; 0.3 gives only 30% of real spread -> manufactured false positives |
| `trend=TRUE` effectively mandatory for label-free | Ritchie 2015 | a single global prior mis-calibrates FDR across abundance |
| min-FC floor log2(1.2) (1.2-fold) via treat() | -- | example floor; common alternatives 1.5-fold (~0.58) or 2-fold (1.0); set by biology, tested against the moderated null |
| BH adjusted p < 0.05 | Benjamini-Hochberg | controls FDR over the WHOLE rejection set, not subsets carved out afterward |
| DEqMS multi-batch TMT: minimum count across batches | Zhu 2020 | the bottleneck batch sets the realized precision |
| realized FDR > 50% from FC+significance double filter | Ebrahimpoor & Goeman 2021 | top-100 at n=12 exceeded 50% FDR at nominal 5% |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| `results$FDR` is NULL | limma `topTable`/`topTreat` have no `$FDR` column | use `adj.P.Val` (BH-adjusted p) |
| `topTreat` row has no `B` | `topTreat` omits `B` (a `topTable` column) | read `logFC, AveExpr, t, P.Value, adj.P.Val` |
| FDR mis-calibrated across abundance | `eBayes` with `trend=FALSE` on intensity data | `eBayes(fit, trend = TRUE, robust = TRUE)` |
| min-FC test inflates FDR | `topTable(lfc=...)` or post-hoc volcano double filter | `treat(fit, lfc=log2(1.2))` then `topTreat()` |
| anticonservative p after batch correction | `removeBatchEffect` output fed to `lmFit` | put batch in the design: `~ batch + condition` |
| DEqMS columns missing | forgot `fit$count` or read limma columns | set `fit$count`, run `spectraCounteBayes`, read `sca.adj.pval` from `outputResult` |
| Student's t instead of Welch | `scipy.stats.ttest_ind` defaults `equal_var=True` | pass `equal_var=False` |
| p-values look like Holm-Sidak | `statsmodels` `multipletests` defaults to `'hs'` | pass `method='fdr_bh'` |
| volcano "anchor/wing" streaks | downshift/imputation feeding the test | model dropout (proDA/msqrob2/MSstats-AFT); report on/off proteins as undetected |

## References

- Ritchie ME, Phipson B, Wu D, Hu Y, Law CW, Shi W, Smyth GK. 2015. limma powers differential expression analyses for RNA-sequencing and microarray studies. *Nucleic Acids Res* 43(7):e47.
- Phipson B, Lee S, Majewski IJ, Alexander WS, Smyth GK. 2016. Robust hyperparameter estimation protects against hypervariable genes and improves power to detect differential expression. *Ann Appl Stat* 10(2):946-963.
- Zhu Y, Orre LM, Zhou Tran Y, et al. 2020. DEqMS: a method for accurate variance estimation in differential protein expression analysis. *Mol Cell Proteomics* 19(6):1047-1057.
- Ahlmann-Eltze C, Anders S. 2019. proDA: probabilistic dropout analysis for identifying differentially abundant proteins in label-free mass spectrometry. *bioRxiv* 661496 (preprint; cite `citation("proDA")`, never a journal).
- Choi M, Chang CY, Clough T, Broudy D, Killeen T, MacLean B, Vitek O. 2014. MSstats: an R package for statistical analysis of quantitative mass spectrometry-based proteomic experiments. *Bioinformatics* 30(17):2524-2526.
- Goeminne LJE, Gevaert K, Clement L. 2016. Peptide-level robust ridge regression improves estimation, sensitivity, and specificity in data-dependent quantitative label-free shotgun proteomics. *Mol Cell Proteomics* 15(2):657-668.
- Sticker A, Goeminne L, Martens L, Clement L. 2020. Robust summarization and inference in proteome-wide label-free quantification. *Mol Cell Proteomics* 19(7):1209-1219.
- Lazar C, Gatto L, Ferro M, Bruley C, Burger T. 2016. Accounting for the multiple natures of missing values in label-free quantitative proteomics data sets to compare imputation strategies. *J Proteome Res* 15(4):1116-1125.
- Stephens M. 2017. False discovery rates: a new deal. *Biostatistics* 18(2):275-294.
- Ebrahimpoor M, Goeman JJ. 2021. Inflated false discovery rate due to volcano plots: problem and solutions. *Brief Bioinform* 22(5):bbab053.

## Related Skills

- quantification - peptide-to-protein summarization, normalization, and IRS that produce the matrix this skill tests
- proteomics-qc - quality control and batch-effect assessment before testing
- protein-inference - razor/shared-peptide ambiguity that drives which protein group gets the quantity
- ptm-analysis - site-level differential testing for modified peptides
- differential-expression/de-results - analogous empirical-Bayes interpretation for RNA-seq DE
- data-visualization/volcano-and-ma-plots - volcano and MA plots of the result table
- pathway-analysis/go-enrichment - functional enrichment of the significant protein hit list
- machine-learning/biomarker-discovery - building predictive panels from differential proteins
- workflows/proteomics-pipeline - end-to-end pipeline that calls this skill as the testing stage
<!-- END FILE: proteomics/differential-abundance/SKILL.md -->

## 子目录：proteomics/peptide-identification

<!-- BEGIN FILE: proteomics/peptide-identification/SKILL.md -->
---
name: bio-proteomics-peptide-identification
description: Peptide-spectrum matching from MS/MS with target-decoy FDR control, framing identification confidence as a property of a ranked list (q-value/PEP) rather than a raw engine score (XCorr, hyperscore, Andromeda, SpecEValue). Covers sequence-database search engines (Comet, MS-GF+, MSFragger, Sage, MaxQuant, MetaMorpheus), concatenated vs separate target-decoy competition, PEP vs q-value, the multi-level FDR cascade, open/mass-tolerant search, rescoring (Percolator, mokapot, MS2Rescore), and pyOpenMS SimpleSearchEngineAlgorithm + FalseDiscoveryRate. Use when identifying peptides from tandem mass spectra and deciding what FDR threshold to act on. Protein grouping and protein-level FDR are protein-inference; PTM site localization is ptm-analysis; DIA peptide-centric scoring is dia-analysis; intensity quant is quantification.
tool_type: mixed
primary_tool: pyOpenMS
---

## Version Compatibility

Reference examples tested with: pyOpenMS 3.1+, pandas 2.2+, numpy 1.26+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Peptide Identification -- Confidence Is a Property of a Ranked List, Not a Single PSM

**"Identify peptides from my MS/MS spectra"** -> Match tandem mass spectra against a protein database, then control false discovery rate by target-decoy competition and act on a q-value -- because a raw match score is meaningless in isolation; only the list-level error rate is interpretable.
- Python: `pyopenms.SimpleSearchEngineAlgorithm().search(...)` for in-process database search, `FalseDiscoveryRate` for q-values
- CLI: `comet`, `msfragger`, `sage`, `MSGFPlus` for high-throughput database searching, `percolator`/`mokapot` for rescoring
- R: `mzID::mzID()` + `flatten()` or `mzR::openIDfile()` + `psms()` to read mzIdentML search results

Scope: this skill owns spectrum-to-peptide matching and PSM/peptide-level FDR. Protein grouping and protein-level (picked) FDR -> protein-inference. PTM site localization and open-search mod discovery follow-up -> ptm-analysis. DIA peptide-centric extraction and scoring -> dia-analysis. FDR-filtered IDs feeding intensities -> quantification. mzML/raw loading -> data-import. OUT OF SCOPE: protein inference, PTM localization scoring, DIA peptide-centric pipelines, label-free/TMT quantification.

## The Single Most Important Modern Insight -- A q-value Is a Verdict on the List, a Raw Score Is Not Even Comparable

1. **Identification confidence is a property of a ranked LIST controlled by target-decoy competition, never a property of one PSM.** The number to act on is a q-value (list-level) or PEP (per-PSM), NOT the engine's raw score. XCorr (Comet), hyperscore (MSFragger/X!Tandem), Andromeda score (MaxQuant), and SpecEValue (MS-GF+) live on different scales, are charge- and length-dependent, and are frequently not even monotone in true probability within a single engine -- which is exactly why rescoring (Percolator/mokapot) exists. "1% FDR" answers "what fraction of the list I keep is wrong," NOT "I am 99% sure of this one ID." The catastrophic error is thresholding on a raw score, or comparing scores across engines.

2. **A q-value is valid only if (a) the decoy DB is a faithful null, (b) targets and decoys competed in ONE concatenated search, and (c) there are enough PSMs for the decoy count to be stable.** Generate decoys at the PROTEIN level then digest (so decoy peptides obey the same enzyme rules), matching the target in size and composition. Concatenated competition gives FDR = (#decoys above threshold) / (#targets above threshold) -- one decoy above threshold estimates one false target. Separate target/decoy searches instead need either the simple Elias-Gygi 2x-decoy estimator FDR = 2 * #decoy / (#target + #decoy) or the more refined mix-max estimator (Keich, Kertesz-Farkas & Noble 2015) -- two distinct options for the separate-search setting, NOT the same formula. Mixing the concatenated and separate forms up is the most common silent FDR error.

3. **PEP and q-value answer different questions; filtering at "PEP <= 0.01" is far stricter than "q <= 0.01."** PEP (posterior error probability, local FDR) is the probability that THIS PSM is wrong; q-value is the FDR of the list cut at this PSM. FDR is the average of PEP over the accepted set (Kall 2008). The worst PSM in a 1%-FDR list typically has a PEP of 10-50%. Use q-value for list cutoffs; use PEP only for per-ID decisions (e.g. picking one PTM site). And PSM-FDR at 1% does NOT give 1% peptide-FDR or 1% protein-FDR -- each level needs its own estimation; hand protein-level control to protein-inference.

## The FDR Vocabulary, Precisely

- **FDR**: the expected proportion of false positives among ALL accepted items at a threshold -- a property of the whole list.
- **q-value**: the minimum FDR at which a given PSM is still accepted; monotone after taking the running minimum from the bottom of the ranked list. Filter on q <= 0.01.
- **PEP (local FDR)**: the probability that THIS PSM is wrong given its score. Local, per-PSM; FDR is the integral of PEP over the accepted set (Kall 2008, "two sides of the same coin").
- **The estimator must match the search mode.** Concatenated target-decoy competition (TDC): FDR = #decoy / #target (no factor 2 -- one best hit per spectrum already resolves the competition). Separate target and decoy searches: either the simple Elias-Gygi 2x-decoy estimator FDR = 2 * #decoy / (#target + #decoy), or the more refined mix-max estimator (Keich, Kertesz-Farkas & Noble 2015). Mix-max is a distinct, calibrated-score procedure for the separate-search setting -- it is NOT a rename of the 2x formula.

## Tool Taxonomy

| Tool / method | Citation | Mechanism / role | When |
|---|---|---|---|
| Comet | Eng 2013 | XCorr + E-value; SEQUEST lineage, open-source | Robust default, TPP pipelines; pairs with Percolator |
| X!Tandem | -- | hyperscore + refinement passes | Legacy/free; semi-tryptic refinement niche |
| MS-GF+ | Kim & Pevzner 2014 | SpecEValue via generating-function DP | Calibrated cross-instrument E-value; ETD/CID, low-res, non-standard enzymes |
| MaxQuant / Andromeda | Cox 2011 | binomial probability score; integrated MBR/LFQ/TMT | All-in-one quant pipeline (LFQ, TMT, SILAC); GUI |
| MSFragger | Kong 2017 | hyperscore via fragment-ion indexing (~100x faster) | Open/mass-tolerant search, PTM discovery, huge datasets; core of FragPipe |
| Sage | Lazear 2023 | hyperscore-style, Rust, rescoring-native | Modern scalable open-source pipelines; emits Percolator-ready features |
| MetaMorpheus | Solntsev 2018 | calibration + G-PTM-D multinotch | PTM discovery with built-in calibration; proteoform-aware |
| pFind 3 | Chi 2018 | open-search engine | Maximal unrestricted-PTM/mutation discovery |
| Percolator | Kall 2007 | semi-supervised SVM re-rank on decoy negatives | Boost IDs at fixed FDR; non-tryptic/PTM/large search spaces |
| mokapot | Fondrie & Noble 2021 | Percolator in Python; swappable XGBoost classifier | Python pipelines, Sage output, custom features |
| MS2Rescore + DeepLC + MS2PIP | Declercq 2022; Bouwmeester 2021; Gabriels 2019 | predicted-RT + predicted-intensity rescoring features | Sharpen target/decoy separation; immunopeptidomics |
| Spectral-library search | -- | match empirical reference spectra (intensity + RT) | Faster/more specific for known peptides -> spectral-libraries |
| Protein grouping / protein FDR | Savitski 2015; The 2016 | picked / picked-group FDR | route OUT -> protein-inference |
| PTM site localization | -- | per-site PEP, localization scoring | route OUT -> ptm-analysis |

## Decision Tree by Scenario

| Scenario | Recommended | Why |
|---|---|---|
| Standard DDA, clean FDR, scriptable | Comet or Sage + Percolator/mokapot at q <= 0.01 | well-validated; rescoring boosts IDs at fixed FDR |
| Cross-instrument / varied fragmentation / odd enzyme | MS-GF+ | SpecEValue is calibrated so a threshold means the same everywhere |
| Discover unknown PTMs / mass shifts | MSFragger open search (-150..+500 Da) | fragment indexing makes wide-window search feasible; then closed search on discovered mods -> ptm-analysis |
| Huge dataset, reproducible, cloud-scale | Sage (rescoring-native) | Rust speed; emits Percolator features directly |
| All-in-one with quant in the same tool | MaxQuant/Andromeda | integrated LFQ/TMT/SILAC and MBR |
| Non-tryptic (immunopeptidomics, degradomics) | any engine + Percolator/MS2Rescore | rescoring gains are largest where search space explodes |
| Few PSMs (single-protein pulldown) | do NOT trust decoy FDR; inspect spectra manually | decoy counts too noisy below ~hundreds of PSMs |
| Need per-site / per-ID confidence | act on PEP, not q-value | q-value is list-level; PEP is local |

Default when uncertain: concatenated target-decoy search with Comet or Sage, rescore with Percolator/mokapot, filter at q <= 0.01, and hand protein-level FDR to protein-inference.

### Database Search with pyOpenMS

**Goal:** Match tandem mass spectra in an mzML file against a protein FASTA and produce scored PSMs as idXML.

**Approach:** `SimpleSearchEngineAlgorithm` actually scores spectra (the hand-rolled `ProteaseDigestion` loop only digests, it never matches a spectrum). The FASTA must already contain target + decoy sequences concatenated for downstream FDR; decoys carry a recognizable prefix.

```python
from pyopenms import SimpleSearchEngineAlgorithm, IdXMLFile

protein_ids = []
peptide_ids = []
search = SimpleSearchEngineAlgorithm()
# spectra are scored against in-silico fragment ions of every candidate peptide
search.search('sample.mzML', 'human_target_decoy.fasta', protein_ids, peptide_ids)

# protein_ids FIRST in load/store -- the OpenMS argument order is fixed
IdXMLFile().store('search_results.idXML', protein_ids, peptide_ids)
```

### Annotate Target/Decoy and Estimate FDR with pyOpenMS

**Goal:** Convert raw PSM scores into q-values and keep only PSMs at 1% FDR.

**Approach:** `PeptideIndexing` maps each PSM back to proteins and flags target vs decoy from the decoy prefix; `FalseDiscoveryRate.apply` runs the concatenated competition; `IDFilter` keeps q <= 0.01. This is the real pyOpenMS path -- not a hand-rolled decoy/target ratio of unknown provenance.

```python
from pyopenms import PeptideIndexing, FalseDiscoveryRate, IDFilter, FASTAFile

fasta = []
FASTAFile().load('human_target_decoy.fasta', fasta)
indexer = PeptideIndexing()
params = indexer.getParameters()
params.setValue('decoy_string', 'DECOY_')      # must match the decoy prefix in the FASTA
params.setValue('decoy_string_position', 'prefix')
indexer.setParameters(params)
indexer.run(fasta, protein_ids, peptide_ids)   # sets target/decoy flags on every hit

FalseDiscoveryRate().apply(peptide_ids)         # concatenated competition -> per-PSM q-value as the new score
IDFilter().filterHitsByScore(peptide_ids, 0.01) # 0.01 = 1% FDR, the community list-level standard
IDFilter().removeDecoyHits(peptide_ids)
```

### FDR from a Results Table (concatenated competition, made explicit)

**Goal:** Compute q-values from any engine's PSM table when the search was a single concatenated target-decoy search.

**Approach:** Rank by score, walk down accumulating target and decoy counts, FDR = decoys/targets, then take the running minimum from the bottom to get monotone q-values. The decoy/target form is correct ONLY for concatenated competition; separate searches need either the Elias-Gygi 2x-decoy form or the mix-max estimator (Keich, Kertesz-Farkas & Noble 2015).

```python
import pandas as pd

psms = pd.read_csv('search_results.tsv', sep='\t')
psms['is_decoy'] = psms['protein'].str.startswith(('DECOY_', 'REV_', 'XXX_'))
psms = psms.sort_values('score', ascending=False).reset_index(drop=True)

# concatenated target-decoy competition: each decoy above threshold estimates one false target
targets = (~psms['is_decoy']).cumsum()
decoys = psms['is_decoy'].cumsum()
psms['fdr'] = decoys / targets
psms['qvalue'] = psms['fdr'][::-1].cummin()[::-1]   # running min from the bottom -> monotone q-values

kept = psms[(psms['qvalue'] <= 0.01) & (~psms['is_decoy'])]   # 1% list-level FDR
```

## Per-Method Failure Modes

### Concatenated vs separate FDR formula mismatch
**Trigger:** applying #decoy/#target to separately-searched targets and decoys, or 2*decoy/(target+decoy) to concatenated competition.
**Mechanism:** the factor of 2 accounts for false hits that could land in either independent database; concatenated competition already resolves that by a single best hit per spectrum.
**Symptom:** systematically under- or over-estimated FDR; irreproducible ID counts.
**Fix:** confirm the search mode; concatenated -> #decoy/#target; separate -> Elias-Gygi 2x-decoy or the mix-max estimator (Keich, Kertesz-Farkas & Noble 2015). In Percolator, mix-max is the default for separate-search input and `-Y`/`--post-processing-tdc` selects target-decoy competition instead; concatenated input forces TDC automatically.

### Thresholding on raw engine score
**Trigger:** filtering on XCorr/hyperscore/Andromeda score, or comparing scores from two engines.
**Mechanism:** scores are uncalibrated, charge/length-dependent, and not monotone in true probability.
**Symptom:** different cutoffs admit different real FDRs; cross-engine merges nonsensical.
**Fix:** always convert to q-value (or SpecEValue/PEP) first; rescore with Percolator/mokapot.

### Decoy FDR on too few PSMs
**Trigger:** reporting "0% FDR" from a single-protein pulldown or tiny PSM list.
**Mechanism:** the decoy count is a noisy Poisson-like estimate; zero observed decoys does not mean zero false targets.
**Symptom:** spuriously confident IDs from small experiments.
**Fix:** below ~hundreds of PSMs, inspect spectra manually; do not act on the decoy q-value.

### Open-search results used for clean FDR or quant
**Trigger:** taking IDs from a wide-window (-150..+500 Da) search as final, FDR-controlled results.
**Mechanism:** wide windows admit "free" mass shifts that inflate random matches; the target-decoy null differs per mass-shift bin.
**Symptom:** inflated, unreliable FDR on open-search output.
**Fix:** treat open search as discovery; follow with a closed search restricted to the discovered mods -> ptm-analysis.

### Rescoring overfitting
**Trigger:** custom features that leak label information, or training without proper cross-validation.
**Mechanism:** the model learns the decoys, making rescored FDR optimistic.
**Symptom:** ID counts jump but downstream validation fails.
**Fix:** use Percolator/mokapot default cross-validation; predicted-feature rescoring (DeepLC/MS2PIP) is safer; validate with entrapment for high-stakes claims (Wen 2025).

### DIA tool FDR taken at face value
**Trigger:** trusting a DIA tool's reported 1% peptide/protein FDR.
**Mechanism:** entrapment shows several DIA tools do not reliably control FDR (Wen 2025).
**Symptom:** real error rate exceeds the reported FDR.
**Fix:** validate with entrapment for high-stakes DIA claims -> dia-analysis.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|---|---|---|
| Precursor tolerance 10-20 ppm (high-res Orbitrap) | -- | matches FT mass accuracy; tighter = fewer random candidates at fixed FDR |
| Precursor tolerance -150..+500 Da (open search) | Kong 2017 | captures arbitrary PTM/mutation shifts; feasible only with fragment indexing |
| Fragment tolerance 0.02 Da (HCD Orbitrap) / 0.6 Da (ion-trap CID) | -- | instrument-dependent; 0.6 Da on Orbitrap discards resolving power |
| Missed cleavages 2 | -- | covers incomplete trypsin digestion without exploding search space |
| PSM/peptide FDR 1% (q <= 0.01) | Elias & Gygi 2007 | community standard; list-level error, not per-PSM |
| Decoy:target ratio 1:1 | Elias & Gygi 2007 | standard; unequal ratios need formula correction |
| Min PSMs for trustworthy decoy FDR: hundreds+ | -- | below this the decoy count is too noisy |
| Variable mods per peptide <= 2-3 | -- | each variable mod multiplies search space and random-match rate |

## Common Errors

| Error / symptom | Cause | Solution |
|---|---|---|
| pyOpenMS "search" returns peptides but never scores spectra | used `ProteaseDigestion`, which only digests a FASTA | use `SimpleSearchEngineAlgorithm().search(mzML, fasta, protein_ids, peptide_ids)` |
| `IdXMLFile().load/store` argument error | wrong order | protein_ids FIRST: `IdXMLFile().load(path, protein_ids, peptide_ids)` |
| FDR ignores decoys / all q-values 0 | decoys not annotated before `FalseDiscoveryRate` | run `PeptideIndexing` with matching `decoy_string` first |
| R: `MSnbase::readMzIdData` not found | that function name does not exist | use `mzID::mzID(file)` + `flatten()`, or `mzR::openIDfile()` + `psms()` (PSMatch/Spectra is the modern path) |
| Percolator q-method mismatched to search mode | mix-max is the default for separate-search input | for separate searches, mix-max (default) or `-Y`/`--post-processing-tdc` for target-decoy competition; concatenated input forces TDC automatically; use `--picked-protein` for protein FDR |
| 1% PSM FDR assumed to give 1% protein FDR | each level needs its own estimation | estimate protein-level (picked) FDR -> protein-inference |
| "PEP <= 0.01" returns far fewer IDs than expected | PEP is per-PSM and far stricter than q-value | filter list cutoffs on q-value; reserve PEP for per-ID decisions |

## References

- Elias, J.E. & Gygi, S.P. 2007. Target-decoy search strategy for increased confidence in large-scale protein identifications by mass spectrometry. *Nature Methods* 4(3):207-214.
- Keich, U., Kertesz-Farkas, A. & Noble, W.S. 2015. Improved false discovery rate estimation procedure for shotgun proteomics. *Journal of Proteome Research* 14(8):3148-3161.
- Kall, L., Canterbury, J.D., Weston, J., Noble, W.S. & MacCoss, M.J. 2007. Semi-supervised learning for peptide identification from shotgun proteomics datasets. *Nature Methods* 4(11):923-925.
- Kall, L., Storey, J.D., MacCoss, M.J. & Noble, W.S. 2008. Posterior error probabilities and false discovery rates: two sides of the same coin. *Journal of Proteome Research* 7(1):40-44.
- Eng, J.K., Jahan, T.A. & Hoopmann, M.R. 2013. Comet: an open-source MS/MS sequence database search tool. *Proteomics* 13(1):22-24.
- Kim, S. & Pevzner, P.A. 2014. MS-GF+ makes progress towards a universal database search tool for proteomics. *Nature Communications* 5:5277.
- Cox, J., Neuhauser, N., Michalski, A., Scheltema, R.A., Olsen, J.V. & Mann, M. 2011. Andromeda: a peptide search engine integrated into the MaxQuant environment. *Journal of Proteome Research* 10(4):1794-1805.
- Kong, A.T., Leprevost, F.V., Avtonomov, D.M., Mellacheruvu, D. & Nesvizhskii, A.I. 2017. MSFragger: ultrafast and comprehensive peptide identification in mass spectrometry-based proteomics. *Nature Methods* 14(5):513-520.
- Lazear, M.R. 2023. Sage: an open-source tool for fast proteomics searching and quantification at scale. *Journal of Proteome Research* 22(11):3652-3659.
- Solntsev, S.K., Shortreed, M.R., Frey, B.L. & Smith, L.M. 2018. Enhanced global post-translational modification discovery with MetaMorpheus. *Journal of Proteome Research* 17(5):1844-1851.
- Chi, H., Liu, C., Yang, H. et al. 2018. Comprehensive identification of peptides in tandem mass spectra using an efficient open search engine. *Nature Biotechnology* 36:1059-1061.
- Fondrie, W.E. & Noble, W.S. 2021. mokapot: fast and flexible semisupervised learning for peptide detection. *Journal of Proteome Research* 20(4):1966-1971.
- Bouwmeester, R., Gabriels, R., Hulstaert, N., Martens, L. & Degroeve, S. 2021. DeepLC can predict retention times for peptides that carry as-yet unseen modifications. *Nature Methods* 18:1363-1369.
- Gabriels, R., Martens, L. & Degroeve, S. 2019. Updated MS2PIP web server delivers fast and accurate MS2 peak intensity prediction for multiple fragmentation methods, instruments and labeling techniques. *Nucleic Acids Research* 47(W1):W295-W299.
- Declercq, A., Bouwmeester, R., Hirschler, A., Carapito, C., Degroeve, S., Martens, L. & Gabriels, R. 2022. MS2Rescore: data-driven rescoring dramatically boosts immunopeptide identification rates. *Molecular & Cellular Proteomics* 21(8):100266.
- Wen, B., Freestone, J., Riffle, M., MacCoss, M.J., Noble, W.S. & Keich, U. 2025. Assessment of false discovery rate control in tandem mass spectrometry analysis using entrapment. *Nature Methods* 22:1454-1463.

## Related Skills

- protein-inference - Group peptides to protein groups and control protein-level (picked) FDR
- ptm-analysis - Open/variable-mod search follow-up and per-site PTM localization
- dia-analysis - DIA peptide-centric extraction and scoring; entrapment FDR validation
- quantification - FDR-filtered IDs feed label-free/TMT intensity quantification
- spectral-libraries - Empirical and predicted spectral-library search as an ID alternative
- data-import - Load mzML/raw MS data before identification
- database-access/uniprot-access - Build the target FASTA (canonical vs isoform, contaminants)
<!-- END FILE: proteomics/peptide-identification/SKILL.md -->

## 子目录：proteomics/protein-inference

<!-- BEGIN FILE: proteomics/protein-inference/SKILL.md -->
---
name: bio-proteomics-protein-inference
description: Groups proteins from peptide identifications and controls protein-level FDR, framing inference as a chosen explanation (parsimony or a probability model) of underdetermined peptide evidence rather than a measurement. Reports protein GROUPS (proteins indistinguishable by observed peptides) with a leading protein, not flat lists. Covers shared-vs-unique peptides, indistinguishable/subsumable proteins, parsimony vs probabilistic (ProteinProphet, EPIFANY) vs razor inference, picked-protein and picked-group FDR, and why the two-peptide rule is wrong. Use when resolving which proteins are present from a peptide list, building protein groups, or estimating protein-level FDR. PSM/peptide FDR and search engines are peptide-identification; razor-vs-unique quant consequences are quantification; isoform/proteoform resolution is top-down and out of scope.
tool_type: mixed
primary_tool: pyOpenMS
---

## Version Compatibility

Reference examples tested with: pyOpenMS 3.1+, pandas 2.2+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

The pyOpenMS protein-inference class names have varied across releases. Confirm the exact spelling at the installed version with `help(pyopenms.EpifanyAlgorithm)` and `help(pyopenms.BasicProteinInferenceAlgorithm)` before relying on the reference code.

# Protein Inference -- A Chosen Explanation of Peptide Evidence, Reported as Groups

**"Tell me which proteins are present from my identified peptides"** -> Assign the observed peptides to a minimal or probability-weighted set of proteins, reported as groups of indistinguishable proteins with a leading accession -- because bottom-up MS measures peptides, and the protein set behind them is inferred, not observed.
- Python: `pyopenms.BasicProteinInferenceAlgorithm().run(peptide_ids, protein_ids)` for parsimony grouping
- Python: `pyopenms.EpifanyAlgorithm` (TOPP tool `Epifany`) for Bayesian belief-propagation inference
- CLI: `ProteinProphet` (TPP) for EM-based probabilistic inference; `Philosopher filter` for FragPipe FDR

Scope: this skill OWNS peptide-to-protein grouping, the indistinguishable/subsumable distinction, the leading-protein convention, inference-method choice, and protein/protein-group FDR. PSM-level and peptide-level FDR plus the search engines that produce the peptide list -> peptide-identification. The quantitative fallout of razor vs unique peptides on protein abundance -> quantification. OUT OF SCOPE: resolving splice isoforms, single-AA variants, or PTM-defined proteoforms (bottom-up groups cannot separate them; that is top-down / proteoform work).

## The Single Most Important Modern Insight -- Protein Inference Is Underdetermined, So the Honest Unit Is a Group, Not a List

1. **The protein set is not uniquely recoverable from peptides, so a protein group -- not a flat protein list -- is the only honest reporting unit.** Many peptides are shared across paralogs, gene families, and isoforms, so distinct protein sets can explain the same peptide evidence equally well. The inference picks ONE explanation under an assumption (parsimony, or a probability model); proteins that the observed peptides cannot tell apart (indistinguishable) MUST be reported as one group with a designated leading protein. A flat list double-counts indistinguishable proteins and breaks target/decoy symmetry at the protein level, silently corrupting FDR.

2. **Protein FDR is its own estimation problem that INFLATES on large data; the fix is PICKED FDR, not the PSM formula reused.** Controlling PSM-FDR at 1% does not give 1% protein-FDR. A deep run has many false PSMs in absolute terms, and each can nucleate a one-hit-wonder false protein; because true proteins accumulate many peptides while false proteins are hit once, the naive protein-FDR balloons to 10-30% on deep datasets. Savitski 2015 picked-protein FDR pairs each target protein with its decoy and keeps only the higher-scoring of the pair before counting, removing the target/decoy asymmetry; The & Kall 2016 extends this to the group level (picked-group FDR), which is required because parsimony grouping is anticonservative otherwise.

3. **The two-peptide rule is wrong -- it increases protein FDR and discards real proteins.** Requiring >=2 peptides per protein (Gupta & Pevzner 2009, "A strike against the two-peptide rule") removes MORE target proteins than decoy proteins, so it raises protein-level FDR rather than lowering it, while throwing away legitimate low-abundance single-peptide IDs. Replace the blanket rule with: control protein-level (picked) FDR, then judge single-peptide IDs by their score, not their peptide count.

## Vocabulary the Rest of This Depends On

- Shared (degenerate) peptide: maps to >1 protein in the searched database. Cannot, alone, distinguish which protein is present.
- Unique peptide: maps to exactly one protein -- the only direct evidence for a specific protein. "Unique" is DATABASE-RELATIVE: a peptide unique against SwissProt may be shared against TrEMBL+isoforms+contaminants. Always document the exact database (isoforms, contaminants, decoys included).
- Indistinguishable proteins: explained by the SAME set of observed peptides -> one group, never two confident IDs.
- Subset / subsumable protein: its observed peptides are a subset of another protein's -> parsimony drops it (the larger protein explains everything it would).
- Leading / representative protein: the group's reported accession. Convention: most peptides, then highest score, then SwissProt canonical over TrEMBL. Downstream tables key on this accession but must retain group membership -- "protein P12345" usually means "the group led by P12345".
- Protein group vs proteoform: a group is an inference artifact (proteins lumped because peptides cannot separate them); a proteoform is a real molecular species (one gene product with a specific sequence + PTM + cleavage state). Bottom-up groups DO NOT resolve proteoforms -- claiming "isoform X present" from a shared-peptide group is overreach.

## Tool Taxonomy

| Tool / method | Citation | Mechanism / role | When |
|---------------|----------|------------------|------|
| Parsimony (Occam) | -- | Greedy minimal protein set explaining all peptides | Fast default; ties broken arbitrarily; anticonservative group-FDR on large data unless picked |
| ProteinProphet | Nesvizhskii 2003 | EM APPORTIONS shared peptides across candidate proteins, weighted by other evidence | TPP / FragPipe pipelines; the classic probabilistic standard |
| EPIFANY | Pfeuffer 2020 | Bayesian network over the peptide-protein graph, loopy belief propagation + convolution trees | OpenMS-recommended modern inference; strong at controlled protein-group FDR |
| Fido | -- | Bayesian generative model (Percolator `--protein`) | Percolator pipelines; superseded by picked-protein for FDR |
| Razor peptide | -- | Shared peptide assigned winner-take-all to the group with most evidence (MaxQuant) | MaxQuant default; ID-fine but distorts QUANT (route to quantification) |
| Picked-protein FDR | Savitski 2015 | Pair target with its decoy, keep the higher-scoring of the pair, then count decoys | Protein-level FDR on any non-trivial dataset |
| Picked-group FDR | The & Kall 2016 | Picking applied at the protein-GROUP level | When the inference unit is the group (the correct unit on deep data) |
| All-proteins / inclusive | -- | Report every protein any peptide could come from | Almost never; massive false-positive protein inflation |

## Decision Tree by Scenario

| Scenario | Recommended | Why |
|----------|-------------|-----|
| Standard DDA run, OpenMS-based pipeline | `EpifanyAlgorithm` (or `BasicProteinInferenceAlgorithm` for parsimony) + picked-group FDR | Modern, group-FDR aware; well-calibrated on benchmarks |
| MaxQuant output (`proteinGroups.txt`) | Parse groups as-is; quantify on UNIQUE peptides | Groups already inferred; razor quant is the trap, not the inference |
| FragPipe / TPP pipeline | ProteinProphet inference + Philosopher/Philosopher-style FDR filtering | Native EM apportionment + 2-level FDR |
| Deep dataset (many thousands of proteins) | Picked-GROUP FDR, NOT naive decoy/target | Naive protein-FDR inflates to 10-30% from one-hit-wonders |
| Sensitive differential abundance downstream | Quantify on unique peptides only -> quantification | Razor assignment can flip between conditions and fake DE |
| Want isoform-level answers | Stop -- route to top-down / proteoform methods | Bottom-up groups cannot resolve proteoforms |
| Few PSMs (single-protein pulldown) | Report evidence, do not trust a "0% protein FDR" | Target-decoy FDR is meaningless at tiny counts |

Default when uncertain: run parsimony grouping (`BasicProteinInferenceAlgorithm` with `annotate_indistinguishable_groups`), report protein GROUPS with a leading accession, and control protein-GROUP FDR with picked-group FDR at 1%. Do NOT impose a two-peptide rule.

### Group Proteins by Parsimony with pyOpenMS

**Goal:** Turn an FDR-filtered peptide identification list into protein groups with a leading protein, resolving shared-peptide ambiguity.

**Approach:** Load the idXML from peptide identification, run the parsimony algorithm with indistinguishable-group annotation on, then read the inferred groups off the protein identification run.

```python
from pyopenms import IdXMLFile, BasicProteinInferenceAlgorithm

protein_ids = []
peptide_ids = []
# protein_ids is FIRST in both load() and store() for IdXMLFile
IdXMLFile().load('peptides_1pct_fdr.idXML', protein_ids, peptide_ids)

inference = BasicProteinInferenceAlgorithm()
params = inference.getParameters()
# annotate_indistinguishable_groups reports indistinguishable proteins as ONE group
params.setValue('annotate_indistinguishable_groups', 'true')
inference.setParameters(params)
inference.run(peptide_ids, protein_ids)

# indistinguishable groups live on the protein identification run
for prot_id in protein_ids:
    for group in prot_id.getIndistinguishableProteins():
        leading = group.accessions[0]  # convention: highest-evidence accession first
        print(leading, group.probability, list(group.accessions))
```

### Bayesian Inference + Group FDR with EPIFANY

**Goal:** Assign calibrated protein/group posteriors and control protein-group FDR with a probability model rather than greedy parsimony.

**Approach:** EPIFANY consumes idXML whose PSMs already carry posterior error probabilities (from Percolator or IDPosteriorErrorProbability), then propagates belief over the peptide-protein graph. The TOPP tool is reliably named `Epifany`; the pyOpenMS class spelling has varied across releases, so introspect first.

```python
import pyopenms
from pyopenms import IdXMLFile

# CONFIRM the class name at the installed version before use:
#   help(pyopenms.EpifanyAlgorithm)
algo_cls = getattr(pyopenms, 'EpifanyAlgorithm')

protein_ids = []
peptide_ids = []
IdXMLFile().load('peptides_with_pep.idXML', protein_ids, peptide_ids)

algo = algo_cls()
# EPIFANY expects PSM posteriors as input; greedy_group_resolution controls
# whether shared peptides are razor-resolved after inference
algo.inferPosteriorProbabilities(protein_ids, peptide_ids, False)

for prot_id in protein_ids:
    for group in prot_id.getIndistinguishableProteins():
        print(group.accessions[0], group.probability)
```

### Picked Protein-Group FDR

**Goal:** Estimate protein-group FDR without the inflation that the reused PSM formula causes on large data.

**Approach:** For each target group, find its decoy counterpart (same accessions with the decoy prefix); keep only the higher-scoring member of each target/decoy PAIR; rank the picked set and count decoys as the FDR estimate. This is the operation the reference example demonstrates end to end.

```python
def picked_group_fdr(groups, decoy_prefix='DECOY_'):
    # groups: list of dicts with 'accessions', 'score', 'is_decoy'
    by_base = {}
    for g in groups:
        base = frozenset(a.replace(decoy_prefix, '') for a in g['accessions'])
        # keep only the higher-scoring of the target/decoy pair (the 'pick')
        if base not in by_base or g['score'] > by_base[base]['score']:
            by_base[base] = g
    picked = sorted(by_base.values(), key=lambda g: g['score'], reverse=True)

    targets = decoys = 0
    for g in picked:
        if g['is_decoy']:
            decoys += 1
        else:
            targets += 1
        g['fdr'] = decoys / targets if targets else 1.0
    running_min = 1.0
    for g in reversed(picked):  # monotone q-values from the bottom up
        running_min = min(running_min, g['fdr'])
        g['qvalue'] = running_min
    return [g for g in picked if not g['is_decoy'] and g['qvalue'] <= 0.01]
```

## Per-Method Failure Modes

### Naive (non-picked) protein/group FDR
**Trigger:** Reusing the PSM-level `decoys/targets` formula at the protein level on a deep dataset.
**Mechanism:** False target proteins (one-hit-wonders) and decoy proteins are not symmetric once peptides are mapped to proteins; true proteins absorb many peptides, false ones do not.
**Symptom:** Reported 1% protein FDR, actual 10-30%; reviewer or entrapment check exposes it.
**Fix:** Picked-protein FDR (Savitski 2015) or picked-group FDR (The & Kall 2016); validate with a two-species or entrapment search.

### Two-peptide rule
**Trigger:** Filtering to proteins with >=2 (unique) peptides "for confidence".
**Mechanism:** The rule removes more target proteins than decoy proteins, inverting the FDR effect, and deletes real low-abundance single-peptide proteins.
**Symptom:** Fewer proteins AND higher true FDR than picked FDR at the same nominal cutoff.
**Fix:** Drop the rule; control picked protein-level FDR and score single-peptide IDs individually.

### Razor-peptide quantification
**Trigger:** Quantifying on MaxQuant's default unique+razor peptides for a sensitive comparison.
**Mechanism:** A shared peptide's full intensity is credited to one group; that razor assignment can flip between conditions when peptide counts shift, so a protein's quantity changes for inference reasons, not biology.
**Symptom:** Spurious differential abundance concentrated on proteins sharing peptides with paralogs.
**Fix:** Quantify on unique peptides only for sensitive comparisons -> quantification.

### Parsimony tie-breaking
**Trigger:** Multiple minimal protein sets explain the peptides equally well.
**Mechanism:** Greedy parsimony breaks ties arbitrarily; minimality is a heuristic, not truth, and a real protein with only shared peptides is silently dropped.
**Symptom:** Reported lead protein differs run-to-run or pipeline-to-pipeline on the same data.
**Fix:** Prefer a probabilistic method (EPIFANY/ProteinProphet) that apportions shared evidence; retain group membership.

### Proteoform overreach
**Trigger:** Reporting "isoform X is present" from a group whose evidence is shared peptides.
**Mechanism:** Splice isoforms, variants, and PTM forms collapse into groups in bottom-up data; the group cannot separate them.
**Symptom:** Isoform-specific claim with no isoform-unique peptide behind it.
**Fix:** Require an isoform-unique peptide for any isoform claim, or use top-down / proteoform methods.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| Protein / protein-group FDR 1% (sometimes 5% for discovery) | community standard | SEPARATE estimation from PSM FDR; never assume 1% PSM implies 1% protein |
| Picked FDR (target/decoy pairing) | Savitski 2015; The & Kall 2016 | Removes target/decoy asymmetry; dataset-size-independent, unlike naive decoy/target |
| Decoy:target ratio 1:1 | community standard | Standard null; unequal ratios require formula correction |
| Min PSMs for trustworthy protein FDR | hundreds+ | Below ~100s of items decoy counts are too noisy; "0% FDR" from zero decoys is luck, not control |
| Two-peptide rule | DO NOT USE (Gupta & Pevzner 2009) | Increases protein FDR and drops real proteins; replaced by picked FDR + per-ID score |
| Single-peptide IDs | judge by score, not count | A high-confidence unique peptide can be a legitimate ID |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| Protein FDR much higher than nominal on deep data | Naive decoy/target reused from PSM level | Picked-protein or picked-group FDR |
| Real low-abundance proteins missing | Two-peptide rule applied | Remove the rule; control picked FDR |
| AttributeError on `EpifanyAlgorithm` / `infer_proteins` | Class name varies by version; the R `ProteinInference::infer_proteins` could not be confirmed to exist | `help(pyopenms.EpifanyAlgorithm)` to find the real name; use pyOpenMS, not an unverified R package |
| Indistinguishable proteins reported as separate IDs | Flat protein list instead of groups | Enable `annotate_indistinguishable_groups`; report groups with a leading protein |
| Spurious DE on paralog-sharing proteins | Razor-peptide quant flipped between conditions | Quantify on unique peptides -> quantification |
| "Unique" peptide count changed when DB changed | Uniqueness is database-relative | Fix and document the database (isoforms, contaminants, decoys) |

## References

- Nesvizhskii, A.I., Keller, A., Kolker, E. & Aebersold, R. (2003). A statistical model for identifying proteins by tandem mass spectrometry. *Analytical Chemistry* 75(17):4646-4658.
- Gupta, N. & Pevzner, P.A. (2009). False discovery rates of protein identifications: a strike against the two-peptide rule. *Journal of Proteome Research* 8(9):4173-4181.
- Savitski, M.M., Wilhelm, M., Hahne, H., Kuster, B. & Bantscheff, M. (2015). A scalable approach for protein false discovery rate estimation in large proteomic data sets. *Molecular & Cellular Proteomics* 14(9):2394-2404.
- The, M., Tasnim, A. & Kall, L. (2016). How to talk about protein-level false discovery rates in shotgun proteomics. *Proteomics* 16(18):2461-2469.
- Pfeuffer, J., Sachsenberg, T., Dijkstra, T.M.H., Serang, O., Reinert, K. & Kohlbacher, O. (2020). EPIFANY: a method for efficient high-confidence protein inference. *Journal of Proteome Research* 19(3):1060-1072.

## Related Skills

- peptide-identification - Produces the FDR-filtered peptide list that feeds inference and shares the target-decoy machinery
- quantification - Consumes inferred groups; razor-vs-unique peptide choice lives here
- data-import - Loads idXML/mzML identification files
- database-access/uniprot-access - Canonical-vs-isoform databases drive uniqueness and the leading-protein convention
<!-- END FILE: proteomics/protein-inference/SKILL.md -->

## 子目录：proteomics/proteomics-qc

<!-- BEGIN FILE: proteomics/proteomics-qc/SKILL.md -->
---
name: bio-proteomics-proteomics-qc
description: Quality control for bottom-up proteomics across three levels -- instrument/raw-signal (mass accuracy, RT/iRT fit, FWHM, TIC vs injection time, % MS2 identified), identification/run (missed cleavages, charge states, PTM handling artifacts, contaminants), and experiment/quantitative (replicate correlation on log2, CV on the linear scale, completeness, MNAR-vs-MCAR missingness, PCA/batch, TMT channel balance, DIA q-values). Frames QC as a control chart against a per-instrument rolling baseline, not fixed cutoffs, and mandates inspecting raw boxplots, per-sample ID counts, total signal, and contaminant removal BEFORE normalizing -- because median normalization erases loading failures. Use when assessing proteomics data quality, diagnosing outlier samples, or deciding which samples to exclude before differential testing. The statistical test itself is differential-abundance; normalization mechanics are quantification; DIA q-value internals are dia-analysis.
tool_type: mixed
primary_tool: pandas
---

## Version Compatibility

Reference examples tested with: pandas 2.2+, numpy 1.26+, scipy 1.12+, matplotlib 3.8+, scikit-learn 1.4+, limma 3.58+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Proteomics Quality Control -- A Three-Level Funnel Where the Matrix Sees the Failure Last

**"Check the quality of my proteomics data"** -> Read instrument, identification, and quantitative metrics as a descending funnel of silent failures, and inspect raw signal BEFORE normalizing -- because by the time a fault reaches the deliverable matrix, normalization has usually erased the evidence.
- Python: `pandas` for matrix QC; `matplotlib`/`seaborn` for raw boxplots, correlation heatmaps, PCA
- R: PTXQC `createReport()` for MaxQuant search-table QC; `limma::plotMDS()`/`plotDensities()`; MSstatsTMT `dataProcessPlotsTMT()` for TMT channel balance

Scope: This skill OWNS QC diagnosis across all three levels -- which metric localizes which fault, what threshold means trouble, and the mandatory inspect-before-normalize ordering. Normalization mechanics route to quantification; the differential test routes to differential-abundance; DIA q-value computation routes to dia-analysis. OUT OF SCOPE: running the statistical test, the normalization algorithms themselves, and DIA q-value/FDR internals.

## The Single Most Important Modern Insight -- QC Is a Three-Level Funnel and Normalization Hides the Evidence

1. **QC is a three-level funnel of silent failures, and the deliverable matrix is the LAST place a problem becomes visible.** Faults originate at the instrument (spray, calibration, column) or in identification (digestion, contamination, PTM artifacts), but a protein matrix only shows the downstream symptom -- a low correlation or an outlier sample. A matrix-only QC pass is one-third of the job and blind to where faults actually start. Localize by descending: read every metric together with its co-readouts, never alone.

2. **Almost no metric has a universal pass/fail cutoff; the defensible practice is a per-instrument, per-method control chart.** Deviation from a lab's own rolling baseline (Levey-Jennings, +/-2 SD warn, +/-3 SD action) detects faults that a constant threshold misses or false-flags (Neely and Palmblad 2024). The numbers below seed a control chart, they are not standards-body limits.

3. **Median normalization HIDES loading problems that must be SEEN first.** Median/quantile normalization works by forcing a chosen summary statistic of every sample equal. A sample that genuinely loaded 3x low sits visibly shifted down in a RAW boxplot -- an obvious, diagnosable defect. The instant the matrix is median-normalized, the algorithm shifts that sample up by a constant to match everyone's median; boxplots line up perfectly; the evidence is mathematically erased. Worse, the low-loaded sample's noisy low-abundance signal gets stretched up to mid-range and injected into the differential test while QC plots look pristine. MANDATE: inspect raw/un-normalized boxplots plus per-sample ID counts, total signal, and missing fraction BEFORE normalizing; remove loading/injection failures and contaminants; THEN normalize and re-plot on the survivors. The identical principle governs TMT channel-loading balance.

## The Three Levels in One Table

| Level | Question | Inputs | Faults localized |
|-------|----------|--------|------------------|
| 1. Instrument / raw-signal | Is the LC-MS hardware performing? | Vendor `.raw`/`.d`; RawTools/RawBeans/rawrr/rawDiag/QuaMeter; Panorama AutoQC | Column, spray/emitter, mass analyzer/calibration |
| 2. Identification / run | Did this run identify peptides correctly? | Search tables (MaxQuant `txt/`, FragPipe `*.tsv`, DIA-NN report); PTXQC | Digestion, sample-handling PTM artifacts, contamination, FDR efficiency |
| 3. Experiment / quantitative | Are the numbers reproducible and comparable? | Protein/peptide intensity matrix; MSstatsTMT, pandas/limma | Loading/pipetting, batch, outliers, missingness, sample swaps |

The most integrative metric (% MS2 identified / ID count) is the first alarm but the LEAST specific -- it moves whenever anything upstream degrades. The same protein-count drop means spray (erratic TIC + maxed injection time), column (lost RT + broad peaks + rising backpressure), or sample (high contaminant fraction) depending on what co-moves.

## Tool Taxonomy

| Tool / method | Level | Citation | Mechanism / role | When |
|---------------|-------|----------|------------------|------|
| PTXQC (R, CRAN) | 2+3 | Bielow 2016 | `createReport()` over MaxQuant `txt/` or mzTab; per-metric scores in [0,1], QC heatmap PDF | MaxQuant output, fast multi-metric report |
| RawTools / RawBeans | 1 | Kovalchik 2019; Morgenstern 2021 | Parse Thermo `.raw` for IT, TIC, FWHM, scan timing | Diagnose instrument faults from raw files |
| rawrr / rawDiag | 1 | Kockmann 2021; Trachsel 2018 | R access to Orbitrap scan metadata | Custom Level-1 plots / method optimization |
| QuaMeter | 1+2 | Ma 2012 | Vendor-independent ID-free and ID-based metrics | Cross-vendor Level-1 QC |
| Skyline + Panorama AutoQC | 1 (longitudinal) | Bereman 2016 | Levey-Jennings + CUSUM/Moving-Range, SD-band flagging | System-suitability trending over time |
| MSstatsTMT | 3 (TMT) | Huang 2020 | `proteinSummarization()`, `dataProcessPlotsTMT()`; filters isolation interference on import | TMT channel-balance and QC plots |
| pandas / limma matrix QC | 3 | (this skill) | Correlation, CV, completeness, PCA on the matrix | Experiment-level QC (the code below) |
| differential-abundance | (route OUT) | -- | The moderated test itself | Hit calling after QC passes |
| quantification | (route OUT) | -- | Normalization and imputation mechanics | The how of normalizing |
| dia-analysis | (route OUT) | -- | DIA q-value/FDR internals | DIA-NN/Spectronaut report computation |

## Decision Tree by Scenario

| Scenario | Recommended | Why |
|----------|-------------|-----|
| MaxQuant `txt/` folder, want fast multi-metric report | PTXQC `createReport(txt_folder=...)` | Scores Level-2/3 metrics vs a representative file; one PDF |
| Protein-count drop, cause unknown | Descend to Level 1: read TIC + injection time + RT/FWHM together | Co-readouts localize spray vs column vs sample |
| Replicate correlation low for one sample | Check if it correlates better with a DIFFERENT group | Distinguishes sample swap from prep failure |
| Boxplots flat but a sample feels wrong | Re-plot the RAW (un-normalized) matrix | Normalization erased the loading evidence |
| Deciding how to impute | Diagnose MNAR (left tail) vs MCAR (all-abundance) from the histogram FIRST | Wrong imputer corrupts present/absent calls |
| TMT data, channel looks off | MSstatsTMT QC plots on RAW reporter intensities | See the imbalance before global median rescales it |
| DIA matrix, how many proteins are real | Filter Global.Q.Value and Global.PG.Q.Value, route q internals to dia-analysis | Precursor q != protein q; both needed |
| Long sample queue, drift suspected | Interspersed QC every 4th-5th injection + Levey-Jennings | Turns one check into a time series |

Default when uncertain: plot the RAW per-sample boxplots, ID counts, total signal, and missing fraction first; remove loading/injection failures and contaminants; only then normalize, re-plot, and proceed to correlation/CV/PCA on the survivors.

## Inspect Raw Signal and Remove Contaminants Before Normalizing

**Goal:** Catch loading/injection failures and strip contaminant/decoy rows while they are still visible -- before normalization erases them.

**Approach:** Load the un-normalized matrix, plot per-sample boxplots plus ID counts and total signal, filter MaxQuant `Potential contaminant`/`Reverse`/`Only identified by site` rows, THEN log-transform and normalize on the survivors.

```python
import pandas as pd
import numpy as np

contaminant_flags = ['Potential contaminant', 'Reverse', 'Only identified by site']

def strip_contaminant_rows(protein_groups):
    keep = pd.Series(True, index=protein_groups.index)
    for col in contaminant_flags:
        match = next((c for c in protein_groups.columns if c.lower() == col.lower()), None)  # MaxQuant casing varies by version -- match case-insensitively
        if match is not None:
            keep &= protein_groups[match].fillna('') != '+'  # MaxQuant marks flagged rows with a literal '+'
    return protein_groups[keep]

def raw_sample_qc(raw_intensities):
    return pd.DataFrame({
        'n_quantified': raw_intensities.notna().sum(),
        'total_signal': raw_intensities.sum(),
        'median_intensity': raw_intensities.median(),
        'missing_pct': 100 * raw_intensities.isna().sum() / len(raw_intensities)})
```

Read the boxplots before normalizing: a sample shifted >=2-3x below its group median is a loading/injection failure to exclude, not to rescale. The contaminant fraction of summed intensity should be small (PTXQC default flags >1%); keratin and trypsin autolysis dominate LOW-INPUT samples (single-cell, IPs, gel bands) because they are a roughly fixed absolute amount whose fractional share explodes as load shrinks.

## Replicate Correlation on log2

**Goal:** Quantify reproducibility without letting a few abundant proteins fake agreement.

**Approach:** Correlate on log2 intensities (variance-stabilized, high-abundance tail compressed), report within-group pairs, and flag a sample correlating better with another group as a possible swap.

```python
from itertools import combinations

def replicate_correlation(log2_intensities, sample_groups):
    corr = log2_intensities.corr(method='pearson')  # log2 first: Pearson on raw is a high-abundance artifact
    rows = []
    for group in sample_groups.unique():
        members = sample_groups[sample_groups == group].index
        for s1, s2 in combinations(members, 2):
            rows.append({'group': group, 's1': s1, 's2': s2, 'r': corr.loc[s1, s2]})
    return pd.DataFrame(rows)
```

Technical replicates r > 0.98 (instrument noise only); biological r ~ 0.90-0.98 (genuine variance, lower is expected and correct); soft floor r > 0.8 to retain a biological replicate. A Spearman check is a robustness aid only -- ranks discard the magnitude that quant QC cares about.

## Coefficient of Variation on the Linear Scale

**Goal:** Summarize per-condition precision with a number that means what it says.

**Approach:** Compute CV = SD/mean on LINEAR (non-log) intensities; if only logged values exist use the geometric-CV formula. Report the median CV per condition (the per-protein distribution is right-skewed).

```python
def median_cv_linear(linear_intensities, sample_groups):
    rows = []
    for group in sample_groups.unique():
        block = linear_intensities[sample_groups[sample_groups == group].index]
        per_protein_cv = block.std(axis=1) / block.mean(axis=1)  # base CV formula REQUIRES linear scale
        rows.append({'group': group, 'median_cv_pct': 100 * per_protein_cv.median()})
    return pd.DataFrame(rows)

def geometric_cv_from_log(log_intensities):
    sigma = log_intensities.std(axis=1) * np.log(2)  # convert log2 SD to natural-log SD
    return 100 * np.sqrt(np.expm1(sigma ** 2))  # gCV = sqrt(exp(sigma^2) - 1)
```

Applying the base formula to log-transformed data compresses CV ~14x (most proteins appear to have CV < 1%) -- meaningless (Brenes 2024). State normalization state, transform, and software params or the CV is uninterpretable: DIA-NN "High precision" mode silently median-normalizes, halving median CV vs "High accuracy". Technical median CV < ~10-20%, biological ~20-40%; a LOWER CV is not automatically better (loose FDR or faulty MS1 extraction produce artificially low CVs).

## Missingness Mechanism and Completeness

**Goal:** Decide how to impute by first deciding why values are missing.

**Approach:** Diagnose the missingness profile -- left-tail concentration means MNAR (left-censored, abundance-dependent), all-abundance scatter means MCAR -- and filter on completeness before imputing only the shallow remainder.

```python
def missingness_profile(log2_intensities, n_bins=20):
    observed = log2_intensities.stack()
    abundance_bins = pd.qcut(observed, n_bins, duplicates='drop')
    present_per_protein = log2_intensities.notna().mean(axis=1)
    mean_abundance = log2_intensities.mean(axis=1)
    return mean_abundance, present_per_protein  # plot present-fraction vs abundance: rising-with-abundance = MNAR

def completeness_filter(log2_intensities, sample_groups, min_valid_frac=0.7):
    keep = pd.Series(False, index=log2_intensities.index)
    for group in sample_groups.unique():
        block = log2_intensities[sample_groups[sample_groups == group].index]
        keep |= block.notna().mean(axis=1) >= min_valid_frac  # valid in >=70% of >=1 condition
    return log2_intensities[keep]
```

kNN-imputing a genuinely-absent (MNAR) value invents mid-range abundance and KILLS a real present/absent difference; a left-shifted draw (Perseus down-shifted normal, downshift=1.8 SD below the observed mean, width=0.3 of observed SD) on an MCAR gap FABRICATES a false low and inflates a difference. Match the imputer to the mechanism. The imputation mechanics themselves are quantification.

## PCA and Batch Detection

**Goal:** See whether the dominant variance is biology or batch, and flag outlier samples.

**Approach:** On the normalized survivors, run PCA, color by condition and by batch, and test whether top PCs associate with batch.

```python
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from scipy.stats import f_oneway

def pca_batch_check(normalized_log2, sample_info, batch_col='batch'):
    imputed = normalized_log2.apply(lambda r: r.fillna(r.median()), axis=1)  # temporary, for PCA only
    pcs = PCA(n_components=5).fit(StandardScaler().fit_transform(imputed.T))
    coords = pd.DataFrame(pcs.transform(StandardScaler().fit_transform(imputed.T)),
                          columns=[f'PC{i+1}' for i in range(5)], index=normalized_log2.columns).join(sample_info)
    for pc in ['PC1', 'PC2', 'PC3']:
        groups = [coords[coords[batch_col] == b][pc] for b in coords[batch_col].unique()]
        _, p = f_oneway(*groups)
        print(f'{pc} ~ {batch_col}: p={p:.4f}')
    return coords, pcs.explained_variance_ratio_
```

A sample isolated from its group is a removal/re-run candidate. If batch is PC1, correct it explicitly (ComBat, or include batch in the design matrix downstream) and re-inspect; never let batch be the dominant axis going into differential testing. Visualization of the projection routes to data-visualization/dimensionality-reduction-plots.

## Per-Method Failure Modes

### Median normalization hides loading failures
**Trigger:** Normalizing the matrix before inspecting raw per-sample signal. **Mechanism:** median-centering shifts each sample by a constant to equalize the very statistic that was the symptom of a low load. **Symptom:** flat, clean boxplots that hide a 3x-low sample now stretched into mid-range. **Fix:** plot RAW boxplots + ID counts + total signal first; exclude failures; then normalize.

### Normalizing with contaminants still in the matrix
**Trigger:** Contaminant/decoy rows left in before log + normalize. **Mechanism:** keratin/trypsin/albumin inflate the denominator and shift the median; when their load differs across groups the differential gets normalized into the real proteins. **Symptom:** spurious fold changes; a contaminant fraction that varies by group. **Fix:** filter `Potential contaminant` + `Reverse` + `Only identified by site` BEFORE log + normalize.

### Wrong imputer for the missingness mechanism
**Trigger:** kNN on MNAR, or left-shift on MCAR. **Mechanism:** kNN borrows mid-range neighbors for a value that is low because it is absent; left-shift draws a deep low for a value missing at random. **Symptom:** killed present/absent calls (kNN-on-MNAR) or inflated false lows (left-shift-on-MCAR). **Fix:** diagnose left-tail vs all-abundance from the histogram first; mechanics route to quantification.

### CV computed on log-transformed data
**Trigger:** Base CV formula applied after log2. **Mechanism:** SD/mean is defined for linear intensity; logging compresses it ~14x. **Symptom:** most proteins appear to have CV < 1%. **Fix:** compute on linear intensity, or use the geometric-CV formula on logged values; always state transform + normalization + software.

### Pearson r on raw intensity
**Trigger:** Correlating un-logged intensities. **Mechanism:** a few high-abundance proteins dominate the covariance. **Symptom:** r = 0.99 while the bulk disagrees. **Fix:** log2 before correlating; Spearman as a robustness check only.

### Bimodal mass-error histogram read as calibration
**Trigger:** A two-peaked ppm-error distribution. **Mechanism:** almost always monoisotopic mis-assignment or co-isolation (a search/sample problem), NOT calibration drift; a generous tolerance still IDs the mis-assigned precursors so ID rate looks fine. **Symptom:** bimodal histogram, normal ID rate. **Fix:** correct isotope-error tolerance/deisotoping, not recalibration.

### Charge-state distribution off the platform baseline
**Trigger:** The fully-tryptic 2+ fraction drifts from the rolling baseline. **Mechanism:** a tryptic peptide carries two basic sites (C-terminal K/R + N-terminus) so 2+ dominates; excess 3+/4+ comes from internal basic residues left by missed cleavages, excess 1+ from poor ionization, short peptides, or contaminants. **Symptom:** raised high-charge fraction (a digestion/chemistry signal) or raised 1+ fraction (an ionization/spray signal). **Fix:** read the charge distribution together with the missed-cleavage rate (high charge co-moving with missed cleavages = under-digestion) to separate a chemistry problem from a spray problem a raw protein-count drop cannot resolve alone.

### TMT ratio compression from co-isolation
**Trigger:** Isobaric quant with a wide isolation window. **Mechanism:** near-isobaric co-eluting precursors are co-isolated and add their own reporters across all channels, a uniform pedestal. **Symptom:** every fold-change compressed toward 1 (a real 10:1 reads ~5:1). **Fix:** filter isolation interference < 50%; prefer SPS-MS3 (McAlister 2014) / FAIMS / narrow windows; run a TKO or empty-channel control to measure the floor.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| Mass accuracy (internal/lock) median \|err\| < 1-3 ppm, single-mode centered 0 | CONVENTION | width approaching MS1 tolerance loses real IDs |
| iRT RT-fit R^2 > 0.99 (warn below) | CONVENTION (mechanism firm) | residual is just LC noise on a stable gradient |
| FWHM alarm on > 20-30% rise vs baseline; >= 8-10 points across FWHM (floor ~5) | Kocher 2011 | peak capacity tracks peptide IDs; points needed for accurate AUC |
| % MS2 identified: < 20% bad, 20-35% ok, >= 35% great | PTXQC `createYaml.R` | generic pass marks, not a biological ceiling |
| Missed cleavages: >= 75-85% at 0 MC; flag > 25-30% with >= 1 MC | OPERATIONAL (PTXQC-style) | porcine trypsin ~78% efficient even ideally |
| Replicate Pearson r (log2): technical > 0.98, biological 0.90-0.98, floor 0.8 | CONVENTION (mechanism firm) | log2 variance-stabilizes; biological variance is real |
| Median CV (linear): technical < 10-20%, biological 20-40% | CONVENTION | DIA < DDA (no stochastic sampling); lower not always better |
| Completeness: valid in >= 50-70% of replicates in >= 1 condition | CONVENTION | filter before imputing |
| Perseus MNAR imputation: downshift = 1.8 SD, width = 0.3 | Tyanova 2016 | deep left tail simulates below-LOD, narrowed so not mistaken for real |
| TMT channel deviation: investigate > ~2x, flag > ~3-4x | CONVENTION | pipetting/labeling vs biology |
| Isolation interference < 50% PSM filter (< 30% stricter) | CONVENTION (PD practice) | above ~50% contaminant dominates, ratios uninterpretable |
| DIA precursor + protein q both <= 0.01, GLOBAL q, PICKED protein estimator | STANDARD | precursor != protein FDR; route internals to dia-analysis |
| Levey-Jennings: +/-2 SD warn, +/-3 SD action; QC every 4th-5th injection | Bereman 2016 | ~95/99.7% of points under stable normal; catch drift early |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| `KeyError: 'Mass Error [ppm]'` | MaxQuant column casing varies by version | match case-insensitively (`Mass error` vs `Mass Error`); never hard-code |
| Contaminant rows have `True`/`False`, filter keeps all | MaxQuant flags with a literal `'+'`, not a boolean | filter `col != '+'` |
| CV unexpectedly tiny (< 1%) | base CV formula applied to log2 data | compute on linear intensity or use geometric CV |
| `r = 0.99` but samples clearly differ | Pearson on raw (un-logged) intensity | log2 transform before correlating |
| PCA dominated by injection day | batch effect, not biology | correct (ComBat / batch in design) and re-inspect; do not proceed |
| PTXQC "not found" via `BiocManager` | PTXQC is on CRAN, not Bioconductor | `install.packages('PTXQC')` |
| `createReport()` errors on a dataframe arg | it takes a txt-folder path / mzTab / YAML, not dataframes | pass `txt_folder=` (the MaxQuant `txt/` directory) |

## References

- Bielow C, Mastrobuoni G, Kempa S. Proteomics Quality Control: Quality Control Software for MaxQuant Results. *J Proteome Res* 2016;15(3):777-787.
- Kovalchik KA, Colborne S, Spencer SEP, et al. RawTools: Rapid and Dynamic Interrogation of Orbitrap Data Files for Mass Spectrometer System Management. *J Proteome Res* 2019;18(2):700-708.
- Morgenstern D, Barzilay R, Levin Y. RawBeans: A Simple, Vendor-Independent, Raw-Data Quality-Control Tool. *J Proteome Res* 2021;20(4):2098-2104.
- Kockmann T, Panse C. The rawrr R Package: Direct Access to Orbitrap Data and Beyond. *J Proteome Res* 2021;20(4):2028-2034.
- Trachsel C, Panse C, Kockmann T, et al. rawDiag: An R Package Supporting Rational LC-MS Method Optimization for Bottom-up Proteomics. *J Proteome Res* 2018;17(8):2908-2914.
- Ma ZQ, Polzin KO, Dasari S, et al. QuaMeter: Multivendor Performance Metrics for LC-MS/MS Proteomics Instrumentation. *Anal Chem* 2012;84(14):5845-5850.
- Bereman MS, Beri J, Sharma V, et al. An Automated Pipeline to Monitor System Performance in Liquid Chromatography-Tandem Mass Spectrometry Proteomic Experiments. *J Proteome Res* 2016;15(12):4763-4769.
- Kocher T, Swart R, Mechtler K. Ultra-High-Pressure RPLC Hyphenated to an LTQ-Orbitrap Velos Reveals a Linear Relation between Peak Capacity and Number of Identified Peptides. *Anal Chem* 2011;83(7):2699-2704.
- Tyanova S, Temu T, Sinitcyn P, et al. The Perseus computational platform for comprehensive analysis of (prote)omics data. *Nat Methods* 2016;13(9):731-740.
- Brenes AJ. Calculating and Reporting Coefficients of Variation for DIA-Based Proteomics. *J Proteome Res* 2024;23(12):5274-5278.
- McAlister GC, Nusinow DP, Jedrychowski MP, et al. MultiNotch MS3 Enables Accurate, Sensitive, and Multiplexed Detection of Differential Expression across Cancer Cell Line Proteomes. *Anal Chem* 2014;86(14):7150-7158.
- Huang T, Choi M, Tzouros M, et al. MSstatsTMT: Statistical Detection of Differentially Abundant Proteins in Experiments with Isobaric Labeling and Multiple Mixtures. *Mol Cell Proteomics* 2020;19(10):1706-1723.
- Neely BA, Palmblad M, et al. Quality Control in the Mass Spectrometry Proteomics Core: A Practical Primer. *J Biomol Tech* 2024;35(3).

## Related Skills

- data-import - Load search-engine output and intensity matrices before QC
- quantification - Normalization and imputation mechanics that QC mandates running AFTER inspection
- differential-abundance - The moderated statistical test QC gates
- dia-analysis - DIA q-value/FDR internals behind the protein-count QC
- data-visualization/dimensionality-reduction-plots - PCA/MDS projection plotting
- workflows/proteomics-pipeline - End-to-end pipeline placing QC before differential testing
<!-- END FILE: proteomics/proteomics-qc/SKILL.md -->

## 子目录：proteomics/ptm-analysis

<!-- BEGIN FILE: proteomics/ptm-analysis/SKILL.md -->
---
name: bio-proteomics-ptm-analysis
description: Frames PTM/phosphoproteomics analysis as three stacked inference layers on a biased enrichment - chemistry selection, site localization (FLR), and protein-level-adjusted quantification with MSstatsPTM - plus kinase-activity and functional triage. Covers MaxQuant Phospho (STY)Sites multiplicity expansion, localization-probability filtering (class I, Ascore, ptmRS, DIA EG.PTMLocalizationProbabilities, DIA-NN PTM.Site.Confidence), false localization rate (LuciPHOr/DeepFLR), motif analysis with experiment-matched backgrounds, diGly/K-GG ubiquitin specificity, acetyl/glyco traps, and KSEA/PTM-SEA. Use when localizing and quantifying phosphorylation, acetylation, ubiquitination, or glycosylation sites from enrichment-based runs and deciding whether an apparent site change is real after subtracting protein abundance. Peptide ID and open/variable-mod search is peptide-identification; underlying protein-level quant is quantification and differential-abundance; DIA acquisition mechanics is dia-analysis.
tool_type: mixed
primary_tool: MSstatsPTM
---

## Version Compatibility

Reference examples tested with: MSstatsPTM 2.4+, pandas 2.2+, numpy 1.26+, scipy 1.12+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# PTM and Phosphoproteomics Analysis -- Three Inference Layers Stacked on a Biased Extraction

**"Find the regulated phosphosites in my enriched samples"** -> Localize each modification, then test whether its abundance change survives subtracting the protein-level change -- because a PTM result is three separate inferences (enrichment, localization, quantification) and each fails silently if the layer below is treated as solved.
- R: `MSstatsPTM::groupComparisonPTM()` for protein-adjusted site testing (the load-bearing tool)
- Python: `pandas` to expand MaxQuant `Phospho (STY)Sites` multiplicity and filter localization probability
- R: `KSEAapp` / PTM-SEA (`ssGSEA2.0`) for kinase-activity inference from the site fold-changes

Scope: this skill OWNS enrichment-chemistry framing, site localization and FLR, multiplicity-resolved site quant, protein-level adjustment, motif analysis, and kinase-activity inference. Peptide identification and open/variable-mod search route to peptide-identification; the underlying protein-level (unenriched) quant routes to quantification and differential-abundance; DIA acquisition mechanics route to dia-analysis. OUT OF SCOPE: intact-glycopeptide glycan-composition search (pGlyco3/MSFragger-Glyco) and absolute occupancy from three-ratio SILAC are noted but not implemented here.

## The Single Most Important Modern Insight -- A PTM Result Is Three Inferences, Not One

1. **Enrichment IS the experiment, and the chemistry is a filter confounded with biology.** The data only contain what the chemistry captured. TiO2 and Fe-IMAC give partially-overlapping phosphoproteomes; anti-K-GG enriches ubiquitin, NEDD8, and ISG15 indistinguishably; a lectin reports only its cognate glycoforms. A between-method or between-lab "biological difference" must FIRST be excluded as a chemistry artifact before it is called biology.
2. **Identifying a peptide is NOT localizing the modification.** A phosphopeptide with two S/T and one phosphate has isobaric positional isomers of identical precursor mass and identical peptide-level score; the localization is a SECOND inference decided only by site-determining fragment ions, with its own error rate (false localization rate, FLR). Target-decoy peptide FDR cannot estimate FLR: a wrong localization is the correct sequence with the mod one residue over, not a decoy sequence (Fermin 2013). A 1% peptide FDR does NOT yield a 1% site FDR -- report them separately.
3. **A change in phosphopeptide abundance is NOT a change in phosphorylation (the biggest quant trap).** Observed PTM signal ~ (site occupancy) x (protein abundance) x (enrichment/ionization factor), so `log2FC(PTM_observed) = log2FC(occupancy) + log2FC(protein)`. Without a paired global (unenriched) proteome run on the SAME samples to subtract `log2FC(protein)`, every protein-abundance change masquerades as a regulated site. Because co-regulated proteins move together, the false positives are pathway-coherent and look biologically convincing -- the worst kind of artifact. This is the entire reason MSstatsPTM exists (Kohler 2023).
4. **Most identified sites have no known function.** Fewer than ~5% of phosphosites are functionally annotated; a fold-change alone says nothing about regulatory relevance. Functional triage (conservation, stoichiometry, Ochoa functional score, confident kinase assignment) is a separate fourth layer on top of the quant (Ochoa 2020).

Bottom line: report THREE numbers, not one -- peptide/PSM FDR, per-site localization probability with its threshold, and an empirically estimated global FLR -- and never call a site "regulated" from a phospho-only run without protein-level adjustment.

## Tool Taxonomy

### Enrichment chemistry (phospho)

| Method | Citation | Mechanism / bias | When |
|---|---|---|---|
| TiO2 (MOAC) | Larsen 2005 | Metal-oxide Lewis-acid surface; skews mono-phospho; needs hydroxy-acid additive | General single-method depth; EasyPhos basis |
| Fe(III)-IMAC | Ruprecht 2015 | Chelated Fe3+ coordinates phosphate; multidentate avidity skews MULTI-phospho | Hierarchical/processive signaling; the mono/multi divergence is STRONGEST here vs TiO2 |
| Ti4+/Zr4+-IMAC | Matheron 2014 | Chelated metal ION on immobilized phosphonate (NOT bulk oxide); bias vs TiO2 is SMALL | Modern automated workflows; metal identity matters more than IMAC-vs-MOAC |
| SIMAC (sequential) | Thingholm 2008 | IMAC acidic elution = mono, basic = multi, then TiO2 on mono fraction | Recovering both populations IMAC alone biases |

Naming trap: Ti4+/Zr4+-IMAC (chelated ions) is DIFFERENT chemistry from TiO2/ZrO2 (bulk oxide). Glycolic acid is the modern additive standard (load 80% ACN / 5% TFA / 0.1 M glycolic acid).

### Other-PTM enrichment and identity traps

| PTM | Reagent / mass | Citation | Headline trap |
|---|---|---|---|
| Ubiquitin (diGly, K-GG, +114.0429) | Anti-K-GG antibody | Xu 2010; Kim 2011 | NOT ubiquitin-specific: K-GG = ubiquitin + NEDD8 (~6% at basal) + ISG15 (rises under interferon). UbiSite (Akimov 2018) is the ubiquitin-specific alternative |
| Ubiquitin alkylation artifact | use chloroacetamide | Nielsen 2008 | Iodoacetamide creates a +114.0429 lysine adduct mimicking ubiquitination; chloroacetamide does not |
| Acetyl-K (+42.0106) | Anti-acetyllysine cocktail | Svinkina 2015 | Isobaric with trimethyl +42.0470 (0.0364 Da, needs high-res); acetyl blocks trypsin -> allow >=4 missed cleavages |
| Glyco N-linked | PNGase F (released) or intact | Riley 2021 | Released loses the glycan; N->D tag +0.984 is isobaric with deamidation -- use PNGase F in H2-18O (+2.988) to disambiguate; N-X-S/T (X!=Pro) sequon is necessary not sufficient |

### Localization scoring

| Tool | Citation | Mechanism | Note |
|---|---|---|---|
| Ascore | Beausoleil 2006 | Cumulative binomial of site-determining ions; DIFFERENCE between best and 2nd-best localization, peak-depth sweep | Ascore >=19 ~ p 0.01 PAIRWISE per-PSM, NOT a dataset FLR |
| PhosphoRS / ptmRS | Taus 2011 | Per-isomer cumulative binomial, tolerance-aware (correct for high-res), per-site probs sum to 100% | In Proteome Discoverer |
| PTMProphet | Shteynberg (TPP) | EM/Bayesian mixture; per-site probs combinable across PSMs to a global FLR | TPP/FragPipe |
| MaxQuant Localization prob | Cox/Mann (Andromeda) | Normalized posterior on the site (fixed peak depth) | column `Localization prob`; >=0.75 = class I |
| DIA localization | Bekker-Jensen 2020 | XIC peak-shape correlation substitutes for missing precursor isolation | Spectronaut `EG.PTMLocalizationProbabilities`; DIA-NN `PTM.Site.Confidence` |
| DeepFLR | Zong 2023 | Deep-learning spectrum predictor + target-decoy FLR | SOTA direction; DDA + DIA |

### Site-FDR / FLR (the layer most pipelines skip)

| Tool | Citation | Mechanism |
|---|---|---|
| LuciPHOr | Fermin 2013 (MCP) | Decoy localizations on non-modifiable residues; rate decoys win = empirical FLR |
| LuciPHOr2 | Fermin 2015 (Bioinformatics) | Generic-PTM successor (do NOT swap the two journals) |
| Decoy amino-acid FLR | Ramsbottom/Jones 2022 | Add a non-modifiable residue to the candidate set; global FLR ~ decoy-site-hits / target-site-hits, frequency-corrected |

### Kinase-activity inference

| Tool | Citation | Mechanism | Limitation |
|---|---|---|---|
| KSEA | Casado 2013 | z-score of a kinase's substrate fold-changes | sqrt(m) favors well-annotated kinases; inherits PhosphoSitePlus bias |
| PTM-SEA / PTMsigDB | Krug 2019 | ssGSEA2.0 on site-level +/-7 flanking-sequence signatures | robust to isoform drift; PERT signatures score "looks like EGF stim" |
| RoKAI | Yilmaz 2021 | Network-smooth profiles before z-score so unobserved sites borrow neighbor signal | attacks missingness; feeds KSEA |

Benchmark result (Mueller-Dott 2025): across ~19 methods, simple z-score (KSEA/RoKAI) matched or beat sophisticated methods. Performance is PRIOR-limited, not algorithm-limited; all methods inherit PhosphoSitePlus curation bias toward CK2/CDK1/PKA/MAPK, and the dark kinome is structurally invisible. Spend effort on the substrate prior, not the estimator.

## Decision Tree by Scenario

| Scenario | Recommended | Why |
|---|---|---|
| Phospho-only run, want regulated sites | Acquire a PAIRED global proteome -> MSstatsPTM `groupComparisonPTM` -> require significance in `ADJUSTED.Model` | Unadjusted site changes are confounded with protein abundance |
| No global proteome available | Report site changes as UNADJUSTED and flag the confound explicitly | Cannot separate occupancy from abundance; do not claim "regulation" |
| Between-method phospho difference | Suspect chemistry (TiO2 vs Fe-IMAC mono/multi bias) BEFORE biology | Enrichment is a confounded filter |
| Multiply-phospho peptides present | Localize per-site (Ascore/ptmRS) AND report empirical global FLR | Peptide FDR != site FDR |
| "Ubiquitination" sites | Confirm chloroacetamide alkylation; treat K-GG as ub + NEDD8 + ISG15; consider UbiSite | Iodoacetamide artifact + NEDD8/ISG15 confound |
| Which kinases moved? | KSEA or PTM-SEA with a curated prior; do not over-interpret dark-kinome silence | Prior-limited; simple z-score suffices |
| Motif logo from the hits | Background = experiment-matched S/T/Y from the identified proteins (NOT whole proteome) | Whole-proteome background rediscovers disordered-region composition bias |

Default when uncertain: localize with the search engine's probability (class I >=0.75), expand MaxQuant multiplicity, run MSstatsPTM with a paired global proteome, and call only `ADJUSTED.Model` hits regulated.

## Expand the MaxQuant Site Table Before Any Quant

**Goal:** Produce a long, multiplicity-resolved, class-I-filtered phosphosite intensity matrix from `Phospho (STY)Sites.txt`.

**Approach:** Each site row spreads its quant across `Intensity___1/___2/___3` (singly/doubly/triply-phospho forms, THREE underscores); the collapsed base `Intensity` mixes phospho-states and can fake dephosphorylation. Drop Reverse/contaminant, filter `Localization prob`, then melt the per-multiplicity columns into rows.

```python
import pandas as pd
import numpy as np

# Filename has a SPACE in the modification name; accept either form.
phospho = pd.read_csv('Phospho (STY)Sites.txt', sep='\t', low_memory=False)

# Newer MaxQuant uses 'Potential contaminant'; older uses 'Contaminant'.
contaminant_col = 'Potential contaminant' if 'Potential contaminant' in phospho.columns else 'Contaminant'
phospho = phospho[(phospho['Reverse'] != '+') & (phospho[contaminant_col] != '+')]

CLASS_I_PROB = 0.75  # Olsen 2006 class-I convention; comparability standard, not a calibrated FLR
phospho = phospho[phospho['Localization prob'] >= CLASS_I_PROB].copy()

gene = phospho['Gene names'].where(phospho['Gene names'].notna(), phospho['Protein'])
phospho['site_id'] = gene.str.split(';').str[0] + '_' + phospho['Amino acid'] + phospho['Position'].astype(int).astype(str)

# Multiplicity columns carry THREE underscores: collapsing them mixes phospho-states.
mult_cols = [c for c in phospho.columns if '___' in c and c.split('___')[-1] in {'1', '2', '3'} and c.startswith('Intensity')]
long = phospho.melt(id_vars=['site_id', 'Amino acid', 'Position', 'Localization prob'], value_vars=mult_cols, var_name='run_multiplicity', value_name='intensity')
long['multiplicity'] = long['run_multiplicity'].str.split('___').str[-1]
long['run'] = long['run_multiplicity'].str.replace(r'___[123]$', '', regex=True).str.replace('Intensity ', '', regex=False)
long = long[long['intensity'] > 0]
long['log2_intensity'] = np.log2(long['intensity'])
```

## Protein-Level Adjustment with MSstatsPTM

**Goal:** Decide whether each site change is real after subtracting the matched protein-abundance change.

**Approach:** MSstatsPTM carries TWO datasets -- a PTM dataset (enriched) and a PROTEIN dataset (global/unenriched). `groupComparisonPTM` fits independent linear models to each and returns a list of THREE: `PTM.Model` (unadjusted), `PROTEIN.Model`, and `ADJUSTED.Model`. The adjustment is `dFC_adj = dFC_PTM - dFC_protein` with `SE_adj = sqrt(SE_PTM^2 + SE_protein^2)`, so adjustment ADDS uncertainty -- a site can be significant unadjusted yet lose significance after adjustment. A confident regulation call requires significance in `ADJUSTED.Model`.

```r
library(MSstatsPTM)

# Converters are <Tool>toMSstatsPTMFormat and return a list with $PTM and $PROTEIN.
# MaxQtoMSstatsPTMFormat reads the MaxQuant 'evidence.txt' (NOT the Phospho (STY)Sites
# table -- the pandas multiplicity-expansion above is a SEPARATE workflow); the FASTA maps
# peptides back to site coordinates. Supply BOTH the enriched evidence and the global
# proteinGroups; without the protein dataset there is nothing to adjust against.
# Arg-name note: the FASTA argument is `fasta_path` in current MSstatsPTM; older builds may
# differ -- run `?MaxQtoMSstatsPTMFormat` to confirm before relying on it.
input <- MaxQtoMSstatsPTMFormat(
  evidence = read.table('evidence.txt', sep = '\t', header = TRUE, quote = ''),
  annotation = read.csv('annotation_ptm.csv'),
  fasta_path = 'uniprot_human.fasta',
  fasta_protein_name = 'uniprot_ac',
  proteinGroups = read.table('proteinGroups.txt', sep = '\t', header = TRUE, quote = ''),
  annotation_protein = read.csv('annotation_protein.csv'),
  mod_id = '\\(Phospho \\(STY\\)\\)',
  which_proteinid_ptm = 'Proteins',
  use_unmod_peptides = FALSE
)

summarized <- dataSummarizationPTM(input, use_log_file = FALSE)
# LabelFree run: data.type = 'LF' (use 'TMT' for isobaric); contrast.matrix defaults to
# full pairwise. groupComparisonPTM has NO `model` argument -- it always fits independent
# PTM and PROTEIN models, then adjusts.
result <- groupComparisonPTM(summarized, data.type = 'LF')

# Three models; the adjusted one is the deliverable.
adjusted <- result$ADJUSTED.Model
regulated <- adjusted[!is.na(adjusted$adj.pvalue) & adjusted$adj.pvalue < 0.05 & abs(adjusted$log2FC) > 1, ]

# How much of each call was protein-driven: compare PTM.Model vs ADJUSTED.Model.
```

## Motif Analysis with the Correct Background

**Goal:** Find kinase/writer motifs around the modified residue without rediscovering amino-acid composition bias.

**Approach:** Use the `Sequence window` (+/-15 residues, 31-mer) MaxQuant already provides, centered on the site. The background MUST be an experiment-matched S/T/Y set drawn from the identified proteins (or a central-residue-preserving shuffle), NOT the whole proteome or IUPAC-random -- those just report the composition of phospho-rich disordered regions. motif-x and MoMo p-values are only valid when the background is built this way.

```python
from collections import Counter

# 'Sequence window' is a 31-mer (+/-15) centered on the modified residue.
WINDOW_HALF = 7  # +/-7 flanking is the standard kinase-motif window
foreground = [w[15 - WINDOW_HALF: 16 + WINDOW_HALF] for w in confident['Sequence window'].dropna() if len(w) >= 31]

# Background: same-residue windows from the matched dataset, NOT the whole proteome.
def position_frequencies(windows):
    counts = {i: Counter() for i in range(-WINDOW_HALF, WINDOW_HALF + 1)}
    for w in windows:
        for offset, aa in zip(range(-WINDOW_HALF, WINDOW_HALF + 1), w):
            if aa not in '_X':
                counts[offset][aa] += 1
    return counts
```

For a publication-grade enrichment logo, hand the foreground and a matched background to a dedicated tool (motif-x / MoMo) and render with data-visualization/sequence-logos.

## A Note on Home-Grown Ascore

The function below is an ILLUSTRATIVE approximation, NOT real Ascore. Real Ascore (Beausoleil 2006) competes the best localization against the second-best, sweeps peak depth 1-10 per 100 Th, and restricts to site-determining ions -- none of which this captures. Use the search engine's own localization probability (MaxQuant `Localization prob`, ptmRS, PTMProphet) for real work, or pyOpenMS `AScore` (introspect the exact API before relying on it). The home-grown form is here only to show the binomial intuition.

```python
import numpy as np
from scipy.stats import binom

def illustrative_localization_score(matched_site_ions, total_ions, depth_p=0.04):
    '''Binomial intuition only; NOT Ascore (no best-vs-second competition or depth sweep).'''
    if total_ions == 0 or matched_site_ions == 0:
        return 0.0
    p_random = 1 - binom.cdf(matched_site_ions - 1, total_ions, depth_p)
    return -10 * np.log10(p_random) if p_random > 0 else 100.0
```

## Per-Method Failure Modes

### Skipping protein-level adjustment
**Trigger:** Differential testing on a phospho-only run with no paired global proteome. **Mechanism:** `log2FC(PTM_observed) = log2FC(occupancy) + log2FC(protein)`; the two terms are inseparable. **Symptom:** Pathway-coherent "regulated sites" that are pure protein-abundance changes (cyclins/histones in cell cycle, stabilized substrates under drug). **Fix:** Run a matched global proteome and adjust via MSstatsPTM; route the protein-level quant to quantification.

### Collapsing the MaxQuant multiplicity
**Trigger:** Quantifying on base `Intensity` instead of `Intensity___1/___2/___3`. **Mechanism:** The collapsed column mixes singly/doubly/triply-phospho forms of the same site. **Symptom:** The singly-phospho form dropping as a neighbor gets phosphorylated reads as dephosphorylation. **Fix:** Expand multiplicity to long form (Perseus "Expand site table" or the melt above) before any stats.

### Treating identification as localization
**Trigger:** Reporting sites at peptide FDR without a localization threshold. **Mechanism:** Isobaric positional isomers share precursor mass and peptide score; CID/ion-trap neutral loss (-98 Da) starves site-determining ions. **Symptom:** A 1% peptide FDR result with a much higher true site error. **Fix:** Filter localization probability (class I >=0.75), report an empirical global FLR (LuciPHOr/DeepFLR), prefer HCD/EThcD.

### diGly read as ubiquitin
**Trigger:** Calling the K-GG proteome "ubiquitination". **Mechanism:** NEDD8 and ISG15 share the LRLRGG C-terminus and leave the identical +114.0429 remnant; iodoacetamide adds a fourth source. **Symptom:** Inflated/false ubiquitin sites, worst under interferon (ISG15) or with iodoacetamide. **Fix:** Chloroacetamide alkylation; treat K-GG as ub+NEDD8+ISG15; use UbiSite for ubiquitin-specific mapping.

### Motif logo against the wrong background
**Trigger:** Whole-proteome or IUPAC-random background. **Mechanism:** Phosphosites sit in disordered, Ser/Pro/acidic-rich regions; that composition dominates the enrichment. **Symptom:** "Enriched" proline/serine motifs that are region bias, not kinase preference. **Fix:** Experiment-matched S/T/Y background or central-residue-preserving shuffle (MoMo default).

### Over-reading kinase-activity output
**Trigger:** Naming the top KSEA/atlas kinase as the responsible enzyme. **Mechanism:** Substrate priors are PhosphoSitePlus-curated (CK2/CDK1/PKA/MAPK heavy); atlas hits are biochemical preference ignoring expression/localization/timing. **Symptom:** Always-the-usual-suspects kinase lists; dark-kinome activity invisible. **Fix:** Use a curated prior, report z-scores with their substrate counts, do not infer absence from silence.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|---|---|---|
| Localization prob class I >= 0.75 | Olsen 2006 | Best site holds >3x the posterior of all alternatives (single-phospho); a comparability standard, not a calibrated error rate |
| Class II 0.5-0.75; class III 0.25-0.5 | Olsen 2006 | Partial / poor localization |
| Ascore >= 19 (p~0.01); loose >13 | Beausoleil 2006 | Pairwise per-PSM best-vs-next confidence; NOT a dataset FLR |
| DIA directDIA localization >= 0.99 | Bekker-Jensen 2020 | Stricter than library-based (0.75) to match DDA error rates |
| DIA-NN site matrix 0.90 / 0.99 | DIA-NN docs | phosphosites_90/99.tsv; class-I-equivalent stringency is HIGHER than MaxQuant 0.75 |
| Acetyl missed cleavages >= 4 | -- | Acetyl-K blocks trypsin; pair LysC + trypsin |
| Kinase atlas motif match >= 90th percentile | Johnson 2023 | Strong motif preference, NOT proof the kinase acted |
| Report peptide FDR and site FLR separately | Fermin 2013 | 1% peptide FDR != 1% site FDR; true site error is typically several-fold higher |

## Common Errors

| Error / symptom | Cause | Solution |
|---|---|---|
| FileNotFoundError on the sites table | Filename has a SPACE: `Phospho (STY)Sites.txt` | Accept either spaced or no-space form |
| Apparent dephosphorylation that is not real | Quantified base `Intensity`, mixing multiplicities | Use `Intensity___1/___2/___3` (three underscores) |
| KeyError / NaN on `Gene names` | Column is FASTA-dependent, absent without gene annotation | Guard with `.notna()` and fall back to `Protein` |
| All sites "regulated" and pathway-coherent | No protein-level adjustment | Require significance in MSstatsPTM `ADJUSTED.Model` |
| `PTM.Q.Value` / `PhosphoSite` not found (DIA-NN) | Those columns do not exist | Use `PTM.Site.Confidence` and `Site.Occupancy.Probabilities` |
| False "ubiquitination" sites | Iodoacetamide +114.0429 lysine artifact | Alkylate with chloroacetamide |
| Acetyl confused with trimethyl | +42.0106 vs +42.0470 isobaric at nominal mass | Require high-res MS; check 0.0364 Da split |

## References

- Beausoleil SA, Villen J, Gerber SA, Rush J, Gygi SP. A probability-based approach for high-throughput protein phosphorylation analysis and site localization. *Nat Biotechnol* 2006;24(10):1285-1292.
- Taus T, Kocher T, Pichler P, et al. Universal and confident phosphorylation site localization using phosphoRS. *J Proteome Res* 2011;10(12):5354-5362.
- Olsen JV, Blagoev B, Gnad F, et al. Global, in vivo, and site-specific phosphorylation dynamics in signaling networks. *Cell* 2006;127(3):635-648.
- Fermin D, Walmsley SJ, Gingras AC, Choi H, Nesvizhskii AI. LuciPHOr: algorithm for phosphorylation site localization with false localization rate estimation using modified target-decoy approach. *Mol Cell Proteomics* 2013;12(11):3409-3419.
- Fermin D, Avtonomov D, Choi H, Nesvizhskii AI. LuciPHOr2: site localization of generic PTMs from tandem mass spectrometry data. *Bioinformatics* 2015;31(7):1141-1143.
- Bekker-Jensen DB, Bernhardt OM, Hogrebe A, et al. Rapid and site-specific deep phosphoproteome profiling by data-independent acquisition without the need for spectral libraries. *Nat Commun* 2020;11:787.
- Kohler D, Tsai TH, Verschueren E, et al. MSstatsPTM: Statistical Relative Quantification of Posttranslational Modifications in Bottom-Up Mass Spectrometry-Based Proteomics. *Mol Cell Proteomics* 2023;22(1):100477.
- Ochoa D, Jarnuczak AF, Vieitez C, et al. The functional landscape of the human phosphoproteome. *Nat Biotechnol* 2020;38(3):365-373.
- Casado P, Rodriguez-Prados JC, Cosulich SC, et al. Kinase-Substrate Enrichment Analysis Provides Insights into the Heterogeneity of Signaling Pathway Activation in Leukemia Cells. *Sci Signal* 2013;6(268):rs6.
- Krug K, Mertins P, Zhang B, et al. A Curated Resource for Phosphosite-specific Signature Analysis. *Mol Cell Proteomics* 2019;18(3):576-593.
- Yilmaz S, Ayati M, Schlatzer D, et al. Robust inference of kinase activity using functional networks. *Nat Commun* 2021;12:1177.
- Larsen MR, Thingholm TE, Jensen ON, Roepstorff P, Jorgensen TJD. Highly selective enrichment of phosphorylated peptides from peptide mixtures using titanium dioxide microcolumns. *Mol Cell Proteomics* 2005;4(7):873-886.
- Ruprecht B, Koch H, Medard G, et al. Comprehensive and reproducible phosphopeptide enrichment using iron immobilized metal ion affinity chromatography (Fe-IMAC) columns. *Mol Cell Proteomics* 2015;14(1):205-215.
- Matheron L, van den Toorn H, Heck AJR, Mohammed S. Characterization of biases in phosphopeptide enrichment by Ti(IV)-IMAC and TiO2 using a massive synthetic library and human cell digests. *Anal Chem* 2014;86(16):8312-8320.
- Thingholm TE, Jensen ON, Robinson PJ, Larsen MR. SIMAC (sequential elution from IMAC), a phosphoproteomics strategy for the rapid separation of monophosphorylated from multiply phosphorylated peptides. *Mol Cell Proteomics* 2008;7(4):661-671.
- Svinkina T, Gu H, Silva JC, et al. Deep, Quantitative Coverage of the Lysine Acetylome Using Novel Anti-acetyl-lysine Antibodies and an Optimized Proteomic Workflow. *Mol Cell Proteomics* 2015;14(9):2429-2440.
- Xu G, Paige JS, Jaffrey SR. Global analysis of lysine ubiquitination by ubiquitin remnant immunoaffinity profiling. *Nat Biotechnol* 2010;28(8):868-873.
- Kim W, Bennett EJ, Huttlin EL, et al. Systematic and Quantitative Assessment of the Ubiquitin-Modified Proteome. *Mol Cell* 2011;44(2):325-340.
- Nielsen ML, Vermeulen M, Bonaldi T, Cox J, Moroder L, Mann M. Iodoacetamide-induced artifact mimics ubiquitination in mass spectrometry. *Nat Methods* 2008;5(6):459-460.
- Akimov V, Barrio-Hernandez I, Hansen SVF, et al. UbiSite approach for comprehensive mapping of lysine and N-terminal ubiquitination sites. *Nat Struct Mol Biol* 2018;25(7):631-640.
- Riley NM, Bertozzi CR, Pitteri SJ. A Pragmatic Guide to Enrichment Strategies for Mass Spectrometry-Based Glycoproteomics. *Mol Cell Proteomics* 2021;20:100029.
- Johnson JL, Yaron TM, Huntsman EM, et al. An atlas of substrate specificities for the human serine/threonine kinome. *Nature* 2023;613(7945):759-766.
- Mueller-Dott S, Jaehnig EJ, et al. Comprehensive evaluation of phosphoproteomic-based kinase activity inference. *Nat Commun* 2025;16:4771.
- Zong Y, Wang Y, Yang Y, et al. DeepFLR facilitates false localization rate control in phosphoproteomics. *Nat Commun* 2023;14:2269.

## Related Skills

- peptide-identification - Identify modified peptides and run open/variable-mod search
- quantification - Underlying protein-level quant feeding the MSstatsPTM PROTEIN dataset
- differential-abundance - Moderated testing on the protein-level intensity matrix
- pathway-analysis/gsea - Enrichment scoring of regulated-site protein lists and PTM-SEA-style signatures
- data-visualization/sequence-logos - Render motif logos from the foreground/background windows
<!-- END FILE: proteomics/ptm-analysis/SKILL.md -->

## 子目录：proteomics/quantification

<!-- BEGIN FILE: proteomics/quantification/SKILL.md -->
---
name: bio-proteomics-quantification
description: Quantifies protein abundance from mass spectrometry using label-free (LFQ/MaxLFQ, DIA fragment-level), isobaric (TMT/iTRAQ reporter ions, MS2 vs SPS-MS3), and metabolic (SILAC) approaches, including peptide-to-protein summarization (Tukey median polish, MaxLFQ, msqrob), sample-loading and IRS cross-plex normalization, and isotopic impurity correction. Use when turning peptide/PSM/reporter signal into a protein-by-sample abundance matrix for downstream analysis. Statistical testing of that matrix is differential-abundance; DIA quant mechanics and DIA-NN runs are dia-analysis; reading search-engine outputs is data-import; razor/shared-peptide group assignment is protein-inference.
tool_type: mixed
primary_tool: MSstats
---

## Version Compatibility

Reference examples tested with: MSstats 4.10+, MSnbase 2.28+, iq 1.9+, numpy 1.26+, pandas 2.2+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Protein Quantification -- Reconstructing Protein Abundance from Ions Whose Physical Origin Dictates the Irreducible Error

**"Quantify proteins from my mass spec data"** -> Reconstruct a protein-by-sample abundance matrix from peptide/reporter ion signals, choosing a summarizer and normalizer that match where the signal physically came from -- because the measurement's physical origin sets an error that no normalization can remove.
- R: `MSstats::dataProcess()` (Tukey median polish summarization) for label-free feature-to-protein
- R: `iq::maxLFQ()` for the real MaxLFQ algorithm (delayed normalization + maximal peptide-ratio least-squares)
- R: `MSnbase::quantify(reporters=TMT10)` + `purityCorrect()` for isobaric reporter extraction
- R/Python: sample-loading + IRS scaling to bridge TMT plexes; per-sample median centering for LFQ

Scope: this skill OWNS converting peptide/PSM/reporter signal into a normalized protein abundance matrix (LFQ, TMT/iTRAQ, SILAC; summarization; normalization; IRS). Statistical testing of the matrix -> differential-abundance. DIA quant mechanics and DIA-NN execution -> dia-analysis. Parsing MaxQuant/DIA-NN outputs -> data-import. Razor/shared-peptide group assignment -> protein-inference. OUT OF SCOPE: missing-value imputation and the downshift false-positive trap (modeled in differential-abundance), and absolute copy-number calibration beyond a one-line pointer.

## The Single Most Important Modern Insight

1. **Every quant method answers "where does the signal physically come from?" differently, and that physical origin dictates the error structure no normalization can remove.** LFQ measures MS1 precursor area (or DIA fragment area) in SEPARATE runs -> the irreducible error is run-to-run variation plus stochastic, left-censored (MNAR) missingness. Isobaric TMT/iTRAQ measures low-m/z reporter ions from CO-ISOLATED, co-eluting peptides in ONE spectrum -> the irreducible error is RATIO COMPRESSION toward 1:1, a PHYSICAL co-isolation effect (interloper reporters add roughly equally to every channel), attacked at the instrument by SPS-MS3 and never fully undone in software. SILAC measures a heavy/light MS1 pair in the SAME scan -> lowest per-ratio variance, but its irreducible vulnerabilities are incomplete labeling and Arg->Pro label scrambling, which bias every ratio and cannot be corrected post hoc because channels are combined before any MS (a correctly mixed sample carries no inherent mixing error). Teach the signal origin and every threshold and failure mode below follows from it.

2. **The peptide-to-protein SUMMARIZATION choice is the highest-leverage decision in the pipeline, and it is invisible in the output.** In log space a peptide intensity is protein abundance + a peptide effect (ionization efficiency, flyability, missed cleavages, modifications) that spans orders of magnitude and is partly context-dependent, plus a run effect. Sum is dominated by the highest-flying peptide (dropout collapses it -> a fold change driven by detectability, not biology); mean is unbiased only if the detected peptide SET is identical across runs (it is not under MNAR); median discards relative-intensity information. Benchmarks confirm the quantification method is a dominant driver of which proteins are called differential (Lin 2022). Report the summarizer as prominently as the test, and run a sensitivity analysis across >=2 summarizers -- that is where the answer is most likely to move.

## Tool Taxonomy

| Tool / method | Citation | Mechanism / role | When |
|---|---|---|---|
| MaxLFQ | Cox 2014 | delayed normalization + maximal shared-peptide log-ratio least-squares; peptide scale cancels in pairwise ratios | label-free DDA/DIA relative quant across many samples |
| `iq::maxLFQ()` | Cox 2014 | R implementation of the real MaxLFQ; call it, do NOT reimplement | running MaxLFQ outside MaxQuant/DIA-NN |
| MSstats Tukey median polish | Choi 2014 | iteratively subtract peptide-medians + run-medians in log space; column effects = per-sample abundance; 50% breakdown | robust label-free default summarizer |
| msqrob (peptide-level) | Sticker 2020; Goeminne 2016 | treats the peptide effect as a covariate not noise; ridge + empirical Bayes + Huber | accuracy-critical small-n, unbalanced coverage (route OUT to differential-abundance) |
| iBAQ | -- | sum(peptide intensities) / number of theoretically observable tryptic peptides | rank / order-of-magnitude within-sample abundance |
| Top3 / Hi3 | Silva 2006 | sum/avg of top-3 peptide intensities, calibrate with one spiked standard | absolute amount, ~2 orders linear |
| Proteomic ruler | Wisniewski 2014 | histone signal as internal molar reference, no spike-in | absolute copies/cell without standards |
| Spectral counting / NSAF | Zybailov 2006 | count PSMs per protein, divide by protein LENGTH then total | largely OBSOLETE; niche AP-MS only |
| TMT/iTRAQ reporter | Ting 2011; McAlister 2014 | isobaric tag; reporter ratios at MS2 or SPS-MS3 | high multiplexing, zero run-to-run variation within a plex |
| SILAC | Ong 2002 | heavy/light precursor pair co-elute in the SAME MS1 scan | lowest-variance ratios, cell culture that can be labeled |
| DIA fragment-level | Demichev 2020 | MaxLFQ at the FRAGMENT level then roll up (route OUT to dia-analysis) | low-missingness label-free cohorts |

## Decision Tree by Scenario

| Scenario | Recommended | Why |
|---|---|---|
| Label-free DDA, MaxQuant evidence.txt | `MSstats::dataProcess` (TMP) | robust summarization with censored-value handling, the workhorse |
| Label-free, need MaxLFQ outside MaxQuant | `iq::maxLFQ()` | the real algorithm; median centering is NOT MaxLFQ |
| Label-free DIA matrix | -> dia-analysis | DIA-NN MaxLFQ at fragment level is owned there |
| TMT, accuracy critical | SPS-MS3 acquisition + reporter extraction | co-isolation rejected at the instrument; software cannot fully undo compression |
| TMT, single plex only | MS2 reporters + sample-loading normalization | within-plex ratios are stable |
| TMT, multiple plexes | sample-loading THEN IRS bridge (Plubell 2017) | absolute reporter intensities are NOT comparable across runs without a reference channel |
| SILAC ratios | verify labeling efficiency + Arg->Pro first | unchecked, both bias every ratio invisibly |
| Absolute copy number | proteomic ruler or Top3 + standard | iBAQ is within-sample rank only |
| AP-MS / affinity-enrichment pulldown | do NOT median/SL/IRS-normalize; control subtraction (SAINT/CompPASS/CRAPome) | an enrichment is not a balanced proteome; data-internal normalization erases the bait signal |
| Which summarizer? | run >=2 (TMP and MaxLFQ) and compare | this is the highest-leverage, invisible choice |

Default when uncertain: label-free DDA -> `MSstats::dataProcess` with `summaryMethod='TMP'`, `normalization='equalizeMedians'`; report the summarizer alongside results and sanity-check against `iq::maxLFQ()`.

## Label-Free Summarization and Normalization

### Summarize peptides to proteins with MSstats

**Goal:** Turn MaxQuant feature-level evidence into a normalized protein-level abundance matrix.

**Approach:** Reformat to MSstats input, then `dataProcess` applies median equalization and Tukey median polish (robust to outlier peptides, 50% breakdown) with censored-value handling for label-free missingness.

```r
library(MSstats)

maxquant_input <- MaxQtoMSstatsFormat(
    evidence = read.table('evidence.txt', sep = '\t', header = TRUE),
    proteinGroups = read.table('proteinGroups.txt', sep = '\t', header = TRUE),
    annotation = read.csv('annotation.csv')
)

# TMP = Tukey median polish; censoredInt='NA' treats missing intensities as left-censored
processed <- dataProcess(maxquant_input, normalization = 'equalizeMedians',
                         summaryMethod = 'TMP', censoredInt = 'NA', MBimpute = FALSE)

protein_abundance <- processed$ProteinLevelData
```

### Run the real MaxLFQ (not median centering)

**Goal:** Produce MaxLFQ protein intensities from a peptide quant matrix.

**Approach:** Call `iq::maxLFQ()`, which implements Cox 2014 delayed normalization and maximal peptide-ratio least-squares. Per-sample median centering shares only the name and silently gives a different answer.

```r
library(iq)

# rows = peptide ions, columns = samples, values = log2 intensities for ONE protein group
result <- maxLFQ(peptide_log2_matrix)
protein_estimate <- result$estimate    # one MaxLFQ value per sample
```

### Median-center label-free intensities (a normalizer, not a summarizer)

**Goal:** Correct per-sample loading differences before testing.

**Approach:** Subtract each sample's median log2 intensity (corrects LOCATION only; it cannot manufacture variance, so it is the safe default). Median centering normalizes; it does NOT summarize peptides to proteins.

```python
import numpy as np
import pandas as pd

log_int = np.log2(intensities.replace(0, np.nan))    # MaxQuant writes 0 for missing; log2(0) = -inf
sample_medians = log_int.median(axis=0)
normalized = log_int - sample_medians + sample_medians.median()
```

## Isobaric (TMT/iTRAQ) Quantification

### Extract and impurity-correct reporter ions

**Goal:** Pull TMT reporter intensities from spectra and correct cross-channel isotope bleed.

**Approach:** Read spectra on disk, `quantify` the reporter region, then `purityCorrect` with a LOT-SPECIFIC impurity matrix from the reagent Certificate of Analysis. `readMSnSet` reads an already-quantified text matrix and does NOT extract reporters.

```r
library(MSnbase)

raw <- readMSData('experiment.mzML', mode = 'onDisk')
# method='max' for centroided spectra; reporters=TMT10 defines the 126-131 reporter m/z
quant <- quantify(raw, reporters = TMT10, method = 'max')

# makeImpuritiesMatrix has manufacturer-default templates; REPLACE with lot-specific Certificate values
imp <- makeImpuritiesMatrix(x = 10)
quant <- purityCorrect(quant, imp)
```

### Bridge multiple TMT plexes with IRS

**Goal:** Make reporter intensities comparable across separate TMT runs.

**Approach:** Absolute reporter intensities for the same protein differ 2-5x between plexes because each plex samples a random point on the elution profile. Sample-loading normalization fixes within-run loading; the Internal Reference Scaling bridge (Plubell 2017) then pins each plex's pooled reference channel to a common per-protein value. Order: SL, then IRS.

```python
import numpy as np
import pandas as pd

# protein_psm_sums: protein x channel, summed PSM reporter ions; one reference channel per plex
def sample_loading_normalize(plex):
    target = plex.sum(axis=0).mean()    # common target = mean column sum within the plex
    return plex * (target / plex.sum(axis=0))

def irs_scale(plexes, ref_cols):
    refs = pd.concat([p[ref] for p, ref in zip(plexes, ref_cols)], axis=1)
    geomean = np.exp(np.log(refs.replace(0, np.nan)).mean(axis=1))    # per-protein geometric mean of references
    out = []
    for p, ref in zip(plexes, ref_cols):
        factor = geomean / p[ref]    # per-protein per-plex scaling factor
        out.append(p.mul(factor, axis=0))
    return out
```

## SILAC Quantification

**Goal:** Compute heavy/light ratios while preserving on/off biology and flagging label artifacts.

**Approach:** A protein present only in the heavy channel is the interesting biology, not a NaN to discard. Verify labeling efficiency (>=95%, target 97-98%) on a heavy-only pilot and assess Arg->Pro conversion before trusting any ratio.

```python
import numpy as np

# Arg10/Lys8 is the common pairing (avoids overlap with the +6 isotope envelope)
SILAC_SHIFTS = {'Arg10': 10.008269, 'Lys8': 8.014199, 'Arg6': 6.020129, 'Lys6': 6.020129}

def silac_log2_ratio(heavy, light):
    if heavy > 0 and light > 0:
        return np.log2(heavy / light)
    if heavy > 0 and light == 0:
        return np.inf     # present only in heavy: real on/off biology, do NOT discard as NaN
    if light > 0 and heavy == 0:
        return -np.inf
    return np.nan
```

## Per-Method Failure Modes

### MaxLFQ reimplemented as median centering
**Trigger:** A homebrew function named `maxlfq` that only subtracts per-sample medians.
**Mechanism:** Real MaxLFQ is delayed normalization plus a maximal peptide-ratio least-squares solve; median centering shares only the name.
**Symptom:** Plausible-looking but systematically different intensities; unbalanced peptide sets handled wrongly.
**Fix:** Call `iq::maxLFQ()`, DIA-NN, or MaxQuant.

### TMT ratio compression
**Trigger:** MS2-only reporter quant on a complex sample.
**Mechanism:** Co-isolated interloper peptides add reporters roughly equally to every channel, pulling large true ratios toward 1:1; PHYSICAL, not removable by normalization.
**Symptom:** "Nothing is significant"; attenuated fold changes, inflated false negatives.
**Fix:** SPS-MS3 acquisition, narrower isolation windows, FAIMS/ion mobility, or complement-reporter methods; a PIF filter helps but MS1 purity underestimates true interference (Savitski 2013).

### TMT plexes concatenated without IRS
**Trigger:** Stacking reporter intensities from multiple plexes directly.
**Mechanism:** Absolute reporter intensities for one protein differ 2-5x across runs from random elution-profile sampling, unrelated to abundance.
**Symptom:** Plex appears as the dominant axis of variation; spurious cross-plex differences.
**Fix:** Include a pooled reference channel in EVERY plex; apply sample-loading then IRS (Plubell 2017).

### Isotopic impurity matrix mis-applied
**Trigger:** Using the default/example impurity matrix, the wrong lot, or a transposed/mis-ordered (127N vs 127C) matrix.
**Mechanism:** A few percent of each channel bleeds to +/-1 Da neighbors; wrong values mis-subtract, negative corrected intensities get clipped.
**Symptom:** Adjacent channels silently biased; extreme contrasts placed in adjacent channels confounded.
**Fix:** Use the lot-specific Certificate of Analysis values; randomize channel-to-condition assignment.

### SILAC Arg->Pro conversion / incomplete labeling
**Trigger:** Pro-containing peptides or a labeling efficiency below ~95%.
**Mechanism:** Cells convert heavy Arg to heavy Pro (+6 Da), splitting Pro-peptide signal and underestimating the heavy channel; residual light masquerades as down-regulation.
**Symptom:** Ratios biased toward light, worse for Pro-rich proteins; invisible without a check.
**Fix:** Proline supplementation, measure conversion per cell line, verify >=95% incorporation on a heavy-only pilot.

### SILAC on/off proteins discarded as NaN
**Trigger:** Returning NaN whenever either channel is zero.
**Mechanism:** A protein present only in heavy (or only light) is the interesting biology, thrown away.
**Symptom:** Largest true changes silently dropped before analysis.
**Fix:** Record present-in-one-channel cases as +/-Inf or flag them; route honest absence handling to differential-abundance.

### Spectral counting / NSAF used for fold changes
**Trigger:** Reaching for PSM counts for quantitative comparison.
**Mechanism:** Count statistics are catastrophic at low abundance and saturate; dynamic exclusion deliberately breaks count-abundance proportionality. NSAF divides intensity by protein LENGTH then total -- a count divided by total spectra is not NSAF.
**Symptom:** Noisy, biased estimates; the wrong normalization labeled NSAF.
**Fix:** Use MS1/MS2 intensity (LFQ/DIA); keep spectral counting as historical context only.

### AP-MS / enrichment pulldown normalized as a balanced proteome
**Trigger:** Median/sample-loading/IRS normalization applied to an affinity-purification or biotin-enrichment pulldown.
**Mechanism:** Data-internal normalization assumes most signal is an unchanging background; a successful pulldown is deliberately non-representative (bait plus a few interactors over background), so equalizing medians or loading rescales away the enrichment being measured.
**Symptom:** Real interactors flattened toward background; bait abundance dominates the axis of variation.
**Fix:** Do not data-internal-normalize an enrichment; score against negative-control pulldowns (SAINT/CompPASS/CRAPome) or normalize to bait abundance.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|---|---|---|
| MaxLFQ min. ratio count = 2 | Cox 2014 (default) | a single shared peptide gives a ratio with no outlier rejection; >=2 lets the median start rejecting interference; setting 1 admits unguarded single-peptide ratios |
| PIF >= 0.75 | community filter | rejects spectra with too much interloper signal; but MS1 purity UNDERESTIMATES true reporter interference (Savitski 2013), so PIF ~0.9 can still be compressed |
| TMT N/C reporter spacing = 6.3 mDa | Thompson 2019 | 13C-vs-15N mass defect; needs high-res MS2 (>=30-50k) to resolve N from C channels |
| Reporter match tolerance ~0.002-0.003 Da | -- | tight enough to separate 6.3 mDa N/C channels at high resolution |
| SILAC labeling efficiency >= 95% (target 97-98%) | -- | residual light contaminates the heavy channel -> false down-regulation; needs ~5-6 doublings |
| Min peptides per protein for quant >= 2 | -- | single-peptide (one-hit) proteins are quant-unreliable |
| Top3 uses exactly the top 3 peptides | Silva 2006 | most intense peptides are most reproducibly detected, closest to uniform per-mole response |

## Common Errors

| Error / symptom | Cause | Solution |
|---|---|---|
| `readMSnSet` does not extract reporters | it reads an already-quantified text matrix | use `readMSData(mode='onDisk')` then `quantify(reporters=TMT10, method='max')` |
| `log2(0) = -inf` in the matrix | MaxQuant writes 0 for "not quantified" | replace 0 -> NaN before any transform |
| Reading `Intensity` when ratios needed | `Intensity` is raw, not normalized; `iBAQ` is within-sample only | use `LFQ intensity` for between-sample LFQ ratios (see data-import) |
| Median centering called MaxLFQ | homebrew shares only the name | call `iq::maxLFQ()` / DIA-NN / MaxQuant |
| `MBimpute=TRUE` injects values silently | AFT imputation in `dataProcess` | set `MBimpute=FALSE`; model missingness in differential-abundance |
| Cross-plex TMT comparison is invalid | no reference channel / no IRS | add a pooled reference channel per plex, apply SL then IRS |
| MSnbase deprecation warnings | MSnbase is in maintenance mode | current pipelines use Spectra + QFeatures (`readQFeatures`, `aggregateFeatures`) |

## References

- Cox J, Hein MY, Luber CA, Paron I, Nagaraj N, Mann M. 2014. Accurate proteome-wide label-free quantification by delayed normalization and maximal peptide ratio extraction, termed MaxLFQ. *Mol Cell Proteomics* 13(9):2513-2526.
- Silva JC, Gorenstein MV, Li GZ, Vissers JPC, Geromanos SJ. 2006. Absolute quantification of proteins by LCMSE: a virtue of parallel MS acquisition. *Mol Cell Proteomics* 5(1):144-156.
- Wisniewski JR, Hein MY, Cox J, Mann M. 2014. A "proteomic ruler" for protein copy number and concentration estimation without spike-in standards. *Mol Cell Proteomics* 13(12):3497-3506.
- Zybailov B, Mosley AL, Sardiu ME, et al. 2006. Statistical analysis of membrane proteome expression changes in Saccharomyces cerevisiae. *J Proteome Res* 5(9):2339-2347.
- Ong SE, Blagoev B, Kratchmarova I, et al. 2002. Stable isotope labeling by amino acids in cell culture, SILAC, as a simple and accurate approach to expression proteomics. *Mol Cell Proteomics* 1(5):376-386.
- Ting L, Rad R, Gygi SP, Haas W. 2011. MS3 eliminates ratio distortion in isobaric multiplexed quantitative proteomics. *Nat Methods* 8(11):937-940.
- McAlister GC, Nusinow DP, Jedrychowski MP, Wuhr M, et al. 2014. MultiNotch MS3 enables accurate, sensitive, and multiplexed detection of differential expression across cancer cell line proteomes. *Anal Chem* 86(14):7150-7158.
- Savitski MM, Mathieson T, Zinn N, et al. 2013. Measuring and managing ratio compression for accurate iTRAQ/TMT quantification. *J Proteome Res* 12(8):3586-3598.
- Thompson A, Wolmer N, Koncarevic S, et al. 2019. TMTpro: design, synthesis, and initial evaluation of a proline-based isobaric 16-plex tandem mass tag reagent set. *Anal Chem* 91(24):15941-15950.
- Plubell DL, Wilmarth PA, Zhao Y, et al. 2017. Extended multiplexing of tandem mass tags (TMT) labeling reveals age and high fat diet specific proteome changes in mouse epididymal adipose tissue. *Mol Cell Proteomics* 16(5):873-890.
- Choi M, Chang CY, Clough T, et al. 2014. MSstats: an R package for statistical analysis of quantitative mass spectrometry-based proteomic experiments. *Bioinformatics* 30(17):2524-2526.
- Goeminne LJE, Gevaert K, Clement L. 2016. Peptide-level robust ridge regression improves estimation, sensitivity, and specificity in data-dependent quantitative label-free shotgun proteomics. *Mol Cell Proteomics* 15(2):657-668.
- Sticker A, Goeminne L, Martens L, Clement L. 2020. Robust summarization and inference in proteome-wide label-free quantification. *Mol Cell Proteomics* 19(7):1209-1219.
- Demichev V, Messner CB, Vernardis SI, Lilley KS, Ralser M. 2020. DIA-NN: neural networks and interference correction enable deep proteome coverage in high throughput. *Nat Methods* 17(1):41-44.
- Lin MH, Wu PS, Wong TH, Lin IY, Lin J, Cox J, Yu SH. 2022. Benchmarking differential expression, imputation and quantification methods for proteomics data. *Brief Bioinform* 23(3):bbac138.

## Related Skills

- data-import - Parse MaxQuant/DIA-NN outputs and pick the right intensity column before quantifying
- protein-inference - Razor/shared-peptide group assignment that determines which protein a peptide counts toward
- differential-abundance - Statistical testing, missing-value modeling, and the downshift false-positive trap
- proteomics-qc - CV, correlation, and PCA checks that confirm normalization worked
- dia-analysis - DIA fragment-level MaxLFQ and DIA-NN execution
- differential-expression/de-results - Shared empirical-Bayes and FDR conventions for expression matrices
- data-visualization/heatmaps-clustering - Visualize the normalized abundance matrix
- workflows/proteomics-pipeline - End-to-end pipeline that calls this skill for the quant step
<!-- END FILE: proteomics/quantification/SKILL.md -->

## 子目录：proteomics/spectral-libraries

<!-- BEGIN FILE: proteomics/spectral-libraries/SKILL.md -->
---
name: bio-proteomics-spectral-libraries
description: Builds and manages DIA spectral libraries as peptide query parameters (precursor m/z, a few fragment m/z plus relative intensities, normalized RT, optional CCS), covering experimental DDA, chromatogram, and in-silico predicted libraries via Koina-served Prosit, AlphaPeptDeep, MS2PIP, and DeepLC, with iRT/CiRT RT calibration, NCE tuning, format conversion (DIA-NN tsv/speclib/parquet, OpenSWATH pqp/TraML, Spectronaut, blib/dlib/elib), and library QC/merge. Use when generating, calibrating, converting, or merging a spectral library to drive a DIA search. Running the actual DIA search is dia-analysis; building from DDA identifications depends on peptide-identification; modified-peptide libraries route to ptm-analysis; quantifying the result is quantification.
tool_type: mixed
primary_tool: encyclopedia
---

## Version Compatibility

Reference examples tested with: koinapy 0.0.5+, ms2pip 4.0+, deeplc 3.0+, pandas 2.2+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# DIA Spectral Libraries -- Query Parameters That Are Only as Good as Their Empirical Calibration

**"Build a spectral library for my DIA search"** -> Assemble a table of peptide query parameters (precursor m/z, top fragment m/z plus relative intensities, normalized RT, optional CCS), then calibrate the predicted RT/CCS to the actual gradient/instrument -- because a DIA library is not whole spectra and an uncalibrated prediction extracts every peak group at the wrong time.
- Python: `koinapy.Koina(...).predict(df)` for Prosit/AlphaPeptDeep/MS2PIP/UniSpec fragment intensities and iRT served from Koina
- Python: `deeplc.DeepLC().calibrate_preds(); .make_preds()` for RT prediction of any modification
- Python: `ms2pip.predict_batch(psms, model='HCD')` for local fragment-intensity prediction
- CLI: EncyclopeDIA for empirical chromatogram libraries; EasyPQP/FragPipe for DDA-based libraries

Scope: this skill owns library generation (experimental, chromatogram, predicted, empirically-corrected), RT/CCS/NCE calibration, format conversion, and library QC/merge. Running the DIA search against the library is dia-analysis. Generating the DDA peptide identifications a DDA library is built from depends on peptide-identification. Modified-peptide and PTM-resolved library design routes to ptm-analysis. Quantifying and rolling up the search output is quantification. OUT OF SCOPE: acquisition-window design (fixed/variable/staggered/diaPASEF) and demultiplexing -- those belong to dia-analysis.

## The Single Most Important Modern Insight -- A Predicted Library Is Only as Good as Its Empirical Calibration

1. **A DIA library is peptide QUERY PARAMETERS, not spectra.** Each entry is a precursor m/z, a handful of fragment m/z with RELATIVE intensities, a normalized RT, and optionally CCS -- the inputs to extract and score a co-eluting fragment-chromatogram peak group, not a lookup spectrum to match (Gillet 2012). The fragments and their relative intensities are the discriminating content; absolute intensity is irrelevant.

2. **Fragment-intensity prediction is robust; predicted RT and CCS are in ARBITRARY model units and MUST be calibrated.** HCD fragmentation is reproducible at matched collision energy, so predicted relative intensities transfer across instruments. But predicted iRT is an arbitrary scale and real RT depends on the exact column, gradient, temperature, and mobile phase. The catastrophic error: drop a predicted library straight into a search without anchoring its RT to observed RT (via iRT/CiRT spike-in peptides or a GPF-DIA empirical pass). Every peak group is then extracted at the wrong time, selectivity collapses, and IDs silently disappear with no error. The same holds for AlphaPeptDeep CCS against the timsTOF's measured 1/K0.

3. **NCE (normalized collision energy) must match the predictor's training or intensities mismatch the real spectra.** Intensity predictors are conditioned on NCE. Feed a value that differs from the instrument's effective NCE and predicted intensities diverge from reality, losing sensitivity with no error. Do not blindly use NCE=30 from a tutorial -- scan candidate NCE values, predict, and pick the one maximizing spectral contrast/correlation against a few real spectra.

## Tool Taxonomy

| Library type / tool | Citation | Mechanism / role | When |
|---------------------|----------|------------------|------|
| Experimental DDA (EasyPQP, FragPipe) | -- | Consensus spectra from DDA runs of the same/pooled sample | Deep DDA already in hand; gold-standard real intensities |
| Chromatogram library (EncyclopeDIA, GPF) | Searle 2018 | GPF-DIA of pooled sample, narrow staggered windows -> empirical RT + real fragments in the actual LC | One project, maximum depth without fractionated DDA |
| In-silico predicted (Prosit, AlphaPeptDeep, MS2PIP+DeepLC) | Gessulat 2019; Zeng 2022 | Deep learning predicts fragment intensities + RT (+CCS) for the whole FASTA digest | No wet-lab library; the default modern route |
| Empirically-corrected predicted (EncyclopeDIA) | Searle 2020 | Predict whole-proteome library, search one GPF-DIA pass, rewrite intensities + RT with observed values | Non-model organisms, variant DBs; best of predicted + empirical |
| Prosit (intensity + iRT) | Gessulat 2019 | HCD/CID intensity conditioned on NCE; iRT model | Served via Koina; broad default predictor |
| AlphaPeptDeep (intensity + RT + CCS) | Zeng 2022 | Modular, retrainable; b/y plus mod neutral losses; predicts CCS | Full predicted library including ion mobility |
| MS2PIP (intensity) | -- | Fast HCD/CID/TMT/immuno intensity models; RT via DeepLC | Local prediction without a server; pairs with DeepLC |
| DeepLC (RT, any modification) | Bouwmeester 2021 | RT prediction for novel/modified peptides; needs calibration peptides | RT for peptidoforms carrying unseen modifications |
| UniSpec (NIST) | -- | Full-range intensity including internal/immonium ions | Available on Koina when richer fragment sets are needed |
| SpectraST (TPP) | -- | Legacy DDA consensus library builder | Legacy only; prefer EasyPQP/FragPipe instead |
| Acquisition window design / demux | -- | Fixed/variable/staggered/diaPASEF schemes | route OUT -> dia-analysis |

## Decision Tree by Scenario

| Scenario | Recommended | Why |
|----------|-------------|-----|
| No prior DDA, model organism, standard mods | Predicted library (Prosit or AlphaPeptDeep via Koina) + iRT calibration | Whole-proteome coverage, bounded search; calibrate RT to the gradient |
| Need ion mobility (timsTOF/diaPASEF) | AlphaPeptDeep (intensity + RT + CCS) | Only predictor here that emits CCS; calibrate CCS to measured 1/K0 |
| Non-model organism or custom/variant DB | Empirically-corrected predicted (Searle 2020) | One GPF-DIA pass rewrites predicted intensities/RT with observed values |
| Maximum depth for one project, have pooled sample | Chromatogram library (EncyclopeDIA + GPF) | Empirical RT and real fragmentation in the actual LC |
| Deep fractionated DDA already acquired | Experimental DDA library (EasyPQP/FragPipe) | Real consensus spectra; gold-standard intensities |
| Library for OpenSWATH | Any source, then OpenSwathDecoyGenerator | OpenSWATH needs decoys IN the library; target-only has no null |
| Modified/PTM peptidoforms required | Include mods in digest; DeepLC for RT of unseen mods | route to ptm-analysis for PTM-resolved design |

Default when uncertain: a Koina-served predicted library (Prosit intensity + iRT) with explicit iRT/CiRT RT calibration and an NCE scan, exported to the search engine's native format.

### Generate a Predicted Library via Koina

**Goal:** Produce fragment intensities and iRT for a peptide list without a local GPU or wet-lab library.

**Approach:** Send a DataFrame of peptide sequences, charges, and collision energies to a Koina-hosted model; the dead proteomicsdb endpoint is replaced by the Koina server. Network calls are shown; the runnable example operates on an in-memory table so it needs no network.

```python
# Koina serves Prosit/AlphaPeptDeep/MS2PIP/UniSpec predictions; verify the
# koinapy constructor signature and input column names at runtime with help(Koina).
from koinapy import Koina
import pandas as pd

inputs = pd.DataFrame({
    'peptide_sequences': ['LGGNEQVTR', 'VEATFGVDESNAK'],
    'precursor_charges': [2, 2],
    'collision_energies': [30, 30]  # NCE; scan candidates and pick max spectral contrast
})

intensity_model = Koina('Prosit_2019_intensity', 'koina.wilhelmlab.org:443')
fragments = intensity_model.predict(inputs)  # mz, intensities, annotation per fragment

irt_model = Koina('Prosit_2019_irt', 'koina.wilhelmlab.org:443')
irt = irt_model.predict(inputs[['peptide_sequences']])  # arbitrary iRT units -- calibrate before use
```

### Calibrate iRT to Observed RT

**Goal:** Map arbitrary-unit predicted iRT onto the run's real RT so peak groups extract at the right time.

**Approach:** Spike or detect anchor peptides (11 Biognosys iRT peptides, or CiRT endogenous peptides when no spike-in exists), fit a regression from library iRT to observed RT, and require a tight fit before trusting it. A global linear fit fails on nonlinear gradients -- fall back to LOWESS.

```python
import numpy as np
from scipy import stats

IRT_PEPTIDES = {'LGGNEQVTR': -24.92, 'GAGSSEPVTGLDAK': 0.00, 'VEATFGVDESNAK': 12.39,
                'YILAGVENSK': 19.79, 'TPVISGGPYEYR': 28.71, 'TPVITGAPYEYR': 33.38,
                'DGLDAASYYAPVR': 42.26, 'ADVTPADFSEWSK': 54.62, 'GTFIIDPGGVIR': 70.52,
                'GTFIIDPAAVIR': 87.23, 'LFLQFGAQGSPFLK': 100.00}

R2_MIN = 0.95  # below this the RT alignment is untrustworthy and extraction windows are misplaced

def fit_irt_to_rt(anchor_irt, observed_rt):
    slope, intercept, r, _, _ = stats.linregress(anchor_irt, observed_rt)
    if r ** 2 < R2_MIN:
        raise ValueError(f'iRT fit R^2={r**2:.3f} < {R2_MIN}; gradient may be nonlinear, use LOWESS')
    return lambda irt: slope * irt + intercept
```

### Convert Library Formats

**Goal:** Move a library between DIA-NN, OpenSWATH, and Spectronaut conventions without silently corrupting RT, intensity, modification, or decoy content.

**Approach:** Conversion is renaming columns AND reconciling units, not a copy. Check RT units (iRT ~ -25..150 vs normalized 0-1 vs minutes), intensity scaling (relative vs absolute), and modification notation (UniMod:35 vs +15.9949 vs Oxidation). For OpenSWATH, generate decoys with OpenSwathDecoyGenerator -- a target-only library has no null.

```python
import pandas as pd

# Spectronaut -> DIA-NN column mapping; iRT and RelativeIntensity are renamed, not recomputed.
SPECTRONAUT_TO_DIANN = {'ModifiedPeptide': 'ModifiedPeptide', 'iRT': 'iRT',
                        'RelativeIntensity': 'LibraryIntensity', 'FragmentMz': 'ProductMz',
                        'FragmentNumber': 'FragmentSeriesNumber', 'PrecursorMz': 'PrecursorMz',
                        'PrecursorCharge': 'PrecursorCharge', 'FragmentCharge': 'FragmentCharge',
                        'FragmentType': 'FragmentType', 'Genes': 'Genes'}

def spectronaut_to_diann(lib):
    out = lib.rename(columns=SPECTRONAUT_TO_DIANN)
    assert out['iRT'].between(-50, 200).all(), 'RT not in iRT units; check column before converting'
    return out
```

### QC and Merge Libraries

**Goal:** Summarize a library and combine multiple libraries without dropping legitimate distinct transitions.

**Approach:** Report precursor/protein counts and transitions-per-precursor, then dedup on the FULL transition key. Deduping on (sequence, fragment-type, fragment-number) alone drops real transitions that differ only in precursor charge or fragment charge -- key on all five.

```python
import pandas as pd

TRANSITION_KEY = ['ModifiedSequence', 'PrecursorCharge', 'FragmentType',
                  'FragmentSeriesNumber', 'FragmentCharge']  # full key; charges matter

def merge_libraries(libs):
    combined = pd.concat(libs, ignore_index=True)
    combined['precursor_total'] = combined.groupby(
        ['ModifiedSequence', 'PrecursorCharge'])['LibraryIntensity'].transform('sum')
    combined = combined.sort_values('precursor_total', ascending=False)
    combined = combined.drop_duplicates(subset=TRANSITION_KEY).drop(columns='precursor_total')
    return combined

def library_stats(lib):
    n_prec = lib.groupby(['ModifiedSequence', 'PrecursorCharge']).ngroups
    return {'precursors': n_prec, 'proteins': lib['ProteinId'].nunique(),
            'transitions_per_precursor': round(len(lib) / n_prec, 1)}
```

## Per-Method Failure Modes

### Predicted RT/CCS used without calibration
**Trigger:** A predicted library is searched directly, RT column straight from the model.
**Mechanism:** Predicted iRT/CCS are arbitrary model units; real RT depends on column/gradient/temperature.
**Symptom:** Drastic ID loss with no error; peak groups extracted at the wrong time.
**Fix:** Fit iRT/CiRT anchors (R^2 > 0.95) or run a GPF-DIA empirical correction (Searle 2020) before searching.

### NCE mismatch
**Trigger:** A fixed collision energy (often 30) reused across instruments/methods.
**Mechanism:** Intensity predictors are NCE-conditioned; wrong NCE shifts predicted relative intensities.
**Symptom:** Quiet sensitivity loss; fewer confident peak groups than expected.
**Fix:** Scan candidate NCE values, predict, and pick the one maximizing spectral contrast against real spectra.

### Missing decoys for OpenSWATH
**Trigger:** A target-only library handed to OpenSWATH.
**Mechanism:** Peptide-centric scoring needs a decoy null; OpenSWATH does not invent one.
**Symptom:** FDR cannot be estimated or is meaningless.
**Fix:** Run OpenSwathDecoyGenerator to append decoys; do NOT also supply decoys to DIA-NN/Spectronaut, which generate their own.

### Modification mismatch between library and data
**Trigger:** Library lacks the sample's variable mods, or carries too many.
**Mechanism:** A library without phospho/ox cannot find those peptidoforms; too many variable mods explode the search space and inflate FDR.
**Symptom:** Missing modified peptides, or inflated IDs.
**Fix:** Match library modifications to the biology; route PTM-resolved design to ptm-analysis.

### Naive merge dropping transitions
**Trigger:** Dedup keyed on (sequence, fragment-type, fragment-number) only.
**Mechanism:** Distinct transitions can share those three fields but differ in precursor or fragment charge.
**Symptom:** Quietly thinner transition lists; weaker peak-group scoring.
**Fix:** Key dedup on (modified-sequence, precursor-charge, fragment-type, fragment-number, fragment-charge).

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| 6 fragments per precursor | OpenSWATH/EncyclopeDIA defaults | Enough for confident peak-group scoring; more invites interference |
| Fragment m/z > precursor m/z, and > ~200 | Practice | Avoids the low-mass region dense with shared/uninformative ions |
| Library FDR 1% (peptide and protein) | EasyPQP defaults | A dirty library poisons every downstream search |
| iRT regression R^2 > 0.95 | Practice | Below this RT alignment is untrustworthy and windows misplace |
| NCE chosen by spectral-contrast scan | Practice | Matches the predictor's training to the instrument's effective NCE |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| ConnectionError on proteomicsdb.org/prosit/api/predict | The old Prosit endpoint is dead | Use Koina: `from koinapy import Koina; Koina('Prosit_2019_intensity', 'koina.wilhelmlab.org:443')` |
| ImportError: cannot import name Predictor from ms2pip | No Predictor class in ms2pip v4 | Call module-level `ms2pip.predict_batch(psms, model='HCD')` returning ProcessingResult objects |
| koinapy TypeError on constructor/columns | Constructor signature and column names vary by version | Verify with `help(Koina)`; inputs are typically `peptide_sequences`, `precursor_charges`, `collision_energies` |
| DeepLC RT all near constant | calibrate_preds not called | `dlc.calibrate_preds(seq_df=cal_df)` before `dlc.make_preds(seq_df=pep_df)`; mods as MS2PIP `location|name` |
| Extraction at wrong time, ID collapse | Predicted RT not calibrated to the gradient | Fit iRT/CiRT anchors or run GPF-DIA empirical correction before searching |
| OpenSWATH FDR meaningless | Target-only library, no decoys | Append decoys with OpenSwathDecoyGenerator |
| Fewer transitions than expected after merge | Dedup key missed charges | Key on the full five-field transition key |

## References

- Gillet LC, Navarro P, Tate S, et al. Targeted data extraction of the MS/MS spectra generated by data-independent acquisition: a new concept for consistent and accurate proteome analysis. *Mol Cell Proteomics* 2012;11(6):O111.016717.
- Searle BC, Pino LK, Egertson JD, et al. Chromatogram libraries improve peptide detection and quantification by data independent acquisition mass spectrometry. *Nat Commun* 2018;9:5128.
- Gessulat S, Schmidt T, Zolg DP, et al. Prosit: proteome-wide prediction of peptide tandem mass spectra by deep learning. *Nat Methods* 2019;16(6):509-518.
- Searle BC, Swearingen KE, Barnes CA, et al. Generating high quality libraries for DIA MS with empirically corrected peptide predictions. *Nat Commun* 2020;11:1548.
- Bouwmeester R, Gabriels R, Hulstaert N, Martens L, Degroeve S. DeepLC can predict retention times for peptides that carry as-yet unseen modifications. *Nat Methods* 2021;18(11):1363-1369.
- Zeng WF, Zhou XX, Willems S, et al. AlphaPeptDeep: a modular deep learning framework to predict peptide properties for proteomics. *Nat Commun* 2022;13:7238.

## Related Skills

- dia-analysis - Run the DIA search against the library and choose the q-value context
- peptide-identification - Generate the DDA identifications a DDA library is built from
- ptm-analysis - Design PTM-resolved and modified-peptide libraries
- quantification - Summarize and roll up the search output to protein abundances
<!-- END FILE: proteomics/spectral-libraries/SKILL.md -->

<!-- END CATEGORY: proteomics -->

