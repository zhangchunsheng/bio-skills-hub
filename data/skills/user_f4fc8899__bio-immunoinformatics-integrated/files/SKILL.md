---
slug: bio-immunoinformatics-integrated
version: 1.0.1
displayName: "免疫信息学 / Immunoinformatics"
name: bio-immunoinformatics-integrated
summary: "中文：免疫信息学综合技能，整合 6 个相关专题，覆盖免疫信息学：MHC结合预测、neoantigen识别、表位预测、TCR特异性注释。 English: Integrated Immunoinformatics skill covering 6 related topics, including Immunoinformatics: MHC class I/II binding prediction, neoantigen identification, epitope prediction, TCR specificity annotation."
description: "中文：这是一个面向免疫信息学的综合生物信息学 Skill，整合当前分类下 6 个相关专题能力。它用于根据研究问题、数据类型和分析阶段，选择合适的方法与工具，规划从输入检查、预处理、核心分析到质量控制、统计解释和结果报告的完整流程。重点覆盖：免疫信息学：MHC结合预测、neoantigen识别、表位预测、TCR特异性注释。当用户提供相关实验数据、测序结果、表格或研究问题时，它会帮助判断分析目标与前置条件，给出工具选择、关键参数、输入输出、常见失败原因、结果解读和可复现建议。主要工具包括：BepiPred, NeoFox, NetMHCIIpan。该 Skill 提供分析设计与实施指导，不替代对具体数据质量、生物学背景和最终结论的人工审查。 English: This is an integrated bioinformatics Skill for Immunoinformatics, combining 6 related topic areas. It helps users choose appropriate methods and tools based on the research question, data type, and analysis stage, and plan an end-to-end workflow from input validation and preprocessing through core analysis, quality control, statistical interpretation, and reporting. It covers Immunoinformatics: MHC class I/II binding prediction, neoantigen identification, epitope prediction, TCR specificity annotation. For relevant experimental data, sequencing results, tables, or research questions, it clarifies prerequisites, recommends tools and parameters, describes expected inputs and outputs, explains common failure modes, and supports reproducible analysis. Primary tools include: BepiPred, NeoFox, NetMHCIIpan. It provides methodological and implementation guidance; final data-quality assessment and biological conclusions still require human review."
---

# immunoinformatics 分类 Skill 整合版

> 本文件整合同一主分类目录下 6 个子目录中的 SKILL.md 内容。
> 各子目录正文按原文保留，并通过标题和边界标记进行区分；源文件中的元数据块未被改写。

---

<!-- BEGIN CATEGORY: immunoinformatics -->

## 子目录：immunoinformatics/epitope-prediction

<!-- BEGIN FILE: immunoinformatics/epitope-prediction/SKILL.md -->
---
name: bio-immunoinformatics-epitope-prediction
description: Predict B-cell and T-cell epitopes for vaccine antigen design and epitope mapping with BepiPred-3.0, DiscoTope-3.0, the IEDB tools, and EL-mode MHC presentation. Encodes the load-bearing asymmetry that T-cell epitope prediction is mature (it reduces to MHC presentation, AUC>0.9) while B-cell prediction is unreliable (linear predictors ~AUC 0.6 because ~90% of real epitopes are conformational) — so structure-based DiscoTope-3.0 on AlphaFold models is the only defensible B-cell path, propensity scales are obsolete, and NetChop is largely redundant on EL-trained models. Use when mapping epitopes or selecting vaccine antigens. MHC binding lives in mhc-binding-prediction.
tool_type: python
primary_tool: BepiPred
---

## Version Compatibility

Reference examples tested with: BepiPred-3.0, pandas 2.2+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

Notes specific to this skill: BepiPred-3.0 ships as the `bepipred3` package and auto-downloads ESM-2 weights on first run; its default threshold is 0.1512 (NOT 0.5). DiscoTope-3.0, ElliPro, SEPPA, NetChop, and NetCTLpan are standalone/web (IEDB or DTU). The IEDB classic and next-generation REST APIs wrap most predictors. Re-verify thresholds and the supported-method list against current docs.

# Epitope Prediction

**"Predict the B-cell and T-cell epitopes in my antigen"** -> Identify antibody-binding (B-cell) and MHC-presented (T-cell) immunogenic regions, with appropriately different confidence for each.
- Python: `bepipred3` for linear B-cell epitopes; IEDB REST API for B-cell/T-cell tools
- CLI/web: DiscoTope-3.0 for conformational B-cell epitopes (structure-based); NetMHCpan/MHCflurry (EL) for T-cell epitopes

## The Single Most Important Modern Insight -- "epitope prediction" is two fields at different maturity, wrongly conflated

T-cell epitope prediction is mature and trustworthy because it reduces to MHC binding/presentation — a sharply constrained problem (a peptide fits the groove or it does not) with an enormous mass-spec eluted-ligand training corpus; NetMHCpan-4.1 and MHCflurry routinely exceed AUC 0.9 for class I. B-cell epitope prediction is unreliable: linear sequence-based predictors land around AUC 0.6, and even the ESM-2-based BepiPred-3.0 falls to AUC 0.663 on the real IEDB external test set. This is structural, not a tuning problem the next network will fix: ~90% of natural B-cell epitopes are conformational/discontinuous — residues clustered in 3D but far apart in sequence — which a sequence-only model is by construction blind to. The single most damaging mistake in this domain is letting the well-deserved confidence in MHC/T-cell prediction leak into unwarranted confidence in B-cell prediction. Write down which problem is being solved before running anything.

## Tool Taxonomy

| Tool | Citation | Target | Input | When |
|------|----------|--------|-------|------|
| NetMHCpan-4.1 EL / MHCflurry | Reynisson 2020; O'Donnell 2020 | T-cell (MHC-I presentation) | sequence + HLA | Default T-cell path; EL encodes processing |
| NetMHCIIpan / NetCTLpan | Nilsson 2023; Stranzl 2010 | T-cell (CD4 / integrated CTL) | sequence + HLA | CD4 epitopes; integrated cleavage+TAP+MHC |
| DiscoTope-3.0 | Høie 2024 | B-cell (conformational) | 3D structure (AlphaFold OK) | The only defensible B-cell method when a structure exists |
| BepiPred-3.0 | Clifford 2022 | B-cell (linear) | sequence | Linear/denatured-target reagents; misses ~90% native |
| ElliPro / SEPPA 3.0 | Ponomarenko 2008; Zhou 2019 | B-cell (conformational) | 3D structure | Fast geometric baseline; SEPPA for glycoproteins |
| Propensity scales | Kolaskar 1990 etc. | B-cell (linear) | sequence | Obsolete; decoration, not data |

## Decision Tree by Scenario

| Scenario | Recommended | Why |
|----------|-------------|-----|
| T-cell (CD8) epitopes | NetMHCpan-4.1 EL / MHCflurry | Mature; defer to mhc-binding-prediction |
| T-cell (CD4) epitopes | NetMHCIIpan-4.3 | Defer to mhc-class-ii-prediction; less reliable |
| B-cell, structure available or foldable | DiscoTope-3.0 on AlphaFold model | Conformational; ~no penalty for predicted structures |
| B-cell glycoprotein (Env/S/HA) | SEPPA 3.0 | Models glycan shielding |
| B-cell, sequence only, peptide/denatured target | BepiPred-3.0 (linear/top-X%) | Legitimate narrow use; state the conformational caveat |
| B-cell, sequence only, native antibody response | Fold a structure first, then DiscoTope-3.0 | Linear prediction structurally cannot see native epitopes |
| Broadly-protective vaccine | + conservation + HLA population coverage | A high-scoring epitope in a hypervariable loop is worthless |

## Predict Linear B-Cell Epitopes (BepiPred-3.0)

**Goal:** Score per-residue linear B-cell epitope probability from sequence, for a linear/denatured-target use case.

**Approach:** Run the `bepipred3` CLI (or package) on a FASTA; it emits per-residue probabilities, a binary FASTA (upper = epitope), and top-X% selections. Use the default threshold 0.1512 or the top-X% mode; treat output as a hypothesis that misses most native conformational epitopes.

```bash
# bepipred3 auto-downloads ESM-2 weights on first run; default threshold 0.1512 (NOT 0.5)
python bepipred3_CLI.py -i antigen.fasta -o bp3_out/ -pred vt_pred -t 0.1512
# or select the top 20% scoring residues per sequence instead of a fixed cutoff:
python bepipred3_CLI.py -i antigen.fasta -o bp3_out/ -pred vt_pred -top 20
```

## Predict Conformational B-Cell Epitopes (DiscoTope-3.0)

**Goal:** Identify antibody-accessible surface patches from a 3D structure (the defensible B-cell path).

**Approach:** Provide a single antigen chain (experimental or AlphaFold). DiscoTope-3.0 scores per-residue conformational propensity and was trained on predicted structures, so AF2 models incur essentially no penalty (AUC 0.799 vs 0.807). Gate trust by pLDDT — accuracy drops ~5 percentile points per 10-point pLDDT decrease — and remember AUC-PR is only ~0.22 (low precision, many false positives).

```python
def gate_discotope_by_plddt(df, plddt_col='pLDDT', score_col='DiscoTope-3.0 score', min_plddt=70):
    '''Keep DiscoTope-3.0 calls only in confidently-folded regions; low-pLDDT loops
    (where antibodies often bind) are exactly where structure-based calls are least
    reliable. df: per-residue DiscoTope-3.0 output joined with model pLDDT.'''
    return df[df[plddt_col] >= min_plddt].sort_values(score_col, ascending=False)
```

## T-Cell Epitopes Reduce to MHC Presentation

**Goal:** Nominate CD8/CD4 epitopes from an antigen.

**Approach:** Tile the antigen and score with EL-mode MHC presentation (class I: mhc-binding-prediction; class II: mhc-class-ii-prediction). Do NOT add NetChop by default — EL models are trained on eluted ligands that already survived proteasomal cleavage and TAP, so the processing signal is implicit; explicit cleavage prediction is largely redundant and can double-penalize. Reserve NetChop/NetCTLpan for long source proteins as a cleavage sanity check or alleles lacking EL coverage.

## Per-Method Failure Modes

### Linear predictor used for native antibody response
**Trigger:** running BepiPred on a folded viral spike to predict neutralizing epitopes. **Mechanism:** native epitopes are conformational; sequence models cannot see them. **Symptom:** "predicted epitopes" that no native antibody targets. **Fix:** fold a structure and use DiscoTope-3.0; reserve linear predictors for peptide/denatured targets.

