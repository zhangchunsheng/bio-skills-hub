---
slug: bio-reporting-integrated
version: 1.0.0
displayName: "报告生成 / Report generation"
name: bio-reporting-integrated
summary: >-
  中文：报告生成综合技能，整合 6 个相关专题，覆盖分析报告生成：RMarkdown/Quarto/Jupyter报告、MultiQC QC聚合、出版物级图表导出。 English: Integrated Report generation skill covering 6 related topics, including Report generation: RMarkdown/Quarto/Jupyter reports, MultiQC QC aggregation, publication-quality figure export.
description: >-
  中文：这是一个面向报告生成的综合生物信息学 Skill，整合当前分类下 6 个相关专题能力。它用于根据研究问题、数据类型和分析阶段，选择合适的方法与工具，规划从输入检查、预处理、核心分析到质量控制、统计解释和结果报告的完整流程。重点覆盖：分析报告生成：RMarkdown/Quarto/Jupyter报告、MultiQC QC聚合、出版物级图表导出。当用户提供相关实验数据、测序结果、表格或研究问题时，它会帮助判断分析目标与前置条件，给出工具选择、关键参数、输入输出、常见失败原因、结果解读和可复现建议。主要工具包括：Quarto, gtsummary, matplotlib。该 Skill 提供分析设计与实施指导，不替代对具体数据质量、生物学背景和最终结论的人工审查。
  English: This is an integrated bioinformatics Skill for Report generation, combining 6 related topic areas. It helps users choose appropriate methods and tools based on the research question, data type, and analysis stage, and plan an end-to-end workflow from input validation and preprocessing through core analysis, quality control, statistical interpretation, and reporting. It covers Report generation: RMarkdown/Quarto/Jupyter reports, MultiQC QC aggregation, publication-quality figure export. For relevant experimental data, sequencing results, tables, or research questions, it clarifies prerequisites, recommends tools and parameters, describes expected inputs and outputs, explains common failure modes, and supports reproducible analysis. Primary tools include: Quarto, gtsummary, matplotlib. It provides methodological and implementation guidance; final data-quality assessment and biological conclusions still require human review.
---

# reporting 分类 Skill 整合版

> 本文件整合同一主分类目录下 6 个子目录中的 SKILL.md 内容。
> 各子目录正文按原文保留，并通过标题和边界标记进行区分；源文件中的元数据块未被改写。

---

<!-- BEGIN CATEGORY: reporting -->

## 子目录：reporting/automated-qc-reports

<!-- BEGIN FILE: reporting/automated-qc-reports/SKILL.md -->
---
name: bio-reporting-automated-qc-reports
description: Aggregates per-tool QC metrics (FastQC, fastp, alignment, quantification, variant calling, single-cell) into one interactive MultiQC report, and guides module scoping, sample-name resolution, large-cohort behavior, and turning the report into an actual QC gate. Use when summarizing QC across many samples, building a shareable quality report, or wiring automated QC into a pipeline.
tool_type: cli
primary_tool: multiqc
---

## Version Compatibility

Reference examples tested with: MultiQC 1.21+ (Plotly era), FastQC 0.12+, STAR 2.7.11+, Subread 2.0+, salmon 1.10+, samtools 1.19+, Picard 3.1+, fastp 0.23+

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

Config keys and defaults move between MultiQC releases (the plotting backend changed from HighCharts to Plotly at 1.20; flat-plot and AI thresholds shifted). When a default matters, confirm it against the installed version: `python -c "import multiqc; print(multiqc.__version__)"` and check that version's `config_defaults.yaml`.

If code throws an error, run `multiqc --help` and adapt flags to the installed version rather than retrying.

# Automated QC Reports with MultiQC

**"Aggregate QC results into one report"** -> Walk a directory of tool outputs, parse the metrics those tools already wrote, and render one interactive HTML report plus a parseable `multiqc_data/` directory.
- CLI: `multiqc <dir>` (scans for recognized tool outputs)

## The Load-Bearing Idea: MultiQC Aggregates, It Does Not Measure

MultiQC computes nothing. It SCRAPES the log/metrics files that FastQC, STAR, Picard, salmon, bcftools, etc. already wrote, re-tabulates those numbers, and renders them. Every value in a report traces back to an upstream tool's output file. Four consequences that drive every real decision below:

- **The report is a triage SNAPSHOT, not a pass/fail gate.** There is no "MultiQC said FAIL -> stop the pipeline." MultiQC has no fail-on-threshold and exits 0 on bad QC. Green/amber/red is either the upstream tool's own status (FastQC writes PASS/WARN/FAIL; MultiQC just displays it) or a threshold a human configured. Gating is a SEPARATE step (see From Report to Gate).
- **Garbage upstream becomes a clean-looking report.** Run a tool with the wrong strandedness, wrong reference, or dedup on amplicon data, and MultiQC faithfully aggregates the wrong numbers into a polished HTML. Polish is not evidence of correctness.
- **An empty report means "nothing matched," not "QC passed."** Point MultiQC at the wrong directory or over-filter modules and it emits a near-empty report with a log warning and exit 0. Always check the sample count in the header against the roster expected.
- **It is only as current as its parsers.** Each module is a hand-written parser keyed to a specific log format. An upstream version bump that changes a header can silently drop a file or mis-map a column.

## Basic Usage

```bash
multiqc results/ -o qc_report/            # scan results/, write qc_report/multiqc_report.html
multiqc results/ -n project_qc -o qc/     # custom report name
multiqc results/ -m fastqc -m star        # ONLY these modules (see scoping below)
multiqc results/ -c multiqc_config.yaml   # reproducible config-driven report
```

## Supported Tools

MultiQC ships parsers for 100+ tools. Common assay groupings:

| Stage | Tools with modules |
|-------|--------------------|
| Read QC | FastQC, fastp, Cutadapt, falco |
| Alignment | STAR, HISAT2, BWA, Bowtie2, samtools, Qualimap, Picard |
| Quantification | featureCounts, Salmon, kallisto, RSeQC |
| Variant calling | bcftools, GATK, Picard, SnpEff, VEP |
| Single-cell | Cell Ranger, STARsolo |

## Module Detection Is Regex - Scope It

Detection runs off `search_patterns.yaml`: each module declares a filename glob/regex (`fn`/`fn_re`) and/or a file-content match (`contents`/`contents_re`, bounded by `num_lines`). Loose patterns (`*.txt`, `*.log`, `*.json`) in a messy directory cause FALSE module matches and PHANTOM samples - a file that is not really that tool's output gets parsed as one. A single file can also satisfy two modules.

Scope explicitly rather than trusting auto-detection across thousands of samples:

```bash
multiqc results/ --ignore "*_tmp/" --ignore "work/"   # drop paths from the search
multiqc results/ -m fastqc -m star -m salmon          # run ONLY named modules
multiqc results/ -e snippy -e custom_content          # run all EXCEPT named modules
```

Tighten an over-loose pattern by overriding `sp:` in the config (`sp: {mytool: {fn: 'real_name_*.txt'}}`). Production configs pin `sp:` and `module_order` instead of relying on detection.

## Sample Names Are Derived, Not Declared

Sample names are NOT read from a manifest. MultiQC derives each name from the matched filename (or a sample column inside the file), then "cleans" it by trimming a ~100-entry default list of extensions (`fn_clean_exts`: `.gz`, `.fastq`, `.bam`, `_fastqc`, ...). This is how `sampleA_R1.fastq.gz`, `sampleA.sorted.bam`, and `sampleA.salmon/` all collapse to one `sampleA` row gathering read, alignment, and quant metrics.

The same mechanism is the #1 large-cohort bug:
- **Merge** - two genuinely different inputs clean to the same name (two lanes both reduce to `sampleA`) and silently overwrite each other's metrics.
- **Split** - one sample appears as several rows because different tools cleaned its name differently (one kept `_L001`, another stripped it).

`multiqc_data/multiqc_sources.txt` maps every parsed file to the sample name it produced - read it first when diagnosing duplicate/missing rows. Controls:

| Need | Control |
|------|---------|
| Add suffixes to strip (keep defaults) | `extra_fn_clean_exts:` in config (do NOT override `fn_clean_exts`, which replaces the defaults) |
| Use the log filename as the name | `--fn_as_s_name` (config `use_filename_as_sample_name`) |
| Disambiguate by directory | `--dirs` / `-d`, `--dirs-depth N` |
| Keep full names, no cleaning | `--fullnames` / `-s` |
| Rename at report time | `--replace-names map.tsv` (pattern -> replacement, two columns) |
| Offer toggleable name sets | `--sample-names headered.tsv` (relabel buttons, does not merge rows) |

## General Statistics and Conditional Formatting Are Configured, Not Authoritative

