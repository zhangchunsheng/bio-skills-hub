# Chapter 5B: Process Requirements — Post-examination, Nonconformity, Data and Continuity (第五章 过程要求：检验后过程、不符合工作、数据控制与应急)

## Core Idea
Once results exist, the laboratory's job is not "done" — clause 7.4–7.8 govern everything that must happen *after* the bench: verifying and releasing results safely, catching and fixing nonconforming work, keeping data/LIS trustworthy, hearing complaints, and staying operational through disruption. Assessors treat this cluster as a single traceability chain: every result, correction, notification, access event, and disruption must leave a documented, time-stamped, attributable record — because the shared failure mode across all five sections is "it happened but nobody can prove how or when."

## Frameworks Introduced
- **Result review before release (结果复核, 7.4.1)**: exact formulation — results must be checked against QC status, clinical plausibility, and prior results (delta check) before an authorized signatory releases the report. When to use: every report, combining automated and manual review. How: define review criteria in SOP, log reviewer identity/time.
- **Critical value closed-loop management (危急值闭环管理, within 7.4)**: generation → verification → notification within a defined time limit → clinician read-back confirmation → documentation → periodic (≥1×/year) joint list review with clinicians. When to use: any result on the alert list. How: dedicated log with mandatory fields (see table).
- **Autoverification validation framework (自动选择与报告的确认, 7.4, new in 2022 edition)**: rules must be documented and validated against manual review before go-live, and re-validated after any rule change; dangerous/abnormal/instrument-flagged results are excluded from auto-release. When to use: whenever LIS auto-releases results without human review. How: comparison study + sign-off + change log.
- **Nonconforming work cycle (不符合工作处理, 7.5)**: identify → assess clinical significance/risk → immediate containment (hold/recall report, notify clinician) → document root cause → corrective/preventive action → authorized resumption. When to use: any deviation from procedure or agreed requirement (QC failure, complaint-triggered, equipment fault). How: single unified NC-work log feeding management review trend analysis.
- **Data/information control framework (数据控制和信息管理, 7.6)**: role-based access + audit trail, pre-use and post-change validation, backup/recovery, downtime contingency. When to use: any computerized system touching pre-/examination/post-examination data. How: combine IT policy with periodic restore drills.
- **Complaint-handling cycle (投诉处理流程, 7.7)**: receive/log → acknowledge → impartial investigation → decision → timely response → document → trend-analyze. When to use: any complaint from clinician, patient, or staff. How: designate an owner not implicated in the complaint.
- **Continuity and contingency planning (连续性和应急预案, 7.8)**: identify foreseeable disruption scenarios → scenario-specific response plan with named owner → periodic drills (≥1×/year) → post-incident/post-drill plan update. When to use: power loss, LIS downtime, critical equipment failure, staff shortage, public-health emergencies.

## Key Concepts
- **Turnaround time / TAT (检验周转时间)** — receipt-to-report interval, defined per test and per priority (routine/常规 vs STAT/急诊), monitored with corrective action on misses [clause 7.4].
- **Authorized signatory (授权签字人)** — the person credentialed to review and release final reports; authorization must be an auditable record [7.4.1].
- **Critical/alert value (危急值)** — a result signalling a life-threatening state requiring immediate clinician notification and read-back [7.4].
- **Amended report (修改报告)** — a post-release correction that must preserve the original result and record who/why/when changed [7.4].
- **Sample retention (样本保留)** — defined storage condition + duration per specimen/test type before disposal [7.4].
- **Nonconforming work (不符合工作)** — any work item not meeting the lab's own procedure or the agreed service requirement [7.5].
- **Audit trail (审计追踪)** — system-level log of who entered/modified/reviewed/deleted data and when [7.6].
- **Validation of information systems (信息系统确认)** — pre-use and post-change verification that the LIS/interface computes and transmits data correctly [7.6].
- **Impartial complaint investigation (独立调查)** — the investigator must not be the person the complaint concerns [7.7].
- **Business continuity / contingency plan (业务连续性/应急预案)** — a rehearsed, scenario-specific plan to keep or resume operation during disruption [7.8].

