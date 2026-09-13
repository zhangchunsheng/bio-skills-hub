# -*- coding: utf-8 -*-
"""
生成《特殊使用级抗菌药物临床药师会诊指南与提示词模板》Word文档

用法：
    python generate_consultation_doc.py [输出路径]

    输出路径（可选）：默认输出到当前工作目录下的
    "特殊使用级抗菌药物临床药师会诊指南与提示词模板.docx"
"""

import sys
import os
from docx import Document
from docx.shared import Pt, RGBColor, Inches, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

doc = Document()

# ============ 全局样式设置 ============
style = doc.styles['Normal']
style.font.name = '宋体'
style.font.size = Pt(11)
style.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')

for section in doc.sections:
    section.top_margin = Cm(2.54)
    section.bottom_margin = Cm(2.54)
    section.left_margin = Cm(3.17)
    section.right_margin = Cm(3.17)


def set_cell_background(cell, color_hex):
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


def add_para(doc, text, bold=False, italic=False, font_size=11, alignment=None, color=None, space_after=6, font_name='宋体'):
    p = doc.add_paragraph()
    if alignment:
        p.alignment = alignment
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


def add_bullet(doc, text, level=0, bold_prefix=None):
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


# ============ 封面 ============
title = doc.add_paragraph()
title.alignment = WD_ALIGN_PARAGRAPH.CENTER
title.paragraph_format.space_before = Pt(80)
title.paragraph_format.space_after = Pt(10)
run = title.add_run('特殊使用级抗菌药物\n临床药师会诊指南与提示词模板')
run.font.name = '黑体'
run.font.size = Pt(26)
run.font.color.rgb = RGBColor(0x1F, 0x4E, 0x79)
run.element.rPr.rFonts.set(qn('w:eastAsia'), '黑体')
run.bold = True

subtitle = doc.add_paragraph()
subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
subtitle.paragraph_format.space_after = Pt(40)
run = subtitle.add_run('—— 从法规要求到临床实践，构建可重复使用的会诊工作流')
run.font.name = '楷体'
run.font.size = Pt(14)
run.font.color.rgb = RGBColor(0x59, 0x59, 0x59)
run.element.rPr.rFonts.set(qn('w:eastAsia'), '楷体')

sep = doc.add_paragraph()
sep.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = sep.add_run('━' * 30)
run.font.size = Pt(12)
run.font.color.rgb = RGBColor(0x1F, 0x4E, 0x79)

info = doc.add_paragraph()
info.alignment = WD_ALIGN_PARAGRAPH.CENTER
info.paragraph_format.space_before = Pt(10)
run = info.add_run('适用对象：抗感染专业临床药师 / 药学部门\n编制目的：规范特殊使用级抗菌药物会诊意见书写，提供可重复使用的提示词模板')
run.font.name = '楷体'
run.font.size = Pt(11)
run.font.color.rgb = RGBColor(0x59, 0x59, 0x59)
run.element.rPr.rFonts.set(qn('w:eastAsia'), '楷体')

doc.add_page_break()

# ============ 目录 ============
add_heading_custom(doc, '目  录', level=1, color=RGBColor(0x1F, 0x4E, 0x79))
toc_items = [
    '第一部分  学习内容：特殊使用级抗菌药物会诊基础知识',
    '    一、政策法规依据与资质要求',
    '    二、特殊使用级抗菌药物分类与特征',
    '    三、会诊工作流程',
    '    四、常用循证参考资源',
    '    五、会诊常见临床场景',
    '第二部分  会诊意见书写总结',
    '    一、书写基本原则',
    '    二、书写框架：「为什么用 → 如何用 → 用后注意」',
    '    三、会诊意见质量自评清单',
    '第三部分  可重复使用的会诊提示词模板',
    '    一、提示词使用说明',
    '    二、完整提示词模板',
    '    三、会诊意见输出示例（参考）',
]
for item in toc_items:
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.line_spacing = 1.5
    run = p.add_run(item)
    run.font.name = '宋体'
    run.font.size = Pt(12)
    run.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')

doc.add_page_break()

# ============================================================
# 第一部分：学习内容
# ============================================================
add_heading_custom(doc, '第一部分  学习内容', level=1, color=RGBColor(0x1F, 0x4E, 0x79))
add_para(doc, '特殊使用级抗菌药物临床药师会诊基础知识', bold=True, font_size=14, alignment=WD_ALIGN_PARAGRAPH.CENTER, color=RGBColor(0x1F, 0x4E, 0x79), space_after=12)

