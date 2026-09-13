---
slug: bio-imaging-mass-cytometry-integrated
version: 1.0.1
displayName: "成像质谱流式 / Imaging mass cytometry (IMC/MIBI)"
name: bio-imaging-mass-cytometry-integrated
summary: "中文：成像质谱流式综合技能，整合 7 个相关专题，覆盖成像质谱流式（IMC/MIBI）：预处理、分割、表型分析、空间分析、患者水平差异分析。 English: Integrated Imaging mass cytometry (IMC/MIBI) skill covering 7 related topics, including Imaging mass cytometry (IMC/MIBI): preprocessing, segmentation, phenotyping, spatial analysis, patient-level differential analysis."
description: "中文：这是一个面向成像质谱流式的综合生物信息学 Skill，整合当前分类下 7 个相关专题能力。它用于根据研究问题、数据类型和分析阶段，选择合适的方法与工具，规划从输入检查、预处理、核心分析到质量控制、统计解释和结果报告的完整流程。重点覆盖：成像质谱流式（IMC/MIBI）：预处理、分割、表型分析、空间分析、患者水平差异分析。当用户提供相关实验数据、测序结果、表格或研究问题时，它会帮助判断分析目标与前置条件，给出工具选择、关键参数、输入输出、常见失败原因、结果解读和可复现建议。主要工具包括：CATALYST, deepcell, diffcyt。该 Skill 提供分析设计与实施指导，不替代对具体数据质量、生物学背景和最终结论的人工审查。 English: This is an integrated bioinformatics Skill for Imaging mass cytometry (IMC/MIBI), combining 7 related topic areas. It helps users choose appropriate methods and tools based on the research question, data type, and analysis stage, and plan an end-to-end workflow from input validation and preprocessing through core analysis, quality control, statistical interpretation, and reporting. It covers Imaging mass cytometry (IMC/MIBI): preprocessing, segmentation, phenotyping, spatial analysis, patient-level differential analysis. For relevant experimental data, sequencing results, tables, or research questions, it clarifies prerequisites, recommends tools and parameters, describes expected inputs and outputs, explains common failure modes, and supports reproducible analysis. Primary tools include: CATALYST, deepcell, diffcyt. It provides methodological and implementation guidance; final data-quality assessment and biological conclusions still require human review."
---

# imaging-mass-cytometry 分类 Skill 整合版

> 本文件整合同一主分类目录下 7 个子目录中的 SKILL.md 内容。
> 各子目录正文按原文保留，并通过标题和边界标记进行区分；源文件中的元数据块未被改写。

---

<!-- BEGIN CATEGORY: imaging-mass-cytometry -->

## 子目录：imaging-mass-cytometry/cell-segmentation

<!-- BEGIN FILE: imaging-mass-cytometry/cell-segmentation/SKILL.md -->
---
name: bio-imaging-mass-cytometry-cell-segmentation
description: Segment single cells from multiplexed IMC/MIBI tissue images using Mesmer/DeepCell, Cellpose, or ilastik+CellProfiler, covering whole-cell vs nuclear segmentation, the summed-membrane-channel decision, nuclear-expansion bias, lateral spillover, resolution-floor parameters, and downstream-proxy evaluation. Use when delineating cells after preprocessing, choosing a segmentation model, building a cell mask for quantification, diagnosing impossible double-positive populations, or troubleshooting over/under-segmentation.
tool_type: python
primary_tool: deepcell
---

## Version Compatibility

Reference examples tested with: steinbock 0.16+, DeepCell 0.12+ (Mesmer), Cellpose 3.0+, numpy 1.26+, scikit-image 0.22+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

Notes specific to this skill: Mesmer expects `(batch, y, x, 2)` with channel 0 = nuclear, channel 1 = membrane, and `image_mpp` set to the TRUE acquisition resolution (~1.0 for IMC) -- it was trained at `model_mpp ~= 0.5` and rescales the input, so a wrong mpp degrades everything. Cellpose `cyto` trains at 30-px and `nuclei` at 17-px diameter; steinbock feeds nuclear-first (reversed vs native Cellpose). Recent steinbock cellpose containers default to the `cpsam` (Cellpose-SAM) model -- pin the version.

# Cell Segmentation for IMC

**"Segment cells from my IMC images"** -> Draw a per-cell boundary mask so that averaging the channels inside each mask yields single-cell expression.
- Python: `deepcell.applications.Mesmer().predict(...)`, `cellpose.models`
- CLI: `steinbock segment deepcell`, `steinbock segment cellpose`

## The Single Most Important Modern Insight -- segmentation is the largest irreversible error source, not a preprocessing step

A single-cell table is literally `for each mask_id: mean(pixels_in_mask, every_channel)`, so the mask defines the support of every measurement and no downstream step -- clustering, batch correction, differential abundance -- can recover a cell the mask merged or split. Two failure modes, and their asymmetry dictates how to tune. Under-segmentation (two cells in one mask) produces LOUD, catchable artifacts: a mask spanning a T cell and a macrophage reports CD3+CD68+, so biologically-impossible co-expression is a segmentation diagnosis until proven otherwise, not a discovery. Over-segmentation (one cell fragmented) is the QUIET, dangerous error: each fragment still looks like a plausible cell, but counts inflate and spatial-neighborhood statistics corrupt without obvious tells. Tuning a watershed or threshold until masks "look clean" usually trades the loud error for the quiet one, which is worse for spatial work. A second, independent problem rides on top: lateral (spatial) spillover -- real signal from a neighbor's membrane bleeding across the shared boundary at ~1 um resolution -- produces the same impossible-co-expression signature even with flawless masks and perfect channel compensation, so the two are confounded and must be addressed separately (REDSEA after segmentation; channel compensation before aggregation).

## Methods Landscape

| Tool / model | Class | Input it consumes | Strength | Fails when |
|--------------|-------|-------------------|----------|------------|
| Mesmer / DeepCell (Greenwald 2022) | deep, trained on TissueNet (incl. IMC/MIBI) | 2-ch: nuclear + summed membrane | purpose-built for multiplexed tissue; the IMC default | summed membrane channel is weak/patchy; wrong `image_mpp` |
| Cellpose / `cpsam` (Stringer 2021; Pachitariu 2025) | deep, flow-field / SAM backbone | 1-2 ch (cyto +- nuclear) | generalist; `cpsam` needs no diameter | default models carry a non-IMC size prior; wrong `diameter` |
| StarDist (Schmidt 2018) | star-convex polygon regression | single nuclear ch | excellent for crowded round nuclei | nuclear-only; breaks on irregular/elongated cells |
| ilastik + CellProfiler (Berg 2019; McQuin 2018) | random-forest pixels -> watershed | painted nucleus/cyto/background | transparent, tunable, no GPU; original IMC pipeline | semantic not instance; seed-threshold-sensitive; manual tuning |

## Decision Tree by Scenario

| Scenario | Recommended | Why |
|----------|-------------|-----|
| Whole-cell phenotyping with a good broadly-expressed membrane marker set | Mesmer whole-cell, `image_mpp` = true resolution | TissueNet includes this modality; first choice for IMC/MIBI |
| Membrane staining weak/patchy/cell-type-specific | Nuclei (StarDist/Mesmer-nuclear) + small constrained expansion | a poor membrane sum systematically under-segments types lacking a marker |
| Only nuclear/intracellular markers needed (TFs, Ki-67) | Nuclear segmentation, quantify directly | nuclear markers barely suffer lateral spillover -- sidesteps the boundary problem |
| Mesmer struggles on the tissue | Cellpose / `cpsam`, optionally retrain (Cellpose 2.0) | a panel-specific learned prior beats a wrong generalist prior |
| Legacy / no-GPU / need full transparency | ilastik -> CellProfiler watershed | the original Bodenmiller pipeline; fully tunable |
| Impossible co-expression appears after any path | re-tune and/or REDSEA before clustering | the rate is the headline under-segmentation/spillover metric |

## Whole-Cell Segmentation with Mesmer

**Goal:** Produce whole-cell instance masks for surface-marker phenotyping.

**Approach:** Stack nuclear and summed-membrane channels as `(batch, y, x, 2)` and pass the true acquisition resolution as `image_mpp`. Mesmer internally rescales to its training resolution, so the mpp is load-bearing, not cosmetic.

```python
import numpy as np
from deepcell.applications import Mesmer

nuclear = img[dna_idx]                       # DNA/Ir channel
membrane = build_membrane(img, membrane_idx) # broadly-expressed membrane sum (see below)
stack = np.stack([nuclear, membrane], axis=-1)[np.newaxis, ...]  # (1, y, x, 2)

app = Mesmer()
masks = app.predict(stack, image_mpp=1.0, compartment='whole-cell')[0, ..., 0]  # ~1.0 for IMC
```

## Build the Summed Membrane Channel

**Goal:** Construct channel 2 so whole-cell masks are not biased against cell types lacking a marker.

**Approach:** Sum BROADLY-expressed membrane markers chosen to cover every cell type present (not only the types of interest), because a cell-type-specific sum is bright on some types and dark on others, systematically under-segmenting the dark ones.

```python
def build_membrane(img, membrane_idx):
    # sum pan-membrane markers covering ALL populations (e.g. pan-cytokeratin for
    # epithelium, CD45 for immune, E-cadherin, Na/K-ATPase) -- inspect the result
    # before trusting whole-cell masks; a patchy sum collapses into nuclear-like masks
    return img[membrane_idx].sum(axis=0)
```

## Orchestrate via steinbock

```bash
# Mesmer/DeepCell (nuclear-first); membrane channels are aggregated per the panel column
steinbock segment deepcell --minmax -o masks

# Cellpose container (current default model is cpsam; channel order is reversed vs native)
steinbock segment cellpose --minmax -o masks

# aggregate per-cell mean intensities (mean is the default and the right phenotyping choice)
steinbock measure intensities -o intensities
```

## Nuclear Segmentation with Constrained Expansion (fallback)

**Goal:** Approximate whole cells when membrane staining is absent, without the bias of free dilation.

**Approach:** Segment nuclei, then expand with a small radius under a competitive/watershed constraint so pixels are owned by exactly one cell. Fixed isotropic dilation is a cell-type-correlated bias (under-captures macrophages, over-captures small cells) and free dilation double-counts boundary pixels into two masks.

```python
from skimage.segmentation import expand_labels, watershed

# expand_labels grows each label into background but stops at the midline between
# labels (no overlap), so each pixel is assigned once -- a partition, unlike free dilation
expanded = expand_labels(nuclear_masks, distance=3)   # ~3 px at 1 um; report the radius
assert expanded.max() == nuclear_masks.max()          # no cells created/destroyed
```

## Per-Tool Failure Modes

### Mesmer -- wrong image_mpp
**Trigger:** leaving the default mpp on 1 um IMC. **Mechanism:** Mesmer rescales the image to its ~0.5 um training resolution; a wrong mpp rescales cells to the wrong learned size. **Symptom:** systematic over/under-segmentation across the whole image. **Fix:** pass `image_mpp` = true acquisition resolution (~1.0 IMC, ~0.5 or finer MIBI).

### Cellpose -- auto-diameter on tiny cells
**Trigger:** auto-diameter on ~5-px IMC nuclei. **Mechanism:** `cyto` rescales to a 30-px target; at single-digit diameters the rescale factor is large and unstable. **Symptom:** merged or fragmented masks. **Fix:** set `diameter` from known cell size in pixels, or use `cpsam` (no diameter dependence).

### Generalist model -- wrong size prior
**Trigger:** default Cellpose `cyto`/`cyto3` on IMC, trusted blindly. **Mechanism:** at ~5 px of evidence the learned PRIOR, not the image, draws the boundary, and a non-IMC prior is wrong. **Symptom:** plausible-looking but systematically biased masks. **Fix:** prefer Mesmer (TissueNet includes IMC/MIBI) or fine-tune Cellpose on the panel; evaluate on downstream proxies.

