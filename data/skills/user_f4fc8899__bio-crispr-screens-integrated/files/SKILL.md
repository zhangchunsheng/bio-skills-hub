---
slug: bio-crispr-screens-integrated
version: 1.0.1
displayName: "CRISPR筛选 / CRISPR screen analysis"
name: bio-crispr-screens-integrated
summary: "中文：CRISPR筛选综合技能，整合 15 个相关专题，覆盖CRISPR筛选分析：库设计、QC、命中基因调用（MAGeCK/BAGEL2/drugZ/JACKS）、Perturb-seq。 English: Integrated CRISPR screen analysis skill covering 15 related topics, including CRISPR screen analysis: library design, QC, hit calling (MAGeCK/BAGEL2/drugZ/JACKS), copy-number correction, Perturb-seq."
description: "中文：这是一个面向CRISPR筛选的综合生物信息学 Skill，整合当前分类下 15 个相关专题能力。它用于根据研究问题、数据类型和分析阶段，选择合适的方法与工具，规划从输入检查、预处理、核心分析到质量控制、统计解释和结果报告的完整流程。重点覆盖：CRISPR筛选分析：库设计、QC、命中基因调用（MAGeCK/BAGEL2/drugZ/JACKS）、Perturb-seq。当用户提供相关实验数据、测序结果、表格或研究问题时，它会帮助判断分析目标与前置条件，给出工具选择、关键参数、输入输出、常见失败原因、结果解读和可复现建议。主要工具包括：BAGEL2, CRISPOR, CRISPRcleanR。该 Skill 提供分析设计与实施指导，不替代对具体数据质量、生物学背景和最终结论的人工审查。 English: This is an integrated bioinformatics Skill for CRISPR screen analysis, combining 15 related topic areas. It helps users choose appropriate methods and tools based on the research question, data type, and analysis stage, and plan an end-to-end workflow from input validation and preprocessing through core analysis, quality control, statistical interpretation, and reporting. It covers CRISPR screen analysis: library design, QC, hit calling (MAGeCK/BAGEL2/drugZ/JACKS), copy-number correction, Perturb-seq. For relevant experimental data, sequencing results, tables, or research questions, it clarifies prerequisites, recommends tools and parameters, describes expected inputs and outputs, explains common failure modes, and supports reproducible analysis. Primary tools include: BAGEL2, CRISPOR, CRISPRcleanR. It provides methodological and implementation guidance; final data-quality assessment and biological conclusions still require human review."
---

# crispr-screens 分类 Skill 整合版

> 本文件整合同一主分类目录下 15 个子目录中的 SKILL.md 内容。
> 各子目录正文按原文保留，并通过标题和边界标记进行区分；源文件中的元数据块未被改写。

---

<!-- BEGIN CATEGORY: crispr-screens -->

## 子目录：crispr-screens/bagel-essentiality

<!-- BEGIN FILE: crispr-screens/bagel-essentiality/SKILL.md -->
---
name: bio-crispr-screens-bagel-essentiality
description: Identifies essential genes from CRISPR-Cas9 fitness screens using BAGEL2 (Kim & Hart 2021 Genome Med), a Bayesian classifier scoring per-gene Bayes Factors via log-likelihood ratios over per-sgRNA fold changes, calibrated against CEGv2 core-essentials (Hart 2017 G3, ~684 genes) and NEGv1 non-essentials (Hart 2014, ~927 genes). Covers the fc + bf + pr workflow, the linear-extrapolation improvement over BAGEL1 truncation, multi-target off-target correction, tumor-suppressor sensitivity (BAGEL2 detects enrichment), and BF calibration (BF >6 ≈ 90% posterior per Hart 2017; ~5% FDR by BAGEL convention). Use when classifying essential vs non-essential genes, calibrating BAGEL2 thresholds against PR curves, identifying tumor suppressors alongside essentials, comparing BAGEL2 hits to MAGeCK / drugZ, or generating publication-quality essentiality calls.
tool_type: cli
primary_tool: BAGEL2
---

## Version Compatibility

Reference examples tested with: BAGEL2 2.0 (hart-lab/bagel, build 115), pandas 2.2+, numpy 1.26+, scipy 1.12+, matplotlib 3.8+.

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `BAGEL.py fc --help`; `BAGEL.py bf --help`; `BAGEL.py pr --help`
- Python: BAGEL2 is distributed via `git clone` (no canonical PyPI release); confirm `BAGEL.py version` after checkout.

If code throws ImportError, AttributeError, or TypeError, introspect the installed package and adapt the example to match the actual API rather than retrying.

## BAGEL2 Essentiality Analysis

**"Identify essential genes from my CRISPR fitness screen using BAGEL2"** -> Compute per-sgRNA fold changes from counts, derive per-gene log-likelihood ratios against reference essential and non-essential gene sets, sum to Bayes Factor, and apply BF threshold calibrated by precision-recall against the reference.

- CLI: `BAGEL.py fc` to compute fold changes
- CLI: `BAGEL.py bf` to compute Bayes Factors
- CLI: `BAGEL.py pr` for precision-recall curves
- Reference sets: CEGv2 (essentials) and NEGv1 (non-essentials); both at https://github.com/hart-lab/bagel

## The BAGEL2 Bayesian Framework (under the hood)

**Why this matters for postdoc-level use:** BAGEL2 uses a Bayes-factor classifier trained on known essential and non-essential genes. The chain:

1. For each sgRNA, compute log-fold-change (LFC) treatment vs control.
2. For each gene, look up per-sgRNA LFCs.
3. For each sgRNA, compute the log-likelihood ratio: `log( P(LFC | gene is essential) / P(LFC | gene is non-essential) )`. The numerator and denominator are KDEs (kernel density estimates) of LFC distributions from CEGv2 and NEGv1 reference sgRNAs.
4. Sum per-gene log-likelihood ratios across all sgRNAs targeting the gene -> per-gene Bayes Factor.
5. Resampling for the confidence interval (default: 10-fold cross-validation; `-b` switches to bootstrapping with `-NB`, default 1000); BF >6 corresponds to ~90% posterior probability (Hart 2017 G3); ~5% FDR by BAGEL convention.

**Critical BAGEL2 improvements over BAGEL1:**

- **Linear extrapolation**: BAGEL1 truncated the LLR at the edges of its KDE; BAGEL2 fits a linear regression in the stable region and extrapolates, giving wider dynamic range. This recovers tumor suppressors (highly positive LFC) that BAGEL1 missed.
- **Multi-target correction**: For sgRNAs targeting multiple genomic loci (off-targets), BAGEL2 discards them and regresses out their BF contribution, but only when `-m/--filter-multi-target` is given together with `--align-info`. The original BAGEL counted off-target hits as essentiality signal.
- **Tumor suppressor sensitivity**: BAGEL2 correctly identifies positive selection (enrichment) genes -- not possible in BAGEL1.

## Calibration to CEGv2 / NEGv1

**Why these reference sets matter:** BAGEL2's discriminative power depends on KDEs of LFCs from known essential vs known non-essential genes. CEGv2 (Hart 2017) is 684 core essential genes shared across cell lines; NEGv1 (Hart 2014) is 927 non-essential genes verified across multiple screens. These act as positive and negative controls within every screen.

Reference set integrity:
- CEGv2: pan-cancer essentials -- common dropouts across most cancer cell lines
- NEGv1: confidently non-essential -- genes without expression or genes with verified neutral status

**Critical pitfall:** Using a custom essentiality reference (e.g., a single-cell-line CRISPR screen) instead of CEGv2 biases the BAGEL2 model toward that line's specific biology. Always use the standardized references unless there is a specific reason for custom training.

## Compute Per-Sample Fold Changes

**Goal:** Generate per-sgRNA fold-change matrix as input for Bayes-factor calculation.

**Approach:** Take normalized counts, compute log-fold-change vs a control (Day 0 or plasmid baseline) per sgRNA.

```bash
# BAGEL2 installation: distributed via git clone (no canonical PyPI release).
git clone https://github.com/hart-lab/bagel
cd bagel

# Inputs:
# counts.txt: tab-separated with columns: sgRNA, GENE, Sample1, Sample2, ...
# Control column(s): typically Day 0 or plasmid sample(s)
# Treatment column(s): screen endpoint

BAGEL.py fc \
    -i counts.txt \
    -o foldchange \                        # NOTE: -o is a LABEL for fc; writes foldchange.foldchange
    -c Plasmid \                           # control sample (or Day 0)
    --min-reads 30                         # default is 0; 30 is a common convention
# Output: foldchange.foldchange (per-sgRNA LFCs) and foldchange.normed_readcount
```

## Compute Bayes Factors

**Goal:** Score per-gene essentiality as a Bayes Factor.

**Approach:** Run `BAGEL.py bf` with the fold-change matrix and reference gene sets. Resampling defaults to 10-fold cross-validation; add `-b -NB N` to bootstrap instead.

```bash
BAGEL.py bf \
    -i foldchange.foldchange \
    -o bayes_factor.txt \
    -e CEGv2.txt \                         # essentials reference (CEGv2)
    -n NEGv1.txt \                          # non-essentials reference
    -c Sample1,Sample2,Sample3 \            # treatment samples to score
    -b -NB 1000                            # opt into bootstrapping (default is 10-fold cross-validation)
# Output: bayes_factor.txt - per-gene Bayes Factor + CI
```

**Output columns:**

| Column | Meaning |
|--------|---------|
| `GENE` | Gene symbol |
| `BF` | Per-gene Bayes Factor (log-likelihood ratio summed across sgRNAs) |
| `STD` | Standard deviation across the 10 cross-validation folds (or bootstrap iterations with `-b`) |
| `NumObs` | Number of sgRNAs contributing |

**Interpretation rule:** BF >6 corresponds to ~90% posterior probability of essentiality against CEGv2 (Hart 2017; FDR ≤3% in that calibration, with ~5% a looser BAGEL convention); higher BF = stronger evidence the gene is essential. BAGEL2 also reports negative BFs which can indicate tumor suppressors (positive selection).

## Precision-Recall Curve

**Goal:** Empirically select BF threshold for a given precision/recall tradeoff.

**Approach:** Run `BAGEL.py pr` to compute precision and recall at every BF level against CEGv2; pick the BF that gives desired precision.

```bash
BAGEL.py pr \
    -i bayes_factor.txt \
    -o precision_recall.txt \
    -e CEGv2.txt \
    -n NEGv1.txt
# Output: precision_recall.txt - precision/recall at each BF threshold
```

**Practical BF ladder (regenerate precision and recall per screen with `BAGEL.py pr`):**

| BF threshold | Use case |
|--------------|----------|
| 0 | Exploratory; highest recall |
| 6 | Standard call (~90% posterior, Hart 2017) |
| 12 | High-confidence |
| 30 | Ultra-stringent; near-certain essentials |

**Pick threshold based on application:** For exploratory hit calling, BF >0 with low precision is acceptable; for clinical-grade essentiality calls, BF >12 or higher.

## Interpret BAGEL2 Results

**Goal:** Stratify genes into essential, non-essential, and tumor-suppressor categories.

**Approach:** Apply BF threshold to classify; flag negative BF as candidate tumor suppressors.

```python
import pandas as pd

def interpret_bagel(bf_path, bf_essential=6, bf_tumor_suppressor=-6):
    '''Classify genes from BAGEL2 BF output.'''
    df = pd.read_csv(bf_path, sep='\t')
    df['call'] = 'neutral'
    df.loc[df['BF'] > bf_essential, 'call'] = 'essential'
    df.loc[df['BF'] < bf_tumor_suppressor, 'call'] = 'tumor_suppressor'
    return df.sort_values('BF', ascending=False)
```

**Tumor suppressor identification:** Genes with significantly negative BF (e.g., <-6) are enriched in the screen, indicating fitness advantage from their loss. This is biologically distinct from "non-essential" and may indicate tumor-suppressor function. BAGEL1 could not detect this; BAGEL2's linear extrapolation enables it.

## Bayesian Reasoning Per Sgrna

**Why this matters:** BAGEL2 computes per-sgRNA contributions; a gene with 4 sgRNAs each contributing +5 to BF gets +20 total. A gene with 3 sgRNAs contributing +5 and 1 sgRNA contributing -3 (off-target or low-efficacy) gets +12 net.

```python
# Per-sgRNA contributions for diagnosis
# Output table: each sgRNA's LLR contribution to gene-level BF
# Useful for identifying low-efficacy guides
```

**Critical:** When per-sgRNA contributions are very heterogeneous (one sgRNA dominates BF), the gene is "guide-of-one"; verify with JACKS efficiency analysis or apply the second-best-sgRNA rule from [[hit-calling]].

## Comparing BAGEL2, MAGeCK, drugZ

| Property | BAGEL2 | MAGeCK | drugZ |
|----------|--------|--------|-------|
| Statistical framework | Bayes factor with reference sets | NB GLM | Bidirectional Z-score |
| Calibrated against | CEGv2 / NEGv1 | Internal null | Vehicle distribution |
| Tumor suppressor detection | YES | Limited (RRA positive-selection score) | YES |
| Best for | Essentiality classification | General hit calling | Chemogenomic drug screens |
| Output | Bayes factor + CI | FDR + LFC | Z-score + FDR per direction |
| Hit threshold | BF >6 | FDR <0.05 | FDR <0.05 |
| Library calibration | Indirect (reference set) | None | None |

**Reconciliation:** BF >6 ≈ 90% posterior probability (Hart 2017 G3); commonly treated as roughly MAGeCK FDR 0.05 by convention. BAGEL2 hits absent from MAGeCK suggest weak signal that BAGEL2's reference anchoring detects but MAGeCK's null-based test misses; verify by inspecting per-sgRNA contributions.

## Failure Modes

### BAGEL2 returns no hits despite known essentials

**Trigger:** Wrong reference gene set file; CEGv2 or NEGv1 file may have wrong format or be missing genes.
**Mechanism:** BAGEL2 trains KDEs on the reference; if references are not representative, KDE separation is poor and no gene has BF >6.
**Symptom:** Median BF near zero; no genes >6 even at low FDR.
**Fix:** Re-download CEGv2 / NEGv1 from https://github.com/hart-lab/bagel. Verify gene symbols match the screen's annotation.

### BAGEL2 calls negative-LFC genes "tumor suppressors"

**Trigger:** Heavy dropout screen where many genes drop out; the dropout signal is captured as positive BF but the *enriched* genes (negative BF) are noise.
**Mechanism:** BAGEL2's symmetric distribution treats deeply enriched genes as significant; in a dropout-only screen, the enrichment signal is purely noise.
**Symptom:** Many genes with negative BF; these don't validate as tumor suppressors.
**Fix:** Restrict tumor-suppressor calling to screens specifically expecting enrichment (e.g., drug-resistance, GoF screens); for dropout screens, only interpret positive BF.

### Bootstrap CI is wide; BF estimates unstable

**Trigger:** Per-gene number of sgRNAs too low (e.g., <4 in some libraries).
**Mechanism:** Bootstrap of LLR over very few sgRNAs creates wide CI.
**Symptom:** STD column larger than BF; many genes have CI spanning zero.
**Fix:** Use a library with at least 4-6 sgRNAs/gene; or switch to bootstrapping (`-b -NB 5000`); or filter out genes with <3 sgRNAs.

### Low BF for known essential despite high LFC

**Trigger:** One sgRNA per gene is contributing very low LLR (off-target or low-efficacy).
**Mechanism:** BAGEL2 sums LLR; one weak guide drags total down.
**Symptom:** Known essential like RPS3 has BF <6 despite 3 of 4 guides showing -5 LFC.
**Fix:** Inspect per-sgRNA LLR; identify the dragging guide; verify whether to exclude or to use JACKS for efficacy-aware analysis.

### Non-cancer cell-line screen with custom essentials

**Trigger:** Human embryonic kidney HEK293T or iPSC-derived neurons where standard essentials may not be essential.
**Mechanism:** CEGv2 is calibrated for cancer cell lines; some essentials in tumor cells are not essential in iPSC.
**Symptom:** PR curve against CEGv2 shows poor separation; many CEGv2 essentials don't drop out.
**Fix:** Use a cell-type-specific essentialome derived for the relevant lineage; or use MAGeCK / Chronos which doesn't depend on reference sets.

## Quantitative Thresholds

| Threshold | Value | Source / Rationale |
|-----------|-------|--------------------|
| Standard essentiality call | BF >6 | Hart 2017: BF>=6 ~ 90% posterior |
| Stricter essentiality call | BF >12 | BAGEL convention; regenerate precision/recall per screen with `BAGEL.py pr` |
| Ultra-stringent call | BF >30 | BAGEL convention |
| BF for tumor-suppressor candidate | <-6 | Empirical; verify with orthogonal screen |
| Resampling | 10-fold cross-validation (default); `-b -NB 1000` to bootstrap | BAGEL2 default |
| Min reads per sgRNA in control | 30 | Convention; the BAGEL2 default is 0 |
| Min sgRNAs per gene for stable BF | 4-6 | Wider with library convention |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| No hits despite essentials present | Wrong reference set | Re-verify CEGv2 / NEGv1 files |
| Wide resampling CI | Too few sgRNAs/gene | Increase library coverage; bootstrap with more iterations |
| Negative BF for known essentials | Confounding factor (e.g., CN amplification) | Pre-correct with CRISPRcleanR / Chronos |
| Tumor suppressor calls don't validate | Pure dropout screen; enrichment is noise | Restrict tumor suppressor calls to expected design |
| Per-sgRNA LLR dominated by one guide | Outlier or off-target | Apply second-best-sgRNA rule |

## References

- Kim E & Hart T. 2021. *Genome Medicine* 13:2. BAGEL2 algorithm and improvements.
- Hart T & Moffat J. 2016. *BMC Bioinformatics* 17:164. BAGEL Bayes factor framework.
- Hart T et al. 2017. *G3* 7:2719. CEGv2 core-essential reference set; BF posterior calibration.
- Hart T et al. 2014. *Mol Syst Biol* 10:733. Gold-standard essential and non-essential reference sets; source of NEGv1.
- Pacini C et al. 2021. *Nat Commun* 12:1661. Integrated cross-study dependencies; reference essentiality benchmarks.

## Related Skills

- crispr-screens/mageck-analysis - MAGeCK RRA/MLE alternative
- crispr-screens/jacks-analysis - JACKS for per-guide efficacy
- crispr-screens/drugz-chemogenomic - drugZ for drug screens
- crispr-screens/hit-calling - Cross-method decision tree
- crispr-screens/screen-qc - Pre-BAGEL QC including CEGv2 PR-AUC
- crispr-screens/library-design - 4-6 sgRNAs/gene library standard
- crispr-screens/copy-number-correction - Pre-correction for cancer-line screens
- pathway-analysis/go-enrichment - Downstream functional analysis
<!-- END FILE: crispr-screens/bagel-essentiality/SKILL.md -->

## 子目录：crispr-screens/base-editing-analysis

<!-- BEGIN FILE: crispr-screens/base-editing-analysis/SKILL.md -->
---
name: bio-crispr-screens-base-editing-analysis
description: Analyzes base-editing screens for variant function. Covers library design (Hanna 2021 ClinVar-scale CBE screen benchmarked on BRCA1/2, Cuella-Martin 2021 DDR saturation), CBE vs ABE chemistry choice (BE3/BE4 vs ABE7.10/ABE8.20/ABE8e), editing-window math (positions 4-8 from PAM-distal end; 4-7 for ABE7.10), bystander-edit quantification and the variant-call ambiguity it creates, sgRNA-efficiency filtering before hit calling, indel byproduct interpretation, the substitution-vs-indel diagnostic, variant annotation against ClinVar / COSMIC, and the Broad be-validation-pipeline. Use when designing a BE variant screen, choosing CBE vs ABE for a specific edit, interpreting bystander-confounded hits, distinguishing functional signal from indel artifact, integrating CRISPResso2 output with screen scoring, or deciding BE vs PE for SNV installation.
tool_type: mixed
primary_tool: CRISPResso2
---

## Version Compatibility

Reference examples tested with: CRISPResso2 2.2.14+, BE-Hive 1.0+ (BE prediction), pandas 2.2+, biopython 1.83+, numpy 1.26+, scipy 1.12+, scikit-learn 1.4+; Broad be-validation-pipeline notebooks (repo HEAD).

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `CRISPResso --version`
- Python: `pip show CRISPResso2`; BE-Hive is a GitHub clone (maxwshen/be_predict_bystander), not a PyPI package

If code throws ImportError, AttributeError, or TypeError, introspect the installed package and adapt the example to match the actual API rather than retrying.

## Base Editing Screen Analysis

**"Analyze my base-editor variant-function screen"** -> Quantify per-sgRNA target-base conversion, bystander rate, and indel byproducts from amplicon sequencing; filter on editing efficiency; map each sgRNA to its intended SNV (target + bystander pattern); compute per-variant fitness from the screen log-fold change; reconcile target vs bystander variant attribution; annotate against ClinVar / COSMIC.

- CLI: `CRISPResso --base_editor_output` for per-amplicon BE quantification
- CLI: Broad `be-validation-pipeline` for end-to-end pooled-screen analysis with editing-efficiency filtering
- Python: `BE-Hive` (Arbab 2020) for editing-efficiency prediction; clone maxwshen/be_predict_bystander and import via sys.path
- Web: `BE-Designer` (Hwang 2018, RGEN Tools) for variant-encoding sgRNA design

## Base Editor Chemistry Selection

| Editor | Reaction | Editing window | Indel byproduct rate | When to use |
|--------|----------|----------------|----------------------|-------------|
| BE3 (Komor 2016) | C->T (also G->A on opposite strand) | Pos 4-8 from PAM-distal end | 5-10% | Original; superseded |
| BE4 / BE4max (Koblan 2018) | C->T | Pos 4-8 | <5% | CBE standard |
| eA3A-BE3 | C->T narrow specificity | Pos 5-7 | <5% | Specifically TC contexts (eA3A prefers TC) |
| ABE7.10 (Gaudelli 2017) | A->G (T->C opposite strand) | Pos 4-7 | <2% | First ABE; slow at non-TA contexts |
| ABE8.20 (Gaudelli 2020) | A->G | Pos 4-8 | <2% | Modern ABE; high activity |
| ABE8e (Richter 2020) | A->G | Pos 4-8 | <2% | Highest editing activity; more processive than ABE7.10 |
| evoCDA-BE | C->T (broader) | Pos 1-9 | 5-10% | Larger editing window; more bystander |
| CGBE1 (Kurt 2021) | C->G | Pos 5-7 | 5-10% | C-to-G transversion; rare use |
| GBE (Zhao 2021) | C->G or C->A | Pos 4-7 | 5-10% | Transversions; less mature |

**Decision rule:** For a target SNV at position 4-8 of a candidate spacer with no bystander Cs/As in the same window, BE3-BE4 or ABE7.10 is sufficient. For high-throughput variant scanning where bystander tolerance must be minimized, use eA3A-BE3 (TC contexts only) for C->T, or ABE7.10 rather than ABE8e/ABE8.20 for A->G -- its 4-7 window is the narrowest ABE.

## Editing Window Math

**Why this matters for postdoc-level use:** Base editors are tethered to dCas9 (or nCas9) and the deaminase acts on the displaced ssDNA "R-loop" formed when Cas9 binds. The deaminase has a fixed reach -- positions 4-8 from the PAM-distal end of the protospacer for canonical BE3/BE4, and 4-7 for ABE7.10. Outside this window, editing efficiency drops by 10-50x.

```
PAM-distal end                                                            PAM-proximal
   |                                                                          |
   1  2  3  4  5  6  7  8  9  10 11 12 13 14 15 16 17 18 19 20    NGG
                  ^^^^^^^^^^^
                  Canonical editing window (positions 4-8)

   For BE4max: positions 4-8 are 5-50x more efficient than positions 1-3 or 9-13 (ABE7.10: 4-7)
   For SpABE8e: positions 4-8 (Richter 2020), matching the corresponding CBEs rather than ABE7.10's narrower 4-7
   For evoCDA-BE: window 1-9 (broader; more bystander)
```

**Critical implication for variant interpretation:** If the intended edit is at position 5 and there is an additional editable C/A at position 7, both will be edited in the same molecule. The screen scores the *combination* of edits, not the intended one alone. This is bystander confounding.

## sgRNA Library Design for BE Screens

**Goal:** Tile editing-window-positioned spacers across a protein region of interest to enable variant scanning.

**Approach:** For each amino acid in the target region, find NGG-adjacent spacers where the SNV-of-interest base falls in editing positions 4-8 with minimal bystander C/A in the same window. Annotate each spacer with the predicted amino acid changes (target + bystander).

```python
import pandas as pd
import re
from Bio.Seq import Seq

def find_be_spacers(cds_sequence, cds_protein_start, target_aa, target_base='C', editor='BE4max'):
    '''Find sgRNAs that place target_base in editor-specific window at target_aa.
    Returns spacers with bystander annotation.

    Args:
        cds_sequence: nucleotide CDS (translated frame 1)
        cds_protein_start: amino acid number of CDS start (usually 1)
        target_aa: amino acid number to install variant (e.g., 130 for residue 130)
        target_base: 'C' (CBE) or 'A' (ABE)
        editor: 'BE3', 'BE4max', 'eA3A-BE3', 'ABE7.10', 'ABE8.20', 'ABE8e', 'evoCDA-BE'

    Returns: DataFrame with spacer, position-in-cds, target-base-position-in-spacer,
             bystander_positions, predicted_aa_changes
    '''
    # Editor-specific editing window (positions from PAM-distal end of spacer)
    window_by_editor = {
        'BE3': (4, 8),       'BE4max': (4, 8),    'eA3A-BE3': (5, 7),
        'ABE7.10': (4, 7),   'ABE8.20': (4, 8),   'ABE8e': (4, 8),     # SpABE8e matches CBE window (Richter 2020)
        'evoCDA-BE': (1, 9),
    }
    window_lo, window_hi = window_by_editor[editor]
    aa_index = target_aa - cds_protein_start  # 0-indexed in protein
    aa_start_nt = aa_index * 3                # nt offset in cds
    candidates = []
    spacer_len = 20
    pam_pattern = re.compile(r'(?=([ACGT]GG))')
    for strand, seq in [('+', cds_sequence), ('-', str(Seq(cds_sequence).reverse_complement()))]:
        for pam_match in pam_pattern.finditer(seq):
            pam_pos = pam_match.start()
            spacer_start = pam_pos - spacer_len
            if spacer_start < 0:
                continue
            spacer = seq[spacer_start:pam_pos]
            # Editor-specific window from PAM-distal end (1-indexed)
            # Find all editable bases in window
            edit_bases_in_window = []
            for i, b in enumerate(spacer[window_lo-1:window_hi], start=window_lo):
                if b == target_base:
                    edit_bases_in_window.append(i)
            if not edit_bases_in_window:
                continue
            # Annotate which edits hit the target_aa codon
            target_codon_start = aa_start_nt
            target_codon_end = target_codon_start + 3
            target_position_in_spacer = []
            for i in edit_bases_in_window:
                genomic_pos = spacer_start + i - 1
                if target_codon_start <= genomic_pos < target_codon_end:
                    target_position_in_spacer.append(i)
            bystander_positions = [i for i in edit_bases_in_window if i not in target_position_in_spacer]
            candidates.append({
                'spacer': spacer,
                'strand': strand,
                'spacer_start': spacer_start,
                'target_positions': target_position_in_spacer,
                'bystander_positions': bystander_positions,
                'n_bystanders': len(bystander_positions),
            })
    return pd.DataFrame(candidates).sort_values('n_bystanders')
```

**Decision rule:** Select spacers with target_positions != empty AND n_bystanders minimized. For variant-by-variant scanning, accept up to 1-2 bystanders if biology of those positions is interpretable; flag for downstream variant attribution.

## Editing Efficiency Filtering (Critical Pre-Hit-Calling)

**Goal:** Drop sgRNAs that do not edit efficiently, since unedited reads represent no biological perturbation.

**Approach:** From CRISPResso2 output, compute target-base-conversion percentage per sgRNA; filter library to sgRNAs with >50% target editing in a pilot or co-screened control.

```python
def filter_by_editing_efficiency(crispresso_outputs_dir, target_pos, target_base, efficiency_threshold=0.5):
    '''Drop sgRNAs that edit <efficiency_threshold of reads at target position.
    crispresso_outputs_dir: directory containing CRISPResso per-sample outputs.'''
    from pathlib import Path
    results = []
    for sample_dir in Path(crispresso_outputs_dir).glob('CRISPResso_on_*'):
        sgrna_id = sample_dir.name.replace('CRISPResso_on_', '')
        quant_file = sample_dir / 'Quantification_window_nucleotide_percentage_table.txt'
        if not quant_file.exists():
            continue
        df = pd.read_csv(quant_file, sep='\t')
        # Find target position in the quantification window
        target_row = df[df['Position'] == target_pos]
        if target_row.empty:
            continue
        # Editing = sum of non-original bases at target position
        original_pct = target_row[target_base].values[0]
        editing_pct = (100 - original_pct) / 100
        results.append({'sgrna_id': sgrna_id, 'editing_pct': editing_pct,
                         'pass_filter': editing_pct >= efficiency_threshold})
    return pd.DataFrame(results)
```

**Convention:** Drop sgRNAs below 50% editing for variant-function screens. A common working split is a 30% editing floor for primary screening and a 50% floor for confirmed hits. Below 30%, the screen has insufficient power; above 70%, results approach saturation editing.

## Bystander Edit Attribution

**Why this matters:** When a sgRNA's editing window contains the target base AND a bystander base, the screen scores the combination. To attribute screen signal to the target variant alone, either (a) include sgRNAs that edit only the target (no bystander) -- often impossible -- or (b) deconvolute via parallel measurements.

**Strategies for variant-by-variant attribution:**

1. **Tile multiple sgRNAs with different bystander patterns:** If 5 different sgRNAs all hit the target base but have different bystanders, common signal across them is target-attributable (Hanna 2021 approach).

2. **Use orthogonal chemistry:** Run the same variant scan with prime editor (no bystanders); cross-validate. See [[prime-editing-screens]].

3. **Bystander stratification:** From CRISPResso2 allele table, partition reads by exact edit pattern (target only, target+bystander_1, target+bystander_2, etc.); separately score each pattern's contribution to the phenotype.

4. **Restrict library:** Use only sgRNAs with zero bystanders in the editing window (rare; may exclude most candidate spacers).

```python
def deconvolute_bystander(allele_table_path, target_pos, bystander_pos_list):
    '''From CRISPResso2 allele table, partition reads by edit pattern at target + bystanders.
    Returns: per-pattern frequency for each combination of target/bystander edits.'''
    alleles = pd.read_csv(allele_table_path, sep='\t', compression='zip')
    # Mark target_edited and per-bystander_edited
    alleles['target_edited'] = alleles['Aligned_Sequence'].str[target_pos-1] != alleles['Reference_Sequence'].str[target_pos-1]
    for bp in bystander_pos_list:
        alleles[f'bystander_{bp}_edited'] = alleles['Aligned_Sequence'].str[bp-1] != alleles['Reference_Sequence'].str[bp-1]
    return alleles.groupby(['target_edited'] + [f'bystander_{bp}_edited' for bp in bystander_pos_list])['Reference_pct'].sum().reset_index()
```

## Hit Calling for Variant-Function Screens

**Goal:** Score per-variant fitness from a base-editor screen.

**Approach:** Filter library to efficiency-passing sgRNAs (>50% editing), then run MAGeCK MLE or drugZ on the sgRNA-level counts; map each significant sgRNA to its predicted variant + bystander pattern; aggregate to per-variant scores.

```python
def aggregate_variant_scores(mageck_sgrna_summary, variant_annotation_df):
    '''Aggregate sgRNA-level scores to per-variant scores.
    variant_annotation_df: per-sgRNA -> predicted variants (target + bystanders).'''
    df = mageck_sgrna_summary.merge(variant_annotation_df, on='sgRNA')
    # Target-only contribution: sgRNAs with no bystanders
    target_only = df[df['n_bystanders'] == 0]
    target_only_scores = target_only.groupby('target_variant')['LFC'].agg(['mean', 'std', 'count'])
    # Mixed signal: sgRNAs with bystanders
    mixed = df[df['n_bystanders'] > 0]
    return target_only_scores, mixed
```

## Hanna 2021 BRCA1/2 Variant-Function Screen Methodology

**Hanna et al 2021 *Cell* 184:1064** benchmarked CBE variant scanning at scale, screening 68,526 sgRNAs covering 52,034 ClinVar variants across 3,584 genes, with BRCA1 and BRCA2 as the positive/negative-selection benchmark:

1. Design the CBE library from predicted variant impact (ClinVar annotation), covering each variant with the sgRNAs that install it
2. Run drug-modifier screens (PARPi sensitivity) with vehicle vs drug
3. Score per variant by aggregating over all sgRNAs that install it; cross-check against bystander-controlled sgRNAs

**Standard surrounding practice:** verify editing efficiency at a control timepoint via amplicon sequencing, drop low-efficiency sgRNAs (see the editing-efficiency convention above), and call sensitizers with a bidirectional method such as drugZ.

**Quantified result:** Recovered known loss-of-function variants in BRCA1 and BRCA2 with high precision, and identified PARP1 variants conferring resistance to PARP inhibitors.

## Cuella-Martin 2021 DDR-Gene Variant Screening

**Cuella-Martin et al 2021 *Cell* 184:1081-1097** screened ~86 DNA-damage-response (DDR) genes (including BRCA1/2) with CBE saturation mutagenesis:

- Saturation CBE design across 86 DDR genes (not BRCA1/2 alone)
- Identified pathogenic/likely-pathogenic variants in critical protein domains
- Combined with biochemical and genetic validation (for example the 53BP1-USP28 interaction surface)
- Demonstrated saturation mutagenesis is feasible at protein-domain scale

**Relationship to Hanna 2021:** the two studies appeared back-to-back in the same *Cell* issue and apply the same CBE variant-scanning strategy to complementary targets -- Hanna benchmarks against ClinVar-annotated variants genome-wide, Cuella-Martin saturates 86 DDR genes. Treat them as complementary methodology references, not as cross-validations of each other.

## Cas9 vs Base Editor vs Prime Editor for Variant Installation

| Approach | What it does | Bystander | Indels | When to use |
|----------|--------------|-----------|--------|-------------|
| Cas9 + HDR template | Installs precise edit + template | None | High (NHEJ competition) | When precise edit needed; high indel byproduct |
| Cas9 (no template) | Random indels at cut site | None | 70%+ | Loss-of-function; not variant-specific |
| CBE (BE3/BE4) | C->T at editing window | Yes (multiple Cs) | <5% | C->T variants with manageable bystanders |
| ABE (ABE7.10/ABE8e) | A->G at editing window | Yes (multiple As) | <2% | A->G variants; clean for single-A spacers |
| CGBE / GBE | C->G or C->A | Yes | 5-10% | Transversions; rare use cases |
| Prime editor (PE2/PE3) | Templated edit; any base change | None | 1-3% | Precise variants; lower efficiency |

**Decision:** For C->T or A->G with available editing window: base editor is preferred (higher efficiency than PE). For other transitions/transversions, multi-base edits, or zero-bystander requirements: prime editor.

## Broad be-validation-pipeline

The Broad Institute's `be-validation-pipeline` (https://broadinstitute.github.io/be-validation-pipeline/) is a CRISPResso2 post-processing and validation toolkit for BE amplicon data -- a set of Jupyter notebooks, not a workflow-engine pipeline. Run CRISPResso2 first, then execute the notebooks in order:

```bash
git clone https://github.com/broadinstitute/be-validation-pipeline
cd be-validation-pipeline
pip install -r requirements.txt

# Step 1: run CRISPResso2 in batch mode (or use the BEV tool on GPP LIMS).
# The batch file is tab-delimited with columns: name, fastq_r1, amplicon_seq, guide_seq
# (plus optional -w, -wc, --exclude_bp_from_left/right).
docker run -v ${PWD}:/DATA -w /DATA -i pinellolab/crispresso2 \
    CRISPRessoBatch --batch_settings batch_file.txt --skip_failed --base_edit

# Step 2: run the notebooks in order against the CRISPResso2 output
#   notebooks/01_BEV_allele_frequencies.ipynb
#   notebooks/02_BEV_nucleotide_percentage_plots.ipynb
#   notebooks/03_BEV_editing_efficiency.ipynb
# Outputs: allele-frequency tables, nucleotide-percentage plots, editing-efficiency heat maps
```

The notebooks cover allele-frequency tabulation, nucleotide-level editing quantification and editing-efficiency summaries. Hit calling is NOT part of this toolkit -- score the screen separately with drugZ or MAGeCK.

## Failure Modes

### Mostly indels in BE sample

**Trigger:** Cas9 contamination, wrong vector (e.g., used pCas9-BE3 plasmid but selected on Cas9 line), or evoCDA-BE / broader-window chemistry.
**Mechanism:** Cas9 cuts dsDNA; BE relies on nicked-ssDNA deamination. Cas9 expression in the same cell creates indels.
**Symptom:** Substitution-vs-indel ratio <3 in CRISPResso output.
**Fix:** Verify vector (nCas9-BE3 not Cas9-BE3); confirm cell line lacks Cas9 background; restrict to specifically engineered BE-cell lines.

### High editing but no biological signal