## Mental Models
- **Use the "closed loop" test for anything safety-critical** (critical values, amended reports, NC work): if you can't show a *start*, an *action*, a *confirmation*, and a *record*, the loop is open and it will be cited.
- **Think of TAT, retention, and backup frequency as promises the lab makes to itself**: a promise without a monitored number ("we report quickly," "we back up regularly") is not assessable; only "≤X minutes," "kept Y days," "daily incremental / weekly full" survive an audit.
- **Think of 7.5 (nonconforming work), 7.7 (complaints), and 7.8 (continuity) as the same "detect → contain → fix → prove it won't recur" skeleton reapplied to three different triggers** (internal deviation, external dissatisfaction, external disruption).
- **Use "who is NOT allowed to touch this" as a design check for LIS and complaints**: role separation (tester ≠ admin) and investigator independence (investigator ≠ subject of complaint) are the two most commonly cited access/impartiality gaps.

## Anti-patterns
- **Releasing reports without documented review criteria**: assessors cannot verify delta-check/QC/clinical-plausibility review happened, even if staff "always do it" informally — undocumented review = no review [7.4.1].
- **Blank fields for untested items**: an empty result field is indistinguishable from an omission; must show "未测/未做" explicitly [7.4].
- **Notifying a critical value but not recording the notification time or read-back confirmation**: the value existing in the LIS is not proof the clinician was actually informed in time — this is the single most common 危急值 nonconformity.
- **Overwriting an amended report's original value**: destroys traceability; both original and amended values, plus reason/author/time, must coexist in the record.
- **Vague retention statements ("samples kept for a while")**: unenforceable and unverifiable; must specify exact days/months by specimen/test type.
- **Shared LIS logins or admin-level rights for testing staff**: breaks audit-trail attribution and allows undetected deletion of reviewed reports (cited nonconformity example, p197).
- **Treating an untested contingency plan as compliant**: a plan that has never been drilled cannot be demonstrated to work; assessors expect drill records and post-drill revisions.
- **Complaint investigated by the person complained about**: violates impartiality and invalidates the finding regardless of outcome.

## Reference Tables

**Mandatory report content elements (检验报告必备要素)** [7.4]
| Element | Requirement |
|---|---|
| Patient identification | Name, gender, age, unique ID, ward/bed or outpatient no. |
| Requester | Ordering clinician/department |
| Specimen | Type, collection time, receipt time |
| Result | Test name, value, unit, reference interval, abnormal-flag marker |
| Method | Stated where result interpretation depends on method |
| Sign-off | Tester/reviewer signature, authorized signatory |
| Report metadata | Report date-time; page "X of Y" |
| Lab identity | Name, address, contact, accreditation mark if applicable |
| Referral note | Must state if performed by an outsourced/referral lab |
| Untested items | Marked "未测/未做," never left blank |

**TAT monitoring** [7.4]: define target TAT separately for routine (常规) vs urgent/STAT (急诊) per test category; track actual-vs-target on a regular cycle (e.g., monthly); trigger corrective action on repeated misses.

**Critical value (危急值) closed-loop record fields** [7.4]
| Field | Content |
|---|---|
| Patient info | ID/name/location |
| Result | Item + value triggering alert |
| Notifier / notified party | Names |
| Notification time | Timestamp within lab's defined limit |
| Read-back confirmation | Clinician repeats value back |
| Clinical feedback | Action taken, if recorded |
| List review | ≥1×/year joint review with clinical departments |

**Autoverification (自动选择与报告) rule design & validation** [7.4]: rules documented in SOP; critical/abnormal/instrument-alarm/delta-fail results excluded from auto-release and routed to manual review; validation study (auto vs manual agreement) required before go-live; re-validation required after any rule change.

**Amended-report (修改报告) traceability fields** [7.4]: original result (retained, not deleted) · amended result · reason for amendment · person who amended · reviewer · amendment timestamp · clinician-notification record if change affects care.

