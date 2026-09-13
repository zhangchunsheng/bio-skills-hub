---
slug: bio-variant-calling-integrated
version: 1.0.0
displayName: "变异检测 / Germline and somatic variant calling"
name: bio-variant-calling-integrated
summary: >-
  中文：变异检测综合技能，整合 13 个相关专题，覆盖种系和体细胞变异检测：SNP/Indel调用、SV检测、VCF操作、规范化、过滤与注释。 English: Integrated Germline and somatic variant calling skill covering 13 related topics, including Germline and somatic variant calling: SNP/Indel calling, SV detection, VCF manipulation, normalization, filtering, and annotation.
description: >-
  中文：这是一个面向变异检测的综合生物信息学 Skill，整合当前分类下 13 个相关专题能力。它用于根据研究问题、数据类型和分析阶段，选择合适的方法与工具，规划从输入检查、预处理、核心分析到质量控制、统计解释和结果报告的完整流程。重点覆盖：种系和体细胞变异检测：SNP/Indel调用、SV检测、VCF操作、规范化、过滤与注释。当用户提供相关实验数据、测序结果、表格或研究问题时，它会帮助判断分析目标与前置条件，给出工具选择、关键参数、输入输出、常见失败原因、结果解读和可复现建议。主要工具包括：DeepVariant, GATK, VEP。该 Skill 提供分析设计与实施指导，不替代对具体数据质量、生物学背景和最终结论的人工审查。
  English: This is an integrated bioinformatics Skill for Germline and somatic variant calling, combining 13 related topic areas. It helps users choose appropriate methods and tools based on the research question, data type, and analysis stage, and plan an end-to-end workflow from input validation and preprocessing through core analysis, quality control, statistical interpretation, and reporting. It covers Germline and somatic variant calling: SNP/Indel calling, SV detection, VCF manipulation, normalization, filtering, and annotation. For relevant experimental data, sequencing results, tables, or research questions, it clarifies prerequisites, recommends tools and parameters, describes expected inputs and outputs, explains common failure modes, and supports reproducible analysis. Primary tools include: DeepVariant, GATK, VEP. It provides methodological and implementation guidance; final data-quality assessment and biological conclusions still require human review.
---

# variant-calling 分类 Skill 整合版

> 本文件整合同一主分类目录下 13 个子目录中的 SKILL.md 内容。
> 各子目录正文按原文保留，并通过标题和边界标记进行区分；源文件中的元数据块未被改写。

---

<!-- BEGIN CATEGORY: variant-calling -->

## 子目录：variant-calling/clinical-interpretation

<!-- BEGIN FILE: variant-calling/clinical-interpretation/SKILL.md -->
---
name: bio-variant-calling-clinical-interpretation
description: Classify variant clinical significance with the ACMG/AMP germline framework and its 2018-2025 ClinGen refinements (graded PVS1 decision tree, PM2 downgraded to Supporting, PP5/BP6 retired, calibrated PP3/BP4, Bayesian points), the AMP/ASCO/CAP somatic tiers and ClinGen oncogenicity system, ClinVar star-rating and gnomAD grpmax filtering-AF interpretation. Use when deciding germline-vs-somatic framework, applying current (not flat-2015) ACMG points, checking for a gene-specific VCEP specification, judging whether a ClinVar assertion or gnomAD frequency is usable evidence, calibrating a pathogenicity predictor, evaluating PVS1 on the MANE Select transcript, or building a VUS reanalysis loop. Not for functional annotation itself (see variant-calling/variant-annotation).
tool_type: mixed
primary_tool: bcftools
---

## Version Compatibility

Reference examples tested with: bcftools 1.19+, cyvcf2 0.30+, InterVar 2.2+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

Note: interpretation guidance evolves. Flat 2015 ACMG defaults are OUT OF DATE; verify the current ClinGen SVI recommendations and any gene-specific VCEP specification before classifying. Never apply germline ACMG to a somatic variant.

# Clinical Variant Interpretation

**"Classify this variant / write the ACMG rationale"** -> Assemble independent, calibrated evidence lines and combine them under the correct framework for a pinned (gene, transcript, disease) context.
- Germline Mendelian: ACMG/AMP + ClinGen SVI refinements (below).
- Somatic/tumor: AMP/ASCO/CAP tiers + ClinGen/CGC/VICC oncogenicity (never ACMG).

## The governing principle

A variant's clinical significance is NOT a database lookup. It is a Bayesian sum of INDEPENDENT, CALIBRATED evidence relative to a pinned context (genome build, MANE Select transcript, gene disease-mechanism, disease prevalence, framework version). Three traps sink most naive pipelines:

1. **Flat 2015 defaults are obsolete.** A current classifier applies the ClinGen SVI refinements (graded PVS1, PM2 downgraded, PP5/BP6 retired, calibrated PP3/BP4, Bayesian points). Using the raw 2015 combining rules is a known error.
2. **Germline and somatic are different questions with different frameworks.** "Does this cause a Mendelian disorder" (ACMG) vs "is this an actionable/oncogenic tumor variant" (Li tiers, Horak oncogenicity). Applying ACMG to a somatic variant is a category error.
3. **A ClinVar assertion is a LEAD, not evidence.** Concordance between submitters is not independence; 1-star is not usable; re-derive from the underlying data.

## Pick the framework FIRST

| Variant origin | Framework | Question answered | Cite |
|----------------|-----------|-------------------|------|
| Germline (constitutional) | ACMG/AMP + ClinGen SVI | Pathogenic..Benign for a Mendelian disorder | Richards 2015; Abou Tayoun 2018; Tavtigian 2020; Pejaver 2022 |
| Somatic (tumor), actionability | AMP/ASCO/CAP tiers I-IV | Diagnostic/prognostic/therapeutic significance in THIS tumor type | Li 2017 |
| Somatic, oncogenicity | ClinGen/CGC/VICC points | Oncogenic..Benign (is it a driver) | Horak 2022 |

Before applying generic ACMG, **check for a ClinGen Variant Curation Expert Panel (VCEP) specification for the gene** (e.g. hearing loss, RASopathy, cardiomyopathy, ENIGMA BRCA1/2). A VCEP spec reweights and constrains criteria and OVERRIDES generic defaults; a 3-star ClinVar assertion often reflects one.

## ACMG/AMP germline: the 2015 baseline and its mandatory refinements

The 2015 consensus (Richards 2015 *Genet Med* 17:405-424) defines five tiers (Pathogenic, Likely Pathogenic, VUS, Likely Benign, Benign) and 28 coded criteria at default strengths: PVS1 (very strong), PS1-4 (strong), PM1-6 (moderate), PP1-5 (supporting); BA1 (stand-alone), BS1-4 (strong), BP1-7 (supporting). A director does NOT interpret with raw 2015 anymore. Apply these ClinGen SVI corrections:

| Refinement | What changed | Consequence for the classifier |
|------------|--------------|-------------------------------|
| Graded PVS1 (Abou Tayoun 2018 *Hum Mutat* 39:1517) | PVS1 is a decision tree, not automatic for any null | Emit PVS1 at Very Strong / Strong / Moderate / Supporting per NMD + mechanism (below) |
| PM2 -> Supporting (ClinGen SVI PM2 v1.0, approved Sept 2020) | Absence from gnomAD is WEAK | Apply PM2 at Supporting, never Moderate |
| PP5 / BP6 RETIRED (Biesecker & Harrison 2018 *Genet Med* 20:1687) | An assertion cannot substitute for evidence | Never use PP5/BP6; cite the underlying data instead |
| Calibrated PP3 / BP4 (Pejaver 2022 *AJHG* 109:2163) | Computational evidence is graded, not flat-Supporting | Use ONE calibrated predictor at its calibrated strength (below) |
| Bayesian points (Tavtigian 2018/2020) | Verbal combining rules approximate naive Bayes | Sum points; graded/fractional strengths are coherent |

### Bayesian points system (Tavtigian 2020 *Hum Mutat* 41:1734)

**Goal:** Combine graded evidence into a tier reproducibly instead of matching verbal rule patterns.

**Approach:** Assign each met criterion a point value by strength (benign subtracts), sum, and threshold. This underlies the emerging points-based ACMG/AMP/CAP/ClinGen overhaul, so prefer it over the 2015 verbal table.

| Strength | Points (P side) | OddsPath (Tavtigian 2018, prior ~0.10) |
|----------|-----------------|-----------------------------------------|
| Supporting | +1 | ~2.08 |
| Moderate | +2 | ~4.33 |
| Strong | +4 | ~18.7 |
| Very Strong | +8 | ~350 |

Classification by summed points: Pathogenic >= 10, Likely Pathogenic 6-9, VUS 0-5, Likely Benign -1 to -6, Benign <= -7 (confirm the exact benign cutpoints against Tavtigian 2020 before hard-coding). Benign criteria (BA1/BS/BP) contribute negative points at the same magnitudes.

### PVS1 decision tree and the NMD 50-nt rule

**Goal:** Assign PVS1 the CORRECT strength for a null variant instead of firing it on any "HIGH impact" call.

**Approach:** Route by gene LOF mechanism, then variant type, then NMD prediction and exon location (Abou Tayoun 2018). Evaluate on the MANE Select transcript, not whichever isoform maximizes severity.

- **Gene mechanism gate:** PVS1 applies ONLY where loss of function is the established disease mechanism (haploinsufficiency). For gain-of-function / dominant-negative genes a null may be benign -- PVS1 must not fire.
- **NMD 50-55 nt rule:** a premature termination codon >~50-55 nt upstream of the last exon-exon junction triggers nonsense-mediated decay (true LOF -> full strength). A PTC in the LAST exon, within ~50 nt of the final junction, or in a single-exon gene ESCAPES NMD -- protein is made; downgrade PVS1 (Strong/Moderate/Supporting) by how much functional protein / which domains are lost.
- **Transcript relevance:** confirm the affected exon is in biologically expressed transcripts; a canonical-splice change in a minor non-expressed isoform is not PVS1.
- "HIGH impact stop_gained" from SnpEff/ANNOVAR is NOT PVS1 -- impact buckets know nothing about NMD or mechanism. Evaluate PVS1 on MANE Select; do not use the worst-consequence transcript. See variant-calling/variant-annotation.

## ClinVar: assertions are leads, not evidence

**"Look up this variant in ClinVar"** -> Read WHO submitted, at what review status, on WHAT evidence -- then re-derive, do not adopt the conclusion.

| CLNREVSTAT | Stars | Usable as evidence? |
|------------|-------|---------------------|
| practice_guideline | 4 | Strongest single-DB signal; still verify vs current evidence |
| reviewed_by_expert_panel | 3 | VCEP; strong, often implies a gene specification |
| criteria_provided,_multiple_submitters,_no_conflicts | 2 | Consensus; check submitters shared no common error |
| criteria_provided,_single_submitter | 1 | A LEAD only -- not usable as evidence |
| criteria_provided,_conflicting_classifications | 1 | Conflict is an informative signal, not noise to average |
| no_assertion_criteria_provided | 0 | No weight |

Rules: 1-star / no-criteria is not evidence. Conflicting interpretations flag genuinely hard variants (penetrance, ancestry, mechanism) -- investigate, do not average. Concordance is not independence (two submitters can copy one original error). PP5/BP6 are retired precisely because an assertion cannot be an evidence input.

### Annotate and read ClinVar fields (bcftools / cyvcf2)

**Goal:** Attach ClinVar assertions as LEADS and surface review status alongside significance.

**Approach:** Annotate CLNSIG/CLNDN/CLNREVSTAT from the ClinVar VCF, then always carry CLNREVSTAT so a 1-star call is never mistaken for evidence. Download the build-matched ClinVar VCF first (usage-guide.md).

```bash
bcftools annotate -a clinvar.vcf.gz \
    -c INFO/CLNSIG,INFO/CLNDN,INFO/CLNREVSTAT input.vcf.gz -Oz -o with_clinvar.vcf.gz

# Surface P/LP leads WITH their review status (never drop CLNREVSTAT)
bcftools view -i 'INFO/CLNSIG~"athogenic"' with_clinvar.vcf.gz \
  | bcftools query -f '%CHROM:%POS %REF>%ALT\t%INFO/CLNSIG\t%INFO/CLNREVSTAT\n'
```

## Population frequency: grpmax filtering-AF, not a global cutoff

**Goal:** Decide BA1/BS1 (or PM2_Supporting) correctly for THIS disease, not with a universal 1% line.

**Approach:** Compare the gnomAD grpmax filtering allele frequency to the maximum credible population AF derived from disease prevalence, heterogeneity, inheritance and penetrance (Whiffin 2017 *Genet Med* 19:1151). A flat cutoff is wrong in both directions.

- **Filtering AF (FAF)** is the LOWER bound of the 95% CI of the grpmax (genetic-ancestry-group max) AF -- gnomAD v4 exposes it as the `fafmax_faf95_max` INFO field (`fafmax_faf95_max_joint` in the joint exome+genome VCF). Using grpmax, not global AF, avoids diluting a variant common in one ancestry across the whole cohort; using the CI lower bound guards against a noisy small-subpopulation estimate.
- **Rule:** if FAF > the disease's maximum credible population AF, apply BA1/BS1. This is per-disease.
- **Presence in gnomAD is NOT benign.** Exceptions a director watches for: recessive carriers are healthy (pathogenic alleles sit at carrier frequency, e.g. CFTR); late-onset / reduced-penetrance alleles appear in adult cohorts (BRCA, Lynch); somatic / clonal-hematopoiesis contamination leaks low-AF calls in DNMT3A/TET2; artifacts in homopolymer/segdup regions -- respect gnomAD PASS/quality flags, not raw AF.
- gnomAD ancestry groups are unevenly sampled, so "absent" is much weaker evidence for an under-represented ancestry; PM2/BS1 strength is implicitly ancestry-dependent. gnomAD v2.1.1 is GRCh37 (Karczewski 2020 *Nature* 581:434); v3/v4 are GRCh38 -- never eyeball "absent" across builds without liftover.

```bash
# Illustrative: filter on a grpmax filtering-AF field, keeping absent sites (annotation-dependent)
bcftools view -i 'INFO/fafmax_faf95_max<0.0001 || INFO/fafmax_faf95_max="."' \
    input.vcf.gz -Oz -o faf_filtered.vcf.gz
```

## Pathogenicity predictors: ONE, calibrated

**Goal:** Convert a computational score into PP3/BP4 at a defensible strength without double-counting.

**Approach:** Pick ONE predictor that reached >= Strong in the ClinGen calibration and apply it at its calibrated threshold (Pejaver 2022). Stacking correlated tools fakes independence and silently over-calls pathogenic.

- PP3 and BP4 are graded (Supporting/Moderate/Strong) and mutually exclusive. For REVEL (Ioannidis 2016 *AJHG* 99:877) the well-reproduced SUPPORTING thresholds are PP3 >= 0.644 and BP4 <= 0.290; higher-strength (Moderate/Strong) cutoffs exist -- read them from the Pejaver 2022 supplement or the current ClinGen SVI table rather than hard-coding.
- Use only ONE tool. REVEL is an ensemble of 13 scores (incl. SIFT, PolyPhen), so "REVEL agrees with PolyPhen" is not corroboration -- PolyPhen is INSIDE REVEL.
- **SIFT and PolyPhen-2 did not reach even Supporting** in the calibration -- a "damaging" call is decorative, not evidence. **Raw CADD did not reach Supporting for PP3** (CADD>=20 calibrated to benign-Moderate -- mild evidence AGAINST missense pathogenicity, the opposite of how it is usually invoked); CADD is for genome-wide/non-coding ranking, not missense PP3.
- **AlphaMissense** (Cheng 2023 *Science* 381:eadg7492) is proteome-wide and not trained on ClinVar labels, but its developer class cutoffs are NOT ACMG strengths -- check the current ClinGen SVI tool list for its calibrated PP3/BP4 thresholds before assigning a strength.
- **Splicing (SpliceAI, Jaganathan 2019 *Cell* 176:535):** delta scores 0-1, developer guidance 0.2 recall / 0.5 recommended / 0.8 precision. A high delta is a PREDICTION; converting it to PS3/PP3 strength needs the ClinGen splicing calibration, and the default scoring window is narrow -- widen it (deep-intronic/pseudoexon variants are otherwise missed). SpliceAI does not report the mis-splicing OUTCOME (exon skip vs intron retention), which determines PVS1 applicability.

### Python: research-triage prioritization (NOT formal ACMG)

**Goal:** Rank candidate variants for review triage using available annotations.

**Approach:** Combine ClinVar leads, grpmax frequency and a single calibrated predictor into a tier. This is a triage helper, not an ACMG classification -- computational scores are supporting only, and stacking here is for RANKING, not evidence.

```python
from cyvcf2 import VCF

def triage_tier(variant):
    # Triage ranking ONLY; not equivalent to ACMG. ClinVar is a lead (carry review status
    # separately), scores are PP3/BP4-supporting, and stacking predictors here just ranks.
    clnsig = str(variant.INFO.get('CLNSIG', ''))
    faf = variant.INFO.get('fafmax_faf95_max', 0) or 0
    revel = variant.INFO.get('REVEL', 0) or 0  # single calibrated predictor

    if 'Pathogenic' in clnsig and 'Likely' not in clnsig:
        return 'PATHOGENIC_LEAD'
    if 'Likely_pathogenic' in clnsig:
        return 'LIKELY_PATHOGENIC_LEAD'
    if 'Benign' in clnsig or faf > 0.05:  # BA1 territory; confirm vs disease-max credible AF
        return 'BENIGN_LEAD'
    if revel >= 0.644 and faf < 0.0001:    # REVEL PP3_Supporting threshold (Pejaver 2022)
        return 'VUS_FAVOR_PATH'
    if revel <= 0.290:                     # REVEL BP4_Supporting threshold
        return 'VUS_FAVOR_BENIGN'
    return 'VUS'

vcf = VCF('annotated.vcf.gz')
report = {'PATHOGENIC_LEAD', 'LIKELY_PATHOGENIC_LEAD', 'VUS_FAVOR_PATH'}
for v in vcf:
    tier = triage_tier(v)
    if tier in report:
        gene = v.INFO.get('SYMBOL', 'NA')
        print(f'{gene}\t{v.CHROM}:{v.POS}\t{tier}\t{v.INFO.get("CLNREVSTAT", ".")}')
```

## Somatic variants: a separate framework

**"Interpret this tumor variant"** -> Ask about actionability and oncogenicity in THIS tumor type, never germline pathogenicity. Tier is tumor-type-specific (BRAF V600E is Tier I in melanoma, lower elsewhere) -- a context-dependence with no germline analog.

**AMP/ASCO/CAP tiers (Li 2017 *J Mol Diagn* 19:4)** -- clinical actionability:
- Tier I: strong significance (FDA-approved therapy for this variant + tumor type, or in guidelines).
- Tier II: potential significance (therapy in another tumor type; trial evidence; multiple studies).
- Tier III: unknown clinical significance (the somatic "VUS").
- Tier IV: benign/likely benign (common, no oncogenic role).

**ClinGen/CGC/VICC oncogenicity (Horak 2022 *Genet Med* 24:986)** -- a SEPARATE points-based axis (Oncogenic..Benign) using cancer-specific codes (hotspot recurrence, functional oncogenic data, tumor frequency). Oncogenicity != actionability: an oncogenic driver may have no drug (Tier III despite oncogenic).

Knowledgebase evidence levels: OncoKB Level 1-4 + R1/R2 (therapeutic), CIViC evidence A-E (read the evidence item, not just the letter), COSMIC recurrence (a hotspot SIGNAL, not clinical actionability). **Tumor-only** assays cannot cleanly separate somatic from germline -- a ~50%/~100% VAF variant may be germline; filter and disclose explicitly, or use paired tumor-normal.

## Classification has an expiry date

A classification is a snapshot relative to the evidence available on its date. Build a reanalysis loop: periodically re-annotate stored VCFs against the latest ClinVar and gnomAD releases and flag VUS whose evidence changed (new functional/segregation data, a new VCEP spec, a frequency that now crosses BA1/BS1). A one-time classification without reanalysis is a latent error.

**Goal:** Re-score stored VUS against a newer ClinVar release and surface those whose assertion has since become definitive.

**Approach:** Re-annotate the prior results with the current ClinVar under a distinct INFO tag, then select records that were Uncertain but now carry a pathogenic/benign assertion.

```bash
# Re-annotate against a newer ClinVar; find VUS that now carry a definitive assertion
bcftools annotate -a clinvar_latest.vcf.gz -c INFO/CLNSIG_NEW:=INFO/CLNSIG \
    prior_results.vcf.gz -Oz -o reannotated.vcf.gz
bcftools view -i 'INFO/CLNSIG~"Uncertain" && (INFO/CLNSIG_NEW~"athogenic" || INFO/CLNSIG_NEW~"enign")' \
    reannotated.vcf.gz -Oz -o reclassified.vcf.gz
```

## Common Errors

| Symptom / mistake | Cause | Fix |
|-------------------|-------|-----|
| PVS1 fired on any stop_gained | Used SnpEff HIGH-impact bucket | Route through the Abou Tayoun tree: mechanism + NMD + MANE transcript |
| PM2 applied at Moderate | Flat 2015 default | PM2_Supporting (ClinGen SVI 2020) |
| Over-called pathogenic | Stacked SIFT+PolyPhen+REVEL | One calibrated predictor at its calibrated strength; the others are inside REVEL |
| Adopted a 1-star ClinVar "Pathogenic" | Treated an assertion as evidence | 1-star is a lead; re-derive; carry CLNREVSTAT |
| Benign called on global AF > 1% | Ignored grpmax + disease context | grpmax FAF vs disease max-credible AF (Whiffin) |
| Common founder allele benignized | Global AF hid an ancestry-specific frequency | Use grpmax; presence in gnomAD != benign |
| ACMG applied to a tumor variant | Wrong framework | Li 2017 tiers + Horak 2022 oncogenicity |
| "Absent in gnomAD" across versions | v2 is GRCh37, v3/v4 GRCh38 | Liftover the variant; check site callability |

## Related Skills

- variant-calling/variant-annotation - VEP/SnpEff/ANNOVAR consequence calls, MANE Select transcripts, tool concordance feeding PVS1
- variant-calling/variant-normalization - left-align/normalize before ClinVar/HGVS matching
- variant-calling/filtering-best-practices - quality/artifact filtering before clinical review
- variant-calling/vcf-basics - VCF field extraction and INFO parsing
- database-access/entrez-fetch - programmatic ClinVar/OMIM download

## References

- Richards S, et al. Standards and guidelines for the interpretation of sequence variants: a joint consensus recommendation of the ACMG and the AMP. *Genetics in Medicine*. 2015;17(5):405-424.
- Abou Tayoun AN, et al. Recommendations for interpreting the loss of function PVS1 ACMG/AMP variant criterion. *Human Mutation*. 2018;39(11):1517-1524.
- Tavtigian SV, et al. Modeling the ACMG/AMP variant classification guidelines as a Bayesian classification framework. *Genetics in Medicine*. 2018;20(9):1054-1060.
- Tavtigian SV, et al. Fitting a naturally scaled point system to the ACMG/AMP variant classification guidelines. *Human Mutation*. 2020;41(10):1734-1737.
- Biesecker LG, Harrison SM. The ACMG/AMP reputable source criteria for the interpretation of sequence variants. *Genetics in Medicine*. 2018;20(12):1687-1688.
- Pejaver V, et al. Calibration of computational tools for missense variant pathogenicity classification and ClinGen recommendations for PP3/BP4 criteria. *American Journal of Human Genetics*. 2022;109(12):2163-2177.
- Whiffin N, et al. Using high-resolution variant frequencies to empower clinical genome interpretation. *Genetics in Medicine*. 2017;19(10):1151-1158.
- Karczewski KJ, et al. The mutational constraint spectrum quantified from variation in 141,456 humans. *Nature*. 2020;581(7809):434-443.
- Ioannidis NM, et al. REVEL: an ensemble method for predicting the pathogenicity of rare missense variants. *American Journal of Human Genetics*. 2016;99(4):877-885.
- Cheng J, et al. Accurate proteome-wide missense variant effect prediction with AlphaMissense. *Science*. 2023;381(6664):eadg7492.
- Jaganathan K, et al. Predicting splicing from primary sequence with deep learning. *Cell*. 2019;176(3):535-548.
- Morales J, et al. A joint NCBI and EMBL-EBI transcript set for clinical genomics and research (MANE). *Nature*. 2022;604:310-315.
- Li MM, et al. Standards and guidelines for the interpretation and reporting of sequence variants in cancer: a joint consensus recommendation of AMP, ASCO, and CAP. *Journal of Molecular Diagnostics*. 2017;19(1):4-23.
- Horak P, et al. Standards for the classification of pathogenicity of somatic variants in cancer (oncogenicity): joint recommendations of ClinGen, CGC, and VICC. *Genetics in Medicine*. 2022;24(5):986-998.
- Landrum MJ, et al. ClinVar: improving access to variant interpretations and supporting evidence. *Nucleic Acids Research*. 2018;46(D1):D1062-D1067.
<!-- END FILE: variant-calling/clinical-interpretation/SKILL.md -->

## 子目录：variant-calling/consensus-sequences

<!-- BEGIN FILE: variant-calling/consensus-sequences/SKILL.md -->
---
name: bio-consensus-sequences
description: Generate consensus FASTA sequences by applying VCF variants onto a reference with bcftools consensus, or build viral/amplicon consensus with iVar. Use when reconstructing a sample-specific reference or haplotype, deciding -H haplotype vs IUPAC vs all-ALT projection, masking no-coverage sites so a consensus does not manufacture false reference calls, or setting iVar min-depth/min-frequency policy for surveillance genomes.
tool_type: cli
primary_tool: bcftools
---

## Version Compatibility

Reference examples tested with: bcftools 1.19+, samtools 1.19+, bedtools 2.31+, iVar 1.4+, minimap2 2.26+, BioPython 1.83+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

Note: the `-H` argument vocabulary (N/R/A/I/LR/LA/SR/SA/NpIu, where `I` = IUPAC code for all genotypes) has grown across bcftools 1.x releases; IUPAC output is available both as the `-H I` code and the standalone `-I`/`--iupac-codes` flag. Always confirm the accepted letters with `bcftools consensus` on the installed version before scripting a selection.

# Consensus Sequences

**"Generate a consensus sequence from my VCF"** -> Apply called variants onto a reference FASTA, producing a sample-specific sequence, with a deliberate choice of haplotype projection and no-coverage masking.
- CLI (from a VCF): `bcftools consensus -f reference.fa input.vcf.gz`
- CLI (viral/amplicon from a BAM): `samtools mpileup ... | ivar consensus -p out`
- Python: `cyvcf2` + `Bio.SeqIO` for SNP-only prototypes

## The governing principle

`bcftools consensus` walks the reference and substitutes ALT alleles at the positions present in the VCF. Everything else is copied from the reference verbatim -- which drives three traps that ruin more consensus analyses than any tool bug:

1. **A consensus silently emits REFERENCE wherever the VCF is silent -- including positions with zero coverage.** No data and confidently-reference look identical in the output. An unmasked consensus therefore manufactures false confidence at exactly the sites where the sample was never observed. Mask no-coverage sites (below) or the FASTA lies.
2. **`-H 1` on an UNPHASED VCF yields a chimeric pseudo-haplotype.** Haplotype selection is only meaningful when genotypes are phased; on unphased data it mixes alleles from different real chromosomes into a sequence that exists in no cell. Verify `|` phasing before selecting a haplotype.
3. **A single FASTA cannot faithfully represent a diploid genome.** Every projection (`-H 1`, `-I`, `-H A`) is lossy in a different way; for phase-sensitive work keep the VCF, not the consensus.

The input VCF must be **bgzipped and indexed** (`bgzip` + `bcftools index`/`tabix`); plain-gzip or unindexed input errors out. The REF bases in the VCF must match the FASTA exactly or bcftools warns and skips those records. Normalize first (see Normalization).

## Basic Usage

`bcftools consensus` reads variants from a bgzipped, indexed VCF and writes FASTA:

```bash
bcftools index input.vcf.gz                                    # .csi index (or tabix -p vcf)
bcftools consensus -f reference.fa input.vcf.gz > consensus.fa
bcftools consensus -f reference.fa -o consensus.fa input.vcf.gz  # -o instead of redirect
```

For a multi-sample VCF, always pass `-s` -- without it, the applied genotypes are undefined:

```bash
bcftools query -l input.vcf.gz                                 # list samples
bcftools consensus -f reference.fa -s sample1 input.vcf.gz > sample1.fa
```

Restrict to a region with `-r` (the FASTA header is then `>chr:from-to`):

```bash
bcftools consensus -f reference.fa -r chr1:1000000-1010000 -s sample1 input.vcf.gz > gene.fa
```

## Haplotype Selection and the Phasing Trap

`-H` chooses which allele to apply from `FORMAT/GT`. The codes are case-insensitive:

| Option | Applies | Use when |
|--------|---------|----------|
| `-H 1` / `-H 2` | Allele at GT index 1 or 2 | Emitting one true chromosome -- **only valid on PHASED genotypes** |
| `-H A` | ALT allele in every genotype | Maximum divergence from reference; a chimera of both chromosomes |
| `-H R` | REF allele at heterozygous sites | Conservative consensus; discards het ALT alleles |
| `-H I` (or the standalone `-I` / `--iupac-codes` flag) | IUPAC ambiguity code | Retain heterozygosity in one sequence (see caveat below) |
| `-H LA`/`LR`/`SA`/`SR` | Longer/shorter allele, tie broken by ALT/REF | Length-driven selection; confirm the letter set on the installed version |

**The chimeric-haplotype footgun.** `-H 1`/`-H 2` are only meaningful when genotypes are phased (`0|1`, pipe separator). With **unphased** genotypes (`0/1`, slash), the assignment of "which allele is haplotype 1" is arbitrary *per site*, so `-H 1` across many heterozygous sites produces a **switch-error mosaic that corresponds to no real chromosome** -- while looking like a clean haplotype FASTA. This is the single most dangerous consensus mistake. Verify phasing before any `-H 1`/`-H 2`:

```bash
bcftools query -f '%CHROM\t%POS[\t%GT]\n' input.vcf.gz | head   # phased: 0|1 ; unphased: 0/1
```

If genotypes are unphased, phase first (read-backed WhatsHap/HapCUT2, trio, statistical SHAPEIT/Eagle -- accurate for common variants, poor for rare/singletons -- or native long-read phasing). See phasing-imputation/haplotype-phasing and variant-calling/vcf-basics for GT interpretation.

## What a Consensus Cannot Represent

A single consensus FASTA is a lossy projection of a diploid genome; the right projection depends on the downstream use, and some tasks need the VCF instead:

| Strategy | Flag | Best for | Loses |
|----------|------|----------|-------|
| Two haplotype sequences | `-H 1` + `-H 2` (phased) | Allele-specific expression, compound-het, HLA, cis-regulatory haplotypes | Nothing (if correctly phased) |
| IUPAC ambiguity codes | `-I` | Retaining het signal in one sequence | Phase/linkage; **many tree/alignment tools read IUPAC as N** |
| All ALT alleles | `-H A` | Max divergence, quick draft | Reality -- exists in no cell |
| REF at het sites | `-H R` | Conservative single sequence | Every heterozygous ALT allele |

Two hard boundaries:

- **For phase-sensitive work, keep the VCF (or two phased haplotype FASTAs), not a single consensus.** Collapsing hets to IUPAC or picking one allele discards linkage that the analysis needs -- treating a consensus FASTA as "the sample's genome" for compound-het or allele-specific analysis is a category error.
- **`bcftools consensus` cannot apply symbolic SV alleles** (`<DEL>`, `<INS>`, `<DUP>`, `<INV>`): those carry no ALT sequence, only INFO fields, so consensus has nothing to substitute. Short-read SV VCFs (Manta/DELLY) are mostly symbolic and are NOT directly consensus-able. Folding SVs into a consensus needs sequence-resolved records (long-read/assembly callers emit these) or an assembly-based approach -- see variant-calling/structural-variant-calling.

For phylogenetics specifically, prefer one clean phased haplotype or a homozygous-ALT-only sequence over IUPAC, because ambiguity codes are silently dropped by many tree builders:

```bash
bcftools view -i 'GT="AA"' input.vcf.gz | bcftools consensus -f reference.fa > hom_alt.fa
```

## Masking No-Coverage Sites (the load-bearing footgun)

Because unobserved positions are emitted as reference (trap 1), a consensus must mask sites with insufficient data. `-m mask.bed` replaces the listed regions (default char N via `--mask-with N`). The mask must be built from **callable depth**, and the depth step hides a silent bug:

**`samtools depth` WITHOUT `-a` OMITS zero-coverage positions** from its output -- so those positions never enter the low-depth BED, never get masked, and stay as reference: the exact false-confidence failure the mask was meant to prevent. Always use `-a` (report all positions) so no-coverage sites are captured:

```bash
# Build a mask of every position below the callable-depth threshold. -a is mandatory:
# without it, zero-coverage positions are absent from the output and escape masking.
samtools depth -a aligned.bam | awk '$3 < 10 {print $1"\t"$2-1"\t"$2}' | bedtools merge > lowcov.bed

bcftools consensus -f reference.fa -m lowcov.bed input.vcf.gz > consensus.fa
```

The `< 10` threshold is a minimum-callable-depth policy (10x is a common floor for confident base calls); set it to the depth below which the calls are not trusted. `bedtools genomecov -bga -ibam aligned.bam` is an equivalent zero-coverage-aware alternative that also emits 0-depth intervals.

Do NOT rely on `-M`/`-a` for this: `-M N` outputs N only for missing `./.` genotypes already present in the VCF, and `-a N` replaces every position absent from the VCF (which N-outs the entire non-variant genome). Neither distinguishes no-coverage from confident-reference -- only a depth-derived mask does.

## Normalization Before Consensus

**Goal:** Apply indels at the correct reference position and sequence.

**Approach:** Left-align and split multiallelics with `bcftools norm` so each record matches the reference context; consensus applies records positionally and mis-represented indels corrupt the output.

```bash
bcftools norm -f reference.fa input.vcf.gz -Oz -o norm.vcf.gz
bcftools index norm.vcf.gz
bcftools consensus -f reference.fa norm.vcf.gz > consensus.fa
```

Un-normalized or overlapping indels produce wrong sequence, and `bcftools consensus` only warns to stderr while still emitting output -- so the corruption is silent unless the stderr is inspected. Even after norm, two records whose REF spans collide remain a hazard; grep the run for warnings and inspect the region. See variant-calling/variant-normalization.

```bash
bcftools consensus -f reference.fa norm.vcf.gz 2>&1 >consensus.fa | grep -i 'overlap\|warn'
```

## Viral / Amplicon Consensus with iVar

For amplicon surveillance (SARS-CoV-2 and similar), `ivar consensus` builds a per-sample consensus directly from a pileup. Its two key thresholds are **epidemiological policy decisions, not defaults to accept blindly** -- they propagate into lineage assignment and transmission-cluster inference:

```bash
# Trim PCR primers FIRST -- primer-derived bases are not sample sequence and, at
# primer-binding-site mutations, cause reference-biased miscalls if left in.
ivar trim -b primers.bed -p trimmed -i aligned.bam
samtools sort -o trimmed.sorted.bam trimmed.bam

# -aa keeps all positions (so no-coverage becomes N), -A keeps orphan mates, -d 0 lifts the depth cap.
samtools mpileup -aa -A -d 0 -B -Q 0 trimmed.sorted.bam | ivar consensus -p sample -q 20 -t 0.5 -m 10 -n N
```

