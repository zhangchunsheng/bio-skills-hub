---
slug: bio-rna-structure-integrated
version: 1.0.0
displayName: "RNA结构 / RNA structure"
name: bio-rna-structure-integrated
summary: >-
  中文：RNA结构综合技能，整合 4 个相关专题，覆盖RNA结构：ViennaRNA二级结构预测、Rfam协方差模型搜索、SHAPE-MaP探测、R-scape共变验证。 English: Integrated RNA structure skill covering 4 related topics, including RNA structure: ViennaRNA secondary structure prediction, Rfam covariance model search, SHAPE-MaP probing, R-scape covariation validation.
description: >-
  中文：这是一个面向RNA结构的综合生物信息学 Skill，整合当前分类下 4 个相关专题能力。它用于根据研究问题、数据类型和分析阶段，选择合适的方法与工具，规划从输入检查、预处理、核心分析到质量控制、统计解释和结果报告的完整流程。重点覆盖：RNA结构：ViennaRNA二级结构预测、Rfam协方差模型搜索、SHAPE-MaP探测、R-scape共变验证。当用户提供相关实验数据、测序结果、表格或研究问题时，它会帮助判断分析目标与前置条件，给出工具选择、关键参数、输入输出、常见失败原因、结果解读和可复现建议。主要工具包括：Infernal, R-scape, ShapeMapper2。该 Skill 提供分析设计与实施指导，不替代对具体数据质量、生物学背景和最终结论的人工审查。
  English: This is an integrated bioinformatics Skill for RNA structure, combining 4 related topic areas. It helps users choose appropriate methods and tools based on the research question, data type, and analysis stage, and plan an end-to-end workflow from input validation and preprocessing through core analysis, quality control, statistical interpretation, and reporting. It covers RNA structure: ViennaRNA secondary structure prediction, Rfam covariance model search, SHAPE-MaP probing, R-scape covariation validation. For relevant experimental data, sequencing results, tables, or research questions, it clarifies prerequisites, recommends tools and parameters, describes expected inputs and outputs, explains common failure modes, and supports reproducible analysis. Primary tools include: Infernal, R-scape, ShapeMapper2. It provides methodological and implementation guidance; final data-quality assessment and biological conclusions still require human review.
---

# rna-structure 分类 Skill 整合版

> 本文件整合同一主分类目录下 4 个子目录中的 SKILL.md 内容。
> 各子目录正文按原文保留，并通过标题和边界标记进行区分；源文件中的元数据块未被改写。

---

<!-- BEGIN CATEGORY: rna-structure -->

## 子目录：rna-structure/covariation-analysis

<!-- BEGIN FILE: rna-structure/covariation-analysis/SKILL.md -->
---
name: bio-rna-structure-covariation-analysis
description: Tests whether a proposed or predicted RNA secondary structure is supported by evolutionary covariation using R-scape, which scores compensatory substitutions against a phylogeny-aware null and estimates the statistical power of the alignment. Use when validating a conserved-structure claim before trusting it (the test that found no support for HOTAIR/Xist/SRA lncRNA structures); separating real covariation from phylogenetic correlation; deciding whether an alignment even has the power to test structure; or building a covariation-supported consensus (CaCoFold) to seed a covariance model or folding.
tool_type: cli
primary_tool: R-scape
---

## Version Compatibility

Reference examples tested with: R-scape 2.0+, Python 3.10+

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `<tool> --version` then `<tool> --help` to confirm flags
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Covariation Analysis

**"Is my RNA's conserved secondary structure real?"** -> Measure whether the base pairs covary across an alignment more than phylogeny and base composition alone would produce, and whether the alignment has the power to detect such covariation.
- CLI: `R-scape -s alignment.sto` to test a given consensus structure
- CLI: `R-scape --cacofold alignment.sto` to build a covariation-supported structure de novo (CaCoFold)

## The governing principle: covariation is the gold standard, but a negative needs POWER

A compensatory (covarying) mutation is the strongest possible evidence for a base pair: if two columns change together across evolution so as to PRESERVE pairing (a G-C in one species becoming A-U in another at the same two positions), that directly evidences the pair, and a structure conserved by covariation across a deep alignment beats any single-sequence thermodynamic prediction. R-scape (Rivas, Clements & Eddy 2017) tests whether observed pairwise covariation EXCEEDS a phylogeny-aware null, separating real structural covariation from the apparent covariation that phylogenetic correlation and biased composition produce on their own.

The load-bearing nuance is that "no significant covariation" is NOT automatically "no structure" -- it can mean the alignment lacks the POWER to detect covariation (too few sequences, or sequences too similar, so there is not enough variation to observe compensatory changes). R-scape estimates, for each pair, the probability it would be called significant if it were a true pair (its power), so the result is a THREE-way verdict, not pass/fail:

| Verdict | Covariation | Power | Meaning |
|---------|-------------|-------|---------|
| Supports a conserved structure | significant pairs found | -- | the structure has evolutionary evidence |
| Rejects a conserved structure | none significant | adequate power | enough variation to detect covariation, yet none -> structure not supported (HOTAIR/Xist/SRA) |
| Cannot infer | none significant | low power | too few/too-similar sequences -> the alignment cannot test structure; gather more diverse homologs |

Reporting only "R-scape found 0 significant pairs" without the power context is the central misuse: a low-power negative says nothing about the structure. R-scape draws the low- vs high-power line at an explicitly arbitrary 10% mean alignment power (the sum of per-pair power over the number of base pairs; Rivas et al. 2020): below ~10%, treat a negative as "cannot infer."

## How R-scape decides

R-scape computes a per-pair covariation statistic (the G-test by default, with average-product correction to remove background phylogenetic signal), builds a null distribution by simulating alignments under the inferred phylogeny and base composition, and assigns each pair an E-value. A pair is significantly covarying when its E-value is at or below the target (default 0.05). It reports the number of expected covarying pairs found, their positions, the inferred substitutions at each, and the per-pair power. Significance is judged against the phylogenetic null, so a raw "positive covariation score" is not enough -- only covariation ABOVE the null counts.

## Test a given consensus structure

The input is a Stockholm alignment with a `#=GC SS_cons` line (the structure to test) -- e.g. an Rfam SEED, an RNAalifold consensus, or a hand-curated structure.

```bash
# -s evaluates the pairs in the alignment's SS_cons; -E sets the E-value target (default 0.05).
# --outdir keeps R-scape's outputs (.cov, .power, .sorted.cov, R2R .svg) out of the CWD.
R-scape -s -E 0.05 --outdir rscape_out alignment.sto
```

With `-s`, R-scape runs TWO tests: one on the pairs in the proposed SS_cons, and a separate one on all OTHER possible pairs -- so a significantly covarying pair OUTSIDE the proposed structure is evidence for a better or alternative fold, not just a yes/no on the given one. (A bare `R-scape alignment.sto` without `-s` tests all possible pairs as one set; `-s` is what scopes the primary test to the proposed structure.)

Outputs include `<msa>.cov` (covarying pairs: positions, score, E-value, substitutions, power), `<msa>.power` (power analysis), `<msa>.sorted.cov`, and an R2R `.svg`/`.pdf` diagram. Read the diagram by its legend: R-scape marks significantly covarying pairs distinctly from pairs that are merely structurally compatible and from pairs inconsistent with the covariation, so the highlighted pairs are the ones with evolutionary support. The header reports nseq, alignment length, average identity, and number of base pairs.

## Build a covariation-supported structure de novo (CaCoFold)

When there is no trusted structure to test, let covariation drive the fold. CaCoFold (`--cacofold`, also accepted as `--fold`) maximizes the support from significantly covarying pairs and can include pseudoknots as additional structure layers.

```bash
# Predict a structure from the alignment's covariation; writes a CaCoFold .sto with a new SS_cons.
R-scape --cacofold -E 0.05 --outdir rscape_out alignment.sto
```

The CaCoFold structure is grounded in evolutionary evidence rather than thermodynamics alone, which makes it a strong consensus to seed a covariance model (ncrna-search) or to compare against a thermodynamic fold (secondary-structure-prediction).

## The lncRNA cautionary tale

R-scape found NO statistically significant covariation support for the proposed secondary structures of the lncRNAs HOTAIR, SRA, and Xist (Rivas et al. 2017), despite their being thermodynamically plausible and widely cited. The lesson: a thermodynamically reasonable, even phylogenetically suggestive, structure is NOT established until covariation is statistically demonstrated, and for many lncRNAs the structural conservation is simply not there. Always run this test before asserting a conserved structure, and always report whether a negative is a power-limited "cannot infer" or a powered "rejects."

## Practical requirements

