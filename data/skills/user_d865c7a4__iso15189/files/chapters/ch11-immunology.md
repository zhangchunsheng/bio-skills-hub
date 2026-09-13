# Chapter 11: Clinical Immunology (第十一章 临床免疫学检验)

## Core Idea
Immunology accreditation runs on **two parallel tracks that chemistry does not need to separate**: qualitative/semi-quantitative assays (infectious-disease serology, autoantibodies — judged by cutoff, grey zone, and concordance) and quantitative immunoassays (hormones, tumor markers — judged by precision/trueness/linearity much like chemistry). The chapter's signature risk is **reporting an unconfirmed screening result as if it were final** — infectious-disease markers (HIV/HBV/HCV/syphilis) carry a mandated national retest-and-confirm algorithm, and the accreditation question is whether the lab's SOP faithfully mirrors that algorithm rather than shortcutting it.

## Discipline-Specific Requirements

### 人员 (Personnel) [clause 6.2]
- Immunology section (临床免疫学专业组) technical lead needs mid-level+ title with immunology background; scope declaration must separate qualitative vs. quantitative immunoassay categories since verification/QC differ.
- Staff releasing infectious-disease serology results (HIV/HBV/HCV/syphilis) require documented authorization beyond general immunoassay competency, given public-health/reporting implications.
- Competency assessment ≥1×/year covers cutoff/grey-zone interpretation, confirmatory-algorithm execution, discordant-result handling, and biosafety practice for infectious specimens.

### 设施与环境 (Facilities & Environment) [clause 6.3]
- Reagent/calibrator cold-chain 2–8°C, continuously monitored; many reagents (enzyme conjugates, antibody-coated beads, chemiluminescence substrate) require **protection from light (避光保存)** with a labeled open-vial stability period.
- Testing areas handling infectious specimens follow biosafety practice comparable to microbiology (sharps/waste segregation).
- Ambient operating range per instrument IFU (commonly 15–30°C), humidity controlled against condensation.

### 设备与试剂 (Equipment & Reagents) [clauses 6.4 equipment, 6.5 calibration/traceability, 6.6 reagents]
- Chemiluminescence/EIA/lateral-flow platforms need installation verification and maintenance, but **verification approach diverges by test type** (see Frameworks). [6.4]
- **New reagent lot verification** [6.6]: mandatory for qualitative kits especially — new lot checked against weak-positive/negative panel and prior lot before clinical use, because cutoff/sensitivity can shift lot to lot.
- Manufacturer-claimed sensitivity/specificity/cross-reactivity from the kit insert kept on file, cross-checked during local verification. [6.6]
- Calibrator/reference-material traceability documented per analyte [6.5, ISO 17034/ISO 17511].
- **Biotin interference**: policy addressing high-dose biotin supplementation risk for streptavidin-biotin chemiluminescence assays (patient advisory/interference flag).

### 检验前 (Pre-examination) [clause 7.2]
- Serum-vs-plasma is kit-specific (some chemiluminescence platforms require serum only); hemolysis/lipemia interferes with signal.
- Labile analytes (e.g., complement C3/C4) need prompt testing or −20°C storage if delayed.
- Infectious specimens: special handling (heat-inactivation prohibited for certain assays; biosafety labeling on tube/request form).

### 检验中 (Examination) [clause 7.3]
- **Qualitative-test verification** [7.3.2]: concordance (符合率) against a reference method/characterized panel — commonly ≥20 positive + ≥20 negative samples, concordance target ≥90–95%; plus limit of detection and cutoff verification spanning near-cutoff concentrations including weak positives.
- **Grey zone (灰区)** [7.3.4 cutoff/reference interpretation]: band around cutoff (notably HIV/HCV screening) where a result is neither clearly negative nor positive and must trigger mandatory duplicate retest or reflex to a confirmatory method — never direct reporting.
- **Quantitative immunoassay verification** [7.3.2, WS/T 641-2018]: precision (CV targets, e.g., thyroid function ≤10%, tumor markers ≤10–15%), trueness/bias (vs. CRM or EQA target), linearity across the measuring range.
- **Hook effect (钩状效应)** [7.3.6 factors affecting examination]: verified/excluded for analytes prone to it at very high concentrations (hCG, ferritin, PSA) via dilution protocol when clinical suspicion contradicts an unexpectedly low/normal result.
- **Retest/confirmation algorithm** [7.3.7 ensuring quality of results]: initial reactive screen → mandatory duplicate retest with same reagent (双孔复检) → if still reactive/discordant, refer to confirmatory testing (e.g., Western blot/NAT for HIV) per the national CDC/health-authority algorithm — lab SOP must mirror this pathway, not an in-house shortcut.

