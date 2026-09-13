# Chapter 6: Management System Requirements (第六章 管理体系要求)

## Core Idea
Clause 8 requires a documented, continually improved quality management system (质量管理体系) that closes the PDCA loop: policy/objectives → controlled documents/records → risk-and-opportunity management → nonconformity/corrective action → evaluation (internal audit + quality indicators) → management review, feeding back into revised objectives. Labs choose **Option A** (self-contained detailed QMS) or **Option B** (leveraging an existing ISO 9001:2015 certification while still proving clauses 4-7 competence) [8.1.2]; almost all CNAS-accredited Chinese labs use Option A.

## Frameworks Introduced
- **PDCA closed-loop traceability**: Quality objective → quality indicator monitoring → nonconformity/audit finding → root-cause corrective action → management review → revised objective. When to use: as the master audit-trail assessors follow across records to confirm the QMS is a living system, not paperwork. How: ensure every objective has a matching indicator, every off-target indicator has a linked NC/CAPA record, and every CAPA outcome is referenced at the next management review.
- **ISO 22367 risk-management cycle** [8.5]: identify → analyze/estimate (probability × severity) → evaluate vs. acceptability criteria → control (eliminate/substitute/engineering/administrative/PPE) → residual-risk re-evaluation → monitor/review. When to use: for organization-level risks (clause 8.5), distinct from process/patient-safety risk under 7.1. How: maintain a risk register with a probability×severity matrix (commonly 5×5, banded into 低/中/高/极高); thresholds are lab-defined, not fixed by ISO.
- **Document hierarchy model**: 质量手册 (quality manual) → 程序文件 (procedures) → 作业指导书 (work instructions) → 记录 (records), a typical four-tier structure described in the quality manual's document-structure section [8.2.2].

## Key Concepts
- **Quality policy (质量方针)** — top management's documented, organization-wide commitment statement to good practice and standard compliance [8.2.1-8.2.2].
- **Quality objectives (质量目标)** — measurable, trackable targets derived from the policy (e.g., TAT compliance rate, QC-CV pass rate, satisfaction score), reviewed at management review.
- **Document control (文件控制)** — controls for approval, review/re-approval, version/revision identification, availability at point of use, legibility, external-document identification, and obsolete-document control [8.3.1 a-g].
- **Controlled vs. uncontrolled copy (受控 vs 非受控/仅供参考)** — distribution-tracked master copies vs. reference-only copies not subject to update notification.
- **Record control (记录控制)** — identification, storage, protection from unauthorized access/amendment, backup, archiving, retention, and disposal [8.4.1-8.4.2]; corrections use single-line strike-through + signature/date (杠改法), never correction fluid.
- **Risk and opportunity register (风险和机遇登记表)** — system-level register (8.5) kept distinct from the 7.1 process/patient-safety risk log.
- **Correction (纠正) vs. corrective action (纠正措施)** [8.7.1] — correction addresses the immediate symptom; corrective action addresses the root cause to prevent recurrence.
- **Quality indicator (QI, 质量指标)** [8.8.2] — a *normative* 2022 requirement (elevated from prior informative guidance) to monitor pre-/intra-/post-examination performance with defined objective, formula, target, monitoring frequency, and action plan.
- **Internal audit (内部审核)** [8.8.3] — planned-interval audits of conformity and effectiveness; auditors must never audit their own work.
- **Management review (管理评审)** [8.9] — top-management periodic review of QMS suitability/adequacy/effectiveness against a mandatory list of inputs and outputs.

## Mental Models
- **Use the "correction vs. corrective action" test whenever an NC is closed**: if the record only describes fixing the one instance (re-issuing a report, retraining one person) with no analysis of why it happened system-wide, treat it as incomplete — genuine closure requires a traceable root cause and a systemic fix.
- **Think of quality indicators as the QMS's vital signs**: they must span all three process phases (pre/intra/post-examination); a persistently red indicator is itself an unopened nonconformity waiting for RCA and management-review escalation.
- **Think of internal audit + management review as the "Check" half of PDCA**: internal audit checks conformity/effectiveness of the running system; management review checks whether the system's objectives and resourcing are still right — one looks inward at execution, the other looks at strategic adequacy.
- **Use "independence" as the litmus test for internal audit validity**: any audit where the auditor reviewed their own department's work is presumptively invalid regardless of how thorough the checklist was.

## Anti-patterns
- **Stamping documents as controlled but leaving stale bench copies in circulation**: assessors routinely find outdated SOP binders at workstations that don't match the current master list — cited as a document-control nonconformity even if the master list itself is correct.
- **Using correction fluid or unsigned edits on records**: destroys the audit trail and is treated as a data-integrity/authenticity failure, not a minor clerical issue.
- **Writing "staff carelessness" (人员疏忽) as the root cause**: rejected as superficial RCA; assessors expect a structured method (five-why, fishbone, FMEA) that surfaces systemic/process contributors (training gaps, procedural ambiguity, design flaws).
- **Self-auditing one's own department during internal audit**: violates the objectivity/impartiality requirement even if findings are accurate — the audit itself becomes the nonconformity.
- **Holding a management review meeting that skips required input topics** (e.g., no discussion of supplier evaluation or personnel feedback): the meeting having occurred does not satisfy 8.9.2 if the agenda is incomplete.
- **Treating quality indicators as a static, one-time list**: indicators must be periodically reviewed for continued appropriateness and tied to actual corrective action when targets are missed — a beautifully formatted but unused QI table is a common superficial-compliance trap.

## Reference Tables

