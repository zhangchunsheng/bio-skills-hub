---
name: industrial-inspection
description: "Industrial quality inspection data auditing. Automatically reviews all Excel inspection reports in a directory, applying 4 core rules (range exceedance, illegal values, deviation anomalies, judgment contradiction) to detect anomalies. Generates cell-level red-marked reports and summary Excel. Triggers: data audit, quality inspection review, anomaly detection, red-mark report."
agent_created: true
---

# Industrial Inspection - Data Quality Audit

## Overview

Automated row-by-row auditing of industrial quality inspection Excel files.
Generates reports with only problematic cells highlighted in red, plus a summary statistics sheet.

## When to Use

When the user needs to audit industrial quality inspection data, review Excel inspection reports, flag anomalous measurements, or produce red-marked inspection reports.

## Workflow

### 1. Confirm Paths

Confirm with the user:
- **Input directory**: where the inspection Excel files are located
- **Output directory**: where reports will be saved (default: current workspace directory)

### 2. Run Inspection Script

Execute the bundled script:

```bash
python3 SKILL_DIR/scripts/audit.py <input_dir> <output_dir>
```

The script automatically:
- Detects and skips header/title rows in Chinese
- Audits every row against 4 core rules
- Highlights only problematic cells in red (not entire rows)
- Generates per-file inspection reports (no title row, no summary row, no extra columns)
- Generates a summary Excel with overview and per-file statistics

### 3. Present Results

After execution, show the user:
- Number of files reviewed, files with issues, total data rows, anomaly rows, overall pass rate
- For each anomaly: product code, test item, specific problem, and which columns are red-marked
- Paths to the generated report files

## Core Audit Rules

Detailed rules are in `references/rules.md`. Summary:

| Rule | Description | Red-Marked Column |
|------|-------------|-------------------|
| Rule 1 - Range Exceedance | Measured value outside standard/reasonable range | Measured Value |
| Rule 2 - Illegal Value | Negative or zero where not allowed | Measured Value |
| Rule 3 - Deviation Anomaly | Absolute deviation rate exceeds 100% | Deviation Rate |
| Rule 4 - Judgment Contradiction | Anomaly present but marked as "qualified" | Judgment Result |

Standard ranges are taken from the "Standard Requirement" column first; if empty, default reasonable physical ranges are used.

## Column Structure

All inspection files are expected to have 10 columns in this order:
0. Product Code
1. Test Item
2. Test Standard
3. Measured Value
4. Standard Requirement (range)
5. Unit
6. Deviation Rate
7. Judgment Result
8. Test Date
9. Tester

## Resources

### scripts/audit.py
Main audit script. Runs independently with input and output directory arguments.

### references/rules.md
Detailed audit rules with full standard ranges and anomaly judgment logic. Read when rule details are needed.
