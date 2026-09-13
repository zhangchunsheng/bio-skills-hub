# -*- coding: utf-8 -*-
"""
生成特殊使用级抗菌药物会诊意见Word文档
患者：肝恶性肿瘤合并自发性细菌性腹膜炎
"""

from docx import Document
from docx.shared import Pt, RGBColor, Inches, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

doc = Document()

# ============ 全局样式 ============
style = doc.styles['Normal']
style.font.name = '宋体'
style.font.size = Pt(11)
style.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')

for section in doc.sections:
    section.top_margin = Cm(2.54)
    section.bottom_margin = Cm(2.54)
    section.left_margin = Cm(2.54)
    section.right_margin = Cm(2.54)


def set_cell_bg(cell, color_hex):
    shading = OxmlElement('w:shd')
    shading.set(qn('w:fill'), color_hex)
    shading.set(qn('w:val'), 'clear')
    cell._tc.get_or_add_tcPr().append(shading)


def add_heading_custom(doc, text, level=1, color=None):
    heading = doc.add_heading(text, level=level)
    for run in heading.runs:
        run.font.name = '黑体'
        run.element.rPr.rFonts.set(qn('w:eastAsia'), '黑体')
        if color:
            run.font.color.rgb = color
    return heading


def add_para(doc, text, bold=False, italic=False, font_size=11, alignment=None, color=None, space_after=6, font_name='宋体', left_indent=None):
    p = doc.add_paragraph()
    if alignment:
        p.alignment = alignment
    if left_indent:
        p.paragraph_format.left_indent = Cm(left_indent)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = 1.5
    run = p.add_run(text)
    run.font.name = font_name
    run.font.size = Pt(font_size)
    run.bold = bold
    run.italic = italic
    run.element.rPr.rFonts.set(qn('w:eastAsia'), font_name)
    if color:
        run.font.color.rgb = color
    return p


def add_rich_para(doc, segments, space_after=6, left_indent=None):
    """添加含多格式的段落，segments为(文本, bold, color)元组列表"""
    p = doc.add_paragraph()
    if left_indent:
        p.paragraph_format.left_indent = Cm(left_indent)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = 1.5
    for text, bold, color in segments:
        run = p.add_run(text)
        run.font.name = '宋体'
        run.font.size = Pt(11)
        run.bold = bold
        run.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
        if color:
            run.font.color.rgb = color
    return p


def add_bullet(doc, text, bold_prefix=None, level=0):
    p = doc.add_paragraph(style='List Bullet')
    p.paragraph_format.left_indent = Cm(1.27 + level * 0.85)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.line_spacing = 1.5
    if bold_prefix:
        run_b = p.add_run(bold_prefix)
        run_b.bold = True
        run_b.font.name = '宋体'
        run_b.font.size = Pt(11)
        run_b.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
    run = p.add_run(text)
    run.font.name = '宋体'
    run.font.size = Pt(11)
    run.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
    return p


# ============ 标题 ============
title = doc.add_paragraph()
title.alignment = WD_ALIGN_PARAGRAPH.CENTER
title.paragraph_format.space_before = Pt(10)
title.paragraph_format.space_after = Pt(6)
run = title.add_run('特殊使用级抗菌药物会诊意见')
run.font.name = '黑体'
run.font.size = Pt(20)
run.font.color.rgb = RGBColor(0x1F, 0x4E, 0x79)
run.element.rPr.rFonts.set(qn('w:eastAsia'), '黑体')
run.bold = True

