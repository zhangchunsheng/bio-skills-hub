#!/usr/bin/env python3
"""Render 表 A.1 医疗机构药物重整记录表 from a validated IR JSON to Word .docx.

Strictly follows T/CHAS 20-2-3—2021 附录 A 表 A.1:
- Header rows: 患者姓名 / 年龄 / 性别 / 联系方式 / ID号 / 入院时间 / 转入时间 /
  出院时间 / 转出时间 / 主要诊断 / 过敏史 / 信息来源
- Drug list columns: 药品名称（通用名）/ 用法用量 / 用药原因 / 开始时间 /
  停止时间 / 备注（药物重整建议及理由）
- Notes 1–3 must appear below the table.
- Signature row remains blank.
- Patient-brought drugs have * appended to the name.
- Unconfirmed adjustments are explicitly labelled "建议讨论 / 待医师确认".
- Watermark "DRAFT - PHARMACIST REVIEW / AWAITING PHYSICIAN CONFIRMATION" added.

Usage:
  python render_form_a1.py <input.json> <output.docx>

Exit code:
  0  success
  2  validation failure
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor


# ----------------------------- helpers -----------------------------


def set_cell_borders(cell) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    tc_borders = OxmlElement("w:tcBorders")
    for border_name in ("top", "left", "bottom", "right"):
        border = OxmlElement(f"w:{border_name}")
        border.set(qn("w:val"), "single")
        border.set(qn("w:sz"), "4")  # 0.5pt
        border.set(qn("w:space"), "0")
        border.set(qn("w:color"), "000000")
        tc_borders.append(border)
    tc_pr.append(tc_borders)


def write_cell(cell, text: str, bold: bool = False, size: int = 11, color: RGBColor | None = None) -> None:
    cell.text = ""
    p = cell.paragraphs[0]
    run = p.add_run(str(text))
    run.font.name = "宋体"
    run._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
    run.font.size = Pt(size)
    run.bold = bold
    if color is not None:
        run.font.color.rgb = color


def write_para(doc: Document, text: str, *, bold: bool = False, size: int = 11, italic: bool = False, color: RGBColor | None = None, align=None) -> None:
    p = doc.add_paragraph()
    if align is not None:
        p.alignment = align
    run = p.add_run(text)
    run.font.name = "宋体"
    run._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic
    if color is not None:
        run.font.color.rgb = color


def add_watermark(doc: Document, text: str) -> None:
    """Add a diagonal red watermark to every section using VML shape."""
    for section in doc.sections:
        # Add header
        header = section.header
        para = header.paragraphs[0]
        run = para.add_run()
        run.font.name = "宋体"
        run._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
        run.font.size = Pt(36)
        run.font.color.rgb = RGBColor(0xC0, 0x00, 0x00)

        # Use a simple paragraph-based banner instead of VML for portability
        # The header repeats on every page, giving a banner effect.
        run.text = text


# ----------------------------- rendering -----------------------------


def render_header(doc: Document, encounter: dict[str, Any]) -> None:
    table = doc.add_table(rows=4, cols=4)
    table.style = "Table Grid"
    rows = [
        ["患者姓名", encounter.get("patient_name", ""), "年龄", encounter.get("patient_age", "")],
        ["性别", encounter.get("patient_gender", ""), "联系方式", encounter.get("patient_contact", "")],
        [
            "ID 号",
            encounter.get("patient_id", ""),
            "入院时间 / 转入时间",
            _format_dt(encounter.get("admission_time") or encounter.get("transfer_in_time")),
        ],
        [
            "出院时间 / 转出时间",
            _format_dt(encounter.get("discharge_time") or encounter.get("transfer_out_time")),
            "主要诊断",
            "、".join(encounter.get("primary_diagnosis") or []),
        ],
    ]
    for r, row in enumerate(rows):
        for c, val in enumerate(row):
            cell = table.cell(r, c)
            set_cell_borders(cell)
            write_cell(cell, val, bold=(c % 2 == 0))

    # Allergy + info-source row
    allergies = encounter.get("allergies") or []
    allergy_text = _format_allergies(allergies)
    sources = "、".join(encounter.get("info_sources") or [])

    extra = doc.add_table(rows=2, cols=2)
    extra.style = "Table Grid"
    extra.cell(0, 0).merge(extra.cell(1, 0))
    write_cell(extra.cell(0, 0), "过敏史\n（食物、药物等过敏史，包括过敏表现）", bold=True)
    set_cell_borders(extra.cell(0, 0))
    write_cell(extra.cell(1, 0), "")
    set_cell_borders(extra.cell(1, 0))
    write_cell(extra.cell(0, 1), allergy_text)
    set_cell_borders(extra.cell(0, 1))
    write_cell(extra.cell(1, 1), f"信息来源：{sources or '待核实'}")
    set_cell_borders(extra.cell(1, 1))


def render_drug_table(doc: Document, drug_records: list[dict[str, Any]], outcomes: list[dict[str, Any]]) -> None:
    columns = [
        "药品名称（通用名）",
        "用法用量",
        "用药原因",
        "开始时间",
        "停止时间",
        "备注（药物重整建议及理由）",
    ]
    if not drug_records:
        drug_records = []

    # Standard says list ALL drugs; renderer reserves at least 10 rows.
    rows = max(len(drug_records), 10) + 1
    table = doc.add_table(rows=rows, cols=6)
    table.style = "Table Grid"

    # Header row
    for c, label in enumerate(columns):
        cell = table.cell(0, c)
        set_cell_borders(cell)
        write_cell(cell, label, bold=True)

    # Outcomes indexed by drug_record_id
    outcome_by_drug: dict[str, dict[str, Any]] = {o.get("drug_record_id"): o for o in outcomes}

    for idx, drug in enumerate(drug_records, start=1):
        if idx >= rows:
            break
        generic = drug.get("generic_name") or drug.get("original_name") or "待核实"
        if drug.get("patient_brought") is True:
            generic = f"{generic}*"
        if drug.get("evidence_status") == "missing":
            generic = f"{generic}（待核实）"

        usage = _format_usage(drug)
        reason = drug.get("indication") or "待核实"
        start = drug.get("start_time") or "待核实"
        stop = drug.get("stop_time") or "待核实"
        note = _format_note(drug, outcome_by_drug.get(drug.get("record_id")))

        values = [generic, usage, reason, start, stop, note]
        for c, val in enumerate(values):
            cell = table.cell(idx, c)
            set_cell_borders(cell)
            write_cell(cell, val)


def render_notes(doc: Document) -> None:
    notes = [
        "注 1.列表中应列出患者全部用药，开展重整的药物请注明重整建议及重整理由。",
        "注 2.如有患者自带药品，请在药品名称后加“*”。",
        "注 3.如因转科需要暂停或调整用药，请注明。",
    ]
    for n in notes:
        write_para(doc, n, size=10, italic=True)


def render_signature(doc: Document) -> None:
    write_para(
        doc,
        "药师签字：_______________   医师签字：______________   日期：_________________",
        size=11,
    )


# ----------------------------- formatters -----------------------------


def _format_dt(value: Any) -> str:
    if not value:
        return ""
    if isinstance(value, str):
        return value
    return str(value)


def _format_allergies(allergies: list[dict[str, Any]]) -> str:
    if not allergies:
        return "无明确过敏史"
    parts = []
    for a in allergies:
        sub = a.get("substance", "")
        cat = a.get("category", "")
        mani = a.get("manifestation") or "待核实"
        parts.append(f"[{cat}] {sub}（{mani}）")
    return "；".join(parts)


def _format_usage(drug: dict[str, Any]) -> str:
    """Compose 用法用量 following common Chinese clinical pharmacy conventions:
    剂型 规格 剂量 频次 途径. Avoid duplicating strength within dose when the
    numeric value already appears in dose (e.g. "75 mg" 75 mg qd → keep both
    only if dose does not already contain the strength)."""
    form = (drug.get("dosage_form") or "").strip()
    strength = (drug.get("strength") or "").strip()
    dose = (drug.get("dose") or "").strip()
    freq = (drug.get("frequency") or "").strip()
    route = (drug.get("route") or "").strip()

    # If dose already contains strength, drop the standalone strength
    def _contains(haystack: str, needle: str) -> bool:
        if not haystack or not needle:
            return False
        # crude numeric match: take any digits+unit from strength
        m = re.search(r"\d+(?:\.\d+)?\s*[a-zA-Z%]+", strength)
        return bool(m and m.group(0).lower() in haystack.lower())

    if _contains(dose, strength):
        strength = ""

    parts = [p for p in (form, strength, dose, freq, route) if p]
    if not parts:
        return "待核实"
    return " ".join(parts)


def _format_note(drug: dict[str, Any], outcome: dict[str, Any] | None) -> str:
    notes: list[str] = []
    if outcome:
        role = outcome.get("decided_by_role")
        result = outcome.get("result")
        reason = outcome.get("reason")
        if role == "physician_confirmed":
            notes.append(f"[已确认] {result}：{reason or ''}")
        else:
            notes.append(f"[建议讨论 / 待医师确认] {result}：{reason or ''}")
    if drug.get("evidence_status") in ("ambiguous", "missing"):
        notes.append(f"[证据状态: {drug['evidence_status']}]")
    for q in drug.get("open_questions") or []:
        notes.append(f"[待核实] {q}")
    return " ".join(notes) if notes else ""


# ----------------------------- main -----------------------------


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def render(input_path: Path, output_path: Path) -> None:
    data = load_json(input_path)
    encounter = data.get("encounter") or {}
    drug_records = data.get("drug_records") or []
    outcomes = data.get("reconciliation_outcomes") or []

    doc = Document()
    section = doc.sections[0]
    section.page_height = Cm(29.7)
    section.page_width = Cm(21.0)
    section.top_margin = Cm(2.0)
    section.bottom_margin = Cm(2.0)
    section.left_margin = Cm(2.5)
    section.right_margin = Cm(2.5)

    # Watermark in header
    add_watermark(
        doc,
        "DRAFT - PHARMACIST REVIEW / AWAITING PHYSICIAN CONFIRMATION",
    )

    # Title
    write_para(
        doc,
        "医疗机构药物重整记录表",
        bold=True,
        size=16,
        align=WD_ALIGN_PARAGRAPH.CENTER,
    )
    write_para(
        doc,
        "（依据 T/CHAS 20-2-3—2021 附录 A 表 A.1）",
        size=10,
        italic=True,
        align=WD_ALIGN_PARAGRAPH.CENTER,
    )

    # Prominent "草稿 / 待医师确认" notice
    write_para(
        doc,
        "★ 药师复核草稿 / 待医师确认 ★",
        bold=True,
        size=14,
        color=RGBColor(0xC0, 0x00, 0x00),
        align=WD_ALIGN_PARAGRAPH.CENTER,
    )

    render_header(doc, encounter)
    doc.add_paragraph()
    render_drug_table(doc, drug_records, outcomes)
    doc.add_paragraph()
    render_notes(doc)
    doc.add_paragraph()
    render_signature(doc)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(output_path)


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print(
            "Usage: python render_form_a1.py <input.json> <output.docx>",
            file=sys.stderr,
        )
        return 2
    input_path = Path(argv[1])
    output_path = Path(argv[2])
    if not input_path.exists():
        print(f"Input not found: {input_path}", file=sys.stderr)
        return 2
    try:
        render(input_path, output_path)
    except Exception as e:
        print(f"Render failed: {e}", file=sys.stderr)
        return 2
    print(f"✅ Rendered: {output_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))