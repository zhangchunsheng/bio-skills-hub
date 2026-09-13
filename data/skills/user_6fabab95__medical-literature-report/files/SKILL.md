---
name: medical-literature-report
description: 面向临床医学、检验医学、护理、药学、公共卫生及生物医学科研，完成英文医学文献的检索筛选、合法全文与补充材料核验、专业中文翻译、研究设计和统计方法解读、批判性评价、证据边界标注、专业实践启示、图文汇报PPT制作及文件归档。适用于按专业方向、关键词、主题、期刊、作者、机构、DOI、PMID等条件查找与比较文献，以及科室学习、研究生组会、文献精读、教学查房和科研汇报。
---

# Medical Literature Report

Build evidence-traceable Chinese literature reports for any medical specialty. Adapt the workflow to the article type, audience, and reporting purpose instead of forcing every paper into one template.

## Route The Request

- Read `references/literature-screening.md` for discovery, comparison, and article selection.
- Read `references/source-acquisition.md` for lawful full-text and supplement acquisition.
- Read `references/medical-translation.md` for Chinese translation or structured close reading.
- Read `references/study-design-appraisal.md` for design-specific methods and critical appraisal.
- Read `references/report-standard.md` before creating or revising a PPT.
- Read `references/evidence-and-practice-interpretation.md` for evidence boundaries and professional implications.
- Run `scripts/article_inventory.py` to inventory PDFs, Office files, and deliverables.
- Run `scripts/package_deliverables.py` to create a verified delivery folder from a manifest.

## Intake

Accept any combination of:

- specialty, disease, population, intervention, exposure, test, biomarker, or outcome;
- keywords or Boolean expressions;
- clinical question or reporting theme;
- journal name, tier, publisher, author, research group, or institution;
- DOI, PMID, PMCID, exact title, or title fragment;
- publication window, language, article type, access requirement, article count, and audience;
- output request such as candidate table, translation, appraisal, PPT, speaker notes, or archive.

Classify each criterion as:

- `hard`: every selected paper must satisfy it;
- `preferred`: use it to rank otherwise eligible papers.

Infer conservatively when the user does not label criteria. State material assumptions in the candidate table. Ask only when a mistaken assumption would change the result substantially.

## Integrated Workflow

1. Normalize the request into hard filters, preferred filters, audience, and deliverables.
2. Identify the article type and study design before selecting an appraisal path.
3. Search current primary sources. Browse whenever publication status, journal metrics, guidelines, access status, affiliations, or other current facts matter.
4. Build a candidate matrix before recommending papers. Never judge suitability from titles alone.
5. Verify bibliographic identity, article type, study design, population, sample size, methods, outcomes, full-text status, figure completeness, and relevance to the target audience.
6. Obtain the main article and necessary supplements from lawful sources. Never bypass paywalls or access controls.
7. Build a source fact sheet before translating or designing slides. Capture numbers, units, effect estimates, confidence intervals, P values, time points, interventions, assays, eligibility criteria, outcome definitions, and stated limitations.
8. Translate or summarize with consistent medical terminology. Preserve uncertainty, null findings, and study-design language.
9. Apply the design-specific appraisal. Distinguish risk of bias, reporting quality, external validity, and practical relevance.
10. Build the presentation claim spine before layout: background -> gap -> objective -> design -> methods -> results -> interpretation -> limitations -> implications.
11. Use original article figures and tables as evidence objects. Crop or enlarge without changing data meaning, labels, scales, or context.
12. Separate original findings, Chinese paraphrase, author interpretation, external evidence, and presenter inference.
13. Render and inspect every slide. Verify citations, page count, media integrity, text overflow, figure readability, and PowerPoint opening.
14. Preserve prior versions and package only requested deliverables after hash verification.

## Default Deliverables

Produce the applicable subset:

- candidate literature comparison table;
- main article, supplements, and provenance log;
- structured Chinese translation or close-reading document;
- design-specific critical appraisal;
- source-faithful Chinese PPTX with speaker-ready narrative;
- separately labeled clinical, laboratory, nursing, pharmacy, or public-health implications;
- discrepancy log for conflicts among text, tables, figures, supplements, registries, or metadata;
- verified archive folder with inventory and hashes.

Do not impose a fixed slide count. A focused paper may need 20-25 slides; a complex trial, diagnostic study, omics paper, or meta-analysis may need 30 or more. Completeness and comprehensibility take priority unless the user gives a hard limit.

## Evidence Rules

- Do not fabricate data, significance, mechanisms, thresholds, citations, impact factors, or article availability.
- Do not convert association into causation or statistical significance into clinical importance.
- Do not present exploratory cutoffs as validated clinical decision limits.
- Do not generalize animal, cell, single-center, subgroup, or post hoc findings beyond their evidence.
- Do not redraw or edit a result figure in a way that changes its meaning.
- Label presenter-derived practice implications as inference based on the paper.
- Verify current journal metrics at task time and record metric name, year, and source.
- Flag discrepancies instead of silently choosing a convenient value.
- Do not expose patient-identifiable or confidential data in outputs.
- Treat outputs as research and education materials, not patient-specific medical advice.

## Script Commands

Inventory deliverables:

```bash
python scripts/article_inventory.py paper.pdf report.pptx --output inventory.json
```

Package deliverables:

```bash
python scripts/package_deliverables.py manifest.json delivery-folder
```

Manifest example:

```json
{
  "articles": [{"source": "/path/paper.pdf", "name": "01_paper.pdf"}],
  "supplements": [],
  "translations": [],
  "presentations": [{"source": "/path/report.pptx"}],
  "source_notes": []
}
```

## Completion Gate

Do not call the work complete until:

- selected papers satisfy all hard criteria and recommendation reasons are explicit;
- article identity, design, date, and access status are verified;
- main text and required supplements are complete or missing content is disclosed;
- translated values and terminology match the source;
- appraisal follows the correct study design;
- every result figure or table in the PPT has provenance;
- inference is visibly separated from source conclusions;
- every slide is rendered and visually checked;
- final files open successfully and copied files match their source hashes.