add_heading_custom(doc, '一、政策法规依据与资质要求', level=2)
add_para(doc, '（一）核心法规', bold=True, space_after=4)
add_para(doc, '2012年原卫生部颁布《抗菌药物临床应用管理办法》（卫生部令第84号），其中第二十七条明确规定：临床应用特殊使用级抗菌药物应当严格掌握用药指证，经抗菌药物管理工作组指定的专业技术人员会诊同意后，由具有相应处方权医师开具处方。', space_after=6)

add_para(doc, '（二）会诊人员资质要求', bold=True, space_after=4)
add_bullet(doc, '具有抗菌药物临床应用经验的感染性疾病科、呼吸科、重症医学科、微生物检验科、药学部门等技术人员', bold_prefix='人员来源：')
add_bullet(doc, '医师需具有高级专业技术职务任职资格', bold_prefix='医师资质：')
add_bullet(doc, '药师需具有高级专业技术职务任职资格，或具有高级专业技术职务任职资格的抗菌药物专业临床药师', bold_prefix='药师资质：')
add_bullet(doc, '经抗菌药物管理工作组审核认定', bold_prefix='授权方式：')

add_para(doc, '（三）会诊模式', bold=True, space_after=4)
add_para(doc, '一般由医师填写会诊申请单，药师审阅病历资料后提出用药建议，药师的工作性质属于咨询模式（advisory model）。药师提供建议，最终处方权归属具有相应权限的医师。', space_after=6)

# 二、药物分类
add_heading_custom(doc, '二、特殊使用级抗菌药物分类与特征', level=2)
add_para(doc, '特殊使用级抗菌药物通常具有以下特征之一：①具有明显或严重不良反应，不宜随意使用；②需要严格控制使用，避免细菌过快产生耐药；③疗效、安全性方面的临床资料较少；④价格昂贵。', space_after=8)

table = doc.add_table(rows=1, cols=3)
table.style = 'Light Grid Accent 1'
table.alignment = WD_TABLE_ALIGNMENT.CENTER
hdr = table.rows[0].cells
headers = ['药物类别', '代表药物', '主要特点与适用场景']
for i, h in enumerate(headers):
    hdr[i].text = ''
    p = hdr[i].paragraphs[0]
    run = p.add_run(h)
    run.bold = True
    run.font.name = '黑体'
    run.font.size = Pt(10)
    run.element.rPr.rFonts.set(qn('w:eastAsia'), '黑体')
    set_cell_background(hdr[i], '1F4E79')
    for run in p.runs:
        run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

drug_data = [
    ('碳青霉烯类', '美罗培南、亚胺培南/西司他丁、比阿培南、厄他培南', '广谱，覆盖G⁻菌（含产ESBLs/AmpC酶）、G⁺菌、厌氧菌；适用于重症感染、多重耐药G⁻菌感染；厄他培南不覆盖铜绿'),
    ('糖肽类', '万古霉素、替考拉宁', '覆盖G⁺菌含MRSA、MRSE、肠球菌；适用于耐药G⁺菌感染；需注意肾毒性，万古霉素需TDM'),
    ('噁唑烷酮类', '利奈唑胺、特地唑胺', '覆盖G⁺菌含MRSA、VRE；组织穿透性好（肺、CSF）；长期使用需监测血小板和乳酸'),
    ('多肽类', '多粘菌素B、多粘菌素E（黏菌素）', '针对碳青霉烯耐药G⁻菌（CRAB、CRPA、CRE）的最后防线；需注意肾毒性和神经毒性'),
    ('甘氨酰环类', '替加环素', '广谱覆盖G⁺、G⁻（不含铜绿）、厌氧菌及非典型病原；适用于cIAI、cSSTI、HAP/VAP；CRE感染联合用药'),
    ('四代头孢', '头孢吡肟', '广谱覆盖G⁺和G⁻含铜绿假单胞菌；适用于院内获得性感染、中性粒细胞减少伴发热'),
    ('五代头孢', '头孢洛林酯', '覆盖MRSA及常见G⁻菌；适用于cSSTI、CAP'),
    ('新型酶抑制剂复合制剂', '头孢他啶/阿维巴坦、美罗培南/法硼巴坦、亚胺培南/西司他丁/雷利巴坦', '针对产KPC等碳青霉烯酶的CRE；头孢他啶/阿维巴坦对OXA-48也有活性'),
    ('新型抗真菌药', '伏立康唑、卡泊芬净、米卡芬净、艾沙康唑', '侵袭性真菌感染（曲霉、念珠菌等）；伏立康唑需TDM'),
    ('其他', '达托霉素', '覆盖G⁺菌含MRSA、VRE；不可用于肺炎（被肺表面活性物质灭活）；需监测CPK'),
]
for row_data in drug_data:
    row = table.add_row()
    for i, cell_text in enumerate(row_data):
        cell = row.cells[i]
        cell.text = ''
        p = cell.paragraphs[0]
        run = p.add_run(cell_text)
        run.font.name = '宋体'
        run.font.size = Pt(9)
        run.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')

