---
slug: bio-pathway-analysis-integrated
version: 1.0.0
displayName: "通路分析 / Functional enrichment analysis"
name: bio-pathway-analysis-integrated
summary: >-
  中文：通路分析综合技能，整合 6 个相关专题，覆盖功能富集分析：ORA、GSEA、SPIA通路拓扑，覆盖GO、KEGG、Reactome、WikiPathways、MSigDB。 English: Integrated Functional enrichment analysis skill covering 6 related topics, including Functional enrichment analysis: ORA, GSEA, SPIA pathway topology across GO, KEGG, Reactome, WikiPathways, MSigDB.
description: >-
  中文：这是一个面向通路分析的综合生物信息学 Skill，整合当前分类下 6 个相关专题能力。它用于根据研究问题、数据类型和分析阶段，选择合适的方法与工具，规划从输入检查、预处理、核心分析到质量控制、统计解释和结果报告的完整流程。重点覆盖：功能富集分析：ORA、GSEA、SPIA通路拓扑，覆盖GO、KEGG、Reactome、WikiPathways、MSigDB。当用户提供相关实验数据、测序结果、表格或研究问题时，它会帮助判断分析目标与前置条件，给出工具选择、关键参数、输入输出、常见失败原因、结果解读和可复现建议。主要工具包括：ReactomePA, clusterProfiler, enrichplot。该 Skill 提供分析设计与实施指导，不替代对具体数据质量、生物学背景和最终结论的人工审查。
  English: This is an integrated bioinformatics Skill for Functional enrichment analysis, combining 6 related topic areas. It helps users choose appropriate methods and tools based on the research question, data type, and analysis stage, and plan an end-to-end workflow from input validation and preprocessing through core analysis, quality control, statistical interpretation, and reporting. It covers Functional enrichment analysis: ORA, GSEA, SPIA pathway topology across GO, KEGG, Reactome, WikiPathways, MSigDB. For relevant experimental data, sequencing results, tables, or research questions, it clarifies prerequisites, recommends tools and parameters, describes expected inputs and outputs, explains common failure modes, and supports reproducible analysis. Primary tools include: ReactomePA, clusterProfiler, enrichplot. It provides methodological and implementation guidance; final data-quality assessment and biological conclusions still require human review.
---

# pathway-analysis 分类 Skill 整合版

> 本文件整合同一主分类目录下 6 个子目录中的 SKILL.md 内容。
> 各子目录正文按原文保留，并通过标题和边界标记进行区分；源文件中的元数据块未被改写。

---

<!-- BEGIN CATEGORY: pathway-analysis -->

## 子目录：pathway-analysis/enrichment-visualization

<!-- BEGIN FILE: pathway-analysis/enrichment-visualization/SKILL.md -->
---
name: bio-pathway-enrichment-visualization
description: Turns an enrichResult or gseaResult from clusterProfiler/enrichplot into a figure that collapses or shows gene-set redundancy, using dotplot, barplot, cnetplot, emapplot, treeplot, ridgeplot, gseaplot2, and upsetplot. Covers why a default top-20 GO dotplot is one biological theme drawn twenty times (the DAG/nesting guarantees redundant overlapping terms), so the figure is a modeling choice between SHOWING redundancy (pairwise_termsim -> emapplot/treeplot) and DELETING it (simplify/REVIGO); why cnetplot/emapplot/treeplot need pairwise_termsim first; why enrichplot ships no barplot for gseaResult (a bar cannot carry a signed NES); why GeneRatio is not fold enrichment; and why showCategory silently truncates. Use when plotting ORA or GSEA results, collapsing redundant GO terms visually, encoding a dotplot, or building a publication enrichment figure. Statistics come from go-enrichment and gsea; generic ggplot -> data-visualization/ggplot2-fundamentals.
tool_type: r
primary_tool: enrichplot
---

## Version Compatibility

Reference examples tested with: enrichplot 1.30+, clusterProfiler 4.18+, ggplot2 3.5+.

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

The single biggest hazard here is the cnetplot/emapplot/goplot API churn. enrichplot 1.25.5 (2024-10) moved these to the ggtangle backend and DROPPED several old arguments (`cex_label_category`, `cex_label_gene`, `circular`, `colorEdge`, `group`/`group_category`/`group_legend`). The examples target the post-churn API (1.30+), but installed bases span three argument generations - run `?cnetplot` / `?emapplot` and adapt rather than pinning one generation.

# Enrichment Visualization

**"Make a figure from my enrichment results"** -> Render an enrichResult or gseaResult with enrichplot, choosing how the gene-set REDUNDANCY is handled - because a raw top-N plot is one biological theme drawn N times, not N findings.
- R: `dotplot(ego, showCategory=20)`; redundancy as structure via `emapplot(pairwise_termsim(ego))`

Scope: turn an `enrichResult`/`gseaResult`/`compareClusterResult` into a figure, and decide whether to SHOW or DELETE redundancy. The ORA/GSEA statistics that produce the objects -> go-enrichment, gsea. The method-selection fork lives in the category README; this skill already explains the redundancy (DAG/nesting) it renders. `simplify()` existence (the GO-DAG dedup) -> go-enrichment. Generic ggplot2 grammar (scales, themes, faceting) -> data-visualization/ggplot2-fundamentals. Cytoscape UI mechanics -> data-visualization/network-visualization.

## The Single Most Important Modern Insight -- An Enrichment Figure Is a Modeling Choice, Not a Rendering of a Table

The default `dotplot(ego, showCategory=20)` is almost never twenty findings. The GO DAG and nested pathway databases guarantee that a real signal surfaces as a CLUSTER of near-identical overlapping terms driven by the same handful of genes: if "mitotic cell cycle" is enriched, then "cell cycle process," "cell cycle," "cell division," and a dozen ancestors and siblings enrich too. Sorting by p-value floats that redundant cluster to the top, so the figure shows ONE theme twenty times and crowds out the second and third themes entirely. The reader infers twenty independent findings; the figure lies by omission.

So the load-bearing question is never "which plotting function" but three decisions:

1. **How is the redundancy collapsed?** SHOW it as structure (`pairwise_termsim` -> `emapplot`/`treeplot`, or EnrichmentMap) so the cluster size conveys support, or DELETE it (`simplify()` for a shorter GO list, REVIGO for a flat-list treemap). Plotting raw top-20 with no collapse step is the error the whole skill exists to prevent.
2. **Is the direction kept?** GSEA results are SIGNED (NES > 0 = activated, NES < 0 = suppressed). Any GSEA figure that maps magnitude to a bar height or |NES|, or colors by a one-sided p-value ramp, silently merges activation and suppression. enrichplot deliberately ships NO barplot method for `gseaResult` for exactly this reason - a bar from zero cannot carry a sign.
3. **Does the caption admit truncation?** `showCategory=20` is a window, not a census. If 200 terms passed FDR it is a 10% sample chosen by whatever `orderBy` used. Report the total significant count and the similarity `method=`/`min_edge=` settings - two honest analysts get different emapplot modules from the same object.

## The Object Model -- What Gets Plotted

Every enrichplot function dispatches on the S4 class of its input, and the SAME function name encodes different things by class:

- `enrichResult` (ORA: enrichGO/enrichKEGG/enricher) - columns `ID, Description, GeneRatio, BgRatio, pvalue, p.adjust, qvalue, geneID, Count`.
- `gseaResult` (GSEA: gseGO/gseKEGG/GSEA) - columns `ID, Description, setSize, enrichmentScore, NES, pvalue, p.adjust, qvalue, rank, leading_edge, core_enrichment`, plus the `@geneList` slot (the ranked named vector that drove the analysis).
- `compareClusterResult` (compareCluster) - stacked results across gene lists; the substrate for faceted dotplots.

Encoding definitions (verified): **GeneRatio = k/n** (k = query genes annotated to the term, n = query genes mapped to any term; stored as the string `"k/n"`). **Count = k** (the numerator alone). **BgRatio = M/N** (M = universe genes annotated to the term, N = universe genes mapped). **Fold enrichment = (k/n)/(M/N)** = `GeneRatio/BgRatio`. GeneRatio is NOT effect size: a giant term (M=800) can post a large GeneRatio with trivial enrichment, while a small term (M=5, k=3) shows a modest GeneRatio but huge fold enrichment. The p-value, not GeneRatio, is the test statistic. dotplot can put `GeneRatio` OR `Count` on x; size = Count, color = p.adjust by default.

## Tool Taxonomy

| Plot / method | Encodes | Class | Redundancy handling | Direction-aware |
|---------------|---------|-------|---------------------|-----------------|
| dotplot | GeneRatio (x), Count (size), p.adjust (color) | ORA + GSEA | none (raw top-N) | only if x/color = NES |
| barplot | Count or GeneRatio (height), p.adjust (color) | ORA ONLY | none | no - misuse for GSEA |
| cnetplot | gene<->term bipartite net; item color = fold change | ORA + GSEA | shows shared genes (gene side) | yes (item color) |
| emapplot | term net; edge = gene overlap; clusters = redundant groups | ORA + GSEA | SHOWS redundancy (term side) | node color = p.adjust |
| treeplot | hierarchical Ward clusters of terms | ORA + GSEA | COLLAPSES into nCluster groups | node color = p.adjust |
| ridgeplot | leading-edge metric density per set | GSEA ONLY | per-set | YES (left/right shift) |
| gseaplot2 | running ES + hit ticks + ranked metric | GSEA ONLY | single / few sets | YES (peak sign) |
| upsetplot | gene-overlap combinations (ORA); per-set metric boxplots (GSEA) | ORA + GSEA | quantifies overlap | metric boxplots for GSEA |
| goplot | induced GO DAG subgraph | GO ONLY | exposes DAG nesting | no |
| heatplot | gene x term matrix, color by fold change | ORA + GSEA | flattened cnetplot | yes (fold change) |
| simplify() | semantic dedup of GO terms | GO ORA/GSEA | DELETES redundant terms (lives in go-enrichment) | n/a |
| REVIGO / EnrichmentMap | non-redundant subset / node-edge map | any list | DELETE / SHOW + annotate | EnrichmentMap by sign |

Citations: dotplot/barplot/cnet/tree/upset/goplot/heatplot are enrichplot, paper-of-record clusterProfiler 4.0 (Wu 2021 *The Innovation* 2:100141). emapplot reimplements EnrichmentMap (Merico 2010 *PLoS One* 5:e13984; protocol Reimand 2019 *Nat Protoc* 14:482). simplify/Wang use GOSemSim (Yu 2010 *Bioinformatics* 26:976). REVIGO (Supek 2011 *PLoS One* 6:e21800). ridgeplot/gseaplot2 display the ES Subramanian 2005 *PNAS* 102:15545 defined.

## Decision Tree by Intent

| Intent | Do this | Why / avoid |
|--------|---------|-------------|
| First look at ORA results | `dotplot(simplify(ego))` - collapse GO redundancy THEN dotplot | avoid raw `dotplot(ego, showCategory=20)` (redundant cluster floats up) |
| Many significant terms, show the structure | `pairwise_termsim()` -> `emapplot` (topology) or `treeplot` (named clusters) | the redundancy becomes the message, not hidden |
| Hundreds of sets, manuscript figure | EnrichmentMap (Cytoscape; Reimand 2019 protocol) -> data-visualization/network-visualization | a top-20 list is indefensible at that scale |
| Flat GO-ID + p-value list from a non-clusterProfiler tool | REVIGO (treemap / MDS) | external semantic collapse |
| GSEA overview, all sets | `ridgeplot(gse)` | direction + shape preserved; never a barplot of NES |
| GSEA, one pathway in detail | `gseaplot2(gse, geneSetID=1)` | the running ES; a single number hides the shape |
| Compare several pathways' running scores | `gseaplot2(gse, geneSetID=1:3)` | overlay in one panel |
| Which genes bridge multiple terms | `cnetplot` (<=5-8 terms) or `heatplot` | a 20-term cnetplot is a hairball |
| Need effect size, not GeneRatio | `dotplot(ego, x='FoldEnrichment')` or compute `GeneRatio/BgRatio` | a dot far right on GeneRatio is not strong over-representation |
| Compare conditions / gene lists | `dotplot(ck) + facet_grid(~Cluster)` on compareCluster | one model, faceted panels |
| term similarity for KEGG/Reactome/custom | `pairwise_termsim(x, method='JC')` (default) | Wang/Resnik need the GO DAG |
| term similarity for GO, want DAG-awareness | `pairwise_termsim(x, method='Wang', semData=godata(...))` | JC sees only gene overlap |
| The ORA/GSEA statistics themselves | -> go-enrichment, gsea | upstream, not visualization |

## Dotplot -- the Three-Channel Summary

`dotplot(object, x='geneRatio', color='p.adjust', showCategory=10, orderBy='x', label_format=30)`. The terms are ordered by `orderBy='x'` (the x variable), NOT by p-value, so by default the TOP dot is the highest GeneRatio, not the most significant. State the ordering or set it.

```r
dotplot(ego, showCategory = 20)                                       # x = GeneRatio, size = Count, color = p.adjust
dotplot(ego, x = 'FoldEnrichment', showCategory = 20)                 # effect size = (k/n)/(M/N), not GeneRatio
dotplot(gse, x = 'NES', showCategory = 20, color = 'p.adjust')        # signed GSEA summary (dotplot dispatches on gseaResult)
dotplot(gse, showCategory = 20, split = '.sign') + facet_grid(~.sign) # split GSEA up vs down
```

For a compareClusterResult, `dotplot.compareClusterResult` defaults `showCategory=5` per cluster and `includeAll=TRUE` (a term top-N in any cluster appears in every column).

## Barplot -- ORA Only

`barplot(height, x='Count', color='p.adjust', showCategory=8)`. There is NO `barplot` method for `gseaResult` (verified) - forcing a bar onto GSEA drops the NES sign. For signed GSEA use a NES dotplot, ridgeplot, or gseaplot2.

```r
barplot(ego, showCategory = 15)                          # height = Count, color = p.adjust
barplot(ego, x = 'GeneRatio', showCategory = 15)
```

## Show the Redundancy -- pairwise_termsim then emapplot/treeplot

**Goal:** Reveal that a block of near-identical enriched terms is one biological theme, by clustering terms on gene-set overlap and drawing the clusters.

**Approach:** Populate the term-similarity matrix first with `pairwise_termsim` (emapplot/treeplot READ `x@termsim` and do NOT compute it), then draw it as a force-directed map (emapplot, shows topology) or a deterministic Ward tree (treeplot, named clusters). The similarity `method=` and `min_edge=` are modeling choices that change the picture.

```r
ego_ts <- pairwise_termsim(ego)                          # JC (Jaccard on gene overlap), the default; any gene-set type
emapplot(ego_ts, showCategory = 30)                      # nodes = terms, edges = overlap >= min_edge (0.2), clusters = redundant groups
treeplot(ego_ts, showCategory = 30, nCluster = 5)        # deterministic Ward clustering into 5 labeled groups

# GO terms, DAG-aware similarity (Wang sees parent/child closeness even with modest gene overlap)
ego_ts <- pairwise_termsim(ego, method = 'Wang', semData = GOSemSim::godata('org.Hs.eg.db', ont = 'BP'))
```

`pairwise_termsim` `method` is exactly one of `{Resnik, Lin, Rel, Jiang, Wang, JC}`, default `JC`. Resnik/Lin/Rel/Jiang/Wang are GO-ONLY and need a `GOSemSimDATA` object; JC works for any gene-set type. Lower `min_edge` and everything connects to everything (the "if every node touches every node, the result IS redundant" diagnostic); raise it and only the strongest overlaps survive.

## Gene-Concept Network (cnetplot)

**Goal:** Show which genes are shared across enriched terms - the redundancy seen from the gene side - and their direction.

**Approach:** Draw a bipartite term-to-gene network, mapping the gene-node color to fold change. Keep to 5-8 terms or it collapses into a hairball. The ggtangle-era arguments differ from older tutorials - introspect before pinning args.

