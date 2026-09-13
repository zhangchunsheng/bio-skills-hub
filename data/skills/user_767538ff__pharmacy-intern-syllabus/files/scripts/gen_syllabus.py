# -*- coding: utf-8 -*-
"""生成《药剂科实习生教学大纲》Word 文档（二甲医院 · 4周实习）

Usage: python gen_syllabus.py [output.docx]
  不带参数时输出到当前工作目录下「药剂科实习生教学大纲.docx」。
"""

import os
import sys
from docx import Document
from docx.shared import Pt, RGBColor, Cm, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

# ---- 颜色 ----
PRIMARY = RGBColor(0x18, 0x5F, 0xA5)   # 专业蓝
ACCENT = RGBColor(0x0F, 0x6E, 0x56)   # 墨绿
TEXT = RGBColor(0x2C, 0x2C, 0x2A)
MUTED = RGBColor(0x5F, 0x5E, 0x5A)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
STAR = RGBColor(0xC0, 0x39, 0x2B)      # 重点红
FILL_HEAD = "185FA5"
FILL_SUB = "E6F1FB"
FILL_ALT = "F4F8FC"
FONT_CN = "微软雅黑"
FONT_EN = "Arial"

OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.getcwd(), "药剂科实习生教学大纲.docx")


# ======================== 工具函数 ========================
def set_cell_bg(cell, color_hex):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), color_hex)
    tc_pr.append(shd)


def set_run(run, size=11, color=TEXT, bold=False, font_cn=FONT_CN):
    run.font.size = Pt(size)
    run.font.color.rgb = color
    run.font.bold = bold
    run.font.name = FONT_EN
    r = run._element
    rPr = r.get_or_add_rPr()
    rFonts = rPr.find(qn('w:rFonts'))
    if rFonts is None:
        rFonts = OxmlElement('w:rFonts')
        rPr.append(rFonts)
    rFonts.set(qn('w:eastAsia'), font_cn)
    rFonts.set(qn('w:ascii'), FONT_EN)
    rFonts.set(qn('w:hAnsi'), FONT_EN)


def add_para(doc, text, size=11, color=TEXT, bold=False, align=None, space_after=4, space_before=0):
    p = doc.add_paragraph()
    if align is not None:
        p.alignment = align
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.line_spacing = 1.25
    run = p.add_run(text)
    set_run(run, size, color, bold)
    return p


