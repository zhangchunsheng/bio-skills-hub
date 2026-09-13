---
slug: clinical-research-design-extractor
version: 1.0.0
displayName: Clinical Research Design Extractor
name: clinical-research-design-extractor
description: "Extract a traceable clinical research design and results from a CSR, protocol, publication, registry record, or project file, or create a SPIRIT-aligned design framework. Use for \"临床研究方案提取\", CSR analysis, participant eligibility, endpoint classification, study-result extraction, protocol comparison, or clinical study planning."
---

# Clinical Research Design Extractor

## Select the Mode

- `源文件解析模式`: parse what the source document actually states.
- `研究设计模式`: propose a design framework and validate it against published evidence.

Never mix extracted facts with design recommendations. Record the source type, version, date, and document ID before analysis.

## Source Hierarchy and Reconciliation

For CSR work, inspect the synopsis, objectives/endpoints, protocol, statistical analysis plan, efficacy results, safety results, tables/listings/figures, and appendices. When documents conflict, preserve each version in a discrepancy table; do not silently choose one.

## Required Extraction Structure

### 1. 研究对象与受试者

Extract target population, setting, sample size, recruitment, screening, allocation, analysis populations, baseline characteristics, and complete inclusion/exclusion criteria. Quote or closely preserve eligibility wording and give a source location. If absent, write `原文未报告`.

### 2. 研究设计

Extract study type, phase, purpose/positioning, prospective/retrospective status, centres, controls, randomization, concealment, blinding, intervention/exposure, comparator, duration, visits, and follow-up.

### 3. 研究方法

Extract procedures, measurements, instruments, data collection, model construction, sample-size method, statistical methods, estimands, analysis populations, missing-data handling, multiplicity control, sensitivity/subgroup analyses, and safety monitoring. Do not include observed result values.

### 4. 研究结果

Report participant disposition and baseline results, then separate:

- `主要终点结果`
- `次要终点结果`
- `探索性终点结果`
- `安全性结果`
- `其他未明确分层结果`

For every result, capture the endpoint's original designation, measure, time point, analysis population, estimate, confidence interval, P value, and source location.

## Endpoint Classification Rules

Classify endpoints according to the source article's objectives, prespecified endpoint hierarchy, statistical analysis plan, results headings, and discussion logic. Do not classify by statistical significance or narrative prominence alone.

- Preserve `primary`, `secondary`, `exploratory`, and `safety` labels when explicitly stated.
- If the article discusses an outcome but never assigns a tier, place it under `其他未明确分层结果` and explain the evidence.
- Record discrepancies between protocol/registry/CSR/publication labels instead of resolving them by guesswork.

Safety extraction must cover AE, SAE, AESI, deaths, discontinuations, laboratory tests, vital signs, ECG, and exposure when reported.

## Two Traceability Tables

Do not conflate these tables:

1. `源文件解析溯源表`: proves that the generated report faithfully parses the supplied article/CSR. Include report field, document ID, exact location, excerpt, and extraction confidence. This supports report fidelity, not study validity.
2. `研究设计外部证据表`: used only in design mode or when explicitly validating the study design. Link each design choice to verified published literature or guidance and state applicability/limitations. This supports design rationale, not source-text fidelity.

## Design Mode

Produce a SPIRIT-aligned framework covering rationale, PICO/PECO, objectives, design, eligibility, intervention/exposure, comparator, endpoint hierarchy, safety outcomes, visits, sample size, statistics, missing data, bias controls, data governance, registration, ethics, and monitoring. Mark every unconfirmed choice as an assumption requiring investigator approval.

## Quality Gate

Block delivery if eligibility is silently omitted, methods and results are mixed, endpoint tiers lack source logic, or a traceability table is presented without stating which type of credibility it supports.
