---
slug: bio-primer-design-integrated
version: 1.0.0
displayName: "引物设计 / PCR/qPCR primer design"
name: bio-primer-design-integrated
summary: >-
  中文：引物设计综合技能，整合 4 个相关专题，覆盖PCR/qPCR引物设计：primer3-py设计、Tm匹配、特异性检查、二聚体/发夹验证。 English: Integrated PCR/qPCR primer design skill covering 4 related topics, including PCR/qPCR primer design: primer3-py design, Tm matching, specificity checking, dimer/hairpin validation.
description: >-
  中文：这是一个面向引物设计的综合生物信息学 Skill，整合当前分类下 4 个相关专题能力。它用于根据研究问题、数据类型和分析阶段，选择合适的方法与工具，规划从输入检查、预处理、核心分析到质量控制、统计解释和结果报告的完整流程。重点覆盖：PCR/qPCR引物设计：primer3-py设计、Tm匹配、特异性检查、二聚体/发夹验证。当用户提供相关实验数据、测序结果、表格或研究问题时，它会帮助判断分析目标与前置条件，给出工具选择、关键参数、输入输出、常见失败原因、结果解读和可复现建议。主要工具包括：mfeprimer, primer3-py。该 Skill 提供分析设计与实施指导，不替代对具体数据质量、生物学背景和最终结论的人工审查。
  English: This is an integrated bioinformatics Skill for PCR/qPCR primer design, combining 4 related topic areas. It helps users choose appropriate methods and tools based on the research question, data type, and analysis stage, and plan an end-to-end workflow from input validation and preprocessing through core analysis, quality control, statistical interpretation, and reporting. It covers PCR/qPCR primer design: primer3-py design, Tm matching, specificity checking, dimer/hairpin validation. For relevant experimental data, sequencing results, tables, or research questions, it clarifies prerequisites, recommends tools and parameters, describes expected inputs and outputs, explains common failure modes, and supports reproducible analysis. Primary tools include: mfeprimer, primer3-py. It provides methodological and implementation guidance; final data-quality assessment and biological conclusions still require human review.
---

# primer-design 分类 Skill 整合版

> 本文件整合同一主分类目录下 4 个子目录中的 SKILL.md 内容。
> 各子目录正文按原文保留，并通过标题和边界标记进行区分；源文件中的元数据块未被改写。

---

<!-- BEGIN CATEGORY: primer-design -->

## 子目录：primer-design/primer-basics

<!-- BEGIN FILE: primer-design/primer-basics/SKILL.md -->
---
name: bio-primer-design-primer-basics
description: Designs and ranks PCR primer pairs for a target template with primer3-py (design_primers), returning pairs with nearest-neighbor Tm, GC, product size, and complementarity scores. Covers why primer3 is a LOCAL weighted-penalty minimizer over the single template supplied (so PRIMER_PAIR_0 is the lowest-penalty pair under the given bounds, never a genome-specificity guarantee), why Tm is a salt/concentration-dependent SantaLucia prediction not a fixed property, why the two primers must be Tm-matched, the seq_args/global_args tag semantics (SEQUENCE_TARGET/INCLUDED/EXCLUDED/OVERLAP_JUNCTION/FORCE_*, 0-based [start,length]), 3'-end and GC-clamp mechanism, 5'-tail handling, masking SNPs under 3' ends, and diagnosing zero-pair runs. Use when designing standard PCR, cloning, genotyping, or sequencing primers, flanking a target, or screening pairs by Tm/size/GC. Genome off-target checking is primer-specificity; dimers/hairpins primer-validation; qPCR and probes qpcr-primers.
tool_type: python
primary_tool: primer3-py
---

## Version Compatibility

Reference examples tested with: primer3-py 2.3+.

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show primer3-py` then `help(primer3.design_primers)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# PCR Primer Design -- Ranked Pairs Under Local Thermodynamic Constraints

**"Design primers to amplify this region"** -> Search candidate primer pairs that satisfy Tm/GC/size/complementarity constraints on the supplied template and rank them by a weighted penalty -- because primer3 sees only that one template, so its top pair certifies LOCAL good behavior, not that the primers bind the target uniquely in the genome.
- Python: `primer3.design_primers(seq_args, global_args)` returns a flat dict of ranked pairs with per-primer Tm/GC and a pair penalty.

