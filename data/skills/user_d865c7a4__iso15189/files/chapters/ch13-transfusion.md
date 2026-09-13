# Chapter 13: Transfusion Medicine (第十三章 临床输血检验认可要求与迎检思路)

## Core Idea
Transfusion/blood-bank accreditation layers ISO 15189 clauses on top of a zero-tolerance catastrophic-error target: an ABO-incompatible transfusion. Every discipline-specific rule in this chapter — double independent typing, forward+reverse ABO confirmation, antiglobulin control cells, electronic-crossmatch eligibility gates, the 30-minute cold-chain rule, and long-tail record retention — exists to engineer out that single failure mode. Unlike other disciplines where the main risk is analytical drift, here the primary risks are patient/sample identification integrity and closed-loop traceability from donor to recipient, so assessors probe identity-verification steps and traceability chains at least as hard as they probe the serology itself.

## Discipline-Specific Requirements

### 总体要求 (General Requirements)
- Scope must state whether the lab performs pre-transfusion compatibility testing only (血型鉴定/抗体筛查/交叉配血) or also blood-component storage/issue, since accreditation scope and legal blood-management scope may differ.
- Compliance is dual-track: beyond the CNAS microbiology-equivalent transfusion application document, the lab must simultaneously satisfy national blood-transfusion regulation (《医疗机构临床用血管理办法》) and relevant 卫生行业标准 (e.g., WS/T clinical-transfusion/reaction standards) — assessors check both the accreditation clause and the underlying legal requirement together.
- Testing capability must be available 24 hours a day (emergency surgery/trauma), so on-call staffing is itself a 总体要求, not only a personnel-resource detail.

### 结构和管理要求 (Structure & Management)
- The lab participates in the hospital's 临床用血管理委员会 (clinical blood-use management committee), contributing usage-audit data.
- Sign-off authority for blood-group/crossmatch reports is authorized **separately** from the lab's general authorized-signatory list, reflecting the direct life-safety consequence of a release error.
- Controlled SOPs must reflect the exact reagent/method combination validated locally (ABO/RhD method, antibody screen/ID method, crossmatch method) — not a generic textbook procedure.

### 人员 (Personnel)
- Transfusion staff need a specific training/certification pathway beyond general lab qualification, re-assessed ≥1×/year, covering ABO/RhD forward+reverse typing, antibody screening, crossmatch (immediate-spin/saline and antiglobulin phases), and emergency-release decision authority.
- **Double independent testing (双人双复核)** is required for every patient's initial ABO/RhD determination — not periodic QC, but a per-patient mandatory second, independent test/reading before the first result can be released.
- On-call/night staff must demonstrate documented competency equivalent to daytime staff for release decisions.

### 设施与环境 (Facilities & Environment)
- Reagent/component storage refrigerators and freezers require continuous monitoring (data logger or ≥2×/day manual check) with alarm backup; any temperature excursion triggers a documented investigation of reagent/component validity before use.
- Blood-storage areas require restricted physical access/security for chain-of-custody reasons.
- Backup power (UPS/generator) for storage refrigerators/freezers is explicitly required, feeding into the lab's 7.8 contingency plan since a storage failure is a patient-safety emergency, not just an equipment fault.

### 设备与试剂 (Equipment & Reagents)
- Core equipment: blood-bank refrigerator (2–6°C, red cells/reagents), platelet agitator/incubator (20–24°C, continuous agitation), plasma freezer (≤-18°C, commonly targeting ≤-25°C), serological centrifuge (time/speed verified against a calibrated reference), 37°C water bath/heating block for the antiglobulin phase — each independently calibrated/verified on a defined schedule.
- Reagent red cell panels and screening cells (commonly a 2–3-cell screening set; extended 8–11-cell panel for identification) require the lot-specific antigram on file; each new lot is QC'd against known positive/negative reactivity before patient use.
- Method changeover (e.g., tube → gel-card/microcolumn) requires local validation with parallel testing against the prior reference method before adoption.