```r
cnetplot(ego, showCategory = 5)                          # ggtangle backend (enrichplot >= 1.25.5)
cnetplot(ego, showCategory = 5, foldChange = gene_list)  # gene color by fold change; node_label = 'all'|'category'|'item'|'none'
# OLDER installed versions used: cnetplot(ego, foldChange=fc, circular=TRUE, colorEdge=TRUE) -- those args were REMOVED; run ?cnetplot
```

## GSEA Plots -- ridgeplot, gseaplot2

`ridgeplot(gse, showCategory=30, fill='p.adjust', core_enrichment=TRUE, orderBy='NES')` draws, per set, a density of the `@geneList` metric values of its LEADING-EDGE genes. Shifted right = up-ranked, left = down-ranked, bimodal = the set straddles both extremes (often too broad). `ridgeplot` needs the `ggridges` package (an enrichplot Suggests-only dependency) or it errors. `gseaplot2(gse, geneSetID, subplots=1:3)` stacks the running ES curve, the hit ticks, and the ranked-metric profile; `geneSetID` is required and accepts an index, a vector (`1:3` to overlay), or an ID string.

```r
ridgeplot(gse, showCategory = 20)                        # direction + shape; the honest GSEA overview
gseaplot2(gse, geneSetID = 1:3, pvalue_table = TRUE)     # overlay three sets' running scores
```

## Specialized Views -- upsetplot, goplot, heatplot

```r
upsetplot(ego, n = 10)                                   # gene-overlap combinations across terms (gseaResult gives per-set metric boxplots)
goplot(ego)                                              # GO-ONLY: the induced DAG subgraph; needs the ggarchery package (enrichplot Suggests)
heatplot(ego, foldChange = gene_list, showCategory = 15) # gene x term matrix, color by direction; a flattened cnetplot
```

## All Outputs Are ggplot Objects

Every enrichplot function returns a ggplot object, so chain ggplot2 modifiers and save with `ggsave`. Generic grammar (themes, scales, faceting) lives in data-visualization/ggplot2-fundamentals.

```r
p <- dotplot(ego, showCategory = 20) + scale_color_viridis_c() + ggtitle('GO BP enrichment')
ggsave('fig.pdf', p, width = 10, height = 8)
```

## Per-Method Failure Modes

### Raw top-20 redundancy artifact
**Trigger:** `dotplot(ego, showCategory=20)` straight from enrichGO on GO results. **Mechanism:** the GO DAG guarantees a real signal surfaces as a nested cluster of overlapping terms driven by the same genes. **Symptom:** twenty bars/dots that are "cell cycle," "cell cycle process," "mitotic cell cycle," "cell division" - one theme repeated. **Fix:** `simplify()` for a shorter list, or `pairwise_termsim` -> `emapplot`/`treeplot` to show the structure, or REVIGO/EnrichmentMap.

### Missing pairwise_termsim
**Trigger:** `emapplot(ego)` or `treeplot(ego)` without the precursor. **Mechanism:** these read `x@termsim`, an empty slot until populated. **Symptom:** an error about a missing termsim slot, or an empty map. **Fix:** `ego_ts <- pairwise_termsim(ego)` first, every time.

### Barplot on gseaResult / dropped NES sign
**Trigger:** coercing a gseaResult to a data frame and bar/dot-plotting |NES| or a p-value ramp. **Mechanism:** a bar from zero is unsigned; |NES| merges activated and suppressed pathways. **Symptom:** a figure that hides that half the pathways are suppressed. **Fix:** there is deliberately no barplot for gseaResult; use a diverging color-by-NES dotplot, ridgeplot, or gseaplot2.

### GeneRatio read as effect size
**Trigger:** "term A has GeneRatio 0.6 so it is strongly over-represented." **Mechanism:** GeneRatio is k/n, not the fold enrichment (k/n)/(M/N). **Symptom:** a giant uninformative term ranked above a small specifically-enriched one. **Fix:** use `x='FoldEnrichment'` (or `GeneRatio/BgRatio`) when specificity is the point; report the p-value as the test statistic.

### Default-ordering misread
**Trigger:** reading the top dot of a default dotplot as "most significant." **Mechanism:** `orderBy='x'` orders by the x variable (GeneRatio), not p.adjust. **Symptom:** a low-significance high-GeneRatio term presented as the headline. **Fix:** order/color by p.adjust explicitly, or state the ordering in the caption.

### Over-trimmed showCategory
**Trigger:** `showCategory=20` when 200 terms passed FDR. **Mechanism:** showCategory truncates to a top-N window by whatever orderBy used. **Symptom:** a 10% sample read as the complete result. **Fix:** report the total significant count and selection criterion in the caption; the figure is a window, not a census.

### Pinned deprecated enrichplot args
**Trigger:** copying `circular=TRUE`, `colorEdge=TRUE`, `cex_label_gene=`, `cex_label_category=`, or `group_category=` from a pre-2024 tutorial. **Mechanism:** enrichplot 1.25.5+ moved cnet/emap/goplot to ggtangle and removed those arguments. **Symptom:** an unused-argument error or a silently ignored arg. **Fix:** `?cnetplot` / `?emapplot` and use the current arguments (`color_item`, `size_category`, `node_label`, `node_label_size`, `min_edge`).

### Wang/IC similarity on non-GO results
**Trigger:** `pairwise_termsim(kegg_result, method='Wang')`. **Mechanism:** Resnik/Lin/Rel/Jiang/Wang require the GO DAG and a GOSemSimDATA object. **Symptom:** an error or a meaningless similarity for KEGG/Reactome/custom sets. **Fix:** use `method='JC'` (gene overlap) for any non-GO gene set.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| `showCategory = 10-30` | enrichplot defaults (dotplot 10, emapplot/treeplot 30) | more terms become unreadable; always report the total significant count alongside |
| `pairwise_termsim(method='JC')` default | enrichplot | Jaccard on gene overlap; works for any gene-set type; non-JC are GO-only |
| `simplify(cutoff=0.7)` | clusterProfiler / GOSemSim (Yu 2010 *Bioinformatics* 26:976) | semantic-similarity redundancy cutoff; lower keeps more terms (lives in go-enrichment) |
| `emapplot(min_edge=0.2)` | enrichplot | draw a term-term edge only above this overlap; if everything still connects, the result is redundant |
| `treeplot(nCluster=5, cluster_method='ward.D')` | enrichplot | deterministic Ward cut into 5 named groups; an explicit, reproducible alternative to emapplot's stochastic layout |
| cnetplot <=5-8 terms | enrichplot (showCategory default 5) | the bipartite layout hairballs past ~8 terms |
| diverging color centered at 0 for NES | Subramanian 2005 *PNAS* 102:15545 | NES is signed; a sequential p-value ramp hides activation vs suppression |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| emapplot/treeplot error about a missing termsim slot | skipped `pairwise_termsim()` | run `x <- pairwise_termsim(x)` first |
| `unused argument (circular = TRUE)` in cnetplot | pre-1.25.5 args under ggtangle backend | `?cnetplot`; use `color_item`/`node_label`/`size_category` |
| no applicable method for 'barplot' on gseaResult | GSEA has no barplot method by design | use a NES dotplot, ridgeplot, or gseaplot2 |
| top dot is not the most significant | default `orderBy='x'` orders by GeneRatio | order/color by p.adjust explicitly |
| dotplot terms all look modestly enriched | GeneRatio is not fold enrichment | `dotplot(ego, x='FoldEnrichment')` |
| Wang similarity errors on KEGG terms | IC/graph methods need the GO DAG | `pairwise_termsim(x, method='JC')` |
| gene labels are Entrez IDs not symbols | object not made readable | `setReadable(x, OrgDb, 'ENTREZID')` before plotting |
| two analysts get different emapplot modules | different `method=` / `min_edge=` | record both in the caption; the clustering is a choice |

## References

- Wu T, Hu E, Xu S, et al. 2021. clusterProfiler 4.0: A universal enrichment tool for interpreting omics data. *The Innovation* 2:100141.
- Yu G, Li F, Qin Y, Bo X, Wu Y, Wang S. 2010. GOSemSim: an R package for measuring semantic similarity among GO terms and gene products. *Bioinformatics* 26:976-978.
- Supek F, Bosnjak M, Skunca N, Smuc T. 2011. REVIGO summarizes and visualizes long lists of gene ontology terms. *PLoS One* 6:e21800.
- Merico D, Isserlin R, Stueker O, Emili A, Bader GD. 2010. Enrichment Map: a network-based method for gene-set enrichment visualization and interpretation. *PLoS One* 5:e13984.
- Reimand J, Isserlin R, Voisin V, et al. 2019. Pathway enrichment analysis and visualization of omics data using g:Profiler, GSEA, Cytoscape and EnrichmentMap. *Nat Protoc* 14:482-517.
- Subramanian A, Tamayo P, Mootha VK, et al. 2005. Gene set enrichment analysis: a knowledge-based approach for interpreting genome-wide expression profiles. *PNAS* 102:15545-15550.

## Related Skills

- go-enrichment - Produces the enrichResult; owns simplify() the GO-DAG dedup
- gsea - Produces the gseaResult; owns the enrichment score and leading-edge concept
- kegg-pathways - KEGG enrichResult/gseaResult to plot (pathview pathway-diagram overlay lives there)
- reactome-pathways - Reactome enrichResult/gseaResult to plot
- wikipathways - WikiPathways enrichResult/gseaResult to plot
- data-visualization/ggplot2-fundamentals - Generic ggplot2 grammar for the returned objects
- workflows/expression-to-pathways - End-to-end DE-to-enrichment-to-figure pipeline
<!-- END FILE: pathway-analysis/enrichment-visualization/SKILL.md -->

## 子目录：pathway-analysis/go-enrichment

<!-- BEGIN FILE: pathway-analysis/go-enrichment/SKILL.md -->
---
name: bio-pathway-go-enrichment
description: Runs Gene Ontology over-representation analysis (ORA) on a gene LIST with clusterProfiler enrichGO, the one-sided hypergeometric/Fisher 2x2 test phyper(k-1, M, N-M, n, lower.tail=FALSE). Covers why the BACKGROUND universe (not the gene list) is the null and decides significance, why omitting universe= is a bug, why enrichGO defaults to ont='MF' not 'BP', why pvalueCutoff filters p.adjust not raw p, why ORA discards effect magnitude and inherits GO-DAG true-path redundancy (simplify, topGO), why RNA-seq gene-length bias inflates long-gene terms (GOseq Wallenius), plus GeneRatio/BgRatio, bitr ID mapping, minGSSize/maxGSSize, groupGO. Use when a pre-selected gene list (DE hits, co-expression module, screen, GWAS-mapped) needs GO annotation. For a ranked no-cutoff analysis see gsea; for other databases see kegg-pathways, reactome-pathways, wikipathways; DE source is differential-expression/de-results; plots in enrichment-visualization.
tool_type: r
primary_tool: clusterProfiler
---

## Version Compatibility

Reference examples tested with: clusterProfiler 4.18.4+, org.Hs.eg.db 3.22+ (goseq 1.54+ for the length-bias snippet).

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

GO annotation lives in the local org.*.eg.db OrgDb and GO.db, both pinned to the Bioconductor release, so a GO ORA is reproducible given the package versions - record `packageVersion('org.Hs.eg.db')` and `packageVersion('GO.db')` with results. enrichGO moved no core arguments recently, but several plot helpers migrated to enrichplot in clusterProfiler 4.x (those live in enrichment-visualization).

# GO Over-Representation Analysis

**"Which biological processes are enriched in my gene list?"** -> Test each GO term for over-representation of the query genes against a defined background with the one-sided hypergeometric test - because the BACKGROUND universe, not the gene list, is what decides which terms look significant.
- R: `enrichGO(gene, universe, OrgDb, keyType='ENTREZID', ont='BP')`

Scope: hypergeometric ORA of a gene LIST against GO terms, with background-universe selection, ID conversion, GO-DAG redundancy reduction, RNA-seq length-bias correction, and the generic `enricher` test for custom gene sets. A ranked-list / no-cutoff analysis -> gsea. KEGG/Reactome/WikiPathways gene sets -> kegg-pathways, reactome-pathways, wikipathways. The DE list source -> differential-expression/de-results. Plots -> enrichment-visualization.

## The Single Most Important Modern Insight -- ORA Is a Competitive 2x2 Hypergeometric Test Whose Null IS the Chosen Universe

ORA does not answer "which pathways are in my gene list". It is a competitive gene-sampling test (Goeman & Buhlmann 2007 *Bioinformatics* 23:980): of the genes flagged (the foreground), are more annotated to term T than expected when drawing the same number at random from the universe? The p-value is the upper tail of the hypergeometric, computed verbatim by DOSE/clusterProfiler as `phyper(k-1, M, N-M, n, lower.tail=FALSE)` = P(X>=k), the one-sided Fisher exact test on the 2x2 table. Here N = universe genes carrying any GO annotation, M = universe genes in T, n = foreground genes annotated, k = the overlap (the `Count` column). The report columns are GeneRatio = k/n and BgRatio = M/N - both denominators restricted to ANNOTATED genes - and fold enrichment = GeneRatio/BgRatio.

Three consequences drive every misuse:

1. **The universe is the null, not a setting.** Change N or M and every p-value changes. Omitting `universe=` defaults N to ALL annotated genes (~18k for human BP); if the assay only measured ~12k genes, terms for tissue-restricted and lowly-expressed genes go spuriously significant. Omitting `universe=` is a bug, not a default - set it to the genes that COULD have entered the foreground (the tested-gene set), map foreground and universe identically, and report N. The whole-genome background is defensible only when every gene truly could have been detected (Wijesooriya 2022; Timmons 2015).
2. **ORA throws away magnitude and inherits the GO DAG.** A gene is in or out at one threshold (no effect size), so a 2000-gene term at 1.2x fold can beat a 12-gene term at 4x on p-value alone - always read fold enrichment alongside p.adjust. The true-path rule propagates each annotation to all ancestors, so one real signal lights up a whole lineage ("cell cycle", "cell cycle process", "mitotic cell cycle" together); those tests are positively correlated, BH still valid but the term list over-reports. Resolve with `simplify()` (semantic collapse, per ontology) or topGO elim/weight (decorrelation in the test).
3. **The deliverable is never "the enriched pathways."** It is a correctly-backgrounded, effect-sized, redundancy-resolved short list of HYPOTHESES - and it cannot be used to validate the DE list that produced it (circular: the terms are a deterministic function of the same genes; Timmons 2015).

## ORA vs GSEA (the central fork)

ORA needs a pre-selected LIST plus a BACKGROUND and binarizes significant/not; GSEA needs a RANKED vector of ALL genes and no cutoff. Pick by whether a ranking exists and whether the cutoff would be arbitrary. The full three-generations taxonomy (ORA vs FCS vs topology) and competitive-vs-self-contained null theory live in the category README - this skill owns the ORA/GO slice.

| Scenario | Method | Why |
|----------|--------|-----|
| All genes carry a DE statistic, cutoff would be arbitrary | GSEA (gseGO) -> gsea | uses the full ranking; no threshold |
| Pre-selected list (co-expression module, GWAS-mapped, screen hits, markers) | ORA (enrichGO) | no ranking available; ORA is appropriate |
| Very small list (< ~15-20 genes) | low ORA power; report fold enrichment + counts, consider GSEA | hypergeometric power collapses on tiny lists |
| RNA-seq DE list with length/selection bias | GOseq (Wallenius) | length-corrected ORA; standard ORA inflates long-gene terms |

## Tool Taxonomy