Scope: designing and ranking PCR primer pairs for a template under thermodynamic and positional constraints, including cloning (5' tails), genotyping (flanking), and single sequencing primers. Genome-wide off-target / in-silico PCR specificity -> primer-specificity. Dimer/hairpin/end-stability validation of chosen oligos -> primer-validation. qPCR primers and hydrolysis/beacon probes -> qpcr-primers. OUT OF SCOPE: degenerate/consensus primers for divergent targets (primer3 does not model IUPAC degeneracy -- use a dedicated consensus designer); long-range PCR amplicons over ~3-5 kb (different polymerase and primer regime); and bisulfite/methylation (MSP/BSP) primers (different rules -- avoid CpGs in the body, account for C->T strand asymmetry -- use a bisulfite-specific designer such as MethPrimer). Fetching the template -> database-access/entrez-fetch. Reverse-complement / subsequence extraction -> sequence-manipulation/seq-objects.

## The Single Most Important Modern Insight -- PRIMER_PAIR_0 Is the Argmin of a Penalty the User Partly Authors, on the Only Template primer3 Sees

1. **primer3 optimizes locally and is blind to the rest of the genome.** It solves a constrained penalty minimization over the ONE `SEQUENCE_TEMPLATE` string: it scores Tm, GC, length, self-/cross-complementarity, hairpins, and 3'-end stability, then returns the lowest-penalty pairs. It never asks whether those primers also bind 50 other loci. So `PRIMER_PAIR_0` means "lowest penalty under the chosen weights and bounds, on this one template" -- it is a hypothesis, not a result. The catastrophic, common error is ordering the top pair without a genome specificity pass (-> primer-specificity).
2. **Tm is a prediction, not a property.** primer3 computes a nearest-neighbor Tm (SantaLucia 1998 *PNAS* 95:1460) at a specific oligo concentration and salt; change the salt/Mg/DNA-conc inputs and the same sequence reports a different Tm. Use predicted Tm to MATCH the two primers (within ~1-2 C) and to RANK candidates, not as the literal anneal temperature. The single largest predicted-vs-bench divergence is free Mg2+ (dNTPs chelate Mg2+ roughly 1:1, so free Mg2+ ~= total Mg - total dNTP; Owczarzy 2008 *Biochemistry* 47:5336).
3. **Bounds and weights do different jobs.** `PRIMER_MIN_*`/`PRIMER_MAX_*` are HARD filters (a candidate outside them is eliminated); `PRIMER_OPT_*` plus the `PRIMER_WT_*` weights only RANK the survivors. Over-tightening BOUNDS is what returns zero pairs; changing weights only re-orders. The defaults are an opinionated weight vector (Tm and size dominate; GC-percent weights are 0 by default), not an objective truth.

## How primer3 Scores: Weighted Penalty Minimization

Each tunable property has an `OPT` target and a weight (often split into `_LT`/`_GT` for below/above optimum). The per-oligo penalty is the weighted sum of deviations; the pair penalty adds pair terms (`PRIMER_PAIR_WT_DIFF_TM` for Tm mismatch, product-size deviation, cross-complementarity). Pairs are sorted ascending by `PRIMER_PAIR_<i>_PENALTY`; index 0 is the minimum. Two consequences the agent must act on: (a) raise `PRIMER_PAIR_WT_DIFF_TM` if a Tm-matched pair matters more than tight product size, and a different pair rises to index 0; (b) to forbid something use a BOUND, to merely discourage it raise a WEIGHT.

## Tool Taxonomy

| Tool / method | Citation | Mechanism / role | When |
|---------------|----------|------------------|------|
| primer3-py `design_primers` | Untergasser 2012 *Nucleic Acids Res* 40:e115 | constraint-satisfaction search + nearest-neighbor Tm; returns ranked pairs | the default PCR primer designer |
| Nearest-neighbor Tm (SantaLucia) | SantaLucia 1998 *PNAS* 95:1460 | salt/concentration-dependent thermodynamic Tm from stacking parameters | every Tm value primer3 reports |
| primer3 Tm/salt implementation | Koressaar & Remm 2007 *Bioinformatics* 23:1289 | the Tm + divalent-cation salt correction primer3 uses | when matching primer3 Tm to bench conditions |
| Mispriming library (`misprime_lib`) | Untergasser 2012 *Nucleic Acids Res* 40:e115 | penalizes similarity to a curated repeat library (HUMREP/RODENT) | keep primers off known repeats (NOT a genome check) |
| Genome BLAST / in-silico PCR | (route OUT) | predicts off-target amplicons from the PAIR | confirm the pair amplifies only the target -> primer-specificity |

## Decision Tree by Scenario

| Scenario | Recommended | Why |
|----------|-------------|-----|
| Standard amplicon over one target | `design_primers` with `SEQUENCE_TARGET` flanking the feature | both primers flank, amplicon spans the feature |
| Amplify within a clean window (one exon) | `SEQUENCE_INCLUDED_REGION` confines primers | no primer falls outside the window |
| Keep primers off a SNP/repeat | `SEQUENCE_EXCLUDED_REGION` (no overlap) | excluding beats N-masking (N-masking still allows a primer with <= MAX_NS_ACCEPTED Ns) |
| Left primer from region A, right from region B | `SEQUENCE_PRIMER_PAIR_OK_REGION_LIST` quadruples | constrains the two primers independently, per pair |
| cDNA-specific (avoid unspliced gDNA) | `SEQUENCE_OVERLAP_JUNCTION_LIST` + `PRIMER_MIN_3_PRIME_OVERLAP_OF_JUNCTION` | a primer straddling the splice junction cannot prime contiguous gDNA |
| One Sanger sequencing primer | `PRIMER_PICK_LEFT_PRIMER=1`, `PRIMER_PICK_RIGHT_PRIMER=0` | single-primer mode; leave >=30-50 bp buffer to the feature |
| Cloning / adapters (restriction, Gibson, T7) | design the binding core in primer3, append the 5' tail afterward | a non-templated tail does not anneal in early cycles |
| Genotype a SNP by allele-specific PCR (ARMS) | discriminating base at the 3' terminus + a second -2/-3 mismatch; allele-specific primer + common reverse | the 3' anchor discriminates the allele, the second mismatch widens it |
| Choose the annealing temperature | Ta ~3-5 C below the lower primer Tm; gradient to optimize; touchdown for hard specificity | predicted Tm is not Ta; the reaction is non-equilibrium |
| Divergent / unknown-reference target (degenerate primers) | a consensus/degenerate designer, NOT primer3 | primer3 cannot model IUPAC degeneracy; design in conserved blocks, keep the 3' anchor non-degenerate |
| Amplicon over ~3-5 kb (long-range PCR) | longer high-Tm primers (24-30 nt), proofreading/long-range polymerase | the enzyme tolerates less mispriming over long extensions; raise OPT_TM/OPT_SIZE, tighten end-stability |
| Confirm the pair is unique genome-wide | -> primer-specificity | primer3 scores thermodynamics, not specificity |
| Check the chosen pair for dimers/hairpins | -> primer-validation | thermodynamic structure prediction of the oligos |

Default when uncertain: standard amplicon with `SEQUENCE_TARGET`, Tm 58-62 C, GC 40-60%, product 100-1000 bp, then route the top pairs to primer-specificity before ordering.

## Design a Tm-Matched Primer Pair

**Goal:** Get ranked primer pairs that amplify the target region within the desired size and Tm window, Tm-matched between the two primers.

**Approach:** Put per-template data (the sequence and any positional constraint) in `seq_args` under `SEQUENCE_*` keys; put run-wide settings (Tm/GC/size bounds, salt) in `global_args` under `PRIMER_*` keys; call `design_primers`; read the ranked pairs from the flat result dict. Supply the real reaction salt so the reported Tm is meaningful.

```python
import primer3

template = 'ATGC...'  # the only sequence primer3 sees

result = primer3.design_primers(
    seq_args={
        'SEQUENCE_ID': 'amp1',
        'SEQUENCE_TEMPLATE': template,
        'SEQUENCE_TARGET': [400, 60],          # [start, length], 0-based; both primers must flank this
    },
    global_args={
        'PRIMER_PICK_LEFT_PRIMER': 1,
        'PRIMER_PICK_RIGHT_PRIMER': 1,
        'PRIMER_NUM_RETURN': 5,
        'PRIMER_OPT_SIZE': 20, 'PRIMER_MIN_SIZE': 18, 'PRIMER_MAX_SIZE': 25,
        'PRIMER_OPT_TM': 60.0, 'PRIMER_MIN_TM': 58.0, 'PRIMER_MAX_TM': 62.0,
        'PRIMER_PAIR_MAX_DIFF_TM': 2.0,        # keep the pair within 2 C of each other
        'PRIMER_MIN_GC': 40.0, 'PRIMER_MAX_GC': 60.0,
        'PRIMER_PRODUCT_SIZE_RANGE': [[150, 400]],
        'PRIMER_SALT_MONOVALENT': 50.0,        # mM; match the reaction (drives Tm)
        'PRIMER_SALT_DIVALENT': 1.5,           # mM Mg2+
        'PRIMER_DNTP_CONC': 0.6,               # mM; subtracted from Mg2+ to get free Mg2+
        'PRIMER_DNA_CONC': 50.0,               # nM oligo
        'PRIMER_EXPLAIN_FLAG': 1,              # so a zero-pair run is diagnosable
    })

for i in range(result['PRIMER_PAIR_NUM_RETURNED']):
    print(result[f'PRIMER_LEFT_{i}_SEQUENCE'], result[f'PRIMER_RIGHT_{i}_SEQUENCE'],
          round(result[f'PRIMER_LEFT_{i}_TM'], 1), round(result[f'PRIMER_RIGHT_{i}_TM'], 1),
          result[f'PRIMER_PAIR_{i}_PRODUCT_SIZE'], round(result[f'PRIMER_PAIR_{i}_PENALTY'], 2))
```

## Positional Constraints: Get the Tag Semantics Right

These are the most error-prone keys; the distinctions are load-bearing. All coordinates are 0-based by default (`PRIMER_FIRST_BASE_INDEX`), and every interval is `[start, length]`, NOT `[start, end]`.

- `SEQUENCE_TARGET = [start, length]` -- a legal pair must FLANK the target (both primers outside, amplicon spans it). Use to force the amplicon to cover a feature.
- `SEQUENCE_INCLUDED_REGION = [start, length]` -- primers are CONFINED within it; no part of a primer may fall outside.
- `SEQUENCE_EXCLUDED_REGION = [[start, length], ...]` -- no primer may OVERLAP any listed interval (even by one base).
- `SEQUENCE_PRIMER_PAIR_OK_REGION_LIST = [[lstart, llen, rstart, rlen], ...]` -- per-pair windows for the left and right primer independently (-1 leaves a side free).
- `SEQUENCE_OVERLAP_JUNCTION_LIST = [pos, ...]` with `PRIMER_MIN_3_PRIME_OVERLAP_OF_JUNCTION` (default 4) and `PRIMER_MIN_5_PRIME_OVERLAP_OF_JUNCTION` (default 7) -- at least one primer must straddle a junction; the 3' overlap is the specificity-determining knob.
- `SEQUENCE_FORCE_LEFT_START/_RIGHT_START` (fix the 5' end) and `_LEFT_END/_RIGHT_END` (fix the 3' end) -- pin a primer to a known oligo while primer3 picks the partner.

## The 3' End Governs Priming -- and 5' Tails Do Not Anneal

Polymerase extends only from a base-paired 3'-OH, so the terminal ~5 nt are the priming anchor: a 3'-terminal mismatch suppresses extension by orders of magnitude (Kwok 1990 *Nucleic Acids Res* 18:999), which is why primer3 weights 3'-end (`_END`) complementarity far above internal (`_ANY`). A GC clamp (`PRIMER_GC_CLAMP`, default 0; set 1) stabilizes the anchor, but a too-stable 3' end is double-edged -- it also anchors at off-target sites, so cap it with `PRIMER_MAX_END_STABILITY` (a positive stability magnitude for the 3'-terminal pentamer in kcal/mol, NOT a signed dG; library default 100.0 = effectively off; lowering to ~9 as a heuristic forbids over-stable ends). For a primer carrying a non-templated 5' tail (restriction site, Gibson arm, T7 promoter, universal tail): design the template-binding CORE in primer3 so its Tm reflects only the annealing region, then prepend the tail in software; pasting the full tailed oligo into a Tm calculator overestimates the anneal Tm. The tail still exists physically, so check dimers/hairpins on the FULL tailed oligo (-> primer-validation).

## Predicted Tm Is Not the Annealing Temperature

The Tm primer3 reports is an equilibrium midpoint against a perfect complement at the supplied oligo/salt concentration; the annealing temperature (Ta) the thermocycler runs is a separate operating point in a non-equilibrium reaction. A workable default is Ta ~3-5 C below the LOWER of the two primers' predicted Tm, then optimize empirically: a gradient PCR brackets the Ta giving a single product, and Rychlik's optimum (Ta_opt = 0.3*Tm_primer + 0.7*Tm_product - 14.9; Rychlik 1990 *Nucleic Acids Res* 18:6409) accounts for the product. When specificity is hard (paralogs, high background), use touchdown PCR (Don 1991 *Nucleic Acids Res* 19:4008): start Ta several degrees ABOVE the expected Tm so only the perfect target nucleates, then step down each cycle -- the specific product established first outcompetes later mispriming.

## Allele-Specific (ARMS) Primers Exploit the 3' End Constructively

The same 3'-terminal sensitivity that causes allele dropout is the basis of allele-specific PCR: place the discriminating base at the primer's 3' TERMINUS so the off-allele mismatches the anchor and fails to extend, and add a second deliberate mismatch at the -2 or -3 position so the off-allele carries two destabilizing mismatches and the discrimination widens (Newton 1989 *Nucleic Acids Res* 17:2503). Design one allele-specific primer per allele sharing a common reverse primer, and confirm discrimination with no-template and opposite-allele controls. (This is the constructive inverse of the SNP-under-3'-end failure mode below.)

## Per-Method Failure Modes

### Top pair ordered without a specificity check
**Trigger:** Treating `PRIMER_PAIR_0` as final. **Mechanism:** primer3 never sees off-target loci; a thermodynamically perfect pair can prime paralogs, pseudogenes, or repeats. **Symptom:** multiple bands on a gel; off-target amplicon in sequencing. **Fix:** route every chosen pair through primer-specificity (Primer-BLAST / in-silico PCR) before ordering.

### Tm mismatch between forward and reverse
**Trigger:** Wide `PRIMER_MIN_TM`/`MAX_TM` with no pair-difference cap. **Mechanism:** the lower-Tm primer is under-annealed at the anneal step, so one strand dominates. **Symptom:** weak/biased amplification, smeary product. **Fix:** set `PRIMER_PAIR_MAX_DIFF_TM` ~2 C and/or raise `PRIMER_PAIR_WT_DIFF_TM`.

### Coordinate or tag confusion
**Trigger:** Passing `[start, end]` instead of `[start, length]`, assuming 1-based, or swapping TARGET (force-flank) / INCLUDED (confine) / EXCLUDED (no-overlap). **Mechanism:** every region shifts or the wrong constraint applies. **Symptom:** primers land in the wrong place, or zero pairs return. **Fix:** use `[start, length]`, keep `PRIMER_FIRST_BASE_INDEX` at 0, and match the tag to intent from the Decision Tree.

### SNP under the 3' end
**Trigger:** A common variant beneath a primer's last ~5 nt. **Mechanism:** the primer matches one allele and mismatches the other at the anchor (Kwok 1990 *Nucleic Acids Res* 18:999), so the alternate allele is under-amplified. **Symptom:** allele dropout / spurious homozygosity. **Fix:** pull common SNPs (dbSNP/gnomAD, MAF >= 1%) and add them to `SEQUENCE_EXCLUDED_REGION`.

### 5'-tail folded into the Tm
**Trigger:** Including a non-templated tail in the annealing-Tm calculation. **Mechanism:** the tail does not pair in early cycles but inflates the computed Tm. **Symptom:** annealing temperature set too high, early-cycle failure. **Fix:** design the core in primer3, append the tail after, re-check dimers on the full oligo.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| Primer length 18-25 nt (opt 20) | Rozen & Skaletsky 2000 *Methods Mol Biol* 132:365 | long enough for specificity, short enough to anneal fast; primer3 default OPT 20 |
| Tm 58-62 C, pair within <=2 C | Koressaar & Remm 2007 *Bioinformatics* 23:1289 | matched Tm so both primers anneal at one Ta; predicted Tm is salt/conc-dependent |
| GC 40-60% | Rozen & Skaletsky 2000 *Methods Mol Biol* 132:365 | default 20-80 is far too wide; extremes prime poorly |
| GC clamp 1 (max 2 in last 5) | community/vendor practice (3'-anchor stability per SantaLucia 1998 *PNAS* 95:1460) | a stable 3' anchor aids extension; >=3 G/C invites mispriming (a design heuristic, not from the NN paper) |
| `PRIMER_MAX_END_STABILITY` ~9 (heuristic) | community practice (param: Untergasser 2012 *Nucleic Acids Res* 40:e115) | positive stability magnitude (kcal/mol) of the 3'-pentamer; library default 100 is off; cap to curb mispriming |
| `PRIMER_MAX_POLY_X` 4 | Untergasser 2012 *Nucleic Acids Res* 40:e115 | homopolymer 3' ends slip-register on repetitive template |
| Product 100-1000 bp (standard PCR) | -- | routine amplicon band; set per assay (qPCR 70-150 -> qpcr-primers) |
| Free Mg2+ ~= total Mg - total dNTP | Owczarzy 2008 *Biochemistry* 47:5336 | only free Mg2+ stabilizes the duplex; the #1 predicted-vs-bench Tm gap |

## Diagnose a Zero-Pair Run

When `PRIMER_PAIR_NUM_RETURNED == 0` this is a constraint problem, not a bug. Set `PRIMER_EXPLAIN_FLAG = 1` and read `PRIMER_LEFT_EXPLAIN`, `PRIMER_RIGHT_EXPLAIN`, `PRIMER_PAIR_EXPLAIN` -- each tallies how many candidates failed for each reason ("considered 4500, GC content failed 1200, low tm 800, ... ok 0"). The dominant bucket names the single constraint to loosen. Loosen ONE constraint at a time and re-read; typical order of suspects: product-size range too narrow, Tm window too tight (or wrong salt/DNA-conc), GC window too tight, positional over-constraint, then complementarity ceilings.

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| `AttributeError: designPrimers` | camelCase deprecated since primer3-py 1.0.0 | use `primer3.design_primers` (snake_case) |
| Zero pairs returned | bounds too tight / region too short / N-masked template | `PRIMER_EXPLAIN_FLAG=1`, loosen one constraint at a time |
| Tm differs from another tool | different salt-correction model or concentrations | match `PRIMER_SALT_*`, `PRIMER_DNTP_CONC`, `PRIMER_DNA_CONC`; compare like for like |
| Primers amplify multiple bands | no genome specificity check | route the pair to primer-specificity (BLAST / in-silico PCR) |
| A `SEQUENCE_*`/`PRIMER_*` key is ignored | wrong dict (SEQUENCE in global_args or vice versa) | put `SEQUENCE_*` in seq_args, `PRIMER_*` in global_args |
| Allele dropout in some samples | SNP under a primer 3' end | exclude common variants from the primer-binding region |
| GC-rich/structured template will not amplify | high effective Tm and secondary structure | add DMSO/betaine/7-deaza-dGTP to lower effective Tm and disrupt structure -- a reagent lever orthogonal to redesign (primer3 does not model additives) |

## References

- Untergasser A, Cutcutache I, Koressaar T, et al. 2012. Primer3 - new capabilities and interfaces. *Nucleic Acids Res* 40:e115.
- Koressaar T, Remm M. 2007. Enhancements and modifications of primer design program Primer3. *Bioinformatics* 23:1289-1291.
- SantaLucia J Jr. 1998. A unified view of polymer, dumbbell, and oligonucleotide DNA nearest-neighbor thermodynamics. *PNAS* 95:1460-1465.
- Owczarzy R, Moreira BG, You Y, et al. 2008. Predicting stability of DNA duplexes in solutions containing magnesium and monovalent cations. *Biochemistry* 47:5336-5353.
- Kwok S, Kellogg DE, McKinney N, et al. 1990. Effects of primer-template mismatches on the polymerase chain reaction: human immunodeficiency virus type 1 model studies. *Nucleic Acids Res* 18:999-1005.
- Rychlik W, Spencer WJ, Rhoads RE. 1990. Optimization of the annealing temperature for DNA amplification in vitro. *Nucleic Acids Res* 18:6409-6412.
- Don RH, Cox PT, Wainwright BJ, et al. 1991. 'Touchdown' PCR to circumvent spurious priming during gene amplification. *Nucleic Acids Res* 19:4008.
- Newton CR, Graham A, Heptinstall LE, et al. 1989. Analysis of any point mutation in DNA. The amplification refractory mutation system (ARMS). *Nucleic Acids Res* 17:2503-2516.
- Rozen S, Skaletsky H. 2000. Primer3 on the WWW for general users and for biologist programmers. *Methods Mol Biol* 132:365-386.

## Related Skills

- primer-validation - Check chosen primers for dimers, hairpins, and 3'-end stability
- primer-specificity - Confirm the pair amplifies only the target genome-wide (in-silico PCR / Primer-BLAST)
- qpcr-primers - Design qPCR primers and hydrolysis/molecular-beacon probes
- database-access/entrez-fetch - Fetch the template sequence to design against
- sequence-manipulation/seq-objects - Reverse-complement and extract subsequences
- sequence-io/read-sequences - Read the target FASTA
<!-- END FILE: primer-design/primer-basics/SKILL.md -->

## 子目录：primer-design/primer-specificity

<!-- BEGIN FILE: primer-design/primer-specificity/SKILL.md -->
---
name: bio-primer-design-primer-specificity
description: Checks whether a PCR primer PAIR amplifies only the intended target genome-wide, using pair-aware in-silico PCR (MFEprimer-3.0, UCSC isPcr, NCBI Primer-BLAST) plus a primer3-py 3'-end-stability prefilter, against the correct database. Covers why plain BLAST is the wrong tool (it scores per-primer similarity, blind to 3'-terminal anchoring and to whether the two primers form a convergent amplicon in range), why a single 3'-terminal mismatch suppresses amplification while internal mismatches are tolerated, why intron-spanning RT-qPCR is defeated by processed pseudogenes that force a GENOME search not transcriptome-only, how to read a Primer-BLAST report (empty unintended-products means none passed its filter, not none exist), and that in-silico checking reduces but never replaces empirical validation. Use when confirming specificity, screening off-target amplicons, avoiding paralog/pseudogene hits, or checking SNPs under the 3' end. Design is primer-basics; dimers primer-validation; alignment read-alignment.
tool_type: mixed
primary_tool: mfeprimer
---

## Version Compatibility

Reference examples tested with: primer3-py 2.3+ (offline prefilter). In-silico PCR tools: MFEprimer 3.x, UCSC isPcr, BLAST+ 2.14+, NCBI Primer-BLAST (web).

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show primer3-py` then `help(primer3.calc_end_stability)` to check signatures
- CLI: `mfeprimer --help`, `isPcr`, `blastn -help` to confirm subcommands and flags

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Primer Specificity -- Does the PAIR Amplify Only the Target Genome-Wide

**"Are these primers specific?"** -> Predict every amplicon the primer PAIR would generate against the correct database and confirm only the intended one survives -- because specificity is a property of a convergent, 3'-anchored, in-range PAIR, not of one primer's similarity to the genome.
- CLI: `mfeprimer -i primers.fa -d genome.fa` (or UCSC `isPcr`, or NCBI Primer-BLAST) predicts amplicons from the pair.
- Python: `primer3.calc_end_stability(primer, site)` ranks 3'-end anchoring -- the variable BLAST ignores.

Scope: genome/transcriptome-wide off-target and mispriming assessment of a chosen primer PAIR via in-silico PCR. Designing primers -> primer-basics. Intramolecular dimers/hairpins of the oligos -> primer-validation. General read alignment / building a BLAST DB -> read-alignment/bwa-alignment, database-access/blast-searches.

## The Single Most Important Modern Insight -- Plain BLAST Is the Wrong Tool, Because Specificity Is a Property of a Predicted Amplicon, Not One Primer's Similarity

1. **The unit of analysis is the amplicon, not the primer.** Amplification needs four things at once: the forward primer anchored, the reverse primer anchored, the two convergent, and the gap within the polymerase's range. BLAST evaluates none of these as a set -- it scores per-query local similarity and stops. So a clean BLAST is false confidence in BOTH directions: a primer with a perfect 5' region but mismatched 3' bases scores a high BLAST hit yet will NOT prime (false off-target), while a primer with internal mismatches but a perfect 3' anchor WILL prime yet may fall below BLAST's word size and be missed (false negative).
2. **The 3' terminus is the governing variable, and BLAST is blind to it.** A single 3'-terminal mismatch suppresses extension by roughly 20-100x depending on identity (A:G/G:A/C:C worst, A:A intermediate, G:T/T:G wobble weakest and NOT automatically safe), while internal mismatches are tolerated (Kwok 1990 *Nucleic Acids Res* 18:999). BLAST maximizes total alignment score and cannot tell a 5' match from a 3' match. Pair-aware tools (Primer-BLAST, MFEprimer, isPcr) use BLAST or a k-mer index only as a candidate FINDER, then apply a pair + 3'-anchor + product-size FILTER.
3. **Search the correct database or the answer is meaningless.** For RT-qPCR, intron-spanning primers do NOT escape genomic DNA: processed pseudogenes are intronless retro-copies that typically carry the exon-exon junction (3'-truncated retrocopies may not), so when present they amplify like cDNA -- the search must cover the GENOME (with pseudogenes and alt/unplaced contigs), not the transcriptome only. This is the most common RT-qPCR specificity trap.

## Why Plain BLAST Fails, Concretely

BLASTn defaults are wrong for a ~20 nt primer: megablast (the default `blastn`) seeds at word 28 and so cannot seed a 20-mer at all; plain `blastn` (word 11) does seed a perfect 20-mer, but its scoring and E-value defaults are tuned for long queries, so short or partial off-target hits fall below threshold; only `blastn-short` (word 7, short-query scoring) is the appropriate task -- and even then it scores similarity, not amplification. And BLAST evaluates each primer independently against the database; it never asks whether the forward and reverse hits face each other within an amplifiable span. So `blastn-short` is acceptable only as a quick EXPLORATORY check for gross multi-copy/repeat problems of a single primer, read with the 3' alignment inspected by hand -- never as the final specificity decision.

## Tool Taxonomy

| Tool / method | Citation | Mechanism / role | When |
|---------------|----------|------------------|------|
| MFEprimer-3.0 | Wang 2019 *Nucleic Acids Res* 47:W610 | k-mer index forbids a mismatch at the first 3' base, then nearest-neighbor scores stable binding; outputs amplicons + Ta/dG + dimer/hairpin modules; CLI/JSON | scriptable local in-silico PCR with thermodynamics; the default programmatic checker |
| NCBI Primer-BLAST | Ye 2012 *BMC Bioinformatics* 13:134 | BLAST candidate-find + convergent-pair + 3'-mismatch filter; "intended vs unintended products" report; any NCBI organism | tunable-mismatch, report-driven web check |
| UCSC In-Silico PCR (isPcr) | Kent (UCSC Genome Browser) | exact predicted product(s) of a pair on a chosen assembly, with coordinates | confirm the intended amplicon exists and is unique on a specific UCSC assembly; local batch |
| `blastn -task blastn-short` | Altschul 1990 *J Mol Biol* 215:403 | similarity seed at word_size 7 | EXPLORATORY single-primer repeat/multi-copy scan only |
| `primer3.calc_end_stability` | SantaLucia & Hicks 2004 *Annu Rev Biophys* 33:415 | dG of a primer's 3' end annealing to a site | rank candidate off-target sites by 3'-anchor strength (the BLAST-blind variable) |

## Decision Tree by Scenario

| Scenario | Recommended | Why |
|----------|-------------|-----|
| Any qPCR / quantitative assay | MFEprimer or Primer-BLAST against genome + transcriptome | off-targets and gDNA corrupt the quantitative number |
| Intron-spanning RT-qPCR | search the GENOME (pseudogenes), not transcriptome-only | processed pseudogenes usually carry the junction and amplify from gDNA |
| Genotyping / allele-specific | weight the 3' end; check SNPs under the anchor (dbSNP/gnomAD) | the 3'-terminal base is the whole assay (Kwok 1990) |
| Confirm intended amplicon on a UCSC assembly | UCSC isPcr | exact product + genomic coordinates on that assembly |
| Tunable mismatch sensitivity + report | Primer-BLAST (loosen/tighten the 3'-mismatch filter) | stress-test how robust specificity is |
| Quick single-primer repeat scan | `blastn-short` word_size 7, dust off | gross multi-copy triage only; never final |
| Multiplex (N primers) | run in-silico PCR over the POOLED primer set + all-pairs cross-dimer | the pooled set enumerates cross-pair amplicons (Fwd_A + Rev_B, convergent and in-range), which per-pair checks miss; Primer-BLAST does NOT check inter-pair dimers either (O(N^2)) |
| Eukaryotic target with gene families / segmental duplications | pair-level genome + transcriptome search | paralogs in conserved exons amplify multiple members; segmental duplications / recent CNV families (e.g. SMN1/SMN2) give two near-identical loci a pair cannot distinguish |

Default when uncertain: run pair-aware in-silico PCR (MFEprimer or Primer-BLAST) against the genome AND, for RT work, the transcriptome; require exactly one intended amplicon, no qualifying off-target, and 3' ends clear of common SNPs -- then still validate empirically.

## Run In-Silico PCR on the Pair

**Goal:** Enumerate every amplicon the pair would make against the correct database and confirm only the intended one survives.

**Approach:** Build the database index once, run the pair-aware tool, and read the predicted products; require a single on-target amplicon of expected size and no qualifying off-target. The commands below need the tool binaries and a genome/transcriptome FASTA, so they are NOT offline-spot-runnable here -- verify flags with `--help` against the installed version.

```bash
# MFEprimer-3.0 (local, thermodynamic; build the k-mer index once, then run)
mfeprimer index -i genome.fa
mfeprimer -i primers.fa -d genome.fa -o specificity.txt        # add --json for pipeline parsing; verify flags with: mfeprimer --help

# UCSC isPcr (exact products on one assembly; primers.txt = "name<TAB>FWD<TAB>REV" per line)
isPcr genome.2bit primers.txt stdout -out=fa

# blastn-short: EXPLORATORY single-primer repeat scan ONLY (not a specificity verdict)
blastn -task blastn-short -word_size 7 -dust no -query primers.fa -db genome -outfmt 6
```

NCBI Primer-BLAST (web, any organism): paste the pair, pick the organism and a database that includes the genome (not "RefSeq mRNA only" for RT-qPCR), set the max product size, and read the report.

## Rank Off-Target Sites by 3'-End Anchoring (offline)

**Goal:** Show why a candidate off-target site that BLAST would surface may or may not actually prime, using the 3'-anchor thermodynamics BLAST ignores.

**Approach:** For each candidate site (the complementary strand the primer would anneal to), contrast the overall duplex dG (`calc_heterodimer`, what a similarity search tracks) with the 3'-anchor dG (`calc_end_stability`); a 3'-terminal mismatch keeps the overall dG strong but collapses the anchor, so the site will not prime despite the similarity.

```python
import primer3

COMP = str.maketrans('ACGT', 'TGCA')
primer = 'GTCTCCTCTGACTTCAACAGCG'
site = primer.translate(COMP)[::-1]                  # the strand the primer anneals to; primer 3' base pairs site[0]

def mut(s, i):
    return s[:i] + ('A' if s[i] != 'A' else 'C') + s[i + 1:]

sites = {'on-target': site, 'internal mismatch': mut(site, len(site) // 2), '3-prime mismatch': mut(site, 0)}

for label, s in sites.items():
    overall = primer3.calc_heterodimer(primer, s).dg / 1000   # what overall similarity tracks
    anchor = primer3.calc_end_stability(primer, s).dg / 1000  # the 3'-anchor BLAST ignores
    print(f'{label}: overall dG={overall:.2f}  3-prime anchor dG={anchor:.2f} kcal/mol')   # 3' mismatch: overall stays strong, anchor collapses
```

## Per-Method Failure Modes

### "BLAST was clean, so it is specific"
**Trigger:** Treating a per-primer BLAST result as a specificity verdict. **Mechanism:** BLAST scores similarity per primer, ignores 3'-anchoring and pairing. **Symptom:** primers pass BLAST but amplify off-target on the bench. **Fix:** use pair-aware in-silico PCR (MFEprimer / Primer-BLAST / isPcr).

### Intron-spanning RT-qPCR checked against the transcriptome only
**Trigger:** Searching "RefSeq mRNA" and concluding gDNA-safe. **Mechanism:** processed pseudogenes are intronless and carry the junction, amplifying like cDNA. **Symptom:** a genomic amplicon at the cDNA size; no-RT control is positive. **Fix:** search the genome (with pseudogenes); keep DNase + no-RT control.

### Misreading an empty Primer-BLAST "unintended" section
**Trigger:** Treating an empty section as proof of uniqueness. **Mechanism:** Primer-BLAST ignores any off-target with >=6 total mismatches OR >=2 mismatches in the last 5 bp at the 3' end -- equivalently it LISTS only hits with <6 total and <2 near the 3', so an empty section means "none my model predicts will amplify," not "none similar exist." **Symptom:** false confidence. **Fix:** loosen the mismatch settings to stress-test, and combine with isPcr.

### Wrong / too-narrow database
**Trigger:** Searching primary assembly only, or one chromosome, or a single transcript set. **Mechanism:** off-targets on alt/unplaced contigs, repeats, or paralog transcripts are excluded. **Symptom:** "unique" in-silico, multiple bands in vitro. **Fix:** match the database to the assay (genome + transcriptome for RT-qPCR; include alt/unplaced contigs).

### SNP/indel under the 3' end
**Trigger:** Validating against the reference only. **Mechanism:** an individual carrying a variant under the 3' anchor fails to amplify that allele (Kwok 1990 *Nucleic Acids Res* 18:999). **Symptom:** allele dropout in some samples. **Fix:** check primer 3' ends against dbSNP/gnomAD common variants and redesign (primer-basics).

### Checking a multiplex pair-by-pair instead of pooled
**Trigger:** Per-pair Primer-BLAST/in-silico PCR on a multiplex set. **Mechanism:** two off-target classes only appear in the POOLED set -- inter-pair cross-dimers (O(N^2), unexamined) and cross-pair amplicons where one pair's forward meets another pair's reverse convergently and in-range. **Symptom:** one channel silently fails or an unexpected band appears. **Fix:** run in-silico PCR over the pooled primer set AND all-pairs cross-dimer screening (primer-validation), not pair-by-pair.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| Primer-BLAST ignores off-target if >=6 total mismatches OR >=2 in last 5 bp at 3' | Ye 2012 *BMC Bioinformatics* 13:134 | encodes the 3'-anchor biology BLAST lacks (its actual default filter) |
| 3'-terminal mismatch suppresses ~20-100x (A:G/G:A/C:C worst, G:T/T:G weakest) | Kwok 1990 *Nucleic Acids Res* 18:999 | why a 3' anchor decides priming; wobble is not automatically safe |
| `blastn-short` word_size 7, dust off | Altschul 1990 *J Mol Biol* 215:403 | short-query-tuned scoring/E-value; megablast (word 28) cannot seed a 20-mer, default blastn (word 11) seeds it but its long-query scoring drops marginal hits |
| Require exactly 1 intended amplicon, expected size | -- | the in-silico pass condition before empirical validation |
| RT-qPCR: search genome + transcriptome | Ye 2012 *BMC Bioinformatics* 13:134 | genome catches pseudogenes/gDNA; transcriptome catches isoforms/paralogs |

## In-Silico Reduces, It Does Not Replace, Empirical Validation

A passing in-silico check removes most bad designs but does not license an assay. Confirm empirically: a gradient PCR to find the annealing temperature giving a single product; a single band on a gel (or single fragment on a TapeStation); for SYBR qPCR a single sharp melt peak with no low-Tm dimer shoulder; and Sanger sequencing of the product to prove identity (a same-size off-target is invisible on a gel). State this honestly -- "Primer-BLAST said it is specific" is not validation of a quantitative assay.

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| Primers pass BLAST, fail in vitro | per-primer similarity, not pair amplicon | run pair-aware in-silico PCR |
| RT-qPCR amplifies gDNA despite intron-spanning | processed pseudogene usually carries the junction | search the genome; DNase + no-RT control |
| Empty Primer-BLAST off-targets but multiple bands | filter hid a 3'-anchored off-target / wrong DB | loosen mismatch settings; search the genome incl. alts |
| isPcr returns nothing for the intended pair | wrong assembly / over-strict default match | confirm the assembly and target presence |
| `mfeprimer` errors on the database | index not built | run `mfeprimer index -i db.fa` first |
| Allele dropout in some individuals | SNP under the 3' end | check 3' ends vs gnomAD; redesign (primer-basics) |

## References

- Ye J, Coulouris G, Zaretskaya I, et al. 2012. Primer-BLAST: a tool to design target-specific primers for polymerase chain reaction. *BMC Bioinformatics* 13:134.
- Wang K, Li H, Xu Y, et al. 2019. MFEprimer-3.0: quality control for PCR primers. *Nucleic Acids Res* 47:W610-W613.
- Kwok S, Kellogg DE, McKinney N, et al. 1990. Effects of primer-template mismatches on the polymerase chain reaction: human immunodeficiency virus type 1 model studies. *Nucleic Acids Res* 18:999-1005.
- SantaLucia J Jr, Hicks D. 2004. The thermodynamics of DNA structural motifs. *Annu Rev Biophys Biomol Struct* 33:415-440.
- Altschul SF, Gish W, Miller W, et al. 1990. Basic local alignment search tool. *J Mol Biol* 215:403-410.

## Related Skills

- primer-basics - Design (or redesign) primers when specificity fails
- primer-validation - Intramolecular dimers/hairpins of the chosen oligos
- qpcr-primers - qPCR assays where specificity and gDNA exclusion are mandatory
- read-alignment/bwa-alignment - Align candidate amplicons / reads to a genome
- database-access/blast-searches - Build/query BLAST databases for candidate finding
<!-- END FILE: primer-design/primer-specificity/SKILL.md -->

## 子目录：primer-design/primer-validation

<!-- BEGIN FILE: primer-design/primer-validation/SKILL.md -->
---
name: bio-primer-design-primer-validation
description: Validates chosen PCR/qPCR oligos for intramolecular thermodynamic liabilities with primer3-py - hairpins, self-dimers, cross-dimers (calc_hairpin/homodimer/heterodimer), and 3'-end stability (calc_end_stability) - returning ThermoResult dG/Tm and ASCII structures. Covers why a "dimer-free" verdict is a PREDICTION at the supplied salt/Mg/dNTP/oligo conditions and temp_c (so the same primer is fine or dimer-prone depending on conditions), why a 3'-END dimer or hairpin is the lethal class (polymerase-extendable into primer-dimer) so structures are ranked by dG at the annealing temperature and 3'-end involvement rather than global Tm, that ThermoResult dG is in cal/mol not kcal/mol, and that .structure_found must gate the numbers. Use when checking primer pairs before ordering, troubleshooting primer-dimers or smears, or screening oligos for secondary structure. Genome off-target/mispriming is primer-specificity; design is primer-basics; probe assays are qpcr-primers.
tool_type: python
primary_tool: primer3-py
---

## Version Compatibility

Reference examples tested with: primer3-py 2.3+.

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show primer3-py` then `help(primer3.calc_heterodimer)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# Primer Validation -- Thermodynamic Self-Structure of the Chosen Oligos

**"Are these primers free of dimers and hairpins?"** -> Predict the most stable intramolecular and inter-primer structures and judge them at the reaction conditions -- because a structure's harm is set by its dG at the annealing temperature and by whether it ties up the 3' end, not by a single global score.
- Python: `primer3.calc_hairpin(seq)`, `calc_homodimer(seq)`, `calc_heterodimer(seq1, seq2)`, `calc_end_stability(seq1, seq2)` return a `ThermoResult` with `.tm`, `.dg`, `.structure_found`.

Scope: thermodynamic validation of the OLIGOS themselves (hairpin, homodimer, heterodimer, 3'-end stability, pair Tm match) under stated conditions. Genome-wide off-target / mispriming / in-silico PCR -> primer-specificity. Designing primers -> primer-basics. qPCR primer+probe co-design -> qpcr-primers.

## The Single Most Important Modern Insight -- A "Dimer-Free" Verdict Is a Prediction at the Conditions Supplied, and the 3' End Is What Kills the Reaction

1. **These are predictions, not facts.** `calc_hairpin`/`calc_homodimer`/`calc_heterodimer` compute a dG/Tm under a specific monovalent/divalent/dNTP/oligo concentration and an evaluation temperature (`temp_c`). The same primer can read "fine" at default 37 C / default salt and "dimer-prone" at the real annealing temperature and Mg2+. Validate at the conditions and `temp_c` of the actual reaction, or the verdict is decorative.
2. **The 3' end is the lethal locus.** A dimer or hairpin that pairs the primer's 3' end is polymerase-EXTENDABLE: it gets turned into primer-dimer that amplifies exponentially, consumes reagents, and (in SYBR qPCR) generates competing signal. A structure with a more negative GLOBAL dG but a free 3' end is far less harmful. So do NOT rank by global dG or global Tm -- inspect 3'-end involvement (`calc_end_stability` and the ASCII structure) and judge at the annealing temperature.
3. **Read the units and the gate.** `ThermoResult.dg`, `.dh` are in cal/mol (and `.ds` in cal/(K.mol)) -- a value of -6000 is -6 kcal/mol, so divide by 1000 before comparing to kcal/mol heuristics. Always check `.structure_found` first: if no structure formed, the `.tm`/`.dg` are not a real duplex.

## The Three Structures, and Why They Differ

- **Hairpin** (intramolecular): the primer folds on itself; harmful mainly when it sequesters the 3' end or raises effective Tm enough to block template annealing.
- **Homodimer** (self-dimer): two copies of one primer pair; common with self-complementary or palindromic primers.
- **Heterodimer** (cross-dimer): the forward and reverse primers pair with each other. A primer can be individually clean and still cross-dimer with its partner, so the pair must be checked explicitly -- this is the dimer most often missed.

## Tool Taxonomy

| Function | Citation | Mechanism / role | When |
|----------|----------|------------------|------|
| `calc_hairpin(seq)` | Untergasser 2012 *Nucleic Acids Res* 40:e115 | most stable self-fold via thermodynamic alignment (ntthal) | screen a single primer/probe for hairpins |
| `calc_homodimer(seq)` | Untergasser 2012 *Nucleic Acids Res* 40:e115 | most stable self-self duplex | self-dimer of one oligo |
| `calc_heterodimer(s1, s2)` | Untergasser 2012 *Nucleic Acids Res* 40:e115 | most stable cross duplex of two oligos | forward-vs-reverse (and probe) cross-dimer |
| `calc_end_stability(s1, s2)` | SantaLucia & Hicks 2004 *Annu Rev Biophys* 33:415 | dG of the 3' end of s1 annealing to s2 | the 3'-anchored, extendable-dimer question |
| `calc_*_tm` (float) | Untergasser 2012 *Nucleic Acids Res* 40:e115 | the `.tm` only, no structure object | fast high-throughput screening |
| `calc_tm(seq)` | SantaLucia 1998 *PNAS* 95:1460 | nearest-neighbor Tm vs perfect complement | the pair Tm-match check |

## Decision Tree by Scenario

| Scenario | Recommended | Why |
|----------|-------------|-----|
| Standard pre-order check of a pair | `calc_hairpin`/`homodimer` on each + `calc_heterodimer` on the pair, at reaction conditions and `temp_c` = Ta | the four-call panel that catches self-structure |
| Suspect a primer-dimer artifact (gel, low-Tm melt peak) | `calc_heterodimer` + `calc_end_stability`, read the ASCII structure for 3'-end pairing | 3'-end dimers are extendable; that is the artifact source. A dimer that appears only at LOW template is diagnostic -- with scarce target, primer-primer collisions win the kinetic competition |
| Screening hundreds of oligos | `calc_hairpin_tm`/`calc_homodimer_tm` (floats) | fast triage; promote flagged ones to full `ThermoResult` |
| One primer designed with a 5' tail | run the calls on the FULL tailed oligo | the tail exists physically (palindromic sites/Gibson arms dimerize) |
| Pair anneals unevenly / one strand dominates | compare `calc_tm` of the two primers | a Tm mismatch >2-3 C, not a dimer, is the cause |
| "Will it amplify only the target?" | -> primer-specificity | that is genome off-target, a different question and toolset |

Default when uncertain: run the four-call panel at the real salt/Mg/dNTP/oligo concentrations with `temp_c` set to the annealing temperature, flag any structure whose dG is strongly negative at Ta, and weight 3'-end involvement most.

## Validate a Primer Pair at Reaction Conditions

**Goal:** Decide whether a chosen forward/reverse pair will misbehave through hairpins or dimers in the actual reaction, with the 3' end weighted appropriately.

**Approach:** Run hairpin and homodimer on each primer and heterodimer on the pair, all at the reaction's salt/Mg/dNTP/oligo concentrations and with `temp_c` set to the annealing temperature; gate every result on `.structure_found`; additionally compute `calc_end_stability` on the heterodimer to expose 3'-anchored (extendable) dimers; compare the two primer Tms for a match.

```python
import primer3

fwd, rev = 'GTCTCCTCTGACTTCAACAGCG', 'ACCACCCTGTTGCTGTAGCCAA'
COND = dict(mv_conc=50.0, dv_conc=3.0, dntp_conc=0.8, dna_conc=250.0, temp_c=60.0)  # match the qPCR/PCR reaction + Ta

def flag(label, res):
    if res.structure_found:
        print(f'{label}: Tm={res.tm:.1f}C dG={res.dg/1000:.2f} kcal/mol')   # dg is cal/mol -> /1000
    else:
        print(f'{label}: no structure')

for name, seq in [('fwd', fwd), ('rev', rev)]:
    flag(f'{name} hairpin', primer3.calc_hairpin(seq, **COND))
    flag(f'{name} homodimer', primer3.calc_homodimer(seq, **COND))

flag('heterodimer', primer3.calc_heterodimer(fwd, rev, **COND))
end = primer3.calc_end_stability(fwd, rev, **COND)            # 3'-end-anchored stability = the extendable-dimer risk
print(f"3'-end stability dG={end.dg/1000:.2f} kcal/mol")

dtm = abs(primer3.calc_tm(fwd, **{k: COND[k] for k in ('mv_conc','dv_conc','dntp_conc','dna_conc')})
          - primer3.calc_tm(rev, **{k: COND[k] for k in ('mv_conc','dv_conc','dntp_conc','dna_conc')}))
print(f'pair Tm difference={dtm:.1f}C')
```

## Reading the Result: dG, the 3' End, and the Structure

`ThermoResult.dg` is in cal/mol (divide by 1000 for kcal/mol). More negative = more stable = more concerning. But two structures with similar Tm can have very different dG at the annealing temperature, and the structure's own Tm is just where its dG crosses zero -- so judge by dG at `temp_c` = Ta, not by Tm. Print `res.ascii_structure` (or `res.ascii_structure_lines`) to SEE where the duplex sits: a dimer that pairs the recessed 3' ends is extendable and disqualifying even at modest dG, while a stronger structure with free 5'/internal pairing only transiently lowers free primer. `calc_end_stability(fwd, rev)` isolates exactly the 3'-end-of-fwd-against-rev stability, which is the right number for "will this dimer extend." It scores the 3' end of the FIRST argument, so check both directions (also `calc_end_stability(rev, fwd)`) -- either primer's 3' end can anchor the extendable dimer.

## Per-Method Failure Modes

### Ranking dimers by global dG or Tm
**Trigger:** Accepting/rejecting a structure on its overall dG or Tm. **Mechanism:** a weak dimer that locks the 3' ends is extended into artifact, while a strong dimer with free 3' ends is benign. **Symptom:** a "passing" pair still produces primer-dimer; a "failing" pair amplifies fine. **Fix:** inspect 3'-end involvement (`calc_end_stability`, ASCII structure) and weight it above whole-molecule dG.

### Validating at the wrong temperature/conditions
**Trigger:** Using default `temp_c=37` and default salt instead of the reaction's Ta and Mg2+. **Mechanism:** structure stability is strongly condition-dependent; a structure that melts below Ta is harmless. **Symptom:** false alarms (or false passes) that do not match the bench. **Fix:** set `temp_c` to the annealing temperature and pass the real mv/dv/dntp/dna concentrations.

### Trusting dG without a structure
**Trigger:** Reading `.dg`/`.tm` without checking `.structure_found`. **Mechanism:** when no structure forms the fields are not a real duplex. **Symptom:** nonsense or contradictory numbers. **Fix:** gate every result on `.structure_found` before reporting.

### Unit confusion (cal vs kcal)
**Trigger:** Comparing `.dg` directly to a kcal/mol threshold. **Mechanism:** primer3-py reports dG in cal/mol, so -6000 is -6 kcal/mol. **Symptom:** thresholds off by 1000x; everything looks catastrophic or fine. **Fix:** divide `.dg` by 1000 before comparing.

### Validating only the binding core of a tailed primer
**Trigger:** Checking the template-binding portion of a primer that carries a 5' tail. **Mechanism:** the full oligo (tail included) is what physically exists; palindromic restriction sites and complementary Gibson arms dimerize. **Symptom:** clean validation, dimers on the bench. **Fix:** run the calls on the FULL tailed oligo.

## Quantitative Thresholds

These are FLAGGING heuristics for inspection, not hard cutoffs; they are condition-dependent (salt, Mg2+, primer concentration, Ta). Read the structure and judge at Ta before accepting or rejecting.

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| Hairpin Tm at least ~10 C below Ta | SantaLucia & Hicks 2004 *Annu Rev Biophys* 33:415 | a hairpin that melts well below the anneal step is largely denatured |
| Dimer dG flag if more negative than ~ -6 to -9 kcal/mol | -- | common practice line; below ~ -9 generally rejected; condition-dependent |
| 3'-END dimer dG: be stricter, flag ~ -3 to -5 kcal/mol | Kwok 1990 *Nucleic Acids Res* 18:999 | 3'-anchored dimers are extendable, so weight them above global dG |
| Pair Tm difference <= 2 C | Koressaar & Remm 2007 *Bioinformatics* 23:1289 | matched Tm so both primers anneal at one Ta |
| Evaluate at `temp_c` = annealing temperature | SantaLucia & Hicks 2004 *Annu Rev Biophys* 33:415 | dG at Ta, not at 37 C, is the harm-relevant quantity |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| `AttributeError: calcHeterodimer` | camelCase deprecated since primer3-py 1.0.0 | use snake_case `calc_heterodimer` |
| Validation disagrees with the bench | default `temp_c`/salt, not the real reaction | pass reaction mv/dv/dntp/dna and `temp_c` = Ta |
| A "clean" pair still makes primer-dimer | judged by global dG, missed the 3' end | check `calc_end_stability` and the ASCII structure |
| dG threshold seems 1000x off | `.dg` is cal/mol, not kcal/mol | divide by 1000 before comparing |
| `.tm`/`.dg` look meaningless | no structure formed | gate on `.structure_found` |
| Pair amplifies one strand only | Tm mismatch, not a dimer | compare `calc_tm` of the two primers; redesign Tm-matched (primer-basics) |

## References

- Untergasser A, Cutcutache I, Koressaar T, et al. 2012. Primer3 - new capabilities and interfaces. *Nucleic Acids Res* 40:e115.
- SantaLucia J Jr, Hicks D. 2004. The thermodynamics of DNA structural motifs. *Annu Rev Biophys Biomol Struct* 33:415-440.
- SantaLucia J Jr. 1998. A unified view of polymer, dumbbell, and oligonucleotide DNA nearest-neighbor thermodynamics. *PNAS* 95:1460-1465.
- Koressaar T, Remm M. 2007. Enhancements and modifications of primer design program Primer3. *Bioinformatics* 23:1289-1291.
- Kwok S, Kellogg DE, McKinney N, et al. 1990. Effects of primer-template mismatches on the polymerase chain reaction: human immunodeficiency virus type 1 model studies. *Nucleic Acids Res* 18:999-1005.

## Related Skills

- primer-basics - Design Tm-matched primer pairs (redesign if validation fails)
- primer-specificity - Genome-wide off-target / in-silico PCR (a different question)
- qpcr-primers - Co-design qPCR primers and probes, including probe self-structure
- sequence-manipulation/seq-objects - Reverse-complement and assemble tailed oligos to validate
<!-- END FILE: primer-design/primer-validation/SKILL.md -->

## 子目录：primer-design/qpcr-primers

<!-- BEGIN FILE: primer-design/qpcr-primers/SKILL.md -->
---
name: bio-primer-design-qpcr-primers
description: Co-designs qPCR/RT-qPCR primers and hydrolysis (TaqMan) or molecular-beacon probes with primer3-py (PRIMER_PICK_INTERNAL_OLIGO, PRIMER_INTERNAL_* tags), for assays whose deliverable is a quantitative measurement device. Covers why amplification efficiency (90-110%, slope -3.6 to -3.1) and single-product specificity make the 2^-ddCq / Pfaffl math valid, why the short amplicon (70-150 bp), tight Tm, and zero-dimer requirement exist, the coupled probe rules (probe Tm 8-10 C above primers so it is bound when Taq's exonuclease cleaves it; no 5' G as it quenches the reporter; C-rich strand; primer3 has NO no-5'-G tag so enforce PRIMER_INTERNAL_MUST_MATCH_FIVE_PRIME=HNNNN), gDNA exclusion by exon-junction spanning AND why pseudogenes defeat it, SYBR melt-curve QC, and reference-gene validation (geNorm/NormFinder). Use when designing TaqMan/SYBR assays, exon-spanning primers, probes, or matched-efficiency multiplex panels. Genome specificity is primer-specificity; dimers primer-validation; standard PCR primer-basics.
tool_type: python
primary_tool: primer3-py
---

## Version Compatibility

Reference examples tested with: primer3-py 2.3+.

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show primer3-py` then `help(primer3.design_primers)` to check signatures

If code throws ImportError, AttributeError, or TypeError, introspect the installed
package and adapt the example to match the actual API rather than retrying.

# qPCR Primer and Probe Design -- Building a Quantitative Measurement Device

**"Design qPCR primers (and a probe) for this target"** -> Co-design a short, single-product, Tm-matched amplicon with an optional internal probe whose constraints are coupled to the primers -- because the assay's job is not to amplify but to MEASURE, and every qPCR-specific rule protects the efficiency the quantification math assumes.
- Python: `primer3.design_primers(seq_args, global_args)` with `PRIMER_PICK_INTERNAL_OLIGO=1` and `PRIMER_INTERNAL_*` for the probe.

Scope: co-designing qPCR/RT-qPCR primers and hydrolysis/beacon probes under coupled Tm/size/junction constraints. Genome-wide specificity / pseudogene checking -> primer-specificity. Intramolecular dimers/hairpins of the oligos and probe -> primer-validation. Standard (non-quantitative) PCR -> primer-basics.

## The Single Most Important Modern Insight -- A qPCR Assay Is a Measurement Device, and Efficiency Is a Parameter in the Equation, Not a QC Afterthought

1. **Validity rests on efficiency and specificity.** A Cq difference maps to a true fold-change only through `(1+E)^-dCq` (at ideal E=1, `2^-ddCq`). That requires amplification efficiency E ~ 90-110% (standard-curve slope -3.6 to -3.1, R^2 > 0.99) AND a single product. The short amplicon (70-150 bp), tight Tm, and zero-dimer requirement all exist to protect E and specificity. `2^-ddCq` is valid ONLY when the target and reference-gene efficiencies are matched and near 100% -- so design for matched ~100% E, or fall back to Pfaffl's efficiency-corrected model.
2. **The probe is coupled to the primers, not bolted on.** A hydrolysis probe must be BOUND when the polymerase extends through it (so Taq's 5'->3' exonuclease cleaves it and frees the reporter), which is why its Tm must sit 8-10 C ABOVE the primer Tm. It must NOT start with G (a 5'-G quenches the reporter even after cleavage), and the C-rich strand is preferred because G-richness anywhere near the reporter also quenches it. primer3's internal-oligo Tm defaults EQUAL the primer defaults, so they must be raised, and there is no dedicated no-5'-G tag -- enforce it with `PRIMER_INTERNAL_MUST_MATCH_FIVE_PRIME='HNNNN'` (IUPAC H = not G) or a post-hoc filter. This is the hydrolysis (TaqMan) probe path; a molecular beacon needs engineered complementary stem arms (a deliberate hairpin) that primer3's internal-oligo picker does NOT design and would flag as a liability -- design the linear core here, add the stem afterward, and exclude that hairpin from validation.
3. **Design-level gDNA exclusion is real but leaky.** Exon-junction-spanning or intron-flanking primers reduce genomic-DNA amplification, but processed pseudogenes (intronless retro-copies that usually carry the junction) defeat junction-spanning, and tiny introns defeat flanking. So DNase + a no-RT control + a genome specificity check (-> primer-specificity) remain mandatory; single-exon genes have no design-level option at all.

## The Quantification Math (Why the Constraints Exist)

Efficiency from a standard curve: `E = 10^(-1/slope) - 1`; perfect doubling is slope -3.32 (E = 100%). Relative quantification with matched ~100% efficiency uses `2^-ddCq` (Livak & Schmittgen 2001 *Methods* 25:402); with UNEQUAL efficiencies use the efficiency-corrected ratio `E_target^dCq / E_ref^dCq` (Pfaffl 2001 *Nucleic Acids Res* 29:e45). Report per MIQE (Bustin 2009 *Clin Chem* 55:611): efficiency, slope, R^2, Cq method, NTC and no-RT controls, and validated reference genes. The design objective is therefore "single short amplicon with slope near -3.32," not "two oligos that amplify."

## Tool Taxonomy

| Tool / method | Citation | Mechanism / role | When |
|---------------|----------|------------------|------|
| primer3-py internal oligo | Untergasser 2012 *Nucleic Acids Res* 40:e115 | `PRIMER_PICK_INTERNAL_OLIGO=1` + `PRIMER_INTERNAL_*` co-designs the probe with the primers | TaqMan / hydrolysis-probe assays |
| `PRIMER_INTERNAL_MUST_MATCH_FIVE_PRIME` | Untergasser 2012 *Nucleic Acids Res* 40:e115 | constrains the probe 5' end (use `HNNNN` to forbid 5'-G) | enforce the no-5'-G probe rule |
| `SEQUENCE_OVERLAP_JUNCTION_LIST` | Untergasser 2012 *Nucleic Acids Res* 40:e115 | forces a primer/probe to straddle a splice junction | cDNA-specific expression assays |
| MIQE reporting | Bustin 2009 *Clin Chem* 55:611 | the minimum information / efficiency-from-standard-curve standard | every quantitative assay |
| geNorm / NormFinder | Vandesompele 2002 *Genome Biol* 3:RESEARCH0034; Andersen 2004 *Cancer Res* 64:5245 | rank reference-gene stability | choosing normalizers, validated per condition |
| In-silico PCR (genome) | (route OUT) | catches pseudogenes / gDNA off-targets | mandatory gDNA/specificity check -> primer-specificity |

## Decision Tree by Scenario

| Scenario | Recommended | Why |
|----------|-------------|-----|
| Probe-based (multiplex-capable, second specificity check) | TaqMan: `PRIMER_PICK_INTERNAL_OLIGO=1`, probe Tm 8-10 C above primers, `HNNNN` 5' | the probe adds sequence specificity and enables multiplex |
| Single target, cheapest, no probe | SYBR (no internal oligo) + mandatory melt-curve QC | dye reports any dsDNA; melt curve is the specificity readout |
| Expression assay, avoid gDNA | exon-junction-spanning primers (`SEQUENCE_OVERLAP_JUNCTION_LIST`) | the junction does not exist contiguously in unspliced gDNA |
| Gene has a processed pseudogene | junction-spanning is NOT enough -> primer-specificity (search genome) + no-RT control | the pseudogene carries the junction |
| Single-exon gene (no junction) | DNase + no-RT control; no design-level gDNA exclusion | there is no intron/junction to exploit |
| AT-rich target / allele discrimination | MGB or LNA probe (shorter, higher effective Tm) | raises probe Tm where a standard probe cannot reach |
| Multiplex panel | spectrally distinct fluorophores, matched E, primer-limiting, all-pairs cross-dimer | competition and cross-dimers dominate; primer-limiting = drop the abundant target's primer concentration so it plateaus early and stops starving the rare target of shared reagents |
| Choosing normalizers | rank a candidate panel with geNorm/NormFinder, validate per condition | a single unvalidated reference gene is a classic error |

Default when uncertain: TaqMan primers+probe, amplicon 70-150 bp, primers Tm ~60 C (within 2 C), probe Tm ~68-70 C with `HNNNN`, exon-junction-spanning for expression, then route the pair to primer-specificity and run a standard curve.

## Co-Design Primers and a TaqMan Probe

**Goal:** Produce a short, Tm-matched amplicon with an internal probe whose Tm is 8-10 C above the primers and whose 5' base is not G.

**Approach:** Turn on internal-oligo picking, set the primer Tm window and a short product range, RAISE the `PRIMER_INTERNAL_*` Tm window 8-10 C above the primers (the defaults equal the primer Tm), and forbid a 5'-G probe with `PRIMER_INTERNAL_MUST_MATCH_FIVE_PRIME='HNNNN'`. For an expression assay add `SEQUENCE_OVERLAP_JUNCTION_LIST`.

```python
import primer3

template = 'ATGC...'  # cDNA (mark the junction position if expression-specific)

result = primer3.design_primers(
    seq_args={'SEQUENCE_ID': 'assay1', 'SEQUENCE_TEMPLATE': template},
    global_args={
        'PRIMER_PICK_LEFT_PRIMER': 1, 'PRIMER_PICK_RIGHT_PRIMER': 1,
        'PRIMER_PICK_INTERNAL_OLIGO': 1,                 # design the probe
        'PRIMER_PRODUCT_SIZE_RANGE': [[70, 150]],        # short amplicon for efficiency
        'PRIMER_NUM_RETURN': 3,
        'PRIMER_OPT_TM': 60.0, 'PRIMER_MIN_TM': 58.0, 'PRIMER_MAX_TM': 62.0,
        'PRIMER_PAIR_MAX_DIFF_TM': 2.0,
        'PRIMER_INTERNAL_OPT_TM': 70.0, 'PRIMER_INTERNAL_MIN_TM': 68.0, 'PRIMER_INTERNAL_MAX_TM': 72.0,
        'PRIMER_INTERNAL_MUST_MATCH_FIVE_PRIME': 'HNNNN',  # IUPAC H = A/C/T = not G at the probe 5' end
        # 'SEQUENCE_OVERLAP_JUNCTION_LIST': [junction_pos],  # add for cDNA-specific assays
    })

for i in range(result['PRIMER_PAIR_NUM_RETURNED']):
    probe = result[f'PRIMER_INTERNAL_{i}_SEQUENCE']
    print(result[f'PRIMER_LEFT_{i}_SEQUENCE'], result[f'PRIMER_RIGHT_{i}_SEQUENCE'], probe,
          'probe5=', probe[0], 'probeTm=', round(result[f'PRIMER_INTERNAL_{i}_TM'], 1),
          'size=', result[f'PRIMER_PAIR_{i}_PRODUCT_SIZE'])
```

## Exon-Junction Spanning, and Its Limits

For a cDNA-specific assay, place a primer or the probe across a splice junction with `SEQUENCE_OVERLAP_JUNCTION_LIST = [pos]` plus `PRIMER_MIN_3_PRIME_OVERLAP_OF_JUNCTION` (default 4) and `PRIMER_MIN_5_PRIME_OVERLAP_OF_JUNCTION` (default 7); the 3' overlap is the specificity-determining knob because a primer that only overlaps at its 5' end can still prime off gDNA from its 3' anchor. The internal-oligo equivalents (`PRIMER_INTERNAL_MIN_3_PRIME_OVERLAP_OF_JUNCTION` / `_5_PRIME_`) constrain the probe. The hard caveat: this does NOT protect against processed pseudogenes, which typically carry the junction in DNA -- so the assay still needs a genome specificity check (-> primer-specificity), DNase treatment, and a no-RT control. Intron-flanking (primers in different exons across a large intron) is the alternative, but fails across tiny introns.

## Assembling a Multiplex Panel

Multiplex is the most failure-prone mode; assemble it in order: (1) design each assay independently (short amplicon, matched Tm, probe offset); (2) check ALL primer+probe oligos pairwise for cross-dimers -- for k assays that is O((2k primers + k probes)^2) checks (a 5-plex = 10 primers + 5 probes = 105 pairwise calls), weighting 3'-end involvement (-> primer-validation); (3) run in-silico PCR over the POOLED primer set so cross-pair amplicons (one assay's forward meeting another's reverse) are caught (-> primer-specificity); (4) assign spectrally distinct fluorophores -- the instrument's optical channels and spectral overlap CAP the plex (most platforms resolve ~4-6 dyes, with color compensation), so the channel count, not the chemistry, usually limits a high-plex; (5) match efficiencies on a multiplex standard curve and primer-limit the abundant targets so they do not starve the rare ones.

## Per-Method Failure Modes

### Fold-changes reported without measuring efficiency
**Trigger:** Applying `2^-ddCq` without a standard curve. **Mechanism:** the method assumes target and reference efficiencies are matched and ~100%; if not, fold-changes are systematically biased. **Symptom:** numbers that are not measurements; results that do not replicate across instruments. **Fix:** run a standard curve, report E/slope/R^2 (MIQE), and use Pfaffl if efficiencies differ.

### Probe Tm not 8-10 C above primers
**Trigger:** Leaving `PRIMER_INTERNAL_*` Tm at the default (equal to the primers). **Mechanism:** the probe is not bound when the polymerase extends through it, so the exonuclease never cleaves it. **Symptom:** weak or no TaqMan signal. **Fix:** raise the internal Tm window 8-10 C above the primer window.

### 5'-G on the probe
**Trigger:** Not forbidding a 5' guanine. **Mechanism:** a 5'-G quenches the reporter even after cleavage. **Symptom:** low signal despite good amplification. **Fix:** `PRIMER_INTERNAL_MUST_MATCH_FIVE_PRIME='HNNNN'` or filter returned probes; prefer the C-rich strand.

### Assuming exon-junction primers are gDNA-proof
**Trigger:** Trusting junction-spanning alone. **Mechanism:** processed pseudogenes carry the spliced junction in genomic DNA. **Symptom:** a positive no-RT control; a genomic amplicon at the cDNA size. **Fix:** genome specificity check (primer-specificity), DNase, and a no-RT control.

### Primer-dimers in a SYBR assay
**Trigger:** Any extendable cross-dimer with SYBR detection. **Mechanism:** the dye reports the dimer, which competes with and can swamp a low-copy target. **Symptom:** a low-Tm shoulder in the melt curve; inflated NTC/low-copy signal. **Fix:** inspect the melt curve for a single sharp peak; validate dimers at reaction conditions (primer-validation).

### Single, unvalidated reference gene
**Trigger:** Normalizing to GAPDH/ACTB by habit. **Mechanism:** the reference may itself be regulated by the treatment. **Symptom:** apparent target changes that track a moving normalizer. **Fix:** rank a candidate panel with geNorm/NormFinder and validate stability in the actual experimental conditions.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| Efficiency 90-110% (slope -3.6 to -3.1, ideal -3.32), R^2 > 0.99 | Bustin 2009 *Clin Chem* 55:611 | the acceptance band that keeps `2^-ddCq` valid |
| Amplicon 70-150 bp | Bustin 2009 *Clin Chem* 55:611 | short products denature/re-prime fully each short cycle -> ~100% E |
| Primer Tm ~58-62 C, pair within 2 C | Koressaar & Remm 2007 *Bioinformatics* 23:1289 | one anneal-extend temperature; matched so neither lags |
| Probe Tm 8-10 C above primer Tm | -- | probe bound before/during extension so the exonuclease can cleave it |
| Probe: no 5'-G, prefer C-rich strand | -- | a 5'-G (and G-richness) quenches the reporter; the standard rule for 5'-reporter hydrolysis probes (reporter/quencher-chemistry dependent) |
| Standard curve: 5-6 points, 10-fold, triplicate | Bustin 2009 *Clin Chem* 55:611 | defines E, R^2, dynamic range, LOD |
| Reference genes: >=2 validated | Vandesompele 2002 *Genome Biol* 3:RESEARCH0034 | geometric mean of stable references beats one gene |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| Weak/no TaqMan signal | probe Tm too low, or 5'-G | raise `PRIMER_INTERNAL_*` Tm 8-10 C; `HNNNN`; C-rich strand |
| No probe returned (0 pairs) | internal Tm window unreachable on this template | widen/lower internal Tm or product range; check with `PRIMER_EXPLAIN_FLAG=1` |
| Positive no-RT control | gDNA / pseudogene amplification | junction-span + genome check (primer-specificity) + DNase |
| Poor efficiency (slope steep/shallow) | amplicon too long, dimers, off-target, or template inhibitors/degraded standard | shorten amplicon, fix dimers (primer-validation), check specificity, clean up template |
| Low-Tm melt peak (SYBR) | primer-dimer | redesign to remove 3'-end cross-dimers (primer-validation) |
| Fold-changes do not replicate | unmatched efficiency, unvalidated reference | match E or use Pfaffl; validate references with geNorm/NormFinder |

## References

- Bustin SA, Benes V, Garson JA, et al. 2009. The MIQE guidelines: minimum information for publication of quantitative real-time PCR experiments. *Clin Chem* 55:611-622.
- Untergasser A, Cutcutache I, Koressaar T, et al. 2012. Primer3 - new capabilities and interfaces. *Nucleic Acids Res* 40:e115.
- Livak KJ, Schmittgen TD. 2001. Analysis of relative gene expression data using real-time quantitative PCR and the 2(-Delta Delta C(T)) method. *Methods* 25:402-408.
- Pfaffl MW. 2001. A new mathematical model for relative quantification in real-time RT-PCR. *Nucleic Acids Res* 29:e45.
- Vandesompele J, De Preter K, Pattyn F, et al. 2002. Accurate normalization of real-time quantitative RT-PCR data by geometric averaging of multiple internal control genes. *Genome Biol* 3:RESEARCH0034.
- Andersen CL, Jensen JL, Orntoft TF. 2004. Normalization of real-time quantitative RT-PCR data: a model-based variance estimation approach to identify genes suited for normalization. *Cancer Res* 64:5245-5250.
- Koressaar T, Remm M. 2007. Enhancements and modifications of primer design program Primer3. *Bioinformatics* 23:1289-1291.

## Related Skills

- primer-basics - Design fundamentals, Tm matching, and the constraint model
- primer-validation - Dimers/hairpins of primers and probe at reaction conditions
- primer-specificity - Genome/pseudogene specificity and gDNA exclusion checking
- sequence-manipulation/transcription-translation - Work with cDNA and reading frames
- differential-expression/deseq2-basics - Downstream analysis qPCR validates against
<!-- END FILE: primer-design/qpcr-primers/SKILL.md -->

<!-- END CATEGORY: primer-design -->

