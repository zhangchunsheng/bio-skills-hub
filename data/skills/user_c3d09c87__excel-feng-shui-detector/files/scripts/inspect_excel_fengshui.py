#!/usr/bin/env python3
import argparse
import json
import posixpath
import re
import zipfile
from collections import Counter
from pathlib import Path
from xml.etree import ElementTree as ET

NS = {
    "m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "pr": "http://schemas.openxmlformats.org/package/2006/relationships",
}
RID = f"{{{NS['r']}}}id"
ERROR_VALUES = {"#NULL!", "#DIV/0!", "#VALUE!", "#REF!", "#NAME?", "#NUM!", "#N/A"}
NUMERIC_TEXT = re.compile(r"^[+-]?(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?%?$")
FULL_COLUMN_REF = re.compile(r"(?<![A-Z0-9_])\$?[A-Z]{1,3}:\$?[A-Z]{1,3}(?![A-Z0-9_])")


def parse_args():
    parser = argparse.ArgumentParser(description="Read-only XLSX feng shui inspector")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output")
    parser.add_argument("--pretty", action="store_true")
    return parser.parse_args()


def read_xml(archive, name):
    try:
        return ET.fromstring(archive.read(name))
    except KeyError:
        return None


def relationships(archive, rels_name, base_part):
    root = read_xml(archive, rels_name)
    result = {}
    if root is None:
        return result
    base_dir = posixpath.dirname(base_part)
    for rel in root.findall("pr:Relationship", NS):
        target = rel.attrib.get("Target", "")
        if target.startswith("/"):
            resolved = target.lstrip("/")
        else:
            resolved = posixpath.normpath(posixpath.join(base_dir, target))
        result[rel.attrib.get("Id")] = {
            "target": resolved,
            "type": rel.attrib.get("Type", ""),
        }
    return result


def shared_strings(archive):
    root = read_xml(archive, "xl/sharedStrings.xml")
    if root is None:
        return []
    values = []
    for item in root.findall("m:si", NS):
        values.append("".join((node.text or "") for node in item.findall(".//m:t", NS)))
    return values


def cell_col(reference):
    match = re.match(r"([A-Z]+)", reference or "")
    if not match:
        return 0
    value = 0
    for char in match.group(1):
        value = value * 26 + ord(char) - 64
    return value


def cell_row(reference):
    match = re.search(r"(\d+)$", reference or "")
    return int(match.group(1)) if match else 0


def range_end(reference):
    endpoint = (reference or "A1").split(":")[-1]
    return cell_row(endpoint), cell_col(endpoint)


def cell_value(cell, strings):
    cell_type = cell.attrib.get("t")
    value_node = cell.find("m:v", NS)
    if cell_type == "inlineStr":
        return "".join((node.text or "") for node in cell.findall(".//m:t", NS))
    raw = value_node.text if value_node is not None and value_node.text is not None else ""
    if cell_type == "s":
        try:
            return strings[int(raw)]
        except (ValueError, IndexError):
            return raw
    return raw


def add_finding(findings, code, severity, sheet, count, evidence, deduction):
    if count <= 0:
        return 0
    findings.append({
        "code": code,
        "severity": severity,
        "sheet": sheet,
        "count": count,
        "evidence": evidence[:12],
        "deduction": deduction,
    })
    return deduction


