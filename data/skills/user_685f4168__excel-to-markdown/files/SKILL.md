---
name: excel-to-markdown
description: Convert general Excel workbooks and delimited spreadsheets into clean Markdown documents, with one output per worksheet, automatic or explicit header detection, merged-cell context preservation, Markdown table or self-contained record layouts, formula handling, sheet selection, and large-file splitting. Use when Codex needs to turn arbitrary .xlsx, .xlsm, .csv, or .tsv data into readable .md files for documentation, review, Git repositories, LLM/RAG ingestion, or knowledge-base import. Also use for legacy .xls files when the runtime has an Excel reader such as xlrd.
---

# Excel to Markdown

Convert a workbook with `scripts/excel_to_markdown.py`. Inspect the workbook first when its structure is ambiguous, then choose a layout that matches the destination.

## Workflow

1. Inspect sheet names, dimensions, merged cells, hidden sheets, title rows, headers, formulas, and representative records.
2. Choose a layout:
   - `table`: Use native Markdown tables for compact, regular data.
   - `records`: Emit one self-contained section per row, separated by `---`. Prefer this for wide sheets, multiline cells, knowledge bases, and RAG.
   - `auto`: Let the script choose `records` for wide or text-heavy data and `table` otherwise.
3. Run the script into a new output directory. Do not overwrite the source workbook.
4. Compare each generated file with its source sheet. Check headers, record counts, merged-cell context, formulas, dates, special characters, and the longest records.
5. Report the output directory, selected layout, included/excluded sheets, warnings, and any unsupported workbook objects such as charts or images.

## Quick Start

Use the bundled Python runtime when available:

```powershell
& '<bundled-python>' '<skill-dir>\scripts\excel_to_markdown.py' '<workbook.xlsx>' --output-dir '<output-dir>'
```

For knowledge-base documents:

```powershell
& '<bundled-python>' '<skill-dir>\scripts\excel_to_markdown.py' '<workbook.xlsx>' --output-dir '<output-dir>' --layout records
```

For a sheet whose header starts on row 3 and spans two rows:

```powershell
& '<bundled-python>' '<skill-dir>\scripts\excel_to_markdown.py' '<workbook.xlsx>' --output-dir '<output-dir>' --sheet 'Data' --header-row 3 --header-rows 2
```

Run `--help` for all options. Useful controls include:

- `--sheet NAME`: Repeat to export selected sheets only.
- `--layout auto|table|records`: Select output structure.
- `--header-row auto|none|N`: Detect, omit, or explicitly locate the first header row.
- `--header-rows N`: Combine multi-row headers.
- `--merged-cells repeat|anchor`: Repeat merged values for record context or keep only anchors.
- `--formulas values|formulas|both`: Export cached values, formulas, or both.
- `--max-rows-per-file N`: Split large sheets without splitting a record.
- `--include-hidden`: Include hidden sheets, rows, and columns.
- `--keep-existing`: Preserve unrelated existing Markdown files in the output directory.

## Conversion Rules

- Default to one Markdown file per visible non-empty worksheet.
- Preserve pre-header title or note rows above the detected header as sheet notes.
- Generate column names when headers are absent or blank, and make duplicate headers unique.
- Repeat merged-cell anchor values by default so each exported record retains its context.
- Convert cell newlines to `<br>` and escape Markdown table pipes.
- Render dates and times in ISO-like form. Retain formulas when cached Excel values are missing.
- Preserve hyperlinks as Markdown links when a cell has a URL target.
- Skip charts, images, comments, macros, conditional formatting, and styling. Warn when the workbook contains charts or images because Markdown cannot represent them automatically.
- Treat each non-empty data row as one record. Do not invent relationships between multiple rows unless the user defines that grouping rule.

## Format Support

- Read `.xlsx`, `.xlsm`, `.xltx`, and `.xltm` with `openpyxl`.
- Read `.csv` and `.tsv` with Python's standard library and encoding/delimiter detection.
- Attempt `.xls` through `pandas`; this requires an installed legacy Excel reader such as `xlrd`. If unavailable, ask the user to resave as `.xlsx` rather than silently changing or losing content.
- Do not claim that cached formula values are recalculated. Excel must have saved them previously; use `--formulas formulas` when exact formula text matters.

## Verification

Before delivery:

- Confirm the number of emitted documents and source sheets.
- Confirm the data-record count printed by the script for every sheet.
- Spot-check the first, middle, and last record of at least one regular sheet.
- Spot-check merged cells, multi-row headers, formula cells, non-ASCII text, pipes, and multiline cells when present.
- Open at least one generated Markdown file and confirm headings, tables, and separators render correctly.
- For `records` output intended for retrieval, check that each section contains enough header/value context to stand alone.
