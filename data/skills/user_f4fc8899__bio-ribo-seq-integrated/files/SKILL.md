---
slug: bio-ribo-seq-integrated
version: 1.0.0
displayName: "核糖体谱分析 / Ribosome profiling"
name: bio-ribo-seq-integrated
summary: >-
  中文：核糖体谱分析综合技能，整合 6 个相关专题，覆盖核糖体谱分析：Ribo-seq预处理、3nt周期性QC、ORF检测、翻译效率、起始位点映射。 English: Integrated Ribosome profiling skill covering 6 related topics, including Ribosome profiling: Ribo-seq preprocessing, 3nt periodicity QC, ORF detection, translation efficiency, initiation site mapping.
description: >-
  中文：这是一个面向核糖体谱分析的综合生物信息学 Skill，整合当前分类下 6 个相关专题能力。它用于根据研究问题、数据类型和分析阶段，选择合适的方法与工具，规划从输入检查、预处理、核心分析到质量控制、统计解释和结果报告的完整流程。重点覆盖：核糖体谱分析：Ribo-seq预处理、3nt周期性QC、ORF检测、翻译效率、起始位点映射。当用户提供相关实验数据、测序结果、表格或研究问题时，它会帮助判断分析目标与前置条件，给出工具选择、关键参数、输入输出、常见失败原因、结果解读和可复现建议。主要工具包括：Plastid, Ribo-TISH, RiboCode。该 Skill 提供分析设计与实施指导，不替代对具体数据质量、生物学背景和最终结论的人工审查。
  English: This is an integrated bioinformatics Skill for Ribosome profiling, combining 6 related topic areas. It helps users choose appropriate methods and tools based on the research question, data type, and analysis stage, and plan an end-to-end workflow from input validation and preprocessing through core analysis, quality control, statistical interpretation, and reporting. It covers Ribosome profiling: Ribo-seq preprocessing, 3nt periodicity QC, ORF detection, translation efficiency, initiation site mapping. For relevant experimental data, sequencing results, tables, or research questions, it clarifies prerequisites, recommends tools and parameters, describes expected inputs and outputs, explains common failure modes, and supports reproducible analysis. Primary tools include: Plastid, Ribo-TISH, RiboCode. It provides methodological and implementation guidance; final data-quality assessment and biological conclusions still require human review.
---

# ribo-seq 分类 Skill 整合版

> 本文件整合同一主分类目录下 6 个子目录中的 SKILL.md 内容。
> 各子目录正文按原文保留，并通过标题和边界标记进行区分；源文件中的元数据块未被改写。

---

<!-- BEGIN CATEGORY: ribo-seq -->

## 子目录：ribo-seq/initiation-site-mapping

<!-- BEGIN FILE: ribo-seq/initiation-site-mapping/SKILL.md -->
---
name: bio-ribo-seq-initiation-site-mapping
description: Map translation initiation sites, including non-AUG and alternative starts, from initiation-drug ribosome profiling (TI-seq). Use when locating start codons, detecting near-cognate or upstream initiation, or analyzing harringtonine, lactimidomycin (GTI-seq/QTI-seq), or retapamulin (Ribo-RET) data.
tool_type: mixed
primary_tool: Ribo-TISH
---

## Version Compatibility

Reference examples tested with: Ribo-TISH 0.2.7+, PRICE/GEDI 1.0.5+, samtools 1.19+

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `<tool> --version` then `<tool> --help` to confirm flags
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Translation Initiation Site Mapping

**"Map where translation starts in my Ribo-seq data"** -> Locate translation initiation sites (TIS) at single-nucleotide resolution, including non-AUG and upstream starts, from initiation-drug profiling experiments.
- CLI: `Ribo-TISH` for TIS detection from harringtonine/LTM data; `PRICE` for EM-based cryptic-start detection

This is a distinct analysis from elongation ORF detection: it asks WHERE initiation occurs (which start codon), not which ORF bodies are translated. It typically requires a dedicated initiation-drug library paired with a standard elongation library.

## Initiation-drug data types (which experiment produced the data)

| Method | Drug(s) | Signal | Citation |
|--------|---------|--------|----------|
| Harringtonine TIS | harringtonine | binds free 60S, blocks the first peptide bond; broad start peak | Ingolia 2011 |
| GTI-seq | lactimidomycin (LTM) + CHX in parallel | LTM blocks translocation at the assembled 80S; sharp start peak | Lee 2012 |
| QTI-seq | LTM then puromycin (sequential) | puromycin strips elongating ribosomes; quantitative, low background | Gao 2015 |
| Ribo-RET (bacteria) | retapamulin | arrests initiating 70S at start codons | Meydan 2019 |

All three drugs CREATE the initiation signal by halting or removing elongation; the data is a deliberate artifact read out at the start codon. LTM gives sharper peaks than harringtonine because it cannot act on elongating ribosomes whose E-site is occupied. QTI-seq (LTM then puromycin) is analyzed on the same LTM path below; the puromycin step only strips elongating ribosomes to lower the background, so the TIS library is still passed as the LTM-type `-t` input. Without an initiation-drug library, start codons can only be inferred indirectly from elongation periodicity (see orf-detection).

## Near-cognate and alternative starts

Initiation occurs at AUG and near-cognate codons differing by one base; the biologically used set is CUG, GUG, ACG, UUG, AUU, AUC, AUA (AAG/AGG also differ by one base but initiate negligibly). CUG is the dominant near-cognate start (~16% of mapped sites in GTI-seq; AUG remains >50%). uORFs especially use near-cognate starts, so initiation mapping must enable alternative start codons to recover them; an AUG-only search misses most upstream initiation.

## Tool selection

| Situation | Tool | Why |
|-----------|------|-----|
| TIS from harringtonine/LTM data, with QC | Ribo-TISH | quality + predict modes; near-cognate via --alt; differential TIS |
| Cryptic/near-cognate starts, EM model | PRICE | per-codon EM; handles near-cognate; designed for cryptic events |
| Bacterial initiation (Ribo-RET) | dedicated retapamulin analysis | prokaryote initiation; eukaryote periodicity tools fit poorly |

## QC the initiation library

**Goal:** Confirm the drug enriched start-codon signal and pick P-site offsets before predicting.

**Approach:** Run Ribo-TISH quality, which reports the metagene profile and writes a per-length offset parameter file.

```bash
# Writes a <ribo.bam>.para.py offset file and a QC figure
ribotish quality -b ribo_elongation.bam -g annotation.gtf -o ribo_quality.txt -f ribo_qc.pdf
ribotish quality -b ribo_tis.bam -g annotation.gtf -o tis_quality.txt -f tis_qc.pdf
```

## Predict initiation sites with Ribo-TISH

**Goal:** Call TIS, including non-AUG starts, using the initiation-drug library.

**Approach:** Run `ribotish predict` with the elongation BAM (-b) and the TIS/harringtonine/LTM BAM (-t), enabling alternative start codons.

```bash
# --harr marks the TIS library as harringtonine-type; --alt enables near-cognate starts
ribotish predict \
    -b ribo_elongation.bam \
    -t ribo_tis.bam \
    -g annotation.gtf \
    -f genome.fa \
    --harr --harrwidth 15 --alt \
    -o tis_predictions.txt
```

The output lists initiation sites with the start codon, ORF type, and significance. For differential initiation across conditions, `ribotish tisdiff` compares two TIS libraries.

## Alternative: cryptic starts with PRICE

**Goal:** Detect cryptic and near-cognate initiation with an EM model.

**Approach:** Prepare the genome and run the Price tool in GEDI on the Ribo-seq reads.

```bash
gedi -e Price -reads ribo_elongation.bam -genomic prepared_genome -prefix price_out
```

PRICE reports a per-ORF p-value from a generalized binomial model (not multiple-testing corrected); codon-level activity is written to `price_out.codons.cit`.

## Interpreting initiation sites

A called TIS is strongest when it shows a sharp drug-induced start peak, a downstream in-frame elongation signal in the standard library, and (for novel sites) conservation or peptide support. Alternative N-terminal starts and uORF starts frequently use near-cognate codons; report the start codon identity, not just the position. Initiation at a uORF does not guarantee a stable protein product (see orf-detection validation).

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| Only AUG starts found | Alternative starts not enabled | Add `--alt` (Ribo-TISH) or use PRICE for near-cognate |
| Broad, smeared start peaks | Harringtonine data treated as sharp LTM data | Use `--harr`; expect broader peaks than LTM |
| `predict` gives weak calls | Missing the paired elongation BAM (-b) | Provide both -b (elongation) and -t (TIS) libraries |
| TIS analysis on elongation-only data | No initiation-drug library present | Initiation mapping needs harringtonine/LTM/RET data; otherwise infer from periodicity |
| Bacterial data mis-called | Eukaryote TIS tool on Ribo-RET data | Use a retapamulin/prokaryote initiation workflow |