**Document-control lifecycle (8.3.1 a-g)**: approve before issue → review/update/re-approve → identify changes & current revision status → ensure availability at point of use → ensure legibility/identifiability → identify & control distribution of externally-originated documents → prevent unintended use of obsolete documents (recall or clearly mark "作废" if retained). Required fields per controlled document: unique ID (文件编号), version/revision no. (版本号), effective date (生效日期), pagination (第X页/共Y页), approval signature. Periodic review cycle: **at least annually (每年至少一次)**.

**Record retention (as discussed with examples; apply the longer of accreditation vs. national-law minimum)**:
| Record type | Retention |
|---|---|
| General technical/quality records, reports, raw data | ≥2 years |
| Equipment calibration/maintenance | through service life + defined period |
| QC / EQA (PT) records | ≥2 years |
| Personnel training/competency records | long-term (through/after employment) |
| Transfusion/blood-group-related records | ≥10 years (per Chinese regulation) |
| Pathology paraffin blocks | ≥15 years |
| Pathology slides | multi-year (per regulation) |

**Risk-management process (per ISO 22367)**: identify → analyze/estimate (probability × severity) → evaluate vs. acceptability criteria → control (eliminate/substitute/engineering/administrative/PPE) → residual-risk evaluation → monitor/review. Typical tool: 5×5 probability×severity matrix banded 低/中/高/极高 (lab-defined thresholds).

**Root-cause analysis / CAPA steps (8.7)**: react & correct (纠正) → evaluate need for corrective action (review/analyze, determine cause(s), check for similar/recurring NCs) → implement corrective action → verify effectiveness → update risk register if needed → amend QMS if needed. Tools: five-why (五问法), fishbone (鱼骨图), FMEA.

**Internal audit rules (8.8.3)**: frequency — full-system coverage **at least once per year** (single audit or rolling partial audits completing within 12 months); auditors selected for objectivity/impartiality, **must not audit own work**; audit report must record date/scope/criteria, auditors, areas audited, NCs (with clause refs), positive observations, follow-up timeline, and overall QMS-effectiveness conclusion.

**Quality indicator (质量指标) set by phase**:
| Phase | Example indicators | Formula pattern | Frequency |
|---|---|---|---|
| Pre-examination | 标本类型/采集量错误率, 标本溶血率, 标本凝块率, 申请单填写错误率, 运送时间不合格率 | (不合格数/总数)×100% | Monthly |
| Intra-examination | 室内质控开展率, 室内质控失控处理及时率, PT/EQA参加率, PT不合格率, 复检符合率 | pass/participation rate | Monthly/per PT cycle |
| Post-examination | 报告TAT达标率, 危急值通报及时率, 报告错误/更正率, 报告不完整率 | compliance rate | Monthly |
| Satisfaction | 患者满意度, 临床满意度 | survey score | ≥annually |

Targets are lab-set (examples cited: TAT compliance ≥90-95%, hemolysis rate ≤2%), not fixed ISO numbers; indicators reviewed for continued appropriateness **at least annually**.

**Management review — mandatory inputs (8.9.2 a-o)**: internal/external issue changes; quality-objective fulfillment; status of actions from prior reviews; internal/external audit outcomes; corrective-action status; external-provider performance; risk/opportunity results; process-improvement outcomes; user/patient feedback & complaints; personnel feedback; resource adequacy; risk-mitigation-action effectiveness; quality-indicator results; EQA/PT results; improvement recommendations.
**Mandatory outputs (8.9.3 a-d)**: decisions on QMS/process effectiveness; process-improvement actions; resource-need decisions; QMS change decisions. Frequency: **at least once per year**; must occur with ≥1 full cycle of operating data (e.g., ≥6-12 months) before initial/renewal assessment.

## Worked Example
An internal audit at a hospital lab found a nurse-facing QC-failure event (glucose assay out of control) had been silently bypassed — staff manually excluded the failing result and released the report without following the QC-failure SOP. RCA (five-why) traced the cause not to "carelessness" but to a training gap: new staff were never taught the Westgard-rule failure-handling procedure. Corrective action went beyond retraining the individual: the lab revised its onboarding curriculum to make QC-exception handling a mandatory competency module for all new hires, then verified effectiveness via a follow-up audit three months later confirming compliant QC-failure handling lab-wide. This closed-loop trace (indicator/audit finding → root cause → systemic corrective action → verified effectiveness) is exactly the pattern assessors look for.

## Key Takeaways
- Clause 8 is a PDCA engine: document/record control feed risk management, which feeds nonconformity handling, which feeds evaluation (audit + QI), which feeds management review, which resets objectives.
- "Correction" alone never satisfies 8.7 — root-cause corrective action, verified for effectiveness, is mandatory.
- Quality indicators are now normative and must cover all three process phases with defined formula/target/frequency, not an ad hoc list.
- Internal audit independence (no self-audit) and completeness of management-review inputs/outputs are the two most frequently cited procedural nonconformities in this chapter's domain.
- Retention periods must satisfy whichever is stricter: the accreditation minimum or Chinese national/professional regulation.

## Connects To
- Clause 7.1 (process-level risk-based thinking) — complements but is distinct from the 8.5 system-level risk register.
- Clause 6.2 (personnel competence assessment methods) — the same multi-method competence-assessment logic reappears for POCT operators in Chapter 7.
- Chapter 7 (POCT) — POCT's quality-assurance and training programs are, in effect, clause-8-style QMS controls (document control, QC, competency, corrective action) applied to a decentralized testing context.
