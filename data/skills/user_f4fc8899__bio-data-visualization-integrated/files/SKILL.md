---
slug: bio-data-visualization-integrated
version: 1.0.1
displayName: "数据可视化 / Scientific data visualization"
name: bio-data-visualization-integrated
summary: "中文：数据可视化综合技能，整合 20 个相关专题，覆盖科学数据可视化：ggplot2/matplotlib出版级图表、热图、曼哈顿图、森林图、UMAP/t-SNE。 English: Integrated Scientific data visualization skill covering 20 related topics, including Scientific data visualization: ggplot2/matplotlib publication figures, heatmaps, Manhattan plots, forest plots, UMAP/t-SNE."
description: "中文：这是一个面向数据可视化的综合生物信息学 Skill，整合当前分类下 20 个相关专题能力。它用于根据研究问题、数据类型和分析阶段，选择合适的方法与工具，规划从输入检查、预处理、核心分析到质量控制、统计解释和结果报告的完整流程。重点覆盖：科学数据可视化：ggplot2/matplotlib出版级图表、热图、曼哈顿图、森林图、UMAP/t-SNE。当用户提供相关实验数据、测序结果、表格或研究问题时，它会帮助判断分析目标与前置条件，给出工具选择、关键参数、输入输出、常见失败原因、结果解读和可复现建议。主要工具包括：ComplexHeatmap, ComplexUpset, NetworkX。该 Skill 提供分析设计与实施指导，不替代对具体数据质量、生物学背景和最终结论的人工审查。 English: This is an integrated bioinformatics Skill for Scientific data visualization, combining 20 related topic areas. It helps users choose appropriate methods and tools based on the research question, data type, and analysis stage, and plan an end-to-end workflow from input validation and preprocessing through core analysis, quality control, statistical interpretation, and reporting. It covers Scientific data visualization: ggplot2/matplotlib publication figures, heatmaps, Manhattan plots, forest plots, UMAP/t-SNE. For relevant experimental data, sequencing results, tables, or research questions, it clarifies prerequisites, recommends tools and parameters, describes expected inputs and outputs, explains common failure modes, and supports reproducible analysis. Primary tools include: ComplexHeatmap, ComplexUpset, NetworkX. It provides methodological and implementation guidance; final data-quality assessment and biological conclusions still require human review."
---

# data-visualization 分类 Skill 整合版

> 本文件整合同一主分类目录下 20 个子目录中的 SKILL.md 内容。
> 各子目录正文按原文保留，并通过标题和边界标记进行区分；源文件中的元数据块未被改写。

---

<!-- BEGIN CATEGORY: data-visualization -->

## 子目录：data-visualization/circos-plots

<!-- BEGIN FILE: data-visualization/circos-plots/SKILL.md -->
---
name: bio-data-visualization-circos-plots
description: Build circular genome visualizations using circlize (R), pyCirclize (Python), or Circos (Perl CLI) with ideogram tracks, multi-data tracks (scatter, histogram, heatmap), chord/link arcs for interactions, and explicit circos.clear() between plots. Covers when circular is appropriate vs when Cartesian wins (Cleveland-McGill 1984), karyograms, and chromosome adjacency in chord diagrams. Use when adjacency on the circle conveys meaning — chromosome-level overview, structural variants, Hi-C interactions, cross-genome comparisons.
tool_type: mixed
primary_tool: circlize
---

## Version Compatibility

Reference examples tested with: circlize 0.4.16+ (R), pyCirclize 1.4+ (Python), Circos 0.69-9 (Perl CLI), ComplexHeatmap 2.18+ (uses circlize for color mapping).

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('<pkg>')` then `?function_name`
- Python: `pip show <package>` then `help(module.function)`

If code throws ImportError, AttributeError, or TypeError, introspect the installed package and adapt the example to match the actual API rather than retrying.

# Circular Genome Plots (Circos)

**"Make a circos plot"** -> Render genome chromosomes around a circle with stacked tracks (histogram, scatter, heatmap) and arcs/chords showing interactions. Krzywinski 2009 *Genome Res* 19:1639 introduced the genre for genome-scale comparative views. The single decision that matters: **does the circular layout convey meaning that Cartesian cannot?**

- R: `circlize::circos.initializeWithIdeogram` + `circos.genomicTrack*` (Gu 2014)
- Python: `pyCirclize.Gcircle`
- CLI: Circos (Perl); config-driven; most flexible but steepest learning

## The Single Most Important Modern Insight -- Circular Plots Often Hide What Cartesian Reveals

Cleveland-McGill 1984 *J Am Stat Assoc* 79:531 effectiveness rankings establish that **position-on-common-scale (Cartesian) is the most accurate visual channel**; circular position requires mental "unwrapping" and impairs precise value comparison. Heer-Bostock 2010 *CHI* replicated the ranking in modern crowd studies. Use circular only when adjacency on the circle conveys meaning that linear cannot.

Use circular ONLY when:
- **Chromosome adjacency matters** (whole-genome SVs, Hi-C contacts where genome circularity is the geometry)
- **Pairwise interactions between many entities** (chord diagrams; chromosome translocations)
- **Aesthetic / overview** infographic for cover figure

Do NOT use circular for:
- Comparing values across categories (Cartesian bar/dot wins)
- Time series (linear axis wins)
- Anything where precise value reading matters

The circos plot is a beautiful but dangerous default. The most-cited published critique is the genre being applied where it adds no information.

## circlize (R) — Modern Default

**Goal:** Render a multi-track circos plot with ideograms, gene-density histogram, variant-density heatmap, and inter-chromosomal SV links.

**Approach:** Initialize with chromosome ideograms via `circos.initializeWithIdeogram`; add tracks with `circos.genomicTrack` + appropriate panel function; add links with `circos.link`; **always call `circos.clear()` after the plot completes.**

```r
library(circlize)

# 1. Initialize with hg38 ideograms
pdf('circos.pdf', width = 8, height = 8)
circos.par(start.degree = 90,             # 12 o'clock start
           gap.degree = c(rep(1, 23), 5)) # bigger gap before chr1 for visual break
# hg38 specifically benefits from explicit chromosome.index to skip unmapped contigs
circos.initializeWithIdeogram(species = 'hg38',
                               chromosome.index = paste0('chr', c(1:22, 'X', 'Y')),
                               plotType = c('axis', 'labels', 'ideogram'))

# 2. Gene-density histogram (outermost data track)
circos.genomicDensity(gene_bed, col = '#0072B2', track.height = 0.08)

# 3. Variant-density heatmap
circos.genomicHeatmap(variant_bed,
                       col = colorRamp2(c(0, 100), c('white', '#D55E00')),
                       heatmap_height = 0.08, side = 'inside')

# 4. CNV scatter
circos.genomicTrack(cnv_bed, ylim = c(-2, 2),
                     panel.fun = function(region, value, ...) {
                         circos.genomicPoints(region, value,
                                              col = ifelse(value > 0.3, '#D55E00',
                                                           ifelse(value < -0.3, '#0072B2', 'grey60')),
                                              pch = 16, cex = 0.4)
                     },
                     track.height = 0.1)

# 5. Inter-chromosomal SV links
for (i in seq_len(nrow(sv_df))) {
    circos.link(sv_df$chr1[i], c(sv_df$start1[i], sv_df$end1[i]),
                sv_df$chr2[i], c(sv_df$start2[i], sv_df$end2[i]),
                col = '#888888', lwd = 0.4)
}

# 6. CRITICAL -- clear global state
circos.clear()
dev.off()
```

## The `circos.clear()` Trap

`circos.par()` settings (start.degree, gap.degree, canvas.xlim, canvas.ylim, clock.wise, circle.margin) are GLOBAL state. After a plot completes, those settings persist into the next plot.

Forgetting `circos.clear()` produces:
- Next `circos.par()` calls silently fail to take effect (warning, easily missed in loops)
- Re-initialization may error or render at wrong angles
- Loop-rendered figures inherit state from the previous iteration

**Always call `circos.clear()` after every plot.** Make it the last line of the plotting block alongside `dev.off()`.

## pyCirclize (Python)

```python
from pycirclize import Circos
import matplotlib.pyplot as plt

sectors = {'chr1': 248956422, 'chr2': 242193529, ...}
circos = Circos(sectors, space=2)                       # space = degree gap between sectors

for sector in circos.sectors:
    sector.text(sector.name, r=110, size=8)
    # outer ideogram
    sector.axis(r_lim=(95, 100), fc='lightgrey')
    # data track
    track = sector.add_track((75, 90))
    track.bar(positions, heights, width=bin_size, color='#0072B2')

# Inter-sector links (chord diagram)
circos.link(('chr1', 1e8, 1.1e8), ('chr5', 2e8, 2.1e8),
            color='#888888', alpha=0.5)

fig = circos.plotfig()
fig.savefig('circos_py.pdf', bbox_inches='tight')
```

pyCirclize is a younger package than circlize but actively developed (Shimoyama 2024+). API more Pythonic than circlize-via-rpy2.

## Circos CLI (Perl) — Most Powerful, Steepest Curve

```bash
# config: circos.conf with karyotype, ideogram, plots, links sections
circos -conf circos.conf -outputfile output.png
```

Circos (Krzywinski 2009) is the original; supports unlimited tracks and arbitrary geometries via configuration. For publication-grade complex figures the Perl tool remains the most powerful. For Python/R workflows, circlize/pyCirclize are more accessible.

## Decision Tree by Use Case

| Use case | Recommended | Why |
|----------|-------------|-----|
| Whole-genome CNV summary | circlize/pyCirclize | Standard genre |
| SV link diagram | Chord arcs in circos | Inter-chromosomal adjacency |
| Hi-C contact summary at chromosome level | circos heatmap track | Adjacency matters |
| Per-sample mutation overview | Circular karyogram | Aesthetic; comparable to OncoPrint |
| Cohort-wide gene expression comparison | NOT circular | Use heatmap (Cartesian wins) |
| Time-series of any kind | NOT circular | Use line plot |
| Pathway diagram | NOT circular | Use Cytoscape |

## Ideogram + Karyogram Without Circos

For per-chromosome data display where circularity is not required, `karyoploteR` (Gel 2017 *Bioinformatics* 33:3088) renders linear ideograms with stacked data tracks — often the better choice for CNV per-chromosome views.

```r
library(karyoploteR)
kp <- plotKaryotype(genome = 'hg38', chromosomes = c('chr1', 'chr7', 'chr17'))
kpAddBaseNumbers(kp)
kpLines(kp, data = cnv_gr, y = cnv_gr$log2)
kpAddCytobandLabels(kp)
```

See `copy-number/cnv-visualization` for karyoploteR in depth.

## Per-Method Failure Modes

### circos.clear() forgotten in a loop

**Trigger:** Plotting multiple circos figures in a `for` loop without `circos.clear()` between.

**Mechanism:** circos.par settings (gap.degree, start.degree, clock.wise) persist across plots.

**Symptom:** Plots 2..N inherit state from plot 1; gap sizes, rotation differ unexpectedly.

**Fix:** End every plot block with `circos.clear()`. Make it a hygiene rule.

### Using circular when Cartesian would be better

**Trigger:** "Circos plot of gene expression across 20 conditions."

**Mechanism:** Circular impairs value comparison (Cleveland-McGill 1984; Heer-Bostock 2010).

**Symptom:** Reviewer or coauthor says "I can't tell which condition is highest."

**Fix:** Use clustered heatmap. Reserve circos for genome-adjacency or chord-diagram use cases.

### Too many links produce a black blob

**Trigger:** Plotting 10000+ chord links between chromosomes.

**Mechanism:** Overlap saturates the center; no individual link visible.

**Symptom:** Center of circos is uniformly dark.

**Fix:** Filter to top-confidence links; OR color-bin by interaction strength with alpha; OR aggregate to chromosome-level summary then link.

### Sector ordering arbitrary

**Trigger:** Default sector order is input order.

**Mechanism:** circlize / pyCirclize do not auto-order chromosomes 1..22, X, Y.

**Symptom:** Chromosomes appear in genome-build-file order.

**Fix:** Explicit `chromosome.index = c(paste0('chr', 1:22), 'chrX', 'chrY')`.

### Wrong species ideogram

**Trigger:** `species = 'hg19'` when data is hg38-coordinate.

**Mechanism:** circlize fetches cytoband data per species; mismatch renders correct ideogram but wrong banding for the data.

**Symptom:** Cytoband boundaries don't match published references.

**Fix:** Match `species` to data coordinate system. For non-standard genomes, supply custom cytoband file. For `species = 'hg38'` specifically, always pass `chromosome.index = paste0('chr', c(1:22, 'X', 'Y'))` to skip unmapped contigs (jokergoo/circlize issue #46).

### Ideogram covers data track

**Trigger:** Default ideogram track height too large; data track squeezed.

**Mechanism:** circos.initializeWithIdeogram uses ~5% of radius; left-over for data.

**Symptom:** Data values invisible because track is too narrow.

**Fix:** Reduce `cytoband.height` in initialization; OR use `plotType = c('axis', 'labels')` to omit ideogram entirely.

### Chromosome label collisions for small chromosomes

**Trigger:** Default label position; small chromosomes (chr21, chr22, chrY) have overlapping labels.

**Mechanism:** Labels drawn at sector midpoints regardless of sector width.

**Symptom:** Labels overlap.

**Fix:** `circos.par(gap.degree = c(rep(1, 22), 10, 10, 10))` for larger gaps before small chromosomes; OR reduce label font size.

## Reconciliation

| Pattern | Cause | Action |
|---------|-------|--------|
| circlize and pyCirclize differ in default rotation | Different start-angle convention | Set `start.degree=90` (R) / equivalent (Python) explicitly |
| Cytoband colors don't match UCSC | Different species cytoband source | Verify species; for custom genomes supply band file |
| Inter-sector links arc the "long way around" | Default arc direction | Some chord packages support `direction = 'short'` |

## Quantitative Thresholds

| Threshold | Value | Source |
|-----------|-------|--------|
| Max sectors readable | ~30 | Visualization practical |
| Max links before blob | ~5000 | Practical; depends on alpha |
| Cytoband.height default | 0.05 of radius | circlize default |
| When circular adds value | Adjacency-meaningful only | Cleveland-McGill 1984 |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| Subsequent plots use wrong rotation | `circos.clear()` forgotten | Always end with `circos.clear()` |
| Chromosomes out of order | Default = input order | Explicit chromosome.index |
| Cytoband mismatch | Wrong species | Match species to data coords |
| Center of circos black | Too many links | Filter or aggregate |
| Reviewer asks "why circular?" | Cartesian would have been clearer | Migrate to heatmap unless adjacency matters |
| Small-chromosome label overlap | Default label position | Larger gap.degree before small sectors |

## References

- Cleveland WS, McGill R. 1984. Graphical perception: theory, experimentation, and application to the development of graphical methods. *J Am Stat Assoc* 79(387):531-554.
- Gel B, Serra E. 2017. karyoploteR: an R/Bioconductor package to plot customizable genomes. *Bioinformatics* 33(19):3088-3090.
- Gu Z, Gu L, Eils R, Schlesner M, Brors B. 2014. circlize implements and enhances circular visualization in R. *Bioinformatics* 30(19):2811-2812.
- Heer J, Bostock M. 2010. Crowdsourcing graphical perception: using Mechanical Turk to assess visualization design. *Proc CHI* 203-212.
- Krzywinski M, Schein J, Birol I, et al. 2009. Circos: an information aesthetic for comparative genomics. *Genome Res* 19(9):1639-1645.
- Shimoyama Y. 2024. pyCirclize: Circular visualization in Python. *GitHub* https://github.com/moshi4/pyCirclize

## Related Skills

- copy-number/cnv-visualization - karyoploteR linear alternative for CNV
- variant-calling/structural-variant-calling - SV data for circos links
- hi-c-analysis/hic-visualization - Hi-C contact data circular display
- data-visualization/genome-tracks - Linear track alternative
- data-visualization/color-palettes - Sector and link palettes
<!-- END FILE: data-visualization/circos-plots/SKILL.md -->

## 子目录：data-visualization/color-palettes

<!-- BEGIN FILE: data-visualization/color-palettes/SKILL.md -->
---
name: bio-data-visualization-color-palettes
description: Select colormaps and qualitative palettes for scientific figures using perceptual-uniformity, color-vision-deficiency safety, and luminance-monotonicity criteria. Covers Crameri scientific colormaps, viridis/cividis/magma, Okabe-Ito categorical, ColorBrewer, and the rainbow/jet critique. Use when choosing palettes for heatmaps, scatter, networks, or any encoding where color carries quantitative or categorical meaning.
tool_type: mixed
primary_tool: viridis
goal_approach_exempt: true
---

## Version Compatibility

Reference examples tested with: viridis 0.6+, RColorBrewer 1.1+, scico 1.5+ (Crameri colormaps in R), khroma 1.12+ (Tol/Crameri palettes in R), matplotlib 3.8+, colorcet 3.0+, ggsci 3.0+, colorspace 2.1+.

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters

If code throws ImportError, AttributeError, or TypeError, introspect the installed package and adapt the example to match the actual API rather than retrying.

# Color Palettes for Scientific Visualization

**"Pick a color palette"** -> Choose a colormap that (a) is perceptually uniform along the relevant data axis, (b) remains interpretable under common color-vision deficiencies, (c) prints correctly to grayscale, and (d) matches the data type — sequential, diverging, cyclic, or qualitative.

- R: `viridis::viridis`, `scico::scale_color_scico`, `khroma::color`, `RColorBrewer::brewer.pal`
- Python: `matplotlib.colormaps`, `colorcet`, `seaborn.color_palette`, `cmcrameri.cm`

## The Three Modern Standards

1. **Perceptual uniformity** -- equal data steps produce equal perceived color steps. viridis (van der Walt 2015), cividis (Nuñez 2018), and the Crameri family (batlow, roma, vik) are designed for this. Jet, rainbow, and red->green are not.

2. **Color vision deficiency safety** -- ~6% of males have deuteranopia / protanopia (red-green deficiency). cividis was explicitly designed to be near-identical under normal and CVD viewing (Nuñez 2018 *PLOS ONE* 13:e0199239). The Okabe-Ito 8-color qualitative palette (popularized in Wong 2011 *Nat Methods* 8:441) is the CVD-safe categorical default.

3. **Grayscale monotonicity** -- a perceptually-uniform sequential colormap has monotonically increasing luminance. Convert the figure to grayscale; if the order is still readable, the colormap is luminance-monotonic. This is the single most actionable test.

## Palette Type by Data Type

| Data type | Use | Avoid |
|-----------|-----|-------|
| Sequential (expression, coverage, density) | viridis, magma, cividis, batlow, lipari | jet, rainbow, hsv |
| Diverging (log fold change, z-score, signed correlation) | vik, roma, RdBu, BrBG, PiYG | jet, rainbow |
| Cyclic (phase, time-of-day, angle) | romaO, vikO, twilight | linear sequential (wrap creates artifactual jump) |
| Categorical (≤8 groups) | Okabe-Ito (Wong 2011), Tol bright, Dark2 | rainbow with N=20, Set1 if CVD matters |
| Categorical (9-20 groups) | tab20, Paired, Polychrome | too-many categorical hues -- consider faceting |
| Categorical (>20) | None -- reconsider design | More colors will not help |

## The Crameri Scientific Colormaps

Crameri 2020 *Nat Commun* 11:5444 documented the prevalence of misleading palettes (rainbow, red-green) across published science and released a family of perceptually-uniform CVD-safe colormaps via Zenodo (doi:10.5281/zenodo.8409685). Key entries:

| Crameri name | Type | Use case |
|--------------|------|----------|
| `batlow` | sequential | Default jet replacement; runs through dark-blue -> ochre -> light-yellow |
| `lipari` | sequential | Higher-saturation alternative; better for projection |
| `vik` | diverging | Blue -> white -> red equivalent, perceptually uniform |
| `roma` | diverging | Slightly warmer than vik |
| `bam` | diverging | Brown -> white -> green |
| `romaO` | cyclic | Phase, time-of-day, angle data |
| `vikO` | cyclic | Diverging cyclic |

```r
library(scico)
# Sequential
ggplot(df, aes(x, y, fill = value)) + geom_tile() +
    scale_fill_scico(palette = 'batlow')
# Diverging
ggplot(df, aes(x, y, fill = lfc)) + geom_tile() +
    scale_fill_scico(palette = 'vik', midpoint = 0)
```

```python
from cmcrameri import cm
import matplotlib.pyplot as plt
plt.imshow(data, cmap=cm.batlow)         # sequential
plt.imshow(data, cmap=cm.vik, vmin=-vmax, vmax=vmax)   # diverging, symmetric
```

## viridis Family (matplotlib default since 3.0)

```r
library(viridis)
scale_color_viridis_c(option = 'viridis')   # default: dark blue -> yellow
scale_color_viridis_c(option = 'magma')     # black -> red -> yellow
scale_color_viridis_c(option = 'inferno')   # black -> purple -> yellow
scale_color_viridis_c(option = 'plasma')    # purple -> pink -> yellow
scale_color_viridis_c(option = 'cividis')   # CVD-optimized
scale_color_viridis_c(option = 'turbo')     # jet-like but perceptually uniform
```

```python
plt.imshow(data, cmap='viridis')   # 'magma', 'inferno', 'plasma', 'cividis', 'turbo'
```

**cividis is the only viridis-family colormap optimized for CVD.** Use it for any figure intended to remain interpretable under deuteranopia/protanopia.

## Okabe-Ito Categorical Palette (Wong 2011)

The 8-color CVD-safe categorical palette. Memorize the hexes:

```r
okabe_ito <- c(
    '#E69F00',  # orange
    '#56B4E9',  # sky blue
    '#009E73',  # bluish green
    '#F0E442',  # yellow
    '#0072B2',  # blue
    '#D55E00',  # vermilion
    '#CC79A7',  # reddish purple
    '#000000'   # black
)
scale_color_manual(values = okabe_ito)
```

Available as `palette.colors(8, 'Okabe-Ito')` in R 4.0+, `scale_color_manual(values = palette.colors(8, 'Okabe-Ito'))`. In matplotlib, `colorblind` style or manual hex list.

For DE plots, the canonical assignment is Up = `#D55E00` (vermilion), Down = `#0072B2` (blue), NS = `#999999` (grey).

## ColorBrewer (Harrower & Brewer 2003)

```r
library(RColorBrewer)
display.brewer.all()                    # interactive palette browser
display.brewer.all(colorblindFriendly = TRUE)   # CVD-safe subset only
brewer.pal(n = 8, name = 'Dark2')       # qualitative
brewer.pal(n = 9, name = 'YlOrRd')      # sequential
brewer.pal(n = 11, name = 'RdBu')       # diverging
```

ColorBrewer's CVD-safe sequential and diverging palettes are publication-defaults. For qualitative beyond 8 colors, switch to Tol/Polychrome — ColorBrewer qualitative tops out at 12 (Set3).

## Scientific Journal Brand Palettes

```r
library(ggsci)
scale_color_npg()       # Nature Publishing Group
scale_color_aaas()      # Science (AAAS)
scale_color_lancet()    # Lancet
scale_color_jama()      # JAMA
scale_color_jco()       # JCO
scale_color_nejm()      # NEJM
```

These are CVD-imperfect — use journal palettes for stylistic compliance, not for accessibility. Verify by colorblindness simulation (below).

## CVD Simulation -- The Mandatory Check

```r
library(colorspace)
# Simulate deuteranopia / protanopia on a palette
cvd_emulator(palette, type = 'deutan')
cvd_emulator(palette, type = 'protan')
cvd_emulator(palette, type = 'tritan')

# Visual side-by-side
demoplot(palette, type = 'heatmap')
```

```python
# colorspacious provides CVD simulation
from colorspacious import cspace_converter
# or use a CVD-safe palette by construction (cividis, Okabe-Ito, Crameri)
```

If a palette is unreadable under deutan simulation, do not use it for accessible figures. Period.

## Grayscale Monotonicity Test

```r
library(scales)
show_col(viridis(10))           # full color
show_col(grey(seq(0, 1, length = 10)))   # equivalent grayscale gradient
```

In practice: save the figure as PNG, open in an image editor, desaturate. If the data order is still readable, the colormap is luminance-monotonic. If it shows arbitrary "rings" or "bands," the colormap is non-monotonic — fix before submitting.

Rainbow / jet fails this test catastrophically. viridis and cividis pass.

## Diverging Palette Setup (LFC, z-score)

```r
library(circlize)
col_fun <- colorRamp2(c(-2, 0, 2), c('#0072B2', 'white', '#D55E00'))
# Symmetric around 0; ALWAYS use symmetric bounds for signed data
```

```python
import matplotlib.pyplot as plt
plt.imshow(data, cmap='RdBu_r', vmin=-2, vmax=2)   # symmetric
# do NOT use vmin=data.min(), vmax=data.max() for diverging data
```

The most common diverging-palette error is asymmetric bounds (`vmin=min, vmax=max`) which mis-aligns zero with the white midpoint.

## Custom Palette Construction

```r
# Discrete categorical
my_palette <- c('Control' = '#0072B2', 'Treatment' = '#D55E00', 'Vehicle' = '#009E73')
scale_color_manual(values = my_palette)

# Continuous gradient between custom colors
colorRampPalette(c('#0072B2', 'white', '#D55E00'))(100)
```

```python
from matplotlib.colors import LinearSegmentedColormap
cmap = LinearSegmentedColormap.from_list('cvd_div', ['#0072B2', '#FFFFFF', '#D55E00'])
```

When building a custom diverging palette: pick endpoints with similar luminance (so neither side dominates), pass through pure white at the midpoint (NOT light gray), and verify with the grayscale test.

## Common Failure Modes

### Asymmetric bounds on diverging data

**Trigger:** `vmin=data.min()`, `vmax=data.max()` on signed data with skewed distribution.

**Mechanism:** Zero no longer maps to the midpoint (white) of the diverging palette.

**Symptom:** Half the cells visually look "below zero" but are actually positive; reviewer confusion.

**Fix:** `vmax = max(abs(data.min()), abs(data.max()))`; then `vmin = -vmax`. Or pre-clip data to a fixed range.

### Categorical palette with too many colors

**Trigger:** 15+ groups all on one colormap.

**Mechanism:** Human color discrimination saturates around 8-10 distinct hues.

**Symptom:** Groups look identical; legend has no information value.

**Fix:** Facet by category, or aggregate small groups into "Other," or use a categorical+marker-shape combination.

### Rainbow / jet still in use

**Trigger:** Default colormaps in older matplotlib (<2.0), MATLAB-derived code, or `colorRampPalette(rainbow(...))`.

**Mechanism:** Rainbow has non-monotonic luminance and includes a perceptual "yellow band" that creates artifactual boundaries.

**Symptom:** Figures show banding that doesn't exist in the data; CVD viewers cannot interpret.

**Fix:** Migrate to viridis (sequential) or vik/roma (diverging). For nostalgic jet-like appearance with perceptual properties, use `turbo` (matplotlib 3.3+).

### Light gray midpoint instead of pure white

**Trigger:** `colorRamp2(c(-2, 0, 2), c('blue', '#EEEEEE', 'red'))`.

**Mechanism:** Light gray reads as "weakly significant" rather than zero — the visual "where is zero" anchor is lost.

**Symptom:** Zero values appear muted, drawing the eye away from the actual midpoint.

**Fix:** Use pure white `'#FFFFFF'` or `'white'` at the midpoint.

### Wrong cmap for non-numeric data

**Trigger:** Continuous colormap applied to a categorical variable (e.g., cluster ID as a continuous gradient).

**Mechanism:** Cluster IDs are nominal — ordering is meaningless; gradient implies false ordering.

**Symptom:** Cluster 2 "looks closer to" cluster 1 than cluster 8, but the cluster numbering is arbitrary.

**Fix:** Use a qualitative categorical palette (Okabe-Ito ≤8; tab20 for more).

### CVD-unsafe palette in a CVD-sensitive figure

**Trigger:** Red-green Set1 in a clinical figure intended for broad audience.

**Mechanism:** ~6% of male readers cannot distinguish red from green.

**Symptom:** Reviewer or colleague reports the figure is unreadable.

**Fix:** Pre-flight with `colorspace::cvd_emulator`; switch to Okabe-Ito for categorical, cividis for sequential.

## Quantitative Thresholds