**Trigger:** Bystander C/A is dominating; intended variant is not the perturbation driving phenotype.
**Mechanism:** When target is at position 5 and bystander is at position 7, the molecule carries both; phenotype is from the bystander.
**Symptom:** Strong screen signal but variant attribution unclear.
**Fix:** Run orthogonal prime-editor scan of the same intended variants; restrict library to bystander-free spacers when possible; deconvolute via allele-frequency table.

### sgRNA shows perfect editing but no fitness signal

**Trigger:** Intended variant is silent or compensatory; the protein function is unchanged.
**Mechanism:** Variants can be tolerated; not all variants are LoF or GoF.
**Symptom:** High editing efficiency (>70%) but per-sgRNA LFC near zero.
**Fix:** Expected outcome for many variants; flag silent / compensatory variants in the report.

### Low editing across all guides

**Trigger:** Wrong cell line for the BE; cell line has poor BE activity (some lines lack APOBEC or have low expression).
**Mechanism:** BE efficiency depends on cell-line expression of TadA or APOBEC components.
**Symptom:** Median editing <30% across library.
**Fix:** Test in a BE-validated cell line (HEK293T, U2OS, K562 generally work); pilot before full screen.

### Library missing intended-variant sgRNAs

**Trigger:** No NGG-adjacent spacer places target base in editing window for that codon.
**Mechanism:** Editor window is fixed; some codons cannot be targeted with given chemistry.
**Symptom:** Specific variants absent from screen.
**Fix:** Use PAM-relaxed BE variants (SpRY-CBE, SpRY-ABE); use prime editor for variants outside BE accessibility; accept that some variants cannot be installed.

## Quantitative Thresholds

| Threshold | Value | Source / Rationale |
|-----------|-------|--------------------|
| Editing window | Positions 4-8 from PAM-distal end (BE3/BE4); 4-7 (ABE7.10); 4-8 (SpABE8e) | Komor 2016; Gaudelli 2017; Richter 2020 |
| Editing efficiency for screen power | >30% (primary); >50% (validation) | Field convention (BE variant screens) |
| Indel byproduct (clean BE) | <5%; <2% for ABE | Koblan 2018 (BE4max); Gaudelli 2017 (ABE) |
| Substitution-vs-indel ratio | >10 (clean BE); <3 (Cas9-like) | CRISPResso2 diagnostic |
| Bystander rate (target attribution) | <10% acceptable; <5% ideal for clean attribution | Application-dependent |
| Cell-line BE activity (pilot) | >30% editing at validated target | Below = wrong cell line for BE |
| Per-amino-acid sgRNA density | 10-15 (saturation designs); 5-8 (smaller screens) | Tradeoff with library size |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| Substitution-vs-indel ratio <3 | Cas9 contamination or wrong BE | Verify vector / cell line; pilot first |
| All edits at bystander positions | Target base outside window | Re-design spacer with target at pos 4-8 |
| Variant attribution unclear | Bystander confounding | Run orthogonal PE; restrict library |
| Library lacks intended variant | No NGG-PAM accessibility | SpRY-CBE; prime editor; accept exclusion |
| Editing <30% library-wide | Cell-line BE inactivity | Re-validate cell line |
| Hit list dominated by single sgRNA | Bystander-driven phenotype | Cross-check with bystander-free sgRNAs |

## References

- Komor AC et al. 2016. *Nature* 533:420. BE3.
- Gaudelli NM et al. 2017. *Nature* 551:464. ABE7.10.
- Koblan LW et al. 2018. *Nat Biotechnol* 36:843. BE4max + improved CBE.
- Richter MF et al. 2020. *Nat Biotechnol* 38:883. ABE8e; phage-assisted evolution of ABE7.10.
- Lapinaite A et al. 2020. *Science* 369:566. ABE8e mechanism.
- Gaudelli NM et al. 2020. *Nat Biotechnol* 38:892. ABE8 series (ABE8.20).
- Hanna RE et al. 2021. *Cell* 184:1064. Massively parallel BRCA1/2 variant function via CBE.
- Cuella-Martin R et al. 2021. *Cell* 184:1081-1097. CBE saturation across 86 DDR genes (BRCA1/2 plus others).
- Arbab M et al. 2020. *Cell* 182:463. BE-Hive prediction of editing outcomes.
- Anzalone AV et al. 2019. *Nature* 576:149. Prime editing (PE2/PE3).
- Clement K et al. 2019. *Nat Biotechnol* 37:224. CRISPResso2.
- Kurt IC et al. 2021. *Nat Biotechnol* 39:41. CGBE1.

## Related Skills

- crispr-screens/crispresso-editing - CRISPResso2 BE/PE mode and allele tables
- crispr-screens/library-design - base-editor library design
- crispr-screens/prime-editing-screens - Orthogonal PE for variant attribution
- crispr-screens/hit-calling - Variant-level hit aggregation
- crispr-screens/screen-qc - Editing-efficiency QC
- crispr-screens/drugz-chemogenomic - drugZ for BE drug-modifier screens
- clinical-databases/clinvar-lookup - Variant pathogenicity annotation
- variant-calling/variant-annotation - VEP for predicted amino acid changes
<!-- END FILE: crispr-screens/base-editing-analysis/SKILL.md -->

## 子目录：crispr-screens/batch-correction

<!-- BEGIN FILE: crispr-screens/batch-correction/SKILL.md -->
---
name: bio-crispr-screens-batch-correction
description: Batch effect correction for CRISPR screens covering ComBat empirical-Bayes, RUV, SVA, control-sgRNA normalization, and the model-based alternative of including batch as a covariate in MAGeCK MLE or Chronos. Covers screen-specific batch sources (passage cohort, library lot, infection day, sequencing run, Cas9 lot, FBS lot), PCA + variance-decomposition diagnostic to decide if correction is needed, when correction harms biology by over-correcting condition into batch, limma removeBatchEffect for visualization-only correction, and relationship to multi-condition design matrices. Use when combining screens for joint analysis, when passage cohort confounds biology, when DepMap-style panels need Chronos with batch covariates, when picking ComBat vs RUV, or when correction harms biology and should be replaced with explicit covariate modeling.
tool_type: mixed
primary_tool: pyComBat
---

## Version Compatibility

Reference examples tested with: pyComBat 0.3.3+ (epigenelabs/pyComBat), MAGeCK 0.5.9+, R/limma 3.58+, sva 3.50+, RUVSeq 1.36+, pandas 2.2+, numpy 1.26+, scikit-learn 1.4+, scipy 1.12+.

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show combat`; `from combat.pycombat import pycombat`
- R: `packageVersion('sva')`; `?ComBat`; `packageVersion('RUVSeq')`; `?RUVg`

If code throws ImportError, AttributeError, or TypeError, introspect the installed package and adapt the example to match the actual API rather than retrying.

## Batch Correction for CRISPR Screens

**"Correct batch effects in my CRISPR screens"** -> Diagnose the batch source, decide whether to remove via empirical-Bayes (ComBat), explicit covariate modeling (MAGeCK MLE / Chronos design matrix), control-guide-anchored normalization, or unwanted-variation decomposition (RUV, SVA), then apply only the correction that preserves biological condition signal.

- Python: `pyComBat.pycombat` for empirical-Bayes correction
- Python: explicit batch covariates in `mageck mle --design-matrix`
- R: `sva::ComBat`, `RUVSeq::RUVg`, `limma::removeBatchEffect`
- Python: Chronos (`crispr_chronos`) natively handles screen-batch covariates

## Batch Sources in CRISPR Screens

| Source | Mechanism | Detectable by |
|--------|-----------|---------------|
| Library lot | Different aliquots or PCR amplifications | Gini shift; plasmid-pool sequencing |
| Cell passage cohort | Cells passaged through different periods | PCA Day-0 samples clustering by passage |
| Infection day | Lentivirus titer drifts; FBS lot changes | PCA Day-0 samples cluster by day |
| Cas9 enzyme lot | Cas9 expression heterogeneity | PR-AUC drift across screens |
| Sequencing run | Lane bias, flowcell variant, machine | Per-sample read-count distribution |
| FBS / culture lot | Fetal bovine serum lot variations confound proliferation | Day-0 vs endpoint differential not present in vehicle |
| Tissue-prep batch | In-vivo: animal cohort, surgical day, organ-prep tech | In-vivo screens (see [[in-vivo-screens]]) |

**Critical:** Batch effects in CRISPR screens often correlate with biology (e.g., the drug arm was processed in batch 2 because that's when the drug arrived). This confounds correction. Always check for confounding before applying ComBat.

## Batch Effect Decision Tree

| Diagnostic finding | Recommended correction |
|--------------------|------------------------|
| PCA shows samples cluster by condition, not batch | No correction needed; biology dominates |
| PCA PC1 separates batches, PC2 separates conditions | Apply ComBat with condition as biological_covariate |
| Batch fully confounded with condition (e.g. all drug in batch 2, all vehicle in batch 1) | Correction will destroy biology; instead redesign next screen with cross-batch balance OR re-analyze with batch in MAGeCK MLE design matrix |
| Day-0 (pre-perturbation) samples cluster by batch | Strong batch effect; ComBat needed |
| Endpoint samples cluster by batch but not Day-0 | Selection-driven artifact (FBS lot etc); correct or include batch as covariate |
| Replicates within a batch are tight; across-batch much wider | Classic batch effect; ComBat |
| Each replicate scatters randomly across PCs | Sample-level noise; no batch correction will help |
| Cancer-line panel with multiple batches | Use Chronos (built-in batch modeling) |

## Diagnose: PCA + Variance Decomposition

**Goal:** Quantify what fraction of variance is batch vs condition before correcting.

**Approach:** Run PCA on log10(counts+1); fit ANOVA decomposing variance into batch and condition components; report variance explained.

```python
import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
from scipy import stats

def batch_diagnostic(counts_df, metadata_df, batch_col='batch', condition_col='condition'):
    '''Variance decomposition: report fraction of PC1/PC2 variance attributable to batch vs condition.'''
    log_counts = np.log10(counts_df + 1).T  # samples as rows
    pca = PCA(n_components=5)
    pcs = pca.fit_transform(log_counts)
    out = pd.DataFrame({
        'PC': range(1, 6),
        'var_explained': pca.explained_variance_ratio_,
    })
    pc_df = pd.DataFrame(pcs, columns=[f'PC{i+1}' for i in range(5)], index=counts_df.columns).join(metadata_df)
    for i in range(5):
        pc = pc_df[f'PC{i+1}']
        f_b, p_b = stats.f_oneway(*[pc[pc_df[batch_col] == b] for b in pc_df[batch_col].unique()])
        f_c, p_c = stats.f_oneway(*[pc[pc_df[condition_col] == c] for c in pc_df[condition_col].unique()])
        out.loc[i, 'batch_F'] = f_b
        out.loc[i, 'batch_p'] = p_b
        out.loc[i, 'cond_F'] = f_c
        out.loc[i, 'cond_p'] = p_c
    return out
```

**Interpretation:** If PC1 has batch F-stat > condition F-stat by 10x, batch is dominating and correction is warranted. If condition dominates PC1, no correction needed.

## ComBat Empirical-Bayes Correction

**Goal:** Remove batch-specific location and scale shifts while preserving biological condition signal.

**Approach:** Log-transform counts, fit ComBat with explicit `biological_covariate` indicating condition (so the model knows which signal to preserve), back-transform.

```python
import numpy as np
from combat.pycombat import pycombat

def combat_correct(counts_df, batch_vector, condition_vector=None):
    '''ComBat on log-counts with optional biological covariate (condition).
    Preserves condition signal while removing batch shifts.'''
    data = np.log2(counts_df.values + 1)
    if condition_vector is not None:
        mod = pd.get_dummies(condition_vector).values.astype(float)
        corrected = pycombat(data, list(batch_vector), mod=mod)      # data must be a DataFrame
    else:
        corrected = pycombat(data, list(batch_vector))               # data must be a DataFrame
    return pd.DataFrame(np.power(2, corrected) - 1,
                         index=counts_df.index, columns=counts_df.columns).clip(lower=0)
```

**Critical caveat:** ComBat assumes batch effects are linear shifts of mean and variance in log space. Non-linear effects (e.g., gene-specific batch sensitivity) remain. Always re-check PCA after correction to confirm batches now overlap.

## RUV (Remove Unwanted Variation)

**Goal:** Identify hidden batch sources via control sgRNAs whose true signal is known.

**Approach:** Designate non-targeting controls as "negative controls" (assumed unchanged); RUV decomposes their variance into unwanted factors, then subtracts these from all data.

```r
library(RUVSeq)
# counts_df: rows = sgRNAs, columns = samples
ntc_indices <- which(rownames(counts_df) %in% ntc_sgrna_names)
seqset <- newSeqExpressionSet(counts = as.matrix(counts_df))
ruv_corrected <- RUVg(seqset, cIdx = ntc_indices, k = 2)  # k = 2 unwanted factors
# Access corrected data
corrected_counts <- normCounts(ruv_corrected)
```

**When to use:** RUV preferred over ComBat when batches are not annotated (e.g., unknown technical confounders). Worse than ComBat when batch is known and well-annotated; ComBat is more direct.

## SVA (Surrogate Variable Analysis)

**Goal:** Estimate unknown latent factors that may confound the screen.

**Approach:** SVA computes surrogate variables that capture variance not explained by known biological factors; these can then be added to the MAGeCK MLE design matrix as covariates.

```r
library(sva)
# counts_df: rows = sgRNAs, columns = samples
mod <- model.matrix(~ condition, data = metadata)
mod0 <- model.matrix(~ 1, data = metadata)
sv_obj <- sva(as.matrix(counts_df), mod, mod0)
n_sv <- sv_obj$n.sv  # number of surrogate variables
# Add to design matrix for MAGeCK MLE
design_mat <- cbind(mod, sv_obj$sv)
```

**Use case:** When the screen has clear biological signal (e.g. essentiality recovery passes) but small effect sizes are hidden by noise; SVA-discovered latent factors as covariates can recover them.

## Batch as Explicit Covariate (Preferred for MAGeCK MLE / Chronos)

**Goal:** Model batch and biology in the same regression instead of pre-correcting.

**Approach:** Add batch indicator columns to the MLE design matrix. The fitted beta for condition is the effect after accounting for batch; no pre-correction needed.

```bash
# Design matrix for a screen with 2 batches and 2 conditions
cat > design.txt <<EOF
Samples         baseline    batch2    treatment
Veh_b1_r1       1           0         0
Veh_b1_r2       1           0         0
Drug_b1_r1      1           0         1
Drug_b1_r2      1           0         1
Veh_b2_r1       1           1         0
Veh_b2_r2       1           1         0
Drug_b2_r1      1           1         1
Drug_b2_r2      1           1         1
EOF

mageck mle \
    --count-table counts.txt \
    --design-matrix design.txt \
    --output-prefix batch_aware_mle
```

**Why this is preferred:** ComBat shifts counts before testing; the MLE-with-covariates approach correctly propagates uncertainty from the batch term into the condition beta's standard error. ComBat-then-test pretends the corrected counts are noise-free, biasing FDR.

## Control-Sgrna Anchored Normalization

**Goal:** Use non-targeting controls as the per-sample reference so batch shifts cancel.

**Approach:** Scale each sample so its NTC sgRNAs have a constant median. Subsequent fold changes are relative to NTCs in each sample, automatically batch-controlling.

```python
def ntc_anchored_normalize(counts_df, ntc_sgrna_names, target_median=1000):
    '''Scale each sample so its NTC median is target_median. Subsequent LFC is NTC-anchored.'''
    is_ntc = counts_df.index.isin(ntc_sgrna_names)
    ntc_medians = counts_df.loc[is_ntc].median(axis=0)
    scale_factors = target_median / ntc_medians.replace(0, np.nan)
    return counts_df * scale_factors, scale_factors
```

**Critical:** Requires ≥500 NTCs in the library (see [[library-design]]). With fewer, the NTC median is unstable and amplifies noise rather than removing batch.

## When NOT to Correct

| Situation | Why correction hurts |
|-----------|----------------------|
| Batch is fully confounded with condition | Correction destroys biology along with batch; redesign or accept |
| Batch effect is smaller than between-replicate noise | Correction adds noise without removing meaningful variance |
| Replicates already correlate >0.95 within and across batches | No batch effect to correct |
| Single-screen analysis | No "batch" to correct; only replicate noise |
| Per-batch sample size <3 | Cannot estimate batch shift reliably; correction is harmful |

## Failure Modes

### ComBat eliminates biological signal

**Trigger:** Batch is correlated with condition (e.g., all drug-arm samples were processed week 2; all vehicle-arm samples week 1).
**Mechanism:** ComBat without a `mod` covariate treats condition variance as batch variance; corrects it away.
**Symptom:** PR-AUC against CEGv2 drops after ComBat correction.
**Fix:** Always supply `mod` covariate matrix indicating condition; verify by comparing PR-AUC before and after.

### RUV adds noise instead of removing it

**Trigger:** k (number of unwanted factors) set too high.
**Mechanism:** RUV's least-squares decomposition over-fits; "removed" variance includes biology.
**Symptom:** Hits decrease and replicate Pearson drops after correction.
**Fix:** Choose k via cross-validation; default k=1 or 2 for most screens.

### Batch-aware MLE collinear design matrix

**Trigger:** Adding a batch indicator that is fully collinear with another design column (e.g., all of batch 2 is also Day 21).
**Mechanism:** MLE design matrix is singular; betas not estimable.
**Symptom:** MAGeCK MLE errors out or produces NaN betas.
**Fix:** Drop the collinear column; re-design experiment with cross-batch balance.

### ComBat after RUV double-corrects

**Trigger:** Applying multiple corrections sequentially.
**Mechanism:** Both methods remove variance; sequential application removes biology twice.
**Symptom:** All signal gone; counts look uniformly noisy.
**Fix:** Pick one method based on diagnostic; never combine.

### Per-batch sample size too small

**Trigger:** 2 replicates per batch with 3 batches; ComBat estimates batch shift from 2 samples.
**Mechanism:** Insufficient data to estimate batch parameters; high-variance estimates.
**Symptom:** Correction makes some batches worse than uncorrected.
**Fix:** Need ≥3 (preferably 4-6) samples per batch; below this, use covariate modeling instead.

## Quantitative Thresholds

| Threshold | Value | Source / Rationale |
|-----------|-------|--------------------|
| PC1 batch F vs condition F | F_batch > 10x F_cond -> apply correction | Standard variance-decomposition diagnostic |
| ComBat min samples per batch | ≥3, ideally 4-6 | Empirical Bayes prior estimation |
| RUV `k` (unwanted factors) | k=1 default; k=2 if multiple known batch sources | Risso 2014; cross-validate |
| NTCs needed for NTC-anchored norm | ≥500 in library | Stable median |
| Post-correction PCA check | Batches must overlap in PC1/PC2 plot | Visual sanity check |
| Post-correction PR-AUC | Should be same or higher than pre | If lower, correction destroyed biology |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| PR-AUC drops after ComBat | Batch confounded with condition | Add `mod` covariate; or redesign |
| MAGeCK MLE NaN beta after adding batch column | Collinear design matrix | Drop collinear column |
| Replicates still cluster by batch after RUV | k too low | Increase k; cross-validate |
| Replicates lose internal cohesion after correction | Over-correction | Reduce k or revert |
| NTC-anchored norm worse than median | Too few NTCs | Use median; add NTCs to next library |
| Sequencing-run-level batch survives ComBat | Non-linear sequencing effect | Pre-normalize with `mageck count --norm-method control` first |

## References

- Johnson WE et al. 2007. *Biostatistics* 8:118. Original ComBat algorithm.
- Leek JT et al. 2012. *Bioinformatics* 28:882. SVA package.
- Risso D et al. 2014. *Nat Biotechnol* 32:896. RUVSeq.
- Pacini C et al. 2021. *Nat Commun* 12:1661. Integrated cross-study dependencies; cross-screen batch-effect correction.
- Vinceti A et al. 2024. *Genome Biol* 25:192. Benchmark of methods for correcting biases in CRISPR-Cas9 screening data.

## Related Skills

- crispr-screens/mageck-analysis - MAGeCK MLE with explicit batch covariates
- crispr-screens/screen-qc - Pre-correction PCA diagnostic
- crispr-screens/copy-number-correction - Chronos handles batch + CN jointly
- crispr-screens/library-design - NTC composition for NTC-anchored normalization
- crispr-screens/jacks-analysis - Joint analysis across batches with shared efficacy
- crispr-screens/hit-calling - Post-correction hit calling
- crispr-screens/in-vivo-screens - In-vivo-specific batch sources (animal cohort, tissue prep)
<!-- END FILE: crispr-screens/batch-correction/SKILL.md -->

## 子目录：crispr-screens/combinatorial-screens

<!-- BEGIN FILE: crispr-screens/combinatorial-screens/SKILL.md -->
---
name: bio-crispr-screens-combinatorial-screens
description: Designs and analyzes combinatorial CRISPR screens covering paired-Cas9 (Big Papi, Najm 2018), enhanced AsCas12a multiplex (enCas12a, DeWeirdt 2021), in4mer 4-guide-array Cas12a (Esmaeili Anvar N et al 2024 Nat Commun 15:3577) and the Inzolia paralog-pair library, paralog-buffering detection (Dede 2020 Genome Biol; Thompson 2021 Nat Commun 12:1302), genetic-interaction (GI) scoring as observed_double_LFC minus expected_additive_double_LFC, synthetic-lethal and synthetic-rescue interaction interpretation, the half-of-essentiality buffered by paralogs phenomenon, multiplex screen statistical analysis with MAGeCK MLE interaction terms, and the relationship to single-cell combinatorial Perturb-seq. Use when designing a paralog or pathway-pair screen, choosing between paired-Cas9 (Big Papi) and Cas12a multiplex (Inzolia), interpreting genetic interaction scores, identifying synthetic-lethal targets for drug development, or scaling beyond single-gene CRISPR screens.
tool_type: mixed
primary_tool: enCas12a
---

## Version Compatibility

Reference examples tested with: MAGeCK 0.5.9+ (for MLE with interaction terms), Inzolia library annotation (Esmaeili Anvar 2024), pandas 2.2+, numpy 1.26+, scipy 1.12+, matplotlib 3.8+.

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `mageck --version`; `mageck mle --help`
- For Cas12a libraries: verify against published Inzolia / in4mer / Big Papi annotations

If code throws ImportError, AttributeError, or TypeError, introspect the installed package and adapt the example to match the actual API rather than retrying.

## Combinatorial CRISPR Screen Analysis

**"Run a combinatorial CRISPR screen to find synthetic-lethal interactions"** -> Design a paired or multiplex library, screen for double-knockout fitness, score per-pair genetic interaction (GI = observed_double - expected_additive), and identify synthetic-lethal (negative GI) and synthetic-rescue (positive GI) interactions.

- CLI: `mageck mle` with explicit interaction terms for paired-Cas9 (Big Papi-style)
- Python: custom GI scoring for Cas12a multiplex (in4mer / Inzolia)
- Modality: enCas12a / LbCas12a single-array multiplex (preferred for paralog screens)

## Combinatorial Architecture Decision Tree

| Goal | Architecture | Library | Why |
|------|--------------|---------|-----|
| Paralog buffering, identify synthetic lethal paralog pairs | enCas12a single-array 4-guide multiplex | Inzolia (Esmaeili Anvar 2024) | Cas9 single-KO misses paralog-buffered essentials (42% of constitutively expressed genes never score, Dede 2020) |
| Test specific pathway pair (e.g., DNA repair branches) | Big Papi (orthologous SaCas9 + SpCas9; two sgRNAs from U6 and H1 in pPapi) | Custom | Mature methodology; orthologous enzymes avoid repeated-element recombination |
| Combinatorial 3-way / 4-way knockout | in4mer (4-guide single Cas12a array) | Custom (in4mer) | Single transcript processed by Cas12a; multi-gene |
| Single-cell Perturb-seq with multi-pert per cell | Combinatorial Perturb-seq + Cas9 multiplex | Custom | Single-cell readout of multi-perturbation effects |
| Drug-modifier + KO interaction | Cas9 KO + drug treatment | Standard libraries | Drug as second "perturbation" |

**Fails when:**
- Dual-sgRNA constructs built from repeated U6/tracr elements: lentiviral recombination collapses them to a single perturbation
- Cas12a screens analyzed as Cas9 screens: MAGeCK normalization fails because Cas12a has different cut profile
- in4mer 4-guide arrays without all-singleton controls: GI scoring requires single-gene baselines

## Cas9 vs Cas12a for Multiplex

| Property | Cas9 paired (Big Papi) | Cas12a multiplex (in4mer / Inzolia) |
|----------|------------------------|--------------------------------------|
| Multiplex capacity per cassette | 2 sgRNAs (paired) | 4 (in4mer); 2 (standard Cas12a) |
| sgRNA processing | U6 and H1 promoters driving sgRNAs for two orthologous Cas9s | Single transcript processed by Cas12a itself |
| sgRNA inhibition with multiple targets | None | None (Cas12a's intrinsic processing handles all) |
| Library size for 1,000 pairs | ~4,000-6,000 paired cassettes (4-6 per pair) | ~2,000 arrays (2 per pair) plus singleton controls |
| Validated libraries | Limited (mostly custom) | Inzolia: ~49k 4-guide arrays covering 19,687 genes plus ~4,435 paralog pairs |
| Per-perturbation editing efficiency | High (each sgRNA independently) | Variable (Cas12a less efficient on some targets) |
| Best for | Pairwise GI of specific interest | Genome-scale paralog buffering; multi-gene perturbation |

**Recommendation:** For modern paralog screens, use Cas12a multiplex with the Inzolia library. It is ~30% smaller than a typical monogenic Cas9 library while additionally covering ~4,000 paralog pairs (Esmaeili Anvar 2024), which makes it more cost-effective at genome scale.

## The Paralog Buffering Phenomenon

**Dede et al 2020 *Genome Biol* 21:262** showed that a large share of constitutively expressed genes are never scored as essential in any Cas9 single-KO fitness screen (3,032 of 7,282; 42%), and that these never-essentials are strongly enriched for paralogs. The reason: gene paralogs perform redundant essential functions. Loss of one paralog is buffered by the other; only loss of both creates the essentiality phenotype.

**Quantified impact:** 24 synthetic-lethal paralog pairs identified in Dede 2020 across 3 cell lines; 19 of 24 (79%) reproduce in >=2 lines, 14 of 24 (58%) in all 3. These pairs were not findable by single-gene Cas9 screens, requiring combinatorial methodology.

**Examples:**
- **MAPK1 (ERK2) + MAPK3 (ERK1):** ERK family redundancy in proliferation
- **PIK3CA + PIK3CB:** PI3K alpha/beta redundancy
- **AKT1 + AKT2:** AKT family redundancy
- **HSP90AA1 + HSP90AB1:** HSP90 alpha/beta redundancy
- **STAG1 + STAG2:** Cohesion complex paralogs

Each is buffered: loss of one is tolerated; loss of both is lethal.

## Genetic Interaction (GI) Scoring

**Goal:** Identify pairs where the double-knockout fitness differs from the additive expectation.

**Approach:** From per-pair and per-singleton fitness data, compute GI = observed_double_LFC - (single_A_LFC + single_B_LFC). Synthetic lethal: GI < threshold (more depleted than additive). Synthetic rescue: GI > threshold (less depleted than additive).

```python
import pandas as pd
import numpy as np
from scipy.stats import zscore

def gi_score(paired_lfc_df, single_lfc_df):
    '''Score genetic interactions from paired vs single LFCs.

    paired_lfc_df: rows = paired-KO; columns = ['gene_A', 'gene_B', 'paired_lfc']
    single_lfc_df: rows = single-KO; columns = ['gene', 'single_lfc']
    '''
    single = dict(zip(single_lfc_df['gene'], single_lfc_df['single_lfc']))
    df = paired_lfc_df.copy()
    df['single_A_lfc'] = df['gene_A'].map(single)
    df['single_B_lfc'] = df['gene_B'].map(single)
    df['expected_additive'] = df['single_A_lfc'] + df['single_B_lfc']
    df['gi_score'] = df['paired_lfc'] - df['expected_additive']
    df = df.dropna(subset=['gi_score'])          # a single missing singleton would NaN every z-score
    df['gi_z'] = zscore(df['gi_score'])
    df['gi_class'] = np.where(df['gi_z'] < -2, 'synthetic_lethal',
                                np.where(df['gi_z'] > 2, 'synthetic_rescue', 'no_interaction'))
    return df.sort_values('gi_z')
```

**Interpretation:**
- GI z-score < -2: Synthetic lethal (double-KO more lethal than expected) -- candidate drug target combinations
- GI z-score > 2: Synthetic rescue (double-KO less lethal than expected) -- compensatory pathway / paradoxical hit
- GI z-score -1 to 1: No interaction; effects are additive

## Run Combinatorial Screen Analysis (MAGeCK MLE with Interaction Indicator)

**Goal:** Use MAGeCK MLE to estimate the effect of each gene independently and the additional effect when both genes are simultaneously perturbed.

**Approach:** Design matrix encodes single-A, single-B, double-AB conditions; the `interaction` column is set to 1 only for double-KO samples. The resulting beta for that column captures the extra effect beyond the sum of single-gene betas. Note: MAGeCK MLE does not natively perform a formal interaction-significance test, but the `interaction|beta` and `|fdr` columns serve as the GI estimate; for formal interaction testing, compute GI = observed_double_lfc - (single_A_lfc + single_B_lfc) explicitly (see GI scoring section below).

```bash
# Design matrix encoding double-KO as a separate "interaction" indicator
# Conditions: NT (control), A_KO, B_KO, A_B_KO
cat > combo_design.txt <<EOF
Samples         baseline    geneA       geneB       interaction
NT_r1           1           0           0           0
NT_r2           1           0           0           0
A_r1            1           1           0           0
A_r2            1           1           0           0
B_r1            1           0           1           0
B_r2            1           0           1           0
AB_r1           1           1           1           1
AB_r2           1           1           1           1
EOF

mageck mle \
    --count-table combo_counts.txt \
    --design-matrix combo_design.txt \
    --output-prefix combo_mle

# Output: per-gene beta scores per design column
# The "interaction" column beta captures additional joint effect beyond additive
```

**Interpretation of MAGeCK MLE output:**

| Column | Meaning |
|--------|---------|
| `geneA|beta` | Single-A effect |
| `geneB|beta` | Single-B effect |
| `interaction|beta` | Additional effect under joint perturbation beyond sum of singles |
| `interaction|p-value`, `|fdr` | Significance vs zero |

A significantly negative `interaction|beta` is synthetic lethal; positive is synthetic rescue. For formal GI hypothesis testing, prefer the explicit GI scoring approach (next section) over MAGeCK MLE interpretation, since MAGeCK MLE does not validate the additive null.

## Inzolia / in4mer 4-Guide Array Analysis

**Esmaeili Anvar 2024 *Nat Commun* 15:3577** introduced in4mer, a Cas12a multiplex architecture where each array contains 4 guides processed by Cas12a's intrinsic crRNA-processing activity. The Inzolia library is the canonical implementation, covering the protein-coding genome plus ~4,435 paralog pairs.

**Library design:**
- 4 guides per cassette (Cas12a single-transcript array)
- Per pair: 2 arrays carrying 2 guides per gene, with the guides presented in different order across the two arrays
- Includes singleton controls: each single gene is covered by 2 four-guide arrays (4 guides per gene, order swapped)
- ~49,000 total arrays covering 19,687 genes, ~4,435 paralog pairs, 376 triples, and 100 quads

```python
# Per-pair analysis from in4mer screen
def in4mer_pair_analysis(paired_counts_df, gene_pairs, value_cols):
    '''Aggregate cassette-level counts to per-pair statistics.
    paired_counts_df: rows = cassettes, with a cassette_id COLUMN (reset_index first if it is the index).
    gene_pairs: DataFrame with cassette_id and gene_A, gene_B columns.
    value_cols: the numeric sample/LFC columns to aggregate.
    '''
    merged = paired_counts_df.merge(gene_pairs, on='cassette_id')
    return merged.groupby(['gene_A', 'gene_B'])[value_cols].agg(['mean', 'std', 'count'])
```

## Failure Modes

### Dual-sgRNA construct recombines in the lentiviral vector

**Trigger:** A dual-sgRNA construct built from repeated elements -- two copies of the U6 promoter, or two copies of the SpCas9 tracrRNA scaffold.
**Mechanism:** Najm 2018 reports that repetitive elements in lentiviral vectors, including the U6 promoter and multiple copies of the tracrRNA sequence, drive high levels of recombination and reduce combinatorial screen efficiency. Big Papi avoids this by pairing two orthologous enzymes (SaCas9 + SpCas9), whose scaffolds differ, and expressing the two sgRNAs from distinct U6 and H1 promoters.
**Symptom:** Constructs collapse to a single perturbation; measured GI scores are diluted toward zero.
**Fix:** Use the pPapi architecture (orthologous Cas9s, U6 + H1) rather than duplicated U6/tracr elements; verify construct integrity by amplicon sequencing of clones.

### Cas12a screen with low editing efficiency

**Trigger:** Cas12a less efficient than Cas9 at some loci; some guides in the 4-guide array don't cut.
**Mechanism:** Cas12a editing rate varies by sequence context; some loci edit at <30%.
**Symptom:** Specific pairs missing expected effects despite cassette presence.
**Fix:** Pilot Cas12a efficiency at the loci before full screen; use enCas12a (enhanced) variant; for known low-efficiency loci, supplement with Cas9.

### GI scoring without singletons

**Trigger:** Library lacks single-gene controls (only paired knockouts).
**Mechanism:** GI = paired - expected_additive requires single-gene LFC; without them, expected cannot be computed.
**Symptom:** Cannot score GI; only paired LFCs available.
**Fix:** Design library to include singletons (place gene A with 3 placeholder guides; gene B with 3 placeholders); re-run with full design.

### Single-gene LFCs from different cell line

**Trigger:** Using public single-gene LFCs (e.g., DepMap) as the baseline for paired-screen GI scoring.
**Mechanism:** Single-gene effects are cell-line specific; using HCT116 single-gene LFCs to score K562 paired-screen GIs is invalid.
**Symptom:** GI scores look noisy; many false positives.
**Fix:** Include singleton controls in the screen; or use cell-line-matched DepMap data.

### Confounding cell-cycle / proliferation in GI scoring

**Trigger:** Paired KO of two cell-cycle-impacting genes; the double-effect saturates cell cycle.
**Mechanism:** If A_KO causes 50% growth arrest and B_KO causes 50%, the combined 75% arrest is already saturating proliferation; additive expectation overestimates double-effect, generating false "synthetic-rescue."
**Symptom:** GI scores positive for pairs of essential cell-cycle genes; biologically unexpected.
**Fix:** Use log-space (LFC) GI scoring rather than linear; saturation is less severe in log-space. Alternative: model with logistic / saturable response curve.

### Library skew amplifying noise

**Trigger:** Inzolia library has uneven cassette representation; some pairs at 10x lower coverage than others.
**Mechanism:** Standard library QC (Gini, skew) applies; low-coverage cassettes yield noisier LFCs.
**Symptom:** GI z-scores vary 2-3x across cassettes targeting the same pair.
**Fix:** Standard library QC; for low-coverage pairs, aggregate fewer cassettes but with more sequencing depth; or drop low-coverage pairs from analysis.

## Cross-Modality Validation

For high-stakes synthetic-lethal hits (drug-target nomination), validate by:

1. **Orthogonal chemistry:** Re-validate with Cas9 if Cas12a, or vice versa
2. **Arrayed validation:** Single-knock-out arrayed setup with same cell line; quantify proliferation
3. **CRISPRi orthogonal:** Use dCas9-KRAB to confirm knockdown phenotype (no DNA damage)
4. **Pharmacological:** Inhibit paralog with drug; confirms target accessibility for drug development

## Quantitative Thresholds

| Threshold | Value | Source / Rationale |
|-----------|-------|--------------------|
| Synthetic lethal GI z-score | <-2 | Standard convention |
| Synthetic rescue GI z-score | >2 | Standard convention |
| No interaction | -1 to +1 | Within additive expectation |
| Cas9 paired-screen cassette count per pair | 4-6 | Standard library convention |
| Cas12a 4-guide arrays per paralog pair (Inzolia) | 2 (2 guides per gene, order swapped) | Esmaeili Anvar 2024 |
| Singletons in combinatorial library | At least 4-6 per single gene | For stable expected_additive |
| Cells per cassette for stable GI | 500+ at infection | Standard pooled-screen coverage |
| Cas12a editing efficiency for inclusion | >50% | Below = unreliable signal |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| Dual-sgRNA construct acts as single | Recombination between repeated U6/tracr elements | Use pPapi (orthologous SaCas9 + SpCas9, U6 + H1) |
| Cas12a low editing | Locus-specific inefficiency | Pilot loci first; use enCas12a |
| Cannot compute GI | No singletons in library | Re-design to include all-singletons |
| GI scores noisy | Library skew | Standard library QC; aggregate cassettes |
| Many false "rescue" GIs | Saturation in linear-space | Use log-space (LFC) GI scoring |
| Drug-target paralog shows no GI in screen | Cell-line-specific buffering | Cross-validate with multiple lines |

## References

- Najm FJ et al. 2018. *Nat Biotechnol* 36:179. Big Papi paired-Cas9 platform.
- DeWeirdt PC et al. 2021. *Nat Biotechnol* 39:94. enAsCas12a multiplex.
- Esmaeili Anvar N et al. 2024. *Nat Commun* 15:3577. in4mer / Inzolia paralog library.
- Dede M et al. 2020. *Genome Biol* 21:262. Paralog buffering in Cas9 screens.
- Thompson NA et al. 2021. *Nat Commun* 12:1302. Combinatorial CRISPR screen identifying paralog fitness effects.
- Boettcher M et al. 2018. *Nat Biotechnol* 36:170. Dual CRISPR activation + knockout directional genetic-interaction screen.
- Horlbeck MA et al. 2018. *Cell* 174:953-967. CRISPRi combinatorial genetic-interaction map; paralog buffering as a co-essentiality pattern was characterized more directly in Dede 2020 *Genome Biol* 21:262 and Gonatopoulos-Pournatzis 2020 *Nat Biotechnol* 38:638.

## Related Skills

- crispr-screens/library-design - Inzolia / in4mer / Big Papi library design
- crispr-screens/screen-qc - Library QC including cassette skew
- crispr-screens/mageck-analysis - MAGeCK MLE with interaction terms
- crispr-screens/hit-calling - Cross-method analysis of combinatorial data
- crispr-screens/perturb-seq-analysis - Combinatorial Perturb-seq
- crispr-screens/copy-number-correction - Pre-correction for cancer-line combinatorial screens
- crispr-screens/in-vivo-screens - In-vivo paralog screens
- pathway-analysis/go-enrichment - Functional analysis of GI clusters
<!-- END FILE: crispr-screens/combinatorial-screens/SKILL.md -->

## 子目录：crispr-screens/copy-number-correction

<!-- BEGIN FILE: crispr-screens/copy-number-correction/SKILL.md -->
---
name: bio-crispr-screens-copy-number-correction
description: Corrects the gene-independent copy-number artifact in CRISPR-Cas9 screens (Aguirre 2016 / Munoz 2016 Cancer Discov) where amplified loci appear essential from DNA-damage burden of simultaneous cuts. Covers the gene-independent DNA-damage / G2-arrest mechanism, CRISPRcleanR (Iorio 2018) unsupervised pre-hoc correction, CERES (Meyers 2017) joint CN + gene-effect model, Chronos (Dempster 2021) DepMap-standard population-dynamics + CN model with lowest residual bias, the decision tree by data availability, the Spearman LFC-vs-CN diagnostic, focal-amplification examples (ERBB2 in HER2+, MYC in colorectal, FGFR1 in head and neck), and CRISPRi/a alternatives that bypass the artifact. Use when screening cancer cell lines, diagnosing essentiality at amplified loci, choosing CRISPRcleanR / CERES / Chronos, deciding whether CN correction is needed before MAGeCK / BAGEL2 / drugZ, or switching from Cas9 to CRISPRi.
tool_type: mixed
primary_tool: CRISPRcleanR
---

## Version Compatibility

Reference examples tested with: CRISPRcleanR 3.0+ (R; github.com/francescojm/CRISPRcleanR), Chronos 2.0+ (https://github.com/broadinstitute/chronos), CERES (legacy, superseded by Chronos), pandas 2.2+, numpy 1.26+, scipy 1.12+.

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('CRISPRcleanR')`; `?ccr.GWclean`
- Python: `pip show crispr_chronos`; `python -c 'import chronos; print(chronos.__file__)'`

