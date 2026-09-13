---
slug: bio-genome-engineering-integrated
version: 1.0.1
displayName: "基因组工程 / Genome engineering"
name: bio-genome-engineering-integrated
summary: "中文：基因组工程综合技能，整合 5 个相关专题，覆盖基因组工程：sgRNA设计、Off-target预测、碱基编辑（CBE/ABE）、Prime editing、HDR供体设计。 English: Integrated Genome engineering skill covering 5 related topics, including Genome engineering: sgRNA design, off-target prediction, base editing (CBE/ABE), prime editing, HDR donor design."
description: "中文：这是一个面向基因组工程的综合生物信息学 Skill，整合当前分类下 5 个相关专题能力。它用于根据研究问题、数据类型和分析阶段，选择合适的方法与工具，规划从输入检查、预处理、核心分析到质量控制、统计解释和结果报告的完整流程。重点覆盖：基因组工程：sgRNA设计、Off-target预测、碱基编辑（CBE/ABE）、Prime editing、HDR供体设计。当用户提供相关实验数据、测序结果、表格或研究问题时，它会帮助判断分析目标与前置条件，给出工具选择、关键参数、输入输出、常见失败原因、结果解读和可复现建议。主要工具包括：BioPython, CRISPOR, Cas-OFFinder。该 Skill 提供分析设计与实施指导，不替代对具体数据质量、生物学背景和最终结论的人工审查。 English: This is an integrated bioinformatics Skill for Genome engineering, combining 5 related topic areas. It helps users choose appropriate methods and tools based on the research question, data type, and analysis stage, and plan an end-to-end workflow from input validation and preprocessing through core analysis, quality control, statistical interpretation, and reporting. It covers Genome engineering: sgRNA design, off-target prediction, base editing (CBE/ABE), prime editing, HDR donor design. For relevant experimental data, sequencing results, tables, or research questions, it clarifies prerequisites, recommends tools and parameters, describes expected inputs and outputs, explains common failure modes, and supports reproducible analysis. Primary tools include: BioPython, CRISPOR, Cas-OFFinder. It provides methodological and implementation guidance; final data-quality assessment and biological conclusions still require human review."
---

# genome-engineering 分类 Skill 整合版

> 本文件整合同一主分类目录下 5 个子目录中的 SKILL.md 内容。
> 各子目录正文按原文保留，并通过标题和边界标记进行区分；源文件中的元数据块未被改写。

---

<!-- BEGIN CATEGORY: genome-engineering -->

## 子目录：genome-engineering/base-editing-design

<!-- BEGIN FILE: genome-engineering/base-editing-design/SKILL.md -->
---
name: bio-genome-engineering-base-editing-design
description: Designs cytosine (CBE, C-to-T) and adenine (ABE, A-to-G) base-editor guides by positioning the target base at the activity-peak of the editing window (protospacer positions ~5-7, PAM-distal numbering), minimizing bystander edits for product purity, reading dinucleotide context (APOBEC1 TC favored / GC disfavored), and selecting the editor variant (BE4max, ABEmax, ABE8e, YE1/SECURE, TadCBE, CGBE, SpG/SpRY-BE). Covers knockout by premature stop (CRISPR-STOP/iSTOP) and splice-site disruption, the three off-target classes (Cas-dependent, Cas-independent DNA, RNA), outcome prediction (BE-Hive/DeepBE), and the base-vs-prime-vs-HDR decision. Use when installing a transition mutation without a double-strand break, knocking out a gene without indels, or choosing CBE vs ABE. Generic guide scoring, prime editing, and HDR donors are separate skills.
tool_type: python
primary_tool: BioPython
---

## Version Compatibility

Reference examples tested with: BioPython 1.83+.

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed package and adapt the example to match the actual API rather than retrying.

BE-Hive is NOT a pip package -- it is a web tool (crisprbehive.design) plus clone-only repos (`maxwshen/be_predict_efficiency`, `be_predict_bystander`) pinning old dependencies (scikit-learn 0.20.3, BioPython 1.73). Use the web tool for a quick answer, the clone for batch use. Editing windows and outcome predictions are **editor-variant- and cell-type- specific** and are activity gradients, not hard boxes -- record which editor model was used.

# Base Editing Design

**"Install a transition mutation without a double-strand break"** -> Write the edit as a base-pair change to pick the editor family, find a PAM that lands the target base at the window peak while keeping bystanders out, read sequence context, choose the editor variant, and report the predicted genotype spectrum -- not a lone efficiency number.
- Python: window/bystander scan with `Bio.Seq` + `re`; per-base context reading
- Web/clone: BE-Hive / DeepBE for the per-base efficiency + bystander genotype spectrum
- Web: BE-Designer (guide enumeration), BE-Analyzer / CRISPResso2 (validate from NGS)

## The Single Most Important Modern Insight -- the job is product PURITY, not editing efficiency

A base editor produces a *distribution of genotypes at one site*, not a binary cut. "80% editing" can mean 80% of alleles carry the clean intended edit, or 80% carry *some* edit -- a soup where a bystander C/A two positions away is also converted half the time, so the exact desired genotype is only 30% of alleles. Both report as "80% efficient." The number that answers the biology is **precise editing: the fraction of alleles with the target edit AND no bystander edit.** Design is dominated by three coupled levers on one ~5-nt window: **(1) where the target base sits** (set by PAM/guide; drives efficiency), **(2) what else sits in the window** (bystander C's/A's; drives purity), **(3) the local dinucleotide context** of each base (drives which actually edit). The corollary trap: a *more active* editor (ABE8e over ABE7.10) raises headline efficiency while *lowering* purity (higher processivity sweeps more bystanders). Rank guides by the predicted **outcome spectrum**, never by efficiency alone.

The second field-defining insight: **base editors have THREE off-target classes, and the two that distinguish CBE from ABE are invisible to every Cas-off-target tool** (below). Most people only think of class 1 (guide-directed); the classes that matter for safety are Cas-independent and guide-invisible.

## Mechanism & the Position-Numbering Convention (get this right)