The General Statistics table is one row per sample with columns each module contributes. Cell colors come from `table_cond_formatting_rules` (numeric `gt`/`lt`/`eq`/`ge`/`le`, string `s_eq`/`s_contains`/`s_ne`). A red ">10% duplication" cell is red because someone wrote that rule (or because a module ships a built-in default rule), not because biology says 10% is bad. Treat formatting as a configured convenience; absence of red is not a pass, and presence of red is not a biological verdict. Column visibility/order/naming are config too (`table_columns_visible`, `table_columns_placement`, `table_columns_name`).

## Large Cohorts: MultiQC Downgrades Automatically

To keep the single HTML openable, MultiQC silently changes rendering as series counts grow. The exact thresholds have moved across versions - verify against the installed `config_defaults.yaml` - but the behaviors are:

| Behavior | Config key | Effect |
|----------|-----------|--------|
| Table -> violin/beeswarm plot | `max_table_rows` (~500) | above the limit the General Stats "table" becomes a distribution plot; per-cell view is lost |
| Interactive plot deferred | `plots_defer_loading_numseries` (~100) | viewer must click to render |
| Interactive -> flat image | `plots_flat_numseries` (moved across versions; HighCharts-era 100, current default much higher) | plots render as static PNG/SVG |

Force a mode for reproducible visuals across cohort sizes: `--flat` / `--interactive` (config `plots_force_flat` / `plots_force_interactive`). At tens of thousands of samples, also scope with `-m`/`--ignore` or split into per-batch reports - MultiQC holds all parsed data in memory before rendering.

## Custom Content (Injecting Custom Metrics)

Two mechanisms; `--custom-data-file` does NOT exist.

- **`_mqc` suffix** - any file named `*_mqc.{tsv,csv,txt,yaml,json,png,...}` is auto-discovered and rendered with no config. The suffix is what makes it findable.
- **`custom_data` in the config** - define a section with `plot_type` (`bargraph`, `linegraph`, `table`, `generalstats`, `image`, ...) and inline data or a search pattern. `plot_type: generalstats` injects columns straight into General Statistics.

## From Report to Gate (the decision MultiQC does not make)

MultiQC is a viewer; QC GATING is separate. The machine-readable truth lives in `multiqc_data/`: `multiqc_data.json` (all parsed values), per-module `multiqc_*.txt` tables, and `multiqc_general_stats.txt`. Build a gate ON TOP of that file, not by scraping the HTML:

```bash
multiqc results/ -o qc/ --data-format json     # write multiqc_data.json
# a downstream script parses qc/multiqc_data/multiqc_data.json,
# applies thresholds, and exits non-zero / quarantines failing samples.
```

This is the correct division of labor: MultiQC presents; the pipeline (nf-core modules, a purpose-built gater like CheckQC, a Nextflow/Snakemake check, or a parse-and-exit script) decides. Building fail-on-threshold logic inside MultiQC is a category error.

## AI Summaries Send Data Off-Network

MultiQC (1.27+) can prepend an LLM-written natural-language summary (`--ai` / `--ai-summary`, `--ai-summary-full`; providers via `ai_provider`: `seqera`, `openai`, `anthropic`, `aws_bedrock`, `custom`; keys via `OPENAI_API_KEY` / `ANTHROPIC_API_KEY` / `SEQERA_ACCESS_TOKEN`). It is OFF by default. When enabled it transmits the aggregated QC metrics - and, unless `ai_anonymize_samples` is set, the SAMPLE NAMES - to an external API over the internet. For clinical, patient, or embargoed data this can be a data-governance violation; use `--no-ai` to strip AI controls from a shared report, or the in-browser on-demand mode (summary stays in browser local storage, not baked into the distributed HTML). Confirm the exact key spelling against the installed version.

## Reproducibility

- **Pin both the MultiQC version and the upstream tool versions.** Parsers, default thresholds, and column sets shift between releases; a report from 1.30 is not byte-stable against one from 1.14.
- **Pin a config, treat the report as a deliverable.** The nf-core pattern: ship `multiqc_config.yml` locking `title`, `module_order`, sample-name cleaning, and `sp:` patterns; expose `--multiqc_config` to layer a user config on top (both apply, user wins). nf-core also emits a `methods_description_template.yml` so the report carries auto-generated methods text and citations for only the tools that ran, plus a consolidated software-versions table.
- **Cross-check the roster.** If 3 of 100 BAMs failed earlier and produced no metrics, MultiQC reports a clean 97-sample report with no indication 3 are missing. It aggregates what exists and has no notion of an expected sample set.

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| Near-empty report, exit 0 | No files matched a search pattern (wrong dir, over-filtered) | Check header sample count; read `multiqc_sources.txt`; relax `-m`/`--ignore` |
| Two samples merged into one row | Names collide after `fn_clean_exts` cleaning | `extra_fn_clean_exts`, `--dirs`, or `--replace-names`; verify in `multiqc_sources.txt` |
| One sample split across rows | Tools cleaned the name differently | `--fn_as_s_name` or `extra_fn_clean_exts` to normalize |
| Phantom sample / wrong module | Loose pattern matched an unrelated file | `--ignore` the path or tighten `sp:`; restrict with `-m` |
| Metric missing after a tool upgrade | Upstream log-format drift broke the parser | Pin tool + MultiQC versions; check the module changelog |
| "table" rendered as a violin plot | Rows exceeded `max_table_rows` | Raise the limit or split the cohort |
| Sensitive sample names left the network | AI summary enabled | `--no-ai`, or `ai_anonymize_samples`; default is off |

## Related Skills

- read-qc/quality-reports - Generate the FastQC/falco inputs MultiQC aggregates
- read-qc/fastp-workflow - Preprocessing QC that feeds the report
- read-qc/rnaseq-qc - Post-alignment RNA-seq metrics surfaced in MultiQC
- workflows/rnaseq-to-de - Full pipeline that emits a MultiQC report as a deliverable

## References

- Ewels P, Magnusson M, Lundin S, Käller M. MultiQC: summarize analysis results for multiple tools and samples in a single report. Bioinformatics. 2016;32(19):3047-3048. doi:10.1093/bioinformatics/btw354
- MultiQC documentation: docs.seqera.io/multiqc (post-2024 features incl. Plotly plots and AI summaries are documented here and in the GitHub CHANGELOG, not a separate paper)
<!-- END FILE: reporting/automated-qc-reports/SKILL.md -->

## 子目录：reporting/figure-export

<!-- BEGIN FILE: reporting/figure-export/SKILL.md -->
---
name: bio-reporting-figure-export
description: Exports publication-ready figures with the correct vector/raster split, embedded editable fonts, color-space-robust palettes, and journal-correct sizing and resolution in matplotlib and ggplot2. Use when preparing figures for journal submission, exporting a dense single-cell or GWAS plot without producing an unopenable vector file, or fixing fonts and colors that break in print.
tool_type: mixed
primary_tool: matplotlib
goal_approach_exempt: true
---

## Version Compatibility

