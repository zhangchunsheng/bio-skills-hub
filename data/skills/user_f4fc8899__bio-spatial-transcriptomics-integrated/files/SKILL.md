---
slug: bio-spatial-transcriptomics-integrated
version: 1.0.0
displayName: "空间转录组学 / Spatial transcriptomics"
name: bio-spatial-transcriptomics-integrated
summary: >-
  中文：空间转录组学综合技能，整合 12 个相关专题，覆盖空间转录组学：Visium/Xenium/MERFISH/CosMx数据加载、去卷积、空间域识别、空间统计。 English: Integrated Spatial transcriptomics skill covering 12 related topics, including Spatial transcriptomics: Visium/Xenium/MERFISH/CosMx data loading, deconvolution, spatial domain identification, spatial statistics.
description: >-
  中文：这是一个面向空间转录组学的综合生物信息学 Skill，整合当前分类下 12 个相关专题能力。它用于根据研究问题、数据类型和分析阶段，选择合适的方法与工具，规划从输入检查、预处理、核心分析到质量控制、统计解释和结果报告的完整流程。重点覆盖：空间转录组学：Visium/Xenium/MERFISH/CosMx数据加载、去卷积、空间域识别、空间统计。当用户提供相关实验数据、测序结果、表格或研究问题时，它会帮助判断分析目标与前置条件，给出工具选择、关键参数、输入输出、常见失败原因、结果解读和可复现建议。主要工具包括：bin2cell, cell2location, muon。该 Skill 提供分析设计与实施指导，不替代对具体数据质量、生物学背景和最终结论的人工审查。
  English: This is an integrated bioinformatics Skill for Spatial transcriptomics, combining 12 related topic areas. It helps users choose appropriate methods and tools based on the research question, data type, and analysis stage, and plan an end-to-end workflow from input validation and preprocessing through core analysis, quality control, statistical interpretation, and reporting. It covers Spatial transcriptomics: Visium/Xenium/MERFISH/CosMx data loading, deconvolution, spatial domain identification, spatial statistics. For relevant experimental data, sequencing results, tables, or research questions, it clarifies prerequisites, recommends tools and parameters, describes expected inputs and outputs, explains common failure modes, and supports reproducible analysis. Primary tools include: bin2cell, cell2location, muon. It provides methodological and implementation guidance; final data-quality assessment and biological conclusions still require human review.
---

# spatial-transcriptomics 分类 Skill 整合版

> 本文件整合同一主分类目录下 12 个子目录中的 SKILL.md 内容。
> 各子目录正文按原文保留，并通过标题和边界标记进行区分；源文件中的元数据块未被改写。

---

<!-- BEGIN CATEGORY: spatial-transcriptomics -->

## 子目录：spatial-transcriptomics/high-resolution-binning

<!-- BEGIN FILE: spatial-transcriptomics/high-resolution-binning/SKILL.md -->
---
name: bio-spatial-transcriptomics-high-resolution-binning
description: Reconstructs single cells from sub-cellular spatial capture units (Visium HD 2um bins, Stereo-seq DNB spots, Slide-seqV2 beads) by aggregating bins UP into cells rather than deconvolving a mixture DOWN. Use when choosing a bin size and recognizing the sparsity-vs-mixture dilemma (2um bins are too sparse to cluster, but binning to 8/16um re-creates the multi-cell mixture deconvolution was meant to escape); deciding between morphology-driven cell reconstruction (Bin2cell -- StarDist/Cellpose nuclei on a registered H&E/DAPI image, then assign 2um bins to nuclei) and fixed-bin aggregation by whether a co-registered cell image exists; recognizing this as the INVERSE of deconvolution (bin UP, not mix DOWN -- this is the AMBIGUOUS regime of the resolution fork); and handling each platform (Visium HD has an image so reconstruct, Slide-seqV2 has no per-bead image so aggregate or deconvolve, Stereo-seq depends on a registered stain).
tool_type: python
primary_tool: bin2cell
---

## Version Compatibility

Reference examples tested with: bin2cell 0.3+, scanpy 1.10+, anndata 0.10+, spatialdata 0.1+, squidpy 1.4+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# High-Resolution Binning

**"Turn my Visium HD 2um bins into cells"** -> Aggregate sub-cellular capture features UP into single-cell profiles, using a registered nucleus image to decide which bins belong to which cell when one exists.
- Python: Bin2cell (`b2c.read_visium` -> `b2c.stardist` -> `b2c.insert_labels` -> `b2c.bin_to_cell`) for image-guided reconstruction; `scanpy`/`squidpy` for fixed-bin aggregation when no image exists

## Governing Principle

Binning is the INVERSE of deconvolution. Deconvolution takes a capture unit that is LARGER than a cell (a 55um Visium spot holding 1-10 cells) and mixes it DOWN into the cell-type fractions inside it. High-resolution platforms have the opposite geometry: a Visium HD 2um bin, a Stereo-seq ~220nm DNB spot, and a Slide-seqV2 10um bead are SMALLER than or comparable to a single cell, so each unit is a fragment of one cell, not a mixture of several. The task is to aggregate fragments UP into whole cells, never to deconvolve a mixture that does not exist. Running deconvolution on 2um bins invents fractional cell-type mixtures inside features that hold only part of one cell.

The trap that defeats the naive fix is coarse binning. The 2um bins are far too sparse to cluster directly -- most bins capture a handful of transcripts or none, so a per-bin expression vector carries no cell-type signal. The reflex is to bin up to a coarser grid (Visium HD ships 8um and 16um bins for exactly this reason). But an 8um bin still spans roughly two cells, so coarse binning trades resolution for the precise multi-cell-mixture problem the high resolution was meant to escape -- it lands back in the DECONVOLVE regime, now needing a reference and a deconvolution method. This is a genuine dilemma, not a tunable knob: too fine is unclusterably sparse, too coarse is a mixture.

The escape is to define the cell from morphology instead of from a fixed grid. When a high-quality registered image exists (Visium HD ships an H&E or DAPI image co-registered to the bin coordinates), segment nuclei on the IMAGE, then assign each 2um bin to the nucleus whose territory contains it, and sum the bins per nucleus into a real single-cell profile. The cell boundary comes from morphology, not from an arbitrary square. Without a per-feature registered cell image (Slide-seqV2 beads have no co-registered cell morphology), morphology reconstruction is impossible and fixed-bin aggregation or bead-level deconvolution (RCTD doublet-mode is common for Slide-seqV2) remains the standard. Platform plus image availability decides the approach -- not the tool.

## The reconstruction decision

This skill IS the AMBIGUOUS regime of the resolution fork named in spatial-deconvolution: the near-single-cell middle where a unit holds part of, or roughly, one cell. The fork there sorts platforms into DECONVOLVE (spot >> cell), SEGMENT (imaging, already single cells), and AMBIGUOUS; everything below is the AMBIGUOUS branch.

| Platform | Native unit | Co-registered cell image? | Recommended approach | Pitfall |
|----------|-------------|---------------------------|----------------------|---------|
| Visium HD | 2um square bins (gapless lawn) | YES -- H&E or DAPI from CytAssist, registered to bins | Morphology-driven reconstruction (Bin2cell: StarDist/Cellpose nuclei -> assign 2um bins -> per-cell sum) | Treating 8um bins as the unit; an 8um bin still mixes ~2 cells |
| Stereo-seq | ~220nm DNB spots, binned (bin20 ~10-14um, bin50 ~25-36um) | Sometimes -- ssDNA/nuclei stain if acquired and registered | Reconstruct from the stain if registered (StereoCell/Cellpose); else fixed-bin aggregation | Default bin50 spans several cells -> a mixture, not a cell |
| Slide-seqV2 | 10um beads (random close-pack) | NO -- beads carry no co-registered cell morphology | Fixed-bin/bead aggregation, or bead deconvolution (RCTD doublet-mode) | Reconstructing cells from morphology -- there is no image to segment |

The discriminating axis is the registered cell image, not the platform name. A Visium HD run without a usable image collapses to the Slide-seqV2 row; a Stereo-seq run with a clean registered ssDNA stain behaves like the Visium HD row. Confirm the image is registered to the bin coordinate frame before trusting any morphology reconstruction; a misregistered image assigns bins to the wrong nuclei silently. Methods here evolve quickly -- verify the current best practice and the tool's registration assumptions against its latest documentation before committing.

## Loading Visium HD bins

**Goal:** Read the 2um bin matrix together with the registered morphology image into one object whose bin coordinates and image pixels share a frame.

**Approach:** Use the Bin2cell reader, which wraps the Space Ranger 2um output and attaches the full-resolution source image; Visium HD tissue positions are PARQUET, not CSV, and the reader handles that. Inspect the bin sparsity before deciding fine-reconstruct vs coarse-aggregate.

```python
import bin2cell as b2c
import numpy as np

# square_002um is the 2um bin output; source_image_path is the full-res H&E/DAPI registered to the bins
adata = b2c.read_visium('visium_hd_outs/binned_outputs/square_002um/',
                        source_image_path='Visium_HD_tissue_image.tif',
                        spaceranger_image_path='visium_hd_outs/spatial/')

median_counts = np.median(np.asarray(adata.X.sum(axis=1)).ravel())   # 2um bins are sparse: often single-digit median UMIs
print(f'bins: {adata.n_obs}, median UMI/bin: {median_counts:.1f}')   # too sparse to cluster -> reconstruct, do not cluster bins
```

## Morphology-driven cell reconstruction (Bin2cell)

**Goal:** Build true single-cell profiles by segmenting nuclei on the registered image and summing the 2um bins that fall inside each nucleus territory.

**Approach:** Scale the H&E to the segmentation resolution, destripe the Visium HD per-row/per-column count artifact, run StarDist for nuclei, insert the labels onto the bin coordinates, expand each nucleus to capture cytoplasmic bins, then collapse bins per label into a cell-level AnnData. Each cell records how many bins it absorbed.

```python
import bin2cell as b2c

mpp = 0.5                                                            # microns-per-pixel for the scaled image; sets StarDist's effective resolution
b2c.scaled_he_image(adata, mpp=mpp, save_path='stardist/he.tiff')
b2c.destripe(adata)                                                 # corrects Visium HD per-row/per-column total-count striping before it biases segmentation

b2c.stardist(image_path='stardist/he.tiff', labels_npz_path='stardist/he.npz',
             stardist_model='2D_versatile_he', prob_thresh=0.01)    # H&E nuclei; '2D_versatile_fluo' for DAPI
b2c.insert_labels(adata, labels_npz_path='stardist/he.npz', basis='spatial',
                  spatial_key='spatial_cropped_150_buffer', mpp=mpp, labels_key='labels_he')
b2c.expand_labels(adata, labels_key='labels_he', expanded_labels_key='labels_he_expanded')   # nucleus -> cell territory for cytoplasmic bins

cdata = b2c.bin_to_cell(adata, labels_key='labels_he_expanded',
                        spatial_keys=['spatial', 'spatial_cropped_150_buffer'])
# cdata is cell-level: bins summed per label; cdata.obs['bin_count'] = bins absorbed per cell -> a QC handle
```

Bins assigned to no nucleus (label 0) are dropped -- they are inter-cellular space or unsegmented territory, and forcing them into a cell fabricates expression. A cell built from very few bins is a low-confidence reconstruction; filter on `bin_count` the way single-cell QC filters on UMIs. When the H&E nuclei miss sparse regions, a second StarDist pass on a gene-expression-derived image (`b2c.grid_image` -> `2D_versatile_fluo`) plus `b2c.salvage_secondary_labels` rescues cells the H&E alone missed.

## Fixed-bin aggregation when no image exists

**Goal:** Produce a workable cell-scale matrix from Slide-seqV2 beads or an imageless Stereo-seq run, accepting that each unit is approximate rather than a morphology-defined cell.

**Approach:** Aggregate to a cell-scale grid (or treat beads as the unit) and pass the result downstream as APPROXIMATE cells; if the bins clearly mix types, hand them to bead-level deconvolution instead of pretending they are pure. Choose the grid in microns, not in bins, so the physical scale is explicit.

```python
import scanpy as sc
import numpy as np

# coords are in microns; choose a grid near one cell diameter (~10um) -- coarser re-creates the multi-cell mixture
bin_um = 10
coords = adata.obsm['spatial']
gx = np.floor(coords[:, 0] / bin_um).astype(int)
gy = np.floor(coords[:, 1] / bin_um).astype(int)
adata.obs['grid'] = [f'{x}_{y}' for x, y in zip(gx, gy)]            # aggregate bins/beads sharing a grid cell

agg = sc.get.aggregate(adata, by_key='grid', func='sum')           # sum counts per grid cell -> approximate cell-scale matrix
agg.X = agg.layers['sum']
# a grid cell spanning two real cells is a MIXTURE -> if so, deconvolve it (see spatial-deconvolution) rather than typing it
```

The honest caveat: a fixed grid is a compromise, and the coarser it is the more it is a deconvolution problem wearing a cell label. If the downstream question is cell typing and the beads visibly mix types, route to spatial-deconvolution (RCTD doublet-mode for Slide-seqV2) instead of clustering the grid.

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| Clustering on 2um bins yields noise / empty clusters | 2um bins are far too sparse (single-digit UMIs) to carry cell-type signal | Do not cluster bins; reconstruct cells (Bin2cell) or aggregate to a cell-scale grid first |
| "Cell types" from 8um/16um bins look like blends | An 8um bin still spans ~2 cells -- it is a mixture, not a cell | Reconstruct from morphology, or treat the bin as a mixture and deconvolve (spatial-deconvolution) |
| Deconvolution "runs" on 2um bins but fractions are nonsense | Deconvolved a sub-cellular fragment as if it were a multi-cell mixture (inverted the geometry) | Aggregate UP into cells; deconvolution applies to spot >> cell, not bin << cell |
| Bin2cell assigns bins to the wrong nuclei | Source image not registered to the bin coordinate frame | Verify image-to-bin registration before reconstruction; a misregistered image fails silently |
| Reconstruction wanted but there is no image to segment | Slide-seqV2 (and imageless Stereo-seq) have no per-bead cell morphology | Use fixed-bin aggregation or bead deconvolution; morphology reconstruction needs a registered image |
| Reconstructed cells have tiny `bin_count` and erratic profiles | Cells built from too few bins are low-confidence | Filter on `bin_count` as single-cell QC filters on UMIs; consider salvage_secondary_labels |
| Striping artifacts bias nuclei or counts | Visium HD per-row/per-column total-count striping left uncorrected | Run `b2c.destripe` before segmentation and before downstream normalization |

## Related Skills

- spatial-deconvolution - the resolution fork that sends the AMBIGUOUS regime here; deconvolution is the opposite (mix DOWN) geometry to this skill's bin UP
- image-analysis - nucleus/cell segmentation (StarDist, Cellpose) that morphology-driven reconstruction depends on
- spatial-data-io - load Visium HD PARQUET bin positions and the registered image before reconstruction
- spatial-preprocessing - QC and normalize the reconstructed cells once they exist (cell-scale, not bin-scale, thresholds)
- single-cell/cell-annotation - annotate the reconstructed cells with markers or label transfer
- single-cell/clustering - cluster reconstructed cells, which now carry cell-scale signal that raw bins lacked

## References

- Polanski K, Bartolome-Casado R, Sarropoulos I, et al. (2024) Bin2cell reconstructs cells from high resolution visium HD data. Bioinformatics 40(9):btae546. DOI 10.1093/bioinformatics/btae546
- Chen A, Liao S, Cheng M, et al. (2022) Spatiotemporal transcriptomic atlas of mouse organogenesis using DNA nanoball-patterned arrays (Stereo-seq). Cell 185(10):1777-1792. DOI 10.1016/j.cell.2022.04.003
- Stickels RR, Murray E, Kumar P, et al. (2021) Highly sensitive spatial transcriptomics at near-cellular resolution with Slide-seqV2. Nature Biotechnology 39:313-319. DOI 10.1038/s41587-020-0739-1
- Schmidt U, Weigert M, Broaddus C, Myers G (2018) Cell detection with star-convex polygons (StarDist). MICCAI, Lecture Notes in Computer Science 11071:265-273. DOI 10.1007/978-3-030-00934-2_30
- Stringer C, Wang T, Michaelos M, Pachitariu M (2021) Cellpose: a generalist algorithm for cellular segmentation. Nature Methods 18:100-106. DOI 10.1038/s41592-020-01018-x
- Cable DM, Murray E, Zou LS, et al. (2022) Robust decomposition of cell type mixtures in spatial transcriptomics (RCTD). Nature Biotechnology 40:517-526. DOI 10.1038/s41587-021-00830-w

Visium HD (2um bins, registered CytAssist H&E/DAPI image, PARQUET tissue positions) is a 10x Genomics product; 10x provides the Space Ranger output specification and onboard image registration but no primary peer-reviewed platform paper, so it is attributed to 10x Genomics rather than a citation.
<!-- END FILE: spatial-transcriptomics/high-resolution-binning/SKILL.md -->

## 子目录：spatial-transcriptomics/image-analysis

<!-- BEGIN FILE: spatial-transcriptomics/image-analysis/SKILL.md -->
---
name: bio-spatial-transcriptomics-image-analysis
description: Segments cells/nuclei and extracts image features from imaging spatial transcriptomics (Xenium, MERFISH/MERSCOPE, CosMx) and H&E/IF tissue images using Cellpose, StarDist, Baysor, and Squidpy. Use when choosing a segmentation strategy (DAPI nucleus + expansion vs membrane-stain whole-cell vs transcript-aware Baysor/proseg vs segmentation-free SSAM) given the available stain; judging whether transcript spillover is fabricating false co-expression and short-range cell-cell signal; and deciding whether the derived cell-by-gene matrix is trustworthy before downstream typing, DE, or ligand-receptor analysis.
tool_type: python
primary_tool: squidpy
---

## Version Compatibility

Reference examples tested with: squidpy 1.7+, scanpy 1.10+, scikit-image 0.22+, numpy 1.26+, pandas 2.2+, cellpose 4.0+ (CLI tools: Baysor 0.6+, proseg 1.0+)

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Image Analysis for Spatial Transcriptomics

**"Segment cells from my imaging data"** -> Draw cell/nucleus boundaries on an image (or on the transcript point cloud) and assign each molecule to one cell, producing a cell-by-gene matrix.
- Python image-based: `cellpose.models.CellposeModel().eval()`, StarDist for nuclei, `squidpy.im.segment()` (watershed baseline)
- CLI transcript-based: Baysor, proseg run on the molecule table (x, y, gene)

**"Extract image features for my spots"** -> Summarize pixel intensity/texture under each Visium spot (a DIFFERENT operation from segmentation -- no cell boundaries are drawn).
- Python: `squidpy.im.calculate_image_features()` (summary, histogram, texture/GLCM)

Keep these two operations distinct. `squidpy.im` feature extraction (texture/summary on H&E) describes the image patch under a spot for domain detection. Segmentation manufactures the cells themselves. This skill leads with segmentation because that is the dominant error source; feature extraction is a downstream convenience.

## Governing Principle

In imaging spatial data the cell is a segmentation HYPOTHESIS, not an observation. The raw data are images plus a table of decoded molecules with x, y (and sometimes z); there is no native cell. A cell-by-gene matrix exists only AFTER an algorithm draws boundaries and assigns each molecule to one cell or to background. Every row of that matrix is produced by the segmentation step, which is the dominant, irreducible upstream error source for every imaging platform -- it confounds typing, DE, and communication downstream (Mitchel et al. 2026 *Nat Genet* 58:434, who find segmentation errors "dominate the results" for context-dependent DE and ligand-receptor inference).

Segmentation fails three ways, and each fabricates a specific downstream lie:
- Over-segmentation splits one cell into many -> inflated cell count; fragments look low-quality and get filtered or mis-typed.
- Under-segmentation merges neighbors into a spatial DOUBLET whose profile is a mixture of two types. Unlike droplet doublets these are spatially structured -- adjacent types merge preferentially -- so standard doublet detectors (Scrublet, DoubletFinder) MISS them, because the synthetic doublets those tools simulate are random pairs, not neighbors.
- Transcript mis-assignment / spillover: a molecule of cell A is assigned to neighbor B (diffusion, optical PSF bleed, z-collapse, boundary error). Spillover is DISTANCE-DEPENDENT and strongest between adjacent heterotypic cells, so it manufactures spatially-structured contamination, not uniform noise.

The cascade is worst for exactly the analyses people prize. A T cell abutting epithelium picks up keratin spillover -> false marker co-expression -> a spurious "transitional/hybrid" state that is pure artifact; rare cells in dense parenchyma (TILs, neutrophils) are swamped by neighbor spillover and lost. Crucially, distance-dependent spillover FABRICATES the short-range co-localization that ligand-receptor and cell-cell communication tools detect -- so an L-R "hit" between two touching types can be a pure segmentation artifact (a circularity; see spatial-communication). Treat the derived matrix as PROVISIONAL and run a contamination QC step before trusting any single-cell-resolution claim.

## The decision: choose by available signal, not by reflex

The first question is not "which tool" but "what boundary signal do I have?" A nuclear stain says where the nucleus is; a membrane/boundary stain says where the cell ENDS. Whole-cell segmentation is boundary-finding, and DAPI carries no boundary information -- so DAPI-only whole-cell is always inference (expansion). Adding a membrane/boundary stain converts that inference into measurement, and is the single highest-leverage change available -- it beats swapping algorithms on DAPI-only data.

| Tool | Class | Input signal | Best when | Fails / weak when |
|------|-------|--------------|-----------|-------------------|
| StarDist | image, star-convex polygons | DAPI, 1 channel | round, crowded NUCLEI; fast | non-convex shapes (whole cells, neurons) cannot be represented; not a whole-cell tool |
| Cellpose | image, DL generalist | 1-2 ch (nucleus +/- membrane) | generalist; 2-channel nucleus+membrane = true whole-cell; retrainable | no transcript-only mode; over/under-segments on DAPI-only without a membrane channel |
| Watershed (`squidpy.im.segment`) | classic flooding | DAPI seeds + intensity | fast baseline; seeded splitting of touching nuclei | over-segments textured nuclei; seed/threshold-sensitive; no shape prior |
| Mesmer / DeepCell | image, DL whole-cell (TissueNet) | 2 ch: nuclear + membrane | any platform WITH a membrane stain (also CODEX/MIBI/IMC); human-level whole-cell | needs a membrane channel; DAPI-only -> nuclear only |
| Baysor | transcript MRF+EM, optional prior | molecule table (+ optional DAPI) | refining/replacing image segmentation by transcriptional composition; recovers cells images miss; runs with or without a prior | sparse/low-plex panel + no prior -> unstable; compute-heavy |
| proseg | transcript, cell-simulation membership | molecule table | transcript-only whole-cell WITHOUT a membrane stain; fast; recovers hard immune cells | sparse-panel limits of all transcript-only methods; newer/less battle-tested |
| SSAM / ClusterMap | segmentation-FREE molecule density | molecule table | cell-type/domain MAPPING when boundaries are hopeless; recovers low-density types | produce NO cell objects -> no per-cell composition, counts, or neighbor graph |

The ladder of trust runs: DAPI-only StarDist/Cellpose-nuclei (accept nuclear sensitivity loss or expansion bias) < membrane-stain whole-cell Mesmer or 2-channel Cellpose < transcript-aware Baysor/proseg (molecules, not a fixed radius, set boundaries) < segmentation-free SSAM/ClusterMap (best mapping, but the cell unit is lost -- no per-cell matrix, neighbor graph, or QC). Methods evolve fast here; verify current best practice against the latest benchmarks before committing.

### Nucleus-only and the expansion trap

Nuclear (DAPI) segmentation is robust because nuclei are round, separated, and high-contrast -- but the nucleus holds only a minority of mRNA, so cytoplasmic transcripts fall OUTSIDE the mask and are discarded (large sensitivity loss) or must be reassigned. The cheap substitute is nucleus expansion: dilate each nuclear mask by a fixed radius until it hits a neighbor. This assumes round, equal-sized, isotropically-arranged cells -- false for almost all tissue. In dense tissue expanded disks collide and partition intercellular space by a Voronoi-like rule unrelated to true membranes (the worst region for spillover); elongated or large-cytoplasm cells (neurons, muscle, glia, macrophages) are badly served -- a fixed disk captures none of their projections and steals neighbors' transcripts. No single radius is correct for a heterogeneous tissue. Expansion is a baseline, not a solution.

Xenium makes this concrete: XOA v1.0-1.9 used DAPI + 15 um nucleus expansion; v2.0+ cut the default to 5 um "for improved accuracy" -- an admission that 15 um over-assigned in dense tissue. The vendor changed the answer, so do not treat any expansion radius as ground truth. Note that Cellpose on Xenium is a community path via Xenium Ranger `import-segmentation`, NOT the built-in XOA default -- do not conflate them.

## Segment nuclei from a DAPI/IF image

**Goal:** Produce instance masks (one integer label per cell) from a nuclear-stain image as the starting cell hypotheses.

**Approach:** Run Cellpose's generalist model; in v4 (Cellpose-SAM) there is one model, channels are no longer an input, and `diameter` is optional because the model is size-invariant. With a membrane channel available, pass it as a second channel for true whole-cell masks instead of nuclei + expansion.