add_para(doc, '', space_after=4)
add_para(doc, '注：各医疗机构应根据本院《抗菌药物分级管理目录》确认具体药品的分级级别，不同医院可能存在差异。', italic=True, font_size=10, color=RGBColor(0x80, 0x80, 0x80))

# 三、会诊流程
add_heading_custom(doc, '三、会诊工作流程', level=2)
add_para(doc, '完整的特殊使用级抗菌药物会诊应包含以下步骤：', space_after=6)
steps = [
    ('第一步：接收会诊申请', '接收主管医师提交的会诊申请单，明确会诊目的和具体问题（如：药物选择、剂量调整、治疗方案优化、不良反应处理等）。'),
    ('第二步：资料收集与评估', '系统查阅电子病历，收集以下信息：\n  · 患者基本信息（年龄、性别、体重、身高）\n  · 诊断与病程记录\n  · 感染相关检验：血常规、炎症标志物（CRP、PCT、IL-6）、肝肾功能、电解质\n  · 病原学检查：培养结果、药敏试验、G/GM试验、mNGS等\n  · 影像学检查结果\n  · 用药史：既往及当前抗菌药物使用情况、疗效评估\n  · 过敏史与不良反应史\n  · 合并用药及药物相互作用风险'),
    ('第三步：床旁评估（必要时）', '对重症、疑难或信息不充分的患者，应走到床旁查看：\n  · 生命体征、意识状态\n  · 感染部位体征（伤口、导管、肺部听诊等）\n  · 引流液/分泌物性状\n  · 与主管医师当面沟通诊疗思路'),
    ('第四步：形成会诊意见', '综合评估后，按照规范格式书写会诊意见，包括用药分析、药物选择、给药方案、监护建议等。'),
    ('第五步：随访与疗效评估', '会诊后跟踪患者治疗反应、复查指标变化，必要时调整方案。降阶梯治疗策略的执行评估。'),
]
for i, (step_title, step_content) in enumerate(steps):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(8)
    p.paragraph_format.line_spacing = 1.5
    run_num = p.add_run(f'{["①","②","③","④","⑤"][i]} {step_title}\n')
    run_num.bold = True
    run_num.font.name = '黑体'
    run_num.font.size = Pt(11)
    run_num.font.color.rgb = RGBColor(0x1F, 0x4E, 0x79)
    run_num.element.rPr.rFonts.set(qn('w:eastAsia'), '黑体')
    run = p.add_run(step_content)
    run.font.name = '宋体'
    run.font.size = Pt(11)
    run.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')

# 四、参考资源
add_heading_custom(doc, '四、常用循证参考资源', level=2)
refs = [
    ('热病（Sanford Guide）', '第50版（2020）/最新版，快速查阅抗感染治疗方案。'),
    ('国家抗微生物治疗指南', '第3版（2018）/最新版，国内权威参考。'),
    ('IDSA指南', '美国感染病学会各专题指南。'),
    ('中华医学会系列指南/共识', '如HAP/VAP指南、腹腔感染指南、抗菌药物指导原则等。'),
    ('相关专科专家共识', '如碳青霉烯类、万古霉素、替加环素临床应用专家共识。'),
    ('CHINET耐药监测网', '中国细菌耐药监测网年度数据。'),
    ('药品说明书', '给药方案、不良反应、禁忌证的法定依据。'),
    ('UpToDate', '循证医学数据库。'),
]
for name, desc in refs:
    p = doc.add_paragraph(style='List Bullet')
    p.paragraph_format.left_indent = Cm(1.27)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.line_spacing = 1.5
    run_b = p.add_run(f'{name}：')
    run_b.bold = True
    run_b.font.name = '宋体'
    run_b.font.size = Pt(11)
    run_b.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
    run = p.add_run(desc)
    run.font.name = '宋体'
    run.font.size = Pt(11)
    run.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')