Reference examples tested with: matplotlib 3.8+, numpy 1.26+, ggplot2 3.5+, ggrastr 1.0+, ragg 1.2+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show matplotlib` then `help(matplotlib.figure.Figure.savefig)`; introspect `matplotlib.rcParams` if a key is renamed
- R: `packageVersion('ggplot2')` then `?ggsave`

If code throws ImportError, AttributeError, or TypeError, introspect the installed package and adapt the example to match the actual API rather than retrying.

# Publication-Ready Figure Export

**"Export this figure for the journal"** -> Save the plot so each part of it survives production: vector structure stays crisp, the dense data layer stays a reasonable file size, text stays editable, and color survives the print conversion.
- Python: `fig.savefig('fig.pdf', dpi=600)` with publication rcParams set
- R: `ggsave('fig.pdf', width=89, units='mm', device=cairo_pdf)`

## The Load-Bearing Idea: A Figure Is Four Layers

A publication figure is not one object; it is four superimposed layers, and export means giving each the representation it needs:

1. **Vector structure** - axes, ticks, spines, gridlines, fit lines, error bars, annotations. Resolution-independent; must stay vector so the typesetter can scale it to 89 mm without pixelation.
2. **Raster data layer** - the dense part: a scatter with 10^5-10^7 points, a heatmap, a micrograph. Drawing a million points as a million vector circles makes a hundreds-of-MB PDF that crashes Illustrator. This layer wants to be pixels.
3. **Type** - every glyph. Editors need it to stay selectable text, not flattened paths or pixels baked into the raster.
4. **Color encoding** - the data-to-color mapping. A scientific choice (perceptual uniformity, color-vision-deficiency safety, grayscale survival) that also interacts with the RGB->CMYK conversion the journal performs without asking.

The expert move is the **hybrid figure**: rasterize only layer 2, keep layers 1 and 3 vector, embed editable fonts, and pick a colormap that survives CMYK and grayscale. Everything below serves that.

A reproducibility framing: a figure is a pure function of (data, code, theme, font availability). If any of those is unpinned, the figure is not reproducible.

## The Hybrid Figure (rasterize only the dense layer)

The single most important export skill for single-cell (UMAP/tSNE) and GWAS (Manhattan) figures. A fully-vector million-point scatter is unopenable and gets rejected by the typesetter's RIP; rasterizing just the data layer keeps file size sane while axes and text stay crisp at any zoom.

```python
import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(3.5, 3.0))     # physical inches = the real size control
ax.scatter(x, y, s=2, rasterized=True, zorder=0)   # 10^6 points -> embedded raster
ax.plot(xfit, yfit, color='black', zorder=2)        # stays vector
ax.set_xlabel('UMAP1')                              # stays vector text
fig.savefig('fig.pdf', dpi=600)                     # dpi governs ONLY the rasterized layer
```

In a vector container, `savefig(dpi=...)` sets the resolution of the embedded raster patch and does nothing to the vector parts. `ax.set_rasterization_zorder(0)` rasterizes every artist below a z-order cleanly. In R use `ggrastr::rasterise(geom_point(size=0.3), dpi=600)` (wraps any geom since 0.2.0), keeping `theme_*` vector.

## Fonts: Keep the Text Editable

The most common typesetter complaint about matplotlib PDFs is un-editable text. matplotlib's default `pdf.fonttype` is **3** (Type 3), which embeds glyphs as PostScript procedures that import into Illustrator as ungrouped paths and cannot be re-selected as text. Set **42** (TrueType, wrapped) so text stays selectable and editable. Fix it once, globally:

```python
import matplotlib as mpl
mpl.rcParams['pdf.fonttype'] = 42      # TrueType, editable text in PDF
mpl.rcParams['ps.fonttype']  = 42      # same for EPS/PS
mpl.rcParams['svg.fonttype'] = 'none'  # SVG: emit real <text>, reference the font by name
```

Type 42/TrueType/Type 3 fonts are subsetted (only used glyphs embedded); Type 1 are not. With large glyph sets (CJK) Type 42 can bloat the PDF - a real tradeoff. `svg.fonttype='none'` keeps words editable in Inkscape/Illustrator but the viewer must have the font (else it substitutes); the default `'path'` outlines every glyph (portable, uneditable). Default to editable text; only outline if a specific production desk asks.

In R, the base `pdf()` device has weak font handling and inconsistent cross-OS rendering; use `cairo_pdf` (embeds fonts and supports alpha). For raster, `ragg::agg_png()`/`agg_tiff()` render anti-aliased text better than cairo/base devices. Rule of thumb: `showtext` for vector devices, `ragg` for raster.

## Color Space: The Author Works in RGB, Print Is CMYK

Screens are additive RGB; offset print is subtractive CMYK. matplotlib and ggplot2 author in RGB only - there is no honest path to a true CMYK figure from them. The journal's pipeline converts RGB->CMYK, and because the CMYK gamut is smaller than sRGB, **saturated out-of-gamut colors shift**: pure RGB blue (#0000FF) and vivid green/cyan come back muddier and darker on paper. The neon scatter that pops on screen can print gray.

What to do: pull colors slightly off full saturation (they survive conversion better); soft-proof downstream in Illustrator/Photoshop with a CMYK profile if it matters; and submit RGB - Nature, Science, Cell, and PLOS all explicitly want RGB, not CMYK, because their pipeline does the conversion and online is RGB anyway. If a legacy desk demands CMYK, convert downstream with an explicit profile and re-check that nothing shifted; do not fake it with a colorspace flag.

## Transparency: EPS Has No Alpha

EPS/PostScript do not support alpha - matplotlib's PS backend renders partially-transparent artists as opaque, so an alpha-blended overplotted scatter loses its density information on EPS export. PDF and SVG support alpha natively; prefer them when transparency carries meaning. If a journal forces EPS and transparency is needed, rasterize that layer (`rasterized=True`) or re-encode density as hexbin/2D-KDE. `savefig(transparent=True)` makes the background transparent for slide overlays, not for print.

## DPI Is Meaningless for Vector

A vector PDF has no inherent resolution; it renders sharp at any zoom. DPI governs only raster formats (PNG/TIFF) and the rasterized data layer inside a vector file. The real size control is the **physical figure size** in inches/mm - design at the journal's exact column width from the start; rescaling a 300-dpi raster to 200% halves its effective resolution. Font sizes are in points (1 pt = 1/72 in) independent of DPI.

The DPI tiers follow the IMAGE CLASS, because print reproduces tone via halftone dots (follow the target journal's own numbers; these are the common production convention):

| Image class | DPI | Why |
|-------------|-----|-----|
| Halftone / grayscale / color photo | 300 | continuous tone matches typical screen rulings |
| Combination (halftone + line/text) | 500-600 | thin lines and small type must not jag against toned background |
| Line art (pure black/white) | 1000-1200 | hard edges alias badly at low DPI - or keep it vector and DPI is moot |

`savefig.dpi` is the file resolution; `figure.dpi` is the on-screen resolution. Independently of DPI, very thin strokes (below ~0.25 pt / 0.1 mm) can drop out or thicken unpredictably at the printer's RIP even in a vector file - keep hairlines at or above the journal's minimum line weight.

## Format Decision

| Format | Type | Use for | Avoid for |
|--------|------|---------|-----------|
| PDF | vector(+raster) | default for most journals; hybrid figures; alpha works | - |
| EPS | vector(+raster) | legacy journal requirement | anything with alpha (flattened opaque) |
| SVG | vector | web; handoff to Illustrator/Inkscape for editing | final print at some desks (support varies) |
| TIFF (LZW) | raster, lossless | print production when a journal demands raster (Cell, PLOS) | large vector-friendly line figures |
| PNG | raster, lossless | online, previews, slides, README figures | print where vector is accepted |
| JPEG | raster, LOSSY | photographs only | any figure with text/lines/edges (DCT ringing) |

Never JPEG for line/text figures - block compression rings along high-contrast edges (gray halos on text, fringing on thin lines). For TIFF, use LZW (near-universal reader support) for 8-bit figures; use ZIP for 16-bit (LZW can inflate 16-bit files).

## Colormaps Are a Scientific Choice, Not Taste

Perceptually-uniform maps (viridis, cividis, magma, inferno, plasma) are constructed in CAM02-UCS so equal data steps map to equal perceived steps with monotonically increasing lightness - which is exactly why they survive grayscale and avoid inventing false gradients. **cividis** is additionally optimized so viewers with and without red-green color-vision deficiency see nearly the same image. By contrast, jet/rainbow has non-monotonic luminance that invents bright/dark bands the data does not have (false edges at yellow/cyan) and collapses to mush in grayscale - a correctness failure, not an aesthetic one.

- Sequential map for ordered data; diverging map (with a meaningful midpoint) for signed data; a categorical CVD-safe palette for discrete classes - never a continuous rainbow for categories.
- Use the **Okabe-Ito** 8-color Color Universal Design palette for categories. Red-green CVD affects up to ~8% of males (population-dependent), so add **redundant encoding** (shape + color, linetype + color, direct labels) so color is never the sole channel.
- Run the grayscale-photocopy test: convert to grayscale and confirm the figure still reads.

## Reproducible Export

- **Byte-stable PDFs:** matplotlib stamps a `CreationDate` into every PDF, so two identical runs differ byte-for-byte (noisy git diffs). Pass `metadata={'CreationDate': None}` to `savefig`, or set the `SOURCE_DATE_EPOCH` env var, for deterministic output.
- **`bbox_inches='tight'` breaks exact widths.** It recomputes the bounding box from drawn content, so output dimensions depend on tick-label lengths and the renderer's font metrics - the same script on two machines (different fonts) yields different-sized PDFs, and it can clip annotations. For camera-ready figures at an exact 89 mm, design to size with `constrained_layout=True` and save without `bbox_inches='tight'`; if cropping is unavoidable, pair it with explicit `pad_inches`.
- **Font-availability nondeterminism:** Helvetica on a Mac vs DejaVu Sans on CI gives different glyph widths, line breaks, and (with tight bbox) different sizes. Pin the font or accept the default and don't crop-to-content.
- **Headless rendering:** call `matplotlib.use('Agg')` before importing pyplot on a cluster/CI box, or just use the file backends, so no display is required.

## Journal Specs (verify against the target journal at submission)

Specs change and vary by sub-journal; re-pull the target's author-guideline page. Snapshot, June 2026:

| Journal | Widths | Min DPI | Formats | Color |
|---------|--------|---------|---------|-------|
| Nature | 89 mm single / 183 mm double; <=170 mm tall | 300 photo, 600+ line | vector AI/EPS/PDF preferred; TIFF raster | RGB |
| Science | 5.7 / 12.1 / 18.4 cm | >=300 at final size; vector preferred | Illustrator-openable vector; no PowerPoint | RGB (not CMYK) |
| Cell Press | 85 / 114 / 174 mm | 300 color, 500 grayscale, 1000 line | TIFF (LZW) or vector | RGB |
| PLOS | 789-2250 px wide; <=2625 px tall | 300-600 (do not exceed 600) | TIFF or EPS only; flattened, LZW, no alpha/layers | RGB or grayscale, 8-bit; no CMYK |

PLOS is strictest (8-bit RGB/grayscale TIFF, no alpha channel, no layers). Cell's grayscale (500) and line (1000) tiers exceed the generic numbers - follow the journal's own.

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| Typesetter: "supply editable text" | default Type 3 fonts | `pdf.fonttype=42`, `ps.fonttype=42`, `svg.fonttype='none'` |
| PDF won't open / hundreds of MB | fully-vector dense scatter | rasterize the data layer (`rasterized=True` / `ggrastr::rasterise`) |
| Colors muddy in print | saturated RGB out of CMYK gamut | desaturate slightly; soft-proof; submit RGB |
| Transparency gone on EPS | EPS has no alpha | rasterize that layer, or use PDF/SVG, or hexbin |
| Figure not exactly 89 mm | `bbox_inches='tight'` non-deterministic size | design to size + `constrained_layout`, drop tight bbox |
| Heatmap shows false bands | jet/rainbow non-monotonic luminance | viridis/cividis (sequential), diverging map for signed data |
| Noisy git diff on identical figure | PDF `CreationDate` timestamp | `metadata={'CreationDate': None}` or `SOURCE_DATE_EPOCH` |

## Related Skills

- data-visualization/ggplot2-fundamentals - Building the plots in R
- data-visualization/matplotlib-fundamentals - Building the plots in Python
- data-visualization/multipanel-figures - Composing multi-panel layouts
- data-visualization/color-palettes - Choosing perceptual and CVD-safe palettes
- reporting/publication-tables - The table counterpart to figure export

## References

- Borland D, Taylor RM 2nd. Rainbow Color Map (Still) Considered Harmful. IEEE Comput Graph Appl. 2007;27(2):14-17. doi:10.1109/MCG.2007.323435
- Nuñez JR, Anderton CR, Renslow RS. Optimizing colormaps with consideration for color vision deficiency to enable accurate interpretation of scientific data. PLoS ONE. 2018;13(7):e0199239. doi:10.1371/journal.pone.0199239
- Okabe M, Ito K. Color Universal Design (CUD): how to make figures and presentations friendly to colorblind people. jfly.uni-koeln.de/color/ (8-color CVD-safe palette)
- van der Walt S, Smith N. A Better Default Colormap for Matplotlib. SciPy 2015 (conference talk; viridis/magma/inferno/plasma constructed in CAM02-UCS). bids.github.io/colormap
<!-- END FILE: reporting/figure-export/SKILL.md -->

## 子目录：reporting/jupyter-reports

<!-- BEGIN FILE: reporting/jupyter-reports/SKILL.md -->
---
name: bio-reporting-jupyter-reports
description: Runs parameterized Jupyter notebooks as reproducible batch report generators with papermill, renders them to HTML/PDF with nbconvert, aggregates results across samples, and makes notebook outputs trustworthy. Use when generating per-sample analysis reports, executing a notebook template across many datasets, or fixing notebooks that do not reproduce.
tool_type: python
primary_tool: papermill
goal_approach_exempt: true
---

## Version Compatibility

Reference examples tested with: papermill 2.6+, nbconvert 7.16+, nbclient 0.10+, jupyter-client 8+, scrapbook 0.5+, jupytext 1.16+, nbstripout 0.7+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show papermill` then `help(papermill.execute_notebook)`
- CLI: `papermill --help`, `jupyter nbconvert --help`