```python
from cellpose import models

model = models.CellposeModel(gpu=False)            # v4 Cellpose-SAM single generalist model; v3 used models.Cellpose(model_type='nuclei')
masks, flows, styles = model.eval(dapi_image, diameter=None)   # v4 returns 3 values + drops channels=; v3 returned masks, flows, styles, diams and took channels=[0,0]
# masks: integer label image; 0 = background, 1..N = cells. This is a HYPOTHESIS, not ground truth.
n_cells = int(masks.max())
```

DAPI-only masks are nuclei. Approximating whole cells without a membrane stain requires expansion (round-cell bias above) or a transcript-aware method. With a membrane/boundary channel, stacking `[nucleus, membrane]` and passing both lets Cellpose-SAM use the first channels in any order -- that converts boundary inference into measurement.

## Re-segment from the transcript table (membrane-free whole-cell)

**Goal:** Recover cells that image-based nuclear segmentation drops (small, irregular, immune) by letting transcript composition and density define boundaries.

**Approach:** Run Baysor or proseg on the per-molecule table (x, y, gene). These are CLI tools; the molecule table is the source of truth and the only object that permits re-segmentation. Optionally seed Baysor with the vendor nuclear masks as a prior.

```bash
# Baysor: molecule-table segmentation; -m = min transcripts/cell, -s = expected cell scale (um), :gene names the gene column
baysor run -x x_location -y y_location -g feature_name -m 30 -s 10 \
  --prior-segmentation-confidence 0.5 transcripts.csv nucleus_id

# proseg: transcript-only whole-cell, reads Xenium/CosMx/MERSCOPE molecule tables directly
proseg --xenium transcripts.csv.gz --output-counts counts.csv.gz --output-cell-polygons cells.geojson
```

Baysor and proseg output per-molecule cell assignments -> rebuild a cell-by-gene matrix from those. Where the panel is sparse and no membrane stain exists, all transcript-only methods become unstable -- check cell-yield and size distributions against the image before trusting them.

## QC the segmentation before trusting the matrix

**Goal:** Detect the segmentation failure modes (over/under-segmentation, spillover) BEFORE they propagate into typing and communication results.

**Approach:** Treat the matrix as provisional. Inspect cell-size and transcripts-per-cell distributions (bimodality flags merged doublets or fragments), check for impossible co-expression of mutually exclusive lineage markers (a spillover signature), and where possible run a dedicated contamination tool.

```python
import numpy as np

counts = np.asarray(adata.X.sum(axis=1)).ravel()       # transcripts per cell
area = adata.obs['cell_area'].to_numpy()               # from the segmentation polygons
# Over-segmentation: a spike of tiny, low-count fragments. Under-segmentation: a tail of huge, high-count "cells".
print('transcripts/cell pct [5,50,95]:', np.percentile(counts, [5, 50, 95]))
print('cell area pct [5,50,95]:', np.percentile(area, [5, 50, 95]))

# Spillover signature: cells co-expressing markers of two mutually exclusive lineages (e.g. epithelial KRT + T-cell CD3).
# Distance-dependent -> these false double-positives concentrate at heterotypic boundaries.
epi = np.asarray(adata[:, 'EPCAM'].X).ravel() > 0
tcell = np.asarray(adata[:, 'CD3E'].X).ravel() > 0
print('suspicious EPCAM+CD3E+ cells:', int((epi & tcell).sum()))
```

Dedicated correction/QC tools target the distance-dependent contamination directly: SPLIT and neighborhood factorization (Mitchel et al. 2026) for contamination, FastReseg for transcript-based re-segmentation (CosMx), and ovrlpy for vertical/z-collapse doublets. SOPA runs Cellpose and Baysor on the same data with patch-based conflict resolution. Run a contamination step before any rare-state, hybrid-state, or short-range L-R claim.

## Extract image features per spot (NOT segmentation)

**Goal:** Summarize the tissue image under each Visium spot (intensity, texture) to augment expression-based spatial-domain detection.

**Approach:** Wrap the image in a Squidpy `ImageContainer` and call `calculate_image_features`. This draws no cell boundaries -- it describes the pixel patch under each spot. Pass `layer='image'` explicitly if a segmentation layer already exists on the container.

```python
import squidpy as sq

img = sq.datasets.visium_hne_image_crop()              # ImageContainer; pair with the matching adata
adata = sq.datasets.visium_hne_adata_crop()
sq.im.calculate_image_features(adata, img, layer='image', features=['summary', 'texture'],
                               key_added='img_features', n_jobs=1, show_progress_bar=False)
# texture = GLCM (contrast, homogeneity, correlation, ASM); summary = per-channel intensity stats
feats = adata.obsm['img_features']                     # rows = spots, columns = features
```

Watershed via `sq.im.segment(img, layer='image', method='watershed')` is a fast classical baseline that over-segments H&E; use it for a quick look, not for production cell calling. Morphology per mask comes from `skimage.measure.regionprops_table` (area, eccentricity, solidity).

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| Many tiny, low-count "cells" | Over-segmentation split single cells | Lower model sensitivity / raise `min_size`; check cell-area histogram for a fragment spike; prefer a learned model over watershed |
| Cluster of cells co-expressing exclusive lineage markers (KRT + CD3) | Transcript spillover fabricating co-expression at heterotypic boundaries | Run a contamination QC (SPLIT, neighborhood factorization); re-segment with a membrane stain or Baysor/proseg; do not interpret as a "hybrid state" |
| A short-range ligand-receptor hit between two touching types | Distance-dependent spillover manufactures the short-range co-localization (circularity) | Validate against segmentation quality; constrain L-R by distance; treat as hypothesis (see spatial-communication) |
| Standard doublet detector finds almost nothing, yet merged cells exist | Spatial doublets are neighbor merges, not random pairs the detector simulates | Inspect transcripts/cell and area tails; re-segment; do not rely on Scrublet/DoubletFinder for imaging merges |
| Cytoplasmic markers nearly absent from every cell | Nucleus-only mask discarded cytoplasmic mRNA | Expand the mask, add a membrane stain, or use a transcript-aware method |
| Sharp drop in transcripts/cell after a vendor software update | Xenium expansion default cut 15 um -> 5 um (v2.0) | Expected; the smaller radius assigns fewer (and fewer mis-assigned) transcripts -- re-run downstream, do not "fix" |
| `model.eval` returns 3 values but code unpacks 4 | Cellpose v4 dropped `diams` and the `channels=` argument | Unpack `masks, flows, styles`; remove `channels=`; `diameter` is optional in v4 |
| `Unable to determine which layer to use` | A segmentation layer was added, so the container has >1 layer | Pass `layer='image'` to `calculate_image_features` / `segment` |
| Transcript-only segmentation yields implausible cell shapes/yield | Sparse/low-plex panel with no prior -> Baysor/proseg unstable | Add a nuclear prior; compare yield + size to the image; fall back to image segmentation |

## Related Skills

- spatial-transcriptomics/spatial-preprocessing - QC floors and non-gene-count normalization for the post-segmentation matrix
- spatial-transcriptomics/spatial-communication - ligand-receptor inference, where segmentation spillover fabricates short-range signal (the circularity)
- spatial-transcriptomics/spatial-proteomics - whole-cell segmentation on membrane markers for CODEX/IMC/MIBI (Mesmer/DeepCell)
- imaging-mass-cytometry/cell-segmentation - segmentation for multiplexed-imaging proteomics
- spatial-transcriptomics/spatial-data-io - load the molecule table (the only object that permits re-segmentation) and the derived matrix

## References

- Stringer C, Wang T, Michaelos M, Pachitariu M (2021) Cellpose: a generalist algorithm for cellular segmentation. Nature Methods 18:100-106. DOI 10.1038/s41592-020-01018-x
- Pachitariu M, Stringer C (2022) Cellpose 2.0: how to train your own model. Nature Methods 19:1634-1641. DOI 10.1038/s41592-022-01663-4
- Schmidt U, Weigert M, Broaddus C, Myers G (2018) Cell Detection with Star-Convex Polygons (StarDist). MICCAI 2018, LNCS 11071:265-273. DOI 10.1007/978-3-030-00934-2_30
- Greenwald NF, Miller G, Moen E, et al. (2022) Whole-cell segmentation of tissue images with human-level performance using large-scale data annotation and deep learning (Mesmer/DeepCell). Nature Biotechnology 40:555-565. DOI 10.1038/s41587-021-01094-0
- Petukhov V, Xu RJ, Soldatov RA, et al. (2022) Cell segmentation in imaging-based spatial transcriptomics (Baysor). Nature Biotechnology 40:345-354. DOI 10.1038/s41587-021-01044-w
- Jones DC, Elz AE, Hadadianpour A, et al. (2025) Cell simulation as cell segmentation (proseg). Nature Methods 22:1331-1342. DOI 10.1038/s41592-025-02697-0
- Park J, Choi W, Tiesmeyer S, et al. (2021) Cell segmentation-free inference of cell types from in situ transcriptomics data (SSAM). Nature Communications 12:3545. DOI 10.1038/s41467-021-23807-4
- Mitchel J, Gao T, Petukhov V, et al. (2026) Impact and correction of segmentation errors in spatial transcriptomics. Nature Genetics 58:434-444. DOI 10.1038/s41588-025-02497-4
- Palla G, Spitzer H, Klein M, et al. (2022) Squidpy: a scalable framework for spatial omics analysis. Nature Methods 19:171-178. DOI 10.1038/s41592-021-01358-2
- Janesick A, Shelansky R, Gottscho AD, et al. (2023) High resolution mapping of the tumor microenvironment using integrated single-cell, spatial and in situ analysis (Xenium). Nature Communications 14:8353. DOI 10.1038/s41467-023-43458-x
<!-- END FILE: spatial-transcriptomics/image-analysis/SKILL.md -->

## 子目录：spatial-transcriptomics/spatial-communication

<!-- BEGIN FILE: spatial-transcriptomics/spatial-communication/SKILL.md -->
---
name: bio-spatial-transcriptomics-spatial-communication
description: Maps cell-cell communication and ligand-receptor co-expression in spatial transcriptomics (Visium, Xenium, MERFISH, CosMx, Slide-seq) with Squidpy ligrec, COMMOT, stLearn, CellChat-spatial, and NicheNet. Use when choosing a method by whether spatial distance is actually modeled (squidpy ligrec is space-blind cluster-permutation vs COMMOT optimal-transport is distance-aware vs stLearn neighborhood vs CellChat-spatial filter) and by secreted-vs-contact-dependent range; choosing the ligand-receptor database knowingly because it drives the result as much as the algorithm; guarding against segmentation-spillover circularity that fabricates short-range hits; treating every ligand-receptor score as a co-expression hypothesis on a confidence ladder, not validated signaling; correcting for thousands of pair-by-cell-type-pair permutation tests; and recognizing that a targeted imaging panel rarely contains the relevant ligands and receptors so a "no communication" call is uninformative.
tool_type: python
primary_tool: squidpy
---

## Version Compatibility

Reference examples tested with: squidpy 1.4+, scanpy 1.10+, anndata 0.10+, commot 0.0.3+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

COMMOT is the distance-aware alternative shown below; LIANA+ wraps and benchmarks several methods/databases; CellChat v2 (R) and NicheNet (R) are noted in the decision table but not coded here.

# Spatial Cell-Cell Communication

**"Map cell-cell communication in my spatial data"** -> Score ligand mRNA in a sender population against receptor mRNA in a receiver population, optionally weighted by spatial proximity, against a permutation null.
- Python: `squidpy.gr.ligrec` (CellPhoneDB engine, space-blind) or `commot.tl.spatial_communication` (optimal transport, distance-aware)
- R: CellChat v2 spatial mode, or NicheNet for downstream receiver-response linkage

## Governing Principle

Co-expression is not communication, and segmentation spillover fabricates exactly the short-range signal these tools reward.

Every standard tool (squidpy ligrec, COMMOT, CellChat, CellPhoneDB, stLearn, SpaTalk, NicheNet) ultimately computes some function of ligand mRNA in a sender cell type and receptor mRNA in a receiver cell type, against a permutation null. None measures protein, binding, secretion, diffusion, or a downstream response. A "significant" ligand-receptor pair means "ligand mRNA in A and receptor mRNA in B are spatially co-expressed above a permutation null, under database D and radius r" -- a co-expression HYPOTHESIS, full stop. The field routinely reports these correlative pairs in the language of validated signaling ("cell type A signals to B via pathway X"); a careful analyst refuses that wording and reads every call as a testable hypothesis (Armingol 2021 *Nat Rev Genet* 22:71-88).

Spatial proximity is a weak filter, not evidence. A distance constraint removes the absurd long-range calls a non-spatial method would make, but two cells being adjacent and co-expressing a pair is nowhere near sufficient for signaling. Adding a radius converts an implausible call into a plausible-looking hypothesis -- that is all it does.

The spillover circularity is the spatial-specific trap. In imaging platforms, distance-dependent transcript mis-assignment between adjacent cells (segmentation spillover) bleeds a sender's ligand transcripts into a touching receiver and vice versa, manufacturing precisely the short-range ligand-receptor co-occurrence these methods detect. A "hit" between two touching cell types can therefore be pure segmentation artifact, and spillover is strongest between adjacent heterotypic cells -- the exact pairs a communication analysis is built to find (Mitchel 2026 *Nat Genet* 58:434). Validate every short-range call against segmentation quality before believing it (see spatial-transcriptomics/image-analysis).

The database is result-determining, as much as the algorithm. CellPhoneDB, CellChatDB, and other resources differ in content, complex/subunit handling, and curation; swapping the resource changes the inferred network as much as or more than swapping the method (Dimitrov 2022 *Nat Commun* 13:3224). Two tools agreeing is often two tools sharing a database, not independent confirmation. Report the database and version as a primary methods parameter.

On capture/spot platforms there is a second spatial trap distinct from imaging spillover: a Visium spot is a 1-10-cell MIXTURE, so the "cell types" fed to a communication tool are deconvolution estimates, and a ligand and its receptor can co-reside within the SAME multi-cell spot with no inter-cellular signaling implied at all. Running ligrec on spot clusters treats regions/niches as cell types and compounds deconvolution error into the L-R call. Prefer single-cell-resolution data, or deconvolve first and restrict the analysis to spots where the sender and receiver types are estimated to be present, and read spot-level calls as the weakest rung of the confidence ladder.

## Method Decision Table

The first question is not "which tool" -- it is "does this method actually model spatial distance, and does it distinguish secreted from contact-dependent range?" Most do not.

| Method | Spatial mechanism | L-R database | Best when | Fails when |
|--------|-------------------|--------------|-----------|------------|
| squidpy `ligrec` (CellPhoneDB engine) | NONE by default -- permutes cluster labels; any cluster can "talk" to any cluster | CellPhoneDB (via omnipath) | Fast scanpy-native CellPhoneDB baseline on large data | Misused as "spatial" -- it is space-blind unless cells are pre-restricted; sensitive to clustering granularity |
| COMMOT (Cang & Nie) | Collective optimal transport; distance COST with a per-pathway cutoff; isotropic, diffusion-like | CellPhoneDB/CellChat-derived, built in | True spatial data; want competition among L-R species + sender/receiver direction maps | One characteristic length per pathway -- cannot separate secreted vs contact; sensitive to the cutoff; transport is not flux |
| stLearn cci | L-R co-expression within local neighborhoods; two-level (label + position) permutation | User-supplied (CellPhoneDB-style) | Spot/imaging hotspot maps of where a pair co-occurs | Tests spatial co-expression enrichment, not signaling; depends on neighborhood radius |
| CellChat v2 (spatial mode, R) | Distance constraint applied as a FILTER on an expression-driven mass-action score | CellChatDB (cofactor-aware; differs from CellPhoneDB) | Pathway-level aggregation, cofactor/antagonist modeling, hierarchy summaries | Mass-action over group-averaged expression is not kinetics; spatial mode still filters a non-spatial score |
| NicheNet (R) | NONE -- not spatial; uses analyst-defined sender/receiver sets | Curated integrated prior network | Linking a ligand to DOWNSTREAM target-gene response in the receiver | Not a detector; the prior is fixed/generic; a "top ligand" is a prior-weighted hypothesis |
| MISTy (R) | Multi-view random forests over juxta/para radii; reports view importances | NONE -- marker-to-marker, no L-R DB | Highly-multiplexed imaging; dissecting spatial co-variation without an L-R DB | Models correlative spatial structure, not signaling flux |

Secreted vs contact-dependent ligands need DIFFERENT ranges, and most tools apply ONE cutoff to all pairs. A juxtacrine pair (Notch-Delta, contact-only) and a diffusible chemokine have categorically different interaction lengths; a single global radius over-calls one class and misses the other. Paracrine spread is a reaction-diffusion process, not a hard radius -- interrogate any fixed cutoff (the ~500 um conventions in the literature are conveniences, not biology). Because methods and databases genuinely compete here, verify current best practice against the latest LIANA+/benchmark docs before committing.

## The Confidence Ladder

A communication claim earns confidence by climbing, not by a low p-value:

co-expression (bare L-R) < proximity-conditioned co-expression < downstream receiver-response support (NicheNet target DE up in neighboring receivers) < orthogonal protein co-localization (the ligand AND receptor protein imaged together) < perturbation (block the ligand/receptor, measure the receiver).

Almost nothing in the spatial literature reaches the perturbation tier. The single most defensible computational move is to require BOTH spatial proximity AND a coherent downstream transcriptional response in the receiver: co-expression proposes, receiver-response disposes.

## Space-Blind Baseline (squidpy ligrec)

**Goal:** Rank ligand-receptor pairs that are co-expressed across annotated cell-type pairs as a fast CellPhoneDB-style baseline.

**Approach:** Run the permutation engine over cluster labels; recognize this is space-blind -- it tests "is this pair unusual for these two cell types," not "is this pair unusually co-located." It needs cell-type annotations (see spatial-transcriptomics/spatial-domains) and fetches the database from omnipath (internet required).

```python
import squidpy as sq

adata = sq.datasets.seqfish()                            # built-in single-cell-resolution fixture with celltype labels
res = sq.gr.ligrec(
    adata,
    cluster_key='celltype_mapped_refined',
    n_perms=1000,                                        # permutation null; more = stabler p-values, slower
    threshold=0.01,                                      # min FRACTION of cells in a cluster expressing the gene -- NOT a p-value
    use_raw=False,                                       # seqfish has no .raw; default True errors here
    copy=True,
)
pvalues = res['pvalues']                                 # MultiIndex columns = (cluster_1, cluster_2), index = (ligand, receptor)
means = res['means']
```

The `threshold` argument is the expression-fraction floor inside the engine, not a significance cutoff -- mislabeling it as a p-value is a common error. The default fetches all omnipath interactions; pass `interactions=<DataFrame with 'source'/'target'>` to pin a known database/version.

## Honest Significance and Multiple Testing

**Goal:** Extract co-expression hypotheses without manufacturing a network from nominal p-values.

**Approach:** The test space is thousands of L-R pairs times every ordered cell-type pair; correct over the full space and treat survivors as ranked hypotheses, not findings.

```python
import numpy as np
import pandas as pd
from statsmodels.stats.multitest import multipletests

flat = pvalues.stack([0, 1], future_stack=True).rename('pval').reset_index()
flat = flat.dropna(subset=['pval'])
flat['padj'] = multipletests(flat['pval'].values, method='fdr_bh')[1]   # correct over the WHOLE pair x celltype-pair space
hits = flat[flat['padj'] < 0.05].sort_values('padj')
print(f'{len(hits)} co-expression hypotheses survive BH-FDR out of {len(flat)} tests')
```

Reporting top-ranked pairs at nominal p without an honest corrected null is how interaction networks get manufactured. Label permutation and position permutation answer different questions; neither asks "is there signaling."

## Distance-Aware Inference (COMMOT)

**Goal:** Score communication with spatial distance actually in the model, and respect a finite signaling range rather than letting any cluster talk to any cluster.

**Approach:** Optimal transport moves ligand "mass" to receptor "mass" across real coordinates under a per-pathway distance cost; set `dis_thr` to the signaling length scale and handle heteromeric complexes explicitly. Use micron coordinates, not pixels.

```python
import commot as ct

# database= identifiers drift across commot releases -- verify against the installed version
df_ligrec = ct.pp.ligand_receptor_database(database='CellPhoneDB_v4.0', species='human')
ct.tl.spatial_communication(
    adata,
    database_name='cellphonedb',
    df_ligrec=df_ligrec,
    dis_thr=200,                                         # signaling range in COORDINATE UNITS (um) -- one length per pathway, isotropic
    heteromeric=True,                                    # respect multi-subunit complexes (e.g. TGFBR1_TGFBR2)
)
# sender/receiver signaling stored in adata.obsm['commot-cellphonedb-sum-sender'] / '-receiver'
```

`dis_thr` is a single characteristic length applied isotropically -- it cannot distinguish a contact-only pair from a diffusing cytokine, so set it per pathway when secreted and juxtacrine pairs are both in play, and report it. Optimal transport gives a directional, competition-aware map, but "transport" is a model device, not measured flux.

## Visualize and Audit

**Goal:** Inspect top pairs while keeping the spillover and panel caveats visible.

**Approach:** Plot the ligrec dotplot for chosen sender/receiver groups, then overlay the actual ligand and receptor expression in space to eyeball whether a "hit" sits exactly at a cell-type boundary (the spillover signature).

```python
sq.pl.ligrec(res, source_groups='Endothelium', alpha=0.05, swap_axes=True)
```

If a short-range hit localizes to the seam between two touching cell types, suspect transcript spillover before signaling: re-check the segmentation, or test whether the pair survives on a re-segmented (Baysor/proseg) matrix.

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| "Cell type A signals to B via pathway X" written as a finding | Treating an L-R score as validated signaling | Report it as a co-expression hypothesis; climb the confidence ladder (receiver-response, protein co-localization, perturbation) |
| Short-range hit between two touching cell types that vanishes after re-segmentation | Distance-dependent transcript spillover manufactured the co-occurrence | Validate against segmentation quality; re-run on a Baysor/proseg matrix (spatial-transcriptomics/image-analysis) |
| Two tools "confirm" the same interaction | They share the same L-R database, not independent evidence | Report database + version as a primary parameter; vary the resource (Dimitrov 2022) |
| Juxtacrine pair over-called or cytokine missed | One global distance cutoff applied to secreted and contact-dependent pairs alike | Set range per signaling class; interrogate any fixed radius (~500 um is a convention) |
| `sq.gr.ligrec` results look space-aware but are not | ligrec permutes cluster labels -- it is space-blind by default | Use COMMOT/stLearn for distance-modeled inference, or pre-restrict cells to a neighborhood |
| L-R call between two cell types inside one Visium spot | A spot is a 1-10-cell mixture; "cell types" are deconvolution estimates and both genes can live in the same spot | Prefer single-cell-resolution data, or deconvolve then restrict to spots where both types are present; treat spot-level calls as the weakest evidence |
| Hundreds of "significant" pairs at nominal p | No correction over thousands of pair x cell-type-pair tests | Apply BH-FDR over the FULL test space; treat survivors as ranked hypotheses |
| Almost no genes match the database; "no communication found" | Targeted imaging panel (Xenium/MERFISH/CosMx) lacks the relevant ligands/receptors/cofactors | Absence on a panel is uninformative; check panel coverage before concluding |
| `threshold` filters nothing / errors as a p-value | `threshold` is the expression-fraction floor, not a significance cutoff | Set it as a fraction (e.g. 0.01-0.1); filter significance on `pvalues` afterward |
| `ValueError` about `.raw` in ligrec | `use_raw=True` default with no `.raw` present | Pass `use_raw=False` |

## Related Skills

- spatial-transcriptomics/image-analysis - the segmentation-spillover circularity that fabricates short-range L-R hits; validate here first
- spatial-transcriptomics/spatial-neighbors - build the spatial graph that distance-aware methods inherit
- spatial-transcriptomics/spatial-statistics - neighborhood enrichment and permutation-null co-occurrence for which-types-co-occur questions
- spatial-transcriptomics/spatial-domains - annotate the cell types that define senders and receivers
- single-cell/cell-communication - the non-spatial CellPhoneDB/CellChat/NicheNet baseline and database choice
- pathway-analysis/go-enrichment - enrich downstream receiver-response programs (note: enrichment on predicted L-R lists is circular)

## References

- Cang Z, Zhao Y, Almet AA, et al. (2023) Screening cell-cell communication in spatial transcriptomics via collective optimal transport (COMMOT). Nature Methods 20(2):218-228. DOI 10.1038/s41592-022-01728-4
- Dimitrov D, Turei D, Garrido-Rodriguez M, et al. (2022) Comparison of methods and resources for cell-cell communication inference from single-cell RNA-Seq data. Nature Communications 13:3224. DOI 10.1038/s41467-022-30755-0
- Palla G, Spitzer H, Klein M, et al. (2022) Squidpy: a scalable framework for spatial omics analysis. Nature Methods 19(2):171-178. DOI 10.1038/s41592-021-01358-2
- Jin S, Guerrero-Juarez CF, Zhang L, et al. (2021) Inference and analysis of cell-cell communication using CellChat. Nature Communications 12:1088. DOI 10.1038/s41467-021-21246-9
- Browaeys R, Saelens W, Saeys Y (2020) NicheNet: modeling intercellular communication by linking ligands to target genes. Nature Methods 17(2):159-162. DOI 10.1038/s41592-019-0667-5
- Pham D, Tan X, Balderson B, et al. (2023) Robust mapping of spatiotemporal trajectories and cell-cell interactions in healthy and diseased tissues (stLearn). Nature Communications 14:7739. DOI 10.1038/s41467-023-43120-6
- Tanevski J, Ramirez Flores RO, Gabor A, et al. (2022) Explainable multiview framework for dissecting spatial relationships from highly multiplexed data (MISTy). Genome Biology 23:97. DOI 10.1186/s13059-022-02663-5
- Mitchel J, Gao T, Petukhov V, et al. (2026) Impact and correction of segmentation errors in spatial transcriptomics. Nature Genetics 58:434-444. DOI 10.1038/s41588-025-02497-4
- Armingol E, Officer A, Harismendy O, Lewis NE (2021) Deciphering cell-cell interactions and communication from gene expression. Nature Reviews Genetics 22(2):71-88. DOI 10.1038/s41576-020-00292-x
<!-- END FILE: spatial-transcriptomics/spatial-communication/SKILL.md -->