- Use a DEEP, DIVERSE alignment: covariation needs sequences that actually vary at paired columns while preserving the pair. Near-identical sequences carry no covariation signal (low power); a handful of sequences cannot test structure.
- Power is driven by the number of independent SUBSTITUTIONS at a pair, not the raw sequence count: a few near-identical sequences have essentially zero power, and meaningful power usually needs dozens of homologs spanning a broad identity range (well below ~90-95% average pairwise identity, ideally down toward ~60%). Size the alignment by R-scape's `.power` output, not by a fixed sequence count.
- Building the alignment is the real bottleneck for poorly conserved RNAs (lncRNAs especially): gather diverged homologs (e.g. synteny-anchored orthologs, an Infernal/cmsearch sweep, or RNAcentral) and align with a structure-aware aligner -- a bad alignment both destroys real covariation and manufactures spurious signal.
- Alignment quality matters: misaligned columns destroy real covariation and can manufacture spurious signal. Validate the alignment before trusting either a positive or a negative.
- Covariation tests CONSERVATION of structure, which is a different question from whether the RNA is a real, expressed transcript -- "is it real" in the transcription/processing sense needs expression and functional evidence, not R-scape.
- R-scape tests pairs, not whole helices alone; helix-level aggregation is available in recent versions for noisier alignments -- check `R-scape --help` for the current options.

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| "0 significant pairs" reported as "no structure" | ignoring power | check the `.power` output; a low-power negative is "cannot infer", not "rejects" |
| R-scape exits with no pairs tested | alignment has no `#=GC SS_cons` and `-s` was used | add a consensus structure, or use `--cacofold` to predict one |
| Outputs (.cov, .svg) dumped into the working directory | no output directory set | pass `--outdir <dir>` |
| Spurious covariation across the whole alignment | misaligned columns or strong phylogenetic correlation | improve the alignment; R-scape's null already corrects phylogeny, but bad alignments still mislead |
| A positive covariation score assumed to validate a pair | score is not significance | require E-value <= target (0.05) against the phylogenetic null, not a raw positive score |

## Related Skills

- secondary-structure-prediction - Predict the structure whose conservation is then tested
- ncrna-search - Validate a custom CM's SS_cons here before building the covariance model
- structure-probing - Experimental evidence complementary to evolutionary covariation
- alignment/msa-statistics - Assess the alignment depth and diversity covariation needs
- phylogenetics/tree-io - The phylogeny underlying the covariation null

## References

- Rivas E, Clements J, Eddy SR. 2017. A statistical test for conserved RNA structure shows lack of evidence for structure in lncRNAs. Nat Methods 14(1):45-48. doi:10.1038/nmeth.4066
- Rivas E, Clements J, Eddy SR. 2020. Estimating the power of sequence covariation for detecting conserved RNA structure. Bioinformatics 36(10):3072-3076. doi:10.1093/bioinformatics/btaa080
- Rivas E. 2020. RNA structure prediction using positive and negative evolutionary information. PLoS Comput Biol 16(10):e1008387. doi:10.1371/journal.pcbi.1008387
- Nawrocki EP, Eddy SR. 2013. Infernal 1.1: 100-fold faster RNA homology searches. Bioinformatics 29(22):2933-2935. doi:10.1093/bioinformatics/btt509
<!-- END FILE: rna-structure/covariation-analysis/SKILL.md -->

## 子目录：rna-structure/ncrna-search

<!-- BEGIN FILE: rna-structure/ncrna-search/SKILL.md -->
---
name: bio-rna-structure-ncrna-search
description: Searches for non-coding RNA homologs and classifies RNA families with Infernal covariance models against Rfam, scoring sequence AND secondary-structure conservation jointly. Use when deciding whether a covariance model is the right tool versus BLAST/nhmmer (structured ncRNA versus lncRNA or mature miRNA); choosing the Rfam gathering threshold over a flat E-value; resolving clan overlaps; building and calibrating a custom CM from a structure-annotated alignment; or preferring a family-specialized tool (tRNAscan-SE, barrnap) over a generic Rfam scan.
tool_type: cli
primary_tool: Infernal
---

## Version Compatibility

Reference examples tested with: Infernal 1.1.4+, BioPython 1.83+, pandas 2.2+

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `<tool> --version` then `<tool> --help` to confirm flags
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# ncRNA Search

**"Search my sequences for known non-coding RNA families"** -> Score candidates against Rfam covariance models that capture both sequence and consensus secondary structure, or build a custom model for a novel family.
- CLI: `cmscan` for querying sequences against the Rfam CM database
- CLI: `cmsearch` for one CM against a sequence database
- CLI: `cmbuild` + `cmcalibrate` + `cmpress` for a custom covariance model

## The governing principle: a covariance model is only worth it for STRUCTURED RNA

A covariance model (CM) is a profile stochastic context-free grammar that models a family's consensus secondary structure AND primary sequence jointly. Its power source is covariation: a base pair is scored by a joint distribution over pair states, so a compensatory double mutation (C-G to G-C, or a G-U wobble) that PRESERVES the pair scores well even though both positions changed -- a BLAST or profile-HMM sees two mismatches and loses the signal. This is why Infernal detects remote homologs of structured RNAs (tRNA, rRNA, riboswitches, SRP, RNase P, ribozymes, snoRNA) past the sequence twilight zone.

The decisive corollary: a CM offers NO advantage when there is little conserved secondary structure to exploit. Many lncRNAs (R-scape finds no significant covariation in HOTAIR/Xist/SRA), mature miRNAs (~22 nt, no base-pairing in the mature strand), and primary-sequence-only motifs gain nothing from a CM -- it is slow and calibration-heavy, and a profile-HMM (nhmmer) or BLASTN is the correct, faster tool. A CM built from a structure-FREE alignment (no real `#=GC SS_cons` pairs) collapses to an HMM and buys nothing but runtime.

| Query / target property | Right tool | Why |
|---|---|---|
| Structured ncRNA, remote homology (tRNA, rRNA, riboswitch, ribozyme, SRP, snoRNA) | Infernal CM (Rfam) | covariation recovers pairs across sequence divergence |
| Structured RNA with a family-specialized tool | the specialist (table below) | tuned models + biology logic beat a generic scan |
| Close homolog, high identity, any RNA | BLASTN / nhmmer | sequence signal suffices, 100-1000x faster |
| lncRNA, mature miRNA, sequence-only motif | nhmmer / BLASTN | no conserved structure to exploit -> CM is overhead |
| Novel structured RNA, no Rfam family | build a custom CM, AFTER validating structure with R-scape | a CM is only as good as its SS_cons |

## Infernal toolchain

- `cmbuild model.cm aln.sto` -- build a CM from a structure-annotated Stockholm alignment; REQUIRES a `#=GC SS_cons` line.
- `cmcalibrate model.cm` -- fit E-value statistics; SLOW (minutes to hours) but MANDATORY before any E-value is meaningful. Without it, search still runs but only bit-score thresholding is valid.
- `cmpress model.cm` -- build the binary index `cmscan` requires (cmsearch does not need it).
- `cmsearch CM seqdb` -- one CM vs a sequence database (e.g. one family vs a genome).
- `cmscan CMdb seqs` -- query sequences vs a CM database (e.g. all of Rfam.cm); this is the genome/transcript ncRNA-annotation layout.
- `cmalign CM seqs` -- align/fold hits back to the CM consensus to recover each hit's secondary structure.

Rfam.cm ships PRE-CALIBRATED: run `cmpress` on it, but do NOT `cmcalibrate` it. Calibration is only for locally built custom models, and must be re-run after every rebuild.

## E-values depend on database size; gathering thresholds do not

A CM E-value scales linearly with the searched database size (Z): the SAME hit gets a different E-value depending on what was searched. `cmsearch` Z defaults to the target sequence-DB size counted on both strands (total residues x2); `cmscan` Z defaults to (query length x2 x number of models). So a cmscan E-value and a cmsearch E-value for the same locus are NOT comparable, and a flat `-E 1e-5` is exactly what curated thresholds replace. Fix Z explicitly with `-Z <Mb>` for reproducible cross-run comparison.

Bit scores are DB-size-INDEPENDENT, which is precisely why Rfam stores its curated cutoffs as bit scores:

| Flag | Threshold (bit-score cutoff stored in the CM) | When |
|---|---|---|
| `--cut_ga` | GA (gathering): the curated family-membership cutoff | the correct DEFAULT for Rfam annotation |
| `--cut_tc` | TC (trusted): lowest score of any known true positive | most conservative |
| `--cut_nc` | NC (noise): highest score of a known false positive | most permissive, exploratory |
| `-E` / `--incE` | flat E-value (reporting / inclusion) | custom CM, or a non-Rfam DB with no curated GA |
| `-T` / `--incT` | flat bit score | custom CM with no calibration, or DB-size-robust cut |

`--cut_ga` beats a flat E-value for Rfam because each family has a different signal-to-noise profile (a 70 nt tRNA vs a 2900 nt rRNA vs a short riboswitch); one flat cutoff over- or under-calls per family, and reintroduces the DB-size dependence GA was designed to avoid.

## The canonical Rfam annotation command