### Predicting epitopes of a wrong model
**Trigger:** DiscoTope on a low-confidence AlphaFold surface loop or a monomer of an oligomeric antigen. **Mechanism:** a subtly wrong surface moves the predicted epitope; an oligomer interface looks exposed in the monomer. **Symptom:** false-positive epitopes at buried/flexible sites. **Fix:** gate by pLDDT; model the biological assembly when the antigen oligomerizes.

### Propensity-scale cargo cult
**Trigger:** reporting Kolaskar-Tongaonkar/Parker/Emini "antigenic regions" as data. **Mechanism:** these are coarse 1980s physicochemical descriptors at/near random. **Symptom:** confident-looking but uninformative B-cell calls. **Fix:** treat as obsolete decoration; everything they encode is subsumed by BepiPred/structure methods.

### Confusing presentation with immunodominance
**Trigger:** ranking vaccine epitopes purely by binding/presentation score. **Mechanism:** immunodominance depends on repertoire, competition, processing kinetics, immune history — none modeled. **Symptom:** a strong predicted binder that is subdominant or ignored in vivo. **Fix:** treat presentation as necessary-not-sufficient; validate by ELISpot/tetramer.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| BepiPred-3.0 default 0.1512 | Clifford 2022 | Balances sens/spec on their benchmark; NOT 0.5 |
| Linear B-cell AUC ~0.6 | Field benchmarks | Barely above random; report as hypothesis |
| DiscoTope-3.0 AUC-ROC ~0.80, AUC-PR ~0.22 | Høie 2024 | Moderate ranking, low precision (minority class) |
| pLDDT >= 70 to trust DiscoTope calls | Høie 2024 | ~5 percentile-point drop per 10-point pLDDT loss |
| ~90% of B-cell epitopes conformational | B-cell literature | Why sequence-only prediction has a low ceiling |
| Skip NetChop on EL-mode predictions | Reynisson 2020 | EL training already encodes cleavage/TAP |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| Over-trusting B-cell predictions | Conflated with mature T-cell prediction | State the maturity asymmetry; treat B-cell as hypothesis |
| Few/no BepiPred epitopes | Applied 0.5 threshold | Use default 0.1512 or top-X% mode |
| False epitopes in flexible loops | Low-pLDDT AlphaFold model | Gate by pLDDT; assess model quality |
| Epitope worthless across strains | No conservation analysis | Add IEDB Epitope Conservancy + MSA |
| Redundant/over-penalized T-cell calls | NetChop stacked on EL model | Use EL presentation as the primary filter |
| Vaccine "designed" in silico | Over-trusting reverse-vaccinology scores | Treat VaxiJen/Vaxign as candidate funnels; validate experimentally |

## References

- Clifford JN, Høie MH, Deleuran S, Peters B, Nielsen M, Marcatili P. 2022. BepiPred-3.0: improved B-cell epitope prediction using protein language models. *Protein Science* 31(12):e4497.
- Høie MH, Gade FS, Johansen JM, et al. 2024. DiscoTope-3.0: improved B-cell epitope prediction using inverse folding latent representations. *Frontiers in Immunology* 15:1322712.
- Jespersen MC, Peters B, Nielsen M, Marcatili P. 2017. BepiPred-2.0: improving sequence-based B-cell epitope prediction using conformational epitopes. *Nucleic Acids Research* 45(W1):W24-W29.
- Kringelum JV, Lundegaard C, Lund O, Nielsen M. 2012. Reliable B cell epitope predictions: impacts of method development and improved benchmarking (DiscoTope-2.0). *PLoS Computational Biology* 8(12):e1002829.
- Ponomarenko J, Bui HH, Li W, et al. 2008. ElliPro: a new structure-based tool for the prediction of antibody epitopes. *BMC Bioinformatics* 9:514.
- Stranzl T, Larsen MV, Lundegaard C, Nielsen M. 2010. NetCTLpan: pan-specific MHC class I pathway epitope predictions. *Immunogenetics* 62(6):357-368.
- Reynisson B, Alvarez B, Paul S, Peters B, Nielsen M. 2020. NetMHCpan-4.1 and NetMHCIIpan-4.0. *Nucleic Acids Research* 48(W1):W449-W454.
- Calis JJA, Maybeno M, Greenbaum JA, et al. 2013. Properties of MHC class I presented peptides that enhance immunogenicity. *PLoS Computational Biology* 9(10):e1003266.
- Bui HH, Sidney J, Li W, Fusseder N, Sette A. 2007. Development of an epitope conservancy analysis tool. *BMC Bioinformatics* 8:361.

## Related Skills

- immunoinformatics/mhc-binding-prediction - T-cell (CD8) epitope prediction reduces to class I presentation
- immunoinformatics/mhc-class-ii-prediction - T-cell (CD4) epitopes; the class II presentation regime
- immunoinformatics/immunogenicity-scoring - ranking epitope candidates by likely T-cell response
- structural-biology/alphafold-predictions - fold an antigen with AlphaFold to enable DiscoTope-3.0
- database-access/entrez-fetch - retrieve antigen sequences/structures for epitope mapping
<!-- END FILE: immunoinformatics/epitope-prediction/SKILL.md -->

## 子目录：immunoinformatics/immunogenicity-scoring

<!-- BEGIN FILE: immunoinformatics/immunogenicity-scoring/SKILL.md -->
---
name: bio-immunoinformatics-immunogenicity-scoring
description: Rank and prioritize neoantigen/epitope candidates by likely T-cell response using NeoFox feature annotation, PRIME2.0, BigMHC-IM, the Łuksza/Balachandran fitness model (agretopicity + foreignness), and pVACtools tiering. Encodes the field's hard truths that immunogenicity is the least-solved layer (dedicated scores ~AUROC 0.6-0.7, modest PPV), that scores are valid only for RANKING within one patient (never absolute go/no-go or cross-patient), that DAI has anchor-inflation and WT-denominator traps, and that stacking weak correlated scores into one number is a red flag. Use when ordering a candidate list for a vaccine. Binding lives in mhc-binding-prediction; calling in neoantigen-prediction.
tool_type: python
primary_tool: NeoFox
---

## Version Compatibility

Reference examples tested with: NeoFox 1.0+, pVACtools 4.1+, pandas 2.2+, numpy 1.26+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

Notes specific to this skill: NeoFox annotates ~16 published features (it does not rank candidates automatically); PRIME 2.x requires MixMHCpred v3.0+ on PATH; BigMHC has separate `-m el` and `-m im` heads. ImmunoBERT is a PRESENTATION model, not an immunogenicity predictor — do not use it here. PRIME2.0 is the *Cell Systems* 2023 paper (the *Cell Reports Medicine* 2021 paper is PRIME v1). Re-verify tool versions and the supported-allele lists before scoring.

# Immunogenicity Scoring

**"Rank my neoantigen candidates by how likely a T cell responds"** -> Annotate presentation + recognition features and order candidates within a patient; never assign an absolute immunogenicity verdict.
- Python: `NeoFox` to compute the published feature panel; `PRIME` / `BigMHC -m im` for recognition scores
- CLI: pVACtools aggregate-report tiering as the auditable, rule-based default ranking

## The Single Most Important Modern Insight -- this is the least-solved layer; rank within a patient, never threshold

Binding/presentation is genuinely good (AUROC high-0.9s); immunogenicity is not close. Predicting whether a displayed peptide provokes a T-cell response requires knowing whether a cognate TCR exists in this patient's repertoire, whether that clone survived thymic negative selection (escaped tolerance), and whether it activates in a suppressive tumor microenvironment — none observable from sequence. Dedicated immunogenicity tools land around AUROC 0.6-0.7 on their own test sets and worse on independent data; in TESLA the dedicated in-silico immunogenicity scores correlated poorly with validated immunogenicity, while presentation strength, binding stability, abundance/expression, agretopicity, and foreignness carried the signal. Two operational rules follow. First, immunogenicity scores are calibrated within a context (a tool, an allele, often a patient's HLA), so they are legitimate for ordering one patient's candidate list and illegitimate for absolute go/no-go or cross-patient/cross-allele comparison. Second, a confident single composite number is a red flag: stacking weak, correlated, IEDB-bias-trained scores into one value launders the bias at higher apparent precision. The honest deliverable is an ordered, feature-annotated shortlist with its uncertainty stated out loud.

## Why "Best Binder" Lost to "Best Quality"

The best-binder heuristic fails on a tolerance argument: a peptide that binds MHC superbly but closely resembles a self-peptide the thymus presented has had its cognate T cells deleted, so display does not help. A moderate binder that looks strikingly un-self may have a full, un-tolerized repertoire. The modern requirement is conjunctive — a useful neoantigen must be both PRESENTED (binding) AND FOREIGN enough (different from self) to have escaped tolerance. The Łuksza/Balachandran fitness model formalizes this: quality = amplitude (how much better the mutant is presented than its WT, a DAI-like term) x recognition potential R (resemblance to known immunogenic foreign epitopes). This is why agretopicity and foreignness, not raw affinity, recur in every validated analysis.

## Tool Taxonomy

| Tool | Citation | What it scores | Note |
|------|----------|----------------|------|
| NeoFox | Lang 2021 | ~16 features at once (DAI, foreignness, dissimilarity, PRIME, PHBR, ...) | Annotates, does NOT rank — the right division of labor |
| pVACtools tiering | Hundal 2020 | Rule-based tiers + within-tier sort | Auditable default; quarantines anchor/subclonal traps |
| PRIME2.0 | Gfeller 2023 | Class I immunogenicity (presentation x TCR-recognition) | Strong; needs MixMHCpred v3.0+ |
| BigMHC-IM | Albert 2023 | Class I immunogenicity (transfer-learned) | High precision; pan-allelic |
| IEDB immunogenicity | Calis 2013 | Class I (AA + position) | Weak, allele-pooled, no self-comparison; one feature only |
| DeepImmuno | Li 2021 | Class I CNN | 9/10mer only; limited alleles |
| fitness model (foreignness) | Łuksza 2017; Balachandran 2017 | Quality = amplitude x recognition | The conceptual backbone |

## Decision Tree by Scenario

| Scenario | Recommended | Why |
|----------|-------------|-----|
| Default: rank a patient's candidates | NeoFox features -> pVACtools tiering -> human curation | Transparent features + auditable tiers, not a black-box score |
| Need a single recognition score | PRIME2.0 or BigMHC-IM | Best-validated class I; report alongside features, not alone |
| "Is this one immunogenic, yes/no?" | Reframe to ranking | No honest tool gives an absolute verdict |
| CD4 / class II immunogenicity | Flag as a frontier (TLimmuno2 etc.) | Class II immunogenicity is even less solved |
| Final shortlist for synthesis | Feature-annotated table + expression/clonality filters | Presentation + abundance carry most real signal (TESLA) |

## Annotate Features, Then Rank Within Patient