### 检验后 (Post-examination) [clause 7.4]
- Screening-reactive-only results carry a standardized interpretive comment (e.g., "pending confirmation") rather than being released as an unqualified final positive.
- Qualitative-test reports include the signal-to-cutoff (S/CO) ratio where applicable, for trend tracking.
- **Urgent notification**: a new HIV-antibody-reactive result requires urgent clinician notification plus public-health reporting per regulation, distinct from routine TAT.
- Cross-platform result comparability for shared patients checked ≥2×/year.

### 质量保证 (Quality Assurance) [clause 7.3.7 ensuring quality of results; clause 8.1-8.9 management system close]
- **IQC for qualitative tests**: ≥1 negative + ≥1 positive control per run (weak-positive control near cutoff where available); any control failure invalidates the run — no patient release. Frequency: every run/day, plus re-verification after any new reagent lot or recalibration.
- **IQC for quantitative immunoassays**: Westgard multi-rule as in chemistry, ≥2 concentration levels, ≥1×/24h or per batch.
- **EQA** [GB/T 22576/GB/T 27043]: mandatory for all reportable analytes, ≥2–3×/year; infectious-marker EQA assesses correct confirmatory-algorithm application, not just the final call. Unsatisfactory → root-cause investigation, retraining, look-back review since last satisfactory event. No-scheme analytes → alternative assessment ≥2×/year.

## Frameworks Introduced
- **Dual-track verification (定性 vs. 定量)**: qualitative tests verified via concordance/cutoff/grey-zone; quantitative immunoassays via precision/trueness/linearity like chemistry. When: any new immunoassay method. How: classify the test first, apply the matching protocol — never substitute one track for the other.
- **Retest-and-confirm algorithm**: reactive screen → duplicate retest → confirmatory referral, per mandated national algorithm. When: HIV/HBV/HCV/syphilis and similar reportable markers. How: SOP maps 1:1 onto the health-authority algorithm; interpretive comments reflect "unconfirmed" status until referral returns.
- **Grey-zone reflex rule**: results in a band around cutoff are neither negative nor positive. When: kits with a manufacturer-defined grey zone (e.g., HIV screening). How: mandatory duplicate retest or confirmatory reflex, never direct reporting of the raw call.

## Key Concepts
- **Cutoff value (临界值/cutoff)** — manufacturer-defined signal threshold separating reactive from non-reactive.
- **Grey zone (灰区)** — band around cutoff requiring mandatory retest/reflex rather than direct interpretation.
- **S/CO ratio (信号/临界值比值)** — signal-to-cutoff ratio reported alongside qualitative results for trend tracking.
- **Concordance (符合率)** — positive/negative percent agreement vs. a reference method/characterized panel, used to verify qualitative assays.
- **Cross-reactivity (交叉反应)** — reactivity with non-target substances documented in the kit insert and checked during verification.
- **Hook effect (钩状效应)** — false low/normal result at very high concentration in one-step immunoassays; excluded via dilution.
- **Confirmatory testing (确认试验)** — mandated reference-lab method (e.g., Western blot, NAT) adjudicating a reactive/discordant screen.
- **Weak-positive control (弱阳性质控品)** — control near cutoff monitoring assay sensitivity drift.
- **Biotin interference (生物素干扰)** — false-result risk in streptavidin-biotin assays from high-dose biotin supplementation.

## Mental Models
- **Use "classify before you verify"**: decide qualitative or quantitative first — a CV/bias protocol on a qualitative kit (or a bare concordance check on a quantitative hormone assay) is the wrong tool.
- **Think of a reactive screen as "provisional, not final"**: nothing is reportable as a definitive positive for a mandated-algorithm marker until retest/confirmation completes.
- **Treat the grey zone as a mandatory reflex trigger, not a judgment call**: handled by protocol (retest/refer), never by discretion to round to positive/negative.