# 五、临床场景
add_heading_custom(doc, '五、会诊常见临床场景', level=2)
scenarios = [
    ('重症感染初始经验治疗', '脓毒症/脓毒症休克、重症HAP/VAP、重症腹腔感染、中枢神经系统感染等。'),
    ('多重耐药菌（MDRO）感染', '产ESBLs肠杆菌、CRE、CRAB、CRPA、MRSA、VRE等的目标治疗。'),
    ('治疗失败/疗效不佳', '已使用抗菌药物48-72h无改善，需分析原因并调整方案。'),
    ('特殊人群剂量调整', '肾功能不全/CRRT、肝功能不全、老年人、儿童、孕妇、肥胖患者。'),
    ('不良反应处理与方案调整', '抗菌药物相关不良反应的识别与方案调整。'),
    ('联合用药方案优化', '复杂感染联合用药的药物选择与药物相互作用规避。'),
    ('降阶梯治疗策略', '经验转目标、广谱转窄谱、静脉转口服的时机判断。'),
]
for name, desc in scenarios:
    p = doc.add_paragraph(style='List Bullet')
    p.paragraph_format.left_indent = Cm(1.27)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.line_spacing = 1.5
    run_b = p.add_run(f'{name}：')
    run_b.bold = True
    run_b.font.name = '宋体'
    run_b.font.size = Pt(11)
    run_b.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
    run = p.add_run(desc)
    run.font.name = '宋体'
    run.font.size = Pt(11)
    run.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')

doc.add_page_break()

# ============================================================
# 第二部分：书写总结
# ============================================================
add_heading_custom(doc, '第二部分  会诊意见书写总结', level=1, color=RGBColor(0x1F, 0x4E, 0x79))

add_heading_custom(doc, '一、书写基本原则', level=2)
principles = [
    ('循证性', '所有用药建议应有循证依据支撑，关键建议应标注证据来源。'),
    ('个体化', '结合患者具体情况给出个体化建议，避免"套模板"。'),
    ('可操作性', '建议应具体、明确、可执行——写明药物通用名、剂量、频次、途径、疗程。'),
    ('完整性', '不仅给出"用什么药"，还应覆盖"怎么用""用多久""注意什么""何时停/换"。'),
    ('清晰性', '会诊记录应结构清晰、层次分明，关键建议应突出显示。'),
    ('协作性', '会诊是咨询模式，建议而非指令，语气应专业、平等。'),
]
for name, desc in principles:
    p = doc.add_paragraph(style='List Bullet')
    p.paragraph_format.left_indent = Cm(1.27)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.line_spacing = 1.5
    run_b = p.add_run(f'{name}：')
    run_b.bold = True
    run_b.font.name = '宋体'
    run_b.font.size = Pt(11)
    run_b.font.color.rgb = RGBColor(0x1F, 0x4E, 0x79)
    run_b.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
    run = p.add_run(desc)
    run.font.name = '宋体'
    run.font.size = Pt(11)
    run.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')

add_heading_custom(doc, '二、书写框架：「为什么用 → 如何用 → 用后注意」', level=2)
add_para(doc, '借鉴用药分析书写模式，会诊意见应按以下逻辑循序渐进：', space_after=8)

fw_table = doc.add_table(rows=1, cols=3)
fw_table.style = 'Light Grid Accent 1'
fw_table.alignment = WD_TABLE_ALIGNMENT.CENTER
fw_hdr = fw_table.rows[0].cells
fw_headers = ['第一步：为什么用（用药分析）', '第二步：如何用（用药方案）', '第三步：用后注意（用药监护）']
for i, h in enumerate(fw_headers):
    fw_hdr[i].text = ''
    p = fw_hdr[i].paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(h)
    run.bold = True
    run.font.name = '黑体'
    run.font.size = Pt(10)
    run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
    run.element.rPr.rFonts.set(qn('w:eastAsia'), '黑体')
    set_cell_background(fw_hdr[i], '1F4E79')

fw_data = [
    '① 感染诊断与严重程度评估\n② 可能致病菌推断\n③ 耐药风险分析\n④ 用药指征确认\n⑤ 现用方案评估\n⑥ 药物选择循证依据',
    '① 药物名称（通用名）\n② 单次剂量+给药频次\n③ 给药途径\n④ 滴注时间\n⑤ 疗程建议\n⑥ 联合用药方案\n⑦ 特殊人群剂量调整\n⑧ 降阶梯策略',
    '① 疗效监测指标与节点\n② 不良反应监测重点\n③ TDM建议（如适用）\n④ 药物相互作用提示\n⑤ 特殊注意事项\n⑥ 停药/转换指征\n⑦ 随访计划',
]
row = fw_table.add_row()
for i, cell_text in enumerate(fw_data):
    cell = row.cells[i]
    cell.text = ''
    for j, line in enumerate(cell_text.split('\n')):
        if j == 0:
            p = cell.paragraphs[0]
        else:
            p = cell.add_paragraph()
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.line_spacing = 1.3
        run = p.add_run(line)
        run.font.name = '宋体'
        run.font.size = Pt(9)
        run.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')