# 会诊信息表
info_table = doc.add_table(rows=4, cols=2)
info_table.alignment = WD_TABLE_ALIGNMENT.CENTER
info_table.style = 'Table Grid'
info_data = [
    ('会诊目的', '肝恶性肿瘤合并自发性细菌性腹膜炎（SBP），头孢曲松+替硝唑经验治疗3天无效，申请升级使用美罗培南'),
    ('会诊意见', '同意使用美罗培南'),
    ('会诊日期', '2026年08月12日'),
    ('会诊药师', 'XXX  副主任药师/主任药师（抗感染专业）'),
]
for i, (k, v) in enumerate(info_data):
    cell_k = info_table.rows[i].cells[0]
    cell_v = info_table.rows[i].cells[1]
    cell_k.text = ''
    cell_v.text = ''
    pk = cell_k.paragraphs[0]
    rk = pk.add_run(k)
    rk.bold = True
    rk.font.name = '黑体'
    rk.font.size = Pt(10)
    rk.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
    rk.element.rPr.rFonts.set(qn('w:eastAsia'), '黑体')
    set_cell_bg(cell_k, '1F4E79')
    pv = cell_v.paragraphs[0]
    rv = pv.add_run(v)
    rv.font.name = '宋体'
    rv.font.size = Pt(10)
    rv.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
    if k == '会诊意见':
        rv.bold = True
        rv.font.color.rgb = RGBColor(0xC0, 0x00, 0x00)

info_table.columns[0].width = Cm(3.5)
info_table.columns[1].width = Cm(13)

doc.add_paragraph()

# ============================================================
# 一、病例摘要与分析
# ============================================================
add_heading_custom(doc, '一、病例摘要与分析', level=2, color=RGBColor(0x1F, 0x4E, 0x79))

add_para(doc, '患者因"肝恶性肿瘤综合治疗后5月余，腹痛1天"入院。既往于2026年2月确诊"原发性肝细胞癌伴肝内、腹腔、双肺多处转移（CNLC IIIB期）"，先后行介入栓塞、化疗、放疗及口服靶向药物治疗，目前肿瘤负荷大、一般状况差。', space_after=6)

add_para(doc, '入院体查：腹部压痛、反跳痛，引流液浑浊，引流管相关腹腔感染可能性大，不排除胆道感染。自发性细菌性腹膜炎、肝损害、麻痹性肠梗阻诊断明确。', space_after=6)

add_para(doc, '关键检验结果：', bold=True, space_after=4)

lab_table = doc.add_table(rows=1, cols=3)
lab_table.style = 'Table Grid'
lab_table.alignment = WD_TABLE_ALIGNMENT.CENTER
lab_hdr = lab_table.rows[0].cells
lab_headers = ['检验项目', '结果', '临床意义']
for i, h in enumerate(lab_headers):
    lab_hdr[i].text = ''
    p = lab_hdr[i].paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(h)
    run.bold = True
    run.font.name = '黑体'
    run.font.size = Pt(10)
    run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
    run.element.rPr.rFonts.set(qn('w:eastAsia'), '黑体')
    set_cell_bg(lab_hdr[i], '1F4E79')

lab_data = [
    ('血WBC', '16.5×10⁹/L ↑，NEU% 93%', '显著炎症反应'),
    ('PCT', '2.45 ng/mL ↑', '细菌感染明确'),
    ('腹水WBC', '13667×10⁶/L ↑↑（多核96%）', 'SBP经典阈值（>250/mm³），重度感染'),
    ('腹水李凡他试验', '阳性(+)', '渗出液'),
    ('腹水GLU', '0.30 mmol/L ↓↓', '细菌大量消耗，高度提示细菌性腹膜炎'),
    ('腹水LDH', '2094 U/L ↑↑', '感染/肿瘤性积液'),
    ('AST', '66.7 U/L ↑', '肝细胞损伤'),
    ('TBIL', '51.54 μmol/L ↑（DBIL 37.35）', '胆汁淤积为主'),
    ('ALP', '166.8 U/L ↑', '胆道梗阻/浸润'),
    ('ALB', '31.3 g/L ↓', '低蛋白血症'),
    ('Cr', '61.9 μmol/L', '肾功能正常'),
    ('Na⁺/Cl⁻', '131.2/96.90 mmol/L ↓', '轻度电解质紊乱'),
]
for row_data in lab_data:
    row = lab_table.add_row()
    for i, cell_text in enumerate(row_data):
        cell = row.cells[i]
        cell.text = ''
        p = cell.paragraphs[0]
        if i == 0:
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        run = p.add_run(cell_text)
        run.font.name = '宋体'
        run.font.size = Pt(9)
        run.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')

