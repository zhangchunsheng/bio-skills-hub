# Chapter 5A: Process Requirements — Pre-examination and Examination (第五章 过程要求：检验前过程与检验过程)

## Core Idea
Clause 7 treats the whole testing pathway — request, collection, transport, reception, analysis, and quality assurance of results — as one continuous, risk-managed, traceable process. ISO 15189:2022 pushes labs from "we followed steps" to "we can show, with records, that risk to the patient was identified and controlled at every stage," and extends lab responsibility to non-lab staff (ward nurses, patients self-collecting) who act on the lab's behalf. For the examination phase, the standard formalizes a tiered evidentiary burden: adopted, unmodified methods need only **verification (验证)**; laboratory-developed or modified methods need full **validation (确认)** — and both feed into ongoing quality assurance via internal quality control (室内质控) and external quality assessment (室间质评).

## Frameworks Introduced
- **Whole-process risk-based thinking (基于风险的思维), clause 7.1**: Lab must have process(es) ensuring patient/sample identification and appropriate handling "as far as reasonably possible" at every process stage; identify risks to patient results from process deviations and act to minimize/prevent recurrence. When to use: at design of every pre-/during-/post-examination SOP. How: maintain a risk register (风险点-发生概率-后果严重性-控制措施-剩余风险), commonly scored with a probability×severity matrix.
- **Verification vs. Validation tiering, clauses 7.3.2/7.3.3**: Verification = confirm an unmodified, previously validated (manufacturer/published/reference) procedure meets its claimed performance before clinical use. Validation = establish performance from scratch for LDTs, modified, or off-label-use procedures. When to use: verification for adopted kits/reference methods; validation for in-house/modified/LDT methods (e.g., LC-MS/MS panels, in-house PCR). How: pre-define acceptance criteria, run defined experiments (below), sign off before "go-live."
- **Measurement uncertainty (测量不确定度, MU), forward-referenced under 7.3**: Lab shall determine MU for each quantitative procedure, use it in result interpretation, and provide it to users on request. How: pragmatic "top-down" method combining long-term IQC imprecision and EQA/PT bias: u_c = √(u(imprecision)² + u(bias)²), expanded uncertainty U = k·u_c (k=2 for ~95% CI).
- **Westgard multirule IQC**: statistically evaluate control results using combination rules (1_3s, 2_2s, R_4s, 4_1s, 10x) rather than a single 2SD limit, selected by test's sigma-metric to balance error detection vs. false rejection.
- **Sigma-metric QC design**: σ = (TEa − |bias|) / CV — guides how many rules and how often QC is run (high σ → simple/infrequent QC; low σ → intensive multirule + frequent QC).

## Key Concepts
- **Turnaround time (TAT，周转时间)** — target time-to-result defined per test/urgency (routine vs. STAT), must be monitored with compliance data and corrective action on misses [7.1].
- **Request information (申请信息)** — minimum data set (patient ID, requester, clinical info, sample type/site, collection/receipt date-time) required on paper or electronic request [7.2.2].
- **Informed consent (患者知情同意)** — explicit signed consent required beyond routine implied consent for HIV testing, genetic testing, invasive collection, and research use of samples [7.2.3].
- **Sample rejection criteria (标本拒收标准)** — pre-defined, documented conditions (mislabeling, wrong container/anticoagulant ratio, hemolysis, clotting, insufficient volume, delayed/mis-temperature transport) triggering rejection and clinician notification [7.2.5].
- **Irreplaceable sample exception (不可替代样本)** — CSF, bone marrow, etc. that fail criteria may still be tested with a report caveat instead of outright rejection, after clinician communication.
- **Verification (验证)** vs **Validation (确认)** — see Frameworks above [7.3.2, 7.3.3].
- **Limit of Blank/Detection/Quantitation (LoB/LoD/LoQ)** — CLSI EP17-style protocol; blank and low-level replicates (commonly n≥60 each across ≥2 lots/days) define detection capability [7.3.3].
- **Biological reference interval (生物参考区间) / clinical decision limit (临床决定值)** — adopted intervals must be verified for the local population (n=20 rule); decision limits (e.g., troponin 99th percentile) sourced from guidelines with documented rationale [7.3.5].
- **Internal Quality Control (室内质量控制, IQC)** and **External Quality Assessment / Proficiency Testing (室间质量评价/PT, EQA)** — ongoing, statistically evaluated verification that results meet intended quality; EQA per ISO/IEC 17043-equivalent schemes [7.3.6].
- **Comparability of results (结果可比性)** — cross-instrument/cross-site/POCT-vs-central-lab agreement, checked at defined intervals against a bias limit.