def inspect_sheet(archive, part, name, state, strings):
    root = read_xml(archive, part)
    if root is None:
        return {"name": name, "state": state, "error": f"Cannot read {part}"}, [], 0
    findings = []
    deduction = 0
    values_by_row = {}
    nonempty_cells = []
    numeric_text_cells = []
    error_cells = []
    full_column_cells = []
    style_ids = set()
    formula_count = 0

    for cell in root.findall(".//m:sheetData/m:row/m:c", NS):
        reference = cell.attrib.get("r", "")
        formula = cell.find("m:f", NS)
        value = cell_value(cell, strings)
        if formula is not None:
            formula_count += 1
            formula_text = formula.text or ""
            if FULL_COLUMN_REF.search(formula_text):
                full_column_cells.append(f"{reference}={formula_text[:100]}")
        if cell.attrib.get("t") == "e" or value in ERROR_VALUES:
            error_cells.append(f"{reference}={value or '#ERROR'}")
        if value != "" or formula is not None:
            nonempty_cells.append(reference)
            row = cell_row(reference)
            col = cell_col(reference)
            values_by_row.setdefault(row, {})[col] = value
        style_id = cell.attrib.get("s")
        if style_id is not None:
            style_ids.add(style_id)
        if cell.attrib.get("t") in {"s", "str", "inlineStr"} and NUMERIC_TEXT.match(str(value).strip()):
            compact = str(value).replace(",", "").replace("%", "").lstrip("+-")
            if not (len(compact) > 1 and compact.startswith("0") and "." not in compact):
                numeric_text_cells.append(reference)

    hidden_rows = [
        row.attrib.get("r", "?")
        for row in root.findall(".//m:sheetData/m:row", NS)
        if row.attrib.get("hidden") in {"1", "true"}
    ]
    hidden_cols = []
    for col in root.findall(".//m:cols/m:col", NS):
        if col.attrib.get("hidden") in {"1", "true"}:
            hidden_cols.append(f"{col.attrib.get('min', '?')}:{col.attrib.get('max', '?')}")
    merged = [
        item.attrib.get("ref", "")
        for item in root.findall(".//m:mergeCells/m:mergeCell", NS)
    ]
    pane = root.find(".//m:sheetViews/m:sheetView/m:pane", NS)
    has_freeze = pane is not None and pane.attrib.get("state") in {"frozen", "frozenSplit"}

    header_row = None
    duplicate_headers = []
    blank_headers = []
    early_rows = {
        row_number: {
            col: value
            for col, value in values_by_row[row_number].items()
            if str(value).strip()
        }
        for row_number in sorted(values_by_row)
        if row_number <= 20
    }
    max_early_width = max((len(values) for values in early_rows.values()), default=0)
    threshold = max(2, int(max_early_width * 0.8 + 0.999))
    for row_number, nonblank in early_rows.items():
        distinct = {str(value).strip().lower() for value in nonblank.values()}
        if len(nonblank) >= threshold and len(distinct) >= 2:
            header_row = row_number
            min_col, max_col = min(nonblank), max(nonblank)
            labels = [
                str(values_by_row[row_number].get(col, "")).strip()
                for col in range(min_col, max_col + 1)
            ]
            blank_headers = [
                f"R{row_number}C{min_col + index}"
                for index, label in enumerate(labels)
                if not label
            ]
            counts = Counter(label.lower() for label in labels if label)
            duplicate_headers = [
                label for label, count in counts.items() if count > 1
            ]
            break

    actual_max_row = max((cell_row(ref) for ref in nonempty_cells), default=0)
    actual_max_col = max((cell_col(ref) for ref in nonempty_cells), default=0)
    dimension = root.find("m:dimension", NS)
    declared_ref = dimension.attrib.get("ref", "") if dimension is not None else ""
    declared_row, declared_col = range_end(declared_ref)
    bloated = (
        actual_max_row > 0
        and declared_row > max(actual_max_row * 10, actual_max_row + 1000)
    ) or (
        actual_max_col > 0
        and declared_col > max(actual_max_col * 10, actual_max_col + 100)
    )

    deduction += add_finding(findings, "formula_error", "high", name, len(error_cells), error_cells, min(36, len(error_cells) * 12))
    deduction += add_finding(findings, "full_column_formula", "medium", name, len(full_column_cells), full_column_cells, min(20, len(full_column_cells) * 5))
    deduction += add_finding(findings, "numeric_text_candidate", "review", name, len(numeric_text_cells), numeric_text_cells, min(20, len(numeric_text_cells)))
    deduction += add_finding(findings, "merged_cells", "review", name, len(merged), merged, min(12, len(merged) * 2))
    hidden_evidence = [f"row:{item}" for item in hidden_rows] + [f"col:{item}" for item in hidden_cols]
    deduction += add_finding(findings, "hidden_structure", "review", name, len(hidden_evidence), hidden_evidence, min(12, len(hidden_evidence) * 2))
    deduction += add_finding(findings, "blank_header", "medium", name, len(blank_headers), blank_headers, min(15, len(blank_headers) * 5))
    deduction += add_finding(findings, "duplicate_header", "medium", name, len(duplicate_headers), duplicate_headers, min(16, len(duplicate_headers) * 8))
    if bloated:
        deduction += add_finding(findings, "used_range_bloat", "high", name, 1, [f"declared={declared_ref}", f"actual≈R{actual_max_row}C{actual_max_col}"], 15)
    if actual_max_row > 100 and not has_freeze:
        deduction += add_finding(findings, "missing_freeze_pane", "low", name, 1, [f"rows={actual_max_row}"], 4)

    summary = {
        "name": name,
        "state": state,
        "part": part,
        "nonempty_cell_count": len(nonempty_cells),
        "actual_max_row": actual_max_row,
        "actual_max_column": actual_max_col,
        "declared_dimension": declared_ref,
        "formula_count": formula_count,
        "merged_range_count": len(merged),
        "hidden_row_count": len(hidden_rows),
        "hidden_column_range_count": len(hidden_cols),
        "style_id_count": len(style_ids),
        "header_row_candidate": header_row,
        "has_freeze_pane": has_freeze,
        "has_auto_filter": root.find(".//m:autoFilter", NS) is not None,
        "table_part_count": len(root.findall(".//m:tableParts/m:tablePart", NS)),
    }
    return summary, findings, deduction