| Flag | Default | Decision |
|------|---------|----------|
| `-m` min depth | 10 | Below this, iVar emits N. Too low -> single-read sequencing errors become "mutations" that corrupt outbreak phylogenies. Too high -> excessive Ns, an unusably fragmented genome. |
| `-t` min frequency to call a base | 0 (majority) | 0 calls the most common base. For a strict majority consensus use 0.5. Too low bakes minority/within-host variants and contamination into the "genome", inflating diversity and creating phantom transmission links. Raise (e.g. 0.03) only deliberately for intrahost variant work, not for a reference consensus. |
| `-q` min base quality | 20 | Bases below this are not counted toward depth/frequency. |
| `-n` no-coverage char | N | Character emitted where depth `< -m`. |

Always report `-m` and `-t` alongside a surveillance consensus -- the genome is only as trustworthy as those two numbers. Alternatives: `bcftools consensus` from a called VCF, or ViralConsensus (Moshiri 2023) which calls consensus directly from the alignment without an intermediate VCF, faster and lower-memory for large batches.

## Filtering Before Consensus

Apply only trusted calls; pipe filtered VCF straight into consensus:

```bash
bcftools view -f PASS input.vcf.gz -Oz -o pass.vcf.gz && bcftools index pass.vcf.gz
bcftools consensus -f reference.fa pass.vcf.gz > consensus.fa

bcftools view -v snps input.vcf.gz -Oz -o snps.vcf.gz && bcftools index snps.vcf.gz  # SNPs only
```

Filtered VCFs must be re-bgzipped and re-indexed before `bcftools consensus` reads them.

## Chain Files and Naming

`-c chain.txt` writes a liftover chain mapping reference coordinates to consensus coordinates -- needed when indels shift positions and annotations must be lifted. `-p PREFIX` prepends a string to output sequence names (`>sample1_chr1`).

```bash
bcftools consensus -f reference.fa -c chain.txt -p "sample1_" input.vcf.gz > consensus.fa
```

## cyvcf2 Consensus (SNP-only prototypes)

For a quick SNP-only substitution in Python (production work should use `bcftools consensus`, which handles indels, phasing, and masking):

```python
from cyvcf2 import VCF
from Bio import SeqIO

ref = {rec.id: list(str(rec.seq)) for rec in SeqIO.parse('reference.fa', 'fasta')}
for v in VCF('input.vcf.gz'):
    if v.is_snp and len(v.ALT) == 1:
        ref[v.CHROM][v.POS - 1] = v.ALT[0]   # POS is 1-based; list index is 0-based
with open('consensus.fa', 'w') as fh:
    for chrom, seq in ref.items():
        fh.write(f'>{chrom}\n{"".join(seq)}\n')
```

## Verify the Consensus

```bash
minimap2 -a reference.fa consensus.fa | samtools view -b -o aln.bam   # inspect where it diverges
bcftools view -H input.vcf.gz | wc -l                                 # variants available to apply
```

## Common Errors

| Error / Symptom | Cause | Fix |
|-----------------|-------|-----|
| `the VCF file is not indexed` | Plain-gzip or missing index | `bgzip` then `bcftools index` (or `tabix -p vcf`) |
| `sequence "chr1" not found` | Chromosome names differ between FASTA and VCF | `bcftools annotate --rename-chrs map.txt` |
| `REF does not match` | Different reference than the caller used | Use the exact FASTA used for calling; normalize |
| Clean haplotype looks wrong | `-H 1` on an unphased VCF -> chimera | Verify `|` phasing; phase before `-H` |
| Consensus reference-identical over gaps | No-coverage sites emitted as reference | Mask with `samtools depth -a` derived BED and `-m` |
| Garbled indels, stderr overlap warnings | Un-normalized/overlapping records | `bcftools norm -f ref.fa` first; inspect warnings |
| `<DEL>`/`<INS>` not applied | Symbolic SV alleles carry no ALT sequence | Use sequence-resolved SV records; see structural-variant-calling |

## Related Skills

- variant-calling/variant-calling - Generate the VCF consensus is built from
- variant-calling/vcf-basics - Interpret GT and phasing (`|` vs `/`) before `-H`
- variant-calling/variant-normalization - Left-align indels before consensus
- variant-calling/filtering-best-practices - Restrict to trusted calls first
- variant-calling/structural-variant-calling - Sequence-resolved SVs for SV-aware consensus
- phasing-imputation/haplotype-phasing - Produce phased genotypes for true haplotypes
- phylogenetics/modern-tree-inference - Build trees from a consensus alignment

## References

- Danecek P, Bonfield JK, Liddle J, Marshall J, Ohan V, Pollard MO, et al. Twelve years of SAMtools and BCFtools. *GigaScience.* 2021;10(2):giab008. doi:10.1093/gigascience/giab008. (bcftools consensus / norm / mpileup.)
- Grubaugh ND, Gangavarapu K, Quick J, Matteson NL, De Jesus JG, Main BJ, et al. An amplicon-based sequencing framework for accurately measuring intrahost virus diversity using PrimalSeq and iVar. *Genome Biology.* 2019;20(1):8. doi:10.1186/s13059-018-1618-7. (iVar consensus/trim; depth `-m` and frequency `-t` thresholds.)
- Moshiri N. ViralConsensus: a fast and memory-efficient tool for calling viral consensus genome sequences directly from read alignment data. *Bioinformatics.* 2023;39(5):btad317. doi:10.1093/bioinformatics/btad317.
<!-- END FILE: variant-calling/consensus-sequences/SKILL.md -->

## 子目录：variant-calling/deepvariant

<!-- BEGIN FILE: variant-calling/deepvariant/SKILL.md -->
---
name: bio-variant-calling-deepvariant
description: Calls germline SNPs and indels with Google DeepVariant, which reframes variant calling as CNN image classification over multi-channel pileup tensors. Covers platform-specific model selection (WGS, WES, PACBIO, ONT_R104, HYBRID_PACBIO_ILLUMINA), one-shot run_deepvariant vs the three-stage make_examples/call_variants/postprocess_variants pipeline, GPU acceleration of call_variants, DeepTrio for family/trio and de-novo calling, and joint genotyping of gVCFs with GLnexus (not GenotypeGVCFs). Use when deciding DeepVariant vs GATK vs DRAGEN, picking the right --model_type for a sequencing platform, avoiding post-hoc GATK hard filters or BQSR that degrade CNN calls, calling de-novo variants in a trio, merging a DeepVariant cohort, or weighing GIAB-trained benchmark accuracy before clinical deployment.
tool_type: cli
primary_tool: DeepVariant
---

## Version Compatibility

Reference examples tested with: DeepVariant 1.6.1+, GLnexus 1.4+, bcftools 1.19+

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `docker run google/deepvariant:<tag> /opt/deepvariant/bin/run_deepvariant --helpfull | head` to confirm flags and available `--model_type` tokens for the build
- `bcftools --version` and `bcftools --help` to confirm flags

If code throws errors, introspect the installed container and adapt the example
to match the actual API rather than retrying.

Note: newer DeepVariant releases (1.8.x+) add model types and rename image tags; always confirm the `--model_type` tokens against the exact container in use rather than assuming this list is complete.

# DeepVariant Variant Calling

**"Call germline variants with DeepVariant"** -> Render each candidate site's read pileup as a multi-channel image and classify its genotype with a trained CNN.
- CLI: `run_deepvariant` (one-shot) or `make_examples` -> `call_variants` -> `postprocess_variants` (three-stage), shipped as a Docker/Singularity container

## The governing principle

DeepVariant replaces the parametric HMM/Bayesian genotyper with a trained convolutional neural network that classifies pileup images into hom-ref / het / hom-alt. Two consequences drive every downstream decision:

1. **There is NO hand-tuned statistical filter to apply afterward.** The CNN already emits a calibrated FILTER column (`PASS` for confident variants, `RefCall` for sites judged homozygous reference). Applying GATK hard filters (QD/FS/MQ/SOR thresholds) or VQSR on top of DeepVariant output removes true positives, not false ones -- those annotations do not even exist in the VCF. Post-call handling is limited to QUAL/GQ thresholding, normalization, and region restriction.
2. **The network learned its error model from RAW base qualities**, so running BQSR upstream costs runtime and slightly LOWERS DeepVariant accuracy. DeepVariant's own guidance is to skip BQSR. The input requirement is a sorted, indexed, duplicate-marked BAM/CRAM -- nothing more.

DeepVariant calls germline variants only. For somatic calling use DeepSomatic (a separate tool from the same team); the diploid genotype classes cannot represent subclonal allele fractions.

## How DeepVariant Works

Three stages, run together by `run_deepvariant` or separately for control over intermediates:

1. **`make_examples`** (CPU-bound, the runtime bottleneck) scans the BAM for candidate sites where non-reference support passes a permissive recall-tuned screen, then renders each candidate as a multi-channel pileup image written to sharded TFRecords. Rows are reads, columns are reference positions; channels encode read base identity, base quality, mapping quality, strand, whether the read supports the candidate allele, and whether the base differs from the reference. Illumina models add an insert-size channel; long-read models add a haplotype channel. Exact tensor dimensions are version-dependent -- treat any published figure as illustrative. Parallelized by `--num_shards`.
2. **`call_variants`** runs the trained Inception-family CNN over each example and emits a 3-class genotype-likelihood output. This is the only GPU-accelerable stage.
3. **`postprocess_variants`** sorts CNN outputs, resolves multiallelics, and converts likelihoods to VCF/gVCF.

This image-based design is why DeepVariant beats parametric callers on indels and in difficult contexts (homopolymers, tandem repeats, low-complexity regions): the CNN learns visual patterns in pileup geometry that heuristic filters miss. Models are platform-specific because sequencer error modes (Illumina substitutions, ONT homopolymer indels) are visually different and each model learns the artifact distribution of its training platform.

## Model Selection

`--model_type` is load-bearing: using the wrong model silently degrades accuracy because the CNN expects platform-specific error patterns in the pileup and does NOT error out. Match the model to the instrument that produced the reads, not to the analysis goal.

