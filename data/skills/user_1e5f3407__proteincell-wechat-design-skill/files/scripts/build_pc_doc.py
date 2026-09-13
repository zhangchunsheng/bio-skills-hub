# -*- coding: utf-8 -*-
"""
build_pc_doc.py — 从 JSON 配置生成 Protein & Cell 公众号论文推介 docx

生成标准 P&C 栏目排版：红底栏目标题、海军蓝小标题、正文缩进、图示居中图，
以及可选的「作者简介」左图右文表格。生成后交给 pc_push.py 推送即可。

配置 JSON 示例：
{
  "title": "T细胞衔接器设计：活性与安全性的权衡",
  "sections": [
    {"type":"section","text":"今日推荐"},
    {"type":"body","text":"2026年6月4日，来自浙江大学药学院的研究团队在 Protein & Cell 发表了题为……"},
    {"type":"section","text":"文章背景"},
    {"type":"body","text":"T细胞衔接器（TCEs）是一类新兴的免疫治疗药物……"},
    {"type":"section","text":"文章要点"},
    {"type":"subhead","text":"关键科学发现"},
    {"type":"num","text":"T细胞端优化：……"},
    {"type":"section","text":"临床转化与药物研发意义"},
    {"type":"num","text":"安全性优化：……"},
    {"type":"section","text":"图示"},
    {"type":"image","path":"GA.png","caption":"本图展示了T细胞衔接器设计中活性与安全性的权衡。"},
    {"type":"section","text":"作者简介"},
    {"type":"author","name":"周展（Zhan Zhou，通讯作者）","affil":"浙江大学药学院",
     "fields":"研究方向：T细胞衔接器与肿瘤免疫治疗","photo":"周展.jpg"},
    {"type":"section","text":"期刊简介"},
    {"type":"body","text":"英文学术月刊《Protein & Cell》致力于报道生命科学……"}
  ]
}

用法：
  python build_pc_doc.py --config article.json --out article.docx
"""
import os, sys, json, argparse
from docx import Document
from docx.shared import Pt, RGBColor, Inches, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_ALIGN_VERTICAL
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

NAVY = RGBColor(0x1F, 0x38, 0x64)
RED  = RGBColor(0xB9, 0x1C, 0x1C)
BODY = RGBColor(0x3F, 0x3F, 0x3F)


def set_cjk(run, size=11, color=None, bold=False):
    run.font.name = "Microsoft YaHei"
    run.font.size = Pt(size)
    run.font.bold = bold
    if color is not None:
        run.font.color.rgb = color
    rPr = run._element.get_or_add_rPr()
    rFonts = rPr.find(qn('w:rFonts'))
    if rFonts is None:
        rFonts = OxmlElement('w:rFonts'); rPr.append(rFonts)
    rFonts.set(qn('w:eastAsia'), 'Microsoft YaHei')
    rFonts.set(qn('w:ascii'),    'Microsoft YaHei')
    rFonts.set(qn('w:hAnsi'),    'Microsoft YaHei')


def _ea_pPr(par):
    rPr = par._element.get_or_add_pPr()
    rFonts_pPr = rPr.find(qn('w:rPr'))
    if rFonts_pPr is None:
        rFonts_pPr = OxmlElement('w:rPr'); rPr.append(rFonts_pPr)
    eaf = rFonts_pPr.find(qn('w:rFonts'))
    if eaf is None:
        eaf = OxmlElement('w:rFonts'); rFonts_pPr.append(eaf)
    eaf.set(qn('w:eastAsia'), 'Microsoft YaHei')


def add_centered_image(path, width):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    _ea_pPr(p)
    p.paragraph_format.space_after = Pt(8)
    p.add_run().add_picture(path, width=width)
    return p


def add_section(text):
    p = doc.add_paragraph()
    _ea_pPr(p)
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after  = Pt(6)
    pPr = p._element.get_or_add_pPr()
    pBdr = OxmlElement('w:pBdr')
    bottom = OxmlElement('w:bottom')
    bottom.set(qn('w:val'), 'single'); bottom.set(qn('w:sz'), '6')
    bottom.set(qn('w:space'), '2'); bottom.set(qn('w:color'), 'B91C1C')
    pBdr.append(bottom); pPr.append(pBdr)
    r = p.add_run(text)
    set_cjk(r, size=16, color=RED, bold=True)


def add_subhead(text):
    p = doc.add_paragraph()
    _ea_pPr(p)
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after  = Pt(3)
    r = p.add_run(text)
    set_cjk(r, size=11, color=BODY, bold=True)


