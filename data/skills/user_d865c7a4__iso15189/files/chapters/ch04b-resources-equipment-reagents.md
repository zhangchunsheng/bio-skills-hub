# Chapter 4b: Resource Requirements — Equipment, Calibration, Reagents, Service Agreements & External Provision (第四章 资源要求：设备、设备校准和计量溯源性、试剂和耗材、服务协议、外部提供的产品和服务)

## Core Idea
Sections 4–8 extend Chapter 4's "define → verify → record" logic to physical/technical resources: equipment must be proven fit-for-purpose before and throughout use; every measurement must trace back to a defensible reference; every reagent lot must be verified before clinical release; and every externally sourced input — service agreement or supplier-provided product — remains fully the lab's responsibility even though someone else performed it.

## Frameworks Introduced
- **Equipment lifecycle control (6.4.1–6.4.7)**: acceptance testing before use → labeled operational status → maintenance/repair with post-repair re-verification → retrospective impact assessment on failure → adverse-event reporting → a complete equipment file. When to use: for every item "significant to lab activities." How: one equipment dossier per asset covering all lifecycle stages, not just a purchase record.
- **Risk-based calibration interval setting (6.5.1)**: interval derived from manufacturer guidance, use frequency, stability/drift history, and criticality — never a copy-pasted default. When to use: at initial calibration-plan design and whenever drift or usage pattern changes. How: document the *rationale* alongside the interval in the calibration plan.
- **Traceability chain documentation (6.5.2)**: link each patient result back through calibrator → reference material/method → SI unit (or, absent a higher-order reference, to the manufacturer's own reference system, explicitly documented as the accepted alternative). When to use: for every quantitative measurand. How: a one-page traceability diagram per analyte/test family.
- **Lot-to-lot verification (6.6.2)**: before releasing a new reagent/consumable lot, run it in parallel with the current lot/controls and compare against defined acceptance criteria. When to use: every lot change for tests affecting result quality. How: parallel-testing protocol + statistical acceptance criteria (e.g., bias within total allowable error) + sign-off gate before clinical use.
- **Risk-tiered supplier evaluation (6.8.1–6.8.2)**: apply full selection/monitoring/reevaluation rigor to critical providers (referral labs, calibration services, critical reagents/equipment) and a lighter process to non-critical ones (office supplies), while retaining full accreditation responsibility regardless of tier. When to use: building or reviewing the approved-supplier list. How: criteria-scored evaluation, periodic reevaluation cycle, documented retain/replace decisions on underperformance.

## Key Concepts
- **Equipment acceptance testing (设备验收试验)** — pre-use verification of performance specs (precision, accuracy, linearity, carryover), distinct from and prior to calibration [6.4.2].
- **Equipment status labeling (设备状态标识)** — commonly a three-colour tagging convention showing usable / restricted / out-of-service status [interpretive practice, 6.4.3–6.4.5].
- **Retrospective impact assessment (既往结果回顾性评估)** — mandatory review of prior results when equipment is later found defective, deciding whether recall/reissue is needed [6.4.5, linked to 8.7].
- **Equipment records/file (设备档案)** — ten-element minimum record set: identity, manufacturer/model/serial, service contact, receipt/in-service dates, condition on receipt, instructions, verification records, maintenance schedule/history, damage/repair/modification history, performance records [6.4.7].
- **Metrological traceability (计量溯源性)** — unbroken calibration chain to SI units/reference material/reference method, or, where none exists, to the manufacturer's documented reference system [6.5.2].
- **Intermediate check (中间检查)** — interim confidence check (e.g., QC trend review) between full calibrations [interpretive content under 6.5].
- **Lot acceptance/lot-to-lot verification (批号验收/批间验证)** — parallel-testing gate before releasing a new reagent lot [6.6.2].
- **Reagent/consumable records (试剂耗材记录)** — lot-level traceability: identity, manufacturer, lot/batch number, receipt/expiry/in-service/withdrawal dates, condition on receipt, verification/performance records [6.6.6].
- **Service agreement (服务协议)** — documented, periodically reviewed scope/TAT/acceptance-rejection terms for internal SLAs and external referral-lab contracts alike [6.7.1].
- **Externally provided products and services (外部提供的产品和服务)** — broad umbrella: referred testing, consultation, calibration/maintenance services, reagents/equipment, and support services (IT, cleaning, waste disposal); lab keeps full responsibility [6.8.1].

## Mental Models
- **Use the "three gates" model for anything physical entering the lab (equipment, reagent lot, calibrator)**: Gate 1 = acceptance/verification before use, Gate 2 = ongoing monitoring/intermediate checks during use, Gate 3 = impact assessment and reporting if it later fails. Missing any gate is the recurring nonconformity pattern across 6.4–6.6.
- **Think of the equipment file as the "biography" of an asset**: from receipt condition through every maintenance, repair, and performance event to eventual retirement — assessors read it front-to-back looking for gaps, not just presence.
- **Think of metrological traceability as a "chain with no acceptable missing link, but an acceptable substitute link"**: when no reference measurement procedure exists (common in immunoassays), documenting the manufacturer's own system as the traceability anchor is valid — silence on traceability is not.
- **Use risk-tiering for supplier oversight**: not all "external provision" deserves equal scrutiny — calibration providers and referral labs are examined like extensions of the lab itself, while low-risk consumable suppliers get a lighter, still-documented process.

## Anti-patterns
- **Skipping acceptance testing after relocation/major repair**: re-installing or repairing equipment and returning it to service without re-verifying performance violates 6.4.2's requirement that acceptance criteria be re-confirmed, not just assumed carried over.
- **Filing calibration certificates without review**: accepting a calibration certificate into a folder without staff actually reviewing its traceability statement and measurement uncertainty is a "paper compliance" failure assessors specifically probe for.
- **Changing reagent lots without lot-to-lot verification**: releasing a new lot for clinical use without parallel-testing against acceptance criteria is a high-impact nonconformity directly tied to patient-facing result discrepancies [6.6.2].
- **Using expired reagents without re-verification**: default use past labeled expiry, absent a documented justification/re-verification, is nonconforming regardless of apparent performance [6.6.3].
- **Excluding POCT and support services from oversight**: point-of-care devices/reagents managed by clinical departments, and support services like IT/cleaning/waste-disposal vendors, are commonly and incorrectly left out of central quality oversight and the supplier list, but both fall within 6.6/6.8 scope.
- **Treating supplier approval as a one-time event**: an approved-supplier list that is never revisited fails 6.8.2's expectation of ongoing performance monitoring and periodic reevaluation.

## Reference Tables

**Equipment lifecycle control points [6.4.1–6.4.7]**
| Stage | Requirement | Evidence expected |
|---|---|---|
| Before use | Acceptance testing vs. specified requirements | IQ/OQ/performance verification data |
| In routine use | Authorized/trained operators only; current instructions available | Authorization list cross-check; SOP at workstation |
| Status display | Clear usable/restricted/out-of-service labeling | Status tag/log |
| Maintenance | Scheduled preventive maintenance per manufacturer/lab procedure | PM schedule + completion records |
| On defect found | Quarantine; retrospective impact assessment; recall/reissue if needed | Impact-assessment record; recall log |
| Adverse incident | Investigate; report to manufacturer/authority | Incident report + reporting confirmation |
| Ongoing file | 10-element equipment record set maintained | Equipment dossier |

**Equipment record — ten elements [6.4.7]**
| # | Element |
|---|---|
| 1 | Identity (unique ID) |
| 2 | Manufacturer, model, serial number |
| 3 | Service/support contact |
| 4 | Receipt date and date placed in service |
| 5 | Location |
| 6 | Condition on receipt (new/used/refurbished) |
| 7 | Manufacturer instructions |
| 8 | Verification records confirming acceptance criteria met |
| 9 | Maintenance performed and schedule |
| 10 | Damage/malfunction/modification/repair history and performance records (incl. calibration/PT) |

**Calibration interval — basis for justification (not a fixed default) [6.5.1]**
| Factor | Effect on interval |
|---|---|
| Manufacturer recommendation | Baseline starting point |
| Frequency of use | Higher use → shorter interval |
| Stability/drift history | Unstable → shorter interval |
| Criticality/risk of the test | High clinical risk → shorter interval, tighter monitoring |
| Regulatory requirement | May set a floor/minimum |

**Reagent/consumable lifecycle control points [6.6.1–6.6.6]**
| Stage | Requirement | Evidence expected |
|---|---|---|
| Selection/purchasing | Documented specification/criteria | Purchase spec; approved list |
| Receipt/new lot | Lot acceptance / lot-to-lot verification before release | Parallel-test record vs. acceptance criteria |
| Storage | FIFO/FEFO, condition monitoring, min-stock policy | Inventory log; temperature log |
| Use | Manufacturer instructions available at point of use | Current package insert / SOP |
| Adverse event | Investigate and report to manufacturer/authority | Incident log |
| Records | Identity, manufacturer, lot/batch, receipt/expiry/in-service/withdrawal dates, verification/performance | Lot record/register |

**Externally provided products/services — risk tiering [6.8.1–6.8.2]**
| Category | Example | Evaluation intensity |
|---|---|---|
| Referred testing | Send-out to reference lab | High — full selection + periodic reevaluation |
| Consultation opinions | External expert review | High |
| Calibration/maintenance services | Metrology provider | High |
| Critical reagents/equipment | Analyzer reagents | High |
| Support services | IT/LIS support, cleaning, waste disposal | Moderate, still documented |
| Non-critical supplies | Office/general consumables | Lower — simplified process |

## Worked Example
**Finding**: An assessor reviews a chemistry analyzer's calibration certificate on file, but interviews reveal no lab staff can explain the certificate's stated measurement uncertainty or confirm the calibration range covers the clinically reported range. Separately, the same lab changed reagent lots for a quantitative assay two weeks prior with no parallel-testing record.
**Root cause**: Calibration certificates are filed on receipt without a review step; lot changes are treated as routine restocking rather than a quality gate.
**Corrective action**: (1) Add a mandatory certificate-review step (traceability statement + uncertainty + range coverage) with sign-off before the certificate is accepted into the equipment file [6.5.2]. (2) Implement a lot-change SOP requiring parallel testing against acceptance criteria with a hold-until-verified release gate [6.6.2].
**Clause link**: 6.5.1/6.5.2 (calibration/traceability) and 6.6.2 (lot acceptance) — both nonconformities share the same underlying pattern: a control that exists on paper but was not actively performed.

## Key Takeaways
- Equipment, calibration, and reagent controls all follow the same "three gates" pattern: verify before use, monitor during use, assess impact and report on failure.
- Calibration intervals and traceability are **risk-justified, not fixed by rule** — the book repeatedly stresses documenting *why* an interval or traceability method was chosen.
- Lot-to-lot verification is the single highest-yield reagent control to check, because skipped verification directly threatens patient-facing result validity.
- External provision (6.8) is deliberately broad — it must include support services and POCT arrangements that labs often place outside their formal quality system by default.
> [gap: pages 116-130 contain extended case-study/summary material revisiting these themes at reduced legibility; core clause content for sections 4-8 captured above with high confidence; no additional book-specific numeric thresholds beyond those in the tables above could be confirmed]

## Connects To
- **Chapter 4a** (sections 1-3): personnel authorization and facility zoning are prerequisites for equipment/reagent controls to function (e.g., only authorized staff may release results after a lot change).
- **8.7 Nonconformity management**: equipment defects and lot-verification failures route directly into corrective-action and, where relevant, result-recall processes.
- **Chapter 5 (Process Requirements)**: examination process validity assumes the resource controls in Chapter 4 (calibrated equipment, verified reagents, evaluated suppliers) are already satisfied.