add_para(doc, '', space_after=6)
add_para(doc, '关键建议的突出显示', bold=True, space_after=4)
add_para(doc, '会诊单密密麻麻的文字可能导致关键建议被淹没或混淆。药学服务的高质量体现之一，就是对关键建议进行单独或突出显示。推荐做法：', space_after=4)
add_bullet(doc, '在会诊意见末尾设置"核心建议"摘要框，用1-3句话概括最关键的用药建议')
add_bullet(doc, '核心药物名称、剂量、疗程等关键信息使用加粗标注')
add_bullet(doc, '特殊注意事项（如滴注时间、配伍禁忌）用醒目标记提示')

add_heading_custom(doc, '三、会诊意见质量自评清单', level=2)
add_para(doc, '书写完成后，逐项核对以下清单，确保会诊意见质量：', space_after=8)
checklist = [
    '是否明确了感染诊断和严重程度',
    '是否分析了可能的致病菌及耐药风险',
    '是否说明了药物选择的循证依据',
    '药物名称是否使用通用名（非商品名）',
    '是否写明了具体剂量、给药频次、给药途径',
    '是否注明了滴注时间或特殊给药要求',
    '是否标注了建议疗程或停药指征',
    '是否评估了肝肾功能并给出剂量调整建议',
    '是否提示了重要不良反应及监测方法',
    '是否注明了药物相互作用或配伍禁忌',
    '是否提出了降阶梯或序贯治疗策略',
    '是否有明确的"核心建议"摘要',
    '语气是否专业、平等、可操作',
    '是否标注了参考文献或循证来源',
]
for item in checklist:
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Cm(1.5)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.line_spacing = 1.5
    run_box = p.add_run('☐ ')
    run_box.font.name = '宋体'
    run_box.font.size = Pt(12)
    run_box.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
    run = p.add_run(item)
    run.font.name = '宋体'
    run.font.size = Pt(11)
    run.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')

doc.add_page_break()

# ============================================================
# 第三部分：提示词模板
# ============================================================
add_heading_custom(doc, '第三部分  可重复使用的会诊提示词模板', level=1, color=RGBColor(0x1F, 0x4E, 0x79))

add_heading_custom(doc, '一、提示词使用说明', level=2)
instructions = [
    '本提示词设计用于辅助临床药师撰写特殊使用级抗菌药物会诊意见。',
    '使用方法：将提示词完整复制，将【患者信息】部分替换为实际患者数据后，输入AI助手，即可生成结构化的会诊意见草稿。',
    '生成的会诊意见为初稿，药师应结合临床判断进行审核、修改和完善后，方可正式签署。',
    '提示词中的【】标注部分为需要填写的内容，{}标注部分为AI将自动生成的内容。',
    '可根据不同感染部位和病原体，灵活调整"会诊目的"中的具体问题。',
    '建议保留"循证依据"要求，确保输出建议有据可依。',
]
for inst in instructions:
    p = doc.add_paragraph(style='List Number')
    p.paragraph_format.left_indent = Cm(1.27)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.line_spacing = 1.5
    run = p.add_run(inst)
    run.font.name = '宋体'
    run.font.size = Pt(11)
    run.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')

add_heading_custom(doc, '二、完整提示词模板', level=2)
add_para(doc, '（以下为可直接复制使用的完整提示词，建议保存为模板文件反复使用）', italic=True, font_size=10, color=RGBColor(0x80, 0x80, 0x80), space_after=8)

