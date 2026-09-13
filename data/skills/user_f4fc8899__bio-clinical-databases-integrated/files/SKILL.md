---
slug: bio-clinical-databases-integrated
version: 1.0.1
displayName: "临床数据库 / Clinical database querying"
name: bio-clinical-databases-integrated
summary: "中文：临床数据库综合技能，整合 12 个相关专题，覆盖临床数据库查询：ClinVar、gnomAD、dbSNP、PharmGKB、HLA分型、PRS、肿瘤突变负荷。 English: Integrated Clinical database querying skill covering 12 related topics, including Clinical database querying: ClinVar, gnomAD, dbSNP, PharmGKB, HLA typing, polygenic risk scores, tumor mutational burden."
description: "中文：这是一个面向临床数据库的综合生物信息学 Skill，整合当前分类下 12 个相关专题能力。它用于根据研究问题、数据类型和分析阶段，选择合适的方法与工具，规划从输入检查、预处理、核心分析到质量控制、统计解释和结果报告的完整流程。重点覆盖：临床数据库查询：ClinVar、gnomAD、dbSNP、PharmGKB、HLA分型、PRS、肿瘤突变负荷。当用户提供相关实验数据、测序结果、表格或研究问题时，它会帮助判断分析目标与前置条件，给出工具选择、关键参数、输入输出、常见失败原因、结果解读和可复现建议。主要工具包括：MSIsensor-pro, PGS Catalog Calculator, PharmCAT。该 Skill 提供分析设计与实施指导，不替代对具体数据质量、生物学背景和最终结论的人工审查。 English: This is an integrated bioinformatics Skill for Clinical database querying, combining 12 related topic areas. It helps users choose appropriate methods and tools based on the research question, data type, and analysis stage, and plan an end-to-end workflow from input validation and preprocessing through core analysis, quality control, statistical interpretation, and reporting. It covers Clinical database querying: ClinVar, gnomAD, dbSNP, PharmGKB, HLA typing, polygenic risk scores, tumor mutational burden. For relevant experimental data, sequencing results, tables, or research questions, it clarifies prerequisites, recommends tools and parameters, describes expected inputs and outputs, explains common failure modes, and supports reproducible analysis. Primary tools include: MSIsensor-pro, PGS Catalog Calculator, PharmCAT. It provides methodological and implementation guidance; final data-quality assessment and biological conclusions still require human review."
---

# clinical-databases 分类 Skill 整合版

> 本文件整合同一主分类目录下 12 个子目录中的 SKILL.md 内容。
> 各子目录正文按原文保留，并通过标题和边界标记进行区分；源文件中的元数据块未被改写。

---

<!-- BEGIN CATEGORY: clinical-databases -->

## 子目录：clinical-databases/acmg-classification

<!-- BEGIN FILE: clinical-databases/acmg-classification/SKILL.md -->
---
name: bio-clinical-databases-acmg-classification
description: Applies ACMG/AMP 2015 framework with ClinGen SVI specifications, Tavtigian 2018/2020 Bayesian point system, Abou Tayoun 2018 PVS1 decision tree, Pejaver 2022 and Bergquist 2025 calibrated PP3/BP4 thresholds for REVEL/BayesDel/AlphaMissense, Brnich 2020 PS3/BS3 OddsPath, Walker 2023 SpliceAI splicing framework, and AMP/ASCO/CAP 2017 tumor tiers. Use when classifying germline variants P / LP / VUS / LB / B, applying VCEP-specific CSpec rules, computing Whiffin BS1, or assigning cancer Tier I-IV per Li 2017.
tool_type: python
primary_tool: requests
---

## Version Compatibility

Reference examples tested with: requests 2.31+, pandas 2.2+, AutoPVS1 (Xiang 2020), InterVar 2.2+, GeneBe 1.0+ (Stawiński 2024 *Clin Genet*). ACMG/AMP Bayesian point system is Tavtigian 2018 *Genet Med* / 2020 *Hum Mutat*. Pejaver 2022 *AJHG* PP3/BP4 calibrated thresholds. ClinGen Splicing Subgroup 2023 (Walker *AJHG*). v3.2 ACMG SF list (Miller 2023). The ACMG 2.0 framework is in development as of May 2026; not yet published.

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `<tool> --version`

If code throws ImportError, AttributeError, or TypeError, introspect the installed package and adapt the example to match the actual API rather than retrying. VCEP-specific CSpec rules override default ACMG application; the authoritative directory is `https://cspec.genome.network/cspec/ui/svi/all`.

# ACMG/AMP Variant Classification Framework

**'Classify this variant per ACMG/AMP'** -> Apply 28-criterion framework using Tavtigian point system; gate on ClinGen SVI specifications and VCEP-specific overrides; assign P / LP / VUS / LB / B classification with evidence trail.

- Python (automated): GeneBe API `https://api.genebe.net/cloud/api-public/v1/variant`
- Python (rule-based): InterVar -> `python InterVar.py -i input.vcf -b hg38 --table_annovar table_annovar.pl`
- Web tools: VarSome (commercial), Franklin/Genoox (commercial), ClinGen VCI (gold standard for SVI)
- Citation: Richards 2015 *Genet Med* 17:405 (original framework); Tavtigian 2020 *Hum Mutat* 41:1734 (point system)

## The Tavtigian Bayesian Point System: The Engine Inside All Modern Classifiers

Richards 2015 specified 28 criteria with strength labels (Supporting / Moderate / Strong / Very Strong); combination rules produced P / LP / VUS / LB / B. **Tavtigian 2018/2020 demonstrated this framework is mathematically a Bayesian classifier and proposed the naturally-scaled point system that every modern automated classifier implements:**

| Strength | Points | Odds of pathogenicity |
|----------|--------|----------------------|
| Supporting | 1 | 2.08:1 |
| Moderate | 2 | 4.33:1 |
| Strong | 4 | 18.7:1 |
| Very Strong | 8 | 350:1 |

Benign codes are negative-signed. Final classification:

| Sum of points | Category |
|---------------|----------|
| >= 10 | **Pathogenic** |
| 6-9 | **Likely Pathogenic** |
| 0-5 | **VUS** |
| -1 to -6 | **Likely Benign** |
| <= -7 | **Benign** |

InterVar / GeneBe / VarSome / Franklin all implement Tavtigian point summation under the hood. Combinations never appearing in the 2015 combining rules (e.g., PVS1_VeryStrong + PM2_Supporting -> LP) emerge naturally from point arithmetic.

## PVS1 Decision Tree (Abou Tayoun 2018 *Hum Mutat* 39:1517)

PVS1 is the most consequential code: pathogenic Very Strong (8 points) for predicted loss-of-function in a gene where LoF is established disease mechanism. The 2018 decision tree refined PVS1 from a binary into a graded code based on:

1. **Variant type**: nonsense / frameshift / canonical +-1,2 splice / initiation codon / single-exon deletion / multi-exon deletion.
2. **NMD prediction**: variant in 5'-most exon OR >50bp upstream of last exon-exon junction -> NMD-triggered. Else truncated protein.
3. **Critical region**: removal of >10% of coding sequence OR removal of a critical functional domain.
4. **Alternative isoform**: does the variant affect a transcript expressed in disease-relevant tissue?

Output strengths:

| Output | Original Strength |
|--------|-------------------|
| PVS1_VeryStrong | Strongest (Very Strong) |
| PVS1_Strong | Strong |
| PVS1_Moderate | Moderate |
| PVS1_Supporting | Supporting |

**Subsumption rule** (Abou Tayoun 2018): PVS1 + PP3 -> only PVS1 counts (PP3 is subsumed). Same for PVS1 + PM4.

**>15 VCEP-specific PVS1 trees exist** as of 2024 (CDH1, ENIGMA BRCA1/2, FH LDLR/APOB/PCSK9, InSiGHT MMR, RASopathies, hearing loss, hypertrophic cardiomyopathy, Rett/Angelman, etc.). The automated implementation is **AutoPVS1** (Xiang 2020).

## Pejaver 2022 PP3/BP4 Calibrated Thresholds (the load-bearing 2024+ calibration)

Pejaver 2022 *AJHG* 109:2163 Bayesian-calibrated 13 missense predictors to PP3/BP4 strength levels using ClinVar P/B variants with leave-one-gene-out cross-validation.

| Predictor | BP4_Strong | BP4_Moderate | BP4_Supporting | PP3_Supporting | PP3_Moderate | PP3_Strong | Fails when |
|-----------|-----------|--------------|----------------|----------------|--------------|------------|-----------|
| **REVEL** | <= 0.016 | <= 0.183 | <= 0.290 | >= 0.644 | >= 0.773 | >= 0.932 | Stacked with BayesDel/VEST4 (training overlap; double-counting) |
| **BayesDel (no AF)** | n/a | <= -0.36 | <= -0.18 | >= 0.13 | >= 0.27 | >= 0.50 | No BP4_Strong reached; combine no-AF version with PM2_Supporting |
| **VEST4** | n/a | <= 0.302 | <= 0.449 | >= 0.764 | >= 0.861 | >= 0.965 | No BP4_Strong reached; indels (missense-trained); regulatory variants |
| **MutPred2** | (Pejaver 2022) | -- | -- | -- | -- | -- | Genes with sparse MAVE training data |
| **AlphaMissense** | NOT ClinGen-endorsed | -- | -- | Use as supporting only | -- | NOT ClinGen-endorsed | Developer threshold 0.564 misapplied as PP3 |

**The numbers to memorize: REVEL >= 0.932 = PP3_Strong; REVEL <= 0.016 = BP4_Strong (<= 0.003 BP4_VeryStrong); the 0.290-0.644 band is indeterminate (no criterion).**

**AlphaMissense calibration** (Bergquist 2025 *Genet Med* 27:101402, ClinGen SVI; originally Bergquist et al. bioRxiv 2024.09.17): this ClinGen SVI calibration extends the graded PP3/BP4 options to AlphaMissense, reaching **PP3_Strong** and at least **BP4_Moderate**. **Critical:** the developer-recommended 0.564 threshold is NOT the calibrated PP3 threshold; verify the current ClinGen SVI recommendation for the exact score cutoffs before applying.

**Do not stack predictors.** REVEL, BayesDel, VEST4 share ClinVar/HGMD training data; using REVEL >= 0.773 AND BayesDel >= 0.27 to claim "two independent moderate hits" is double-counting. Pejaver 2022 explicitly recommends using ONE predictor per variant.

## PM2_Supporting (ClinGen SVI 2020)

The original PM2 ("absent from controls") was over-weighted. SVI 2020 downgraded to **PM2_Supporting** (1 point, not 2). Mechanism: most rare variants are benign. Empirical recalibration showed ~6 variants per gene downgrade from LP to VUS when PM2 -> Supporting. Many 2017-2019 LP curations require re-classification post-SVI 2020 update.

## PS3/BS3 Functional Evidence (Brnich 2020 *Genome Med* 12:3)

OddsPath framework; the four-step SOP:

1. Define disease mechanism for the gene.
2. Evaluate assay class (e.g., MAVE, biochemical, animal model).
3. Evaluate specific assay instance (controls, replicate consistency).
4. Apply per-variant.

OddsPath calibration mapping to ACMG strengths:

| OddsPath | Pathogenic strength | Benign strength |
|----------|--------------------:|----------------:|
| > 18.7 | Very Strong | n/a |
| 4.3 - 18.7 | Strong | -- |
| 2.1 - 4.3 | Moderate | -- |
| 1.2 - 2.1 | Supporting | (mirror) |

**MAVEdb deep-mutational scans** with >=11 controls (>=5 P/LP + >=5 B/LB) can yield up to PS3_Strong/BS3_Strong via OddsPath calibration. This is the entry point for MAVE/saturation-mutagenesis evidence into ACMG.

**Default-Strong PS3 application is increasingly over-strengthening** without OddsPath calibration; ClinGen SVI recommends moving toward PS3_Moderate as default unless OddsPath > 4.3.

## ClinGen SVI Splicing Subgroup 2023 (Walker *AJHG* 110:1046)

**SpliceAI is the recommended primary splicing tool.** Calibrated thresholds:

| SpliceAI DS_max | Strength (Walker 2023: computational splice codes applied at Supporting weight) |
|-----------------|----------|
| >= 0.2 | PP3_Supporting (minimum threshold for ANY splicing PP3) |
| 0.1 - 0.2 | Indeterminate (no criterion) |
| <= 0.1 | BP4_Supporting |

SpliceAI prediction alone does NOT reach PP3_Strong; strength escalation requires experimental/RNA splicing evidence (PS3) or the repurposed PVS1 route.

**SpliceVault / 300K-RNA** (Dawes 2023 *Nat Genet* 55:324): does NOT predict whether a variant is splice-altering; predicts WHAT the aberrant transcript will be (which exon skips, which cryptic site activates). 96% sensitivity for exon-skipping; 86% for cryptic site activation in 140 clinical RNA-tested cases. Critical for PVS1 application to splice variants because PVS1 depends on whether the aberrant transcript triggers NMD.

**Pangolin** (Zeng 2022 *Genome Biol* 23:103): SpliceAI improvement for cryptic donor sites; not yet ClinGen-endorsed but increasingly used as tiebreaker.

## BS1 / BA1 (Whiffin Max-Credible-AF)

BA1 default: AF > 5% in non-bottleneck group per ClinGen SVI; VCEP-specific overrides (Hearing Loss VCEP uses 0.5% AR).

BS1 gene-specific: `(prevalence x heterogeneity x allelic-contribution) / (penetrance x 2)` from Whiffin 2017 *Genet Med* 19:1151. Compare against gnomAD `grpmax_faf95`.

See `clinical-databases/gnomad-frequencies` for FAF95 details.

## ClinGen VCEP CSpec Hierarchy

| Layer | Authority | Application |
|-------|-----------|-------------|
| Generic ACMG/AMP 2015 | Richards 2015 | Default fallback |
| ClinGen SVI specifications | SVI Working Group | Overrides generic for all genes (PM2 -> Supporting; AutoPVS1 trees; etc.) |
| VCEP-specific CSpec | Gene/disease-specific expert panel | Overrides SVI for that gene-disease |

**ClinGen VCEP CSpec authoritative registry:** `https://cspec.genome.network/cspec/ui/svi/all`. ~80-90 VCEPs as of 2025. Examples:
- Hearing Loss VCEP: PM2 -> supporting default; PS3 thresholds upgraded for OTOF; BA1 lowered to 0.5% AR.
- ENIGMA BRCA1/2 VCEP: gene-specific PVS1 trees with NMD escape rules; PS4 case-control thresholds.
- Inherited Cardiac Conditions VCEP: gene-specific PS4 (5+ unrelated probands for PS4_Supporting).

**Apply VCEP CSpec when one exists.** Generic ACMG with no VCEP awareness is unreliable for many genes.

## Cancer Somatic Framework (Li 2017 *J Mol Diagn* 19:4)

AMP/ASCO/CAP somatic variant interpretation; four tiers:

| Tier | Definition | Action |
|------|-----------|--------|
| **Tier I-A** | FDA-approved drug for same tumor type with this biomarker | On-label therapy |
| **Tier I-B** | Professional guidelines (NCCN, ESMO) | Standard-of-care |
| **Tier II-C** | FDA drug in different tumor type (off-label) | Basket trials |
| **Tier II-D** | Preclinical / investigational | Research |
| **Tier III** | VUS-somatic | Watch list |
| **Tier IV** | Benign-somatic | Filter out |

**Knowledgebases:** OncoKB (MSKCC; Chakravarty 2017), CIViC (Griffith 2017 *Nat Genet* 49:170), CGI (Tamborero 2018), JAX-CKB, COSMIC. **OncoKB Levels** (1-4 therapeutic) map to AMP tiers loosely.

The **Variant Interpretation for Cancer Consortium (VICC) Meta-Knowledgebase** standards (2024-2025) harmonize across knowledgebases. ClinGen Somatic VCEPs are emerging (started 2022).

## Decision Tree by Variant Type

| Variant type | Recommended workflow |
|--------------|----------------------|
| Predicted LoF in known LoF-mechanism gene | AutoPVS1 decision tree -> PVS1_VeryStrong/Strong/Moderate/Supporting; check VCEP-specific PVS1 |
| Missense in known missense-pathogenic gene | Apply Pejaver 2022 PP3/BP4 calibrated thresholds; ONE predictor only |
| Splice variant | SpliceAI DS_max + SpliceVault for aberrant-transcript prediction; PP3_Supporting if DS_max >=0.2 (strength escalation needs RNA/experimental evidence) |
| Synonymous | SpliceAI for cryptic splice effect; synVep / PrimateAI synonymous extension |
| Variant in ACMG SF v3.2 gene | Apply full classification; flag P/LP for opt-in disclosure |
| Cancer somatic variant | AMP/ASCO/CAP 2017 Tier I-IV; cross-check OncoKB / CIViC |
| Variant in Limited gene-disease validity | ClinGen Strong/Definitive required for clinical action |
| Functional evidence available | Brnich 2020 PS3/BS3 OddsPath framework |
| Family segregation | PP1 / BS4 LOD score per Biesecker 2024 |
| In-trans observations (AR) | PM3 with ClinGen tabular scoring system |
| HGVS-c on alternative transcript | Re-evaluate on MANE Select |

## Standard Workflow: ACMG Classification

**Goal:** Apply ACMG/AMP framework to a candidate variant with proper SVI specifications and VCEP overrides.

**Approach:** Pull aggregated evidence; apply Pejaver-calibrated in-silico thresholds; check VCEP-specific CSpec; sum Tavtigian points.

```python
import requests
import pandas as pd


# Pejaver 2022 calibrated REVEL thresholds (one-predictor rule applies)
REVEL_THRESHOLDS = {
    'BP4_VeryStrong': (-float('inf'), 0.003),
    'BP4_Strong': (0.003, 0.016),
    'BP4_Moderate': (0.016, 0.183),
    'BP4_Supporting': (0.183, 0.290),
    # (0.290, 0.644) = indeterminate zone, no criterion applied
    'PP3_Supporting': (0.644, 0.773),
    'PP3_Moderate': (0.773, 0.932),
    'PP3_Strong': (0.932, float('inf'))
}

# Tavtigian point assignments (Tavtigian 2020 Hum Mutat)
STRENGTH_POINTS = {
    'PVS1_VeryStrong': 8, 'PVS1_Strong': 4, 'PVS1_Moderate': 2, 'PVS1_Supporting': 1,
    'PS1': 4, 'PS2': 4, 'PS3': 4, 'PS3_Moderate': 2, 'PS3_Supporting': 1, 'PS4': 4,
    'PM1': 2, 'PM2_Supporting': 1, 'PM3': 2, 'PM3_Strong': 4, 'PM3_VeryStrong': 8,
    'PM4': 2, 'PM5': 2, 'PM6': 2,
    'PP1': 1, 'PP1_Moderate': 2, 'PP1_Strong': 4,
    'PP2': 1, 'PP3_Supporting': 1, 'PP3_Moderate': 2, 'PP3_Strong': 4, 'PP4': 1, 'PP5': 1,
    # Benign codes (negative)
    'BA1': -100,  # Standalone benign
    'BS1': -4, 'BS2': -4, 'BS3': -4, 'BS3_Moderate': -2, 'BS3_Supporting': -1, 'BS4': -4,
    'BP1': -1, 'BP2': -1, 'BP3': -1,
    'BP4_Supporting': -1, 'BP4_Moderate': -2, 'BP4_Strong': -4, 'BP4_VeryStrong': -8,
    'BP5': -1, 'BP6': -1, 'BP7': -1
}


def classify_revel_pp3_bp4(revel_score):
    '''Map REVEL score to PP3/BP4 strength per Pejaver 2022.'''
    if revel_score is None:
        return None
    for code, (lo, hi) in REVEL_THRESHOLDS.items():
        if lo <= revel_score < hi:
            return code
    return None


def classify_alphamissense_supporting_only(am_score):
    '''AlphaMissense is currently supporting-only; ClinGen has not endorsed PP3 calibration.

    Cheng 2023 developer threshold 0.564 is NOT the Pejaver-style PP3 calibration.
    '''
    if am_score is None:
        return None
    if am_score >= 0.7:
        return 'PP3_Supporting'   # Tentative; ClinGen not endorsed
    if am_score <= 0.2:
        return 'BP4_Supporting'   # Tentative
    return None


def spliceai_to_acmg(ds_max):
    '''Walker 2023 SVI Splicing Subgroup framework.

    Computational SpliceAI codes are applied at Supporting weight.
    SpliceAI >= 0.20 -> PP3_Supporting (minimum for ANY splicing PP3).
    SpliceAI <= 0.1 -> BP4_Supporting.
    Prediction alone does not reach PP3_Strong; escalation needs RNA/experimental evidence.
    '''
    if ds_max is None:
        return None
    if ds_max >= 0.20:
        return 'PP3_Supporting'
    if ds_max <= 0.1:
        return 'BP4_Supporting'
    return None


def tavtigian_classify(criteria_assigned):
    '''Sum Tavtigian points and classify P / LP / VUS / LB / B.

    criteria_assigned: list of criterion strings (e.g., ['PVS1_VeryStrong', 'PM2_Supporting'])
    '''
    points = sum(STRENGTH_POINTS.get(c, 0) for c in criteria_assigned)
    if any(c == 'BA1' for c in criteria_assigned):
        return {'classification': 'Benign', 'points': points, 'rationale': 'BA1 standalone'}
    if points >= 10:
        category = 'Pathogenic'
    elif points >= 6:
        category = 'Likely Pathogenic'
    elif points >= 0:
        category = 'VUS'
    elif points >= -6:
        category = 'Likely Benign'
    else:
        category = 'Benign'
    return {'classification': category, 'points': points, 'criteria': criteria_assigned}


def genebe_classify(hgvs):
    '''Query GeneBe API (Stawiński 2024) for automated ACMG classification.

    GeneBe is open-source, Tavtigian-point-system-based, and performs comparably to
    VarSome (which is commercial, 82% ACMG criteria auto-application rate).
    '''
    r = requests.get(f'https://api.genebe.net/cloud/api-public/v1/variant',
                     params={'variant': hgvs, 'genome': 'hg38'},
                     timeout=30)
    r.raise_for_status()
    return r.json()


def whiffin_max_credible_af(prevalence, max_allelic_contribution=1.0,
                              max_genetic_contribution=1.0, penetrance=1.0):
    '''Compute gene-specific BS1 max-credible-AF (Whiffin 2017 Genet Med).

    Returns: max-credible per-allele frequency under dominant inheritance.
    For autosomal recessive, transform appropriately.
    '''
    return (prevalence * max_genetic_contribution * max_allelic_contribution) / (penetrance * 2)


def apply_bs1_ba1(grpmax_faf95, max_credible_af, ba1_threshold=0.05):
    '''Apply ClinGen SVI BS1/BA1 from gnomAD grpmax FAF95.'''
    if grpmax_faf95 is None or grpmax_faf95 == 0.0:
        return 'PM2_Supporting'
    if grpmax_faf95 > ba1_threshold:
        return 'BA1'
    if grpmax_faf95 > max_credible_af:
        return 'BS1'
    return None
```

## Per-Operation Failure Modes

**1. Stacking REVEL + BayesDel + VEST4 as independent evidence**
- Trigger: Apply PP3 from multiple predictors.
- Mechanism: Predictors share training data; double-counting.
- Symptom: Inflated PP3 strength; over-classified LP.
- Fix: Use ONE predictor per variant (Pejaver 2022).

**2. AlphaMissense PP3_Strong with developer 0.564 threshold**
- Trigger: Apply AlphaMissense >0.564 -> PP3_Strong.
- Mechanism: 0.564 is the developer-recommended likely-pathogenic threshold, NOT a calibrated PP3 cutoff; use the ClinGen SVI calibration (Bergquist 2025) score thresholds instead.
- Symptom: Over-application of PP3.
- Fix: Use AlphaMissense as supporting evidence only; defer to Pejaver-calibrated REVEL.

**3. PVS1 applied to nonsense variant in GoF gene**
- Trigger: Nonsense variant in SCN5A reported as PVS1 for LQT3.
- Mechanism: SCN5A has both LoF (Brugada) and GoF (LQT3) mechanisms. PVS1 should NOT apply if LoF is not the established mechanism.
- Symptom: Wrong classification; clinical action mis-directed.
- Fix: Check ClinGen gene-disease mechanism; apply PVS1 only when LoF is established.

**4. Generic ACMG instead of VCEP CSpec**
- Trigger: Apply default ACMG to a variant in a gene with VCEP-specific CSpec.
- Mechanism: VCEP CSpec overrides for the gene; e.g., Hearing Loss VCEP PM2 default = supporting, BA1 = 0.5%.
- Symptom: Wrong strength applied; misclassification.
- Fix: Check `https://cspec.genome.network/cspec/ui/svi/all` for active VCEP; apply gene-specific CSpec.

**5. PM2 at Moderate (pre-2020 SVI)**
- Trigger: Apply PM2 = Moderate (2 points) per 2015 rules.
- Mechanism: SVI 2020 downgraded to PM2_Supporting (1 point).
- Symptom: ~6 variants per gene over-strengthened LP.
- Fix: Use PM2_Supporting per current SVI.

**6. PS3 default Strong without OddsPath**
- Trigger: Apply PS3 = Strong without OddsPath calibration.
- Mechanism: Default PS3 = Strong over-strengthens; Brnich 2020 SOP requires OddsPath > 4.3 for Strong.
- Symptom: PS3-driven over-classification.
- Fix: Apply Brnich 2020 four-step OddsPath; default move to PS3_Moderate without OddsPath > 4.3.

**7. Synonymous treated as no impact**
- Trigger: Filter out synonymous variants from classification pipeline.
- Mechanism: Synonymous can disrupt splicing; SpliceAI captures this.
- Symptom: Pathogenic splice-disrupting synonymous missed.
- Fix: Always run SpliceAI on synonymous variants in disease genes; PP3_Supporting if DS_max >= 0.2.

**8. ClinVar P + ClinGen Limited validity**
- Trigger: Report variant P in gene with Limited gene-disease validity.
- Mechanism: ClinVar P is variant-level; gene-disease validity is upstream.
- Symptom: Mis-attribution to a non-disease gene.
- Fix: Apply ClinGen gene-disease validity gate (Moderate+ for clinical action); for Limited genes, require VCEP curation.

**9. Variant on wrong transcript**
- Trigger: HGVS-c on alt transcript; functional impact different on MANE Select.
- Mechanism: Tissue-specific isoform considerations; MANE Select 2024+ is clinical standard.
- Symptom: Wrong consequence prediction.
- Fix: Re-evaluate on MANE Select transcript; cross-check with VEP `--mane_select`.

## Reconciliation: When Tools Disagree

| Pattern | Likely cause | Action |
|---------|-------------|--------|
| GeneBe LP vs VarSome P | Different VCEP-specific application | Check VCEP CSpec; apply gene-specific rules |
| ClinVar P vs my classification VUS | Submission stale OR my evidence incomplete | Re-curate with current evidence; check ClinVar star + freshness |
| REVEL PP3_Strong vs SpliceAI BP4 | Variant has missense impact but no splice impact | Apply ONE predictor; if splice-altering, PVS1 trumps |
| PVS1 applies but ClinGen Limited validity | Variant-level vs gene-disease tension | Treat as candidate; require VCEP or strong functional evidence |
| ClinGen VCI vs automated tool | VCI is gold standard for expert curation | Trust VCI; automated tools approximate |
| AlphaMissense 0.564 dev call vs calibrated strength | Developer threshold not calibrated | Use the ClinGen SVI calibrated cutoffs (Bergquist 2025) |

## Quantitative Thresholds and Conventions

| Threshold | Convention | Source |
|-----------|-----------|--------|
| Tavtigian P | >= 10 points | Tavtigian 2020 |
| Tavtigian LP | 6-9 points | Tavtigian 2020 |
| Tavtigian VUS | 0-5 points | Tavtigian 2020 |
| Tavtigian LB | -1 to -6 | Tavtigian 2020 |
| Tavtigian B | <= -7 | Tavtigian 2020 |
| REVEL PP3_Strong | >= 0.932 | Pejaver 2022 |
| REVEL BP4_Strong | <= 0.016 | Pejaver 2022 |
| SpliceAI PP3 (Supporting) | >= 0.2 | Walker 2023 |
| SpliceAI BP4 (Supporting) | <= 0.1 | Walker 2023 |
| BA1 default | grpmax_faf95 > 5% | ClinGen SVI |
| BS1 | grpmax_faf95 > gene-specific max-credible-AF | Whiffin 2017 |
| PM2 -> PM2_Supporting | Always (post-SVI 2020) | SVI 2020 |
| PS3 OddsPath Strong | > 4.3 | Brnich 2020 |
| PVS1 LoF mechanism check | Required (do not apply if GoF) | Abou Tayoun 2018 |
| ACMG SF v3.2 | 81 genes | Miller 2023 |
| Cancer Tier I-A | FDA drug + same tumor + this biomarker | Li 2017 |

## Common Errors

| Symptom | Cause | Solution |
|---------|-------|----------|
| Over-application of PP3 | Multiple predictors stacked | ONE predictor only |
| AlphaMissense PP3_Strong from dev threshold | 0.564 not calibrated | Use Pejaver-style REVEL |
| LP variant in gene with Limited validity | No gene-disease gate | Apply ClinGen gene-disease validity |
| PVS1 in GoF gene | Wrong mechanism | Check ClinGen gene-disease mechanism |
| Non-VCEP rule for VCEP-covered gene | Generic ACMG | Apply VCEP CSpec |
| PM2 = Moderate | Pre-SVI 2020 | Use PM2_Supporting |
| PS3 = Strong default | No OddsPath | Apply Brnich 2020 OddsPath |

## Anticipated Reviewer Pushback

| Pushback | Standard response |
|----------|-------------------|
| "Why Tavtigian point system?" | Every modern automated classifier implements it (InterVar, GeneBe, VarSome, Franklin). The 2015 combining rules are subsumed; many P/LP combinations only emerge from points. |
| "Why ONE predictor and not REVEL + BayesDel?" | Pejaver 2022 explicit recommendation; predictors share training data. |
| "AlphaMissense PP3_Strong?" | ClinGen SVI calibrated AlphaMissense to graded PP3/BP4 (Bergquist 2025); use the calibrated cutoffs, not the developer 0.564 threshold. |
| "PVS1 for nonsense in SCN5A LQT3" | LQT3 is GoF; LoF mechanism not established; PVS1 does not apply. |
| "Generic ACMG vs VCEP" | VCEP CSpec overrides generic; we check `cspec.genome.network` for active VCEP. |
| "Splice variant PP3 from SpliceAI" | Walker 2023 SVI Splicing Subgroup: DS_max >= 0.2 applies PP3 at Supporting weight; prediction alone does not reach PP3_Strong (needs RNA/experimental evidence). |
| "PM2 Moderate or Supporting?" | SVI 2020 downgraded to Supporting; we use Supporting for all classification post-2020. |

## References

- Richards S et al. 2015. Standards and guidelines for the interpretation of sequence variants. *Genet Med* 17:405. (Original ACMG/AMP)
- Tavtigian SV et al. 2018. Modeling the ACMG/AMP variant classification guidelines as a Bayesian classification framework. *Genet Med* 20:1054.
- Tavtigian SV et al. 2020. Fitting a naturally scaled point system to the ACMG/AMP variant classification guidelines. *Hum Mutat* 41:1734.
- Abou Tayoun AN et al. 2018. Recommendations for interpreting the loss of function PVS1 ACMG/AMP variant criterion. *Hum Mutat* 39:1517.
- Pejaver V et al. 2022. Calibration of computational tools for missense variant pathogenicity classification. *Am J Hum Genet* 109:2163.
- Bergquist T et al. 2025. Calibration of additional computational tools expands ClinGen recommendation options for variant classification with PP3/BP4 criteria. *Genet Med* 27:101402.
- Brnich SE et al. 2020. Recommendations for application of the functional evidence PS3/BS3 criterion using the ACMG/AMP sequence variant interpretation framework. *Genome Med* 12:3.
- Walker LC et al. 2023. ClinGen SVI Splicing Subgroup recommendations. *Am J Hum Genet* 110:1046.
- Biesecker LG et al. 2024. ClinGen guidance for use of the PP1/BS4 co-segregation and PP4 phenotype specificity criteria for sequence variant pathogenicity classification. *Am J Hum Genet* 111:24. (PP1/BS4 co-segregation)
- Cheng J et al. 2023. Accurate proteome-wide missense variant effect prediction with AlphaMissense. *Science* 381:eadg7492.
- Jaganathan K et al. 2019. Predicting splicing from primary sequence with deep learning. *Cell* 176:535. (SpliceAI)
- Zeng T et al. 2022. Predicting RNA splicing from DNA sequence using Pangolin. *Genome Biol* 23:103.
- Dawes R et al. 2023. SpliceVault predicts the precise nature of variant-associated mis-splicing. *Nat Genet* 55:324.
- Whiffin N et al. 2017. Using high-resolution variant frequencies to empower clinical genome interpretation. *Genet Med* 19:1151.
- Li MM et al. 2017. Standards and guidelines for the interpretation and reporting of sequence variants in cancer. *J Mol Diagn* 19:4. (AMP/ASCO/CAP)
- Miller DT et al. 2023. ACMG SF v3.2 list. *Genet Med* 25:100866.
- Stawiński P, Płoski R. 2024. Genebe.net: implementation and validation of an automatic ACMG variant pathogenicity criteria assignment. *Clin Genet* 106:119.
- Kopanos C et al. 2019. VarSome: the human genomic variant search engine. *Bioinformatics* 35:1978.
- Li Q, Wang K. 2017. InterVar: clinical interpretation of genetic variants. *Am J Hum Genet* 100:267.
- Xiang J et al. 2020. AutoPVS1 -- automated PVS1 decision-tree implementation (verify exact venue/year against the published code/release).
- ClinGen CSpec Registry: `https://cspec.genome.network/cspec/ui/svi/all`
- ClinGen VCI (Variant Curation Interface): `https://curation.clinicalgenome.org/`

## Related Skills

- clinical-databases/variant-prioritization - Rare-disease pipeline (filters variants; this skill classifies)
- clinical-databases/clinvar-lookup - ClinVar evidence aggregation
- clinical-databases/gnomad-frequencies - BS1/BA1 with Whiffin FAF95
- clinical-databases/myvariant-queries - Aggregated annotation pull
- variant-calling/clinical-interpretation - Clinical reporting workflow
<!-- END FILE: clinical-databases/acmg-classification/SKILL.md -->

## 子目录：clinical-databases/clinvar-lookup

<!-- BEGIN FILE: clinical-databases/clinvar-lookup/SKILL.md -->
---
name: bio-clinical-databases-clinvar-lookup
description: Queries ClinVar for variant pathogenicity classifications, ClinGen VCEP curations, and somatic-vs-germline interpretations via REST API, weekly VCF, or bulk XML. Use when determining clinical significance, triangulating conflicting interpretations, or aggregating evidence against the ACMG/AMP framework with ClinGen SVI specifications.
tool_type: python
primary_tool: requests
---

## Version Compatibility

Reference examples tested with: requests 2.31+, cyvcf2 0.30+, pandas 2.2+, bcftools 1.19+, Entrez Direct 21.0+, lxml 5.0+ (for v2 XML schema).

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed package and adapt the example to match the actual API rather than retrying. ClinVar XML schema v2 (rolled out in 2024) replaces `<ClinVarSet>` with `<VariationArchive>` as the top-level anchor; XSLT or parsers targeting the legacy element silently emit zero records.

# ClinVar Lookup and Clinical-Significance Triangulation

**'Look up the clinical significance of this variant'** -> Retrieve ClinVar VCV-level aggregate, SCV-level submissions, ClinGen Variant Curation Expert Panel (VCEP) overrides, and conflict-resolution status.

- Python (REST): `requests.get()` against the E-utilities `clinvar` database
- Python (local VCF): `cyvcf2.VCF('clinvar.vcf.gz')` for batch queries against the weekly snapshot
- CLI: `bcftools annotate -a clinvar.vcf.gz -c INFO/CLNSIG,INFO/CLNREVSTAT,INFO/CLNDN`
- Cross-database: ClinGen Allele Registry CA ID via `https://reg.clinicalgenome.org/`

## The Identifier Hierarchy (VCV / SCV / RCV): Get This Wrong and Everything Downstream Breaks

| Level | Format | What it aggregates | When to use | Fails when |
|-------|--------|--------------------|-------------|-----------|
| **SCV** | `SCVxxxxxxxxx.N` | One submitter, one variant, one condition (atomic submission unit) | Auditing who said what; conflict triangulation | Aggregated reporting (use VCV); cross-condition analysis |
| **RCV** | `RCVxxxxxxxxx.N` | All SCVs for a single (variant, condition) pair | Condition-stratified analysis; legacy aggregation | Variant-level reporting across all conditions (use VCV) |
| **VCV** | `VCVxxxxxxxxx.N` | All RCVs for one variant across all conditions | Canonical anchor since 2017; default API entrypoint | Condition-specific clinical action (use RCV); CLNSIG collapses multi-condition |

**Operational footgun:** the `clinvar.vcf.gz` `CLNSIG` field is the *variant-level* (VCV) aggregate. A variant Pathogenic for disease A but VUS for disease B collapses to "Pathogenic/Conflicting". For condition-stratified analysis, parse RCV-level XML, never `CLNSIG` alone.

**2024 XML schema overhaul:** ClinVar v2 XML separates `GermlineClassification`, `SomaticClinicalImpact`, and `OncogenicityClassification` under one `<VariationArchive>` anchor. The legacy `<ClinicalSignificance>` element is gone. Pipelines built before September 2024 against `<ClinVarSet>` silently emit zero records on new XML. The dual-release period ended December 2024.

## Star Ratings and the Override Hierarchy

| Stars | Review status | What it means operationally |
|-------|--------------|---------------------------|
| 4 | Practice guideline | ACMG/CAP CFTR-level (vanishingly rare) |
| 3 | Expert panel reviewed (ClinGen VCEP) | **FDA-recognized tier**; overrides lower-star records for clinical action |
| 2 | Multiple submitters, criteria provided, no conflicts | Reliable aggregate |
| 1 | Single submitter OR conflicting interpretations (often mis-reported as 2-star) | Use with scrutiny |
| 0 | No assertion criteria provided | Literature-only or legacy submissions |

ClinVar does NOT retract or hide lower-star records when a VCEP publishes; a variant can simultaneously display "Pathogenic (3-star VCEP)" and "Conflicting interpretations (1-star)". Tools handle this differently (VarSeq, Franklin, GenoOx each pick a winner via different rules); this is a major source of inter-tool disagreement.

## ClinGen Variant Curation Expert Panels (VCEPs)

As of 2025, ~80-90 VCEPs are approved or in progress across RASopathies, hereditary cancer (ENIGMA BRCA1/2, InSiGHT MMR), cardiomyopathy (sarcomere genes), hearing loss, RPE65/IRD, inborn errors of metabolism, and FH. The current count is moving; the authoritative directory is the Criteria Specification Registry at `https://cspec.genome.network/cspec/ui/svi/all`.

Each VCEP publishes a **gene-disease-specific CSpec** that re-weights ACMG/AMP criteria. The Hearing Loss VCEP downgrades PM2 to supporting by default and upgrades PS3 thresholds for OTOF. Treating "ACMG/AMP" as a single rubric across all genes is the most common error in non-specialist tooling.

## ACMG/AMP, ClinGen SVI Specifications, and the Bayesian Point System

The Richards 2015 28-criterion framework is the foundation, but **every modern automated classifier (InterVar, GeneBe, Franklin, VarSome) implements the Tavtigian 2018/2020 Bayesian point system**, not the original combining rules. Strengths map to points: Supporting=1, Moderate=2, Strong=4, Very Strong=8 (benign codes negative). Final categories: P >=10, LP 6-9, VUS 0-5, LB -1 to -6, B <=-7.

For variant interpretation framework details, calibrated in-silico thresholds, and PVS1 decision-tree logic, defer to `clinical-databases/acmg-classification`. This skill focuses on querying ClinVar; it intentionally does not re-implement classification.

## Conflicting Interpretations and Conflict Resolution

Harrison 2017 *Genet Med* 19:1096 (PMID 28301460) showed 87% of inter-lab conflicts were resolvable by reassessment plus data sharing. As of 2024, only 3.8% of conflicting BRCA1 missense VUS reached consensus despite years of effort; conflict resolution is slow even in best-curated genes.

**Submission staleness** is non-trivial: ClinVar does not push reclassifications to submitters; a 2017 SCV can persist on an active label in 2026 if the lab has not re-submitted. Genome Alert! (Yauy 2022 *Genet Med*) was built specifically to detect classification drift between weekly releases. The median delta is ~1,247 classification changes per month with potential clinical impact.

## Decision Tree by Query Scenario

| Scenario | Recommended path | Why |
|----------|------------------|-----|
| Single variant, known gene/condition | E-utilities `esummary` against `clinvar` DB | Lowest latency, returns VCV-level summary |
| Batch (10-1000 variants) by HGVS or rsID | myvariant.info with `fields=clinvar` | Aggregated, includes ClinVar review status |
| Batch (>1000) or coordinate-based | Local `clinvar.vcf.gz` with `bcftools annotate` or `cyvcf2` | No rate limits; weekly snapshot |
| Condition-stratified (variant in disease A vs B) | Bulk XML `VariationArchive` parsing | RCV is the only level that preserves per-condition classification |
| Cross-database join with gnomAD / dbSNP / COSMIC | ClinGen Allele Registry CA ID | Build-agnostic, transcript-agnostic canonical identifier |
| Reproducible analysis with citable date | First-Thursday-of-month archive on FTP | Only monthly snapshots are archived; weekly releases disappear |

## REST API Query (E-utilities)

**Goal:** Retrieve VCV-level ClinVar summary for a single variant by ID, gene, or HGVS.

**Approach:** Hit `esummary.fcgi` or `esearch.fcgi` against `db=clinvar`, parse JSON, then optionally hydrate to full record with `efetch`.

```python
import requests

EUTILS = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils'

def clinvar_summary(variation_id):
    '''Retrieve VCV-level summary by ClinVar VariationID (do not confuse with CA ID).

    The germline / somatic / oncogenicity classification nesting shown below
    follows the ClinVar 2024 eSummary v2 schema described in the data-access
    documentation. Field names have changed between API versions -- inspect
    the actual JSON returned by eSummary for the live ClinVar version before
    pinning these key paths in production.
    '''
    r = requests.get(f'{EUTILS}/esummary.fcgi',
                     params={'db': 'clinvar', 'id': variation_id, 'retmode': 'json'},
                     timeout=30)
    r.raise_for_status()
    record = r.json()['result'][str(variation_id)]
    return {
        'vcv': record.get('accession'),
        'name': record.get('title'),
        'germline_class': record.get('germline_classification', {}).get('description'),
        'germline_review_status': record.get('germline_classification', {}).get('review_status'),
        'somatic_clinical': record.get('clinical_impact_classification', {}).get('description'),
        'oncogenicity': record.get('oncogenicity_classification', {}).get('description'),
        'last_evaluated': record.get('germline_classification', {}).get('last_evaluated')
    }

def clinvar_search_gene(gene, pathogenic_only=False, retmax=500):
    term = f'{gene}[gene]'
    if pathogenic_only:
        term += ' AND (clinsig_pathogenic[Properties] OR clinsig_likely_pathogenic[Properties])'
    r = requests.get(f'{EUTILS}/esearch.fcgi',
                     params={'db': 'clinvar', 'term': term, 'retmax': retmax, 'retmode': 'json'},
                     timeout=30)
    return r.json()['esearchresult']['idlist']
```

## Local VCF Query (Weekly Snapshot)

**Goal:** Annotate or look up thousands of variants without rate limits.

**Approach:** Download the weekly `clinvar.vcf.gz` (note: only first-Thursday-of-month is archived; for longitudinal stability pin to monthly archives), query by genomic coordinates with cyvcf2 or annotate VCFs with bcftools.

```bash
mkdir -p clinvar/$(date +%Y%m); cd clinvar/$(date +%Y%m)
wget https://ftp.ncbi.nlm.nih.gov/pub/clinvar/vcf_GRCh38/clinvar.vcf.gz
wget https://ftp.ncbi.nlm.nih.gov/pub/clinvar/vcf_GRCh38/clinvar.vcf.gz.tbi
```

```python
from cyvcf2 import VCF

clinvar = VCF('clinvar.vcf.gz')

def lookup(chrom, pos, ref, alt):
    '''Look up by GRCh38 coords. Returns variant-level (VCV) aggregate; not RCV.'''
    for v in clinvar(f'{chrom}:{pos}-{pos}'):
        if v.REF == ref and alt in v.ALT:
            info = v.INFO
            return {
                'vcv_id': info.get('ALLELEID'),
                'clnsig': info.get('CLNSIG'),
                'clnsig_conf': info.get('CLNSIGCONF'),
                'clnrevstat': info.get('CLNREVSTAT'),
                'clndn': info.get('CLNDN'),
                'clnvc': info.get('CLNVC'),
                'clnhgvs': info.get('CLNHGVS'),
                'clndisdb': info.get('CLNDISDB'),
                'oncdn': info.get('ONCDN'),
                'scidn': info.get('SCIDN')
            }
    return None
```

```bash
bcftools annotate \
    -a clinvar.vcf.gz \
    -c INFO/CLNSIG,INFO/CLNREVSTAT,INFO/CLNDN,INFO/CLNVC,INFO/CLNHGVS,INFO/CLNSIGCONF \
    input.vcf.gz -O z -o annotated.vcf.gz
bcftools index -t annotated.vcf.gz
```

## ClinGen Allele Registry (CA IDs): The Real Cross-Database Anchor

ClinGen Allele Registry (`https://reg.clinicalgenome.org/`) computes a build-agnostic, transcript-agnostic CA ID (format `CA######`) for any allele projectable onto NCBI references (GRCh37, GRCh38, T2T-CHM13, any RefSeq transcript). The Registry covers ~700M+ alleles, vastly more than ClinVar. CA ID and ClinVar VariationID are one-to-one *when a variant exists in ClinVar*.

```python
def car_id(hgvs_g):
    '''Resolve HGVS-g to canonical ClinGen Allele Registry CA ID.'''
    r = requests.put(f'https://reg.clinicalgenome.org/allele',
                     headers={'Content-Type': 'text/plain'},
                     data=hgvs_g, timeout=30)
    return r.json().get('@id', '').split('/')[-1] if r.ok else None
```

Use CA ID for any join touching non-ClinVar resources (gnomAD, dbSNP, COSMIC, MAVEdb). VariationID was renumbered during the 2017 ClinVar schema redesign; treating it as a stable cross-build identifier is unsafe.

## Per-Operation Failure Modes

**1. Treating CLNSIG as gospel for condition-specific work**
- Trigger: Pull `CLNSIG=Pathogenic` from `clinvar.vcf.gz` and report variant as pathogenic for the patient's specific phenotype.
- Mechanism: CLNSIG is VCV-level aggregate; a variant can be P for disease A and B for disease B.
- Symptom: Patient phenotype does not match the disease where the variant is actually pathogenic; clinical action is wrong.
- Fix: Parse RCV-level XML (`<RCVAccession>` per condition); cross-check `CLNDN` and report per-condition classifications.

**2. Parsing legacy XML against 2024 schema**
- Trigger: XSLT or parser anchored on `<ClinVarSet>` or `<ClinicalSignificance>`.
- Mechanism: 2024 schema replaces both anchors with `<VariationArchive>` + germline/somatic/oncogenicity tripartite classifications.
- Symptom: Silent zero-record output, no error.
- Fix: Re-target to `<VariationArchive>` and read `GermlineClassification`, `SomaticClinicalImpact`, `OncogenicityClassification` separately.

**3. Counting `variant_summary.txt` rows naively**
- Trigger: `wc -l variant_summary.txt` to estimate variant count.
- Mechanism: One row per assembly per variant (GRCh37 *and* GRCh38); double-counts.
- Symptom: Counts inflated ~2x.
- Fix: `awk -F'\t' '$17=="GRCh38"' variant_summary.txt | wc -l`.

**4. Trusting VariationID as a stable cross-build identifier**
- Trigger: Join gnomAD-v4 records by ClinVar VariationID.
- Mechanism: VariationIDs were renumbered for a subset of variants during the 2017 schema overhaul.
- Symptom: Spurious mismatches at low rate (~1-2%).
- Fix: Use ClinGen Allele Registry CA ID, which is computed deterministically from sequence.

**5. Ignoring star-rating override hierarchy**
- Trigger: Pipeline picks the most-recent SCV regardless of review status.
- Mechanism: A 1-star SCV submitted yesterday outranks a 3-star VCEP curation from 2022 by date.
- Symptom: Clinical reports cite outdated or non-expert assertions over expert-panel decisions.
- Fix: Sort by `review_status` rank (4>3>2>1>0); use the highest-star record. For ties, sort by date.

**6. Aggregating "Conflicting" without inspecting the conflict**
- Trigger: Treat `CLNSIG=Conflicting interpretations` as VUS.
- Mechanism: "Conflicting" can mean (P vs LP), (P vs VUS), or (P vs LB); the clinical meaning is completely different across these.
- Symptom: Patients with high-evidence P variants reported as ambiguous; or true VUS reported as actionable.
- Fix: Parse `CLNSIGCONF` to see exact conflict; weight by submitter star.

**7. Missing somatic interpretations**
- Trigger: Pre-2024 pipeline reads only `CLNSIG`.
- Mechanism: Somatic classifications live in new INFO fields (`ONCDN`, `SCIDN`, `CLNSIGSOMATIC`) since 2024.
- Symptom: Cancer variants appear unclassified.
- Fix: Read `ONCDN` (oncogenicity disease name), `SCIDN` (somatic clinical impact disease name), and the somatic-specific significance fields.

## Reconciliation: When Sources Disagree

| Pattern | Likely cause | Action |
|---------|-------------|--------|
| ClinVar P vs gnomAD AF > 1% | Variant is true founder allele in unstratified gnomAD subset, OR ClinVar P is a stale low-star assertion | Check `grpmax_faf95` excluding bottleneck groups; check ClinVar star rating |
| ClinVar P vs AlphaMissense < 0.1 | Variant in NMD-escape region, alternative isoform, or ClinVar P is mis-curated | Check Pejaver 2022 calibration in `acmg-classification` skill; cross-check VCEP |
| VCEP 3-star P vs commercial-lab 1-star B | VCEP supersedes for clinical action | Use VCEP; flag submitter for resubmission |
| ClinVar VCV-level P vs RCV-level VUS for actual condition | VCV averages across conditions | Always report at RCV level for clinical action |
| ClinVar P vs LOVD/HGMD discordant | LOVD/HGMD use different classification systems; HGMD "DM" != ACMG P | Triangulate against published evidence; do not auto-translate labels |
| ClinVar P missing for a known disease variant | Submission lag (~6-12 months typical for new findings) | Check published literature; flag for ClinVar submission |

## Quantitative Thresholds and Operational Conventions

| Threshold | Convention | Source |
|-----------|-----------|--------|
| Star >= 2 | Acceptable confidence for clinical action without further review | ClinGen SVI operational guidance |
| Star = 3 | VCEP-curated; supersedes lower-star records | ClinGen FDA Recognition 2018 |
| `CLNSIG` includes 'Pathogenic' OR 'Likely_pathogenic' | Treat as actionable for ACMG | ClinVar field schema |
| `CLNSIGCONF` present | Multiple SCVs disagree; do NOT auto-action | ClinVar field schema |
| Monthly archive | Use first-Thursday-of-month FTP snapshot for reproducible analyses | NCBI FTP retention policy |
| Submission staleness | Re-check classification annually for active diagnostic variants | Yauy 2022 *Genet Med* (Genome Alert!) |
| AF > 5% in gnomAD | BA1 standalone benign per ClinGen SVI default (VCEP overrides exist) | Richards 2015; SVI specs |
| 1247 changes/month | Median variants with classification change per release | Yauy 2022 |

## ClinVar Somatic vs Germline: 2024 Tripartite

The 2024 schema separates three orthogonal classifications, each with its own `ReviewStatus` and `DateLastEvaluated`:

- **GermlineClassification:** Pathogenic / Likely Pathogenic / VUS / LB / B per ACMG/AMP 2015 + SVI.
- **SomaticClinicalImpact:** Tier I / II / III / IV per AMP/ASCO/CAP 2017 (Li 2017 *J Mol Diagn*).
- **OncogenicityClassification:** Oncogenic / Likely Oncogenic / VUS / Likely Benign / Benign per ClinGen/CGC/VICC 2022 oncogenicity framework.

A single VCV can carry all three with distinct evaluations; the legacy "Pathogenic" label is now ambiguous if not qualified by classification type.

## Common Errors

| Symptom | Cause | Solution |
|---------|-------|----------|
| Empty result from `efetch db=clinvar` | rsID passed where VariationID expected | Use `esearch` first to resolve rsID to VariationID |
| `CLNSIG` is `_None` or comma-separated mess | Variant has multi-condition RCVs; VCF collapses them | Parse RCV XML for per-condition values |
| Variant present in ClinVar XML but absent from VCF | Variant lacks GRCh38 coordinates (legacy GRCh37-only submission) | Check `<VariationArchive><SequenceLocation>` per assembly |
| 2024-format XML parser silently emits zero records | XML schema v2 incompatibility | Re-target to `<VariationArchive>` |
| Conflicting interpretations with same star rating across two submitters | True scientific disagreement; sometimes resolved by VCEP later | Apply Tavtigian point system to manually reconcile; flag for VCEP review |
| Variant has CA ID but no VariationID | Variant in Allele Registry but never submitted to ClinVar | Use AlleleRegistry as canonical; submit to ClinVar if novel pathogenic |
| `CLNSIG` says Pathogenic but no associated condition `CLNDN` | Orphan classification (older submissions) | Treat as low confidence; cross-check publication |
| Variants pulled by gene return only some isoforms | RefSeq transcript priority differences | Use MANE Select transcript explicitly; cross-check with VEP `--mane_select` |

## Anticipated Reviewer Pushback

| Pushback | Standard response |
|----------|-------------------|
| "Why is this pathogenic variant 1-star?" | We report star rating per submission; clinical action requires star >=2 OR VCEP curation per ClinGen SVI 2018. |
| "ClinVar says P but gnomAD AF = 2%" | Reconciled via Whiffin FAF95 max-credible-AF framework; bottleneck-group rule applied. |
| "This VCV count differs from ClinVar.gov" | We pulled from the monthly archive (first-Thursday-of-month) for reproducibility; the live web is post-most-recent-weekly. |
| "Why wasn't the somatic variant flagged?" | Pre-2024 XML schema had no separate somatic field; we now read `ONCDN`/`SCIDN`/`SomaticClinicalImpact` per v2 schema. |
| "VarSome says LP but this says VUS" | Tool-specific aggregation rule differences; VarSome auto-applies PP3+PM2 by default per Tavtigian point system; we apply VCEP-specific PP3 calibration per CSpec. |
| "rsID match returned wrong variant" | rsID is a cluster identifier; multi-allelic rsIDs require allele-level resolution; we use SPDI or CA ID. |
| "Why retest a 2022-curated variant?" | Classifications drift as evidence accrues; ClinGen recommends annual re-review for active diagnostic variants. |

## References

- Landrum MJ et al. 2025. ClinVar: updates to support classifications of both germline and somatic variants. *Nucleic Acids Res* 53(D1):D1313.
- Harrison SM et al. 2017. Clinical laboratories collaborate to resolve differences in variant interpretations submitted to ClinVar. *Genet Med* 19:1096.
- Yauy K et al. 2022. Genome Alert! a standardized procedure for genomic variant reinterpretation and automated gene-phenotype reassessment. *Genet Med* 24:1316.
- Tavtigian SV et al. 2018. Modeling the ACMG/AMP variant classification guidelines as a Bayesian classification framework. *Genet Med* 20:1054.
- Tavtigian SV et al. 2020. Fitting a naturally scaled point system to the ACMG/AMP variant classification guidelines. *Hum Mutat* 41:1734.
- Richards S et al. 2015. Standards and guidelines for the interpretation of sequence variants. *Genet Med* 17:405. (Original ACMG/AMP 2015)
- Pejaver V et al. 2022. Calibration of computational tools for missense variant pathogenicity classification. *Am J Hum Genet* 109:2163.
- Abou Tayoun AN et al. 2018. Recommendations for interpreting the loss of function PVS1 ACMG/AMP variant criterion. *Hum Mutat* 39:1517.
- Brnich SE et al. 2020. Recommendations for application of the functional evidence PS3/BS3 criterion using the ACMG/AMP sequence variant interpretation framework. *Genome Med* 12:3.
- Li MM et al. 2017. Standards and guidelines for the interpretation and reporting of sequence variants in cancer. *J Mol Diagn* 19:4. (AMP/ASCO/CAP somatic framework)
- ClinGen Allele Registry: `https://reg.clinicalgenome.org/docs/cg-car/`
- CSpec Registry: `https://cspec.genome.network/cspec/ui/svi/all`

## Related Skills

- clinical-databases/acmg-classification - ACMG/AMP framework, PVS1 decision tree, Pejaver calibrated PP3/BP4 thresholds, Bayesian point system
- clinical-databases/myvariant-queries - Aggregated queries including ClinVar overlay
- clinical-databases/variant-prioritization - Rare-disease filtering pipeline using ClinVar
- clinical-databases/gnomad-frequencies - Population frequency for BS1/BA1 cross-check
- variant-calling/clinical-interpretation - Clinical reporting workflow
<!-- END FILE: clinical-databases/clinvar-lookup/SKILL.md -->

## 子目录：clinical-databases/dbsnp-queries

<!-- BEGIN FILE: clinical-databases/dbsnp-queries/SKILL.md -->
---
name: bio-clinical-databases-dbsnp-queries
description: Resolves rsIDs, navigates RsMergeArch/SNPHistory merge chains, and converts between rsID, SPDI, HGVS, and VCF representations using the dbSNP Build 156 JSON architecture. Use when normalizing variant identifiers, joining variant databases by cluster ID, or tracking deprecated rsIDs through historical merges.
tool_type: python
primary_tool: myvariant
---

## Version Compatibility

Reference examples tested with: myvariant 1.0+, requests 2.31+, biopython 1.83+, Entrez Direct 21.0+. dbSNP Build 156 (September 2022) is the current schema; Build 151 (2017) was the last with relational SQL dumps. Builds 152-155 dual-released JSON+SQL; 156+ is JSON-only.

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed package and adapt the example to match the actual API rather than retrying. The Variation Services REST API uses path-based versioning (`/variation/v0/`); E-utilities `db=snp` returns thin legacy summaries missing build-156 schema fields.

# dbSNP Queries and rsID Normalization

**'Look up this rsID / normalize variant representations'** -> Resolve rsIDs through merge chains, compute canonical SPDI, and convert between rsID, HGVS-g, HGVS-c, and VCF allele representations.

- Python (aggregator): `myvariant.MyVariantInfo().getvariant(rsid, fields=['dbsnp', 'clinvar', 'gnomad_exome'])`
- Python (direct): `requests.get(f'https://api.ncbi.nlm.nih.gov/variation/v0/refsnp/{rsid_int}')`
- Python (E-utilities, legacy): `Bio.Entrez.esearch(db='snp', term=rsid)`; returns thin summary
- Bulk: `ftp.ncbi.nlm.nih.gov/snp/latest_release/JSON/refsnp-chr{N}.json.bz2`

## rsID Is a Cluster Identifier, Not a Variant Identifier

This is the load-bearing concept. dbSNP cluster definition: ss records (submitted SNPs) are mapped to the genome and clustered into RefSNPs by *position + variant type*, not by allele. A single rsID can point to a *locus* with multiple alleles:

- `rs12345` may resolve to {A>G, A>T, A>C} at one position; the RefSNP JSON `primary_snapshot_data.placements_with_allele[*].alleles` enumerates them.
- ~6-8% of dbSNP rsIDs are multi-allelic.
- PLINK and many older tools historically misuse rsIDs as if they were variant identifiers, which fails for multi-allelic sites and yields wrong genotype assignments.

**Rule:** Use rsID as a *human-facing label only*; use SPDI or ClinGen Allele Registry CA ID for joins.

## Build 156 Schema Overhaul: What Changed

| Aspect | Build 151 (2017) | Build 156 (2022) and current |
|--------|------------------|------------------------------|
| Distribution | Relational SQL dumps + XML | JSON per RefSNP, partitioned by chromosome |
| FTP path | `ftp/snp/organisms/human_9606/` | `ftp.ncbi.nlm.nih.gov/snp/latest_release/JSON/` |
| Primary key | `snp_id`, `ss_id` | `refsnp_id`, with `primary_snapshot_data` block |
| Frequency data | Embedded sparse | ALFA aggregated populations |
| Merge tracking | `RsMergeArch.bcp.gz` | `refsnp-merged.json.bz2` (also `RsMergeArch.bcp.gz` retained for legacy) |
| Withdrawn | `SNPHistory.bcp.gz` | `refsnp-withdrawn.json.bz2` |
| API access | Legacy E-utilities `db=snp` only | Variation Services REST `/v0/refsnp/{id}` returns the full JSON |

E-utilities still works for `db=snp` but returns a thin pre-156 summary missing key fields like `primary_snapshot_data.placements_with_allele`; pipelines reliant on Entrez get out-of-date data.

## RsMergeArch: The Multi-Hop Merge Footgun

When two rsIDs are found to refer to the same allele cluster, the higher (later-assigned) rsID is merged into the lower. `RsMergeArch.bcp.gz` stores `(rsHigh, rsLow, rsCurrent)` tuples.

**The trap:** `rsCurrent` in any given row is the merge target at the time of that merge event, NOT the current dbSNP rsID. A multi-merge chain (rs3 -> rs2 -> rs1, then later rs1 -> rs0) appears as multiple rows. Naive one-hop lookup resolves to a stale ID.

Withdrawn rsIDs (submitter-withdrawn or QC-failed) live in `SNPHistory.bcp.gz`, not RsMergeArch. Both tables must be consulted to resolve any historical rsID.

## SPDI: The Canonical Variant Representation

SPDI (Sequence:Position:Deletion:Insertion) format: `NC_000017.11:43044294:G:A`. Position is **0-based, half-open** (differs from HGVS's 1-based, fully-closed).

The **Contextual Allele** transformation (Variant Overprecision Correction Algorithm) returns the right-aligned, normalized canonical form across left-aligned VCFs and right-aligned HGVS conventions. This is the basis for ClinGen Allele Registry CA ID computation.

| Representation | Build dependency | Transcript dependency | Bijective? | Best for |
|----------------|-----------------|----------------------|------------|----------|
| **VCF (chrom-pos-ref-alt)** | Yes | No | Yes (same build) | Pipelines, bulk |
| **SPDI** | Yes (via RefSeq accession) | No | Yes for SNV/small indel | Canonical normalization |
| **HGVS-g** | Yes (`NC_xxxxx.N`) | No | Yes for SNV/small indel | Human-readable genomic |
| **HGVS-c** | Indirect (via transcript) | Yes | No (one HGVS-c -> many HGVS-g) | Clinical reporting |
| **HGVS-p** | Indirect | Yes | Degenerate (one HGVS-p -> many HGVS-c) | Protein-level annotation |
| **rsID** | None (cluster identifier) | None | NO (multi-allelic) | Human label only |
| **CA ID** | None (canonical) | None | Yes | Cross-database join |

## Decision Tree by Query Scenario

| Scenario | Recommended path | Why |
|----------|------------------|-----|
| Resolve single rsID to coordinates + alleles | Variation Services `/v0/refsnp/{id}` | Returns full Build 156 JSON, including merge history |
| Resolve historical/deprecated rsID | Variation Services `/v0/refsnp/{id}` -> follow `merged_snapshot_data` chain | Single-hop RsMergeArch lookup misses multi-hop chains |
| Batch query 100-10k rsIDs | myvariant.info `getvariants(rsids)` | Aggregated with ClinVar/gnomAD overlay; rate-limit safe |
| Convert coords <-> rsID | myvariant.info HGVS query or Variation Services `/spdi/{spdi}/rsid` | SPDI is the canonical bridge |
| Normalize variant representations | Variation Services `/hgvs/{hgvs}/contextuals` | Returns canonical SPDI, right-aligned |
| Bulk genomic-wide rsID -> coords | Local download of `refsnp-chr{N}.json.bz2` + parser | No rate limits; weekly snapshots |
| Joining dbSNP with gnomAD by ID | Use SPDI or CA ID, never rsID alone | rsID is a cluster; alleles may not match |
| Get population AF for common variant | ALFA (via Variation Services) for array-genotyped variants; gnomAD for sequencing-derived | Different sample compositions |

## Single rsID Resolution

**Goal:** Resolve an rsID to full Build 156 RefSNP JSON, including coordinates, alleles, gene context, and merge history.

**Approach:** Hit Variation Services `/v0/refsnp/{id_without_rs}`; the response includes `primary_snapshot_data` (current) and `merged_snapshot_data` (if this rsID is itself a merge target).

```python
import requests

VARSVC = 'https://api.ncbi.nlm.nih.gov/variation/v0'

def refsnp(rsid):
    '''Fetch full Build 156 RefSNP JSON. rsid can be 'rs121913529' or 121913529.'''
    rs_int = str(rsid).lstrip('rs')
    r = requests.get(f'{VARSVC}/refsnp/{rs_int}', timeout=30)
    if r.status_code == 404:
        return None
    r.raise_for_status()
    return r.json()

def summarize_refsnp(payload):
    '''Extract minimal fields. Handles multi-allelic cluster correctly.

    The placement JSON nests assembly metadata; the precise path varies by
    Build / API version. Common variants seen in the wild:
        placement['seq_id_traits_by_assembly'][0]['assembly_name']
        placement['placement_annot']['seq_id_traits_by_assembly'][0]['assembly_name']
    Inspect the actual JSON returned for the current dbSNP Build before
    relying on either path in production.
    '''
    if payload is None or payload.get('is_withdrawn'):
        return None
    primary = payload.get('primary_snapshot_data', {})
    placements = primary.get('placements_with_allele', [])
    def assembly_name(p):
        traits = (p.get('placement_annot') or p).get('seq_id_traits_by_assembly') or []
        return traits[0].get('assembly_name') if traits else ''
    grch38 = next((p for p in placements if 'GRCh38' in (assembly_name(p) or '')), None)
    if grch38 is None:
        return None
    alleles = []
    for allele in grch38.get('alleles', []):
        spdi = allele.get('allele', {}).get('spdi', {})
        alleles.append({
            'ref': spdi.get('deleted_sequence'),
            'alt': spdi.get('inserted_sequence'),
            'seq_id': spdi.get('seq_id'),
            'pos_0based': spdi.get('position')
        })
    return {
        'rsid': payload.get('refsnp_id'),
        'gene': primary.get('allele_annotations', [{}])[0].get('assembly_annotation', [{}])[0].get('genes', [{}])[0].get('locus'),
        'placements_grch38': alleles,
        'is_multiallelic': len(alleles) > 2,
        'merge_history': payload.get('merged_snapshot_data', [])
    }
```

## Multi-Hop Merge Resolution

**Goal:** Resolve a possibly-deprecated rsID to the current canonical rsID, following the full merge chain.

**Approach:** Recursively follow `merged_snapshot_data` until the response has no further merge entries, with cycle detection.

```python
def resolve_merge_chain(rsid, max_hops=10):
    '''Follow multi-hop merge chain. Cycle-safe with max_hops cap.'''
    seen = set()
    current = str(rsid).lstrip('rs')
    for _ in range(max_hops):
        if current in seen:
            return {'error': 'merge cycle detected', 'chain': list(seen)}
        seen.add(current)
        payload = refsnp(current)
        if payload is None:
            return {'error': 'not found', 'final_rsid': current, 'chain': list(seen)}
        if payload.get('is_withdrawn'):
            return {'status': 'withdrawn', 'final_rsid': current, 'chain': list(seen)}
        primary = payload.get('primary_snapshot_data')
        if primary is not None:
            return {'status': 'resolved', 'final_rsid': payload.get('refsnp_id'), 'chain': list(seen)}
        merged = payload.get('merged_snapshot_data', [])
        if not merged:
            return {'status': 'orphan', 'final_rsid': current, 'chain': list(seen)}
        current = str(merged[0].get('merged_into', ''))
    return {'error': 'hop limit', 'chain': list(seen)}
```

## SPDI <-> HGVS <-> VCF Conversion

**Goal:** Move between variant representations using Variation Services as the canonical bridge.

**Approach:** SPDI endpoints handle build resolution and right-alignment; HGVS contextuals applies the Variant Overprecision Correction Algorithm.

```python
def hgvs_to_spdi_canonical(hgvs):
    '''Resolve HGVS to canonical SPDI via the Variant Overprecision Correction Algorithm.'''
    r = requests.get(f'{VARSVC}/hgvs/{hgvs}/contextuals', timeout=30)
    if not r.ok:
        return None
    contextuals = r.json().get('data', {}).get('spdis', [])
    return contextuals[0] if contextuals else None

def spdi_to_rsid(spdi_str):
    '''SPDI 'NC_000017.11:43044294:G:A' -> rsID if a cluster exists.'''
    r = requests.get(f'{VARSVC}/spdi/{spdi_str}/rsids', timeout=30)
    if not r.ok:
        return None
    rsids = r.json().get('data', {}).get('rsids', [])
    return rsids[0] if rsids else None

def vcf_to_canonical_spdi(chrom, pos, ref, alt, assembly='GRCh38'):
    '''VCF (1-based) -> SPDI (0-based, right-aligned).'''
    refseq_map = {('1', 'GRCh38'): 'NC_000001.11', ('17', 'GRCh38'): 'NC_000017.11'}
    refseq = refseq_map.get((str(chrom).lstrip('chr'), assembly))
    if refseq is None:
        return None
    raw_spdi = f'{refseq}:{pos - 1}:{ref}:{alt}'
    r = requests.get(f'{VARSVC}/spdi/{raw_spdi}/canonical_representative', timeout=30)
    return r.json().get('data', {}).get('spdi') if r.ok else None
```

## ALFA Frequencies vs gnomAD

| Source | Sample basis | Variants covered | When to use |
|--------|-------------|------------------|-------------|
| **ALFA** | ~1M dbGaP subjects (array + WGS) across 12 ancestry groups | 447M+ sites; broader (includes array-only) | Common variants, dbGaP-deposited cohorts |
| **gnomAD v4** | 807k WGS+WES individuals across 9 ancestry groups | Sequencing-derived (deeper at rare variants) | Rare-variant FAF95, ACMG BS1/BA1 |

ALFA does NOT provide FAF95-style upper-bound CIs; raw AF only. ALFA captures consent-tier metadata enabling consent-respecting lookups for variants gnomAD doesn't carry.

```python
def alfa_frequency(rsid, ancestry='Total'):
    '''Pull ALFA per-population AF via Variation Services.'''
    payload = refsnp(rsid)
    if payload is None:
        return None
    freq_records = payload.get('primary_snapshot_data', {}).get('allele_annotations', [{}])[0].get('frequency', [])
    alfa_records = [f for f in freq_records if 'ALFA' in f.get('study_name', '')]
    for record in alfa_records:
        if record.get('common_name') == ancestry:
            return {
                'allele': record.get('observation', {}).get('inserted_sequence'),
                'count': record.get('allele_count'),
                'total': record.get('total_count'),
                'freq': record.get('allele_count') / record.get('total_count') if record.get('total_count') else None
            }
    return None
```

## Per-Operation Failure Modes

**1. Treating rsID as a unique variant identifier**
- Trigger: Join two databases by rsID expecting a single variant.
- Mechanism: rsID is a cluster identifier; multi-allelic clusters have 2-4 alleles at one position.
- Symptom: Allele mismatches at low rate (~6-8% of sites); silent merger of unrelated variants.
- Fix: Normalize both sides to SPDI or CA ID before joining.

**2. Single-hop RsMergeArch lookup**
- Trigger: Read one row of `RsMergeArch.bcp.gz` and treat `rsCurrent` as the final answer.
- Mechanism: Multi-hop merges (rs3 -> rs2 -> rs1 -> rs0) span multiple rows; each row records one hop only.
- Symptom: Resolved rsID is itself stale; subsequent queries return outdated annotation.
- Fix: Follow merge chains recursively via Variation Services `merged_snapshot_data` (handles multi-hop in one call).

**3. Confusing withdrawn vs merged**
- Trigger: Query a withdrawn rsID and find no merge target.
- Mechanism: Withdrawn rsIDs live in `SNPHistory.bcp.gz`, not RsMergeArch. They are NOT merged into anything; the cluster was QC-failed or submitter-retracted.
- Symptom: 404 from naive lookup; pipelines proceed with stale rsID.
- Fix: Check `is_withdrawn` field in RefSNP JSON; flag the variant for manual review.

**4. E-utilities thin summary**
- Trigger: Use `Entrez.esummary(db='snp')` and treat output as authoritative.
- Mechanism: E-utilities `db=snp` returns a pre-Build-156 summary missing `primary_snapshot_data.placements_with_allele`, frequency data, and merge history.
- Symptom: Annotations look incomplete or out-of-date.
- Fix: Use Variation Services REST `/v0/refsnp/{id}` for full JSON.

**5. SPDI 0-based vs HGVS 1-based mismatch**
- Trigger: Build SPDI string from VCF position without converting to 0-based.
- Mechanism: SPDI position is 0-based half-open; VCF is 1-based.
- Symptom: Coordinate off-by-one; SPDI does not resolve to expected rsID.
- Fix: SPDI position = (VCF position - 1). For indels, also normalize ref/alt.

**6. Strand/orientation ambiguity for A/T C/G variants**
- Trigger: Merge variants across builds or platforms relying on rsID alone.
- Mechanism: rsID is locus-level; opposite-strand alleles get the same rsID with different ref/alt representation.
- Symptom: Strand-flipped genotypes after merge.
- Fix: Use SPDI (which encodes strand via deleted/inserted sequence) or MAF-match for ambiguous variants.

## Reconciliation: When Sources Disagree

| Pattern | Likely cause | Action |
|---------|-------------|--------|
| dbSNP rsID returns 404 in current build | Withdrawn (in `refsnp-withdrawn.json.bz2`) | Check withdrawal reason; consider manual curation |
| rsID resolves to different coords across builds | Genome assembly change (GRCh37 -> GRCh38) | Use SPDI with explicit RefSeq accession; lift over via `pyliftover` |
| ALFA AF and gnomAD AF disagree by >2x | Different sample compositions; ALFA includes array-only sites under-represented in gnomAD | Trust gnomAD for sequencing data; ALFA for array-derived; use the more relevant source |
| Multiple rsIDs map to one SPDI | True duplicates from independent submissions; rare since Build 152 enforced cluster merging | Pick the lowest rsID per RsMergeArch convention |
| One rsID has different ref allele in dbSNP vs gnomAD | dbSNP uses NCBI's ref; gnomAD aligns to its build assembly | Normalize to SPDI before joining |

## Quantitative Thresholds and Conventions

| Threshold | Convention | Source |
|-----------|-----------|--------|
| Build 156 | Current as of Sep 2022; JSON-only distribution | dbSNP NCBI |
| Multi-allelic rate | ~6-8% of dbSNP rsIDs are multi-allelic | operational estimate |
| Variation Services rate limit | 10 req/s with API key; 3 req/s without | NCBI E-utilities policy |
| SPDI position | 0-based, half-open | NCBI SPDI specification |
| HGVS position | 1-based, fully-closed | HGVS nomenclature |
| ALFA samples | ~1M individuals across 12 ancestries (2024 release) | NCBI dbGaP aggregation |
| Bulk download chunks | One file per chromosome (`refsnp-chr{N}.json.bz2`) | NCBI FTP |

## Common Errors

| Symptom | Cause | Solution |
|---------|-------|----------|
| 404 from Variation Services on valid rsID | rsID is withdrawn or never assigned | Check `refsnp-withdrawn.json.bz2`; consider strand-flipped equivalent |
| Merge chain resolves but final rsID has different alleles | Multi-allelic cluster; pick allele matching the variant | Filter `placements_with_allele.alleles[*]` by allele match |
| ALFA frequency missing for common variant | Variant not in dbGaP-deposited studies | Fall back to gnomAD (sequencing-derived) |
| `Entrez.esummary` returns old data | Legacy E-utilities, not Build 156 schema | Switch to Variation Services REST `/v0/refsnp/{id}` |
| HGVS-c conversion fails for synonymous variants | Some HGVS-c rely on non-MANE transcripts not in NCBI default | Specify transcript explicitly; use VEP `--mane_select` |
| SPDI for indel does not round-trip | Left/right alignment mismatch | Use `/spdi/{spdi}/canonical_representative` for normalization |
| Bulk JSON parse OOM | `refsnp-chr1.json.bz2` is ~20GB uncompressed | Stream parse with `bz2.BZ2File` + line-by-line JSON; do not load whole file |

## Anticipated Reviewer Pushback

| Pushback | Standard response |
|----------|-------------------|
| "Why not just use rsID for the join?" | rsID is a cluster identifier; ~6-8% of clusters are multi-allelic, causing silent mismatches. We use SPDI / CA ID. |
| "This annotation says rs12345 but the literature says rs67890" | rsIDs are merged; we resolved through `RsMergeArch` / `merged_snapshot_data` to the current canonical rsID. |
| "dbSNP frequency != gnomAD frequency" | ALFA (dbSNP-embedded) and gnomAD use different sample sets and different ascertainment (array vs sequencing); reconciled per use case. |
| "Why wasn't Entrez used?" | Entrez `db=snp` returns the pre-Build-156 summary missing key fields; we use Variation Services REST for the full JSON. |
| "Coordinate off-by-one in the SPDI" | SPDI is 0-based half-open; VCF is 1-based; intentional conversion applied. |

## References

- Phan L et al. 2025. The evolution of dbSNP: 25 years of impact in genomic research. *Nucleic Acids Res* 53:D925.
- Sayers EW et al. 2024. Database resources of the National Center for Biotechnology Information. *Nucleic Acids Res* 52:D33.
- Holmes JB et al. 2020. SPDI: data model for variants and applications at NCBI. *Bioinformatics* 36:1902.
- NCBI Variation Services API: `https://api.ncbi.nlm.nih.gov/variation/v0/`
- dbSNP FTP layout: `ftp.ncbi.nlm.nih.gov/snp/latest_release/JSON/`
- ALFA release notes: `https://www.ncbi.nlm.nih.gov/snp/docs/gsr/alfa/`
- ClinGen Allele Registry: `https://reg.clinicalgenome.org/docs/cg-car/`

## Related Skills

- clinical-databases/myvariant-queries - Aggregated rsID + annotation queries
- clinical-databases/clinvar-lookup - ClinVar VariationID vs rsID linkage
- clinical-databases/gnomad-frequencies - Frequency lookups by canonical SPDI
- clinical-databases/variant-prioritization - Pipeline using normalized variant IDs
- database-access/entrez-search - General Entrez query patterns
<!-- END FILE: clinical-databases/dbsnp-queries/SKILL.md -->

## 子目录：clinical-databases/gnomad-frequencies

<!-- BEGIN FILE: clinical-databases/gnomad-frequencies/SKILL.md -->
---
name: bio-clinical-databases-gnomad-frequencies
description: Queries gnomAD v4 (807k samples), v3, v2.1.1, and constraint metrics with grpmax FAF95, bottleneck-group exclusion, LOEUF interpretation, SV/CNV/mtDNA catalogs, and Whiffin max-credible-AF framework. Use when filtering rare variants, applying ACMG BS1/BA1, ranking genes by LoF intolerance, or selecting between v2 (GRCh37 + chrX/Y constraint) and v4 (GRCh38 + 807k samples).
tool_type: python
primary_tool: requests
---

## Version Compatibility

Reference examples tested with: requests 2.31+, hail 0.2.130+, pandas 2.2+, myvariant 1.0+. Current gnomAD release is **v4.1 (May 2024)**; v4.1 fixed the v4.0 AN under-counting issue that inflated rare-variant AF estimates by 5-10%.

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- Hail: `hl.version()`; pin to >=0.2.130 for v4 schema

If code throws ImportError, AttributeError, or TypeError, introspect the installed package and adapt the example to match the actual API rather than retrying. The gnomAD browser GraphQL API at `https://gnomad.broadinstitute.org/api` is the supported public endpoint; Hail Tables on Google Cloud Storage at `gs://gcp-public-data--gnomad/` are the supported bulk access.

# gnomAD Frequency Queries and Constraint

**'How rare is this variant in the general population?'** -> Pull allele frequency, grpmax FAF95 (the ACMG-grade frequency), LOEUF gene-level constraint, structural variant catalog, mtDNA frequencies, and the appropriate dataset version per use case.

- Python (single variant): GraphQL via `requests.post('https://gnomad.broadinstitute.org/api', json={'query': ..., 'variables': ...})`
- Python (aggregator): `myvariant.MyVariantInfo().getvariant(hgvs, fields=['gnomad_exome', 'gnomad_genome'])`
- Python (bulk): `hl.read_table('gs://gcp-public-data--gnomad/release/4.1/ht/exomes/gnomad.exomes.v4.1.sites.ht')`

## v2.1.1 / v3.1.2 / v4.x: When to Use Which

This is the most consequential decision in any gnomAD query. The releases are **not interchangeable**; choice determines what can and cannot be said about a variant.

| Release | Build | Samples | Use when | Fails when |
|---------|-------|---------|----------|-----------|
| **v2.1.1** | GRCh37 | 125,748 exomes + 15,708 genomes | Constraint metrics needed (LOEUF v2 most-validated); chrX/Y constraint required; GRCh37 native non-negotiable | GRCh38 native cohort; modern rare-variant FAF95 (use v4) |
| **v3.1.2** | GRCh38 | 76,156 genomes (NO exomes) | Non-coding region rare variants on GRCh38; mtDNA frequencies | Exome variants needed (no exomes); 76k cohort smaller than v4 |
| **v4.0/v4.1** | GRCh38 | 730,947 exomes + 76,215 genomes = **807,162 total** | Default for everything; rare-variant filtering, FAF95, gene queries | chrX/Y constraint (not released); cancer-cohort analysis (no TCGA in v4) |

**Critical caveats:**
- v4 genomes are the SAME 76,215 v3 samples reprocessed against GRCh38 with updated pipelines; not independent.
- ~81% of v2 genomes are also in v3; joint v2+v3 meta-analysis must dedupe at sample ID.
- v4 includes 416,555 UK Biobank exomes under a specific collaboration agreement; check use terms.
- **v4 does NOT include TCGA**, so the `non_cancer` subset is unnecessary; the v4 subset is `non_ukb` (excludes UKB exomes for ancestry rebalancing).
- Liftover v2 (GRCh37 -> GRCh38) is NOT equivalent to v4 native; variant representation differs at ~0.5-1% of sites due to assembly fixes.

## v4 Ancestry Groups: popmax -> grpmax Terminology

v4 ancestry groups: **AFR, AMR, ASJ, EAS, FIN, MID, NFE, SAS, AMI, REMAINING**. The **MID (Middle Eastern) group was new in v4**; previously absorbed into "OTH". The **REMAINING** group (31,256 v4 samples) is individuals who did not cluster with any reference; they contribute to overall AF but not to grpmax.

**Terminology shift:** gnomAD documentation and ACMG-facing narrative uses **grpmax** (genetic ancestry group max) -- replacing the older **popmax** ("population max") term -- to disambiguate genetic ancestry from self-reported race/ethnicity. The public GraphQL schema still exposes legacy field names containing `popmax` (e.g. `faf95.popmax`, `faf95.popmax_population`); these are the grpmax values under the modern terminology. Always check the schema version when writing queries; new browsers may rename these fields.

`grpmax_faf95` is the operational ACMG field. It computes the maximum 95% lower-CI allele frequency, **excluding bottleneck groups** (AMI, ASJ, FIN, REMAINING) because pathogenic founder variants in those groups would otherwise falsely trigger BS1/BA1. MID is included in grpmax but is the smallest non-bottleneck group with highest per-allele variance.

## Filtering Allele Frequency (FAF95): The ACMG-Grade AF

Whiffin 2017 *Genet Med* 19:1151 introduced FAF95 = Poisson lower bound of 95% CI for AF. By construction, AF > FAF95; FAF95 is the conservative frequency for ACMG application.

**Max-credible-AF formula:** `(prevalence x heterogeneity x allelic-contribution) / (penetrance x 2)`. Plug in disease parameters to get the gene-specific BA1 / BS1 threshold; compare against `grpmax_faf95`.

| Code | Threshold | Notes |
|------|-----------|-------|
| **BA1** | AF > 5% in any non-bottleneck group | ClinGen SVI default; VCEPs may override (Hearing Loss VCEP uses 0.5%) |
| **BS1** | AF > gene-specific max-credible-AF | Computed per gene via Whiffin formula |
| **PM2_Supporting** | Absent or ultra-rare in gnomAD | Downgraded from PM2_Moderate in SVI 2020 |

Use `grpmax_faf95`, not raw AF, for BS1/BA1 application; this is the ClinGen-recommended approach.

## Constraint Metrics: pLI, LOEUF, missense Z

Karczewski 2020 *Nature* 581:434 defined LOEUF as the upper bound of the 90% CI of observed/expected pLoF count per gene. LOEUF is **recommended over pLI** because it is continuous and accounts for gene size more rigorously.

| Metric | What | Interpretation |
|--------|------|----------------|
| **LOEUF** | Upper bound of 90% CI of LoF observed/expected ratio | Lower = more LoF-intolerant; **first decile (LOEUF < 0.35 v2; < 0.6 v4) = strongly intolerant** |
| **pLI** | Probability LoF intolerant | Still used; gnomAD team recommends LOEUF for ranking |
| **Missense Z** | Z-score of observed-vs-expected missense | Z > 3.09 = 'constrained' set (~p < 0.001, one-tailed) |
| **Missense O/E** | Observed/expected missense ratio | Continuous form of missense Z |

**Critical version mismatch:**
- v2.1.1 constraint metrics published 2020; v4 constraint published **March 2024** (4 months after v4 data release).
- **v4 constraint is autosomes only; chrX and chrY constraint metrics in v4 are NOT released**. For X/Y constraint, fall back to v2.1.1.
- **LOEUF first decile shifted v2 to v4**: v2 < 0.35; v4 < 0.6 (larger sample shifted the distribution). Gene rank in deciles is stable across versions but absolute thresholds are NOT interchangeable.

## Subsets: non_cancer, non_neuro, controls

| Release | Subset | Removes | Use when |
|---------|--------|---------|----------|
| v2.1.1 | `non_cancer` | TCGA | Cancer-related variant analysis (avoids circularity) |
| v2.1.1 | `non_neuro` | Psychiatric/neuro cohorts | Neuropsychiatric variant analysis |
| v2.1.1 | `controls` | Cases with known disease (~60k samples) | Disease-association calibration |
| v3.1.2 | `non_v2` | v2 overlapping samples | Independent of v2 |
| v3.1.2 | `controls_and_biobanks` | Disease cases retained, biobanks emphasized | Population-level reference |
| v4 | `non_ukb` | UK Biobank exomes | When EUR-skew of UKB problematic |
| v4 | `non_neuro` | Deprecated | -- |
| v4 | `non_cancer` | Unnecessary (no TCGA in v4) | -- |

## SV Catalog and CNV

| Resource | Release | Samples | Coverage |
|----------|---------|---------|----------|
| gnomAD-SV v2 | Collins 2020 *Nature* 581:444 | 14,891 unrelated WGS | 433k SVs, GRCh37 |
| gnomAD-SV v4 | Nov 2023 | 63,046 unrelated WGS | 1,199,117 high-confidence SVs, GRCh38 |
| gnomAD-CNV v4 | Nov 2023 | 464,297 individuals (exome-derived gCNV) | Rare (AF < 1%) autosomal coding CNVs |

gnomAD-CNV v4 is the resource that democratized exome-derived CNV background frequencies; previously only ExAC-CNV provided this at scale.

## mtDNA (Laricchia 2022 *Genome Res* 32:569)

10,850 unique mtDNA variants across 56,434 individuals (v3.1). Frequencies reported per nuclear-ancestry AND per mitochondrial-haplogroup. Heteroplasmy >=10% threshold; ~1/250 individuals carry pathogenic mtDNA variant at heteroplasmy >=10%. mtDNA inheritance is non-Mendelian; standard ACMG criteria do not apply directly; use MITOMAP and HmtVar in parallel.

## VEP Version Pinning

Each gnomAD release pins to a VEP version:
- **v4 uses VEP 105** with GENCODE 39 / Ensembl 105 transcripts
- v2.1.1 uses VEP 85

A variant's consequence prediction can flip between v2 and v4 due to MANE Select adoption and transcript-set updates. Always pin VEP version when reproducing gnomAD annotations.

## Decision Tree by Query Scenario

| Scenario | Recommended path | Why |
|----------|------------------|-----|
| Single variant AF lookup | GraphQL API or myvariant.info | Lowest latency; returns full per-ancestry breakdown |
| ACMG BS1/BA1 application | `grpmax_faf95` from v4 | The ClinGen-recommended field |
| Gene-level LoF constraint (autosomes) | LOEUF from v4 March 2024 release | Larger sample, more stable |
| Gene-level LoF constraint (chrX/Y) | LOEUF from v2.1.1 | v4 X/Y constraint NOT released |
| Bulk rare-variant filter (cohort-scale) | Hail Table on GCS | No rate limits; full schema |
| SV frequency | gnomAD-SV v4 (WGS) or gnomAD-CNV v4 (exome) | Choose by data type |
| mtDNA frequency | v3.1 mtDNA release (Laricchia 2022) | Only gnomAD release with mtDNA |
| Cancer-variant analysis | v2.1.1 `non_cancer` subset OR v4 (no TCGA) | Avoid TCGA circularity in v2 |
| Comparison across builds | Use canonical SPDI or CA ID, normalize first | Liftover != native |

## Single Variant Query (GraphQL)

**Goal:** Retrieve exome + genome AF, grpmax, FAF95, and per-ancestry breakdown for one variant.

**Approach:** Hit gnomAD's GraphQL API with explicit dataset version; parse the nested response.

```python
import requests

GNOMAD_API = 'https://gnomad.broadinstitute.org/api'

def query_variant(chrom, pos, ref, alt, dataset='gnomad_r4'):
    '''Query gnomAD GraphQL for variant frequency + grpmax FAF95.

    dataset options: gnomad_r4 (v4.1, default), gnomad_r3, gnomad_r2_1
    '''
    query = '''
    query VariantById($variantId: String!, $dataset: DatasetId!) {
      variant(variantId: $variantId, dataset: $dataset) {
        variant_id
        rsids
        exome {
          ac
          an
          af
          homozygote_count
          filters
          populations { id ac an }
          faf95 { popmax popmax_population }
        }
        genome {
          ac
          an
          af
          homozygote_count
          filters
          populations { id ac an }
          faf95 { popmax popmax_population }
        }
      }
    }
    '''
    variant_id = f'{chrom}-{pos}-{ref}-{alt}'
    r = requests.post(GNOMAD_API,
                      json={'query': query, 'variables': {'variantId': variant_id, 'dataset': dataset}},
                      timeout=30)
    r.raise_for_status()
    return r.json().get('data', {}).get('variant')


def grpmax_faf95(payload):
    '''Extract the grpmax FAF95; the ACMG-grade frequency. Excludes bottleneck groups.'''
    exome = payload.get('exome') if payload else None
    if exome and exome.get('faf95'):
        return {
            'faf95': exome['faf95'].get('popmax'),
            'grpmax_ancestry': exome['faf95'].get('popmax_population'),
            'source': 'exome'
        }
    genome = payload.get('genome') if payload else None
    if genome and genome.get('faf95'):
        return {
            'faf95': genome['faf95'].get('popmax'),
            'grpmax_ancestry': genome['faf95'].get('popmax_population'),
            'source': 'genome'
        }
    return {'faf95': 0.0, 'grpmax_ancestry': None, 'source': 'absent'}
```

## ACMG BS1/BA1 Application

**Goal:** Apply Whiffin max-credible-AF framework to a candidate variant.

**Approach:** Compute the gene-specific BS1 threshold from disease parameters, compare to `grpmax_faf95`.

```python
def max_credible_af(prevalence, max_allelic_contribution=1.0, max_genetic_contribution=1.0,
                    penetrance=1.0):
    '''Whiffin 2017 max-credible-AF formula.

    Args:
        prevalence: disease prevalence (e.g., 1/10000 = 1e-4)
        max_allelic_contribution: max contribution of single allele to disease in any case
        max_genetic_contribution: max contribution of this gene to disease in any case
        penetrance: probability that variant carriers develop disease

    Returns: max-credible per-allele frequency under dominant inheritance (use /2 for AR)
    '''
    return (prevalence * max_genetic_contribution * max_allelic_contribution) / (penetrance * 2)


def apply_bs1_ba1(grpmax_faf95_val, max_credible, ba1_threshold=0.05):
    '''Apply ClinGen SVI BS1/BA1 criteria.

    BA1 default 5% per ClinGen SVI; VCEP-specific overrides exist (Hearing Loss = 0.5%).
    BS1 = max-credible-AF specific to gene+disease.
    '''
    if grpmax_faf95_val is None:
        return 'PM2_Supporting'  # Absent or ultra-rare
    if grpmax_faf95_val > ba1_threshold:
        return 'BA1'
    if grpmax_faf95_val > max_credible:
        return 'BS1'
    return None  # No criterion triggered; variant is consistent with rare-disease causation
```

## Gene-Level Constraint (LOEUF)

**Goal:** Retrieve gene constraint metrics with awareness of version mismatch for chrX/Y.

**Approach:** Use v4 LOEUF for autosomes; fall back to v2.1.1 for chrX/Y. Report LOEUF decile, not raw value, to avoid cross-version comparison errors.

```python
def query_gene_constraint(gene_symbol, dataset='gnomad_r4'):
    '''Pull gene constraint metrics. Note: v4 has no chrX/Y constraint; use v2 fallback.'''
    query = '''
    query GeneById($symbol: String!) {
      gene(gene_symbol: $symbol, reference_genome: GRCh38) {
        gene_id
        symbol
        chrom
        gnomad_constraint {
          oe_lof
          oe_lof_lower
          oe_lof_upper
          oe_mis
          oe_mis_upper
          pli
          mis_z
        }
      }
    }
    '''
    r = requests.post(GNOMAD_API,
                      json={'query': query, 'variables': {'symbol': gene_symbol}},
                      timeout=30)
    r.raise_for_status()
    gene = r.json().get('data', {}).get('gene')
    if gene is None:
        return None
    if gene.get('chrom') in ('X', 'Y'):
        gene['constraint_note'] = ('v4 constraint NOT released for chrX/Y; query v2.1.1 '
                                   'via gnomad_r2_1 dataset on the v2 endpoint')
    return gene
```

## Bulk Query via Hail (cohort-scale)

**Goal:** Filter millions of variants by AF, grpmax, or LOEUF without API rate limits.

**Approach:** Read gnomAD v4 Hail Table from Google Cloud Storage; use `hl.read_table()` + filter operations.

```python
import hail as hl

def init_hail_for_gnomad():
    '''Initialize Hail for gnomAD v4 GCS access. Requires Hail 0.2.130+.'''
    hl.init(default_reference='GRCh38')


def filter_rare_variants_hail(input_vcf, max_grpmax_faf95=0.0001, output_path='filtered.mt'):
    '''Filter input MT to variants below grpmax FAF95 threshold using gnomAD v4 exomes.'''
    ht_v4 = hl.read_table('gs://gcp-public-data--gnomad/release/4.1/ht/exomes/'
                          'gnomad.exomes.v4.1.sites.ht')
    mt = hl.import_vcf(input_vcf, reference_genome='GRCh38')
    mt = mt.annotate_rows(gnomad=ht_v4[mt.locus, mt.alleles])
    mt = mt.filter_rows(
        (hl.is_missing(mt.gnomad.grpmax_faf95)) |
        (mt.gnomad.grpmax_faf95.faf95 < max_grpmax_faf95)
    )
    mt.write(output_path, overwrite=True)
    return mt
```

## Per-Operation Failure Modes

**1. Using popmax/AF where grpmax_faf95 belongs**
- Trigger: Apply BS1 with raw AF instead of FAF95.
- Mechanism: Raw AF inflates for low-N populations; FAF95 is the lower-bound CI; conservative.
- Symptom: Pathogenic variants falsely categorized BS1 in small-N ancestry groups (especially MID with v4's smallest sample size).
- Fix: Use `grpmax_faf95.popmax` field; not `populations[i].af`.

**2. Failing to exclude bottleneck groups**
- Trigger: Compute grpmax including AMI, ASJ, FIN, REMAINING.
- Mechanism: Founder variants in bottleneck groups can reach AF > 5% but are not population-general; would falsely trigger BA1.
- Symptom: Founder-population pathogenic variants reported benign.
- Fix: Use gnomAD's pre-computed `grpmax_faf95` which excludes bottleneck groups by design.

**3. Querying v4 constraint for chrX/Y**
- Trigger: Pull LOEUF for DMD or USP9Y from v4 release.
- Mechanism: v4 March 2024 constraint release excluded sex chromosomes.
- Symptom: Missing or stale constraint metrics for X/Y genes.
- Fix: Query v2.1.1 LOEUF for chrX/Y; use v4 for autosomes; report LOEUF decile rather than raw value.

**4. Comparing LOEUF absolute values across v2/v4**
- Trigger: "v4 LOEUF for GENE-X is 0.45; v2 was 0.30; has it become more tolerant?"
- Mechanism: Larger v4 sample shifts the LOEUF distribution upward; first-decile threshold shifted v2 < 0.35 -> v4 < 0.6.
- Symptom: Genes appear to lose constraint between versions when they have not.
- Fix: Compare deciles, not absolute values; or stay within one version.

**5. v2 -> v4 liftover assumed equivalent**
- Trigger: Project v2 GRCh37 variants onto GRCh38 with CrossMap, treat as v4 native.
- Mechanism: ~0.5-1% of sites have different representations after liftover due to assembly fixes (e.g., gaps closed, contigs joined).
- Symptom: Inconsistent AFs at low rate; failed cross-version reproducibility.
- Fix: Query v4 native by GRCh38 coordinates directly; do not use liftover output as v4-equivalent.

**6. UKB sample contamination of grpmax**
- Trigger: Compute grpmax across v4 default subset; observe inflated NFE/SAS.
- Mechanism: 416,555 UK Biobank exomes dominate the v4 NFE+SAS subsets.
- Symptom: Variants common in UKB but rare globally falsely look common.
- Fix: Use `non_ukb` subset for grpmax when ancestry composition matters.

**7. v3 vs v4 confusion; "I want WGS"**
- Trigger: User says "I want WGS AFs" and pipeline pulls v4 genomes.
- Mechanism: v4 genomes are the SAME 76,215 v3 samples reprocessed against GRCh38; not independent.
- Symptom: WGS AFs appear identical to v3.1.2; not a bug, but worth flagging.
- Fix: Document that v4 genomes = v3 genomes reprocessed; for true independent WGS, no such resource yet exists at scale.

**8. Constraint applied to multi-isoform gene without transcript awareness**
- Trigger: Apply LOEUF "for the gene" when LoF is isoform-specific.
- Mechanism: gnomAD constraint is computed on the canonical transcript; tissue-specific or alternative isoforms may have different LoF tolerance.
- Symptom: Mis-prioritization of variants on minor transcripts.
- Fix: Cross-check with MANE Select; for isoform-specific LoF, use isoform-level constraint where available (rare).

## Reconciliation: When Sources Disagree

| Pattern | Likely cause | Action |
|---------|-------------|--------|
| ClinVar P vs gnomAD `grpmax_faf95` > 1% | Founder-population pathogenic; or ClinVar is stale low-star | Apply Whiffin max-credible-AF for the gene; check ClinVar star/freshness |
| v2 LOEUF < 0.35 vs v4 LOEUF = 0.5 | Distribution shifted with v4 sample size, not biology | Use deciles; v4 first decile = < 0.6 |
| v2 AF != v4 AF for same variant | Sample overlap (v3 in v4) + new exomes; expected | Trust v4 default; non-overlapping subsets via `non_v2` or `non_ukb` |
| Variant present in v3 genomes, absent v4 exomes | Variant outside exome capture region (intronic, intergenic) | Use v3.1.2 or v4 genomes for non-coding |
| gnomAD-SV v2 vs v4 different breakpoints | v2 GRCh37, v4 GRCh38; assembly fixes shift coords | Use v4 native; document build |
| Browser shows lower AF than Hail Table | Browser pre-filters with `filters=PASS`; Hail Table includes all | Apply `filters` filter in Hail explicitly |

## Quantitative Thresholds and Conventions

| Threshold | Convention | Source |
|-----------|-----------|--------|
| BA1 default | grpmax_faf95 > 5% in non-bottleneck group | Richards 2015 + ClinGen SVI |
| BS1 | grpmax_faf95 > gene-specific max-credible-AF | Whiffin 2017 |
| PM2_Supporting | Absent or ultra-rare in gnomAD | SVI 2020 downgrade |
| LOEUF first decile v2 | < 0.35 | Karczewski 2020 |
| LOEUF first decile v4 | < 0.6 | gnomAD constraint release March 2024 |
| Missense Z constrained | Z > 3.09 (~p < 0.001) | Samocha 2014 |
| mtDNA heteroplasmy carrier threshold | >=10% heteroplasmy | Laricchia 2022 |
| v4 sample size | 730,947 exomes + 76,215 genomes = 807,162 | gnomAD v4.0 release Nov 2023 |
| Bottleneck groups (excluded from grpmax) | AMI, ASJ, FIN, REMAINING | gnomAD v4 documentation |
| API rate limit | None published; ~10 req/s practical | gnomAD browser GraphQL |

## Common Errors

| Symptom | Cause | Solution |
|---------|-------|----------|
| `Cannot read property 'af' of undefined` | Variant not in dataset; `variant` returned null | Check `if payload is None`; absence is biologically informative |
| FAF95 = 0 for a known common variant | `grpmax_faf95` only computed when AN sufficient | Check AC and AN directly; FAF95 is 0 when N too low to estimate |
| Variant filter status `AC0` or `RF` | Failed gnomAD QC | Variants with non-`PASS` should usually be excluded from analysis |
| Different AFs between gnomAD browser and Hail Table | Browser auto-applies PASS filter; Hail does not | Filter `filters.size() == 0` (i.e., `PASS`) in Hail |
| LOEUF appears worse in v4 vs v2 | Distribution shifted with larger sample | Compare deciles, not absolute values |
| SV not found in v4-SV | v2-SV is GRCh37, v4-SV is GRCh38; or variant not called in WGS | Try v2-SV with liftover; or check gnomAD-CNV for exome-derived |
| mtDNA variant missing | Only v3.1 has mtDNA; not in v4 | Query v3.1 directly |

## Anticipated Reviewer Pushback

| Pushback | Standard response |
|----------|-------------------|
| "Why FAF95 instead of AF?" | Raw AF is point estimate; FAF95 is Poisson lower-bound 95% CI; ClinGen SVI recommendation for BS1/BA1. |
| "Why exclude FIN and ASJ from grpmax?" | Founder-population pathogenic variants reach high AF locally; including them would trigger false BA1. |
| "This LOEUF differs from the 2020 paper" | We use v4 March 2024 constraint (807k samples); 2020 paper used v2 (141k samples). Decile rank is stable; absolute shifted. |
| "Why not v4 for chrX constraint?" | v4 March 2024 constraint release is autosomes only; chrX/Y not yet released as of 2025. Fall back to v2. |
| "Why v3 if v4 exists?" | v4 genomes = v3 genomes reprocessed; for genome-only analysis they are equivalent. |
| "Variant exists in liftover v2 but not v4" | ~0.5-1% of sites differ post-assembly fixes; use v4 native, not liftover, as ground truth. |
| "Browser AF higher than this value" | Browser includes flagged variants by default; we filter on PASS. |

## References

- Chen S et al. 2024. A genomic mutational constraint map using variation in 76,156 human genomes. *Nature* 625:92.
- Karczewski KJ et al. 2020. The mutational constraint spectrum quantified from variation in 141,456 humans. *Nature* 581:434.
- Samocha KE et al. 2014. A framework for the interpretation of de novo mutation in human disease. *Nat Genet* 46:944.
- Collins RL et al. 2020. A structural variation reference for medical and population genetics. *Nature* 581:444.
- Laricchia KM et al. 2022. Mitochondrial DNA variation across 56,434 individuals in gnomAD. *Genome Res* 32:569.
- Whiffin N et al. 2017. Using high-resolution variant frequencies to empower clinical genome interpretation. *Genet Med* 19:1151.
- ClinGen guidance on gnomAD v4 (March 2024): `https://clinicalgenome.org/site/assets/files/9445/clingen_guidance_to_vceps_regarding_the_use_of_gnomad_v4_march_2024.pdf`
- gnomAD v4 release notes: `https://gnomad.broadinstitute.org/news/2023-11-gnomad-v4-0/`
- gnomAD v4.1 updates: `https://gnomad.broadinstitute.org/news/2024-05-gnomad-v4-1-updates/`

## Related Skills

- clinical-databases/clinvar-lookup - Pathogenicity classification (gnomAD AF used for BS1/BA1)
- clinical-databases/acmg-classification - Whiffin FAF95 framework applied to ACMG criteria
- clinical-databases/variant-prioritization - Rare-disease pipeline using grpmax_faf95
- clinical-databases/myvariant-queries - Aggregated queries including gnomAD overlay
- population-genetics/population-structure - Population stratification background
<!-- END FILE: clinical-databases/gnomad-frequencies/SKILL.md -->

## 子目录：clinical-databases/hla-typing

<!-- BEGIN FILE: clinical-databases/hla-typing/SKILL.md -->
---
name: bio-clinical-databases-hla-typing
description: Calls HLA class I and class II alleles at 2/4/6/8-field resolution from WGS/WES/RNA-seq/long-read data using OptiType, HLA-LA, T1K, Polysolver, HLA-HD, arcasHLA, StarPhase, or HIBAG imputation. Use when typing for HSCT, solid-organ transplant, neoantigen prediction, PGx screening (B*57:01, B*15:02, etc.), or disease-association studies, with reconciliation across tools and IPD-IMGT/HLA version mismatch handling.
tool_type: cli
primary_tool: T1K
---

## Version Compatibility

Reference examples tested with: OptiType 1.3.5, HLA-LA 1.0.4, T1K 1.0.6 (Song 2023), Polysolver 4.0, HLA-HD 1.7.1, arcasHLA 0.6.0, StarPhase 1.0+ (PacBio), HIBAG 1.40+, samtools 1.19+, bwa-mem 0.7.17+. IPD-IMGT/HLA database release frequency is quarterly; tools must be re-bundled with the current release to capture new alleles (~38,000 alleles at Jan 2024; ~43,000+ by Jul 2025).

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed package and adapt the example to match the actual API rather than retrying. Tool reference-bundle vintage matters more than algorithm choice for non-European cohorts; a 2022-bundled HLA-LA will silently miss thousands of post-2022 alleles dominant in African and South Asian ancestry.

# HLA Typing for Clinical Applications

**'Determine HLA genotype for HSCT / neoantigen prediction / PGx screening'** -> Call HLA class I (A, B, C) and class II (DRB1, DRB3/4/5, DQA1, DQB1, DPA1, DPB1) alleles at the resolution required by the downstream application.

- CLI (general-purpose all-rounder): `t1k --preset hla -1 R1.fq -2 R2.fq -f hla_reference.fa`
- CLI (class I gold standard from WES/WGS): `OptiTypePipeline.py -i R1.fq R2.fq -d`
- CLI (class I + II with PRG): `HLA-LA.pl --BAM input.bam --graph PRG_MHC_GRCh38_withIMGT`
- CLI (RNA-seq): `arcasHLA extract sample.bam -o out && arcasHLA genotype out/sample.extracted.fq.gz`
- CLI (long-read transplant-grade): PacBio HiFi StarPhase
- R (imputation from SNP arrays): `HIBAG::predict()` with ancestry-stratified reference panel

## Resolution Levels and What Each Application Requires

HLA nomenclature: **HLA-A\*02:01:01:01** = family : protein-changing : synonymous : intronic/UTR. **Expression suffixes:** `N` (null; DNA present, no protein expressed); `L` (low expression); `S` (secreted); `Q` (questionable); `A` (aberrant). A serologically apparent DR4-positive donor carrying `DRB4*01:03:01:02N` is functionally DR53-negative; a classic HSCT donor-selection failure.

| Application | Min resolution | Why |
|-------------|---------------|-----|
| **HSCT (unrelated donor)** | 6-field (12/12 match) | Null alleles + permissive DPB1 + Bw4/Bw6 + TCE3 core/non-core |
| **Solid organ transplant** | 4-field (2-digit:2-digit) | Eplet-level epitope match (HLAMatchmaker, PIRCHE-II) |
| **ICI neoantigen prediction** | 4-field class I + II | NetMHCpan-4.1 minimum |
| **HLA-disease association** | 4-field | Standard for GWAS HLA fine-mapping |
| **HLA-B\*57:01 abacavir screen** | 4-field, specific | Other \*57 alleles (\*57:03) do NOT cause HSS |
| **HLA-B\*15:02 carbamazepine** | 4-field, specific | \*15:02 only; \*15:01 (NFE-common) is not the risk allele |

## G-Groups vs P-Groups: Routinely Confused

- **G-groups** collapse alleles with identical DNA sequence across the antigen-recognition exons (class I exons 2-3; class II exon 2). Use for sequence-level lab QC.
- **P-groups** collapse alleles encoding identical mature protein across class I positions 1-90 (or class II beta1 domain positions 1-94). Use for epitope-based matching and neoantigen prediction.

## DRB1 + DRB3/4/5 Linkage: The Mandatory Sanity Check

DR haplotype linkage is fixed and is the canonical sanity check on any DR typing:

| DRB1 allele family | Linked DRB3/4/5 |
|---------------------|-----------------|
| DR1 (\*01), DR8 (\*08), DR10 (\*10) | None |
| DR3 (\*03), DR11 (\*11), DR12 (\*12), DR13 (\*13), DR14 (\*14) | DRB3 |
| DR4 (\*04), DR7 (\*07), DR9 (\*09) | DRB4 |
| DR15 (\*15), DR16 (\*16) | DRB5 |

Any caller reporting DRB4 with `DRB1*15:01` is broken or has a chimera. Use this as a routine QC check on automated pipelines.

## Algorithmic Taxonomy: Short-Read Tools

| Tool | Class I | Class II | KIR | Resolution | Approach | Fails when |
|------|---------|----------|-----|-----------|----------|-----------|
| **OptiType** (Szolek 2014 *Bioinformatics* 30:3310) | Yes (~97% 4-digit) | No | No | 4-field | ILP on exons 2-3 | Class II needed; very deep contamination |
| **Polysolver** (Shukla 2015 *Nat Biotechnol* 33:1152) | Yes (~95% 4-digit) | No | No | 4-field | Allele-specific ref alignment | Class II; non-European ancestry under-typing |
| **HLA-LA** (Dilthey 2019 *Bioinformatics* 35:4394) | Yes (~94% class I) | Yes (strong class II) | No | 4-field | Graph-based PRG | High RAM/disk (~30-100 GB scratch) |
| **T1K** (Song 2023 *Genome Res*) | Yes (~99% 4-digit) | Yes (~99%) | Yes (KIR + KIR3DL2 ligand) | 4-field | EM on consensus reference | Newer; less benchmarking on edge cases |
| **HLA-HD** (Kawaguchi 2017 *Hum Mutat* 38:788) | Yes (~98%) | Yes (~95%) | No | 4-field | Bowtie2 against IPD-IMGT | License required for commercial use |
| **arcasHLA** (Orenbuch 2020 *Bioinformatics* 36:33) | Yes (~100% 2-field) | Yes (>99% 2-field) | No | 4-field from RNA-seq | EM on STAR alignment | DNA-seq; population prior bias in non-EUR |
| **PHLAT, HLAforest, HLAminer, seq2HLA, HLAreporter** | Yes | Some | No | Mostly 2-4 field | Various | Older; superseded |

**Operational benchmark consensus:** in the Claeys 2023 *BMC Genomics* 13-tool benchmark (Matey-Hernandez 2018), HLA-HD was the top class-II caller and OptiType (WES) / arcasHLA (RNA) the class-I anchors. T1K (Song 2023, not in that benchmark) adds class I + II + KIR co-typing in one pass and is the 2024-2026 all-rounder recommendation for WGS/WES.

## Long-Read and Ultra-High-Resolution

| Tool | Platform | Resolution | Use case |
|------|----------|-----------|----------|
| **StarPhase** (PacBio official 2024+) | PacBio HiFi | 8-field (full-field) | Transplant-grade typing |
| **HLA*ASM** | PacBio HiFi | 8-field | Assembly-based |
| **FuFiHLA** (2025 bioRxiv) | PacBio HiFi + ONT R10 | 8-field | Platform-agnostic |
| **HLAminer streaming** (Warren 2025) | ONT long-read | 4-field | Streaming nanopore |
| **pbaa + StarPhase** | PacBio amplicon | 8-field | Cost-effective targeted typing |

ONT R9 was historically unreliable for null-allele discrimination due to homopolymer errors; R10.4 with duplex closes the gap for class I and is competitive with PacBio HiFi for class II. PacBio HiFi remains the gold standard for DPB1 4-field typing.

## SNP-Based HLA Imputation: The Ancestry Footgun

When only SNP-array genotypes are available (GWAS cohorts), use imputation:

| Tool | Approach | Reference panel | Best for |
|------|----------|----------------|----------|
| **HIBAG** (Zheng 2014 *Pharmacogenomics J* 14:192) | Random forest from SNP-array | Pre-fit per-ancestry classifiers (EUR, AS, AFR, HIS) | Population-stratified GWAS |
| **HLA-TAPAS** (Luo 2021 *Nat Genet* 53:1504) | Multi-ancestry imputation | 21,546 multi-ancestry reference | Cross-ancestry GWAS |
| **HLA*IMP:02** (Dilthey 2013) | Hidden Markov | EUR-only | Legacy; EUR-only |
| **SNP2HLA** (Jia 2013) | Beagle-based | Type 1 Diabetes / EUR | Older; EUR-only |
| **CookHLA** (Cook 2021) | Hybrid SNP2HLA + supplementary | Multi-ancestry refs | Modern alternative to SNP2HLA |
| **Multi-Ethnic Reference Panel** (Degenhardt 2019) | Multi-ancestry imputation | Cross-population samples | Cross-ancestry GWAS |

**Critical caveat:** imputation panel quality is the limiting factor, NOT the imputation algorithm. EUR-trained HIBAG on East-Asian SNP-array data produces confidently wrong calls. African-ancestry imputation accuracy drops 10-20 percentage points without an ancestry-matched panel (Douillard 2024 *HLA*). For populations underrepresented in IPD-IMGT/HLA itself, imputation is fundamentally limited regardless of method.

## Decision Tree by Scenario

| Scenario | Recommended path | Why |
|----------|------------------|-----|
| WGS/WES, class I only, max speed | OptiType | Best class-I accuracy, ILP-based, fast |
| WGS/WES, class I + II, general-purpose | T1K | Best all-rounder; class I + II + KIR co-typing |
| WGS/WES, class II reference grade | HLA-LA | Strong class-II accuracy (graph-based PRG) |
| RNA-seq tumor/normal for ICI | arcasHLA | RNA-seq native; expressed-allele-aware |
| Transplant 6+ field resolution | StarPhase (PacBio HiFi) | 8-field native; reference standard |
| Cost-effective targeted typing | pbaa + StarPhase amplicons | Lower cost than WGS |
| TCGA-style cancer cohort | Polysolver | TCGA convention; reproduces published values |
| SNP array (e.g., UKB) | HIBAG with population-matched panel | No sequencing data |
| Multi-ancestry GWAS | HLA-TAPAS | Cross-ancestry reference |
| Class II DPB1 4-field certainty | StarPhase or HiFi | Pre-2021 WES kits under-cover DPB1 |
| ONT-only data | T1K or HLAminer streaming for class I; ONT R10.4+ duplex for class II | R9 unreliable for nulls |

## HLA and Pharmacogenomics

| HLA allele | Drug | Reaction | Population enrichment | OR |
|------------|------|----------|----------------------|-----|
| **B\*57:01** | Abacavir | Hypersensitivity syndrome | All ancestries (5-8% NFE) | ~100 |
| **B\*15:02** | Carbamazepine, oxcarbazepine | SJS/TEN | Han Chinese, Thai, Malay (>=5%) | ~2500 |
| **B\*58:01** | Allopurinol | SJS/TEN | Han Chinese, Korean, Thai | ~580 |
| **A\*31:01** | Carbamazepine | DRESS, MPE | Europeans, Japanese | ~12 |
| **B\*13:01** | Dapsone | DDS | Han Chinese, SE Asian | -- |
| **B\*35:02** (NOT \*35:01) | Minocycline | DILI | All ancestries | -- |
| **B\*35:01** | TMP-SMX | DILI | Mixed | -- |
| **B\*14:01** | TMP-SMX | DILI | African | -- |
| **A\*33:01/03** | Terbinafine | DILI | Multi-ancestry | -- |
| **DRB1\*15:01 + DQB1\*06:02 haplotype** | Amoxicillin-clavulanate | DILI | Europeans | -- |
| **B\*15:13** | Phenytoin | SJS | Malaysian | -- |

**Operational rule:** Pharmacogenomic HLA screening requires 4-field resolution; 2-field (e.g., "B*15") misses the specific allele.

## Standard Workflow: T1K on WGS/WES

**Goal:** Type HLA class I, class II, KIR from short-read sequencing with KIR3DL1 Bw4/Bw6 ligand prediction.

**Approach:** Extract MHC-region reads, run T1K with IPD-IMGT/HLA reference; T1K outputs allele-pair calls + class II haplotype + KIR.

```bash
# Extract chr6:28-34 Mb plus alt contigs (alt-aware alignment is critical)
samtools view -b -h input.bam chr6:28000000-34000000 chr6_GL000250v2_alt chr6_GL000251v2_alt \
                              chr6_GL000252v2_alt chr6_GL000253v2_alt chr6_GL000254v2_alt \
                              chr6_GL000255v2_alt chr6_GL000256v2_alt > hla_region.bam

samtools sort -n hla_region.bam -o hla_sorted.bam
samtools fastq -1 hla_R1.fq -2 hla_R2.fq -s singletons.fq -0 /dev/null hla_sorted.bam

# Run T1K (preset hla; includes class I + II).
# Some releases ship the entry point as `run-t1k` (a wrapper script) rather than `t1k`;
# verify with `which run-t1k` / `which t1k` before scripting.
t1k --preset hla \
    -1 hla_R1.fq -2 hla_R2.fq \
    -f hla_idx/hlaidx_rna_seq.fa \
    -o sample_hla \
    --threads 8

# Output: sample_hla_genotype.tsv with HLA-A, B, C, DRB1, DRB3/4/5, DQA1, DQB1, DPA1, DPB1
```

## OptiType for Class I (TCGA-Compatible)

**Goal:** Type HLA-A, B, C at 4-field from WES with high accuracy.

**Approach:** Razers3-based alignment to IMGT class-I reference; ILP optimization to assign reads to allele pairs.

```bash
samtools view -h input.bam chr6:28000000-34000000 | samtools fastq -1 R1.fq -2 R2.fq -
OptiTypePipeline.py -i R1.fq R2.fq -d -o optitype_out -c config.ini
```

```ini
# config.ini
[mapping]
razers3=/usr/bin/razers3
threads=8
[ilp]
solver=glpk
threads=8
[behavior]
deletebam=true
unpaired_weight=0
use_discordant=false
```

## HLA-LA for Class II (PRG-Based)

**Goal:** Type both class I and class II at 4-field with the highest class-II accuracy of any WES tool.

**Approach:** Population reference graph (PRG) covering the MHC; HLA-LA maps reads to the PRG and infers the most likely paths.

```bash
HLA-LA.pl \
    --BAM input.bam \
    --graph PRG_MHC_GRCh38_withIMGT \
    --workingDir hla_la_out \
    --sampleID sample_name \
    --maxThreads 8

# Output: hla_la_out/sample_name/hla/R1_bestguess_G.txt
# Format: Locus, Allele1, Allele2, AverageCoverage
```

## arcasHLA for RNA-seq

**Goal:** Type HLA class I + II directly from RNA-seq for ICI neoantigen prediction.

**Approach:** Extract HLA-mapped reads from STAR BAM, EM-based genotype call against IMGT.

```bash
# Update reference to current IPD-IMGT/HLA release
arcasHLA reference --update

# Extract and genotype
arcasHLA extract sample.bam -o arcas_out --threads 8
arcasHLA genotype arcas_out/sample.extracted.fq.gz -o arcas_out --threads 8 --population prior

# Output: arcas_out/sample.genotype.json
```

## SNP-Array Imputation (HIBAG): For GWAS Cohorts

**Goal:** Impute HLA from SNP array genotypes when sequencing is unavailable.

**Approach:** HIBAG random-forest classifier with population-matched reference panel.

```r
library(HIBAG)

# Population-matched panel is critical; mismatch causes systematic errors
# Available panels: EUR, ASN, AFR, HIS (download from HIBAG release page)
load('European-HLA4-hg19.RData')

# Load PLINK genotype (.bed/.bim/.fam)
gen <- hlaBED2Geno(bed.fn='cohort.bed', fam.fn='cohort.fam', bim.fn='cohort.bim')

# Predict each locus
hla_A <- predict(model.list[['A']], gen, type='response+prob')
hla_B <- predict(model.list[['B']], gen, type='response+prob')
hla_DRB1 <- predict(model.list[['DRB1']], gen, type='response+prob')

# Filter on probability >= 0.5 for downstream use; lower for exploratory
```

## Per-Operation Failure Modes

**1. Alt-aware alignment missing**
- Trigger: BAM was aligned with bwa-mem against GRCh38 *without* `--alt-aware`; HLA reads are coerced to chr6 primary contigs.
- Mechanism: GRCh38 has ~8 alternate HLA contigs (chr6_GL000250v2_alt, etc.); without alt-aware alignment, reads from these regions get assigned to suboptimal positions on the primary chr6.
- Symptom: HLA typing accuracy drops 5-10 percentage points; high read-coverage variants get miscalled.
- Fix: Re-align the HLA region with bwa-mem-alt or use the original cDNA reference for HLA typing (extract reads to FASTQ first).

**2. Stale IPD-IMGT/HLA bundle**
- Trigger: Tool was installed in 2022 with the corresponding IPD-IMGT/HLA release; never updated.
- Mechanism: ~5000+ new alleles added between 2022 and 2025; new alleles dominant in under-represented ancestries.
- Symptom: Non-European samples get common alleles reported as ambiguous or as the closest legacy match.
- Fix: Update the tool's reference bundle (HLA-LA: rebuild PRG; T1K: re-run `t1k-build`; OptiType: update `data/hla_reference_dna.fasta`).

**3. EUR-trained imputation on non-EUR samples**
- Trigger: Use HIBAG European panel on East-Asian or African ancestry samples.
- Mechanism: Random forest was trained on EUR allele frequencies; non-EUR alleles missing from training set.
- Symptom: Confidently wrong calls; high probability assigned to incorrect alleles.
- Fix: Use ancestry-matched HIBAG panel; or switch to HLA-TAPAS multi-ancestry; or fall back to sequencing.

**4. Cross-mapping DRB-related loci**
- Trigger: Naive bwa-mem alignment without read-grouping at DRB1/DRB3/DRB4/DRB5.
- Mechanism: DRB1, DRB3, DRB4, DRB5 share extensive sequence identity; reads map ambiguously.
- Symptom: DR3/DR4/DR5 paralog reads contaminate DRB1 calls; haplotype linkage rule (e.g., DRB1*15:01 + DRB5) violated.
- Fix: Use HLA-LA or T1K which model paralogous loci jointly; verify DRB1+DRB3/4/5 haplotype rule.

**5. DPB1 under-coverage in pre-2021 WES kits**
- Trigger: Used SureSelect v5 or Nextera Rapid Capture WES; DPB1 reports homozygous typing.
- Mechanism: Pre-2021 capture kits under-covered DPB1 exon 2.
- Symptom: Heterozygous DPB1 reported as homozygous; affects HSCT matching.
- Fix: Confirm capture coverage at DPB1; if insufficient, supplement with targeted amplicon or use WGS/long-read.

**6. Class II expression-allele confusion**
- Trigger: Report `DRB4*01:03:01:02N` as functional DR53.
- Mechanism: N-suffix = null allele (DNA present but no protein expressed).
- Symptom: Functionally DR53-negative donor reported as DR53-positive; transplant matching failure.
- Fix: Parse 4-field suffix (`N`, `L`, `S`, `Q`, `A`); treat N as null in functional analysis; preserve full nomenclature for typing report.

**7. Specific allele vs allele family confusion**
- Trigger: PGx screen reports "B*57" carrier as abacavir-risk-positive.
- Mechanism: HLA-B*57 family includes \*57:01 (abacavir HSS risk), \*57:02, \*57:03 (no HSS risk).
- Symptom: False-positive abacavir contraindication; patient denied effective therapy.
- Fix: Report at 4-field minimum; B\*57:01 specifically, not B\*57.

**8. KIR co-typing mistaken for HLA**
- Trigger: Report KIR allele as HLA.
- Mechanism: KIR (chromosome 19) and HLA (chromosome 6) are functionally paired (KIR3DL1 binds HLA-Bw4) but are distinct loci.
- Symptom: Wrong locus annotation; downstream tools fail.
- Fix: Use T1K which co-types HLA + KIR + KIR3DL2 ligand and labels output correctly.

## Reconciliation: When Tools Disagree

| Pattern | Likely cause | Action |
|---------|-------------|--------|
| OptiType vs HLA-LA class I disagree | Stale reference bundle in one; non-EUR ancestry | Update both; rerun; prefer the one with current reference |
| HLA-LA vs T1K class II disagree | DRB1+DRB3/4/5 haplotype rule violated in one | Check haplotype linkage; the consistent caller is correct |
| HIBAG vs sequencing disagree | EUR-trained model on non-EUR sample | Trust sequencing; use ancestry-matched HIBAG panel |
| Tumor vs normal HLA differ | Tumor LOH at HLA locus (frequent in NSCLC, HNSCC) | Run LOHHLA / DASH to confirm somatic loss; report germline + somatic |
| DPB1 homozygous on WES, het on WGS | WES kit under-covers DPB1 exon 2 | Trust WGS; flag WES result as low confidence |
| Class I 4-field stable across tools, class II differs | Class II is fundamentally harder | Prefer HLA-LA or StarPhase for class II |
| arcasHLA vs OptiType for tumor RNA | arcasHLA returns expressed-allele only (may miss silenced allele due to LOH) | Confirm with DNA-based typing for transplant context |

## Quantitative Thresholds and Conventions

| Threshold | Convention | Source |
|-----------|-----------|--------|
| IPD-IMGT/HLA quarterly release | Updates Jan/Apr/Jul/Oct | IPD-IMGT/HLA database |
| Current allele count | ~43,000+ at Jul 2025 | IPD-IMGT/HLA database release notes (Barker DJ et al, *NAR* DB issue) |
| HLA region coordinates | chr6:28000000-34000000 (GRCh38) | Standard |
| HLA-LA RAM requirement | ~30-100 GB scratch | HLA-LA documentation |
| OptiType class I 4-digit accuracy | ~98% (1000G benchmark) | Claeys 2023 |
| Polysolver class I 4-digit accuracy | ~95% | Matey-Hernandez 2018 |
| HLA-HD class II accuracy | Top class-II WES tool | Claeys 2023 |
| T1K class I + II accuracy | ~99% / ~99% | Song 2023 |
| HIBAG probability cutoff | >=0.5 for clinical-grade; >=0.3 for exploratory | HIBAG documentation |
| 1000G allele coverage | ~60-70% of African-ancestry alleles still under-represented in IPD-IMGT/HLA | Robinson 2024 |
| HSCT matching standard | 10/10 or 12/12 at 6-field | NMDP/WMDA guidelines |
| TCE3 core alleles | DPB1\*02:01, \*04:01, \*04:02, \*23:01 | Arrieta-Bolaños 2022 *Blood* 140:659 |

## CIWD v3.0.0 Ambiguity Catalogue

Hurley 2020 *HLA* 95:516; compiled from >8M unrelated HSCT donors across 7 geographic/ancestral groups. Categories: Common (18%, n=545), Intermediate (17%, n=513), Well-Documented (65%, n=1,997) at 2-field. Replaces legacy CWD 2.0 (Mack 2013); many older pipelines still hardcode CWD 2.0; a quiet quality failure.

## TCE3 Core vs Non-Core (Arrieta-Bolaños 2022/2024 *Blood*)

DPB1 mismatch GvHD/relapse risk depends on TCE3 group:
- **Core (DPB1\*02:01, \*04:01, \*04:02, \*23:01):** GvHD reduction with permissive mismatch in the GvH direction.
- **Non-core:** Relapse-protection effects predominate.

Now operational in NMDP donor selection algorithms; legacy TCE3 frameworks (Crocchiolo 2009) lack this stratification.

## Common Errors

| Symptom | Cause | Solution |
|---------|-------|----------|
| HLA-DRA in output (DRB1 expected) | Tool confused paralogs | Use HLA-LA or T1K which model paralog loci correctly |
| Class II reports "no call" | Pre-2021 WES kit under-covers class II | Switch to WGS or amplicon |
| Tumor and normal HLA differ | LOH at HLA locus | Confirm with LOHHLA; report germline call as ground truth |
| Imputation reports rare allele with high probability | Reference panel mismatch with cohort ancestry | Switch to ancestry-matched panel |
| 4-field call but only 2-field appears in report | Tool default truncation | Use `--full-field` or equivalent flag |
| Same sample gives different 4-field calls across runs | Stochastic tie-breaking | Pin random seed; report all equally-supported calls |
| DRB4 with DRB1*15 | Linkage rule violated; bug or chimera | Re-run; check for sample swap |
| Null allele not reported in summary | Tool drops N-suffix; output is misleading | Use raw 4-field output; never strip suffixes for clinical reports |

## Anticipated Reviewer Pushback

| Pushback | Standard response |
|----------|-------------------|
| "Why T1K when HLA-LA is the published reference?" | T1K matches HLA-LA accuracy on class II while also typing class I + KIR in one pass with lower RAM; we cite both. |
| "These African-ancestry samples have low confidence" | IPD-IMGT/HLA still under-represents African ancestry (~30-40% allele gap); we ran with current 2025 release; for transplant we recommend long-read confirmation. |
| "DRB1 vs DRB3/4/5 reported inconsistently" | We verified DRB1+DRB3/4/5 linkage rule on each sample as routine QC; flagged violations for re-typing. |
| "Why is HLA-B\*15:01 not flagged for carbamazepine?" | \*15:01 (NFE common) is not the SJS risk allele; \*15:02 (Han Chinese) is. PGx requires 4-field specificity. |
| "Imputation results differ from sequencing" | Imputation panel quality is the limiting factor; EUR-trained HIBAG on non-EUR is unreliable; we used ancestry-matched panel. |
| "TCGA pipeline used Polysolver, why T1K?" | TCGA convention is Polysolver; for *current* analysis we use T1K which has better class-II and KIR coverage. We can reproduce Polysolver if back-comparison needed. |

## References

- Robinson J et al. 2024. 25 years of the IPD-IMGT/HLA Database. *HLA* 103:e15549.
- Barker DJ et al. 2026. The IPD-IMGT/HLA database: recent developments in sequence submission. *Nucleic Acids Res* 54:D1152.
- Szolek A et al. 2014. OptiType: precision HLA typing from NGS data. *Bioinformatics* 30:3310.
- Dilthey AT et al. 2019. HLA*LA; HLA typing from linearly projected graph alignments. *Bioinformatics* 35:4394.
- Song L et al. 2023. Efficient and accurate KIR and HLA genotyping with massively parallel sequencing data. *Genome Res* 33:923.
- Shukla SA et al. 2015. Comprehensive analysis of cancer-associated somatic mutations in class I HLA genes. *Nat Biotechnol* 33:1152.
- Kawaguchi S et al. 2017. HLA-HD: An accurate HLA typing algorithm for next-generation sequencing data. *Hum Mutat* 38:788.
- Orenbuch R et al. 2020. arcasHLA: high-resolution HLA typing from RNAseq. *Bioinformatics* 36:33.
- Claeys A et al. 2023. Benchmark of tools for in silico prediction of MHC class I and class II genotypes from NGS data. *BMC Genomics* 24:247.
- Matey-Hernandez ML et al. 2018. Benchmarking the HLA typing performance of Polysolver and Optitype in 50 Danish parental trios. *BMC Bioinformatics* 19:239.
- Zheng X et al. 2014. HIBAG; HLA genotype imputation with attribute bagging. *Pharmacogenomics J* 14:192.
- Luo Y et al. 2021. A high-resolution HLA reference panel capturing global population diversity. *Nat Genet* 53:1504.
- Hurley CK et al. 2020. Common, intermediate and well-documented HLA alleles in world populations: CIWD version 3.0.0. *HLA* 95:516.
- Arrieta-Bolaños E et al. 2022. A core group of structurally similar HLA-DPB1 alleles drives permissiveness after HCT. *Blood* 140:659.
- Arrieta-Bolaños E et al. 2024. Directionality of HLA-DP permissive mismatches improves risk prediction. *Blood* 144:1747.
- Douillard V et al. 2024. Optimal population-specific HLA imputation with dimension reduction. *HLA* 103:e15282.

## Related Skills

- clinical-databases/pharmacogenomics - HLA-drug interactions, abacavir/carbamazepine screening
- immunoinformatics/mhc-binding-prediction - Downstream HLA-peptide binding for neoantigen
- workflows/neoantigen-pipeline - HLA typing as upstream step
- clinical-databases/clinvar-lookup - HLA disease associations
- population-genetics/population-structure - Ancestry-aware imputation context
<!-- END FILE: clinical-databases/hla-typing/SKILL.md -->

## 子目录：clinical-databases/msi-detection

<!-- BEGIN FILE: clinical-databases/msi-detection/SKILL.md -->
---
name: bio-clinical-databases-msi-detection
description: Calls microsatellite instability from WES/WGS/targeted-panel with MSIsensor, MSIsensor-pro, MSIsensor-ct (panel-aware), mSINGS, and MANTIS for FDA pembrolizumab MSI-H pan-tumor / Lynch syndrome / dMMR ICI biomarker. Use when stratifying ICI eligibility (Le 2015), pairing MSI with TMB-H (Sha 2020 / Salem 2018), screening Lynch syndrome (universal IHC + MSI), or distinguishing MSI-H tumors from POLE-exo hypermutator with overlapping signatures.
tool_type: cli
primary_tool: MSIsensor-pro
---

## Version Compatibility

Reference examples tested with: MSIsensor-pro 1.2+, MSIsensor 0.6+, MANTIS 1.0.5+, samtools 1.19+, mSINGS 5.6+, pandas 2.2+, cyvcf2 0.30+. FDA pembrolizumab MSI-H / dMMR pan-tumor approval is from 2017 (Le 2015 *NEJM*; KEYNOTE-016/164/158); approval extended to colorectal first-line in 2020.

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `<tool> --version`

If code throws ImportError, AttributeError, or TypeError, introspect the installed package and adapt the example to match the actual API rather than retrying. MSIsensor-pro replaces MSIsensor for tumor-only assays; MSIsensor-ct is the bTMB-equivalent for ctDNA panels.

# MSI Detection; The Companion ICI Biomarker to TMB

**'Detect MSI status from this somatic sequencing data'** -> Profile microsatellite instability across canonical loci (Bethesda 5 panel + extended NGS-derived sites); classify MSI-H / MSS / MSI-L per Bethesda / FDA / KEYNOTE convention.

- CLI (recommended tumor-only): `msisensor-pro msi -d microsatellites.list -t tumor.bam -o msi_out -b 16`
- CLI (paired tumor-normal): `msisensor msi -d microsatellites.list -n normal.bam -t tumor.bam -o msi_out`
- CLI (ctDNA / blood MSI): `msisensor-ct ...`
- CLI (older WES standard): `mantis -t tumor.bam -n normal.bam -b targets.bed --threads 8`

## The Regulatory and Trial Landscape

| Event | Year | Threshold | Notes |
|-------|------|-----------|-------|
| **Le 2015** *NEJM* | 2015 | MSI-H + ICI in CRC | The seminal paper: pembrolizumab in MSI-H CRC ORR 40% vs 0% MSS |
| **FDA pembrolizumab MSI-H / dMMR pan-tumor** | 2017 | MSI-H | First tissue-agnostic FDA approval (KEYNOTE-016/164/158) |
| **FDA pembrolizumab first-line MSI-H CRC** | 2020 | MSI-H + first-line CRC | KEYNOTE-177 |
| **CheckMate 142** | 2017-2018 | MSI-H + nivolumab/ipilimumab | Pan-tumor MSI-H second-line |
| **ESMO 2024** | 2024 | MSI-H | Maintained pan-tumor MSI-H biomarker |
| **Universal Lynch screening** | -- | IHC + MSI on all CRC <= 70 yr | NCCN / ACG / EGAPP guidelines |

## MSI vs dMMR vs TMB-H: The Conceptual Hierarchy

| Term | Definition | Method | Relationship |
|------|-----------|--------|--------------|
| **dMMR (deficient MMR)** | Loss of MMR protein function | IHC (MLH1, MSH2, MSH6, PMS2) | Causes MSI |
| **MSI-H** | Microsatellite instability high | PCR-based Bethesda or NGS | Consequence of dMMR |
| **Lynch syndrome** | Germline MMR mutation | Germline sequencing | Causes ~50% of MSI-H CRC; rest are sporadic (MLH1 hyper-methylation) |
| **TMB-H** | >= 10 mut/Mb | NGS panel / WES | Statistical correlate of MSI-H |
| **POLE-exo hypermutator** | POLE proofreading defect | Sequencing / signatures | Hypermutator WITHOUT MMR-D; MSI-stable typically |

**MSI-H + TMB-H overlap** (Chalmers 2017 *Genome Med* 9:34):
- ~83% of MSI-H tumors are TMB-H.
- ~16% of TMB-H solid tumors are MSI-H.
- Sha 2020 *Cancer Discov*: MSI-H is the more established dMMR biomarker for ICI decisions; TMB-H not additive.

**POLE-exo vs MMR-D:**
- POLE-exo (SBS10a/10b): hypermutator (100-300 mut/Mb pure); typically MSI-stable.
- MMR-D (SBS6/15/26/44 + ID1/2): 30-50 mut/Mb typical; MSI-H.
- POLE-exo + MMR-D (SBS14 + SBS20): ultra-hypermutator >=500 mut/Mb; MSI-H.

## Tool Taxonomy

| Tool | Paired | Tumor-only | ctDNA | Algorithm | Fails when |
|------|--------|-----------|-------|-----------|-----------|
| **MSIsensor** (Niu 2014 *Bioinformatics*) | Yes | No | No | Bayesian + read-length distribution | Tumor-only data (no baseline); cohort baseline missing |
| **MSIsensor-pro** (Jia 2020 *Genom Proteom Bioinform*) | Optional | **Yes** | No | Distribution comparison to baseline | Baseline cohort not provided; panel < 50 loci |
| **MSIsensor-ct** (Han 2021 *Brief Bioinform*) | -- | -- | **Yes** | cfDNA-aware | Tumor fraction < 3%; low ctDNA shed |
| **MANTIS** (Kautto 2017 *Oncotarget*) | Yes | No | No | Step-wise difference | Tumor-only; low coverage at microsatellites |
| **mSINGS** (Salipante 2014 *Clin Chem*) | -- | Yes | No | Background panel (unstable-loci fraction) | Background panel poorly characterized for cohort |

**Operational consensus 2024-2026:**
- **Tumor + paired normal WES:** MSIsensor or MANTIS.
- **Tumor-only assay** (commercial panels, often unpaired): MSIsensor-pro with reference baseline.
- **ctDNA / liquid biopsy:** MSIsensor-ct.
- **Lynch screening:** IHC FIRST (rules out 90%+); MSI-PCR / NGS confirmatory.

## Decision Tree by Scenario

| Scenario | Recommended path | Why |
|----------|------------------|-----|
| Tumor + paired normal WES | MSIsensor (standard) | Reference paired-normal comparison |
| Tumor-only WES/panel | MSIsensor-pro with panel baseline | No matched normal needed |
| ctDNA / liquid biopsy | MSIsensor-ct | cfDNA-aware |
| Lynch syndrome screening | Universal IHC + MSI (NCCN) | IHC catches 90%+; MSI for IHC-equivocal |
| FDA pembrolizumab eligibility | Validate per FoCR PCR + IHC + NGS concordance | Cross-platform required |
| MSI-H + TMB-H concurrence | MSI-H is primary biomarker | Sha 2020; TMB-H not additive |
| POLE+MMR ultra-hypermutator | Sigprofiler signatures (SBS14, SBS20) | Mechanism beyond MSI alone |
| Sporadic MSI-H | Confirm MLH1 hypermethylation; rule out Lynch | Distinguishes sporadic vs germline |
| MSI-stable + TMB-H | Investigate POLE-exo signature (SBS10a/10b) | POLE-exo causes hypermutator without MSI |
| Pan-tumor screening | MSI + IHC + TMB combined | Multiple modalities for ICI eligibility |

## Bethesda Panel and Modern NGS-Derived Loci

The original **NCI/Bethesda reference panel** (Boland 1998) used BAT-25 and BAT-26 plus three dinucleotide markers (D2S123, D5S346, D17S250); >= 2 of 5 loci unstable -> MSI-H. Modern PCR assays use the **mononucleotide pentaplex** (the current clinical standard), which replaced the dinucleotide markers for improved cross-population specificity:
- **BAT-25** (chr4)
- **BAT-26** (chr2)
- **NR-21** (chr14)
- **NR-24** (chr2)
- **MONO-27** (chr2)

NGS-based MSI panels use 50-1000+ microsatellite loci. MSI-H requires unstable status at >=40% of tested loci typically (varies by panel calibration).

## Standard Workflow: MSIsensor-pro Tumor-Only

**Goal:** Compute MSI status from tumor-only WES/panel.

**Approach:** Generate baseline from population reference; compare patient tumor.

```bash
# Generate microsatellite list from reference genome (one-time)
msisensor-pro scan -d /reference/GRCh38.fa -o microsatellites.list -p 1 -m 5

# Generate baseline from N normal control samples (one-time per panel)
msisensor-pro baseline -d microsatellites.list -i normal_samples.list -o baseline.list -b 16

# Score tumor sample. The `-i sample_id` flag is uncommon: in typical msisensor-pro
# usage the sample identifier is derived from the BAM file -- verify the flag set
# against `msisensor-pro pro --help` for the installed release.
msisensor-pro pro \
    -d microsatellites.list \
    -t tumor.bam \
    -o msi_output \
    -b 16 \
    --baseline baseline.list

# Output: msi_output_all (raw); msi_output_unstable (unstable loci); msi_output.txt (summary)
# Critical column: %_unstable. Threshold MSI-H typically >= 20-30% depending on panel.
```

## Paired Tumor-Normal MSIsensor

```bash
msisensor msi \
    -d microsatellites.list \
    -n normal.bam \
    -t tumor.bam \
    -o msi_paired_out \
    -b 16

# Output: %_unstable in paired comparison
# MSI-H threshold: >= 20% by FoCR guidance; varies 10-30% across studies
```

## MANTIS Step-wise Difference

```bash
mantis.py \
    -t tumor.bam \
    -n normal.bam \
    -b microsatellite_targets.bed \
    --threads 8 \
    -o mantis_output

# Output: mantis_output.kmer_counts (raw), mantis_output (status)
# Threshold MSI-H: stepwise difference > 0.4 (default)
```

## MSI-H Classification Logic

```python
import pandas as pd


def classify_msi(unstable_percentage, panel_calibrated_cutoff=20.0):
    '''Classify MSI status from percentage of unstable loci.

    Bethesda PCR: >=2 of 5 unstable -> MSI-H (40% loci)
    NGS: panel-specific cutoffs typically 10-30%
    Concordance: MSI-PCR + IHC + NGS should agree (FoCR)
    '''
    if unstable_percentage >= panel_calibrated_cutoff:
        return 'MSI-H'
    elif unstable_percentage >= panel_calibrated_cutoff / 2:
        return 'MSI-L (intermediate; treat as MSS clinically per FDA)'
    else:
        return 'MSS'


def msi_lynch_workflow(msi_status, ihc_results, mlh1_methylation_status, germline_test):
    '''Standard Lynch syndrome workflow.

    Args:
        msi_status: 'MSI-H' / 'MSS' / 'MSI-L'
        ihc_results: dict {MLH1: 'retained' or 'loss', MSH2, MSH6, PMS2}
        mlh1_methylation_status: 'methylated' (sporadic) / 'unmethylated' (Lynch suspect)
        germline_test: 'positive' / 'negative' / 'not_performed'
    '''
    if msi_status != 'MSI-H':
        return 'No further Lynch screening indicated'

    ihc_loss = [gene for gene, status in ihc_results.items() if status == 'loss']
    if not ihc_loss:
        return 'MSI-H with retained IHC; consider Lynch with germline testing'

    if 'MLH1' in ihc_loss:
        if mlh1_methylation_status == 'methylated':
            return 'Sporadic MSI-H (MLH1 hypermethylation); not Lynch'
        elif mlh1_methylation_status == 'unmethylated':
            return 'Lynch suspect (MLH1 loss without methylation); proceed with germline testing'
        else:
            return 'MLH1 loss; perform methylation test'

    return f'MSH2/6/PMS2 loss ({", ".join(ihc_loss)}); strong Lynch suspect; germline testing'


def msi_tmb_ici_decision(msi_status, tmb_value, tumor_type=None, dmmr_ihc=None):
    '''Integrated ICI eligibility from MSI + TMB.

    Sha 2020: MSI-H is primary biomarker; TMB-H not additive.
    McGrail 2021: TMB-H NOT endorsed for breast/prostate/glioma alone.
    '''
    msi_high = msi_status == 'MSI-H'
    dmmr_positive = dmmr_ihc == 'positive'
    tmb_h = tmb_value >= 10

    if msi_high or dmmr_positive:
        return ('ICI eligible: MSI-H or dMMR (FDA pembrolizumab 2017 pan-tumor; KEYNOTE-016/164/158); '
                'TMB-H is not additive (Sha 2020).')
    if tmb_h and tumor_type and tumor_type.lower() in ('breast', 'prostate', 'glioma'):
        return ('TMB-H but tumor type excluded by ESMO 2024 / McGrail 2021. '
                'Consider tumor-type-specific cutoff.')
    if tmb_h:
        return 'TMB-H pan-tumor (FDA pembrolizumab 2020); ICI eligible.'
    return 'MSS + TMB-low. Standard chemo per tumor type.'
```

## Per-Operation Failure Modes

**1. Tumor-only with paired-normal tool**
- Trigger: Run MSIsensor on tumor-only BAM.
- Mechanism: MSIsensor requires paired normal for baseline comparison.
- Symptom: Tool errors or produces unstable noisy result.
- Fix: Use MSIsensor-pro for tumor-only; or use mSINGS background-panel approach.

**2. Panel size too small**
- Trigger: 30-locus panel called MSI-H based on 20% threshold (= 6 unstable loci).
- Mechanism: Small panel + stochastic unstable rates produce high false-positive rates.
- Symptom: False-positive MSI-H in WES-comparable panels with < 50 microsatellite loci.
- Fix: Validate panel calibration with reference cohort; use panel-specific cutoff; minimum 50 informative loci.

**3. IHC vs MSI discordance not investigated**
- Trigger: IHC retains all four MMR proteins; MSI-H by sequencing.
- Mechanism: IHC may miss subtle loss; MSI may include MSH6-only subtype (more variable); rare germline POLE+MMR ultra-hypermutators show MSI.
- Symptom: Apparent discordance; classification ambiguous.
- Fix: Cross-check with germline MMR sequencing; check for POLE-exo on Sigprofiler.

**4. MSI-H + Lynch syndrome confusion**
- Trigger: Report MSI-H tumor as "Lynch syndrome".
- Mechanism: ~50% of MSI-H CRC is sporadic (MLH1 hypermethylation, not germline Lynch).
- Symptom: Incorrect family counseling; wrong screening.
- Fix: Apply IHC + MLH1 methylation + germline testing workflow.

**5. POLE-exo hypermutator labeled MSI**
- Trigger: Tumor with 200 mut/Mb POLE-exo signature labeled MSI-H.
- Mechanism: Pure POLE-exo causes hypermutator WITHOUT MSI (different repair mechanism); apparent MSI-H call may be a false positive in high-mutation context.
- Symptom: Misclassification; ICI eligibility still positive but for different mechanism.
- Fix: Run Sigprofiler signatures (SBS10a/10b vs SBS6/15/26/44); confirm POLE-exo via SBS10 contribution.

**6. ctDNA MSI without sufficient tumor fraction**
- Trigger: Run MSIsensor-ct on cfDNA with <1% tumor fraction.
- Mechanism: Low ctDNA fraction produces noise-dominated unstable locus counts.
- Symptom: False-negative or unstable MSI call.
- Fix: Estimate tumor fraction first (ichorCNA); require >= 3% for reliable cfDNA MSI.

**7. Universal screening missed**
- Trigger: CRC patient < 70 yr without IHC / MSI.
- Mechanism: NCCN / ACG universal Lynch screening required; without it, Lynch syndrome undiagnosed.
- Symptom: Family loses screening benefit.
- Fix: Universal IHC + MSI on all CRC < 70; institute reflex testing.

**8. MSI-L treated as actionable**
- Trigger: Report MSI-L (intermediate) as ICI-eligible.
- Mechanism: FDA approval specifies MSI-H; MSI-L = MSS clinically.
- Symptom: ICI given on insufficient indication; reimbursement issues.
- Fix: Apply MSI-H threshold strictly per FDA; MSI-L = MSS.

## Reconciliation: When Sources Disagree

| Pattern | Likely cause | Action |
|---------|-------------|--------|
| PCR Bethesda MSI-H vs NGS MSS | Bethesda panel uses 5 loci only; less sensitive | Trust NGS with >=50 informative loci |
| NGS MSI-H vs IHC retained | Subtle MMR loss; MSH6-only subtype; or POLE-exo | Confirm with germline + POLE-exo signature analysis |
| Paired-normal MSI-H + tumor-only MSS | Sample swap or low tumor purity in tumor-only | Re-validate; check purity (>=20% required) |
| MSIsensor-pro vs MSIsensor (paired) | Different baseline thresholds | Apply panel-specific calibration |
| MSI-H suspected but tools differ | Borderline mutational burden | Use signature analysis (SBS6/15/26/44) as orthogonal evidence |
| ctDNA MSI vs tissue MSI | Tumor fraction low | Trust tissue; estimate ctDNA fraction |

## Quantitative Thresholds and Conventions

| Threshold | Convention | Source |
|-----------|-----------|--------|
| Bethesda MSI-H | >= 2/5 unstable | Boland 1998 |
| NGS MSI-H cutoff | 10-30% unstable loci (panel-specific) | Various |
| MANTIS MSI-H threshold | Step-wise difference > 0.4 | Kautto 2017 |
| MSIsensor MSI-H threshold | >= 20% by FoCR | Friends of Cancer Research |
| Minimum informative loci | >= 50 NGS loci | Panel-design convention |
| ctDNA tumor fraction minimum | >= 3% for reliable cfDNA MSI (depth-dependent operational floor; MSIsensor-ct reports 0.05% LOD only at >= 3000x) | Operational convention |
| Tumor purity minimum | >= 20% | Standard |
| FDA approval | MSI-H or dMMR pan-tumor (2017) | KEYNOTE-016/164/158 |
| First-line MSI-H CRC | KEYNOTE-177 (2020) | -- |
| MSI-H -> TMB-H rate | ~83% | Chalmers 2017 |
| TMB-H -> MSI-H rate | ~16% | Chalmers 2017 |
| Sporadic MSI-H mechanism | ~50% MLH1 hypermethylation | Various |
| Universal screening cutoff | CRC <= 70 yr | NCCN / ACG |

## Common Errors

| Symptom | Cause | Solution |
|---------|-------|----------|
| MSI-H + IHC retained discordance | Subtle loss; MSH6-only; or rare hypermutator | Cross-check germline + signatures |
| Borderline MSI call | Panel too small | Use >= 50 informative loci |
| Tumor-only MSI low confidence | Background subtraction needed | Use MSIsensor-pro with cohort baseline |
| MSI-H + TMB-H reported additive | Tautology per Sha 2020 | MSI-H is primary; TMB-H not additive |
| POLE-exo labeled MMR-D | Different mechanism; mutation count differs | Run Sigprofiler; SBS10a/10b is POLE-exo |
| Sporadic MSI-H mis-labeled Lynch | Need MLH1 methylation test | Confirm MLH1 methylation + germline |

## Anticipated Reviewer Pushback

| Pushback | Standard response |
|----------|-------------------|
| "MSI-H + TMB-H both reported additive" | Sha 2020 *Cancer Discov*: MSI-H is the primary biomarker; TMB-H is statistical correlate. We report MSI-H first; TMB-H reported but noted not additive. |
| "Why MSIsensor-pro instead of MSIsensor?" | MSIsensor requires paired normal; MSIsensor-pro handles tumor-only via cohort baseline. Most commercial panels are tumor-only. |
| "MSI-PCR vs NGS discordant" | Bethesda 5-locus panel is less sensitive; we use NGS >=50 informative loci for confirmation. |
| "Universal Lynch screening?" | NCCN / ACG recommend reflex IHC + MSI on all CRC <= 70 yr; we implemented universal screening protocol. |
| "POLE-exo hypermutator with MSI-H?" | Sigprofiler signature analysis distinguishes: SBS10a/10b = POLE-exo (typically MSI-stable); SBS6/15/26/44 = MMR-D. POLE+MMR concurrent produces ultra-hypermutator. |
| "MSI-L?" | FDA approval specifies MSI-H; MSI-L = clinically MSS; we apply MSI-H threshold strictly. |
| "ctDNA MSI viability?" | MSIsensor-ct works if tumor fraction >= 3%; we estimate via ichorCNA; below threshold falls back to tissue. |

## References

- Le DT et al. 2015. PD-1 blockade in tumors with mismatch-repair deficiency. *NEJM* 372:2509. (The seminal paper)
- Marabelle A et al. 2020. Efficacy of pembrolizumab in patients with noncolorectal high MSI/dMMR cancer. *J Clin Oncol* 38:1.
- Niu B et al. 2014. MSIsensor: microsatellite instability detection using paired tumor-normal sequence data. *Bioinformatics* 30:1015.
- Jia P et al. 2020. MSIsensor-pro: fast, accurate, and matched-normal-sample-free detection of microsatellite instability. *Genomics Proteomics Bioinformatics* 18:65.
- Han X et al. 2021. MSIsensor-ct: microsatellite instability detection using cfDNA sequencing data. *Brief Bioinform* 22:bbaa402.
- Kautto EA et al. 2017. Performance evaluation for rapid detection of pan-cancer microsatellite instability with MANTIS. *Oncotarget* 8:7452.
- Salipante SJ et al. 2014. Microsatellite instability detection by NGS. *Clin Chem* 60:1192.
- Boland CR et al. 1998. National Cancer Institute workshop on microsatellite instability for cancer detection and familial predisposition. *Cancer Res* 58:5248.
- Salem ME et al. 2018. Landscape of tumor mutation load, mismatch repair deficiency, and PD-L1 expression in a large patient cohort of gastrointestinal cancers. *Mol Cancer Res* 16:805.
- Chalmers ZR et al. 2017. Analysis of 100,000 human cancer genomes reveals the landscape of tumor mutational burden. *Genome Med* 9:34.
- Sha D et al. 2020. Tumor mutational burden as a predictive biomarker in solid tumors. *Cancer Discov* 10:1808.
- Vanderwalde A et al. 2018. Microsatellite instability status determined by next-generation sequencing and compared with PD-L1 and tumor mutational burden in 11,348 patients. *Cancer Med* 7:746.

## Related Skills

- clinical-databases/tumor-mutational-burden - TMB as related ICI biomarker
- clinical-databases/somatic-signatures - SBS6/15/26/44 MMR-D signatures + SBS10a/10b POLE-exo
- clinical-databases/clinvar-lookup - Lynch syndrome variant pathogenicity (MLH1, MSH2, MSH6, PMS2)
- clinical-databases/variant-prioritization - Germline MMR variant prioritization for Lynch
- variant-calling/clinical-interpretation - Clinical reporting
<!-- END FILE: clinical-databases/msi-detection/SKILL.md -->

## 子目录：clinical-databases/myvariant-queries

<!-- BEGIN FILE: clinical-databases/myvariant-queries/SKILL.md -->
---
name: bio-clinical-databases-myvariant-queries
description: Queries myvariant.info BioThings aggregator for ClinVar, gnomAD, dbSNP, dbNSFP, COSMIC, CADD, and CIViC annotations in batched, version-tracked requests. Use when annotating variant lists from multiple databases simultaneously without managing per-source APIs, and when reproducibility-grade analyses require recording source data versions via _meta.
tool_type: python
primary_tool: myvariant
---

## Version Compatibility

Reference examples tested with: myvariant 1.0.0+, requests 2.31+, pandas 2.2+. myvariant.info aggregates >=21 sources; the operative version of each source is queryable via the `_meta` field and the `/v1/metadata` endpoint.

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed package and adapt the example to match the actual API rather than retrying. dbNSFP version drift is the dominant staleness vector: AlphaMissense was added to dbNSFP v4.4 (~2024); querying `dbnsfp.alphamissense.score` returns whatever version of dbNSFP is currently loaded; check `_meta.src.dbnsfp.version`.

# MyVariant.info Queries; Aggregated Annotation

**'Annotate my variants with ClinVar + gnomAD + CADD + AlphaMissense in one batch'** -> Query the BioThings myvariant.info aggregator with field selection and version tracking, then parse nested responses.

- Python: `myvariant.MyVariantInfo().getvariant(hgvs_or_rsid, fields=['clinvar', 'gnomad_exome', 'dbnsfp'])`
- Python (batch): `mv.getvariants(ids_list, fields=...)`; up to 1000 IDs per request
- Python (search): `mv.query('clinvar.gene.symbol:BRCA1 AND clinvar.clinical_significance:Pathogenic')`
- REST: `GET https://myvariant.info/v1/variant/{hgvs_or_id}?fields=...`
- Bulk: `POST https://myvariant.info/v1/variant` with comma-separated IDs

## BioThings Architecture (Lelong 2022 *Bioinformatics*)

myvariant.info is one of three flagship BioThings APIs (with MyGene.info and MyChem.info). All three share the BioThings SDK, which auto-deploys an Elasticsearch index from heterogeneous source files via per-source dataloaders. The 2022 paper formalized the SDK; the architecture itself is older (Xin 2016 *Genome Biol*).

- Elasticsearch-backed: queries use Lucene operators (AND, OR, NOT, range like `dbnsfp.cadd.phred:>20`)
- Dotted-field-name syntax for nested JSON
- The `_id` field is canonical HGVS-g per record (e.g., `chr7:g.117199644G>A`)

## Aggregated Sources: ~21 and Counting

| Source | What | Notes |
|--------|------|-------|
| ClinVar | Pathogenicity | Weekly refresh |
| gnomAD v4 exomes + genomes | Population AF | grpmax_faf95 surfaced |
| dbSNP Build 156 | rsID + alleles | RsMergeArch resolved |
| dbNSFP v4.x | Meta-aggregator of 40+ in silico predictors | Includes AlphaMissense, REVEL, BayesDel |
| CADD | Deleteriousness | Genome-wide |
| CIViC | Cancer interpretation | Per-disease |
| COSMIC | Somatic variants | Catalogue of Somatic Mutations |
| EVS | Exome Variant Server | Legacy (deprecated by gnomAD) |
| ExAC | ExAC frequencies | Legacy (superseded by gnomAD) |
| GRASP | GWAS associations | -- |
| GWAS Catalog | Curated GWAS | -- |
| Wellderly | Disease-resistant elderly cohort | -- |
| EMV | -- | -- |
| DOCM | Database of Curated Mutations | -- |
| ICGC | International cancer | -- |
| MutDB | -- | -- |
| GO | Gene Ontology | -- |
| Snpeff | snpEff annotations | -- |
| GeneReviews | Disease/gene reviews | -- |
| MutPred | Functional impact | -- |

**dbNSFP is itself an aggregator.** Querying `dbnsfp.alphamissense.score` returns the version that dbNSFP loaded, not AlphaMissense direct. The lag from publication (Cheng 2023 *Science*) to integration into myvariant.info is typically 6-18 months via dbNSFP.

## Scopes and Query Forms

| Endpoint | Method | Use |
|----------|--------|-----|
| `/v1/variant/{id}` | GET | Single canonical-ID lookup |
| `/v1/variant` | POST (batched IDs) | Batch lookup, up to 1000 IDs |
| `/v1/query?q={lucene}` | GET | Flexible Elasticsearch search |
| `/v1/metadata` | GET | Per-source versions |

**Scopes** (the `scopes` parameter on `/v1/query` POST) specifies which fields to match an input ID against: `hgvs`, `rsid`, `dbsnp.rsid`, `dbnsfp.genename`, `chrom`, `_id`. The `_id` is canonical HGVS-g.

## Reproducibility: The `_meta` Field

Every record carries `_meta.src` showing per-source version:

```python
mv = myvariant.MyVariantInfo()
record = mv.getvariant('chr7:g.140453136A>T', fields=['_meta', 'clinvar', 'dbnsfp.alphamissense'])
print(record['_meta']['src']['dbnsfp']['version'])  # e.g., '4.7a'
print(record['_meta']['src']['clinvar']['version'])  # e.g., '20250901'
```

For reproducibility, record per-source versions in analysis output alongside results.

## Comparison to Alternatives

| Tool | Approach | When to use |
|------|----------|-------------|
| **myvariant.info** | Cloud aggregator, ES-backed | Quick batch annotation, no local setup |
| **OpenCRAVAT** (Pagel 2020 *JCO Clin Cancer Inform*) | Local install, modular annotators | Offline / PHI-sensitive |
| **VarSome** (Kopanos 2019 *Bioinformatics* 35:1978; commercial) | Hosted, 22 sources | 82% ACMG criteria auto-application (highest); clinical labs |
| **Franklin / Genoox** | Commercial hosted | 59 data sources; family/cohort analysis |
| **GeneBe.net** (Stawiński 2024 *Clin Genet*) | Open-source web + API | Free Tavtigian-point-system-based ACMG; comparable to VarSome |
| **ANNOVAR / VEP / snpEff** | Local annotation tools | Pipeline integration, batch annotation, no ACMG |

**myvariant.info does NOT produce ACMG calls**; it is purely an annotation aggregator. Pair with InterVar, GeneBe, or the `acmg-classification` skill for classification.

## Decision Tree by Query Scenario

| Scenario | Recommended path | Why |
|----------|------------------|-----|
| Single variant batch annotation | `getvariant(hgvs, fields=...)` | One call, all aggregated sources |
| 10-1000 variants | `getvariants(list, fields=...)` | Batch endpoint, up to 1000 |
| > 1000 variants | Chunk to 1000 + sleep | Rate limit + JSON size |
| Search by gene + pathogenicity | `mv.query('clinvar.gene.symbol:BRCA1 AND clinvar.clinical_significance:Pathogenic', size=200)` | Elasticsearch Lucene |
| ACMG-grade pipeline | myvariant for annotation -> InterVar / GeneBe for classification | myvariant does not produce ACMG calls |
| Offline / PHI-sensitive | OpenCRAVAT or VEP locally | myvariant requires HTTP |
| Reproducibility | Always record `_meta.src.<source>.version` | dbNSFP version is the dominant staleness vector |
| Source-specific deep dive | Use the source-specific skill (clinvar-lookup, gnomad-frequencies) | myvariant is aggregator-grade, not source-deep |

## Standard Annotation Workflow

**Goal:** Annotate a list of variants with the canonical clinical fields for downstream prioritization.

**Approach:** Batch `getvariants` with explicit field list; record `_meta` versions; convert to DataFrame.

```python
import myvariant
import pandas as pd

mv = myvariant.MyVariantInfo()

CLINICAL_FIELDS = [
    'clinvar.clinical_significance',
    'clinvar.review_status',
    'clinvar.variant_id',
    'gnomad_exome.faf95',
    'gnomad_exome.af.af',
    'gnomad_exome.an.an',
    'gnomad_genome.faf95',
    'gnomad_genome.af.af',
    'dbsnp.rsid',
    'dbnsfp.alphamissense.score',
    'dbnsfp.alphamissense.pred',
    'dbnsfp.revel.score',
    'dbnsfp.cadd.phred',
    'dbnsfp.spliceai.master_pred',
    'dbnsfp.spliceai.ds_max',
    'cosmic.cosmic_id',
    'civic.openCravatUrl',
    '_meta'
]

def annotate_variant_list(hgvs_list):
    '''Batch-annotate variants with ClinVar / gnomAD / dbNSFP / COSMIC / CIViC fields.'''
    chunked = [hgvs_list[i:i+1000] for i in range(0, len(hgvs_list), 1000)]
    rows = []
    versions = None
    for chunk in chunked:
        results = mv.getvariants(chunk, fields=CLINICAL_FIELDS)
        for r in results:
            if versions is None and r.get('_meta'):
                versions = {src: meta.get('version') for src, meta in r['_meta'].get('src', {}).items()}
            clinvar = r.get('clinvar', {}) or {}
            gnomad_e = r.get('gnomad_exome', {}) or {}
            gnomad_g = r.get('gnomad_genome', {}) or {}
            dbnsfp = r.get('dbnsfp', {}) or {}
            faf95 = (gnomad_e.get('faf95', {}) or gnomad_g.get('faf95', {})) or {}
            rows.append({
                'variant': r.get('query'),
                'clinvar_sig': clinvar.get('clinical_significance'),
                'clinvar_review': clinvar.get('review_status'),
                'gnomad_grpmax_faf95': faf95.get('popmax'),
                'grpmax_ancestry': faf95.get('popmax_population'),
                'gnomad_af': gnomad_e.get('af', {}).get('af') or gnomad_g.get('af', {}).get('af'),
                'rsid': r.get('dbsnp', {}).get('rsid'),
                'alphamissense': dbnsfp.get('alphamissense', {}).get('score'),
                'revel': dbnsfp.get('revel', {}).get('score'),
                'cadd_phred': dbnsfp.get('cadd', {}).get('phred'),
                'spliceai_ds_max': dbnsfp.get('spliceai', {}).get('ds_max')
            })
    return pd.DataFrame(rows), versions
```

## Elasticsearch Query Patterns

**Goal:** Search beyond canonical IDs; e.g., all pathogenic variants in a gene, all variants in a genomic region with CADD > 20.

**Approach:** Lucene syntax in `mv.query()`; support boolean operators, ranges, wildcards.

```python
def find_pathogenic_in_gene(gene_symbol, max_results=500):
    '''Find ClinVar P/LP variants in a gene.'''
    query = f'clinvar.gene.symbol:{gene_symbol} AND '\
            'clinvar.clinical_significance:(Pathogenic OR "Likely pathogenic")'
    hits = mv.query(query, size=max_results, fields=['_id', 'clinvar.clinical_significance',
                                                       'clinvar.review_status'])
    return hits.get('hits', [])


def find_high_cadd_in_region(chrom, start, end, min_cadd=25):
    '''Find variants in region with CADD phred above threshold.'''
    query = f'chrom:{chrom} AND hg19.start:[{start} TO {end}] AND '\
            f'dbnsfp.cadd.phred:>{min_cadd}'
    return mv.query(query, size=500, fields=['_id', 'dbnsfp.cadd.phred', 'clinvar.clinical_significance'])


def find_alphamissense_pathogenic(gene, min_score=0.564):
    '''Find AlphaMissense pathogenic missense in a gene.

    Note: Cheng 2023 dev cutoff is 0.564 BUT this is NOT the Pejaver-style calibrated
    PP3 threshold. ClinGen has not endorsed AlphaMissense thresholds as of May 2026;
    use AlphaMissense as supporting evidence only.
    '''
    query = f'dbnsfp.genename:{gene} AND dbnsfp.alphamissense.score:>{min_score}'
    return mv.query(query, size=500, fields=['_id', 'dbnsfp.alphamissense', 'clinvar.clinical_significance'])
```

## Per-Operation Failure Modes

**1. Stale dbNSFP version**
- Trigger: Query `dbnsfp.alphamissense.score` and trust as current.
- Mechanism: dbNSFP version lags new tools by 6-18 months; AlphaMissense (Cheng 2023) was integrated into dbNSFP 4.4 (~2024).
- Symptom: Predictions appear missing for variants newly scored by AlphaMissense.
- Fix: Check `_meta.src.dbnsfp.version`; for cutting-edge predictions query AlphaMissense API directly.

**2. Treating AlphaMissense dev threshold as PP3-calibrated**
- Trigger: Apply AlphaMissense score >0.564 as PP3 evidence.
- Mechanism: Cheng 2023 developer-recommended threshold is NOT the Pejaver 2022 calibration framework; ClinGen has not endorsed strength-graded thresholds for AlphaMissense as of May 2026.
- Symptom: Over-application of PP3 in ACMG classification.
- Fix: Treat AlphaMissense as supporting evidence; defer to `clinical-databases/acmg-classification` for calibrated thresholds.

**3. Stacking REVEL + BayesDel + AlphaMissense as independent evidence**
- Trigger: Use multiple in silico predictors as additive PP3 evidence.
- Mechanism: REVEL, BayesDel, VEST4 share ClinVar/HGMD training labels; AlphaMissense is partially independent but correlates strongly with conservation.
- Symptom: Inflated PP3 strength; double-counting.
- Fix: Apply ONE predictor per variant (Pejaver 2022 explicit recommendation).

**4. Rate-limit ignorance**
- Trigger: Loop sequentially over 10k variants with `getvariant()`.
- Mechanism: ~1000 req/sec aggregate per source IP; loops trigger throttling or 429s.
- Symptom: Increasing latency, eventual failures.
- Fix: Use `getvariants(chunk, fields=...)` with chunk size 1000; sleep ~0.5s between chunks.

**5. Field-path errors silently return None**
- Trigger: Query `gnomad_exome.faf95.popmax` but typo as `gnomad_exome.faf` or `gnomad.exomes.faf95`.
- Mechanism: Elasticsearch returns null for non-existent paths; no error raised.
- Symptom: All values None; no error.
- Fix: Use `print(mv.getvariant(test_id))` first to inspect actual field structure; check `/v1/metadata/fields`.

**6. Multi-allelic rsID returns one variant only**
- Trigger: Query `rs12345` and treat returned variant as the variant of interest.
- Mechanism: rsID is a cluster identifier; multi-allelic clusters return multiple records.
- Symptom: Wrong allele returned for ~6-8% of rsIDs.
- Fix: Use HGVS-g instead of rsID for unambiguous lookups; for rsID queries, inspect all returned variants and filter by allele.

**7. Sample overlap between sources**
- Trigger: Treat ClinVar + gnomAD as independent corroboration.
- Mechanism: ClinVar variants often *derive from* gnomAD-included individuals; not statistically independent.
- Symptom: False sense of independent evidence in ACMG application.
- Fix: ClinVar P + gnomAD rare is operationally additive evidence per ACMG but understand the populations may overlap.

## Reconciliation: When Sources Inside myvariant Disagree

| Pattern | Likely cause | Action |
|---------|-------------|--------|
| dbNSFP REVEL != ClinVar PP3 strength | Different curation cohort | Use Pejaver 2022 calibrated thresholds (see `acmg-classification`) |
| ClinVar P + AlphaMissense benign | NMD-escape region, alternative isoform, ClinVar P stale | Cross-check with conservation, splicing predictions |
| gnomAD AF differs across exome vs genome | Sample sizes differ; exome has 730k, genome 76k | Use exome FAF95 when available; genome as fallback |
| COSMIC + ClinVar overlap | True dual-classification (germline + somatic) | Report both contexts |
| Variant missing from one source | Source-specific coverage gaps | Cross-check directly with primary source skill (clinvar-lookup, gnomad-frequencies) |

## Quantitative Thresholds and Conventions

| Threshold | Convention | Source |
|-----------|-----------|--------|
| Batch endpoint cap | 1000 IDs per POST | myvariant.info docs |
| Rate limit | ~1000 req/sec aggregate; lower per IP | myvariant.info docs |
| dbNSFP refresh lag | 6-18 months from primary source release | dbNSFP release history |
| `_meta.src` field | Per-source version is always available | BioThings SDK convention |
| Lucene escape | Special chars need `\` (e.g., `chr7\:140453136`) | Elasticsearch convention |
| Multi-allelic rsID | ~6-8% of dbSNP rsIDs are multi-allelic | operational estimate |
| AlphaMissense PP3 calibration | NOT yet ClinGen-endorsed (as of May 2026) | ClinGen SVI |
| REVEL PP3_Strong calibration | >= 0.932 per Pejaver 2022 | Pejaver 2022 *AJHG* |

## Common Errors

| Symptom | Cause | Solution |
|---------|-------|----------|
| `KeyError: 'gnomad_exome'` | Variant absent from gnomAD exome dataset | Use `.get('gnomad_exome', {})` defensively |
| `None` for AlphaMissense on rare variants | dbNSFP coverage gap; variant in alt-spliced isoform | Query AlphaMissense API directly, or accept None |
| Search returns 0 hits despite known matches | Lucene escape on `:` in chr coords | Quote the chrom-position term or escape `:` |
| Batch returns < input IDs | Some IDs not in any source | Check `notfound` field in response |
| Different AF in myvariant vs gnomAD browser | dbNSFP version != current gnomAD release | Check `_meta.src.gnomad_exome.version` |
| 503 on bulk query | Rate limit | Reduce chunk to 500; sleep 1s between |
| `_id` doesn't match input | myvariant uses canonical HGVS-g; input was rsID or non-canonical | Re-query by `_id` after first resolution |

## Anticipated Reviewer Pushback

| Pushback | Standard response |
|----------|-------------------|
| "myvariant.info is just an aggregator; why not query sources directly?" | Aggregator avoids per-source API setup; sufficient for single-source unique queries we defer to source-specific skills. |
| "This annotation differs from VarSome" | VarSome uses its own ACMG implementation; myvariant.info does NOT produce ACMG calls; we pair with `acmg-classification`. |
| "dbNSFP REVEL differs from REVEL website" | dbNSFP version is on the order of 1 year behind primary; check `_meta.src.dbnsfp.version`. |
| "AlphaMissense calibration thresholds were missed" | AlphaMissense is integrated via dbNSFP; PP3 calibration is in `clinical-databases/acmg-classification` skill. |
| "Why not OpenCRAVAT?" | OpenCRAVAT requires local install; myvariant is faster for batch annotation. Switch to OpenCRAVAT for PHI-sensitive or offline workflows. |

## References

- Lelong S et al. 2022. BioThings SDK: a toolkit for building high-performance data APIs in biomedical research. *Bioinformatics* 38:2077.
- Xin J et al. 2016. High-performance web services for querying gene and variant annotation. *Genome Biol* 17:91.
- Cheng J et al. 2023. Accurate proteome-wide missense variant effect prediction with AlphaMissense. *Science* 381:eadg7492.
- Pejaver V et al. 2022. Calibration of computational tools for missense variant pathogenicity classification. *Am J Hum Genet* 109:2163.
- Pagel KA et al. 2020. Integrated informatics analysis of cancer-related variants. *JCO Clin Cancer Inform* 4:310. (OpenCRAVAT)
- Kopanos C et al. 2019. VarSome: the human genomic variant search engine. *Bioinformatics* 35:1978.
- Stawiński P, Płoski R. 2024. Genebe.net: implementation and validation of an automatic ACMG variant pathogenicity criteria assignment. *Clin Genet* 106:119.
- myvariant.info docs: `https://docs.myvariant.info/en/latest/`
- BioThings field metadata: `https://myvariant.info/v1/metadata/fields`

## Related Skills

- clinical-databases/clinvar-lookup - Source-level deep ClinVar queries
- clinical-databases/gnomad-frequencies - Source-level deep gnomAD queries
- clinical-databases/dbsnp-queries - Source-level rsID resolution
- clinical-databases/acmg-classification - ACMG framework with Pejaver calibration
- clinical-databases/variant-prioritization - Pipeline using aggregated annotations
<!-- END FILE: clinical-databases/myvariant-queries/SKILL.md -->

## 子目录：clinical-databases/pharmacogenomics

<!-- BEGIN FILE: clinical-databases/pharmacogenomics/SKILL.md -->
---
name: bio-clinical-databases-pharmacogenomics
description: Queries PharmGKB / CPIC / DPWG for drug-gene interactions; calls CYP2D6/CYP2C9/CYP2C19/DPYD/TPMT/NUDT15/UGT1A1/SLCO1B1 star alleles and phenotype with PharmCAT, Cyrius (CYP2D6 structural variants), Aldy, Stargazer; applies Caudle 2020 activity-score translation. Use when implementing pharmacogenomic-guided prescribing, applying CPIC vs DPWG guidance, screening HLA risk alleles for ICI / antiepileptics / abacavir, or interpreting compound TPMT+NUDT15 thiopurine risk.
tool_type: mixed
primary_tool: PharmCAT
---

## Version Compatibility

Reference examples tested with: PharmCAT 2.13+, Cyrius 1.1+ (Chen 2021), Aldy 4.0+, Stargazer 2.0+, StarPhase 1.0+ (PacBio HiFi), HIBAG 1.40+, requests 2.31+, pandas 2.2+. CPIC guideline versions are gene-specific; PharmVar releases are quarterly. DPYD dosing uses the CPIC gene activity-score system (Amstutz 2018 *Clin Pharmacol Ther* 103:210, the 2017-update guideline); the 2025 TPMT/NUDT15 update (Maillard 2026) refines compound-IM dosing.

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed package and adapt the example to match the actual API rather than retrying. PharmVar is the authoritative star-allele source (`https://www.pharmvar.org`); the older Human CYP Allele Nomenclature Database was deprecated in 2017.

# Pharmacogenomics; Star Alleles, Activity Scores, and CPIC/DPWG Guidance

**'What is my patient's CYP2D6 metabolizer status and should I adjust their tamoxifen dose?'** -> Call star alleles (haplotype-level), translate diplotype -> activity score -> phenotype, apply CPIC + DPWG dosing.

- CLI (recommended): `pharmcat -vcf input.vcf.gz -o pharmcat_out`; CPIC-recommended, single-tool reporting
- CLI (CYP2D6 SV-aware): `cyrius -m sample.bam -o cyrius_out`; mandatory addition for CYP2D6
- CLI (multi-gene CN-aware): `aldy genotype -p illumina sample.bam`; alternative
- CLI (long-read 8-field): PacBio HiFi `starphase`; transplant-grade including HLA
- R (SNP-array): HIBAG for HLA-B*57:01/B*15:02/B*58:01/A*31:01 imputation
- API: `requests.get('https://api.pharmgkb.org/v1/data/clinicalAnnotation', ...)`

## Governance: CPIC vs DPWG vs PharmGKB vs FDA

These four authorities are routinely conflated. They differ in scope, scale, and recommendations:

| Authority | Scope | Output | Anchors |
|-----------|-------|--------|---------|
| **CPIC** (US Clinical Pharmacogenetics Implementation Consortium) | Once a result is available, what to prescribe | Level A/B/C/D gene-drug pair + strength of recommendation per phenotype + evidence quality | ~26 guidelines, ~25 genes, 100+ drugs as of 2026 |
| **DPWG** (Dutch Pharmacogenetics Working Group) | Whether to test AND what to prescribe | 5-pt (0-4) evidence + 7-pt (AA-F) clinical-relevance scale | G-Standaard (Dutch EHR-integrated); RCT-validated via PREPARE |
| **PharmGKB clinical annotation levels** | Evidence cataloguing | 1A/1B/2A/2B/3/4 | 1A = guideline OR medical-society OR PGRN/eMERGE implementation; NOT pure evidence |
| **FDA Table of Pharmacogenomic Biomarkers** | Drug label info | ~300 drugs (informational) | NOT an actionability list; many entries are dosing-suggestion-only |
| **FDA Table of Pharmacogenetic Associations** | Actionable subset | Closer to CPIC | Compare head-to-head with CPIC |

**Bank et al 2018** *Clin Pharmacol Ther* 103:599 (DOI 10.1002/cpt.762) is the canonical CPIC-vs-DPWG comparison. Notable disagreements:
- CYP2D6 IM + multiple antidepressants: DPWG actionable; CPIC says insufficient evidence.
- HLA-B*15:11 carbamazepine: DPWG actionable; CPIC silent.
- CYP2C19 IM + voriconazole: dosing magnitudes differ 25-50%.

**Common PGx-evidence critiques:** (1) EUR over-representation in discovery cohorts; (2) most PGx RCTs are open-label / prescriber-unblinded; (3) publication bias in antiseizure PGx may overstate effects ~2x; (4) subjective composite endpoints.

## PharmGKB Clinical Annotation Levels: What 1A Actually Means

| Level | Requirement |
|-------|-------------|
| **1A** | Variant-drug pair appears in CPIC guideline OR medical-society guideline OR is implemented at a PGRN/eMERGE site |
| **1B** | Replication in multiple cohorts; preponderance of evidence; no formal guideline yet |
| **2A** | Replicated association in a VIP (Very Important Pharmacogene) |
| **2B** | Replicated association in non-VIP gene |
| **3** | Single significant association OR mixed-evidence variant-drug pair |
| **4** | In vitro / case report / molecular evidence only |

1A does NOT require RCT evidence; mechanism + guideline status suffices.

## Star Allele Nomenclature (PharmVar)

PharmVar (`https://www.pharmvar.org`) is authoritative for: CYP1A1, CYP1A2, CYP1B1, CYP2A6, CYP2A13, CYP2B6, CYP2C8, CYP2C9, CYP2C19, CYP2D6, CYP2E1, CYP2F1, CYP2J2, CYP2R1, CYP2S1, CYP2W1, CYP3A4, CYP3A5, CYP3A7, CYP3A43, CYP4A11, CYP4F2, CYP19A1, CYP26A1, DPYD, NUDT15, SLCO1B1, TPMT.

**A star allele is a haplotype, not a single variant.** *Suballeles* (*1.001, *1.002, etc.) encode the exact SNV+indel pattern within a defined functional haplotype.

**The *1 reference is the PharmVar consensus reference, NOT biological wild type.** Defined as the absence of all known functional variants at the locus.

### CYP2D6 Activity Scores (Caudle 2020 *Clin Transl Sci*; DOI 10.1111/cts.12692)

| Phenotype | Activity score (AS) range |
|-----------|--------------------------|
| **PM (Poor Metabolizer)** | 0 |
| **IM (Intermediate Metabolizer)** | 0 < AS < 1.25 |
| **NM (Normal Metabolizer)** | 1.25 <= AS <= 2.25 |
| **UM (Ultra-rapid)** | AS > 2.25 |

Key per-allele activity values (selected):

| Allele | Activity | Notes |
|--------|----------|-------|
| \*1, \*2, \*35 | 1.0 | Normal |
| \*3, \*4, \*5 (gene deletion), \*6, \*7, \*8, \*11, \*12, \*15, \*19, \*20, \*36, \*40, \*42 | 0 | No function |
| \*9, \*41, \*17, \*29 | 0.5 | Decreased function (substrate-specific caveats for \*17) |
| **\*10** | **0.25** | **Caudle 2020 RESET from 0.5 to 0.25**; reclassified large fractions of East-Asian populations to IM |
| \*68 | 0 | Hybrid; non-functional |

**\*4xN is clinically silent:** a no-function allele multiplied by N is still no-function. Reporting *4xN as UM is the most-common reportable error in clinical PGx.

### CYP2D6 Structural Complexity

CYP2D6 on 22q13.2 sits adjacent to the highly-similar CYP2D7 pseudogene. Four classes of structural variant that no SNV-only caller can resolve:

1. **Gene deletion (\*5):** ~13 kb deletion; activity 0; diagnostic *REP6/REP7* breakpoint.
2. **Gene duplication/multiplication (\*1xN, \*2xN, \*4xN, \*10xN, \*17xN, \*35xN, \*36xN):** Tandem copies; clinical impact depends on which allele is amplified; **\*4xN is clinically silent**.
3. **CYP2D7 -> CYP2D6 hybrids (\*13):** Pseudogene fused 5'; non-functional.
4. **CYP2D6 -> CYP2D7 hybrids (\*36, \*61, \*63, \*68, \*83):** 5' CYP2D6 with 3' pseudogene exon 9 conversion; typically embedded in duplications upstream of *10 (East Asian) or upstream of *4 (European).

**GATK / DeepVariant alone cannot call any of these.** They operate on multi-mapper-filtered BAMs; 97%+ identity between CYP2D6 and CYP2D7 produces silent miscalls of every \*5, \*13, \*36, \*68, \*4xN sample.

## Algorithmic Taxonomy: Star Allele Callers

| Tool | CYP2D6 SV | CYP2D6 CN | Other PGx genes | Phased | Validation | Fails when |
|------|-----------|-----------|-----------------|--------|------------|-----------|
| **PharmCAT** (Sangkuhl 2020 *Clin Pharmacol Ther*) | No (consumes outside SV calls) | No | 21 CPIC genes; full clinical reporting | Phased or unphased VCF | High; CPIC reference | CYP2D6 SV-rich samples need Cyrius/StellarPGx upstream |
| **Cyrius** (Chen 2021 *Pharmacogenomics J*) | **Yes (99.3% concordance)** | **Yes** | CYP2D6 only | Phased haplotypes | GeT-RM 99.3% | Other genes (single-purpose tool) |
| **BCyrius** (PubMed 39901590, 2025) | Yes (extended) | Yes | CYP2D6 only | Phased | Extended SV diversity | Other genes |
| **Aldy v4** (Numanagic 2018 *Nat Commun*) | Yes | Yes | CYP2D6, CYP2A6, CYP2B6, etc. | Phased | GeT-RM 82-87% (CYP2D6) | Less accurate than Cyrius for CYP2D6 |
| **Stargazer** (Lee 2019 *Genet Med*) | Limited | Yes | ~50 PGx genes | Statistical phasing | ~84% (CYP2D6) | Fails on rare alleles; statistical phasing is unstable |
| **StellarPGx** | Yes (~99%) | Yes | CYP2D6 + others | Phased | GeT-RM ~99% | Less widely deployed than Cyrius |
| **Astrolabe** (proprietary, formerly Constellation) | Yes | Yes | Multi-gene | Proprietary | Industry-validated | License required |
| **StarPhase** (PacBio HiFi 2024+) | Yes | Yes | All CPIC Level A genes + HLA | Native phasing | Long-read gold standard | Requires PacBio HiFi |

**Canonical clinical workflow 2024-2026:** PharmCAT for the panel + Cyrius (or StellarPGx) for CYP2D6 SVs + dedicated HLA typer (T1K, OptiType, HLA-LA) for HLA.

Twesigomwe 2020 *npj Genom Med*: inter-tool discordance 10-18% on CYP2D6; nearly all in samples carrying SVs.

## HLA-Drug Associations: Mechanistically Distinct from CYP

HLA associations are **idiosyncratic immune reactions**, not dose-response phenomena. Effect sizes (OR 50-1000+) far exceed any CYP polymorphism. Testing rationale is **screen-and-avoid**, not dose-adjust.

| Allele | Drug | Reaction | Population | Landmark |
|--------|------|----------|------------|----------|
| **HLA-B\*57:01** | Abacavir | HSS | All ancestries (5-8% NFE) | Mallal 2008 *NEJM* (PREDICT-1) |
| **HLA-B\*15:02** | Carbamazepine, oxcarbazepine, phenytoin, lamotrigine (weaker) | SJS/TEN | Han Chinese, Thai, Malay, Indian (>=5%) | Chung 2004 *Nature*; FDA black-box 2007 |
| **HLA-A\*31:01** | Carbamazepine | DRESS, MPE, SJS/TEN | Europeans (2-5%), Japanese | McCormack 2011 *NEJM* |
| **HLA-B\*58:01** | Allopurinol | SJS/TEN, DRESS | Han Chinese (10-15%), Thai, Korean | Hung 2005 *PNAS* (OR ~580) |
| **HLA-B\*13:01** | Dapsone | DDS | Han Chinese, SE Asian | Zhang 2013 *NEJM* |
| **HLA-B\*35:02** (NOT \*35:01) | Minocycline | DILI | All | Urban 2017 *J Hepatol* |
| **HLA-B\*35:01** | TMP-SMX | DILI, DRESS-like | African American | Li 2021 *Hepatology* |
| **HLA-B\*14:01** | TMP-SMX | DILI | European American (OR 9.20) | Li 2021 |
| **HLA-A\*33:01/03** | Terbinafine | DILI | Multi-ancestry | Nicoletti 2017 |
| **HLA-DRB1\*15:01-DQB1\*06:02 haplotype** | Amoxicillin-clavulanate | DILI | Europeans | Stephens 2013 |
| **HLA-B\*15:13** | Phenytoin | SJS | Malaysian | Chang 2017 |

**Critical:** HLA screening requires 4-field resolution. \*57:01 (abacavir risk) vs \*57:03 (no risk); \*35:02 (minocycline DILI) vs \*35:01 (TMP-SMX DILI). See `clinical-databases/hla-typing` for typing.

## Non-CYP Pharmacogenes: Variant-Level Detail

### DPYD (5-FU / Capecitabine / Tegafur); Activity Score Framework

The CPIC DPYD guideline (Amstutz 2018 *Clin Pharmacol Ther* 103:210) uses a **gene activity score** system. Activity values: normal-function = 1.0, decreased = 0.5, no function = 0.

| Variant | rsID | Allele | Activity |
|---------|------|--------|----------|
| c.1905+1G>A | rs3918290 | DPYD*2A | 0 (splice disruption) |
| c.1679T>G | rs55886062 | DPYD*13 (p.I560S) | 0 |
| c.2846A>T | rs67376798 | (p.D949V) | 0.5 |
| c.1129-5923C>G / c.1236G>A (HapB3) | rs56038477 / rs75017182 | HapB3 | 0.5 |

Gene AS = sum of two lowest activities. Recommended dose: AS 2 = full dose; AS 1.5 = 50% start + TDM; AS 1.0 = 50% start + TDM; AS 0 = avoid.

c.85T>C (DPYD\*9A) is NOT in the CPIC actionable set despite frequent commercial reporting; evidence does not support clinical decrement.

EU universal pre-treatment testing standard since Henricks 2018 *Lancet Oncol* (genotype-guided dosing lowered severe fluoropyrimidine toxicity in DPYD variant carriers, e.g. DPYD*2A grade >=3 toxicity RR 2.87 -> 1.31) and EMA 2020 endorsement. US lags; ASCO/NCCN moved 2022-2024.

### TPMT + NUDT15 (Thiopurines); 2025 Update

Maillard 2026 *Clin Pharmacol Ther* update emphasizes greater dose reduction for **compound TPMT/NUDT15 IM**.

| Gene | Variant | Activity | Population |
|------|---------|----------|-----------|
| TPMT *2 | c.238G>C | 0 | -- |
| TPMT *3A | c.460G>A + c.719A>G | 0 | EUR-common |
| TPMT *3B | c.460G>A | 0 | -- |
| TPMT *3C | c.719A>G | 0 | AFR / EAS dominant |
| NUDT15 *3 | c.415C>T (rs116855232) | 0 | ~9.8% East Asian; <1% EUR |

NUDT15 *3 is the **dominant thiopurine determinant in East Asians**; TPMT-alone testing misses these patients (Yang 2015 *J Clin Oncol*).

### UGT1A1 (Irinotecan, Atazanavir)

- \*28 (TA7 promoter repeat vs \*1 = TA6, \*37 = TA8); EUR-common
- \*6 (c.211G>A, p.G71R); East Asian dominant
- Severe neutropenia in \*28/\*28 at irinotecan >=180 mg/m^2

### CYP2C19 + Clopidogrel; The Most-Litigated Pair

- **Pare 2010** *NEJM*: no benefit of clopidogrel in \*2 carriers in CURE/ACTIVE-A.
- **TAILOR-PCI** (Pereira 2020 *JAMA*): 5,302 patients post-PCI; primary endpoint MACE @12mo HR 0.66, **p=0.06 (negative by pre-specified alpha)** but positive in sensitivity analyses.
- **Pereira NL et al 2021 meta-analysis** (7 RCTs, 15,949 patients): ~30% MACE reduction in CYP2C19 LOF carriers (*JACC Cardiovasc Interv* 14:739).
- **Consensus 2024 (ACC/AHA/ESC):** genotype-guided therapy reasonable; strongest in post-PCI ACS.

### Warfarin (CYP2C9 + VKORC1 + CYP4F2)

- **EU-PACT 2013** *NEJM*: PGx dosing positive (European).
- **COAG 2013** *NEJM*: PGx dosing negative; worse in African Americans because algorithm omitted CYP2C9 \*5, \*6, \*8, \*11 alleles common in African ancestry. **Paradigmatic ancestry-algorithm failure** (Daneshjou 2014 *Blood*).
- IWPC algorithm explains 47-55% of dose variance.

### SLCO1B1 + Simvastatin

- rs4149056 (c.521T>C, p.V174A); OR 4.5 per C allele for myopathy on 80 mg simvastatin (SEARCH 2008 *NEJM*).
- 2022 CPIC update broadened to all statins with SLCO1B1 substrate behavior.

### Other Actionable

- **CYP2B6 *6** (c.516G>T + c.785A>G): efavirenz dose 600 -> 400 mg in *6/*6 (ENCORE1).
- **CYP3A5 *3** (rs776746): non-expressers (\*3, \*6, \*7) are the *common* state in non-AFR; expressers need 1.5-2x higher tacrolimus dose.
- **G6PD** (CPIC 2022 Gammal 2023): X-linked; female heterozygotes have mosaic activity that single-timepoint assay misclassifies.

## Decision Tree by Scenario

| Scenario | Recommended path | Why |
|----------|------------------|-----|
| Multi-gene PGx panel from VCF | PharmCAT | CPIC-recommended; 21 genes + full clinical reporting |
| CYP2D6 with structural variants | Cyrius (or StellarPGx) | Only tools with reliable SV calling from short-read |
| All CPIC Level A + HLA from one sample | PacBio HiFi + StarPhase | Long-read single-pass typing |
| Pre-emptive panel for cohort | PREPARE-style 12-gene panel | Swen 2023 RCT-validated |
| HLA-B\*57:01 abacavir screen | T1K or OptiType (4-field); HIBAG if SNP-array | Need 4-field specificity |
| African-ancestry warfarin | IWPC algorithm + CYP2C9 *5/*6/*8/*11 explicit | COAG failure paradigm |
| East Asian thiopurine | NUDT15 + TPMT | NUDT15 *3 is dominant in EAS |
| Compound IM (TPMT + NUDT15) | Apply 2025 update | More aggressive dose reduction than single-gene IM |
| Activity score interpretation | Caudle 2020 thresholds for CYP2D6; gene-specific for others | Per CPIC |

## PharmCAT Workflow (Recommended Multi-Gene Pipeline)

**Goal:** Generate CPIC-compliant pharmacogenomic report from a phased or unphased VCF covering 21 PGx genes.

**Approach:** Run PharmCAT on the VCF; supplement CYP2D6 with Cyrius output if SVs suspected; cross-reference HLA from separate typing.

```bash
# PharmCAT (CPIC-recommended; covers 21 genes including CYP2C19, CYP2C9, CYP2D6,
# DPYD, TPMT, NUDT15, UGT1A1, SLCO1B1, CYP3A5, CYP4F2, VKORC1, IFNL3/IFNL4, etc.)

# 1. Preprocess VCF (ensures correct ref allele alignment + chr formatting)
pharmcat_vcf_preprocessor.py \
    -vcf input.vcf.gz \
    -refFna GRCh38.fa \
    -o pharmcat_input/

# 2. Run PharmCAT
java -jar pharmcat.jar \
    -vcf pharmcat_input/input.preprocessed.vcf.bgz \
    -o pharmcat_output/

# Output: <sample>.report.html with phenotype, activity score, dosing recommendations
```

For CYP2D6 SV-rich samples, run Cyrius separately and pass outside calls to PharmCAT:

```bash
# Cyrius for CYP2D6 (99.3% concordance vs Aldy 82-87%, Stargazer 84%)
cyrius -m sample.bam -o cyrius_out --threads 8
# Output: cyrius_out/sample.tsv with diplotype + activity score

# Pass outside calls to PharmCAT
java -jar pharmcat.jar \
    -vcf pharmcat_input/input.preprocessed.vcf.bgz \
    -po cyrius_out/cyrius_for_pharmcat.tsv \
    -o pharmcat_output_with_cyrius/
```

## CYP2D6 Activity Score Calculation

**Goal:** Convert CYP2D6 diplotype to activity score and phenotype with Caudle 2020 conventions.

**Approach:** Look up per-allele activity values; handle copy-number duplications; apply Caudle 2020 phenotype bins.

```python
# Caudle 2020 activity values; *10 reset from 0.5 to 0.25 in 2020
CYP2D6_ACTIVITY = {
    '*1': 1.0, '*2': 1.0, '*35': 1.0,
    '*3': 0.0, '*4': 0.0, '*5': 0.0, '*6': 0.0, '*7': 0.0, '*8': 0.0,
    '*11': 0.0, '*12': 0.0, '*15': 0.0, '*19': 0.0, '*20': 0.0,
    '*36': 0.0, '*40': 0.0, '*42': 0.0, '*68': 0.0,
    '*9': 0.5, '*41': 0.5, '*17': 0.5, '*29': 0.5,
    '*10': 0.25,
    '*13': 0.0,
}


def cyp2d6_activity(diplotype):
    '''Convert CYP2D6 diplotype to activity score.

    Accepts e.g. '*1/*4' or '*2xN/*10' or '*4xN/*10'. Copy-number-aware:
    - *4xN is clinically silent (no-function * N = 0)
    - *1xN, *2xN multiply functional activity
    '''
    left, right = diplotype.split('/')
    return _allele_activity(left) + _allele_activity(right)


def _allele_activity(allele_str):
    '''Handle copy-number suffix xN. *4xN remains 0 (the most common mis-classification).'''
    if 'x' in allele_str:
        base, n = allele_str.split('x')
        copies = int(n) if n != 'N' else 2  # 'N' usually >=2; clinical assumes 2 unless quantified
        return CYP2D6_ACTIVITY.get(base, 1.0) * copies
    return CYP2D6_ACTIVITY.get(allele_str, 1.0)


def cyp2d6_phenotype(activity_score):
    '''Caudle 2020 phenotype bins.'''
    if activity_score == 0:
        return 'Poor Metabolizer'
    if activity_score < 1.25:
        return 'Intermediate Metabolizer'
    if activity_score <= 2.25:
        return 'Normal Metabolizer'
    return 'Ultrarapid Metabolizer'


# Example: *4xN/*10; the classic clinical-silence footgun
diplotype = '*4xN/*10'
score = cyp2d6_activity(diplotype)  # 0 (from *4xN) + 0.25 (from *10) = 0.25
print(f'{diplotype}: AS={score}, phenotype={cyp2d6_phenotype(score)}')  # IM, NOT UM
```

## DPYD Activity Score (CPIC)

```python
DPYD_2024_ACTIVITY = {
    'c.1905+1G>A': 0.0,    # *2A; splice donor
    'c.1679T>G': 0.0,      # *13; p.I560S
    'c.2846A>T': 0.5,      # p.D949V
    'HapB3': 0.5,          # c.1129-5923C>G linked with c.1236G>A
}


def dpyd_activity(variants):
    '''Compute DPYD gene activity score from observed variants.

    Sum the two lowest activities across the two alleles. CPIC dosing:
    - AS 2.0: full dose
    - AS 1.5: 50% start + TDM
    - AS 1.0: 50% start + TDM
    - AS 0.0: avoid
    '''
    activities = sorted([DPYD_2024_ACTIVITY.get(v, 1.0) for v in variants])
    return sum(activities[:2])


def dpyd_dosing(activity_score):
    if activity_score >= 1.99:
        return 'Full dose'
    if activity_score >= 1.0:
        return '50% starting dose + therapeutic drug monitoring'
    return 'Avoid fluoropyrimidines'
```

## PharmGKB API for Drug-Gene Pair Lookup

```python
import requests

PHARMGKB = 'https://api.pharmgkb.org/v1'


def clinical_annotation(gene_symbol):
    '''Query PharmGKB clinical annotations by gene.'''
    r = requests.get(f'{PHARMGKB}/data/clinicalAnnotation',
                     params={'view': 'base', 'location.genes.symbol': gene_symbol},
                     timeout=30)
    return r.json().get('data', [])


def cpic_guideline(gene_symbol):
    '''Query CPIC guidelines via PharmGKB.'''
    r = requests.get(f'{PHARMGKB}/data/guideline',
                     params={'view': 'base', 'relatedGenes.symbol': gene_symbol, 'source': 'CPIC'},
                     timeout=30)
    return r.json().get('data', [])
```

## Per-Operation Failure Modes

**1. *4xN -> "Ultrarapid Metabolizer"**
- Trigger: Pipeline reports CYP2D6 \*4xN as UM.
- Mechanism: \*4 has activity 0; \*4 x N = still 0. Only functional alleles (\*1, \*2, \*35) become UM when amplified.
- Symptom: Patient labeled as needing dose reduction when they should be PM/IM.
- Fix: Look up per-allele activity BEFORE multiplying by N; \*4xN = 0; AS depends entirely on the other allele.

**2. Calling CYP2D6 from short-read without SV-aware tool**
- Trigger: Use GATK + PharmCAT only on CYP2D6.
- Mechanism: 97%+ CYP2D6/CYP2D7 identity; SVs (deletion, duplications, hybrids) silently miscalled.
- Symptom: ~10-18% of samples miscalled (Twesigomwe 2020); concentrated in samples with SVs.
- Fix: Add Cyrius (or StellarPGx) for CYP2D6; pass outside calls to PharmCAT.

**3. Pre-2020 \*10 activity value**
- Trigger: Use activity = 0.5 for CYP2D6 \*10.
- Mechanism: Caudle 2020 reset \*10 from 0.5 to 0.25 based on metabolic-ratio evidence.
- Symptom: East-Asian samples mis-classified as NM (when should be IM).
- Fix: Use Caudle 2020 activity table; \*10 = 0.25.

**4. EUR-only DPYD panel**
- Trigger: Pre-treat fluoropyrimidine using CPIC-core 4-variant panel only.
- Mechanism: 4-variant panel captures EUR DPD-deficient carriers but misses additional DPYD variants enriched in non-European populations (Offer 2014 identified ~30 such deleterious variants).
- Symptom: African-ancestry patients suffer severe toxicity despite "negative" PGx.
- Fix: Use extended panel for AFR cohorts; supplement with phenotype testing (uracil/dihydrouracil plasma ratio).

**5. TPMT testing without NUDT15**
- Trigger: Pre-treat thiopurines using TPMT-only PGx in East Asian patient.
- Mechanism: NUDT15 *3 (9.8% EAS, <1% EUR) is the dominant determinant in EAS.
- Symptom: EAS patients TPMT-wildtype suffer severe myelosuppression.
- Fix: Always test NUDT15 alongside TPMT; apply Maillard 2026 compound-IM rules.

**6. HLA-B\*57 -> "abacavir risk" (4-field underspecified)**
- Trigger: Screen reports "B*57 present" as contraindication.
- Mechanism: B*57:01 (HSS risk), B*57:02, B*57:03 (no HSS risk).
- Symptom: False contraindication; patient denied effective therapy.
- Fix: Report 4-field; B*57:01 specifically.

**7. CYP3A5 *3 / non-expresser confusion**
- Trigger: Apply "CYP3A5 normal metabolizer" to *3/*3 in tacrolimus dosing.
- Mechanism: *3/*3 are NON-EXPRESSERS (most common state in non-AFR); expressers (any *1) need 1.5-2x higher dose.
- Symptom: Tacrolimus over-dosing in expressers; under-dosing in non-expressers.
- Fix: Apply CPIC 2015 (Birdwell) tacrolimus dosing; flag expresser status.

**8. Activity-based vs allele-based confusion**
- Trigger: Sum activities across substrate-non-specific assumption for *17.
- Mechanism: CYP2D6 *17 shows substrate-dependent activity (reduced for some substrates, near-normal for others).
- Symptom: Substrate-specific dose recommendations applied generically.
- Fix: Use substrate-specific guidance where available; flag *17 in AFR cohorts.

## Reconciliation: When Tools Disagree

| Pattern | Likely cause | Action |
|---------|-------------|--------|
| Cyrius vs Aldy CYP2D6 disagree | SV-rich sample; Aldy less accurate | Trust Cyrius |
| PharmCAT vs CPIC website disagree on phenotype | PharmCAT version lag or *10 activity value drift | Update PharmCAT to current release |
| CPIC vs DPWG dosing differ | Independent guideline bodies | Cite both; use jurisdiction-appropriate one |
| Patient phenotype doesn't match genotype | Drug-drug interaction; clearance physiology; non-pharmacogenetic factor | Consider phenoconversion; clinical reassessment |
| TPMT-only test vs IM phenotype | Missed NUDT15 in EAS | Re-test with NUDT15 |
| *4xN reported as UM | Tool bug | Use SV-aware tool and Caudle 2020 activity table |
| HLA-B*57 reported without 4-field | Insufficient resolution | Re-type at 4-field minimum |

## Quantitative Thresholds and Conventions

| Threshold | Convention | Source |
|-----------|-----------|--------|
| Cyrius CYP2D6 accuracy | 99.3% on GeT-RM reference samples | Chen 2021 *Pharmacogenomics J* |
| Aldy CYP2D6 accuracy | 82-87% on GeT-RM | Twesigomwe 2020 |
| Stargazer CYP2D6 accuracy | ~84% on GeT-RM | Twesigomwe 2020 |
| Inter-tool CYP2D6 discordance | 10-18% (concentrated in SV samples) | Twesigomwe 2020 |
| PREPARE ADR reduction | OR 0.70 (95% CI 0.54-0.91) for actionable interactions | Swen 2023 *Lancet* |
| PREPARE actionable variant rate | 93.5% of patients had >=1 actionable variant | Swen 2023 |
| TAILOR-PCI primary endpoint | HR 0.66 (95% CI 0.43-1.02), p=0.06 (negative) | Pereira 2020 *JAMA* |
| Pereira 2021 meta-analysis | ~30% MACE reduction in CYP2C19 LOF carriers | Pereira 2021 *JACC Cardiovasc Interv* 14:739 |
| Henricks 2018 DPYD outcome | Per-variant toxicity reduction (DPYD*2A grade >=3 RR 2.87 -> 1.31) | Henricks 2018 *Lancet Oncol* |
| NUDT15 *3 frequency | ~9.8% East Asian vs <1% EUR | Relling 2019 CPIC *Clin Pharmacol Ther* 105:1095 |
| HLA-B*57:01 OR for abacavir HSS | ~100 (case-control) | Mallal 2002 *Lancet* 359:727 |

## Common Errors

| Symptom | Cause | Solution |
|---------|-------|----------|
| CYP2D6 reported as UM in samples with *4xN | Tool not SV-aware OR Caudle 2020 not applied | Use Cyrius; check *4xN handling |
| East-Asian patient labeled CYP2D6 NM | *10 still at activity 0.5 | Update activity table to Caudle 2020 (*10 = 0.25) |
| African patient suffers warfarin bleeding despite "wildtype" CYP2C9 | Panel omits *5/*6/*8/*11 (AFR-common) | Use ancestry-aware panel; supplement with INR-guided dosing |
| Severe thiopurine toxicity in TPMT-wildtype EAS patient | NUDT15 not tested | Always pair TPMT + NUDT15 |
| Patient with CYP2C19 *2/*2 and clopidogrel failure | Expected; no genotype-guided alternative chosen | Switch to prasugrel/ticagrelor per CPIC |
| DPYD AS = 0 but no dose adjustment | Single-variant rule used instead of activity score | Update to the CPIC activity-score framework |
| HLA-B*57:01 false positive | 2-field B*57 result misinterpreted | Re-type at 4-field |

## Anticipated Reviewer Pushback

| Pushback | Standard response |
|----------|-------------------|
| "TAILOR-PCI missed primary endpoint; why genotype clopidogrel?" | Sensitivity analyses positive; Pereira 2021 meta-analysis (7 RCTs) +30% MACE reduction; ESC 2023 endorses; ACC 2022 weaker. |
| "DPYD universal screening is expensive" | Henricks 2018 per-variant toxicity reduction + Knikman 2021 cost-effective; EU standard since 2020; US ASCO/NCCN updated 2022-2024. |
| "CYP2D6 SV calling is unreliable" | Cyrius 99.3% on GeT-RM (Chen 2021); not unreliable; the prior tools were. |
| "*10 = 0.25 disagrees with old paper" | Caudle 2020 *Clin Transl Sci* consensus reset based on substrate-metabolic-ratio evidence. |
| "GeneSight is approved by my hospital" | GUIDED trial (Greden 2019) missed primary endpoint; physician-unblinded; literature shows modest effects inseparable from expectancy bias. |
| "Why pair TPMT + NUDT15?" | NUDT15 *3 is the dominant thiopurine determinant in East Asians (9.8% vs TPMT *3C ~2%); compound IM (TPMT + NUDT15) requires more aggressive dose reduction per Maillard 2026. |
| "HLA imputation from SNP array reliable?" | EUR-trained panel on EUR samples ~95%; cross-ancestry drops to 70-80%; for HSCT use sequencing-based typing. |

## References

- Sangkuhl K et al. 2020. Pharmacogenomics Clinical Annotation Tool (PharmCAT). *Clin Pharmacol Ther* 107:203.
- Chen X et al. 2021. Cyrius: accurate CYP2D6 genotyping using whole-genome sequencing data. *Pharmacogenomics J* 21:251.
- Numanagic I et al. 2018. Allelic decomposition and exact genotyping of highly polymorphic and structurally variant genes. *Nat Commun* 9:828. (Aldy)
- Lee SB et al. 2019. Stargazer: a tool for calling star alleles. *Genet Med* 21:361.
- Twesigomwe D et al. 2020. A systematic comparison of pharmacogene star allele calling bioinformatics algorithms. *npj Genom Med* 5:30.
- Caudle KE et al. 2020. Standardizing CYP2D6 genotype to phenotype translation. *Clin Transl Sci* 13:116. (Activity-score reset for *10)
- Bank PCD et al. 2018. Comparison of the guidelines of the CPIC and the Dutch Pharmacogenetics Working Group. *Clin Pharmacol Ther* 103:599.
- Amstutz U et al. 2018. CPIC guideline for dihydropyrimidine dehydrogenase genotype and fluoropyrimidine dosing: 2017 update. *Clin Pharmacol Ther* 103:210. (DPYD activity score)
- Swen JJ et al. 2023. PREPARE: A pre-emptive pharmacogenetic testing strategy. *Lancet* 401:347.
- Henricks LM et al. 2018. DPYD-guided dose individualization to fluoropyrimidines. *Lancet Oncol* 19:1459.
- Pereira NL et al. 2020. Effect of genotype-guided oral P2Y12 inhibitor selection vs conventional clopidogrel therapy on ischemic outcomes after PCI. *JAMA* 324:761. (TAILOR-PCI)
- Pereira NL et al. 2021. Effect of CYP2C19 genotype on ischemic outcomes during oral P2Y12 inhibitor therapy: a meta-analysis. *JACC Cardiovasc Interv* 14:739.
- Mallal S et al. 2008. HLA-B*5701 screening for hypersensitivity to abacavir. *NEJM* 358:568. (PREDICT-1)
- Chung WH et al. 2004. Medical genetics: a marker for Stevens-Johnson syndrome. *Nature* 428:486.
- McCormack M et al. 2011. HLA-A*3101 and carbamazepine-induced hypersensitivity reactions in Europeans. *NEJM* 364:1134.
- Hung SI et al. 2005. HLA-B*5801 allele as a genetic marker for severe cutaneous adverse reactions caused by allopurinol. *PNAS* 102:4134.
- Yang JJ et al. 2015. Inherited NUDT15 variant is a genetic determinant of mercaptopurine intolerance. *J Clin Oncol* 33:1235.
- Relling MV et al. 2019. CPIC guideline for thiopurine dosing based on TPMT and NUDT15 genotypes: 2018 update. *Clin Pharmacol Ther* 105:1095.
- PharmCAT documentation: `https://pharmcat.org`
- PharmVar: `https://www.pharmvar.org`
- CPIC: `https://cpicpgx.org`
- DPWG: `https://www.knmp.nl/dpwg`

## Related Skills

- clinical-databases/hla-typing - HLA-B*57:01, B*15:02, B*58:01, A*31:01 typing
- clinical-databases/clinvar-lookup - Variant pathogenicity for non-PGx context
- clinical-databases/variant-prioritization - Rare-disease pipeline
- clinical-databases/myvariant-queries - Aggregated PGx variant annotation
- chemoinformatics/admet-prediction - Drug metabolism prediction
<!-- END FILE: clinical-databases/pharmacogenomics/SKILL.md -->

## 子目录：clinical-databases/polygenic-risk

<!-- BEGIN FILE: clinical-databases/polygenic-risk/SKILL.md -->
---
name: bio-clinical-databases-polygenic-risk
description: Constructs and validates polygenic risk scores using LDpred2-auto, SBayesRC, MegaPRS, PRS-CS, PROSPER, MUSSEL, BridgePRS, JointPRS, PRSmix, or PGS Catalog Calculator with ancestry-aware reference panels (HapMap3, UKB-LD), ancestry-conditional calibration, and PRS-RS reporting standards. Use when computing PRS for cohorts, applying absolute-risk transformation, assessing cross-ancestry portability (Martin 2017 / Ding 2023 continuous ancestry), or auditing PRS manuscripts against the 22-item PRS-RS reviewer checklist.
tool_type: mixed
primary_tool: PGS Catalog Calculator
---

## Version Compatibility

Reference examples tested with: bigsnpr 1.12+ (LDpred2; Privé 2020), PRSice-2 2.3.5+, PRS-CS 1.0.0+ (Ge 2019), gctb 2.5+ (SBayesR/SBayesS/SBayesRC; Zheng 2024), LDAK 6.0+ (MegaPRS; Zhang 2021), pgsc_calc 2.0+ (nf-core; Lambert 2024), Hail 0.2.130+, numpy 1.26+, pandas 2.2+. No general FDA PRS guidance document exists as of May 2026; the operative regulatory text is the August 2025 Federal Register notice on Cancer Predisposition Risk Assessment Systems (Class II device with special controls).

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- R: `packageVersion('<pkg>')` then `?function_name`
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed package and adapt the example to match the actual API rather than retrying. The LDpred2-auto `snp_ldpred2_auto()` signature changed in bigsnpr 1.11+; pin `allow_jump_sign = FALSE` and `shrink_corr = 0.95` explicitly.

# Polygenic Risk Scores; Construction, Calibration, Reporting

**'Compute a PRS for my cohort using these GWAS summary statistics'** -> Match variants to target genotypes, choose method by data availability + trait architecture, derive LD-aware effect estimates, score, normalize by ancestry, transform to absolute risk.

- CLI (recommended one-stop): `pgsc_calc --target target.vcf --pgs_id PGS000001` (nf-core, Lambert 2024)
- R (SOTA single-ancestry): `bigsnpr::snp_ldpred2_auto()` (Privé 2020)
- CLI (multi-ancestry SOTA): `PRS-CSx`, `PROSPER`, `MUSSEL`, `BridgePRS`, `JointPRS`
- CLI (SBayesRC with functional annotations): `gctb --sbayes-rc --bfile target --gwas-summary sumstats.ma`
- CLI (legacy baseline): `PRSice_linux` (clumping + thresholding; still cited for some clinical scores)

## Method Landscape: 2026 Operational Ranking

| Method | Approach | Best for | Fails when |
|--------|----------|----------|-----------|
| **SBayesRC** (Zheng 2024 *Nat Genet*) | Bayesian + 96 functional annotations | EUR; sparse traits | Sumstats LD-incoherent with reference; chain divergence (run --impute-summary first) |
| **MegaPRS** (Zhang 2021 *Nat Commun*) | BLD-LDAK heritability model | EUR; sparser traits | Lacks GCTA-model assumptions; legacy GCTA pipelines |
| **LDpred2-auto** (Privé 2020) | Bayesian + auto-tuning | Polygenic EUR | LD ref mismatch (s > 0.05); allow_jump_sign default True (must pin FALSE) |
| **PRS-CS-auto** (Ge 2019 *Nat Commun*) | Continuous-shrinkage prior | Polygenic EUR | Sparse-trait architecture; HapMap3-restricted variants only |
| **lassosum2** (Privé 2022) | Penalized regression | EUR alternative | Highly polygenic (Bayesian methods better); requires tuning data |
| **C+T** (PRSice-2; Choi 2019) | Clumping + thresholding | Legacy clinical scores (PRS313) | Highly polygenic; Bayesian methods dominate |
| **PROSPER** (Zhang 2024 *Nat Commun*) | Ensemble penalized regression | Multi-ancestry, AFR + others | Single-ancestry; tuning set < 1000 |
| **MUSSEL** (Jin 2024 *Cell Genomics*) | Spike-slab + super-learner | Multi-ancestry; admixed AFR | Single-ancestry; lacks tuning data |
| **JointPRS** (Xu L et al 2025 *Nat Commun* 16:3841) | Data-adaptive Bayesian | Multi-ancestry; sumstats only | Single-ancestry; very small target |
| **PRS-CSx** (Ruan 2022 *Nat Genet*) | PRS-CS multi-ancestry extension | Multi-ancestry with EUR + non-EUR sumstats | Low causal-variant overlap across ancestries |
| **BridgePRS** (Hoggart 2024 *Nat Genet*) | Ridge-bridge sharing | Low-h^2 AFR / low causal overlap | Standard scenarios (PROSPER/MUSSEL win) |
| **PolyPred / PolyPred+** (Weissbrod 2022) | BOLT-LMM + PolyFun-SuSIE | Multi-ancestry; biobank-scale | Small individual-level data; expensive |

**Citation traps caught by senior PIs:**
- **PRSmix** (Truong 2024); *Cell Genomics*, NOT *Nat Genet*.
- **MUSSEL** (Jin 2024); *Cell Genomics*.
- **PROSPER** (Zhang 2024); *Nat Commun*, NOT *Nat Genet*.
- **Hingorani 2023**; *BMJ Medicine* (NOT main *BMJ*).
- **Mavaddat 2023 BOADICEA update**; *Cancer Epi Biomark Prev*, NOT *Nat Genet*.
- **Mullins 2021** is bipolar disorder, NOT MDD (Howard 2019 *Nat Neurosci* = MDD; Mullins 2021 = BD).

## Multi-Ancestry: The Big Problem

Martin 2019 *Nat Genet* established the ~4.5x R^2 attenuation between EUR and AFR (Martin 2017 *AJHG* first showed demographic history drives it). Updates:
- **Martin 2019** *Nat Genet*: "Clinical use of current polygenic risk scores may exacerbate health disparities".
- **Mostafavi 2020** *eLife*: PRS accuracy varies even within a single ancestry due to age, sex, SES, GxE.
- **Ding 2023** *Nature* 618: PGS accuracy decays *continuously* along genetic-ancestry continuum (Pearson r = -0.95 vs PC distance from training data). **The 2026 standard is to report PRS performance vs continuous PC distance, NOT discrete ancestry boxes.**
- **Hou 2023** *Nat Genet*: causal effects are similar across local ancestries within admixed individuals (radmix ~0.95), supporting cross-population transfer.

Multi-ancestry method choice:
1. Individual-level non-EUR training data + tuning set >= 1000: **PROSPER** or **MUSSEL** (top performance).
2. Summary statistics only + small tuning: **JointPRS** or **PRS-CSx**.
3. Low h^2 / very polygenic / low causal overlap: **BridgePRS**.
4. Functional annotations critical + EUR-dominant: **SBayesRC** (cross-ancestry via `--ldm-eigen`).

## Calibration: The Hingorani Reframing

Khera 2018 *Nat Genet* established the clinical-PRS narrative; **Hingorani 2023** *BMJ Med* is the operative critique:

- HR/OR per SD is modest (~1.3 per SD); **similar to family history alone**.
- Among individuals who develop disease, only ~11% are detected at conventional high-risk PRS threshold; 5% false-positive rate.
- CAD top-2.5% PRS captures 7% of cases; breast-cancer top-2.5% captures 6%.
- Wald-Hingorani detection-rate / false-positive-rate ratios approach 10:1 for screening; current PRS achieve 2-3:1.

**Calibration mechanics:**
- Cross-ancestry calibration breaks for the *variance* of the PRS distribution, not just the mean.
- Recalibration: subtract conditional mean given first 4-10 PCs; divide by conditional SD; convert to percentile. **Compute PCs in the test cohort, NOT discovery-cohort PCs**.
- For absolute risk: integrate over external incidence curve (BOADICEA v5 / CanRisk for breast cancer; FOS for CAD).

## PRS-RS Reporting Standards (Wand 2021 *Nature*)

22-item checklist. Reviewer-priority items: cohort independence between development + evaluation (item 13); confounder adjustment in evaluation (item 16); absolute-risk reporting (item 19); ancestry composition of validation (item 21). *Nature Genetics*-tier manuscripts without PRS-RS adherence are rejected at review.

## Decision Tree by Scenario

| Scenario | Recommended path | Why |
|----------|------------------|-----|
| EUR cohort + individual-level data | LDpred2-auto or SBayesRC | SBayesRC integrates functional annotations |
| EUR cohort + sumstats only | MegaPRS or SBayesRC | LDpred2 also viable |
| Highly polygenic trait (height, BMI, education) | LDpred2-auto, PRS-CS-auto | Continuous-shrinkage priors well-suited |
| Sparse trait (lipids, AMD) | MegaPRS, SBayesRC | BLD-LDAK or SBayesR mixture priors |
| Multi-ancestry, large tuning set | PROSPER or MUSSEL | Top performance per benchmarks |
| Multi-ancestry, sumstats + small tuning | JointPRS or PRS-CSx | Joint Bayesian framework |
| Multi-ancestry, target = AFR | MUSSEL or BridgePRS | Best non-EUR performance |
| Combining multiple PGS Catalog scores | PRSmix (single trait) or PRSmix+ (cross-trait) | Elastic-net combination |
| Production score for biobank | `pgsc_calc` Nextflow nf-core | Handles liftover, ancestry, normalization automatically |
| No tuning data available | LDpred2-auto, PRS-CS-auto, JointPRS-auto | Bayesian auto-tuning |
| Clinical reporting | Apply Hingorani-aware framing: absolute-risk transform via external incidence curve | HR/OR per SD (~1.3) alone is inadequate for screening |

## Standard Workflow: LDpred2-auto

**Goal:** Compute LDpred2-auto PRS from sumstats + target genotypes with appropriate LD reference and sample-overlap detection.

**Approach:** Use bigsnpr R package; match variants strand-aware; compute LD or use prebuilt UK Biobank LD; run `snp_ldpred2_auto()` with shrinkage and jump-sign guards; assess `s` parameter for LD mismatch.

```r
library(bigsnpr)
library(data.table)

# Load target genotypes (PLINK .bed/.bim/.fam -> bigSNP object .rds)
# snp_readBed('target.bed', 'target.rds')
obj <- snp_attach('target.rds')
G <- obj$genotypes
map <- obj$map

# Load GWAS summary stats (standardized format)
sumstats <- fread('gwas_sumstats.txt')
# Required columns: chr, pos, a0 (ref), a1 (effect), beta, beta_se, n_eff, p

# Match variants strand-aware (snp_match handles A/T C/G ambiguity)
df_beta <- snp_match(sumstats, map, strand_flip = TRUE)

# Compute LD correlation matrix (in-sample) OR use prebuilt UKB LD.
# For a 3 cM window, pass the cM positions via `infos.pos = CHR_POS_CM` and set
# `size = 3`. Writing `size = 3/1000` is silently broken because 0.003 rounds to 0.
corr <- snp_cor(G, ind.col = df_beta[['_NUM_ID_']],
                infos.pos = df_beta[['cM']],
                size = 3,  # 3 cM window when infos.pos is in cM
                ncores = 8)

# LDSC heritability estimate + LD mismatch (s) diagnostic
ldsc_res <- snp_ldsc2(corr, df_beta)
h2_est <- ldsc_res[['h2']]
ldsc_s <- ldsc_res[['int']]  # intercept; large => sample overlap

# LDpred2-auto; run multiple chains in parallel
multi_auto <- snp_ldpred2_auto(
    corr, df_beta,
    h2_init = h2_est,
    vec_p_init = seq_log(1e-4, 0.2, 30),
    burn_in = 500, num_iter = 200,
    allow_jump_sign = FALSE,        # CRITICAL: pin to FALSE to avoid sign artifacts
    shrink_corr = 0.95,             # LD-shrinkage guard
    ncores = 8
)

# Filter divergent chains
beta_auto <- sapply(multi_auto, function(x) x$beta_est)
range_auto <- sapply(multi_auto, function(x) diff(range(x$corr_est)))
keep <- range_auto > (0.95 * quantile(range_auto, 0.95))
beta_final <- rowMeans(beta_auto[, keep, drop = FALSE])

# Score
pred <- big_prodMat(G, beta_final, ind.col = df_beta[['_NUM_ID_']])
```

## SBayesRC Workflow (Functional Annotations)

**Goal:** Compute PRS integrating ~96 functional annotations (baseline-LD v2.2) for +14% R^2 over SBayesR.

**Approach:** GCTB CLI with the SBayesRC algorithm; preprocess sumstats with `--impute-summary`.

```bash
# 1. Impute missing variants in sumstats against reference panel
gctb \
    --sbayes-rc \
    --impute-summary \
    --gwas-summary gwas_sumstats.ma \
    --ldm-eigen ukb_eigen_ld.eigen \
    --annot baselineLD_v2.2 \
    --out sbayesrc_preprocessed.ma

# 2. Run SBayesRC main step
gctb \
    --sbayes-rc \
    --gwas-summary sbayesrc_preprocessed.ma \
    --ldm-eigen ukb_eigen_ld.eigen \
    --annot baselineLD_v2.2 \
    --num-chains 4 --chain-length 25000 --burn-in 5000 \
    --out sbayesrc_run

# 3. Score target genotypes
plink2 --bfile target \
       --score sbayesrc_run.snpRes 2 5 8 header \
       --out sbayesrc_scores
```

## PGS Catalog Calculator (Production Pipeline)

**Goal:** Compute multiple published PGS scores in one pipeline with automatic liftover, ancestry projection, and normalization.

**Approach:** Nextflow nf-core `pgsc_calc` workflow handles GRCh37/38 liftover, PC-projection-based ancestry assignment, ambiguous-SNP filtering, and mean/variance normalization.

```bash
# Calculate multiple PGS for cohort
nextflow run pgscatalog/pgsc_calc \
    --input samplesheet.csv \
    --target_build GRCh38 \
    --pgs_id PGS000004,PGS000019,PGS001775 \
    --run_ancestry resources/pgsc_HGDP+1kGP_v1.tar.zst \
    --outdir pgsc_output/ \
    -profile docker
```

## Multi-Ancestry PRS-CSx

**Goal:** Compute multi-ancestry PRS using ancestry-specific GWAS sumstats jointly via continuous-shrinkage Bayesian framework.

**Approach:** PRS-CSx jointly models multiple ancestries with shared shrinkage prior; outperforms per-ancestry PRS-CS for non-EUR.

```bash
python PRScsx.py \
    --ref_dir=ldblk_1kg \
    --bim_prefix=target \
    --sst_file=eur_sumstats.txt,afr_sumstats.txt,eas_sumstats.txt \
    --n_gwas=200000,30000,50000 \
    --pop=EUR,AFR,EAS \
    --out_dir=prscsx_out --out_name=cohort \
    --phi=1e-2  # tune by trait architecture: 1e-2 polygenic, 1e-4 sparse

# Score each ancestry-specific posterior, then combine on tuning set
for pop in EUR AFR EAS; do
    plink2 --bfile target \
           --score prscsx_out/cohort_${pop}_pst_eff_a1_b0.5_phi1e-02.txt 2 4 6 \
           --out scores_${pop}
done
```

## Score Normalization and Ancestry Recalibration

**Goal:** Convert raw PRS to ancestry-conditional percentiles for clinical interpretation.

**Approach:** Subtract conditional mean given test-cohort PCs (NOT discovery PCs); divide by conditional SD.

```python
import numpy as np
from scipy import stats
import statsmodels.api as sm

def ancestry_conditional_normalize(prs, pcs, n_pcs=10):
    '''Recalibrate PRS by removing ancestry effects (Ding 2023 continuous-ancestry).

    pcs: matrix of principal components computed in the TEST cohort (not discovery).
    Returns: ancestry-conditional Z scores.
    '''
    X = sm.add_constant(pcs[:, :n_pcs])
    mean_model = sm.OLS(prs, X).fit()
    expected = mean_model.predict(X)
    residuals = prs - expected

    log_var_model = sm.OLS(np.log(residuals ** 2 + 1e-12), X).fit()
    expected_log_var = log_var_model.predict(X)
    sd = np.sqrt(np.exp(expected_log_var))

    return residuals / sd


def prs_to_percentile(z_scores):
    '''Convert ancestry-conditional Z to population percentile.'''
    return stats.norm.cdf(z_scores) * 100


def absolute_risk_transform(percentile, incidence_curve_age, age):
    '''Integrate over external age-conditional incidence curve to get absolute risk.

    Khera 2018 used FOS for CAD; Lee 2019 BOADICEA v5 for breast cancer.
    The HR-per-SD-only framing (Hingorani 2023 critique) is insufficient for screening.
    '''
    base_risk = incidence_curve_age(age)
    z = stats.norm.ppf(percentile / 100)
    relative_risk = np.exp(z * 0.5)  # placeholder; trait-specific log HR
    return base_risk * relative_risk
```

## Sample Overlap Detection (EraSOR / Bivariate LDSC Intercept)

**Goal:** Detect overlap between PRS-discovery cohort and target cohort, which inflates apparent PRS performance.

**Approach:** Run bivariate LDSC; |intercept| > 0.05 with target n >= 1000 is the typical alarm.

```bash
# bivariate LDSC for sample overlap
ldsc.py \
    --rg target_sumstats.sumstats.gz,discovery_sumstats.sumstats.gz \
    --ref-ld-chr eur_w_ld_chr/ \
    --w-ld-chr eur_w_ld_chr/ \
    --out overlap_check

# Inspect *.log: gcov_int is the sample-overlap-driven intercept (after gencov correction)
# |gcov_int| > 0.05 with target n >= 1000 => substantial overlap
```

## Per-Operation Failure Modes

**1. Discovery + tuning + test overlap (the inflated R^2 trap)**
- Trigger: GWAS run on UKB; PRS evaluated in UKB; tuning on UKB subset.
- Mechanism: Discovery samples leak into test set; PRS-derived effects fit the test data perfectly.
- Symptom: Reported R^2 inflated 2-5x; performance does not replicate in external cohort.
- Fix: Three-way disjoint sample partition (Wray 2014 *J Child Psychol Psychiatry*; Choi 2020 *Nat Protoc*); use **EraSOR** (Choi 2023 *GigaScience*) or bivariate LDSC intercept; threshold |intercept| > 0.05 with target n >= 1000.

**2. Treating discrete ancestry boxes as ground truth**
- Trigger: Report "PRS for AFR cohort" without quantifying genetic distance.
- Mechanism: Ancestry is continuous (Ding 2023 *Nature*); per-PC distance from training data drives R^2 with r = -0.95.
- Symptom: Reviewers reject for incomplete ancestry characterization.
- Fix: Project test cohort onto reference PCs; report performance as a function of continuous PC distance.

**3. Strand-ambiguous SNPs (A/T, C/G) handled wrong**
- Trigger: Drop or trust strand annotation across cohorts.
- Mechanism: ~10-15% of SNPs are strand-ambiguous; cross-platform/cohort scoring requires explicit handling.
- Symptom: Strand-flipped variants reverse effect direction; PRS uncorrelated with phenotype.
- Fix: PRSice-2 default drops them; LDpred2 `snp_match()` frequency-matches with 0.4-0.6 MAF tolerance.

**4. LD reference mismatch (high `s` parameter)**
- Trigger: Use 1KG-EUR LD for UK Biobank target; LDpred2 silently uses mismatched LD.
- Mechanism: `snp_ldsc2()` returns LD-mismatch parameter `s`; values > 0.05 indicate problematic mismatch.
- Symptom: Posterior effect estimates inflated; PRS doesn't replicate.
- Fix: Use UKB LD panel (n=40k+) instead of 1KG-EUR (n=489); inspect `s` routinely.

**5. PCs in derivation but not in evaluation**
- Trigger: GWAS uses 10 PCs; PRS evaluation regression omits PCs.
- Mechanism: Population stratification effects re-enter the PRS-phenotype association without PC control.
- Symptom: Apparent PRS association is partially ancestry confounding, not biology.
- Fix: Include same PCs in evaluation regression; compute PCs in TEST cohort (not discovery).

**6. Treating HR per SD = 1.5 as clinically actionable**
- Trigger: Report "top 5% PRS = 1.5x risk -> screening criterion".
- Mechanism: HR/OR per SD (~1.3) is similar to family history; Wald-Hingorani DR-to-FPR ratios approach 10:1 for true screening utility; PRS achieve 2-3:1.
- Symptom: Clinical implementation produces high false-positive rates.
- Fix: Integrate over external incidence curve for absolute-risk reporting; benchmark against family history specifically.

**7. PRSmix / MUSSEL / PROSPER cited in wrong journal**
- Trigger: Manuscript cites these as *Nat Genet*.
- Mechanism: PRSmix and MUSSEL = *Cell Genomics*; PROSPER = *Nat Commun*.
- Symptom: Senior PIs catch in review.
- Fix: Verify citations against PubMed before submission.

**8. HLA region included in PRS without explicit handling**
- Trigger: Compute autoimmune-disease PRS with HLA region included naively.
- Mechanism: HLA region (chr6 25-35 Mb) has extreme LD; SNP-based PRS does not capture classical HLA allele effects.
- Symptom: Reviewer flags incomplete HLA modeling.
- Fix: Exclude HLA region from main PRS; model classical HLA alleles separately via HIBAG / SNP2HLA / HLA-LA; report HLA-excluded + HLA-augmented versions.

**9. Sex chromosomes mishandled**
- Trigger: PRS includes chrX without sex-specific dosage coding.
- Mechanism: Males 0/1; females 0/1/2 unless XCI-corrected.
- Symptom: Cross-sex comparison invalid.
- Fix: Drop chrX OR apply explicit sex-stratified dosage encoding.

## Reconciliation: When Methods Disagree

| Pattern | Likely cause | Action |
|---------|-------------|--------|
| LDpred2-auto vs PRS-CS-auto disagree on top decile | Trait sparsity differs; method assumption mismatch | Use SBayesRC as tiebreaker; ensemble via PRSmix |
| Multi-ancestry methods rank differently | Tuning set size; ancestry composition | Report ensemble; document hyperparameter sensitivity |
| EUR PRS R^2 << non-EUR target R^2 | Expected; Martin 2017 transferability | Switch to PROSPER / MUSSEL / BridgePRS |
| PRS performance differs across age strata | Mostafavi 2020; within-ancestry heterogeneity | Report age-stratified PRS performance |
| PRS unrelated to phenotype despite high h^2 | Sample overlap; strand-ambiguous SNPs; PC issues | Run EraSOR; check `snp_match()` flips; recompute PCs in test |
| PRS percentile shifts with array platform | Different ascertainment of common variants | Recalibrate per-platform; use ancestry-conditional Z |

## Quantitative Thresholds and Conventions

| Threshold | Convention | Source |
|-----------|-----------|--------|
| HapMap3 SNPs | ~1.1M variants; required for PRS-CS, LDpred2 | HapMap project |
| LDpred2 LD ref `s` | < 0.05 indicates well-matched LD | Privé 2022 |
| EraSOR | |intercept| > 0.05 with n >= 1000 => sample overlap | Choi 2023 |
| MAF range for ambiguous SNPs | Drop or frequency-match 0.4-0.6 | LDpred2 default |
| INFO score (imputed) | >= 0.8 for inclusion | QC convention |
| Kinship coefficient cutoff | KING > 0.0884 = 3rd-degree or closer; remove | KING documentation |
| HLA region exclusion | chr6 28-34 Mb (some use 25-35) | Convention |
| HR/OR per SD typical | ~1.3 per SD | Hingorani 2023 BMJ Med |
| Top 2.5% PRS CAD detection rate | ~7% of cases captured | Hingorani 2023 |
| Mavaddat PRS313 | 313 SNPs, breast cancer | Mavaddat 2019 |
| Khera CAD PRS | ~6.6M variants | Khera 2018 |
| Patel CAD PRS | GPS_Mult; multi-ancestry SOTA 2023 | Patel 2023 |

## Common Errors

| Symptom | Cause | Solution |
|---------|-------|----------|
| PRS R^2 << expected on held-out data | Sample overlap with discovery | Run EraSOR; rebuild three-way disjoint splits |
| LDpred2-auto chains diverge | LD mismatch (`s` > 0.05) or wrong h^2 init | Use UKB LD panel; check `snp_ldsc2()` output |
| Strand-flip warnings ignored | `snp_match` defaults | Set `strand_flip = TRUE`; review flipped variants |
| HLA region produces extreme PRS values | Long-range LD | Exclude chr6 28-34 Mb; model HLA separately |
| Non-EUR PRS at chance | Method not multi-ancestry-aware | Switch to PROSPER/MUSSEL/BridgePRS |
| Different ranking with same data | Stochastic MCMC | Seed; report posterior CIs; check convergence |
| PGS Catalog liftover failure | Incompatible build | Use pgsc_calc auto-liftover; check log |
| Top 1% PRS appears benign | Conditional mean drift across ancestries | Apply Ding 2023 ancestry-conditional Z |

## Anticipated Reviewer Pushback

| Pushback | Standard response |
|----------|-------------------|
| "PRS HR 1.5 per SD is similar to family history" | Acknowledged (Hingorani 2023). We report absolute-risk integrated over age-conditional incidence (Wald-Hingorani framing); we do NOT recommend population-level screening on PRS alone. |
| "Why use Bayesian methods over C+T?" | LDpred2-auto / PRS-CS / SBayesRC capture polygenic architecture better; ~16-18% higher prediction correlation (r) vs C+T per Pain 2021 / Privé 2022 benchmarks. |
| "Why not use the largest published GWAS?" | We checked sample overlap between discovery and target with EraSOR / bivariate LDSC intercept; |intercept| < 0.05. |
| "Discrete ancestry boxes don't capture genetic structure" | Agreed; we report PRS performance vs continuous PC distance (Ding 2023 *Nature*); discrete labels are summary only. |
| "Why exclude HLA?" | HLA region extreme LD makes SNP-based posteriors unstable; we model classical HLA alleles separately via HIBAG / SNP2HLA. |
| "PRS-CS phi parameter; how chosen?" | We use --phi=auto with multiple chains; for sparse traits (lipids) 1e-4; for highly polygenic (height) 1e-2. |
| "Where is the absolute risk?" | Reported per Wand 2021 PRS-RS item 19; integrated over age-conditional incidence using external curve. |
| "FDA PRS guidance?" | No general FDA PRS draft guidance exists as of 2026; August 2025 Federal Register Class II classification for Cancer Predisposition Risk Assessment Systems is the operative regulatory text. |
| "Why three different references for SBayesRC?" | Zheng 2024 *Nat Genet* is the primary paper; baseline-LD is Gazal 2017; UKB LD panel is the bigsnpr/Privé 2020 release. |

## References

- Privé F et al. 2020. LDpred2: better, faster, stronger. *Bioinformatics* 36:5424.
- Privé F et al. 2022. Identifying and correcting for misspecifications in GWAS summary statistics and polygenic scores. *Hum Genet Genom Adv* 3:100136. (LDpred2 misspecification + lassosum2)
- Ge T et al. 2019. Polygenic prediction via Bayesian regression and continuous shrinkage priors. *Nat Commun* 10:1776. (PRS-CS)
- Ruan Y et al. 2022. Improving polygenic prediction in ancestrally diverse populations. *Nat Genet* 54:573. (PRS-CSx)
- Zheng Z et al. 2024. Leveraging functional genomic annotations and genome coverage to improve polygenic prediction of complex traits within and between ancestries. *Nat Genet* 56:767. (SBayesRC)
- Lloyd-Jones LR et al. 2019. Improved polygenic prediction by Bayesian multiple regression on summary statistics. *Nat Commun* 10:5086. (SBayesR)
- Zeng J et al. 2021. Widespread signatures of natural selection across human complex traits and functional genomic categories. *Nat Commun* 12:1164. (SBayesS)
- Zhang Q et al. 2021. Improved genetic prediction of complex traits from individual-level data or summary statistics. *Nat Commun* 12:4192. (MegaPRS)
- Zhang J et al. 2024. An ensemble penalized regression method for multi-ancestry polygenic risk prediction. *Nat Commun* 15:3238. (PROSPER)
- Jin J et al. 2024. MUSSEL: enhanced Bayesian polygenic risk prediction leveraging information across multiple ancestry groups. *Cell Genomics* 4:100539.
- Xu L et al. 2025. JointPRS: a data-adaptive framework for multi-population genetic risk prediction incorporating genetic correlation. *Nat Commun* 16:3841.
- Hoggart CJ et al. 2024. BridgePRS leverages shared genetic effects across ancestries. *Nat Genet* 56:180.
- Weissbrod O et al. 2022. Leveraging fine-mapping and multipopulation training data to improve cross-population polygenic risk scores. *Nat Genet* 54:450. (PolyPred)
- Zhao Z et al. 2022. The construction of cross-population polygenic risk scores using transfer learning. *Am J Hum Genet* 109:1998. (TL-PRS)
- Truong B et al. 2024. Integrative polygenic risk score improves the prediction accuracy of complex traits and diseases (PRSmix). *Cell Genomics* 4:100523.
- Mostafavi H et al. 2020. Variable prediction accuracy of polygenic scores within an ancestry group. *eLife* 9:e48376.
- Ding Y et al. 2023. Polygenic scoring accuracy varies across the genetic ancestry continuum. *Nature* 618:774.
- Hou K et al. 2023. Causal effects on complex traits are similar for common variants across segments of different continental ancestries within admixed individuals. *Nat Genet* 55:549.
- Hingorani AD et al. 2023. Performance of polygenic risk scores in screening, prediction, and risk stratification. *BMJ Med* 2:e000554.
- Wand H et al. 2021. Improving reporting standards for polygenic scores in risk prediction studies. *Nature* 591:211. (PRS-RS)
- Lambert SA et al. 2021. The Polygenic Score Catalog as an open database for reproducibility and systematic evaluation. *Nat Genet* 53:420.
- Lambert SA et al. 2024. Enhancing the Polygenic Score Catalog with tools for score calculation and ancestry normalization. *Nat Genet* 56:1989.
- Fritsche LG et al. 2020. Cancer PRSweb: an online repository with polygenic risk scores for major cancer traits and their evaluation in two independent biobanks. *Am J Hum Genet* 107:815. (PRSweb)
- Khera AV et al. 2018. Genome-wide polygenic scores for common diseases identify individuals with risk equivalent to monogenic mutations. *Nat Genet* 50:1219.
- Aragam KG et al. 2022. Discovery and systematic characterization of risk variants and genes for coronary artery disease in over a million participants. *Nat Genet* 54:1803.
- Patel AP et al. 2023. A multi-ancestry polygenic risk score improves risk prediction for coronary artery disease. *Nat Med* 29:1793.
- Mavaddat N et al. 2019. Polygenic risk scores for prediction of breast cancer and breast cancer subtypes. *Am J Hum Genet* 104:21. (PRS313)
- Conti DV et al. 2021. Trans-ancestry genome-wide association meta-analysis of prostate cancer identifies new susceptibility loci. *Nat Genet* 53:65.
- Trubetskoy V et al. 2022. Mapping genomic loci implicates genes and synaptic biology in schizophrenia. *Nature* 604:502. (PGC3)
- Howard DM et al. 2019. Genome-wide meta-analysis of depression identifies 102 independent variants. *Nat Neurosci* 22:343. (MDD)
- Mullins N et al. 2021. Genome-wide association study of more than 40,000 bipolar disorder cases. *Nat Genet* 53:817. (BIPOLAR; not MDD)
- Bellenguez C et al. 2022. New insights into the genetic etiology of Alzheimer's disease. *Nat Genet* 54:412.
- Mahajan A et al. 2022. Multi-ancestry genetic study of type 2 diabetes highlights the power of diverse populations. *Nat Genet* 54:560. (DIAMANTE)
- Suzuki K et al. 2024. Genetic drivers of heterogeneity in type 2 diabetes pathophysiology. *Nature* 627:347. (Largest T2D multi-ancestry GWAS)
- PGS Catalog: `https://www.pgscatalog.org`
- PGS Catalog Calculator: `https://github.com/PGScatalog/pgsc_calc`
- Federal Register August 2025 Cancer Predisposition Risk Assessment System: `https://www.federalregister.gov/documents/2025/08/21/2025-16035/`

## Related Skills

- clinical-databases/gnomad-frequencies - Population AF for QC
- clinical-databases/variant-prioritization - Rare-variant filtering background
- clinical-databases/clinvar-lookup - Variant pathogenicity
- causal-genomics/mendelian-randomization - PRS as instrument
- population-genetics/population-structure - Ancestry inference for PC computation
- machine-learning/biomarker-discovery - PRS as biomarker component
<!-- END FILE: clinical-databases/polygenic-risk/SKILL.md -->

## 子目录：clinical-databases/somatic-signatures

<!-- BEGIN FILE: clinical-databases/somatic-signatures/SKILL.md -->
---
name: bio-clinical-databases-somatic-signatures
description: Extracts and assigns COSMIC v3.4 mutational signatures (86 SBS / 11 DBS / 18 ID / 21 CN / 16 SV) from somatic VCFs using SigProfilerSuite, MutationalPatterns, MuSiCal mvNMF, SigNet, or HRDetect. Use when characterizing DNA-damage etiology (BRCA1/2 HRD, MMR-D, POLE, APOBEC3A, UV, tobacco, aflatoxin, 5-FU/SBS17b, platinum, colibactin SBS88), routing PARP inhibitor decisions, or auditing de novo extraction vs refit choice for cohort size.
tool_type: mixed
primary_tool: SigProfilerAssignment
---

## Version Compatibility

Reference examples tested with: SigProfilerMatrixGenerator 1.2+ (Bergstrom 2019), SigProfilerExtractor 1.1.24+ (Islam 2022), SigProfilerAssignment 0.1+ (Diaz-Gay 2023), MutationalPatterns 3.12+ (Manders 2022), MuSiCal 0.7+ (Jin 2024), SigNet (Serrano 2023, bioRxiv), HRDetect (Davies 2017 / Degasperi 2022 implementations), pandas 2.2+, R 4.3+. COSMIC v3.4 (2023, COSMIC v98): 86 SBS, 11 DBS, 18 ID, 21 CN, 16 SV signatures (v3.6 is the current catalog as of 2026).

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- R: `packageVersion('<pkg>')` then `?function_name`

If code throws ImportError, AttributeError, or TypeError, introspect the installed package and adapt the example to match the actual API rather than retrying. COSMIC signature naming evolves: SBS40 was split to SBS40a/b/c in v3.4 (Senkin 2024); SBS17 split to SBS17a/b (5-FU); SBS10 split to SBS10a-d (POLE/POLD1).

# Somatic Mutational Signatures; Etiology, Extraction, Clinical Use

**'Extract mutational signatures from this tumor cohort and identify HRD/MMR/APOBEC processes'** -> Generate 96-context (or DBS/ID/CN/SV) matrix from VCF; choose de novo extraction (NMF) vs refit-to-COSMIC by cohort size; map dominant signatures to etiology; flag clinical actionability.

- Python (recommended): SigProfilerMatrixGenerator -> SigProfilerExtractor (de novo) or SigProfilerAssignment (refit)
- R alternative: `MutationalPatterns::fit_to_signatures()` (strict refit) or `extract_signatures()` (NMF de novo)
- Python (mvNMF for non-uniqueness): MuSiCal (Jin 2024 *Nat Genet*)
- Python (deep learning low-mutation count): SigNet (Serrano 2023)
- R (HRD-specific): HRDetect (Davies 2017 *Nat Med*); the 6-feature BRCA-deficiency classifier

## COSMIC v3.4 Catalog: Evolution and Composition

| Class | Count | Encoding |
|-------|-------|----------|
| **SBS** (Single Base Substitutions) | 86 | 96 trinucleotide contexts (6 substitution types x 16 trinucleotides) |
| **DBS** (Doublet Base Substitutions) | 11 | 78 strand-agnostic doublet classes (Bergstrom 2019) |
| **ID** (Insertion/Deletion) | 18 | 83 categories (indel length x repeat context x microhomology) |
| **CN** (Copy Number) | 21 | 48 channels (total CN x heterozygosity x segment length; Steele 2022 *Nature*) |
| **SV** (Structural Variants) | 16 | 32 channels (cluster x length x type) |

**Recent splits to know:**
- **SBS40 -> SBS40a / SBS40b / SBS40c** (Senkin 2024 *Nature*): pan-cancer active (40a); RCC-specific (40b/c).
- **SBS17 -> SBS17a (T>C uncertain) / SBS17b (T>G in CTT, 5-FU)** (Christensen 2019 *Nat Commun*; Pich 2019 *Nat Genet*).
- **SBS7 -> SBS7a / 7b / 7c / 7d** (UV photoproduct chemistry; Alexandrov 2020).
- **SBS10 -> SBS10a (POLE P286R) / 10b (POLE V411L) / 10c / 10d (POLD1)** (Hodel 2020 *Mol Cell*).

## Etiology Table (Postdoc-grade)

| Signature | Etiology | Clinical implication | Notes |
|-----------|----------|---------------------|-------|
| **SBS1** | Spontaneous 5mC deamination at CpG | Age-correlated; mitotic-rate biomarker | Clock-like |
| **SBS5** | UNKNOWN, clock-like; age-correlated | -- | Reviewer-accepted: "unknown, clock-like"; NOT polymerase fidelity errors |
| **SBS2 / SBS13** | APOBEC (APOBEC3A dominant per Petljak 2022) | Often co-occur; kataegis; ICI response signal | A3A vs A3B via YTCA vs RTCA tetranucleotide ratio |
| **SBS3** | HRD (BRCA1/2 deficient flat profile) | **PARP inhibitor eligibility** | HRDetect 98.7% sensitivity (Davies 2017) |
| **ID6** | HRD microhomology-mediated deletions | PARP eligibility | Pairs with SBS3 |
| **CN17 (HRD-CN1)** | HRD chromosomal instability | PARP eligibility; also BRCA1 promoter hypermethylation | Steele 2022 |
| **SBS6 / 14 / 15 / 20 / 21 / 26 / 44 + ID1 / 2** | MMR-D | ICI eligibility | Lynch typically 6/15/26/44; sporadic MLH1-hyperMet typically 21/26 |
| **SBS14 + SBS20** | POLE+MMR or POLD1+MMR double defect | Ultra-hypermutator; ICI excellent response | >500 mut/Mb |
| **SBS10a / 10b** | POLE-exo P286R / V411L | Hypermutator; ICI excellent response | 100-300 mut/Mb pure POLE |
| **SBS10c / 10d** | POLD1 | -- | Less common |
| **SBS28** | POLE indirect | Often co-extracted with SBS10 | -- |
| **SBS4 + DBS2** | Tobacco smoking; benzo[a]pyrene-G adducts | Lung cancer | C>A bias |
| **SBS7a/b/c/d + DBS1** | UV (CPD vs 6-4 photoproduct chemistry) | Melanoma | CC>TT dipyrimidine, CC>AA |
| **SBS24** | Aflatoxin | HCC (geographic) | C>A at CpC; Schulze 2015 *Nat Genet* |
| **SBS22** | Aristolochic acid | UTC, HCC | T>A at CpTpG; Hoang 2013 *Sci Transl Med* |
| **SBS17b** | 5-Fluorouracil | Therapy-induced | T>G in CTT context |
| **SBS31 / 35 / 86 / 87** | Platinum chemotherapy | Therapy-induced; second cancers | Cisplatin / carboplatin / oxaliplatin |
| **SBS11** | Temozolomide | Glioma post-TMZ | C>T at unmethylated CpC/CpT |
| **SBS88 + ID18** | Colibactin (pks+ E. coli) | CRC etiology; NTHL1-syndrome backgrounds | Pleguezuelos-Manzano 2020 *Nature* |
| **SBS30** | NTHL1 BER deficiency | Lynch-like; cancer predisposition | High cosine to FFPE artifact |
| **SBS-FFPE-artifact** | Formalin-induced C>T (NOT SBS33 as commonly cited) | Sequencing artifact | ~0.90 cosine to SBS30 (formalin-induced C>T characterization in mutational-signatures literature; specific paper attribution removed pending verification) |

**CRITICAL CORRECTION:** The widely-cited "SBS33 = FFPE artifact" is wrong. Modern literature attributes FFPE artifact to a signature resembling SBS30 (NTHL1-BER-deficiency profile); after enzymatic uracil repair the artifact instead resembles SBS1.

## Tool Taxonomy

| Tool | Approach | Class coverage | When to use | Fails when |
|------|----------|----------------|-------------|-----------|
| **SigProfilerSuite** (Alexandrov lab; Bergstrom 2019 *BMC Genomics*; Islam 2022 *Cell Genomics*; Diaz-Gay 2023 *Bioinformatics*) | Matrix gen -> NMF de novo / forward-backward refit | SBS / DBS / ID / CN / SV | Field standard; CPIC-equivalent for signatures | Heavy compute for de novo (100 NMF replicates) |
| **MutationalPatterns** (Manders 2022 *BMC Genomics*) | R-based; strict refit + NMF de novo | SBS / DBS / ID; lesion segregation | R workflows; reproducible refit | Lacks SV signatures |
| **MuSiCal** (Jin 2024 *Nat Genet*) | mvNMF (minimum-volume NMF) addressing NMF non-uniqueness | SBS / DBS / ID | Mid-size cohorts; novel signatures suspected | Less benchmarking at very large scale |
| **SigNet** (Serrano 2023, bioRxiv) | ANN-based signature attribution | SBS | Low mutation counts | New tool; reproducibility data still maturing |
| **YAPSA** (Hubschmann 2021) | Linear combination decomposition | SBS | Comparison runs | Less widely used |
| **MutSignatures** (Fantini 2020) | Probabilistic refits | SBS | -- | -- |
| **deconstructSigs** (Rosenthal 2016) | NNLS (unregularized) | SBS | **DEPRECATED; never use** | NNLS overfits onto reference set; superseded by SigProfilerAssignment |
| **mSigAct** | Signatures from RNA-seq | SBS | RNA-seq only contexts | Limited resolution |
| **Helmsman** (Carlson 2018) | Fast matrix construction | SBS / DBS / ID | Preprocessing step only | Not for extraction/refit |
| **HRDetect** (Davies 2017 *Nat Med*) | Lasso logistic on 6 features (SBS3 / SBS8 / RS3 / RS5 / HRD-LOH / del-microhomology proportion) | HRD-specific | BRCA1/2 deficiency classifier | Breast/ovarian-trained; cross-cancer needs revalidation |
| **MutationTimer** (Gerstung 2020 *Nature*) | Mutation timing relative to CN states | SBS | PCAWG-style evolution | Requires Battenberg/ASCAT CN; >=30x coverage |

**The deprecation:** deconstructSigs is the most-cited signature tool in publications but is **operationally deprecated**. NNLS without regularization overfits onto the ~70-signature reference; reviewers flag manuscripts using it without SigProfilerAssignment sensitivity. Replace with SigProfilerAssignment or MutationalPatterns strict refit.

## De Novo vs Refit: The Field's Most-Contested Choice

**Degasperi 2022** *Science* (12,222 WGS, UK 100k Genomes) argued refitting underestimates novel signatures because variance is forced onto existing references. They identified 40 additional SBS and 18 DBS signatures by full de novo extraction.

**Operational rule:**

| Mutation count per sample | Cohort size | Approach |
|---------------------------|-------------|----------|
| > 200 (SBS96) | N >= 50 (or 100 for DBS/ID/CN) | **De novo extraction** (SigProfilerExtractor, MuSiCal); validate via split-sample CV + bootstrap stability |
| > 200 | N < 50 | Refit (SigProfilerAssignment) |
| 50-200 | Any | Refit only; flag low confidence |
| < 50 | Any | **Do not attempt single-sample signature analysis** |

**SigProfilerExtractor stability gates:**
- `nmf_replicates = 100` (default 100, do not reduce)
- minimum stability >= 0.2 per signature
- minimum average stability >= 0.8 across signatures
- combined stability == 1.0 for selected rank

Manuscripts reporting extraction without these stability values are unreviewable.

## Decision Tree by Scenario

| Scenario | Recommended path | Why |
|----------|------------------|-----|
| Single tumor WGS, > 200 mutations | SigProfilerAssignment refit | Single-sample de novo is unstable |
| Cohort >= 50 WGS, novel etiology suspected | SigProfilerExtractor de novo + cross-validate | Capture potentially novel signatures |
| Cohort >= 50 WGS, established cancer type | SigProfilerAssignment refit | Field consensus; fast |
| Mid-size cohort with novel signatures | MuSiCal mvNMF | Handles NMF non-uniqueness |
| Low mutation count (<100/sample) | SigNet (Serrano 2023) | ANN-based; optimized for low mutation counts |
| BRCA1/2 deficiency screen | HRDetect (Davies 2017) | 6-feature lasso classifier; 98.7% sensitivity |
| Tumor evolution / mutation timing | MutationTimer (Gerstung 2020) | Requires Battenberg CN; PCAWG-validated |
| FFPE samples | SigProfilerAssignment with explicit FFPE-artifact handling | SBS30-like artifact; matched fresh-frozen controls ideal |
| WES (not WGS) | SigProfilerMatrixGenerator with `exome=True` | Trinucleotide-context correction for capture bias |
| RNA-seq only | mSigAct | Limited resolution; supplement with DNA-seq if available |
| HRD CN signatures | SigProfilerExtractor CN mode + CN17 (HRD-CN1) | Steele 2022 framework |
| Cross-cancer signature comparison | SigProfilerSuite with strand bias on | Aristolochic-acid SBS22 shows strong transcribed-strand bias |

## Standard Workflow: SigProfilerSuite

**Goal:** Generate 96-context mutation matrix, extract de novo signatures with stability validation, and decompose to COSMIC v3.4 reference.

**Approach:** Three-step pipeline with explicit version pinning and stability gates.

```python
# Step 1: Install reference genome (one-time)
from SigProfilerMatrixGenerator import install as genInstall
genInstall.install('GRCh38')

# Step 2: Generate matrix
from SigProfilerMatrixGenerator.scripts import SigProfilerMatrixGeneratorFunc as matGen
matrices = matGen.SigProfilerMatrixGeneratorFunc(
    project='cohort_2026',
    genome='GRCh38',
    vcfFiles='/path/to/vcf_directory',
    plot=True,
    exome=False,  # True if WES; corrects trinucleotide capture bias
    bed_file=None,  # Restrict to BED region if panel
    chrom_based=False,
    tsb_stat=True  # Transcribed-strand statistics
)
```

```python
# Step 3a (cohort >= 50): de novo extraction with stability gates
from SigProfilerExtractor import sigpro as sig
sig.sigProfilerExtractor(
    input_type='matrix',
    input_data='cohort_2026/output/SBS/cohort_2026.SBS96.all',
    output='extraction_output',
    reference_genome='GRCh38',
    opportunity_genome='GRCh38',
    minimum_signatures=1,
    maximum_signatures=12,
    nmf_replicates=100,            # Required for stability
    cpu=-1,
    seeds='random',
    matrix_normalization='gmm',
    resample=True,
    batch_size=1,
    refit_denovo_signatures=True,
    cosmic_version=3.4              # Match to current COSMIC release
)
```

```python
# Step 3b (single sample or cohort < 50): refit to COSMIC
from SigProfilerAssignment import Analyzer as Analyze
Analyze.cosmic_fit(
    samples='cohort_2026/output/SBS/cohort_2026.SBS96.all',
    output='assignment_output',
    input_type='matrix',
    genome_build='GRCh38',
    cosmic_version=3.4,
    signature_database='SBS_GRCh38_GRCh38',  # Verify against the SigProfilerAssignment release; the bundled
                                              # COSMIC signature-database identifiers change between versions.
    nnls_add_penalty=0.05,         # Forward-add gate
    nnls_remove_penalty=0.01,      # Backward-remove gate
    initial_remove_penalty=0.05,
    refit_denovo_signatures=False,
    make_plots=True,
    sample_reconstruction_plots=True
)
```

## MutationalPatterns Strict Refit (R Alternative)

**Goal:** Same as SigProfilerAssignment but in R; suited for Bioconductor pipelines.

**Approach:** Cosine-based stopping reduces overfitting vs deconstructSigs.

```r
library(MutationalPatterns)
library(BSgenome.Hsapiens.UCSC.hg38)

# Load VCFs as GRanges
vcf_files <- list.files('vcf_dir', pattern = '\\.vcf$', full.names = TRUE)
sample_names <- gsub('\\.vcf$', '', basename(vcf_files))
vcfs <- read_vcfs_as_granges(vcf_files, sample_names,
                              ref_genome = 'BSgenome.Hsapiens.UCSC.hg38')

# Generate 96-context matrix
mut_mat <- mut_matrix(vcf_list = vcfs, ref_genome = 'BSgenome.Hsapiens.UCSC.hg38')

# Fit to COSMIC v3.4 with strict refit (cosine-stopping; avoids deconstructSigs overfit)
signatures <- get_known_signatures(muttype = 'snv', source = 'COSMIC_v3.4',
                                    sig_type = 'reference', genome = 'GRCh38')
strict_refit <- fit_to_signatures_strict(mut_mat, signatures, max_delta = 0.004)

# Plot relative + absolute contributions
plot_contribution(strict_refit$fit_res$contribution, signatures, mode = 'relative')
```

## HRDetect for BRCA1/2 Deficiency

**Goal:** Classify tumors as HRD vs HR-proficient using the 6-feature Davies 2017 lasso.

**Approach:** Compute SBS3, SBS8, RS3 (rearrangement signature 3), RS5, HRD-LOH score, and the proportion of deletions with microhomology; apply lasso classifier.

```r
# Davies 2017 HRDetect framework
# Features: SBS3, SBS8, RS3, RS5, HRD-LOH, proportion of deletions with microhomology
# Output: probability of HRD; threshold 0.7 = HRD-positive
library(signature.tools.lib)

hrdetect <- HRDetect_pipeline(
    SNV_vcf_files = snv_vcfs,
    Indels_vcf_files = indel_vcfs,
    SV_bedpe_files = sv_bedpes,
    CNV_tab_files = cnv_tables,
    genome.v = 'hg38',
    nparallel = 8
)

# hrdetect$hrdetect_output has BRCA_prob per sample
# >= 0.7 = HRD-positive; consider PARP inhibitor
```

## Per-Operation Failure Modes

**1. Single-sample de novo extraction**
- Trigger: Run SigProfilerExtractor on a cohort of 1.
- Mechanism: NMF requires multiple samples to find stable rank; single-sample 96-context spectrum has unstable signature decomposition.
- Symptom: Tool runs but signatures are noisy and inconsistent across replicates.
- Fix: Use refit (SigProfilerAssignment) for cohorts < 50; never de novo on single samples.

**2. Sub-100-mutation sample analyzed individually**
- Trigger: Calculate signatures for a tumor with <100 mutations.
- Mechanism: 96-context SBS spectrum needs 200-500 mutations for stable estimation; sub-100 produces signal-to-noise dominated by stochastic context distribution.
- Symptom: Random or implausible signature contributions.
- Fix: Aggregate samples in a meta-tumor for cohort analysis; for single-sample at low count consider SigNet which is optimized for low counts.

**3. FFPE artifact misclassified as SBS30 / SBS33**
- Trigger: Pipeline reports SBS33 (or SBS30) as biologically meaningful.
- Mechanism: FFPE-induced C>T deamination produces a profile resembling SBS30 (~0.90 cosine); after enzymatic uracil repair resembles SBS1. Pre-2022 literature incorrectly cited SBS33.
- Symptom: False NTHL1-BER-deficiency or "unknown SBS33" reports in cohorts using FFPE samples without matched controls.
- Fix: Run matched fresh-frozen controls in cohort; flag FFPE samples for separate analysis; use enzymatic-uracil pretreatment; expect SBS30-like artifact, not SBS33.

**4. WES + signature analysis without trinucleotide correction**
- Trigger: Run SigProfilerExtractor on WES VCFs with `exome=False`.
- Mechanism: WES capture has biased trinucleotide composition vs whole genome.
- Symptom: Apparent signature differences from WGS-derived signatures are artifactual.
- Fix: Set `exome=True`; this triggers trinucleotide-context correction.

**5. Refit chosen for cohort with novel etiology**
- Trigger: Tropical-region cohort with putative novel mutagen exposure; refit to COSMIC.
- Mechanism: Refit constrains variance onto existing catalog; novel signatures appear as residual or are decomposed onto closest-cosine known signatures.
- Symptom: Apparent absence of novel etiology despite biological hypothesis.
- Fix: For cohorts >= 50 run de novo extraction with cross-validation; Senkin 2024 kidney cancer cohort exemplifies the gain.

**6. APOBEC SBS2 vs SBS13 conflation; A3A vs A3B**
- Trigger: Report "APOBEC activity" without subtype.
- Mechanism: Petljak 2022 *Nature* established APOBEC3A as dominant active deaminase; the SBS2/SBS13 ratio reflects REV1-dependent translesion synthesis.
- Symptom: Lose mechanistic insight; potential mis-attribution.
- Fix: Distinguish A3A (YTCA 5' tetranucleotide preference) vs A3B (RTCA); cite Petljak 2022.

**7. SBS5 attributed to "polymerase fidelity errors"**
- Trigger: Manuscript claims SBS5 = replication errors.
- Mechanism: SBS5 etiology is contested; clock-like, age-correlated, modulated by ERCC2/TC-NER but not established as polymerase errors.
- Symptom: Reviewers reject.
- Fix: Report as "unknown, clock-like" until field consensus.

**8. Cross-version comparison without re-extraction**
- Trigger: Compare SBS40 contributions from v3.2 (single signature) vs v3.4 (split into 40a/b/c).
- Mechanism: Signature splits/merges occur between versions; cross-version exposures are not directly comparable.
- Symptom: Apparent "loss" or "gain" of activity due to renaming.
- Fix: Re-run with current COSMIC version; document version in methods.

**9. Strand bias ignored**
- Trigger: SBS22 (aristolochic acid) reported without transcribed-strand bias.
- Mechanism: Aristolochic-acid mutagenesis strongly biased toward transcribed strand; SigProfiler handles via `tsb_stat=True`, MutationalPatterns supports, deconstructSigs ignores.
- Symptom: Mis-attribution; loss of mechanistic evidence.
- Fix: Use SigProfiler or MutationalPatterns; enable strand-bias output.

## Reconciliation: When Methods Disagree

| Pattern | Likely cause | Action |
|---------|-------------|--------|
| SigProfiler de novo vs refit different signatures | De novo finds novel + refit forces onto COSMIC | If cohort >= 50, prefer de novo; document |
| MutationalPatterns vs SigProfilerAssignment different exposures | NNLS vs forward-backward selection differences | Compare cosine similarity to mut_mat; pick better reconstruction |
| HRDetect calls HR-deficient + BRCA wildtype | BRCA1 promoter hypermethylation; PALB2 / FBXW7 / CDK12 alterations | Confirm with HRD-LOH score; assay BRCA1 methylation |
| Cosine to SBS3 high but ID6 absent | Single-feature HRD signal insufficient | Use HRDetect 6-feature classifier, not SBS3 alone |
| APOBEC signature present + low TMB | Cohort has APOBEC but not hypermutator | Both can coexist; YTCA/RTCA discriminates A3A vs A3B |
| FFPE samples produce SBS30 / SBS33-like signal | Almost always artifact | Run matched FF controls; use enzymatic uracil pretreatment |
| Cohort signature contributions implausible | Sub-100-mutation samples included | Stratify by mutation count; report >=200 separately |

## Quantitative Thresholds and Conventions

| Threshold | Convention | Source |
|-----------|-----------|--------|
| SBS96 stable extraction | >=200 mutations per sample | Alexandrov 2020 |
| De novo extraction cohort | N >= 50 (SBS); N >= 100 (DBS/ID/CN) | Field consensus |
| nmf_replicates | 100 (default; do not reduce) | SigProfilerExtractor |
| Stability gate | minimum stability >= 0.2; average >= 0.8 | SigProfilerExtractor defaults |
| Cosine similarity for "same signature" | > 0.85 (some use 0.90) | Convention |
| SBS-FFPE-artifact cosine to SBS30 | ~0.90 | formalin-induced C>T characterization (mutational-signatures literature; specific primary citation pending verification) |
| HRDetect threshold | BRCA_prob >= 0.7 = HRD-positive | Davies 2017 |
| POLE-exo + MMR mutation count | >500 mut/Mb (ultra-hypermutator) | Alexandrov 2020 |
| Pure POLE-exo mutation count | 100-300 mut/Mb | Alexandrov 2020 |
| MMR-D typical mutation count | 30-50 mut/Mb | Salem 2018 *Mol Cancer Res* |
| COSMIC version | 3.4 (2023, COSMIC v98); v3.6 current | COSMIC database |

## Common Errors

| Symptom | Cause | Solution |
|---------|-------|----------|
| Tool reports SBS33 in FFPE cohort | Mis-attribution of FFPE artifact | Confirm by examining trinucleotide pattern; FFPE artifact resembles SBS30 in modern catalog |
| Single tumor signature attribution unstable | Sub-200-mutation sample analyzed alone | Aggregate; use SigNet for low-count |
| Refit ignores novel etiology | Forced onto COSMIC reference | Run de novo on cohort if N >= 50 |
| HRDetect false negative | Missing one of 6 features (ID6, RS3, RS5, HRD-LOH) | Confirm all features computed; assay BRCA1 methylation |
| Strand bias not detected | Tool/setting ignores transcribed-strand | Use SigProfilerSuite with `tsb_stat=True` or MutationalPatterns |
| WES vs WGS signatures differ | Capture-bias trinucleotide composition | Set `exome=True` in SigProfilerMatrixGenerator |
| Platinum-treated tumor: SBS31 vs SBS35 confusion | Both attributed to platinum; SBS35 closer to direct Drost lab signature | Report both; cosine to direct |
| Aristolochic-acid signature in non-exposure context | Bias from highly-expressed transcribed-strand artifacts | Check geographic + clinical history |

## Anticipated Reviewer Pushback

| Pushback | Standard response |
|----------|-------------------|
| "Why not deconstructSigs?" | Operationally deprecated; NNLS overfits. Use SigProfilerAssignment or MutationalPatterns strict refit. |
| "Single tumor signatures meaningless?" | Below 200 mutations: yes. We aggregate cohorts and run refit for low-mutation samples. |
| "The de novo NMF rank choice?" | nmf_replicates=100 with stability gates; minimum >=0.2, average >=0.8, combined =1.0; SigProfilerExtractor defaults. |
| "FFPE samples bias signatures" | Modern attribution: FFPE artifact resembles SBS30 (not SBS33); we run matched FF controls or use enzymatic uracil pretreatment. |
| "SBS5 etiology; 'unknown' is unsatisfying" | Tomasetti-Vogelstein clock model; Druck 2026 FHIT + TC-NER; field has not converged; we report "unknown, clock-like". |
| "Why no APOBEC subtype distinction?" | Reported via YTCA vs RTCA tetranucleotide ratio per Petljak 2022; not all tools surface this; we used SigProfilerTopography. |
| "Cohort cross-comparison with old paper" | Re-extracted with COSMIC v3.4; signature splits (SBS40 -> 40a/b/c, SBS17 -> 17a/b) make pre-2024 exposures non-comparable. |
| "HRDetect cross-cancer validation" | Original Davies 2017 trained on breast cancer; we revalidated in our cohort with cross-cancer HRD-LOH score. |

## References

- Alexandrov LB et al. 2020. The repertoire of mutational signatures in human cancer. *Nature* 578:94. (PCAWG)
- Tate JG et al. 2019. COSMIC: the Catalogue Of Somatic Mutations In Cancer. *Nucleic Acids Res* 47:D941. (COSMIC v86)
- Senkin S et al. 2024. Geographic variation of mutagenic exposures in kidney cancer genomes. *Nature* 629:910. (SBS40a/b/c split)
- Steele CD et al. 2022. Signatures of copy number alterations in human cancer. *Nature* 606:984. (COSMIC CN signatures)
- Petljak M et al. 2022. Mechanisms of APOBEC3 mutagenesis in human cancer cells. *Nature* 607:799. (A3A dominance)
- Bergstrom EN et al. 2019. SigProfilerMatrixGenerator: a tool for visualizing and exploring patterns of small mutational events. *BMC Genomics* 20:685.
- Islam SMA et al. 2022. Uncovering novel mutational signatures by de novo extraction with SigProfilerExtractor. *Cell Genomics* 2:100179.
- Diaz-Gay M et al. 2023. Assigning mutational signatures to individual samples and individual somatic mutations with SigProfilerAssignment. *Bioinformatics* 39:btad756.
- Manders F et al. 2022. MutationalPatterns: the one-stop shop for the analysis of mutational processes. *BMC Genomics* 23:134.
- Jin H et al. 2024. Accurate and sensitive mutational signature analysis with MuSiCal. *Nat Genet* 56:541.
- Davies H et al. 2017. HRDetect is a predictor of BRCA1 and BRCA2 deficiency based on mutational signatures. *Nat Med* 23:517.
- Degasperi A et al. 2022. Substitution mutational signatures in whole-genome-sequenced cancers in the UK population. *Science* 376:abl9283.
- Christensen S et al. 2019. 5-Fluorouracil treatment induces characteristic T>G mutations in human cancer. *Nat Commun* 10:4571. (SBS17b)
- Pich O et al. 2019. The mutational footprints of cancer therapies. *Nat Genet* 51:1732.
- Hayward NK et al. 2017. Whole-genome landscapes of major melanoma subtypes. *Nature* 545:175. (UV signatures)
- Schulze K et al. 2015. Exome sequencing of hepatocellular carcinomas. *Nat Genet* 47:505. (Aflatoxin SBS24)
- Hoang ML et al. 2013. Mutational signature of aristolochic acid exposure as revealed by whole-exome sequencing. *Sci Transl Med* 5:197ra102.
- Pleguezuelos-Manzano C et al. 2020. Mutational signature in colorectal cancer caused by genotoxic pks+ E. coli. *Nature* 580:269. (Colibactin SBS88)
- Gerstung M et al. 2020. The evolutionary history of 2,658 cancers. *Nature* 578:122. (MutationTimer)
- Hodel KP et al. 2020. POLE mutation spectra are shaped by the mutant allele identity, its abundance, and mismatch repair status. *Mol Cell* 78:1166.
- (FFPE-induced C>T mutational artifact: the earlier "Guyard 2022 Nat Commun" attribution could not be verified -- consult current FFPE-artifact literature for a confirmed primary citation.)
- COSMIC Signatures: `https://cancer.sanger.ac.uk/signatures/`

## Related Skills

- clinical-databases/tumor-mutational-burden - TMB and ICI biomarker
- clinical-databases/msi-detection - MSI as MMR-D biomarker (paired with SBS6/15/26/44)
- variant-calling/variant-calling - Somatic VCF input
- variant-calling/variant-calling - Mutect2 / Strelka2 somatic upstream
- data-visualization/heatmaps-clustering - Signature contribution visualization
<!-- END FILE: clinical-databases/somatic-signatures/SKILL.md -->

## 子目录：clinical-databases/tumor-mutational-burden

<!-- BEGIN FILE: clinical-databases/tumor-mutational-burden/SKILL.md -->
---
name: bio-clinical-databases-tumor-mutational-burden
description: Calculates tumor mutational burden from WES/WGS/panel data with Friends of Cancer Research harmonization equations, per-assay calibration (FDA 10/Mb = 7.8 TSO500 = 8.4 OncomineTML), synonymous/indel/germline filtering, hypermutator tiering, blood TMB, and integration with HLA-LOH and neoantigen quality (Luksza 2017 fitness). Use when assessing ICI eligibility under tumor-specific cutoffs (McGrail 2021), comparing tissue vs bTMB, or auditing TMB-H reporting against ESMO 2024 and FDA pembrolizumab pan-tumor 2020.
tool_type: python
primary_tool: cyvcf2
---

## Version Compatibility

Reference examples tested with: cyvcf2 0.30+, VEP 111+ (or snpEff 5.2+), pandas 2.2+, numpy 1.26+, LOHHLA 1.0+ (McGranahan 2017), DASH 1.0+ (Pyke 2022). v4.1 (May 2024) gnomAD is current for germline subtraction. Friends of Cancer Research TMB harmonization framework (Vega 2021 *Ann Oncol*) and ESMO 2024 (Mosele *Ann Oncol*) define the operational thresholds.

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `<tool> --version`

If code throws ImportError, AttributeError, or TypeError, introspect the installed package and adapt the example to match the actual API rather than retrying. TMB calculation requires VCF with VEP / snpEff / Funcotator consequence annotations; the panel size used as denominator MUST match the assay's actual scored region, NOT the panel's total content.

# Tumor Mutational Burden; Calculation, Harmonization, ICI Eligibility

**'Calculate TMB from this somatic VCF and apply ICI eligibility cutoff'** -> Count nonsynonymous coding variants passing VAF/depth/germline filters; divide by assay scored region in Mb; apply assay-calibrated TMB-H cutoff; integrate with MSI / HLA-LOH / neoantigen quality.

- Python: `cyvcf2.VCF()` + VEP/snpEff consequence parsing + panel-size normalization
- CLI: `bcftools view` filtering + custom counting
- HLA-LOH: LOHHLA (McGranahan 2017 *Cell*) or DASH (Pyke 2022 *Nat Commun*)
- Neoantigen quality: pVAC-tools, NetMHCpan-4.1, Luksza 2017 fitness model

## Regulatory and Trial Landscape

| Event | Year | Threshold | Notes |
|-------|------|-----------|-------|
| **KEYNOTE-158 + FDA pembrolizumab pan-tumor approval** | 2020 | TMB-H >= 10 mut/Mb | FoundationOne CDx companion diagnostic; 10 cohorts |
| **Friends of Cancer Research TMB harmonization Phase I (Merino 2020)** | 2020 | -- | 11 panels vs WES truth; 3-fold panel-specific differences |
| **Friends of Cancer Research Phase II (Vega 2021)** | 2021 | Calibration equations | 19 platforms; per-assay calibration to WES-aligned TMB-Mb |
| **ESMO 2024 (Mosele *Ann Oncol*)** | 2024 | TMB-H >= 10/Mb retained (tumour-agnostic, ESCAT IB) | Tumour-type limits per McGrail 2021 |
| **KEYNOTE-189 (NSCLC + pembrolizumab + chemo)** | 2018 | -- | TMB-H did NOT enrich for benefit with chemo backbone |
| **POSEIDON / KEYNOTE-021 / KEYNOTE-407** | 2019-2022 | -- | TMB inconsistent with chemo backbones |
| **B-F1RST + BFAST Cohort C (bTMB)** | 2022 | bTMB >= 16/Mb | BFAST Cohort C FAILED primary endpoint |

## Friends of Cancer Research Harmonization: Cross-Panel Calibration

Merino 2020 *J Immunother Cancer*: in silico panel sampling from TCGA WES truth showed panel-specific TMB can differ 3-fold for identical samples. Vega 2021 *Ann Oncol* derived per-panel calibration equations to translate panel TMB to WES-aligned TMB-Mb.

**Per-panel calibration to FoundationOne 10/Mb sensitivity:**

| Panel | Scored region (Mb) | Equivalent threshold for FDA 10/Mb pan-tumor | Fails when |
|-------|---------------------|----------------------------------------------|-----------|
| **FoundationOne CDx** | 0.8 Mb scored (NOT 1.1 Mb total) | 10 mut/Mb (FDA reference; F1CDx companion) | Using 1.1 Mb panel total inflates TMB ~37%; pipeline excludes synonymous (F1CDx includes them) |
| **MSK-IMPACT v3** | 0.98 Mb | ~10 (full Vega 2021 calibration recommended) | Tumor purity < 30%; non-paired-normal mode |
| **MSK-IMPACT v4** | 1.22 Mb | ~10 | -- |
| **TruSight Oncology 500** | ~1.3 Mb scored (from 1.94 Mb total) | **7.8 mut/Mb** | Pipeline uses 10/Mb instead of the TMB2-calibrated 7.8 (Ramos-Paradas 2021) |
| **Oncomine Tumor Mutation Load** | 1.2 Mb | **8.4 mut/Mb** | Pipeline uses 10/Mb instead of the TMB2-calibrated 8.4 (Ramos-Paradas 2021) |
| **Caris MI Tumor Seek** | ~1.2 Mb |; (verify Caris docs) | -- |
| **Tempus xT v3** | 0.6 Mb | -- | Below 0.8 Mb minimum reliability threshold |
| **Predicine ATLAS** | ~0.6 Mb | -- | Below 0.8 Mb minimum; high sampling variance |

**TMB =/= TMB across vendors.** Manuscripts that compare TMB across panels without per-assay calibration are unreviewable. Use the Vega 2021 calibration equations or WES re-projection.

## Variant-Counting Subtleties

These choices alter TMB by 5-20%:

| Variable | Convention | Notes |
|----------|-----------|-------|
| **Synonymous variants** | **FoundationOne CDx INCLUDES synonymous** (rationale: reduces sampling noise); MSK-IMPACT and most academic pipelines exclude | The FDA companion diagnostic counts synonymous; frequent misconception |
| **Indels** | FoundationOne includes; some assays exclude frameshift only | 5-15% TMB impact |
| **Germline subtraction** | Paired-normal (gold standard); else gnomAD AF <=0.5% (sometimes 1%) for tumor-only | Population-stratified gnomAD AF for ancestry-diverse cohorts |
| **VAF threshold** | FoundationOne >=5%; >=10% for tumor-only no UMI; down to 2% with paired-normal | Lower VAF risks contamination/artifacts |
| **Hotspots** | COSMIC-confirmed driver hotspots typically EXCLUDED (not random) | Inflates TMB if included |
| **Tumor purity** | FoundationOne >=20%; MSK-IMPACT >=30% | Below floor erodes VAF-based filtering |
| **VEP version** | Pin to assay's annotation version | gnomAD v4 uses VEP 105 |

## Hypermutator Tiering

| Class | Threshold | Common etiology |
|-------|-----------|----------------|
| **TMB-H (FDA pan-cancer)** | >= 10 mut/Mb | Variable; ICI eligible |
| **Hypermutator (research)** | >= 100 mut/Mb | MMR-D, POLE-exo |
| **Ultra-hypermutator** | >= 500 mut/Mb | POLE+MMR concurrent |

MSI-H typically 30-50 mut/Mb; pure POLE-exo P286R 100-300 mut/Mb; POLE-exo + MMR-D exceeds 500. MSI-H and TMB-H overlap substantially (~83% of MSI-H are TMB-H) but only ~16% of TMB-H solid tumors are MSI-H (Chalmers 2017 *Genome Med* 9:34).

## The Tumor-Type-Specific Cutoff Debate

**McGrail 2021** *Ann Oncol* is the most damning paper for the universal 10/Mb cutoff. TMB-H predicts ICI response in melanoma, NSCLC, bladder; but FAILS in breast, prostate, glioma. ORR in TMB-H melanoma/NSCLC/bladder was 39.8%; TMB-H breast/prostate/glioma was 15.3%. Mechanistic explanation: TMB only predicts when baseline CD8 T-cell infiltrate is present.

**Sha 2020** *Cancer Discov*: TMB-H predicts ICI benefit in MSS subset but adds nothing on top of MSI-H (because MSI-H is uniformly hypermutator and uniformly responsive).

**Samstein 2019** *Nat Genet* (MSK-IMPACT 1,662 ICI-treated): cancer-specific TMB cutoffs (top 20% within each tumor type) outperform universal 10/Mb.

**ESMO 2024** retained TMB-H >= 10/Mb pan-tumor (tumour-agnostic, ESCAT IB). The tumour-type limits (poor performance in breast, prostate, glioma) come from **McGrail 2021**, not ESMO.

## Blood TMB (bTMB): The Negative-Trial Story

**Gandara 2018** *Nat Med*: bTMB on Foundation Medicine FoundationACT panel; POPLAR + OAK retrospective. bTMB >= 16 mut/Mb showed PFS benefit with atezolizumab in NSCLC.

**B-F1RST (Kim 2022)**: prospective phase 2 test of bTMB >= 16 as a first-line atezolizumab predictor in NSCLC; did NOT meet its pre-specified primary endpoint (bTMB-H improved ORR 28.6% vs 4.4%, only a non-significant PFS/OS trend).

**BFAST Cohort C (Peters 2022)**: FAILED primary endpoint; atezolizumab vs chemo in bTMB-H NSCLC did not improve investigator-assessed PFS. Dominant confounder: low ctDNA shed fraction produces false-negative bTMB.

**Operational state:** bTMB is research-grade in tissue-naive settings; tissue TMB remains the regulatory standard.

## Neoantigen Quality: Beyond Raw TMB

**Luksza 2017** *Nature*: neoantigen fitness model. Combines "non-selfness" (TCR recognition probability via IEDB similarity) + "selfness" (MHC binding affinity differential vs WT peptide). Pancreatic-cancer validation (Balachandran 2017 *Nature*): long-term survivors had higher-quality neoantigens. Luksza 2022 *Nature*: immunoediting over 10 years.

**McGranahan 2016** *Science*: **clonal neoantigen burden** (mutations present in all tumor cells) predicts ICI response better than total. Subclonal-rich tumors evade despite high TMB.

**HLA-LOH** (McGranahan 2017 *Cell*, LOHHLA; Pyke 2022 *Nat Commun*, DASH; Montesion 2021 *Cancer Discov* for the ~17% pan-cancer estimate): HLA-LOH occurs in ~40% of NSCLC and abolishes neoantigen presentation for the lost allele. ~17% pan-cancer; >30% in HNSCC / NSCLC / cervical. Co-occurs with high subclonal burden + APOBEC + immune escape.

## Decision Tree by Scenario

| Scenario | Recommended path | Why |
|----------|------------------|-----|
| Pan-tumor ICI eligibility (FDA pembrolizumab) | TMB-H >= 10/Mb on FoundationOne CDx | FDA companion diagnostic |
| Non-FoundationOne panel | Apply per-assay calibration to the FoundationOne 10/Mb equivalent | TSO500 = 7.8; Oncomine = 8.4 (Ramos-Paradas 2021) |
| WES TMB | Compute directly; threshold per ESMO 2024 = 10/Mb | WES is reference standard |
| Tissue-naive bTMB | Caution: BFAST Cohort C failed | Research-grade; check ctDNA shed fraction |
| Breast / prostate / glioma | TMB-H does not enrich ICI response per McGrail 2021 | Tumor-type-specific cutoffs |
| MSI-H + TMB-H concurrence | MSI-H supersedes for ICI biomarker decision | Sha 2020 |
| Hypermutator characterization (>=100/Mb) | Confirm MMR-D or POLE-exo via signatures + IHC | Co-occurrence is common |
| Neoantigen quality (research) | Luksza fitness + HLA-LOH (LOHHLA / DASH) + clonality (McGranahan) | Beyond raw TMB |
| Cross-panel comparison | Vega 2021 calibration equations OR WES re-projection | Direct comparison invalid |

## Standard Workflow

**Goal:** Compute TMB from a VEP-annotated somatic VCF with full filtering.

**Approach:** Parse cyvcf2; apply VAF + depth + germline (gnomAD) filters; count nonsynonymous coding consequences; divide by scored Mb.

```python
from cyvcf2 import VCF
import re

NONSYNONYMOUS_CONSEQUENCES = {
    'missense_variant', 'stop_gained', 'stop_lost', 'start_lost', 'start_retained',
    'frameshift_variant', 'inframe_insertion', 'inframe_deletion',
    'splice_donor_variant', 'splice_acceptor_variant',
    'protein_altering_variant', 'initiator_codon_variant'
}

# Vega 2021-calibrated scored regions (Mb)
PANEL_SCORED_REGION = {
    'FoundationOne_CDx': 0.8,           # Scored region; NOT 1.1 panel total
    'MSK_IMPACT_v3': 0.98,
    'MSK_IMPACT_v4': 1.22,
    'TSO500': 1.3,                       # Scored from 1.94 total
    'Oncomine_TML': 1.2,
    'Caris_MI': 1.2,
    'Tempus_xT_v3': 0.6,                 # Borderline reliability
    'WES': 30.0,
    'WGS': 3000.0
}

# TMB2 (Ramos-Paradas 2021) equivalent thresholds for FDA 10/Mb FoundationOne sensitivity
ASSAY_TMB_H_CUTOFF = {
    'FoundationOne_CDx': 10.0,
    'TSO500': 7.8,
    'Oncomine_TML': 8.4,
    'MSK_IMPACT_v3': 10.0,  # Approximate; full Vega 2021 calibration recommended
    'MSK_IMPACT_v4': 10.0,
    'WES': 10.0
}


def parse_consequences_from_vep(csq_field, csq_header):
    '''Parse VEP CSQ INFO field; returns list of per-transcript consequence types.'''
    if not csq_field:
        return []
    cons_idx = csq_header.index('Consequence')
    out = []
    for transcript in csq_field.split(','):
        fields = transcript.split('|')
        if len(fields) > cons_idx:
            out.append(fields[cons_idx])
    return out


def is_nonsynonymous(consequences, include_synonymous=False):
    '''Check if variant has nonsynonymous coding consequence.

    FoundationOne CDx convention INCLUDES synonymous (set include_synonymous=True).
    MSK-IMPACT and most academic pipelines exclude.
    '''
    target = set(NONSYNONYMOUS_CONSEQUENCES)
    if include_synonymous:
        target.add('synonymous_variant')
    for cons_str in consequences:
        for cons in cons_str.split('&'):
            if cons in target:
                return True
    return False


def calculate_tmb(vcf_path, scored_region_mb, csq_header,
                   min_vaf=0.05, min_depth=100, max_gnomad_af=0.005,
                   include_synonymous=False, exclude_hotspots=True,
                   hotspot_bed=None):
    '''Calculate TMB with filtering per Vega 2021 harmonization.

    Args:
        scored_region_mb: panel's SCORED region (NOT total panel)
        min_vaf: 0.05 (FoundationOne) to 0.10 (tumor-only no UMI)
        max_gnomad_af: 0.005 (0.5%) typical for tumor-only germline filter
        include_synonymous: True for FoundationOne CDx-compatible; False for MSK-IMPACT
        exclude_hotspots: COSMIC drivers excluded (not random mutations)
    '''
    vcf = VCF(vcf_path)
    cons_idx = csq_header.index('Consequence') if 'Consequence' in csq_header else 1
    nonsyn_count = 0
    total_pass = 0

    for v in vcf:
        if v.FILTER is not None:  # FILTER == None means PASS in cyvcf2
            continue
        depth = v.INFO.get('DP', 0)
        if depth < min_depth:
            continue
        vaf = _get_vaf(v)
        if vaf is None or vaf < min_vaf:
            continue
        gnomad_af = v.INFO.get('gnomAD_AF', 0) or v.INFO.get('AF_popmax', 0) or 0
        if gnomad_af > max_gnomad_af:
            continue
        total_pass += 1

        csq = v.INFO.get('CSQ', '')
        consequences = parse_consequences_from_vep(csq, csq_header)
        if is_nonsynonymous(consequences, include_synonymous=include_synonymous):
            nonsyn_count += 1

    tmb = nonsyn_count / scored_region_mb
    return {
        'tmb': round(tmb, 2),
        'nonsynonymous_count': nonsyn_count,
        'total_passing_filters': total_pass,
        'scored_region_mb': scored_region_mb
    }


def _get_vaf(variant):
    '''Extract VAF from genotype FORMAT fields (Mutect2 AD or AF).'''
    try:
        ad = variant.format('AD')
        if ad is not None and len(ad) > 0:
            ad0 = ad[0]
            total = sum(ad0)
            return ad0[1] / total if total > 0 else None
    except Exception:
        pass
    try:
        af = variant.format('AF')
        if af is not None and len(af) > 0:
            return float(af[0])
    except Exception:
        pass
    return None


def classify_tmb(tmb_value, assay='FoundationOne_CDx'):
    '''Apply ESMO 2024 / FDA pembrolizumab cutoff with Vega 2021 calibration per assay.'''
    cutoff = ASSAY_TMB_H_CUTOFF.get(assay, 10.0)
    if tmb_value >= 500:
        category = 'Ultra-hypermutator (>=500/Mb; POLE+MMR likely)'
    elif tmb_value >= 100:
        category = 'Hypermutator (>=100/Mb; MMR-D or POLE)'
    elif tmb_value >= cutoff:
        category = f'TMB-H (>= {cutoff}/Mb {assay}-calibrated; pan-tumor ICI eligible per FDA 2020)'
    else:
        category = 'TMB-low'
    return category
```

## TMB-MSI Concordance and Reconciliation

**Goal:** When MSI-H is present, TMB-H adds no information (Sha 2020).

```python
def tmb_msi_reconcile(tmb_value, msi_status, tumor_type=None):
    '''Reconcile TMB + MSI for ICI decision.'''
    tmb_high = tmb_value >= 10
    msi_high = msi_status == 'MSI-H'

    if msi_high:
        return ('ICI eligible by MSI-H (FDA 2017 pembrolizumab); TMB-H adds no information '
                '(Sha 2020 Cancer Discov).')
    if tmb_high and tumor_type in ('breast', 'prostate', 'glioma'):
        return ('TMB-H present but does not enrich ICI response in this tumor type (McGrail 2021). '
                'Tumor-specific cutoffs recommended.')
    if tmb_high:
        return ('TMB-H pan-tumor; ICI eligible (FDA pembrolizumab 2020). '
                'Confirm baseline CD8 infiltrate; check HLA-LOH (McGranahan 2017 LOHHLA).')
    return 'TMB-low; MSS. Standard-of-care chemo.'
```

## Per-Operation Failure Modes

**1. Using panel total size as denominator (NOT scored region)**
- Trigger: Compute TMB = nonsynonymous count / 1.1 Mb for FoundationOne.
- Mechanism: FoundationOne CDx total panel is 1.1 Mb; SCORED region (counted for TMB denominator) is 0.8 Mb.
- Symptom: TMB underestimated by ~37%.
- Fix: Use 0.8 Mb for FoundationOne CDx scored region per Vega 2021.

**2. Cross-panel comparison without calibration**
- Trigger: TSO500 reports TMB = 9.5; compared to FoundationOne 10/Mb cutoff.
- Mechanism: the TMB2 project (Ramos-Paradas 2021) showed the equivalent threshold is 7.8/Mb on TSO500 (not 10/Mb).
- Symptom: TSO500 TMB-H called positive at incorrect threshold.
- Fix: Apply assay-specific calibration; the TSO500 equivalent cutoff = 7.8/Mb (Ramos-Paradas 2021).

**3. FoundationOne synonymous mis-handling**
- Trigger: Compare academic pipeline (no synonymous) to FoundationOne reference (synonymous included).
- Mechanism: FoundationOne CDx counts synonymous; MSK-IMPACT and most academic pipelines exclude.
- Symptom: Academic pipeline TMB systematically lower than FoundationOne by ~10-20%.
- Fix: Match the counting convention to the comparison reference; document explicitly.

**4. Tumor-only TMB inflated**
- Trigger: Tumor-only WES with naive germline filter (gnomAD AF > 1%).
- Mechanism: Population-specific common variants leak through if gnomAD AF threshold not stratified by ancestry.
- Symptom: AFR/EAS patient TMB inflated 1.5-3x; misclassified as TMB-H.
- Fix: Stratify gnomAD AF by patient ancestry; use grpmax FAF95; threshold <= 0.5%.

**5. bTMB applied without ctDNA shed check**
- Trigger: Report bTMB low in a metastatic patient.
- Mechanism: Low ctDNA shed fraction produces false-negative bTMB (BFAST Cohort C failure mechanism).
- Symptom: Patient with high tissue TMB labeled bTMB-low; ICI not offered.
- Fix: Check tumor fraction (e.g., ichorCNA, MAF of known driver) before trusting bTMB-low; consider tissue TMB.

**6. TMB-H applied to breast / prostate / glioma**
- Trigger: ICI prescribed for TMB-H breast cancer based on pan-tumor approval.
- Mechanism: McGrail 2021 demonstrated TMB fails to enrich for ICI response in breast, prostate, glioma.
- Symptom: ICI offered with low expectation of benefit; patient bears unnecessary toxicity.
- Fix: Apply tumor-type-specific cutoffs (Samstein 2019); document the McGrail 2021 tumor-type caveat in report.

**7. Hotspots inflating TMB**
- Trigger: Include BRAF V600E and KRAS G12C in TMB count.
- Mechanism: Driver hotspots are non-random; including biases TMB upward in driver-mutated samples.
- Symptom: TMB inflated in samples with strong drivers.
- Fix: Exclude COSMIC-confirmed hotspots (provide hotspot BED).

**8. MSI-H -> add TMB-H -> additive ICI confidence**
- Trigger: Report TMB-H as additional support for ICI in MSI-H patient.
- Mechanism: MSI-H is uniformly hypermutator + uniformly ICI-responsive; adding TMB-H is statistical tautology (Sha 2020).
- Symptom: Reviewer flag.
- Fix: Report MSI-H + TMB-H concurrence but explicitly note TMB-H is NOT additive given MSI-H.

**9. Ignoring HLA-LOH**
- Trigger: TMB-H + neoantigen prediction without LOH check.
- Mechanism: HLA-LOH abolishes neoantigen presentation for lost allele in ~17% pan-cancer (>30% HNSCC / NSCLC / cervical).
- Symptom: Apparent neoantigen burden inflated.
- Fix: Run LOHHLA (McGranahan 2017) or DASH (Pyke 2022); flag HLA-LOH-positive tumors.

## Reconciliation: When Sources Disagree

| Pattern | Likely cause | Action |
|---------|-------------|--------|
| Vendor TMB vs WES TMB differ 2-3x | Panel-specific scored region + counting convention | Apply Vega 2021 calibration |
| FoundationOne vs MSK-IMPACT same sample differ | Synonymous handling differs | Document both; cite Vega 2021 |
| Tissue TMB vs bTMB differ | ctDNA shed fraction low; tumor heterogeneity | Trust tissue; check ctDNA fraction for bTMB confidence |
| TMB-H + MSI-H | Expected concurrence | MSI-H is the primary biomarker; TMB-H not additive |
| TMB-H + clinical PD-L1-negative | Independent biomarkers | Report both; ICI eligibility still per TMB-H pan-tumor |
| Patient with TMB-H but PR rate low | Tumor-type-specific cutoff; HLA-LOH | Apply Samstein 2019 cancer-specific cutoff; check HLA-LOH |
| POLE-exo + MMR-D | Ultra-hypermutator | ICI excellent response expected |

## Quantitative Thresholds and Conventions

| Threshold | Convention | Source |
|-----------|-----------|--------|
| FDA pembrolizumab pan-tumor | TMB-H >= 10 mut/Mb on FoundationOne CDx | FDA 2020 |
| TSO500 equivalent cutoff | 7.8 mut/Mb | Ramos-Paradas 2021 |
| Oncomine TML equivalent cutoff | 8.4 mut/Mb | Ramos-Paradas 2021 |
| Hypermutator | >= 100 mut/Mb | Research convention |
| Ultra-hypermutator | >= 500 mut/Mb | POLE+MMR; ICI excellent |
| MSI-H typical TMB | 30-50 mut/Mb | Research convention |
| MSI-H + TMB-H overlap | ~83% MSI-H are TMB-H; ~16% TMB-H are MSI-H | Chalmers 2017 *Genome Med* 9:34 |
| Tumor purity floor | FoundationOne >=20%; MSK-IMPACT >=30% | Vendor documentation |
| Min VAF | FoundationOne 5%; tumor-only no UMI 10% | Vendor documentation |
| Tumor-only germline filter | gnomAD AF <=0.5% (sometimes 1%) | Convention |
| Panel size minimum | >= 0.8 Mb workable; >= 1.0 Mb preferred; < 0.5 Mb unreliable | Vega 2021 |
| HLA-LOH frequency | ~17% pan-cancer; >30% HNSCC / NSCLC / cervical | Montesion 2021 |

## Common Errors

| Symptom | Cause | Solution |
|---------|-------|----------|
| TMB much lower than FoundationOne report | Used panel total (1.1) instead of scored (0.8) | Use 0.8 Mb for FoundationOne |
| Academic TMB systematically lower | Excluded synonymous; FoundationOne includes | Match counting convention |
| AFR / EAS tumor-only TMB inflated | gnomAD AF filter EUR-only | Use grpmax FAF95; stratify by patient ancestry |
| bTMB negative but tissue positive | Low ctDNA shed | Use tissue TMB; check fraction |
| TMB-H in breast cancer with poor response | McGrail 2021 tumor-type limitation | Use tumor-type-specific cutoff |
| MSI-H + TMB-H reported as additive | Tautology | MSI-H is primary biomarker |
| POLE-exo + low TMB | Tumor sequencing artifact OR low tumor purity | Check VAF distribution; re-call if purity low |
| Variant counting differs across replicates | Random VAF sampling at borderline thresholds | Set explicit VAF floor + replicate-stable filter |

## Anticipated Reviewer Pushback

| Pushback | Standard response |
|----------|-------------------|
| "Why panel-specific cutoffs?" | Vega 2021 demonstrated panel variance; the FoundationOne 10/Mb = TSO500 7.8 = Oncomine 8.4 equivalences are from the TMB2 project (Ramos-Paradas 2021). Universal 10/Mb is wrong across non-F1 platforms. |
| "TMB-H is supposed to be tumor-agnostic" | FDA pan-tumor approval based on KEYNOTE-158; ESMO 2024 retained it tumour-agnostic. McGrail 2021 + Samstein 2019 demonstrate tumor-type-specific limits. |
| "Synonymous variants?" | FoundationOne CDx counts synonymous; academic pipelines exclude. We document the counting convention and apply Vega 2021 calibration. |
| "Why exclude hotspots?" | Driver hotspots are non-random; including biases TMB upward in driver-mutated samples vs cohort comparator. |
| "Tumor-only TMB unreliable" | Acknowledged; we apply stringent gnomAD grpmax FAF95 filtering stratified by patient ancestry; report paired-normal-validated subset separately. |
| "Why HLA-LOH integration?" | McGranahan 2017 (LOHHLA) + Montesion 2021 show ~17% pan-cancer (>30% HNSCC / NSCLC / cervical) lose HLA via LOH; apparent neoantigen burden over-estimated without LOH check. |
| "bTMB?" | BFAST Cohort C failed primary endpoint (Peters 2022); bTMB is research-grade in tissue-naive only; we use tissue TMB as regulatory standard. |
| "Why ultra-hypermutator distinction?" | POLE+MMR (>=500 mut/Mb) shows superior ICI response per multiple case series; mechanistically distinct from MMR-D alone. |

## References

- Marabelle A et al. 2020. Association of TMB with efficacy of pembrolizumab in advanced solid tumours from the phase 2 KEYNOTE-158 study. *Lancet Oncol* 21:1353.
- Merino DM et al. 2020. Establishing guidelines to harmonize tumor mutational burden (TMB). *J Immunother Cancer* 8:e000147. (FoC Phase I)
- Vega DM et al. 2021. Aligning tumor mutational burden (TMB) quantification across diagnostic platforms: phase II of the Friends of Cancer Research TMB Harmonization Project. *Ann Oncol* 32:1626.
- Mosele MF et al. 2024. Recommendations for the use of next-generation sequencing for patients with advanced cancer in 2024. *Ann Oncol* 35:588. (ESMO 2024)
- McGrail DJ et al. 2021. High tumor mutation burden fails to predict immune checkpoint blockade response across all cancer types. *Ann Oncol* 32:661.
- Sha D et al. 2020. Tumor mutational burden as a predictive biomarker in solid tumors. *Cancer Discov* 10:1808.
- Ramos-Paradas J et al. 2021. Tumor mutational burden assessment in non-small-cell lung cancer samples: results from the TMB2 harmonization project comparing three NGS panels. *J Immunother Cancer* 9:e001904.
- Samstein RM et al. 2019. TMB and survival after immunotherapy across cancer types. *Nat Genet* 51:202.
- Chalmers ZR et al. 2017. Analysis of 100,000 human cancer genomes reveals the landscape of TMB. *Genome Med* 9:34.
- Yarchoan M et al. 2017. Tumor mutational burden and response rate to PD-1 inhibition. *NEJM* 377:2500.
- Gandara DR et al. 2018. Blood-based TMB as a predictor of response to atezolizumab in NSCLC. *Nat Med* 24:1441.
- Peters S et al. 2022. Atezolizumab versus chemotherapy in advanced or metastatic NSCLC with high blood-based tumor mutational burden: BFAST Cohort C. *Nat Med* 28:1831.
- Salem ME et al. 2018. Landscape of tumor mutation load, mismatch repair deficiency, and PD-L1 expression in a large patient cohort of gastrointestinal cancers. *Mol Cancer Res* 16:805.
- Luksza M et al. 2017. A neoantigen fitness model predicts tumour response to checkpoint blockade immunotherapy. *Nature* 551:517.
- Luksza M et al. 2022. Neoantigen quality predicts immunoediting in survivors of pancreatic cancer. *Nature* 606:389.
- McGranahan N et al. 2016. Clonal neoantigens elicit T cell immunoreactivity and sensitivity to immune checkpoint blockade. *Science* 351:1463.
- McGranahan N et al. 2017. Allele-specific HLA loss and immune escape in lung cancer evolution. *Cell* 171:1259. (LOHHLA)
- Montesion M et al. 2021. Somatic HLA class I loss is a widespread mechanism of immune evasion which refines the use of TMB as a biomarker. *Cancer Discov* 11:282.
- Pyke RM et al. 2022. A machine learning algorithm with subclonal sensitivity reveals widespread pan-cancer HLA loss of heterozygosity. *Nat Commun* 13:1925. (DASH)
- Friends of Cancer Research TMB harmonization resources: `https://friendsofcancerresearch.org/tmb/`

## Related Skills

- clinical-databases/somatic-signatures - Mutational signatures including HRD (PARP) and MMR-D (ICI)
- clinical-databases/msi-detection - MSI-H is the related ICI biomarker
- clinical-databases/hla-typing - HLA typing for neoantigen prediction and LOH
- variant-calling/variant-calling - Mutect2 / Strelka2 somatic upstream
- variant-calling/clinical-interpretation - ACMG / AMP cancer framework
<!-- END FILE: clinical-databases/tumor-mutational-burden/SKILL.md -->

## 子目录：clinical-databases/variant-prioritization

<!-- BEGIN FILE: clinical-databases/variant-prioritization/SKILL.md -->
---
name: bio-clinical-databases-variant-prioritization
description: Prioritizes rare-disease variants from trio/quad WES/WGS with de novo (DeNovoGear, Triodenovo), compound-heterozygous phasing (WhatsHap), mosaic VAF tiering, phenotype-driven ranking (Exomiser, Phen2Gene, AMELIE), ClinGen gene-disease validity gating, and ACMG SF v3.2 secondary findings reporting. Use when running diagnostic exome / genome pipelines, identifying candidate Mendelian disease genes, screening for incidental findings, or auditing VUS reclassification cycles. The ACMG/AMP classification framework (PVS1 decision tree, Pejaver PP3/BP4 calibration, Tavtigian point system) is in clinical-databases/acmg-classification.
tool_type: python
primary_tool: pandas
---

## Version Compatibility

Reference examples tested with: pandas 2.2+, cyvcf2 0.30+, pyhgvs 0.12+, Exomiser 14.0+ (Smedley 2015), Phen2Gene 1.2+ (Zhao 2020), DeNovoGear 1.1.1+ (Ramu 2013), WhatsHap 2.0+ (Patterson 2015), HPO 2024+ (Human Phenotype Ontology). ACMG Secondary Findings list is v3.2 (Miller 2023): 81 genes.

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `<tool> --version`

If code throws ImportError, AttributeError, or TypeError, introspect the installed package and adapt the example to match the actual API rather than retrying. Phenotype-driven prioritization REQUIRES high-quality HPO terms; without rich phenotypic input Exomiser/AMELIE degrade significantly.

# Rare-Disease Variant Prioritization Pipeline

**'Prioritize candidate disease-causing variants from this trio exome'** -> Filter to rare + functional + inheritance-consistent variants; rank by phenotype concordance; flag ACMG SF v3.2 incidental findings; report tiers with classification logic deferred to `acmg-classification`.

- Python (filtering pipeline): pandas + cyvcf2 + myvariant.info aggregation
- CLI (phenotype-driven ranking): `exomiser --analysis hiPHIVE-prioritised.yml`
- Python (de novo calling): DeNovoGear / Triodenovo / PossibleDeNovo
- CLI (compound het phasing): `whatshap phase --indels` for singletons; trio-based for families
- Python (HPO concordance): Phen2Gene / AMELIE / Phenolyzer
- VCEP curations: `https://cspec.genome.network/cspec/ui/svi/all`

## Pipeline Architecture: The Standard Rare-Disease Funnel

Typical trio exome enters as 40,000-100,000 variants per individual; reaches diagnostic candidate list of 1-10 variants through cascading filters:

| Stage | Filter | Variant count (typical trio) |
|-------|--------|------------------------------|
| Raw joint-called | -- | 100k-150k |
| QC filter (PASS, depth, GQ, missingness) | GATK best practices + Hail QC | 80k-120k |
| Population frequency | gnomAD grpmax_faf95 < 0.0001 (or disease-specific Whiffin max-credible-AF) | 5k-15k |
| Functional consequence | Coding / splice / regulatory | 1k-3k |
| Inheritance pattern | de novo / AR-hom / AR-compoundhet / X-linked / mosaic | 50-500 |
| Phenotype concordance | Exomiser hiPHIVE / Phen2Gene / AMELIE score | 5-50 |
| ACMG classification | Defer to `acmg-classification` | 1-10 |
| ACMG SF v3.2 cross-check | Miller 2023 (81 genes) | Separate output |

## Inheritance-Based Filtering

| Pattern | Filter |
|---------|--------|
| **De novo (DNV)** | Variant in proband, absent in both parents; needs trio | Apply DeNovoGear / Triodenovo / GATK PossibleDeNovo; visual IGV inspection (~10-30% false-positive rate without) |
| **Autosomal recessive; homozygous** | Hom-alt in proband; het in both parents | gnomAD grpmax_faf95 < 0.005 recessive threshold (Whiffin formula) |
| **Autosomal recessive; compound het** | Two het variants in same gene on opposite alleles | Trio-phased OR read-based phasing via WhatsHap (works within ~500 bp; longer needs parents or long-read) |
| **X-linked recessive** | Male proband hemizygous; carrier mother het | chrX coords; check Klinefelter / mosaic XXY |
| **X-linked dominant** | Het in affected; consider XCI skewing in females | Report XCI status if relevant |
| **Mitochondrial heteroplasmy** | mtDNA variant present at varying heteroplasmy across tissues | Use MITOMAP + HmtVar; ACMG criteria do not apply directly |
| **Mosaic** | Sub-clonal VAF in proband; absent in inherited transmissions | VAF 5-30% suggestive; tissue-dependent (blood vs buccal vs affected tissue) |

## De Novo Calling: Trio Analysis

**Goal:** Identify variants present in proband but absent in both parents with high specificity.

**Approach:** Use specialized DNV callers; supplement with manual IGV inspection.

| Tool | Approach | Use case |
|------|----------|----------|
| **DeNovoGear** (Ramu 2013 *Nat Methods*) | Bayesian, considers parent-of-origin | Standard for trio WES |
| **Triodenovo** (Wei 2015) | Bayesian + family-aware | Alternative |
| **GATK PossibleDeNovo annotation** | Hard filter | Quick prefilter; not standalone |
| **DeNovoCNN** (2022) | Deep learning trio caller | Most accurate as of 2022-2026 |

**False-DNV rate:** ~10-30% without manual IGV inspection; concentrated in:
- Tandem repeat regions (DNM rate inflated)
- Heterozygous parent with low coverage
- Mosaic parents (parental mosaicism transmitted to >1 offspring)
- Mapping errors in segmental duplications

## Phenotype-Driven Prioritization

| Tool | Approach | Performance (typical benchmark) | Fails when |
|------|----------|--------------------------------|-----------|
| **Exomiser** (Smedley 2015 *Nat Protoc*) | hiPHIVE: phenotype + interactome + sequence damage | 74% top-1; 94% top-5 (Cipriani 2020) | Sparse HPO (< 5 specific terms); novel-disease gene |
| **Phen2Gene** (Zhao 2020 *NARGAB*) | HPO-to-gene mapping; faster than Exomiser | Similar top-5 | Phenotype-only filtering insufficient |
| **AMELIE** (Birgmeier 2020 *Sci Transl Med*) | Literature-mining + phenotype | Best when literature is rich | New / rare disease without literature; specific patient HPO unmatched |
| **Phenolyzer** (Yang 2015 *Nat Methods*) | Phenotype-based gene scoring | Legacy | Modern multi-feature tools (Exomiser, AMELIE) preferred |
| **GADO** (Deelen 2019 *Nat Commun*) | Gene Network-based; HPO-free option | When HPO is sparse | Phenotype-rich cases where Exomiser hiPHIVE wins |
| **CADA** (Peng 2021) | Cross-species gene prioritization | Animal model integration | Genes without orthologs; rare-disease without animal model |

**Critical requirement:** all phenotype-driven tools degrade significantly with sparse HPO terms. Capture 5-10 specific HPO terms; avoid generic "intellectual disability" alone.

## ClinGen Gene-Disease Validity: Mandatory Gating

Strande et al. 2017 *AJHG* + ClinGen ongoing curation: **Limited / Moderate / Strong / Definitive** evidence per gene-disease pair.

| Category | When to apply |
|----------|---------------|
| **Definitive** | Strong literature evidence + functional / population genetic evidence | Apply full ACMG framework |
| **Strong** | -- | Apply full framework |
| **Moderate** | -- | Apply framework but flag |
| **Limited** | Single case report or weak segregation | Treat candidate cautiously; PP2 / BP1 should not apply |
| **Disputed** | Contradicting evidence | Do not call pathogenic without VCEP curation |
| **No Known Disease Relationship** | Gene not associated with the queried disease | Do not call |

**Many commercial panels include genes with only Limited validity.** ClinGen-curated `https://search.clinicalgenome.org/kb/gene-validity` is the authoritative directory.

## ACMG Secondary Findings v3.2 (Miller 2023 *Genet Med* 25:100866)

81 genes for opt-in/opt-out reporting on clinical exome/genome. Growth: 56 -> 59 -> 73 -> 78 -> 81. **v3.2 additions: CALM1, CALM2, CALM3** (calmodulinopathy; long QT / CPVT; high actionability via beta-blockade + ICD).

Inclusion criteria: ClinGen Strong or Definitive gene-disease validity + ClinGen ADWG actionability scoring.

```python
ACMG_SF_V3_2_GENES = [
    # Cardiomyopathies
    'ACTA2', 'ACTC1', 'BAG3', 'COL3A1', 'DES', 'FBN1', 'FLNC', 'GLA', 'LMNA', 'MYBPC3',
    'MYH11', 'MYH7', 'MYL2', 'MYL3', 'PRKAG2', 'PKP2', 'RBM20', 'SCN5A', 'SMAD3',
    'TGFBR1', 'TGFBR2', 'TMEM43', 'TNNC1', 'TNNI3', 'TNNT2', 'TPM1', 'TTN',
    # CALM v3.2 additions (calmodulinopathies)
    'CALM1', 'CALM2', 'CALM3',
    # Arrhythmias and channelopathies
    'CACNA1S', 'KCNH2', 'KCNQ1', 'RYR1', 'RYR2',
    # Vascular
    'ACVRL1', 'ENG',
    # Cancer predisposition
    'APC', 'ATM', 'BAP1', 'BMPR1A', 'BRCA1', 'BRCA2', 'BRIP1', 'CDH1', 'CDKN2A',
    'CHEK2', 'GREM1', 'HOXB13', 'MAX', 'MEN1', 'MLH1', 'MSH2', 'MSH6', 'MUTYH',
    'NF2', 'PALB2', 'PMS2', 'PTEN', 'RAD51C', 'RAD51D', 'RB1', 'RET', 'SDHAF2',
    'SDHB', 'SDHC', 'SDHD', 'SMAD4', 'STK11', 'TMEM127', 'TP53', 'TSC1', 'TSC2',
    'VHL', 'WT1',
    # Other
    'FH', 'GAA', 'HFE', 'HNF1A', 'LDLR', 'OTC', 'PCSK9', 'TTR'
]
# Note: above list is illustrative; pin to Miller 2023 supplement for exact set.
```

## Decision Tree by Scenario

| Scenario | Recommended path | Why |
|----------|------------------|-----|
| Trio WES, suspected Mendelian | Full pipeline with DeNovoGear + Exomiser + HPO | Standard rare-disease workflow |
| Singleton WES | WhatsHap read-based phasing + AR-hom + AR-compoundhet candidates | Compound het hard without trio |
| Suspected mosaic | Lower VAF threshold (2-30%); deep coverage (>200x) | Standard tools miss mosaic |
| Long-read genome | Add SV calling + STR repeat expansion | SVs miss in short-read |
| Newborn screening (BabyScreen+) | 605-gene Mendelian panel with current ACMG SF v3.2 | Lunke 2025 *Nat Med* 31:4236 |
| Cancer predisposition | ClinGen Hereditary Cancer VCEPs + ACMG SF cancer subset | Use VCEP CSpec |
| Cardiomyopathy / arrhythmia | ClinGen HCM / DCM / LQT VCEPs | Strict gene-disease validity |
| Population screening | ACMG SF v3.2 (81 genes) opt-in/opt-out | Miller 2023 |

## Standard Pipeline Workflow

**Goal:** From a trio joint-called VCF, output ranked candidate variants with inheritance pattern, phenotype concordance, and ACMG SF flags.

**Approach:** Cascading filters with QC, population frequency, functional consequence, inheritance, phenotype.

```python
from cyvcf2 import VCF
import pandas as pd
from pathlib import Path

# Quality + population frequency filter (apply first)
def filter_qc_and_frequency(vcf_path, max_grpmax_faf95=0.0001, min_dp=10, min_gq=20):
    '''Stage 1: QC + frequency filter. Reduces 100k -> ~5-15k variants.'''
    vcf = VCF(vcf_path)
    samples = vcf.samples  # e.g., [proband, mother, father]
    rows = []
    for v in vcf:
        if v.FILTER is not None:
            continue
        if min(v.gt_depths) < min_dp:
            continue
        if v.QUAL is not None and v.QUAL < min_gq:
            continue
        gnomad = (v.INFO.get('grpmax_faf95') or v.INFO.get('AF_grpmax') or
                  v.INFO.get('AF_popmax') or 0)
        if gnomad > max_grpmax_faf95:
            continue
        rows.append({
            'chrom': v.CHROM, 'pos': v.POS, 'ref': v.REF, 'alt': v.ALT[0],
            'genotypes': dict(zip(samples, v.gt_types.tolist())),
            'depth': dict(zip(samples, v.gt_depths.tolist())),
            'gnomad_faf95': gnomad,
            'consequence': v.INFO.get('CSQ', '').split('|')[1] if v.INFO.get('CSQ') else None
        })
    return pd.DataFrame(rows)


def call_de_novo(df, proband, mother, father):
    '''Stage 2: identify DNV candidates: hom-ref both parents, het/hom-alt proband.

    Implements Mendelian-violation logic; supplement with DeNovoGear or DeNovoCNN
    for production (this implementation has 10-30% false-positive rate without IGV).
    '''
    is_dnv = []
    for _, row in df.iterrows():
        gts = row['genotypes']
        if gts[mother] == 0 and gts[father] == 0 and gts[proband] in (1, 3):
            # Mother hom-ref AND father hom-ref AND proband het OR hom-alt
            # Confidence boost: depth at parent sites should be >= 10 to trust hom-ref
            if row['depth'][mother] >= 10 and row['depth'][father] >= 10:
                is_dnv.append(True)
                continue
        is_dnv.append(False)
    df['is_de_novo_candidate'] = is_dnv
    return df


def call_compound_het(df, proband, mother, father, gene_col='gene'):
    '''Stage 3: identify compound het: two het variants in same gene, one from each parent.

    Trio phasing is gold standard; singletons require WhatsHap read-based phasing.
    '''
    het_in_proband = df[df['genotypes'].apply(lambda gts: gts[proband] == 1)]
    candidate_genes = []
    for gene in het_in_proband[gene_col].unique():
        if pd.isna(gene):
            continue
        gene_variants = het_in_proband[het_in_proband[gene_col] == gene]
        # Need >= 2 variants; one inherited from each parent
        maternal_het = gene_variants[gene_variants['genotypes'].apply(
            lambda gts: gts[mother] == 1 and gts[father] == 0)]
        paternal_het = gene_variants[gene_variants['genotypes'].apply(
            lambda gts: gts[father] == 1 and gts[mother] == 0)]
        if len(maternal_het) >= 1 and len(paternal_het) >= 1:
            candidate_genes.append(gene)
    df['is_compound_het_candidate'] = df[gene_col].isin(candidate_genes)
    return df


def flag_acmg_sf(df, acmg_sf_genes, gene_col='gene', clnsig_col='clinvar_sig'):
    '''Stage: flag ACMG Secondary Findings (Miller 2023 v3.2; 81 genes).

    Only P/LP variants in SF genes are reportable as secondary findings.
    '''
    df['is_acmg_sf_candidate'] = (
        df[gene_col].isin(acmg_sf_genes) &
        df[clnsig_col].astype(str).str.contains('athogenic', na=False)
    )
    return df


def filter_by_clingen_validity(df, validity_table, gene_col='gene',
                                min_validity='Moderate'):
    '''Gate on ClinGen gene-disease validity. Limited or Disputed -> low confidence.

    validity_table: DataFrame from `https://search.clinicalgenome.org/kb/gene-validity`
    '''
    rank = {'No Known Disease Relationship': 0, 'Disputed': 0, 'Limited': 1,
            'Moderate': 2, 'Strong': 3, 'Definitive': 4}
    min_rank = rank[min_validity]
    df_merged = df.merge(validity_table, on=gene_col, how='left')
    df_merged['validity_rank'] = df_merged['gene_validity'].map(rank).fillna(0)
    df_merged['pass_validity'] = df_merged['validity_rank'] >= min_rank
    return df_merged


def phenotype_score_with_exomiser_yml(yml_path, vcf_path, hpo_terms, output_dir):
    '''Emit Exomiser command for phenotype-driven ranking.

    HPO terms (e.g., HP:0001250 for seizures) must be SPECIFIC.
    Sparse generic HPO degrades Exomiser hiPHIVE accuracy significantly.
    '''
    return (f'java -jar exomiser-cli-14.0.0.jar --analysis {yml_path} '
            f'--vcf {vcf_path} --hpo {",".join(hpo_terms)} '
            f'--output-dir {output_dir}')
```

## Per-Operation Failure Modes

**1. De novo with false-positive rate 10-30%**
- Trigger: Report DNV candidates from Mendelian-violation analysis without IGV inspection.
- Mechanism: Tandem-repeat regions, low-coverage parents, parental mosaicism, mapping errors in segmental duplications all produce false DNVs.
- Symptom: 10-30% of reported DNVs are artifacts.
- Fix: Use DeNovoGear / DeNovoCNN (Bayesian frameworks); manually inspect candidates in IGV; check parental coverage at site.

**2. Compound het without phasing**
- Trigger: Report two hets in same gene as compound het without confirming phase.
- Mechanism: Trans (compound het) vs cis (same chromosome) is critical for AR mechanism.
- Symptom: False-positive compound het when both variants are in cis.
- Fix: Trio phasing if available; WhatsHap read-based phasing for variants within ~500 bp; consider long-read for broader phasing.

**3. Limited-validity gene reported as diagnostic**
- Trigger: Gene appears on commercial panel; variant labeled disease-causing.
- Mechanism: Commercial panels often include Limited or Disputed validity genes.
- Symptom: False-positive diagnostic report.
- Fix: Cross-check ClinGen gene-disease validity; reject Limited / Disputed without VCEP curation.

**4. Sparse HPO terms degrading Exomiser**
- Trigger: Submit Exomiser with single generic HPO (e.g., HP:0001250 "Seizure" only).
- Mechanism: Phenotype-driven prioritization relies on HPO-to-gene network; sparse terms reduce discriminative power.
- Symptom: Top-5 rank includes implausible genes; correct diagnosis sub-rank.
- Fix: Capture 5-10 specific HPO terms (e.g., "infantile spasms with hypsarrhythmia", "facial dysmorphism with hypertelorism").

**5. ACMG SF v3.1 used instead of v3.2**
- Trigger: Pipeline reports SF based on 78-gene v3.1 list; misses CALM1/2/3 calmodulinopathies.
- Mechanism: v3.2 (Miller 2023) added CALM1, CALM2, CALM3.
- Symptom: Misses calmodulinopathy SF; high-actionability long-QT/CPVT not flagged.
- Fix: Use Miller 2023 v3.2 list (81 genes); re-run prior cohorts.

**6. Mosaic variants below standard VAF threshold**
- Trigger: Filter at VAF >= 30% on standard pipeline.
- Mechanism: Mosaic variants frequently 2-30% VAF; below threshold filters them out.
- Symptom: Mosaic disease missed (e.g., Proteus syndrome PIK3CA, McCune-Albright GNAS).
- Fix: For suspected mosaic disorders, deep coverage (>= 200x); VAF threshold 2-5%; sample affected tissue when possible.

**7. ClinVar P variant in Limited-validity gene**
- Trigger: Variant labeled P in ClinVar; gene-disease validity is Limited.
- Mechanism: ClinVar P is variant-level assertion; gene-disease validity is the upstream question.
- Symptom: Reported P variant in non-disease-associated gene.
- Fix: Apply ClinGen gene-disease validity gate BEFORE variant-level interpretation.

**8. VUS reclassification gaps**
- Trigger: VUS labeled 2017 still in active diagnostic report 2025.
- Mechanism: VUS are reclassified as evidence accrues in actively-curated genes; a one-time classification has an expiry date.
- Symptom: Stale classifications drive incorrect clinical decisions.
- Fix: Annual VUS re-review for active diagnostic variants; tools like Genome Alert! (Yauy 2022) automate detection of monthly ClinVar changes.

**9. Inheritance pattern assumed wrong**
- Trigger: Assume AD inheritance for a gene with variable expressivity / incomplete penetrance.
- Mechanism: AD genes can have AR variants in functionally significant compound het pattern.
- Symptom: Miss AR mechanism in mostly-AD gene.
- Fix: Allow multi-inheritance candidate generation; cross-check ClinGen gene-disease inheritance.

## Reconciliation: When Sources Disagree

| Pattern | Likely cause | Action |
|---------|-------------|--------|
| Exomiser ranks low; ClinVar says P | Sparse or wrong HPO terms; rare disease in atypical gene | Re-run with full HPO; manual review |
| ClinVar P + ClinGen Limited validity | Variant-level vs gene-disease tension | Treat as candidate; require VCEP curation or functional evidence |
| DeNovoGear high posterior; trio coverage uneven | Parental mosaicism or mapping error | IGV review; consider parent-of-origin testing |
| Compound het in phasing-ambiguous gene | Distance > 500 bp; can't phase from reads | Trio phasing; long-read confirmation |
| SF gene with V3.1 list; missing CALM | Miller 2023 v3.2 update | Re-run with v3.2 (81 genes) |
| Phenotype tool disagrees with clinical | Tool-specific phenotype model; literature gap | Cross-check with AMELIE for literature-mining alternative |
| Mosaic suspected but standard pipeline negative | VAF below 30% threshold | Deep targeted sequencing or affected tissue |

## Quantitative Thresholds and Conventions

| Threshold | Convention | Source |
|-----------|-----------|--------|
| Rare-disease frequency filter | grpmax_faf95 < 0.0001 | ClinGen SVI |
| Recessive disease filter | grpmax_faf95 < 0.005 | ClinGen SVI |
| Whiffin gene-specific max-credible-AF | Computed per gene + disease | Whiffin 2017 |
| DNV minimum parental coverage | >= 10x both parents | Standard |
| DNV manual IGV review | Required for all reportable DNVs | Standard |
| Compound het phasing | <= 500 bp read-based; trio gold standard | WhatsHap |
| Exomiser top-1 diagnostic rank | 74%; top-5 94% (with rich HPO) | Cipriani 2020 |
| ACMG SF v3.2 genes | 81 (Miller 2023) | Miller 2023 *Genet Med* |
| VUS reclassification cycle | Reassess as evidence accrues; ClinGen recommends periodic re-review | convention |
| Mosaic VAF threshold | 2-30% | Convention |
| ClinGen gene-disease validity gate | Moderate or Strong minimum for diagnostic reporting | ClinGen SVI |

## Common Errors

| Symptom | Cause | Solution |
|---------|-------|----------|
| Too many candidate variants (>50) | Frequency filter too loose | Tighten to grpmax_faf95 < 0.0001 (dominant) or 0.005 (recessive) |
| No DNV candidates in obvious DNV phenotype | False-negative DNV calling | DeNovoGear / DeNovoCNN; check parental sample swap |
| Compound het in gene known AD only | Phasing not validated | Confirm phase via trio or long-read |
| Exomiser top hit unrelated to phenotype | HPO too generic or wrong | Add specific HPO; check ontology version |
| Mosaic disease missed | VAF threshold too high | Deep coverage; affected tissue sampling; VAF 2-5% |
| SF gene match flagged but variant benign | Wrong variant classification | Apply ACMG framework via `acmg-classification` skill |
| Genotype-phenotype discordance | Locus heterogeneity OR multi-gene contribution | Run digenic / oligogenic analysis tools |

## Anticipated Reviewer Pushback

| Pushback | Standard response |
|----------|-------------------|
| "Why grpmax_faf95 instead of AF?" | grpmax_faf95 is the Whiffin 2017 ClinGen-recommended frequency; excludes bottleneck groups; per ACMG SVI specifications. |
| "Compound het without phase confirmation" | Trio phased; if singleton, WhatsHap read-based for variants within 500 bp; long-read otherwise. |
| "DNV call without IGV review?" | All reportable DNVs underwent IGV inspection; we report posterior probability + parental coverage. |
| "ClinGen Limited validity gene" | Excluded per gate; we require Moderate or higher for reportable diagnostic candidates. |
| "Why ACMG SF v3.2 not v3.1?" | v3.2 (Miller 2023) added CALM1/2/3 calmodulinopathies (high actionability). We use current. |
| "Phenotype-driven prioritization with single HPO term?" | We submit 5-10 specific HPO terms; sparse input degrades Exomiser. |
| "ACMG classification logic?" | Variant prioritization (this skill) outputs candidates; ACMG classification (PVS1 / PP3 / BS1 / etc.) is in `acmg-classification` skill. |
| "Why not VarSome / Franklin automated ACMG?" | We report aggregated annotations via myvariant.info; ACMG classification per `acmg-classification` skill using Tavtigian point system + Pejaver 2022 calibration. |

## References

- Richards S et al. 2015. Standards and guidelines for the interpretation of sequence variants. *Genet Med* 17:405. (ACMG/AMP)
- Miller DT et al. 2023. ACMG SF v3.2 list for reporting of secondary findings in clinical exome and genome sequencing. *Genet Med* 25:100866.
- Smedley D et al. 2015. Next-generation diagnostics and disease-gene discovery with the Exomiser. *Nat Protoc* 10:2004.
- Zhao M et al. 2020. Phen2Gene: rapid phenotype-driven gene prioritization for rare diseases. *NARGAB* 2:lqaa032.
- Birgmeier J et al. 2020. AMELIE speeds Mendelian diagnosis by matching patient phenotype and genotype to primary literature. *Sci Transl Med* 12:eaau9113.
- Cipriani V et al. 2020. An improved phenotype-driven tool for rare Mendelian variant prioritization. *Genes* 11:460.
- Ramu A et al. 2013. DeNovoGear: de novo indel and point mutation discovery and phasing. *Nat Methods* 10:985.
- Patterson M et al. 2015. WhatsHap: weighted haplotype assembly for future-generation sequencing reads. *J Comput Biol* 22:498.
- Strande NT et al. 2017. Evaluating the clinical validity of gene-disease associations: an evidence-based framework developed by ClinGen. *AJHG* 100:895.
- Whiffin N et al. 2017. Using high-resolution variant frequencies to empower clinical genome interpretation. *Genet Med* 19:1151.
- Lunke S et al. 2025. Feasibility, acceptability and clinical outcomes of the BabyScreen+ genomic newborn screening study. *Nat Med* 31:4236.
- Yauy K et al. 2022. Genome Alert! *Genet Med* 24:1316. (VUS reclassification monitoring)
- ClinGen gene-disease validity: `https://search.clinicalgenome.org/kb/gene-validity`
- HPO: `https://hpo.jax.org/`
- ACMG SF v3.2 supplement: `https://www.gimjournal.org/article/S1098-3600(23)00879-1/fulltext`

## Related Skills

- clinical-databases/acmg-classification - PVS1 / PP3 / BS1 / PM2 calibration and Tavtigian point system
- clinical-databases/clinvar-lookup - Variant pathogenicity database query
- clinical-databases/gnomad-frequencies - Population frequency filtering
- clinical-databases/myvariant-queries - Aggregated annotation
- clinical-databases/pharmacogenomics - PGx variant handling
- variant-calling/clinical-interpretation - Clinical reporting workflow
- variant-calling/filtering-best-practices - Upstream QC
<!-- END FILE: clinical-databases/variant-prioritization/SKILL.md -->

<!-- END CATEGORY: clinical-databases -->

