# Chapter 12: Clinical Microbiology (第十二章 临床微生物学检验认可要求与迎检思路)

## Core Idea
Microbiology accreditation applies the same ISO 15189 clauses as other disciplines but with a distinctive risk profile: results depend on organism *growth kinetics* rather than a single instrument readout, so turnaround time, "negative" reporting, and critical-value chains must be tiered (smear → preliminary culture → final ID+AST) instead of treated as one clock. The chapter's two other structural pillars are biosafety (staff/environment protection from live pathogens) and QC/reagent traceability (reference-strain-verified media, reagents, and antimicrobial susceptibility testing, with annual breakpoint-version control). Assessors probe whether the lab can *prove* each stage independently, not just show a final report.

## Discipline-Specific Requirements

### 人员 (Personnel)
- Section leadership requires a medical-microbiology/laboratory-medicine background plus defined years of relevant experience; sign-off authority for 涂片报告 (smear reports) is authorized **separately** from 鉴定与药敏报告 (identification & susceptibility reports), reflecting their different risk/complexity levels.
- Competency must be assessed **per task**, not as one blanket "microbiology" skill: Gram-stain smear reading, colony/culture reading, biochemical/automated identification, susceptibility interpretation, and blood-culture instrument operation are each evaluated separately, typically ≥1×/year, via direct observation, blind/proficiency panels, or split-sample comparison against senior staff.
- New, rotating, or trainee staff may not release results independently until task-specific competency is documented; on-call/night staff must show equivalent documented competency to daytime staff.
- Continuing education records must cover new identification technology (MALDI-TOF, molecular methods) and annual resistance-mechanism/breakpoint updates.

### 设施与环境 (Facilities & Environment)
- Aerosol-generating steps (specimen processing, subculture, AST inoculation) require a Class II biosafety cabinet (生物安全柜), certified for airflow/HEPA integrity by a qualified external service **≥1×/year**.
- Routine bacteriology is performed at BSL-2 (二级生物安全实验室); suspected highly pathogenic or notifiable organisms (e.g., *Brucella*, *M. tuberculosis*, avian influenza) require escalation/referral per a written list rather than local full workup.
- Workflow must be physically segregated along a "contaminated → semi-contaminated → clean" (污染区-半污染区-清洁区) single direction to prevent cross-contamination; AFB/sputum processing needs independent or negative-pressure ventilation where performed on-site.
- Autoclave/waste decontamination is validated with a biological indicator at a defined frequency (each critical load, commonly ≥1×/week); environmental temperature/humidity for incubator rooms and reagent storage is logged, with access restricted to trained staff.

### 设备与试剂 (Equipment & Reagents)
- Incubators are monitored ≥2×/day (or continuously with alarm); CO2 incubators require CO2-concentration monitoring in addition to temperature; the acceptable range is specific to the target organism (routine 35–37°C).
- Automated blood-culture and ID/AST systems (VITEK, MALDI-TOF, Phoenix, etc.) require installation verification, periodic performance verification against reference strains, and periodic correlation checks against a manual/reference method.
- **Media QC (培养基质量控制)**: each batch/lot is checked before use for sterility, growth-promotion, and selectivity/biochemical reactions using reference strains.
- **Reagent/AST QC frequency**: each new lot of media, Gram-stain/biochemical reagents, and antimicrobial disks/panels is checked before use; routine QC continues thereafter at a defined interval — daily for reagents run alongside patient testing (e.g., Gram-stain controls same day as patient smears), and for AST QC strains a weekly baseline that may step down toward monthly only after a defined run of consecutive in-control days (per CLSI weekly→monthly stepdown criteria).
- **Antimicrobial susceptibility testing (AST/药敏试验) breakpoint control**: the lab must document which CLSI M100 edition (or EUCAST version/year) is currently in force, its internal annual-update review process, and a superseded-version log, because S/I/R interpretive categories shift year to year on the same MIC/zone value.

### 检验前 (Pre-examination)
- Specimen-specific rejection criteria: unlabeled/mismatched specimens, wrong container, transport time beyond the defined stability window, insufficient volume, or a request-type/specimen-type mismatch (e.g., anaerobic culture ordered on an aerobic swab).
- Transport is specimen-type specific (blood-culture bottles near body temperature, prompt delivery; urine refrigerated if delay >~2h; see Reference Tables). Blood-culture policy defines minimum draw volume per bottle/age group and collection sets (2 sets/2 venipuncture sites for adults) to distinguish bacteremia from contamination.

### 检验中 (Examination)
- Identification workflow proceeds colony morphology → Gram stain → biochemical/automated ID → confirmatory testing for clinically significant or unusual organisms, with defined criteria for referral to a reference lab (unidentifiable organism, unusual resistance phenotype, notifiable pathogen).
- AST method (disk diffusion / broth microdilution / gradient strip) must match the organism, run with parallel QC; fastidious organisms require documented alternate media/methods.

