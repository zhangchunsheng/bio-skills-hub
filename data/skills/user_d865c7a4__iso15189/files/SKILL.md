---
name: iso15189-accreditation
description: |
  Knowledge base distilled from anonymized reference materials on ISO 15189:2022 medical
  laboratory accreditation. Use when preparing a medical laboratory
  for ISO 15189 / CNAS-CL02 accreditation or assessment (迎检) — interpreting clauses,
  verification vs validation, IQC/EQA and QC design, measurement uncertainty and traceability,
  discipline-specific requirements (haematology, body fluids, chemistry, immunology, microbiology,
  transfusion, histopathology, cytopathology, molecular diagnostics), POCT, LIS/data control,
  laboratory safety and biosafety, and the CNAS accreditation application, on-site assessment,
  and application-form annexes. Also use to study the reference material or look up a term or threshold.
cowork:
  category: research
  icon: BookOpen
---

# ISO 15189:2022 Medical Laboratory Accreditation — Interpretation & Assessment Guide

Distilled from anonymized reference materials on ISO 15189:2022 medical laboratory accreditation.
The reference material provides a clause-by-clause interpretation of ISO 15189:2022 (adopted in China as **CNAS-CL02:2023**) paired
with, for each clause, a **迎检思路** — what a lab must actually have, do, and show to pass a CNAS on-site
assessment. 23 chapter files across three parts: the general standard (Ch 1–7), discipline-specific requirements
(Ch 8–18), and the accreditation application itself (Ch 19–20).

## How to Use
- **Answering a clause question** → read the matching chapter file, then check `cheatsheet.md` for the decision rule.
- **A discipline question** (e.g. "what does microbiology need for AST QC?") → read that discipline chapter (Ch 8–18) **plus** the generic chapter it refines (Ch 4/5A/5B/6). The discipline document adds requirements on top of the generic clause; it does not restate it.
- **A quick threshold or "how often / how many"** → `cheatsheet.md` first.
- **A term** → `glossary.md`. **A repeated technique** (sigma QC, top-down MU, traceability chain) → `patterns.md`.
- **Preparing an application** → Ch 19 (process, eligibility, on-site mechanics) then Ch 20 (annex-by-annex worked examples).
- Clause numbers cite ISO 15189:2022 / CNAS-CL02:2023. Discipline rules cite the application documents CNAS-CL02-A00x. Verify any figure against the current published document before using it in a formal submission.

## Core Frameworks & Mental Models

- **"Performed ≠ met" (the master rule)**: a requirement is satisfied only by a dated, signed, attributable **record** that it was verified — not by the activity having happened. Assessors chase the record. This underlies every chapter.
- **Define → Provide → Verify → Record** (resource pattern, clause 6): applies to personnel, facilities, equipment, reagents, and external services alike. The record is the evidence.
- **PDCA management-system loop** (clause 8): policy/objectives → controlled documents/records → risk & opportunity → nonconformity/corrective action → evaluation (internal audit + quality indicators) → management review → revised objectives. Labs pick **Option A** (self-contained QMS) or **Option B** (leverage ISO 9001) — almost all CNAS labs use Option A.
- **Verify vs Validate** (clause 7.3): unmodified adopted method → **verification (验证)** (precision, trueness, linearity, reference-interval applicability); LDT / modified / off-label → full **validation (确认)** (adds measurement uncertainty, LoB/LoD/LoQ, analytical specificity). Under-classifying an LDT as verify-only is a classic serious finding.
- **Risk-based thinking across the pathway** (clause 5.6, new in 2022): identify and mitigate patient risk continuously across pre-/examination/post-stages using probability × severity — not as an annual form. Replaces the old "preventive action" clause.
- **QC design by sigma** (clause 7.3.6): σ = (TEa − |bias|) / CV chooses Westgard rule stringency and QC frequency per analyte. A Westgard violation → **stop releasing results**, investigate, correct, resume.
- **EQA/PT discipline**: participate for every in-scope test with routine staff/method; |z| ≤ 2 satisfactory, |z| ≥ 3 unsatisfactory; no scheme exists → alternative comparison ≥2×/year. External verification is never optional.
- **Traceability chain** (clause 6.5, ISO 17511): patient result → calibrators → CRM/reference procedure → SI; where no higher-order reference exists, document traceability to the manufacturer's reference system.
- **Contamination defence-in-depth** (molecular, clause 6.3 / 194号): four physically separated PCR areas + uni-directional flow + air-pressure gradient + per-run controls together — the facility design IS the primary control.
- **Closed-loop critical value (危急值)** (clause 7.4): detect → notify within a time limit → read-back → record who/when/what/action. "Closed" only when confirmed receipt is logged.
- **Discipline-refines-generic** (Ch 8–18): always read the discipline application document together with the generic clause it sits on. **Six-annex mutual consistency** (Ch 20): the application form and 附表1–6 must agree on who applies, who is competent, what is tested, how each clause is evidenced, and proof of external verification.

