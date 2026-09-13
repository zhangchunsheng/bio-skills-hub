# Patterns — Recurring Accreditation Techniques (常用方法与模式)

Reusable techniques the book applies again and again across disciplines. Each: when to use, how, trade-offs.

## Define → Provide → Verify → Record (the resource pattern, clause 6)
- **When**: any resource requirement — personnel, facility, equipment, reagent, external service.
- **How**: (1) *define* the requirement/spec, (2) *provide/secure* it, (3) *verify* it meets spec before use, (4) keep a dated, signed *record*. A requirement is never "met" at step 2.
- **Trade-offs**: heavy on documentation; but the record IS the accreditation evidence — skipping step 4 makes a correctly-performed activity un-provable.

## PDCA management-system loop (clause 8)
- **When**: structuring or auditing the whole QMS.
- **How**: policy/objectives → controlled documents/records → risk & opportunity → nonconformity/corrective action → evaluation (internal audit + quality indicators) → management review → revised objectives.
- **Trade-offs**: Option A (self-contained QMS) vs Option B (leverage existing ISO 9001) — almost all CNAS labs use Option A because Option B still must prove clauses 4–7 competence separately.

## Verification-vs-Validation tiering (clause 7.3)
- **When**: bringing any examination procedure into service.
- **How**: unmodified adopted method → verification (lighter parameter set); LDT/modified/off-label → full validation (adds MU, LoB/LoD/LoQ, specificity). See cheatsheet for minimum designs.
- **Trade-offs**: validation is expensive (dozens–hundreds of data points); under-classifying an LDT as "verify-only" is a common serious finding.

## Contamination defence-in-depth (molecular, clause 6.3)
- **When**: any nucleic-acid amplification workflow.
- **How**: physical four-area separation + uni-directional flow + air-pressure gradient + per-run negative/no-template controls + environmental amplicon monitoring. No single layer is sufficient.
- **Trade-offs**: space- and cost-intensive; closed cartridge systems can justify relaxation via risk assessment.

## Closed-loop critical-value (危急值) handling (clause 7.4)
- **When**: any result crossing a critical/alert threshold.
- **How**: detect → notify the right clinician within a defined time limit → read-back confirmation → record who/when/what/action. The loop is "closed" only when receipt is confirmed and logged.
- **Trade-offs**: adds call-time burden; but an unclosed loop is a direct patient-safety nonconformity.

## Traceability chain (clause 6.5)
- **When**: any quantitative result.
- **How**: patient result → working calibrator → manufacturer standing calibrator → CRM / reference measurement procedure → SI unit (ISO 17511). Where no higher-order reference exists, traceability to the manufacturer's documented reference system is acceptable.
- **Trade-offs**: for some analytes the chain stops at the manufacturer — disclose the limitation rather than overclaim SI traceability.

## Sigma-metric QC design (clause 7.3.6)
- **When**: choosing Westgard rules and QC frequency per analyte.
- **How**: σ = (TEa − |bias|) / CV; high σ → single/simple rules; low σ → multirule + higher frequency, or redesign the method.
- **Trade-offs**: requires reliable bias (EQA) and CV (long-term IQC) estimates; uniform QC across all tests wastes effort on high-σ assays and under-controls low-σ ones.

## Top-down measurement uncertainty (clause 7.3.4)
- **When**: reporting/estimating MU for a quantitative procedure.
- **How**: u_c = √(u(imprecision)² + u(bias)²); U = k·u_c, k=2 for ~95% CI, using long-term IQC CV and EQA/PT bias. Review after new lot, recalibration, or service.
- **Trade-offs**: pragmatic vs a full bottom-up (GUM) budget; adequate for clinical labs and expected by assessors.

## Discipline-refines-generic mapping (Part 2 pattern)
- **When**: reading any discipline chapter (8–18).
- **How**: each discipline application document (CNAS-CL02-A00x) does NOT restate the generic clause — it adds the discipline-specific criterion on top of clauses 6/7/8. Always read the generic chapter (4/5A/5B/6) alongside the discipline chapter.
- **Trade-offs**: you must hold two documents in view at once; but the discipline doc alone is incomplete.

## Six-annex mutual-consistency (application pattern, Ch 20)
- **When**: assembling or checking an accreditation application.
- **How**: the application form + 附表1–6 must agree on who applies, who is competent/signs, what is tested (applied subset vs full menu), how each criterion clause is evidenced, and proof of external verification. Cross-check every person, item, and clause reference across all annexes.
- **Trade-offs**: tedious reconciliation; a single mismatch (a signatory listed for a test not in the menu) stalls acceptance.

## Risk-based thinking across the pathway (clause 5.6, new in 2022)
- **When**: continuously — not annually.
- **How**: identify risks to patients at every pre-/examination/post-stage, score probability × severity, mitigate, re-assess. Feeds nonconformity, method choice, and management review.
- **Trade-offs**: replaces the old standalone "preventive action" clause; treating it as a once-a-year form is the top misuse.