Both families are a **ssDNA deaminase fused to a Cas9 NICKASE (nCas9, D10A)**, guided by an ordinary sgRNA -- **no double-strand break**. When Cas9 binds, the non-target (PAM-containing) strand is displaced as ssDNA in the R-loop; the deaminase edits bases on that displaced strand within the window. **Canonical numbering (Komor 2016): position 1 = PAM-DISTAL (5' end of the spacer), position 20 = PAM-PROXIMAL (next to the PAM at 21-23). The editing window is ~positions 4-8, peak ~5-7.** (This is the opposite of what older tutorials sometimes say.)
- **CBE:** cytidine deaminase (rAPOBEC1) C->U, + **UGI** (blocks uracil excision -- the main CBE purity determinant), nCas9 nicks the unedited strand -> resolves to C->T (G->A other strand).
- **ABE:** lab-evolved TadA* deaminase A->inosine (read as G) -> resolves to A->G (T->C other strand). No UGI needed (inosine is not efficiently excised) -- a key reason early ABE was intrinsically cleaner than CBE.

## The Window Is a Gradient, Editor-Specific -- not a box

Activity inside the "box" is a steep gradient: a target at position 6 edits far better than one at 8; a bystander at 8 edits at a fraction of one at 5. The design move is "how close to the 5-6-7 peak is my target, and how far toward the cold edges can I push the bystanders?" The width is a property of the **editor variant**: ABE8e's high processivity widens it to ~3-11, so a guide that was bystander-clean with ABE7.10 becomes dirty when "upgraded" to ABE8e without re-checking. Carrying a window assumption across an editor switch is the most common silent failure.

## Editor Variant Selection

| Editor | Class | When |
|--------|-------|------|
| **BE4max / AncBE4max** | CBE | default modern CBE (Koblan 2018) |
| **ABEmax** | ABE | strong default ABE (Koblan 2018) |
| **ABE8e** | ABE | maximum activity (hard targets, screens) -- but WIDER window, MORE bystanders/off-target, LOSES context preference (Richter 2020; Lapinaite 2020) |
| YE1 / SECURE-BE3 | CBE | narrowed window / low RNA off-target (Grunewald 2019) |
| **TadCBE / TadDE** | CBE / dual | lowest Cas-independent DNA+RNA off-target CBE (Neugebauer 2023) |
| CGBE1 | C->G | the only transversion a base editor does well (Kurt 2021) |
| A&C-BEmax / SPACE | dual | simultaneous C->T and A->G (niche; adds bystander surface) (Grunewald 2020; Sakata 2020) |
| SpG / SpRY base editors | any | when no canonical NGG positions the base (Walton 2020) -- more class-1 off-target |

Default BE4max/ABEmax; reach for ABE8e for activity at a purity cost; a SECURE/TadCBE variant when off-target matters; a PAM-flexible editor when no NGG positions the base. The *deaminase* choice (rAPOBEC1 vs APOBEC3A vs eA3A vs evolved TadA) sets window width, context, and off-target far more than the BE3-vs-BE4 generation number.

## The Three Off-Target Classes -- ask "which of the three?" first

| Class | Mechanism | Detected by | Mitigation |
|-------|-----------|-------------|------------|
| **1. Cas-dependent DNA** | guide mismatch-tolerance, like ordinary Cas9 | GUIDE-/CIRCLE-seq; in-silico (-> off-target-prediction) | high-fidelity Cas; guide selection |
| **2. Cas-INDEPENDENT DNA** | deaminase edits transiently-exposed genomic ssDNA, **no guide** | GOTI (Zuo 2019); WGS (Jin 2019) | choose a low-activity-deaminase variant (YE1, **TadCBE**) |
| **3. RNA** | deaminase edits cellular mRNA, **no guide**, transient | RNA-seq (Grunewald/Rees/Zhou 2019) | **SECURE** variants (rAPOBEC1 R33A; ABE F148A); TadCBE |

Classes 2-3 have no protospacer, so they are **invisible to every guide-based predictor** -- the guide cannot be designed to avoid them; only a cleaner editor can. **CBE has historically been the dirtier family on classes 2-3** (Zuo/Jin: CBE >20x background Cas-independent SNVs, mostly C>T in transcribed DNA; early ABE did not) -- a genuine input to the CBE-vs-ABE choice. But this is *variant*-specific, not family-destiny: ABE8e raised it back up; TadCBE pulled CBE's down. Class-3 RNA edits are transient (RNA turns over) -- a real dose/exposure-dependent liability for chronic/AAV/therapeutic use, often tolerable for a transient cell-line transfection.

## Knockout by Base Editing (no DSB)

Base editing knocks out a gene without a double-strand break -- no indel lottery, no large deletions/translocations, no p53 response, works in **non-dividing cells**, and safe for **multiplex** (no translocations between simultaneous cut sites). Two routes:
- **Premature stop (CRISPR-STOP/iSTOP):** a CBE converts **CAA->TAA, CAG->TAG, CGA->TGA** (sense) or **TGG->stop** via the antisense strand. Only these four codons are reachable; target an **early** stop (before functional domains, NMD-competent). iSTOP precomputed sgRNAs cover 97-99% of genes (Billon 2017; Kuscu 2017).
- **Splice-site disruption:** edit the invariant splice-donor **GT** or acceptor **AG** -> mis- splicing / exon skipping (Kluesner 2021). Often the more robust KO (every gene has many junctions; only ~half have a well-placed early stop codon).

The quiet failure mode: a base-editor KO is only as complete as the editing -- an incompletely edited cell still makes wild-type protein, and a bystander can turn an intended silent KO into a missense allele. Prefer an early pmSTOP; fall back to splice disruption; verify protein.

## Decision Tree by Scenario

| Desired edit | Use | Why |
|--------------|-----|-----|
| Write edit as base-pair change first | -- | C:G->T:A = CBE; A:T->G:C = ABE; resolves strand confusion (a "G->A" edit is a CBE job) |
| C:G->T:A or A:T->G:C transition, base positionable | **CBE / ABE** | higher efficiency, cleaner, no DSB -- preferred over PE/HDR for transitions |
| C->G transversion | CGBE | the only transversion a base editor does |
| Any other transversion, small indel, multi-base | -> prime-editing-design | beyond base-editor chemistry |
| Large insertion / knock-in | -> hdr-template-design (or PE+integrase) | beyond base editing |
| Knockout, no DSB / non-dividing / multiplex | **BE pmSTOP or splice disruption** | no translocations, works in post-mitotic cells |
| Both CBE and ABE could make it (opposite strands) | break the tie on **purity + off-target** | ABE historically cleaner on classes 2-3 (per variant) |
| No NGG positions the base | SpG/SpRY base editor | accept more class-1 off-target |
| Off-target raised | ask "which of the three classes?" | class 1 -> off-target-prediction; 2-3 -> editor variant |
| Validate outcomes | -> crispr-screens/base-editing-analysis | amplicon NGS spectrum |

## Find Editable Guides and Read the Window

**Goal:** Find guides that place the target base near the window peak with the fewest in-window bystanders, and read the genotype spectrum the window implies.

**Approach:** Scan both strands for PAMs, compute where the target base lands in the spacer (PAM-distal = position 1), keep guides where it falls in the window, list bystander C's/A's, and read the 5' dinucleotide context of each (TC favored / GC disfavored for APOBEC1). The position-efficiency values below are **coarse illustrative gradients, not measurements** -- for a real outcome spectrum use BE-Hive/DeepBE, then validate by NGS. (See `examples/base_editing_design.py`.)

```python
from Bio.Seq import Seq
import re

CBE_WINDOW = (4, 8)   # activity gradient, peak ~5-7; PAM-distal numbering (position 1 = 5' end of spacer)
ABE_WINDOW = (4, 8)   # ABE7.10 tighter (~4-7); ABE8e WIDER (~3-11) -- editor-specific
```

## Per-Method Failure Modes

### Ranked guides by efficiency, shipped a genotype soup
**Trigger:** sorting by on-target editing %. **Mechanism:** efficiency hides the bystander spectrum. **Symptom:** "80% edited" but few alleles have the exact desired genotype. **Fix:** rank by predicted precise (bystander-free) editing; report the spectrum (BE-Hive).

### Carried a window across an editor switch
**Trigger:** "upgraded" to ABE8e, kept the ABE7.10 window. **Mechanism:** ABE8e's window is wider (~3-11). **Symptom:** new bystanders, dirtier product. **Fix:** use the variant-specific window; re-check bystanders after any editor change.

### Treated a base-editor off-target like a Cas9 off-target
**Trigger:** running GUIDE-seq/in-silico predictors and declaring it safe. **Mechanism:** those cover only class 1; classes 2-3 are guide-invisible. **Symptom:** clean class-1 report, genome/transcriptome-wide deaminase collateral. **Fix:** ask "which of the three?"; for 2-3 pick a SECURE/TadCBE variant.

### Picked the wrong editor (strand confusion)
**Trigger:** wanting a "G->A" change and reaching for ABE. **Mechanism:** G->A is C->T on the complement = a CBE job. **Symptom:** no editor can make it. **Fix:** write the edit as a base-pair change first.

### "I designed a stop, the gene is off"
**Trigger:** assuming pmSTOP = knockout. **Mechanism:** incomplete editing leaves WT protein; a late/NMD-escaping stop leaves functional product; a bystander makes a missense allele. **Fix:** target an early stop or splice site; verify at the protein level.

### Reached for SpRY by default
**Trigger:** using a PAM-flexible editor for convenience. **Mechanism:** relaxed PAM tolerates more mismatches -> more class-1 off-target. **Fix:** exhaust NGG first; use SpG/SpRY as a deliberate trade and check off-target harder.

## Quantitative Thresholds

| Parameter | Value | Source |
|-----------|-------|--------|
| CBE window | ~positions 4-8, peak 5-7 (PAM-distal numbering) | Komor 2016 |
| ABE7.10 window | ~4-7/4-8 | Gaudelli 2017 |
| ABE8e window | ~3-11 (wider, more bystanders) | Richter 2020; Lapinaite 2020 |
| APOBEC1 context | TC strongly preferred, GC strongly disfavored | Komor 2016 |
| iSTOP codons | CAA/CAG/CGA (sense) + TGG (antisense) | Billon 2017 |
| iSTOP gene coverage | 97-99% of genes (with some editor) | Billon 2017 |
| CBE Cas-independent DNA off-target | >20x background (early CBE; not early ABE) | Zuo 2019; Jin 2019 |
| Purity metric | report % target-edit-AND-no-bystander, or the full spectrum | BE-Hive (Arbab 2020) |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| No editable guide found | no PAM lands the base at ~5-7 | use SpG/SpRY base editor; check the other strand |
| Many in-window bystanders | multi-C/multi-A window | reposition to the peak; narrowed-window variant (YE1); exploit GC-context disfavor |
| "Fewest off-target edits" conflates bystanders with off-targets | mislabeling | bystanders are in-window on-locus; off-targets are elsewhere -- different fixes |
| Clean predicted spectrum but genomic collateral | model predicts on-target window only | classes 2-3 need editor choice + orthogonal assays |

## References

- Komor AC, Kim YB, Packer MS, Zuris JA, Liu DR (2016). Programmable editing of a target base in genomic DNA without double-stranded DNA cleavage. *Nature* 533(7603):420-424.
- Komor AC, Zhao KT, Packer MS, et al. (2017). Improved base excision repair inhibition and bacteriophage Mu Gam protein yields C:G-to-T:A base editors with higher efficiency and product purity (BE4/BE4-Gam). *Sci Adv* 3(8):eaao4774.
- Gaudelli NM, Komor AC, Rees HA, et al. (2017). Programmable base editing of A:T to G:C in genomic DNA without DNA cleavage (ABE7.10). *Nature* 551(7681):464-471.
- Koblan LW, Doman JL, Wilson C, et al. (2018). Improving cytidine and adenine base editors by expression optimization and ancestral reconstruction (BE4max/AncBE4max/ABEmax). *Nat Biotechnol* 36(9):843-846.
- Richter MF, Zhao KT, Eton E, et al. (2020). Phage-assisted evolution of an adenine base editor with improved Cas domain compatibility and activity (ABE8e). *Nat Biotechnol* 38(7):883-891.
- Lapinaite A, Knott GJ, Palumbo CM, et al. (2020). DNA capture by a CRISPR-Cas9-guided adenine base editor. *Science* 369(6503):566-571.
- Zuo E, Sun Y, Wei W, et al. (2019). Cytosine base editor generates substantial off-target single-nucleotide variants in mouse embryos (GOTI). *Science* 364(6437):289-292.
- Jin S, Zong Y, Gao Q, et al. (2019). Cytosine, but not adenine, base editors induce genome-wide off-target mutations in rice. *Science* 364(6437):292-295.
- Grunewald J, Zhou R, Garcia SP, et al. (2019). Transcriptome-wide off-target RNA editing induced by CRISPR-guided DNA base editors. *Nature* 569(7756):433-437.
- Zhou C, Sun Y, Yan R, et al. (2019). Off-target RNA mutation induced by DNA base editing and its elimination by mutagenesis. *Nature* 571(7764):275-278.
- Rees HA, Wilson C, Doman JL, Liu DR (2019). Analysis and minimization of cellular RNA editing by DNA adenine base editors (SECURE-ABE). *Sci Adv* 5(5):eaax5717.
- Grunewald J, Zhou R, Iyer S, et al. (2019). CRISPR DNA base editors with reduced RNA off-target and self-editing activities (SECURE-BE3). *Nat Biotechnol* 37(9):1041-1048.
- Billon P, Bryant EE, Joseph SA, et al. (2017). CRISPR-Mediated Base Editing Enables Efficient Disruption of Eukaryotic Genes through Induction of STOP Codons (iSTOP). *Mol Cell* 67(6):1068-1079.
- Kuscu C, Parlak M, Tufan T, et al. (2017). CRISPR-STOP: gene silencing through base-editing-induced nonsense mutations. *Nat Methods* 14(7):710-712.
- Kluesner MG, Lahr WS, Lonetree CL, et al. (2021). CRISPR-Cas9 cytidine and adenosine base editing of splice-sites mediates highly-efficient disruption of proteins in primary and immortalized cells. *Nat Commun* 12:2437.
- Arbab M, Shen MW, Mok BY, et al. (2020). Determinants of Base Editing Outcomes from Target Library Analysis and Machine Learning (BE-Hive). *Cell* 182(2):463-480.
- Song M, Kim HK, Lee S, et al. (2020). Sequence-specific prediction of the efficiencies of adenine and cytosine base editors (DeepBE). *Nat Biotechnol* 38(9):1037-1043.
- Hwang GH, Park J, Lim K, et al. (2018). Web-based design and analysis tools for CRISPR base editing (BE-Designer/BE-Analyzer). *BMC Bioinformatics* 19:542.
- Kurt IC, Zhou R, Iyer S, et al. (2021). CRISPR C-to-G base editors for inducing targeted DNA transversions in human cells (CGBE1). *Nat Biotechnol* 39(1):41-46.
- Neugebauer ME, Hsu A, Arbab M, et al. (2023). Evolution of an adenine base editor into a small, efficient cytosine base editor with low off-target activity (TadCBE/TadDE). *Nat Biotechnol* 41(5):673-685.
- Walton RT, Christie KA, Whittaker MN, Kleinstiver BP (2020). Unconstrained genome targeting with near-PAMless engineered CRISPR-Cas9 variants (SpG/SpRY). *Science* 368(6488):290-296.
- Grunewald J, Zhou R, Lareau CA, et al. (2020). A dual-deaminase CRISPR base editor enables concurrent adenine and cytosine editing (A&C-BEmax). *Nat Biotechnol* 38(7):861-864.
- Sakata RC, Ishiguro S, Mori H, et al. (2020). Base editors for simultaneous introduction of C-to-T and A-to-G mutations. *Nat Biotechnol* 38(7):865-869.

## Related Skills

- grna-design - Cas-domain on-target/class-1 guide scoring this skill builds the window/bystander layer on
- prime-editing-design - For transversions (except C->G), indels, and multi-base replacements
- off-target-prediction - Owns the class-1 Cas-dependent off-target assays/prediction
- crispr-screens/base-editing-analysis - Quantify editing outcomes from NGS after the experiment
- crispr-screens/crispresso-editing - Amplicon editing-spectrum quantification
- variant-calling/variant-annotation - Annotate the consequence of the installed edit
<!-- END FILE: genome-engineering/base-editing-design/SKILL.md -->

## 子目录：genome-engineering/grna-design

<!-- BEGIN FILE: genome-engineering/grna-design/SKILL.md -->
---
name: bio-genome-engineering-grna-design
description: Designs and ranks guide RNAs (sgRNAs) for CRISPR-Cas9/Cas12a gene knockout by scanning a target for PAM sites (NGG SpCas9, NNGRRT SaCas9, TTTV Cas12a, NG SpCas9-NG, near-PAMless SpRY), enumerating candidate spacers, applying hard filters (Pol-III TTTT terminator, 5' G, GC), ranking on-target activity with the context-appropriate model (Rule Set 2/Azimuth for U6/lentiviral, CRISPRscan for T7/embryo, DeepHF for high-fidelity variants, DeepCpf1 for Cas12a), and predicting the indel/frameshift outcome (Bae out-of-frame score, inDelphi, FORECasT, Lindel). Use when selecting sgRNAs to knock out a gene, choosing a nuclease/PAM for a constrained locus, picking which exon to target, or shortlisting guides before an off-target check. Off-target specificity, base/prime editing, and HDR donors are separate skills.
tool_type: python
primary_tool: CRISPOR
---

## Version Compatibility

Reference examples tested with: BioPython 1.83+, CRISPOR 5.0+ (web/CLI).

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed package and adapt the example to match the actual API rather than retrying.

Output depends on inputs more than tool versions: on-target scores are **model-specific and not interchangeable** (a 0.7 Azimuth score is not a 0.7 CRISPRscan score), and the **valid model is set by how the guide is delivered/transcribed**, not by preference. Record the nuclease, the delivery context (U6/lentiviral vs in-vitro T7/RNP), and the reference genome build used for any off-target step.

# Guide RNA Design

**"Design guide RNAs to knock out my gene"** -> Establish the delivery context, scan the target for the nuclease's PAM on both strands, drop guides that fail hard filters, rank survivors with the context-valid on-target model, choose the cut site by exon/transcript biology, and prefer guides whose predicted indel spectrum is frameshift-rich.
- Python: enumerate PAMs and apply hard filters with `Bio.Seq` + `re`; compute a Bae-style microhomology out-of-frame score
- CLI/web: `crispor.py <genome> in.fa out.tsv` aggregates the context-appropriate on-target score + off-target nomination per genome
- Web/code: inDelphi / FORECasT / Lindel for the full repair-outcome distribution

## The Single Most Important Modern Insight -- a guide produces a reproducible indel *distribution*, not "a cut", and knockout success is a property of that distribution

Two facts that naive design ignores and that pass review constantly:

1. **On-target efficiency scores are weak, context-locked predictors.** Rule Set 2, CRISPRscan, and DeepCas9 scores correlate with measured cutting at only **Spearman ~0.4 across realistic contexts** (~0.7 is the ceiling even within one matched context; the *same* guides re-tested in another cell line correlate ~0.37-0.48). Each was trained on one assay -- U6-Pol-III lentiviral vs in-vitro T7 vs RNP -- and **does not transfer** across nuclease, delivery, promoter, cell type, or temperature (Haeussler 2016). Using CRISPRscan (T7/zebrafish-trained) to rank guides for a U6 lentiviral screen is a category error. **Rank to shortlist, then design 3-6 guides and validate** -- never trust the rank as truth.

2. **Efficient editing is not knockout.** A cut yields a *characteristic, reproducible* set of indels (Shen 2018; Allen 2019; Chen 2019); roughly **1/3 of indels are in-frame**, so a 95%-efficient guide can still leave functional protein. Worse, even a confirmed frameshift may not eliminate protein -- translation reinitiation, exon skipping, NMD escape, and transcriptional adaptation rescue ~1/3 of verified knockouts (Smits 2019; Mou 2017; El-Brolosy 2019). So the modern question is **"which guide, at which site, produces a high out-of-frame fraction in an NMD-competent, constitutive transcript region?"** -- couple an *outcome model* to *exon biology*, not just an efficiency score. Verify the knockout at the **protein** level.

## On-Target Score Taxonomy -- each model is valid for ONE context

| Model | Citation | Trained on (valid for) | Notes |
|-------|----------|------------------------|-------|
| Rule Set 1 | Doench 2014 *Nat Biotechnol* 32:1262 | U6 mammalian | superseded; origin of GC/position rules |
| **Rule Set 2 / Azimuth** | Doench/Fusi 2016 *Nat Biotechnol* 34:184 | **U6/lentiviral mammalian KO -- the default for screens & cell lines** | gradient-boosted; best U6 predictor (Haeussler 2016) |
| **CRISPRscan** | Moreno-Mateos 2015 *Nat Methods* 12:982 | **in-vitro T7 / embryo injection -- NOT U6** | wrong tool for lentiviral screens |
| DeepSpCas9 | Kim 2019 *Sci Adv* 5:eaax9249 | SpCas9 mammalian; strong transfer | CNN |
| **DeepHF** | Wang 2019 *Nat Commun* 10:4284 | conditions on the **enzyme variant** (WT, eSpCas9, HF1) | use when using a high-fidelity Cas9 |
| **DeepCpf1 / Seq-deepCpf1** | Kim 2018 *Nat Biotechnol* 36:239 | **AsCas12a** (Deep adds chromatin) | use for Cas12a, not Cas9 |

Treat any score as a **rank-and-shortlist** signal (Spearman ~0.4 across context), never an oracle.

## Nuclease & PAM Taxonomy -- expanding PAM range trades away activity/specificity

| Nuclease | PAM | Guide | Cut | When |
|----------|-----|-------|-----|------|
| **SpCas9 (WT)** | 5'-NGG-3' | 20 nt | blunt, ~3 bp 5' of PAM | default workhorse; most data, most scores |
| SaCas9 | 5'-NNGRRT-3' | ~21 nt | blunt | ~1 kb smaller -> **fits a single AAV** (Ran 2015) |
| SpCas9-NG | 5'-NG-3' | 20 nt | blunt | relaxed PAM; lower activity at many sites (Nishimasu 2018) |
| xCas9 | NG, GAA, GAT | 20 nt | blunt | broad PAM, high specificity, site-variable/modest activity (Hu 2018) |
| SpRY | near-PAMless (NRN>NYN) | 20 nt | blunt | "target anywhere"; pays in activity + off-target breadth (Walton 2020) |
| AsCas12a / LbCas12a | 5'-TTTV-3' (5' PAM) | ~20-23 nt | staggered 5' overhang | AT-rich targets; self-processing crRNA array = easy multiplexing |
| enAsCas12a | expanded (TTTV + non-canonical) | ~20-23 nt | staggered | ~2x activity + broadened range (Kleinstiver 2019) |

Default to WT-SpCas9-NGG; escalate to NG/xCas9/SpRY only when no acceptable NGG sits in the required window, and expect to validate harder (the valid on-target score and the off-target burden both change).

## Decision Tree by Scenario

| Scenario | Recommended | Why |
|----------|-------------|-----|
| Single-gene KO, NGG in an early constitutive exon | SpCas9 + Rule Set 2/Azimuth shortlist -> outcome model -> off-target | frameshift in an NMD-competent exon kills all isoforms |
| In-vitro-transcribed / embryo / RNP injection | score with **CRISPRscan**, apply T7 (not U6) filters | Rule Set 2 is invalid here; TTTT/5'G Pol-III rules do not apply |
| AT-rich target, no good NGG; or multiplex KO | Cas12a (TTTV) + DeepCpf1 | PAM availability and crRNA-array multiplexing, not on-target score, are limiting |
| AAV in-vivo delivery | SaCas9 (NNGRRT) | packaging limit dictates the compact nuclease, which dictates the PAM set |
| Functional/negative-selection screen | tile sgRNAs across the **conserved functional domain** (Shi 2015) | domain indels are LoF even in-frame -> more true nulls than 5'-exon targeting |
| Have ranked candidates, need specificity | -> off-target-prediction | on-target score does not predict specificity |
| Scale to many genes | -> crispr-screens/library-design | pooled library construction |
| Single base change / no DSB tolerated | -> base-editing-design or prime-editing-design | scarless, DSB-free; KO-by-stop also avoids indels |

## Enumerate and Filter Candidate Guides

**Goal:** Return valid candidate spacers for a target, on both strands, dropping guides that cannot work in the chosen delivery context.

**Approach:** Scan both strands for the nuclease's PAM, extract the protospacer upstream (Cas9) or downstream (Cas12a) of each PAM, and apply hard filters -- reject `TTTT` (Pol-III terminator) for U6/H1 expression, flag a missing 5' G for U6 (prepend a G rather than replace the first base), and note GC outside ~40-70% as a soft penalty. Ranking comes from the context-valid model (route to CRISPOR), not from a hand-rolled score.

```python
from Bio.Seq import Seq
import re

GC_MIN, GC_MAX = 0.40, 0.70   # outside this band on-target activity falls off (Doench 2014); soft penalty

def find_guides(sequence, pam='NGG', guide_length=20):
    '''Enumerate SpCas9 (NGG) spacers on both strands; spacer is 5' of the PAM.'''
    seq = sequence.upper()
    guides = []
    for m in re.finditer(r'(?=([ACGT]GG))', seq):
        pos = m.start()
        if pos >= guide_length:
            guides.append({'spacer': seq[pos - guide_length:pos], 'pam': seq[pos:pos + 3],
                           'cut': pos - 3, 'strand': '+'})   # SpCas9 cuts ~3 bp 5' of the PAM
    rc = str(Seq(seq).reverse_complement())
    n = len(seq)
    for m in re.finditer(r'(?=([ACGT]GG))', rc):
        pos = m.start()
        if pos >= guide_length:
            guides.append({'spacer': rc[pos - guide_length:pos], 'pam': rc[pos:pos + 3],
                           'cut': n - (pos - 3), 'strand': '-'})
    return guides

def passes_u6_filters(spacer):
    '''Hard filters for U6/H1 Pol-III expression (NOT applicable to in-vitro T7/RNP).'''
    gc = sum(c in 'GC' for c in spacer) / len(spacer)
    return 'TTTT' not in spacer and GC_MIN <= gc <= GC_MAX   # TTTT terminates Pol III
```

## Rank On-Target Activity in the Valid Context

**Goal:** Shortlist guides by predicted cutting using the model that matches the delivery context.

**Approach:** Do NOT hand-roll a scoring matrix. Route to CRISPOR, which selects the context-appropriate score (Rule Set 2/Azimuth for U6/lentiviral, CRISPRscan for T7/embryo) per the Haeussler 2016 logic and also nominates off-targets against the chosen genome. Treat the returned score as a shortlist signal, then carry 3-6 candidates forward.

```bash
# CRISPOR: aggregates the context-valid on-target score + off-target nomination per genome
crispor.py hg38 target.fa guides.tsv --maxOcc 60000
# columns include the on-target score (context-selected) and off-target counts/specificity
```

## Choose the Cut Site by Exon Biology (the under-used lever)

KO success is mostly won here, and pure efficiency ranking fails:
- Target an **early, constitutive coding exon** (present in all protein-coding isoforms) -- but **not the start-ATG region** (downstream reinitiation can rescue an N-terminal truncation).
- **Avoid the last exon and the last ~50 nt of the penultimate exon** -- PTCs there **escape NMD**, leaving a stable, possibly-functional truncated protein.
- Keep the cut **away from splice donor/acceptor sites** unless splice disruption is the goal -- indels there cause **exon skipping** that can restore frame (Mou 2017).
- Confirm the exon is constitutive **in the cell type of interest** (an exon spliced out of the dominant isoform is a silent failure), and screen for **SNPs under the protospacer/PAM** in the actual background (mismatch/PAM loss -> allele dropout).
- For ruthless KO / screens: **tile the conserved functional domain** (Shi 2015), not the gene start.

## Predict the Editing Outcome (frameshift fraction decides KO)

**Goal:** Prefer guides whose predicted indel spectrum is frameshift-rich (and, for a single-genotype line, dominated by one outcome).

**Approach:** Cas9 repair outcomes are predictable from the ~30 bp of local sequence flanking the cut. The cheap, no-ML signal is the **Bae 2014 microhomology out-of-frame score**: enumerate microhomology pairs flanking the cut, weight each predicted MMEJ deletion, and report the fraction whose length is not a multiple of 3. For a full genotype distribution use **inDelphi** (Shen 2018), **FORECasT** (Allen 2019), or **Lindel** (Chen 2019). Rank by **(editing efficiency) x (out-of-frame fraction)** -- a 70%-efficient guide with frameshift fraction 0.9 beats a 90%-efficient guide at 0.5. (See `examples/grna_design.py` for a runnable Bae-style out-of-frame implementation.)

## Per-Method Failure Modes

### "We used the top-ranked guide" with no validation
**Trigger:** sorting by on-target score and taking #1. **Mechanism:** scores are Spearman ~0.4 across context. **Symptom:** confident ranking, poor empirical hit rate. **Fix:** design 3-6 guides per gene and validate; treat the score as triage.

### Score used out of its training context
**Trigger:** CRISPRscan for a lentiviral screen, or Rule Set 2 for embryo RNP. **Mechanism:** each model is an assay artifact (Haeussler 2016). **Symptom:** "principled" but wrong ranking. **Fix:** pick the score from the delivery context before reading any number.

### Efficient cut, no knockout phenotype
**Trigger:** ranking by editing efficiency. **Mechanism:** ~1/3 in-frame indels + reinitiation/exon-skipping/NMD-escape/compensation. **Symptom:** high indel %, residual protein, milder-than-knockdown phenotype. **Fix:** rank by frameshift fraction (Bae/inDelphi), target early constitutive NMD-competent exons, verify at protein level.

### Last-exon / splice-site guide
**Trigger:** "early exon" applied naively. **Mechanism:** late PTC escapes NMD; splice-site indel skips the exon. **Symptom:** stable truncated/reframed protein. **Fix:** retarget an early constitutive exon away from junctions.

### Poly-T or missing 5' G in a U6 construct
**Trigger:** spacer with `TTTT` or non-G 5' end expressed from U6/H1. **Mechanism:** Pol-III termination / poor initiation. **Symptom:** little or no sgRNA. **Fix:** reject TTTT; prepend (do not replace) a 5' G. (Irrelevant for in-vitro T7/RNP.)

### Allele dropout in a non-reference background
**Trigger:** designing against GRCh38 for a patient/hybrid/cancer line. **Mechanism:** a SNP in the seed or PAM blocks one allele. **Symptom:** heterozygous "knockout" with a retained functional allele. **Fix:** design against the actual genotype.

## Quantitative Thresholds

| Parameter | Value | Source / rationale |
|-----------|-------|--------------------|
| On-target score use | rank/shortlist only; ~0.4 Spearman across context | Haeussler 2016 |
| GC content | ~40-70% (soft penalty) | Doench 2014 |
| Pol-III terminator | reject `TTTT` (U6/H1 only) | Pol-III termination |
| 5' G (U6) | prepend a G if absent | Pol-III initiation preference |
| SpCas9 cut | ~3 bp 5' of NGG (blunt) | Jinek 2012 |
| Bae out-of-frame score | prefer **>66** | Bae 2014 frameshift-reliability recommendation |
| KO ranking | efficiency x out-of-frame fraction | frameshift fraction, not cutting, drives KO |
| Guides per gene | **3-6**, validate empirically | scores are weak; redundancy buys back error |
| Exon target | early, constitutive, NMD-competent (not last exon / last ~50 nt of penult.) | PTC must trigger NMD across all isoforms |
| Residual protein after frameshift | expect ~1/3 retain protein | Smits 2019 |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| No guides found | no PAM in window / wrong PAM for nuclease | try Cas12a (TTTV) for AT-rich; widen window; SpCas9-NG/SpRY as last resort |
| Guide cuts but no KO phenotype | last exon / 3'UTR / in-frame indels / compensation | retarget early constitutive exon; rank by frameshift; verify protein |
| Score looks low for a clearly good guide | score used outside its training context | use the context-valid model |
| Heterozygous result in a non-reference line | SNP under guide/PAM | design against the actual genotype |

## References

- Jinek M, et al. (2012). A programmable dual-RNA-guided DNA endonuclease in adaptive bacterial immunity. *Science* 337(6096):816-821.
- Doench JG, et al. (2014). Rational design of highly active sgRNAs for CRISPR-Cas9-mediated gene inactivation. *Nat Biotechnol* 32(12):1262-1267.
- Doench JG, Fusi N, Sullender M, et al. (2016). Optimized sgRNA design to maximize activity and minimize off-target effects of CRISPR-Cas9. *Nat Biotechnol* 34(2):184-191.
- Moreno-Mateos MA, et al. (2015). CRISPRscan: designing highly efficient sgRNAs for CRISPR-Cas9 targeting in vivo. *Nat Methods* 12(10):982-988.
- Haeussler M, et al. (2016). Evaluation of off-target and on-target scoring algorithms and integration into the guide RNA selection tool CRISPOR. *Genome Biol* 17:148.
- Kim HK, et al. (2019). SpCas9 activity prediction by DeepSpCas9. *Sci Adv* 5(11):eaax9249.
- Wang D, et al. (2019). Optimized CRISPR guide RNA design for two high-fidelity Cas9 variants by deep learning (DeepHF). *Nat Commun* 10:4284.
- Kim HK, et al. (2018). Deep learning improves prediction of CRISPR-Cpf1 guide RNA activity (DeepCpf1). *Nat Biotechnol* 36(3):239-241.
- Bae S, Kweon J, Kim HS, Kim JS (2014). Microhomology-based choice of Cas9 nuclease target sites. *Nat Methods* 11(7):705-706.
- Shen MW, et al. (2018). Predictable and precise template-free CRISPR editing of pathogenic variants (inDelphi). *Nature* 563(7733):646-651.
- Allen F, et al. (2019). Predicting the mutations generated by repair of Cas9-induced double-strand breaks (FORECasT). *Nat Biotechnol* 37(1):64-72.
- Chen W, et al. (2019). Massively parallel profiling and predictive modeling of the outcomes of CRISPR-Cas9 double-strand break repair (Lindel). *Nucleic Acids Res* 47(15):7989-8003.
- Shi J, et al. (2015). Discovery of cancer drug targets by CRISPR-Cas9 screening of protein domains. *Nat Biotechnol* 33(6):661-667.
- Smits AH, et al. (2019). Biological plasticity rescues target activity in CRISPR knock outs. *Nat Methods* 16(11):1087-1093.
- Mou H, et al. (2017). CRISPR/Cas9-mediated genome editing induces exon skipping by alternative splicing or exon deletion. *Genome Biol* 18(1):108.
- El-Brolosy MA, et al. (2019). Genetic compensation triggered by mutant mRNA degradation. *Nature* 568(7751):193-197.
- Ran FA, et al. (2015). In vivo genome editing using Staphylococcus aureus Cas9. *Nature* 520(7546):186-191.
- Nishimasu H, et al. (2018). Engineered CRISPR-Cas9 nuclease with expanded targeting space (SpCas9-NG). *Science* 361(6408):1259-1262.
- Hu JH, et al. (2018). Evolved Cas9 variants with broad PAM compatibility and high DNA specificity (xCas9). *Nature* 556(7699):57-63.
- Walton RT, et al. (2020). Unconstrained genome targeting with near-PAMless engineered CRISPR-Cas9 variants (SpRY). *Science* 368(6488):290-296.
- Kleinstiver BP, et al. (2019). Engineered CRISPR-Cas12a variants with increased activities and improved targeting ranges (enAsCas12a). *Nat Biotechnol* 37(3):276-282.
- Concordet JP, Haeussler M (2018). CRISPOR: intuitive guide selection for CRISPR/Cas9 genome editing experiments and screens. *Nucleic Acids Res* 46(W1):W242-W245.

## Related Skills

- off-target-prediction - Check genome-wide specificity after on-target design (a separate axis from activity)
- base-editing-design - DSB-free knockout via premature stop / splice disruption when indels are unwanted
- prime-editing-design - Scarless small edits without a double-strand break
- hdr-template-design - Design the donor when the goal is a precise knock-in, not a knockout
- crispr-screens/library-design - Pool guides into a screening library (domain tiling, Rule Set 2 logic)
- crispr-screens/crispresso-editing - Quantify indel/editing outcomes from amplicon sequencing
- primer-design/primer-basics - Design validation/genotyping primers around the cut
- primer-design/primer-specificity - Confirm genotyping primers are unique near paralogs/off-targets
- genome-intervals/gtf-gff-handling - Get exon coordinates to restrict guide placement
<!-- END FILE: genome-engineering/grna-design/SKILL.md -->

## 子目录：genome-engineering/hdr-template-design

<!-- BEGIN FILE: genome-engineering/hdr-template-design/SKILL.md -->
---
name: bio-genome-engineering-hdr-template-design
description: Designs donor/repair templates for precise CRISPR knock-ins -- choosing the format (ssODN, long-ssDNA/Easi-CRISPR, dsDNA/plasmid, AAV6), sizing homology arms, placing the cut within ~10 bp of the edit, and adding a mandatory codon-checked blocking (PAM/seed) mutation so the edited allele is not re-cut. Frames the HDR-vs-NHEJ-vs-MMEJ pathway competition, the MMEJ (PITCh) and homology-independent (HITI/HMEJ) alternatives for post-mitotic cells, ssODN strand/asymmetry choice, phosphorothioate end-protection, and ranked HDR enhancers. Use when designing a donor for a point mutation, epitope/fluorophore tag, allele replacement, or knock-in, or when HDR efficiency is low. Guide design and base/prime editing are separate skills.
tool_type: python
primary_tool: primer3-py
---

## Version Compatibility

Reference examples tested with: BioPython 1.83+, primer3-py 2.0+.

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed package and adapt the example to match the actual API rather than retrying.

primer3-py designs PRIMERS (use `primer3.bindings.design_primers(seq_args, global_args)`; the camelCase `designPrimers` is deprecated since 1.0.0), not homology arms -- arm extraction and codon-aware blocking are the skill's own BioPython code. Design arms and guide against the **actual cell line's sequence**, not GRCh38 -- a SNP in an arm reduces annealing and a SNP in the PAM/seed can mean the guide does not cut.

# HDR Template Design

**"Design a donor for my CRISPR knock-in"** -> Decide the format by edit size and whether the cell cycles, size the arms, confirm a guide cuts within ~10 bp of the edit, and add a codon-checked blocking mutation so the corrected allele cannot be re-cut.
- Python: arm extraction + codon-aware PAM/seed blocking with `Bio.Seq`; `primer3.bindings.design_primers()` for arm-amplification and junction-validation primers
- Decision: format/route by cell type (cycling vs post-mitotic) and insert size

## The Single Most Important Modern Insight -- HDR is the minority pathway, and a donor without a blocking mutation is a self-destructing one

A Cas9 double-strand break is repaired by whichever pathway wins a kinetic race, and in most cells the winner is **classical NHEJ** (fast, all cell-cycle phases). MMEJ (microhomology, S/G2) and **HDR (template-dependent, S/G2 only)** are minority players, so **unenhanced HDR knock-in is typically single-digit to low-double-digit percent -- that is normal, not a failure.** The donor is not "the sequence to insert"; it is the toolkit for tilting a race NHEJ is structurally favored to win. The corollary, and the field's most expensive misread: **a donor with perfect arms but no blocking mutation gets its successful edit erased** -- the corrected allele still has an intact protospacer + PAM, so Cas9 re-cuts it and NHEJ scars it, and the indel reads out as "HDR failed" (indistinguishable from low HDR). So when someone reports "low HDR, lots of indels," the first question is not "how long are the arms?" -- it is **"does the donor disrupt the PAM or seed?"** A blocking mutation is mandatory and must be codon-checked; without it the readout is re-cutting, not HDR.

## The Pathway Competition (everything follows from this)

| Pathway | Cell cycle | Template | Signature | Relevance |
|---------|-----------|----------|-----------|-----------|
| **c-NHEJ** | all phases (dominant) | none | indels | the competitor; the engine HITI exploits |
| **MMEJ / alt-EJ** (Pol theta) | S/G2 | 5-25 bp microhomology | microhomology-flanked deletions | the PITCh route |
| **HDR / HR** | **S/G2 only** | sister chromatid or **exogenous donor** | precise, scarless | the classic knock-in route; minority |
| SSA | S/G2 | repeats | deletion between repeats | nuisance |

End resection (cell-cycle-gated, licensed in S/G2; 53BP1-RIF1 protects ends/pro-NHEJ, BRCA1 antagonizes it/pro-HDR) decides the fork. Consequences: **post-mitotic cells barely do HDR** -> for neurons/muscle/in-vivo tissue, HITI/HMEJ (NHEJ-based) is the *correct first choice*, not a fallback. Timing RNP+donor delivery into S/G2 raises HDR (Lin 2014, up to ~38% in HEK293T) -- the donor is necessary but the cell-cycle state gates it.

## Donor Format Decision

| Format | Insert | Arms | Best for | Caveat |
|--------|--------|------|----------|--------|
| **ssODN** | <= ~50 bp edits | ~30-60 nt each (total ~120-200 nt) | point mutations, small tags, loxP | synthesis ceiling ~200 nt; strand choice contested |
| **long ssDNA (Easi-CRISPR)** | ~0.2-2 kb | ~50-100 nt | cassettes, floxed/conditional alleles, zygote KI | **less toxic & less random integration than dsDNA**; harder to make |
| dsDNA (PCR/linear) | ~0.1-1.5 kb | ~200-800 bp | medium cassettes | **dsDNA is toxic** (innate sensing) + random integration |
| plasmid / HMEJ | up to several kb | ~500-2000 bp | large insertions, conditional alleles | backbone integration risk; slowest |
| **AAV6** | <= ~4.5 kb (ITR-to-ITR, arms included) | ~400 bp-1 kb | hard-to-transfect primary cells (HSPC, T, iPSC), in vivo | manufacturing cost; cargo cap is a hard wall |

Heuristics: point/small edit -> ssODN; 0.2-2 kb -> **lssDNA over dsDNA** (cleaner) for animal/zygote work; large cassette -> plasmid/HMEJ (lines) or **AAV6+RNP** (primary cells); **post-mitotic -> HITI**.

## Homology Arms, Edit-to-Cut Distance, and the Blocking Mutation (the most-botched trio)

- **Arm length:** ssODN ~30-60 nt each (more does not help, costs synthesis); dsDNA/plasmid ~500-800 bp sweet spot. Match the **actual cell-line sequence**, not the reference.
- **Edit-to-cut distance drives guide choice:** HDR incorporation falls sharply with distance, so place the cut **within ~10 bp of the edit** (Paquet 2016). The guide and donor are a *joint* design -- a "great" guide cutting 25 bp away is worse than a mediocre one cutting 3 bp away. **If no guide cuts within ~10 bp, HDR is the wrong tool** -> reconsider base/prime editing.
- **Blocking mutation (mandatory, codon-checked):** disrupt the **PAM** synonymously (preferred -- change a G in the NGG at a wobble position); if the PAM has no synonymous option, introduce **silent seed-region** mutations (PAM-proximal ~10-12 nt; PAM-distal mismatches are tolerated and do not block). The blocking edit must sit within the ~10 bp incorporation window (which is also where it blocks best). Paquet 2016 (CORRECT) raises per-allele accuracy ~10-fold and allows zygosity control by distance.

## ssODN Strand & Asymmetry (an over-cited rule) + the reliable win

Richardson 2016 proposed an ssODN **complementary to the non-target strand**, **asymmetric with the longer arm PAM-proximal (~91 nt) and the shorter PAM-distal (~36 nt)**. Subsequent systematic work could **not** reproduce this as universal: the optimal strand flips by locus and the asymmetric advantage often vanishes once both arms are >=30 nt. Treat it as a **prior to test, not a law** -- generate both strands and symmetric+asymmetric variants and test them. By contrast, **phosphorothioate (PS) end-protection (2-3 terminal bases each end)** is a near-universal cheap win (exonuclease resistance) -- encode these at opposite confidence levels.

## MMEJ / Homology-Independent Routes (when HDR is the wrong tool)

- **PITCh / CRIS-PITCh (MMEJ, Nakade 2014):** ~5-25 bp microhomologies instead of long arms; Pol theta joins donor to genome. Appeal is purely donor-construction convenience (microhomologies are primer overhangs); cost is error-prone junctions.
- **HITI (Suzuki 2016):** **homology-INDEPENDENT, NHEJ-based -> works in non-dividing cells.** The donor carries the same Cas9 target site(s) in **reverse orientation** flanking the insert; wrong-orientation insertions reconstitute the site and get re-cut/ejected, right-orientation insertions destroy it and lock in. Junctions can carry small indels.
- **HMEJ (Yao 2017):** ~800 bp arms PLUS flanking gRNA sites that linearize the donor in vivo; higher KI than HR/NHEJ/MMEJ in some contexts but ties/loses in others (mESC, N2a) -- test at the target locus.

| Situation | Route |
|-----------|-------|
| Point/small edit, cycling cells | ssODN + HDR (with blocking mutation) |
| Medium/large cassette, cycling line | HDR (lssDNA/plasmid) or HMEJ |
| Large cassette, primary cells (HSPC/T/iPSC) | AAV6 donor + RNP + HDR |
| Clean zygote/animal KI, <=2 kb | lssDNA Easi-CRISPR + HDR |
| Trivial donor construction wanted | PITCh (MMEJ) |
| **Non-dividing / post-mitotic / in vivo** | **HITI** (or HMEJ) |
| Edit far from any cut / single base | -> base-editing-design or prime-editing-design (donor-free) |

## HDR Enhancers -- ranked experiments, not multipliers

Most enhancers are marginal, cell-type-specific, and frequently non-reproducible; the published fold-changes are line-specific maxima. A blocking mutation and a cut near the edit matter more than any small molecule.
- **First tier (try by default, low risk):** cell-cycle timing of RNP delivery (Lin 2014); cold shock (32 C, 24-48 h; Guo 2018); PS end-protection; RNP+ssODN co-delivery.
- **Second tier (test in the target cells, expect variability):** DNA-PKcs inhibition (M3814/nedisertib -- the most consistently potent small molecule); 53BP1 inhibition (i53 / Alt-R HDR Enhancer).
- **Bottom tier (mention with a reproducibility warning):** SCR7 (widely un-reproducible), RS-1.

## Generate the Donor, Block Re-cutting (codon-checked), and Design Validation Primers

**Goal:** Assemble a donor that incorporates the edit AND survives re-cutting, with primers to amplify the arms and genotype the junction.

**Approach:** Extract arms flanking the cut, insert the edit, then add a blocking mutation -- disrupt the PAM synonymously if a wobble option exists, else introduce silent seed mutations -- verifying the change does not alter the encoded amino acid. Use primer3-py for arm-amplification/junction primers. (See `examples/hdr_template_design.py` for codon-aware blocking and a primer3 call.)

```python
from Bio.Seq import Seq

def synonymous_pam_block(codon_table, pam_codon, alt_codon):
    '''Return True only if a PAM-disrupting codon swap keeps the same amino acid (silent).'''
    return codon_table.get(pam_codon) == codon_table.get(alt_codon)   # never mutate the PAM without this check
```

## Per-Method Failure Modes

### "I got an indel, so HDR failed"
**Trigger:** low edit, mostly indels, no blocking mutation. **Mechanism:** the corrected allele keeps an intact PAM -> Cas9 re-cuts -> NHEJ scar. **Symptom:** indels indistinguishable from no-HDR. **Fix:** add a codon-checked PAM/seed blocking mutation; the readout was re-cutting, not HDR.

### Edit far from the cut
**Trigger:** best-cutting guide is 25 bp from the edit. **Mechanism:** HDR incorporation falls with distance. **Symptom:** only the blocking mutation is incorporated (useless silent-only allele) or no edit. **Fix:** choose a guide cutting within ~10 bp; if none, switch to base/prime editing.

### Frame-unaware blocking mutation
**Trigger:** blindly changing the NGG's second G to A. **Mechanism:** the PAM may be in a coding frame. **Symptom:** an unintended missense/nonsense change. **Fix:** verify the swap is synonymous; else use silent seed mutations.

### dsDNA in sensitive cells
**Trigger:** a plasmid/PCR donor in iPSC/primary/zygotes. **Mechanism:** dsDNA toxicity + random integration. **Symptom:** low viability, random integrants. **Fix:** use lssDNA (Easi-CRISPR) or AAV6.

### HDR donor in post-mitotic cells
**Trigger:** ssODN/plasmid for neurons/in-vivo tissue. **Mechanism:** HDR runs only in S/G2. **Symptom:** essentially no knock-in. **Fix:** use HITI (NHEJ-based) or HMEJ.

### Arms designed against the reference
**Trigger:** GRCh38 arms for a passaged/cancer line. **Mechanism:** line-specific SNPs in the arm or PAM/seed. **Symptom:** poor annealing or no cut. **Fix:** design against the cell line's actual sequence; account for ploidy/zygosity.

## Quantitative Thresholds

| Parameter | Value | Source |
|-----------|-------|--------|
| ssODN total length | ~120-200 nt | synthesis ceiling |
| ssODN arm | ~30-60 nt each | below ~30 HDR drops; above ~60 diminishing returns |
| dsDNA/plasmid arm | ~200-800 bp (up to ~2 kb) | ~500-800 bp common sweet spot |
| lssDNA insert | ~0.2-2 kb | Easi-CRISPR range |
| AAV cargo | <= ~4.5 kb (arms included) | packaging limit (hard wall) |
| PITCh microhomology | ~5-25 bp | MMEJ working range |
| **Edit-to-cut distance** | **<= ~10 bp** | HDR incorporation falls with distance (Paquet 2016) |
| Phosphorothioate | 2-3 terminal bases each end | exonuclease resistance |
| Cold shock | 32 C, 24-48 h | G2/M accumulation (Guo 2018) |
| Typical raw HDR | single-digit to ~20% (up to ~38-60% optimized) | minority pathway |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| Low HDR, mostly indels | no blocking mutation (re-cutting) | add codon-checked PAM/seed block |
| Only the silent mutation incorporated | edit too far from cut | cut within ~10 bp or switch to base/prime editing |
| Toxicity / random integration | dsDNA in sensitive cells | lssDNA or AAV6 |
| No knock-in in neurons/in vivo | HDR donor in post-mitotic cells | HITI/HMEJ |
| AAV donor will not package | arms + insert exceed ~4.5 kb | shorten arms/insert; budget against the cap |

## References

- Richardson CD, Ray GJ, DeWitt MA, Curie GL, Corn JE (2016). Enhancing homology-directed genome editing by catalytically active and inactive CRISPR-Cas9 using asymmetric donor DNA. *Nat Biotechnol* 34(3):339-344.
- Lin S, Staahl BT, Alla RK, Doudna JA (2014). Enhanced homology-directed human genome engineering by controlled timing of CRISPR/Cas9 delivery. *eLife* 3:e04766.
- Paquet D, Kwart D, Chen A, et al. (2016). Efficient introduction of specific homozygous and heterozygous mutations using CRISPR/Cas9 (CORRECT). *Nature* 533(7601):125-129.
- Quadros RM, Miura H, Harms DW, et al. (2017). Easi-CRISPR: a robust method for one-step generation of mice carrying conditional and insertion alleles using long ssDNA donors and CRISPR ribonucleoproteins. *Genome Biol* 18:92.
- Nakade S, Tsubota T, Sakane Y, et al. (2014). Microhomology-mediated end-joining-dependent integration of donor DNA in cells and animals using TALENs and CRISPR/Cas9 (PITCh). *Nat Commun* 5:5560.
- Suzuki K, Tsunekawa Y, Hernandez-Benitez R, et al. (2016). In vivo genome editing via CRISPR/Cas9 mediated homology-independent targeted integration (HITI). *Nature* 540(7631):144-149.
- Yao X, Wang X, Hu X, et al. (2017). Homology-mediated end joining-based targeted integration using CRISPR/Cas9 (HMEJ). *Cell Res* 27(6):801-814.
- Guo Q, Mintier G, Ma-Edmonds M, et al. (2018). 'Cold shock' increases the frequency of homology directed repair gene editing in induced pluripotent stem cells. *Sci Rep* 8:2080.
- Untergasser A, Cutcutache I, Koressaar T, et al. (2012). Primer3 -- new capabilities and interfaces. *Nucleic Acids Res* 40(15):e115.

## Related Skills

- grna-design - Choose the guide; HDR consumes its cut site (tightly coupled via edit-to-cut distance)
- base-editing-design - Donor-free alternative for single-base transitions far from any cut
- prime-editing-design - Donor-free precise small edits, and twinPE/PASTE for large insertions
- primer-design/primer-basics - PCR primers for arm amplification and junction genotyping
- primer-design/primer-validation - Check genotyping primers for dimers and hairpins
- primer-design/primer-specificity - Confirm the genotyping amplicon is unique (off-target/pseudogenes)
- sequence-io/read-sequences - Parse GenBank CDS/start/stop features for tag placement and codon-aware design
- variant-calling/variant-annotation - Confirm the installed edit and its consequence
<!-- END FILE: genome-engineering/hdr-template-design/SKILL.md -->

## 子目录：genome-engineering/off-target-prediction

<!-- BEGIN FILE: genome-engineering/off-target-prediction/SKILL.md -->
---
name: bio-genome-engineering-off-target-prediction
description: Nominates and assesses CRISPR off-target sites genome-wide. Enumerates candidate sites by mismatch and bulge tolerance with Cas-OFFinder/CRISPRitz, ranks them with the published CFD score (SpCas9-only, relative ranker) or MIT/CRISTA/energy models, runs variant-aware screening against gnomAD/individual genomes (CRISPRme), and frames the empirical genome-wide discovery assays (GUIDE-seq, CIRCLE-seq, CHANGE-seq, DISCOVER-seq, Digenome-seq) and high-fidelity nuclease choice (HiFi Cas9, Sniper-Cas9, eSpCas9, SpCas9-HF1). Use when assessing guide RNA specificity, choosing among candidate guides, screening a therapeutic guide against population variation, or planning empirical off-target validation. Distinguishes predicted vs detected vs validated. On-target activity scoring and deaminase (Cas-independent) base/prime-editor off-targets are separate skills.
tool_type: mixed
primary_tool: Cas-OFFinder
---

## Version Compatibility

Reference examples tested with: Cas-OFFinder 3.0+, pandas 2.2+, Python 3.10+.

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed package and adapt the example to match the actual API rather than retrying.

Results depend on inputs far more than tool versions: the candidate list is bounded by the **reference genome build, the mismatch/bulge tolerance, and the PAM pattern** searched, not by the Cas-OFFinder version. The **CFD matrix is SpCas9/NGG-specific and a relative ranker, not a calibrated cutting probability**. Load the published CFD tables (Doench 2016 / CRISPOR distribution) rather than hand-typing values. Cas-OFFinder is the maintained `snugel/cas-offinder` repository (native DNA/RNA bulge support from v3.0.0).

# Off-Target Prediction

**"Check my guide for off-targets"** -> Enumerate candidate sites genome-wide by mismatch/bulge tolerance, rank them by a per-site score, decide whether in-silico is sufficient or empirical discovery is required, and report each claim at the right rung: predicted, detected, or validated.
- CLI: `cas-offinder input.txt G output.txt` enumerates sites (no ranking)
- Python: CFD scoring from the published mismatch/PAM tables; aggregate specificity
- Web/CLI: `CRISPRme` for variant-aware (gnomAD + individual) nomination; `CRISPOR` to aggregate

## The Single Most Important Modern Insight -- in-silico enumeration nominates *candidates*; it does not measure *which sites are cut*

The naive model -- "search the genome within N mismatches, score by CFD, the high scorers are my off-targets" -- is wrong in three structural ways no better scoring fixes:

1. **Mismatch count is not cleavage.** A 2-mismatch site in closed chromatin may never be cut; a 3-mismatch site in open chromatin near an active promoter is. Cellular cutting depends on chromatin, dose, and exposure time -- invisible to a sequence search.
2. **Bulges and non-canonical PAMs are routinely missed.** Real validated off-targets occur with 1-2 nt DNA/RNA bulges and at NAG/NGA PAMs; fixed-alignment mismatch-only search misses them. **The failure is silent** -- a clean report looks identical whether the guide is specific or the search just couldn't see the off-target.
3. **CFD is a narrow, SpCas9-only relative ranker.** A CFD of 0.08 is not "8% chance of cutting"; comparing two guides' aggregate scores is fine, reading an absolute CFD as a safety threshold is not.

The corollary, and the central professor-level point: **in-silico lists overlap only partially with empirically validated off-targets, and the empirical genome-wide assays disagree with *each other* too.** No single method is authoritative. Off-target evidence escalates: **predicted -> detected by an unbiased assay -> validated by targeted amplicon deep-seq.** Conflating these rungs is the field's most common error. Therapeutic-grade assessment is *triangulation* (variant-aware in-silico + >=2 orthogonal empirical assays + amplicon validation + a structural readout), never one tool's output.

## In-Silico Taxonomy -- enumerate, then score, then aggregate

| Layer | Tool | Citation | Role / caveat |
|-------|------|----------|---------------|
| Enumerate | **Cas-OFFinder** | Bae 2014 *Bioinformatics* 30:1473 | exhaustive, alignment-free, GPU; **DNA/RNA bulges** (native v3.0.0); returns sites, **no ranking** |
| Enumerate (variant) | CRISPRitz | Cancellieri 2020 *Bioinformatics* 36:2001 | enumerates against genome **+ a VCF** of variants, with bulges; backend of CRISPRme |
| Enumerate (scale) | GuideScan2 | Schmidt 2025 *Genome Biol* 26:41 | genome-wide specificity databases (NOT Nat Biotechnol) |
| Score (per-site) | **CFD** | Doench 2016 *Nat Biotechnol* 34:184 | position x mismatch-type matrix x PAM penalty; **SpCas9/NGG only**, poor on bulges; de facto standard |
| Score (legacy) | MIT/Hsu | Hsu 2013 *Nat Biotechnol* 31:827 | original; **deprecated/flawed** -- report, don't lead with it |
| Score (ML) | CRISTA; Elevation | Abadi 2017; Listgarten 2018 | Elevation folds in chromatin accessibility |
| Aggregate | **CRISPOR**; **CRISPRme** | Concordet 2018 *NAR* 46:W242; Cancellieri 2023 *Nat Genet* 55:34 | CRISPOR = research one-stop; CRISPRme = variant-aware therapeutic nominator |

The unifying caveat: every score is bounded by the enumerator's coverage -- **if the enumerator didn't propose a site (bulge, distal PAM, beyond the mismatch cutoff), no scorer will ever flag it.**

## Empirical Discovery Assays -- each has a characteristic bias; concordance is partial

| Assay | Citation | Class | Bias |
|-------|----------|-------|------|
| **CIRCLE-seq** | Tsai 2017 *Nat Methods* 14:607 | in-vitro (cell-free) | **over-calls** (no chromatin); most sensitive *candidate generator* |
| **CHANGE-seq** | Lazzarotto 2020 *Nat Biotechnol* 38:1317 | in-vitro | scalable CIRCLE-seq; same over-call caveat |
| Digenome-seq | Kim 2015 *Nat Methods* 12:237 | in-vitro (WGS) | unbiased but depth-limited, expensive |
| SITE-seq | Cameron 2017 *Nat Methods* 14:600 | in-vitro | concentration series ranks sensitivity |
| **GUIDE-seq** | Tsai 2015 *Nat Biotechnol* 33:187 | cell-based (dsODN tag) | physiological; **misses rare sites**, cell-type-specific, hard in primary/RNP |
| **DISCOVER-seq** | Wienert 2019 *Science* 364:286 | cell-based (MRE11 ChIP, in situ) | tag-free, works in vivo; depends on transient MRE11 occupancy |
| TTISS | Schmid-Burgk 2020 *Mol Cell* 78:794 | cell-based | high-throughput; benchmarks fidelity variants |

**The load-bearing reality:** in-vitro assays over-call (high sensitivity, low cellular specificity); cell-based assays under-call rare sites and are cell-type-dependent (K562 yields far more hits than HEK293 for the same guide). Cross-method discordance is *information*, not noise -- sites found by both are high-confidence; in-vitro-only sites are likely chromatin-protected. The defensible workflow is the **VIVO** logic (Akcakaya 2018): sensitive in-vitro generator -> cell-based assay in the relevant cell type -> amplicon validation.

## Decision Tree by Scenario

| Scenario | Recommended | Why |
|----------|-------------|-----|
| Research knockout / screen (some off-target tolerable) | CRISPOR or GuideScan2 to pick the most specific guide; Cas-OFFinder (<=4 mm + bulges) to eyeball top sites | in-silico is sufficient when being wrong is cheap |
| Choosing among candidate guides | rank by **aggregate CFD specificity** (compare guides, not absolute safety) | specificity is a separate axis from on-target activity (-> grna-design) |
| Human therapeutic guide | **variant-aware** CRISPRme vs gnomAD (+ patient genome), bulges on | a common ancestry-enriched SNP can create a real off-target (rs114518452 / BCL11A) |
| Therapeutic, choosing the nuclease | high-fidelity variant **in the delivery format actually used** | RNP -> HiFi Cas9 (R691A) or Sniper-Cas9; plasmid-tuned variants can lose their edge as RNP |
| Therapeutic validation | >=2 orthogonal empirical assays -> amplicon deep-seq with stated LoD -> structural readout | predicted != detected != validated; amplicons miss large deletions/translocations |
| Base/prime-editor off-targets | this skill covers **Cas-dependent** only | deaminase (Cas-independent) DNA/RNA off-targets -> base-editing-design / prime-editing-design |

## High-Fidelity Nucleases -- often a bigger lever than guide reselection

| Variant | Citation | Note |
|---------|----------|------|
| eSpCas9(1.1) | Slaymaker 2016 *Science* 351:84 | neutralizes non-target-strand contacts; characterized mostly as plasmid |
| SpCas9-HF1 | Kleinstiver 2016 *Nature* 529:490 | weakens 4 Cas9-DNA H-bonds; plasmid-characterized |
| HypaCas9 | Chen 2017 *Nature* 550:407 | conformational proofreading gate |
| evoCas9 | Casini 2018 *Nat Biotechnol* 36:265 | ~79x fidelity; ~90% residual on-target |
| **Sniper-Cas9** | Lee 2018 *Nat Commun* 9:3048 | high specificity **and works as RNP** |
| **HiFi Cas9 (R691A)** | Vakulskas 2018 *Nat Med* 24:1216 | single mutation; **the RNP-favored therapeutic variant** |

Two tacit points: (1) **delivery format matters** -- eSpCas9/HF1 can lose their fidelity advantage delivered as a high transient RNP bolus; HiFi Cas9 and Sniper-Cas9 stay specific and active as RNP. (2) **Fidelity has a guide-dependent on-target tax** -- a variant clean and active on guide A can be nearly dead on guide B. Pick the variant, then **test it on the target guide in the intended delivery format**; transferability is not assumable.

## Variant-Aware Screening (reference-only is a clinical liability)

A patient is not GRCh38. A common SNP can restore a PAM or remove the protective mismatch at a near-target site, *creating* an off-target that exists only in some individuals -- and because variant frequencies differ by ancestry, reference-only screening systematically misses off-targets common in under-represented populations. For a human therapeutic guide, an off-target check must expand from "checked off-targets" to "checked off-targets **variant-aware, across ancestries**" -- run CRISPRme against gnomAD (and the treated individual's genome).

## Enumerate Candidate Sites with Cas-OFFinder

**Goal:** Generate the genome-wide candidate-site list for one or more guides, including bulges and relaxed PAMs.

**Approach:** Write the Cas-OFFinder input file -- genome path, an optional DNA/RNA bulge line (v3.0.0+), a pattern with N's at guide positions and the PAM (use `NRG` to also catch NAG/NGG), then one query line per guide (guide bases + N's for the PAM positions, same length as the pattern) with its mismatch tolerance. Run on GPU if available. The output is a flat site list with mismatch counts -- it is a hypothesis set to score downstream, not a verdict.

```bash
# input.txt
# /path/to/genome_dir            # directory of FASTA (Cas-OFFinder indexes it)
# 2 2                            # DNA bulge, RNA bulge (omit this line for no-bulge search)
# NNNNNNNNNNNNNNNNNNNNNRG        # 20 N (guide) + NRG PAM -> also catches NAG
# GGCCGACCTGTCGCTGACGCNNN 4      # query: 20 guide bases + NNN (PAM positions), <=4 mismatches
cas-offinder input.txt G output.txt   # G=GPU, C=CPU, A=auto
```

## Score Candidates with the Published CFD Tables

**Goal:** Rank candidate sites by relative cleavage propensity and compute an aggregate guide-specificity score for comparing guides.

**Approach:** Do NOT hand-type the CFD matrix. Load the published Doench 2016 tables (`mismatch_score.pkl`, `pam_scores.pkl` -- they ship with CRISPOR and the Doench code), take the product of per-position mismatch penalties x the PAM penalty for each site, and aggregate as `100/(1 + sum(CFD))` with per-site CFDs on a 0-1 scale (the CRISPOR specificity formulation; equivalently `10000/(100 + 100*sum)`). Compare aggregate scores *among candidate guides*; never read an absolute CFD as a safety guarantee. (See `examples/off_target_analysis.py`.)

```python
import pickle

def load_cfd_tables(mismatch_pkl, pam_pkl):
    '''Load the published Doench 2016 CFD tables (distributed with CRISPOR) -- do not fabricate.'''
    with open(mismatch_pkl, 'rb') as f:
        mismatch = pickle.load(f)   # keys like 'rA:dG,3' -> penalty
    with open(pam_pkl, 'rb') as f:
        pam = pickle.load(f)        # keys like 'AG' -> penalty
    return mismatch, pam
```

## Structural Consequences Amplicon Panels Miss

Validating only with a short amplicon at each predicted site systematically misses the large-scale outcomes that are often the real safety concern:
- **Large deletions / complex rearrangements at the on-target** (Kosicki 2018 *Nat Biotechnol* 36:765) -- kilobase deletions whose alleles often drop out of the PCR, so the amplicon reads back *more wild-type than it is*.
- **Chromosomal translocations** between on- and off-target (or multiplexed) cuts -- need junction-capture (PEM-seq, UDiTaS, HTGTS, CAST-seq), not amplicon panels. A "clean" amplicon panel does **not** certify the absence of these.

## The Evidence Ladder & Limit of Detection

| Rung | Meaning | Method | Floor |
|------|---------|--------|-------|
| Predicted | sequence-similar candidate | Cas-OFFinder/CRISPOR/CRISPRme | n/a |
| Detected | nuclease acts there (unbiased) | GUIDE-/CIRCLE-/DISCOVER-/CHANGE-seq | assay-dependent |
| Validated | confirmed editing + allele frequency | targeted amplicon deep-seq (rhAmpSeq) + CRISPResso2 | ~0.1-0.5% (~0.1% with UMI/duplex) |

**"Not detected" means "below the LoD," never "zero."** State the LoD: 0.05% editing is irrelevant for a research knockout but is ~50,000 mis-edited cells in a 10^8-cell therapy.

## Per-Method Failure Modes

### "I ran Cas-OFFinder, so I checked my off-targets"
**Trigger:** treating an in-silico mismatch list as a verdict. **Mechanism:** the search sees sequence homology, not cellular cutting; bulges/chromatin/sub-LoD editing are invisible. **Symptom:** clean report, real off-targets later. **Fix:** in-silico chooses *which guide to try*; validate empirically when being wrong matters.

### Clean amplicon panel read as "safe"
**Trigger:** amplicon-seq only at predicted sites. **Mechanism:** large deletions drop out of PCR (Kosicki 2018); the panel can't discover sites the in-silico search missed. **Symptom:** falsely clean. **Fix:** feed the panel from an unbiased discovery assay; add a structural/translocation readout; state the LoD.

### One assay treated as ground truth
**Trigger:** "CIRCLE-seq is the gold standard." **Mechanism:** in-vitro over-calls, cell-based under-calls rare/cell-type-specific sites; they disagree by design. **Symptom:** over- or under-stated risk. **Fix:** triangulate (in-vitro generator + cell-based in the relevant cell type + validation).

### High-fidelity nuclease recommended without delivery context
**Trigger:** "use eSpCas9 for specificity." **Mechanism:** plasmid-tuned variants can lose the advantage as RNP; the on-target tax is guide-dependent. **Symptom:** lost activity or lost specificity. **Fix:** RNP -> HiFi Cas9/Sniper-Cas9; test the variant on the target guide in the intended format.

### Reference-only screen for a therapeutic guide
**Trigger:** searching GRCh38 only. **Mechanism:** ancestry-enriched SNPs create/destroy off-targets. **Symptom:** a real, population-specific off-target missed. **Fix:** CRISPRme vs gnomAD + the individual's genome.

### Bulge / non-canonical-PAM off-target missed
**Trigger:** mismatch-only search at NGG. **Mechanism:** the mismatch-count abstraction can't represent a 1 nt bulge or an NAG site. **Symptom:** assay finds an off-target the search "missed." **Fix:** enable bulges (Cas-OFFinder v3) and search a relaxed PAM (NRG).

## Quantitative Thresholds

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| Mismatch cutoff | <=4 typical (CRISPOR default); up to 6 for thorough | meaningful cutting rare beyond 4-5 mm, but bulges/variants rescue more-distant sites |
| Bulge size | up to ~2 (DNA + RNA) | real validated off-targets occur with 1-2 nt bulges |
| CFD per-site | relative ranker; attention >~0.1-0.2; high-risk near on-target | not a calibrated probability |
| Aggregate specificity (CRISPOR) | higher better; >~80 commonly "good" *for choosing guides* | research heuristic, NOT a clinical pass/fail |
| Amplicon LoD | ~0.1-0.5% (~0.1% with UMI/duplex) | below this, PCR/sequencer error dominates |
| High-fidelity on-target tax | guide- and format-dependent | always test the variant on the target guide |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| Cas-OFFinder returns nothing | wrong genome path / pattern-query length mismatch | query length must equal pattern length; check the genome dir/FASTA |
| CFD scores look fabricated/wrong | hand-typed matrix | load the published `mismatch_score.pkl`/`pam_scores.pkl` |
| Assay finds an off-target the search missed | mismatch-only, NGG-only search | enable bulges; search NRG |
| "No detectable off-targets" claimed as zero | LoD not stated | report the limit of detection; absence is bounded, not absolute |

## References

- Bae S, Park J, Kim JS (2014). Cas-OFFinder: a fast and versatile algorithm that searches for potential off-target sites of Cas9 RNA-guided endonucleases. *Bioinformatics* 30(10):1473-1475.
- Doench JG, Fusi N, Sullender M, et al. (2016). Optimized sgRNA design to maximize activity and minimize off-target effects of CRISPR-Cas9. *Nat Biotechnol* 34(2):184-191.
- Hsu PD, et al. (2013). DNA targeting specificity of RNA-guided Cas9 nucleases. *Nat Biotechnol* 31(9):827-832.
- Cancellieri S, et al. (2020). CRISPRitz: rapid, high-throughput and variant-aware in silico off-target site identification. *Bioinformatics* 36(7):2001-2008.
- Schmidt H, et al. (2025). Genome-wide CRISPR guide RNA design and specificity analysis with GuideScan2. *Genome Biol* 26:41.
- Abadi S, et al. (2017). A machine learning approach for predicting CRISPR-Cas9 cleavage efficiencies and patterns (CRISTA). *PLoS Comput Biol* 13(10):e1005807.
- Listgarten J, et al. (2018). Prediction of off-target activities for the end-to-end design of CRISPR guide RNAs (Elevation). *Nat Biomed Eng* 2(1):38-47.
- Concordet JP, Haeussler M (2018). CRISPOR: intuitive guide selection for CRISPR/Cas9 genome editing experiments and screens. *Nucleic Acids Res* 46(W1):W242-W245.
- Yan J, et al. (2020). Benchmarking and integrating genome-wide CRISPR off-target detection and prediction. *Nucleic Acids Res* 48(20):11370-11379.
- Tsai SQ, et al. (2015). GUIDE-seq enables genome-wide profiling of off-target cleavage by CRISPR-Cas nucleases. *Nat Biotechnol* 33(2):187-197.
- Kim D, et al. (2015). Digenome-seq: genome-wide profiling of CRISPR-Cas9 off-target effects in human cells. *Nat Methods* 12(3):237-243.
- Cameron P, et al. (2017). Mapping the genomic landscape of CRISPR-Cas9 cleavage (SITE-seq). *Nat Methods* 14(6):600-606.
- Tsai SQ, et al. (2017). CIRCLE-seq: a highly sensitive in vitro screen for genome-wide CRISPR-Cas9 nuclease off-targets. *Nat Methods* 14(6):607-614.
- Wienert B, et al. (2019). Unbiased detection of CRISPR off-targets in vivo using DISCOVER-seq. *Science* 364(6437):286-289.
- Lazzarotto CR, et al. (2020). CHANGE-seq reveals genetic and epigenetic effects on CRISPR-Cas9 genome-wide activity. *Nat Biotechnol* 38(11):1317-1327.
- Schmid-Burgk JL, et al. (2020). Highly Parallel Profiling of Cas9 Variant Specificity (TTISS). *Mol Cell* 78(4):794-800.e8.
- Akcakaya P, et al. (2018). In vivo CRISPR editing with no detectable genome-wide off-target mutations (VIVO). *Nature* 561:416-419.
- Scott DA, Zhang F (2017). Implications of human genetic variation in CRISPR-based therapeutic genome editing. *Nat Med* 23:1095-1101.
- Lessard S, et al. (2017). Human genetic variation alters CRISPR-Cas9 on- and off-targeting specificity at therapeutically implicated loci. *PNAS* 114(52):E11257-E11266.
- Cancellieri S, et al. (2023). Human genetic diversity alters off-target outcomes of therapeutic gene editing (CRISPRme). *Nat Genet* 55(1):34-43.
- Slaymaker IM, et al. (2016). Rationally engineered Cas9 nucleases with improved specificity (eSpCas9). *Science* 351(6268):84-88.
- Kleinstiver BP, et al. (2016). High-fidelity CRISPR-Cas9 nucleases with no detectable genome-wide off-target effects (SpCas9-HF1). *Nature* 529(7587):490-495.
- Chen JS, et al. (2017). Enhanced proofreading governs CRISPR-Cas9 targeting accuracy (HypaCas9). *Nature* 550(7676):407-410.
- Casini A, et al. (2018). A highly specific SpCas9 variant is identified by in vivo screening in yeast (evoCas9). *Nat Biotechnol* 36(3):265-271.
- Lee JK, et al. (2018). Directed evolution of CRISPR-Cas9 to increase its specificity (Sniper-Cas9). *Nat Commun* 9:3048.
- Vakulskas CA, et al. (2018). A high-fidelity Cas9 mutant delivered as a ribonucleoprotein complex enables efficient gene editing in human hematopoietic stem and progenitor cells (HiFi Cas9). *Nat Med* 24(8):1216-1224.
- Kosicki M, Tomberg K, Bradley A (2018). Repair of double-strand breaks induced by CRISPR-Cas9 leads to large deletions and complex rearrangements. *Nat Biotechnol* 36:765-771.
- Clement K, et al. (2019). CRISPResso2 provides accurate and rapid genome editing sequence analysis. *Nat Biotechnol* 37(3):224-226.

## Related Skills

- grna-design - Design and on-target-score guides before the specificity check (a separate axis)
- base-editing-design - Owns the deaminase (Cas-independent) DNA/RNA off-target classes
- prime-editing-design - pegRNA off-target considerations and PE3 nicking-guide specificity
- crispr-screens/crispresso-editing - Quantify and validate editing at candidate sites from amplicon reads
- variant-calling/variant-annotation - Annotate whether off-targets hit genes/pathogenic loci
- genome-intervals/bed-file-basics - Intersect off-target sites with exons/oncogenes for prioritization
- database-access/ncbi-datasets-cli - Download the reference genome for the search
<!-- END FILE: genome-engineering/off-target-prediction/SKILL.md -->

## 子目录：genome-engineering/prime-editing-design

<!-- BEGIN FILE: genome-engineering/prime-editing-design/SKILL.md -->
---
name: bio-genome-engineering-prime-editing-design
description: Designs pegRNAs and nicking guides for prime editing (PE) -- choosing the nick/strand, tuning the primer-binding site (PBS) and reverse-transcription template (RTT) as a per-locus panel, selecting the PE system (PE2/PE3/PE3b/PE4/PE5/PEmax/PE7), adding MMR-evading and PAM-disrupting silent edits, appending epegRNA 3' motifs (tevopreQ1/mpknot), and ranking with PRIDICT/DeepPrime. Covers twinPE/PASTE for large insertions and the prime-vs-base-editing decision. Use when designing a scarless point mutation, small insertion/deletion, or any of the 12 base conversions without a double-strand break, when efficiency is low and MMR inhibition or pegRNA stabilization is needed, or when routing a large insertion to an integrase method. Generic guide scoring and base editing are separate skills.
tool_type: mixed
primary_tool: PrimeDesign
---

## Version Compatibility

Reference examples tested with: BioPython 1.83+, PrimeDesign 1.2+ (Docker), PRIDICT2.0 (web/code).

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed package and adapt the example to match the actual API rather than retrying.

PrimeDesign is Docker-only (no pip) and takes the edit inline in a single string with exact parenthesis notation (below) -- the most-hallucinated thing in PE tooling; verify it against the repo, never reconstruct from memory. Outcome-prediction models are trained mostly on HEK293T + small edits (<=3 bp); their scores are priors, not measurements, and degrade off-distribution. The PE *system* (MMR status, expressed vs synthetic pegRNA) drives efficiency more than any oligo tweak.

# Prime Editing Design

**"Install a precise small edit without a double-strand break"** -> Establish the edit, cell type, MMR status, and delivery; choose the nick position/strand; design a *panel* of PBS x RTT combinations; pick the PE system; add the free wins (PAM-disrupting + MMR-evading silent edits, a 3' motif); rank with a model; and test.
- CLI (Docker): `PrimeDesign` generates ranked pegRNA + nicking-guide components from a reference + edit string
- Python: assemble/sweep PBS x RTT panels with `Bio.Seq`; enforce the don't-end-on-C and 5'-G rules
- Web/code: PRIDICT2.0 / DeepPrime rank candidates by intended-edit and indel rate

## The Single Most Important Modern Insight -- there is no universal PBS/RTT optimum, and the *system* choice carries the order of magnitude

Two reframes:

1. **PBS and RTT length are parameters to optimize per locus, not constants to look up.** The PBS x RTT optimum is locus-specific -- it depends on local GC (which sets the PBS annealing Tm), the edit, the nick-to-edit distance, and chromatin. A high-GC target wants a *short* PBS; a low-GC target a *long* one; the "13/15" that is perfect at one locus is useless 200 bp away. A hard-coded default produces a sequence that *looks* valid, so nothing flags it until the data come back at 2%. The correct deliverable is **a ranked panel** (a few PBS x a few RTT x the viable nicks), tested or model-ranked -- emitting a single pegRNA is the tell of someone who has never run PE.

2. **Prime editing efficiency is a cellular-genetics problem, not just oligo design.** The cell's mismatch repair (MMR; MutSalpha/MutLalpha) detects the edit:original heteroduplex and excises the *edited* strand, reverting it and spawning indels. The biggest post-2019 jump was not a better PBS -- it was **inhibiting MMR (MLH1dn -> PE4/PE5, ~7.7x average)**. The second was **stopping the pegRNA 3' end from being degraded** (epegRNA motifs; PE7's La protein). Design now means choosing the *system* (PE2 vs PE3b vs PE5max+epegRNA vs PE7) as much as the sequence. First branch: what edit, what cell type, MMR-proficient or not, expressed or synthetic.

## Mechanism (the design rules fall out of it)

The prime editor (Anzalone 2019) is **Cas9 H840A nickase + engineered M-MLV reverse transcriptase**, programmed by a **pegRNA** = sgRNA (spacer + scaffold) with a 3' extension read 5'->3' as **[RTT][PBS]**. (1) The nickase cuts the protospacer (PAM) strand ~3 nt 5' of the PAM, exposing a free 3'-OH. (2) The **PBS** anneals to that nicked 3' end (the genomic strand becomes the primer). (3) The RT extends through the **RTT**, synthesizing a new 3' DNA flap that *encodes the edit*. (4) FEN1-type nucleases preferentially excise the unedited 5' flap, favoring incorporation of the edited 3' flap; ligation seals it. (5) The resulting heteroduplex is resolved by MMR -- which preferentially reverts the edit (hence the MMR section below). Consequences: PBS length is tuned by annealing Tm; **RTT length = nick-to-edit distance + edit + 3' homology tail (~10-16 nt)**; efficiency falls as the edit moves farther from the nick; the edit must lie within the RTT.

## The PE System Stack -- orthogonal axes, not a "bigger number is better" ranking

| System | Adds over previous | Acts on | Cite |
|--------|--------------------|---------|------|
| PE1 | Cas9 H840A + **wild-type** M-MLV RT | proof of concept | Anzalone 2019 |
| **PE2** | **engineered M-MLV RT** (pentamutant) | the workhorse enzyme | Anzalone 2019 |
| PE3 | + second **nicking sgRNA** on the non-edited strand (~1.5-4x) | flap resolution / MMR strand bias -- **but raises indels** (transient near-DSB) | Anzalone 2019 |
| **PE3b** | PE3 ngRNA matching only the **edited** sequence -> nick fires *after* the edit | near-eliminates PE3's indels; **only possible when the edit makes/breaks a protospacer** | Anzalone 2019 |
| PE4 | PE2 + **MLH1dn** (dominant-negative MMR) (~7.7x avg) | MMR globally | Chen 2021 |
| PE5 | PE3 + MLH1dn | second nick + MMR | Chen 2021 |
| **PEmax** | optimized protein (codon, NLS, R221K/N394K, linker); +MLH1dn = **PE4max/PE5max** | the protein | Chen 2021 |
| PE7 | PEmax-family + **La-protein** RBD capping the pegRNA 3' end | pegRNA stability | Yan 2024 |

The expert move is to reason about which axis the problem needs: low efficiency in an MMR-active cell -> add MLH1dn; too many indels -> drop to PE2 or design **PE3b** (not PE3); short pegRNA half-life -> epegRNA/PE7. Note: in **MMR-deficient lines** (HCT116, many tumor lines) PE2 already behaves like PE4, so MLH1dn adds nothing -- benchmark numbers from such lines overstate the gain in MMR-proficient primary cells. **PE5max + epegRNA is the modern default workhorse** for hard, MMR-active contexts.

## pegRNA Parameters & the Free Wins

- **PBS (~8-17 nt; start ~11-15):** tune to annealing Tm/GC, not a fixed length. pegFinder's starting heuristic is PBS ~= 24 - (GC%/5), clamped 8-17; test a small ladder (e.g. 10/13/15/17).
- **RTT:** = nick-to-edit + edit + ~10-16 nt 3' homology. Shorter RTT is usually more efficient -- use the shortest that spans the edit with adequate homology, then test a couple.
- **Don't end the synthesized flap on a C** (a C at the +1 templated position lowers efficiency; PrimeDesign exposes `--filter_c1_extension`).
- **5' G for U6:** prepend a G if the spacer lacks one -- **prepend, do not replace** the first base (replacing creates a spacer:target mismatch).
- **PAM-disrupting silent edit (free win):** if the edit (or an added silent change) destroys the protospacer/PAM, the editor cannot re-nick the edited strand -> fewer indels, and the change doubles as an MMR-evading mismatch. Always check whether the edit can be routed to disrupt the PAM.
- **MMR-evading bystander edits (free win):** add 1-2 *silent* substitutions next to the intended edit to make a >=3-bp edited "bubble" that MMR recognizes less efficiently -> higher correct-edit yield. Trivial in coding sequence (synonymous codons); the tactic of choice before reaching for MLH1dn.

## epegRNA 3' Motifs & pegRNA Stability

The pegRNA 3' extension (RTT+PBS) is single-stranded RNA that is **exonucleolytically degraded** before it can prime RT -- an invisible failure (the molecule is made, just chewed back). **epegRNAs** append a structured pseudoknot motif to the 3' end (Nelson 2022): use **tevopreQ1** by default (~3-4x gain, no added off-target); **mpknot** is larger and benefits most from a **pegLIT**-designed linker (tevopreQ1/evopreQ1 often work linker-free). **PE7** (La protein) attacks the same degradation from the protein side and is **partly redundant** with epegRNAs (PE7's gains are largest with plain pegRNAs) -- don't stack them as if independent. For synthetic (non-expressed) pegRNAs where a folded motif is awkward, PE7 / La-optimized 3' chemistry is the lever instead.

## Outcome Prediction (rank, but still test)

| Model | Predicts | Cite |
|-------|----------|------|
| **PRIDICT / PRIDICT2.0** | intended-edit + unintended (indel) rate; 2.0 is chromatin-aware across lines | Mathis 2023 *Nat Biotechnol* 41:1151; Mathis 2025 *Nat Biotechnol* 43:712 |
| **DeepPrime / DeepPrime-FT** | efficiency across 8 PE systems x 7 cell types, edits <=3 bp | Yu 2023 *Cell* 186:2256 |
| Easy-Prime | XGBoost pegRNA design with RNA-structure features | Li 2021 *Genome Biol* 22:235 |

Limits: trained mostly on HEK293T + small edits; scores degrade for large edits, untrained cell types, primary/iPS cells, and in vivo loci. A high score says "worth synthesizing," not "will work in the target cell." Report **edit:indel purity, not efficiency alone** (PE3's indel liability hides when only the intended-edit rate is reported).

## Large / Advanced Edits (single-pegRNA PE runs out of room)

| Strategy | Mechanism | Size | Cite |
|----------|-----------|------|------|
| **twinPE** | two pegRNAs template complementary flaps -> replacement/deletion/inversion | up to ~hundreds bp; +recombinase -> kb | Anzalone 2022 *Nat Biotechnol* 40:731 |
| GRAND editing | dual pegRNAs, RTTs complementary to each other (non-genomic) -> template-free insertion | up to a few hundred bp (drops sharply >~400 bp) | Wang 2022 |
| **PASTE** | PE writes a serine-integrase attB site, integrase drops in a donor | **~10-36 kb**, DSB-free | Yarnall 2023 *Nat Biotechnol* 41:500 |

Route "knock in a 2 kb reporter" to twinPE+integrase/PASTE (or HDR/HITI) -- a single giant-RTT pegRNA is a category error.

## Decision Tree by Scenario

| Scenario | Recommended | Why |
|----------|-------------|-----|
| C->T / G->A or A->G / T->C transition, base positionable in a window | -> base-editing-design | BE is higher-efficiency, cleaner, no flap/MMR competition for its transition |
| Any of the other small edits (other transversions, small indels, combined) | prime editing, panel of PBS x RTT | PE owns the precise-small-edit-without-a-DSB box |
| Low efficiency in an MMR-proficient cell | PE4/PE5 (MLH1dn) + MMR-evading silent edits | MMR is the dominant barrier |
| Indels unacceptable (therapeutic) | PE2 or **PE3b** (not PE3) | PE3's second nick raises indels |
| Expressed pegRNA | add a tevopreQ1 3' motif (PE5max+epegRNA default) | fixes invisible 3'-degradation |
| Large insertion (genes/tags, >~hundreds bp) | -> twinPE+integrase / PASTE / hdr-template-design | beyond single-pegRNA flap capacity |
| Knockout only (any frameshift) | -> grna-design (plain Cas9) | PE's precision is wasted; nuclease is simpler/more efficient |
| Validate edits | -> crispr-screens/crispresso-editing | quantify intended-edit and indel rates from amplicons |

## Generate Designs with PrimeDesign (verified notation)

**Goal:** Produce ranked pegRNA + nicking-guide candidates for a precise edit.

**Approach:** Encode the reference and edit in ONE inline string with PrimeDesign's exact parenthesis notation, then run the Docker CLI; it sweeps PBS/RTT, ranks pegRNAs (PAM-disrupted preferred), and nominates ngRNAs. Do not hand-roll the design as the only step.

```bash
# PrimeDesign edit-string notation (verify against the repo README; the most-hallucinated PE detail):
#   substitution:  ...AAACG(T/A)CTTCC...        # ref/edit, slash-separated
#   insertion:     ...AAACGT(+CTT)CTTCC...      # bare leading + (also (/CTT))
#   deletion:      ...AAAAC(-GTCT)TCCAAT...     # bare leading - (also (GTCT/))
#   combinatorial: GCCTGTGACTAACTGC(G/T)CCA(+ATCG)AAACGTC(-TTCC)AATCCCCTTATCCAATTTA
docker run -v ${PWD}/:/DATA -w /DATA pinellolab/primedesign primedesign_cli \
  -f edits.csv -pbs 10 12 14 -rtt 10 16 22 -nick_dist_min 0 -nick_dist_max 100 -out designs/
```

## Sweep a PBS x RTT Panel and Enforce the Hard Rules

**Goal:** Build a small, ordered panel of pegRNA extensions for one nick, applying the don't-end-on-C and 5'-G rules.

**Approach:** For each PBS length, take the reverse complement of the genomic sequence 5' of the nick; for each RTT length, build the edited 3' flap and reject extensions whose first templated base is C. Rank the panel by a model (PRIDICT/DeepPrime) for synthesis. (See `examples/prime_editing_design.py`.)

```python
from Bio.Seq import Seq

def prepend_u6_g(spacer):
    return spacer if spacer.startswith('G') else 'G' + spacer   # prepend, never replace
```

## Per-Method Failure Modes

### One pegRNA from a fixed PBS=13/RTT=15
**Trigger:** treating PBS/RTT as constants. **Mechanism:** the optimum is locus-specific (GC/Tm/nick distance/chromatin). **Symptom:** valid-looking pegRNA, ~2% editing. **Fix:** design and test a PBS x RTT panel; rank with PRIDICT2.0/DeepPrime.

### Designed for the edit, ignored the repair machinery
**Trigger:** installing only the literal intended base. **Mechanism:** MMR reverts the edit; an intact PAM lets the editor re-nick. **Symptom:** low yield + indels. **Fix:** add a PAM-disrupting silent edit and 1-2 MMR-evading silent edits; use PE4/PE5 (MLH1dn) in MMR-active cells.

### Reached for PE3 when PE3b was available
**Trigger:** reading the ladder as a scalar. **Mechanism:** PE3's second nick is a transient near-DSB. **Symptom:** good efficiency, unacceptable indels. **Fix:** if the edit makes/breaks a protospacer, design PE3b; otherwise drop to PE2/PE4.

### Reported % editing without % indels
**Trigger:** efficiency-only readout. **Mechanism:** PE yields a mix (edit/unedited/indel). **Symptom:** a "40%" pegRNA that throws 15% indels looks fine. **Fix:** report edit:indel purity (PRIDICT predicts both).

### Trusted a model score off-distribution / forgot the locus
**Trigger:** picking the top-scored pegRNA, skipping the panel, in a non-HEK293T context. **Mechanism:** models are trained on HEK293T + small edits; chromatin dominates and is invisible to sequence. **Symptom:** "designed perfectly, didn't work." **Fix:** weight the model less far from training; still test; a closed locus may sink any design.

### 5' G replaced, or flap ends on C, or large insert forced into one pegRNA
**Trigger:** `'G'+spacer[1:]`; RTT ending on C; 2 kb into one RTT. **Mechanism:** spacer:target mismatch; +1-C re-incorporation; flap can't template/resolve. **Fix:** prepend the G; shift RTT off a terminal C; route large inserts to twinPE/PASTE.

## Quantitative Thresholds

| Parameter | Value | Source |
|-----------|-------|--------|
| PBS length | ~8-17 nt, tuned to Tm/GC (start ~24-GC%/5) | Anzalone 2019; pegFinder heuristic |
| RTT | edit + ~10-16 nt 3' homology; shortest workable | Anzalone 2019 |
| Nick-to-edit | as small as possible; efficiency falls with distance | Anzalone 2019 |
| PE3 ngRNA distance | ~40-100 bp (sweet spot ~50-90), non-edited strand | Anzalone 2019 |
| Flap +1 base | not C | Anzalone 2019 / PrimeDesign `--filter_c1_extension` |
| MMR inhibition gain | ~7.7x avg (MMR-proficient cells only) | Chen 2021 |
| epegRNA 3' motif | tevopreQ1 default; ~3-4x | Nelson 2022 |
| Deliverable | a ranked panel, report edit:indel purity | field practice |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| Editing ~2% despite a "perfect" pegRNA | fixed PBS/RTT, unfavorable locus | test a panel; consider MLH1dn/epegRNA; the locus may be closed |
| High indels with PE3 | second nick on non-edited strand | use PE3b (if the edit makes/breaks a protospacer) or PE2 |
| PrimeDesign mis-encodes the edit | wrong inline notation | use exact `(ref/edit)`/`(+ins)`/`(-del)`; verify against the repo |
| No benefit from MLH1dn | MMR-deficient cell line | PE2 already behaves like PE4 there |

## References

- Anzalone AV, Randolph PB, Davis JR, et al. (2019). Search-and-replace genome editing without double-strand breaks or donor DNA. *Nature* 576(7785):149-157.
- Chen PJ, Hussmann JA, Yan J, et al. (2021). Enhanced prime editing systems by manipulating cellular determinants of editing outcomes. *Cell* 184(22):5635-5652.
- Nelson JW, Randolph PB, Shen SP, et al. (2022). Engineered pegRNAs improve prime editing efficiency. *Nat Biotechnol* 40(3):402-410.
- Yan J, Oyler-Castrillo P, Ravisankar P, et al. (2024). Improving prime editing with an endogenous small RNA-binding protein. *Nature* 628(8008):639-647.
- Anzalone AV, Gao XD, Podracky CJ, et al. (2022). Programmable deletion, replacement, integration and inversion of large DNA sequences with twin prime editing. *Nat Biotechnol* 40(5):731-740.
- Yarnall MTN, Ioannidi EI, Schmitt-Ulms C, et al. (2023). Drag-and-drop genome insertion of large sequences without double-strand DNA cleavage using CRISPR-directed integrases (PASTE). *Nat Biotechnol* 41(4):500-512.
- Hsu JY, Grunewald J, Szalay R, et al. (2021). PrimeDesign software for rapid and simplified design of prime editing guide RNAs. *Nat Commun* 12:1034.
- Chow RD, Chen JS, Shen J, Chen S (2021). A web tool for the design of prime-editing guide RNAs (pegFinder). *Nat Biomed Eng* 5(2):190-194.
- Mathis N, Allam A, Kissling L, et al. (2023). Predicting prime editing efficiency and product purity by deep learning (PRIDICT). *Nat Biotechnol* 41(8):1151-1159.
- Mathis N, Allam A, Talas A, et al. (2025). Machine learning prediction of prime editing efficiency across diverse chromatin contexts (PRIDICT2.0). *Nat Biotechnol* 43(5):712-719.
- Yu G, Kim HK, Park J, et al. (2023). Prediction of efficiencies for diverse prime editing systems in multiple cell types (DeepPrime). *Cell* 186(10):2256-2272.
- Li Y, Chen J, Tsai SQ, Cheng Y (2021). Easy-Prime: a machine learning-based prime editor design tool. *Genome Biol* 22:235.

## Related Skills

- base-editing-design - Preferred for the single transition a base editor can make
- grna-design - Generic spacer scoring; plain-nuclease knockout when precision is unneeded
- off-target-prediction - pegRNA spacer and PE3 nicking-guide off-target considerations
- hdr-template-design - Large-insertion alternative (HDR/HITI) when PASTE/twinPE is not used
- crispr-screens/prime-editing-screens - Pooled prime-editing screen analysis
- crispr-screens/crispresso-editing - Quantify intended-edit vs indel rates from amplicons
- variant-calling/variant-annotation - Identify the pathogenic variant to correct or install
<!-- END FILE: genome-engineering/prime-editing-design/SKILL.md -->

<!-- END CATEGORY: genome-engineering -->