If code throws ImportError, AttributeError, or TypeError, introspect the installed package and adapt the example to match the actual API rather than retrying.

# Jupyter Reports with Papermill

**"Generate a reproducible analysis report"** -> Execute a parameterized notebook in a clean kernel, producing an executed-notebook artifact, then render it to a code-hidden HTML/PDF report.
- Python: `papermill.execute_notebook(input, output, parameters={...})`
- CLI: `jupyter nbconvert --execute --to html notebook.ipynb`

## The Load-Bearing Idea: A Notebook Has Hidden State; the Report Is the Executed Artifact

A `.ipynb` is JSON holding cell source, **saved outputs**, and per-cell **execution_count** integers - and those three are decoupled. The kernel is a long-lived process with a mutable namespace, so a user can run cell 5, edit cell 2, rerun it, delete cell 3, run cell 7, and save. The stored outputs then reflect a kernel state that NO top-to-bottom rerun reproduces. Non-monotonic execution counts are the forensic tell.

This is intrinsic to the REPL-on-a-document model, not a bug. The discipline answer is mechanical: **Restart Kernel and Run All** before sharing, so saved outputs equal one clean linear run. papermill and `nbconvert --execute` are that discipline automated - they always spin up a FRESH kernel and run cells strictly in document order, so the output is by construction the record of one clean run. The value is not "trust the saved outputs," it is "regenerate them from a known-empty state."

The empirical case (Pimentel et al.): of ~1.4M GitHub notebooks, only ~24% of those executed finished without error and only ~4% reproduced their stored outputs; ~36% had out-of-order cells, and the dominant failure was `ImportError` - environment, not logic. (It is a public-GitHub corpus, so the absolute rates carry selection bias, but the failure mode is the lesson.) Two lessons: saved outputs are not reproducible (always re-execute), and the #1 fix is pinning the environment (see below).

## Two Artifacts People Conflate

- **Executed notebook** - papermill's output, or `nbconvert --execute --to notebook`. A record of the run: same cells, freshly computed outputs, an injected-parameters cell. For audit/debug/aggregation, not for humans to read as prose.
- **Human report** - `nbconvert --to html/pdf`, optionally `--no-input` to hide code. The rendered deliverable.

A papermill pipeline does both: execute the parameterized notebook -> output `.ipynb` (the evidence) -> convert to HTML/PDF (the report).

## Parameterizing with papermill

Tag ONE cell `parameters` holding defaults. At execution papermill inserts a NEW cell tagged `injected-parameters` immediately AFTER it, containing only the overrides; because Python runs top-to-bottom, the injected cell shadows the defaults.

```python
import papermill as pm
pm.execute_notebook('template.ipynb', 'out/sampleA.ipynb',
                    parameters={'sample_id': 'sampleA', 'fdr_threshold': 0.05})
```

- If NO cell is tagged `parameters`, the injected cell goes at the TOP and downstream references to a param raise NameError. Keep all parameters in one tagged cell.
- **Type coercion is the #1 CLI gotcha.** `-p name value` YAML-parses the value (`-p n 5` -> int, `-p flag true` -> bool); `-r name value` keeps it a raw string (`-r chrom 1` -> `"1"`, needed for sample IDs like `007` or chromosome `"1"`). `-y`/`--parameters_yaml` and `-f`/`--parameters_file` pass lists/dicts. The Python API passes native objects directly with no YAML round-trip - prefer it in pipelines to avoid coercion surprises.

## Execution Controls That Matter in Pipelines

- `execution_timeout` (CLI `--execution-timeout`) - seconds per cell; **default is forever (None)**. A long bioinformatics cell hangs a pipeline silently without this. Set it.
- `kernel_name` / `--kernel` - must be a REGISTERED kernelspec; a mismatch is a top failure cause. The kernel must point at the pinned environment.
- `log_output=True` / `--log-output` - stream each cell's stdout/stderr for CI visibility.
- On a cell exception papermill raises `PapermillExecutionError`, STILL writes the output notebook with the traceback captured (evidence preserved), then exits non-zero. Tag a cell `raises-exception` to allow it to fail without aborting. Fail loud, keep the artifact.
- papermill reads/writes notebooks from `s3://`, `gs://`, `adl://`/`abs://`, and `http(s)://` out of the box (cloud connectors are extras: `pip install papermill[s3]`), so serverless per-sample execution works.
- The fresh-kernel guarantee holds when papermill owns the kernel lifecycle (the default `execute_notebook` path). Advanced patterns that reuse a kernel across notebooks forgo the from-empty-state guarantee - let papermill create the kernel.

## Rendering to a Report

`nbconvert --execute` runs the notebook top-to-bottom in a fresh kernel and writes regenerated outputs - that re-execution, not the saved outputs, is what makes a converted report reproducible.