```bash
# One-time setup
wget https://ftp.ebi.ac.uk/pub/databases/Rfam/CURRENT/Rfam.cm.gz && gunzip Rfam.cm.gz
wget https://ftp.ebi.ac.uk/pub/databases/Rfam/CURRENT/Rfam.clanin
cmpress Rfam.cm   # NOT cmcalibrate -- Rfam.cm is pre-calibrated

# Annotate a genome. -Z = 2 x genome size in Mb keeps E-values reproducible; --rfam is the
# large-DB strict filter; --nohmmonly forces CM mode so GA cutoffs stay valid for every model.
cmscan -Z 100 --cut_ga --rfam --nohmmonly --fmt 2 --clanin Rfam.clanin \
    --tblout genome.tblout Rfam.cm genome.fa > genome.cmscan

# Clan deoverlapping: --fmt 2 adds the 'olp' column; the documented Rfam filter drops hits
# marked '=' (dominated by a higher-scoring clanmate), keeping '^' (best of an overlap) and '*' (no overlap).
grep -v ' = ' genome.tblout > genome.deoverlapped.tblout
```

`--clanin` with `--fmt 2` plus the `grep -v ' = '` post-filter is the documented deoverlap path; `--oclan` is a valid in-tool alternative but not what the modern Rfam pipeline uses, so do not treat it as mandatory.

## Reading --fmt 2 output (the column shift that breaks fmt-1 parsers)

`--fmt 2` prepends an `idx` column and inserts a `clan name` column versus the default `--fmt 1`, so every downstream field index shifts -- a parser written for fmt 1 silently reads the wrong columns. Verified 0-based fmt-2 cmscan indices: idx 0, target/family name 1, accession 2, query/seq name 3, query accession 4, clan 5, mdl type 6, mdl_from 7, mdl_to 8, seq_from 9, seq_to 10, strand 11, trunc 12, pass 13, gc 14, bias 15, score 16, E-value 17, inc 18, olp 19. In cmscan the model name is column 1 and the sequence name is column 3; in cmsearch they are reversed -- a parser must branch on which tool produced the file.

Interpretive columns: `trunc` is `no`, `5'`, `3'`, or `5'&3'` for hits running off a contig end (often REAL incomplete genes worth keeping, not a discard flag; `--anytrunc` allows truncation at any internal position (E-values become less accurate), `--notrunc` disables it entirely); `bias` is the composition correction already subtracted (a large bias flags a low-complexity hit); mdl_from/mdl_to are consensus coordinates, so a small model span is a partial match even when `trunc` is `no`.

## Recovering the structure of a hit (the CM payoff over BLAST)

A significant CM hit yields not just a family label but an implied secondary structure -- the distinctive payoff a BLAST hit cannot give. Fold the hit sequences back to the model with `cmalign` to map the consensus structure onto them.

```bash
# Pull the family CM from Rfam, then align hits to recover their consensus structure
cmfetch Rfam.cm RF00005 > tRNA.cm
cmalign --outformat Pfam tRNA.cm hits.fa > hits.sto   # Stockholm with #=GC SS_cons per hit
```

The `#=GC SS_cons` line in the output is the structural hypothesis for each hit -- the prior to feed to probing (structure-probing) or to validate with covariation (covariation-analysis).

## A hit is a family assignment, not a functional call

A significant CM hit means the locus has sequence + structure consistent with the family; it does NOT prove the RNA is expressed, processed, or functional. Pseudogenes (tRNA-derived SINEs, rRNA pseudogenes) score well. tRNAscan-SE's high-confidence-set logic exists precisely to separate likely-functional tRNAs from numerous genomic pseudogenes. Frame a CM hit as a family assignment plus a structural hypothesis; confirm function with orthogonal evidence (expression, conservation, synteny, probing).

## Specialized tool beats a generic Rfam scan (when one exists)

| RNA class | Use this, not a generic Rfam scan | Why |
|---|---|---|
| tRNA | tRNAscan-SE 2.0 | tRNA-specific isotype/anticodon models, pseudogene filtering, high-confidence set |
| rRNA (5S/16S/18S/23S/28S) | barrnap or RNAmmer | per-kingdom HMM models tuned for rRNA; fast |
| C/D-box snoRNA | snoscan | models the guide-target duplex + box C/D a generic CM cannot |
| H/ACA + C/D snoRNA (ab initio) | snoReport 2.0 | RNA-fold + SVM on box/structure features |
| miRNA | miRBase lookup / miRDeep2 | CMs are poor on mature miRNA; precursors need read support |

Use the generic Rfam cmscan for broad "what ncRNA families are in here" sweeps and for classes without a dedicated tool.

## Building a custom CM well

```bash
# The Stockholm alignment MUST carry a #=GC SS_cons line in WUSS notation: <> or () = nested pairs,
# [] and {} = additional pseudoknot layers, . = unpaired (a structure-free alignment yields only an
# HMM-equivalent model). Validate the SS_cons covariation with R-scape FIRST (covariation-analysis).
cmbuild -n MYFAM myfam.cm alignment.sto
cmcalibrate --cpu 8 myfam.cm     # required for E-values; re-run after every rebuild
cmpress myfam.cm
cmsearch --cpu 8 -T 30 --tblout hits.tbl myfam.cm target.fa > hits.out
```

If `cmcalibrate` is skipped, thresholding MUST use bit score (`-T <bits>`), not E-value. The iterative search-align-rebuild loop (`cmsearch -A new_hits.sto`) grows a family but risks homology overextension and model drift -- gate each round on score and retained covariation, and recalibrate after every rebuild.

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| Parsed `score`/`evalue` are nonsense numbers | parsing `--fmt 2` output with fmt-1 indices | use fmt-2 indices (score 16, E-value 17), or run `--fmt 1` |
| `Error: failed to open ... .i1m` (cmscan) | Rfam.cm not pressed | `cmpress Rfam.cm` |
| E-values look meaningful on a custom CM but are not | `cmcalibrate` was skipped | calibrate, or threshold on bit score `-T` |
| Recalibrating Rfam.cm takes hours | Rfam.cm is already calibrated | press it, never calibrate it |
| Same hit, different E-value across runs | E-value scales with database size Z | use `--cut_ga`, or fix `-Z <Mb>` |
| Redundant overlapping hits from related families | clan overlap not resolved | `--fmt 2 --clanin` then `grep -v ' = '` |
| A CM search on a lncRNA finds nothing useful | no conserved structure to exploit | use nhmmer/BLASTN instead of a CM |
| tRNA search misses or over-calls genes | generic Rfam tRNA model lacks tRNA logic | use tRNAscan-SE 2.0 |

## Related Skills

- secondary-structure-prediction - Predict structure for novel ncRNA candidates with no Rfam hit
- covariation-analysis - Validate a custom CM's SS_cons with R-scape before building
- structure-probing - Experimental reactivities to corroborate a CM's consensus structure
- genome-annotation/ncrna-annotation - Genome-wide ncRNA annotation pipelines
- alignment/msa-statistics - Evaluate alignment quality before CM building
- database-access/entrez-fetch - Fetch Rfam/RNAcentral records

## References

- Eddy SR, Durbin R. 1994. RNA sequence analysis using covariance models. Nucleic Acids Res 22(11):2079-2088. doi:10.1093/nar/22.11.2079
- Nawrocki EP, Eddy SR. 2013. Infernal 1.1: 100-fold faster RNA homology searches. Bioinformatics 29(22):2933-2935. doi:10.1093/bioinformatics/btt509
- Griffiths-Jones S, Bateman A, Marshall M, Khanna A, Eddy SR. 2003. Rfam: an RNA family database. Nucleic Acids Res 31(1):439-441. doi:10.1093/nar/gkg006
- Kalvari I, Nawrocki EP, Ontiveros-Palacios N, Argasinska J, Lamkiewicz K, Marz M, Griffiths-Jones S, Toffano-Nioche C, Gautheret D, Weinberg Z, Rivas E, Eddy SR, Finn RD, Bateman A, Petrov AI. 2021. Rfam 14: expanded coverage of metagenomic, viral and microRNA families. Nucleic Acids Res 49(D1):D192-D200. doi:10.1093/nar/gkaa1047
- Chan PP, Lin BY, Mak AJ, Lowe TM. 2021. tRNAscan-SE 2.0: improved detection and functional classification of transfer RNA genes. Nucleic Acids Res 49(16):9077-9096. doi:10.1093/nar/gkab688
- Lagesen K, Hallin P, Rodland EA, Staerfeldt HH, Rognes T, Ussery DW. 2007. RNAmmer: consistent and rapid annotation of ribosomal RNA genes. Nucleic Acids Res 35(9):3100-3108. doi:10.1093/nar/gkm160
- Lowe TM, Eddy SR. 1999. A computational screen for methylation guide snoRNAs in yeast. Science 283(5405):1168-1171. doi:10.1126/science.283.5405.1168
- Rivas E, Clements J, Eddy SR. 2017. A statistical test for conserved RNA structure shows lack of evidence for structure in lncRNAs. Nat Methods 14(1):45-48. doi:10.1038/nmeth.4066
<!-- END FILE: rna-structure/ncrna-search/SKILL.md -->