def add_body(text):
    p = doc.add_paragraph()
    _ea_pPr(p)
    p.paragraph_format.line_spacing = 1.8
    p.paragraph_format.space_after  = Pt(6)
    r = p.add_run(text)
    set_cjk(r, size=11, color=BODY)


def add_num(text):
    p = doc.add_paragraph(style='List Number')
    _ea_pPr(p)
    p.paragraph_format.line_spacing = 1.8
    p.paragraph_format.space_after  = Pt(4)
    r = p.add_run(text)
    set_cjk(r, size=11, color=BODY)


def add_author_block(name, affil, fields, photo):
    table = doc.add_table(rows=1, cols=2)
    table.alignment = WD_ALIGN_PARAGRAPH.CENTER
    table.autofit = False
    table.columns[0].width = Cm(4.2)
    table.columns[1].width = Cm(11.0)
    row = table.rows[0]
    tblPr = table._element.tblPr
    borders = OxmlElement('w:tblBorders')
    for edge in ('top', 'left', 'bottom', 'right', 'insideH', 'insideV'):
        b = OxmlElement(f'w:{edge}')
        b.set(qn('w:val'), 'nil'); borders.append(b)
    tblPr.append(borders)
    # 左：照片
    cell_l = row.cells[0]; cell_l.width = Cm(4.2)
    cell_l.vertical_alignment = WD_ALIGN_VERTICAL.TOP
    p_l = cell_l.paragraphs[0]; p_l.alignment = WD_ALIGN_PARAGRAPH.CENTER; _ea_pPr(p_l)
    if photo and os.path.exists(photo):
        p_l.add_run().add_picture(photo, width=Cm(3.6))
    # 右：姓名 / 单位 / 研究方向
    cell_r = row.cells[1]; cell_r.width = Cm(11.0)
    cell_r.vertical_alignment = WD_ALIGN_VERTICAL.TOP
    p0 = cell_r.paragraphs[0]; _ea_pPr(p0); p0.paragraph_format.space_after = Pt(2)
    r0 = p0.add_run(name or '');
    set_cjk(r0, size=12.5, color=NAVY, bold=True)
    if affil:
        pa = cell_r.add_paragraph(); _ea_pPr(pa); pa.paragraph_format.space_after = Pt(2)
        set_cjk(pa.add_run(affil), size=10.5)
    if fields:
        pf = cell_r.add_paragraph(); _ea_pPr(pf); pf.paragraph_format.space_after = Pt(4)
        set_cjk(pf.add_run(fields), size=10.5, line=1.6)


def build(config, out_path):
    global doc
    doc = Document()
    normal = doc.styles['Normal']
    normal.font.name = "Microsoft YaHei"
    normal.font.size = Pt(11)
    normal.font.color.rgb = BODY
    rPr_def = normal.element.get_or_add_rPr()
    rf_def = rPr_def.find(qn('w:rFonts'))
    if rf_def is None:
        rf_def = OxmlElement('w:rFonts'); rPr_def.append(rf_def)
    rf_def.set(qn('w:eastAsia'), 'Microsoft YaHei')
    rf_def.set(qn('w:ascii'),    'Microsoft YaHei')
    rf_def.set(qn('w:hAnsi'),    'Microsoft YaHei')

    for sec in config.get('sections', []):
        t = sec.get('type')
        if t == 'section':
            add_section(sec['text'])
        elif t == 'subhead':
            add_subhead(sec['text'])
        elif t == 'body':
            add_body(sec['text'])
        elif t == 'num':
            add_num(sec['text'])
        elif t == 'image':
            p = sec.get('path')
            if p and os.path.exists(p):
                add_centered_image(p, width=Inches(5.8))
                if sec.get('caption'):
                    add_body(sec['caption'])
            else:
                print('  [警告] 图片缺失:', p)
        elif t == 'author':
            add_author_block(sec.get('name', ''), sec.get('affil', ''),
                             sec.get('fields', ''), sec.get('photo', ''))
        else:
            print('  [警告] 未知段落类型:', t)

    doc.save(out_path)
    print('OK ->', out_path)


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description='从 JSON 生成 P&C 公众号栏目 docx')
    ap.add_argument('--config', required=True, help='文章配置 JSON 路径')
    ap.add_argument('--out', required=True, help='输出 docx 路径')
    args = ap.parse_args()
    if not os.path.exists(args.config):
        print('ERROR: config 不存在:', args.config); sys.exit(1)
    with open(args.config, 'r', encoding='utf-8') as f:
        cfg = json.load(f)
    build(cfg, args.out)