### 检验前 (Pre-examination)
- Positive patient identification (two identifiers, e.g., name + unique ID) is required at both sample collection and the pre-transfusion bedside check; ambiguously labeled samples are rejected and re-drawn with no exception except through the defined emergency pathway.
- **Sample validity window**: a pretransfusion sample is valid for compatibility testing typically only ≤3 days if the patient has been transfused or pregnant within the preceding 3 months, because new alloantibodies can form in that window.
- Sample collection/labeling for transfusion testing specifically requires verification beyond the generic pre-examination rule, given the identification-error stakes.

### 检验中 (Examination)
- **ABO/RhD typing**: forward typing (cell + known anti-A/anti-B/anti-D) AND reverse typing (serum/plasma + A1/B reagent cells) are BOTH mandatory for ABO; any forward/reverse discrepancy must be resolved (repeat, extended panel, or referral) before release. Weak-D/Du testing pathway applies to initial RhD-negative results in defined patient categories.
- **Antibody screening**: performed with a 2–3-cell reagent panel at a method sensitive enough to include the antiglobulin/indirect-Coombs phase (or gel/solid-phase equivalent); a positive screen triggers antibody identification with an extended (commonly 8–11-cell) panel before crossmatch proceeds.
- **Crossmatch**: serologic crossmatch is required whenever the antibody screen is positive or there is a history of a clinically significant antibody (methods/acceptance in Reference Tables). **Electronic/computer crossmatch** is permitted only under the eligibility gate below — otherwise serologic crossmatch is mandatory.
- **AHG/Coombs control cell check**: every negative antiglobulin-phase result (screening or crossmatch) must be confirmed by adding IgG-sensitized check cells that show agglutination, ruling out a false-negative from reagent/technical failure.
- **Emergency release (紧急/应急发血)**: when compatibility testing cannot finish in time for a life-threatening emergency, a physician-signed emergency-release request permits issue of type-specific or O-type units before full testing completes; compatibility testing is still completed retrospectively, and every release is logged (authorizer, time, units, reason) and reviewed afterward.
- Massive-transfusion and neonatal/obstetric pathways are documented separately from routine and single-unit emergency release.

### 检验后 (Post-examination)
- **Bidirectional traceability**: every issued unit must be traceable donor/unit number ↔ patient ID ↔ compatibility result ↔ issuing staff ↔ time issued ↔ bedside administration confirmation, in both directions.
- Units are visually inspected before issue (bag integrity, discoloration, hemolysis, clots, expiry); failing units are quarantined, not issued.
- **30-minute cold-chain rule**: a unit removed from controlled storage for more than ~30 minutes may not return to inventory and must be discarded/specially handled.
- **Transfusion reaction investigation** follows the 10-step sequence in Frameworks below, with clerical identity check performed *before* re-testing serology since clerical error is the most common root cause. Implicated unit segment/pilot tubing and patient pre-/post-transfusion samples are retained for the investigation and afterward.

### 质量保证 / 管理体系要求 (Quality Assurance / Management System)
- Retention periods are markedly longer than the generic 2-year baseline: compatibility-testing, unit-issue, and reaction-investigation records are kept long-term (book cites a long-tail retention driven by national blood-safety regulation, commonly discussed at the ≥10-year class), while the pretransfusion patient sample itself is kept refrigerated for a shorter defined window (commonly ≥7 days post-transfusion) to support reaction workup.
- **Look-back (追溯调查)**: if a donor is later found positive for a transmissible marker, the lab must be able to trace all components issued from that donor and notify recipients' clinicians.
- Proficiency testing/EQA for ABO/RhD typing and antibody screening/identification is mandatory; unsatisfactory performance suspends reporting of the affected test pending investigation and retraining.
- Risk management explicitly names ABO-incompatible transfusion as the top catastrophic-severity risk, with double-ID-check, double independent typing, and barcode/electronic verification as documented controls in the risk register.
- Management review and internal audit track transfusion-specific KPIs: ABO mistyping near-misses, crossmatch TAT, emergency-release frequency/appropriateness, reaction rate and workup completeness, and EQA performance.
- Blood-bank nonconformities (ABO/RhD discrepancy, failed crossmatch, reagent QC failure, storage temperature excursion, reaction investigation) are escalated immediately rather than batched for periodic review, given patient-safety severity.