If code throws ImportError, AttributeError, or TypeError, introspect the installed package and adapt the example to match the actual API rather than retrying.

## Copy-Number Bias Correction in CRISPR Screens

**"Correct copy-number artifacts in my cancer-cell-line screen"** -> Identify gene-independent depletion at amplified loci, apply CRISPRcleanR (pre-hoc, unsupervised, position-based) or Chronos (joint model, supervised with CN profile) to remove the artifact, then proceed to hit calling on corrected data.

- R: `CRISPRcleanR::ccr.GWclean()` for unsupervised pre-hoc correction (no CN profile required)
- Python: Chronos (`crispr_chronos`) for joint cell-population dynamics + CN modeling
- Python: CERES (legacy, superseded by Chronos)

## The Copy-Number Artifact (Mechanism)

**Aguirre AJ et al 2016 *Cancer Discov* 6:914** and **Munoz DM et al 2016 *Cancer Discov* 6:900** demonstrated that focal amplification regions in cancer cell lines appear systematically "essential" in CRISPR-Cas9 screens, independent of the gene's actual biology. The mechanism:

1. A focal amplification creates 4-50+ copies of a genomic region.
2. Each sgRNA targeting a gene in that region cuts at all copies simultaneously.
3. Multiple cuts trigger a DNA-damage response and G2 arrest, in both TP53-mutant and TP53-wild-type lines but with larger magnitude in wild-type (Aguirre 2016).
4. Cells arrest in G2 phase; the sgRNA appears depleted because its bearer cells don't proliferate.
5. The depletion is proportional to the number of simultaneous cuts, not the gene's essentiality.

**Consequence:** ERBB2 appears essential in HER2-amplified SK-BR-3. MYC appears essential in MYC-amplified colorectal lines (10+ copies). FGFR1 appears essential in FGFR1-amplified head-and-neck lines. These are all false positives.

**Affects:** All Cas9-KO screens in cancer cell lines. Universal, not conditional. Cannot be remediated by sequencing depth, library size, or replicate count. Requires explicit correction.

The p53-dependence of Cas9-cut toxicity in general was characterized later, by Haapaniemi 2018 and Ihry 2018.

**Bypassed by:**
- CRISPRi (catalytically dead Cas9, no DNA damage) -> no artifact
- CRISPRa (catalytically dead Cas9) -> no artifact
- Base editing (single-strand nick + deaminase) -> reduced artifact
- Prime editing (nick + RT) -> reduced artifact

## Correction Method Decision Tree

| Available data | Recommended method | Why |
|----------------|---------------------|-----|
| Cell-line panel without matched CN profile | CRISPRcleanR | Unsupervised; uses genomic position only |
| Single cell line with matched WGS/SNP-array CN | CRISPRcleanR or Chronos | Either works; Chronos more rigorous |
| DepMap-scale (1000+ cell lines, longitudinal) | Chronos | Population-dynamics + screen quality + CN; DepMap quarterly standard |
| Single cell line, multi-timepoint | Chronos | Leverages longitudinal counts |
| Need to integrate with downstream MAGeCK | CRISPRcleanR (pre-hoc) | Outputs corrected counts for any downstream tool |
| Multiple cell lines + multiple batches | Chronos | Joint modeling of all dimensions |

## CRISPRcleanR (Iorio 2018) - Unsupervised Pre-Hoc

**Goal:** Correct copy-number bias without requiring matched CN profile by detecting position-based systematic enrichment / depletion patterns.

**Approach:** Order sgRNAs by chromosomal coordinate; detect segments where sgRNAs show systematic depletion (or enrichment) inconsistent with single-gene biology; shift these segments toward the global mean. The intuition: focal amplifications create depletion bands extending tens to hundreds of kb; non-amplified essential genes are punctate.

```r
library(CRISPRcleanR)

# Load library annotation (sgRNA -> chromosomal coordinates)
data(KY_Library_v1.0)   # KY library; replace with your library annotation
# OR use ccr.PrepareAnnotations() to make custom

# Load count data with first 2 cols: sgRNA, gene, then sample counts
counts <- read.table('counts.txt', header=TRUE, sep='\t')

# 1. Normalize and compute logFC
norm_counts <- ccr.NormfoldChanges(filename='counts.txt', min_reads=30,
                                     EXPname='my_screen',
                                     libraryAnnotation=KY_Library_v1.0)

# 2. Compute genome-sorted sgRNA fold changes
gw_log_fc <- ccr.logFCs2chromPos(norm_counts$logFCs,
                                   KY_Library_v1.0)

# 3. Apply CRISPRcleanR correction
corrected <- ccr.GWclean(gw_log_fc, display=TRUE, label='my_screen')
# Output: corrected$corrected_logFCs and corrected$segments
# corrected_logFCs can replace LFCs downstream

# 4. Re-derive corrected counts for downstream MAGeCK
corrected_counts <- ccr.correctCounts('my_screen',
                                        norm_counts$norm_counts,
                                        corrected,
                                        KY_Library_v1.0,
                                        OutDir='./')
```

**Key parameter:** `min_reads=30` is the lower-count threshold for inclusion. This must match the library-coverage strategy; too high removes legitimate guides, too low keeps noisy guides.

**Output:** Pre-corrected LFCs and counts that can be fed into MAGeCK / BAGEL2 / drugZ as if they were the original screen data. The correction is independent of CN profile (unsupervised) and works on cell lines without matched WGS.

## Chronos (Dempster 2021) - Joint Population-Dynamics + CN Model

**Goal:** Estimate gene fitness while jointly accounting for copy-number-driven depletion, screen quality, and longitudinal cell-population dynamics.

**Approach:** Model the cell population over time as an ODE driven by per-gene fitness effects; add a separate term for copy-number-driven depletion; estimate all parameters via maximum-likelihood with regularization. Outputs a "gene effect score" normalized against the empirical distributions of essential and non-essential reference genes.

```python
# Chronos (pip install crispr_chronos, or pip install git+https://github.com/broadinstitute/chronos)
import chronos
from chronos.hit_calling import get_probability_dependent

# Inputs
# 1. Counts: rows = sgRNA, columns = samples (per-timepoint per-cell-line)
# 2. Sequence map: sgRNA -> cell line -> sample timepoint
# 3. Guide-gene map
# 4. Copy-number profile per cell line (applied AFTER training, not at construction)

# All three inputs are dicts of DataFrame keyed by library name, not bare DataFrames.
model = chronos.Chronos(
    sequence_map={'screen': sequence_map},
    guide_gene_map={'screen': guide_gene_map},
    readcounts={'screen': counts_df},
)
model.train(nepochs=301)
gene_effects = model.gene_effect                      # attribute, not a method call

# Copy-number correction is a separate post-hoc step, not a constructor argument
gene_effects_cn = chronos.alternate_CN(gene_effects, copy_number_df)
gene_probabilities = get_probability_dependent(gene_effects_cn, negative_control_genes, positive_control_genes)
```

**DepMap convention:** A gene-effect score <-1 corresponds to "essential" in that cell line; <-0.5 is "depleting." Each DepMap release (quarterly) provides Chronos gene effects and probabilities.

**Critical:** Chronos benefits most from longitudinal data (multiple timepoints per cell line) but can run with multiple cell lines at a single timepoint. Copy number is optional: Chronos trains without it and `alternate_CN` applies the correction afterwards. For a single screen (one line, one timepoint) without a matched CN profile, use CRISPRcleanR instead.

## CERES (Legacy, Superseded by Chronos)

**Meyers RM et al 2017 *Nat Genet* 49:1779** introduced the first formal CN-correction method at DepMap scale. CERES decomposes per-sgRNA LFC as `sgRNA_efficacy * gene_effect - CN_term(copy_number)`, fitting jointly. Superseded by Chronos at DepMap in 2021 due to Chronos' better handling of screen quality and longitudinal data. CERES remains useful for cross-validation.

## Detect Uncorrected CN Bias

**Goal:** Verify that copy-number bias is corrected (or detect it in raw data).

**Approach:** For genes with matched CN profile, compute Spearman ρ between gene-level LFC and copy number. A negative correlation (-ρ) indicates amplified genes are depleted, i.e., CN artifact.

```python
import pandas as pd
from scipy.stats import spearmanr

def detect_cn_bias(gene_lfc_df, cn_df):
    '''Test whether gene-level LFC negatively correlates with copy number.
    A bias-free screen has Spearman rho near zero between CN and LFC.'''
    merged = gene_lfc_df.merge(cn_df, on='gene')
    rho, p = spearmanr(merged['copy_number'], merged['lfc'])
    return {
        'cn_lfc_rho': rho,
        'p_value': p,
        'amplified_mean_lfc': merged[merged['copy_number'] > 4]['lfc'].mean(),
        'diploid_mean_lfc': merged[(merged['copy_number'] >= 1.5) & (merged['copy_number'] <= 2.5)]['lfc'].mean(),
        'bias_present': rho < -0.1 and p < 0.01,
    }
```

**Threshold (operational convention):** Spearman ρ <-0.10 between LFC and CN indicates significant CN bias. Even modest amplifications generate detectable artifact. Run this diagnostic before AND after correction.

## Reconciliation: When CN Correction Fails

If post-CRISPRcleanR or post-Chronos the CN-LFC Spearman is still significantly negative, the correction is incomplete. Possible causes:

1. **Insufficient CN resolution:** A specific 4-copy region went undetected. Refine CN profile with deeper WGS.
2. **CRISPRcleanR position-based correction missed it:** The amplification is small relative to the segmentation algorithm's resolution. Use Chronos with matched CN profile.
3. **Genomic rearrangement creates a "ghost" amplification:** A complex rearrangement appears as normal CN but Cas9 cuts at multiple sites due to translocation breakpoints. Combine WGS structural variants with the analysis.
4. **Cell line has an unusually strong cut-toxicity response:** The artifact may persist; use CRISPRi screens for that line.

## Apply CN Correction to Pipeline

**Workflow:**

```
1. mageck count (raw counts)
2. screen-qc verification
3. CN diagnostic: Spearman of LFC vs CN (if CN profile available)
4. If bias detected:
   a. CRISPRcleanR (pre-hoc) -> corrected counts -> MAGeCK / BAGEL2 / drugZ
   OR
   b. Chronos (joint model with CN profile) -> gene effects directly
5. Re-diagnose: Spearman of CORRECTED LFC vs CN should be near zero
6. Hit calling
```

For DepMap-style large panels:
```
Chronos handles batch + CN + screen quality in one step; no pre-correction needed.
```

For Project Score-style panel (Behan 2019):
```
CRISPRcleanR was used historically; cross-check with Chronos when CN profile available.
```

## Failure Modes

### CRISPRcleanR removes legitimate essential signal

**Trigger:** A genuine essential gene happens to lie in a region with adjacent uncorrected non-essential signal; the segment-based correction includes the essential.
**Mechanism:** CRISPRcleanR's `ccr.GWclean()` segments sgRNAs by position; segments containing multiple genes with directional consistency are corrected as a unit.
**Symptom:** A known essential drops out of post-correction hit list.
**Fix:** Inspect segments manually; if a known essential was within a corrected segment, investigate. Cross-check with non-CN-corrected MAGeCK + BAGEL2 to see if essential was a hit pre-correction.

### Chronos fails on single-timepoint or single-cell-line data

**Trigger:** Chronos requires multiple timepoints (or multiple cell lines) for population-dynamics estimation.
**Mechanism:** Single observation per condition leaves model under-determined.
**Symptom:** Chronos errors out or produces flat gene-effect distributions.
**Fix:** Use CRISPRcleanR (which handles single-timepoint single-line); collect multi-timepoint data for Chronos.

### Spearman ρ still negative after CRISPRcleanR

**Trigger:** Amplification is too small or complex for the segment-based approach.
**Mechanism:** CRISPRcleanR detects systematic spatial patterns; isolated 4-copy regions can slip through.
**Symptom:** Post-correction Spearman ρ -0.05 to -0.10 between LFC and CN.
**Fix:** Refine CN profile (deeper WGS); apply Chronos with matched CN as alternative; or supplement with focal-amplification-aware methods.

### Cell line lacks matched CN profile

**Trigger:** Newly characterized line or rare patient-derived line; WGS not done.
**Mechanism:** Chronos requires CN as input; CRISPRcleanR doesn't but works better with it.
**Symptom:** Cannot apply Chronos; CRISPRcleanR less precise without supervised CN.
**Fix:** Run SNP-array (cheap, fast) or low-coverage WGS to obtain CN profile; in interim, use CRISPRcleanR unsupervised mode.

### CN amplification at non-coding region drives apparent essentiality

**Trigger:** Amplification at a gene-poor region; sgRNAs at edge genes get artifactually depleted.
**Mechanism:** Even non-essential genes adjacent to amplifications are depleted because the Cas9 cuts are at the amplified loci.
**Symptom:** Non-essential genes near amplification show LFC <0.
**Fix:** Inspect chromosomal position of "essential" hits; flag genes within 100 kb of known amplifications for orthogonal validation. This is the classic Aguirre 2016 observation.

## CRISPRi/a Alternative

**For variant-function or non-cancer-line essentiality screens, switching to CRISPRi (catalytically dead dCas9-KRAB) avoids the artifact entirely.** No DNA double-strand breaks = no DNA-damage G2 arrest = no copy-number-driven depletion.

| Approach | CN artifact | When to use |
|----------|--------------|-------------|
| Cas9 KO | YES; requires correction | Loss-of-function essentiality, traditional screens |
| CRISPRi | NO | Cancer lines with focal amps; knockdown of cuttable-toxic genes |
| CRISPRa | NO | Gain-of-function; activation screens |
| Base editing | Reduced (single-strand nick) | Variant function |
| Prime editing | Reduced | Precise edits |

See [[library-design]] for CRISPRi (Dolcetto) and CRISPRa (Calabrese) library options.

## Quantitative Thresholds

| Threshold | Value | Source / Rationale |
|-----------|-------|--------------------|
| Spearman ρ (CN vs LFC) | <-0.10 -> bias present | Operational convention |
| Copies for detectable artifact | >6 | Operational convention; response scales with copy number (Aguirre 2016) |
| CRISPRcleanR `min_reads` | 30 (default) | Iorio 2018; lower thresholds in low-coverage screens |
| Chronos gene-effect threshold for "essential" | <-1 (cancer line) | DepMap convention |
| Chronos gene-probability for "essential" | >0.5 | DepMap convention (dependency-probability cutoff) |
| Post-correction Spearman ρ | abs(ρ) <0.05 | Acceptable correction quality |
| Cell-line CN profile resolution | ≥SNP-array level | Below this, CRISPRcleanR unsupervised |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| Chronos errors on single-timepoint screen | Insufficient longitudinal data | Use CRISPRcleanR instead |
| CRISPRcleanR removes a known essential | Segment-based over-correction | Manually inspect segments; cross-check with non-corrected |
| Spearman ρ still -0.15 after correction | Method too coarse for the amp | Refine CN profile; use Chronos |
| ERBB2 listed as essential in SK-BR-3 | Uncorrected HER2 amplification | Always apply correction before hit calling |
| CN profile missing for newly characterized line | Profile not generated | Run SNP-array / low-coverage WGS |
| Hits restricted to non-amplified regions only | Over-correction | Reduce CRISPRcleanR aggressiveness; check known biology |

## References

- Aguirre AJ et al. 2016. *Cancer Discov* 6:914. Copy-number gene-independent toxicity.
- Munoz DM et al. 2016. *Cancer Discov* 6:900. CN amplification CRISPR artifacts.
- Haapaniemi E et al. 2018. *Nat Med* 24:927. Cas9 cutting induces a p53-mediated DNA-damage response.
- Ihry RJ et al. 2018. *Nat Med* 24:939. p53 inhibits Cas9 engineering in human pluripotent stem cells.
- Meyers RM et al. 2017. *Nat Genet* 49:1779. CERES; first formal CN correction at DepMap scale.
- Iorio F et al. 2018. *BMC Genomics* 19:604. CRISPRcleanR.
- Dempster JM et al. 2021. *Genome Biol* 22:343. Chronos.
- Behan FM et al. 2019. *Nature* 568:511. Project Score with CRISPRcleanR-corrected data.
- Pacini C et al. 2021. *Nat Commun* 12:1661. Integrated cross-study dependencies; DepMap quality scoring.
- DepMap Q4 2024+ data releases. https://depmap.org/portal/

## Related Skills

- crispr-screens/screen-qc - CN-LFC Spearman diagnostic; pre-correction QC
- crispr-screens/library-design - Switch to Dolcetto (CRISPRi) to bypass artifact
- crispr-screens/mageck-analysis - MAGeCK on CRISPRcleanR-corrected counts
- crispr-screens/bagel-essentiality - BAGEL2 on CRISPRcleanR-corrected counts
- crispr-screens/hit-calling - Cancer-line hit calling with Chronos
- crispr-screens/batch-correction - Chronos handles batch + CN jointly
- crispr-screens/jacks-analysis - JACKS does not handle CN bias
- clinical-databases/clinvar-lookup - Variant annotation downstream
- copy-number/copy-ratio-segmentation - CN profile derivation upstream
<!-- END FILE: crispr-screens/copy-number-correction/SKILL.md -->

## 子目录：crispr-screens/crispresso-editing

<!-- BEGIN FILE: crispr-screens/crispresso-editing/SKILL.md -->
---
name: bio-crispr-screens-crispresso-editing
description: Quantifies CRISPR editing outcomes with CRISPResso2 (Clement 2019 Nat Biotechnol) across Cas9-nuclease (indels, HDR), CBE and ABE base editors (target conversion + bystander), and prime editor (pegRNA-templated) modes. Covers single-amplicon (CRISPResso), multi-sample batch (CRISPRessoBatch), pooled-amplicon (CRISPRessoPooled), WGS off-target (CRISPRessoWGS), and sample-comparison (CRISPRessoCompare) workflows; quantification-window math that controls what is called edited; substitution-vs-indel diagnostic to distinguish BE from Cas9 contamination; MMEJ deletion pattern interpretation; allele-frequency tables; and failure modes from amplicon misalignment or contamination. Use when quantifying editing from amplicon sequencing, choosing CRISPResso mode by design, distinguishing intended edits from bystanders and indel byproducts, debugging low-alignment runs, or generating publication-grade editing reports.
tool_type: cli
primary_tool: CRISPResso2
---

## Version Compatibility

Reference examples tested with: CRISPResso2 2.2.14+ (pinellolab/CRISPResso2), pandas 2.2+, numpy 1.26+, matplotlib 3.8+.

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `CRISPResso --version`; `CRISPRessoBatch --help`; `CRISPRessoPooled --help`; `CRISPRessoWGS --help`; `CRISPRessoCompare --help`
- Python: `from CRISPResso2 import ...`

If code throws ImportError, AttributeError, or TypeError, introspect the installed package and adapt the example to match the actual API rather than retrying.

## CRISPResso2 Editing Quantification

**"Quantify CRISPR editing from my amplicon sequencing"** -> Align amplicon reads against the reference, classify each read as unmodified / NHEJ / HDR / base-edited / prime-edited within the quantification window, and report per-edit-type frequencies, indel size distributions, allele-frequency tables, and substitution-position profiles.

- CLI: `CRISPResso` -- single amplicon, single sample
- CLI: `CRISPRessoBatch` -- multi-sample with per-sample parameters
- CLI: `CRISPRessoPooled` -- multi-amplicon pooled amplicon sequencing
- CLI: `CRISPRessoWGS` -- off-target quantification from whole-genome BAM
- CLI: `CRISPRessoCompare` -- pairwise outcome comparison (e.g., treated vs untreated)

## Mode Decision Tree

| Experimental design | Mode | Key parameters |
|---------------------|------|----------------|
| Single amplicon, single sample (e.g. pilot edit validation) | `CRISPResso` | `--amplicon_seq`, `--guide_seq` |
| Same amplicon, many samples (e.g. timecourse, dose response) | `CRISPRessoBatch` | `--batch_settings` table |
| Many amplicons, pooled in one library (e.g. arrayed validation pool) | `CRISPRessoPooled` | `--amplicons_file` |
| Off-target survey from whole-genome BAM | `CRISPRessoWGS` | `--bam_file`, `--reference_file`, `--region_file` |
| Comparing two CRISPResso runs (e.g. condition A vs B) | `CRISPRessoCompare` | two positional output folders |
| HDR / knock-in validation | `CRISPResso` with `--expected_hdr_amplicon_seq` | Same as base CRISPResso |
| Cytosine base editor (C->T) | `CRISPResso --base_editor_output` | `--conversion_nuc_from C --conversion_nuc_to T` |
| Adenine base editor (A->G) | `CRISPResso --base_editor_output` | `--conversion_nuc_from A --conversion_nuc_to G` |
| Prime editor (templated edit) | `CRISPResso` with pegRNA parameters | `--prime_editing_pegRNA_spacer_seq`, `--prime_editing_pegRNA_extension_seq`, `--prime_editing_pegRNA_scaffold_seq` |

**Fails when:**
- Pooled-amplicon mode applied to amplicons that share primer sequences -- reads get misassigned.
- Base editor mode without specifying `--conversion_nuc_from`/`--conversion_nuc_to` -- defaults assume CBE (C->T); ABE runs will misclassify.
- Prime editor mode without `--prime_editing_pegRNA_extension_seq` -- the RTT template is missing, no edit is detectable.

## The Quantification Window

**Why this matters for postdoc-level use:** CRISPResso classifies reads as "edited" or "unmodified" based on whether *modifications fall inside the quantification window* (not the whole amplicon). The window is centered on the predicted cut site (Cas9: 3 bp upstream of PAM; Cas12a: 18 bp downstream of PAM) with a default size of 1. `--quantification_window_size N` extends N bp on EACH side, so the window is 2N bp wide.

```bash
# Default Cas9 setup
--quantification_window_size 1                  # 1-bp window at cut site
--quantification_window_center -3               # 3 bp upstream of PAM

# Base editor: widen window to cover editing positions 4-8
--quantification_window_size 10                 # 10 bp each side (20 bp total)
--quantification_window_center -10              # center on the editing window
```

**Consequences of mis-sized window:**
- Too narrow: misses edits at HDR positions or far bystanders; underestimates editing
- Too wide: includes random sequencing errors; inflates editing rate
- Wrong center: edits at correct position are scored as outside the window

For base editing screens a widened window is conventional; CRISPResso2's own base-editor guidance uses `--quantification_window_center -17` with a window sized to span the editing positions. For prime editing with multi-base templated edits, widen to encompass the entire edit region.

## Single-Amplicon Cas9 Editing

**Goal:** Quantify indel frequencies and HDR efficiency from a single target site.

**Approach:** Align FASTQ reads to the reference and (optional) expected-HDR amplicon, classify each read, and report aggregated statistics.

```bash
CRISPResso \
    --fastq_r1 sample_R1.fastq.gz \
    --fastq_r2 sample_R2.fastq.gz \
    --amplicon_seq <amplicon_sequence_ref_genome> \
    --guide_seq <20nt_protospacer_no_PAM> \
    --expected_hdr_amplicon_seq <edited_amplicon_for_HDR> \  # OPTIONAL
    --quantification_window_size 1 \
    --quantification_window_center -3 \
    --min_average_read_quality 30 \                          # Phred quality filter
    --output_folder sample_results \
    --name sample_id

# Outputs:
#   sample_results/<name>/CRISPResso_mapping_statistics.txt
#   sample_results/<name>/CRISPResso_quantification_of_editing_frequency.txt
#   sample_results/<name>/Alleles_frequency_table.zip
#   sample_results/<name>/3a.<ref>.Indel_size_distribution.pdf
#   sample_results/<name>/4b.<ref>.Insertion_deletion_substitution_locations.pdf
#   (PDF by default; add --save_also_png for PNG)
```

**Key outputs:**

| File | Content |
|------|---------|
| `CRISPResso_mapping_statistics.txt` | Tab-separated, one data row: READS IN INPUTS, READS AFTER PREPROCESSING, READS ALIGNED, N_COMPUTED_ALN, ... (no percentage columns) |
| `CRISPResso_quantification_of_editing_frequency.txt` | % unmodified, % NHEJ, % HDR (if expected), per-edit-class breakdown |
| `Alleles_frequency_table.zip` | Per-allele sequences and frequencies (allele-level resolution) |
| `Nucleotide_percentage_table.txt` | Per-position A/C/G/T/- frequencies (substitutions + deletions) |
| `Quantification_window_nucleotide_percentage_table.txt` | Same, restricted to quantification window (base-editor analysis) |


## Base Editor Quantification

**Goal:** Distinguish target base conversion from bystander edits and indel byproducts.

**Approach:** Run CRISPResso with `--base_editor_output` flag and specify the conversion direction; widen the quantification window to cover the editing window.

```bash
# Cytosine Base Editor (CBE): C->T conversion
CRISPResso \
    --fastq_r1 cbe_sample.fastq.gz \
    --amplicon_seq <amplicon_seq> \
    --guide_seq <20nt_protospacer> \
    --base_editor_output \
    --conversion_nuc_from C \
    --conversion_nuc_to T \
    --quantification_window_size 10 \
    --quantification_window_center -10 \
    --output_folder cbe_results \
    --name cbe_sample

# Adenine Base Editor (ABE): A->G conversion
CRISPResso \
    --fastq_r1 abe_sample.fastq.gz \
    --amplicon_seq <amplicon_seq> \
    --guide_seq <20nt_protospacer> \
    --base_editor_output \
    --conversion_nuc_from A \
    --conversion_nuc_to G \
    --quantification_window_size 10 \
    --quantification_window_center -10 \
    --output_folder abe_results \
    --name abe_sample
```

**Reading the output:**

| Metric | Where | Interpretation |
|--------|-------|----------------|
| Target editing % | `Quantification_window_nucleotide_percentage_table.txt`, target C/A row | Primary endpoint |
| Bystander editing % | Same table, other C/A positions in window | Off-target byproduct in window |
| Indel rate | `CRISPResso_quantification_of_editing_frequency.txt` | Cas9-like cut artifacts; should be <5% for clean BE |
| Substitution-vs-indel ratio | Derived | Ratio >10 indicates clean BE; <3 indicates cut-mediated mutagenesis instead |

**Critical:** Bystander editing is intrinsic to base editors (the deaminase acts across a 5-nt window); it is not noise. Report bystander rates alongside target rates. See [[base-editing-analysis]] for variant-call implications.

## Prime Editor Quantification

**Goal:** Quantify pegRNA-templated edits versus indel byproducts and partial edits.

**Approach:** Provide spacer, extension (PBS + RTT), and scaffold sequences; CRISPResso identifies reads matching the intended edit.

```bash
CRISPResso \
    --fastq_r1 pe_sample.fastq.gz \
    --amplicon_seq <amplicon_seq> \
    --guide_seq <20nt_protospacer> \
    --prime_editing_pegRNA_spacer_seq <20nt_protospacer> \
    --prime_editing_pegRNA_extension_seq <RTT+PBS_sequence> \
    --prime_editing_pegRNA_scaffold_seq <scaffold_sequence> \
    --output_folder pe_results \
    --name pe_sample

# Output adds:
#   Prime-editing outcomes are extra amplicon rows (Reference / Prime-edited / Scaffold-incorporated)
#   inside CRISPResso_quantification_of_editing_frequency.txt
```

**Reading prime-editor output:**

| Metric | Interpretation |
|--------|----------------|
| Intended edit % | The pegRNA-encoded edit was correctly installed |
| Scaffold incorporation % | Reverse transcription read into scaffold instead of stopping at edit; failure mode |
| Indel % | Nick-only editing without templated repair; common at low-PE-activity sites |
| Unmodified % | Read matches the reference exactly |

A high-quality prime-edit run shows intended-edit fraction >5% and scaffold incorporation <2%. See [[prime-editing-screens]] for pegRNA design rules.

## Batch Mode (Multi-Sample, Same Amplicon)

**Goal:** Process tens to hundreds of samples with same amplicon design (e.g., a timecourse, dose response, or replicate panel).

**Approach:** Provide a tab-separated batch settings file with per-sample parameters; CRISPRessoBatch runs all in parallel.

```bash
# batch_settings.txt (tab-separated, headers required)
# name    fastq_r1                fastq_r2                amplicon_seq    guide_seq
# t0      t0_R1.fq.gz             t0_R2.fq.gz             ACGT...         GUIDE
# t6      t6_R1.fq.gz             t6_R2.fq.gz             ACGT...         GUIDE
# t12     t12_R1.fq.gz            t12_R2.fq.gz            ACGT...         GUIDE
# t24     t24_R1.fq.gz            t24_R2.fq.gz            ACGT...         GUIDE

CRISPRessoBatch \
    --batch_settings batch_settings.txt \
    --batch_output_folder batch_run \
    --skip_failed \
    --n_processes 8

# Outputs:
#   batch_run/CRISPRessoBatch_RUNNING_LOG.txt
#   batch_run/CRISPRessoBatch_quantification_of_editing_frequency.txt  (aggregated)
#   batch_run/CRISPResso_on_<name>/ for each sample
```

## Pooled-Amplicon Mode

**Goal:** Process multi-amplicon sequencing libraries (e.g., arrayed validation pools).

**Approach:** Provide an amplicon table with one row per target; CRISPRessoPooled de-multiplexes reads to the correct amplicon.

```bash
# amplicons.txt (tab-separated; header may vary by CRISPResso2 version)
# amplicon_name  amplicon_seq    guide_seq
# BRCA1_exon3    ACGT...         GUIDE1
# TP53_exon7     ACGT...         GUIDE2
# KRAS_codon12   ACGT...         GUIDE3

CRISPRessoPooled \
    --fastq_r1 pooled_R1.fastq.gz \
    --fastq_r2 pooled_R2.fastq.gz \
    --amplicons_file amplicons.txt \
    --output_folder pooled_run \
    --n_processes 8

# Outputs:
#   pooled_run/SAMPLES_QUANTIFICATION_SUMMARY.txt
#   pooled_run/CRISPResso_on_<amplicon>/ for each amplicon
```

**Failure mode:** Amplicons with shared primer regions get reads assigned to whichever amplicon comes first. Design primers with ≥3-bp distinguishing regions or use unique molecular identifiers.

## WGS Off-Target Mode

**Goal:** Quantify off-target editing from whole-genome sequencing.

**Approach:** Provide BAM file + reference + BED file of suspected off-target sites; CRISPResso extracts reads from each region and quantifies edits.

```bash
CRISPRessoWGS \
    --bam aligned.bam \
    --reference genome.fa \
    --region_file off_targets.bed \
    --output_folder wgs_run \
    --n_processes 8
```

**Use case:** Validate empirically that an in vivo / clinical-grade edit has minimal off-target activity (combine with GUIDE-seq or CIRCLE-seq predicted sites).

## Parse Output in Python

**Goal:** Pull editing metrics into downstream analysis or reports.

**Approach:** Read the tab-separated quantification files and the JSON metadata.

```python
import pandas as pd
import json
from pathlib import Path

def parse_crispresso(output_dir):
    '''Extract key metrics from CRISPResso output directory.'''
    out = {}
    # Mapping statistics
    map_stats = {}
    with open(Path(output_dir) / 'CRISPResso_mapping_statistics.txt') as f:
        for line in f:
            k, v = line.strip().split('\t')
            map_stats[k] = v
    out['mapping_pct'] = float(map_stats.get('READS_ALIGNED_PERCENTAGE', 'nan'))
    out['reads_aligned'] = int(map_stats.get('READS_ALIGNED', '0'))
    # Editing quantification
    quant = pd.read_csv(Path(output_dir) / 'CRISPResso_quantification_of_editing_frequency.txt', sep='\t')
    out['editing_quant'] = quant.set_index('Amplicon').to_dict()
    # JSON metadata
    info_path = Path(output_dir) / 'CRISPResso2_info.json'
    if info_path.exists():
        out['info'] = json.loads(info_path.read_text())
    return out
```

## Failure Modes

### Low alignment rate (<50%)

**Trigger:** Wrong amplicon sequence (off by one nt, wrong strand, primer-trimmed vs untrimmed).
**Mechanism:** CRISPResso fails to align reads beyond the amplicon edges; discards as unmappable.
**Symptom:** `READS_ALIGNED_PERCENTAGE` <50%; per-position coverage drops at amplicon edges.
**Fix:** Re-derive amplicon from genome at primer-trimmed boundaries; verify strand orientation; check that primers are NOT included in `--amplicon_seq`.

### High substitution rate but low indel (Cas9 sample)

**Trigger:** Sample contamination with adjacent amplicon, primer-dimer, or sequencing error inflation.
**Mechanism:** Random substitutions inflate the per-position substitution rate without true indels.
**Symptom:** Substitutions >2% at base positions outside the cut site; alignment metrics look fine.
**Fix:** Increase `--min_average_read_quality` to 30+; filter contaminating amplicons; check primer-dimer in `CRISPResso_RUNNING_LOG.txt`.

### Bystander C/A editing inflates "editing efficiency"

**Trigger:** Base-editor sample with wide quantification window; bystander Cs at adjacent positions counted as edits.
**Mechanism:** Default `--quantification_window_size 10` includes all positions in editing window; bystander edits are real but distinct from target edit.
**Symptom:** Editing efficiency 80%+ but target SNV is 30%; bystander rate is 50%.
**Fix:** Always read the per-position table (`Quantification_window_nucleotide_percentage_table.txt`), not just the aggregate. Report target and bystander rates separately. See [[base-editing-analysis]].

### Prime editor sample with high scaffold incorporation

**Trigger:** RTT is too short relative to PBS, or pegRNA stops short.
**Mechanism:** Reverse transcriptase reads past the edit into scaffold sequence; product is detectable but undesired.
**Symptom:** Scaffold incorporation >5%; intended edit efficiency lower than expected.
**Fix:** Re-design pegRNA with longer RTT; verify with PRIDICT2 (see [[prime-editing-screens]]).

### MMEJ deletion misclassified as NHEJ