## Related Skills

- orf-detection - Call and validate the ORF bodies downstream of mapped starts
- ribosome-periodicity - Calibrate P-site offsets for both libraries
- riboseq-preprocessing - Align the elongation and initiation-drug libraries
- ribosome-stalling - Initiation drugs are not for elongation pausing

## References

- Ingolia NT, Lareau LF, Weissman JS. 2011. Ribosome profiling of mouse embryonic stem cells reveals the complexity and dynamics of mammalian proteomes. Cell 147(4):789-802. doi:10.1016/j.cell.2011.10.002
- Lee S, Liu B, Lee S, Huang SX, Shen B, Qian SB. 2012. Global mapping of translation initiation sites in mammalian cells at single-nucleotide resolution. Proc Natl Acad Sci USA 109(37):E2424-E2432. doi:10.1073/pnas.1207846109
- Gao X, Wan J, Liu B, Ma M, Shen B, Qian SB. 2015. Quantitative profiling of initiating ribosomes in vivo. Nat Methods 12(2):147-153. doi:10.1038/nmeth.3208
- Zhang P, He D, Xu Y, et al. 2017. Genome-wide identification and differential analysis of translational initiation. Nat Commun 8:1749. doi:10.1038/s41467-017-01981-8
- Erhard F, Halenius A, Zimmermann C, et al. 2018. Improved Ribo-seq enables identification of cryptic translation events. Nat Methods 15(5):363-366. doi:10.1038/nmeth.4631
- Meydan S, Marks J, Klepacki D, et al. 2019. Retapamulin-assisted ribosome profiling reveals the alternative bacterial proteome. Mol Cell 74(3):481-493. doi:10.1016/j.molcel.2019.02.017
<!-- END FILE: ribo-seq/initiation-site-mapping/SKILL.md -->

## 子目录：ribo-seq/orf-detection

<!-- BEGIN FILE: ribo-seq/orf-detection/SKILL.md -->
---
name: bio-ribo-seq-orf-detection
description: Detect and quantify translated ORFs from Ribo-seq using 3-nucleotide periodicity, including uORFs, internal ORFs, dORFs, and novel ORFs. Use when finding actively translated regions beyond annotated CDS, classifying ORFs by the 2022 community standard, quantifying ORF-level translation, or choosing between periodicity-based callers.
tool_type: mixed
primary_tool: RiboCode
---

## Version Compatibility

Reference examples tested with: RiboCode 1.2+, ORFquant 1.0+, ORFik 1.22+, DESeq2 1.42+, pandas 2.2+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# ORF Detection

**"Detect translated ORFs from my Ribo-seq data"** -> Identify actively translated open reading frames (uORFs, internal ORFs, dORFs, novel ORFs) using 3-nucleotide periodicity (not mere coverage) as the evidence of translation, then classify and quantify them.
- CLI: `RiboCode` for periodicity-based de novo ORF calling
- R: `ORFquant` for isoform-aware quantification; `ORFik` as the general toolkit

The discriminating signal is PERIODICITY: a translated ORF shows footprint P-sites in frame 0 (F0 >> F1, F2). Coverage alone is not evidence of translation. Every method needs a correct per-read-length P-site offset first (see ribosome-periodicity).

## ORF-type nomenclature (Mudge 2022 standard)

The GENCODE-led standard (Mudge et al 2022) defines the umbrella term "Ribo-seq ORF" and six positional categories. These are positional, not modification-based (N-terminal extensions are not part of the scheme).

| Category | Definition (transcript-relative) |
|----------|----------------------------------|
| uORF | Entirely within the 5' UTR, not overlapping the CDS |
| uoORF | Upstream-overlapping: starts in 5' UTR, overlaps CDS start out-of-frame |
| intORF | Internal/nested: within the CDS in a different frame |
| dORF | Entirely within the 3' UTR, not overlapping the CDS |
| doORF | Downstream-overlapping: overlaps the CDS stop into the 3' UTR |
| lncRNA-ORF | ORF on a transcript annotated as long non-coding RNA |

Related terms: sORF/smORF (<100 codons, product = microprotein), annotated CDS, novel. Catalogs: sORFs.org, OpenProt.

## Near-cognate start codons (the ATG-only blind spot)

Initiation occurs at AUG and at near-cognate codons differing from AUG by one base; the biologically used set is CUG, GUG, ACG, UUG, AUU, AUC, AUA (AAG/AGG also differ by one base but initiate negligibly). CUG is the dominant near-cognate start (~16% of mapped initiation sites; AUG remains >50%). uORFs ESPECIALLY use near-cognate starts, so an ATG-only scanner misses the majority of real uORFs. Periodicity-based callers can be configured with alternative starts (RiboCode `-A`); the manual finder below is ATG-only and is a teaching toy unless extended.

## Tool selection

| Situation | Tool | Why |
|-----------|------|-----|
| De novo discovery (uORFs, novel ORFs), standard Ribo-seq | RiboCode | Periodicity-based, maintained, supports alternative starts |
| Isoform-aware detection + per-ORF quantification | ORFquant | Resolves ORFs across overlapping isoforms; built on Ribo-seQC |
| General R toolkit (uORF finding, P-site shift, TE, plots) | ORFik | Comprehensive; NOT a dedicated de novo caller |
| Initiation-site / non-AUG mapping (needs harringtonine/LTM) | Ribo-TISH, PRICE | TI-seq-aware (see initiation-site-mapping) |
| Assay-agnostic, no TI-seq, short + long ORFs | ribotricer | Phasing-only, species-calibrated cutoff |
| Bacteria/prokaryotes | DeepRibo, smORFer | Prokaryote-trained (eukaryote periodicity tools fit poorly) |
| Differential ORF translation | P-site counts per ORF then DESeq2 | Count-based DE on ORF-level counts |

ORFik and ORFquant are DISTINCT packages (different authors, repos, methods): ORFik (Tjeldnes 2021, general toolkit) is not the same as ORFquant (Calviello 2020, dedicated isoform-aware caller). Do not install ORFik expecting ORFquant.

## Call ORFs de novo with RiboCode

**Goal:** Identify periodicity-significant ORFs, including uORFs at near-cognate starts.

**Approach:** Prepare transcript annotation, run `metaplots` to select periodic read lengths and their P-site offsets, then run `RiboCode` with optional alternative starts.

```bash
# Step 1: annotation
prepare_transcripts -g annotation.gtf -f genome.fa -o ribocode_annot

# Step 2: metaplots picks periodic read lengths + per-length P-site offsets -> config .txt
#   (read lengths come from THIS step, NOT from a -l flag)
metaplots -a ribocode_annot -r transcriptome.bam -o metaplots_out

# Step 3: call ORFs. -A adds near-cognate starts; -l is the longest-ORF toggle (yes/no)
RiboCode -a ribocode_annot -c metaplots_out_pre_config.txt \
    -A CTG,GTG -l no -p 0.05 -o ribocode_result
```

RiboCode works in transcript coordinates, so the `-r` input is the TRANSCRIPTOME-projected BAM (`Aligned.toTranscriptome.out.bam`), not the genome BAM; a genome BAM silently misbehaves. Its core test is a MODIFIED WILCOXON SIGNED-RANK test on the per-codon P-site frame distribution (a separate binomial file is a secondary output). The `-l` flag toggles longest-ORF selection; it is NOT a read-length list.

## Parse and classify RiboCode output

**Goal:** Split called ORFs by the standard categories.

**Approach:** Read the tabular result and group on the `ORF_type` column, whose RiboCode values are `annotated`, `uORF`, `dORF`, `Overlap_uORF`, `Overlap_dORF`, `Internal`, `novel`.

```python
import pandas as pd

def load_ribocode_orfs(path):
    '''Load the RiboCode result table (<output_name>.txt) and group by ORF_type.'''
    df = pd.read_csv(path, sep='\t')
    groups = {t: df[df['ORF_type'] == t] for t in df['ORF_type'].unique()}
    return df, groups
```

RiboCode writes the result as `<output_name>.txt` (plus a `<output_name>_collapsed.txt`), e.g. `ribocode_result.txt` for `-o ribocode_result`; its columns include `ORF_ID`, `ORF_type`, transcript/genome start-stop, `pval_combined`, and `adjusted_pval`.

## Quantify ORFs isoform-aware with ORFquant

**Goal:** Quantify ORF-level translation while resolving footprints across overlapping isoforms.

**Approach:** Prepare annotation once, feed Ribo-seQC-prepared input, then run the master function.

```r
library(ORFquant)

prepare_annotation_files(annotation_directory = "annot/",
                         twobit_file = "genome.2bit",
                         gtf_file = "annotation.gtf")
# Ribo-seQC writes a for_ORFquant object from the Ribo-seq BAM; pass it here
run_ORFquant(for_ORFquant_file = "sample_for_ORFquant",
             annotation_file = "annot/annotation.gtf_Rannot",
             n_cores = 4)
```