**Goal:** Order one patient's candidates without collapsing fragile features into a single over-trusted number.

**Approach:** Compute the feature panel (NeoFox), apply the non-negotiable expression/clonality filters first, then sort by presentation + abundance + quality features, keeping the features visible side by side for human curation. Cross-patient comparison is invalid.

```python
import pandas as pd

def rank_within_patient(df, expr_col='gene_expression', vaf_col='rna_vaf'):
    '''Filter (not score) on expression/clonality first, then order by presentation,
    abundance, and quality. Returns a feature-annotated table for human curation, not
    a verdict. Scores are within-patient only - never compare across patients/alleles.'''
    keep = df[(df[expr_col] >= 1.0) & (df[vaf_col] >= 0.25)].copy()
    sort_cols = ['presentation_rank', 'gene_expression', 'agretopicity', 'foreignness']
    ascending = [True, False, False, False]
    cols = [c for c in sort_cols if c in keep.columns]
    asc = [a for c, a in zip(sort_cols, ascending) if c in keep.columns]
    return keep.sort_values(cols, ascending=asc)
```

## Compute Agretopicity (DAI) Defensively

**Goal:** Use the mutant-vs-WT binding gain without falling into its two traps.

**Approach:** Agretopicity (ratio, IC50_WT / IC50_MT; the DAI family — Duan 2014 uses the difference form) rewards a mutant that binds while WT does not. Trap 1: an anchor-position mutation inflates it without changing the TCR-facing surface (quarantine via the Anchor tier). Trap 2: when WT binds very poorly, the denominator explodes and the ratio is dominated by prediction noise — a value of 200 on a barely-estimable WT is not 100x more meaningful than a value of 2.

```python
def defensive_dai(df, wt='wt_ic50', mt='mt_ic50', anchor='mutation_at_anchor', wt_cap=5000):
    '''Flag anchor-inflated and denominator-unstable DAI rather than trusting the number.'''
    out = df.copy()
    out['dai'] = out[wt] / out[mt]
    out['dai_anchor_artifact'] = out[anchor]                 # surface unchanged -> DAI is artifact
    out['dai_unstable'] = out[wt] > wt_cap                   # WT barely presented -> ratio is noise
    out['dai_trustworthy'] = ~out['dai_anchor_artifact'] & ~out['dai_unstable']
    return out
```

## Per-Method Failure Modes

### Treating a score as a verdict
**Trigger:** "score > X means immunogenic" or comparing scores across patients. **Mechanism:** scores are calibrated within tool/allele/patient. **Symptom:** false confidence; cross-patient mis-ranking. **Fix:** rank within a patient; state uncertainty; never threshold absolutely.

### The composite-score illusion
**Trigger:** summing/modeling DAI + foreignness + dissimilarity + hydrophobicity + PRIME into one number. **Mechanism:** components are weak, correlated (several measure "un-selfness"), and trained on ill-defined negatives. **Symptom:** an authoritative-looking 3-decimal number hiding fragile assumptions. **Fix:** keep features side by side; use auditable tiers; let a human weigh axes.

### DAI anchor inflation / denominator instability
**Trigger:** trusting a high DAI. **Mechanism:** anchor mutation changes binding not TCR surface; tiny WT binding blows up the ratio. **Symptom:** top-ranked candidates that are anchor artifacts or noise. **Fix:** inspect mutation position and actual WT binding; quarantine via Anchor tier.

### Negative-set blindness
**Trigger:** trusting a new tool's headline AUROC. **Mechanism:** IEDB "negatives" conflate proven-non-immunogenic with untested; redrawing realistic negatives collapses performance. **Symptom:** great benchmark, poor real-world PPV. **Fix:** ask how negatives were defined before reading the number.

### CD4/class II blind spot
**Trigger:** optimizing a vaccine purely on class I immunogenicity. **Mechanism:** CD4 help drives durable efficacy but class II immunogenicity is a frontier. **Symptom:** optimizing the better-measured half of a two-armed problem. **Fix:** flag class II as unproven; include CD4 epitopes via mhc-class-ii-prediction.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| Dedicated immunogenicity AUROC ~0.6-0.7 | TESLA; tool benchmarks | The honest performance ceiling; weak prior, not verdict |
| Gene TPM >= 1, RNA VAF >= 0.25 | pVACtools defaults | Unexpressed/low-VAF peptides are not displayed (filter first) |
| Subclonal at DNA VAF <= purity/4 | pVACtools | Clonal targets beat subclonal (McGranahan 2016) |
| Presentation + abundance carry the signal | Wells 2020 (TESLA) | Most predictive power is upstream of recognition scores |
| Rank within patient only | Score calibration | Cross-patient/allele comparison is invalid |
| Agretopicity ratio (amplitude); DAI difference | Łuksza 2017; Duan 2014 | Inspect position + WT binding; anchor inflation and denominator instability |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| Absolute "immunogenic: yes/no" claim | Thresholded a within-context score | Reframe as within-patient ranking |
| Over-trusted single composite | Stacked weak correlated scores | Keep features visible; audit with tiers |
| High-DAI artifacts at top | Anchor mutation / unstable WT denominator | Defensive DAI; Anchor tier |
| Used ImmunoBERT as immunogenicity | It is a presentation model | Use PRIME/BigMHC-IM/Calis for recognition |
| Great AUROC, poor validation | Ill-defined negative set | Interrogate negatives; demand functional validation |
| Class II candidates over-trusted | CD4 immunogenicity is a frontier | Flag uncertainty; treat as unproven |

## References

- Wells DK, van Buuren MM, Dang KK, et al. 2020. Key parameters of tumor epitope immunogenicity revealed through a consortium approach improve neoantigen prediction (TESLA). *Cell* 183(3):818-834.
- Łuksza M, Riaz N, Makarov V, et al. 2017. A neoantigen fitness model predicts tumour response to checkpoint blockade immunotherapy. *Nature* 551:517-520.
- Balachandran VP, Łuksza M, Zhao JN, et al. 2017. Identification of unique neoantigen qualities in long-term survivors of pancreatic cancer. *Nature* 551:512-516.
- Calis JJA, Maybeno M, Greenbaum JA, et al. 2013. Properties of MHC class I presented peptides that enhance immunogenicity. *PLoS Computational Biology* 9(10):e1003266.
- Schmidt J, Smith AR, Magnin M, et al. 2021. Prediction of neo-epitope immunogenicity reveals TCR recognition determinants (PRIME). *Cell Reports Medicine* 2(2):100194.
- Gfeller D, Schmidt J, Croce G, et al. 2023. Improved predictions of antigen presentation and TCR recognition with MixMHCpred2.2 and PRIME2.0. *Cell Systems* 14(1):72-83.
- Albert BA, Yang Y, Shao XM, et al. 2023. Deep neural networks predict class I MHC epitope presentation and transfer learn neoepitope immunogenicity (BigMHC). *Nature Machine Intelligence* 5(8):861-872.
- Duan F, Duitama J, Al Seesi S, et al. 2014. Genomic and bioinformatic profiling of mutational neoepitopes reveals new rules to predict anticancer immunogenicity (DAI). *Journal of Experimental Medicine* 211(11):2231-2248.
- Richman LP, Vonderheide RH, Rech AJ. 2019. Neoantigen dissimilarity to the self-proteome predicts immunogenicity and response to immune checkpoint blockade. *Cell Systems* 9(4):375-382.
- Lang F, Riesgo-Ferreiro P, Löwer M, Sahin U, Schrörs B. 2021. NeoFox: annotating neoantigen candidates with neoantigen features. *Bioinformatics* 37(22):4246-4247.
- Hundal J, Kiwala S, McMichael J, et al. 2020. pVACtools: a computational toolkit to identify and visualize cancer neoantigens. *Cancer Immunology Research* 8(3):409-420.

## Related Skills

- immunoinformatics/neoantigen-prediction - produces the candidate list this skill ranks
- immunoinformatics/mhc-binding-prediction - the presentation features that carry most of the signal
- immunoinformatics/mhc-class-ii-prediction - CD4 immunogenicity, the under-served frontier
- immunoinformatics/epitope-prediction - epitope candidates feeding the ranking
- clinical-databases/somatic-signatures - clonal neoantigen burden as an ICI-response correlate
<!-- END FILE: immunoinformatics/immunogenicity-scoring/SKILL.md -->

## 子目录：immunoinformatics/mhc-binding-prediction

<!-- BEGIN FILE: immunoinformatics/mhc-binding-prediction/SKILL.md -->
---
name: bio-immunoinformatics-mhc-binding-prediction
description: Predict peptide-MHC class I binding and natural presentation with MHCflurry, NetMHCpan-4.1, and MixMHCpred to nominate candidate CD8 T-cell epitopes. Covers the binding-affinity (BA) vs eluted-ligand (EL/presentation) distinction, why %Rank beats raw nM for cross-allele work, the MS abundance bias that misranks low-expression neoantigens, allele-coverage inequity, and length bias. Use when scanning a protein or peptide set for class I epitopes, scoring neoantigen candidates, or choosing a binding predictor. For CD4/HLA class II see mhc-class-ii-prediction.
tool_type: python
primary_tool: mhcflurry
---

## Version Compatibility

Reference examples tested with: MHCflurry 2.1+, pandas 2.2+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

Notes specific to this skill: MHCflurry 2.2.0+ switched its backend from TensorFlow to PyTorch (Python 3.10+) — confirm `mhcflurry-downloads fetch` succeeded and the backend imports before scoring. NetMHCpan-4.1 and MixMHCpred are standalone academic binaries, not pip-installable; the IEDB REST API wraps NetMHCpan if a local install is unavailable. Tool versions move fast — re-verify supported-allele lists and default %Rank thresholds against current docs.

# MHC Binding Prediction

**"Predict which peptides bind/are presented by MHC class I"** -> Score peptide-HLA class I binding affinity and natural-presentation likelihood to nominate candidate CD8 epitopes.
- Python: `mhcflurry.Class1PresentationPredictor.load().predict()` (pip-installable, forgiving allele parser)
- CLI: `netMHCpan` (field default; EL score by default, `-BA` adds affinity) or `MixMHCpred` (MS-deconvolution, EL-only)

## The Single Most Important Modern Insight -- a strong predicted binder is a candidate for the next experiment, not an epitope