add_para(doc, '', space_after=4)
add_para(doc, '既往抗感染方案：头孢曲松2g ivd qd ×3天 + 替硝唑0.4g ivd qd ×3天，疗效评估无效（感染征象持续，腹水实验室检查结果支持活动性感染）。', space_after=6)

# ============================================================
# 二、抗感染治疗分析
# ============================================================
add_heading_custom(doc, '二、抗感染治疗分析', level=2, color=RGBColor(0x1F, 0x4E, 0x79))

add_heading_custom(doc, '（一）用药指征评估', level=3)
add_rich_para(doc, [('同意升级至美罗培南，使用指征充分：', True, RGBColor(0xC0, 0x00, 0x00))])

add_numbered_list = [
    'SBP诊断明确：腹水PMN>250/mm³是诊断金标准，本例腹水WBC达13667×10⁶/L（多核96%），结合腹水李凡他(+)、GLU极低(0.30)、LDH显著升高(2094)，SBP诊断无疑；',
    '重症感染征象：发热、WBC显著升高、PCT升高、麻痹性肠梗阻；',
    '多重耐药菌感染高危因素：长期住院、多次介入操作史、引流管留置、1月前输血史、晚期肿瘤长期消耗低蛋白血症（免疫低下）、既往已用三代头孢+硝基咪唑暴露；',
    '经验治疗失败：规范三代头孢+抗厌氧菌治疗3天，临床无改善；',
    '复杂感染背景：不能排除胆道感染（ALP/TBIL升高）、引流管相关感染、医院获得性感染。',
]
for item in add_numbered_list:
    p = doc.add_paragraph(style='List Number')
    p.paragraph_format.left_indent = Cm(1.27)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.line_spacing = 1.5
    run = p.add_run(item)
    run.font.name = '宋体'
    run.font.size = Pt(11)
    run.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')

add_heading_custom(doc, '（二）病原学分析', level=3)
add_para(doc, '基于感染部位及多重耐药菌风险，主要考虑：', space_after=4)

path_table = doc.add_table(rows=1, cols=3)
path_table.style = 'Table Grid'
path_table.alignment = WD_TABLE_ALIGNMENT.CENTER
path_hdr = path_table.rows[0].cells
path_headers = ['病原类型', '可能性', '依据']
for i, h in enumerate(path_headers):
    path_hdr[i].text = ''
    p = path_hdr[i].paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(h)
    run.bold = True
    run.font.name = '黑体'
    run.font.size = Pt(10)
    run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
    run.element.rPr.rFonts.set(qn('w:eastAsia'), '黑体')
    set_cell_bg(path_hdr[i], '1F4E79')

path_data = [
    ('产ESBLs肠杆菌（大肠埃希菌、肺炎克雷伯菌）', '高', 'SBP最常见病原，三代头孢治疗失败高度提示'),
    ('耐药革兰阴性菌（CRKP、CRPA、CRAB）', '中-高', '长期住院、引流管、抗菌药物暴露'),
    ('肠球菌（含VRE）', '中', '腹腔感染常见，胆道感染不能排除'),
    ('MRSA', '中', '长期住院、免疫低下'),
    ('厌氧菌', '已覆盖', '已用替硝唑，但仍进展，需评估覆盖强度'),
    ('真菌（念珠菌）', '待排除', '长期抗菌药物、免疫低下、引流管'),
]
for row_data in path_data:
    row = path_table.add_row()
    for i, cell_text in enumerate(row_data):
        cell = row.cells[i]
        cell.text = ''
        p = cell.paragraphs[0]
        if i == 1:
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(cell_text)
        run.font.name = '宋体'
        run.font.size = Pt(9)
        run.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')