## Chapter Index

**Part 1 — The ISO 15189:2022 standard, clause by clause**
| Ch | Title | Covers |
|----|-------|--------|
| 1 | [Terms and Definitions](chapters/ch01-terms-and-definitions.md) | Clause 3 vocabulary; verify vs validate; EQA vs PT; sample vs specimen |
| 2 | [General Requirements](chapters/ch02-general-requirements.md) | Clause 4 — impartiality, confidentiality, patient-related requirements |
| 3 | [Structure & Governance](chapters/ch03-structure-and-governance.md) | Clause 5 — legal entity, director, activities, authority, objectives, risk management |
| 4a | [Resources — People & Facilities](chapters/ch04a-resources-people-facilities.md) | Clause 6.1–6.3 — personnel competence/authorization, facilities & environment |
| 4b | [Resources — Equipment & Reagents](chapters/ch04b-resources-equipment-reagents.md) | Clause 6.4–6.8 — equipment, calibration/traceability, reagents, service agreements, external provision |
| 5A | [Process — Pre-exam & Examination](chapters/ch05a-process-pre-examination-and-examination.md) | Clause 7.2–7.3 — collection/consent/rejection, verify/validate, MU, reference intervals, IQC/EQA |
| 5B | [Process — Post-exam & Controls](chapters/ch05b-process-post-examination-and-controls.md) | Clause 7.4–7.8 — reporting, critical values, nonconforming work, data, complaints, continuity |
| 6 | [Management System](chapters/ch06-management-system.md) | Clause 8 — documents/records, risk, CAPA, internal audit, quality indicators, management review |
| 7 | [POCT Additional Requirements](chapters/ch07-poct.md) | Annex A — governance, verification/comparability, QC, operator training for point-of-care testing |

**Part 2 — Discipline-specific requirements (CNAS-CL02-A00x)**
| Ch | Title | Covers |
|----|-------|--------|
| 8 | [Clinical Haematology](chapters/ch08-haematology.md) | Blood-film morphology competence, analyzer flags, comparability |
| 9 | [Clinical Body Fluids](chapters/ch09-body-fluids.md) | Urinalysis/manual microscopy review, body-fluid cell counting |
| 10 | [Clinical Chemistry](chapters/ch10-clinical-chemistry.md) | TEa budget, calibration verification, traceability, inter-instrument comparison, Westgard IQC |
| 11 | [Clinical Immunology](chapters/ch11-immunology.md) | Qualitative cut-off/grey-zone, retest/confirmation algorithms, QC for qualitative tests |
| 12 | [Clinical Microbiology](chapters/ch12-microbiology.md) | Biosafety, reference-strain QC, AST breakpoint version control, tiered reporting |
| 13 | [Transfusion Medicine](chapters/ch13-transfusion.md) | ABO double-typing, antibody screen, crossmatch, cold chain, traceability |
| 14 | [Histopathology](chapters/ch14-histopathology.md) | Fixation, grossing, IHC/frozen section, staffing & competence, retention |
| 15 | [Cytopathology](chapters/ch15-cytopathology.md) | Screener workload cap, rescreening, cyto-histo correlation, TBS |
| 16 | [Molecular Diagnostics](chapters/ch16-molecular-diagnostics.md) | Four-area PCR lab, air-pressure gradient, per-run controls, NGS validation |
| 17 | [Data Control & Information Management](chapters/ch17-data-and-information.md) | Clause 7.6 — LIS validation, access/audit trail, backup/restore, downtime, external hosting |
| 18A | [Safety — Governance & Biosafety](chapters/ch18a-safety-governance-and-biosafety.md) | Risk grading, BSL levels, biosafety cabinets, PPE, incident/exposure reporting |
| 18B | [Safety — Chemical/Fire/Transport/Waste](chapters/ch18b-safety-chemical-fire-transport-waste.md) | Chemical & radiation safety, fire, electrical, specimen transport (UN3373), medical-waste disposal |