| Threshold | Value | Source |
|-----------|-------|--------|
| Max distinguishable categorical hues | 8-10 | Wong 2011; perceptual research |
| CVD prevalence (males of European descent) | ~6% deutan/protan, ~0.5% tritan | Various; Nuñez 2018 cites figures |
| Diverging midpoint | pure white (#FFFFFF) | Not light gray; preserves zero anchor |
| Crameri batlow / lipari -- general-purpose sequential | – | Crameri 2020 |
| cividis -- CVD-optimal sequential | – | Nuñez 2018 |
| Okabe-Ito -- 8-color qualitative CVD-safe | – | Wong 2011 |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| Diverging plot with zero not at white | Asymmetric bounds | Use symmetric `vmin = -vmax` |
| Rainbow "bands" visible in heatmap | Non-monotonic luminance of rainbow | Replace with viridis or turbo |
| Categorical plot with indistinguishable groups | Too many hues | Facet, aggregate, or shape+color |
| CVD viewer reports unreadable figure | Red-green palette | Switch to Okabe-Ito or cividis |
| Light gray at diverging midpoint | Wrong center color | Use pure white |
| Grayscale conversion shows banding | Non-luminance-monotonic colormap | Use viridis family or Crameri |
| Heatmap with one cell saturating the scale | No quantile clipping | See data-visualization/heatmaps-clustering for robust bounds |

## References

- Crameri F, Shephard GE, Heron PJ. 2020. The misuse of colour in science communication. *Nat Commun* 11:5444. doi:10.1038/s41467-020-19160-7
- Harrower M, Brewer CA. 2003. ColorBrewer.org: an online tool for selecting colour schemes for maps. *Cartogr J* 40(1):27-37.
- Nuñez JR, Anderton CR, Renslow RS. 2018. Optimizing colormaps with consideration for color vision deficiency to enable accurate interpretation of scientific data. *PLOS ONE* 13(7):e0199239.
- Borland D, Taylor RM II. 2007. Rainbow color map (still) considered harmful. *IEEE Comput Graph Appl* 27(2):14-17.
- Light A, Bartlein PJ. 2004. The end of the rainbow? Color schemes for improved data graphics. *Eos Trans AGU* 85(40):385,391.
- Wong B. 2010. Points of view: Color coding. *Nat Methods* 7(8):573.
- Wong B. 2011. Points of view: Color blindness. *Nat Methods* 8(6):441.
- Gehlenborg N, Wong B. 2012. Points of view: Mapping quantitative data to color. *Nat Methods* 9(8):769.

## Related Skills

- data-visualization/heatmaps-clustering - Robust diverging bounds for heatmaps
- data-visualization/volcano-and-ma-plots - Okabe-Ito Up/Down/NS conventions
- data-visualization/ggplot2-fundamentals - Applying palettes in ggplot2 scales
- data-visualization/dimensionality-reduction-plots - Categorical palette for cluster labels
<!-- END FILE: data-visualization/color-palettes/SKILL.md -->

## 子目录：data-visualization/dimensionality-reduction-plots

<!-- BEGIN FILE: data-visualization/dimensionality-reduction-plots/SKILL.md -->
---
name: bio-data-visualization-dimensionality-reduction-plots
description: Produce and interpret PCA, t-SNE, UMAP, and PHATE plots for high-dimensional omics data with rigor about which method preserves what (variance, local structure, manifold, transitions), hyperparameter sensitivity, and the well-documented limits of 2D embeddings. Covers PCA biplot/scree/loadings, t-SNE PCA initialization (Kobak-Berens 2019), UMAP n_neighbors/min_dist trade-offs, and the Chari-Pachter 2023 critique. Use when visualizing high-dimensional data — bulk PCA, single-cell embeddings, multi-omics integration projections.
tool_type: mixed
primary_tool: scanpy
---

## Version Compatibility

Reference examples tested with: scanpy 1.10+, anndata 0.10+, scikit-learn 1.4+, umap-learn 0.5+, openTSNE 1.0+, phate 1.0+, ggplot2 3.5+, PCAtools 2.16+, matplotlib 3.8+.

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters

If code throws ImportError, AttributeError, or TypeError, introspect the installed package and adapt the example to match the actual API rather than retrying.

# Dimensionality-Reduction Plots

**"Make a PCA / UMAP / t-SNE plot"** -> Choose a projection method aligned with what the plot must reveal — variance explained (PCA), local neighborhood structure (t-SNE), manifold approximation with some global structure (UMAP), or continuous transitions (PHATE). Set hyperparameters deliberately. Communicate the projection's limits and refuse to over-interpret 2D distances.

- Python: `sklearn.decomposition.PCA`, `openTSNE`, `umap-learn`, `phate`, `scanpy.tl.umap` / `scanpy.tl.tsne` / `scanpy.tl.pca`
- R: `prcomp`, `PCAtools::pca`, `Seurat::RunPCA` / `RunUMAP` / `RunTSNE`, `phateR`

## The Single Most Important Modern Insight -- 2D Embeddings Distort

Chari & Pachter 2023 *PLOS Comp Biol* 19:e1011288 demonstrated that 2D embeddings of single-cell data lose >95% of the high-dimensional geometry — local neighborhoods are preserved by construction, but distances between distant cells, density estimates, and global topology are NOT preserved. The "specious art" of single-cell genomics is the practice of reading 2D layout as biology.

Practical consequence: a UMAP plot communicates "these cells are similar locally" and nothing more. Distance between clusters is meaningless. Density of points within a cluster is dominated by the embedding's repulsion parameter, not the underlying biology. A trajectory inferred from "the gap" between two clusters in UMAP space is an artifact unless validated against the high-dimensional data (RNA velocity, diffusion pseudotime, PHATE).

A second foundational paper is Kobak & Berens 2019 *Nat Commun* 10:5416 on t-SNE for single-cell: PCA initialization + early-exaggeration + multi-scale similarity kernels recover more global structure than default t-SNE settings. The same logic applies to UMAP via `init='spectral'` (default) and `min_dist`.

## Algorithmic Taxonomy

| Method | Preserves | Hyperparameters | Strength | Fails when |
|--------|-----------|-----------------|----------|------------|
| PCA | Linear variance (orthogonal, ordered) | n_components, scaling | Interpretable via loadings; deterministic; variance % per axis | Non-linear manifolds; high-dim data with few effective dims |
| t-SNE (van der Maaten 2008) | Local neighborhoods (Student-t similarity) | perplexity (typ. 30-50), learning_rate, n_iter, init | Crisp cluster separation | Global distances meaningless; cluster sizes deceptive; non-deterministic |
| UMAP (McInnes 2018, Becht 2018) | Manifold local + partial global | n_neighbors (typ. 15-50), min_dist (typ. 0.1-0.5), spread | Faster than t-SNE; better global preservation than default t-SNE; deterministic given seed | Still distorts; n_neighbors small -> shattered; large -> homogenized |
| PHATE (Moon 2019) | Continuous transitions, branching trajectories | k (knn), t (diffusion power) | Best for developmental trajectories; preserves transition geometry | Slower; less canonical for clustering display |
| Diffusion map | Diffusion distance | epsilon, n_components | Theoretically motivated; supports pseudotime | Less visually striking; less commonly used |
| MDS / classical MDS | Global Euclidean distances | n_components, dissimilarity matrix | Honest about distance preservation | Computationally expensive >5000 points |
| Isomap | Geodesic distance on knn graph | n_neighbors, n_components | Captures non-linear manifold | Sensitive to k; less popular than UMAP |
| Force-directed (PAGA, ForceAtlas2) | Graph topology | Layout-specific | Best for connectivity (PAGA cluster graph) | Not for dense cells; aesthetic |

## Decision Tree by Scenario

| Scenario | Recommended | Why |
|----------|-------------|-----|
| Bulk RNA-seq sample QC | PCA on log-vst counts; show PC1 vs PC2 with metadata color | Variance explained is meaningful for batch detection |
| Single-cell broad cluster overview | UMAP `n_neighbors=30, min_dist=0.3` after PCA(50) | Standard; preserves clusters; faster than t-SNE |
| Single-cell with delicate trajectories | PHATE OR diffusion map | Preserves continuous transitions |
| Cluster cardinality / boundary visualization | t-SNE with PCA init, perplexity=50 (Kobak-Berens) | Crisper cluster separation than UMAP |
| Multi-omics integration projection | MOFA factors + PCA, or UMAP of joint embedding | Per-omics projection often misleading |
| Spatial transcriptomics with histology | UMAP for transcriptional axis; SEPARATE spatial scatter | UMAP collapses physical space |
| Identify which genes drive variation | PCA biplot with loadings as arrows | Loadings are interpretable; UMAP/t-SNE has no loadings |
| Demonstrating batch confound | PCA color by batch -- if PC1/PC2 separates batches, batch is the dominant variance | UMAP can hide batch effect via local neighborhood preservation |
| Visualizing 50 conditions | UMAP/t-SNE for nuance; faceted PCA for interpretability | Method choice depends on question |

## PCA -- The Underused Workhorse

PCA is interpretable, deterministic, and the loadings explain WHY samples cluster — UMAP/t-SNE cannot do this. For bulk RNA-seq sample QC, PCA is the right answer 90% of the time.

**Goal:** Project samples into a low-dim space whose axes are linear combinations of features ordered by variance explained, then visualize PC1 vs PC2 colored by metadata.

**Approach:** Variance-stabilize counts (DESeq2 `vst()` / `rlog()`); run PCA on transposed expression matrix; annotate axes with variance-explained percentages; layer screeplot and loadings plot to support interpretation.

```r
library(DESeq2)
library(PCAtools)
library(ggplot2)
vsd <- vst(dds, blind = FALSE)
p <- pca(assay(vsd), metadata = as.data.frame(colData(dds)))
biplot(p, colby = 'condition', shape = 'batch', lab = NULL,
       hline = 0, vline = 0,
       legendPosition = 'right',
       title = paste0('PCA: PC1 (', round(p$variance[1], 1), '%) vs PC2 (', round(p$variance[2], 1), '%)'))
screeplot(p, components = 1:10)
loadings_plot <- plotloadings(p, components = 1, rangeRetain = 0.05)
```

```python
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt

pca = PCA(n_components=10)
X_pca = pca.fit_transform(X)
var = pca.explained_variance_ratio_

fig, axes = plt.subplots(1, 2, figsize=(10, 4))
axes[0].scatter(X_pca[:, 0], X_pca[:, 1], c=labels, alpha=0.7)
axes[0].set_xlabel(f'PC1 ({var[0]*100:.1f}%)')
axes[0].set_ylabel(f'PC2 ({var[1]*100:.1f}%)')
axes[1].plot(range(1, 11), var, 'o-')
axes[1].set_xlabel('PC')
axes[1].set_ylabel('Variance explained')
```

**Always label axes with variance explained.** A PCA plot without `PC1 (45%)` annotation is unreadable. If PC1 = 5% and PC2 = 4%, apparent "clusters" may be noise.

## t-SNE -- Kobak-Berens Modern Defaults

Default t-SNE (Maaten 2008) loses global structure. Kobak-Berens 2019 demonstrated that three changes recover it:

1. **Initialize with PCA**, not random — `init='pca'` (openTSNE) or pre-compute PCA scores as init
2. **High learning rate** — `learning_rate = n/12` (n = number of points), not the default 200
3. **Early exaggeration** — `exaggeration=12, early_exaggeration_iter=250` for large data

```python
import openTSNE
import numpy as np

# Kobak-Berens defaults
embedding = openTSNE.TSNE(
    perplexity=30,                          # 30-50 typical
    n_iter=750,
    initialization='pca',                   # NOT random
    learning_rate=X.shape[0] / 12,          # scales with n
    n_jobs=-1,
    random_state=42).fit(X)
```

```r
library(Rtsne)
set.seed(42)
ts <- Rtsne(X, perplexity = 30, theta = 0.5, pca_scale = TRUE,
            initial_dims = 50, max_iter = 750)
# Rtsne does not natively support PCA initialization; use external init via Y_init=
```

**Perplexity is the local-vs-global trade-off.** Low (5) -> local; high (100) -> global. 30-50 is standard for >1000 points.

## UMAP -- Modern Defaults and the Random-Seed Trap

```python
import umap
reducer = umap.UMAP(
    n_neighbors=30,        # local-global balance; 15-50 typical
    min_dist=0.3,          # tightness of clusters; 0.1-0.5 typical
    n_components=2,
    metric='euclidean',
    random_state=42)       # reproducibility
embedding = reducer.fit_transform(X)
```

```r
library(uwot)
set.seed(42)
um <- umap(X, n_neighbors = 30, min_dist = 0.3, metric = 'euclidean')
```

```python
# scanpy convention -- after sc.tl.pca, sc.pp.neighbors
sc.pp.neighbors(adata, n_neighbors=30, n_pcs=50)
sc.tl.umap(adata, min_dist=0.3, random_state=42)
sc.pl.umap(adata, color='leiden', palette='tab20', frameon=False,
           legend_loc='on data', legend_fontsize=7,
           save='_clusters.pdf')
```

**`min_dist` controls tightness, NOT separation.** Smaller min_dist = tighter clusters. Does not change which cells cluster together — only how dense the rendering is.

**`n_neighbors` controls local-vs-global.** Small n_neighbors = local fragmentation; large n_neighbors = clusters merge.

**Random seed matters.** UMAP is deterministic given seed; without setting seed, results vary across runs. Always set `random_state` (umap-learn) or `seed=` (uwot).

**scanpy.pl.umap save trap:** `save='_x.pdf'` writes to `sc.settings.figdir` (default `./figures/`) with prefix `umap`, producing `figures/umap_x.pdf` — not the path specified. Default `dpi_save = 150` is below journal requirements.

## PHATE -- For Continuous Trajectories

```python
import phate
phate_op = phate.PHATE(knn=10, decay=40, t='auto', n_jobs=-1, random_state=42)
emb = phate_op.fit_transform(X)
plt.scatter(emb[:, 0], emb[:, 1], c=pseudotime, cmap='viridis', s=5)
```

PHATE preserves transition geometry — for embryonic development, differentiation trajectories, or any continuous-state biology, PHATE is more faithful than UMAP. For discrete cell types, UMAP is fine.

## Per-Method Failure Modes

### Over-interpreting UMAP distances

**Trigger:** Reading "cluster A is closer to cluster B than to C" as biological similarity.

**Mechanism:** UMAP preserves local neighborhoods; global distances are NOT preserved (Chari-Pachter 2023).

**Symptom:** Conclusion contradicts hierarchical clustering / RNA velocity / known biology.

**Fix:** Validate inter-cluster relationships against high-dimensional metrics (correlation, distance in PCA space, RNA velocity).

### t-SNE / UMAP without random seed

**Trigger:** Reproducibility request; figure differs between runs.

**Mechanism:** Both methods use stochastic optimization; default seed varies.

**Symptom:** Re-running the script produces visibly different layouts.

**Fix:** Set `random_state=42` (umap-learn, sklearn) or `seed=42` (R uwot/Rtsne).

### Perplexity too low for the data

**Trigger:** Default t-SNE perplexity (30) on small dataset (<500 points).

**Mechanism:** Perplexity > n/3 fails; cells artificially fragment.

**Symptom:** Plot shows "shattered" small clusters that don't correspond to biology.

**Fix:** For small n: perplexity = max(5, n/30). For very large n: perplexity 50-100.

### PCA without scaling

**Trigger:** `prcomp(X)` or `PCA().fit(X)` without scaling rows/columns first.

**Mechanism:** Genes with high absolute expression dominate variance; PCA captures library-size effect rather than biological variation.

**Symptom:** PC1 perfectly correlates with library size or with total expression.

**Fix:** Use `vst()` / `rlog()` (DESeq2) or log + scale (`prcomp(X, scale.=TRUE)`). For single-cell, normalize then `sc.pp.scale_data`.

### UMAP cluster shapes "interpreted" as biological signal

**Trigger:** Reporting that a cluster is "elongated" or "round" as biological observation.

**Mechanism:** UMAP cluster shape is an artifact of `min_dist` and `n_neighbors`, not biology.

**Symptom:** Reviewer asks "why is the immune cluster elongated?"; no answer except the embedding.

**Fix:** Do not interpret cluster shape. Report cluster membership and validate biology via marker genes.

### scanpy.pl.umap save writes to figures/ subdirectory

**Trigger:** `sc.pl.umap(adata, save='myplot.pdf')` with the expectation that myplot.pdf will land in the current directory.

**Mechanism:** `save=` is concatenated with `sc.settings.figdir` (default `./figures/`) and prefixed with `umap`.

**Symptom:** File not at the requested path; actually at `figures/umapmyplot.pdf`.

**Fix:** Set `sc.settings.figdir='/abs/path/'` AND `save='_descriptive.pdf'` so result is `figures/umap_descriptive.pdf`. For full path control use `matplotlib.savefig` after `sc.pl.umap(show=False)`.

### Default DPI 150 below journal requirements

**Trigger:** scanpy `sc.settings.set_figure_params()` default `dpi_save=150`.

**Mechanism:** Nature/Cell require 300+ DPI for raster.

**Symptom:** Figure looks fine on screen, rejected at submission.

**Fix:** `sc.set_figure_params(dpi_save=300, figsize=(4, 4))`.

### PCA loadings interpreted on UMAP/t-SNE coordinates

**Trigger:** "PC1 axis on UMAP" — projecting loadings onto UMAP.

**Mechanism:** UMAP/t-SNE coordinates have no linear interpretation; loadings are PCA-specific.

**Symptom:** Conclusion about "what UMAP-x means" that has no foundation.

**Fix:** Use PCA when loadings are needed. Show UMAP for visualization and PCA for axis-driving gene identification, separately.

## Reconciliation: When Methods Disagree

| Pattern | Likely cause | Action |
|---------|--------------|--------|
| t-SNE shows distinct clusters; UMAP merges them | t-SNE over-emphasizes local structure; UMAP n_neighbors too large | Both views valid; check Leiden cluster assignments rather than embedding |
| PCA shows batch on PC1; UMAP hides it | UMAP preserves local neighborhood within each batch | Run UMAP only after batch correction; PCA is the canonical batch-effect diagnostic |
| PHATE shows continuous trajectory; UMAP shows discrete clusters | PHATE preserves transitions; UMAP "blobifies" continuous data | Use PHATE for trajectory display; UMAP for discrete cell-type display |
| Reproducibility breaks across re-runs | Random seed not set | Set seed; document version of umap-learn/openTSNE |
| Cluster boundaries differ between Seurat/scanpy UMAP | Different defaults for n_neighbors, min_dist, init | Standardize hyperparameters; report explicitly |

**Operational rule:** report ALL hyperparameters used (perplexity, n_neighbors, min_dist, random_state). State the embedding's interpretation limit ("local neighborhood; distances between clusters not meaningful"). For trajectory claims, validate with RNA velocity, pseudotime, or PHATE.

## Quantitative Thresholds

| Threshold | Value | Source |
|-----------|-------|--------|
| t-SNE perplexity | 30-50 for n>1000; max(5, n/30) for n<500 | Maaten 2008; Kobak-Berens 2019 |
| UMAP n_neighbors | 15-50 default range | umap-learn docs; Becht 2018 |
| UMAP min_dist | 0.1-0.5 | Tighter for crisp clusters, looser for continua |
| t-SNE learning rate | n / 12 (Kobak-Berens) | Default 200 over-shrinks large data |
| PCA n_components for downstream UMAP | 30-50 | Standard scanpy workflow |
| Single-cell n_neighbors for sc.pp.neighbors | 15-30 | Wolf 2018 Scanpy paper |
| Save DPI for publication | 300+ | Nature/Cell figure guidelines |
| Random seed | 42 (or any fixed integer) | Reproducibility |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| Plot differs between runs | Random seed not set | `random_state=42` always |
| PC1 = library size | No scaling/normalization | `vst()` or `log + scale` before PCA |
| Cluster shapes "interpreted" biologically | UMAP artifact | Do not interpret shape; report membership |
| scanpy save writes to wrong path | figdir + prefix concatenation | Set figdir explicitly OR use matplotlib.savefig |
| t-SNE fragments small dataset | Perplexity too high for n | Use perplexity = max(5, n/30) |
| Inter-cluster "distance" used in trajectory claim | UMAP distances not meaningful | Validate with RNA velocity / PHATE |
| Loadings interpreted on UMAP axes | UMAP has no loadings | Use PCA for loading-driven interpretation |

## Anticipated Reviewer Pushback

| Pushback | Standard response |
|----------|-------------------|
| "Why UMAP and not t-SNE?" | UMAP for cluster overview (faster, better global preservation given Becht 2018); t-SNE in supplementary if cluster boundaries are the focus |
| "What hyperparameters?" | Explicit n_neighbors, min_dist, n_pcs, random_state in caption AND methods |
| "Why is cluster X shaped this way?" | UMAP/t-SNE cluster shape is an embedding artifact; cluster membership is the biological observation |
| "Are these trajectories real?" | Validated via RNA velocity / PHATE / diffusion pseudotime (NOT inferred from UMAP layout alone) |
| "Why PCA?" | Variance explained per axis is interpretable for sample QC; loadings identify driving genes (uniquely PCA, NOT UMAP) |

## References

- Becht E, McInnes L, Healy J, et al. 2019. Dimensionality reduction for visualizing single-cell data using UMAP. *Nat Biotechnol* 37(1):38-44.
- Chari T, Pachter L. 2023. The specious art of single-cell genomics. *PLOS Comp Biol* 19(8):e1011288.
- Kobak D, Berens P. 2019. The art of using t-SNE for single-cell transcriptomics. *Nat Commun* 10:5416.
- McInnes L, Healy J, Melville J. 2018. UMAP: Uniform Manifold Approximation and Projection for dimension reduction. *arXiv:1802.03426*.
- Moon KR, van Dijk D, Wang Z, et al. 2019. Visualizing structure and transitions in high-dimensional biological data. *Nat Biotechnol* 37(12):1482-1492.
- van der Maaten L, Hinton G. 2008. Visualizing data using t-SNE. *J Mach Learn Res* 9:2579-2605.
- Wolf FA, Angerer P, Theis FJ. 2018. SCANPY: large-scale single-cell gene expression data analysis. *Genome Biol* 19:15.

## Related Skills

- single-cell/preprocessing - PCA / neighbor-graph computation before embedding
- single-cell/clustering - Leiden / Louvain cluster assignments visualized in UMAP
- single-cell/trajectory-inference - PHATE, diffusion pseudotime, RNA velocity for trajectory claims
- data-visualization/color-palettes - Categorical palette for cluster labels
- data-visualization/distribution-plots - Per-cluster gene-expression follow-up
- data-visualization/heatmaps-clustering - Alternative view of the same high-dim matrix
<!-- END FILE: data-visualization/dimensionality-reduction-plots/SKILL.md -->

## 子目录：data-visualization/distribution-plots

<!-- BEGIN FILE: data-visualization/distribution-plots/SKILL.md -->
---
name: bio-data-visualization-distribution-plots
description: Plot per-group distributions of continuous data using boxplots, violins, beeswarms, quasirandom jitter, and raincloud plots with sample-size honesty (Weissgerber 2015), KDE-bandwidth awareness, and N-aware encoding choices. Use when comparing distributions across a small number of groups — expression per cluster, biomarker per arm, scores per condition — and the bar-of-mean default is misleading.
tool_type: mixed
primary_tool: ggplot2
---

## Version Compatibility

Reference examples tested with: ggplot2 3.5+, ggbeeswarm 0.7+, ggdist 3.3+, gghalves 0.1.4+, seaborn 0.13+, matplotlib 3.8+, ptitprince 0.3+ (Python raincloud).

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters

If code throws ImportError, AttributeError, or TypeError, introspect the installed package and adapt the example to match the actual API rather than retrying.

# Distribution Plots

**"Plot the distribution per group"** -> Render boxplot, violin, beeswarm, or raincloud calibrated to N per group, the underlying distribution shape, and the audience's ability to read each encoding. The default `geom_bar(stat='summary')` is the canonical misleading choice — Weissgerber 2015 *PLOS Biol* documented that 703 top physiology papers use bar-of-mean despite multiple distinct distributions producing identical bars.

- R: `ggplot2::geom_boxplot`, `ggplot2::geom_violin`, `ggbeeswarm::geom_quasirandom`, `ggdist::stat_halfeye`, `gghalves::geom_half_violin`
- Python: `seaborn.boxplot/violinplot/swarmplot/stripplot`, `ptitprince.RainCloud`

## The Single Most Important Modern Insight -- Bars of Means Lie

Weissgerber, Milic, Winham & Garovic 2015 *PLOS Biol* 13:e1002128 surveyed 703 papers in top physiology journals and found that bar-and-line graphs of means dominate, despite **many distinct distributions producing identical bar plots**. Bimodal data, skewed data, and data with outliers all collapse to the same bar height and error bar. The bar plot is a hypothesis test result rendered as visualization; the visualization should show the data.

The modern alternative is to **show every point** for n < 30, layer summary on top, and reserve summary-only plots for large N where points would overplot.

## Decision Tree by N per Group

| N per group | Recommended | Avoid |
|-------------|-------------|-------|
| 3-10 | Dot plot or jittered raw points + median bar | Bar of mean |
| 10-30 | Beeswarm OR quasirandom + box overlay | Bare boxplot (hides bimodality) |
| 30-200 | Raincloud (Allen 2019) OR box + jitter | Bare violin (default KDE bandwidth oversmooths) |
| 200-1000 | Letter-value plot (Hofmann 2017) OR violin with explicit bandwidth | Box alone (collapses tails) |
| >1000 | Density (KDE) or histogram + summary stats | Individual points (overplot) |

**Always annotate N** somewhere on the plot (caption, x-axis tick label, or stratum count).

## Box, Violin, Beeswarm, Raincloud -- The Four Standard Encodings

### Boxplot (Tukey 1977) -- summary only

```r
ggplot(df, aes(group, value, fill = group)) +
    geom_boxplot(outlier.shape = NA, alpha = 0.7, width = 0.5) +
    geom_jitter(width = 0.2, alpha = 0.5, size = 1) +
    scale_fill_manual(values = c('#0072B2', '#D55E00')) +
    labs(x = NULL, y = 'Expression') +
    theme_classic()
```

Box shows: median, IQR, 1.5×IQR whiskers, outliers. Hides: bimodality, sample size, density.

**Notched boxplot** (`notch = TRUE`): notches show 95% CI for median (±1.58·IQR/√n); non-overlapping notches roughly indicate distinct medians. Use with N ≥ 15.

### Violin -- density + summary

```r
ggplot(df, aes(group, value, fill = group)) +
    geom_violin(alpha = 0.7, trim = FALSE,
                bw = 'SJ') +                            # Sheather-Jones bandwidth
    geom_boxplot(width = 0.1, fill = 'white', outlier.shape = NA) +
    scale_fill_manual(values = c('#0072B2', '#D55E00'))
```

**KDE bandwidth pitfall:** ggplot's default is Silverman's rule of thumb, which oversmooths bimodal data into a single mode. Use `bw = 'SJ'` (Sheather-Jones plug-in) for honest representation of multimodality.

**`trim = TRUE`** (default) cuts the violin at the data range — visually misleading because the violin's tails imply density extending beyond the data. `trim = FALSE` lets the KDE extend.

### Beeswarm / quasirandom -- every point shown deterministically

```r
library(ggbeeswarm)
ggplot(df, aes(group, value, color = group)) +
    geom_quasirandom(method = 'quasirandom', width = 0.3, alpha = 0.7) +
    scale_color_manual(values = c('#0072B2', '#D55E00')) +
    stat_summary(fun = median, geom = 'crossbar', width = 0.5, color = 'black')
```

Quasirandom (van der Corput sequence; Bostock implementation) gives reproducible jitter that fills space without random scatter. Beeswarm is similar but with collision avoidance. Both are deterministic — reruns produce identical layouts.

### Raincloud (Allen 2019) -- distribution + summary + raw

**Goal:** Show distribution (half-violin), summary (boxplot), and raw observations (jittered points) in a single per-group panel without occlusion.

**Approach:** Place a half-violin on one side, a thin boxplot in the middle, and jittered points on the other side via `gghalves::geom_half_violin` + `geom_boxplot` + `geom_half_point` with `position_nudge` offsets; flip to horizontal so the visual reads as a literal raincloud.

```r
library(gghalves)
ggplot(df, aes(group, value, fill = group, color = group)) +
    geom_half_violin(side = 'r', alpha = 0.7, position = position_nudge(x = 0.15)) +
    geom_boxplot(width = 0.15, outlier.shape = NA, alpha = 0.7,
                 position = position_nudge(x = -0.05)) +
    geom_half_point(side = 'l', alpha = 0.5, size = 1.5, range_scale = 0.4,
                    position = position_nudge(x = -0.2)) +
    scale_fill_manual(values = c('#0072B2', '#D55E00')) +
    scale_color_manual(values = c('#0072B2', '#D55E00')) +
    coord_flip()                                          # horizontal "raincloud"
```

```python
import ptitprince as pt
import seaborn as sns
pt.RainCloud(x='group', y='value', data=df,
             palette=['#0072B2', '#D55E00'],
             bw='scott', cut=0,                          # bandwidth + trim
             width_viol=0.6, orient='h')
```

Raincloud = half-violin (distribution) + boxplot (summary) + jittered raw points. Allen 2019 *Wellcome Open Res* 4:63 — modern publication default for N 30-200.

### Letter-value plot (Hofmann-Wickham 2017)

```r
library(lvplot)
ggplot(df, aes(group, value, fill = group)) +
    geom_lv(k = 5, alpha = 0.7) +
    scale_fill_manual(values = c('#0072B2', '#D55E00'))
```

Extends Tukey's boxplot via additional letter-value quantiles (Hofmann, Wickham, Kafadar 2017 *J Comput Graph Stat* 26:469). For large N, the standard boxplot collapses tail structure; letter-value preserves it.

```python
sns.boxenplot(x='group', y='value', data=df,
              palette=['#0072B2', '#D55E00'])             # seaborn calls it boxenplot
```

### Stacked / split violin (paired comparisons)

```r
library(introdataviz)               # split-violin geom
ggplot(df, aes(group, value, fill = condition)) +
    geom_split_violin(alpha = 0.7) +
    geom_boxplot(width = 0.15, position = position_dodge(0.5), outlier.shape = NA)
```

For 2-condition comparison within each group, split-violin shows both densities back-to-back. More compact than dodged violins.

## Per-Method Failure Modes

### Bar of mean with SEM

**Trigger:** `geom_bar(stat = 'summary')` + `geom_errorbar(stat = 'summary', fun.data = mean_se)`.

**Mechanism:** Mean ± SEM collapses all distributional information; reader cannot assess bimodality, skew, or N.

**Symptom:** Reviewer asks to "show the data"; the figure must be redone.

**Fix:** Replace with raincloud, beeswarm, or boxplot+jitter. Show points for N < 30.

### Violin with default Silverman bandwidth oversmooths bimodality

**Trigger:** `geom_violin()` without specifying `bw`.

**Mechanism:** Silverman's rule of thumb assumes unimodal Gaussian; oversmooths bimodal data into a single peak.

**Symptom:** Single-cell expression bimodality (off / on) renders as a unimodal violin; biologically false.

**Fix:** `bw = 'SJ'` (Sheather-Jones plug-in) for honest bimodality. Note: `nrd0` IS Silverman; `nrd` (Scott) oversmooths less than Silverman but Sheather-Jones is preferred.

### Notched boxplot with too-small N

**Trigger:** `notch = TRUE` with N < 15 per group.

**Mechanism:** Notch can extend beyond Q1/Q3, producing visually-misleading "inside-out" notches.

**Symptom:** ggplot warning ("notch went outside hinges"); notches look weird.

**Fix:** Use notches only with N ≥ 15. For smaller N, show raw points instead.

### Boxplot hides outliers when jittered points are overlaid

**Trigger:** `geom_boxplot() + geom_jitter()` with default `outlier.shape = 19`.

**Mechanism:** Outliers render twice — once from boxplot (large dots), once from jitter (smaller dots) — visually duplicated.

**Symptom:** Some points appear bigger than others without reason.

**Fix:** `geom_boxplot(outlier.shape = NA)` when overlaying raw points.

### Trim = TRUE on violin misleads about tails

**Trigger:** `geom_violin()` default `trim = TRUE`.

**Mechanism:** Default trims violin at the data range; the visual still shows narrowing "tails" implying density extends slightly beyond the data.

**Symptom:** Reader infers density beyond observed range.

**Fix:** `trim = FALSE` to let KDE extend, OR explicitly cap with `coord_cartesian`. Document the choice.

### No N annotation

**Trigger:** Boxplot with no N per group reported.

**Mechanism:** Reader cannot assess statistical power; tiny N looks identical to large N at this encoding.

**Symptom:** Reviewer requests "show N per group."

**Fix:** Add N to x-axis tick label (`Control (n=12)`) or use `stat_summary(geom='text', fun.data = function(x) data.frame(label = paste('n=', length(x))))`.

### Wide raincloud at small N

**Trigger:** Raincloud applied with N = 5 per group.

**Mechanism:** KDE with N=5 is meaningless; violin shape is artifact of bandwidth.

**Symptom:** Smooth violin from 5 points; misleads about underlying distribution.

**Fix:** For N < 30, drop the violin half; use box + raw points only.

## Reconciliation: When Encodings Disagree

| Pattern | Cause | Action |
|---------|-------|--------|
| Bar of mean shows clear separation; raincloud shows overlapping distributions | Bars hide overlap | Use raincloud; bars exaggerate effect |
| Violin shows unimodal; histogram shows bimodal | Default Silverman bandwidth oversmooths | Re-render with `bw = 'SJ'` |
| Boxplot medians look distinct; t-test n.s. | Boxplot of small N is unreliable | Show raw points; rerun with appropriate non-parametric test |
| Notched boxplot notches non-overlap; rank test n.s. | Notch is an approximation, not a hypothesis test | Notches are heuristic only; use formal test |

**Operational rule:** for N < 30, show every point. For N 30-200, raincloud. For N > 200, letter-value or violin with explicit bandwidth. Always annotate N.

## Quantitative Thresholds

| Threshold | Value | Source |
|-----------|-------|--------|
| N for valid notched boxplot | ≥15 | Common practice |
| N to show raw points | <30 | Weissgerber 2015 |
| N where violin > box | >30 (with explicit bandwidth) | Visualization guidance |
| Whisker length (Tukey) | 1.5 × IQR | Tukey 1977 |
| Notch length (McGill 1978) | ±1.58 × IQR / sqrt(N) | McGill 1978 |
| KDE bandwidth (Sheather-Jones) | plug-in selector | Sheather-Jones 1991 |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| Bimodal data shown as unimodal violin | Default Silverman bandwidth | `bw = 'SJ'` |
| Duplicate large points on box + jitter | `outlier.shape` not suppressed | `geom_boxplot(outlier.shape = NA)` |
| Notches "inside-out" | N too small | Show raw points; remove notch |
| Raincloud looks smooth at N=5 | KDE meaningless at small N | Drop violin half; box + points only |
| No N visible | Default boxplot | Add `n=...` to x label or stat_summary text |
| Violin tails extend beyond data | `trim = TRUE` default + KDE bandwidth | `trim = FALSE` and cap with `coord_cartesian` |
| Bar of mean criticized in review | Weissgerber 2015 default failure | Replace with raincloud or box+jitter |

## References

- Allen M, Poggiali D, Whitaker K, Marshall TR, van Langen J, Kievit RA. 2019. Raincloud plots: a multi-platform tool for robust data visualization. *Wellcome Open Res* 4:63. doi:10.12688/wellcomeopenres.15191.1
- Hofmann H, Wickham H, Kafadar K. 2017. Letter-value plots: boxplots for large data. *J Comput Graph Stat* 26(3):469-477. doi:10.1080/10618600.2017.1305277
- McGill R, Tukey JW, Larsen WA. 1978. Variations of box plots. *Am Stat* 32(1):12-16.
- Sheather SJ, Jones MC. 1991. A reliable data-based bandwidth selection method for kernel density estimation. *J R Stat Soc B* 53(3):683-690.
- Streit M, Gehlenborg N. 2014. Points of view: Bar charts and box plots. *Nat Methods* 11(2):117.
- Tukey JW. 1977. *Exploratory Data Analysis.* Addison-Wesley.
- Weissgerber TL, Milic NM, Winham SJ, Garovic VD. 2015. Beyond bar and line graphs: time for a new data presentation paradigm. *PLOS Biol* 13(4):e1002128. doi:10.1371/journal.pbio.1002128

## Related Skills

- data-visualization/statistical-annotation - Add p-value brackets to distribution plots
- data-visualization/color-palettes - CVD-safe categorical palettes
- data-visualization/ggplot2-fundamentals - Grammar of graphics base
- single-cell/markers-annotation - Stacked / split violin for scRNA gene-by-cluster
- clinical-biostatistics/effect-measures - Effect size to accompany distribution
<!-- END FILE: data-visualization/distribution-plots/SKILL.md -->

## 子目录：data-visualization/flow-and-transition-plots

<!-- BEGIN FILE: data-visualization/flow-and-transition-plots/SKILL.md -->
---
name: bio-data-visualization-flow-and-transition-plots
description: Build Sankey, alluvial, river, and CONSORT-style flow diagrams to visualize cohort transitions, cell-state changes, or pipeline filtering using ggalluvial, networkD3, plotly, and consort. Use when showing how entities move between categories across timepoints (cell states, drug response classes, patient flow through a trial) or filtering pipelines (variants filtered through QC stages).
tool_type: mixed
primary_tool: ggalluvial
---

## Version Compatibility

Reference examples tested with: ggalluvial 0.12+, networkD3 0.4+, plotly 4.10+, consort 0.2+ (CONSORT diagrams), pySankey 0.0.1+.

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('<pkg>')` then `?function_name`
- Python: `pip show <package>` then `help(module.function)`

If code throws ImportError, AttributeError, or TypeError, introspect the installed package and adapt the example to match the actual API rather than retrying.

# Flow and Transition Plots

**"Show how things flow between categories"** -> Render entities as ribbons whose width encodes count, flowing between ordered columns of categories. Sankey emphasizes total flow magnitude; alluvial emphasizes per-entity continuity (each row's path is traceable); CONSORT formalizes the trial-filtering convention. The decision space: which method (Sankey vs alluvial vs CONSORT), how to order categories within each column, and whether to highlight specific entity trajectories.

- R: `ggalluvial::geom_alluvium`, `networkD3::sankeyNetwork`, `consort::consort_plot`
- Python: `plotly.graph_objects.Sankey`, `pySankey`

## The Single Most Important Modern Insight -- Sankey vs Alluvial Are Different

**Sankey** plots show flow from sources to sinks; each ribbon represents an aggregate count. The horizontal direction is "flow." Use for energy flows, web-traffic funnels, cohort dropouts.

**Alluvial** plots track *individual entities* through multiple ordered category columns (axes). Each row of input data becomes a continuous ribbon; intersections at each axis show counts in each category. Use for cell-state transitions across timepoints, drug-response trajectories, longitudinal class changes.

A Sankey shows "100 cells became neuron, 50 became glia"; an alluvial shows "of the 100 that became neurons at t2, 80 came from the proliferating pool at t1." Different encoding, different scientific story.

## Decision Tree by Use Case

| Use case | Recommended | Tool |
|----------|-------------|------|
| Single timepoint, source-to-sink flow | Sankey | networkD3, plotly |
| Multi-timepoint entity trajectories | Alluvial | ggalluvial |
| Clinical trial patient flow | CONSORT (formal vertical box-and-arrow) | consort R package |
| Variant filtering pipeline | CONSORT-style flow | consort or manual diagrammeR |
| Cell-state transitions (scRNA timepoints) | Alluvial OR Sankey if 2 timepoints | ggalluvial |
| Drug response class changes | Alluvial | ggalluvial |
| Gene-set membership across conditions | UpSet (alternative) | data-visualization/upset-plots |

## ggalluvial -- Modern R Default for Alluvial

**Goal:** Visualize entity (e.g., cell, patient) trajectories across multiple ordered axes with ribbon-width = count.

**Approach:** Reshape to "lodes" (long) format with one row per entity-stratum, or "alluvia" (wide) format with one row per entity; use `geom_alluvium` for ribbons and `geom_stratum` for column boxes.

```r
library(ggalluvial)
library(ggplot2)

# Wide (alluvia) format: one row per entity
df_wide <- data.frame(
    entity_id = 1:1000,
    t1 = sample(c('A', 'B', 'C'), 1000, replace = TRUE),
    t2 = sample(c('A', 'B', 'C'), 1000, replace = TRUE),
    t3 = sample(c('A', 'B', 'C'), 1000, replace = TRUE))

ggplot(df_wide, aes(axis1 = t1, axis2 = t2, axis3 = t3)) +
    geom_alluvium(aes(fill = t1), alpha = 0.7, width = 1/6) +
    geom_stratum(width = 1/6, fill = 'grey90', color = 'black') +
    geom_text(stat = 'stratum', aes(label = after_stat(stratum)), size = 3) +
    scale_x_discrete(limits = c('t1', 't2', 't3')) +
    scale_fill_manual(values = c('#0072B2', '#D55E00', '#009E73')) +
    labs(y = 'Entities', x = NULL) +
    theme_classic()
```

`aes(fill = t1)` colors each ribbon by its starting class — common pattern for "where did this end up cluster come from?" stories.

## networkD3 -- Interactive Sankey

```r
library(networkD3)

# Nodes and links
nodes <- data.frame(name = c('Source A', 'Source B', 'Sink X', 'Sink Y', 'Sink Z'))
links <- data.frame(source = c(0, 0, 1, 1),
                    target = c(2, 3, 3, 4),
                    value  = c(40, 30, 50, 20))

sankeyNetwork(Links = links, Nodes = nodes,
              Source = 'source', Target = 'target', Value = 'value',
              NodeID = 'name',
              colourScale = JS('d3.scaleOrdinal(d3.schemeCategory10);'),
              fontSize = 12, nodeWidth = 30, height = 400, width = 700)
```

networkD3 produces interactive HTML — drag nodes, hover for values. For static publication figure, screenshot or export via `webshot2`.

## plotly Sankey (Python)

```python
import plotly.graph_objects as go

fig = go.Figure(go.Sankey(
    node=dict(label=['Source A', 'Source B', 'Sink X', 'Sink Y', 'Sink Z'],
              color=['#0072B2', '#56B4E9', '#D55E00', '#E69F00', '#009E73']),
    link=dict(source=[0, 0, 1, 1],
              target=[2, 3, 3, 4],
              value=[40, 30, 50, 20],
              color=['rgba(0,114,178,0.4)'] * 4)))
fig.update_layout(title='Flow', font_size=12)
fig.write_html('sankey.html')
fig.write_image('sankey.pdf')           # requires Kaleido (NOT orca; orca is EOL)
```

## CONSORT Diagrams -- The Formal Trial-Flow Standard

CONSORT 2010 (Schulz 2010 *BMJ* 340:c332) is the canonical clinical-trial flow diagram. The `consort` R package implements the structure:

```r
library(consort)

# Trial enrollment flow
g <- add_box(txt = c('Assessed for eligibility (n=200)'))
g <- add_side_box(g, txt = c('Excluded (n=50)\n  - Not meeting criteria (n=30)\n  - Declined (n=15)\n  - Other (n=5)'))
g <- add_box(g, txt = c('Randomized (n=150)'))
g <- add_split(g, txt = c('Allocated to intervention (n=75)\n  - Received as allocated (n=70)\n  - Did not receive (n=5)',
                          'Allocated to control (n=75)\n  - Received as allocated (n=73)\n  - Did not receive (n=2)'))
g <- add_box(g, txt = c('Lost to follow-up (n=2)\nDiscontinued (n=3)',
                        'Lost to follow-up (n=1)\nDiscontinued (n=2)'))
g <- add_box(g, txt = c('Analysed (n=75)\nExcluded from analysis (n=0)',
                        'Analysed (n=75)\nExcluded from analysis (n=0)'))
plot(g)
```

CONSORT is a *required* element in randomized trial publication (CONSORT 2010 statement, item 13a).

## Per-Method Failure Modes

### Sankey used when alluvial is appropriate

**Trigger:** Multi-timepoint cell-state data plotted as Sankey instead of alluvial.

**Mechanism:** Sankey collapses to source-sink summary; loses entity-trajectory continuity.

**Symptom:** Reader sees "cluster A -> 50% to B, 50% to C" but cannot trace individual trajectories.

**Fix:** Use ggalluvial for multi-axis trajectories; Sankey for single-step source-to-sink.

### Category ordering within column not specified

**Trigger:** Default ggalluvial ordering by frequency.

**Mechanism:** Categories shuffle position across columns; ribbons cross excessively.

**Symptom:** Visual spaghetti; hard to follow.

**Fix:** Set explicit factor levels (`factor(t1, levels = c('A', 'B', 'C'))`) AND consider ggalluvial's `lode.guidance` to minimize crossings.

### Ribbon coloring by destination instead of origin

**Trigger:** `geom_alluvium(aes(fill = t3))` for a "where did these come from" story.

**Mechanism:** Color encodes the wrong axis; readers misinterpret.

**Symptom:** Story is "where did final cluster Z come from" but ribbons are colored by Z — every ribbon to Z is the same color.

**Fix:** `aes(fill = t1)` if origin matters; `aes(fill = t3)` if destination matters.

### CONSORT diagram missing required boxes

**Trigger:** Skipping "Lost to follow-up" or "Excluded from analysis" boxes.

**Mechanism:** CONSORT 2010 requires reporting at each stage.

**Symptom:** Submission flagged for non-compliance with CONSORT 2010 item 13a.

**Fix:** Use `consort` package which scaffolds the required structure; cross-check against CONSORT 2010 statement.

### plotly Sankey value sum mismatch

**Trigger:** Source-to-target sums don't balance.

**Mechanism:** plotly Sankey requires conservation: sum of in-flows = sum of out-flows at each non-terminal node.

**Symptom:** Layout renders but node sizes look wrong; ribbons stretch/compress incorrectly.

**Fix:** Verify upstream data: per-node `sum(value where target=node) == sum(value where source=node)` for internal nodes.

### Static export of plotly Sankey fails silently

**Trigger:** `fig.write_image('sankey.pdf')` without kaleido installed.

**Mechanism:** plotly defaults to Kaleido for static export since orca EOL; kaleido is optional dependency.

**Symptom:** No file written; no error in some plotly versions.

**Fix:** `pip install kaleido`; verify with `import kaleido`.

## Reconciliation: When Implementations Differ

| Pattern | Cause | Action |
|---------|-------|--------|
| ggalluvial and networkD3 show different orderings | Different default stratum/node ordering | Set explicit factor levels / node order |
| CONSORT box counts don't sum | Box-content arithmetic error | Audit each box; consort package enforces structure |
| Cells appear/disappear between alluvial axes | Missing data in some timepoints | Decide: drop entities with NA; OR add "Missing" category |

## Quantitative Thresholds

| Threshold | Value | Source |
|-----------|-------|--------|
| Max categories per column for legibility | 5-7 | Visualization practical |
| Max axes for alluvial | 4-5 | Above this ribbons too crossed |
| CONSORT requirement | Required for RCTs | Schulz 2010 CONSORT 2010 |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| Excessive ribbon crossing | Categories unordered | Explicit factor levels; lode.guidance |
| Trajectories not traceable | Sankey used instead of alluvial | Switch to ggalluvial |
| CONSORT non-compliant | Missing required boxes | Use consort package |
| Sankey node sizes wrong | Flow not conserved | Audit source-target sums |
| plotly static export blank | kaleido not installed | `pip install kaleido` |
| Color story unclear | Wrong axis for fill | Decide origin vs destination story |

## References

- Brunson J. 2020. ggalluvial: Layered grammar for alluvial plots. *J Open Source Softw* 5(49):2017.
- Sankey MH. 1898. The thermal efficiency of steam engines. *Proc Inst Civil Eng* 134:278-312. (origin)
- Schulz KF, Altman DG, Moher D; CONSORT Group. 2010. CONSORT 2010 Statement: updated guidelines for reporting parallel group randomised trials. *BMJ* 340:c332.
- Riehmann P, Hanfler M, Froehlich B. 2005. Interactive Sankey diagrams. *IEEE Symp Information Visualization*.

## Related Skills

- data-visualization/upset-plots - Alternative for set-intersection rather than flow
- clinical-biostatistics/trial-reporting - CONSORT diagrams in trial publication
- single-cell/trajectory-inference - Cell-state transition data for alluvial
- workflows/biomarker-pipeline - Pipeline filtering flows
<!-- END FILE: data-visualization/flow-and-transition-plots/SKILL.md -->

## 子目录：data-visualization/forest-funnel-plots

<!-- BEGIN FILE: data-visualization/forest-funnel-plots/SKILL.md -->
---
name: bio-data-visualization-forest-funnel-plots
description: Build forest plots (HR, OR, RR, beta-coefficient summaries with CIs) and funnel plots (meta-analysis publication-bias diagnostics) using forestplot, metafor, ggforest, and MendelianRandomization with proper axis-scaling, summary-diamond placement, subgroup nesting, and Egger / trim-and-fill asymmetry tests. Use when summarizing effects across subgroups, trials, or instruments — meta-analysis, Mendelian randomization, subgroup HRs.
tool_type: r
primary_tool: metafor
---

## Version Compatibility

Reference examples tested with: metafor 4.4+, forestplot 3.1+, ggforestplot 0.1+ (subgroup forests), ggforest from survminer 0.4.9+, MendelianRandomization 0.10+.

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('<pkg>')` then `?function_name`

If code throws ImportError, AttributeError, or TypeError, introspect the installed package and adapt the example to match the actual API rather than retrying.

# Forest and Funnel Plots

**"Summarize effects across studies / subgroups"** -> Render each effect estimate (HR, OR, RR, β) as a square (size = inverse variance / weight), horizontal bar (95% CI), and label, with an optional summary diamond at the bottom from a meta-analysis pool (fixed-effect or random-effects). The funnel plot diagnoses publication bias by plotting effect size vs precision; asymmetry indicates missing small-study-with-null-result publications (Egger 1997).

- R: `metafor::forest`, `metafor::funnel`, `forestplot::forestplot`, `survminer::ggforest` (Cox HR forests), `MendelianRandomization::mr_forest`

## The Single Most Important Modern Insight -- Heterogeneity Is the First Question

A pooled effect estimate is meaningless if the underlying studies are heterogeneous. The Higgins I² statistic (Higgins-Thompson 2002 *Stat Med* 21:1539) quantifies between-study variance; the conventional 25/50/75% interpretation tiers come from the Cochrane Handbook §10.10.2 (Higgins et al editors), NOT the original Higgins-Thompson paper which cautioned against rigid cutoffs. A meta-analysis with I² > 75% and a pooled effect must explain the heterogeneity (subgroup analysis, meta-regression) — pooling without explanation is statistically defensible but biologically unhelpful.

A forest plot's bottom must report: pooled estimate + 95% CI + I² + τ² (between-study variance) + Q-test p-value. Without these, the plot is a list of effects, not a meta-analysis.

## Decision Tree by Analysis Type

| Analysis | Tool | Pooling model | Forest method |
|----------|------|---------------|---------------|
| Single-trial subgroup HRs | survminer::ggforest | None (subgroup display) | Coxph object |
| Meta-analysis of binary outcomes | metafor::rma -> forest() | DerSimonian-Laird or REML random-effects | Standard forest |
| Meta-analysis of continuous outcomes | metafor::rma(yi, vi) | REML random-effects | Standard forest |
| Mendelian randomization | MendelianRandomization::mr_forest | Multiple MR methods | MR-specific forest |
| Subgroup forest with interaction p | metafor::rma + addpoly + interaction model | Subgroup REML | Nested forest |
| Network meta-analysis | netmeta::forest.netmeta | Bayesian or frequentist | Network forest |
| Cumulative meta-analysis (over time) | metafor::cumul + forest | – | Cumulative forest |

## Fixed-Effect vs Random-Effects Meta-Analysis

| Model | Assumption | When appropriate | Pooled estimate weight |
|-------|------------|-------------------|------------------------|
| Fixed-effect (Mantel-Haenszel, IVS) | All studies estimate the same true effect | Single mechanism, homogeneous design | 1 / within-study variance |
| Random-effects (DerSimonian-Laird, REML) | Studies estimate distinct true effects from a common distribution | Heterogeneous designs / populations | 1 / (within + between variance) |

**Use random-effects by default.** Fixed-effect assumes all studies estimate the *same* parameter, which is almost never true across multi-center trials with different populations. REML is the modern default (Viechtbauer 2005); DerSimonian-Laird is the older default still commonly seen.

## metafor::rma + forest -- The Reference Implementation

**Goal:** Pool study-level effect estimates with random-effects meta-analysis; render a forest plot with study weights, individual effect+CI, and pooled summary diamond.

**Approach:** Compute per-study yi (effect) and vi (sampling variance); fit REML random-effects model; pass to forest() with prediction interval if heterogeneity is non-trivial.

```r
library(metafor)

# Input: per-study effect (yi) and variance (vi)
# For OR: yi = log(OR), vi = SE(log(OR))^2
# For HR: yi = log(HR), vi = SE(log(HR))^2
res <- rma(yi = log_or, vi = log_or_se^2,
           data = studies, slab = paste(author, year),
           method = 'REML')

# I^2 and tau^2 in the summary
summary(res)
# I^2 (residual heterogeneity)
# tau^2 (estimated amount of (residual) heterogeneity)
# Q-test for heterogeneity

forest(res,
       atransf = exp,                           # display OR on natural scale
       at = log(c(0.25, 0.5, 1, 2, 4)),         # ticks at meaningful OR values
       refline = 0,                              # log(1) for OR/HR/RR
       xlab = 'Odds Ratio (95% CI)',
       header = c('Study', 'OR [95% CI]'),
       mlab = bquote(paste('RE Model (Q = ', .(round(res$QE, 2)),
                            ', df = ', .(res$k - 1),
                            ', p = ', .(format.pval(res$QEp, digits = 2)),
                            '; ', I^2, ' = ', .(round(res$I2, 1)), '%)')),
       addpred = TRUE)                          # prediction interval per Higgins 2009
```

`addpred = TRUE` adds a 95% prediction interval — where a new study's effect is expected to fall (Higgins-Thompson-Spiegelhalter 2009 *JRSS-A*). This is the most honest summary when I² > 30%.

## ggforest for Cox Subgroup Forests

```r
library(survminer)
fit <- coxph(Surv(time, status) ~ treatment + age + sex + stage, data = df)
ggforest(fit,
         data = df,
         main = 'Subgroup HRs',
         cpositions = c(0.02, 0.22, 0.4),
         fontsize = 0.7,
         refLabel = 'Reference',
         noDigits = 2)
```

ggforest produces a publication-ready subgroup forest from a coxph object. For pre-specified subgroup analyses (treatment × subgroup interaction), test interaction explicitly and annotate the p-value.

## Small-k Regime -- When Meta-Analysis Asymptotics Break

For k < 5 studies, the REML-based 95% CI from `metafor::rma()` is severely anti-conservative — it relies on chi-square asymptotics that fail with few studies. Use **Hartung-Knapp-Sidik-Jonkman (HKSJ)** adjustment (`test = 'knha'`):

```r
res_hksj <- rma(yi = log_or, vi = log_or_se^2, data = studies,
                method = 'REML', test = 'knha')           # HKSJ for k<5
```

HKSJ uses a t-distribution with k-1 degrees of freedom and adjusts SE via the Q-statistic — well-calibrated even at k=3. For k < 3 a meta-analysis is not advisable; report individual study effects in a forest plot without a pooled summary.

Also: I² is uninterpretable below k = 5 (Borenstein 2017 *Res Synth Methods* 8:5); the point estimate has wide CI dominated by k itself, not heterogeneity. **Do not report I² for k < 5.**

## Funnel Plot and Egger Test

**Goal:** Diagnose publication bias by visual asymmetry of effect size vs precision.

**Approach:** Plot effect (x) vs SE (inverted y); under no bias, points form a symmetric inverted funnel with the pooled estimate at the apex. Asymmetry suggests missing small-N null-result studies. Egger's regression test (Egger 1997 *BMJ* 315:629) formalizes the asymmetry.

```r
funnel(res,
       xlab = 'log(OR)',
       refline = res$b)

# Egger's test
regtest(res, model = 'lm', predictor = 'sei')
# significant p indicates asymmetry; suggests publication bias

# Trim-and-fill (Duval-Tweedie 2000) -- adjusts for asymmetry
res_tf <- trimfill(res)
forest(res_tf)
funnel(res_tf)
```

**Contour-enhanced funnel plot** (Peters 2008 *J Clin Epidemiol* 61:991) overlays significance contours (p < 0.10, < 0.05, < 0.01); asymmetry concentrated in "non-significant" regions indicates publication bias more specifically than generic asymmetry.

```r
funnel(res, level = c(90, 95, 99), shade = c('white', 'gray55', 'gray75'),
       refline = 0, legend = TRUE)
```

## Per-Method Failure Modes

### Pooling under high heterogeneity without explanation

**Trigger:** Random-effects meta-analysis pooled with I² > 75%; no subgroup or meta-regression.

**Mechanism:** Pooled estimate is a weighted average across substantively different effects; biologically meaningless.

**Symptom:** Pooled OR = 1.5 with 95% CI (1.2-1.8) but per-study effects range 0.3-5.0.

**Fix:** Run subgroup analysis or meta-regression to explain heterogeneity; report I², τ², and prediction interval; do NOT report a single pooled effect as the answer.

### Fixed-effect when studies are heterogeneous

**Trigger:** Default fixed-effect model on multi-population data.

**Mechanism:** Fixed-effect weights = 1/within-study variance, ignoring between-study variance.

**Symptom:** CI is misleadingly narrow; reviewer asks "why fixed effect with high I²?"

**Fix:** Switch to REML random-effects (`method = 'REML'`); document the choice.

### Egger test p-value over-interpreted

**Trigger:** k < 10 studies; significant Egger p taken as definitive publication bias.

**Mechanism:** Egger's test is underpowered with few studies; sensitive to single outliers.

**Symptom:** Conclusion "publication bias" from k=6 trials.

**Fix:** Egger requires k ≥ 10 (Sterne 2011 *BMJ* 343:d4002); for fewer studies, visual funnel + contour-enhanced funnel is more reliable.

### Trim-and-fill imputed studies presented as data

**Trigger:** Reporting trim-and-fill adjusted estimate as "the answer."

**Mechanism:** Trim-and-fill is a sensitivity analysis; imputed studies are hypothetical.

**Symptom:** Original pooled OR = 2.0; trim-and-fill adjusted to 1.5; report says "adjusted estimate is 1.5."

**Fix:** Present original AND trim-and-fill side-by-side; trim-and-fill is sensitivity, not primary.

### Subgroup forest without interaction test

**Trigger:** Subgroup HRs plotted; conclusion "treatment works in subgroup X."

**Mechanism:** Visual differences across subgroups don't establish significant interaction.

**Symptom:** Subgroup forest shows HR=0.5 in subgroup A, HR=1.0 in subgroup B; no formal test.

**Fix:** Add treatment × subgroup interaction term to the model; report interaction p; cite Brookes 2001 / Wang 2007 for subgroup analysis caveats.

### Forest plot axis on linear scale for ratios

**Trigger:** OR/HR/RR plotted with linear x-axis.

**Mechanism:** Ratios are multiplicatively symmetric; linear axis compresses < 1 effects.

**Symptom:** OR = 0.5 (halving) appears smaller than OR = 2 (doubling) on a linear scale, even though they are biologically equivalent.

**Fix:** Always log-scale the x-axis for ratios. metafor's `atransf = exp` + `at = log(c(0.25, 0.5, 1, 2, 4))` is the canonical pattern.

### Weights not visible (point sizes uniform)

**Trigger:** Default forestplot package without weight encoding.

**Mechanism:** Reader cannot tell study influence on pool.

**Symptom:** A 5-patient pilot looks visually equivalent to a 5000-patient trial.

**Fix:** Use metafor `forest()` which auto-encodes weight via box size. forestplot package needs `boxsize =` argument.

## Reconciliation: When Methods Disagree

| Pattern | Cause | Action |
|---------|-------|--------|
| Fixed-effect significant; random-effects n.s. | High heterogeneity inflates RE variance | Trust random-effects when I² > 30% |
| Egger n.s. but funnel looks asymmetric | k < 10 -> Egger underpowered | Trust visual; report contour-enhanced funnel |
| Trim-and-fill imputes many studies | Severe asymmetry | Caution; sensitivity, not primary |
| Subgroup forest suggests effect modification; interaction test n.s. | Visual difference does not establish formal interaction | Trust interaction test |
| MR forest shows divergent estimates across methods | Pleiotropy or weak instruments | Run MR-Egger, weighted median, mode-based (sensitivity); cite Bowden 2015 |

## Quantitative Thresholds

| Threshold | Value | Source |
|-----------|-------|--------|
| I² substantial heterogeneity | > 50% | Cochrane Handbook §10.10.2 (Higgins et al editors) |
| I² considerable heterogeneity | > 75% | Cochrane Handbook §10.10.2 (Higgins et al editors) |
| Egger test min k | ≥ 10 | Sterne 2011 *BMJ* |
| Prediction interval (where new study lands) | report when I² > 30% | Higgins-Thompson-Spiegelhalter 2009 |
| Forest x-axis | log scale for ratios | Convention |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| Pooled estimate with I² = 90% | No heterogeneity exploration | Subgroup / meta-regression |
| Linear x-axis for OR forest | Ratios should be log-symmetric | `atransf = exp, at = log(...)` |
| Uniform point sizes | Weights not encoded | metafor::forest auto-encodes; forestplot needs boxsize |
| Egger from k=5 | Underpowered | k ≥ 10 for Egger |
| Trim-and-fill as primary | Sensitivity, not primary | Present both; document |
| Subgroup effect without interaction test | Visual ≠ test | Add interaction term |
| MR forest with single method | Pleiotropy risk | Triangulate methods |

## References

- Bowden J, Davey Smith G, Burgess S. 2015. Mendelian randomization with invalid instruments: effect estimation and bias detection through Egger regression. *Int J Epidemiol* 44(2):512-525.
- Brookes ST, Whitley E, Peters TJ, et al. 2001. Subgroup analyses in randomised controlled trials: quantifying the risks of false-positives and false-negatives. *Health Technol Assess* 5(33):1-56.
- DerSimonian R, Laird N. 1986. Meta-analysis in clinical trials. *Control Clin Trials* 7(3):177-188.
- Duval S, Tweedie R. 2000. Trim and fill: a simple funnel-plot–based method of testing and adjusting for publication bias in meta-analysis. *Biometrics* 56:455-463.
- Egger M, Davey Smith G, Schneider M, Minder C. 1997. Bias in meta-analysis detected by a simple, graphical test. *BMJ* 315(7109):629-634.
- Higgins JPT, Thompson SG. 2002. Quantifying heterogeneity in a meta-analysis. *Stat Med* 21(11):1539-1558.
- Higgins JPT, Thompson SG, Spiegelhalter DJ. 2009. A re-evaluation of random-effects meta-analysis. *JRSS-A* 172(1):137-159.
- Peters JL, Sutton AJ, Jones DR, Abrams KR, Rushton L. 2008. Contour-enhanced meta-analysis funnel plots help distinguish publication bias from other causes of asymmetry. *J Clin Epidemiol* 61(10):991-996.
- Sterne JAC, Sutton AJ, Ioannidis JPA, et al. 2011. Recommendations for examining and interpreting funnel plot asymmetry in meta-analyses of randomised controlled trials. *BMJ* 343:d4002.
- Viechtbauer W. 2010. Conducting meta-analyses in R with the metafor package. *J Stat Softw* 36(3):1-48.
- Hartung J, Knapp G. 2001. A refined method for the meta-analysis of controlled clinical trials with binary outcome. *Stat Med* 20(24):3875-3889.
- IntHout J, Ioannidis JPA, Borm GF. 2014. The Hartung-Knapp-Sidik-Jonkman method for random effects meta-analysis is straightforward and considerably outperforms the standard DerSimonian-Laird method. *BMC Med Res Methodol* 14:25.
- Borenstein M, Higgins JPT, Hedges LV, Rothstein HR. 2017. Basics of meta-analysis: I² is not an absolute measure of heterogeneity. *Res Synth Methods* 8(1):5-18.
- Higgins JPT, Thomas J, Chandler J, et al (editors). *Cochrane Handbook for Systematic Reviews of Interventions* (current version). Section 10.10.2 — interpretation tiers for I².

## Related Skills

- clinical-biostatistics/effect-measures - HR / OR / RR / NNT definitions
- clinical-biostatistics/subgroup-analysis - Interaction tests for subgroup HRs
- causal-genomics/mendelian-randomization - MR-specific forest + sensitivity
- clinical-biostatistics/trial-reporting - CONSORT and meta-analysis reporting
- data-visualization/color-palettes - Palette for multi-study or subgroup forests
<!-- END FILE: data-visualization/forest-funnel-plots/SKILL.md -->

## 子目录：data-visualization/genome-tracks

<!-- BEGIN FILE: data-visualization/genome-tracks/SKILL.md -->
---
name: bio-data-visualization-genome-tracks
description: Build genome-browser-style multi-track figures with pyGenomeTracks (config-driven), Gviz (R), and IGV batch screenshotting. Covers BigWig coverage tracks, BED/peak overlays, gene-model rendering, Hi-C matrix tracks, BedPE link arcs, spike-in-aware normalization, and the bamCoverage --normalizeUsing trap. Use when producing publication figures of genomic loci with stacked aligned tracks (coverage, peaks, genes, interactions) for ChIP-seq, ATAC-seq, RNA-seq, Hi-C, or generic locus visualization.
tool_type: mixed
primary_tool: pyGenomeTracks
---

## Version Compatibility

Reference examples tested with: pyGenomeTracks 3.9+, Gviz 1.46+ (Bioconductor), deepTools 3.5+, GenomicRanges 1.54+, IGV 2.18+ (batch mode).

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)`
- R: `packageVersion('<pkg>')` then `?function_name`
- CLI: `<tool> --version` then `<tool> --help`

If code throws ImportError, AttributeError, or TypeError, introspect the installed package and adapt the example to match the actual API rather than retrying.

# Genome Browser Tracks

**"Plot a genomic locus with multiple tracks"** -> Build a stacked figure where each track (coverage from BigWig, peaks from BED, genes from GTF, Hi-C from cool, loops from BedPE) is aligned to genome coordinates. The decisions that matter: track normalization (especially for ChIP-Rx spike-in), gene-model rendering style (UCSC vs FlyBase), y-axis sharing across samples, and which tool fits the workflow — pyGenomeTracks (config-driven, reproducible, headless), Gviz (R Bioconductor), IGV batch (interactive-tool screenshots).

- Python / CLI: `pyGenomeTracks` (Lopez-Delisle 2021 *Bioinformatics* 37:422)
- R: `Gviz::plotTracks` (Hahne-Ivanek 2016)
- Interactive: IGV (Robinson 2011 *Nat Biotechnol* 29:24) with batch scripting

## The Single Most Important Modern Insight -- Spike-In Normalization Cannot Be Done With --normalizeUsing

deepTools `bamCoverage` is the canonical BigWig generator. Its `--normalizeUsing` flag accepts {RPKM, CPM, BPM, RPGC, None} — none of which implement ChIP-Rx spike-in normalization. All four divide by *sample-internal* mapped read counts and will UNDO any spike-in correction.

For ChIP-Rx (Orlando 2014 *Cell Rep* 9:1163):
1. Compute spike-in scale factor externally: `scale = 1 / (spike_reads_per_million)` OR per Orlando method
2. Pass via `--scaleFactor <value>` with `--normalizeUsing None`
3. **Do NOT combine `--scaleFactor` with `--normalizeUsing CPM/RPGC`** — re-normalizes the signal and undoes spike-in

This is the most common silent error in ChIP-seq visualization. The BigWig looks fine; the cross-sample comparison is wrong by the spike-in factor.

## pyGenomeTracks — Config-Driven, Reproducible

**Goal:** Render a multi-track locus figure from a config file specifying each track's source file, style, height, and color.

**Approach:** Write an `.ini` file with one section per track; invoke `pyGenomeTracks --tracks tracks.ini --region chr1:1000000-2000000 --outFileName out.pdf`.

```ini
# tracks.ini
[x-axis]
where = top
fontsize = 8

