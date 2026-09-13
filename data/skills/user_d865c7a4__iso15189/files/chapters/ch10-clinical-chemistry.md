# Chapter 10: Clinical Chemistry (第十章 临床化学检验)

## Core Idea
Clinical chemistry accreditation is built around **quantitative measurement defensibility**: every reportable number must be traceable to a metrological reference, verified against an allowable-total-error (TEa) budget, and monitored continuously through IQC/EQA. Unlike microbiology's growth-kinetics risk or immunology's qualitative cutoff logic, chemistry's central assessment question is "can you prove this number is close enough to the truth, and would you catch it if it drifted?" — answered through calibration traceability, precision/trueness/linearity verification, and Westgard-rule internal QC, all anchored to an explicit TEa criterion per analyte.

## Discipline-Specific Requirements

### 人员 (Personnel) [clause 6.2]
- Chemistry section (临床化学专业组) has a technical lead (专业组长, mid-level+ title, chemistry background) responsible for method selection, validation sign-off, QC-trend oversight.
- Staff in specialized sub-disciplines (TDM 治疗药物监测, 内分泌激素, 肿瘤标志物) need competency assessed ≥1×/year, explicitly covering interference/flag recognition (H/I/L) since automation shifts risk from technique to interpretation.
- Rotating/new staff (incl. nurses on blood-gas POCT) cannot release results unsupervised without documented chemistry-specific sign-off.

### 设施与环境 (Facilities & Environment) [clause 6.3]
- Reagent/calibrator storage at 2–8°C requires continuous or ≥2×/day temperature monitoring/logging; freezer reagents (−20°C) need defrost-cycle control.
- Analyzer room conditions follow manufacturer IFU (commonly 18–25°C); blood-gas/electrolyte analyzers additionally require protection from direct sunlight, vibration, and strong electromagnetic sources (e.g., away from MRI).

### 设备与试剂 (Equipment & Reagents) [clauses 6.4 equipment, 6.5 calibration/traceability, 6.6 reagents]
- Each analyzer requires installation/acceptance verification, then scheduled maintenance (日/周/月/年保养 logs). [6.4]
- **Calibration verification (校准验证)** [6.5, ISO 17511]: triggered by major maintenance, reagent-lot change, QC shift/trend, or at a routine interval of **≤6 months**; uses materials spanning the full reportable range (low/mid/high, ≥3–5 points) including clinically decisive concentrations.
- **Inter-instrument comparison (仪器比对)** [6.4/7.3.2]: ≥2×/year between backup/parallel analyzers, acceptance judged against the TEa budget (commonly bias ≤ 1/2 TEa).
- Manual volumetric equipment (pipettes) calibrated ≥1×/year. [6.4]
- **New reagent/calibrator lot verification** [6.6]: compare new vs. old lot using pooled patient samples across the range, or QC materials, before releasing the new lot clinically.

### 检验前 (Pre-examination) [clause 7.2]
- Analyte-specific collection rules: fasting 8–12h for glucose/lipid panel; correct anticoagulant (lithium heparin for blood gas/electrolytes; EDTA contaminates Ca²⁺/K⁺); minimized tourniquet time (raises K⁺/lactate).
- **H/I/L rejection**: lab-defined hemolysis/icterus/lipemia index cutoffs per analyte (manufacturer interference tables) beyond which a result is rejected/flagged.
- Stability windows: glucose in unseparated non-fluoride tube falls ~5–7%/hour — separate within ≤2h or draw in fluoride (glycolysis-inhibitor) tube.

### 检验中 (Examination — method validation core) [clause 7.3]
- **Method verification package** before clinical use [7.3.2, WS/T 641-2018]: precision (within/between-run CV), trueness/bias (vs. CRM or EQA/inter-lab target), linearity/reportable range (≥5 points, low–mid–high), method comparison (≥40 patient samples, bias assessed against TEa per WS/T 403).
- **Measurement uncertainty (MU)** [7.3.3]: Type A (IQC between-run SD) + Type B (calibrator/CRM cert uncertainty), expressed as expanded uncertainty k=2 (~95% CI); required wherever a result is read against a fixed clinical decision limit.
- **Traceability chain** [6.5.2, ISO 17511]: SI unit → reference method/material (e.g., IDMS for creatinine) → manufacturer calibrator → patient result; documented per analyte.
- **Biological reference intervals** [7.3.4]: manufacturer intervals locally verified (≥20 individuals) or re-established (≥120) if not transferable; age/sex/physiological-state partitioning where demographic-dependent (ALP in children, creatinine by age/sex, pregnancy trimesters).
- **Critical values (危急值)** [7.3.6/7.4.1, WS/T 616]: e.g., glucose <2.2 or >22.2 mmol/L; K⁺ <2.8 or >6.2 mmol/L; Na⁺ <120 or >160 mmol/L; notification target ≤30 min with logged read-back.

### 检验后 (Post-examination) [clause 7.4]
- Auto-verification (自动审核) rules, if used, must be documented, validated, and periodically re-reviewed.
- Reflex-testing algorithms (e.g., abnormal liver panel triggering add-on tests) must be a documented SOP, not an ad hoc technologist decision.
- Result comparability across duplicate/multi-site analyzers checked ≥2×/year.

### 质量保证 (Quality Assurance) [clause 7.3.7 ensuring quality of results; clause 8.1-8.8.2 management system close]
- **IQC**: Westgard multi-rule (1-3s, 2-2s, R-4s, 4-1s, 10x) applied per analyte, ≥1×/24 h or per batch, minimum 2 QC concentration levels.
- **EQA** [GB/T 27043]: participation required for every reportable analyte, commonly ≥2–3×/year (national scheme, 5 samples/event typical); unsatisfactory performance triggers root-cause investigation, corrective action, and a look-back review of patient results issued since the last satisfactory event.
- Where no formal EQA exists, alternative performance assessment (inter-lab comparison / retained-sample retesting) at a defined frequency substitutes.