add_para(doc, '', space_after=4)
add_heading_custom(doc, '（三）药物选择循证依据', level=3)
add_para(doc, '美罗培南选择依据：', bold=True, space_after=4)
add_bullet(doc, '抗菌谱广：覆盖G⁺菌、G⁻菌（含ESBLs/AmpC酶的肠杆菌、铜绿假单胞菌）、厌氧菌')
add_bullet(doc, '腹腔感染循证支持：IDSA/SIS复杂腹腔感染指南推荐碳青霉烯类用于高危患者')
add_bullet(doc, 'SBP三代头孢失败后的标准升级方案')
add_bullet(doc, '肝功能不全时无需调整剂量（主要经肾清除）')
add_bullet(doc, '患者肾功能正常，可用足剂量')

add_para(doc, '', space_after=4)
add_para(doc, '参考依据：', bold=True, space_after=2)
refs = [
    '《肝硬化腹水及相关并发症的诊疗指南》. 中华肝脏病杂志, 2017.',
    'IDSA/SIS. Diagnosis and Management of Complicated Intra-abdominal Infection. Clin Infect Dis, 2010.',
    '热病：桑福德抗微生物治疗指南（第50版）.',
    '国家抗微生物治疗指南（第3版）. 人民卫生出版社, 2018.',
    '美罗培南药品说明书.',
]
for ref in refs:
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Cm(1.0)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.line_spacing = 1.3
    run = p.add_run(f'• {ref}')
    run.font.name = '宋体'
    run.font.size = Pt(10)
    run.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')

# ============================================================
# 三、会诊建议
# ============================================================
add_heading_custom(doc, '三、会诊建议（用药方案）', level=2, color=RGBColor(0x1F, 0x4E, 0x79))

# 核心方案表
plan_table = doc.add_table(rows=0, cols=2)
plan_table.style = 'Table Grid'
plan_table.alignment = WD_TABLE_ALIGNMENT.CENTER

plan_items = [
    ('推荐药物', '注射用美罗培南'),
    ('给药方案', '1g q8h 静脉滴注'),
    ('滴注时间', '每次静脉滴注不少于60分钟（条件允许建议延长输注至2-3小时，可提高%fT>MIC，优化β-内酰胺类PK/PD达标率）'),
    ('建议疗程', '7-14天，根据临床反应、腹水复查及培养结果调整；如明确胆道感染可适当延长至14-21天'),
]
for k, v in plan_items:
    row = plan_table.add_row()
    cell_k = row.cells[0]
    cell_v = row.cells[1]
    cell_k.text = ''
    cell_v.text = ''
    pk = cell_k.paragraphs[0]
    rk = pk.add_run(k)
    rk.bold = True
    rk.font.name = '黑体'
    rk.font.size = Pt(10)
    rk.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
    rk.element.rPr.rFonts.set(qn('w:eastAsia'), '黑体')
    set_cell_bg(cell_k, '4472C4')
    pv = cell_v.paragraphs[0]
    rv = pv.add_run(v)
    rv.font.name = '宋体'
    rv.font.size = Pt(10)
    rv.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')

plan_table.columns[0].width = Cm(3.0)
plan_table.columns[1].width = Cm(13.5)

add_para(doc, '', space_after=4)

add_heading_custom(doc, '联合用药方案', level=3)
add_para(doc, '暂不常规联合，但以下情况需评估：', space_after=4)

combo_table = doc.add_table(rows=1, cols=2)
combo_table.style = 'Table Grid'
combo_table.alignment = WD_TABLE_ALIGNMENT.CENTER
combo_hdr = combo_table.rows[0].cells
combo_headers = ['触发条件', '建议联合方案']
for i, h in enumerate(combo_headers):
    combo_hdr[i].text = ''
    p = combo_hdr[i].paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(h)
    run.bold = True
    run.font.name = '黑体'
    run.font.size = Pt(10)
    run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
    run.element.rPr.rFonts.set(qn('w:eastAsia'), '黑体')
    set_cell_bg(combo_hdr[i], '1F4E79')

