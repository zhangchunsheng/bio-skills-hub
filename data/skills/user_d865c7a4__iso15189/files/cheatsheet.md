# Cheatsheet — ISO 15189:2022 Accreditation Decision Rules (决策速查)

Decision rules, thresholds, and assessment "tells" distilled from the book. When a number is a common default rather than a fixed standard requirement, it is marked *(default)*. Verify against the current CNAS-CL02:2023 and the discipline application document (CNAS-CL02-A00x) before citing in a formal document.

## The one-line rule for everything
**"Performed" ≠ "met." A requirement is met only when a dated, signed, attributable record proves it was verified.** Assessors chase the record, not the activity. If you can't show who did it, when, and that it was checked — it doesn't count.

## Verify vs. Validate (7.3) — the most-tested distinction
| Situation | Do | Parameters |
|---|---|---|
| Adopt a method **unmodified** (manufacturer/published/reference) | **Verification (验证)** | Precision, trueness/bias, reportable range/linearity, reference-interval applicability |
| **LDT**, modified method, or off-label use | **Validation (确认)** | + measurement uncertainty, analytical specificity/interference, LoB/LoD/LoQ, measuring interval, (qualitative) diagnostic sens/spec |

**Default minimum designs** *(as presented in the book)*: precision ≈20 points (2 levels × 2 reps/day × 5 days); trueness ≥20 patient samples or CRM/recovery; linearity ≥5 levels; LoB/LoD ≥60 replicates each across ≥2 lots/days (CLSI EP17-style); reference-interval verification n=20 (**verified if ≤2/20 = ≤10% fall outside**), own interval ≥120/partition.

## Quality control quick rules
- **IQC**: ≥2 QC levels per run/24 h; establish mean/SD from ≥20 points first. A Westgard violation (1₃ₛ, 2₂ₛ, R₄ₛ, 4₁ₛ, 10ₓ) → **STOP releasing results**, investigate, correct, then resume. Releasing through an out-of-control signal = major nonconformity.
- **Right-size QC with sigma**: σ = (TEa − |bias|) / CV. High σ → simpler rules, less frequent QC; low σ → intensive multirule or redesign.
- **EQA/PT**: participate for **every** in-scope test, routine staff + routine method, no inter-lab collusion before deadline. Scoring: **|z| ≤ 2 satisfactory · 2<|z|<3 warning · |z| ≥ 3 unsatisfactory**. Unsatisfactory → root cause + retrospective patient-result review + corrective action. Recurrence (2 consecutive, or 2 within 6 months) → consider suspending the test.
- **No EQA scheme exists?** Use an alternative (inter-lab comparison, CRM, collaborative PT) **≥2×/year** — external verification is still mandatory.
- **Comparability** (multi-instrument/POCT vs central): **≥2×/year**, ~20 patient samples across the range, acceptance often **bias ≤ ½ TEa**.

## Pre-examination tells (7.2)
- **Label AFTER collection, at the bedside** — never pre-label. Pre-labeling breaks person-to-sample link = major nonconformity even if the result is correct.
- **Explicit signed consent** required for: HIV antibody, genetic/gene testing, invasive procedures, research use of leftover samples. Routine venipuncture's implied consent does not cover these.
- **Irreplaceable sample** (CSF, bone marrow, frozen tissue) that fails rejection criteria → do NOT auto-reject; test with a documented caveat + clinician communication.
- New transport (pneumatic tube) must be **validated by split-sample comparison** before routine use.

## Facility "hard gates" (physical, non-negotiable)
- **PCR / molecular** (卫办医政发〔2010〕194号): four physically separated areas (reagent-prep → specimen-prep → amplification → product-analysis), **uni-directional flow**, monitored **air-pressure gradient (Pa)**, PCR operator certificate (上岗证). Merging areas or reverse flow = classic contamination nonconformity.
- **Biosafety**: pathogen risk-grade → BSL level → containment + biosafety-cabinet class; autoclave validated with biological indicators (**121 °C, 15–20 min** *(default cycle)*).
- **Cold chain**: reagent/blood storage **2–8 °C** with continuous or ≥2×/day logged monitoring; a released blood unit out of controlled storage **>30 min** must not be returned to inventory *(transfusion default)*.

## Discipline "signature" thresholds (verify against the A-document)
| Discipline | Signature rule |
|---|---|
| Haematology (Ch 8) | Blood-film morphology review criteria + analyzer-flag rules; morphology competence assessed and recorded |
| Chemistry (Ch 10) | Every result traceable (ISO 17511) + TEa budget; calibration verification **≤6 months** *(default)*; inter-instrument comparison ≥2×/yr, bias ≤ ½ TEa |
| Immunology (Ch 11) | Qualitative assays: cut-off/grey-zone (灰区), retest/confirmation algorithm for infectious markers |
| Microbiology (Ch 12) | Reference-strain (ATCC) media/reagent QC; AST breakpoint version control (CLSI/EUCAST) reviewed **annually** |
| Transfusion (Ch 13) | Double independent ABO typing, forward+reverse confirmation; zero-tolerance for ABO-incompatible transfusion |
| Histopathology (Ch 14) | 10% neutral buffered formalin; fixation **6–48 h**; competence interval ≤1 yr (new staff ≥2 in first 6 mo); signatory ≥3 yr + intermediate title; objectives 标本合格率>95%, 诊断符合率>98%, 新项目>2/yr |
| Cytopathology (Ch 15) | Gynae screener **≤100 slides/working day**; cytology-histology correlation; TBS reporting |
| Molecular (Ch 16) | Per-run positive + negative + no-template + internal controls; NGS pipeline validated & version-controlled |

## Management-system cadence (Ch 6, clause 8)
- **Internal audit**: cover all clauses/areas over the cycle (commonly annually); auditors independent of the audited area.
- **Management review**: all mandated inputs (audit results, EQA, quality indicators, complaints, NC/CAPA, risk) → documented outputs/actions.
- **Nonconformity**: contain → root cause → corrective action → **effectiveness check** (the step most often missing).
- **Records/documents**: controlled, current version at point of use; retention per regulation.

## Application eligibility gates (Ch 19) — before you apply
- Management system has **actually operated** and produced clinical results (not just written).
- At least one full **internal audit + management review** cycle completed.
- **EQA participation history** for applied-for tests.
- Authorised signatories meet qualification (title + years in field).
- The six annexes (附表1–6) mutually consistent: who applies / who is competent / what is tested / how each clause is evidenced / proof of external verification.

## Tells & smells (instant nonconformity signals)
- SOP at the bench is an **outdated version**, or missing a required element (QC, reference interval, critical value, review/approval date).
- Quality objective phrased as a sentiment ("continuously improve") with no measurable target or review cadence.
- Stop-work / corrective-action authority assigned to a **department name, not a person**.
- Backups exist but **no restore test** recorded.
- Shared LIS logins → no attribution on result release/amendment.
- Risk register treated as an **annual paperwork exercise**, not continuous across the pathway.
- Off-site/mobile/POCT activity not inventoried under the same controls as the main site.