**Part 3 — Applying for accreditation (下篇)**
| Ch | Title | Covers |
|----|-------|--------|
| 19 | [Applying & Assessment Prep](chapters/ch19-applying-and-assessment-prep.md) | CNAS document system, accreditation process, eligibility/acceptance, on-site assessment mechanics |
| 20 | [Application Form Worked Examples](chapters/ch20-application-form-worked-examples.md) | 申请书 + 附表1–6 filled field-by-field with the rule for each |

## Topic Index (where to look)
- **Verification / validation / LDT** → Ch 1, Ch 5A, `cheatsheet.md`
- **IQC / Westgard / sigma-metric** → Ch 5A, `patterns.md`, `cheatsheet.md`
- **EQA / PT / proficiency testing / no-scheme alternative** → Ch 5A, `cheatsheet.md`
- **Measurement uncertainty (MU)** → Ch 5A, `patterns.md`
- **Metrological traceability / calibration** → Ch 4b, Ch 10, `patterns.md`
- **Reference intervals / clinical decision limits** → Ch 1, Ch 5A
- **Critical values (危急值) / reporting / TAT** → Ch 5B
- **Nonconforming work / CAPA / risk management** → Ch 3 (5.6), Ch 5B, Ch 6
- **Internal audit / quality indicators / management review** → Ch 6
- **Personnel competence & authorization** → Ch 4a; discipline specifics in Ch 8–18
- **Facilities / environment / incompatible activities** → Ch 4a; PCR zoning in Ch 16
- **Equipment / reagents / lot acceptance / suppliers** → Ch 4b
- **POCT** → Ch 7
- **LIS / data integrity / audit trail / backup / downtime** → Ch 5B, Ch 17
- **Biosafety / BSL / biosafety cabinet / PPE** → Ch 18A
- **Chemical/fire/electrical safety, specimen transport, waste** → Ch 18B
- **Molecular / PCR / NGS / contamination control** → Ch 16
- **Transfusion / ABO / crossmatch / cold chain** → Ch 13
- **Pathology fixation / IHC / frozen section / workload caps** → Ch 14, Ch 15
- **CNAS application / eligibility / on-site assessment / annexes (附表)** → Ch 19, Ch 20

## Supporting Files
- `glossary.md` — 98 key terms (English + 中文) with clause references, alphabetical.
- `patterns.md` — recurring techniques (Define→Provide→Verify→Record, PDCA, sigma QC, top-down MU, traceability chain, contamination defence, six-annex consistency) with when/how/trade-offs.
- `cheatsheet.md` — decision rules, thresholds, discipline signature rules, application eligibility gates, and assessment "tells & smells."

## Scope & Limits
- This is a **study and preparation aid** distilled from one Chinese reference book, not the standard itself and not official CNAS guidance. Always confirm against the current published **ISO 15189:2022 / CNAS-CL02:2023** and the relevant discipline application document (**CNAS-CL02-A00x**) before relying on a figure in a formal submission or audit response.
- Some numeric thresholds are the book's stated **defaults** or common practice, not fixed standard requirements — the cheatsheet marks these. Discipline chapters vary in depth; where the source pages thinned out (parts of Ch 15) the file says so rather than inventing figures.
- Does not evaluate a specific lab's compliance or substitute for a qualified assessor; use it to know what to look for and prepare.