combo_data = [
    ('48-72h仍无效，腹水培养出MRSA/VRE', '加用万古霉素或替考拉宁'),
    ('真菌感染征象（G/GM阳性、引流液真菌）', '加用棘白菌素类（卡泊芬净50mg qd）'),
    ('培养出CRKP/CRPA', '联合多粘菌素B/E或头孢他啶/阿维巴坦'),
    ('高度怀疑肠球菌感染', '加用利奈唑胺或达托霉素'),
]
for row_data in combo_data:
    row = combo_table.add_row()
    for i, cell_text in enumerate(row_data):
        cell = row.cells[i]
        cell.text = ''
        p = cell.paragraphs[0]
        run = p.add_run(cell_text)
        run.font.name = '宋体'
        run.font.size = Pt(9)
        run.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')

add_para(doc, '', space_after=4)
add_heading_custom(doc, '特殊人群剂量调整', level=3)
add_bullet(doc, 'Cr 61.9 μmol/L，eGFR正常，无需调整', bold_prefix='肾功能：')
add_bullet(doc, '美罗培南不经肝脏代谢，轻中度肝功能不全无需调整；但需注意肝功能监测', bold_prefix='肝功能：')
add_bullet(doc, 'ALB 31.3 g/L ↓，美罗培南蛋白结合率低（约2%），影响小', bold_prefix='低蛋白血症：')
add_bullet(doc, 'Na⁺ 131.2、Cl⁻ 96.90，纠正电解质紊乱', bold_prefix='电解质紊乱：')

add_heading_custom(doc, '降阶梯策略', level=3)
add_bullet(doc, '腹水培养/血培养结果回报后立即评估')
add_bullet(doc, '病原明确且敏感者，降阶梯为敏感窄谱药物（如敏感的三代/四代头孢、β-内酰胺/β-内酰胺酶抑制剂复合制剂）')
add_bullet(doc, '临床稳定、PCT正常、腹水PMN<250/mm³后，可考虑转为口服序贯（根据药敏选择）')

# ============================================================
# 四、用药监护建议
# ============================================================
add_heading_custom(doc, '四、用药监护建议', level=2, color=RGBColor(0x1F, 0x4E, 0x79))

add_heading_custom(doc, '1. 疗效监测', level=3)
eff_table = doc.add_table(rows=1, cols=2)
eff_table.style = 'Table Grid'
eff_table.alignment = WD_TABLE_ALIGNMENT.CENTER
eff_hdr = eff_table.rows[0].cells
eff_headers = ['监测内容', '频次/时点']
for i, h in enumerate(eff_headers):
    eff_hdr[i].text = ''
    p = eff_hdr[i].paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(h)
    run.bold = True
    run.font.name = '黑体'
    run.font.size = Pt(10)
    run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
    run.element.rPr.rFonts.set(qn('w:eastAsia'), '黑体')
    set_cell_bg(eff_hdr[i], '4472C4')

eff_data = [
    ('体温、症状体征', '每日'),
    ('血常规、CRP、PCT', 'q48h'),
    ('腹水常规、生化', '3-5天后复查'),
    ('腹水培养、血培养', '体温下降或临床稳定后评估'),
    ('肝肾功能、电解质', 'q72h'),
    ('腹部影像', '必要时'),
]
for row_data in eff_data:
    row = eff_table.add_row()
    for i, cell_text in enumerate(row_data):
        cell = row.cells[i]
        cell.text = ''
        p = cell.paragraphs[0]
        run = p.add_run(cell_text)
        run.font.name = '宋体'
        run.font.size = Pt(9)
        run.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')

