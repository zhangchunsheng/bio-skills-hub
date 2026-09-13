---
slug: clinical-statistics-audit
version: 1.0.0
displayName: Clinical Statistics Audit
name: clinical-statistics-audit
description: "Audit the statistical design, analysis, and reporting of a clinical study, protocol, CSR, or manuscript and return a traceable Chinese remediation report. Use for 临床统计审计, statistical-method review, endpoint-analysis checks, CONSORT/STROBE/STARD/TRIPOD reporting checks, or pre-submission statistical QA."
---

# Clinical Statistics Audit

## Audit Contract

Identify the supplied artifact, version, study type, intended use, target journal or reporting guideline, and whether the request concerns a protocol, results report, or published manuscript. Audit only evidence available in the supplied material. Mark absent information as `原文未报告` or `待统计学家确认`; do not infer methods, sample-size calculations, or results.

Do not alter the manuscript unless the user explicitly requests a revised copy. Preserve the source text, tables, figures, footnotes, and reference numbering.

## Workflow

1. Classify the study as randomized trial, observational study, diagnostic study, prediction-model study, systematic review/meta-analysis, single-arm study, or other. State the basis and uncertainty.
2. Build a source-traceability table for the research question, population, intervention/exposure, comparator, outcome hierarchy, sample size, analysis population, statistical methods, results, and limitations. Each row must include an original location.
3. Select the applicable reporting checklist: `CONSORT` for randomized trials, `STROBE` for observational studies, `STARD` for diagnostic accuracy studies, `TRIPOD` for prediction models, `PRISMA` for systematic reviews/meta-analyses, or state why no listed checklist applies.
4. Audit the design-analysis match, endpoint-analysis match, result-reporting completeness, and checklist coverage. Separate confirmed defects from issues that require additional data or specialist judgment.
5. Produce the audit report and apply the quality gate below.

## Required Checks

### Design and Analysis Population

Check allocation/randomization, concealment, blinding, control/comparator, unit of analysis, follow-up, analysis population (`ITT`, modified ITT, per-protocol, safety set), protocol deviations, and confounding controls where applicable. Check whether the stated estimand/question matches the analysis population and time point.

### Endpoints and Statistical Methods

For every primary, secondary, exploratory, and safety endpoint, record original wording, outcome type, time point, model/test, effect estimate, confidence interval, P value, and source location. Check whether:

- continuous, binary, time-to-event, count, repeated-measure, clustered, or ordinal data have an appropriate method;
- covariate adjustment, baseline handling, interaction/subgroup tests, sensitivity analyses, and model assumptions are described and justified;
- missing data, censoring, multiplicity, interim analyses, and protocol/SAP deviations are addressed;
- sample-size assumptions and the analysis code/software/version are reported when relevant.

Do not label a method as wrong solely because an alternative is possible. Explain the mismatch between the stated question/data and the reported method.

### Results and Reporting

Check participant flow, baseline balance, denominators, missingness, harms, precision, effect size, confidence interval, P-value presentation, absolute and relative measures, tables/figures, and consistency among abstract, main text, tables, figures, registry/protocol, and conclusions. Flag selective emphasis, unsupported causal language, or conclusions exceeding design/evidence.

## Severity and Deliverable

Return a Chinese `临床统计审计报告` containing:

| Section | Requirement |
|---|---|
| 审计范围 | artifact, version, study type, intended use, inspected sources, exclusions |
| 方法与报告概览 | extracted design, endpoints, analysis populations, methods, and applicable guideline |
| 发现清单 | ID, original location, source excerpt, severity, issue, rationale, and correction action |
| 报告规范核查表 | checklist item, status, evidence location, and required action |
| 整改优先级 | owner, prerequisite, acceptance criterion, and re-audit trigger |
| 审计结论 | `PASS`, `CONDITIONAL PASS`, or `BLOCK`, with unresolved limitations |

Use `Critical`, `High`, `Medium`, or `Low` severity. Write all findings, analysis, and recommendations in Chinese except original quoted text, standard guideline names, statistical notation, software names, and necessary English technical terms.

## Quality Gate and Boundary

Issue `BLOCK` for an undisclosed primary endpoint change, materially incompatible analysis, missing key analysis population/denominator, unsupported efficacy or safety conclusion, or an unresolvable conflict between core sources. Issue `CONDITIONAL PASS` only when every remaining defect has a bounded remediation action, owner, and re-audit trigger. Otherwise issue `PASS` only for the inspected scope.

This Skill provides methodologic quality assurance. It does not replace a biostatistician's independent analysis, statistical sign-off, institutional ethics review, data monitoring, regulatory review, or clinical judgment.
