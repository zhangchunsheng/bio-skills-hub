# Chapter 1: Terms and Definitions (术语和定义)

## Core Idea
ISO 15189:2022 clause 3 (术语和定义) redefines/expands the vocabulary shared with ISO/IEC 17000, ISO 9000, and VIM (ISO/IEC Guide 99); the single practical lesson the authors stress is that **internal terminology consistency** across the quality manual, SOPs, forms, and reports is itself audited evidence of genuine (not superficial) standard adoption.

## Frameworks Introduced
- **Three-source validation of a reference interval**: for every reportable test the lab must classify its 生物参考区间 (biological reference interval) as (1) self-established, (2) verified-from-transfer, or (3) directly adopted, and retain the supporting data accordingly. Use when publishing or reviewing any reference interval on a report.
- **Verification vs. Validation decision split**: unmodified manufacturer method → **证实/verification** (precision, trueness/bias vs. claim, reportable range); modified or lab-developed method (LDT) → **确认/validation** (full performance study: accuracy, precision, linearity, clinical performance). Use when introducing or changing any test method, before first clinical use.
- **标本 (specimen) vs 样品 (sample) staging**: 标本 = material as originally collected; 样品 = portion(s) taken from a specimen and prepared for examination. Use this distinction to word SOP steps and chain-of-custody/labeling records unambiguously.

## Key Concepts
- **accreditation (认可)** — third-party attestation of a conformity assessment body's competence, impartiality, and consistent operation; voluntary, distinct from mandatory practice licensing [clause 3].
- **alert interval / critical interval (警示区间/危急值)** — result range signaling immediate risk requiring urgent clinical action.
- **calibration (校准)** — two-step operation: establish the relation between reference values and indications (with uncertainty), then use it to derive a result from an indication; distinct from calibration verification/adjustment.
- **examination (检验)** — the set of operations determining the value/characteristic of a property of a sample; the standard's precise term, not to be mixed with colloquial 检测/化验.
- **external quality assessment / EQA (室间质量评价)** — evaluation via interlaboratory comparison; broader than 能力验证 (proficiency testing, PT), a formal statistical subset.
- **harm (危害) / risk (风险)** — harm = physical injury or damage to health/property/environment; risk = probability of harm × severity — the vocabulary underpinning risk-based thinking used later in clause 5.6.
- **medical laboratory (医学实验室/临床实验室)** — examines human body materials for diagnosis/prevention/monitoring/treatment/health assessment; may include advisory services and POCT sites within its scope.
- **metrological traceability (计量学溯源性)** — a measurement result's property of being related to a reference via a documented, unbroken calibration chain, each link contributing uncertainty.
- **quality indicator (质量指标)** — measurable metric of how well quality characteristics meet requirements (e.g., TAT compliance, sample rejection rate); requires targets and periodic review.
- **turnaround time / TAT (检验周转时间)** — interval from request/sample receipt to result release, monitored by urgency category.

## Mental Models
- Think of clause 3 as a **shared dictionary contract**: the lab doesn't need to restate these definitions, but every internal document must use them without contradiction — inconsistency itself is treated as a red flag.
- Use the **verification/validation split** as a gate: "did we change anything about the manufacturer's intended use?" If yes → validation; if no → verification only.
- Think of **EQA as the umbrella, PT as one instrument under it** — an item can satisfy the EQA requirement through PT, but where no PT scheme exists, some other interlaboratory comparison (e.g., split-sample exchange) must fill the gap.
- Use the **标本→样品 pipeline** as a mental checklist for traceability: every SOP step should be clearly assignable to either the "collection" stage or the "preparation/testing" stage.

## Anti-patterns
- **Treating "危急值" and "警示区间/alert interval" as fully interchangeable without cross-mapping them in SOPs**: assessors will probe for the standard's exact wording next to the lab's domestic terminology; an unmapped mismatch reads as a copy-paste manual, not genuine understanding.
- **Classifying a modified method as merely "verified"**: skipping the fuller validation performance study for a method that differs from the manufacturer's intended use is a common and serious nonconformity.
- **Mixing 标本 and 样品 in the same SOP interchangeably**: cited repeatedly by the authors as a frequent, easily-avoidable nonconformity trigger.
- **Publishing a reference interval without recording which of the three sourcing methods was used**: leaves the lab unable to justify the interval's validity during technical review.

## Reference Tables
| Term pair | Distinguishing question | Evidence required |
|---|---|---|
| 校准 calibration vs. 校准验证/调校 | Does it establish the value-indication relationship, or decide if an existing instrument still meets criteria? | Calibration cert + separate acceptance/adjustment log |
| 证实 verification vs. 确认 validation | Is the method unmodified from the manufacturer's intended use? | Verification data (unmodified) vs. full performance dossier (modified/LDT) |
| 标本 specimen vs. 样品 sample | Is this the material as collected, or a prepared portion for testing? | Collection record vs. preparation/testing record |
| EQA vs. PT | Is this a broad interlab comparison, or a formal statistical scheme under ISO/IEC 17043? | EQA/PT enrollment records; alternative-assessment plan if no scheme exists |

## Worked Example
A lab adopts a send-out immunoassay in-house **without modification** to the manufacturer's protocol — the authors classify this as requiring only **verification** (precision, bias vs. claim, reportable range check). By contrast, a lab that develops its own **cut-off value** for a novel biomarker is developing a lab-developed test, requiring full **validation**, including a clinical performance study, before results can be released. The distinguishing question the authors pose to assessors and labs alike: "did anything about intended use change?" — if yes, verification alone is an under-documented nonconformity waiting to be found.

## Key Takeaways
1. Terminology consistency across all lab documents is itself audited evidence — map domestic terms (e.g., 危急值) explicitly to the standard's terms (alert interval) in your SOPs.
2. Classify every method as unmodified (→ verification) or modified/developed (→ validation) *before* clinical use, and keep the classification rationale on file.
3. Never conflate 标本 and 样品 — use them to anchor distinct SOP stages for traceability.
4. Every reference interval must show its sourcing method (self-established / verified-transfer / adopted) with supporting data.
5. Where no EQA/PT scheme exists for a test, document an alternative interlaboratory comparison mechanism.
6. Metrological traceability requires a full unbroken chain to the highest available reference, not just a calibration certificate on file.

## Connects To
- **Ch2**: The harm/hazard/risk vocabulary from clause 3 directly underlies the risk-identification language used in 4.1 impartiality risk assessment.
- **Ch3**: Quality indicator and risk/harm definitions here are the operational building blocks for clause 5.5 (objectives, which are measured via quality indicators) and clause 5.6 (risk management, which applies the harm/hazard/risk framework across the testing pathway).