### 检验后 (Post-examination)
- **Tiered critical values**: any positive blood-culture Gram stain, positive sterile-body-fluid smear/culture, or identification of a notifiable/highly pathogenic organism (*Salmonella typhi*, *N. meningitidis*, *C. diphtheriae*, *B. anthracis*, *V. cholerae*, CRE) is called to the clinician **immediately on the smear/preliminary result**, not held for the final ID+AST report, and simultaneously triggers infection-control/public-health reporting.
- Reports must state the interpretive AST category (S/I/R) with reference to the specific breakpoint table/version used; "no growth" reports must confirm the defined minimum incubation period was completed — reporting negative before that window closes is a nonconformity.
- **Tiered TAT**: smear (same shift/hours) < preliminary culture growth < final ID+AST (routine bacteria commonly 48–72h, longer for slow growers/fungi/mycobacteria) — each stage carries its own monitored target, not a single test-wide TAT.
- Clinically significant isolates are retained frozen for a defined period (commonly ≥1 week) to support add-on testing, repeat AST, or outbreak investigation.

### 质量保证 (Quality Assurance)
- Internal QC (室内质控) for AST runs against the CLSI/EUCAST reference-strain table each testing day (or the qualifying reduced frequency); out-of-range results block release of that run's patient results pending root-cause investigation.
- External quality assessment (室间质评/EQA) is mandatory for every identification/susceptibility category offered; unsatisfactory performance triggers investigation, retraining, and suspension of reporting for the affected test until resolved.
- Where no EQA program exists for a test, the lab performs alternative performance assessment (inter-lab split-sample or blind-panel comparison) at a defined frequency.
- Comparability between duplicate/backup instruments or manual-vs-automated methods is verified periodically; personnel accuracy (smear reading, ID agreement, AST major/very-major error rates) is tracked as ongoing competency evidence.

## Frameworks Introduced
- **Tiered critical-value/TAT chain**: smear → preliminary growth → final ID+AST, each stage independently timed and independently alarm-gated. When to use: any culture-based test. How: separate SOP clocks and separate notification triggers per stage, not one blended TAT.
- **Breakpoint version-control log**: CLSI M100/EUCAST edition-in-force documented, reviewed annually, superseded versions archived. When to use: whenever AST interpretive categories are applied. How: annual review checklist tied to LIS interpretive-table update.
- **Task-split competency assessment**: smear/culture-reading/ID/AST interpretation assessed as distinct skills, ≥1×/year each. When to use: all microbiology staff. How: direct observation + blind panel + split-sample comparison, logged per task.

## Key Concepts
- **Biosafety cabinet (生物安全柜)** — Class II containment for aerosol-generating steps; airflow/HEPA certified ≥1×/year.
- **QC/reference strain (标准菌株)** — ATCC-numbered organism used to verify media, reagent, ID, and AST performance before/alongside patient testing.
- **Breakpoint (折点)** — the CLSI/EUCAST interpretive S/I/R threshold; version/year must be tracked.
- **Critical value (危急值)** — e.g., a positive blood-culture smear or notifiable-pathogen ID, reported ahead of the final culture report.
- **Minimum incubation/holding time (最低培养时间)** — the period that must elapse before a negative culture can be finalized.
- **Growth-promotion test (生长促进试验)** — batch-level media QC confirming expected growth/reactions.
- **Isolate retention (菌株保留)** — frozen storage of significant isolates for a defined follow-up window.
- **Alternative performance assessment (替代评估)** — blind-panel/inter-lab comparison used when no formal EQA scheme exists for a test.

## Mental Models
- **Use "one test, three clocks"** for any culture-based examination: smear TAT, preliminary-growth TAT, and final ID+AST TAT are separate promises, each needing its own monitored target.
- **Think of AST QC as "two failure modes stacked"**: (1) the reagent/media itself might be bad (media/reagent QC with reference strains) and (2) the interpretive table might be stale (breakpoint version control) — both must be current for a susceptibility result to be trustworthy.
- **Use "referral list, not judgment call"** for biosafety escalation: whether an organism requires BSL-2+ handling or reference-lab referral should be answered by a pre-written list, not by an individual technologist's risk assessment in the moment.

## Anti-patterns
- **Treating microbiology competency as one blanket sign-off**: hides that a person may read smears well but misinterpret AST — assessors expect per-task records.
- **Reporting "no growth" before the minimum incubation window closes**: an early negative is unverifiable and risks false-negative patient harm.
- **Waiting for final ID+AST to call a positive blood culture**: defeats the purpose of the smear-stage critical value; bacteremia notification must not wait on identification.
- **Applying a stale AST breakpoint table**: an unchanged MIC value can flip from S to R (or vice versa) purely from a CLSI/EUCAST annual update — using last year's table without a documented review is a citable gap even if the assay itself is unchanged.
- **Releasing patient AST results from a run whose QC strain was out of range**: QC failure must gate release, not be reviewed after the fact.