## 子目录：rna-structure/secondary-structure-prediction

<!-- BEGIN FILE: rna-structure/secondary-structure-prediction/SKILL.md -->
---
name: bio-rna-structure-secondary-structure-prediction
description: Predicts RNA secondary structure with ViennaRNA, treating the Boltzmann ensemble (partition function, base-pair probabilities, centroid, MEA, stochastic samples) as the object rather than a single MFE fold. Covers consensus folding from alignments (RNAalifold), SHAPE-constrained folding, RNA-RNA interaction (RNAcofold/RNAduplex/RNAup), local and linear-time methods for long RNA, and pseudoknot-aware tools. Use when folding an RNA and choosing between MFE, centroid, MEA, or ensemble sampling; judging whether a single structure is well-defined; folding long RNAs where a global MFE is meaningless; handling suspected pseudoknots; or weighing thermodynamic versus comparative versus deep-learning prediction.
tool_type: cli
primary_tool: ViennaRNA
---

## Version Compatibility

Reference examples tested with: ViennaRNA 2.6+, matplotlib 3.8+, numpy 1.26+

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `<tool> --version` then `<tool> --help` to confirm flags
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Secondary Structure Prediction

**"Predict the secondary structure of my RNA sequence"** -> Compute base pairs under a nearest-neighbor thermodynamic model, but report the Boltzmann ENSEMBLE (partition function, base-pair probabilities, centroid/MEA, per-base confidence), not a single fold.
- CLI: `RNAfold -p` for single-sequence ensemble folding
- CLI: `RNAalifold` for consensus structure from an alignment
- CLI: `RNAcofold` / `RNAduplex` / `RNAup` for RNA-RNA interaction
- Python: `import RNA` (`fold_compound`) for scripted ensemble analysis

## The governing principle: the MFE is one sample from an ensemble, not "the structure"

The minimum free energy (MFE) structure is the single lowest-energy fold, but every possible structure has probability proportional to exp(-G/RT). The partition function (McCaskill 1990) sums over that whole Boltzmann ensemble and yields the probability of each base pair, not just one fold. The MFE is frequently NOT the biologically relevant structure: riboswitches sit at a poised switch between two folds, many RNAs are genuinely dynamic, and the functional fold is often slightly suboptimal. Report the MFE alone and the uncertainty is hidden.

Three consequences shape every decision below:
- Trust the ENSEMBLE, not the point estimate. Use partition-function quantities (base-pair probability > 0.9, low positional entropy, low ensemble diversity) as the per-pair and per-base confidence. A low MFE with a diffuse base-pair-probability matrix means the single structure is not trustworthy.
- Accuracy is modest and length-dependent. Single-sequence thermodynamic folding recovers ~70-73% of base pairs for short, well-behaved RNAs (tRNA, 5S rRNA) and degrades sharply beyond ~700 nt. A single global MFE of a multi-kilobase mRNA or viral genome is close to meaningless -> use local (RNAplfold), linear-time (LinearFold/LinearPartition), comparative, or probing-restrained methods.
- ViennaRNA folds only nested canonical + wobble (G-U) pairs. Pseudoknots are silently excluded (general pseudoknot prediction is NP-hard); non-canonical pairs (sheared G-A, base triples, the Leontis-Westhof geometric families) are invisible. A confidently wrong nested fold is the failure mode for frameshift elements, riboswitch aptamers, and viral UTRs.

## Which ViennaRNA program for which question

| Question / input | Tool | Why |
|---|---|---|
| Fold one sequence, want structure + confidence | RNAfold -p | MFE + partition function (centroid/MEA/diversity) |
| Ensemble free energy only, no dot plot (speed) | RNAfold -p0 | skips base-pair probabilities, ~50% faster |
| Consensus structure from an alignment of homologs | RNAalifold | thermodynamics + covariation |
| Two RNAs that dimerize (full model + concentrations) | RNAcofold (-c) | intra+inter pairs, equilibrium species |
| Fast two-strand hybridization screen | RNAduplex | inter-molecular pairs only, no internal structure |
| sRNA/miRNA-target where site accessibility matters | RNAup | opening energy + hybridization (correct for buried sites) |
| Sample alternative conformations | RNAsubopt -p N / `fc.pbacktrack(n)` | Boltzmann sampling |
| Long mRNA: local pairing / target accessibility | RNAplfold | windowed pair + unpaired probabilities |
| Long RNA/genome: find local structured elements | RNALfold | locally stable structures, bounded span |
| Sequence longer than a few kb | LinearFold / LinearPartition | O(n), avoids a meaningless global O(n^3) fold |
| Pseudoknot suspected | IPknot / ProbKnot / Knotty | nested folders structurally cannot |
| Have SHAPE/DMS reactivities | RNAfold --shape (Deigan) | restrain folding with experimental data |

## Which "answer" to report

| Goal | Answer | Note |
|---|---|---|
| Quick single estimate | MFE | over-calls weak pairs; not for long/low-complexity RNA |
| Conservative, ensemble-representative structure | centroid | minimum total base-pair distance to ensemble; fewer false pairs, can under-pair |
| Best single structure (esp. with probing data) | MEA (tune gamma) | high gamma -> more pairs/recall, low gamma -> fewer/precision |
| Per-pair / per-base confidence | base-pair probability (>0.9) + positional entropy | structure-agnostic confidence track |
| Conformational switching / multiple states | stochastic sampling | cluster the samples into populations |
| Is one structure well-defined? | ensemble diversity (low) + ensemble defect | length-relative, not an absolute cutoff |

## RNAfold: single-sequence ensemble folding

```bash
# MFE only
echo "GGGCUAUUAGCUCAGUUGGUUAGAGCGCACCCCUGAUAAGGGUGAGGUCGCUGAUUCGAAUUCAGCAUAGCCCA" | RNAfold --noPS

# Ensemble: partition function + base-pair probabilities + centroid + MEA + ensemble diversity
# --noPS suppresses the *_dp.ps / *_ss.ps PostScript files RNAfold writes to the CWD by default
echo ">myRNA" > rna.fa && echo "GGGCUAUUAGCUCAGUUGGUUAGAGCGCACC" >> rna.fa
RNAfold -p --MEA --noLP --noPS < rna.fa
```

Key flags (verified against the current manpage):

| Option | Effect |
|--------|--------|
| `-p` | partition function + base-pair-probability matrix (unlocks centroid/MEA/diversity) |
| `-p0` | ensemble free energy ONLY, no base-pair probabilities (faster) |
| `--MEA[=gamma]` | maximum-expected-accuracy structure (default gamma 1.0); `--MEA` implies `-p` |
| `-d2` | dangling-end model (default); use `-d0` for comparative/alignment folding to avoid dangle artifacts |
| `-d3` | also allow coaxial stacking of adjacent helices in multiloops (MFE folding only; the partition function `-p` ignores `-d3` and falls back to `-d2`, so ensemble quantities do not reflect it) |
| `--noLP` | forbid lonely (isolated) base pairs; standard for well-folded RNA |
| `--maxBPspan N` | cap base-pair span; crude knob for long sequences |
| `-T 37` | folding temperature in Celsius (default 37) |
| `--shape FILE` / `--shapeMethod` | SHAPE-directed folding (see structure-probing) |
| `-g` | allow G-quadruplex formation (default off; turn on for G-rich sequences where G4s compete with canonical pairing) |
| `--noPS` | suppress PostScript drawings (always set in scripts to avoid CWD clutter) |

## Centroid, MEA, sampling, and per-base confidence (Python)

`fc.pf()` MUST be called before `bpp()`, `centroid()`, `MEA()`, `pbacktrack()`, `positional_entropy()`, `ensemble_defect()`, or `mean_bp_distance()` -- they all read the partition-function matrices and silently return empty/garbage otherwise.

```python
import RNA

seq = 'GCGGAUUUAGCUCAGUUGGGAGAGCGCCAGACUGAAGAUCUGGAGGUCCUGUGUUCGAUCCACAGAAUUCGCACCA'
fc = RNA.fold_compound(seq)

mfe_struct, mfe = fc.mfe()
_, ensemble_g = fc.pf()                 # partition function; ensemble G <= MFE always

centroid, _ = fc.centroid()             # conservative, fewer false-positive pairs
mea_struct, _ = fc.MEA()                # MEA(gamma); gamma>1 favors pairing (recall), gamma<1 precision
diversity = fc.mean_bp_distance()       # ensemble diversity: low = well-defined (read RELATIVE to length)
defect = fc.ensemble_defect(mfe_struct) # expected wrongly-paired positions of this structure vs ensemble
entropy = fc.positional_entropy()       # per-base Shannon entropy: low = confidently paired-or-unpaired

```

