# Chapter 7: Additional Requirements for Point-of-Care Testing (第七章 即时检验(POCT)的附加要求)

## Core Idea
POCT (即时检验/床旁检测, Point-of-Care Testing) is testing performed near or at the site of patient care — by nurses, ICU staff, or clinicians rather than laboratory personnel — whose results can immediately change patient care. ISO 15189:2022 Annex A applies whenever the organization has assigned responsibility for POCT to the laboratory: the lab (through a coordinator/committee) must extend its full quality oversight — governance, method verification/comparability, QC, connectivity, and operator training/authorization — into decentralized, non-lab-controlled sites, even though it does not directly perform the testing.

## Frameworks Introduced
- **POCT governance chain**: hospital-level POCT management committee (POCT管理委员会, cross-departmental) → laboratory-appointed POCT coordinator (POCT协调员/总负责人, technical authority spanning all sites) → ward/unit operators. When to use: whenever POCT devices are used outside the central lab under the lab's accreditation scope. How: formalize authority in a hospital policy document so the coordinator's technical authority overrides departmental reporting lines.
- **Device-lifecycle verification loop**: pre-deployment verification/comparison → periodic comparability study vs. central-lab reference method → lot-to-lot verification on reagent change → QC-failure suspension/re-verification before return to service. When to use: for every POCT device/method under lab scope, continuously, not just at initial rollout.
- **Operator authorization cycle** (mirrors clause 6.2 competence-assessment logic): initial training → competency assessment (favoring direct observation, per the six main-text competence-assessment methods) → authorization → annual re-training/re-assessment → suspension on lapse. When to use: for every individual POCT operator; enforce via a POCT-DMS (POCT数据管理系统) that can lock out unauthorized/expired IDs.

## Key Concepts
- **POCT (即时检验)** — testing at/near the point of care with potential immediate impact on patient management, in scope of Annex A when organized under the lab's authority.
- **POCT management committee (POCT管理委员会)** — cross-departmental governance body (hospital leadership, lab, nursing, user departments) setting POCT policy.
- **POCT coordinator (POCT协调员/总负责人)** — lab-designated person(s) with technical authority over POCT spanning all sites, regardless of operators' departmental hierarchy.
- **Comparability study (方法学比对)** — periodic comparison of POCT results against the central-lab reference method to confirm clinical equivalence/interchangeability.
- **POCT-DMS (POCT数据管理系统)** — connectivity/data-management layer linking devices to LIS/HIS: automatic result transfer, operator-ID capture, and lock-out of unauthorized/expired operators.
- **Lot verification (批号验证)** — mandatory parallel testing of a new reagent/strip lot against the old lot (with controls and/or patient samples) before clinical release.
- **Operator authorization (操作人员授权)** — formal, dated authorization required before independent testing; must be actively maintained via re-training/re-assessment, not granted once and forgotten.
- **Quality assurance programme (质量保证方案)** — POCT-specific internal QC (IQC) plus EQA/PT participation, or an alternative comparison method when formal EQA is unavailable for a given analyte.
- **Direct observation (直接观察)** — the practical, most-used competency-assessment method for bedside operators, echoing the six competence-assessment methods of clause 6.2.

## Mental Models
- **Think of the lab as the "quality backbone" running through a decentralized network**: physical testing happens in wards/ICU/OR, but every quality control point (method verification, QC, training, data review) still terminates back at the laboratory's authority — decentralization of location must never mean decentralization of quality accountability.
- **Use the "same patient, same truth" test for comparability**: if a clinician could plausibly compare a POCT glucose value against a central-lab glucose value for the same patient, the two must be demonstrably comparable — this is why periodic comparability studies (not one-time validation) are required.
- **Treat operator authorization like a perishable credential**: it expires and must be renewed (annual re-training/assessment); systems that don't automatically enforce expiry (manual lists) are inherently weaker controls than DMS lock-out enforcement.
- **When formal EQA doesn't exist for a POCT analyte, don't treat that as an exemption from oversight** — substitute an alternative comparison (split-sample vs. reference method) so reliability is still demonstrated by some objective means.

## Anti-patterns
- **Allowing a POCT coordinator's authority to be undermined by departmental hierarchy** (e.g., a ward director refusing lab oversight of "their" device): breaks the entire governance chain and is a citable major nonconformity in Annex A's management-responsibility requirement.
- **Skipping periodic comparability studies after initial device validation**: a device that passed verification at rollout can still drift or be used with a population/context where bias emerges — comparability must be an ongoing (e.g., twice-yearly) activity, not a one-time gate.
- **Letting wards self-purchase POCT reagents outside centralized procurement**: bypasses the lab's supply-chain QC oversight and risks unapproved/expired reagents entering patient testing.
- **Allowing an operator to test before authorization is complete** (e.g., a newly rotated nurse using her login before her competency sign-off): a major nonconformity requiring retrospective review of any results she generated, plus a system-level fix (ID lock-out), not just individual retraining.
- **Manual result transcription without a compensating control on non-connected devices**: introduces transcription error risk; requires a documented two-person verification (双人核对) as a stated interim control, with a plan to migrate to connected devices.
- **Treating "no formal EQA available" as grounds to skip quality assurance entirely**: the lab must still implement an alternative comparison method — silence on this point is a gap, not a valid exemption.