[h3k27ac]
file = h3k27ac.bw
title = H3K27ac
height = 3
color = #D55E00
min_value = 0
max_value = 50
number_of_bins = 700
summary_method = mean
nans_to_zeros = true

[spacer]
height = 0.3

[peaks]
file = h3k27ac_peaks.narrowPeak
title = Peaks
height = 0.8
color = #888888
display = collapsed
labels = false
file_type = narrowPeak

[loops]
file = loops.bedpe
title = Loops
height = 2
file_type = links
links_type = arcs
color = '#0072B2'
line_width = 0.5

[hic]
file = matrix.cool
title = Hi-C (KR-normalized)
height = 8
depth = 1000000
min_value = 0
max_value = auto
transform = log1p
colormap = RdYlBu_r

[genes]
file = gencode.v44.gtf
title = Genes
height = 5
fontsize = 8
style = UCSC                            # or 'flybase'; UCSC merges transcripts, flybase shows all
prefered_name = gene_name
merge_transcripts = true
color = '#3C5488'
border_color = black
```

```bash
pyGenomeTracks --tracks tracks.ini \
    --region chr1:1000000-2000000 \
    --outFileName locus.pdf \
    --width 18 \                          # CENTIMETERS not inches; default 40 cm
    --dpi 300

# For multiple regions from a BED:
pyGenomeTracks --tracks tracks.ini --BED regions.bed \
    --outFileName multi.pdf
```

**`--width` is in centimeters**, not inches. Default 40 cm; Nature double-column = 18.3 cm. `--decreasingXAxis` flips orientation for minus-strand loci.

## Gviz (R Bioconductor)

```r
library(Gviz)
library(GenomicRanges)
library(TxDb.Hsapiens.UCSC.hg38.knownGene)

# Tracks
axTrack <- GenomeAxisTrack()
itrack <- IdeogramTrack(genome = 'hg38', chromosome = 'chr1')

txdb <- TxDb.Hsapiens.UCSC.hg38.knownGene
grTrack <- GeneRegionTrack(txdb, genome = 'hg38', chromosome = 'chr1',
                            name = 'Genes', transcriptAnnotation = 'symbol',
                            collapseTranscripts = 'meta')

dTrack <- DataTrack(range = 'h3k27ac.bw', type = 'h',
                     chromosome = 'chr1', name = 'H3K27ac',
                     col.histogram = '#D55E00', fill.histogram = '#D55E00')

aTrack <- AnnotationTrack(range = 'peaks.bed', name = 'Peaks',
                           chromosome = 'chr1', fill = '#888888',
                           stacking = 'dense')

# Render
plotTracks(list(itrack, axTrack, dTrack, aTrack, grTrack),
           from = 1000000, to = 2000000,
           sizes = c(1, 1, 3, 1, 4),
           background.title = 'transparent',
           cex.title = 0.7,
           cex.axis = 0.6)
```

## IGV Batch Scripting

For interactive-tool screenshots without launching the GUI:

```bash
# batch.txt
new
genome hg38
load sample.bam
load peaks.bed
snapshotDirectory ./screenshots
goto chr1:1000000-2000000
sort base
maxPanelHeight 500
snapshot region1.png
goto chr2:5000000-6000000
snapshot region2.png
exit
```

```bash
igv -b batch.txt
```

IGV batch is suitable when the workflow requires IGV's specific rendering style (allele frequencies, split-read pairs, soft-clipped sequences) — features pyGenomeTracks and Gviz don't replicate.

## BigWig Generation — The Spike-In Trap

```bash
# WITHOUT spike-in (e.g., RNA-seq, ATAC-seq):
bamCoverage -b sample.bam -o sample.bw \
    --binSize 10 \
    --normalizeUsing BPM \
    --effectiveGenomeSize 2913022398        # hg38 effective; check for build

# CORRECT ChIP-Rx spike-in:
# 1. Compute scale factor externally
SPIKE_RPM=$(samtools view -c sample.spike.bam) 
SCALE_FACTOR=$(echo "scale=10; 1000000 / $SPIKE_RPM" | bc)

# 2. Apply --scaleFactor with --normalizeUsing None
bamCoverage -b sample.bam -o sample.bw \
    --binSize 10 \
    --normalizeUsing None \                  # CRITICAL: None
    --scaleFactor $SCALE_FACTOR

# INCORRECT (silent error):
bamCoverage -b sample.bam -o sample.bw \
    --normalizeUsing CPM \                   # WRONG: undoes spike-in
    --scaleFactor $SCALE_FACTOR
```

## Track Comparison Across Samples

For multi-sample tracks (control vs treatment), set shared y-axis explicitly:

```ini
[sample1_bw]
file = sample1.bw
title = Control
height = 3
color = '#0072B2'
min_value = 0
max_value = 100                              # SHARED max across samples

[sample2_bw]
file = sample2.bw
title = Treatment
height = 3
color = '#D55E00'
min_value = 0
max_value = 100                              # SAME max for visual comparability
overlay_previous = share-y                   # for overlay; omit for stack
```

Without shared y-axis, the "taller" sample is the one with stronger absolute signal — but the figure visually conflates signal magnitude with rendering scale.

## Per-Method Failure Modes

### bamCoverage --normalizeUsing undoes spike-in

**Trigger:** ChIP-Rx workflow using `--normalizeUsing CPM` AND `--scaleFactor`.

**Mechanism:** CPM normalization divides by sample-internal reads; cancels the spike-in factor.

**Symptom:** Spike-in-normalized tracks look the same as un-normalized; cross-condition comparison wrong.

**Fix:** `--normalizeUsing None` with `--scaleFactor`. Validate by examining tracks at known reference loci where signal should match between samples.

### Different y-axis across samples

**Trigger:** Auto-scaled `max_value = auto` per-sample.

**Mechanism:** Each track scales independently to its own max.

**Symptom:** Visual "looks same" across samples that actually differ in magnitude.

**Fix:** Set explicit `min_value` and `max_value` to the same value across samples.

### Wrong gene-model style

**Trigger:** `style = flybase` for human data (or vice versa).

**Mechanism:** UCSC merges overlapping transcripts; flybase shows all isoforms; pile-up of isoforms unreadable for transcript-dense human loci.

**Symptom:** Gene track is a forest of overlapping arrows.

**Fix:** `style = UCSC` for human/mouse; `merge_transcripts = true` to collapse to canonical isoform.

### pyGenomeTracks --width interpreted as inches

**Trigger:** `--width 7` thinking inches.

**Mechanism:** Default unit is centimeters; `--width 7` is 7 cm = 2.75 inches.

**Symptom:** Tiny figure that doesn't match journal column width.

**Fix:** `--width 18.3` for Nature double column (18.3 cm = 183 mm). `--width 8.9` for single column.

### Track order top-down vs bottom-up confusion

**Trigger:** Expecting tracks in config-file order; pyGenomeTracks renders top-to-bottom (config[0] = top).

**Mechanism:** Convention differs across tools (Gviz top-to-bottom; some browsers bottom-to-top).

**Symptom:** Gene model at top instead of bottom.

**Fix:** Verify against config file order; for "genes at bottom" put `[genes]` section last.

### Hi-C matrix track depth too low

**Trigger:** `depth = 100000` for a 2 Mb region.

**Mechanism:** Hi-C matrix track shows interactions up to `depth` distance; smaller than region collapses the triangle.

**Symptom:** Hi-C track shows only a thin band.

**Fix:** `depth` should be ≥ half the region width; for 2 Mb region, `depth = 1000000` minimum.

### IGV batch script silent failures

**Trigger:** Typo in batch command; IGV continues to next command.

**Mechanism:** IGV batch mode doesn't fail-fast.

**Symptom:** Subset of snapshots missing; no error.

**Fix:** Verify each snapshot was produced; small batches and `set echo TRUE` for debugging.

## Reconciliation: When Tracks Disagree

| Pattern | Cause | Action |
|---------|-------|--------|
| Tracks look identical pre/post spike-in | --normalizeUsing canceled spike-in | Switch to None + --scaleFactor |
| Coverage differs between bamCoverage and IGV | Different binning; smoothing default | Specify --binSize explicitly; verify with raw BAM |
| Peaks in different positions across tools | Different peak-caller output (MACS narrowPeak vs broadPeak) | Document caller; cross-reference upstream chip-seq/peak-calling |
| Hi-C matrix orientation flipped | Pre-rotation vs post-rotation convention | Most tools assume upper-triangle; check vendor |

## Quantitative Thresholds

| Threshold | Value | Source |
|-----------|-------|--------|
| pyGenomeTracks --width default | 40 cm | Tool default; Nature ~18.3 cm |
| pyGenomeTracks --dpi recommended | 300 for publication | Standard |
| bamCoverage --binSize typical | 10-50 bp | Resolution vs file size trade-off |
| Hi-C track depth | >= half region width | Tool convention |
| Effective genome size hg38 | 2913022398 | UCSC |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| Spike-in normalized tracks look unnormalized | --normalizeUsing canceled spike-in | --normalizeUsing None + --scaleFactor |
| Y-axis differs across samples | Auto-scaling per-track | Explicit min/max in config |
| Gene track unreadable | flybase style on dense human locus | UCSC + merge_transcripts = true |
| Figure tiny | --width interpreted as inches | --width in CM |
| Hi-C band thin | depth too small | depth >= 0.5 × region width |
| IGV screenshots missing | Batch error silent | Verify per-snapshot; small batches |
| Coverage off by 2x | Strand-specific issue | Use --filterRNAstrand or split strands |

## References

- Hahne F, Ivanek R. 2016. Visualizing genomic data using Gviz and Bioconductor. *Methods Mol Biol* 1418:335-351.
- Lopez-Delisle L, Rabbani L, Wolff J, et al. 2021. pyGenomeTracks: reproducible plots for multivariate genomic datasets. *Bioinformatics* 37(3):422-423.
- Orlando DA, Chen MW, Brown VE, et al. 2014. Quantitative ChIP-seq normalization reveals global modulation of the epigenome. *Cell Rep* 9(3):1163-1170.
- Ramírez F, Ryan DP, Grüning B, et al. 2016. deepTools2: a next generation web server for deep-sequencing data analysis. *Nucleic Acids Res* 44(W1):W160-W165.
- Robinson JT, Thorvaldsdóttir H, Winckler W, et al. 2011. Integrative Genomics Viewer. *Nat Biotechnol* 29(1):24-26.

## Related Skills

- alignment-files/bam-statistics - BAM-level QC before bigwig
- chip-seq/peak-calling - Peak files for tracks
- chip-seq/chipseq-visualization - ChIP-seq-specific tracks
- hi-c-analysis/hic-visualization - Hi-C-specific contact maps
- alternative-splicing/sashimi-plots - Splice-junction tracks
- data-visualization/multipanel-figures - Combining track figures
- genome-intervals/bigwig-tracks - BigWig file handling
<!-- END FILE: data-visualization/genome-tracks/SKILL.md -->

## 子目录：data-visualization/ggplot2-fundamentals

<!-- BEGIN FILE: data-visualization/ggplot2-fundamentals/SKILL.md -->
---
name: bio-data-visualization-ggplot2-fundamentals
description: Build publication-quality figures in R with ggplot2 using the grammar of graphics (data + aesthetics + geometries + scales + facets + themes) with CVD-safe palettes, cairo_pdf TrueType embedding, programmatic aes via tidy evaluation, and the theme_classic publication baseline. Use when producing static figures in R for papers, presentations, or reports.
tool_type: r
primary_tool: ggplot2
goal_approach_exempt: true
---

## Version Compatibility

Reference examples tested with: ggplot2 3.5+, scales 1.3+, ggrepel 0.9.5+, ggtext 0.1.2+, viridis 0.6+, scico 1.5+, patchwork 1.2+ (axes='collect' requires 1.2.0+).

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters

If code throws ImportError, AttributeError, or TypeError, introspect the installed package and adapt the example to match the actual API rather than retrying.

# ggplot2 Fundamentals

**"Build a publication figure in R"** -> Express the figure as **data + aesthetic mappings + one or more geometries + scales + facets + theme**. The grammar of graphics (Wilkinson 2005; Wickham 2010 *J Comput Graph Stat* 19:3) makes each visual element separately addressable — change scales without rewriting geoms; swap geom_point for geom_violin without touching aesthetics.

- R: `ggplot(data, aes(x, y)) + geom_point() + scale_color_manual(...) + theme_classic()`
- Programmatic: `aes(x = .data[[var]])` for tidy-eval; `!!sym(var)` for older base R style

## The Three Modern Defaults

1. **theme_classic() + remove panel grid + Okabe-Ito palette** as the publication baseline. `theme_minimal` adds light gridlines; `theme_bw` adds a panel border; both work but `theme_classic` is the cleanest for journals.

2. **cairo_pdf for export** — `ggsave('out.pdf', device = cairo_pdf)` embeds TrueType fonts (searchable PDFs); default `ggsave('.pdf')` uses pdf() which produces journal-incompatible fonts on some systems.

3. **Tidy evaluation for programmatic aes** — `aes(x = .data[[var]])` is the modern idiom (ggplot2 3.0+); the older `aes_string(x = var)` is deprecated. For dplyr-style symbol evaluation, use `!!sym(var)` with `aes(x = !!sym(var))`.

## Grammar in Layers

```r
library(ggplot2)

# data + aes + geom is the minimum
ggplot(df, aes(x = condition, y = expression)) +
    geom_boxplot() +
    geom_jitter(width = 0.2, alpha = 0.5) +
    # scales
    scale_y_continuous(trans = 'log10', labels = scales::label_log()) +
    scale_color_manual(values = c('#0072B2', '#D55E00')) +
    # labels
    labs(x = NULL, y = 'Expression (log10)',
         title = 'Gene X across conditions',
         caption = 'Source: ...') +
    # facets
    facet_wrap(~ tissue, ncol = 3, scales = 'free_y') +
    # theme
    theme_classic(base_size = 10) +
    theme(panel.grid = element_blank(),
          strip.background = element_blank(),
          strip.text = element_text(face = 'bold'))
```

## Common Geoms

```r
geom_point(alpha = 0.7, size = 1, rasterize = TRUE)   # rasterize: ggplot2 3.5+ inline OR ggrastr::rasterize()
geom_line(linewidth = 0.5)                             # linewidth replaces size for lines (ggplot2 3.4+)
geom_col()                                              # bar with y values (use this; geom_bar(stat='identity') is older)
geom_bar()                                              # bar with counts
geom_boxplot(outlier.shape = NA)                       # always suppress when overlaying jitter
geom_violin(bw = 'SJ', trim = FALSE)                   # Sheather-Jones bandwidth; show full tails
geom_histogram(bins = 30)                              # bins NOT binwidth for control
geom_density(alpha = 0.5)
geom_tile(aes(fill = z))                               # heatmap building block
geom_text(aes(label = label), check_overlap = TRUE)
geom_text_repel(aes(label = label), max.overlaps = Inf)   # ggrepel; max.overlaps = Inf prevents silent label drops
```

## Aesthetic Mappings

```r
aes(x, y, color, fill, shape, size, alpha, linetype, linewidth, group)

# Color vs fill: color = stroke; fill = interior (boxplot, bar, area, polygon)
# Use both when needed: geom_point(aes(color = group, fill = group), shape = 21)
```

**Constant inside vs mapping inside aes** is a common confusion:
```r
geom_point(color = 'red')             # constant: every point red
geom_point(aes(color = group))        # mapping: color varies with group
```

## Scales

```r
# Continuous
scale_x_continuous(limits = c(0, 10), breaks = seq(0, 10, 2),
                    labels = scales::label_number(scale = 1e-6, suffix = 'M'))
scale_y_log10()
scale_y_continuous(trans = 'sqrt')

# Discrete
scale_x_discrete(limits = c('Control', 'Treatment', 'Vehicle'))   # explicit order
scale_color_manual(values = c(Control = '#0072B2', Treatment = '#D55E00'))

