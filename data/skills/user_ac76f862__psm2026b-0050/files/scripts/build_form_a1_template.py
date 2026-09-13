#!/usr/bin/env python3
"""Create the form-a1-template.docx asset for the medication-reconciliation-record skill.

Template structure strictly follows T/CHAS 20-2-3—2021 附录 A 表 A.1:
- 表头: 患者姓名 / 年龄 / 性别 / 联系方式 / ID号 / 入院时间 / 转入时间 / 出院时间 / 转出时间 / 主要诊断 / 过敏史 / 信息来源
- 药物列表列名: 药品名称（通用名） / 用法用量 / 用药原因 / 开始时间 / 停止时间 / 备注（药物重整建议及理由）
- 表下注释 3 条
- 签字栏: 药师签字 / 医师签字 / 日期

This template is a *skeleton*: it has empty cells. The actual rendering
fills the cells from validated IR JSON via scripts/render_form_a1.py.
"""

from pathlib import Path

from docx import Document
from docx.enum.table import WD_ALIGN_VERTICAL
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from docx.shared import Cm, Pt


HERE = Path(__file__).resolve().parent
ASSETS_DIR = HERE.parent / "assets"


def set_cell_borders(cell):
    """Add single-line 0.5pt borders to a cell."""
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


def set_cell_text(cell, text, bold=False, size=11):
    cell.text = ""
    p = cell.paragraphs[0]
    run = p.add_run(text)
    run.font.name = "宋体"
    run._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
    run.font.size = Pt(size)
    run.bold = bold


def build_template(out_path: Path) -> None:
    doc = Document()

    # Page setup: A4, margins
    section = doc.sections[0]
    section.page_height = Cm(29.7)
    section.page_width = Cm(21.0)
    section.top_margin = Cm(2.0)
    section.bottom_margin = Cm(2.0)
    section.left_margin = Cm(2.5)
    section.right_margin = Cm(2.5)

    # Title
    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title_run = title.add_run("医疗机构药物重整记录表")
    title_run.bold = True
    title_run.font.name = "黑体"
    title_run._element.rPr.rFonts.set(qn("w:eastAsia"), "黑体")
    title_run.font.size = Pt(16)

    subtitle = doc.add_paragraph()
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    subtitle_run = subtitle.add_run("（依据 T/CHAS 20-2-3—2021 附录 A 表 A.1）")
    subtitle_run.font.name = "宋体"
    subtitle_run._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
    subtitle_run.font.size = Pt(10)
    subtitle_run.italic = True

    doc.add_paragraph()

    # Header table: 4 columns x 4 rows
    header_table = doc.add_table(rows=4, cols=4)
    header_table.style = "Table Grid"
    header_labels = [
        ["患者姓名", "", "年龄", ""],
        ["性别", "", "联系方式", ""],
        ["ID 号", "", "入院时间 / 转入时间", ""],
        ["出院时间 / 转出时间", "", "主要诊断", ""],
    ]
    for r, row in enumerate(header_labels):
        for c, text in enumerate(row):
            cell = header_table.cell(r, c)
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            set_cell_borders(cell)
            set_cell_text(cell, text, bold=(c % 2 == 0))

    # Merge cells for label-value pairs
    for r in range(4):
        header_table.cell(r, 0).merge(header_table.cell(r, 1))
        header_table.cell(r, 2).merge(header_table.cell(r, 3))

    # Allergy + info-source row (single label column, then content)
    extra_table = doc.add_table(rows=2, cols=2)
    extra_table.style = "Table Grid"
    extra_table.cell(0, 0).merge(extra_table.cell(1, 0))
    set_cell_text(extra_table.cell(0, 0), "过敏史\n（食物、药物等过敏史，包括过敏表现）", bold=True)
    extra_table.cell(0, 0).vertical_alignment = WD_ALIGN_VERTICAL.CENTER
    set_cell_borders(extra_table.cell(0, 0))
    set_cell_borders(extra_table.cell(0, 1))
    set_cell_borders(extra_table.cell(1, 1))
    set_cell_text(extra_table.cell(0, 1), "")
    set_cell_text(extra_table.cell(1, 1), "信息来源：□患者/家属  □病历资料  □其他________")

    doc.add_paragraph()

    # Drug list table header
    drug_table = doc.add_table(rows=11, cols=6)
    drug_table.style = "Table Grid"
    columns = [
        "药品名称（通用名）",
        "用法用量",
        "用药原因",
        "开始时间",
        "停止时间",
        "备注（药物重整建议及理由）",
    ]
    for c, label in enumerate(columns):
        cell = drug_table.cell(0, c)
        cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        set_cell_borders(cell)
        set_cell_text(cell, label, bold=True, size=11)
    for r in range(1, 11):
        for c in range(6):
            set_cell_borders(drug_table.cell(r, c))
            set_cell_text(drug_table.cell(r, c), "", size=11)

    doc.add_paragraph()

    # Notes
    notes = [
        "注 1. 列表中应列出患者全部用药，开展重整的药物请注明重整建议及重整理由。",
        "注 2. 如有患者自带药品，请在药品名称后加“*”。",
        "注 3. 如因转科需要暂停或调整用药，请注明。",
    ]
    for note in notes:
        p = doc.add_paragraph()
        run = p.add_run(note)
        run.font.name = "宋体"
        run._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
        run.font.size = Pt(10)
        run.italic = True

    doc.add_paragraph()

    # Signature row
    sig = doc.add_paragraph()
    sig_run = sig.add_run(
        "药师签字：_______________   医师签字：______________   日期：_________________"
    )
    sig_run.font.name = "宋体"
    sig_run._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
    sig_run.font.size = Pt(11)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(out_path)
    print(f"✅ Template saved to: {out_path}")


if __name__ == "__main__":
    build_template(ASSETS_DIR / "form-a1-template.docx")