| Source / method | Citation | Mechanism / role | When |
|-----------------|----------|------------------|------|
| enrichGO (clusterProfiler) | Yu 2012 *OMICS* 16:284; Wu 2021 *Innovation* 2:100141 | one-sided hypergeometric per GO term; local OrgDb | the default ORA workhorse for a gene list |
| GO DAG (BP/MF/CC) | Ashburner 2000 *Nat Genet* 25:25 | three DAGs; true-path propagation to ancestors | the annotation structure being tested |
| simplify (GOSemSim) | Wang 2007 *Bioinformatics* 23:1274 | semantic-similarity de-redundancy, per ontology | collapse redundant ancestor lineages, keep calibrated p/FDR |
| topGO elim/weight/weight01 | Alexa 2006 *Bioinformatics* 22:1600 | decorrelates the GO graph inside the test | specificity-resolved short list (treat scores as ranking, not FDR) |
| GOseq | Young 2010 *Genome Biol* 11:R14 | Wallenius noncentral hypergeometric weighted by a length PWF | RNA-seq DE with gene-length/selection bias |
| enricher (clusterProfiler) | Yu 2012 *OMICS* 16:284 | same hypergeometric engine on a custom TERM2GENE | any gene set (MSigDB, in-house) not in a DB function |
| gseGO / GSEA | (route -> gsea) | rank-based running-sum, permutation null | a ranking exists; no arbitrary cutoff |

## Run the GO ORA

**Goal:** Find GO terms over-represented in a gene list relative to the genes that could have been selected.

**Approach:** Build the foreground and the universe with the SAME ID mapping, set `ont` explicitly (the source default is 'MF'), pass `universe=` (omitting it is a bug), and read fold enrichment alongside p.adjust.

```r
library(clusterProfiler)
library(org.Hs.eg.db)

ego <- enrichGO(gene          = gene_list,        # foreground ENTREZ IDs
                universe      = universe_ids,     # tested-gene set, mapped identically -- NOT the genome
                OrgDb         = org.Hs.eg.db,
                keyType       = 'ENTREZID',
                ont           = 'BP',             # SET explicitly: source default is 'MF', not 'BP'
                pAdjustMethod = 'BH',
                pvalueCutoff  = 0.05,             # filters p.adjust (despite the name), not raw pvalue
                qvalueCutoff  = 0.2,
                minGSSize     = 10,
                maxGSSize     = 500,
                readable      = TRUE)             # map ENTREZ -> SYMBOL in the output
```

The returned `enrichResult` has columns `ID, Description, GeneRatio, BgRatio, pvalue, p.adjust, qvalue, geneID, Count` (plus `ONTOLOGY` when `ont='ALL'`). `pvalueCutoff` filters the ADJUSTED p, so an empty table usually means the cutoff or the universe, not biology - inspect everything with `pvalueCutoff=1, qvalueCutoff=1`.

## Build the Foreground and Universe from DE Results

**Goal:** Turn a DE table into the foreground gene vector and the matched background universe.

**Approach:** Filter the DE table to the hits for the foreground; take the genes that were actually TESTED for the universe (DESeq2: rows with non-NA pvalue survive independent filtering); map both with the same `bitr` call. The DE mechanics and the `$padj`/`$adj.P.Val` column choice live in differential-expression/de-results.

```r
de <- read.csv('de_results.csv')

sig_genes  <- de$gene_id[de$padj < 0.05 & abs(de$log2FoldChange) > 1]   # foreground = hits
all_tested <- de$gene_id[!is.na(de$pvalue)]                            # universe = tested genes, NOT all rows, NOT the genome

fg_map <- bitr(sig_genes,  fromType = 'SYMBOL', toType = 'ENTREZID', OrgDb = org.Hs.eg.db)
bg_map <- bitr(all_tested, fromType = 'SYMBOL', toType = 'ENTREZID', OrgDb = org.Hs.eg.db)

gene_list    <- unique(fg_map$ENTREZID)   # deduplicate one-to-many maps before counting
universe_ids <- unique(bg_map$ENTREZID)
```

`bitr` one-to-many maps produce duplicate rows that inflate `Count`; deduplicate. If more than ~15% of genes fail to convert the result is unreliable - report the conversion rate. Mixed up- and down-regulated genes cancel in one list: run ORA separately per direction when direction matters.

## Reduce GO-DAG Redundancy with simplify

**Goal:** Collapse the redundant ancestor lineage so one biological signal is one entry, not a dozen.

**Approach:** `simplify()` removes terms whose semantic similarity to a kept term exceeds the cutoff. It operates on ONE ontology (GOSemSim defines similarity within a single DAG), so run BP/MF/CC separately and simplify each - it does NOT de-redundify an `ont='ALL'` object.

```r
ego_bp <- enrichGO(gene_list, universe = universe_ids, OrgDb = org.Hs.eg.db, keyType = 'ENTREZID', ont = 'BP', readable = TRUE)
ego_bp <- simplify(ego_bp, cutoff = 0.7, by = 'p.adjust', select_fun = min, measure = 'Wang')
```

`measure='Wang'` (the default) is graph-topology-based and stable across annotation releases; IC-based measures ('Resnik', 'Lin', 'Jiang', 'Rel') shift with the annotation corpus. topGO elim/weight01 is the alternative that decorrelates inside the test, returning a specificity-resolved list directly - but its conditioned p-values are best treated as a ranking, not calibrated FDR (Alexa 2006).

## Correct RNA-seq Length Bias with GOseq

**Goal:** Stop long, highly-expressed genes from looking enriched for a purely technical reason.

**Approach:** DE-detection power scales with read count, which scales with transcript length and expression, so the foreground is enriched for long genes - and RPKM/TMM normalization does NOT fix it (it corrects abundance, not detection power). GOseq fits a probability weighting function (PWF) over the bias variable and tests with the Wallenius noncentral hypergeometric (Young 2010). The input is a NAMED 0/1 vector over ALL tested genes; goseq returns UNADJUSTED p-values, so apply BH afterward.

```r
library(goseq)

all_genes <- de$gene_id[!is.na(de$pvalue)]
de_genes  <- as.integer(all_genes %in% sig_genes)   # named binary vector over the tested set
names(de_genes) <- all_genes

pwf <- nullp(de_genes, 'hg38', 'ensGene')           # fits the length PWF; inspect the fit plot
go  <- goseq(pwf, 'hg38', 'ensGene', method = 'Wallenius')   # default; 'Hypergeometric' ignores bias (= standard ORA)
go$padj <- p.adjust(go$over_represented_pvalue, method = 'BH')   # goseq does NOT BH-correct internally
```

GSEA on a length-neutral ranking statistic (the moderated t / Wald z) is largely immune to this bias - one more reason to consider gsea for RNA-seq.

## All Three Ontologies and a Descriptive Breakdown

`ont='ALL'` runs BP/MF/CC separately and rbinds them with an `ONTOLOGY` column (`pool=FALSE` default; `pool=TRUE` treats the three as one set). `groupGO` is NOT a test - it classifies genes at a fixed DAG level for a GO-slim overview (counts, no p-values); never read its counts as significance.

```r
ego_all <- enrichGO(gene_list, universe = universe_ids, OrgDb = org.Hs.eg.db, keyType = 'ENTREZID', ont = 'ALL', readable = TRUE)
ggo     <- groupGO(gene_list, OrgDb = org.Hs.eg.db, keyType = 'ENTREZID', ont = 'BP', level = 3, readable = TRUE)
```

## Custom Gene Sets with enricher

For gene sets not covered by a DB function (MSigDB collections, in-house sets), `enricher` runs the SAME hypergeometric engine against a two-column TERM2GENE table; pass the same explicit `universe`.

```r
ego_custom <- enricher(gene_list, TERM2GENE = t2g, universe = universe_ids,
                       pvalueCutoff = 0.05, pAdjustMethod = 'BH', minGSSize = 10, maxGSSize = 500, qvalueCutoff = 0.2)
```

## Other Organisms

Swap the OrgDb: `org.Mm.eg.db` (mouse), `org.Dr.eg.db` (zebrafish), `org.Sc.sgd.db` (yeast, `keyType='ORF'`). Check usable key types with `keytypes(OrgDb)`.

## Per-Method Failure Modes

### Whole-genome or default universe
**Trigger:** omitting `universe=`, or passing the genome when the assay measured fewer genes. **Mechanism:** N defaults to all annotated genes, inflating the denominator with genes that never could have been selected. **Symptom:** a confident table where tissue-restricted / lowly-expressed-gene terms dominate. **Fix:** set `universe=` to the tested-gene set, map foreground and universe identically, report N.

### p read without fold enrichment (term-size trap)
**Trigger:** ranking results by p.adjust alone. **Mechanism:** a 2000-gene term has enormous power at tiny fold enrichment; p scales with term size. **Symptom:** vague broad terms ("cellular process") top the list, specific terms buried. **Fix:** read fold enrichment = (k/n)/(M/N) alongside p.adjust; trim extremes with minGSSize=10, maxGSSize=500.

### Redundant ancestor lineage counted as findings
**Trigger:** reporting "cell cycle", "cell cycle process", "mitotic cell cycle" as separate discoveries. **Mechanism:** true-path propagation lights up a whole lineage from one signal; the tests are positively correlated. **Symptom:** the top 20 is one biological theme repeated. **Fix:** `simplify()` per ontology, or topGO weight01; never count lineage members as independent hits.

### RNA-seq length / selection bias
**Trigger:** standard ORA on an RNA-seq DE list without length correction. **Mechanism:** detection power scales with count ~ length/expression; TMM/RPKM fixes abundance, not power. **Symptom:** long-gene categories (ECM, adhesion) enriched, short-gene (ribosomal) depleted - and it survives FDR. **Fix:** GOseq with a length PWF + `method='Wallenius'`, then BH; or GSEA on a bias-neutral statistic.

### Wrong ID type or silent gene loss
**Trigger:** passing ENSEMBL/SYMBOL with a mismatched `keyType`, or not checking the bitr conversion rate. **Mechanism:** unmapped IDs are dropped, shrinking the foreground; one-to-many maps inflate Count. **Symptom:** "no gene can be mapped", or a suspiciously small/large Count. **Fix:** match `keyType` to one of `keytypes(OrgDb)`, deduplicate after bitr, report conversion rate (flag >15% loss).

### pvalueCutoff misread as raw-p filter
**Trigger:** concluding "no significant terms" when strong raw p exists. **Mechanism:** `pvalueCutoff` filters p.adjust, not pvalue. **Symptom:** an empty table despite plausible signal. **Fix:** inspect with `pvalueCutoff=1, qvalueCutoff=1`, then judge on p.adjust.

### simplify on ont='ALL'
**Trigger:** calling `simplify()` on an `ont='ALL'` object. **Mechanism:** semantic similarity is defined within ONE ontology, not across BP/MF/CC. **Symptom:** redundancy not removed, or an error. **Fix:** run BP/MF/CC separately and simplify each.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| `pvalueCutoff = 0.05` | clusterProfiler default | filters on p.adjust (NOT raw pvalue); standard FDR gate |
| `qvalueCutoff = 0.2` | clusterProfiler default | secondary q-value gate; loosen to 1 to inspect all terms |
| `pAdjustMethod = 'BH'` | Benjamini-Hochberg | controls FDR; valid under the positive dependence of true-path-correlated terms (Bonferroni is needlessly strict here) |
| `minGSSize = 10` | enrichGO default | drop tiny sets that overfit and are noisy |
| `maxGSSize = 500` | enrichGO default | drop huge general sets that always "enrich" with trivial fold |
| `simplify(cutoff = 0.7)` | GOSemSim/Wang | semantic-similarity redundancy cutoff; lower keeps more terms, higher is more aggressive |
| fold enrichment > 2 | heuristic | (k/n)/(M/N); a rough "strong" flag, never a substitute for p.adjust |
| ID-conversion loss > 15% | heuristic | above this the foreground is too eroded to trust; report the rate |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| `--> No gene can be mapped` | wrong keyType / OrgDb, or IDs not in the OrgDb | match keyType to `keytypes(OrgDb)`; bitr to ENTREZID first |
| Empty result table | `pvalueCutoff` filters p.adjust; or universe too large; or IDs lost | set cutoffs to 1 to inspect; fix the universe; check conversion rate |
| Vague broad terms dominate | ranking by p alone (term-size trap) | read fold enrichment; trim with minGSSize/maxGSSize |
| Many redundant ancestor terms | GO-DAG true-path propagation | `simplify()` per ontology, or topGO weight01 |
| simplify does nothing / errors on ALL | similarity is per-ontology | run BP/MF/CC separately |
| Description column shows IDs not names | not readable | `readable=TRUE` or `setReadable(ego, OrgDb, 'ENTREZID')` |
| Tested MF when expecting BP | enrichGO default `ont='MF'` | set `ont` explicitly every call |

## References

- Ashburner M, Ball CA, Blake JA, et al. 2000. Gene Ontology: tool for the unification of biology. *Nat Genet* 25:25-29.
- Yu G, Wang LG, Han Y, He QY. 2012. clusterProfiler: an R package for comparing biological themes among gene clusters. *OMICS* 16:284-287.
- Wu T, Hu E, Xu S, et al. 2021. clusterProfiler 4.0: a universal enrichment tool for interpreting omics data. *The Innovation* 2(3):100141.
- Goeman JJ, Buhlmann P. 2007. Analyzing gene expression data in terms of gene sets: methodological issues. *Bioinformatics* 23:980-987.
- Alexa A, Rahnenfuhrer J, Lengauer T. 2006. Improved scoring of functional groups from gene expression data by decorrelating GO graph structure. *Bioinformatics* 22(13):1600-1607.
- Young MD, Wakefield MJ, Smyth GK, Oshlack A. 2010. Gene ontology analysis for RNA-seq: accounting for selection bias. *Genome Biol* 11(2):R14.
- Wang JZ, Du Z, Payattakool R, et al. 2007. A new method to measure the semantic similarity of GO terms. *Bioinformatics* 23(10):1274-1281.
- Timmons JA, Szkop KJ, Gallagher IJ. 2015. Multiple sources of bias confound functional enrichment analysis of global -omics data. *Genome Biol* 16:186.
- Wijesooriya K, Jadaan SA, Perera KL, et al. 2022. Urgent need for consistent standards in functional enrichment analysis. *PLoS Comput Biol* 18(3):e1009935.

## Related Skills

- gsea - Ranked-list GSEA alternative when a full ranking exists and a cutoff is arbitrary
- kegg-pathways - KEGG pathway and module enrichment
- reactome-pathways - Reactome curated-pathway enrichment
- wikipathways - WikiPathways community-pathway enrichment
- enrichment-visualization - Dot/bar/cnet/emap/tree plots of enrichment results
- differential-expression/de-results - Source of the gene list and the tested-gene universe
- database-access/entrez-fetch - Fetch gene annotations / ID maps from NCBI
- workflows/expression-to-pathways - End-to-end DE-to-enrichment pipeline
<!-- END FILE: pathway-analysis/go-enrichment/SKILL.md -->

## 子目录：pathway-analysis/gsea

<!-- BEGIN FILE: pathway-analysis/gsea/SKILL.md -->
---
name: bio-pathway-gsea
description: Tests a ranked gene vector for coordinated expression shifts in GO, KEGG, Reactome, or MSigDB gene sets with clusterProfiler's gseGO, gseKEGG, gsePathway, and GSEA (fgseaMultilevel engine), and scores per-sample pathway activity with ssGSEA and GSVA. Covers why a GSEA result is a deterministic function of three implicit choices (the ranking STATISTIC, the weight exponent p, and which LABELS are permuted), why the input must be a NAMED vector sorted DECREASING by a signed variance-calibrated metric (DESeq2 stat, limma t) not a raw p-value that erases direction, why preranked gene-permutation is anti-conservative for correlated sets (CAMERA is the fix), why nPerm is gone (eps governs tiny p), and why set.seed is required. Use when every gene carries a DE statistic, when a hard cutoff is arbitrary, or when ORA finds nothing. For gene-list ORA see go-enrichment; the ranking statistic comes from differential-expression/de-results.
tool_type: r
primary_tool: clusterProfiler
---

## Version Compatibility

Reference examples tested with: clusterProfiler 4.18.4+, org.Hs.eg.db 3.22+, msigdbr 26+, fgsea 1.36+.

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