## Mental Models
- **Use the n=20 rule when adopting, not establishing, a reference interval**: verify with 20 local reference individuals; ≤2 outliers (≤10%) confirms fit-for-use. Think of it as a "spot-check," not a re-derivation — full establishment (large partitioned samples) is only needed when no suitable published interval exists.
- **Think of verification as "does it work here?" and validation as "does it work at all?"**: verification borrows someone else's proof of principle and checks local performance; validation builds the proof of principle from zero across every relevant analytical characteristic.
- **Treat EQA/PT like an audit you can't cram for**: samples must be handled by routine staff exactly as patient samples, with no inter-lab discussion before submission — the value is in ordinary practice being caught out, not in a best-case demonstration.
- **Use sigma-metrics to right-size QC effort**: don't apply the same QC frequency/rule set to every test — a high-sigma method needs less scrutiny than a low-sigma one; over-testing wastes resources, under-testing misses errors.

## Anti-patterns
- **Pre-labeling collection tubes before entering the patient's room**: breaks the person-to-sample link at the single highest-risk point in pre-examination; assessors treat this as a major nonconformity even if the final result is correct.
- **Releasing patient results while IQC is in violation ("test now, fix later")**: defeats the entire purpose of statistical QC; must stop, investigate, correct, then release.
- **Using only training sign-off as "authorization" evidence for competence** (recurring theme from adjacent clauses) — extends to accepting a manufacturer's verification/validation claim without local data.
- **Adopting a new analyzer's reference interval or switching platforms without re-verifying partitions (age/sex/pediatric)**: silent adoption without local verification and without notifying clinicians of a changed interval is a documented nonconformity pattern.
- **No documented alternative when no commercial EQA exists**: skipping external comparison entirely for niche/LDT tests instead of arranging inter-laboratory comparison or reference-material checks.
- **Validating a pneumatic tube or new transport method by assumption rather than data**: must run a split-sample comparison (e.g., hemolysis index, K+) before routine use, and exclude fragile analytes (e.g., blood gas) if data shows unacceptable bias.

## Reference Tables

**Verification vs. Validation — scope and parameters**
| Scenario | Requirement | Typical parameters checked |
|---|---|---|
| Unmodified adopted method (manufacturer/reference/published) | Verification (7.3.2) | Precision, trueness/bias, reportable range (linearity), reference interval applicability |
| LDT / self-developed / modified / off-label-use method | Full validation (7.3.3) | Precision (repeatability + intermediate), trueness, measurement uncertainty, analytical specificity (interference/cross-reactivity), analytical sensitivity, LoB/LoD/LoQ, measuring interval, diagnostic sensitivity/specificity (qualitative) |

**Typical minimum sample sizes / acceptance criteria (as presented)**
| Parameter | Minimum n / design | Acceptance |
|---|---|---|
| Precision (verification) | ~20 data points (e.g., 2 levels × 2 reps/day × 5 days, CLSI EP15-style) | CV within manufacturer's claim |
| Precision (full validation) | Longer study (e.g., 20 days × 2 reps/day, CLSI EP05-style) | Meets pre-defined CV target |
| Trueness/bias | ≥20 patient samples (method comparison) or CRM/recovery | Bias within clinical/TEa-based limit |
| Linearity/reportable range | ≥5 concentration levels across claimed range | Recovery within defined %/clinical bias |
| Carry-over | High-low alternating sequence (e.g., H-H-L-L-L) | Below manufacturer claim / clinically insignificant |
| LoB / LoD | ≥60 replicates each (blank; low-level sample), ≥2 lots/days (CLSI EP17-style) | Meets pre-defined statistical limit |
| LoQ | Derived from LoD study | CV (e.g., ≤20% for immunoassays) at LoQ concentration |
| Reference interval verification | n = 20 reference individuals | ≤2/20 (≤10%) outliers → verified; else investigate/establish own interval |
| Reference interval establishment (fallback) | Large partitioned sample (CLSI C28-style, commonly ≥120/partition) | Statistically derived interval |

**Sample rejection criteria (标本拒收标准) — representative categories**
| Category | Example condition | Disposition |
|---|---|---|
| Identification | Missing/mismatched label vs. request | Reject, recollect |
| Container/anticoagulant | Wrong tube; incorrect fill ratio (e.g., citrate tube underfilled) | Reject |
| Hemolysis | Interferes with K+, LDH, AST etc. | Reject or qualify result |
| Clotted sample | CBC/coagulation | Reject |
| Insufficient volume | Below minimum required | Reject |
| Contamination/dilution | Drawn from infusion line | Reject |
| Transport delay/temperature | Exceeds stability window | Reject |
| Irreplaceable sample (CSF, marrow) | Fails criteria but unique | Test with documented caveat + clinician notification, not automatic rejection |