**Trigger:** Deletions with microhomology at junction; CRISPResso reports them as indels but doesn't distinguish MMEJ.
**Mechanism:** MMEJ creates predictable deletions using flanking microhomologies; biologically distinct from random NHEJ.
**Symptom:** Recurring same-size deletions in allele table (e.g., -7 bp deletion in 30% of reads).
**Fix:** Examine `Alleles_frequency_table` for over-represented allele patterns; flag MMEJ-mediated deletions for interpretation (these may be inferred from indel hotspots).

## Quantitative Thresholds

| Threshold | Value | Source / Rationale |
|-----------|-------|--------------------|
| Cas9 editing efficiency (functional KO) | >70% indels | Field convention; below this, KO is incomplete |
| Indel rate (clean base editor) | <5% | Field convention; >5% = unwanted cut activity |
| Target conversion (CBE) | >30% | Variable by target; below this, screen power is poor |
| Target conversion (ABE) | >30% | ABE typically lower per-base than CBE |
| Bystander rate (BE) | <10% acceptable; <5% ideal | Application-dependent; for variant function studies, must be controlled |
| Intended-edit % (prime editor) | >5% per-edit | Field convention; can be 50%+ at favorable sites |
| Scaffold incorporation (PE) | <2% | High-quality pegRNA design |
| Alignment rate | >85% | Below this, amplicon design or contamination issue |
| Minimum read quality | Phred 30 | Q30 Illumina base-call-accuracy standard |
| Quantification window size (Cas9) | 1 | Clement 2019 default; precise cut-site analysis |
| Quantification window size (BE) | 10 | Cover editing window positions 4-13 |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| Alignment rate <50% | Wrong amplicon sequence | Re-verify; primers should NOT be in amplicon_seq |
| All reads "modified" | Misaligned reference | Check amplicon strand; reverse-complement test |
| BE shows mostly indels | Cas9 contamination or wrong protein | Re-derive cell line origin; check Cas9 vs nCas9-BE3 |
| Inconsistent batch results | Different amplicon_seq per sample | Use CRISPRessoBatch with consistent amplicon |
| Pooled-amplicon misassignment | Primer overlap between amplicons | Re-design with ≥3-bp distinguishing regions |
| Out-of-window edits ignored | Window too narrow | Increase `--quantification_window_size` |
| Scaffold incorporation high (PE) | RTT too short | Re-design pegRNA |
| Allele frequency dominated by 1 read | Low input / clonal | Verify input cell count; rerun if singleton |

## References

- Clement K et al. 2019. *Nat Biotechnol* 37:224. CRISPResso2 algorithm and modes.
- Pinello L et al. 2016. *Nat Biotechnol* 34:695. Original CRISPResso.
- Anzalone AV et al. 2019. *Nature* 576:149. Prime editing (PE-1/PE-2/PE-3).
- Komor AC et al. 2016. *Nature* 533:420. Base editing (BE3).
- Findlay GM et al. 2018. *Nature* 562:217. Saturation genome editing.

## Related Skills

- crispr-screens/base-editing-analysis - Variant-function analysis using CRISPResso2 BE output
- crispr-screens/prime-editing-screens - PRIDICT2 pegRNA design + PE-tiling
- crispr-screens/library-design - sgRNA / pegRNA design for editing screens
- crispr-screens/screen-qc - Editing-efficiency QC for variant interpretation
- variant-calling/variant-annotation - Annotate detected variants downstream
- read-alignment/bwa-alignment - For WGS off-target alignment input
<!-- END FILE: crispr-screens/crispresso-editing/SKILL.md -->

## 子目录：crispr-screens/drugz-chemogenomic

<!-- BEGIN FILE: crispr-screens/drugz-chemogenomic/SKILL.md -->
---
name: bio-crispr-screens-drugz-chemogenomic
description: Analyzes CRISPR drug-modifier (chemogenomic) screens with drugZ (Colic et al. 2019 Genome Med), a bidirectional Z-score method that identifies synthetic-lethal sensitizing genes and resistance-conferring suppressor genes from vehicle vs drug comparisons. Covers vehicle-anchored design (not Day-0), the bidirectional Z math giving greater sensitivity to small-effect hits than MAGeCK / STARS / edgeR / RIGER on drug screens, per-gene sumZ and normZ, synth (sensitizer) vs supp (suppressor) FDR, multi-dose handling, integration with control sgRNAs, and comparison with MAGeCK MLE with dose covariate. Use when running a drug-modifier CRISPR screen, identifying sensitizing or resistance genes for a drug candidate, choosing drugZ vs MAGeCK MLE for chemogenomic analysis, troubleshooting low-effect drug screens where MAGeCK lacks sensitivity, or designing a drug-screen layout (vehicle vs drug arms).
tool_type: cli
primary_tool: drugZ
---

## Version Compatibility

Reference examples tested with: drugZ Aug-2019+ (hart-lab/drugz; Python 3.6+), MAGeCK 0.5.9+, pandas 2.2+, numpy 1.26+, scipy 1.12+, statsmodels 0.14+, matplotlib 3.8+.

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `python drugz.py --help` (the repo has no setup.py, so there is no `drugz` console script)
- GitHub: install via `git clone https://github.com/hart-lab/drugz`

If code throws ImportError, AttributeError, or TypeError, introspect the installed package and adapt the example to match the actual API rather than retrying.

## drugZ Chemogenomic Analysis

**"Identify genes that sensitize or confer resistance to my drug in a CRISPR screen"** -> Compare drug-treated vs vehicle-treated arms (NOT Day-0 baseline) using bidirectional Z-scores per sgRNA, sum to per-gene normalized Z, and rank genes for sensitizer (synthetic lethal) vs suppressor (resistance) phenotype.

- CLI: `python drugz.py -i counts.txt -o drugz.txt -c Vehicle_r1,Vehicle_r2 -x Drug_r1,Drug_r2`
- Python: programmatic via `drugz.drugZ_analysis(args)` (takes an argparse Namespace)
- Workflow: vehicle-anchored counts -> Z-scoring -> per-gene summation -> direction-specific FDR

## Why drugZ for Drug Screens (not MAGeCK)

| Property | drugZ | MAGeCK RRA | MAGeCK MLE |
|----------|-------|------------|-------------|
| Bidirectional sensitivity | YES (sensitizer + resistance same scale) | Asymmetric (neg/pos separately) | Asymmetric |
| Drug-anchored baseline | YES (drug vs vehicle) | Either (drug vs vehicle or vs Day 0) | Either |
| Sensitivity to small effects | Highest (bidirectional Z; Colic et al. 2019) | Moderate | Moderate |
| Statistical framework | Empirical-Bayes windowed Z-score on guide-level log fold change | NB + alpha-RRA | NB GLM with design matrix |
| Handles guide-level noise | sgRNA-level z aggregation | Rank-based aggregation | Built-in guide-efficacy term (optional) |
| Best for | Drug-modifier / chemogenomic screens | General essentiality / standard 2-condition | Time course / multi-condition |

**Why MAGeCK is suboptimal for drug screens:** MAGeCK's RRA was designed for two-condition essentiality; drug-vs-vehicle screens often have small effect sizes (10-30% sgRNA shift) that RRA rank-based aggregation under-detects. drugZ uses parametric Z-scoring tuned for these small effects.

**Benchmark (Colic et al. 2019):** On DNA-damage-response chemogenomic screens, drugZ hits were far more strongly enriched for the expected pathway (DDR) than STARS, MAGeCK, edgeR or RIGER hits across FDR thresholds, reflecting better sensitivity to the moderate fitness defects typical of drug-gene interactions. Compare methods on expected-pathway enrichment, not raw hit count.

## The drugZ Algorithm (under the hood)

1. For each sgRNA, compute log2-fold-change drug vs vehicle: `LFC_drug_vs_veh`
2. Compute an empirical-Bayes Z per sgRNA: `Z = LFC / eb_std`, where `eb_std` is the standard deviation of a sliding window of guides with similar control abundance (`--half_window_size`, default 500), smoothed monotonically
3. Per gene, sum Z across all sgRNAs targeting it: `sumZ = sum(Z_sgRNA)`
4. Normalize and re-standardize across genes: `normZ = zscore(sumZ / sqrt(numObs))`
5. Compute a one-sided p-value per direction: synth (sensitizer = negative normZ) and supp (resistance = positive normZ)
6. Benjamini-Hochberg FDR correction per direction

**Critical:** Vehicle vs drug, NOT Day 0 vs drug. Day-0 baseline conflates proliferation effects with drug effects.

## Run drugZ on a Drug-Modifier Screen

**Goal:** Quantify per-gene sensitizing and suppressor effects from a chemogenomic screen.

**Approach:** Run `drugz.py` with vehicle and drug sample columns; output per-gene sumZ, normZ, and direction-specific p-values + FDR.

```bash
git clone https://github.com/hart-lab/drugz
cd drugz

# Standard drug screen comparison:
# Vehicle (DMSO or carrier) replicates: Veh_r1, Veh_r2, Veh_r3
# Drug-treated replicates: Drug_r1, Drug_r2, Drug_r3

python drugz.py \
    -i counts.txt \                       # input read-count file (tab-separated)
    -o drugz_output.txt \                  # output file
    -c Veh_r1,Veh_r2,Veh_r3 \              # control samples (comma-separated)
    -x Drug_r1,Drug_r2,Drug_r3 \           # treated samples (comma-separated)
    -r RPS3,RPL11,EIF3A \                  # OPTIONAL: comma-delimited GENE NAMES to exclude (not a file)
    -p 5                                   # pseudocount (default 5)

# Output: drugz_output.txt with columns:
#   GENE, sumZ, numObs, normZ, pval_synth, rank_synth, fdr_synth, pval_supp, rank_supp, fdr_supp
```

**Output columns:**

| Column | Meaning |
|--------|---------|
| `GENE` | Gene symbol |
| `numObs` | Number of non-zero guide x replicate observations |
| `sumZ` | Summed per-sgRNA Z-score |
| `normZ` | sumZ / sqrt(numObs), re-standardized across genes |
| `pval_synth` | One-sided p-value for sensitizer (negative effect; gene KO sensitizes to drug) |
| `rank_synth` | Rank for sensitizers |
| `fdr_synth` | BH-corrected FDR for sensitizers |
| `pval_supp` | One-sided p-value for suppressor (positive effect; gene KO confers resistance) |
| `rank_supp` | Rank for suppressors |
| `fdr_supp` | BH-corrected FDR for suppressors |

**Interpretation:**
- Sensitizers (synthetic lethal): `fdr_synth < 0.05` -- loss of these genes makes cells more sensitive to drug. Examples: PARPi targets BRCA1/2; cisplatin sensitizes ERCC.
- Suppressors (resistance): `fdr_supp < 0.05` -- loss of these genes confers resistance. Examples: drug-efflux genes; drug target itself paradoxically.

## Vehicle vs Day-0 Reference: Critical Decision

**Why this matters:** Drug screen analysis can compare drug to:
1. **Vehicle (DMSO / carrier)** -- isolates drug-specific effect; correct anchor.
2. **Day 0 (initial library)** -- conflates proliferation, drug, and vehicle effects.

```
counts at Day 0          (no perturbation; cloning baseline)
    |
    v
counts at Day 7 - Vehicle (proliferation only; what survives in normal culture)
counts at Day 7 - Drug    (proliferation + drug effect)
    |
    v
Drug effect = LFC(Drug vs Vehicle)         # CORRECT
Wrong:       LFC(Drug vs Day 0)            # confounds drug with general proliferation
```

drugZ specifically requires `-c` to name the vehicle samples. Always include matched vehicle controls in drug screens.

## Drug-Dose and Time-Course Designs

**drugZ for dose-response:** Not natively designed for dose; instead, run drugZ separately at each dose vs vehicle, then look for genes with consistent direction across doses.

```bash
for DOSE in low mid high; do
    python drugz.py \
        -i counts.txt \
        -o drugz_${DOSE}.txt \
        -c Veh_r1,Veh_r2 \
        -x Drug${DOSE}_r1,Drug${DOSE}_r2
done

# Then aggregate: genes significant at high dose AND consistent direction at mid/low dose
```

**For multi-condition drug-screens** (time × drug × cell-line), use MAGeCK MLE with explicit design matrix instead -- MLE handles multi-factorial; drugZ does not.

## Comparison: drugZ vs MAGeCK MLE for Drug Screen

**Goal:** When to use each method.

| Question | drugZ | MAGeCK MLE |
|----------|-------|-------------|
| Single drug, single dose, vehicle vs drug | YES (preferred) | Acceptable |
| Multiple doses, drug response curve | Per-dose drugZ + meta | YES (preferred with dose covariate) |
| Time course at single dose | Per-timepoint drugZ + meta | YES (preferred with time covariate) |
| Drug + cell-line panel | Per-line drugZ + meta | YES (or Chronos) |
| Combinatorial drug pairs | Per-pair drugZ + meta | YES (preferred with interaction) |
| Synergy / antagonism detection | Limited (per-drug calling only) | YES (interaction term in MLE) |
| Small effect sizes (LFC <0.5) | Highest sensitivity | Lower sensitivity |
| Heavy selection (>40% guides change) | OK | Norm needs control sgRNAs |

**Reconciliation:** For simple drug-modifier screens with one drug and one vehicle, run both drugZ and MAGeCK MLE; hits called by both are high confidence; drugZ-only hits at low LFC need orthogonal validation (drug + arrayed validation).

## Removing Genes from Null Distribution

**Goal:** Exclude reference essential or control genes from the Z-score null distribution.

**Approach:** Provide `-r` with a file listing gene symbols whose sgRNA-level Z scores should not influence the null. Useful when CEGv2 essentials would otherwise inflate the null distribution.

```bash
# Pass a file with one gene per line
cat > remove_essential.txt <<EOF
RPS3
RPL11
EIF3A
POLR2A
CDK1
EOF

python drugz.py \
    -i counts.txt \
    -o drugz_clean.txt \
    -c Veh_r1,Veh_r2 \
    -x Drug_r1,Drug_r2 \
    -r remove_essential.txt
```

**When to use:** If pilot drugZ runs show many essential genes appearing as "sensitizers" purely because they drop out under any condition, removing them gives a cleaner drug-specific signal.

## Failure Modes

### drugZ shows no synthetic-lethal hits despite known sensitizing genes

**Trigger:** Comparing drug vs Day-0 instead of drug vs vehicle.
**Mechanism:** Day-0 comparison conflates drug effect with normal-culture proliferation; essential genes drop in both conditions, masking drug-specific sensitization.
**Symptom:** PARPi screen shows no sensitization at BRCA1/BRCA2 despite expected biology.
**Fix:** Re-run with vehicle samples passed to `-c`. The drug-vs-vehicle is the canonical comparison.

### High false-positive rate among essential genes

**Trigger:** Essential genes drop out in both vehicle and drug arms; small relative shift gives misleadingly high Z.
**Mechanism:** drugZ's Z-score is symmetric; essential genes drop in both arms but slightly more in drug -> "synthetic lethal" call.
**Symptom:** Hit list dominated by RPS, RPL, EIF essentials.
**Fix:** Use `-r` with a comma-delimited list of essential gene names to exclude; or filter the output post-hoc.

### Inconsistent results between repeats of drugZ

**Trigger:** Insufficient sgRNAs per gene; small effect sizes.
**Mechanism:** drugZ's per-gene sumZ depends on enough sgRNAs to be stable; with 3-4 sgRNAs/gene, single-guide noise drives variation.
**Symptom:** Same data produces different top hits across repeated runs.
**Fix:** Use a 6+ sgRNAs/gene library (Avana, Dolcetto); or aggregate multiple drugZ runs with different bootstrap seeds; or use MAGeCK MLE for stability.

### drugZ ignores dose information

**Trigger:** Multi-dose screen analyzed at highest dose only.
**Mechanism:** drugZ doesn't model dose; running at one dose loses the dose-response information.
**Symptom:** Hits at high dose may be dose-specific (not true responders).
**Fix:** Run drugZ at each dose; require consistency across doses for high-confidence hits.

### Drug-target gene appears as "suppressor"

**Trigger:** Loss of drug target reduces drug binding, increasing drug resistance.
**Mechanism:** Real biology -- drug target itself is a resistance gene from a KO perspective.
**Symptom:** Drug-target gene like PARP1 appears in suppressor list for PARPi screen.
**Fix:** Expected biology. Annotate the drug target separately. The suppressor list is correct.

## Quantitative Thresholds

| Threshold | Value | Source / Rationale |
|-----------|-------|--------------------|
| Sensitizer hit | `fdr_synth < 0.05` | Colic et al. 2019; BH-corrected |
| Suppressor hit | `fdr_supp < 0.05` | Same |
| High-confidence sensitizer | `fdr_synth < 0.01 AND normZ < -3` | Conservative |
| Pseudocount default | 5 | Colic et al. 2019 |
| Min sgRNAs per gene for stable Z | 4-6 | Below this, Z varies between runs |
| Vehicle replicates needed | 3+ | For stable Z null distribution |
| Drug replicates needed | 3+ | For per-gene sumZ stability |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| No hits | Wrong control samples (Day-0 instead of vehicle) | Re-run with vehicle |
| Hits dominated by essentials | Essentials inflate null | Use `-r` with a comma-list of CEGv2 |
| Unstable hits across runs | Too few sgRNAs/gene | Use 6+ sgRNAs/gene library |
| Drug-target appears in suppressor | Real biology | Annotate separately |
| MAGeCK and drugZ disagree | Different statistical sensitivity | drugZ more sensitive; trust for chemogenomic |
| Inconsistent between doses | Real dose effect | Require consistency across doses |

## References

- Colic M et al. 2019. *Genome Medicine* 11:52. drugZ algorithm and chemogenomic-interaction benchmark.
- Olivieri M et al. 2020. *Cell* 182:481. DDR chemogenomic screens with drugZ.
- Behan FM et al. 2019. *Nature* 568:511. Project Score; genome-wide cancer-dependency screens for target prioritization.

## Related Skills

- crispr-screens/mageck-analysis - MAGeCK MLE alternative for multi-condition drug screens
- crispr-screens/bagel-essentiality - BAGEL2 alternative; sensitive to tumor-suppressor / drug-target
- crispr-screens/hit-calling - Cross-method decision tree including drugZ
- crispr-screens/screen-qc - Pre-drugZ QC including replicate concordance
- crispr-screens/library-design - 6+ sgRNAs/gene library for stable Z
- crispr-screens/copy-number-correction - Pre-correction for cancer-line drug screens
- crispr-screens/base-editing-analysis - Variant-function drug-modifier screens
- pathway-analysis/go-enrichment - Functional analysis of drug-modifier hits
- clinical-databases/clinvar-lookup - Clinical interpretation of drug targets
<!-- END FILE: crispr-screens/drugz-chemogenomic/SKILL.md -->

## 子目录：crispr-screens/hit-calling

<!-- BEGIN FILE: crispr-screens/hit-calling/SKILL.md -->
---
name: bio-crispr-screens-hit-calling
description: Cross-method decision tree for calling hits in pooled CRISPR screens. Catalogs statistical models (MAGeCK RRA, MAGeCK MLE, BAGEL2, drugZ, JACKS, Chronos, CERES), experimental designs each is built for, failure modes outside design domain, reconciliation when methods disagree, multiple-testing and effect-size thresholds, the order of operations (count -> QC -> CN-correct -> hit-call -> validate), the second-best-sgRNA conservative rule, and consensus-hit strategy. Use when choosing among MAGeCK / BAGEL2 / drugZ / JACKS / Chronos for a given design, reconciling disagreement across two or three methods on the same screen, deciding whether to require consensus, gating downstream validation by hit-confidence tier, or interpreting unstable hit lists across reruns.
tool_type: mixed
primary_tool: MAGeCK
---

## Version Compatibility

Reference examples tested with: MAGeCK 0.5.9+, BAGEL2 2.0, drugZ Aug 2019+, JACKS 0.2.0+, Chronos 2.0+ (DepMap), CERES 1.0+, pandas 2.2+, numpy 1.26+, scipy 1.12+, statsmodels 0.14+.

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `mageck --version`, `BAGEL.py version`, `python drugz.py --help`
- Python: `pip show crispr_chronos` (JACKS installs from GitHub, not PyPI)

If code throws ImportError, AttributeError, or TypeError, introspect the installed package and adapt the example to match the actual API rather than retrying.

## Hit Calling Decision Tree

**"Identify significant hits in my CRISPR screen"** -> Choose the analysis method that matches the experimental design, statistical assumptions, and quality grade of the screen. Reconcile across methods when high-stakes hits must be validated.

The primary hit-calling methods cover non-overlapping niches; the decision is not "which is best" but "which matches the design."

| Design / question | Primary method | Why | Secondary check |
|--------------------|----------------|-----|------------------|
| Two-condition essentiality, one cell line, no CN concerns | MAGeCK RRA | Robust, fast, gold-standard for ranked analysis | BAGEL2 (Bayes factor on same data) |
| Time course (3+ timepoints) | MAGeCK MLE | RRA cannot model multi-condition | JACKS (efficacy-aware) |
| Multi-cell-line panel (cancer dependency) | Chronos | Models CN bias + screen quality jointly | MAGeCK MLE per line + meta-analysis |
| Drug screen (vehicle vs drug) | drugZ | Bidirectional Z; vehicle-anchored | MAGeCK MLE with dose covariate |
| Multi-screen joint, same library | JACKS | Shared efficacy; enables ~2.5x smaller screens | MAGeCK MLE; results should converge |
| Essentiality classification with reference sets | BAGEL2 | Bayes factor with CEGv2/NEGv1 calibration | MAGeCK RRA |
| Combinatorial / paired guide | MAGeCK MLE with GI scoring | Models interaction term; see [[combinatorial-screens]] | Custom GI scoring |
| Single-cell perturbation (Perturb-seq) | SCEPTRE | NB GLM + permutation; see [[perturb-seq-analysis]] | Mixscape pre-filter |
| Cancer-line copy-number screen | Chronos (preferred) or CERES | Joint CN-bias + gene-effect modeling; see [[copy-number-correction]] | CRISPRcleanR pre-hoc + MAGeCK |

## Statistical Models Compared

| Method | Year | Statistical model | Tests | Best for | Fails when |
|--------|------|-------------------|-------|----------|------------|
| MAGeCK RRA | 2014 | NB per-sgRNA -> alpha-RRA per gene | Two-sided | General two-condition | >40% guides change (median norm breaks); time course; cancer-line CN |
| MAGeCK MLE | 2015 | NB GLM with design matrix; per-gene beta | Wald per condition | Multi-condition / time course | Cell-line specific essentiality; CN bias |
| BAGEL2 | 2021 | Bayes factor from log-likelihood ratio | Essential vs non-essential | Essentiality classification | Non-essentiality screens; drug screens |
| drugZ | 2019 | Bidirectional Z-score on guide-level LFC | Sensitizer vs suppressor | Drug-modifier / chemogenomic | Essentiality (no biological prior); time-course |
| JACKS | 2019 | Variational Bayes: LFC = gene * efficacy | Per-gene posterior | Multi-screen joint, library calibration | Single screen; cross-chemistry |
| Chronos | 2021 | Cell-population dynamics ODE + NB | Gene effect adjusted for screen quality | Cancer-line panels, longitudinal | Single screen; non-cancer applications |
| CERES | 2017 | Nonlinear model decoupling CN-bias from gene effect | Per-gene effect | Cancer-line panel with CN profile | Superseded by Chronos at DepMap |

## RRA vs MLE Within MAGeCK

| Property | RRA (`mageck test`) | MLE (`mageck mle`) |
|----------|----------------------|---------------------|
| Conditions supported | 2 | Multiple (design matrix) |
| Statistical test | Robust rank aggregation | Wald on beta from NB GLM |
| Output | neg/pos score, FDR per direction | beta per condition |
| sgRNA efficiency | Not modeled (optional fixed input) | Modeled via `--sgrna-efficiency` |
| Outlier robustness | High (rank-based) | Lower (likelihood-based) |
| Best for | Standard 2-condition screen | Time course, drug screen, multi-cell-line, paired |
| Speed | Fast | Slow (per-gene optimization) |

## Algorithmic Taxonomy: Why Each Was Built

| Method | Designed to solve |
|--------|--------------------|
| MAGeCK RRA | First robust statistical framework for CRISPR-screen ranking; alpha-RRA borrowed from RRA in microarray meta-analysis |
| MAGeCK MLE | Extend MAGeCK to multi-condition; explicit beta scores allow direct LFC interpretation |
| BAGEL2 | Reference-set-anchored Bayesian classification; precision-recall calibrated; tumor-suppressor sensitivity (BAGEL1 was uni-directional) |
| drugZ | Drug-modifier screens have low effect sizes and need bidirectional sensitivity; STARS/MAGeCK miss synthetic-lethal hits |
| JACKS | Sample-size reduction via library-shared efficacy; library calibration as side product |
| Chronos | DepMap-scale (1000+ cell lines, billions of cell-divisions) needs population-dynamics model; CN bias + screen quality first-class |
| CERES | First to formally decouple CN from gene effect at DepMap scale; superseded but historically important |

## Run All Five on the Same Data (Consensus Strategy)

**Goal:** For high-stakes hits (drug-target nomination, paper-level claims), require agreement across 2-3 orthogonal methods.

**Approach:** Run MAGeCK + BAGEL2 + (drugZ or JACKS) on the same count matrix; rank by each; classify hits as called by 1, 2, or 3 methods.

```python
import pandas as pd

def consensus_hits(mageck_path, bagel_path, drugz_path,
                   mageck_fdr_thresh=0.05, bagel_bf_thresh=5, drugz_fdr_thresh=0.05):
    '''Build consensus across MAGeCK / BAGEL2 / drugZ on the same screen.
    Each hit gets a count of supporting methods.'''
    mageck = pd.read_csv(mageck_path, sep='\t')[['id', 'neg|fdr']].rename(columns={'id': 'gene', 'neg|fdr': 'mageck_neg_fdr'})
    bagel = pd.read_csv(bagel_path, sep='\t')[['GENE', 'BF']].rename(columns={'GENE': 'gene', 'BF': 'bagel_bf'})
    drugz = pd.read_csv(drugz_path, sep='\t')[['GENE', 'fdr_synth']].rename(columns={'GENE': 'gene', 'fdr_synth': 'drugz_synth_fdr'})
    merged = mageck.merge(bagel, on='gene', how='outer').merge(drugz, on='gene', how='outer')
    merged['mageck_hit'] = merged['mageck_neg_fdr'] < mageck_fdr_thresh
    merged['bagel_hit'] = merged['bagel_bf'] > bagel_bf_thresh
    merged['drugz_hit'] = merged['drugz_synth_fdr'] < drugz_fdr_thresh
    merged['consensus_count'] = (merged[['mageck_hit', 'bagel_hit', 'drugz_hit']].astype(int)).sum(axis=1)
    return merged.sort_values('consensus_count', ascending=False)
```

**Confidence tiers:**

| Tier | Definition | Validation requirement |
|------|------------|-------------------------|
| Tier 1 (high) | Called by 3/3 methods | Arrayed validation; orthogonal modality (CRISPRi if originally Cas9) |
| Tier 2 (medium) | Called by 2/3 methods | Arrayed validation in matched line |
| Tier 3 (exploratory) | Called by 1/3 methods | Treat as hypothesis; further screens before publication |

## Reconciliation: When Two Methods Disagree

| Pattern | Likely cause | Action |
|---------|--------------|--------|
| MAGeCK significant, BAGEL2 not | BAGEL2 trained on CEGv2/NEGv1; gene is essential but not in reference | Trust MAGeCK; flag for follow-up |
| BAGEL2 significant, MAGeCK not | BAGEL2 has tumor-suppressor sensitivity MAGeCK lacks | Investigate sgrna_summary for one weak guide |
| MAGeCK significant, JACKS not | JACKS down-weighted one outlier guide | Trust JACKS if guides agree; outlier may be off-target |
| Chronos and MAGeCK disagree on cancer line | Chronos accounts for CN; MAGeCK does not | Trust Chronos; apply [[copy-number-correction]] |
| drugZ significant, MAGeCK not on drug screen | drugZ bidirectional Z is more sensitive | Trust drugZ for chemogenomic; MAGeCK may miss small effects |
| MAGeCK MLE significant, MAGeCK RRA not in 2-condition | Beta-score effect size is significant but rank-based not | Trust MLE if guides consistent; RRA may be over-conservative |
| All methods disagree | Either no real biology or all methods are mis-applied | Stop. Re-audit QC; check chemistry / library / design matrix |

## Second-Best sgRNA Conservative Rule

**Goal:** Reduce false positives from single outlier sgRNAs by requiring the second-most-extreme guide per gene to also be a hit.

**Approach:** For each gene, sort sgRNAs by LFC; require the second-best LFC to exceed a threshold. Rejects genes that depend on one extreme guide.

```python
def second_best_lfc(sgrna_lfc_df, genes_series, direction='neg'):
    '''Return per-gene LFC of the second-best sgRNA in the direction of interest.
    For dropout (direction="neg"), second-most-negative LFC.'''
    results = []
    for gene in genes_series.unique():
        gene_lfc = sgrna_lfc_df[genes_series == gene].sort_values()
        if direction == 'neg':
            second = gene_lfc.iloc[1] if len(gene_lfc) >= 2 else gene_lfc.iloc[0]
        else:
            second = gene_lfc.iloc[-2] if len(gene_lfc) >= 2 else gene_lfc.iloc[-1]
        results.append({'gene': gene, 'second_best_lfc': second})
    return pd.DataFrame(results)
```

**Rule:** A high-confidence hit has second-best LFC also passing the threshold. A guide-of-one hit has only one extreme guide and should be flagged for orthogonal validation. This rule predates JACKS and is implicit in MAGeCK RRA but explicit elsewhere.

## Multiple-Testing Correction Conventions

| Method | Native correction | Cross-method comparison |
|--------|---------------------|---------------------------|
| MAGeCK RRA | BH per direction | `neg|fdr`, `pos|fdr` |
| MAGeCK MLE | BH per condition | `<cond>|fdr` |
| BAGEL2 | Bootstrap BF; reports BF threshold | BF > 6 ≈ 90% posterior (Hart 2017); ~5% FDR by convention |
| drugZ | BH per direction | `fdr_synth`, `fdr_supp` |
| JACKS | Posterior probability + BH | `fdr_log10` (log10 FDR) |
| Chronos | DepMap gene-effect probability | `effect_probability` |

**Reconciliation:** BF >6 in BAGEL2 corresponds to ~90% posterior probability (Hart 2017 G3, by overlap with CEGv2) and is commonly used as a stringent cutoff roughly comparable to MAGeCK FDR 0.05. Treat that equivalence as an approximate convention, not an exact calibration. drugZ FDR is per-direction; the `fdr_synth` and `fdr_supp` columns are independent BH corrections.

## Order of Operations

```
1. Library design (see library-design)         <- design quality dictates hit calling
2. Plasmid pool sequencing                     <- baseline; non-negotiable
3. Run screen at MOI 0.3, 500x coverage
4. Sequence endpoint
5. Run mageck count                            <- generates raw + normalized counts
6. Screen QC (see screen-qc)                   <- gates downstream method choice
7. Copy-number correction if cancer line       <- CRISPRcleanR or Chronos; see copy-number-correction
8. Batch correction if multi-batch             <- see batch-correction
9. Hit calling (this skill)                    <- choose method by design
10. Consensus across 2-3 methods               <- for high-stakes hits
11. Orthogonal validation                      <- arrayed; different chemistry
12. Pathway analysis                           <- see pathway-analysis/gsea
```

## Custom z-score Hit Calling (when standard tools don't fit)

**Goal:** Compute gene-level z-scores when neither MAGeCK nor BAGEL2 fits the experimental design.

**Approach:** RPM-normalize, compute per-sgRNA log2 fold-changes, aggregate to gene level, derive z-score from the null distribution of non-targeting controls (cleanest) or all genes (assumes <40% changing), apply BH correction.

```python
import pandas as pd
import numpy as np
from scipy import stats
from statsmodels.stats.multitest import multipletests

def custom_zscore_hit_calling(counts_df, ctrl_cols, treat_cols, genes_series, ntc_genes=None):
    '''Z-score gene-level hit calling. If ntc_genes provided, null derived from NTCs only;
    otherwise from all genes (assumes <40% changing).'''
    def rpm(df):
        return df.div(df.sum(axis=0), axis=1) * 1e6
    ctrl_rpm = rpm(counts_df[ctrl_cols])
    treat_rpm = rpm(counts_df[treat_cols])
    lfc_per_sgrna = np.log2((treat_rpm.mean(axis=1) + 1) / (ctrl_rpm.mean(axis=1) + 1))
    gene_lfc = pd.DataFrame({'gene': genes_series, 'lfc': lfc_per_sgrna}).groupby('gene')['lfc'].agg(['mean', 'std', 'count'])
    gene_lfc.columns = ['mean_lfc', 'std_lfc', 'n_sgrnas']
    if ntc_genes is not None:
        null = gene_lfc.loc[gene_lfc.index.isin(ntc_genes), 'mean_lfc']
        null_mean, null_std = null.median(), null.std()
    else:
        null_mean = gene_lfc['mean_lfc'].median()
        null_std = gene_lfc['mean_lfc'].std()
    gene_lfc['z'] = (gene_lfc['mean_lfc'] - null_mean) / null_std
    gene_lfc['p'] = 2 * stats.norm.sf(np.abs(gene_lfc['z']))
    gene_lfc['fdr'] = multipletests(gene_lfc['p'], method='fdr_bh')[1]
    return gene_lfc.sort_values('z')
```

## Failure Modes

### MAGeCK and BAGEL2 disagree by 200+ hits at FDR 0.05

**Trigger:** Heavy-selection screen (>40% guides change) or cancer-line CN bias.
**Mechanism:** MAGeCK median normalization breaks; BAGEL2 is robust due to reference-set anchoring.
**Symptom:** MAGeCK hit list inflated; BAGEL2 list closer to expected size.
**Fix:** Run MAGeCK with `--norm-method control`; apply CN correction; trust BAGEL2 for essentiality.

### Chronos and MAGeCK disagree at the top 10 in a cancer line

**Trigger:** Top hits are at amplified loci.
**Mechanism:** Chronos models CN bias; MAGeCK does not.
**Symptom:** ERBB2 in HER2+, MYC in MYC-amplified, etc. are top hits in MAGeCK but not Chronos.
**Fix:** Apply [[copy-number-correction]] before MAGeCK or switch to Chronos.

### drugZ and MAGeCK disagree on small-effect drug-modifier screen

**Trigger:** Effect size is small; MAGeCK rank-based test is less sensitive than drugZ bidirectional Z.
**Mechanism:** drugZ specifically optimized for small effects in drug screens (Colic et al. 2019); MAGeCK RRA loses sensitivity at small effects.
**Symptom:** At matched FDR, drugZ calls small-effect chemogenomic interactions (e.g. DDR genes) that MAGeCK RRA misses, with stronger expected-pathway enrichment.
**Fix:** Use drugZ as primary for chemogenomic; MAGeCK as confirmatory. See [[drugz-chemogenomic]].

### JACKS down-weights efficiency, MAGeCK doesn't, disagreement

**Trigger:** A gene has one or two strong sgRNAs and 2-3 weak ones; MAGeCK averages them, JACKS down-weights the weak.
**Mechanism:** JACKS variational Bayes correctly identifies low-efficacy guides; MAGeCK aggregates without this prior.
**Symptom:** Gene is JACKS hit but not MAGeCK.
**Fix:** Inspect per-sgRNA LFC; if strong guides are consistent, JACKS is correct. Validate gene orthogonally.

### Consensus across 3 methods is empty (no hits)

**Trigger:** Either no real biology, or each method has different failure mode being triggered.
**Mechanism:** Screen quality is low; signal-to-noise across all methods is poor.
**Symptom:** Tier 1 consensus list is empty.
**Fix:** Re-audit QC. Check Cas9 selection, MOI, timepoint, library positioning. Re-run screen if QC fails.

## Quantitative Thresholds

| Threshold | Value | Source / Rationale |
|-----------|-------|--------------------|
| MAGeCK RRA FDR (gene-level) | <0.05 | Li 2014; standard publication |
| MAGeCK RRA LFC | abs(LFC) >1 | 2-fold; biological |
| BAGEL2 Bayes Factor | >6 standard; >12 stricter | Hart 2017; BAGEL convention |
| drugZ FDR | <0.05 per direction | Colic et al. 2019 |
| JACKS fdr_log10 | <-1 (FDR <0.1); <-2 (FDR <0.01) | Standard FDR convention |
| Chronos dependency probability | >0.5 | DepMap convention (dependency-probability cutoff) |
| Tier 1 consensus (3 methods) | 100% agreement | High confidence; minimal validation needed |
| Tier 2 consensus (2 of 3) | 67% agreement | Arrayed validation required |
| Tier 3 (1 method only) | Hypothesis; flag for follow-up | Multiple screens or arrayed required |
| Second-best sgRNA rule | Second-best LFC also passes threshold | Reduces single-guide outliers |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| All genes significant in MAGeCK RRA | Heavy selection breaks median norm | `--norm-method control`; or use BAGEL2 |
| BAGEL2 returns no hits despite known essentials | Wrong reference gene set | Verify CEGv2/NEGv1 files match library |
| drugZ output empty | Used Day 0 as control instead of vehicle | Re-run with vehicle as control |
| Chronos errors out | Missing CN profile for cell line | Use CRISPRcleanR (unsupervised) instead |
| Methods disagree by orders of magnitude | Quality issue or design mismatch | Re-audit QC; reconcile via tier consensus |
| Empty tier 1 consensus | No real biology OR QC failure | Re-audit QC |
| Single-guide-driven hits | Outlier sgRNA | Apply second-best rule; orthogonal validate |