| `--model_type` | Use for | Trained on | Fails / degrades when |
|----------------|---------|-----------|-----------------------|
| `WGS` | Illumina short-read WGS | 30-50x PCR-free Illumina | applied to exome without `--regions`, to long reads, or to PCR-amplicon data |
| `WES` | Illumina exome/targeted | capture exome | run without a `--regions` BED (wastes hours scanning off-target genome) |
| `PACBIO` | PacBio HiFi (CCS) | HiFi, Q30+ per-read | applied to CLR reads (Q10-15 error profile the model never saw) |
| `ONT_R104` | ONT R10.4+ chemistry | R10.4 simplex/duplex | applied to R9.4 data (use Clair3's R9.4 model); accuracy still below HiFi |
| `HYBRID_PACBIO_ILLUMINA` | samples with BOTH HiFi and Illumina | mixed HiFi+Illumina | only one platform is available |

## When to Use DeepVariant vs GATK vs DRAGEN

- **DeepVariant** -- best indel accuracy and best difficult-region/long-read performance among open tools; generalizes across platforms with a model swap; needs no filter tuning. Default choice for indels, difficult regions, and long reads.
- **GATK HaplotypeCaller** -- every parameter auditable, mature joint calling with reference-confidence squaring-off, and regulatory precedent. Prefer for very large cohorts needing GenomicsDB scaling or clinical pipelines already validated on GATK. See variant-calling/gatk-variant-calling.
- **DRAGEN** -- FPGA-accelerated, ~20-25 min per 30x genome, wins the difficult-to-map benchmarks; prefer for throughput when the hardware or cloud is available (subject to the GIAB-overfitting caveat below).

The full engine-selection decision table lives in variant-calling/variant-calling -- consult it before committing a production pipeline; the choice depends on cohort size, platform, auditability, and throughput, not on accuracy alone.

## Installation

```bash
docker pull google/deepvariant:1.6.1

# GPU support (NVIDIA GPU + nvidia-container-toolkit required)
docker pull google/deepvariant:1.6.1-gpu

# Singularity alternative
singularity pull docker://google/deepvariant:1.6.1
```

## One-Shot Run

```bash
docker run -v "${PWD}:/input" -v "${PWD}/output:/output" \
    google/deepvariant:1.6.1 \
    /opt/deepvariant/bin/run_deepvariant \
    --model_type=WGS \
    --ref=/input/reference.fa \
    --reads=/input/sample.bam \
    --output_vcf=/output/sample.vcf.gz \
    --output_gvcf=/output/sample.g.vcf.gz \
    --num_shards=16
```

Always generate a gVCF (`--output_gvcf`) even for a single sample -- it enables downstream joint calling with GLnexus without re-running DeepVariant.

Exome/targeted calling adds `--regions`:

```bash
docker run -v "${PWD}:/data" google/deepvariant:1.6.1 \
    /opt/deepvariant/bin/run_deepvariant \
    --model_type=WES \
    --ref=/data/reference.fa \
    --reads=/data/exome.bam \
    --regions=/data/targets.bed \
    --output_vcf=/data/exome.vcf.gz \
    --num_shards=8
```

PacBio HiFi and ONT differ only in `--model_type=PACBIO` or `--model_type=ONT_R104`. HiFi's Q30+ reads give the CNN clean pileups; R10.4+ chemistry substantially reduces the systematic homopolymer-indel errors that made earlier ONT chemistries unusable for short-variant calling.

## Three-Stage Pipeline

For control over intermediates (custom sharding, resuming, mixing CPU/GPU nodes), run the stages separately:

```bash
# Stage 1: render pileup images (CPU-bound; parallelize with sharded --examples)
docker run -v "${PWD}:/data" google/deepvariant:1.6.1 \
    /opt/deepvariant/bin/make_examples \
    --mode calling \
    --ref /data/reference.fa \
    --reads /data/sample.bam \
    --examples /data/examples.tfrecord.gz \
    --gvcf /data/gvcf.tfrecord.gz

# Stage 2: CNN inference (the GPU-accelerable stage)
docker run -v "${PWD}:/data" google/deepvariant:1.6.1 \
    /opt/deepvariant/bin/call_variants \
    --outfile /data/call_variants.tfrecord.gz \
    --examples /data/examples.tfrecord.gz \
    --checkpoint /opt/models/wgs

# Stage 3: emit VCF/gVCF
docker run -v "${PWD}:/data" google/deepvariant:1.6.1 \
    /opt/deepvariant/bin/postprocess_variants \
    --ref /data/reference.fa \
    --infile /data/call_variants.tfrecord.gz \
    --outfile /data/output.vcf.gz \
    --gvcf_outfile /data/output.g.vcf.gz \
    --nonvariant_site_tfrecord_path /data/gvcf.tfrecord.gz
```

## GPU Acceleration

GPU acceleration benefits ONLY `call_variants` (CNN inference); `make_examples` and `postprocess_variants` are CPU-bound and scale with `--num_shards`. For large cohorts, parallelizing across samples on CPU nodes is often more cost-effective than queuing for GPUs.

```bash
docker run --gpus all -v "${PWD}:/data" \
    google/deepvariant:1.6.1-gpu \
    /opt/deepvariant/bin/run_deepvariant \
    --model_type=WGS \
    --ref=/data/reference.fa \
    --reads=/data/sample.bam \
    --output_vcf=/data/output.vcf.gz \
    --num_shards=16
```

## DeepTrio (Family / Trio Calling)

DeepTrio extends the pileup image to span proband plus both parents simultaneously, so the CNN learns inheritance context and calls de-novo variants directly. This beats naive trio subtraction, whose apparent de-novo set is dominated by false positives from independent per-sample errors. Use DeepTrio for family studies, Mendelian-consistency work, and de-novo discovery. It ships proband and parent models for Illumina WGS/WES and PacBio (`--model_type WGS|WES|PACBIO`) and uses a separate image tag (`deeptrio-<version>`).

```bash
docker run -v "${PWD}:/data" google/deepvariant:deeptrio-1.6.1 \
    /opt/deepvariant/bin/run_deeptrio \
    --model_type=WGS \
    --ref=/data/reference.fa \
    --reads_child=/data/child.bam \
    --reads_parent1=/data/father.bam \
    --reads_parent2=/data/mother.bam \
    --sample_name_child=CHILD \
    --sample_name_parent1=FATHER \
    --sample_name_parent2=MOTHER \
    --output_vcf_child=/data/child.vcf.gz \
    --output_vcf_parent1=/data/father.vcf.gz \
    --output_vcf_parent2=/data/mother.vcf.gz \
    --output_gvcf_child=/data/child.g.vcf.gz \
    --output_gvcf_parent1=/data/father.g.vcf.gz \
    --output_gvcf_parent2=/data/mother.g.vcf.gz \
    --num_shards=16
```

Merge the three per-sample gVCFs with GLnexus (below) into one trio VCF; the joint context is what supports Mendelian-violation and de-novo-rate analysis.

## Joint Calling with GLnexus

DeepVariant gVCFs are joint-genotyped with GLnexus, NOT GATK GenotypeGVCFs -- GLnexus performs allele unification across per-sample gVCFs and grows its database incrementally as samples are added, avoiding full-cohort reprocessing. See variant-calling/joint-calling for the GATK reference-confidence alternative and when each is appropriate.

```bash
for bam in *.bam; do
    sample=$(basename "$bam" .bam)
    docker run -v "${PWD}:/data" google/deepvariant:1.6.1 \
        /opt/deepvariant/bin/run_deepvariant \
        --model_type=WGS --ref=/data/reference.fa --reads=/data/$bam \
        --output_vcf=/data/${sample}.vcf.gz \
        --output_gvcf=/data/${sample}.g.vcf.gz \
        --num_shards=16
done

docker run -v "${PWD}:/data" quay.io/mlin/glnexus:v1.4.1 \
    /usr/local/bin/glnexus_cli \
    --config DeepVariantWGS \
    /data/*.g.vcf.gz \
    | bcftools view - -Oz -o cohort.vcf.gz
```

| GLnexus `--config` | Use case | Notes |
|--------------------|----------|-------|
| `DeepVariantWGS` | Illumina WGS gVCFs | Default for most WGS cohorts |
| `DeepVariantWES` | Illumina exome gVCFs | Tuned for higher-depth, narrower-region calling |
| `DeepVariant_unfiltered` | Keep all variant sites | Research exploration; more false positives, useful for trio/de-novo where RefCall sites matter |

The DeepVariant+GLnexus path is a strong open-source alternative to GATK joint calling. Representative benchmark (Yun et al. 2020, GIAB, 40x WGS): cohort Mendelian-violation rate 1.7% vs GATK-VQSR 5.0%; SNP F1 error 0.07% vs 1.23%; indel F1 error 1.14% vs 2.92%. On a 2,504-sample cohort the GLnexus merge ran ~8x faster on chromosome 22 (0.84 h vs 6.83 h) and DeepVariant gVCFs were ~7x smaller on disk genome-wide (2.20 TB vs 15.16 TB). These figures are sample-, coverage-, and version-specific -- not fixed constants.

## Output and Quality Control

DeepVariant output is already CNN-filtered (`PASS` / `RefCall` in FILTER). Do NOT apply GATK hard filters or VQSR. Legitimate post-call handling is QUAL/GQ thresholding, normalization, and region restriction.

```bash
bcftools stats output.vcf.gz > stats.txt

# Ti/Tv sanity check: expect ~2.0-2.1 for WGS, ~3.0-3.3 for WES
bcftools stats output.vcf.gz | grep TSTV

# QUAL is CNN confidence; GQ is genotype quality. Threshold, do not re-filter on GATK annotations.
bcftools view -i 'QUAL>20 && FMT/GQ>20' output.vcf.gz -Oz -o filtered.vcf.gz
```

## Benchmarking and the GIAB Circularity Caveat

Benchmark against a GIAB truth set with a haplotype-aware comparator (hap.py + vcfeval), restricted to the confident-region BED and stratified by region difficulty:

```bash
docker run -v "${PWD}:/data" jmcdani20/hap.py:latest \
    /opt/hap.py/bin/hap.py \
    /data/HG002_GRCh38_truth.vcf.gz \
    /data/deepvariant_output.vcf.gz \
    -f /data/HG002_confident.bed \
    -r /data/reference.fa \
    -o /data/benchmark \
    --engine=vcfeval --threads 16
```

The load-bearing caveat: DeepVariant is TRAINED on GIAB truth sets (primarily HG001) and then routinely BENCHMARKED on GIAB samples. When train and test both derive from HG001-HG007, a headline F1 of 0.999 partly measures memorization of the truth set's idiosyncrasies, not generalization. The honest read weights held-out-sample performance (train on HG001/3/4/5/6/7, test on HG002 -- as precisionFDA V2 did by scoring the semi-blinded parents HG003/HG004), reports difficult-region and CMRG strata rather than one genome-wide number, and -- before clinical deployment -- validates on population-matched, characterized material rather than trusting a published GIAB F1. A benchmark that reports one global F1 without stratification and without a held-out or non-GIAB sample is not decision-grade (Krusche et al. 2019).

## Approximate Accuracy vs Other Callers

Approximate F1 from GIAB HG002/HG003/HG004 on GRCh38; exact values vary by sample, coverage, and version. On easy SNPs every modern caller exceeds F1 0.999, so the decision-relevant gaps are indels and difficult regions.

| Caller | SNP F1 | Indel F1 | Speed (30x WGS) | Notes |
|--------|--------|----------|-----------------|-------|
| DeepVariant | ~0.999 | ~0.993 | ~4-6 h CPU, ~1-2 h GPU | Highest open-tool indel accuracy; slow without GPU |
| GATK HaplotypeCaller | ~0.999 | ~0.989 | ~4-8 h CPU | Auditable; joint-calling ecosystem |
| Strelka2 | ~0.998 | ~0.960 | ~1-2 h CPU | Fast; no longer actively maintained |
| Clair3 | ~0.998 | ~0.980 | ~8 h (50x ONT) | Strong for long reads; active development |

## Resource Requirements

| Data | RAM | CPU time | GPU time | Notes |
|------|-----|----------|----------|-------|
| WGS 30x | 64 GB | ~4-6 h | ~1-2 h | `--num_shards` scales make_examples linearly |
| WES | 32 GB | ~30 min | ~10 min | Smaller target region |
| PacBio HiFi 30x | 64 GB | ~3-5 h | ~1-2 h | Fewer but longer reads |
| ONT 50x | 64 GB | ~6-8 h | ~2-3 h | Higher error rate -> more candidate sites |

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| Accuracy far below published F1 | Wrong `--model_type` for the platform (silent degradation, no error) | Match the model to the instrument (WGS/WES/PACBIO/ONT_R104) |
| Applying GATK hard filters removes true variants | DeepVariant has no QD/FS/MQ annotations; the CNN already filtered | Threshold on QUAL/GQ only; never run VQSR or hard filters on DeepVariant output |
| Slightly worse calls than expected on Illumina | BQSR was run upstream | Skip BQSR; DeepVariant learned its error model from raw qualities |
| WES run takes hours scanning empty genome | `--regions` BED omitted | Always pass `--regions` for exome/targeted data |
| GPU gives little speedup | Only `call_variants` uses the GPU; make_examples is CPU-bound | Raise `--num_shards` for the CPU stages; use GPU for call_variants |
| Trio de-novo set is full of false positives | Naive per-sample subtraction | Use DeepTrio, which learns inheritance context directly |
| Joint calling fails with GenotypeGVCFs | DeepVariant gVCFs are not GATK reference-confidence gVCFs | Merge with GLnexus, not GenotypeGVCFs |
| No `Number=R` / allele-specific fields for filtering | DeepVariant does not emit them | Do not build a GATK-style filter; rely on the CNN FILTER + QUAL/GQ |

## Related Skills

- variant-calling/gatk-variant-calling - GATK HaplotypeCaller alternative with auditable parameters, joint calling, and VQSR/VETS
- variant-calling/variant-calling - engine-selection decision table (DeepVariant vs GATK vs DRAGEN vs bcftools) and lightweight bcftools calling
- variant-calling/joint-calling - GATK reference-confidence joint genotyping, the alternative to GLnexus for cohorts
- variant-calling/filtering-best-practices - post-calling filtering for callers that DO expose hard-filter annotations (not DeepVariant)
- variant-calling/vcf-statistics - QC metrics (Ti/Tv, het/hom) for the called VCF
- long-read-sequencing/clair3-variants - long-read variant-calling alternative, especially for ONT R9.4 and resource-constrained settings

## References

- Poplin R, Chang P-C, Alexander D, et al. A universal SNP and small-indel variant caller using deep neural networks. *Nature Biotechnology* 36(10):983-987 (2018). DOI 10.1038/nbt.4235. (DeepVariant.)
- Yun T, Li H, Chang P-C, Lin MF, Carroll A, McLean CY. Accurate, scalable cohort variant calls using DeepVariant and GLnexus. *Bioinformatics* 36(24):5582-5589 (2020). DOI 10.1093/bioinformatics/btaa1081. (DeepVariant+GLnexus cohort benchmark.)
- Kolesnikov A, Goel S, Nattestad M, et al. DeepTrio: Variant Calling in Families Using Deep Learning. *bioRxiv* 2021.04.05.438434 (2021). DOI 10.1101/2021.04.05.438434. (Preprint; DeepTrio.)
- Shafin K, Pesout T, Chang P-C, et al. Haplotype-aware variant calling with PEPPER-Margin-DeepVariant enables high accuracy in nanopore long-reads. *Nature Methods* 18:1322-1332 (2021). DOI 10.1038/s41592-021-01299-w. (ONT long-read path.)
- Krusche P, Trigg L, Boutros PC, et al. Best practices for benchmarking germline small-variant calls in human genomes. *Nature Biotechnology* 37:555-560 (2019). DOI 10.1038/s41587-019-0054-x. (hap.py/vcfeval, confident regions, stratification.)
- Olson ND, Wagner J, McDaniel J, et al. PrecisionFDA Truth Challenge V2: Calling variants from short and long reads in difficult-to-map regions. *Cell Genomics* 2(5):100129 (2022). DOI 10.1016/j.xgen.2022.100129. (Held-out scoring; difficult-region performance.)
<!-- END FILE: variant-calling/deepvariant/SKILL.md -->

## 子目录：variant-calling/filtering-best-practices

<!-- BEGIN FILE: variant-calling/filtering-best-practices/SKILL.md -->
---
name: bio-variant-calling-filtering-best-practices
description: Filters germline and somatic variant callsets at the site and genotype level with GATK VQSR (VQSLOD, truth-sensitivity tranches), VETS/ScoreVariantAnnotations, NVScoreVariants, hard filters with per-annotation thresholds, and bcftools/cyvcf2 expressions, plus Ti/Tv-based QC. Use when deciding between VQSR, hard filtering, and ML recalibration by cohort size and platform, setting SNP vs indel thresholds, replicating the missing-annotation-passes rule so hom-alt sites survive, applying genotype-level GQ/DP filters, or validating filter impact. Not for VCF normalization (see variant-calling/variant-normalization) or summary statistics (see variant-calling/vcf-statistics).
tool_type: mixed
primary_tool: bcftools
---

## Version Compatibility

Reference examples tested with: GATK 4.6+, bcftools 1.19+, cyvcf2 0.30+

Note: CNNScoreVariants is deprecated as of GATK 4.6.1.0 (replaced by NVScoreVariants, a PyTorch drop-in); VETS (ExtractVariantAnnotations/TrainVariantAnnotationsModel/ScoreVariantAnnotations) is BETA. Confirm tool availability with `gatk --list` on the installed build before scripting a pipeline.

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Variant Filtering Best Practices

**"Filter my variant calls"** -> Flag or remove low-quality variant sites, and separately null out untrustworthy per-sample genotypes, using a model matched to cohort size, platform, and organism.
- CLI: GATK VariantRecalibrator/ApplyVQSR (large cohorts), VariantFiltration (hard filters), ScoreVariantAnnotations (VETS), NVScoreVariants (single-sample DL); bcftools filter/view
- Python: cyvcf2 for custom per-variant logic

## The governing principle

Filtering decides WHICH errors a callset keeps, not whether they exist. The two site-level paradigms fail in OPPOSITE regimes: VQSR (a ratio of two learned Gaussian-mixture densities over annotation space) collapses on small or exome cohorts; static hard thresholds discard real variants at scale. Two rules follow. First, site-level filtering ("is this SITE real?") and genotype-level filtering ("is this SAMPLE's genotype trustworthy?") are orthogonal -- both are needed, site first. Second, SNPs and indels have different error processes (base-calling/strand vs alignment-ambiguity-in-repeats) and different truth resources, so they are ALWAYS filtered separately then merged. None of these mistakes throws an error: the VCF stays structurally valid while the numbers are silently wrong.

## Site-Level Filter Method Selection

Somatic data is a separate track: use GATK FilterMutectCalls, never VQSR or germline hard filters (the annotations and error model differ).

| Method | Best when | Fails when |
|--------|-----------|------------|
| Hard filters (VariantFiltration) | Single sample, exome, targeted panel, non-model organism, or any callset lacking truth resources | Precision-critical work at scale -- static cutoffs leave real variants on the table |
| VQSR (VariantRecalibrator/ApplyVQSR) | Human, a single deep WGS OR ~30+ jointly-genotyped exomes, HapMap/Omni/Mills truth sets available | A single exome/panel (too few variants): the GMM is non-identifiable and VQSLOD is noise |
| Allele-specific VQSR (`-AS`, `AS_*` annotations) | Very large cohorts (biobank/gnomAD scale) where one bad allele at a multiallelic must not sink the site | Small cohorts; adds nothing over site-level VQSR |
| VETS (ScoreVariantAnnotations, BETA) | Modern GATK replacement for VQSR; scikit-learn isolation-forest on site annotations, more robust than GMM, works down to smaller cohorts | Still BETA -- validate against a truth set before production use |
| NVScoreVariants (deep learning) | A single sample, especially a single exome/panel where VQSR has too few variants to train; PyTorch CNN scores reads+reference, then FilterVariantTranches applies tranches | Needs a GPU-friendly env for the 2D model; replaced deprecated CNNScoreVariants |
| DL-native caller output (DeepVariant, DRAGEN ML) | The caller already emits calibrated QUAL / vendor FILTER flags | Do NOT re-apply GATK hard filters on top -- annotation distributions differ; filter on the caller's own fields |

Methodology is evolving (VETS is displacing VQSR). Verify the current recommended path against the installed GATK version's "How to Filter variants" article before committing a pipeline.

## VQSR -- Mechanism and Why It Breaks

**Goal:** Recalibrate a large jointly-genotyped human callset with a data-driven quality score.

**Approach:** Fit a Gaussian mixture model (GMM) to the annotation profile of known-true sites (positive model), bootstrap a second GMM on the low-probability-tail artifact sites (negative model), and score each variant by VQSLOD = log( P(annotations | positive) / P(annotations | negative) ). Then choose a truth-sensitivity TRANCHE rather than thresholding VQSLOD directly: a "99.7 tranche" is the VQSLOD cutoff that RETAINS 99.7% of the truth-set sites. Tranches are truth-set SENSITIVITIES, not FDRs.

Three load-bearing consequences the agent must respect:
- VQSR estimates full covariance matrices in ~6-8 annotation dimensions, so it needs tens of thousands of variants -- as practical GATK convention, a single deep WGS (which alone supplies millions of sites) OR ~30+ jointly-genotyped exomes. On a single exome or panel the model is non-identifiable or wildly overfit -- it may report "converged" while VQSLOD is garbage. This is the single most common real-world VQSR misuse.
- On exomes, DP must NOT be supplied as a VQSR annotation: capture depth tracks bait design, not truth, and injects a spurious signal.
- SNPs and indels are recalibrated in separate runs (`-mode SNP`, `-mode INDEL`) because indels are ~10x rarer and their GMM fails first (see governing principle).

```bash
# SNP recalibration: fit the GMM in annotation space against truth resources
gatk VariantRecalibrator \
    -R reference.fa -V cohort.vcf.gz \
    --resource:hapmap,known=false,training=true,truth=true,prior=15.0 hapmap.vcf.gz \
    --resource:omni,known=false,training=true,truth=true,prior=12.0 omni.vcf.gz \
    --resource:1000G,known=false,training=true,truth=false,prior=10.0 1000G.vcf.gz \
    --resource:dbsnp,known=true,training=false,truth=false,prior=2.0 dbsnp.vcf.gz \
    -an QD -an MQ -an MQRankSum -an ReadPosRankSum -an FS -an SOR \
    -mode SNP \
    -O snp.recal --tranches-file snp.tranches
# For exomes: OMIT -an DP (capture depth is uninformative of truth), add -an QD -an FS etc. only

# Apply the chosen truth-sensitivity tranche (keeps 99.7% of truth-set SNPs)
gatk ApplyVQSR \
    -R reference.fa -V cohort.vcf.gz \
    -mode SNP --recal-file snp.recal --tranches-file snp.tranches \
    --truth-sensitivity-filter-level 99.7 \
    -O snp.recalibrated.vcf.gz
```

Run the identical pair with `-mode INDEL` and the Mills/1000G gold-indel resource, then merge the recalibrated SNP and indel callsets. For a single exome or panel (too few variants for VQSR), replace this whole block with hard filters or NVScoreVariants.

## GATK Hard Filters (SNPs and indels separately)

**Goal:** Flag artifacts with static, per-annotation thresholds when VQSR is inapplicable.

**Approach:** Split the callset by type (`SelectVariants`), apply type-appropriate OR-combined fail conditions with `VariantFiltration`, then merge. Each annotation targets an independent error mode; a variant fails if it violates ANY one.

**"Filter my variants using GATK best practices"** -> Apply GATK's recommended annotation cutoffs, separately for SNPs and indels.

```bash
# SNPs
gatk VariantFiltration -R reference.fa -V raw_snps.vcf -O filtered_snps.vcf \
    --filter-expression "QD < 2.0" --filter-name "QD2" \
    --filter-expression "FS > 60.0" --filter-name "FS60" \
    --filter-expression "MQ < 40.0" --filter-name "MQ40" \
    --filter-expression "MQRankSum < -12.5" --filter-name "MQRankSum-12.5" \
    --filter-expression "ReadPosRankSum < -8.0" --filter-name "ReadPosRankSum-8" \
    --filter-expression "SOR > 3.0" --filter-name "SOR3"

# Indels: FS loosened to 200, ReadPosRankSum tightened to -20, MQ/MQRankSum DROPPED
gatk VariantFiltration -R reference.fa -V raw_indels.vcf -O filtered_indels.vcf \
    --filter-expression "QD < 2.0" --filter-name "QD2" \
    --filter-expression "FS > 200.0" --filter-name "FS200" \
    --filter-expression "ReadPosRankSum < -20.0" --filter-name "ReadPosRankSum-20" \
    --filter-expression "SOR > 10.0" --filter-name "SOR10"
```

The SNP/indel threshold difference is the point, not an inconsistency: real indels have messier local alignments in repeats, so strand bias (FS) is naturally higher and the gate is loosened to 200; spurious indels cluster at read ends, so ReadPosRankSum is tightened to -20. Mapping-quality metrics (MQ, MQRankSum) are dropped for indels because they are less diagnostic there and the truth model is weaker. Values are GATK-recommended lenient starting points -- verify against the installed version's docs and tune to the annotation histograms of the dataset.

### The hom-alt "missing => PASS" trap

MQRankSum, ReadPosRankSum, and BaseQRankSum are rank-sum tests comparing ref- vs alt-supporting reads, so they are only DEFINED at heterozygous sites. At hom-alt sites there are no ref reads and the annotation is missing (`.`). GATK's `VariantFiltration` fires a filter only when the value is PRESENT and violates the cutoff -- a missing value PASSES. Anyone hand-writing the equivalent in bcftools MUST replicate this: guard every RankSum term with an explicit `|| INFO/X = "."`, or every hom-alt variant silently fails and vanishes.

```bash
# GATK SNP hard filter (plus a QUAL>=30 floor, which is not part of GATK's canonical set)
# -- the "|| = \".\"" guard on each RankSum term lets hom-alt sites (undefined RankSums) pass
bcftools filter -i '
    QUAL >= 30 && (INFO/QD >= 2.0 || INFO/QD = ".") &&
    (INFO/FS <= 60.0 || INFO/FS = ".") && (INFO/MQ >= 40.0 || INFO/MQ = ".") &&
    (INFO/MQRankSum >= -12.5 || INFO/MQRankSum = ".") &&
    (INFO/ReadPosRankSum >= -8.0 || INFO/ReadPosRankSum = ".") &&
    (INFO/SOR <= 3.0 || INFO/SOR = ".")' raw_snps.vcf.gz -Oz -o snps_filtered.vcf.gz
```

## Quality Metric Rationale

| Metric | Threshold | Rationale |
|--------|-----------|-----------|
| QD (QualByDepth) | <2.0 | QUAL normalized by alt-supporting depth. Raw QUAL grows with coverage, so a 500x artifact can post a huge QUAL; QD removes that inflation. Bimodal in practice -- real variants ~12-35, artifacts near 0. The workhorse, not QUAL. |
| FS (FisherStrand) | >60 (SNP), >200 (indel) | Phred-scaled Fisher's-exact p-value for strand bias. Real variants are strand-symmetric; many artifacts are strand-specific. Breaks down at exon/read ends where SOR takes over. |
| SOR (StrandOddsRatio) | >3.0 (SNP); >10.0 (indel) is a commonly-added community/WDL convention, not part of GATK's canonical indel set (QD/QUAL/FS/ReadPosRankSum) | Symmetric-odds strand-bias metric that tolerates the legitimate strand imbalance at exon/read ends where FS false-positives. Complements FS, does not replace it. |
| MQ (RMSMappingQuality) | <40.0 | RMS mapping quality of reads at the site. Low MQ => reads map ambiguously (repeats, paralogs, segdups) => likely mapping artifact. |
| MQRankSum | <-12.5 | Rank-sum of mapping quality, alt- vs ref-supporting reads. Strongly negative => alt reads map worse => probable mismapping. Missing at hom-alt sites. |
| ReadPosRankSum | <-8.0 (SNP), <-20.0 (indel) | Rank-sum of within-read position, alt vs ref bases. Strongly negative => alt clusters at read ends (highest error, least reliable alignment). Missing at hom-alt sites. |
| DP (depth) | context-specific | Extreme depth (>2x or <0.3x mean) suggests collapsed repeats or poor capture. Filtering on DP alone removes real variants in duplicated regions -- always combine with MQ/MQRankSum. Never a VQSR annotation on exomes. |
| GQ (genotype quality) | <20 | Genotype-level, not site-level. Phred confidence in the called genotype; GQ 20 = 99%. |

## Site-Level vs Genotype-Level Filtering

The two are orthogonal and both are required, in order. Site filters (above) decide whether a SITE is real. Genotype filters set an individual sample's genotype to no-call (`./.`) when it is untrustworthy at an otherwise-passing site:
- GQ < 20 => set `./.` (genotype confidence below 99%).
- DP < 8-10 => set `./.` (too few reads for a confident diploid call, for WGS).
- Allele balance far from 0.5 at hets (e.g. alt fraction <0.2 or >0.8) => suspect mapping artifact, CNV, or contamination; derive from AD (GATK does not emit AB directly).

Ordering matters: apply genotype-level no-calls BEFORE computing cohort metrics (missingness, HWE, allele frequency). Computing HWE on a matrix full of low-GQ garbage genotypes manufactures spurious deviation. Pipeline: site filter -> genotype filter -> recompute cohort QC.

```bash
# Genotype-level: null out low-confidence genotypes, keeping the site
bcftools filter -S . -e 'FMT/GQ<20 | FMT/DP<8' passing_sites.vcf.gz -Oz -o gt_filtered.vcf.gz
```

## bcftools filter -- Soft vs Hard

**Goal:** Flag (soft) or remove (hard) variants by expression on QUAL, INFO, and FORMAT fields.

**Approach:** `-e` excludes, `-i` includes; `-s NAME` writes a named FILTER label instead of dropping; `bcftools view -f PASS` extracts survivors at the end.

```bash
bcftools filter -e 'QUAL<30' input.vcf.gz -o filtered.vcf          # hard: drop failing
bcftools filter -s 'LowQual' -e 'QUAL<30' input.vcf.gz -o marked.vcf  # soft: label failing
bcftools view -f PASS marked.vcf -o passed.vcf                      # extract PASS survivors
```

Operators: `< <= > >=  = == !=  && ||  !`. Aggregate over samples with `MIN() MAX() AVG() SUM()`. Guard against missing values explicitly (`INFO/DP!="."`), for the same hom-alt reason as above.

## Somatic Variant Filtering

**Goal:** Filter tumor-normal somatic calls with the caller's own model, not germline thresholds.

**Approach:** Run GATK FilterMutectCalls with contamination and segmentation tables, then layer additional thresholds on TLOD and VAF.

```bash
gatk FilterMutectCalls -R reference.fa -V mutect2_raw.vcf \
    --contamination-table contamination.table \
    --tumor-segmentation segments.table \
    -O mutect2_filtered.vcf
bcftools filter -i 'INFO/TLOD>6.3 && FMT/AF[0]>0.05 && FMT/DP[0]>20' \
    mutect2_filtered.vcf -o somatic_final.vcf
```

## Python Filtering (cyvcf2)

**Goal:** Apply custom multi-metric per-variant logic in Python.

**Approach:** Iterate with cyvcf2, read QUAL/INFO fields, write survivors with Writer. `INFO.get` returns None for missing tags -- treat None as pass to avoid the hom-alt trap.

```python
from cyvcf2 import VCF, Writer

vcf = VCF('input.vcf.gz')
writer = Writer('filtered.vcf', vcf)
for variant in vcf:
    qual = variant.QUAL or 0
    dp = variant.INFO.get('DP') or 1e9      # missing depth => do not fail on depth
    fs = variant.INFO.get('FS') or 0.0      # missing strand bias => pass (None -> 0)
    mq = variant.INFO.get('MQ') or 1e9      # missing MQ => pass
    if qual >= 30 and dp >= 10 and fs <= 60.0 and mq >= 40.0:
        writer.write_record(variant)
writer.close(); vcf.close()
```

## Validate Filtering

**Goal:** Confirm filtering removed artifacts without stripping true variants.

**Approach:** Compare before/after `bcftools stats`; check Ti/Tv and Het/Hom against expected ranges and known-variant recovery. A filter that improves one metric while degrading another is miscalibrated.

| Metric | WGS | WES | Interpretation |
|--------|-----|-----|----------------|
| Ti/Tv | 2.0-2.1 | 3.0-3.3 | Below range => excess false positives (random errors have Ti/Tv ~0.5, diluting the signal); a WES set at ~2.1 signals too-loose filtering. WES is higher from CpG-transition-rich coding enrichment. |
| Het/Hom | 1.5-2.0 | 1.5-2.0 | Strongly ancestry-dependent. Elevated => contamination; depressed => inbreeding/ROH. Stratify by ancestry before flagging outliers. |
| Known (dbSNP) % | >99% | >99% | Low known-variant recovery indicates over-filtering. |

```bash
bcftools stats input.vcf > before.txt
bcftools stats filtered.vcf | grep '^TSTV'                    # Ti/Tv after filtering
bcftools query -f '%FILTER\n' filtered.vcf | sort | uniq -c   # counts per FILTER label
```

If Ti/Tv drops after filtering, the filters are preferentially removing true transitions -- relax them. See variant-calling/vcf-statistics for the full QC panel (het/hom by ancestry, contamination, relatedness).

## Region-Based Filtering

Stratify by genomic context; artifact-prone regions dominate false positives. Exclude with `bcftools view -T ^regions.bed`:
- ENCODE exclusion list (github.com/Boyle-Lab/Blacklist) -- anomalous-signal regions (centromeres, satellites).
- GIAB stratification BEDs -- low-complexity, segdups, tandem repeats; essential for honest benchmarking (`bcftools isec` against a GIAB truth set).
- LCR-hs38 (Heng Li) -- homopolymers and simple repeats where indel calling is unreliable.

## Common Filtering Pitfalls

- Applying SNP thresholds to indels: distributions differ (FS, SOR, ReadPosRankSum). Always split by type first.
- Treating missing RankSum as failing: silently deletes every hom-alt site (see the missing => PASS trap).
- Running VQSR on a single exome or panel: too few variants, the GMM is non-identifiable (a single deep WGS is fine); use hard filters, VETS, or NVScoreVariants.
- Re-applying GATK hard filters on DeepVariant/DRAGEN output: their calibrated fields already encode quality; the GATK annotations may be absent or differently distributed.
- Filtering on depth alone: removes real variants in collapsed segdups; combine DP with MQ/MQRankSum.
- Choosing thresholds without looking: plot each annotation stratified by known TP (HapMap) vs likely FP and cut at the valley; GATK defaults are population-level starting points.

## Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `no such INFO tag` | Tag absent from VCF | Check header: `bcftools view -h in.vcf` |
| `syntax error` in expression | Invalid operator | Use `\|\|` not `or`; quote missing as `= "."` |
| Every hom-alt site removed | RankSum missing not guarded | Add `\|\| INFO/X = "."` to each RankSum term |
| VQSR "converged" but nonsense | Too few samples/variants | Switch to hard filters, VETS, or NVScoreVariants |
| empty output | Filter too strict | Relax thresholds; inspect annotation histograms |

## Related Skills

- variant-calling/variant-calling - Variant calling with bcftools to generate VCF files
- variant-calling/gatk-variant-calling - GATK HaplotypeCaller and joint genotyping upstream of VQSR
- variant-calling/deepvariant - Deep-learning caller whose output needs no separate site filter
- variant-calling/variant-annotation - Functional annotation after filtering
- variant-calling/variant-normalization - Left-align and decompose before filtering for consistent comparisons
- variant-calling/vcf-statistics - Ti/Tv, het/hom, contamination, and relatedness QC of filter effects
- variant-calling/vcf-basics - VCF field interpretation, PL/GQ/QUAL, and Number=A/R/G subsetting

## References

- DePristo MA, Banks E, Poplin R, et al. A framework for variation discovery and genotyping using next-generation DNA sequencing data. *Nature Genetics.* 2011;43(5):491-498. -- VQSR foundational description.
- Van der Auwera GA, Carneiro MO, Hartl C, et al. From FastQ Data to High-Confidence Variant Calls: the GATK Best Practices pipeline. *Current Protocols in Bioinformatics.* 2013;43:11.10.1-11.10.33. -- hard-filtering and VQSR usage.
- Poplin R, Chang P-C, Alexander D, et al. A universal SNP and small-indel variant caller using deep neural networks. *Nature Biotechnology.* 2018;36(10):983-987. -- DeepVariant (DL-native calls need no separate filter).
- Danecek P, Bonfield JK, Liddle J, et al. Twelve years of SAMtools and BCFtools. *GigaScience.* 2021;10(2):giab008. -- bcftools filter/view/stats.
<!-- END FILE: variant-calling/filtering-best-practices/SKILL.md -->

## 子目录：variant-calling/gatk-variant-calling

<!-- BEGIN FILE: variant-calling/gatk-variant-calling/SKILL.md -->
---
name: bio-gatk-variant-calling
description: Call germline SNPs and indels with GATK HaplotypeCaller and the GVCF joint-genotyping workflow. Covers the local-reassembly + PairHMM mechanism (why HC beats pileup callers on indels), the -ERC GVCF reference-confidence model and <NON_REF> allele, BQSR-vs-DRAGSTR and --dragen-mode error modeling, allele-specific (AS_) annotations, and edge cases (ploidy, Mutect2 mitochondria mode, sex chromosomes/PAR, contamination gating). Use when deciding whether to use HaplotypeCaller vs a pileup or DRAGEN caller, whether BQSR still earns its place, whether to call per-sample GVCFs for a cohort, or how to handle non-diploid, mitochondrial, sex-chromosome, or contaminated samples. Not for post-calling filtering depth (see variant-calling/filtering-best-practices) or cohort joint-genotyping scaling (see variant-calling/joint-calling).
tool_type: cli
primary_tool: gatk
---

## Version Compatibility

Reference examples tested with: GATK 4.5+, bcftools 1.19+

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

Note: flag DEFAULTS (e.g. `--max-alternate-alleles`, `--heterozygosity`, `--standard-min-confidence-threshold-for-calling`) drift across GATK 4.x releases and DRAGEN-mode ports models into the caller. Confirm any default with `gatk <Tool> --help` rather than trusting a memorized value.

# GATK Variant Calling

**"Call germline variants from my BAM with GATK"** -> Detect SNPs/indels by locally reassembling candidate haplotypes in active regions and genotyping reads against them.
- CLI: `gatk HaplotypeCaller` (germline diploid), `gatk Mutect2` (somatic / mitochondria / mosaic)

## Why HaplotypeCaller, not a pileup caller

A pileup/position-based caller (bcftools mpileup, the old UnifiedGenotyper) genotypes each column of the alignment independently, trusting the mapper's per-read placement. Near indels and clustered variation that placement is a per-read greedy optimum, not a locus-consistent one, so the same indel gets (mis)placed differently in different reads and is systematically misrepresented. HaplotypeCaller (HC) discards the local alignment and re-derives it: in any region showing signal it performs **local de-novo reassembly** of candidate haplotypes, then realigns every read against those haplotypes. The indel is then represented ONCE, in an assembled haplotype, not independently in each read. This is why HC (and DRAGEN, and DeepVariant) beat pileup callers on indels and complex loci, and why HC is the reference implementation everything else is benchmarked against.

### How HaplotypeCaller works (decision-relevant mechanism)

1. **Active-region determination.** HC computes a per-locus activity score (a fast reference-vs-non-reference genotype-likelihood contrast on the pileup), smooths it with a Gaussian kernel, and thresholds it (`--active-probability-threshold`, default 0.002) to seed active regions, padded so the assembler sees flanking reference. Non-active bases still get a reference-confidence emission in GVCF mode. Pathologically high-depth or highly repetitive regions can fail to assemble -- exactly where DeepVariant/DRAGEN pull ahead.
2. **Local reassembly.** For each active region HC builds a de-Bruijn-like graph from k-mers of the reference plus overlapping reads (default k = 10 and 25, merged), prunes low-weight (error) edges, and enumerates best-supported haplotypes. Each haplotype is Smith-Waterman-realigned to the reference to translate assembled sequence into concrete SNP/indel events.
3. **PairHMM read-vs-haplotype likelihoods.** For every (read, haplotype) pair HC computes P(read | haplotype) with a Pair Hidden Markov Model that integrates over ALL alignments (forward algorithm), not just the best one -- the statistically correct way to weight support when the alignment itself is uncertain. This is the dominant compute cost; production runs use vectorized (AVX/AVX-512) kernels via `--pair-hmm-implementation` and `--native-pair-hmm-threads`. DRAGEN moves this same kernel onto an FPGA.
4. **Genotype likelihoods.** Per-haplotype likelihoods are marginalized to per-allele likelihoods, then genotype likelihoods (PLs) are computed under the assumed ploidy via the Bayesian DePristo/GATK model, emitting GT/AD/DP/GQ/PL plus site annotations (QD, FS, MQ, MQRankSum, ReadPosRankSum, SOR).
5. **The diploid assumption.** Genotyping defaults to diploid (`--sample-ploidy 2`), which hard-codes true alleles at fraction 0, 0.5, or 1.0. Anything violating that (pooled, polyploid, CNV, mosaic, hemizygous chrX/Y) needs an explicit `--sample-ploidy` or a somatic caller -- see Edge Cases.

## Pipeline decision tree

```
What is the analysis context?
├── Single sample, want DRAGEN-like accuracy, open-source -> HaplotypeCaller --dragen-mode (hard-filter on QUAL)
├── Cohort < ~2000, human -> per-sample -ERC GVCF -> joint genotype -> VQSR/VETS (see joint-calling)
├── Cohort > ~2000, human -> ReblockGVCF + GnarlyGenotyper "Biggest Practices", or DeepVariant + GLnexus (see joint-calling)
├── Non-human / non-model organism -> hard filtering (no VQSR training resources)
├── Targeted panel / small exome -> hard filtering (too few variants for VQSR)
├── Non-diploid / pooled / sex chromosomes / mitochondria -> set --sample-ploidy or use Mutect2 (see Edge Cases)
└── Somatic / mosaic variants -> Mutect2 (not HaplotypeCaller)
```

## Single-sample calling

**Goal:** Call germline SNPs and indels from one sample.

**Approach:** Run HaplotypeCaller directly to VCF; add annotations, intervals, or a calling-confidence floor as needed.

```bash
# Basic call
gatk HaplotypeCaller -R reference.fa -I sample.bam -O sample.vcf.gz

# Exome / panel: restrict to capture targets (much faster, fewer off-target artifacts)
gatk HaplotypeCaller -R reference.fa -I sample.bam -L targets.interval_list -O sample.vcf.gz

# Add standard annotations explicitly (usually emitted by default; force when a downstream filter needs them)
gatk HaplotypeCaller -R reference.fa -I sample.bam -O sample.vcf.gz \
    -A Coverage -A QualByDepth -A FisherStrand -A StrandOddsRatio \
    -A MappingQualityRankSumTest -A ReadPosRankSumTest
```

MarkDuplicates is required before calling for all modes. Whether BQSR precedes it is a real decision -- see below.

## The GVCF reference-confidence model (`-ERC GVCF`)

**Goal:** Make per-sample calls that can later be combined into a cohort without re-visiting BAMs.

**Approach:** Emit a GVCF that records confidence at EVERY position, then joint-genotype separately.

`-ERC GVCF` records, at every position (variant and non-variant), how confidently the site is homozygous reference. Two properties make it the backbone of scalable cohort calling:
- **The `<NON_REF>` symbolic allele.** Every record carries a symbolic ALT `<NON_REF>` ("any allele not yet observed") with AD/PL computed against it. At joint-genotyping time a variant discovered in ANOTHER sample can therefore be evaluated in THIS sample even though this sample looked reference -- the evidence against `<NON_REF>` supplies it. This is what makes per-sample GVCFs forward-compatible with alleles found later in the cohort, and lets joint genotyping distinguish confident hom-ref from no-data (the "squaring-off" of a ragged genotype matrix).
- **GQ banding.** Contiguous non-variant sites with similar GQ collapse into homRef blocks so a GVCF is not one line per base. `-ERC BP_RESOLUTION` disables banding (one line per base, larger files).

```bash
# Per-sample GVCF (do this once per sample; reusable when the cohort grows -- the N+1 win)
gatk HaplotypeCaller -R reference.fa -I sample.bam -O sample.g.vcf.gz -ERC GVCF

# Single-sample genotyping straight from one GVCF
gatk GenotypeGVCFs -R reference.fa -V sample.g.vcf.gz -O sample.vcf.gz
```

The **N+1 problem**: naive joint calling re-processes all N samples whenever the cohort changes; the GVCF captures the expensive assembly/likelihood work once per sample, so adding sample N+1 only re-runs the cheap consolidation + GenotypeGVCFs. Cohort consolidation (`GenomicsDBImport` vs `CombineGVCFs`), scaling to tens of thousands (`ReblockGVCF`, `GnarlyGenotyper`), and joint-genotyping mechanics live in variant-calling/joint-calling -- not duplicated here.

## BQSR, DRAGSTR, and DRAGEN-GATK mode

**Does BQSR still earn its place? (honestly unsettled).** BaseRecalibrator/ApplyBQSR builds an empirical error model over base-call covariates (reported quality, read group, cycle, sequence context) to correct systematic, instrument-specific miscalibration. On older continuous-quality 4-color instruments (HiSeq, MiSeq) it mattered. On modern 2-color chemistry (NovaSeq/NextSeq) qualities are emitted in only ~4 coarse bins, leaving little smooth structure to recalibrate; empirically the callset is largely unchanged with vs without BQSR, with the delta concentrated in borderline-GQ sites. Broad keeps BQSR in Best Practices for pipeline consistency; several large pipelines drop it on binned data. Treat it as caller/instrument-dependent, not mandatory -- there is no consensus universal recommendation.

```bash
gatk BaseRecalibrator -R reference.fa -I sample.bam \
    --known-sites dbsnp.vcf.gz --known-sites Mills_and_1000G_gold_standard.indels.vcf.gz \
    -O recal.table
gatk ApplyBQSR -R reference.fa -I sample.bam --bqsr-recal-file recal.table -O sample.recal.bam
```

**Where the indel-accuracy lever actually moved: DRAGSTR.** Indel errors scale with tandem-repeat context, so the bigger gain is STR-aware indel modeling, not base-quality recalibration. DRAGEN-GATK adds **DRAGSTR**: a per-sample auto-calibration (`CalibrateDragstrModel` -> `--dragstr-params-path`) that models a-priori indel error/variant probability as a function of STR period (repeat-unit length) and length (copy number), adjusting the PairHMM indel gap priors before genotyping.

**`--dragen-mode`.** DRAGEN is Illumina's FPGA-accelerated map-align-call engine (a genome in ~20-25 min; wins the difficult-to-map precisionFDA V2 regions using alt-aware mapping). Illumina and Broad co-developed **DRAGEN-GATK**, porting DRAGEN's error models into open-source GATK to a *functionally equivalent* pipeline (Regier et al. 2018: pipelines are functionally equivalent when their call differences are smaller than sequencing-replicate differences). `HaplotypeCaller --dragen-mode` enables DRAGSTR plus **BQD** (Base Quality Dropout, systematic local quality collapse) and **FRD** (Foreign Read Detection, contaminating/mismapped reads), and **replaces classic BQSR** -- error modeling moves inside the caller. QUAL is well-calibrated, so hard-filtering on QUAL is sufficient without VQSR.

```bash
# Single-sample DRAGEN mode (no separate BQSR); GVCF variant for cohorts
gatk HaplotypeCaller -R reference.fa -I sample.markdup.bam -O sample.g.vcf.gz -ERC GVCF --dragen-mode

# DRAGEN-mode hard filter: GATK-recommended QUAL floor for DRAGEN-GATK output
gatk VariantFiltration -R reference.fa -V sample.vcf.gz -O sample.filtered.vcf.gz \
    --filter-expression "QUAL < 10.4139" --filter-name "DRAGENHardQUAL"  # Broad's documented DRAGEN-mode QUAL cutoff
```

DRAGEN-ML's advertised FP/FN reductions and speed figures are vendor-reported (Illumina), trained on GIAB truth; treat GIAB benchmark dominance with the overfitting caveat that DL/ML callers may not transfer identically to non-GIAB ancestries.

## Allele-specific annotations (AS_)

Standard annotations (QD, FS, MQ, ...) lump all reads at a site together, so at a multiallelic site a real allele co-located with an error-driven allele shares one site-level pass/fail. **AS_ annotations** (request with `-G AS_StandardAnnotation` during GVCF calling / genotyping) compute each metric per allele (AS_QD, AS_FS, AS_SOR, AS_MQ, AS_MQRankSum, AS_ReadPosRankSum), letting AS_VQSR (`-AS`) filter each allele independently. The benefit grows with cohort size, because multiallelic sites -- where a true allele and an artifact collide at one position -- proliferate as sample count rises. The GVCF workflow propagates the raw per-allele data through joint genotyping to enable this.

## Filtering: choose the method, then see filtering-best-practices

Filtering separates real variants from artifacts AFTER calling; SNPs and indels always filter separately (different annotation distributions). Pick the method here; the full VariantRecalibrator/ApplyVQSR, VETS, and hard-filter recipes with threshold rationale live in variant-calling/filtering-best-practices.

| Context | Method | Why |
|---|---|---|
| Human WGS cohort, many variants | VQSR (or its successor VETS: ExtractVariantAnnotations -> TrainVariantAnnotationsModel -> ScoreVariantAnnotations) | Enough variants + truth resources to fit the model |
| Large cohort with many multiallelics | AS_VQSR (`-AS`) | Per-allele filtering at colliding sites |
| Single exome / gene panel | Hard filtering | Too few variants for a stable GMM (a single WGS has enough; the floor is exome/panel-specific) |
| Non-model organism | Hard filtering | No HapMap/1000G/Mills truth resources |
| DRAGEN-mode output | Hard filter on QUAL | QUAL is well-calibrated |
| Somatic (Mutect2) | FilterMutectCalls | Dedicated somatic filtering, not VQSR |

VQSR needs many variants overlapping the truth resources to fit a stable multivariate density; it is unreliable on single exomes or panels -- those must hard-filter. GATK is deprecating VQSR toward VETS (isolation-forest backend); verify the current recommended path in the GATK release notes before committing a pipeline.

## Edge cases

**Ploidy (`--sample-ploidy`).** The number of genotypes is the multiset coefficient C(ploidy + alleles - 1, ploidy), so PL vectors blow up in both ploidy and allele count -- the reason high-ploidy and pooled calling are memory-heavy.

| Case | Setting | Why |
|---|---|---|
| Pooled samples (n individuals) | `--sample-ploidy 2n` | Estimate an allele count, not an individual genotype; diploid collapses intermediate frequencies |
| Polyploid organism | `--sample-ploidy 4` (etc.) | Dosage genotypes (AAAB=0.25, AABB=0.5) cannot be represented as het |
| Non-PAR chrX/Y in a 46,XY sample | `--sample-ploidy 1` (or `--ploidy-regions` BED) | Hemizygous; diploid calling emits impossible "hets" from error/paralog mismap |
| PAR1/PAR2 | Diploid (mask PAR on Y, call X-PAR as diploid) | PARs recombine and are diploid in both sexes |

**Mitochondria -> Mutect2, not HaplotypeCaller.** mtDNA heteroplasmy is a continuous VAF (mathematically identical to subclonal somatic variation) that a diploid genotype model cannot express, so use a somatic caller. Run `gatk Mutect2 --mitochondria-mode` (raises low-AF sensitivity). Because rCRS (NC_012920.1, 16,569 bp circular) is linearized in the control region, align twice -- to the standard reference and to one shifted ~8,000 bp (`ShiftFasta`) that moves the artificial breakpoint out of the D-loop -- call control-region variants on the shifted reference, `LiftoverVcf` back, and merge. NUMT-derived reads inflate false low-heteroplasmy calls, so distrust calls below ~5% AF (this underpins the gnomAD mtDNA callset, Laricchia et al. 2022).

**Contamination is a gate before trusting any call.** Even 1-3% cross-sample contamination injects minority alleles that push allele balance far enough from 0/0.5/1 to be scored as low-fraction hets. Estimate it first: **VerifyBamID2** (Zhang et al. 2020, ancestry-agnostic, genotype-free -- models sample ancestry via a PCA/SVD panel, avoiding v1's population-mismatch bias), or **CHARR** (Lu et al. 2023, variant-level only -- needs just a gVCF/VCF, ~$0.0003/sample, from reference-allele leakage at hom-alt sites). Convention: FREEMIX >= 0.03 (3%) flags a probable contaminated/swapped sample (a guide, not a hard constant). For somatic work, feed `CalculateContamination`'s table into `FilterMutectCalls` (`--contamination-table`) so genuine low-fraction variants are separated from contamination artifacts.

## Parallelization

```bash
# Scatter HaplotypeCaller by contig, then gather
for interval in chr{1..22} chrX chrY; do
    gatk HaplotypeCaller -R reference.fa -I sample.bam -L $interval \
        -O sample.${interval}.g.vcf.gz -ERC GVCF &
done
wait
gatk GatherVcfs $(for c in chr{1..22} chrX chrY; do echo "-I sample.${c}.g.vcf.gz"; done) -O sample.g.vcf.gz

# PairHMM is the compute bottleneck: give it native SIMD threads
gatk HaplotypeCaller -R reference.fa -I sample.bam -O sample.vcf.gz --native-pair-hmm-threads 4
```

## Common Errors

| Symptom | Cause | Fix |
|---|---|---|
| Spurious heterozygous calls across non-PAR chrX/Y in a male | Called as diploid | `--sample-ploidy 1` for non-PAR X/Y (split intervals or `--ploidy-regions`) |
| mtDNA low-heteroplasmy variants missed or all filtered | HaplotypeCaller's diploid model cannot express continuous VAF | Use `Mutect2 --mitochondria-mode` + shifted reference |
| Excess false hets genome-wide, allele balance off 0.5 | Sample contamination / swap | Estimate with VerifyBamID2 or CHARR before trusting calls |
| Real variant not called in a repeat/high-depth region | Assembly failed (cyclic graph at all k, or region too complex/deep) | Compare against DeepVariant/DRAGEN; check `--max-assembly-region-size`, downsampling |
| VariantRecalibrator fails to converge / errors | Too few variants or too little truth-resource overlap | Hard-filter instead (single sample, exome, panel, non-model organism) |
| Indel mis-genotyped near a homopolymer/STR | Base-quality recalibration does not model repeat-context indel error | Use `--dragen-mode` (DRAGSTR STR-aware indel model) |
| A variant appears as `*/A` or `*/*` after joint genotyping | Spanning-deletion `*` allele: this position is inside an upstream deletion in some samples | Expected; `bcftools norm`-decompose and let annotators special-case `*` |

## Related Skills

- variant-calling/joint-calling - Cohort consolidation (GenomicsDBImport/CombineGVCFs), GenotypeGVCFs, and scaling to tens of thousands
- variant-calling/filtering-best-practices - Full VQSR/VETS and hard-filter recipes with threshold rationale
- variant-calling/deepvariant - CNN-based alternative; wins indels/difficult regions, ships platform-specific models
- variant-calling/variant-calling - bcftools pileup alternative (faster, less accurate on indels)
- variant-calling/variant-normalization - Left-align/decompose before annotation or benchmarking
- variant-calling/variant-annotation - Annotate final calls with VEP/SnpEff
- variant-calling/vcf-basics - View and query the resulting VCF
- read-alignment/bwa-alignment - Produce the aligned BAM HaplotypeCaller consumes

## References

- McKenna A, et al. The Genome Analysis Toolkit: a MapReduce framework for analyzing next-generation DNA sequencing data. *Genome Research* 20:1297-1303 (2010). DOI 10.1101/gr.107524.110.
- DePristo MA, et al. A framework for variation discovery and genotyping using next-generation DNA sequencing data. *Nature Genetics* 43:491-498 (2011). DOI 10.1038/ng.806.
- Poplin R, et al. Scaling accurate genetic variant discovery to tens of thousands of samples. *bioRxiv* 201178 (2018). DOI 10.1101/201178. PREPRINT (GATK's recommended cite for the GVCF reference-confidence + joint-genotyping methodology).
- Van der Auwera GA, et al. From FastQ Data to High-Confidence Variant Calls: The Genome Analysis Toolkit Best Practices Pipeline. *Current Protocols in Bioinformatics* 43:11.10.1-11.10.33 (2013). DOI 10.1002/0471250953.bi1110s43.
- Regier AA, et al. Functional equivalence of genome sequencing analysis pipelines enables harmonized variant calling across human genetics projects. *Nature Communications* 9:4038 (2018). DOI 10.1038/s41467-018-06159-4.
- Olson ND, et al. PrecisionFDA Truth Challenge V2: Calling variants from short and long reads in difficult-to-map regions. *Cell Genomics* 2:100129 (2022). DOI 10.1016/j.xgen.2022.100129.
- Behera S, et al. Comprehensive genome analysis and variant detection at scale using DRAGEN. *Nature Biotechnology* 43:1177-1191 (2025). DOI 10.1038/s41587-024-02382-1.
- Zhang F, et al. Ancestry-agnostic estimation of DNA sample contamination from sequence reads. *Genome Research* 30:185-194 (2020). DOI 10.1101/gr.246934.118. (VerifyBamID2.)
- Lu W, et al. CHARR efficiently estimates contamination from DNA sequencing data. *American Journal of Human Genetics* 110:2068-2076 (2023). DOI 10.1016/j.ajhg.2023.10.011.
- Laricchia KM, et al. Mitochondrial DNA variation across 56,434 individuals in gnomAD. *Genome Research* 32:569-582 (2022). DOI 10.1101/gr.276013.121.
<!-- END FILE: variant-calling/gatk-variant-calling/SKILL.md -->

## 子目录：variant-calling/joint-calling

<!-- BEGIN FILE: variant-calling/joint-calling/SKILL.md -->
---
name: bio-variant-calling-joint-calling
description: Joint genotype a cohort of per-sample gVCFs with GATK (HaplotypeCaller -ERC GVCF -> GenomicsDBImport or CombineGVCFs -> GenotypeGVCFs) or GLnexus for DeepVariant gVCFs, producing a squared-off sample-by-site genotype matrix. Use when deciding between joint genotyping and merging single-sample callsets (never bcftools merge as absent==hom-ref), choosing GenomicsDBImport vs CombineGVCFs by cohort size and memory, solving the N+1 problem so a new sample does not force re-calling everyone, understanding cohort rescue of low-coverage het sites, handling the spanning-deletion star allele and GQ/PL recomputation at the joint step, scaling to biobank cohorts by interval sharding, or picking DeepVariant+GLnexus over the GATK path on throughput. Not for single-sample calling (see variant-calling/gatk-variant-calling) or VQSR/hard-filter mechanism (see variant-calling/filtering-best-practices).
tool_type: cli
primary_tool: GATK
---

## Version Compatibility

Reference examples tested with: GATK 4.5+, GLnexus 1.4+, bcftools 1.19+

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Joint Calling

**"Joint genotype my cohort samples"** -> Combine per-sample gVCFs into a single cohort callset with consistent genotyping across all sites, enabling cohort filtering and population-level analysis.
- CLI (GATK): `gatk HaplotypeCaller -ERC GVCF` -> `gatk GenomicsDBImport` (or `CombineGVCFs`) -> `gatk GenotypeGVCFs`
- CLI (DeepVariant cohorts): `deepvariant --output_gvcf` per sample -> `glnexus_cli --config DeepVariantWGS`

## The Governing Principle: Genotype Jointly, Never Merge Callsets

Joint genotyping is not the same operation as merging single-sample VCFs, and confusing the two silently corrupts a cohort callset. Two facts drive every decision below:

- **Joint genotyping rescues low-coverage het sites.** Evidence is borrowed across samples: when one carrier has a confident variant, the cohort allele frequency raises the Bayesian prior at that exact site for every other sample, so a second sample with only 2-3 supporting reads (which per-sample would fall below threshold) is rescued into a confident genotype. This "borrowing information" mechanism is strongest at low coverage and is why a cohort callset is more sensitive than N independent callsets (DePristo 2011 *Nat Genet* 43:491; Poplin 2018 *bioRxiv* 201178).
- **Joint genotyping produces a squared-off matrix** - a genotype at every variant site for every sample. The reference-confidence `<NON_REF>` allele in each gVCF lets GenotypeGVCFs distinguish confident homozygous reference (`0/0`) from no-data/no-call (`./.`) at a site another sample carries.

The decision this forces: **never `bcftools merge` single-sample callsets as if an absent record means hom-ref.** A single-sample VCF omits sites where that sample looked reference, so a naive merge fills those cells with `./.` (missing), NOT `0/0` - a sample genuinely hom-ref and a sample never assessed become indistinguishable, and downstream allele frequencies and association tests are wrong. `./.` != `0/0` is the load-bearing distinction (see variant-calling/vcf-manipulation for merge semantics and variant-calling/vcf-basics for the genotype-field grammar). Genotype from gVCFs so every cell is filled from evidence, not assumption.

## Why Joint Calling Matters

Single-sample calling discards cross-sample evidence that is critical for accurate genotyping:

- **Statistical power from shared evidence** - A site with 2 alt reads in one sample is borderline and would typically be missed. If 50 other samples in the cohort also show 2 alt reads at that site, the evidence is overwhelming and the variant is clearly real. Joint calling aggregates this weak-per-sample signal into strong cohort-level evidence.
- **Genotype refinement via cohort priors** - Individual genotype likelihoods are combined with cohort allele frequencies as a Bayesian prior. A heterozygous call at a common variant site (AF=0.3) receives more support than the same call at a site with no other carriers. This prior dramatically improves accuracy for low-coverage samples.
- **Consistent site representation** - All samples are genotyped at the same sites, producing homozygous-reference calls where applicable. Without joint calling, a missing genotype is ambiguous: it could mean homozygous-reference or simply insufficient coverage. This "missing = reference" assumption is a common source of false negatives in downstream analysis.
- **Cohort filtering eligibility** - Variant quality score recalibration (VQSR) and its successor VETS operate on the whole-cohort variant distribution and need cohort-scale variant counts: a single deep WGS genome supplies enough, but exomes are variant-poor so the ~30-sample floor applies to exomes/panels, not WGS (VQSR's Gaussian mixture needs enough variants to fit), so filtering is inherently a cohort operation, not a per-sample one (see Step 4).

## The N+1 Problem and Why gVCFs Solve It

Naive joint calling re-visits every BAM whenever the cohort changes: adding one genome forces re-calling all N. The gVCF workflow decouples expensive per-sample **discovery** (local assembly + PairHMM likelihoods, captured once per sample in the gVCF) from cheap cohort-wide **genotyping**. Adding sample N+1 then requires only generating that one gVCF plus re-running the cheap consolidation and GenotypeGVCFs - the assembly work for the existing N is never repeated. The gVCF is the reusable intermediate; GenomicsDB workspaces can even be updated in place (`--genomicsdb-update-workspace-path`). GATK frames this as decoupling "the initial identification of potential variant sites from the genotyping step, which is the only part that really needs to be done jointly" (see variant-calling/gatk-variant-calling for per-sample gVCF generation).

## Cohort Size Decision Table

| Cohort Size | Approach | Notes |
|---|---|---|
| <100 | CombineGVCFs or GenomicsDB | Either works; CombineGVCFs is simpler to manage |
| 100-10,000 | GenomicsDB + GenotypeGVCFs | Standard GATK Best Practices; shard by chromosome |
| 10,000-100,000 | GATK Biggest Practices | Heavily sharded and parallelized across intervals |
| >100,000 | DeepVariant + GLnexus, or Hail VDS | GATK becomes unwieldy at this scale; purpose-built tools required |

## GenomicsDBImport vs CombineGVCFs

Both produce a combined object that GenotypeGVCFs consumes; they differ in how they store it and how they scale.

| | GenomicsDBImport | CombineGVCFs |
|---|---|---|
| Storage | GenomicsDB workspace on a TileDB array backend; transposes sample-centric gVCFs into a locus-centric sparse 2-D array (samples x positions) | Pure-Java hierarchical merge into a single combined gVCF |
| Scaling | Best when N is large; the locus-centric transpose is what makes per-locus genotyping fast at scale | Fails when N grows - memory-hungry and slow; recommended only as a small-cohort fallback |
| Portability | Workspace is not a plain gVCF; genotype via `gendb://` | Output is a plain gVCF, portable and inspectable |
| Incremental | Add new samples with `--genomicsdb-update-workspace-path` (the N+1 win in practice) | No incremental mode; re-run over all samples |
| Best when | >100 samples, sharded by interval, biobank scale | <100 samples, or a small family/trio where simplicity wins |

Memory landmine specific to GenomicsDBImport: the heavy lifting runs in native C/C++ (TileDB), so cap the JVM heap (`--java-options -Xmx`) at ~80-90% of RAM. Over-allocating the JVM starves the native layer and causes a native out-of-memory failure that looks unrelated to heap size.

## Workflow Overview

```
Sample BAMs
    │
    ├── HaplotypeCaller (per-sample, -ERC GVCF)
    │   └── sample1.g.vcf.gz, sample2.g.vcf.gz, ...
    │
    ├── CombineGVCFs or GenomicsDBImport
    │   └── Combine into cohort database
    │
    ├── GenotypeGVCFs
    │   └── Joint genotyping
    │
    └── VQSR or Hard Filtering
        └── Final VCF
```

## Step 1: Per-Sample gVCF Generation

```bash
# Generate gVCF for each sample
gatk HaplotypeCaller \
    -R reference.fa \
    -I sample1.bam \
    -O sample1.g.vcf.gz \
    -ERC GVCF

# With intervals (faster)
gatk HaplotypeCaller \
    -R reference.fa \
    -I sample1.bam \
    -O sample1.g.vcf.gz \
    -ERC GVCF \
    -L intervals.bed
```

### Batch Processing

```bash
# Process all samples
for bam in *.bam; do
    sample=$(basename $bam .bam)
    gatk HaplotypeCaller \
        -R reference.fa \
        -I $bam \
        -O ${sample}.g.vcf.gz \
        -ERC GVCF &
done
wait
```

## Step 2a: CombineGVCFs (Small Cohorts)

For <100 samples:

```bash
gatk CombineGVCFs \
    -R reference.fa \
    -V sample1.g.vcf.gz \
    -V sample2.g.vcf.gz \
    -V sample3.g.vcf.gz \
    -O cohort.g.vcf.gz
```

### From Sample Map

```bash
# Create sample map file
# sample1    /path/to/sample1.g.vcf.gz
# sample2    /path/to/sample2.g.vcf.gz

ls *.g.vcf.gz | while read f; do
    echo -e "$(basename $f .g.vcf.gz)\t$f"
done > sample_map.txt

# Combine with -V for each
gatk CombineGVCFs \
    -R reference.fa \
    $(cat sample_map.txt | cut -f2 | sed 's/^/-V /') \
    -O cohort.g.vcf.gz
```

## Step 2b: GenomicsDBImport (Large Cohorts)

For >100 samples, use GenomicsDB:

```bash
# Create sample map
ls *.g.vcf.gz | while read f; do
    echo -e "$(basename $f .g.vcf.gz)\t$f"
done > sample_map.txt

# Import to GenomicsDB (per chromosome for parallelism)
gatk GenomicsDBImport \
    --sample-name-map sample_map.txt \
    --genomicsdb-workspace-path genomicsdb_chr1 \
    -L chr1 \
    --reader-threads 4

# Or all chromosomes
for chr in {1..22} X Y; do
    gatk GenomicsDBImport \
        --sample-name-map sample_map.txt \
        --genomicsdb-workspace-path genomicsdb_chr${chr} \
        -L chr${chr} &
done
wait
```

### Update GenomicsDB with New Samples

```bash
gatk GenomicsDBImport \
    --genomicsdb-update-workspace-path genomicsdb_chr1 \
    --sample-name-map new_samples.txt \
    -L chr1
```

### GenomicsDB Critical Caveats

GenomicsDB is powerful but has sharp edges that can cause data loss or silent failures:

- **No sample replacement** - Existing samples cannot be updated or overwritten. Only new samples with different names can be added. To fix a sample, the entire workspace must be recreated.
- **Intervals locked at import time** - The genomic intervals specified during the initial import cannot be changed on incremental updates. Adding new regions requires reimporting from scratch.
- **Fragment accumulation** - Each incremental batch creates a new database fragment. After thousands of incremental additions, file handle exhaustion becomes likely. Run `--consolidate` periodically to merge fragments.
- **Corruption risk on failed adds** - A failed incremental import can leave the datastore in an inconsistent state. Always backup the workspace directory before running `--genomicsdb-update-workspace-path`.
- **Batch size for memory** - Set `--batch-size 50` to control memory consumption. The default is `0`, which loads ALL samples in a single batch (maximum memory); a finite batch size trades a little speed for a bounded heap, so set it explicitly for large cohorts. Larger batches load more gVCFs simultaneously and can exhaust heap space.

## Step 3: GenotypeGVCFs

### From Combined gVCF

```bash
gatk GenotypeGVCFs \
    -R reference.fa \
    -V cohort.g.vcf.gz \
    -O cohort.vcf.gz
```

### From GenomicsDB

```bash
gatk GenotypeGVCFs \
    -R reference.fa \
    -V gendb://genomicsdb_chr1 \
    -O chr1.vcf.gz

# All chromosomes
for chr in {1..22} X Y; do
    gatk GenotypeGVCFs \
        -R reference.fa \
        -V gendb://genomicsdb_chr${chr} \
        -O chr${chr}.vcf.gz &
done
wait

# Merge chromosomes
bcftools concat chr{1..22}.vcf.gz chrX.vcf.gz chrY.vcf.gz \
    -Oz -o cohort.vcf.gz
```

### What GenotypeGVCFs Recomputes (and Why It Is Not a Copy)

GenotypeGVCFs re-derives genotypes jointly from the stored per-sample PL vectors (including the `<NON_REF>` likelihood) under a Bayesian model; it does not simply copy per-sample genotypes into a wider file. Two consequences matter when reading the output:

- **GQ and PL are recomputed against the finalized cohort allele set.** Once the real ALT alleles are known cohort-wide, the `<NON_REF>` likelihood is redistributed onto them and PLs are recomputed; GQ is then the difference of the two smallest PLs. A sample's genotype/GQ in the joint VCF can therefore differ from what its single-sample gVCF implied - this is the rescue mechanism working, not a bug.
- **The allele-frequency prior comes from `--heterozygosity`** (expected theta, ~0.001 for humans; verify in-tool) and `--indel-heterozygosity`, folding the cohort allele count into each sample's posterior. `--stand-call-conf` (~30; verify in-tool) drops sites below that QUAL.

### Multiallelics and the Spanning-Deletion `*` Allele

Joint genotyping across a cohort surfaces two representation issues absent from single-sample calling:

- **`--max-alternate-alleles`** caps the ALT alleles genotyped per site (most-supported kept; confirm the default with `gatk GenotypeGVCFs --help` for the installed version). Genotyping cost scales roughly exponentially in ALT count, so GATK caps it and discourages raising it; `--max-genotype-count` similarly bounds genotype configurations. Highly multiallelic sites are also where GenotypeGVCFs can blow past very large RAM at scale.
- **The `*` spanning/overlapping-deletion allele** (VCF 4.3 reserved) appears at a variant position that falls *inside an upstream deletion carried by some samples*. It means "for a sample carrying the upstream deletion, these bases are deleted/absent" - not reference, not the local ALT. Such a sample genotypes as `*/A` or `*/*`, which correctly keeps deletion-carriers from being called spuriously hom-ref at the interior site. Downstream tools must special-case it: VEP/SnpEff have no ref/alt sequence to predict a consequence on, and `bcftools norm` decomposition often splits or filters it, so it is a frequent source of annotation surprises after joint genotyping.

### With Allele-Specific Annotations

For larger cohorts where multiallelic sites are common, allele-specific annotations allow VQSR to evaluate each allele independently rather than penalizing a good allele because a co-occurring allele is poor:

```bash
gatk GenotypeGVCFs \
    -R reference.fa \
    -V gendb://genomicsdb \
    -O cohort.vcf.gz \
    -G StandardAnnotation \
    -G AS_StandardAnnotation
```

When allele-specific annotations are present, use `-AS` mode in VariantRecalibrator and ApplyVQSR for allele-level filtering.

## Step 4: Filtering Is a Cohort Operation

Filtering the joint VCF is a whole-cohort step, not a per-sample one, and it must run *after* joint genotyping. VQSR (and its GATK successor VETS) fit a model to the cohort-wide distribution of site annotations - VQSR's Gaussian mixture needs enough variants and enough overlap with the truth resources to converge, which is why it is unreliable on a single exome or a small panel. This is the decision:

| Cohort | Filter | Why |
|---|---|---|
| Single deep WGS, or a joint cohort (~30+ exomes) | VQSR, or VETS (isolation forest, VQSR's successor) | Enough variants to fit a stable multivariate model -- one WGS genome supplies millions of sites, but exomes are variant-poor so the ~30-sample floor applies to exomes/panels, not WGS; pass `-AS` when allele-specific annotations were emitted so each allele at a multiallelic site is filtered independently |
| Single exome, gene panel, or too few variants | Hard filters | GMM will not converge on too few variants; use fixed per-annotation thresholds instead |

The full VariantRecalibrator/ApplyVQSR/VETS invocations, training resources, tranche levels, and hard-filter thresholds live in variant-calling/filtering-best-practices - this skill does not duplicate that mechanism. A minimal hard-filter fallback for a small cohort:

```bash
gatk VariantFiltration \
    -R reference.fa \
    -V cohort.vcf.gz \
    --filter-expression "QD < 2.0" --filter-name "QD2" \
    --filter-expression "FS > 60.0" --filter-name "FS60" \
    --filter-expression "MQ < 40.0" --filter-name "MQ40" \
    -O cohort.filtered.vcf.gz
```

## Batch Effects in Joint Calling

Joint genotyping mitigates most batch effects because it re-evaluates genotype likelihoods across all samples simultaneously, recalibrating quality scores against the full cohort distribution. However, certain batch effects persist through joint calling because they affect the underlying read data, not the genotyping model:

- **Different library prep protocols** - PCR-free vs PCR-based libraries produce different duplicate and error profiles
- **Different capture kits (WES)** - Exome kits target different regions; sites outside the intersection have systematically missing data in some batches
- **Significantly different coverage distributions** - 10x WGS samples mixed with 30x samples will have systematically different genotype quality at heterozygous sites
- **Different reference genome versions** - Mixing GRCh37 and GRCh38 alignments is not valid; all samples must use the same reference
- **Mixing WGS and WES** - Fundamentally different coverage profiles; off-target WES regions behave like very-low-coverage WGS

Mitigation: process all samples through an identical upstream pipeline (same aligner, same duplicate marking, same BQSR resources). If batches are unavoidable, include batch as a covariate in downstream association or differential analyses.

## When to Re-genotype

| Scenario | Action | Rationale |
|---|---|---|
| Adding new samples | Re-genotype (GenomicsDB incremental add + GenotypeGVCFs on full database) | New samples change cohort allele frequencies, improving all genotype calls |
| Changing reference genome | Full reprocess from alignment | gVCF coordinates are reference-specific |
| Updating caller version | Optional but recommended for consistency | Different caller versions may produce different quality scores; mixing versions adds noise |
| Adding new genomic intervals | Reimport from scratch | GenomicsDB intervals are locked at initial import; incremental update cannot expand them |

## DeepVariant + GLnexus Alternative

GLnexus is a scalable gVCF-merging/joint-genotyping engine (originally rocksdb-backed) that grows a cohort **incrementally** as samples are added, avoiding the full-cohort reprocessing the GenomicsDBImport + GenotypeGVCFs path requires. Yun et al. tuned its quality thresholds for DeepVariant output; the optimized presets ship in GLnexus v1.2.2+ as `DeepVariantWGS` (whole-genome) and `DeepVariantWES` (whole-exome). The original method was validated at cohort scale on ~50,000 exomes (Lin 2018 *bioRxiv* 343970). Prefer this path when DeepVariant is the caller (see variant-calling/deepvariant).

```bash
# Step 1: Run DeepVariant per sample to produce gVCFs
run_deepvariant --model_type=WGS \
    --ref=reference.fa --reads=sample.bam \
    --output_vcf=sample.vcf.gz --output_gvcf=sample.g.vcf.gz

# Step 2: Joint call with GLnexus (pre-tuned configs encode DeepVariant-tuned GQ + multiallelic handling)
# GLnexus emits BCF on stdout; pipe through bcftools to bgzip a VCF
glnexus_cli --config DeepVariantWGS --bed intervals.bed \
    sample1.g.vcf.gz sample2.g.vcf.gz ... | bcftools view - | bgzip -c > cohort.vcf.gz
```

### DeepVariant+GLnexus vs GATK GenomicsDB (representative numbers)

From the GLnexus benchmark (Yun et al. 2020 *Bioinformatics* 36:5582, GIAB 40x WGS and the 2,504-sample 1000 Genomes cohort). These are one study's figures at specific versions/coverage - treat as representative, not universal:

| Metric | DeepVariant + GLnexus | GATK (VQSR) |
|---|---|---|
| SNP F1 error | 0.07% | 1.23% |
| Indel F1 error | 1.14% | 2.92% |
| Cohort Mendelian violation rate | 1.7% | 5.0% |
| Cohort merge time, chr22 (2,504 samples) | 0.84 h | 6.83 h (GenomicsDBImport + GenotypeGVCFs) |
| Cohort gVCF footprint | 2.20 TB | 15.16 TB |

The throughput gap (GLnexus merge ~8x faster, DeepVariant gVCFs ~7x smaller on disk) is the practical reason large DeepVariant cohorts use GLnexus rather than routing DeepVariant gVCFs through GenotypeGVCFs.

## Scaling to Biobank Cohorts (tens of thousands+)

Naive GenotypeGVCFs does not scale to tens of thousands of samples: I/O and per-site QUAL computation dominate, GenotypeGVCFs can exceed very large RAM at highly multiallelic sites, and single-interval GenomicsDB workspaces plus fragment proliferation and open-file-descriptor limits become the recurring failures. The scaling levers:

- **Shard by interval.** Run one GenomicsDBImport + GenotypeGVCFs per chromosome (or finer) in parallel, then `bcftools concat`. A `--sample-name-map` file (sample<TAB>path, one per line) is mandatory at this scale - passing thousands of `-V` arguments is unmanageable and slow.
- **ReblockGVCF then GnarlyGenotyper (GATK "Biggest Practices").** ReblockGVCF drops uncalled/low-GQ alleles and re-bands reference blocks, shrinking files and merge time; GnarlyGenotyper approximates QUAL from a precomputed `QUALapprox` INFO field without iterating over all genotypes, the dominant cost saver above ~tens of thousands of samples. Broad switches production to reblocking around ~2,000 samples for cost. gnomAD v2.1 aggregated its callset in Hail and filtered with a custom random-forest model rather than VQSR (Karczewski 2020 *Nature* 581:434); later releases (v3+) ingest gVCFs directly via the Hail sparse combiner.
- **The DRAGEN / GLnexus route.** At biobank scale many projects avoid the vanilla GATK path entirely: DeepVariant + GLnexus (throughput above), or Illumina DRAGEN's integrated map-align-call engine. Verify a project's exact production pipeline rather than assuming it is GATK joint calling.

## Complete Pipeline Script

**Goal:** Run the full joint calling workflow from BAMs to filtered cohort VCF.

**Approach:** Generate per-sample gVCFs, import into GenomicsDB, joint genotype, then index and compute statistics.

```bash
#!/bin/bash
set -euo pipefail

REFERENCE=$1
OUTPUT_DIR=$2
THREADS=16

mkdir -p $OUTPUT_DIR/{gvcfs,genomicsdb,vcfs}

echo "=== Step 1: Generate gVCFs ==="
for bam in data/*.bam; do
    sample=$(basename $bam .bam)
    gatk HaplotypeCaller \
        -R $REFERENCE \
        -I $bam \
        -O $OUTPUT_DIR/gvcfs/${sample}.g.vcf.gz \
        -ERC GVCF &

    # Limit parallelism
    while [ $(jobs -r | wc -l) -ge $THREADS ]; do sleep 1; done
done
wait

echo "=== Step 2: Create sample map ==="
ls $OUTPUT_DIR/gvcfs/*.g.vcf.gz | while read f; do
    echo -e "$(basename $f .g.vcf.gz)\t$(realpath $f)"
done > $OUTPUT_DIR/sample_map.txt

echo "=== Step 3: GenomicsDBImport ==="
gatk GenomicsDBImport \
    --sample-name-map $OUTPUT_DIR/sample_map.txt \
    --genomicsdb-workspace-path $OUTPUT_DIR/genomicsdb \
    -L intervals.bed \
    --reader-threads 4

echo "=== Step 4: Joint genotyping ==="
gatk GenotypeGVCFs \
    -R $REFERENCE \
    -V gendb://$OUTPUT_DIR/genomicsdb \
    -O $OUTPUT_DIR/vcfs/cohort.vcf.gz

echo "=== Step 5: Index ==="
bcftools index -t $OUTPUT_DIR/vcfs/cohort.vcf.gz

echo "=== Statistics ==="
bcftools stats $OUTPUT_DIR/vcfs/cohort.vcf.gz > $OUTPUT_DIR/vcfs/cohort_stats.txt

echo "=== Complete ==="
echo "Joint VCF: $OUTPUT_DIR/vcfs/cohort.vcf.gz"
```

## Tips

### Memory for Large Cohorts

```bash
# Increase Java heap for GenotypeGVCFs (default 4g is often insufficient for >500 samples)
gatk --java-options "-Xmx64g" GenotypeGVCFs ...

# For GenomicsDBImport, --batch-size controls how many gVCFs are loaded simultaneously
gatk GenomicsDBImport --batch-size 50 ...
```

## Common Errors

| Symptom | Cause | Fix |
|---|---|---|
| Merged cohort has `./.` where samples are truly hom-ref; allele frequencies look wrong | `bcftools merge` of single-sample VCFs treats absent records as missing, not `0/0` | Genotype from gVCFs (GenotypeGVCFs/GLnexus) so every cell is filled from evidence; never merge single-sample callsets for a cohort matrix |
| GenomicsDBImport dies with a native/out-of-memory error despite a large `-Xmx` | Over-allocated JVM heap starves the native TileDB layer | Cap `--java-options -Xmx` at ~80-90% of RAM; the heavy lifting is native C/C++ |
| Cannot update an existing sample in GenomicsDB | GenomicsDB has no sample replacement; only new sample names can be added | Recreate the workspace to fix a sample; use `--genomicsdb-update-workspace-path` only to ADD |
| `--genomicsdb-update-workspace-path` cannot expand to new regions | Intervals are locked at initial import | Reimport from scratch to add genomic intervals |
| `*` alleles / genotypes like `*/A` break VEP/SnpEff or vanish after `bcftools norm` | Spanning-deletion symbolic allele has no ref/alt sequence to annotate | Expected after joint genotyping; special-case or split `*` records before annotation |
| VariantRecalibrator fails to converge or errors | Too few variants for the Gaussian mixture (a single exome/panel, not a single WGS) | Fall back to hard filters for exomes/panels below ~30 samples (see filtering-best-practices) |
| Fewer ALT alleles than expected at a multiallelic site | `--max-alternate-alleles` dropped the least-supported alts | Raise cautiously (cost scales ~exponentially); confirm the default with `--help` |

## Related Skills

- variant-calling/gatk-variant-calling - Single-sample HaplotypeCaller and per-sample gVCF generation (the N+1 intermediate)
- variant-calling/deepvariant - DeepVariant caller feeding the GLnexus pathway
- variant-calling/filtering-best-practices - VQSR/VETS and hard-filter mechanism (not duplicated here)
- variant-calling/vcf-manipulation - Merge/subset semantics and why single-sample merge != joint genotyping
- variant-calling/vcf-basics - Genotype-field grammar (`./.` vs `0/0`, the `*` allele)
- population-genetics/plink-basics - Population analysis of joint calls
- workflows/fastq-to-variants - End-to-end germline pipeline

## References

- DePristo MA, Banks E, Poplin R, et al. A framework for variation discovery and genotyping using next-generation DNA sequencing data. *Nature Genetics* 43(5):491-498 (2011). DOI 10.1038/ng.806.
- Poplin R, Ruano-Rubio V, DePristo MA, et al. Scaling accurate genetic variant discovery to tens of thousands of samples. *bioRxiv* 201178 (2018). DOI 10.1101/201178. Preprint; GATK's recommended cite for the GVCF/reference-confidence + joint-genotyping methodology.
- Yun T, Li H, Chang P-C, Lin MF, Carroll A, McLean CY. Accurate, scalable cohort variant calls using DeepVariant and GLnexus. *Bioinformatics* 36(24):5582-5589 (2020). DOI 10.1093/bioinformatics/btaa1081.
- Lin MF, Rodeh O, Penn J, et al. GLnexus: joint variant calling for large cohort sequencing. *bioRxiv* 343970 (2018). DOI 10.1101/343970. Preprint (original GLnexus method).
- Karczewski KJ, Francioli LC, Tiao G, et al. The mutational constraint spectrum quantified from variation in 141,456 humans. *Nature* 581(7809):434-443 (2020). DOI 10.1038/s41586-020-2308-7.
<!-- END FILE: variant-calling/joint-calling/SKILL.md -->

## 子目录：variant-calling/structural-variant-calling

<!-- BEGIN FILE: variant-calling/structural-variant-calling/SKILL.md -->
---
name: bio-variant-calling-structural-variant-calling
description: Call structural variants (>=50 bp deletions, insertions, inversions, duplications, translocations) from short- or long-read data by reconstructing four orthogonal signals (discordant pairs, split reads via the SA tag, read depth, local assembly). Covers Manta, DELLY, LUMPY/smoove, GRIDSS2, SvABA for short reads and Sniffles2, cuteSV, pbsv, dipcall/PAV for long reads, each mapped to the signals it fuses and the blind spots that follow. Use when choosing an SV caller from its signal set and failure modes, decoding the SVLEN-sign / symbolic-vs-BND / CIPOS VCF representation minefield, force-genotyping a cohort matrix instead of unioning discovery VCFs, merging populations with sequence-aware Truvari vs position-only SURVIVOR, parameterizing a Truvari benchmark, or deciding when short-read insertion recall forces a switch to long reads. Not for pure copy-number dosage (see copy-number/cnvkit-analysis).
tool_type: cli
primary_tool: manta
---

## Version Compatibility

Reference examples tested with: Manta 1.6+, DELLY 1.2+, GRIDSS 2.13+, smoove 0.2+, SvABA 1.1+, bcftools 1.19+, samtools 1.19+, SURVIVOR 1.0.7+, Truvari 4.0+, Sniffles2 2.2+, cuteSV 2.0+

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

Note: DELLY 1.x and Truvari 4.x renamed flags/defaults from earlier lines (Truvari's alt-sequence-similarity param was `--pctsim`, now `--pctseq`); always confirm against `--help` before trusting old muscle memory.

# Structural Variant Calling

**"Call structural variants from my WGS data"** -> Reconstruct large rearrangements (DEL, INS, INV, DUP, BND) that no single read reports directly, by fusing evidence from how alignments break, disagree, or deviate from expectation.
- CLI (short read): `configManta.py` (Manta), `delly call`, `smoove call` (LUMPY), `gridss`, `svaba run`
- CLI (long read): `sniffles`, `cuteSV`, `pbsv`, `dipcall.kit`/`pav` (assembly-based)

## The governing principle: SV discovery is signal reconstruction, not base-calling

An SV caller is not a pileup genotyper. SVs are never observed directly by a read; they are *inferred* from four orthogonal signals, and each caller fuses only a subset. Its blind spots follow directly from which signals it omits (Mahmoud 2019 *Genome Biol* 20:246 is the canonical signal-to-blind-spot map).

1. Discordant read pairs (RP) - a pair whose insert size or orientation departs from the library distribution. A DEL inflates the apparent insert; a tandem DUP gives everted (`+/+`/`-/-`) pairs; an INV flips one strand; an interchromosomal event splits mates across chromosomes. RP never sees the junction base, so it localizes a breakpoint only to fragment-size uncertainty (~+/-300-500 bp).
2. Split reads / soft-clips (SR) - one read aligning in two pieces to non-contiguous positions, recorded via the BAM SA (supplementary alignment) tag. The clip point IS the breakpoint at base resolution (~+/-0-10 bp). Requires a read that straddles the junction with unique anchor on both sides - impossible inside a repeat longer than the read or for an INS larger than (read length - anchor).
3. Read depth (RD) - copy-number shifts local coverage (het DEL ~0.5x, DUP ~1.5x, hom DEL ~0). The ONLY signal for large CNVs whose breakpoints fall in unmappable repeats; blind to balanced events (INV, balanced BND) that leave dosage unchanged. Resolution is bin-size-limited (100 bp-1 kb), the worst of any signal.
4. Local assembly (AS) - reconstruct the breakpoint-spanning contig de novo from clipped/discordant reads, then realign it. Recovers the exact junction sequence, microhomology, and inserted bases; resolves events no single read spans. Most powerful and most expensive; separates GRIDSS/Manta/SvABA from LUMPY.

| Caller | RP | SR | RD | Assembly | Primary blind spot |
|--------|----|----|----|----------|--------------------|
| Manta | Yes | Yes | filter/score only | Yes (targeted, breakend-local) | Large INS beyond breakend-local contig; balanced events in repeats |
| DELLY | Yes | Yes (SR realign for refinement) | Yes (`delly cnv` module) | No de novo | INS (only small, SR-anchored); precision below assembly callers |
| LUMPY / smoove | Yes | Yes | No | No | INS entirely (no representation for novel inserted sequence) |
| GRIDSS2 | Yes | Yes | via GRIPSS/PURPLE downstream | Yes (genome-wide positional de Bruijn graph) | Pure RD-only CNVs with no junction reads; long-repeat interiors |
| SvABA | Yes | Yes | No | Yes (genome-wide SGA local assembly) | Large INS still assembly-limited; multi-kb DEL/DUP rely on RP linkage |
| CNVnator | No | No | Yes (mean-shift on RD bins) | No | Everything balanced; no breakpoint resolution; no small SVs |

### The real tradeoff is sensitivity vs breakpoint resolution (not vs specificity)

- RP-heavy calling maximizes SENSITIVITY (a pair spanning a junction is easy, works at low depth) but yields IMPRECISE breakpoints (+/-hundreds bp, `CIPOS=-289,301`).
- SR / assembly calling maximizes RESOLUTION (base-precise, `CIPOS=0,0`) but LOSES sensitivity wherever a read cannot cleanly straddle the junction (repeats, low depth, large INS).

Below ~30x the SR signal thins (fewer reads straddle any junction) and callers silently drift into the low-resolution RP-only regime. A caller demanding SR confirmation reports beautiful breakpoints and misses the repeat-mediated events that matter clinically; a caller accepting RP-only calls finds more but hands back wide confidence intervals.

## Caller selection

| Caller | Signals fused | Best when | Fails / do NOT use when |
|--------|---------------|-----------|--------------------------|
| Manta | RP+SR+targeted AS | Default germline/somatic; fastest assembly-capable caller (sub-hour on 30x) | WES/panel WITHOUT `--exome` (high-depth filter silently drops true SVs); large INS beyond local assembly |
| DELLY | RP+SR (+RD CNV module) | Cohorts (site-list-then-regenotype); INV/BND | General large-INS calling; needs base-precise breakpoints in repeats |
| smoove (LUMPY) | RP+SR (probabilistic) | Simple, sane-default germline pipeline at low-moderate depth | ANY INS-critical pipeline (structurally zero INS recall) |
| GRIDSS2 | RP+SR+genome-wide AS | Highest precision; somatic; single-breakends (viral integration, centromeric) | Using raw VCF as a callset (it is a breakpoint GRAPH - run GRIPSS/PURPLE/LINX); need speed |
| SvABA | RP+SR+genome-wide AS | The 20-300 bp indel/SV "twilight zone"; templated-insertion detection in cancer | Large balanced events; when Manta speed suffices |
| CNVnator / CNVpytor | RD only | Dosage CNVs with breakpoints in unmappable repeats | Balanced SVs; any breakpoint-precision need (see copy-number/cnvkit-analysis) |
| Sniffles2 / cuteSV / pbsv | long-read alignment | INS, repeat-mediated SVs, phased SVs, population `.snf` merging | Only short reads available |

Consensus recipe: run DELLY + Manta + SvABA + GRIDSS2 (the latter GRIPSS-filtered first, since its raw VCF is a breakpoint graph, not a callset) and require >=2/4 agreement - singletons are enriched for false positives, so intersection trades a little recall for a large precision gain. Caveat: this caps INS recall (LUMPY-class blind spots drag the intersection down); for INS-heavy work prefer one assembly caller + a graph genotyper, or long reads. Methods evolve - verify current ensemble practice against tool docs before committing.

## SV detection limits by platform

| SV type | Short read | Long read | Key limitation |
|---------|-----------|-----------|----------------|
| Deletion | Good (RP+SR) | Excellent | Short reads miss DELs buried in repeats |
| Duplication | Moderate (RP+RD) | Good | Tandem vs dispersed unreliable with short reads |
| Inversion | Moderate (RP) | Good | Breakpoints in repeats cause false negatives |
| Insertion | Poor (~30-50% recall) | Excellent (~90%+) | Physics limit: no short read spans an INS > read length |
| Translocation | Moderate (discordant) | Good | High FP rate near centromeres/telomeres |
| Complex/nested | Poor | Good (assembly) | Overlapping SVs confound short-read signals |

Insertions are a physics limit, not a tuning failure. Placing and sizing an INS requires reads spanning both junctions plus the novel bases; when the INS exceeds read length (Illumina 150 bp), no read spans it and the inserted sequence is unrecoverable without assembly - and short-read assembly fails again when the insertion is a repeat (mobile element, VNTR). GIAB HG002 Tier 1 contains MORE INS than DEL (7,281 INS vs 5,464 DEL >=50 bp; Zook 2020 *Nat Biotechnol* 38:1347), yet INS are the hardest short-read class. Ebert 2021 (*Science* 372:eabf7117) found 68% of 107,590 assembly-discovered SVs were missed by short reads. Do NOT benchmark short-read INS against a long-read truth set and blame the caller - ~30-50% is the ceiling by construction.

## The VCF representation minefield

The VCF spec represents SVs three ways and callers disagree on all three - this is where careful people lose days.

- SVTYPE - the class (DEL/INS/DUP/INV/BND).
- END (INFO) - the other breakpoint on the same chromosome. POS is the last unaffected anchor base, so a DEL at POS=1000, END=2000 removes 1001-2000. Off-by-one here corrupts every length calc. (VCF 4.4 began deprecating INFO/END for symbolic alleles; bcftools/GATK still emit and consume the classic field.)
- SVLEN - SIGNED length: DEL is NEGATIVE, INS/DUP positive by historical convention (Manta, DELLY follow it; some tools emit absolute values). NEVER filter on raw SVLEN without `ABS()` or a naive `SVLEN >= 50` drops every deletion.
- CIPOS / CIEND - confidence intervals encoding the RP-vs-SR resolution story: an SR-resolved breakpoint is `CIPOS=0,0`, an RP-only one is `CIPOS=-289,301`. This is the ground truth for "how much do I trust this breakpoint" and exactly what a population merger must respect.
- IMPRECISE (flag) - set when the breakpoint is RP/depth-derived, not junction-resolved; its absence implies PRECISE. An all-IMPRECISE callset cannot be merged tightly.

Breakend (BND) notation - the part everyone gets wrong. A rearrangement whose two sides are not a simple same-chromosome span is written as PAIRED BND records linked by `MATEID`, with an ALT string whose bracket direction encodes the join orientation:
```
2   321681  bnd_V  T  ]13:123456]T   MATEID=bnd_U
13  123456  bnd_U  A  A[2:321681[    MATEID=bnd_V
```
One reciprocal translocation is 2 BND records; chromothripsis is a graph of dozens. The SAME biological inversion can appear as `<INV>` in Manta, as 2+ BND records in GRIDSS, and as a DEL+DUP artifact pair in a naive RD caller - a merger that does not understand this triple-counts or drops the event.

## Manta

Manta builds a genome-wide breakend association graph from RP+SR, then does targeted local assembly of each candidate breakend and realigns the contig for base-resolution breakpoints. `candidateSmallIndels.vcf.gz` is the recommended indel-candidate input for Strelka2.

```bash
configManta.py --bam sample.bam --referenceFasta reference.fa --runDir manta_run
manta_run/runWorkflow.py -j 8
# results/variants/: diploidSV.vcf.gz (germline), candidateSV.vcf.gz (unscored superset),
#   candidateSmallIndels.vcf.gz (Strelka2 input)
```

WES/panel and RNA need explicit modes - default depth filtering assumes WGS-uniform coverage and silently drops true SVs at high-depth targeted loci:
```bash
# --exome disables the high-depth filter; --rna handles split alignments across splice junctions
configManta.py --bam sample.bam --referenceFasta reference.fa --exome \
    --callRegions regions.bed.gz --runDir manta_exome
```

Tumor-normal somatic mode adds `somaticSV.vcf.gz`:
```bash
configManta.py --tumorBam tumor.bam --normalBam normal.bam \
    --referenceFasta reference.fa --runDir manta_somatic
manta_somatic/runWorkflow.py -j 8
```

## DELLY

BCF output by default; the scalable cohort pattern is site-list-then-regenotype (Section below), not one big multi-BAM call.

```bash
delly call -g reference.fa -o sv_calls.bcf sample.bam
bcftools view sv_calls.bcf > sv_calls.vcf

# Per-type calling (INS recovers only small, SR-anchored insertions)
delly call -t DEL -g ref.fa -o deletions.bcf sample.bam   # also DUP, INV, BND, INS

# Somatic: call tumor+normal, then classify with a sample sheet
delly call -g reference.fa -o svs.bcf tumor.bam normal.bam
printf 'tumor\ttumor\nnormal\tcontrol\n' > samples.tsv
delly filter -f somatic -o somatic_svs.bcf -s samples.tsv svs.bcf
```

## smoove (LUMPY, with genotyping + depth annotation)

Nobody runs raw `lumpyexpress` anymore. smoove wraps LUMPY + svtyper + duphold with sane defaults and a cohort workflow. duphold annotates each DEL/DUP with three depth fold-changes: over the whole event (`DHFC`), over GC/mappability-matched bins (`DHBFC`), and over the immediate flanks (`DHFFC`) - a cheap, high-value filter for RP-only calls lacking depth support. duphold's own recommended false-positive filters are `DHFFC < 0.7` for deletions (flanking fold-change, its most robust metric) and `DHBFC > 1.3` for duplications.

```bash
smoove call --name sample --fasta reference.fa --outdir smoove_out -p 8 sample.bam
# smoove_out/sample-smoove.genotyped.vcf.gz

# Filter RP-only false positives that lack depth corroboration (duphold's recommended fields)
bcftools view -i '(SVTYPE!="DEL" && SVTYPE!="DUP") || (SVTYPE="DEL" && FMT/DHFFC<0.7) || (SVTYPE="DUP" && FMT/DHBFC>1.3)' \
    smoove_out/sample-smoove.genotyped.vcf.gz > smoove.dhfc.vcf
```

## GRIDSS: the raw VCF is a breakpoint graph, not a callset

GRIDSS2 is the only short-read caller doing genome-wide break-end assembly (positional de Bruijn graph) before calling, and the only one reporting single break-ends (SGL) where just one side maps - viral integrations, centromeric/telomeric junctions. But its raw VCF is deliberately noisy low-level breakpoints; it is NOT usable directly. The intended chain is GRIDSS -> GRIPSS (filtering/linkage) -> PURPLE (purity/ploidy/copy-number) -> LINX (interprets breakpoints into chromothripsis, breakage-fusion-bridge, fusions).

```bash
# --assembly must be a writable path; reference needs .fai and .dict
gridss --reference reference.fa --output gridss_raw.vcf \
    --assembly gridss_assembly.bam --threads 8 sample.bam

# Somatic: GRIDSS2 tumor+normal, then GRIPSS filtering
gridss --reference reference.fa --output gridss_raw.vcf --assembly asm.bam \
    --labels normal,tumor --threads 8 normal.bam tumor.bam
# GRIPSS (launched as `java -jar gripss.jar` in practice) also requires PON inputs
# (-pon_sgl_file, -pon_sv_file, -known_hotspot_file); confirm the full flag set with its docs.
gripss -sample tumor -reference normal -ref_genome reference.fa \
    -ref_genome_version 38 -pon_sgl_file sgl.pon -pon_sv_file sv.pon \
    -vcf gridss_raw.vcf -output_dir gripss_out/
```

## Genotyping is not discovery (do NOT union discovery VCFs into a population matrix)

Discovery answers "is there an SV here, and what/where?"; genotyping answers "what is each sample's GT (0/0, 0/1, 1/1) here?". These are different statistical problems. A sample recorded 0/0 in a discovery-VCF union may simply not have had that event DISCOVERED in it - a false "missing", not a true reference genotype. Building an allele-frequency-quality cohort matrix requires FORCE-GENOTYPING every sample at every discovered site.

Correct cohort workflow: discover per-sample -> merge to a non-redundant SITE list -> re-genotype ALL samples at ALL sites -> merge genotypes.

| Genotyper | Model | Use when |
|-----------|-------|----------|
| svtyper (in SpeedSeq, Chiang 2015) | Bayesian RP+SR at known breakpoints | LUMPY/smoove sites; DEL/DUP/INV/BND (NOT insertions) |
| Paragraph (Chen 2019) | realign reads to a per-SV sequence graph (ref+alt paths) | Modern short-read choice; genotypes INS (alt path contains the inserted bases) |
| GraphTyper2 (Eggertsson 2019) | joint SNV+SV over a pangenome graph | N in the tens of thousands (genotyped 49,962 Icelanders) |

```bash
# DELLY's native squared-off pattern: per-sample call -> merge SITES -> regenotype at sites
delly call -g ref.fa -o s1.bcf s1.bam        # ... one per sample
delly merge -o sites.bcf s1.bcf s2.bcf s3.bcf
delly call -g ref.fa -v sites.bcf -o s1.geno.bcf s1.bam   # regenotype each at the union sites
bcftools merge -m id -Ob -o cohort.bcf s1.geno.bcf s2.geno.bcf s3.geno.bcf
```

## Population merging: the merge parameters ARE the result

"The same SV" across samples/callers is a fuzzy concept because breakpoints disagree by CIPOS margins. Position-only merging inflates allele frequency by up to 2.2x versus sequence-aware merging, because it collapses distinct nearby alleles into one (English 2022 *Genome Biol* 23:271). For any AF-dependent analysis (constraint, association, catalogs), always report the merger and its parameters.

| Merger | Matching | Use when |
|--------|----------|----------|
| SURVIVOR (Jeffares 2017) | position + type + strand agreement, min-callers; NOT sequence-aware | Fast caller-consensus on ONE sample; 1000 bp `max_dist` cheerfully merges two different 300 bp DELs 800 bp apart |
| Jasmine (Kirsche 2023) | (breakpoint, length) proximity graph via KD-tree + constrained Kruskal | Long-read cohort merging at population scale |
| Truvari collapse (English 2022) | SEQUENCE-aware (refdist + size + alt-sequence similarity) | Any AF work or population catalog where allelic diversity must be preserved |

```bash
# SURVIVOR: max_dist=1000 min_callers=2 type_agree=1 strand_agree=1 est_dist=0 min_size=50
ls manta.vcf delly.vcf gridss.vcf smoove.vcf > vcf_list.txt
SURVIVOR merge vcf_list.txt 1000 2 1 1 0 50 merged.vcf   # single-sample caller consensus only
```

## Benchmarking: an SV F1 is meaningless without its Truvari parameters

Every SV F1/recall/precision figure is a function of the matching parameters; papers routinely report incomparable numbers. A Truvari `bench` true positive must match a truth variant under ALL of:

| Flag | Default | What loosening it does |
|------|---------|------------------------|
| `--refdist` | 500 | larger -> RP-only IMPRECISE calls start matching |
| `--pctsize` | 0.70 | lower -> size-sloppy calls pass (reciprocal size similarity) |
| `--pctseq` (was `--pctsim`) | 0.70 | `0` disables alt-sequence checking entirely - the quiet trick that inflates short-read INS scores |
| `--sizemin` / `--sizemax` | 50 / - | choosing the window can hide a caller weak at one size class |

```bash
# Report EVERY parameter; --pctseq 0 would make this uninterpretable
truvari bench -b truth.vcf.gz -c calls.vcf.gz -o bench_out/ --passonly \
    --refdist 500 --pctsize 0.70 --pctseq 0.70 --sizemin 50
```

Three escalating bars are routinely conflated: (1) event detection (loose, RP-only callers pass), (2) breakpoint accuracy (tight `--refdist`, only SR/assembly pass; matters at exon/splice boundaries), (3) genotype accuracy (add genotype-aware comparison; a caller can detect an event yet call het-as-hom, fatal for Mendelian work). Also stratify by region: run GIAB-CMRG (Wagner 2022 *Nat Biotechnol* 40:672), not just Tier 1 - CMRG covers the medically relevant repetitive genes Tier 1 EXCLUDES, and false duplications in GRCh37/38 (e.g. *CBS*, *KCNE1*) cause reference-specific misses that masking raised from 8% to 100% recall.

## Filter and annotate

```bash
bcftools view -i 'ABS(SVLEN) >= 50' svs.vcf > svs.min50.vcf   # ABS() is mandatory (DEL sign); see examples/svlen_sign_filter.py
bcftools view -i 'SVTYPE="DEL"' svs.vcf > deletions.vcf        # or INS/INV/DUP/BND
bcftools view -f PASS svs.vcf > svs.pass.vcf

AnnotSV -SVinputFile svs.vcf -genomeBuild GRCh38 -outputFile annotated_svs
# gene overlap, DGV/gnomAD-SV population AF, ClinVar pathogenicity
```

## Long reads: near-direct observation

A long read (HiFi ~15-25 kb, ONT tens of kb to Mb) physically spans the SV and both flanks in one molecule, converting inference-over-fragments into near-direct observation: INS become trivial (the read carries the inserted bases), repeat-mediated SVs resolve, and heterozygous variants on one read are natively phased. Switch to long reads when INS/complex/repeat SVs or phased haplotyping matter more than per-sample cost.

| Caller | Approach | Best for |
|--------|----------|----------|
| Sniffles2 (Smolka 2024) | signature + per-sample `.snf` population merge | ONT/HiFi general; mosaic/low-VAF SVs; linear-in-N cohorts |
| cuteSV (Jiang 2020) | signature clustering + refinement | Highest recall on noisy ONT |
| pbsv | official PacBio, tandem-repeat-aware | HiFi (pair with pbmm2 alignments) |
| SVIM (Heller 2019) | reports origin AND destination of duplications | tandem-vs-interspersed DUP discrimination |
| dipcall (Li 2018) / PAV (Ebert 2021) | assembly-vs-reference from phased haplotype assemblies | highest-quality callsets and truth sets |
| Severus (Keskus 2025) | phased somatic breakpoint graph | complex somatic rearrangements from long reads |

```bash
# minimap2/pbmm2 -> sort -> caller. Sniffles2 population design: per-sample .snf, then combine
sniffles --input sample.bam --reference reference.fa --snf sample.snf
sniffles --input s1.snf s2.snf s3.snf --vcf population.vcf   # combine scales linearly in N
```

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| Default Manta on WES/panel loses true SVs | high-depth filter assumes WGS-uniform coverage | add `--exome` |
| Cohort "0/0" genotypes wrong; AF too low | took a UNION of discovery VCFs | force-genotype at merged sites (Paragraph/GraphTyper2/`delly -v`) |
| AF up to 2.2x too high vs another catalog | position-only merge (SURVIVOR-1000) | use sequence-aware Truvari for AF work |
| `ABS(SVLEN)>=50` filter drops all deletions | filtered raw SVLEN (DEL is negative) | always wrap in `ABS()` |
| Zero INS recall | LUMPY/smoove has no INS representation | use an assembly caller or long reads |
| Short-read INS recall "only ~40%" | benchmarked vs a long-read truth set | physics limit, not caller fault; ~30-50% is the ceiling |
| GRIDSS raw VCF looks like noise | it is a breakpoint GRAPH, not a callset | run GRIPSS -> PURPLE -> LINX |
| `-H 1` haplotype consensus is chimeric | genotypes were unphased | phase first (see variant-calling/consensus-sequences) |
| Truvari F1 not reproducible | reported without parameters | state refdist/pctsize/pctseq/sizemin and whether GT was compared |

## Related Skills

- copy-number/cnvkit-analysis - read-depth CNV detection for dosage changes with breakpoints in unmappable repeats (complements junction-based SV callers)
- long-read-sequencing/structural-variants - full long-read SV pipelines (Sniffles2, cuteSV, pbsv, assembly-based)
- variant-calling/consensus-sequences - applying variants to a reference; phasing before `-H` haplotype extraction; why symbolic SVs are not consensus-able
- variant-calling/vcf-manipulation - view, query, and reshape SV VCFs
- variant-calling/filtering-best-practices - general VCF filtering principles applicable to SV callsets
- variant-calling/variant-annotation - functional annotation of SVs (gene overlap, population AF, pathogenicity)
- alignment-files/alignment-filtering - BAM preparation and quality filtering before SV calling

## References

- Mahmoud M, Gobet N, Cruz-Davalos DI, Mounier N, Dessimoz C, Sedlazeck FJ. Structural variant calling: the long and the short of it. 2019 *Genome Biology* 20:246.
- Chen X, Schulz-Trieglaff O, Shaw R, Barnes B, Schlesinger F, Kallberg M, Cox AJ, Kruglyak S, Saunders CT. Manta: rapid detection of structural variants and indels for germline and cancer sequencing applications. 2016 *Bioinformatics* 32:1220-1222.
- Rausch T, Zichner T, Schlattl A, Stutz AM, Benes V, Korbel JO. DELLY: structural variant discovery by integrated paired-end and split-read analysis. 2012 *Bioinformatics* 28:i333-i339.
- Layer RM, Chiang C, Quinlan AR, Hall IM. LUMPY: a probabilistic framework for structural variant discovery. 2014 *Genome Biology* 15:R84.
- Cameron DL, Schroder J, Penington JS, Do H, Molania R, Dobrovic A, Speed TP, Papenfuss AT. GRIDSS: sensitive and specific genomic rearrangement detection using positional de Bruijn graph assembly. 2017 *Genome Research* 27:2050-2060.
- Cameron DL, Baber J, Shale C, Valle-Inclan JE, Besselink N, van Hoeck A, et al. GRIDSS2: comprehensive characterisation of somatic structural variation using single breakend variants and structural variant phasing. 2021 *Genome Biology* 22:202.
- Wala JA, Bandopadhayay P, Greenwald NF, O'Rourke R, Sharpe T, Stewart C, et al. SvABA: genome-wide detection of structural variants and indels by local assembly. 2018 *Genome Research* 28:581-591.
- Abyzov A, Urban AE, Snyder M, Gerstein M. CNVnator: an approach to discover, genotype, and characterize typical and atypical CNVs from family and population genome sequencing. 2011 *Genome Research* 21:974-984.
- Chiang C, Layer RM, Faust GG, Lindberg MR, Rose DB, Garrison EP, Marth GT, Quinlan AR, Hall IM. SpeedSeq: ultra-fast personal genome analysis and interpretation. 2015 *Nature Methods* 12:966-968. (introduces the svtyper genotyper)
- Chen S, Krusche P, Dolzhenko E, Sherman RM, Petrovski R, Schlesinger F, et al. Paragraph: a graph-based structural variant genotyper for short-read sequence data. 2019 *Genome Biology* 20:291.
- Eggertsson HP, Kristmundsdottir S, Beyter D, Jonsson H, Skuladottir A, Hardarson MT, et al. GraphTyper2 enables population-scale genotyping of structural variation using pangenome graphs. 2019 *Nature Communications* 10:5402.
- Jeffares DC, Jolly C, Hoti M, Speed D, Shaw L, Rallis C, Balloux F, Dessimoz C, Bahler J, Sedlazeck FJ. Transient structural variations have strong effects on quantitative traits and reproductive isolation in fission yeast. 2017 *Nature Communications* 8:14061. (introduces SURVIVOR)
- Kirsche M, Prabhu G, Sherman R, Ni B, Battle A, Aganezov S, Schatz MC. Jasmine and Iris: population-scale structural variant comparison and analysis. 2023 *Nature Methods* 20:408-417.
- English AC, Menon VK, Gibbs RA, Metcalf GA, Sedlazeck FJ. Truvari: refined structural variant comparison preserves allelic diversity. 2022 *Genome Biology* 23:271.
- Zook JM, Hansen NF, Olson ND, Chapman L, Mullikin JC, Xiao C, et al. A robust benchmark for detection of germline large deletions and insertions. 2020 *Nature Biotechnology* 38:1347-1355. (GIAB HG002 SV Tier 1)
- Wagner J, Olson ND, Harris L, McDaniel J, Cheng H, Fungtammasan A, et al. Curated variation benchmarks for challenging medically relevant autosomal genes. 2022 *Nature Biotechnology* 40:672-680. (GIAB-CMRG)
- Li H, Bloom JM, Farjoun Y, Fleharty M, Gauthier L, Neale B, MacArthur D. A synthetic-diploid benchmark for accurate variant-calling evaluation. 2018 *Nature Methods* 15:595-597. (dipcall/syndip)
- Ebert P, Audano PA, Zhu Q, Rodriguez-Martin B, Porubsky D, Bonder MJ, et al. Haplotype-resolved diverse human genomes and integrated analysis of structural variation. 2021 *Science* 372:eabf7117. (PAV; 68% of SVs missed by short reads)
- Sedlazeck FJ, Rescheneder P, Smolka M, Fang H, Nattestad M, von Haeseler A, Schatz MC. Accurate detection of complex structural variations using single-molecule sequencing. 2018 *Nature Methods* 15:461-468. (Sniffles v1 + NGMLR)
- Smolka M, Paulin LF, Grochowski CM, Horner DW, Mahmoud M, Behera S, et al. Detection of mosaic and population-level structural variants with Sniffles2. 2024 *Nature Biotechnology*. doi:10.1038/s41587-023-02024-y.
- Jiang T, Liu Y, Jiang Y, Li J, Gao Y, Cui Z, et al. Long-read-based human genomic structural variation detection with cuteSV. 2020 *Genome Biology* 21:189.
- Heller D, Vingron M. SVIM: structural variant identification using mapped long reads. 2019 *Bioinformatics* 35:2907-2915.
- Keskus AG, et al. Severus detects somatic structural variation and complex rearrangements in cancer genomes using long-read sequencing. 2025 *Nature Biotechnology*. doi:10.1038/s41587-025-02618-8.
- pbsv - PacBio structural variant caller (no dedicated publication): github.com/PacificBiosciences/pbsv
- smoove (no dedicated publication): github.com/brentp/smoove
- Pedersen BS, Quinlan AR. Duphold: scalable, depth-based annotation and curation of high-confidence structural variant calls. 2019 *GigaScience* 8(4):giz040. (source of the DHFFC<0.7 / DHBFC>1.3 depth filters)
<!-- END FILE: variant-calling/structural-variant-calling/SKILL.md -->

## 子目录：variant-calling/variant-annotation

<!-- BEGIN FILE: variant-calling/variant-annotation/SKILL.md -->
---
name: bio-variant-annotation
description: Annotates VCF variants with functional consequences, population frequencies, and pathogenicity scores using bcftools annotate/csq, Ensembl VEP, SnpEff, and ANNOVAR. Use when deciding which annotation engine and version to pin, which transcript set to report on (RefSeq vs Ensembl vs MANE Select/Plus Clinical, and why VEP --pick is dangerous clinically), how to reconcile HGVS 3'-shifting with VCF left-alignment, which consequence plus NMD status governs PVS1 eligibility, which single calibrated predictor to use for PP3/BP4 (REVEL, AlphaMissense, CADD, SpliceAI deltas), or how to read gnomAD v2/v3/v4 grpmax filtering allele frequency instead of one global AF cutoff. Not for ACMG combining rules or final classification (see variant-calling/clinical-interpretation).
tool_type: mixed
primary_tool: VEP
---

## Version Compatibility

Reference examples tested with: bcftools 1.19+, VEP 110+, SnpEff 5.2+, ANNOVAR 2020Jun07+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `<tool> --version` then `<tool> --help` to confirm flags
- Note: SnpEff and SnpSift use single-dash `-version`, not `--version`

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

Note: gnomAD v2 is GRCh37; v3/v4 are GRCh38. MANE transcripts exist only on GRCh38. Confirm the build of every annotation source matches the VCF before annotating.

# Variant Annotation

**"Annotate my variants with functional and clinical information"** -> Map each variant onto a transcript model, classify its coding/splice consequence, and attach population frequency and pathogenicity evidence.
- CLI: `vep` (Ensembl), `snpEff`/`SnpSift`, `table_annovar.pl` (ANNOVAR), `bcftools csq`/`annotate`
- Python: `cyvcf2` to parse VEP CSQ / SnpEff ANN strings; `bcftools +split-vep` to flatten them

## The governing principle: annotation is not deterministic

A variant's consequence is not a property of the variant. It is a property of the tuple (variant, transcript model, engine, engine version, parameter set). Change any element and the reported consequence, the HGVS string, and downstream the ACMG PVS1 eligibility can all change. The single most damaging naive belief in clinical genomics is that a VCF line has one true annotation. It does not. On any discordant result the first question is never "what does the variant do" but "which transcript and which tool+version produced that call."

The decision is therefore NOT to find the "right" tool. It is to PIN every axis and record it on the report: genome build, transcript set (prefer MANE Select on GRCh38), engine + version, predictor + version, gnomAD version. Reproducibility comes from pinning, not from picking. Never compare a variant annotated on RefSeq to one annotated on Ensembl.

Three independent axes of non-determinism: the transcript SET (RefSeq vs Ensembl/GENCODE vs MANE), the transcript-SELECTION heuristic (canonical, worst-consequence, `--pick`, MANE Select), and the ENGINE itself (VEP/SnpEff/ANNOVAR encode different splice-region widths, up/downstream windows, HGVS-shifting rules, and consequence-severity orderings). Discordance concentrates in indels, splice-region, and multi-transcript genes; loss-of-function calls that drive PVS1 are among the least concordant across engines (McLaren 2016 *Genome Biol* 17:122; Cingolani 2012 *Fly* 6(2):80-92; Wang 2010 *Nucleic Acids Res* 38(16):e164).

## Normalize before annotation, and never hand-derive HGVS from POS

Normalization is mandatory: the same variant represented differently produces different annotations.

```bash
# -m-any splits multiallelic records to biallelic so each ALT gets its own annotation
bcftools norm -f reference.fa -m-any input.vcf.gz -Oz -o normalized.vcf.gz
```

The HGVS 3'-rule vs VCF left-align clash is a genuine, still-live trap. VCF normalization requires indels **left-aligned** (most 5' on the forward genomic strand; Tan 2015 *Bioinformatics* 31(13):2202-2204). HGVS mandates the **opposite**: the 3'-rule places an indel in a repeat at the most 3' position with respect to the **transcript**. For a plus-strand gene, transcript-3' is the rightmost genomic position, the opposite end from VCF left-alignment; for a minus-strand gene the two can coincide by accident of strand. Net effect: a correctly left-aligned VCF POS and a correct HGVS `c.` string for the same indel can point to different repeat units.

Rules:
- Left-align + normalize the VCF BEFORE annotation (idempotent representation for matching/merging).
- Rely on the engine's HGVS generator to apply the transcript 3'-shift (VEP does; verify SnpEff/ANNOVAR per version). Never hand-derive an HGVS string from POS.
- When matching a patient variant to a ClinVar/literature HGVS, normalize BOTH to the same representation first. `dup` vs `ins` describe the same event but do not string-match. See variant-calling/variant-normalization.
- Adjacent SNVs in one codon (an MNV split by the caller) can be individually benign but jointly change the amino acid; per-SNV annotation silently misannotates. Use phase-aware annotation.

## Choosing the transcript set

| Set | What it is | When to report on it |
|-----|-----------|----------------------|
| MANE Select | One transcript/gene, byte-identical `NM_`/`ENST` on GRCh38 (Morales 2022 *Nature* 604:310-315) | Default for clinical reporting -- gives a single cross-database-stable c./p. |
| MANE Plus Clinical | Extra isoforms for genes where MANE Select misses known pathogenic variants | Add alongside MANE Select where assigned |
| RefSeq (`NM_`/`NR_`) | NCBI-curated; most ClinVar/HGMD/literature `c.` use these | Legacy clinical pins; may carry sequence absent from the reference |
| Ensembl/GENCODE (`ENST`) | Comprehensive, genome-aligned, more transcripts/gene | Research; NOT 1:1 with RefSeq -- c. positions differ |
| Worst-consequence across all | Most severe over every overlapping transcript | Discovery only -- inflates severity, manufactures false PVS1 |

Decision: report on MANE Select (plus MANE Plus Clinical where assigned), not worst-consequence. Worst-consequence reports a canonical splice change in a minor non-expressed isoform as "splice" even when MANE Select is intronic, manufacturing false PVS1 candidates; restricting to MANE Select alone can miss a variant that only hits a MANE Plus Clinical isoform -- which is exactly why that tier exists. The Ensembl "canonical" transcript is frequently NOT the MANE Select one, so migrating a pipeline to MANE changes some reported c. coordinates (expected, not erroneous). MANE is GRCh38-only; GRCh37 pipelines must lift over or maintain their own per-gene transcript pins.

**Why `--pick` is dangerous for clinical use.** VEP by default reports all consequences for all overlapping transcripts. `--pick` collapses to one block per variant using an ordered heuristic whose defaults are canonical status, biotype, consequence rank, then transcript length, then finally accession order. The late tiebreakers are not clinically motivated: when transcripts tie, `--pick` can let transcript length or alphanumeric `ENST` order decide which consequence a real patient gets, can pick per-variant (so variant A and variant B in one gene land on different transcripts, destroying coordinate consistency), and can silently hide a PVS1-eligible consequence behind a benign one. Defensible configurations: pin MANE Select (with Plus Clinical), or pin the lab's validated per-gene list. If `--pick`-style collapse is used at all, constrain it so MANE leads and length/accession never decide:

```bash
# --pick_order forces MANE first; length/accession can no longer choose the reported transcript
vep -i norm.vcf --vcf --cache --offline --assembly GRCh38 \
    --mane_select --pick --pick_order mane_select,canonical,biotype,rank -o out.vcf
```

## Consequence, impact, and NMD (the PVS1 hinge)

Anchor the vocabulary to Sequence Ontology (SO) terms (`missense_variant`, `stop_gained`, `frameshift_variant`, `splice_donor_variant`, `splice_acceptor_variant`, `start_lost`, `stop_lost`, `inframe_deletion`, `synonymous_variant`, ...), which VEP emits natively. SnpEff/ANNOVAR map to mostly-equivalent terms but differ on splice-region width and finer intronic terms (VEP adds `splice_donor_5th_base_variant`, `splice_polypyrimidine_tract_variant`), so term-level matching across engines is impossible.

Impact buckets are NOT evidence. SnpEff `HIGH/MODERATE/LOW/MODIFIER` and ANNOVAR `exonic;splicing` groupings are triage conveniences. `HIGH` lumps `stop_gained`, `frameshift`, and canonical splice together, but whether any of these earns PVS1 depends on NMD, exon location, and the gene's LOF mechanism -- none of which the bucket knows. Treating "HIGH impact" as "PVS1 met" is a classic error.

**The NMD 50-nt / last-exon rule** governs PVS1 strength (Abou Tayoun 2018 *Hum Mutat* 39(11):1517-1524). A premature termination codon (PTC) more than ~50-55 nt upstream of the last exon-exon junction triggers nonsense-mediated decay -> no protein -> strong LOF. A PTC in the **last exon**, or within ~50 nt of the final junction (3' end of the penultimate exon), **escapes NMD** -- the truncated protein IS made, so full-strength PVS1 on the "NMD -> no protein" logic is unjustified (downgrade to PVS1_Strong/Moderate/Supporting depending on how much protein / which domains are lost). Single-exon genes have no junctions, so a nonsense variant escapes NMD by construction; PTCs near the start can reinitiate downstream. PVS1 also requires that LOF is the established disease mechanism -- a null allele in a gain-of-function/dominant-negative gene must NOT fire PVS1. The ACMG combining lives in variant-calling/clinical-interpretation; this skill supplies the consequence + NMD inputs it needs.

## Annotation engines: run commands

Fix the transcript set and tool+version in the pipeline and record them; that, not tool choice, is what makes annotation reproducible.

### Ensembl VEP

**Goal:** Annotate consequence, HGVS, impact, frequencies, and plugin predictions against Ensembl/MANE.

**Approach:** Run offline against the cache with explicit assembly and transcript selection; add predictor plugins rather than relying on the built-in SIFT/PolyPhen.

```bash
# --everything enables --hgvs --symbol --canonical --af --af_gnomade --af_gnomadg --sift b
# --polyphen b --pubmed etc. Prefer --mane_select over the enabled --canonical for reporting.
vep -i norm.vcf.gz -o out.vcf --vcf --cache --offline \
    --species homo_sapiens --assembly GRCh38 --everything --mane_select --fork 4
```

```bash
# Calibrated predictors as plugins (one calibrated tool per evidence type -- see below)
vep -i norm.vcf.gz -o out.vcf --vcf --cache --offline \
    --plugin dbNSFP,dbNSFP4.3a.gz,REVEL_score,CADD_phred \
    --plugin AlphaMissense,file=AlphaMissense_hg38.tsv.gz \
    --plugin SpliceAI,snv=spliceai_snv.vcf.gz,indel=spliceai_indel.vcf.gz
```

### SnpEff / SnpSift

**Goal:** Fast batch effect annotation plus database cross-referencing.

**Approach:** `snpEff ann` against a prebuilt genome database, then chain `SnpSift annotate`/`filter`.

```bash
# Human GRCh38 DB expands to 3-4 GB in memory; give the JVM >= 8 GB or it OOMs/thrashes
snpEff -Xmx8g ann GRCh38.105 norm.vcf > out.vcf
snpEff -Xmx8g ann GRCh38.105 norm.vcf | SnpSift annotate clinvar.vcf.gz > annotated.vcf
```

### ANNOVAR

**Goal:** Table-driven gene/frequency/pathogenicity annotation.

**Approach:** `table_annovar.pl` with paired `-protocol`/`-operation` lists (g=gene, f=filter, r=region).

```bash
table_annovar.pl norm.vcf humandb/ -buildver hg38 -out annotated -remove \
    -protocol refGene,gnomad30_genome,clinvar_20230416,dbnsfp42a \
    -operation g,f,f,f -nastring . -vcfinput
```

### bcftools csq / annotate

**Goal:** Lightweight consequence prediction (csq) and database field transfer (annotate) without a full engine.

**Approach:** `csq` maps variants to a GFF3 and emits a `BCSQ` field; `annotate -c` copies ID/INFO columns from a position-matched source.

```bash
bcftools csq -f reference.fa -g genes.gff3.gz norm.vcf.gz -Oz -o csq.vcf.gz   # adds BCSQ
bcftools annotate -a dbsnp.vcf.gz -c ID norm.vcf.gz -Oz -o rsid.vcf.gz        # copy rsIDs
```

See usage-guide.md for BED/TAB annotation, field removal, `--set-id`, chromosome renaming, and database download recipes.

## Pathogenicity predictors: one calibrated tool, not a stack

Two structural problems pervade this literature. (1) Circularity: most predictors train on ClinVar/HGMD labels, so benchmarking or ACMG-calibrating on those same databases is partly self-referential; a headline "AUC 0.9x" is optimistic on truly novel variants. (2) Ensembles ingest each other: REVEL is a random forest over 13 component scores including SIFT and PolyPhen, so "REVEL agrees with PolyPhen" is not independent corroboration -- PolyPhen is inside REVEL. Independence between evidence lines is the load-bearing assumption of the ACMG points system; stacking correlated predictors silently over-calls pathogenic.

Therefore: use exactly ONE calibrated predictor per evidence type (missense; splicing), applied at its calibrated strength.

| Predictor | Scope | Use for PP3/BP4 |
|-----------|-------|-----------------|
| REVEL (Ioannidis 2016 *AJHG* 99(4):877-885) | rare missense | Best-calibrated single missense tool; calibrated thresholds below |
| AlphaMissense (Cheng 2023 *Science* 381(6664):eadg7492) | missense, proteome-wide | Not trained on ClinVar labels (uses population frequency + structure); use the CURRENT ClinGen SVI calibrated thresholds, not the developer class cutoffs |
| CADD (Kircher 2014 *Nat Genet* 46:310-315) | all variant types | Genome-wide/non-coding ranking, NOT missense PP3 -- see caveat |
| SIFT / PolyPhen-2 (Ng 2003 *NAR* 31:3812; Adzhubei 2010 *Nat Methods* 7(4):248) | missense | Do not use as standalone evidence -- see below |
| SpliceAI (Jaganathan 2019 *Cell* 176(3):535-548) | splice-altering | The splicing predictor; delta-score interpretation below |

**SIFT/PolyPhen alone are near-worthless now.** In the ClinGen SVI calibration (Pejaver 2022 *Am J Hum Genet* 109(12):2163-2177) neither reached even Supporting strength for PP3; both call a large fraction of all missense "damaging" (low positive predictive value on rare variants); and both are components of REVEL, so quoting them alongside it double-counts. Legacy pipelines surfacing "SIFT: deleterious, PolyPhen: probably damaging" prominently are decorative, not evidentiary.

**CADD >= 20 is not "pathogenic."** In Pejaver 2022 raw CADD did not reach Supporting for PP3, and the developer-recommended CADD >= 20 mapped to Moderate evidence for **benign** -- an inversion of how CADD 20 is casually used. Reserve CADD for its intended non-coding/genome-wide ranking.

**Calibrated REVEL thresholds (Pejaver 2022).** PP3_Supporting >= 0.644 and BP4_Supporting <= 0.290 are the well-reproduced values. The Moderate/Strong REVEL cutoffs (commonly quoted as PP3_Moderate >= 0.773, PP3_Strong >= 0.932; BP4_Moderate <= 0.183, BP4_Strong <= 0.016) come from the supplementary tables and are not uniformly reproduced -- verify against the Pejaver 2022 supplement / current ClinGen SVI recommendation table before hard-coding, rather than treating them as fixed. PP3 and BP4 are mutually exclusive by construction; only tools reaching >= Strong in the calibration qualify.

**SpliceAI delta scores.** Per variant, SpliceAI emits four deltas (acceptor gain/loss, donor gain/loss), each 0-1; the max is the headline. Developer-recommended interpretation: 0.2 high recall, 0.5 recommended, 0.8 high precision. Caveats: (i) know whether the pipeline uses the masked or raw model; (ii) the default scoring window is +/-50 bp -- deep-intronic/pseudoexon effects need a widened window (up to +/-10 kb) or are missed; (iii) a delta is a prediction, and converting it to PS3/PP3 strength needs the ClinGen splicing calibration, not the raw cutoffs; (iv) it does not report the RESULT (exon skip vs intron retention), which is what determines PVS1. Pangolin (Zeng 2022 *Genome Biol* 23:103) is an emerging tissue-aware alternative -- check current ClinGen splicing guidance. AlphaMissense and the splicing calibrations are still-evolving; verify the current ClinGen SVI approved-tool list before standardizing on one.

## Population frequency: grpmax filtering AF, not a global cutoff

gnomAD version + build is itself a trap. v2.1.1 is 141,456 individuals (125,748 exomes + 15,708 genomes) on **GRCh37** (Karczewski 2020 *Nature* 581(7809):434-443); v3 is genomes-only on GRCh38; v4 aggregates ~730k exomes + ~76k genomes on **GRCh38** (release totals per the gnomAD v4 release notes; the v4 genome constraint map is Chen 2024 *Nature* 625(7993):92-100). Comparing AF across versions requires liftover of the VARIANT (not just the coordinate), which can mis-map indels/segdups. "Absent" can mean "not callable here," not "not present in humans" -- always check site coverage/callability and the PASS/`AS_FilterStatus` flags, not just raw AF.

A single global AF cutoff ("AF > 1% -> benign") is wrong in both directions. The maximum credible population AF for a truly pathogenic allele is per-disease -- it depends on prevalence, allelic and genetic heterogeneity, inheritance, and penetrance (Whiffin 2017 *Genet Med* 19(10):1151-1158). Use the **filtering allele frequency (FAF)**: the lower bound of the 95% CI of the **grpmax** AF (the highest AF among genetic-ancestry groups, formerly "popmax"; v4 fields `grpmax`, `AF_grpmax`, `fafmax_faf95_max`, and the joint exome+genome VCF tag `fafmax_faf95_max_joint`). Global AF dilutes a variant common in one ancestry across the whole cohort; grpmax exposes it. Apply BA1/BS1 when FAF exceeds the disease's maximum credible AF -- too-lenient a global line benignizes nothing for ultra-rare high-penetrance disease, and too-strict a global line wrongly benignizes founder alleles that reach several percent in one ancestry.

**"In gnomAD therefore benign" is a fallacy.** Documented exceptions: recessive disease (healthy carriers -> pathogenic alleles present at carrier frequency, e.g. CFTR p.Phe508del); late-onset/reduced-penetrance disease (gnomAD adults can be pre-symptomatic carriers of adult-onset cancer/cardiomyopathy/neurodegeneration alleles, e.g. BRCA/Lynch); somatic/clonal-hematopoiesis contamination (low-AF calls in DNMT3A/TET2 can be somatic, not germline). Ancestry sampling is uneven, so "absent" is much weaker evidence for an under-represented ancestry than for a well-sampled one. The full BA1/BS1/PM2 combining lives in variant-calling/clinical-interpretation.

## Python: parse an annotated VCF

**Goal:** Flatten VEP CSQ (or SnpEff ANN) transcript blocks into per-transcript dicts for filtering.

**Approach:** Read the CSQ format from the header, then split each record's CSQ on commas (transcripts) and pipes (fields).

```python
from cyvcf2 import VCF

vcf = VCF('vep_output.vcf')
csq_fields = None
for h in vcf.header_iter():
    if h['HeaderType'] == 'INFO' and h['ID'] == 'CSQ':
        csq_fields = h['Description'].split('Format: ')[1].rstrip('"').split('|')
        break

for variant in vcf:
    csq = variant.INFO.get('CSQ')
    if not csq:
        continue
    for block in csq.split(','):
        ann = dict(zip(csq_fields, block.split('|')))
        # MANE_SELECT is populated only for the MANE transcript; prefer it over worst-consequence
        if ann.get('MANE_SELECT') and ann.get('IMPACT') in ('HIGH', 'MODERATE'):
            print(variant.CHROM, variant.POS, ann['SYMBOL'], ann['Consequence'])
```

`bcftools +split-vep -f '%CHROM\t%POS\t%SYMBOL\t%Consequence\n' -s worst out.vcf.gz` does the same at the CLI; `-s worst` and `-p` control which block(s) surface.

## Complete annotation pipeline

**Goal:** Normalize, then annotate on MANE Select with calibrated predictors, then triage.

**Approach:** Left-align/split multiallelics, run VEP with MANE-led selection and predictor plugins, filter to HIGH/MODERATE for review (triage, not classification).

```bash
#!/bin/bash
set -euo pipefail
INPUT=$1; REFERENCE=$2; VEP_CACHE=$3; OUT=$4

bcftools norm -f "$REFERENCE" -m-any "$INPUT" -Oz -o "${OUT}_norm.vcf.gz"
bcftools index "${OUT}_norm.vcf.gz"

# --mane_select + constrained --pick_order so MANE leads and length/accession never decide
vep -i "${OUT}_norm.vcf.gz" -o "${OUT}_vep.vcf" \
    --vcf --cache --offline --dir_cache "$VEP_CACHE" --assembly GRCh38 \
    --everything --mane_select --pick --pick_order mane_select,canonical,biotype,rank --fork 4

bgzip "${OUT}_vep.vcf" && bcftools index "${OUT}_vep.vcf.gz"
bcftools view -i 'INFO/CSQ~"HIGH" || INFO/CSQ~"MODERATE"' \
    "${OUT}_vep.vcf.gz" -Oz -o "${OUT}_review.vcf.gz"
```

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| Two labs report different c. for one indel | HGVS 3'-shift vs VCF left-align, strand-dependent | Normalize both to one representation before matching; never hand-derive HGVS from POS |
| "HIGH impact stop_gained" assumed PVS1 | Impact bucket ignores NMD, exon location, LOF mechanism | Check the NMD 50-nt/last-exon rule and gene mechanism before invoking PVS1 |
| Consequence changed after MANE migration | Ensembl canonical != MANE Select for many genes | Expected, not an error; communicate the coordinate change |
| Empty gnomAD annotations | Build mismatch (v2=GRCh37 vs v3/v4=GRCh38) or chr naming (chr1 vs 1) | Match build; `bcftools annotate --rename-chrs`; check site callability |
| VEP/SnpEff/ANNOVAR disagree on consequence | Different transcript set / splice width / severity ranking | Not a bug; pin one engine+version+transcript set and record it |
| `--pick` picked a non-clinical transcript | Length/accession tiebreaker fell through | Constrain `--pick_order mane_select,...` or pin a per-gene list |
| Predictors "all agree it's damaging" | Correlated tools (REVEL contains SIFT/PolyPhen) double-counted | Use ONE calibrated predictor at its calibrated strength |

## Related Skills

- variant-calling/variant-normalization - Left-align and split multiallelics; the mandatory step before annotation and HGVS
- variant-calling/clinical-interpretation - ACMG/AMP combining rules, PVS1/PP3/BP4 strengths, ClinVar star ratings, final classification
- variant-calling/filtering-best-practices - Filter by annotation and quality fields
- variant-calling/vcf-basics - Query annotated INFO/CSQ fields
- variant-calling/vcf-manipulation - Merge and manipulate annotated VCFs
- database-access/entrez-fetch - Download annotation databases (ClinVar, dbSNP)

## References

- McLaren W, et al. The Ensembl Variant Effect Predictor. *Genome Biology*. 2016;17:122. doi:10.1186/s13059-016-0974-4
- Cingolani P, et al. A program for annotating and predicting the effects of SNPs, SnpEff. *Fly (Austin)*. 2012;6(2):80-92. doi:10.4161/fly.19695
- Wang K, Li M, Hakonarson H. ANNOVAR: functional annotation of genetic variants. *Nucleic Acids Research*. 2010;38(16):e164. doi:10.1093/nar/gkq603
- Morales J, et al. A joint NCBI and EMBL-EBI transcript set for clinical genomics and research (MANE). *Nature*. 2022;604:310-315. doi:10.1038/s41586-022-04558-8
- Tan A, Abecasis GR, Kang HM. Unified representation of genetic variants. *Bioinformatics*. 2015;31(13):2202-2204. doi:10.1093/bioinformatics/btv112
- Abou Tayoun AN, et al. Recommendations for interpreting the loss of function PVS1 ACMG/AMP variant criterion. *Human Mutation*. 2018;39(11):1517-1524. doi:10.1002/humu.23626
- Pejaver V, et al. Calibration of computational tools for missense variant pathogenicity classification and ClinGen recommendations for PP3/BP4 criteria. *American Journal of Human Genetics*. 2022;109(12):2163-2177. doi:10.1016/j.ajhg.2022.10.013
- Ioannidis NM, et al. REVEL: an ensemble method for predicting the pathogenicity of rare missense variants. *American Journal of Human Genetics*. 2016;99(4):877-885. doi:10.1016/j.ajhg.2016.08.016
- Cheng J, et al. Accurate proteome-wide missense variant effect prediction with AlphaMissense. *Science*. 2023;381(6664):eadg7492. doi:10.1126/science.adg7492
- Kircher M, et al. A general framework for estimating the relative pathogenicity of human genetic variants (CADD). *Nature Genetics*. 2014;46:310-315. doi:10.1038/ng.2892
- Ng PC, Henikoff S. SIFT: predicting amino acid changes that affect protein function. *Nucleic Acids Research*. 2003;31(13):3812-3814. doi:10.1093/nar/gkg509
- Adzhubei IA, et al. A method and server for predicting damaging missense mutations (PolyPhen-2). *Nature Methods*. 2010;7(4):248-249. doi:10.1038/nmeth0410-248
- Jaganathan K, et al. Predicting splicing from primary sequence with deep learning (SpliceAI). *Cell*. 2019;176(3):535-548. doi:10.1016/j.cell.2018.12.015
- Zeng T, Li YI. Predicting RNA splicing from DNA sequence using Pangolin. *Genome Biology*. 2022;23:103. doi:10.1186/s13059-022-02664-4
- Karczewski KJ, et al. The mutational constraint spectrum quantified from variation in 141,456 humans (gnomAD v2.1.1). *Nature*. 2020;581(7809):434-443. doi:10.1038/s41586-020-2308-7
- Chen S, et al. A genomic mutational constraint map using variation in 76,156 human genomes (gnomAD v4). *Nature*. 2024;625(7993):92-100. doi:10.1038/s41586-023-06045-0
- Whiffin N, et al. Using high-resolution variant frequencies to empower clinical genome interpretation. *Genetics in Medicine*. 2017;19(10):1151-1158. doi:10.1038/gim.2017.26
<!-- END FILE: variant-calling/variant-annotation/SKILL.md -->

## 子目录：variant-calling/variant-calling

<!-- BEGIN FILE: variant-calling/variant-calling/SKILL.md -->
---
name: bio-variant-calling
description: Call germline SNPs and indels from a BAM/CRAM with bcftools mpileup and call, and select the right calling engine for the job. Use when generating a VCF from aligned reads, choosing between bcftools, GATK HaplotypeCaller, DeepVariant, and DRAGEN, setting ploidy for haploid/organelle/polyploid/sex-chromosome calling, or deciding whether pileup-based calling is good enough versus a local-reassembly caller for indels and difficult regions. Not for cohort joint genotyping (see variant-calling/joint-calling), GATK-specific workflows (see variant-calling/gatk-variant-calling), deep-learning calling (see variant-calling/deepvariant), or somatic/low-VAF detection.
tool_type: cli
primary_tool: bcftools
---

## Version Compatibility

Reference examples tested with: bcftools 1.19+

Before using code patterns, verify installed versions match. If versions differ:
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

Note: bcftools mpileup applies BAQ (per-Base Alignment Quality) by default; this is a real behavior that changes calls, not a nuisance flag (see The Governing Principle).

# Variant Calling from a BAM

**"Call SNPs and indels from my aligned reads"** -> Compute per-position genotype likelihoods from a BAM/CRAM against the reference, then call variant sites under a Bayesian model at the assumed ploidy.
- CLI (fast, position-based): `bcftools mpileup -f ref.fa in.bam | bcftools call -mv`
- CLI (reassembly, higher indel accuracy): GATK HaplotypeCaller (variant-calling/gatk-variant-calling)
- CLI (deep learning): DeepVariant (variant-calling/deepvariant)

This skill does the bcftools calling and is the engine-selection hub: it tells the agent when pileup calling is the right tool and when to hand off to a reassembly or deep-learning caller.

## The Governing Principle

There are two families of short-variant caller, and the choice between them is the single most consequential decision here.

- **Position-based genotype-likelihood callers** (bcftools mpileup|call, the old samtools/UnifiedGenotyper lineage) trust the aligner's per-read placement. At each reference position they tally the pileup, compute P(reads | genotype) per site, and call under a Bayesian model. Fast, transparent, no training data. But the mapper places each read greedily and independently, so an indel near a read end or inside a repeat is placed inconsistently across reads, and the per-position model cannot repair that. bcftools mitigates it with **BAQ** (per-Base Alignment Quality: base qualities near a likely misalignment are downweighted so a shaky column does not produce a confident false SNP), but BAQ suppresses false positives rather than reconstructing the true indel.
- **Local-reassembly / haplotype callers** (GATK HaplotypeCaller, DeepVariant, DRAGEN) discard the local alignment in an active region and re-derive it: assemble candidate haplotypes, realign every read to them (PairHMM or a learned model), then genotype. The indel is represented once, on the assembled haplotype, instead of (mis)placed per read. This is precisely why they beat pileup callers on indels, clustered variants, and difficult regions.

Consequence: bcftools is fine-to-excellent for **simple germline SNPs** and quick genome-wide scans, materially **weaker on indels and in low-complexity / segmental-duplication / MHC regions**, and not built for somatic low-VAF detection or scalable cohort joint calling. Pick the engine from the analysis, not from habit.

## Engine Selection (the decision that comes before any command)

Guidance, not dogma; on a production human pipeline, validate against current GIAB/GA4GH benchmarks (hap.py + vcfeval) before committing.

| Engine | Best when | Fails / weak when | Hand off to |
|--------|-----------|-------------------|-------------|
| **bcftools mpileup\|call** | Simple germline SNPs; non-model/organelle/microbial genomes (no training data, any ploidy); quick exploratory scans; low compute; small multi-sample sets | Indels in homopolymers/STRs; segdups, MHC, low-mappability; low-VAF somatic/mosaic; cohorts beyond ~100 samples | this skill |
| **GATK HaplotypeCaller** | Auditable open-source human WGS/WES; every parameter inspectable; the joint-calling/best-practices orthodoxy (GVCF -> GenomicsDBImport -> GenotypeGVCFs) | Lower indel/difficult-region accuracy than DeepVariant/DRAGEN; local assembly can abort in pathological high-depth/repeat regions | variant-calling/gatk-variant-calling; variant-calling/joint-calling |
| **DeepVariant** | Best open-source accuracy on **indels and difficult regions**; PacBio HiFi / ONT (platform-specific trained models); generalizes off one training sample | Needs the correct platform model (wrong model degrades accuracy); GPU helps; cohort merge needs GLnexus, not GenotypeGVCFs | variant-calling/deepvariant |
| **DRAGEN** | Maximum throughput on Illumina (FPGA, ~20-25 min/genome); leads difficult-to-map benchmarks (alt-aware mapping) | Proprietary/hardware- or license-gated; ML recalibrator trained on GIAB truth (benchmark-overfitting caveat) | vendor pipeline; `HaplotypeCaller --dragen-mode` for an open-source approximation |

Honest state of the field: **DeepVariant and DRAGEN lead on indels and difficult regions**; **GATK is the joint-calling and best-practices reference** everyone else is measured against; **bcftools wins on speed, simplicity, non-model organisms, and organelle/haploid calling**. On easy SNPs every modern caller exceeds F1 0.999, so a caller's headline SNP number is rarely the deciding factor - indels and hard regions are.

## bcftools mpileup + call

**Goal:** Detect germline SNPs and indels from aligned reads with the pileup-and-call pipeline.

**Approach:** Generate per-position genotype likelihoods with mpileup (BAQ on by default), pipe as uncompressed BCF into the multiallelic caller.

### Basic calling
```bash
bcftools mpileup -f reference.fa input.bam | bcftools call -mv -Oz -o variants.vcf.gz
bcftools index variants.vcf.gz
```

### Recommended single-sample pipeline
```bash
# -Ou between steps avoids VCF (de)serialization; -q/-Q drop poorly-supported reads/bases;
# -a requests the FORMAT tags downstream filtering needs (DP, allelic depths, strand-bias p)
bcftools mpileup -Ou -f reference.fa \
    -q 20 -Q 20 \
    -a FORMAT/DP,FORMAT/AD,FORMAT/SP \
    input.bam | \
bcftools call -mv -Oz -o variants.vcf.gz
bcftools index variants.vcf.gz
```

### Region-restricted and multi-sample calling
```bash
# Single region / BED targets
bcftools mpileup -f reference.fa -r chr1:1000000-2000000 input.bam | bcftools call -mv -Oz -o region.vcf.gz
bcftools mpileup -f reference.fa -R targets.bed input.bam | bcftools call -mv -Oz -o targets.vcf.gz

# Multiple BAMs (small cohorts only; see The Governing Principle for the scaling limit)
bcftools mpileup -f reference.fa sample1.bam sample2.bam sample3.bam | bcftools call -mv -Oz -o cohort.vcf.gz

# BAM list file: one path per line
bcftools mpileup -f reference.fa -b bams.txt | bcftools call -mv -Oz -o cohort.vcf.gz
```

## The mpileup / call flags that change results

| Stage | Flag | Effect |
|-------|------|--------|
| mpileup | `-f ref.fa` | Reference FASTA (required); must be the exact one used for alignment |
| mpileup | `-q INT` | Min mapping quality; `-q 20` drops ambiguously placed reads (paralog mismapping) |
| mpileup | `-Q INT` | Min base quality; `-Q 20` drops low-confidence base calls |
| mpileup | `-a LIST` | Extra FORMAT/INFO tags: `FORMAT/AD` (allelic depths), `FORMAT/DP`, `FORMAT/SP` (Phred strand-bias p), `FORMAT/ADF`/`ADR` (per-strand), `INFO/AD` |
| mpileup | `-d INT` | Max per-file depth (default 250); set to 3-4x expected mean coverage to avoid truncating high-coverage sites |
| mpileup | `-B` / `-E` | `-B` disables BAQ (more raw indel signal, more false SNPs near indels); `-E` recomputes BAQ on the fly (more sensitive, slower) |
| call | `-m` | Multiallelic caller - default, recommended for all new work |
| call | `-c` | Consensus caller - legacy; only for reproducing old pipelines |
| call | `-v` | Emit variant sites only (omit to emit all sites, e.g. for hom-ref confidence) |
| call | `-O z\|b\|u\|v` | Output: `z` bgzipped VCF, `b` BCF, `u` uncompressed BCF (piping), `v` VCF |
| call | `--ploidy` / `--ploidy-file` | Sample/region ploidy (below) |
| call | `-P FLOAT` | Mutation-rate prior (default 1.1e-3, human); lower for inbred lines, raise for diverse/outbred populations |

The multiallelic caller (`-m`) handles sites with several ALT alleles natively and is statistically superior; the consensus caller (`-c`) exists only for backward reproducibility.

## Ploidy: sample, organelle, and sex-chromosome calling

**Goal:** Match the caller's ploidy to the biology so genotypes are representable.

**Approach:** Set a scalar ploidy for uniform samples, or a ploidy file (or built-in preset) to vary ploidy by region and sex.

Wrong ploidy silently corrupts calls: calling a diploid as haploid halves heterozygous sensitivity; calling a haploid/hemizygous region as diploid manufactures false heterozygous calls from every error and paralog mismap.

```bash
# Haploid: bacteria, mitochondria (nuclear germline heteroplasmy caveat below), non-PAR chrX/chrY in a male
bcftools mpileup -f reference.fa input.bam | bcftools call -m --ploidy 1 -Oz -o haploid.vcf.gz

# Built-in human preset applies karyotype-aware sex-chromosome ploidy
bcftools call -m --ploidy GRCh38 ...

# Ploidy file: CHROM  FROM  TO  SEX  PLOIDY  (chrY absent in females -> 0)
#   chrX  1  -1  M  1
#   chrX  1  -1  F  2
#   chrY  1  -1  M  1
#   chrY  1  -1  F  0
#   *     1  -1  *  2
bcftools mpileup -f reference.fa input.bam | bcftools call -m --ploidy-file ploidy.txt -Oz -o sexaware.vcf.gz
```

Scope notes: true **mitochondrial heteroplasmy** is continuous-VAF (not 0/0.5/1) and is a somatic-shaped signal - a diploid or haploid genotype model cannot express it; use a somatic caller (GATK Mutect2 `--mitochondria-mode`) for real heteroplasmy work. **Polyploid/pooled** samples need `--ploidy N` set to the true copy number so dosage/allele-count is preserved rather than collapsed to het.

## After calling: the pipeline map

A raw caller VCF is not a finished callset. The standard downstream order:

1. **Normalize** - left-align and split multiallelics so identical variants have identical records: `bcftools norm -f reference.fa -m -any variants.vcf.gz -Oz -o norm.vcf.gz`. Do this before ANY comparison, annotation, or merge. See variant-calling/variant-normalization.
2. **Filter** - bcftools produces no VQSR/DL score, so apply quality/depth/strand hard filters (e.g. `QUAL`, `FORMAT/DP`, `SP`) suited to the depth and platform. See variant-calling/filtering-best-practices.
3. **Inspect / query** - counts, Ti/Tv, per-sample stats. See variant-calling/vcf-basics and variant-calling/vcf-statistics.

## Comparing callers honestly

If the point of choosing bcftools vs a reassembly caller is accuracy, compare them correctly - this is where naive analyses go wrong:

- **Normalize both callsets first** (`bcftools norm -f ref.fa -m -any`). Two VCFs can encode the identical haplotype with different records (indel placement in repeats, MNP vs split SNVs); un-normalized records mismatch spuriously.
- **Use haplotype-aware benchmarking, not `bcftools isec`.** A line-diff / `isec` on raw records overcounts both false positives and false negatives from representation alone. Score against a GIAB truth set with **hap.py + vcfeval** inside the confident-region BED (Krusche 2019), reporting SNVs and indels separately.
- **Stratify.** A genome-wide F1 hides the differences that matter - they live in indels-in-repeats, segdups, and MHC. Report per-region, not one headline number.

## Performance

**Goal:** Speed up calling on large inputs.

**Approach:** Pipe uncompressed BCF between stages, thread both tools, and shard by chromosome.

```bash
# Threaded, uncompressed-BCF pipe
bcftools mpileup -Ou -f reference.fa --threads 4 input.bam | \
    bcftools call -mv --threads 4 -Oz -o variants.vcf.gz

# Parallel by chromosome, then concatenate
for chr in chr1 chr2 chr3; do
    bcftools mpileup -Ou -f reference.fa -r "$chr" input.bam | \
        bcftools call -mv -Oz -o "${chr}.vcf.gz" &
done
wait
bcftools concat -Oz -o all.vcf.gz chr*.vcf.gz
bcftools index all.vcf.gz
```

## Difficult regions (know where pileup calling breaks)

- **Homopolymers / STRs** - the dominant indel false-positive source; slippage + mapping ambiguity + representation ambiguity all concentrate here. Validate indels in homopolymers >6 bp with a reassembly caller or manual review, or switch engines.
- **Segmental duplications / low mappability** - paralog reads pile up and manufacture false SNPs; sites with mean `MQ` <40 signal ambiguous mapping. `-q 20` helps; a reassembly/alt-aware caller helps more.
- **MHC and other hyper-polymorphic loci** - extreme divergence from the reference; expect reduced recall from any linear-reference caller.
- **High-depth regions** - set `-d` to 3-4x expected mean coverage; the default 250 truncates deep targeted panels and can bias likelihoods.

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| `no FASTA reference` | `-f` omitted | Add `-f reference.fa` |
| `[E::faidx] ... different number of sequences` / reference mismatch | mpileup reference != alignment reference | Use the exact FASTA the BAM was aligned to; compare `@SQ` in `samtools view -H` against `grep '^>' ref.fa` |
| No variants called | Coverage too low, `-q`/`-Q` too strict, empty/wrong BAM | Check `samtools depth`; relax `-q`/`-Q`; confirm reference build |
| False heterozygous calls everywhere on chrX/chrY (male) | Non-PAR sex chromosome called as diploid | Set `--ploidy 1` for non-PAR, or use a `--ploidy-file` / `--ploidy GRCh38` |
| Excess indel false positives in repeats | Position-based limitation, not a bug | Normalize + hard-filter; validate or recall indels with a reassembly caller |
| Downstream tools disagree on the same variant | Records not normalized | `bcftools norm -f ref.fa -m -any` before comparing/merging/annotating |

## Related Skills

- variant-calling/vcf-basics - View and query the resulting VCF
- variant-calling/variant-normalization - Left-align and split multiallelics before comparison
- variant-calling/filtering-best-practices - Hard-filter a bcftools callset (no VQSR/DL score)
- variant-calling/vcf-statistics - Ti/Tv, counts, and callset QC
- variant-calling/gatk-variant-calling - Local-reassembly calling with HaplotypeCaller and DRAGEN-GATK mode
- variant-calling/deepvariant - Deep-learning caller; best indel/difficult-region accuracy, long-read models
- variant-calling/joint-calling - Scalable cohort genotyping (GVCF workflow, GLnexus)
- alignment-files/pileup-generation - Alternative pileup generation
- read-alignment/bwa-alignment - Upstream mapping that determines calling quality

## References

- Li H. A statistical framework for SNP calling, mutation discovery, association mapping and population genetical parameter estimation from sequencing data. *Bioinformatics* 27(21):2987-2993 (2011). DOI 10.1093/bioinformatics/btr509. (The mpileup genotype-likelihood model.)
- Danecek P, Bonfield JK, Liddle J, Marshall J, Ohan V, Pollard MO, Whitwham A, Keane T, McCarthy SA, Davies RM, Li H. Twelve years of SAMtools and BCFtools. *GigaScience* 10(2):giab008 (2021). DOI 10.1093/gigascience/giab008. (bcftools mpileup/call/norm implementation.)
- DePristo MA, Banks E, Poplin R, Garimella KV, Maguire JR, Hartl C, et al. A framework for variation discovery and genotyping using next-generation DNA sequencing data. *Nature Genetics* 43(5):491-498 (2011). DOI 10.1038/ng.806. (Local-reassembly genotyping framework - the reassembly contrast.)
- Poplin R, Chang P-C, Alexander D, Schwartz S, Colthurst T, Ku A, et al. A universal SNP and small-indel variant caller using deep neural networks. *Nature Biotechnology* 36(10):983-987 (2018). DOI 10.1038/nbt.4235. (DeepVariant.)
- Krusche P, Trigg L, Boutros PC, Mason CE, De La Vega FM, Moore BL, et al. Best practices for benchmarking germline small-variant calls in human genomes. *Nature Biotechnology* 37:555-560 (2019). DOI 10.1038/s41587-019-0054-x. (hap.py/vcfeval, confident-region model, normalize-before-compare.)
<!-- END FILE: variant-calling/variant-calling/SKILL.md -->

## 子目录：variant-calling/variant-normalization

<!-- BEGIN FILE: variant-calling/variant-normalization/SKILL.md -->
---
name: bio-variant-normalization
description: Left-align and trim indels to parsimonious canonical form, decompose MNPs (atomize), and split multiallelic variants with bcftools norm. Use when comparing variants across callers or cohorts, preparing a VCF for database annotation or ClinVar/dbSNP matching, merging VCFs, reconciling vt-vs-bcftools representation discordance, or resolving the VCF-left-align vs HGVS-3'-rule clash.
tool_type: cli
primary_tool: bcftools
---

## Version Compatibility

Reference examples tested with: bcftools 1.19+, cyvcf2 0.30+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

The `--atomize`/`--old-rec-tag` flags require bcftools 1.12+ (`--keep-sum` requires 1.11+). Earlier versions require `vt decompose_blocksub` as an alternative.

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Variant Normalization

Left-align indels, decompose MNPs, and split multiallelic sites using bcftools norm.

**"Put my VCF in canonical form before comparing, annotating, or merging"** -> Enforce one representation per biological event so tuple-keyed operations recognize the same variant across sources.
- CLI: `bcftools norm -m-any -f ref.fa` (split multiallelic, then left-align + parsimony each biallelic)
- Alternatives: `vt normalize` + `vt decompose`; GATK `LeftAlignAndTrimVariants`

## The Normalized Form (governing principle)

A variant is **normalized** if and only if it is BOTH (Tan, Abecasis & Kang 2015):

1. **Parsimonious (minimal representation).** No base can be trimmed from either end of REF/ALT without creating a zero-length allele or changing the variant. Indels keep exactly ONE anchor base (VCF forbids empty alleles), so a deletion of `A` is written `REF=CA ALT=C`, not `REF=A ALT=`.
2. **Left-aligned.** POS cannot be shifted further left while keeping the allele lengths and the reference-relative meaning unchanged.

Both are required: parsimony alone leaves an indel positionally ambiguous inside a repeat; left-alignment alone can leave redundant shared bases. Together they define a single canonical `(CHROM, POS, REF, ALT)` key, and normalization is **idempotent** -- normalizing an already-normalized VCF changes nothing. That idempotence is what makes the key safe to join, merge, and match on.

The algorithm (as in `vt normalize` and `bcftools norm`):
- **Right-trim:** while all alleles end in the same base AND all have length >= 2, drop the last base of each.
- **Left-extend:** while any allele has length 0, prepend the reference base immediately to the left to every allele and decrement POS.
- **Left-trim:** while all alleles start with the same base AND all have length >= 2, drop the first base of each and increment POS.

The right-trim-then-left-roll loop is exactly what shifts an indel through a repeat to its leftmost equivalent position.

## When Normalization is Mandatory

Not normalizing before certain operations leads to missed matches and false discordance. Normalization is required:

- **Before comparing variants from different callers.** Each caller may represent the same indel at different positions or encode MNPs differently. Without normalization, identical variants appear discordant.
- **Before database annotation.** dbSNP, ClinVar, and gnomAD store variants in canonical left-aligned, parsimonious representation. A right-aligned or non-parsimonious indel will fail to match its database entry.
- **Before merging VCF files from different sources.** `bcftools merge` matches on CHROM/POS/REF/ALT; different representations of the same variant produce duplicate entries instead of a single merged record.
- **Before any variant set operations.** Intersection (`bcftools isec`), complement, and union operations all rely on exact positional matching. Non-normalized variants silently fall through set comparisons.

Normalization is generally safe to skip only when a single caller produced all variants and no cross-file comparison or database lookup is needed.

## Why Left-Alignment Matters in Repeats (the silent miss)

The same variant can be written multiple ways:

```
chr1  100  ATCG  A      (right-aligned)
chr1  100  ATC   A      (left-aligned, parsimonious -- the canonical form)
chr1  101  TCG   T      (shifted position, different anchor base)
```

The ambiguity is worst in homopolymers and tandem repeats. In reference `...AAAAAAA...`, a single-base `A` deletion is positionally ambiguous: deleting ANY one of the seven A's yields the identical alternate haplotype, so different callers/aligners emit it at different POS. Left-alignment defines the canonical (leftmost) position, giving the one biological event one representation.

The load-bearing consequence: a one-base-off (non-left-aligned) indel in a homopolymer is a valid VCF line that produces a **different** `(CHROM, POS, REF, ALT)` tuple. Annotation and matching keyed on that tuple then silently **miss** the dbSNP/ClinVar/gnomAD entry that sits at the canonical coordinate -- a clinically actionable variant is reported as absent or novel, with **no error thrown**. The VCF is structurally valid; the numbers are wrong. `bcftools merge` of a normalized and an un-normalized cohort likewise emits duplicate rows for the same event, inflating counts and splitting allele frequencies.

Decision: always left-align + parsimony (`bcftools norm -f ref.fa`) against the EXACT downstream reference before annotation, database matching, set operations, or merging -- never rely on callers to emit canonical form.

## Recommended Normalization Pipeline

The order of operations matters. Performing these steps out of order can produce incorrect results (e.g., left-aligning a multiallelic record may normalize differently than splitting first, then left-aligning each biallelic record independently).

The correct order:

1. **Decompose MNPs** into atomic SNPs (`--atomize`)
2. **Split multiallelic** sites into biallelic records (`-m-`)
3. **Left-align and trim** against the reference (`-f reference.fa`)

Combined as a piped pipeline:

```bash
bcftools norm --atomize input.vcf.gz | \
    bcftools norm -m- | \
    bcftools norm -f reference.fa -Oz -o normalized.vcf.gz
bcftools index normalized.vcf.gz
```

For VCFs without MNPs (e.g., GATK HaplotypeCaller output, which does not emit MNPs), the atomize step can be skipped:

```bash
bcftools norm -m- input.vcf.gz | \
    bcftools norm -f reference.fa -Oz -o normalized.vcf.gz
```

A single-pass `bcftools norm -f ref.fa -m-any` is acceptable for basic use cases but does not control the decomposition order and skips MNP atomization.

## Tool Discordance: bcftools vs vt vs GATK

All three implement the same Tan-2015 left-align + parsimony core and agree on simple biallelic indels. They diverge on decomposition:

| Behavior | `vt` | `bcftools norm` | GATK `LeftAlignAndTrimVariants` |
|----------|------|-----------------|--------------------------------|
| Left-align + parsimony (biallelic) | yes (`normalize`) | yes (`-f`) | yes |
| Split multiallelic | `vt decompose` (separate step) | `-m-any` | `--split-multi-allelics` |
| Decompose MNP -> SNPs | `vt decompose_blocksub` splits MNPs **by default** (`vt decompose` only splits multiallelics) | only with `--atomize` (bcftools >= 1.12); **NOT by default** | does not decompose MNPs into SNPs |
| Block substitution / complex | `vt decompose_blocksub` | `--atomize` | limited |

The discordance that burns people: `vt decompose_blocksub` splits MNPs/block substitutions into SNPs by default, `bcftools norm` does not (it needs `--atomize`). Running the same normalization with the two tools yields a **different variant count** (bcftools keeps an MNP as one record; vt emits separate SNPs). If cohort A is atomized with vt and cohort B is left un-atomized with bcftools, every MNP is a systematic representation mismatch, manufacturing **spurious cohort-private "variants"** in any cross-cohort comparison.

Decision: standardize on ONE normalization tool + exact flag set across every cohort intended for comparison, and record the command. `bcftools norm` is the de-facto production standard (htslib-maintained; integrates split, atomize, and left-align in one pass). Note GATK's left-alignment window (`--max-leading-bases`) means indels inside repeats longer than the window may not fully left-align -- verify the installed default with `gatk LeftAlignAndTrimVariants --help` before trusting STR-embedded indels.

## Left-Alignment

**"Normalize my VCF before comparing callers"** -> Left-align indel representations and split multiallelic sites for consistent variant comparison.

```bash
bcftools norm -f reference.fa input.vcf.gz -Oz -o normalized.vcf.gz
```

Left-alignment cannot roll an indel leftward without the reference bases to its left, so `-f/--fasta-ref` is non-negotiable. Two traps make the reference choice load-bearing:
- The FASTA must be the **exact** reference the VCF was called against. A different build patch, `chr1`-vs-`1` contig naming, or a masked-vs-unmasked sequence yields **wrong** left-aligned coordinates. On a REF mismatch `bcftools norm` **errors and exits non-zero by default** (`-c e`) rather than warning -- do not paper over it with `-c w`; a single off-by-one in a contig shifts every indel.
- It must be the SAME reference used **downstream** (the annotation-database build, the other cohort). Normalizing to GRCh38 and matching against a GRCh37 dbSNP is a guaranteed miss even when local left-alignment is perfect.

### Check for Normalization Issues

```bash
bcftools norm -f reference.fa -c w input.vcf.gz > /dev/null
```

Check modes (`-c`):
- `e` - Error and exit on mismatch (default)
- `w` - Warn on mismatch and continue (use this to enumerate all mismatches)
- `x` - Exclude mismatches
- `s` - Set correct REF from reference

## Multiallelic Splitting

### Split Multiallelic to Biallelic

```bash
bcftools norm -m-any input.vcf.gz -Oz -o split.vcf.gz
```

Before:
```
chr1  100  .  A  G,T  30  PASS  .  GT  1/2
```

After:
```
chr1  100  .  A  G  30  PASS  .  GT  1/0
chr1  100  .  A  T  30  PASS  .  GT  0/1
```

### Splitting Caveats

Splitting creates artificial missing information. A sample with genotype 1/2 (compound heterozygous for two different ALT alleles) becomes 0/1 in both split records. The information that both alleles were present at the same site in the same individual is lost. This has consequences for:

- **Phasing and compound heterozygosity detection.** Clinical pipelines that identify compound hets (two damaging variants on different alleles of the same gene) can misinterpret split records as independent heterozygous calls rather than co-occurring alleles at one site.
- **Allele depth (AD) interpretation.** AD values are retained per allele in each split record, but the genotype relationship between alleles at the same site is gone.
- **Population allele frequency estimation.** Splitting followed by naive frequency calculation can double-count samples at multiallelic sites.

Decision guidance:

| Downstream tool | Splitting required? | Rationale |
|----------------|-------------------|-----------|
| PLINK, PLINK2 | Yes | PLINK requires biallelic records |
| Most GWAS tools | Yes | Expect biallelic sites |
| Hail | No | Handles multiallelics natively; splitting loses information |
| bcftools csq | No | Supports multiallelic consequence calling |
| VEP | Either | Handles both; multiallelic may give richer output |
| ClinVar matching | Yes | ClinVar entries are biallelic |

When a downstream tool does not require splitting, prefer keeping multiallelic sites intact to preserve genotype relationships.

### Split Options

| Option | Description |
|--------|-------------|
| `-m-any` | Split all multiallelic sites |
| `-m-snps` | Split multiallelic SNPs only |
| `-m-indels` | Split multiallelic indels only |
| `-m-both` | Split SNPs and indels separately |
| `-m+any` | Join biallelic sites into multiallelic |
| `-m+snps` | Join biallelic SNPs |
| `-m+indels` | Join biallelic indels |
| `-m+both` | Join SNPs and indels separately |

### Join Biallelic to Multiallelic

```bash
bcftools norm -m+any input.vcf.gz -Oz -o merged.vcf.gz
```

Rejoining after analysis can restore compound heterozygosity context, but only if the split records were not independently filtered (removing one allele of a 1/2 site makes the remaining record misleading).

### Field Reapportionment and Spanning Deletions

Splitting a multiallelic is NOT information-lossless. Per-allele fields must be reapportioned according to their header `Number` code, and `bcftools norm -m-` uses those codes to subset correctly:
- `Number=A` (one value per ALT, e.g. `AF`, `AC`) -> take the k-th element for the k-th ALT.
- `Number=R` (one per allele including REF, e.g. `AD` -> ref depth first) -> off-by-one relative to `A`.
- `Number=G` (one per genotype, e.g. `PL`, `GL`) -> subsetting needs the genotype-index formula.
- `Number=.` -> variable count; parsers **cannot** auto-subset, so these fields are silently carried whole onto every split record.

The trap: a custom INFO/FORMAT field mis-declared `Number=.` when it is really `A` is NOT subset on split, so every biallelic record keeps the full multiallelic vector and downstream tools read the **wrong allele's** value. Joining back (`-m+`) cannot always reconstruct the original PLs exactly. Rule: split once, early, and stay biallelic; join only for final delivery if a consumer requires it.

Spanning-deletion `*` alleles (VCF: "allele missing due to overlapping deletion") are meaningful only relative to the overlapping deletion recorded on another line. Splitting can strand a `*` allele from the deletion it references; bcftools handles this, but naive third-party splitters corrupt it. Use `--keep-sum AD` when the summed allele depth must be preserved across split records.

## Atomize Complex Variants (MNP Decomposition)

Multi-nucleotide polymorphisms (MNPs) are adjacent substitutions reported as a single record (e.g., ATG->GCA). Not all callers emit MNPs:

| Caller | Emits MNPs? | Notes |
|--------|------------|-------|
| FreeBayes | Yes | Reports MNPs and complex events natively |
| Octopus | Yes | Local haplotype-aware, emits block substitutions |
| GATK HaplotypeCaller | No | Decomposes variants during calling; may emit nearby SNPs in the same haplotype block |
| DeepVariant | Rarely | Primarily emits SNPs and indels |

Decomposing MNPs is necessary when comparing output from callers that represent them differently. Without atomization, an MNP from FreeBayes will not match the equivalent individual SNPs from GATK.

### Atomize MNPs to SNPs

```bash
bcftools norm --atomize input.vcf.gz -Oz -o atomized.vcf.gz
```

Before:
```
chr1  100  .  ATG  GCA  30  PASS
```

After:
```
chr1  100  .  A  G  30  PASS
chr1  101  .  T  C  30  PASS
chr1  102  .  G  A  30  PASS
```

**Caveat -- decomposition destroys phase needed for functional annotation.** The original MNP record guarantees that its substitutions occur on the SAME haplotype. Atomization discards that guarantee. The concrete failure: two adjacent SNVs falling in one codon, annotated independently after decomposition, can each look **synonymous** while the true MNV (the haplotype) is **missense or nonsense** (or the reverse). VEP/SnpEff give the wrong amino-acid consequence on decomposed alleles because they no longer see the codon change.

This is the unresolved decompose-vs-atomic tension: decompose for variant **matching** (dbSNP/ClinVar/gnomAD lookup, allele-frequency comparison), but compute **functional consequence** on the haplotype-resolved (undecomposed / phased) representation -- run `bcftools csq` on the un-atomized VCF, which is codon-aware. Keep the atomized copy for matching and the un-atomized copy for annotation; do not feed atomized alleles to a per-record consequence caller. See variant-calling/variant-annotation.

### Atomize with Old Record Tag

```bash
bcftools norm --atomize --old-rec-tag ORIGINAL input.vcf.gz -Oz -o atomized.vcf.gz
```

Preserves the original record as an INFO annotation, enabling traceability back to the pre-atomized variant.

## The Normalization <-> HGVS 3'-Rule Clash

VCF normalization and HGVS nomenclature shift indels in **opposite** directions, so a correctly normalized VCF and a correct HGVS string for the same indel can name different repeat units:
- **VCF left-alignment** shifts an ambiguous indel to the most **5'** position on the **forward genomic strand**.
- **HGVS mandates the 3'-rule:** the indel is described at the most **3'** position with respect to the **transcript** (coding reading direction).

For a **plus-strand** gene, transcript-3' equals genomic-rightward -- the OPPOSITE end from VCF left-alignment. For a **minus-strand** gene, transcript-3' points genomic-leftward and can coincide with left-alignment, but only by accident of strand. The result: the VCF POS and the HGVS `c.` position for one deletion legitimately disagree, and a tool that generates HGVS by naively translating the left-aligned POS without re-shifting 3' on the transcript emits a non-compliant string. This is a leading cause of "two labs reported different c. positions for the same deletion."

Decision: **never hand-derive HGVS from POS.** Left-align + normalize the VCF for matching/merging (idempotent, reproducible), and rely on the annotation engine's HGVS generator to apply the transcript 3'-shift (VEP does this; verify SnpEff/ANNOVAR per version). When matching a patient variant to a ClinVar or literature HGVS string, normalize BOTH to the same representation first -- two strings that look different can be the same variant. See variant-calling/variant-annotation and variant-calling/clinical-interpretation.

## Fixing Reference Alleles

**Goal:** Correct or remove variants whose REF allele does not match the reference genome.

**Approach:** Use bcftools norm -c with mode s (set correct REF) or x (exclude mismatches).

### Fix Mismatches from Reference

```bash
bcftools norm -f reference.fa -c s input.vcf.gz -Oz -o fixed.vcf.gz
```

This sets REF alleles to match the reference genome. Use with caution: REF mismatches often indicate a genome build mismatch, and silently "fixing" REF may mask a liftover error rather than correcting a trivial typo.

### Exclude Mismatches

```bash
bcftools norm -f reference.fa -c x input.vcf.gz -Oz -o clean.vcf.gz
```

Removes variants where REF does not match the reference. Safer than `-c s` when the cause of mismatch is unknown.

## Remove Duplicates After Splitting

```bash
bcftools norm -d exact input.vcf.gz -Oz -o deduped.vcf.gz
```

Duplicate removal options (`-d`):
- `exact` - Remove exact duplicates (same CHROM, POS, REF, ALT)
- `snps` - Remove duplicate SNPs only
- `indels` - Remove duplicate indels only
- `both` - Remove duplicate SNPs and indels
- `all` - Remove all duplicates at the same position
- `none` - Keep duplicates (default)

## Common Workflows

### Full Normalization for Caller Comparison

**Goal:** Make VCFs from different callers directly comparable.

**Approach:** Apply the same three-step normalization pipeline to each VCF, then use set operations.

```bash
for vcf in gatk.vcf.gz freebayes.vcf.gz; do
    base=$(basename "$vcf" .vcf.gz)
    bcftools norm --atomize "$vcf" | \
        bcftools norm -m- | \
        bcftools norm -f reference.fa -Oz -o "${base}.norm.vcf.gz"
    bcftools index "${base}.norm.vcf.gz"
done

bcftools isec -p comparison gatk.norm.vcf.gz freebayes.norm.vcf.gz
```

The `isec` output directories: `0000.vcf` = private to first file, `0001.vcf` = private to second, `0002.vcf`/`0003.vcf` = shared variants from each file.

### Before Database Annotation

```bash
bcftools norm --atomize variants.vcf.gz | \
    bcftools norm -m- | \
    bcftools norm -f reference.fa -Oz -o for_annotation.vcf.gz
bcftools index for_annotation.vcf.gz
```

### Prepare for GWAS (PLINK)

**Goal:** Produce a biallelic, SNP-only, deduplicated VCF suitable for PLINK import.

**Approach:** Normalize, split, restrict to SNPs, and remove duplicates.

```bash
bcftools norm -f reference.fa -m- input.vcf.gz | \
    bcftools view -v snps | \
    bcftools norm -d exact -Oz -o gwas_ready.vcf.gz
bcftools index gwas_ready.vcf.gz
```

## cyvcf2 Normalization Check

**Goal:** Assess how many variants require normalization before running bcftools norm.

**Approach:** Iterate with cyvcf2 and count multiallelic sites and complex (MNP) variants.

```python
from cyvcf2 import VCF

def needs_normalization(variant):
    if len(variant.ALT) > 1:
        return True
    ref, alt = variant.REF, variant.ALT[0]
    if len(ref) > 1 and len(alt) > 1 and len(ref) == len(alt):
        return True
    return False

total, needs_norm, multiallelic, mnps = 0, 0, 0, 0
for variant in VCF('input.vcf.gz'):
    total += 1
    if len(variant.ALT) > 1:
        multiallelic += 1
    ref, alt = variant.REF, variant.ALT[0]
    if len(ref) > 1 and len(alt) > 1 and len(ref) == len(alt):
        mnps += 1
    if needs_normalization(variant):
        needs_norm += 1

print(f'Total variants: {total}')
print(f'Needing normalization: {needs_norm} ({needs_norm/total*100:.1f}%)')
print(f'  Multiallelic sites: {multiallelic}')
print(f'  MNPs: {mnps}')
```

Note: this check does not detect indels requiring left-alignment, since that requires reference context. The count is a lower bound.

## Quick Reference

| Task | Command |
|------|---------|
| Left-align indels | `bcftools norm -f ref.fa in.vcf.gz` |
| Split multiallelic | `bcftools norm -m-any in.vcf.gz` |
| Join to multiallelic | `bcftools norm -m+any in.vcf.gz` |
| Atomize MNPs | `bcftools norm --atomize in.vcf.gz` |
| Fix REF alleles | `bcftools norm -f ref.fa -c s in.vcf.gz` |
| Remove duplicates | `bcftools norm -d exact in.vcf.gz` |
| Full pipeline | `bcftools norm --atomize \| bcftools norm -m- \| bcftools norm -f ref.fa` |

## Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `REF does not match` | Wrong reference or genome build mismatch | Verify the reference FASTA matches the build used during calling |
| `not sorted` | Unsorted input | Run `bcftools sort` first |
| `duplicate records` | Same position twice after splitting | Use `-d exact` to remove |
| `--atomize` unrecognized | bcftools < 1.12 | Upgrade bcftools, or use `vt decompose_blocksub` as alternative |
| Split records carry wrong per-allele AF/AD | custom field mis-declared `Number=.` | Fix the header `Number` to `A`/`R`/`G` so bcftools subsets it on split |
| HGVS `c.` position disagrees with VCF POS | left-align (5' genomic) vs HGVS 3'-rule (transcript) | Expected; let the annotation engine emit HGVS, never hand-derive from POS |

## Related Skills

- variant-calling/variant-calling - Generate VCF files from alignments
- variant-calling/filtering-best-practices - Filter after normalization
- variant-calling/vcf-manipulation - Merge, intersect, and compare VCFs
- variant-calling/variant-annotation - Annotate normalized variants against databases
- variant-calling/gatk-variant-calling - GATK HaplotypeCaller workflow (does not emit MNPs)
- variant-calling/clinical-interpretation - ClinVar lookup requires normalized representation
- alignment-files/sam-bam-basics - BAM format and reference genome handling

## References

- Tan A, Abecasis GR, Kang HM. Unified representation of genetic variants. *Bioinformatics.* 2015;31(13):2202-2204. doi:10.1093/bioinformatics/btv112 (formal normalization definition: parsimony + left-alignment, and the `vt normalize` algorithm)
<!-- END FILE: variant-calling/variant-normalization/SKILL.md -->

## 子目录：variant-calling/vcf-basics

<!-- BEGIN FILE: variant-calling/vcf-basics/SKILL.md -->
---
name: bio-vcf-basics
description: View, query, and interpret VCF/BCF variant files with bcftools and cyvcf2. Use when inspecting variants, extracting fields with query format strings, converting VCF/BCF, or correctly reading a field -- QUAL (site) vs GQ (genotype) vs PL/GL likelihoods, AD vs DP and allele balance, GT phasing/ploidy/PS and missing-vs-hom-ref, INFO/FORMAT Number A/R/G semantics, symbolic alleles (<DEL>, <NON_REF>, spanning *) and END, or telling a raw gVCF apart from a filtered callset.
tool_type: cli
primary_tool: bcftools
---

## Version Compatibility

Reference examples tested with: bcftools 1.19+, cyvcf2 0.30+, numpy 1.26+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# VCF/BCF Basics

**"Show me and extract fields from this VCF"** -> Parse the VCF/BCF format, then view, subset, or pull specific columns into a flat table.
- CLI: `bcftools view` / `bcftools query -f`
- Python: `cyvcf2.VCF` (iterate records with attribute access)

## The governing principle

A VCF field is only meaningful once its LEVEL and its `Number` are known. QUAL is a site-level property; GQ, PL, AD, DP, GT are per-sample. QUAL and GQ answer different questions and are NOT interchangeable. A field's header `Number` (A/R/G/.) dictates how many values it carries and how it must be re-subset after a multiallelic split. And several encodings are load-bearing traps: `.` (missing) is never `0/0` (hom-ref); a bare `*` ALT is a spanning-deletion placeholder, not an allele; a gVCF `<NON_REF>` record is a reference-confidence intermediate, not a filtered call. Read the header, read the Number, read the level -- a structurally valid VCF read at the wrong level silently produces wrong numbers with no error.

## Format Overview

| Format | Description | Use Case |
|--------|-------------|----------|
| VCF | Text format, human-readable | Debugging, small files |
| VCF.gz | Compressed VCF (bgzip) | Standard distribution |
| BCF | Binary VCF | Fast processing, large files |

## VCF Format Structure

```
##fileformat=VCFv4.2
##INFO=<ID=DP,Number=1,Type=Integer,Description="Total Depth">
##FORMAT=<ID=GT,Number=1,Type=String,Description="Genotype">
##FORMAT=<ID=DP,Number=1,Type=Integer,Description="Read Depth">
#CHROM  POS     ID      REF     ALT     QUAL    FILTER  INFO    FORMAT  SAMPLE1
chr1    1000    rs123   A       G       30      PASS    DP=50   GT:DP   0/1:25
```

### Header Lines (##)
- `##fileformat` - VCF version
- `##INFO` / `##FORMAT` - INFO / FORMAT field definitions (ID, Number, Type)
- `##FILTER` - Filter definitions
- `##contig` - Reference contigs (required for region indexing and contig order)
- `##reference` - Reference genome

### The Header Contract

Every INFO/FORMAT tag used in the body MUST be declared in a `##INFO`/`##FORMAT` line giving its ID, Number, and Type; parsers (bcftools, cyvcf2, pysam) read these declarations to know how many values a field holds and how to type it. An out-of-sync header -- a tag used but not declared, or declared with the wrong Number/Type -- silently breaks parsing: a `Number=1` declaration over data that holds a vector, or a missing `##contig`, makes tools drop, mistype, or mis-subset values with NO error thrown. After any hand-edit or annotation that adds a field, update the header to match (`bcftools +fill-tags` and `bcftools annotate` manage this automatically).

### Data Columns

| Column | Description |
|--------|-------------|
| CHROM | Chromosome |
| POS | 1-based position of the first base in REF (contrast BED's 0-based half-open) |
| ID | Variant identifier (e.g., rs number) or `.` if novel |
| REF | Reference allele (matches the reference exactly) |
| ALT | Alternate allele(s), comma-separated. `*` = allele missing due to an overlapping deletion at this site |
| QUAL | Phred-scaled quality of the ALT assertion, `-10*log10 P(no variant)`; higher = more confident a variant exists (site-level, NOT per-sample) |
| FILTER | PASS or semicolon-separated filter names. `.` means filters were not applied |
| INFO | Semicolon-separated key=value pairs (site-level annotations) |
| FORMAT | Colon-separated format keys defining per-sample field order |
| SAMPLE | Colon-separated values matching FORMAT order |

## Critical Field Interpretation

What each field actually measures -- and what it does not -- drives every filtering and interpretation decision. QUAL, GQ, and PL answer three DIFFERENT questions.

### QUAL vs GQ vs PL/GL: three different confidences

| Field | Level | Scale | Question answered |
|-------|-------|-------|-------------------|
| QUAL (col 6) | Site | Phred: `-10*log10 P(no variant)` | "Is there ANY variant at this site?" |
| GQ (FORMAT) | Genotype | Phred, capped at 99 | "Is THIS sample's assigned genotype correct?" |
| PL (FORMAT) | Genotype | Phred, rebased to min=0 | Relative likelihood of every possible genotype |
| GL (FORMAT) | Genotype | log10, `<=0`, raw | Same info as PL, unscaled (`PL = -10*GL`, rebased) |

QUAL is computed once across all samples and SCALES with total depth, so a high-coverage artifact can carry a large QUAL -- hence QD (QUAL normalized by depth) is preferred for filtering. GQ is per-sample and does not scale with cohort size. They are NOT interchangeable: QUAL can be high while an individual genotype is uncertain (low GQ), and a sample can have a confident genotype (high GQ) at a site with only moderate QUAL. Filter site-level junk on QUAL/QD; no-call untrustworthy genotypes on GQ.

### PL/GL, and how GQ is derived

PL holds phred-scaled genotype likelihoods, rebased so the CALLED (most likely) genotype is exactly 0 and every other value is its phred penalty relative to that call. For a biallelic diploid site PL is ordered `[PL(0/0), PL(0/1), PL(1/1)]` -- the index of the 0 IS the genotype the caller assigned. GL is the same information as raw log10 likelihoods (`<=0`, larger is better). GQ = the difference between the two SMALLEST PL values, i.e. phred confidence in the call versus the next-best genotype; GQ=0 means the top two genotypes are tied (uninformative), GQ is capped at 99 by convention.

For a site with n alleles, diploid genotype `j/k` (j<=k) sits at PL index `k*(k+1)/2 + j` (this is the `Number=G` ordering). Getting this index formula wrong is the classic bug when re-parsing PL after a multiallelic split -- the vector must be re-subset by the formula, never sliced positionally.

### AD vs DP, and allele balance

AD (FORMAT, `Number=R`) is per-allele read depth `[ref_depth, alt1_depth, ...]`, REF first. DP is total depth. `sum(AD)` is often LESS than DP -- expected, not an error:
- DP counts all reads spanning the position, including uninformative reads (low base quality, ambiguous alignment, filtered reads).
- AD counts only reads that confidently support a specific allele.
- INFO/DP (site-level, summed across samples) differs from FORMAT/DP (per-sample).

Allele balance for a het is DERIVED from AD (GATK does not emit it directly): `AB = alt_AD / (ref_AD + alt_AD)`. A true het sits near 0.5; hets far from 0.5 (e.g. `<0.2` or `>0.8`) suggest a mapping artifact, CNV, or contamination.

### INFO/FORMAT Number semantics (A / R / G / .)

Every `##INFO`/`##FORMAT` header declares a `Number` telling a parser how many values a field holds AND how to re-subset it when a multiallelic record is split:

| Number | One value per | Examples | On multiallelic split |
|--------|---------------|----------|-----------------------|
| `A` | ALT allele | AF, AC | take the k-th element for the k-th ALT |
| `R` | allele incl. REF | AD | REF value first, then per-ALT (off-by-one vs A) |
| `G` | genotype | PL, GL | re-subset via the `k*(k+1)/2+j` index formula |
| `.` | variable/unknown | -- | parser CANNOT auto-subset; carried whole onto every record |
| `0` | flag (presence only) | -- | -- |

Load-bearing for correctness: `bcftools norm -m-` uses these codes to reapportion fields on split. A field mis-declared `Number=.` when it is really `A` keeps its full multiallelic vector on every split record, so downstream tools read the WRONG allele's value with no error. See variant-calling/variant-normalization for split/join reapportionment.

### Key INFO Annotations for Filtering

| Annotation | Meaning | What It Detects |
|-----------|---------|-----------------|
| QD | QUAL / allele depth | Low values suggest variant quality not supported by reads |
| FS | Fisher strand bias (phred-scaled) | Variant reads predominantly on one strand (artifact) |
| SOR | Strand odds ratio | Same as FS but handles high-depth sites better |
| MQ | Root mean square mapping quality | Low values indicate reads map ambiguously (paralogous regions) |
| MQRankSum | MQ difference: ref vs alt reads | Very negative = alt reads map much worse than ref (suspicious) |
| ReadPosRankSum | Read position: ref vs alt reads | Very negative = variant only at read ends (misalignment artifact) |

## Genotype Encoding

| Genotype | Meaning |
|----------|---------|
| `0/0` | Homozygous reference (confidently called ref) |
| `0/1` | Heterozygous |
| `1/1` | Homozygous alternate |
| `1/2` | Heterozygous for two different ALT alleles (compound het at multiallelic site) |
| `./.` | Missing genotype (no confident call) |
| `0\|1` | Phased heterozygous (allele before `\|` is on haplotype 1) |

### Phased vs Unphased

- `/` separates **unphased** alleles -- the two chromosomal copies are known, but which came from which parent is not
- `|` separates **phased** alleles -- haplotype assignment is known (read-backed phasing, trio analysis, or long-read sequencing)
- Phasing matters for compound heterozygosity: two variants in a gene are pathogenic together only if on different haplotypes (in *trans*), not the same haplotype (in *cis*)

### Phase Sets (PS)

A `|` is only meaningful WITHIN a phase set. The FORMAT/PS tag (an integer, usually the POS of the block's first variant) groups variants phased relative to EACH OTHER; `0|1` in two different PS blocks are not guaranteed to lie on the same physical haplotype. Read-backed phasers (WhatsHap) and trio phasing emit PS. A `|` with no consistent PS across records carries no global phase -- a subtle trap when merging phased VCFs.

### Ploidy and Missing vs Hom-Ref

Ploidy is read from the NUMBER of alleles in GT: `0/1` diploid, `0` haploid (chrY, chrM, male chrX outside the PAR), `0/1/1` triploid. Per-region ploidy (PAR, chrX in males, mito) must match the sample karyotype.

`.` (missing) is NOT reference. `./.` = no-call (genotype could not be determined, usually low depth); `0/0` = confidently called homozygous reference. Treating `./.` as `0/0` inflates the reference-allele count and biases allele frequencies, missingness, and burden tests. This is load-bearing: never impute `./.` as reference. In a gVCF, the ABSENCE of a record also does not mean reference -- see the reference-confidence model below.

### Multiallelic Genotypes

At multiallelic sites (e.g. ALT = G,T), allele indices reference the comma-separated ALT list: 0=REF, 1=first ALT, 2=second ALT. `1/2` means one copy of each ALT. Splitting multiallelics into biallelic records with `bcftools norm -m-` converts `1/2` into two `0/1` records, losing compound-heterozygosity information -- see variant-calling/variant-normalization for caveats.

## Symbolic Alleles, END, and Spanning Deletions

Not every ALT spells out a sequence. Symbolic alleles are angle-bracketed placeholders for events whose sequence is not given inline:

| ALT | Meaning |
|-----|---------|
| `<DEL>` `<DUP>` `<INS>` `<INV>` `<CNV>` | Structural-variant classes (sequence not spelled out) |
| `<NON_REF>` | gVCF: "any allele not yet observed" (reference-confidence model) |
| `<*>` | Same role as `<NON_REF>` in some callers' gVCF/mpileup output |
| `*` (bare) | Spanning deletion: allele MISSING because an upstream deletion on ANOTHER line overlaps this position |

Two parsing traps:
- `INFO/END` gives the end coordinate of a symbolic/large event. A tool that infers a record's span from `len(REF)` is WRONG for symbolic alleles -- it must read END. gVCF reference blocks also use END to mark the last position of the band.
- The bare `*` ALT is interpretable only relative to the overlapping deletion on another record; it is not a real alternate allele here. Splitting/subsetting can strand a `*` from the deletion it references (see variant-calling/variant-normalization).

### gVCF and the `<NON_REF>` Reference-Confidence Model

A gVCF (GATK HaplotypeCaller `-ERC GVCF`) is fundamentally different from a filtered callset: it emits a record for EVERY position or block, not just variant sites. Non-variant stretches are compressed into END-delimited blocks (bands) grouped by GQ, so a gVCF is not one line per base.

- Every record carries a symbolic `<NON_REF>` ALT with PL/AD computed against "any unseen allele." This lets joint genotyping evaluate a site in THIS sample even when the variant was only discovered in ANOTHER cohort sample -- the `<NON_REF>` likelihood supplies the evidence.
- Its purpose is to distinguish, at every site, confident homozygous reference from no-data/no-call -- solving the missing-vs-reference problem when squaring off a cohort matrix.
- A gVCF is NOT ready for analysis; it is an intermediate. It must be joint-genotyped (`GenomicsDBImport`/`CombineGVCFs` -> `GenotypeGVCFs`) to yield a normal VCF. Do NOT filter, annotate, or count variants on a raw gVCF, and never build a multi-sample callset by `bcftools merge`-ing single-sample project VCFs when gVCF joint-genotyping is available -- merging fabricates hom-ref genotypes. See variant-calling/joint-calling.

## bcftools view

**Goal:** View, subset, and convert VCF/BCF files from the command line.

**Approach:** Use `bcftools view` with flags for header control, region selection, sample extraction, and format conversion.

```bash
bcftools view input.vcf.gz | head           # full records
bcftools view -h input.vcf.gz               # header only
bcftools view -H input.vcf.gz | head        # skip header
bcftools view input.vcf.gz chr1:1000000-2000000   # region (needs index)
bcftools view -s sample1,sample2 input.vcf.gz      # keep samples
bcftools view -s ^sample3 input.vcf.gz             # exclude samples
```

## bcftools query

**Goal:** Extract specific fields from a VCF in a custom tabular format.

**Approach:** Use `bcftools query -f` with format specifiers for CHROM, POS, INFO, and FORMAT fields. Square brackets `[...]` loop over samples.

```bash
bcftools query -f '%CHROM\t%POS\t%REF\t%ALT\n' input.vcf.gz
bcftools query -f '%CHROM\t%POS\t%INFO/DP\t%INFO/AF\n' input.vcf.gz
bcftools query -f '%CHROM\t%POS[\t%GT]\n' input.vcf.gz              # per-sample GT
bcftools query -f '%CHROM\t%POS[\t%SAMPLE=%GT]\n' -s sample1 input.vcf.gz
bcftools query -H -f '%CHROM\t%POS\t%REF\t%ALT\n' input.vcf.gz     # column header
```

### Common Format Specifiers

| Specifier | Description |
|-----------|-------------|
| `%CHROM` `%POS` `%ID` | Position fields |
| `%REF` `%ALT` | Alleles |
| `%QUAL` `%FILTER` | Site quality / filter status |
| `%INFO/TAG` | INFO field value |
| `%TYPE` | Variant type (snp, indel, etc.) |
| `[%GT]` `[%DP]` `[%AD]` `[%GQ]` | Per-sample FORMAT fields (loop in `[...]`) |
| `[%SAMPLE]` | Sample name |
| `\n` `\t` | Newline / tab |

## Format Conversion and Indexing

**Goal:** Convert between VCF, compressed VCF, and BCF, and index for region queries.

**Approach:** Use `bcftools view` output flags (`-Ov/-Oz/-Ou/-Ob`), then bgzip + index.

```bash
bcftools view -Ob -o output.bcf input.vcf.gz   # VCF -> BCF
bcftools view -Ov -o output.vcf input.bcf      # BCF -> VCF
bgzip input.vcf                                 # -> input.vcf.gz (bgzip, NOT gzip)
bcftools index input.vcf.gz                     # -> .csi index
bcftools index -t input.vcf.gz                  # -> .tbi (tabix) index
```

### Output Format Options

| Flag | Format |
|------|--------|
| `-Ov` | Uncompressed VCF |
| `-Oz` | Compressed VCF (bgzip) |
| `-Ou` | Uncompressed BCF (fast piping) |
| `-Ob` | Compressed BCF |

BCF is the binary encoding of VCF: faster to parse and smaller for large callsets. Region queries (`chr1:1-1000`) require a bgzipped+indexed VCF or a BCF -- plain `.gz` (gzip) is not seekable and fails.

## cyvcf2 Python Alternative

**Goal:** Read, query, and write VCF files programmatically in Python.

**Approach:** Use cyvcf2's `VCF` reader to iterate variants with attribute access to fields, and `Writer` to emit filtered output.

**"Parse this VCF in Python"** -> Open with cyvcf2 and iterate variant records.

### Open, Iterate, and Access Fields
```python
from cyvcf2 import VCF

vcf = VCF('input.vcf.gz')
for variant in vcf:
    # ALT is a list; QUAL is site-level and may be None
    print(variant.CHROM, variant.POS, variant.REF, variant.ALT)
    print(variant.ID, variant.QUAL, variant.FILTER, variant.var_type)
    dp = variant.INFO.get('DP')   # INFO field, None if absent
    af = variant.INFO.get('AF')
    break
vcf.close()
```

### Access Genotypes and Per-Sample Fields
```python
from cyvcf2 import VCF

vcf = VCF('input.vcf.gz')
samples = vcf.samples
for variant in vcf:
    # gt_types: 0=HOM_REF, 1=HET, 2=UNKNOWN(missing), 3=HOM_ALT
    gts = variant.gt_types
    depths = variant.format('DP')   # numpy array, one row per sample
    gqs = variant.format('GQ')      # per-sample genotype quality
    ad = variant.format('AD')       # per-allele depth, Number=R
    print(dict(zip(samples, gts)))
    break
vcf.close()
```

Note: cyvcf2 codes missing genotypes as `gt_types == 2` (UNKNOWN) -- treat that as no-call, never as HOM_REF.

### Fetch Region and Read the Header
```python
from cyvcf2 import VCF

vcf = VCF('input.vcf.gz')
print(vcf.samples, vcf.seqnames)      # sample names, contig names
for info in vcf.header_iter():
    if info['HeaderType'] == 'INFO':
        print(info['ID'], info['Description'])
for variant in vcf('chr1:1000000-2000000'):   # requires an index
    print(variant.CHROM, variant.POS)
```

### Write Filtered VCF
```python
from cyvcf2 import VCF, Writer

vcf = VCF('input.vcf.gz')
writer = Writer('output.vcf', vcf)   # inherit the input header
for variant in vcf:
    if variant.QUAL is not None and variant.QUAL > 30:   # QUAL is site-level
        writer.write_record(variant)
writer.close()
vcf.close()
```

## Quick Reference

| Task | bcftools | cyvcf2 |
|------|----------|--------|
| View VCF | `bcftools view file.vcf.gz` | `VCF('file.vcf.gz')` |
| View header | `bcftools view -h file.vcf.gz` | `vcf.header_iter()` |
| Get region | `bcftools view file.vcf.gz chr1:1-1000` | `vcf('chr1:1-1000')` |
| Query fields | `bcftools query -f '%CHROM\t%POS\n'` | Loop with properties |
| Count variants | `bcftools view -H file.vcf.gz \| wc -l` | `sum(1 for _ in vcf)` |
| VCF to BCF | `bcftools view -Ob -o out.bcf in.vcf.gz` | Use Writer |

## Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `no BGZF EOF marker` | Not bgzipped (plain gzip) | Recompress with `bgzip`, not `gzip` |
| `index required` / region query fails | Missing index | Run `bcftools index` (`-t` for tabix) |
| `sample not found` | Wrong sample name | Check with `bcftools query -l` |
| INFO/FORMAT field missing or mistyped | Header out of sync with body | Fix `##INFO`/`##FORMAT` Number/Type; use `bcftools +fill-tags` |
| Every hom-alt or missing site vanishes on filter | Treated `.`/`./.` as failing or as ref | Missing != hom-ref; make missing pass, never impute `0/0` |
| Wrong allele's AF/AD after split | `Number=.` field not re-subset | Declare the true `Number` (A/R/G) so bcftools reapportions |

## Related Skills

- variant-calling/variant-calling - Generate VCF from alignments
- variant-calling/variant-normalization - Split multiallelics, left-align, Number-code reapportionment
- variant-calling/filtering-best-practices - Filter variants by site (QUAL/QD) and genotype (GQ/DP)
- variant-calling/joint-calling - gVCF reference-confidence model and joint genotyping
- variant-calling/vcf-manipulation - Merge, concat, intersect VCFs
- alignment-files/pileup-generation - Generate pileup for calling

## References

- Danecek P, Auton A, Abecasis G, et al. The variant call format and VCFtools. *Bioinformatics.* 2011;27(15):2156-2158. doi:10.1093/bioinformatics/btr330 (VCF format definition)
- Danecek P, Bonfield JK, Liddle J, et al. Twelve years of SAMtools and BCFtools. *GigaScience.* 2021;10(2):giab008. doi:10.1093/gigascience/giab008 (bcftools view/query/norm reference)
- The Variant Call Format Specification (VCFv4.3/4.4). GA4GH / samtools hts-specs. https://samtools.github.io/hts-specs/ (symbolic alleles, END, `*` overlapping-deletion allele, Number=A/R/G, PL/GL/GQ, gVCF `<NON_REF>`)
<!-- END FILE: variant-calling/vcf-basics/SKILL.md -->

## 子目录：variant-calling/vcf-manipulation

<!-- BEGIN FILE: variant-calling/vcf-manipulation/SKILL.md -->
---
name: bio-vcf-manipulation
description: Combine, split, sort, intersect, and subset VCF/BCF files with bcftools merge, concat, isec, sort, view, and reheader. Use when merging different samples into a cohort VCF, concatenating per-chromosome or per-region call sets for the same samples, intersecting or complementing call sets from different callers, subsetting samples/regions, harmonizing sample names and ##contig headers, or recomputing AC/AN/AF after subsetting. Covers the normalize-before-combine rule, the single-sample-merge 0/0-fabrication trap (merge is not joint genotyping), merge vs concat vs isec selection, and the --naive concat and -R-vs-T region caveats. Not for structural-variant merging by breakpoint fuzz (see variant-calling/structural-variant-calling) or joint genotyping of gVCFs (see variant-calling/joint-calling).
tool_type: cli
primary_tool: bcftools
---

## Version Compatibility

Reference examples tested with: bcftools 1.19+, cyvcf2 0.30+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

The `+fill-tags` plugin ships with bcftools; `--naive-force` and `-m snp-ins-del` are recent additions -- confirm with `bcftools concat --help` / `bcftools merge --help` on the installed build.

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# VCF Manipulation

Combine, split, sort, intersect, and subset VCF/BCF files with bcftools.

**"Combine, compare, or restructure my VCFs"** -> Pick the operation from what changes (samples vs regions vs set membership), and normalize first so the same biological variant is recognized as the same row.
- CLI: `bcftools merge` (add samples), `bcftools concat` (add regions), `bcftools isec` (set operations), `bcftools view` (subset), `bcftools sort` / `bcftools reheader` (order and header fixes)

## The governing principle: normalize BEFORE combining

Every combine operation here -- merge, concat `-d` dedup, isec, and downstream annotate -- keys on the `(CHROM, POS, REF, ALT)` tuple, and `bcftools isec` defaults to `-c none` (an ALT must match exactly to count as the same variant). An indel that is not left-aligned + parsimonious, an un-split multiallelic, or an un-decomposed MNP is a **structurally valid** VCF line carrying a *different* tuple for the *same* biological event. The combine then silently mis-joins: isec reports false discordance, merge emits duplicate rows and splits the allele frequency, dedup misses the duplicate. Nothing errors -- the counts are simply wrong.

Decision: **normalize (left-align + parsimony against the SAME reference, split multiallelics) every input before any merge/concat-dedup/isec/annotate.** This matters most for indels in homopolymers/STRs, where callers legitimately disagree on POS. It is safe to skip only when a single caller produced all inputs and no cross-file matching or database lookup follows. The canonical incantation is `bcftools norm -m-any -f ref.fa`; see variant-calling/variant-normalization for the full pipeline, MNP atomization, and the vt-vs-bcftools discordance -- do NOT re-derive that here, cross-reference it.

## merge vs concat vs isec (choose by what differs)

| Operation | Inputs differ in | Produces | Requires index | Fails / misused when |
|-----------|------------------|----------|----------------|----------------------|
| `bcftools merge` | **samples** (same sites) | one multi-sample VCF (columns unioned) | yes | given the SAME sample split by region -> use concat; given single-sample VCFs and treated as joint genotyping -> fabricates 0/0 (see trap below) |
| `bcftools concat` | **regions** (same samples, e.g. per-chromosome) | one VCF spanning all regions (rows appended) | only with `-a` | inputs from DIFFERENT samples -> use merge; inputs overlap without `-a`; `--naive` used when headers/sample-order differ |
| `bcftools isec` | neither -- same cohort, compare membership | per-input private/shared partition dirs | yes | inputs not normalized to identical representation -> false discordance |

Common confusion: `concat -a` (`--allow-overlaps`) resolves duplicate records from the SAME sample across overlapping region files; it does NOT union genotypes across different samples -- that is merge. If bcftools reports a "different samples" error, the operation is inverted.

## The merge trap: `bcftools merge` is not joint genotyping

When merging single-sample VCFs, a site called in sample A but simply **absent** from sample B's file is ambiguous: was B confidently homozygous reference there, or was B never covered/called? A project VCF cannot answer this. `bcftools merge` fills B's genotype with `./.` (missing) by default, and `-0/--missing-to-ref` overrides it to `0/0` -- but **both are guesses**, because merge has no evidence for the unseen site. `-0` therefore **fabricates** hom-ref genotypes and inflates the reference-allele count (see the vcf-basics `./.`-is-not-`0/0` distinction). Use `-0` only when every input truly covered every site (e.g. gVCF-derived, or a shared target with confirmed coverage), never as a convenience to remove `./.`.

Decision: to build a multi-sample callset with correct hom-ref-vs-no-data resolution, **joint-genotype gVCFs** (`GenomicsDBImport`/`CombineGVCFs` -> `GenotypeGVCFs`), do not `bcftools merge` single-sample project VCFs -- see variant-calling/joint-calling. Reserve `bcftools merge` for combining already-jointly-genotyped cohorts, or samples that share a target with known coverage.

Merge also requires two harmonizations, or it silently drops or mis-collapses records:
- **Consistent representation.** All inputs must be normalized and split the same way first. If cohort A is split biallelic and cohort B keeps multiallelics, merge mis-collapses the shared site. Normalize all inputs identically (governing principle above).
- **Matching `##contig` headers and sample names.** Merge unions sample columns; duplicate sample names abort unless `--force-samples` renames them, and mismatched contig naming (`chr1` vs `1`) prevents sites from aligning. Fix names/contigs with `bcftools reheader` first.

## bcftools merge (combine different samples)

```bash
# Union samples across per-sample (already joint-genotyped or shared-target) VCFs
bcftools merge -l files.txt -Oz -o cohort.vcf.gz    # -l: one VCF path per line
bcftools index cohort.vcf.gz
```

- `-m, --merge` controls multiallelic collapse at shared sites (default `both`): `-m none` keeps a SNP and an indel at one POS as separate records; `-m snps`/`-m indels` restrict which types collapse. Leave the default unless a downstream tool needs types kept apart.
- `--force-samples` disambiguates colliding sample names; `-r chr:beg-end` restricts to a region (inputs must be indexed).

## bcftools concat (stitch regions for the same samples)

```bash
# Genome-wide file from per-chromosome calls (same samples, disjoint regions)
bcftools concat chr{1..22}.vcf.gz chrX.vcf.gz -Oz -o genome.vcf.gz
```

- `-a, --allow-overlaps` is needed when region files overlap (e.g. windowed calling); pair with `-d/--rm-dups <snps|indels|both|all|exact>` to output a duplicate once. `-a` requires indexed inputs.
- `-n, --naive` concatenates BCF/VCF blocks WITHOUT recompression -- very fast for a large per-chromosome set, but it does only a header-compatibility check and requires identical headers and identical sample order across all files; it cannot reorder or reconcile anything. `--naive-force` skips even the header check and will silently produce a corrupt file if headers differ -- avoid it unless the files were provably produced identically.
- concat does NOT sort across file boundaries; overlapping unsorted inputs need `-a`, and the final file may still need `bcftools sort`.

## bcftools sort (order by CHROM then POS)

```bash
bcftools sort -T /scratch/tmp -m 4G input.vcf.gz -Oz -o sorted.vcf.gz   # -T tempdir, -m spill threshold for large files
```

An unsorted VCF breaks everything downstream: `tabix`/`bcftools index` require coordinate-sorted input to build the index, and merge/isec/`view -r` all depend on that index for random access. Sort after any operation that can leave records out of order (naive concat of misordered files, some reheader edits). `-T`/`-m` bound memory for genome-scale files.

## bcftools isec (set operations on call sets)

```bash
# Normalize BOTH first (governing principle), then partition
bcftools norm -m-any -f ref.fa gatk.vcf.gz     -Oz -o gatk.norm.vcf.gz
bcftools norm -m-any -f ref.fa freebayes.vcf.gz -Oz -o fb.norm.vcf.gz
bcftools isec -p comparison -Oz gatk.norm.vcf.gz fb.norm.vcf.gz
```

`-p dir` writes the four-way partition (`-Oz` to compress):

| File | Contents |
|------|----------|
| `0000.vcf[.gz]` | private to file 1 |
| `0001.vcf[.gz]` | private to file 2 |
| `0002.vcf[.gz]` | shared, file-1 records (file-1 INFO/FORMAT) |
| `0003.vcf[.gz]` | shared, file-2 records (file-2 INFO/FORMAT) |

`0002` and `0003` are the SAME sites with each file's own annotations -- pick by which annotations are needed downstream. Select membership instead of the full partition with `-n` and route records with `-w` (1-based file indices):

| Flag | Meaning |
|------|---------|
| `-n=2 -w1` | present in exactly 2 files, output file-1 records |
| `-n+2 -w1` | present in >=2 files |
| `-n~10 -w1` | present in file1 but NOT file2 (boolean mask) |
| `-C` | complement: positions only in file1, missing in the rest |

`-c, --collapse` sets what counts as "the same record"; the default `none` demands an exact REF+ALT match (why normalization is mandatory first), whereas `-c all` matches on position alone and ignores ALT -- rarely what a caller comparison wants.

## Subsetting samples and regions (`bcftools view`)

```bash
bcftools view -s sample1,sample2 input.vcf.gz -Oz -o subset.vcf.gz   # -s ^s3 to EXCLUDE; -S file for a list
bcftools view -r chr1:1e6-2e6      input.vcf.gz -Oz -o region.vcf.gz  # -R file.bed for many regions
```

Two nuances that bite:
- **`-r`/`-R` (regions) vs `-t`/`-T` (targets).** `-r`/`-R` use the index to JUMP to regions (fast, require an index) and consider both POS and an indel's end; `-t`/`-T` STREAM the whole file filtering on POS (no index needed, slower). With `-R`, overlapping regions in the BED can emit a record MORE THAN ONCE and out of order -- deduplicate/sort after, or use non-overlapping regions.
- **Stale INFO counts after subsetting.** Dropping samples makes INFO `AC/AN/AF` wrong. `bcftools view -s` updates `AC/AN` by default (unless `-I/--no-update`), but recompute the full tag set explicitly: `bcftools +fill-tags subset.vcf.gz -Oz -o out.vcf.gz -- -t AC,AN,AF`.

## Header harmonization (`bcftools reheader`)

```bash
printf 'old_name\tnew_name\n' > rename.txt
bcftools reheader -s rename.txt input.vcf.gz -o renamed.vcf.gz   # -s renames samples only, no record rewrite
```

`reheader` rewrites only the header (fast, no record pass): `-s` maps sample names, `-h` swaps in a whole new header, `-f ref.fa.fai` fixes `##contig` lines to match a reference. Harmonize sample names and contigs BEFORE merge so columns and sites align.

## Structural variants merge differently -- do NOT use `bcftools merge`

For SVs (`<DEL>`/`<DUP>`/`<INV>`/BND), "the same event" is fuzzy: breakpoints disagree by CIPOS/CIEND margins, so tuple-exact bcftools operations treat one deletion called by two tools as two variants. SV merging needs coordinate-and-size (ideally sequence) aware tools -- Truvari, SURVIVOR, or Jasmine -- whose distance/size parameters ARE the result. Use bcftools here only for small variants; route SV consensus to variant-calling/structural-variant-calling.

## Quick Reference

| Task | Command |
|------|---------|
| Union samples | `bcftools merge -l files.txt -Oz -o cohort.vcf.gz` |
| Stitch regions | `bcftools concat chr{1..22}.vcf.gz -Oz -o genome.vcf.gz` |
| Fast stitch (identical headers) | `bcftools concat --naive chr*.bcf -Ob -o all.bcf` |
| Sort | `bcftools sort -T tmp input.vcf -Oz -o sorted.vcf.gz` |
| Compare callers | `bcftools isec -p dir a.norm.vcf.gz b.norm.vcf.gz` |
| Shared only | `bcftools isec -n=2 -w1 a.vcf.gz b.vcf.gz -Oz -o shared.vcf.gz` |
| Subset samples | `bcftools view -s s1,s2 in.vcf.gz -Oz -o out.vcf.gz` |
| Recompute AC/AN/AF | `bcftools +fill-tags in.vcf.gz -- -t AC,AN,AF` |
| Rename samples | `bcftools reheader -s names.txt in.vcf.gz` |

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| `different samples` on concat | merge/concat inverted (different samples given to concat) | Use merge for samples, concat for regions |
| False discordance in isec | inputs not normalized to one representation | `bcftools norm -m-any -f ref.fa` both first (see variant-normalization) |
| Duplicate rows / split AF after merge | inputs represented inconsistently, or un-normalized indels | Normalize + split all inputs identically before merge |
| Fabricated `0/0` genotypes, inflated ref-allele count | `-0/--missing-to-ref` on single-sample merge (not joint genotyping) | Drop `-0`; joint-genotype gVCFs instead (joint-calling) |
| `not sorted` / index build fails | unsorted records | `bcftools sort` then re-index |
| `--naive` output corrupt | headers or sample order differ across inputs | Reheader to a common header, or drop `--naive` |
| Records duplicated / out of order after `-R` | overlapping regions in the BED | Use non-overlapping regions, then sort/dedup |
| Sample-name conflict aborts merge | duplicate sample names across files | `--force-samples`, or `reheader -s` first |
| Stale `AF` after subsetting samples | INFO not fully recomputed | `bcftools +fill-tags -- -t AC,AN,AF` |

## Related Skills

- variant-calling/variant-normalization - Normalize (left-align, split, atomize) before any merge/isec -- the load-bearing prerequisite
- variant-calling/joint-calling - Joint-genotype gVCFs instead of merging single-sample VCFs (correct hom-ref vs no-data)
- variant-calling/vcf-basics - VCF fields, the `./.`-is-not-`0/0` distinction, sample/region query
- variant-calling/structural-variant-calling - SV merging by breakpoint fuzz (Truvari/SURVIVOR/Jasmine), not bcftools
- variant-calling/filtering-best-practices - Filter call sets before combining
- variant-calling/vcf-statistics - Sanity-check Ti/Tv and counts after manipulation
- variant-calling/variant-calling - Upstream variant discovery that produces input VCFs

## References

- Danecek P, Bonfield JK, Liddle J, et al. Twelve years of SAMtools and BCFtools. *GigaScience.* 2021;10(2):giab008. doi:10.1093/gigascience/giab008 (bcftools merge/concat/isec/norm/view/reheader reference implementation)
- Tan A, Abecasis GR, Kang HM. Unified representation of genetic variants. *Bioinformatics.* 2015;31(13):2202-2204. doi:10.1093/bioinformatics/btv112 (why normalization before tuple-keyed merge/isec is mandatory)
<!-- END FILE: variant-calling/vcf-manipulation/SKILL.md -->

## 子目录：variant-calling/vcf-statistics

<!-- BEGIN FILE: variant-calling/vcf-statistics/SKILL.md -->
---
name: bio-vcf-statistics
description: Compute and interpret VCF quality-control metrics (Ti/Tv, het/hom, novel/known, missingness, HWE, contamination, relatedness) with bcftools stats, vcftools, plot-vcfstats, and identity tools (somalier, peddy, KING). Use when judging whether a callset is trustworthy, diagnosing a low Ti/Tv or outlier het/hom sample, deciding whether an HWE deviation is error or biology, screening a cohort for sample swaps/contamination/wrong-sex before analysis, or comparing call sets before and after filtering. Not for applying filters (see variant-calling/filtering-best-practices) or normalizing representation (see variant-calling/variant-normalization).
tool_type: cli
primary_tool: bcftools
---

## Version Compatibility

Reference examples tested with: bcftools 1.19+, vcftools 0.1.16+, somalier 0.2.19+, peddy 0.4.8+, cyvcf2 0.30+, numpy 1.26+

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- CLI: `<tool> --version` then `<tool> --help` to confirm flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

Note: `bcftools gtcheck` was rewritten around bcftools 1.10; the old `-G/--GTs-only` flag is gone. Modern gtcheck cross-checks all samples in one file when `-g` is omitted, and uses `-E/--error-probability`. Verify flags against the installed build.

# VCF Statistics

**"Is this callset any good, and are the samples who the manifest says they are?"** -> Summarize variant counts and quality distributions, then read each QC metric as a signal whose expected value is context-dependent.

- CLI: `bcftools stats` (+ `plot-vcfstats`), `vcftools`, `somalier`, `peddy`
- Python: `cyvcf2` for custom per-record statistics

## The governing principle

No QC metric has a universal pass value. Each metric's expected range depends on the assay (WGS vs WES), the sample's ancestry, and the cohort it sits in, so QC is not threshold-checking but reading a deviation for its mechanistic meaning and acting on it. Three rules follow. First, always compare a sample against a matched cohort (same assay, same inferred ancestry), never against an absolute number. Second, order of operations matters: apply genotype-level filters (set `./.` where GQ/DP/allele-balance fail) BEFORE computing cohort missingness, call rate, or HWE, because low-quality genotypes left in the matrix drive spurious missingness and HWE deviation. Third, sample-identity QC is a graph problem, not a per-sample check: build the all-pairs relatedness matrix and reconcile it against the declared pedigree/manifest, and do this BEFORE any association or burden analysis, because one undetected swap or contaminated sample can fabricate or erase a genome-wide-significant hit.

## QC metric decision table

Expected values are stated conventions (they shift with capture kit, ancestry, reference build, and caller); treat them as starting points and confirm against a matched cohort.

| Metric | Expected (WGS) | Expected (WES) | A deviation MEANS | Action |
|--------|---------------|---------------|-------------------|--------|
| Ti/Tv (overall) | ~2.0-2.1 | ~3.0-3.3 | Low -> false-positive transversions dilute the signal (random errors have Ti/Tv ~0.5); high -> over-filtering removed transversions | Tighten site filters if low; check filter for transversion bias if high |
| Ti/Tv (novel only) | near overall | near overall | Novel Ti/Tv well below the known-site value -> FP contamination in the novel fraction | Raise stringency; the novel set is where FPs concentrate |
| Het/hom ratio | ancestry-dependent (~1.5-1.6 EUR, ~2.0+ AFR) | same | High vs same-ancestry cohort -> contamination or reference bias; low -> inbreeding/consanguinity/ROH or chromosome loss | Stratify by ancestry first; then flag within-ancestry outliers |
| Novel fraction (vs dbSNP) | low for common; high for rare/singleton | same | Novel COMMON variants -> almost always artifacts; high novel rare -> expected or under-studied population | Stratify novel% by frequency; investigate common novels |
| Call rate (per sample) | >95-98% | >95-98% | Low -> low-coverage/low-quality sample | Drop worst samples, then recompute per-variant missingness (iterate) |
| Call rate (per variant) | >95-99% | >95-99% | Low -> site in a hard-to-genotype region | Drop worst variants after sample QC; rare variants tolerate more missing |
| Het allele-balance (hets) | centered on 0.5 | 0.5 | Shifted away from 0.5 + elevated het count -> contamination signature | Confirm with VerifyBamID2 (on the BAM) or CHARR (on the VCF/gVCF) -- the real test |
| Excess-het / HWE | in equilibrium within ancestry | same | EXCESS het -> collapsed paralog/CNV mapping artifact; het DEFICIT -> often real (Wahlund/inbreeding) | Filter on excess het only, within ancestry, in controls; do NOT blanket-filter HWE |
| Relatedness (kinship) | matches manifest | matches manifest | Unexpected high kinship -> sample swap/duplicate; a "replicate" that is not -> mislabel | Reconcile the all-pairs matrix against the pedigree with KING/somalier/peddy |

## bcftools stats

**Goal:** Generate comprehensive variant statistics (counts, Ti/Tv, per-sample het/hom and singletons, indel and depth distributions).

**Approach:** Run bcftools stats and read the section-tagged output lines; add `-s -` for per-sample metrics.

```bash
bcftools stats input.vcf.gz > stats.txt              # cohort-level
bcftools stats -s - input.vcf.gz > per_sample.txt    # per-sample (PSC/PSI lines)
bcftools stats file1.vcf.gz file2.vcf.gz > cmp.txt   # compare two callsets
plot-vcfstats -p qc_plots/ stats.txt                 # render PDF + PNGs (needs matplotlib)
```

Output sections: `SN` summary numbers, `TSTV` transition/transversion, `SiS` singletons, `AF` allele-frequency spectrum, `QUAL` quality distribution, `IDD` indel-length distribution, `ST` substitution types, `DP` depth distribution, `PSC` per-sample counts (hom-ref, het, hom-alt, transitions, transversions, missing), `PSI` per-sample indels.

```bash
bcftools stats input.vcf.gz | grep "^SN"    | cut -f3-   # counts
bcftools stats input.vcf.gz | grep "^TSTV"  | cut -f5     # Ti/Tv ratio
bcftools stats -s - input.vcf.gz | grep "^PSC"           # per-sample het/hom/missing
```

## Ti/Tv ratio

Transitions (purine<->purine A<->G, pyrimidine<->pyrimidine C<->T) are favored over transversions because CpG deamination (methylated C->T) is the single most common vertebrate point mutation and is a transition, and because transitions are more often synonymous. A random error spectrum gives Ti/Tv ~0.5, so a callset diluted with false positives drifts DOWNWARD. WES runs higher than WGS (~3.0-3.3 vs ~2.0-2.1) because coding regions are CpG- and constraint-enriched and transitions at CpGs plus codon degeneracy push the ratio up.

Ti/Tv is the single fastest gross-error smell test. A WES callset reporting Ti/Tv ~2.1 is telling the analyst the filtering is too loose. Stratify: compute Ti/Tv on the novel fraction separately (below) since that is where false positives concentrate. Ancestry and target design shift the exact number, so compare against a matched cohort, not the absolute.

## Het/hom ratio and ancestry

The per-sample het:non-ref-hom ratio reflects heterozygosity relative to the reference, so it is strongly ancestry-dependent: African-ancestry genomes diverge more from GRCh (a mostly European-ancestry assembly) and carry more het calls (commonly ~2.0+), European ancestry sits ~1.5-1.6, and the value shifts across populations. A single global het/hom cutoff is therefore wrong: it would flag every AFR sample in a EUR-tuned pipeline.

Infer ancestry first (peddy/somalier project onto 1000 Genomes PCs), then flag outliers WITHIN each ancestry group. An elevated het/hom versus same-ancestry peers indicates contamination (foreign reads manufacture spurious hets) or reference bias; a depressed het/hom indicates inbreeding/consanguinity, a long run of homozygosity, or chromosome loss.

## Novel/known ratio via dbSNP

Overlapping the callset with dbSNP gives an orthogonal false-positive signal independent of Ti/Tv. Annotate known/novel and stratify by frequency, because the diagnostic differs by allele frequency: novel COMMON variants are almost always artifacts (real common variants are already catalogued), while novel rare/singleton variants are expected and biologically real. A single novel% without frequency stratification is uninformative.

```bash
bcftools annotate -a dbsnp.vcf.gz -c ID input.vcf.gz -Oz -o annotated.vcf.gz
# novel fraction = records with ID "." over total; stratify by INFO/AF
bcftools view -H annotated.vcf.gz | awk '{n++; if($3==".") novel++} END{print "novel:", novel/n}'
```

## Missingness and call rate

Call rate is the fraction of sites with a non-missing genotype for a sample; missingness is its complement. Only `./.` (no-call) counts as missing; `0/0` (confident hom-ref) does NOT, so treating no-call as hom-ref biases allele frequencies. GWAS convention drops samples below ~95-98% call rate and variants below ~95-99% (dataset-dependent conventions).

The iteration trap: sample-level and variant-level missingness are coupled, so applying both thresholds in one pass is wrong. Drop the worst samples, recompute per-variant missingness, drop the worst variants, and repeat. Critically, apply genotype-level filters (`./.` where GQ<20 or DP<8) BEFORE computing cohort missingness or HWE, or low-quality genotypes will drive both.

```bash
vcftools --gzvcf input.vcf.gz --missing-indv --out sample_miss   # .imiss (per-sample)
vcftools --gzvcf input.vcf.gz --missing-site --out site_miss     # .lmiss (per-site)
```

## HWE filtering (excess-het only)

Hardy-Weinberg testing flags genotype frequencies that deviate from p^2:2pq:q^2, but a naive two-sided HWE gate throws away real biology. The discipline:

- **Filter on EXCESS heterozygosity only.** Heterozygote excess is the signature of a mapping artifact: a duplicated/collapsed region piles reads from two paralogous copies onto one locus, manufacturing spurious hets everywhere. Heterozygote DEFICIT, by contrast, is often real (Wahlund effect from substructure, inbreeding, selection, a true null allele). GATK's `ExcessHet` and `InbreedingCoeff` and gnomAD's `ExcessHet` filter the excess side only.
- **Compute within an ancestry-homogeneous subgroup.** Pooling populations with different allele frequencies induces a Wahlund het-deficit that mimics genotyping error; HWE on a mixed cohort filters good variants.
- **Use the EXACT test, not chi-square.** The chi-square approximation is anticonservative for rare variants and small samples; the standard is the Wigginton-Cutler-Abecasis exact test (implemented in vcftools `--hardy` and PLINK).
- **In case/control studies, compute HWE in CONTROLS only.** A true association at a strong-effect locus produces HWE deviation in cases; filtering it removes the hit.

```bash
vcftools --gzvcf controls.vcf.gz --hardy --out hwe               # exact-test P per site
# GATK ExcessHet (phred): larger = more excess het = more suspect
bcftools query -f '%CHROM\t%POS\t%INFO/ExcessHet\n' input.vcf.gz | awk '$3>54.69'
```

The threshold 54.69 is GATK's default ExcessHet cutoff (phred-scaled p ~= 3.4e-6, ~the 1000-sample z=-4.5 boundary); tune it to the cohort size.

## Contamination signatures

Cross-sample contamination is visible in VCF statistics before any dedicated test: the het allele-balance distribution shifts away from 0.5 (foreign reads add minor-allele support at true hom sites and skew true hets), the het count and het/hom ratio rise, and the novel-fraction Ti/Tv drops. These are SIGNALS, not the measurement. The real test runs on the BAM/CRAM: VerifyBamID2 (Zhang et al. 2020) estimates the contamination fraction alpha ancestry-agnostically by modeling observed allele fractions against population frequencies, and CHARR estimates alpha directly from VCF-level reference-read counts at hom-alt sites. An alpha above ~0.02-0.03 is a red flag; somatic pipelines are sensitive to even 1%. GATK pipelines feed `--contamination alpha` from VerifyBamID2. See variant-calling/gatk-variant-calling for wiring contamination estimates into calling.

```bash
# quick het allele-balance sanity check from AD (het genotypes only)
bcftools query -i 'GT="het"' -f '[%AD]\n' input.vcf.gz | \
    awk -F',' '{ab=$2/($1+$2); s+=ab; n++} END{print "mean het AB:", s/n}'   # expect ~0.5
```

## Sample-swap, relatedness, and sex checks (mandatory cohort QC)

Sample swaps are among the most common errors in sequencing studies, so identity QC is not optional. Build the all-pairs relatedness matrix and reconcile it against the manifest; swaps appear as off-diagonal surprises (unexpected relatedness) or on-diagonal failures (a "replicate" that is not).

| Tool | Input | Detects | Notes |
|------|-------|---------|-------|
| `bcftools gtcheck` | VCF | Same-file swaps/duplicates (quick) | Native, no reference panel; discordance score, not a relatedness graph |
| KING (Manichaikul 2010) | PLINK bed | Robust kinship without allele-freq/ancestry assumptions | Reference method; kinship bands below |
| peddy (Pedersen 2017) | VCF + PED | Reported vs inferred sex, relationships, ancestry (PCA on 1000G) | Fast, VCF-only; ideal PED-vs-VCF reconciliation |
| somalier (Pedersen 2020) | BAM/CRAM/VCF | Relatedness/ancestry/sex at scale; cross-checks RNA-seq vs WGS | Tiny per-sample sketches; tens of thousands of samples in seconds |

KING kinship coefficient bands: >0.354 duplicate/MZ twin, [0.177, 0.354] first-degree (parent-child, full sib), [0.0884, 0.177] second-degree, [0.0442, 0.0884] third-degree. A pair not expected to be related at ~0.5 is a swap or duplicate.

```bash
# bcftools: cross-check all samples in one file (no -g), or against a truth VCF (-g)
bcftools gtcheck input.vcf.gz > gtcheck.txt          # DC lines: query, genotyped, discordance, sites
bcftools gtcheck -g reference.vcf.gz query.vcf.gz    # concordance to a genotyping panel

# peddy: PED-vs-VCF sex/relatedness/ancestry, 4 CPUs, HTML + CSVs
python -m peddy -p 4 --plot --prefix cohort_qc input.vcf.gz cohort.ped

# somalier: extract sketches then relate against the pedigree
somalier extract -d extracted/ --sites sites.vcf.gz -f ref.fa input.vcf.gz
somalier relate --ped cohort.ped extracted/*.somalier    # writes an HTML relatedness report
somalier ancestry --labels 1kg-labels.tsv 1kg/*.somalier ++ extracted/*.somalier    # PCA projection (labelled ++ query)

# vcftools: KING-robust kinship directly from a VCF
vcftools --gzvcf input.vcf.gz --relatedness2 --out kin    # .relatedness2 (Manichaikul method)
```

## Stratified evaluation

A caller with 99% overall accuracy may drop to 70% in difficult regions, so single-number accuracy hides where a callset fails. Evaluate stratified by region class using GIAB stratification BED files (github.com/genome-in-a-bottle/genome-stratifications).

```bash
bcftools stats -R easy_regions.bed      input.vcf.gz > easy.txt
bcftools stats -R difficult_regions.bed input.vcf.gz > difficult.txt
```

Key strata and their failure modes: homopolymer runs (systematic indel errors, Illumina/Ion Torrent), tandem repeats / low-complexity (alignment ambiguity inflates FP and FN), segmental duplications (paralogous mapping -> false hets), high-GC >70% / low-GC <25% (coverage-bias missingness), MHC/centromeric (extreme polymorphism or repetitiveness). A drop in Ti/Tv within difficult regions confirms elevated false positives there.

## Quick counts with query

```bash
bcftools view -H input.vcf.gz | wc -l              # total records
bcftools view -v snps   -H input.vcf.gz | wc -l    # SNPs
bcftools view -v indels -H input.vcf.gz | wc -l    # indels
bcftools view -f PASS   -H input.vcf.gz | wc -l    # PASS variants
bcftools query -f '%QUAL\n' input.vcf.gz | awk '{s+=$1;n++} END{print "mean QUAL:", s/n}'
```

See examples/vcf_stats.py for a cyvcf2 script computing counts, Ti/Tv, and mean QUAL in one pass; the usage guide covers per-sample genotype distributions and the allele-frequency spectrum.

## Quick Reference

| Task | Command |
|------|---------|
| Full stats | `bcftools stats input.vcf.gz` |
| Per-sample het/hom/missing | `bcftools stats -s - input.vcf.gz \| grep "^PSC"` |
| Ti/Tv ratio | `bcftools stats input.vcf.gz \| grep "^TSTV" \| cut -f5` |
| Per-sample missingness | `vcftools --gzvcf in.vcf.gz --missing-indv` |
| Exact HWE (controls) | `vcftools --gzvcf controls.vcf.gz --hardy` |
| KING kinship | `vcftools --gzvcf in.vcf.gz --relatedness2` |
| Sex/ancestry/relatedness | `python -m peddy -p 4 --plot --prefix qc in.vcf.gz in.ped` |
| Scalable identity QC | `somalier extract ...` then `somalier relate --ped ...` |
| Plot stats | `plot-vcfstats -p dir stats.txt` |

## Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| Every AFR sample flagged as high het/hom | Single global cutoff across ancestries | Infer ancestry, flag outliers within each group |
| Good variants filtered by HWE | Two-sided HWE on a mixed cohort or on cases | Excess-het only, within ancestry, controls-only |
| Spurious HWE/missingness | Cohort metrics computed before genotype filtering | Set `./.` on low GQ/DP first, then recompute |
| `bcftools gtcheck -G 1` errors | `-G` removed after the 1.10 rewrite | Drop `-G`; cross-check runs by default without `-g` |
| Low Ti/Tv only in novel set | False positives concentrate in novel variants | Raise stringency; recheck against dbSNP overlap |
| `plot-vcfstats not found` / no plots | matplotlib missing or not on PATH | `pip install matplotlib`; check `which plot-vcfstats` |

## Related Skills

- variant-calling/filtering-best-practices - Apply the site and genotype filters these metrics motivate
- variant-calling/gatk-variant-calling - VerifyBamID2 contamination estimate feeding `--contamination`
- variant-calling/variant-normalization - Normalize before comparing or annotating call sets
- variant-calling/vcf-basics - View, query, and understand VCF fields
- variant-calling/vcf-manipulation - Compare and merge call sets
- variant-calling/joint-calling - Cohort genotyping where population QC applies
- alignment-files/bam-statistics - Upstream alignment QC that drives variant statistics

## References

- Danecek P, Bonfield JK, Liddle J, et al. Twelve years of SAMtools and BCFtools. 2021 *GigaScience* 10:giab008. (bcftools stats/gtcheck)
- Danecek P, Auton A, Abecasis G, et al. The variant call format and VCFtools. 2011 *Bioinformatics* 27:2156-2158. (vcftools QC)
- Wigginton JE, Cutler DJ, Abecasis GR. A note on exact tests of Hardy-Weinberg equilibrium. 2005 *American Journal of Human Genetics* 76:887-893. (exact HWE test)
- Manichaikul A, Mychaleckyj JC, Rich SS, et al. Robust relationship inference in genome-wide association studies. 2010 *Bioinformatics* 26:2867-2873. (KING kinship)
- Pedersen BS, Quinlan AR. Who's Who? Detecting and Resolving Sample Anomalies in Human DNA Sequencing Studies with Peddy. 2017 *American Journal of Human Genetics* 100:406-413. (peddy)
- Pedersen BS, Bhetariya PJ, Brown J, et al. Somalier: rapid relatedness estimation for cancer and germline studies using efficient genome sketches. 2020 *Genome Medicine* 12:62. (somalier)
- Zhang F, Flickinger M, Gagliano Taliun SA, et al. Ancestry-agnostic estimation of DNA sample contamination from sequence reads. 2020 *Genome Research* 30:185-194. (VerifyBamID2)
<!-- END FILE: variant-calling/vcf-statistics/SKILL.md -->

<!-- END CATEGORY: variant-calling -->