For uORF discovery in a general R workflow, ORFik provides `findUORFs()` and the true P-site shift is `detectRibosomeShifts()` then `shiftFootprints()` (there are no `p_offsets`/`lengths` arguments on `fimport`).

## Manual ORF scan (teaching reference, ATG-only)

**Goal:** Illustrate ORF finding mechanics; not a substitute for a periodicity caller.

**Approach:** Scan three frames for start-to-stop pairs. This finds only ATG starts and uses coverage, not periodicity, so it misses near-cognate uORFs and cannot confirm active translation on its own.

```python
def find_orfs(seq, min_codons=10):
    '''Find ATG-to-stop ORFs in all three frames (ATG-only: a teaching toy).'''
    seq = str(seq).upper()
    stops = {'TAA', 'TAG', 'TGA'}
    orfs = []
    for frame in range(3):
        i = frame
        while i < len(seq) - 2:
            if seq[i:i+3] == 'ATG':
                for j in range(i + 3, len(seq) - 2, 3):
                    if seq[j:j+3] in stops:
                        if (j + 3 - i) >= min_codons * 3:
                            orfs.append({'start': i, 'end': j + 3, 'frame': frame})
                        i = j
                        break
            i += 3
    return orfs
```

## Validate called ORFs

**Goal:** Separate genuine translation from coverage artifacts.

**Approach:** Check the in-frame (frame-0) fraction within the ORF; compare the ORF's footprint read-length distribution to annotated CDS with FLOSS; use ORFscore for frame bias; add PhyloCSF/conservation or mass-spec peptide evidence for novel microproteins.

FLOSS (Ingolia 2014) is half the summed absolute difference between an ORF's footprint length-fraction histogram and the CDS reference; a high-coverage region whose length distribution is non-CDS-like is likely not genuine translation. A called ORF with no frame-0 enrichment, a non-ribosomal FLOSS, and no conservation/peptide support should be treated as a candidate, not a finding.

## Differential ORF translation

**Goal:** Compare ORF-level translation across conditions.

**Approach:** Count offset-corrected P-sites per ORF per sample into an integer matrix, then run DESeq2.

```r
library(DESeq2)
dds <- DESeqDataSetFromMatrix(orf_psite_counts, coldata, ~ condition)
dds <- DESeq(dds)
res <- results(dds)   # adjusted p-value is res$padj
```

Ribosome occupancy is not translation efficiency; a TE change needs an RNA-seq denominator (see translation-efficiency).

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| RiboCode runs but uses wrong read lengths | `-l 27,28,29,30` passed as read lengths | `-l` is the longest-ORF toggle; read lengths come from `metaplots` config |
| KeyError on `ORF_type == 'noncoding'` | Wrong category names | RiboCode emits `Overlap_uORF/Overlap_dORF/Internal/novel`, not `noncoding` |
| `library(ORFik)` cannot find ORFquant functions | ORFik and ORFquant conflated | They are different packages; install ORFquant from its own repo |
| `fimport(p_offsets=, lengths=)` errors | Those arguments do not exist | Use `detectRibosomeShifts()` then `shiftFootprints()` |
| `RibORF.py -f -r -g -o` not found | Fabricated single-command CLI | RibORF is a Perl multi-script pipeline (logistic regression) |
| Most uORFs missing | ATG-only scan | Use a periodicity caller with `-A` near-cognate starts |
| High-coverage "ORF" is not real | Coverage used as the translation signal | Require frame-0 enrichment + FLOSS/ORFscore validation |

## Related Skills

- ribosome-periodicity - Calibrate the per-length P-site offsets ORF callers consume
- initiation-site-mapping - Map start codons (including non-AUG) from harringtonine/LTM data
- translation-efficiency - Add an RNA-seq denominator to turn occupancy into TE
- ribosome-stalling - Interpret pause sites within called ORFs
- differential-expression/deseq2-basics - Differential ORF-level translation

## References

- Mudge JM, Ruiz-Orera J, Prensner JR, et al. 2022. Standardized annotation of translated open reading frames. Nat Biotechnol 40(7):994-999. doi:10.1038/s41587-022-01369-0
- Xiao Z, Huang R, Xing X, Chen Y, Deng H, Yang X. 2018. De novo annotation and characterization of the translatome with ribosome profiling data. Nucleic Acids Res 46(10):e61. doi:10.1093/nar/gky179
- Calviello L, Hirsekorn A, Ohler U. 2020. Quantification of translation uncovers the functions of the alternative transcriptome. Nat Struct Mol Biol 27(8):717-725. doi:10.1038/s41594-020-0450-4
- Tjeldnes H, Labun K, Torres Cleuren Y, Chyżyńska K, Świrski M, Valen E. 2021. ORFik: a comprehensive R toolkit for the analysis of translation. BMC Bioinformatics 22:336. doi:10.1186/s12859-021-04254-w
- Choudhary S, Li W, Smith AD. 2020. Accurate detection of short and long active ORFs using Ribo-seq data. Bioinformatics 36(7):2053-2059. doi:10.1093/bioinformatics/btz878
- Ingolia NT, Brar GA, Stern-Ginossar N, et al. 2014. Ribosome profiling reveals pervasive translation outside of annotated protein-coding genes. Cell Rep 8(5):1365-1379. doi:10.1016/j.celrep.2014.07.045
- Bazzini AA, Johnstone TG, Christiano R, et al. 2014. Identification of small ORFs in vertebrates using ribosome footprinting and evolutionary conservation. EMBO J 33(9):981-993. doi:10.1002/embj.201488411
<!-- END FILE: ribo-seq/orf-detection/SKILL.md -->

## 子目录：ribo-seq/riboseq-preprocessing

<!-- BEGIN FILE: ribo-seq/riboseq-preprocessing/SKILL.md -->
---
name: bio-ribo-seq-riboseq-preprocessing
description: Preprocess ribosome profiling reads with UMI handling, adapter trimming, contaminant/rRNA depletion, and footprint-aware alignment. Use when preparing Ribo-seq FASTQ for periodicity QC, ORF detection, translation efficiency, or stalling analysis, or when deciding how to deduplicate, which aligner to use, or how to size-select ribosome-protected fragments.
tool_type: cli
primary_tool: STAR
---

## Version Compatibility

Reference examples tested with: cutadapt 4.4+, umi_tools 1.1+, STAR 2.7.11+, bowtie2 2.5.3+, SortMeRNA 4.3+, samtools 1.19+

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `<tool> --version` then `<tool> --help` to confirm flags
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Ribo-seq Preprocessing

**"Preprocess my ribosome profiling data"** -> Extract UMIs, trim the 3' linker, deplete rRNA/tRNA contaminants, align footprints with end-to-end (non-soft-clipped) settings, deduplicate only when UMIs allow it, and QC the read-length distribution.
- CLI: `umi_tools extract` -> `cutadapt` -> `bowtie2`/`SortMeRNA` (contaminant removal) -> `STAR` (genome + transcriptome projection) -> `umi_tools dedup` -> `samtools`

The canonical modern order (nf-core/riboseq, McGlincy & Ingolia 2017) is UMI-extract FIRST (the UMI lives in the read and must move to the read name before the linker is cut), then trim, then contaminant removal (before the expensive aligner), then align, then dedup on the BAM.

## Upstream context that changes the analysis (ask before trusting the data)

- **How were cells harvested, and with which drug?** Cycloheximide (CHX) pre-treatment of live cells lets initiation continue while elongation arrests, fabricating start-codon and 5'-ramp density and distorting downstream dwell-time work (Hussmann 2015). Flash-freeze with no drug (or CHX only in the lysis buffer) is the gold standard. Harvest method is recorded at preprocessing because it gates which downstream conclusions are valid (see ribosome-stalling).
- **Which nuclease?** RNase I (eukaryotes) trims close to the ribosome with little sequence bias, giving sharp ~28-30 nt footprints and crisp periodicity. RNase I is inhibited by the E. coli ribosome and FAILS in bacteria, so bacterial protocols use micrococcal nuclease (MNase), which has sequence bias, broader footprints, and forces 3'-end P-site anchoring (Mohammad 2019). A eukaryote-tuned pipeline silently misanalyzes MNase/bacterial data.
- **Are there UMIs?** The dedup decision depends entirely on this (table below).

## The decisions that shape preprocessing

### Deduplication: with-UMI vs without-UMI (the load-bearing choice)

| Situation | What to do | Why |
|-----------|-----------|-----|
| Library has UMIs (McGlincy & Ingolia design or kit) | `umi_tools extract` before trim, `umi_tools dedup` on the BAM (`--method directional`) | UMI separates a true PCR duplicate (same position + length + UMI) from two independent ribosomes on the same codon (same position + length, different UMI) |
| No UMIs | Do NOT position-deduplicate; keep all reads | Many distinct ribosomes give identical 5' position AND identical footprint length; `markdup`/Picard would delete real footprints and flatten high-occupancy codons |
| Low input (single cells, scarce tissue, selective/IP profiling) | UMIs are essential | Few input molecules force heavy PCR; without UMIs amplified-once and amplified-1000x are indistinguishable |