prompt_text = """【角色设定】
你是一名具有高级专业技术职务任职资格的抗感染专业临床药师，具有丰富的抗菌药物临床应用经验，负责特殊使用级抗菌药物会诊。你的任务是根据患者信息，撰写一份规范、循证、个体化、可操作的特殊使用级抗菌药物会诊意见。

【书写要求】
1. 严格遵循"为什么用 → 如何用 → 用后注意"的逻辑框架
2. 所有用药建议须有循证依据，在相应位置标注参考来源
3. 药物使用通用名，剂量、频次、途径、疗程须具体明确
4. 结合患者个体特征（肝肾功能、体重、年龄等）给出调整建议
5. 关键建议须在末尾以"核心建议"摘要形式突出显示
6. 语气专业、平等，体现药学咨询的协作性
7. 参考资源优先级：最新国内指南/共识 > IDSA指南 > 热病（Sanford Guide）> 国家抗微生物治疗指南 > 药品说明书 > UpToDate

【患者基本信息】
- 姓名/性别/年龄/体重/身高：【填写】
- 入院日期：【填写】
- 主诉：【填写】
- 现病史：【填写】
- 既往史：【填写】（含基础疾病、手术史等）
- 过敏史：【填写】（药物过敏史及不良反应史，若无请注明"否认"）
- 基础疾病：【填写】（糖尿病、慢性肾病、肝病、免疫抑制等）

【感染相关情况】
- 感染诊断/疑似诊断：【填写】
- 感染部位：【填写】（如肺部、腹腔、泌尿道、血流、中枢神经系统、皮肤软组织等）
- 感染类型：【填写】（社区获得性/院内获得性/呼吸机相关/导管相关等）
- 感染严重程度：【填写】（轻/中/重/危重；如有脓毒症或脓毒症休克请注明；qSOFA评分、SOFA评分等）
- 发病时间/病程：【填写】

【实验室及辅助检查】
- 血常规：WBC【】x10^9/L，NEU【】x10^9/L，NEU%【】%，Hb【】g/L，PLT【】x10^9/L
- 炎症标志物：CRP【】mg/L，PCT【】ng/mL，IL-6【】pg/mL
- 肝功能：ALT【】U/L，AST【】U/L，TBIL【】umol/L，ALB【】g/L
- 肾功能：Cr【】umol/L，BUN【】mmol/L，eGFR【】mL/min/1.73m2
- 凝血功能：PT【】s，APTT【】s，D-Dimer【】mg/L
- 血气分析（如适用）：pH【】，PaO2【】mmHg，Lac【】mmol/L
- 尿常规：【填写异常项】
- 病原学检查：
  - 痰培养/血培养/尿培养/分泌物培养/脑脊液培养：【填写结果】
  - 药敏试验结果：【填写，含敏感(S)/中介(I)/耐药(R)】
  - G试验/GM试验：【填写】
  - mNGS/tNGS结果（如有）：【填写】
  - 其他分子诊断（如Xpert MTB/RIF、FilmArray等）：【填写】
- 影像学检查：【填写关键发现】

【当前及既往用药情况】
- 入院后抗菌药物使用史：
  - 药物1：【通用名+剂量+频次+给药途径】，使用时间【起止】，疗效评估【有效/无效/不确定】
  - 药物2：【通用名+剂量+频次+给药途径】，使用时间【起止】，疗效评估【有效/无效/不确定】
- 合并用药：【填写所有重要合并用药，尤其是可能产生相互作用的药物】
- 既往门诊/外院抗菌药物使用（如有）：【填写】

【肾功能动态变化（如适用）】
- 是否接受肾脏替代治疗：是/否（模式：【CRRT/IHD/PD】，参数：【填写】）
- 近期Cr变化趋势：【填写】

【会诊目的/核心问题】
请根据以上信息，回答以下问题：
【填写具体会诊问题，例如：
  1. 是否有使用特殊使用级抗菌药物的指征？
  2. 建议选择哪种/哪些抗菌药物？理由是什么？
  3. 具体给药方案（剂量、频次、途径、疗程）？
  4. 是否需要联合用药？如需要，联合方案是什么？
  5. 肾功能不全如何调整剂量？
  6. 降阶梯策略是什么？】"""

p = doc.add_paragraph()
p.paragraph_format.space_after = Pt(8)
p.paragraph_format.left_indent = Cm(0.5)
p.paragraph_format.right_indent = Cm(0.5)
run = p.add_run(prompt_text)
run.font.name = '等线'
run.font.size = Pt(10)
run.element.rPr.rFonts.set(qn('w:eastAsia'), '等线')