Sample alternative conformations from the Boltzmann ensemble (riboswitches, bistable RNA) with the CLI `RNAsubopt -p N` (N stochastic samples) or the Python `fc.pbacktrack(N)` after `fc.pf()`; cluster the samples to find conformational populations. `fc.pbacktrack` requires a ViennaRNA build with stochastic backtracking enabled -- if it returns nothing, use `RNAsubopt -p N`.

Decision rule: one well-defined structure -> centroid or MEA; report stability/confidence -> partition-function quantities (base-pair probabilities + positional entropy); conformational switching -> stochastic sampling; quick single estimate -> MFE (with the caveats above).

## Constrained and SHAPE-directed folding

```python
import RNA

seq = 'GCGGAUUUAGCUCAGUUGGGAGAGCGCCAGACUGAAGAUCUGGAGGUCCUGUGUUCGAUCCACAGAAUUCGCACCA'

# Hard constraints: force positions unpaired or paired
fc = RNA.fold_compound(seq)
fc.hc_add_up(35, RNA.CONSTRAINT_CONTEXT_ALL_LOOPS)   # 1-indexed; force position 35 unpaired
fc.hc_add_bp(1, 72, RNA.CONSTRAINT_CONTEXT_ALL_LOOPS)
constrained, c_mfe = fc.mfe()

# Soft SHAPE pseudo-energy restraint (Deigan model). The reactivity vector is 1-INDEXED:
# prepend -999 as a placeholder for index 0; -999 elsewhere means "no data" (NOT zero reactivity).
# m=1.8, b=-0.6 is the standard SHAPE pair (Hajdin 2013, the ViennaRNA default), not Deigan 2009's own m=2.6/b=-0.8.
fc2 = RNA.fold_compound(seq)
reactivities = [-999.0] + [0.1, 0.05, 0.8, 0.9] + [-999.0] * (len(seq) - 4)
fc2.sc_add_SHAPE_deigan(reactivities, 1.8, -0.6)
shape_struct, shape_mfe = fc2.mfe()   # this energy INCLUDES the SHAPE pseudo-energy; do NOT compare it to the unrestrained MFE
```

The energy returned after a SHAPE restraint folds in the pseudo-energy bonus, so it is not on the same scale as an unconstrained MFE -- compare the STRUCTURES (base-pair distance, SHAPE agreement), not the two energy numbers. See structure-probing for obtaining reactivities and for the SHAPE-vs-DMS parameter choice.

## Comparative (consensus) folding: homologs beat a single sequence

Evolution conserves structure while sequence drifts, so a compensatory substitution (an A-U in one species becoming G-C at the same two columns) is direct evidence of a real pair that thermodynamics alone cannot see. RNAalifold folds an alignment with a combined thermodynamic + covariation score.

```bash
# Consensus structure; format (Stockholm/Clustal/FASTA) is auto-detected, alignment is positional.
# --ribosum_scoring improves covariation detection; -d0 avoids dangle artifacts at gapped columns.
RNAalifold --ribosum_scoring -d0 -p --noPS alignment.sto
```

| Option | Effect |
|--------|--------|
| `--cfactor` | covariation weight (default 1.0; lower leans on thermodynamics) |
| `--nfactor` | penalty for sequences that cannot form the consensus pair (default 1.0) |
| `--ribosum_scoring` | use RIBOSUM covariation matrices (recommended) |
| `-p` | consensus partition function + base-pair probabilities |

RNAalifold accuracy depends entirely on alignment quality and real covariation: near-identical sequences carry no covariation signal and it degrades toward noisy single-sequence folding. RNAalifold assumes a FIXED, correct alignment; when homologs cannot be aligned reliably, TurboFold II co-estimates alignment AND structure across the sequences jointly (Tan et al. 2017) and is the better choice. A predicted consensus structure is a HYPOTHESIS until covariation is statistically validated -- test it with R-scape (see covariation-analysis), which found no significant covariation support for the proposed HOTAIR/Xist/SRA lncRNA structures.

## Long RNA: do not fold one global structure

For a multi-kilobase mRNA, lncRNA, or viral genome, a single global O(n^3) MFE both over-pairs across long ranges and is slow, and folding is co-transcriptional and local in reality.

```bash
# Windowed local pairing + per-position UNPAIRED (accessibility) probabilities
RNAplfold -W 200 -L 150 -u 30 < long_rna.fa      # -W window, -L max base-pair span, -u accessibility region length

# Scan for locally stable structured elements with a bounded span
RNALfold -L 150 < long_rna.fa

# Linear-time approximate MFE (LinearFold) and partition function (LinearPartition), if installed
echo "GGGAAACCC..." | linearfold
echo "GGGAAACCC..." | linearpartition
```

LinearFold's 5'->3' beam search can match or improve accuracy versus the exact cubic algorithm on long RNAs (the exact global model is not more correct when a single structure is not meaningful), besides being far faster.

## Pseudoknots: ViennaRNA cannot, by construction

The standard dynamic programming forbids crossing pairs, and general pseudoknot prediction is NP-hard (Lyngso & Pedersen 2000) -- RNAfold/RNAalifold silently return the best NESTED structure. Suspect a pseudoknot for tmRNA, telomerase RNA, RNase P, many riboswitch aptamers (SAM-II, preQ1), -1 ribosomal frameshift elements, IRES, and group I/II intron cores.

| Tool | Class / method | Note |
|------|----------------|------|
| IPknot | integer programming over base-pair probabilities | fast, broad class, the pragmatic default |
| ProbKnot | MEA assembly from McCaskill probabilities (RNAstructure) | any topology, fastest/most scalable |
| Knotty | MFE over the broad CCJ class | more complex crossing topologies |
| pknotsRG | MFE over restricted simple recursive pseudoknots, O(n^4) | narrower class |

Pseudoknot prediction is substantially less accurate and more expensive than nested folding -- treat any predicted pseudoknot as a hypothesis to corroborate with a second tool, covariation, or probing.

## RNA-RNA interaction: pick by the binding question

| Tool | Models | Use when |
|------|--------|----------|
| RNAcofold | both intramolecular AND intermolecular pairs; `-c` gives equilibrium concentrations | full dimerization model |
| RNAduplex | inter-molecular pairs only (no internal structure), fast | first-pass target screen |
| RNAup | opening (accessibility) energy + hybridization energy | sRNA/miRNA-target where the site may be buried in structure (the physically correct choice) |

The two strands are concatenated with `&` (RNAcofold/RNAduplex); RNAup takes the two sequences on separate lines.

```bash
# Full dimer model (intra + inter pairs); -p for the heterodimer partition function
echo "GCGCGCAUAU&AUAUGCGCGC" | RNAcofold -p --noPS
# With -c, RNAcofold reads the two monomer concentrations and reports equilibrium fractions of the
# five species (AB, AA, BB, A, B) -- use it to ask how much dimer actually forms, not just whether it is favorable.

# Fast inter-molecular-only hybridization screen (no internal structure)
echo "GCGCGCAUAU&AUAUGCGCGC" | RNAduplex

# Accessibility-corrected sRNA/miRNA-target binding: opening energy + hybridization (-b includes both)
RNAup -b < two_sequences.fa
```

## Thermodynamics vs deep learning: DL is not a default for novel RNA

Deep-learning predictors (SPOT-RNA, UFold, E2Efold) report high accuracy ON FAMILIES SEEN IN TRAINING, but under family-fold cross-validation that removes train/test homology their accuracy collapses to at or below the thermodynamic baseline (Szikszai et al. 2022); the apparent gains are intra-family memorization, and benchmark sets are ~55% rRNA / >90% rRNA+tRNA (Flamm et al. 2022). For a genuinely novel RNA (unseen Rfam family), no single-sequence method (DL or thermodynamic) is reliable -- the robust evidence is covariation (R-scape) and experimental probing. If using DL, prefer the thermodynamics-integrated hybrid MXfold2 over end-to-end nets; never cite intra-family accuracy as proof of de-novo performance.

"Is this more structured than random?" (z-score vs shuffled controls, RNAz, randfold): shuffles MUST preserve DINUCLEOTIDE composition (Altschul-Erikson), because MFE is dominated by GC content and base stacking, a dinucleotide property -- a mononucleotide shuffle inflates significance and makes almost anything look stable. For an alignment, RNAz combines a dinucleotide-controlled z-score with a structure conservation index (SCI = consensus MFE / mean single-sequence MFE; ~1 = a conserved structure), but reads Clustal/MAF, not Stockholm. A negative z-score means "more stable than random," NOT "this structure is correct"; covariation is the stronger evidence standard.

## Method-class selection (the big fork)

| Situation | Recommended | Avoid as default |
|---|---|---|
| Single novel RNA, no homologs | thermodynamic ensemble (RNAfold -p / RNAstructure) | pure end-to-end DL |
| Aligned homologs with covariation | RNAalifold + R-scape validation | single-sequence MFE |
| Homologs but no trusted alignment | TurboFold II (joint alignment + structure) | align-then-RNAalifold on a poor alignment |
| Have SHAPE/DMS reactivities | probing-restrained folding (Deigan/Zarringhalam) | unrestrained MFE |
| Long mRNA / transcriptome scale | RNAplfold / LinearFold+LinearPartition | global O(n^3) MFE |
| Pseudoknot biology | IPknot/ProbKnot/Knotty + cross-check | RNAfold (cannot) |
| Willing to use DL | MXfold2 (thermodynamics-integrated) | E2Efold/UFold on unseen families |