```bash
jupyter nbconvert --to html --no-input out/sampleA.ipynb     # code-hidden stakeholder report
jupyter nbconvert --execute --to html template.ipynb         # execute then render in one step
jupyter nbconvert --to webpdf out/sampleA.ipynb              # PDF without LaTeX
```

- `--to pdf` needs a LaTeX toolchain (xelatex + pandoc) - the classic CI pain. `--to webpdf` renders HTML then prints via headless Chromium (`pip install nbconvert[webpdf]`, `--allow-chromium-download`) and avoids TeX entirely. The tradeoff: webpdf uses Chromium page geometry, so wide tables and long code lines can clip at the page edge, whereas LaTeX `--to pdf` paginates and wraps better for table-heavy reports.
- `--no-input` hides all code; `--no-prompt` drops the `In[ ]:`/`Out[ ]:` prompts; `TagRemovePreprocessor.remove_cell_tags` strips cells by tag (tag setup cells to remove them). Custom branded layouts use the nbconvert 6+ directory-template system (`--template <name>`).

## Aggregating Results Across Samples

`papermill.record` is deprecated (since papermill 1.0). Use **scrapbook**: in the template, `import scrapbook as sb; sb.glue('auc', 0.91)` records named scraps (and `sb.glue('fig', obj, display=True)` for figures). Downstream, `sb.read_notebooks('reports/').papermill_dataframe` aggregates every executed notebook's scraps into one tidy table - the canonical pattern for looping papermill over a sample sheet then collecting per-sample QC into a cohort summary.

## Version Control: Never Commit Outputs

`.ipynb` is JSON with embedded base64 outputs and `execution_count`, so committing it raw gives giant unreviewable diffs, brutal merge conflicts, and leaked data. Three complementary fixes:

- **nbstripout** - a git clean filter (`*.ipynb filter=nbstripout` in `.gitattributes`) that strips outputs and execution counts on `git add`; the working copy keeps its outputs. Highest-leverage single fix.
- **jupytext** - pairs `.ipynb` with a text twin (`py:percent` is runnable and diff-friendly, or Markdown/`.qmd`); commit the text file as source of truth, regenerate outputs. Lets a notebook be code-reviewed as a normal PR.
- **jupyter-cache** - caches executed outputs keyed by a code-cell hash; the engine Jupyter Book/MyST-NB and Quarto use to skip re-running expensive cells. Right tool when notebooks are doc sources with long compute.

## Reproducible Execution Is Not Reproducible Science

State this plainly: papermill and `nbconvert --execute` guarantee EXECUTION ORDER and a clean kernel - they do NOT guarantee the ENVIRONMENT or numerical determinism. The same parameterized notebook rerun against newer numpy/scanpy, a different BLAS, or an unseeded RNG runs flawlessly and produces DIFFERENT numbers. Order-reproducibility is necessary, not sufficient. Pair papermill with: a pinned environment (conda lockfile / `requirements.txt` with exact versions, ideally a container; the registered kernel must point at it), seeded RNGs for any stochastic step (clustering, UMAP, splits, bootstraps), and pinned reference/DB versions. To catch silent drift, **nbval** (`pytest --nbval`) re-executes and compares new outputs against stored ones in CI.

## When a Notebook Report Is the Wrong Tool

The notebook is the REPORT, not the PIPELINE. Heavy compute (alignment, variant calling, large scanpy integration, anything multi-hour or needing a scheduler, retries, or parallel fan-out) belongs in a workflow manager (Snakemake/Nextflow/WDL). papermill notebooks shine as the final per-sample or per-cohort summary plus figures over already-computed results. Rule of thumb: if `--retry`, `--cluster`, or a DAG is wanted, it is a pipeline; if a parameterized HTML/PDF of results is wanted, it is a papermill report. Note Quarto can consume a `.ipynb` directly, so papermill (parameterize/execute) and Quarto (render) interoperate.

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| Saved outputs do not match a rerun | Out-of-order interactive execution / hidden state | Restart-and-run-all; let papermill/`nbconvert --execute` regenerate |
| Parameter is a bool when a string was wanted | `-p` YAML-parses values | use `-r name value` for raw strings, or the Python API |
| NameError on a parameter | No `parameters`-tagged cell | tag one cell `parameters`; keep all params there |
| Pipeline hangs on one cell | `execution_timeout` defaults to forever | set `execution_timeout` |
| `--to pdf` fails in CI | no LaTeX toolchain | use `--to webpdf` (headless Chromium) |
| Giant notebook diffs / leaked data in git | committing outputs | nbstripout filter or jupytext pairing |
| Reruns months later give different numbers | environment/seed not pinned | pin env + container, seed RNGs, nbval in CI |

## Related Skills

- reporting/quarto-reports - Document-first reporting that can render the same notebooks
- reporting/rmarkdown-reports - R-based literate reports
- workflows/scrnaseq-pipeline - Heavy compute that belongs in a pipeline, with the notebook as the summary report
- single-cell/preprocessing - Analysis embedded inside per-sample notebook templates

## References

- Pimentel JF, Murta L, Braganholo V, Freire J. A large-scale study about quality and reproducibility of Jupyter notebooks. MSR '19, IEEE/ACM. 2019:507-517. doi:10.1109/MSR.2019.00077
- Pimentel JF, Murta L, Braganholo V, Freire J. Understanding and improving the quality and reproducibility of Jupyter notebooks. Empir Softw Eng. 2021;26:65. doi:10.1007/s10664-021-09961-9
- Rule A, Birmingham A, Zuniga C, et al. Ten simple rules for writing and sharing computational analyses in Jupyter Notebooks. PLoS Comput Biol. 2019;15(7):e1007007. doi:10.1371/journal.pcbi.1007007
- Kluyver T, Ragan-Kelley B, Pérez F, et al. Jupyter Notebooks - a publishing format for reproducible computational workflows. ELPUB 2016, IOS Press. 2016:87-90. doi:10.3233/978-1-61499-649-1-87
<!-- END FILE: reporting/jupyter-reports/SKILL.md -->

## 子目录：reporting/publication-tables

<!-- BEGIN FILE: reporting/publication-tables/SKILL.md -->
---
name: bio-reporting-publication-tables
description: Builds publication-ready tables - descriptive Table 1, regression and differential-expression result tables, and supplementary tables - with gtsummary, gt, flextable, and kableExtra (R) or great_tables, pandas, and tableone (Python), choosing the right statistics and the right export format. Use when making a Table 1, exporting a formatted results table for a paper, or writing a gene-symbol-safe supplementary table.
tool_type: mixed
primary_tool: gtsummary
goal_approach_exempt: true
---

## Version Compatibility

