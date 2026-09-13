---
name: excel-intelligent-processing-architecture
description: Guide token-efficient, script-first Excel/CSV analysis workflows with ETL-quality reusable scripts. Use when Codex needs to process spreadsheets, normalize merged-cell or multi-header Excel files into standard tables, analyze CSV/XLS/XLSX data, support multi-file or multi-sheet joins, choose between openpyxl/pandas/polars/DuckDB/sqlglot, avoid sending raw large data to the LLM, validate SQL results, generate scheduler-friendly analysis scripts, or design an Excel data-processing workflow or skill.
---

# Excel Intelligent Processing Architecture

## Purpose

Use this skill to route Excel/CSV work through a reliable architecture instead of letting the LLM read raw spreadsheets directly. Keep the skill at workflow level: inspect, standardize, analyze with deterministic tools, validate, then let the LLM explain results.

For implementation details, edge cases, and expanded design notes, read `references/full-design.md` only when needed.

## Core Architecture

```text
Excel/CSV input
  -> file inspection
  -> non-standard classification
  -> standard-table normalization
  -> optional multi-table relationship profiling
  -> DuckDB registration
  -> data profiling SQL
  -> resolve required business ambiguity
  -> generate an executable analysis script
  -> run the script for the first formal result
  -> validate script output
  -> natural-language explanation
  -> keep the executed script as the reusable Recipe
```

## Tool Roles

- Use `openpyxl` or `xlrd` to inspect Excel structure: sheets, dimensions, merged cells, formulas, hidden rows/columns, candidate headers, and cell ranges.
- Use CSV sniffing and encoding detection for CSV files before loading the full file.
- Use `pandas` for moderate cleaning, reshaping, standardization, and Excel/CSV interoperability.
- Use `polars` for larger columnar processing or performance-sensitive transformations.
- Use `duckdb` for SQL analysis, joins, aggregations, window functions, direct CSV/Parquet querying, and reproducible computation.
- Use `sqlglot` when SQL parsing, validation, templating, or dialect-safe rewriting is needed.
- Use the LLM only for intent understanding, field semantics, analysis planning, SQL drafting, ambiguity resolution, and final explanation.
- Use `openpyxl` or `xlsxwriter` to produce final Excel outputs.

## Classification

Classify each file, sheet, or detected table region before analysis:

- `C: standard table` - one header row, continuous data rows, no merged cells, no mixed summary rows. Register directly into DuckDB.
- `B: light non-standard` - title row, trailing blank rows/columns, tail summary rows, minor type inconsistencies. Clean automatically and continue.
- `A1: complex but normalizable` - merged cells, multi-row headers, grouped headers, vertical category merges, title/notes areas. Normalize first, then continue.
- `A2: not reliably recoverable` - multiple interleaved tables, cells containing multiple embedded records, missing semantics, ambiguous table boundaries. Stop automatic analysis and explain what needs fixing.

Do not reject merged cells or multi-row headers by default. Try to normalize them unless the structure is genuinely ambiguous.

## Standardization Rules

Convert human-formatted spreadsheets into standard tables:

- Fill vertical merged values downward when they represent row categories.
- Fill horizontal merged values across when they represent grouped headers.
- Flatten multi-row headers into one unique header row.
- Remove or separate title rows, notes, subtotals, grand totals, and empty regions.
- Preserve lineage fields when useful: source file, source sheet, source row, and source column.
- Keep field naming in three layers: original name, SQL-safe name, and semantic display name.
- Ensure SQL-safe names are valid identifiers. Do not generate names that are empty, numeric-only, start with a digit, duplicate another field, or depend on lossy ASCII extraction. When transliteration is unavailable or unsafe, prefer stable aliases such as `col_001`, `col_002`, and keep the original display names in the field map.

Never ask the LLM to compute over an unnormalized merged-cell matrix.

## Multi-Table Support

Explicitly support:

- multiple uploaded Excel/CSV files;
- multiple sheets within one workbook;
- multiple detected table regions in one sheet;
- joins between standard tables and normalized tables.