# Colormap (sequential, diverging, cyclic) -- see color-palettes
scale_color_viridis_c(option = 'viridis')
scale_color_scico(palette = 'batlow')                              # Crameri
scale_fill_gradient2(low = '#0072B2', mid = 'white', high = '#D55E00', midpoint = 0)

# Date / time
scale_x_date(date_breaks = '1 year', date_labels = '%Y')
```

## Facets

```r
facet_wrap(~ var, ncol = 3, scales = 'free_y')
facet_grid(rows = vars(condition), cols = vars(timepoint), scales = 'free_x')
facet_grid(condition ~ timepoint)                                  # formula syntax
```

`scales = 'free_y'` lets each panel have its own y-range — appropriate when biological scales differ across facets. `scales = 'fixed'` (default) is the right choice when comparing across panels.

## Theme

```r
# Publication baseline
theme_pub <- theme_classic(base_size = 10) +
    theme(
        panel.grid = element_blank(),
        axis.text = element_text(color = 'black'),
        axis.ticks = element_line(color = 'black', linewidth = 0.3),
        axis.line = element_line(color = 'black', linewidth = 0.3),
        legend.position = 'right',
        legend.key.size = unit(0.4, 'cm'),
        strip.background = element_blank(),
        strip.text = element_text(face = 'bold', size = 9),
        plot.title = element_text(face = 'bold', size = 11),
        plot.tag = element_text(face = 'bold', size = 11))

# Save as a function for re-use across project
```

## Programmatic Plots (Tidy Evaluation)

```r
# Pass variable name as a string
plot_var <- function(df, x_var, y_var) {
    ggplot(df, aes(x = .data[[x_var]], y = .data[[y_var]])) +
        geom_point()
}
plot_var(df, 'PC1', 'PC2')

# Alternative: bare names via embracing
plot_var2 <- function(df, x_var, y_var) {
    ggplot(df, aes(x = {{ x_var }}, y = {{ y_var }})) +
        geom_point()
}
plot_var2(df, PC1, PC2)
```

`aes_string` is deprecated as of ggplot2 3.0. `.data[[var]]` is the modern programmatic idiom.

## Labels with ggtext (rich-text)

```r
library(ggtext)
ggplot(df, aes(x, y)) + geom_point() +
    labs(x = 'log<sub>2</sub> fold change',
         y = '\\u2212log<sub>10</sub>(*p*)') +
    theme(axis.title.x = element_markdown(),
          axis.title.y = element_markdown())
```

ggtext renders inline HTML / Markdown in titles, captions, axis labels — much better than `expression(...)` for italics + subscripts + special characters.

## Saving — TrueType Embedding

```r
# cairo_pdf for TrueType embedded; portable across systems
ggsave('figure.pdf', plot = p,
       width = 89, height = 70, units = 'mm',
       device = cairo_pdf)

# Vector + raster mix via ggrastr (for large scatter)
library(ggrastr)
ggplot(df, aes(x, y)) +
    rasterise(geom_point(alpha = 0.5), dpi = 300) +
    theme_pub
ggsave('out.pdf', device = cairo_pdf)

# PNG for raster
ggsave('figure.png', p, width = 89, height = 70, units = 'mm', dpi = 300)

# TIFF for some journals
ggsave('figure.tiff', p, width = 89, height = 70, units = 'mm', dpi = 300,
       compression = 'lzw')
```

## Common Failure Modes

### Default ggsave fonts not embedded

**Trigger:** `ggsave('out.pdf', p)` without `device = cairo_pdf`.

**Mechanism:** Default pdf() device on some systems produces non-embedded fonts.

**Symptom:** Reviewer or coauthor opens PDF; text renders in wrong font; journal rejects.

**Fix:** Always `device = cairo_pdf` for PDF saves.

### Mapping vs constant aesthetic confusion

**Trigger:** `geom_point(aes(color = 'red'))` — string 'red' becomes a categorical mapping.

**Mechanism:** `aes()` interprets its arguments as variables; 'red' becomes a 1-level factor and gets mapped to the FIRST default color.

**Symptom:** Points appear blue (or whatever default) with a legend showing "red" as a category.

**Fix:** Move outside aes: `geom_point(color = 'red')` for a constant; keep inside for a mapping.

### linewidth vs size for lines

**Trigger:** `geom_line(size = 0.5)` in ggplot2 3.4+.

**Mechanism:** ggplot2 3.4+ renamed line-width control from `size` to `linewidth`; `size` still works for points.

**Symptom:** Warning "Using `size` aesthetic for lines was deprecated"; lines render but warning.

**Fix:** `geom_line(linewidth = 0.5)`. `geom_point(size = 1)` is correct.

### facet_wrap scales = 'free' confuses cross-panel comparison

**Trigger:** `facet_wrap(~ var, scales = 'free')` for figures intended to compare across panels.

**Mechanism:** Each panel has its own scale; visual comparison invalid.

**Symptom:** Reviewer asks "why are these heights different?"

**Fix:** Use `scales = 'fixed'` (default) when cross-panel comparison matters; use `'free_y'` only when panels are inherently different scales.

### aes_string deprecated

**Trigger:** `aes_string(x = 'PC1', y = 'PC2')` for programmatic plotting.

**Mechanism:** Deprecated since ggplot2 3.0; emits warning.

**Symptom:** Deprecation warning in script log.

**Fix:** `aes(x = .data[['PC1']], y = .data[['PC2']])` OR `aes(x = !!sym(x_var))`.

### ggrepel max.overlaps default drops labels

**Trigger:** `geom_text_repel(aes(label = label))` with N > 10 labels.

**Mechanism:** Default `max.overlaps = 10`; labels exceeding this are silently dropped with a warning.

**Symptom:** Some labeled genes are silently missing; warning buried in log.

**Fix:** `geom_text_repel(aes(label = label), max.overlaps = Inf)` OR `options(ggrepel.max.overlaps = Inf)` at script top.

### Saving with size in inches but intended mm

**Trigger:** `ggsave('out.pdf', p, width = 89, height = 70)` thinking mm.

**Mechanism:** Default `units = 'in'`.

**Symptom:** Figure is 89 inches wide — too large to open in Illustrator.

**Fix:** `units = 'mm'` explicit. Nature single column = 89mm; double column = 183mm.

## References

- Wickham H. 2016. *ggplot2: Elegant Graphics for Data Analysis* (2nd ed). Springer.
- Wickham H. 2010. A layered grammar of graphics. *J Comput Graph Stat* 19(1):3-28.
- Wilkinson L. 2005. *The Grammar of Graphics* (2nd ed). Springer.

## Related Skills

- data-visualization/color-palettes - Scale_color/_fill palette selection
- data-visualization/multipanel-figures - patchwork composition
- data-visualization/distribution-plots - Box / violin / raincloud geoms
- data-visualization/volcano-and-ma-plots - ggplot2 volcano with ggrepel
- data-visualization/heatmaps-clustering - ComplexHeatmap and ggplot2 geom_tile
<!-- END FILE: data-visualization/ggplot2-fundamentals/SKILL.md -->

## 子目录：data-visualization/heatmaps-clustering

<!-- BEGIN FILE: data-visualization/heatmaps-clustering/SKILL.md -->
---
name: bio-data-visualization-heatmaps-clustering
description: Build clustered heatmaps for expression matrices and other features-by-samples data with rigorous distance/linkage/scaling choices, robust color mapping, optimal leaf ordering, and ComplexHeatmap/pheatmap/seaborn rendering. Covers the ward.D vs ward.D2 trap, the row-vs-column scaling decision, multi-track annotations, oncoPrint, and raster rendering for large matrices. Use when visualizing expression patterns across samples or identifying co-regulated clusters.
tool_type: mixed
primary_tool: ComplexHeatmap
---

## Version Compatibility

Reference examples tested with: ComplexHeatmap 2.18+, pheatmap 1.0.13 (still maintained as of 2025-06), circlize 0.4.16+, seaborn 0.13+, scipy 1.12+, scanpy 1.10+, ggplot2 3.5+.

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters

If code throws ImportError, AttributeError, or TypeError, introspect the installed package and adapt the example to match the actual API rather than retrying.

# Heatmaps and Hierarchical Clustering

**"Make a clustered heatmap"** -> Render an expression / feature matrix as a colored grid with hierarchical-clustering dendrograms, after committing to (a) how to scale the data (row z-score vs raw vs robust), (b) which distance metric (Euclidean vs correlation vs Manhattan), (c) which linkage criterion (ward.D2 vs complete vs average), (d) how to order the leaves (default vs optimal leaf ordering), (e) how to map values to color (sequential vs diverging, robust quantile bounds), and (f) which package can handle the matrix size and annotation complexity.

- R: `ComplexHeatmap::Heatmap()` (modern default), `pheatmap::pheatmap()` (still maintained, simpler API)
- Python: `seaborn.clustermap()`, `scanpy.pl.heatmap()` (single-cell-aware)

## The Single Most Important Modern Insight -- Distance, Linkage, and Scaling Are Three Independent Decisions

A heatmap's dendrograms are produced by three orthogonal choices, each with material biological consequences:

1. **Scaling** decides what "similar" means. Row z-scoring asks "do these genes covary across samples?" — it strips absolute level. Raw values ask "do these genes have similar magnitude AND pattern?" Robust scaling (quantile clip) asks "do these covary after suppressing outliers?"
2. **Distance metric** decides how dissimilar two profiles are. Euclidean on z-scored data ≈ `1 − Pearson` correlation; Manhattan tolerates outliers; correlation distance preserves co-regulation patterns regardless of amplitude.
3. **Linkage** decides how to merge clusters. Ward minimizes within-cluster sum of squares (compact, spherical clusters); complete uses max distance (compact, outlier-sensitive); average is balanced; single chains (almost never what genomics wants).

The biological story changes depending on these choices. A "module" identified with `complete` linkage on Euclidean distance of raw counts is *not the same module* identified with `ward.D2` on correlation distance of z-scored data. Both can be defensible; neither is automatic. **Pick deliberately, document, and verify the clustering against orthogonal evidence before claiming the modules are biological.**

## The ward.D vs ward.D2 Trap (Murtagh-Legendre 2014)

R `stats::hclust` exposes two methods both labeled "Ward": `ward.D` and `ward.D2`. They produce *different* dendrograms on the same data. Only `ward.D2` (squared distances input) implements Ward's actual minimum-variance criterion (Murtagh & Legendre 2014 *J Classif* 31:274). `ward.D` is a historical implementation that does not.

```r
hclust(dist(x), method = 'ward.D')   # NOT Ward's criterion -- legacy
hclust(dist(x), method = 'ward.D2')  # Ward's actual minimum-variance criterion
```

`pheatmap::pheatmap(clustering_method='ward.D2')` and `ComplexHeatmap::Heatmap(clustering_method_rows='ward.D2')` both pass through to `hclust`. Always specify `ward.D2` unless reproducing a paper that used the unlabeled `ward` (which actually called `ward.D` pre-R 3.1).

## Decision Tree by Scenario

| Scenario | Scaling | Distance | Linkage | Why |
|----------|---------|----------|---------|-----|
| Bulk RNA-seq, expression patterns across samples | row z-score | euclidean | ward.D2 | Standard; z-score removes absolute level so co-regulated genes cluster regardless of magnitude |
| Methylation beta values (already bounded [0,1]) | raw (no scale) | euclidean or manhattan | ward.D2 | Beta values are interpretable on absolute scale; scaling would distort |
| Co-expression module discovery | row z-score | correlation (`1 - cor`) | average | WGCNA convention; preserves co-regulation pattern |
| ChIP/ATAC peak intensity across samples | raw log-counts | euclidean | ward.D2 | Peaks are interpretable on absolute scale after log |
| Sample QC (correlation of samples) | column-wise raw | correlation | ward.D2 | The correlation IS the data; don't scale before computing it |
| Methylation array with outliers | raw + clip 1-99% | euclidean | ward.D2 | Outliers dominate Euclidean; robust clip preserves signal |
| Single-cell pseudobulk by cell type | row z-score | euclidean | ward.D2 | Same as bulk; downsample to <500 cells per type for rendering |
| Mutation matrix (binary present/absent) | raw | binary (jaccard) | average or complete | Standard distance for binary data; ward inappropriate |
| Drug response across cell lines | row z-score | spearman correlation | ward.D2 | Drug-rank patterns matter more than absolute IC50 |

## Color Mapping -- The Quietly Most-Important Choice

A heatmap is a color encoding of a matrix. The default linear mapping from data to color is rarely correct:

1. **Diverging data needs symmetric bounds.** For z-scores or log-fold changes, the color bar must be symmetric around zero. `colorRamp2(c(-2, 0, 2), c('#0072B2', 'white', '#D55E00'))` ALWAYS, not `colorRamp2(c(min, mean, max), ...)`.

2. **Robust quantile bounds.** Single outliers compress the entire color scale. Clip at 1st/99th percentile before mapping: `bounds <- quantile(mat, c(0.01, 0.99))`. ComplexHeatmap's `colorRamp2(c(bounds[1], 0, bounds[2]), ...)` is standard. Without this, one outlier sample turns the entire heatmap pale.

3. **Sequential data uses a perceptually-uniform colormap.** viridis, magma, cividis (Nuñez 2018), or batlow (Crameri 2020). NOT jet, NOT rainbow, NOT `colorRampPalette(c('blue','red'))(100)` which has a non-monotonic luminance.

4. **Diverging palettes from Crameri** (`vik`, `roma`) or ColorBrewer (`RdBu`, `BrBG`) are perceptually uniform. Reverse the default direction for log-fold-change (negative = blue, positive = red, by biological convention).

## Optimal Leaf Ordering (Bar-Joseph 2001)

A dendrogram for n leaves has 2^(n-1) consistent linear orderings — only one is the leaf order shown. Default `hclust` gives a deterministic but visually arbitrary ordering. **Optimal Leaf Ordering (OLO)** chooses the consistent ordering that minimizes the sum of distances between adjacent leaves — making visually adjacent rows actually similar, and revealing block structure in the heatmap that the default ordering hides.

```r
library(ComplexHeatmap)
library(seriation)

# OLO via seriation
dist_rows <- dist(mat)
hc_rows <- hclust(dist_rows, method = 'ward.D2')
olo_rows <- seriate(dist_rows, method = 'OLO', control = list(hclust = hc_rows))

Heatmap(mat,
        cluster_rows = as.dendrogram(olo_rows[[1]]),
        cluster_columns = TRUE,
        clustering_method_columns = 'ward.D2')
```

For matrices >2000 rows OLO becomes slow (O(n^4) in worst case; modern implementations are much faster). The trade-off is worth it for publication figures.

## Annotation Tracks -- ComplexHeatmap as the Reference

**Goal:** Render an annotated heatmap with column metadata (condition, batch, age), row metadata (pathway, gene class), and split panels for grouped display.

**Approach:** Define `HeatmapAnnotation` (column) and `rowAnnotation` objects with explicit color lists; render with `Heatmap()` specifying `row_split`/`column_split` for grouped layout; use `draw()` to commit, not bare `Heatmap()`, when running non-interactively.

```r
library(ComplexHeatmap)
library(circlize)

# Robust symmetric color mapping
bounds <- quantile(abs(mat[!is.na(mat)]), 0.99)
col_fun <- colorRamp2(c(-bounds, 0, bounds), c('#0072B2', 'white', '#D55E00'))

# Column metadata
ha_col <- HeatmapAnnotation(
    Condition = metadata$condition,
    Batch     = metadata$batch,
    Age       = anno_barplot(metadata$age),
    col = list(
        Condition = c(Control = '#56B4E9', Treatment = '#D55E00'),
        Batch     = c(A = '#009E73', B = '#0072B2', C = '#CC79A7')
    ),
    annotation_name_gp = gpar(fontsize = 8)
)

# Row metadata
ha_row <- rowAnnotation(
    Pathway = gene_info$pathway,
    LogFC   = anno_barplot(gene_info$log2FC, baseline = 0,
                            gp = gpar(fill = ifelse(gene_info$log2FC > 0,
                                                     '#D55E00', '#0072B2'))),
    col = list(Pathway = c(Metabolism = '#8491B4', Signaling = '#91D1C2'))
)

ht <- Heatmap(mat,
              name = 'Z-score',
              col  = col_fun,
              top_annotation  = ha_col,
              left_annotation = ha_row,
              row_split    = gene_info$pathway,
              column_split = metadata$condition,
              clustering_method_rows    = 'ward.D2',
              clustering_method_columns = 'ward.D2',
              clustering_distance_rows    = 'euclidean',
              clustering_distance_columns = 'euclidean',
              show_row_names = FALSE,
              use_raster = TRUE)          # rasterize cell layer for >2000 rows

draw(ht, merge_legends = TRUE)            # draw() not bare Heatmap()
```

### The `draw()` requirement (silent failure)

A bare `Heatmap(mat)` works at the R console because auto-print invokes `draw()`. **Inside `for`, `lapply`, `function`, Quarto/Rmd chunks, or `Rscript`, a bare `Heatmap()` produces no output and no error.** Always wrap in `draw()` non-interactively. Only `draw()` exposes `merge_legends`, `heatmap_legend_side`, `ht_gap`, and `padding`.

## seaborn.clustermap (Python)

```python
import seaborn as sns
import numpy as np
import pandas as pd

# Robust symmetric bounds (1-99% quantile)
vmax = np.quantile(np.abs(df.values[~np.isnan(df.values)]), 0.99)

# col_colors / row_colors for categorical annotations
condition_colors = metadata['condition'].map({'Control': '#56B4E9', 'Treatment': '#D55E00'})
batch_colors = metadata['batch'].map({'A': '#009E73', 'B': '#0072B2', 'C': '#CC79A7'})
col_colors = pd.DataFrame({'Condition': condition_colors, 'Batch': batch_colors})

g = sns.clustermap(df,
                   cmap='RdBu_r', center=0, vmin=-vmax, vmax=vmax,
                   row_cluster=True, col_cluster=True,
                   method='ward',                      # seaborn uses scipy ward, equivalent to R ward.D2
                   metric='euclidean',
                   z_score=0,                          # 0 = rows, 1 = columns
                   col_colors=col_colors,
                   dendrogram_ratio=0.15,
                   cbar_pos=(0.02, 0.8, 0.03, 0.15),
                   figsize=(10, 12),
                   rasterized=True)                    # rasterize the cell layer
```

**`standard_scale` vs `z_score` confusion:**
- `z_score=0` standardizes ROWS to mean 0, SD 1 (most common request)
- `z_score=1` standardizes COLUMNS to mean 0, SD 1
- `standard_scale=0` rescales ROWS to [0, 1] via `(x − min) / (max − min)` — NOT z-scoring, compresses outliers nonlinearly
- The two are mutually exclusive — passing both errors

A heatmap published with `standard_scale` looks like a z-scored heatmap but the color encoding is not interpretable as standard deviations.

## OncoPrint -- The Specialized Mutation-Matrix Heatmap

OncoPrint (Cerami 2012 *Cancer Discov* 2:401; canonical at cBioPortal) is a stylized heatmap for mutation matrices where each cell encodes multiple alteration types via overlapping rectangles. Different from generic heatmaps — see `data-visualization/oncoprint-mutation-matrices` for the dedicated skill. Mentioned here only to note that `ComplexHeatmap::oncoPrint()` is the R implementation and inherits all the cluster/annotation machinery of `Heatmap()`.

## Per-Method Failure Modes

### ward.D used when ward.D2 was intended

**Trigger:** `clustering_method = 'ward'` or `'ward.D'` (with or without the .D).

**Mechanism:** R `hclust` `ward.D` is a legacy implementation that does NOT use squared distances — it does not implement Ward's minimum-variance criterion (Murtagh-Legendre 2014).

**Symptom:** Different dendrogram than published papers that say "Ward"; clusters look subtly different; reproducibility issues across R versions.

**Fix:** Always specify `ward.D2` explicitly. For pheatmap and ComplexHeatmap, pass `clustering_method_rows = 'ward.D2'` and `clustering_method_columns = 'ward.D2'`.

### One outlier compresses the color scale

**Trigger:** Plotting matrix without quantile clipping; one extreme value dominates the color range.

**Mechanism:** Default `colorRamp2(c(min(mat), 0, max(mat)), ...)` is dominated by the outlier — the rest of the matrix renders within a narrow band of pale colors.

**Symptom:** Heatmap looks "washed out" except for one cell or one column; biological pattern invisible.

**Fix:** `bounds <- quantile(abs(mat), 0.99); col_fun <- colorRamp2(c(-bounds, 0, bounds), c('#0072B2', 'white', '#D55E00'))`. ComplexHeatmap's `colorRamp2` does NOT clip values exceeding the range — they render at the extreme color, which is the intended behavior.

### ComplexHeatmap silently produces no output in a script

**Trigger:** Bare `Heatmap(mat)` inside a `for` loop, `lapply`, `function()`, Quarto/Rmd code chunk, or `Rscript` invocation.

**Mechanism:** Auto-print only happens at the top-level R prompt; in non-interactive contexts the Heatmap object is created but never rendered.

**Symptom:** No error, no warning, no PDF output. Looks like the script ran successfully.

**Fix:** Always wrap in `draw()`: `pdf('out.pdf', ...); draw(Heatmap(mat, ...)); dev.off()`. Use the `draw()` call to set legend layout: `draw(ht, merge_legends = TRUE, heatmap_legend_side = 'right')`.

### Clustering applied to ordered conditions

**Trigger:** `cluster_columns = TRUE` when columns are an ordered sequence (time points, dose levels, treatment stages).

**Mechanism:** Hierarchical clustering re-orders columns to maximize within-cluster similarity, destroying the time/dose axis.

**Symptom:** Time-course heatmap with time points scrambled; reader cannot follow temporal pattern.

**Fix:** `cluster_columns = FALSE` for ordered conditions. To group while preserving order, use `column_split` or `column_order` explicitly.

### Z-score on a sparse matrix

**Trigger:** Row z-scoring a matrix with many zero values (e.g., single-cell expression, sparse peak counts).

**Mechanism:** `(x − mean) / sd` is ill-defined when a row is mostly zeros — sd is dominated by the few non-zero values; z-scores explode for the non-zero entries.

**Symptom:** A few cells render as extreme colors; most cells are washed-out near-zero.

**Fix:** For single-cell, work with cluster-summarized pseudobulk matrices, not raw single-cell expression. For sparse peak data, filter rows by minimum non-zero count before scaling.

### Correlation distance applied to data with batch effect

**Trigger:** `clustering_distance_rows = 'correlation'` on a matrix where samples have a strong batch effect.

**Mechanism:** Correlation preserves co-regulation pattern but is sensitive to global structure. If batch shifts ALL genes up in one batch, correlation distance reads this as "co-regulation."

**Symptom:** Modules cluster by batch, not by biology.

**Fix:** Batch-correct (limma::removeBatchEffect or ComBat) before clustering. Confirm with PCA that batch is no longer the dominant axis.

### pheatmap's `gaps_col` interacts with `cluster_cols`

**Trigger:** Setting `gaps_col = c(5, 10)` with `cluster_cols = TRUE`.

**Mechanism:** When `cluster_cols = TRUE`, `gaps_col` is silently ignored; the dendrogram-determined order has no concept of position.

**Symptom:** No gaps appear; no warning.

**Fix:** To use `gaps_col`, set `cluster_cols = FALSE` and pre-arrange the columns explicitly. Or in ComplexHeatmap use `column_split` to combine clustering AND visual gaps.

### Raster rendering at low DPI looks pixelated

**Trigger:** `use_raster = TRUE` (default for large heatmaps in ComplexHeatmap) with default `raster_quality = 1`.

**Mechanism:** Default raster quality is set for screen rendering; the bitmap is upscaled for PDF output, producing blocky cells.

**Symptom:** Heatmap cells look pixelated at print zoom; diagonal "stair-stepping" on cell boundaries.

**Fix:** `Heatmap(..., use_raster = TRUE, raster_quality = 5)` increases the raster resolution. Set `raster_device = 'CairoPNG'` for transparency support.

## Reconciliation: When Methods Disagree

| Pattern | Likely cause | Action |
|---------|--------------|--------|
| ComplexHeatmap and pheatmap give different dendrograms | pheatmap uses `dist()` with default `method = 'euclidean'`; ComplexHeatmap defaults to the same but different clustering distance defaults | Verify both with `clustering_distance_rows = 'euclidean'`, `clustering_method_rows = 'ward.D2'` explicitly |
| Same code, different dendrogram across R versions | R 3.1 renamed `'ward'` to `'ward.D'` and added `'ward.D2'` | Always specify `ward.D2` explicitly; never `'ward'` |
| Z-scored heatmap with extreme colors only in a few cells | Sparse matrix with zero-inflation | Filter low-expression rows; OR shift to robust scaling (`(x - median) / mad`) |
| Modules cluster by batch | Correlation distance picked up batch effect | Batch-correct upstream; verify via PCA |
| seaborn clustermap produces different clusters than R | seaborn `method='ward'` calls scipy.cluster.hierarchy.linkage which IS ward.D2-equivalent; difference is usually `metric` default | Set `metric='euclidean'` explicitly in both |
| OncoPrint mutual-exclusivity panel appears empty | `column_order` is being computed by clustering instead of preserved | Pass `column_order = ...` explicitly to oncoPrint |

**Operational rule:** a clustered heatmap is reproducible only when scaling, distance, linkage, color bounds, and (for OLO) the seriation method are all explicitly stated. Defaults differ across packages and across versions of the same package.

## Quantitative Thresholds

| Threshold | Value | Source |
|-----------|-------|--------|
| Robust color bound | 1st-99th percentile of |matrix| | Standard publication practice; suppresses single-outlier dominance |
| Raster trigger | >2000 rows or >2000 columns | ComplexHeatmap default `use_raster = TRUE` above 2000 |
| OLO practical limit | ~5000 rows | O(n^4) worst case; modern Bar-Joseph implementations faster |
| z-score symmetry | bounds around 0 | Z-scores are symmetric by construction |
| Minimum non-zero count to z-score | >=3 non-zero values per row | Below this sd is unreliable |
| Single-cell pseudobulk threshold | Downsample to <500 cells/group | Otherwise PDF rendering hangs |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| No PDF output from a script | Bare `Heatmap()` without `draw()` | Wrap in `draw()`; use `pdf()` / `dev.off()` explicitly |
| Color scale washed out | One outlier dominates | Clip to 1st-99th percentile; symmetric bounds for diverging |
| Time-course columns scrambled | `cluster_columns = TRUE` on ordered data | `cluster_columns = FALSE`; use `column_split` |
| pheatmap `gaps_col` ignored | Conflict with `cluster_cols = TRUE` | Disable clustering OR switch to ComplexHeatmap split |
| Dendrogram differs from a paper | Default `clustering_method` mismatch | Always specify `ward.D2`; never `ward` |
| seaborn standard_scale interpreted as z-score | Different rescaling functions | Use `z_score=0` for row z-scoring; `standard_scale` is min-max not z |
| Heatmap renders pixelated | Default raster_quality = 1 | Set `raster_quality = 5` for publication |
| Z-score blows up for some rows | Sparse rows; near-zero sd | Filter low-expression rows OR robust scale |
| Modules cluster by batch not biology | Batch effect not removed | limma::removeBatchEffect or ComBat upstream |

## Anticipated Reviewer Pushback

| Pushback | Standard response |
|----------|-------------------|
| "Which clustering method?" | Explicit ward.D2 (Murtagh-Legendre 2014) on row-z-scored Euclidean distance. Alternatives evaluated in supplementary |
| "How were leaves ordered?" | Optimal Leaf Ordering via seriation::seriate (Bar-Joseph 2001); reduces visually-adjacent dissimilarity |
| "Why this color scale?" | Diverging palette symmetric around zero, bounds = 1st-99th percentile of |z|. Robust to outliers per standard practice |
| "Why z-score?" | Removes absolute level so co-regulated genes cluster regardless of magnitude. Raw values clustered separately (supplementary) |
| "Why row split by pathway?" | Pre-specified gene-set annotation (KEGG/Reactome) to verify clustering recovers known biology, not to bias it |
| "Reproducibility across R versions?" | `ward.D2` is stable across R 3.1+; `clustering_method = 'ward'` is not — never used |

## References

- Bar-Joseph Z, Gifford DK, Jaakkola TS. 2001. Fast optimal leaf ordering for hierarchical clustering. *Bioinformatics* 17(suppl 1):S22-S29. doi:10.1093/bioinformatics/17.suppl_1.S22
- Cerami E, Gao J, Dogrusoz U, et al. 2012. The cBio cancer genomics portal: an open platform for exploring multidimensional cancer genomics data. *Cancer Discov* 2(5):401-404.
- Crameri F, Shephard GE, Heron PJ. 2020. The misuse of colour in science communication. *Nat Commun* 11:5444.
- Gehlenborg N, Wong B. 2012. Points of view: Heat maps. *Nat Methods* 9(3):213.
- Gehlenborg N, Wong B. 2012. Points of view: Mapping quantitative data to color. *Nat Methods* 9(8):769.
- Gu Z, Eils R, Schlesner M. 2016. Complex heatmaps reveal patterns and correlations in multidimensional genomic data. *Bioinformatics* 32(18):2847-2849.
- Murtagh F, Legendre P. 2014. Ward's hierarchical agglomerative clustering method: which algorithms implement Ward's criterion? *J Classif* 31(3):274-295.
- Nuñez JR, Anderton CR, Renslow RS. 2018. Optimizing colormaps with consideration for color vision deficiency to enable accurate interpretation of scientific data. *PLOS ONE* 13(7):e0199239.

## Related Skills

- data-visualization/color-palettes - Sequential and diverging colormap selection
- data-visualization/oncoprint-mutation-matrices - Mutation-matrix heatmap (ComplexHeatmap oncoPrint)
- data-visualization/multipanel-figures - Combine heatmaps into journal layouts
- data-visualization/dimensionality-reduction-plots - PCA / UMAP as alternative views of the same matrix
- differential-expression/de-visualization - Heatmap of top DE genes
- single-cell/markers-annotation - Single-cell dotplot / matrixplot as scRNA alternatives
<!-- END FILE: data-visualization/heatmaps-clustering/SKILL.md -->

## 子目录：data-visualization/interactive-visualization

<!-- BEGIN FILE: data-visualization/interactive-visualization/SKILL.md -->
---
name: bio-data-visualization-interactive-visualization
description: Build interactive HTML/web visualizations with plotly (Python/R), bokeh (Python), and gganimate/plotly frames for animation, with awareness of current Kaleido static-export model (post-orca-EOL), HTML file-size bloat, and the limits of interactive-only output for journal submission. Use when producing zoomable/hoverable plots for notebook EDA, supplementary HTML, dashboards, or animated time-course / iteration visualizations.
tool_type: mixed
primary_tool: plotly
---

## Version Compatibility

Reference examples tested with: plotly 5.24+, plotly R 4.10+, bokeh 3.4+, kaleido 1.0+ (note: v1 dropped bundled Chrome), gganimate 1.0.9+, altair 5.4+, htmlwidgets 1.6+.

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)`
- R: `packageVersion('<pkg>')` then `?function_name`

If code throws ImportError, AttributeError, or TypeError, introspect the installed package and adapt the example to match the actual API rather than retrying.

# Interactive Visualization

**"Build an interactive plot"** -> Render a zoomable, hoverable, panable HTML/web visualization, knowing that interactive output is a SUPPLEMENT to (not replacement for) the static figure needed for journal submission. Choose plotly for fastest onboarding and ggplot2 conversion (`ggplotly`); bokeh for streaming/server-side; altair for grammar-of-graphics; D3.js for full custom.

- Python: `plotly.graph_objects`, `plotly.express`, `bokeh`, `altair`
- R: `plotly` (via `ggplotly`), `htmlwidgets` ecosystem (leaflet, networkD3, DT)

## The Single Most Important Modern Insight -- Kaleido v1 and the Static-Export Pipeline

Interactive plots produce HTML, but journals need static PDF/PNG. The plotly static-export pipeline changed materially in 2025:

- **Orca is end-of-life** (deprecated 2021, removed pipeline 2025)
- **`fig.write_image(..., engine='orca')` removed in plotly 6.2** (post-Sept 2025)
- **Kaleido v1+ is the current standard** — pass no `engine=` argument
- **Kaleido v1 dropped bundled Chrome** — requires installed Chrome / Chromium
- **EPS export removed in Kaleido v1** (was supported via orca's bundled Chromium)

For static export of plotly figures in 2026: `pip install kaleido`; verify Chrome installed; `fig.write_image('out.pdf')`. Test by writing to a known path and inspecting file size; silent failure on missing Chrome was a 2024-2025 pain point that v1 partially addresses with clearer errors.

## Interactive vs Static — The Reproducibility Cost

Interactive HTML has hidden trade-offs:

- **File size**: a 5000-point plotly HTML is 3-5 MB (embedded JS bundle). 50000 points crashes browsers without WebGL acceleration.
- **Non-citable**: a paper figure must be static. Always export static alongside.
- **Browser version drift**: HTML from 2020 plotly may not render in 2026 browsers.
- **Cannot be alt-text described**: accessibility weaker than static.

Use interactive for notebooks (exploration), supplementary HTML (online journal supplement), dashboards (Streamlit/Dash/Shiny). For the journal figure, always also produce static.

## plotly (Python) — Standard Interactive

**Goal:** Build an interactive HTML plot with zoom, pan, and hover-tooltip behavior; export both interactive HTML for supplements and static PDF for the journal figure.

**Approach:** Use `plotly.express` for declarative high-level plots OR `graph_objects` for fine control; enable WebGL via `render_mode='webgl'` or `Scattergl` for >5000 points; export HTML with `write_html()` and static with `write_image()` after installing Kaleido v1+ and Chrome.

```python
import plotly.express as px
import plotly.graph_objects as go

# Express: high-level, declarative
fig = px.scatter(df, x='PC1', y='PC2', color='cluster',
                  hover_data=['gene_count', 'sample_id'],
                  color_discrete_sequence=['#0072B2', '#D55E00', '#009E73'],
                  title='PCA')
fig.update_layout(template='plotly_white', width=600, height=500)

# WebGL acceleration for >5000 points
fig = px.scatter(df, x='PC1', y='PC2', color='cluster', render_mode='webgl')

# Save
fig.write_html('pca.html')
fig.write_image('pca.pdf')                   # requires kaleido + Chrome

# Graph_objects: low-level
fig = go.Figure(go.Scattergl(                 # Scattergl == WebGL scatter
    x=df['PC1'], y=df['PC2'],
    mode='markers',
    marker=dict(color=df['cluster_code'], colorscale='Tab10', size=4),
    text=df['sample_id'], hoverinfo='text'))
```

## plotly (R) — ggplotly Conversion

```r
library(plotly)
library(ggplot2)

p <- ggplot(df, aes(x = PC1, y = PC2, color = cluster, text = sample_id)) +
    geom_point() + theme_classic()

# Convert ggplot to interactive plotly
p_int <- ggplotly(p, tooltip = c('text', 'x', 'y', 'colour'))

# Save
htmlwidgets::saveWidget(p_int, 'pca.html', selfcontained = TRUE)
```

ggplotly is the lowest-friction R interactive path — write ggplot, get plotly.

## bokeh (Python) — Server-Side / Streaming

```python
from bokeh.plotting import figure, output_file, save
from bokeh.models import ColumnDataSource, HoverTool

output_file('pca_bokeh.html')

source = ColumnDataSource(df)
p = figure(title='PCA', x_axis_label='PC1', y_axis_label='PC2',
           tools='pan,wheel_zoom,box_zoom,reset,hover,save')
p.scatter('PC1', 'PC2', source=source, size=8, alpha=0.7,
          color={'field': 'cluster', 'transform': cluster_cmap})
p.add_tools(HoverTool(tooltips=[('Sample', '@sample_id'), ('Cluster', '@cluster')]))
save(p)
```

bokeh is stronger than plotly for streaming dashboards and server-side aggregation. Static export via `bokeh.io.export_png` requires selenium + Chrome.

## Animation — gganimate (R) and plotly frames (Python)

```r
library(gganimate)
p <- ggplot(df, aes(x, y, color = condition)) +
    geom_point(size = 3) +
    theme_classic() +
    transition_time(time) +                  # animate over time
    labs(title = 'Time: {frame_time}')

anim <- animate(p, nframes = 100, fps = 20, width = 600, height = 400,
                 renderer = gifski_renderer())
anim_save('time_course.gif', anim)
```

```python
import plotly.express as px
fig = px.scatter(df, x='x', y='y', color='condition',
                  animation_frame='time',
                  animation_group='entity_id',
                  range_x=[xmin, xmax], range_y=[ymin, ymax])
fig.write_html('time_course.html')
```

Animation suits time-course data, iterative algorithm visualization, before-after comparisons. Limit to ≤100 frames; longer animations bloat file size and tax viewer attention.

## htmlwidgets Ecosystem (R)

```r
library(DT)                                 # interactive tables
datatable(df, filter = 'top', extensions = 'Buttons',
          options = list(dom = 'Bfrtip', buttons = c('csv', 'excel')))

library(leaflet)                            # interactive maps
leaflet(spatial_df) %>% addTiles() %>% addCircles()

library(networkD3)                          # interactive networks
sankeyNetwork(...) %>% saveWidget('sankey.html')
```

htmlwidgets is the R answer to plotly's JavaScript wrapping — many specialized packages for tables, maps, networks, all producing standalone HTML.

## Per-Method Failure Modes

### plotly static export silently fails

**Trigger:** `fig.write_image('out.pdf')` without kaleido installed.

**Mechanism:** plotly previously fell back to orca (now removed); current versions raise ValueError but older versions silently skipped.

**Symptom:** No file written; OR file written with default settings.

**Fix:** `pip install kaleido`; verify Chrome is installed (kaleido v1+ requires it); test with `fig.write_image('test.pdf')` after install.

### orca dependency in older code

**Trigger:** Following 2020-2022 plotly tutorials with `engine='orca'`.

**Mechanism:** orca is EOL; `engine=` parameter deprecated in plotly 6.2 (post-Sep 2025).

**Symptom:** ValueError or DeprecationWarning.

**Fix:** Remove `engine=` argument; use Kaleido v1 (default).

### EPS export needed but Kaleido v1 dropped it

**Trigger:** Journal requires EPS; Kaleido v1 only supports PDF/PNG/SVG/JPG/WebP.

**Mechanism:** Bundled Chromium in v0 supported EPS; v1 unbundled and dropped it.

**Symptom:** kaleido error on EPS export.

**Fix:** Export PDF, then convert via `pdf2ps` (ghostscript). For complex figures may produce raster EPS — verify acceptability with journal.

### HTML file > 10 MB

**Trigger:** Plotly scatter of 50000 points exported as HTML.

**Mechanism:** Each point + hover data embedded; JS bundle ~3 MB; data scales linearly.

**Symptom:** Browser hangs opening; reviewer's network throttles upload.

**Fix:** Use Scattergl (WebGL); OR Datashader pre-aggregation; OR ship static + small HTML supplement.

### gganimate slow on large frames

**Trigger:** `transition_time` with 100+ frames and 10000+ points per frame.

**Mechanism:** Each frame rendered independently.

**Symptom:** Animation takes hours.

**Fix:** Downsample frames; pre-aggregate per-frame data; OR use plotly animation (in-browser interpolation faster).

### Interactive plot shown as figure in paper

**Trigger:** Manuscript references interactive HTML as Figure 2.

**Mechanism:** Journals require static; interactive HTML is supplement.

**Symptom:** Submission requires figure resubmission as static.

**Fix:** Always produce both static (figure) + interactive (supplement) versions.

## Reconciliation

| Pattern | Cause | Action |
|---------|-------|--------|
| Kaleido / orca confusion in plotly | Pipeline changed 2024-2025 | Use Kaleido v1+; no `engine=` |
| ggplotly drops some custom theme | Conversion loses non-translatable ggplot elements | Manually re-add via `plotly::layout()` |
| bokeh static export fails | selenium not installed | `pip install selenium`; Chrome required |
| htmlwidgets self-contained doesn't work offline | CDN-linked resources by default | `saveWidget(..., selfcontained = TRUE)` |

## Quantitative Thresholds

| Threshold | Value | Source |
|-----------|-------|--------|
| HTML file size warning | >10 MB | Practical |
| Scattergl trigger | >5000 points | plotly performance |
| Animation max frames | ~100 | Viewer attention + file size |
| Selfcontained HTML on | always for portability | htmlwidgets best practice |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| Static export silent failure | kaleido / Chrome missing | Install both |
| HTML bloated | Large N points | Scattergl or Datashader |
| orca DeprecationWarning | Following old tutorial | Remove engine=, use Kaleido v1 |
| EPS export fails | Kaleido v1 dropped EPS | PDF + pdf2ps |
| ggplotly tooltips show wrong fields | Default `tooltip` argument | Specify `tooltip = c(...)` |
| Animation file too large | Too many frames | Downsample / pre-aggregate |
| Interactive cited as paper figure | Journal requires static | Produce both |

## References

- Sievert C. 2020. *Interactive Web-Based Data Visualization with R, plotly, and shiny.* Chapman and Hall/CRC.
- Plotly Python — Static Image Generation Changes (2024-2025). https://plotly.com/python/static-image-generation-changes/
- Bostock M, Ogievetsky V, Heer J. 2011. D³ Data-Driven Documents. *IEEE TVCG* 17(12):2301-2309.
- Wickham H, Pedersen TL, Seidel D. 2022. gganimate (CRAN). https://gganimate.com

## Related Skills

- reporting/quarto-reports - Embed interactive HTML in scientific reports
- reporting/rmarkdown-reports - htmlwidgets in Rmd
- data-visualization/ggplot2-fundamentals - ggplot input for ggplotly
- data-visualization/dimensionality-reduction-plots - Interactive UMAP/PCA exploration
- data-visualization/network-visualization - PyVis interactive networks
<!-- END FILE: data-visualization/interactive-visualization/SKILL.md -->

## 子目录：data-visualization/lollipop-protein-maps

<!-- BEGIN FILE: data-visualization/lollipop-protein-maps/SKILL.md -->
---
name: bio-data-visualization-lollipop-protein-maps
description: Plot per-gene mutation distributions on a protein-domain map (lollipop / needle plots) showing mutation position, recurrence count, and variant classification with maftools, g3-lollipop, trackViewer, and ProteinPaint. Use when visualizing recurrent mutation hotspots on a single gene's protein, marking domain boundaries from UniProt/Pfam, comparing missense vs truncating distributions, or contrasting two cohorts on the same lollipop.
tool_type: mixed
primary_tool: maftools
---

## Version Compatibility

Reference examples tested with: maftools 2.18+, trackViewer 1.38+, g3-lollipop (JavaScript via R `g3viz` 1.2+), Bio.PDB 1.83+ (for domain coordinates). ProteinPaint is a hosted service.

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('<pkg>')` then `?function_name`
- Python: `pip show <package>` then `help(module.function)`

If code throws ImportError, AttributeError, or TypeError, introspect the installed package and adapt the example to match the actual API rather than retrying.

# Lollipop / Needle Protein Maps

**"Plot mutations on a gene's protein"** -> Render a horizontal protein backbone with colored domain rectangles (from UniProt/Pfam/InterPro), then stack vertical lines ("stems") at mutated amino-acid positions, capped with circles ("lollipops") whose size reflects mutation count and whose color encodes variant class. The biological story is hotspot identification — a tall stack of recurrences at a single residue (e.g., KRAS G12, PIK3CA E545/H1047) is the visual signature of a driver mutation.

- R: `maftools::lollipopPlot`, `trackViewer::lolliplot`, `g3viz::g3Lollipop`
- Python: `pyLollipop` (limited maintenance); ProteinPaint via API
- Web: cBioPortal, ProteinPaint, MutationMapper

## The Single Most Important Modern Insight -- Hotspot Recurrence Drives the Plot

A lollipop plot exists to identify hotspots — residues with disproportionate recurrence. The MutSig hotspot test (Lawrence 2014 *Nature* 505:495) and statisticalhotspot methods (Chang 2016 *Nat Biotechnol* 34:155) formalize this: a residue's mutation count should exceed the gene-wide background rate × residue count. Visualizing this on a domain map IS the diagnostic.

Key practical consequences:
- **Stack height ≠ frequency**: a tall lollipop at residue 600 means recurrence, not population frequency. Annotate the count.
- **Domain colors should encode functional class** (kinase, SH2, binding), not random hue.
- **Mark known activating/inactivating residues** (G12 for KRAS, R175 for TP53) with bold labels.

## Decision Tree by Question

| Question | Approach |
|----------|----------|
| Where are the hotspots? | Lollipop with size = count; label top 5 recurrent residues |
| Missense vs truncating distribution? | Color stems by class; tumor suppressors show truncating spread; oncogenes show missense hotspots |
| Compare two cohorts | Stacked lollipops (one cohort up, one down) on shared domain map |
| 3D-cluster hotspot detection? | Use HotMAPS / 3D Hotspots — beyond linear lollipop |
| Druggable position? | Add ClinVar / OncoKB level annotation at the residue |

## maftools::lollipopPlot

**Goal:** Render per-gene mutation distribution on Pfam domain map with count-sized lollipops and class-colored stems.

**Approach:** Pass MAF and gene to `lollipopPlot`; maftools queries Pfam for domain coordinates automatically; outputs ggplot2 object.

```r
library(maftools)
maf <- read.maf(maf = 'cohort.maf')

# Default lollipop
lollipopPlot(maf = maf, gene = 'TP53',
             AACol = 'HGVSp_Short',
             labelPos = c(175, 248, 273),                   # mark canonical hotspots
             labPosSize = 1.0,
             showMutationRate = TRUE,
             domainLabelSize = 1,
             printCount = TRUE,
             colors = c(Missense_Mutation = '#D55E00',
                        Nonsense_Mutation = '#000000',
                        Frame_Shift_Del   = '#0072B2',
                        Frame_Shift_Ins   = '#56B4E9',
                        Splice_Site       = '#CC79A7',
                        In_Frame_Del      = '#009E73'))
```

```r
# Compare two cohorts -- one up, one down
lollipopPlot2(m1 = cohort_a, m2 = cohort_b,
              gene = 'TP53',
              m1_name = 'Cohort A',
              m2_name = 'Cohort B',
              AACol1 = 'HGVSp_Short', AACol2 = 'HGVSp_Short',
              colors = my_palette)
```

## trackViewer::lolliplot -- Fine Control over Track Layout

```r
library(trackViewer)
library(GenomicRanges)

# Build SNP (lollipop) and feature (domain) GRanges
snps <- GRanges('chr17', IRanges(c(175, 248, 273), width = 1, names = c('R175H', 'R248Q', 'R273H')),
                color = c('#D55E00', '#D55E00', '#D55E00'),
                score = c(45, 38, 29))                       # mutation count
features <- GRanges('chr17',
                    IRanges(c(102, 323, 363), width = c(190, 30, 30),
                            names = c('DNA-binding', 'Tetramerization', 'Regulatory')),
                    fill = c('#0072B2', '#009E73', '#CC79A7'),
                    height = 0.04)

lolliplot(snps, features, ylab = 'Mutation count',
          xaxis = TRUE, yaxis = TRUE)
```

trackViewer is more flexible than maftools for non-standard layouts (custom domain sources, multi-protein stacking, integration with genome coordinates).

## g3viz / g3-lollipop -- Interactive HTML

```r
library(g3viz)
mutation_data <- hgvspChange2protein(maf, gene = 'TP53')
g3Lollipop(mutation_data,
           gene.symbol = 'TP53',
           protein.change.col = 'AA_Change',
           plot.options = g3Lollipop.theme(theme.name = 'nature'),
           output.filename = 'TP53_lollipop.html')
```

g3-lollipop produces an interactive HTML — hover tooltips, click-to-filter, exportable. Suitable for supplementary HTML supplement; not for journal figure submission directly.

## Domain Annotation Sources

| Source | Format | Stability | Caveat |
|--------|--------|-----------|--------|
| Pfam (via maftools) | Pfam-A domain coordinates | Updated occasionally | maftools caches local; may lag Pfam release |
| UniProt | Domain + Region features (varied types) | Daily updates | API-driven; rate limits |
| InterPro | Integrated multi-database | More inclusive than Pfam | Different sub-classifications |
| Custom | Hand-curated for specific paper | Reproducible | Cite source |

For canonical isoform: maftools uses the canonical UniProt isoform by default. For specific isoform: pass `refSeqID` or `proteinID` explicitly. Mutations annotated against a different isoform will be off-by-residue.

## Per-Method Failure Modes

### Mutations not labeled with AA position

**Trigger:** MAF column `HGVSp_Short` missing or malformed.

**Mechanism:** maftools expects `HGVSp_Short` (e.g., 'p.R175H'); falls back to other columns inconsistently.

**Symptom:** "No mutations to plot" or wrong positions.

**Fix:** Verify `HGVSp_Short` column exists; reformat from HGVSp if needed. Use `AACol` argument to specify which column.

### Isoform mismatch

**Trigger:** Mutations called against ENST00000269305 but plotted against canonical ENST00000288602 (TP53).

**Mechanism:** Residue numbering differs across isoforms.

**Symptom:** Known R175H plotted at R177H or in a different domain.

**Fix:** Annotate the isoform in the figure caption; pass `proteinID` to `lollipopPlot` to force a specific isoform.

### Domain map outdated

**Trigger:** maftools' cached Pfam annotation is older than the protein's current Pfam release.

**Mechanism:** Domain coordinates can shift across Pfam versions.

**Symptom:** Domain boundaries off by a few residues; published-figure mismatch.

**Fix:** Pull domain coordinates from UniProt directly (current); pass via `trackViewer::lolliplot` features.

### Recurrence at low-coverage region overinterpreted

**Trigger:** "Hotspot" identified at a residue with high coverage variance — looks recurrent but is a sequencing artifact.

**Mechanism:** Capture-bait coverage variability; some residues sequenced more deeply.

**Symptom:** "Hotspot" in untargeted region; not validated in WGS.

**Fix:** Verify recurrence in independent cohort (TCGA Pan-Cancer + ICGC); use MutSig hotspot test (Lawrence 2014) for formal hotspot calling.

### Counts encoded only as size; no actual numbers shown

**Trigger:** Default `printCount = FALSE`.

**Mechanism:** Size-encoded counts beyond ~10 saturate visually.

**Symptom:** Reader cannot tell whether the top lollipop is 30 vs 300 mutations.

**Fix:** `printCount = TRUE` annotates each lollipop with its count.

### Domain colors random; no functional grouping

**Trigger:** Default rainbow domain colors.

**Mechanism:** Domains colored by accident, not by function class.

**Symptom:** Reader cannot quickly identify which domain is the kinase.

**Fix:** Manually map domain colors by functional class (kinase = blue, binding = green, regulatory = purple).

## Reconciliation: When Hotspots Disagree

| Pattern | Cause | Action |
|---------|-------|--------|
| Hotspot in cohort A absent in B | Cohort A enriched for a subtype OR small N | Stratify by subtype; cite both N |
| 3D hotspot test calls residues not on lollipop | Linear adjacency misses 3D proximity | Use HotMAPS / 3D Hotspots for spatial clusters |
| Recurrent residue lacks OncoKB evidence | Novel hotspot OR sequencing artifact | Confirm via independent cohort + WGS |
| Frame-shift indels not aligned to expected codon | Different annotation tool (VEP vs SnpEff) | Standardize annotation; verify HGVSp |

**Operational rule:** annotate the isoform; show absolute counts on lollipops; verify hotspots against TCGA Pan-Cancer + ICGC before novel-hotspot claims.

## Quantitative Thresholds

| Threshold | Value | Source |
|-----------|-------|--------|
| Hotspot recurrence cutoff | depends on gene length + cohort size | Lawrence 2014 — formal MutSig test |
| Display all mutations vs filter | Recurrent (count ≥ 2) for clarity; show all in supplement | Visualization practical |
| Domain source default | Pfam (maftools default); UniProt for current | Tool-specific |
| Cohort N for credible hotspot | ≥200 for a single gene; pan-cancer for novel | Standard practice |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| No mutations on plot | HGVSp_Short column missing | Verify / reformat from HGVSp |
| Mutations at wrong position | Isoform mismatch | Specify proteinID; document isoform |
| Domain boundaries slightly off | maftools Pfam cache outdated | Pull from UniProt; use trackViewer |
| Hotspot size saturates | Counts >10 indistinguishable by size | `printCount = TRUE` to annotate numbers |
| Random domain colors | Default rainbow | Manual mapping by functional class |
| Novel hotspot from one cohort | Insufficient N | Verify in TCGA + ICGC |

## References

- Chang MT, Asthana S, Gao SP, et al. 2016. Identifying recurrent mutations in cancer reveals widespread lineage diversity and mutational specificity. *Nat Biotechnol* 34(2):155-163.
- Gao J, Aksoy BA, Dogrusoz U, et al. 2013. Integrative analysis of complex cancer genomics and clinical profiles using the cBioPortal. *Sci Signal* 6(269):pl1.
- Lawrence MS, Stojanov P, Mermel CH, et al. 2014. Discovery and saturation analysis of cancer genes across 21 tumour types. *Nature* 505:495-501.
- Mayakonda A, Lin DC, Assenov Y, Plass C, Koeffler HP. 2018. Maftools: efficient and comprehensive analysis of somatic variants in cancer. *Genome Res* 28(11):1747-1756.
- Ou J, Zhu LJ. 2019. trackViewer: a Bioconductor package for interactive and integrative visualization of multi-omics data. *Nat Methods* 16:453-454.
- Zhou X, Edmonson MN, Wilkinson MR, et al. 2016. Exploring genomic alteration in pediatric cancer using ProteinPaint. *Nat Genet* 48(1):4-6.

## Related Skills

- data-visualization/oncoprint-mutation-matrices - Cohort-wide mutation matrix
- variant-calling/variant-annotation - Annotate HGVSp upstream
- clinical-databases/variant-prioritization - Filter variants before lollipop
- data-visualization/color-palettes - CVD-safe class palettes
- structural-biology/structure-navigation - 3D protein structure for hotspot interpretation
<!-- END FILE: data-visualization/lollipop-protein-maps/SKILL.md -->

## 子目录：data-visualization/manhattan-qq-locuszoom

<!-- BEGIN FILE: data-visualization/manhattan-qq-locuszoom/SKILL.md -->
---
name: bio-data-visualization-manhattan-qq-locuszoom
description: Build Manhattan, Miami, QQ, and locuszoom-style regional plots from GWAS, TWAS, PWAS, and QTL summary statistics with correct genomic-inflation diagnostics, multi-trait overlays, lead-SNP labeling, and LD-aware regional rendering. Use when visualizing association results across the genome, comparing two traits, computing genomic inflation lambda, or zooming into a locus with LD coloring.
tool_type: mixed
primary_tool: qqman
---

## Version Compatibility

Reference examples tested with: qqman 0.1.9 (R), CMplot 4.5+ (R), matplotlib 3.8+, pandas 2.2+, scipy 1.12+, plinkQC 0.3+. For locuszoom-style: locuszoomr 0.3+ (R) or pyranges + matplotlib.

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters

If code throws ImportError, AttributeError, or TypeError, introspect the installed package and adapt the example to match the actual API rather than retrying.

# Manhattan, QQ, and Locuszoom Plots

**"Plot my GWAS results"** -> Render per-variant -log10(p) across the genome (Manhattan), compare expected vs observed p quantiles (QQ + λGC), overlay two traits with mirrored axes (Miami), and zoom into a locus with LD-colored points + recombination rate + gene track (locuszoom). The choices that matter: significance thresholds, axis truncation for ultra-significant peaks, lead-SNP labeling, and LD reference selection for regional plots.

- R: `qqman::manhattan` / `qqman::qq` (Turner 2018), `CMplot::CMplot`, `locuszoomr::locus_plot`
- Python: `matplotlib` + `pandas` for custom; `assocplots` for ready-made

## The Single Most Important Modern Insight -- The Threshold Is Always Conditional

The "genome-wide significant" line at `p < 5e-8` (Pe'er 2008 *Genet Epidemiol* 32:381) is calibrated for **European-ancestry common-variant GWAS** assuming ~1M effectively independent tests. It is the wrong threshold for:

- **Whole-genome sequencing** including rare variants (~5e-9 EUR, ~1e-9 AFR; Pulit 2017 *Genet Epidemiol* 41:145; Xu 2014 *Genet Epidemiol* 38:281)
- **Non-European ancestry** with different LD structure (typically more stringent)
- **TWAS / PWAS** with ~20,000 tested genes (Bonferroni 2.5e-6)
- **Multi-ethnic meta-analysis** (5e-9 by convention for trans-ancestry)
- **Burden / SKAT rare-variant tests** (per-gene; ~2.5e-6)
- **Locus-wise fine-mapping** (within-locus testing, no genome-wide correction needed)

A Manhattan plot's significance line is a contract with the reader about which multiple-testing regime applies. Mismatched thresholds over- or under-report hits.

## Decision Tree by Analysis

| Analysis | Genome-wide threshold | Suggestive threshold | Reference |
|----------|----------------------|---------------------|-----------|
| Common-variant GWAS (Eur) | 5e-8 | 1e-5 | Pe'er 2008 *Genet Epidemiol* 32:381 |
| Whole-genome sequencing (all variants, EUR) | 5e-9 | 5e-8 | Pulit 2017 *Genet Epidemiol* 41:145; Xu 2014 *Genet Epidemiol* 38:281 |
| Non-European ancestry (empirical per pop) | ~3.24e-8 AFR; ~9.26e-8 EAS | – | Kanai 2016 *J Hum Genet* 61:861 |
| TWAS (~20k genes) | 2.5e-6 (Bonferroni) | 1e-4 | Standard practice |
| PWAS (~5k proteins) | 1e-5 | 1e-4 | Standard practice |
| eQTL trans (genome-wide per probe) | Bonferroni over genes × variants | Per-tissue | GTEx convention |
| eQTL cis (within 1Mb) | nominal p < 1e-5 with permutation | – | GTEx FastQTL |
| Rare-variant gene burden | 2.5e-6 | 1e-4 | Bonferroni 20k genes |
| Trans-ancestry meta-analysis | 5e-9 | – | Convention |

## Genomic Inflation (λGC) -- The Mandatory QC Step

**Goal:** Quantify whether observed p-values are inflated relative to the chi-square null, indicating cryptic population structure, relatedness, or technical artifacts.

**Approach:** Convert observed p to chi-square; compute median chi-square divided by 0.4549 (the median of chi-square_1; Devlin-Roeder 1999); plot expected vs observed quantiles (QQ plot).

```r
library(qqman)
chisq <- qchisq(1 - df$P, df = 1)
lambda <- median(chisq) / 0.4549
# lambda = 1.0 -> no inflation
# lambda > 1.1 -> investigate; could indicate confounding
# lambda > 1.2 -> almost certainly confounded; principal components or LMM needed

qq(df$P, main = paste('QQ plot (lambda =', round(lambda, 3), ')'))
```

```python
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

chisq = stats.chi2.isf(df['P'], df=1)
lambda_gc = np.median(chisq) / stats.chi2.ppf(0.5, df=1)

# QQ plot
expected = -np.log10(np.arange(1, len(df)+1) / (len(df) + 1))
observed = -np.log10(np.sort(df['P']))
fig, ax = plt.subplots(figsize=(4, 4))
ax.scatter(expected, observed, s=2)
ax.plot([0, max(expected)], [0, max(expected)], 'r--')
ax.set_xlabel(r'Expected $-\log_{10}(p)$')
ax.set_ylabel(r'Observed $-\log_{10}(p)$')
ax.set_title(f'QQ ($\\lambda_{{GC}} = {lambda_gc:.3f}$)')
```

**Interpretation**:
- λ = 1.00 ± 0.02 — well-calibrated
- λ > 1.05 — possible inflation; consider sample-size adjustment (`λ_1000 = 1 + (λ - 1) * 1000/n`)
- λ > 1.10 — confounded; population structure not removed; rerun with PC adjustment or LMM (BOLT-LMM, GEMMA, SAIGE)
- λ < 1.00 — deflation; usually a bug (wrong test statistic, conservative p-values)

Inflation can also be **legitimate polygenic signal** (Yang 2011 *Eur J Hum Genet* 19:807). Distinguish via LD-score regression intercept: confounding inflates intercept; polygenic signal inflates slope.

## Small-N and Rare-Variant Regimes -- When Standard Asymptotics Break

Standard logistic regression / Wald test p-values are anti-conservative when (a) case count < 200, (b) per-variant minor-allele count < 20, (c) case-control ratio is severely unbalanced (typical in EHR-derived cohorts). λGC may look normal but per-variant p-values are inflated independently — a Manhattan plot of these p-values is misleading regardless of inflation diagnostics.

| Regime | Test choice | Tool |
|--------|-------------|------|
| Balanced case-control, N>5000, MAF>0.01 | Standard logistic / linear regression | PLINK, REGENIE |
| Unbalanced (case fraction <10%), large N | SPA-corrected logistic regression | SAIGE, REGENIE Firth/SPA |
| Small N (<5000) | Penalized regression with bias correction | SAIGE Firth, REGENIE |
| Rare variants (MAC <20) | Gene-burden or SKAT-O | STAAR, REGENIE burden |

Specifically: **SAIGE** (Zhou 2018 *Nat Genet* 50:1335) and **REGENIE** (Mbatchou 2021 *Nat Genet* 53:1097) implement saddlepoint-approximation (SPA) and Firth-bias correction. Use them for any cohort with severe case-control imbalance; the Manhattan / QQ output is then defensibly calibrated.

## Manhattan Plot -- Canonical Layout

```r
library(qqman)
manhattan(df,
          chr = 'CHR', bp = 'BP', p = 'P', snp = 'SNP',
          col = c('#0072B2', '#56B4E9'),
          genomewideline = -log10(5e-8),
          suggestiveline = -log10(1e-5),
          ylim = c(0, max(-log10(df$P)) * 1.1),
          highlight = lead_snps,
          annotatePval = 5e-8,
          annotateTop = TRUE)
```

```python
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def manhattan_plot(df, p_threshold=5e-8, suggestive=1e-5, y_cap=None):
    df = df.sort_values(['CHR', 'BP']).copy()
    df['neg_log10_p'] = -np.log10(df['P'])
    if y_cap:
        df['neg_log10_p'] = df['neg_log10_p'].clip(upper=y_cap)

    df['x'] = np.arange(len(df))
    chr_ticks = df.groupby('CHR')['x'].median()
    chr_colors = ['#0072B2', '#56B4E9']

    fig, ax = plt.subplots(figsize=(10, 4))
    for i, (chrom, group) in enumerate(df.groupby('CHR')):
        ax.scatter(group['x'], group['neg_log10_p'],
                   c=chr_colors[i % 2], s=3, rasterized=True)
    ax.axhline(-np.log10(p_threshold), color='red', linestyle='--', lw=0.5)
    ax.axhline(-np.log10(suggestive), color='grey', linestyle='--', lw=0.5)
    ax.set_xticks(chr_ticks)
    ax.set_xticklabels(chr_ticks.index, rotation=0)
    ax.set_xlabel('Chromosome')
    ax.set_ylabel(r'$-\log_{10}(p)$')
    return fig
```

## Extreme Tail Handling -- The Y-Axis Cap

Genome-wide significant peaks routinely reach -log10(p) = 100+ (e.g., GWAS of BMI at FTO). The visual effect: one peak fills the y-axis, all other signal is invisible.

**Fixes (ordered by preference):**

1. **Cap and indicate:** `y_cap = 25`; clip points above the cap; mark capped points with `^` arrow at the top of the panel. Use Y-axis label "−log10(P), capped at 25"
2. **Split y-axis** via `ggbreak::scale_y_break()` (R) or `axes_grid1.divider` (matplotlib)
3. **Two-panel plot** with full y range in top, zoomed range in bottom
4. **Use sqrt or asinh transform:** less intuitive but preserves all data; rarely chosen for Manhattan

## Miami Plot -- Two-Trait Comparison

```r
# CMplot supports Miami natively
library(CMplot)
CMplot(list(trait1_df, trait2_df),
       plot.type = 'm',
       multraits = TRUE,
       threshold = 5e-8,
       threshold.col = 'red',
       col = list(c('#0072B2','#56B4E9'), c('#D55E00','#E69F00')),
       file = 'jpg', file.output = TRUE)
```

Miami plot mirrors trait 1 above the x-axis, trait 2 below. Useful for shared-locus discovery (mirrored peaks at the same locus = pleiotropy candidate).

## Locuszoom-Style Regional Plot

A locuszoom plot zooms into a ~1Mb window around a lead SNP, colors SNPs by LD r² to the lead, overlays recombination rate (cM/Mb), and shows the gene track. The canonical tool is locuszoom.org (Pruim 2010 *Bioinformatics* 26:2336); the R package is `locuszoomr` (Lai 2024).

```r
library(locuszoomr)
loc <- locus(gene = 'TCF7L2',
             flank = 5e5,
             ens_db = 'EnsDb.Hsapiens.v86',
             data = gwas_df,
             snp = 'SNP', chrom = 'CHR', pos = 'BP', p = 'P', labs = 'SNP')
# LD computed via LDlinkR / 1000G reference
loc <- link_LD(loc, pop = 'EUR', token = ldlink_token)
locus_plot(loc, labels = c('index', 'top'))
```

**LD reference choice:** ALWAYS match the GWAS population. Using a 1000G European LD reference for a Japanese GWAS produces wrong LD colorings and misleads fine-mapping.

## Per-Method Failure Modes

### Inflation diagnosed as polygenic signal

**Trigger:** λGC = 1.15; analyst concludes "polygenic," moves on.

**Mechanism:** Inflation can be confounding (population structure, relatedness, technical) OR polygenicity. LD-score regression separates them: intercept = confounding; slope = polygenicity.

**Symptom:** Top hits replicate poorly in independent cohorts.

**Fix:** Run LDSC (`ldsc.py --h2`); intercept significantly > 1 indicates confounding. Adjust with 10-20 PCs or switch to LMM.

### Wrong significance threshold for the analysis

**Trigger:** Plotting Bonferroni-naive 5e-8 line on a TWAS or rare-variant burden plot.

**Mechanism:** 5e-8 is calibrated for ~1M independent common-variant tests; other analyses have different effective test counts.

**Symptom:** Reviewer flags "this gene doesn't pass Bonferroni" but the plot's red line is at 5e-8.

**Fix:** Match the threshold to the analysis (table above).

### Cap with no indication

**Trigger:** Y-axis clipped at 25 without arrow markers for capped points.

**Mechanism:** Reader cannot tell how high the true peak is.

**Symptom:** Reviewer asks for actual p-value; the reported 1e-100 conflicts with the displayed cap at 25.

**Fix:** Mark capped points with `^` symbol; annotate axis "(capped at 25)"; include unclipped numerical value in caption.

### Manhattan with random chromosome colors

**Trigger:** `col = rainbow(22)` for chromosome alternating.

**Mechanism:** 22 random hues add no information; visual chaos.

**Symptom:** Reader cannot quickly identify which chromosome a peak is on.

**Fix:** Two-color alternation (`c('#0072B2', '#56B4E9')`). Chromosome boundaries are clear from spacing alone.

### LD reference mismatched to GWAS population

**Trigger:** 1000G EUR LD reference used to color a Japanese / African GWAS regional plot.

**Mechanism:** LD differs by population; r² is population-specific.

**Symptom:** Locuszoom shows uncorrelated SNPs in red (high r²) or vice versa.

**Fix:** Match LD reference to GWAS population; for trans-ancestry GWAS, show per-population panels or use largest-N population reference and annotate the discrepancy.

### qqman::manhattan ignores BP order within chromosome

**Trigger:** Unsorted input data frame.

**Mechanism:** qqman plots in input row order, not coordinate order.

**Symptom:** Peaks render as vertical scatter at wrong x-position.

**Fix:** `df <- df %>% arrange(CHR, BP)` before plotting.

## Reconciliation: When QC Metrics Disagree

| Pattern | Likely cause | Action |
|---------|--------------|--------|
| λGC > 1.1 but LDSC intercept ~1 | Polygenic signal | Document; no action needed |
| λGC > 1.1 AND LDSC intercept > 1 | Confounding | Add PCs / use LMM |
| QQ plot "S-shaped" | Severe inflation or non-additive model misspecification | Inspect; possibly model misspecified |
| QQ plot deflated below diagonal | Conservative p (e.g., score test); or wrong test stat | Review test statistic computation |
| Top SNP genome-wide but small effect | Likely true; or relatedness | Verify in unrelated subset |
| Replication fails for top hits | Confounding (winner's curse); or true heterogeneity | Trans-ancestry meta-analysis or LMM rerun |

## Quantitative Thresholds

| Threshold | Value | Source |
|-----------|-------|--------|
| Common-variant GWAS sig | 5e-8 | Pe'er 2008 |
| WGS sig (all variants, EUR) | 5e-9 | Pulit 2017; Xu 2014 |
| Empirical pop-specific (e.g., EAS) | ~9.26e-8 EAS | Kanai 2016 |
| TWAS / PWAS Bonferroni | 0.05 / n_genes | Standard |
| λGC well-calibrated | 1.00 ± 0.02 | Standard |
| λGC investigate | >1.05 | Common practice |
| λGC confounded | >1.10 | Common practice |
| Sample-size adjusted λ | λ_1000 = 1 + (λ - 1) × 1000/n | Standard scaling |
| Suggestive threshold | 1e-5 | Pe'er 2008 |
| Y-cap typical | 25-50 -log10(p) | Visualization choice |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| Peaks at wrong x position | Data not sorted by CHR, BP | `arrange(CHR, BP)` upstream |
| λGC reported as conclusion alone | Confounding vs polygenicity not separated | Run LDSC for intercept vs slope |
| Threshold line at 5e-8 on TWAS | Wrong multiple-testing regime | Use Bonferroni-correct threshold |
| Y-axis crushed by one peak | No cap, no split | Cap at 25-50 with arrow markers OR split axis |
| Regional plot LD colors look wrong | LD reference mismatched to GWAS pop | Match LD reference to ancestry |
| QQ plot deflated | Conservative test or wrong stat | Verify test statistic |
| Manhattan with 22 distinct hues | Cosmetic clutter | Two-color alternation |
| Lead SNPs unlabeled | Default labeling off | `annotatePval = 5e-8, annotateTop = TRUE` |

## References

- Kanai M, Tanaka T, Okada Y. 2016. Empirical estimation of genome-wide significance thresholds based on the 1000 Genomes Project data set. *J Hum Genet* 61:861-866.
- Lai R. 2024. locuszoomr: an R/Bioconductor package for locus visualization. (CRAN package documentation)
- Pulit SL, de With SAJ, de Bakker PIW. 2017. Resetting the bar: statistical significance in whole-genome sequencing-based association studies of global populations. *Genet Epidemiol* 41(2):145-151.
- Xu C, Tachmazidou I, Walter K, et al. 2014. Estimating genome-wide significance for whole-genome sequencing studies. *Genet Epidemiol* 38(4):281-290.
- Pe'er I, Yelensky R, Altshuler D, Daly MJ. 2008. Estimation of the multiple testing burden for genomewide association studies of nearly all common variants. *Genet Epidemiol* 32:381-385.
- Pruim RJ, Welch RP, Sanna S, et al. 2010. LocusZoom: regional visualization of genome-wide association scan results. *Bioinformatics* 26:2336-2337.
- Pearson TA, Manolio TA. 2008. How to interpret a genome-wide association study. *JAMA* 299(11):1335-1344.
- Turner SD. 2018. qqman: an R package for visualizing GWAS results using Q-Q and manhattan plots. *J Open Source Softw* 3(25):731.
- Yang J, Weedon MN, Purcell S, et al. 2011. Genomic inflation factors under polygenic inheritance. *Eur J Hum Genet* 19(7):807-812.
- Bulik-Sullivan BK, Loh PR, Finucane HK, et al. 2015. LD Score regression distinguishes confounding from polygenicity in genome-wide association studies. *Nat Genet* 47:291-295.
- Devlin B, Roeder K. 1999. Genomic control for association studies. *Biometrics* 55(4):997-1004.
- Mbatchou J, Barnard L, Backman J, et al. 2021. Computationally efficient whole-genome regression for quantitative and binary traits. *Nat Genet* 53(7):1097-1103.
- Zhou W, Nielsen JB, Fritsche LG, et al. 2018. Efficiently controlling for case-control imbalance and sample relatedness in large-scale genetic association studies. *Nat Genet* 50(9):1335-1341.

## Related Skills

- population-genetics/association-testing - Run the GWAS that produces the summary stats
- workflows/gwas-pipeline - End-to-end GWAS workflow including QC
- causal-genomics/fine-mapping - Within-locus fine-mapping post-locuszoom
- causal-genomics/colocalization-analysis - Two-trait shared-causal-variant analysis
- data-visualization/color-palettes - Two-color chromosome alternation
- phasing-imputation/imputation-qc - Pre-GWAS imputation QC affects QQ
<!-- END FILE: data-visualization/manhattan-qq-locuszoom/SKILL.md -->

## 子目录：data-visualization/matplotlib-fundamentals

<!-- BEGIN FILE: data-visualization/matplotlib-fundamentals/SKILL.md -->
---
name: bio-data-visualization-matplotlib-fundamentals
description: Build publication-quality figures with matplotlib using the object-oriented Figure/Axes API, constrained_layout, rcParams customization, TrueType (Type-42) font embedding for journal submission, and CVD-safe palettes. Covers seaborn integration, common chart types, axis formatting, and the small gotchas that distinguish reproducible matplotlib from notebook scratch. Use when producing publication figures in Python — RNA-seq scatter, single-cell embeddings, generic biological plotting.
tool_type: python
primary_tool: matplotlib
goal_approach_exempt: true
---

## Version Compatibility

Reference examples tested with: matplotlib 3.8+, seaborn 0.13+, numpy 1.26+, pandas 2.2+.

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed package and adapt the example to match the actual API rather than retrying.

# matplotlib Fundamentals

**"Make a publication figure in Python"** -> Build via the **object-oriented Figure/Axes API** (not pyplot state-machine), with `constrained_layout` for axes alignment, `pdf.fonttype=42` for journal-compliant TrueType fonts, CVD-safe palettes, and rasterized point layers for large scatter. The pyplot interface is for notebook scratch; the Figure/Axes API is for reproducible figures.

- Python: `fig, ax = plt.subplots()` -> `ax.scatter` / `ax.plot` / `ax.bar`; `seaborn.objects` (new grammar API) for ggplot-like

## The Three Modern Defaults

1. **Object-oriented API** — `fig, ax = plt.subplots(figsize=(4, 3))` then `ax.scatter(x, y)`, `ax.set_xlabel(...)`. The pyplot state-machine (`plt.scatter`, `plt.xlabel`) hides which axes are being modified and breaks in multi-subplot figures.

2. **constrained_layout** — `plt.subplots(constrained_layout=True)` automatically prevents axis-label clipping and tight-packs subplots. Replaces the older `tight_layout()` and is the default in matplotlib 3.6+.

3. **Type-42 (TrueType) font embedding** — `plt.rcParams['pdf.fonttype']=42` produces searchable/editable PDF text. Default Type-3 PostScript glyphs are not searchable and **rejected by Nature, IEEE, ACM, and many other publishers**.

## Standard Setup for Publication

```python
import matplotlib.pyplot as plt
import matplotlib as mpl

# rcParams for publication compliance
mpl.rcParams.update({
    'pdf.fonttype': 42,                 # TrueType -- searchable PDFs
    'ps.fonttype': 42,                  # TrueType in EPS
    'font.family': 'sans-serif',
    'font.sans-serif': ['Arial', 'Helvetica', 'DejaVu Sans'],
    'font.size': 7,                     # Nature requires 5-7 pt body text
    'axes.labelsize': 7,
    'axes.titlesize': 8,
    'xtick.labelsize': 6,
    'ytick.labelsize': 6,
    'legend.fontsize': 6,
    'figure.dpi': 100,                  # display
    'savefig.dpi': 300,                 # save
    'savefig.bbox': 'tight',
    'savefig.pad_inches': 0.05,
    'axes.linewidth': 0.5,
    'xtick.major.width': 0.5,
    'ytick.major.width': 0.5,
    'lines.linewidth': 1.0,
    'patch.linewidth': 0.5,
})
```

## Figure / Axes API

```python
import matplotlib.pyplot as plt

# Single axes
fig, ax = plt.subplots(figsize=(89/25.4, 70/25.4),       # 89mm x 70mm in inches; Nature single col
                       constrained_layout=True)
ax.scatter(x, y, c='#0072B2', s=10, alpha=0.7, edgecolors='none', rasterized=True)
ax.set_xlabel('PC1 (45%)')
ax.set_ylabel('PC2 (12%)')
ax.spines[['top', 'right']].set_visible(False)
fig.savefig('scatter.pdf')

# Grid of axes
fig, axes = plt.subplots(2, 3, figsize=(180/25.4, 100/25.4),  # 180mm double col
                          constrained_layout=True)
for ax, (label, panel_data) in zip(axes.flat, data.items()):
    ax.plot(panel_data['x'], panel_data['y'])
    ax.set_title(label, fontsize=8)
```

## Common Chart Types

```python
# Scatter -- always rasterized for >1000 points
ax.scatter(x, y, c=values, cmap='viridis', s=8, alpha=0.6,
           edgecolors='none', rasterized=True)
plt.colorbar(ax.collections[0], ax=ax, label='Expression', shrink=0.8)

# Line
ax.plot(x, y1, color='#0072B2', label='Control', linewidth=1)
ax.plot(x, y2, color='#D55E00', label='Treatment', linewidth=1)
ax.fill_between(x, y_low, y_high, color='#0072B2', alpha=0.2)
ax.legend(frameon=False, fontsize=6)

# Bar
ax.bar(categories, values, color='#0072B2', edgecolor='black', linewidth=0.5)

# Box / violin (prefer seaborn for these -- see distribution-plots)
ax.boxplot([group_a, group_b, group_c], labels=['A', 'B', 'C'],
           patch_artist=True, boxprops=dict(facecolor='#0072B2', alpha=0.7))

# Histogram
ax.hist(values, bins=30, color='#0072B2', edgecolor='white', linewidth=0.5)

# Heatmap (prefer seaborn for clustered; see heatmaps-clustering)
im = ax.imshow(matrix, cmap='RdBu_r', aspect='auto', vmin=-vmax, vmax=vmax)
plt.colorbar(im, ax=ax, label='Z-score')
```

## seaborn Integration

```python
import seaborn as sns

# seaborn shares the matplotlib Figure/Axes -- pass ax= argument
fig, ax = plt.subplots(figsize=(4, 3), constrained_layout=True)
sns.scatterplot(data=df, x='log_fold_change', y='neg_log_p',
                hue='significance', palette=['#999999', '#0072B2', '#D55E00'],
                s=10, alpha=0.7, ax=ax, rasterized=True)

# seaborn 0.13+ has the `objects` grammar interface (ggplot-like)
import seaborn.objects as so
(so.Plot(df, x='log_fold_change', y='neg_log_p')
   .add(so.Dots(pointsize=2), color='significance')
   .scale(color=['#999999', '#0072B2', '#D55E00']))
```

**Return-type gotcha:** seaborn axes-level functions (`scatterplot`, `boxplot`, `barplot`) return Axes. Figure-level (`displot`, `relplot`, `catplot`) return FacetGrid — needs `.set_axis_labels(x, y)` not `.set_xlabel(x)`.

## Axis Formatting

```python
# Log scale
ax.set_yscale('log')

# Scientific notation
from matplotlib.ticker import ScalarFormatter
ax.xaxis.set_major_formatter(ScalarFormatter(useMathText=True))

# Date axis
import matplotlib.dates as mdates
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))