prompt_text2 = """【输出格式要求】
请按以下框架输出会诊意见：

====================================
        特殊使用级抗菌药物会诊意见
====================================

一、病例摘要与分析
{1-2段简要概括：患者基本信息、感染诊断、严重程度、关键检验/病原学结果、当前治疗情况及存在的问题}

二、抗感染治疗分析
（一）用药指征评估
{评估是否具备使用特殊使用级抗菌药物的指征，引用相关分级管理规定和指南}
（二）病原学分析
{分析可能的致病菌、耐药风险，结合本院/本地区耐药监测数据}
（三）药物选择循证依据
{说明推荐药物的理由，引用指南/共识/循证证据}

三、会诊建议（用药方案）
1. 推荐药物：【通用名】
2. 给药方案：单次剂量【】+ 频次【】+ 给药途径【】
3. 滴注时间：【填写，如"每次静脉滴注不少于60分钟"】
4. 建议疗程：【填写，如"7-14天，根据临床反应调整"】
5. 联合用药方案（如有）：【填写】
6. 特殊人群剂量调整：
   - 肾功能调整：【CrCl>50: 常规剂量；CrCl 10-50: 剂量调整为__; CrCl<10: 剂量调整为__】
   - 肝功能调整：【如适用】
   - CRRT剂量调整：【如适用，注明置换液流量对应的剂量】
7. 降阶梯策略：【经验治疗__天后，根据病原学结果降阶梯为__；或体温正常__天后转为口服序贯】

四、用药监护建议
1. 疗效监测：
   - 临床症状观察：【体温、症状体征变化】
   - 实验室复查：【复查血常规、CRP、PCT的时间节点】
   - 影像学随访：【如适用】
2. 不良反应监测：
   - 重点监测：【如肾毒性->监测Cr/q2d；血液毒性->监测血常规/q3d；肝毒性->监测肝功能/q3d】
   - 预警指标：【如Cr较基线升高>50%、PLT<50x10^9/L等】
   - 处理措施：【出现不良反应时的应对策略】
3. 治疗药物监测（TDM）：
   - 【如万古霉素：目标谷浓度15-20mg/L，首次监测时间：给药后第4剂给药前30min】
   - 【如伏立康唑：目标谷浓度2-5.5mg/L】
   - 【如不适用TDM，注明"该药物无需常规TDM"】
4. 药物相互作用提示：【列出重要相互作用及规避方法】
5. 特殊注意事项：【如配伍禁忌、储存要求、给药顺序等】

五、参考文献
1. 【列出引用的指南/共识/文献，格式规范】

====================================
  核心建议摘要（Key Recommendations）
====================================
【用1-3句话，加粗标注最关键的用药建议】

建议：_______________________________
理由：_______________________________
监护：_______________________________

====================================

会诊药师：【姓名】  职称：【高级/副主任药师/主任药师】
会诊日期：【YYYY年MM月DD日】"""

p2 = doc.add_paragraph()
p2.paragraph_format.space_after = Pt(8)
p2.paragraph_format.left_indent = Cm(0.5)
p2.paragraph_format.right_indent = Cm(0.5)
run2 = p2.add_run(prompt_text2)
run2.font.name = '等线'
run2.font.size = Pt(10)
run2.element.rPr.rFonts.set(qn('w:eastAsia'), '等线')

# 示例
add_heading_custom(doc, '三、会诊意见输出示例（参考）', level=2)
add_para(doc, '以下示例展示使用上述提示词生成的会诊意见样稿，供参考格式和深度：', space_after=8)