## References

- Li W et al. 2014. *Genome Biol* 15:554. MAGeCK alpha-RRA.
- Li W et al. 2015. *Genome Biol* 16:281. MAGeCK MLE.
- Kim E & Hart T. 2021. *Genome Med* 13:2. BAGEL2.
- Colic M et al. 2019. *Genome Med* 11:52. drugZ.
- Allen F et al. 2019. *Genome Res* 29:464. JACKS.
- Dempster J et al. 2021. *Genome Biol* 22:343. Chronos.
- Meyers R et al. 2017. *Nat Genet* 49:1779. CERES.
- Hart T & Moffat J. 2016. *BMC Bioinformatics* 17:164. BAGEL Bayes factor framework.
- Hart T et al. 2017. *G3* 7:2719. CEGv2/NEGv1 calibration.

## Related Skills

- crispr-screens/mageck-analysis - Full MAGeCK RRA + MLE detail
- crispr-screens/bagel-essentiality - Full BAGEL2 detail
- crispr-screens/drugz-chemogenomic - Full drugZ detail for drug screens
- crispr-screens/jacks-analysis - Full JACKS detail and library calibration
- crispr-screens/copy-number-correction - Chronos, CERES, CRISPRcleanR
- crispr-screens/screen-qc - Quality gates that drive method choice
- crispr-screens/library-design - Library type dictates analysis method
- crispr-screens/combinatorial-screens - GI scoring (synthetic lethality)
- crispr-screens/perturb-seq-analysis - SCEPTRE for single-cell screens
- crispr-screens/batch-correction - Multi-batch normalization upstream of hit calling
- pathway-analysis/gsea - Downstream pathway enrichment
- pathway-analysis/go-enrichment - GO enrichment of hit lists
<!-- END FILE: crispr-screens/hit-calling/SKILL.md -->

## 子目录：crispr-screens/in-vivo-screens

<!-- BEGIN FILE: crispr-screens/in-vivo-screens/SKILL.md -->
---
name: bio-crispr-screens-in-vivo-screens
description: Designs and analyzes in vivo CRISPR screens in animal tumor models, organoids, and immune-cell adoptive transfers. Covers bottleneck math (250x cells/sgRNA requires ~25M cells implanted; impossible for most syngeneic models, forcing focused libraries), focused library design (Manguso 2017 Nature 547:413 immune screen; Chen 2015 tumor screens), CRISPR-StAR intrinsic-control screening (Uijttewaal 2025 Nat Biotechnol 43:1848), clonal-dynamics-limited detection, tumor-explant DNA recovery, syngeneic vs xenograft vs PDX considerations, and the relationship to downstream MAGeCK / drugZ analysis. Use when designing in vivo CRISPR screens for tumor / immune / metastasis biology, choosing focused vs genome-wide for animal models, addressing bottleneck-induced clonal collapse, picking the syngeneic / xenograft / PDX model, integrating in vivo with in vitro results, or applying CRISPR-StAR for animal experiments.
tool_type: mixed
primary_tool: MAGeCK
---

## Version Compatibility

Reference examples tested with: MAGeCK 0.5.9+, MAGeCK-VISPR 0.5.6+, pandas 2.2+, numpy 1.26+.

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `mageck --version`
- Reference focused libraries: Manguso 2017, Chen 2015, public Addgene aliquots

If code throws ImportError, AttributeError, or TypeError, introspect the installed package and adapt the example to match the actual API rather than retrying.

## In Vivo CRISPR Screen Analysis

**"Design or analyze an in vivo CRISPR screen"** -> Account for the dramatic bottleneck during animal implantation and tumor growth; use focused libraries; recover DNA from tumor explants; analyze with bottleneck-adjusted hit calling.

- CLI: `mageck count` + `mageck test` for standard analysis
- Special handling: bottleneck-adjusted coverage thresholds; per-tissue per-animal replicate structure

## The In Vivo Bottleneck Problem

**Why in vivo screens differ from in vitro:**

| Constraint | In vitro | In vivo |
|------------|----------|---------|
| Cells per condition | 10M-100M (unlimited) | Limited by injection volume (1-5M cells typical) |
| Implant -> early tumor cell count | N/A | 10-100x drop typical |
| Late tumor cell count | N/A | Further 5-10x reduction; ~4 sgRNAs/gene retained in late tumors (Scheidmann 2022) |
| Bottleneck per animal | None | Tens of millions of cells fail to engraft |
| Library coverage achievable | 500-1000x | Often 50-100x effective at endpoint |
| sgRNAs survivable | Full library | 66-97% in early (14 d) tumors, strongly cell-line dependent (Lee 2023); by 38-43 d most reads come from the top 1% of guides |

**Math:** A 70,000-sgRNA library at 500x coverage requires 35M cells in pool. Most syngeneic models can implant 1-5M cells. Result: real coverage is 70x at best; effective coverage at endpoint is even lower after bottleneck.

**Solution:** Use focused libraries (500-3,000 genes; ~3,000-15,000 sgRNAs) to maintain reasonable coverage despite the bottleneck.

## Focused Library Design for In Vivo

**Manguso et al 2017 *Nature* 547:413** established the canonical in vivo CRISPR screen methodology with a focused library:

- 2,398 genes covering kinases, phosphatases, cell-surface proteins, antigen presentation, immune regulation and chromatin remodeling; the 2,368 expressed in the melanoma line were the ones scored
- 4 sgRNAs per gene, delivered as four sub-pools of one sgRNA per gene plus 100 non-targeting controls each (9,992 sgRNAs total)
- Targeted at immune-evasion biology in syngeneic mouse melanoma
- Recovered the known immune-evasion genes Cd274 (PD-L1) and Cd47, and identified Ptpn2 loss as sensitizing tumors to immunotherapy through increased IFN-gamma signaling and antigen presentation

**Standard focused-library principles:**

1. **Gene selection:** Define the biology to be tested (e.g., immune evasion, metastasis); restrict library to genes plausibly involved (kinases, surface proteins, regulators)
2. **Library size:** 500-3,000 genes; 3-6 sgRNAs/gene; total 3,000-18,000 sgRNAs
3. **Coverage achievable:** With 5M cells implanted, 100-300x coverage is achievable

**Public focused libraries:**
- Manguso 2017 immune library (Addgene)
- DepMap focused panels for specific pathways
- Custom: order from Twist via CRISPick or CRISPOR

## CRISPR-StAR (Stochastic Activation by Recombination; Uijttewaal 2025)

**Uijttewaal et al 2025 *Nat Biotechnol* 43(11):1848** (published online Dec 2024) introduced CRISPR-StAR, which holds sgRNAs inactive until cells have engrafted and re-expanded, then activates each sgRNA in only half the progeny of a clone to generate matched active-vs-inactive internal controls.

**How it works:**
1. Library is delivered as sgRNAs held in an inactive state, alongside a tamoxifen-inducible CreERT2 recombinase
2. Cells are implanted in animal at MOI 0.3; they engraft and re-expand into single-cell-derived clones (no editing yet); library complexity preserved
3. Tamoxifen induces CreERT2 recombination, which stochastically activates the sgRNA in ~half the cells of each clone
4. Active and still-inactive (wild-type) cells of the same clone, tracked by UMI barcodes, form paired internal active-vs-control comparisons
5. Screen proceeds; tumor harvest, DNA extraction, sequencing
6. Per-clone active-vs-inactive contrast suppresses engraftment and clonal-drift noise

**What it buys:** CRISPR-StAR enables genome-scale in vivo screens (vs focused libraries) by generating intrinsic per-clone controls; outperforms conventional in vivo screens in therapy-resistant mouse melanoma models (Uijttewaal 2025).

## Syngeneic vs Xenograft vs PDX

| Model | Immune system | Use case |
|-------|---------------|----------|
| Syngeneic (e.g., B16 melanoma in C57BL/6) | Intact mouse immunity | Tumor-immune interaction; checkpoint biology |
| Xenograft (human cancer line in NSG) | Absent / impaired | Tumor cell-intrinsic biology; drug response in human cells |
| PDX (patient-derived xenograft) | Absent / impaired | Patient-specific biology; therapy testing |
| Humanized mouse | Reconstituted human immunity | Tumor-immune in human context (limited) |
| Organoid in vivo | None (in vitro) | Tumor cell-intrinsic in 3D structure |

**Decision rule:** For immune-targeting drug screens, use syngeneic. For human-cancer cell-intrinsic biology, use xenograft. For patient-specific drug screens, use PDX. Each requires different cell numbers and bottleneck planning.

## Tumor DNA Extraction and Sequencing

**Goal:** Recover sufficient sgRNA-containing DNA from tumor explants for sequencing.

**Approach:** Dissect tumor; lyse with proteinase K; extract genomic DNA; amplify the sgRNA locus by PCR; sequence on MiSeq / NextSeq / NovaSeq.

```bash
# Typical PCR + sequencing parameters for in vivo screens
# Per-tumor DNA: 0.5-5 mg yield from typical syngeneic tumor
# Per-sample sequencing depth: >=500 reads/sgRNA at endpoint (bottleneck-limited libraries need depth, not breadth)
# Multiple animals per condition (n=5-10) to account for clonal variation

# mageck count for in vivo
mageck count \
    --list-seq library.csv \
    --sample-label Plasmid,Animal1,Animal2,Animal3,Animal4,Animal5 \
    --fastq Plasmid.fq.gz A1.fq.gz A2.fq.gz A3.fq.gz A4.fq.gz A5.fq.gz \
    --norm-method median \
    --output-prefix in_vivo_screen
```

## Hit Calling for In Vivo

**Goal:** Identify per-gene fitness effects despite high inter-animal variability.

**Approach:** Each animal is a "replicate" with high variance due to clonal dynamics. Use MAGeCK MLE with animal-as-batch covariate, or run MAGeCK RRA per animal and meta-analyze.

```bash
# Option A: MAGeCK MLE with batch covariate
cat > in_vivo_design.txt <<EOF
Samples         baseline    tumor   animal_2  animal_3  animal_4  animal_5
Plasmid         1           0       0         0         0         0
Animal1         1           1       0         0         0         0
Animal2         1           1       1         0         0         0
Animal3         1           1       0         1         0         0
Animal4         1           1       0         0         1         0
Animal5         1           1       0         0         0         1
EOF

mageck mle \
    --count-table in_vivo_screen.count.txt \
    --design-matrix in_vivo_design.txt \
    --output-prefix in_vivo_mle
```

**Per-animal RRA + meta-analysis:**

```python
import pandas as pd

# Run mageck test on each animal vs plasmid
# Combine with Stouffer's Z method
from scipy.stats import norm

def meta_analyze_animals(per_animal_results):
    '''per_animal_results: list of MAGeCK gene_summary.txt per animal.'''
    merged = pd.concat([df.assign(animal=i) for i, df in enumerate(per_animal_results)])
    grouped = merged.groupby('id')
    meta = grouped.apply(lambda g: pd.Series({   # pandas 2.2+: pass include_groups=False
        'mean_neg_score': g['neg|score'].mean(),
        # clip to keep norm.ppf finite at p=0; negate so positive z = stronger depletion,
        # matching examples/per_animal_meta_analysis.py
        'stouffer_z': -norm.ppf(g['neg|p-value'].clip(1e-10, 1 - 1e-10)).sum() / (len(g) ** 0.5),
        'animals_significant': (g['neg|fdr'] < 0.05).sum(),
        'n_animals': len(g)
    }))
    return meta.sort_values('stouffer_z')
```

## Failure Modes

### Clonal dominance from low complexity

**Trigger:** Implanted cells lack sufficient library complexity; a few clones dominate the tumor.
**Mechanism:** Inter-animal stochasticity in cell engraftment creates founder effects.
**Symptom:** Per-animal hit lists vary dramatically; no genes appear across all animals.
**Fix:** Use focused library to maintain coverage; increase animals per condition (n=10+); use CRISPR-StAR to delay bottleneck.

### Tumor DNA extraction yields no sgRNA reads

**Trigger:** Wrong library or library not amplified well from tumor DNA.
**Mechanism:** PCR primers don't match the sgRNA flanking; or insufficient DNA template.
**Symptom:** Low mapping rate (<10%); few sgRNAs detected per tumor.
**Fix:** Verify library plasmid sequence; design primers specific to lentiviral cassette; use 10-100 ng input DNA + 25 PCR cycles.

### In vivo PR-AUC against CEGv2 is poor

**Trigger:** Tumor biology differs from in vitro CEGv2 calibration; not all essentials are essential in animal context.
**Mechanism:** Cells in vivo have different growth conditions (nutrients, hypoxia, immune pressure) than in vitro; CEGv2 calibration assumes in vitro context.
**Symptom:** CEGv2 PR-AUC <0.5 in vivo despite high in vitro PR-AUC.
**Fix:** Use cell-type-and-context-specific essentialome (e.g., a corresponding in vitro screen of the same cell type) as a baseline; in vivo essentialome is biology-dependent.

### Pre-screen Cas9 selection failure

**Trigger:** Cas9-positive cells were not selected before implantation; library has Cas9-negative escapers.
**Mechanism:** Cas9-negative cells carry sgRNA but no editing; persist in tumor without biological perturbation.
**Symptom:** Specific essentiality signals weak; PR-AUC low.
**Fix:** Always select Cas9-positive cells (FACS or selection) before infection; verify by Cas9 IHC or flow.

### Inter-animal variability dominates hit calling

**Trigger:** Limited animals per condition (n=3-5); each has high variance.
**Mechanism:** Per-animal clonal dynamics produce different sgRNA distributions; no consistent signal across few animals.
**Symptom:** MAGeCK p-values inflated; FDR uncalibrated.
**Fix:** Increase animals per condition to 10+; use meta-analysis across animals (Stouffer); validate top hits in arrayed format with n=10 mice each.

### Tumor heterogeneity destroys screen signal

**Trigger:** Spontaneously arising mutations in some tumor regions create non-clonal heterogeneity.
**Mechanism:** Tumor heterogeneity is genuine biology; not all cells in tumor are descendants of original engrafted cells.
**Symptom:** Per-region sequencing shows different sgRNA distributions within same tumor.
**Fix:** Sample multiple tumor regions; or use whole-tumor genomic DNA pooling (averages out heterogeneity).

## Quantitative Thresholds

| Threshold | Value | Source / Rationale |
|-----------|-------|--------------------|
| Cells per animal | 1-5M typical for syngeneic; 5-10M for xenograft | Tumor model dependent |
| sgRNAs per gene in library (focused) | 4-6 | Standard convention |
| Library size for in vivo focused | 3,000-15,000 sgRNAs | Maintainable coverage |
| Coverage at endpoint | ≥50x, ideally 100-200x | Lower than in vitro 500x |
| Animals per condition | 10+ for hit-calling; 5 minimum | Inter-animal variability |
| Animals per condition for arrayed validation | 10 | Tighter signal needed |
| In vivo CEGv2 PR-AUC | >0.4 (context-dependent) | Lower than in vitro 0.7 |
| Late tumor sgRNA-per-gene | ~3.93 mean | Scheidmann 2022 (CTC-derived breast-cancer xenograft; model-dependent) |
| Days to harvest (tumor) | 12-21 days post-implant | Time for selection to manifest |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| No hits | Library complexity collapsed | Use focused library or CRISPR-StAR |
| Per-animal hit lists differ | Clonal dominance | Use focused library; increase animals |
| Low CEGv2 PR-AUC | Context-specific essentialome | Use in vivo-specific reference set |
| Low mapping rate | Wrong sequencing primers | Verify library lentiviral architecture |
| Coverage at endpoint <50x | Implantation bottleneck | Increase cells implanted; focused library |

## References

- Manguso RT et al. 2017. *Nature* 547:413. In vivo CRISPR screen for immune evasion; canonical focused-library design.
- Chen S et al. 2015. *Cell* 160:1246. Original in vivo Cas9 screening methodology.
- Lee TW et al. 2023. *Cancer Gene Ther* 30:1610. Clonal dynamics limit detection of selection in tumour xenograft CRISPR/Cas9 screens.
- Scheidmann MC et al. 2022. *Cancer Res* 82:681. In vivo CRISPR screen in a CTC-derived xenograft; late-tumor sgRNA-per-gene retention.
- Uijttewaal ECH et al. 2025. *Nat Biotechnol* 43:1848 (online Dec 2024). CRISPR-StAR intrinsic-control screening for in vivo models.

## Related Skills

- crispr-screens/library-design - Focused library design for in vivo
- crispr-screens/mageck-analysis - MAGeCK MLE with animal-as-batch covariate
- crispr-screens/hit-calling - Per-animal meta-analysis strategies
- crispr-screens/screen-qc - In-vivo-specific QC thresholds
- crispr-screens/batch-correction - Animal cohort as batch in MLE
- crispr-screens/combinatorial-screens - In vivo combinatorial screens
- crispr-screens/copy-number-correction - Cancer-line in vivo screens
- pathway-analysis/go-enrichment - Functional analysis of in vivo hits
<!-- END FILE: crispr-screens/in-vivo-screens/SKILL.md -->

## 子目录：crispr-screens/jacks-analysis

<!-- BEGIN FILE: crispr-screens/jacks-analysis/SKILL.md -->
---
name: bio-crispr-screens-jacks-analysis
description: Runs JACKS (Joint Analysis of CRISPR/Cas9 Knockout Screens; Allen et al 2019 Genome Research) which models per-sgRNA log-fold-change as the product of a treatment-dependent gene-essentiality term and a treatment-independent guide-efficacy term. Covers the Bayesian decomposition math, the hierarchical efficacy prior shared across screens performed with the same library, when JACKS outperforms MAGeCK (multi-screen joint analysis, libraries with broad efficacy variance) and when it does not (single screen, novel libraries with no prior efficacy), library-reuse efficacy transfer, downstream essentiality interpretation, and the 2.5x sample-size reduction enabled by efficacy-aware testing. Use when running multiple screens with the same library, when guide-level noise is suspected to dominate per-gene signal, when reusing published essentiality reference screens for efficacy priors, or when comparing screens performed across cell lines that share library but differ biologically.
tool_type: python
primary_tool: JACKS
---

## Version Compatibility

Reference examples tested with: JACKS 0.2.0+ (felicityallen/JACKS), pandas 2.2+, numpy 1.26+, scipy 1.12+, matplotlib 3.8+.

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `python run_JACKS.py --help` (run_JACKS.py at the JACKS repo root after clone)
- Python: from jacks.jacks_io import runJACKS; help(runJACKS)
- GitHub: install via `git clone https://github.com/felicityallen/JACKS && cd JACKS && pip install .`

If code throws ImportError, AttributeError, or TypeError, introspect the installed package and adapt the example to match the actual API rather than retrying.

## JACKS CRISPR Screen Analysis

**"Analyze CRISPR screens with guide-level efficacy modeling"** -> Jointly model per-sgRNA log-fold-change across one or more screens as the product of gene essentiality and guide efficacy, sharing efficacy across screens with the same library so that low-quality guides are down-weighted automatically.

- CLI: `python run_JACKS.py countfile replicatefile guidemappingfile [options]` (script at JACKS repo root)
- Python: `from jacks.jacks_io import runJACKS` for programmatic use; lower-level `from jacks.infer import inferJACKS`
- Output: per-gene essentiality (`X1`), per-sgRNA efficacy (`X1`), log-likelihood ratio per gene

## The JACKS Model (under the hood)

**Why this matters for postdoc-level use:** JACKS decomposes the observed per-sgRNA log-fold-change as:

```
LFC[i, c] = gene_effect[g(i), c] * guide_efficacy[i] + noise
```

where `i` is sgRNA index, `c` is screen condition, `g(i)` is the gene targeted by sgRNA i. Gene effect varies by condition (different cell lines, different treatments) but guide efficacy is intrinsic to the sgRNA sequence and is treated as constant across screens. The model fits both parameters via variational Bayes with hierarchical priors:

- `guide_efficacy[i] ~ Normal(1, 1)` (Gaussian prior, mean 1, variance 1), shared across all sgRNAs
- `gene_effect[g, c] ~ Normal(0, sigma_c^2)` per condition

The variational posterior gives expected guide efficacy and gene effect; log-likelihood-ratio tests against a null (zero gene effect) provide gene-level significance.

**Critical assumption:** Guide efficacy is treated as cell-line independent within the same chemistry. Allen 2019 reports per-sgRNA Cas9 KO efficacy is consistent across randomly selected batches of cell lines (within-chemistry), supporting library-shared efficacy. **However**, efficacy is NOT shareable across chemistries: Cas9 KO efficacy != CRISPRi knockdown efficiency != CRISPRa activation efficiency. JACKS must be run separately per chemistry; use only within the same chemistry on the same library.

## When JACKS Outperforms MAGeCK and BAGEL2

| Scenario | Advantage | Expected gain (Allen 2019) |
|----------|-----------|------------------------------|
| Multi-screen joint analysis (>=3 screens with same library) | Efficacy shared; noise averaged | ~21% lower error vs MAGeCK; 9% vs original BAGEL; 91-99% of cell lines improved (method-dependent) |
| Reusing public reference screens (DepMap, Project Score) as efficacy prior | Transfer learning | New screens can be smaller; efficacy priors transfer across same-library screens |
| Libraries with broad efficacy variance (e.g. older GeCKOv2) | Down-weights known weak guides | Larger gain than on Brunello (already efficacy-filtered) |
| Heterogeneous quality (mixed plasmid quality across screens) | Per-screen noise estimation | Cleaner per-condition gene effects |

## When JACKS Is Not the Right Tool

- **Single screen, no prior efficacy:** JACKS has nothing to leverage; MAGeCK or BAGEL2 work as well.
- **Single timepoint / two-condition essentiality:** RRA or BAGEL2 simpler and equivalent.
- **Heavy-selection drug screens:** drugZ explicit for chemogenomic; JACKS less sensitive.
- **Cancer-cell-line copy-number screens:** Chronos preferred; jointly models CN bias + screen quality; JACKS does neither.
- **Cross-chemistry sharing (e.g. CRISPRi + Cas9):** Efficacy is chemistry-specific; do not share.

## Run JACKS Joint Analysis

**Goal:** Jointly analyze multiple CRISPR screens performed with the same library and chemistry.

**Approach:** Provide a count matrix with all samples across all screens, a replicate map identifying which samples belong to which screen and condition, and a sgRNA-to-gene map. JACKS learns guide efficacy shared across screens and gene effects per screen.

```python
# Programmatic invocation
from jacks.jacks_io import runJACKS

# Input file paths
counts_path = 'counts.txt'                    # rows=sgRNA; first cols 'sgRNA' (or custom), then sample counts
replicate_map_path = 'replicatemap.txt'       # tab-separated with header: Replicate, Sample, Control
guide_map_path = 'guidemap.txt'               # tab-separated with header: sgRNA, Gene

# Replicate map format (tab-separated WITH header; column names match flags below)
# Replicate                Sample          Control
# Screen1_T1               Screen1_T       Screen1_C
# Screen1_T2               Screen1_T       Screen1_C
# Screen1_C1               Screen1_C       Screen1_C
# Screen2_T1               Screen2_T       Screen2_C
# Screen2_T2               Screen2_T       Screen2_C
# Screen2_C1               Screen2_C       Screen2_C

runJACKS(
    countfile=counts_path,
    replicatefile=replicate_map_path,
    guidemappingfile=guide_map_path,
    rep_hdr='Replicate',
    sample_hdr='Sample',
    ctrl_sample_hdr='Control',                # per-sample control specification
    sgrna_hdr='sgRNA',
    gene_hdr='Gene',
    outprefix='jacks_out',
    apply_w_hp=True,                          # hierarchical prior on the gene effect w (the JACKS help notes: not recommended)
)
```

```bash
# Equivalent CLI run (run_JACKS.py is at the JACKS repo root after clone)
python run_JACKS.py \
    counts.txt \
    replicatemap.txt \
    guidemap.txt \
    --rep_hdr Replicate \
    --sample_hdr Sample \
    --ctrl_sample_hdr Control \              # per-sample control (or --common_ctrl_sample <name>)
    --sgrna_hdr sgRNA \
    --gene_hdr Gene \
    --outprefix jacks_out \
    --apply_w_hp                              # hierarchical prior on the gene effect w (not recommended by the tool's own help)
# Outputs:
#   jacks_out_gene_JACKS_results.txt      gene effect: header `Gene` + one column per cell line
#   jacks_out_gene_std_JACKS_results.txt  matching posterior std per gene per cell line
#   jacks_out_gene_pval_JACKS_results.txt p-values (written only when --ctrl_genes is supplied)
#   jacks_out_grna_JACKS_results.txt      sgRNA-level: header `sgrna`, `X1`, `X2`
#   jacks_out_JACKS_results_full.pickle  full posterior for downstream
```

## Output Interpretation

| Column | Meaning | Direction |
|--------|---------|-----------|
| `X1` (gene file) | Posterior mean of gene_effect | Negative = essential (depleted); positive = enriched |
| gene std file | Posterior std of the gene effect | Lower = more confident; combine as effect/std for a z-like statistic |
| `X1` (sgRNA file) | Posterior mean of guide efficacy | Centred near 1 and unbounded; the reference Avana set spans negative values to >100 |
| `X2` (sgRNA file) | Second moment E(X^2) of efficacy; std = sqrt(X2 - X1^2) | Confidence in the efficacy estimate |

**Interpretation rule:** A gene is essential if its effect is negative and large relative to its posterior std (effect/std well below zero); supply `--ctrl_genes` to also get a p-value file. The X1/X2 ratio gives a z-like statistic; |X1/X2| > 2 corresponds to ~95% credible deviation from zero. Sort by X1 (most negative first) for essentiality rank.

## Build Library-Wide Efficacy Prior from Reference Screens

**Goal:** Transfer learned efficacy from a large public screen panel to a new small screen.

**Approach:** Run JACKS on the reference panel (e.g. DepMap CRISPR screens with TKOv3 or Brunello), extract per-sgRNA efficacy posterior, and supply it as the prior for a new screen.

```python
def extract_efficacy_prior(reference_jacks_results):
    '''Build per-sgRNA efficacy prior (mean + std) from a large reference screen.'''
    df = pd.read_csv(reference_jacks_results, sep='\t')
    prior = df[['sgrna', 'X1', 'X2']]      # --reffile requires these exact column names; do not rename
    return prior

# Use in new JACKS run via --reffile <path>
# Reference: Allen 2019 Genome Research 29:464; efficacy-aware testing enables ~2.5x smaller screens (fewer replicates/guides)
```

## Per-sgRNA Efficacy Diagnostics

**Goal:** Identify low-efficacy guides for library refinement.

**Approach:** Examine the distribution of inferred efficacies; guides below 0.3 are likely non-functional and should be excluded from re-designed libraries.

```python
import matplotlib.pyplot as plt

def efficacy_summary(grna_results_path, low_threshold=0.3):
    df = pd.read_csv(grna_results_path, sep='\t')
    df['low_eff'] = df['X1'] < low_threshold
    summary = {
        'total_guides': len(df),
        'low_efficacy_count': df['low_eff'].sum(),
        'low_efficacy_pct': df['low_eff'].mean() * 100,
        'median_efficacy': df['X1'].median(),
        'q25_q75': (df['X1'].quantile(0.25), df['X1'].quantile(0.75)),
    }
    # Per-gene proportion of low-efficacy guides
    by_gene = df.groupby('Gene')['low_eff'].mean().sort_values(ascending=False)
    summary['genes_with_all_low_eff'] = (by_gene == 1).sum()  # genes where every guide is weak
    return summary, by_gene
```

**Critical:** Genes where every guide is low-efficacy will show no signal regardless of biology. Filter from interpretation; flag for re-design with updated rules (Brunello / TKOv3).

## Comparing JACKS, MAGeCK, BAGEL2

| Property | JACKS | MAGeCK | BAGEL2 |
|----------|-------|--------|--------|
| Statistical framework | Variational Bayes | NB GLM + alpha-RRA / MLE | Bayes factor on per-sgRNA fold change |
| Models guide efficacy | Yes (jointly) | No (optional fixed input) | No |
| Multi-screen joint | Yes (native) | Limited (MLE design matrix) | No (per-screen) |
| Speed | Slow (variational inference) | Fast | Fast |
| Output | gene effect + sgRNA efficacy | beta or RRA score | Bayes Factor |
| Best for | Multi-screen joint analyses, library calibration | General-purpose, single screen | Essentiality classification |
| Quantified accuracy gain (Allen 2019) | ~21% lower error vs MAGeCK; 9% vs BAGEL v1 | Reference | Not benchmarked (Allen 2019 compared BAGEL v1) |

**Reconciliation:** Hits identified by JACKS AND MAGeCK are high confidence. JACKS-only hits typically reflect strong gene signals where one or two guides were dragging down MAGeCK; verify the up-weighted high-efficacy guides have the expected sign. MAGeCK-only hits at FDR <0.05 may be single-guide outliers; check sgrna_summary for guide-level dispersion.

## Failure Modes

### Efficacy collapsed near zero for all guides

**Trigger:** Screen used a chemistry the model doesn't support (e.g., CRISPRi screen analyzed with JACKS defaults).
**Mechanism:** CRISPRi efficacy is fundamentally different from Cas9-KO efficacy; the Beta-prior hyperparameters fit on Cas9 data don't transfer.
**Symptom:** Median efficacy <0.2; almost no significant gene effects.
**Fix:** Train per-chemistry priors separately; for CRISPRi/a, current JACKS recommends `--apply_w_hp` with manually set hyperparameters from a CRISPRi reference dataset.

### Cross-cell-line efficacy disagreement

**Trigger:** Pooling screens across cell lines with very different Cas9 expression / chromatin / fitness baselines.
**Mechanism:** Efficacy depends on Cas9 expression and chromatin accessibility; sharing across lines averages real per-line differences.
**Symptom:** Per-line gene effects look noisier than per-line MAGeCK results.
**Fix:** Use Chronos for multi-cell-line screens with screen-quality modeling; reserve JACKS for screens with matched chemistry + cell type / culture conditions.

### MCMC / variational convergence failure

**Trigger:** Too few iterations relative to library size (10k iters for 100k-guide library is sometimes insufficient).
**Mechanism:** Variational lower bound has not plateaued; estimates noisy.
**Symptom:** Repeated runs produce different gene effects.
**Fix:** JACKS exposes no iteration flag on the CLI (internally `n_iter=50`); instead increase guides per gene or add screens, and verify the result is stable across re-runs (JACKS exposes no seed flag).

### sgRNA-to-gene map mismatch

**Trigger:** Guide map and count matrix use different sgRNA naming conventions (e.g. `BRCA1_1` vs `BRCA1.1`).
**Mechanism:** JACKS reads the map as a join; mismatched rows give NaN gene effects.
**Symptom:** Many genes missing from output.
**Fix:** Standardize naming; sanity check `len(jacks_output) == n_genes_expected`.

### Reference efficacy prior from wrong library

**Trigger:** Using DepMap Brunello efficacy as prior for a screen with a custom TKOv3-style library.
**Mechanism:** Per-sgRNA efficacy is sequence-specific; sgRNAs in one library map to different gene contexts than another.
**Symptom:** Worse gene-effect estimation than no prior.
**Fix:** Match library exactly; if no matched reference exists, run without prior.

## Reconciliation: When JACKS and Other Tools Disagree

| Pattern | Likely cause | Action |
|---------|--------------|--------|
| JACKS significant, MAGeCK not | One low-efficacy guide dragged MAGeCK; JACKS down-weighted it | Trust JACKS if 3+ high-efficacy guides agree |
| MAGeCK significant, JACKS not | All guides have similar efficacy; JACKS prior shrinks signal | Verify per-guide LFC consistency in MAGeCK sgrna_summary |
| JACKS efficacy ~0.5 for all guides | Hierarchical prior over-shrinkage | Run with `--apply_w_hp` false; refit hyperparameters |
| Gene effect different sign from MAGeCK | Multi-screen pooling created mean effect different from single-screen | Run per-screen separately to confirm |

## Quantitative Thresholds

| Threshold | Value | Source / Rationale |
|-----------|-------|--------------------|
| Hit call | gene effect negative with abs(effect/std) > 2 | Bayesian z-equivalent; p-values need --ctrl_genes |
| Effective gene signal | X1 < 0 AND abs(X1/X2) > 2 | Bayesian z-equivalent |
| Low-efficacy guide flag | X1 (sgRNA) <0.3 | Operational convention; below this, guide likely non-functional |
| Reference for prior reuse | DepMap or Project Score panel | Established efficacy distribution |
| Minimum screens for joint efficacy benefit | 3+ | Below this, single-screen tools (MAGeCK/BAGEL2) equivalent |
| Iterations for variational inference | 5000+ publication; 1000 default | Verify ELBO plateaus |
| Cross-library efficacy transfer | Not supported | Different libraries -> different sequences -> different efficacies |
| Cross-chemistry efficacy transfer | Not supported | Cas9 efficacy != CRISPRi efficacy |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| Many NaN gene effects | sgRNA-to-gene map mismatch | Verify naming consistency between count matrix and map |
| Median efficacy <0.2 | Wrong chemistry assumed by prior | Disable `--apply_w_hp` or use matched prior |
| ELBO not plateaued | Too few iterations | Increase iterations to 5000+ |
| Inconsistent gene effects between runs | Variational inference is initialization-sensitive | Re-run and compare; JACKS exposes no seed flag |
| Library-reuse prior doesn't help | Wrong library reference | Match library exactly |

## References

- Allen F et al. 2019. *Genome Research* 29:464. JACKS; original Bayesian joint analysis paper.
- Allen F, Parts L (Wellcome Sanger Institute). https://github.com/felicityallen/JACKS. Official repository.
- Behan FM et al. 2019. *Nature* 568:511. Project Score CRISPR panel; library-wide reference screen data.
- Meyers RM et al. 2017. *Nat Genet* 49:1779. Avana CRISPR DepMap; reference panel for efficacy transfer.

## Related Skills

- crispr-screens/mageck-analysis - MAGeCK RRA/MLE comparison
- crispr-screens/bagel-essentiality - Alternative for essentiality without efficacy modeling
- crispr-screens/library-design - sgRNA design rules informed by JACKS efficacy output
- crispr-screens/copy-number-correction - Chronos preferred for cancer-line multi-screen analyses
- crispr-screens/screen-qc - Pre-JACKS QC; replicate Pearson must pass before joint analysis
- crispr-screens/hit-calling - Cross-method decision tree
- crispr-screens/batch-correction - JACKS does not adjust for batch; pre-correct if necessary
<!-- END FILE: crispr-screens/jacks-analysis/SKILL.md -->

## 子目录：crispr-screens/library-design

<!-- BEGIN FILE: crispr-screens/library-design/SKILL.md -->
---
name: bio-crispr-screens-library-design
description: Designs pooled sgRNA libraries for CRISPR knockout, interference (CRISPRi), activation (CRISPRa), Cas12a multiplex, base-editor, and prime-editor screens. Covers on-target scoring (Rule Set 2, Azimuth, DeepSpCas9, CRISPRon), off-target scoring (CFD, MIT), TSS-relative positioning for CRISPRi/a (Horlbeck, Dolcetto, Calabrese), PAM-variant chemistries, control-guide composition, oligo cloning architecture, and library QC. Use when choosing a genome-wide library (GeCKOv2 vs Avana vs Brunello vs TKOv3 vs Inzolia), designing a focused or paralog-focused custom library, picking CRISPRi vs CRISPRa TSS windows, deciding control-guide proportions, or diagnosing library skew and dropout in a freshly cloned pool.
tool_type: mixed
primary_tool: CRISPOR
---

## Version Compatibility

Reference examples tested with: CRISPOR 5.01+, BioPython 1.83+, pandas 2.2+, numpy 1.26+, Azimuth 2.0+ (Doench 2016), CRISPRon 1.0+ (Xiang 2021), DeepSpCas9 1.0+ (Kim 2019).

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `crispor.py --help` from the crisporWebsite clone
- Python: Azimuth has no console script; call `azimuth.model_comparison.predict(...)`

If code throws ImportError, AttributeError, or TypeError, introspect the installed package and adapt the example to match the actual API rather than retrying.

## sgRNA Library Design

**"Design a CRISPR library for my screen"** -> Pick a chemistry (Cas9 KO, CRISPRi, CRISPRa, Cas12a, base or prime editor), score candidate guides for on-target activity and off-target liability, position them relative to gene/TSS, add appropriate controls, lay out the oligo for synthesis, and validate the cloned pool.

- Python: `crispor.py` (web + CLI) for batch genome-wide guide scoring with CFD+MIT off-target
- Python: `azimuth` (Microsoft Research) for Rule Set 2 on-target predictions (Brunello-style)
- Python: `CRISPRon`, `DeepSpCas9` for modern deep-learning predictors
- R: `crisprDesign` (Bioconductor) for integrated annotation-aware design

## Library Chemistry Decision Tree

