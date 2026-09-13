# -*- coding: utf-8 -*-
"""
pharmacy-science-pipeline · Word 文档样式与表格辅助（python-docx）
===============================================================
科普文章 / 选题表 的统一样式。在含 python-docx 的 python 中调用：

    from docx_builder import Document, setup_page, h1, h2, h3, body, bullet, numbered, notebox, shade, cell_shade, set_run

要点：
- 微软雅黑；标题深蓝、正文深灰、提醒灰底橙框。
- 自定义底纹/边框需用 OxmlElement（python-docx 原生不含），已封装好。
"""

from docx import Document
from docx.shared import Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

FONT = "微软雅黑"

# 主题色（RGB 元组）
C_TITLE = (14, 42, 71)      # 0E2A47 深蓝
C_SUB   = (20, 56, 92)      # 14385C
C_BLUE  = (42, 111, 219)    # 2A6FDB
C_BODY  = (30, 30, 30)
C_ACCENT = (232, 84, 30)    # E8541E 橙红


def set_run(run, size=11, bold=False, color=(0, 0, 0), font=FONT):
    """设置 run 字体（含中文 eastAsia），避免中文样式失效。"""
    run.font.name = font
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = RGBColor(*color)
    rpr = run._element.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rpr.append(rfonts)
    rfonts.set(qn("w:eastAsia"), font)
    rfonts.set(qn("w:ascii"), font)
    rfonts.set(qn("w:hAnsi"), font)


def shade(par, fill):
    """段落底纹。"""
    ppr = par._p.get_or_add_pPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), fill)
    ppr.append(shd)


def border(par, color="E8541E", sz=14):
    """段落四边边框（提醒框用）。"""
    ppr = par._p.get_or_add_pPr()
    pbdr = OxmlElement("w:pBdr")
    for edge in ("top", "left", "bottom", "right"):
        e = OxmlElement("w:" + edge)
        e.set(qn("w:val"), "single")
        e.set(qn("w:sz"), str(sz))
        e.set(qn("w:space"), "6")
        e.set(qn("w:color"), color)
        pbdr.append(e)
    ppr.append(pbdr)


def cell_shade(cell, fill):
    """单元格底纹（斑马纹/表头用）。"""
    tcpr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), fill)
    tcpr.append(shd)


def setup_page(doc):
    """A4 + 2.2~2.3cm 页边距。"""
    sec = doc.sections[0]
    sec.page_width = Cm(21)
    sec.page_height = Cm(29.7)
    sec.left_margin = Cm(2.2)
    sec.right_margin = Cm(2.2)
    sec.top_margin = Cm(2.3)
    sec.bottom_margin = Cm(2.3)


def _p(doc, text="", size=11, bold=False, color=C_BODY, align=None,
       before=6, after=6, line=1.4):
    p = doc.add_paragraph()
    if align is not None:
        p.alignment = align
    pf = p.paragraph_format
    pf.space_before = Pt(before)
    pf.space_after = Pt(after)
    pf.line_spacing = line
    if text:
        set_run(p.add_run(text), size, bold, color)
    return p


def h1(doc, t):
    return _p(doc, t, size=22, bold=True, color=C_TITLE, before=14, after=8)


def h2(doc, t):
    return _p(doc, t, size=17, bold=True, color=C_SUB, before=10, after=6)


def h3(doc, t):
    return _p(doc, t, size=14, bold=True, color=C_BLUE, before=8, after=4)


def body(doc, t, size=11, color=C_BODY):
    return _p(doc, t, size=size, color=color, before=2, after=4, line=1.5)


def bullet(doc, t, size=11):
    p = doc.add_paragraph(style="List Bullet")
    set_run(p.add_run(t), size)
    return p


def numbered(doc, t, size=11):
    p = doc.add_paragraph(style="List Number")
    set_run(p.add_run(t), size)
    return p


def notebox(doc, title, lines, fill="FDECEA", color="E8541E"):
    """灰底橙框提醒块；title 为标题，lines 为要点列表。"""
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(4)
    set_run(p.add_run("⚠ " + title), 12, True, C_ACCENT)
    pp = doc.add_paragraph()
    pp.paragraph_format.left_indent = Cm(0.4)
    pp.paragraph_format.space_after = Pt(6)
    shade(pp, fill)
    border(pp, color)
    for ln in lines:
        set_run(pp.add_run(ln + "\n"), 10.5, color=(90, 30, 20))
    return pp


def zebra_table(doc, headers, rows, header_fill="0E2A47",
                zebra1="FFFFFF", zebra2="EAF1F8"):
    """通用斑马纹表：headers 表头，rows 为行列表。"""
    n_col = len(headers)
    tbl = doc.add_table(rows=1, cols=n_col)
    tbl.style = "Table Grid"
    tbl.alignment = WD_ALIGN_PARAGRAPH.CENTER
    hdr = tbl.rows[0].cells
    for i, h in enumerate(headers):
        cell_shade(hdr[i], header_fill)
        set_run(hdr[i].paragraphs[0].add_run(h), 11, True, (255, 255, 255))
    for r, row in enumerate(rows):
        cells = tbl.add_row().cells
        fill = zebra1 if r % 2 == 0 else zebra2
        for i, val in enumerate(row):
            cell_shade(cells[i], fill)
            set_run(cells[i].paragraphs[0].add_run(str(val)), 10.5,
                    color=(20, 20, 20))
    return tbl


if __name__ == "__main__":
    # 最小自检：生成一份示例文档确认辅助函数可用
    d = Document()
    setup_page(d)
    h1(d, "示例：药学科普标题")
    body(d, "这是一段正文示例，说明 docx_builder 的样式可用。")
    bullet(d, "要点一")
    bullet(d, "要点二")
    notebox(d, "用药安全红线", ["起红疹立刻停药就医", "剂量由医生个体化决定"])
    zebra_table(d, ["序号", "选题", "理由"],
                [["1", "示例选题", "示例理由"], ["2", "示例选题二", "示例理由二"]])
    out = "docx_builder_demo.docx"
    d.save(out)
    print("docx_builder OK ->", out)