## Frameworks Introduced
- **Double independent ABO/RhD typing (双人双复核)**: two people/two independent tests required for every initial patient blood-type determination. When to use: every new patient typing. How: second reader/tester blind to the first result, discrepancies resolved before release.
- **Electronic crossmatch eligibility gate**: two on-file ABO/RhD determinations + current negative antibody screen + validated LIS logic — all three required, or fall back to serologic crossmatch. When to use: routine crossmatch requests. How: hard-code the eligibility check in the LIS rather than relying on operator judgment.
- **Ten-step transfusion-reaction workup**: stop → clerical check → retype/crossmatch → DAT → hemolysis check → further workup → documented classification → report → corrective action. When to use: any suspected transfusion reaction. How: mandatory checklist completed before any conclusion is signed.
- **Bidirectional traceability chain**: donor/unit ↔ patient ↔ tester ↔ time, verifiable in both directions plus look-back capability. When to use: every issued component. How: barcode/electronic unit-patient linkage plus retained records supporting retrospective donor-to-recipient tracing.

## Key Concepts
- **Forward/reverse typing (正定型/反定型)** — cell-typing with known antisera plus serum-typing against known reagent cells; both required for ABO, discrepancies resolved before release.
- **Antibody screening / identification (抗体筛查/抗体鉴定)** — 2–3-cell panel to detect, extended 8–11-cell panel to specify, clinically significant alloantibodies.
- **Electronic crossmatch (电子交叉配血)** — LIS-based compatibility determination valid only under the eligibility gate above.
- **AHG/Coombs control cell (抗人球蛋白质控细胞)** — IgG-sensitized cells confirming a negative antiglobulin-phase result is genuine.
- **Emergency release (紧急/应急发血)** — physician-authorized issue ahead of completed compatibility testing, always followed by retrospective completion and review.
- **Bidirectional traceability (双向可追溯性)** — donor/unit-to-patient and patient-to-donor/unit linkage.
- **Look-back (追溯调查)** — retrospective recipient tracing after a donor is found positive for a transmissible marker.
- **Sample validity window (标本有效期)** — pretransfusion sample validity, ≤3 days if recently transfused/pregnant.
- **30-minute rule (30分钟规则)** — cold-chain-out time limit before a unit must be discarded rather than restocked.

## Mental Models
- **Use "engineered redundancy" as the lens for every serology step**: forward+reverse typing, double independent testing, and AHG control cells all exist because a single test/single reader is not trusted to catch a catastrophic ABO error — redundancy is the control, not a formality.
- **Think of electronic crossmatch as "borrowing trust from two prior tests"**: it is only valid because two independent ABO/RhD results and a current negative screen already exist; remove any one leg and the software has nothing to stand on.
- **Use "clerical error first" as the default hypothesis in any reaction workup**: because mislabeling/misidentification is the most common root cause, the workup sequence checks identity before it re-tests serology.
- **Think of retention periods here as proportional to consequence tail-length**: chemistry results have a short dispute window, but transfusion has legal/infectious-disease look-back exposure spanning years, so records are kept far longer than the generic 2-year baseline.

## Anti-patterns
- **Releasing an ABO/RhD result from forward typing alone**: misses subgroup/technical discrepancies that reverse typing would catch — the classic route to a catastrophic mistyping.
- **Allowing electronic crossmatch without verifying the eligibility gate**: substitutes software logic for a safety check that hasn't actually been earned by the patient's testing history.
- **Skipping the AHG/Coombs control cell on a negative antiglobulin result**: a negative result is meaningless if the reagent's activity itself was never confirmed.
- **Returning a unit to inventory after it exceeded the ~30-minute cold-chain-out limit**: temperature-abuse risk cannot be verified visually; this is a common cited nonconformity.
- **Concluding a transfusion-reaction classification before completing the full workup (e.g., skipping DAT)**: produces an unsupported clinical conclusion and hides a possible lab/clerical root cause.
- **Applying the generic 2-year record-retention baseline to transfusion records**: undercuts the legal/look-back retention this discipline specifically requires.

## Reference Tables

**Blood-group serology core rules**
| Step | Requirement |
|---|---|
| ABO typing | Forward AND reverse typing both mandatory; discrepancies resolved before release |
| RhD typing | Standard typing; weak-D/Du pathway for initial RhD-negative in defined categories |
| Initial patient typing | Double independent testing (双人双复核) |