def add_h1(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(16)
    p.paragraph_format.space_after = Pt(8)
    run = p.add_run(text)
    set_run(run, size=16, color=PRIMARY, bold=True)
    # 底部边框
    pPr = p._p.get_or_add_pPr()
    pBdr = OxmlElement('w:pBdr')
    bottom = OxmlElement('w:bottom')
    bottom.set(qn('w:val'), 'single')
    bottom.set(qn('w:sz'), '12')
    bottom.set(qn('w:space'), '4')
    bottom.set(qn('w:color'), FILL_HEAD)
    pBdr.append(bottom)
    pPr.append(pBdr)
    return p


def add_h2(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(4)
    run = p.add_run(text)
    set_run(run, size=13, color=ACCENT, bold=True)
    return p


def add_h3(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(2)
    run = p.add_run(text)
    set_run(run, size=11.5, color=PRIMARY, bold=True)
    return p


def add_bullet(doc, text, level=0):
    p = doc.add_paragraph(style='List Bullet')
    p.paragraph_format.left_indent = Cm(0.75 + level * 0.5)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.line_spacing = 1.2
    run = p.add_run(text)
    set_run(run, size=11, color=TEXT)
    return p


def add_table_header_row(table, headers, widths=None):
    hdr = table.rows[0].cells
    for i, h in enumerate(headers):
        hdr[i].text = ''
        p = hdr[i].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(h)
        set_run(run, size=10.5, color=WHITE, bold=True)
        set_cell_bg(hdr[i], FILL_HEAD)
    if widths:
        for i, w in enumerate(widths):
            for row in table.rows:
                row.cells[i].width = Cm(w)


def add_data_row(table, row_idx, cells_data, alt=False):
    row = table.rows[row_idx]
    for i, txt in enumerate(cells_data):
        cell = row.cells[i]
        cell.text = ''
        p = cell.paragraphs[0]
        p.paragraph_format.space_after = Pt(1)
        p.paragraph_format.line_spacing = 1.15
        run = p.add_run(txt)
        set_run(run, size=10, color=TEXT)
        if alt:
            set_cell_bg(cell, FILL_ALT)


def style_table_borders(table):
    tbl = table._tbl
    tblPr = tbl.tblPr
    borders = OxmlElement('w:tblBorders')
    for edge in ('top', 'left', 'bottom', 'right', 'insideH', 'insideV'):
        el = OxmlElement(f'w:{edge}')
        el.set(qn('w:val'), 'single')
        el.set(qn('w:sz'), '4')
        el.set(qn('w:color'), 'BFD4E6')
        borders.append(el)
    tblPr.append(borders)


def make_table(doc, headers, rows, widths=None):
    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    style_table_borders(table)
    add_table_header_row(table, headers, widths)
    for i, row_data in enumerate(rows, start=1):
        add_data_row(table, i, row_data, alt=(i % 2 == 0))
    return table


def add_kv_table(doc, pairs):
    """两列键值表"""
    table = doc.add_table(rows=len(pairs), cols=2)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    style_table_borders(table)
    for i, (k, v) in enumerate(pairs):
        r = table.rows[i]
        c0, c1 = r.cells
        c0.width = Cm(3.5); c1.width = Cm(12)
        c0.text = ''; c1.text = ''
        p0 = c0.paragraphs[0]; p0.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run0 = p0.add_run(k); set_run(run0, 10.5, WHITE, True)
        set_cell_bg(c0, FILL_HEAD)
        p1 = c1.paragraphs[1] if len(c1.paragraphs) > 1 else c1.paragraphs[0]
        c1.paragraphs[0].text = ''
        p1 = c1.paragraphs[0]
        run1 = p1.add_run(v); set_run(run1, 10.5, TEXT)
        if i % 2 == 0:
            set_cell_bg(c1, FILL_ALT)
    return table


# ======================== 数据：知识点 ========================
# 每个单元: (单元号, 单元名, 学时, 教学方法, [(知识点, 标记)])
# 标记: "★" 重点, "▲" 难点, "★▲" 重点+难点, "" 普通

MODULE1_UNITS = [
    ("1.1", "药理学核心概念", "理论1.5+实操0.5", "讲授+示教",
     [
        ("药代动力学 ADME 四过程（吸收/分布/代谢/排泄）定义及临床意义", "★"),
        ("消除半衰期（t½）概念，稳态血药浓度需 4–5 个 t½ 达成", "★"),
        ("生物利用度定义，绝对与相对生物利用度的区别", ""),
        ("首过效应概念及规避途径（舌下/直肠/静脉给药）", "★"),
        ("表观分布容积（Vd）的数值与药物组织分布的关系", ""),
        ("清除率（CL）与给药间隔/维持剂量设计的联系", "▲"),
        ("药效学：受体、亲和力、内在活性概念", "▲"),
        ("量效关系曲线，效价强度与效能的区别", "▲"),
        ("治疗指数 TI = LD50/ED50 及安全范围的意义", "★"),
     ]),
    ("1.2", "药物分类体系", "理论1+实操0.5", "讲授+实物辨识",
     [
        ("按药理作用分类：抗感染/心血管/呼吸/消化/内分泌/神经/免疫", "★"),
        ("按剂型分类：固体/半固体/液体/气体注射剂", "★"),
        ("ATC（解剖-治疗-化学）分类法简介", ""),
        ("处方药与非处方药（OTC）分类及管理区别", "★"),
        ("国家基本药物目录与医保甲/乙类", ""),
        ("药品通用名与商品名区别，处方须用通用名", "★"),
     ]),
    ("1.3", "剂型与给药途径", "理论1+实操1", "讲授+示教+情景模拟",
     [
        ("缓释/控释制剂特点：不可掰开、嚼碎，需整片吞服", "★"),
        ("肠溶片原理：空腹服，不可嚼碎或掰开", "★"),
        ("泡腾片正确用法：水中完全溶解后饮用，严禁直接口服", "★"),
        ("舌下含片原理（硝酸甘油）及正确含服方法", "★"),
        ("注射剂给药途径（iv/im/sc/id）及推注速度要求", ""),
        ("静脉输液配伍注意及滴速控制（老年/心功能不全）", "▲"),
        ("吸入剂、栓剂、透皮贴剂等特殊剂型使用方法", ""),
        ("给药途径对药效的影响（首过效应、起效速度）", "▲"),
     ]),
    ("1.4", "药品说明书解读方法", "理论1+实操1", "讲授+案例讨论",
     [
        ("说明书核心结构：适应证/用法用量/禁忌/不良反应/注意事项", "★"),
        ("处方缩写：q.d./b.i.d./t.i.d./q.i.d./q.n./PRN/顿服含义", "★"),
        ("特殊人群剂量调整说明的识别与执行", ""),
        ("药物相互作用与配伍禁忌栏的识别", "★"),
        ("贮藏条件：冷藏2–8℃/阴凉≤20℃/常温≤30℃/避光", "★"),
        ("批准文号格式：国药准字 H/Z/S/J + 8 位", ""),
        ("说明书修订追踪意识，以最新版为准", ""),
     ]),
    ("1.5", "特殊管理药品", "理论1+实操1", "讲授+轮转实操",
     [
        ("麻醉药品定义及常用品种（吗啡、芬太尼、羟考酮等）", "★"),
        ("精神药品定义，分第一类/第二类及代表药", "★"),
        ("医疗用毒性药品定义及品种（阿托品、洋地黄毒苷等）", ""),
        ("放射性药品简介", ""),
        ("「五专」管理：专人负责/专柜加锁/专账/专处方/专册登记", "★"),
        ("麻精药品处方限量规定（注射剂1次量/控缓释7日/普通3日）", "★▲"),
        ("空安瓿回收、残损药品销毁与双人见证制度", "★"),
     ]),
]

MODULE2_UNITS = [
    ("2.1", "抗感染药物临床应用", "理论1.5+实操1", "讲授+案例讨论",
     [
        ("抗菌药物分级管理：非限制使用/限制使用/特殊使用", "★"),
        ("常用抗菌药分类及代表药（β-内酰胺/大环内酯/喹诺酮/氨基糖苷）", "★"),
        ("围术期预防用药时机：切皮前 0.5–1h，疗程一般≤24h", "★"),
        ("经验性治疗与目标治疗（药敏指导）的区别", ""),
        ("PK/PD 参数：MIC、T>MIC、AUC/MIC 临床意义", "▲"),
        ("多重耐药菌（MDRO）用药选择原则", "▲"),
        ("抗菌药常见不良反应：过敏/肝肾损伤/二重感染", "★"),
        ("特殊使用级抗菌药审批流程（会诊+审批）", "★"),
     ]),
    ("2.2", "心脑血管系统药物", "理论1+实操1", "讲授+案例讨论",
     [
        ("降压药五大类及代表药：CCB/ACEI/ARB/利尿剂/β阻滞剂", "★"),
        ("高血压分级管理及目标值（一般<140/90）", ""),
        ("他汀类调脂药机制及肝功能/肌酸激酶监测", "★"),
        ("抗血小板药（阿司匹林/氯吡格雷）及出血风险", "★"),
        ("华法林抗凝：INR 监测目标值 2.0–3.0", "★"),
        ("新型口服抗凝药（利伐沙班/达比加群）特点", ""),
        ("心衰「金三角」用药及监测", ""),
        ("心血管药物常见相互作用（如他汀+大环内酯）", "▲"),
     ]),
    ("2.3", "呼吸/消化/内分泌系统用药", "理论1.5+实操1", "讲授+示教+案例讨论",
     [
        ("吸入剂分类及正确使用方法（都保/准纳器/气雾剂）", "★"),
        ("平喘药阶梯治疗（β2激动剂/ICS/茶碱）", ""),
        ("PPI 适应证及长期使用风险（骨折/低镁/感染）", "★"),
        ("降糖药分类：双胍/磺脲/DPP-4i/SGLT2i/胰岛素", "★"),
        ("胰岛素分类（速效/短效/中效/长效/预混）及注射技术", "★"),
        ("低血糖识别（血糖<3.9mmol/L）与处理（15g葡萄糖法则）", "★"),
        ("甲亢/甲减用药（甲巯咪唑/左甲状腺素）及监测", ""),
        ("骨质疏松用药（双膦酸盐空腹服法）", ""),
     ]),
    ("2.4", "合理用药基本原则", "理论1+实操1", "讲授+案例讨论",
     [
        ("合理用药四要素：安全/有效/经济/适当", "★"),
        ("适应证适宜性判断（有无指征）", "★"),
        ("重复用药识别（同类或同效药物叠加）", "★"),
        ("配伍禁忌识别（物理/化学/药理）", "▲"),
        ("超适应证用药的判定与风险", ""),
        ("抗菌药物使用强度（AUD）控制意识", "★"),
        ("注射剂合理使用原则：能口服不肌注，能肌注不静注", "★"),
     ]),
    ("2.5", "常见药物相互作用", "理论1+实操0.5", "讲授+案例讨论",
     [
        ("药动学相互作用：吸收/分布/代谢/排泄四环节", "★"),
        ("CYP450 酶抑制剂与诱导剂及代表药", "★▲"),
        ("CYP3A4 常见底物及高风险相互作用", "▲"),
        ("药效学相互作用：协同与拮抗", ""),
        ("华法林与常见药物/食物相互作用", "★"),
        ("他汀类与相互作用高风险药物（克拉霉素/环孢素等）", "★"),
        ("中西药联合应用的相互作用风险", ""),
     ]),
    ("2.6", "药品不良反应识别与处理", "理论1+实操1", "讲授+情景模拟",
     [
        ("ADR 定义与药物不良事件（ADE）的区别", "★"),
        ("ADR 分类：A 型（剂量相关）/B 型（剂量无关）/C 型（长期）", "★"),
        ("Naranjo 评分量表应用（0–13 分）", "▲"),
        ("严重 ADR 识别：过敏性休克/肝衰/肾衰/剥脱性皮炎", "★"),
        ("过敏性休克应急处理流程（肾上腺素首选）", "★"),
        ("ADR 上报流程与时限（新的/严重 15 日内，死亡立即）", "★"),
        ("因果关系评价五级标准：肯定/很可能/可能/可疑/不可能", "★"),
     ]),
    ("2.7", "特殊人群用药", "理论1.5+实操0.5", "讲授+案例讨论",
     [
        ("老年人药代动力学改变及剂量调整原则（小剂量起始）", "★"),
        ("Beers 标准：老年人潜在不适当用药", "★"),
        ("老年人多重用药管理与用药重整", ""),
        ("儿童剂量计算（按体重/体表面积）", "★"),
        ("儿童用药禁忌（喹诺酮影响软骨/四环素影响牙齿）", "★"),
        ("妊娠期用药 FDA 分级（A/B/C/D/X）", "★"),
        ("哺乳期用药安全（L1–L5 分级）", ""),
        ("肾功能不全用药调整（按 eGFR 分级调整）", "▲"),
     ]),
    ("2.8", "处方审核与点评要点", "理论1+实操1.5", "讲授+案例讨论+轮转实操",
     [
        ("处方审核三要素：合法性/规范性/适宜性", "★"),
        ("处方点评制度及抽样比例（每科室每月≥25 张）", "★"),
        ("不合理处方三类：不规范/用药不适宜/超常处方", "★"),
        ("适宜性审核要点：适应证/剂量/途径/重复/相互作用", "▲"),
        ("抗菌药物处方专项点评内容", "★"),
        ("处方点评结果反馈与整改闭环", ""),
     ]),
]

MODULE3_UNITS = [
    ("3.1", "药品调剂全流程", "理论0.5+实操4", "讲授+示教+情景模拟+轮转实操",
     [
        ("调剂五步：收方→审核→调配→核对→发药", "★"),
        ("「四查十对」内容（查处方/药品/配伍禁忌/用药合理性）", "★"),
        ("双人核对制度执行与签字", "★"),
        ("门诊与住院调剂流程差异", ""),
        ("电子处方系统操作要点", ""),
        ("调剂差错高发环节识别与防范", "▲"),
     ]),
    ("3.2", "处方管理办法要点", "理论0.5+实操1", "讲授+案例讨论",
     [
        ("处方权管理：执业医师开具、药师调剂", "★"),
        ("处方有效期：当日有效，特殊情况最长不超过 3 日", "★"),
        ("处方保存期限：普通 1 年/精神 2 年/麻醉 3 年", "★"),
        ("处方限量：普通 7 日量/急诊 3 日量/慢性病可适当延长", "★"),
        ("处方书写规范：药名/剂量/单位/用法完整", "★"),
        ("不合格处方处理与登记", ""),
     ]),
    ("3.3", "药品储存养护", "理论0.5+实操2", "讲授+轮转实操",
     [
        ("药品贮藏条件分类：冷处 2–8℃/阴凉≤20℃/常温≤30℃", "★"),
        ("避光与遮光的区别及执行", ""),
        ("冷链药品管理（胰岛素、疫苗等）全程温控", "★"),
        ("拆零药品管理及记录", ""),
        ("近效期药品管理（有效期<6 个月黄色预警）", "★"),
        ("先进先出/近期先出原则执行", "★"),
        ("药品质量可疑识别（变色/沉淀/裂片/异味）", "★"),
     ]),
    ("3.4", "麻精药品管理细则", "理论0.5+实操2", "讲授+示教+轮转实操",
     [
        ("「五专」管理具体执行标准", "★"),
        ("双人双锁专柜保管制度", "★"),
        ("逐日登记（日清日结）与账物相符", "★"),
        ("麻醉药品处方限量（注射 1 次量/控缓释 7 日/其他 3 日）", "★▲"),
        ("第一类/第二类精神药品处方限量", "★"),
        ("空安瓿回收与登记制度", "★"),
        ("残损药品销毁流程（双人见证、记录备案）", "★"),
        ("麻精药品丢失/被盗 2 小时内上报", "★"),
     ]),
    ("3.5", "药品盘点与效期管理", "理论0.5+实操1.5", "讲授+轮转实操",
     [
        ("药品盘点制度（月盘/季盘/年盘）", "★"),
        ("账物相符率要求（≥99.5%）", "★"),
        ("效期识别与预警系统操作", "★"),
        ("近效期药品处理：催销/退换/报损", ""),
        ("过期药品报损与销毁流程", "★"),
        ("盘点差异分析与处理记录", ""),
     ]),
    ("3.6", "发药交代与用药咨询", "理论0.5+实操3", "讲授+情景模拟+轮转实操",
     [
        ("发药交代核心内容：药名/用途/用法用量/注意事项", "★"),
        ("特殊剂型用药交代（缓释/肠溶/吸入剂）", "★"),
        ("用药咨询应答流程（倾听→询问→分析→建议→记录）", ""),
        ("漏服处理原则（时间过半补服规则）", "★"),
        ("药品保存指导（冷藏/避光/防潮）", ""),
        ("门诊用药咨询窗口沟通技巧", ""),
     ]),
    ("3.7", "差错防范与上报", "理论0.5+实操0.5", "讲授+案例讨论",
     [
        ("调剂差错类型：内差（未发药）与外差（已发药）", "★"),
        ("差错高发环节：相似药名/相似包装/剂量错误", "★"),
        ("三重防线：审方/调配/发药核对", "★"),
        ("高警示药品管理及红色标识", "★"),
        ("听似/看似药品（LASA）管理与分隔存放", "★"),
        ("非惩罚性差错上报制度与流程", "★"),
        ("差错分析与持续改进（PDCA）", ""),
     ]),
    ("3.8", "医疗安全与院感防控", "理论0.5+实操0.5", "讲授+示教",
     [
        ("手卫生时机：两前（接触患者前/无菌操作前）三后", "★"),
        ("药品调配职业防护（手套/口罩）", ""),
        ("职业暴露处理流程（针刺伤冲洗/挤血/消毒/上报）", "★"),
        ("医疗废物分类与处置（感染性/损伤性/化学性）", "★"),
        ("药品安全自查制度与记录", ""),
        ("突发事件应急：药品短缺/群体 ADR 事件", ""),
     ]),
]


# ======================== 文档构建 ========================
def build():
    doc = Document()
    # 页面设置
    section = doc.sections[0]
    section.page_width = Cm(21)
    section.page_height = Cm(29.7)
    section.top_margin = Cm(2.2)
    section.bottom_margin = Cm(2.2)
    section.left_margin = Cm(2.5)
    section.right_margin = Cm(2.5)

    # Normal 样式
    normal = doc.styles['Normal']
    normal.font.name = FONT_EN
    normal.font.size = Pt(11)
    normal._element.rPr.rFonts.set(qn('w:eastAsia'), FONT_CN)

    # ---- 封面信息 ----
    add_para(doc, "药剂科实习生教学大纲", size=22, color=PRIMARY, bold=True,
             align=WD_ALIGN_PARAGRAPH.CENTER, space_after=2, space_before=30)
    add_para(doc, "（二甲医院 · 4 周岗前培训）", size=13, color=MUTED,
             align=WD_ALIGN_PARAGRAPH.CENTER, space_after=20)

    # 基本信息表
    info_pairs = [
        ("适用对象", "药学专业实习生（本科 / 大专）"),
        ("实习周期", "4 周（约 80 学时，理论 32 + 实操 48）"),
        ("编制单位", "药剂科"),
        ("编制依据", "《处方管理办法》《医疗机构药事管理规定》《抗菌药物临床应用管理办法》《药品管理法》"),
        ("编制日期", "2026 年 8 月"),
    ]
    add_kv_table(doc, info_pairs)
    add_para(doc, "", space_after=6)

    # ---- 第一部分：大纲说明 ----
    add_h1(doc, "一、大纲说明")
    add_para(doc, "本大纲面向二甲医院药剂科实习生岗前培训，按照「模块 → 单元 → 知识点」三级结构设计，"
             "覆盖药物基础知识、药物临床应用、药剂科日常工作注意细则三大模块，共 21 个教学单元。"
             "内容结合二甲医院药剂科实际（药品种类、病种、人员配置），突出可落地、可考核，"
             "杜绝照搬三甲模板。涉及具体药品剂量与适应证，以最新说明书与临床指南为准。")
    add_para(doc, "标注说明：★ 表示重点（必须掌握），▲ 表示难点（易错或需重点突破），★▲ 表示既是重点又是难点。",
             color=MUTED, size=10)

    # ---- 第二部分：总体学时分配 ----
    add_h1(doc, "二、总体学时分配")
    add_para(doc, "按 4 周实习周期设计，每周约 20 学时，理论：实操 ≈ 2 : 3。", color=MUTED, size=10)
    make_table(doc,
        ["模块", "内容", "理论学时", "实操学时", "小计"],
        [
            ["模块一", "药物基础知识", "12", "6", "18"],
            ["模块二", "药物临床应用", "14", "10", "24"],
            ["模块三", "药剂科日常工作注意细则", "6", "32", "38"],
            ["合计", "—", "32", "48", "80"],
        ],
        widths=[2.2, 6.5, 2.2, 2.2, 1.8])
    add_para(doc, "", space_after=4)
    add_para(doc, "说明：模块三实操占比高，因实习生主要在调剂岗位轮转；各单元学时可根据排班微调，"
             "但模块三实操总学时不得低于 30。", color=MUTED, size=9.5)

    # ---- 第三部分：考核方式与合格标准 ----
    add_h1(doc, "三、考核方式与合格标准")
    make_table(doc,
        ["考核项目", "形式", "占比", "合格标准"],
        [
            ["模块一 理论笔试", "闭卷，单选+多选+判断", "25%", "≥ 60 分"],
            ["模块二 处方审核与案例分析", "笔试+处方点评实操", "35%", "≥ 70 分"],
            ["模块三 岗位技能考核", "现场操作（调剂/养护/发药交代）", "30%", "≥ 70 分"],
            ["平时表现", "考勤/学习态度/带教笔记", "10%", "带教老师评定"],
        ],
        widths=[4.5, 5.5, 1.8, 3.2])
    add_para(doc, "", space_after=4)
    add_para(doc, "综合合格标准：总分 ≥ 60 分，且各模块单项均达合格线。不合格者安排补考，"
             "补考仍不合格者延长实习 1 周或退回学校。", color=MUTED, size=9.5)

    # ======================== 模块一 ========================
    add_h1(doc, "模块一：药物基础知识")
    add_para(doc, "理论 12 学时 + 实操 6 学时，共 18 学时。", color=MUTED, size=10)

    add_h2(doc, "教学目标")
    add_h3(doc, "知识目标")
    for t in [
        "掌握药代动力学（ADME）、半衰期、生物利用度、首过效应等核心概念",
        "熟悉常用药物分类体系与剂型特点",
        "掌握药品说明书各栏目含义及解读方法",
        "掌握麻醉/精神/毒性/放射性药品的分类与「五专」管理要求",
    ]:
        add_bullet(doc, t)
    add_h3(doc, "技能目标")
    for t in [
        "能正确解读药品说明书并提取关键用药信息",
        "能根据剂型指导患者正确用药（缓释/肠溶/泡腾/吸入剂等）",
        "能识别特殊管理药品并执行「五专」管理流程",
        "能完成特殊管理药品的登记、回收与销毁记录",
    ]:
        add_bullet(doc, t)
    add_h3(doc, "态度目标")
    for t in [
        "树立药品安全第一意识，理解规范操作的重要性",
        "培养严谨求实的药学职业素养",
        "尊重法规，养成按制度办事的习惯",
    ]:
        add_bullet(doc, t)

    for code, name, hours, method, points in MODULE1_UNITS:
        add_h2(doc, f"单元 {code} {name}")
        add_para(doc, f"建议学时：{hours} ｜ 教学方法：{method}", color=MUTED, size=10)
        make_table(doc,
            ["序号", "知识点", "标记"],
            [[str(i+1), p, m] for i, (p, m) in enumerate(points)],
            widths=[1.4, 12.6, 2.0])

    # ======================== 模块二 ========================
    add_h1(doc, "模块二：药物临床应用")
    add_para(doc, "理论 14 学时 + 实操 10 学时，共 24 学时。", color=MUTED, size=10)

    add_h2(doc, "教学目标")
    add_h3(doc, "知识目标")
    for t in [
        "掌握抗感染、心血管、呼吸、消化、内分泌等重点系统常用药物",
        "掌握合理用药四要素及处方审核要点",
        "熟悉常见药物相互作用机制与高风险组合",
        "掌握 ADR 分类、识别与上报流程",
        "掌握特殊人群（老年/儿童/孕产妇/肝肾功能不全）用药调整原则",
    ]:
        add_bullet(doc, t)
    add_h3(doc, "技能目标")
    for t in [
        "能完成处方合法性、规范性、适宜性审核",
        "能识别重复用药、配伍禁忌与药物相互作用",
        "能运用 Naranjo 量表进行 ADR 关联性评价",
        "能处理过敏性休克等严重 ADR 应急情况",
        "能对特殊人群处方提出用药建议",
    ]:
        add_bullet(doc, t)
    add_h3(doc, "态度目标")
    for t in [
        "树立合理用药与用药安全意识",
        "培养以患者为中心的药学服务理念",
        "养成循证用药、参考最新指南的习惯",
    ]:
        add_bullet(doc, t)

    for code, name, hours, method, points in MODULE2_UNITS:
        add_h2(doc, f"单元 {code} {name}")
        add_para(doc, f"建议学时：{hours} ｜ 教学方法：{method}", color=MUTED, size=10)
        make_table(doc,
            ["序号", "知识点", "标记"],
            [[str(i+1), p, m] for i, (p, m) in enumerate(points)],
            widths=[1.4, 12.6, 2.0])

    # ======================== 模块三 ========================
    add_h1(doc, "模块三：药剂科日常工作注意细则")
    add_para(doc, "理论 6 学时 + 实操 32 学时，共 38 学时。本模块为实习核心，实操占比最高。", color=MUTED, size=10)

    add_h2(doc, "教学目标")
    add_h3(doc, "知识目标")
    for t in [
        "掌握药品调剂全流程及「四查十对」",
        "掌握《处方管理办法》核心要点",
        "掌握药品储存养护条件与效期管理",
        "掌握麻精药品管理细则与销毁流程",
        "熟悉差错防范三重防线与院感防控要求",
    ]:
        add_bullet(doc, t)
    add_h3(doc, "技能目标")
    for t in [
        "能独立完成门诊/住院药品调剂操作",
        "能执行药品盘点、效期预警与近效期处理",
        "能完成麻精药品的调剂、登记与空安瓿回收",
        "能规范进行发药交代与用药咨询",
        "能识别差错并按流程上报",
    ]:
        add_bullet(doc, t)
    add_h3(doc, "态度目标")
    for t in [
        "树立流程即安全的理念，严格执行核对制度",
        "养成非惩罚性上报意识，主动报告差错与隐患",
        "培养良好的医患沟通与药学服务态度",
        "遵守院感规范，注重职业防护",
    ]:
        add_bullet(doc, t)

    for code, name, hours, method, points in MODULE3_UNITS:
        add_h2(doc, f"单元 {code} {name}")
        add_para(doc, f"建议学时：{hours} ｜ 教学方法：{method}", color=MUTED, size=10)
        make_table(doc,
            ["序号", "知识点", "标记"],
            [[str(i+1), p, m] for i, (p, m) in enumerate(points)],
            widths=[1.4, 12.6, 2.0])

    # ---- 附：教学方法说明 ----
    add_h1(doc, "附：教学方法说明")
    method_pairs = [
        ("讲授法", "适用于理论概念、法规要点，带教老师系统讲解"),
        ("示教演示法", "带教老师完整演示操作流程并口述要点，实习生观摩"),
        ("情景模拟法", "设置「陷阱处方」或模拟发药场景，检验实习生识别与应对能力"),
        ("案例讨论法", "以真实差错案例或 ADR 案例为载体，引导分析与讨论"),
        ("轮转实操法", "在门诊药房、住院药房、麻精药柜等岗位轮转，在带教指导下实际操作"),
    ]
    make_table(doc,
        ["教学方法", "适用场景与说明"],
        [[k, v] for k, v in method_pairs],
        widths=[3.5, 12.5])

    # ---- 附：参考法规与依据 ----
    add_h1(doc, "附：参考法规与依据")
    for ref in [
        "《中华人民共和国药品管理法》（2019 修订）",
        "《处方管理办法》（卫生部令第 53 号）",
        "《医疗机构药事管理规定》（卫医政发〔2011〕11 号）",
        "《抗菌药物临床应用管理办法》（卫生部令第 84 号）",
        "《麻醉药品和精神药品管理条例》（国务院令第 442 号）",
        "《医疗机构麻醉药品、第一类精神药品管理规定》（卫医发〔2005〕438 号）",
        "《药品不良反应报告和监测管理办法》（卫生部令第 81 号）",
        "相关药品最新说明书及国家卫生计生委发布的临床用药指南",
    ]:
        add_bullet(doc, ref)

    add_para(doc, "提示：涉及具体药品剂量、适应证、相互作用等内容，应以最新版药品说明书与"
             "国家发布的临床诊疗指南为准；本大纲标注「以最新指南为准」处尤需注意。",
             color=MUTED, size=9.5, space_before=8)

    doc.save(OUT)
    print("Saved:", OUT)


if __name__ == "__main__":
    build()
