---
name: excel-overflow-fix
description: Fix Excel cell overflow/truncation issues by auto-detecting cells with content exceeding cell boundaries and applying wrap text + row height adjustments. Only modifies the "审定表" sheet (audit confirmation sheet), leaving all other sheets untouched. Use when processing financial audit working papers (.xlsx/.xls) where cell content is cut off or not fully visible when printing. Triggered by requests involving cell overflow, truncated text, row height adjustment, print formatting, or audit working paper formatting.
slug: excel-overflow-fix101
---

# Excel Overflow Fix

## Overview

This skill fixes cell overflow/truncation issues in Excel audit working papers. It automatically detects cells where content exceeds the visible area (including merged cells), applies text wrapping, and adjusts row heights so all content is fully visible and printable.

**Key guarantees:**
- Only modifies the sheet named "审定表" (audit confirmation sheet)
- Never changes cell content, formulas, or data
- Only adjusts formatting (wrap text + row height)
- All other sheets remain completely untouched

## Workflow

### Step 1: Locate Files

Identify the folder containing the Excel files to process. The skill handles both `.xlsx` and `.xls` files.

### Step 2: Run the Fix Script

Execute the bundled Python script:

```bash
python scripts/fix_overflow.py <input_folder> [output_folder]
```

**Parameters:**
- `input_folder` (required): Path to folder containing Excel files
- `output_folder` (optional): Where to save fixed files. Defaults to `<input_folder>/fixed`

**Example:**
```bash
python scripts/fix_overflow.py "C:\Users\Dell\Desktop\底稿"
```

### Step 3: Review Output

Fixed files are saved with `_fixed` suffix in the output folder. Each file's "审定表" sheet will have:
- Overflow cells wrapped properly
- Row heights adjusted to fit content
- All other sheets identical to original

## How It Works

1. **Scan**: Iterates through all cells in the "审定表" sheet
2. **Detect**: Identifies cells where text length exceeds visible width
3. **Fix**: Sets `wrapText=True` and calculates required row height
4. **Adjust**: Updates row heights (with 200px max limit to prevent extreme cases)

**Overflow detection logic:**
- Skips metadata markers (`---`, `calction`)
- Skips pure numbers and reference codes
- Ignores text shorter than 8 characters
- Calculates needed lines based on column width and font size
- Handles merged cells by distributing height across merged rows

## Requirements

- Python 3.x
- openpyxl library (`pip install openpyxl`)

## Resources

### scripts/
- `fix_overflow.py` - Main script for batch processing Excel files

## Notes

- The script processes ALL `.xlsx` and `.xls` files in the input folder
- Files without a "审定表" sheet are skipped
- Files with no overflow issues are skipped (not saved)
- Maximum row height is capped at 200px to prevent excessive heights