Binding to MHC is necessary but nowhere near sufficient for immunogenicity. The real path is a funnel: expression -> proteasomal processing -> TAP transport and loading -> stable surface display -> a cognate T cell that survived thymic selection and activates. Binding prediction addresses essentially one stage. Each downstream stage discards a large fraction of binders, so the precision of "predicted binder -> validated epitope" is low even when the binding model itself is excellent. Two operational corollaries follow. First, never report a presentation score to a collaborator as an "immunogenicity" or "epitope" probability — that is a different, far weaker prediction (immunoinformatics/immunogenicity-scoring). Second, the modern EL/MS models that now define the field learned natural presentation from mass-spec immunopeptidomes, which over-represent peptides from highly expressed proteins; the model therefore partly learns "comes from an abundant protein" as a proxy for "is presented." That bias is exactly backwards for neoantigen discovery, where the targets are mutated and often lowly expressed, living in the under-detected tail the model systematically under-ranks.

## Tool Taxonomy (Class I)

| Tool | Citation | Score type | Form | Use when |
|------|----------|-----------|------|----------|
| NetMHCpan-4.1 | Reynisson 2020 | EL (default) + BA (`-BA`) | standalone/web/IEDB | Field default; broadest allele coverage; presentation discovery |
| MHCflurry 2.0 | O'Donnell 2020 | BA + processing + presentation | pip Python | Scripting, messy allele strings, integrated presentation score |
| MixMHCpred 3.0 | Tadros 2025 | EL only (MS motifs) | standalone | MS-grounded presentation; cross-allele/species extrapolation study |
| NetMHC-4.0 | Andreatta 2016 | BA only | standalone/web | Legacy reproducibility; allele-specific, data-rich common alleles |
| MHCnuggets | Shao 2020 | BA (IC50) | pip Python | High-throughput TCGA-scale screens; rare-allele transfer learning |

## BA vs EL -- the conceptual axis that determines which score to read

BA (binding affinity) models train on in-vitro competitive-binding IC50 assays and measure only whether the groove can hold the peptide thermodynamically. EL (eluted-ligand / presentation) models train on mass-spec immunopeptidomics — peptides actually eluted from MHC on real cells — so the label implicitly folds in processing, transport, editing, and surface stability. Read BA for "could this bind the groove if delivered there"; read EL/presentation for "is this likely naturally presented," which is the default and recommended output of NetMHCpan-4.1, MHCflurry's presentation predictor, and MixMHCpred. IEDB codifies the split: `netmhcpan_ba` = recommended-binding, `netmhcpan_el` = recommended-epitope. Pick by intent.

## Decision Tree by Scenario

| Scenario | Recommended | Why |
|----------|-------------|-----|
| Quick scriptable scan, messy allele names | MHCflurry presentation predictor | pip-installable, normalizes `A*02:01`/`A0201`/`HLA-A0201` |
| Maximal accuracy / broadest alleles | NetMHCpan-4.1 EL | Field default; concurrent MS motif deconvolution |
| Neoantigen candidate scoring | EL/presentation + expression check | EL under-ranks low-expression mutants (abundance bias) |
| "Can it physically bind" (engineered/delivered peptide) | BA mode (`-BA`, MHCflurry affinity) | Question is thermodynamic, not presentation |
| Rare / non-European allele | NetMHCpan-4.1, but verify training support | Pan-models extrapolate; confidence drops off the manifold |
| Cross-allele ranking in a multi-HLA patient | %Rank, never raw nM | nM scales differ per allele; nM cutoffs are allele-biased |

## Predict Presentation with MHCflurry

**Goal:** Score peptides against a patient genotype and report the best-presenting allele per peptide.

**Approach:** Load the presentation predictor; pass `alleles` as a sample->genotype dict so the model reports `best_allele`, `affinity` (nM), `affinity_percentile` (%Rank), and `presentation_score` (0-1, higher = more likely presented). Supply real `n_flanks`/`c_flanks` only if the genomic context is known.

```python
from mhcflurry import Class1PresentationPredictor

predictor = Class1PresentationPredictor.load()
df = predictor.predict(
    peptides=['SIINFEKL', 'GILGFVFTL', 'NLVPMVATV'],
    alleles={'patient1': ['HLA-A*02:01', 'HLA-A*24:02', 'HLA-B*07:02']},
    include_affinity_percentile=True,   # required: %Rank column is off by default
    verbose=0,
)
# columns: peptide, sample_name, affinity, best_allele, processing_score,
#          presentation_score, and affinity_percentile (only with the flag above)
# affinity nM: LOWER is stronger. presentation_score: HIGHER is more likely presented.
```

## Interpret with %Rank, Not Raw nM

**Goal:** Classify binding strength in a way that is comparable across alleles.

**Approach:** Threshold on %Rank (percentile of the score against random peptides for that same allele), not on absolute IC50. The 500 nM convention is allele-biased — it over-calls permissive alleles and under-calls restrictive ones, skewing a multi-HLA patient's epitope list toward a subset of the genotype.

```python
def classify_by_percentile(affinity_percentile):
    '''Class I %Rank cutoffs (NetMHCpan convention). LOWER percentile = stronger.
    Strong binder <= 0.5%; weak binder <= 2.0%. Use %Rank for any cross-allele
    comparison; raw nM is only meaningful within a single allele.'''
    if affinity_percentile <= 0.5:
        return 'strong'
    elif affinity_percentile <= 2.0:
        return 'weak'
    return 'non-binder'
```

## Scan a Protein for Class I Epitopes

**Goal:** Enumerate candidate epitopes across a protein for a patient genotype.

**Approach:** Tile 8-11mers (9mers dominate real ligands), score all windows in one batched call, keep windows under the 2% weak-binder cutoff. See examples/mhc_binding.py for the full tiling-and-rank script.

```python
def scan_protein(protein_seq, genotype, lengths=(8, 9, 10, 11)):
    from mhcflurry import Class1PresentationPredictor
    predictor = Class1PresentationPredictor.load()
    peptides = [protein_seq[i:i + k] for k in lengths for i in range(len(protein_seq) - k + 1)]
    df = predictor.predict(peptides=peptides, alleles={'patient': list(genotype)},
                           include_affinity_percentile=True, verbose=0)
    return df[df['affinity_percentile'] <= 2.0].sort_values('affinity_percentile')
```

## Per-Method Failure Modes

### Pan-model extrapolation on rare alleles
**Trigger:** scoring an allele with little/no training support (much of HLA-C, many non-European alleles). **Mechanism:** pan-models emit a confident %Rank for any allele sequence — there is no built-in "I don't know." **Symptom:** a flat/mushy predicted motif; calls that don't validate. **Fix:** check the allele is in the trained/supported list and that close pseudosequence neighbors had real ligands; downgrade confidence when extrapolating.

### EL abundance bias misranks neoantigens
**Trigger:** ranking mutated, low-expression peptides by EL/presentation score alone. **Mechanism:** MS immunopeptidomes over-represent abundant proteins; EL partly learns expression as a presentation proxy. **Symptom:** housekeeping-gene peptides float to the top; real low-expression neoantigens sink. **Fix:** combine EL with measured expression (TPM) and judge within-target, not against the proteome.

### Placeholder flanks corrupt the processing score
**Trigger:** passing dummy `n_flanks`/`c_flanks` to get a presentation/processing number. **Mechanism:** the processing model reads flanking context; wrong flanks inject noise. **Symptom:** processing_score that tracks nothing biological. **Fix:** supply the true genomic flanks, or omit flanks and read affinity/EL only.

### Allele in the list != well-trained on that allele
**Trigger:** trusting a number because the allele appears in `-listMHC`/`supported_alleles`. **Mechanism:** coverage is not training support. **Fix:** treat coverage and data depth as separate questions.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| Class I strong binder <= 0.5% Rank | NetMHCpan-4.1 default (`-rth 0.5`) | Percentile normalizes per-allele score scales |
| Class I weak binder <= 2.0% Rank | NetMHCpan-4.1 default (`-rlt 2.0`) | Standard recall/precision balance for candidate lists |
| Peptide length 8-11mers (9 dominant) | Immunopeptidome composition | 9mers dominate training; non-9mers thinner evidence |
| IC50 <= 500 nM "strong" (legacy) | Pre-pan-allele convention | Allele-biased; AVOID for cross-allele work, use %Rank |
| 2-field (4-digit) HLA resolution | IMGT/HLA, groove determinants | Higher fields are synonymous/intronic; serotype is insufficient |
| Evaluate by PPV@top-N, not bare AUC | Zhao & Sher 2018; imbalance | True ligands ~1 in 10,000+; AUC is computed on an unreal balance |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| Epitope list skewed to one HLA in a patient | Thresholded on nM not %Rank | Use affinity_percentile / %Rank |
| MHCflurry import/backend error | TF->PyTorch backend change (2.2.0+) | Use Python 3.10+; re-run `mhcflurry-downloads fetch` |
| Confident number on an untrained allele | Pan-model extrapolation | Verify supported allele + training depth |
| Low-expression neoantigen under-ranked | EL/MS abundance bias | Integrate expression; rank within-target |
| Reporting presentation as "immunogenicity" | Conflating funnel stages | Defer to immunogenicity-scoring; caveat the report |
| Class II call trusted like class I | Different maturity regime | Use mhc-class-ii-prediction; treat II as hypothesis |

## References

- Reynisson B, Alvarez B, Paul S, Peters B, Nielsen M. 2020. NetMHCpan-4.1 and NetMHCIIpan-4.0: improved predictions of MHC antigen presentation by concurrent motif deconvolution and integration of MS MHC eluted ligand data. *Nucleic Acids Research* 48(W1):W449-W454.
- O'Donnell TJ, Rubinsteyn A, Laserson U. 2020. MHCflurry 2.0: improved pan-allele prediction of MHC class I-presented peptides by incorporating antigen processing. *Cell Systems* 11(1):42-48.e7.
- Tadros DM, Racle J, Gfeller D, et al. 2025. Predicting MHC-I ligands across alleles and species: how far can we go? *Genome Medicine* 17:25.
- Andreatta M, Nielsen M. 2016. Gapped sequence alignment using artificial neural networks: application to the MHC class I system (NetMHC-4.0). *Bioinformatics* 32(4):511-517.
- Shao XM, Bhattacharya R, Huang J, et al. 2020. High-throughput prediction of MHC class I and II neoantigens with MHCnuggets. *Cancer Immunology Research* 8(3):396-408.
- Zhao W, Sher X. 2018. Systematically benchmarking peptide-MHC binding predictors: from synthetic to naturally processed epitopes. *PLOS Computational Biology* 14(11):e1006457.
- Trolle T, Metushi IG, Greenbaum JA, et al. 2015. Automated benchmarking of peptide-MHC class I binding predictions. *Bioinformatics* 31(13):2174-2181.

## Related Skills