### Alignment: genome (STAR, spliced) vs transcriptome (bowtie2, unspliced)

| Axis | Genome (STAR) | Transcriptome (bowtie2) |
|------|---------------|-------------------------|
| Splicing / novel junctions | Handles introns; required for junction-spanning footprints | Cannot span genomic introns; only annotated transcript cDNA |
| Multimapping | Lower (isoforms collapse to one locus) | High (every shared isoform + paralog multiplies hits) |
| Novel/uORF discovery | Strong (ribotricer/Ribo-TISH work off genome BAM + GTF) | Limited to annotated transcripts |
| P-site / periodicity coords | Project with `--quantMode TranscriptomeSAM` | Native transcript coords (convenient for riboWaltz) |
| Recommended | DEFAULT for mammals: STAR genome + transcriptome projection in one pass | Compact genomes (yeast) or when transcript-coordinate counts are the explicit goal |

### Contaminant removal approach

| Approach | Tool | Tradeoff |
|----------|------|----------|
| Combined-index depletion | bowtie2/STAR vs an rRNA+tRNA+snoRNA+snRNA FASTA, keep unmapped | Fast, full control of the contaminant set; the de-facto standard |
| Dedicated rRNA filter | SortMeRNA v4 (rRNA HMM/k-mer DBs) | rRNA-specialized but covers only rRNA; often paired with a separate ncRNA index |
| Layered (nf-core/riboseq) | BBSplit (broad) then SortMeRNA (rRNA) | Production-grade; most thorough |

rRNA is the dominant contaminant: commonly 50-90% (often >80%) of a Ribo-seq library, because nuclease digestion of the ribosome itself produces abundant rRNA fragments in the footprint size range. Wet-lab depletion (RiboZero/RiboCop/biotinylated subtraction oligos) reduces but never eliminates it, so in-silico removal is mandatory. Effective mRNA depth is a small fraction of raw reads.

## Extract UMIs

**Goal:** Move the UMI from the read sequence into the read name so it survives every later step and can deduplicate the final BAM.

**Approach:** Run `umi_tools extract` FIRST, before adapter trimming, with the barcode pattern matching the library's read structure (N = random UMI base extracted to the name, X = fixed base kept).

```bash
# Only when the library has UMIs. Pattern is library-specific.
# McGlincy & Ingolia 2017 split the 7-nt UMI (5 nt in the linker + 2 nt from circularization)
umi_tools extract \
    --bc-pattern=NNNNN \
    --stdin reads.fastq.gz \
    --stdout reads.umi.fastq.gz \
    --log umi_extract.log
```

When the UMI is split across the read (an inline 5' portion plus a portion inside the 3' linker, as in McGlincy & Ingolia 2017), the linker-embedded part is otherwise lost at trimming: extract it from the 3' end too (a second `umi_tools extract` with a `--3prime` pattern, or cutadapt's `{N}` linker capture) rather than discarding it. A pattern matching only the 5' inline bases recovers half the UMI and under-collapses duplicates.

## Trim the 3' linker

**Goal:** Remove the 3' adapter that is always read through because footprints (~28-30 nt) are far shorter than the read.

**Approach:** Run cutadapt with the known adapter and a PERMISSIVE length floor, and discard reads where no adapter was found.

```bash
# --discard-untrimmed: a footprint without read-through adapter is almost never a real footprint
# -m 15: permissive floor (do NOT narrow to 28-32 yet; inspect the length distribution first)
cutadapt \
    -a CTGTAGGCACCATCAAT \
    --discard-untrimmed \
    -m 15 -M 40 \
    -j 0 \
    -o reads.trimmed.fastq.gz \
    reads.umi.fastq.gz
```

The classic Ingolia linker `CTGTAGGCACCATCAAT` is an example only; the real sequence is protocol/kit-specific and McGlincy-Ingolia linkers embed the UMI and sample barcode, so the trimmed "adapter" region may include them.

## Remove rRNA and other contaminants

**Goal:** Discard rRNA/tRNA/snoRNA reads before the expensive spliced aligner runs.

**Approach:** Align to a combined contaminant index and keep only the unmapped reads, OR use a dedicated rRNA filter.

```bash
# Option A: combined contaminant index (rRNA + tRNA + snoRNA + snRNA), keep unmapped
bowtie2 -x contaminant_index \
    -U reads.trimmed.fastq.gz \
    --un-gz reads.noncontam.fastq.gz \
    -S /dev/null -p 8

# Option B: SortMeRNA v4 (use a per-sample --workdir; a shared kvdb collides across runs)
sortmerna \
    --ref rRNA_db/silva-euk-18s-id95.fasta \
    --ref rRNA_db/silva-euk-28s-id98.fasta \
    --reads reads.trimmed.fastq.gz \
    --aligned rRNA_hits --other reads.noncontam \
    --fastx --workdir sortmerna_sampleA --threads 8
```

## Align footprints (STAR, Ribo-seq-tuned)

**Goal:** Map cleaned footprints with settings appropriate for 28-30 nt reads, preserving the exact ends needed for P-site assignment.

**Approach:** Use STAR end-to-end (no soft-clipping), short-read seeding, a low mismatch cap, and transcriptome projection in one pass.

```bash
# --alignEndsType EndToEnd: the single most important Ribo-seq STAR flag.
#   STAR defaults to Local, which soft-clips footprint ends and corrupts P-site offsets.
# --seedSearchStartLmax 15: STAR's default 50 is wrong for ~30 nt reads.
# Do NOT set --alignIntronMax 1 on a genome (that forbids splicing and defeats STAR).
STAR --runMode alignReads \
    --genomeDir STAR_index \
    --readFilesIn reads.noncontam.fastq.gz \
    --readFilesCommand zcat \
    --alignEndsType EndToEnd \
    --seedSearchStartLmax 15 \
    --outFilterMismatchNmax 2 \
    --outFilterMultimapNmax 10 --outSAMmultNmax 1 --outMultimapperOrder Random \
    --quantMode TranscriptomeSAM GeneCounts \
    --outSAMtype BAM SortedByCoordinate \
    --outFileNamePrefix sampleA_ --runThreadN 8

samtools index sampleA_Aligned.sortedByCoord.out.bam
```

Multimapping is higher in Ribo-seq than RNA-seq (paralogs, ncRNA, repeats). `--outFilterMultimapNmax 1` (unique-only) is simplest but silently drops translated paralogs/repeats; keeping a few multimappers with one random primary, or resolving by EM (RSEM) downstream, retains that signal. STAR's default `--outFilterScoreMinOverLread`/`--outFilterMatchNminOverLread` (0.66) are tuned for ~100 nt reads; very short footprints occasionally need these relaxed if good alignments are rejected.

## Deduplicate (only with UMIs)

**Goal:** Collapse PCR duplicates without destroying genuine co-occupancy.

**Approach:** Run `umi_tools dedup` on the aligned, sorted, indexed BAM; the `directional` method tolerates UMI sequencing errors.

```bash
# Run ONLY if the library has UMIs. Without UMIs, skip this entirely.
umi_tools dedup \
    --stdin sampleA_Aligned.sortedByCoord.out.bam \
    --stdout sampleA.dedup.bam \
    --method directional --log umi_dedup.log
samtools index sampleA.dedup.bam
```

Deduplicate WHICHEVER BAM the downstream step counts on. RiboCode and riboWaltz consume the transcriptome-projected BAM (`Aligned.toTranscriptome.out.bam`), so with UMIs that BAM must be deduplicated too (`umi_tools dedup --per-contig`, because reads sit on transcript "chromosomes"); deduplicating only the genome BAM leaves the ORF/periodicity inputs PCR-inflated. Note also that these blocks assume single-end reads (the Ribo-seq norm); paired-end kits that place the UMI on R2 need a different extract pattern.

## QC the preprocessing

**Goal:** Confirm the library captured real footprints before trusting any downstream analysis.

**Approach:** Plot the read-length distribution, report the contaminant fraction and mapping rate, and (with UMIs) the post-dedup complexity.

```bash
# Read-length distribution is THE key plot: expect a sharp mammalian peak ~28-30 nt,
# sometimes a ~20-22 nt shoulder (the open-A-site footprint population, Lareau 2014).
samtools view sampleA.dedup.bam | awk '{print length($10)}' | sort -n | uniq -c
samtools flagstat sampleA.dedup.bam
```