**Sample retention by type (样本保留期限)** [7.4] — illustrative categories from the book:
| Specimen/test category | Typical retention |
|---|---|
| Routine chemistry/immunology (refrigerated) | Short-term (days), enough for add-on/repeat testing |
| Whole blood/plasma | Through report release + short buffer |
| Transfusion/blood-group & cross-match samples | Longer minimum hold (commonly ≥7 days) for recheck |
| Infectious-marker-positive samples | Extended hold per infectious-disease management rules |
| Pathology blocks/slides | Long-term (years) per pathology-specific regulation |

**Record retention periods (记录保存期限)** [7.6/general]: raw test data, reports, QC and calibration records — baseline ≥2 years; personnel training/competency records — through employment and beyond; equipment records — life of equipment; transfusion/blood-group and pathology records — materially longer than the 2-year baseline, driven by legal/clinical-dispute exposure.

**Nonconforming-work handling steps (不符合工作处理步骤)** [7.5]: ① Identify (source: QC failure, abnormal result, complaint, equipment fault) → ② Assess clinical significance/risk → ③ Immediate action (hold or recall report; notify clinician if already released) → ④ Document (what/when/who/root cause) → ⑤ Corrective/preventive action → ⑥ Authorized resumption of work by a responsible person → trend-analyzed as management-review input.

**LIS validation & access-control requirements** [7.6]: unique login per user, no shared passwords, role-based permission tiers (tester cannot alter reference intervals; only admin can); full audit trail (who/what/when for entry, modification, review, deletion); validation before go-live and re-validation after every software change/upgrade, including instrument–LIS and LIS–HIS interface checks.

**Backup/recovery & continuity requirements** [7.6/7.8]: backup on a defined cadence (commonly daily incremental + weekly full), offsite/off-system copy, periodic restore drills to confirm backup validity; documented manual fallback procedure for LIS downtime with staff trained in advance and a data re-entry/verification step on restoration; scenario-specific contingency plans (power loss, LIS failure, critical equipment failure, staff shortage, public-health emergency) each with a named responsible person and communication plan; drills ≥1×/year with post-drill plan updates.

**Complaint handling steps & timelines (投诉处理)** [7.7]: ① Receive & log → ② Acknowledge receipt to complainant → ③ Assign an impartial investigator (not the person complained about) → ④ Investigate and assess validity → ⑤ Decide on action → ⑥ Respond to complainant within the lab's committed timeframe → ⑦ Document full cycle → ⑧ Trend-analyze recurring complaints for systemic improvement.

## Worked Example
An assessor reviews a chemistry report that was corrected in the LIS after release. Finding: the original (incorrect) potassium value was overwritten with no audit trail — no record of who changed it, when, or why, and no note confirming whether the ordering clinician was told. This is cited as a nonconformity against both 7.4 (amended-report traceability) and 7.6 (audit trail/data integrity). Root cause: LIS configuration allowed direct edits to released results instead of routing through an "amend" function. Corrective action: reconfigure LIS so released results are locked (append-only amendment with mandatory reason/author/time fields), retrain staff on the amendment SOP, and re-audit a sample of recent amended reports to confirm the fix. This single scenario shows how 7.4 and 7.6 requirements interlock — a technically "fixed" result is still a finding if its correction cannot be reconstructed.

## Key Takeaways
- Post-examination compliance is really a *traceability* test: review, critical-value notification, amendments, NC-work resolution, LIS changes, complaints, and contingency actions all must show who/when/why, not just that they occurred.
- Numeric commitments (TAT targets, critical-value notification limits, retention days/years, backup cadence, drill frequency ≥1×/year) must be explicit in SOPs — vague promises cannot be assessed.
- Autoverification and LIS access control are the two newer/high-scrutiny areas in the 2022 edition: both require documented validation before use, not just after-the-fact justification.
- Nonconforming work, complaints, and contingency planning share one skeleton — detect, contain, fix, prevent recurrence, prove it via drills/records.

## Connects To
- Chapter 5A (7.1–7.3: pre-examination and examination processes) — the upstream source of the results and QC data being reviewed here.
- Chapter on Management System Requirements (clause 8) — nonconformity records, complaint trends, and contingency-drill outcomes all feed into management review (8.9) and corrective/preventive action (8.7–8.8).
- Personnel and competence chapter — authorized signatories and NC-work decision-makers must have documented competency/authorization records.
