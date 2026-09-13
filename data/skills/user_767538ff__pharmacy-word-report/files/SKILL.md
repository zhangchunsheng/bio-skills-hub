---
icon: icon.png
name: pharmacy-word-report
description: 'This skill should be used when a hospital pharmacist or clinical pharmacist provides a drug-use / pharmacy outbound (药库出库) Excel file and asks for a formatted Word (.docx) analysis report with three-line tables (三线表), conclusion-first sections, and embedded charts. It covers the full pipeline: profile and validate the Excel, aggregate spend by drug (Top 50), ATC level 1–4, and department, detect suspicious department–drug mismatches, then generate a layered, publication-ready Word report. Trigger phrases include 药品使用分析报表, 生成Word格式的药品使用分析, 三线表, 药库出库分析, 科室药品使用分析, and any request to turn a drug-outbound spreadsheet into a Chinese pharmacy management report.'
slug: pharmacy-word-report
version: 1.0.0
displayName: 医院药品使用分析
summary: 'This skill should be used when a hospital pharmacist or clinical pharmacist provides a drug-use / pharmacy outbound (药库…
category: 药学服务
license: Internal
tags: [药学服务]
author: 雷明
---


# Pharmacy Word Report（药品使用分析 → 三线表 Word 报表）

## Overview

This skill turns a hospital drug-use / pharmacy-outbound Excel workbook into a structured, layered
Word report with three-line tables (三线表) and conclusion-first narrative. It reuses two bundled
Python scripts (`analyze.py` for aggregation + charts, `build_docx.py` for the Word document) and a
report template (`references/report_template.md`). The workflow is deterministic, so the same
scripts run month after month — only the input file changes.

## When to Use

- User uploads / references a pharmacy drug-use Excel (columns typically include 科室, 入库单位, 数量,
  单价, 金额, 医保编码, 通用名, 最终ATC分类1级…4级) and asks for a Word analysis report.
- User asks for "三线表 / 结论先行 / 分层级" pharmacy reports, or "药库出库 / 科室药品使用分析".
- Do **not** use for pure data exploration without a deliverable, or for non-pharmacy spreadsheets
  (use the generic data-analysis skills instead).

## Constraints (always enforce)

- **No fabrication**: aggregate only the fields present; never impute or backfill missing values.
  Report missing/zero values truthfully (e.g., 金额为 0 / 单价为 0 记录).
- **结论先行 + 分层级 + 三线表**: every section opens with a 【结论】 sentence; tables use only top /
  header-bottom / bottom horizontal rules (no vertical lines).
- **脱敏**: never surface patient-identifying data; this dataset has none by design.
- Amounts in 万元 for table cells, 亿元 for overall magnitude; 占比 = share of total hospital spend.

## Workflow

### Step 1 — Set up the environment (first run only)
Create an isolated venv and install dependencies (the bundled scripts need them):
```
(managed-python) -m venv (venv)
(venv)/Scripts/pip install pandas openpyxl python-docx matplotlib
```
Use the managed Python runtime; do not install into the user environment.

### Step 2 — Profile & validate (optional but recommended)
Read the Excel with `pandas`. Verify `金额 == 数量 × 单价` (flag any mismatch above 0.01), report per-column
missing counts, and confirm the ATC 1–4 columns are fully populated. This is the data-quality basis
for the report's "数据概况与质量" section.

### Step 3 — Run the aggregation script
```
(venv)/Scripts/python.exe scripts/analyze.py (input.xlsx) [workdir]
```
`analyze.py` (see its `--help` / header for the column map `COLMAP`) produces, in `workdir`:
- `analysis_results.json` — all aggregates (meta, top50, atc1/atc2/atc3_top/atc4_top, dept_top,
  dept_dom, susp_mismatch, susp_concentration, quality).
- `figs/*.png` — Top15 drugs, spend Pareto, ATC1 distribution, Top15 departments.
It also prints a short digest. Adjust `COLMAP` at the top if the user's column names differ.

### Step 4 — Build the Word report
```
(venv)/Scripts/python.exe scripts/build_docx.py (analysis_results.json) (output.docx)
```
`build_docx.py` reads the JSON and figures and writes a layered report:
1. 标题 + 数据来源/时间/粒度 行
2. 一、数据概况与质量（概况三线表）
3. 二、总体药品使用金额分析（Top50 三线表 + 帕累托图 + 合理性分析）
4. 三、ATC 分类分析（ATC1 全部22类、ATC2 前30 + 图）
5. 四、科室药品使用分析（科室前30、专科-药品匹配存疑、单药超过30% 高度集中 + 图 + 小结）
6. 附录：ATC3/4 级前30；方法学声明

Tables are rendered as three-line tables via `three_line_table()` (top rule, header-bottom rule,
bottom rule; no vertical/inner borders). CJK fonts are set to 宋体 (body) / 黑体 (headings).

### Step 5 — Present & iterate
Call `present_files` with the `.docx`. If the user wants a different month, re-run Steps 3–4 with the
new file; if they want extra sections (e.g., DUI/ABC/排序比), extend `analyze.py` and the report
builder, referencing `drug-use-data-analysis` for the metric definitions.

## Suspicion heuristics (already encoded)
- `susp_mismatch`: a department whose name signals a clearly non-oncology / non-systemic specialty
  (康复/理疗/中医/皮肤/眼科/口腔/耳鼻喉/生殖/妇产/保健/营养/心理/精神…) but whose #1 drug by spend
  is 抗肿瘤药及免疫调节剂. Present these as "需药师核实", and annotate clinically-plausible cases
  (e.g., 阿达木单抗 in 风湿/眼科, 环孢素 in 生殖中心) as NOT irrational.
- `susp_concentration`: departments where a single drug exceeds 30% of the department's spend
  (structural concentration flag). Report count + top examples; do not assert irrationality.

## Resources

### scripts/analyze.py
Aggregation + chart generation. Reads the 11-column pharmacy workbook, writes `analysis_results.json`
and `figs/`. Column names are mapped via `COLMAP` at the top (edit if the schema differs).

### scripts/build_docx.py
Word renderer. Consumes `analysis_results.json` + the `figs/` PNGs; emits a three-line-table report.
Deterministic and reusable; only the input JSON/path change per run.

### references/report_template.md
The canonical report outline, table specs, and the clinical-suspicion annotation rules. Load when you
need to adjust section structure, table columns, or the "需药师核实" wording without re-reading scripts.