When competing methods or parameters are in play, verify current behavior against the installed tool's `--help` and the latest docs before trusting a number.

## Getting the structure out and drawing it

Dot-bracket is the default text form; CT and BPSEQ are the interchange formats downstream tools (ProbKnot, IPknot, RNAstructure) read and write. To DRAW a structure, use forna (web), R2DT (template-based standard layouts for known families), or VARNA; RNAfold's own `*_ss.ps` PostScript drawing is exactly what `--noPS` suppresses, so drop `--noPS` when the built-in diagram is wanted. The example renders the base-pair probability dot plot with matplotlib.

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| `AttributeError: module 'RNA' has no attribute 'sequence_shuffle'` | no such ViennaRNA function | use a dinucleotide-preserving shuffle (`ushuffle`, `esl-shuffle -d`) for z-scores |
| `bpp()`/`centroid()`/`MEA()` return empty or garbage | `fc.pf()` not called first | call `fc.pf()` before any ensemble quantity |
| `*_dp.ps` / `*_ss.ps` files appearing in the working directory | RNAfold/RNAalifold write PostScript by default | pass `--noPS` (and run in a scratch dir) |
| Long mRNA gives one improbable global fold | global MFE is meaningless past ~700 nt | use RNAplfold / LinearFold / LinearPartition |
| Predicted structure has a pseudoknot the tool "missed" | RNAfold cannot represent crossing pairs | use IPknot / ProbKnot / Knotty |
| Consensus structure looks confident but is wrong | RNAalifold trusts the alignment; no real covariation | validate with R-scape; check alignment quality |
| `RNAalifold --aln alignment.sto` treated as input flag | `--aln` is an OUTPUT (annotated PostScript) flag | pass the alignment positionally: `RNAalifold alignment.sto` |
| SHAPE-constrained fold barely changes | reactivity vector mis-indexed or zeros where data is missing | vector is 1-indexed (prepend -999); use -999 for no-data, not 0 |

## Related Skills

- structure-probing - Obtain SHAPE/DMS reactivities to constrain folding
- ncrna-search - Classify structured RNAs by family with Infernal/Rfam
- covariation-analysis - Statistically validate a predicted conserved structure with R-scape
- genome-annotation/ncrna-annotation - Genome-wide ncRNA annotation
- small-rna-seq/target-prediction - miRNA-target prediction using accessibility
- sequence-manipulation/sequence-properties - Sequence composition and GC content
- data-visualization/heatmaps-clustering - Rendering the base-pair probability matrix (dot plot)

## References

- McCaskill JS. 1990. The equilibrium partition function and base pair binding probabilities for RNA secondary structure. Biopolymers 29(6-7):1105-1119. doi:10.1002/bip.360290621
- Mathews DH, Sabina J, Zuker M, Turner DH. 1999. Expanded sequence dependence of thermodynamic parameters improves prediction of RNA secondary structure. J Mol Biol 288(5):911-940. doi:10.1006/jmbi.1999.2700
- Ding Y, Chan CY, Lawrence CE. 2005. RNA secondary structure prediction by centroids in a Boltzmann weighted ensemble. RNA 11(8):1157-1166. doi:10.1261/rna.2500605
- Lu ZJ, Gloor JW, Mathews DH. 2009. Improved RNA secondary structure prediction by maximizing expected pair accuracy. RNA 15(10):1805-1813. doi:10.1261/rna.1643609
- Lorenz R, Bernhart SH, Honer zu Siederdissen C, Tafer H, Flamm C, Stadler PF, Hofacker IL. 2011. ViennaRNA Package 2.0. Algorithms Mol Biol 6:26. doi:10.1186/1748-7188-6-26
- Lyngso RB, Pedersen CNS. 2000. RNA pseudoknot prediction in energy-based models. J Comput Biol 7(3-4):409-427. doi:10.1089/106652700750050862
- Sato K, Kato Y, Hamada M, Akutsu T, Asai K. 2011. IPknot: fast and accurate prediction of RNA secondary structures with pseudoknots using integer programming. Bioinformatics 27(13):i85-i93. doi:10.1093/bioinformatics/btr215
- Bellaousov S, Mathews DH. 2010. ProbKnot: fast prediction of RNA secondary structure including pseudoknots. RNA 16(10):1870-1880. doi:10.1261/rna.2125310
- Jabbari H, Wark I, Montemagno C, Will S. 2018. Knotty: efficient and accurate prediction of complex RNA pseudoknot structures. Bioinformatics 34(22):3849-3856. doi:10.1093/bioinformatics/bty420
- Tan Z, Fu Y, Sharma G, Mathews DH. 2017. TurboFold II: RNA structural alignment and secondary structure prediction informed by multiple homologs. Nucleic Acids Res 45(20):11570-11581. doi:10.1093/nar/gkx815
- Huang L, Zhang H, Deng D, Zhao K, Liu K, Hendrix DA, Mathews DH. 2019. LinearFold: linear-time approximate RNA folding by 5'-to-3' dynamic programming and beam search. Bioinformatics 35(14):i295-i304. doi:10.1093/bioinformatics/btz375
- Zhang H, Zhang L, Mathews DH, Huang L. 2020. LinearPartition: linear-time approximation of RNA folding partition function and base-pairing probabilities. Bioinformatics 36(Suppl_1):i258-i267. doi:10.1093/bioinformatics/btaa460
- Hajdin CE, Bellaousov S, Huggins W, Leonard CW, Mathews DH, Weeks KM. 2013. Accurate SHAPE-directed RNA secondary structure modeling, including pseudoknots. Proc Natl Acad Sci USA 110(14):5498-5503. doi:10.1073/pnas.1219988110
- Sato K, Akiyama M, Sakakibara Y. 2021. RNA secondary structure prediction using deep learning with thermodynamic integration (MXfold2). Nat Commun 12:941. doi:10.1038/s41467-021-21194-4
- Szikszai M, Wise M, Datta A, Ward M, Mathews DH. 2022. Deep learning models for RNA secondary structure prediction (probably) do not generalise across families. Bioinformatics 38(16):3892-3899. doi:10.1093/bioinformatics/btac415
- Flamm C, Wielach J, Wolfinger MT, Badelt S, Lorenz R, Hofacker IL. 2022. Caveats to deep learning approaches to RNA secondary structure prediction. Front Bioinform 2:835422. doi:10.3389/fbinf.2022.835422
- Rivas E, Clements J, Eddy SR. 2017. A statistical test for conserved RNA structure shows lack of evidence for structure in lncRNAs. Nat Methods 14(1):45-48. doi:10.1038/nmeth.4066
<!-- END FILE: rna-structure/secondary-structure-prediction/SKILL.md -->

## 子目录：rna-structure/structure-probing

<!-- BEGIN FILE: rna-structure/structure-probing/SKILL.md -->
---
name: bio-rna-structure-structure-probing
description: Processes experimental RNA structure probing data (SHAPE-MaP, DMS-MaPseq) into per-nucleotide reactivity profiles with ShapeMapper2, then uses them as soft restraints on thermodynamic folding. Covers reagent and readout choice (SHAPE vs DMS, mutational-profiling vs RT-stop), the three control samples, per-transcript normalization, the Deigan vs Zarringhalam pseudo-energy models, in-cell versus in-vitro interpretation, and multi-conformation deconvolution. Use when converting probing reads to reactivities; deciding SHAPE versus DMS parameters; judging whether low reactivity means base-paired or protein-bound; or detecting whether an RNA populates more than one structure.
tool_type: cli
primary_tool: ShapeMapper2
---

## Version Compatibility

Reference examples tested with: ShapeMapper2 2.1.5+, ViennaRNA 2.6+, SEISMIC-RNA 0.20+, matplotlib 3.8+, pandas 2.2+, numpy 1.26+

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `<tool> --version` then `<tool> --help` to confirm flags
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Structure Probing

**"Process my SHAPE-MaP experiment to get RNA reactivity profiles"** -> Convert per-nucleotide chemical-modification signal into reactivities, normalize them, then feed them as SOFT restraints into thermodynamic folding.
- CLI: `shapemapper` (ShapeMapper2) for end-to-end SHAPE-MaP / DMS-MaP processing
- CLI: `RNAfold --shape` (ViennaRNA) for reactivity-restrained folding
- CLI: `seismic` (SEISMIC-RNA) for DMS-MaPseq and multi-conformation clustering

## The governing principle: reactivity is flexibility, not pairing, and it is a constraint, not a structure