**IQC (Westgard) rules and role**
| Rule | Trigger | Error type flagged |
|---|---|---|
| 1_3s | 1 observation beyond mean ± 3SD | Random error (reject) |
| 2_2s | 2 consecutive same-side beyond ±2SD | Systematic error (reject) |
| R_4s | Within-run range > 4SD | Random error (reject) |
| 4_1s | 4 consecutive same-side beyond ±1SD | Systematic error (reject) |
| 10x | 10 consecutive on same side of mean | Systematic drift (reject) |

IQC design: ≥2 material levels; frequency per run/24h or per batch (higher for POCT/high-risk tests); control mean/SD established from ≥20 data points before use; rule stringency and frequency selected via sigma-metric.

**EQA/PT and comparability**
| Item | Rule as presented |
|---|---|
| EQA scheme conformance | Should meet ISO/IEC 17043-equivalent program requirements |
| Samples handled by | Routine testing staff, routine method — no special handling |
| Communication | No inter-participant discussion of results before submission deadline |
| Performance scoring | z-score: \|z\|≤2 satisfactory; 2<\|z\|<3 warning; \|z\|≥3 unsatisfactory (or % deviation vs. TEa) |
| Repeated failure trigger | Consecutive/recurring unsatisfactory results (e.g., 2 consecutive or 2 within 6 months) → escalated CA, possible scope suspension |
| No EQA scheme exists | Alternative: inter-laboratory comparison, CRM, collaborative/research PT, or split-sample vs. alternative method — typically ≥2×/year |
| Inter-instrument/inter-site comparability | Evaluate ≥2×/year across measuring interval using patient samples/QC/EQA material; acceptance often within ½ TEa |

**Sample stability/storage/retention (representative figures noted in text)**
| Sample/analyte | Handling note |
|---|---|
| Glucose (no preservative) | Degrades several %/hour at room temp; separate/add glycolysis inhibitor promptly |
| Potassium | Separate serum/plasma from cells promptly to avoid hemolysis-driven false elevation |
| Blood gas | Analyze very soon after draw (minutes) or keep iced |
| Coagulation (citrate plasma) | Analyze within a few hours of proper centrifugation |
| Bilirubin | Light-protect; photodegrades |
| Pre-transfusion/compatibility sample | Retained several days at 2–8°C per transfusion regulation |
| Pathology blocks/slides | Retained long-term (years) per regulation |

> [gap: exact numeric hours/percentages for some stability figures on pp.148-149 were partially illustrative in the source table and should be cross-checked against the book's precise printed table if exact citation is required]

## Worked Example
A clinical chemistry lab switches immunoassay analyzers and adopts the new platform's manufacturer reference intervals for TSH, including pediatric partitions, without running its own verification. Clinicians flag inconsistent neonatal TSH interpretations. On assessment, this is raised as a nonconformity against 7.3.5: the lab failed to verify applicability of an adopted reference interval to its local population and did not notify users of the interval change. Corrective action: the lab runs a verification study using 20 reference individuals per relevant partition (e.g., pediatric and adult), confirms ≤2/20 outliers per partition, formally documents the rationale, and issues a notification to ordering clinicians before the interval goes live. This mirrors the general assessment pattern in this chapter: an unverified "silent adoption" of a performance claim (reference interval, transport method, or analytical method) is the recurring nonconformity theme across 7.2 and 7.3.

## Key Takeaways
- Clause 7.1 requires documented, risk-based control of the *entire* process, including TAT monitoring and whole-chain patient/sample identification — even where non-lab staff perform steps.
- Pre-examination (7.2) responsibility extends outward: request-form content, patient preparation/consent, collection labeling discipline, validated transport, defined rejection criteria, and documented stability/retention windows must all be objectively evidenced.
- Examination (7.3) distinguishes verification (adopted methods) from validation (LDT/modified methods) with different, more extensive parameter sets for the latter; every quantitative test needs a documented measurement uncertainty.
- Reference intervals/decision limits must be sourced, verified (n=20 rule) or established, and any change communicated to users.
- Quality assurance is closed-loop: IQC (Westgard multirules, sigma-metric design) catches errors before release; EQA/PT (or a documented alternative when none exists) and periodic comparability checks (≥2×/year) catch what IQC cannot.

## Connects To
- Chapter 4 (Resource Requirements, clause 6): personnel competence/authorization underpins who may collect samples, perform verification/validation, and release results.
- Chapter 5B (Post-examination processes, clause 7.4, and beyond): sample retention/disposal, result review/release, and reporting build directly on the pre-examination retention rules and examination QA data established here.
- Management System requirements (nonconformity management, risk and opportunity, management review): IQC/EQA failures and process nonconformities feed the same corrective-action and management-review loop described elsewhere in the book.