# Tick frequency
ax.set_xticks(np.arange(0, 10, 2))
ax.set_xticklabels(['A', 'B', 'C'], rotation=45, ha='right')

# Grid
ax.grid(axis='y', alpha=0.3, linestyle='--', linewidth=0.5)
```

## Color and Palette

```python
# CVD-safe categorical
okabe_ito = ['#E69F00', '#56B4E9', '#009E73', '#F0E442',
             '#0072B2', '#D55E00', '#CC79A7', '#000000']

# Perceptually-uniform sequential (Crameri batlow / viridis cividis)
from cmcrameri import cm as cmc
plt.imshow(data, cmap=cmc.batlow)
plt.imshow(data, cmap='viridis')                          # built-in

# Diverging symmetric for LFC / z-score
vmax = np.quantile(np.abs(data), 0.99)
plt.imshow(data, cmap='RdBu_r', vmin=-vmax, vmax=vmax)   # symmetric
```

See `data-visualization/color-palettes` for full palette decision tree.

## Saving

```python
# PDF for vector text + raster scatter (best of both)
fig.savefig('figure.pdf', dpi=300, bbox_inches='tight')

# PNG for raster (web, presentations)
fig.savefig('figure.png', dpi=300, bbox_inches='tight')

# TIFF for some journals
fig.savefig('figure.tiff', dpi=300, pil_kwargs={'compression': 'tiff_lzw'})

# SVG for editable vector
fig.savefig('figure.svg', bbox_inches='tight')
```

## Common Failure Modes

### Default Type-3 fonts rejected by journals

**Trigger:** Default `pdf.fonttype=3` (PostScript Type 3 glyphs as drawing operators).

**Mechanism:** Type-3 glyphs are not searchable or selectable; many journals reject.

**Symptom:** Submission rejected at automated check; "Type 3 fonts not permitted."

**Fix:** `mpl.rcParams['pdf.fonttype']=42` AND `ps.fonttype=42`. Verify with `pdffonts figure.pdf` showing `TrueType`.

### tight_layout fails on complex grids

**Trigger:** `plt.tight_layout()` on a figure with colorbars or shared axes.

**Mechanism:** tight_layout doesn't account for axes added after-the-fact (colorbars).

**Symptom:** Labels clipped; subplots overlap colorbar.

**Fix:** Use `constrained_layout=True` in `plt.subplots()` instead; or `fig.set_constrained_layout(True)` after creation.

### pyplot state-machine in multi-subplot

**Trigger:** `plt.xlabel(...)` after `plt.subplots(2, 3)`.

**Mechanism:** pyplot calls modify the *current* axes — usually the last created. Multi-subplot code becomes order-dependent.

**Symptom:** Wrong subplot gets the label.

**Fix:** Use `ax.set_xlabel(...)` with explicit axes reference.

### Scatter of 100000 points crashes PDF viewer

**Trigger:** Vector scatter at large N; one PDF page becomes 50 MB.

**Mechanism:** Each scatter point is a vector circle.

**Symptom:** PDF takes 30 seconds to open; Illustrator crashes; reviewer files complaint.

**Fix:** `rasterized=True` on the scatter call. Keep axes and text vector.

### seaborn FacetGrid vs Axes return-type confusion

**Trigger:** `g = sns.displot(...)`; calling `g.set_xlabel('x')` fails.

**Mechanism:** displot returns FacetGrid; needs `.set_axis_labels(x, y)` or per-axes iteration.

**Symptom:** AttributeError on .set_xlabel.

**Fix:** Use `set_axis_labels` for FacetGrid; `set_xlabel` for Axes. Switch to axes-level `sns.histplot(ax=ax)` to get Axes-API behavior.

### figsize in inches when mm was intended

**Trigger:** `figsize=(89, 70)` thinking mm; matplotlib expects inches.

**Mechanism:** Default figure unit is inches.

**Symptom:** Figure is 89 inches wide.

**Fix:** Convert: `figsize=(89/25.4, 70/25.4)` for mm input.

### Colorbar over-fills the axes

**Trigger:** Default `plt.colorbar(im, ax=ax)`.

**Mechanism:** Colorbar takes the same height as the axes; on small subplots dominates.

**Symptom:** Subplot looks squished.

**Fix:** `plt.colorbar(im, ax=ax, shrink=0.6, aspect=20)`; or use `make_axes_locatable` for fine control.

### Vector grid + rasterized scatter mixed properly

**Trigger:** Want vector axes + raster scatter; save as PDF.

**Mechanism:** Default rasterization can include axes if not controlled.

**Symptom:** Whole plot rasterized; axis text blurry on zoom.

**Fix:** Per-element `rasterized=True` on scatter only; axes and text stay vector. Set `fig.set_rasterization_zorder(0)` to globally control.

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| PDF rejected by journal | Type-3 fonts | `pdf.fonttype=42` |
| Subplots overlap | No constrained_layout | `plt.subplots(constrained_layout=True)` |
| Wrong subplot labeled | pyplot state-machine | Use ax.set_xlabel explicitly |
| 50 MB PDF | Vector scatter at large N | `rasterized=True` on scatter |
| Figure too big | mm interpreted as inches | Divide by 25.4 |
| Colorbar dominates | Default size | `shrink=0.6, aspect=20` |
| seaborn .set_xlabel fails | FacetGrid not Axes | `g.set_axis_labels(x, y)` |
| Axes spine missing | Wrong API | `ax.spines[['top','right']].set_visible(False)` |

## References

- Hunter JD. 2007. Matplotlib: A 2D graphics environment. *Comput Sci Eng* 9(3):90-95.
- Rougier NP, Droettboom M, Bourne PE. 2014. Ten simple rules for better figures. *PLOS Comp Biol* 10(9):e1003833.
- Waskom ML. 2021. seaborn: statistical data visualization. *J Open Source Softw* 6(60):3021.

## Related Skills

- data-visualization/color-palettes - Palette selection
- data-visualization/multipanel-figures - GridSpec and patchwork-equivalent layouts
- data-visualization/distribution-plots - seaborn boxplot/violin/raincloud
- data-visualization/heatmaps-clustering - seaborn.clustermap
- data-visualization/volcano-and-ma-plots - matplotlib scatter for volcano
- reporting/figure-export - DPI / format / journal-spec details
<!-- END FILE: data-visualization/matplotlib-fundamentals/SKILL.md -->

## 子目录：data-visualization/multipanel-figures

<!-- BEGIN FILE: data-visualization/multipanel-figures/SKILL.md -->
---
name: bio-data-visualization-multipanel-figures
description: Compose multi-panel publication figures with patchwork, cowplot, gridExtra (R), or matplotlib GridSpec/subfigures (Python) including shared axes/legends/guides collection, panel labels in Nature/Cell convention, and journal-spec sizing. Covers patchwork ≥1.2.0 axes='collect' feature, Type-42 font embedding, and the cairo_pdf save path. Use when composing 2+ subpanels into a single figure for journal submission.
tool_type: mixed
primary_tool: patchwork
---

## Version Compatibility

Reference examples tested with: patchwork 1.2+ (axes='collect' requires this version, released 2024-01-05), cowplot 1.1+, ggplot2 3.5+, matplotlib 3.8+ (subfigures stable since 3.4).

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('<pkg>')` then `?function_name`
- Python: `pip show <package>` then `help(module.function)`

If code throws ImportError, AttributeError, or TypeError, introspect the installed package and adapt the example to match the actual API rather than retrying.

# Multi-Panel Figures

**"Combine plots into a multi-panel figure"** -> Arrange individual plots into a single composed figure with consistent sizing, shared legends/axes, and panel labels (a, b, c) in the Nature/Cell convention. The decision space: which composition library (patchwork most modern in R; matplotlib subfigures in Python), how to share legends and axes, and how to size at journal specifications.

- R: `patchwork` (modern; supports axes/guides collection since 1.2), `cowplot` (older; align_plots), `gridExtra` (basic grid arrange)
- Python: `matplotlib.gridspec.GridSpec`, `fig.subfigures()` (matplotlib 3.4+)

## The Single Most Important Modern Insight -- Axes Collection Requires patchwork ≥ 1.2.0

patchwork 1.2.0 (released 2024-01-05) added `axes = 'collect'` and `axis_titles = 'collect'` to `plot_layout()`. These collect repeated axes / titles across subplots into a single shared axis label — the same way `guides = 'collect'` (available since patchwork 1.0) collects legends.

Without this, multi-panel figures with shared axes show redundant labels on every subplot (visually cluttered AND non-Nature compliant). Verify patchwork version is ≥ 1.2.0; older versions silently ignore the `axes` argument.

## patchwork -- Modern R Composition

**Goal:** Compose 4 ggplot objects into a 2×2 panel figure with shared legend, collected axes, and bold panel labels (a, b, c, d) in upper-left of each subplot.

**Approach:** Combine plots with `+`, `/`, `|` operators; apply `plot_layout(guides='collect', axes='collect')` for shared elements; add `plot_annotation(tag_levels='a')` for Nature-style panel labels.

```r
library(patchwork)
library(ggplot2)

p1 <- ggplot(df, aes(x, y)) + geom_point() + theme_classic()
p2 <- ggplot(df, aes(group, value)) + geom_boxplot() + theme_classic()
p3 <- ggplot(df, aes(x)) + geom_histogram() + theme_classic()
p4 <- ggplot(df, aes(x, y, color = group)) + geom_point() + theme_classic()

# 2x2 grid
fig <- (p1 + p2) / (p3 + p4) +
    plot_annotation(tag_levels = 'a',
                    theme = theme(plot.tag = element_text(face = 'bold', size = 10))) +
    plot_layout(guides = 'collect',         # share legends
                axes = 'collect',           # share axes (patchwork >= 1.2.0)
                axis_titles = 'collect')

ggsave('figure1.pdf', fig, width = 180, height = 140, units = 'mm', device = cairo_pdf)
```

## patchwork Operators

```r
p1 + p2                                     # side-by-side
p1 / p2                                     # vertical stack
(p1 | p2) / p3                              # mixed: top row two, bottom one
p1 + p2 + p3 + plot_layout(ncol = 3)
p1 + p2 + plot_layout(widths = c(2, 1))     # 2:1 width ratio

# Complex grid via design string
design <- "
AAB
AAB
CCC
"
p1 + p2 + p3 + plot_layout(design = design)

# Inset
p1 + inset_element(p2, left = 0.6, bottom = 0.6, right = 1, top = 1)
```

## cowplot -- Alternative with Alignment Focus

```r
library(cowplot)

# plot_grid is the workhorse
combined <- plot_grid(p1, p2, p3, p4,
                       ncol = 2, labels = 'AUTO',         # 'AUTO' = A, B, C, D
                       label_size = 12, label_fontface = 'bold',
                       align = 'hv',                       # align horizontally + vertically
                       rel_widths = c(1, 1), rel_heights = c(1, 1))

# Nested grids
top_row <- plot_grid(p1, p2, ncol = 2, labels = c('A', 'B'))
bottom <- plot_grid(p3, p4, ncol = 2, labels = c('C', 'D'))
combined <- plot_grid(top_row, bottom, nrow = 2, rel_heights = c(1, 1.2))

ggsave('figure.pdf', combined, width = 180, height = 140, units = 'mm', device = cairo_pdf)
```

cowplot is older but its alignment behavior is sometimes more reliable than patchwork on edge cases (axes-with-titles of different lengths).

## matplotlib GridSpec (Python)

```python
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

fig = plt.figure(figsize=(180/25.4, 120/25.4), constrained_layout=True)
gs = GridSpec(2, 3, figure=fig)

ax1 = fig.add_subplot(gs[0, 0])
ax2 = fig.add_subplot(gs[0, 1:])         # top right, spans columns 1-2
ax3 = fig.add_subplot(gs[1, :])           # bottom row, spans all columns

ax1.scatter(x, y, s=4, rasterized=True)
ax2.plot(x, y)
ax3.bar(cats, vals)

# Panel labels at (-0.15, 1.05) of each axes
for ax, lbl in zip([ax1, ax2, ax3], 'abc'):
    ax.text(-0.15, 1.05, lbl, transform=ax.transAxes,
            fontsize=10, fontweight='bold', va='top')

fig.savefig('figure.pdf', dpi=300, bbox_inches='tight')
```

## matplotlib Subfigures

```python
fig = plt.figure(figsize=(180/25.4, 120/25.4), constrained_layout=True)
subfigs = fig.subfigures(1, 2, width_ratios=[2, 1])

# Left subfigure has 2 stacked panels
axs_left = subfigs[0].subplots(2, 1)
axs_left[0].plot(x, y)
axs_left[1].scatter(x, y, rasterized=True)

# Right subfigure has one panel
ax_right = subfigs[1].subplots(1, 1)
ax_right.imshow(matrix)
subfigs[1].colorbar(ax_right.images[0], ax=ax_right, shrink=0.5)
```

Subfigures are stronger than GridSpec for complex compositions because each subfigure has its own constrained_layout.

## Journal Sizing

| Journal | Single col | Double col | Max height |
|---------|------------|------------|------------|
| Nature | 89 mm | 183 mm | 247 mm |
| Cell | 85 mm | 174 mm | 235 mm |
| Science | 55 mm | 120 mm | 220 mm |
| PNAS | 87 mm | 178 mm | 225 mm |
| eLife | 86 mm | 175 mm | ~240 mm |

Always set explicit units in mm; default inches is the most common source of "figure too large" errors.

## Panel Labels — Nature/Cell Convention

- **Nature**: lowercase bold serif (a, b, c) in upper-left corner of each panel; 8 pt
- **Cell**: uppercase bold sans-serif (A, B, C); placed flush left at panel top
- **Science**: capital bold (A, B, C)

```r
# patchwork tag_levels for lowercase (Nature)
plot_annotation(tag_levels = 'a',
                theme = theme(plot.tag = element_text(face = 'bold', size = 9)))
# 'A' for uppercase (Cell)
plot_annotation(tag_levels = 'A')
# 'i' for roman numerals (sometimes for sub-panels)
```

```r
# cowplot
plot_grid(..., labels = 'AUTO')   # auto uppercase A, B, C
plot_grid(..., labels = 'auto')   # auto lowercase a, b, c
```

## Per-Method Failure Modes

### patchwork axes='collect' silently ignored

**Trigger:** Using `plot_layout(axes='collect')` with patchwork < 1.2.0.

**Mechanism:** Older versions silently accept the argument but don't act on it.

**Symptom:** Redundant axes on each subplot; no warning or error.

**Fix:** `packageVersion('patchwork')` must be ≥ 1.2.0. Update with `install.packages('patchwork')`.

### Default ggsave produces non-portable PDF

**Trigger:** `ggsave('out.pdf', fig)` without `device = cairo_pdf`.

**Mechanism:** Default pdf() device produces fonts that journals reject on some systems.

**Symptom:** Submission rejected at automated check; "non-embedded fonts."

**Fix:** Always `device = cairo_pdf`.

### Figure dimensions in inches when mm intended

**Trigger:** `ggsave('out.pdf', fig, width = 180, height = 140)`.

**Mechanism:** Default `units = 'in'`.

**Symptom:** Figure file rejected for being 180 × 140 inches.

**Fix:** Explicit `units = 'mm'`.

### Panel labels not aligned to panel content

**Trigger:** patchwork `plot_annotation(tag_levels)` with subplots of different y-axis label widths.

**Mechanism:** Tag is positioned relative to the plot canvas, including the y-axis label area.

**Symptom:** Labels are at different horizontal positions in each panel.

**Fix:** Either standardize y-label widths (pad with whitespace) OR move tags inside the plotting area: `theme(plot.tag.position = c(0.02, 0.98))`.

### cowplot align='v' fails on plots of different widths

**Trigger:** `plot_grid(p_wide, p_narrow, align = 'v')`.

**Mechanism:** Vertical alignment requires same x-axis widths.

**Symptom:** Plots align at the y-axis but x-axis labels are offset.

**Fix:** Use `align = 'hv'` if both alignments needed; otherwise patchwork's `axes='collect'` handles this more gracefully.

### Shared legend lost in patchwork

**Trigger:** `(p1 + p2) + plot_layout(guides = 'collect')` but p1 and p2 use different scales.

**Mechanism:** `guides='collect'` merges identical guides; different scales produce duplicate (not merged) legends.

**Symptom:** Two legends still appear.

**Fix:** Standardize the scales across subplots (same `scale_color_manual(values=...)`); OR drop one legend via `& theme(legend.position = 'none')` on the redundant plot.

### matplotlib GridSpec with constrained_layout=False

**Trigger:** Older code with `plt.subplots` no constrained_layout; tight_layout fails on colorbars.

**Mechanism:** tight_layout doesn't know about post-hoc colorbars.

**Symptom:** Colorbar overlaps adjacent subplot.

**Fix:** `plt.figure(constrained_layout=True)` and use `fig.add_subplot(gs[...])`. constrained_layout is the default-on choice in matplotlib 3.6+.

## Reconciliation

| Pattern | Cause | Action |
|---------|-------|--------|
| patchwork and cowplot align differently | Different alignment algorithms | Try both; cowplot's `align='hv'` and patchwork's `axes='collect'` rarely produce identical results |
| Panel labels position differs between sessions | Different y-axis label widths | Standardize across panels |
| Shared legend duplicated | Scales differ across subplots | Use identical scales OR drop legend from N-1 panels |

## Quantitative Thresholds

| Threshold | Value | Source |
|-----------|-------|--------|
| Nature single column | 89 mm | Nature figure guidelines |
| Nature double column | 183 mm | Nature figure guidelines |
| Body text size | 5-7 pt | Nature rejects outside range |
| Panel label size | 8 pt bold | Nature convention |
| patchwork axes='collect' minimum version | 1.2.0 (2024-01-05) | patchwork release notes |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| Redundant axis labels per panel | patchwork < 1.2.0 OR axes='collect' not set | Update + add to plot_layout |
| Non-embedded font rejection | Default ggsave device | `device = cairo_pdf` |
| Figure 180 in × 140 in | Default units = 'in' | `units = 'mm'` |
| Panel tags misaligned | Different y-label widths | Standardize or move tag inside |
| Cowplot vertical alignment fails | Different x-axis widths | Use 'hv' OR switch to patchwork |
| Two legends instead of shared | Scales differ across subplots | Unify scales |
| matplotlib colorbar overlaps subplot | No constrained_layout | constrained_layout=True |

## References

- Pedersen TL. 2024. patchwork: the composer of plots. *CRAN package* (v1.2.0 release notes).
- Wilke CO. 2017. cowplot: streamlined plot theme and plot annotations for ggplot2. *CRAN package*.
- Hunter JD. 2007. Matplotlib: A 2D graphics environment. *Comput Sci Eng* 9(3):90-95.

## Related Skills

- data-visualization/ggplot2-fundamentals - Individual ggplot objects
- data-visualization/matplotlib-fundamentals - Python equivalent
- reporting/figure-export - DPI / format / journal-spec compliance
- data-visualization/color-palettes - Consistent palette across subpanels
<!-- END FILE: data-visualization/multipanel-figures/SKILL.md -->

## 子目录：data-visualization/network-visualization

<!-- BEGIN FILE: data-visualization/network-visualization/SKILL.md -->
---
name: bio-data-visualization-network-visualization
description: Visualize biological networks (PPI, gene-regulatory, co-expression, pathway) with layout algorithm choice (ForceAtlas2, Fruchterman-Reingold, Kamada-Kawai, hive plots), edge bundling, community-based coloring, and reproducible seeds using NetworkX, PyVis, igraph, and Cytoscape automation. Use when rendering biological networks for static publication, interactive HTML exploration, or Cytoscape-format export.
tool_type: python
primary_tool: NetworkX
---

## Version Compatibility

Reference examples tested with: networkx 3.2+, igraph 0.10+ (Python and R), pyvis 0.3+, py4cytoscape 1.9+, matplotlib 3.8+, datashader 0.16+ (for large-graph rasterization).

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- R: `packageVersion('<pkg>')` then `?function_name`

If code throws ImportError, AttributeError, or TypeError, introspect the installed package and adapt the example to match the actual API rather than retrying.

# Network Visualization

**"Plot a biological network"** -> Select a layout algorithm (force-directed for general; hive plot for comparative; ForceAtlas2 for scale-free; circular for small dense), encode node attributes (size by degree/centrality, color by community/module), and choose rendering tier (matplotlib for static publication; PyVis for interactive HTML; Cytoscape for journal-grade compositing). The dominant pitfall is treating layout as biology — node positions in force-directed plots are NOT biologically meaningful; only connectivity is.

- Python: `networkx`, `pyvis.Network`, `py4cytoscape`, `datashader` (large graphs)
- R: `igraph`, `ggraph` (ggplot2-grammar for networks)
- Desktop: Cytoscape (Shannon 2003), Gephi (ForceAtlas2 native)

## The Single Most Important Modern Insight -- Layout Is an Artifact, Not Biology

A force-directed layout (Fruchterman-Reingold, ForceAtlas2, spring) is the result of an optimization that minimizes edge crossing and balances repulsion. The visual position of a node has no biological meaning — it is determined by the layout algorithm + random initialization + iteration count + repulsion parameters.

Two consequences:
1. **Set `random_state` / `seed` for reproducibility.** Without it, the same network produces different layouts across runs.
2. **Do not read "cluster A is closer to cluster B than C" as biology.** Inter-community distances in force-directed layouts are not preserved. Only EDGE existence and node DEGREE are biological signals from the visual.

For biology-faithful layouts, use **hive plots** (Krzywinski 2012) which anchor nodes to fixed axes by metadata, OR **circular** layouts which preserve symmetry but don't claim distance meaning.

## Decision Tree by Network Type and Question

| Network | Recommended layout | Reason |
|---------|--------------------|--------|
| Generic PPI (<500 nodes) | Fruchterman-Reingold OR Kamada-Kawai | General-purpose; clean separation |
| Scale-free PPI (>500 nodes, hub-spoke) | ForceAtlas2 (Jacomy 2014) | Designed for scale-free networks |
| Gene regulatory (directed) | Hierarchical OR ForceAtlas2 with edge direction | Direction matters; hierarchical for cascade |
| Pathway / signaling | Manual or Cytoscape layout | Curated layouts in WikiPathways/Reactome |
| Co-expression module visualization | Hive plot anchored by module assignment | Comparative; nodes by category |
| Many-to-many (>10k edges) | Hierarchical edge bundling (Holten 2006) | Reduces visual clutter |
| Large network (>50k nodes) | Datashader raster + interactive zoom | matplotlib chokes; raster is the only honest display |
| Connectivity-only (no positions) | Adjacency matrix heatmap | Network as matrix avoids layout artifact |
| Comparing two networks | Side-by-side same layout (`pos` reused) | Otherwise layout differences mask biology |

## Layout Algorithms

```python
import networkx as nx

# Spring / Fruchterman-Reingold (general)
pos = nx.spring_layout(G, k=1/np.sqrt(len(G)), iterations=100, seed=42)

# Kamada-Kawai (better for small dense)
pos = nx.kamada_kawai_layout(G)

# Circular
pos = nx.circular_layout(G)

# Shell (hub at center, periphery outside)
pos = nx.shell_layout(G, nlist=[hub_nodes, periphery_nodes])

# Spectral (reveals clusters)
pos = nx.spectral_layout(G)

# Bipartite (two sets)
pos = nx.bipartite_layout(G, top_nodes)

# Hierarchical (DAG)
pos = nx.nx_pydot.graphviz_layout(G, prog='dot')   # requires graphviz
```

For ForceAtlas2 in Python: `fa2_modified` (newer maintained fork) or use Gephi for the canonical implementation. For ggraph in R:

```r
library(ggraph)
ggraph(g, layout = 'fr') +                          # Fruchterman-Reingold
    geom_edge_link(alpha = 0.3) +
    geom_node_point()

ggraph(g, layout = 'kk') +                          # Kamada-Kawai
ggraph(g, layout = 'circle') +
ggraph(g, layout = 'graphopt') +                    # OpenOrd-style for large
```

## Hive Plots (Krzywinski 2012) — Biology-Faithful

A hive plot anchors nodes to 2-3 fixed axes by a categorical attribute (e.g., node type, module, chromosome); edges drawn as arcs between axes. Removes the "hairball" effect by replacing free 2D layout with structured 1D axes.

```python
# HiveNetX or pyveplot for hive layouts
# Or use d3.js HivePlot for interactive
# R: HivePlotData via igraph + custom rendering
```

Use hive plots when comparing networks across conditions OR when nodes have a categorical structure (e.g., TFs vs targets, chromosomes for 3D-genome interactions).

## Hierarchical Edge Bundling (Holten 2006)

For many-to-many networks within a hierarchical structure (gene hierarchies, taxonomies), edge bundling routes edges along the tree backbone, dramatically reducing clutter.

```r
library(ggraph)
ggraph(graph, layout = 'dendrogram', circular = TRUE) +
    geom_conn_bundle(data = get_con(from = from_idx, to = to_idx),
                     alpha = 0.4, tension = 0.8, edge_colour = 'grey60') +
    geom_node_point() +
    theme_void()
```

## NetworkX + matplotlib — Standard Static

**Goal:** Render a PPI network with node size proportional to degree, color by community, and edge width by interaction confidence.

**Approach:** Compute layout once with fixed seed; compute attributes (degree, community); render in layers via `nx.draw_networkx_*` functions for fine control.

```python
import networkx as nx
import matplotlib.pyplot as plt
from networkx.algorithms.community import greedy_modularity_communities
import numpy as np

# Layout with fixed seed for reproducibility
pos = nx.spring_layout(G, k=1.5, seed=42)

# Compute attributes
degrees = dict(G.degree())
communities = list(greedy_modularity_communities(G))
node_to_community = {n: i for i, c in enumerate(communities) for n in c}

# Sizes scaled to degree
sizes = [100 + degrees[n] * 50 for n in G.nodes()]
colors = [node_to_community[n] for n in G.nodes()]

# Render in layers
fig, ax = plt.subplots(figsize=(10, 8))
nx.draw_networkx_edges(G, pos, alpha=0.3, edge_color='grey', width=0.5, ax=ax)
nodes = nx.draw_networkx_nodes(G, pos, node_size=sizes, node_color=colors,
                                cmap='tab20', edgecolors='black', linewidths=0.5, ax=ax)
# Label only high-degree (hub) nodes
hubs = [n for n in G.nodes() if degrees[n] >= 10]
nx.draw_networkx_labels(G, pos, labels={n: n for n in hubs}, font_size=8, ax=ax)
ax.axis('off')
plt.tight_layout()
plt.savefig('network.pdf', bbox_inches='tight', dpi=300)
```

## PyVis — Interactive HTML

```python
from pyvis.network import Network

net = Network(height='700px', width='100%', bgcolor='white', font_color='black')
net.from_nx(G)

# Per-node styling
for node in G.nodes():
    net.get_node(node)['size'] = 10 + degrees[node] * 5
    net.get_node(node)['color'] = palette[node_to_community[node] % len(palette)]
    net.get_node(node)['title'] = f'{node}\nDegree: {degrees[node]}'

net.toggle_physics(True)
net.set_options('{"physics": {"forceAtlas2Based": {"gravitationalConstant": -50}}}')
net.save_graph('network.html')
```

PyVis wraps vis.js; produces standalone HTML. Suitable for supplementary HTML; not for static journal figure.

## Cytoscape Automation (py4cytoscape)

```python
import py4cytoscape as p4c
# Cytoscape desktop must be running

p4c.create_network_from_networkx(G, title='PPI')
p4c.layout_network('force-directed')

# Custom style
style_name = 'DegreeStyle'
p4c.create_visual_style(style_name)
p4c.set_node_size_mapping('degree', [1, 5, 20], [30, 60, 120],
                            mapping_type='c', style_name=style_name)
p4c.set_node_color_mapping('degree', [1, 10, 20], ['#FFFFCC', '#FD8D3C', '#BD0026'],
                             mapping_type='c', style_name=style_name)
p4c.set_visual_style(style_name)

# Export
p4c.export_image('network.pdf', type='PDF')
```

Cytoscape is the desktop reference for publication-grade biological networks; py4cytoscape exposes script control from Python or R (via cyREST).

## Per-Method Failure Modes

### Layout positions interpreted as biology

**Trigger:** "Cluster A is between cluster B and C, so it's transitional."

**Mechanism:** Force-directed positions are optimization artifacts.

**Symptom:** Conclusion contradicts orthogonal evidence; not replicable with different seed.

**Fix:** Frame conclusions in terms of edge existence and node degree only. For trajectory claims, use the relevant time-series tool (RNA velocity, pseudotime), not the network layout.

### Layout differs across runs

**Trigger:** No random seed set.

**Mechanism:** Spring / FA2 are stochastic.

**Symptom:** Rerun produces a visibly different figure.

**Fix:** `seed=42` (NetworkX) or `set.seed(42)` (R igraph) before layout.

### Comparing two networks with different layouts

**Trigger:** `spring_layout` run separately for two conditions.

**Mechanism:** Layouts differ; visual change conflated with biological change.

**Symptom:** Concludes "this protein moved" when only the layout moved.

**Fix:** Compute layout on the union network OR pass the same `pos` to both renders.

### Hairball — too many edges with poor layout

**Trigger:** Dense network with default force-directed; >5k edges.

**Mechanism:** Edge crossings dominate; no structure visible.

**Symptom:** Visual is a uniform dense blob.

**Fix:** Hierarchical edge bundling (Holten 2006), filter to top-confidence edges, use a hive plot, OR raster with Datashader.

### Hub labels obscure non-hub structure

**Trigger:** Labeling every node in a network with >100 nodes.

**Mechanism:** Labels overlap; visual clutter.

**Symptom:** Cannot read any labels; figure too busy.

**Fix:** Label only hubs (degree > threshold) OR genes of interest. Use ggrepel-style repulsion in matplotlib via adjustText.

### Edge widths uniform when weights are meaningful

**Trigger:** Default `width=1` for all edges.

**Mechanism:** Edge attribute (correlation, confidence, weight) not encoded.

**Symptom:** Reader cannot tell strong from weak interactions.

**Fix:** `width = [G[u][v]['weight'] for u, v in G.edges()]` with normalization to visible range.

### PyVis HTML size explodes for large networks

**Trigger:** `net.from_nx(G)` with 10000+ nodes.

**Mechanism:** Embedded JavaScript file balloons; browser hangs.

**Symptom:** HTML file 100+ MB; doesn't render.

**Fix:** For large networks switch to Datashader or Cytoscape with Cytoscape.js for web; PyVis is for <2000 nodes.

## Reconciliation: When Layouts Disagree

| Pattern | Cause | Action |
|---------|-------|--------|
| Two layouts of same network look different | Different algorithm or seed | Standardize; report algorithm + seed |
| Cytoscape and NetworkX disagree | Cytoscape default = grid; NetworkX = spring | Pick one; document |
| Communities don't separate visually | Layout doesn't preserve community structure | Use spectral layout OR color-code communities; do not rely on positional separation |
| Same nodes "move" between conditions | Layout re-computed | Reuse layout from union network |

## Quantitative Thresholds

| Threshold | Value | Source |
|-----------|-------|--------|
| Max edges for spring layout legibility | ~2000 | Practical |
| Max nodes for PyVis HTML | ~2000 | Browser memory |
| When to bundle edges | >5000 edges or many-to-many | Holten 2006 |
| When to use Datashader | >50000 nodes or edges | Standard |
| Min degree for labeling | depends; 5-10 typical | Practical |
| Random seed | always set (42 is convention) | Reproducibility |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| Layout differs across runs | No seed | Always `seed=42` |
| "Distance between clusters" interpreted | Layout artifact | Frame conclusions on edges/degree only |
| Hairball | Dense + force-directed | Bundle / hive / filter / Datashader |
| Two networks' layouts not comparable | Computed separately | Use union network layout |
| Edge widths uniform | Default | Encode weight |
| Label clutter | All nodes labeled | Hubs only |
| PyVis 100MB HTML | Too large for PyVis | Switch to Cytoscape.js / Datashader |

## References

- Csardi G, Nepusz T. 2006. The igraph software package for complex network research. *InterJournal Complex Systems* 1695.
- Fruchterman TMJ, Reingold EM. 1991. Graph drawing by force-directed placement. *Softw Pract Exp* 21(11):1129-1164.
- Hagberg A, Schult D, Swart P. 2008. Exploring network structure, dynamics, and function using NetworkX. *Proc 7th Python in Science Conference (SciPy 2008)*.
- Holten D. 2006. Hierarchical edge bundles: visualization of adjacency relations in hierarchical data. *IEEE TVCG* 12(5):741-748.
- Jacomy M, Venturini T, Heymann S, Bastian M. 2014. ForceAtlas2, a continuous graph layout algorithm for handy network visualization designed for the Gephi software. *PLoS ONE* 9(6):e98679.
- Krzywinski M, Birol I, Jones SJM, Marra MA. 2012. Hive plots—rational approach to visualizing networks. *Brief Bioinform* 13(5):627-644.
- Pedersen T. 2024. ggraph (CRAN). https://ggraph.data-imaginist.com
- Shannon P, et al. 2003. Cytoscape: a software environment for integrated models of biomolecular interaction networks. *Genome Res* 13(11):2498-2504.