A permissive trim floor matters here: a tight 28-32 nt gate applied before this plot discards the ~20-22 nt population and hides QC problems. Size-select narrowly only after inspecting the distribution, and prefer per-read-length analysis downstream (riboWaltz, RiboFlow assign per-length P-site offsets).

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| Flat 33/33/33 frame downstream; weak periodicity | Footprint ends soft-clipped by STAR Local mode | Add `--alignEndsType EndToEnd`; never rely on STAR defaults for footprints |
| Junction-spanning footprints all lost | `--alignIntronMax 1` set on a genome alignment | Remove it (or only use it when the "genome" is a transcriptome FASTA) |
| High-occupancy codons look flattened after "dedup" | Position-based dedup on a library WITHOUT UMIs | Do not deduplicate without UMIs; same position + length is mostly real biology |
| SortMeRNA errors on the second sample | Shared default kvdb workdir collides across runs | Give each sample a fresh `--workdir` |
| Very few reads survive trimming | `--discard-untrimmed` plus a wrong adapter sequence | Confirm the actual linker (kit/protocol-specific); inspect a few raw reads |
| Mammalian peak missing, broad smear instead | Over-digestion, wrong size gate too early, or MNase data analyzed as RNase I | Plot length distribution first; for bacteria expect MNase breadth and 3'-anchoring |

## Related Skills

- ribosome-periodicity - Validate 3-nt periodicity and calibrate P-site offsets on the aligned BAM
- orf-detection - Detect translated ORFs once footprints are aligned and offsets known
- translation-efficiency - Needs matched RNA-seq processed consistently with the footprints
- read-qc/quality-reports - General read quality control before footprint-specific steps
- read-alignment/star-alignment - General STAR alignment background

## References

- Ingolia NT, Ghaemmaghami S, Newman JRS, Weissman JS. 2009. Genome-wide analysis in vivo of translation with nucleotide resolution using ribosome profiling. Science 324(5924):218-223. doi:10.1126/science.1168978
- McGlincy NJ, Ingolia NT. 2017. Transcriptome-wide measurement of translation by ribosome profiling. Methods 126:112-129. doi:10.1016/j.ymeth.2017.05.028
- Mohammad F, Green R, Buskirk AR. 2019. A systematically-revised ribosome profiling method for bacteria reveals pauses at single-codon resolution. eLife 8:e42591. doi:10.7554/eLife.42591
- Lareau LF, Hite DH, Hogan GJ, Brown PO. 2014. Distinct stages of the translation elongation cycle revealed by sequencing ribosome-protected mRNA fragments. eLife 3:e01257. doi:10.7554/eLife.01257
- Smith T, Heger A, Sudbery I. 2017. UMI-tools: modeling sequencing errors in Unique Molecular Identifiers to improve quantification accuracy. Genome Res 27(3):491-499. doi:10.1101/gr.209601.116
<!-- END FILE: ribo-seq/riboseq-preprocessing/SKILL.md -->

## 子目录：ribo-seq/ribosome-periodicity

<!-- BEGIN FILE: ribo-seq/ribosome-periodicity/SKILL.md -->
---
name: bio-ribo-seq-ribosome-periodicity
description: Validate Ribo-seq library quality by measuring 3-nucleotide periodicity and calibrating read-length-specific P-site offsets. Use when checking whether footprints capture genuine translation, determining P-site offsets for downstream ORF/TE/stalling analysis, or deciding which read lengths to keep.
tool_type: mixed
primary_tool: riboWaltz
---

## Version Compatibility

Reference examples tested with: riboWaltz 2.0+, plastid 0.6+, numpy 1.26+, scipy 1.12+, pysam 0.22+

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Ribosome Periodicity and P-site Calibration

**"Check if my Ribo-seq data shows triplet periodicity and get my P-site offsets"** -> Confirm footprints carry codon phase (the signature of genuine elongating ribosomes) and compute the read-length-specific offset from the read end to the P-site codon, the prerequisite for every codon-resolution analysis.
- R: `riboWaltz` for P-site offset calibration and per-length periodicity (the de-facto standard)
- Python: `plastid` `metagene` + `psite` CLI scripts as the alternative path

## Why periodicity is the QC gate

An elongating ribosome advances exactly one codon (3 nt) per translocation, so P-site-assigned footprints over a CDS pile up in one reading frame (frame 0 >> frames +1/+2). This sub-codon comb is what distinguishes Ribo-seq from RNA-seq, and a library without it cannot support frame-based ORF calling, TE, or dwell-time work regardless of read depth. Contamination (rRNA/tRNA), degraded RNA, and over-digestion all give phase-free, RNA-seq-like coverage.

## P-site geometry (what is being calibrated)

The ribosome has three tRNA sites: A (aminoacyl, decodes the incoming codon), P (peptidyl, holds the nascent chain), E (exit). Codon position is reported at the P-site, which sits at a fixed OFFSET inside the ~28-30 nt footprint. The offset is the distance from the mapped read end to the first nucleotide of the P-site codon. A-site offset = P-site + 3; E-site = P-site - 3. The A-site is the relevant site for tRNA/decoding effects (see ribosome-stalling).

## The decisions that shape periodicity QC

### P-site offset method

| Method | Map from | Best when | Caveat |
|--------|----------|-----------|--------|
| 5'-end + offset | 5' end | sharp 5' ends, classic RNase I libraries (~+12 for 28 nt) | breaks if the 5' end is ragged/variably trimmed |
| 3'-end + offset | 3' end | variable 5' trimming, sharper 3' end; standard for bacteria/MNase | offset still length-dependent; verify per length |
| auto (riboWaltz) | 5' or 3', chosen per length | default; let the data pick the more consistent end | reports both, decides per read-length population |
| center (plastid) | both ends | very noisy ends | loses sub-codon sharpness |

The canonical ~+12 nt offset for 28-29 nt mammalian footprints is a STARTING expectation, not a constant. Offsets are read-length-specific and dataset-specific and must be calibrated empirically; a fixed lookup table silently misassigns codons.

### Tool choice

| Tool | Language | Role |
|------|----------|------|
| riboWaltz | R | offset calibration + per-length frame % (primary) |
| plastid | Python | `metagene`/`psite` CLI offsets + count vectors |
| Ribo-seQC | R | one-shot HTML QC report (P-site, region, periodicity) |
| ribotricer | Python | phase-score check that is robust to P-site shift |

## Calibrate offsets and frame with riboWaltz

**Goal:** Determine the per-read-length P-site offset and the frame-0 fraction that together certify the library.

**Approach:** Convert BAMs to riboWaltz tables, filter lengths by periodicity, compute offsets with `extremity="auto"`, then read off frame percentages per length.

```r
library(riboWaltz)

annotation <- create_annotation(gtfpath = "annotation.gtf")
reads <- bamtolist(bamfolder = "bams", annotation = annotation)

# Keep only read lengths with strong frame-0 enrichment
# periodicity_threshold is a frame-0 percentage (here 50%); tune per dataset
reads <- length_filter(reads, length_filter_mode = "periodicity",
                       periodicity_threshold = 50)

# extremity="auto" picks the 5' or 3' end giving the most consistent per-length offset;
# the corrected offset refines the temporary one to the local maximum (occupancy correction)
offsets <- psite(reads, flanking = 6, extremity = "auto")
reads_psite <- psite_info(reads, offsets)

# Frame-0 fraction per read length is the primary, defensible periodicity metric
frames_by_length <- frame_psite_length(reads_psite, annotation,
                                       sample = names(reads)[1])
```

## Read off the periodicity metrics

**Goal:** Decide pass/fail and which lengths to retain.

**Approach:** Use the frame-0 fraction as the headline number and the metaheatmap/metaprofile as visual confirmation.

```r
# Pooled frame distribution and the start/stop metaprofile
frames <- frame_psite(reads_psite, annotation, sample = names(reads)[1])
metaprofile_psite(reads_psite, annotation, sample = names(reads)[1],
                  utr5l = 25, cdsl = 40, utr3l = 25)
metaheatmap_psite(reads_psite, annotation, sample = names(reads)[1])
```

Frame-0 fraction rule of thumb: good libraries put roughly >60-70% of in-CDS P-sites in frame 0 (vs the 33% null); ~45-60% is marginal; near-uniform 33/33/33 is uninterpretable at codon level. Report per read length, not just pooled.

If NO read length clears the periodicity threshold (length_filter returns empty), the library is RNA-seq-like and supports only gene-level counting, not codon-resolution ORF/TE/stalling analysis; that is the verdict, not a reason to keep lowering the threshold. Lower it only to inspect the best-available length, not to rescue an aperiodic library.

A bimodal length distribution is expected, not an error: alongside the ~28-30 nt footprint there is a ~21 nt population from ribosomes with an open (empty) A-site (Lareau 2014). Inspect the ~21 nt class per length rather than discarding it as contamination; its phase and offset differ from the long footprints and it carries elongation-state information.

## Alternative: plastid offsets via the CLI

**Goal:** Get per-length offsets without R, using plastid's verified workflow.

**Approach:** Build a start-codon ROI with `metagene generate`, then run the `psite` script, which writes an offsets table and per-length profile plots.