## Anti-patterns
- **Releasing an HIV/HBV/HCV screening-reactive result as final positive**: skips the mandated retest/confirmatory pathway, risking irreversible harm from an unconfirmed call.
- **Applying quantitative CV/bias logic to a qualitative kit (or vice versa)**: doesn't answer the relevant accreditation question for that test type.
- **Ignoring the grey zone by rounding a near-cutoff signal**: defeats the manufacturer's built-in reflex trigger.
- **Reporting a low/normal hCG, ferritin, or PSA without excluding hook effect when clinically suspected**: risks a false-negative-equivalent result.
- **Skipping IQC on a qualitative run**: still requires negative+positive control every run; a missed control means the run cannot be trusted.

## Reference Tables

| Topic | Criterion |
|---|---|
| Qualitative concordance (符合率) | ≥20 positive + ≥20 negative characterized samples; target ≥90–95% |
| Cutoff verification | Panel spanning near-cutoff concentrations incl. weak positives |
| Grey zone (灰区) | Mandatory duplicate retest or confirmatory reflex; never direct report |
| Cross-reactivity | Checked against kit-insert cross-reacting substances list |
| Quantitative immunoassay CV | Thyroid hormones ≤10%; tumor markers ≤10–15% (parallels Ch10: trueness vs. CRM/EQA, linearity, hook-effect exclusion via dilution) |
| Retest/confirm algorithm | (1) Screen reactive → not final → (2) duplicate retest same reagent (双孔复检) → (3) still reactive/discordant → refer to confirmatory lab (WB/NAT) → (4) report carries "unconfirmed" comment until referral returns |
| QC — qualitative tests | ≥1 negative + ≥1 positive control (+weak-positive where available) every run/day; any failure invalidates run; re-verify after new lot/recalibration |
| QC — quantitative immunoassays | Westgard multi-rule, ≥2 levels, ≥1×/24h or per batch |
| EQA | All reportable analytes, ≥2–3×/year; infectious-marker EQA assesses algorithm execution not just final call; no-scheme → alternative assessment ≥2×/year |
| Temp/humidity/light | Reagent fridges 2–8°C continuously monitored; light-sensitive conjugates/substrates protected from light; ambient lab range ~15–30°C per IFU; humidity controlled |

## Worked Example
An assessor reviews a case where a patient's initial HIV screening test returned reactive. The technologist, following an informal in-house shortcut, released the result as "HIV Ab positive" without the mandated duplicate retest or confirmatory referral. Finding: the SOP lacked an explicit reflex step tying "screen reactive" to "duplicate retest → confirmatory referral," so individual judgment substituted for the required algorithm — a major nonconformity given public-health impact. Corrective action: SOP rewritten to hard-code the national algorithm as a system-enforced reflex (LIS blocks final-positive reporting until a confirmatory result is entered), staff retrained, recent HIV-reactive reports retrospectively reviewed.

## Key Takeaways
- Immunology's accreditation logic bifurcates into qualitative (cutoff/grey-zone/concordance) and quantitative (precision/trueness/linearity) tracks — each needs its own verification and QC approach.
- The retest-and-confirm algorithm for infectious-disease markers is a legally/publicly mandated pathway, not a lab-optional practice; SOPs must mirror it exactly.
- Grey zone, hook effect, and biotin interference are discipline-specific failure modes that generic chemistry-style verification would miss.
- Qualitative-test IQC (positive/negative/weak-positive controls per run) is a distinct, non-negotiable control scheme from quantitative Westgard rules.

## Connects To
- **Ch 5 (Process — examination/post-examination)**: the retest/confirmation algorithm and grey-zone reflex rule refine the generic critical-value and result-release clauses for markers with legally mandated confirmatory pathways.
- **Ch 4 (Resources — Equipment/Reagents)**: light-sensitive/cold-chain reagent handling and lot-to-lot verification instantiate the generic reagent-management requirement for immunoassay-specific fragility.
- **Ch 6 (Management System Requirements)**: EQA failures, discordant infectious-marker results, and confirmatory-algorithm deviations are explicit nonconformity triggers feeding the same corrective-action/management-review cycle as other disciplines.