SHAPE reagents acylate the ribose 2'-OH at a rate set by local nucleotide FLEXIBILITY / conformational dynamics; DMS methylates the Watson-Crick face of A (N1) and C (N3). High reactivity means flexible/accessible, low means constrained. The routine over-interpretation is "low reactivity = base-paired": a nucleotide can be unreactive because it is base-paired OR because it is tertiary-contacted, protein-bound, ligand-occluded, or stacked. Reactivity probes CONSTRAINT, and it cannot by itself distinguish pairing from other protection. Before interpreting any low-reactivity region, rule out the TECHNICAL causes first: a long flat run can be low read depth / no-data or global undermodification, not structure -- check effective depth and confirm low-depth positions are carried as -999, not 0.

Two consequences govern everything below:
- Reactivities are a RESTRAINT on folding, not a structure. They enter as pseudo-free-energy terms that bias the thermodynamic fold and raise accuracy substantially, but they do not yield a structure on their own and cannot disambiguate pairing from other protection.
- A per-position profile is a POPULATION AVERAGE. If the RNA samples more than one structure (riboswitches, dynamic mRNAs), the averaged profile can match no real structure. Detecting and deconvolving multiple conformations requires per-read data (mutational profiling) and clustering (SEISMIC-RNA / DREEM), not a single profile.

## Reagent and readout choices

SHAPE acts on the backbone 2'-OH, so it reports all four bases; DMS reads only A/C by default (G/U carry no Watson-Crick-face signal and must be masked to no-data before folding). Newer DMS-MaPseq protocols recover G(N1)/U(N3) signal for a four-base readout (via mutation-signature filtering plus optimized buffer, not the buffer alone) -- only treat DMS as four-base if the protocol and analysis explicitly enable it; otherwise mask G/U.

| Goal | Reagent | Reads | Note |
|------|---------|-------|------|
| In-vitro, all-base, fast | 1M7 (SHAPE) | A/C/G/U flexibility | default; m/b = 1.8/-0.6 |
| In-cell SHAPE (membrane-permeable) | NAI, NAI-N3, 5NIA, 2A3 | A/C/G/U | NAI-N3 -> icSHAPE click enrichment; 2A3 among the strongest in vivo |
| In-cell, cheap, A/C-resolved | DMS | A(N1)/C(N3) | works in vivo; mask G/U to no-data |
| Tertiary-contact flagging | 1M6/NMIA vs 1M7 (differential SHAPE) | A/C/G/U | report the DIFFERENCE, not absolute |
| Fill G/U coverage | CMCT (G/U), kethoxal (G) | G,U / G | low throughput, rarely MaP-coupled |

Mutational profiling (MaP) vs RT-stop is a fundamental analysis fork, not a detail: in MaP the reverse transcriptase reads THROUGH the adduct (Mn2+/TGIRT/Marathon-RT) and misincorporates, encoding each modification as a point mutation; in RT-stop the adduct truncates the cDNA and the read 5'-end is counted. They need different scoring, and a pipeline tuned for one is wrong for the other.