```bash
# CLI-first: there is NO top-level plastid.metagene_analysis() function
metagene generate cds_start --landmark cds_start --annotation_files annotation.gtf
psite cds_start_rois.txt psite_out --min_length 26 --max_length 34 \
    --require_upstream --count_files riboseq.bam
```

```python
# Apply the calibrated offsets in Python
from plastid import BAMGenomeArray, VariableFivePrimeMapFactory, GTF2_TranscriptAssembler

ga = BAMGenomeArray('riboseq.bam')
ga.set_mapping(VariableFivePrimeMapFactory.from_file(open('psite_out_p_offsets.txt')))
transcripts = list(GTF2_TranscriptAssembler('annotation.gtf'))
# Per-transcript P-site counts: vec = transcript.get_counts(ga)
```

## Compute a body-coverage periodicity score

**Goal:** Quantify periodicity strength from the CDS body, not the initiation peak.

**Approach:** Build per-nucleotide P-site coverage along the CDS, trim the start/stop peaks, then take the frame-0 fraction or the spectral power at period 3.

```python
import numpy as np

def body_frame_fraction(psite_coverage, trim_start=45, trim_stop=15):
    '''Frame-0 fraction over CDS-body P-site coverage.

    The start (initiation) and stop (termination) peaks dwarf the body and carry
    their own phase, so they are trimmed (trim in nt; ~15 codons start, ~5 codons stop).
    '''
    body = psite_coverage[trim_start:len(psite_coverage) - trim_stop]
    frames = [body[f::3].sum() for f in range(3)]
    total = sum(frames)
    return frames[0] / total if total else 0.0
```

Running an FFT on the start-codon metagene is the wrong signal: that profile is dominated by a single initiation peak, not sustained codon phase. The spectral test must run on uniform CDS-body P-site coverage; otherwise report the frame-0 fraction directly.

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| `ImportError: cannot import name 'metagene_analysis'` | No such function exists in plastid | Use the `metagene generate` + `psite` CLI, or riboWaltz |
| Periodicity "score" always ~0 or meaningless | FFT run on the start-codon metagene, or frames never populated | Score CDS-body P-site coverage; use frame_psite_length |
| Offset works for one length, breaks others | A single hardcoded offset (e.g. 12) applied to all lengths | Calibrate per read length; A-site = P-site + 3 |
| Strong "periodicity" that is just the start peak | Start/stop codon peaks not trimmed | Trim ~15 codons at start, ~5 at stop before scoring |
| Bacterial library looks aperiodic | MNase data with ragged 5' ends mapped 5'-anchored | Anchor on the 3' end; expect weaker periodicity than RNase I |
| Short/long read lengths dilute the signal | Phase-free length tails kept in the analysis | length_filter mode "periodicity"; analyze per length |

## Related Skills

- riboseq-preprocessing - Produce the aligned BAM and inspect the read-length distribution
- orf-detection - Consumes the per-length P-site offsets to call translated ORFs
- translation-efficiency - Needs correct P-site positioning for CDS footprint counts
- ribosome-stalling - Uses the calibrated A-site offset for codon occupancy

## References

- Lauria F, Tebaldi T, Bernabò P, Groen EJN, Gillingwater TH, Viero G. 2018. riboWaltz: Optimization of ribosome P-site positioning in ribosome profiling data. PLoS Comput Biol 14(8):e1006169. doi:10.1371/journal.pcbi.1006169
- Dunn JG, Weissman JS. 2016. Plastid: nucleotide-resolution analysis of next-generation sequencing and genomics data. BMC Genomics 17(1):958. doi:10.1186/s12864-016-3278-x
- Calviello L, Sydow D, Harnett D, Ohler U. 2019. Ribo-seQC: comprehensive analysis of cytoplasmic and organellar ribosome profiling data. bioRxiv 601468. doi:10.1101/601468
- Ingolia NT, Ghaemmaghami S, Newman JRS, Weissman JS. 2009. Genome-wide analysis in vivo of translation with nucleotide resolution using ribosome profiling. Science 324(5924):218-223. doi:10.1126/science.1168978
- Lareau LF, Hite DH, Hogan GJ, Brown PO. 2014. Distinct stages of the translation elongation cycle revealed by sequencing ribosome-protected mRNA fragments. eLife 3:e01257. doi:10.7554/eLife.01257
<!-- END FILE: ribo-seq/ribosome-periodicity/SKILL.md -->

## 子目录：ribo-seq/ribosome-stalling

<!-- BEGIN FILE: ribo-seq/ribosome-stalling/SKILL.md -->
---
name: bio-ribo-seq-ribosome-stalling
description: Detect ribosome pausing and stalling at codon resolution from Ribo-seq, using local-relative occupancy metrics and A-site assignment. Use when studying elongation dynamics, codon dwell times, pause motifs, or ribosome collisions, and when judging whether a pause is real biology or a cycloheximide artifact.
tool_type: python
primary_tool: Plastid
---

## Version Compatibility

Reference examples tested with: plastid 0.6+, numpy 1.26+, scipy 1.12+, biopython 1.83+, twobitreader 3.1+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Ribosome Stalling Detection

**"Find ribosome pause sites in my data"** -> Detect codon positions where ribosomes dwell longer than the local average, attribute them to A-site decoding or nascent-chain effects, and judge whether the signal is real or a drug artifact.
- Python: `plastid` for A-site codon density, local-relative pause scoring, and motif context

## Read this first: cycloheximide destroys pause signal

A pause is only meaningful when footprint positions reflect in-vivo dwell times. Cycloheximide (CHX) pre-treatment of live cells violates this: arrest is not instantaneous, ribosomes run on after the drug, density redistributes downstream, codon-specific pausing is attenuated, and an artifactual start-codon peak appears. Hussmann 2015 showed CHX data report a WEAK NEGATIVE correlation between codon rate and tRNA abundance while flash-frozen data report a STRONG POSITIVE one -- the drug flips the conclusion. A pause analysis on CHX data largely measures the drug.

Decision rule before any dwell/pause analysis:
- Flash-frozen, no drug (or CHX only in lysis at high concentration) -> codon-resolution dwell-time analysis is valid.
- CHX pre-incubation of live cells -> restrict to qualitative/gene-level statements; do not report codon dwell times or tRNA correlations as biology.
- Harringtonine/lactimidomycin data are for initiation-site mapping, not elongation pausing (see initiation-site-mapping).

## A-site vs P-site: the offset choice changes the biology

