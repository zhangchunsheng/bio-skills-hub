# Chapter 17: Data Control and Information Management (数据控制和信息管理)

## Core Idea
Clause 7.6 (数据控制和信息管理) treats the laboratory information system (LIS) and every data path around it as a **measuring system for information**: if a result can be altered, lost, mis-transmitted, or read by the wrong person without a trace, the analytical quality upstream is worthless. ISO 15189:2022 requires that information systems be validated before use and after every change, that access and authority be controlled, that data integrity and audit trails be preserved, that downtime not stop patient care, and that externally hosted/vendor-managed systems remain fully the laboratory's responsibility — with the whole regime driven by risk management (ISO 22367).

## Discipline-Specific Requirements

### 系统验证 (System validation) [clause 7.6.1, 7.6.3]
- The information system (LIS, middleware, analyser interfaces, auto-verification rules) must be **validated before clinical use** and **re-validated after any change** — version upgrades, new interfaces, changed reference intervals or calculation formulas, new auto-verification rules.
- Validation covers correct data capture, calculation, unit handling, reference-interval flagging, and result transmission end-to-end (analyser → LIS → report/HIS), not just the analyser in isolation.

### 权限与安全 (Authorities & security) [clause 7.6.1, 6.2, 6.3]
- Access is role-based with defined authorities: who may enter, edit, verify/release, and amend results; who may change system configuration and reference intervals. Unique user IDs, password policy, and periodic access review are required.
- The lab defines who is authorised to manage the information system (system administrator responsibilities), separated from routine result-release authority where risk warrants.

### 数据完整性与审计追踪 (Data integrity & audit trail) [clause 7.6.3]
- Every result creation, modification, and release is attributable, time-stamped, and preserved (audit trail); amended results retain the original value, the change, who made it and when.
- Calculations and auto-verification logic are documented and controlled so that a result cannot be silently transformed.

### 备份与恢复 (Backup & recovery) [clause 7.6.1, 7.6.4]
- Regular, defined-frequency backups with **tested restore** — a backup that has never been restored is not evidence of recoverability. Backup media/location protected against the same event that would destroy the primary (off-site or segregated).

### 接口与传输 (Interfaces & transmission) [clause 7.6.3]
- Data transmitted between systems (analysers, LIS, HIS, external portals) is checked for completeness and correctness; interface mappings are validated and monitored so no field is dropped or mis-aligned.

### 变更管理与停机应急 (Change management & downtime contingency) [clause 7.6.3, 7.6.4]
- A documented **downtime/contingency procedure (信息系统故障应急预案)** keeps testing and reporting running during LIS failure (manual worksheets, result hold/notification, reconciliation on recovery), tied to the continuity requirements of clause 7.8.
- Changes follow controlled change management: risk-assess, test/validate, authorise, record.

### 外部托管 (Externally hosted / vendor-managed systems) [clause 7.6.1, 7.6.5]
- When the LIS or data storage is hosted by a vendor or off-site (including cloud), the laboratory remains responsible: a service agreement defines security, availability, backup, access, and audit rights, and the lab verifies the provider meets the same clause 7.6 controls.

## Frameworks Introduced
- **Validate-before-and-after-change (信息系统验证)**: no information system enters or continues clinical use without validation at go-live and re-validation after each change [clause 7.6.1/7.6.3]. Use for LIS, middleware, interfaces, auto-verification, formula/reference-interval edits.
- **Attributable-traceable-preserved (ALCOA-style data integrity)**: every data action is attributable to a person, time-stamped, and preserved with an audit trail [clause 7.6.3]. Use to judge any edit/amendment path.
- **Backup-with-tested-restore**: recoverability is proven only by a successful test restore, not by the existence of backups [clause 7.6.1/7.6.4].
- **Responsibility-does-not-outsource**: an externally hosted system is still the lab's clause-7.6 obligation, secured by a service agreement [clause 7.6.5].

## Key Concepts
- **information system (信息系统/LIS)** — all hardware/software handling laboratory data, from analyser interfaces to report delivery [clause 7.6.1].
- **validation of the information system (信息系统验证)** — documented proof the system handles data correctly before use and after change [clause 7.6.3].
- **access authority (访问权限)** — role-based rights to enter, edit, release, amend, and configure [clause 7.6.1].
- **audit trail (审计追踪)** — attributable, time-stamped record of data creation/change/release [clause 7.6.3].
- **downtime contingency plan (信息系统应急预案)** — procedures maintaining service during system failure [clause 7.6.4].
- **backup and restore (备份与恢复)** — periodic backup with tested recovery [clause 7.6.4].
- **externally managed system (外部管理的信息系统)** — vendor/off-site-hosted system still under the lab's responsibility via agreement [clause 7.6.5].
- **data integrity (数据完整性)** — assurance data is complete, unaltered, and traceable across its lifecycle [clause 7.6.3].

