---
slug: bio-clinical-biostatistics-integrated
version: 1.0.1
displayName: "临床生物统计学 / Clinical biostatistics"
name: bio-clinical-biostatistics-integrated
summary: "中文：临床生物统计学综合技能，整合 12 个相关专题，覆盖临床生物统计学：CDISC SDTM/ADaM、logistic回归、亚组分析、生存分析、缺失数据敏感性分析。 English: Integrated Clinical biostatistics skill covering 12 related topics, including Clinical biostatistics: CDISC SDTM/ADaM, logistic regression, subgroup analysis, survival analysis, missing data sensitivity."
description: "中文：这是一个面向临床生物统计学的综合生物信息学 Skill，整合当前分类下 12 个相关专题能力。它用于根据研究问题、数据类型和分析阶段，选择合适的方法与工具，规划从输入检查、预处理、核心分析到质量控制、统计解释和结果报告的完整流程。重点覆盖：临床生物统计学：CDISC SDTM/ADaM、logistic回归、亚组分析、生存分析、缺失数据敏感性分析。当用户提供相关实验数据、测序结果、表格或研究问题时，它会帮助判断分析目标与前置条件，给出工具选择、关键参数、输入输出、常见失败原因、结果解读和可复现建议。主要工具包括：RBesT, gMCP, lifelines。该 Skill 提供分析设计与实施指导，不替代对具体数据质量、生物学背景和最终结论的人工审查。 English: This is an integrated bioinformatics Skill for Clinical biostatistics, combining 12 related topic areas. It helps users choose appropriate methods and tools based on the research question, data type, and analysis stage, and plan an end-to-end workflow from input validation and preprocessing through core analysis, quality control, statistical interpretation, and reporting. It covers Clinical biostatistics: CDISC SDTM/ADaM, logistic regression, subgroup analysis, survival analysis, missing data sensitivity. For relevant experimental data, sequencing results, tables, or research questions, it clarifies prerequisites, recommends tools and parameters, describes expected inputs and outputs, explains common failure modes, and supports reproducible analysis. Primary tools include: RBesT, gMCP, lifelines. It provides methodological and implementation guidance; final data-quality assessment and biological conclusions still require human review."
---

# clinical-biostatistics 分类 Skill 整合版

> 本文件整合同一主分类目录下 12 个子目录中的 SKILL.md 内容。
> 各子目录正文按原文保留，并通过标题和边界标记进行区分；源文件中的元数据块未被改写。

---

<!-- BEGIN CATEGORY: clinical-biostatistics -->

## 子目录：clinical-biostatistics/adaptive-designs

<!-- BEGIN FILE: clinical-biostatistics/adaptive-designs/SKILL.md -->
---
name: bio-clinical-biostatistics-adaptive-designs
description: Designs adaptive clinical trials including group-sequential (O'Brien-Fleming, Pocock, Lan-DeMets spending), sample-size re-estimation (blinded Friede-Kieser, unblinded Cui-Hung-Wang, Mehta-Pocock promising zone), seamless Phase 2/3 with treatment-arm selection, population enrichment, and response-adaptive randomisation. Covers FDA 2019 Final Adaptive Designs Guidance, FDA 2022 Master Protocols, and ICH E20 Step 2b/3 draft (June 2025, NOT final). Use when planning interim analyses, sample-size re-estimation, or master/platform-trial designs.
tool_type: r
primary_tool: rpact
goal_approach_exempt: true
---

## Version Compatibility

Reference examples tested with: R `rpact` 4.2+ (Wassmer/Brannath), `gsDesign` 3.6+ and `gsDesign2` 1.1+ (Anderson/Merck), `adaptr`, `simtrial`. Commercial: East/EastHorizon (Cytel), ADDPLAN (ICON), FACTS (Berry Consultants).

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('<pkg>')` then `?function_name`
- Python adaptive packages are limited; R is the regulatory de facto standard

If code throws an error, introspect the installed package and adapt the example to match the actual API rather than retrying.

# Adaptive Clinical Trial Designs

**"Design an adaptive trial"** -> Pre-specify a design with one or more interim adaptations (early stopping, sample-size re-estimation, treatment selection, population enrichment, randomisation ratio changes) that strongly controls Type-I error at the trial-wide level via combination tests or the Conditional Rejection Probability principle.

## Regulatory Status -- The 2024-2026 Landscape

**FDA 2019 Final Adaptive Designs Guidance** (Federal Register 2019-25986, Dec 2 2019) finalised the 2010 and 2018 drafts. Recognises 5 design types: group-sequential, blinded SSR, unblinded SSR, adaptive enrichment, adaptive randomisation.

**FDA 2022 Final Master Protocols Guidance** (March 2022, NOT 2018 — common citation error): basket (one drug, many diseases), umbrella (multiple drugs, one disease), platform (perpetual, drugs enter/exit).

**ICH E20 Adaptive Clinical Trials**: **Step 2b draft June 25 2025; Step 3 public consultation (EU deadline Nov 30 2025; FDA Federal Register Sept 30 2025); Step 4 final expected in 2026.** As of May 2026, ICH E20 is NOT final. The EFPIA/PhRMA position paper preceded the formal ICH work; Berry Consultants public comment letter is one of the more important submissions.

**FDA CDER Bayesian Methodology Draft (Jan 2026)** (FDA-2025-D-3217): first-ever drug-side Bayesian guidance; permits Bayesian primary inference in pivotals with simulation-based Type-I error calibration.

**Project Optimus (FDA OCE, 2021-2024)**: rewrites Phase I/II oncology by requiring randomised dose comparison before registration, replacing MTD-and-go. Made BOIN, mTPI-2, and multi-arm dose-finding the default.

## Algorithmic Taxonomy

| Design type | Adaptation | Type-I preservation | Software | Strength | Fails when |
|-------------|-----------|---------------------|----------|----------|------------|
| Group-sequential (O'Brien-Fleming) | Early stopping for efficacy/futility | Boundary calculation; very conservative early, near-nominal at end | rpact, gsDesign | FDA's preferred adaptive design | More complex SAP; IDMC firewall essential |
| Group-sequential (Pocock) | Early stopping | Constant nominal alpha at each look | rpact, gsDesign | Easy early stopping | Large penalty at final analysis |
| Wang-Tsiatis power family | Early stopping | Parameterised by Delta | rpact | Tunable conservatism | Δ choice matters |
| Lan-DeMets spending function | Early stopping (flexible timing) | Alpha-spending function | rpact, gsDesign | Operational flexibility; analyses don't need pre-specified number | FDA's de facto preferred framework |
| Blinded SSR (Friede-Kieser 2006) | Re-estimate variance/event-rate; recompute n | No Type-I inflation; agency-uncontroversial | rpact | EMA/FDA endorsed | Variance estimate must be blinded |
| Unblinded SSR (Cui-Hung-Wang 1999) | Increase n based on interim effect estimate | Requires CHW weights for control; or Mehta-Pocock promising zone | rpact | Recovers power if interim promising | IDMC firewall must be perfect; Jennison-Turnbull 2015 critique |
| Mehta-Pocock promising zone (2011) | Increase n if conditional power in (0.3, 0.8) | Calibrated so Type-I inflation negligible (~0.001) | rpact | Operational simplicity | "Stealth alpha inflation" critique (Jennison 2015) |
| Bauer-Köhne 1994 combination | Combine stagewise p-values via Fisher product | Any pre-specified design modification | rpact | Most flexible; theoretical foundation | Power loss vs designed group-sequential |
| Müller-Schäfer 2001 CRP principle | Preserve null conditional rejection probability | Any adaptation at any time | rpact | Modern theoretical bedrock | Implementation complexity |
| Adaptive enrichment | Drop sub-populations failing futility | Closed-test stage-wise | rpact, adaptr | Recovers power on responders | Selection bias on enriched population |
| Response-adaptive randomisation | Update allocation probabilities | Stratification + time-trend covariates required | adaptr, FACTS | Patient-welfare; learn-and-confirm | Drift bias, estimator bias; controversial (Hey-Kimmelman 2015 ethics) |
| Bayesian platform (I-SPY 2 style) | RAR + biomarker stratification + graduation criterion | Frequentist OCs via simulation | FACTS, custom Stan/JAGS | Modern oncology adaptive | Operational complexity; requires IDMC sophistication |

**Postdoc reading list:**

- Bauer P, Köhne K 1994 *Biometrics* 50:1029 (combination test; original adaptive)
- Cui L, Hung HMJ, Wang SJ 1999 *Biometrics* 55:853 (CHW weighted test for unblinded SSR)
- Müller HH, Schäfer H 2001 *Biometrics* 57:886 (CRP principle — theoretical bedrock)
- Mehta CR, Pocock SJ 2011 *Stat Med* 30:3267 (promising zone)
- Jennison C, Turnbull BW 2015 *Stat Med* 34(29):3793-3810 (Mehta-Pocock critique)
- Friede T, Kieser M 2006 *Biom J* 48:537 (blinded SSR)
- Lan KKG, DeMets DL 1983 *Biometrika* 70:659 (alpha spending function)
- O'Brien PC, Fleming TR 1979 *Biometrics* 35:549 (OBF boundary)
- Pocock SJ 1977 *Biometrika* 64:191 (Pocock boundary)
- Hey SP, Kimmelman J 2015 *Clin Trials* 12:102 (RAR ethics critique)
- Berry DA 2015 commentary *Clin Trials* 12:107 (counter)
- Robertson DS, Lee KM, López-Kolkovska BC, Villar SS 2023 *Stat Sci* 38:185 (canonical modern RAR review)
- Wassmer G, Brannath W 2016 *Group Sequential and Confirmatory Adaptive Designs in Clinical Trials* (Springer)
- Jennison C, Turnbull BW 2000 *Group Sequential Methods with Applications to Clinical Trials* (CRC)

## Decision Tree by Scenario

| Scenario | Recommended approach | Why |
|----------|---------------------|-----|
| Confirmatory trial wanting interim early stopping | Group-sequential with O'Brien-Fleming boundaries via gsDesign | FDA-preferred; near-nominal final alpha |
| Group-sequential with flexible look timing | Lan-DeMets spending function | Operational flexibility; FDA de facto preferred |
| Phase 3 with uncertain nuisance parameter (variance, event rate) | Blinded SSR (Friede-Kieser) | No Type-I inflation; agency-uncontroversial |
| Phase 3 wanting to increase n if interim shows promise | Mehta-Pocock promising zone with CHW weights | Recovers power; calibrated Type-I |
| Seamless Phase 2/3 with arm selection | Bauer-Köhne combination test + closed testing | Most flexible; cite Müller-Schäfer CRP |
| Adaptive enrichment (drop subpopulation) | Adaptive enrichment with closed-test stage-wise | Recovers power on responders |
| Multi-arm oncology platform | Bayesian platform with RAR (I-SPY 2 model) | Patient-welfare argument strong for multi-arm |
| 2-arm phase 3 oncology with potential RAR | Avoid RAR; group-sequential preferred | Hey-Kimmelman 2015 ethics + drift bias |
| Continuous endpoint, treatment discontinuation, follow-up data available | Hybrid: J2R imputation for treatment-discontinuation ICEs, MMRM-MAR for other missingness | Aprocitentan PRECISION precedent (2024); FDA de facto standard 2024-2025 for treatment-policy estimands |
| Phase 1 dose-finding | BOIN (FDA Fit-for-Purpose qualified 2021) | Transparent, tabulated decisions; no bedside Bayesian software |
| Phase 1b/2 dose-optimisation (Project Optimus) | Multi-arm BOIN-12 or multi-dose randomised | FDA Aug 2024 final dose-optimisation guidance |
| Basket trial (one drug, multiple diseases) | EXNEX or robust MAP via RBesT | Borrows across baskets while permitting one to detach |
| Umbrella trial (one disease, multiple drugs) | Bayesian platform with shared control | FDA Master Protocols 2022 |
| Pediatric extrapolation borrowing from adults | Power prior with discount γ in 0.3-0.6 | FDA Bayesian Jan 2026 draft endorses |

## Group-Sequential Designs

### O'Brien-Fleming -- the regulatory default

```r
library(gsDesign)

# OBF boundaries; 3 interim looks at 33%, 67%, 100% information
design <- gsDesign(
    k = 4,                  # total analyses including final
    test.type = 1,          # 1-sided efficacy
    alpha = 0.025,
    beta = 0.10,            # power = 0.90
    sfu = sfLDOF,           # Lan-DeMets approximation of OBF
    timing = c(0.25, 0.50, 0.75, 1.0)
)
print(design)
plot(design)
```

OBF is **very conservative at early looks** (nominal alpha approximately 0.0001 at 25% info) and **near-nominal at final analysis** (~0.024 of 0.025). Preferred by FDA because the final-analysis penalty is small.

### Pocock -- constant nominal

Constant nominal alpha at each look. Easy early stopping but large final-analysis penalty (~0.018 of 0.025 with k=4). Rarely used in confirmatory.

### Lan-DeMets spending function -- the modern flexibility

```r
# Lan-DeMets OBF-like spending function (sfLDOF)
# Allows analysis timing to differ from pre-specified
design_flex <- gsDesign(
    k = 3,
    sfu = sfLDOF,      # OBF-like spending
    alpha = 0.025,
    beta = 0.10
)

# Actual analyses can occur at different information fractions
# Spending function returns alpha to spend at each look based on actual timing
```

**The flexibility:** sponsor can perform analyses at different information fractions than originally planned. FDA's de facto preferred framework.

### Sample-size for group-sequential

```r
# Time-to-event group-sequential
library(gsDesign)
n_gs <- gsSurv(
    k = 3,
    test.type = 2,    # 2-sided
    alpha = 0.025,
    beta = 0.10,
    sfu = sfLDOF,
    lambdaC = 0.04,   # control hazard per month
    hr = 0.70,        # treatment HR
    eta = 0.005,      # dropout hazard
    T = 24,           # total study duration
    minfup = 12       # minimum follow-up
)
print(n_gs)
```

## Sample-Size Re-Estimation

### Blinded SSR (Friede-Kieser 2006)

Re-estimate nuisance parameter (variance σ² for continuous, control event rate p_0 for binary, overall event rate for survival) from blinded interim data. **No Type-I error inflation when test statistic ignores the SSR.**

```r
library(rpact)
# Blinded SSR for continuous outcome
design_blinded_ssr <- getDesignGroupSequential(
    kMax = 2,
    alpha = 0.025,
    beta = 0.20,
    sided = 1,
    informationRates = c(0.5, 1)
)

# At interim, re-estimate variance and recompute n
# (manual implementation; rpact has built-in support via getDesignInverseNormal for unblinded)
```

EMA Reflection Paper 2007 and FDA 2019 explicitly endorse blinded SSR. **Uncontroversial.**

### Unblinded SSR (Cui-Hung-Wang 1999)

Interim effect estimate triggers sample-size change. **Type-I inflation if naive:** Cui-Hung-Wang showed 8% Type-I vs 2.5% target.

The Cui-Hung-Wang weighted test uses pre-specified weights from the original design:

```
Z_weighted = w_1 * Z_1 + w_2 * Z_2_residual
```

where w_1, w_2 are the pre-specified weights (based on original n_1, n_2) and Z_2_residual is the test statistic on the data after the interim. **Pre-specified weights preserve alpha** even if the actual n at stage 2 differs.

```r
library(rpact)
design_unblinded_ssr <- getDesignInverseNormal(
    kMax = 2,
    alpha = 0.025,
    beta = 0.20,
    sided = 1,
    informationRates = c(0.5, 1),
    typeOfDesign = 'WT',  # Wang-Tsiatis power family
    deltaWT = 0.25
)

# Use inverse normal combination for adaptive SSR
analysis_result <- getAnalysisResults(
    design_unblinded_ssr,
    dataInput = getDataMeans(...)
)
```

### Mehta-Pocock Promising Zone (2011)

At interim, compute conditional power (CP) given observed effect:

- **Unfavourable zone** (CP < ~30%): stop or continue without modification
- **Promising zone** (CP in 30-80%): increase n to recover power; NO Type-I penalty if increase rule pre-specified and uses original test statistic with original weights
- **Favourable zone** (CP > 80%): continue without change

```r
# rpact implementation
# Sample size recalculation in promising zone
n_increased <- getSampleSizeMeans(
    design_unblinded_ssr,
    alternative = 5,        # detect mean diff of 5
    stDev = 12,
    groups = 2
)
```

**The mathematical sleight:** promising zone is constructed so unconditional Type-I error inflation is negligible (~0.001) even WITHOUT CHW weighting. **Jennison-Turnbull 2015 critique:** stealth alpha inflation in unpublished simulation assumptions; inefficient relative to CHW-weighted GSD. Mehta defends on operational grounds.

**Edwards et al 2020 *Trials* 21:1000** is the systematic review.

## Combination Tests and CRP Principle

**Bauer-Köhne 1994** *Biometrics* 50:1029: combine stagewise p-values via Fisher's product test. Permits design modifications post-interim while controlling Type-I error.

**Müller-Schäfer 2001** *Biometrics* 57:886: **Conditional Rejection Probability (CRP) principle** — preserve the null conditional rejection probability at every adaptation, and unconditional Type-I is preserved. The theoretical bedrock of all post-2001 confirmatory adaptive designs.

Müller-Schäfer 2004 *Stat Med* 23:2497 extended to ANY design change at ANY time.

```r
# rpact natively supports combination tests
design_comb <- getDesignFisher(
    kMax = 3,
    alpha = 0.025,
    sided = 1
)

# Or inverse normal combination
design_inv_norm <- getDesignInverseNormal(
    kMax = 3,
    alpha = 0.025,
    informationRates = c(0.33, 0.67, 1.0)
)
```

## Adaptive Enrichment

Drop sub-populations failing futility; re-power on responders. **Closed-test stage-wise** to control familywise error across full and enriched populations.

```r
# rpact: enrichment design via getDesignEnrichmentSubgroup
# Standard implementation requires explicit definition of full population (F)
# and enriched population (S)
```

**Postdoc concern:** selection bias on the enriched population — the observed treatment effect on the enriched subgroup is biased upward by selection. Bias-correction via simulation or hierarchical Bayesian.

## Response-Adaptive Randomisation -- The Ethics Fight

**Hey & Kimmelman 2015 *Clin Trials* 12:102 "Are outcome-adaptive allocation trials ethical?"** Argued RAR's purported ethical advantage (equipoise, sub-optimal exposure minimisation) **fails in two-arm and early-phase settings** because:

1. Drift bias inflates Type-I error / biases estimates (time trends confounded with allocation)
2. Consent dynamics confused — patients believe allocation is "personalised" when stochastic
3. Marginal patient-welfare benefit is statistical and small while operational risks real

**Counter-arguments:**

- **Berry DA 2015 commentary** *Clin Trials* 12:107: RAR enables learn-and-confirm, multi-arm platforms (I-SPY 2 model) where the patient-welfare argument IS the point and equal allocation would be unethical given accumulating evidence.
- **Saville & Berry 2016 *Clin Trials* 13:358:** RAR's operating characteristics are competitive in multi-arm platforms. Drift bias and Type-I inflation are controlled by adjusting for temporal trends (time-trend covariates) alongside stratification and proper analysis weights -- the "Bayesian time machine" approach developed in later work.
- **Buyse 2015 *Clin Trials* 12:119:** Hey-Kimmelman correct for 2-arm but wrong for multi-arm.

**Consensus position (2020s; ICH E20):** RAR appropriate when (a) multi-arm (>=3 arms), (b) rare disease / limited pool, (c) strong PoC of differential biomarker response, (d) robust drift-bias adjustment and pre-specified analysis weights. **Inappropriate for confirmatory 2-arm trials.**

**Robertson, Lee, López-Kolkovska, Villar 2023 *Stat Sci* 38:185 ("Response-adaptive randomization: from myths to practical considerations")** is the canonical modern review settling the debate.

## Bayesian Platform Trials

**I-SPY 2 (Barker-Sigman 2009 *Clin Pharmacol Ther*; Park-Liu 2016 *NEJM* 375:11):** neoadjuvant breast cancer; 10 biomarker-defined subtypes × multiple arms; Bayesian RAR; graduation criterion = posterior predictive probability of success in 300-patient Phase 3 ≥ 85%. Berry Consultants designed the engine. Multiple drugs graduated (neratinib, veliparib, pembrolizumab).

**GBM AGILE (Alexander 2018; published readouts beginning 2024):** glioblastoma; response-adaptive Bayesian; first global registrational platform in neuro-oncology. Regorafenib readout 2025 *JCO* JCO-25-01137.

**REMAP-CAP (Angus 2020 *JAMA*):** severe pneumonia, repurposed for COVID-19 in 2020; **Bayesian factorial multi-domain design** — multiple intervention domains tested simultaneously and combinatorially. Generated corticosteroid signal in COVID independently of RECOVERY.

### Drop-the-loser vs promising-the-winner

- **Adaptive arm-dropping (futility):** Bayesian posterior probability of beating control drops below threshold -> arm closes. Mathematically straightforward; FDA-acceptable.
- **"Promising-the-winner" (graduate to Phase 3):** introduces selection bias. Bias-adjusted estimators (Robertson 2023; conditional MLE) now standard in I-SPY 2 reports.

## Phase I Dose-Finding -- BOIN, mTPI, CRM

| Design | Citation | Idea | Where it wins |
|--------|----------|------|---------------|
| CRM | O'Quigley-Pepe-Fisher 1990 | Single-parameter logistic/power model; updates posterior MTD probability after each cohort | Statistically efficient; skeleton calibration needed |
| EWOC | Babb-Rogatko-Zacks 1998 | CRM-like with explicit overdose-control constraint (P(dose > MTD) <= 0.25) | Safer than CRM in small trials |
| mTPI | Ji et al 2010 *Clin Trials* 7:653 | Beta-binomial; UPM decision rule on under/proper/over-dosing intervals | Pre-tabulated decisions; documented over-shoot bias |
| mTPI-2 / Keyboard | Guo-Wang-Yang-Lynn-Ji 2017 | Fixes mTPI Ockham bias by equal-width intervals | Default mTPI replacement |
| BOIN | Liu-Yuan 2015 *J R Stat Soc C* 64:507 | Pre-tabulated escalation interval bounds optimised to minimise incorrect-decision probability | **FDA Fit-for-Purpose qualified Dec 2021**; near-CRM with no bedside software |

**Why FDA prefers BOIN operationally:** qualified as Fit-for-Purpose under FDA's Drug Development Tools program (FDA Determination Letter, December 10, 2021). Investigator uses pre-printed escalation table — no real-time Bayesian software at the bedside.

R packages: `BOIN`, `dfcrm` (Cheung — author of CRM textbook), `trialr` (Brock — includes EffTox), `escalation` (Brock — unified framework).

## Reconciliation: When Methods Disagree

| Pattern | Likely cause | Action |
|---------|--------------|--------|
| Blinded SSR n vs unblinded SSR n differ substantially | Unblinded SSR uses interim effect estimate; blinded uses nuisance parameter only | Blinded is Type-I-clean; unblinded requires CHW weighting; pre-specify the approach in SAP |
| Group-sequential rejects at interim; Cui-Hung-Wang weighted final test does not | Naive interim rejection used original test statistic; CHW weights downweight late data | Pre-specify boundary and weights; do NOT switch tests mid-stream |
| Mehta-Pocock promising-zone vs CHW-weighted GSD give different n increases | Promising zone calibrated for Type-I (~0.001 inflation); CHW more efficient under known effect | Jennison-Turnbull 2015 critique: promising zone "stealth alpha"; pre-specify with simulation OCs |
| Adaptive enrichment selects subgroup at interim; replication shows smaller effect | Selection bias on enriched population (winner's curse) | Bias-correction via conditional MLE or hierarchical Bayesian; cite Robertson 2023 |
| RAR posterior allocation favours active in 2-arm trial; randomisation drift bias suspected | Time trends confounded with allocation changes | Pre-specify time-trend covariates in analysis; use proper analysis weights; cite Robertson 2023 RAR consensus (RAR INAPPROPRIATE for 2-arm confirmatory) |
| BOIN vs CRM choose different MTD on same data | CRM uses model; BOIN uses tabulated boundaries; differ when skeleton mis-calibrated | BOIN Fit-for-Purpose qualified (Dec 2021); CRM more efficient under correct skeleton; report OCs over both |
| I-SPY 2 graduation criterion met but Phase 3 replication fails | Selection bias on graduated arm; PP threshold not bias-corrected | Apply conditional MLE; cite Robertson 2023; report both raw and bias-corrected estimates |
| Müller-Schäfer CRP preserved but ad hoc rule appears Type-I-inflated in simulation | Implementation deviation from formal CRP | Verify CRP equation precisely; report OCs via simulation; cite Müller-Schäfer 2001 |

## Per-Method Failure Modes

### Unblinded SSR with naive sample increase

- **Trigger:** Sponsor increases n based on interim effect without CHW weighting.
- **Mechanism:** Type-I inflation up to 8% (Cui-Hung-Wang 1999 simulation).
- **Symptom:** Independent reanalysis finds Type-I > 5%.
- **Fix:** Pre-specify CHW weights from original design; use combination test in rpact.

### Mehta-Pocock promising-zone "stealth alpha"

- **Trigger:** Promising-zone applied without sufficient simulation.
- **Mechanism:** Jennison-Turnbull 2015 critique — Type-I inflation hidden in unpublished simulation assumptions.
- **Symptom:** Independent reanalysis finds Type-I 5.3% vs nominal 5%.
- **Fix:** Pre-specify increase rule transparently; report simulation OCs.

### RAR drift bias

- **Trigger:** RAR in trial with time trends (calendar effects, learning curves).
- **Mechanism:** Time trends confounded with allocation changes; biased effect estimate.
- **Symptom:** Effect estimate sensitive to time-trend adjustment.
- **Fix:** Pre-specify time-trend covariates in analysis; use proper analysis weights; cite Robertson 2023.

### Schoenfeld formula under immunotherapy delayed effect

- **Trigger:** Sample size calculated via Schoenfeld 1981 assuming PH.
- **Mechanism:** Delayed effect violates PH; events under-estimated by 20-50%.
- **Symptom:** Trial under-powered; observed events insufficient.
- **Fix:** Lakatos 1988 or simulation under expected HR(t); cite Lin 2020 NPH Working Group.

### IDMC firewall failure in unblinded SSR (IDMC = Independent Data Monitoring Committee; the regulatory-standard term)

- **Trigger:** Interim effect estimate leaks beyond IDMC.
- **Mechanism:** Sponsor inference from increase decision reveals direction of interim effect.
- **Symptom:** Regulator audit reveals unblinding.
- **Fix:** Strict firewall SOP; only "increase / no increase" communicated to sponsor; cite ICH E20.

### Adaptive enrichment selection bias

- **Trigger:** Enriched population effect reported without bias correction.
- **Mechanism:** Selection on subgroup with promising interim effect inflates estimate.
- **Symptom:** Independent replication on enriched subgroup gives smaller effect.
- **Fix:** Bias-correction via simulation or hierarchical Bayesian; cite Robertson 2023 for bias-adjusted estimation.

### RAR in 2-arm confirmatory

- **Trigger:** RAR applied to confirmatory 2-arm trial.
- **Mechanism:** Hey-Kimmelman 2015 critique — drift bias, consent confusion, marginal benefit.
- **Symptom:** Reviewer rejects RAR as inappropriate for setting.
- **Fix:** Group-sequential with futility/efficacy boundaries instead; cite Robertson 2023 consensus.

### CRM skeleton mis-calibration

- **Trigger:** CRM applied with default skeleton without simulation.
- **Mechanism:** Skeleton dictates target dose; mis-calibration biases MTD.
- **Symptom:** MTD selection differs systematically from clinical expectation.
- **Fix:** Calibrate skeleton via Lee-Cheung 2009 indifference-interval method; or switch to BOIN.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| FDA Fit-for-Purpose BOIN qualification (Dec 2021) | FDA Drug Development Tools program | First dose-finding design with formal FDA endorsement |
| Mehta-Pocock promising zone CP 30-80% | Mehta-Pocock 2011 | Mathematical calibration for Type-I preservation |
| RAR appropriate >= 3 arms | Robertson 2023 consensus | Multi-arm patient-welfare argument |
| OBF nominal alpha ~0.024 at final / 0.025 | gsDesign | Small final penalty preferred by FDA |
| Schoenfeld under non-PH under-estimates 20-50% | Lin 2020 NPH WG | Use Lakatos or simulation |
| I-SPY 2 graduation: PP success in Phase 3 >= 85% | Barker 2009 | Bayesian platform standard |
| Power prior discount γ 0.3-0.6 for pediatric extrapolation | FDA Bayesian Jan 2026 draft | Partial borrowing default |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| Unblinded SSR with naive sample increase | No CHW weighting | Pre-specify CHW weights; cite Cui-Hung-Wang 1999 |
| Mehta-Pocock without simulation OCs | Stealth alpha inflation | Report simulation OCs; cite Jennison 2015 |
| RAR in 2-arm confirmatory | Misapplication | Group-sequential instead; cite Robertson 2023 |
| Schoenfeld for immuno-oncology | PH assumption violated | Lakatos or simulation; cite Lin 2020 |
| Adaptive enrichment effect reported uncorrected | Selection bias | Bias-correction; cite Robertson 2023 |
| CRM with default skeleton | Mis-calibration | Calibrate via Lee-Cheung 2009 or switch to BOIN |
| ICH E20 cited as "finalised April 2024" | Confusion with EFPIA position paper | ICH E20 is Step 2b/3 draft (June 2025); not final |
| FDA Master Protocols "2018" | 2018 was draft | March 2022 was the final |
| Bauer-Köhne combination test as "old-fashioned" | Misunderstanding | Foundational; cited in modern combination-test implementations |
| Stop-for-efficacy at first interim with OBF | OBF nominal alpha ~0.0001 at 25% info | Trial must show very strong evidence to stop early; expected |

## Anticipated Reviewer Pushback

| Pushback | Response |
|----------|----------|
| "How is Type-I error controlled?" | Closed testing via Müller-Schäfer CRP principle; specific implementation is inverse normal combination test in rpact |
| "Why these boundaries?" | OBF via Lan-DeMets sfLDOF spending function; preserves final-analysis power; pre-specified in SAP |
| "Pre-specification of SSR rule?" | Promising zone CP in (0.3, 0.8) triggers increase to n_max via CHW-weighted statistic; pre-specified n_max in SAP |
| "IDMC firewall?" | IDMC receives interim effect estimate; sponsor receives only "increase / no increase" decision; SOP documented; pre-specified |
| "RAR ethics?" | Multi-arm (4 arms) setting; Berry 2015 consensus that patient-welfare argument valid; drift-bias adjustment in primary analysis |
| "Promising zone vs CHW-weighted GSD?" | Operational simplicity preferred; OCs from simulation confirm Type-I ~5%; supportive Cui-Hung-Wang analysis |
| "Adaptive enrichment bias?" | Bias-correction via simulation; conditional MLE for enriched-population effect; cite Robertson 2023 |
| "Phase 1 BOIN vs CRM?" | BOIN Fit-for-Purpose qualified by FDA Dec 2021; tabulated decisions; no bedside Bayesian software |

## References

- Babb J, Rogatko A, Zacks S. 1998. Cancer Phase I clinical trials: efficient dose escalation with overdose control. *Stat Med* 17:1103-1120.
- Bauer P, Köhne K. 1994. Evaluation of experiments with adaptive interim analyses. *Biometrics* 50:1029-1041.
- Berry DA. 2015. Commentary on Hey & Kimmelman. *Clin Trials* 12:107-109.
- Cui L, Hung HMJ, Wang SJ. 1999. Modification of sample size in group sequential clinical trials. *Biometrics* 55:853-857.
- FDA. 2019. Adaptive Designs for Clinical Trials of Drugs and Biologics. Final Guidance.
- FDA. 2022. Master Protocols: Efficient Clinical Trial Design Strategies to Expedite Development of Oncology Drugs and Biologics. Final Guidance, March 2022.
- FDA. 2026. Use of Bayesian Methodology in Clinical Trials. Draft Guidance, January 2026.
- Friede T, Kieser M. 2006. Sample size recalculation in internal pilot study designs. *Biom J* 48:537-555.
- Hey SP, Kimmelman J. 2015. Are outcome-adaptive allocation trials ethical? *Clin Trials* 12:102-106.
- Jennison C, Turnbull BW. 2015. Adaptive sample size modification in clinical trials: start small then ask for more? *Stat Med* 34(29):3793-3810.
- Lan KKG, DeMets DL. 1983. Discrete sequential boundaries for clinical trials. *Biometrika* 70:659-663.
- Liu S, Yuan Y. 2015. Bayesian optimal interval designs for phase I clinical trials. *JRSS-C* 64:507-523.
- Mehta CR, Pocock SJ. 2011. Adaptive increase in sample size when interim results are promising. *Stat Med* 30:3267-3284.
- Müller HH, Schäfer H. 2001. Adaptive group sequential designs for clinical trials: combining the advantages of adaptive and of classical group sequential approaches. *Biometrics* 57:886-891.
- O'Brien PC, Fleming TR. 1979. A multiple testing procedure for clinical trials. *Biometrics* 35:549-556.
- O'Quigley J, Pepe M, Fisher L. 1990. Continual reassessment method: a practical design for phase 1 clinical trials in cancer. *Biometrics* 46:33-48.
- Pocock SJ. 1977. Group sequential methods in the design and analysis of clinical trials. *Biometrika* 64:191-199.
- Robertson DS, Lee KM, López-Kolkovska BC, Villar SS. 2023. Response-adaptive randomization in clinical trials: from myths to practical considerations. *Stat Sci* 38:185-208.
- Wassmer G, Brannath W. 2016. *Group Sequential and Confirmatory Adaptive Designs in Clinical Trials*. Springer.

## Related Skills

- clinical-biostatistics/power-and-sample-size - Sample size for adaptive designs
- clinical-biostatistics/multiplicity-graphical - Closed testing in adaptive contexts
- clinical-biostatistics/bayesian-trials - Bayesian platform trials, BOIN/CRM/EWOC
- clinical-biostatistics/trial-reporting - Reporting adaptive trial results per CONSORT 2025
- clinical-biostatistics/survival-analysis - Adaptive designs for TTE endpoints
- experimental-design/sample-size - General sample-size methods
<!-- END FILE: clinical-biostatistics/adaptive-designs/SKILL.md -->

## 子目录：clinical-biostatistics/bayesian-trials

<!-- BEGIN FILE: clinical-biostatistics/bayesian-trials/SKILL.md -->
---
name: bio-clinical-biostatistics-bayesian-trials
description: Designs Bayesian clinical trials including Phase I dose-finding (BOIN, CRM, EWOC, mTPI-2), meta-analytic-predictive (MAP) priors with robust mixtures for external data borrowing, EXNEX for basket trials, hierarchical models for safety AE (Berry-Berry), Bayesian platform trials (I-SPY 2, GBM AGILE, REMAP-CAP), and posterior probability stopping rules. Covers FDA Bayesian Devices Guidance (2010), FDA Bayesian Methodology in Drugs Draft (January 2026), BOIN Fit-for-Purpose qualification (December 2021), and Project Optimus dose-optimisation. Use when designing dose-finding studies, platform trials, or sensitivity analyses with informative priors.
tool_type: r
primary_tool: RBesT
goal_approach_exempt: true
---

## Version Compatibility

Reference examples tested with: R `RBesT` 1.7+ (Roche), `OncoBayes2` 0.8+ (Novartis), `BOIN` 2.7+, `dfcrm` 0.2-2+, `escalation` 0.1+, `trialr` 0.1.6+, `bayesDP`, `psborrow2` (FDA-supported), `rstan` / `cmdstanr`, `brms`. Legacy: `JAGS`, `WinBUGS`.

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('<pkg>')` then `?function_name`
- Confirmatory regulatory work: validate against pinned package versions in submission

If code throws an error, introspect the installed package and adapt the example to match the actual API rather than retrying.

# Bayesian Clinical Trials

**"Design a Bayesian clinical trial"** -> Specify a prior, likelihood, and decision rule with frequentist operating characteristics demonstrated via simulation; for dose-finding use FDA-endorsed BOIN; for borrowing use robust MAP priors; for adaptive platforms use posterior probability of efficacy stopping with simulation-calibrated thresholds.

## Regulatory Status -- The 2024-2026 Bayesian Pivot

**FDA 2010 CDRH Bayesian Devices Guidance** (Feb 5 2010): the only Bayesian-specific FDA guidance until January 2026. Why devices were ahead: CDRH's PMA pathway permits one pivotal trial and accepts borrowing from prior/OUS data more readily than CDER. Example: Edwards SAPIEN (PARTNER B, PMA P100041, Nov 2011) was approved on a single randomized pivotal trial (TAVR vs standard therapy in inoperable patients); the later SAPIEN 3 intermediate-risk PMA used a propensity-score comparison of a single-arm cohort against PARTNER IIA surgical controls -- illustrating CDRH's acceptance of non-randomized/borrowed comparisons.

**FDA January 2026 CDER Bayesian Methodology Draft** (FDA-2025-D-3217; comment period closed March 13 2026): first-ever drug-side Bayesian guidance. Explicit that Bayesian primary inference in pivotals is acceptable provided:
- Prospective specification
- Simulation-based operating characteristics (including frequentist Type-I error under null scenarios — agency still wants calibration)
- Justified priors
- Code/data sufficient for FDA replication

**Project Optimus (FDA OCE, launched 2021; final dose-optimisation guidance Aug 2024):** rewrites Phase I/II oncology by requiring randomised dose comparison before registration. Has made multi-arm randomised dose-finding (BOIN-12, gBOIN-ET) much more important than classic MTD-finding.

**FDA BOIN Fit-for-Purpose qualification (December 2021):** first formal FDA endorsement of a specific dose-finding design under the Drug Development Tools program.

**ICH E20 (Step 2b/3 draft June 2025; NOT final)** treats Bayesian as a legitimate analytic framework but requires demonstration of acceptable frequentist operating characteristics (Type-I, power) over a pre-specified parameter space.

## Algorithmic Taxonomy

| Method | Use case | Software | Strength | Fails when |
|--------|----------|----------|----------|------------|
| BOIN | Phase I MTD | R `BOIN` (Yuan) | **FDA Fit-for-Purpose 2021**; pre-tabulated decisions; no bedside Bayesian software | Statistically less efficient than CRM under correct skeleton |
| mTPI-2 / Keyboard | Phase I MTD | R `escalation`; R `Keyboard` | Default replacement for mTPI; fixes Ockham bias | Tabulated; transparency |
| CRM | Phase I MTD | R `dfcrm`, `trialr` | Most efficient under correct skeleton | Skeleton mis-specification biases MTD |
| EWOC | Phase I MTD | R `ewoc`, `dfcrm` | Explicit overdose-control constraint (P(dose>MTD) <= 0.25) | More conservative than CRM in small trials |
| BOIN-12 / gBOIN-ET | Phase 1b dose-optimisation (Project Optimus) | R `BOIN` extensions | Multi-arm randomised dose comparison | Requires explicit efficacy + toxicity scoring |
| MAP prior | Borrowing from historical control arms | R `RBesT::gMAP` | Industry-standard borrowing | Sample-size of MAP prior must be calibrated (Schmidli 2014) |
| Robust MAP | Borrowing with prior-data conflict protection | R `RBesT::robustify` | Adds vague component (weight 0.1-0.3) to detach if conflict | Mixture weight choice affects borrowing |
| EXNEX | Basket trial across rare-disease strata | R `bhmbasket`; OncoBayes2 | Avoids HM catastrophic borrowing; mixture 0.5/0.5 default (Neuenschwander 2016) | Default weights may over-borrow |
| Dixon-Simon shrinkage | Subgroup analysis | Custom Stan/brms | Honest about no qualitative interaction prior | Prior on tau drives results |
| Berry-Berry 3-level hierarchical | AE multiplicity (AE within PT within SOC) | R `c212`; JMP Clinical | Tames safety multiplicity | Spike-and-slab tuning matters |
| Posterior probability stopping | Adaptive sequential | Custom; FACTS commercial | Bayesian likelihood-principle compatible | Threshold calibration via simulation |
| Predictive probability of success | End-of-Phase-2 go/no-go | Custom Stan | Decision-theoretic; integrates over posterior | Requires Phase 3 design specified |
| Spiegelhalter skeptical/enthusiastic prior | Sensitivity for regulatory pivotals | Custom | Frames regulator-vs-sponsor evidence | Prior elicitation effort |
| Power prior | Pediatric extrapolation borrowing from adults | R `bayesDP`, `psborrow2` | Partial borrowing with discount gamma | gamma choice (Jan 2026 FDA draft: 0.3-0.6) |

**Postdoc reading list:**

- FDA 2010 *Guidance for Industry: Use of Bayesian Statistics in Medical Device Clinical Trials* (Feb 5 2010)
- FDA 2026 Draft *Use of Bayesian Methodology in Clinical Trials* (FDA-2025-D-3217, Jan 2026)
- Berry SM, Carlin BP, Lee JJ, Müller P 2010 *Bayesian Adaptive Methods for Clinical Trials* (CRC)
- Schmidli H, Gsteiger S, Roychoudhury S, O'Hagan A, Spiegelhalter D, Neuenschwander B 2014 *Biometrics* 70:1023 (MAP + robust MAP)
- Weber S, Li Y, Seaman J, Kakizume T, Schmidli H 2021 *J Stat Softw* 100:19 (RBesT)
- Neuenschwander B, Wandel S, Roychoudhury S, Bailey S 2016 *Pharm Stat* 15:123 (EXNEX)
- Liu S, Yuan Y 2015 *J R Stat Soc C* 64:507 (BOIN)
- O'Quigley J, Pepe M, Fisher L 1990 *Biometrics* 46:33 (CRM)
- Babb J, Rogatko A, Zacks S 1998 *Stat Med* 17:1103 (EWOC)
- Ji Y, Liu P, Li Y, Bekele BN 2010 *Clin Trials* 7:653 (mTPI)
- Guo W, Wang SJ, Yang S, Lynn H, Ji Y 2017 *Contemp Clin Trials* 58:23 (mTPI-2 / Keyboard)
- Berry SM, Broglio KR, Groshen S, Berry DA 2013 *Clin Trials* 10:720 (basket trial hierarchical)
- Berry SM, Berry DA 2004 *Biometrics* 60:418 (three-level AE hierarchical)
- Spiegelhalter DJ, Freedman LS, Parmar MKB 1994 *JRSS-A* 157:357 (skeptical/enthusiastic prior framework)
- Rugo HS et al 2016 *NEJM* 375:23 (I-SPY 2 veliparib-carboplatin)
- Angus DC et al 2020 *JAMA* (REMAP-CAP COVID rationale)

## Decision Tree by Scenario

| Scenario | Recommended approach | Why |
|----------|---------------------|-----|
| Phase 1 oncology, single-agent MTD | BOIN with target DLT 30%; cohort size 3 | FDA Fit-for-Purpose 2021; tabulated escalation |
| Phase 1 oncology, combination (2 agents) | BLRM with EXNEX in OncoBayes2 | Multi-dimensional dose; industry standard at Novartis/Roche |
| Phase 1b/2 dose-optimisation (Project Optimus) | BOIN-12 or gBOIN-ET; randomised 2-dose comparison | Aug 2024 FDA dose-optimisation guidance |
| Phase 3 with historical control arms available | Robust MAP via RBesT; gMAP() + robustify() | Industry standard borrowing with prior-data conflict protection |
| Basket trial across rare-disease strata | EXNEX (0.5 EX / 0.5 NEX mixture) via OncoBayes2 | Avoids HM catastrophic borrowing |
| Pediatric extrapolation from adult data | Power prior with discount gamma 0.3-0.6 | working convention; the FDA Bayesian Jan 2026 draft does not prescribe a specific gamma range -- check the draft for the current language before quoting |
| Phase 3 trial with single arm + RWE comparator | Propensity-score-integrated power prior via psborrow2 | FDA-supported package for external controls |
| Adaptive trial wanting posterior-probability stopping | Custom Stan model + simulation-calibrated threshold | Bayesian likelihood-principle compatible; no penalty for repeated looks |
| End-of-Phase-2 go/no-go | Predictive probability of success in Phase 3 | Integrates posterior over Phase 3 design |
| Hypothesis-generating safety AE analysis (>100 PTs) | Berry-Berry 3-level hierarchical (AE within PT within SOC) | Tames multiplicity; spike-and-slab on log OR |
| Subgroup analysis post-signal | Bayesian shrinkage (Dixon-Simon, RBesT) | Hemmings-Koch 2019: shrinkage for replication planning, NOT signal generation |
| Regulatory pivotal sensitivity | Spiegelhalter skeptical-prior framework | Frames "evidence for regulators" vs "evidence for sponsor" |

## Phase I Dose-Finding -- BOIN, CRM, mTPI-2

### BOIN (FDA-preferred operational)

```r
library(BOIN)

# Generate escalation table for protocol
boundary_table <- get.boundary(
    target = 0.30,           # target DLT rate
    ncohort = 10,            # 10 cohorts -> max 30 patients with size 3
    cohortsize = 3,
    n.earlystop = 12,        # stop early at lowest dose if 12 patients show futility
    p.saf = 0.6 * 0.30,      # "safe" escalation boundary
    p.tox = 1.4 * 0.30       # "toxic" de-escalation boundary
)
print(boundary_table)
# Pre-printed at investigator desk; no bedside Bayesian software

# Operating characteristics simulation
oc_boin <- get.oc(
    target = 0.30,
    p.true = c(0.05, 0.10, 0.20, 0.30, 0.40, 0.55),  # true DLT per dose
    ncohort = 10,
    cohortsize = 3,
    ntrial = 1000
)
print(oc_boin)
# Reports: MTD selection accuracy, overdose risk, average sample size
```

**BOIN's transparency-over-modelling philosophy:** unlike CRM, BOIN does NOT use information from intermediate dose levels in a model-based way. The Jin-Yuan vs Neuenschwander/Mozgunov debate (Stat Med, Pharm Stat, since ~2018): BLRM/CRM are statistically more efficient under correct model; BOIN is operationally simpler and more transparent.

### CRM with calibrated skeleton

```r
library(dfcrm)

prior_skeleton <- getprior(halfwidth = 0.05, target = 0.30, nu = 3, nlevel = 6)
# Lee-Cheung 2009 indifference-interval calibration

crm_sim <- crmsim(
    PI = c(0.05, 0.10, 0.20, 0.30, 0.40, 0.55),
    prior = prior_skeleton,
    target = 0.30,
    n = 30,
    x0 = 1,                  # starting dose
    nsim = 1000,
    method = 'bayes',
    model = 'logistic'
)
print(crm_sim)
```

**Skeleton mis-specification is the canonical CRM failure mode.** Lee-Cheung 2009 indifference-interval method gives a systematic calibration approach.

### EWOC (overdose control)

```r
# Babb-Rogatko-Zacks 1998: explicit P(dose > MTD) <= alpha (default 0.25)
# Implementation in dfcrm::ewoc; or `ewoc` package
```

## MAP Priors and RBesT

**Schmidli et al 2014 *Biometrics* 70:1023:** Meta-Analytic-Predictive prior. Fit random-effects meta-analysis of historical control arms; derive predictive distribution for new control arm; use as informative prior. Effective sample size from history typically 20-80% of new control arm.

```r
library(RBesT)

# Historical control data (4 prior studies)
historical_data <- data.frame(
    study = c('s1', 's2', 's3', 's4'),
    n = c(40, 35, 50, 45),
    r = c(8, 6, 12, 9)         # responders
)

# Fit MAP via gMAP (Stan-based random-effects meta-analysis)
map_prior <- gMAP(
    cbind(r, n - r) ~ 1 | study,
    data = historical_data,
    family = binomial,
    tau.dist = 'HalfNormal',
    tau.prior = 0.5,           # between-study SD prior
    beta.prior = cbind(0, 2)    # weakly informative on logit response
)
print(map_prior)

# Approximate posterior with mixture for downstream computation
map_mix <- automixfit(map_prior, Nc = 2)
print(map_mix)

# Effective sample size
ess(map_mix)

# Robust MAP: add vague mixture component (weight 0.1-0.3) to guard against prior-data conflict
robust_map <- robustify(map_mix, weight = 0.2, mean = 0.5, n = 1)
print(robust_map)
ess(robust_map)
```

**Robust MAP rationale:** if the new data disagree with historical (prior-data conflict), the mixture down-weights the informative component automatically. The mixture weight on the informative component is a tuning choice and should be varied in a pre-specified sensitivity analysis.

## EXNEX for Basket Trials

**Neuenschwander, Wandel, Roychoudhury, Bailey 2016 *Pharm Stat* 15:123:** Mixture of exchangeable (shared mean+variance) + non-exchangeable (per-basket independent), typically weighted 0.5/0.5. Avoids HM catastrophic borrowing when one basket truly different.

```r
library(OncoBayes2)  # Novartis-developed; canonical EXNEX implementation

# Or simplified via bhmbasket
library(bhmbasket)

# Conceptual: each basket has its own posterior, with shrinkage governed by exchangeability mixture
# Default weights 0.5 EX / 0.5 NEX
# Sensitivity over weights (0.1, 0.3, 0.5, 0.7, 0.9) is essential
```

## Bayesian Platform Trials

### I-SPY 2 (Rugo et al 2016 *NEJM* 375:23)

Neoadjuvant breast cancer; 10 biomarker-defined subtypes × multiple arms; Bayesian RAR; **graduation criterion = posterior predictive probability of success in 300-patient Phase 3 ≥ 0.85.** Berry Consultants designed engine.

```r
# Conceptual implementation requires custom Stan or FACTS (Berry Consultants commercial)

# Pseudocode:
# 1. Fit hierarchical model to platform data: response ~ arm + biomarker_subtype + arm:subtype
# 2. Posterior draws of treatment effect by subtype
# 3. For each draw, simulate Phase 3 trial: n=300, treatment vs control, observed effect
# 4. Compute proportion of draws meeting Phase 3 success criterion
# 5. If proportion >= 0.85, arm graduates
```

### REMAP-CAP (Angus 2020 *JAMA*)

Severe pneumonia, repurposed for COVID-19; Bayesian factorial multi-domain design. Generated corticosteroid signal independently of RECOVERY.

### Drop-the-loser vs promising-the-winner

- **Adaptive arm-dropping (futility):** posterior P(beating control) drops below threshold -> close. Mathematically straightforward.
- **"Promising-the-winner":** selection bias. Bias-adjusted estimators (Robertson 2023; conditional MLE) standard in I-SPY 2 reports.

## Hierarchical Models for Safety Multiplicity (Berry-Berry 2004)

**Berry SM, Berry DA 2004 *Biometrics* 60:418:** three-level hierarchical model for AE multiplicity (AE within MedDRA PT within SOC); spike-and-slab on the log OR. Tames the FDA-feared multiplicity in safety summaries.

```r
library(c212)  # Berry-Berry implementation

# Conceptual: each AE has log OR drawn from spike-and-slab prior
# Spike at 0 (no effect); slab as N(mu_SOC, sigma_SOC)
# SOC-level parameters from N(mu_overall, sigma_overall)
# Borrowing within SOC; shrinkage toward 0 if no evidence

# JMP Clinical also implements this for industry use
```

## Power Priors for Borrowing

```r
library(bayesDP)
library(psborrow2)  # FDA-supported package

# Power prior: combines current data L(theta | D_current) with historical L(theta | D_hist)^gamma
# gamma in [0, 1]; gamma = 0 = no borrowing; gamma = 1 = full pooling

# Typical pediatric extrapolation: gamma = 0.3 to 0.6 per FDA Bayesian Jan 2026 draft
```

## External Control Arms and Real-World Evidence (RWE)

**The 2024-2026 regulatory shift:** FDA has materially expanded acceptance of external/historical/synthetic control arms in rare disease, paediatric, and accelerated-approval settings. Key documents: FDA 2018 RWE Framework (and 2024 enhancements), FDA 2023 Considerations for Use of RWE/RWD for Regulatory Decisions, EMA Reflection Paper on Use of RWE in Regulatory Decision-Making (effective 2024). Bayesian methods are the natural fit because historical data become prior information rather than concurrent control.

### Methodology taxonomy

| Method | Borrowing mechanism | Discount control | When to use |
|--------|---------------------|------------------|-------------|
| Power prior (Ibrahim-Chen 2000) | Likelihood of historical data raised to power gamma | gamma in [0, 1] fixed or modelled | When historical data is single source; gamma ~ Beta in adaptive power prior |
| Robust MAP (Schmidli 2014) | Meta-analytic-predictive prior + vague mixture | Mixture weight (typ 0.1-0.3) | Multiple historical control arms; standard for borrowing |
| Commensurate prior (Hobbs 2011) | Conditional model on agreement parameter | Tau estimated from data | When agreement between historical and current is data-determined |
| Propensity-integrated power prior | Power prior weighted by PS overlap | gamma * (PS-trimmed overlap) | RWE comparator with covariate imbalance |
| Doubly robust ATT via causal inference | IPW + outcome regression | n/a | RWE comparator; identifies marginal ATT |

### psborrow2 — the FDA-supported RWE framework

The `psborrow2` package (Genentech / Bayer / FDA-Janssen collaboration; CRAN 2024+) is the canonical R implementation for propensity-score-integrated Bayesian Dynamic Borrowing. **The skeleton below illustrates the workflow conceptually; verify exact function names and arguments against the current `psborrow2` vignette before use** (the package API has evolved through 2024-2026).

```r
library(psborrow2)

# Define external and internal data
ext_data <- data.frame(usubjid = ..., trt = 0, outcome = ..., covariates = ...)
int_data <- data.frame(usubjid = ..., trt = 0 | 1, outcome = ..., covariates = ...)

# Create borrowing design
borrowing_design <- borrowing_full(
    method_name = "BDB",  # Bayesian Dynamic Borrowing
    ext_flag_col = "ext",
    tau_prior = prior_gamma(0.001, 0.001)  # weakly informative on borrowing
)

# Outcome model (Cox for TTE; logistic for binary)
outcome_model <- outcome_surv_exponential(
    time_var = "time",
    cens_var = "cens",
    baseline_prior = prior_normal(0, 100),
    trt_prior = prior_normal(0, 100)
)

# Run Bayesian analysis with covariate adjustment + borrowing
result <- create_analysis_obj(
    data_matrix = borrow_obj,
    outcome = outcome_model,
    borrowing = borrowing_design,
    covariates = c("age", "ecog", "baseline_severity")
)
mcmc_result <- mcmc_sample(result, n_chains = 4, n_iter = 4000)
```

### Operational rules (FDA 2024-2025 RWE practice)

1. **Pre-specify the RWE source** and document acquisition (registry, EHR, claims, RWD vendor)
2. **Demonstrate comparability** via propensity-score overlap (standardised mean differences <0.25 for key prognostic factors)
3. **Apply discount priors** — full pooling (gamma=1) is regulatory-rejected; typical discount gamma 0.3-0.6
4. **Sensitivity over borrowing strength** — report results at multiple gamma or mixture weights
5. **Tipping-point analysis on prior-data agreement** — at what discount does the conclusion flip?
6. **E-value or bound for unmeasured confounding** (VanderWeele-Ding 2017) — required for FDA submissions; reports the minimum strength of unmeasured confounding that could overturn the result

### When RWE is NOT acceptable

- Trial sponsor and RWE source have meaningful incentive misalignment (e.g., RWE from non-disinterested source)
- RWE captured before standard-of-care evolved (constancy violation, similar to NI biocreep)
- Outcome definitions differ between RWE and current trial (variable harmonisation impossible)
- Censoring patterns in RWE differ structurally from trial (administrative vs disease-driven)
- Highly variable baseline characteristics impossible to balance via propensity weighting

### Recent decisive cases (2024-2026)

- **Zynteglo (FDA 2022, ongoing post-market):** beta-thalassemia gene therapy; single-arm trial vs natural history RWE comparator
- **Skysona (FDA 2022):** cerebral adrenoleukodystrophy; RWE natural-history comparator
- **Multiple ultra-rare disease accelerated approvals 2024-2025:** RWE/external control increasingly accepted in <100-patient trials

## Spiegelhalter Skeptical/Enthusiastic Priors

**Spiegelhalter, Freedman, Parmar 1994 *JRSS-A* 157:357:** the trip-wire / skeptical-prior framework. Pre-specify a skeptical prior centred at the null and an enthusiastic prior centred at the alternative; stopping requires the skeptic to be convinced (posterior under skeptical prior exceeds threshold).

**Frames "evidence for regulators" vs "evidence for sponsor" in Bayesian language**; still cited in modern Bayesian-trial protocols.

```r
# Skeptical prior: N(0, sd_sk) — centred at null
# Enthusiastic prior: N(delta_alt, sd_en) — centred at clinically meaningful effect
# Decision: stop for efficacy if P(theta > 0 | skeptical posterior) > 0.975
#           stop for futility if P(theta < delta_alt | enthusiastic posterior) > 0.80
```

## Per-Method Failure Modes

### CRM with mis-calibrated skeleton

- **Trigger:** Default or arbitrary skeleton without indifference-interval calibration.
- **Mechanism:** Skeleton dictates target dose; mis-calibration biases MTD.
- **Symptom:** MTD selection differs systematically from clinical expectation.
- **Fix:** Calibrate via Lee-Cheung 2009; or switch to BOIN.

### MAP prior with prior-data conflict

- **Trigger:** Historical control rate differs substantially from observed current control.
- **Mechanism:** Informative MAP prior pulls toward historical; current data poorly fit.
- **Symptom:** Posterior dominated by prior; current data evidence under-weighted.
- **Fix:** Robust MAP with mixture weight 0.2-0.3; verify prior-data conflict via posterior predictive checks.

### EXNEX with default 0.5/0.5 weights

- **Trigger:** Default mixture weights without sensitivity.
- **Mechanism:** 50% EX weight allows substantial borrowing even when basket differs.
- **Symptom:** Detected differential basket "softened" by borrowing.
- **Fix:** Sensitivity analysis over weights (0.1, 0.3, 0.5, 0.7, 0.9); report range.

### Posterior probability stopping without simulation-calibrated threshold

- **Trigger:** Stopping rule P(theta > 0 | data) > 0.975 applied without Type-I simulation.
- **Mechanism:** Bayesian rule may not control frequentist Type-I in regulatory sense.
- **Symptom:** FDA review flags lack of Type-I demonstration.
- **Fix:** Simulate under null; calibrate threshold so frequentist Type-I = nominal.

### I-SPY 2 graduation criterion without bias correction

- **Trigger:** Graduated arm's effect estimate reported uncorrected.
- **Mechanism:** Selection on PP > 0.85 inflates estimate.
- **Symptom:** Phase 3 confirmation finds smaller effect than platform suggested.
- **Fix:** Bias-correction via conditional MLE or hierarchical Bayesian; cite Robertson 2023.

### Bayesian shrinkage for signal discovery (Dane vs Hemmings)

- **Trigger:** Hierarchical model fit during signal discovery rather than replication planning.
- **Mechanism:** Shrinkage pre-emptively damps heterogeneity being searched for.
- **Symptom:** Signal detected by causal forest gets shrunken to null in shrinkage analysis.
- **Fix:** Hemmings-Koch 2019 position — shrinkage for replication planning, not signal generation; cite Dane et al 2019 EFSPI white paper + critique.

### Power prior with gamma = 1 (full pooling)

- **Trigger:** Full pooling of historical and current data.
- **Mechanism:** Ignores between-study heterogeneity; biases estimate.
- **Symptom:** Overconfident posterior; cross-validation reveals poor fit.
- **Fix:** Working-convention discount gamma 0.3-0.6 (the FDA Bayesian Jan 2026 draft does not prescribe a specific range); sensitivity over gamma.

### WinBUGS reproducibility

- **Trigger:** Submission contains WinBUGS code without containerised environment.
- **Mechanism:** Older Windows-only software; reproducibility fragile.
- **Symptom:** Reviewer cannot replicate analysis.
- **Fix:** Migrate to Stan (`rstan`/`cmdstanr`); Docker/renv-pinned environment; include seeds + posterior diagnostics (R-hat <1.01, ESS >1000 per chain).

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| FDA BOIN Fit-for-Purpose qualification (Dec 2021) | FDA Drug Development Tools program | First formal FDA dose-finding endorsement |
| Target DLT rate 30% (Phase 1 oncology) | Standard convention | Modal target across oncology Phase 1 |
| MAP prior effective sample size 20-80% of new control | Schmidli 2014 | Borrowing strength typical range |
| Robust MAP mixture weight 0.1-0.3 | Schmidli 2014 | Guards against prior-data conflict |
| EXNEX default 0.5 EX / 0.5 NEX | Neuenschwander 2016 | Standard starting weight; sensitivity required |
| I-SPY 2 graduation PP >= 0.85 | I-SPY 2 operational reports (Rugo/Park 2016) | Bayesian platform standard |
| Power prior gamma 0.3-0.6 for pediatric extrapolation | working convention; the FDA Bayesian Jan 2026 draft does not prescribe a specific range | Partial borrowing default |
| Stan R-hat <1.01, ESS >1000 per chain | Vehtari 2021 *Bayesian Analysis* | Posterior convergence criteria |
| EWOC overdose constraint P(dose > MTD) <= 0.25 | Babb-Rogatko-Zacks 1998 | Safety floor |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| CRM with arbitrary skeleton | No calibration | Lee-Cheung 2009 indifference-interval; or BOIN |
| MAP without prior-data conflict check | Posterior dominated by prior | Robust MAP; PP-check; sensitivity over mixture weight |
| EXNEX with single weight scheme | No sensitivity | Weights 0.1, 0.3, 0.5, 0.7, 0.9; report range |
| Posterior probability stopping without Type-I sim | Regulatory rejection | Simulate under null; calibrate threshold |
| I-SPY 2 graduated arm reported uncorrected | Selection bias | Conditional MLE; cite Robertson 2023 |
| Bayesian shrinkage for signal discovery | Hemmings-Koch critique | Shrinkage for replication only |
| Power prior gamma = 1 | Full pooling | Discount 0.3-0.6 per FDA 2026 draft |
| WinBUGS without containerisation | Reproducibility | Stan + Docker/renv-pinned |
| BOIN vs CRM comparison without simulation OCs | Apples-to-oranges | Compare OCs over same true DLT rates |
| FDA cited for Bayesian drugs guidance pre-2026 | Confusion | FDA 2010 is DEVICES; FDA 2026 (draft) is drugs |

## Anticipated Reviewer Pushback

| Pushback | Response |
|----------|----------|
| "Type-I error control?" | Simulation under null demonstrates frequentist Type-I = nominal at threshold chosen; documented in SAP appendix |
| "Prior justification?" | MAP from historical control arms via gMAP; robust mixture weight 0.2 for prior-data conflict; sensitivity over prior provided |
| "Why BOIN over CRM?" | BOIN Fit-for-Purpose qualified Dec 2021; pre-tabulated escalation; no bedside Bayesian software; OCs comparable to CRM in simulation |
| "EXNEX weight sensitivity?" | Reported over weights 0.1, 0.3, 0.5, 0.7, 0.9; results stable; primary at 0.5/0.5 per Neuenschwander 2016 |
| "Power prior gamma?" | Discount 0.5 per FDA Bayesian Jan 2026 draft; sensitivity over 0.3-0.7 provided |
| "Posterior probability threshold?" | Calibrated via simulation to frequentist Type-I 0.025 one-sided; cite Berry 2010 |
| "Stan reproducibility?" | Docker container + renv-pinned R + Stan version; seeds provided; R-hat <1.01, ESS >2000 per parameter |
| "Bias correction on platform graduation?" | Conditional MLE applied to estimate Phase 3 effect; cite Robertson 2023 |
| "Why not frequentist instead?" | Bayesian framework permits borrowing (rare disease, pediatric); working convention; the FDA Bayesian Jan 2026 draft does not prescribe a specific gamma range -- check the draft for the current language before quoting primary inference with simulation calibration |

## References

- Babb J, Rogatko A, Zacks S. 1998. Cancer Phase I clinical trials: efficient dose escalation with overdose control. *Stat Med* 17:1103-1120.
- Berry SM, Berry DA. 2004. Accounting for multiplicities in assessing drug safety: a three-level hierarchical mixture model. *Biometrics* 60:418-426.
- Berry SM, Broglio KR, Groshen S, Berry DA. 2013. Bayesian hierarchical modeling of patient subpopulations: efficient designs of Phase II oncology clinical trials. *Clin Trials* 10:720-734.
- Berry SM, Carlin BP, Lee JJ, Müller P. 2010. *Bayesian Adaptive Methods for Clinical Trials*. CRC.
- Dane A, Spencer A, Rosenkranz G, Lipkovich I, Parke T. 2019. Subgroup analysis and interpretation for phase 3 confirmatory trials: EFSPI/PSI white paper. *Pharm Stat* 18:126-139.
- FDA. 2010. Guidance for Industry: Use of Bayesian Statistics in Medical Device Clinical Trials.
- FDA. 2021. BOIN Drug Development Tool Fit-for-Purpose Qualification.
- FDA. 2026. Use of Bayesian Methodology in Clinical Trials. Draft Guidance (FDA-2025-D-3217).
- Guo W, Wang SJ, Yang S, Lynn H, Ji Y. 2017. A Bayesian interval dose-finding design addressing Ockham's razor: mTPI-2. *Contemp Clin Trials* 58:23-33.
- Hemmings R, Koch A. 2019. Commentary on Dane et al. *Pharm Stat* 18:140-144.
- Ji Y, Liu P, Li Y, Bekele BN. 2010. A modified toxicity probability interval method for dose-finding trials. *Clin Trials* 7:653-663.
- Liu S, Yuan Y. 2015. Bayesian optimal interval designs for phase I clinical trials. *JRSS-C* 64:507-523.
- Neuenschwander B, Wandel S, Roychoudhury S, Bailey S. 2016. Robust exchangeability designs for early phase clinical trials with multiple strata. *Pharm Stat* 15:123-134.
- O'Quigley J, Pepe M, Fisher L. 1990. Continual reassessment method: a practical design for phase 1 clinical trials in cancer. *Biometrics* 46:33-48.
- Rugo HS et al. 2016. Adaptive randomization of veliparib-carboplatin treatment in breast cancer. *NEJM* 375:23-34.
- Robertson DS, Lee KM, López-Kolkovska BC, Villar SS. 2023. Response-adaptive randomization in clinical trials: from myths to practical considerations. *Stat Sci* 38:185-208.
- Schmidli H, Gsteiger S, Roychoudhury S, O'Hagan A, Spiegelhalter D, Neuenschwander B. 2014. Robust meta-analytic-predictive priors in clinical trials with historical control information. *Biometrics* 70:1023-1032.
- Spiegelhalter DJ, Freedman LS, Parmar MKB. 1994. Bayesian approaches to randomized trials. *JRSS-A* 157:357-387.
- Vehtari A et al. 2021. Rank-normalization, folding, and localization: an improved R-hat for assessing convergence. *Bayesian Analysis*.
- Weber S, Li Y, Seaman J, Kakizume T, Schmidli H. 2021. Applying meta-analytic-predictive priors with the R Bayesian evidence synthesis tools. *J Stat Softw* 100:19.

## Related Skills

- clinical-biostatistics/adaptive-designs - Group-sequential, SSR, platform trials
- clinical-biostatistics/subgroup-analysis - Bayesian shrinkage for HTE (Dixon-Simon, Berry)
- clinical-biostatistics/power-and-sample-size - Bayesian SS via predictive probability of success
- clinical-biostatistics/multiplicity-graphical - Berry-Berry AE hierarchical
- clinical-biostatistics/trial-reporting - Bayesian inference reporting per CONSORT 2025
- clinical-biostatistics/missing-data-sensitivity - Bayesian rbmi imputation
- machine-learning/biomarker-discovery - Bayesian HTE for biomarker subgroups
- experimental-design/sample-size - General methods
<!-- END FILE: clinical-biostatistics/bayesian-trials/SKILL.md -->

## 子目录：clinical-biostatistics/categorical-tests

<!-- BEGIN FILE: clinical-biostatistics/categorical-tests/SKILL.md -->
---
name: bio-clinical-biostatistics-categorical-tests
description: Tests associations between categorical variables in clinical data using chi-square, Fisher's exact, Boschloo, Cochran-Mantel-Haenszel, and modern McNemar variants with calibrated confidence intervals (Wilson, Newcombe, Miettinen-Nurminen). Use when analyzing categorical outcomes, paired binary endpoints, or testing treatment-outcome independence in confirmatory or exploratory clinical trials.
tool_type: python
primary_tool: scipy
---

## Version Compatibility

Reference examples tested with: scipy 1.12+ (Boschloo and Barnard added in 1.7), statsmodels 0.14+, pingouin 0.5+, exact2x2 (R) 1.6+, pandas 2.1+, numpy 1.26+.

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- R packages cited for reference (exact2x2, Exact, ratesci): use `packageVersion()` then `?function_name` to verify parameters

If code throws ImportError, AttributeError, or TypeError, introspect the installed package and adapt the example to match the actual API rather than retrying.

# Categorical Association Tests for Clinical Data

**"Test association between categorical variables"** -> Determine whether treatment and a categorical clinical outcome are statistically independent (or that marginal proportions agree, for paired data) using a test calibrated to the design, the sample size, and the regulatory question.

## Algorithmic Taxonomy

| Test | Design | Asymptotic / exact | Conditioning | Strength | Fails when |
|------|--------|--------------------|--------------|----------|------------|
| Pearson chi-square (no continuity correction) | Independent groups, any RxC | Asymptotic | None | Standard for n>=40 with all expected counts >=5; matches Miettinen-Nurminen score CI | Any expected cell <1; >20% of cells with expected <5 (Cochran 1954) |
| Fisher's exact (conditional) | Independent 2x2 | Exact | Conditions on BOTH margins | Exact small-sample guarantee on level | Conservative (true alpha << nominal); discards information by double conditioning (Mehta-Senchaudhuri 2003) |
| Boschloo's exact | Independent 2x2 | Exact unconditional | Conditions on ONE margin only | Uniformly more powerful than Fisher (Boschloo 1970; Mehta-Senchaudhuri 2003); preserves nominal alpha exactly | Computationally heavier; RxC extensions limited |
| Barnard's exact | Independent 2x2 | Exact unconditional | Conditions on ONE margin only | Maximises nuisance parameter; well-calibrated | Slightly less powerful than Boschloo on average; compute scales O(n^2) |
| CMH (Mantel-Haenszel) | Stratified independent groups | Asymptotic | Conditions within strata | Tests common-OR null across strata; pooled OR estimator | Assumes no qualitative interaction; misleading when ORs reverse direction across strata |
| Breslow-Day | Stratified independent groups | Asymptotic | Within strata | Tests homogeneity of stratum ORs | Underpowered with few strata or sparse strata; non-significance does NOT prove homogeneity |
| McNemar (asymptotic, no continuity correction) | Paired binary | Asymptotic | Conditions on discordant pairs | Fagerland 2013 default; outperforms exact conditional | Discordant pair count b+c < 25 (chi-square approximation breaks) |
| Mid-p McNemar | Paired binary | Quasi-exact | Discordant pairs | Fagerland-Lydersen-Laake 2013 recommended default; less conservative than exact conditional | Slight under-coverage tolerable at small b+c |
| Exact conditional McNemar (Liddell 1983) | Paired binary | Exact | Discordant pairs only | Guaranteed coverage | Over-conservative; loses power vs mid-p or unconditional |
| Suissa-Shuster exact unconditional | Paired binary | Exact unconditional | All N pairs | Uniformly more powerful than exact conditional McNemar; 20-40% smaller n for same power | Implementation only in R `exact2x2::mcnemarExactDP` and SAS macros |

**Postdoc reading:** Lydersen, Fagerland & Laake 2009 *Stat Med* 28:1159 ("Recommended tests for association in 2x2 tables") argues **Fisher's exact should be retired from routine use** in favour of Boschloo or asymptotic Pearson; Fagerland-Lydersen-Laake 2013 *BMC Med Res Methodol* 13:91 makes the parallel case for mid-p or asymptotic McNemar over exact conditional. Regulatory practice (FDA reviewers) is moving in this direction but Fisher and exact conditional McNemar remain entrenched in many SAPs by inertia.

## Decision Tree by Experimental Scenario

| Scenario | Recommended test | Why |
|----------|------------------|-----|
| Independent 2x2, all expected >=5, n>=40 | Pearson chi-square, `correction=False` | Standard asymptotic; Yates' continuity correction is overly conservative and now discouraged |
| Independent 2x2, expected <5 in any cell OR n<40 | Boschloo's exact (`scipy.stats.boschloo_exact`) | Uniformly more powerful than Fisher; preserves exact Type-I control |
| Independent RxC, expected <5 in >20% of cells | Permutation chi-square or Fisher-Freeman-Halton (R `coin::chisq_test(distribution = approximate())`) | Exact RxC asymptotic invalid; permutation preserves level |
| Stratified design (multi-site, multi-stratum randomisation) | CMH for the pooled test + Breslow-Day for homogeneity + per-stratum ORs | Stratification factor in randomisation MUST appear in analysis (Kahan-Morris 2012 *Stat Med* 31:328: ignoring is over-conservative -- SE biased upward, power loss) |
| Stratified with sign-reversing effect (Simpson's paradox suspected) | Always report stratum-specific ORs + visual diagnostic; consider logistic regression with interaction | CMH pooled OR can mask sign reversal; homogeneity test underpowered |
| Paired binary (pre/post on same subjects; matched case-control) | Asymptotic McNemar (`mcnemar(table, exact=False, correction=False)`) when b+c >= 25; mid-p when b+c < 25 | Fagerland 2013 simulations show mid-p and asymptotic outperform exact conditional |
| Matched-pair non-inferiority (especially diagnostics) | Suissa-Shuster exact unconditional via R `exact2x2` | 20-40% smaller n than exact conditional for same power |
| Composite endpoint (any of several events) | Logistic regression with covariate adjustment, not chi-square | Composite changes the estimand under ICH E9(R1); see clinical-biostatistics/effect-measures |

## Chi-Square Test (Pearson, no continuity correction)

**Goal:** Test whether treatment group and outcome category are independent under asymptotic Type-I control.

**Approach:** Construct a contingency table, verify expected cell counts, compute the Pearson chi-square statistic without Yates' continuity correction.

```python
from scipy.stats import chi2_contingency
import pandas as pd

table = pd.crosstab(df['treatment'], df['outcome'])
chi2, p, dof, expected = chi2_contingency(table, correction=False)
if (expected < 5).any():
    print('WARNING: switch to Boschloo (2x2) or permutation chi-square (RxC)')
```

**Cochran 1954 rule (the precise version, not the textbook caricature):** "no expected cell should be <1 AND no more than 20% of cells should have expected <5." The textbook "all >=5" rule is the conservative simplification. With well-balanced 2x2 trials this rarely matters; with sparse RxC tables it materially expands the asymptotic range. The R `chisq.test` issues a warning under the strict Cochran rule; Python users must check manually.

**Why Yates' correction is now discouraged:** continuity correction was introduced to approximate the exact distribution under H0 but inflates Type-II error by ~10% (D'Agostino, Chase & Belanger 1988 *Am Stat* 42:198). Modern computing makes Boschloo's exact test cheap; the correct fix for sparse 2x2 is Boschloo, not chi-square + continuity.

## Fisher's Exact -- and why Boschloo is usually better

**Goal:** Test 2x2 association with exact Type-I control.

**Approach:** Use Fisher's exact only when historical SAP requires it; otherwise prefer Boschloo's test.

```python
from scipy.stats import fisher_exact, boschloo_exact

odds_ratio, p_fisher = fisher_exact(table.values, alternative='two-sided')

# Boschloo (uniformly more powerful than Fisher):
# n= controls Sobol sampling resolution for the null distribution (scipy 1.12+; default 32);
# higher = more precise p-value at higher CPU cost. NOT the sample size per arm.
result = boschloo_exact(table.values, alternative='two-sided', n=64)
p_boschloo = result.pvalue
```

**The conditioning critique (Mehta-Senchaudhuri 2003):** Fisher's exact conditions on both margins of the 2x2 table, discarding information about the marginal totals. Boschloo conditions on one margin only and treats the second as a nuisance to be maximised over -- recovering the discarded information. Power gain at n=10/arm is 16-20 percentage points for moderate effects. Boschloo *uses Fisher's p-value as its test statistic*, then computes the exact unconditional null distribution of that p-value -- so it is automatically at least as powerful as Fisher.

**Since scipy 1.10**, `fisher_exact` returns the sample (unconditional) odds ratio, not the conditional MLE. For the conditional MLE matching R's `fisher.test`, use `scipy.stats.contingency.odds_ratio(table, kind='conditional')`.

## Cochran-Mantel-Haenszel (Stratified)

**Goal:** Test treatment-outcome association while controlling for a stratification variable; quantify the common odds ratio across strata.

**Approach:** Construct per-stratum 2x2 tables, compute MH pooled OR and CMH test of H0: common-OR = 1; test homogeneity via Breslow-Day.

```python
from statsmodels.stats.contingency_tables import StratifiedTable
import pandas as pd

tables = []
for stratum in df['site'].unique():
    stratum_data = df[df['site'] == stratum]
    t = pd.crosstab(stratum_data['treatment'], stratum_data['outcome']).values
    if t.shape == (2, 2) and t.min() > 0:
        tables.append(t)

st = StratifiedTable(tables)
print(st.test_null_odds())          # CMH H0: common OR = 1
print(st.oddsratio_pooled)          # MH pooled OR
print(st.oddsratio_pooled_confint(method='normal'))
print(st.test_equal_odds())         # Breslow-Day H0: equal stratum ORs
```

### Per-method failure modes

**CMH -- Simpson's paradox masking**

- **Trigger:** Stratum-specific ORs reverse direction across strata while the pooled MH OR appears null or modestly different from 1.
- **Mechanism:** CMH pools weighted log-ORs; equal-magnitude opposite-sign ORs cancel.
- **Symptom:** Breslow-Day p < 0.05 with stratum ORs visually reversing.
- **Fix:** Report stratum-specific ORs as primary; the MH pooled estimate is not a valid summary. Move to logistic regression with treatment-by-stratum interaction.

**Breslow-Day -- low-power false reassurance**

- **Trigger:** Few strata (k<5) or sparse strata (mean cell count <10).
- **Mechanism:** Breslow-Day chi-square has k-1 df; with k=3 and modest heterogeneity, power can be <40%.
- **Symptom:** Breslow-Day p > 0.5 with stratum ORs visually heterogeneous on a forest plot.
- **Fix:** Always supplement with a forest plot of stratum-specific ORs. Use likelihood-ratio interaction test from logistic regression as a second check.

**CMH -- ignoring randomisation stratification factors**

- **Trigger:** Randomisation was stratified (sex, region, baseline severity) but the primary analysis pools across strata.
- **Mechanism:** Stratified randomisation removes between-stratum variability that the unstratified SE still counts.
- **Symptom:** Over-conservative inference -- SE biased upward, CIs too wide, Type-I below nominal, power loss (Kahan-Morris 2012).
- **Fix:** Strata variables from randomisation MUST appear in analysis -- either CMH, logistic regression with strata, or stratified log-rank.

## McNemar's Test for Paired Binary Data

**Goal:** Test the null of marginal homogeneity (P(positive at time 1) = P(positive at time 2)) for paired binary observations.

**Approach:** Default to asymptotic McNemar without continuity correction when discordant pairs >=25; switch to mid-p when discordant pairs <25; reserve exact conditional only when regulator-mandated.

```python
from statsmodels.stats.contingency_tables import mcnemar
import numpy as np

# table[i,j] = count with outcome i at time 1 and j at time 2
table = np.array([[45, 15], [5, 35]])  # b=15, c=5 discordant

# Asymptotic, no continuity correction -- the Fagerland 2013 recommended default
result = mcnemar(table, exact=False, correction=False)
print(result.statistic, result.pvalue)

# Exact conditional (Liddell 1983) -- only when b+c is very small or required by SAP
result_exact = mcnemar(table, exact=True)
```

**Fagerland-Lydersen-Laake 2013 *BMC Med Res Methodol* 13:91 simulation findings:** mid-p McNemar and asymptotic McNemar (no continuity correction) outperform exact conditional McNemar across small-to-moderate samples. The exact conditional is *too conservative* because it conditions on a discrete margin (the discordant pair count). Their title is the methodological provocation -- "The McNemar test: asymptotic and mid-p are better than exact conditional."

**Suissa-Shuster 1991 *Biometrics* 47:361 exact unconditional** uses *all* N pairs (not just discordant) -- uniformly more powerful than exact conditional McNemar; sample sizes 20-40% smaller for the same power. Available in R `exact2x2::mcnemarExactDP`. Practically essential for matched-pair non-inferiority in diagnostic device trials.

## Effect Sizes for Categorical Data

**Goal:** Quantify association strength beyond p-values.

**Approach:** Phi for 2x2, Cramer's V for RxC; bias-corrected variants in pingouin.

```python
import numpy as np
import pingouin as pg

n = table.values.sum()
phi = np.sqrt(chi2 / n)
k = min(table.shape) - 1
cramers_v = np.sqrt(chi2 / (n * k))

# Pingouin with multiple test variants and bias correction:
expected, observed, stats = pg.chi2_independence(df, x='treatment', y='outcome')
# stats columns: test, lambda, chi2, dof, pval, cramer, power
```

**Cohen 1988 effect-size benchmarks:**

| df | Small | Medium | Large |
|----|-------|--------|-------|
| 1 | 0.10 | 0.30 | 0.50 |
| 2 | 0.07 | 0.21 | 0.35 |
| 3 | 0.06 | 0.17 | 0.29 |

Phi equals Cramer's V for 2x2 (k=1). For RxC, only Cramer's V is valid because phi can exceed 1.

## Reconciliation: When Methods Disagree

| Pattern | Likely cause | Action |
|---------|--------------|--------|
| Fisher exact p > 0.05 but Boschloo p < 0.05 | Fisher over-conservative via double-margin conditioning (Mehta-Senchaudhuri 2003); Boschloo recovers power | Cite Boschloo as primary; provide Fisher in appendix for transparency |
| Pearson chi-square p < 0.05 but Fisher exact p > 0.05 | Asymptotic approximation breaking down at small expected counts (Cochran rule violation) | Use Boschloo (exact unconditional, more powerful than Fisher); document expected-count diagnostic in SAP |
| CMH pooled OR not significant, stratum-specific ORs strongly differ | Simpson's paradox -- opposite-sign cancellation OR effect modification | Report stratum-specific ORs as primary; switch to logistic regression with treatment-by-stratum interaction; forest plot stratum ORs |
| Breslow-Day non-significant but stratum-OR forest plot visually heterogeneous | Low power of Breslow-Day with few/sparse strata | Cite low-power caveat; report LR interaction test from logistic as secondary; do NOT claim homogeneity |
| McNemar exact conditional p > 0.05 but mid-p McNemar p < 0.05 | Exact conditional over-conservative due to discrete-margin conditioning | Cite Fagerland-Lydersen-Laake 2013; mid-p or asymptotic recommended; exact conditional only when SAP-mandated |
| Suissa-Shuster unconditional p < exact conditional McNemar p | Unconditional uses all N pairs; conditional discards concordant pairs | Suissa-Shuster preferred for matched-pair NI (esp. diagnostic devices) due to 20-40% smaller n |
| Wald CI excludes null but Wilson/Newcombe CI overlaps null | Wald has poor coverage near 0 and 1 (Brown-Cai-DasGupta 2001) | Wilson/Newcombe/MN preferred; cite as regulatory standard |
| Multiple categorical secondary endpoints, correlation structure unclear | Bonferroni overly conservative; Hochberg requires PRDS (Sarkar 1998) | See clinical-biostatistics/multiplicity-graphical for Bretz-Maurer graphical procedures and PRDS check |

## Confidence Intervals for Proportions and Differences

For a single proportion, **Wald is bad** for small samples and extreme p (Brown-Cai-DasGupta 2001 *Stat Sci* 16:101 documents "chaotic" coverage with coverage dropping to 0.0 in extreme cells). Use Wilson score or Jeffreys.

For a 2x2 risk difference or risk ratio, the regulatory standard for CI is **Miettinen-Nurminen score-based** (1985 *Stat Med* 4:213) -- consistent with the Pearson chi-square test and accepted by FDA/EMA for noninferiority margins.

```python
from statsmodels.stats.proportion import proportion_confint, proportions_ztest

# Single proportion: Wilson is the modern default
ci = proportion_confint(45, 60, alpha=0.05, method='wilson')
# Also available: 'jeffreys', 'agresti_coull', 'beta' (Clopper-Pearson exact)

# Difference of proportions: Newcombe-Wilson hybrid / MOVER
from statsmodels.stats.proportion import confint_proportions_2indep
ci_diff = confint_proportions_2indep(45, 60, 30, 60, method='newcomb', alpha=0.05)
# 'wald' is discouraged; 'newcomb' (Newcombe-Wilson hybrid) and 'agresti-caffo' are calibrated
```

For Miettinen-Nurminen CIs (the regulatory standard for stratified RD or RR), use R `ratesci::scoreci(contrast='RD'|'RR', distrib='bin', stratified=TRUE)` -- there is no production-grade Python implementation as of 2026.

## Post-Hoc Pairwise Comparisons

```python
from statsmodels.stats.multitest import multipletests
from itertools import combinations

categories = df['outcome'].unique()
pvalues, comparisons = [], []
for cat1, cat2 in combinations(categories, 2):
    subset = df[df['outcome'].isin([cat1, cat2])]
    sub_table = pd.crosstab(subset['treatment'], subset['outcome'])
    _, p_val, _, _ = chi2_contingency(sub_table, correction=False)
    pvalues.append(p_val)
    comparisons.append(f'{cat1} vs {cat2}')

reject, adjusted_p, _, _ = multipletests(pvalues, method='holm')
```

`method='holm'` (FWER) for confirmatory; `method='fdr_bh'` for exploratory. **Critical bug:** `multipletests` default is `method='hs'` (Holm-Sidak), NOT Holm or Bonferroni -- always specify explicitly. The FDA Multiple Endpoints Final Guidance (October 2022) requires FWER control for key secondary endpoints in regulatory submissions; FDR is acceptable for exploratory subgroup screens only.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| n >= 40 for 2x2 chi-square | Cochran 1954 *Biometrics* 10:417 | Below this, asymptotic chi-square distribution approximation degrades regardless of expected counts |
| All expected >=5 OR <=20% with expected <5 AND none <1 | Cochran 1954 (strict) | Textbook "all >=5" is overconservative; the strict rule expands chi-square's valid range |
| Yates' correction discouraged | D'Agostino, Chase & Belanger 1988 *Am Stat* 42:198 | Overly conservative; correct fix for sparse 2x2 is Boschloo's exact, not continuity-corrected chi-square |
| Discordant pairs >=25 for asymptotic McNemar | Fagerland-Lydersen-Laake 2013 *BMC MRM* 13:91 | Below this, chi-square approximation breaks; switch to mid-p, not exact conditional |
| Newcombe-Wilson / Miettinen-Nurminen for RD CI | Newcombe 1998a *Stat Med* 17:873 | Wald CI for RD has poor coverage and can produce limits outside [-1, 1] |
| Boschloo > Fisher for small 2x2 | Mehta-Senchaudhuri 2003; Lydersen-Fagerland-Laake 2009 *Stat Med* 28:1159 | Boschloo uniformly more powerful at same Type-I |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| `multipletests(p)` returns Holm-Sidak adjusted p | Default method is 'hs' not Holm/Bonferroni | Always specify `method='holm'` or `'bonferroni'` explicitly |
| `Table2x2(crosstab.values)` gives reciprocal OR | `pd.crosstab` orders columns alphabetically; statsmodels expects event-positive column first | Reorder: `cross[[1, 0]]` or `cross[['Yes', 'No']]` |
| Fisher's exact in published paper, Boschloo missing | SAP inertia; reviewers unfamiliar with Boschloo | Cite Mehta-Senchaudhuri 2003 in the SAP; use Boschloo as primary with Fisher in appendix |
| `fisher_exact` returns "wrong" OR vs R | Since scipy 1.10, scipy returns sample (unconditional) OR; R returns conditional MLE | Use `scipy.stats.contingency.odds_ratio(table, kind='conditional')` to match R |
| CMH significant but stratum ORs reverse direction | Simpson's paradox; Breslow-Day underpowered | Forest plot stratum ORs; report stratum-specific as primary; switch to logistic with interaction |
| Yates' correction enabled by default in `chi2_contingency` | scipy default is `correction=True` for 2x2 | Always pass `correction=False` for Pearson chi-square |
| McNemar p-value much larger than expected | Default may be exact conditional in some packages; over-conservative | Use asymptotic without continuity correction (Fagerland 2013) |
| Stratified randomisation ignored in primary analysis | Common SAP error | Include strata in CMH, logistic, or stratified log-rank; ignoring is over-conservative -- SE biased upward, power loss (Kahan-Morris 2012) |

## Anticipated Reviewer Pushback

| Pushback | Response |
|----------|----------|
| "Why not Fisher's exact?" | Cite Lydersen-Fagerland-Laake 2009; Boschloo is uniformly more powerful at same alpha. Provide Fisher p in appendix for direct comparison. |
| "Why no continuity correction?" | D'Agostino-Chase-Belanger 1988 -- Yates' inflates Type-II by ~10%. The correct fix for sparse 2x2 is Boschloo's exact, not Yates'. |
| "Are these ORs collapsible?" | OR is non-collapsible (see clinical-biostatistics/effect-measures); marginal and conditional ORs differ even without confounding. Cite Permutt 2020. |
| "Why mid-p McNemar over exact conditional?" | Fagerland-Lydersen-Laake 2013 simulations show exact conditional is over-conservative; mid-p and asymptotic maintain nominal Type-I with better power. |
| "Adjustment for stratification factors?" | Per ICH E9 and FDA 2023 covariate adjustment guidance, strata from randomisation must appear in analysis. CMH or logistic with strata as covariates. |
| "What is the estimand?" | Per ICH E9(R1), categorical-test analyses target a specific estimand (treatment policy is implicit if all randomised analysed). Articulate explicitly. |

## References

- Boschloo RD. 1970. Raised conditional level of significance for the 2x2 table when testing the equality of two probabilities. *Stat Neerl* 24:1.
- Brown LD, Cai TT, DasGupta A. 2001. Interval estimation for a binomial proportion. *Stat Sci* 16:101-117.
- Cochran WG. 1954. Some methods for strengthening the common chi-squared tests. *Biometrics* 10:417-451.
- D'Agostino RB, Chase W, Belanger A. 1988. The appropriateness of some common procedures for testing the equality of two independent binomial populations. *Am Stat* 42:198-202.
- Fagerland MW, Lydersen S, Laake P. 2013. The McNemar test for binary matched-pairs data: mid-p and asymptotic are better than exact conditional. *BMC Med Res Methodol* 13:91.
- FDA. 2022. Multiple Endpoints in Clinical Trials -- Guidance for Industry. Federal Register Oct 2022.
- Kahan BC, Morris TP. 2012. Improper analysis of trials randomised using stratified blocks or minimisation. *Stat Med* 31:328-340.
- Liddell FDK. 1983. Simplified exact analysis of case-referent studies; matched pairs; dichotomous exposure. *J Epidemiol Community Health* 37:82-84.
- Lydersen S, Fagerland MW, Laake P. 2009. Recommended tests for association in 2x2 tables. *Stat Med* 28:1159-1175.
- Mehta CR, Senchaudhuri P. 2003. Conditional vs unconditional exact tests for comparing two binomials. (Cytel technical report; widely cited in subsequent literature.)
- Miettinen O, Nurminen M. 1985. Comparative analysis of two rates. *Stat Med* 4:213-226.
- Newcombe RG. 1998a. Interval estimation for the difference between independent proportions: comparison of eleven methods. *Stat Med* 17:873-890.
- Newcombe RG. 1998b. Improved confidence intervals for the difference between binomial proportions based on paired data. *Stat Med* 17:2635-2650.
- Permutt T. 2020. Do covariates change the estimand? *Stat Biopharm Res* 12:45-53.
- Suissa S, Shuster JJ. 1991. The 2x2 matched-pairs trial: exact unconditional design and analysis. *Biometrics* 47:361-372.

## Related Skills

- clinical-biostatistics/effect-measures - Detailed OR/RR/RD with modern CI methods (Wilson, Newcombe, Miettinen-Nurminen)
- clinical-biostatistics/logistic-regression - Regression alternative with covariate adjustment; modified Poisson for RR
- clinical-biostatistics/subgroup-analysis - Stratified analysis with interaction terms and HTE methods
- clinical-biostatistics/multiplicity-graphical - Bretz-Maurer graphical procedures for confirmatory multiplicity
- clinical-biostatistics/trial-reporting - CONSORT 2025 and ICH E9(R1) reporting of categorical analyses
- experimental-design/multiple-testing - General multiple testing correction methods
<!-- END FILE: clinical-biostatistics/categorical-tests/SKILL.md -->

## 子目录：clinical-biostatistics/cdisc-data-handling

<!-- BEGIN FILE: clinical-biostatistics/cdisc-data-handling/SKILL.md -->
---
name: bio-clinical-biostatistics-cdisc-data
description: Reads, validates, and prepares CDISC SDTM and ADaM clinical trial data for analysis. Covers SDTM domain joins (DM, AE, EX, VS, LB, DS), ADaM architecture (ADSL, BDS, OCCDS, ADTTE) with traceability, treatment-emergent AE conventions, baseline derivation, SUPPQUAL/NSV handling, Define-XML 2.1, and Pinnacle 21 / CORE validation. Use when working with clinical trial datasets in CDISC SDTM/ADaM format, preparing analysis-ready data, or validating for regulatory submission.
tool_type: python
primary_tool: pyreadstat
goal_approach_exempt: true
---

## Version Compatibility

Reference examples tested with: pyreadstat 1.2+, pandas 2.1+, numpy 1.26+. CDISC standards referenced: SDTM 2.0 / SDTMIG 3.4 (SDTM 3.0 / SDTMIG 4.0 in public review through April 2026); ADaMIG v1.3 (2021); OCCDS v1.1 (Nov 2021); BDS-for-TTE v1.0; Define-XML 2.1 (FDA-recommended for studies starting on/after March 15, 2023); Dataset-JSON v1.1 (Dec 2024; FDA Federal Register notice April 2025); Pinnacle 21 Community 4.0+; CORE (CDISC Open Rules Engine, 2021). Define-XML 2.1 FDA support began March 15, 2021 and is required for studies starting on/after March 15, 2023.

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- R packages cited (essential for ADaM derivation): admiral (Roche/openpharma), metacore, metatools, xportr

If code throws ImportError, AttributeError, or TypeError, introspect the installed package and adapt the example to match the actual API rather than retrying.

# CDISC SDTM and ADaM Data Handling

**"Load clinical trial data"** -> Parse CDISC SDTM domain files; build or consume ADaM analysis-ready datasets; preserve subject-level and event-level structure; respect traceability and validation expectations for regulatory submission.
- Python: `pyreadstat.read_xport()`, `pd.read_sas()`, `pd.merge()`
- R: `haven::read_xpt()`, `admiral` for ADaM derivation, `Pinnacle21` or `CORE` for validation

## Aggregation Strategy Taxonomy -- Choose the Right Question

| Strategy | Scientific question answered | Example endpoint | Fails when |
|----------|------------------------------|------------------|------------|
| Any event (binary) | Does treatment change probability of experiencing the event at all? | Had any serious AE: Yes/No | Treatment changes event burden but not anyone-event probability |
| Event count | Does treatment change burden of events per patient? | Total AE count per subject | Subjects with 1 vs 10 events treated equivalently |
| Maximum severity | Does treatment shift patients toward more severe manifestations? | Worst AESEV per subject | Confounded with event count (more events -> higher chance of severe) |
| First event + time | Does treatment delay onset of the event? | Time to first serious AE (TTE) | Multiple events per subject ignored |
| Rate (events per person-time) | What is the per-time-unit rate? | AEs per subject-year | Requires exposure-time tracking; differential dropout biases rates |
| Composite (per ICH E9 R1) | Event becomes part of endpoint definition | Death = treatment failure | Direction of components conflict; needs hierarchy |

These are NOT interchangeable. A drug might not change the proportion with AEs (binary: no effect) but increase events per patient (count: harmful). **The choice must be pre-specified in the SAP based on the scientific question, not analytic convenience.**

## Decision Tree by Scenario

| Scenario | Recommended aggregation | Why |
|----------|------------------------|-----|
| Primary safety endpoint, single SAE event | Any event (binary); analyse with logistic | Standard regulatory; cite FDA Safety Reporting Guidance |
| Total adverse-event burden across study | Event count per subject; analyse with Poisson or negative binomial | Captures all events; sandwich SE recommended |
| Toxicity grade comparison across arms | Max severity per subject; ordinal logistic with PO check | Preserves grade ordering; cite Brant test for PO |
| Time-to-first AE (Kaplan-Meier visualisation) | First event + time; censor non-events | See clinical-biostatistics/survival-analysis |
| Rate of exacerbations per patient-year | Rate via negative binomial with offset for exposure time | Standard in COPD/asthma trials |
| Composite endpoint (e.g., MACE) | Component-level definition with hierarchy | Pre-specify per ICH E9(R1) composite strategy |
| Stratification factor extraction | Use STRATA1, STRATA2 from RANDB or DM SUPP | Must appear in analysis (Kahan-Morris 2012) |
| Baseline value derivation | VSBLFL='Y' / LBBLFL='Y'; derive latest pre-dose only if flag missing | Trust SDTM flag when present |

## SDTM vs ADaM -- The Regulatory Layer Cake

| Layer | Standard | Purpose | Granularity | Examples |
|-------|----------|---------|-------------|----------|
| Source CRF | EDC system | Raw data capture | Form/page | Rave, Medidata, Veeva |
| SDTM | SDTM 2.0 / SDTMIG 3.4 | Tabulation; "what happened" | One row per observation | DM, AE, EX, VS, LB, DS |
| ADaM | ADaMIG v1.3 (2021); v3.0 in development | Analysis-ready; "one-PROC-away from CSR table" | Subject (ADSL), parameter-timepoint (BDS), occurrence (OCCDS) | ADSL, ADAE, ADLB, ADTTE, ADRS |
| TLF | Sponsor SAS / R / Python | Tables, listings, figures for CSR | Output | Statistical methods section, demographic table, primary efficacy |

**The ADaM Fundamental Principles (the "ROT" document):**

1. Analysis-ready (one procedure call -> the analysis result)
2. Traceability (every value links back to SDTM via metadata)
3. Clear/unambiguous communication via Define-XML
4. Naming conventions (PARAM, PARAMCD, AVAL, AVALC, BASE, CHG, PCHG, ABLFL, ANL01FL, ...)
5. Structural rules (ADSL one row per subject; BDS one row per subject/parameter/timepoint/analysis flag)

**Postdoc reading:** the ADaM IG v1.3 PDF (cdisc.org), ADaM ROT, FDA Study Data Technical Conformance Guide (current 2024 version), Pinnacle 21 validation rule catalog, PHUSE Connect 2023-2025 conference proceedings.

## SDTM Domain Overview

| Domain | Level | Description | Key Variables |
|--------|-------|-------------|---------------|
| DM | Subject | Demographics (one row per subject) | USUBJID, ARM, ARMCD, ACTARM, ACTARMCD, AGE, SEX, RACE, RFSTDTC, RFXSTDTC, RFENDTC |
| AE | Event | Adverse events (multiple per subject) | USUBJID, AETERM, AEDECOD, AEBODSYS, AESEV, AESER, AESTDTC, AEENDTC |
| EX | Event | Drug exposure/dosing | USUBJID, EXTRT, EXDOSE, EXSTDTC, EXENDTC |
| VS | Event | Vital signs | USUBJID, VSTESTCD, VSSTRESN, VSBLFL, VISIT |
| LB | Event | Lab results | USUBJID, LBTESTCD, LBSTRESN, LBSTRESC, LBORRES, LBBLFL, LBSPEC |
| DS | Event | Disposition | USUBJID, DSDECOD, DSSTDTC |
| SE | Event | Subject elements (treatment epochs) | USUBJID, ETCD, SESTDTC, SEENDTC |
| MH | Event | Medical history | USUBJID, MHDECOD, MHCAT |
| CM | Event | Concomitant medications | USUBJID, CMDECOD, CMSTDTC, CMENDTC |

USUBJID = STUDYID-SITEID-SUBJID is the universal merge key. Subject-level domains (DM) have one row per USUBJID; event-level domains have multiple.

**ARM vs ACTARM:** ARM is planned treatment from randomisation; ACTARM is actual treatment received. **In crossover designs, ARM differs from ACTARM by definition;** in parallel-arm trials, they diverge when subjects are randomised to one arm but receive another (per-protocol violations). Primary analyses use ARM (ITT); safety uses ACTARM.

**RFSTDTC vs RFXSTDTC:** RFSTDTC is "first study activity date" (typically screening start); RFXSTDTC is "first treatment date." For treatment-emergent adverse event (TEAE) calculations, ALWAYS use RFXSTDTC (per ICH E2A) — RFSTDTC includes screening AEs which are not treatment-emergent.

## Reading .xpt Files

```python
import pyreadstat
import pandas as pd

# pyreadstat (recommended -- handles SAS metadata)
dm, meta = pyreadstat.read_xport('dm.xpt')
# meta.column_names, meta.column_labels, meta.variable_value_labels

# pandas built-in (SAS XPORT v5)
dm = pd.read_sas('dm.xpt', format='xport', encoding='utf-8')

# CSV fallback (common in academic datasets)
dm = pd.read_csv('DM.csv')
```

When pyreadstat is available, the metadata object provides column labels, value labels, and format information lost with other readers. **Critical for analysis-dataset derivation:** the metadata carries the controlled-terminology codelist, essential for handling values like AESEV ('MILD'/'MODERATE'/'SEVERE') with semantic ordering.

## SAS XPT v5 vs Dataset-JSON -- The 2025-2026 Transition

**SAS XPT v5** is the current FDA submission format but dates to 1995, with constraints:

- 8-character variable names (so `LBSTRESN` is a max-length name)
- 200-character text values
- No UTF-8 (ASCII only) -> problematic for multilingual trials
- Single dataset per file

**Dataset-JSON v1.1 (CDISC, December 2024; FDA Federal Register notice April 2025)** is the modern replacement. PHUSE-CDISC-FDA pilot has demonstrated drop-in feasibility. FDA adoption timeline pending as of mid-2026; EMA and PMDA exploring in parallel.

**Pragmatic position:** for the next ~2 years, SAS XPT v5 will remain the de facto submission format; sponsors should architect for Dataset-JSON migration but maintain XPT compliance.

## Joining Domains -- The Right Way

```python
import pandas as pd

dm = pd.read_csv('DM.csv')
ae = pd.read_csv('AE.csv')

# WRONG: merging event-level directly onto subject-level inflates rows
# RIGHT: aggregate first, then merge
any_serious = ae.groupby('USUBJID')['AESER'].apply(lambda x: (x == 'Y').any()).reset_index()
any_serious.columns = ['USUBJID', 'HAD_SERIOUS_AE']

analysis = dm.merge(any_serious, on='USUBJID', how='left')
analysis['HAD_SERIOUS_AE'] = analysis['HAD_SERIOUS_AE'].fillna(False)
```

**Always use `how='left'` when merging onto DM** to preserve all randomised subjects, even those with no events. Fill missing event indicators with 0 or False.

### Aggregation strategy must follow the scientific question

| Strategy | Scientific question | Example |
|----------|---------------------|---------|
| Any event (binary) | Does treatment increase probability of experiencing the event at all? | Had any serious AE: yes/no |
| Event count | Does treatment increase event burden per patient? | Total AE count per subject |
| Maximum severity | Does treatment shift toward more severe manifestations? | Worst AESEV per subject |
| First event + time | Does treatment delay onset? | Time to first serious AE |
| Rate (events per person-time) | What is the per-time-unit rate? | AEs per subject-year |

These are NOT interchangeable. A drug might not change the proportion with AEs (binary: no effect) but increase events per patient (count: harmful). The choice must follow the SAP, not analytic convenience.

```python
# Count events per subject
ae_counts = ae.groupby('USUBJID').size().reset_index(name='AE_COUNT')

# Maximum severity per subject (map to numeric first -- string max is unreliable)
severity_map = {'MILD': 1, 'MODERATE': 2, 'SEVERE': 3}
ae['AESEV_NUM'] = ae['AESEV'].map(severity_map)
max_severity = ae.groupby('USUBJID')['AESEV_NUM'].max().reset_index()

# Specific event: COVID-19 adverse event
covid_ae = ae[ae['AEDECOD'] == 'COVID-19']
covid_ae['AESEV_NUM'] = covid_ae['AESEV'].map(severity_map)
had_covid = covid_ae.groupby('USUBJID')['AESEV_NUM'].max().reset_index()
had_covid.columns = ['USUBJID', 'COVID_SEVERITY']

analysis = dm.merge(had_covid, on='USUBJID', how='left')
analysis['HAD_COVID'] = analysis['COVID_SEVERITY'].notna().astype(int)
```

## ADaM Architecture -- The Postdoc Deep Dive

### ADSL (Subject-Level) -- The Spine

**Exactly one row per subject.** Every other ADaM dataset must merge to ADSL on USUBJID. Standard variables:

- **USUBJID** -- universal subject ID
- **TRT01A / TRT01P / ACTARMCD / ARMCD** -- planned and actual treatment, period 1
- **TRTSDT / TRTEDT** -- treatment start/end dates (derived from EX, not SDTM)
- **AGE, SEX, RACE, ETHNIC** -- demographics from DM
- **RANDDT** -- randomisation date
- **DCSREAS / DCSREASP / DCSREASCD** -- discontinuation reason (coded + verbatim)
- **Population flags:** ITTFL, FASFL, SAFFL, PPROTFL, EFFFL (Y/N flags for analysis populations)
- **Stratification factors:** STRATA1, STRATA2 (from randomisation)
- **Baseline covariates** that will be used as model covariates downstream

### BDS (Basic Data Structure) -- Long Format Analysis Data

**One row per subject per parameter per analysis timepoint per analysis flag.** Used for ADVS, ADLB, ADEFF, ADQS, ADTTE.

Required variables:

- **USUBJID, STUDYID** -- merge keys
- **PARAM, PARAMCD, PARAMN** -- parameter name, code, number
- **AVISIT, AVISITN** -- analysis visit name, number
- **ADT, ADY** -- analysis date, analysis day (relative to TRTSDT)
- **AVAL, AVALC** -- analysis value (numeric, character)
- **BASE** -- baseline value (replicated per subject/parameter)
- **CHG, PCHG** -- change from baseline, percent change
- **ABLFL** -- 'Y' for the baseline record
- **ANL01FL, ANL02FL** -- analysis flags for primary/secondary analyses
- **DTYPE** -- derivation type ('LOCF', 'WOCF', 'AVERAGE', 'BOCF', or null for original)
- **BASETYPE** -- when multiple baselines per subject/parameter (crossover)
- **EPOCH** -- study period (SCREENING, TREATMENT, FOLLOW-UP)

```python
# Example: derive ADLB BDS structure from LB SDTM
import pandas as pd

lb = pd.read_csv('LB.csv')
adsl = pd.read_csv('ADSL.csv')

# Filter to active tests
adlb = lb[lb['LBTESTCD'].isin(['ALT', 'AST', 'CREAT', 'HGB'])].copy()
adlb['AVAL'] = adlb['LBSTRESN']
adlb['PARAM'] = adlb['LBTEST']
adlb['PARAMCD'] = adlb['LBTESTCD']

# Merge subject-level treatment from ADSL
adlb = adlb.merge(adsl[['USUBJID', 'TRT01A', 'TRTSDT']], on='USUBJID')

# Compute analysis day
adlb['ADT'] = pd.to_datetime(adlb['LBDTC'], errors='coerce')
adlb['TRTSDT'] = pd.to_datetime(adlb['TRTSDT'], errors='coerce')
adlb['ADY'] = (adlb['ADT'] - adlb['TRTSDT']).dt.days + 1  # Day 1 = first dose

# Set ABLFL from LBBLFL
adlb['ABLFL'] = (adlb['LBBLFL'] == 'Y').map({True: 'Y', False: None})

# Derive BASE per subject/parameter
baselines = adlb[adlb['ABLFL'] == 'Y'][['USUBJID', 'PARAMCD', 'AVAL']]
baselines.columns = ['USUBJID', 'PARAMCD', 'BASE']
adlb = adlb.merge(baselines, on=['USUBJID', 'PARAMCD'], how='left')

# Compute CHG and PCHG
adlb['CHG'] = adlb['AVAL'] - adlb['BASE']
adlb['PCHG'] = 100 * adlb['CHG'] / adlb['BASE']
```

### OCCDS (Occurrence Data Structure) -- One Row per Event

OCCDS v1.1 (Nov 2021) handles AE, CM, MH. Variables: AEDECOD, AEBODSYS, AESEV, AESER, ASTDT (analysis start date), AENDT, TRTEMFL.

**OCCDS v1.1 added TRTEM01FL through TRTEM##FL** for multi-period treatment-emergent flags — essential for crossover and multi-phase studies where a single TRTEMFL is ambiguous.

### ADTTE (Time-to-Event) -- The CNSR Convention Trap

The **ADaM BDS for TTE v1.0** uses BDS structure with extra variables for survival analysis:

- **STARTDT** -- time origin (typically TRTSDT for OS; RANDDT for PFS; response date for DOR)
- **ADT** -- analysis date (event date if event, censoring date if censored)
- **AVAL** = ADT - STARTDT (+1 if "first day = day 1" convention)
- **AVALU** = 'DAYS' (or 'MONTHS' for some endpoints)
- **CNSR** -- censoring indicator. **CONVENTION: CNSR = 0 for events; positive integers for censoring**, integer encodes censoring reason
- **EVNTDESC** -- text description ('Death due to disease', 'Last alive contact')
- **CNSDTDSC, SRCDOM, SRCVAR, SRCSEQ** -- traceability back to SDTM source

**The CNSR convention is OPPOSITE to most statistical packages**, which use 1 = event. R `survival::Surv(time, event)` expects event=1; SAS PROC LIFETEST takes CENSORED= statement that's opposite to CNSR convention. **This is a perpetual bug source.** When passing ADTTE to analysis:

```python
# Convert CDISC ADTTE CNSR to R/Python statistical convention
adtte['event'] = (adtte['CNSR'] == 0).astype(int)  # 1 = event for survival packages
```

### Define-XML 2.1

Every ADaM dataset requires variable-level metadata in Define-XML 2.1 (FDA-required for studies starting on/after March 15, 2023; support began March 15, 2021). Fields per variable:

- **Origin** -- CRF, derived, predecessor SDTM variable
- **Derivation rule** -- free text or controlled algorithm
- **Codelist** -- linked controlled terminology
- **Length, datatype, label**

The FDA reviewer's Analysis Data Reviewer's Guide (ADRG) is now expected in every NDA/BLA — walks reviewer through how each analysis dataset was built.

**Two-level traceability expectation:** SDTM raw -> ADaM analysis-ready, with no orphan derivations. FDA reviewers explicitly trace AE counts in CSR table -> ADAE rows -> AE SDTM rows. Any break is a flag.

## Treatment-Emergent AE -- The Convention Variation

**ICH E2A (1995)** defines an AE generically. **TEAE is sponsor-defined:**

```
TRTEMFL = 'Y' if AE.ASTDT >= TRTSDT AND AE.ASTDT <= TRTEDT + X days
```

X = post-treatment follow-up window. Common values:

- Small molecules: 28 or 30 days
- Biologics with extended half-life: longer (e.g., 60-90 days for mAbs)
- Cell/gene therapy: indefinite (lifelong monitoring expected)

**Sponsor variation:**

- Day-of-first-dose AE included as TEAE (FDA preference) vs excluded (some EMA reviewers)
- Partial-date imputation: impute day 15 if only month/year known, vs censor as missing
- Worsening of pre-existing AE: flagged via SEV change vs requires new PT (preferred term)

**MedDRA SOC/PT hierarchy:** AEs coded to MedDRA Preferred Terms (PT), grouped by System Organ Class (SOC). Clinically related PTs (e.g., 'Diarrhea' / 'Frequent bowel movements' / 'Loose stools') often combined via Standardized MedDRA Queries (SMQs) or sponsor-defined groupings. ADAE typically carries both AEDECOD (PT) and SMQ/group flags.

## Baseline Derivation

**ABLFL = 'Y'** marks the record whose AVAL becomes BASE for all other records of the same subject/parameter.

**Standard rule:** last non-missing assessment on or before first dose (TRTSDT). If protocol mandates a specific baseline visit ('Day 1 pre-dose'), that visit's record is flagged.

```python
# Derive ABLFL when SDTM baseline flag is missing/inconsistent
import pandas as pd

vs['VSDTC_dt'] = pd.to_datetime(vs['VSDTC'], errors='coerce')
vs = vs.merge(adsl[['USUBJID', 'TRTSDT']], on='USUBJID')
vs['is_pre_treatment'] = vs['VSDTC_dt'] <= pd.to_datetime(vs['TRTSDT'])

# Latest pre-treatment value per subject/parameter
baseline_records = (vs[vs['is_pre_treatment'] & vs['VSSTRESN'].notna()]
                    .sort_values('VSDTC_dt')
                    .groupby(['USUBJID', 'VSTESTCD'])
                    .tail(1))
baseline_records['derived_ABLFL'] = 'Y'
```

**Critical detail:** filter on VSBLFL='Y' (or LBBLFL='Y') as the primary source. Only fall back to derivation when the flag is missing. Trust the SDTM flag when present; CRF-level baseline designation embeds clinical judgement the analyst cannot reconstruct.

**BASETYPE** required when more than one baseline exists per subject/parameter (crossover studies, multi-period trials). Distinguishes "Period 1 Baseline" vs "Period 2 Baseline."

**DTYPE** values per CDISC controlled terminology: 'LOCF' (last observation carried forward), 'WOCF' (worst), 'AVERAGE', 'BOCF' (baseline observation carried forward), null for original. **Pinnacle 21 flags any DTYPE value not in CT.**

## SUPPQUAL and the NSV Transition

**SUPPQUAL (supplemental qualifiers)** is the legacy mechanism for sponsor-defined variables that don't fit standard SDTM domain columns. Long-format QNAM/QVAL pairs:

```python
supp = pd.read_sas('suppae.xpt', format='xport', encoding='utf-8')
supp_pivot = supp.pivot_table(
    index='USUBJID', columns='QNAM', values='QVAL', aggfunc='first'
).reset_index()
ae_enriched = ae.merge(supp_pivot, on='USUBJID', how='left')
```

For record-level SUPPQUAL (where IDVAR and IDVARVAL identify specific rows):

```python
supp_record = supp[supp['IDVAR'] == 'AESEQ'].copy()
supp_record['AESEQ'] = supp_record['IDVARVAL'].astype(float)
supp_pivot_record = supp_record.pivot_table(
    index=['USUBJID', 'AESEQ'], columns='QNAM', values='QVAL', aggfunc='first'
).reset_index()
ae_enriched = ae.merge(supp_pivot_record, on=['USUBJID', 'AESEQ'], how='left')
```

**The 2024-2026 SUPP transition:** Therapeutic Area User Guides (TAUGs) increasingly use NS-- domain extensions or **Non-Standard Variables (NSV) Registry**-listed variables directly in the parent domain, instead of QNAM/QVAL pairs in SUPP--. Not a hard deprecation but the direction is clear. The Non-Standard Variables Registry at cdisc.org is the new canonical place to look up sponsor-extension variables.

## Date Handling -- The Partial-Date Reality

```python
dm['RFSTDT'] = pd.to_datetime(dm['RFSTDTC'], errors='coerce')
ae['AESTDT'] = pd.to_datetime(ae['AESTDTC'], errors='coerce')
ae['AEENDT'] = pd.to_datetime(ae['AEENDTC'], errors='coerce')

# Days from randomization to AE onset
ae_with_ref = ae.merge(dm[['USUBJID', 'RFSTDT']], on='USUBJID')
ae_with_ref['AE_ONSET_DAY'] = (ae_with_ref['AESTDT'] - ae_with_ref['RFSTDT']).dt.days
```

**SDTM dates are ISO 8601 strings.** Partial dates (e.g., '2023-03' without day) are common. `errors='coerce'` converts these to NaT rather than raising errors. For analysis requiring complete dates, CDISC conventions impute missing day as the 1st for start dates and the last day of the month for end dates, but imputation rules should match the SAP.

**SDTM records include EPOCH** (SCREENING, TREATMENT, FOLLOW-UP). For TEAEs, filter AEs to onset during or after the treatment epoch. Including pre-treatment AEs confounds the treatment effect estimate.

## Validation -- Pinnacle 21 and CORE

**Pinnacle 21 (Certara, formerly OpenCDISC)** is the de facto FDA submission validation standard. Validates against FDA Validation Rules + CDISC IG conformance + Define-XML schema. Severity tiers:

- **Reject** -- submission will not be accepted
- **Error** -- must justify
- **Warning** -- should investigate

**FDA Validation Rules** are published quarterly by FDA Office of Translational Sciences; Pinnacle 21 wraps these into its rule engine.

**CORE (CDISC Open Rules Engine, 2021)** is a newer open-source alternative using YAML-defined rules from the CDISC Rules Catalog. Gaining traction but not yet at Pinnacle-21 parity for confirmatory submissions.

```bash
# Pinnacle 21 Community (free; appropriate for non-pivotal trials)
p21-community validate --rules sdtmig-3.4 --output-dir validation_output study_data/
```

## Population Flags

| Flag | Source | Purpose |
|------|--------|---------|
| ITTFL | DM all randomised | Primary efficacy population (ICH E9 default) |
| FASFL | ITT minus eligibility failures + no post-baseline | Practical primary (FAS = Full Analysis Set) |
| SAFFL | EX (received at least one dose) | Safety analysis (AE reporting) |
| PPROTFL | SE + DS + protocol-violation list | Per-protocol; sensitivity only |
| EFFFL | Sponsor-defined | Modified ITT variants |

**FAS vs ITT subtlety:** FAS may exclude post-randomisation subjects (ineligibility, no post-baseline efficacy); ITT cannot. Many SAPs equate them; FDA may insist on stricter ITT at submission. Pre-specify both with explicit FAS exclusion criteria in the protocol.

## Missing Data Considerations -- The Clinical Reasoning Layer

Before any imputation/complete-case decision, **examine the DS (Disposition) domain to tabulate reasons for discontinuation by treatment arm.** If discontinuation rates or reasons differ between arms, missing data is likely informative (MNAR) and standard MMRM-MAR is questionable.

```python
ds = pd.read_csv('DS.csv')
dropouts = ds[ds['DSDECOD'] != 'COMPLETED']
dropouts_by_arm = dropouts.merge(adsl[['USUBJID', 'ARM']], on='USUBJID')
discontinuation_reasons = dropouts_by_arm.groupby(['ARM', 'DSDECOD']).size().unstack(fill_value=0)
```

This is the data-quality precursor to choosing the estimand strategy in trial-reporting (see ICH E9(R1)) — missing patterns informed by DS drive the choice between treatment-policy, hypothetical, or composite ICE strategies.

## Common Pitfalls

| Pitfall | Symptom | Solution |
|---------|---------|----------|
| Event-level merged onto subject-level without aggregation | Row count inflates after merge | Aggregate first, then merge |
| First chronological record used as baseline | Misclassified baseline | Filter on VSBLFL='Y' / LBBLFL='Y'; derive only if missing |
| Character (xxORRES) used for analysis | Inconsistent numeric coercion | Use xxSTRESN (numeric standardised); missing xxSTRESN with present xxORRES means 'NOT DONE' or '<LLOQ' |
| ARM used in safety analysis | Crossover or actual-treatment differs | Use ACTARM for safety; ARM for ITT efficacy |
| RFSTDTC used as TEAE reference | Includes screening AEs | Use RFXSTDTC (first treatment); cite ICH E2A |
| ADTTE CNSR confused with stat-pkg convention | Wrong event/censoring assignment | CDISC: CNSR=0 means event; convert: `event = (CNSR == 0).astype(int)` |
| Partial date parsing error | NaT in date column | `pd.to_datetime(..., errors='coerce')` |
| SUPPQUAL granularity confusion | Wrong rows merged | Check IDVAR before choosing subject vs record-level merge |
| Non-standard column names treated as standard SDTM | Missing variables | Inspect actual columns; map to semantic roles |
| Pinnacle 21 not run before submission | FDA reject | Always validate against current SDTMIG and FDA Validation Rules before submission |

### Common non-standard column mappings

| Standard SDTM | Common alternatives | Role |
|---------------|--------------------|------|
| ARM / ARMCD | TRTGRP, TRT01P, treatment, group | Treatment assignment |
| AEDECOD | AEPT, ae_term, preferred_term | AE preferred term |
| AESEV (text) | AESEV (numeric 1-4), severity, AETOXGR | Severity / toxicity grade |
| USUBJID | SUBJID, subject_id, patient_id | Subject identifier |
| RFXSTDTC | trt_start, first_dose_date | First treatment date |
| LBSTRESN | lab_value_num, result_numeric | Lab numeric result |

## Quantitative Thresholds and Conventions

| Threshold/Convention | Source | Rationale |
|----------------------|--------|-----------|
| TEAE window: 28-30 days post-treatment for small molecules | ICH E2A; sponsor convention | Mode of action, half-life inform window |
| RFXSTDTC for TEAE reference (not RFSTDTC) | ICH E2A | RFSTDTC includes screening; TEAE is post-treatment |
| ABLFL='Y' for last non-missing pre-dose | CDISC ADaM IG v1.3 | Standard baseline definition; trust SDTM flag |
| ARM (planned) for ITT efficacy; ACTARM for safety | ICH E9 | Crossover/PP-violation handling |
| Pinnacle 21 validation before submission | FDA Study Data Technical Conformance Guide | Standard quality gate; reject errors block acceptance |
| Define-XML 2.1 for studies starting >=March 15, 2023 | FDA Study Data Standards Catalog | Older 2.0 still accepted for prior studies |
| Dataset-JSON v1.1 (Dec 2024; FDA notice April 2025) | CDISC + FDA Federal Register | Modern replacement for XPT v5; timeline pending |
| CNSR=0 for events, positive integers for censoring | ADaM BDS-for-TTE v1.0 | OPPOSITE of R `survival` and most stat packages |

## Anticipated Reviewer Pushback

| Pushback | Response |
|----------|----------|
| "RFXSTDTC or RFSTDTC for TEAE?" | RFXSTDTC per ICH E2A; RFSTDTC would include screening AEs |
| "Baseline from VSBLFL or derived?" | VSBLFL when present; documented derivation rule when missing |
| "Pinnacle 21 errors?" | All errors resolved or justified; warnings reviewed and documented |
| "Define-XML 2.1 ADRG provided?" | Yes — analysis dataset traceability documented to variable level |
| "ITT vs FAS reconciliation?" | Pre-specified in protocol with explicit FAS exclusion criteria |
| "OCCDS v1.1 multi-period flags?" | TRTEM01FL...TRTEM##FL pre-specified for crossover periods |
| "ADTTE CNSR convention conversion documented?" | Explicit: CDISC CNSR=0 means event; convert to event=1 for downstream R/Python |

## References

- CDISC. 2021. Analysis Data Model Implementation Guide (ADaMIG) v1.3.
- CDISC. 2021. Occurrence Data Structure (OCCDS) v1.1.
- CDISC. 2012. ADaM Basic Data Structure for Time-to-Event Analyses v1.0.
- CDISC. 2024. Dataset-JSON v1.1.
- FDA. 2024. Study Data Technical Conformance Guide.
- FDA Federal Register Notice. April 2025. Dataset-JSON Pilot Comment Request.
- ICH. 1995. E2A: Clinical Safety Data Management -- Definitions and Standards for Expedited Reporting.
- ICH. 1998. E9: Statistical Principles for Clinical Trials.
- ICH. 2019. E9(R1) Addendum on Estimands and Sensitivity Analysis.
- Pinnacle 21 (Certara). 2024. Community Edition Validation Rules.
- PHUSE/CDISC. 2024. Dataset-JSON Pilot Reports.

## Related Skills

- clinical-biostatistics/logistic-regression - Model binary outcomes from prepared ADaM/SDTM data
- clinical-biostatistics/trial-reporting - Use prepared analysis datasets for ICH E9(R1) estimands and CONSORT 2025 reporting
- clinical-biostatistics/missing-data-sensitivity - DS-domain reasoning informs estimand choice
- clinical-biostatistics/survival-analysis - ADTTE CNSR convention; time-to-event preparation
- expression-matrix/metadata-joins - General metadata joining patterns
<!-- END FILE: clinical-biostatistics/cdisc-data-handling/SKILL.md -->

## 子目录：clinical-biostatistics/effect-measures

<!-- BEGIN FILE: clinical-biostatistics/effect-measures/SKILL.md -->
---
name: bio-clinical-biostatistics-effect-measures
description: Computes and interprets treatment effect measures (OR, RR, RD, HR, NNT) with calibrated confidence intervals (Wilson, Newcombe, Miettinen-Nurminen, MOVER, profile likelihood, Bender NNT) and reports marginal vs conditional estimands per FDA 2023 covariate adjustment guidance. Use when reporting treatment effects in confirmatory trials, comparing effect sizes across studies, or constructing forest plots.
tool_type: python
primary_tool: statsmodels
---

## Version Compatibility

Reference examples tested with: statsmodels 0.14+, numpy 1.26+, pandas 2.1+, matplotlib 3.8+, marginaleffects (Python) 0.0.13+ / (R) 0.20+. R packages cited: ratesci, exact2x2, marginaleffects, riskCommunicator, RobinCar.

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- R: `packageVersion('<pkg>')` then `?function_name`

If code throws ImportError, AttributeError, or TypeError, introspect the installed package and adapt the example to match the actual API rather than retrying.

# Treatment Effect Measures for Clinical Trials

**"Compute treatment effect sizes"** -> Estimate the population-level treatment contrast (OR, RR, RD, HR, NNT) with a confidence interval calibrated to sample size and a clear declaration of whether the estimand is marginal or conditional under ICH E9(R1).

## Algorithmic Taxonomy

| Measure | Scale | Collapsible? | Best CI method | When to use | Fails when |
|---------|-------|--------------|----------------|-------------|------------|
| OR | Log-odds ratio | NO (non-collapsible) | Profile likelihood; Wald acceptable for n>100 per arm | Case-control (only valid measure); logistic regression default | Outcome prevalence > 10% (OR overstates RR); Hauck-Donner pathology near boundary |
| RR | Log-risk ratio | YES | Miettinen-Nurminen score; MOVER-R | Cohort, RCT with common outcomes | Sparse strata; one or both p near 0 (Wald log-RR breaks) |
| RD (absolute risk difference) | Linear probability | YES | Newcombe-Wilson hybrid; Miettinen-Nurminen | Clinically interpretable absolute scale; FDA-preferred for binary | Predictions outside [0,1] from linear models |
| HR (hazard ratio) | Log-hazard ratio | NO | Wald with profile likelihood for small n | Time-to-event with PH | PH violation (see clinical-biostatistics/survival-analysis) |
| NNT/NNH | 1/RD | n/a (derived from RD) | Bender 2001 *CCT* 22:102 (Altman 1998 base) | Communicating absolute benefit to clinicians | RD CI crosses zero (NNT becomes NNTB-infinity-NNTH) |
| Difference in RMST | Time scale | YES | Wald with delta method; pseudo-observation regression | Time-to-event with PH violation | Different max follow-up across arms (truncation tau ambiguous) |

**Postdoc reading:** Permutt 2020 *Stat Biopharm Res* 12:45 ("Do covariates change the estimand?") established that the conditional OR from a multivariable logistic regression is a *different parameter* than the marginal OR -- and the FDA May 2023 Final Guidance "Adjusting for Covariates in RCTs" requires the **marginal** estimand for primary reporting (see clinical-biostatistics/logistic-regression for g-computation/standardisation machinery).

## Decision Tree by Scenario

| Scenario | Recommended estimand + CI | Why |
|----------|---------------------------|-----|
| RCT, binary outcome, prevalence <10% | OR with Wald CI; report as primary | OR ~= RR at low prevalence; standard regulatory currency |
| RCT, binary outcome, prevalence >=10% | RR or RD via modified Poisson with HC1/HC3 sandwich SE; OR as secondary | OR substantially overstates RR; modified Poisson directly estimates RR (Zou 2004 *AJE* 159:702) |
| RCT, binary outcome, primary endpoint per FDA 2023 | Marginal RD via g-computation with sandwich SE; conditional OR as supportive | FDA 2023 final guidance: marginal estimand for primary; cite Permutt 2020 |
| Case-control study | OR only (RR unidentifiable); profile likelihood CI | OR is the only measure estimable from case-control design |
| Noninferiority on absolute scale | Miettinen-Nurminen score CI for RD | Regulatory standard for RD CIs; consistent with Pearson chi-square |
| Noninferiority on relative scale | Miettinen-Nurminen score CI for RR; Koopman 1984 acceptable | Wald log-RR has poor coverage near boundary; MN is the regulatory expectation |
| Stratified design with site/region strata | MH pooled OR with stratified MN CI (R `ratesci::scoreci(..., stratified=TRUE)`) | Preserves stratification; cite Kahan-Morris 2012 |
| Reporting NNT for clinicians | Bender 2001 *CCT* 22:102 method; report as NNTB(lower)..infinity..NNTH(upper) when CI crosses zero | Standard in BMJ/Lancet/Cochrane |
| Time-to-event with PH violation | RMST difference; cite Royston-Parmar 2013, Uno 2014 | HR is a misleading single-number summary under non-PH (see survival-analysis) |

## Crude Effect Measures from 2x2 Tables

**Goal:** Compute unadjusted OR, RR, RD from a contingency table with calibrated CIs.

**Approach:** Use Table2x2 for OR/RR with Wald CIs, but switch to score-based methods (Miettinen-Nurminen, Newcombe-Wilson) for regulatory contexts.

```python
from statsmodels.stats.contingency_tables import Table2x2
from statsmodels.stats.proportion import confint_proportions_2indep
import numpy as np

# Table layout: [[treated_event, treated_no_event], [control_event, control_no_event]]
table = np.array([[a, b], [c, d]])
t = Table2x2(table)
print('OR:', t.oddsratio, t.oddsratio_confint())        # Wald log-OR CI
print('RR:', t.riskratio, t.riskratio_confint())         # Wald log-RR CI

# Modern CI for RD (regulatory preferred):
ci_rd = confint_proportions_2indep(a, a+b, c, c+d, method='newcomb', alpha=0.05)
# 'newcomb' = Newcombe-Wilson hybrid; 'agresti-caffo' is the +1+1 +1+1 adjustment
# For Miettinen-Nurminen stratified CIs, use R `ratesci::scoreci`
```

**Table orientation is critical:** Table2x2 interprets the first column as "outcome present." `pd.crosstab` orders columns alphabetically; if outcome is coded 0/1, the table will have 0 first and the OR will be the *reciprocal* of intended. Always reorder: `cross = cross[[1, 0]]` or `cross = cross[['Yes', 'No']]`. This is a silent direction-reversing error.

**For the underlying significance test of a 2x2:** Pearson chi-square (no Yates) at n>=40 with adequate expected counts; otherwise Boschloo's exact (uniformly more powerful than Fisher's exact at the same Type-I per Mehta-Senchaudhuri 2003; Lydersen-Fagerland-Laake 2009). See clinical-biostatistics/categorical-tests for the algorithmic taxonomy.

## Modern Confidence Intervals -- the Postdoc Toolkit

Wald CIs are the textbook default but have well-documented coverage failures (Brown-Cai-DasGupta 2001 *Stat Sci* 16:101 -- "chaotic" coverage near 0 and 1 even with moderate n; Newcombe 1998a *Stat Med* 17:873 documents 11 alternatives for the difference of two proportions).

### Single proportion

| Method | When | Status |
|--------|------|--------|
| Wald | Never preferred | Defunct for serious work; coverage can drop to 0.0 (Brown-Cai-DasGupta) |
| Wilson (score) | General default | Brown-Cai-DasGupta recommended; matches Pearson chi-square test |
| Jeffreys (Beta(1/2,1/2)) | Small n | Equal-tailed Jeffreys; Bayesian with reference prior; recommended for small n |
| Clopper-Pearson | When exact guarantee required | Over-covers by 1-4 percentage points; sometimes regulatory-required |
| Agresti-Coull | Simple Wald replacement | +2/+2 adjustment; teaching default |
| Mid-p Clopper-Pearson | When CP over-coverage hurts NI margin | Less conservative than CP; slight under-coverage |

```python
from statsmodels.stats.proportion import proportion_confint
ci = proportion_confint(45, 60, alpha=0.05, method='wilson')
# Other methods: 'jeffreys', 'agresti_coull', 'beta' (Clopper-Pearson), 'normal' (Wald)
```

### Difference of two proportions (RD)

| Method | Citation | Verdict |
|--------|----------|---------|
| Wald | textbook | Poor; can produce limits outside [-1,1] |
| Newcombe-Wilson hybrid / MOVER | Newcombe 1998a | Recommended; balanced of computational simplicity and coverage |
| Agresti-Caffo (+1+1, +1+1) | Agresti-Caffo 2000 *Am Stat* 54:280 | Add 1 success + 1 failure per arm, then Wald; surprisingly good for small n |
| Miettinen-Nurminen score | Miettinen-Nurminen 1985 *Stat Med* 4:213 | **Regulatory standard for RD**; consistent with Pearson chi-square; SAS PROC FREQ `riskdiff(method=mn)` |
| Chan-Zhang exact unconditional | Chan-Zhang 1999 *Biometrics* 55:1202 | Guaranteed coverage; needed when MN under-covers near extreme p |

### Ratio of two proportions (RR)

| Method | Citation | Verdict |
|--------|----------|---------|
| Wald on log(RR) ("Katz log") | textbook (Katz 1978) | Defunct for serious work; biased when either p small |
| Koopman 1984 score | *Biometrics* 40:513 | Iterative; original score CI for RR |
| Miettinen-Nurminen score | Miettinen-Nurminen 1985 | Regulatory standard; R `ratesci::scoreci(contrast='RR')` |
| MOVER-R | Donner-Zou 2012 *Stat Methods Med Res* 21:347 | Construct CI on theta1 - R*theta2 not on R directly; allows asymmetric CIs |

### Odds ratio

| Method | Citation | Verdict |
|--------|----------|---------|
| Wald on log(OR) | textbook | Fast; suffers Hauck-Donner effect when cell counts small |
| Cornfield exact | Cornfield 1956 | Exact reference standard; often over-conservative |
| Mid-p Cornfield | Berry-Armitage 1995 *Statistician* 44:417 | Less conservative; slight under-coverage |
| Profile likelihood | Venzon-Moolgavkar 1988 *Appl Stat* 37:87 | **Transformation-invariant; no Hauck-Donner pathology**; R `MASS::confint.glm` default for `glm` |

**Hauck-Donner effect (1977 *JASA* 72:851; revived by Yee 2022 *JASA* 117:1763):** the Wald test statistic is *non-monotonic* in the parameter estimate near the boundary -- a large OR can produce a tiny Wald chi-square so the test fails to reject when it should. Use LR or profile-likelihood inference. `VGAM::hdeff()` detects this in fitted models.

## Number Needed to Treat (NNT) -- the Bender 2001 *CCT* 22:102 Way

**Goal:** Convert RD to clinically intuitive NNT with a CI that handles the singularity at RD = 0.

**Approach:** Compute RD CI first, then transform; when RD CI crosses zero, report NNTB(lower) -> infinity -> NNTH(upper).

```python
import numpy as np

def nnt_with_ci(treated_events, treated_n, control_events, control_n, alpha=0.05):
    """Bender 2001 *CCT* 22:102 method; transforms RD CI to NNT CI handling singularity."""
    p_t = treated_events / treated_n
    p_c = control_events / control_n
    rd = p_c - p_t   # positive = treatment helps
    se_rd = np.sqrt(p_t * (1 - p_t) / treated_n + p_c * (1 - p_c) / control_n)
    z = 1.96 if alpha == 0.05 else None
    rd_ci = (rd - z * se_rd, rd + z * se_rd)

    nnt = 1 / rd if rd != 0 else float('inf')
    if rd_ci[0] > 0 and rd_ci[1] > 0:
        return f'NNTB {1/rd_ci[1]:.0f} to {1/rd_ci[0]:.0f}'
    elif rd_ci[0] < 0 and rd_ci[1] < 0:
        return f'NNTH {1/-rd_ci[1]:.0f} to {1/-rd_ci[0]:.0f}'
    else:
        # CI crosses zero -- Bender convention
        if rd > 0:
            return f'NNTB {nnt:.0f} (NNTB {1/rd_ci[1]:.0f} to inf to NNTH {1/-rd_ci[0]:.0f})'
        return f'NNTH {-nnt:.0f} (similar split)'
```

**Bender 2001 *Controlled Clinical Trials* 22:102-110** resolves the discontinuity at RD = 0: NNT has a singularity there, so a CI that crosses zero produces a disjoint NNT CI ("NNTB(some) -> infinity -> NNTH(some)"). The Cochrane/BMJ convention is to report exactly this -- the infinity in the middle signals non-significance and is more honest than truncating to one side.

**NNT from OR + baseline risk** (when only the OR is published):

```python
def nnt_from_or(odds_ratio, baseline_risk):
    baseline_odds = baseline_risk / (1 - baseline_risk)
    treatment_odds = baseline_odds * odds_ratio
    treatment_risk = treatment_odds / (1 + treatment_odds)
    arr = abs(baseline_risk - treatment_risk)
    return 1 / arr if arr > 0 else float('inf')
```

| OR | Baseline 5% | Baseline 20% | Baseline 50% |
|----|-------------|--------------|--------------|
| 0.5 | NNT=42 | NNT=12 | NNT=6 |
| 0.7 | NNT=70 | NNT=20 | NNT=12 |

**Always report baseline risk alongside NNT** -- the same OR produces dramatically different NNTs.

## Marginal RD via G-Computation -- The FDA 2023 Recipe

**Goal:** Compute the marginal RD (FDA 2023 primary estimand for binary endpoints) from a fitted logistic regression -- without requiring the analyst to switch model class.

**Approach:** Standardise over the observed covariate distribution. Predict per-subject probability under treatment=1 AND under treatment=0; take the mean of each; the difference is the marginal RD. SE via influence function or bootstrap.

```python
import statsmodels.formula.api as smf
import numpy as np

# Step 1: Fit logistic with covariates
fit = smf.logit('y ~ z + x1 + x2 + x3', data=df).fit()

# Step 2: Predict under each treatment regime (counterfactual prediction)
df_z1 = df.assign(z=1)
df_z0 = df.assign(z=0)
p_z1 = fit.predict(df_z1)
p_z0 = fit.predict(df_z0)

# Step 3: Marginal estimates
marg_p1 = p_z1.mean()
marg_p0 = p_z0.mean()
marg_rd = marg_p1 - marg_p0          # FDA 2023 primary
marg_rr = marg_p1 / marg_p0
marg_or = (marg_p1 / (1 - marg_p1)) / (marg_p0 / (1 - marg_p0))

# Step 4: SE via bootstrap (or analytical influence function in R `marginaleffects`)
n_boot = 1000
boot_rds = np.zeros(n_boot)
rng = np.random.default_rng(42)
for b in range(n_boot):
    idx = rng.choice(len(df), size=len(df), replace=True)
    fit_b = smf.logit('y ~ z + x1 + x2 + x3', data=df.iloc[idx]).fit(disp=0)
    p1_b = fit_b.predict(df_z1.iloc[idx]).mean()
    p0_b = fit_b.predict(df_z0.iloc[idx]).mean()
    boot_rds[b] = p1_b - p0_b

se_marg_rd = boot_rds.std(ddof=1)
ci_marg_rd = (marg_rd - 1.96*se_marg_rd, marg_rd + 1.96*se_marg_rd)
```

**R equivalent (preferred for confirmatory):**

```r
library(marginaleffects)
fit <- glm(y ~ z + x1 + x2 + x3, family = binomial, data = df)
avg_comparisons(fit, variables = 'z', vcov = 'HC3')
# Returns marginal RD with HC3 sandwich SE; CIs; deltamethod_inference
```

**Tsiatis et al 2008 robustness guarantee:** under randomisation Z ⊥ X, the g-computation marginal estimator is consistent for marginal ATE EVEN IF the outcome model is misspecified. Efficiency depends on model quality; consistency does not. This is why FDA 2023 accepts marginal RD via g-computation without requiring proof of correct logistic mean structure.

## Marginal vs Conditional Effects -- The Core ICH E9(R1) Question

For logistic regression, the maximum-likelihood coefficient on Z in `glm(Y ~ Z + X, family=binomial)` is the **conditional log odds ratio** -- the OR comparing Z=1 to Z=0 *holding X fixed*. Because the OR is non-collapsible, this is *different* from the marginal log OR even under perfect randomisation. Gail, Wieand & Piantadosi 1984 (*Biometrika* 71:431) first showed that treatment-effect estimates from nonlinear models are biased for the marginal effect when prognostic covariates are omitted, even under randomisation; this non-collapsibility is what FDA 2023 addresses by targeting a marginal estimand.

```python
# Conditional OR (the default; biased toward null vs marginal OR)
import statsmodels.formula.api as smf
import numpy as np

model = smf.logit('y ~ z + x1 + x2', data=df).fit()
cond_or = np.exp(model.params['z'])

# Marginal RD via g-computation / standardisation:
df_z1, df_z0 = df.assign(z=1), df.assign(z=0)
p_z1 = model.predict(df_z1).mean()
p_z0 = model.predict(df_z0).mean()
marg_rd = p_z1 - p_z0
marg_rr = p_z1 / p_z0
marg_or = (p_z1 / (1-p_z1)) / (p_z0 / (1-p_z0))

# Variance via influence function or bootstrap (RobinCar / marginaleffects)
# R: marginaleffects::avg_comparisons(model, variables='z', vcov='HC3')
```

**The reporting standard post-FDA-2023:** marginal estimand as primary (RD with HC3 sandwich SE), conditional as supportive. The two are different parameters, not different estimates of the same parameter. See clinical-biostatistics/logistic-regression for full g-computation machinery and Tsiatis et al 2008 *Stat Med* 27:4658.

### Non-collapsibility -- the standard explanation

A conditional (adjusted) OR typically differs from the marginal (unadjusted) OR even WITHOUT confounding. Conditioning on a prognostic covariate (one that predicts outcome but is unrelated to treatment) changes the OR by a mathematical property -- not bias. In most settings, the conditional OR is *further from the null* than the marginal OR. **This is what postdocs argue about:** Frank Harrell argues conditional effects are more clinically meaningful (they apply to individuals); FDA via Permutt argues marginal effects are what regulatory submissions need (the population-level decision). FDA 2023 settles it for regulatory reporting: marginal primary, conditional supportive.

**Risk ratios and risk differences are collapsible.** Marginal and conditional RR/RD are equal absent confounding. This is why FDA 2023 favours RD as the primary estimand for binary outcomes -- the conditional vs marginal distinction disappears.

## Reconciliation: When Methods Disagree

| Pattern | Likely cause | Action |
|---------|--------------|--------|
| Conditional OR (from adjusted logistic) > marginal OR (from g-computation) | Non-collapsibility (Permutt 2020); adjusted ORs further from null than marginal under most covariate structures | Report marginal RD as primary per FDA 2023; conditional OR as supportive with explicit parameter label |
| Wald CI excludes null but Wilson/Newcombe-Wilson CI overlaps null | Wald has poor coverage near 0 and 1 (Brown-Cai-DasGupta 2001) | Wilson for single proportion; Newcombe-Wilson hybrid or Miettinen-Nurminen for differences; cite as regulatory standard |
| Crude OR vs stratified MH-OR differ substantially | Confounding by stratification factor OR non-collapsibility OR effect modification | If RCT with stratified randomisation, use stratified analysis (Kahan-Morris 2012); if observational, investigate confounding via stratum-specific OR forest plot |
| OR vs RR direction agree but magnitudes differ greatly | Outcome prevalence > 10% (OR overstates RR at high baseline risk) | Use modified Poisson (Zou 2004) for direct RR estimation; report both for transparency |
| NNT from one trial vs another differs despite similar OR | Baseline risk differs across trials (NNT = 1/ARR depends on baseline) | Always report NNT alongside baseline risk; cite Bender 2001 *CCT* 22:102 for NNTB-inf-NNTH convention |
| Profile-likelihood CI differs from Wald CI in small-cell scenario | Hauck-Donner effect (Wald non-monotone near boundary; Yee 2022) | Use profile likelihood (R `MASS::confint.glm`); detect via `VGAM::hdeff()` |
| RMST difference and HR give different conclusions on treatment benefit | HR is time-averaged log-HR under PH violation; RMST captures cumulative benefit | Under PH violation, RMST is the more interpretable summary; see clinical-biostatistics/survival-analysis |

## Modified Poisson Regression for Common Outcomes

When prevalence > 10% and the policy quantity is RR (not OR), modified Poisson with sandwich SE directly estimates the RR (Zou 2004 *AJE* 159:702):

```python
import statsmodels.api as sm
import numpy as np

poisson_model = sm.GLM(df['outcome'],
                       sm.add_constant(df[['treatment', 'age']]),
                       family=sm.families.Poisson()).fit(cov_type='HC1')
rr_estimates = np.exp(poisson_model.params)
rr_ci = np.exp(poisson_model.conf_int())
```

`cov_type='HC1'` (Huber-White sandwich) corrects the over-dispersion that Poisson assumes; without it, SEs are wrong because binary data are NOT Poisson. Use HC3 (jackknife approximation) for n < 250 (Long-Ervin 2000 *Am Stat* 54:217). HC1 is the Stata default; HC3 is the R `sandwich` package default -- the difference can flip noninferiority p-values for n < 200.

## Forest Plots

```python
import matplotlib.pyplot as plt
import numpy as np

def forest_plot(labels, effects, lower_cis, upper_cis, ref_line=1.0, figsize=(8, 6), log_scale=True):
    fig, ax = plt.subplots(figsize=figsize)
    y_pos = range(len(labels))
    ax.errorbar(effects, y_pos,
                xerr=[np.array(effects) - np.array(lower_cis),
                      np.array(upper_cis) - np.array(effects)],
                fmt='D', color='black', capsize=3, markersize=5)
    ax.axvline(x=ref_line, color='gray', linestyle='--', linewidth=0.8)
    ax.set_yticks(list(y_pos))
    ax.set_yticklabels(labels)
    ax.set_xlabel('Effect estimate (95% CI)')
    if log_scale:
        ax.set_xscale('log')
    plt.tight_layout()
    return fig
```

Log scale ensures reciprocal effects (OR 0.5 and OR 2.0) appear equidistant from the null. For RD or RMST difference, use a linear scale.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| Prevalence > 10% -> prefer RR over OR | Zhang-Yu 1998 *JAMA* 280:1690 | OR overstates RR materially; modified Poisson or log-binomial recovers RR directly |
| n > 100 per arm for Wald CI on log-OR | Brown-Cai-DasGupta 2001; Newcombe 1998a | Below this, Wald coverage is poor; profile likelihood or score-based preferred |
| HC1 (Stata default) vs HC3 (R default) for small n | Long-Ervin 2000 *Am Stat* 54:217 | HC3 (jackknife approximation) recommended for n <=250; difference can flip NI p-values |
| Marginal estimand for primary regulatory report | FDA 2023 Final Guidance | Marginal RD/RR/OR via g-computation; conditional OR is a different parameter (Permutt 2020) |
| Miettinen-Nurminen CI for RR/RD | Miettinen-Nurminen 1985; FDA/EMA NI margin practice | Regulatory standard; consistent with Pearson chi-square |
| Bender NNT convention | Bender 2001 *Controlled Clinical Trials* 22:102-110; Cochrane/BMJ style | When RD CI crosses zero, NNT CI is disjoint; report NNTB(lower) -> inf -> NNTH(upper) |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| Adjusted OR much larger than unadjusted | Non-collapsibility, not confounding | Cite Permutt 2020; report both with explicit estimand labels (conditional vs marginal) |
| NNT reported as "NNT=25, CI 12 to -200" | Sign-confused output when RD CI crosses zero | Use Bender 2001 *CCT* 22:102 convention: "NNTB 25 (NNTB 12 to inf to NNTH 200)" |
| OR reported without baseline risk for clinical translation | Common in published papers | Always report event rates per arm alongside OR; provide NNT at observed baseline |
| `Table2x2` returns reciprocal OR | Column ordering puts outcome=0 first | Reorder: `crosstab[[1, 0]]` |
| Poisson SE much smaller than expected | Forgot `cov_type='HC1'` or 'HC3' | Always specify sandwich SE for modified Poisson; without it, SEs are wrong |
| Wald log-RR CI extends below 0 or implausibly | Katz log RR fails for small p | Switch to Miettinen-Nurminen or Koopman score; R `ratesci::scoreci(contrast='RR')` |
| Hauck-Donner: huge OR with non-significant Wald p | Wald non-monotonic near boundary | Use profile likelihood: R `MASS::confint.glm`; detect with `VGAM::hdeff()` |
| "Adjusted" model gives smaller effect than expected | Mediator adjustment | Check causal DAG; adjusting for mediators attenuates effect toward null |

## Anticipated Reviewer Pushback

| Pushback | Response |
|----------|----------|
| "Is the OR collapsible across the included covariates?" | No -- OR is non-collapsible. Cite Permutt 2020. Report marginal RD via g-computation as primary per FDA 2023. |
| "Why MN over Wald CI?" | Wald has poor coverage for sparse 2x2; MN matches Pearson chi-square test and is the FDA/EMA standard for NI margins. |
| "Hauck-Donner pathology check?" | For small cell counts: switch to profile likelihood CI (R `MASS::confint.glm`); cite Yee 2022 *JASA* 117:1763. |
| "Why HC3 over HC1?" | n <=250 favours HC3 per Long-Ervin 2000; HC1 (Stata) and HC3 (R sandwich) can disagree at small n. |
| "Where is the marginal effect?" | Per FDA 2023, marginal RD/RR via g-computation is the primary estimand for binary outcomes; conditional is supportive. |
| "Why NNT in 'NNTB-infinity-NNTH' notation?" | Bender 2001 *CCT* 22:102 convention; standard in BMJ/Lancet/Cochrane. Disjoint CI honestly conveys non-significance. |
| "Adjustment for stratification factors?" | Strata included in modified Poisson or in MN stratified CI via `ratesci::scoreci(stratified=TRUE)`; ignoring is over-conservative -- SE biased upward, power loss (Kahan-Morris 2012). |
| "What about effect modification across subgroups?" | Pooled estimate reported as primary; stratum-specific ORs in forest plot; Breslow-Day test for homogeneity; if heterogeneous, do not pool -- see clinical-biostatistics/subgroup-analysis. |
| "Post-hoc subgroup OR was significant -- can a claim be made?" | Not credible without pre-specification per EMA 2019 / CONSORT 2025; frame as hypothesis-generating; replicate in independent cohort before claiming. |

## References

- Agresti A, Caffo B. 2000. Simple and effective confidence intervals for proportions and differences of proportions. *Am Stat* 54:280-288.
- Altman DG. 1998. Confidence intervals for the number needed to treat. *BMJ* 317:1309.
- Bender R. 2001. Calculating confidence intervals for the number needed to treat. *Controlled Clinical Trials* 22:102-110.
- Brown LD, Cai TT, DasGupta A. 2001. Interval estimation for a binomial proportion. *Stat Sci* 16:101-117.
- Chan ISF, Zhang Z. 1999. Test-based exact confidence intervals for the difference of two binomial proportions. *Biometrics* 55:1202-1209.
- Cornfield J. 1956. A statistical problem arising from retrospective studies. *3rd Berkeley Symp* 4:135-148.
- Donner A, Zou GY. 2012. Closed-form confidence intervals for functions of the normal mean and standard deviation. *Stat Methods Med Res* 21:347-359.
- FDA. 2023. Adjusting for Covariates in Randomized Clinical Trials. Final Guidance, May 2023.
- Hauck WW, Donner A. 1977. Wald's test as applied to hypotheses in logit analysis. *JASA* 72:851-853.
- Katz D, Baptista J, Azen SP, Pike MC. 1978. Obtaining confidence intervals for the risk ratio in cohort studies. *Biometrics* 34:469-474.
- Koopman PAR. 1984. Confidence intervals for the ratio of two binomial proportions. *Biometrics* 40:513-517.
- Long JS, Ervin LH. 2000. Using heteroscedasticity consistent standard errors in the linear regression model. *Am Stat* 54:217-224.
- Miettinen O, Nurminen M. 1985. Comparative analysis of two rates. *Stat Med* 4:213-226.
- Newcombe RG. 1998a. Interval estimation for the difference between independent proportions: comparison of eleven methods. *Stat Med* 17:873-890.
- Permutt T. 2020. Do covariates change the estimand? *Stat Biopharm Res* 12:45-53.
- Royston P, Parmar MKB. 2013. Restricted mean survival time. *BMC Med Res Methodol* 13:152.
- Tsiatis AA, Davidian M, Zhang M, Lu X. 2008. Covariate adjustment for two-sample treatment comparisons in randomized clinical trials. *Stat Med* 27:4658-4677.
- Venzon DJ, Moolgavkar SH. 1988. A method for computing profile-likelihood-based confidence intervals. *Appl Stat* 37:87-94.
- Yee TW. 2022. On the Hauck-Donner effect in Wald tests: detection, tipping points, and parameter space characterization. *JASA* 117:1763-1774.
- Zou G. 2004. A modified Poisson regression approach to prospective studies with binary data. *AJE* 159:702-706.

## Related Skills

- clinical-biostatistics/categorical-tests - 2x2 testing infrastructure that produces ORs/RRs/RDs
- clinical-biostatistics/logistic-regression - Adjusted ORs, g-computation, modified Poisson for marginal RR
- clinical-biostatistics/subgroup-analysis - Forest plots and stratified effect estimates
- clinical-biostatistics/survival-analysis - HR, RMST, hazard-free alternatives for time-to-event
- clinical-biostatistics/trial-reporting - CONSORT 2025 and ICH E9(R1) effect reporting
- clinical-biostatistics/missing-data-sensitivity - Effect measure CIs under MI pooling (Rubin's rules)
<!-- END FILE: clinical-biostatistics/effect-measures/SKILL.md -->

## 子目录：clinical-biostatistics/logistic-regression

<!-- BEGIN FILE: clinical-biostatistics/logistic-regression/SKILL.md -->
---
name: bio-clinical-biostatistics-logistic-regression
description: Performs logistic regression for clinical trial outcomes (binary, ordinal, multinomial) with marginal-vs-conditional estimand reporting per FDA 2023 covariate adjustment guidance, g-computation/standardisation for marginal effects, modified Poisson for RR, Brant test for proportional odds, Firth penalty for separation, and Hauck-Donner detection. Use when modeling binary or ordinal endpoints in confirmatory or exploratory clinical trials.
tool_type: python
primary_tool: statsmodels
---

## Version Compatibility

Reference examples tested with: statsmodels 0.14+, scipy 1.12+, numpy 1.26+, pandas 2.1+, firthmodels 0.3+, marginaleffects 0.0.13+ (Python) / 0.20+ (R). R packages cited: RobinCar, marginaleffects, brant, MASS, VGAM.

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- R: `packageVersion('<pkg>')` then `?function_name`

If code throws ImportError, AttributeError, or TypeError, introspect the installed package and adapt the example to match the actual API rather than retrying.

# Logistic Regression for Clinical Outcomes

**"Model clinical outcomes with logistic regression"** -> Estimate the marginal or conditional treatment effect on a binary or ordinal endpoint using a model that respects randomisation stratification, declares its estimand, and survives covariate misspecification.

**Conditional vs marginal (the non-collapsibility subtlety):** the OR is non-collapsible. The conditional OR from logistic regression is a *different parameter* than the marginal OR, even when there is NO confounding and randomisation is perfect. This is mathematical, not statistical bias. FDA 2023 favours marginal RD (via g-computation) for primary reporting to avoid parameter ambiguity. See clinical-biostatistics/effect-measures and Permutt 2020.

## Algorithmic Taxonomy

| Approach | Estimand | Inference | Strength | Fails when |
|----------|----------|-----------|----------|------------|
| Unadjusted logistic / chi-square | Marginal OR | Wald or LR | Simple; transparent | Loses efficiency vs adjusted (Senn 2013); inflates SE under stratified randomisation (Kahan-Morris 2012) |
| Logistic with covariates (ML, Wald CI) | **Conditional** log-OR | Wald | Standard; widely available | Conditional OR != marginal OR due to non-collapsibility (Permutt 2020); not the FDA 2023 primary estimand |
| Logistic + g-computation / standardisation | **Marginal** RD/RR/OR | Influence function or bootstrap SE | FDA 2023 recommended primary estimand for binary | Requires correct outcome model AND post-fit standardisation; needs robust SE machinery |
| Targeted Maximum Likelihood (TMLE) | Marginal RD/RR/OR | Influence function | Provably efficient; doubly robust in observational | Implementation heavier; mostly R (`tmle`, `tmle3`); rare in confirmatory submissions |
| Modified Poisson with sandwich SE | Marginal RR | HC1/HC3 sandwich | Direct RR estimation when prevalence >10% | Slightly less efficient than log-binomial when log-binomial converges |
| Log-binomial regression | Marginal RR | Wald | Direct RR estimation | Frequent convergence failure when predicted risk near 1 |
| Firth penalised logistic | Conditional OR (penalised) | Penalised LR test preferred | Handles separation, rare events (<5% prevalence) | Wald CI/p liberal; must use PLR test (Heinze-Schemper 2002) |
| Ordinal logistic (proportional odds) | Common conditional OR across cut-points | Wald or LR | Preserves ordering information | Proportional odds assumption violation (Brant test) |
| Partial proportional odds | PO holds for some covariates, not others | Hybrid | Salvages ordinal model when PO fails for one predictor | Increased complexity; harder interpretation |
| Multinomial logistic | Per-category log-OR | Wald | No PO assumption needed | Loses efficiency; harder communication |

**Postdoc reading list:** Permutt 2020 *Stat Biopharm Res* 12:45 (conditional vs marginal estimand); FDA May 2023 Final Guidance "Adjusting for Covariates in RCTs" (the regulatory rulebook); Tsiatis et al 2008 *Stat Med* 27:4658 (robust ANCOVA framework); Senn 2013 *Stat Med* 32:1439 (precision from adjustment even under perfect balance); Kahan-Morris 2012 *Stat Med* 31:328 (must adjust for stratification factors).

## Decision Tree by Scenario

| Scenario | Recommended approach | Why |
|----------|---------------------|-----|
| RCT, binary primary endpoint, no covariate adjustment in SAP | Unadjusted logistic with marginal OR; chi-square supportive | Simple regulatory case; consider whether covariate adjustment would gain power (Senn 2013) |
| RCT, binary primary, covariates pre-specified, FDA 2023 compliant | **Logistic adjusted + g-computation for marginal RD**; conditional OR supportive | FDA 2023 final: marginal estimand for primary; mention HC3 sandwich SE |
| RCT, stratified randomisation (sex/region/severity) | Include strata as covariates in logistic; the analytic decision is non-optional | Kahan-Morris 2012: ignoring strata is over-conservative -- SE biased upward, CIs too wide, power loss |
| Common outcome (prevalence >10%) where RR is the policy quantity | Modified Poisson + HC1/HC3 OR log-binomial regression | Avoid OR misinterpretation; Zou 2004; cite EMA 2015 on covariate adjustment |
| Rare event (<5% prevalence) or separation observed | Firth penalty + penalised LR test for p-value | Heinze-Schemper 2002; Wald p from Firth is liberal |
| Ordinal outcome, PO assumption supportable | Proportional odds; verify with Brant test (R `brant::brant`) | Most efficient when PO holds; common in toxicity grading and PROs |
| Ordinal outcome, PO fails on one or two predictors | Partial PO model (R `VGAM::vglm(..., cumulative(parallel=FALSE~X))`) | Salvages most efficiency; only the offending coefficient gets per-cut-point estimate |
| Ordinal outcome, PO fails widely | Multinomial logistic | Worst case; loses ordering info but valid |
| Single arm observational with strong confounding | Logistic adjusted + g-computation + propensity weighting | Doubly robust; cite Hernan-Robins; consider TMLE |
| Binary endpoint, longitudinal repeated measures | GEE or generalised linear mixed model | Sandwich SE for GEE; mixed-model OR is subject-specific not marginal |

## Standard Workflow

**Goal:** Fit a covariate-adjusted logistic regression for a binary clinical endpoint with explicit reference category and pre-specified covariates.

**Approach:** Use the formula API for automatic categorical handling and explicit reference; report both the conditional log-OR and the marginal RD via g-computation.

```python
import statsmodels.formula.api as smf
import pandas as pd
import numpy as np

# CRITICAL: set reference category explicitly. statsmodels default is alphabetical,
# so 'Active' sorts before 'Placebo' and the OR direction silently flips.
model = smf.logit(
    'outcome ~ C(ARM, Treatment(reference="Placebo")) + age + C(sex) + baseline_score',
    data=df
).fit()

# Conditional ORs (Wald)
or_table = pd.DataFrame({
    'OR': np.exp(model.params),
    'Lower_CI': np.exp(model.conf_int()[0]),
    'Upper_CI': np.exp(model.conf_int()[1]),
    'p_value': model.pvalues
})

# Marginal RD via g-computation (the FDA 2023-recommended primary estimand):
df_active = df.assign(ARM='Active')
df_placebo = df.assign(ARM='Placebo')
risk_active = model.predict(df_active).mean()
risk_placebo = model.predict(df_placebo).mean()
marginal_rd = risk_active - risk_placebo
# For SE, use influence-function or bootstrap; see RobinCar / marginaleffects in R
```

**The reference-category trap is the single most common silent bug.** `smf.logit('y ~ C(ARM)')` uses alphabetical ordering, so `ARM='Active'` becomes 1 and `ARM='Placebo'` becomes 0 -- but with `ARM=['Active','Placebo','Control']`, 'Active' is the reference and 'Placebo' is the comparison. Always pass `Treatment(reference="Placebo")` or equivalent. R `glm(y ~ relevel(ARM, ref='Placebo'))`.

## Marginal vs Conditional Estimand -- The FDA 2023 Pivot

**The single most important methodological shift in clinical biostatistics 2020-2025.** Permutt 2020 established and FDA 2023 codified: the maximum-likelihood coefficient on Z in `glm(Y ~ Z + X, family=binomial)` is the **conditional log-OR** -- the OR comparing Z=1 to Z=0 holding X fixed. Due to OR non-collapsibility, this is a *different parameter* than the **marginal log-OR** (the OR comparing the entire treated population to the entire control population), even under perfect randomisation.

**The FDA 2023 final guidance** ("Adjusting for Covariates in Randomized Clinical Trials," May 2023) endorses covariate-adjusted nonlinear-model analysis *provided the analyst targets a marginal estimand*. Reporting the conditional OR from a multivariable logistic regression as "the treatment effect" silently changes the estimand from what was pre-specified.

### G-computation / Standardisation

```python
# Marginal effects on three scales via g-computation:
df_z1 = df.assign(ARM='Active')
df_z0 = df.assign(ARM='Placebo')
p_z1 = model.predict(df_z1)
p_z0 = model.predict(df_z0)

marg_p1 = p_z1.mean()
marg_p0 = p_z0.mean()
marg_rd = marg_p1 - marg_p0
marg_rr = marg_p1 / marg_p0
marg_or = (marg_p1 / (1 - marg_p1)) / (marg_p0 / (1 - marg_p0))
```

**For valid SE:** the delta-method/influence-function variance and HC3 sandwich are required. Python `marginaleffects` v0.0.13+ implements this via `marginaleffects.avg_comparisons(model, variables='ARM', vcov='HC3')`. R is more mature: `marginaleffects::avg_comparisons` (Arel-Bundock-Greifer-Heiss 2024 *JSS* 111:9), `RobinCar` (purpose-built for FDA 2023), `riskCommunicator`.

**Tsiatis et al 2008 robustness guarantee:** under randomisation Z ⊥ X, the g-computation marginal estimator is *consistent* for the marginal ATE even if the outcome model is misspecified. Efficiency depends on model quality; consistency does not. This is why FDA 2023 accepts the marginal RD via g-computation without requiring proof of correct logistic mean structure.

**Reporting template (post-FDA-2023):**

> "Primary estimand: marginal risk difference of -8.5 percentage points (95% CI -12.7 to -4.2, HC3 SE), computed by g-computation/standardisation from a logistic regression adjusted for age, sex, and baseline severity. Supportive: conditional OR 0.48 (95% CI 0.34-0.67, Wald) from the same model."

## Modified Poisson for Common Outcomes -- Direct RR

When prevalence > 10% and the policy quantity is RR (not OR), modified Poisson with sandwich SE is the de facto modern standard (Zou 2004 *AJE* 159:702):

```python
import statsmodels.api as sm
import numpy as np

X = sm.add_constant(df[['treatment', 'age', 'baseline_score']])
poisson_model = sm.GLM(df['outcome'], X, family=sm.families.Poisson()).fit(cov_type='HC1')
rr = np.exp(poisson_model.params)
rr_ci = np.exp(poisson_model.conf_int())
```

`cov_type='HC1'` corrects the over-dispersion that Poisson inherently assumes. Without it the variance is wrong because binary data are NOT Poisson. For n < 250, HC3 is preferred (Long-Ervin 2000). **What postdocs argue about:** modified Poisson vs log-binomial -- log-binomial directly models RR but frequently fails to converge when predicted risk approaches 1; modified Poisson always converges but is marginally less efficient when log-binomial works.

## Proportional Odds and Brant Test

**Proportional odds (PO)** assumption: the effect of each predictor is constant across all cut-points of the ordinal outcome. Must be tested or the model parameters are invalid.

```python
from statsmodels.miscmodels.ordinal_model import OrderedModel
from statsmodels.api import MNLogit
import pandas as pd

df['severity'] = pd.Categorical(df['severity'], categories=['mild', 'moderate', 'severe'], ordered=True)

po_model = OrderedModel.from_formula('severity ~ treatment + age', data=df, distr='logit').fit(method='bfgs', disp=0)
mn_model = MNLogit.from_formula('severity ~ treatment + age', data=df).fit(disp=0)

# LR test for PO vs MN (omnibus)
lr_stat = 2 * (mn_model.llf - po_model.llf)
lr_df = mn_model.df_model - po_model.df_model
from scipy.stats import chi2
lr_p = 1 - chi2.cdf(lr_stat, lr_df)

# Per-coefficient Brant test in R: brant::brant(po_model_object)
# The Brant test localises which predictor(s) violate PO -- essential before deciding on partial PO
```

**The omnibus LR test is necessary but not sufficient.** Brant test (Brant 1990 *Biometrics* 46:1171; R `brant::brant`) provides per-coefficient PO tests, identifying *which* predictor violates PO. If only one or two predictors violate PO, fit a **partial proportional odds model** (R `VGAM::vglm(..., cumulative(parallel=FALSE~X1+X2))`) rather than abandoning the model entirely.

**OrderedModel intercept gotcha:** do NOT add an intercept term. Threshold parameters (cut-points between ordinal levels) replace the intercept. An explicit constant causes non-identifiability and optimiser failure.

## Separation and Firth Penalty

**Detection:**

```python
from firthmodels import FirthLogisticRegression, detect_separation
import numpy as np

sep_result = detect_separation(X, y)
if sep_result.separation:
    print(sep_result.summary())
# Manual signs: coefficient > 10, SE > 100, convergence warnings
```

**Firth penalty (Firth 1993 *Biometrika* 80:27):**

```python
firth = FirthLogisticRegression()
firth.fit(X, y)
or_firth = np.exp(firth.coef_)

# IMPORTANT: Wald p-values from Firth are LIBERAL (anti-conservative).
# Prefer the penalised likelihood-ratio test (PLRT).
# Some Python `firthlogist` releases expose a PLRT attribute (e.g. `pvalues_lrt_`)
# but its presence and name vary by release -- check `dir(firth)` against the
# installed version, otherwise compute the PLRT manually from the penalised
# log-likelihoods of nested models.
```

**Heinze-Schemper 2002 *Stat Med* 21:2409** showed Wald inference from Firth is **liberal** (anti-conservative); the penalised likelihood-ratio test (PLRT) is the recommended inference. PLRT attributes (e.g. `pvalues_lrt_`) appear in some Python Firth packages but the exact attribute name varies by release -- introspect the installed package; compute the PLRT manually if no attribute is exposed:

```python
def penalised_lrt(firth_full, firth_reduced):
    # Compute 2 * (penalised log-lik full - penalised log-lik reduced) ~ chi-square_df
    pass  # implementation depends on package version; see Heinze-Schemper 2002
```

Firth's method was originally designed for finite-sample bias reduction, not separation per se -- it adds the Jeffreys prior penalty to the likelihood, keeping coefficients finite under separation as a side effect. Also recommended for rare events (<5% prevalence) where ML bias is non-negligible.

## Hauck-Donner Effect Detection

**The Hauck-Donner effect (1977 *JASA* 72:851; revived by Yee 2022 *JASA* 117:1763):** the Wald test statistic is non-monotonic in the parameter estimate near the boundary. A large log-OR can produce a small Wald chi-square -- so the Wald test fails to reject when LR/profile-likelihood would. Common in small samples with strong predictors.

```python
# In R, detect with VGAM::hdeff() and replace Wald with profile likelihood:
# MASS::confint.glm(model) returns profile-likelihood CIs as default
# Python equivalent: bootstrap or manual profile likelihood
```

**When to suspect Hauck-Donner:** large coefficient magnitude with non-significant Wald p; large SE with finite estimate; switching from Wald to LR test changes significance. The fix is always: switch to profile likelihood or LR inference.

## Reconciliation: When Methods Disagree

| Pattern | Likely cause | Action |
|---------|--------------|--------|
| Conditional OR from logistic vs marginal RD from g-computation give different conclusions | Non-collapsibility (OR is non-collapsible; RD is collapsible) | Report marginal RD as primary per FDA 2023; conditional OR as supportive with explicit parameter label; cite Permutt 2020 |
| ML logistic diverges (large coefficient, huge SE); Firth penalised converges | Complete or quasi-complete separation in covariate-outcome relationship | Firth penalty with penalised LR test (NOT Wald p-values); cite Heinze-Schemper 2002 |
| Modified Poisson and log-binomial give different RR estimates | Log-binomial convergence fragility when predicted risk approaches 1 | Modified Poisson with sandwich SE preferred for robust convergence; cite Zou 2004 |
| Proportional-odds (cumulative logit) and multinomial give different inferences | PO assumption violated for one or more predictors (Brant test rejects) | Localise via Brant test; if 1-2 predictors violate, partial-PO model in VGAM; if widely, multinomial |
| Adjusted vs unadjusted treatment effect differ substantially | Confounding (in observational) OR non-collapsibility (in RCT) | In RCT, non-collapsibility expected (Permutt 2020); in observational, investigate confounding via DAG |
| Large OR with non-significant Wald p-value | Hauck-Donner effect: Wald non-monotone near boundary (Yee 2022) | Use profile-likelihood CI (R `MASS::confint.glm`); detect via `VGAM::hdeff()` |
| Stratified analysis significant; unstratified not | Achieved SE smaller in stratified analysis | Include stratification factors in primary model (Kahan-Morris 2012); ignoring biases the SE upward and loses power (over-conservative) |
| Significant treatment effect on conditional model vanishes when mediator included | Adjusting for post-treatment variable on causal pathway | Never adjust for mediators in primary; use causal DAG to distinguish confounder vs mediator |

## Per-Method Failure Modes

### Reference-category silent reversal

- **Trigger:** Treatment variable coded as character with `Active` and `Placebo`; reference not explicitly set.
- **Mechanism:** statsmodels defaults to alphabetical ordering; 'Active' becomes the reference.
- **Symptom:** OR for "ARM[T.Placebo]" appears in output; direction is the opposite of intended.
- **Fix:** Always pass `C(ARM, Treatment(reference="Placebo"))` or numeric encoding with explicit comment.

### Adjusting for a mediator

- **Trigger:** Including a post-randomisation variable that lies on the causal pathway.
- **Mechanism:** Adjustment blocks the causal effect, attenuating treatment effect estimate toward null.
- **Symptom:** Significant unadjusted effect becomes non-significant after adjustment for "mechanism" variable (e.g., inflammation marker).
- **Fix:** Use causal DAG to distinguish confounder from mediator; never adjust for post-treatment variables in the primary analysis. See ICH E9(R1).

### Hauck-Donner non-monotonicity

- **Trigger:** Small samples, strong predictor, cell counts approaching zero.
- **Mechanism:** Wald test statistic is non-monotone in the parameter near the boundary.
- **Symptom:** Large OR magnitude with non-significant Wald p; switching to LR test changes significance.
- **Fix:** Use profile likelihood (R `MASS::confint.glm`) or LR inference; detect with `VGAM::hdeff()`.

### Complete or quasi-complete separation

- **Trigger:** A predictor perfectly predicts outcome in a subset of the data.
- **Mechanism:** Likelihood is monotone in that coefficient; ML estimate diverges to infinity.
- **Symptom:** Coefficient >10, SE >100, convergence warning; convergence message says "fitted probabilities numerically 0 or 1."
- **Fix:** Firth penalty (`firthmodels`); inference via penalised LR test, not Wald.

### Proportional odds violation undetected

- **Trigger:** Ordinal outcome fit with cumulative-logit (PO) model without testing assumption.
- **Mechanism:** PO assumes a constant effect across cut-points; violation invalidates model parameters.
- **Symptom:** Brant test rejects PO for one or more predictors; per-cut-point effects in a saturated model diverge.
- **Fix:** Brant test first; if PO fails on one predictor, partial PO model; if widely fails, multinomial logistic.

### Stratified randomisation not in analysis

- **Trigger:** Stratification by site/region/severity at randomisation; analysis ignores strata.
- **Mechanism:** Achieved SE smaller than calculated SE because randomisation removed between-stratum variability.
- **Symptom:** Over-conservative inference -- SE biased upward, CIs too wide, Type-I error below nominal, and power loss (Kahan-Morris 2012).
- **Fix:** Include stratification factors as covariates in the logistic; this is non-optional per ICH E9, FDA 2023, EMA 2015.

## Model Diagnostics

| Diagnostic | Method | Threshold | Caveat |
|-----------|--------|-----------|--------|
| Discrimination | ROC-AUC (`sklearn.metrics.roc_auc_score`) | >0.7 acceptable, >0.8 good | Trial-level, not patient-individual; depends on outcome prevalence |
| Calibration -- primary | Calibration plot (observed vs predicted in deciles) | Curve along the diagonal | Visual; preferred over H-L |
| Calibration -- secondary | Hosmer-Lemeshow chi-square | p > 0.05 | Low power n<200; oversensitive n>2000 |
| Pseudo R-squared | model.prsquared (McFadden) | >0.2 excellent | NOT comparable to OLS R-squared |
| Events per variable | n_events / n_covariates | >=10 EPV (Peduzzi 1996) | Below this: bias, overfitting; consider Firth |

### Hosmer-Lemeshow

```python
from scipy.stats import chi2
import pandas as pd

def hosmer_lemeshow(y_true, y_pred, n_groups=10):
    df_hl = pd.DataFrame({'y': y_true, 'prob': y_pred})
    df_hl['group'] = pd.qcut(df_hl['prob'], n_groups, duplicates='drop')
    grouped = df_hl.groupby('group').agg(obs=('y', 'sum'), n=('y', 'count'), pred=('prob', 'mean'))
    grouped['expected'] = grouped['n'] * grouped['pred']
    hl_stat = (((grouped['obs'] - grouped['expected']) ** 2) /
               (grouped['n'] * grouped['pred'] * (1 - grouped['pred']))).sum()
    actual_groups = len(grouped)
    return hl_stat, 1 - chi2.cdf(hl_stat, actual_groups - 2)
```

**H-L is supplementary, not primary:** Hosmer-Lemeshow has low power n<200 (rarely rejects even for poor calibration) and oversensitive n>2000 (rejects for trivial miscalibration). The decile choice is also arbitrary -- `pd.qcut(..., duplicates='drop')` can reduce the actual number of groups when probabilities tie, changing df. Use calibration plots (smoothed observed vs predicted) as primary; Hosmer-Lemeshow as supplementary p-value.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| 10 events per variable (EPV) | Peduzzi et al 1996 *J Clin Epidemiol* 49:1373 | Below this, coefficient bias and CI mis-coverage |
| Prevalence > 10% -> prefer marginal RR via modified Poisson | Zou 2004 *AJE* 159:702 | OR overstates RR; modified Poisson directly estimates RR |
| Marginal estimand for primary regulatory analysis | FDA 2023 Final Guidance | Conditional OR is a different parameter than marginal (Permutt 2020) |
| Brant test for PO assumption | Brant 1990 *Biometrics* 46:1171 | Omnibus LR test misses per-coefficient violations |
| Firth penalty with penalised LR test, not Wald | Heinze-Schemper 2002 *Stat Med* 21:2409 | Wald is liberal under Firth penalty |
| HC3 sandwich SE for n <=250 | Long-Ervin 2000 *Am Stat* 54:217 | HC1 (Stata default) anti-conservative in small samples |
| Stratification factors in analysis when used in randomisation | Kahan-Morris 2012 *Stat Med* 31:328 | Ignoring biases SE upward -- CIs too wide, power loss (over-conservative) |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| OR direction opposite of expected | Alphabetical reference; 'Active' sorts before 'Placebo' | `C(ARM, Treatment(reference="Placebo"))` always |
| Conditional and marginal OR differ substantially | Non-collapsibility, not confounding | Cite Permutt 2020; report both with explicit labels |
| Treatment effect vanishes after adjustment | Adjusted for a mediator (post-treatment variable) | Causal DAG check; never adjust for post-treatment in primary |
| Huge coefficient, huge SE, non-significant Wald | Separation OR Hauck-Donner | Detect separation: `firthmodels.detect_separation`; switch to Firth + PLRT |
| H-L p > 0.5 with obvious miscalibration | Low power at n<200 | Use calibration plot as primary; H-L supplementary |
| H-L p < 0.001 with great-looking plot | Oversensitive at n>2000 | Use calibration plot; cite Steyerberg 2019 for cautions |
| `OrderedModel` fails to converge with intercept | Threshold parameters replace intercept | Drop the explicit constant |
| `firth.pvalues_` looks too low | Wald p from Firth is liberal | Inspect the installed Firth package for a PLRT attribute (e.g. `pvalues_lrt_`); compute PLRT manually if none is exposed |
| GLM(family=Binomial) and Logit give same point but different output | `sm.Logit` provides `pred_table()`, `prsquared`; `sm.GLM` does not | Use Logit unless changing link functions |
| Robust SE not reported for modified Poisson | Missing `cov_type='HC1'` or 'HC3' | Always specify sandwich SE for modified Poisson |

## Anticipated Reviewer Pushback

| Pushback | Response |
|----------|----------|
| "Why is the marginal RD different from the conditional OR's implied RD?" | Non-collapsibility of OR; cite Permutt 2020 and FDA 2023. Marginal RD via g-computation is the primary per FDA 2023. |
| "Adjustment for stratification factors?" | Pre-specified strata included in the model. Cite Kahan-Morris 2012 and ICH E9. |
| "How were covariates chosen?" | Pre-specified in the SAP based on prior literature/clinical knowledge. No data-driven selection (which would inflate Type-I). |
| "Why not use stepwise selection?" | Stepwise leaks signal from the outcome and inflates Type-I. Pre-specification is the regulatory norm; cite FDA 2023. |
| "PH check for the longitudinal binary?" | Binary doesn't have PH; if longitudinal, used GEE with sandwich SE or GLMM; see ICH E9 estimand for treatment policy. |
| "Why Firth not standard logistic?" | Separation detected (or rare events <5%); standard ML diverges; Firth penalty + PLRT recommended (Heinze-Schemper 2002). |
| "Brant test result?" | PO holds for predictors X1, X2, X3; PO fails for X4 -> partial PO model fit per VGAM. |
| "Calibration?" | Calibration plot in supplement; H-L p reported as supplementary, not primary. |

## References

- Arel-Bundock V, Greifer N, Heiss A. 2024. How to interpret statistical models using marginaleffects in R and Python. *J Stat Softw* 111:9.
- Brant R. 1990. Assessing proportionality in the proportional odds model for ordinal logistic regression. *Biometrics* 46:1171-1178.
- FDA. 2023. Adjusting for Covariates in Randomized Clinical Trials for Drugs and Biological Products. Final Guidance, May 2023.
- Firth D. 1993. Bias reduction of maximum likelihood estimates. *Biometrika* 80:27-38.
- Hauck WW, Donner A. 1977. Wald's test as applied to hypotheses in logit analysis. *JASA* 72:851-853.
- Heinze G, Schemper M. 2002. A solution to the problem of separation in logistic regression. *Stat Med* 21:2409-2419.
- Kahan BC, Morris TP. 2012. Improper analysis of trials randomised using stratified blocks or minimisation. *Stat Med* 31:328-340.
- Lin DY, Wei LJ. 1989. The robust inference for the Cox proportional hazards model. *JASA* 84:1074-1078.
- Long JS, Ervin LH. 2000. Using heteroscedasticity consistent standard errors in the linear regression model. *Am Stat* 54:217-224.
- Moore KL, van der Laan MJ. 2009. Covariate adjustment in randomized trials with binary outcomes: TMLE. *Stat Med* 28:39-64.
- Peduzzi P, Concato J, Kemper E, Holford TR, Feinstein AR. 1996. A simulation study of the number of events per variable in logistic regression analysis. *J Clin Epidemiol* 49:1373-1379.
- Permutt T. 2020. Do covariates change the estimand? *Stat Biopharm Res* 12:45-53.
- Senn S. 2013. Seven myths of randomisation in clinical trials. *Stat Med* 32:1439-1450.
- Steyerberg EW. 2019. *Clinical Prediction Models* (2nd ed). Springer.
- Tsiatis AA, Davidian M, Zhang M, Lu X. 2008. Covariate adjustment for two-sample treatment comparisons in randomized clinical trials. *Stat Med* 27:4658-4677.
- Wang B, Susukida R, Mojtabai R, Amin-Esmaeili M, Rosenblum M. 2023. Model-robust inference for clinical trials that improve precision by stratified randomization and covariate adjustment. *JASA* 118:1152-1163.
- Yee TW. 2022. On the Hauck-Donner effect in Wald tests. *JASA* 117:1763-1774.
- Zou G. 2004. A modified Poisson regression approach to prospective studies with binary data. *AJE* 159:702-706.

## Related Skills

- clinical-biostatistics/cdisc-data-handling - Prepare analysis datasets from CDISC SDTM/ADaM domains
- clinical-biostatistics/effect-measures - Modern CI methods; marginal vs conditional in depth
- clinical-biostatistics/categorical-tests - Chi-square and Fisher alternatives for unadjusted tests
- clinical-biostatistics/subgroup-analysis - Interaction terms and HTE detection
- clinical-biostatistics/survival-analysis - Cox regression for time-to-event analogues
- clinical-biostatistics/multiplicity-graphical - Bretz-Maurer graphs for multiple endpoints from one logistic model
- clinical-biostatistics/trial-reporting - CONSORT 2025 and ICH E9(R1) reporting of logistic analyses
<!-- END FILE: clinical-biostatistics/logistic-regression/SKILL.md -->

## 子目录：clinical-biostatistics/missing-data-sensitivity

<!-- BEGIN FILE: clinical-biostatistics/missing-data-sensitivity/SKILL.md -->
---
name: bio-clinical-biostatistics-missing-data
description: Implements missing-data sensitivity analyses for confirmatory clinical trials including MMRM under MAR (with Kenward-Roger correction), reference-based multiple imputation (J2R, CR, CIR, LMCF per Carpenter-Roger 2013), Permutt delta-adjustment / tipping-point analysis, pattern-mixture identifying restrictions (CCMV, NCMV, ACMV), and the Cro vs Bartlett variance debate. Use when handling missing primary or secondary endpoint data in regulatory submissions following NRC 2010 and ICH E9(R1).
tool_type: mixed
primary_tool: rbmi
---

## Version Compatibility

Reference examples tested with: R `mmrm` 0.3+ (Roche/openpharma), R `rbmi` 1.5+ (Roche/Bayer via insightsengineering), R `mice` 3.16+, R `mitools` 2.4+, Python `sklearn` 1.4+, `statsmodels` 0.14+.

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('<pkg>')` then `?function_name`
- Python: `pip show <package>` then `help(module.function)`

If code throws ImportError, AttributeError, or TypeError, introspect the installed package and adapt the example to match the actual API rather than retrying.

# Missing Data Sensitivity for Confirmatory Trials

**"Handle missing data in a confirmatory clinical trial"** -> Pre-specify the missing-data assumption per ICH E9(R1); execute the primary analysis under the chosen assumption (typically MAR via MMRM or MI); run clinically-articulable MNAR sensitivity analyses (reference-based MI per Carpenter-Roger 2013); report the tipping delta that would overturn the conclusion (Permutt 2016).

## The Foundation -- NRC 2010 and ICH E9(R1)

**The U.S. National Research Council Panel** ("The Prevention and Treatment of Missing Data in Clinical Trials," 2010; chaired by Roderick Little; Little, D'Agostino, Cohen et al 2012 *NEJM* 367:1355): 18 recommendations grouped as prevention (Recs 1-7), analysis (Recs 8-14), sensitivity (Recs 15-18).

Key recommendations:

- **Rec 10:** explicitly REJECT LOCF and BOCF as default; they are biased even under MCAR
- **Rec 13:** endorses WGEE (weighted GEE) for marginal estimands
- **Rec 15:** "examining sensitivity to assumptions about the missing-data mechanism should be a mandatory component of reporting"

**ICH E9(R1) (2019)** forces the ordering: define the estimand (5 attributes including ICE strategy) BEFORE choosing the analysis. The missing-data strategy maps to the ICE handling strategy:

- **Treatment policy** ICE strategy + missing post-ICE data -> reference-based MI (J2R typical)
- **Hypothetical** ICE strategy -> MMRM under MAR; g-computation
- **Composite** ICE strategy -> ICE becomes part of endpoint; no missing-data problem for that subject
- **While-on-treatment** ICE strategy -> pre-ICE values only; censored at ICE
- **Principal stratum** -> latent stratum, requires Bayesian or sensitivity over unverifiable assumptions

## Missing-Data Mechanisms

| Mechanism | Definition | Testable? | Valid method |
|-----------|------------|-----------|--------------|
| MCAR | Independent of all data | Partially (Little's 1988 test) | Complete-case unbiased but loses power |
| MAR | Depends on observed data only | NOT testable | MMRM under MAR; MI under MAR |
| MNAR | Depends on unobserved values | NOT testable | Sensitivity analysis (J2R, CR, CIR, tipping point, pattern-mixture, selection model) |

**Critical philosophical point: MAR vs MNAR cannot be distinguished from observed data alone.** This is fundamental. Pre-specify the assumed mechanism in the SAP based on clinical reasoning, not the data.

## Algorithmic Taxonomy

| Method | Estimand strategy | Identification | Variance | Strength | Fails when |
|--------|-------------------|----------------|----------|----------|------------|
| Complete-case analysis | MAR or MCAR | MAR | Standard | Simple; valid under MCAR | Loses power; biased under MAR with informative covariates |
| LOCF | Implicit MNAR | Assumes flat post-ICE trajectory | Standard | Historically used | Biased even under MCAR (Mallinckrodt 2008); NRC 2010 rejects |
| MMRM with UN+KR | Hypothetical via MAR | MAR | Kenward-Roger SE | FDA-favoured continuous longitudinal | High differential dropout makes MAR implausible |
| Multiple imputation (MAR) | Hypothetical via MAR | MAR | Rubin's rules | Flexible; handles arbitrary patterns | sample_posterior must be enabled; only works with default estimator in sklearn |
| Reference-based MI (J2R, CR, CIR, LMCF) | Treatment policy / MNAR sensitivity | Clinical narrative (e.g., "after withdrawal patient resembles placebo") | Cro 2019 information-anchored vs Wolbers 2022 frequentist (active debate) | FDA-acceptable; clinician-interpretable | Variance choice contested; Rubin over-conservative, jackknife may inflate Type-I |
| Tipping-point delta-adjustment | MNAR sensitivity | Pre-specified delta function | Standard | Direct regulatory question: "how bad would missing data have to be?" | Delta interpretation depends on scale |
| Pattern-mixture with CCMV | Pattern-mixture MNAR | "Missing pattern resembles completer pattern" | Multiple imputation | Identifies missing cells via restriction | CCMV may be implausible if completers are atypical |
| Pattern-mixture with NCMV | Pattern-mixture MNAR | "Missing pattern resembles neighbouring pattern" | MI | Less extreme assumption than CCMV | Choice of "neighbouring" is ambiguous |
| Pattern-mixture with ACMV | Pattern-mixture MNAR (equivalent to MAR) | "Missing pattern resembles available cases" | MI | Equivalent to MAR (Molenberghs 1998) | Reduces to standard MAR analysis |
| Selection model (Diggle-Kenward 1994) | MNAR | Joint normal outcome + logistic dropout | Likelihood | Theoretically elegant | Conclusions driven by untestable parametric assumptions; FDA discouraged |
| Retrieved-dropout MI | Treatment policy | Sampling from observed post-discontinuation data | MI variance | Empirically grounded (no model assumption for missing) | Requires actual post-ICE data collection |

**Postdoc reading list:**

- NRC 2010 *Prevention and Treatment of Missing Data in Clinical Trials* (National Academies)
- Little RJA, D'Agostino R, Cohen ML et al 2012 *NEJM* 367:1355 (NRC summary)
- Mallinckrodt CH 2008/2014 Drug Information Journal / TIRS (MMRM case)
- Carpenter JR, Roger JH, Kenward MG 2013 *J Biopharm Stat* 23:1352 (reference-based MI)
- Cro S, Carpenter JR, Kenward MG 2019 *JRSS-A* 182:623 (information-anchored variance)
- Bartlett JW 2021 *Stat Biopharm Res* 15(1):178 (frequentist variance counter)
- Wolbers M, Noci A, Delmar P et al 2022 *Pharm Stat* 21(6):1246-1257 (CMI+jackknife)
- Permutt T 2016 *Stat Med* 35:2876 (analyst as adversary; tipping point)
- Diggle PJ, Kenward MG 1994 *JRSS-C* 43:49 (selection model + canonical critique)
- Molenberghs G, Michiels B, Kenward MG, Diggle PJ 1998 *Stat Neerl* 52:153 (pattern-mixture identifying restrictions; ACMV = MAR under monotone)
- Olarte Parra C, Daniel RM, Bartlett JW 2022 *Stat Biopharm Res* (MMRM-MAR IS a hypothetical estimator)

## Decision Tree by Scenario

| Scenario | Recommended approach | Why |
|----------|---------------------|-----|
| Continuous endpoint, monotone missingness, MAR plausible | MMRM with UN + Kenward-Roger via R `mmrm` | FDA-favoured Mallinckrodt 2008/2014 default |
| Continuous endpoint, ICE = treatment discontinuation, treatment policy estimand | Hybrid: J2R for discontinuation ICEs, MMRM-MAR for other (Aprocitentan 2024 precedent) | De facto FDA standard 2024-2025 |
| Continuous endpoint, treatment policy + post-ICE data collected | Retrieved-dropout MI (Wegovy STEP precedent) | Empirically grounded; FDA 2025 obesity guidance endorses |
| Continuous endpoint, MNAR sensitivity required | J2R via `rbmi` with both Rubin's variance AND frequentist (CMI+jackknife) | Cro vs Bartlett debate; report both for safety |
| Continuous endpoint, tipping-point analysis | Permutt 2016 delta-adjustment in active arm only | Direct regulatory question; pre-specify delta range |
| Binary endpoint with missing primary | MI with logistic imputation; modified Poisson for marginal RR | Per FDA 2023 covariate adjustment |
| Time-to-event with informative censoring | IPCW (Robins) or sensitivity under composite | Censoring-as-event composite; pre-specify per ICH E9(R1) |
| Very high missingness (>40%) | Report as hypothesis-generating; multiple sensitivity analyses | NRC 2010 caveat |
| Aducanumab-style differential dropout pattern | MAR primary is questionable; treatment-policy with reference-based MI primary | Lessons from the aducanumab review (Nov 2020 AdCom voted against; approved 2021) |
| Pediatric trial with hard-to-retain population | Retrieved-dropout MI + Bayesian extrapolation from adult data | FDA 2025 obesity pediatric extension guidance |

## MMRM Under MAR -- The FDA-Preferred Continuous Analysis

**Goal:** Estimate the treatment-by-visit contrast at the primary timepoint for a continuous longitudinal endpoint under MAR with valid Type-I control in small/moderate trials.

**Approach:** Fit MMRM with unstructured covariance, REML, Kenward-Roger DF correction via the Roche/openpharma `mmrm` package; pre-specify the convergence fallback hierarchy in the SAP.

**Mallinckrodt 2008/2014:** for continuous longitudinal endpoints under monotone (or near-monotone) MAR, an MMRM with treatment + visit + treatment-by-visit + baseline + baseline-by-visit, UN covariance, REML, contrast at primary timepoint -- is consistent and FDA-preferred.

```r
library(mmrm)
fit <- mmrm(
    formula = change_from_baseline ~ baseline + arm * visit + us(visit | subject),
    data = trial_data,
    method = "Kenward-Roger-Linear",  # matches SAS PROC MIXED bit-for-bit
    reml = TRUE
)
summary(fit)
```

**Kenward-Roger flavour question:**

- `method = "Kenward-Roger"` -- full second-order KR (Kenward-Roger 1997 *Biometrics* 53:983)
- `method = "Kenward-Roger-Linear"` -- drops second-order Cholesky-derivative term; matches SAS PROC MIXED bit-for-bit
- Most regulatory submissions use Kenward-Roger-Linear for SAS-R reproducibility

**Convergence fallback hierarchy** (pre-specify in SAP):

1. UN with KR (preferred)
2. UN with Satterthwaite (if KR fails)
3. Heterogeneous Toeplitz (k+1 parameters)
4. AR(1) with heterogeneous variances
5. CS with heterogeneous variances (last resort)

**The Olarte Parra unification (2022):** MMRM under MAR IS a causal hypothetical estimand by g-formula equivalence under specific identifying assumptions. The issue is articulation, not statistical machinery.

## Reference-Based Multiple Imputation -- The rbmi Framework

**Carpenter-Roger-Kenward 2013** operationalises MNAR sensitivity as clinical narrative, not numeric delta:

- **J2R:** "after withdrawal the patient instantly resembles the placebo arm"
- **CR:** "the entire post-baseline trajectory copied from placebo, with subject's baseline deviation preserved"
- **CIR:** "the patient retains on-treatment increment but trends with placebo arm thereafter, anchored at last observed value"
- **LMCF:** "patient stays at last on-treatment mean"

```r
library(rbmi)

# Define imputation model
vars <- set_vars(
    outcome = 'CHG',  # change from baseline
    visit = 'AVISIT',
    subjid = 'USUBJID',
    group = 'ARM',
    covariates = c('BASE', 'STRATA1'),
    method = method_bayes(n_samples = 100)
)

# Draws -> Impute -> Analyse -> Pool pipeline
draws_obj <- draws(data = trial_data, vars = vars)
imputed_j2r <- impute(draws_obj,
                      references = c('Active' = 'Placebo', 'Placebo' = 'Placebo'))
analyses <- analyse(imputed_j2r,
                    fun = ancova,
                    vars = list(outcome = 'CHG', visit = 'AVISIT',
                                group = 'ARM', covariates = c('BASE')))
result <- pool(analyses)  # Rubin's rules pooling
summary(result)
```

### Inference engine choice (rbmi)

1. **Bayesian MI + Rubin's rules** (historical default) -- information-anchored variance
2. **Approximate Bayesian via REML + bootstrap** -- frequentist variance
3. **Conditional mean imputation + jackknife** (Wolbers 2022) -- deterministic; FDA-friendly
4. **BMLMI** (Lipkovich-Ratitch) -- bootstrapped MI with within/between decomposition

## The Variance Debate -- Cro vs Bartlett

**The single most active argument in current biostatistics.**

**Cro/Carpenter/Kenward 2019 *JRSS-A* 182:623:** Rubin's-rules variance applied to J2R/CR/CIR is approximately information-anchored — the relative loss of information from missingness in sensitivity analysis matches the relative loss in MAR primary analysis. True repeated-sampling variance is "information positive" because reference-based MI borrows from reference arm, reducing marginal variance of active arm BELOW what an MAR analysis with same missingness would give.

**Philosophical position (Cro et al):** a sensitivity analysis should not import information the primary analysis didn't have; if borrowing from placebo makes active CI narrower, it's no longer anchored.

**The clearer framing for postdocs:** the dispute is NOT about "which variance is conservative" — it is about "which variance answers the right question." Cro: if the sensitivity analysis is meant to assess robustness to MAR, the variance should be the one that matches the informational scope of the primary MAR analysis (Rubin's, which under-states borrowing). Bartlett: if J2R is taken as the true data-generating mechanism, then the variance of inference under that mechanism is the frequentist (jackknife) variance, which delivers nominal Type-I. Both can be correct under different framings of "what is the sensitivity analysis for?"

**Bartlett 2021 *Stat Biopharm Res* 15(1):178 + Wolbers 2022 *Pharm Stat* counter:** if J2R is the actual sampling model under which inference is made, the correct frequentist variance is the one delivering nominal Type-I and coverage — the jackknife/bootstrap variance, NOT Rubin's. Simulations: Bayesian MI + Rubin's gives Type-I 0.9-2.5% (over-conservative); CMI+jackknife gives 4.84-4.96% (nominal) under J2R.

**Regulatory practice 2024-2026:**

- EMA tolerates either
- FDA reviewers increasingly flag Rubin's variance under reference-based MI as needing a frequentist sensitivity analysis in addition
- **Safe approach:** report both — Bayesian MI + Rubin's as primary (per Cro), CMI+jackknife frequentist as supportive (per Wolbers)

## Permutt Tipping-Point Analysis

**Permutt 2016 *Stat Med* 35:2876** (Permutt was head of FDA Division of Biometrics IV at the time): the regulator's question is not "what is a reasonable MNAR adjustment?" but "how bad would the missing data have to be in the active arm to overturn the significant primary result?"

```r
library(rbmi)

# Delta-template: per-visit, per-arm, per-pattern delta
delta_grid <- seq(0, 20, by = 2)  # delta range to scan
results <- list()
for (delta in delta_grid) {
    delta_template <- delta_template(imputed, delta = delta,
                                      dlag = c(1, 1, 1, 1))  # apply to all post-ICE visits
    analyses <- analyse(imputed, delta = delta_template, fun = ancova, vars = vars)
    pooled <- pool(analyses)
    results[[as.character(delta)]] <- pooled
}

# Find minimum delta that flips p > 0.05 -> tipping delta
```

**Delta-adjustment patterns:**

- **One-arm shift (FDA preferred):** add delta to imputed values in active arm only
- **Symmetric shift:** both arms worsened by delta (probes systematic optimism)
- **Reverse shift:** placebo improved by delta (more aggressive)

**Report tipping delta in residual SD units** (FDA preference for cross-trial comparison), not raw outcome units.

## Pattern-Mixture and Selection Models

### Pattern-mixture identifying restrictions (Little 1993, Molenberghs et al 1998)

Pattern-mixture factorises joint distribution as observed-data distribution stratified by dropout pattern × pattern probability. Introduces unidentifiable parameters for unobserved cells, resolved by restrictions:

- **CCMV (Complete-Case Missing-Value):** equates missing conditional to completer pattern's conditional
- **NCMV (Neighbouring-Case Missing-Value):** uses conditional of patients with one additional measurement
- **ACMV (Available-Case Missing-Value):** weights across all patterns where relevant components observed

**Molenberghs et al 1998 proved ACMV is exactly equivalent to MAR under monotone missingness** — so pattern-mixture under ACMV is a reparameterisation of MAR analysis.

J2R/CR/CIR/LMCF are pattern-mixture models with reference-arm-based identifying restrictions.

### Selection model (Diggle-Kenward 1994)

Joints a multivariate normal response model with logistic dropout model that depends on the unobserved current value.

**Canonical critique** (Diggle-Kenward 1994 discussion; Molenberghs/Kenward/Verbeke subsequent work): selection-model MNAR conclusions are driven not by data but by parametric assumptions that are *empirically untestable* — the difference between MAR and MNAR fit is identified entirely from joint normality assumption. A non-normal response will spuriously appear MNAR.

**FDA position:** selection models are used as sensitivity, never primary. FDA Division of Biometrics has repeatedly pushed back on selection models on the grounds that "the sponsor cannot tell me in clinical English what assumption I am being asked to accept." Reference-based MI is preferred because it is clinically articulable.

## Multiple Imputation in Python -- The sklearn Caveats

```python
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer
import statsmodels.formula.api as smf
import numpy as np
import pandas as pd

n_imputations = 20  # rule: m >= 100 * FMI

# CRITICAL: sample_posterior=True only works with BayesianRidge (default estimator)
imputer = IterativeImputer(max_iter=10, random_state=0, sample_posterior=True)

results = []
for i in range(n_imputations):
    imputer.set_params(random_state=i)
    imputed = pd.DataFrame(imputer.fit_transform(df[numeric_cols]), columns=numeric_cols)
    for col in ['ARM', 'sex']:
        imputed[col] = df[col].values
    model = smf.logit('outcome ~ C(ARM, Treatment(reference="Placebo")) + age', data=imputed).fit(disp=0)
    results.append({'coef': model.params.iloc[1], 'se': model.bse.iloc[1]})

# Rubin's rules
pooled_coef = np.mean([r['coef'] for r in results])
within_var = np.mean([r['se']**2 for r in results])
between_var = np.var([r['coef'] for r in results], ddof=1)
total_var = within_var + (1 + 1/n_imputations) * between_var
pooled_se = np.sqrt(total_var)
```

**Critical caveats:**

- `sample_posterior=True` SILENTLY ignored if estimator changed from BayesianRidge (e.g., to RandomForest) -> MI degenerates to single imputation
- IterativeImputer is experimental; API may change without standard deprecation
- For mixed types (binary + continuous), consider `miceforest` or R `mice`/`rbmi`
- Imputation model must include all analysis-model predictors (congeniality per Meng 1994)
- Include outcome as predictor in imputation model but exclude from imputed variables
- Never impute treatment assignment (fully determined by randomisation)

**For confirmatory regulatory work, prefer R `rbmi` or `mice` over Python sklearn** — the SAS / R precedent is stronger, the variance theory is better-developed.

## Decisive Regulatory Cases

### Aducanumab (Biogen BLA 761178, 2021)

EMERGE and ENGAGE both stopped early for futility; EMERGE high-dose positive, ENGAGE negative. MMRM-MAR primary. FDA Office of Biostatistics (Tristan Massie review) argued futility-stop-induced missingness was NOT MAR (differential ARIA-driven unblinding). The November 2020 advisory committee voted overwhelmingly against approval; FDA nonetheless approved in June 2021, over-ruling OB. Textbook case showing MAR-based primary in trial with high differential missingness is regulator-divisive.

**Lesson:** when differential dropout patterns differ by arm in clinically meaningful ways, MAR is questionable; primary should be treatment-policy with reference-based MI.

### Aprocitentan (Idorsia PRECISION, FDA 2024)

Sassi-Sayadi et al 2025 *Ther Innov Regul Sci* (PMC12753554) documents the negotiation. FDA pushed back on MMRM-MAR primary; accepted compromise: stratified imputation — J2R for treatment-discontinuation ICEs, MAR-MMRM for other missingness.

**Lesson:** this hybrid is now the de facto FDA standard for treatment-policy estimands. Pre-specify in SAP.

### Wegovy/Ozempic STEP trials (Wilding 2021 *NEJM*)

Retrieved-dropout MI as primary for treatment-policy estimand. Missing body weight at week 68 imputed by sampling from observed week-68 measurements among "retrieved dropouts" (patients who discontinued semaglutide but remained in follow-up). J2R-MI as supportive.

**Lesson:** RD-MI is now standard for chronic weight management. FDA 2025 obesity guidance explicitly endorses MI as primary.

## Per-Method Failure Modes

### MMRM-MAR with high differential missingness

- **Trigger:** Dropout rate or reason differs by arm (toxic active vs tolerated placebo).
- **Mechanism:** MAR requires that conditional on observed covariates, missingness is unrelated to outcome — implausible when patients drop out *because* the treatment isn't working.
- **Symptom:** Discontinuation reasons differ qualitatively; primary p sensitive to model specification.
- **Fix:** Treatment-policy estimand with retrieved-dropout MI as primary; J2R as sensitivity; tipping-point delta in active arm.

### Rubin's variance under reference-based MI

- **Trigger:** J2R/CR/CIR with only Rubin's-rules variance reported.
- **Mechanism:** Rubin's variance is information-anchored but over-conservative (Cro 2019).
- **Symptom:** Power loss vs frequentist variance.
- **Fix:** Report frequentist variance via CMI+jackknife as supportive (Wolbers 2022); cite both Cro and Bartlett.

### `sample_posterior=False` in sklearn IterativeImputer

- **Trigger:** Default behaviour ignored OR estimator changed from BayesianRidge.
- **Mechanism:** Imputations are point predictions, near-identical across draws; between-imputation variance ~ 0.
- **Symptom:** Artificially narrow Rubin's-pooled CIs.
- **Fix:** Always `sample_posterior=True`; verify estimator is BayesianRidge; consider R `rbmi`.

### Diggle-Kenward selection model as primary

- **Trigger:** Selection model used as primary MNAR analysis.
- **Mechanism:** MNAR vs MAR distinction driven by joint normality assumption, not data.
- **Symptom:** Reviewer asks "what clinical assumption am I being asked to accept?" and sponsor cannot answer in clinical English.
- **Fix:** Switch to pattern-mixture (reference-based MI) for primary; selection model as supportive sensitivity only.

### LOCF as primary or "conservative"

- **Trigger:** SAP specifies LOCF as primary analysis or as "conservative" sensitivity.
- **Mechanism:** LOCF is biased even under MCAR (Mallinckrodt 2008); discards uncertainty.
- **Symptom:** Reviewer cites NRC 2010 Rec 10 against LOCF.
- **Fix:** MMRM under MAR as primary; reference-based MI for MNAR sensitivity; LOCF only as historical comparison if at all.

### Imputation model uncongenial with analysis model

- **Trigger:** Analysis model includes treatment-by-covariate interaction but imputation model does not.
- **Mechanism:** Uncongeniality biases estimates and invalidates Rubin's variance pooling.
- **Symptom:** Pooled SE smaller than independent bootstrap suggests.
- **Fix:** Imputation model must be at least as flexible as analysis model (Meng 1994).

### Tipping delta in raw units only

- **Trigger:** Tipping-point analysis reports delta in raw outcome scale.
- **Mechanism:** Hard to compare across trials; clinical plausibility unclear.
- **Symptom:** Reviewer asks "how many SDs is that?"
- **Fix:** Report in residual SD units (FDA preference); both raw and standardised.

## Reconciliation: When Methods Disagree

| Pattern | Likely cause | Action |
|---------|--------------|--------|
| MMRM-MAR CI overlaps null; J2R MI CI excludes null | Reference-based MI borrows information from reference arm, reducing active-arm marginal variance below what MAR analysis with same missingness would give (Cro 2019) | Both valid under their assumptions; choose by clinical plausibility (MAR vs MNAR after differential dropout); report both; cite estimand strategy |
| Bayesian MI + Rubin's variance Type-I ~1%; CMI+jackknife Type-I ~5% under J2R | Rubin's information-anchored, over-conservative (Cro 2019); jackknife frequentist nominal (Wolbers 2022); active methodological debate | Report both; flag as Cro vs Bartlett debate; FDA increasingly accepts jackknife as supportive |
| LOCF "conservative" sensitivity gives smaller effect than MMRM-MAR | LOCF assumes flat post-ICE trajectory; biased even under MCAR (Mallinckrodt 2008) | Replace LOCF with reference-based MI; cite NRC 2010 Rec 10; reframe sensitivity as "MNAR robustness" not "conservative" |
| Tipping delta is small relative to MCID | MAR plausibility weak; primary result fragile to mild MNAR | Report tipping delta in residual SD AND relative to MCID; reconsider primary estimand toward treatment-policy with reference-based MI |
| Pattern-mixture with CCMV vs J2R conclusions differ | CCMV assumes missing pattern mirrors completers; J2R assumes mirror reference arm; different MNAR mechanisms | Choose based on which clinical scenario is more plausible (Carpenter-Roger 2013); report both as sensitivity range |
| Selection model (Diggle-Kenward) rejects MAR; pattern-mixture (reference-based MI) accepts MAR | Selection model MNAR conclusion driven by joint normality assumption (not data); pattern-mixture clinically articulable | Report pattern-mixture as primary sensitivity; selection model as supportive only; FDA prefers clinical articulation |
| MMRM with UN converges in arm A but not arm B | Convergence fragility in unstructured covariance with high dropout in one arm | Apply pre-specified SAP fallback (UN+KR -> UN+Satterthwaite -> heterogeneous Toeplitz -> AR(1)); document in CSR |

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| m >= 100 * FMI imputations (linear rule of thumb) | von Hippel 2020 *Sociol Methods Res* 49:699 (two-stage quadratic refinement) | Stable pooled SE; with 40% missingness and FMI~0.3, m=30 needed |
| Missing > 40% on key variable | NRC 2010 | MI under MAR unreliable; treat as hypothesis-generating |
| Kenward-Roger DF correction for MMRM with UN | Kenward-Roger 1997 | Without it MMRM-REML under-covers; Type-I inflates 1-2 pp |
| Tipping delta in residual SD units | FDA Division of Biometrics preference | Cross-trial comparison |
| Rubin's vs frequentist for reference-based MI | Cro 2019 vs Wolbers 2022 | Report both for regulatory safety |
| Pre-specify ICE strategy in SAP | ICH E9(R1) | Estimand-before-method |
| Examine DS domain for differential dropout | NRC 2010 implicit | If dropout differs by arm, MAR is suspect |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| LOCF reported as "conservative" | Persistent misconception | LOCF is biased under MCAR (Mallinckrodt 2008); cite NRC 2010 |
| MAR primary in trial with differential dropout | MAR plausibility not verified | Examine DS; if differential, switch to treatment-policy + reference-based MI |
| Selection model used as primary | Untestable parametric assumption drives MNAR conclusion | Pattern-mixture (reference-based MI) as primary; selection model as supportive |
| sample_posterior silently ignored | Estimator changed from BayesianRidge in sklearn | Verify estimator; consider R `rbmi` or `mice` |
| Imputation model missing interaction term | Uncongeniality with analysis model | Include analysis-model predictors AND interactions |
| Tipping delta in raw outcome scale only | Hard to compare | Report in residual SD units alongside raw |
| Rubin's variance for J2R without frequentist sensitivity | Cro 2019 over-conservative | CMI+jackknife frequentist as supportive (Wolbers 2022) |
| MMRM with CS forced after UN convergence failure | Pre-specification of fallback missing | Pre-specify hierarchy in SAP; document deviation if invoked |
| MI without outcome as predictor in imputation model | Underestimates association | Include outcome as predictor; exclude from imputed variables |
| MMRM in Python (statsmodels.mixedlm) treated as FDA-equivalent | Lacks Kenward-Roger | Use R `mmrm` for confirmatory; statsmodels.mixedlm only for exploratory |

## Anticipated Reviewer Pushback

| Pushback | Response |
|----------|----------|
| "Why MAR not MNAR primary?" | Examined DS domain; dropout rates and reasons symmetric across arms; cite Mallinckrodt 2008 MMRM-MAR convention |
| "Why not LOCF as sensitivity?" | LOCF biased even under MCAR; cite NRC 2010 Rec 10; J2R and tipping-point are clinically articulable alternatives |
| "Rubin's variance for J2R?" | Cite Cro 2019 information-anchored argument as rationale; report frequentist (CMI+jackknife) as supportive per Wolbers 2022 |
| "Tipping delta plausibility?" | Tipping delta = X.X in residual SD units; X.X exceeds MCID of Y.Y; deemed clinically implausible |
| "Selection model sensitivity?" | Provided as supportive; cite Diggle-Kenward 1994 critique that conclusions are driven by joint normality assumption; pattern-mixture is the primary sensitivity |
| "Imputation model congeniality?" | Imputation model includes all analysis-model predictors and interactions per Meng 1994 |
| "ICE strategy?" | Pre-specified per ICH E9(R1): treatment policy primary, hypothetical sensitivity, with explicit ICE mechanism in protocol |
| "Why m=20 imputations?" | Computed m >= 100 * FMI; observed FMI=0.20 -> m=20 sufficient (von Hippel 2020) |
| "Retrieved-dropout MI with sparse post-ICE data?" | If post-ICE retrieval is <50% complete, retrieved-dropout MI degrades to reference-based; switch to J2R as primary with reference-based MI as named sensitivity per Aprocitentan precedent |
| "Why is the reference arm chosen for J2R clinically plausible?" | Per ICH E9(R1), reference-based MI assumes post-discontinuation trajectory mirrors the placebo arm; this matches the clinical scenario of "patient stops treatment due to AE and returns to standard-of-care baseline." Documented in protocol with medical-monitor sign-off. |

## References

- Bartlett JW. 2021. Reference-based multiple imputation -- what is the right variance and how to estimate it. *Stat Biopharm Res* 15(1):178-186.
- Carpenter JR, Roger JH, Kenward MG. 2013. Analysis of longitudinal trials with protocol deviation: a framework for relevant, accessible assumptions, and inference via multiple imputation. *J Biopharm Stat* 23:1352-1371.
- Cro S, Carpenter JR, Kenward MG. 2019. Information-anchored sensitivity analysis: theory and application. *JRSS-A* 182:623-645.
- Diggle PJ, Kenward MG. 1994. Informative drop-out in longitudinal data analysis. *JRSS-C* 43:49-93.
- EMA. 2010. Guideline on Missing Data in Confirmatory Clinical Trials. EMA/CPMP/EWP/1776/99 Rev.1.
- ICH. 2019. E9(R1) Addendum on Estimands and Sensitivity Analysis.
- Kenward MG, Roger JH. 1997. Small sample inference for fixed effects from REML. *Biometrics* 53:983-997.
- Little RJA. 1988. A test of missing completely at random for multivariate data with missing values. *JASA* 83:1198-1202.
- Little RJA. 1993. Pattern-mixture models for multivariate incomplete data. *JASA* 88:125-134.
- Little RJA, D'Agostino R, Cohen ML et al. 2012. The prevention and treatment of missing data in clinical trials. *NEJM* 367:1355-1360.
- Mallinckrodt CH, Lane PW, Schnell D, Peng Y, Mancuso JP. 2008. Recommendations for the primary analysis of continuous endpoints in longitudinal clinical trials. *Drug Information Journal* 42:303-319.
- Sassi-Sayadi M, Verweij P, Cornelisse P. 2025. Regulatory experiences with the use of multiple imputation for missing data in a phase 3 confirmatory trial. *Ther Innov Regul Sci*.
- Meng XL. 1994. Multiple-imputation inferences with uncongenial sources of input. *Stat Sci* 9:538-558.
- Molenberghs G, Michiels B, Kenward MG, Diggle PJ. 1998. Monotone missing data and pattern-mixture models. *Stat Neerl* 52:153-161.
- NRC. 2010. *The Prevention and Treatment of Missing Data in Clinical Trials*. National Academies Press.
- Olarte Parra C, Daniel RM, Bartlett JW. 2022. Hypothetical estimands in clinical trials: a unification of causal inference and missing data methods. *Stat Biopharm Res* 15(2):421-432.
- Permutt T. 2016. Sensitivity analysis for missing data in regulatory submissions. *Stat Med* 35:2876-2879.
- von Hippel PT. 2020. How many imputations are needed (a two-stage calculation using a quadratic rule). *Sociol Methods Res* 49:699-718.
- Wolbers M, Noci A, Delmar P, Gower-Page C, Yiu S, Bartlett JW. 2022. Standard and reference-based conditional mean imputation. *Pharm Stat* 21(6):1246-1257.

## Related Skills

- clinical-biostatistics/trial-reporting - Estimand framework + CONSORT 2025 missing-data item 21c
- clinical-biostatistics/logistic-regression - Adjusted logistic with MI for binary endpoints
- clinical-biostatistics/effect-measures - Effect-measure CIs under MI pooling
- clinical-biostatistics/cdisc-data-handling - DS domain reasoning for missingness mechanism
- clinical-biostatistics/survival-analysis - Informative censoring as missing-data analogue
- clinical-biostatistics/adaptive-designs - Interim missing-data assumptions
<!-- END FILE: clinical-biostatistics/missing-data-sensitivity/SKILL.md -->

## 子目录：clinical-biostatistics/multiplicity-graphical

<!-- BEGIN FILE: clinical-biostatistics/multiplicity-graphical/SKILL.md -->
---
name: bio-clinical-biostatistics-multiplicity-graphical
description: Implements multiplicity control for confirmatory clinical trials using graphical procedures (Bretz-Maurer-Hommel), gatekeeping (parallel, serial, mixed), Hochberg/Hommel/Holm with PRDS, and the closed-testing principle (Marcus-Peritz-Gabriel; Goeman 2021 admissibility). Covers FDA Multiple Endpoints Final Guidance (October 2022), graphical procedures via R gMCP, primary + key-secondary + subgroup hierarchies, and FWER vs FDR distinction. Use when designing the multiplicity strategy for confirmatory trials with multiple primary or key secondary endpoints.
tool_type: r
primary_tool: gMCP
goal_approach_exempt: true
---

## Version Compatibility

Reference examples tested with: R `gMCP` 0.8.16+, `graphicalMCP` 0.2+, `gatekeeping`, `multcomp`, `multxpert`; Python `statsmodels` 0.14+ for basic FDR/FWER methods.

Before using code patterns, verify installed versions match. If versions differ:
- R: `packageVersion('<pkg>')` then `?function_name`
- Python: `pip show <package>` then `help(module.function)`

If code throws ImportError, AttributeError, or TypeError, introspect the installed package and adapt the example to match the actual API rather than retrying.

# Multiplicity Control for Confirmatory Trials

**"Design the multiplicity strategy for my trial"** -> Specify a closed-testing procedure (graphical, gatekeeping, hierarchical, or step-down Bonferroni-Holm) that controls family-wise error rate at the trial-wide level across primary endpoints, key secondary endpoints, and subgroup analyses, with provable strong FWER control.

## The Foundational Theorem -- Closed Testing Is Necessary

**Marcus, Peritz & Gabriel 1976 *Biometrika* 63:655:** a hypothesis H_I (I ⊆ {1,...,m}) is rejected iff every intersection hypothesis ∩_{J⊇I} H_J is rejected by a valid α-level local test. Strong FWER control holds for ANY choice of local tests.

**Goeman, Hemerik & Solari 2021 *Ann Stat* 49:1218** tightens this: closed testing is not merely sufficient — it is *necessary* for admissibility under FDP/FWER/k-FWER. **Every admissible multiplicity procedure is equivalent to some closed test.** Graphical procedures, gatekeepers, Hommel, fixed-sequence, fallback — all are closed tests in disguise.

**FWER vs FDR philosophical divide:**

- **FWER:** P(any false positive among m tests) — regulatory standard for confirmatory inference (agency wants to bound per-trial false-positive rate)
- **FDR:** Expected proportion of false discoveries among rejections — exploratory standard (genomics, fMRI, biomarker screens) where many true positives expected

Confirmatory clinical trials use FWER essentially universally.

## Algorithmic Taxonomy

| Procedure | Type | FWER control | Power profile | Use case |
|-----------|------|--------------|---------------|----------|
| Bonferroni | Single-step | Yes, any dependence | Conservative; loses 30-50% power vs Hommel under positive dependence | Very small m; worst-case dependence |
| Holm 1979 | Step-down | Yes, any dependence | Better than Bonferroni; uniformly dominates | Default for any dependence pattern |
| Hochberg 1988 | Step-up | Yes under PRDS (Sarkar 1998) | Better than Holm under PRDS | Positive correlation; verify PRDS |
| Hommel 1988 | Step-up via closed tests | Yes under PRDS | Uniformly dominates Hochberg by 1-3% | Whenever Hochberg is valid |
| Fixed-sequence (hierarchical) | Sequential | Yes, any dependence | Full alpha for first; subsequent zero if any fail | When clear priority ordering; "key secondary" labelling |
| Parallel gatekeeping (Dmitrienko 2003) | Multi-family | Yes | Family-by-family; secondary tested if any primary rejects | Primary family + secondary family |
| Serial gatekeeping | Sequential families | Yes | Strict: family k tested only if ALL of family k-1 reject | Co-primary + secondary tiers |
| Mixed gatekeeping (Dmitrienko-Tamhane 2008) | Combination | Yes | Combines closed-testing local procedures across families | Complex hierarchies |
| Graphical procedures (Bretz-Maurer 2009) | Closed-test as directed graph | Yes by construction | Flexible; allocate alpha to hypotheses via graph weights | Modern standard for confirmatory SAPs |
| Graphical + Simes/parametric (Bretz et al 2011) | Closed-test with non-Bonferroni local tests | Yes when Simes valid | Gains power under correlation | Complex co-primary + key secondary + subgroup hierarchies |
| Maurer-Bretz 2013 entangled graphs | Memory-augmented graphs | Yes by construction | Alpha propagation depends on origin | Parent-descendant constraints |
| Benjamini-Hochberg 1995 | FDR | FDR controlled at level q | Higher power than FWER | Exploratory only; NOT for confirmatory regulatory |

**Postdoc reading list:**

- Marcus R, Peritz E, Gabriel KR 1976 *Biometrika* 63:655 (closed testing — the foundation)
- Goeman JJ, Hemerik J, Solari A 2021 *Ann Stat* 49:1218 (closed testing necessary for admissibility)
- Holm S 1979 *Scand J Stat* 6:65 (step-down Bonferroni)
- Hochberg Y 1988 *Biometrika* 75:800 (step-up Simes)
- Hommel G 1988 *Biometrika* 75:383 (closed Simes; dominates Hochberg)
- Sarkar SK 1998/2008 *Ann Stat* (PRDS for Hochberg validity)
- Bretz F, Maurer W, Brannath W, Posch M 2009 *Stat Med* 28:586 (graphical procedures — foundational paper)
- Bretz F, Posch M, Glimm E, Klinglmueller F, Maurer W, Rohmeyer K 2011 *Biom J* 53:894 (Simes/parametric extensions)
- Maurer W, Bretz F 2013 *Stat Med* 32:1739 (entangled graphs / memory)
- Dmitrienko A, Offen WW, Westfall PH 2003 *Stat Med* 22:2387 (parallel gatekeeping)
- Dmitrienko A, Tamhane AC, Wiens B 2008 *Biom J* (mixed/multistage gatekeeping)
- FDA 2022 *Multiple Endpoints in Clinical Trials* Final Guidance (October 2022)
- Pocock SJ, Ariti CA, Collier TJ, Wang D 2012 *Eur Heart J* (win-ratio)

## Decision Tree by Scenario

| Scenario | Recommended procedure | Why |
|----------|----------------------|-----|
| 2 co-primary endpoints (both must succeed) | No alpha split needed; per-endpoint alpha-level test; cite FDA 2022 | Co-primary doesn't split alpha; inflates n via joint power |
| 2 multiple primary endpoints (any-wins) | Graphical procedure or Holm with weights | Alpha must be allocated; graphical is flexible |
| 1 primary + 2 key secondary endpoints | Hierarchical (serial gatekeeping) OR graphical with alpha propagation | Modern SAPs favour graphical |
| 1 primary + 3 secondary + 4 subgroup analyses | Graphical procedure via gMCP with pre-specified weights | Complex hierarchies benefit from graph visualisation |
| Primary endpoint + tipping-point sensitivity | No multiplicity adjustment needed for sensitivity | Sensitivity is "what if" not "another claim" |
| Many exploratory biomarker subgroups | Benjamini-Hochberg FDR | Exploratory; not for label claims |
| Win-ratio composite (cardiology) | Single test; no multiplicity | Composite captures multiple events in single hierarchy |
| Subgroup analysis (pre-specified) | Graphical alpha allocation; small budget (≤20% by convention); see Dane 2019 for subgroup discipline | Confirmatory subgroup discovery requires explicit allocation |
| Adaptive trial with treatment arm dropping | Combination tests (Bauer-Köhne 1994) + closed testing | See clinical-biostatistics/adaptive-designs |
| Group-sequential with multiple endpoints | gsDesign or rpact with multivariate alpha spending | Hierarchical alpha across both time and endpoints |

## Bretz-Maurer Graphical Procedures -- The Modern Standard

**The Bretz-Maurer-Brannath-Posch 2009 *Stat Med* 28:586 framework recast weighted Bonferroni-Holm closed tests as directed weighted graphs:**

- Vertices = elementary null hypotheses with local weights summing to 1
- Directed edges = alpha-propagation rule (when a hypothesis is rejected, its weight redistributes to descendants per edge weights)
- The graph IS the procedure: a single visual fully specifies a closed-test procedure across primary, key secondary, and subgroup hierarchies

### gMCP R package

```r
library(gMCP)

# Construct a graph for primary + 2 key secondary endpoints
# Primary endpoint at full alpha; if rejected, alpha propagates equally to secondaries
hypotheses <- c('Primary', 'Sec1', 'Sec2')
weights <- c(1, 0, 0)  # initial alpha all on primary
# Transition matrix: rows = source, columns = target
# When Primary rejects, weight 0.5 goes to each secondary; when Sec1/Sec2 rejects, alpha returns
transitions <- matrix(c(
    0,    0.5,  0.5,
    0,    0,    1,
    0,    1,    0
), nrow = 3, byrow = TRUE, dimnames = list(hypotheses, hypotheses))

graph <- graphMCP(m = transitions, weights = weights, hnames = hypotheses)
# Note: in current gMCP, the graph constructor is `graphMCP(m=, weights=, hnames=)`;
# `matrix2graph()` appeared in older tutorials and is not the canonical exported API
# -- verify with `?graphMCP` / `?gMCP` in the installed gMCP release before scripting.
# Set p-values from the trial
p_vals <- c(Primary = 0.018, Sec1 = 0.042, Sec2 = 0.038)

# Run the graphical procedure at alpha = 0.025
result <- gMCP(graph, pvalues = p_vals, alpha = 0.025)
print(result)
# Hierarchical rejection: Primary rejects -> alpha propagates to secondaries -> ...
```

### Standard SAP graph patterns

| Pattern | Graph topology | Use |
|---------|----------------|-----|
| Pure hierarchical (fixed sequence) | H1 -> H2 -> H3 with weight 1 on each transition | Strict ordering |
| Holm graph (equal weights) | Each Hi -> Hj with weight 1/(m-1) | No priority ordering |
| Primary + secondaries | Primary -> Sec1 (0.5), Sec2 (0.5); Sec1 ↔ Sec2 (1) | Pivotal labeling claims |
| Co-primary chain | H1 -> H2 with full weight if BOTH H1a, H1b reject | Co-primary + secondary |
| Subgroup branch | Primary -> Subgroup_OS (0.2), Sec1 (0.4), Sec2 (0.4) | Discovery subgroup with budget |

### Bretz et al 2011 -- Simes and parametric extensions

When endpoints are positively correlated, replace the Bonferroni-based intersection test with Simes (for positive dependence) or parametric (using known correlation):

```r
library(gMCP)
# Use Simes-based local tests at each intersection
result_simes <- gMCP(graph, pvalues = p_vals, alpha = 0.025, test = 'Simes')
# Or parametric with estimated correlation matrix
result_param <- gMCP(graph, pvalues = p_vals, alpha = 0.025, corr = correlation_matrix)
```

### Maurer-Bretz 2013 entangled graphs

**Entangled graphs** add memory: the alpha propagation can depend on the *origin* of the alpha. This allows parent-descendant constraints that a single non-entangled graph cannot express. Example: secondary endpoint Sec1 receives alpha only from Primary, never from Sec2.

**Postdoc argument:** purists argue memory makes the procedure non-coherent in Gabriel's sense; Glimm/Maurer/Bretz argue it matches real-world inferential intent.

**Gabriel coherence in plain terms:** a coherent procedure rejects a hypothesis H consistently regardless of which superset of H is being tested. Non-entangled graphs are coherent: if H1 is rejected via path A, it would also be rejected via path B. **Entangled (memory-bearing) graphs sacrifice coherence:** the same H may be rejected when alpha arrives from one parent but not from another, because the propagation history changes the available alpha. The trade-off is operational power -- entangled graphs can encode "secondary X is meaningful only if primary Y rejects, not if primary Z rejects" inferential intent that flat coherent procedures cannot express. Choose based on whether the SAP needs path-dependent priority.

## Gatekeeping Procedures

### Serial gatekeeping (hierarchical)

Test H1 at full alpha; only if it rejects, test H2 at full alpha; etc. **Maximises power for H1** but H_k becomes inferentially worthless once any H_j (j<k) fails.

```r
# Hierarchical / serial: just a chain graph in gMCP
hyp <- c('H1', 'H2', 'H3', 'H4')
weights <- c(1, 0, 0, 0)
trans <- matrix(c(0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0),
                 nrow=4, dimnames=list(hyp, hyp))
graph <- graphMCP(m = trans, weights = weights, hnames = hyp)
```

**Pre-specification of order is critical** — based on clinical importance, NOT expected effect size. Ordering by expected effect is data-driven and inflates Type-I.

### Parallel gatekeeping (Dmitrienko 2003)

Secondary family is tested only if *at least one* primary rejects. Bonferroni-based parallel gatekeeper has stepwise representation (Guilbaud 2007 *Biom J* 49:917).

### Mixed / multistage (Dmitrienko-Tamhane 2008)

Permits using any closed-testing local procedure (e.g., Holm in family 1, Hommel in family 2) and combining via closure principle. R `gMCP::generalMixGatekeeping` or `Mediana`/`MultXpert` packages.

**Postdoc tradeoff:** parallel gatekeeping power loss vs collapsing endpoints into a composite (which avoids multiplicity but dilutes effect if components move in opposite directions); whether tree gatekeeping (Dmitrienko et al 2008 *Stat Med* 27:3446) over-engineers vs equivalent graphical procedure.

## Hochberg vs Hommel vs Holm

**Holm 1979** — step-down rejective Bonferroni; FWER controlled under any joint dependence. **Conservative but robust.**

**Hochberg 1988** — step-up using ordered Simes critical values; needs Simes inequality which requires PRDS (Sarkar 1998, 2008). Under PRDS, Hochberg uniformly dominates Holm.

**Hommel 1988** — also Simes-based but uses closed-testing tableau directly (not step-up shortcut). Uniformly more powerful than Hochberg (typically 1-3% gain).

### When Hochberg fails (anti-conservative)

**Hochberg becomes Type-I-inflated under negative dependence** — relevant when comparing endpoints mathematically constrained to move in opposite directions (LDL-C and HDL-C; complementary efficacy and safety endpoints).

**Sarkar critique:** when PRDS cannot be proven, fall back to Holm. The lost power is the price of robustness.

```python
# Python: statsmodels supports Holm, Hochberg, Hommel
from statsmodels.stats.multitest import multipletests

p_vals = [0.018, 0.042, 0.038, 0.015]
for method in ['holm', 'hochberg', 'hommel', 'bonferroni']:
    reject, adj_p, _, _ = multipletests(p_vals, alpha=0.05, method=method)
    print(f'{method}: reject={reject}, adjusted={adj_p}')
```

## FDA Multiple Endpoints Final Guidance (October 2022)

**Federal Register 2022-22882** finalises 2017 draft. Key changes vs draft:

- Explicit recognition of newer methods including win-ratio (Pocock 2012 *Eur Heart J*) and weighted composites
- Clearer language that "key secondary" endpoints are those for which sponsor wishes to make label claims and which must be in a Type-I-error-controlled hierarchy
- Appendix with worked graphical-procedure examples

### Categories

| Category | Approach | Note |
|----------|----------|------|
| Composite | Single test; no multiplicity | Win-ratio, DOOR/RADAR, time-to-first-event |
| Co-primary (all-win) | Each at full alpha; n inflated for joint power | Power = product of marginals |
| Multiple primary (any-wins) | Alpha must be split (Bonferroni or graphical) | More n required than co-primary if effects similar |
| Primary + key secondary | Hierarchical or graphical | Modern preference: graphical for flexibility |

**Winner's bias warning:** when post-hoc-selected endpoints are emphasised, bias-corrected effect estimates are recommended (same selection-bias issue as adaptive design).

## The "Almighty Primary Endpoint" Critique

**Dmitrienko-D'Agostino 2017 *Stat Med* 36:4423 editorial** surveys progress in trial-multiplicity methodology. A recurring theme motivating that work: insisting on a single primary endpoint can lose power when a therapy has broad multi-domain benefit (heart failure drugs with effects on mortality, hospitalisation, symptoms, biomarkers) -- motivating composite endpoints, the win ratio, or multiple primary endpoints with explicit alpha allocation.

**Win-ratio (Pocock-Ariti-Collier-Wang 2012)** and **hierarchical composite (DOOR/RADAR, Evans 2015)** are responses — they preserve a single inferential test while letting multiple endpoints contribute.

**FDA counter-position** (Hung, O'Neill, Wang): without a designated primary, sponsors and regulators negotiate over secondary endpoints post hoc, destroying inferential meaning. Hence the FDA 2022 guidance reaffirms key-secondary hierarchies.

## Per-Method Failure Modes

### Hochberg under negative dependence

- **Trigger:** Endpoints constrained to move in opposite directions (LDL vs HDL; efficacy vs harm).
- **Mechanism:** Hochberg's PRDS assumption fails; Simes inequality doesn't hold; Type-I inflated.
- **Symptom:** Replication with Holm finds non-significant where Hochberg rejected.
- **Fix:** Switch to Holm (no PRDS assumption); cite Sarkar 1998.

### Fixed-sequence with wrong ordering

- **Trigger:** Ordering by expected effect size rather than clinical priority.
- **Mechanism:** Data-driven ordering inflates Type-I.
- **Symptom:** Reviewer asks for pre-specified ordering rationale.
- **Fix:** Pre-specify order by clinical priority in SAP; document rationale.

### Graphical procedure without pre-specified weights

- **Trigger:** Weights chosen at analysis time to favour observed results.
- **Mechanism:** Equivalent to post-hoc multiplicity tuning; inflates Type-I.
- **Symptom:** Multiple "what if" graph variants in CSR.
- **Fix:** Pre-specify graph and weights in SAP; document at protocol design.

### Bonferroni when graph would gain power

- **Trigger:** Default conservative choice when no thought put into structure.
- **Mechanism:** Loses 30-50% power vs Hommel/graphical when m ~ 10 correlated tests.
- **Symptom:** Underpowered trial reaches non-significance where graphical procedure would.
- **Fix:** Design a proper graph in `gMCP`; cite Bretz-Maurer 2009.

### FDR used for confirmatory primary

- **Trigger:** SAP specifies BH-FDR for primary multiplicity.
- **Mechanism:** FDR controls expected proportion of false discoveries, not P(any false positive).
- **Symptom:** Regulatory reviewer rejects as non-confirmatory.
- **Fix:** FWER (graphical, Holm, Hochberg, Hommel) for confirmatory; FDR for exploratory only.

### Subgroup analyses claimed without multiplicity

- **Trigger:** Trial reports 10 subgroups with one significant at α=0.05.
- **Mechanism:** ~40% probability of at least one false positive under global null.
- **Symptom:** Cherry-picked subgroup claim in submission.
- **Fix:** Pre-specified graphical alpha allocation OR explicit hypothesis-generating label; cite EMA 2019 subgroup guideline.

### Win-ratio reported without hierarchical priority

- **Trigger:** Win-ratio composite with unspecified component priority.
- **Mechanism:** Component prioritisation drives the result; arbitrary choice = data-dependent answer.
- **Symptom:** Two analysts get different results from same data depending on hierarchy.
- **Fix:** Pre-specify hierarchy in SAP; sensitivity over alternative hierarchies.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| FWER for confirmatory; FDR for exploratory | ICH E9; FDA 2022 Multiple Endpoints | Regulatory standard universally |
| Bonferroni: ~10 tests -> 30-50% power loss | Sarkar 1998 PRDS | Conservative under positive dependence |
| PRDS required for Hochberg validity | Sarkar 2008 *Ann Stat* | Otherwise Type-I inflated; fall back to Holm |
| Subgroup α budget <=20% of total (convention) | Dane 2019 EFSPI white paper (subgroup discipline) | Discipline against subgroup fishing |
| Key secondary requires hierarchy in SAP | FDA 2022 Final | Labeling claims need Type-I-controlled test |
| Composite avoids multiplicity but dilutes effect | Pocock 2012 *Eur Heart J* | Win-ratio captures heterogeneity in single test |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| Hochberg applied to negatively-dependent endpoints | PRDS not checked | Switch to Holm (cite Sarkar 1998) |
| Fixed-sequence ordering data-driven | Post-hoc selection | Pre-specify clinical priority in SAP |
| Bonferroni at 10 correlated endpoints | Default conservatism | Graphical procedure (gMCP); 30-50% power gain |
| FDR for confirmatory primary | Misunderstanding error rates | FWER mandatory for confirmatory; FDR exploratory only |
| Graphical procedure run with multiple weight schemes | Post-hoc graph tuning | Pre-specify single graph in SAP |
| Subgroups significant without multiplicity | Cherry-picking | Pre-specified allocation OR explicit hypothesis-generating label |
| Co-primary treated as multiple primary | Confused alpha allocation | Co-primary: no alpha split; inflate n. Multiple primary: split alpha |
| Win-ratio component priority unspecified | Data-driven choice | Pre-specify hierarchy with rationale; sensitivity over alternatives |
| `multipletests` default `method='hs'` (Holm-Sidak) | Common Python mistake | Always specify `method='holm'`, `'hommel'`, etc., explicitly |
| Sensitivity analysis listed as a "key secondary" requiring alpha | Confusion about role | Sensitivity is "what if" not "another claim"; no alpha needed |

## Anticipated Reviewer Pushback

| Pushback | Response |
|----------|----------|
| "Why this multiplicity procedure?" | Closed testing per Marcus-Peritz-Gabriel; specific implementation is graphical (Bretz-Maurer 2009) with pre-specified weights in SAP |
| "Why Hommel not Holm?" | PRDS holds (positive correlation among endpoints); Hommel dominates Holm by 1-3% with no Type-I cost |
| "Why graph weights X, Y, Z?" | Clinical priority: primary > key secondary > exploratory; weights reflect labelling claim hierarchy |
| "Are these endpoints positively correlated?" | Sensitivity analyses provided: Bonferroni, Holm, Hochberg, Hommel results all in CSR appendix; concordant |
| "Where is alpha for the subgroup analysis?" | Pre-specified 20% of primary alpha allocated (a common convention); cite Dane 2019 for subgroup discipline |
| "Why not just composite endpoint?" | Composite would dilute differential effect on mortality vs hospitalisation; key-secondary hierarchy preserves component-level claims |
| "PRDS check for Hochberg?" | Endpoints positively correlated via simulation under null; PRDS holds; Hochberg/Hommel valid |
| "Sensitivity in the hierarchy?" | No — sensitivity is "what if" and does not require alpha. Listed as supportive not key secondary. |

## References

- Bretz F, Maurer W, Brannath W, Posch M. 2009. A graphical approach to sequentially rejective multiple test procedures. *Stat Med* 28:586-604.
- Bretz F, Posch M, Glimm E, Klinglmueller F, Maurer W, Rohmeyer K. 2011. Graphical approaches for multiple comparison procedures using weighted Bonferroni, Simes, or parametric tests. *Biom J* 53:894-913.
- Burman CF, Sonesson C, Guilbaud O. 2009. A recycling framework for the construction of Bonferroni-based multiple tests. *Stat Med* 28:739-761.
- Dmitrienko A, Offen WW, Westfall PH. 2003. Gatekeeping strategies for clinical trials that do not require all primary effects to be significant. *Stat Med* 22:2387-2400.
- Dmitrienko A, Tamhane AC, Wiens BL. 2008. General multistage gatekeeping procedures. *Biom J* 50:667-677.
- FDA. 2022. Multiple Endpoints in Clinical Trials. Final Guidance.
- Goeman JJ, Hemerik J, Solari A. 2021. Only closed testing procedures are admissible for controlling false discovery proportions. *Ann Stat* 49:1218-1238.
- Guilbaud O. 2007. Bonferroni parallel gatekeeping -- transparent generalizations, adjusted p-values, and short proofs. *Biom J* 49:917-927.
- Hochberg Y. 1988. A sharper Bonferroni procedure for multiple tests of significance. *Biometrika* 75:800-802.
- Holm S. 1979. A simple sequentially rejective multiple test procedure. *Scand J Stat* 6:65-70.
- Hommel G. 1988. A stagewise rejective multiple test procedure based on a modified Bonferroni test. *Biometrika* 75:383-386.
- Marcus R, Peritz E, Gabriel KR. 1976. On closed testing procedures with special reference to ordered analysis of variance. *Biometrika* 63:655-660.
- Maurer W, Bretz F. 2013. Memory and other properties of multiple test procedures generated by entangled graphs. *Stat Med* 32:1739-1753.
- Pocock SJ, Ariti CA, Collier TJ, Wang D. 2012. The win ratio: a new approach to the analysis of composite endpoints in clinical trials. *Eur Heart J* 33:176-182.
- Sarkar SK. 2008. Generalizing Simes' test and Hochberg's stepup procedure. *Ann Stat* 36:337-363.

## Related Skills

- clinical-biostatistics/trial-reporting - Multiplicity strategy reporting per CONSORT 2025
- clinical-biostatistics/subgroup-analysis - Subgroup multiplicity allocation
- clinical-biostatistics/power-and-sample-size - Power adjustment for co-primary endpoints
- clinical-biostatistics/adaptive-designs - Combination tests for adaptive multiplicity
- clinical-biostatistics/effect-measures - Reporting multiple effect measures post-multiplicity adjustment
- experimental-design/multiple-testing - General methods (FDR, FWER, q-values)
<!-- END FILE: clinical-biostatistics/multiplicity-graphical/SKILL.md -->

## 子目录：clinical-biostatistics/power-and-sample-size

<!-- BEGIN FILE: clinical-biostatistics/power-and-sample-size/SKILL.md -->
---
name: bio-clinical-biostatistics-power-sample-size
description: Computes sample size and power for clinical trials including continuous, binary, and time-to-event endpoints; superiority, non-inferiority, and equivalence designs; FDA 2016 non-inferiority margin selection with M1/M2 framework; Schoenfeld 1981 and Lakatos 1988 for survival; Schuirmann TOST and 80-125% bioequivalence; minimum clinically important difference (MCID) vs δ distinction. Use when justifying trial size in protocol or SAP per CONSORT 2025 item 16a.
tool_type: mixed
primary_tool: statsmodels
goal_approach_exempt: true
---

## Version Compatibility

Reference examples tested with: statsmodels 0.14+, scipy 1.12+, numpy 1.26+, pandas 2.1+. R packages cited: pwr, gsDesign (Anderson/Merck), gsDesign2, rpact (Wassmer/Brannath), presize, npsurvSS, nph, simtrial.

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- R: `packageVersion('<pkg>')` then `?function_name`

If code throws ImportError, AttributeError, or TypeError, introspect the installed package and adapt the example to match the actual API rather than retrying.

# Power and Sample Size for Clinical Trials

**"Justify the trial's sample size"** -> Compute the n needed to detect a pre-specified alternative δ with power 1-β at significance α, accounting for endpoint distribution, design (superiority/NI/equivalence), expected dropout, multiplicity, and stratification — and distinguish δ (the effect the trial is powered to detect) from MCID (the clinically meaningful difference).

## The Foundational Distinction -- δ vs MCID

**δ (the alternative effect):** what the trial is *powered to detect*. Usually set above the MCID because sponsors want a strong signal that exceeds noise + design uncertainty.

**MCID (Minimum Clinically Important Difference):** the smallest effect size considered clinically meaningful. Jaeschke-Singer-Guyatt 1989 *Control Clin Trials* 10:407 (anchor-based) and Norman-Sloan-Wyrwich 2003 *Med Care* 41:582 ("the remarkable universality of half a standard deviation") established the modern conventions.

**Confusing the two has produced both:**

- Underpowered trials where sponsor sets δ = MCID and gets a CI straddling zero
- Overgenerous NI margins where sponsor sets M2 = full MCID (NI margin should be a fraction of MCID)

**Postdoc rule of thumb:** for superiority, δ >= 1.5 × MCID; for NI, M2 <= 0.5 × MCID.

## Algorithmic Taxonomy

| Design | Formula / approach | Software | Strength | Fails when |
|--------|--------------------|----------|----------|------------|
| Two-sample t-test, continuous | Cohen's d; n = 2 × (z_α/2 + z_β)² / d² | `pwr::pwr.t.test` (R); `statsmodels.power.tt_ind_solve_power` (Py) | Standard | Heteroscedasticity; non-normal outcomes |
| Two-sample proportions (Fleiss) | Asymptotic normal approximation with/without continuity correction | `power.prop.test` (R) -- uncorrected; `pwr::pwr.2p.test`; statsmodels | Standard | n < 100/arm: continuity correction debate (D'Agostino 1988) |
| Survival (Schoenfeld 1981) | events ≈ 4(z_α/2 + z_β)² / (log HR)² for 1:1 | `gsDesign::nSurv`; `npsurvSS::size_two_arm` | Standard PH-conformant | PH violated (immuno-oncology) under-estimates by 20-50% |
| Survival under non-PH (Lakatos 1988) | Markov chain accommodating time-varying HR, accrual, dropout | `gsDesign::nSurv`; `npsurvSS`; `simtrial` | Handles immuno-oncology delayed effects | Requires explicit specification of HR(t) and accrual |
| MaxCombo SS under NPH | Simulation-based; pre-specify weight family | `nphRCT`; `simtrial` | Robust to NPH pattern | Computationally heavier |
| Non-inferiority fixed-margin | n = (z_α + z_β)² × variance / M² | `pwr::pwr.t2n.test` adapted; `rpact::getSampleSizeMeans` | Pre-discounted M | Constancy assumption violation invisible |
| Non-inferiority synthesis | Pool historical control-vs-placebo + current test-vs-control | `gsDesign::ssTwoArmTest` | More efficient than fixed-margin | Constancy assumption MUST hold exactly |
| Equivalence TOST | Two one-sided tests at α each | `pwr::pwr.t.test` adapted; `presize` | No multiplicity adjustment needed | Wrong question when superiority/NI is intended |
| Group-sequential | Lan-DeMets spending function | `rpact`; `gsDesign` | Interim analyses; early stopping | More complex SAP |
| Sample-size re-estimation (Mehta-Pocock) | Promising-zone conditional power | `rpact::getSampleSizeMeans` with reestimation | Recovers power if interim shows promise | Unblinded SSR scares FDA |
| Cluster-randomised | Adjust for design effect = 1 + (m-1)ICC | `clusterPower`; `pwr` adapted | Standard | ICC misspecification |

**Postdoc reading list:**

- Fleiss JL 1981 *Statistical Methods for Rates and Proportions* (with/without continuity correction tables)
- Schoenfeld DA 1981 *Biometrika* 68:316 (canonical TTE formula)
- Lakatos E 1988 *Biometrics* 44:229 (Markov chain SS for complex survival)
- Schuirmann DJ 1987 *J Pharmacokinet Biopharm* 15:657 (TOST)
- Jaeschke R, Singer J, Guyatt GH 1989 *Control Clin Trials* 10:407 (MCID anchor-based)
- Norman GR, Sloan JA, Wyrwich KW 2003 *Med Care* 41:582 (0.5 SD heuristic)
- Snapinn SM 2000 *Curr Control Trials Cardiovasc Med* 1:19 (NI biocreep)
- Temple R, Ellenberg SS 2000 *Ann Intern Med* 133:455 + 133:464 (NI assay sensitivity; **Ann Intern Med NOT NEJM** — common citation error)
- Hung HMJ, Wang SJ, O'Neill RT 2005 *Biom J* (NI within-trial Type-I not guaranteed)
- Mehta CR, Pocock SJ 2011 *Stat Med* 30:3267 (promising zone)
- Lin RS, Lin J, Roychoudhury S et al 2020 *Stat Biopharm Res* (NPH Working Group)

## Decision Tree by Scenario

| Scenario | Recommended approach | Why |
|----------|---------------------|-----|
| Continuous outcome, two-arm parallel, superiority | Fleiss / Cohen's d formula via `power.t.test` or statsmodels | Standard; cite Fleiss 1981 |
| Binary outcome, n > 100/arm | Uncorrected normal approximation via `power.prop.test`; statsmodels `power_proportions_2indep` | Adequate for n > 100 |
| Binary outcome, n < 100/arm | Fisher exact-based simulation OR Fleiss with continuity correction | Continuity correction debate; cite D'Agostino 1988 if uncorrected |
| Time-to-event with PH | Schoenfeld 1981 via `gsDesign::nSurv` | Standard; pre-specify hazards |
| Time-to-event under expected NPH (immuno-oncology) | Lakatos 1988 OR simulation via `simtrial::simtrial`/`nphRCT` | Schoenfeld under-estimates by 20-50%; cite Lin 2020 |
| Non-inferiority continuous | Fixed-margin with M2 = 0.5 × historical M1 (discounted) | FDA 2016 NI guidance; cite Temple-Ellenberg 2000 |
| Non-inferiority binary | Fixed-margin with Miettinen-Nurminen CI for RD | Cite EMA NI guidance; MN-CI standard |
| Bioequivalence (Cmax/AUC) | TOST with 80-125% margins on geometric mean ratio | FDA 1992 BE guidance; Schuirmann 1987 |
| Cluster-randomised | n × design effect = 1 + (m-1)ICC | Cite Murray 1998 cluster RCT methodology |
| Group-sequential | Lan-DeMets spending function | `rpact` or `gsDesign` |
| Pilot for sample size re-estimation | Blinded SSR (Friede-Kieser 2006) | No Type-I inflation; safer than unblinded |
| Promising-zone reestimation | Mehta-Pocock 2011 with pre-specified increase rule | Recovers power; cite caveat re Jennison-Turnbull 2015 critique |

## Continuous Outcomes -- Two-Sample t-Test

```python
from statsmodels.stats.power import tt_ind_solve_power

# Solve for n per group
n = tt_ind_solve_power(
    effect_size=0.5,  # Cohen's d = (mu1 - mu2) / sigma
    alpha=0.05,
    power=0.80,
    alternative='two-sided'
)
print(f'n per arm = {np.ceil(n):.0f}')

# Solve for power given n
power = tt_ind_solve_power(effect_size=0.5, alpha=0.05, nobs1=100, alternative='two-sided')
```

**Cohen's d benchmarks:** small = 0.2, medium = 0.5, large = 0.8. Choose d to detect based on prior literature or clinically meaningful effect, NOT post-hoc to fit the affordable n.

**Inflate for dropout:** if dropout rate is q, multiply final n by 1/(1-q). For q=0.20, n_total = n/0.80.

**Stratified randomisation efficiency:** if randomisation stratifies on prognostic factors with combined R² = r against outcome, the effective n is n/(1-r²). Senn 2013 *Stat Med* 32:1439 makes the precision argument explicit.

## Binary Outcomes -- The Continuity Correction Debate

```python
from statsmodels.stats.power import NormalIndPower
import math

# Without continuity correction
p1, p2 = 0.30, 0.20
pbar = (p1 + p2) / 2
z_alpha = 1.96  # two-sided alpha=0.05
z_beta = 0.84   # power=0.80
n = ((z_alpha * math.sqrt(2 * pbar * (1 - pbar)) +
      z_beta * math.sqrt(p1 * (1 - p1) + p2 * (1 - p2))) / (p1 - p2)) ** 2
print(f'n per arm (uncorrected) = {math.ceil(n)}')

# Continuity-corrected (Fleiss formula)
correction = (1 + math.sqrt(1 + 4 / (n * abs(p1 - p2)))) ** 2 / 4
n_corrected = math.ceil(n * correction)
print(f'n per arm (continuity corrected) = {n_corrected}')
```

**The continuity correction debate** (D'Agostino, Chase & Belanger 1988 *Am Stat* 42:198):

- Pro (Fleiss, Yates): better matches the exact distribution under H0
- Con: overly conservative, wastes ~10% sample size; modern computing makes exact (Fisher-Irwin, Boschloo) tests feasible

**R's `power.prop.test` uses uncorrected normal approximation** — can over-state power 5-10% in small samples (n<100). For confirmatory work with n<100, use simulation-based SS via `simr` or `presize`.

## Survival (Time-to-Event)

### Schoenfeld 1981 -- the canonical formula

```python
import math

# Events needed for two-sample log-rank under PH (Schoenfeld 1981)
from scipy.stats import norm

def schoenfeld_events(hr, alpha=0.05, power=0.80, allocation_ratio=1.0, two_sided=True):
    """
    events = (z_crit + z_beta)^2 / (p*(1-p) * log(HR)^2)

    where z_crit = z_{1-alpha/2} for two-sided test OR z_{1-alpha} for one-sided.
    """
    z_crit = norm.ppf(1 - alpha/2) if two_sided else norm.ppf(1 - alpha)
    z_beta = norm.ppf(power)
    p = 1 / (1 + allocation_ratio)
    return math.ceil((z_crit + z_beta) ** 2 / (p * (1 - p) * math.log(hr) ** 2))

# For HR=0.70, alpha=0.05 two-sided, 80% power, 1:1 -> approx 247 events
events_needed = schoenfeld_events(hr=0.70)
print(f'Events needed for HR=0.70: {events_needed}')
```

**Events drive power, not subjects.** Convert to n via expected event rate and follow-up:

```python
# n needed = events / overall event probability over follow-up
expected_overall_event_prob = 0.40  # from pilot or historical
n_per_arm = math.ceil(events_needed / (2 * expected_overall_event_prob))
# Inflate for dropout
n_per_arm_with_dropout = math.ceil(n_per_arm / (1 - 0.15))  # 15% dropout
```

### Lakatos 1988 -- complex survival

Use R `gsDesign::nSurv()` or `npsurvSS::size_two_arm()` for complex scenarios with:

- Time-varying hazard ratios (delayed effect)
- Non-uniform accrual
- Different dropout rates per arm
- Cure fractions

```r
library(gsDesign)
n_lakatos <- nSurv(
    lambdaC = 0.04,     # control hazard per month
    hr = 0.70,           # treatment HR
    eta = 0.005,         # dropout hazard per month
    T = 24,              # total study duration in months
    minfup = 12,         # minimum follow-up
    accrualTime = 12,    # accrual duration
    alpha = 0.025,       # one-sided
    beta = 0.10          # power = 90%
)
print(n_lakatos)
```

### Under non-PH (immuno-oncology with delayed effect)

**Schoenfeld 1981 ASSUMES PH.** Under immuno-oncology with delayed separation, the formula under-estimates required events by 20-50%. The fix:

```r
# Simulate under expected hazard pattern (Lin 2020 NPH Working Group recommendation)
library(simtrial)
sim_result <- simtrial(
    n_per_arm = 250,
    enroll_rate = piecewise_enroll(),
    fail_rate = piecewise_fail(  # delayed-effect specification
        duration = c(6, 18),
        fail_rate = c(0.04, 0.04),  # control
        hr = c(1.0, 0.5),            # treatment HR is 1 for first 6 months, then 0.5
        dropout_rate = c(0.005, 0.005)
    ),
    total_duration = 36
)
# Compute empirical power via MaxCombo or weighted log-rank
```

## Non-Inferiority Designs -- The FDA 2016 Framework

**FDA NI Trials Guidance (November 2016)** establishes the canonical M1/M2 framework:

- **M1** = entire effect of active control vs placebo (lower bound of CI from historical meta-analysis)
- **M2** = clinically acceptable loss, typically M1/2 (50% effect retention) but as conservative as M1/4 for mortality endpoints

**The "double discount" trap:** M2 = 0.5 × (lower CI bound of M1) effectively requires 50% retention of a discounted historical estimate, yielding a much tighter margin than naive point-estimate retention. This has effectively halted new antibiotic NDA development under stringent NI margins.

```python
# Fixed-margin NI sample size (binary endpoint)
import math

p_control = 0.85         # historical/observed control success rate
p_test = 0.85            # null assumption: test = control (NI null is test - control < -M2)
margin_M2 = 0.05         # pre-specified clinically acceptable loss
z_alpha = 1.645          # one-sided alpha=0.025
z_beta = 0.84            # power=0.80

# Approximate: n per arm
variance_term = p_control * (1 - p_control) + p_test * (1 - p_test)
n = math.ceil((z_alpha + z_beta) ** 2 * variance_term / margin_M2 ** 2)
print(f'NI sample size per arm: {n}')
```

**Use Miettinen-Nurminen score CI for RD** (the regulatory standard) when computing the NI margin from observed proportions. Cite `ratesci::scoreci` (R) for production.

**Constancy assumption:** the historical placebo-vs-active effect must persist in the NI trial. If standard of care drifted, M1 over-estimates and margin is too liberal. **Hung-Wang-O'Neill 2005** *Biom J* critique: NI trials have NO within-trial Type-I error guarantee — alpha is conditional on constancy.

**Assay sensitivity (Temple-Ellenberg 2000 *Ann Intern Med* 133:455 + 133:464):** NI trials have only *external* assay sensitivity (inferred from historical data + constancy); placebo-controlled trials have *internal* assay sensitivity. This is why NI trials are second-best when placebo is ethical.

## Equivalence Designs and Bioequivalence

**TOST (Two One-Sided Tests; Schuirmann 1987):** reject H0 of inequivalence iff both one-sided tests reject at α each — equivalent to the 1-2α CI lying within (-δ, +δ). Closed under intersection-union -> no multiplicity adjustment needed despite two tests.

```python
# TOST sample size for continuous outcome
import math

def tost_sample_size(mu_diff, sigma, margin, alpha=0.05, power=0.80):
    """Sample size per arm for TOST equivalence test."""
    z_alpha = 1.645  # one-sided
    z_beta = 0.84
    effect = abs(margin - abs(mu_diff))
    if effect <= 0:
        raise ValueError('|mu_diff| must be < margin')
    n = math.ceil(2 * sigma ** 2 * (z_alpha + z_beta) ** 2 / effect ** 2)
    return n

n_eq = tost_sample_size(mu_diff=0.0, sigma=10, margin=5)
print(f'Equivalence sample size per arm: {n_eq}')
```

**FDA 1992 bioequivalence (80-125% rule):** geometric mean ratio of Cmax and AUC must have 90% CI within (0.80, 1.25). Implemented in `PowerTOST` R package for crossover BE designs.

## Crossover Designs -- Bioequivalence and Repeated-Measures

**Crossover trials** randomise each subject to receive both treatments in different periods. Power calculation is fundamentally different from parallel: the within-subject SD (sigma_w) drives power, not between-subject SD (sigma_b). With reasonable carryover-free designs, crossover requires ~25-50% the n of parallel for the same precision.

```python
# Two-period crossover sample size (continuous endpoint)
import math

def crossover_n_continuous(mean_diff, sd_within, alpha=0.05, power=0.80):
    """n per sequence (so total n = 2*n) for two-period crossover."""
    z_alpha = 1.96  # two-sided
    z_beta = 0.84   # power=0.80
    n_per_seq = math.ceil(2 * (z_alpha + z_beta)**2 * sd_within**2 / mean_diff**2)
    return n_per_seq, 2 * n_per_seq  # n_per_seq, n_total
```

### Bioequivalence (FDA 1992 / EMA 2010 framework)

**Average bioequivalence:** geometric mean ratio (GMR) of test/reference Cmax and AUC must have 90% CI within (0.80, 1.25). Log-transform pharmacokinetic parameters; analyse with mixed-effects ANOVA (period, sequence, treatment, subject random).

```r
library(PowerTOST)
# Sample size for 2x2 crossover bioequivalence with CV (within-subject)
n_be <- sampleN.TOST(
    alpha = 0.05,
    targetpower = 0.80,
    theta0 = 0.95,        # expected GMR
    theta1 = 0.80,        # lower BE bound
    theta2 = 1.25,        # upper BE bound
    CV = 0.25,             # within-subject CV
    design = '2x2x2'      # standard 2-period 2-sequence
)
print(n_be)
```

**Highly variable drugs (CV > 30%):** standard 80-125% fails with feasible n. Use **scaled average bioequivalence (SABE)**; the expanding-limits (ABEL) approach below is the EMA method (the FDA's reference-scaled RSABE uses a different criterion and `PowerTOST::sampleN.RSABE()`):
- Reference-scaled limits: theta = exp(0.760 * sigma_WR) when sigma_WR > 0.294
- Widens BE bounds proportional to within-subject variability of reference
- `PowerTOST::sampleN.scABEL()` for sample size

### Carryover assessment (Grizzle 1965)

**Grizzle test** for carryover: compares baseline-adjusted period 1 vs period 2 effects. **Now controversial:** the two-stage Grizzle carryover pretest is misleading -- it inflates the Type-I error of the treatment comparison (Freeman 1989 *Stat Med* 8:1421); significant "carryover" should drive design choice (washout extension), not an analysis switch (Senn 2002, *Cross-over Trials in Clinical Research*, 2nd ed.).

**Modern operational rule:** pre-specify adequate washout (>=5 half-lives); do NOT routinely test for carryover in primary analysis. If carryover is biologically plausible, use parallel design or extend washout.

### Period effect

Period effects (calendar/learning) are estimable in 2x2 crossover. Standard analysis includes period as fixed effect:

```r
library(nlme)
fit <- lme(response ~ treatment + period, random = ~1 | subject, data = df)
```

If period significant, treatment effect is still unbiased (orthogonal in balanced 2x2); report period effect for transparency.

### Decision tree -- when crossover is appropriate

| Scenario | Use crossover? | Why |
|----------|----------------|-----|
| Bioequivalence of pharmacokinetic parameters | YES | Standard regulatory; within-subject precision much higher |
| Chronic stable disease (HTN, GERD, asthma) | YES | Reversible response; ~50% sample size savings |
| Acute disease (sepsis, MI) | NO | Cannot retreat same patient |
| Curative intent (oncology, surgery) | NO | Treatment alters disease state irreversibly |
| Long-half-life drug (>1 week) | NO | Washout impractical |
| Patient-reported outcomes with strong period bias | CAUTION | Period bias may dominate |

## MCID -- Anchor-Based vs Distribution-Based

| Method | Source | Description |
|--------|--------|-------------|
| Anchor-based | Jaeschke 1989 | Patient-reported anchor question; MCID = mean change in subjects who report "small important" change |
| 1 SEM (Wyrwich 1999) | *J Clin Epidemiol* | MCID ≈ standard error of measurement |
| 0.5 SD (Norman 2003) | *Med Care* 41:582 | "Remarkable universality of half a standard deviation" across PROMs |
| 0.5 SD baseline | Common rule of thumb | Quick approximation for unknown PROMs |

**Postdoc rule:** δ in power calculation should EXCEED MCID (often 1.5-2× MCID) so that trials are powered to detect effects clearly larger than the noise threshold.

## Multiple Endpoints -- See multiplicity-graphical

For co-primary endpoints, power-adjust per FDA Multiple Endpoints Guidance (October 2022):

- **Co-primary (all-must-win):** each endpoint at full alpha but joint power = product -> inflate n
- **Multiple primary (any-wins):** alpha split (e.g., Bonferroni or graphical)
- **Hierarchical:** test in order; if any fail, downstream cannot be claimed

## Reconciliation: When Methods Disagree

| Pattern | Likely cause | Action |
|---------|--------------|--------|
| Schoenfeld n much smaller than Lakatos simulation n | PH violated under expected HR(t) pattern (immuno-oncology delayed effect) | Use Lakatos OR simulation under expected HR(t); cite Lin 2020 NPH Working Group |
| Continuity-corrected vs uncorrected proportion SS differ by ~10% | Asymptotic approximation debate (D'Agostino 1988) | For confirmatory n < 100/arm, use simulation-based SS; document correction approach in SAP |
| NI margin per FDA double discount (50% of M1 lower CI) vs sponsor proposed margin (50% of M1 point estimate) | Sponsor uses point estimate; FDA expects lower-CI discount | FDA 2016 NI guidance: M2 from lower CI bound is the regulatory expectation |
| Bayesian predictive probability of success vs frequentist power give different n | Bayesian integrates prior uncertainty; frequentist conditions on hypothesised δ | Bayesian PPoS more honest about pre-trial uncertainty; frequentist preferred for confirmatory regulatory; report both for adaptive contexts |
| TOST and CI-inclusion approach give different equivalence conclusions | TOST is two-one-sided at α; CI is 1-2α — mathematically equivalent so should NOT disagree | If disagree, check α conventions (Schuirmann 1987: TOST at α, CI at 1-2α) |
| Sponsor's MCID vs published anchor-based MCID differ | Different anchor questions or population | Cite primary MCID source; cross-check with Norman 2003 0.5 SD heuristic; declare in SAP |
| Stratified-randomisation SS calculation vs unstratified differ substantially | Stratification efficiency gain via Senn 2013 formula | Use stratified formula; cite efficiency = 1/(1-r²) where r² is R² of strata against outcome |
| Cluster-RCT SS underpowered after enrollment | ICC misspecified at design (most common SS failure in cluster RCTs) | Use historical ICC + sensitivity analysis at ±50% of estimate; cite Murray 1998 |

## Per-Method Failure Modes

### Schoenfeld under non-PH

- **Trigger:** Immunotherapy or other delayed-effect mechanism
- **Mechanism:** Schoenfeld assumes constant log-HR
- **Symptom:** Trial under-powered; observed events insufficient
- **Fix:** Lakatos 1988 or simulation under expected HR(t); cite Lin 2020 NPH Working Group

### Continuity correction debate

- **Trigger:** Small-sample binary design
- **Mechanism:** Uncorrected normal approx over-states power; corrected wastes ~10%
- **Symptom:** Trial reach significance at lower n than expected
- **Fix:** Use simulation-based SS for n<100; pre-specify correction approach in SAP

### NI margin too liberal

- **Trigger:** M2 set to MCID rather than 50% of historical M1
- **Mechanism:** Allows clinically unacceptable inferiority within "non-inferior" CI
- **Symptom:** Regulators flag margin as inappropriate at scientific advice
- **Fix:** M2 <= 0.5 × MCID; M2 <= 0.5 × historical M1 lower bound (FDA double discount)

### Constancy assumption violated

- **Trigger:** NI trial with new standard of care differing from historical
- **Mechanism:** M1 derived from historical data no longer reflects current control efficacy
- **Symptom:** Active control performs worse than expected; "successful" NI may mask true inferiority
- **Fix:** Synthesis approach with formal sensitivity to constancy; consider three-arm trial with small placebo

### MCID confused with δ

- **Trigger:** Sponsor sets δ = MCID in power calculation
- **Mechanism:** Trial powered to detect smallest meaningful effect, with no margin for noise/dropout
- **Symptom:** Effect estimate near MCID with wide CI straddling zero
- **Fix:** δ >= 1.5 × MCID; document rationale in SAP

### Promising-zone "stealth alpha inflation"

- **Trigger:** Mehta-Pocock SSR applied without sufficient simulation
- **Mechanism:** a naive unblinded increase analysed with the conventional (unweighted) statistic inflates Type-I error (Cui-Hung-Wang 1999); the pre-specified weighted CHW statistic preserves alpha
- **Symptom:** Type-I inflation when the CHW weighting is dropped; separately, Jennison-Turnbull 2015 show the promising zone is inefficient -- the largest power gains per added patient lie outside it
- **Fix:** Pre-specify increase rule transparently; report simulation operating characteristics

### Unblinded SSR -- DMC firewall failure

- **Trigger:** Interim effect estimate leaked beyond IDMC
- **Mechanism:** Sponsor inference from sample-size increase decision reveals direction of interim effect
- **Symptom:** Regulator audit reveals unblinding
- **Fix:** Strict firewall; only "increase / no increase" communicated to sponsor; document SOP

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| δ >= 1.5 × MCID for superiority | Postdoc rule; Norman 2003 implication | δ = MCID gives no margin for sampling variation |
| M2 <= 0.5 × historical M1 (FDA double discount) | FDA NI 2016 guidance | Conservative retention against biocreep |
| M2 <= 0.5 × MCID for NI | Standard regulatory expectation | Acceptable loss < clinically meaningful difference |
| Schoenfeld under non-PH under-estimates by 20-50% | Lin 2020 NPH WG | Switch to Lakatos or simulation |
| Continuity correction wastes ~10% sample size | D'Agostino, Chase & Belanger 1988 *Am Stat* 42:198 | Modern computing makes exact tests cheap |
| 90% CI within (0.80, 1.25) for BE | FDA 1992 BE guidance | Geometric mean ratio of Cmax/AUC |
| Unblinded SSR Type-I requires CHW weights | Cui-Hung-Wang 1999 | Naive increase inflates Type-I |
| Promising-zone CP range ~30-80% | Mehta-Pocock 2011 *Stat Med* 30:3267 | Mathematical calibration for Type-I preservation |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| Trial under-powered for immunotherapy | Schoenfeld formula used under non-PH | Lakatos or simulation; cite Lin 2020 |
| δ = MCID, CI straddles zero | δ-MCID confusion | Pre-specify δ >= 1.5 × MCID |
| NI "success" but active much worse than historical | Constancy violation | Cite Hung 2005; consider synthesis or 3-arm |
| Unblinded SSR with naive sample increase | Type-I inflation | CHW-weighted test; cite Cui-Hung-Wang 1999 |
| `power.prop.test` over-states power n < 100 | Uncorrected normal approximation | Simulation-based SS or Fleiss continuity correction |
| BE failure after large n with point estimate near 1.0 | Variability higher than assumed | Re-estimate from pilot; consider replicate design for highly variable drugs |
| Promising-zone tipping to favourable not pre-specified | Operational confusion | Document increase rule in SAP; pre-specify cap |
| Cluster RCT n based on individual-level | Design effect ignored | n × (1 + (m-1)ICC); cite Murray 1998 |
| TOST sample size with non-zero true difference | Treating null as abs(mu_diff)=0 | Include realistic mu_diff in calculation |

## Anticipated Reviewer Pushback

| Pushback | Response |
|----------|----------|
| "Is δ realistic?" | Justified from prior phase 2; δ exceeds MCID by factor X; pre-specified |
| "Why this NI margin?" | M2 = 50% of historical lower-CI M1 per FDA 2016 double discount; M2 < MCID |
| "Constancy assumption?" | Reviewed historical placebo-vs-active effect over time; stable; sensitivity to lower-end constancy provided |
| "Schoenfeld vs Lakatos?" | PH plausible from phase 2 KM; pre-specified Schoenfeld; Lakatos simulation under expected delayed-effect as sensitivity |
| "Continuity correction?" | n > 200/arm; uncorrected normal approximation valid (Fleiss 1981) |
| "Bioequivalence variability assumption?" | Conservative (upper bound of historical CV); pilot will trigger re-estimation if CV >X% |
| "Cluster ICC source?" | Historical ICC from prior cluster trial in similar setting; sensitivity at ICC ±50% provided |
| "MCID source?" | Anchor-based MCID from validation study (Jaeschke 1989); supported by 0.5 SD heuristic (Norman 2003) |
| "Promising zone or just blinded SSR?" | Promising zone with pre-specified CP boundaries; CHW weights for Type-I control |

## References

- Cui L, Hung HMJ, Wang SJ. 1999. Modification of sample size in group sequential clinical trials. *Biometrics* 55:853-857.
- D'Agostino RB, Chase W, Belanger A. 1988. The appropriateness of some common procedures for testing the equality of two independent binomial populations. *Am Stat* 42:198-202.
- FDA. 2016. Non-Inferiority Clinical Trials to Establish Effectiveness. Final Guidance.
- FDA. 2022. Multiple Endpoints in Clinical Trials. Final Guidance.
- Fleiss JL. 1981. *Statistical Methods for Rates and Proportions* (2nd ed). Wiley.
- Friede T, Kieser M. 2006. Sample size recalculation in internal pilot study designs. *Biom J* 48:537-555.
- Hung HMJ, Wang SJ, O'Neill RT. 2005. A regulatory perspective on choice of margin and statistical inference issue in non-inferiority trials. *Biom J* 47:28-36.
- Jaeschke R, Singer J, Guyatt GH. 1989. Measurement of health status: ascertaining the minimal clinically important difference. *Control Clin Trials* 10:407-415.
- Lakatos E. 1988. Sample sizes based on the log-rank statistic in complex clinical trials. *Biometrics* 44:229-241.
- Lin RS, Lin J, Roychoudhury S, Anderson KM, Hu T, Huang B, Leon LF, Liao JJZ, Liu R, Luo X, Mukhopadhyay P, Qin R, Tatsuoka K, Wang X, Wang Y, Zhu J, Chen TT, Iacona R. 2020. Alternative analysis methods for time to event endpoints under nonproportional hazards: a comparative analysis. *Stat Biopharm Res*.
- Mehta CR, Pocock SJ. 2011. Adaptive increase in sample size when interim results are promising. *Stat Med* 30:3267-3284.
- Norman GR, Sloan JA, Wyrwich KW. 2003. Interpretation of changes in health-related quality of life: the remarkable universality of half a standard deviation. *Med Care* 41:582-592.
- Schoenfeld DA. 1981. The asymptotic properties of nonparametric tests for comparing survival distributions. *Biometrika* 68:316-319.
- Schuirmann DJ. 1987. A comparison of the two one-sided tests procedure and the power approach for assessing the equivalence of average bioavailability. *J Pharmacokinet Biopharm* 15:657-680.
- Senn S. 2013. Seven myths of randomisation in clinical trials. *Stat Med* 32:1439-1450.
- Snapinn SM. 2000. Noninferiority trials. *Curr Control Trials Cardiovasc Med* 1:19-21.
- Temple R, Ellenberg SS. 2000. Placebo-controlled trials and active-control trials in the evaluation of new treatments, part 1: ethical and scientific issues. *Ann Intern Med* 133:455-463.
- Ellenberg SS, Temple R. 2000. Placebo-controlled trials and active-control trials in the evaluation of new treatments, part 2: practical issues and specific cases. *Ann Intern Med* 133:464-470.
- Wyrwich KW, Tierney WM, Wolinsky FD. 1999. Further evidence supporting an SEM-based criterion for the identification of meaningful intra-individual changes in health-related quality of life. *J Clin Epidemiol* 52:861-873.

## Related Skills

- clinical-biostatistics/survival-analysis - TTE-specific sample size (Schoenfeld, Lakatos, simulation)
- clinical-biostatistics/effect-measures - δ on OR/RR/RD scales
- clinical-biostatistics/categorical-tests - Binary endpoint test selection
- clinical-biostatistics/multiplicity-graphical - Power adjustment for co-primary endpoints
- clinical-biostatistics/adaptive-designs - SSR, promising zone, group-sequential
- clinical-biostatistics/bayesian-trials - Bayesian SS via predictive probability of success
- clinical-biostatistics/trial-reporting - CONSORT 2025 item 16a (sample size justification)
- experimental-design/sample-size - General sample-size methods
- experimental-design/power-analysis - General power methods
<!-- END FILE: clinical-biostatistics/power-and-sample-size/SKILL.md -->

## 子目录：clinical-biostatistics/subgroup-analysis

<!-- BEGIN FILE: clinical-biostatistics/subgroup-analysis/SKILL.md -->
---
name: bio-clinical-biostatistics-subgroup-analysis
description: Performs subgroup and heterogeneous treatment effect (HTE) analyses for clinical trials. Covers Mantel-Haenszel pooling, Breslow-Day, interaction tests in regression, RERI for additive interaction, modern data-adaptive HTE methods (STEPP, SIDES, causal forests, X/R-learners), Bayesian shrinkage (Dixon-Simon, MAP, EXNEX), graphical multiplicity (Bretz-Maurer), and credibility frameworks (Sun BMJ, EMA 2019). Use when analyzing treatment effects across patient subgroups for regulatory submissions or precision-medicine claims.
tool_type: python
primary_tool: statsmodels
---

## Version Compatibility

Reference examples tested with: statsmodels 0.14+, scipy 1.12+, numpy 1.26+, pandas 2.1+, matplotlib 3.8+, scikit-learn 1.4+. R packages cited: grf, policytree, causalToolbox, personalized, SIDES, stepp, gMCP, partykit, RBesT, brms.

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- R: `packageVersion('<pkg>')` then `?function_name`

If code throws ImportError, AttributeError, or TypeError, introspect the installed package and adapt the example to match the actual API rather than retrying.

# Subgroup Analysis and Heterogeneous Treatment Effects

**"Analyze treatment effects across subgroups"** -> Test whether treatment effects differ across pre-specified or data-discovered subgroups using interaction tests, stratified estimators, modern data-adaptive HTE methods, or Bayesian shrinkage -- with explicit declaration of confirmatory vs exploratory intent and credibility assessment.

## The Senn Foundation -- Why Most Subgroup Claims Are Wrong

**Senn 2018 *Nature* 563:619-621 (and *Statistical Issues in Drug Development* Ch. 9, 14):** observed between-patient response variation is NOT evidence of patient-level HTE. It conflates within-patient noise, period effects, regression-to-the-mean, and measurement error with true individual heterogeneity. Senn-Rolfe-Julious 2011 *SMMR* 20:657 documents that variance-component decomposition of replicate-crossover trials repeatedly fails to find subject-by-treatment interaction even where reviewers were certain one must exist.

**Brookes et al 2004 *J Clin Epidemiol* 57:229 — the 4x penalty:** detecting a treatment-by-subgroup interaction requires approximately 4x the sample size needed to detect the main treatment effect of similar magnitude. A trial powered to detect OR=0.6 overall cannot reliably detect subgroup differences of similar magnitude. Non-significant interaction tests are usually underpowered, not null.

**Senn's aphorism (paraphrased from SIDD):** "a trial can have subgroup analyses or proper power, not both." A single trial cannot simultaneously be powered for a primary effect AND for credible subgroup discovery; pretending otherwise misrepresents posterior uncertainty.

## Algorithmic Taxonomy

| Method | What it answers | Inference | Strength | Fails when |
|--------|-----------------|-----------|----------|------------|
| Mantel-Haenszel / CMH | Common OR across pre-defined strata | Asymptotic | Preserves stratification factor from randomisation | Stratum ORs reverse direction (Simpson) |
| Breslow-Day | Homogeneity of stratum ORs | Asymptotic chi-square | Test of effect modification | Underpowered with few/sparse strata; non-significance NOT proof of homogeneity |
| Gail-Simon 1985 | **Qualitative** interaction (sign reversal) | Likelihood ratio | Distinguishes quantitative from qualitative | Original LR is liberal at small n; use exact critical values (Pan-Wolfe 1997) |
| Logistic regression interaction | Per-subgroup conditional OR | Wald, LR | Most efficient single-model approach | Conditional ORs subject to non-collapsibility; over-fits in multi-way |
| RERI | Additive interaction on multiplicative scale | Delta-method or bootstrap CI | Captures public-health-relevant scale | Delta-method poor near boundary; nonlinear function of three ORs |
| STEPP (Bonetti-Gelber 2000) | Continuous covariate subgroups via overlapping windows | Permutation supremum test | Avoids dichotomisation of biomarkers | Window-size choice affects results; correlated estimates require permutation inference |
| SIDES / SIDEScreen (Lipkovich 2011) | Data-discovered subgroups via recursive partitioning | Resampling-adjusted base-vs-complement p | Multiplicity correctly absorbed | Tuning skeleton parameters affects FWER calibration |
| QUINT (Dusseldorp 2014) | Qualitative-interaction trees | Bootstrap stability | Directly tests crossover (A-better, B-better, equal) | Only two-arm continuous/binary; survival extensions ad hoc |
| Virtual Twins (Foster 2011) | Per-subject CATE via twin RF predictions | Bootstrap | Decouples nuisance from interpretable subgroup | Biased when RF underestimates effect heterogeneity in either arm |
| Causal forests (Athey-Wager 2019) | Pointwise CATE with honest splits | Influence-function CI | Asymptotic Gaussianity; doubly robust via AIPW | Finite-sample CI validity at trial-scale n debated (Rehill 2025) |
| Meta-learners X/R-learner (Künzel 2019) | Marginal/conditional CATE | Cross-fit influence function | X-learner dominates T-learner when arms unbalanced | Needs propensity for X-learner; R-learner requires nuisance n^(1/4) rate |
| MOB (Zeileis 2008) | Parameter-instability trees | M-fluctuation test | Theoretically clean; invariant to monotone transforms | Worse out-of-sample CATE than causal forest at large p |
| Bayesian shrinkage (Dixon-Simon 1991) | Posterior subgroup effects shrunken to overall | Posterior intervals from MCMC | Honest about prior expectation of no qualitative interaction | Prior choice on tau drives results; Dane et al 2019 white paper warns against for signal generation |
| EXNEX (Neuenschwander 2016) | Mixture of exchangeable + per-basket non-exchangeable | Posterior | Avoids HM "catastrophic borrowing" when one basket truly different | Weight choice (often 0.5/0.5 default) affects borrowing strength |

**Postdoc reading list:**

- Wang et al 2007 *NEJM* 357:2189 ("Reporting of subgroup analyses in clinical trials") — the canonical NEJM-mandated practice
- Sun et al 2010/2012 *BMJ* 340:c117 and 344:e1553 — 11 credibility criteria
- Dane, Spencer, Rosenkranz, Lipkovich, Parke 2019 *Pharm Stat* 18:126 with Hemmings-Koch commentary at 18:140 — EFSPI white paper + critique
- EMA 2019 Guideline on subgroups (EMA/CHMP/539146/2013, effective Aug 2019) — distinguishes "assessment subgroups" (regulatory, pre-specified) from "discovery subgroups" (exploratory)
- Athey & Wager 2019 *Observational Studies* 5:37; Athey, Tibshirani, Wager 2019 *Ann Stat* 47:1148 — causal forests
- Rehill 2025 *Int Stat Rev* — applied causal forest audit; many papers misreport tuning and omit honest-splitting/calibration diagnostics

## Decision Tree by Scenario

| Scenario | Recommended approach | Why |
|----------|----------------------|-----|
| Pre-specified subgroup in confirmatory trial | Interaction term in single model + graphical-procedure multiplicity (gMCP) | EMA 2019 "assessment subgroup"; interaction test + Bonferroni-graph alpha control |
| Stratified randomisation by site/region | CMH or logistic with strata as covariates; stratum-specific OR reported in forest plot | Kahan-Morris 2012; ignoring strata is over-conservative (SE biased upward, power loss); strata-specific ORs for transparency |
| 5-15 pre-specified subgroups, regulatory submission | Forest plot + interaction tests + Holm/graphical FWER correction | Default regulatory presentation; multiplicity adjustment expected |
| Continuous biomarker subgroup (e.g., HbA1c, biomarker score) | STEPP (sliding-window plot + permutation supremum test) | Avoids arbitrary dichotomisation; cite Bonetti-Gelber 2004 |
| Suspected qualitative interaction (treatment helps some, harms others) | Gail-Simon 1985 LR test with Pan-Wolfe 1997 exact critical values | Distinguishes quantitative from qualitative; critical for label restriction |
| Data-discovery of HTE subgroup | SIDES/SIDEScreen with permutation FWER + replication mandate | Lipkovich 2011; signal-discovery not signal-confirmation |
| Continuous CATE estimation with many covariates | Causal forest (R `grf::causal_forest`) + RATE test (Yadlowsky 2025) | Modern HTE; honest splitting; influence-function CIs; RATE tests whether ranking is predictive vs prognostic |
| Basket trial across rare-disease strata | EXNEX or robust MAP with `RBesT` | Borrows across strata while permitting one to detach if truly different |
| Subgroup signal needing replication planning | Bayesian shrinkage for adjusted estimates; Sun 2012 winner's curse | Selected subgroups have inflated effect by selection bias |
| Pediatric extrapolation borrowing from adult data | Power prior (gamma in 0.3-0.6) per FDA Bayesian draft Jan 2026 | Partial borrowing with discount; standard regulatory approach |

## Mantel-Haenszel and Stratified Analysis

**Goal:** Estimate a pooled treatment effect across strata while testing homogeneity.

**Approach:** Construct per-stratum 2x2 tables; CMH for pooled OR and null test; Breslow-Day for homogeneity (with caveats).

```python
from statsmodels.stats.contingency_tables import StratifiedTable
import pandas as pd
import numpy as np

tables = []
for stratum in df['site'].unique():
    sub = df[df['site'] == stratum]
    t = pd.crosstab(sub['treatment'], sub['outcome']).values
    if t.shape == (2, 2) and t.min() > 0:
        tables.append(t)

st = StratifiedTable(tables)
print('MH pooled OR:', st.oddsratio_pooled)
print('95% CI:', st.oddsratio_pooled_confint())
print('CMH H0: common OR=1, p =', st.test_null_odds().pvalue)
print('Breslow-Day H0: equal ORs, p =', st.test_equal_odds().pvalue)
```

**Breslow-Day power trap:** with k=3 strata and modest heterogeneity, Breslow-Day power can be <40%. Non-significance does NOT prove homogeneity — it just means the null cannot be rejected. Always supplement with a forest plot AND an LR interaction test from logistic regression.

## Interaction Terms in Regression -- The Correct Way

**Single model with interaction is the regulatory standard** — comparing p-values from separate per-subgroup models is statistically invalid (separate models have different power, and the p-value differences confound effect size with sample size).

```python
import statsmodels.formula.api as smf
import numpy as np

# Single model with interaction (CORRECT)
model = smf.logit(
    'outcome ~ C(treatment, Treatment(reference="Placebo")) * C(age_group)',
    data=df
).fit()
# Interaction coefficient tests effect modification
# LR test: compare to additive model:
additive = smf.logit('outcome ~ C(treatment, Treatment(reference="Placebo")) + C(age_group)', data=df).fit()
lr_p = 1 - chi2.cdf(2 * (model.llf - additive.llf), model.df_model - additive.df_model)

# Extract subgroup-specific ORs for reporting:
for group in df['age_group'].unique():
    sub_model = smf.logit('outcome ~ C(treatment, Treatment(reference="Placebo"))',
                          data=df[df['age_group'] == group]).fit()
    or_val = np.exp(sub_model.params.iloc[1])
    ci = np.exp(sub_model.conf_int().iloc[1])
    print(f'{group}: OR={or_val:.3f} ({ci[0]:.3f}-{ci[1]:.3f})')
```

## RERI for Additive Interaction

```python
# Fit interaction model: outcome ~ treatment + subgroup_indicator + treatment:subgroup_indicator
# OR_11 = OR for treated in subgroup (vs untreated not in subgroup)
# OR_10 = OR for treated not in subgroup
# OR_01 = OR for untreated in subgroup
reri = or_11 - or_10 - or_01 + 1
# RERI > 0 = synergism (combined effect > sum of individual)
# RERI = 0 = no additive interaction
# RERI < 0 = antagonism
# CI requires delta method or bootstrap (nonlinear function of three ORs)
```

**Multiplicative vs additive interaction:** logistic regression tests multiplicative interaction (ratio of ORs). Null multiplicative interaction does NOT imply null additive interaction. For public health decisions, additive interaction is often more relevant.

## Modern Data-Adaptive HTE Methods

### STEPP (Subpopulation Treatment Effect Pattern Plot)

```python
# R recommended; Python equivalents are emerging
# library(stepp)
# subset_obj <- new('stwin', type='sliding', r1=100, r2=200)  # window sizes
# step_obj <- stepp(eff='binary', cov='biomarker', trt='treatment',
#                   resp='outcome', subset=subset_obj, ...)
# plot(step_obj); test_pattern(step_obj, nperm=1000)
```

Bonetti-Gelber 2000/2004; window-size choice (sliding vs tail-oriented) affects results. **Naive simultaneous CIs are wrong** — estimates are correlated across windows; use permutation-based supremum tests of pattern flatness (Yip et al 2016 *Clin Trials* 13(4):382; tail-oriented STEPP is more stable than the sliding-window variant).

### SIDES / SIDEScreen

```python
# R: library(SIDES) or library(rsides)
# Recursive partitioning with differential-effect splitting + permutation-adjusted subgroup p
```

Lipkovich-Dmitrienko-Denne-Enas 2011 *Stat Med* 30:2601; SIDEScreen (Lipkovich-Dmitrienko 2014 *J Biopharm Stat* 24:130) adds variable-importance prefilter + base-vs-complement test. **The inferential complement test correctly absorbs multiplicity of considered splits** — Bonferroni alternatives over-correct.

### Causal forests (Athey-Wager)

```python
# R recommended; econml is the Python equivalent
# library(grf)
# cf <- causal_forest(X, Y, W, num.trees=2000)
# tau.hat <- predict(cf, X)$predictions
# test_calibration(cf)  # omnibus calibration test
```

**Honest splitting** (one sub-sample for splits, another for leaf estimates) yields asymptotic Gaussianity and pointwise CIs (Athey-Tibshirani-Wager 2019 *Ann Stat* 47:1148). Doubly-robust variants use AIPW pseudo-outcomes.

**Diagnostic discipline (Rehill 2025 audit):** applied causal-forest papers frequently misreport tuning, skip honest-splitting validation, or omit the `test_calibration` check. Required diagnostic steps:

1. Honest splitting enabled (`honesty=TRUE`)
2. `test_calibration(cf)` — regresses actual treatment effects on out-of-bag CATE predictions; significant positive slope = CATE has signal
3. Variable importance via permutation
4. RATE/AUTOC test (Yadlowsky 2025 *JASA*) — single p-value omnibus test for whether CATE ranking has predictive (not just prognostic) value

### Meta-learners (Künzel-Sekhon-Bickel-Yu 2019 *PNAS* 116:4156)

- **S-learner:** single outcome model on (Z, X); take difference. Biased when treatment effect smaller than baseline effect.
- **T-learner:** separate models per arm; take difference. Standard baseline.
- **X-learner:** T-learner + cross-imputation + propensity weighting. Dominates T-learner when arms unbalanced (1:k, k>=3) or true CATE is smoother than response.
- **R-learner (Nie-Wager 2021 *Biometrika* 108:299):** orthogonal Robinson-style residualisation, debiased ML. Asymptotically dominates X-learner when nuisance models converge at n^(1/4) rate.

```python
# Python: econml
from econml.dml import CausalForestDML, LinearDML
from econml.metalearners import XLearner, TLearner
# Or: from causalml.inference.meta import LRSRegressor, XGBTRegressor

xl = XLearner(models=GradientBoostingRegressor(), propensity_model=LogisticRegression())
xl.fit(Y, T=W, X=X)
cate = xl.effect(X)
```

## Bayesian Shrinkage -- The Postdoc Argument

**Dixon-Simon 1991 *Biometrics* 47:871:** exchangeable mean-zero prior on treatment-by-subgroup interaction coefficients; subgroup posteriors shrink to overall trial effect, proportional to evidence of heterogeneity. Honest about prior expectation that no qualitative interaction will hold.

**Berry, Broglio, Groshen, Berry 2013 *Clin Trials* 10:720 (NOT JCO — common citation error):** hierarchical pooling across baskets calibrated by between-basket variance tau-squared. Inflated false-positives when tau-squared mis-specified (Freidlin-Korn 2013 *Clin Cancer Res* 19:1326 critique).

**EXNEX (Neuenschwander, Wandel, Roychoudhury, Bailey 2016 *Pharm Stat* 15:123):** mixture of exchangeable (shared mean+variance) + non-exchangeable (per-basket independent) components, typically weighted 0.5/0.5. Avoids HM catastrophic borrowing when one basket truly different. Now near-standard in oncology basket trials.

**MAP priors (Schmidli et al 2014 *Biometrics* 70:1023):** meta-analytic-predictive prior. Fit random-effects meta-analysis of historical control arms, derive predictive distribution for new control arm, use as informative prior. Effective sample size from history typically 20-80% of new control arm. **Robust MAP** adds vague mixture component (weight 0.1-0.3) to guard against prior-data conflict. R `RBesT` is the canonical CRAN tool (Weber et al 2021 *J Stat Softw* 100:19).

**The Dane vs Hemmings argument:**

- Dane et al 2019 *Pharm Stat* 18:126 (EFSPI white paper): propose a standardised-effect benchmark in the neighbourhood of ~0.5σ for "noteworthy heterogeneity" (verify the exact figure against the white paper before quoting); tiered structure (key/important/exploratory); signal-vs-noise diagnostics.
- Hemmings & Koch 2019 *Pharm Stat* 18:140 commentary: **explicitly REJECT Bayesian shrinkage for signal generation** because "Bayesian shrinkage assumes treatment effects are consistent" and pre-emptively damps the very heterogeneity one is searching for. Shrinkage is endorsed only for *post-signal replication planning*.

**What postdocs argue about:** whether shrinkage is appropriate at the signal-generation stage; the prior on tau drives everything (Senn-style: tau ~ HalfNormal(0, 0.1); regulatory-tolerant: tau ~ HalfNormal(0, 0.5)).

## Multiplicity for Subgroup Analyses

**Bonferroni is rarely right** for subgroup tests because they are heavily positively correlated (same outcome, overlapping samples). Bonferroni assumes worst-case dependence; loses 30-50% power vs Hommel/resampling for ~10 demographic subgroups.

**Graphical procedures (Bretz-Maurer-Hommel)** — see clinical-biostatistics/multiplicity-graphical for full treatment. The graph for a typical subgroup analysis SAP:

- Primary endpoint at full alpha
- Alpha propagates to "key secondary" endpoints if primary rejects
- Alpha propagates to pre-specified subgroup interaction tests if primary rejects
- Discovery subgroups at most receive a small alpha slice (Dane et al recommend <=20%)

```python
# R: library(gMCP); graphView(graphMCP(...))  # interactive or programmatic
```

**Goeman, Hemerik, Solari 2021 *Ann Stat* 49:1218:** "only closed testing procedures are admissible for controlling FDP/FWER/k-FWER" — graphical, gatekeeping, Hommel, fallback are all closed tests in disguise. The graph IS the procedure.

## Pre-Specified vs Post-Hoc and EMA 2019

| Aspect | Pre-specified ("assessment") | Post-hoc ("discovery") |
|--------|------------------------------|------------------------|
| Timing | Before unblinding, in SAP | After seeing data |
| Credibility | High if biologically justified | Low; hypothesis-generating only |
| Regulatory weight per EMA 2019 | Can support labeling claims | Cannot support claims alone |
| Multiplicity adjustment | Required per SAP (graphical or Holm) | Required + heavy skepticism |
| Number expected | Few (5-15); pre-justified | Unlimited but unblindable |

**EMA 2019 Guideline on Investigation of Subgroups in Confirmatory Trials (EMA/CHMP/539146/2013, effective Aug 2019)** position: interaction tests alone are "neither necessary nor sufficient"; consistency is a holistic judgment; subgroup-specific licensing requires pre-specified evidence of differential effect PLUS biological rationale.

**Sun BMJ 2012 11 credibility criteria** (the canonical academic framework):

1. Covariate measured pre-randomisation
2. A priori hypothesis
3. Direction pre-specified
4. One of few tests with multiplicity adjustment
5. Within-study comparison (not between)
6. Interaction test significant
7. Statistically independent subgroup
8. Large effect and all subgroups reported
9. Consistent across related outcomes
10. Consistent across studies
11. Biological plausibility / indirect evidence

## Quantitative vs Qualitative Interaction

**Gail-Simon 1985 *Biometrics* 41:361:** LR test against the "all-same-direction" null. Distinguishes quantitative (magnitude varies, direction preserved) from qualitative (sign reverses) — only the latter carries decision-changing weight clinically.

**Pan-Wolfe 1997 *Stat Med* 16(14):1645, Li-Chan 2006 *J Biopharm Stat* 16(6):831:** tests for qualitative interaction of clinical significance; the original Gail-Simon normal-approximation LR is liberal at small n.

**Why qualitative interaction matters for regulators:** may warrant restricting indication to the benefiting subgroup (label carve-out).

## The Winner's Curse and Sun et al 2012

Sun et al 2012 *BMJ* systematic review found that of 207 trials reporting subgroup analyses, 64 claimed a primary-outcome subgroup effect, yet most claims failed the credibility criteria — the textbook winner's-curse signature, where effects in selected *significant* subgroups are inflated by chance and regression to the mean.

**Mechanism:** selecting a subgroup conditional on its interaction p being small selects for upward sampling fluctuations; the posterior MLE conditional on selection is biased upward by ~SE × inverse Mills ratio at the selection threshold.

**Mitigations:**

- Bayesian shrinkage (Dixon-Simon, RBesT) — posterior subgroup means shrink to overall
- Cross-validation (Athey-Wager honest splitting)
- Yadlowsky RATE 2025 *JASA* — single-p omnibus test for whether CATE ranking has predictive vs prognostic value

## Reconciliation: When Methods Disagree

| Pattern | Likely cause | Action |
|---------|--------------|--------|
| Causal forest CATE shows HTE; interaction test in logistic non-significant | Causal forest detects nonlinear/multivariate HTE; interaction test only linear bivariate | Causal forest with Yadlowsky RATE 2025 omnibus test is more sensitive; cite as discovery, not confirmatory; replicate in independent sample |
| STEPP pattern significant at one window choice; flat at another | Window-size choice (sliding vs tail-oriented) affects results (Yip 2016; tail-oriented more stable than sliding) | Pre-specify window choice in SAP; report sensitivity over choices; use permutation supremum test |
| Bayesian shrinkage (Dixon-Simon) yields null subgroup effect; frequentist sees signal | Shrinkage pulls subgroup posteriors toward overall trial effect | Bayesian shrinkage appropriate for replication PLANNING (Hemmings-Koch 2019), not signal generation; report frequentist as primary in discovery |
| MH stratified analysis gives different pooled OR than logistic with strata as covariates | MH conditions on stratum; logistic does not (assumes additivity of strata effects) | Both are valid under different assumptions; logistic preferred when stratum-treatment interaction tested formally |
| EXNEX basket trial gives different per-basket estimate under default 0.5/0.5 vs 0.3/0.7 mixture | Mixture weight controls borrowing strength (Neuenschwander 2016) | Sensitivity over weights 0.1-0.9; primary at 0.5/0.5; cite range |
| Gail-Simon qualitative interaction test rejects; LR interaction test does not | Qualitative test detects sign reversal; LR test detects magnitude | Both tests are answering different questions; qualitative interaction is regulatorily significant (label restriction) |
| Subgroup signal from data-adaptive HTE method (SIDES, causal forest) without replication | Winner's curse (Sun 2012); effects in selected subgroups are inflated | Apply Bayesian shrinkage OR honest cross-validation; report as discovery only; require Phase 3 replication |
| Causal forest test_calibration passes; RATE/AUTOC fails | test_calibration measures any signal (prognostic OR predictive); RATE measures predictive value | RATE 2025 is the modern omnibus; should replace test_calibration as primary HTE check |

## Per-Method Failure Modes

### CMH masking Simpson's paradox

- **Trigger:** Stratum-specific ORs reverse direction; pooled MH OR appears null.
- **Mechanism:** CMH pools weighted log-ORs; opposite-sign equal-magnitude cancel.
- **Symptom:** Breslow-Day p < 0.05 with visible stratum sign reversal.
- **Fix:** Report stratum-specific as primary; switch to logistic with interaction term; pooled OR invalid.

### Breslow-Day false reassurance

- **Trigger:** Few strata (k<5) or sparse strata.
- **Mechanism:** Low power; chi-square with k-1 df.
- **Symptom:** Breslow-Day p>0.5 with forest plot showing visible heterogeneity.
- **Fix:** Forest plot + LR interaction test from logistic regression.

### STEPP correlated estimates with naive CI

- **Trigger:** STEPP plot with naive pointwise CIs at each window.
- **Mechanism:** Overlapping windows share patients; estimates are correlated.
- **Symptom:** Apparent significance at individual windows that disappears under permutation.
- **Fix:** Permutation-based supremum test of pattern flatness; report supremum p, not pointwise.

### Causal forest without honest splitting

- **Trigger:** Default settings without `honesty=TRUE`.
- **Mechanism:** In-sample split selection biases leaf estimates.
- **Symptom:** Over-fit CATE; failed `test_calibration`.
- **Fix:** Always `honesty=TRUE`; tune via `tune.parameters="all"`; cite Rehill 2025 audit.

### Bayesian shrinkage damping real heterogeneity

- **Trigger:** Hierarchical model fit during signal discovery (not replication planning).
- **Mechanism:** Prior on tau forces subgroup effects toward overall.
- **Symptom:** Subgroup detected by causal forest gets shrunken to null in shrinkage analysis.
- **Fix:** Hemmings-Koch position — shrinkage for replication planning, NOT signal generation; cite Dane et al 2019 + critique.

### EXNEX with default 0.5/0.5 weights when one basket genuinely different

- **Trigger:** Default mixture weights without elicitation.
- **Mechanism:** 50% EX weight still allows substantial borrowing.
- **Symptom:** Detected differential basket "softened" by borrowing.
- **Fix:** Sensitivity analysis over mixture weights (0.1, 0.3, 0.5, 0.7, 0.9); report range.

### Stratified randomisation ignored in subgroup analysis

- **Trigger:** Site-stratified randomisation; subgroup analysis without site adjustment.
- **Mechanism:** Achieved SE smaller than calculated SE.
- **Symptom:** Over-conservative subgroup interaction tests (SE biased upward, Type-I below nominal, power loss).
- **Fix:** Include stratification factors as model covariates (Kahan-Morris 2012).

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| ~4x sample size for interaction detection vs main effect | Brookes et al 2004 *J Clin Epidemiol* 57:229 | Subgroup analyses are powered by interaction effect, not main effect |
| 0.5σ standardised effect = "noteworthy heterogeneity" | Dane et al 2019 EFSPI white paper *Pharm Stat* 18:126 | Discipline for declaring subgroup signals worth pursuing |
| Pre-specified subgroups for label claim | EMA 2019 subgroup guideline | Discovery subgroups cannot support indication restriction |
| Bonferroni: ~10 subgroups -> 30-50% power loss vs Hommel | Sarkar 1998 | Subgroup tests positively correlated; Bonferroni over-conservative |
| Honest splitting required for causal forest | Athey-Tibshirani-Wager 2019; Rehill 2025 | Without it, CIs are invalid; Rehill 2025 finds many applied papers omit it |
| 11 credibility criteria | Sun BMJ 2012 344:e1553 | Canonical academic checklist; EMA 2019 implicitly references |
| RATE/AUTOC test (Yadlowsky 2025) | *JASA* 120(549):38-51 | Single-p omnibus for HTE-ranking predictive value |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| Per-subgroup p-values compared as evidence of HTE | Statistically invalid | Single model with interaction term; report interaction p, not per-subgroup p |
| "Non-significant interaction = no HTE" | Underpowered interaction test | Cite Brookes 2004 4x rule; "absence of evidence" framing |
| Breslow-Day non-sig taken as homogeneity | Low power with few strata | Forest plot + LR interaction; cite EMA 2019 |
| STEPP with naive pointwise CIs reported | Correlated estimates | Permutation supremum test (R `stepp::test_pattern`) |
| Causal forest CIs without honest splitting | Default settings | `honesty=TRUE`; tune; calibration test; cite Rehill 2025 |
| Bayesian shrinkage for "fishing" subgroup discovery | Misapplication | Use for replication planning per Hemmings-Koch; cite Dane white paper |
| Selected subgroup effect reported without shrinkage | Winner's curse | Apply Bayesian shrinkage (RBesT) or report selection-corrected estimate |
| Subgroup p < 0.05 claimed as evidence with no multiplicity | Common SAP omission | Graphical procedure with pre-specified alpha allocation (gMCP) |
| MH pooled OR with sign-reversing stratum ORs | Simpson's paradox | Report stratum-specific; switch to interaction model |
| Causal forest tau.hat reported without RATE test | Missing modern omnibus test | Yadlowsky 2025 RATE/AUTOC; cite |

## Anticipated Reviewer Pushback

| Pushback | Response |
|----------|----------|
| "Is this pre-specified?" | Per EMA 2019, distinguish assessment (pre-specified, regulatory weight) vs discovery (post-hoc, hypothesis-generating); be explicit. |
| "Where is multiplicity correction?" | Graphical procedure with alpha allocation per SAP; cite Bretz-Maurer 2009 + gMCP. |
| "Interaction power check?" | Brookes 2004: ~4x main effect SS needed; report interaction power calculation in SAP. |
| "Is this finding clinically plausible?" | Cite biological mechanism (e.g., known pharmacogenomic pathway); cite Sun 2012 criterion 11. |
| "Winner's curse control?" | Bayesian shrinkage per Dixon-Simon (RBesT) for adjusted estimate; or honest cross-validation. |
| "Why STEPP not categorical subgroups?" | Avoids arbitrary dichotomisation of continuous biomarker; cite Bonetti-Gelber 2004. |
| "Causal forest calibration?" | `test_calibration` p-value reported; honest splitting enabled; cite Rehill 2025 audit standards. |
| "Sensitivity to prior in shrinkage analysis?" | tau ~ HalfNormal(0, 0.1), 0.25, 0.5 reported; results stable across plausible priors. |

## References

- Athey S, Tibshirani J, Wager S. 2019. Generalized random forests. *Ann Stat* 47:1148-1178.
- Berry SM, Broglio KR, Groshen S, Berry DA. 2013. Bayesian hierarchical modeling of patient subpopulations: efficient designs of Phase II oncology clinical trials. *Clin Trials* 10:720-734.
- Bonetti M, Gelber RD. 2000. A graphical method to assess treatment-covariate interactions using the Cox model on subsets of the data. *Stat Med* 19(19):2595-2609.
- Bonetti M, Gelber RD. 2004. Patterns of treatment effects in subsets of patients in clinical trials. *Biostatistics* 5:465-481.
- Bretz F, Maurer W, Brannath W, Posch M. 2009. A graphical approach to sequentially rejective multiple test procedures. *Stat Med* 28:586-604.
- Brookes ST, Whitely E, Egger M, Davey Smith G, Mulheran PA, Peters TJ. 2004. Subgroup analyses in randomized trials: risks of subgroup-specific analyses; power and sample size for the interaction test. *J Clin Epidemiol* 57:229-236. (Author surname is "Whitely", not "Whitley".)
- Dane A, Spencer A, Rosenkranz G, Lipkovich I, Parke T. 2019. Subgroup analysis and interpretation for phase 3 confirmatory trials: white paper of the EFSPI/PSI working group. *Pharm Stat* 18:126-139.
- Dixon DO, Simon R. 1991. Bayesian subset analysis. *Biometrics* 47:871-881.
- Dusseldorp E, Van Mechelen I. 2014. Qualitative interaction trees: a tool to identify qualitative treatment-subgroup interactions. *Stat Med* 33:219-237.
- EMA. 2019. Guideline on the investigation of subgroups in confirmatory clinical trials. EMA/CHMP/539146/2013.
- Foster JC, Taylor JMG, Ruberg SJ. 2011. Subgroup identification from randomized clinical trial data. *Stat Med* 30:2867-2880.
- Gail M, Simon R. 1985. Testing for qualitative interactions between treatment effects and patient subsets. *Biometrics* 41:361-372.
- Goeman JJ, Hemerik J, Solari A. 2021. Only closed testing procedures are admissible for controlling false discovery proportions. *Ann Stat* 49:1218-1238.
- Hemmings R, Koch A. 2019. Commentary on Dane et al. *Pharm Stat* 18:140-144.
- Kahan BC, Morris TP. 2012. Improper analysis of trials randomised using stratified blocks or minimisation. *Stat Med* 31:328-340.
- Künzel SR, Sekhon JS, Bickel PJ, Yu B. 2019. Metalearners for estimating heterogeneous treatment effects using machine learning. *PNAS* 116:4156-4165.
- Lipkovich I, Dmitrienko A, Denne J, Enas G. 2011. Subgroup identification based on differential effect search: SIDES. *Stat Med* 30:2601-2621.
- Neuenschwander B, Wandel S, Roychoudhury S, Bailey S. 2016. Robust exchangeability designs for early phase clinical trials with multiple strata. *Pharm Stat* 15:123-134.
- Nie X, Wager S. 2021. Quasi-oracle estimation of heterogeneous treatment effects. *Biometrika* 108:299-319.
- Pan G, Wolfe DA. 1997. Test for qualitative interaction of clinical significance. *Stat Med* 16(14):1645-1652.
- Rehill P. 2025. How do applied researchers use the causal forest? A methodological review. *Int Stat Rev*.
- Schmidli H, Gsteiger S, Roychoudhury S, O'Hagan A, Spiegelhalter D, Neuenschwander B. 2014. Robust meta-analytic-predictive priors in clinical trials with historical control information. *Biometrics* 70:1023-1032.
- Senn S. 2018. Statistical pitfalls of personalised medicine. *Nature* 563:619-621.
- Sun X, Briel M, Walter SD, Guyatt GH. 2010. Is a subgroup effect believable? Updating criteria to evaluate the credibility of subgroup analyses. *BMJ* 340:c117.
- Sun X et al. 2012. Credibility of claims of subgroup effects in randomised controlled trials: systematic review. *BMJ* 344:e1553.
- Wager S, Athey S. 2018. Estimation and inference of heterogeneous treatment effects using random forests. *JASA* 113:1228-1242.
- Wang R, Lagakos SW, Ware JH, Hunter DJ, Drazen JM. 2007. Statistics in medicine -- reporting of subgroup analyses in clinical trials. *NEJM* 357:2189-2194.
- Weber S, Li Y, Seaman J, Kakizume T, Schmidli H. 2021. Applying meta-analytic-predictive priors with the R Bayesian evidence synthesis tools. *J Stat Softw* 100:19.
- Yadlowsky S, Fleming S, Shah N, Brunskill E, Wager S. 2025. Evaluating treatment prioritization rules via rank-weighted average treatment effects. *JASA* 120(549):38-51.

## Related Skills

- clinical-biostatistics/categorical-tests - CMH, Breslow-Day, chi-square within strata
- clinical-biostatistics/effect-measures - Forest plots, OR/RR/RD reporting
- clinical-biostatistics/logistic-regression - Interaction terms in regression
- clinical-biostatistics/multiplicity-graphical - Bretz-Maurer graphical procedures (in depth)
- clinical-biostatistics/bayesian-trials - MAP/EXNEX/Berry hierarchical models (in depth)
- clinical-biostatistics/trial-reporting - CONSORT 2025 + EMA 2019 reporting of subgroup analyses
- experimental-design/multiple-testing - General multiplicity correction methods
- machine-learning/biomarker-discovery - HTE for biomarker-defined subgroups
<!-- END FILE: clinical-biostatistics/subgroup-analysis/SKILL.md -->

## 子目录：clinical-biostatistics/survival-analysis

<!-- BEGIN FILE: clinical-biostatistics/survival-analysis/SKILL.md -->
---
name: bio-clinical-biostatistics-survival-analysis
description: Performs time-to-event analysis for clinical trials including Cox proportional hazards regression with PH diagnostics, restricted mean survival time (RMST) under non-PH, competing risks via Fine-Gray vs cause-specific Cox, weighted log-rank and MaxCombo for non-proportional hazards, recurrent events (Andersen-Gill, PWP, WLW), and interval-censored data. Use when analyzing time-to-event endpoints (OS, PFS, DOR, TTR, TTNT) in oncology or other clinical trials.
tool_type: mixed
primary_tool: lifelines
---

## Version Compatibility

Reference examples tested with: lifelines 0.27+, scikit-survival 0.21+, statsmodels 0.14+, pandas 2.1+, numpy 1.26+. R packages cited (still the SOTA for survival): survival 3.8+, survRM2, cmprsk, riskRegression, mstate, flexsurv, icenReg, rpsftm.

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- R: `packageVersion('<pkg>')` then `?function_name`

If code throws ImportError, AttributeError, or TypeError, introspect the installed package and adapt the example to match the actual API rather than retrying.

# Time-to-Event Analysis for Clinical Trials

**"Analyze time-to-event endpoint"** -> Estimate a hazard, survival probability, cumulative incidence, or restricted mean time using a method calibrated to (a) whether proportional hazards holds, (b) whether competing events exist, (c) whether censoring is informative, and (d) which estimand the trial targets under ICH E9(R1).

## The Single Most Important Modern Insight -- PH Almost Never Holds

In modern oncology with checkpoint inhibitors, targeted therapies, crossover, and depleted high-risk subjects over follow-up, **proportional hazards (PH) violations are the rule, not the exception**. The Cross-Pharma NPH Working Group (Lin et al 2020 *Stat Biopharm Res*; Magirr-Burman 2021 *Stat Biopharm Res* 15(2):295) documented systematic PH violations across phase III oncology trials, particularly delayed-effect patterns from checkpoint inhibitors.

The Cox HR is a *time-averaged log-hazard ratio* under PH violation (Xu-O'Quigley 2000), which may or may not be the estimand of interest. RMST (Royston-Parmar 2013) provides a clinically interpretable, hazard-free alternative.

## Algorithmic Taxonomy

| Method | Estimand | Inference | Strength | Fails when |
|--------|----------|-----------|----------|------------|
| Log-rank (unstratified) | Test of S_A(t) = S_B(t) all t | Permutation / asymptotic chi-square | Standard; preserves Type-I under PH | Underpowered under non-PH; treats all events equally |
| Stratified log-rank | Same null within strata, pooled | Asymptotic | Preserves stratification factor from randomisation | Stratification factor must be pre-specified |
| Weighted log-rank G(rho, gamma) | Direction-specific test under non-PH | Asymptotic | High power for delayed/early/middle effects | Weight choice must match true effect time profile; chasing weight = p-hacking |
| Cox PH | Conditional log-HR | Wald, LR, score | Standard; semi-parametric; covariate adjustment | PH violation makes HR a misleading summary; check via cox.zph |
| Stratified Cox | Same; baseline hazards differ by stratum | Wald | Handles non-PH by stratification | Loses inference on stratification variable; cannot interact treatment with strata |
| Time-varying Cox (`tt()`) | Time-dependent log-HR | Wald | Quantifies non-PH explicitly | Interpretability — no single "the HR"; choose g(t) carefully |
| Flexible parametric (Royston-Parmar) | Time-varying log-HR via splines | Wald | Smooth S(t), HR(t); supports extrapolation | Spline choice affects results; software in R `stpm2/stpm3` |
| RMST | Difference in mean survival truncated at tau | Wald with delta or pseudo-obs regression | Hazard-free; clinically interpretable in time units | tau choice; min follow-up across arms constrains tau |
| MaxCombo | Maximum over weighted log-rank family | Asymptotic multivariate normal | Robust to range of NPH patterns | Can reject in opposite directions on same data (Magirr 2022 critique) |
| Fine-Gray subdistribution HR | Conditional subdistribution HR | Wald | Direct CIF modeling | Andersen-Keiding 2012 critique: violates causal hazard semantics |
| Cause-specific Cox | Conditional cause-specific HR | Wald | Causally interpretable | Predicts hazards, not CIFs; need both for CIF prediction |
| Multi-state Cox (mstate) | Transition-specific HRs | Wald | Subsumes competing risks; handles relapse/remission | More complex; more parameters to estimate |
| Andersen-Gill (recurrent) | Rate ratio | Robust (cluster) Wald | Most efficient under exchangeability | Assumes exchangeable events |
| PWP (recurrent) | Conditional event-order HR | Stratified Wald | Handles event-order qualitative heterogeneity | More strata = more parameters; smaller per-stratum n |
| Interval-censored Cox (NPMLE) | Cumulative hazard | Likelihood ratio | Correct for periodic-assessment data | Slower; software in R `icenReg` |

**Postdoc reading list:**

- Royston-Parmar 2013 *BMC Med Res Methodol* 13:152 (RMST as primary)
- Uno et al 2014 *JCO* 32:2380 (RMST in oncology)
- Andersen-Keiding 2012 *Stat Med* 31:1074 (Fine-Gray semantic critique)
- Putter-Schumacher-van Houwelingen 2020 *Biom J* 62:790 (Fine-Gray revisited; reduction factor)
- Putter-Fiocco-Geskus 2007 *Stat Med* 26:2389 (competing risks tutorial)
- Magirr-Burman 2021 *Stat Biopharm Res* 15(2):295 (MaxCombo critique)
- Grambsch-Therneau 1994 *Biometrika* 81:515 (scaled Schoenfeld residuals)
- Buyse-Molenberghs 1998 *Biometrics* 54:1014 (PFS-OS surrogacy framework)
- Sun et al 2021 *Pharm Stat* 20:793 (estimands in oncology; ICH E9(R1) ICE strategies)
- Sun 2006 *The Statistical Analysis of Interval-Censored Failure Time Data* (Springer)

## Decision Tree by Scenario

| Scenario | Recommended approach | Why |
|----------|---------------------|-----|
| OS, drug expected to extend survival uniformly, PH plausible | Stratified log-rank + Cox HR with cox.zph diagnostic | Standard regulatory approach; pre-specify stratification factors from randomisation |
| PFS in immuno-oncology with expected delayed separation | MaxCombo with pre-specified G(0,0), G(0,1), G(1,0), G(1,1); RMST as sensitivity | Robust to NPH; explicit direction check (Magirr-Burman 2021) |
| OS with crossover to active arm | Treatment policy estimand (ITT) primary; RPSFT/IPCW as sensitivity for hypothetical | ICH E9(R1); FDA/EMA accept both, ITT is primary |
| Time-to-event with assessment-schedule artifact (periodic scans) | Interval-censored Cox (R `icenReg::ic_par`) | Standard right-censoring at midpoint is biased |
| DOR (duration of response) | KM among responders; censor at next-therapy/death/dropout per pre-specified estimand | Weber 2023 *Pharm Stat*; responder-conditioned = doubly post-randomisation |
| Competing risk: drug efficacy on event A in context of high event-B mortality | Cause-specific Cox for A AND for B; report both; CIF via Aalen-Johansen | Andersen-Keiding 2012; Fine-Gray SHR is not causal |
| Prediction of CIF for clinical decision | Fine-Gray for CIF estimate; cause-specific Cox for etiology | Putter-Fiocco-Geskus 2007 split |
| Multi-state model (alive -> relapse -> death) | mstate framework with transition-specific Cox models | Subsumes competing risks |
| Recurrent events (exacerbations, hospitalisations) | Andersen-Gill with robust SE; cite event-order assumption | Most efficient; falls back to PWP if order matters |
| Single-arm OS extrapolation for HTA | Flexible parametric (Royston-Parmar) + external information | Smooth tail; supports extrapolation beyond trial follow-up |
| Non-PH with crossing hazards | RMST with pre-specified tau; OR multi-state model | HR loses meaning under crossing |

## Cox PH Diagnostics -- The Therneau-Grambsch Test (and Its Pitfalls)

**Goal:** Detect violations of the proportional hazards assumption that would invalidate the Cox HR as a meaningful summary statistic.

**Approach:** Compute scaled Schoenfeld residuals (Grambsch-Therneau 1994); regress against a time-transform g(t) under H0 of zero slope; supplement the asymptotic p-value with a graphical residual plot since the test is sensitive to g(t) choice and sample-size dependent.

```python
from lifelines import CoxPHFitter
from lifelines.statistics import proportional_hazard_test

cph = CoxPHFitter()
cph.fit(df, duration_col='time', event_col='event', formula='treatment + age + baseline_score')
cph.print_summary()

# Schoenfeld residuals PH test (lifelines)
results = proportional_hazard_test(cph, df, time_transform='rank')
print(results.summary)

# In R: cox.zph(coxph_fit) returns same with KM transform as default
```

**The g(t) choice trap (Park-Hendry 2015 *American Journal of Political Science*):** the test power depends critically on g(t). KM transform, identity, log, and rank give materially different p-values. With n > 5000 even trivial deviations reject; with n < 100 the test misses meaningful violations.

**Critical interpretation rule: a global p > 0.05 does NOT mean PH holds — it means the null cannot be rejected.** The graphical diagnostic is more informative — a flat smoothed line is the target. Use cox.zph as a *failure detector*, not a *PH validator*.

```python
# Plot scaled Schoenfeld residuals (lifelines)
cph.check_assumptions(df, p_value_threshold=0.05, show_plots=True)
```

### Fixes when PH violated

1. **Stratify** on the violating covariate (loses inference on it)
2. **Time-dependent coefficients:** `coxph(Surv(t, d) ~ x + tt(x), tt=function(x,t,...) x*log(t))` in R; lifelines: `formula='treatment * time'`
3. **Royston-Parmar flexible parametric** (R `flexsurv::flexsurvspline` or `rstpm2::stpm2`)
4. **RMST** as primary; HR as secondary

## Restricted Mean Survival Time (RMST) -- The Modern Alternative

**Royston-Parmar 2013 + Uno 2014 case:** RMST(tau) = E[min(T, tau)] = integral from 0 to tau of S(t) dt = area under KM curve up to tau. The difference RMST_A(tau) - RMST_B(tau) is a **time gained in months** -- clinically interpretable, requires no PH assumption, always estimable up to the minimum of the largest follow-up across arms.

```python
# Python: rmst via lifelines or manual
from lifelines.utils import restricted_mean_survival_time
from lifelines import KaplanMeierFitter

kmf_A = KaplanMeierFitter().fit(df[df['arm']=='A']['time'], event_observed=df[df['arm']=='A']['event'])
kmf_B = KaplanMeierFitter().fit(df[df['arm']=='B']['time'], event_observed=df[df['arm']=='B']['event'])
tau = 36  # months; pre-specified
rmst_A = restricted_mean_survival_time(kmf_A, t=tau)
rmst_B = restricted_mean_survival_time(kmf_B, t=tau)
print(f'RMST diff: {rmst_A - rmst_B:.2f} months')

# R: survRM2::rmst2(time, status, arm, tau=36) is the standard
```

### The tau (truncation time) choice

- **Statistical constraint:** tau <= min(largest follow-up time in each arm) to avoid extrapolation (Tian et al 2020 *Biometrics* gives rigorous treatment)
- **Clinical constraint:** tau should reflect a clinically meaningful horizon (5-year OS in adjuvant; 24-month PFS in metastatic)
- **Data-dependent tau inflates Type-I error** — MUST be pre-specified in SAP. Post-hoc tau tuning to chase significance is p-hacking.

### Pseudo-observation regression (Andersen-Hansen-Klein 2004)

For each subject i, compute jackknife pseudo-value θ_i(tau) = n·RMST(tau) - (n-1)·RMST_{-i}(tau). Regress pseudo-values on covariates via GEE — enables RMST regression WITH covariate adjustment, including time-varying covariates, no PH assumption.

R implementation: `pseudo::pseudomean()` + GEE via `geepack::geeglm()`.

**Lambert critique (postdoc reading):** Paul Lambert (`stpm3` author) is on record that RMST is "not unambiguously simpler than HR for clinicians." HR has 50-year pedagogy lead. RMST is cumulative (not instantaneous) and cannot detect crossing hazards beyond chosen tau. The argument for RMST is hazard-free interpretability under non-PH; the argument against is communication and tau sensitivity.

## Competing Risks -- The Andersen-Keiding Framework

### Fine-Gray subdistribution hazard

```python
# Python: scikit-survival or lifelines (limited support); R is the SOTA
# R: library(cmprsk); crr(time, fstatus, cov, failcode=1, cencode=0)
# R: library(riskRegression); FGR(formula, data=df, cause=1)
```

**Fine-Gray 1999** introduced subdistribution hazard lambda^FG(t) = -d/dt log[1 - F_1(t)] where F_1 is CIF for cause 1. The proportional subdistribution hazards model places covariates on this hazard. Subjects who experience competing events remain in the risk set with IPCW weighting — mathematically convenient but **conceptually weird**.

**The Andersen-Keiding 2012 critique** (*Stat Med* 31:1074): Fine-Gray subdistribution hazard violates the three principles for valid hazard functionals:

1. Hazard must be a real instantaneous risk among those truly at risk -> FG keeps dead competing-event subjects "at risk"
2. Covariate effects must be interpretable as causal -> FG coefficients confound the competing-event hazard
3. Hazard must support landmarking (conditioning on survival to s) -> FG does not

**The competing-risk confounding trap** (Putter-Schumacher-van Houwelingen 2020 *Biom J* 62:790; the reduction factor decomposition makes it explicit): any covariate that increases the cause-specific hazard of competing event A will *decrease* the subdistribution hazard for event B simply because A removes subjects from the population at risk of B. A Fine-Gray "protective" effect on B may be an iatrogenic killer via A.

### Practical rule (Putter-Fiocco-Geskus 2007)

- **For prediction of CIF (cumulative incidence)** -> Fine-Gray is fine; report CIF curves and SHR
- **For etiology / causal effect on the event** -> use cause-specific Cox (treat competing events as censoring); report cause-specific HRs for BOTH event of interest AND competing events
- **For multi-state semantics** (alive -> relapse -> death) -> use multi-state framework with transition-specific Cox models

### The CIF is always estimable

Aalen-Johansen estimator (multi-state generalisation of KM) gives the CIF non-parametrically. **The KM estimator is biased upward in the presence of competing risks** — it treats competing events as non-informative censoring and overestimates 1 - CIF.

```r
# R: library(mstate); msfit(coxph_fit, newdata, trans); probtrans(msfit_obj)
# R: library(survival); survfit(Surv(time, event_factor) ~ 1) with multi-state Surv
```

## Log-Rank Variants and MaxCombo

```python
from lifelines.statistics import logrank_test, multivariate_logrank_test

# Stratified log-rank (lifelines uses `weightings=` -- note plural)
results = multivariate_logrank_test(
    df['time'], df['arm'], df['event'], weightings='peto'
)
# weightings options (lifelines 0.27+): None, 'wilcoxon', 'tarone-ware',
# 'peto', 'fleming-harrington' (also accepts kwargs for Fleming-Harrington p, q)
```

| Test | Citation | When to use |
|------|----------|-------------|
| Standard log-rank (G(0,0)) | Mantel 1966 | PH holds |
| Wilcoxon | Wilcoxon 1945 | Down-weights late events; early-effect detection |
| Tarone-Ware | Tarone-Ware 1977 | Compromise |
| Peto-Peto | Peto-Peto 1972, Prentice 1978 | Robust to ties and censoring distribution differences between arms |
| Fleming-Harrington G(rho, gamma) | Fleming-Harrington 1981 | Direction-specific: G(0,1) for late-emphasis (delayed effects), G(1,0) for early |
| MaxCombo | Karrison 2016 | Take maximum over family; control multiplicity via joint MVN |

### The MaxCombo controversy

**Magirr-Burman 2021 *Stat Biopharm Res* 15(2):295**: MaxCombo can reject the null in **opposite directions** on the same dataset. Formally, it rejects the strong null H_0: S_A(t) = S_B(t) for all t, but the rejection direction is determined by the dominant weight, which can flip across portions of the curve. **KEYNOTE-042 demonstration**: MaxCombo simultaneously favouring pembrolizumab AND chemo depending on weight choice.

**Cross-Pharma NPH Working Group recommendation:** MaxCombo with directionality constraints — require positive z-statistic at the late-emphasis weight before declaring superiority; report the dominant weight and its direction.

## Interval Censoring -- When Standard Right-Censoring Is Wrong

**PFS is REALLY interval-censored** — events known only between consecutive RECIST scans. The convention is to treat it as right-censored at midpoint or first-PD-scan date. This is a long-standing methodological compromise defensible only when scan intervals are short and balanced across arms.

```r
# R: library(icenReg)
# fit_ic <- ic_par(cbind(left, right) ~ treatment + age, data=df, dist='weibull', model='ph')
# ic_sp() for semi-parametric; ic_npar() for NPMLE
```

**Sun 2006** *The Statistical Analysis of Interval-Censored Failure Time Data* (Springer) is the canonical reference. NPMLE via Turnbull's algorithm; Cox-like regression via Finkelstein 1986 / Pan 1999 EM algorithms.

**When to switch from right-censored midpoint to interval-censored:** scan intervals > 4 weeks; scan timing differs between arms (open-label trials with potential differential ascertainment); regulatory submission where 2-3% effect-size shift matters.

## Recurrent Events -- AG vs PWP vs WLW

| Model | Risk set | Baseline hazard | Best when |
|-------|----------|-----------------|-----------|
| Andersen-Gill 1982 | Total time; subject at risk continuously between events | Common (counting process) | Events exchangeable; rate model; no event-order effect |
| PWP gap-time (Prentice-Williams-Peterson 1981) | Stratified by event number; subject enters stratum k after event k-1 | Stratum-specific | Event-order matters; later events qualitatively different |
| WLW (Wei-Lin-Weissfeld 1989) | Marginal -- separate Cox per event order | Per-event-order | Multiple types of events; uses sandwich variance |

```python
# Python: lifelines does not have native AG; use coxph with (start, stop, event) format
# R: coxph(Surv(start, stop, event) ~ trt + cluster(id), data=long_df) for AG
# R: + strata(enum) for PWP
```

**Box-Steffensmeier critique:** WLW is often misused — fitting separate Cox to "time to 2nd event" treats it as a first-event problem rather than conditional on prior history, inflating effect estimates. PWP-gap-time is the cleanest conditional model. AG most efficient when exchangeability holds.

**Modern advice (Rogers et al 2014; Cook-Lawless 2007 book):** AG with robust variance as default; PWP if events qualitatively heterogeneous; avoid WLW unless events are truly distinct types.

## Oncology PFS/OS Estimands -- The 2024 Reality

Per ICH E9(R1), the same PFS dataset yields different HRs depending on censoring rules. Each rule corresponds to a different intercurrent-event strategy:

| Censoring rule | ICE strategy | Estimand |
|----------------|-------------|----------|
| Censor at last assessment before missing visits | Hypothetical (had visit not been missed) | What would PFS be if visits never missed? |
| Censor at start of new anticancer therapy | Hypothetical (no subsequent therapy) | What would PFS be without rescue? |
| Count subsequent therapy as event | Composite (subsequent therapy = treatment failure) | Treatment-failure-free survival |
| No censoring (event = last assessment + progression) | Treatment policy | Real-world PFS with policy of allowing rescue |

**The 2024 European Journal of Cancer demonstration (PMID 38547775):** two sets of censoring rules — FDA-favoured vs trialist-favoured — applied to the *same* PFS data shifted median PFS from 32 to 43 months in the experimental arm with no change in control. This is the estimand changing, not analytic artefact.

**Fleming 2025 argument:** handle subsequent therapy by treatment-policy -- continue follow-up rather than censor at the switch -- keeping progression + death as the composite endpoint to preserve ITT. Controversial because not censoring at subsequent therapy blurs interpretation as "tumor growth control."

### Informative censoring -- detection and handling

**The mechanism:** standard right-censored Cox / KM assumes censoring is non-informative (the censoring process is unrelated to the underlying failure time after conditioning on observed covariates). **When this fails, KM is biased upward** in the arm with informative censoring -- patients who drop out due to lack of efficacy or toxicity are precisely the ones who would have failed early.

**TROPiCS-02 informative censoring (Li et al 2023 *JCO* 41:1629):** "evaporative cooling" of progression events. Patients on the toxic arm discontinue and are censored BEFORE the next protocol-mandated scan that would have captured progression; KM biases PFS upward in the toxic arm. Templeton 2020 *Nat Rev Clin Oncol* and Campigotto-Weller 2014 *JCO* are foundational citations.

**Detection workflow:**

1. **Tabulate censoring reasons by arm** from CDISC DS (Disposition) or ADaM ADTTE CNSR integer values:
   - CNSR=1 (lost to follow-up): symmetric across arms = OK
   - CNSR=2 (withdrew consent): if asymmetric, investigate why
   - CNSR=3 (admin EoS): symmetric by definition
   - CNSR=4 (subsequent therapy initiated): differential is the canonical informative pattern
   - CNSR=5+ (toxicity discontinuation): differential is highly informative

2. **Compare KM curves for censoring distribution** by arm. If "time-to-censoring" KM differs by arm in same direction as outcome, suspect informative censoring.

3. **Cox-Snell or Schoenfeld residuals on censoring-as-event model**: if treatment is significantly associated with censoring hazard, censoring is informative.

**Handling strategies (per ICH E9(R1) and Sun 2021):**

| Strategy | When to use | Implementation |
|----------|-------------|----------------|
| Composite endpoint (treatment-policy) | ICE has clinical meaning (subsequent therapy = treatment failure) | Re-define event as "first of (progression OR subsequent therapy OR death)"; eliminates need for censoring assumption |
| IPCW with stabilised weights (Robins 1992) | Hypothetical estimand under "no informative dropout" | R `ipw::ipwtm` or custom: weight = inverse probability of remaining uncensored given baseline + time-varying covariates |
| Sensitivity: worst-case / best-case imputation | Bounding the true effect under informative censoring | Censored patients = events at censoring date (worst case); or remain at risk (best case); report range |
| Multistate model | Multiple competing causes of censoring | `mstate` for transition-specific Cox; handles death + dropout + subsequent therapy as separate states |
| RPSFT / structural nested failure time | Crossover-induced informative censoring | R `rpsftm` package; FDA / EMA acceptable for OS hypothetical estimand under crossover |

**IPCW workflow (stabilised weights per Robins-Finkelstein 2000):**

```r
# Stabilised IPCW: w(t) = S_num(t) / S_denom(t)
# where S_denom predicts remaining-uncensored given baseline + time-varying covariates,
# and S_num predicts remaining-uncensored given treatment alone (numerator for stabilisation)

# Step 1: fit censoring (NOT event) hazard models
# Note: outcome variable for these models is "1 if censored, 0 if event or still at risk"
denom_cens <- coxph(Surv(time, censored) ~ treatment + age + baseline_severity, data=df)
num_cens   <- coxph(Surv(time, censored) ~ treatment, data=df)

# Step 2: compute survival probabilities (NOT hazards) for "remaining uncensored"
# basehaz + linear predictor -> S(t) per subject; the `survfit` + `summary` API gives S_i(t_i)
S_denom <- summary(survfit(denom_cens, newdata=df), times=df$time)$surv
S_num   <- summary(survfit(num_cens,   newdata=df), times=df$time)$surv

# Step 3: stabilised IPCW weight per subject at their observed time
df$ipcw <- S_num / S_denom

# Step 4: weighted Cox for the event of interest with robust SE
fit_ipcw <- coxph(Surv(time, event) ~ treatment + age + baseline_severity,
                  data=df, weights=df$ipcw, robust=TRUE)
```

**Note:** in practice use the `ipw::ipwtm` (or `ipwExt`) wrapper which handles the time-varying weights and stabilisation correctly; the pseudocode above shows the underlying machinery. Verify weight distribution: median weight near 1, no extreme values (>10 indicates near-violation of positivity).

**Operational rule:** for any TTE primary analysis where DS shows differential censoring reasons by arm, the regulatory expectation is (1) tabulate reasons in CSR, (2) report sensitivity under IPCW or composite, (3) discuss whether primary HR/RMST changes under sensitivity.

## ADaM ADTTE -- The CNSR Convention Trap

**CDISC ADTTE convention: CNSR = 0 for events, positive integers for censoring reasons** (1 = lost to follow-up, 2 = withdrew consent, 3 = admin EoS, 4 = subsequent therapy, etc.). **Opposite to most stat packages** which use 1 = event.

```python
# Convert ADTTE for Python / R
import pandas as pd

adtte = pd.read_csv('ADTTE.csv')
adtte['event'] = (adtte['CNSR'] == 0).astype(int)  # 1 = event for survival packages
adtte['time'] = adtte['AVAL']  # AVAL is in days/months per AVALU
```

This is a perpetual bug source. See clinical-biostatistics/cdisc-data-handling for the full ADTTE specification.

## Per-Method Failure Modes

### Cox PH violation undetected

- **Trigger:** Significant treatment HR reported without cox.zph diagnostic
- **Mechanism:** Cox HR is a time-averaged log-HR under PH violation; the "the HR" interpretation breaks
- **Symptom:** Hazard plots show crossing; cox.zph rejects PH; KM curves diverge then converge
- **Fix:** Report cox.zph result; switch to RMST or time-varying Cox; cite Grambsch-Therneau 1994

### Fine-Gray reported as causal effect

- **Trigger:** Fine-Gray SHR interpreted as "treatment effect on event of interest"
- **Mechanism:** SHR confounds with competing-event hazard (Andersen-Keiding 2012)
- **Symptom:** SHR interpretation contradicts cause-specific Cox results; reviewer confusion
- **Fix:** Use cause-specific Cox for etiology; Fine-Gray for CIF prediction only; report both per Putter-Fiocco-Geskus 2007

### KM curve biased upward under competing risks

- **Trigger:** KM applied to event of interest treating competing events as non-informative censoring
- **Mechanism:** KM estimates 1 - cause-specific hazard cumulative; competing events deplete denominator
- **Symptom:** KM survival exceeds Aalen-Johansen 1 - CIF estimate
- **Fix:** Use Aalen-Johansen estimator for CIF; never KM in competing-risk setting

### MaxCombo direction flipping

- **Trigger:** MaxCombo significant; direction not pre-specified
- **Mechanism:** MaxCombo's family can include weights that favour opposite directions
- **Symptom:** Different reports show opposite "winner" depending on weight choice
- **Fix:** Pre-specify directional constraints; require positive z at late-emphasis weight before claiming superiority; cite Magirr-Burman 2021

### Tau chosen post-hoc to favour significance

- **Trigger:** RMST tau adjusted after seeing data
- **Mechanism:** Selection bias; tau-tuning is a flavour of p-hacking
- **Symptom:** Sponsor's RMST result differs from independently re-analysed with pre-specified tau
- **Fix:** Pre-specify tau in SAP; cite Tian 2020 *Biometrics*

### Right-censored midpoint for interval-censored PFS

- **Trigger:** Scan intervals long or differential between arms; standard right-censored Cox applied
- **Mechanism:** Midpoint imputation is biased; SE underestimates
- **Symptom:** Replication with interval-censored Cox gives different point estimate and wider CI
- **Fix:** R `icenReg::ic_par` or `ic_sp`; Sun 2006

### CNSR convention confusion

- **Trigger:** ADTTE CNSR=1 passed to R `survival::Surv(time, event)` expecting event=1
- **Mechanism:** Censoring/event role reversed
- **Symptom:** "Event count" matches censoring count from CSR; nonsensical HR
- **Fix:** Always convert: `event = (CNSR == 0).astype(int)`; cite ADaM IG v1.3

## Reconciliation: When Methods Disagree

| Pattern | Likely cause | Action |
|---------|--------------|--------|
| Cox HR significant, RMST difference non-significant | HR is time-averaged log-HR under PH violation; RMST captures cumulative effect | If PH violated, RMST is the more interpretable summary; HR may be artifact of late-event preponderance |
| MaxCombo rejects null but direction depends on weight | MaxCombo's rejection direction is determined by dominant weight; can flip across weight choices (Magirr-Burman 2021) | Pre-specify directional constraint (positive z at late-emphasis weight) before declaring superiority; do NOT post-hoc select winning weight |
| Fine-Gray SHR vs cause-specific Cox HR conflict on direction | Fine-Gray confounds with competing-event hazard; cause-specific isolates causal effect on event of interest (Andersen-Keiding 2012) | For causal claims use cause-specific Cox; Fine-Gray for CIF prediction only; report both per Putter-Fiocco-Geskus 2007 |
| Stratified log-rank p < unstratified p | Stratification removes between-stratum variance; correct standard error smaller | Stratified analysis matches randomisation; unstratified is over-conservative (SE biased upward, power loss) per Kahan-Morris 2012 |
| KM survival curve vs Aalen-Johansen 1-CIF disagree in competing-risks setting | KM treats competing events as non-informative censoring (biased upward) | Use Aalen-Johansen for CIF; never KM in competing-risk setting |
| Schoenfeld-formula SS insufficient at trial end (events under-collected) | Non-PH (immuno-oncology delayed effect) violates Schoenfeld assumption; under-estimates events 20-50% | Re-power using Lakatos 1988 or simulation under expected HR(t); cite Lin 2020 NPH Working Group |
| Right-censored midpoint Cox HR vs interval-censored Cox HR differ | Midpoint imputation biased when scan intervals long or asymmetric | Switch to interval-censored Cox via icenReg when scan intervals > 4 weeks or differ by arm |
| ADTTE CNSR=1 produces nonsensical results | CDISC convention reversal: CNSR=0 means event in ADaM | Always convert: `event = (CNSR == 0).astype(int)` before stat-package call |

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| cox.zph p > 0.05 is NOT proof of PH | Grambsch-Therneau 1994; Park-Hendry 2015 | Failure detector, not validator |
| RMST tau <= min(largest follow-up per arm) | Tian 2020 *Biometrics* | Avoid extrapolation; tau pre-specified in SAP |
| MaxCombo with directional constraint | Magirr-Burman 2021 *Stat Biopharm Res* 15(2):295 | Prevents opposite-direction rejections |
| Cause-specific Cox for etiology; FG for CIF prediction | Putter-Fiocco-Geskus 2007 | Andersen-Keiding 2012 critique |
| Scan intervals > 4 weeks -> interval-censored analysis | Sun 2006 | Midpoint right-censoring is biased |
| 10 events per covariate for Cox | Peduzzi 1995 *J Clin Epidemiol* | Below this, bias and overfitting |
| Schoenfeld 1981 events formula assumes PH | Schoenfeld 1981 | Under non-PH, under-estimates required events by 20-50%; cite Lakatos 1988 for non-PH SS |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| Cox HR reported with cox.zph p < 0.001 ignored | Diagnostic skipped | Report RMST or time-varying Cox; cite Therneau-Grambsch |
| KM curve labeled "survival from event of interest" with competing risks | Bias upward | Aalen-Johansen CIF; never KM with competing risks |
| Fine-Gray HR reported as "treatment effect" | Misinterpretation of SHR | Cite Andersen-Keiding; report cause-specific too |
| MaxCombo with no direction restriction | Direction-flipping risk | Pre-specify constraints (Magirr-Burman 2021) |
| ADTTE CNSR=1 used as "1=event" | Convention reversal | `event = (CNSR == 0).astype(int)` |
| PFS midpoint right-censored without interval-censored sensitivity | Scan-schedule bias | Interval-censored analysis when scan intervals long |
| Stratified randomisation factor not in Cox | Over-conservative (SE biased upward, Type-I below nominal, power loss) | Include strata via `strata()` or as covariate |
| Schoenfeld SS calculation in immuno-oncology | PH assumption violated | Simulate under expected hazard pattern (Lakatos 1988); use MaxCombo SS |
| tau set to longest follow-up post-hoc | RMST p-hacking | Pre-specify tau in SAP; cite Tian 2020 |
| Recurrent-event WLW with naive "time to 2nd event" | Inflated effect | AG with robust SE, or PWP gap-time |

## Anticipated Reviewer Pushback

| Pushback | Response |
|----------|----------|
| "PH assumption check?" | cox.zph result reported with caveat that p>0.05 doesn't prove PH; graphical diagnostic in supplement |
| "Why RMST not HR?" | PH violated; HR is misleading time-average; RMST is hazard-free in interpretable time units (Royston-Parmar 2013) |
| "How was tau chosen?" | Pre-specified in SAP based on clinical horizon AND statistical constraint min(largest follow-up); cite Tian 2020 |
| "Fine-Gray or cause-specific Cox?" | Both reported per Putter 2007: FG for CIF prediction, cause-specific Cox for etiology; cite Andersen-Keiding 2012 |
| "MaxCombo direction validation?" | Pre-specified directional constraint; positive z at late-emphasis weight required; cite Magirr-Burman 2021 |
| "Crossover handling?" | ITT primary (treatment policy); RPSFT or IPCW as sensitivity (hypothetical); cite Robins-Tsiatis |
| "Informative censoring?" | Censoring reasons tabulated by arm; symmetric -> no concern; differential -> sensitivity under composite or worst-case |
| "ADTTE CNSR convention?" | Explicit conversion documented: ADaM CNSR=0 means event; converted to event=1 for downstream R/Python |
| "Schoenfeld SS under expected NPH?" | Simulation-based SS using expected hazard pattern (Lakatos 1988); NOT Schoenfeld formula |
| "Multi-state vs Fine-Gray?" | Multi-state when alive->relapse->death is the disease model; Fine-Gray only for CIF prediction of one cause |

## References

- Andersen PK, Keiding N. 2012. Interpretability and importance of functionals in competing risks and multistate models. *Stat Med* 31:1074-1088.
- Andersen PK, Hansen MG, Klein JP. 2004. Regression analysis of restricted mean survival time based on pseudo-observations. *Lifetime Data Anal* 10:335-350.
- Buyse M, Molenberghs G. 1998. Criteria for the validation of surrogate endpoints in randomized experiments. *Biometrics* 54:1014-1029.
- Cox DR. 1972. Regression models and life-tables. *JRSS-B* 34:187-220.
- Fine JP, Gray RJ. 1999. A proportional hazards model for the subdistribution of a competing risk. *JASA* 94:496-509.
- Karrison TG. 2016. Versatile tests for comparing survival curves based on weighted log-rank statistics. *Stat J* 16:678-690.
- Lakatos E. 1988. Sample sizes based on the log-rank statistic in complex clinical trials. *Biometrics* 44:229-241.
- Sun S, Weber HJ, Butler E, Rufibach K, Roychoudhury S. 2021. Estimands in hematologic oncology trials. *Pharm Stat* 20(4):793-805.
- Magirr D, Burman CF. 2021. The strong null hypothesis and the MaxCombo test. *Stat Biopharm Res* 15(2):295-296. (Earlier "Cherry-picking in survival analysis" attribution was a blog post, Oct 2022.)
- Mantel N. 1966. Evaluation of survival data and two new rank order statistics arising in its consideration. *Cancer Chemotherapy Reports* 50:163-170.
- Peduzzi P et al. 1995. Importance of events per independent variable in proportional hazards analysis. *J Clin Epidemiol* 48:1503-1510.
- Putter H, Fiocco M, Geskus RB. 2007. Tutorial in biostatistics: competing risks and multi-state models. *Stat Med* 26:2389-2430.
- Putter H, Schumacher M, van Houwelingen HC. 2020. On the relation between the cause-specific hazard and the subdistribution rate for competing risks data: the Fine-Gray model revisited. *Biom J* 62:790-807.
- Royston P, Parmar MKB. 2013. Restricted mean survival time: an alternative to the hazard ratio. *BMC Med Res Methodol* 13:152.
- Schoenfeld DA. 1981. The asymptotic properties of nonparametric tests for comparing survival distributions. *Biometrika* 68:316-319.
- Sun J. 2006. *The Statistical Analysis of Interval-Censored Failure Time Data*. Springer.
- Grambsch PM, Therneau TM. 1994. Proportional hazards tests and diagnostics based on weighted residuals. *Biometrika* 81:515-526.
- Tian L, Jin H, Uno H, Lu Y, Huang B, Anderson KM, Wei LJ. 2020. On the empirical choice of the time window for restricted mean survival time. *Biometrics* 76(4):1157-1166.
- Uno H et al. 2014. Moving beyond the hazard ratio in quantifying the between-group difference in survival analysis. *JCO* 32:2380-2385.
- Xu R, O'Quigley J. 2000. Estimating average regression effect under non-proportional hazards. *Biostatistics* 1:423-439.

## Related Skills

- clinical-biostatistics/effect-measures - HR vs RMST as effect measures; CI methods
- clinical-biostatistics/trial-reporting - ICH E9(R1) estimand framework for time-to-event
- clinical-biostatistics/missing-data-sensitivity - Informative censoring and tipping-point for survival
- clinical-biostatistics/cdisc-data-handling - ADTTE structure and CNSR convention
- clinical-biostatistics/subgroup-analysis - Subgroup HTE for survival endpoints
- clinical-biostatistics/power-and-sample-size - Schoenfeld and Lakatos sample size for TTE
- clinical-biostatistics/multiplicity-graphical - Co-primary survival endpoints
- machine-learning/survival-analysis - Predictive survival models and ML extensions
<!-- END FILE: clinical-biostatistics/survival-analysis/SKILL.md -->

## 子目录：clinical-biostatistics/trial-reporting

<!-- BEGIN FILE: clinical-biostatistics/trial-reporting/SKILL.md -->
---
name: bio-clinical-biostatistics-trial-reporting
description: Prepares statistical reports for clinical trials following CONSORT 2025, SPIRIT 2025, ICH E9(R1) estimands, and FDA 2023 covariate adjustment guidance. Covers Table 1 generation, analysis populations (ITT/FAS/PP/Safety), the 5 ICH E9(R1) intercurrent-event strategies, MMRM under MAR (mmrm), reference-based MI (rbmi J2R/CR/CIR), Permutt tipping-point sensitivity, and Rubin's-rules vs frequentist variance debate. Use when preparing regulatory submissions, defining estimands, or implementing missing-data sensitivity analyses.
tool_type: python
primary_tool: tableone
---

## Version Compatibility

Reference examples tested with: tableone 0.9+, statsmodels 0.14+, scikit-learn 1.4+, pandas 2.1+, numpy 1.26+. R packages cited (essential for current regulatory work): mmrm 0.3+ (Roche/openpharma), rbmi 1.5+ (Roche/Bayer via insightsengineering), gMCP, RBesT.

Before using code patterns, verify installed versions match. If versions differ:
- Python: `pip show <package>` then `help(module.function)` to check signatures
- R: `packageVersion('<pkg>')` then `?function_name`

If code throws ImportError, AttributeError, or TypeError, introspect the installed package and adapt the example to match the actual API rather than retrying.

# Trial Reporting Under CONSORT 2025 + ICH E9(R1)

**"Prepare a clinical trial statistical report"** -> Define the estimand explicitly per ICH E9(R1); execute a covariate-adjusted primary analysis targeting the right summary measure; pre-specify the missing-data strategy and run regulatory-grade sensitivity analyses; structure the output per CONSORT 2025 and the new SPIRIT 2025 alignment.

## The Single Most Important Methodological Shift -- The Estimand Comes First

**Kahan, Cro, Li, Harhay 2023 *Am J Epidemiol* 192:987 ("Eliminating Ambiguous Treatment Effects Using Estimands"):** 98% of published trial reports do not describe what the reported treatment effect represents. 54% of trials: impossible to deduce the estimand from reported methods. In 74% of trials submitted for regulatory approval 1996-2017, "what-if" hypothetical effects were used but only 2 trials explained this.

**The framework:** ICH E9(R1) Addendum (November 2019, EMA effective 30 July 2020, FDA May 2021) defines an estimand as the precise specification of what is being estimated, via five attributes:

1. **Treatment condition** -- what is being compared
2. **Population** -- which patients
3. **Endpoint** -- which variable
4. **Population-level summary measure** -- mean diff, OR, HR, RD
5. **Intercurrent-event (ICE) handling strategy** -- one of five

**The order is non-negotiable:** specify the estimand BEFORE choosing the statistical method. Choosing MMRM and retrofitting the estimand to match is the canonical error.

## The Five Intercurrent-Event Strategies

| Strategy | What it does | Typical implementation | Identification cost | Regulatory pattern |
|----------|--------------|------------------------|---------------------|---------------------|
| **Treatment policy** | Include all data regardless of ICE | ANCOVA on observed value (retrieved-dropout data); ITT-like | Trivially identified; needs full follow-up regardless of ICE | FDA-preferred default for cardio/HF/CV-safety; Fleming 2025 endorsement |
| **Hypothetical** | What would have been observed had ICE not occurred | MMRM under MAR; g-computation; IPCW; reference-based MI under MAR | Sequential ignorability (causal); MAR (missing-data shorthand) | Heavy use in CNS, diabetes, respiratory; EMA more accepting than FDA |
| **Composite** | Incorporate ICE into endpoint | Death = non-responder; PFS = composite of progression OR death; MACE | Identified from observed data; embeds a ranking choice | Standard in oncology PFS; acceptable when ICE has clinical signal |
| **While-on-treatment** | Use only pre-ICE values | Censor at discontinuation (for TTE); analyse last pre-ICE value (for repeated measures) | Estimates conditional quantity | Safety endpoints (AE rate per time on drug); FDA cautious for efficacy |
| **Principal stratum** | Confine to latent stratum (e.g. tolerators) | Bayesian estimation under monotonicity/principal ignorability | Latent membership; unverifiable assumptions | Rare as primary; some oncology/vaccine acceptance |

**Postdoc reading list:**

- Bornkamp, Rufibach, Lin, Liu, Mehrotra, Roychoudhury, Schmidli, Shentu, Wolbers 2021 *Pharm Stat* 20:737 — principal stratum critique
- Olarte Parra, Daniel, Bartlett 2022 *Stat Biopharm Res* — proves MMRM-MAR IS a hypothetical estimator under specific causal assumptions
- Permutt 2016 *Stat Med* 35:2876; 2020 *Stat Biopharm Res* 12:45 — FDA Missing Data Working Group taxonomy; "do covariates change the estimand?"
- Fleming, Carroll, Wittes et al 2025 *Stat Med* — argue treatment policy is the only strategy preserving randomisation; critique hypothetical
- Morris 2026 *Stat Med* — causal-perspective comment on Fleming
- Lipkovich, Ratitch, Mallinckrodt 2020 *Stat Biopharm Res* — Rubin causal model connection

## Decision Tree for Estimand Selection

| Trial scenario | Recommended estimand strategy | Why |
|----------------|-------------------------------|-----|
| Continuous endpoint, monotone missingness, MAR plausible | Hypothetical via MMRM (mmrm + KR) | Standard FDA-favoured MAR analysis; cite Mallinckrodt 2008/2014 |
| Continuous endpoint, ICE = treatment discontinuation, sponsor wants effectiveness | Treatment policy via retrieved-dropout MI | If post-ICE data available; ITT-respecting |
| Continuous endpoint, treatment-policy primary with ICE-related missingness | Hybrid: J2R for discontinuation ICEs, MMRM-MAR for other missingness | Aprocitentan precedent; de facto FDA standard 2024-2025 |
| Binary endpoint, RCT, FDA 2023-compliant | Marginal RD via g-computation; conditional OR supportive | See clinical-biostatistics/logistic-regression for g-computation |
| Oncology OS with crossover | Treatment policy as primary; hypothetical (RPSFT/IPCW) as sensitivity | Sotorasib CodeBreaK 200 precedent |
| Oncology PFS | Treatment policy for subsequent-therapy ICE (composite may incorporate death) | Sun 2021 framework; Fleming 2025 |
| Weight management / chronic disease | Retrieved-dropout MI (Wegovy STEP precedent); J2R supportive | FDA 2025 obesity draft guidance explicitly endorses |
| Long-term safety endpoint | While-on-treatment for rate; treatment policy for cumulative incidence | Standard ICH E2A practice |
| AlloSCT in hematologic oncology | Composite "event-free survival" treating alloSCT as event | Sun 2021 (alloSCT as intercurrent event); "no alloSCT" hypothetical is clinically meaningless |
| Symptomatic palliative endpoint with high dropout | Composite with worst-rank for dropouts (Permutt trimmed means) | Permutt 2017 *Pharm Stat* 16:20 |

## MMRM -- The FDA-Favoured MAR Analysis

**Mallinckrodt 2008/2014, codified in DIA Scientific Working Group "three pillars" doctrine:** for continuous longitudinal endpoints under monotone (or near-monotone) MAR, an MMRM with treatment + visit + treatment-by-visit + baseline + baseline-by-visit, unstructured (UN) within-subject covariance, REML, contrast at the primary timepoint -- is the consistent and FDA-preferred analysis. LOCF is biased even under MCAR because it discards imputation uncertainty and assumes a flat post-withdrawal trajectory.

### The mmrm R package (Roche / openpharma)

```r
library(mmrm)
fit <- mmrm(
    formula = change_from_baseline ~ baseline + arm * visit + us(visit | subject),
    data = trial_data,
    method = "Kenward-Roger",  # or "Satterthwaite", "Kenward-Roger-Linear"
    reml = TRUE
)
summary(fit)  # treatment-by-visit contrast at primary timepoint
```

**The Kenward-Roger flavour question:** `method = "Kenward-Roger"` uses full second-order Kenward-Roger (Kenward-Roger 1997 *Biometrics* 53:983), which inflates SE for fixed-effect contrasts using an adjusted covariance estimator with second-order Taylor terms. **`method = "Kenward-Roger-Linear"` drops the second-order Cholesky-derivative term to match SAS PROC MIXED bit-for-bit.** Most submissions use Kenward-Roger-Linear to maintain SAS-R reproducibility.

### Convergence-vs-correctness trade-off

Unstructured (UN) covariance has p(p+1)/2 parameters for p visits. With ~30-50 patients per arm by week 12 and 6+ visits, UN can fail to converge. The industry-standard fallback hierarchy per pre-specified SAP:

1. UN with KR (preferred)
2. UN with Satterthwaite (if KR fails)
3. Heterogeneous Toeplitz (k+1 parameters)
4. AR(1) with heterogeneous variances
5. CS with heterogeneous variances (last resort)

Each step down imposes more structure and the structure can be wrong — biasing both SEs and point estimates. CS imposes equal correlation across time which is rarely true for treatment-ramp-up endpoints (HbA1c, BP). Pre-specify the fallback in the SAP, not at analysis time.

### MMRM = hypothetical estimator (Olarte Parra unification)

**Olarte Parra, Daniel, Bartlett 2022 *Stat Biopharm Res*:** under specific identifying assumptions, MMRM under MAR IS a causal hypothetical estimand via g-formula equivalence. The "issue" is articulation, not statistical machinery — MMRM-MAR implicitly answers a hypothetical estimand whose hypothetical scenario must be made explicit in the SAP (e.g., "what would the mean response at week 24 be had all patients continued randomised treatment and remained observable?").

## Reference-Based Multiple Imputation -- The rbmi Framework

**Carpenter, Roger, Kenward 2013 *J Biopharm Stat* 23:1352** — the canonical paper. Reference-based MI operationalises MNAR sensitivity not as a numeric delta but as a clinical narrative:

- **Jump-to-reference (J2R):** "after withdrawal the patient instantly resembles the placebo arm"
- **Copy-reference (CR):** "the entire post-baseline trajectory copied from placebo, with subject's baseline deviation preserved"
- **Copy-increments-in-reference (CIR):** "the patient retains the on-treatment increment but trends with the placebo arm thereafter, anchored at last observed value"
- **Last-mean-carried-forward (LMCF):** "patient stays at last on-treatment mean"

**rbmi R package (Wolbers et al 2022 *Pharm Stat* 21(6):1246-1257; CRAN; insightsengineering):**

```r
library(rbmi)
# Draws -> Impute -> Analyse -> Pool pipeline
draws <- draws(data = trial_data, vars = vars,
               method = method_bayes(n_samples = 100))
imputed <- impute(draws, references = c('Active' = 'Placebo', 'Placebo' = 'Placebo'))
analyses <- analyse(imputed, fun = ancova,
                    vars = list(outcome = 'change', visit = 'avisit',
                                group = 'arm', covariates = c('baseline')))
result <- pool(analyses)  # Rubin's rules pooling
```

Four inference engines:

1. **Bayesian MI + Rubin's rules** (historical default) — information-anchored variance
2. **Approximate Bayesian via REML + bootstrap** — frequentist variance from bootstrap
3. **Conditional mean imputation + jackknife** (Wolbers 2022 contribution) — single deterministic imputation per ANCOVA-linearity theorem, jackknife for SE; FDA-friendly because deterministic + frequentist
4. **BMLMI (bootstrapped MI of Lipkovich/Ratitch)** — within/between variance decomposition

## The Variance Debate -- Cro/Carpenter vs Bartlett/Wolbers

**The single most active methodological argument in current biostatistics.**

**Cro/Carpenter/Kenward 2019 *JRSS-A* 182:623 ("Information-Anchored Sensitivity Analysis"):** proved that Rubin's-rules variance applied to J2R/CR/CIR is *approximately information-anchored* — the relative loss of information from missingness in the sensitivity analysis matches the relative loss in the MAR primary analysis. True repeated-sampling variance is "information positive" because reference-based imputation borrows from the reference arm and reduces the marginal variance of the active arm BELOW what an MAR analysis with the same missingness would give.

**Philosophical position:** a sensitivity analysis should not import information the primary analysis did not have; if borrowing from placebo makes the active-arm CI narrower, the analysis is no longer "anchored" to the same information state.

**Bartlett 2021 *Stat Biopharm Res* 15(1):178 + Wolbers 2022 *Pharm Stat* counter:** if J2R is the actual sampling model under which inference is made, then the *correct* frequentist variance is the one that delivers nominal Type-I error and CI coverage under that model -- the jackknife/bootstrap variance, NOT Rubin's. Simulations in `rbmi` vignettes: Bayesian MI with Rubin's gives Type-I error 0.9-2.5% (over-conservative); CMI+jackknife gives 4.84-4.96% (nominal) under J2R; Bayesian MI loses real power.

**Regulatory practice 2024-2025 is bifurcating:** EMA tolerates either; FDA reviewers increasingly flag Rubin's-rules variance under reference-based MI as needing a frequentist sensitivity analysis in addition. **What postdocs argue about:** whether Type-I inflation under bootstrap is the price of correct inference, or evidence J2R was never coherent as a true sampling model.

## Permutt Tipping-Point Analysis -- The Analyst as Adversary

**Permutt 2016 *Stat Med* 35:2876** (Permutt was head of FDA Division of Biometrics IV): the regulator's question is not "what is a reasonable MNAR adjustment?" but "how bad would the missing data have to be in the active arm to overturn the significant primary result?"

**Delta-adjustment patterns:**

- One-arm shift (FDA preferred): add delta to imputed values in active arm only; vary delta from 0 to the value that nullifies the effect
- Symmetric shift: both arms worsened by delta (probes systematic optimism)
- Reverse shift: placebo improved by delta (more aggressive, rarely needed)

```r
# rbmi with delta adjustment
delta <- delta_template(imputed, delta = c(0, 5, 10, 15, 20), dlag = c(1, 1, 1, 1))
adjusted <- analyse(imputed, delta = delta, ...)
# Report: minimum delta that flips p-value below 0.05
```

The regulator then judges whether the tipping delta is clinically plausible — larger than the active-arm treatment effect itself? Larger than the MCID? FDA-preferred report: tipping delta in units of residual SD (for cross-trial comparison), not raw outcome units.

## Decisive Regulatory Cases -- The 2020-2025 Casebook

**Aducanumab (Biogen BLA 761178, 2021):** EMERGE and ENGAGE studies both stopped early for futility; EMERGE high-dose positive, ENGAGE negative. MMRM-MAR primary. FDA Office of Biostatistics (Tristan Massie review) argued futility-stop-induced missingness was not MAR (differential ARIA-driven unblinding); the Nov 2020 AdCom voted overwhelmingly against approval. Textbook case showing MAR-based primary in trial with high differential missingness is regulator-divisive.

**Aprocitentan (Idorsia PRECISION trial, FDA approval 2024):** documented in Sassi-Sayadi et al 2025 *Ther Innov Regul Sci* (PMC12753554). FDA pushed back on sponsor's MMRM-MAR primary; MAR was not credible for treatment-discontinuers. Accepted compromise: stratified imputation — J2R for treatment-discontinuation ICEs, MAR-MMRM for other missingness. This hybrid is now de facto FDA standard for treatment-policy estimand.

**Wegovy/Ozempic STEP trials (Wilding 2021 *NEJM*; NDA 215256):** retrieved-dropout MI as primary for treatment-policy. Missing body weight at week 68 imputed by sampling from observed week-68 measurements among "retrieved dropouts" (patients who discontinued semaglutide but remained in follow-up). J2R-MI as supportive. RD-MI now standard for chronic weight management. FDA 2025 obesity guidance explicitly endorses MI as primary.

## Table 1 -- Baseline Characteristics

**CONSORT 2010 discouraged baseline significance tests** because randomisation is a known mechanism, not a hypothesis. Many journals still require them.

```python
from tableone import TableOne

columns = ['age', 'sex', 'race', 'bmi', 'baseline_score', 'disease_stage']
categorical = ['sex', 'race', 'disease_stage']

table1 = TableOne(df, columns=columns, categorical=categorical,
                  groupby='ARM', pval=True, smd=True,
                  missing=True, overall=True)
print(table1.tabulate(tablefmt='github'))
table1.to_excel('table1.xlsx')
```

**Use standardised mean differences (SMD) rather than p-values:** SMD > 0.1 suggests meaningful imbalance regardless of statistical significance.

**Senn's "balance testing is incoherent" (1994 *Stat Med* 13:1715; Altman 1985):** balancing via randomisation, testing balance, then adjusting only when the test fails is a selection rule that destroys nominal Type-I error. Pre-specify covariates in the SAP; do not condition adjustment on observed imbalance.

## Analysis Populations -- ITT vs FAS vs PP vs Safety

| Population | Definition | Bias direction | Primary use |
|-----------|------------|----------------|-------------|
| ITT | All randomised, as randomised | Conservative (toward null) | Primary efficacy per ICH E9 |
| FAS (Full Analysis Set) | ITT excluding eligibility failures + subjects with no post-baseline data | Middle ground; close to ITT | Common practical primary; ICH E9 "as complete as possible while remaining unbiased" |
| Per-Protocol | Completed treatment per protocol without major violations | Anti-conservative (inflates effect) | Sensitivity analysis only |
| Safety | All received at least one dose | n/a | AE analysis |
| mITT | Sponsor-defined modified ITT | Variable | Pre-specify and justify |

**FAS vs ITT distinction is critical for regulatory submissions** — FAS may exclude post-randomisation subjects (ineligibility, no post-baseline efficacy); ITT cannot. Sponsors often equate them on the SAP only to discover at submission that FDA expected stricter ITT. Pre-specification in protocol is essential.

```python
itt = dm.copy()
pp = dm[dm['USUBJID'].isin(completers) & ~dm['USUBJID'].isin(protocol_violators)]
dosed = ex[ex['EXDOSE'] > 0]['USUBJID'].unique()
safety = dm[dm['USUBJID'].isin(dosed)]
```

## Missing Data Mechanisms -- The Practical Framework

| Mechanism | Definition | Testable? | Valid method |
|-----------|------------|-----------|--------------|
| MCAR | Independent of all data | Partially (Little's test) | Complete-case unbiased but loses power |
| MAR | Depends on observed data only | NO (assumption) | MMRM under MAR; MI under MAR |
| MNAR | Depends on unobserved values | NO | Requires sensitivity analysis (J2R, CR, CIR, tipping point) |

**MAR vs MNAR cannot be distinguished from observed data alone — this is a fundamental limitation.** Pre-specify the assumed mechanism in the SAP; pre-specify the sensitivity analysis under MNAR (NRC 2010 Recommendation 15: "examining sensitivity to assumptions about the missing-data mechanism should be a mandatory component of reporting").

**Clinical reasoning beyond the abstraction:** examine the DS (Disposition) domain to tabulate reasons for discontinuation by treatment arm. If discontinuation rates or reasons differ between arms, missing data is likely informative and MNAR sensitivity analyses are mandatory.

## Standard MMRM-MAR Primary Analysis Code

**Goal:** Execute the FDA-preferred primary analysis for a continuous longitudinal endpoint under MAR with valid Type-I in small/moderate trials.

**Approach:** Fit MMRM with unstructured covariance + Kenward-Roger via the Roche/openpharma `mmrm` R package; in Python, use `statsmodels.mixedlm` as exploratory-only (lacks KR).

```python
# Python is weak for MMRM — current state of the art is R `mmrm`
# For Python users, statsmodels.mixedlm is the closest alternative but lacks
# Kenward-Roger; consider rpy2 to call R from Python for confirmatory work.

import statsmodels.formula.api as smf
import pandas as pd

# Random intercept LMM (suboptimal vs MMRM but Python-native)
model = smf.mixedlm(
    'change ~ baseline + C(ARM) * C(VISIT)',
    data=df_long,
    groups=df_long['USUBJID']
).fit(reml=True)
# WARNING: this is NOT FDA-equivalent to MMRM with UN+KR
# For confirmatory work, use R `mmrm` package via rpy2 or fit in R directly
```

## Multiple Imputation in Python (sklearn)

```python
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer
import statsmodels.formula.api as smf
import numpy as np

n_imputations = 20  # rule: m >= 100 * FMI (fraction of missing info)
imputer = IterativeImputer(max_iter=10, random_state=0, sample_posterior=True)

results = []
for i in range(n_imputations):
    imputer.set_params(random_state=i)
    imputed = pd.DataFrame(imputer.fit_transform(df[numeric_cols]), columns=numeric_cols)
    for col in ['ARM', 'sex']:
        imputed[col] = df[col].values
    model = smf.logit(
        'outcome ~ C(ARM, Treatment(reference="Placebo")) + age', data=imputed
    ).fit(disp=0)
    results.append({'coef': model.params.iloc[1], 'se': model.bse.iloc[1]})

# Rubin's rules
pooled_coef = np.mean([r['coef'] for r in results])
within_var = np.mean([r['se']**2 for r in results])
between_var = np.var([r['coef'] for r in results], ddof=1)
total_var = within_var + (1 + 1/n_imputations) * between_var
pooled_se = np.sqrt(total_var)
pooled_or = np.exp(pooled_coef)
```

**Critical sklearn caveats:**

- `sample_posterior=True` is essential — without it all m imputations are nearly identical
- **`sample_posterior=True` only works with `BayesianRidge` (the default estimator)**. If estimator is changed (e.g., `RandomForestRegressor`), parameter is silently ignored and MI degenerates to single imputation
- IterativeImputer treats binary covariates as continuous; consider `miceforest` for mixed types or move to R `mice`/`rbmi`
- Only impute covariates and post-baseline outcomes, NOT treatment assignment (fully determined by randomisation)
- Include outcome in imputation model as predictor but exclude from imputed variables to avoid circular dependency
- IterativeImputer is **experimental** in sklearn — API may change without standard deprecation

**Congeniality (Meng 1994):** imputation model must be at least as flexible as analysis model. If analysis includes treatment-by-covariate interactions, imputation model should include them. Uncongenial imputation biases estimates and invalidates variance pooling.

## Co-Primary Endpoints and Multiplicity

| Method | Approach | Conservatism |
|--------|----------|--------------|
| Bonferroni | alpha / m | Most conservative |
| Hierarchical (gatekeeping) | Pre-specified order; proceed only if previous rejects | Moderate; full alpha for first |
| Graphical procedure (Bretz-Maurer) | Directed graph; alpha propagates on rejection | Flexible; standard in modern SAPs |
| Hochberg / Hommel step-up | Ordered p-values vs alpha/(m-k+1) | Less conservative than Bonferroni; requires PRDS |

See clinical-biostatistics/multiplicity-graphical for the full Bretz-Maurer-Hommel treatment with `gMCP`.

## Reconciliation: When Methods Disagree

| Pattern | Likely cause | Action |
|---------|--------------|--------|
| MMRM-MAR primary p < 0.05; reference-based MI sensitivity p > 0.05 | MNAR mechanism after treatment discontinuation; J2R imputes active arm toward placebo | Decide which estimand is regulatory primary; if treatment policy, switch to reference-based MI as primary (Aprocitentan precedent) |
| Retrieved-dropout MI vs J2R-MI differ | RD-MI uses observed post-ICE data; J2R uses reference-arm-based assumption | If post-ICE data available, RD-MI is empirically grounded (preferred); J2R as supportive |
| Cro information-anchored variance vs Wolbers frequentist variance differ | Information-anchored Rubin's pools within+between; frequentist jackknife/bootstrap captures borrowing-induced variance reduction | Report both; cite Cro 2019 and Wolbers 2022 (Bartlett 2021 frequentist critique); 2024-2025 FDA practice accepts both with one as supportive |
| ITT primary p < 0.05; PP secondary p > 0.05 | Per-protocol excludes non-completers (often differentially); PP-only effect inflated when significant; non-significance in PP is signal of fragility | ITT remains primary (ICH E9); PP as sensitivity flag; investigate completer pattern |
| Statistical significance achieved but effect estimate below MCID | Powered for δ << MCID; or δ = MCID with no precision margin | Pre-specify δ >= 1.5 × MCID in SAP (postdoc rule); report against pre-specified MCID, not 0 |
| Estimand strategies (hypothetical vs treatment-policy) give different effect sizes | Different ICE-handling strategies target different parameters | Report all pre-specified estimands; pick PRIMARY for the regulatory question (not the "winner"); cite Kahan 2023 |
| Subgroup effect estimate >2x main effect | Winner's curse -- discovery-data subgroup estimates are inflated | Apply Bayesian shrinkage (Dixon-Simon, RBesT) for corrected estimate; cite as discovery, not confirmatory |

## CONSORT 2025 (April 2025) -- What Changed

**Citation:** Hopewell, Chan, Collins et al 2025. CONSORT 2025 statement. *Lancet* 405:1633-1640. E&E in BMJ 2025;389:e081124.

**30-item checklist (was 25)**, 7 new items, 3 substantially revised, 1 deleted. Key new items relevant to statistical reporting:

- **Item 4** (data and code sharing — where/how de-identified IPD and analysis code can be accessed) — NEW
- **Item 15** (how harms were actually assessed — methods, attribution, intensity, monitoring rules) — NEW; absorbs CONSORT-Harms 2022
- **Item 21c** (missing-data handling methods) — NEW; reflects NRC 2010 / Carpenter-Kenward consensus
- **Item 24a/24b** (intervention/comparator actual delivery details) — absorbs TIDieR

**Estimands did NOT make consensus for mandatory inclusion** — they appear in Box 1 (terminology only). **For regulatory submissions, ICH E9(R1) is the operative estimand standard, NOT CONSORT 2025.** Sponsors should follow ICH E9(R1) directly for the 5-attribute estimand statement.

**No DOORS framework in CONSORT 2025** — diversity/equity additions are happening via a separate SAGER-SPIRIT-CONSORT alignment workstream (GENDRO/EASE).

## CONSORT Flow Diagram

```python
flow = {
    'screened': len(screening_log),
    'eligible': len(screening_log[screening_log['eligible']]),
    'randomized': len(dm),
    'allocated_drug': len(dm[dm['ARM'] == 'Drug']),
    'allocated_placebo': len(dm[dm['ARM'] == 'Placebo']),
    'completed_drug': len(dm[(dm['ARM'] == 'Drug') & dm['USUBJID'].isin(completers)]),
    'completed_placebo': len(dm[(dm['ARM'] == 'Placebo') & dm['USUBJID'].isin(completers)]),
    'analyzed_itt': len(itt),
    'analyzed_fas': len(fas),
    'analyzed_pp': len(pp),
    'analyzed_safety': len(safety),
}
```

CONSORT 2025 templates on consort-spirit.org now explicitly accommodate non-1:1 allocation, cluster, multi-arm, and crossover variants.

## Per-Method Failure Modes

### MMRM-MAR with high differential missingness

- **Trigger:** Differential dropout between arms (e.g., toxic active vs tolerated placebo).
- **Mechanism:** MAR assumption requires that conditional on observed covariates, missingness is unrelated to outcome — implausible when patients drop out *because* the treatment isn't working.
- **Symptom:** Discontinuation reasons differ qualitatively between arms; primary p-value sensitive to model specification.
- **Fix:** Treatment-policy estimand with retrieved-dropout MI as primary; J2R as sensitivity. Tipping-point delta in active arm (Permutt 2016).

### Reference-based MI with Rubin's variance

- **Trigger:** J2R/CR/CIR with Rubin's-rules variance reported as primary.
- **Mechanism:** Rubin's variance is information-anchored but over-conservative (Cro 2019); under-rejects relative to nominal.
- **Symptom:** Power loss vs frequentist variance; Type-I 0.9-2.5% vs nominal 5% in J2R simulations.
- **Fix:** Report frequentist variance via CMI+jackknife as supportive (Wolbers 2022); cite both Cro and Bartlett.

### sample_posterior=False in IterativeImputer

- **Trigger:** Default behaviour or estimator changed away from BayesianRidge.
- **Mechanism:** Imputations are point predictions, near-identical across draws; between-imputation variance approximately zero.
- **Symptom:** Artificially narrow Rubin's-pooled CIs.
- **Fix:** Always set `sample_posterior=True`; verify estimator is BayesianRidge; consider `miceforest` or R `mice` for mixed types.

### Per-protocol as primary

- **Trigger:** SAP specifies PP analysis as primary.
- **Mechanism:** Excludes non-completers who may have dropped due to treatment failure; inflates effect.
- **Symptom:** PP effect much larger than ITT; reviewers raise post-randomisation bias concern.
- **Fix:** ITT or FAS as primary per ICH E9; PP as sensitivity only.

### Method-before-estimand

- **Trigger:** SAP describes MMRM, MI, or LOCF without specifying the estimand the method targets.
- **Mechanism:** Retrofits the estimand to match the chosen method.
- **Symptom:** Reviewer asks "what is the estimand?" and sponsor cannot articulate.
- **Fix:** Per ICH E9(R1), define the 5 attributes BEFORE choosing method; cite Kahan 2023.

### Missing the FAS vs ITT distinction

- **Trigger:** Treating FAS and ITT as synonymous.
- **Mechanism:** FAS may exclude eligibility failures or no-post-baseline; ITT cannot.
- **Symptom:** Submission counts differ between FAS and ITT; reviewer asks for ITT.
- **Fix:** Pre-specify both populations explicitly in protocol; report both with reconciliation.

## Quantitative Thresholds

| Threshold | Source | Rationale |
|-----------|--------|-----------|
| m >= 100 * FMI imputations (linear rule of thumb) | von Hippel 2020 *Sociol Methods Res* (two-stage quadratic refinement) | Adequate for stable pooled SE; with 40% missingness and FMI ~0.3, m=30 needed |
| SMD > 0.1 = meaningful imbalance | Austin 2009 *Stat Med* 28:3083 | Beyond what randomisation would normally produce |
| Missing data > 40% on key variable | NRC 2010 | Above this, MI under MAR is unreliable; treat as hypothesis-generating |
| Kenward-Roger DF correction for MMRM with UN | Kenward-Roger 1997 | Without it, MMRM-REML under-covers in small/moderate trials; Type-I inflates 1-2 pp |
| Information-anchored vs frequentist variance for reference-based MI | Cro 2019 vs Wolbers 2022 | Active regulatory debate; report both for safety |
| Tipping delta in residual SD units, not raw | FDA Division of Biometrics preference | Cross-trial comparison; report adjacent to raw |
| Treatment policy default for cardio/HF/CV | Fleming 2025 *Stat Med* | Only strategy preserving randomisation; FDA-favoured |

## Common Errors

| Error / symptom | Cause | Solution |
|-----------------|-------|----------|
| Reviewer: "what is the estimand?" with no answer | Method-before-estimand | Pre-specify 5 attributes in protocol; cite Kahan 2023 finding 98% don't articulate |
| LOCF used as primary | Inertia or "conservative" misconception | LOCF is biased even under MCAR (Mallinckrodt 2008); switch to MMRM or MI |
| MMRM with CS covariance treated as equivalent to UN | Convergence forced fallback without pre-specification | Pre-specify fallback hierarchy; document deviation if invoked |
| Rubin's variance for J2R with no sensitivity | Cro 2019 information-anchored argument applied without acknowledgement | Cite Bartlett 2021 + Wolbers 2022; report frequentist variance via CMI+jackknife |
| Tipping delta in raw outcome units only | Hard to compare cross-trial | Also report in residual SD units (FDA preference) |
| ITT and FAS conflated | SAP vague on distinction | Pre-specify both with explicit criteria for FAS exclusion |
| Per-protocol significant, ITT not — sponsor highlights PP | Post-randomisation bias inflation | ITT as primary; PP as sensitivity with explicit caveat |
| Imputation only of outcome | Throws away covariates | Joint imputation of outcome + covariates; cite Carpenter-Roger 2013 |
| `sample_posterior` silently ignored | Non-default estimator | Verify with `imputer.estimator` is BayesianRidge or use rbmi/mice |

## Anticipated Reviewer Pushback

| Pushback | Response |
|----------|----------|
| "What is the estimand?" | Articulate 5 ICH E9(R1) attributes; cite Kahan 2023; state ICE strategy with mechanism (not just label). |
| "Is MAR plausible?" | Examine DS for differential discontinuation patterns; if differential, switch to treatment-policy with retrieved-dropout MI or J2R sensitivity. |
| "Why MMRM not LOCF?" | Mallinckrodt 2008/2014 case for MMRM; LOCF is biased even under MCAR. Cite DIASWG three-pillars doctrine. |
| "Why Rubin's not frequentist variance for J2R?" | Cite Cro 2019 information-anchored argument as rationale; report frequentist (CMI+jackknife) as supportive per Wolbers 2022. |
| "Tipping point analysis result?" | Minimum delta in active arm that flips p > 0.05; report in residual SD units; judge plausibility against MCID and treatment effect. |
| "FAS vs ITT?" | Pre-specified in protocol; FAS excludes [explicit criteria]; both populations analysed; reconciliation table provided. |
| "Has the SAP been registered?" | Yes — clinicaltrials.gov NCTxxxxx with full SAP appended; EU CTR EUCTxxxx; SPIRIT 2025 compliant. |
| "How is subsequent therapy handled?" | Pre-specified per ICH E9(R1); composite strategy (e.g., subsequent therapy = treatment failure) or treatment-policy (include all data). |
| "Where is the multiplicity adjustment for co-primary / key secondary?" | Bretz-Maurer graphical procedure via gMCP pre-specified in SAP; alpha allocation diagram in CSR appendix; cite CONSORT 2025 item 30 (limitations, multiplicity of analyses) + FDA Multiple Endpoints Final Oct 2022; see clinical-biostatistics/multiplicity-graphical. |
| "How are missing baseline covariates handled in ANCOVA?" | Complete-case ANCOVA is unbiased under MCAR baseline missingness (White & Thompson 2005 *Stat Med* 24:993); proportion with complete baseline reported in flow diagram; if >5% missing, multiple imputation of baseline as sensitivity analysis. |

## References

- Bornkamp B, Rufibach K, Lin J, Liu Y, Mehrotra DV, Roychoudhury S, Schmidli H, Shentu Y, Wolbers M. 2021. Principal stratum strategy: potential role in drug development. *Pharm Stat* 20:737-751.
- Carpenter JR, Roger JH, Kenward MG. 2013. Analysis of longitudinal trials with protocol deviation: a framework for relevant, accessible assumptions, and inference via multiple imputation. *J Biopharm Stat* 23:1352-1371.
- Cro S, Carpenter JR, Kenward MG. 2019. Information-anchored sensitivity analysis: theory and application. *JRSS-A* 182:623-645.
- EMA. 2010. Guideline on Missing Data in Confirmatory Clinical Trials. EMA/CPMP/EWP/1776/99 Rev.1.
- Fleming TR, Carroll KJ, Wittes JT, Emerson SS, Rothmann M, Collins S, Levin G. 2025. A perspective on the appropriate implementation of ICH E9(R1) addendum strategies for handling intercurrent events. *Stat Med* 44:e70104.
- Hopewell S, Chan AW, Collins GS, et al. 2025. CONSORT 2025 statement. *Lancet* 405:1633-1640.
- ICH. 2019. E9(R1) Addendum on Estimands and Sensitivity Analysis in Clinical Trials. Step 4.
- Kahan BC, Cro S, Li F, Harhay MO. 2023. Eliminating ambiguous treatment effects using estimands. *Am J Epidemiol* 192:987-994.
- Kenward MG, Roger JH. 1997. Small sample inference for fixed effects from restricted maximum likelihood. *Biometrics* 53:983-997.
- Lipkovich I, Ratitch B, Mallinckrodt CH. 2020. Causal inference and estimands in clinical trials. *Stat Biopharm Res* 12:54-67.
- Mallinckrodt CH, Lane PW, Schnell D, Peng Y, Mancuso JP. 2008. Recommendations for the primary analysis of continuous endpoints in longitudinal clinical trials. *Drug Information Journal* 42:303-319.
- Sassi-Sayadi M, Verweij P, Cornelisse P. 2025. Regulatory experiences with the use of multiple imputation for missing data in a phase 3 confirmatory trial. *Ther Innov Regul Sci*.
- Morris TP. 2026. Comment on Fleming et al. *Stat Med* e70455.
- NRC. 2010. The Prevention and Treatment of Missing Data in Clinical Trials. National Academies Press.
- Olarte Parra C, Daniel RM, Bartlett JW. 2022. Hypothetical estimands in clinical trials: a unification of causal inference and missing data methods. *Stat Biopharm Res* 15(2):421-432.
- Permutt T. 2016. Sensitivity analysis for missing data in regulatory submissions. *Stat Med* 35:2876-2879.
- Permutt T. 2020. Do covariates change the estimand? *Stat Biopharm Res* 12:45-53.
- Sun S, Weber HJ, Butler E, Rufibach K, Roychoudhury S. 2021. Estimands in hematologic oncology trials. *Pharm Stat* 20(4):793-805.
- von Hippel PT. 2020. How many imputations are needed (a two-stage calculation using a quadratic rule). *Sociol Methods Res* 49:699-718.
- Wolbers M, Noci A, Delmar P, Gower-Page C, Yiu S, Bartlett JW. 2022. Standard and reference-based conditional mean imputation. *Pharm Stat* 21(6):1246-1257.

## Related Skills

- clinical-biostatistics/cdisc-data-handling - SDTM/ADaM data preparation feeding the analysis dataset
- clinical-biostatistics/logistic-regression - Primary analysis models (binary) with marginal-vs-conditional
- clinical-biostatistics/effect-measures - Effect-measure CIs under MI pooling
- clinical-biostatistics/subgroup-analysis - Pre-specified subgroup analyses for the CSR
- clinical-biostatistics/missing-data-sensitivity - MMRM, reference-based MI, tipping point (in depth)
- clinical-biostatistics/multiplicity-graphical - Bretz-Maurer graphs for co-primary and key secondary
- clinical-biostatistics/survival-analysis - Time-to-event estimand framing under ICH E9(R1)
- clinical-biostatistics/power-and-sample-size - Sample size justification per CONSORT 2025 item 16a
- reporting/rmarkdown-reports - Formatted statistical report generation
- experimental-design/multiple-testing - General multiplicity correction
<!-- END FILE: clinical-biostatistics/trial-reporting/SKILL.md -->

<!-- END CATEGORY: clinical-biostatistics -->