For a workbook with multiple sheets, inspect and classify each sheet independently. Register each analyzable sheet as a separate table, using stable table names and preserving source metadata.

Before generating join SQL, create a relationship profile:

- candidate primary keys;
- candidate foreign keys;
- field-name similarity;
- value overlap;
- uniqueness rate;
- null rate;
- type compatibility;
- expected join cardinality.

Use high-confidence relationships automatically when the user intent is clear. Ask a light natural-language confirmation when multiple join paths, duplicate keys, or ambiguous fields could change the answer.

## SQL and Analysis Rules

Generate SQL from compact context, not raw data. Include only:

- table names and columns;
- field types and semantic names;
- data profile summaries;
- relationship profile summaries;
- cleaning notes;
- user intent;
- constraints such as row limits and read-only execution.

For formal analysis tasks, do not treat ad hoc SQL execution as the final path. Use data profiling and temporary SQL for exploration, then generate a script that contains the selected normalization, query, validation, and output logic. The first user-facing result must come from running that script.

Execute generated SQL inside the script or scripted workflow and validate the result before explaining it. Do not present unexecuted SQL output as fact.

Allow aggregate full-table scans such as `COUNT`, `SUM`, and `GROUP BY`. For detail-row output, add `LIMIT` and avoid returning huge raw result sets.

Run SQL in a read-only sandbox. Disallow mutation, DDL, filesystem access, network access, and unconstrained Cartesian joins.

## Script-First Recipe Layer

Treat Recipe capture as the execution layer for formal analysis, not a decorative follow-up. After data structure insight, normalization planning, relationship profiling, and required ambiguity confirmation are complete, generate an executable script before the first formal execution. The first verified analysis result must be produced by that script, and the same script becomes the reusable Recipe artifact.

Default to landing a script for any formal analysis task. Exceptions are pure structure inspection, unrecoverable structure diagnosis, explicit one-off user requests that do not need reuse, or trivial direct checks such as row counts. If the user mentions repeatability, scheduled runs, reports, automation, batch processing, or reuse, a script is mandatory.

Keep the user-facing reuse artifact simple: provide an executable script plus invocation instructions. The script must accept at least a file path parameter so it can be scheduled by third-party platforms. It must run without hidden interactive prompts by default.

Internally, a Recipe should still capture the business operation, not only the final SQL string:

- user intent in natural language;
- input shape requirements, such as required table roles and field roles;
- normalization assumptions, including header flattening, merged-cell filling, and removed summary rows;
- table roles, such as fact table, dimension table, lookup table, or calendar table;
- field roles, such as time, metric, dimension, join key, filter, and display field;
- join plan, including join type, keys, cardinality expectation, and unmatched-row handling;
- metric definitions and filters;
- query plan or SQL template;
- result validation rules;
- explanation template or interpretation type;
- output format, such as table, Excel report, chart, or Markdown summary;
- provenance, including original file profile, generated SQL, and cleaning log references.

Prefer structured Recipe data over string-only SQL replacement. Use SQL AST parsing or a structured query plan when possible; raw SQL should be kept for audit and debugging.

The script should include:

- a runnable script, such as `python analyze_inventory.py <file_path>`;
- required parameters, especially input file path;
- optional parameters, such as sheet name, output directory, and output format;
- deterministic loading, normalization, relationship matching, SQL or dataframe analysis, validation, and output steps;
- generated outputs, such as CSV, JSON, XLSX, or Markdown;
- scheduler-friendly exit behavior: exit code `0` on success, non-zero on failure, and clear stderr messages;
- enough comments or metadata to identify metric definitions, join assumptions, and cleaning decisions.

Generated scripts must meet ETL job quality standards:

- separate extract, transform, validate, load/output, and report steps in functions or clear blocks;
- use CLI parameters instead of hard-coded input paths, sheet names, output paths, or business dates;
- write run artifacts to a run directory, including profiles, field maps, cleaning logs, SQL, validation results, and outputs;
- make reruns deterministic and safe: do not mutate source files, overwrite only explicit output paths, and avoid hidden state;
- fail fast on missing required columns, incompatible types, ambiguous joins, and validation breaches;
- produce machine-readable outputs and logs, such as JSON validation summaries and CSV/XLSX result tables;
- keep dependencies minimal and check optional dependencies before use.

Generate the script only after:

- table shapes, candidate headers, and field mappings are known;
- normalization assumptions are explicit enough to encode;
- join behavior is understood when multiple tables are involved;
- any ambiguous metric or join choice has been resolved.

Accept the script as the reusable Recipe only after it executes successfully, the result passes validation, and the user-facing answer is coherent.

When reusing a Recipe:

- inspect and classify the new file again;
- normalize tables before matching roles;
- match required table roles and field roles against the new data profile;
- rebuild joins from relationship profiles or confirmed keys;
- validate metric compatibility and date grain;
- execute the Recipe script or regenerate it from the structured Recipe when the input shape changed;
- compare validation checks against the original Recipe expectations.

Ask for light confirmation when Recipe reuse is ambiguous, such as multiple candidate metrics, multiple time fields, missing required roles, or a join that could double-count.

Mark a Recipe as not applicable when required tables, fields, or relationships are missing. Do not force a template onto incompatible data.

## Ambiguity Rules

Default to automation, but ask for confirmation when:

- the metric definition is ambiguous, such as growth rate, active, retention, profit, or conversion;
- several columns could match the user intent;
- several join keys or join paths are plausible;
- join cardinality may create double counting;
- the requested output is likely to be a huge detail table.

Confirm business meaning, not SQL syntax. Keep SQL hidden from ordinary users unless they ask for technical details.

## Validation Checklist

Before final output, verify:

- normalized column names are unique and non-empty;
- row-count changes from cleaning are explainable;
- field types are correct enough for the requested analysis;
- the generated script executed successfully for formal analysis tasks;
- the generated script is parameterized, rerunnable, and has no hard-coded user-local paths except documented defaults;
- ETL validation artifacts were written, including row-count checks, schema checks, and join checks when relevant;
- generated SQL inside the script executed successfully when SQL is used;
- empty results are explained;
- joins did not unexpectedly multiply rows;
- unmatched join rows are counted when relevant;
- aggregates are not double-counting many-to-many relationships;
- result size is within limits;
- final explanation is based only on computed results.

## Token Discipline

Do not send full spreadsheets or large CSV text to the LLM. Prefer:

- file and sheet summaries;
- candidate header rows;
- field names and types;
- sample rows capped to the minimum needed;
- representative values per column;
- data profiles;
- relationship profiles;
- computed result tables;
- anomaly samples.

If more detail is needed, create intermediate files and refer to them by path rather than loading everything into context.

## Failure and Fallback

Use staged fallback:

- If structure is unclear, output a structure report and ask for the smallest necessary clarification.
- If DuckDB is missing from the runtime, try to install or enable DuckDB for the active environment before falling back.
- If DuckDB installation or import fails, record the failure and continue with pandas or polars as a true fallback.
- If DuckDB is available but registration fails, try pandas or polars loading and normalization.
- If SQL fails, repair it with the error message, table schema, and constraints; cap repair attempts.
- If DuckDB lacks resources, narrow the query, chunk the data, or switch to polars/pandas.
- If the requested analysis cannot be performed safely, explain the limitation in natural language.

Record cleaning logs, generated SQL, relationship assumptions, retries, and fallback decisions for auditability.

## Deliverable Shape

For analysis tasks, return:

- concise natural-language answer;
- result table or output file;
- key notes about filters, cleaning, joins, unmatched rows, and truncation;
- for formal analysis tasks, the executed script path and a short command-line usage example for schedulers, unless the task is explicitly one of the script exceptions.

For architecture or implementation tasks, use this skill as the high-level design guide and read `references/full-design.md` only when detailed module design or configuration is required.