**Antibody screening & identification**
| Stage | Panel size | Trigger |
|---|---|---|
| Screening | 2–3 reagent cells | Routine pretransfusion workup |
| Identification | 8–11 cell extended panel | Positive screen |

**Crossmatch methods & acceptance**
| Method | When required | Acceptance |
|---|---|---|
| Serologic (major+minor, saline+AHG phase) | Positive antibody screen or antibody history | No agglutination/hemolysis at all phases, both sides |
| Electronic/computer | Only if: 2 on-file ABO/RhD results + current negative screen + validated LIS logic | System-generated compatibility per validated logic |

**Reagent/sample storage & monitoring**
| Item | Condition | Monitoring |
|---|---|---|
| Red cells / reagent red cells & antisera | 2–6°C | Continuous logger or ≥2×/day + alarm |
| Platelets | 20–24°C, continuous agitation | Continuous |
| Plasma | ≤-18°C (commonly ≤-25°C target) | Continuous logger + alarm |
| AHG/antiglobulin reagent | Per manufacturer | Coombs control cell each use |

**Emergency release procedure**: physician written/signed request → issue type-specific or O-type unit → retrospective completion of full compatibility testing → log (authorizer, time, units, reason) → post-hoc review by transfusion committee/pathologist.

**Transfusion-reaction investigation sequence**: stop transfusion → clerical check → repeat ABO/RhD + crossmatch → DAT → hemolysis comparison (pre vs post sample) → additional workup (e.g., unit culture) → documented classification → hemovigilance report → corrective action.

**Sample and record retention**
| Item | Retention |
|---|---|
| Pretransfusion patient sample | Refrigerated, commonly ≥7 days post-transfusion |
| Sample validity for testing | ≤3 days if transfused/pregnant in preceding 3 months |
| Compatibility/issue/reaction records | Long-term, materially longer than generic 2-year baseline (≥10-year class per national blood regulation) |
| Cold-chain-out unit | Discard if out of controlled storage >~30 minutes |

## Worked Example
An assessor reviews an emergency electronic-crossmatch case: a trauma patient's unit was released via electronic crossmatch, but the LIS history showed only one prior ABO/RhD determination on file (not the required two), and the antibody-screen record from the current admission was missing. Finding: the electronic-crossmatch eligibility gate was not actually met, so the "compatible" result had not earned the redundancy it relied on. Root cause: the LIS allowed manual override of the electronic-crossmatch option without enforcing the eligibility check. Corrective action: hard-code the two-determination-plus-negative-screen check into the LIS so electronic crossmatch cannot be selected unless both conditions are system-verified; retrospectively, the case is reworked with a full serologic crossmatch. This illustrates why electronic crossmatch is a *conditional* framework, not a default shortcut.

## Key Takeaways
- Every discipline-specific rule in this chapter is ultimately a defense against one catastrophic failure mode: ABO-incompatible transfusion — forward+reverse typing, double independent testing, and AHG control cells are redundancy layers, not paperwork.
- Electronic crossmatch and emergency release are both *conditional* frameworks: each has explicit eligibility criteria that must be system- or process-verified, never assumed.
- Traceability is bidirectional and long-tailed: donor-to-patient linkage and look-back capability must work retrospectively, years after issue, which drives this chapter's much longer record-retention rules.
- The reaction-investigation workup checks identity (clerical error) before it re-checks serology, because misidentification — not antibody complexity — is the most common root cause of acute reactions.

## Connects To
- **Ch 4 (Resources — Personnel/Facilities/Equipment)**: double independent typing and dedicated transfusion-training pathways are this discipline's concrete instantiation of the generic competency-assessment clause; cold-chain storage/backup-power rules refine the generic facilities/equipment clauses.
- **Ch 5 (Process — pre/examination/post-examination)**: sample-validity windows, forward/reverse typing, and the transfusion-reaction workup refine the generic pre-examination identification rules and the 7.4/7.5 critical-value and nonconforming-work processes for a life-safety-critical test.
- **Ch 6 (Management System Requirements)**: ABO-incompatible-transfusion risk registration, look-back capability, and long-tail retention are this discipline's specific application of the generic risk-management (8.5), document-control (8.3), and record-retention requirements.