## Reference Tables

**POCT governance roles**:
| Role | Scope |
|---|---|
| POCT management committee (POCT管理委员会) | Hospital-wide policy, cross-department coordination, chaired typically by hospital deputy director |
| POCT coordinator (POCT协调员/总负责人) | Lab-appointed; technical authority over device selection, procedure approval, training oversight, QC oversight, LIS connectivity, results review — across ALL POCT sites regardless of location's reporting line |
| Ward/unit operator | Performs testing under authorization; follows POCT SOP/quick-reference card; escalates per defined contact path |

**Operator authorization / training / re-training cycle**:
Initial training (theory, device operation, QC, specimen/patient-ID confirmation, result interpretation incl. critical values, biosafety, troubleshooting, escalation contact) → competency assessment (favor direct observation + ≥1 additional method: QC/PT review, knowledge test) → authorization granted & entered on authorized-operator register → **annual (每年至少一次)** re-training/re-assessment → authorization suspended immediately on lapse or unauthorized-use detection, pending retraining.

**POCT QC and comparability requirements**:
| Requirement | Cited frequency/criteria |
|---|---|
| Internal QC (室内质控) | ≥1x/day, 2 levels (high/low) (每日一次高低两水平); also upon every reagent-lot change |
| QC failure response | Immediate suspension of device use; notify lab/coordinator; correct & re-verify before returning to service |
| Comparability vs. central-lab method | Example: ≥2x/year (每年至少2次), ≥~20 paired samples spanning measuring range, pre-set bias/acceptance criteria |
| Lot-to-lot verification | Parallel run of new vs. old lot with controls/patient samples before releasing new lot clinically |
| EQA/PT participation | Enrolled per POCT test/technology; if unavailable, use alternative (e.g., split-sample) comparison, documented |

**Connectivity/data requirements**: Where technically feasible, POCT devices connect to LIS/HIS for automatic result transfer + operator-ID capture; periodic (e.g., monthly) lab review of POCT data trends (QC compliance rate per site/operator, abnormal-result patterns); where not connectable, mandatory documented two-person manual-transcription verification as an interim compensating control; POCT-DMS ideally auto-locks unauthorized/expired operator IDs.

## Worked Example
A CNAS assessment of a hospital's POCT program surfaced four linked gaps mapped to the chapter's own four sections: (1) **总体要求** — the POCT coordinator's authority wasn't clearly empowered across all departments; (2) **管理要求** — some devices lacked a comparability study against the central lab; (3) **质量保证方案** — QC records were incomplete at two ward sites; (4) **培训方案** — two operators' authorizations had lapsed without being blocked. The hospital's corrective-action plan addressed all four under committee-level oversight, with a follow-up audit confirming closure — illustrating that POCT governance, method comparability, QC, and operator training form a single accountability chain, and a failure in one link (e.g., weak coordinator authority) tends to cascade into failures in the others (uncontrolled devices, unmonitored QC, expired authorizations).

## Key Takeaways
- Annex A applies only when the lab has been assigned responsibility for POCT — but where it applies, the lab's quality obligations are as complete as for central-lab testing, just executed through a coordinator/committee structure.
- Comparability with the central-lab reference method must be periodic (not one-time), with defined sample counts and bias criteria.
- Operator authorization is a living, expiring credential requiring annual renewal — enforce expiry technologically (DMS lock-out) rather than relying purely on manual tracking.
- QC failure must immediately suspend device use; lot changes must be verified before clinical release.
- Where connectivity or formal EQA is unavailable, the lab must implement a documented compensating control (two-person verification; alternative comparison method) rather than treating the gap as an exemption.

## Connects To
- Clause 6.2 (personnel competence assessment, six methods) — directly reused/adapted for POCT operator competency assessment.
- Clause 7 process requirements (sample ID, pre-examination handling) — POCT patient/sample identification and critical-value escalation mirror main-text pre-/post-examination controls.
- Chapter 6 clause 8 (document control, record control, nonconformity/CAPA, quality indicators) — POCT's SOP control, QC-failure handling, and gap corrective actions are direct applications of the same clause-8 QMS machinery to a decentralized setting.
