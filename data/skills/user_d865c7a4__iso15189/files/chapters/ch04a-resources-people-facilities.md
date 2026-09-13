# Chapter 4a: Resource Requirements — General, Personnel, Facilities & Environment (第四章 资源要求：总体要求、人员、设施和环境条件)

## Core Idea
Chapter 4 interprets ISO 15189:2022 clause 6 (Resource Requirements). Sections 1–3 establish that a lab must first *determine and secure* the inputs — general resource adequacy, competent authorized personnel, and suitable/controlled facilities — before any process (Chapter 5) can be trusted. The recurring assessment logic: a requirement is not "met" until there is a **documented, dated, signed record** showing it was verified, not merely performed informally.

## Frameworks Introduced
- **Resource-adequacy planning (6.1 总体要求)**: the lab must identify all resources (personnel, facilities, equipment, reagents/consumables, services) needed for its declared scope, evaluate them against requirements, and show planning/budget evidence tying resources to scope. When to use: at annual planning and whenever scope changes. How: maintain a resource inventory/catalog cross-referenced to the test menu; document contingency actions when resources are insufficient.
- **Competence-before-authorization chain (6.2.2 → 6.2.3)**: define competence requirements for a role → assess competence using ≥2 objective methods → only then issue a scoped, dated authorization. When to use: onboarding, role change, new method introduction. How: job description with competence criteria → competence assessment record → authorization document referencing that specific assessment.
- **Facility risk-zoning model (6.3.2, illustrated via PCR labs)**: physically/procedurally separate "incompatible activities" (清洁区/半污染区/污染区 or reagent-prep/specimen-prep/amplification/product-analysis zones) with unidirectional workflow. When to use: any workflow where cross-contamination or interference is plausible. How: floor plan showing zoning + access control + one-way personnel/sample flow.

## Key Concepts
- **Resource adequacy (资源充分性)** — resources must be sized to actual scope, not generic; verified via management review inputs [6.1].
- **Competence requirements (岗位能力要求)** — documented education, qualification, training, skills, experience per role, defined before staffing [6.2.2].
- **Authorization (授权)** — formal, scoped grant of permission tied to a competence-assessment outcome, not to training attendance alone [6.2.3].
- **Continuing education (继续教育和专业发展)** — planned, tracked CE/in-service training beyond initial onboarding [6.2.4].
- **Personnel records (人员记录)** — the mandated file: certificates, job description, competence/training/CE records, performance review, incident/exposure/immunization history [6.2.5].
- **Environmental condition control (环境条件控制)** — monitored, recorded, range-limited conditions (temp, humidity, power, biosafety) that could invalidate results [6.3.2].
- **Incompatible activities (不相容活动)** — activities requiring physical/procedural separation, e.g., PCR pre-/post-amplification zoning [6.3.2].
- **Storage facility integrity (储存设施完整性)** — segregated, condition-controlled storage protecting samples/reagents/records from deterioration, contamination, loss [6.3.3].
- **Sample collection facility design (患者样品采集设施)** — privacy, safety, and patient-condition accommodation without adversely affecting result quality [6.3.5].
- **Facility maintenance program (设施维护和环境条件)** — scheduled maintenance/cleaning/pest-control that must not adversely affect lab activities [6.3.6].

## Mental Models
- **Use the "competence chain" test whenever you see a staff member performing a regulated task**: ask for (1) written competence requirement for that role, (2) the dated competence-assessment record, (3) the authorization document that cites it. A missing link anywhere breaks the chain, and this is the single most common Chapter-4 personnel nonconformity pattern.
- **Think of facility zoning as "workflow becomes physical layout"**: wherever a process document describes sequential, non-reversible steps prone to contamination (most visibly PCR), the assessor expects the floor plan and access control to mirror that sequence one-directionally.
- **Think of the personnel/facility record set as an "assessor's checklist in disguise"**: clauses 6.2.5's list of file contents and 6.3's environmental parameters are literally what an assessor will ask to see item-by-item — treat the clause text as the audit checklist.