Reference examples tested with: gtsummary 2.0+, gt 0.10+, flextable 0.9+, kableExtra 1.4+, great_tables 0.13+, pandas 2.2+, tableone 0.9+, openpyxl 3.1+

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('gtsummary')` then `?tbl_summary` (gtsummary had a major API refresh at v2.0)
- Python: `pip show great_tables` then `help(great_tables.GT.save)`

If code throws an error, introspect the installed package and adapt the example to the actual API rather than retrying.

# Publication-Ready Tables

**"Make my Table 1"** / **"export this results table for the paper"** -> Generate the table programmatically with the right statistics and export it to the journal's target format.
- R: `gtsummary::tbl_summary(data, by=arm)` then `as_flex_table()` -> Word
- Python: `great_tables.GT(df)` -> HTML/PNG; `tableone.TableOne(...)` for a descriptive table

## The Load-Bearing Idea: A Table Is Structure + Precision + the Right Statistics

Three orthogonal concerns, and conflating them is where tables go wrong:

- **Structure** - rows are units (subjects, genes, models), columns are variables/groups, spanners group columns, footnotes/source-notes carry the apparatus. This is the grammar of tables that gt, great_tables, and flextable all encode.
- **Precision** - report to MEANINGFUL precision, not the float default. P-values to 2-3 significant figures or "<0.001"; estimates to the precision the CI supports; percentages to 0-1 decimal. A `3.14159265` mean is noise.
- **The right statistics** - a table is DESCRIPTIVE (summarize the sample: n(%), mean(SD) or median(IQR)) or INFERENTIAL (estimate + CI + test statistic, with the effect size primary and the p-value never alone). Declare which.

The deepest framing, shared with figures: a table is a deterministic function of data + code. Same input + same code -> the same table, byte for byte. Manual edits in Word break this; every number must trace to a line of code. That principle dictates the tooling - generate programmatically and never hand-edit the output.

## Tool Decision (by language and target format)

Target format dominates: Word for most biomedical journals, LaTeX for some genomics/physics venues, HTML for web/preprints/Quarto, CSV/Excel for machine-readable supplements.

| Need | Tool | Path |
|------|------|------|
| R, descriptive Table 1 or regression results | **gtsummary** | `tbl_summary` / `tbl_regression` -> `as_flex_table()` / `as_gt()` |
| R, going to Word/PowerPoint | **flextable** | `save_as_docx()` (most reliable Word fidelity; pairs with officer) |
| R, going to LaTeX/PDF | **gt** or **kableExtra** | `gtsave('x.tex')` / `kbl(format='latex')` |
| R, going to HTML/Quarto | **gt** or **kableExtra** | `as_raw_html()` / `save_kable()` |
| Python, display HTML/image | **great_tables** | `GT(df)` -> `save('x.png')` / `as_raw_html()` |
| Python, going to LaTeX | **pandas Styler** | `df.style.format(...).to_latex()` (pandas 1.3+) |
| Either, classic Table 1 with SMD | **tableone** | `CreateTableOne` (R) / `TableOne` (Python) |
| Machine-readable supplement | **CSV** (preferred) or Excel | gene-symbol-safe export (below) |

`gt` has the broadest R export (HTML/PNG/PDF/RTF/LaTeX/Word). `great_tables.save()` is image+PDF only (HTML via `as_raw_html()`/`write_raw_html()`) - NO native Word or LaTeX, a real limitation vs the R stack. **DT is for interactive exploration and online-only/interactive HTML supplements** - never for a static print/PDF table.

## Table 1 Is Descriptive, Not Inferential

Table 1 reports baseline characteristics so the reader can judge who was studied and how comparable the groups are. It describes the sample; it is not a place to test hypotheses.

**The p-value fallacy (randomized trials):** adding a p-value column comparing arms in a randomized trial is discouraged by CONSORT and statisticians. In a properly randomized trial any baseline imbalance is by definition due to chance, so the test asks whether a difference could have arisen by chance when the assignment WAS by chance - it tests a null already known true. A "significant" baseline p-value is a Type I error by construction; a non-significant one tells nothing new. The right response to a worrying imbalance on a prognostic covariate is to adjust for it (pre-specified ANCOVA covariate), not test it (Senn 1994; CONSORT 2010 item 15). gtsummary's documentation cautions against `add_p()` on a randomized Table 1 for this reason.

- **Randomized Table 1:** no p-value column. To convey balance, use **standardized mean differences (SMD)** - they describe the magnitude of imbalance (|SMD| > 0.1 is a common "notable" rule of thumb) without the inferential fallacy. If a journal or regulator nonetheless requires a baseline comparison column, report it but interpret per Senn: a "significant" baseline difference in a properly randomized trial is a Type I error, not evidence of confounding. Note `add_difference()` compares exactly two groups; for >2 arms, SMD is defined pairwise, so report reference-group or all-pairs SMDs rather than one omnibus value.
- **Observational studies:** a comparison column can be defensible (the groups genuinely may differ), but multiplicity (many rows -> many tests) and "significant does not mean important" still bite, and SMD is the standard balance diagnostic in propensity-score/causal contexts. SMD is preferred over p-values for balance in essentially all cases.

## Continuous Summaries and Missingness

- **mean(SD) vs median(IQR) is distribution-driven.** Symmetric -> mean(SD); skewed/heavy-tailed (most biomarkers, counts, lab values, length-of-stay) -> median(IQR), because the mean is pulled by the tail. gtsummary defaults continuous variables to `median (p25, p75)` - defensible because biomedical variables are usually skewed and normality cannot be assumed column by column. Override per-variable (`statistic = list(age ~ "{mean} ({sd})")`) only after checking normality. Categorical: n(%), and state row% vs column% (baseline tables want column%).
- **Missingness must be SHOWN, not silently dropped.** The cardinal sin is computing percentages on complete cases with no indication rows were dropped - a reader cannot tell 90% from 90%-of-the-60%-with-data. gtsummary's `missing = "ifany"` (default) shows a missing row when any value is absent; `missing_text = "Unknown"` labels it. Never compute denominators that hide missingness; if rows are dropped, report the analyzed N in the table or a footnote.

## Getting Formatting Into the Target Format

- **Word** (the chronic pain point): flextable `save_as_docx()` is the most reliable path; gtsummary `as_flex_table()` then `save_as_docx()` gives the best Word fidelity; gt `gtsave('x.docx')` works but routes through rmarkdown and supports fewer Word styles. great_tables has NO native Word export.
- **LaTeX:** `gtsave('x.tex')`, `kableExtra::kbl(format='latex', booktabs=TRUE)`, or pandas `Styler.to_latex()`.
- **HTML:** gt `as_raw_html()`, great_tables `as_raw_html()`/`write_raw_html()`, kableExtra `save_kable()`.

## The Excel Gene-Symbol Hazard

Excel, with default settings, auto-converts gene symbols and IDs when it PARSES them - opening a CSV, double-clicking, or typing: `SEPT2` -> `2-Sep`, `MARCH1` -> `1-Mar`; RIKEN IDs like `2310009E13` -> `2.31E+13` (precision lost irreversibly); long numeric accessions lose trailing digits to float rounding. (The corruption is a parse behavior, not a write behavior - a string written by openpyxl stays intact until Excel re-interprets it, which is why forcing text format matters.) Ziemann et al. 2016 found ~19.6% of papers with supplementary Excel gene lists affected; Abeysooriya et al. 2021 showed it persisted at 30.9% and drove HGNC to rename the families (SEPT->SEPTIN, MARCH->MARCHF) in 2020 - biology changed its nomenclature to defend against a spreadsheet bug.

When a gene table must reach Excel:
- **Prefer CSV** and tell the consumer to import the gene column as Text (not double-click).
- **If writing .xlsx**, set the gene column to Excel text format `'@'` (openpyxl `cell.number_format = '@'`; XlsxWriter `add_format({'num_format': '@'})` or `write_string()`). Note pandas `Styler.format` is IGNORED by `to_excel` - set the number format via the writer, not the styler.
- **Verify by reopening** - the only sure check.

## Precision and Locale

Report to significant figures, not the float default (`fmt_number(decimals=)`, `pvalue_fun`, Styler `.format('{:.2f}')`). Watch the decimal-comma locale trap: a CSV written in a `,`-decimal locale becomes unparseable elsewhere and Excel may re-misinterpret columns. Write numeric supplements with `.`-decimal and document the locale rather than relying on the system default.

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| p-value column on a randomized Table 1 | testing a null known to be true | drop it; use SMD for balance |
| Percentages do not add up / hide dropped rows | missingness silently excluded | `missing="ifany"`; report analyzed N |
| `SEPT2` became a date in the supplement | Excel auto-conversion | CSV + import-as-text, or `'@'` text format in .xlsx |
| mean(SD) misleads on a skewed variable | wrong summary statistic | median(IQR) for skewed data |
| Word table lost its formatting | exported HTML/LaTeX into Word | flextable `save_as_docx()` |
| great_tables won't save to Word/LaTeX | not supported (image/HTML/PDF only) | use the R stack, or export PNG/HTML |
| Excel export ignored my number format | `Styler.format` is dropped by `to_excel` | set `number_format` via the ExcelWriter |

## Related Skills

- reporting/figure-export - The figure counterpart to table export
- reporting/rmarkdown-reports - Embedding kable/gt tables in R reports
- reporting/quarto-reports - Embedding tables in Quarto reports
- clinical-biostatistics/trial-reporting - CONSORT trial reporting context for Table 1
- differential-expression/de-results - Result tables these formatters present

## References

- Senn S. Testing for baseline balance in clinical trials. Stat Med. 1994;13(17):1715-1726. doi:10.1002/sim.4780131703
- Schulz KF, Altman DG, Moher D; CONSORT Group. CONSORT 2010 Statement: updated guidelines for reporting parallel group randomised trials. BMC Med. 2010;8:18 (item 15, baseline table). doi:10.1186/1741-7015-8-18
- Ziemann M, Eren Y, El-Osta A. Gene name errors are widespread in the scientific literature. Genome Biol. 2016;17:177. doi:10.1186/s13059-016-1044-7
- Abeysooriya M, Soria M, Kasu MS, Ziemann M. Gene name errors: Lessons not learned. PLoS Comput Biol. 2021;17(7):e1008984. doi:10.1371/journal.pcbi.1008984
<!-- END FILE: reporting/publication-tables/SKILL.md -->

## 子目录：reporting/quarto-reports

<!-- BEGIN FILE: reporting/quarto-reports/SKILL.md -->
---
name: bio-reporting-quarto-reports
description: Builds reproducible Quarto reports, presentations, and websites across R, Python, and Julia, with correct engine selection, cache-vs-freeze semantics, native cross-references, parameters, and environment pinning. Use when creating a Quarto report of an analysis, setting up freeze for CI, or debugging cross-references, caching, or working-directory issues.
tool_type: mixed
primary_tool: Quarto
goal_approach_exempt: true
---

## Version Compatibility

Reference examples tested with: Quarto 1.4+, knitr 1.45+, pandoc 3.1+ (bundled), scanpy 1.10+, matplotlib 3.8+

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `quarto --version`, `quarto check`, `quarto render --help`

Some flags and project keys move between Quarto releases (e.g. the file-based `--execute-params`); confirm against `quarto render --help`. If a render fails, run `quarto check` and adapt to the installed version rather than retrying.

# Quarto Reports

**"Create a Quarto analysis report"** -> Write a document mixing code (R/Python/Julia), narrative, and figures that executes through a computational engine and renders to HTML/PDF/Word.
- CLI: `quarto render report.qmd --to html`

## The Pipeline: Engine, Then Pandoc

Both Quarto and R Markdown end at pandoc; what differs is what runs before it. Quarto first picks a computational ENGINE, then pandoc converts to the target format. The engine is a property of the document's languages, and it determines what runtime the rendering machine needs:

- Any `{r}` chunk present -> **knitr** engine (same knit -> md -> pandoc path as R Markdown).
- Only `{python}`/`{julia}` chunks -> **jupyter** engine (executes via a Jupyter kernel, then pandoc).
- **Both R and Python -> knitr + reticulate in ONE process**, so R and Python share a session and can pass objects back and forth. (This is why mixed-language docs "just work" through knitr, not jupyter.)
- Override in YAML: `engine: knitr` / `engine: jupyter`, or pin a kernel with `jupyter: python3`.

The consequence: a Python-only `.qmd` on the jupyter engine needs a registered Jupyter kernel; switched to knitr+reticulate it needs R+reticulate instead. Freeze (below) lets CI skip needing either.

## Cache vs Freeze (the load-bearing distinction)

These solve DIFFERENT problems and are constantly conflated:

> knitr **cache** makes a SINGLE render faster by skipping unchanged chunks. Quarto **freeze** lets a DIFFERENT machine (CI / a website build) render with NO language runtime installed, by reusing stored results.

| | cache (`execute: cache`) | freeze (`execute: freeze`) |
|---|---|---|
| Granularity | per-chunk (knitr) / per-notebook (jupyter-cache) | per-document |
| Problem solved | skip unchanged chunks during a render | skip ALL execution on publish/CI |
| Key | MD5(code + evaluating options); data only via `cache.extra` | source-file hash (`auto`) or never re-run (`true`) |
| Lives in | `*_cache/` (per-doc) | `_freeze/` (project - **commit it**) |
| Runtime needed to render? | yes (still renders, skips some chunks) | **no** - CI renders with no R/Python |
| Invalidates on upstream DATA change? | NO unless `cache.extra` | only via source change (`auto`); data not auto-tracked |
| Scope | within one render | only FULL project renders |

Two edges that trip everyone:
- **The stale-cache footgun:** `cache=TRUE` keys on chunk CODE, not the data it reads. If `data.csv` changes but the chunk code is byte-identical, the cached (stale) result is served. Bind the data into the key: `cache.extra = tools::md5sum('data.csv')`. Cross-chunk dependencies need `dependson='chunkA'` (or `autodep=TRUE`, best-effort).
- **Freeze only acts on FULL project renders.** `quarto render onefile.qmd` and `quarto render subdir/` always execute, ignoring `freeze:`. Arrange CI to do a whole-project `quarto render` so frozen results are honored. Commit `_freeze/` so others render without reproducing the environment.
- **They compose, not conflict.** Freeze decides whether the project re-executes at all; when it does (source changed), knitr cache still skips unchanged chunks within that run.

## The Working-Directory Trap

Chunks execute with the working directory set to the document's folder, NOT the project root (default `execute-dir: file`). So `pd.read_csv('data/x.csv')` works interactively from the project root but breaks on render when the `.qmd` lives in `reports/`. Set `project: execute-dir: project` in `_quarto.yml` to run all chunks from the project root, or use root-anchored paths (`here::here(...)` in R). Never `setwd()` in a chunk - it desyncs figure/cache file placement.

## Cross-References Need the Type Prefix

A Quarto label is a cross-reference ONLY if it starts with a reserved lower-case type prefix: `fig-`, `tbl-`, `sec-`, `eq-`, `lst-`, theorem/callout families. `#| label: scatter` is a dead anchor; `#| label: fig-scatter` is referenceable as `@fig-scatter`. This is the #1 cause of a reference rendering as `?@fig-x`.