gseKEGG queries the live KEGG REST API, so the same code returns different results as KEGG updates; pin the run date. gseGO/gsePathway and MSigDB GSEA use local annotation (`org.*.eg.db`, `reactome.db`, msigdbr) and are reproducible given the package version. The single source of truth for versions is this block, not headings.

# Gene Set Enrichment Analysis (GSEA)

**"Which pathways shift coordinately across my full ranked gene list, with no cutoff?"** -> Walk a weighted running-sum down the genome-wide ranking and test whether each gene set piles up at one END - because that score reports the structure of YOUR ranking, so the ranking metric and the permutation type, not the gene sets, decide the result.
- R: `gseGO(geneList, OrgDb, ont)`, `gseKEGG(geneList, organism)`, `GSEA(geneList, TERM2GENE)`

Scope: threshold-free Functional Class Scoring (FCS) of a RANKED vector - the running-sum ES, the ranking-metric choice, the permutation null, NES/FDR, the leading edge, and per-sample ssGSEA/GSVA scores. A pre-selected unranked gene LIST -> go-enrichment (ORA). The ranking statistic source -> differential-expression/de-results. KEGG/Reactome/WikiPathways database semantics -> kegg-pathways, reactome-pathways, wikipathways. Plots -> enrichment-visualization.

## The Single Most Important Modern Insight -- A GSEA Result Is a Deterministic Function of Three Usually-Implicit Choices: the Ranking Statistic, the Weight Exponent p, and the Permuted Labels

GSEA is not a discovery about biology - it is the running-sum's report on the ranking it was handed. The weighted enrichment score (Subramanian 2005; the default `exponent=1` weights each hit by the gene's statistic magnitude) asks exactly one question: do the members of a set pile up at one END of YOUR ranking. So the result is fixed by three decisions tutorials usually leave silent, and Wijesooriya 2022 found most published GSEA papers report none of them.

1. **The ranking statistic IS the experiment.** Rank by a signed, variance-calibrated metric (DESeq2 `stat`, limma moderated `t`) - sign gives direction, variance-calibration sinks noisy low-information genes to the middle. Ranking by a RAW p-value erases the sign, so up- and down-regulated genes collapse together and NES becomes uninterpretable. Ranking by bare log2FC lets a handful of low-count genes with huge unstable fold changes hijack the leading edge. A bad ranking is faithfully reported as a ranking artifact.
2. **The permutation type sets validity.** Phenotype (sample-label) permutation preserves the gene-gene correlation that co-regulated pathways are made of - it is the gold standard for type-I error control because it preserves that correlation, but needs the expression matrix and adequate n per group (~>=7); below that n its validity degrades. clusterProfiler/fgsea preranked are FORCED into GENE permutation, which treats genes as independent, destroys that correlation, and is ANTI-CONSERVATIVE: it returns "significant" pathways that are nothing but co-expression. Accept it, report it, and prefer CAMERA when the design matrix is available (full competitive/self-contained theory in the category README).
3. **The honesty is bounded by reporting.** Log the ranking metric, the exponent p, the permutation type, the gene-set collection and its version/date, the size filters, and the multiple-testing method. Without those, the result is unfalsifiable.

## Tool Taxonomy

| Method | Citation | Mechanism / role | When |
|--------|----------|------------------|------|
| Preranked GSEA (gseGO/gseKEGG/GSEA) | Subramanian 2005 *PNAS* 102:15545; Mootha 2003 *Nat Genet* 34:267 | weighted running-sum ES over a ranked vector; gene-permutation null | the common case: a ranked statistic for all genes, no matrix |
| fgsea engine | Korotkevich 2021 *bioRxiv* 060012 (preprint) | fgseaMultilevel; resolves tiny p accurately down to `eps` | the engine under `by='fgsea'` (default); what gives sub-1/nperm p-values |
| Phenotype-permutation GSEA | Subramanian 2005 *PNAS* 102:15545 | shuffles sample labels; preserves gene-gene correlation | matrix + phenotype + ~>=7/group; the gold-standard competitive test |
| CAMERA | Wu & Smyth 2012 *NAR* 40:e133 | competitive, VIF-corrects inter-gene correlation analytically | matrix + design; want a correlation-honest competitive test |
| ROAST / fry | Wu 2010 *Bioinformatics* 26:2176 | self-contained rotation test; valid at any n | matrix + design, tiny n, "is the set DE at all" |
| ssGSEA | Barbie 2009 *Nature* 462:108 | per-sample rank-based enrichment score | a per-sample pathway-activity matrix (no contrast test) |
| GSVA | Hanzelmann 2013 *BMC Bioinformatics* 14:7 | unsupervised per-sample, per-set kernel/CDF score | per-sample features for clustering/survival/ML |

## Decision Tree by Scenario

| Scenario | Recommended | Why |
|----------|-------------|-----|
| Ranked statistic for ALL genes, cutoff would be arbitrary | preranked `gseGO`/`gseKEGG`/`GSEA` | threshold-free; the common case (report gene-permutation) |
| Pre-selected unranked list (module, GWAS hits, screen) | ORA -> go-enrichment | no genome-wide ranking exists |
| Function annotation, broad GO coverage | `gseGO` | GO is the broadest local resource |
| Metabolic / signaling pathways | `gseKEGG` -> kegg-pathways | KEGG maps (live DB) |
| Reaction-level, reproducible offline | `gsePathway` -> reactome-pathways | local reactome.db |
| Curated MSigDB hallmark / C2 / C5 | `GSEA(TERM2GENE)` + msigdbr | generic-input GSEA on any collection |
| Matrix + design, want competitive + correlation-honest | `limma::camera` | VIF-corrects the inter-gene correlation gene-permutation ignores |
| Matrix + design, tiny n / covariates, "is set DE at all" | `limma::roast`/`fry` | self-contained rotation, valid at any n |
| Per-sample pathway-activity matrix for clustering/ML | ssGSEA / GSVA | scores each sample, not a contrast test |
| The DE statistic / ranking itself | -> differential-expression/de-results | upstream, not enrichment |

## Build the Ranked Vector (the Caller-Owned Step)

**Goal:** Turn a DE table into the named numeric vector sorted strictly decreasing that every preranked function requires, ranked by a signed variance-calibrated metric.

**Approach:** Pick the ranking metric to match the DE tool, name the vector by gene ID, drop NAs, deduplicate to one statistic per gene, and sort decreasing. The DE mechanics and the `$padj`/`$adj.P.Val` column conventions live in differential-expression/de-results.

| DE source | Ranking metric | Column | Why |
|-----------|----------------|--------|-----|
| DESeq2 | Wald statistic | `stat` | signed + variance-calibrated; best single choice for RNA-seq |
| limma / voom | moderated t-statistic | `t` | empirical-Bayes shrinkage borrows variance; signed |
| edgeR (QL) | `sign(logFC) * -log10(PValue)` | derived | no single signed statistic column |
| any tool, last resort | log2 fold change | `log2FoldChange` | magnitude only; noisy for low-count genes |

```r
library(clusterProfiler)
library(org.Hs.eg.db)

de <- read.csv('de_results.csv')          # DE list source: differential-expression/de-results
gene_list <- de$stat                       # DESeq2 Wald stat: signed + variance-calibrated
names(gene_list) <- de$entrez_id
gene_list <- gene_list[!is.na(gene_list)]
gene_list <- gene_list[!duplicated(names(gene_list))]   # one statistic per gene; duplicates double-count hits
gene_list <- sort(gene_list, decreasing = TRUE)         # REQUIRED: unsorted input silently mis-ranks
```

Ranking by `sign(log2FC) * -log10(pmax(pvalue, 1e-300))` (for edgeR, or when a Wald stat is unavailable) preserves direction and clamps `p==0` from going to `Inf`. Never rank by raw p-value alone (sign erased) or by `lfcShrink(type='normal')` (deprecated prior distorts the ranking). apeglm/ashr-shrunk results DROP the `stat` column - pull `stat` from the unshrunk `results(dds)` if ranking by it.

## Run Preranked GSEA on GO

**Goal:** Find GO terms whose members shift coordinately up or down across the full ranking, with no significance cutoff.

**Approach:** Set the permutation seed for reproducibility, set `eps=0` for exact tiny p-values, run gseGO, then map the leading-edge IDs back to symbols and read `core_enrichment` as the interpretable core.

```r
set.seed(123)                              # fixes the multilevel Monte Carlo; any fixed seed
gse_go <- gseGO(geneList = gene_list, OrgDb = org.Hs.eg.db, keyType = 'ENTREZID',
                ont = 'BP', exponent = 1, minGSSize = 10, maxGSSize = 500,
                eps = 0, pvalueCutoff = 0.05, pAdjustMethod = 'BH',
                seed = TRUE, by = 'fgsea', verbose = FALSE)
gse_go <- setReadable(gse_go, OrgDb = org.Hs.eg.db, keyType = 'ENTREZID')
```

`gseaResult` columns: `ID`, `Description`, `setSize`, `enrichmentScore` (raw ES), `NES`, `pvalue`, `p.adjust` (BH), `qvalue`, `rank` (ES-peak position), `leading_edge`, `core_enrichment` (`/`-separated leading-edge IDs). Report `p.adjust`/`qvalue`, never raw `pvalue` and never an invented `$FDR`. NES sign = direction: positive = top of the ranking (up in the contrast), negative = bottom.

## Run GSEA on KEGG, Reactome, or MSigDB

**Goal:** Apply the same preranked engine to a pathway database with the gene-ID type that database expects.

**Approach:** gseKEGG/gsePathway need ENTREZ-style IDs; choose the collection, keep the seed and `eps=0`, and note KEGG queries the live REST API (date-dependent) while Reactome and MSigDB are local.

```r
set.seed(123)
gse_kegg <- gseKEGG(geneList = gene_list, organism = 'hsa', keyType = 'ncbi-geneid',   # Entrez-named vector; 'kegg' keyType is the prokaryote locus-tag path
                    minGSSize = 10, maxGSSize = 500, eps = 0,
                    pvalueCutoff = 0.05, seed = TRUE, verbose = FALSE)   # live KEGG API; pin the date

library(msigdbr)
h <- msigdbr(species = 'Homo sapiens', collection = 'H')    # 26.x: collection= (was category=); gs_collection (was gs_cat)
t2g <- h[, c('gs_name', 'ncbi_gene')]                       # 26.x Entrez column is ncbi_gene; older releases used entrez_gene
gse_h <- GSEA(geneList = gene_list, TERM2GENE = t2g, exponent = 1,
              minGSSize = 10, maxGSSize = 500, eps = 0,
              pvalueCutoff = 0.05, seed = TRUE, verbose = FALSE)
```

If the installed msigdbr still uses `category=`/`entrez_gene`, the old form works but warns - check `?msigdbr` and `names(h)`. ReactomePA's `gsePathway(geneList, organism='human')` reads the local reactome.db and also needs ENTREZ IDs.

## Per-Sample Scores: ssGSEA and GSVA (Not a Contrast Test)

**Goal:** Convert an expression matrix into a gene-set-by-sample activity matrix to feed clustering, survival, or a classifier - there is no per-pathway p-value here.

**Approach:** GSVA >= 1.50 uses a PARAMETER-OBJECT API: build `gsvaParam(...)` or `ssgseaParam(...)` and pass it to `gsva()`. The old `gsva(expr, gset.idx.list, method=)` signature is defunct.

```r
# GSVA >= 1.50 / Bioc 3.18 parameter-object API (older method= signature errors)
library(GSVA)
gsva_scores  <- gsva(gsvaParam(expr_matrix, gene_sets))      # unsupervised per-sample set scores
ssgsea_scores <- gsva(ssgseaParam(expr_matrix, gene_sets))   # ssGSEA via the same dispatch
```

Use GSEA (preranked or phenotype) for a CONTRAST and a pathway-level p-value; use ssGSEA/GSVA for a per-sample activity matrix for downstream modeling. GSVA is not installed in the reference environment - verify the installed signature with `?gsva` before running.

## Per-Method Failure Modes

### Ranking by raw p-value
**Trigger:** `gene_list <- -log10(de$pvalue)` with no `sign()`. **Mechanism:** the magnitude is symmetric, so up- and down-regulated genes both land at the top. **Symptom:** NES signs are meaningless; "enriched" sets mix directions. **Fix:** rank by `sign(log2FC) * -log10(pmax(p, 1e-300))`, or use DESeq2 `stat` / limma `t`.

### Preranked p-values treated as correlation-honest
**Trigger:** reporting FDR 0.001 from gseGO/fgsea on a co-regulated set. **Mechanism:** gene permutation assumes gene independence; correlated sets inflate the set-statistic variance, so p is too small. **Symptom:** "significant" pathways that are co-expression and do not replicate. **Fix:** state the permutation type; for type-I control with a design matrix use CAMERA (Wu & Smyth 2012).

### Unsorted or duplicated geneList
**Trigger:** an un-sorted vector, or duplicate gene names after ID conversion. **Mechanism:** clusterProfiler assumes pre-sorting and uses names to map into sets; duplicates double-count a gene in the hit increments. **Symptom:** silently wrong ES, or an fgsea ties warning. **Fix:** `sort(gl[!duplicated(names(gl))], decreasing=TRUE)`; prefer a continuous metric (Wald stat / moderated t rarely tie).

### Bare log2FC ranking
**Trigger:** ranking by `log2FoldChange` from raw counts. **Mechanism:** a gene with 2 vs 8 counts shows a huge unstable LFC. **Symptom:** the leading edge is one or two low-count outliers, not a coordinated shift. **Fix:** rank by `stat`/`t`; if LFC is unavoidable use apeglm/ashr-shrunk LFC (never `type='normal'`).

### No set.seed
**Trigger:** running gseGO without fixing the seed. **Mechanism:** the multilevel Monte Carlo is stochastic. **Symptom:** p-values and the significant-set list drift across identical reruns. **Fix:** `set.seed(123)` AND `seed=TRUE` in the call.

### Tiny leading edge believed
**Trigger:** trusting a high |NES| without inspecting `core_enrichment`. **Mechanism:** a 1-2 gene leading edge is outlier-driven, not a pathway shift; large sets reach high |NES| by chance. **Symptom:** an unreplicated headline pathway. **Fix:** FDR first, then leading-edge size/concentration, then NES for prioritization.

### Stale nPerm / FDR<0.25 lore
**Trigger:** copying `nPerm=10000` and "FDR < 0.25" from a Broad-desktop tutorial. **Mechanism:** `nPerm` was REMOVED at the fgsea/multilevel switch; clusterProfiler `p.adjust` is BH, not the Broad empirical-null FDR that 0.25 was calibrated for. **Symptom:** an argument error (`nPerm`) or a mis-transplanted threshold. **Fix:** drop `nPerm`, govern tiny-p with `eps`, treat `p.adjust` as BH and pick a defensible cutoff (often 0.05).

### Stale GSVA call
**Trigger:** `gsva(expr, gene_sets, method='ssgsea')`. **Mechanism:** GSVA >= 1.50 dispatches on a parameter object's class. **Symptom:** the old signature errors. **Fix:** `gsva(gsvaParam(expr, gene_sets))` / `ssgseaParam(...)`.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| `exponent = 1` | Subramanian 2005 *PNAS* 102:15545 | weights each hit by |statistic|; p=0 is the unweighted KS that flags middle-clustered sets with no strong genes |
| `minGSSize = 10` | clusterProfiler default | drops tiny sets that overfit on one outlier |
| `maxGSSize = 500` | clusterProfiler default | drops overly broad sets that always 'enrich' |
| `eps = 0` (default 1e-10) | clusterProfiler / fgsea | replaces nPerm: `eps=0` resolves exact tiny p-values; 1e-10 is the default floor |
| `pAdjustMethod = 'BH'` | clusterProfiler default | Benjamini-Hochberg FDR; NOT the Broad empirical-null FDR, so do not reflex to 0.25 |
| `pvalueCutoff = 0.05` | clusterProfiler default | filters on p.adjust by default; defensible BH cutoff |
| ~>=7 samples/group | Broad GSEA docs | minimum for a non-degenerate phenotype-permutation null |
| `set.seed(123)` | reproducibility | any fixed seed; the point is to fix the multilevel Monte Carlo |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| Error about names / wrong ES | geneList not named or not sorted decreasing | `sort(setNames(v, ids), decreasing=TRUE)` |
| `--> No gene can be mapped` | wrong keyType/OrgDb, or non-ENTREZ IDs | `bitr` to the expected ID type first |
| gseKEGG returns 0 terms | ENSEMBL/SYMBOL passed, wrong organism code, or KEGG API down | convert to kegg-id/ENTREZ; check the `organism` code; retry (live API) |
| Different results each run | no `set.seed`, or live KEGG DB changed | fix the seed; pin the KEGG run date |
| `nPerm` argument error | copied from a pre-4.0 tutorial | remove `nPerm`; use `eps` |
| GSVA `method=` error | pre-1.50 signature | `gsva(gsvaParam(expr, sets))` |
| `core_enrichment` is NA / all-ID | `setReadable` not applied | `setReadable(gse, OrgDb, keyType='ENTREZID')` |