## Mental Models
- Treat the LIS as **an instrument that measures information**: it needs verification, QC, change control, and a maintenance record just like an analyser.
- Use "**can this result be changed without a trace?**" as the integrity test — if yes, the audit-trail requirement of 7.6.3 is unmet.
- Think of backups as **untested until restored**: the assessment question is "show me the last restore test," not "show me the backup schedule."
- For a cloud/vendor system, ask "**where does the lab's responsibility end?**" — the correct answer under 7.6.5 is "it doesn't; it's covered by an agreement."

## Anti-patterns
- **Go-live or upgrade with no validation record**: new/changed LIS logic can misroute results or misflag reference intervals undetected [clause 7.6.3].
- **Shared or generic logins**: destroys attribution, so the audit trail cannot identify who released or amended a result [clause 7.6.1/7.6.3].
- **Backups never test-restored**: discovered non-recoverable only during a real disaster [clause 7.6.4].
- **No downtime procedure**: an LIS outage halts reporting or forces untracked manual results with no reconciliation [clause 7.6.4].
- **Cloud/vendor system with no service agreement covering security, backup, and audit rights**: the lab has silently outsourced a responsibility it cannot outsource [clause 7.6.5].
- **Auto-verification rules changed without re-validation**: a mis-set rule can release erroneous results at scale [clause 7.6.3].

## Reference Tables

**Clause 7.6 sub-requirements and evidence**
| Sub-area | Requirement | Evidence an assessor asks for |
|---|---|---|
| 7.6.1 General / authorities | Roles, access control, responsibility for the system | Access matrix, user list, admin responsibility record |
| 7.6.3 System management / integrity | Validated system; audit trail; controlled changes | Validation report (go-live + each change), audit-trail sample, change log |
| 7.6.4 Downtime / backup | Contingency plan; backup + tested restore | Downtime SOP, backup schedule, **restore-test record** |
| 7.6.5 External / off-site | Vendor/hosted system under agreement | Service agreement covering security, availability, backup, audit rights |

**When a change requires re-validation (clause 7.6.3)**
| Change | Re-validate? |
|---|---|
| LIS version upgrade / patch | Yes |
| New analyser interface | Yes |
| Changed reference interval or calculation formula | Yes |
| New/edited auto-verification rule | Yes |
| New report template affecting content | Yes (content/mapping check) |

## Worked Example
During assessment, a lab shows a nightly LIS backup schedule and a signed information-security policy. The assessor asks two questions. First, "when did you last successfully restore from a backup?" — the lab has never tested a restore, so recoverability is unproven (7.6.4 nonconformity). Second, reviewing a corrected potassium result, the assessor finds the amendment shows the new value but not the original or the editor's identity, because the analysts share one LIS login (7.6.3 / 7.6.1 nonconformity — attribution and original-value preservation lost). Corrective action: schedule and document periodic test restores; assign unique user IDs and enable the audit trail so every amendment preserves the original value, timestamp, and author.

## Key Takeaways
1. Clause 7.6 makes the LIS a validated, controlled system — validate before use and re-validate after every change (upgrades, interfaces, reference intervals, auto-verification).
2. Attribution is everything: unique logins + audit trail so every creation, edit, and release is traceable to a person and time; amendments preserve the original.
3. Backups prove nothing until a restore is tested — keep a restore-test record.
4. A downtime/contingency plan must keep reporting alive and reconcile results on recovery (ties to clause 7.8 continuity).
5. Externally hosted/vendor systems stay the lab's responsibility, secured by a service agreement covering security, availability, backup, and audit rights.
6. The regime is risk-driven (ISO 22367): controls scale with the harm a data error could cause a patient.

## Connects To
- **Ch 5B (clause 7.6 within the process chain)**: Chapter 17 is the deep-dive of the same clause 7.6 introduced with post-examination controls.
- **Ch 5B (clause 7.8 continuity)**: downtime contingency is the information-system face of business continuity.
- **Ch 16 (molecular/NGS)**: high-volume sequencing data makes 7.6 data-integrity and pipeline version control especially critical.
- **Ch 6 (clause 8.4 records, 8.5 risk)**: record control and risk management underpin data retention and the risk-based scaling of information controls.
- **Ch 4 (clause 6.8 externally provided services)**: vendor-hosted systems also invoke the externally-provided-services controls.