## 子目录：spatial-transcriptomics/spatial-data-io

<!-- BEGIN FILE: spatial-transcriptomics/spatial-data-io/SKILL.md -->
---
name: bio-spatial-transcriptomics-spatial-data-io
description: Loads spatial transcriptomics data from Visium, Visium HD, Xenium, MERFISH/MERSCOPE, CosMx, Slide-seq/Curio, and Stereo-seq into AnnData or SpatialData using spatialdata-io and Squidpy. Use when deciding which platform class is in hand (imaging/in-situ vs sequencing/capture), which reader matches the platform (spatialdata_io.xenium/merscope/cosmx vs squidpy.read.visium/vizgen/nanostring), whether to work from the per-transcript molecule table (the re-segmentable source of truth) or the segmentation-derived per-cell matrix (quality-filtered, inherits all segmentation error), whether a molecule table even exists (spot platforms have none), and how to keep coordinate frames and units (pixel vs micron) registered to histology.
tool_type: python
primary_tool: spatialdata
---

## Version Compatibility

Reference examples tested with: spatialdata 0.2+, spatialdata-io 0.1.5+, squidpy 1.4+, scanpy 1.10+, anndata 0.10+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Spatial Data I/O

**"Load my spatial data"** -> Parse a platform's output bundle into one coordinate frame holding the expression matrix, coordinates, images, and (for imaging) the molecule table and segmentation shapes.
- Imaging/in-situ (Xenium, MERSCOPE/MERFISH, CosMx, seqFISH): `spatialdata_io.{xenium, merscope, cosmx}` -> SpatialData with a per-transcript `points` table AND a derived per-cell `tables` matrix.
- Sequencing/capture (Visium, Visium HD, Slide-seq/Curio, Stereo-seq): `squidpy.read.visium` or `spatialdata_io.{visium, visium_hd, curio, stereoseq}` -> spot/bin matrix + coordinates; NO molecule table.

## Governing Principle

The single most consequential I/O fact is that the two platform classes emit different primary objects, and one class emits two of them that are easy to confuse.

Imaging/in-situ platforms emit TWO physically distinct primary objects. The first is a per-TRANSCRIPT molecule table -- one row per decoded molecule with x, y (and often z), gene, a decoding-quality value, and a cell-assignment-or-unassigned. The second is a per-CELL expression matrix, genes-by-cells, DERIVED by overlaying a segmentation and counting the molecules that fall inside each boundary. The matrix looks exactly like scRNA-seq and is therefore wrongly trusted as ground truth, but it is a downstream product: it inherits every segmentation error and is usually quality-filtered (Xenium keeps Q>=20 in the matrix while the transcript table keeps everything). The molecule table is the source of truth and the ONLY object that lets the analyst re-segment, recover unassigned molecules, or do subcellular work. A loader that returns only the cell matrix has silently discarded the re-segmentable layer.

Sequencing/capture platforms (Visium, Slide-seq, Stereo-seq) have NO molecule table -- a spot/bead/bin is mini-bulk over the cells beneath it, captured as a single barcoded profile. Do not go looking for a transcript table that does not exist; the only objects are the barcode-by-gene matrix, the coordinates, and the tissue image.

A second trap is coordinate frames. Images, spot/cell coordinates, and molecule points each live in their own intrinsic pixel or array axes; overlaying transcripts on histology, or building a neighbor graph with a micron radius, requires the right transform (Visium scalefactors; imaging micron-to-pixel matrices). SpatialData makes the frames explicit (intrinsic vs a shared extrinsic "global" system); the legacy AnnData layout hides them in `uns['spatial'][library_id]['scalefactors']`. Mixing frames silently places points off the image or builds a graph at the wrong scale.

## The Platform-Class Fork

The first question of any spatial dataset is which side of the fork it sits on, because it decides what objects exist and what the rest of the pipeline must do.

| Class | Platforms | Primary objects | Molecule table? | Cell unit | Downstream |
|---|---|---|---|---|---|
| Imaging / in-situ | Xenium, MERSCOPE/MERFISH, CosMx, seqFISH | molecule table + segmentation-derived cell matrix + images + shapes | YES (source of truth) | from segmentation (a hypothesis) | segment, then label-transfer typing |
| Sequencing / capture | Visium, Visium HD, Slide-seq/Curio, Stereo-seq, GeoMx | barcode/bin-by-gene matrix + coordinates + image | NO | spot/bin = 1-10-cell MIXTURE (GeoMx ROI = many-cell region; sub-cell bins = fraction of a cell) | deconvolution (or bin/segment-up for sub-cell bins) |

## Object-Model Landscape

Each toolkit is a strategy for co-storing four things in one frame: an expression matrix, geometry (spot circles, cell/nucleus polygons, centroids), raster images (H&E, DAPI, multiplex IF -- often gigapixel), and (imaging only) the molecule point cloud. They differ in how separately they keep these and which is the forward path.