example_text = """====================================
        特殊使用级抗菌药物会诊意见
====================================

一、病例摘要与分析
患者，男性，72岁，因"反复咳嗽咳痰20年，加重伴发热5天"入院。诊断：AECOPD合并院内获得性肺炎（HAP）。既往多次住院抗感染治疗，有广谱抗菌药物暴露史。入院后经验性使用哌拉西林/他唑巴坦4.5g q8h ivgtt x3天，体温无明显下降，痰培养示铜绿假单胞菌（仅对碳青霉烯类、头孢他啶、阿米卡星敏感），血培养阴性。当前Cr 145umol/L（eGFR约42mL/min），WBC 15.2x10^9/L，NEU% 88%，PCT 3.8ng/mL。会诊核心问题：是否需要调整为碳青霉烯类？方案如何？

二、抗感染治疗分析
（一）用药指征评估
患者为HAP，既往广谱抗菌药物暴露，现有铜绿假单胞菌感染且对哌拉西林/他唑巴坦耐药，具备使用特殊使用级抗菌药物（碳青霉烯类）的指征。
（二）病原学分析
痰培养示铜绿假单胞菌，药敏显示对哌拉西林/他唑巴坦耐药、碳青霉烯类敏感。结合患者多次住院史及广谱抗菌药物暴露，考虑为院内获得性铜绿假单胞菌感染，不排除产AmpC酶可能。
（三）药物选择循证依据
根据《中国成人HAP/VAP诊断和治疗指南（2018）》及热病第50版，铜绿假单胞菌HAP首选抗假单胞菌beta-内酰胺类。本例病原菌对哌拉西林/他唑巴坦耐药，对碳青霉烯类敏感，故推荐调整为美罗培南。
（参考：《中国成人HAP/VAP诊断和治疗指南》2018版；热病第50版）

三、会诊建议（用药方案）
1. 推荐药物：美罗培南
2. 给药方案：1g q8h 静脉滴注
3. 滴注时间：每次静脉滴注不少于60分钟（延长滴注可提高PK/PD达标率）
4. 建议疗程：7-14天，根据临床反应和病原学结果评估
5. 联合用药：暂不建议联合用药。如治疗48-72h无效，可考虑联合阿米卡星15mg/kg qd ivgtt（需监测肾功能）
6. 特殊人群剂量调整：
   - 肾功能调整：患者eGFR约42mL/min，推荐美罗培南1g q12h
   - 如肾功能进一步恶化，需动态调整
7. 降阶梯策略：如治疗有效，获得药敏确认后可考虑降阶梯为头孢他啶2g q8h ivgtt（根据肾功能调整）

四、用药监护建议
1. 疗效监测：
   - 临床症状：每日监测体温、痰量及性状、呼吸困难程度
   - 实验室复查：q48h复查血常规、CRP、PCT；q72h复查肝肾功能
   - 影像学随访：治疗1周后复查胸片或胸部CT
2. 不良反应监测：
   - 中枢神经系统：美罗培南可引起癫痫（尤其高龄、肾功能不全），需观察意识状态
   - 肾功能：监测Cr变化，q48-72h
   - 肝功能：监测ALT/AST/TBIL，q72h
   - 凝血功能：监测PT/APTT
3. TDM：美罗培南暂不常规推荐TDM，但重症及肾功能不全患者有条件时可进行（目标fT>MIC 40%）
4. 药物相互作用：丙戊酸钠血药浓度可被碳青霉烯类显著降低，如患者使用丙戊酸钠需特别告知医师
5. 特殊注意事项：不可与丙戊酸钠同用；配伍时注意与多种药物存在配伍禁忌，建议单独通路输注

五、参考文献
1. 中华医学会呼吸病学分会. 中国成人HAP/VAP诊断和治疗指南（2018年版）. 中华结核和呼吸杂志, 2018, 41(4):255-280.
2. 热病：桑福德抗微生物治疗指南（第50版）.
3. 国家抗微生物治疗指南（第3版）. 人民卫生出版社, 2018.
4. 美罗培南药品说明书.

====================================
  核心建议摘要
====================================
建议：停用哌拉西林/他唑巴坦，调整为美罗培南1g q12h ivgtt（>60min），疗程7-14天。
理由：痰培养示铜绿假单胞菌对哌拉西林/他唑巴坦耐药、对碳青霉烯类敏感；患者高龄+肾功能不全，需根据eGFR调整剂量。
监护：重点监测肾功能、中枢神经系统反应；q48h复查炎症指标；注意不可与丙戊酸钠同用。

====================================

会诊药师：XXX  职称：副主任药师
会诊日期：2026年XX月XX日"""

p3 = doc.add_paragraph()
p3.paragraph_format.space_after = Pt(8)
p3.paragraph_format.left_indent = Cm(0.3)
p3.paragraph_format.right_indent = Cm(0.3)
run3 = p3.add_run(example_text)
run3.font.name = '等线'
run3.font.size = Pt(9)
run3.element.rPr.rFonts.set(qn('w:eastAsia'), '等线')

# 结尾
doc.add_paragraph()
end = doc.add_paragraph()
end.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = end.add_run('— 文档结束 —')
run.font.name = '楷体'
run.font.size = Pt(11)
run.font.color.rgb = RGBColor(0x80, 0x80, 0x80)
run.element.rPr.rFonts.set(qn('w:eastAsia'), '楷体')

note = doc.add_paragraph()
note.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = note.add_run('本文档仅供临床药师参考，具体用药请结合患者实际情况并遵循本院抗菌药物管理规定。')
run.font.name = '楷体'
run.font.size = Pt(9)
run.font.italic = True
run.font.color.rgb = RGBColor(0xA0, 0xA0, 0xA0)
run.element.rPr.rFonts.set(qn('w:eastAsia'), '楷体')

# ============ 保存 ============
default_name = '特殊使用级抗菌药物临床药师会诊指南与提示词模板.docx'
if len(sys.argv) > 1:
    output_path = sys.argv[1]
    if os.path.isdir(output_path):
        output_path = os.path.join(output_path, default_name)
else:
    output_path = os.path.join(os.getcwd(), default_name)

doc.save(output_path)
print(f'文档已保存：{output_path}')