## References

- Mootha VK, Lindgren CM, Eriksson KF, et al. 2003. PGC-1alpha-responsive genes involved in oxidative phosphorylation are coordinately downregulated in human diabetes. *Nat Genet* 34:267-273.
- Subramanian A, Tamayo P, Mootha VK, et al. 2005. Gene set enrichment analysis: a knowledge-based approach for interpreting genome-wide expression profiles. *PNAS* 102:15545-15550.
- Korotkevich G, Sukhov V, Budin N, et al. Fast gene set enrichment analysis. *bioRxiv* 060012 (preprint). DOI 10.1101/060012.
- Wu D, Smyth GK. 2012. Camera: a competitive gene set test accounting for inter-gene correlation. *Nucleic Acids Res* 40:e133.
- Wu D, Lim E, Vaillant F, et al. 2010. ROAST: rotation gene set tests for complex microarray experiments. *Bioinformatics* 26:2176-2182.
- Barbie DA, Tamayo P, Boehm JS, et al. 2009. Systematic RNA interference reveals that oncogenic KRAS-driven cancers require TBK1. *Nature* 462:108-112.
- Hanzelmann S, Castelo R, Guinney J. 2013. GSVA: gene set variation analysis for microarray and RNA-seq data. *BMC Bioinformatics* 14:7.
- Reimand J, Isserlin R, Voisin V, et al. 2019. Pathway enrichment analysis and visualization of omics data using g:Profiler, GSEA, Cytoscape and EnrichmentMap. *Nat Protoc* 14:482-517.
- Wijesooriya K, Jadaan SA, Perera KL, et al. 2022. Urgent need for consistent standards in functional enrichment analysis. *PLoS Comput Biol* 18:e1009935.

## Related Skills

- go-enrichment - Gene-list ORA alternative when no ranking exists
- kegg-pathways - KEGG pathway and module enrichment and ID conventions
- reactome-pathways - Reactome curated-pathway enrichment (local DB)
- wikipathways - WikiPathways community-pathway enrichment
- enrichment-visualization - gseaplot2, ridgeplot, and dotplot of GSEA results
- differential-expression/de-results - Source of the ranking statistic and the padj column conventions
- workflows/expression-to-pathways - End-to-end DE-to-enrichment pipeline
<!-- END FILE: pathway-analysis/gsea/SKILL.md -->

## 子目录：pathway-analysis/kegg-pathways

<!-- BEGIN FILE: pathway-analysis/kegg-pathways/SKILL.md -->
---
name: bio-pathway-kegg-pathways
description: Tests gene lists, ranked vectors, and fold-change vectors against KEGG pathways and modules with clusterProfiler enrichKEGG/enrichMKEGG (ORA), gseKEGG (GSEA), and SPIA/graphite (signed-topology perturbation) in R. Owns the third pathway-analysis generation because KEGG ships signed directed signaling topology (KGML). Covers why a KEGG result is a timestamped join against a live REST API (irreproducible unless pinned with a gson snapshot, not the stale 2012 KEGG.db), why enrichKEGG keyType is kegg/ncbi-geneid not OrgDb ENSEMBL/SYMBOL (zero hits), why organism is a KEGG code (hsa, pae) with prokaryotic locus tags, and why SPIA works only on signaling maps. Use when finding enriched KEGG pathways or modules, scoring signed pathway perturbation, analyzing prokaryotes or non-model organisms via locus tags or KO, comparing conditions with compareCluster, or overlaying data with pathview. The hypergeometric universe lives in go-enrichment; the GSEA engine in gsea.
tool_type: r
primary_tool: clusterProfiler
---

## Version Compatibility

Reference examples tested with: clusterProfiler 4.18+, org.Hs.eg.db 3.18+, gson 0.1+ (snapshot pinning), SPIA 2.50+ and graphite 1.56+ (topology section).

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