def label(score):
    if score >= 85:
        return "办公室祥瑞"
    if score >= 70:
        return "小煞可化"
    if score >= 50:
        return "暗流涌动"
    return "百鬼夜行"


def main():
    args = parse_args()
    input_path = Path(args.input)
    if input_path.suffix.lower() != ".xlsx":
        raise SystemExit("inspect_excel_fengshui: input must be a .xlsx file")
    try:
        with zipfile.ZipFile(input_path) as archive:
            workbook = read_xml(archive, "xl/workbook.xml")
            if workbook is None:
                raise ValueError("xl/workbook.xml not found")
            rels = relationships(archive, "xl/_rels/workbook.xml.rels", "xl/workbook.xml")
            strings = shared_strings(archive)
            sheets = []
            findings = []
            hidden_sheets = []
            for item in workbook.findall(".//m:sheets/m:sheet", NS):
                name = item.attrib.get("name", "(unnamed)")
                state = item.attrib.get("state", "visible")
                rel = rels.get(item.attrib.get(RID))
                if not rel:
                    continue
                summary, sheet_findings, deduction = inspect_sheet(
                    archive, rel["target"], name, state, strings
                )
                sheets.append(summary)
                findings.extend(sheet_findings)
                if state != "visible":
                    hidden_sheets.append(name)

            styles = read_xml(archive, "xl/styles.xml")
            style_count = 0
            if styles is not None:
                cell_xfs = styles.find("m:cellXfs", NS)
                style_count = int(cell_xfs.attrib.get("count", "0")) if cell_xfs is not None else 0
            if style_count > 50:
                deduction = min(15, 5 + (style_count - 50) // 20)
                add_finding(findings, "style_fragmentation", "medium", "(workbook)", style_count, [f"cellXfs={style_count}"], deduction)
            if hidden_sheets:
                add_finding(findings, "hidden_structure", "review", "(workbook)", len(hidden_sheets), hidden_sheets, min(9, len(hidden_sheets) * 3))
    except (zipfile.BadZipFile, ET.ParseError, ValueError) as exc:
        raise SystemExit(f"inspect_excel_fengshui: {exc}") from exc

    caps = {
        "formula_error": 36,
        "used_range_bloat": 15,
        "full_column_formula": 20,
        "blank_header": 15,
        "duplicate_header": 16,
        "style_fragmentation": 15,
        "missing_freeze_pane": 8,
    }
    code_totals = Counter()
    review_total = 0
    low_total = 0
    for finding in findings:
        if finding["severity"] == "review":
            review_total += finding["deduction"]
        elif finding["severity"] == "low":
            low_total += finding["deduction"]
        else:
            code_totals[finding["code"]] += finding["deduction"]
    confirmed_deduction = sum(
        min(total, caps.get(code, total))
        for code, total in code_totals.items()
    )
    total_deduction = confirmed_deduction + min(20, review_total) + min(8, low_total)
    score = max(0, 100 - min(100, total_deduction))
    priority = {"high": 0, "medium": 1, "review": 2, "low": 3}
    findings.sort(key=lambda item: (priority.get(item["severity"], 9), -item["deduction"], item["sheet"]))
    report = {
        "source": str(input_path),
        "feng_shui_score": score,
        "label": label(score),
        "sheet_count": len(sheets),
        "hidden_sheet_count": len(hidden_sheets),
        "style_count": style_count,
        "sheets": sheets,
        "findings": findings,
        "limitations": [
            "Static OOXML inspection does not recalculate formulas.",
            "Numeric-looking text may be a legitimate identifier and requires manual review.",
            "Visual layout, charts, external links, and business logic require separate inspection.",
            "Macros, binary workbooks, legacy XLS, and password-protected files are not supported.",
        ],
    }
    text = json.dumps(report, ensure_ascii=False, indent=2 if args.pretty else None) + "\n"
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(text, encoding="utf-8")
    else:
        print(text, end="")


if __name__ == "__main__":
    main()