| Framework (language) | Core object | Molecule table | Per-cell matrix | Segmentation geometry | Images | Best when |
|---|---|---|---|---|---|---|
| SpatialData / scverse (Python) | `SpatialData` of elements | `points` (dask -> Parquet) | `tables` (AnnData) | `labels` (masks) + `shapes` (geopandas polygons) | `images` (xarray, OME-NGFF/Zarr, lazy) | Multimodal, larger-than-memory, multiple platforms in one store; re-segmentation |
| Squidpy + AnnData (Python) | `AnnData` | via SpatialData/readers | `adata.X` | in `obs`/external | `uns['spatial']` (legacy) | Standard AnnData spatial graph stats on spot or cell matrices |
| Seurat v5 (R) | `Seurat`, geometry in `@images` | `FOV@molecules` | `Assay5` counts | `FOV@boundaries` (Centroids + Segmentation) | platform `SpatialImage` | R single-cell users; v5 integration |
| SpatialExperiment / SFE-Voyager (Bioc, R) | `SpatialExperiment` / `SpatialFeatureExperiment` | `rowGeometries` (sf points, SFE only) | SCE assay | `colGeometries` (cellSeg/nucSeg/spotPoly) | `imgData()` | Bioconductor scran/scater; geospatial ESDA (Moran's I) |
| Giotto Suite (R) | `giotto` (multi-scale) | subcellular molecule layer | aggregated cell layer | polygon/cell layers | image layers | One technology-agnostic object spanning molecule -> cell -> region |

SpatialData is the forward-path Python standard because it is the only framework that natively keeps the molecule table, multiscale OME-NGFF images, and segmentation shapes as first-class, frame-aware elements. Because a SpatialData `table` IS an AnnData, all of `squidpy.gr.*` runs on it unchanged.

## Platform-to-Reader Map

| Platform | spatialdata-io reader | squidpy.read | Key I/O fact |
|---|---|---|---|
| Visium | `visium` | `visium` | spot, no molecule table; `tissue_positions.csv` gained a header at Space Ranger v2.0 (readers handle both) |
| Visium HD | `visium_hd` | -- | bins (2/8/16um); `tissue_positions.parquet` (PARQUET, not CSV); 8um bin still spans ~2 cells |
| Xenium | `xenium` | -- (none) | molecule table `transcripts.parquet` (all Q) + Q>=20 cell matrix; needs `experiment.xenium` manifest |
| MERSCOPE / MERFISH | `merscope` | `vizgen` | there is NO `merfish` reader -- `merscope` handles both; boundaries went hdf5-folder -> single `cell_boundaries.parquet` at instrument SW v232 |
| CosMx | `cosmx` | `nanostring` | flat CSVs with a run/slide prefix; `tx_file` (molecule table) absent for protein-only panels |
| Slide-seq / Curio | `curio` | -- (none) | bead, no molecule table |
| Stereo-seq | `stereoseq` | -- | DNB sub-cellular; binned up to cells |

`squidpy.read` provides ONLY `visium`, `vizgen`, and `nanostring` -- it has no `xenium` or `slideseq` reader. For Xenium, Slide-seq/Curio, Stereo-seq, and Visium HD, use the `spatialdata_io` reader. `scanpy.read_visium` is deprecated as of scanpy 1.11 -- prefer `squidpy.read.visium` (identical obsm/uns layout) or `spatialdata_io.visium`.

## Load Visium (Spot/Capture)

**Goal:** Read a Space Ranger bundle into an AnnData with coordinates, image, and scalefactors, without reaching for the deprecated scanpy reader.

**Approach:** Use `squidpy.read.visium`; coordinates land in `obsm['spatial']` (pixels of the full-res image), image and scalefactors in `uns['spatial'][library_id]`.

```python
import squidpy as sq

adata = sq.read.visium('spaceranger_out/')         # filtered matrix + spatial/; NOT a cell -- each spot is a 1-10-cell mixture
library_id = list(adata.uns['spatial'].keys())[0]
scalef = adata.uns['spatial'][library_id]['scalefactors']
# obsm['spatial'] is in FULL-RES pixels; multiply by tissue_hires_scalef to index the hires image
print(adata.n_obs, 'spots', adata.n_vars, 'genes', '| spot diameter (px):', scalef['spot_diameter_fullres'])
```

## Load Imaging Data and Keep the Molecule Table

**Goal:** Load Xenium (or MERSCOPE/CosMx) so BOTH the per-transcript molecule table and the derived cell matrix are available, not just the matrix.

**Approach:** Use the `spatialdata_io` reader, which returns a SpatialData object; the molecule table lives in `sdata.points`, the cell matrix in `sdata.tables`, segmentation polygons in `sdata.shapes`, images in `sdata.images`. Inspect element names with `print(sdata)` -- they vary by platform and reader version.

```python
import spatialdata_io as sdio

sdata = sdio.xenium('xenium_out/')                 # needs experiment.xenium manifest
print(sdata)                                       # lists points/tables/shapes/images element names

transcripts = sdata.points['transcripts']          # dask DataFrame: x, y, z, feature_name, qv, cell_id -- ALL Q-scores
adata = sdata.tables['table']                      # AnnData cell matrix -- Q>=20 filtered, inherits segmentation error
# the matrix is a DERIVED product; the molecule table is the re-segmentable source of truth
print('molecules:', transcripts.shape[0].compute(), '| cells in matrix:', adata.n_obs)
```

For MERSCOPE substitute `sdio.merscope('merscope_out/')`; for CosMx `sdio.cosmx('cosmx_out/')`. As an AnnData-only alternative for MERSCOPE, `sq.read.vizgen(path, counts_file='cell_by_gene.csv', meta_file='cell_metadata.csv')` returns the cell matrix but discards the molecule table.

## Load Other Capture Platforms

**Goal:** Load Visium HD bins, Slide-seq/Curio beads, or Stereo-seq into a SpatialData object.

**Approach:** Use the matching `spatialdata_io` reader; none of these has a molecule table, and Visium HD / Stereo-seq bins are smaller than a cell (the inverse-of-deconvolution regime -- see spatial-deconvolution).

```python
import spatialdata_io as sdio

sdata_hd = sdio.visium_hd('visium_hd_out/')        # tissue_positions are PARQUET; pick a bin (8um default still ~2 cells)
sdata_ss = sdio.stereoseq('stereoseq_out/')        # DNB sub-cellular spots, binned up to cells
sdata_bead = sdio.curio('slideseq_out/')           # Slide-seq/Curio beads; ~1 cell but ~1/3 carry >=2 types
```

## Inspect and Register Coordinate Frames

**Goal:** Confirm whether coordinates are in pixels or microns before building a graph or overlaying on histology, so a neighbor radius or a plotted point lands at the right scale.

**Approach:** In SpatialData read the element transformations (intrinsic vs the shared "global" extrinsic frame); in the AnnData layout read the scalefactors. Never assume `obsm['spatial']` units -- Visium is full-res pixels, most imaging readers place a micron "global" frame.

```python
from spatialdata.transformations import get_transformation

# SpatialData: every element carries transforms into shared coordinate systems
print(sdata.coordinate_systems)                    # e.g. ['global']
print(get_transformation(sdata['transcripts'], get_all=True))   # intrinsic -> global (often micron scaling)
```

## Convert SpatialData to AnnData

**Goal:** Extract the cell/spot matrix as a plain AnnData for tools that expect one, while keeping coordinates.

**Approach:** Copy the `table`, set `obsm['spatial']` from the matching shapes/centroids. Persist via `sdata.write(...)` ONLY to a scratch path -- a `.zarr` store is a DIRECTORY, not a file, so it must never be committed.

```python
adata = sdata.tables['table'].copy()
# write a zarr STORE (a directory) to scratch, never the repo; rm -rf when done
# sdata.write('/tmp/scratch/store.zarr')
```

## Common Errors

| Symptom | Cause | Fix |
|---|---|---|
| `AttributeError: module 'squidpy.read' has no attribute 'xenium'` (or `slideseq`) | `squidpy.read` only has `visium`, `vizgen`, `nanostring` | Use `spatialdata_io.xenium` / `spatialdata_io.curio` for those platforms |
| `spatialdata_io` has no `merfish` reader | The reader is named for the instrument, not the chemistry | Use `spatialdata_io.merscope` (handles MERFISH and MERSCOPE) |
| `DeprecationWarning` / future removal on `scanpy.read_visium` | Deprecated as of scanpy 1.11 | Use `squidpy.read.visium` or `spatialdata_io.visium` (same layout) |
| Cell matrix has far fewer transcripts than the molecule table | Imaging cell matrix is Q>=20 filtered and segmentation-derived | Treat the matrix as provisional; use `sdata.points` (all Q) to re-segment or audit |
| Trusting the cell matrix as ground truth; weird co-expression | The matrix inherits all segmentation/spillover error | Validate against the molecule table; re-segment (see image-analysis) |
| Looking for a transcript table in Visium/Slide-seq and finding none | Capture platforms have no molecule table | Stop -- a spot is mini-bulk; there is nothing to re-segment |
| Visium HD reader fails reading `tissue_positions.csv` | Visium HD positions are PARQUET (`tissue_positions.parquet`) | Use `spatialdata_io.visium_hd`, which expects the parquet bundle |
| Older Visium positions parse with a shifted header | `tissue_positions.csv` gained a header at Space Ranger v2.0 | Current readers handle both; upgrade `spatialdata-io`/`squidpy` if parsing legacy files |
| MERSCOPE boundaries not found | hdf5-folder boundaries became single `cell_boundaries.parquet` at SW v232 | Match reader version to instrument software; point at the parquet if present |
| Seurat `@coordinates` slot missing (R interop) | Seurat 5.1 `VisiumV2` has no `coordinates` slot (V1 did) | Use `GetTissueCoordinates()`; there is no V1->V2 converter |
| Transcripts plot off the image | Points and image in different frames/units (pixel vs micron) | Apply the reader's transform / scalefactor before overlaying |
| A stray `.zarr` directory left in the repo after writing | `sdata.write` makes a directory store; `git status` hides untracked dirs | Write to scratch; `rm -rf` the store; run `git status --porcelain | grep '/$'` |

## Related Skills

- spatial-preprocessing - QC floors and normalization that differ by platform class after loading
- image-analysis - re-segment the molecule table; the cell matrix is a segmentation hypothesis
- spatial-deconvolution - recover cell-type proportions from spot mixtures that have no molecule table
- high-resolution-binning - bin/segment-up sub-cellular Visium HD and Stereo-seq captures
- spatial-visualization - plot spots vs imaging FOVs with the correct coordinate frame
- single-cell/data-io - non-spatial scRNA-seq loading for the deconvolution/label-transfer reference

## References

- Marconato L, Palla G, Yamauchi KA, et al. (2025) SpatialData: an open and universal data framework for spatial omics. Nature Methods 22(1):58-62. DOI 10.1038/s41592-024-02212-x
- Palla G, Spitzer H, Klein M, et al. (2022) Squidpy: a scalable framework for spatial omics analysis. Nature Methods 19(2):171-178. DOI 10.1038/s41592-021-01358-2
- Wolf FA, Angerer P, Theis FJ (2018) SCANPY: large-scale single-cell gene expression data analysis. Genome Biology 19:15. DOI 10.1186/s13059-017-1382-0
- Virshup I, Rybakov S, Theis FJ, Angerer P, Wolf FA (2024) anndata: Access and store annotated data matrices. Journal of Open Source Software 9(101):4371. DOI 10.21105/joss.04371
- Hao Y, Stuart T, Kowalski MH, et al. (2024) Dictionary learning for integrative, multimodal and scalable single-cell analysis. Nature Biotechnology 42(2):293-304. DOI 10.1038/s41587-023-01767-y
- Righelli D, Weber LM, Crowell HL, et al. (2022) SpatialExperiment: infrastructure for spatially-resolved transcriptomics data in R using Bioconductor. Bioinformatics 38(11):3128-3131. DOI 10.1093/bioinformatics/btac299
- Moore J, Allan C, Besson S, et al. (2021) OME-NGFF: a next-generation file format for expanding bioimaging data-access strategies. Nature Methods 18:1496-1498. DOI 10.1038/s41592-021-01326-w
- Janesick A, Shelansky R, Gottscho AD, et al. (2023) High resolution mapping of the tumor microenvironment using integrated single-cell, spatial and in situ analysis (Xenium). Nature Communications 14:8353. DOI 10.1038/s41467-023-43458-x
<!-- END FILE: spatial-transcriptomics/spatial-data-io/SKILL.md -->

## 子目录：spatial-transcriptomics/spatial-deconvolution

<!-- BEGIN FILE: spatial-transcriptomics/spatial-deconvolution/SKILL.md -->
---
name: bio-spatial-transcriptomics-spatial-deconvolution
description: Estimates per-spot cell type composition of spatial transcriptomics mixtures (Visium, Slide-seq, Stereo-seq) from an scRNA-seq reference with cell2location, RCTD, SPOTlight, stereoscope, SpatialDWLS, or reference-free STdeconvolve. Use when deciding whether a platform even needs deconvolution (the resolution fork -- a 55um Visium spot is a 1-10-cell MIXTURE -> deconvolve, but a Xenium/MERFISH/CosMx cell is already single -> segment instead, and running deconvolution there invents fractions that do not exist); choosing cell2location (absolute abundance) vs RCTD/SPOTlight/stereoscope/SpatialDWLS (proportions only) by output and runtime; matching the scRNA reference to tissue and condition (the reference IS the result -- a missing cell type is silently misassigned to its nearest neighbor with no error flag); and handling compositional outputs that sum to 1 with CLR/ILR rather than naive per-type t-tests.
tool_type: python
primary_tool: cell2location
---

## Version Compatibility

Reference examples tested with: cell2location 0.1.4+, scvi-tools 1.0+, scanpy 1.10+, anndata 0.10+, numpy 1.26+

RCTD/SPOTlight/STdeconvolve are R packages (spacexr, SPOTlight, STdeconvolve via Bioconductor); call them from R or via rpy2.

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Spatial Deconvolution

**"What cell types are in each spot?"** -> Decompose a multi-cell capture spot into the fractions (or absolute numbers) of each cell type, using an annotated scRNA-seq reference as the basis.
- Python: cell2location (`RegressionModel` -> `Cell2location`), stereoscope/DestVI (scvi-tools), Tangram (`tg.map_cells_to_space`), STdeconvolve (reference-free, R)
- R: RCTD (`spacexr::create.RCTD`/`run.RCTD`), SPOTlight, SpatialDWLS (Giotto), CARD

The operation BRANCHES on the platform before any tool is chosen. The first question is not "which method" but "does this data even contain mixtures?" -- answered by the resolution fork below.

## The resolution fork

Deconvolution recovers the cell-type composition of a MIXTURE. Whether a mixture exists is set by the capture unit size relative to a mammalian cell (~8-30um diameter), and it sorts every dataset into three regimes. Choosing the wrong regime is the most expensive error in spatial analysis -- far more damaging than picking the second-best method within a regime.

| Platform | Unit size | Single cell? | Regime |
|----------|-----------|--------------|--------|
| Visium v1/v2 | 55um spot, 100um pitch | No (~1-10+ cells/spot) | DECONVOLVE |
| GeoMx DSP | region of interest | No (many cells) | DECONVOLVE (SpatialDecon) |
| Visium HD | 2um bins, analyzed at 8/16um | 8um still mixes cells | AMBIGUOUS (reconstruct OR deconvolve) |
| Stereo-seq | ~220nm spots, binned (bin50/bin100) | binned to cell scale | AMBIGUOUS |
| Slide-seqV2 | 10um beads | near single-cell | AMBIGUOUS (RCTD doublet-mode common) |
| Xenium | transcript point cloud + DAPI | YES (segmented) | SEGMENT + annotate -- do NOT deconvolve |
| MERFISH / MERSCOPE | subcellular | YES | SEGMENT + annotate -- do NOT deconvolve |
| CosMx SMI | subcellular | YES | SEGMENT + annotate -- do NOT deconvolve |

- DECONVOLVE: a capture array has no per-transcript cell assignment, so the spot is an unavoidable mixture and only mixture modeling recovers composition. The H&E underlay can count nuclei but cannot say which transcript came from which cell.
- SEGMENT (imaging platforms): the data are already single cells. The work is segmentation (assign transcripts to cells) then annotation (cluster + markers, or label-transfer). Running deconvolution here is conceptually WRONG -- it fabricates fractional mixtures inside cells that are already pure. See image-analysis for segmentation and single-cell/cell-annotation for label transfer.
- AMBIGUOUS (the near-single-cell middle): bins/beads still hold partial or multiple cells. When a high-quality registered image exists (Visium HD), morphology-driven cell RECONSTRUCTION (Bin2cell, StarDist/Cellpose nuclei expansion) is increasingly preferred over treating bins as fixed mixtures; without per-bead morphology (Slide-seqV2), assignment/deconvolution (often RCTD doublet-mode) remains standard. No settled consensus -- see high-resolution-binning.

## Governing Principle

A deconvolution result is a PROJECTION of the single-cell reference onto the spatial data. The reference is not a neutral input -- it is the dominant determinant of the answer, more than the algorithm.

The #1 trap is the missing or mismatched cell type. If a real type is ABSENT from the reference, its transcripts are forced onto the transcriptionally nearest type that IS present. The proportions still sum to 1 and look clean, and there is no internal warning -- garbage reference produces confident garbage proportions. The reference must match the TISSUE, the CONDITION (a healthy reference mis-estimates activated-immune or malignant states whose expression has shifted), and ideally the technology/protocol (snRNA-seq vs whole-cell dissociation bias propagates straight into the numbers). The reference is NOT ground truth.

Every benchmark reinforces the same lesson: reference quality and the cell-type abundance pattern swing results MORE than method choice, and a plain NNLS baseline outperforms nearly half the dedicated methods (Sang-Aram 2024 *eLife* 12:RP88431; Li 2022 *Nat Methods* 19:662-670). Method-shopping is the wrong lever; reference quality is the right one. Rare-type fractions (below a few percent) are the least reliable numbers in the output -- corroborate any rare type with its spatial marker genes before believing it. More tools is not more confidence: two NB-regression methods agreeing is pseudo-replication, not orthogonal validation. The defensible confidence move is reference-sensitivity analysis (perturb or swap the reference) plus an orthogonal modality.

Outputs are COMPOSITIONAL: per-spot proportions live on a simplex (sum to 1), so an increase in one type mechanically decreases the others. Downstream comparison must use CLR/ILR or compositional tests -- naive per-type t-tests/correlations on raw proportions are mis-specified.

## Choosing a method

The first axis is output: cell2location uniquely returns ABSOLUTE cell abundance (expected cell numbers per spot); the rest return proportions only. "Number of cells of type X" and "fraction of the spot that is type X" answer different biological questions. The second axis is runtime and whether spatial coordinates or a platform-shift correction are modeled. When competing methods exist, verify current best practice against the latest benchmark before committing -- this field moves fast.

| Method | Model | Reference | Output | Best when | Fails when |
|--------|-------|-----------|--------|-----------|------------|
| cell2location | Bayesian hierarchical NB (variational, pyro/scvi-tools) | yes | ABSOLUTE abundance | absolute counts wanted; large atlases; models platform shift | GPU-light setups (slow VI); over-trusting rare types |
| RCTD (spacexr) | Poisson + per-gene platform-effect random effect | yes | proportions | fast, widely used; doublet-mode for Slide-seq/high-res | non-R pipelines without rpy2 |
| stereoscope | Negative-binomial MLE of spot mixtures | yes | proportions | principled NB; in scvi-tools | speed (among slowest) |
| SPOTlight | Seeded NMF + NNLS | yes | proportions | fast, transparent, R/Bioconductor | mid-pack accuracy |
| SpatialDWLS | Dampened weighted least squares + marker enrichment | yes | proportions | fastest tier; consistently top in Li 2022 | needs Giotto |
| CARD | CAR-prior spatially-informed NMF regression | yes (can run ref-free) | proportions (smoothed) | spatially structured tissue; coordinates help | sharp composition boundaries (over-smooths) |
| Tangram | Deep-learning alignment (cell->voxel mapping) | yes | mapping (proportions as by-product) | transcript imputation; flexible platforms | pure proportion accuracy (it is a mapper) |
| STdeconvolve | Reference-FREE LDA topic model | NO | proportions + topic profiles | no matched reference exists; sanity check | types co-occurring in fixed ratios; topics need post-hoc annotation |

cell2location and RCTD are reliably top-tier across independent benchmarks (Li 2022; Sang-Aram 2024; *Nat Commun* 2023 14:1548). When no matched reference exists, STdeconvolve is the escape hatch -- it is immune to the missing-type trap because it uses no reference, but its topics are de novo and must be annotated afterward.

## cell2location step 1: reference signatures

**Goal:** Learn each cell type's per-gene expression signature from the annotated scRNA-seq reference, correcting for the technical/batch structure of the reference.

**Approach:** Filter genes to informative ones, fit a negative-binomial RegressionModel with the cell-type label and any batch as covariates, then export the posterior per-cluster mean expression. cell2location consumes RAW integer counts -- do NOT pass log-normalized data.

```python
import cell2location
import numpy as np
import scanpy as sc
from cell2location.utils.filtering import filter_genes
from cell2location.models import RegressionModel

adata_ref = sc.read_h5ad('reference_scrna.h5ad')           # raw counts in .X
adata_ref.obs['cell_type'] = adata_ref.obs['cell_type'].astype('category')

selected = filter_genes(adata_ref, cell_count_cutoff=5, cell_percentage_cutoff2=0.03, nonz_mean_cutoff=1.12)
adata_ref = adata_ref[:, selected].copy()

# batch_key absorbs technical structure across reference samples; drop if a single batch
RegressionModel.setup_anndata(adata_ref, labels_key='cell_type', batch_key='sample')
mod = RegressionModel(adata_ref)
mod.train(max_epochs=250, accelerator='gpu')               # use_gpu= is deprecated; accelerator in {'gpu','cpu','auto'}
adata_ref = mod.export_posterior(adata_ref, sample_kwargs={'num_samples': 1000})

factors = adata_ref.uns['mod']['factor_names']
if 'means_per_cluster_mu_fg' in adata_ref.varm:
    inf_aver = adata_ref.varm['means_per_cluster_mu_fg'][[f'means_per_cluster_mu_fg_{f}' for f in factors]].copy()
else:
    inf_aver = adata_ref.var[[f'means_per_cluster_mu_fg_{f}' for f in factors]].copy()
inf_aver.columns = factors                                 # genes x cell_types signature matrix
```

## cell2location step 2: spatial mapping

**Goal:** Decompose each spatial spot into absolute cell-type abundances using the reference signatures.

**Approach:** Restrict both objects to shared genes, set up the Cell2location model with the signature matrix and the expected cells-per-spot, then train. N_cells_per_location is a tissue-dependent prior (Visium ~10-30, denser tissue higher); detection_alpha controls within-experiment normalization (20 is the tutorial default; raise toward 200 if technical variability in total counts is high).

```python
adata_vis = sc.read_h5ad('visium.h5ad')                    # raw counts
shared = np.intersect1d(adata_vis.var_names, inf_aver.index)
adata_vis = adata_vis[:, shared].copy()
inf_aver = inf_aver.loc[shared, :]

cell2location.models.Cell2location.setup_anndata(adata_vis, batch_key='sample')
mod_sp = cell2location.models.Cell2location(adata_vis, cell_state_df=inf_aver,
                                            N_cells_per_location=30, detection_alpha=20)
mod_sp.train(max_epochs=30000, batch_size=None, train_size=1, accelerator='gpu')
adata_vis = mod_sp.export_posterior(adata_vis, sample_kwargs={'num_samples': 1000, 'batch_size': mod_sp.adata.n_obs})

# q05 = 5% posterior quantile = 'at least this many cells of this type are present' (conservative)
abundance = adata_vis.obsm['q05_cell_abundance_w_sf']      # ABSOLUTE expected cell numbers per spot
abundance.columns = factors
adata_vis.obs[abundance.columns] = abundance.values
```

cell2location returns absolute abundances. Convert to proportions only if proportions are the question -- doing so discards the information that distinguishes cell2location from the proportion-only methods.

## Handling compositional outputs

**Goal:** Compare cell-type composition across spots, regions, or conditions without the spurious negative correlations that the sum-to-1 constraint manufactures.

**Approach:** Map proportions out of the simplex with the centered log-ratio (CLR) before any correlation, t-test, or linear model. Add a small pseudocount because CLR is undefined at zero.

```python
import numpy as np

def clr(proportions, pseudocount=1e-6):
    p = proportions + pseudocount
    p = p / p.sum(axis=1, keepdims=True)
    log_p = np.log(p)
    return log_p - log_p.mean(axis=1, keepdims=True)       # subtract per-spot geometric-mean log

abund = adata_vis.obsm['q05_cell_abundance_w_sf'].values
proportions = abund / abund.sum(axis=1, keepdims=True)
clr_comp = clr(proportions)                                # now safe for downstream correlation / DE / t-tests
```

For differential abundance between conditions, prefer a compositional method (ALDEx2, scCODA, or a Dirichlet-multinomial model) over per-type t-tests on raw fractions; the same closed-data logic that breaks naive correlations breaks naive DA.

## Reference-free sanity check

**Goal:** Detect a missing-reference-type problem and recover composition when no matched scRNA-seq reference exists.

**Approach:** Run STdeconvolve (LDA topic model, R) on the spatial data alone, then check whether any de novo topic matches no reference cell type -- a topic with strong spatial structure and marker genes for a type absent from the reference is direct evidence the reference is incomplete.

```r
library(STdeconvolve)
counts <- cleanCounts(spatial_counts_matrix, min.lib.size = 100)   # genes x spots
corpus <- restrictCorpus(counts, removeAbove = 1.0, removeBelow = 0.05)
ldas <- fitLDA(t(as.matrix(corpus)), Ks = seq(8, 15))              # K = number of topics, scan a range
opt <- optimalModel(models = ldas, opt = 'min')
res <- getBetaTheta(opt, perc.filt = 0.05)
deconv_prop <- res$theta                                          # spots x topics proportions
# annotate topics post hoc via res$beta (topic gene profiles) against known markers
```

## Validating against marker genes

**Goal:** Confirm that an estimated cell-type fraction tracks the in-situ expression of that type's canonical markers, not the reference's wishful thinking.

**Approach:** For each type, correlate its estimated proportion across spots with the mean spatial expression of its marker genes; weak or negative correlation flags a misassignment or a reference mismatch.

```python
markers = {'T_cell': ['CD3D', 'CD3E', 'CD8A'], 'Macrophage': ['CD68', 'CD14', 'CSF1R'], 'Epithelial': ['EPCAM', 'KRT8']}
for ct, genes in markers.items():
    present = [g for g in genes if g in adata_vis.var_names]
    if not present or ct not in proportions_df.columns:
        continue
    expr = np.asarray(adata_vis[:, present].X.mean(axis=1)).ravel()
    corr = np.corrcoef(expr, proportions_df[ct].values)[0, 1]
    print(f'{ct}: marker-vs-proportion r = {corr:.3f}')        # low r -> suspect reference or misassignment
```

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| Deconvolution "works" on Xenium/MERFISH/CosMx but fractions are nonsensical | Ran deconvolution on single-cell-resolution imaging data, inventing mixtures inside pure cells | Segment then annotate (image-analysis, single-cell/cell-annotation); deconvolution does not apply |
| A histologically present cell type appears in NO spot | Type is absent from the reference; its signal was silently reassigned to the nearest present type | Add the missing type to the reference; cross-check with STdeconvolve for an unmatched topic |
| Confident proportions, but disease/activated states look wrong | Condition mismatch -- healthy reference deconvolving diseased tissue | Use a condition-matched reference; activated/malignant states are transcriptionally far from healthy |
| Per-type t-test finds "everything changes oppositely" | Naive test on compositional (sum-to-1) proportions creates spurious negative correlation | CLR/ILR transform first; use ALDEx2/scCODA/Dirichlet-multinomial for differential abundance |
| Rare cell type fraction swings wildly between runs/references | Rare-type fractions are the least reliable output; abundance-pattern sensitivity | Treat <few-percent fractions skeptically; corroborate with spatial markers; do reference-sensitivity analysis |
| `ValueError`/garbage from cell2location after normalizing | Passed log-normalized data; cell2location needs RAW integer counts | Feed raw counts; stash normalized layers separately |
| `TypeError: unexpected keyword 'use_gpu'` | `use_gpu` deprecated in current scvi-tools | Use `accelerator='gpu'` (or 'cpu'/'auto') |
| Two methods agree, reported as validation | Two NB-regression methods are pseudo-replication, not orthogonal | Validate by perturbing the reference and against an orthogonal modality (matched imaging, in-situ markers) |
| Every spot contains a little of every immune type | Spot-edge transcript spillover / diffusion inflates apparent co-localization | RCTD doublet-mode or spillover-aware segmentation; treat ubiquitous low fractions with suspicion |

## Related Skills

- spatial-domains - group spots into tissue regions; a domain is a region, not a cell type or a niche
- high-resolution-binning - the AMBIGUOUS regime (Visium HD, Stereo-seq, Slide-seq): reconstruct cells vs deconvolve bins
- image-analysis - segment cells from imaging platforms, where deconvolution does not apply
- single-cell/cell-annotation - annotate the imaging cells after segmentation, and label the scRNA-seq reference
- single-cell/preprocessing - build a clean reference; the reference IS the result
- spatial-preprocessing - QC and normalize the spatial data before deconvolution
- spatial-visualization - map estimated proportions and abundances onto the tissue

## References

- Kleshchevnikov V, Shmatko A, Dann E, et al. (2022) Cell2location maps fine-grained cell types in spatial transcriptomics. Nature Biotechnology 40:661-671. DOI 10.1038/s41587-021-01139-4
- Cable DM, Murray E, Zou LS, et al. (2022) Robust decomposition of cell type mixtures in spatial transcriptomics (RCTD). Nature Biotechnology 40:517-526. DOI 10.1038/s41587-021-00830-w
- Andersson A, Bergenstrahle J, Asp M, et al. (2020) Single-cell and spatial transcriptomics enables probabilistic inference of cell type topography (stereoscope). Communications Biology 3:565. DOI 10.1038/s42003-020-01247-y
- Elosua-Bayes M, Nieto P, Mereu E, Gut I, Heyn H (2021) SPOTlight: seeded NMF regression to deconvolute spatial transcriptomics spots with single-cell transcriptomes. Nucleic Acids Research 49(9):e50. DOI 10.1093/nar/gkab043
- Biancalani T, Scalia G, Buffoni L, et al. (2021) Deep learning and alignment of spatially resolved single-cell transcriptomes with Tangram. Nature Methods 18(11):1352-1362. DOI 10.1038/s41592-021-01264-7
- Ma Y, Zhou X (2022) Spatially informed cell-type deconvolution for spatial transcriptomics (CARD). Nature Biotechnology 40:1349-1359. DOI 10.1038/s41587-022-01273-7
- Dong R, Yuan GC (2021) SpatialDWLS: accurate deconvolution of spatial transcriptomic data. Genome Biology 22:145. DOI 10.1186/s13059-021-02362-7
- Miller BF, Huang F, Atta L, Sahoo A, Fan J (2022) Reference-free cell type deconvolution of multi-cellular pixel-resolution spatially resolved transcriptomics data (STdeconvolve). Nature Communications 13:2339. DOI 10.1038/s41467-022-30033-z
- Sang-Aram C, Browaeys R, Seurinck R, Saeys Y (2024) Spotless, a reproducible pipeline for benchmarking cell type deconvolution in spatial transcriptomics. eLife 12:RP88431. DOI 10.7554/eLife.88431
- Li B, Zhang W, Guo C, et al. (2022) Benchmarking spatial and single-cell transcriptomics integration methods for transcript distribution prediction and cell type deconvolution. Nature Methods 19:662-670. DOI 10.1038/s41592-022-01480-9
<!-- END FILE: spatial-transcriptomics/spatial-deconvolution/SKILL.md -->

## 子目录：spatial-transcriptomics/spatial-domains

<!-- BEGIN FILE: spatial-transcriptomics/spatial-domains/SKILL.md -->
---
name: bio-spatial-transcriptomics-spatial-domains
description: Identify spatially coherent tissue domains (regions like cortical layers, tumor vs stroma) in Visium, Visium HD, Xenium, MERFISH, Slide-seq, and Stereo-seq data with Squidpy, BANKSY, BayesSpace, STAGATE, and GraphST. Use when distinguishing a domain (a region with many cell types) from a cell type (one cell's identity) and a niche (local cell-type composition); choosing a domain method by tissue geometry (laminar/continuous vs high-resolution imaging vs non-contiguous); tuning the spatial-weight knob (BANKSY lambda, BayesSpace smoothing, SpaGCN histology weight, GNN graph radius) to avoid over-smoothing into blobs or under-smoothing into salt-and-pepper; choosing the number of domains k as a biological decision with k+-1 sensitivity; and reading the Yuan 2024 benchmark with the DLPFC continuous-laminar caveat.
tool_type: python
primary_tool: squidpy
---

## Version Compatibility

Reference examples tested with: squidpy 1.4+, scanpy 1.10+, anndata 0.10+, scikit-learn 1.4+; BANKSY (banksy_py / R Banksy), BayesSpace 1.12+ (R), STAGATE/GraphST optional

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Spatial Domain Detection

**"Identify tissue domains in my section"** -> Partition the tissue into spatially contiguous regions of homogeneous expression/composition, using BOTH transcriptional similarity AND spatial proximity, so the output is a region label per spot/cell that is spatially coherent.
- Python: `squidpy.gr.spatial_neighbors` for the graph, then a neighbor-augmented or graph-based domain method (BANKSY, STAGATE, GraphST)
- R: BayesSpace (`spatialCluster`), BASS, or Banksy

## Governing Principle

A spatial domain is a REGION, not a cell type, and not a niche -- conflating the three is the central conceptual error of this analysis. A CELL TYPE is one cell's transcriptional identity. A NICHE (cellular neighborhood) is the local cell-type COMPOSITION around a cell -- which types co-occur. A SPATIAL DOMAIN is a contiguous tissue region (a cortical layer, tumor core, stromal band) that contains MANY cell types and several niches. If the question is "which cell types co-occur," that is a niche question and belongs to neighborhood-enrichment analysis (spatial-statistics), NOT domain segmentation; running the wrong one answers the wrong question.

Domain methods exist because plain Leiden/Louvain on expression alone ignores coordinates and produces salt-and-pepper, spatially-incoherent labels. Every domain method deliberately adds a spatial term so neighbors tend to share a label. The load-bearing decision is therefore NOT the clustering algorithm -- it is the SPATIAL-WEIGHT knob (BANKSY lambda, BayesSpace smoothing, SpaGCN histology weight, GNN graph radius). Too much spatial weight is the #1 trap, over-smoothing: it erases real boundaries and merges biologically distinct regions into blobs. Too little reverts to salt-and-pepper. The number of domains k is the second decision, and it is a BIOLOGICAL choice (how fine a regionalization the question needs), not a statistic to optimize against a silhouette score -- report k, justify it, and show sensitivity to k+-1.

## Domain vs Niche vs Cell Type

| Concept | What it is | Unit | Right tool |
|---------|-----------|------|-----------|
| Cell type | One cell's transcriptional identity (lineage/state) | a cell | clustering + markers (single-cell/clustering) |
| Niche / cellular neighborhood | Local cell-type composition -- which types co-occur around a cell | a neighborhood | neighborhood enrichment / co-occurrence (spatial-statistics) |
| Spatial domain | Contiguous tissue region of homogeneous expression, containing many types | a region | domain segmentation (this skill) |

A domain can contain several niches; a niche can span domain boundaries. BANKSY and BASS switch between cell-typing and domain detection via a single parameter, which underscores that these are different outputs of related machinery, not the same task.

## Domain Methods by Mechanism

The mechanism for "using the neighbors" is the axis that separates the methods. No method is a universal winner (Yuan 2024 *Nat Methods*); selection is scenario-specific.

| Method | Spatial mechanism | Needs k? | Best when | Fails when |
|--------|-------------------|----------|-----------|------------|
| BayesSpace | MRF (Potts) smoothing prior on a t-mixture in PCA space; also enhances sub-spot resolution | yes (q) | Visium laminar/continuous tissue; want sub-spot enhancement | non-contiguous regions; MCMC is slow; smoothing strength is a fixed prior |
| BASS | Bayesian hierarchical: cell-type AND domain jointly, Potts prior, multi-sample | yes (C, D) | joint cell-type + domain, multi-sample, low-continuity tissue | heavier to run; needs both counts set |
| STAGATE | Graph attention autoencoder; learns per-edge weights, reconstructs from a spatially-smoothed latent | embedding free; downstream k for mclust | continuous tissue; attention down-weights cross-boundary edges (fights over-smoothing); scales to Slide-seq/Stereo-seq | black-box embedding; sensitive to graph radius |
| GraphST | Graph self-supervised contrastive learning | yes (mclust) | low-res Visium; also does integration + deconvolution | sensitive to graph construction |
| SpaGCN | GCN fusing expression + coordinates + histology RGB | searches resolution to hit target count | H&E histology is informative | needs registered histology |
| SEDR | Masked autoencoder + variational graph autoencoder | yes (mclust) | Visium/Slide-seq/Stereo-seq, robust on DLPFC | graph-construction sensitivity |
| BANKSY | Neighbor-AUGMENTED features: own + neighborhood-mean + azimuthal Gabor; then Leiden/k-means | no fixed k | high-res imaging AND sequencing; unifies cell typing (lambda~0.2) and domains (lambda~0.8); very scalable; transparent | lambda mis-set collapses the task it solves |
| UTAG | Message passing: multiply features by normalized adjacency (one-hop average), then Leiden | no fixed k | multiplexed imaging/proteomics (IMC, CODEX, MIBI); fast | one-hop smoothing only |
| stLearn (SME) | Histology-CNN-weighted smoothing of each spot's expression, then clustering | downstream Louvain/k-means | H&E available and well-registered | only as good as image registration |

Mechanism families: MRF/Bayesian smoothing (BayesSpace, BASS, PRECAST) vs graph neural net (STAGATE, GraphST, SpaGCN, SEDR) vs neighbor-augmentation (BANKSY, UTAG) vs histology-guided (stLearn, SpaGCN). Benchmarks evolve fast -- verify the current verdict for the tissue geometry before committing.

## Read the Benchmark With the DLPFC Caveat

The standard ground truth is DLPFC (Maynard 2021 *Nat Neurosci* 24:425-436): 12 Visium sections of human dorsolateral prefrontal cortex, manually annotated into 6 cortical layers + white matter, scored by ARI. The Yuan 2024 (*Nat Methods* 21:712-722) benchmark of 13 methods x 34 datasets concludes there is NO single winner -- methods are complementary across accuracy, spatial continuity, marker detection, scalability, and robustness. On DLPFC, GNN/graph methods (STAGATE, SEDR, DeepST) and BayesSpace are among the most robust, and a technology-stratified benchmark (Chen 2025 *iMeta* 4:e70084) finds STAGATE/GraphST best on low-resolution Visium while BASS/stLearn/BANKSY lead on high-resolution platforms.

The caveat: DLPFC is a CONTINUOUS, LAMINAR tissue, which flatters smoothing-friendly methods. Do not over-generalize these rankings to non-laminar tissue. ALL methods struggle with NON-CONTIGUOUS domains (the same region appearing in separated patches -- scattered tumor nests, immune aggregates) because the spatial prior assumes contiguity; for non-contiguous biology, lower the spatial weight or switch to a niche/neighborhood analysis rather than domain segmentation.

## Build the Spatial Graph

**Goal:** Construct the spatial neighbor graph that every domain method inherits.

**Approach:** Use a hex lattice for Visium (6 neighbors) and a generic kNN/Delaunay graph for imaging point clouds; the graph radius IS a spatial-weight knob (too dense over-smooths, too sparse fragments).

```python
import squidpy as sq
import scanpy as sc

adata = sc.read_h5ad('preprocessed.h5ad')

# Visium hex lattice: 6 immediate neighbors. For imaging point clouds use
# coord_type='generic' with KNN or Delaunay. Build in microns where possible --
# a graph built in pixels has a different radius than one built in microns.
sq.gr.spatial_neighbors(adata, coord_type='grid', n_neighs=6)
```

## Expression-Only Clustering Is the Salt-and-Pepper Baseline

**Goal:** Show why a domain method is needed at all.

**Approach:** Cluster on expression PCA with no spatial term; the result is spatially incoherent and demonstrates the failure domain methods correct.

```python
sc.pp.neighbors(adata, n_neighbors=15, n_pcs=30)
sc.tl.leiden(adata, resolution=0.5, key_added='expr_leiden',
             flavor='igraph', n_iterations=2, directed=False)

# Plot on tissue: speckled, no contiguous regions -- this is the baseline a
# domain method is built to beat, not a domain result.
sq.pl.spatial_scatter(adata, color='expr_leiden')
```

## Neighbor-Augmented Domains (BANKSY-style) and the Spatial-Weight Knob

**Goal:** Produce spatially coherent domains and make the over-smoothing knob explicit.

**Approach:** BANKSY concatenates each cell's own expression with its neighborhood-mean expression, mixed by lambda; lambda~0.2 yields cell typing, lambda~0.8 yields domains. A transparent neighbor-augmented matrix reproduces the idea with Squidpy when the BANKSY package is unavailable -- the lambda here is the load-bearing decision, not the clustering call.

```python
import numpy as np
from sklearn.preprocessing import normalize

# Mean expression over each spot's spatial neighbors (the neighborhood signal).
W = normalize(adata.obsp['spatial_connectivities'], norm='l1', axis=1)
neighbor_mean = W @ adata.obsm['X_pca']

# lambda is the spatial-weight knob: ~0.8 for domains, ~0.2 for cell typing.
# Too high -> blobs (boundaries erased); too low -> salt-and-pepper.
lam = 0.8
augmented = np.concatenate(
    [np.sqrt(1 - lam) * adata.obsm['X_pca'], np.sqrt(lam) * neighbor_mean], axis=1)
adata.obsm['X_banksy'] = augmented

sc.pp.neighbors(adata, use_rep='X_banksy', key_added='banksy')
sc.tl.leiden(adata, resolution=0.5, key_added='domains', neighbors_key='banksy',
             flavor='igraph', n_iterations=2, directed=False)
sq.pl.spatial_scatter(adata, color='domains')
```

If the BANKSY package is installed, prefer it: `import banksy_py` (Python) or the R `Banksy` Bioconductor package compute the own + neighborhood-mean + azimuthal Gabor (AGF) features and expose lambda directly.

## Sweep the Spatial Weight to Find the Over-Smoothing Edge

**Goal:** Locate the lambda where boundaries are sharp but regions stay contiguous.

**Approach:** Recompute domains across a lambda grid and inspect boundaries against histology; the right lambda is the largest value before distinct regions merge into blobs, judged visually, not by an internal score.

```python
for lam in [0.2, 0.5, 0.8]:
    aug = np.concatenate(
        [np.sqrt(1 - lam) * adata.obsm['X_pca'],
         np.sqrt(lam) * (W @ adata.obsm['X_pca'])], axis=1)
    adata.obsm['X_banksy'] = aug
    sc.pp.neighbors(adata, use_rep='X_banksy', key_added='banksy')
    sc.tl.leiden(adata, resolution=0.5, key_added=f'domains_l{lam}',
                 neighbors_key='banksy', flavor='igraph', n_iterations=2, directed=False)

# Low lambda -> speckled; high lambda -> over-smoothed blobs. Pick by eye
# against known tissue architecture, not by silhouette.
sq.pl.spatial_scatter(adata, color=['domains_l0.2', 'domains_l0.5', 'domains_l0.8'])
```

## Choose k as a Biological Decision, With k+-1 Sensitivity

**Goal:** Set the number of domains to the regionalization the question needs and show the answer is not fragile to it.

**Approach:** When a method takes k directly (BayesSpace q, mclust on a GNN embedding), run k, k-1, k+1 and report all three; do not silently optimize k against a clustering score, which has no biological ground truth.

```python
from sklearn.mixture import GaussianMixture

for k in [6, 7, 8]:  # DLPFC has 6 layers + white matter -> k near 7
    gm = GaussianMixture(n_components=k, covariance_type='full', random_state=0)
    adata.obs[f'domains_k{k}'] = gm.fit_predict(adata.obsm['X_banksy']).astype(str)

# Report k+-1 side by side; a domain that only appears at one k is a weak claim.
sq.pl.spatial_scatter(adata, color=['domains_k6', 'domains_k7', 'domains_k8'])
```

## BayesSpace for Laminar Tissue (R)

**Goal:** Apply an MRF smoothing prior, the robust choice on continuous Visium tissue.

**Approach:** Preprocess, then `spatialCluster` with q domains; the smoothing prior couples neighboring spots. Run in R and import the labels.

```r
library(BayesSpace)

sce <- readRDS('sce.rds')
sce <- spatialPreprocess(sce, platform = 'Visium', n.PCs = 15)
# q is the biological k; nrep is MCMC iterations. spatialEnhance() can split
# spots into subspots for higher resolution after spatialCluster().
sce <- spatialCluster(sce, q = 7, nrep = 10000)
write.csv(data.frame(barcode = colnames(sce), domain = sce$spatial.cluster),
          'bayesspace_domains.csv', row.names = FALSE)
```

## STAGATE for High-Resolution or Large Sections (optional)

**Goal:** Learn a spatially-aware embedding whose attention down-weights cross-boundary edges.

**Approach:** Build the STAGATE radius graph, train the graph-attention autoencoder, then cluster the embedding; set the radius to the over-smoothing knob.

```python
import STAGATE  # optional dependency; pip install STAGATE_pyG or use the TF build

STAGATE.Cal_Spatial_Net(adata, rad_cutoff=150)  # rad_cutoff is the graph radius knob
STAGATE.Stats_Spatial_Net(adata)
adata = STAGATE.train_STAGATE(adata)

sc.pp.neighbors(adata, use_rep='STAGATE')
sc.tl.leiden(adata, resolution=0.5, key_added='stagate_domains',
             flavor='igraph', n_iterations=2, directed=False)
```

## Name Domains From Markers

**Goal:** Attach anatomical labels to spatially coherent clusters.

**Approach:** Rank per-domain markers, then map cluster IDs to region names; marker p-values from the same data that defined the domains are for ranking and labeling only, not inference (the double-dipping caveat from single-cell/clustering).

```python
sc.tl.rank_genes_groups(adata, groupby='domains', method='wilcoxon')
markers = sc.get.rank_genes_groups_df(adata, group=None)
print(markers.groupby('group').head(5))

domain_names = {'0': 'White matter', '1': 'Layer 1', '2': 'Layer 2/3'}
adata.obs['region'] = adata.obs['domains'].map(domain_names)
sq.pl.spatial_scatter(adata, color='region')
```

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| Speckled, spatially incoherent labels | No spatial term (plain Leiden on expression) or spatial weight too low | Use a domain method; raise lambda / smoothing / graph density |
| Regions merged into smooth blobs, boundaries gone | Over-smoothing -- spatial weight too high or graph radius too large | Lower lambda / smoothing strength / rad_cutoff; check boundaries against histology |
| Scattered tumor nests collapse into one domain or vanish | Non-contiguous domain; spatial prior assumes contiguity (Yuan 2024) | Lower the spatial weight, or switch to niche/neighborhood analysis (spatial-statistics) |
| Domain count feels arbitrary / reviewer questions k | k optimized against a silhouette score instead of chosen biologically | Set k from the biology; report k+-1 sensitivity; justify the regionalization |
| Domains track a single sample/section | Batch confounded with biology in multi-sample data | Use a multi-sample method (BASS, PRECAST, GraphST integration) or integrate first |
| Answer changes with no parameter change | Spatial graph rebuilt with different units (pixels vs microns) or different kNN/Delaunay | Pin the graph construction and coordinate units; build once, reuse |
| "Domain" answer to a "which types co-occur" question | Domain segmentation used for a niche question | Use neighborhood enrichment / co-occurrence (spatial-statistics) instead |
| Marker p-values quoted as proof a domain is real | Double-dipping (testing the clustering that defined the groups) | Use markers for ranking/labeling only; validate regions against known architecture |

## Related Skills

- spatial-neighbors - Build and tune the spatial graph every domain method inherits
- spatial-statistics - Niche/neighborhood enrichment and co-occurrence when the question is which cell types co-occur, not which region this is
- spatial-deconvolution - Per-spot cell-type composition; domains are regions, deconvolution is composition within a spot
- single-cell/clustering - Non-spatial clustering, resolution sweeps, and the double-dipping caveat on post-clustering marker tests

## References

- Zhao et al. (2021). Spatial transcriptomics at subspot resolution with BayesSpace. Nat Biotechnol 39:1375-1384.
- Hu et al. (2021). SpaGCN: integrating gene expression, spatial location and histology to identify spatial domains and SVGs by graph convolutional network. Nat Methods 18:1342-1351.
- Dong & Zhang (2022). Deciphering spatial domains from spatially resolved transcriptomics with an adaptive graph attention auto-encoder (STAGATE). Nat Commun 13:1739.
- Long et al. (2023). Spatially informed clustering, integration, and deconvolution of spatial transcriptomics with GraphST. Nat Commun 14:1155.
- Singhal et al. (2024). BANKSY unifies cell typing and tissue domain segmentation for scalable spatial omics data analysis. Nat Genet 56:431-441.
- Kim et al. (2022). Unsupervised discovery of tissue architecture in multiplexed imaging (UTAG). Nat Methods 19:1653-1661.
- Xu et al. (2024). Unsupervised spatially embedded deep representation of spatial transcriptomics (SEDR). Genome Med 16:12.
- Li & Zhou (2022). BASS: multi-scale and multi-sample analysis enables accurate cell type clustering and spatial domain detection in spatial transcriptomic studies. Genome Biol 23:168.
- Yuan et al. (2024). Benchmarking spatial clustering methods with spatially resolved transcriptomics data. Nat Methods 21:712-722.
- Chen et al. (2025). A comprehensive benchmarking for spatially resolved transcriptomics clustering methods across variable technologies, organs, and replicates. iMeta 4:e70084.
- Maynard et al. (2021). Transcriptome-scale spatial gene expression in the human dorsolateral prefrontal cortex. Nat Neurosci 24:425-436.
- Palla et al. (2022). Squidpy: a scalable framework for spatial omics analysis. Nat Methods 19:171-178.
<!-- END FILE: spatial-transcriptomics/spatial-domains/SKILL.md -->

## 子目录：spatial-transcriptomics/spatial-multiomics

<!-- BEGIN FILE: spatial-transcriptomics/spatial-multiomics/SKILL.md -->
---
name: bio-spatial-transcriptomics-spatial-multiomics
description: Integrates spatial RNA with a second modality (protein, ATAC, or histone marks) on spatial CITE-seq, DBiT-seq, spatial-ATAC, or Visium CytAssist data. Use when deciding vertical (same-pixel co-profiling -> WNN/MOFA joint factors) versus diagonal (serial adjacent sections -> registration via PASTE/STalign) integration; recognizing that modalities from serial sections are DIFFERENT cells so joint same-cell methods do not apply; handling a bounded antibody/feature panel where absence is uninformative; or treating a pixel/spot as a multi-cell mixture rather than a single cell.
tool_type: python
primary_tool: muon
---

## Version Compatibility

Reference examples tested with: muon 0.1+, mudata 0.2+, scanpy 1.10+, anndata 0.10+, mofapy2 0.7+, paste-bio 1.4+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Spatial Multi-omics Integration

**"Integrate my spatial RNA with protein / ATAC / a histone mark"** -> Decide whether the modalities are co-measured on the SAME pixels or come from DIFFERENT sections, then either build one joint representation or register two distinct cell populations.
- Same pixel (vertical): `muon`/`mudata` container -> `muon.tl.mofa` joint factors, or WNN-style per-modality weighting.
- Different sections (diagonal): `paste`/`paste2` (optimal-transport alignment), `STalign` (diffeomorphic registration), `GPSA` (common coordinate).

## Governing Principle

Serial-section modalities are DIFFERENT cells -- integration across them is registration, not coupling. A z-step of even 5-10 um lands on a different cell population, so RNA on section N and ATAC on section N+1 share NO cell. Aligning them (PASTE/STalign/GPSA) produces an approximate coordinate correspondence between distinct populations, never a cell-to-cell correspondence. Any cross-modality "coupling" read off a registered pair is a statistical imputation across non-identical cells, not a measurement. The single most-abused move in this subfield is presenting diagonal, registration-based integration with the confident language of same-cell co-measurement (Vandereyken 2023 *Nat Rev Genet*).

Vertical (same-pixel co-profiling) versus diagonal (different cells, must register or anchor) is therefore THE decision, and it is categorical, not a tuning choice. Same-pixel platforms (the Fan-lab DBiT family, spatial-CITE-seq, Visium CytAssist Gene+Protein) justify joint same-cell methods -- WNN, MOFA, totalVI-style models -- because pairing is real. Applying WNN/MOFA diagonally, across serial sections, silently violates the matching assumption: the math runs and returns factors and weights that look meaningful but encode registration artifacts as if they were joint biology.

Two further traps ride on top of the fork. First, every spatial multi-omics platform measures PIXELS or spots (10-55 um) or sub-micron DNBs that must be binned -- "single-cell multi-omics in space" is almost always a downstream binning/segmentation CLAIM, not a property of the measurement, and a multi-cell pixel mixing a sender and a receiver can manufacture apparent within-cell cross-modal coupling. Second, the protein (or ATAC, or histone-mark) side is a TARGETED panel: the antibody set is chosen a priori, so a protein "absent" was likely never in the panel, exactly as a targeted RNA panel bounds what RNA can be detected -- absence is uninformative on either side.

## The Integration Regime Fork

| Regime | What is shared | Example assay | Correct approach | Fails when |
|---|---|---|---|---|
| Vertical / same-pixel | Same pixels (real pairing) | spatial-CITE-seq, DBiT-seq, Visium CytAssist, spatial epigenome-transcriptome | Joint factor / weighted-graph: MOFA, WNN, totalVI-style | Treating a multi-cell pixel as one cell; ignoring panel bound |
| Diagonal / serial-section | Nothing (distinct cells) | RNA on section N + ATAC on section N+1; two technologies on adjacent slices | Spatial REGISTRATION: PASTE/PASTE2, STalign, GPSA | Feeding registered pairs into WNN/MOFA as if same-cell |

When the regime is ambiguous (a vendor markets "co-profiling" but the modalities were run on adjacent sections), default to diagonal: assume different cells until same-pixel co-capture is documented.

## Spatial Multi-omics Platform Table

| Platform | Modalities co-measured | Same-pixel vs serial | Resolution | Integration approach | Best when / fails when |
|---|---|---|---|---|---|
| spatial-CITE-seq (Liu/Fan 2023) | ~100s proteins (ADTs) + whole transcriptome | Same pixel | 20-25 um pixels | Vertical: MOFA/WNN on MuData | Whole-transcriptome RNA + real protein pairing; fails as single cells (pixel = several cells), protein bounded by ADT panel |
| DBiT-seq (Liu/Fan 2020) | mRNA + protein (antibody DNA tags) | Same pixel | 10/25/50 um pixels | Vertical: MOFA/WNN | True co-capture; even 10 um pixel is 1-several cells, no segmentation |
| spatial-ATAC-seq (Deng/Fan 2022) | Chromatin accessibility (single modality) | Same pixel grid | 20/50 um | Integrate with RNA section by REGISTRATION (diagonal) | ATAC-only per run; sparse per-pixel; pair to RNA only across sections |
| Spatial epigenome-transcriptome (Zhang/Fan 2023) | (ATAC or one histone mark) + RNA, same pixel | Same pixel | 20 um (near-single-cell) | Vertical: joint factors | Genuinely paired per pixel; one mark per run; pixels still not segmented cells |
| Visium CytAssist Gene+Protein (10x, commercial) | Whole transcriptome + ~31-35 protein panel | Same spot | 55 um spots | Vertical BUT deconvolve: spot = many cells | Same-spot pairing; protein limited to validated panel; no peer-reviewed primary paper |
| Stereo-CITE-seq (BGI, preprint) | mRNA + protein on Stereo-seq array | Same array | sub-micron DNBs (must bin) | Vertical after binning | Flag as not peer-reviewed; protein sensitivity under-characterized |

Methods and platforms move fast here; verify the current co-capture claim and the recommended joint method against the vendor and tool docs before committing, especially whether a "multiomics" product co-captures on one pixel or runs adjacent sections.

## Vertical: Build a Same-Pixel MuData (RNA + Protein)

**Goal:** Assemble one MuData whose RNA and protein modalities are indexed on the SAME pixels, the precondition for any same-cell joint method.

**Approach:** Wrap each modality as an AnnData, share one pixel index and the spatial coordinates, then intersect observations so every pixel carries both modalities before joint modeling.

```python
import muon as mu
import mudata as md
import scanpy as sc

rna = sc.read_h5ad('spatial_cite_rna.h5ad')        # pixels x genes, whole transcriptome
prot = sc.read_h5ad('spatial_cite_adt.h5ad')       # SAME pixels x bounded ADT panel

# both modalities MUST be indexed on identical pixel barcodes -- this is what makes pairing real
mdata = md.MuData({'rna': rna, 'prot': prot})
mdata.obsm['spatial'] = rna.obsm['spatial']        # one shared coordinate frame for both modalities

sc.pp.normalize_total(mdata['rna']); sc.pp.log1p(mdata['rna'])
sc.pp.highly_variable_genes(mdata['rna'])
# ADT is a targeted panel: CLR across pixels, not log1p-of-counts; absence of a marker is uninformative
mu.prot.pp.clr(mdata['prot'])

mu.pp.intersect_obs(mdata)                          # keep only pixels present in BOTH modalities
```

## Vertical: Joint MOFA Factors Across Modalities

**Goal:** Learn interpretable latent factors shared across RNA and protein, with per-modality variance explained, on co-measured pixels.

**Approach:** Run MOFA on the MuData, then read the joint embedding and inspect which factors are RNA-driven versus protein-driven before clustering or spatial mapping.

```python
# MOFA assumes the modalities are matched on the same pixels -- valid ONLY because this is same-pixel data
mu.tl.mofa(mdata, n_factors=10, use_var='highly_variable', outfile=None)   # writes mdata.obsm['X_mofa']

sc.pp.neighbors(mdata, use_rep='X_mofa')
sc.tl.leiden(mdata)

# mu.tl.mofa trains in place (returns None); write the model with outfile= and
# read per-modality variance explained back with mofax. A factor that is ~100%
# one modality is not "multi-omic" structure -- it is that modality's own signal.
# import mofax; m = mofax.mofa_model('mofa_model.hdf5'); m.get_variance_explained()
```

WNN is the alternative joint method when interpretable factors are not needed: build a per-modality reduction, then learn per-pixel modality weights. A single modality dominating the weights is the same red flag as in single-cell CITE-seq (see single-cell/multimodal-integration). The protein panel is bounded, so a pixel scoring "negative" for a marker may simply lack that antibody, not the protein.

## Diagonal: Register Serial Sections (Different Cells)

**Goal:** Place two adjacent-section datasets in a common coordinate frame so that NEARBY does not require SAME-CELL.

**Approach:** Compute an optimal-transport alignment between the two slices over expression plus physical distance, then stack them on shared coordinates -- the output is a coordinate map between DISTINCT cell populations, never a cell correspondence.

```python
import paste as pst

# sliceA and sliceB are AnnData from ADJACENT sections -- DIFFERENT cells, not the same tissue plane
pi = pst.pairwise_align(sliceA, sliceB)            # transport plan between spots, NOT a cell-to-cell map

# stack onto a shared frame for joint visualization / neighborhood comparison only
new_slices = pst.stack_slices_pairwise([sliceA, sliceB], [pi])
# any cross-modality "coupling" inferred here is imputed across non-identical cells -- label it as such
```

PASTE2 handles partial overlap between sections; STalign performs diffeomorphic (LDDMM) registration; GPSA learns a Gaussian-process common coordinate. All produce a coordinate correspondence, not a cell correspondence -- do not feed the registered pair into WNN/MOFA as though the pixels were paired.

## Common Errors

| Symptom | Cause | Fix |
|---|---|---|
| WNN/MOFA "joint" factors that look biological but irreproducible across replicate sections | Ran a same-cell joint method across SERIAL sections (different cells) | Use registration (PASTE/STalign/GPSA); reserve WNN/MOFA for same-pixel data only |
| Cross-modal "coupling" reported as same-cell co-regulation from adjacent slices | Treated a registered coordinate map as a cell-to-cell correspondence | State the regime is diagonal; report coupling as imputed across non-identical cells, not measured |
| Marker called "absent" / cell type "missing" in the protein modality | Antibody was never in the bounded ADT panel | Treat panel absence as uninformative; check the panel manifest before any negative claim |
| A factor or weight is ~100% one modality but called "multi-omic" | Per-modality variance not inspected; one denser modality dominates | Report per-modality variance explained / per-pixel weights; down-weight or denoise the dominant modality |
| ADT/protein values explode after log1p | Modeled a targeted protein panel as RNA counts | Use CLR (or arcsinh) across pixels for protein, not log1p-of-UMIs |
| "Single-cell multi-omics" conclusions from pixel data | Treated a 20-55 um pixel/spot as one cell | Bin/segment explicitly and disclose it; a multi-cell pixel can manufacture within-cell cross-modal coupling |
| MOFA / WNN errors on pixel mismatch | RNA and protein indexed on non-identical pixel barcodes | `mu.pp.intersect_obs(mdata)` so every pixel carries both modalities |

## Related Skills

- spatial-transcriptomics/spatial-proteomics - protein-intensity (not count) handling, arcsinh, segmentation-dominated panels for the protein side
- spatial-transcriptomics/spatial-data-io - load each modality with the correct reader before assembling a MuData
- single-cell/multimodal-integration - WNN/totalVI/MOFA+ mechanics, ADT denoising, and the anchor-structure fork in non-spatial data
- multi-omics-integration/mofa-integration - MOFA factor interpretation and likelihood choice across modalities

## References

Liu Y, DiStasio M, Su G, et al. High-plex protein and whole transcriptome co-mapping at cellular resolution with spatial CITE-seq. Nat Biotechnol 41(10):1405-1409 (2023).
Liu Y, Yang M, Deng Y, et al. High-Spatial-Resolution Multi-Omics Sequencing via Deterministic Barcoding in Tissue (DBiT-seq). Cell 183(6):1665-1681 (2020).
Deng Y, Bartosovic M, Kukanja P, et al. Spatial profiling of chromatin accessibility in mouse and human tissues. Nature 609(7926):375-383 (2022).
Zhang D, Deng Y, Kukanja P, et al. Spatial epigenome-transcriptome co-profiling of mammalian tissues. Nature 616(7955):113-122 (2023).
Zeira R, Land M, Strzalkowski A, Raphael BJ. Alignment and integration of spatial transcriptomics data (PASTE). Nat Methods 19(5):567-575 (2022).
Argelaguet R, Arnol D, Bredikhin D, et al. MOFA+: a statistical framework for comprehensive integration of multi-modal single-cell data. Genome Biol 21:111 (2020).
Hao Y, Hao S, Andersen-Nissen E, et al. Integrated analysis of multimodal single-cell data (WNN). Cell 184(13):3573-3587 (2021).
Vandereyken K, Sifrim A, Thienpont B, Voet T. Methods and applications for single-cell and spatial multi-omics. Nat Rev Genet 24(8):494-515 (2023).
Marconato L, Palla G, Yamauchi KA, et al. SpatialData: an open and universal data framework for spatial omics. Nat Methods 22(1):58-62 (2025).
<!-- END FILE: spatial-transcriptomics/spatial-multiomics/SKILL.md -->

## 子目录：spatial-transcriptomics/spatial-neighbors

<!-- BEGIN FILE: spatial-transcriptomics/spatial-neighbors/SKILL.md -->
---
name: bio-spatial-transcriptomics-spatial-neighbors
description: Build the spatial neighbor graph that every downstream spatial statistic (Moran's I, neighborhood enrichment, co-occurrence, spatial domains) inherits, using Squidpy. Use when choosing the graph type (kNN vs Delaunay vs fixed-radius vs Visium hex grid) and understanding why it silently changes every downstream result; handling variable cell density (kNN fixes neighbor COUNT, fixed-radius fixes physical DISTANCE -- each distorts the other); getting coordinate units right (pixels vs microns; Visium array coords are not distance); pruning Delaunay long edges across tissue gaps; running the graph sensitivity analysis almost nobody runs; and knowing when planar section neighbors misrepresent a 3D tissue.
tool_type: python
primary_tool: squidpy
---

## Version Compatibility

Reference examples tested with: squidpy 1.4+, scanpy 1.10+, anndata 0.10+, numpy 1.26+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Spatial Neighbor Graphs

**"Build a spatial neighbor graph for my tissue"** -> Define which cells or spots count as spatial neighbors, encoded as a sparse weights matrix W over `adata.obsm['spatial']`.
- Python: `squidpy.gr.spatial_neighbors()` -> writes `adata.obsp['spatial_connectivities']` and `adata.obsp['spatial_distances']`

The platform-class fork sets the default geometry. Sequencing/capture data on a fixed lattice (Visium hex, Visium HD grid) has a KNOWN adjacency -> use `coord_type='grid'`. Imaging/in-situ point clouds (Xenium, MERFISH, CosMx) have irregular cell positions -> use `coord_type='generic'` with Delaunay or kNN. The first question is always which side of the fork the data is on, because it decides whether "neighbor" is a lattice fact or a modeling choice.

## Governing Principle

The graph is the model that all spatial statistics inherit. Moran's I, Geary's C, neighborhood enrichment, co-occurrence, and every graph-neural-network spatial-domain method are functions `f(expression, W)` of the spatial weights matrix W -- the graph is not preprocessing, it is literally an argument to the statistic. Change k from 6 to 30, switch Delaunay to kNN, or row-standardize W instead of leaving it binary, and the Moran's I value, the enrichment z-scores, the SVG ranking, and the domain boundaries all move. The analyst is never measuring "spatial structure"; they are measuring spatial structure as seen through one particular definition of adjacency.

This is the most under-reported researcher degree of freedom in the field, and it has a name geographers settled decades ago: the modifiable areal unit problem -- aggregate or re-adjacency the units and the answer changes. There is no canonical W. The honest workflow therefore does what almost no paper does: build the graph under at least two definitions, rerun the downstream statistic, and report which genes/pairs/domains are graph-robust versus graph-fragile. A result that survives only one graph choice is a result about that graph, not about the tissue.

Two failure directions bound the choice. Too dense a graph (large k, large radius, many rings) over-smooths -- it inflates apparent autocorrelation, washes out local detail, and merges distinct domains into blobs. Too sparse a graph fragments the tissue into disconnected components, flags spurious local outliers, and misses real medium-scale structure. The right density is the one whose downstream conclusion is stable; the specific k is not the deliverable, the stability across k is.

## The Graph-Construction Decision

Each family silently assumes something different about the tissue, and that assumption -- not the algorithm -- is what fails.

| Graph type | Degree behavior | Density bias | Best when | Fails when |
|---|---|---|---|---|
| Visium hex grid (`coord_type='grid'`, `n_rings`) | Fixed 6 per ring; known lattice | None (regular lattice) | Visium / capture grids where geometry is fixed and exact | A spot is treated as a cell -- it is a 1-10-cell mixture, so spot adjacency mixes deconvolution error with real contact |
| kNN (`coord_type='generic'`, `n_neighs`) | Constant COUNT k | Radius implicitly stretches in sparse regions, connecting distant cells | Single-cell platforms (Xenium/MERFISH/CosMx) where fixed degree is wanted | Density varies sharply; asymmetric by default (A is B's neighbor but not vice versa) |
| Fixed-radius (`radius=r`) | Variable -- more neighbors where dense | STRONG: dense regions get more neighbors of EVERYTHING -> inflated enrichment that is pure density artifact | A real physical interaction range exists (ligand diffusion ~tens of microns) AND density is ~uniform | Density gradients; radius set in the wrong coordinate unit |
| Delaunay (`delaunay=True`) | Variable; parameter-free "who touches whom" | Mild | Single-cell data wanting a parameter-free contact graph | Tissue has gaps/holes/folds -> long spurious edges leap across empty space; needs distance pruning |

Three points the naive analyst misses. `squidpy.gr.nhood_enrichment` builds NO graph of its own -- it consumes whatever graph `spatial_neighbors` already stored in `obsp` (and errors if none exists); the Squidpy non-grid default is kNN with `n_neighs=6` (`delaunay=False`), so a published z-score is specific to whichever graph produced it and would change under a different graph -- always know which graph produced the number. kNN is asymmetric; "mutual kNN" (edge only if both cells are in each other's k-set) is more conservative and stops hub cells in dense regions from dominating. Unpruned Delaunay over tissue with necrotic holes or folds connects cells micrometers apart on the slide but biologically unrelated -- pruning by a max edge length is the standard fix.

## Variable Cell Density: There Is No Free Lunch

A fixed-radius neighborhood gives dense regions more neighbors and sparse regions fewer. Because neighborhood enrichment, co-occurrence, and local statistics all depend on neighbor COUNTS, a pure density gradient masquerades as biological signal: a dense lymphoid follicle gets inflated "enrichment" of everything simply because every cell there has more neighbors. kNN fixes the count (it adapts the radius to local density) but then distorts physical distance -- a "neighbor" in sparse stroma may sit far away. The density structure of the tissue dictates which distortion is tolerable: use kNN/Delaunay when density varies (the common case in real tissue); reserve fixed-radius for roughly uniform tissue where an absolute physical interaction range is the actual biological question.

## The Coordinate-Unit Trap

A radius, a co-occurrence interval, and a Delaunay pruning cutoff are all in PHYSICAL distance units. If `adata.obsm['spatial']` holds pixels, array row/col indices, or arbitrary units, a "50-unit radius" is silently meaningless. Visium array row/col is a lattice index, not microns; full-resolution Visium pixel coordinates need the Space Ranger scale factor (`spot_diameter_fullres`, `tissue_hires_scalef`) to convert to physical distance. Imaging platforms store microns or pixels depending on the reader. Confirm the unit BEFORE setting any distance parameter -- the single cheapest check is to measure nearest-neighbor spacing and compare it to the known platform pitch (Visium ~100 microns center-to-center).

**Goal:** Confirm the coordinate unit so that any radius is physically meaningful.

**Approach:** Measure median nearest-neighbor distance from a temporary kNN graph and compare it to the known platform geometry; a Visium grid in microns should read ~100, in pixels it reads hundreds-to-thousands.

```python
import squidpy as sq
import scanpy as sc
import numpy as np

sq.gr.spatial_neighbors(adata, coord_type='generic', n_neighs=1)   # nearest neighbor only, just to read spacing
nn = adata.obsp['spatial_distances'].data
print(f'median nearest-neighbor spacing: {np.median(nn):.1f} units')
# Visium pitch is ~100 microns; a value of hundreds-to-thousands means coords are in PIXELS -> rescale or use grid mode
```

## Build the Graph by Platform Class

**Goal:** Construct the adjacency that matches the platform geometry rather than a one-size default.

**Approach:** Use grid mode for Visium hex (the lattice is exact and known); use generic Delaunay or kNN for imaging point clouds; store under named keys so multiple graphs coexist for the sensitivity check below.

```python
# Visium hex lattice: 6 immediate neighbors per ring; n_rings=2 widens the neighborhood deliberately
sq.gr.spatial_neighbors(adata, coord_type='grid', n_neighs=6, n_rings=1, key_added='visium_hex')

# Imaging point cloud, fixed-degree: constant k, radius adapts to local density
sq.gr.spatial_neighbors(adata, coord_type='generic', n_neighs=10, key_added='knn10')

# Imaging point cloud, parameter-free contact graph (delaunay=True is opt-in; the
# generic default is kNN with n_neighs=6)
sq.gr.spatial_neighbors(adata, coord_type='generic', delaunay=True, key_added='delaunay')
```

## Prune Delaunay Long Edges Across Tissue Gaps

**Goal:** Stop Delaunay from inventing long-range "neighbors" that leap across necrotic holes, folds, or slide background.

**Approach:** Build Delaunay, then prune to a physically sensible maximum edge length using `radius` as a `(min, max)` interval -- edges longer than `max` (in microns) are dropped.

```python
# radius as a (min, max) tuple prunes the graph to edges within that physical-distance interval;
# choose max from the tissue: a few cell diameters (e.g. 50 microns) kills cross-gap edges, keeps true contacts
sq.gr.spatial_neighbors(adata, coord_type='generic', delaunay=True, radius=(0.0, 50.0), key_added='delaunay_pruned')

pruned = adata.obsp['delaunay_pruned_connectivities']
print(f'edges after pruning: {pruned.nnz}; mean degree: {pruned.nnz / adata.n_obs:.1f}')
```

## Run the Graph Sensitivity Analysis (the one almost nobody runs)

**Goal:** Decide whether a downstream conclusion is a property of the tissue or an artifact of the graph choice.

**Approach:** Build the graph under several adjacency definitions, store each under its own key, then recompute the downstream statistic on each and flag results that are not stable across graphs.

```python
graphs = {}
for k in (6, 15, 30):
    sq.gr.spatial_neighbors(adata, coord_type='generic', n_neighs=k, key_added=f'knn{k}')
    graphs[f'knn{k}'] = adata.obsp[f'knn{k}_connectivities']
sq.gr.spatial_neighbors(adata, coord_type='generic', delaunay=True, key_added='delaunay')
graphs['delaunay'] = adata.obsp['delaunay_connectivities']

# Recompute the downstream statistic per graph (Moran's I shown); compare rankings, not single values.
# A gene/pair/domain that only appears under one graph is graph-fragile -- report it as such.
import scanpy as sc
for name, W in graphs.items():
    adata.obsp['spatial_connectivities'] = W            # spatial_autocorr reads the active 'spatial' graph
    adata.obsp['spatial_distances'] = adata.obsp[f'{name}_distances'] if f'{name}_distances' in adata.obsp else adata.obsp['spatial_distances']
    sq.gr.spatial_autocorr(adata, mode='moran', genes=adata.var_names[:50].tolist())
    adata.uns[f'moranI_{name}'] = adata.uns['moranI'].copy()
```

## Inspect the Graph Before Trusting It

**Goal:** Catch fragmentation (too sparse) and over-connection (too dense) before they corrupt every downstream number.

**Approach:** Summarize degree distribution and connected components; a healthy graph is one connected component with a tight degree distribution, not many islands or a few hub cells.

```python
import numpy as np
conn = adata.obsp['spatial_connectivities']
degree = np.asarray((conn > 0).sum(axis=1)).ravel()
print(f'mean degree {degree.mean():.1f}; min {degree.min()}; max {degree.max()}')
# isolated cells (degree 0) signal fragmentation; a heavy max-degree tail signals density-driven hubs
print(f'isolated cells: {(degree == 0).sum()}')
```

## The 2D-Section vs 3D-Tissue Caveat

A tissue section is one ~5-10 micron optical/physical plane of a three-dimensional organ. Two cells that are planar neighbors in the section may be far apart in the intact tissue, and two true 3D neighbors may sit in different sections and never appear adjacent in the graph. Cells truncated at the section's top or bottom surface carry partial transcript profiles (only the captured fraction of the cell), which depresses their counts and distorts their degree. Any neighbor graph built from a single section is a planar slice of the real 3D adjacency -- adequate for in-plane analysis, but it does not license 3D-contact claims. Reconstructing true 3D neighbors from serial sections (registration, z-stacking, alignment across planes) is a different problem that this graph does not solve. Layered, ducted, or crypted tissue is also anisotropic (covariance is direction-dependent), so an isotropic graph that ignores orientation underpowers directional structure -- a caveat to keep when neighbor counts feed directional or layer-aware statistics.

## Common Errors

| Symptom | Cause | Fix |
|---|---|---|
| Every cell has wildly different neighbor counts; dense regions show "enrichment" of everything | Fixed-radius graph on density-varying tissue -- pure density artifact | Use kNN or Delaunay (constant or contact-based degree); reserve `radius` for ~uniform tissue with a real physical range |
| A radius of 50 captures all cells or none | `adata.obsm['spatial']` is in pixels or array units, not microns | Confirm the unit (measure nearest-neighbor spacing vs platform pitch); apply the Visium scale factor or use `coord_type='grid'` |
| Long edges cross empty space / necrotic holes; spurious long-range neighbors | Unpruned Delaunay over tissue with gaps or folds | Prune with `radius=(0, max)` at a few cell diameters; inspect the overlaid graph |
| Visium neighbors look irregular instead of a clean hex lattice | `coord_type='generic'` used on a Visium grid | Use `coord_type='grid'` with `n_rings`; the lattice adjacency is exact and known |
| Downstream Moran's I / enrichment z-scores change when k is changed | Expected -- the statistic is `f(expression, W)`; the graph is the model | Run the sensitivity analysis across k and Delaunay; report only graph-robust results |
| Graph splits into many connected components | Graph too sparse (k too small, radius too short) | Increase k or radius, or switch to Delaunay; check isolated-cell count |
| Spot-level neighborhood enrichment over-interpreted as cell-cell contact | A Visium spot is a 1-10-cell mixture, not a cell | Treat spot adjacency as spot-level; deconvolve (spatial-transcriptomics/spatial-deconvolution) before cell-level claims |
| 3D-contact conclusion drawn from one section | Planar neighbors are a slice of 3D adjacency; truncated cells have partial profiles | Restrict claims to in-plane; use serial-section reconstruction for true 3D neighbors |

## Related Skills

- spatial-transcriptomics/spatial-statistics - the neighbor graph is the W fed to Moran's I, neighborhood enrichment, and co-occurrence
- spatial-transcriptomics/spatial-domains - graph-based domain methods inherit this adjacency and its over-smoothing/fragmentation tradeoff
- spatial-transcriptomics/spatial-communication - ligand-receptor proximity tests run on this graph and inherit its density bias
- spatial-transcriptomics/spatial-data-io - load coordinates and confirm their unit before building any graph
- single-cell/clustering - expression-space kNN graphs, the non-spatial counterpart

## References

- Palla G, Spitzer H, Klein M, et al. (2022) Squidpy: a scalable framework for spatial omics analysis. Nature Methods 19(2):171-178. DOI 10.1038/s41592-021-01358-2
- Moran PAP (1950) Notes on continuous stochastic phenomena. Biometrika 37(1/2):17-23. DOI 10.1093/biomet/37.1-2.17
- Geary RC (1954) The contiguity ratio and statistical mapping. The Incorporated Statistician 5(3):115-145. DOI 10.2307/2986645
- Getis A, Ord JK (1992) The analysis of spatial association by use of distance statistics. Geographical Analysis 24(3):189-206. DOI 10.1111/j.1538-4632.1992.tb00261.x
- Ripley BD (1977) Modelling spatial patterns. Journal of the Royal Statistical Society Series B 39(2):172-212. DOI 10.1111/j.2517-6161.1977.tb01615.x
- Dos Santos Peixoto R, Miller BF, Brusko MA, et al. (2025) Characterizing cell-type spatial relationships across length scales in spatially resolved omics data. Nature Communications 16:350. DOI 10.1038/s41467-024-55700-1
<!-- END FILE: spatial-transcriptomics/spatial-neighbors/SKILL.md -->

## 子目录：spatial-transcriptomics/spatial-preprocessing

<!-- BEGIN FILE: spatial-transcriptomics/spatial-preprocessing/SKILL.md -->
---
name: bio-spatial-transcriptomics-spatial-preprocessing
description: Quality control, filtering, and normalization for spatial transcriptomics (Visium, Visium HD, Xenium, MERFISH/MERSCOPE, CosMx, Slide-seq) with Squidpy and Scanpy. Use when setting QC floors that do NOT delete real low-count imaging cells (an scRNA min_counts=500 floor deletes nearly every Xenium cell, whose vector is tens-to-low-hundreds of transcripts); deciding whether to normalize at all when library size carries spatial biology rather than pure technical depth; choosing cell-volume/area normalization over Pearson residuals for skewed targeted panels; reading negative-control-probe / blank-barcode false-discovery rates; and inspecting QC spatially on the tissue rather than only in violins.
tool_type: python
primary_tool: squidpy
---

## Version Compatibility

Reference examples tested with: squidpy 1.5+, scanpy 1.10+, anndata 0.10+, spatialdata 0.2+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Spatial Preprocessing

**"QC and normalize my spatial data"** -> Flag and remove low-quality spots/cells, then put counts on a scale fit for downstream domain and marker analysis -- but the right QC floors and the right normalization both depend on which side of the platform fork the data sits.
- Sequencing/spot (Visium, Visium HD, Slide-seq, Stereo-seq): a spot/bin is mini-bulk over 1-10 cells; QC on UMI/spot, genes/spot, mito-%, cells/spot; normalization must respect that library size tracks cellularity.
- Imaging/in-situ (Xenium, MERSCOPE/MERFISH, CosMx, seqFISH): a cell is segmentation-derived, carries tens-to-low-hundreds of transcripts over a TARGETED panel; QC on a low transcript floor, cell area, and negative-control FDR; normalization must not be gene-count-based.

## The platform-class fork (decide this first)

The first question on any spatial dataset is which assay family produced it, because it changes every QC threshold and the entire normalization decision.

| Axis | Sequencing/spot (Visium, Slide-seq, Stereo-seq) | Imaging/in-situ (Xenium, MERSCOPE, CosMx) |
|---|---|---|
| Unit | spot/bin = 1-10-cell mixture | segmentation-derived single cell |
| Counts/unit | hundreds-thousands UMI | tens-low hundreds transcripts |
| Gene space | whole-transcriptome (poly-A) or probe panel | TARGETED panel (100-1000), genes/cell ceilinged at panel size |
| Mito-% QC | available (mixed-cell average) | usually impossible (mito off-panel) |
| Specificity metric | none native | negative-control-probe / blank-barcode FDR |
| Library-size meaning | confounds cells-per-spot + cellularity | confounds cell SIZE/AREA + segmentation error |

## Governing Principle

In single-cell RNA-seq library size is a technical nuisance to divide out. In spatial transcriptomics LIBRARY SIZE CARRIES BIOLOGY, and that single fact governs both QC and normalization. On Visium, total counts per spot are spatially structured and correlated with anatomy because they confound with the number of cells per spot and tissue cellularity (Bhuva 2024 *Genome Biol* 25:99). On imaging platforms, total counts per cell confound with cell SIZE/AREA -- a physically larger segmented cell holds more molecules for purely geometric reasons -- and with segmentation error itself. Naively dividing library size out (CP10k, log1p, scran pooling) therefore removes real spatially-structured biology and measurably degrades spatial-domain detection.

For imaging the bias is UPSTREAM of any residual model. Because a targeted panel is small, hand-curated, and skewed toward a few high markers, any gene-count-based size factor is dominated by a handful of genes and becomes panel-composition-dependent. Atta and Fan 2024 (*Genome Biol* 25:153) compared library-size, Pearson/SCTransform, DESeq2, TMM, and volume/area normalization on skewed panels: the four gene-count methods inject region-specific bias of up to ~13% DE error and fold-change SIGN REVERSAL in up to 19% of genes, while volume/area normalization avoids it because its denominator is independent of panel composition. The load-bearing consequence: Pearson residuals and SCTransform, the gold standard for whole-transcriptome scRNA, do NOT rescue a skewed imaging panel -- they are still gene-count-based and the bias sits in the panel design. The fix is non-gene-count normalization (cell volume/area, Moffitt-style) or spatially-aware joint modeling (SpaNorm).

A clean violin plot proves nothing. A count floor that silently deletes a spatial cluster of small cells (lymphocytes), a normalization that erases a cellularity gradient, and a focal hybridization failure all survive a tidy genes-per-cell distribution. The dangerous artifacts are spatial, so QC must be inspected spatially.

## scRNA QC thresholds are wrong for imaging

Carrying scRNA defaults onto imaging data deletes the data. Imaging cells carry tens-to-low-hundreds of transcripts -- one to two orders of magnitude below droplet scRNA -- so an `min_counts=500` floor removes nearly every real cell. Genes/cell can never exceed the panel size, so the "high genes = doublet" heuristic is meaningless (the ceiling is the panel, not a doublet). Mito genes are usually off-panel, so `pct_counts_mt` QC is often impossible. Worst, an aggressive count floor preferentially deletes the smallest REAL cells (lymphocytes, neutrophils), biasing tissue composition rather than removing noise.

### QC-metric-by-platform table

| Metric | Visium (spot) | Imaging (Xenium/MERSCOPE/CosMx) | Rationale / trap |
|---|---|---|---|
| counts/unit | UMI/spot; no universal floor; OSTA DLPFC flags <600 | transcripts/cell tens-low hundreds; community floor ~10 (Squidpy), some 20 | scRNA `min_counts=500` deletes nearly every imaging cell; floor confounds cellularity/cell-size |
| genes/unit | genes/spot; OSTA flags <400 | genes/cell CEILING = panel size (100-1000) | "high genes = doublet" meaningless for imaging |
| mito-% | mixed-cell average; OSTA flags >0.28 (brain) | usually off-panel -> impossible | tissue-dependent; brain tolerates higher |
| cell area (um^2) | n/a (spot is fixed) | MAD-based on counts/area | flags over/under-segmentation; no fixed vendor min |
| negative-control FDR | n/a | THE imaging specificity metric | false-discovery proxy; no scRNA analogue |
| cells/spot | nuclei estimate; OSTA flags >10 | n/a | confirms spot is a mixture |

Thresholds are tissue-dependent and "somewhat arbitrary" (the OSTA Visium worked example flags UMI<600, genes<400, mito>0.28, cells/spot>10 on DLPFC, removing 32/3639 spots -- a starting point, not a law). The imaging floor of ~10 transcripts/cell is a Squidpy/community convention, NOT a vendor specification; community CosMx floors run higher (commonly ~20 counts/cell, scaling up with plex), so confirm the cutoff against the panel and tissue rather than copying a number.

**Goal:** Annotate negative controls and mito genes (where present), compute QC metrics, and set platform-appropriate floors without deleting real low-count cells.

**Approach:** Branch on the fork. For imaging, identify control-probe prefixes, filter on a low transcript floor and cell area; for spot data, use UMI/genes/mito floors. Always compute metrics, then look at them spatially before cutting.

```python
import squidpy as sq
import scanpy as sc
import numpy as np

# Imaging branch: control features carry platform-specific prefixes -- they are the specificity ruler, not genes
ctrl_prefixes = ('NegControlProbe', 'NegControlCodeword', 'BLANK', 'Blank', 'NegPrb')   # Xenium / MERFISH / CosMx
adata.var['control'] = adata.var_names.str.startswith(ctrl_prefixes)
adata.var['mt'] = adata.var_names.str.startswith(('MT-', 'mt-'))                          # usually empty on imaging panels
sc.pp.calculate_qc_metrics(adata, qc_vars=['control', 'mt'], percent_top=None, inplace=True)
# inplace defaults to False and returns DataFrames; pass inplace=True to write .obs/.var
```

## Negative controls -- the imaging specificity metric

Imaging platforms include features that decode to nothing biological: Xenium negative-control PROBES (off-target binding) plus negative-control CODEWORDS (pure optical/decoding error), MERFISH/MERSCOPE blank barcodes (valid codewords with no probe), CosMx NegPrb (alien synthetic sequences). They are the only native false-discovery proxy in spatial data. The canonical metric is FDR = mean counts per control feature / mean counts per real gene; the community-acceptable band is roughly <=1-5% of signal (Xenium typically <0.1%, MERFISH ~4%, CosMx highest). Compute it before trusting any gene-level claim, and treat controls as a panel-wide QC gate -- not as genes to cluster on.

**Goal:** Quantify the per-feature false-discovery rate and drop controls before normalization and clustering.

**Approach:** Average per-feature counts within the control set and within real genes, take the ratio, then subset the matrix to real genes only.

```python
ctrl = adata.var['control'].values
mean_ctrl = np.asarray(adata[:, ctrl].X.sum(axis=0)).ravel().mean() if ctrl.any() else 0.0
mean_gene = np.asarray(adata[:, ~ctrl].X.sum(axis=0)).ravel().mean()
fdr = mean_ctrl / mean_gene if mean_gene else float('nan')
print(f'negative-control FDR: {fdr:.4f}  (band ~<=0.01-0.05)')
adata = adata[:, ~ctrl].copy()   # controls are a QC ruler, never clustering features
```

## Inspect QC spatially, then filter

A QC gradient across the section -- counts falling toward one edge, mito rising in a corner -- is a technical artifact (edge effects, uneven permeabilization, focal hybridization failure), not biology, and a violin plot hides it. Always map QC onto tissue coordinates before choosing thresholds, and check WHERE the cells slated for removal actually fall.

**Goal:** Reveal spatially-structured quality artifacts and confirm a proposed floor is not removing a coherent tissue region.

**Approach:** Color the spatial scatter by each QC metric; a smooth spatial gradient signals a technical artifact to address (or model) rather than threshold away.

```python
sq.pl.spatial_scatter(adata, color=['total_counts', 'n_genes_by_counts'], shape=None, ncols=2)
# shape=None renders points (imaging/Slide-seq); omit it for Visium hex spots with a tissue image
```

**Goal:** Apply platform-appropriate floors that remove debris and segmentation failures without biasing composition.

**Approach:** Imaging -- low transcript floor plus a cell-area sanity bound. Spot -- UMI/genes/mito floors. Either way, filter genes seen in too few units last.

```python
# Imaging floor: ~10 transcripts/cell is a Squidpy/community convention, NOT a vendor spec
sc.pp.filter_cells(adata, min_counts=10)
if 'cell_area' in adata.obs:
    lo, hi = adata.obs['cell_area'].quantile([0.01, 0.99])     # trim segmentation over/under-calls, tissue-dependent
    adata = adata[(adata.obs['cell_area'] > lo) & (adata.obs['cell_area'] < hi)].copy()
sc.pp.filter_genes(adata, min_cells=5)

# Spot branch instead (Visium): tissue-dependent floors -- the OSTA DLPFC example, not universal law
# sc.pp.filter_cells(adata, min_counts=600)
# sc.pp.filter_cells(adata, min_genes=400)
# adata = adata[adata.obs['pct_counts_mt'] < 28].copy()
```

## Normalization -- the central decision

Do not reach reflexively for `normalize_total` + `log1p`. The shipped Squidpy tutorials run it for both Xenium and MERFISH, so it is the de-facto default -- and it is exactly what the benchmark papers argue is biased for spatial data. Decide deliberately from the table, and because methods compete here, verify current best practice against the installed tool's docs and the latest benchmarks before committing.

### Normalization-method table

| Method | Assumption | Best when | Fails when |
|---|---|---|---|
| `normalize_total` + `log1p` | library size = pure technical nuisance | cross-platform comparability; quick default; tool tutorials | spatial -- removes spatially-structured biology (Bhuva 2024); imaging skewed panel |
| Analytic Pearson residuals | closed-form NB offset; depth as fixed offset | whole-transcriptome Visium HVG/PCA | imaging targeted panel -- still gene-count-based, inherits panel-skew bias (Atta/Fan 2024) |
| SCTransform v2 | regularized NB GLM, depth slope fixed | whole-transcriptome UMI / Visium | does NOT fix skewed imaging panels (gene-count-based) |
| Cell volume/area | concentration is the biological quantity | IMAGING skewed panel (Moffitt-style) | denominator needs reliable segmentation; cannot fix segmentation error itself |
| SpaNorm (spatially-aware) | library size and biology are entangled; remove only library-size component | spot AND imaging; preserve spatial structure | newer; R/Bioconductor |

**Goal (spot, whole-transcriptome):** Stabilize depth for HVG/PCA while keeping raw counts, accepting that crude library-size division can blur domains.

**Approach:** Stash raw counts, then either run the standard log1p pipeline knowingly or prefer analytic Pearson residuals for feature selection on whole-transcriptome Visium.

```python
adata.layers['counts'] = adata.X.copy()                    # stash raw -- HVG flavors and re-normalization need it
sc.pp.normalize_total(adata)                               # target_sum=None scales to the dataset MEDIAN, not the arbitrary 1e4
sc.pp.log1p(adata)                                         # library size carries biology -- this can blur spatial domains
# Whole-transcriptome Visium feature selection alternative (gene-count-based, fine here, NOT for imaging panels):
# sc.experimental.pp.normalize_pearson_residuals(adata)
```

**Goal (imaging, targeted panel):** Normalize without injecting panel-composition bias, using a denominator independent of gene counts.

**Approach:** Divide each cell's counts by its segmented area/volume (copies per unit area), then log-transform -- the Moffitt-style fix benchmarks favour over Pearson residuals for skewed panels.

```python
adata.layers['counts'] = adata.X.copy()
if 'cell_area' in adata.obs:                               # area/volume denominator is panel-composition-independent
    sf = adata.obs['cell_area'].values / adata.obs['cell_area'].median()
    adata.X = adata.X / sf[:, None]
    sc.pp.log1p(adata)
# If no segmentation area is available, prefer SpaNorm (R) over reflexive normalize_total on a skewed panel
```

## Common Errors

| Symptom | Cause | Fix |
|---|---|---|
| Nearly all imaging cells filtered out | scRNA `min_counts=500` floor on tens-of-transcript cells | Use a low floor (~10 transcripts/cell); branch QC on the platform fork |
| Spatial domains blur / merge after normalization | Crude library-size division erased a cellularity/anatomy gradient (library size carries biology) | Prefer SpaNorm or volume/area; if using log1p, know it can blur domains |
| Fold-change sign flips between normalizations | Gene-count size factor is panel-composition-dependent on a skewed imaging panel | Use non-gene-count (cell area/volume) normalization; Pearson/SCT do NOT fix it |
| `pct_counts_mt` is all zero / NaN | Mito genes are not on the targeted imaging panel | Skip mito-% QC for imaging; QC on transcript floor + cell area instead |
| "Doublet" cells flagged by high gene count | genes/cell ceiling IS the panel size -- not a doublet signal | Drop the high-genes heuristic for imaging; use cell area / spatial doublets |
| Control features cluster as their own group | Negative-control probes/codewords left in the matrix | Compute control FDR, then subset to real genes before clustering |
| Smallest cell type vanished after filtering | A count floor preferentially deleted small real cells (lymphocytes) | Inspect spatially where cuts fall; lower the floor; check composition before/after |
| Claimed a novel cell-state signature from imaging marker genes | An imaging panel (even 5,000-plex) is pre-selected for KNOWN biology; off-panel genes are absent by design, not by expression | Treat absence of an off-panel gene as uninformative; de-novo state discovery is bounded by the panel -- corroborate on whole-transcriptome data before claiming novelty |
| QC looks fine in violins but a region is empty | Spatial QC gradient (edge/permeabilization artifact) invisible in violins | Map QC onto tissue with `sq.pl.spatial_scatter` before thresholding |
| Counts inflated ~2x after re-running normalization | Normalized already-normalized data | Normalize raw once; restore from `layers['counts']` |

## Related Skills

- spatial-data-io - load Visium/Xenium/MERFISH and reach the molecule table vs the segmentation-derived matrix
- image-analysis - segment cells from imaging data, the upstream error source that sets imaging QC and cell area
- spatial-deconvolution - the next step for spot data, where library size and reference choice decide proportions
- single-cell/preprocessing - the scRNA QC/normalization baseline these thresholds deliberately depart from
- single-cell/clustering - cluster the QC'd cells; resolution is not a truth knob
- single-cell/cell-annotation - label-transfer typing for a targeted panel (de-novo marker discovery is panel-bounded)

## References

- Bhuva DD, Tan CW, Salim A, et al. (2024) Library size confounds biology in spatial transcriptomics data. Genome Biology 25:99. DOI 10.1186/s13059-024-03241-7
- Atta L, Clifton K, Anant M, Aihara G, Fan J (2024) Gene count normalization in single-cell imaging-based spatially resolved transcriptomics. Genome Biology 25:153. DOI 10.1186/s13059-024-03303-w
- Lause J, Berens P, Kobak D (2021) Analytic Pearson residuals for normalization of single-cell RNA-seq UMI data. Genome Biology 22:258. DOI 10.1186/s13059-021-02451-7
- Palla G, Spitzer H, Klein M, et al. (2022) Squidpy: a scalable framework for spatial omics analysis. Nature Methods 19:171-178. DOI 10.1038/s41592-021-01358-2
- Salim A, Bhuva DD, Chen C, et al. (2025) SpaNorm: spatially-aware normalisation for spatial transcriptomics data. Genome Biology 26:109. DOI 10.1186/s13059-025-03565-y
- Moffitt JR, Bambah-Mukku D, Eichhorn SW, et al. (2018) Molecular, spatial, and functional single-cell profiling of the hypothalamic preoptic region. Science 362:eaau5324. DOI 10.1126/science.aau5324
- Janesick A, Shelansky R, Gottscho AD, et al. (2023) High resolution mapping of the tumor microenvironment using integrated single-cell, spatial and in situ analysis. Nature Communications 14:8353. DOI 10.1038/s41467-023-43458-x
- Maynard KR, Collado-Torres L, Weber LM, et al. (2021) Transcriptome-scale spatial gene expression in the human dorsolateral prefrontal cortex. Nature Neuroscience 24:425-436. DOI 10.1038/s41593-020-00787-0
<!-- END FILE: spatial-transcriptomics/spatial-preprocessing/SKILL.md -->

## 子目录：spatial-transcriptomics/spatial-proteomics

<!-- BEGIN FILE: spatial-transcriptomics/spatial-proteomics/SKILL.md -->
---
name: bio-spatial-transcriptomics-spatial-proteomics
description: Analyzes multiplexed antibody-imaging data (CODEX/PhenoCycler, MIBI-TOF, IMC, CyCIF, Opal/Vectra mIF) as continuous protein intensity rather than transcript counts, using scimap and squidpy. Use when choosing an intensity transform/normalization (arcsinh cofactor vs z-score vs percentile -- NOT log1p-of-counts) and correcting channel spillover and antibody-batch effects; deciding whether to phenotype by gating or by clustering on intensities; recognizing that a bounded antibody panel makes marker absence uninformative; treating whole-cell segmentation (Mesmer) as the dominant error source; and knowing which platform applies and when to defer to the imaging-mass-cytometry skills for the IMC pipeline.
tool_type: python
primary_tool: scimap
---

## Version Compatibility

Reference examples tested with: scimap 2.0+, scanpy 1.10+, anndata 0.10+, squidpy 1.4+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Spatial Proteomics Analysis

**"Analyze my CODEX/MIBI/IMC multiplexed-imaging data"** -> Turn a cell-by-marker protein-intensity matrix into phenotyped cells and spatial neighborhoods, while treating intensity as a continuous, confounded signal.
- Python: per-marker `arcsinh`/z-score transform -> spillover/batch correction -> `scimap.tl.phenotype_cells()` (gating) or `scimap.tl.cluster()` (clustering) -> `squidpy.gr.nhood_enrichment()`

## Governing Principle

Protein intensity is continuous with antibody, batch, and staining confounds -- it is not a molecule count, and treating it like one is a category error that propagates through every downstream result.

A multiplexed-imaging measurement is the reporter signal (fluorescence photons or secondary-ion/metal counts) for an antibody bound to its epitope. That signal scales with antibody affinity, conjugation efficiency, staining-day conditions, fixation, and detector response -- none of which are the abundance of the protein, and all of which differ between markers and between samples. Consequences that separate this from RNA-based spatial omics: there is no Poisson/NB count model, so the variance-stabilizing transform is arcsinh (or z-score/percentile), NEVER log1p applied as if the values were UMIs; metal/fluor channels leak into each other (spillover) and must be compensated; and antibody-batch and staining variation must be normalized before any cross-sample comparison. Hickey 2021 (*Front Immunol* 12:727626) made the cost concrete: crossing 5 normalizations x 4 clustering methods on ONE CODEX dataset produced 20 different cell-type annotations -- the normalization-and-clustering choice, not the biology, dominated the phenotype calls.

The antibody panel is targeted, so absence is uninformative. A 20-100 marker panel is chosen a priori; the phenotype space is bounded by it exactly as an imaging RNA panel (Xenium/MERFISH/CosMx) bounds detectable transcripts. A cell type whose defining markers are off-panel is invisible or silently mis-assigned to the nearest panel-defined type -- there is no de-novo discovery. "Marker X is absent" usually means "X was not stained," not "the protein is not there."

Segmentation is the dominant downstream error source -- the per-cell intensity vector is only as good as the cell mask. There is no native cell in an image; a cell-by-marker matrix exists only after an algorithm draws boundaries. Lateral spillover of membrane/cytoplasmic signal into neighboring masks fabricates phantom double-positive cells (a CD3+CD20+ "cell" is usually a T cell touching a B cell), and every neighborhood, niche, and proximity result inherits that error. Whole-cell segmentation on a membrane/boundary stain (Mesmer/DeepCell, trained on the ~1M-cell TissueNet, is the multiplexed-imaging standard) is the highest-leverage decision; nucleus-only loses cytoplasmic signal and nucleus-expansion assumes round equal cells. The IMC/MIBI pipeline mechanics live in the imaging-mass-cytometry category -- this skill owns the platform breadth and the intensity reframe; defer the deep pipeline there.

## The Platform-Breadth Decision

This skill owns BREADTH across antibody-based platforms; IMC pipeline DEPTH lives in imaging-mass-cytometry. The first question is which platform produced the data, because chemistry sets the confounds.

| Platform | Chemistry | Markers | Strengths | Dominant confounds |
|----------|-----------|---------|-----------|--------------------|
| CODEX / PhenoCycler (Goltsev 2018) | DNA-barcoded antibodies, iterative fluorescent reporter cycles | ~50-60+ | High-plex on a standard fluorescence microscope; sub-um optical | Cycle-to-cycle registration drift, photobleaching/tissue degradation over many cycles; continuous intensity |
| MIBI-TOF (Angelo 2014; Keren 2019) | Lanthanide-metal antibodies, ion beam + TOF mass spec | ~40 metal channels | High resolution (~260-500 nm); low autofluorescence | Slow, small FOV; semi-quantitative (secondary-ion yield, detector); isotopic/channel crosstalk (spillover) |
| IMC (Giesen 2014) | Metal-isotope antibodies, UV laser ablation + CyTOF | ~40 metal channels | Metal multiplexing, no autofluorescence | ~1 um, slow ablation; metal-channel spillover (Chevrier 2018); conjugation-efficiency bias. Pipeline -> imaging-mass-cytometry |
| CyCIF / t-CyCIF (Lin 2018) | Cyclic IF: stain ~4 dyes, image, bleach, restain | up to ~60 | Conventional optical microscope, accessible | Bleach/restain degrades antigenicity; registration drift; autofluorescence |
| Opal / Vectra mIF (Parra 2017) | Tyramide-amplified multispectral IF | ~6-8 | Clinical-grade, FFPE-validated | Low plex; spectral unmixing artifacts; amplification nonlinearity |

CODEX/CyCIF/Opal yield continuous FLUORESCENCE intensity; MIBI/IMC yield semi-quantitative METAL counts (still not transcript counts -- they carry detector and spillover effects, not Poisson sampling). All five share the targeted-panel and segmentation traps above. When the data is specifically IMC or MIBI and the question is the end-to-end processing workflow (spillover compensation, segmentation execution, FlowSOM phenotyping on metal channels), defer to imaging-mass-cytometry rather than reimplementing it here.

## Transform and Normalize Intensities

**Goal:** Put marker intensities on a comparable, variance-stabilized scale and remove antibody-batch and staining confounds before phenotyping -- without imposing a count model.

**Approach:** Apply arcsinh with a per-dataset-tuned cofactor (or z-score/percentile), then correct channel spillover and batch; choose the transform deliberately, because this choice dominates the cell-type calls.

| Transform | Form | Best when | Fails / caveat |
|-----------|------|-----------|----------------|
| arcsinh (cofactor) | `arcsinh(x / cofactor)` | Mass-cytometry-like intensities (CyTOF/IMC/MIBI); compresses high values, near-linear near zero | Cofactor ~5 is a CyTOF CONVENTION (Bendall 2011), NOT auto-optimal for imaging -- too small over-expands near-zero noise into spurious populations; tune and sanity-check per dataset |
| z-score (per marker) | `(x - mean) / sd` | Cross-marker comparability for clustering | Sensitive to outliers; assumes roughly symmetric post-transform spread |
| percentile / min-max (per marker) | clip to e.g. 1st-99th pct, scale 0-1 | Gating-style cutoffs; robust to extreme bright pixels | Throws away absolute scale; per-image rescaling can erase real cross-sample differences |
| log1p-of-counts | `log(1 + x)` with NB/Poisson tooling | RNA UMI counts | WRONG for intensity -- there is no count process; imposes a model the data does not follow |

scimap's `pp.rescale` fits a per-marker two/three-component Gaussian mixture to set the 0-1 gating scale (an intensity-aware step, distinct from log1p-as-counts); for clustering, an explicit arcsinh or z-score on `adata.X` is the transparent choice.

```python
import numpy as np
import scimap as sm

# Tune the cofactor: start at 5 (CyTOF convention) but verify the near-zero
# population is not split into a phantom 'positive' cluster for each marker.
cofactor = 5
adata.layers['intensity'] = adata.X.copy()              # stash raw intensities
adata.X = np.arcsinh(adata.X / cofactor)                # variance-stabilize; NOT log1p-of-counts

# Antibody/staining-batch correction across images or staining days.
# Intensity differences between batches masquerade as biology -- correct before merging.
sm.pp.combat(adata, batch_key='imageid')                # batch_key names the confound column in .obs
```

Channel spillover (isotopic impurity and oxide/abundance-sensitivity crosstalk for metals; spectral bleed for fluorophores) creates false double-positive cells. Estimate a spillover matrix from single-stain bead controls and correct by non-negative least squares (Chevrier 2018, implemented in CATALYST/spillR). For IMC/MIBI specifically, run compensation through the imaging-mass-cytometry/data-preprocessing skill rather than reimplementing the matrix here.

## Phenotype Cells: Gating vs Clustering

**Goal:** Assign each cell a cell-type label from its marker-intensity vector.

**Approach:** Choose GATING (flow-cytometry-style positive/negative thresholds encoded as a marker workflow) when the panel has canonical lineage markers and the types are known a priori, or CLUSTERING (Leiden/PhenoGraph/FlowSOM on transformed intensities) for unsupervised discovery within the bounded panel; gating and clustering can give materially different calls, and cluster boundaries shift with the transform, cofactor, k, and segmentation spillover.

scimap gating expects a phenotype-workflow DataFrame, not a dict: first column = group, second = cell-type name, remaining columns = marker names holding `pos`/`neg`/`allpos`/`allneg`/`anypos`/`anyneg`.

```python
import pandas as pd
import scimap as sm

# Build the gating workflow (or load a CSV). 'allpos' = all listed markers must clear the gate.
workflow = pd.DataFrame([
    ['lineage', 'T_cell',     'allpos', 'allpos', 'neg',    'neg'],
    ['lineage', 'B_cell',     'allpos', 'neg',    'allpos', 'neg'],
    ['lineage', 'Macrophage', 'allpos', 'neg',    'neg',    'allpos'],
    ['lineage', 'Tumor',      'neg',    'neg',    'neg',    'neg'],
], columns=['group', 'phenotype', 'CD45', 'CD3', 'CD20', 'CD68'])

sm.pp.rescale(adata, gate=None, method='by_image')       # per-marker GMM sets the 0-1 scale; 'by_image' rescales each image separately
sm.tl.phenotype_cells(adata, phenotype=workflow, gate=0.5, label='phenotype')   # gate=0.5 after rescale
```

```python
# Unsupervised alternative: cluster the transformed intensities, then annotate clusters by marker means.
sm.tl.cluster(adata, method='leiden', resolution=1.0, label='leiden')
# A 'protein absent' cluster may simply lack the marker on the panel -- annotate against the panel, not the transcriptome.
```

Phenotyping on a targeted panel cannot discover a type whose markers are off-panel; an unexpected "negative-for-everything" cluster is often an unstained type, not a novel state. Audit phantom double-positives (e.g. CD3+CD20+) as likely segmentation spillover before treating them as biology.

## Spatial Neighborhood and Interaction Analysis

**Goal:** Quantify which phenotypes are spatial neighbors more or less than chance, and summarize recurrent cellular neighborhoods.

**Approach:** Build a spatial graph on cell centroids, then run a permutation-based neighborhood-enrichment test; for niches, summarize each cell's k-nearest-neighbor window by composition and cluster the windows (Schurch 2020 cellular-neighborhoods logic). Co-occurrence is not communication, and a "neighborhood" inherits every segmentation/normalization error upstream.

```python
import squidpy as sq

sq.gr.spatial_neighbors(adata, coord_type='generic', n_neighs=10)   # imaging cells are a point cloud, not a grid -> 'generic'
sq.gr.nhood_enrichment(adata, cluster_key='phenotype')              # label-permutation null; z-scores in adata.uns
sq.pl.nhood_enrichment(adata, cluster_key='phenotype')
```

```python
# Recurrent cellular neighborhoods (niches): per-cell composition of the local window, then cluster.
sm.tl.spatial_count(adata, phenotype='phenotype', method='knn', knn=10, label='neighborhood_counts')
sm.tl.cluster(adata, method='kmeans', k=8, use_raw=False, label='neighborhood')   # k is a biological choice; report k +/- 1 sensitivity
```

The neighbor count k and the upstream phenotype calls both define the result; report the window size and show sensitivity. On a 20-100 marker panel the relevant ligand AND receptor AND cofactors are rarely all present, so multiplexed-imaging "communication" is almost always cell-type PROXIMITY (niche co-occurrence), not measured ligand-receptor co-localization -- a weaker inference than transcriptomic LR, because the LR pair was never measured.

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| Spurious "positive" populations near zero; clusters that split noise | Treated intensity as counts with `log1p`, or used an untuned tiny arcsinh cofactor | Use arcsinh with a per-dataset-tuned cofactor (start ~5, verify near-zero is not over-expanded), or z-score/percentile -- never log1p-of-counts |
| Phantom CD3+CD20+ (or any lineage-incompatible) double-positive cells | Channel spillover and/or segmentation lateral spillover between adjacent cells | Compensate spillover (NNLS, Chevrier 2018) and audit segmentation; treat double-positives as artifacts until proven |
| Cell types differ wildly between two runs of the same data | Normalization x clustering choice dominates calls (Hickey 2021: 20 annotations from one CODEX dataset) | Fix and report the transform, cofactor, normalization, and clustering; do not present one pipeline's calls as ground truth |
| Cross-sample comparison shows a "batch" cell type | Antibody-lot/staining/fixation intensity differences not normalized | Correct batch (combat or per-image rescale) before merging or comparing samples |
| Concluded a cell type or marker is "absent" | Read panel absence as biological absence on a bounded antibody panel | State that absence on a targeted panel is uninformative; the marker was likely not stained |
| Neighborhood/interaction result looks strong but is not reproducible | Built on bad segmentation masks; enrichment inherits the mask error | Validate segmentation (membrane-stain whole-cell, Mesmer) before trusting any spatial result |
| `sm.tl.spatial_cluster` returns one cluster or nonsense | Ran it before building the neighborhood matrix it reads | Compute `sm.tl.spatial_count` (or `sm.tl.spatial_lda`) first, then point `spatial_cluster(df_name=...)` at that result |
| `phenotype_cells` errors or mislabels everything | Passed a dict instead of the workflow DataFrame, or did not `rescale` first | Pass a group/phenotype/marker DataFrame with pos/neg/allpos codes; run `sm.pp.rescale` before phenotyping |

## Related Skills

- image-analysis - whole-cell segmentation upstream of every per-cell intensity vector (the dominant error source)
- imaging-mass-cytometry/cell-segmentation - Mesmer/Cellpose segmentation execution and error propagation for IMC/MIBI
- imaging-mass-cytometry/phenotyping - FlowSOM/Phenograph phenotyping on metal channels and the double-positive artifact
- spatial-transcriptomics/spatial-multiomics - integrating spatial proteomics with matched spatial transcriptomics (ADT/CytAssist)
- spatial-transcriptomics/spatial-statistics - permutation nulls, neighborhood enrichment, and co-occurrence shared with squidpy

## References

- Goltsev Y, Samusik N, Kennedy-Darling J, et al. (2018) Deep profiling of mouse splenic architecture with CODEX multiplexed imaging. Cell 174(4):968-981. DOI 10.1016/j.cell.2018.07.010
- Angelo M, Bendall SC, Finck R, et al. (2014) Multiplexed ion beam imaging of human breast tumors. Nature Medicine 20(4):436-442. DOI 10.1038/nm.3488
- Keren L, Bosse M, Thompson S, et al. (2019) MIBI-TOF: a multiplexed imaging platform relates cellular phenotypes and tissue structure. Science Advances 5(10):eaax5851. DOI 10.1126/sciadv.aax5851
- Giesen C, Wang HAO, Schapiro D, et al. (2014) Highly multiplexed imaging of tumor tissues with subcellular resolution by mass cytometry. Nature Methods 11(4):417-422. DOI 10.1038/nmeth.2869
- Lin J-R, Izar B, Wang S, et al. (2018) Highly multiplexed immunofluorescence imaging of human tissues and tumors using t-CyCIF and conventional optical microscopes. eLife 7:e31657. DOI 10.7554/eLife.31657
- Parra ER, Uraoka N, Jiang M, et al. (2017) Validation of multiplex immunofluorescence panels using multispectral microscopy for immune-profiling of FFPE human tumor tissues. Scientific Reports 7(1):13380. DOI 10.1038/s41598-017-13942-8
- Greenwald NF, Miller G, Moen E, et al. (2022) Whole-cell segmentation of tissue images with human-level performance using large-scale data annotation and deep learning (Mesmer/DeepCell). Nature Biotechnology 40(4):555-565. DOI 10.1038/s41587-021-01094-0
- Stringer C, Wang T, Michaelos M, Pachitariu M (2021) Cellpose: a generalist algorithm for cellular segmentation. Nature Methods 18(1):100-106. DOI 10.1038/s41592-020-01018-x
- Chevrier S, Crowell HL, Zanotelli VRT, et al. (2018) Compensation of signal spillover in suspension and imaging mass cytometry. Cell Systems 6(5):612-620. DOI 10.1016/j.cels.2018.02.010
- Bendall SC, Simonds EF, Qiu P, et al. (2011) Single-cell mass cytometry of differential immune and drug responses across a human hematopoietic continuum. Science 332(6030):687-696. DOI 10.1126/science.1198704
- Hickey JW, Tan Y, Nolan GP, Goltsev Y (2021) Strategies for accurate cell type identification in CODEX multiplexed imaging data. Frontiers in Immunology 12:727626. DOI 10.3389/fimmu.2021.727626
- Schurch CM, Bhate SS, Barlow GL, et al. (2020) Coordinated cellular neighborhoods orchestrate antitumoral immunity at the colorectal cancer invasive front. Cell 182(5):1341-1359. DOI 10.1016/j.cell.2020.07.005
<!-- END FILE: spatial-transcriptomics/spatial-proteomics/SKILL.md -->

## 子目录：spatial-transcriptomics/spatial-statistics

<!-- BEGIN FILE: spatial-transcriptomics/spatial-statistics/SKILL.md -->
---
name: bio-spatial-transcriptomics-spatial-statistics
description: Detects spatially variable genes, spatial autocorrelation, and cell-type colocalization for spatial transcriptomics using Squidpy with PySAL/esda for local statistics. Use when choosing an SVG method by its null and scaling (SpatialDE/SPARK GP variance-component vs SPARK-X/nnSVG linear vs Moran/Geary graph autocorrelation); separating genes that are spatially variable because of cell-type composition from genes regulated within a cell type; choosing the right autocorrelation statistic (global Moran/Geary vs Getis-Ord hot/cold spots vs local LISA and its FDR trap); and choosing a colocalization null strong enough to defeat the abundance/compartment confound (conditional or toroidal vs the weak Squidpy default permutation).
tool_type: python
primary_tool: squidpy
---

## Version Compatibility

Reference examples tested with: squidpy 1.4+, scanpy 1.10+, anndata 0.10+, esda 2.5+, libpysal 4.9+ (SPARK, SPARK-X, and nnSVG are R/Bioconductor packages)

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Spatial Statistics

**"Find spatially variable genes / run Moran's I / test which cell types colocalize"** -> Quantify spatial structure in expression or in cell-type arrangement against an explicit null model.
- Python: `squidpy.gr.spatial_autocorr` (Moran/Geary), `squidpy.gr.nhood_enrichment`, `squidpy.gr.co_occurrence`, `esda.Moran_Local`/`esda.getisord.G_Local` (LISA, Getis-Ord)
- R: SPARK / SPARK-X / nnSVG (SVG), `spdep` (Moran/Geary/Getis-Ord/LISA)

## Governing Principle

Two reframes decide whether a spatial-statistics result means anything. Both are silent failures: the code runs, the numbers look clean, and the interpretation is wrong.

A "spatially variable gene" is not necessarily spatially REGULATED. Moran's I, Geary's C, SPARK-X, and SpatialDE all detect that a gene's expression is spatially autocorrelated -- but a gene that is simply a marker of a spatially clustered cell type scores as "spatially variable" with zero cell-intrinsic spatial regulation, purely because the CELL TYPE is spatially organized. A hepatocyte gene in zonated liver, MAG in white matter, KRT17 in epithelium: all top SVGs, none of them regulated in space. This cell-type-driven signal swamps the genuinely interesting cell-type-INDEPENDENT signal (a gene graded across a niche WITHIN one cell type). Sample-wide SVG lists therefore largely re-derive marker genes and overlap heavily with HVGs -- if the SVG list is roughly the HVG list, the spatial test added almost nothing. The interesting question (within-type spatial regulation) needs cell-type-aware methods (C-SIDE, CTSV, CELINA/Celina), which are themselves unsettled and carry their own false positives. Decision: if the question is "where is tissue organized," sample-wide SVG is correct (the cell-type structure IS the answer); if the question is "which genes are regulated beyond cell identity," sample-wide SVG is the WRONG tool -- test within cell type or regress out composition first.

The null and the graph define the result. Every spatial statistic is computed on a neighbor graph (a weights matrix W) against a null distribution, and both are researcher choices, not properties of the tissue. Change kNN k from 6 to 30 and Moran's I, the enrichment z-scores, and the SVG ranking all move. Change the colocalization null from global label-shuffle to within-compartment and most "A is near B" claims evaporate. SVG methods disagree heavily across the literature precisely because each tests a DIFFERENT null (variance-component-zero vs covariance-independence vs graph-autocorrelation-zero) -- that disagreement is expected, not a bug. The honest workflow names the null, names the graph (cross-ref spatial-neighbors), and reports whether a hit survives a second graph or a stronger null.

## Choosing an SVG Method

**Goal:** Pick a spatially-variable-gene test whose null hypothesis and computational scaling match the platform and the biological question.

**Approach:** Match GP variance-component methods to small Gaussian/count data, linear-scaling methods to single-cell-resolution data, and treat the SVG list as method-conditional -- cross-method intersection is more trustworthy than any single ranking, though it is small.

| Method | Null it tests | Scaling | Best when | Fails when |
|--------|---------------|---------|-----------|------------|
| SpatialDE (GP) | spatial variance component = 0 at the tested length scale | O(n^3); infeasible past ~1e4 locations | Small Visium-scale, Gaussian on log-normalized | Sparse/low counts violate Gaussian; fixed length-scale grid misses other scales |
| SPARK (count GLSM) | no pattern matching any of 10 fixed kernels | O(n^3)-ish (PQL); slow at large n | Small count data; want Poisson model, not Gaussian | Pattern unlike its 10 kernels; still cell-type-confounded |
| SPARK-X | expression covariance independent of location covariance | LINEAR in n and genes | 1e4-1e6 cells (MERFISH/Xenium/CosMx) needing scalability | Fixed location kernels miss unusual length scales; low power on small focal hotspots |
| nnSVG (NNGP) | spatial variance = 0, with a per-gene length scale | LINEAR in n | Length scales genuinely differ across genes; large single-cell data | Still cell-type-confounded; more compute per gene than SPARK-X; needs adequate counts |
| Moran's I / Geary's C | no autocorrelation on graph W | Fast (sparse W) | Quick screen on an existing neighbor graph | Single fixed scale (the graph); misses multi-focal/small hotspots |

There is no uniformly best SVG method; power is pattern-specific (SPARK-X, nnSVG, and Moran's I all have LOW power for genes high in small focal areas). Methods evolve fast -- verify the current benchmark before committing. Threshold on EFFECT SIZE (fraction of spatial variance), not p alone: with thousands of cells, trivial autocorrelation reaches tiny p-values.

## Computing Spatial Autocorrelation with Squidpy

**Goal:** Rank genes by graph-based spatial autocorrelation as a fast SVG screen.

**Approach:** Build a neighbor graph, run Moran's I (or Geary's C) per gene with a permutation/analytic p-value and FDR, then read effect size before significance.

```python
import squidpy as sq
import scanpy as sc

# The graph IS the model: k, coord_type, and units all change the result (see spatial-neighbors)
sq.gr.spatial_neighbors(adata, coord_type='generic', n_neighs=6)   # 6 mimics the Visium hex lattice

# genes=None defaults to highly_variable if present; n_perms adds a permutation null, corr_method applies FDR
sq.gr.spatial_autocorr(adata, mode='moran', n_perms=100, corr_method='fdr_bh')   # statsmodels name, not 'benjamini-hochberg'
moran = adata.uns['moranI']                  # columns: I, pval_norm, pval_norm_fdr_bh, ...

# Threshold on effect size (I) AND FDR, not p alone -- large n makes trivial autocorrelation 'significant'
svg = moran[(moran['I'] > 0.1) & (moran['pval_norm_fdr_bh'] < 0.05)].sort_values('I', ascending=False)
```

A top-ranked SVG here is a hypothesis about spatial structure, NOT evidence of spatial regulation. Before interpreting, compare the SVG list to the HVG list: the overlap is cell-type marker genes; the SVG-not-HVG subset (modest-amplitude gradients) is where spatial information actually lives.

## Choosing an Autocorrelation Statistic

**Goal:** Match the statistic to the spatial question -- "is this gene clustered" is a different question from "where is it HIGH" and from "is THIS region a cluster."

**Approach:** Use a global statistic for one tissue-wide number, Getis-Ord when the sign (hot vs cold) matters, and local LISA for non-stationary tissue -- but pay the local multiple-testing tax correctly.

| Statistic | Global / local | Hot vs cold? | Use when |
|-----------|----------------|--------------|----------|
| Moran's I | global | NO (clustering of like values only) | One number: is this gene spatially structured across the whole section |
| Geary's C | global | NO | Same as Moran but more sensitive to LOCAL/short-range differences; disagreement with Moran is informative |
| Getis-Ord Gi* | local | YES -- separates high-clusters from low-clusters | "Where is this gene HIGH" -- hot/cold spot mapping |
| Local Moran / LISA | local | partial (HH/LL/HL/LH quadrants) | Non-stationary tissue: per-location clusters and spatial outliers |

Moran's I and Geary's C cannot tell a hot spot from a cold spot -- both flag "similar values cluster" regardless of high or low. Choosing Moran when the question is "where is this gene HIGH" is a category error; use Getis-Ord Gi*. A non-significant GLOBAL Moran's I does NOT mean "no spatial structure": over heterogeneous tissue, positive autocorrelation in one region cancels negative in another, so use local statistics for non-stationary sections.

```python
from esda.getisord import G_Local
from esda.moran import Moran_Local
from libpysal.weights import KNN

coords = adata.obsm['spatial']
w = KNN.from_array(coords, k=6)
w.transform = 'r'                            # row-standardized; changes the value AND its variance vs binary W

gene = adata[:, 'GENE1'].X.toarray().ravel()
gi = G_Local(gene, w, transform='B', star=True, permutations=999)   # star=True -> Gi* (includes self); binary weights for Getis-Ord
lisa = Moran_Local(gene, w, permutations=999)            # conditional-permutation local null
adata.obs['GENE1_hotspot'] = gi.Zs                       # positive Z = hot spot, negative = cold spot
adata.obs['GENE1_lisa_q'] = lisa.q                       # 1=HH, 2=LH, 3=LL, 4=HL
```

Local statistics carry a DOUBLE trap. There are n tests (one per location), so uncorrected LISA/Gi* maps are mostly false positives -- FDR is mandatory, and Anselin recommends stricter base cutoffs (0.01/0.005/0.001), not 0.05. Worse, the local statistics are themselves spatially autocorrelated (adjacent locations share neighbors, so adjacent I_i values are correlated), which violates the independence assumption of standard BH-FDR; the effective number of tests is far below n. Conditional permutation gives the correct local null but does not fix the cross-location dependence. Treat the cluster map as exploratory, not a set of independent discoveries.

## Testing Cell-Type Colocalization

**Goal:** Decide whether two cell types are SPECIFICALLY associated in space, not merely both abundant or both in the same compartment.

**Approach:** Choose a permutation null strong enough to defeat the abundance/compartment confound; the Squidpy default answers only the weak question, and a co-occurrence distance profile is more informative than a single z-score.

| Null model | What it permutes | Controls for | Misses |
|------------|------------------|--------------|--------|
| Global label permutation (Squidpy `nhood_enrichment` default) | all labels over all positions | graph topology, marginal counts | tissue compartmentalization -- two abundant co-compartment types pass trivially |
| Conditional / within-compartment permutation | labels within a region only | shared-compartment forcing | cross-compartment questions; the region choice is itself a degree of freedom |
| Toroidal shift | whole label field translated (wrapped) | each type's first-order density pattern | anisotropy; boundary realism (wrapping a bounded tissue is artificial) |
| Grid-tile shuffle across scales (CRAWDAD) | labels within tiles of size s | structure above scale s -- isolates colocalization AT scale s | within-tile structure below s |

The single most common error in spatial-omics papers is reading a positive `nhood_enrichment` z-score as a specific A-B interaction. Under the weak global-permutation null it usually reflects co-compartmentalization plus abundance: two stromal populations, or tumor plus tumor-associated macrophages both in the tumor bed, pass trivially. A specific-affinity claim must SURVIVE a stronger null (conditional/within-compartment, toroidal shift preserving each type's density, or CRAWDAD's scale-explicit tiles). Rare-type enrichment is the least trustworthy: few edges give high-variance, often spuriously large |z| -- be most skeptical exactly where the biology is most exciting (a rare type near the tumor).

For clustering as a function of distance rather than a single graph z, Ripley's K/L (`squidpy.gr.ripley`, mode `'L'`) counts within-cluster neighbors within radius r against a complete-spatial-randomness expectation, so it reads as clustering vs dispersion ACROSS scale per cell type (squidpy computes the univariate L per cluster; a true bivariate cross-K answering "are A and B closer than chance, at what radius" needs a dedicated point-process tool such as spatstat). Its assumptions are the geostatistics ones tissue violates: a bounded, holey, non-stationary window. EDGE CORRECTION is mandatory and usually omitted -- without it, counts near the tissue boundary or a necrotic hole are biased DOWN and read as false depletion, so an ROI with gaps needs an edge-corrected estimator (or restrict analysis to the interior).

```python
sq.gr.spatial_neighbors(adata, coord_type='generic', delaunay=True)   # nhood_enrichment reuses this stored graph

# Global label-permutation null -- the WEAK question: more adjacent than complete spatial randomness?
sq.gr.nhood_enrichment(adata, cluster_key='cell_type', n_perms=1000)
z = adata.uns['cell_type_nhood_enrichment']['zscore']

# co_occurrence gives a DISTANCE PROFILE (at what scale colocalization appears/vanishes), unlike a single z
sq.gr.co_occurrence(adata, cluster_key='cell_type')
```

Cellular Neighborhoods (Schurch/Nolan: cluster per-cell windows of neighbor composition) have NO inferential null at all -- they are descriptive k-means clusters whose number and window size are user knobs. They are useful summaries but routinely over-read as tested findings; the number of neighborhoods is chosen, not discovered, and identity shifts with window size. Test them downstream (neighborhood composition vs outcome), do not report them as significant in themselves.

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| Top SVGs are all known cell-type markers; SVG list ~= HVG list | Sample-wide SVG re-derives markers of spatially clustered cell types (cell-type-driven, not regulated) | Ask within-type: regress out cell-type composition or use ctSVG (C-SIDE/CTSV/CELINA); report the SVG-not-HVG subset |
| Moran's I finds "clustering" but cannot locate where the gene is HIGH | Moran/Geary detect clustering of like values, blind to high vs low | Use Getis-Ord Gi* for hot/cold spots |
| LISA/Gi* map is mostly "significant"; thousands of hits | n tests, AND local statistics are spatially autocorrelated so naive BH-FDR is invalid | FDR with stricter cutoffs (0.001); conditional permutation; treat map as exploratory, not independent discoveries |
| Confident "cell type A interacts with B" that vanishes on a second look | Default `nhood_enrichment` global-permutation null only beats complete randomness; abundant co-compartment types pass trivially | Demand survival under a conditional/within-compartment or toroidal null; report abundances |
| Global Moran's I near zero but tissue is clearly structured | Non-stationarity: opposite-sign local regions cancel in one global number | Use local statistics (LISA/Gi*); stratify by region |
| SVG ranking changes completely between two runs/tools | Different graph (k, Delaunay vs kNN) or different null -- methods test different hypotheses | Name the graph and null; report graph-robust hits; expect cross-method intersection to be small |
| Radius/length-scale statistic gives nonsense | Coordinates in pixels/array units, parameter in microns; Visium array coords are not microns | Convert to microns via scale factors before any distance parameter (see spatial-neighbors) |
| Rare cell type shows a huge enrichment z-score | Few edges -> high-variance estimate -> large |z| by chance | Report cell-type abundances; discount enrichment involving rare types |

## Related Skills

- spatial-neighbors - builds the graph W that every statistic here inherits; the choice propagates
- spatial-domains - region-level structure; a domain is not a colocalization result
- spatial-communication - ligand-receptor in space; the spillover/abundance confounds recur there
- single-cell/markers-annotation - cell-type labels feeding colocalization, and the marker overlap that confounds SVG

## References

- Svensson V, Teichmann SA, Stegle O (2018) SpatialDE: identification of spatially variable genes. Nature Methods 15(5):343-346. DOI 10.1038/nmeth.4636
- Sun S, Zhu J, Zhou X (2020) Statistical analysis of spatial expression patterns for spatially resolved transcriptomic studies (SPARK). Nature Methods 17(2):193-200. DOI 10.1038/s41592-019-0701-7
- Zhu J, Sun S, Zhou X (2021) SPARK-X: non-parametric modeling enables scalable and robust detection of spatial expression patterns for large spatial transcriptomic studies. Genome Biology 22:184. DOI 10.1186/s13059-021-02404-0
- Weber LM, Saha A, Datta A, Hansen KD, Hicks SC (2023) nnSVG for the scalable identification of spatially variable genes using nearest-neighbor Gaussian processes. Nature Communications 14:4059. DOI 10.1038/s41467-023-39748-z
- Palla G, Spitzer H, Klein M, et al. (2022) Squidpy: a scalable framework for spatial omics analysis. Nature Methods 19(2):171-178. DOI 10.1038/s41592-021-01358-2
- Schurch CM, Bhate SS, Barlow GL, et al. (2020) Coordinated cellular neighborhoods orchestrate antitumoral immunity at the colorectal cancer invasive front. Cell 182(5):1341-1359. DOI 10.1016/j.cell.2020.07.005
- Dos Santos Peixoto R, Miller BF, Brusko MA, et al. (2025) Characterizing cell-type spatial relationships across length scales in spatially resolved omics data (CRAWDAD). Nature Communications 16:350. DOI 10.1038/s41467-024-55700-1
- Moran PAP (1950) Notes on continuous stochastic phenomena. Biometrika 37(1/2):17-23. DOI 10.2307/2332142
- Geary RC (1954) The contiguity ratio and statistical mapping. The Incorporated Statistician 5(3):115-145. DOI 10.2307/2986645
- Getis A, Ord JK (1992) The analysis of spatial association by use of distance statistics. Geographical Analysis 24(3):189-206. DOI 10.1111/j.1538-4632.1992.tb00261.x
- Anselin L (1995) Local indicators of spatial association -- LISA. Geographical Analysis 27(2):93-115. DOI 10.1111/j.1538-4632.1995.tb00338.x
<!-- END FILE: spatial-transcriptomics/spatial-statistics/SKILL.md -->

## 子目录：spatial-transcriptomics/spatial-visualization

<!-- BEGIN FILE: spatial-transcriptomics/spatial-visualization/SKILL.md -->
---
name: bio-spatial-transcriptomics-spatial-visualization
description: Plots spatial transcriptomics expression, clusters, and annotations on tissue using Squidpy and Scanpy. Use when choosing the plotter and spot size by platform fork (sc.pl.spatial / sq.pl.spatial_scatter with real scalefactors and capture diameter for spot/capture data like Visium and Slide-seq, versus molecule/segmentation overlays for imaging/FOV data like Xenium, MERFISH, and CosMx); getting the histology coordinate-frame transform right (micron<->pixel, scalefactors) so points land on the image; and avoiding the honest-visualization traps where interpolation/KDE manufactures spatial pattern not in the data, oversized markers fake tissue coverage, jet and other non-uniform colormaps distort structure, and non-metric UMAP/tSNE distances are misread as spatial conclusions.
tool_type: python
primary_tool: squidpy
---

## Version Compatibility

Reference examples tested with: squidpy 1.4+, scanpy 1.10+, anndata 0.10+, matplotlib 3.8+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Spatial Visualization

**"Plot expression / clusters / a score on my tissue section"** -> Render per-feature values at their real spatial coordinates, optionally over the histology image, without inventing structure the assay did not measure.
- Spot/capture fork (Visium, Visium HD, Slide-seq): `scanpy.pl.spatial` or `squidpy.pl.spatial_scatter` WITH the dataset's `scalefactors` and a `spot_size`/`size` set to the real capture diameter.
- Imaging/FOV fork (Xenium, MERFISH/MERSCOPE, CosMx): `squidpy.pl.spatial_scatter` with `shape=None` for the cell/molecule point cloud, or polygon shapes for segmentation overlays, or a platform viewer (Xenium Explorer, napari, Vitessce, TissUUmaps).

## Governing Principle

Plotting differs by the platform-class fork, and rendering choices can manufacture pattern that is not in the data.

The first decision is which side of the fork the data sits on, because it selects the plotter and the meaning of marker size. Spot/capture data carries a histology image and a `scalefactors` block that maps array coordinates to image pixels; the plotted spot stands for a real capture spot (a 55 um Visium spot is a 1-10-cell mixture, not a cell) and the marker size should reflect that capture diameter. Imaging/FOV data is a point cloud of segmented cells or individual transcript molecules with no Visium-style hex lattice; forcing it through a spot plotter or oversizing markers paints continuous tissue coverage over what is actually sparse, discrete detections. Using the wrong plotter or an arbitrary spot size silently misrepresents the tissue.

The deeper trap is that several common rendering choices invent structure. Smoothing, kernel-density, kriging, or contouring a sparse spatial field produces a continuous surface that looks like high-resolution biology but is interpolated -- the apparent gradients and domains can be artifacts of the kernel, and any spatial statistic (Moran's I, domain calls) computed on the smoothed field is partly circular. Oversized markers are rhetorical: in `scanpy.pl.spatial` `size` is a scaling factor on the spot diameter, so inflating it merges neighbors and fakes contiguity the assay never resolved. A perceptually non-uniform colormap (jet/rainbow) invents banding and edges in a smooth gradient and is unreadable under color-vision deficiency, and silent `vmin`/`vmax` clipping can erase or exaggerate differences. Finally, UMAP/tSNE distances are NOT metric (the same caveat as single-cell/clustering) -- gaps and cluster spacing in an embedding carry no spatial meaning and must not be read as tissue conclusions. Honest spatial visualization shows the raw points, names the transform and any clipping, and never lets a plotting parameter assert biology the measurement did not contain.

## Plot genre by platform fork

| Plot genre | Spot/capture fork (Visium, Slide-seq) | Imaging/FOV fork (Xenium, MERFISH, CosMx) | Honesty pitfall to avoid |
|------------|----------------------------------------|--------------------------------------------|--------------------------|
| Expression / cluster on tissue | `sc.pl.spatial` (uses `scalefactors`) or `sq.pl.spatial_scatter` | `sq.pl.spatial_scatter(shape=None)` point cloud | Oversized `spot_size`/`size` faking coverage |
| Histology overlay | `sc.pl.spatial(img_key='hires')`; scalefactor maps coords->pixels | `sq.pl.spatial_scatter(img=True, img_res_key=...)` with the registered image | Wrong coordinate frame (micron vs pixel) -> points off image |
| Single-molecule / transcript map | not applicable (no molecule table) | scatter the transcript x,y table, or Xenium Explorer / napari | Treating segmented matrix as raw molecules |
| Segmentation / boundary overlay | not applicable | `sq.pl.spatial_scatter` polygon shapes, or napari/TissUUmaps | Hiding segmentation error behind tidy cell polygons |
| Continuous field / heatmap | per-spot color, NO interpolation | per-cell color, NO interpolation | KDE/kriging/contour manufacturing gradients |
| Embedding (UMAP/tSNE) | `sc.pl.umap` for QC only | `sc.pl.umap` for QC only | Reading non-metric embedding distance as spatial |

When competing rendering options exist (point cloud vs polygon overlay, sequential vs diverging colormap), verify the current platform viewer and Squidpy plotting docs before committing -- spatial tooling and platform exports change quickly.

## Spot/Capture Plot with Real Scalefactors and Spot Size

**Goal:** Show expression or cluster labels at true spot positions on a spot/capture section with a marker size that reflects the capture geometry, not a guess.

**Approach:** Let `sc.pl.spatial` read the `uns['spatial']` `scalefactors` so spot coordinates align to the histology image; size markers from the recorded spot diameter rather than an arbitrary constant.

```python
import scanpy as sc
import squidpy as sq

# scalefactors live in adata.uns['spatial'][library_id]; sc.pl.spatial reads them automatically.
sc.pl.spatial(adata, color=['leiden', 'total_counts'], img_key='hires', alpha_img=0.6, ncols=2)

# A spot is a 1-10-cell MIXTURE, not a cell -- do not relabel spot clusters as cell types.
# squidpy resolves the scalefactor from library_id; size here is relative to the spot diameter.
sq.pl.spatial_scatter(adata, color='leiden', library_id='V1_Human_Lymph_Node', size=1.0)
```

## Imaging/FOV Overlay (Point Cloud and Segmentation)

**Goal:** Render imaging-platform cells or molecules in their real micron coordinates without imposing a spot lattice they do not have.

**Approach:** Use `sq.pl.spatial_scatter` with `shape=None` for the segmented-cell point cloud (or polygon shapes when boundaries are stored), and overlay the registered image only when its transform is known.

```python
# Imaging data is a point cloud, not a hex grid: shape=None plots cells as points in micron space.
# With no image, `size` is the ACTUAL dot size, not a scaling factor -- keep it small so sparse
# detections do not visually merge into fake continuous tissue.
sq.pl.spatial_scatter(adata, color='cell_type', shape=None, size=8, img=False)

# Overlay the registered morphology image only when the coordinate frame is trusted.
sq.pl.spatial_scatter(adata, color='EPCAM', shape=None, size=8, img=True, img_alpha=0.5)
```

## Histology Coordinate-Frame Overlay

**Goal:** Place transcripts/spots on the H&E or DAPI image so each point lands on the histological structure it came from.

**Approach:** Map array/micron coordinates into image-pixel space with the correct scalefactor (or platform affine); never plot raw micron coordinates onto a pixel image. Inspect the alignment before trusting any structure read off the overlay.

```python
# Spot/capture: hires-image pixel coords = spatial coords * tissue_hires_scalef.
library_id = list(adata.uns['spatial'].keys())[0]
scalef = adata.uns['spatial'][library_id]['scalefactors']['tissue_hires_scalef']
img = adata.uns['spatial'][library_id]['images']['hires']

import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(8, 8))
ax.imshow(img)                                   # image is in pixel space
coords_px = adata.obsm['spatial'] * scalef       # transform microns/array units -> pixels
ax.scatter(coords_px[:, 0], coords_px[:, 1], s=6, c='red')
ax.set_axis_off()                                # a small misalignment puts expression in the wrong structure
```

## Honest Continuous Field (Colormap and No Interpolation)

**Goal:** Show a continuous score across the section truthfully -- visible raw points, a perceptually uniform colormap, and disclosed clipping.

**Approach:** Color each measured spot/cell directly (never interpolate between them), pick a perceptually uniform map, and state any `vmin`/`vmax` clip rather than letting it silently reshape the gradient.

```python
# Color the MEASURED points only. Do NOT KDE/kriging/contour a sparse field -- that manufactures
# gradients and any Moran's I / domain call computed on the smoothed surface is partly circular.
sc.pl.spatial(adata, color='CD3D', cmap='viridis', vmin=0, vmax='p99')   # 'p99' clip is disclosed, not hidden

# Avoid jet/rainbow: perceptually non-uniform maps invent banding and fail color-vision-deficiency
# readers. Scientific colour maps (Crameri) are perceptually uniform; install cmcrameri to use them.
# import cmcrameri.cm as cmc; sc.pl.spatial(adata, color='CD3D', cmap=cmc.batlow)
```

## Interactive Exploration

Large imaging sections and multi-resolution images are better explored interactively than in static panels. napari (image + points + shapes layers), Vitessce (web, multimodal), TissUUmaps (large image-plus-marker viewing), and the vendor Xenium Explorer / Xenium Panel viewer all pan-and-zoom over the full-resolution data. The same coordinate-frame discipline applies: points must be transformed into the viewer's pixel space (for spot/capture, multiply spatial coordinates by the relevant `tissue_*_scalef`).

```python
import napari
library_id = list(adata.uns['spatial'].keys())[0]
img = adata.uns['spatial'][library_id]['images']['hires']
scalef = adata.uns['spatial'][library_id]['scalefactors']['tissue_hires_scalef']
viewer = napari.Viewer()
viewer.add_image(img, name='tissue')
viewer.add_points(adata.obsm['spatial'] * scalef, size=10, name='spots')   # transform into pixel space
napari.run()
```

## Embedding Caveat

`sc.pl.umap`/`sc.pl.tsne` are legitimate for QC and cluster sanity-checks, but UMAP/tSNE distances are not metric: the size of gaps between clusters and the apparent spacing of points carry no quantitative meaning, and nothing spatial can be concluded from them. Read tissue structure off the spatial plot, never off the embedding (see single-cell/clustering for the full caveat).

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| Spots overlap into a solid sheet; sparse signal looks continuous | `spot_size`/`size` set far above the real capture diameter | Size markers from the spot diameter; for imaging keep `size` small (it is the actual dot size when no image) |
| Points land off the image or in the wrong tissue region | Plotting micron/array coordinates onto a pixel image without the scalefactor/affine | Transform coords -> pixels (`* tissue_hires_scalef`, or the platform affine) before overlay |
| Smooth gradients/domains that vanish on the raw points | Field was KDE/kriged/contoured/imputed; pattern is the kernel, not the tissue | Plot measured points only; show raw alongside any smoothed view and disclose the kernel |
| Banding/edges appear in a smooth field; figure unreadable in grayscale | jet/rainbow or other perceptually non-uniform colormap | Use a perceptually uniform map (viridis, or Crameri scientific colour maps via cmcrameri) |
| Two conditions look very different for the same expression | Inconsistent or silent `vmin`/`vmax` between panels | Fix and disclose the color scale across panels (shared `vmin`/`vmax`) |
| Imaging cells plotted on a hex/grid lattice or with empty image background | Spot plotter (`sc.pl.spatial`) or default `shape` used on imaging point-cloud data | Use `sq.pl.spatial_scatter(shape=None)`; pass the registered image only with a known transform |
| Conclusions drawn from gaps between UMAP clusters | Treating non-metric embedding distance as spatial/quantitative | Restrict spatial claims to the spatial plot; use UMAP for QC only |
| Spot clusters labeled as cell types | A capture spot is a 1-10-cell mixture, not a cell | Label spot clusters as regions/niches; deconvolve for composition (spatial-deconvolution) |
| Per-spot proportion/scatterpie map read as measured composition | Deconvolution output is a model estimate carrying reference and fit uncertainty | Present proportion maps as estimates; rare-type fractions are least reliable, so corroborate before reading them off the map (spatial-deconvolution) |

## Related Skills

- spatial-data-io - load the platform data and the histology image plus scalefactors that plotting depends on
- spatial-domains - produce the region labels rendered on the section
- spatial-statistics - compute Moran's I / neighborhood enrichment whose results are plotted here
- data-visualization/heatmaps-clustering - general perceptually-uniform colormap and figure conventions
- single-cell/clustering - the non-metric UMAP/tSNE distance caveat that applies to embeddings

## References

- Palla G, Spitzer H, Klein M, et al. (2022) Squidpy: a scalable framework for spatial omics analysis. Nature Methods 19(2):171-178. DOI 10.1038/s41592-021-01358-2
- Wolf FA, Angerer P, Theis FJ (2018) SCANPY: large-scale single-cell gene expression data analysis. Genome Biology 19:15. DOI 10.1186/s13059-017-1382-0
- Marconato L, Palla G, Yamauchi KA, et al. (2025) SpatialData: an open and universal data framework for spatial omics. Nature Methods 22(1):58-62. DOI 10.1038/s41592-024-02212-x
- Crameri F, Shephard GE, Heron PJ (2020) The misuse of colour in science communication. Nature Communications 11:5444. DOI 10.1038/s41467-020-19160-7
- Chari T, Pachter L (2023) The specious art of single-cell genomics. PLoS Computational Biology 19(8):e1011288. DOI 10.1371/journal.pcbi.1011288
<!-- END FILE: spatial-transcriptomics/spatial-visualization/SKILL.md -->

<!-- END CATEGORY: spatial-transcriptomics -->