````markdown
```{python}
#| label: fig-umap
#| fig-cap: "UMAP embedding colored by cluster"
sc.pl.umap(adata, color='leiden')
```
See @fig-umap. Methods are in @sec-methods.
````

A figure/table from a code cell needs both the prefixed `label` and a `fig-cap`/`tbl-cap`. Section refs need `{#sec-methods}` on the heading AND `number-sections: true`. (Base R Markdown cannot cross-reference at all - that requires bookdown; see reporting/rmarkdown-reports.)

## Parameters: knitr vs jupyter Differ

- **knitr engine:** YAML `params:` block, accessed read-only as `params$x`. Override: `quarto render doc.qmd -P alpha:0.2`.
- **jupyter engine:** there is NO `params:` block. Designate a cell tagged `parameters` (papermill convention) with default assignments; variables are then top-level names. A `params:` YAML block on a jupyter-engine document is silently ignored - a common bug.

````markdown
```{python}
#| tags: [parameters]
input_file = "adata.h5ad"
n_top_genes = 2000
```
````

`-P key:val` overrides on the CLI for both engines.

## Document Basics and Layout

```yaml
---
title: "Analysis Report"
date: today
format:
  html:
    toc: true
    code-fold: true
    embed-resources: true   # one portable self-contained HTML
execute:
  warning: false
  freeze: auto
---
```

Per-cell options use the `#|` hash-pipe (`#| echo: false`, `#| fig-width: 8`, `#| cache: true`). Tabsets group alternative views under `::: {.panel-tabset}`; callouts (`::: {.callout-note}`) flag notes/warnings/tips. Render multiple formats by listing them under `format:` and `quarto render` (or `--to pdf`); PDF needs a TeX engine (`quarto install tinytex`).

## Self-Contained Output

`embed-resources: true` base64-inlines images, CSS, and JS into one portable HTML (maps to pandoc `--embed-resources --standalone`; the older `--self-contained` is deprecated since pandoc 2.19). htmlwidgets (plotly, DT) get inlined too, so an interactive report is one openable file - but each widget library inflates the size.

## The Document Captures Code, Not the Environment

Quarto does not pin package versions or the interpreter. A `.qmd` that renders perfectly today can silently change output next year when a dependency updates. The document gives byte-reproducible output only if code, data, AND versions are unchanged - and versions are not in the repo unless pinned. For real reproducibility add a lockfile/container: `renv::snapshot()` (`renv.lock`) for R, `environment.yml`/`requirements.txt` for Python, Docker/Apptainer when the OS, TeX, and pandoc must also be pinned. **Freeze is not reproducibility** - `_freeze/` lets CI skip execution, but the frozen results came from an uncaptured environment. Record provenance with `sessionInfo()` / `sessioninfo::session_info()` (provenance, not a restore mechanism). For journal submission, Quarto manuscript/journal templates (`quarto-journals/...`) produce article-formatted output from the same source.

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| `@fig-x` renders as `?@fig-x` | label missing the type prefix | name it `fig-x`/`tbl-x` and give it a caption |
| `params:` ignored on a Python doc | jupyter engine uses a `parameters`-tagged cell, not `params:` | tag a cell `parameters`, or use the knitr engine |
| Stale results after editing data | `cache` keys on code, not data | `cache.extra = tools::md5sum('data.csv')` |
| CI re-runs everything despite freeze | single-file/subdir render ignores freeze | do a full-project `quarto render`; commit `_freeze/` |
| `read_csv('data/..')` fails on render | working dir = doc folder, not project root | `execute-dir: project` or `here::here()` |
| Report reproduces differently months later | environment not pinned | renv.lock / conda env / container |
| PDF render fails | no TeX engine | `quarto install tinytex` |

## Related Skills

- reporting/rmarkdown-reports - R-focused alternative; needs bookdown for cross-references
- reporting/jupyter-reports - Parameterized notebook execution Quarto can consume
- reporting/publication-tables - Formatted tables to embed in the report
- data-visualization/ggplot2-fundamentals - Figures for R-engine reports
- data-visualization/interactive-visualization - Interactive dashboards (Quarto `format: dashboard` for static/self-contained, Shiny when a running server is acceptable)

## References

- Knuth DE. Literate Programming. Comput J. 1984;27(2):97-111. doi:10.1093/comjnl/27.2.97
- Xie Y, Allaire JJ, Grolemund G. R Markdown: The Definitive Guide. Chapman & Hall/CRC; 2018
- Xie Y, Dervieux C, Riederer E. R Markdown Cookbook. Chapman & Hall/CRC; 2020
- Quarto documentation: quarto.org (cache/freeze, cross-references, parameters, execution engine)
<!-- END FILE: reporting/quarto-reports/SKILL.md -->