| Goal | Chemistry | Canonical library | Guides/gene | TSS / target window |
|------|-----------|-------------------|-------------|---------------------|
| Loss-of-function essentiality, fitness | SpCas9 KO | Brunello, TKOv3, Avana | 4 (Brunello), 4 (TKOv3), 6 (Avana) | Constitutive exons, prefer aa 5-65% from N-terminus |
| Knockdown of non-cuttable genes, dosage-sensitive | dCas9-KRAB (CRISPRi) | Dolcetto, Horlbeck v2 | 6 (Dolcetto), 5 (Horlbeck) | Optimum +25 to +75 downstream of FANTOM5 TSS, searched out to -50/+300 (Dolcetto, Sanson 2018); -25 to +500 (Horlbeck v2) |
| Gain-of-function, gene activation | dCas9-VP64 / SAM / SunTag (CRISPRa) | Calabrese, Horlbeck-CRISPRa | 6 (Calabrese), 5 (Horlbeck) | -150 to -75 from TSS (Calabrese); -550 to -25 (Horlbeck v2) |
| Paralog buffering, GI screens | enAsCas12a multiplex | Inzolia, in4mer | 4-guide arrays | Constitutive exons |
| Variant function, SNV scanning | CBE / ABE | Custom tiling library | Tile editing windows | Editing window pos 4-8 from PAM-distal end |
| Precise edit, indel-free | Prime editor | Custom PRIDICT-designed | Tile pegRNAs | Anywhere with NGG PAM within 30 nt of edit |

**Fails when:**
- CRISPRi/a targeting wrong TSS: any TSS without FANTOM5 CAGE evidence is suspect; guides positioned against the wrong TSS lose most of their knockdown.
- Cas9 KO of essential paralogs: single-KO buffering hides paralog-redundant essentials (42% of constitutively expressed genes never score, Dede 2020); switch to Cas12a multiplex.
- Base editor over an exon-intron boundary: editing-window bystanders create splice variants instead of the intended SNV.

## On-Target Scoring: Algorithmic Taxonomy

| Predictor | Year | Training set | Strengths | Fails when |
|-----------|------|--------------|-----------|------------|
| Doench Rule Set 1 | 2014 | Flow-sorted GFP+ knockouts | Simple, interpretable | Limited training data; sub-optimal at >NGG context |
| Doench Rule Set 2 / Azimuth 2.0 | 2016 | 1,841 flow-cytometry guides (Doench 2014) plus new guides tiling additional genes | Gold-standard for SpCas9; basis of Brunello | Trained on dropouts; under-predicts efficacy for nuclear-localized targets |
| DeepSpCas9 | 2019 | 12,832 synthetic targets integrated in HEK293T | Spearman ~0.77 vs measured indel frequency on held-out data | Black-box; sensitive to chromatin/context features it wasn't trained on |
| CRISPRon | 2021 | High-throughput indel sequencing | Best for therapeutic-grade target nomination | Slow per-guide; over-fits to its specific cell line |
| DeepHF | 2019 | ~171k guides in HEK293T (WT 55,604; eSpCas9(1.1) 58,167; HF1 56,888) | Separate model per enzyme variant, including WT | Pick the model matching the enzyme actually used |

**Reconciliation:** When predictors disagree, prefer the model whose training cell line matches the screen line (DeepSpCas9 was trained on synthetic targets integrated in HEK293T). For Brunello selection, Azimuth/Rule Set 2 is sufficient because the library was built with it -- introducing a different scorer creates apples-to-oranges ranking with the original library.

## Off-Target Scoring

| Score | Year | Math | Cutoff convention |
|-------|------|------|--------------------|
| MIT (Hsu) | 2013 | Position-weighted mismatch penalty | Specificity score 0-100, higher is better; CRISPOR treats >=50 as a good guide |
| CFD (Doench) | 2016 | Position+nucleotide-specific penalty fit on Brunello | Per-site CFD >0.2 counts a candidate off-target (Doench 2016); CRISPOR's aggregate CFD specificity score is 0-100, higher is better |
| Elevation | 2018 | ML on CFD + mismatch positions | Tighter than CFD |

CFD remains the default for genome-wide library design. **Critical pitfall:** CFD penalizes only mismatches, not bulges; for ≤1 mismatch + 1-bp bulge off-targets, validate empirically with GUIDE-seq or CIRCLE-seq. CRISPOR reports both the MIT (Hsu) and CFD guide specificity scores in a single output.

## Score and Rank sgRNAs for a Target Gene

**Goal:** Generate ranked sgRNA candidates for a single gene, jointly scored on on-target activity (Rule Set 2 / Azimuth) and off-target liability (CFD).

**Approach:** Identify all PAM-adjacent 20-nt protospacers in the target gene's coding sequence, retain only those in the first 5-65% of the protein (constitutive-exon convention from Brunello), filter on GC 30-70% and absence of poly-T (≥4 Ts terminates U6), call Azimuth for on-target and CRISPOR for off-target, and select the top N satisfying both criteria.

```python
import re
import pandas as pd
import numpy as np
from Bio.Seq import Seq

def find_sgrna_candidates(cds_sequence, pam='NGG', guide_length=20):
    '''Return all protospacer candidates with PAM coordinates on + strand.
    Caller must filter by exon position and Azimuth/CFD score.'''
    pam_pattern = re.compile(f'(?=([ACGT]{{{guide_length}}}{pam.replace("N", "[ACGT]")}))')
    candidates = []
    for strand, seq in [('+', cds_sequence), ('-', str(Seq(cds_sequence).reverse_complement()))]:
        for m in pam_pattern.finditer(seq):
            spacer = m.group(1)[:guide_length]
            if 'TTTT' in spacer or spacer.count('G') + spacer.count('C') not in range(6, 15):
                continue
            candidates.append({'spacer': spacer, 'strand': strand,
                               'pos_in_cds': m.start() if strand == '+' else len(seq) - m.start() - 23,
                               'gc_frac': (spacer.count('G') + spacer.count('C')) / guide_length})
    return pd.DataFrame(candidates)

def annotate_exon_position(candidates_df, cds_length):
    '''Filter to protospacers within first 5-65% of CDS (Brunello convention).
    Reason: N-terminal indels truncate protein; very-N-terminal hits alt initiation;
    C-terminal hits miss functional domains (Doench 2016 Nat Biotech).'''
    lo, hi = 0.05 * cds_length, 0.65 * cds_length
    return candidates_df[(candidates_df['pos_in_cds'] >= lo) & (candidates_df['pos_in_cds'] <= hi)].copy()
```

## CRISPRi / CRISPRa TSS Targeting

**Goal:** Position guides relative to the empirical TSS for maximum knockdown (CRISPRi) or activation (CRISPRa).

**Approach:** Resolve TSS from FANTOM5 CAGE peaks (highest-ranked peak per gene; fall back to Ensembl/RefSeq if absent), define the modality-specific window, score candidate spacers in that window with Rule Set 2 plus the Horlbeck/Sanson CRISPRi/a-tailored rules, and select 5-6 guides per gene biased toward the window center.

```python
def crispri_window(tss_coord, strand='+'):
    '''Dolcetto convention: search -50 to +300 around the FANTOM5 highest-rank CAGE peak.
    Reason: Sanson 2018 found +25 to +75 nt downstream of the TSS optimal for CRISPRi,
    so rank candidates toward that band; the search is relaxed outward to fill the
    per-gene guide quota when poorly-annotated TSSs leave too few candidates.'''
    if strand == '+':
        return (tss_coord - 50, tss_coord + 300)
    return (tss_coord - 300, tss_coord + 50)

def crispra_window(tss_coord, strand='+'):
    '''Calabrese convention: -150 to -75 upstream of TSS.
    Reason: dCas9-VP64 (and SAM, SunTag) activate maximally when bound
    just upstream of Pol II loading. Horlbeck v2 CRISPRa uses -550 to -25
    (broader, lower per-guide signal). For SAM, prefer Calabrese tightness;
    for SunTag, Horlbeck width is acceptable.'''
    if strand == '+':
        return (tss_coord - 150, tss_coord - 75)
    return (tss_coord + 75, tss_coord + 150)
```

**Critical nuance:** Cell-type-specific TSSs differ from the FANTOM5 consensus in ~15% of genes. For tissue-specific screens (e.g., neuron, hepatocyte), re-derive TSSs from a matched CAGE / GRO-seq / PRO-seq dataset before locking guide positions, or knockdown efficiency drops several-fold. The single most common cause of "weak" CRISPRi hits is mis-positioned guides against an alternative TSS.

## Genome-Wide Library Selection

| Library | Year | Modality | Size (genes x guides) | sgRNA rules | Notable |
|---------|------|----------|-----------------------|-------------|---------|
| GeCKOv2 | 2014 | Cas9 KO | ~19k x 6 (~123k) | Exon position + off-target specificity (predates Rule Set 1) | Older; legacy datasets still use it |
| Avana | 2016 | Cas9 KO | 110,257 as published; DepMap screens a ~4-guide subset (Meyers 2017: 70,086 after filtering, 17,670 genes) | Rule Set 1 | Still the Broad's primary Cas9 library; CERES->Chronos changed in 2021, not the library |
| Brunello | 2016 | Cas9 KO | ~19k x 4 (~77k) | Rule Set 2 + CFD | Modern standard for new screens |
| TKOv3 | 2017 | Cas9 KO | ~18k x 4 (~71k) | Hart on/off-target | Bagel/BAGEL2-optimized |
| Humagne | 2020 | enAsCas12a | ~19.8k x 1 dual-guide construct (~20k per set) | enAsCas12a rules | Compact Cas12a sets C and D |
| Horlbeck CRISPRi v2 | 2016 | dCas9-KRAB | ~18k x 5 (~104k) | Horlbeck CRISPRi rules | First-gen, still widely used |
| Dolcetto | 2018 | dCas9-KRAB | ~19k x 3 per set (114,061 across Sets A+B) | Horlbeck + Rule Set 2 | Modern CRISPRi standard |
| Horlbeck CRISPRa | 2016 | dCas9-VP64 | ~18k x 5 (~104k) | Horlbeck CRISPRa rules | Original CRISPRa |
| Calabrese | 2018 | dCas9-VP64 | ~18.9k x 3 per set (113,238 across Sets A+B) | Tight TSS window | Modern CRISPRa standard |
| Inzolia | 2024 | enAsCas12a | ~49k arrays: 19,687 genes (2 arrays each) plus ~4,435 paralog pairs | enAsCas12a rules | Paralog-pair multiplex; ~30% smaller than a typical Cas9 library |
| in4mer | 2024 | Cas12a (4-guide) | Custom | enAsCas12a multiplex | Triple/quadruple KO per cassette |

**dAUC trajectory (essentiality benchmark):** GeCKOv2 < Avana < Brunello/TKOv3 (Doench 2016 + Hart 2017). Moving from 4 to 6 sgRNAs/gene gives diminishing returns; the larger gain is moving from Rule Set 1 to Rule Set 2.

**Cost-coverage tradeoff:** A 77k-guide Brunello at 500x cells/sgRNA needs 38.5M cells in pool, scalable. A 117k-guide Calabrese at 500x needs 59M cells -- often the deciding factor against CRISPRa for difficult-to-grow lines.

## PAM Variants and Alternative Cas Enzymes

| Enzyme | PAM | Spacer length | Best for |
|--------|-----|---------------|----------|
| SpCas9 (WT) | NGG | 20 nt | Standard pooled screens; broadest library support |
| eSpCas9, SpCas9-HF1 | NGG | 20 nt | Lower off-target rate; use for therapeutic-grade nomination |
| SpCas9-NG | NG | 20 nt | Expanded targeting (~4x coverage); accept lower activity per guide |
| SpRY | NRN / NYN | 20 nt | Near-PAMless; coverage at every position; ~50% lower per-guide activity |
| SaCas9 | NNGRRT | 21 nt | AAV-packageable (small ORF); rarely used in pooled screens |
| AsCas12a, LbCas12a | TTTV | 23 nt | AT-rich regions; staggered cut; lower expression noise |
| enAsCas12a (DeWeirdt 2021) | Expanded TTTV + several non-canonical | 23 nt | Combinatorial / paralog screens |

**Decision rule:** If the screen requires every possible TSS position (saturation tiling, dense regulatory dissection), use SpRY despite lower activity; otherwise, NGG is best because the on-target predictors were trained on it.

## Control Guides

A genome-wide library should include:

| Control type | Count | Purpose |
|--------------|-------|---------|
| Non-targeting (scrambled, no genomic match) | 500-1,000 (~1% of library) | Primary null distribution for CRISPRi/a; safe baseline for normalization |
| Safe-harbor (AAVS1, ROSA26-equivalent) | 50-100 | Cas9-only: absorbs cut-toxicity baseline (matters for amplicon-correction) |
| Olfactory receptors (presumed non-expressed) | 50-100 | Second null set for orthogonal normalization |
| Reference essentials (CEGv2 subset: e.g. RPS3, RPL11, EIF3A, POLR2A) | 50-100 | Internal positive control; QC dropout signal |
| Reference non-essentials (NEGv1 subset) | 50-100 | Internal negative control; BAGEL2 calibration |

**Critical pitfall:** Using only AAVS1 as the negative control in a Cas9 screen creates a normalization baseline biased toward "any cut is bad." Always add NTCs or non-essentials so that downstream median normalization and PR-AUC against CEGv2 work without baseline-shift artifacts.

## Library Composition for Specialized Screens

**Paralog buffering (Cas12a multiplex):** Build 4-guide arrays where positions 1-2 target gene A and positions 3-4 target paralog gene B. Inzolia covers ~4,435 paralog pairs within ~49k arrays. Singleton controls (gene A alone, gene B alone) must be included to score genetic interaction = double_KO_LFC - sum(single_KO_LFC).

**Base editor screens (tiling-library design):** Tile NGG-adjacent spacers across exons; ensure editing window (positions 4-8 from PAM-distal end) lands inside coding exons; flag bystander Cs/As in the window for downstream interpretation. Restrict to 50-90% editing efficiency a priori (filter out predicted low-efficacy guides) -- see [[base-editing-analysis]].

**Tiling / regulatory dissection:** Dense (every 5-10 bp) CRISPRi or CRISPRa guides across the candidate region; CRISPRi has broader signal width (good for enhancer discovery) but Cas9-indel tiling has sharper resolution (good for pinpointing critical bases). Pair with CRISPR-SURF deconvolution.

## Oligo Design for Pooled Synthesis

**Goal:** Generate the final oligo sequence ready for chip-based synthesis. Vendor limits differ: Twist oligo pools cap at ~300 nt per oligo with no fixed pool size, GenScript's 92K format spans 20-170 nt, and Agilent OLS 244K spans 30-230 nt.

**Approach:** Add subpool PCR primers (so multiple sublibraries can share a synthesis array), the BsmBI/Esp3I overhang for golden-gate cloning into LentiGuide-Puro (Addgene 52963) or LentiCRISPRv2, and append the tracrRNA scaffold if the array length permits.

```python
def build_oligo(spacer, vector='lentiGuide-Puro', subpool_idx=None):
    '''Construct final oligo for pooled synthesis.

    LentiGuide-Puro / LentiCRISPRv2 use BsmBI (Esp3I) with these overhangs:
        forward: 5'-CACCG[spacer]-3'
        reverse: 5'-AAAC[revcomp(spacer)]C-3'
    For chip synthesis, the spacer is flanked by subpool-specific PCR primers.'''
    subpool_fwd = {
        1: 'GGAAAGGACGAAACACCG',   # subpool 1 forward primer + BsmBI overhang
        2: 'GAGGCACTGGGCAGGTACCG',
    }.get(subpool_idx, 'GGAAAGGACGAAACACCG')
    # First 33 nt of the Chen 2013 sgRNA(F+E) optimized scaffold. NOTE: lentiGuide-Puro (#52963)
    # and lentiCRISPRv2 (#52961) carry the ORIGINAL scaffold; F+E belongs to lentiCRISPRv2-Opti (#163126).
    scaffold_short = 'GTTTAAGAGCTATGCTGGAAACAGCATAGCAAG'
    oligo = subpool_fwd + spacer + scaffold_short
    if len(oligo) > 200:
        raise ValueError(f'Oligo length {len(oligo)} exceeds the 200 nt design budget; check the vendor limit')
    return oligo
```

**Subpool design:** A large synthesis pool can be partitioned into multiple sublibraries via subpool primers; each sub-PCR amplifies its subpool, allowing one synthesis batch to serve several screens. Typical subpool size: 10k-20k oligos.

## Library QC After Cloning

| Metric | Target | Failure mode if missed |
|--------|--------|------------------------|
| sgRNA detection (>25 reads/guide in plasmid pool) | ≥99% | Founder effect: missing guides cannot be screened; dropout impossible to distinguish from missing |
| Gini coefficient of plasmid pool | <0.1 | Synthesis defects or PCR bias; pool unfit for screening at standard 500x coverage |
| Skew ratio (top 10% / bottom 10%) | <2 (good), <5 (acceptable) | Skew >5 means underrepresented guides cannot generate statistical signal even at 1000x |
| % zero-count sgRNAs in plasmid pool | <0.5% | Plasmid bottleneck during cloning; re-amplify or re-clone |
| Replicate Pearson on plasmid pool (between sequencing technical replicates) | >0.99 | Sequencing artifact, not biology |

**Plasmid pool sequencing convention:** 200-500 reads per sgRNA before any biology (i.e. 15-40M reads for a 77k Brunello). This is the baseline against which all downstream depletion is computed; sequencing the plasmid is non-negotiable.

## Failure Modes

### Wrong TSS in CRISPRi/a library

**Trigger:** Using Ensembl/RefSeq TSS instead of empirical CAGE peak for genes with broad or non-canonical promoters.
**Mechanism:** dCas9-KRAB knockdown is maximal within ±100 bp of the actual Pol II loading site; canonical annotation can be off by 1-10 kb.
**Symptom:** "Easy" essentials (RPS, RPL, EIF) show normal dropout but newer genes don't; library validates poorly against CEGv2.
**Fix:** Re-derive TSS from FANTOM5 CAGE highest-rank peak; for tissue-specific lines, use matched CAGE or GRO-seq.

### Library skew from PCR bias during amplification

**Trigger:** Amplifying the cloned plasmid pool with too many PCR cycles (>20) or with high-GC-bias polymerase.
**Mechanism:** GC-extreme guides amplify nonlinearly; high-GC guides dominate, low-GC guides drop out.
**Symptom:** Gini >0.2 on plasmid pool; sgRNAs with GC <30% systematically depleted.
**Fix:** Cap PCR at 15 cycles; use Q5 or NEBNext Ultra II (low-bias); sequence at 500x post-amp to confirm Gini.

### Oligo-synthesis dropouts in low-complexity guides

**Trigger:** Chip-synthesis errors at homopolymer runs or guides starting with GGGG.
**Mechanism:** Synthesis chemistry has higher error rate at low-complexity regions; missing oligos cannot be cloned.
**Symptom:** Specific guides absent from plasmid pool despite no design-rule violation.
**Fix:** Re-design replacement guides; for production runs, request 2-3x synthesis depth so dropouts are buffered.

### Polyclonality from high MOI

**Trigger:** Infection at MOI >0.5 to "save cells."
**Mechanism:** Poisson math: at MOI 0.3, 26% of all cells are infected and 4% carry >=2 sgRNAs (14% of the infected fraction); at MOI 0.5, 39% are infected and 9% carry >=2.
**Symptom:** Hits include neutral genes that co-infect with true essentials.
**Fix:** MOI 0.3 strict; titer Cas9-positive cells specifically; re-check by qPCR of integration.

### Wrong control proportion

**Trigger:** <100 non-targeting controls in a 70k library.
**Mechanism:** Null distribution for normalization and FDR rests on the NTC variance; too few NTCs yields unstable median and inflated FDR.
**Symptom:** Erratic gene-level p-values; MAGeCK FDR fluctuates wildly between runs.
**Fix:** ~1% of library (500-1,000) NTCs; supplement with non-essential-gene controls.

## Quantitative Thresholds

| Threshold | Value | Source / Rationale |
|-----------|-------|--------------------|
| GC content | 30-70% | Doench 2016 Nat Biotech: guides outside this range have low activity |
| Poly-T avoidance | ≤3 consecutive T | U6 Pol III terminator; ≥4 Ts terminates sgRNA transcription |
| Guides per gene (Cas9) | 4 (Brunello/TKOv3 standard); up to 6 (Avana, older) | Doench 2016 reports diminishing gene recovery below 4 sgRNAs/gene; returns flatten above 6 |
| CRISPRi window | -50 to +300 search; +25 to +75 optimum | Sanson 2018 (Dolcetto); Horlbeck v2 uses -25 to +500 |
| CRISPRa window | -150 to -75 from TSS | Sanson 2018 (Calabrese); narrower than Horlbeck v2 (-550 to -25) |
| NTCs in library | ~1% (500-1,000 in a 70k library) | DepMap library design notes; rule-of-thumb for stable null |
| MOI | 0.3 | Poisson: P(>=2 sgRNAs/cell) = 4% at MOI 0.3 |
| Coverage at infection | 500 cells/sgRNA | DepMap convention; 200x minimum, 1000x for noisy / in-vivo |
| CRISPOR MIT specificity score | >=50 (higher = more specific) | CRISPOR convention (Haeussler 2016) |
| Library skew (top 10% / bottom 10%) | <2 ideal, <5 acceptable | Joung 2017 Nat Protoc |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| sgRNA fails to express | Poly-T in spacer terminates U6 | Filter `TTTT` in design; this is the #1 silent failure |
| CRISPRi guide gives no knockdown | Wrong TSS used | Re-derive TSS from FANTOM5 / matched CAGE |
| Library Gini >0.3 in plasmid pool | PCR over-amplification or synthesis defect | Cap at 15 cycles; re-sequence plasmid; consider re-synthesis |
| Hits include amplified loci (e.g. ERBB2 in HER2+) | Copy-number amplicon false-essentiality | See [[copy-number-correction]] |
| Paralog gene absent from hit list despite expression | Cas9 single-KO buffering | Switch to Cas12a multiplex; see [[combinatorial-screens]] |
| Cas12a oligo doesn't cut | Forgot Cas12a's TTTV PAM is 5' of spacer, not 3' | Re-orient: PAM-then-spacer for Cas12a, opposite of Cas9 |

## References

- Doench JG et al. 2014. *Nat Biotechnol* 32:1262. Rule Set 1.
- Doench JG et al. 2016. *Nat Biotechnol* 34:184. Rule Set 2, CFD, Brunello/Avana libraries.
- Sanjana NE et al. 2014. *Nat Methods* 11:783. GeCKOv2.
- Hart T et al. 2017. *G3* 7:2719. TKOv3 library; CEGv2/NEGv1 reference essentiality gene sets.
- Sanson KR et al. 2018. *Nat Commun* 9:5416. Dolcetto + Calabrese libraries; CRISPRi/a TSS rules.
- Horlbeck MA et al. 2016. *eLife* 5:e19760. CRISPRi/a design rules; Horlbeck v2 library.
- Kim HK et al. 2019. *Sci Adv* 5:eaax9249. DeepSpCas9.
- Xiang X et al. 2021. *Nat Commun* 12:3238. CRISPRon.
- Tycko J et al. 2019. *Nat Commun* 10:4063. Off-target toxicity mitigation in CRISPR screens.
- DeWeirdt PC et al. 2021. *Nat Biotechnol* 39:94. enAsCas12a optimization.
- Esmaeili Anvar N et al. 2024. *Nat Commun* 15:3577. Inzolia / in4mer paralog library.
- Dede M et al. 2020. *Genome Biol* 21:262. Paralog buffering invisible to Cas9 single-KO.
- Joung J et al. 2017. *Nat Protoc* 12:828. Genome-wide library screen protocol.
- Shalem O et al. 2014. *Science* 343:84. Original GeCKO genome-scale knockout library design.

## Related Skills

- crispr-screens/screen-qc - Validate library skew, Gini, replicate correlation
- crispr-screens/mageck-analysis - Analyze screens run with the designed library
- crispr-screens/combinatorial-screens - Cas12a multiplex / paralog-pair library design
- crispr-screens/base-editing-analysis - base-editor library design
- crispr-screens/prime-editing-screens - PRIDICT2-optimized pegRNA libraries
- crispr-screens/copy-number-correction - Filter amplicon-driven artifacts in cancer-cell-line screens
<!-- END FILE: crispr-screens/library-design/SKILL.md -->

## 子目录：crispr-screens/mageck-analysis

<!-- BEGIN FILE: crispr-screens/mageck-analysis/SKILL.md -->
---
name: bio-crispr-screens-mageck-analysis
description: Analyzes pooled CRISPR screens with MAGeCK (Li et al 2014), covering count generation (mageck count), the RRA two-condition workflow (mageck test using alpha-RRA over per-sgRNA negative-binomial p-values), the MLE multi-condition workflow (mageck mle with explicit design matrix and beta-score output), normalization choice (median vs total vs control-sgRNA vs spike-in), sgRNA efficiency injection, paired-sample testing, time-course design, drug-screen versus dropout-screen design matrices, MAGeCKFlute and MAGeCK-VISPR downstream visualization, and decision logic for when to use MAGeCK vs JACKS / BAGEL2 / drugZ / Chronos. Use when running a fresh CRISPR screen analysis, picking RRA vs MLE for the experimental design, choosing a normalization method from QC signatures, debugging MLE convergence failure or NaN beta scores, comparing MAGeCK output across tools, or building a batch-aware multi-cell-line / multi-condition MLE design matrix.
tool_type: cli
primary_tool: MAGeCK
---

## Version Compatibility

Reference examples tested with: MAGeCK 0.5.9+, MAGeCKFlute 2.0+ (R/Bioconductor), MAGeCK-VISPR 0.5.6+, pandas 2.2+, numpy 1.26+, matplotlib 3.8+.

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `mageck --version`, `mageck count --help`, `mageck test --help`, `mageck mle --help`
- R: `packageVersion('MAGeCKFlute')`, `?FluteRRA`, `?FluteMLE`

If code throws ImportError, AttributeError, or TypeError, introspect the installed package and adapt the example to match the actual API rather than retrying.

## MAGeCK CRISPR Screen Analysis

**"Run MAGeCK on my pooled CRISPR screen"** -> Count sgRNAs from FASTQ, normalize across samples, and rank genes by enrichment or depletion using either the robust rank aggregation (RRA) test for two-condition designs or the maximum-likelihood (MLE) model with explicit design matrix for multi-condition / time-course / drug screens.

- CLI: `mageck count` -> `mageck test` for two-condition RRA
- CLI: `mageck mle` for multi-condition / time-course / multi-cell-line MLE
- R: `MAGeCKFlute::FluteRRA()` / `FluteMLE()` for downstream visualization and pathway analysis
- Python: `mageck-vispr` for interactive QC + result dashboard

## RRA vs MLE Decision Tree

| Experimental design | Recommended | Why |
|---------------------|-------------|-----|
| Two conditions (e.g. drug vs vehicle, treated vs untreated), single cell line, no covariates | `mageck test` (RRA) | RRA is more robust to outlier sgRNAs; faster; default for most published screens |
| Time series (Day 0 -> Day 7 -> Day 14 -> Day 21) | `mageck mle` | RRA cannot model multiple timepoints jointly; MLE estimates per-condition beta scores |
| Multi-cell-line panel (e.g. DepMap-style 5-50 lines) | `mageck mle` with cell-line covariate, or Chronos | MLE handles >2 conditions; Chronos preferred at DepMap scale |
| Paired samples (each replicate matched donor/cell prep) | `mageck mle` with paired design | RRA does not support pairing |
| Combinatorial (treatment x cell line x time) | `mageck mle` with full factorial design | RRA only handles 1 factor |
| Drug screen (vehicle vs drug, multiple doses) | `mageck mle` with dose covariate OR drugZ (preferred for chemogenomic) | drugZ optimized for chemogenomic; see [[drugz-chemogenomic]] |
| Essentiality (Day 0 -> endpoint, single condition) | `mageck test` for simple dropout; `mageck mle` if multi-cell-line | RRA suffices; or BAGEL2 for Bayesian essentiality; see [[bagel-essentiality]] |
| Multi-batch / multi-screen joint analysis | `mageck mle` with batch covariate, JACKS for guide efficacy, or Chronos | See [[batch-correction]] |

**Fails when:**
- Using RRA for time-series and treating each timepoint as a separate test: false-discovery inflation from un-modeled temporal correlation. Use MLE.
- Using MLE without explicit design matrix in a screen with severe batch effects: beta scores include batch variance. Add batch covariate.
- Using MAGeCK for drug screens without vehicle control: comparing drug vs Day 0 conflates drug effect with proliferation. Compare drug vs vehicle, not Day 0. See [[drugz-chemogenomic]].

## The RRA Algorithm (under the hood)

**Why this matters for postdoc-level use:** RRA is not "non-parametric"; it tests whether per-gene sgRNA p-value ranks are more clustered toward the extremes than expected under the uniform null. The chain:

1. `mageck count` normalizes raw counts (median by default) and outputs `*.count_normalized.txt`.
2. `mageck test` computes a per-sgRNA p-value under a NB model fitted to per-gene variance (mean-variance trend stabilized via empirical Bayes shrinkage; same family as edgeR/DESeq2 but simpler dispersion estimation).
3. Per-sgRNA p-values are ranked; ranks are normalized to percentile (rho).
4. For each gene with k sgRNAs, the alpha-RRA score is the minimum over `Pr(beta(i, k-i+1) <= rho_i)` for i in 1..k -- the probability of observing the i-th smallest rank in a uniform sample.
5. Gene-level p-value is computed by permuting sgRNA-to-gene assignment to derive an empirical null over alpha-RRA scores.
6. Multiple-testing correction is Benjamini-Hochberg.

**Critical assumption:** RRA assumes most sgRNAs are non-changing (used to estimate the NB dispersion). If >40% of sgRNAs change, median normalization fails and the dispersion estimate is biased. Symptom: every gene appears significant. Fix: use control-sgRNA normalization (`--norm-method control`) with non-targeting controls as the reference.

## The MLE Model (under the hood)

**Why this matters:** MLE assumes the per-sgRNA log-count is Negative-Binomial with mean determined by a linear combination of condition betas plus an sgRNA-efficiency term (if supplied). The chain:

1. Define a design matrix where rows are samples and columns are conditions; entries are 1 if the sample belongs to the condition, 0 otherwise. A baseline column (all 1s) is required.
2. Per-gene, the model is `log(count_ij) = baseline_i + sum_c (beta_gc * design_jc) + log(sgrna_efficiency_i) + log(size_factor_j)` where i is sgRNA, j is sample, c is condition.
3. The optimizer finds the per-gene beta_gc maximizing the NB likelihood; per-gene Wald-statistic gives a p-value per condition.
4. Each beta represents the log-fold-change in that condition relative to baseline, accounting for sgRNA efficiency.

**Critical assumption:** Beta scores are interpretable only when the design matrix is correctly specified. A common error is omitting batch as a covariate -- the resulting betas absorb batch variance. The fix is to add batch columns; the betas then estimate biology after batch adjustment.

**Convergence failure:** MLE NaN beta scores indicate optimizer divergence -- usually because a gene has too few sgRNAs with non-zero counts in the relevant conditions. The output includes such genes with NaN; do not interpret them as zero effect.

## Count sgRNAs from FASTQ

**Goal:** Quantify sgRNA representation from raw sequencing data.

**Approach:** Run `mageck count` to map FASTQ reads to the sgRNA library reference, producing a normalized count matrix and QC summary. Set `--norm-method median` (default; robust to outliers) or `--norm-method control` (when many sgRNAs change).

```bash
mageck count \
    --list-seq library.csv \                       # sgRNA library: sgRNA id, sequence, gene (in that order)
    --sample-label Plasmid,Day0,Veh_r1,Veh_r2,Drug_r1,Drug_r2 \
    --fastq Plasmid.fq.gz Day0.fq.gz Veh_r1.fq.gz Veh_r2.fq.gz Drug_r1.fq.gz Drug_r2.fq.gz \
    --norm-method median \                         # see normalization decision below
    --output-prefix screen \
    --trim-5 AUTO                                  # length(s) to trim from 5' end; AUTO detects it (int or comma-list also accepted)

# Outputs:
#   screen.count.txt           raw counts
#   screen.count_normalized.txt normalized counts (median-scaled)
#   screen.countsummary.txt    per-sample QC: Gini, reads, mapping rate, % zero-count
#   screen.log                  per-FASTQ mapping stats
```

**Library file format (tab- or comma-separated; first row is header):**

```
sgRNA,Sequence,Gene
BRCA1_1,ATGGATTTATCTGCTCTTCG,BRCA1
BRCA1_2,CAGCAGATACTTGATGCATC,BRCA1
NTC_0001,GACGCATCGAATCAATAGCC,NonTargeting_0001
```

## Normalization Decision

| `--norm-method` | When to use | Mechanism | Fails when |
|------------------|-------------|-----------|------------|
| `median` (default) | Standard screen, <40% guides change | Scale each sample to a common median of all guides | Heavy selection (>40% guides change) inflates median, biasing scaling |
| `total` | Equal sequencing depth assumed, no outliers | Scale to total reads | Sensitive to PCR jackpots / outlier high-count guides |
| `none` | Already-normalized inputs (DEPRECATED for raw FASTQ counting) | Skips scaling | Almost never appropriate; only for already-normalized inputs |
| `control` | Heavy selection screens; library has ≥500 NTCs | Scale each sample so non-targeting controls have constant median | Requires `--control-sgrna ntcs.txt` listing NTC sgRNAs |

**Diagnostic:** Run with `median` first. If essentialome PR-AUC against CEGv2 is high and Gini is in range, accept. If PR-AUC <0.5 despite reasonable Gini, retry with `control` -- this isolates whether median normalization was masking the signal.

## MAGeCK Test (RRA for Two-Condition)

**Goal:** Identify genes significantly enriched or depleted between treatment and control.

**Approach:** Compute per-sgRNA NB-model p-values, rank, apply alpha-RRA to get per-gene scores, permute for gene-level FDR. Outputs separate columns for positive and negative selection.

```bash
mageck test \
    --count-table screen.count.txt \
    --treatment-id Drug_r1,Drug_r2 \
    --control-id Veh_r1,Veh_r2 \
    --norm-method median \
    --output-prefix drug_vs_veh \
    --gene-lfc-method median \                     # alternative: mean (less robust)
    --sort-criteria pos                            # rank for positive selection (choices: neg, pos; default neg)
# Outputs: drug_vs_veh.gene_summary.txt (gene-level), drug_vs_veh.sgrna_summary.txt
```

**Gene-summary columns:**

| Column | Meaning |
|--------|---------|
| `id` | Gene symbol |
| `num` | Number of sgRNAs in library for this gene |
| `neg|score`, `pos|score` | alpha-RRA score, negative- or positive-selection direction |
| `neg|p-value`, `pos|p-value` | Permutation p-value |
| `neg|fdr`, `pos|fdr` | BH-corrected FDR |
| `neg|rank`, `pos|rank` | Rank by score (1 = top hit in that direction) |
| `neg|lfc`, `pos|lfc` | Median log-fold-change of sgRNAs in that direction |

**Interpretation rule:** A gene is a strong essential if `neg|fdr < 0.05` AND `neg|lfc < -1`. A gene is a strong resistance hit if `pos|fdr < 0.05` AND `pos|lfc > 1`. Genes with `fdr < 0.05` but `|lfc| < 0.5` are statistically significant but biologically weak -- worth flagging for orthogonal validation.

## MAGeCK MLE (Multi-Condition)

**Goal:** Estimate gene effects across complex experimental designs with multiple conditions, time points, batches, or covariates.

**Approach:** Specify a design matrix mapping samples to conditions, then run `mageck mle` which fits a NB GLM with sgRNA-efficiency term and outputs per-gene per-condition beta scores.

```bash
# Design matrix: design.txt (tab-separated)
# Samples must match sample-label in mageck count output
# baseline column must be present and all 1
cat > design.txt <<EOF
Samples	baseline	day7	day14	day21
Day0	1	0	0	0
Day7_r1	1	1	0	0
Day7_r2	1	1	0	0
Day14_r1	1	0	1	0
Day14_r2	1	0	1	0
Day21_r1	1	0	0	1
Day21_r2	1	0	0	1
EOF

mageck mle \
    --count-table screen.count.txt \
    --design-matrix design.txt \
    --output-prefix timecourse_mle \
    --norm-method median \
    --sgrna-efficiency efficiency.txt \            # OPTIONAL: from JACKS or library design
    --sgrna-eff-name-column 0 \                    # 0-based; 0 is the default
    --sgrna-eff-score-column 1 \                   # 0-based; 1 is the default
    --max-sgrnapergene-permutation 40              # skip genes with more sgRNAs than this (default 40)
# Outputs: timecourse_mle.gene_summary.txt with beta scores per condition + Wald p-values
```

**Gene-summary columns (MLE):**

| Column | Meaning |
|--------|---------|
| `Gene` | Gene symbol |
| `sgRNA` | Number of sgRNAs |
| `<condition>|beta` | Effect-size estimate (log-fold-change relative to baseline) |
| `<condition>|z` | Wald z-statistic |
| `<condition>|p-value` | Two-sided p-value |
| `<condition>|fdr` | BH-corrected FDR |
| `<condition>|wald-fdr` | Wald-statistic-based FDR (alternative) |