## Frameworks Introduced
- **Allowable Total Error (TEa, 允许总误差)**: TotalError=|bias|+1.96×CV (or 2×CV) ≤ analyte TEa (CLIA'88/WS/T 403/EQA target). When: judging if precision+trueness is fit for clinical use. How: compute from verification data vs. TEa table.
- **Calibration verification/linearity check**: ≥3–5 points across range, ≤6-month routine or trigger-based. When: after maintenance/lot-change/QC excursion, and routinely. How: recover assigned values within limits at each level.
- **Traceability chain documentation**: SI → reference method/material → calibrator → result. When: every quantitative analyte's calibrator. How: manufacturer traceability statement on file, linked to SOP.

## Key Concepts
- **TEa (允许总误差)** — max combined bias+imprecision permitted for clinical usability [method validation].
- **Calibration verification (校准验证)** — periodic proof the calibration curve still recovers correct values.
- **Metrological traceability (计量学溯源性)** — documented chain linking a result to an SI-traceable reference.
- **Measurement uncertainty (测量不确定度, MU)** — expanded uncertainty (k=2) combining QC imprecision + calibrator uncertainty.
- **Method comparison (方法学比对)** — ≥40 patient samples vs. reference/previous method to assess bias.
- **H/I/L index (溶血/黄疸/脂血指数)** — interference flags used to reject/annotate results.
- **Reflex testing (反射性检测)** — pre-defined add-on test auto-triggered by an abnormal primary result.
- **Auto-verification (自动审核)** — rule-based automatic release of results meeting validated criteria.

## Mental Models
- **Use "one budget, three inputs"** for method acceptability: bias, CV, and their combination (total error) must all fit inside the single TEa envelope — a method can fail even with excellent CV if bias is too large, or vice versa.
- **Use "trigger OR calendar"** for calibration verification: whichever comes first between a defined event (maintenance/lot change/QC shift) and the ≤6-month calendar limit forces re-verification.
- **Think of traceability as a chain, not a certificate**: every link (reference method/material → calibrator → instrument) must be documented; a missing link breaks defensibility even if the final number looks right.

## Anti-patterns
- **Verifying only precision (CV) and skipping trueness/bias**: passes an internally-consistent but systematically wrong method.
- **Treating calibration verification as a fixed 6-month checkbox only**: misses required re-verification after a reagent-lot change or QC trend, which are independent triggers.
- **Applying manufacturer reference intervals without local verification**: population differences (age/sex/ethnicity) can make an unverified interval clinically misleading.
- **Skipping H/I/L interference flagging**: releases a numerically "in range" result that is analytically invalid due to hemolysis/lipemia/icterus.

## Reference Tables

| Topic | Criterion |
|---|---|
| TEa formula | \|Bias\|+1.96×CV (or 2×CV) ≤ TEa (source: CLIA'88 / WS/T 403-2012 / EQA target) |
| Typical TEa | Glucose ≈10%; Cholesterol ≈10%; ALT/AST ≈20%; Creatinine ≈15%; Urea ≈9% |
| Calibration verification | ≥3–5 points, low/mid/high; trigger = maintenance/lot-change/QC-shift OR routine ≤6 months |
| Inter-instrument comparison | ≥2×/year, bias ≤½ TEa |
| MU | Type A (IQC SD) + Type B (calibrator/CRM cert), expanded k=2 (~95% CI) |
| Traceability chain | SI → reference method/material (e.g., IDMS) → calibrator → result |
| IQC | Westgard multi-rule (1-3s/2-2s/R-4s/4-1s/10x); ≥2 levels; ≥1×/24h or per batch |
| EQA | All reportable analytes; ≥2–3×/year (~5 samples/event); fail → root-cause + look-back review; no-scheme → alternative assessment ≥2×/year |
| Critical values | Glucose <2.2 or >22.2 mmol/L; K⁺ <2.8 or >6.2 mmol/L; Na⁺ <120 or >160 mmol/L; notify ≤30min + read-back |

## Worked Example
An assessor reviews a creatinine method after a reagent-lot change. Records show routine calibration verification was last done 4 months ago (within the ≤6-month window), so the lab concluded no action was needed. Finding: lot change is an *independent* trigger requiring re-verification regardless of calendar timing — this was skipped, and QC that day showed a small undetected shift. Root cause: SOP referenced only the calendar interval, not event-based triggers. Corrective action: SOP revised to require verification on *either* trigger; patient results since the lot change reviewed retrospectively against TEa.

## Key Takeaways
- Chemistry's accreditation logic centers on defensible quantitative numbers: TEa, calibration verification, traceability, and MU together prove a result is "close enough" and monitored.
- Verification must cover precision, trueness, AND linearity — passing only one is insufficient.
- Calibration verification triggers are event-based (maintenance/lot/QC shift) as well as calendar-based (≤6 months) — either alone is incomplete.
- Reference intervals and critical values must be locally verified/defined, not merely inherited from the manufacturer.

## Connects To
- **Ch 5 (Process — examination)**: TEa, calibration verification, traceability, and MU are chemistry's concrete instantiation of the generic method-validation and metrological-traceability clauses.
- **Ch 4 (Resources — Equipment/Reagents)**: inter-instrument comparison and new-lot verification refine the generic equipment/reagent-management requirements for a quantitative discipline.
- **Ch 6 (Management System Requirements)**: EQA failures and QC excursions feed the same nonconforming-work, corrective-action, and management-review cycle as other disciplines.