add_para(doc, '', space_after=4)
add_heading_custom(doc, '2. 不良反应监测', level=3)
add_para(doc, '重点关注：', bold=True, space_after=4)
add_bullet(doc, '原有肝损害基础（Child-Pugh可能B-C级），美罗培南虽不经肝代谢，但重症感染本身可加重肝损伤。监测AST/ALT/TBIL，q72h', bold_prefix='肝功能：')
add_bullet(doc, '美罗培南可抑制维生素K依赖性凝血因子合成，监测PT/INR；本例TBIL升高、ALB降低，凝血风险增加', bold_prefix='凝血功能：')
add_bullet(doc, '肝病基础+低蛋白血症，CNS毒性（癫痫、震颤、意识障碍）风险增加，需每日评估意识状态', bold_prefix='中枢神经系统：')
add_bullet(doc, '监测Cr/BUN，q72h', bold_prefix='肾功能：')
add_bullet(doc, '警惕艰难梭菌感染', bold_prefix='胃肠道反应：')

add_para(doc, '', space_after=2)
add_para(doc, '预警指标：', bold=True, space_after=4)
add_bullet(doc, 'TBIL较基线升高>50%')
add_bullet(doc, 'Cr较基线升高>50%')
add_bullet(doc, 'PLT<50×10⁹/L 或 INR>1.5')
add_bullet(doc, '出现精神症状/抽搐')

add_heading_custom(doc, '3. TDM建议', level=3)
add_bullet(doc, '重症感染建议TDM，目标谷浓度≥2-4 mg/L（MIC依赖），重症患者可追求100% fT>MIC', bold_prefix='美罗培南：')
add_bullet(doc, '第3剂给药前30min采血测谷浓度', bold_prefix='采样时间：')
add_bullet(doc, '首次监测后根据结果调整剂量', bold_prefix='调整：')

add_heading_custom(doc, '4. 药物相互作用', level=3)
add_rich_para(doc, [('丙戊酸钠：', True, RGBColor(0xC0, 0x00, 0x00)), ('绝对禁忌——美罗培南可显著降低丙戊酸钠血药浓度（降幅可达60-100%），如患者使用丙戊酸钠需立即换药', False, None)])
add_bullet(doc, '不建议与其他药物配伍，单独通路输注')
add_bullet(doc, '关注其他合并用药（抗肿瘤靶向药、肝毒性药物）的相互作用')

add_heading_custom(doc, '5. 特殊注意事项', level=3)
add_bullet(doc, '建议立即送检：腹水培养+药敏、血培养（必要时）、腹水mNGS（若常规培养阴性），为降阶梯提供依据')
add_bullet(doc, '引流管管理：评估引流管必要性，避免长期留置成为感染源')
add_bullet(doc, '营养支持：低蛋白血症（ALB 31.3）需加强营养')
add_bullet(doc, '纠正电解质紊乱')
add_bullet(doc, '关注肝硬化基础下的肝性脑病风险')

# ============================================================
# 五、核心建议摘要（突出显示）
# ============================================================
add_para(doc, '', space_after=6)

# 用表格做核心建议框
core_table = doc.add_table(rows=1, cols=1)
core_table.alignment = WD_TABLE_ALIGNMENT.CENTER
core_cell = core_table.rows[0].cells[0]
core_cell.text = ''
set_cell_bg(core_cell, 'FFF2CC')

# 边框
tcPr = core_cell._tc.get_or_add_tcPr()
tcBorders = OxmlElement('w:tcBorders')
for border_name in ['top', 'left', 'bottom', 'right']:
    border = OxmlElement(f'w:{border_name}')
    border.set(qn('w:val'), 'single')
    border.set(qn('w:sz'), '12')
    border.set(qn('w:color'), 'BF8F00')
    tcBorders.append(border)
tcPr.append(tcBorders)

p_title = core_cell.paragraphs[0]
p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p_title.add_run('⚑ 核心建议摘要（Key Recommendations）')
run.font.name = '黑体'
run.font.size = Pt(13)
run.font.color.rgb = RGBColor(0xBF, 0x8F, 0x00)
run.bold = True
run.element.rPr.rFonts.set(qn('w:eastAsia'), '黑体')