**Interpretation rule:** Beta scores are log2-fold-changes; a beta of -1 in condition day21 means sgRNAs are 2-fold depleted in day-21 relative to baseline. NaN betas indicate convergence failure (typically a gene with too few non-zero counts in that condition); exclude from interpretation.

## Sample MAGeCK Test for Drug Screen with sgRNA Efficiency

```bash
mageck test \
    --count-table screen.count.txt \
    --treatment-id Drug_r1,Drug_r2,Drug_r3 \
    --control-id Veh_r1,Veh_r2,Veh_r3 \
    --norm-method control \                         # NTCs as normalization reference
    --control-sgrna ntcs.txt \                      # one NTC sgRNA per line
    --gene-lfc-method median \
    --variance-estimation-samples Day0_r1,Day0_r2 \  # estimate variance from these samples
    --output-prefix drug_screen_normalized
# --sgrna-efficiency / --sgrna-eff-name-column / --sgrna-eff-score-column are `mageck mle` options,
# not `mageck test` options; pass them to mle if guide-efficacy weighting is needed.
```

**Reading order:** Run `mageck count` -> screen-qc skill for QC -> `mageck test` or `mageck mle` -> `MAGeCKFlute` for visualization -> downstream pathway analysis.

## Time-Course Analysis

**Goal:** Identify genes with consistent depletion or enrichment across multiple time points.

**Approach:** Run `mageck mle` with a design matrix where each timepoint is a separate column, then test for monotonic trends in per-condition beta scores.

```python
import pandas as pd
import numpy as np

def time_course_consistency(mle_results, conditions=['day7', 'day14', 'day21']):
    '''Identify genes with monotonic beta trends across timepoints.
    Returns genes where all betas same sign and trend is monotone.'''
    beta_cols = [f'{c}|beta' for c in conditions]
    fdr_cols = [f'{c}|fdr' for c in conditions]
    df = mle_results[['Gene'] + beta_cols + fdr_cols].copy()
    df['all_negative'] = (df[beta_cols] < 0).all(axis=1)
    df['all_positive'] = (df[beta_cols] > 0).all(axis=1)
    df['monotone'] = df[beta_cols].apply(lambda x: (np.diff(x) <= 0).all() or (np.diff(x) >= 0).all(), axis=1)
    df['any_sig'] = (df[fdr_cols] < 0.05).any(axis=1)
    return df[df['monotone'] & df['any_sig']].sort_values(beta_cols[-1])
```

## Visualizing Results

**Goal:** Generate publication-grade volcano plot and rank plot of MAGeCK output.

**Approach:** Load gene_summary.txt, plot `-log10(fdr)` vs LFC, color by significance, annotate top hits.

```python
import matplotlib.pyplot as plt
import numpy as np

def volcano(gene_summary_path, direction='neg', fdr_threshold=0.05, lfc_threshold=1.0):
    '''direction: "neg" for dropout, "pos" for enrichment.'''
    df = pd.read_csv(gene_summary_path, sep='\t')
    lfc_col = f'{direction}|lfc'
    fdr_col = f'{direction}|fdr'
    fig, ax = plt.subplots(figsize=(9, 7))
    sig = (df[fdr_col] < fdr_threshold) & (np.abs(df[lfc_col]) > lfc_threshold)
    ax.scatter(df.loc[~sig, lfc_col], -np.log10(df.loc[~sig, fdr_col].clip(lower=1e-10)),
                c='lightgray', alpha=0.4, s=10)
    ax.scatter(df.loc[sig, lfc_col], -np.log10(df.loc[sig, fdr_col].clip(lower=1e-10)),
                c='red' if direction == 'neg' else 'blue', alpha=0.7, s=18)
    top = df.loc[sig].nsmallest(15, fdr_col)
    for _, r in top.iterrows():
        ax.annotate(r['id'], (r[lfc_col], -np.log10(max(r[fdr_col], 1e-10))), fontsize=7)
    ax.axhline(-np.log10(fdr_threshold), ls='--', c='black', lw=0.5)
    ax.axvline(0, c='gray', lw=0.5)
    ax.set_xlabel(f'{direction} LFC')
    ax.set_ylabel(f'-log10({direction} FDR)')
    return fig
```

## MAGeCKFlute Integration (R)

**Goal:** Use the canonical pathway-analysis dashboard for downstream visualization.

**Approach:** Load MAGeCK output in R, run FluteRRA or FluteMLE, which produces volcano, rank, square-plot, and KEGG/Reactome enrichment.

```r
library(MAGeCKFlute)
# After mageck test
FluteRRA(gene_summary = "drug_vs_veh.gene_summary.txt",
         sgrna_summary = "drug_vs_veh.sgrna_summary.txt",
         organism = "hsa",
         outdir = "flute_output/")

# After mageck mle
FluteMLE(gene_summary = "timecourse_mle.gene_summary.txt",
         treatname = "day21", ctrlname = "baseline",
         organism = "hsa",
         outdir = "flute_mle_output/")
```

## MAGeCK-VISPR Interactive Dashboard

```bash
mageck-vispr init my_screen
# Edit config.yaml to point to counts + library
snakemake --cores 8                 # mageck-vispr generates a Snakemake workflow; run it with snakemake
vispr server results/*.vispr.yaml   # serve the interactive dashboard
```

## Failure Modes

### NaN beta scores in MLE output

**Trigger:** A gene has fewer than 2 non-zero-count sgRNAs in the relevant condition.
**Mechanism:** MLE optimizer cannot fit beta when likelihood is flat (insufficient evidence).
**Symptom:** `mle.gene_summary.txt` shows NaN in specific gene-condition cells.
**Fix:** Filter these genes from downstream interpretation; they are not "zero effect" but undetermined. If many genes show NaN, the screen depth is too low or many guides have failed -- audit with screen-qc.

### Every gene appears significant after RRA

**Trigger:** >40% of sgRNAs change direction (heavy selection screen).
**Mechanism:** Median normalization assumes most guides are non-changing; under heavy selection, median is biased and dispersion estimation breaks.
**Symptom:** Thousands of "hits" at FDR <0.05; volcano plot looks like a U with no separation.
**Fix:** Switch to `--norm-method control` with non-targeting controls; or use BAGEL2 / Chronos for essentiality analysis (`mageck` is not designed for screens with high-fraction true essentiality).

### MLE beta absorbs batch variance

**Trigger:** Multi-batch screen run without explicit batch covariate in design matrix.
**Mechanism:** Without a batch column, beta_condition includes both biological signal and batch difference between conditions.
**Symptom:** Beta scores differ between batches for the same biological condition; PCA shows samples cluster by batch not condition.
**Fix:** Add batch covariate columns to design matrix (e.g., one column per batch indicator); the biological betas are then estimated after batch adjustment. See [[batch-correction]].

### sgRNA-efficiency injection makes scores worse

**Trigger:** Supplied JACKS efficiency scores from a different cell line / chemistry than the current screen.
**Mechanism:** sgRNA efficacy is cell-line and modality dependent; HEK293T efficiency is not HCT116 efficiency; Cas9 efficiency is not CRISPRi efficiency.
**Symptom:** Some genes that were hits without efficiency become non-significant with efficiency.
**Fix:** Use efficiency derived from JACKS run on the matching cell line / library / chemistry, or use no efficiency (treat all sgRNAs as equal).

### Lack of cell-line covariate in multi-line screen

**Trigger:** Running `mageck mle` on multiple cell lines without a cell-line indicator column.
**Mechanism:** Each cell line has different essentiality profile; combining without indicator pools variance and dilutes per-line signal.
**Symptom:** Per-line known essentials don't show up; results look like a meta-analysis without effect sizes.
**Fix:** Add cell-line indicator columns; or move to Chronos which models cell-line and screen-quality jointly (see [[hit-calling]]).

## Reconciliation: When MAGeCK Disagrees With Other Tools

| Pattern | Likely cause | Action |
|---------|--------------|--------|
| MAGeCK FDR significant, BAGEL2 Bayes factor not | Different reference set; BAGEL2 trained on CEGv2/NEGv1 | Trust BAGEL2 for essentiality calling; MAGeCK for general LFC |
| MAGeCK significant, JACKS not | JACKS down-weighted noisy guides; MAGeCK trusts all 4 | Inspect per-sgRNA scores; if one sgRNA dominates, JACKS is right |
| MAGeCK and Chronos agree at top 100; disagree at 100-300 | Chronos accounts for CN and screen quality; MAGeCK does not | Trust Chronos for cancer-line screens; MAGeCK lacks CN correction |
| MAGeCK significant, drugZ not | drugZ uses bidirectional Z; MAGeCK uses RRA | For chemogenomic, trust drugZ (vehicle-anchored) |
| RRA and MLE disagree on same data | RRA more robust to outliers; MLE more sensitive | Higher-ranked hits in both = high confidence; only-one-method = orthogonal validate |

## Quantitative Thresholds

| Threshold | Value | Source / Rationale |
|-----------|-------|--------------------|
| Hit FDR (gene-level) | <0.05 | MAGeCK paper Li 2014; standard |
| Hit LFC magnitude | >1 (2-fold) | Biologically interpretable effect size; FDR-only hits at low LFC need validation |
| Normalization fraction-changing threshold | <40% guides change for median norm | Median-normalization assumption (most guides unchanged) |
| sgRNAs needed for reliable MLE | ≥3 per gene with non-zero counts in each condition | MAGeCK 0.5+ behavior; below this, NaN |
| Time-course conditions for MLE | ≥3 (otherwise use test) | MLE statistical power |
| PR-AUC of ranked hits against CEGv2 | >0.7 for "passing" essentiality screen | Community convention (CEGv2 from Hart 2017); see [[screen-qc]] |
| RRA permutation passes per gene | 100 default; raise via `--additional-rra-parameters "--permutation N"` | Not exposed directly on `mageck test`; trades runtime |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| `mageck count` outputs mostly zero counts | Library column order swapped, or wrong `--trim-5` length | Library must be sgRNA id, sequence, gene; try `--trim-5 AUTO` |
| All genes significant | Median normalization break (heavy selection) | `--norm-method control` |
| NaN beta in MLE | Gene with insufficient non-zero counts | Exclude from interpretation |
| Two-condition MLE works but ranks differ from RRA | Different test statistic | Both correct; check direction and use the appropriate one |
| Hits include amplified genes | No CN correction | See [[copy-number-correction]] |
| Library not detected in screen.countsummary.txt | Library file format wrong | Check column order is sgRNA id, sequence, gene (no spaces) |

## References

- Li W et al. 2014. *Genome Biol* 15:554. MAGeCK; original alpha-RRA algorithm.
- Li W et al. 2015. *Genome Biol* 16:281. MAGeCK-VISPR; QC + visualization.
- Wang B et al. 2019. *Nat Protoc* 14:756. MAGeCKFlute pathway analysis.
- Joung J et al. 2017. *Nat Protoc* 12:828. Screen protocol.
- Hart T et al. 2017. *G3* 7:2719. CEGv2/NEGv1 reference sets for benchmarking.

## Related Skills

- crispr-screens/screen-qc - Pre-MAGeCK QC; gates whether to use median or control normalization
- crispr-screens/jacks-analysis - Joint efficacy + essentiality; alternative to MLE
- crispr-screens/bagel-essentiality - BAGEL2 Bayes-factor calling; alternative for essentiality
- crispr-screens/drugz-chemogenomic - drugZ for chemogenomic screens; alternative for drug screens
- crispr-screens/hit-calling - Cross-method decision tree
- crispr-screens/copy-number-correction - CRISPRcleanR / Chronos for cancer-line CN correction
- crispr-screens/batch-correction - Multi-batch design-matrix construction
- pathway-analysis/gsea - Downstream GSEA on ranked hits
- pathway-analysis/go-enrichment - GO enrichment of hit lists
<!-- END FILE: crispr-screens/mageck-analysis/SKILL.md -->

## 子目录：crispr-screens/perturb-seq-analysis