KEGG is a LIVE DATABASE, not a package. enrichKEGG/enrichMKEGG/gseKEGG query the KEGG REST API (https://rest.kegg.jp/) at call time, so the same code on the same genes returns DIFFERENT pathways months apart as KEGG updates. For any reported result, pin the release with a gson snapshot (below) and record the access date; `use_internal_data=TRUE` does NOT pin the current KEGG (it loads the deprecated 2012 KEGG.db).

# KEGG Pathway and Topology Enrichment

**"Which KEGG pathways are perturbed in my data?"** -> Join genes to KEGG's curated pathway/module gene sets (ORA or GSEA), or propagate fold-changes through KEGG's signed wiring (SPIA) - and pin the KEGG release, because the result is a timestamped query against a moving curation, not a fact about the biology.
- R: `enrichKEGG(gene, organism, keyType)` | `gseKEGG(geneList, organism)` | `spia(de, all, organism)`

Scope: KEGG-specific enrichment across all three generations - membership ORA (enrichKEGG/enrichMKEGG), ranked GSEA (gseKEGG), and signed-topology perturbation (SPIA/graphite). KEGG ID mapping (organism codes, keyType, bitr_kegg, prokaryotic locus tags, KO routing), reproducibility/pinning, and pathview map overlay live here. The hypergeometric test and the universe problem -> go-enrichment. The GSEA running-sum engine and ranking-metric choice -> gsea. Reactome/WikiPathways gene sets -> reactome-pathways, wikipathways. Generic dot/cnet/emap plots -> enrichment-visualization. The DE list and fold-changes -> differential-expression/de-results.

## The Single Most Important Modern Insight -- A KEGG Result Is a Timestamped Join Against a Moving, Partially-Paywalled Curation, Not a Fact About Biology

Two consequences follow, and both are invisible until someone reruns the analysis.

1. **The query is live, so the result is irreproducible unless the release is pinned.** enrichKEGG/gseKEGG/SPIA hit the KEGG REST API at call time; KEGG adds maps, re-annotates genes, and revises edges continuously, so identical code returns a different pathway list next quarter. The fix is a gson snapshot: `gson_KEGG('hsa')` downloads the current KEGG pathway/module sets into a GSON object, `write.gson()`/`read.gson()` persist it, and the generic `enricher(gene, gson=k)` / `GSEA(geneList, gson=k)` run frozen and offline against it. Record the access date. `use_internal_data=TRUE` is NOT this fix - it silently reaches for the deprecated 2012 `KEGG.db`, which is the wrong, stale snapshot.

2. **KEGG is the only mainstream database shipping signed, directed signaling topology (KGML), which is why this skill owns the third generation of pathway analysis.** ORA and GSEA treat a pathway as an unordered bag of exchangeable genes; SPIA asks a question they structurally cannot pose - given where each gene sits in the wiring and the sign of every edge, how perturbed is this pathway? That requires the topology only KEGG (and a few others via graphite) provides. The discipline: choose the generation by the question (membership? rank? signed perturbation?), match keyType/organism to the actual IDs (locus tags for bacteria, KO for non-model), set the universe to the genes that could have been called DE, and pin the release before publishing.

## Tool Taxonomy (KEGG Across the Three Generations)

| Method | Generation | Engine | Uses log2FC? | Uses topology/direction? | Suitable KEGG maps | Citation |
|--------|-----------|--------|--------------|--------------------------|--------------------|----------|
| enrichKEGG (ORA) | 1st (over-representation) | hypergeometric | no (gene list) | no | all | Wu 2021 *The Innovation* 2:100141; Kanehisa & Goto 2000 *Nucleic Acids Res* 28:27 |
| enrichMKEGG (ORA on modules) | 1st | hypergeometric | no | no | modules (M-numbers) | Wu 2021 *The Innovation* 2:100141 |
| gseKEGG (GSEA) | 2nd (functional class scoring) | fgsea running sum | yes (ranking) | no | all (as sets) | Wu 2021 *The Innovation* 2:100141; engine -> gsea |
| SPIA | 3rd (pathway topology) | pNDE (ORA) x pPERT (perturbation) -> pG | yes (named log2FC) | YES (signed KGML) | SIGNALING only | Tarca 2009 *Bioinformatics* 25:75; Draghici 2007 *Genome Res* 17:1537 |
| graphite + runSPIA | 3rd | SPIA over harmonized graphs | yes | YES | signaling (KEGG/Reactome) | Sales 2012 *BMC Bioinformatics* 13:20 |

The three-generations framing (ORA -> FCS -> pathway topology) is Khatri 2012 *PLoS Comput Biol* 8:e1002375; this skill is the KEGG instantiation of all three (the category README compares the generations across databases).

## Decision Tree by Scenario

| Scenario | Recommended | Why |
|----------|-------------|-----|
| Pre-selected gene list, "which KEGG pathways" | enrichKEGG (ORA), set the universe | no ranking available; membership test |
| All genes carry a DE statistic, no clear cutoff | gseKEGG -> gsea | uses the full ranking; no arbitrary cutoff |
| Want WHERE in a broad pathway the signal sits | enrichMKEGG (modules) | M-numbers are tighter functional units |
| Have named log2FC + want signed perturbation on a SIGNALING map | SPIA (or graphite + runSPIA) | propagates fold-changes through the wiring; uses direction |
| Metabolic-pathway question (glycolysis, TCA) | enrichKEGG / gseKEGG | metabolic maps are compound-mediated; SPIA is undefined there |
| Human / mouse / model eukaryote | bitr -> Entrez, keyType='ncbi-geneid' | KEGG gene ID == Entrez for these organisms |
| Bacterial / prokaryotic data | locus tags, keyType='kegg', NO OrgDb/bitr | bacterial KEGG IDs ARE locus tags; no org.*.eg.db exists |
| Non-model organism with no KEGG genome | map to KO, organism='ko' | the universal escape hatch into KEGG pathway space |
| Result must be reproducible / published | gson_KEGG snapshot + enricher/GSEA, record date | live unpinned queries drift; use_internal_data pins the WRONG 2012 db |
| Multiple conditions to compare side by side | compareCluster(fun='enrichKEGG') | one model, faceted dotplot; never compare raw p-values |
| Overlay per-gene data on the KEGG map image | pathview -> render | a KEGG-specific operation; generic plots -> enrichment-visualization |
| The DE list / fold-changes themselves | -> differential-expression/de-results | upstream, not enrichment |

## Prepare the Gene IDs (the Join That Decides Everything)

**Goal:** Get the query genes and the universe into the exact ID type KEGG expects for the organism, because every KEGG failure is a join failure.

**Approach:** For model eukaryotes convert SYMBOL/ENSEMBL to Entrez (KEGG's gene ID for hsa/mmu/rno) and pass keyType='ncbi-geneid'. For prokaryotes pass locus tags directly with keyType='kegg' and no OrgDb. Convert the universe the same way. Passing ENSEMBL/SYMBOL to enrichKEGG returns zero hits silently.

```r
library(clusterProfiler)
library(org.Hs.eg.db)

de <- read.csv('de_results.csv')   # DE list source -> differential-expression/de-results
sig_symbols <- de$gene[de$padj < 0.05 & abs(de$log2FoldChange) > 1]   # padj is the DESeq2 adjusted-p column
sig_entrez  <- bitr(sig_symbols, fromType='SYMBOL', toType='ENTREZID', OrgDb=org.Hs.eg.db)$ENTREZID

# universe = genes that COULD have been called DE (non-NA test statistic), same ID type
universe <- bitr(de$gene[!is.na(de$pvalue)], fromType='SYMBOL', toType='ENTREZID', OrgDb=org.Hs.eg.db)$ENTREZID
```

`bitr_kegg(geneID, fromType, toType, organism)` converts among KEGG's own ID flavors ('kegg', 'ncbi-geneid', 'ncbi-proteinid', 'uniprot') via the REST conv endpoint - use it when starting from UniProt or NCBI protein IDs. Check KEGG coverage of an organism with `search_kegg_organism('Pseudomonas aeruginosa', by='scientific_name')`.

## Run KEGG ORA (enrichKEGG / enrichMKEGG)

**Goal:** Find KEGG pathways (or modules) over-represented among the query genes relative to the measured universe.

**Approach:** Run enrichKEGG with the correct organism code, keyType, and an explicit universe; enrichKEGG has no `readable` argument, so translate the geneID column to symbols afterward with setReadable (eukaryotes only).

```r
kk <- enrichKEGG(gene=sig_entrez, organism='hsa', keyType='ncbi-geneid',
                 universe=universe, pvalueCutoff=0.05, pAdjustMethod='BH',
                 minGSSize=10, maxGSSize=500, qvalueCutoff=0.2)
kk <- setReadable(kk, OrgDb=org.Hs.eg.db, keyType='ENTREZID')   # eukaryotes only; no OrgDb -> keep raw IDs
head(as.data.frame(kk))   # ID, Description, GeneRatio, BgRatio, pvalue, p.adjust, qvalue, geneID, Count

mkk <- enrichMKEGG(gene=sig_entrez, organism='hsa', keyType='ncbi-geneid', universe=universe)   # KEGG MODULES (M-numbers)
```

Report `p.adjust`/`qvalue`, not raw `pvalue`. Fold enrichment = GeneRatio / BgRatio. enrichMKEGG tests smaller, sparser sets: higher resolution (which sub-process is hit) but lower power and many genes belong to no module.

## Run KEGG GSEA (gseKEGG)

**Goal:** Find KEGG sets whose genes shift coordinately across the full ranking, with no cutoff.

**Approach:** Build a named numeric vector sorted DECREASING by the ranking metric, fix the seed (gseKEGG defaults `seed=FALSE`), then run gseKEGG. The running-sum engine and the ranking-metric choice are owned by gsea; only the KEGG arguments (organism, keyType) are KEGG-specific.

```r
geneList <- de$log2FoldChange; names(geneList) <- de$entrez   # names = Entrez IDs
geneList <- sort(geneList[!is.na(geneList)], decreasing=TRUE)
set.seed(123)   # gseKEGG seed=FALSE by default; fix it so permutation p-values are reproducible
kk2 <- gseKEGG(geneList=geneList, organism='hsa', keyType='ncbi-geneid', minGSSize=10, maxGSSize=500, pvalueCutoff=0.05)
```

## Run Signed-Topology Perturbation (SPIA) -- the Third Generation

**Goal:** Score how perturbed each SIGNALING pathway is given both the over-representation of DE genes and the propagation of their fold-changes through the signed wiring.

**Approach:** SPIA combines pNDE (the classical over-representation evidence) with pPERT (the probability of the observed total accumulated perturbation tA, computed by propagating log2 fold-changes through KGML activation/inhibition edges) into a single global pG, then FDR-corrects it. It needs a NAMED vector of DE fold-changes plus the universe, and is defined only for signaling maps. graphite is the modern route: it harmonizes node IDs, resolves complexes/families, removes compounds, and can run SPIA over Reactome topology too.

```r
library(SPIA)
sig <- de[de$padj < 0.05, ]   # DE genes only
map <- bitr(sig$gene, 'SYMBOL', 'ENTREZID', org.Hs.eg.db)   # bitr drops/many-to-one: MERGE, never assign as names
de_vec <- setNames(sig$log2FoldChange[match(map$SYMBOL, sig$gene)], map$ENTREZID)
de_vec <- de_vec[!duplicated(names(de_vec))]
res <- spia(de=de_vec, all=universe, organism='hsa', nB=2000, plots=FALSE)   # nB=2000 bootstraps for pPERT
# output cols: Name, ID, pSize, NDE, pNDE, tA, pPERT, pG, pGFdr, pGFWER, Status, KEGGLINK
# Status reports inferred Activated / Inhibited from the sign of tA

# graphite route (decouples from KEGG's bundled data; works on Reactome too)
library(graphite)
db <- pathways('hsapiens', 'kegg')
db <- convertIdentifiers(db, 'ENTREZID')
prepareSPIA(db, 'kegg_hsa_spia')              # writes the pathway dataset file
gr <- runSPIA(de=de_vec, all=universe, 'kegg_hsa_spia')
```

SPIA aborts if more than ~1% of the DE IDs are absent from `all`, so build the universe from the same ID space. The standalone SPIA package also ships a frozen `hsaSPIA` data object that is an OLDER snapshot than a live enrichKEGG query - do not mix the two in one comparison.

## Pin the KEGG Release for Reproducibility

**Goal:** Freeze the KEGG data a result depends on so the analysis is reproducible and runs offline.

**Approach:** Snapshot the current KEGG sets into a GSON object, persist it, and run enrichment against the snapshot with the generic enricher/GSEA (which accept a `gson` argument); record the access date. Do NOT use use_internal_data=TRUE for this.

```r
library(gson)                                      # GSON class + write.gson/read.gson
k <- gson_KEGG('hsa')                              # gson_KEGG is exported by clusterProfiler; downloads current KEGG sets
k@accessed_date <- as.character(Sys.Date())        # the accessed_date slot survives write/read; a base attr() does not
write.gson(k, file.path(tempdir(), 'kegg_hsa.gson'))
k <- read.gson(file.path(tempdir(), 'kegg_hsa.gson'))

kk_pinned  <- enricher(sig_entrez, gson=k, universe=universe)   # frozen ORA, offline, reproducible
gsea_pinned <- GSEA(geneList, gson=k)                            # frozen GSEA against the snapshot
```

## Compare Multiple Conditions

**Goal:** See shared and condition-specific KEGG pathways across groups in one faceted figure.

**Approach:** Pass named gene lists to compareCluster with fun='enrichKEGG'; it fits one model and produces a faceted dotplot. Compare pathway-ID SETS across conditions, never raw p-values (they depend on sample size, DE gene count, and the KEGG release).

```r
clusters <- list(up=up_entrez, down=down_entrez)
ck <- compareCluster(geneClusters=clusters, fun='enrichKEGG', organism='hsa', keyType='ncbi-geneid')
ck <- setReadable(ck, OrgDb=org.Hs.eg.db, keyType='ENTREZID')
# dotplot(ck) -> enrichment-visualization for the plot grammar
```

## Overlay Data on the KEGG Map (pathview)

pathview downloads a KEGG pathway's KGML and image, joins per-gene values to the nodes, and writes a colored map PNG/PDF (a KEGG-specific operation owned here; generic dot/cnet/emap plots route to enrichment-visualization). It writes files to the working directory and queries KEGG live.

```r
library(pathview)
vals <- setNames(de$log2FoldChange, de$entrez)
pathview(gene.data=vals, pathway.id='hsa04110', species='hsa', gene.idtype='entrez')   # writes hsa04110.pathview.png
```

## Per-Method Failure Modes

### ENSEMBL/SYMBOL passed to enrichKEGG
**Trigger:** feeding OrgDb-style ENSEMBL or SYMBOL IDs to enrichKEGG/gseKEGG. **Mechanism:** KEGG's keyType is 'kegg'/'ncbi-geneid'/'ncbi-proteinid'/'uniprot', not an OrgDb keytype, so no IDs join. **Symptom:** zero enriched pathways, no error. **Fix:** bitr to Entrez and set keyType='ncbi-geneid' (eukaryotes), or pass locus tags with keyType='kegg' (prokaryotes).

### Live-query result treated as reproducible
**Trigger:** reporting an enrichKEGG/gseKEGG/SPIA result without pinning the release. **Mechanism:** the REST query returns the CURRENT KEGG, which changes over time. **Symptom:** a rerun months later yields a different pathway list. **Fix:** snapshot with gson_KEGG, run enricher/GSEA against the gson, and record the access date.

### use_internal_data=TRUE believed to pin current KEGG
**Trigger:** setting use_internal_data=TRUE for reproducibility. **Mechanism:** it loads the deprecated 2012 KEGG.db, not a current pin (and may simply fail). **Symptom:** stale or absent pathways unlike the live result. **Fix:** use a gson snapshot instead; treat KEGG.db as legacy-only.

### SPIA on metabolic maps
**Trigger:** running SPIA/graphite topology on glycolysis or other metabolic maps. **Mechanism:** metabolic maps are compound-mediated and give no clean signed gene->gene graph. **Symptom:** meaningless perturbation scores. **Fix:** restrict SPIA to signaling maps; use enrichKEGG/gseKEGG for metabolism.

### Whole-database universe in ORA
**Trigger:** omitting `universe`. **Mechanism:** the default background is all KEGG-annotated genes, biased toward well-studied, metabolically central genes. **Symptom:** inflated significance for pathways enriched in measured/expressed genes (the tissue-specificity artifact). **Fix:** set universe to the genes that could have been called DE, in the same ID type.

### Locus-tag / strain mismatch in prokaryotes
**Trigger:** locus tags from a re-annotated genome or a different strain than KEGG's reference. **Mechanism:** the gene-ID join is exact; drifted locus tags do not match KEGG's `pae`/`eco` genome. **Symptom:** many genes silently dropped, weak or empty enrichment. **Fix:** confirm the organism code and reference genome with search_kegg_organism; align locus tags to KEGG's annotation, or route through KO.

### bitr/OrgDb forced onto bacteria
**Trigger:** running bitr() or setReadable() on a prokaryote. **Mechanism:** no org.*.eg.db exists for most bacteria and there is no Entrez==KEGG identity. **Symptom:** bitr fails or empties the gene list; setReadable errors. **Fix:** pass locus tags directly with keyType='kegg'; keep raw IDs (no setReadable).

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| pvalueCutoff=0.05 | enrichKEGG/gseKEGG default | filters on p.adjust by default; standard FDR gate |
| qvalueCutoff=0.2 | clusterProfiler default | secondary q-value gate on enrichResult |
| pAdjustMethod='BH' | clusterProfiler default | Benjamini-Hochberg FDR; less conservative than Bonferroni for discovery |
| minGSSize=10 | enrichKEGG default | drop tiny sets that overfit and give unstable p-values |
| maxGSSize=500 | enrichKEGG default | drop very broad sets that always 'enrich' |
| nB=2000 | SPIA default | bootstrap replicates for the pPERT null; raise for stable small p-values |
| SPIA aborts if >1% of DE IDs absent from `all` | Tarca 2009 *Bioinformatics* 25:75 | the perturbation null requires the DE genes live in the universe |
| set.seed before gseKEGG/SPIA | reproducibility | gseKEGG seed=FALSE and SPIA bootstrap are stochastic; fix the seed |
| ID-conversion loss > ~15% | practice heuristic | report the bitr conversion rate; heavy loss makes the result unreliable |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| enrichKEGG returns 0 pathways | ENSEMBL/SYMBOL passed, or wrong organism code, or KEGG API unreachable | bitr to Entrez + keyType='ncbi-geneid'; verify code with search_kegg_organism; check network |
| `setReadable` errors | no OrgDb for the organism (prokaryote) | skip setReadable; keep raw KEGG IDs |
| `gson=` rejected by enrichKEGG | enrichKEGG/gseKEGG have no gson argument | pass the gson to the generic enricher()/GSEA() instead |
| Different pathways on rerun | live KEGG changed between runs | pin with a gson snapshot and record the access date |
| SPIA: "more than 1% of de IDs not in all" | DE IDs not a subset of the universe | build de and all from the same ID space |
| SPIA gives nonsense on glycolysis | topology on a metabolic map | use enrichKEGG/gseKEGG; SPIA is signaling-only |
| Bacterial list gives 0 hits | Entrez/bitr forced onto a prokaryote | pass locus tags with keyType='kegg', no OrgDb |

## References

- Kanehisa M, Goto S. 2000. KEGG: Kyoto Encyclopedia of Genes and Genomes. *Nucleic Acids Res* 28:27-30.
- Kanehisa M, Furumichi M, Sato Y, et al. 2023. KEGG for taxonomy-based analysis of pathways and genomes. *Nucleic Acids Res* 51:D587-D592.
- Wu T, Hu E, Xu S, et al. 2021. clusterProfiler 4.0: A universal enrichment tool for interpreting omics data. *The Innovation* 2:100141.
- Tarca AL, Draghici S, Khatri P, et al. 2009. A novel signaling pathway impact analysis (SPIA). *Bioinformatics* 25:75-82.
- Draghici S, Khatri P, Tarca AL, et al. 2007. A systems biology approach for pathway level analysis. *Genome Res* 17:1537-1545.
- Sales G, Calura E, Cavalieri D, Romualdi C. 2012. graphite - a Bioconductor package to convert pathway topology to gene network. *BMC Bioinformatics* 13:20.
- Luo W, Brouwer C. 2013. Pathview: an R/Bioconductor package for pathway-based data integration and visualization. *Bioinformatics* 29:1830-1831.
- Khatri P, Sirota M, Butte AJ. 2012. Ten years of pathway analysis: current approaches and outstanding challenges. *PLoS Comput Biol* 8:e1002375.

## Related Skills

- go-enrichment - Hypergeometric ORA and the background-universe problem
- gsea - GSEA running-sum engine and ranking-metric choice (gseKEGG)
- reactome-pathways - Reactome curated-pathway enrichment (reproducible local DB)
- wikipathways - WikiPathways community-pathway enrichment
- enrichment-visualization - Dot/bar/cnet/emap/ridge plots of enrichment results
- differential-expression/de-results - Source of the gene list and the fold-changes
- workflows/expression-to-pathways - End-to-end DE-to-enrichment pipeline
<!-- END FILE: pathway-analysis/kegg-pathways/SKILL.md -->

## 子目录：pathway-analysis/reactome-pathways

<!-- BEGIN FILE: pathway-analysis/reactome-pathways/SKILL.md -->
---
name: bio-pathway-reactome
description: Tests a gene list or ranked gene vector for over-representation or coordinated shifts in Reactome's curated, peer-reviewed, reaction-level pathways using ReactomePA's enrichPathway (ORA) and gsePathway (GSEA), reading the local reactome.db so a run is reproducible given the Bioconductor release. Covers why Reactome's atomic unit is the REACTION and pathways are nested containers so a parent and child enrich on the same genes and double-count one signal, why only human is curated and every other species is orthology-inferred, why enrichPathway has NO keyType argument and returns nothing unless genes are ENTREZ (bitr first), and why viewPathway draws a LOCAL reaction network from a pathway NAME. Use when reaction-level granularity, peer-reviewed curation, or an offline-reproducible database is wanted; for comparative multi-sample or multi-omics analysis use ReactomeGSA. The DE list comes from differential-expression; plots from enrichment-visualization.
tool_type: r
primary_tool: ReactomePA
---

## Version Compatibility

Reference examples tested with: ReactomePA 1.54+, reactome.db 1.95+, clusterProfiler 4.18+.

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

reactome.db is a LOCAL Bioconductor annotation package pinned to the Bioconductor release, so enrichPathway/gsePathway are reproducible offline given the package version - unlike KEGG and WikiPathways, which query a live database. The reactome.org web AnalysisService tracks the current quarterly Reactome release and can therefore disagree with a local ReactomePA run (see Failure Modes).

# Reactome Pathway Enrichment

**"Which curated Reactome pathways does my gene list over-represent?"** -> Test each Reactome pathway for over-representation against a measured background, then deduplicate the hierarchy - because a Reactome result is one signal projected onto a tree of nested reactions, not a list of independent findings.
- R: `enrichPathway(gene_entrez, organism='human', universe=measured_entrez, readable=TRUE)`

Scope: ORA (enrichPathway) and GSEA (gsePathway) over Reactome reaction-rolled-to-pathway gene sets, the ENTREZ-only constraint, hierarchy deduplication, the human-curated-only species caveat, the local viewPathway reaction-network plot, and the ReactomeGSA comparative pointer. The hypergeometric test and background-universe theory -> go-enrichment. The GSEA running-sum engine and ranking metric -> gsea. The DE list / ranking statistic -> differential-expression/de-results. Dotplot/emapplot/cnetplot/gseaplot2 -> enrichment-visualization.

## The Single Most Important Modern Insight -- Reactome's Atomic Unit Is the Reaction and Pathways Are Nested Containers, So a Result Is One Signal Projected Onto a Tree, Not a List

Reactome is not a collection of pathway maps like KEGG. Its atomic unit is the ReactionlikeEvent - a single typed molecular transformation (binding, catalysis, transport, modification) with a PubMed citation - and pathways are containers that group reactions and sub-pathways into a deep event hierarchy (`TopLevelPathway -> Pathway -> sub-Pathway -> Reaction`). Two consequences define every decision in this skill:

1. **Granularity is the reason to choose Reactome AND the multiple-testing tax.** A Reactome hit is finer than a KEGG map - a specific, peer-reviewed, literature-grounded reaction - which is why it is worth using. But finer means MORE gene sets (many tiny leaf pathways plus a few huge top-level ones), so the multiple-testing burden is heavier and `minGSSize`/`maxGSSize` matter more than for GO.
2. **Nesting double-counts the signal.** A gene annotated to one leaf reaction is a member of that pathway AND every ancestor, so a parent and child enrich on the SAME genes. A live cell-cycle gene list returns "Cell Cycle Checkpoints" (parent), "G2/M Checkpoints", and "G1/S Transition" (children) stacked at the top - one signal, three "independent" small p-values. A Reactome table is therefore read by reasoning about the hierarchy (report the deepest significant node, ancestors as context), not by sorting on p.adjust.

Second load-bearing fact: **only human is curated; every non-human pathway is orthology-inferred from the human reactions, not independently curated.** Mouse projection is ~81% complete, exotic species far less, so a "Reactome mouse pathway" is a hypothesis from orthology that inherits human-curation gaps and misses mouse-specific biology. The honest output is "the deepest curated human pathway nodes my list over-represents, deduplicated against their ancestors, against a background of genes I actually measured."

## Tool Taxonomy

| Source / engine | Citation | Mechanism / role | When |
|-----------------|----------|------------------|------|
| Reactome database | Milacic 2024 *Nucleic Acids Res* 52:D672 | expert-authored, externally peer-reviewed, PubMed-cited reactions in a deep event hierarchy; CC0 | the gene-set source: reaction-level, reproducible, open |
| ReactomePA enrichPathway (ORA) | Yu & He 2016 *Mol BioSyst* 12:477 | one-sided hypergeometric test over reaction-rolled-to-pathway sets; local reactome.db; ENTREZ-only | a pre-selected gene LIST + a measured universe |
| ReactomePA gsePathway (GSEA) | Yu & He 2016 *Mol BioSyst* 12:477 | fgsea running-sum over a ranked vector; ENTREZ-only | all genes carry a statistic; distributed signal; no cutoff |
| ReactomePA viewPathway | Yu & He 2016 *Mol BioSyst* 12:477 | LOCAL ggraph reaction-network plot of ONE pathway by NAME | inspect the reactions/entities of a single hit, optionally colored by fold change |
| ReactomeGSA | Griss 2020 *Mol Cell Proteomics* 19:2115 | hosted AnalysisService client: comparative GSA / ssGSEA / PADOG, multi-omics, per-scRNA-cluster | BETWEEN-condition, multi-omics, or single-cell-cluster pathway comparison |

## Decision Tree by Scenario

| Scenario | Recommended | Why |
|----------|-------------|-----|
| Pre-selected significant-gene list + a measured background | `enrichPathway(gene, universe=)` | ORA needs a list and the universe decides significance |
| All genes carry a DE statistic, cutoff would be arbitrary | `gsePathway(geneList)` -> gsea | running-sum over the full ranking; no cutoff |
| Genes are SYMBOL or ENSEMBL | `bitr(..., toType='ENTREZID')` FIRST | enrichPathway has no keyType; non-ENTREZ silently returns empty |
| Parent and child both enriched on the same genes | report the deepest significant node; ancestors = context | nesting double-counts; they are ONE finding |
| Compare pathways BETWEEN conditions / across omics / scRNA clusters | ReactomeGSA (`perform_reactome_analysis`/`analyse_sc_clusters`) | ReactomePA is single-list; the hosted service is comparative |
| Non-human within the 7 ReactomePA organisms | set `organism=`; flag results as orthology-inferred | the projection is a hypothesis, not curation |
| Species beyond the 7 (bacteria, plant, etc.) | web AnalysisService / ReactomeGSA, not ReactomePA | reactome.db maps only 7 organisms |
| Deeper metabolic coverage wanted | supplement with KEGG -> kegg-pathways | KEGG remains the deeper metabolic resource |
| The ORA-vs-GSEA decision itself, or null/benchmark theory | -> the category README | the cross-database method-selection fork lives there |
| The DE list / ranking statistic itself | -> differential-expression/de-results | upstream, not enrichment |

ReactomePA's `organism` accepts exactly seven values: human, rat, mouse, celegans, yeast, zebrafish, fly. This is a reactome.db mapping ceiling, NOT a Reactome ceiling - the database projects to ~14-20 species and the web AnalysisService covers them; do not conflate the two.

## Over-Representation Analysis (enrichPathway)

**Goal:** Find Reactome pathways over-represented in a significant-gene list, against the genes actually measured.

**Approach:** Convert the gene list to ENTREZ (mandatory - no keyType argument), pass the measured background as `universe`, run enrichPathway, then read the hierarchy rather than the raw row order.

```r
library(ReactomePA)
library(org.Hs.eg.db)
library(clusterProfiler)   # bitr

sig_entrez <- bitr(sig_symbols, fromType='SYMBOL', toType='ENTREZID', OrgDb=org.Hs.eg.db)$ENTREZID
universe   <- bitr(all_tested_symbols, fromType='SYMBOL', toType='ENTREZID', OrgDb=org.Hs.eg.db)$ENTREZID

ora <- enrichPathway(gene=sig_entrez, organism='human', universe=universe,
                     pvalueCutoff=0.05, qvalueCutoff=0.2,
                     minGSSize=10, maxGSSize=500, readable=TRUE)
# enrichResult columns: ID Description GeneRatio BgRatio RichFactor FoldEnrichment zScore
#                       pvalue p.adjust qvalue geneID Count
# FoldEnrichment and RichFactor are columns - read effect size there, do not compute GeneRatio/BgRatio by hand.
```

Without `universe`, the background is all ~11,200 Reactome-annotated ENTREZ genes (the live `BgRatio` denominator), not the genes measured, which over-states significance. `readable=TRUE` maps the `geneID` column back to symbols. Reading the result means deduplicating the hierarchy: identify the deepest significant pathway for each signal and note its ancestors as context, not as separate hits. ReactomePA has no `simplify()` equivalent (unlike GO's DAG), so this is a manual judgment call; the visual collapse (treeplot, emapplot) is owned by enrichment-visualization.

## GSEA (gsePathway)

**Goal:** Find Reactome pathways whose genes shift coordinately across the full ranking, without a significance cutoff.

**Approach:** Build a named numeric vector sorted decreasing by the ranking statistic with ENTREZ names, set a seed for permutation reproducibility, then run gsePathway and read the leading edge.

```r
gene_list <- de$stat                       # any per-gene statistic: t-stat, signed -log10 p, shrunken log2FC
names(gene_list) <- de$entrez              # names MUST be ENTREZ
gene_list <- sort(gene_list, decreasing=TRUE)

set.seed(123)                              # gsePathway permutes; fix the seed so p-values reproduce
gse <- gsePathway(geneList=gene_list, organism='human',
                  pvalueCutoff=0.05, pAdjustMethod='BH', verbose=FALSE)
# gseaResult columns: ID Description setSize enrichmentScore NES pvalue p.adjust qvalue rank leading_edge core_enrichment
```

GSEA uses the whole ranking, so the universe/background pitfall of ORA does not apply - but the hierarchy double-counting STILL does: a parent and child both score on the same leading-edge genes. The ranking metric IS the experiment (the same genes ranked differently give different leading edges); the metric choice is owned by gsea.

## viewPathway - the Reactome reaction-network plot

**Goal:** Draw the reactions and physical entities of ONE enriched pathway, optionally colored by fold change.

**Approach:** Pass the pathway NAME (the `Description`, NOT the R-HSA id) to viewPathway; it renders a LOCAL ggraph reaction network in the R graphics device. To open the actual web diagram, build the PathwayBrowser URL from the R-HSA id and browseURL it.

```r
top_name <- ora@result$Description[1]                       # the NAME, not $ID
viewPathway(top_name, organism='human', readable=TRUE, foldChange=gene_list)

# the interactive web diagram needs the R-HSA id, NOT viewPathway:
browseURL(paste0('https://reactome.org/PathwayBrowser/#/', ora@result$ID[1]))
```

`viewPathway`'s `keyType` controls the ID type of the `foldChange` names only (so a SYMBOL-named fold-change vector works with `keyType='SYMBOL'`); the ENTREZ-only constraint of enrichPathway does not extend to it. Route generic dotplot/emapplot/cnetplot/gseaplot2 to enrichment-visualization; viewPathway is owned here because it is Reactome-data-structure-specific.

## ReactomeGSA - comparative and multi-omics

**Goal:** Compare pathway activity BETWEEN conditions, across omics layers, or across single-cell clusters - which ReactomePA's single-list model cannot do.

**Approach:** ReactomeGSA is a separate Bioconductor client to Reactome's hosted AnalysisService; build a request, add datasets, and send it to the server (network required; results track the server's release, not a local reactome.db).

```r
library(ReactomeGSA)
req <- ReactomeAnalysisRequest(method='Camera')                  # or 'ssGSEA', 'PADOG'
req <- add_dataset(req, expression_values=expr_matrix, name='RNAseq',
                   type='rnaseq_counts', comparison_factor='condition',
                   comparison_group_1='A', comparison_group_2='B', sample_data=meta)
res <- perform_reactome_analysis(req)                            # sends to the server
pw  <- pathways(res)                                             # combined pathway table
sc  <- analyse_sc_clusters(seurat_obj, use_interactors=FALSE)    # per-cluster ssGSEA
```

Use ReactomePA for "is this one list over-represented / coordinately changed"; use ReactomeGSA for "which pathways DIFFER between conditions / omics / clusters".

## Per-Method Failure Modes

### SYMBOL or ENSEMBL passed to enrichPathway/gsePathway
**Trigger:** feeding a symbol or Ensembl vector because enrichGO accepted one. **Mechanism:** enrichPathway has NO keyType argument; the gene->pathway map is reactome.db's ENTREZ-keyed table, so non-ENTREZ ids match nothing. **Symptom:** zero rows on a clearly enriched list, no error. **Fix:** `bitr(..., toType='ENTREZID')` first; this is the #1 "why are my results empty" cause.

### No universe -> inflated significance
**Trigger:** calling enrichPathway without `universe=`. **Mechanism:** the background defaults to all ~11,200 Reactome-annotated genes, not the ~15,000 genes measured, shrinking every p-value. **Symptom:** implausibly significant pathways, BgRatio denominator ~11230. **Fix:** pass the measured ENTREZ set as `universe`.

### Reading the hierarchy as independent hits
**Trigger:** reporting the top-N rows by p.adjust as N findings. **Mechanism:** membership propagates up the event tree, so parent/child/sibling rows share genes. **Symptom:** "G1/S Transition", "Mitotic G1 phase and G1/S transition", and "S Phase" stacked at the top of one cell-cycle list. **Fix:** deduplicate to the deepest significant node per signal; note ancestors as context; treat BH over hierarchy rows as anti-conservative because the rows are not independent tests.

### viewPathway misuse
**Trigger:** `viewPathway('R-HSA-109582')` or expecting a browser to open. **Mechanism:** the first argument is `pathName` (the Description), and the function draws a LOCAL ggraph plot, not a browser window. **Symptom:** an error / empty plot from the id, or surprise that no browser opens. **Fix:** pass `ora@result$Description[i]`; for the web diagram `browseURL('https://reactome.org/PathwayBrowser/#/<R-HSA-id>')`.

### Trusting non-human Reactome as curated
**Trigger:** interpreting a mouse/rat/fly result as curated biology. **Mechanism:** only human is curated; all others are orthology-projected from the human reactions (mouse ~81% complete, less for distant species). **Symptom:** species-specific findings that have no human ortholog are simply absent, and projected hits inherit human-curation gaps. **Fix:** flag every non-human result as orthology-inferred and confirm species-specific hits independently.

### Assuming the R package and the web AnalysisService agree
**Trigger:** quoting "Reactome says pathway X, p=..." without naming the tool. **Mechanism:** ReactomePA pins to the installed reactome.db snapshot while the web tool tracks the current quarterly release, and their default backgrounds and identifier-projection differ. **Symptom:** a collaborator's reactome.org p-values differ from the local ones on the same list. **Fix:** state the tool, the release/reactome.db version, and the background; do not treat the two as interchangeable.

### Assuming arbitrary-organism support
**Trigger:** passing a bacterial or plant `organism`. **Mechanism:** reactome.db maps only 7 organisms for ReactomePA. **Symptom:** an unsupported-organism error. **Fix:** for species beyond the 7, use the web AnalysisService or ReactomeGSA.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| `pvalueCutoff=0.05` | enrichPathway/gsePathway default | filters on p.adjust (BH) by default in the result; standard FDR gate |
| `qvalueCutoff=0.2` | enrichPathway default | secondary q-value gate on the ORA result |
| `pAdjustMethod='BH'` | enrichPathway default | Benjamini-Hochberg FDR; less conservative than Bonferroni, but anti-conservative across nested hierarchy rows |
| `minGSSize=10` | enrichPathway default | drop tiny leaf pathways (2-3 genes) that inflate false positives; matters MORE for Reactome's deep tree |
| `maxGSSize=500` | enrichPathway default | drop huge top-level pathways (e.g. "Signal Transduction") that always enrich and are uninformative |
| Reactome background ~11,200 | live BgRatio denominator | the ENTREZ genes with any Reactome annotation; the implicit universe if `universe=` is omitted |
| Mouse projection ~81% complete | Reactome inference docs | the fraction of human reactions projected to mouse by orthology; far lower for distant species |
| `set.seed(123)` before gsePathway | reproducibility | gsePathway permutes; without a fixed seed the permutation p-values drift between runs |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| enrichPathway returns 0 rows on a clear list | genes are SYMBOL/ENSEMBL, not ENTREZ | `bitr(..., toType='ENTREZID')` first (no keyType arg) |
| Implausibly significant pathways | no `universe=`, background is all ~11k Reactome genes | pass the measured ENTREZ set as `universe` |
| Top hits are parent/child of one pathway | hierarchy nesting double-counts the signal | report the deepest significant node; ancestors as context |
| `viewPathway('R-HSA-...')` errors or is empty | first arg is the NAME (Description), not the id | `viewPathway(ora@result$Description[i], ...)` |
| viewPathway did not open a browser | it draws a LOCAL ggraph plot | `browseURL('https://reactome.org/PathwayBrowser/#/<id>')` for the web diagram |
| Different p-values than reactome.org | release skew + different universe between local db and web service | name the tool, reactome.db version, and background |
| gsePathway results change each run | no `set.seed` before the permutation | set a fixed seed |
| Unsupported-organism error | organism outside the 7 reactome.db maps | use the web AnalysisService / ReactomeGSA |

## References

- Milacic M, Beavers D, Conley P, et al. 2024. The Reactome Pathway Knowledgebase 2024. *Nucleic Acids Res* 52:D672-D678.
- Yu G, He QY. 2016. ReactomePA: an R/Bioconductor package for reactome pathway analysis and visualization. *Mol BioSyst* 12:477-479.
- Griss J, Viteri G, Sidiropoulos K, Nguyen V, Fabregat A, Hermjakob H. 2020. ReactomeGSA - Efficient Multi-Omics Comparative Pathway Analysis. *Mol Cell Proteomics* 19:2115-2125.

## Related Skills

- go-enrichment - The hypergeometric test and the background-universe problem
- gsea - The GSEA running-sum engine and ranking-metric choice
- kegg-pathways - KEGG pathway/module enrichment; deeper metabolic coverage
- wikipathways - WikiPathways community-pathway enrichment (also CC0)
- enrichment-visualization - Dot/bar/cnet/emap/tree/GSEA plots of enrichment results
- differential-expression/de-results - Source of the gene list and the ranking statistic
- workflows/expression-to-pathways - End-to-end DE-to-enrichment pipeline
<!-- END FILE: pathway-analysis/reactome-pathways/SKILL.md -->

## 子目录：pathway-analysis/wikipathways

<!-- BEGIN FILE: pathway-analysis/wikipathways/SKILL.md -->
---
name: bio-pathway-wikipathways
description: Tests a gene list (ORA, enrichWP) or a ranked gene vector (GSEA, gseWP) against the WikiPathways community-curated pathway collection with clusterProfiler and rWikiPathways. Covers why a WikiPathways result is a snapshot of a live, monthly-updated database (enrichWP/gseWP/gson_WP silently pull data.wikipathways.org/current/), why reproducibility requires pinning a dated GMT via downloadPathwayArchive(date=, format='gmt'), why the WP GMT is Entrez-keyed so symbols and Ensembl silently overlap nothing, why universe=NULL gives a biased all-WP-genes background, how to split the name%version%wpid%org term, and why WikiPathways (CC0, no peer review) complements KEGG/Reactome. Use when running open community-pathway enrichment, covering a non-model WP species, catching disease/drug pathways missing from KEGG/Reactome, or needing a reproducible dated analysis. The gene list comes from differential-expression/de-results; visualize with enrichment-visualization.
tool_type: r
primary_tool: rWikiPathways
---

## Version Compatibility

Reference examples tested with: clusterProfiler 4.18+, rWikiPathways 1.26+, org.Hs.eg.db 3.18+.

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

WikiPathways is a LIVE, monthly-updated database. `enrichWP`, `gseWP`, and `gson_WP` all download `data.wikipathways.org/current/gmt/` at run time, so the SAME code returns DIFFERENT pathways and p-values months apart with no error. `current/` is not a version. For a reproducible analysis pin a dated release with `downloadPathwayArchive(date='YYYYMMDD', organism=, format='gmt')` and report the date. All `enrichWP`/`gseWP`/`downloadPathwayArchive` calls require internet at run time.

# WikiPathways Enrichment

**"Which community-curated WikiPathways are enriched in my genes?"** -> Test WikiPathways gene sets against a gene list (ORA) or a ranked vector (GSEA), pinning a dated GMT for reproducibility - because the live monthly database changes under identical code, and the WP GMT is Entrez-keyed so any other ID type silently overlaps nothing.
- R (ORA): `enrichWP(entrez, organism='Homo sapiens', universe=all_entrez)`
- R (GSEA): `gseWP(named_decreasing_entrez_vector, organism='Homo sapiens')`
- R (reproducible): `downloadPathwayArchive(date='YYYYMMDD', organism=, format='gmt')` -> `read.gmt` -> split term -> `enricher`/`GSEA`

Scope: WikiPathways-specific enrichment - the data model, the `current/`-vs-dated GMT reproducibility pin, the Entrez-GMT requirement, the term-field split, PFOCR as a noisier complement, and the WP-vs-KEGG-vs-Reactome contrast. The ORA/GSEA method choice and hypergeometric/background theory -> the category README. The DE list and ranking statistic -> differential-expression/de-results. KEGG and Reactome -> kegg-pathways, reactome-pathways. Plot grammar -> enrichment-visualization.

## The Single Most Important Modern Insight -- A WikiPathways Result Is a Snapshot of a Live, Community-Edited Database Taken on the Run Date

WikiPathways is a wiki: anyone can create or edit a pathway, content is CC0, and there is NO formal journal-style peer review gating a pathway's publication (Pico 2008 *PLoS Biol* 6:e184; Martens 2021 *NAR* 49:D613). The collection is republished as a dated GMT archive every MONTH. Three properties every misuse forgets:

1. **`current/` is not a version.** `enrichWP`, `gseWP`, and `gson_WP` all silently download `data.wikipathways.org/current/gmt/` - the latest monthly release. Identical code two months apart returns different pathways and different p-values, with no error and no warning. Reproducibility is NOT a code freeze; it is a dated GMT: `downloadPathwayArchive(date='20240310', organism='Homo sapiens', format='gmt')`, read it, run `enricher`/`GSEA` on the pinned sets, and report the date in methods. `gson_WP()` freezes only within a session (it snapshots `current/`), not across time.

2. **The WP GMT speaks Entrez, and the wrong ID type fails silently.** The GMT is Entrez-keyed via BridgeDb. Passing SYMBOL or ENSEMBL yields near-zero overlap and an empty or misleading result with NO error - convert to Entrez upstream (`bitr`/OrgDb) before `enrichWP`. Likewise `universe=NULL` makes the background "all genes that happen to be in WP" - a small, biased set that inflates significance; pass the assayed/tested Entrez vector as `universe`.

3. **A community pathway is a hypothesis someone drew, not a reviewed fact.** The two things that make WP valuable (open CC0 license, anyone-can-edit curation that captures disease/drug pathways KEGG and Reactome lack, e.g. the COVID-19 Disease Map) are the same two things that make its quality heterogeneous. Many WP pathways are also imported from KEGG/Reactome, so "three databases agree" can be circular rather than independent. Treat each hit as a community claim - check `getPathwayInfo(WPID)` last-edit/curation before leaning on a single WP pathway for a key conclusion - and run WP as a COMPLEMENT to KEGG/Reactome, never a sole peer-reviewed source.

## Tool Taxonomy

| Source / function | Citation | Mechanism / role | When |
|-------------------|----------|------------------|------|
| WikiPathways ORA (`enrichWP`) | Pico 2008 *PLoS Biol* 6:e184; Martens 2021 *NAR* 49:D613; Wu 2021 *Innovation* 2:100141 | hypergeometric test vs the WP GMT (delegates to `enricher`); downloads `current/` | a thresholded gene LIST against community pathways |
| WikiPathways GSEA (`gseWP`) | Agrawal 2024 *NAR* 52:D679; Wu 2021 *Innovation* 2:100141 | running-sum FCS over a ranked vector (delegates to `GSEA`); downloads `current/` | all genes ranked, no arbitrary cutoff |
| `rWikiPathways` (query/download) | Slenter/Hanspers/Pico, Bioconductor | API client: `listOrganisms`, `listPathways`, `getPathwayInfo`, `getXrefList`, `findPathwaysByText`, `downloadPathwayArchive` | inspect pathways, fetch genes, pin a dated GMT |
| Dated GMT + `enricher`/`GSEA` | Wu 2021 *Innovation* 2:100141 | run enrichment on a pinned, parsed GMT, bypassing auto-download | the REPRODUCIBLE pattern; report the date |
| PFOCR (Pathway Figure OCR) | Hanspers 2020 *Genome Biol* 21:273; Shin 2023 *BMC Genomics* 24:713 | machine-OCR'd gene sets from published figures; larger + noisier, no edges | high-recall disease/process coverage as a complement; NOT what `enrichWP` queries |
| KEGG / Reactome (siblings) | -> kegg-pathways, reactome-pathways | metabolic/signaling maps (live) / curated reactions (local) | the primary databases WP complements |

## Decision Tree by Scenario

| Scenario | Recommended | Why |
|----------|-------------|-----|
| Quick exploratory ORA, reproducibility not yet needed | `enrichWP(entrez, organism, universe=all_entrez)` | fastest path; log that it used the `current/` release |
| Publication / reproducible analysis | `downloadPathwayArchive(date='YYYYMMDD', organism, format='gmt')` -> read -> split -> `enricher`/`GSEA` | the dated GMT is the only cross-time pin; report the date |
| All genes carry a DE statistic, cutoff would be arbitrary | `gseWP` (see the category README for the ORA/GSEA choice) | ranked FCS uses the full list, no cutoff |
| Pre-selected list (module, screen hits, GWAS loci) | `enrichWP` ORA | no ranking available |
| Disease / drug pathways missing from KEGG/Reactome | WP as a complement, run alongside KEGG/Reactome | community content is genuinely additive where it exists |
| Maximum gene/process coverage, noise tolerable | PFOCR (separate resource), not `enrichWP` | figure-OCR sets are higher-recall, lower-precision |
| Non-model but WP-supported species (zebrafish, fly, worm, Arabidopsis) | `enrichWP(entrez, '<scientific name>')`, verify via `get_wp_organisms()` | WP covers ~30+ species |
| Compare up- vs down-regulated | `compareCluster(geneClusters=list(up=..,down=..), fun='enrichWP', organism=)` | one model, faceted dotplot |
| Genes are SYMBOL/ENSEMBL | convert to Entrez first (`bitr`) | the WP GMT is Entrez-keyed; other types overlap nothing |

## Over-Representation Analysis (enrichWP)

**Goal:** Find WikiPathways over-represented in a thresholded gene list, against a defensible background.

**Approach:** Convert significant genes to Entrez, pass the tested-gene set as `universe`, run `enrichWP`, then make the result readable. `enrichWP` downloads the `current/` GMT - acceptable for exploration, but pin a date for anything reportable.

```r
library(clusterProfiler)
library(org.Hs.eg.db)

# enrichWP downloads the current/ WP GMT over the network; symbols/Ensembl must be Entrez first
sig <- bitr(sig_symbols, fromType='SYMBOL', toType='ENTREZID', OrgDb=org.Hs.eg.db)$ENTREZID
all_entrez <- bitr(tested_symbols, fromType='SYMBOL', toType='ENTREZID', OrgDb=org.Hs.eg.db)$ENTREZID

wp <- enrichWP(gene=sig, organism='Homo sapiens', universe=all_entrez,
               pvalueCutoff=0.05, pAdjustMethod='BH', minGSSize=10, maxGSSize=500, qvalueCutoff=0.2)
wp <- setReadable(wp, OrgDb=org.Hs.eg.db, keyType='ENTREZID')   # geneID column -> symbols
as.data.frame(wp)   # ID=WPID, Description, GeneRatio, BgRatio, p.adjust, qvalue, Count
```

## GSEA (gseWP)

**Goal:** Find WikiPathways whose genes shift coordinately across the full ranking, with no cutoff.

**Approach:** Build a NAMED Entrez vector sorted DECREASING by the ranking metric, fix the permutation seed, then run `gseWP`. There is no `universe` argument - FCS uses the whole ranked list.

```r
gl <- sort(setNames(de$log2FoldChange, de$entrez), decreasing=TRUE)   # named, decreasing, Entrez names
set.seed(123)                                                          # fix permutation reproducibility
wp_gsea <- gseWP(geneList=gl, organism='Homo sapiens',
                 pvalueCutoff=0.05, pAdjustMethod='BH', minGSSize=10, maxGSSize=500)
as.data.frame(wp_gsea)   # NES, p.adjust, core_enrichment (the leading edge)
```

## Reproducible Analysis with a Dated GMT (the correct pattern)

**Goal:** Make a WP analysis reproducible across re-runs by pinning a dated release instead of pulling `current/`.

**Approach:** Download a dated GMT (pass `format='gmt'` - the default is `gpml`), split the compound `name%version%wpid%org` term field into TERM2GENE/TERM2NAME, run `enricher`/`GSEA` on the pinned sets, and report the date in methods.

```r
library(rWikiPathways)
library(tidyr)

# downloadPathwayArchive needs an organism to actually download a file (organism=NULL opens the index)
gmt <- downloadPathwayArchive(date='20240310', organism='Homo sapiens', format='gmt', destpath=tempdir())
wp2gene <- read.gmt(file.path(tempdir(), gmt))
wp2gene <- separate(wp2gene, term, c('name','version','wpid','org'), sep='%')   # term is a %-joined compound
t2g <- wp2gene[, c('wpid','gene')]   # TERM2GENE
t2n <- wp2gene[, c('wpid','name')]   # TERM2NAME

wp_pinned <- enricher(sig, universe=all_entrez, TERM2GENE=t2g, TERM2NAME=t2n)   # report date='20240310'
```

`gson_WP(organism)` returns a GSON snapshot object, but it still pulls `current/` - it freezes a session, NOT a chosen historical date. Only the dated `downloadPathwayArchive` GMT survives a re-run months later.

## Query the Database Directly (rWikiPathways)

```r
library(rWikiPathways)

listOrganisms()                          # supported species (full scientific names; ~30+)
listPathways('Homo sapiens')             # all WPIDs + names for a species
getPathwayInfo('WP554')                  # metadata incl. last-edit; check before trusting a single hit
getXrefList('WP554', 'L')                # genes by BridgeDb system code: 'L'=Entrez, 'H'=HGNC, 'En'=Ensembl
findPathwaysByText('cancer')             # text search (searchPathways() is NOT a current function)
```

## Other Organisms

```r
wp_mouse <- enrichWP(gene=mouse_entrez, organism='Mus musculus')
wp_zfish <- enrichWP(gene=zfish_entrez, organism='Danio rerio')
# verify the exact organism string before running:
get_wp_organisms()                       # plural accessor; the string must match exactly
```

## Per-Method Failure Modes

### Unpinned current/ release
**Trigger:** running `enrichWP`/`gseWP`/`gson_WP` without `downloadPathwayArchive(date=)`. **Mechanism:** all three download `data.wikipathways.org/current/`, the latest monthly release. **Symptom:** the same script returns different pathways/p-values months apart, with no error. **Fix:** pin a dated GMT, run `enricher`/`GSEA` on it, and report the date.

### Symbols or Ensembl into an Entrez GMT
**Trigger:** passing SYMBOL/ENSEMBL IDs to `enrichWP`/`gseWP`. **Mechanism:** the WP GMT is Entrez-keyed via BridgeDb, so non-Entrez IDs overlap nothing. **Symptom:** an empty or near-empty result, NO error. **Fix:** `bitr` to ENTREZID first; confirm the conversion rate before trusting the result.

### Default universe inflates significance
**Trigger:** `universe=NULL` (the default). **Mechanism:** `enricher` then uses "all genes in the WP GMT" as background - a small, biased set, not the assayed genes. **Symptom:** implausibly strong p-values for tissue-specific or off-target pathways. **Fix:** pass the tested-gene Entrez vector as `universe`.

### gson_WP mistaken for a reproducibility pin
**Trigger:** treating `gson_WP()` as "the snapshot" for a reproducible analysis. **Mechanism:** it snapshots `current/` into an object - it freezes a session, not a historical date. **Symptom:** a re-run months later gives a different snapshot. **Fix:** use the dated `downloadPathwayArchive` GMT for cross-time reproducibility.

### Unsplit GMT term field
**Trigger:** `read.gmt` on a WP GMT without splitting the term. **Mechanism:** the set-name field is a compound `name%version%wpid%org` joined by `%`. **Symptom:** WPIDs and clean names are buried in one column; TERM2GENE/TERM2NAME are wrong. **Fix:** `separate(., term, c('name','version','wpid','org'), sep='%')` (or use `read.gmt.wp`).

### searchPathways() is gone
**Trigger:** calling `searchPathways('cancer', 'Homo sapiens')`. **Mechanism:** it is not a current rWikiPathways function. **Symptom:** an error. **Fix:** `findPathwaysByText()` / `findPathwayIdsByText()`.

### format defaults to gpml
**Trigger:** `downloadPathwayArchive(date=, organism=)` without `format='gmt'`. **Mechanism:** `format` defaults to `gpml`, which `read.gmt` cannot read. **Symptom:** a GPML file or a parse error. **Fix:** pass `format='gmt'`.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| `pvalueCutoff=0.05` | `enricher`/`GSEA` default | filters on p.adjust (BH) by default; standard FDR gate |
| `qvalueCutoff=0.2` | clusterProfiler `enricher` default | secondary q-value gate on ORA |
| `pAdjustMethod='BH'` | clusterProfiler default | Benjamini-Hochberg FDR; not Bonferroni (too conservative for gene-set screens) |
| `minGSSize=10` | `enricher`/`GSEA` default | drop tiny WP pathways that overfit; many WP specialist sets fall below this and are never tested |
| `maxGSSize=500` | `enricher`/`GSEA` default | drop overly broad sets that always "enrich" |
| `set.seed(123)` for `gseWP` | reproducibility convention | permutation p-values drift across runs without a fixed seed (any fixed seed works) |
| Pin `date='YYYYMMDD'` | Martens 2021 *NAR* 49:D613 | WP republishes monthly; `current/` is not a version, so report the dated release |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| `enrichWP` returns 0 terms | passed SYMBOL/ENSEMBL not Entrez | `bitr` to ENTREZID first |
| Implausibly significant pathways | `universe=NULL` (all-WP-genes background) | pass the tested-gene Entrez vector as `universe` |
| Different results each run | unpinned `current/` release | `downloadPathwayArchive(date=, format='gmt')`; report the date |
| `searchPathways` error | function removed | use `findPathwaysByText()` |
| `read.gmt` term column is a `%`-compound | term field not split | `separate(., term, c('name','version','wpid','org'), sep='%')` |
| `downloadPathwayArchive` opens a browser / downloads nothing | `organism=NULL` | name the organism to actually download a file |
| GPML where a GMT was expected | `format` defaulted to `gpml` | pass `format='gmt'` |
| `gseWP` error about vector names | geneList not named or not sorted decreasing | build a named Entrez vector, `sort(decreasing=TRUE)` |

## References

- Pico AR, Kelder T, van Iersel MP, Hanspers K, Conklin BR, Evelo C. 2008. WikiPathways: pathway editing for the people. *PLoS Biol* 6(7):e184.
- Martens M, Ammar A, Riutta A, et al. 2021. WikiPathways: connecting communities. *Nucleic Acids Res* 49(D1):D613-D621.
- Agrawal A, Balci H, Hanspers K, et al. 2024. WikiPathways 2024: next generation pathway database. *Nucleic Acids Res* 52(D1):D679-D689.
- Hanspers K, Riutta A, Summer-Kutmon M, Pico AR. 2020. Pathway information extracted from 25 years of pathway figures. *Genome Biol* 21:273.
- Shin MG, Pico AR. 2023. Using published pathway figures in enrichment analysis and machine learning. *BMC Genomics* 24:713.
- Wu T, Hu E, Xu S, et al. 2021. clusterProfiler 4.0: A universal enrichment tool for interpreting omics data. *The Innovation* 2(3):100141.

## Related Skills

- go-enrichment - GO over-representation alternative
- gsea - Ranked-list GSEA mechanics and the ranking metric
- kegg-pathways - KEGG pathway/module enrichment (the primary DB WP complements)
- reactome-pathways - Reactome curated-pathway enrichment (the primary DB WP complements)
- enrichment-visualization - Dot/bar/cnet/emap/GSEA plots of the enrichment result
- differential-expression/de-results - Source of the gene list and the ranking statistic
- workflows/expression-to-pathways - End-to-end DE-to-enrichment pipeline
<!-- END FILE: pathway-analysis/wikipathways/SKILL.md -->

<!-- END CATEGORY: pathway-analysis -->