p1 = core_cell.add_paragraph()
p1.paragraph_format.space_before = Pt(6)
p1.paragraph_format.line_spacing = 1.5
run_b = p1.add_run('建议：')
run_b.bold = True
run_b.font.name = '宋体'
run_b.font.size = Pt(11)
run_b.font.color.rgb = RGBColor(0xC0, 0x00, 0x00)
run_b.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
run = p1.add_run('停用头孢曲松+替硝唑，升级为美罗培南 1g q8h ivgtt（每次输注≥60分钟），疗程7-14天。')
run.font.name = '宋体'
run.font.size = Pt(11)
run.bold = True
run.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')

p2 = core_cell.add_paragraph()
p2.paragraph_format.line_spacing = 1.5
run_b = p2.add_run('理由：')
run_b.bold = True
run_b.font.name = '宋体'
run_b.font.size = Pt(11)
run_b.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
run = p2.add_run('①SBP诊断明确（腹水PMN 96%、WBC 13667×10⁶/L、李凡他+、GLU极低）；②医院获得性感染高危因素（引流管、长期住院、免疫低下、既往抗菌药物暴露）；③三代头孢+硝基咪唑经验治疗3天无效，需覆盖产ESBLs等多重耐药菌。')
run.font.name = '宋体'
run.font.size = Pt(11)
run.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')

p3 = core_cell.add_paragraph()
p3.paragraph_format.line_spacing = 1.5
run_b = p3.add_run('监护：')
run_b.bold = True
run_b.font.name = '宋体'
run_b.font.size = Pt(11)
run_b.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
run = p3.add_run('q48h复查PCT/血常规，3-5d复查腹水；监测肝肾功能、凝血功能、CNS反应；第3剂前TDM监测美罗培南谷浓度；腹水培养/mNGS结果回报后及时降阶梯。')
run.font.name = '宋体'
run.font.size = Pt(11)
run.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')

# ============================================================
# 签名区
# ============================================================
add_para(doc, '', space_after=12)

sign_table = doc.add_table(rows=2, cols=2)
sign_table.alignment = WD_TABLE_ALIGNMENT.CENTER
sign_table.style = 'Table Grid'
sign_data = [
    ('会诊药师', 'XXX'),
    ('职称', '副主任药师 / 主任药师（抗感染专业）'),
]
for i, (k, v) in enumerate(sign_data):
    cell_k = sign_table.rows[i].cells[0]
    cell_v = sign_table.rows[i].cells[1]
    cell_k.text = ''
    cell_v.text = ''
    pk = cell_k.paragraphs[0]
    pk.alignment = WD_ALIGN_PARAGRAPH.CENTER
    rk = pk.add_run(k)
    rk.bold = True
    rk.font.name = '黑体'
    rk.font.size = Pt(10)
    rk.element.rPr.rFonts.set(qn('w:eastAsia'), '黑体')
    set_cell_bg(cell_k, 'D9E2F3')
    pv = cell_v.paragraphs[0]
    rv = pv.add_run(v)
    rv.font.name = '宋体'
    rv.font.size = Pt(10)
    rv.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')

sign_table.columns[0].width = Cm(4.0)
sign_table.columns[1].width = Cm(12.5)

add_para(doc, '', space_after=6)
date_p = doc.add_paragraph()
date_p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
run = date_p.add_run('会诊日期：2026年08月12日')
run.font.name = '宋体'
run.font.size = Pt(11)
run.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')

# 结尾说明
add_para(doc, '', space_after=4)
note = doc.add_paragraph()
note.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = note.add_run('本会诊意见供临床参考，具体用药请结合患者实际情况并遵循本院抗菌药物管理规定。')
run.font.name = '楷体'
run.font.size = Pt(9)
run.font.italic = True
run.font.color.rgb = RGBColor(0xA0, 0xA0, 0xA0)
run.element.rPr.rFonts.set(qn('w:eastAsia'), '楷体')

# 保存
output_path = r'C:\Users\Administrator\WorkBuddy\会诊\会诊意见_肝恶性肿瘤合并自发性细菌性腹膜炎_美罗培南.docx'
doc.save(output_path)
print(f'文档已保存：{output_path}')