## Anti-patterns
- **Treating training attendance as authorization**: a sign-in sheet for a training session is not proof of competence or authorization; assessors specifically look for the competence-assessment record and a separate authorization document referencing it [6.2.3].
- **Single-method competence assessment**: assessing competence only via one channel (e.g., only a supervisor's informal sign-off) fails the expectation of multiple, objective assessment methods (direct observation, record review, blind/retested samples, problem-solving checks, PT/EQA performance).
- **Undifferentiated storage**: storing incompatible items together (e.g., flammable reagents next to samples, or archived and in-use samples undifferentiated) without segregation or access control violates 6.3.3's integrity requirement.
- **Monitoring without recorded acceptance ranges**: logging temperature/humidity without a documented acceptable range and a corrective-action trigger is monitoring in name only — 6.3.2 requires both control and record with actionable limits.
- **Facility failures with no documented impact assessment**: an equipment/facility failure (e.g., a freezer breakdown) handled informally, with no linkage to potential sample/result impact, fails 6.3.6's expectation that maintenance issues are risk-assessed against ongoing activities.

## Reference Tables

**Personnel competence assessment — method mix (interpretive guidance under 6.2.2/6.2.3)**
| Assessment method | What it evidences | Typical trigger |
|---|---|---|
| Direct observation of routine work | Practical execution skill | Initial authorization; periodic re-check |
| Review of records/reports produced | Accuracy/completeness of documentation | Ongoing, at record review |
| Retesting of previously examined (blind) samples | Result reproducibility | Periodic, esp. after long routine runs |
| Problem-solving/troubleshooting assessment | Judgment under abnormal conditions | Initial + periodic |
| PT/EQA performance review | External-benchmarked accuracy | Each PT cycle |
| Direct monitoring of equipment maintenance/function checks | Operational competence beyond testing itself | Role-specific, ongoing |

*Interval note*: the standard and this book do not prescribe one universal number (e.g., a fixed "every 6 months"); interval must be justified per role by risk, complexity, and frequency of the activity — reviewers check for the **rationale**, not a specific count.

**Personnel record file — minimum contents [6.2.5]**
| Element | Purpose |
|---|---|
| Education/qualification certificates | Prove baseline credential |
| Job description | Define scope of role |
| Competence assessment records | Prove demonstrated capability |
| Training/CE records | Prove ongoing development |
| Performance review records | Prove ongoing suitability |
| Incident/exposure/immunization records | Prove safety compliance where relevant |

**Facility zoning example — molecular/PCR lab (解读 illustration under 6.3.2)**
| Zone | Function | Flow rule |
|---|---|---|
| 试剂储存区 (Reagent storage) | Master mix/reagent prep | Entry point, no return flow |
| 标本制备区 (Specimen prep) | Nucleic acid extraction | One-way onward only |
| 扩增区 (Amplification) | PCR amplification | No return to prep areas |
| 产物分析区 (Product analysis) | Post-amplification detection | Terminal zone |

## Worked Example
**Finding**: During an on-site assessment, a technologist is observed independently releasing molecular test results. The lab produces a training sign-in sheet dated six months earlier as the only evidence of qualification.
**Root cause**: No documented competence-assessment record exists linking the training to a demonstrated capability; no formal authorization document was issued citing that assessment.
**Corrective action**: Lab creates a standard authorization template requiring (1) a documented competence assessment using ≥2 methods (e.g., direct observation + blind sample retest), (2) a dated authorization signed by the lab director referencing the assessment result and defining exact scope (which tests, which systems), (3) a renewal trigger when methods change.
**Clause link**: 6.2.2 (competence requirements) + 6.2.3 (authorization) — nonconformity closed only once the authorization traceably derives from an assessment, not from training alone.

## Key Takeaways
- Resource sections are checked as a **chain of evidence**: requirement defined → competence/condition assessed → authorization/acceptance granted → record retained. Any broken link is a nonconformity even if the underlying work is technically fine.
- Personnel and facility clauses share the same underlying test: can the lab produce a **dated, signed record** proving the requirement was verified, not just asserted?
- Facility risk-zoning (especially for PCR) is the book's canonical illustration of turning an abstract "control environmental conditions" clause into a concrete, inspectable floor plan.
- No universal numeric interval is mandated for competence reassessment; the expectation is a **documented, risk-based rationale** for whatever interval the lab chooses.

## Connects To
- **Chapter 4b** (this same chapter, sections 4-8): equipment, calibration, reagents, service agreements, and external providers extend the same "define requirement → verify → record" logic to physical/technical resources.
- **8.7 Nonconformity management**: personnel/facility failures found here (e.g., unauthorized staff performing tests) route directly into nonconformity and corrective-action processes.
- **4.1 Management commitment / management review**: resource-adequacy planning (6.1) is a standing input to management review.