## 子目录：reporting/rmarkdown-reports

<!-- BEGIN FILE: reporting/rmarkdown-reports/SKILL.md -->
---
name: bio-reporting-rmarkdown-reports
description: Creates reproducible R Markdown analysis reports (HTML, PDF, Word) with knitr, covering the render pipeline, the interactive-vs-knit session trap, cache invalidation, bookdown cross-references, parameterization, and environment pinning. Use when generating an R-based analysis report, debugging a report that knits differently than it runs interactively, or fixing caching or cross-references.
tool_type: r
primary_tool: rmarkdown
goal_approach_exempt: true
---

## Version Compatibility

Reference examples tested with: rmarkdown 2.25+, knitr 1.45+, bookdown 0.37+, DESeq2 1.42+, ggplot2 3.5+, DT 0.31+, kableExtra 1.4+

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters

If code throws an error, introspect the installed package (`?rmarkdown::render`, `?knitr::opts_chunk`) and adapt the example to the actual API rather than retrying.

# R Markdown Reports

**"Create an R Markdown report"** -> Write an R-centric document combining code chunks, results, and narrative that knits to HTML/PDF/Word.
- R: `rmarkdown::render('report.Rmd')`, or the Knit button in RStudio

## The Pipeline: knitr, Then Pandoc

An `.Rmd` always renders in two stages: **knitr** executes the chunks and weaves the results into an intermediate `.md`, then **pandoc** converts that `.md` into the target format (LaTeX via a TeX engine for PDF). knitr is the only execution engine for `.Rmd` (other languages run only as knitr engines); it is the successor to Sweave, adding caching, hooks, and markdown hosting. `rmarkdown::render()` orchestrates both stages. Knowing the split explains most failures: a chunk error is knitr; a formatting or cross-reference problem is usually pandoc/bookdown.

## The "Works Interactively, Fails on Knit" Trap

This is the single most common reproducibility surprise. `rmarkdown::render()` defaults to `envir = parent.frame()`, so calling it from the console evaluates chunks in the caller's environment - it can SEE objects sitting in the interactive global env. The RStudio **Knit button does NOT**: it spawns a fresh, clean R session. So a report that relies on a `df` created interactively renders fine via `render()` from the console, then fails when a colleague clicks Knit or CI runs it, because the fresh session has no `df`.

Guards:
- Treat the document as self-sufficient - every object must be CREATED in a chunk, never assumed present.
- To mimic the button before trusting a report, render in isolation: `rmarkdown::render('r.Rmd', envir = new.env())`, or in a fresh process via `callr::r(...)` / `xfun::Rscript_call(rmarkdown::render, ...)`.

## Caching: cache Keys on Code, Not Data

`cache=TRUE` stores a chunk's result in a `*_cache/` dir and reloads it on re-knit if the chunk is "unchanged" - where the cache key is an MD5 of the chunk CODE plus evaluating options. The footgun: if a chunk reads `data.csv` and the FILE changes but the chunk code is byte-identical, the hash is unchanged and knitr serves the STALE cached result. Bind the data into the key:

````r
```{r de-analysis, cache=TRUE, cache.extra=tools::md5sum('counts.csv')}
dds <- DESeq(DESeqDataSetFromMatrix(counts, metadata, ~ condition))
```
````

Cross-chunk dependencies are not tracked automatically either: if chunk B uses an object from chunk A, editing A does not invalidate B's cache by default - declare `dependson='de-analysis'` (or `autodep=TRUE`, best-effort).

## The Working-Directory Trap

knitr evaluates chunks with the working directory set to the directory of the `.Rmd`, NOT the project root. So `read.csv('data/x.csv')` works when run interactively from the project root but breaks on knit if the `.Rmd` lives in `reports/`. Fixes, in order of preference: `here::here('data/x.csv')` (anchors to the project root, most robust); `knitr::opts_knit$set(root.dir = '...')` in the setup chunk (note `opts_knit`, not `opts_chunk`); or `rmarkdown::render('r.Rmd', knit_root_dir = '...')`. Never `setwd()` in a chunk - it desyncs figure/cache file placement.

## Cross-References Require bookdown

Base rmarkdown CANNOT cross-reference figures, tables, sections, or equations. Use a bookdown output format - `bookdown::html_document2`, `bookdown::pdf_document2`, `bookdown::word_document2` - which add numbering and `\@ref(type:label)`. Two hard requirements: the figure/table chunk must be LABELED, and it must have a CAPTION (`fig.cap=`); a captionless figure is emitted unnumbered and cannot be referenced.

````yaml
output:
  bookdown::html_document2:
    toc: true
````
````r
```{r volcano, fig.cap="Volcano plot of differential expression"}
plot(res$log2FoldChange, -log10(res$pvalue))
```
See Figure \@ref(fig:volcano).
````

(Quarto has native cross-references without bookdown - see reporting/quarto-reports.)

## Parameterized Reports

Declare defaults in YAML and read them as a read-only list:

````yaml
params:
  count_file: "counts.csv"
  fdr_threshold: 0.05
````
````r
counts <- read.csv(params$count_file)
```
````

Override per render and loop over samples:

```r
rmarkdown::render('report.Rmd', params = list(count_file = 'sampleB.csv'),
                  output_file = 'sampleB_report.html')
```

`rmarkdown::render(..., params = 'ask')` launches the "Knit with Parameters" UI.

## Document Basics, Tables, and Output

```yaml
---
title: "RNA-seq Report"
date: "`r Sys.Date()`"
output:
  html_document:
    toc: true
    toc_float: true
    code_folding: hide
    self_contained: true   # base64-embed assets into one portable HTML
---
```

A `setup` chunk with `knitr::opts_chunk$set(echo=TRUE, message=FALSE, warning=FALSE, fig.width=10)` sets document-wide defaults. Section tabs use `## Results {.tabset}`. Inline results splice with `` `r ...` ``. For tables: `knitr::kable()` + `kableExtra` for STATIC publication tables; `DT::datatable()` for INTERACTIVE HTML exploration - DT is a JavaScript widget, not for print/PDF, and it inflates the HTML (see reporting/publication-tables for the formatted-table decision). `self_contained: true` (default for `html_document`) embeds all assets into one portable file at a size cost; htmlwidgets get inlined too.

## The Document Captures Code, Not the Environment

rmarkdown does not pin package versions or R itself. A report that knits perfectly today can change output next year when a dependency updates. The document gives byte-reproducible output only if code, data, AND versions are unchanged - and versions are not in the repo unless pinned. Add `renv::snapshot()` (`renv.lock`, commit it) for package pinning, and a container (Docker/Apptainer) when the OS, TeX, and pandoc must also be fixed. End the report with `sessionInfo()` / `sessioninfo::session_info()` - provenance for the reader, not a restore mechanism. Seed any stochastic step (`set.seed`).

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| Renders from console, fails on Knit | `render` sees globals (`parent.frame`); Knit uses a fresh session | make every object chunk-created; test with `envir=new.env()` |
| Stale results after editing data | `cache` keys on code, not data | `cache.extra=tools::md5sum('data.csv')` |
| `read.csv('data/..')` fails on knit | working dir = `.Rmd` folder, not project root | `here::here()` or `knit_root_dir=` |
| `\@ref(fig:x)` shows as `??` | base rmarkdown can't cross-ref, or no caption/label | bookdown `*_document2` + chunk label + `fig.cap` |
| Edited upstream chunk, downstream cache stale | dependencies not tracked | `dependson=` or `autodep=TRUE` |
| Report changes output months later | environment not pinned | renv.lock + container; seed RNGs |
| PDF knit fails | no LaTeX | `tinytex::install_tinytex()` |

## Related Skills

- reporting/quarto-reports - Successor with native cross-references and multi-language support
- reporting/publication-tables - Formatted static tables (gt/gtsummary/flextable) for reports
- reporting/figure-export - Exporting the report's figures for publication
- differential-expression/de-results - The analysis these reports typically present

## References

- Xie Y. Dynamic Documents with R and knitr. 2nd ed. Chapman & Hall/CRC; 2015
- Xie Y. bookdown: Authoring Books and Technical Documents with R Markdown. Chapman & Hall/CRC; 2016
- Xie Y, Allaire JJ, Grolemund G. R Markdown: The Definitive Guide. Chapman & Hall/CRC; 2018
- Xie Y, Dervieux C, Riederer E. R Markdown Cookbook. Chapman & Hall/CRC; 2020
<!-- END FILE: reporting/rmarkdown-reports/SKILL.md -->

<!-- END CATEGORY: reporting -->