- immunoinformatics/mhc-class-ii-prediction - CD4/HLA class II binding (the harder, less-reliable regime; open groove, register, DQ pairing)
- immunoinformatics/neoantigen-prediction - applies class I binding to tumor mutations; where the EL abundance bias bites
- immunoinformatics/immunogenicity-scoring - the separate, weaker prediction of T-cell response (binding != immunogenicity)
- immunoinformatics/epitope-prediction - T-cell epitope mapping reduces to MHC presentation; B-cell epitopes are a different problem
- clinical-databases/hla-typing - determine the patient genotype that conditions every prediction
<!-- END FILE: immunoinformatics/mhc-binding-prediction/SKILL.md -->

## 子目录：immunoinformatics/mhc-class-ii-prediction

<!-- BEGIN FILE: immunoinformatics/mhc-class-ii-prediction/SKILL.md -->
---
name: bio-immunoinformatics-mhc-class-ii-prediction
description: Predict peptide-MHC class II (HLA-DR/DQ/DP) binding and presentation for CD4 T-cell epitopes with NetMHCIIpan-4.3 and MixMHC2pred-2.0. Covers why class II is far less reliable than class I (open binding groove, 9-mer register ambiguity, sparse noisy training data, DR>DP>DQ accuracy asymmetry), the DQ/DP heterodimer alpha/beta pairing trap, and the looser 1%/5% %Rank thresholds. Use when predicting CD4 epitopes for vaccine help, mapping class II neoantigens, or scoring long peptides against DR/DQ/DP. For CD8/class I see mhc-binding-prediction.
tool_type: cli
primary_tool: NetMHCIIpan
---

## Version Compatibility

Reference examples tested with: NetMHCIIpan 4.3+, MixMHC2pred 2.0+, pandas 2.2+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

Notes specific to this skill: NetMHCIIpan and MixMHC2pred are standalone academic binaries (not pip-installable); the IEDB MHC-II REST API wraps NetMHCIIpan if a local install is unavailable. Allele nomenclature differs sharply between tools and between isotypes (DR single-chain vs DQ/DP heterodimer) — confirm the exact string format against the installed tool before scoring. Class II %Rank thresholds (1%/5%) are LOOSER than class I (0.5%/2.0%); do not copy class I cutoffs.

# MHC Class II Prediction

**"Predict which long peptides bind/are presented by HLA class II"** -> Score peptide-HLA class II (DR/DQ/DP) presentation to nominate candidate CD4 T-cell epitopes, inferring the 9-mer binding core within each long peptide.
- CLI: `NetMHCIIpan` (field default; EL score by default, `-BA` adds affinity; pan-DR/DQ/DP)
- CLI: `MixMHC2pred` (MS-deconvolution motifs; models the reverse DP binding mode)

## The Single Most Important Modern Insight -- class II is basically broken, and that must be stated plainly