<!-- BEGIN FILE: crispr-screens/perturb-seq-analysis/SKILL.md -->
---
name: bio-crispr-screens-perturb-seq-analysis
description: Analyzes single-cell pooled CRISPR screens (Perturb-seq, CROP-seq, Perturb-CITE-seq, ECCITE-seq, multiome) where each cell carries an sgRNA and a scRNA-seq / surface-protein / chromatin readout. Covers experimental design (direct-capture Perturb-seq Dixit 2016 vs CROP-seq 3'UTR-barcoded Datlinger 2017 vs ECCITE-seq vs Multiome), MOI for sgRNA assignment, escaper-cell filtering (Mixscape, Papalexi 2021), SCEPTRE NB GLM + permutation for low-MOI (Barry 2024 Genome Biol 25:124), the Pertpy framework, factor decomposition, genome-scale Perturb-seq (Replogle 2022 Cell, 2.5M cells), and per-perturbation single-cell DE. Use when running a single-cell CRISPR screen, choosing direct-capture vs CROP-seq architecture, filtering escaper cells, performing single-cell DE, integrating Perturb-seq with pathway analysis, scaling to GW CRISPRi via Replogle protocol, or analyzing multi-omics screens.
tool_type: python
primary_tool: Pertpy
---

## Version Compatibility

Reference examples tested with: Pertpy 0.6+, SCEPTRE 0.10+ (R / katsevich-lab/sceptre), Mixscape via Seurat 4.3+ or Pertpy, scanpy 1.10+, anndata 0.10+, pandas 2.2+, numpy 1.26+, scipy 1.12+.

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show pertpy scanpy anndata`
- R: `packageVersion('sceptre')`; `?sceptre`; `?Seurat::PrepLDA`

If code throws ImportError, AttributeError, or TypeError, introspect the installed package and adapt the example to match the actual API rather than retrying.

## Single-Cell Perturb-Seq Analysis

**"Analyze a single-cell pooled CRISPR perturbation screen"** -> Assign sgRNAs to cells, filter unperturbed escapers, normalize counts, fit per-gene differential expression conditioned on perturbation, and rank perturbations by their molecular effect.

- Python: `pertpy` unified framework for Mixscape + SCEPTRE-via-R + differential expression
- R: `sceptre` for low-MOI NB GLM + permutation testing
- Python/R: `Seurat::MixscapeLDA` and downstream

## Experimental Architecture Comparison

| Method | Year | Architecture | Readout | MOI | Single-cell sgRNA detection |
|--------|------|--------------|---------|-----|------------------------------|
| Perturb-seq (Dixit 2016, *Cell*) | 2016 | sgRNA expressed in cassette; direct PCR capture | scRNA-seq | Low-to-moderate (MOI ~0.35-1.4; a minority of cells receive multiple guides, enabling epistasis analysis) | Yes via amplicon-PCR pre-sequencing |
| CROP-seq (Datlinger 2017, *Nat Methods*) | 2017 | hU6-sgRNA cassette placed in the 3' LTR of lentiGuide-Puro; LTR duplication puts the sgRNA in the 3'UTR of the Pol II puromycin-resistance transcript | scRNA-seq | Low (1-2 sgRNAs/cell) | Native via 10X 3' chemistry |
| Perturb-CITE-seq (Frangieh 2021, *Nat Genet*) | 2021 | Adds surface-protein hashtag oligos to CROP-seq | scRNA-seq + ADT (protein) | Low | CROP-seq architecture |
| ECCITE-seq (Mimitou 2019, *Nat Methods*) | 2019 | Surface-protein hashtag with sgRNA-marked cells | scRNA-seq + ADT | Low | Hash + sgRNA |
| Perturb-ATAC (Rubin 2019, *Cell*) | 2019 | scATAC-seq readout | scATAC | Low | sgRNA capture via separate library prep |
| Perturb-multiome (10X) | 2021+ | scRNA + scATAC simultaneously | scRNA + ATAC | Low | Direct capture from sgRNA cassette |
| Replogle GW Perturb-seq (2022, *Cell*) | 2022 | Multiplexed CRISPRi with sgRNA barcoding | scRNA-seq | 1 sgRNA/cell | Direct capture |

**Decision rule:** For genome-wide CRISPRi screens, Replogle's CRISPRi + 10X 3' direct-capture protocol is the gold standard (>2.5M cells; the genome-scale K562 screen targeted ~9,866 expressed genes in Replogle 2022). For protein readout, Perturb-CITE-seq. For chromatin, Perturb-multiome. For low-throughput pilot, original Dixit Perturb-seq.

## MOI and sgRNA Assignment

**The central technical challenge:** Each cell must receive exactly one sgRNA (otherwise the perturbation is undefined). At MOI 0.3, ~26% of cells get ≥1 sgRNA, but 4% get ≥2; the cells with multiple sgRNAs must be filtered or analyzed as combinatorial perturbations.

**Assignment workflow:**

1. **Detect sgRNA reads per cell:** From the sgRNA library prep (direct capture or 3'UTR barcode), count reads per sgRNA per cell.
2. **Threshold:** Most pipelines use 10+ reads of one sgRNA to assign that perturbation.
3. **Multiplets:** Cells with 2+ sgRNAs at >10 reads each are either multi-perturbed (analyzable as combinatorial) or doublets.
4. **Doublet detection:** Use scDblFinder, Scrublet, or AMULET (multiome) to identify doublets independently from sgRNA assignment.

**Goal:** Assign a single perturbation identity (or 'multiplet'/'none') to every cell from the sgRNA counts matrix.

**Approach:** Threshold per-cell sgRNA reads at ≥10 (Pertpy convention); cells exceeding the threshold for exactly one sgRNA are assigned that perturbation; cells with multiple sgRNAs above threshold are flagged as multiplets for filtering or combinatorial analysis.

```python
# sgRNA assignment via threshold counting
def assign_sgrna(adata, sgrna_counts_layer='sgrna_counts', threshold=10):
    '''Per-cell sgRNA assignment. Returns single assignment or 'multiplet'/'none'.'''
    import numpy as np
    counts = adata.layers[sgrna_counts_layer]  # cells x sgRNAs
    above_thresh = counts >= threshold
    n_sgrna_per_cell = above_thresh.sum(axis=1)
    assignments = np.where(
        n_sgrna_per_cell == 0, 'none',
        np.where(n_sgrna_per_cell == 1,
                  [adata.var_names[i] for i in counts.argmax(axis=1)],
                  'multiplet'))
    adata.obs['sgrna_assignment'] = assignments
    return adata
```

## Escaper Cell Filtering (Mixscape)

**Why this matters:** Not all sgRNA-positive cells actually edit. The escaper fraction is guide- and gene-dependent: Papalexi 2021 measured ~25% escapers for IFNGR2, perturbation rates of 39-92% across four IRF1 guides (i.e. 8-61% escapers), and no detectable perturbation at all for 15 genes. Including escapers dilutes the perturbation effect; Mixscape identifies and filters them.

**Mixscape algorithm:** For each perturbed cell, compute a "perturbation signature" = (its expression) - (mean of K nearest non-targeting-control cells). This signature isolates the perturbation effect from cell-state variation. Cells with perturbation signature similar to NTC distribution are escapers.

```python
import pertpy as pt
import scanpy as sc

# adata is a scRNA-seq AnnData with 'sgrna_assignment' column
# Pertpy 0.6+ Mixscape API (verify against installed pertpy with help(pt.tl.Mixscape))
mixscape = pt.tl.Mixscape()
mixscape.perturbation_signature(
    adata=adata,
    pert_key='sgrna_assignment',     # .obs column with sgRNA target per cell
    control='NTC',                   # name of non-targeting control in pert_key column
    n_neighbors=20,                  # K neighbors for KNN-NTC subtraction
)
# Writes .layers['X_pert'] with perturbation-signature-corrected expression

# Filter escapers: classify perturbed cells as KO (true perturbation) or NP (non-perturbed/escaper)
mixscape.mixscape(
    adata=adata,
    pert_key='sgrna_assignment',     # pert_key (not 'labels' in modern pertpy)
    control='NTC',
    new_class_name='mixscape_class', # .obs column to write
)
# Defaults to layer='X_pert' (output of perturbation_signature)

# Keep only KO cells for downstream analysis
adata_ko = adata[adata.obs['mixscape_class_global'].isin(['KO'])   # mixscape_class holds '<gene> KO'; the bare label is in mixscape_class_global].copy()
print(f'KO cells: {adata_ko.n_obs} ({adata_ko.n_obs/adata.n_obs:.1%} of perturbed)')
```

**Critical:** Mixscape can fail when the perturbation has weak phenotype; empirically Mixscape detects perturbations with log-fold-change <-0.5 (depletion) reliably, but weaker effects collapse into the NTC distribution. For genome-wide screens, run Mixscape per perturbation; for low-effect perturbations, trust the assignment without filtering.

## SCEPTRE for Low-MOI Differential Expression

**Why this matters:** Standard differential-expression tools (DESeq2, MAST) assume Gaussian-mixture distribution and fail at single-cell scale with sparse, zero-inflated data. SCEPTRE (Katsevich Lab, 2021; low-MOI variant Barry 2024 Genome Biol) uses a negative-binomial GLM with conditional resampling:

1. Per gene, fit NB GLM: `log(expr_g) ~ pert_indicator + technical_factors`
2. Compute z-score for the perturbation coefficient
3. Resample the pert_indicator (conditional on counts) 500-1000 times; compute permutation null
4. Get FDR via permutation; not parametric

```r
library(sceptre)

# Input: sce object or sparse matrix + metadata
# Required: gene_expression_matrix, perturbation_indicator (binary per cell per pert),
#           technical_factors (batch, n_genes, etc.)

# For each gene + perturbation pair:
# Current sceptre API is a pipeline of composable steps:
sceptre_object <- import_data(response_matrix, grna_matrix, grna_target_data_frame,
                              moi = 'low', extra_covariates = covariates_df)
sceptre_object <- set_analysis_parameters(sceptre_object, discovery_pairs = pairs_df)
sceptre_object <- assign_grnas(sceptre_object)
sceptre_object <- run_qc(sceptre_object)
sceptre_object <- run_calibration_check(sceptre_object)
sceptre_object <- run_discovery_analysis(sceptre_object)
results <- get_result(sceptre_object, analysis = 'run_discovery_analysis')
# Output: per-gene-per-pert p-value, log-fold-change, FDR
```

**Advantage over MAST:** SCEPTRE's permutation NB GLM is the only method that maintains calibrated FDR in pooled-screen scRNA-seq (Barry 2024 benchmark). MAST and Wilcoxon are over-confident due to data sparsity.

## Pertpy Unified Framework

**Pertpy** (https://pertpy.readthedocs.io) integrates Mixscape, distance-based perturbation comparison, EdgeR/PyDESeq2/WilcoxonTest DE, and factor models in a single AnnData-based interface. For SCEPTRE specifically, invoke the R sceptre package separately (Pertpy does not wrap it).

```python
import pertpy as pt
import scanpy as sc

# Load data
mdata = pt.dt.papalexi_2021()      # returns a MuData object
adata = mdata['rna']  # built-in example from Mixscape paper

# Standard scRNA-seq preprocessing (scanpy)
sc.pp.normalize_total(adata, target_sum=1e4)
sc.pp.log1p(adata)
sc.pp.highly_variable_genes(adata, n_top_genes=2000)

# Mixscape escaper filtering (writes .layers['X_pert'] and .obs['mixscape_class'])
ms = pt.tl.Mixscape()
ms.perturbation_signature(adata, pert_key='perturbation', control='NT', n_neighbors=20)
ms.mixscape(adata, pert_key='perturbation', control='NT')

# Filter to KO cells
adata_ko = adata[adata.obs['mixscape_class'].isin(['KO', 'NT'])].copy()

# Pseudobulk differential expression via pertpy (PyDESeq2 backend)
de = pt.tl.PyDESeq2(adata_ko, design='~perturbation')
de.fit()
results_df = de.test_contrasts(contrast=('perturbation', 'GENE_X', 'NT'))

# For calibrated SCEPTRE on low-MOI single-cell data, use R sceptre directly
# (Barry 2024 Genome Biol; not bundled in pertpy)
```

## Genome-Wide Perturb-Seq (Replogle 2022)

**Replogle 2022 *Cell* 185:2559** demonstrated genome-wide Perturb-seq:
- >2.5M cells total; the genome-scale K562 screen targeted ~9,866 expressed genes (with a 2,057-gene essential subset)
- CRISPRi via dCas9-KRAB
- Native 10X 3' direct-capture for sgRNA
- Median >100 cells per perturbation as screened (Replogle 2022)
- Cluster-based analysis of perturbed cells reveals gene-program organization

**Scaling principles:**
- Cells per perturbation: 500-1,000 minimum for stable DE
- 10X channels: 10-30 channels at 5,000-10,000 cells each
- Cost: ~$50-100K for genome-scale

```python
# Replogle-style genome-wide design
# Each cell -> 1 library element (low MOI)
# Each gene -> 1 dual-sgRNA CRISPRi element (2 distinct sgRNAs per element)
# Replogle 2022 retained >2.5M cells at a median >100 cells per perturbation
# Total: ~9,900 expressed genes x 1 element = ~9,900 elements

```

## Factor-Based Analysis

For complex perturbation responses, decompose the per-cell perturbation effect into shared latent factors:

```python
import pertpy as pt

# FR-Perturb ("Factorize-Recover") decomposes perturbation effects into shared factors.
# It is NOT part of pertpy: it is a standalone CLI from douglasyao/FR-Perturb
# (Yao et al. 2023 Nat Biotechnol). Run it outside Python:
#   python run_FR_Perturb.py --input <expression> --perturbations <matrix> --out <prefix>
```

## Multiomic Perturb-seq (RNA + ATAC)

**For chromatin readout:** Use 10X Multiome with CRISPRi/a; sgRNA assignment via the same scATAC-seq library.

```python
# Multiome: scRNA + scATAC + sgRNA
# Use ArchR or Signac for ATAC integration
# Use Pertpy for RNA-side DE
import muon as mu
mdata = mu.MuData({'rna': adata_rna, 'atac': adata_atac})
# Joint differential analysis across modalities
```

## Failure Modes

### Low sgRNA detection per cell

**Trigger:** Direct-capture method on CROP-seq library, or 3'UTR barcoding on direct-capture library.
**Mechanism:** Architecture mismatch -- the sgRNA can't be detected by the wrong library prep.
**Symptom:** sgRNA assignment rate <50% of cells.
**Fix:** Match library prep to architecture; for CROP-seq, use 10X 3' chemistry; for direct-capture Perturb-seq, use the Dixit amplicon-PCR pre-sequencing.

### Mixscape filters too many cells as escapers

**Trigger:** Weak perturbation phenotype; Mixscape's NTC-subtracted signature is similar to NTC null.
**Mechanism:** Mixscape assumes a detectable signal; weak knockdown is misclassified as escaper.
**Symptom:** >50% of perturbed cells classified as "NP" (non-perturbed); known essentials show no effect.
**Fix:** Lower Mixscape stringency; skip Mixscape for low-effect perturbations; verify Cas9 expression first.

### Doublet contamination drives apparent multi-perturbation cells

**Trigger:** High cell density loading on 10X channels.
**Mechanism:** Two cells in one droplet appear to carry two sgRNAs.
**Symptom:** "Multiplet" rate >5% after sgRNA assignment.
**Fix:** Reduce cell loading per channel (5,000-7,000 instead of 10,000); run Scrublet or scDblFinder; remove doublets before sgRNA assignment.

### MAST or Wilcoxon over-call hits

**Trigger:** Using parametric DE tools on sparse, zero-inflated scRNA-seq.
**Mechanism:** These tools assume Gaussian or simpler null; single-cell data has zero-inflation that makes them over-confident.
**Symptom:** Thousands of significant DE genes per perturbation; FDR uncalibrated.
**Fix:** Use SCEPTRE (permutation-based NB GLM); Barry 2024 benchmark shows this is the only method with calibrated FDR.

### Genome-scale Perturb-seq with insufficient cells per perturbation

**Trigger:** <500 cells per perturbation in genome-scale experiment.
**Mechanism:** DE estimation requires sufficient cells per condition; <500 lacks power for moderate effects.
**Symptom:** Inconsistent hit calls across replicates; pathway analysis non-specific.
**Fix:** Scale up cell numbers; or run focused (sub-genome) Perturb-seq with more cells per pert.

## Quantitative Thresholds

| Threshold | Value | Source / Rationale |
|-----------|-------|--------------------|
| MOI for single sgRNA per cell | 0.3 | Poisson math; ~26% infected, 4% multi-infected |
| sgRNA assignment threshold | ≥10 reads of one sgRNA | Pertpy / direct-capture convention |
| Multiplet rate (post-doublet filter) | <5% | Typical 10X 3' chemistry |
| Mixscape KO retention | Guide-dependent; 39-92% observed | Papalexi 2021 |
| Cells per perturbation (DE power) | 500-1,000 minimum | Power convention (Replogle 2022 screened at a median >100) |
| SCEPTRE permutations | 1,000+ | Barry 2024 |
| Genes per cell (QC) | ≥500-1,000 | Standard scRNA QC |
| Mt% threshold | <15-20% | Standard scRNA QC |
| Doublet detection threshold | scDblFinder, Scrublet defaults | Methods agree |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| Low sgRNA detection | Architecture mismatch | Match library prep |
| Too many escapers in Mixscape | Weak phenotype | Skip Mixscape; verify Cas9 |
| Inflated DE hits | MAST / Wilcoxon used | Switch to SCEPTRE |
| Inconsistent gene effects between channels | Channel batch effect | Add channel as covariate in SCEPTRE |
| Multiplet rate >10% | Over-loading cells | Reduce loading; doublet filter |
| Per-pert DE with <100 cells | Insufficient power | Increase cell numbers; or accept low resolution |

## References

- Dixit A et al. 2016. *Cell* 167:1853. Original Perturb-seq.
- Datlinger P et al. 2017. *Nat Methods* 14:297. CROP-seq.
- Frangieh CJ et al. 2021. *Nat Genet* 53:332. Perturb-CITE-seq.
- Mimitou EP et al. 2019. *Nat Methods* 16:409. ECCITE-seq.
- Rubin AJ et al. 2019. *Cell* 176:361. Perturb-ATAC.
- Papalexi E et al. 2021. *Nat Genet* 53:322. Mixscape.
- Barry T, Mason K, Roeder K, Katsevich E. 2024. *Genome Biol* 25:124. SCEPTRE for low-MOI Perturb-seq.
- Replogle JM et al. 2022. *Cell* 185:2559. Genome-wide Perturb-seq.
- Heumos L et al. 2026. *Nat Methods* 23:350-359. DOI 10.1038/s41592-025-02909-7. Pertpy framework.
- Jiang L et al. 2025. *Nat Cell Biol* 27:505. Mixscale (perturbation-strength-aware Perturb-seq).

## Related Skills

- crispr-screens/library-design - Direct-capture vs CROP-seq library design
- crispr-screens/screen-qc - sgRNA assignment rates as QC
- crispr-screens/mageck-analysis - Pseudobulk analysis as alternative
- crispr-screens/hit-calling - Pseudo-bulk hit calling alternative
- single-cell/preprocessing - scRNA-seq preprocessing
- single-cell/clustering - Post-DE clustering
- single-cell/multimodal-integration - Multiome Perturb-seq
- single-cell/perturb-seq - General single-cell screen analysis
- pathway-analysis/go-enrichment - Pathway enrichment of perturbation hits
<!-- END FILE: crispr-screens/perturb-seq-analysis/SKILL.md -->

## 子目录：crispr-screens/prime-editing-screens

<!-- BEGIN FILE: crispr-screens/prime-editing-screens/SKILL.md -->
---
name: bio-crispr-screens-prime-editing-screens
description: Designs and analyzes pooled prime-editor (PE) screens for installing precise genetic variants without bystander confounding. Covers pegRNA design with PRIDICT and PRIDICT2 for predicting per-pegRNA editing efficiency, pegRNA architecture (spacer + scaffold + PBS + RTT), PE2/PE3/PE3b/PEmax variants, MOSAIC in situ saturation mutagenesis, the PRIME pooled-screen methodology (Ren 2023; ~3,699 ClinVar variant screens), chromatin context as a major locus-level determinant of PE efficiency, scaffold-incorporation and indel byproduct quantification with CRISPResso2, and the cross-modal validation strategy of PE + base-editor screens for variant function. Use when designing a pegRNA library for variant installation, choosing between BE and PE for a specific edit, predicting pegRNA efficiency before library synthesis, analyzing PE screen output, distinguishing intended-edit from scaffold-incorporation, or scaling PE screens to thousands of variants.
tool_type: mixed
primary_tool: PRIDICT2
---

## Version Compatibility

Reference examples tested with: PRIDICT2 v1.0+ (https://github.com/uzh-dqbm-cmi/PRIDICT2), CRISPResso2 2.2.14+, pandas 2.2+, biopython 1.83+, numpy 1.26+.

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `python pridict2_pegRNA_design.py single --help`; `python pridict2_pegRNA_design.py batch --help`
- Web: PRIDICT2 web interface at https://pridict.it/

If code throws ImportError, AttributeError, or TypeError, introspect the installed package and adapt the example to match the actual API rather than retrying.

## Prime-Editing Screen Analysis

**"Design or analyze a pooled prime-editor screen"** -> Design pegRNAs (spacer + scaffold + PBS + RTT) for intended edits, predict efficiency with PRIDICT2, filter pre-synthesis to efficient candidates, install variants in the screen, quantify intended-edit vs scaffold-incorporation vs indel via CRISPResso2, and aggregate to per-variant fitness scores.

- Python: `PRIDICT2` for pegRNA efficiency prediction
- Python: `ePRIDICT` for chromatin-context prediction; pair with PRIDICT2 rather than replacing it
- CLI: `CRISPResso --prime_editing_pegRNA_*` for amplicon-level analysis
- Workflow: pegRNA library design -> PRIDICT2 filtering -> screen execution -> CRISPResso2 quantification -> per-variant scoring

## Prime Editor Chemistry Comparison

| Editor | Year | Mechanism | Indel rate | Use when |
|--------|------|-----------|------------|----------|
| PE2 (Anzalone 2019) | 2019 | nCas9-RT fusion + pegRNA | 1-3% | Standard PE; lowest indel rate |
| PE3 | 2019 | PE2 + nick of opposite strand by additional sgRNA | 2-5% | Higher editing efficiency, slightly more indels |
| PE3b | 2019 | PE3 with edit-blocking ssgRNA | 1-3% | When PE3's added nick risks unwanted indels |
| PEmax (Chen 2021) | 2021 | Engineered RT + nCas9 | 1-2% | Higher editing rate per pegRNA |
| PE5max (Chen 2021) | 2021 | PE3 plus MMR inhibition (MLH1dn) on the PEmax architecture | 1% | Highest efficiency at favorable sites |
| PE6 / dual-pegRNA (2023) | 2023 | Engineered compact PE; twin-pegRNA systems | Variable | Specific applications |

**Decision rule:** For pooled screens at scale, PE2 or PEmax (single-guide architecture) is preferred over PE3, whose additional nicking sgRNA complicates library architecture. For specific high-efficiency edits, PEmax + PRIDICT2-optimized pegRNA.

## pegRNA Architecture

A pegRNA contains four critical elements that determine efficiency:

```
5'  SPACER (20 nt)  -- standard sgRNA spacer; defines target locus via NGG PAM
    +
    SCAFFOLD (~80 nt) -- canonical or recoded scaffold (Chen 2021 recodes it to cut scaffold-incorporation byproducts)
    +
    PBS (Primer Binding Site, 8-15 nt) -- complements protospacer downstream of cut site
    +
    RTT (Reverse Transcription Template, 10-30 nt) -- encodes intended edit; copied by RT
3'
```

**Key design parameters:**
- **PBS length:** 11-13 nt typical; longer for high-GC contexts; PBS GC fraction critical (35-65% target)
- **RTT length:** 10-20 nt typical; longer for distant edits (10+ bp away from cut)
- **RTT-edit position:** intended edit at position 4-30 from cut site
- **Scaffold:** standard sgRNA scaffold OR the Chen 2021 recoded scaffold, which removes homology with the genomic target and cuts scaffold-derived byproducts. The recoding does not itself raise editing efficiency; that comes from MLH1dn and the PEmax architecture.

## PRIDICT and PRIDICT2 pegRNA Efficiency Prediction

**Mathis N et al 2023 *Nat Biotechnol* 41:1151 (PRIDICT v1) / 2025 *Nat Biotechnol* 43(5):712 (PRIDICT2; published online June 2024)** developed deep-learning predictors of per-pegRNA editing efficiency. PRIDICT2 is the current state of the art.

```bash
# PRIDICT2 is invoked via CLI: pridict2_pegRNA_design.py
# Single sequence input:
python pridict2_pegRNA_design.py single \
    --sequence-name BRCA1_c5135 \
    --sequence "AGCAGCCT(C/T)CTGAATGCCC...60nt_context" \    # parens = intended edit
    --output-dir predictions/ \
    --use_5folds                                              # 5-fold ensemble averaging

# Batch input from CSV:
python pridict2_pegRNA_design.py batch \
    --input-fname variants_to_design.csv \                    # CSV: sequence_name, sequence
    --output-dir predictions/ \
    --cores 4 \
    --summarize                                               # generate summary table

# Output: per-pegRNA predictions in predictions/<sequence_name>/
# Columns: PBS_sequence, PBS_length, RTT_sequence, RTT_length, predicted_editing_efficiency,
#          predicted_indel_rate, deep_ensemble_score, etc.
```

**Loading PRIDICT2 results in Python:**

```python
import pandas as pd
from pathlib import Path

def load_pridict2_predictions(prediction_dir):
    '''Load PRIDICT2 batch outputs from prediction_dir/'''
    summary = pd.read_csv(Path(prediction_dir) / '<timestamp>_summary_K562_batch_summary.csv')
    # summary has columns: sequence_name, PBS, RTT, predicted_efficiency, predicted_indel, etc.
    return summary
```

**Key determinants of PE efficiency (Mathis 2025 PRIDICT2):**

| Feature | Effect on efficiency |
|---------|----------------------|
| PBS GC content | 40-55% optimal; high GC slows annealing |
| PBS length | 11-13 nt optimal; longer for high-GC PBS |
| RTT length | 10-20 nt typical; trade-off between coverage and processivity |
| Edit position in RTT | Closest to PBS = highest efficiency |
| Chromatin context | Dominant locus effect; H3K9me3 heterochromatin ~0.8% vs ~2.2% elsewhere |
| Cell line / Cas9 expression | Variable; piloting required |
| Cell cycle phase | S/G2 = higher efficiency |

**Critical insight from Mathis 2025:** Chromatin context is a major locus-level determinant that sequence-only predictors miss, which is why ePRIDICT is designed to be combined with PRIDICT2.0 rather than replace it -- the pairing helps most in regions of lower chromatin accessibility. For genome-scale screens, validate predictions empirically at representative loci.

## PRIME Pooled Screen Methodology

**Ren X et al 2023 *Mol Cell* 83:4633** established the PRIME pooled prime-editing screen methodology (earlier 2023 bioRxiv preprint):

- pegRNA library covering thousands of intended variants, screened for specificity at design time (Ren 2023 used GuideScan2; add PRIDICT2 efficiency prediction for new designs)
- Lentiviral delivery in a PE-expressing cell line (Ren 2023: MOI 0.3 for the MYC-enhancer screen, MOI 0.5 for the variant screens)
- Selection on integration marker
- Time-course screen for variant function (e.g., drug sensitivity)
- Endpoint amplicon sequencing of each pegRNA target locus
- CRISPResso2 quantification of intended-edit %
- MAGeCK / drugZ-style hit calling on edit-efficient pegRNAs

**Quantified scale:** ~3,699 ClinVar variants installed in a single PRIME screen, alongside 1,304 breast-cancer GWAS variants.

## MOSAIC In Situ Saturation Mutagenesis

**MOSAIC (Hsu 2024, bioRxiv)** is a high-throughput in-situ saturation-mutagenesis prime-editing method with multiplexed read-out:

- Tile pegRNAs across protein domains for systematic mutagenesis
- Saturation: every possible amino acid change in a region
- Identify drug-resistance variants in real-time
- Smaller per-variant cell numbers (more variants total)

**Use case:** Cancer-drug-resistance variant scanning; protein-domain function mapping.

## Run PRIDICT2 on a Custom pegRNA Library

**Goal:** Predict editing efficiency for thousands of pegRNAs before library synthesis.

**Approach:** Build a CSV with one row per intended edit (sequence + edit notation), run PRIDICT2 in batch mode, parse the per-pegRNA efficiency summary, and filter to candidates above the chosen efficiency threshold.

```bash
# Step 1: prepare batch input CSV (sequence_name, sequence with (REF/ALT) edit notation)
cat > variants.csv <<EOF
sequence_name,sequence
BRCA1_R71X,AGCAGCCT(C/T)CTGAATGCCC...
MLH1_c677,GAGCTGAGC(A/G)GAGGCTCTTGAAGC...
EOF

# Step 2: run PRIDICT2 batch
python pridict2_pegRNA_design.py batch \
    --input-fname variants.csv \
    --output-dir predictions/ \
    --cores 8 \
    --summarize
```

```python
# Step 3: parse and filter
import pandas as pd
predictions = pd.read_csv('predictions/<timestamp>_summary_K562_batch_summary.csv')

# Filter to pegRNAs with predicted efficiency > 50% (library-inclusion convention)
filtered = predictions[predictions['predicted_editing_efficiency'] > 50]
print(f'pegRNAs passing PRIDICT2 >50%: {len(filtered)} / {len(predictions)}')

# Pick top 3 per intended edit
top3 = (filtered.sort_values(['sequence_name', 'predicted_editing_efficiency'],
                              ascending=[True, False])
                 .groupby('sequence_name').head(3))
top3.to_csv('peg_library_filtered.csv', index=False)
```

## Cross-Validate PE with Base Editor Screens

**Goal:** Confirm variant-function calls from PE with orthogonal BE screens.

**Approach:** Design parallel BE library for the same variants; run both screens; intersect hits.

```python
# BE screen output (target conversion + bystander)
be_hits = pd.read_csv('be_screen_hits.tsv', sep='\t')
# PE screen output (intended edit + scaffold-incorp + indel)
pe_hits = pd.read_csv('pe_screen_hits.tsv', sep='\t')

# Intersect on intended variant
concordant = be_hits.merge(pe_hits, on='variant_id', suffixes=('_be', '_pe'))
# Filter to high-confidence: both methods call variant + same direction
concordant['high_confidence'] = (concordant['be_fdr'] < 0.05) & (concordant['pe_fdr'] < 0.05) & \
                                 (np.sign(concordant['be_lfc']) == np.sign(concordant['pe_lfc']))
```

**Critical:** PE-only hits in BE-coverable variants are suspect (BE should detect them). PE-only hits in non-BE-coverable variants (e.g., transversions) are genuinely PE-unique.

## CRISPResso2 for PE Quantification

```bash
CRISPResso \
    --fastq_r1 pe_sample.fq.gz \
    --amplicon_seq <amplicon_seq> \
    --guide_seq <20nt_spacer> \
    --prime_editing_pegRNA_spacer_seq <spacer> \
    --prime_editing_pegRNA_extension_seq <RTT+PBS> \
    --prime_editing_pegRNA_scaffold_seq <scaffold> \
    --quantification_window_size 25 \              # widen to cover edit
    --output_folder pe_results \
    --name sample_id

# Output: CRISPResso_quantification_of_editing_frequency.txt
# Prime-editing outcomes appear as extra amplicon ROWS (Reference / Prime-edited /
# Scaffold-incorporated), each with Unmodified%, Modified% and read counts.
```

## Failure Modes

### Low pegRNA efficiency despite high PRIDICT prediction

**Trigger:** Sequence-only prediction missed chromatin context.
**Mechanism:** Closed chromatin reduces Cas9 binding and RT activity; PRIDICT2 only sees sequence.
**Symptom:** PRIDICT2 predicts 60% efficiency; observed is 5%.
**Fix:** Cross-reference target with chromatin accessibility data (ATAC-seq) in the cell line; flag pegRNAs at silenced loci; pilot before screen.

### High scaffold incorporation

**Trigger:** RTT too short relative to PBS, or RT processivity issue.
**Mechanism:** RT reads past edit into scaffold; resulting product is detectable but undesired.
**Symptom:** Scaffold incorporation >5%; intended edit efficiency low.
**Fix:** Re-design pegRNA with longer RTT; verify with PRIDICT2 score for scaffold_incorp; pilot at representative loci.

### PE2 cell line lacks RT expression

**Trigger:** PE2 construct expressed at low level; insufficient RT for productive editing.
**Mechanism:** PE2 requires high RT expression; some cell lines down-regulate.
**Symptom:** Library-wide editing <10%; not locus-specific.
**Fix:** Verify PE2 expression by Western blot; consider PEmax (higher activity); use better-validated cell lines (K562, HEK293T, U2OS).

### Multi-base intended edit but only one base installed

**Trigger:** Long RTT designed for multi-base edit; RT prematurely terminates.
**Mechanism:** RT processivity drops with longer RTT; multi-base edits often incomplete.
**Symptom:** Allele table shows partial-edit alleles (some bases installed, not all).
**Fix:** Re-design with shorter RTT covering only the closest edits; or use PE3 to nick opposite strand and force longer RT processivity.

### Library missing intended variant

**Trigger:** No suitable PAM/PBS/RTT combination for the intended edit.
**Mechanism:** PE requires NGG PAM within 30 nt of edit; rare edits cannot be installed.
**Symptom:** Specific variants absent from library.
**Fix:** Use SpRY-PE for relaxed PAM; accept that some variants cannot be PE-installed; consider BE if applicable.

## Cas9 vs BE vs PE for Variant Installation

| Approach | Bystander | Indels | Coverage | When to use |
|----------|-----------|--------|----------|-------------|
| Cas9 + HDR | None | High | Variable (depends on template integration) | Precise edits at scale; high indel byproduct |
| Base editor | YES | Low (<5%) | Limited by editing window | C->T or A->G at editable position |
| Prime editor | NONE | Low (<3%) | NGG-PAM within 30 nt of edit | Precise variants; multi-base; transversions |
| Cas9 (no template) | NONE | 70%+ | Anywhere with NGG | LoF only; not variant-specific |

**Decision tree:**
- C->T or A->G at editing-window position: BE (higher efficiency than PE)
- Multi-base / transversion / out-of-window: PE
- LoF without specifying variant: Cas9
- Random insertions: HDR (lower throughput than PE)

## Quantitative Thresholds

| Threshold | Value | Source / Rationale |
|-----------|-------|--------------------|
| PRIDICT2 efficiency for library inclusion | >50% | Project-chosen cutoff; PRIDICT2 prescribes none |
| Intended edit % for screen power | >5%; >20% at favorable sites | Field convention |
| Scaffold incorporation | <2% (clean PE); <5% acceptable | Empirical |
| Indel byproduct | <3% (PE2); <5% (PE3) | Anzalone 2019; Chen 2021 |
| PBS GC content | 40-55% | PRIDICT2 |
| PBS length | 11-13 nt | PRIDICT2 |
| RTT length | 10-20 nt | PRIDICT2 |
| Edit position from cut | 1-30 nt | Anzalone 2019 |
| Cell line for PE | K562, HEK293T, U2OS validated | High RT expression |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| Low editing across library | Cell-line RT inactivity | Verify PE2 expression; switch to validated line |
| Scaffold incorporation >10% | RTT too short | Re-design with longer RTT |
| Partial multi-base edits | RT processivity limit | Shorter RTT or PE3 |
| PRIDICT predicts but observes much lower | Chromatin context | Pilot at chromatin-aware sites |
| Library missing variants | No NGG PAM | SpRY-PE; BE alternative |
| PE concordant with BE on transitions, disagrees on transversions | PE handles transversions BE doesn't | Expected; trust PE |

## References

- Anzalone AV et al. 2019. *Nature* 576:149. Original PE2/PE3 (foundational prime editing paper).
- Mathis N et al. 2023. *Nat Biotechnol* 41:1151. PRIDICT v1 deep-learning pegRNA prediction.
- Mathis N et al. 2025. *Nat Biotechnol* 43(5):712 (published online June 2024). PRIDICT2 + chromatin context (current state-of-the-art).
- Chen PJ et al. 2021. *Cell* 184:5635. PEmax + engineered RT.
- Hsu JY, Lam KC, Shih J, Pinello L, Joung JK 2024 bioRxiv (doi:10.1101/2024.04.25.591078). MOSAIC in situ saturation mutagenesis via prime editing.
- Ren X et al. 2023. *Mol Cell* 83:4633. PRIME pooled prime-editing screen (~3,699 ClinVar variants); variant-installation scale.

## Related Skills

- crispr-screens/library-design - pegRNA library design
- crispr-screens/base-editing-analysis - Orthogonal BE for variant attribution
- crispr-screens/crispresso-editing - CRISPResso2 PE mode and quantification
- crispr-screens/hit-calling - Per-variant hit calling
- crispr-screens/screen-qc - Editing-efficiency QC
- variant-calling/variant-annotation - Annotate edited variants
- clinical-databases/clinvar-lookup - Variant pathogenicity
<!-- END FILE: crispr-screens/prime-editing-screens/SKILL.md -->

## 子目录：crispr-screens/screen-qc

<!-- BEGIN FILE: crispr-screens/screen-qc/SKILL.md -->
---
name: bio-crispr-screens-screen-qc
description: Quality control for pooled CRISPR screens covering library representation, Gini index, log-skew, replicate Pearson and Spearman concordance, essentialome precision-recall AUC against CEGv2 (Hart 2017), Cas9 cut-toxicity diagnostics, copy-number amplicon detection (Aguirre 2016 / Munoz 2016), bottleneck propagation through plasmid pool, infection, selection, and endpoint stages, MOI verification, and DepMap-style screen-quality scoring. Use when assessing screen quality before hit calling, deciding whether to repeat or rescue a screen, diagnosing low-confidence hits, choosing between MAGeCK / BAGEL2 / Chronos based on quality grade, picking a normalization strategy from QC signatures, or evaluating whether an in-vivo screen retained adequate library complexity.
tool_type: python
primary_tool: MAGeCK-VISPR
---

## Version Compatibility

Reference examples tested with: MAGeCK 0.5+ (count + VISPR), MAGeCKFlute 2.0+ (R), pandas 2.2+, numpy 1.26+, scikit-learn 1.4+, matplotlib 3.8+, seaborn 0.13+.

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `mageck --version` then `mageck count --help`; R: `packageVersion('MAGeCKFlute')`
- R: `packageVersion('MAGeCKFlute')` then `?BatchRemove` / `?FluteRRA`

If code throws ImportError, AttributeError, or TypeError, introspect the installed package and adapt the example to match the actual API rather than retrying.

## CRISPR Screen Quality Control

**"Audit my CRISPR screen quality before hit calling"** -> Assess library representation, replicate concordance, depth, drift, and biological signal recovery using DepMap-grade metrics, then decide whether the screen is usable, salvageable, or must be repeated.

- Python: `pandas` + `scikit-learn` for Gini, AUC, PCA; `MAGeCKFlute` (R) for one-shot QC dashboard
- CLI: `mageck count` writes Gini and mapping stats unconditionally to `<prefix>.countsummary.txt` (`GiniIndex`, `Reads`, `Mapped`, `Percentage`); MAGeCK-VISPR for an interactive dashboard

## QC Stage Hierarchy

A pooled screen has six distinct bottlenecks where complexity can collapse. Audit each:

| Stage | Metric | Acceptable threshold | Failure consequence |
|-------|--------|----------------------|----------------------|
| Plasmid pool | Gini, skew, % zero-count guides | Gini <0.1, skew <2 (Joung 2017 states <10), zero <0.5% | Missing guides cannot be screened; dropout indistinguishable from non-coverage |
| Day-0 infection | Library coverage, MOI verification | ≥99% guide detection at 500x cells/sgRNA; MOI 0.3 | Founder effects; polyclonality with high MOI |
| Selection (puro/blast) | % cells surviving, time-course Gini | 30-40% survival at 5-7 days; Gini drift <0.05 | Selection artifact; fast-growers enriched |
| Endpoint | Replicate correlation, depth | Pearson >=0.8 on log-counts (MAGeCK-VISPR floor), Spearman >0.7-0.8, >500 reads/sgRNA (Joung 2017 screening) | Noise dominates; FDR inflates |
| Biological signal | CEGv2 PR-AUC, NEGv1 false-positive rate | PR-AUC >0.7 at FDR 5% (community "passing" convention); CEGv2 enrichment in top 1k | Screen lacks essentiality signal; hits not credible |
| Copy-number artifact | Amplified-region enrichment, sgRNA-cut-count correlation | No correlation between sgRNA off-target count and depletion | False-positive essentiality at amplicons; ERBB2 in HER2+ etc. |

Each metric below quantifies one of these stages.

## Library Representation Metrics

**Goal:** Detect dropout, oversaturation, and library bottlenecks at each sequencing stage.

**Approach:** Compute per-sample zero-count fraction, low-count fraction (<30 reads, the CRISPRcleanR `ccr.NormfoldChanges` default), and percentile-based skew, then track how these change between plasmid -> Day-0 -> endpoint to localize the bottleneck.

```python
import pandas as pd
import numpy as np

def library_representation(counts_df):
    '''Per-sample library coverage diagnostics.
    counts_df: rows = sgRNAs, columns = samples (numeric counts).'''
    out = pd.DataFrame(index=counts_df.columns)
    out['n_sgrnas_detected'] = (counts_df > 0).sum()
    out['pct_zero'] = (counts_df == 0).sum() / len(counts_df) * 100
    out['pct_lowcount'] = (counts_df < 30).sum() / len(counts_df) * 100
    out['median_count'] = counts_df.median()
    out['p10_count'] = counts_df.quantile(0.10)
    out['p90_count'] = counts_df.quantile(0.90)
    out['skew_ratio'] = out['p90_count'] / out['p10_count'].replace(0, np.nan)
    return out

def stage_specific_thresholds():
    '''Stage conventions: Joung 2017 (zero-count, skew) + MAGeCK-VISPR (Gini).'''
    return {
        'plasmid':  {'pct_zero_max': 0.5, 'skew_max': 2.0, 'gini_max': 0.10},   # skew 2.0 is a stricter modern convention; Joung 2017 states <10
        'day_0':    {'pct_zero_max': 1.0, 'skew_max': 2.5, 'gini_max': 0.12},
        'endpoint': {'pct_zero_max': 5.0, 'skew_max': 10.0, 'gini_max': 0.30},
    }
```

**Interpretation:** Plasmid pool failing Gini <0.1 indicates synthesis or amplification bias; the screen is unfit for use. Endpoint Gini drifting above 0.30 indicates either heavy biological selection (acceptable for strong-phenotype drug screens) or a bottleneck (must be diagnosed). The Day-0 vs plasmid delta isolates whether the issue arose during infection (cloning is unlikely to lose specific guides between extraction and infection -- the change happens in cells).

## Gini Coefficient

**Goal:** Quantify how unevenly reads are distributed across sgRNAs in a single sample.

**Approach:** Sort non-zero counts ascending, compute Gini via the cumulative-fraction formula. Compare against stage-specific thresholds.

```python
def gini(x):
    '''Gini coefficient: 0 = perfect equality, 1 = maximal inequality.
    Uses non-zero counts only; zero-count sgRNAs handled separately by % zero.'''
    x = np.sort(x[x > 0].astype(float))
    if x.size == 0:
        return np.nan
    n = x.size
    cumx = np.cumsum(x)
    return (n + 1 - 2 * np.sum(cumx) / cumx[-1]) / n
```

**Stage-specific thresholds:** only the plasmid Gini <=0.1 is a published cutoff (MAGeCK-VISPR); the remaining grades are operational convention.

| Stage | Excellent | Acceptable | Concerning | Failure |
|-------|-----------|------------|------------|---------|
| Plasmid pool | <0.10 | <0.15 | 0.15-0.20 | >0.20 |
| Day 0 (post-infection) | <0.12 | <0.18 | 0.18-0.25 | >0.25 |
| Endpoint (post-selection) | <0.30 | <0.40 | 0.40-0.55 | >0.55 |

A Gini that climbs from 0.10 (plasmid) to 0.45 (endpoint) is expected when the screen exerts strong selection (drug, lethal-condition). A Gini that climbs to 0.45 without any biological selection (e.g., a control-vs-control timepoint comparison) indicates technical drift.

## Replicate Concordance

**Goal:** Verify that biological/technical replicates agree before testing for between-condition differences.

**Approach:** Compute pairwise Pearson on log10(counts+1) (MAGeCK-VISPR convention) and Spearman ρ on raw rank, between every replicate pair within a condition. Flag any pair below the MAGeCK-VISPR floor of 0.8 Pearson on log-scale.

```python
def replicate_concordance(counts_df, condition_map):
    '''condition_map: {condition_name: [sample_col1, sample_col2, ...]}.'''
    log_counts = np.log10(counts_df + 1)
    rows = []
    for cond, samples in condition_map.items():
        if len(samples) < 2:
            continue
        for i in range(len(samples)):
            for j in range(i+1, len(samples)):
                r_pearson = log_counts[[samples[i], samples[j]]].corr().iloc[0, 1]
                r_spearman = counts_df[[samples[i], samples[j]]].corr(method='spearman').iloc[0, 1]
                rows.append({'condition': cond, 'rep1': samples[i], 'rep2': samples[j],
                             'pearson_log': r_pearson, 'spearman': r_spearman})
    return pd.DataFrame(rows)
```

**Thresholds:** 0.8 Pearson is the MAGeCK-VISPR floor; the stricter grades are operational convention.

| Metric | Excellent | Acceptable | Failure |
|--------|-----------|------------|---------|
| Pearson on log10(counts+1) | >0.95 | >0.85 | <0.80 |
| Spearman on raw ranks | >0.85 | >0.70 | <0.60 |

**When Pearson is high but Spearman is low**, a few outlier sgRNAs are driving correlation (one extreme guide dominates). Inspect the scatterplot; typically caused by PCR jackpotting at a single guide. Hit calling should use a method that ranks (RRA, drugZ) rather than one that fits per-sgRNA fold change directly.

## Essentialome Recovery (CEGv2 PR-AUC)

**Goal:** Verify the screen has detectable biological essentiality signal by checking whether known essentials (Hart 2017 CEGv2) drop out faster than known non-essentials (NEGv1).

**Approach:** Compute precision-recall AUC where positives are CEGv2 genes and negatives are NEGv1; the screen "passes" if PR-AUC >0.7 (community convention; the CEGv2/NEGv1 sets come from Hart 2017 / Hart 2014).

```python
from sklearn.metrics import precision_recall_curve, auc, roc_auc_score

def essentialome_recovery(gene_lfc_df, cegv2_set, negv1_set):
    '''gene_lfc_df: must have ["gene", "lfc"] columns (gene-level mean LFC, negative = depleted).
    cegv2_set, negv1_set: sets of gene symbols from Hart 2017.'''
    labeled = gene_lfc_df[gene_lfc_df['gene'].isin(cegv2_set | negv1_set)].copy()
    labeled['is_essential'] = labeled['gene'].isin(cegv2_set).astype(int)
    y_score = -labeled['lfc']  # negative LFC = depleted = more essential -> higher score
    precision, recall, _ = precision_recall_curve(labeled['is_essential'], y_score)
    return {
        'pr_auc': auc(recall, precision),
        'roc_auc': roc_auc_score(labeled['is_essential'], y_score),
        'n_essential_detected': labeled['is_essential'].sum(),
        'n_nonessential_detected': (1 - labeled['is_essential']).sum(),
    }
```

**Source / threshold:** Hart 2017 *G3* 7:2719 defines CEGv2 (~684 core essentials); NEGv1 (~927 non-essentials) comes from Hart 2014 *Mol Syst Biol* 10:733. Both lists at https://github.com/hart-lab/bagel/blob/master/CEGv2.txt and NEGv1.txt. DepMap convention: PR-AUC >0.7 at FDR 5% is the "passing" threshold; <0.5 means the screen has no essentiality signal and is not interpretable.

**When PR-AUC is low despite good Gini and Pearson**: cause is usually one of (a) Cas9 was not selected for before screen start (lots of Cas9-negative cells in the pool diluting signal), (b) puromycin selection truncated too aggressively (over-bottleneck), (c) the timepoint is too early (need 14-21 days for KO + decay + selection to manifest). Each has a different remediation.

## Copy-Number Amplicon Bias Diagnostic

**Goal:** Detect the Aguirre 2016 / Munoz 2016 copy-number artifact where sgRNAs targeting amplified loci appear "essential" purely from DNA-damage burden.

**Approach:** Bin genes by copy number (if known from matched WGS/SNP-array) and check whether mean LFC correlates with CN. Alternatively, count off-target cut sites per sgRNA and check correlation with depletion -- amplified loci share many identical cut sites.

```python
def cn_bias_diagnostic(gene_lfc_df, cn_df):
    '''cn_df: per-gene copy number (from WGS/SNP-array/matched ASCAT).
    Tests whether amplified genes show systematically lower LFC.'''
    merged = gene_lfc_df.merge(cn_df, on='gene')
    bins = pd.qcut(merged['copy_number'], q=5, duplicates='drop')
    bin_lfc = merged.groupby(bins, observed=True)['lfc'].agg(['mean', 'median', 'std', 'count'])
    from scipy.stats import spearmanr
    rho, p = spearmanr(merged['copy_number'], merged['lfc'])
    return {'cn_vs_lfc_rho': rho, 'cn_vs_lfc_p': p,
            'amplified_mean_lfc': merged[merged['copy_number'] > 4]['lfc'].mean(),
            'diploid_mean_lfc': merged[(merged['copy_number'] >= 1.5) & (merged['copy_number'] <= 2.5)]['lfc'].mean(),
            'per_bin': bin_lfc}
```

**Interpretation:** A Spearman ρ < -0.1 between copy number and LFC indicates copy-number artifact. The diagnostic threshold is conservative -- Aguirre 2016 showed the effect scales with copy number and with the number of cut sites per sgRNA. Remediation: use CRISPRcleanR, CERES, or Chronos (see [[copy-number-correction]]) before hit calling.

## Sequencing Depth Audit

**Goal:** Verify that sequencing depth is sufficient to resolve fold changes at the smallest interesting effect size.

**Approach:** Compute reads/sgRNA per sample and the coefficient of variation (CV) of total reads across samples. Compare against Joung 2017's >100 reads/sgRNA for plasmid QC and >500 for screening, or MAGeCK-VISPR's 300x.

```python
def depth_audit(counts_df):
    '''Verify depth: Joung 2017 recommends >100 reads/sgRNA for plasmid QC and
    >500 for screening; MAGeCK-VISPR uses 300x.'''
    total = counts_df.sum()
    n_sgrnas = len(counts_df)
    depth = total / n_sgrnas
    cv = total.std() / total.mean()
    return pd.DataFrame({'total_reads': total, 'reads_per_sgrna': depth,
                          'depth_grade': np.where(depth < 100, 'FAIL',
                                          np.where(depth < 300, 'CAUTION',
                                          np.where(depth < 500, 'OK', 'EXCELLENT')))}).assign(across_sample_cv=cv)
    # 100 = Joung 2017 plasmid-QC floor; 300 = MAGeCK-VISPR; 500 = Joung 2017 screening
```

**CV interpretation:** CV >0.5 across samples in total reads indicates demultiplexing imbalance or library-pooling error; even if individual samples pass depth thresholds, the relative count is then biased.

## MOI Verification

**Goal:** Confirm that infection occurred at MOI 0.3-0.5 so that ≤1 sgRNA/cell predominates.

**Approach:** From titration plate (control wells with serial-diluted virus), compute infection efficiency, then verify by qPCR of integrated proviral copy number in the screen pool.

| MOI | P(≥1 sgRNA/cell) | P(≥2 sgRNAs/cell) | Cells with 2+ guides as fraction of infected |
|-----|------------------|--------------------|-----------------------------------------------|
| 0.3 | 26% | 4% | 14% |
| 0.5 | 39% | 9% | 23% |
| 1.0 | 63% | 26% | 41% |

**Decision rule:** Always titrate to 0.3. At 0.5, 14-23% of "perturbed" cells carry combinatorial perturbations that confound single-gene scoring. The Poisson math is non-negotiable -- there is no analytical correction for high-MOI confounding.

## PCA and Batch Effect Detection

**Goal:** Visualize whether samples cluster by biology or by batch.

**Approach:** PCA on log10(counts+1); samples should cluster by condition, not by batch/replicate-day/library-lot.

```python
from sklearn.decomposition import PCA

def screen_pca(counts_df, metadata_df, condition_col='condition'):
    '''metadata_df: rows = samples, columns include condition_col, batch (optional).'''
    log_counts = np.log10(counts_df + 1).T  # samples as rows for PCA
    pca = PCA(n_components=3)
    pcs = pca.fit_transform(log_counts)
    out = pd.DataFrame(pcs, columns=['PC1', 'PC2', 'PC3'], index=counts_df.columns)
    out = out.join(metadata_df)
    return out, pca.explained_variance_ratio_
```

**Interpretation:** If PC1 separates batches, see [[batch-correction]]. If PC1 separates conditions cleanly, the screen has interpretable biology. If neither separates anything, the screen has no signal (failed) or is dominated by technical noise.

## Composite DepMap-Style Quality Score

**Goal:** Generate a single quality grade combining all metrics for pipeline gating.

**Approach:** Rescale each metric to a comparable 0-1 direction and average them into a single gate score. Screens scoring <-1 SD are typically excluded from DepMap.

```python
def composite_qc_score(per_sample_qc):
    '''per_sample_qc: one row per sample, joining library_representation() output
    (n_sgrnas_detected, reads_per_sgrna) with gini, pearson_min_replicate, pr_auc
    and n_sgrnas_total.'''
    metrics = {
        'gini_inv': 1 - per_sample_qc['gini'],
        'pearson': per_sample_qc['pearson_min_replicate'],
        'pr_auc': per_sample_qc['pr_auc'],
        'depth_log': np.log10(per_sample_qc['reads_per_sgrna']),
        'detected_frac': per_sample_qc['n_sgrnas_detected'] / per_sample_qc['n_sgrnas_total'],
    }
    return pd.DataFrame(metrics).mean(axis=1)
```

This is a pipeline gate, not a publication metric. DepMap reports `gene effect score quality` (Chronos-derived) separately from screen quality; Pacini 2021 scores the latter with NNMD.

## Failure Modes

### High Gini in plasmid pool despite passing all design rules

**Trigger:** Library was cloned and amplified through too many PCR cycles (>20) or used a high-GC-bias polymerase.
**Mechanism:** Each PCR cycle compounds GC bias by ~5%; high-GC and low-GC guides become non-linear functions of starting abundance.
**Symptom:** Gini >0.15 in plasmid, GC-content stratification of dropout.
**Fix:** Cap PCR at 15 cycles for amplification; use Q5 / NEBNext Ultra II / KAPA HiFi (low-bias); re-sequence post-amp; if still bad, re-clone from glycerol stock.

### Falling PR-AUC across timepoints despite stable Gini

**Trigger:** Cas9 was not selected for before screen start; Cas9-negative cells in the pool dilute essentiality signal.
**Mechanism:** Each Cas9-negative cell carries a sgRNA but no editing; its sgRNA persists despite biological essentiality of the target.
**Symptom:** PR-AUC declines from 0.7 at week 1 to 0.4 at week 3; Gini and Pearson both pass.
**Fix:** Always select Cas9-positive cells (FACS or blast) before infection. For a salvage of an already-run screen, model Cas9-expression heterogeneity as a noise floor and accept reduced sensitivity.

### Apparent essentiality of amplified loci

**Trigger:** Cancer cell line with focal amplification (ERBB2 in SK-BR-3, MYC in colorectal, FGFR1 in head and neck).
**Mechanism:** Aguirre 2016 / Munoz 2016: many simultaneous Cas9 cuts trigger a DNA-damage response and G2 arrest; sgRNAs at amplified loci appear depleted independently of target essentiality.
**Symptom:** Hits include genes within known amplicons; sgRNAs with more genome-wide cut sites are more depleted.
**Fix:** Apply CRISPRcleanR pre-hoc or use Chronos/CERES with matched CN profile (see [[copy-number-correction]]). Always required for cancer-cell-line screens, not optional.

### Outlier replicate dragging Pearson down

**Trigger:** One technical replicate had a library-prep failure (low input, PCR jackpot, sequencing-lane swap).
**Mechanism:** Outlier sample has different total reads or different per-sgRNA distribution but passes individual sample QC.
**Symptom:** Pearson between replicates 0.85-0.90 with one pair as outlier; condition-level means look fine.
**Fix:** Drop the outlier replicate; re-derive Pearson on the remaining pair. If only two replicates and one is outlier, the condition lacks replication and must be re-run.

### Low Day-0 coverage from high MOI

**Trigger:** Infection at MOI >0.5.
**Mechanism:** Poisson: at MOI 0.5, 23% of infected cells carry multiple sgRNAs; the "single-perturbation" assumption underlying every analysis method is violated.
**Symptom:** Apparent gene-gene interactions in single-gene screens; gene-level z-scores noisy; Pearson lower than expected for high-quality counts.
**Fix:** No analytical correction. Re-titrate, re-infect at MOI 0.3, re-run screen.

### CRISPRi/a screen with no signal on validated essentials

**Trigger:** Library targets wrong TSS (Ensembl canonical vs FANTOM5 highest-rank).
**Mechanism:** dCas9-KRAB knockdown is maximal within ±100 bp of the actual Pol II loading site; canonical annotation can be off 1-10 kb.
**Symptom:** RPS/RPL/EIF families dropping out as expected (these have clean canonical TSSs) but downstream genes failing; PR-AUC on broader CEGv2 panel drops.
**Fix:** Re-design library against FANTOM5 highest-CAGE-peak TSS (Sanson 2018); for tissue-specific lines, use matched CAGE / GRO-seq.

## Quantitative Thresholds

| Threshold | Value | Source / Rationale |
|-----------|-------|--------------------|
| Plasmid Gini | <0.10 | Li W et al 2015 MAGeCK-VISPR *Genome Biol* 16:281 |
| Plasmid skew ratio (p90/p10) | <10 (Joung 2017); <2 is a stricter modern convention | Joung 2017 *Nat Protoc* 12:828 |
| % zero-count sgRNAs (plasmid) | <0.5% | Joung 2017 *Nat Protoc* 12:828 |
| % zero-count sgRNAs (endpoint) | <1% ideal, <5% tolerated | Li W et al 2015 *Genome Biol* 16:281 |
| Replicate Pearson on log10(counts+1) | >=0.8 (MAGeCK-VISPR floor); >0.95 ideal | Li W et al 2015 MAGeCK-VISPR *Genome Biol* 16:281 |
| Replicate Spearman | >0.70 | Operational convention |
| CEGv2 PR-AUC at FDR 5% | >0.70 passing; >0.85 high quality | Community convention (CEGv2 from Hart 2017 *G3* 7:2719) |
| Reads per sgRNA per sample | >100 plasmid QC and >500 screening (Joung 2017); 300+ (MAGeCK-VISPR) | Joung 2017; Li W et al 2015 |
| Library coverage at infection | 500x cells/sgRNA | Joung 2017; DepMap |
| In-vivo coverage | 50-200x at endpoint | Bottleneck-limited; see [[in-vivo-screens]] |
| MOI at infection | 0.3 strict | Poisson: P(≥2)=4% at 0.3 vs 9% at 0.5 |
| CN-bias Spearman ρ (LFC vs copy number) | abs(ρ) <0.10 | Operational convention |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| Plasmid Gini >0.2 | PCR over-amplification | Re-sequence; cap PCR at 15 cycles |
| Endpoint PR-AUC <0.5 | Cas9 not selected pre-screen | Select Cas9+; redo if mid-screen |
| Pearson high, Spearman low | A few outlier sgRNAs dominate | Use RRA / rank-based hit calling |
| Replicate Pearson <0.8 | Library-prep failure on one rep | Drop outlier; re-run if singleton |
| % zero increases dramatically Day-0 -> endpoint | Selection bottleneck | Reduce selection pressure; or increase coverage |
| Top hits include amplified-region genes | CN bias | CRISPRcleanR or Chronos |
| MOI verification shows 0.6+ | Over-infected | Re-run at lower MOI; no rescue |
| Detected fraction <90% in Day 0 | Coverage too low | Increase cells; expect drift |

## References

- Joung J et al. 2017. *Nat Protoc* 12:828. Genome-wide screen protocol; coverage and depth conventions.
- Li W et al. 2014. *Genome Biol* 15:554. MAGeCK.
- Li W et al. 2015. *Genome Biol* 16:281. MAGeCK-VISPR; Gini, zero-count, depth and replicate-correlation QC cutoffs.
- Wang B et al. 2019. *Nat Protoc* 14:756. MAGeCKFlute; QC dashboard.
- Hart T et al. 2017. *G3* 7:2719. CEGv2 core-essential reference set; PR-AUC screen-quality benchmarking.
- Hart T et al. 2014. *Mol Syst Biol* 10:733. Gold-standard essential and non-essential reference sets; source of NEGv1.
- Aguirre AJ et al. 2016. *Cancer Discov* 6:914. Copy-number amplicon false-essentiality.
- Munoz DM et al. 2016. *Cancer Discov* 6:900. Copy-number gene-independent toxicity.
- Pacini C et al. 2021. *Nat Commun* 12:1661. Integrated cross-study dependencies; NNMD screen-quality metric and cross-study batch correction.
- Meyers RM et al. 2017. *Nat Genet* 49:1779. CERES; mechanism of CN bias.
- Sanson KR et al. 2018. *Nat Commun* 9:5416. Dolcetto/Calabrese TSS rules.
- Dempster JM et al. 2021. *Genome Biol* 22:343. Chronos screen-quality model.

## Related Skills

- crispr-screens/library-design - Compose libraries that pass plasmid QC
- crispr-screens/mageck-analysis - Run MAGeCK count to generate QC inputs
- crispr-screens/copy-number-correction - Remediate Aguirre / Munoz CN artifact
- crispr-screens/batch-correction - Address inter-batch / cell-line confounding
- crispr-screens/hit-calling - Pick method by QC grade
- crispr-screens/in-vivo-screens - In-vivo-specific bottleneck QC
<!-- END FILE: crispr-screens/screen-qc/SKILL.md -->

<!-- END CATEGORY: crispr-screens -->