The P-site offset (~12 nt from the 5' end for canonical 28-30 nt footprints) must be calibrated per read length, not hardcoded (see ribosome-periodicity). The relevant site depends on the mechanism: tRNA-availability/decoding pauses register at the A-SITE (A-site = P-site + 3), so codon-occupancy and tRNA work assign to the A-site. Nascent-chain effects (polyproline, charge) act at the P-site/exit tunnel and upstream. State which site is used; the peak position relative to A/P/E is itself diagnostic.

## Pause-metric selection

| Metric | Definition | Caveat |
|--------|-----------|--------|
| Per-transcript z-score | (density - gene mean)/gene SD | not the field standard; SD inflated by the peaks sought; arbitrary threshold |
| Pause score | local density / gene-mean density at that position | needs a per-gene coverage floor; the standard local-relative metric |
| Codon occupancy | mean over all instances of a codon of (position density / gene mean) | normalize each gene to its own mean FIRST, then pool; assign to A-site |
| RUST | binarize each position vs the gene mean, average the metafootprint | outlier-robust; resists a few high peaks dominating |
| Disome density | footprints from two stacked ribosomes (~58-62 nt) | the cleanest in-vivo strong-pause readout (Arpat 2020) |

The two normalization rules the naive z-score violates: never z-score across positions of differently-expressed genes (high-expression genes dominate) -- normalize each gene to its own mean first; and require a real per-gene coverage floor (a few hundred in-frame footprints), far above a `sum > 100` cutoff, or per-position metrics are noise.

## Calculate A-site codon density (plastid)

**Goal:** Get a per-codon occupancy vector for each CDS at the A-site.

**Approach:** Map footprints to the A-site offset, fetch the CDS count vector, and reduce each codon to its summed in-frame count.

```python
from plastid import BAMGenomeArray, GTF2_TranscriptAssembler, FivePrimeMapFactory
import numpy as np

def asite_codon_occupancy(bam_path, gtf_path, asite_offset=15):
    '''Per-codon A-site occupancy per CDS. A-site offset = P-site (~12) + 3.

    A single fixed offset is a simplification valid only when one read length
    dominates. For production, calibrate per length (ribosome-periodicity) and
    map with VariableFivePrimeMapFactory.from_file using A-site = P-site + 3.
    '''
    alignments = BAMGenomeArray(bam_path, mapping=FivePrimeMapFactory(offset=asite_offset))
    out = {}
    for tx in GTF2_TranscriptAssembler(gtf_path):
        if tx.cds_start is None:
            continue
        cds = tx.get_cds()
        counts = cds.get_counts(alignments)          # numpy vector over the CDS
        n_codons = len(counts) // 3
        # Sum the 3 positions of each codon into a SCALAR (one value per codon)
        per_codon = np.array([counts[i*3:i*3+3].sum() for i in range(n_codons)])
        out[tx.get_name()] = per_codon
    return out
```

`cds.get_counts(alignments)` is the count method on the SegmentChain; `BAMGenomeArray` has no `count_in_region`/`get_density`. Reducing each codon to a scalar (sum of its three positions) is essential -- storing the whole vector at each codon makes every downstream metric garbage.

## Score pauses with a local-relative metric

**Goal:** Flag codons where occupancy exceeds the gene's own average.

**Approach:** Divide each position by the gene mean (a pause score), require adequate coverage, and threshold.

```python
def pause_scores(per_codon_occupancy, min_total=500, score_threshold=5.0):
    '''Pause score = codon occupancy / gene-mean occupancy (local-relative).

    min_total: per-gene footprint floor; below this, scores are noise.
    score_threshold: fold-over-gene-mean to call a pause (tune per dataset).
    '''
    pauses = []
    for tx, occ in per_codon_occupancy.items():
        if occ.sum() < min_total:
            continue
        mean = occ.mean()
        if mean == 0:
            continue
        scores = occ / mean
        for pos in np.where(scores > score_threshold)[0]:
            pauses.append({'transcript': tx, 'codon': int(pos),
                           'pause_score': float(scores[pos])})
    return pauses
```

## Codon occupancy across genes

**Goal:** Estimate per-codon-type dwell, averaged across the transcriptome.

**Approach:** Normalize each gene to its own mean BEFORE pooling, then average per codon identity (the A-site codon).

Pool mean-of-ratios, not ratio-of-means: a raw average across genes is dominated by highly expressed genes. The per-codon occupancy is then a relative dwell estimate -- and only on no-drug data. The tRNA-availability correlation (codon occupancy vs tRNA adaptation index) is modest, sign- and protocol-dependent, and reflects charged-tRNA levels rather than gene copy number; report the effect size, not a presumed strong negative correlation.

## Known pause mechanisms

| Motif / feature | Mechanism |
|-----------------|-----------|
| Polyproline (PPP, PPG) | Rigid proline geometry stalls peptidyl transfer; rescued by eIF5A (eukaryotes) / EF-P (bacteria) |
| Poly-basic (Lys/Arg runs) | Basic nascent chain drags on the negatively-charged exit tunnel; poly-Lys also involves sliding on A-rich codons |
| Rare/low-tRNA codons | Slow A-site decoding; real but modest, and inflated in CHX data |
| Internal Shine-Dalgarno (bacteria) | Anti-SD base-pairing with 16S rRNA; real but contested (protocol-dependent) |

## Ribosome collisions and disome-seq (the modern readout)

When a ribosome stalls, the trailing ribosome collides into it, forming a disome whose ~58-62 nt footprint maps collision sites transcriptome-wide -- a cleaner in-vivo strong-pause readout than monosome relative density (Arpat 2020; ~10% of ribosomes can be in disomes). The collided-disome interface is the trigger for ribosome quality control: ZNF598 (mammals) / Hel2 (yeast) ubiquitinate small-subunit proteins, recruiting the splitting machinery and no-go decay. A monosome pause that coincides with a disome peak, replicates, and survives in no-drug data is strong evidence of a real, acted-upon stall.

## Extract pause-site sequence context

**Goal:** Find amino-acid motifs enriched at pause sites.

**Approach:** Build the per-transcript CDS sequences from a genome (plastid's `get_sequence` needs a genome, not a SegmentChain), then translate a window centered on the A-site codon of each pause.

```python
from Bio.Seq import Seq
import twobitreader

def cds_sequences_from_genome(gtf_path, twobit_path):
    '''Map transcript name -> spliced CDS nucleotide sequence.'''
    from plastid import GTF2_TranscriptAssembler
    genome = twobitreader.TwoBitFile(twobit_path)   # dict-like {chrom: seq}
    seqs = {}
    for tx in GTF2_TranscriptAssembler(gtf_path):
        if tx.cds_start is None:
            continue
        seqs[tx.get_name()] = tx.get_cds().get_sequence(genome)
    return seqs

def pause_motifs(pauses, cds_sequences, window_codons=5):
    '''Amino-acid context around each pause (centered on the A-site codon).'''
    motifs = []
    for p in pauses:
        seq = cds_sequences.get(p['transcript'])
        if not seq:
            continue
        c = p['codon']
        s, e = max(0, (c - window_codons) * 3), min(len(seq), (c + window_codons + 1) * 3)
        if (e - s) % 3 == 0:
            motifs.append(str(Seq(seq[s:e]).translate()))
    return motifs
```

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| Strong start-codon "pause", odd tRNA correlation | CHX pre-treatment artifacts | Use flash-frozen no-drug data; restrict CHX data to gene-level claims |
| `AttributeError` on `count_in_region`/`get_density` | Not BAMGenomeArray methods | Use `cds.get_counts(alignments)` |
| Every codon occupancy identical | Whole count vector stored per codon | Store a scalar: sum the 3 positions of each codon |
| `TypeError` from `get_sequence` | Passed a SegmentChain, not a genome | Load a genome FASTA/2bit; call `cds.get_sequence(genome)` |
| Pauses dominated by one highly expressed gene | Global z-score / ratio-of-means | Normalize each gene to its own mean first; mean-of-ratios |
| Noisy, irreproducible pauses | Coverage floor too low (sum > 100) | Require a few hundred in-frame footprints per gene |
| tRNA correlation overstated | Assumed strong negative on CHX data | Report effect size; depends on charging and harvest |

## Related Skills

- ribosome-periodicity - Calibrate the A-site offset before scoring occupancy
- orf-detection - Locate the ORFs that pause sites fall within
- initiation-site-mapping - Distinguish initiation drugs from elongation pausing
- translation-efficiency - Gene-level translation context

## References

- Hussmann JA, Patchett S, Johnson A, Sawyer S, Press WH. 2015. Understanding biases in ribosome profiling experiments reveals signatures of translation dynamics in yeast. PLoS Genet 11(12):e1005732. doi:10.1371/journal.pgen.1005732
- Gerashchenko MV, Gladyshev VN. 2014. Translation inhibitors cause abnormalities in ribosome profiling experiments. Nucleic Acids Res 42(17):e134. doi:10.1093/nar/gku671
- O'Connor PBF, Andreev DE, Baranov PV. 2016. Comparative survey of the relative impact of mRNA features on local ribosome profiling read density. Nat Commun 7:12915. doi:10.1038/ncomms12915
- Arpat AB, Liechti A, De Matos M, Dreos R, Janich P, Gatfield D. 2020. Transcriptome-wide sites of collided ribosomes reveal principles of translational pausing. Genome Res 30(7):985-999. doi:10.1101/gr.257741.119
- Charneski CA, Hurst LD. 2013. Positively charged residues are the major determinants of ribosomal velocity. PLoS Biol 11(3):e1001508. doi:10.1371/journal.pbio.1001508
- Schuller AP, Wu CC, Dever TE, Buskirk AR, Green R. 2017. eIF5A functions globally in translation elongation and termination. Mol Cell 66(2):194-205. doi:10.1016/j.molcel.2017.03.003
- Li GW, Oh E, Weissman JS. 2012. The anti-Shine-Dalgarno sequence drives translational pausing and codon choice in bacteria. Nature 484(7395):538-541. doi:10.1038/nature10965
<!-- END FILE: ribo-seq/ribosome-stalling/SKILL.md -->

## 子目录：ribo-seq/translation-efficiency

<!-- BEGIN FILE: ribo-seq/translation-efficiency/SKILL.md -->
---
name: bio-ribo-seq-translation-efficiency
description: Quantify translation efficiency (TE) as ribosome occupancy relative to mRNA abundance and test for differential TE between conditions. Use when separating translational from transcriptional regulation, distinguishing genuine translational control from buffering, or choosing between riborex, Xtail, anota2seq, and DESeq2 interaction models.
tool_type: mixed
primary_tool: riborex
---

## Version Compatibility

Reference examples tested with: riborex 2.4+, xtail 1.1+, anota2seq 1.24+, DESeq2 1.42+, pandas 2.2+

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('<pkg>')` then `?function_name` to verify parameters
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Translation Efficiency

**"Calculate translation efficiency from my Ribo-seq and RNA-seq"** -> Compute footprint density relative to mRNA density per gene and test which genes change translation independently of transcription, distinguishing real translational control from buffering.
- R: `riborex` (DESeq2/edgeR backend), `Xtail`, or `anota2seq` for differential TE
- Python: per-gene TE ratio for ranking/visualization only

TE = RPF density / mRNA density over the SAME region. Both assays must come from matched samples and be counted over the CDS. TE isolates translational regulation and is a relative translation-rate proxy at steady state; occupancy is not protein output.

## The central trap: a ratio is for ranking, not testing

The naive per-gene ratio (TPM_ribo/TPM_rna) is fine for ranking and plots but WRONG for differential testing: it ignores count heteroskedasticity, treating a gene with 5 reads like one with 5000. Differential TE is NOT "compute TE per condition then test the difference" -- it is a CONDITION x ASSAY INTERACTION on raw counts with proper negative-binomial dispersion modeling, where log2FC(TE) = log2FC(RPF) - log2FC(mRNA). The whole differential-TE field exists to do this interaction correctly.

## Mode of regulation: control vs buffering

When both assays move, there are distinct biological modes that a single TE fold-change cannot separate:

| Mode | RPF | mRNA | TE | Meaning |
|------|-----|------|-----|---------|
| mRNA abundance | up | up | ~flat | transcriptional, not translational |
| translation (forwarded) | up | flat | up | genuine translational control -> protein changes |
| buffering | flat | up | down | translation absorbs the mRNA change, protein held constant |

Buffering (a homeostatic mechanism) and genuine translational activation can produce the SAME |log2FC(TE)|. Calling a buffered gene "translationally activated" is a wrong conclusion. Only anota2seq formally names the mode, by regressing translated mRNA on total mRNA (analysis of partial variance).

## Differential-TE tool selection

| Tool | Statistic | Names buffering | Best when |
|------|-----------|-----------------|-----------|
| riborex | wraps DESeq2/edgeR/Voom on a merged interaction design | no | fast drop-in for DESeq2 users |
| Xtail | two pipelines (FC-vs-FC, ratio-vs-ratio), reports the more conservative | partial (won't call a buffered gene a hit) | conservative differential-TE calls + clean plots |
| anota2seq | per-mRNA APV + random variance model | YES | mode-of-regulation biology; the postdoc-grade choice |
| RiboDiff | NB GLM, shared dispersion by default | no | few replicates; CLI pipeline |
| DESeq2 interaction | ~assay+condition+assay:condition, Wald or LRT | no (post-hoc) | full control, custom contrasts, batch terms |

## Quick per-gene TE (ranking screen only)

**Goal:** Rank genes by TE for a quick look, not for inference.

**Approach:** Normalize both assays, take the log2 ratio over the CDS with a pseudocount.

```python
import numpy as np

def log2_te(ribo_cds_tpm, rna_cds_tpm, pseudocount=0.1):
    '''Per-gene log2 TE for ranking/plots. Both inputs counted over the CDS.

    Pseudocount 0.1 TPM avoids log(0) and dampens low-count noise. Not for testing.
    '''
    return np.log2((ribo_cds_tpm + pseudocount) / (rna_cds_tpm + pseudocount))
```

Count BOTH assays over the CDS. Using full-transcript RNA against CDS-only RPF introduces a UTR-length confound (long-UTR genes look low-TE). Exclude the first ~15 and last ~5 codons of the CDS so initiation and termination peaks do not dominate the RPF count.

## Differential TE with riborex

**Goal:** Test differential TE reusing a familiar DE engine.

**Approach:** Pass CDS count matrices and condition vectors; riborex builds the interaction design internally and returns DESeq2-format results.

```r
library(riborex)

# rna_counts / ribo_counts: genes x samples integer CDS counts
res <- riborex(rnaCntTable = rna_counts, riboCntTable = ribo_counts,
               rnaCond = c("ctrl", "ctrl", "treat", "treat"),
               riboCond = c("ctrl", "ctrl", "treat", "treat"),
               engine = "DESeq2")
sig <- res[which(res$padj < 0.05), ]   # log2FoldChange is the TE change
```

Engines are `"DESeq2"` (default), `"edgeR"`, `"edgeRD"`, `"Voom"` (Voom is single-factor only).

## Differential TE with anota2seq (names the mode)

**Goal:** Separate translation, buffering, and mRNA-abundance regulation.

**Approach:** Provide translated (RPF) and total (RNA) matrices, run the pipeline, then classify each gene's mode.

```r
library(anota2seq)

ads <- anota2seqDataSetFromMatrix(dataP = ribo_counts, dataT = rna_counts,
                                  phenoVec = c("ctrl", "ctrl", "treat", "treat"),
                                  dataType = "RNAseq", normalize = TRUE)
ads <- anota2seqRun(ads, useRVM = TRUE)
ads <- anota2seqRegModes(ads)   # one mode per gene: translation > abundance > buffering
translation_hits <- anota2seqGetOutput(ads, analysis = "translation",
                                       output = "selected", selContrast = 1)
```

## Differential TE with a DESeq2 interaction

**Goal:** Full control over the interaction model.

**Approach:** Merge RPF and RNA counts, fit the interaction, and select the interaction coefficient by name from `resultsNames` (never hardcode it).

```r
library(DESeq2)
counts <- cbind(ribo_counts, rna_counts)
coldata <- data.frame(
    condition = factor(rep(c("ctrl", "ctrl", "treat", "treat"), 2)),
    assay = factor(rep(c("ribo", "rna"), each = 4)))
dds <- DESeqDataSetFromMatrix(counts, coldata, ~ assay + condition + assay:condition)
dds <- DESeq(dds)

# The interaction name is auto-generated from factor levels; pick it programmatically.
# DESeq2 renders interaction coefficients with a DOT (e.g. assayrna.conditiontreat),
# while main effects use underscores -- so match the dot, not the formula's colon.
nm <- grep("\\.", resultsNames(dds), value = TRUE)
res_te <- results(dds, name = nm)
```

Size factors are estimated PER ASSAY (ribo among ribo, RNA among RNA); the implicit assumption is that the median gene's TE is unchanged. If a global translational shift is expected (e.g. mTOR inhibition), median normalization is violated and spike-ins are needed to anchor absolute scale.

## Confounders to check

mRNA isoform switching changes the CDS/UTR counting region between conditions; UTR changes that alter uORF usage can make a main-ORF TE change SECONDARY to uORF regulation rather than direct translational control. Cross-check called ORFs and uORFs (see orf-detection) before attributing a TE shift to the main ORF.

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| Low-count genes dominate the hit list | t-test/ratio on log-TE | Use count-based GLM (riborex/Xtail/anota2seq/DESeq2) |
| Long-UTR genes systematically low TE | RNA counted over full transcript, RPF over CDS | Count both over the CDS |
| `results(dds, name='conditiontreat.assayribo')` errors | Hardcoded interaction name | Select from `resultsNames(dds)` by the "." term (interaction coefficients render with a dot, not the formula's colon) |
| Unstable dispersion or anota2seq RVM warnings | Too few replicates (n=2 as in the examples) | Use >=3 replicates per condition per assay; n=2 is illustrative only |
| Buffered gene reported as translationally activated | Single TE fold-change cannot separate modes | Use anota2seq mode-of-regulation |
| TE shifts vanish or invert globally | Global translational change breaks median normalization | Add spike-ins; do not assume median TE unchanged |
| Initiation peak inflates RPF counts | Whole-CDS counting including start/stop peaks | Trim first ~15 / last ~5 codons |

## Related Skills

- ribosome-periodicity - Calibrate P-site offsets for CDS footprint counts
- orf-detection - Rule out uORF-driven (secondary) TE changes
- rna-quantification/featurecounts-counting - Generate matched RNA-seq CDS counts
- differential-expression/deseq2-basics - Count-based DE foundations

## References

- Li W, Wang W, Uren PJ, Penalva LOF, Smith AD. 2017. Riborex: fast and flexible identification of differential translation from Ribo-seq data. Bioinformatics 33(11):1735-1737. doi:10.1093/bioinformatics/btx047
- Xiao Z, Zou Q, Liu Y, Yang X. 2016. Genome-wide assessment of differential translations with ribosome profiling data. Nat Commun 7:11194. doi:10.1038/ncomms11194
- Oertlin C, Lorent J, Murie C, Furic L, Topisirovic I, Larsson O. 2019. Generally applicable transcriptome-wide analysis of translation using anota2seq. Nucleic Acids Res 47(12):e70. doi:10.1093/nar/gkz223
- Zhong Y, Karaletsos T, Drewe P, et al. 2017. RiboDiff: detecting changes of mRNA translation efficiency from ribosome footprints. Bioinformatics 33(1):139-141. doi:10.1093/bioinformatics/btw585
- Love MI, Huber W, Anders S. 2014. Moderated estimation of fold change and dispersion for RNA-seq data with DESeq2. Genome Biol 15(12):550. doi:10.1186/s13059-014-0550-8
<!-- END FILE: ribo-seq/translation-efficiency/SKILL.md -->

<!-- END CATEGORY: ribo-seq -->