| Axis | MaP (mutation) | RT-stop (truncation) |
|------|----------------|----------------------|
| Adduct encoded as | misincorporation/deletion | RT drop-off (read 5'-end) |
| Reads/molecule informative | many | one |
| Single-molecule / correlated analysis | yes (per-read mutation strings) | no |
| Tools | ShapeMapper2, SEISMIC-RNA, rf-count -sm 3/4 | rf-count -sm 1/2, icSHAPE, StructureFold |
| Methods | SHAPE-MaP, DMS-MaPseq | Mod-seq, Structure-seq, DMS-seq, icSHAPE |

icSHAPE / Structure-seq / DMS-seq are RT-stop methods; do not push them through a MaP mutation-rate pipeline (ShapeMapper2/SEISMIC).

## ShapeMapper2: the three samples and verified flags

The three sample roles are distinct: MODIFIED is the signal; UNTREATED subtracts background (SNPs, RT errors, intrinsic damage); DENATURED normalizes sequence-dependent reactivity bias (divide modified by denatured when no good no-data reference exists). The untreated control is mandatory; the denatured control improves normalization.

```bash
# ShapeMapper2 is Linux-only; on macOS use Docker/Singularity (see usage-guide).
shapemapper \
    --target target_rna.fa \
    --name my_rna \
    --modified --R1 mod_R1.fastq.gz --R2 mod_R2.fastq.gz \
    --untreated --R1 unmod_R1.fastq.gz --R2 unmod_R2.fastq.gz \
    --out results/ \
    --nproc 8 \
    --min-depth 5000
```

| Option | Effect (verified default) |
|--------|---------------------------|
| `--target` / `--name` | reference FASTA / output basename |
| `--modified` / `--untreated` / `--denatured` | the three samples, each followed by `--R1/--R2` |
| `--amplicon` | primer-trimmed amplicon mode |
| `--min-depth` | minimum effective depth to report a nt (default 5000) |
| `--min-qual-to-count` | minimum basecall quality in a mutation (default 30, not 20) |
| `--max-bg` | max untreated mutation frequency (default 0.05) |
| `--star-aligner` | use STAR instead of Bowtie2 (recommended for long targets) |
| `--nproc` / `--overwrite` | threads / overwrite output |

ShapeMapper2 writes a `results/` tree. The reactivity table is `<name>_<RNA>_profile.txt`; the folder-ready files are SEPARATE: `<name>_<RNA>.shape` (2 columns: position, normalized reactivity; excluded = -999) and `<name>_<RNA>.map` (4 columns: position, normalized reactivity, stderr, base). There is no combined `_map.shape` file.

Key `profile.txt` columns: `Nucleotide` is the POSITION integer (1-based); `Sequence` is the base character; `Reactivity_profile` is raw; `Norm_profile` is after normalization. Fold with `Norm_profile` (or the `.shape`/`.map` file), never the raw `Reactivity_profile` -- the pseudo-energy parameters assume normalized input.

## Normalization: per-transcript, and why raw reactivities are not comparable

Raw reactivity (background-subtracted modified mutation rate) sits on an arbitrary, experiment-specific scale set by reagent dose, RT efficiency, and depth. The standard 2-8% / box-plot normalization excludes outliers (top ~2% as a whisker cap), then scales by the mean of the next most-reactive ~8-10% of nucleotides, so normalized values mostly fall ~0-2 with ~1.0 = average reactivity. This scale factor is PER TRANSCRIPT: raw reactivities from different transcripts or experiments are NOT comparable, so never pool or compare raw reactivities across them. To compare two conditions (e.g. +/- ligand), use delta-SHAPE at matched positions with the per-nt standard errors, not raw subtraction. Low-depth nucleotides must become no-data (-999), not zero.

## Reactivity-restrained folding and the pseudo-energy model

The Deigan model adds a soft pseudo-energy to every nucleotide in a stacked pair: deltaG = m * ln(1 + reactivity) + b. It is a restraint, not a hard constraint -- a nucleotide can still pair against the data if the global fold demands it.

| Situation | Model / ViennaRNA flag | Parameters |
|-----------|------------------------|------------|
| Standard SHAPE (1M7/NAI) | Deigan `--shapeMethod="Dm1.8b-0.6"` | m=1.8, b=-0.6 (Hajdin 2013) |
| Noisy data / probabilistic target | Zarringhalam `--shapeMethod="Z"` | target pairing probability |
| Penalize unpaired only | Washietl `--shapeMethod="W"` | perturbation vector |
| DMS-MaPseq | Deigan-style, A/C only, G/U set to -999 | no DMS-specific standard; commonly reuse 1.8/-0.6, or tune |

The m=1.8, b=-0.6 pair is the Hajdin et al. 2013 standard and the ViennaRNA "Deigan" DEFAULT -- it is NOT Deigan et al. 2009's own values (m=2.6, b=-0.8); cite it correctly. For DMS, apply the restraint ONLY to A/C and set G/U to -999, or the model invents constraints at bases that carry no signal. The folded energy a tool reports after a SHAPE/DMS restraint INCLUDES the pseudo-energy bonus, so it is not comparable to an unrestrained MFE -- judge the result by structure agreement, not by a more-negative energy.

```bash
# Fold directly from the ShapeMapper2 .shape file (already normalized)
RNAfold --shape=results/my_rna_my_rna.shape --shapeMethod="Dm1.8b-0.6" --noPS < target_rna.fa
```

## In-cell vs in-vitro: the occupancy trap

In-vitro (refolded, deproteinized) RNA reports pure thermodynamics; in-cell reports the RNA as it exists, with bound proteins, ligands, and chaperone-remodeled states all altering reactivity. An in-cell PROTECTED nucleotide may be protein-bound or ligand-occluded, not base-paired -- the single biggest in-cell misinterpretation. Cells also actively unfold mRNA: genome-wide in-vivo DMS showed mRNAs are MORE unfolded in vivo than in vitro (Rouskin 2014). The in-cell-minus-in-vitro difference is itself the signal for protein/ligand footprints (Spitale 2015).

| Want | Condition | Reagent | Caveat |
|------|-----------|---------|--------|
| De-novo thermodynamic structure | in-vitro refolded | 1M7 SHAPE / DMS | MFE-like, no proteins |
| Functional in-cell state | in-cell | NAI/2A3/5NIA, DMS | protected != paired (occupancy) |
| Protein/ligand footprint | in-cell vs in-vitro delta | matched reagent | needs both, matched depth |

## Multiple conformations: cluster, do not average

If a profile looks inconsistent with any single structure, the RNA may populate more than one. DREEM (Tomezsko 2020) and its maintained successor SEISMIC-RNA cluster MaP reads by co-occurring mutations (expectation-maximization) to deconvolve coexisting conformers; RING-MaP (Homan 2014) and PAIR-MaP (Mustoe 2019) use correlated mutations between positions to detect through-space communication and direct base pairs. These need per-read mutation data, which only MaP provides.

```bash
# DMS-MaPseq processing and multi-conformation clustering with SEISMIC-RNA
# Subcommand names vary by version (released: align/relate/mask/cluster; recent dev renames
# relate->idmut, mask->filter). Run `seismic --help` to confirm before scripting.
seismic align target.fa reads_R1.fq.gz reads_R2.fq.gz --out seismic_out
seismic relate seismic_out target.fa --out seismic_out
seismic mask seismic_out --out seismic_out
seismic cluster seismic_out --max-clusters 3 --out seismic_out
```

For RNA Framework (rf-count -> rf-norm), the reference is `-f` and the BAM/SAM files are positional; choose the MaP-vs-RT-stop scoring in rf-norm with `-sm` (1 Ding RT-stop, 2 Rouskin RT-stop, 3 Siegfried MaP, 4 Zubradt MaP) and the normalization with `-nm` (1 = 2-8% default, 3 = box-plot); restrict reactive bases for DMS with `-rb AC`.

```bash
rf-count -f reference.fa modified.bam untreated.bam -o rf_out/
rf-norm -i rf_out/index.rci -t rf_out/modified.rc -u rf_out/untreated.rc -sm 3 -nm 1 -rb AC
```

## Quality thresholds

| Metric | Threshold | Rationale |
|--------|-----------|-----------|
| Effective depth | >= 5000 | reliable per-nt mutation-rate estimation for MaP |
| Untreated mutation rate | < 0.5% | overall expectation; higher suggests SNP, RT-prone motif, or damage (individual nt above `--max-bg`=5% are auto-excluded) |
| Modified mutation rate | ~1-10% | too low = undermodified; too high = degraded |
| No-data marker | -999 | low-depth/high-background nt; carry through folding, do not treat as 0 |

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| `KeyError: 'Reactivity_profile'` or garbled sequence | reading base from `Nucleotide` (it is the position integer) | read the base from `Sequence`; fold with `Norm_profile` |
| `FileNotFoundError: my_rna_map.shape` | no combined file is written | use the separate `<name>_<RNA>.shape` (2-col) and `.map` (4-col) |
| Folding barely changes with SHAPE data | folding with raw `Reactivity_profile`, or vector mis-indexed | use `Norm_profile`; vector is 1-indexed (prepend -999), -999 = no data |
| DMS constraints look noisy at G/U | G/U carry no Watson-Crick DMS signal | mask G/U to -999 before folding and before normalization |
| `rf-count -t target.fa -r mod.bam -rc unt.bam` errors | wrong flags | reference is `-f`; BAMs are positional; there is no `-r`/`-rc` |
| Two conditions disagree but raw reactivities were compared | raw values are per-transcript, non-comparable | compare normalized profiles (delta-SHAPE) with standard errors |
| Profile fits no single structure | RNA populates multiple conformations | cluster MaP reads with SEISMIC-RNA / DREEM |
| In-cell protected region called "paired" | protection may be protein/ligand occupancy | compare in-cell vs in-vitro; do not equate protection with pairing |
| A long unreactive stretch read as a stable hairpin | could be low depth/no-data or undermodification, not pairing | check effective depth (>=5000) and that low-depth nt are -999 before interpreting |

## Related Skills

- secondary-structure-prediction - The folding engine the reactivities restrain
- ncrna-search - Identify the RNA family and a CM consensus structure to probe against
- covariation-analysis - Independent (evolutionary) evidence for the pairs probing suggests
- epitranscriptomics/m6a-peak-calling - RNA modifications that confound DMS/SHAPE reactivity
- clip-seq/binding-site-annotation - In-cell protection as an RBP footprint
- read-qc/quality-reports - QC of the underlying sequencing reads

## References

- Merino EJ, Wilkinson KA, Coughlan JL, Weeks KM. 2005. RNA structure analysis at single nucleotide resolution by selective 2'-hydroxyl acylation and primer extension (SHAPE). J Am Chem Soc 127(12):4223-4231. doi:10.1021/ja043822v
- Mortimer SA, Weeks KM. 2007. A fast-acting reagent for accurate analysis of RNA secondary and tertiary structure by SHAPE chemistry. J Am Chem Soc 129(14):4144-4145. doi:10.1021/ja0704028
- Deigan KE, Li TW, Mathews DH, Weeks KM. 2009. Accurate SHAPE-directed RNA structure determination. Proc Natl Acad Sci USA 106(1):97-102. doi:10.1073/pnas.0806929106
- Zarringhalam K, Meyer MM, Dotu I, Chuang JH, Clote P. 2012. Integrating chemical footprinting data into RNA secondary structure prediction. PLoS ONE 7(10):e45160. doi:10.1371/journal.pone.0045160
- Hajdin CE, Bellaousov S, Huggins W, Leonard CW, Mathews DH, Weeks KM. 2013. Accurate SHAPE-directed RNA secondary structure modeling, including pseudoknots. Proc Natl Acad Sci USA 110(14):5498-5503. doi:10.1073/pnas.1219988110
- Cordero P, Kladwang W, VanLang CC, Das R. 2012. Quantitative dimethyl sulfate mapping for automated RNA secondary structure inference. Biochemistry 51(36):7037-7039. doi:10.1021/bi3008802
- Rouskin S, Zubradt M, Washietl S, Kellis M, Weissman JS. 2014. Genome-wide probing of RNA structure reveals active unfolding of mRNA structures in vivo. Nature 505(7485):701-705. doi:10.1038/nature12894
- Homan PJ, Favorov OV, Lavender CA, Kursun O, Ge X, Busan S, Dokholyan NV, Weeks KM. 2014. Single-molecule correlated chemical probing of RNA. Proc Natl Acad Sci USA 111(38):13858-13863. doi:10.1073/pnas.1407306111
- Siegfried NA, Busan S, Rice GM, Nelson JAE, Weeks KM. 2014. RNA motif discovery by SHAPE and mutational profiling (SHAPE-MaP). Nat Methods 11(9):959-965. doi:10.1038/nmeth.3029
- Smola MJ, Rice GM, Busan S, Siegfried NA, Weeks KM. 2015. Selective 2'-hydroxyl acylation analyzed by primer extension and mutational profiling (SHAPE-MaP) for direct, versatile and accurate RNA structure analysis. Nat Protoc 10(11):1643-1669. doi:10.1038/nprot.2015.103
- Spitale RC, Flynn RA, Zhang QC, Crisalli P, Lee B, Jung JW, Kuchelmeister HY, Batista PJ, Torre EA, Kool ET, Chang HY. 2015. Structural imprints in vivo decode RNA regulatory mechanisms. Nature 519(7544):486-490. doi:10.1038/nature14263
- Zubradt M, Gupta P, Persad S, Lambowitz AM, Weissman JS, Rouskin S. 2017. DMS-MaPseq for genome-wide or targeted RNA structure probing in vivo. Nat Methods 14(1):75-82. doi:10.1038/nmeth.4057
- Busan S, Weeks KM. 2018. Accurate detection of chemical modifications in RNA by mutational profiling (MaP) with ShapeMapper 2. RNA 24(2):143-148. doi:10.1261/rna.061945.117
- Incarnato D, Morandi E, Simon LM, Oliviero S. 2018. RNA Framework: an all-in-one toolkit for the analysis of RNA structures and post-transcriptional modifications. Nucleic Acids Res 46(16):e97. doi:10.1093/nar/gky486
- Mustoe AM, Lama NN, Irving PS, Olson SW, Weeks KM. 2019. RNA base-pairing complexity in living cells visualized by correlated chemical probing (PAIR-MaP). Proc Natl Acad Sci USA 116(49):24574-24582. doi:10.1073/pnas.1905491116
- Tomezsko PJ, Corbin VDA, Gupta P, Swaminathan H, Glasgow M, Persad S, Edwards MD, Rouskin S. 2020. Determination of RNA structural diversity and its role in HIV-1 RNA splicing (DREEM). Nature 582(7812):438-442. doi:10.1038/s41586-020-2253-5
<!-- END FILE: rna-structure/structure-probing/SKILL.md -->

<!-- END CATEGORY: rna-structure -->