For class I, modern pan-allele EL predictors recover most true ligands at high precision and the field has hit diminishing returns. The same architectures, on the same conceptual pipeline, produce dramatically weaker class II predictions. The honest one-line summary to give a collaborator is: "trust a class I strong-binder call; treat a class II call as a ranked hypothesis, not a fact." Four compounding reasons, not one, cause this. The groove is open at both ends, so a 12-25mer can sit in multiple registers and the model must infer which latent 9-residue core is the true binding frame — an error-prone latent-variable problem class I (closed groove, defined termini) never faces. The training data are smaller and noisier: in-vitro class II binding assays are notoriously irreproducible, and class II immunopeptidomics yields fewer, longer, more heterogeneous peptides. The three isotypes are unequally tractable — historically DR >> DP > DQ, because DR was studied first and most while DQ was data-starved (NetMHCIIpan-4.3's headline 2023 contribution was finally closing this gap with tailored data acquisition, a sign of how recent and data-driven the fix is). And DP/DQ are obligate alpha/beta heterodimers whose chains are independently polymorphic, so the effective number of distinct molecules is the combinatorial product of alpha and beta alleles.

## The DQ/DP heterodimer pairing trap

A donor's DQA1 and DQB1 alleles pair both in cis (same haplotype) and in trans (across haplotypes), so a heterozygous individual can express up to four DQ heterodimers — and some trans-pairs are non-functional or rare. Mechanically feeding all DQA1 x DQB1 combinations to NetMHCIIpan generates molecules that do not biologically exist; taking only cis pairs may miss real trans-dimers. There is no fully automated, universally agreed resolution. The expert move is to be explicit about the pairing assumption, prefer documented haplotype pairings, and flag DQ (and to a lesser extent DP) epitope calls as lower-confidence than DR. DR is single-chain (the alpha is effectively invariant), so it carries none of this combinatorial burden and is the most trustworthy isotype.

## Tool Taxonomy (Class II)

| Tool | Citation | Score type | Loci | Use when |
|------|----------|-----------|------|----------|
| NetMHCIIpan-4.3 | Nilsson 2023 | EL (default) + BA (`-BA`) | DR, DQ, DP (+ mouse H-2, BoLA) | Field default; broadest coverage; closes DQ gap; reverse-mode binders |
| MixMHC2pred-2.0 | Racle 2023 | EL only (MS motifs) | DR, DQ, DP | MS-grounded motifs; models reverse (C->N) DP binding mode |
| MHCnuggets | Shao 2020 | BA (IC50) | class I + II | High-throughput screens; rare-allele transfer learning |
| NetMHCIIpan-4.0 | Reynisson 2020 | EL + BA | DR, DQ, DP | Reproducing 2020-era results; superseded by 4.3 |

## Decision Tree by Scenario

| Scenario | Recommended | Why |
|----------|-------------|-----|
| Default CD4 epitope screen | NetMHCIIpan-4.3 EL | Broadest, pan-allele, current accuracy |
| DR-restricted, want highest confidence | NetMHCIIpan-4.3 (DRB1_*) | DR is the most reliable isotype (single-chain) |
| DQ or DP restriction | NetMHCIIpan-4.3 + explicit pairing | Heterodimer combinatorics; flag as lower-confidence |
| MS-grounded motif / DP reverse binders | MixMHC2pred-2.0 | Built from deconvolved immunopeptidomes; models reverse mode |
| Class II neoantigens (CD4 help) | NetMHCIIpan-4.3 EL + expression | CD4 help boosts vaccine efficacy; EL still abundance-biased |
| No local install | IEDB MHC-II REST API | Wraps NetMHCIIpan, always-current versions |

## Running the Predictions (the fragile commands - run as written)

NetMHCIIpan reads a peptide list or FASTA and scores against one or more alleles. EL %Rank is the default output; `-BA` adds an affinity prediction. The model reports the inferred 9-mer core and its offset.

```bash
# DR (single-chain: beta allele names the molecule)
netMHCIIpan -f peptides.txt -inptype 1 -a DRB1_0101 -BA -xls -xlsfile out.tsv

# DQ heterodimer (BOTH chains, hyphen-joined) and DP
netMHCIIpan -f antigen.fasta -a HLA-DQA10501-DQB10201,HLA-DPA10103-DPB10401 -length 15
```
Key flags: `-a` allele(s, comma-separated), `-f` input, `-inptype` (0=FASTA, 1=peptide list), `-length` peptide length(s) to consider, `-BA` add affinity, `-xls`/`-xlsfile` tab output, `-list` dump supported alleles.

MixMHC2pred uses chain-underscore allele names with a DOUBLE underscore between heterodimer chains, and alleles are space-separated:
```bash
MixMHC2pred -i peptides.txt -o out.txt -a DRB1_15_01 DRB5_01_01 DPA1_02_01__DPB1_01_01
```

## Per-Method Failure Modes

### Register ambiguity in the open groove
**Trigger:** any class II prediction on a long peptide. **Mechanism:** the 9-mer binding core can sit in several frames; the model infers the latent core. **Symptom:** the reported core shifts with small input changes; unstable rankings. **Fix:** treat the call as a hypothesis; corroborate with MixMHC2pred and check core consistency; never over-interpret a single offset.

### DQ/DP heterodimer mis-pairing
**Trigger:** expanding a genotype to all DQA1 x DQB1 (or DPA1 x DPB1) combinations. **Mechanism:** not all alpha/beta pairs form stable functional dimers; trans-pairs may be rare. **Symptom:** epitope calls against molecules that do not exist in the donor. **Fix:** restrict to documented/cis pairings, state the assumption, flag DQ/DP as lower-confidence than DR.

### Copying class I thresholds
**Trigger:** applying 0.5%/2.0% %Rank to class II. **Mechanism:** class II distributions and recommended cutoffs differ. **Symptom:** over-stringent filtering, missed real binders. **Fix:** use class II cutoffs (strong <= 1%, weak <= 5%).

### EL abundance bias (shared with class I)
**Trigger:** ranking class II neoantigens by EL alone. **Mechanism:** MS immunopeptidomes over-represent abundant proteins. **Symptom:** low-expression CD4 neoantigens under-ranked. **Fix:** integrate expression; judge within-target.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| Class II strong binder <= 1% Rank | NetMHCIIpan-4.x default | Looser than class I; reflects class II score distributions |
| Class II weak binder <= 5% Rank | NetMHCIIpan-4.x default | Standard recall/precision balance for class II |
| Peptide length 12-25mers (core = 9) | Open-groove biology | Class II ligands are long with ragged termini; core always 9 |
| MixMHC2pred input 12-21mers | Racle 2023 | Outside this range or non-standard residues -> NA |
| 2-field (4-digit) typing for both chains | IMGT/HLA | Both alpha and beta needed for DQ/DP heterodimers |
| Isotype confidence DR > DP > DQ | Nilsson 2023 | Reflects historical training-data depth per isotype |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| Allele not recognized | Wrong nomenclature for the tool | NetMHCIIpan `DRB1_0101`/`HLA-DQA10501-DQB10201`; MixMHC2pred `DRB1_15_01`/`DPA1_02_01__DPB1_01_01` |
| Calls against non-existent molecules | Naive DQ/DP combinatorial expansion | Use cis/documented pairings; flag DQ/DP |
| Over-stringent, few binders | Class I cutoffs applied | Use 1%/5% class II thresholds |
| Unstable core/offset | Register ambiguity | Corroborate across tools; treat as hypothesis |
| `NA` scores from MixMHC2pred | Peptide outside 12-21mer / non-standard residue | Filter input length and alphabet first |
| Class II trusted like class I | Different maturity regime | Report as ranked hypotheses, not facts |

## References

- Nilsson JB, Kaabinejadian S, Yari H, et al. 2023. Accurate prediction of HLA class II antigen presentation across all loci using tailored data acquisition and refined machine learning (NetMHCIIpan-4.3). *Science Advances* 9(47):eadj6367.
- Racle J, Guillaume P, Schmidt J, et al. 2023. Machine learning predictions of MHC-II specificities reveal alternative binding mode of class II epitopes (MixMHC2pred-2.0). *Immunity* 56(6):1359-1375.e13.
- Racle J, Michaux J, Rockinger GA, et al. 2019. Robust prediction of HLA class II epitopes by deep motif deconvolution of immunopeptidomes (MixMHC2pred-1.0). *Nature Biotechnology* 37:1283-1286.
- Reynisson B, Alvarez B, Paul S, Peters B, Nielsen M. 2020. NetMHCpan-4.1 and NetMHCIIpan-4.0: improved predictions of MHC antigen presentation by concurrent motif deconvolution and integration of MS MHC eluted ligand data. *Nucleic Acids Research* 48(W1):W449-W454.
- Shao XM, Bhattacharya R, Huang J, et al. 2020. High-throughput prediction of MHC class I and II neoantigens with MHCnuggets. *Cancer Immunology Research* 8(3):396-408.

## Related Skills

- immunoinformatics/mhc-binding-prediction - CD8/HLA class I binding (the solved regime; closed groove, 0.5%/2.0% cutoffs)
- immunoinformatics/neoantigen-prediction - class II neoantigens for CD4 help; pVACseq runs both classes
- immunoinformatics/immunogenicity-scoring - CD4 immunogenicity is even less solved than CD8
- immunoinformatics/epitope-prediction - T-cell epitope prediction reduces to MHC presentation
- clinical-databases/hla-typing - resolve DR/DQ/DP alleles for both chains
<!-- END FILE: immunoinformatics/mhc-class-ii-prediction/SKILL.md -->

## 子目录：immunoinformatics/neoantigen-prediction

<!-- BEGIN FILE: immunoinformatics/neoantigen-prediction/SKILL.md -->
---
name: bio-immunoinformatics-neoantigen-prediction
description: Identify tumor neoantigens from somatic variants with pVACtools (pVACseq/pVACfuse/pVACbind/pVACvector/pVACview) for personalized cancer vaccines and checkpoint biomarkers. Encodes the field's hard truth that binding prediction is the easy, near-solved part and single-digit-percent PPV lives downstream — so it centers clonality/CCF, HLA LOH (the silent invalidator), expression, proximal-variant phasing, agretopicity/foreignness quality, and the predicted->presented->immunogenic validation tiers. Use when nominating vaccine targets, ranking neoantigens, or building a tumor-to-candidate pipeline. Binding details in mhc-binding-prediction; ranking in immunogenicity-scoring.
tool_type: mixed
primary_tool: pVACtools
---

## Version Compatibility

Reference examples tested with: Ensembl VEP 111+, pVACtools 4.1+, MHCflurry 2.1+, VAtools 5+, pandas 2.2+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

Notes specific to this skill: pVACtools is now at 7.x; positional CLI args are stable across 4.x-7.x but defaults and the supported-algorithm list change between releases — always run `pvacseq run --help` against the installed build. pVACseq requires the Wildtype and Frameshift VEP plugins; the Downstream plugin was replaced by Frameshift in pVACtools 2.0, so 4.x+ pipelines must NOT use Downstream. A local IEDB install (`--iedb-install-directory`) is strongly preferred over the rate-limited public API for patient data.

# Neoantigen Prediction

**"Find neoantigens from my tumor mutations"** -> Translate somatic variants into mutant peptides, predict patient-HLA presentation, and rank by tumor-specific quality for vaccine/biomarker use.
- CLI: `pvacseq run` on a VEP-annotated, expression/readcount-annotated somatic VCF + patient HLA (pVACtools)
- CLI: `pvacfuse` (fusions via AGFusion/Arriba), `pvacbind` (arbitrary peptides), `pvacview` (manual re-tiering)
- Python: VAtools annotation, LOHHLA/CCF integration, aggregate-report parsing

## The Single Most Important Modern Insight -- binding is the easy part; PPV lives downstream

The visible surface of the field — NetMHCpan, MHCflurry, the IC50 column everyone sorts on — is the binding step, and binding is the one step the field has genuinely cracked. The positive predictive value of a binding-only neoantigen pipeline is single-digit percent: of peptides confidently called strong binders, the large majority are never presented, and of those presented, the large majority never elicit a T-cell response (TESLA; Wells 2020). This is structural, not a bad IC50 cutoff — each step of the presentation-and-recognition cascade multiplies a low conditional probability. The corrective: spend the analysis on the filters and features that govern the predicted->presented->immunogenic attrition (clonality/CCF, HLA LOH, expression, agretopicity, foreignness, processing, validation tiers) and treat the choice of binding algorithm as a near-afterthought with sane defaults. TESLA's five features that actually separated immunogenic peptides from binders: HLA binding affinity, source-gene expression ("tumor abundance"), peptide-HLA binding stability, hydrophobicity, and the two recognition features — agretopicity and foreignness.

## The pVACtools Suite

| Sub-tool | Input that defines the peptide | Use case |
|----------|--------------------------------|----------|
| pVACseq | VEP-annotated somatic VCF (SNV + indel/frameshift) | The workhorse: point mutations and frameshifts |
| pVACfuse | AGFusion / Arriba fusion output | Fusion-junction novel-ORF neoantigens |
| pVACbind | a plain peptide FASTA | Score arbitrary peptides (MS hits, splice peptides); no WT/agretopicity |
| pVACvector | chosen epitopes | Order epitopes into a vaccine string, minimizing junctional neo-epitopes |
| pVACview | `*.all_epitopes.aggregated.tsv` | Human-in-the-loop review and re-tiering (the decision step) |

## Upstream Chain (every link can silently poison the output)

| Step | Tool(s) | Failure if skipped/wrong |
|------|---------|--------------------------|
| Somatic calling (T/N) | Mutect2, Strelka2 (consensus) | Germline leak -> false neoantigens; indels matter most (frameshifts) |
| VEP annotation | VEP + Wildtype + Frameshift plugins, `--fasta`, `--tsl`, `--symbol` | Most error-prone step; wrong plugins -> no WT peptide / no frameshift ORF |
| HLA typing (I and II) | OptiType (class I, WES), arcasHLA (RNA), HLA-HD (II) | Wrong allele = confident garbage; type at 4-digit; reconcile DNA vs RNA |
| Expression | kallisto/salmon TPM, `vcf-expression-annotator` | `--expn-val` passes everything if unannotated -> ships unexpressed "neoantigens" |
| Read counts | bam-readcount, `vcf-readcount-annotator` | VAF/coverage filters pass everything if unannotated |
| Phasing | merge somatic+germline, WhatsHap / GATK ReadBackedPhasing | Proximal in-cis variants -> peptides the patient never makes (neoepiscope, Wood 2020) |

## Decision Tree by Scenario

| Scenario | Recommended | Why |
|----------|-------------|-----|
| SNV + indel neoantigens | pVACseq, all_class_i | The workhorse; frameshifts via Frameshift plugin |
| Gene fusions | pVACfuse (AGFusion/Arriba, with STAR-Fusion read support) | Junction novel ORFs; demand junction read support |
| Proximal germline/somatic variants nearby | pVACseq `--phased-proximal-variants-vcf` | Otherwise the peptide sequence is wrong |
| Need quality features (DAI, foreignness, dissimilarity) | NeoFox / antigen.garnish on pVAC candidates | pVAC tiers; NeoFox computes the ~16 published features |
| Reproducible end-to-end | nextNEOpi (HLA + VEP + pVACseq + NeoFox + LOHHLA) | Wires the whole chain including LOHHLA and purity |
| Final candidate selection | pVACview manual re-tiering | Tiers say WHY a candidate failed; human triage |

## Run VEP, Then pVACseq

**Goal:** Produce the VEP annotation pVACseq actually consumes, then call neoantigens.

**Approach:** Run VEP with the Wildtype + Frameshift plugins and a protein FASTA; annotate expression and read counts with VAtools; supply a phased proximal-variants VCF; then `pvacseq run` with the patient HLA and sane filters.

```bash
pvacseq install_vep_plugin $VEP_PLUGINS          # installs Wildtype + Frameshift
vep --input_file somatic.vcf --output_file somatic.vep.vcf --format vcf --vcf \
    --symbol --terms SO --tsl --hgvs --fasta GRCh38.fa --offline --cache --dir_cache $VEP_CACHE \
    --plugin Frameshift --plugin Wildtype --pick

vcf-expression-annotator somatic.vep.vcf kallisto.tsv custom transcript -s TUMOR \
    --id-column target_id --expression-column tpm -o somatic.vep.expn.vcf

pvacseq run somatic.vep.expn.vcf TUMOR \
    "HLA-A*02:01,HLA-A*24:02,HLA-B*07:02,HLA-B*44:02,HLA-C*07:02,DRB1*01:01" \
    all_class_i pvac_out/ \
    -e1 8,9,10,11 --iedb-install-directory $IEDB \
    --phased-proximal-variants-vcf phased.vcf.gz \
    --normal-vaf 0.02 --tdna-vaf 0.25 --trna-vaf 0.25 --expn-val 1.0 -t 8
```
Key flags: `-e1/-e2` epitope lengths; `-b/--binding-threshold` (default 500 nM); `--percentile-threshold` (recommend 2); `-m/--top-score-metric` median|lowest; `--allele-specific-binding-thresholds` (preferred over flat 500 nM); `--net-chop-method`/`--netmhc-stab` (processing + stability features).

## Compute Agretopicity (DAI) Correctly

**Goal:** Quantify how much more foreign the mutant looks than its wild-type counterpart.

**Approach:** Agretopicity (the fitness-model amplitude; Łuksza 2017) is the WT/MT binding ratio. A high value means the mutant binds while the WT does not — the surface is new to the immune system, so reactive T cells were not deleted in the thymus. The original differential agretopicity index (DAI; Duan 2014) is the difference form; both forms share the traps below. Requires the matched WT peptide (the Wildtype plugin), so pVACbind cannot compute it.

```python
import pandas as pd

def add_agretopicity(df, wt='Median WT IC50 Score', mt='Median MT IC50 Score'):
    '''Agretopicity (amplitude) = IC50_WT / IC50_MT (ratio > 1 = mutant binds better -> favorable).
    Anchor-position mutations inflate DAI without changing the TCR-facing surface, so
    pair DAI with anchor evaluation rather than trusting it alone.'''
    out = df.copy()
    out['agretopicity'] = out[wt] / out[mt]
    out['dai_favorable'] = out['agretopicity'] > 1
    return out
```

## Drop Candidates on Lost HLA Alleles (LOHHLA)

**Goal:** Remove neoantigens predicted to be presented by an HLA allele the tumor has deleted.

**Approach:** HLA LOH is an immune-escape mechanism in ~40% of NSCLC (McGranahan 2017) and is invisible to binding/expression/clonality filters. Run LOHHLA (or a subclonal-sensitive equivalent like DASH) with the HLA type and tumor purity/ploidy, then filter the aggregate report. This step sits outside pVACtools and errors silently if skipped.

```python
def drop_lost_allele_candidates(df, lost_alleles, allele_col='HLA Allele'):
    '''lost_alleles: set of alleles called as LOH-lost by LOHHLA. A peptide assigned
    to a lost allele is not weakly presented - it is not presented at all.'''
    return df[~df[allele_col].isin(set(lost_alleles))].copy()
```

## Per-Method Failure Modes

### HLA LOH silent invalidation
**Trigger:** ranking candidates without running LOHHLA. **Mechanism:** tumor deletes the haplotype that would present its neoantigens; upstream signals all look fine. **Symptom:** beautiful candidates on an absent allele. **Fix:** mandatory separate LOHHLA step; drop lost-allele candidates.

### Subclonal mis-tiering from raw VAF
**Trigger:** using VAF as clonality without purity/CN correction. **Mechanism:** clonality needs cancer cell fraction (CCF = f(VAF, purity, local CN)). **Symptom:** clonal mutation in low-purity sample read as subclonal (and vice versa in amplified regions). **Fix:** estimate purity (ASCAT/Sequenza/PURPLE) and CCF (PyClone) before tiering.

### Unphased proximal variants
**Trigger:** running pVACseq with only the somatic VCF when nearby in-cis variants exist. **Mechanism:** the translated peptide depends on both variants on the haplotype. **Symptom:** predicted/synthesized peptides the tumor never makes. **Fix:** supply `--phased-proximal-variants-vcf` (merge somatic+germline, phase with WhatsHap/GATK).

### Silent filter pass-through
**Trigger:** expression/VAF/coverage filters set but the values never annotated into the VCF. **Mechanism:** the filter passes everything when the field is absent. **Symptom:** unexpressed/low-coverage candidates in the output. **Fix:** annotate with VAtools first; confirm the FORMAT/INFO fields exist.

### Frameshift/fusion over-trust and MS-gap
**Trigger:** treating frameshift/fusion presentation scores like canonical SNV scores. **Mechanism:** EL/MS training is dominated by canonical 8-11mers from point mutations. **Symptom:** narrow-looking CIs on a poorly-supported class; no MS evidence misread as absence. **Fix:** widen confidence on these high-value classes; build a personalized MS search DB before claiming MS absence.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| Binding threshold 500 nM (default) | pVACseq `-b` default | Entry gate only; prefer `--allele-specific-binding-thresholds` / %Rank |
| `--normal-vaf` 0.02 | pVACseq default | Germline-leak guard (esp. tumor-only-ish setups) |
| `--tdna-vaf` / `--trna-vaf` 0.25 | pVACseq default | Min tumor DNA/RNA VAF to keep |
| `--expn-val` 1.0 TPM | pVACseq default | Unexpressed mutation is not a neoantigen |
| Coverage normal/tDNA/tRNA 5/10/10 | pVACseq defaults | Below this, VAF/clonality calls are noise |
| Clonal CCF ~1 (clonal >> subclonal) | McGranahan 2016 | Subclonal targets select for resistant majority |
| Agretopicity/DAI > 1 favorable | Łuksza 2017; TESLA | WT binds poorly -> surface not tolerized |
| Validate beyond tier 1 | Wells 2020; Ott/Sahin 2017 | Predicted != presented != immunogenic |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| pVACseq misses frameshifts / no WT peptide | Used Downstream plugin or omitted Wildtype | Install Wildtype + Frameshift (Downstream dropped in pVACtools 2.0) |
| Everything passes the expression filter | TPM never annotated | `vcf-expression-annotator` before run |
| Non-overlapping neoantigen lists across labs | Different HLA typers/resolution | Type at 4-digit; reconcile DNA vs RNA; WES preferred |
| Candidates on a deleted allele | LOHHLA skipped | Run LOHHLA; drop lost-allele candidates |
| Wrong mutant peptide sequence | Proximal variants unphased | `--phased-proximal-variants-vcf` |
| Subclonal target promoted | Ranked by VAF/IC50, no CCF | Estimate purity + CCF; respect the Subclonal tier |

## References

- Wells DK, van Buuren MM, Dang KK, et al. 2020. Key parameters of tumor epitope immunogenicity revealed through a consortium approach improve neoantigen prediction (TESLA). *Cell* 183(3):818-834.
- Hundal J, Kiwala S, McMichael J, et al. 2020. pVACtools: a computational toolkit to identify and visualize cancer neoantigens. *Cancer Immunology Research* 8(3):409-420.
- McGranahan N, Furness AJS, Rosenthal R, et al. 2016. Clonal neoantigens elicit T cell immunoreactivity and sensitivity to immune checkpoint blockade. *Science* 351(6280):1463-1469.
- McGranahan N, Rosenthal R, Hiley CT, et al. 2017. Allele-specific HLA loss and immune escape in lung cancer evolution (LOHHLA). *Cell* 171(6):1259-1271.
- Łuksza M, Riaz N, Makarov V, et al. 2017. A neoantigen fitness model predicts tumour response to checkpoint blockade immunotherapy. *Nature* 551:517-520.
- Balachandran VP, Łuksza M, Zhao JN, et al. 2017. Identification of unique neoantigen qualities in long-term survivors of pancreatic cancer. *Nature* 551:512-516.
- Richman LP, Vonderheide RH, Rech AJ. 2019. Neoantigen dissimilarity to the self-proteome predicts immunogenicity and response to immune checkpoint blockade. *Cell Systems* 9(4):375-382.
- Wood MA, Nguyen A, Struck AJ, et al. 2020. neoepiscope improves neoepitope prediction with multivariant phasing. *Bioinformatics* 36(3):713-720.
- Lang F, Riesgo-Ferreiro P, Löwer M, Sahin U, Schrörs B. 2021. NeoFox: annotating neoantigen candidates with neoantigen features. *Bioinformatics* 37(22):4246-4247.
- Ott PA, Hu Z, Keskin DB, et al. 2017. An immunogenic personal neoantigen vaccine for patients with melanoma. *Nature* 547:217-221.

## Related Skills

- immunoinformatics/mhc-binding-prediction - the binding step (the solved, low-leverage part); EL abundance bias bites here
- immunoinformatics/mhc-class-ii-prediction - class II neoantigens for CD4 help (compounded uncertainty)
- immunoinformatics/immunogenicity-scoring - quality ranking (DAI, foreignness, dissimilarity) of the candidate list
- clinical-databases/hla-typing - the genotype substrate; wrong calls poison everything
- clinical-databases/somatic-signatures - clonal neoantigen burden predicts ICI response (McGranahan 2016)
- variant-calling/variant-calling - upstream somatic SNV/indel calls
- workflows/neoantigen-pipeline - the end-to-end orchestration
<!-- END FILE: immunoinformatics/neoantigen-prediction/SKILL.md -->

## 子目录：immunoinformatics/tcr-epitope-binding

<!-- BEGIN FILE: immunoinformatics/tcr-epitope-binding/SKILL.md -->
---
name: bio-immunoinformatics-tcr-epitope-binding
description: Infer or annotate TCR antigen specificity by unsupervised clustering (TCRdist/tcrdist3, GLIPH2, clusTCR, GIANA) and database lookup (VDJdb, IEDB, McPAS-TCR), and rank candidates with supervised predictors (ERGO-II, NetTCR-2.x, pMTnet) under explicit caveats. Encodes the central truth that general TCR-epitope prediction for UNSEEN epitopes essentially does not work (collapses to near-random; IMMREP22, Grazioli 2022) because labeled data is dominated by a few immunodominant epitopes and there is no true negative set — so clustering for discovery is the honest task and de-novo binding needs wet-lab validation. Use when annotating TCR specificity or grouping a repertoire. Epitope/MHC context lives in mhc-binding-prediction.
tool_type: python
primary_tool: tcrdist3
---

## Version Compatibility

Reference examples tested with: tcrdist3 0.2+, pandas 2.2+, scipy 1.12+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

Notes specific to this skill: tcrdist3 expects IMGT-style columns (`cdr3_b_aa`, `v_b_gene`, `j_b_gene`, and the `_a_` analogs, plus `count`). Tools disagree on whether CDR3 keeps the leading Cys / trailing Phe-Trp — a common silent input mismatch. Supervised predictors (ERGO-II, NetTCR, pMTnet) are separate repos with pretrained weights; their reported AUCs depend heavily on the train/test split and negative-sampling scheme. Re-verify before trusting any number.

# TCR-Epitope Binding

**"What antigen does this TCR recognize / which TCRs share specificity?"** -> Annotate specificity by clustering + database lookup; predict de-novo binding only as a validation-bound hypothesis.
- Python: `tcrdist3` (TCRrep distance + meta-clonotypes), GLIPH2, clusTCR, GIANA for clustering
- Python: ERGO-II / NetTCR-2.x / pMTnet for supervised scoring (caveated); VDJdb/IEDB/McPAS-TCR for lookup

## The Single Most Important Modern Insight -- general prediction for unseen epitopes does not work; clustering does

Every supervised TCR-epitope predictor performs respectably on epitopes seen in training and collapses to near-random on epitopes it has never seen (Grazioli 2022; IMMREP22, Meysman 2023 across 23 models). The cause is the data, not the architecture: the labeled TCR-pMHC universe is dominated by a few immunodominant epitopes (NLVPMVATV/CMV, GILGFVFTL/influenza M1, SARS-CoV-2 spike), so a model learns "is this an anti-CMV TCR" rather than the rules of TCR-peptide docking. Compounding this, there is no true negative set — experiments report binders, and absence of a measured non-binder is not non-binding — so every supervised model manufactures negatives, and that choice dominates the reported metric more than the architecture (Dens 2023). The honest, defensible task is unsupervised specificity clustering: "these TCRs are sequence-similar enough to likely share a specificity," a discovery statement used within one dataset and propagated by guilt-by-association to a known member. Clustering is honest because it never extrapolates into unseen-epitope space; per-pair prediction is dishonest when it pretends to. Route the user to the honest task and refuse to let a supervised per-pair probability substitute for a tetramer.

## Tool Taxonomy

| Tool | Citation | Task | Input | Note |
|------|----------|------|-------|------|
| TCRdist / tcrdist3 | Dash 2017; Mayer-Blackwell 2021 | Clustering (distance) | CDR3 + V/J, both chains | Multi-loop distance, 3x weight on CDR3; meta-clonotypes |
| GLIPH2 | Huang 2020 | Clustering (global + motif) | CDR3β + V/J + HLA | Predicts restricting allele; background-repertoire dependent |
| clusTCR | Valkiers 2021 | Clustering (Faiss+MCL) | CDR3β | Scales to millions; speed for specificity |
| GIANA / iSMART | Zhang 2021; Zhang 2020 | Clustering (fast) | CDR3β | Small high-specificity clusters |
| ERGO-II | Springer 2021 | Supervised prediction | CDR3β(+α,V,J,MHC) | Degrades gracefully; seen-epitope only |
| NetTCR-2.x | Montemurro 2021 | Supervised prediction | paired CDR3α+β | Paired beats single-chain; ~150 pos/epitope needed |
| pMTnet / PanPep | Lu 2021; Gao 2023 | Supervised, neoantigen-aimed | CDR3β + peptide + MHC | Zero-shot claims need skepticism |

## Reference Databases (training set AND lookup table)

| Database | Citation | Content | Caveat |
|----------|----------|---------|--------|
| VDJdb | Shugay 2018; Bagaev 2020 | Curated TCR-pMHC with confidence 0-3 | Filter on confidence; skewed to HLA-A*02:01 |
| IEDB | Vita 2019 | TCR + pMHC assays | The corpus most predictors draw on |
| McPAS-TCR | Tickotsky 2017 | Pathology-organized (infection/cancer/autoimmune) | Human + mouse |
| 10x dextramer | Zhang 2021 (Sci Adv) | Largest paired-chain set, 4 donors | Labels are threshold calls, not gold; multiplets/background |

## Decision Tree by Scenario

| Scenario | Recommended | Why |
|----------|-------------|-----|
| Have known specificities (tetramer sort / DB hits) | Cluster (tcrdist3/GLIPH2) + lookup, propagate labels | The honest, bounded question |
| Group a repertoire by likely shared specificity | tcrdist3 or clusTCR within one cohort | Discovery within dataset; keep HLA as covariate |
| Truly de-novo novel epitope (e.g. neoantigen) | Rank with pMTnet/PanPep, label as hypothesis, validate | Prediction does not generalize; tetramer/functional assay decides |
| Millions of CDR3s | clusTCR (Faiss+MCL) | Speed at modest specificity cost |
| Predict restricting HLA from sequence | GLIPH2 | Infers allele from cross-donor co-occurrence |
| "Does this TCR bind peptide X?" for unseen X | No reliable computational answer | State plainly; there is no third branch |

## Cluster TCRs by Specificity (tcrdist3)

**Goal:** Group TCRs likely to share an antigen, for discovery within one cohort.

**Approach:** Build a TCRrep (which computes the position-weighted multi-loop distance, 3x on CDR3), then cluster the pairwise matrix and annotate clusters containing a known-specificity member. Keep HLA as an explicit covariate — the same CDR3 on a different allele is a different specificity.

```python
from tcrdist.repertoire import TCRrep
from scipy.cluster.hierarchy import linkage, fcluster
from scipy.spatial.distance import squareform

def cluster_tcrs(df, max_dist=50):
    '''df needs IMGT columns: cdr3_b_aa, v_b_gene, j_b_gene (+ _a_ analogs), count.
    Returns cluster labels; annotate clusters that contain a database/tetramer hit.'''
    tr = TCRrep(cell_df=df, organism='human', chains=['beta'])
    condensed = squareform(tr.pw_beta, checks=False)
    return fcluster(linkage(condensed, method='average'), t=max_dist, criterion='distance')
```

## Annotate by Database Lookup

**Goal:** Assign specificity to TCRs that match known TCR-pMHC pairs.

**Approach:** Match exactly or near-exactly against VDJdb/IEDB/McPAS, filtering VDJdb on its confidence score, and report the database hit and HLA restriction driving each annotation — not a per-pair probability dressed as certainty.

```python
import pandas as pd

def lookup_vdjdb(query_cdr3b, vdjdb, min_confidence=1):
    '''Exact CDR3b match against a confidence-filtered VDJdb. Near-matches (edit
    distance 1) belong to the clustering route, not a binding claim.'''
    db = vdjdb[vdjdb['vdjdb.score'] >= min_confidence]
    hits = db[db['cdr3'].isin(set(query_cdr3b))]
    return hits[['cdr3', 'antigen.epitope', 'antigen.species', 'mhc.a']]
```

## Per-Method Failure Modes

### Unseen-epitope collapse
**Trigger:** using a supervised model on an epitope absent from training. **Mechanism:** models learn a few well-sampled specificities, not docking rules. **Symptom:** great benchmark AUC, near-random on novel epitopes. **Fix:** route de-novo questions to ranking-plus-validation; never report a confident per-pair call.

### Negative-sampling artifact
**Trigger:** trusting a headline AUC. **Mechanism:** manufactured negatives (shuffled or random-TCR) create artificial separability; repeated-negative leakage lets the model count TCR frequency. **Symptom:** AUC > 0.85 with no discussion of negatives/splits. **Fix:** read the negative-sampling sentence first; require epitope-disjoint evaluation.

### CDR3β-only ceiling
**Trigger:** strong claims from a β-only model. **Mechanism:** alpha chain and V/J carry heavy signal; bulk β-only is information-poor. **Symptom:** big AUC from the least informative input (i.e. from artifacts). **Fix:** prefer paired-chain data; add V/J; discount β-only headline numbers.

### Clustering confounds (HLA + background)
**Trigger:** pooling multi-donor repertoires and clustering naively. **Mechanism:** same CDR3 on different HLA is a different specificity; motif enrichment depends on the reference background. **Symptom:** merged unrelated TCRs; spurious "enriched" motifs. **Fix:** cluster within a coherent cohort, keep HLA as a covariate, match the background repertoire.

### Metrics that lie
**Trigger:** a single global or per-epitope-averaged AUC. **Mechanism:** averaging over seen epitopes hides the novel-epitope collapse. **Symptom:** one trustworthy-looking number, no split description. **Fix:** demand epitope-disjoint (TPP-II/III) splits reported per-epitope with a peptide-distance decay analysis.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| ~150 distinct binders per epitope | Montemurro 2021 | Below this a per-epitope supervised model is unreliable |
| VDJdb confidence >= 1 (use 2-3 for high) | Shugay 2018 | Low-confidence records are weakly supported |
| 10x call: UMI > 10 and > 5x top negative-control | Zhang 2021 | Dextramer labels are threshold calls, not gold |
| Evaluate on epitope-disjoint split | IMMREP22; Grazioli 2022 | Seen-epitope/shuffled splits hide the collapse |
| tcrdist CDR3 weight 3x other loops | Dash 2017 | CDR3 is the chief specificity determinant |
| Paired α+β > single chain | Montemurro 2021; IMMREP22 | β-only caps achievable accuracy |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| Confident de-novo binding call | Supervised model on unseen epitope | Reframe as hypothesis; validate by tetramer/assay |
| Irreproducible published AUC | Leaky split / negative-sampling bias | Re-evaluate on epitope-disjoint clean split |
| Merged unrelated TCR clusters | Mixed-HLA pooling | Cluster within cohort; HLA covariate |
| Input not recognized by tool | CDR3 Cys/Phe-Trp convention mismatch | Match the tool's IMGT trimming convention |
| Over-trusted 10x labels | Treated threshold calls as gold | Require replicate/donor concordance |
| Structure "solves" it | AlphaFold hype on a hard interface | Use TCRdock to rank/rationalize candidates, not screen |

## References

- Dash P, Fiore-Gartland AJ, Hertz T, et al. 2017. Quantifiable predictive features define epitope-specific T cell receptor repertoires (TCRdist). *Nature* 547(7661):89-93.
- Mayer-Blackwell K, Schattgen S, Cohen-Lavi L, et al. 2021. TCR meta-clonotypes for biomarker discovery with tcrdist3. *eLife* 10:e68605.
- Glanville J, Huang H, Nau A, et al. 2017. Identifying specificity groups in the T cell receptor repertoire (GLIPH). *Nature* 547(7661):94-98.
- Huang H, Wang C, Rubelt F, Scriba TJ, Davis MM. 2020. Analyzing the M. tuberculosis immune response by T-cell receptor clustering with GLIPH2. *Nature Biotechnology* 38:1194-1202.
- Valkiers S, Van Houcke M, Laukens K, Meysman P. 2021. clusTCR: a Python interface for rapid clustering of large sets of CDR3 sequences. *Bioinformatics* 37(24):4865-4867.
- Zhang H, Zhan X, Li B. 2021. GIANA allows computationally-efficient TCR clustering and multi-disease repertoire classification by isometric transformation. *Nature Communications* 12:4699.
- Springer I, Tickotsky N, Louzoun Y. 2021. Contribution of T cell receptor alpha and beta CDR3, MHC typing, V and J genes to peptide binding prediction (ERGO-II). *Frontiers in Immunology* 12:664514.
- Montemurro A, Schuster V, Povlsen HR, et al. 2021. NetTCR-2.0 enables accurate prediction of TCR-peptide binding using paired TCRα and β sequence data. *Communications Biology* 4:1060.
- Lu T, Zhang Z, Zhu J, et al. 2021. Deep learning-based prediction of the T cell receptor-antigen binding specificity (pMTnet). *Nature Machine Intelligence* 3:864-875.
- Meysman P, Barton J, Bravi B, et al. 2023. Benchmarking solutions to the T-cell receptor epitope prediction problem: IMMREP22 workshop report. *ImmunoInformatics* 9:100024.
- Grazioli F, Mösch A, Machart P, et al. 2022. On TCR binding predictors failing to generalize to unseen peptides. *Frontiers in Immunology* 13:1014256.
- Dens C, Bittremieux W, Affaticati F, Laukens K, Meysman P. 2023. The pitfalls of negative data bias for the T-cell epitope specificity challenge. *Nature Machine Intelligence* 5:1063-1065.
- Shugay M, Bagaev DV, Zvyagin IV, et al. 2018. VDJdb: a curated database of T-cell receptor sequences with known antigen specificity. *Nucleic Acids Research* 46(D1):D419-D427.
- Bradley P. 2023. Structure-based prediction of T cell receptor:peptide-MHC interactions (TCRdock). *eLife* 12:e82813.

## Related Skills

- immunoinformatics/mhc-binding-prediction - the pMHC context a TCR recognizes (HLA restriction)
- immunoinformatics/neoantigen-prediction - de-novo neoantigen TCRs are the unseen-epitope case where prediction fails
- tcr-bcr-analysis/mixcr-analysis - upstream TCR repertoire extraction from sequencing
- single-cell/clustering - paired single-cell TCR data and embedding-based grouping
- workflows/tcr-pipeline - end-to-end repertoire processing
<!-- END FILE: immunoinformatics/tcr-epitope-binding/SKILL.md -->

<!-- END CATEGORY: immunoinformatics -->