## Reference Tables

**Biosafety & containment**
| Item | Requirement |
|---|---|
| Routine bacteriology | BSL-2 |
| Aerosol-generating steps | Class II biosafety cabinet, certified ≥1×/year |
| Notifiable/high-risk organisms | Escalate/refer per written list (e.g., *Brucella*, *M. tuberculosis*, avian influenza) |
| Decontamination | Autoclave validated with biological indicator each critical load / ≥1×/week |
| Workflow | Single-direction 污染区→半污染区→清洁区 |

**Staff competence areas (assessed separately, ≥1×/year)**
| Task | Method |
|---|---|
| Gram-stain smear reading | Direct observation / blind panel |
| Culture/colony reading | Split-sample comparison |
| Identification (biochemical/automated) | Blind panel, reference-method comparison |
| AST interpretation | QC strain comparison, error-rate tracking |
| Blood-culture instrument operation | Direct observation |

**Reference (QC) strains commonly used for media/ID/AST QC**
| Organism | ATCC no. | Use |
|---|---|---|
| *E. coli* | 25922 | General QC, disk diffusion |
| *S. aureus* | 25923 / 29213 | Disk diffusion / MIC QC |
| *P. aeruginosa* | 27853 | AST QC |
| *E. faecalis* | 29212 | AST QC |
| *K. pneumoniae* | 700603 | ESBL QC |
| *H. influenzae* | 49247 / 49766 | Fastidious-organism AST QC |
| *N. gonorrhoeae* | 49226 | AST QC |
| *S. pneumoniae* | 49619 | AST QC |
| *B. fragilis* | 25285 | Anaerobe AST QC |
| *C. albicans* | 90028 | Fungal QC |

**Incubator/CO2/temperature monitoring**: ≥2×/day manual check or continuous logging with alarm; CO2 incubators monitor gas concentration alongside temperature; routine target 35–37°C, adjusted per organism.

**AST QC & breakpoint version control**: new lot/shipment QC before use; routine QC daily (reagents run same-day as patient tests) to weekly (AST QC strains), stepping down only after a defined in-control run; current CLSI M100/EUCAST edition documented and reviewed annually, superseded versions archived.

**Blood culture & critical-result/transport rules**: 2 sets/2 sites per adult draw; positive smear called immediately as critical value; notifiable-pathogen ID triggers clinical + public-health reporting; negative culture requires minimum incubation completion; bottles near-body-temperature with prompt delivery; urine refrigerated if delay >~2h; stool/swabs in appropriate transport media.

## Worked Example
An assessor reviews a blood-culture workflow: the automated analyzer flagged a bottle positive at 2:15am, but the Gram-stain result and clinician notification were not logged until the day-shift review at 8:00am. Finding: no documented SOP linking "instrument positive alarm → immediate Gram stain → immediate critical-value call," so the smear-stage critical value was effectively skipped overnight. Root cause: the critical-value chain was built around the *final* culture report, not the *preliminary* alarm. Corrective action: a dedicated blood-culture-positive workflow requiring on-call staff to perform the smear and call within a defined limit at any hour, with the call time logged — closing the gap between instrument alarm and the tiered critical-value chain described above.

## Key Takeaways
- Microbiology's accreditation risk is structurally different from chemistry/hematology: growth kinetics force a *tiered* TAT/critical-value chain (smear → preliminary → final) rather than one clock.
- Competency, QC, and breakpoint currency must all be demonstrated at the *task* level (smear vs. ID vs. AST), not as a single microbiology-wide claim.
- Biosafety (BSL-2, BSC certification, referral lists) is a first-class, discipline-specific resource requirement layered on top of the generic facilities clause.
- Reference-strain-based QC and annual breakpoint-version control are the two traceability anchors that make an AST result defensible.

## Connects To
- **Ch 4 (Resources — Personnel/Facilities/Equipment)**: task-split competency, BSC certification, and reference-strain QC are microbiology's concrete instantiation of the generic personnel/facility/equipment clauses.
- **Ch 5 (Process — pre/examination/post-examination)**: tiered TAT and the smear-first critical-value chain refine the generic 7.4 critical-value and TAT requirements for a growth-dependent test.
- **Ch 6 (Management System Requirements)**: EQA/alternative-performance-assessment failures and QC-strain excursions feed the same nonconforming-work and management-review cycle as other disciplines, with biosafety incidents as an added trigger category.