## Related Skills

- gene-regulatory-networks/coexpression-networks - Build the network to visualize
- database-access/interaction-databases - Fetch PPI data
- data-visualization/multipanel-figures - Combine network with other plots
- data-visualization/color-palettes - Community / module color schemes
- single-cell/cell-communication - Cell-cell interaction networks
<!-- END FILE: data-visualization/network-visualization/SKILL.md -->

## 子目录：data-visualization/oncoprint-mutation-matrices

<!-- BEGIN FILE: data-visualization/oncoprint-mutation-matrices/SKILL.md -->
---
name: bio-data-visualization-oncoprint-mutation-matrices
description: Build OncoPrint and co-mutation matrix plots from somatic-variant cohorts using ComplexHeatmap, maftools, and comut.py with alteration-type stacking, sample ordering by mutational burden, mutual-exclusivity overlays, and clinical annotation tracks. Use when visualizing per-sample mutation patterns across recurrent driver genes, comparing alteration classes, or identifying mutually-exclusive / co-occurring driver pairs.
tool_type: mixed
primary_tool: ComplexHeatmap
---

## Version Compatibility

Reference examples tested with: ComplexHeatmap 2.18+, maftools 2.18+, comut 0.0.3+, MAFtools requires R 4.0+; comut.py requires pandas 2.0+, matplotlib 3.8+.

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- R: `packageVersion('<pkg>')` then `?function_name`

If code throws ImportError, AttributeError, or TypeError, introspect the installed package and adapt the example to match the actual API rather than retrying.

# OncoPrint and Mutation Matrix Plots

**"Plot mutations across a cohort"** -> Render a gene-by-sample matrix where each cell stacks colored rectangles encoding alteration class (missense, truncating, splice, copy-gain, copy-loss, fusion). Sort samples by burden, optionally split by clinical group, and overlay co-mutation / mutual-exclusivity annotations. OncoPrint (Cerami 2012 *Cancer Discov* 2:401; canonical at cBioPortal) is the genre-defining visualization.

- R: `ComplexHeatmap::oncoPrint`, `maftools::oncoplot`
- Python: `comut.CoMut`, `cbioportal`-style implementations

## The Single Most Important Modern Insight -- Cell Stacking Encodes Multiple Alterations Per Cell

OncoPrint differs from a generic heatmap because each cell can encode multiple alterations simultaneously through *stacked* rectangles. A patient with both a missense and a copy-gain in TP53 shows one cell with two overlapping colored rectangles (e.g., green diamond inside red square). This stacking is the whole point — it preserves the multi-modal alteration landscape that flattening to a single category destroys.

In ComplexHeatmap's `oncoPrint`, the `alter_fun` argument is the rendering specification: a named list of functions, one per alteration class, each drawing its rectangle inside the cell. Get this right and the figure works; get it wrong and overlapping alterations are invisible.

## Decision Tree by Cohort and Question

| Question | Sort by | Display |
|----------|---------|---------|
| Which genes are most altered? | Gene frequency (default) | Bar above samples (sample TMB); bar right of genes (gene frequency) |
| Per-patient burden patterns | Sample burden | TMB bar on top; sample-name labels |
| Subtype-driver enrichment | Clinical group then burden | `column_split` by group; per-group frequency right bar |
| Mutual exclusivity (BRAF vs NRAS) | Custom (alphabetic-by-mutation pattern) | Memo sort; overlay log10(OR) heatmap |
| Co-occurrence (TP53 + MYC) | Custom | Same pattern; positive OR coloring |
| Driver vs passenger comparison | Two panels | Concatenate two oncoPrints horizontally |

## ComplexHeatmap::oncoPrint -- Canonical Implementation

**Goal:** Render a cohort mutation matrix with stacked alteration-class encoding, sample annotations, and a sample-sorted, gene-frequency-ranked layout.

**Approach:** Convert the MAF/variant table to a gene-by-sample matrix of `;`-delimited alteration strings; define `alter_fun` rendering one rectangle per class; pass to `oncoPrint()` with column annotations.

```r
library(ComplexHeatmap)
library(circlize)

# Input: matrix where each cell is a string like 'Missense;Amp' or '' for no alteration
# Rows = genes; columns = samples

# Color per alteration class
col <- c('Missense'   = '#56B4E9',
         'Truncating' = '#000000',
         'Splice'     = '#CC79A7',
         'Amp'        = '#D55E00',
         'HomDel'     = '#0072B2',
         'Fusion'     = '#009E73')

# alter_fun -- one function per class, each drawing inside the cell
alter_fun <- list(
    background = function(x, y, w, h)
        grid.rect(x, y, w - unit(0.5, 'mm'), h - unit(0.5, 'mm'),
                  gp = gpar(fill = '#EEEEEE', col = NA)),
    Amp = function(x, y, w, h)
        grid.rect(x, y, w - unit(0.5, 'mm'), h - unit(0.5, 'mm'),
                  gp = gpar(fill = col['Amp'], col = NA)),
    HomDel = function(x, y, w, h)
        grid.rect(x, y, w - unit(0.5, 'mm'), h - unit(0.5, 'mm'),
                  gp = gpar(fill = col['HomDel'], col = NA)),
    Missense = function(x, y, w, h)
        grid.rect(x, y, w - unit(0.5, 'mm'), h * 0.5,
                  gp = gpar(fill = col['Missense'], col = NA)),
    Truncating = function(x, y, w, h)
        grid.rect(x, y, w - unit(0.5, 'mm'), h * 0.33,
                  gp = gpar(fill = col['Truncating'], col = NA)),
    Splice = function(x, y, w, h)
        grid.rect(x, y, w - unit(0.5, 'mm'), h * 0.25,
                  gp = gpar(fill = col['Splice'], col = NA)),
    Fusion = function(x, y, w, h)
        grid.points(x, y, pch = 17, size = unit(2, 'mm'),
                    gp = gpar(col = col['Fusion'])))

# Clinical column annotation
ha_clin <- HeatmapAnnotation(
    Subtype = clinical$subtype,
    Stage   = clinical$stage,
    col = list(Subtype = c(Luminal='#0072B2', Basal='#D55E00', HER2='#009E73'),
               Stage   = c(I='#FFFFCC', II='#FED976', III='#FD8D3C', IV='#BD0026')))

oncoPrint(mat,
          alter_fun = alter_fun,
          col = col,
          top_annotation = ha_clin,
          column_title = 'TCGA-BRCA mutation landscape',
          row_names_gp = gpar(fontsize = 8),
          pct_gp = gpar(fontsize = 7),
          show_pct = TRUE,
          remove_empty_columns = FALSE,
          remove_empty_rows = FALSE)
```

## maftools::oncoplot -- Faster Onboarding

For TCGA-style MAF files, `maftools::oncoplot` is the lower-friction option:

```r
library(maftools)
maf <- read.maf(maf = 'tcga.maf', clinicalData = clinical)
oncoplot(maf = maf,
         top = 20,                            # top 20 mutated genes
         clinicalFeatures = c('Subtype', 'Stage'),
         annotationColor = list(Subtype = c(Luminal='#0072B2', Basal='#D55E00'),
                                 Stage = c(I='#FFFFCC', IV='#BD0026')),
         sortByAnnotation = TRUE,
         removeNonMutated = FALSE)
```

maftools defaults handle alteration-class colors, sample sorting, and percentage bars automatically. Customization is more limited than ComplexHeatmap.

## Mutual Exclusivity and Co-Occurrence

```r
# maftools provides somaticInteractions
si <- somaticInteractions(maf = maf, top = 20,
                          pvalue = c(0.05, 0.01),
                          fontSize = 0.7)
# Plot returns a matrix of -log10(p) with sign by direction (+ co-occur, - mutex)
```

Mutual-exclusivity testing on small cohorts (N < 50) is underpowered; reported "significant" mutex on n=20 with 2 mutations each is uninterpretable. Aggregate to larger cohorts (TCGA + ICGC pan-cancer) or report effect size with CI rather than p-value.

**Fisher exact vs DISCOVER:** standard 2x2 Fisher tests sample-mutation pairs, ignoring per-gene mutation rate background. DISCOVER (Canisius 2016 *Genome Biol* 17:261) models per-tumor mutation probability and is preferred for pan-cancer analyses where mutation rate varies 100× across samples.

## comut.py -- Python Equivalent

```python
import comut
import pandas as pd

# Long-format: columns = sample, category (gene), value (alteration class)
toy_comut = comut.CoMut()
toy_comut.add_categorical_data(
    data=mutation_long_df,
    name='Mutations',
    category_order=top_genes,
    value_order=['Truncating', 'Missense', 'Splice', 'Amp', 'HomDel'],
    mapping={'Truncating': '#000000', 'Missense': '#56B4E9',
             'Splice': '#CC79A7', 'Amp': '#D55E00', 'HomDel': '#0072B2'})

toy_comut.add_categorical_data(
    data=clinical_long_df,
    name='Subtype',
    mapping={'Luminal': '#0072B2', 'Basal': '#D55E00'})

toy_comut.add_continuous_data(
    data=tmb_long_df,
    name='TMB',
    mapping='viridis',
    value_range=(0, 30))

toy_comut.plot_comut(figsize=(12, 8))
toy_comut.figure.savefig('comut.pdf', dpi=300, bbox_inches='tight')
```

## Per-Method Failure Modes

### Alterations flattened to a single class

**Trigger:** Reducing each cell to a single most-severe alteration, losing the stack.

**Mechanism:** Loses the multi-alteration biology (e.g., MYC amp + missense in TP53).

**Symptom:** OncoPrint looks like a simple heatmap; co-occurring multi-class events invisible.

**Fix:** Build the cell as `;`-separated alteration string; define `alter_fun` for each class.

### Sample sort by gene 1 frequency only

**Trigger:** Default `oncoPrint` sorts samples by altered-gene-1 status; weakens the "memo sort" pattern.

**Mechanism:** True OncoPrint uses memoSort (Cerami 2012) which sorts by the binary altered-or-not pattern across the top genes.

**Symptom:** Samples with the same alteration profile are not adjacent; "staircase" pattern lost.

**Fix:** ComplexHeatmap `oncoPrint` uses memoSort by default; do NOT override `column_order` unless intentional.

### Showing only mutated samples (`remove_empty_columns = TRUE`)

**Trigger:** Default in some implementations.

**Mechanism:** Drops samples with no mutations in the displayed genes — but those samples ARE part of the cohort.

**Symptom:** Sample count differs from cohort N; denominator-based percentages wrong.

**Fix:** `remove_empty_columns = FALSE` to preserve all samples; percentages now reflect true cohort fraction.

### Hypermutators dominate visual

**Trigger:** Cohort with 1-2 POLE-mutant or MSI-H samples; TMB bar saturates.

**Mechanism:** Hypermutator TMB is 10-100× the typical sample.

**Symptom:** All other samples' TMB bars are invisible; one column dominates.

**Fix:** Log-transform the TMB annotation: `anno_barplot(log10(tmb + 1))`; OR cap with `ylim`.

### Mutex/co-occurrence p-values overinterpreted on small cohorts

**Trigger:** Fisher exact test on N < 50 with low mutation counts.

**Mechanism:** With 2 mutations vs 3 mutations in 20 samples, all p-values are dominated by noise.

**Symptom:** "Significant mutex" claim from a tiny pilot.

**Fix:** Aggregate to ≥100 samples for credible mutex; use DISCOVER (Canisius 2016) instead of Fisher when mutation rate varies 100× across samples.

## Small-Cohort Regime (N = 20-50)

For rare-cancer cohorts where N < 50, the standard OncoPrint + Fisher mutex pipeline is statistically uninterpretable:

| Action | What to do |
|--------|------------|
| Report per-gene frequencies | Use exact-binomial CI (Clopper-Pearson via `binom.test`) — Wald CI is invalid at low frequency |
| Do NOT report mutex p-values | Fisher exact on 2x2 with cell counts ≤ 5 has no power; the "significant" mutex finding is noise |
| Hypothesis generation only | Pool with TCGA Pan-Cancer + ICGC for credible mutex; treat the cohort as the *replication* not the discovery |
| Co-occurrence reporting | OR with Haldane-Anscombe 0.5 correction for zero cells; report alongside cohort N |

Show the OncoPrint for visual transparency, but the per-gene-frequency *table* (with exact-binomial CIs) is the load-bearing scientific output, not the mutex test.

## Reconciliation: When Implementations Differ

| Pattern | Cause | Action |
|---------|-------|--------|
| ComplexHeatmap and maftools show different sample orders | Different memoSort defaults | Specify `sortByAnnotation` explicitly; report sort criterion in caption |
| Percentage labels differ | `remove_empty_columns = TRUE` vs FALSE | Document denominator (cohort-N vs altered-N) |
| Some alterations missing from a sample | Filtering: silent SNVs, low VAF | Document filtering criteria upstream |

## Quantitative Thresholds

| Threshold | Value | Source |
|-----------|-------|--------|
| Cohort N for valid mutex | ≥100 (pan-cancer); ≥50 (single-cohort with effect-size focus) | Common practice |
| Display top genes | 10-25 in single panel | More creates visual clutter |
| Sample N for OncoPrint | 50-1000 (above: switch to summary panel) | Visualization practical |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| Co-occurring multi-class events invisible | Single-class flattening | Use `;`-separated cells + alter_fun list |
| Sample order doesn't show staircase | column_order override | Trust default memoSort |
| Sample count differs from cohort | `remove_empty_columns = TRUE` | Set to FALSE |
| TMB bar dominated by 1-2 samples | Hypermutators on linear scale | log10 + 1 transform |
| Mutex p-values on N=20 | Underpowered | Aggregate cohorts; use DISCOVER |
| Gene frequency right-bar mismatches percentages | Denominator definition | Document cohort-N vs altered-N |

## References

- Canisius S, Martens JWM, Wessels LFA. 2016. A novel independence test for somatic alterations in cancer shows that biology drives mutual exclusivity but chance explains most co-occurrence. *Genome Biol* 17:261.
- Cerami E, Gao J, Dogrusoz U, et al. 2012. The cBio cancer genomics portal: an open platform for exploring multidimensional cancer genomics data. *Cancer Discov* 2(5):401-404.
- Gao J, Aksoy BA, Dogrusoz U, et al. 2013. Integrative analysis of complex cancer genomics and clinical profiles using the cBioPortal. *Sci Signal* 6(269):pl1.
- Gu Z, Eils R, Schlesner M. 2016. Complex heatmaps reveal patterns and correlations in multidimensional genomic data. *Bioinformatics* 32(18):2847-2849.
- Mayakonda A, Lin DC, Assenov Y, Plass C, Koeffler HP. 2018. Maftools: efficient and comprehensive analysis of somatic variants in cancer. *Genome Res* 28(11):1747-1756.

## Related Skills

- data-visualization/heatmaps-clustering - Generic heatmap underlying oncoPrint
- data-visualization/lollipop-protein-maps - Per-gene mutation maps on protein domains
- data-visualization/color-palettes - Alteration-class palette selection
- clinical-databases/variant-prioritization - Filter variants before OncoPrint
- variant-calling/variant-annotation - Annotate consequences upstream
- copy-number/cnv-annotation - Integrate CNV calls into the oncoprint
<!-- END FILE: data-visualization/oncoprint-mutation-matrices/SKILL.md -->

## 子目录：data-visualization/sequence-logos

<!-- BEGIN FILE: data-visualization/sequence-logos/SKILL.md -->
---
name: bio-data-visualization-sequence-logos
description: Build sequence logos from aligned DNA, RNA, or protein motifs using ggseqlogo (R), Logomaker (Python), or WebLogo with explicit bits vs probability encoding, background-frequency correction, custom alphabets, and multi-logo stacking. Use when visualizing motif PWMs (TF binding, splice sites, CRISPR spacers), aligned-position composition, or comparing two motif sets.
tool_type: mixed
primary_tool: ggseqlogo
---

## Version Compatibility

Reference examples tested with: ggseqlogo 0.2 (CRAN; per Wagih 2017), Logomaker 0.8+ (Python), WebLogo 3.7+ (CLI), Biopython 1.83+ (motif parsing), MEME suite 5.5+.

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- R: `packageVersion('<pkg>')` then `?function_name`

If code throws ImportError, AttributeError, or TypeError, introspect the installed package and adapt the example to match the actual API rather than retrying.

# Sequence Logos

**"Plot a sequence motif"** -> Render a per-position stack of letters whose total height encodes information content (Schneider-Stephens 1990 *Nucleic Acids Res* 18:6097) and individual letter height is proportional to base/aa frequency. The information-content encoding makes conserved positions visually tall and variable positions visually short — the visual is *the conservation profile*.

- R: `ggseqlogo::ggseqlogo` (Wagih 2017 *Bioinformatics* 33:3645)
- Python: `logomaker.Logo`
- CLI: `weblogo` (Crooks 2004 *Genome Res* 14:1188)

## The Single Most Important Modern Insight -- Bits vs Probability Are Different Visualizations

A sequence logo can encode each position as **bits** (information content) or **probability** (raw frequency). They look superficially similar; they communicate different things.

- **Bits (Schneider-Stephens 1990):** position height = `R = log2(K) − H(p)` where K=4 for DNA, H is Shannon entropy. Maximum 2 bits for DNA, 4.3 bits for protein. A fully conserved position is 2 bits; a uniform position is 0. This is the canonical motif encoding.
- **Probability:** position height = 1.0; letter height = frequency. Every position has the same total height. Cannot distinguish "conserved A" from "variable" — both can show 100% A at a position.
- **EDLogo (enrichment-depletion):** Dey et al. 2018 — uses log-odds of observed vs background, supporting depleted-residue display.

**Default to bits unless a specific reason exists otherwise.** Bits is what reviewers expect to see for a TF binding site, splice site, or CRISPR spacer composition.

## Decision Tree by Use Case

| Use case | Encoding | Background | Tool |
|----------|----------|------------|------|
| TF binding motif (JASPAR/CIS-BP PWM) | bits | uniform OR genome composition | ggseqlogo, Logomaker |
| Splice-site motif (5'SS, 3'SS) | bits | uniform | ggseqlogo |
| CRISPR sgRNA position-composition | probability | – | logomaker (custom alphabet) |
| Protein motif (kinase substrate) | bits | proteome composition | Logomaker (matrix_type='counts') |
| Alignment-conservation cartoon | bits OR probability | depends on intent | WebLogo |
| Differential motif (TF-A vs TF-B) | EDLogo log-odds | TF-B | Logomaker (matrix_type='weight') |

## ggseqlogo (R) -- Canonical Bioinformatics Default

**Goal:** Render a sequence motif as a per-position letter stack whose total height encodes information content (Schneider-Stephens 1990) and individual letter heights reflect frequency, optionally corrected for genome background.

**Approach:** Pass a PWM matrix (rows = letters, columns = positions) or vector of aligned same-length sequences to `ggseqlogo()` with `method = 'bits'` and explicit `bg_freq` for the relevant genome composition; stack multiple motifs as a named list.

```r
library(ggseqlogo)

# Input: PWM matrix (rows = positions, columns = nucleotides A/C/G/T)
# or aligned sequence vector

# From a vector of aligned sequences (same length)
seqs <- c('ATGCAA', 'ATGCAC', 'ATGCAG', 'ATGCAT', 'ACGCAA')
ggseqlogo(seqs, method = 'bits')

# From a PWM matrix (probability or counts)
pwm <- matrix(c(0.7, 0.1, 0.1, 0.1,
                0.1, 0.7, 0.1, 0.1,
                0.4, 0.1, 0.4, 0.1), ncol = 3,
              dimnames = list(c('A', 'C', 'G', 'T'), NULL))
ggseqlogo(pwm, method = 'bits')           # 'bits' OR 'probability'

# Multiple logos stacked (e.g., compare TF-A and TF-B)
ggseqlogo(list(TFA = seqs_a, TFB = seqs_b),
          method = 'bits',
          col_scheme = 'nucleotide')
```

```r
# Custom color scheme (protein motif, kinase substrate)
ggseqlogo(protein_pwm,
          method = 'bits',
          seq_type = 'aa',                      # auto-detected usually
          col_scheme = make_col_scheme(
              chars = c('S','T','Y','K','R','H','D','E','A','V','L','I','M'),
              cols  = c('#D55E00','#D55E00','#D55E00',          # phospho-acceptors
                        '#0072B2','#0072B2','#0072B2',          # basic
                        '#CC79A7','#CC79A7',                    # acidic
                        '#009E73','#009E73','#009E73','#009E73','#009E73')))  # hydrophobic
```

## Logomaker (Python) -- Most Flexible

```python
import logomaker
import pandas as pd

# Counts matrix (rows = position, columns = ACGT)
counts_df = pd.DataFrame({'A': [10, 0, 5, 8],
                          'C': [0, 8, 5, 1],
                          'G': [0, 2, 0, 0],
                          'T': [0, 0, 0, 1]})

# Convert counts -> information (bits)
ic_df = logomaker.transform_matrix(counts_df,
                                    from_type='counts',
                                    to_type='information',
                                    background=[0.25] * 4)    # uniform; pass real background for corrected IC

import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(6, 2))
logo = logomaker.Logo(ic_df,
                      color_scheme='classic',           # 'NajafabadiEtAl2017' for protein
                      shade_below=0.5,
                      fade_below=0.5,
                      font_name='Arial Rounded MT Bold')
logo.style_xticks(rotation=0)
logo.ax.set_ylabel('Bits')
```

```python
# Weight matrix (signed) -- enrichment vs depletion
weight_df = logomaker.transform_matrix(counts_df,
                                        from_type='counts',
                                        to_type='weight',
                                        background=genome_composition)
logo = logomaker.Logo(weight_df, color_scheme='classic',
                       flip_below=True)                  # depleted letters below axis
```

## WebLogo (CLI / web)

```bash
weblogo --format pdf --sequence-type dna \
        --color-scheme classic --units bits \
        --composition equiprobable \
        --fineprint '' \
        --size large \
        < aligned.fasta > logo.pdf
```

WebLogo (Crooks 2004) is the original; supports many formats and is scriptable. For reproducible figures, prefer ggseqlogo or Logomaker (programmatic, easier to integrate with multi-panel figures).

## Background Composition Correction

The bits encoding assumes a uniform background by default. For genome-derived motifs, the background should match the genome:

- Human genome: A=0.29, C=0.21, G=0.21, T=0.29 (approx)
- GC-rich genomes (Streptomyces): A=0.18, C=0.32, G=0.32, T=0.18

Without correction, a motif preferring GC in a genome where GC is rare overestimates information; conversely, an A-rich motif in an AT-rich genome underestimates.

```r
# ggseqlogo: pass `bg_freq`
ggseqlogo(pwm, method = 'bits',
          bg_freq = c(A = 0.29, C = 0.21, G = 0.21, T = 0.29))
```

```python
logomaker.transform_matrix(counts_df, from_type='counts', to_type='information',
                            background=[0.29, 0.21, 0.21, 0.29])
```

## Per-Method Failure Modes

### Probability encoding mistaken for bits

**Trigger:** Default `method = 'probability'` in some implementations.

**Mechanism:** Every position has total height 1; visually flat with all letters same total.

**Symptom:** Reviewer asks "why doesn't the logo show conservation gradient?"

**Fix:** Use `method = 'bits'` for the standard motif encoding.

### Background uniform when genome composition matters

**Trigger:** Uniform `bg_freq = c(0.25, 0.25, 0.25, 0.25)` for a non-uniform genome.

**Mechanism:** Information content overestimates conservation for preferred bases.

**Symptom:** Reported motif looks more conserved than it actually is.

**Fix:** Pass genome composition to `bg_freq` / `background` parameter.

### PWM rows/columns reversed

**Trigger:** Input matrix in samples-as-rows convention; logomaker expects positions-as-rows.

**Mechanism:** Logo renders the wrong dimension as "position."

**Symptom:** Logo has letter count = number of input rows, not motif length.

**Fix:** Transpose the matrix; verify with `print(matrix.shape)` before plotting.

### Custom alphabet not recognized

**Trigger:** RNA logo with `U` instead of `T`; protein logo with `J` or `Z`.

**Mechanism:** ggseqlogo and logomaker auto-detect alphabet from input; unusual characters may fail.

**Symptom:** Letters render as boxes or missing entirely.

**Fix:** Explicit `seq_type = 'rna'` (ggseqlogo) or pass custom color scheme (Logomaker).

### Aligned sequences of unequal length

**Trigger:** Vector of motif instances with different lengths.

**Mechanism:** Most tools require equal-length input.

**Symptom:** Error or only first N positions plotted.

**Fix:** Pre-align (MEME / TOMTOM) or trim to a common length.

### Logo for too few input sequences

**Trigger:** PWM from N=5 sequences plotted as if N=500.

**Mechanism:** Information content has small-N bias; even random sequences look "conserved" at N=5.

**Symptom:** Logo appears more meaningful than the input warrants.

**Fix:** Compute small-sample correction (Schneider 1986; standard in MEME); annotate N in caption; require N ≥ 20 for credible motif.

### Stacked logos with different alphabets compared

**Trigger:** Stacking a DNA logo above a protein logo for visual comparison.

**Mechanism:** Maximum information content differs (2 bits DNA vs 4.3 bits protein); y-axes are not comparable.

**Symptom:** Apparent "weaker" protein logo because of higher possible max.

**Fix:** Normalize both to fractional information (0-1) OR present separately.

## Reconciliation: When Logos Differ

| Pattern | Cause | Action |
|---------|-------|--------|
| ggseqlogo vs Logomaker show different heights | Different default backgrounds (uniform vs explicit) | Standardize background; recompute |
| WebLogo vs Logomaker differ at low-conservation positions | Small-sample correction differs | Use consistent N; report sample-corrected IC |
| JASPAR vs MEME PWM look different | JASPAR uses observed counts; MEME has Dirichlet prior | Document source; cite version |

## Quantitative Thresholds

| Threshold | Value | Source |
|-----------|-------|--------|
| Max IC per DNA position | 2 bits | Schneider-Stephens 1990 |
| Max IC per protein position | 4.32 bits (log2(20)) | Schneider-Stephens 1990 |
| Min N for credible motif | ≥ 20 instances; ≥ 100 ideal | Common practice |
| Small-sample correction | Schneider 1986 entropy correction | MEME default; ggseqlogo via small-N tools |
| TF binding-site length typical | 6-20 bp | Biology |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| Logo flat with all positions = 1 | Probability mode | Switch to bits |
| Motif looks too conserved | Uniform bg in non-uniform genome | Pass `bg_freq` |
| Letter count = N samples not motif length | Matrix transposed | Verify shape |
| RNA U renders as box | Alphabet not recognized | `seq_type = 'rna'` |
| Logos at different scales overlaid | Different alphabets | Normalize OR separate |
| Logo from N=5 looks meaningful | Small-sample bias | Require N>=20; annotate |

## References

- Crooks GE, Hon G, Chandonia JM, Brenner SE. 2004. WebLogo: a sequence logo generator. *Genome Res* 14(6):1188-1190.
- Dey KK, Xie D, Stephens M. 2018. A new sequence logo plot to highlight enrichment and depletion. *bioRxiv*.
- Schneider TD. 1986. Information content of binding sites on nucleotide sequences. *J Mol Biol* 188(3):415-431.
- Schneider TD, Stephens RM. 1990. Sequence logos: a new way to display consensus sequences. *Nucleic Acids Res* 18(20):6097-6100.
- Tareen A, Kinney JB. 2020. Logomaker: beautiful sequence logos in Python. *Bioinformatics* 36(7):2272-2274.
- Wagih O. 2017. ggseqlogo: a versatile R package for drawing sequence logos. *Bioinformatics* 33(22):3645-3647.

## Related Skills

- chip-seq/motif-analysis - Discover the PWM that becomes the logo
- atac-seq/footprinting - Footprinting motifs to visualize
- clip-seq/clip-motif-analysis - CLIP-derived motifs
- alignment/multiple-alignment - Aligned sequences as logo input
- data-visualization/color-palettes - Custom alphabet color schemes
<!-- END FILE: data-visualization/sequence-logos/SKILL.md -->

## 子目录：data-visualization/statistical-annotation

<!-- BEGIN FILE: data-visualization/statistical-annotation/SKILL.md -->
---
name: bio-data-visualization-statistical-annotation
description: Add p-value brackets, significance asterisks, and effect-size annotations to distribution plots using ggpubr, ggsignif, and statannotations with correct test selection (parametric vs non-parametric vs paired), multiple-testing adjustment, and rendering of negative results. Use when a boxplot/violin/raincloud needs in-figure statistical comparisons between groups.
tool_type: mixed
primary_tool: ggpubr
---

## Version Compatibility

Reference examples tested with: ggpubr 0.6+, ggsignif 0.6+, rstatix 0.7+, statannotations 0.6+ (Python), seaborn 0.13+.

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('<pkg>')` then `?function_name`
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed package and adapt the example to match the actual API rather than retrying.

# Statistical Annotation

**"Add p-values to my plot"** -> Render pairwise group comparisons as brackets with the correct statistical test (parametric vs non-parametric, paired vs unpaired, independent vs nested), adjusted for multiple testing, with rendering of significance as either numerical p OR asterisks. The choices that matter: which test is appropriate for the data, what multiple-testing adjustment applies, and whether to show n.s. (non-significant) results.

- R: `ggpubr::stat_compare_means`, `ggsignif::geom_signif`, `rstatix::t_test`/`wilcox_test`
- Python: `statannotations.Annotator`, `scipy.stats` directly

## The Single Most Important Modern Insight -- The Test Must Match the Data

Tool defaults are NOT data-appropriate. `ggpubr::stat_compare_means(method='t.test')` uses Welch's two-sample t-test assuming approximate normality and unequal variances. This is wrong when:

1. **Data are non-normal and N is small (<30):** use Mann-Whitney U (`method='wilcox.test'`).
2. **Data are paired:** use paired t-test or paired Wilcoxon (`paired = TRUE`).
3. **Comparing >2 groups:** ANOVA / Kruskal-Wallis with post-hoc, not all-pairs t-test (multiple-testing penalty).
4. **Data are nested (cells within patients, replicates within samples):** linear mixed model, NOT pairwise test.

The bracket-and-asterisk visual is the same; the underlying statistics are not. Choose the test deliberately.

## Decision Tree for Test Selection

| Question | Recommended test | Function |
|----------|------------------|----------|
| 2 unpaired groups, normal, N≥30 | Welch t-test | `t.test()`, `stat_compare_means(method='t.test')` |
| 2 unpaired groups, non-normal or small N | Mann-Whitney U (Wilcoxon rank-sum) | `wilcox.test()`, `stat_compare_means(method='wilcox.test')` |
| 2 paired groups | Paired t-test OR Wilcoxon signed-rank | `paired = TRUE` |
| 3+ groups, normal | One-way ANOVA + Tukey HSD post-hoc | `aov()`, `TukeyHSD()` |
| 3+ groups, non-normal | Kruskal-Wallis + Dunn post-hoc | `kruskal.test()`, `dunn.test()` |
| Nested data (cells in patients) | Linear mixed model | `lme4::lmer()` |
| Time-course / repeated measures | Repeated-measures ANOVA OR LMM | `nlme::lme()` |
| Two-way factorial | Two-way ANOVA + interaction term | `aov(y ~ a*b)` |
| Survival / time-to-event | Log-rank, NOT t-test | `survdiff()` |
| Categorical outcome | Chi-square OR Fisher exact | `chisq.test()`, `fisher.test()` |

## Multiple Testing Adjustment

For pairwise comparisons among K groups, there are K(K-1)/2 unadjusted p-values. Without adjustment, family-wise error rate inflates rapidly:
- 3 groups: 3 comparisons; α_FW = 14% at nominal 5%
- 4 groups: 6 comparisons; α_FW = 26%
- 6 groups: 15 comparisons; α_FW = 54%

```r
# rstatix supports per-comparison adjustment
library(rstatix)
df %>%
    pairwise_wilcox_test(value ~ group, p.adjust.method = 'bonferroni') %>%
    add_xy_position(x = 'group')
```

`p.adjust.method` options:
- `'bonferroni'` — strictest; controls FWER
- `'holm'` — stepwise Bonferroni; uniformly more powerful than Bonferroni
- `'BH'` (Benjamini-Hochberg) — FDR; less strict than FWER; standard for genomics
- `'fdr'` — alias for BH

For figure annotations, **holm** is the modern default — controls FWER and is more powerful than bonferroni. For a small number of pre-planned comparisons (≤3), Bonferroni is fine.

## ggpubr -- Standard ggplot2 Workflow

**Goal:** Add per-comparison p-value brackets between groups on a distribution plot, using a test appropriate to data shape and adjusting for multiple comparisons.

**Approach:** Build the base plot with `ggboxplot()`; add `stat_compare_means()` with explicit `method`, `comparisons`, `p.adjust.method`, and `label` arguments; render as asterisks (`p.signif`) for terse display or numeric (`p.format`) for precise display.

```r
library(ggpubr)

# Default boxplot + p-value bracket(s)
ggboxplot(df, x = 'group', y = 'value', color = 'group',
          add = 'jitter', palette = 'npg') +
    stat_compare_means(method = 'wilcox.test',           # explicit; default is t-test
                       comparisons = list(c('Control', 'Treatment'),
                                          c('Control', 'Vehicle'),
                                          c('Treatment', 'Vehicle')),
                       label = 'p.signif',               # 'p.signif' for asterisks; 'p.format' for numeric
                       p.adjust.method = 'holm',
                       method.args = list(alternative = 'two.sided'))
```

For an overall test plus pairwise:

```r
# Overall + per-comparison
ggboxplot(df, x = 'group', y = 'value', color = 'group') +
    stat_compare_means(method = 'kruskal.test',          # overall test
                       label.y = 1.05 * max(df$value)) +
    stat_compare_means(comparisons = pairs,
                       method = 'wilcox.test',
                       p.adjust.method = 'holm',
                       label = 'p.signif')
```

## ggsignif -- Lighter Alternative

```r
library(ggsignif)
ggplot(df, aes(group, value, fill = group)) +
    geom_boxplot() +
    geom_signif(comparisons = list(c('Control', 'Treatment')),
                test = 'wilcox.test',
                map_signif_level = TRUE,                  # asterisks vs numeric p
                step_increase = 0.1) +
    scale_fill_manual(values = c('#0072B2', '#D55E00'))
```

`map_signif_level = TRUE` converts p-values to asterisks per Wasserstein-Lazar 2016 convention:
- `***` p < 0.001
- `**` p < 0.01
- `*` p < 0.05
- `ns` p ≥ 0.05

For literal p-values, set `FALSE`.

## statannotations (Python)

```python
import seaborn as sns
from statannotations.Annotator import Annotator

ax = sns.boxplot(x='group', y='value', data=df, palette=['#0072B2', '#D55E00', '#009E73'])

pairs = [('Control', 'Treatment'),
         ('Control', 'Vehicle'),
         ('Treatment', 'Vehicle')]

annotator = Annotator(ax, pairs, data=df, x='group', y='value')
annotator.configure(test='Mann-Whitney',                    # 't-test_ind', 't-test_paired', 'Wilcoxon', etc
                    comparisons_correction='holm',
                    text_format='star',                     # 'star', 'simple', 'full'
                    line_height=0.02,
                    text_offset=0.5)