### Channel compensation in the wrong order
**Trigger:** REDSEA before segmentation, or channel compensation after aggregation. **Mechanism:** channel spillover is pixel-level (must be corrected before the per-cell average); lateral spillover is defined on segmented neighbors (must be corrected after). **Symptom:** residual impossible co-expression. **Fix:** pixel-compensate -> segment -> aggregate -> REDSEA.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| `image_mpp` ~= 1.0 (IMC) | Greenwald 2022; Mesmer `model_mpp` ~0.5 | match acquisition resolution to the rescaler |
| Cellpose `cyto` 30 px / `nuclei` 17 px | Stringer 2021 | the trained-diameter targets the model rescales to |
| Nuclear expansion ~3 px @ 1 um | ImcSegmentationPipeline convention | approximates a thin cytoplasm without crossing into neighbors |
| Lymphocyte ~5-7 px @ 1 um/px | Giesen 2014 | the resolution floor that makes size priors load-bearing |
| Impossible-co-expression rate | Bai 2021 | per-slide under-segmentation/lateral-spillover monitor; not an F1 substitute |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| CD3+CD68+ "hybrid" cluster | under-segmentation or lateral spillover | treat as QC failure; re-tune + REDSEA before clustering |
| Whole-cell masks collapse to nuclei | weak/patchy summed membrane channel | broaden the membrane sum or fall back to nuclei + expansion |
| Same pixel counted in two cells | free dilation expansion | use `expand_labels`/watershed (exclusive ownership); assert label count unchanged |
| Macrophages under-captured | fixed isotropic nuclear dilation | constrained expansion; accept and report the bias; don't cross-compare with whole-cell data |
| Native Cellpose channel args do nothing in steinbock | steinbock reverses channel order | configure channels via the steinbock panel column, not native `--chan` semantics |
| High IoU but wrong biology | optimizing a pixel-overlap metric | accept on downstream proxies (impossible-co-expression rate, count/density sanity, positive-fraction stability); audit dense regions |

## References

- Giesen C, Wang HAO, Schapiro D, et al. 2014. Highly multiplexed imaging of tumor tissues with subcellular resolution by mass cytometry. *Nat Methods* 11(4):417-422. — IMC ~1 um resolution floor.
- Berg S, Kutra D, Kroeger T, et al. 2019. ilastik: interactive machine learning for (bio)image analysis. *Nat Methods* 16(12):1226-1232. — pixel classification stage.
- McQuin C, Goodman A, Chernyshev V, et al. 2018. CellProfiler 3.0: Next-generation image processing for biology. *PLoS Biol* 16(7):e2005970. — watershed instance segmentation.
- Schmidt U, Weigert M, Broaddus C, Myers G. 2018. Cell Detection with Star-Convex Polygons. *MICCAI 2018*, LNCS 11071:265-273. — StarDist nuclear baseline.
- Stringer C, Wang T, Michaelos M, Pachitariu M. 2021. Cellpose: a generalist algorithm for cellular segmentation. *Nat Methods* 18(1):100-106. — Cellpose diameters.
- Pachitariu M, Rariden M, Stringer C. 2025. Cellpose-SAM: superhuman generalization for cellular segmentation. *bioRxiv* doi:10.1101/2025.04.28.651001. — the cpsam SAM-backbone model (preprint).
- Greenwald NF, Miller G, Moen E, et al. 2022. Whole-cell segmentation of tissue images with human-level performance using large-scale data annotation and deep learning. *Nat Biotechnol* 40(4):555-565. — Mesmer/DeepCell, TissueNet, image_mpp.
- Bai Y, Zhu B, Rovira-Clave X, et al. 2021. Adjacent Cell Marker Lateral Spillover Compensation and Reinforcement for Multiplexed Images. *Front Immunol* 12:652631. — REDSEA boundary compensation; lateral spillover signature.
- Windhager J, Zanotelli VRT, Schulz D, et al. 2023. An end-to-end workflow for multiplexed image processing and analysis. *Nat Protoc* 18(11):3565-3613. — steinbock segmentation/measurement.

## Related Skills

- data-preprocessing - channel spillover compensation precedes segmentation
- phenotyping - consumes the single-cell mask and intensities; double-positives diagnose segmentation
- spatial-analysis - over-segmentation corrupts neighborhood statistics
- quality-metrics - segmentation QC metrics and the impossible-co-expression monitor
- interactive-annotation - overlay masks on channels to audit boundaries
<!-- END FILE: imaging-mass-cytometry/cell-segmentation/SKILL.md -->

## 子目录：imaging-mass-cytometry/data-preprocessing

<!-- BEGIN FILE: imaging-mass-cytometry/data-preprocessing/SKILL.md -->
---
name: bio-imaging-mass-cytometry-data-preprocessing
description: Load and preprocess imaging mass cytometry (IMC) and MIBI data from raw MCD/TXT through hot-pixel removal, spillover compensation, and variance-stabilizing transformation, covering readimc/steinbock ingestion, NNLS spillover compensation (CATALYST), IMC-Denoise, and the IMC arcsinh-cofactor question. Use when starting analysis from raw MCD files, building per-channel TIFF stacks, compensating channel spillover, choosing an arcsinh cofactor, or preparing single-cell intensities for phenotyping.
tool_type: mixed
primary_tool: steinbock
---

## Version Compatibility

Reference examples tested with: steinbock 0.16+, readimc 0.7+, numpy 1.26+, CATALYST 1.28+ (R/Bioconductor), cytomapper 1.16+ (R)

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

Notes specific to this skill: IMC pixels are integer ion COUNTS, not fluorescence intensities. `CATALYST::compCytof` defaults to `method='nnls'` (non-negativity preserved); pass `cofactor=1` explicitly for IMC single-cell means (the compCytof default is `NULL`/5, the suspension value). The spillover-matrix and SCE channel names must both be `(metal)(mass)Di` (e.g. `Sm152Di`) or compensation silently no-ops. steinbock's hot-pixel filter is `steinbock preprocess imc images --hpf 50` (a signed 8-neighbor difference, not a median filter).

# IMC Data Preprocessing

**"Preprocess my imaging mass cytometry data"** -> Ingest raw acquisitions, suppress acquisition noise, compensate channel spillover, and variance-stabilize counts so each cell's measured intensity reflects real antigen abundance.
- Python/CLI: `readimc.MCDFile`, `steinbock preprocess imc images --hpf 50`
- R: `CATALYST::compCytof`, `cytomapper::compImage` for spillover compensation

## The Single Most Important Modern Insight -- IMC pixels are ion counts, and non-negativity is physics, not a preference

Every IMC/MIBI pixel is an integer number of detected metal ions from one ~1 um laser shot, drawn from a low-count, zero-inflated, near-Poisson regime where most pixels read 0-2 counts and the limit of detection is ~6 counts. Four consequences govern every preprocessing decision, and importing fluorescence-microscopy habits violates all four. (1) There is no continuous Gaussian background to subtract -- the floor is a count floor, and a true-negative pixel still reads 1-2 counts by Poisson chance. (2) Negative values are physically meaningless, so flow-style spillover compensation (exact matrix inverse) is wrong because it manufactures negatives; non-negative least squares (NNLS) is mandatory (Chevrier 2018 *Cell Syst* 6:612). (3) Per-pixel "expression" is mostly shot noise -- signal emerges only after segmentation sums a cell's pixels, so pixel maps are for localization and QC, never quantification. (4) Spillover is SPATIAL: a bright cell bleeding into a neighboring mass channel contaminates adjacent pixels, fabricating co-localization and false marker positivity at cell borders -- which means uncompensated spillover manufactures the exact cell-cell interactions IMC exists to measure. The corollary that trips up suspension-CyTOF veterans: the arcsinh cofactor is NOT 5 (cofactor 1 is the modern IMC default, Hunter 2024 *Cytometry A* 105:36), and there are no in-stream calibration beads in ablated tissue.

## Preprocessing Pipeline Order (load-bearing)

```
read .mcd (readimc) -> panel filter+sort (keep column) -> hot-pixel removal (DIMR or --hpf 50)
  -> [optional] DeepSNiF on low-SNR channels only -> spillover compensation (NNLS)
  -> segmentation (on compensated nuclear/membrane channels) -> per-cell aggregation
  -> arcsinh(cofactor 1) -> z-score / cohort-anchored normalization
```

Order is not cosmetic: denoise operates on RAW counts (the Poisson noise model is defined there), compensate BEFORE segmentation when spatial fidelity matters (corrupted membrane channels yield wrong boundaries that no later step recovers), and transform/normalize LAST.

## Denoising Taxonomy

| Method | Targets | Risk | When to use | Fails when |
|--------|---------|------|-------------|------------|
| steinbock `--hpf 50` | hot pixels | low | default fast hot-pixel pass | absolute-count threshold over-clips bright channels, under-cleans dim ones |
| IMC-Denoise DIMR (Lu 2023) | hot pixels | low | self-calibrating hot-pixel removal | misclassifies large multi-pixel hot-pixel clusters as signal |
| IMC-Denoise DeepSNiF (Lu 2023) | shot noise | HIGH | only channels with mean positive intensity < ~7 | over-smooths sparse/punctate markers and sub-1-2 um structure; biases extreme-low-count regions |
| 3x3 median filter | (do not use) | severe | never | returns 0 for isolated real single-positive pixels -- erases sparse biology |

## Decision Tree by Scenario

| Scenario | Recommended | Why |
|----------|-------------|-----|
| Single-stain QC shows >~2% off-target spillover at relevant masses | Compensate (NNLS) before phenotyping | leak corrupts type calls and (spatially) neighborhood stats |
| Spatial neighborhood / interaction analysis is the endpoint | Pixel-level compensation (`compImage`) before segmentation | spillover is spatial and fakes interactions; cell-mean compensation comes too late |
| Means-only phenotyping, segmentation channels uncontaminated | Cell-level `compCytof` on SCE means | cheaper, less per-pixel Poisson noise |
| Channel driven above ~5,000 dual counts | Re-titrate at acquisition; do not compensate | linearity (and thus the matrix) breaks above saturation |
| Panel pre-designed to avoid bright/dim mass adjacencies, QC near-clean | Compensation ~ identity; skipping is defensible | avoids NNLS noise on near-zero pixels |
| Channel mean positive intensity < ~7, cannot phenotype on it | DIMR + DeepSNiF | shot noise dominates; denoising is the only way to use it |
| Channel clean, or punctate, or the one segmentation runs on | DIMR / `--hpf` only; skip DeepSNiF | DeepSNiF over-smooths real isolated signal and blurs boundaries |

## Read Raw Acquisitions

**Goal:** Ingest the multi-ROI MCD (the canonical source) and keep the metal-to-target panel mapping intact.

**Approach:** Open the MCD with readimc, iterate slides and acquisitions, and carry both `channel_names` (metals) and `channel_labels` (targets) -- conflating them is the most common ingestion bug. Prefer MCD over TXT (one ROI per file, and absent on Hyperion XTi).

```python
from readimc import MCDFile

with MCDFile('slide.mcd') as f:
    slide = f.slides[0]
    for acq in slide.acquisitions:
        img = f.read_acquisition(acq)              # (channels, y, x) float32 ion counts
        metals = acq.channel_names                 # e.g. 'Sm152' -- the mass channel
        targets = acq.channel_labels               # e.g. 'CD3'  -- the antibody target
        print(acq.id, img.shape, dict(zip(metals, targets)))
```

## Extract and Hot-Pixel Filter with steinbock

**Goal:** Build per-channel TIFF stacks, filtered to the analysis panel and de-spiked.

**Approach:** The panel CSV is both a filter and a sort key -- only `keep==1` rows are written and their row order defines channel order in the stack, so it must be pinned as a versioned artifact. The `--hpf` filter compares each pixel to its 8 neighbors with a signed difference and replaces spikes with the neighbor maximum (a conservative, valley-preserving operation), not a median.

```bash
# generate the panel template (edit the keep column before extracting)
steinbock preprocess imc panel

# extract TIFFs (keep-filtered, panel-ordered) with hot-pixel removal; 50 is a count
# difference, not a universal constant -- raise it for high-dynamic-range markers
steinbock preprocess imc images --hpf 50
```

## Spillover Compensation (NNLS)

**Goal:** Remove channel crosstalk (oxide M+16, abundance-sensitivity M+-1, isotopic impurity) without introducing negative counts.