annotator.apply_and_annotate()
```

## Per-Method Failure Modes

### Default t-test on non-normal data

**Trigger:** `stat_compare_means(method='t.test')` (default) on log-distributed expression.

**Mechanism:** t-test assumes approximate normality; non-normal data with small N inflates Type-I.

**Symptom:** Significant p where rank test gives p > 0.05.

**Fix:** Switch to `method='wilcox.test'` for non-normal or small-N data. Verify normality with Shapiro-Wilk if borderline.

### Pairwise tests without adjustment

**Trigger:** Multiple bracket annotations with raw p-values.

**Mechanism:** K(K-1)/2 comparisons inflate FWER without adjustment.

**Symptom:** All-pairwise significant at nominal 0.05; doesn't replicate.

**Fix:** `p.adjust.method = 'holm'` (or 'bonferroni' or 'BH'). Document choice.

### Paired data tested as independent

**Trigger:** Before/after measurements in same subjects, tested with unpaired t-test.

**Mechanism:** Ignores within-subject correlation; loses power.

**Symptom:** Non-significant p where paired test gives significant.

**Fix:** `paired = TRUE` (R) or `t-test_paired` (statannotations). Verify subjects are correctly matched.

### Nested data tested with pairwise t

**Trigger:** Hundreds of cells per patient, tested as if each cell is independent.

**Mechanism:** Pseudoreplication — within-patient correlation ignored; p-values dramatically over-significant.

**Symptom:** p < 1e-50 from a dataset where the actual N is ~10 patients.

**Fix:** Linear mixed model (`lme4::lmer(value ~ group + (1|patient_id))`); aggregate to per-patient median first; or pseudobulk.

### Asterisks shown but p-values not reported anywhere

**Trigger:** `label = 'p.signif'` exclusively.

**Mechanism:** Reader cannot recover the actual p-value.

**Symptom:** Reviewer asks for exact p; not in figure or supplementary.

**Fix:** Either show numeric p (`label = 'p.format'`) or include test results table in supplementary.

### n.s. annotation hidden

**Trigger:** Showing only significant brackets, omitting non-significant.

**Mechanism:** Selective reporting biases interpretation.

**Symptom:** Reader assumes untested pairs were significant.

**Fix:** Either annotate all comparisons (with n.s. for non-significant) OR pre-specify which pairs are tested in the legend/caption.

### Reading effect size from p-value

**Trigger:** Conclusion "highly significant difference" from p = 1e-10 on a tiny effect.

**Mechanism:** Large N inflates significance for trivial differences.

**Symptom:** Effect size negligible despite extreme p.

**Fix:** Always report effect size (Cohen's d, Cliff's delta, median difference with CI) alongside p. The bracket should convey direction AND magnitude, not just significance.

## Reconciliation: When Tests Disagree

| Pattern | Cause | Action |
|---------|-------|--------|
| t-test significant; Wilcoxon n.s. | Outliers driving t-test; rank test robust | Trust Wilcoxon for non-normal data |
| Unpaired n.s.; paired significant | Within-subject correlation matters | Use paired if subjects are matched |
| Pairwise all-significant; ANOVA n.s. | Multiple-testing inflation in pairwise | ANOVA / Kruskal-Wallis is the overall test; pairwise post-hoc only after omnibus significant |
| Pseudo-replicated p < 1e-50; LMM p = 0.1 | Pseudoreplication | LMM is correct; pseudo-replicated p is meaningless |
| Bonferroni-adjusted n.s.; raw p < 0.05 | Adjustment correctly identified borderline | Trust adjusted; document the test family |

## Quantitative Thresholds

| Threshold | Value | Source |
|-----------|-------|--------|
| α for FWER control | 0.05 family-wise | Standard |
| α for FDR control | 0.05 expected FDR (BH) | Benjamini-Hochberg 1995 |
| Asterisk convention | * <0.05, ** <0.01, *** <0.001 | Common practice |
| Bonferroni cutoff | 0.05 / K(K-1)/2 | Standard |
| Holm step-down | better than Bonferroni for all K | Holm 1979 |
| FDR (BH) | less strict than FWER | Genomics standard |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| Reviewer asks "why t-test?" | Default not justified | Pre-justify test choice |
| Many pairwise-significant; doesn't replicate | No multiple-testing adjustment | Holm or BH |
| Effect "highly significant" but tiny | Large N inflates p | Report effect size |
| Asterisks only; no p-values | `label = 'p.signif'` exclusively | Show p.format OR provide table |
| Pseudoreplication inflated p | Cells treated as independent | LMM or pseudobulk |
| n.s. comparisons hidden | Selective reporting | Annotate all pre-specified pairs |
| Numeric p truncated to '<2.22e-16' | R default precision | Manual formatting or report as `< 2e-16` |

## References

- Benjamini Y, Hochberg Y. 1995. Controlling the false discovery rate: a practical and powerful approach to multiple testing. *J R Stat Soc B* 57:289-300.
- Dunn OJ. 1964. Multiple comparisons using rank sums. *Technometrics* 6(3):241-252.
- Holm S. 1979. A simple sequentially rejective multiple test procedure. *Scand J Stat* 6(2):65-70.
- Kassambara A. 2020. *Practical Statistics in R for Comparing Groups: Numerical Variables.* (ggpubr / rstatix tutorial).
- Wasserstein RL, Lazar NA. 2016. The ASA's statement on p-values: context, process, and purpose. *Am Stat* 70(2):129-133.

## Related Skills

- data-visualization/distribution-plots - Underlying box/violin/raincloud
- clinical-biostatistics/categorical-tests - Chi-square / Fisher tests for categorical outcomes
- clinical-biostatistics/effect-measures - Effect size to report alongside p
- experimental-design/multiple-testing - Methods for controlling FWER and FDR
<!-- END FILE: data-visualization/statistical-annotation/SKILL.md -->

## 子目录：data-visualization/upset-plots

<!-- BEGIN FILE: data-visualization/upset-plots/SKILL.md -->
---
name: bio-data-visualization-upset-plots
description: Build UpSet plots to visualize set intersections beyond 4 sets (where Venn fails) using ComplexUpset (modern, ggplot2-grammar) or the unmaintained UpSetR, with explicit cardinality vs degree sorting, attribute panels, and query highlighting. Use when comparing overlap across many gene sets, peak sets, variant lists, or any set membership matrix where Venn diagrams become illegible.
tool_type: mixed
primary_tool: ComplexUpset
---

## Version Compatibility

Reference examples tested with: ComplexUpset 1.3+ (R, Krassowski), UpSetR 1.4.0 (last 2019 release; effectively unmaintained), upsetplot 0.9+ (Python).

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('<pkg>')` then `?function_name`
- Python: `pip show <package>` then `help(module.function)`

If code throws ImportError, AttributeError, or TypeError, introspect the installed package and adapt the example to match the actual API rather than retrying.

# UpSet Plots

**"Show set intersections for 4+ sets"** -> Replace Venn diagrams (which become illegible past 4 sets) with UpSet (Lex 2014 *IEEE TVCG* 20:1983). The display: a matrix of dots indicating which sets participate in each intersection, with a vertical bar above each column showing intersection size and horizontal bars on the left showing per-set total size. Sort by intersection size (cardinality) for "biggest overlaps first" or by degree (number of sets) for grouped layout.

- R: `ComplexUpset::upset` (Krassowski; ggplot2-native, **recommended**), `UpSetR::upset` (Conway 2017; legacy, unmaintained)
- Python: `upsetplot.UpSet`

## The Single Most Important Modern Insight -- UpSetR Is Effectively Unmaintained

UpSetR (Conway, Lex, Gehlenborg 2017 *Bioinformatics* 33:2938) is the original R implementation but has had no CRAN release since v1.4.0 (2019). ComplexUpset (Krassowski; CRAN active through 2025-07) is the actively maintained ggplot2-grammar replacement. For new work in 2026, **prefer ComplexUpset**. Caveat: ggplot2 4.0 (mid-2025) broke ComplexUpset's `upset()` function (issue #213); pin to compatible versions until patched.

The Lex 2014 paper and underlying UpSet visualization concept are not affected — the visualization is the same; the difference is which R package implements it best in the current ecosystem.

## ComplexUpset (Modern Default)

**Goal:** Render a set-intersection plot with cardinality-sorted bars, optional metadata stacks (e.g., percent of intersection significant), and pre-specified queries highlighting biologically relevant intersections.

**Approach:** Convert set memberships to a long-format data frame with one row per element and binary columns per set; pass to `upset()` with `intersections='all'` or pre-specified subset; use `ComplexUpset::upset_query` to highlight intersections.

```r
library(ComplexUpset)
library(ggplot2)

# Convert from list of sets to long format
sets <- list(SetA = c('Gene1','Gene2','Gene3','Gene4'),
             SetB = c('Gene2','Gene3','Gene5','Gene6'),
             SetC = c('Gene1','Gene3','Gene6','Gene7'),
             SetD = c('Gene3','Gene4','Gene7','Gene8'))

# Long-format binary membership matrix
all_elements <- unique(unlist(sets))
df <- data.frame(element = all_elements)
for (s in names(sets)) df[[s]] <- df$element %in% sets[[s]]

# UpSet
upset(df,
      intersect = names(sets),                          # which columns are sets
      n_intersections = 20,                             # show top 20 intersections
      sort_intersections = 'descending',                # by cardinality
      sort_intersections_by = 'cardinality',            # 'cardinality' OR 'degree'
      base_annotations = list(
          'Intersection size' = intersection_size(
              counts = TRUE,
              text = list(size = 3))),
      themes = upset_modify_themes(
          list('Intersection size' = theme(panel.grid = element_blank()))))
```

## Sorting -- Cardinality vs Degree

**Cardinality sort** (default): intersections ordered by size (largest first). Reveals "the biggest overlap is A∩B."

**Degree sort**: intersections grouped by *number of sets they include* (1-set intersections, then 2-set, then 3-set, etc.). Reveals "how distributed are the overlaps across set counts?"

Choose based on the scientific question. Cardinality is the default for "find the biggest overlap"; degree is appropriate when comparing across "exclusive to 1 set" vs "shared by all."

## Pre-Specified Queries / Highlighting

```r
upset(df,
      intersect = names(sets),
      queries = list(
          upset_query(intersect = c('SetA', 'SetB'),
                       color = '#D55E00', fill = '#D55E00',
                       only_components = c('intersections_matrix', 'Intersection size')),
          upset_query(intersect = c('SetA', 'SetC', 'SetD'),
                       color = '#0072B2', fill = '#0072B2',
                       only_components = c('intersections_matrix', 'Intersection size'))))
```

## Attribute Panels (ComplexUpset Strength)

Unlike UpSetR's "boxplot.summary," ComplexUpset supports arbitrary ggplot annotations stacked above the intersection bars:

```r
upset(df,
      intersect = names(sets),
      annotations = list(
          'log2 FC' = ggplot(mapping = aes(x = intersection, y = log2FC)) +
                       geom_boxplot() + theme_classic(),
          'Significant fraction' = ggplot(mapping = aes(x = intersection, fill = significant)) +
                                    geom_bar(position = 'fill') +
                                    scale_fill_manual(values = c('TRUE' = '#D55E00', 'FALSE' = 'grey80')) +
                                    theme_classic()))
```

## upsetplot (Python)

```python
from upsetplot import from_contents, UpSet
import matplotlib.pyplot as plt

sets = {'SetA': ['Gene1','Gene2','Gene3','Gene4'],
        'SetB': ['Gene2','Gene3','Gene5','Gene6'],
        'SetC': ['Gene1','Gene3','Gene6','Gene7']}
data = from_contents(sets)

upset = UpSet(data,
              subset_size='count',
              show_counts=True,
              sort_by='cardinality',                    # 'cardinality' OR 'degree'
              sort_categories_by='cardinality',
              facecolor='#0072B2',
              element_size=40)
upset.style_subsets(present=['SetA', 'SetB'], facecolor='#D55E00')   # highlight specific intersection
fig = plt.figure(figsize=(8, 5))
upset.plot(fig=fig)
plt.savefig('upset.pdf', bbox_inches='tight')
```

## UpSetR (Legacy — Use Only for Reproducibility)

```r
library(UpSetR)
upset(fromList(sets),
      nsets = 4, nintersects = 20,
      order.by = 'freq',
      decreasing = TRUE,
      mb.ratio = c(0.6, 0.4),
      point.size = 3,
      line.size = 1,
      text.scale = c(1.5, 1.3, 1.3, 1, 1.5, 1.3))
```

UpSetR works but lacks ggplot2 grammar and active maintenance. Reproducing a paper's UpSetR figure is the main reason to use it in 2026.

## Per-Method Failure Modes

### Using UpSetR for new work in 2026

**Trigger:** Following older tutorials that default to UpSetR.

**Mechanism:** UpSetR has not had a CRAN release since 2019; integration with current ggplot2 / R ecosystem stale.

**Symptom:** Limited customization; ggplot2 layer not available; eventual breakage.

**Fix:** Switch to ComplexUpset for new figures. UpSetR is fine for reproducing old figures.

### ggplot2 4.0 broke ComplexUpset

**Trigger:** ggplot2 4.0 (mid-2025) introduced API changes; ComplexUpset's `upset()` errored.

**Mechanism:** Upstream ggplot2 changes affected ComplexUpset internals (issue #213).

**Symptom:** "Error in `upset()`: ..." after ggplot2 upgrade.

**Fix:** Pin compatible versions (`renv::install('ggplot2@3.5.2')`) until ComplexUpset patches. Check GitHub issues for fix status.

### Too many sets makes UpSet unreadable

**Trigger:** UpSet with 10+ sets and `n_intersections = Inf`.

**Mechanism:** Number of possible intersections is 2^N − 1; with 10 sets that's 1023 columns.

**Symptom:** Vertical bars too thin to read; matrix dots unrecognizable.

**Fix:** Set `n_intersections = 20` (or whatever fits); pre-filter to relevant intersections via `intersections = list(c('SetA','SetB'), c('SetA','SetC','SetD'))`.

### Single-set "intersections" obscure cross-set overlap story

**Trigger:** Default sort by cardinality puts "set exclusives" first (often largest).

**Mechanism:** "SetA only" is technically a 1-set intersection; usually larger than any 2+set overlap.

**Symptom:** First 4-5 bars are "exclusive to X," obscuring the cross-set story.

**Fix:** Filter via `intersections` argument to exclude 1-set; OR sort by degree to group; OR use `mode='intersect'` (vs `'distinct'`) for different counting.

### Element duplicate across sets in `fromList`

**Trigger:** Same element appears in multiple sets but stored as duplicate rows.

**Mechanism:** `fromList` expects each element appears once per set; duplicates inflate counts.

**Symptom:** Intersection counts don't sum to known totals.

**Fix:** `lapply(sets, unique)` before `fromList`.

### upsetplot from_contents vs from_indicators

**Trigger:** Wrong input format function used.

**Mechanism:** `from_contents` for dict of element lists; `from_indicators` for already-pivoted binary frame.

**Symptom:** TypeError or wrong intersections.

**Fix:** Check input shape; use the appropriate constructor.

## Reconciliation: When Implementations Differ

| Pattern | Cause | Action |
|---------|-------|--------|
| ComplexUpset and UpSetR show different intersection counts | Different element duplication handling | `lapply(sets, unique)`; verify both agree |
| ComplexUpset slow on >10 sets | 2^N intersections enumerated | Pre-specify relevant intersections; use `n_intersections` |
| upsetplot Python output differs from R | sort_by default differs | Set sort_by explicitly in both |
| Excluding 1-set intersections | mode='distinct' vs 'intersect' | `intersections` parameter; document |

## Quantitative Thresholds

| Threshold | Value | Source |
|-----------|-------|--------|
| Max sets for legible UpSet | 8-10 | Visualization practical |
| Show top intersections | 15-25 | Above this matrix too thin |
| When to use UpSet vs Venn | >3 sets | Lex 2014 |
| 2^N intersections | grows exponentially | Set n_intersections limit |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| Intersection columns too thin | Too many intersections shown | `n_intersections = 20`; pre-filter |
| 1-set bars dominate | Default cardinality sort | Exclude 1-set OR sort by degree |
| Intersection counts wrong | Duplicate elements in fromList input | `lapply(sets, unique)` |
| UpSetR error after R upgrade | Unmaintained package | Switch to ComplexUpset |
| ComplexUpset breaks after ggplot2 update | ggplot2 4.0 issue #213 | Pin ggplot2 ≤ 3.5.2 |
| Python upsetplot mismatch with R | Different default sort | Standardize sort_by |

## References

- Conway JR, Lex A, Gehlenborg N. 2017. UpSetR: an R package for the visualization of intersecting sets and their properties. *Bioinformatics* 33(18):2938-2940.
- Krassowski M. 2020. ComplexUpset (R package). https://github.com/krassowski/complex-upset
- Lex A, Gehlenborg N, Strobelt H, Vuillemot R, Pfister H. 2014. UpSet: visualization of intersecting sets. *IEEE Trans Vis Comput Graph* 20(12):1983-1992.

## Related Skills

- data-visualization/heatmaps-clustering - Alternative for smaller set membership (Venn alternative is OncoPrint-style)
- pathway-analysis/go-enrichment - Gene-set overlaps to visualize
- differential-expression/de-results - DE gene-list comparisons
- data-visualization/flow-and-transition-plots - Alluvial as alternative for membership flow
<!-- END FILE: data-visualization/upset-plots/SKILL.md -->

## 子目录：data-visualization/volcano-and-ma-plots

<!-- BEGIN FILE: data-visualization/volcano-and-ma-plots/SKILL.md -->
---
name: bio-data-visualization-volcano-and-ma-plots
description: Build volcano and MA plots from differential-expression / association results with LFC shrinkage, FDR-adjusted thresholds, sensible label placement, and axis-truncation conventions. Covers EnhancedVolcano, ggplot2, matplotlib, and the apeglm/ashr/normal shrinkage decision. Use when visualizing differential-expression results (RNA-seq, ChIP-seq, ATAC-seq, proteomics) or any per-feature effect-size + p-value table.
tool_type: mixed
primary_tool: ggplot2
---

## Version Compatibility

Reference examples tested with: DESeq2 1.42+, EnhancedVolcano 1.20+, ggplot2 3.5+, ggrepel 0.9.5+, matplotlib 3.8+, numpy 1.26+, adjustText 1.1+, apeglm 1.28+, ashr 2.2+.

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters

If code throws ImportError, AttributeError, or TypeError, introspect the installed package and adapt the example to match the actual API rather than retrying.

# Volcano and MA Plots

**"Plot differential-expression results"** -> Place per-feature shrunken effect estimate on the x-axis and a significance measure (-log10 padj or -log10 p) on the y-axis. The decision space spans which effect estimate (raw vs shrunken), which significance measure (raw p vs adjusted vs s-value), how to encode categories (color by direction, not by gradient), how to label (top-N is rarely informative), and how to handle the tail (extreme p compresses the plot).

- R: `EnhancedVolcano::EnhancedVolcano()`, `ggplot2 + ggrepel`, `DESeq2::plotMA()`
- Python: `matplotlib.scatter` with `adjustText`, `sanbomics.tools.volcano`, custom seaborn

## The Single Most Important Modern Insight -- Plot Shrunken LFC

Raw log2 fold change from DESeq2 / edgeR is the maximum-likelihood estimate and **inflates wildly at low counts**. A gene with 2 vs 0 reads gets log2FC = Inf; one with 4 vs 1 gets log2FC = 2 with a huge standard error. A naive volcano labels these as "top hits" purely because they have extreme estimates, not because they have a real signal.

`DESeq2::lfcShrink()` applies an empirical-Bayes prior to pull noisy low-count LFCs toward zero while leaving well-estimated genes essentially untouched. Since DESeq2 v1.28, the default shrinkage is `type='apeglm'` (Zhu, Ibrahim, Love 2019 *Bioinformatics* 35:2084) which uses a Cauchy prior — heavy enough to preserve large real effects, sharp enough at zero to deflate noise. Plot the shrunken LFC. The unshrunken LFC is a misleading effect estimate for ranking, labeling, or thresholding.

A complementary modern alternative is the **s-value** (Stephens 2017 *Biostatistics* 18:275): the local false sign rate — probability that the sign of the effect is wrong. s-values rank genes by *how confident the sign is*, which is what a volcano plot is implicitly trying to communicate. Where padj answers "is the effect non-zero," s answers "do we know which direction."

## Shrinkage Method Selection

| Method | Prior | Best for | Fails when |
|--------|-------|----------|------------|
| `apeglm` (Zhu 2019) | Cauchy | Default; preserves large LFCs, deflates noise | Requires `coef=`; no support for `contrast=` |
| `ashr` (Stephens 2017) | Mixture of normals | Comparisons requiring `contrast=`; supports s-values | Slightly more aggressive shrinkage of medium effects |
| `normal` (DESeq2 original) | Zero-centered normal | Legacy reproducibility only | Over-shrinks large effects; **deprecated** in current DESeq2 vignette |
| Unshrunken MLE | None | NEVER for volcano/MA plots | Low-count genes dominate the tails with no real signal |

```r
library(DESeq2)
dds <- DESeq(dds)
res_apeglm <- lfcShrink(dds, coef = 'condition_treated_vs_control', type = 'apeglm')
res_ashr <- lfcShrink(dds, contrast = c('condition', 'treated', 'control'), type = 'ashr')
# ashr also returns svalue column (Stephens 2017 local false sign rate)
```

For edgeR users: `topTags()` already provides moderated p-values but does not shrink LFC. Use `glmTreat()` for a moderated test against a non-zero LFC threshold; this is the edgeR equivalent of the shrunken-LFC philosophy.

## Decision Tree by Scenario

| Scenario | Recommended | Why |
|----------|-------------|-----|
| Bulk RNA-seq with DESeq2 | `lfcShrink(type='apeglm')` + plot on padj threshold | apeglm is the default since DESeq2 v1.28 |
| Non-default contrast required | `lfcShrink(type='ashr')` | apeglm requires `coef=`, ashr accepts `contrast=` |
| Single-cell pseudobulk DE | `lfcShrink(type='apeglm')` + raster the plot | sc datasets often >20k genes; raster prevents PDF lag |
| Proteomics (limma/MSstats) | Already moderated; plot logFC vs adj.P.Val directly | limma's empirical-Bayes already shrinks |
| Microarray (limma) | `topTable()` adj.P.Val + logFC | Same — limma is the original shrunken-LFC method |
| ATAC/ChIP differential peaks | `lfcShrink(type='apeglm')` on DESeq2/DiffBind | Treat peaks as features identically to genes |
| Want to rank by sign-confidence | ashr's svalue, NOT padj | Stephens 2017 — sign-aware ranking |
| Many comparisons in one figure | Faceted MA plot with shared y-axis | MA scales better than volcano for >6 panels |

## Volcano with ggplot2 + ggrepel

**Goal:** Plot shrunken LFC vs -log10 p-value, color by significance class, label genes of interest with non-overlapping repulsion.

**Approach:** Compute a categorical significance variable from padj AND |LFC| thresholds; pre-select labels (genes of interest OR top-N by combined rank) before plotting; use `ggrepel::geom_text_repel` with `max.overlaps = Inf` to guarantee every selected label appears.

```r
library(ggplot2)
library(ggrepel)
library(dplyr)

volcano_plot <- function(res, fdr = 0.05, lfc_threshold = 1, label_genes = NULL, top_n = 10) {
    res <- as.data.frame(res) %>%
        tibble::rownames_to_column('gene') %>%
        mutate(
            significance = case_when(
                is.na(padj) ~ 'NS',
                padj < fdr & log2FoldChange > lfc_threshold ~ 'Up',
                padj < fdr & log2FoldChange < -lfc_threshold ~ 'Down',
                TRUE ~ 'NS'
            ),
            neg_log10_p = -log10(pvalue)
        )

    if (is.null(label_genes)) {
        label_genes <- res %>%
            filter(significance != 'NS') %>%
            mutate(rank_score = -log10(pvalue) * abs(log2FoldChange)) %>%
            arrange(desc(rank_score)) %>%
            head(top_n) %>%
            pull(gene)
    }
    res$label <- ifelse(res$gene %in% label_genes, res$gene, '')

    okabe_ito <- c(Up = '#D55E00', Down = '#0072B2', NS = '#999999')

    ggplot(res, aes(log2FoldChange, neg_log10_p, color = significance)) +
        geom_point(alpha = 0.6, size = 1.3) +
        scale_color_manual(values = okabe_ito, name = NULL) +
        geom_vline(xintercept = c(-lfc_threshold, lfc_threshold),
                   linetype = 'dashed', color = 'grey40', linewidth = 0.3) +
        geom_hline(yintercept = -log10(fdr), linetype = 'dashed',
                   color = 'grey40', linewidth = 0.3) +
        geom_text_repel(aes(label = label), color = 'black', size = 3,
                        max.overlaps = Inf, box.padding = 0.4, segment.size = 0.2,
                        min.segment.length = 0) +
        labs(x = expression(log[2]~'fold change (shrunken)'),
             y = expression(-log[10]~italic(p))) +
        theme_classic(base_size = 10) +
        theme(panel.grid = element_blank())
}
```

Key design choices encoded above:
- Colors from Okabe-Ito (Wong 2011 *Nat Methods* 8:441) — CVD-safe categorical palette
- `max.overlaps = Inf` because the ggrepel default of 10 silently drops labels with no error (see [[api_gotchas]])
- Threshold line on `-log10(fdr)` matches the *adjusted* p threshold; drawing it on raw p creates a meaningless line
- `rank_score = -log10(pvalue) * abs(log2FoldChange)` selects labels that are both significant AND have non-trivial effect; pure top-N-by-p selects high-count genes with tiny effects

## EnhancedVolcano -- Production Use and Its Gotchas

```r
library(EnhancedVolcano)
EnhancedVolcano(res,
    lab = rownames(res),
    x = 'log2FoldChange',
    y = 'padj',                    # use padj NOT pvalue for the threshold line
    pCutoff = 0.05,
    FCcutoff = 1,
    selectLab = c('TP53', 'MYC', 'BRCA1'),
    drawConnectors = TRUE,
    widthConnectors = 0.3,
    maxoverlapsConnectors = Inf,
    colAlpha = 0.6,
    pointSize = 1.5,
    labSize = 3,
    col = c('grey60', '#0072B2', '#56B4E9', '#D55E00'),
    legendPosition = 'right')
```

**Gotcha 1: `selectLab` filters through pCutoff AND FCcutoff.** Genes explicitly listed but failing thresholds appear unlabeled, with no warning. This is the most common "why is the gene missing" failure. To force-label regardless of thresholds, pre-shrink the input so the genes pass the cutoff, or switch to a manual ggplot layer.

**Gotcha 2: `y = 'pvalue'` vs `y = 'padj'`.** Many tutorials use raw `pvalue` for the y-axis, then draw the threshold line at `-log10(0.05)` — that line corresponds to a raw p < 0.05, not an FDR. Use `y = 'padj'` so the threshold is meaningful.

**Gotcha 3: Asymmetric x-limits hide the diverging null distribution.** Use `xlim = c(-max(abs(LFC)), max(abs(LFC)))` so the plot is symmetric around zero.

## MA Plot -- The Underused Diagnostic

The MA plot (log2-mean vs log2-fold-change) is the original RNA-seq diagnostic (Dudoit 2002 *JASA*). It exposes the abundance-dependent variance structure that the volcano hides:

- A fan-shaped MA plot with extreme LFCs concentrated at low baseMean indicates **inadequate shrinkage**
- A horizontal "stripe" of significant genes at one LFC value indicates **batch confound with treatment**
- An asymmetric distribution (more Up than Down) at the low-count end indicates **library-size normalization failure**

```r
library(DESeq2)
plotMA(res_apeglm, alpha = 0.05, ylim = c(-5, 5))
# alpha colors significant points; ylim clips for readability without losing the gene
```

```python
import matplotlib.pyplot as plt
import numpy as np

def ma_plot(res, fdr=0.05, ax=None):
    if ax is None:
        fig, ax = plt.subplots(figsize=(6, 5))
    sig = (res['padj'] < fdr) & res['padj'].notna()
    ax.scatter(np.log10(res.loc[~sig, 'baseMean']), res.loc[~sig, 'log2FoldChange'],
               c='#999999', s=4, alpha=0.4, rasterized=True)
    ax.scatter(np.log10(res.loc[sig, 'baseMean']), res.loc[sig, 'log2FoldChange'],
               c='#D55E00', s=6, alpha=0.7, rasterized=True)
    ax.axhline(0, color='black', linewidth=0.5)
    ax.set_xlabel(r'$\log_{10}$ mean normalized count')
    ax.set_ylabel(r'$\log_2$ fold change (shrunken)')
    return ax
```

`rasterized=True` is critical for >5000 points — vector scatter creates 5MB+ PDFs that crash Illustrator.

## Per-Method Failure Modes

### Unshrunken LFC plotted as volcano

**Trigger:** Calling `results(dds)` and plotting `log2FoldChange` directly, without `lfcShrink()`.

**Mechanism:** ML estimate has infinite-variance tails at low counts; one read difference produces log2FC = Inf.

**Symptom:** "Top hits" by |LFC| are all genes with baseMean < 5; biologically interesting genes with moderate LFC are hidden in the noise cloud.

**Fix:** `lfcShrink(dds, coef=..., type='apeglm')` for the default case; `type='ashr'` if `contrast=` is needed.

### Raw p threshold line drawn on adjusted axis

**Trigger:** Drawing `geom_hline(yintercept = -log10(0.05))` on a plot whose y-axis is `-log10(padj)`.

**Mechanism:** padj < 0.05 corresponds to FDR < 5% control, NOT to raw p < 0.05. The drawn line is at the wrong y-value relative to the data.

**Symptom:** Visible "significant" points sit below the FDR line; the legend says "FDR < 0.05" but the line doesn't separate them correctly.

**Fix:** Be explicit: if y-axis is padj, use `-log10(fdr)` as the threshold line value AND label it "FDR threshold." If y-axis is raw p, an FDR threshold cannot be drawn as a horizontal line — the FDR threshold moves per gene.

### Top-N-by-p selects low-effect-size hits

**Trigger:** `head(arrange(res, pvalue), 20)` to choose labels.

**Mechanism:** With large N, the smallest p-values belong to high-count, low-variance, biologically-boring genes (housekeeping). Effect size and statistical confidence are not the same thing.

**Symptom:** Labels are GAPDH, ACTB, B2M — never the gene that drives the biology.

**Fix:** Rank by `-log10(p) * abs(log2FoldChange)` (geometric average of the two axes), OR pre-specify labels of interest from prior knowledge.

### ggrepel `max.overlaps` silently drops labels

**Trigger:** Default `max.overlaps = 10`; 30 genes labeled in code; only 10 render.

**Mechanism:** ggrepel emits a warning ("18 unlabeled data points (too many overlaps)") but no error. In a Quarto/Rmd render the warning is buried in the log.

**Symptom:** Reviewer asks "where is gene X?"; the label was specified in code but did not render.

**Fix:** `geom_text_repel(..., max.overlaps = Inf)` or `options(ggrepel.max.overlaps = Inf)` at the top of the script.

### Extreme p-values compress the upper axis

**Trigger:** Genes with p = 1e-200 or smaller (common in cancer datasets) push the y-axis maximum to 200; all biologically meaningful genes pile up at the bottom.

**Mechanism:** -log10 expands the tail; one ultra-significant gene visually dominates.

**Symptom:** Volcano looks like an Eiffel Tower with most genes squished near y = 0-20.

**Fix:** Cap the y-axis (`ylim = c(0, 50)` and use `coord_cartesian` so capped points stay in the data but render at the edge) OR transform with `sqrt(-log10(p))` to compress the tail OR split the y-axis with `ggbreak`.

### `lfcShrink(type='normal')` on a modern DESeq2

**Trigger:** Following old tutorials that pre-date DESeq2 v1.28 when apeglm became the default.

**Mechanism:** The `'normal'` prior over-shrinks large real effects toward zero.

**Symptom:** Volcano looks "too clean" — genuine 8-fold changes appear as 2-3 fold.

**Fix:** Use `type='apeglm'` (default since v1.28) or `type='ashr'`. Vignette removed `'normal'` from recommendations.

### EnhancedVolcano's `selectLab` filters by thresholds

**Trigger:** Listing genes in `selectLab` that have `padj > pCutoff`.

**Mechanism:** Source code applies `pCutoff` AND `FCcutoff` filter to `selectLab` membership; silently drops any that don't pass.

**Symptom:** Specific genes requested in `selectLab` do not appear; no warning.

**Fix:** Pre-shrink (so genes pass) or build the labeled subset manually with `ggrepel` and add as an annotation layer.

## Reconciliation: When Methods Disagree

| Pattern | Likely cause | Action |
|---------|--------------|--------|
| apeglm and ashr give different "top hits" | Different prior shapes; medium-effect, medium-count genes are most sensitive | Both are valid; pick one and document. apeglm is the DESeq2 default and the published recommendation |
| EnhancedVolcano shows fewer points than ggplot | EnhancedVolcano drops `padj = NA` (DESeq2 independent filtering) | Confirm by counting `is.na(res$padj)`; to include them, set NA padj to 1 before plotting |
| Volcano has many "significant" genes but MA plot shows them all at low baseMean | Unshrunken LFC; the volcano is showing fold-change noise | Re-plot with shrunken LFC; the MA-plot fan is the diagnostic |
| Forest of horizontal stripes in MA at integer LFC | Pseudocount-induced quantization in low-count genes | Increase normalization-method aggressiveness OR filter low-count genes upstream |
| Half the genes have padj = NA | DESeq2 independent filtering (Bourgon-Gentleman-Huber 2010 *PNAS*) excluded them as low-mean | This is correct behavior; do NOT set `independentFiltering = FALSE` to hide it. Report the NA count |

**Operational rule:** the volcano plot is read in this priority order — (1) is LFC shrunken? (2) is the y-axis padj or raw p? (3) does the threshold line match the axis? (4) are labels selected by combined rank? If any of these is wrong, the plot is misleading regardless of how attractive it looks.

## Quantitative Thresholds

| Threshold | Value | Source |
|-----------|-------|--------|
| Default LFC cutoff for "biologically relevant" | \|log2FC\| > 1 (2-fold) | Convention; sensitive analyses use 0.58 (1.5-fold) for subtle effects |
| Default FDR cutoff | padj < 0.05 | Benjamini-Hochberg 1995 *JRSS-B* 57:289 |
| Stricter cutoff for unbiased screens | padj < 0.01 | Reduces false positives in unbiased genome-wide analyses |
| Relaxed cutoff for exploratory / hypothesis-generating | padj < 0.10 or 0.20 | Acceptable for follow-up enrichment, NOT for "hits" |
| s-value cutoff (Stephens 2017) | s < 0.005 corresponds approximately to padj < 0.05 | Stephens 2017 *Biostatistics* 18:275 |
| Raster threshold | >5000 points | Vector PDF crashes Illustrator; raster scatter, keep axes vector |
| ggrepel max.overlaps | Set to Inf for publication | Default 10 silently drops labels |
| Volcano y-axis cap | -log10(p) > 50 typically warrants capping | Visual compression of biologically meaningful genes |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| All "top hits" have baseMean < 5 | Unshrunken LFC | `lfcShrink(type='apeglm')` |
| Threshold line doesn't separate colored from grey points | y = pvalue but threshold drawn at FDR | Switch y to padj OR redraw line at FDR-equivalent p |
| Labeled gene does not appear in EnhancedVolcano | `selectLab` filtered by pCutoff/FCcutoff | Pre-shrink or build labels manually |
| Volcano renders as a flat horizontal cloud | Extreme p (e.g., 1e-200) dominates y-axis | Cap with `coord_cartesian(ylim = c(0, 50))` or use sqrt transform |
| PDF crashes Illustrator | Vector scatter of >10000 points | Set `rasterized = TRUE` in geom_point or matplotlib scatter |
| ggrepel labels 10 of 30 selected genes | Default `max.overlaps = 10` | `geom_text_repel(max.overlaps = Inf)` |
| Volcano "significant" gene count differs from DESeq2 summary | EnhancedVolcano drops `padj = NA` | Set NA padj to 1 or document the discrepancy |
| Up and Down counts asymmetric for a balanced experiment | Library-size normalization failure | Re-run DESeq2 with `estimateSizeFactors(type='poscounts')` for sparse data |

## Anticipated Reviewer Pushback

| Pushback | Standard response |
|----------|-------------------|
| "Why is this LFC shrunken? Show me the unshrunken." | Shrunken LFC is the recommended estimate for ranking and visualization (Zhu 2019). Unshrunken LFC inflates at low counts and gives misleading rank. Unshrunken is available in the supplementary table |
| "Why padj < 0.05 not p < 0.05?" | padj controls FDR via Benjamini-Hochberg. Raw p < 0.05 across 20000 genes yields ~1000 false positives by chance; padj < 0.05 caps the expected false-positive rate at 5% of called hits |
| "Why are X gene and Y gene not labeled?" | Labels selected by combined rank (-log10(p) * \|LFC\|) or pre-specified gene list. List of all significant genes is in supplementary table T1 |
| "The volcano looks too clean / too sparse." | Color encodes 3 categories (Up/Down/NS), not a gradient. Gradient encoding implies a continuous interpretation of significance which is invalid — significance is a threshold decision |
| "Why is the x-axis asymmetric?" | Asymmetric x-axis reflects the asymmetry of the data. If symmetry is preferred for visual interpretation, use `xlim = c(-X, X)` with X = max(\|LFC\|) |

## References

- Anders S, Huber W. 2010. Differential expression analysis for sequence count data. *Genome Biol* 11:R106.
- Benjamini Y, Hochberg Y. 1995. Controlling the false discovery rate: a practical and powerful approach to multiple testing. *JRSS-B* 57:289-300.
- Bourgon R, Gentleman R, Huber W. 2010. Independent filtering increases detection power for high-throughput experiments. *PNAS* 107:9546-9551.
- Dudoit S, Yang YH, Callow MJ, Speed TP. 2002. Statistical methods for identifying differentially expressed genes in replicated cDNA microarray experiments. *Stat Sin* 12:111-139.
- Love MI, Huber W, Anders S. 2014. Moderated estimation of fold change and dispersion for RNA-seq data with DESeq2. *Genome Biol* 15:550.
- Stephens M. 2017. False discovery rates: a new deal. *Biostatistics* 18(2):275-294. doi:10.1093/biostatistics/kxw041
- Wong B. 2011. Points of view: Color blindness. *Nat Methods* 8(6):441. doi:10.1038/nmeth.1618
- Zhu A, Ibrahim JG, Love MI. 2019. Heavy-tailed prior distributions for sequence count data: removing the noise and preserving large differences. *Bioinformatics* 35(12):2084-2092. doi:10.1093/bioinformatics/bty895

## Related Skills

- differential-expression/de-results - Filter and rank DE result tables before plotting
- differential-expression/deseq2-basics - Run DESeq2 to produce the input results object
- differential-expression/de-visualization - DESeq2 / edgeR built-in plot helpers
- data-visualization/distribution-plots - Boxplot / raincloud follow-up for specific gene panels
- data-visualization/color-palettes - Okabe-Ito and CVD-safe palette selection
- data-visualization/ggplot2-fundamentals - Underlying grammar of graphics
- pathway-analysis/go-enrichment - Functional enrichment from the gene lists produced
<!-- END FILE: data-visualization/volcano-and-ma-plots/SKILL.md -->

<!-- END CATEGORY: data-visualization -->