**Approach:** Estimate the spillover matrix from single-stain controls per positive EVENT then take the median (population-summary estimation overcompensates because IMC's zero background biases ratios), then apply NNLS. Compensate pixels (`compImage`) before segmentation for spatial work, or cell means (`compCytof`) after segmentation otherwise. Channel names must be `(metal)(mass)Di`.

```r
library(CATALYST)
library(imcRtools)

# estimate the matrix from spotted single-stain TXTs (filenames carry the metal)
sce <- readSCEfromTXT('spillover/')
sce <- prepData(sce, transform = TRUE, cofactor = 5)   # cofactor 5 for PIXEL spot data
sce <- assignPrelim(sce); sce <- estCutoffs(sce); sce <- applyCutoffs(sce)
sm  <- computeSpillmat(sce)                            # the spillover matrix

# cell-level compensation on segmented single-cell means (NNLS is the default)
sce_cells <- compCytof(sce_cells, sm, method = 'nnls', cofactor = 1, overwrite = FALSE)
```

```r
# OR pixel-level compensation on the image stack, before segmentation (spatial fidelity)
library(cytomapper)
images <- compImage(images, adaptSpillmat(sm, channelNames(images)))
```

## Transform and Normalize

**Goal:** Variance-stabilize counts and remove batch offset without destroying cross-sample comparability.

**Approach:** Apply arcsinh with cofactor 1 on single-cell means (the OPTIMAL-derived IMC default, not the suspension-CyTOF 5), then z-score per channel against cohort-wide statistics. Per-image percentile or min-max scaling is a one-way door that makes equal biology look unequal across samples -- reserve it for visualization and always retain raw/compensated counts.

```python
import numpy as np

def arcsinh_cofactor1(cell_means):
    # cofactor 1 for IMC single-cell means (Hunter 2024); state the cofactor explicitly --
    # no field-wide standard exists, so reproducibility requires reporting it
    return np.arcsinh(cell_means / 1.0)

def zscore_per_channel(expr, mean, std):
    # mean/std computed COHORT-WIDE (not per-image) so scales stay comparable across samples
    return (expr - mean) / std
```

## Per-Method Failure Modes

### Flow-style compensation -- negative counts
**Trigger:** exact matrix inversion (`method='flow'` or generic linear unmixing). **Mechanism:** the inverse violates non-negativity and produces negative ion counts. **Symptom:** negative compensated values, downstream stats corrupted. **Fix:** `compCytof(..., method='nnls')` (the default); negatives are a solver artifact, not evidence compensation is wrong.

### Channel-name mismatch -- silent no-op
**Trigger:** SCE channel names are `Sm152` but the spillover matrix uses `Sm152Di` (or vice versa). **Mechanism:** name-based mapping finds no match. **Symptom:** compensation runs without error but changes nothing. **Fix:** enforce `(metal)(mass)Di`; reconcile with `adaptSpillmat()`.

### DeepSNiF on every channel -- invented structure
**Trigger:** blanket denoising "to clean things up." **Mechanism:** the Hessian continuity prior imposes spatial smoothness on genuinely sparse/punctate markers. **Symptom:** rare-population or punctate signal blurred into neighbors; biased low-count regions. **Fix:** denoise only channels with mean positive intensity < ~7; validate against the un-denoised image; never denoise the segmentation channel without checking boundary integrity.

### Per-image normalization before cross-sample comparison
**Trigger:** independent per-image 99th-percentile or min-max scaling, then comparing samples. **Mechanism:** image A's 99th percentile (40 counts) and image B's (400 counts) map to the same [0,1]. **Symptom:** a dim positive in A reads like a bright positive in B; differential abundance is spurious. **Fix:** derive normalization from cohort-wide statistics or a shared anchor; keep raw counts to re-derive.

### Median filtering as a denoiser
**Trigger:** `ndimage.median_filter` on the count image. **Mechanism:** a 3x3 median over sparse single-positive pixels returns 0. **Symptom:** real isolated membrane/punctate signal erased. **Fix:** use the neighbor-spike filter (`--hpf`) or DIMR; never blanket-median IMC.

### MIBI data run through the IMC pipeline unchanged
**Trigger:** applying this steinbock/CATALYST flow to MIBI-TOF data as if it were IMC. **Mechanism:** MIBI is SIMS on Au/Ta conductive slides, so it carries a 197Au slide background and crosstalk classes the CATALYST single-stain-bead model does not target. **Symptom:** gold-background contamination and uncorrected MIBI crosstalk. **Fix:** remove the Au/native-background channels and run MAUI (Baranski 2021) before this pipeline; treat the CATALYST spillover step as IMC-specific.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| arcsinh cofactor 1 (single-cell means) | Hunter 2024 *Cytometry A* 105:36 | maximizes positive/negative separation (Fisher ratio) for IMC counts; 5 over-compresses |
| arcsinh cofactor 5 (pixel/spot data) | CATALYST IMC workflow | pixel spot counts are higher-scale than cell means |
| Linearity ceiling ~5,000 dual counts | Chevrier 2018 *Cell Syst* 6:612 | above it count->abundance bends and the spillover matrix is invalid |
| `--hpf 50` (count difference) | steinbock convention | a per-experiment heuristic, not a universal constant -- tune to dynamic range |
| DeepSNiF only if mean positive intensity < ~7 | Lu 2023 *Nat Commun* 14:1601 | above ~7 the channel is effectively noise-immune; denoising is pure risk |
| Detection limit ~6 ion counts | Lu 2023 *Nat Commun* 14:1601 | below this, signal and shot noise are indistinguishable per pixel |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| `compCytof` runs but values unchanged | channel-name format mismatch | enforce `Sm152Di`; `adaptSpillmat()` |
| Negative compensated counts | flow-style inversion | use `method='nnls'` |
| "Channel 12 is a different antibody for collaborators" | panel keep/order changed after segmentation | pin `panel.csv` as a versioned artifact; never reorder post-segmentation |
| Rare population vanished after denoising | DeepSNiF on a sparse channel | restrict DeepSNiF to low-SNR non-punctate channels |
| TXT loads only one ROI | analyzing TXT instead of MCD | ingest the multi-ROI `.mcd` with `readimc` |
| Cross-sample differences disappear or explode | per-image normalization | cohort-anchored normalization; keep raw counts |

## References

- Giesen C, Wang HAO, Schapiro D, et al. 2014. Highly multiplexed imaging of tumor tissues with subcellular resolution by mass cytometry. *Nat Methods* 11(4):417-422. — IMC ~1 um ion-count origin.
- Chevrier S, Crowell HL, Zanotelli VRT, Engler S, Robinson MD, Bodenmiller B. 2018. Compensation of Signal Spillover in Suspension and Imaging Mass Cytometry. *Cell Syst* 6(5):612-620.e5. — three spillover sources, single-stain beads, NNLS, ~5,000 dual-count linearity, CATALYST.
- Lu P, Oetjen KA, Bender DE, et al. 2023. IMC-Denoise: a content aware denoising pipeline to enhance Imaging Mass Cytometry. *Nat Commun* 14:1601. — DIMR hot-pixel and DeepSNiF shot-noise removal; mean>7 noise-immune guide.
- Windhager J, Zanotelli VRT, Schulz D, et al. 2023. An end-to-end workflow for multiplexed image processing and analysis. *Nat Protoc* 18(11):3565-3613. — the steinbock workflow and readimc/imcRtools ingestion.
- Hunter B, Nicorescu I, Foster E, et al. 2024. OPTIMAL: An OPTimized Imaging Mass cytometry AnaLysis framework for benchmarking segmentation and data exploration. *Cytometry A* 105(1):36-53. — arcsinh cofactor 1 and z-score-after-arcsinh for IMC.
- Baranski A, Milo I, Greenbaum S, et al. 2021. MAUI (MBI Analysis User Interface): An image processing pipeline for Multiplexed Mass Based Imaging. *PLoS Comput Biol* 17(4):e1008887. — MIBI-specific crosstalk, aggregate, and gold-background removal.

## Related Skills

- quality-metrics - reading the spillover matrix and gating channels before compensation
- cell-segmentation - segmentation runs on compensated nuclear/membrane channels
- phenotyping - consumes the arcsinh-transformed single-cell matrix
- flow-cytometry/compensation-transformation - suspension spillover and arcsinh background
- single-cell/preprocessing - AnnData conventions for the single-cell matrix
<!-- END FILE: imaging-mass-cytometry/data-preprocessing/SKILL.md -->

## 子目录：imaging-mass-cytometry/differential-analysis

<!-- BEGIN FILE: imaging-mass-cytometry/differential-analysis/SKILL.md -->
---
name: bio-imaging-mass-cytometry-differential-analysis
description: Compare cell-type composition and spatial features across conditions in IMC/MIBI cohorts with the patient as the experimental unit, covering pseudoreplication, per-patient aggregation, mixed models, compositional (Dirichlet/scCODA) differential abundance, diffcyt, per-image-to-patient spatial differential testing (SpaceANOVA), batch covariates, and FDR. Use when testing whether a cell type or spatial niche differs between groups, avoiding cell-level pseudoreplication, choosing a differential-abundance method, or correctly powering an IMC cohort comparison.
tool_type: mixed
primary_tool: diffcyt
---

## Version Compatibility

Reference examples tested with: diffcyt 1.22+ (R), lme4 1.1+ (R), statsmodels 0.14+, scanpy 1.10+, sccoda 0.1.9+, numpy 1.26+, pandas 2.2+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

Notes specific to this skill: cell-type proportions are compositional (they sum to 1), so a real increase in one type forces apparent decreases in others -- a Dirichlet/CLR-aware method (scCODA) or a reference cell type is needed, not independent per-type tests. statsmodels `mixedlm` fits patient as a random effect. diffcyt operates on per-sample cluster counts (DA) and per-sample median marker expression (DS).

# IMC Differential Analysis

**"Compare cell types and spatial structure between my conditions"** -> Aggregate to the patient, then test across patients -- never across cells.
- Python: `statsmodels.formula.api.mixedlm`, `sccoda`, `scanpy`
- R: `diffcyt`, `lme4::lmer`, SpaceANOVA for spatial differential testing

## The Single Most Important Modern Insight -- the replicate is the patient, not the cell, and the million-cell count is a red herring

After phenotyping and spatial analysis, every interesting claim ("disease has more Tregs", "responders have more CD8-tumor contact") is a comparison BETWEEN groups, and the single most common fatal error is testing it at the cell level. Hundreds of thousands of cells from one patient are not independent replicates -- they are correlated reads of one biological sample, and cells within an image are massively spatially autocorrelated. Testing at the cell level inflates n by orders of magnitude and manufactures significance: a per-cell test over 50,000 cells reports p~0 for trivial effects because the effective sample size is the number of PATIENTS (often 10-40), not cells (Squair 2021 *Nat Commun* 12:5692). In imaging this is worse than in scRNA because slide and ROI add nesting levels and ROIs are not random samples of the tissue. The correct spine is invariant across every differential question: compute a per-image (or per-ROI) summary, aggregate to ONE value per patient, then test across patients with the patient as the unit -- a mixed model with patient as a random effect (image nested within patient), a pseudobulk-style per-patient summary, or a cell-count-weighted average of per-image statistics (Samorodnitsky and Wu 2024 *Brief Bioinform* 25:bbae522). Two riders complete the picture: cell-type proportions are COMPOSITIONAL (they are constrained to sum to 1, so a real rise in one type mechanically depresses the others, and independent per-type tests double-count this), and acquisition BATCH drifts by day/run and can align with clinical group, so batch must be a covariate and acquisition order randomized against condition. Phenotyping-method choice and statistical-unit choice are orthogonal: getting the cell types right does not excuse testing them wrong.

## Differential Question Taxonomy

| Question | Per-image summary | Patient-level test |
|----------|-------------------|--------------------|
| Cell-type abundance differs between groups | per-image cell-type proportions | mixed model on proportions; scCODA (compositional); diffcyt-DA |
| A functional/state marker differs within a type | per-image median marker per type | pseudobulk per patient + limma/edgeR; diffcyt-DS |
| A spatial interaction/niche differs between groups | per-image enrichment z / Ripley's K / CN abundance | mixed model / cell-count-weighted; SpaceANOVA (FANOVA on cross-K) |

## Decision Tree by Scenario

| Scenario | Recommended | Why |
|----------|-------------|-----|
| Compare cell-type proportions, several types shift | scCODA (or CLR + mixed model) | handles the compositional constraint and the reference-type problem |
| Standard cytometry-style DA on clusters | diffcyt-DA (edgeR on per-sample counts) | designed for per-sample cluster counts; established |
| Multiple ROIs per patient | mixed model, patient random effect (image nested) | respects nesting; or cell-count-weighted aggregate |
| Few patients (n < ~10) | simple per-patient test; report low power honestly | do NOT rescue power with cell count |
| Differential functional-marker expression within a type | pseudobulk per patient + limma/edgeR (diffcyt-DS) | aggregates out cell-level pseudoreplication |
| Spatial interaction/niche across groups | per-image spatial stat -> patient aggregate; SpaceANOVA | the spatial statistic is the summary; the unit is still the patient |
| Acquisition batch aligns with group | include batch covariate; if confounded, the contrast is unrescuable | randomize acquisition order against condition |

## Aggregate to the Patient (the spine)

**Goal:** Collapse millions of cells to one summary per patient before any test.

**Approach:** Compute per-image cell-type proportions, then aggregate images to their patient. Every downstream test consumes this patient-level table, not the cell table.

```python
import pandas as pd

# obs has one row per cell with image_id, patient, condition, cell_type
counts = obs.groupby(['patient', 'condition', 'image_id', 'cell_type']).size().unstack(fill_value=0)
image_prop = counts.div(counts.sum(axis=1), axis=0)            # per-image proportions
patient_prop = image_prop.groupby(['patient', 'condition']).mean()   # one row per patient
```

## Differential Abundance with a Mixed Model

**Goal:** Test a cell type's proportion across groups while respecting patient/ROI nesting.

**Approach:** Fit a mixed model with patient as a random effect when multiple ROIs per patient exist; this absorbs within-patient correlation that a fixed-effect test would treat as independent replication.

```python
import statsmodels.formula.api as smf

# one row per image; proportion of the target type; patient random intercept
df = image_prop.reset_index().rename(columns={'Treg': 'prop'})   # 'Treg' = an actual cell_type column
model = smf.mixedlm('prop ~ condition + batch', df, groups=df['patient'])   # batch as covariate
res = model.fit()
print(res.summary())   # the condition coefficient is tested with patient as the unit
```

## Compositional Differential Abundance (scCODA)

**Goal:** Avoid the false "everything changed" artifact when proportions are constrained to sum to 1.

**Approach:** Model the counts as compositional against a reference cell type; a change is interpreted relative to that reference rather than as an independent per-type shift.

```python
import sccoda.util.cell_composition_data as dat
from sccoda.util import comp_ana as mod

# patient-level cell-type COUNTS (not proportions); pick a biologically stable reference type
data = dat.from_pandas(patient_counts, covariate_columns=['condition'])
analysis = mod.CompositionalAnalysis(data, formula='condition', reference_cell_type='Epithelial')
result = analysis.sample_hmc()
result.summary()
```

## Differential Spatial Feature

**Goal:** Test whether a spatial interaction or niche differs between groups, at the patient unit.

**Approach:** Treat the per-image spatial statistic (a neighborhood-enrichment z, a Ripley's cross-K curve, a CN abundance) as the summary, aggregate to patient, and test across patients with FDR over cell-type pairs. SpaceANOVA does this as a functional ANOVA on per-image cross-K with subject structure.

```python
import statsmodels.formula.api as smf
from statsmodels.stats.multitest import multipletests

# per_image_pair: rows = (image_id, patient, condition, batch, enrichment_z) for ONE type pair
pvals = {}
for pair, sub in per_image_pair.groupby('pair'):
    res = smf.mixedlm('enrichment_z ~ condition + batch', sub, groups=sub['patient']).fit()
    pvals[pair] = res.pvalues['condition[T.responder]']
padj = dict(zip(pvals, multipletests(list(pvals.values()), method='fdr_bh')[1]))   # FDR across pairs
```

## Differential State Within a Type

**Goal:** Test whether a functional/state marker (Ki67, PD-1) differs within a cell type between groups.

**Approach:** Pseudobulk to one value per patient per cell type (median marker expression among that type's cells), then test across patients. diffcyt-DS (R) formalizes this on per-sample medians; the Python pseudobulk path is below.

```python
import numpy as np

t = adata[adata.obs['cell_type'] == 'T cell']
ki67 = t[:, 'Ki67'].X
ki67 = ki67.toarray().ravel() if hasattr(ki67, 'toarray') else np.asarray(ki67).ravel()
pb = t.obs.assign(ki67=ki67).groupby(['patient', 'condition'])['ki67'].median().reset_index()
print(smf.ols('ki67 ~ condition', pb).fit().pvalues['condition[T.responder]'])   # one value per patient
```

## Per-Method Failure Modes

### Cell-level testing
**Trigger:** a t-test/Wilcoxon/regression over individual cells. **Mechanism:** correlated cells from one sample are pseudoreplicates; effective n is the patient count. **Symptom:** p~0 for trivial effects; "significant" findings that do not replicate. **Fix:** aggregate to per-patient summaries; test across patients.

### Independent per-type proportion tests
**Trigger:** a separate test per cell type on proportions. **Mechanism:** proportions sum to 1, so a real rise in one type depresses others mechanically. **Symptom:** many types appear to change in opposite directions. **Fix:** compositional model (scCODA) or CLR transform with a reference type.

### Over-correcting batch
**Trigger:** aggressive integration to make clusters patient-agnostic, then testing on corrected data. **Mechanism:** correction can treat real between-patient biology as batch. **Symptom:** the disease signal disappears. **Fix:** correct minimally, validate that invariant types align while variable types stay separate, and keep integration out of the across-patient inference path.

### Rescuing power with cell count
**Trigger:** claiming significance from n=4 patients because millions of cells were imaged. **Mechanism:** cell count is not replication. **Symptom:** confident claims from few patients. **Fix:** report the patient n and the true power honestly; collect more patients.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| Unit of replication = patient count (often 10-40) | Squair 2021 *Nat Commun* 12:5692 | cells/ROIs are pseudoreplicates |
| Cell-count-weighted per-image aggregation | Samorodnitsky and Wu 2024 *Brief Bioinform* 25:bbae522 | controls type-I error with high power (vs unweighted ROI averaging) |
| Reference cell type for compositional DA | Buttner 2021 *Nat Commun* 12:6876 | proportions are not independent |
| BH-FDR across cell-type pairs and radii | multiplicity | ~200 pairs x radii guarantees false positives |
| Batch covariate; randomize acquisition order | spatial dossier | run drift can align with clinical group |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| p~0 with a trivial effect | cell-level test | per-patient aggregation; mixed model |
| All cell types "changed" | compositional constraint ignored | scCODA / CLR with reference type |
| Disease signal vanished after integration | batch over-correction | minimal correction; keep it out of the test |
| Significant with n=4 patients | power rescued by cell count | report patient n; do not over-claim |
| Many significant pairs | no FDR across pairs/radii | BH-FDR over the full grid |

## References

- Squair JW, Gautier M, Kathe C, et al. 2021. Confronting false discoveries in single-cell differential expression. *Nat Commun* 12:5692. — pseudoreplication; aggregate to sample.
- Samorodnitsky S, Wu MC. 2024. Statistical analysis of multiple regions-of-interest in multiplexed spatial proteomics data. *Brief Bioinform* 25(6):bbae522. — ROI aggregation, cell-count-weighted averaging, SPOT omnibus.
- Seal S, Neelon B, Angel PM, et al. 2024. SpaceANOVA: Spatial Co-occurrence Analysis of Cell Types in Multiplex Imaging Data Using Point Process and Functional ANOVA. *J Proteome Res* 23(4):1131-1143. — FANOVA on per-image cross-K with subject structure.
- Weber LM, Nowicka M, Soneson C, Robinson MD. 2019. diffcyt: Differential discovery in high-dimensional cytometry via high-resolution clustering. *Commun Biol* 2:183. — diffcyt-DA/DS.
- Buttner M, Ostner J, Muller CL, Theis FJ, Schubert B. 2021. scCODA is a Bayesian model for compositional single-cell data analysis. *Nat Commun* 12:6876. — compositional differential abundance.
- Schurch CM, Bhate SS, Barlow GL, et al. 2020. Coordinated Cellular Neighborhoods Orchestrate Antitumoral Immunity at the Colorectal Cancer Invasive Front. *Cell* 182(5):1341-1359.e19. — cellular neighborhoods compared across patients.

## Related Skills

- phenotyping - supplies the cell-type labels whose proportions are compared
- spatial-analysis - supplies the per-image spatial statistics that become patient-level summaries
- quality-metrics - batch must be diagnosed and entered as a covariate
- experimental-design/randomization-blocking - the experimental-unit and pseudoreplication foundation
- clinical-biostatistics/subgroup-analysis - multiplicity and effect estimation in clinical cohorts
- flow-cytometry/differential-analysis - diffcyt-DA/DS for suspension cytometry
<!-- END FILE: imaging-mass-cytometry/differential-analysis/SKILL.md -->

## 子目录：imaging-mass-cytometry/interactive-annotation

<!-- BEGIN FILE: imaging-mass-cytometry/interactive-annotation/SKILL.md -->
---
name: bio-imaging-mass-cytometry-interactive-annotation
description: Interactive cell annotation and image QC for IMC/MIBI using napari, napari-imc, Mantis Viewer, and cytomapper, covering the pixels-to-cell-table bridge, overlaying masks to catch segmentation/spillover artifacts, inter-annotator variability as the accuracy ceiling, contrast-as-threshold, and building class-balanced ground-truth label sets. Use when manually labeling cells, generating training data for a classifier, QC-ing segmentation on the image, confirming clusters are spatially real, or choosing an annotation viewer.
tool_type: python
primary_tool: napari
---

## Version Compatibility

Reference examples tested with: napari 0.4.18+, napari-imc 0.7+, numpy 1.26+, scikit-learn 1.4+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

Notes specific to this skill: core napari cannot open `.mcd` -- the `napari-imc` plugin reads raw Fluidigm/Standard BioTools files in machine coordinates. napari `add_labels` edits integer masks (segmentation QC); `add_points` with a `features` table holds per-cell categorical labels. Mantis Viewer is a standalone Electron app from CANDELbio/Parker Institute (NOT the Bodenmiller group). napari has no journal paper -- cite the Zenodo DOI.

# Interactive Annotation

**"Manually annotate cell types in my IMC data"** -> Look at the image with masks overlaid to label cells, generate ground truth, and catch the artifacts a cell table hides.
- Python: `napari.Viewer` with `napari-imc` (raw `.mcd`), `add_labels`/`add_points`
- R: `cytomapper::cytomapperShiny` (gate then see the gate on tissue)

## The Single Most Important Modern Insight -- annotation is the pixels-to-cell-table bridge, and the image vetoes the table

The IMC pipeline collapses a multi-GB pixel stack into a cell-by-marker table via a segmentation mask and mean-intensity extraction, and that table has thrown away three things only the image still contains: whether the mask boundary matches a real cell, where a marker's signal physically sits (its spillover provenance), and morphology/context. None of these surface as an outlier in the table -- a merged CD3+CD20+ "cell" looks like a plausible rare double-positive, not an error -- so the table is seductive precisely because it is tidy and statistical. Annotation is the only QC step that lets pixels veto the table. The expert habit is distrust of any cell-table claim (a cluster, a double-positive population, a rare type) until it has been seen on the image with its mask overlaid. Three concrete bridge operations follow: overlay the mask on the DNA + summed-membrane channels and walk the image (the irreplaceable segmentation QC); paint clusters back onto tissue, where a real cluster forms coherent structures (a tumor nest, a T-cell zone) and an artifact cluster scatters as salt-and-pepper haze along the boundary between two real clusters (spatial incoherence is the tell); and gate in image space, not only expression space, because a biaxial gate drawn on the table is a thresholding decision made blind to the pixels. Two hard limits frame all of it: manual labels are not ground truth (expert-vs-expert concordance is only ~86%, and a substantial share of disagreements reflect genuinely ambiguous cells, so chasing >90% classifier accuracy is chasing noise above human agreement), and the display contrast limit IS a positivity threshold, so auto-scaling per image silently moves what counts as "positive" field to field.

## Viewer Landscape

| Tool | Stack | What it is for |
|------|-------|----------------|
| napari + napari-imc | Python | open raw `.mcd`, overlay channels + masks + annotation layers, scriptable |
| napari-steinpose | napari plugin | human-in-the-loop Cellpose segmentation inside napari |
| Mantis Viewer | Electron (CANDELbio/Parker) | dedicated ground-truth label + region/population curation on huge images |
| cytomapper / cytomapperShiny | R/Bioconductor | gate on up to ~24 markers and see the gated cells painted on tissue |
| cytoviewer | R/Bioconductor | interactive image + mask overlay colored by cell metadata |
| TissUUmaps 3 | browser/WebGL | whole-slide QC of marker/point overlays at 10^7+ points |
| QuPath | Java | whole-slide pathology; map clusters/cells back to tissue for validation |

## Decision Tree by Scenario

| Task | Tool | Why |
|------|------|-----|
| Open and inspect a raw `.mcd` | napari + napari-imc | only it reads IMC in machine coordinates |
| Generate ground-truth labels for a classifier | Mantis Viewer or napari points | built for population curation across large images |
| Gate a population and confirm it on tissue | cytomapperShiny | the gate-then-see-on-tissue loop |
| Whole-slide point-overlay QC | TissUUmaps | scales to 10^7 points |
| Segmentation mask QC/edit | napari `add_labels` / napari-steinpose | paint/fill integer masks |
| Confirm a cluster is real | paint cluster back on tissue (any viewer) | spatial incoherence = artifact |

## Open Raw IMC and Overlay the Mask

**Goal:** Put the raw channels, the segmentation mask, and an annotation layer in one canvas.

**Approach:** Use napari-imc for the `.mcd`, overlay the mask outlines on DNA + a summed membrane channel, and add a labels or points layer for annotation. Fix the contrast limits explicitly so "positive" means the same thing across fields.

```python
import napari

viewer = napari.Viewer()
viewer.open('slide.mcd', plugin='napari-imc')          # reads acquisitions + panoramas
viewer.add_labels(cell_masks, name='masks')            # outlines to audit boundaries
# fix contrast (a display limit IS a positivity threshold) -- record it in the protocol
viewer.add_image(dna, name='DNA', contrast_limits=[0, 20], colormap='gray', blending='additive')
napari.run()
```

## Paint Clusters Back onto Tissue

**Goal:** Decide whether a data-driven cluster is real biology or an artifact.

**Approach:** Color the mask by cluster and look: a real cluster forms coherent spatial structures; an artifact cluster scatters along the boundary between two real clusters.

```python
import numpy as np

def cluster_label_image(masks, cell_ids, cluster_of_cell):
    # paint each cell's cluster id back onto its mask; view in napari and demand spatial
    # coherence (nests/zones/sheets). Salt-and-pepper haze along a boundary = artifact.
    out = np.zeros_like(masks)
    lut = dict(zip(cell_ids, cluster_of_cell))
    for cid, cl in lut.items():
        out[masks == cid] = cl + 1
    return out
```

## Build a Class-Balanced Ground-Truth Set

**Goal:** Produce a training set that learns rare types and generalizes across batches.

**Approach:** Tissue is wildly imbalanced (hundreds vs tens-of-thousands of cells per class), so deliberately over-sample rare types when choosing what to label, and spread annotation across multiple patients/compartments -- label breadth beats label depth. Aim for hundreds-to-low-thousands of confident cells per class.

```python
import numpy as np

def sample_cells_to_annotate(cell_ids, cell_types, per_class=300, rng=None):
    # over-sample rare classes toward a target count; annotating random fields lets rare
    # types stay unlearnably sparse
    rng = rng or np.random.default_rng(0)
    picks = []
    for ct in np.unique(cell_types):
        pool = cell_ids[cell_types == ct]
        picks.append(rng.choice(pool, size=min(per_class, len(pool)), replace=False))
    return np.concatenate(picks)
```

## Per-Trap Failure Modes

### Trusting a table double-positive
**Trigger:** a CD3+CD20+ population from the cell table. **Mechanism:** under-segmentation or lateral spillover makes a chimeric vector that looks like a plausible rare type. **Symptom:** a "novel doublet lineage". **Fix:** overlay mask + both channels on those exact cells; two abutting nuclei means a segmentation artifact.

### Per-image auto-contrast while annotating
**Trigger:** letting the viewer auto-scale each field. **Mechanism:** the contrast limit is a positivity threshold; auto-scaling moves it per field. **Symptom:** "positive" drifts image to image; inconsistent labels. **Fix:** fix and record contrast limits; apply the same transform to every annotator and image.

### Chasing >90% classifier accuracy
**Trigger:** treating manual labels as ground truth. **Mechanism:** expert-vs-expert concordance is ~86%, and many disagreements reflect genuinely ambiguous cells. **Symptom:** overfitting to one annotator's noise. **Fix:** use multi-annotator consensus for the evaluation set; report inter-annotator agreement as the ceiling.

### Annotating one ROI deeply
**Trigger:** labeling many cells in a single field. **Mechanism:** batch/staining variation between images is a top failure mode. **Symptom:** the classifier generalizes only to that ROI. **Fix:** spread annotation across patients/images and compartments; breadth over depth.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| Inter-annotator concordance ~86% | Amitay 2023 *Nat Commun* 14:4302 | the realistic accuracy ceiling; many disagreements are genuinely ambiguous |
| Hundreds-to-low-thousands confident cells/class | Amitay 2023; Shaban 2024 | enough to train; rare classes and inter-image variation bind, not total count |
| Over-sample rare classes + Poisson-resample augmentation | Amitay 2023 *Nat Commun* 14:4302 | tissue is imbalanced; signal is ion counts |
| Labels NOT harvested from clustering | annotation hygiene | clustering-derived labels re-import the double-positive artifact |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| `.mcd` will not open in napari | core napari has no IMC reader | install and use the `napari-imc` plugin |
| Annotation layer behaves unexpectedly | wrong layer type | `add_labels` for masks, `add_points` (with `features`) for per-cell labels |
| Cluster looks tight but is biologically odd | spillover/segmentation artifact | paint it on tissue; demand spatial coherence |
| Rare cell type unlearnable | random-field annotation | deliberately over-sample rare types; augment |
| Classifier plateaus below expectation | exceeding inter-annotator agreement | accept the ~86% ceiling; consensus-label the evaluation set |

## References

- napari contributors. 2019. napari: a multi-dimensional image viewer for Python. Zenodo. doi:10.5281/zenodo.3555620. — no journal paper exists; cite the Zenodo DOI.
- Amitay Y, Bussi Y, Feinstein B, Bagon S, Milo I, Keren L. 2023. CellSighter: a neural network to classify cells in highly multiplexed images. *Nat Commun* 14:4302. — inter-annotator concordance; ground-truth and augmentation.
- Shaban M, et al. 2024. MAPS: pathologist-level cell type annotation from tissue images through machine learning. *Nat Commun* 15:28. — annotation scale and class imbalance.
- Geuenich MJ, Hou J, Lee S, et al. 2021. Automated assignment of cell identity from single-cell multiplexed imaging and proteomic data. *Cell Syst* 12(12):1173-1186.e5. — marker-prior labels as expert annotation.
- Bankhead P, Loughrey MB, Fernandez JA, et al. 2017. QuPath: Open source software for digital pathology image analysis. *Sci Rep* 7:16878. — whole-slide validation.
- Pielawski N, Andersson A, Avenel C, et al. 2023. TissUUmaps 3: Improvements in interactive visualization, exploration, and quality assessment of large-scale spatial omics data. *Heliyon* 9(5):e15306. — whole-slide point QC.
- Chevrier S, Crowell HL, Zanotelli VRT, et al. 2018. Compensation of Signal Spillover in Suspension and Imaging Mass Cytometry. *Cell Syst* 6(5):612-620.e5. — channel spillover (distinct from lateral spillover caught visually).

## Related Skills

- cell-segmentation - mask overlay is the irreplaceable segmentation QC
- phenotyping - annotation supplies labels/priors and confirms clusters are real
- quality-metrics - the image catches artifacts that table statistics cannot
- data-preprocessing - contrast/transform choices mirror preprocessing thresholds
- spatial-analysis - spatial coherence of a painted cluster validates it
<!-- END FILE: imaging-mass-cytometry/interactive-annotation/SKILL.md -->

## 子目录：imaging-mass-cytometry/phenotyping

<!-- BEGIN FILE: imaging-mass-cytometry/phenotyping/SKILL.md -->
---
name: bio-imaging-mass-cytometry-phenotyping
description: Assign cell types from marker expression in IMC/MIBI data using clustering (PhenoGraph/FlowSOM/Leiden/Pixie), marker-based probabilistic classifiers (Astir), or image-context CNNs (CellSighter), covering the double-positive segmentation artifact, lineage-vs-state markers, the two spillover types, and why a "cell type" in imaging is conditioned on a segmentation guess. Use when phenotyping segmented IMC cells, choosing clustering vs classification, diagnosing implausible double-positive populations, separating lineage from functional markers, or transferring labels across a cohort.
tool_type: python
primary_tool: scanpy
---

## Version Compatibility

Reference examples tested with: scanpy 1.10+, anndata 0.10+, astir 0.1.4+, numpy 1.26+, scikit-learn 1.4+, FlowSOM 2.10+ (R)

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

Notes specific to this skill: arcsinh cofactor for IMC single-cell means is ~1, not the suspension-CyTOF 5 -- do not hard-code 5. Astir assigns a per-cell probability and routes below-threshold cells (default 0.7) to "Unknown" rather than forcing a call. CellSighter consumes raw multi-channel image crops + masks (not a mean matrix). FlowSOM consensus metaclustering can override `set.seed()` via ConsensusClusterPlus.

# Cell Phenotyping for IMC

**"Assign cell types to my segmented IMC cells"** -> Map each cell's marker profile to an identity, while distinguishing real co-expression from segmentation/spillover artifacts.
- Python: `scanpy.tl.leiden` (cluster then annotate), `astir` (marker-dictionary classifier)
- R: `FlowSOM` (self-organizing-map clustering)

## The Single Most Important Modern Insight -- a "cell type" in imaging is an inference conditioned on a segmentation guess

In suspension CyTOF each event is one physically isolated cell; in imaging, every cell-by-marker row is the integral of pixels inside a polygon a segmentation algorithm drew, and that polygon is wrong at a non-trivial fraction of cells -- so the most dangerous phenotypes are not biology but boundary artifacts. The canonical case is the CD3+CD20+ ("T/B") double-positive, also CD3+CD68+ and panCK+CD45+. It arises by two distinct mechanisms that are indistinguishable in the mean matrix: segmentation merging (one polygon spans a T cell and a B cell) and lateral spillover (a neighbor's membrane bleeds across the boundary even with perfect masks). The diagnostic tell that separates artifact from biology is spatial: artifactual double-positives localize to cell BORDERS and to high-density regions, so a suspect population must be mapped back onto the image before it is believed (CellSighter authors state the matrix cannot separate the two). The asymmetry that drives method choice: clustering CREATES the artifact as a named population, while a marker-dictionary classifier (Astir) REFUSES it -- a true double-positive vector matches no defined type and is quarantined as "Unknown" rather than crowned a new lineage. This is why imaging-aware groups increasingly prefer (semi-)supervised phenotyping for the lineage layer, and why mean-expression clustering imported wholesale from CyTOF inherits none of the spatial information that would let it notice the polygon was wrong.

## Phenotyping Approach Taxonomy

| Approach | Tools | Input | Robust to bad segmentation? | Failure signature |
|----------|-------|-------|-----------------------------|-------------------|
| Unsupervised clustering | PhenoGraph, FlowSOM, Leiden | cell x marker mean matrix | No -- averages spilled signal into a fake type | phantom double-positive clusters; resolution-dependent type count |
| Pixel-then-cell clustering | Pixie (ark-analysis) | pixel x marker, then cell | More -- avoids committing to a segmentation mean early | parameter-sensitive; still unsupervised |
| Marker-based probabilistic | Astir | mean matrix + marker->type YAML | Partially -- ambiguous cells -> "Unknown" | high Unknown rate if dictionary/markers wrong |
| Image-context CNN | CellSighter, MAPS | raw image crops + masks + labels | Yes -- sees where the signal sits | needs representative labels not harvested from clustering |
| Segmentation-aware mixture | STARLING | mean matrix + doublet prior | Yes -- models a cell as a mixture of two | newer; verify priors |

## Decision Tree by Scenario

| Scenario | Recommended | Why |
|----------|-------------|-----|
| Can write marker->celltype rules, no training labels | Astir (lineage layer) | deterministic, fast, "Unknown" for ambiguous, separates type from state |
| Have expert-labeled cells, segmentation/spillover is a known problem | CellSighter | image context rejects border/spillover double-positives |
| Severe segmentation doubt | STARLING | explicitly models doublet/contamination mixtures |
| Annotated reference cohort, want label transfer | STELLAR | graph model using neighborhood + expression |
| Exploratory, no priors, accept manual annotation | Pixie (most robust) or Leiden/FlowSOM (least) | always run the double-positive image-diagnostic first |
| Any across-condition comparison of the resulting types | hand off to differential-analysis | phenotyping and statistical-unit choice are orthogonal |

## Load and Transform

**Goal:** Build the single-cell matrix on the correct count scale.

**Approach:** Arcsinh with cofactor ~1 for IMC means (not 5), and keep raw counts available. Treat zeros as genuine low ion counts plus Poisson noise, not technical dropout -- scRNA-style imputation hallucinates expression.

```python
import scanpy as sc
import anndata as ad
import numpy as np

adata = ad.read_h5ad('imc_segmented.h5ad')
adata.layers['counts'] = adata.X.copy()
adata.X = np.arcsinh(adata.X / 1.0)   # cofactor ~1 for IMC single-cell means, not 5
```

## Marker-Based Classification with Astir

**Goal:** Assign lineage with a principled abstention instead of a forced call.

**Approach:** Encode marker->celltype rules in a YAML with separate `cell_type` and `cell_state` blocks; Astir returns a per-cell probability and labels below-threshold cells "Unknown". The Unknown rate is itself QC -- 40% Unknown means the dictionary or panel is mis-specified, not that the cells are exotic.

```python
from astir.data import from_anndata_yaml

# inputs are PATHS: an .h5ad and a marker YAML with a cell_type block (CD3->T, CD20->B,
# CD68->Macrophage; no type is both) and an optional cell_state block (Ki67, PD-1)
ast = from_anndata_yaml('imc_segmented.h5ad', 'markers.yaml')
ast.fit_type()
celltypes = ast.get_celltypes(threshold=0.7)   # per-cell labels; < 0.7 -> 'Unknown' (information, not failure)
```

## Cluster on Lineage Markers Only

**Goal:** Discover structure without splitting one type into activation states.

**Approach:** Cluster on lineage markers only; mixing continuous state markers (Ki67, PD-1) fragments one type into proliferating/resting pseudo-types. Validating clusters with the same markers used to cluster is circular -- confirm with held-out evidence (spatial context, independent markers).

```python
lineage = ['CD45', 'CD3', 'CD8', 'CD4', 'CD20', 'CD68', 'E-cadherin']   # lineage only, no Ki67/PD-1
sub = adata[:, lineage]
sc.pp.pca(sub, n_comps=min(15, len(lineage)))
sc.pp.neighbors(sub, n_neighbors=15)
sc.tl.leiden(sub, resolution=0.5)
adata.obs['leiden'] = sub.obs['leiden']
# report cluster stability across resolutions/seeds rather than one hand-picked setting
```

## Diagnose Double-Positive Populations

**Goal:** Decide whether an implausible co-expressing population is biology or artifact.

**Approach:** A real co-expressing cell has the second marker over its own membrane/cytoplasm; an artifact has it concentrated on the border adjacent to a donor neighbor. Quantify how often the suspect cells sit next to a cell of the donor type -- border + donor-adjacency means spillover/merge, not a lineage.

```python
import squidpy as sq

sq.gr.spatial_neighbors(adata, coord_type='generic', delaunay=True)
suspect = adata.obs['cell_type'] == 'CD3+CD20+?'
# if suspect cells are overwhelmingly adjacent to true B cells (the CD20 donor), the CD20
# is spillover/merge, not endogenous -- treat the population as a QC failure, not a discovery
```

## Per-Method Failure Modes

### Clustering -- arbitrary resolution invents types
**Trigger:** tuning Leiden resolution / FlowSOM metacluster count until clusters match expectation. **Mechanism:** the resolution directly sets the type count; it is an identifiability hole, not a tuning knob. **Symptom:** unreproducible type counts; clusters drift across samples. **Fix:** fix the type set with a dictionary/classifier, or report stability across resolutions and seeds.

### FlowSOM -- seed override
**Trigger:** `set.seed()` then consensus metaclustering, expecting reproducibility. **Mechanism:** ConsensusClusterPlus resets the seed internally. **Symptom:** cluster identities differ between runs. **Fix:** set the seed inside the consensus call; assess label stability across runs.

### "I compensated, so no double-positives"
**Trigger:** running CATALYST channel compensation and assuming spatial spillover is handled. **Mechanism:** channel/isotope spillover and lateral/optical spillover are different physical problems. **Symptom:** double-positives persist after channel compensation. **Fix:** channel compensation early (pixel level), REDSEA boundary compensation after segmentation; neither fixes a merged segment -- improve segmentation first.

### Imputing IMC zeros
**Trigger:** scRNA-style dropout imputation on the count matrix. **Mechanism:** IMC zeros are largely genuine low counts, not a capture-dropout mechanism. **Symptom:** hallucinated expression, inflated positivity. **Fix:** model low counts as low counts; do not impute.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| arcsinh cofactor ~1 (IMC means) | Hunter 2024 *Cytometry A* 105:36 | preserves positive/negative separation; 5 over-compresses |
| Astir assignment threshold 0.7 (package default) | Geuenich 2021 *Cell Syst* 12:1173 | principled abstention; the Unknown rate is a QC metric |
| ~40 markers, no redundancy | panel design | one channel can decide a fate -- verify the load-bearing channel per type |
| CellSighter labels NOT from clustering | Amitay 2023 *Nat Commun* 14:4302 | clustering-derived labels re-import the double-positive artifact |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| Tidy CD3+CD20+ cluster reported as a lineage | clustering legitimized a segmentation/spillover artifact | diagnose border-localization on the image; treat as QC failure |
| One T-cell type split into two clusters | state markers (Ki67) mixed into lineage clustering | cluster lineage on lineage markers; profile state within type |
| ~40% of cells "Unknown" in Astir | mis-specified dictionary or missing type | inspect Unknown cells; iterate the YAML; tune 0.7 consciously |
| Cluster identities drift between analyses | stochastic clustering / FlowSOM seed | pin seeds, assess stability; do not assume "cluster 7" is stable |
| "Disease has more Tregs" with p~0 | cell-level testing (pseudoreplication) | aggregate to per-patient proportions; see differential-analysis |

## References

- Levine JH, Simonds EF, Bendall SC, et al. 2015. Data-Driven Phenotypic Dissection of AML Reveals Progenitor-like Cells that Correlate with Prognosis. *Cell* 162(1):184-197. — PhenoGraph.
- Van Gassen S, Callebaut B, Van Helden MJ, et al. 2015. FlowSOM: Using self-organizing maps for visualization and interpretation of cytometry data. *Cytometry A* 87(7):636-645. — FlowSOM.
- Traag VA, Waltman L, van Eck NJ. 2019. From Louvain to Leiden: guaranteeing well-connected communities. *Sci Rep* 9(1):5233. — Leiden.
- Geuenich MJ, Hou J, Lee S, et al. 2021. Automated assignment of cell identity from single-cell multiplexed imaging and proteomic data. *Cell Syst* 12(12):1173-1186.e5. — Astir.
- Amitay Y, Bussi Y, Feinstein B, Bagon S, Milo I, Keren L. 2023. CellSighter: a neural network to classify cells in highly multiplexed images. *Nat Commun* 14:4302. — image-context classification.
- Liu CC, Greenwald NF, et al. 2023. Robust phenotyping of highly multiplexed tissue imaging data using pixel-level clustering. *Nat Commun* 14:4618. — Pixie.
- Brbic M, Cao K, Hickey JW, et al. 2022. Annotation of spatially resolved single-cell data with STELLAR. *Nat Methods* 19(11):1411-1418. — label transfer.
- Campbell KR, et al. 2025. Segmentation aware probabilistic phenotyping of single-cell spatial protein expression data. *Nat Commun* 16:389. — STARLING.
- Bai Y, Zhu B, Rovira-Clave X, et al. 2021. Adjacent Cell Marker Lateral Spillover Compensation and Reinforcement for Multiplexed Images. *Front Immunol* 12:652631. — REDSEA.
- Chevrier S, Crowell HL, Zanotelli VRT, et al. 2018. Compensation of Signal Spillover in Suspension and Imaging Mass Cytometry. *Cell Syst* 6(5):612-620.e5. — channel spillover.
- Hunter B, Nicorescu I, Foster E, et al. 2024. OPTIMAL: An OPTimized Imaging Mass cytometry AnaLysis framework for benchmarking segmentation and data exploration. *Cytometry A* 105(1):36-53. — arcsinh cofactor 1 for IMC single-cell means.

## Related Skills

- cell-segmentation - double-positives diagnose the segmentation/spillover that phenotyping inherits
- data-preprocessing - arcsinh cofactor and channel spillover compensation
- spatial-analysis - phenotype labels feed neighborhood and niche analysis
- differential-analysis - comparing cell-type proportions across conditions at the patient level
- interactive-annotation - mapping clusters back onto tissue to confirm they are real
- flow-cytometry/clustering-phenotyping - FlowSOM/PhenoGraph background for suspension data
<!-- END FILE: imaging-mass-cytometry/phenotyping/SKILL.md -->

## 子目录：imaging-mass-cytometry/quality-metrics

<!-- BEGIN FILE: imaging-mass-cytometry/quality-metrics/SKILL.md -->
---
name: bio-imaging-mass-cytometry-quality-metrics
description: Quality control for IMC/MIBI data across pixel, channel, image, slide, and batch levels, covering Poisson-count SNR (cell-level Gaussian-mixture and empty-channel comparison), spillover-matrix QC (the three physical sources), drift and the missing EQ-bead analog, acquisition artifacts, and sample-of-origin batch effects. Use when deciding whether to keep or drop a channel, ROI, or slide, distinguishing a dim antibody from a failed one, reading a spillover matrix, or diagnosing batch-driven clustering before analysis.
tool_type: mixed
primary_tool: CATALYST
---

## Version Compatibility

Reference examples tested with: numpy 1.26+, scikit-learn 1.4+, scanpy 1.10+, CATALYST 1.28+ (R), spillR 1.0+ (R)

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

Notes specific to this skill: IMC values are integer ion (dual) counts, so SNR must respect Poisson statistics, not fluorescence intuition; biology lives in 1-2 count differences. There is no EQ-bead in-line drift normalizer for ablated tissue. CATALYST `normCytof` is for SUSPENSION bead normalization, not IMC images -- do not apply it to image data. Compensate raw pixels before transformation.

# IMC Quality Metrics

**"Assess the quality of my IMC acquisition"** -> Gate the data at the level each failure lives at -- pixel, channel, image, slide, batch -- before analysis, not by normalizing after.
- Python: `numpy`/`scikit-learn` for SNR, artifacts, batch diagnosis
- R: `CATALYST::plotSpillmat`, `spillR` for spillover QC

## The Single Most Important Modern Insight -- QC is multi-level, and every metric is blind at some level

IMC/MIBI QC is not one number. The data live in a Poisson ion-count regime where "noise" has a defined statistical meaning, and the failures that actually destroy an experiment -- a dead antibody, an unbalanced batch, cells that cluster by which slide they came from rather than by phenotype -- are panel/staining/batch problems that are invisible to per-image SNR. So a single metric is always blind at some level, and the discipline is to gate (drop a channel, ROI, or slide) before analysis rather than normalize after, because correction moves a distribution but never creates the positive/negative separation that staining never produced. Three corollaries a postdoc internalizes. (1) Counts are Poisson: a real floor-abundance epitope genuinely yields a few counts, so "2 counts" is signal or noise depending on dwell, area, and the aggregation level -- SNR grows as sqrt(N) when pixels are pooled into a cell. (2) Dim is not failed: a correctly-titrated antibody to a sparse antigen is supposed to be dim; failure is INSEPARABILITY of positive and negative populations, judged against a known-empty channel, not low absolute intensity. (3) IMC has no EQ-bead drift normalizer -- ablated fixed tissue cannot be spiked with calibration beads, so the only honest cross-batch yardstick is an anchor reference sample included in every run (Casanova 2025), and the absence of an in-line standard is itself expert knowledge.

## Multi-Level QC Framework

| Level | What to measure | Characteristic failure | Blind to |
|-------|-----------------|------------------------|----------|
| Pixel | hot pixels, shot noise, dynamic range | detector spikes; Poisson noise on dim signal | whether the channel is biologically real |
| Channel (marker) | cell-level SNR, spillover in/out, vs empty channel | dead antibody, crosstalk, oxide/+-1 leak | spatial artifacts, batch |
| Image / ROI | mean intensity, cell coverage, ablation completeness | failed ablation, folding, off-target ROI | cross-sample comparability |
| Slide / acquisition | detector drift over time, tune (Lu duals) | within-run sensitivity decay, mis-tune | between-slide offset |
| Batch / cohort | sample-of-origin clustering, lot effects | the cohort clusters by batch not biology | nothing -- the top level |

## Decision Tree by Scenario

| Observation | Decision | Basis |
|-------------|----------|-------|
| Cell-level positive/negative mixture won't separate; signal ~ empty/80ArAr channel | DROP (failed antibody) | inseparability, not intensity |
| Low absolute counts but clean separation, pattern matches biology + control tissue | KEEP (dim-but-real); use at aggregated levels | dim != failed |
| High signal, low SNR (everything "positive") | DROP or re-titrate | non-specific binding |
| Heavy +16 oxide or impurity from a co-expressed partner | DROP or re-mass the panel | unrescuable by compensation |
| Striping / incomplete-ablation banding | DROP the ROI | physical failure, not correctable noise |
| DNA/Ir dropout over a region | MASK the region, keep the rest | non-ablation/tissue loss |
| Tune fails (Lu duals below panel criterion) | RE-TUNE / re-acquire | instrument not in spec |
| Cells cluster by slide/patient not phenotype | batch-correct; if it won't mix, the contrast is confounded | sample-of-origin effect |

## Cell-Level SNR (the decision-relevant number)

**Goal:** Judge marker adequacy at the unit of analysis (the cell), in a count-aware way.

**Approach:** Fit a two-component Gaussian mixture to per-cell mean counts (on non-transformed counts) and take mean(positive)/mean(negative); a failed antibody is one whose components do not separate, regardless of brightness. Compare the distribution to a known-empty channel as the operational "did this antibody work" test.

```python
import numpy as np
from sklearn.mixture import GaussianMixture

def cell_snr(per_cell_counts):
    # two-component mixture on raw per-cell means: separation, not brightness, defines success
    gm = GaussianMixture(n_components=2, random_state=0).fit(per_cell_counts.reshape(-1, 1))
    pos, neg = np.sort(gm.means_.ravel())[::-1]
    return pos / neg if neg > 0 else np.inf

def matches_empty(channel_counts, empty_channel_counts, q=95, tol=2.0):
    # compare the POSITIVE tail (q-th percentile), not the median: a real-but-sparse marker
    # carries its signal in the tail while a failed channel's tail sits at the empty floor.
    # True -> indistinguishable from 80ArAr / an unconjugated lanthanide -> the honest "failed" test
    return np.percentile(channel_counts, q) - np.percentile(empty_channel_counts, q) <= tol
```

## Spillover Matrix QC

**Goal:** Decide whether a panel's crosstalk is acceptable before compensating.

**Approach:** Generate the matrix from single-stain controls and read whole rows, not just neighbors -- spillover has three physically distinct sources with different mass signatures and different fixes. Acceptability is co-expression-dependent: the same percentage is fine between unrelated markers and fatal between co-expressed ones.

```r
library(CATALYST)

sce <- readSCEfromTXT('spillover/')         # single-metal-spotted slides; filenames carry the metal
sce <- prepData(sce, transform = TRUE, cofactor = 5)
sce <- assignPrelim(sce); sce <- applyCutoffs(estCutoffs(sce))
sm  <- computeSpillmat(sce)
plotSpillmat(sce, sm)                        # inspect M+-1 (abundance), M+16 (oxide), and
                                             # any bright off-diagonal at a NON-adjacent mass (impurity)
```

## Batch / Sample-of-Origin QC

**Goal:** Catch the dominant real-world failure -- cells clustering by slide/patient rather than phenotype -- which no per-image metric reports.

**Approach:** Embed cells and color by patient, slide, day, and antibody lot; if cells separate by sample, there is a batch problem. Diagnose before correcting, and correct at the batch layer with an anchor reference sample.

```python
import scanpy as sc

sc.pp.pca(adata); sc.pp.neighbors(adata); sc.tl.umap(adata)
sc.pl.umap(adata, color=['patient', 'slide', 'acquisition_day', 'antibody_lot'])
# separation by these = batch, not biology; a dead/unbalanced channel cannot be normalized into life
```

## Per-Source Failure Modes

### "2 counts is noise"
**Trigger:** discarding low-count channels by fluorescence intuition. **Mechanism:** at 1 um^2/~1 ms dwell a floor-abundance epitope yields a few counts; biology lives in 1-2 count differences. **Symptom:** real dim markers dropped. **Fix:** judge adequacy at the aggregation level analyzed; SNR scales sqrt(N) with pooled pixels; mean expression > ~7 is effectively noise-immune.

### Pixel correlation read as spillover
**Trigger:** flagging high pixel-channel Pearson correlation as spillover. **Mechanism:** co-expressed real markers correlate too; spillover is a directional, mass-structured leak. **Symptom:** false spillover calls, missed real ones. **Fix:** read the single-stain spillover matrix; diagnose by mass signature (+-1, +16, named impurity mass), not correlation.

### Compensating a saturated or co-expressed channel
**Trigger:** trusting compensation on very bright donors or co-expressed pairs. **Mechanism:** the matrix is linear only in the linear range and cannot separate real co-expression from leak. **Symptom:** over/under-shoot; subtracted real biology. **Fix:** keep total per-pair spillover low by panel design; use NNLS (CATALYST) or flag-and-replace (spillR); the real fix is upstream mass assignment.

### Per-image QC declared sufficient
**Trigger:** passing per-image SNR and skipping cross-sample QC. **Mechanism:** FFPE/ischemia/lot variation shifts baselines by batch. **Symptom:** unsupervised analysis groups by sample-of-origin. **Fix:** UMAP/ridgeline by patient/slide/day/lot; include anchor samples; correct at the batch layer.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| Mean expression > ~7 ~ noise-immune | Lu 2023 *Nat Commun* 14:1601 | below it shot noise perturbs per-cell values |
| Abundance sensitivity (M+-1) < 0.3% (Tb) | Han 2018 *Nat Protoc* 13:2121 | TOF peak-tail spec; tuning target, not guarantee |
| Oxide (M+16) < 3% (La) | Han 2018 *Nat Protoc* 13:2121 | plasma-oxide spec; worst for abundant structural markers |
| Isotopic impurity up to ~4% at a named mass | Han 2018 *Nat Protoc* 13:2121 | not predictable from mass proximity -- read the lot |
| Tune ~ Lu >= 1500 dual counts | panel-specific convention | a pass criterion, stated in dual counts (unit matters) |
| Pixel foreground (Otsu) signal < 2/image -> flag | steinbock/IMCDataAnalysis | image-level marker filter |

Where the field has NO accepted threshold (itself expert knowledge): a universal SNR cutoff for a "good marker"; a single spillover percentage defining an "acceptable panel" (acceptability is co-expression-dependent); an in-line pixel-level drift-normalization standard equivalent to EQ beads; a fixed hot-pixel count threshold (DIMR/KNN are adaptive precisely because a fixed cutoff fails across brightnesses).

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| Dropped a real sparse marker | judged by absolute intensity | drop on inseparability + match-to-empty + wrong spatial pattern |
| Spillover "fixed" but double-positives persist | compensated co-expressed/saturated channel | re-mass the panel; NNLS/spillR; compensate raw pixels |
| Cohort clusters by patient | unaddressed batch | anchor reference sample; diagnose before correcting |
| Threshold "1500" or "2" ambiguous | unit omitted | always state dual counts; thresholds are panel/instrument-specific |
| Striped ROI "denoised" | physical ablation failure treated as noise | drop the ROI |
| Indium nuclear signal taken as a marker (MIBI) | In localizes to nuclei | treat as artifact unless validated; use 197Au + background masking |

## References

- Giesen C, Wang HAO, Schapiro D, et al. 2014. Highly multiplexed imaging of tumor tissues with subcellular resolution by mass cytometry. *Nat Methods* 11(4):417-422. — IMC origin; ~50 copies/um^2 detection floor.
- Chevrier S, Crowell HL, Zanotelli VRT, et al. 2018. Compensation of Signal Spillover in Suspension and Imaging Mass Cytometry. *Cell Syst* 6(5):612-620.e5. — spillover sources, single-stain beads, less accurate at high ion load, CATALYST.
- Han G, Spitzer MH, Bendall SC, Fantl WJ, Nolan GP. 2018. Metal-isotope-tagged monoclonal antibodies for high-dimensional mass cytometry. *Nat Protoc* 13(10):2121-2148. — M+-1/M+16/impurity specs and panel design.
- Finck R, Simonds EF, Jager A, et al. 2013. Normalization of mass cytometry data with bead standards. *Cytometry A* 83A(5):483-494. — EQ four-element bead normalization (suspension).
- Ijsselsteijn ME, Somarakis A, Lelieveldt BPF, Hollt T, de Miranda NFCC. 2021. Semi-automated background removal limits data loss and normalizes imaging mass cytometry data. *Cytometry A* 99(12):1187-1197. — sample-of-origin clustering, FFPE/ischemia variation.
- Baranski A, Milo I, Greenbaum S, et al. 2021. MAUI: An image processing pipeline for Multiplexed Mass Based Imaging. *PLoS Comput Biol* 17(4):e1008887. — MIBI artifacts, gold/indium, 1-2 count biology.
- Lu P, Oetjen KA, Bender DE, et al. 2023. IMC-Denoise: a content aware denoising pipeline to enhance Imaging Mass Cytometry. *Nat Commun* 14:1601. — Poisson noise model, mean>7 noise-immune.
- Guazzini M, Reisach AG, Weichwald S, Seiler C. 2024. spillR: spillover compensation in mass cytometry data. *Bioinformatics* 40(6):btae337. — flag-and-replace compensation, preserves correlations.
- Windhager J, Zanotelli VRT, Schulz D, et al. 2023. An end-to-end workflow for multiplexed image processing and analysis. *Nat Protoc* 18(11):3565-3613. — image/cell-level QC and SNR conventions.
- Casanova C, et al. 2025. Standardization of Suspension and Imaging Mass Cytometry Single-Cell Readouts for Clinical Decision Making. *Cytometry A* 107(6):390-403. — anchor/reference samples for batch-level drift correction.

## Related Skills

- data-preprocessing - hot-pixel removal, denoising, and NNLS spillover compensation
- cell-segmentation - segmentation QC and the impossible-co-expression monitor
- phenotyping - failed channels and batch corrupt cell-type calls
- differential-analysis - batch as a covariate when comparing across conditions
- flow-cytometry/cytometry-qc - suspension bead normalization and channel QC background
<!-- END FILE: imaging-mass-cytometry/quality-metrics/SKILL.md -->

## 子目录：imaging-mass-cytometry/spatial-analysis

<!-- BEGIN FILE: imaging-mass-cytometry/spatial-analysis/SKILL.md -->
---
name: bio-imaging-mass-cytometry-spatial-analysis
description: Analyze spatial cell-cell interactions, neighborhoods, and niches in IMC/MIBI data with squidpy and imcRtools, covering neighborhood-enrichment permutation nulls, the abundance-vs-density confound, inhomogeneous Ripley's K, cellular-neighborhood discovery, graph-construction (contact vs proximity), and edge effects. Use when testing whether cell types co-locate, choosing a spatial null, building a neighbor graph, discovering tissue niches, or deciding whether a spatial pattern is real or a density/segmentation artifact.
tool_type: python
primary_tool: squidpy
---

## Version Compatibility

Reference examples tested with: squidpy 1.3+, scanpy 1.10+, anndata 0.10+, numpy 1.26+, imcRtools 1.8+ (R), spatstat 3.0+ (R)

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

Notes specific to this skill: squidpy's `nhood_enrichment` z-score is unbounded and scales with graph degree, so it is NOT comparable across images of different cell counts. squidpy does not implement Ripley's K (its `ripley` and `co_occurrence` are loose analogs); the inhomogeneous K that conditions on tissue density lives in R `spatstat::Kinhom`/`Kcross.inhom`. Build the graph with `gr.spatial_neighbors(coord_type='generic')` before any test.

# Spatial Analysis for IMC

**"Analyze spatial cell interactions in my IMC data"** -> Build a neighbor graph, then test cell-type co-location against an explicitly chosen null, or discover recurrent niches.
- Python: `squidpy.gr.spatial_neighbors`, `squidpy.gr.nhood_enrichment`, `squidpy.gr.co_occurrence`
- R: `imcRtools::buildSpatialGraph`, `spatstat::Kcross.inhom`

## The Single Most Important Modern Insight -- a spatial interaction is a hypothesis test, and the null silently decides what is measured

A "spatial interaction" or "niche" is not an observation; it is a test against a null model, and which null is chosen (label-shuffle vs CSR vs density-conditioned vs patient-level) decides whether the result is real biology, a density gradient, a segmentation artifact, or upstream clustering. The label-permutation null (histoCAT, squidpy `nhood_enrichment`) holds cell positions fixed and shuffles identities: it DOES control global abundance (a rare type cannot show spurious enrichment just from being rare) but it does NOT control local density or tissue architecture -- so two cell types that merely share an anatomical compartment (both enriched in a follicle or at an invasive margin) score as strongly "interacting" with no direct affinity. This density confound is the dominant false-positive engine, and a finding significant under CSR but null under inhomogeneous Ripley's K is a density artifact, not an interaction. Two further facts compound it: the `nhood_enrichment` z-score is unbounded and graph-degree-dependent, so a z of 30 in a 50k-cell image and a z of 8 in a 5k-cell image are not on the same scale (never threshold a fixed z across heterogeneous images); and the replicate is the patient, not the cell or the image, so a per-cell test over tens of thousands of cells reports p~0 for trivial effects (pseudoreplication). The skill forces two questions onto every analysis: against which null, and at which unit.

## Spatial Methods Taxonomy

| Method | Measures | Null / inference | Confound it does NOT control |
|--------|----------|------------------|------------------------------|
| histoCAT / squidpy `nhood_enrichment` | A neighbors B more/less than chance | within-image label shuffle; z-score | local density, architecture, edges |
| squidpy `interaction_matrix` | raw cluster-cluster edge counts | none (descriptive) | everything -- just counts |
| squidpy `co_occurrence` | P(B \| A at distance d) / P(B) | none (descriptive curve) | needs its own CSR null |
| Ripley's K/L, cross-K, K_inhom | clustering vs dispersion over radii | CSR; K_inhom conditions on intensity | tissue inhomogeneity (unless K_inhom); ROI shape |
| Cellular Neighborhoods (CN) | recurrent local compositions (niches) | none -- clustering, not a test | window size = scale; doubly-derived |
| Spatial-LDA / UTAG | microenvironment topics / tissue domains | generative / unsupervised | topic/domain count arbitrary |
| Moran's I / Geary's C | spatial autocorrelation of a continuous mark | permutation / analytic | graph definition; global stat masks local |

## Decision Tree by Scenario

| Question | Method | Why |
|----------|--------|-----|
| Do two named types co-locate more than chance? (fast screen, one image) | `nhood_enrichment` / histoCAT | abundance-aware permutation z |
| Same, but worried about density/architecture | inhomogeneous cross-K (`Kcross.inhom`) | conditions on the tissue's own intensity surface |
| At what scale is a type clustered/dispersed? | Ripley's K/L over radii (edge-corrected) | second-order structure across distance |
| What recurrent multicellular niches exist? (discovery) | Cellular Neighborhoods (sweep window k) | recurrent compositions; no built-in test |
| Is a continuous marker/score spatially structured? | Moran's I (global) / Geary's C (local) | autocorrelation |
| Does an interaction/niche differ between conditions? | hand off to differential-analysis | per-image summary -> patient unit -> mixed model + FDR |

## Build the Spatial Graph (contact vs proximity)

**Goal:** Construct the graph whose definition matches the biological claim.

**Approach:** Delaunay approximates physical adjacency (contact/juxtacrine) but invents long edges across lumen/necrosis, so prune by a max distance; fixed radius gives true proximity (paracrine) at a stated micron scale; kNN silently mixes contact and proximity because fixed k spans microns in dense regions and hundreds of microns in sparse ones. Build the graph per image.

```python
import squidpy as sq
import numpy as np

# contact graph: Delaunay, then prune edges longer than a biological max distance (um)
sq.gr.spatial_neighbors(adata, coord_type='generic', delaunay=True)
dist = adata.obsp['spatial_distances']
keep = dist.copy(); keep.data[keep.data > 30] = 0; keep.eliminate_zeros()   # cap at ~30 um
adata.obsp['spatial_connectivities'] = (keep > 0).astype(float)

# OR proximity graph: fixed radius at a justified micron scale (paracrine range)
# sq.gr.spatial_neighbors(adata, coord_type='generic', radius=30.0)
```

## Neighborhood Enrichment with a Named Null

**Goal:** Test co-location per image with the abundance-aware permutation null, knowing its blind spot.

**Approach:** Run `nhood_enrichment` per image (so the shuffle is within-image), keep the z as a per-image summary, and never threshold a fixed z across images of different size. Cross-check density-driven hits against inhomogeneous K.

```python
per_image_z = {}
for img_id, idx in adata.obs.groupby('image_id').groups.items():
    sub = adata[idx].copy()
    sq.gr.spatial_neighbors(sub, coord_type='generic', delaunay=True)
    sq.gr.nhood_enrichment(sub, cluster_key='cell_type', seed=0)
    per_image_z[img_id] = sub.uns['cell_type_nhood_enrichment']['zscore']
# aggregate these per-image summaries to the PATIENT unit in differential-analysis, not here
```

## Cellular Neighborhoods (niche discovery)

**Goal:** Find recurrent local cell-type compositions, treating them as exploratory.

**Approach:** Per cell, summarize the composition of its window of neighbors, then cluster the windows. The window size IS the spatial scale and is almost always unjustified, so sweep it and report that the biological conclusion survives k in {10, 20, 30}. A CN has no built-in significance test; significance enters only as a cross-condition comparison (differential-analysis).

```python
from sklearn.cluster import KMeans
import pandas as pd

def cellular_neighborhoods(adata, k_window=20, n_cn=10):
    sq.gr.spatial_neighbors(adata, coord_type='generic', n_neighs=k_window)   # window = k neighbors
    conn = adata.obsp['spatial_connectivities']
    onehot = pd.get_dummies(adata.obs['cell_type']).values
    comp = (conn @ onehot)                       # neighbor composition per cell
    comp = comp / comp.sum(axis=1, keepdims=True).clip(min=1)
    return KMeans(n_clusters=n_cn, random_state=0).fit_predict(comp)

adata.obs['CN'] = cellular_neighborhoods(adata, k_window=20)   # sweep k_window to check stability
```

## Per-Method Failure Modes

### nhood_enrichment -- density false positive
**Trigger:** reporting a z-score as a "significant interaction." **Mechanism:** the label-shuffle null absorbs abundance but not local density, so co-compartmentalized types score as interacting. **Symptom:** every type pair sharing a region looks attracted. **Fix:** name the null; cross-check with inhomogeneous cross-K; or shuffle within a compartment, not the whole image.

### Fixed z threshold across images
**Trigger:** calling z>2 "significant" across images of different cell counts. **Mechanism:** the z is unbounded and scales with graph degree. **Symptom:** large images dominate; small images never reach threshold. **Fix:** rank within image or convert to an effect size; aggregate per-image summaries to the patient unit.

### Unpruned Delaunay / kNN mislabeled as contact
**Trigger:** kNN graph results called "contact," or Delaunay across tissue gaps. **Mechanism:** fixed k mixes contact and proximity by density; Delaunay invents long edges across voids. **Symptom:** phantom interactions across lumen/necrosis. **Fix:** prune Delaunay by a max distance; use fixed radius for paracrine claims; state the micron scale.

### CSR Ripley's K on inhomogeneous tissue
**Trigger:** homogeneous-Poisson K on structured tissue. **Mechanism:** CSR assumes constant intensity, so everything tests as clustered. **Symptom:** universal "clustering". **Fix:** inhomogeneous K (`Kinhom`/`Kcross.inhom`) that divides by the estimated intensity surface.

### Niche taken as a discovered fact
**Trigger:** treating a CN as established biology. **Mechanism:** it is doubly-derived (cluster cells -> cluster windows) with an arbitrary window and k, and no significance test. **Symptom:** different labs report different niches on the same tissue. **Fix:** sweep window k; report stability (NMI/ARI); validate niche-defining markers against raw images for spillover.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| CN window = 10 nearest neighbors, 9 CNs retained | Schurch 2020 *Cell* 182:1341 | the canonical CN convention -- sweep it, do not adopt blindly |
| CODEX i-niches: Delaunay 1st-tier, k-means = 100 | Goltsev 2018 *Cell* 174:968 | window/scale is a choice, not a default |
| n_perm >= 10,000 for small corrected p | Schapiro 2017 *Nat Methods* 14:873 | n_perm=1000 floors p at ~1/1001, too coarse after FDR |
| BH-FDR across ~C(C+1)/2 type pairs x radii | multiplicity | ~200 pairs at p<0.05 guarantees false positives |
| Prune Delaunay at a biological max distance (e.g. ~30 um) | graph hygiene | removes edges across acellular voids |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| "Significant interaction" that is two types in one compartment | density confound under label-shuffle | inhomogeneous cross-K; shuffle within compartment |
| p~0 across 50k cells | cell-level pseudoreplication | per-image summary -> patient unit (differential-analysis) |
| Niche changes with the window/k | window IS the scale | sweep k_window and n_cn; report stability |
| Boundary cells dominate a small ROI | ignored edge effects | edge-corrected K; erode/buffer the ROI interior |
| Many "significant" pairs | no multiple-testing correction | BH-FDR across all pairs and radii |

## References

- Schapiro D, Jackson HW, Raghuraman G, et al. 2017. histoCAT: analysis of cell phenotypes and interactions in multiplex image cytometry data. *Nat Methods* 14(9):873-876. — neighborhood permutation test.
- Goltsev Y, Samusik N, Kennedy-Darling J, et al. 2018. Deep Profiling of Mouse Splenic Architecture with CODEX Multiplexed Imaging. *Cell* 174(4):968-981.e15. — cellular neighborhoods (i-niches).
- Schurch CM, Bhate SS, Barlow GL, et al. 2020. Coordinated Cellular Neighborhoods Orchestrate Antitumoral Immunity at the Colorectal Cancer Invasive Front. *Cell* 182(5):1341-1359.e19. — canonical CN convention.
- Palla G, Spitzer H, Klein M, et al. 2022. Squidpy: a scalable framework for spatial omics analysis. *Nat Methods* 19(2):171-178. — squidpy spatial functions.
- Chen Z, Soifer I, Hilton H, Keren L, Jojic V. 2020. Modeling Multiplexed Images with Spatial-LDA Reveals Novel Tissue Microenvironments. *J Comput Biol* 27(8):1204-1218. — Spatial-LDA.
- Kim J, Rustam S, Mosquera JM, et al. 2022. Unsupervised discovery of tissue architecture in multiplexed imaging. *Nat Methods* 19(12):1653-1661. — UTAG domains.
- Ripley BD. 1977. Modelling Spatial Patterns. *J R Stat Soc Series B* 39(2):172-212. — the K-function.
- Moran PAP. 1950. Notes on Continuous Stochastic Phenomena. *Biometrika* 37(1/2):17-23. — Moran's I.
- Geary RC. 1954. The Contiguity Ratio and Statistical Mapping. *Incorporated Statistician* 5(3):115-145. — Geary's C.

## Related Skills

- phenotyping - cell-type labels are the input to every spatial test
- differential-analysis - testing whether interactions/niches differ between conditions at the patient level
- cell-segmentation - over-segmentation and lateral spillover create fake niches
- data-preprocessing - uncompensated spillover manufactures false cell-cell interactions
- spatial-transcriptomics/spatial-statistics - shared squidpy neighborhood and autocorrelation methods
<!-- END FILE: imaging-mass-cytometry/spatial-analysis/SKILL.md -->

<!-- END CATEGORY: imaging-mass-cytometry -->

