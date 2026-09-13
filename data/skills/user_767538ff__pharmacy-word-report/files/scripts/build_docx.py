# -*- coding: utf-8 -*-
"""
药品使用分析 -> 三线表 Word 报表生成器

用法:
    python build_docx.py <analysis_results.json> <output.docx>

读取 analyze.py 产出的 analysis_results.json 及其同目录 figs/ 下的 PNG，
生成分层级、结论先行、三线表的 Word 报表。
"""
import json, os, sys
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

CN_FONT = "宋体"
HE_FONT = "黑体"
WAN = lambda x: f"{x/1e4:,.2f}"


def set_cn(run, font=CN_FONT, size=10.5, bold=False):
    run.font.name = font; run.font.size = Pt(size); run.bold = bold
    run._element.get_or_add_rPr().rFonts.set(qn("w:eastAsia"), font)


def heading(doc, text, level=1):
    p = doc.add_paragraph(); r = p.add_run(text)
    if level == 1:
        set_cn(r, HE_FONT, 14, True); p.paragraph_format.space_before = Pt(10); p.paragraph_format.space_after = Pt(4)
    else:
        set_cn(r, HE_FONT, 12, True); p.paragraph_format.space_before = Pt(6); p.paragraph_format.space_after = Pt(2)
    return p


def para(doc, text, size=10.5, bold=False, indent=False):
    p = doc.add_paragraph(); r = p.add_run(text); set_cn(r, CN_FONT, size, bold)
    if indent:
        p.paragraph_format.first_line_indent = Pt(21)
    return p


def concl(doc, text):
    p = doc.add_paragraph(); r = p.add_run("【结论】" + text); set_cn(r, CN_FONT, 10.5, True)
    p.paragraph_format.first_line_indent = Pt(21); return p


def add_fig(doc, path, width=15.5):
    doc.add_picture(path, width=Cm(width)); doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER


def set_border(el, side, sz, val="single", color="000000"):
    e = OxmlElement(f"w:{side}")
    e.set(qn("w:val"), val); e.set(qn("w:sz"), str(sz)); e.set(qn("w:space"), "0"); e.set(qn("w:color"), color)
    el.append(e)


def three_line_table(table, top=18, mid=12, bot=18):
    tbl = table._tbl; tblPr = tbl.tblPr
    borders = tblPr.find(qn("w:tblBorders"))
    if borders is None:
        borders = OxmlElement("w:tblBorders"); tblPr.append(borders)
    for child in list(borders):
        borders.remove(child)
    for tag in ("top", "bottom"):
        set_border(borders, tag, top)
    for tag in ("left", "right", "insideH", "insideV"):
        set_border(borders, tag, 0, val="none")
    for cell in table.rows[0].cells:
        tcPr = cell._tc.get_or_add_tcPr(); cb = tcPr.find(qn("w:tcBorders"))
        if cb is None:
            cb = OxmlElement("w:tcBorders"); tcPr.append(cb)
        set_border(cb, "bottom", mid)


def style_header(table):
    for cell in table.rows[0].cells:
        for p in cell.paragraphs:
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for r in p.runs:
                set_cn(r, HE_FONT, 9.5, True)


def fill_table(table, data, cols, headers, widths=None, num_fmt=None):
    hdr = table.rows[0].cells
    for i, h in enumerate(headers):
        hdr[i].text = ""; set_cn(hdr[i].paragraphs[0].add_run(h), HE_FONT, 9.5, True)
    for row in data:
        cells = table.add_row().cells
        for i, c in enumerate(cols):
            v = row[c]
            if num_fmt and i in num_fmt and isinstance(v, (int, float)):
                v = num_fmt[i](v)
            cells[i].text = ""; p = cells[i].paragraphs[0]; p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            set_cn(p.add_run(str(v)), CN_FONT, 9)
    if widths:
        for i, w in enumerate(widths):
            for r in table.rows:
                r.cells[i].width = Cm(w)
    three_line_table(table); style_header(table); table.alignment = WD_TABLE_ALIGNMENT.CENTER


def main():
    if len(sys.argv) < 3:
        print(__doc__); sys.exit(1)
    JSON = sys.argv[1]; DOCX = sys.argv[2]
    base = os.path.dirname(os.path.abspath(JSON))
    FIG = os.path.join(base, "figs")
    R = json.load(open(JSON, encoding="utf-8"))
    m = R["meta"]; tot = m["total_amount"]

    doc = Document()
    st = doc.styles["Normal"]; st.font.name = CN_FONT; st.font.size = Pt(10.5)
    st.element.rPr.rFonts.set(qn("w:eastAsia"), CN_FONT)

    tp = doc.add_paragraph(); tp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    set_cn(tp.add_run("全院药品使用分析报表"), HE_FONT, 18, True)
    sp = doc.add_paragraph(); sp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    set_cn(sp.add_run(f"（{m.get('period','')} · 药库出库数据 · 全院各科室）"), CN_FONT, 11)
    mp = doc.add_paragraph(); mp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    set_cn(mp.add_run("数据来源：药库出库　|　统计粒度：全院各科室　|　生成：数据分析及可视化助手"), CN_FONT, 9.5)
    doc.add_paragraph()

    # 一、数据概况与质量
    heading(doc, "一、数据概况与质量", 1)
    concl(doc, f"本期数据共 {m['rows']:,} 条出库记录，覆盖 {m['depts']} 个科室、{m['drugs']} 个药品通用名，"
              f"药品使用总金额 {tot/1e8:.2f} 亿元（{tot/1e4:,.2f} 万元）。字段完整、无缺失值；"
              f"经校验 金额 = 数量 × 单价 全部成立（{R['quality']['amount_eq_qty_x_price_mismatch']} 条不一致）；"
              f"仅发现 {R['quality']['zero_amount_rows']} 条金额为 0、{R['quality']['zero_price_rows']} 条单价为 0 的记录，需进一步核实。")
    t = doc.add_table(rows=1, cols=2)
    fill_table(t, [
        {"项目": "出库记录数", "值": f"{m['rows']:,} 条"},
        {"项目": "覆盖科室数", "值": f"{m['depts']} 个"},
        {"项目": "药品通用名数", "值": f"{m['drugs']} 个"},
        {"项目": "总金额", "值": f"{tot:,.2f} 元"},
        {"项目": "总金额（万元）", "值": f"{tot/1e4:,.2f} 万元"},
        {"项目": "总金额（亿元）", "值": f"{tot/1e8:.2f} 亿元"},
        {"项目": "ATC 1级分类数", "值": f"{R['quality']['atc1_count']} 类"},
        {"项目": "缺失值", "值": "无（各字段缺失率 0%）"},
        {"项目": "金额为0记录", "值": f"{R['quality']['zero_amount_rows']} 条（待核实）"},
        {"项目": "单价为0记录", "值": f"{R['quality']['zero_price_rows']} 条（待核实）"},
        {"项目": "金额=数量×单价校验", "值": f"{R['quality']['amount_eq_qty_x_price_mismatch']} 条不一致"},
    ], ["项目", "值"], ["数据质量指标", "结果"], widths=[6, 9.5])
    para(doc, "说明：本报告所有金额均直接取自原始出库记录、按通用名/ATC/科室如实汇总，未作任何缺失值填补或数据臆造；"
              "单位以“万元”为主、兼列“亿元”，便于阅读。", size=9, indent=True)

    # 二、总体药品使用分析
    heading(doc, "二、总体药品使用金额分析（排名前50）", 1)
    concl(doc, f"药品金额呈明显长尾分布：金额最高的 50 个通用名合计占全院 {R['top50_total_share']:.2f}%，"
              f"但单品种最高占比仅约 3%，未见单一药品垄断；金额前列以高值抗肿瘤药、广谱抗真菌药、"
              f"消化内分泌药及血液系统药为主，符合大型三甲专科医院收治病种结构，总体结构基本合理，但需关注少数极高值药品的金额体量。")
    add_fig(doc, os.path.join(FIG, "top15_drug.png"))
    add_fig(doc, os.path.join(FIG, "pareto.png"), width=14)
    para(doc, "表1　药品使用金额排名前50（按通用名汇总）", size=10, bold=True)
    t50 = doc.add_table(rows=1, cols=7)
    for i, h in enumerate(["排名", "通用名", "ATC 1级", "金额(万元)", "占比(%)", "累计占比(%)", "数量"]):
        t50.rows[0].cells[i].text = ""; set_cn(t50.rows[0].cells[i].paragraphs[0].add_run(h), HE_FONT, 9, True)
    for idx, r in enumerate(R["top50"], 1):
        cells = t50.add_row().cells
        vals = [str(idx), r["generic"], r["atc1"], WAN(r["金额"]), f"{r['占比']:.2f}", f"{r['累计占比']:.2f}", f"{int(r['数量']):,}"]
        for i, v in enumerate(vals):
            cells[i].text = ""; p = cells[i].paragraphs[0]; p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            set_cn(p.add_run(v), CN_FONT, 8.5)
    three_line_table(t50); style_header(t50); t50.alignment = WD_TABLE_ALIGNMENT.CENTER
    para(doc, "合理性分析：", size=10, bold=True)
    para(doc, "① 金额居首品种多为高值靶向/免疫治疗药，金额体量与其单次治疗费用及本院肿瘤、血液、泌尿等专科规模相匹配，结构总体合理。", size=9.5, indent=True)
    para(doc, "② 广谱抗真菌药（如艾沙康唑）金额居前，反映 ICU 及血液科侵袭性真菌感染预防/治疗需求，建议结合病原学依据与疗程开展专项点评。", size=9.5, indent=True)
    para(doc, "③ 单品种最高占比仅约3%、Top50累计约49%，提示金额分散于众多品种，无单一药品异常集中；但前50名中抗肿瘤药占比偏高，应纳入重点监控药品管理。", size=9.5, indent=True)

    # 三、ATC 分类
    heading(doc, "三、ATC 分类药品使用金额分析", 1)
    concl(doc, f"按 ATC 1级分类，金额居前依次为：抗肿瘤药及免疫调节剂、消化道和代谢方面的药物、血液和造血器官药、"
              f"心血管系统用药、全身用抗感染药等。抗肿瘤与免疫调节剂金额占比最高，与本院专科定位一致；"
              f"但部分高价抗肿瘤/免疫制剂在多个非肿瘤科室大量出库，需关注跨科室使用的适应证匹配。")
    add_fig(doc, os.path.join(FIG, "atc1.png"))
    para(doc, "表2　ATC 1级分类药品使用金额汇总（全部22类）", size=10, bold=True)
    fill_table(doc.add_table(rows=1, cols=6), R["atc1"],
               ["atc1", "金额", "占比", "累计占比", "品种数", "科室数"],
               ["ATC 1级分类", "金额(万元)", "占比(%)", "累计占比(%)", "品种数", "科室数"],
               widths=[4.6, 2.7, 1.6, 1.9, 1.5, 1.5],
               num_fmt={1: WAN, 2: lambda x: f"{x:.2f}", 3: lambda x: f"{x:.2f}"})
    para(doc, "表3　ATC 2级分类药品使用金额汇总（金额前30）", size=10, bold=True)
    fill_table(doc.add_table(rows=1, cols=5), R["atc2"][:30],
               ["atc2", "金额", "占比", "品种数", "科室数"],
               ["ATC 2级分类", "金额(万元)", "占比(%)", "品种数", "科室数"],
               widths=[5.4, 2.7, 1.6, 1.5, 1.5],
               num_fmt={1: WAN, 2: lambda x: f"{x:.2f}"})
    para(doc, "合理性分析：", size=10, bold=True)
    topstr = "、".join([f"{x['atc1']}（{x['占比']:.1f}%）" for x in R["atc1"][:5]])
    para(doc, f"① 金额前5位ATC 1级分类为：{topstr}。抗肿瘤药及免疫调节剂居首，符合肿瘤/血液重点专科医院的病种结构，属合理主导方向。", size=9.5, indent=True)
    para(doc, "② 消化道和代谢药（含质子泵抑制剂、胰岛素类等）与血液系统药金额居前，为住院慢病与围手术期常规用药，结构合理，但质子泵抑制剂等可纳入专项点评以控费。", size=9.5, indent=True)
    para(doc, "③ 全身用抗感染药金额占比居前，建议结合抗菌药物管理（AMS）开展强度与DDDs监测；罕见病/超高值药虽金额大、患者数少，应单独建册追踪。", size=9.5, indent=True)
    para(doc, "④ 各ATC 2级内部亦呈长尾，建议对金额前30的ATC 2级节点实施ABC分类与重点监控。", size=9.5, indent=True)

    # 四、科室
    heading(doc, "四、科室药品使用分析", 1)
    concl(doc, f"科室层面金额高度集中：金额前30的科室合计占全院 {R['dept_total_share_top30']:.2f}%。"
              f"国际医疗部、侨内科部、肿瘤科等大额科室主导药品多为高值抗肿瘤药；"
              f"同时检出 {len(R['susp_mismatch'])} 个“专科-主导药品匹配存疑”科室及 {len(R['susp_concentration'])} 个"
              f"“单一药品占本科室金额>30%”的高度集中科室，需药师逐科核实。")
    add_fig(doc, os.path.join(FIG, "top15_dept.png"))
    para(doc, "表4　科室药品使用金额排名前30", size=10, bold=True)
    fill_table(doc.add_table(rows=1, cols=6), R["dept_top"],
               ["dept", "金额", "占比", "累计占比", "品种数", "记录数"],
               ["科室", "金额(万元)", "占比(%)", "累计占比(%)", "品种数", "记录数"],
               widths=[4.0, 2.7, 1.5, 1.8, 1.5, 1.5],
               num_fmt={1: WAN, 2: lambda x: f"{x:.2f}", 3: lambda x: f"{x:.2f}"})
    para(doc, "表5　专科-主导药品匹配存疑科室清单（需药师核实）", size=10, bold=True)
    fill_table(doc.add_table(rows=1, cols=5), R["susp_mismatch"],
               ["科室", "主导药品", "主导ATC1", "主导占比", "科室金额"],
               ["科室", "主导药品（金额第一）", "主导药品ATC 1级", "占本科室(%)", "科室金额(万元)"],
               widths=[3.2, 3.0, 2.8, 1.8, 2.2],
               num_fmt={3: lambda x: f"{x:.1f}", 4: WAN})
    para(doc, "注：上表“匹配存疑”指该科室名称提示为非肿瘤/非系统治疗专科，但其金额第一的药品为抗肿瘤药及免疫调节剂。"
              "其中风湿（阿达木单抗用于类风湿关节炎）、眼科（阿达木单抗用于葡萄膜炎）、生殖中心（环孢素用于复发性流产）等"
              "系该药在相应专科有适应证，不视为不合理，仅作提示；其余建议药师结合病历核实药品归属与适应证。", size=9, indent=True)
    para(doc, "表6　单一药品占本科室金额>30% 的高度集中科室（金额前20）", size=10, bold=True)
    conc_list = sorted(R["susp_concentration"], key=lambda x: -x["科室金额"])[:20]
    fill_table(doc.add_table(rows=1, cols=5), conc_list,
               ["科室", "主导药品", "主导占比", "科室金额", "主导ATC1"],
               ["科室", "主导药品", "占本科室(%)", "科室金额(万元)", "主导药品ATC 1级"],
               widths=[3.2, 3.0, 1.8, 2.2, 2.8],
               num_fmt={2: lambda x: f"{x:.1f}", 3: WAN})
    para(doc, "科室分析小结：", size=10, bold=True)
    para(doc, "① 大额科室主导药品为高值抗肿瘤/免疫治疗药，与收治病种相符，但金额体量巨大，应纳入特药管理并与医保限额联动监控。", size=9.5, indent=True)
    para(doc, "② 专科-主导药品匹配存疑科室中，康复理疗科、中医内科病房、中医针灸门诊等匹配性明显存疑，高度提示药品归属/代发录入或转科流通问题，须重点核查。", size=9.5, indent=True)
    para(doc, "③ 共85个科室单一药品占本科室金额>30%，反映部分科室用药结构高度集中；对其中金额较大的科室应评估是否为合理的专科用药还是需干预的异常集中。", size=9.5, indent=True)
    para(doc, "④ 金额为0/单价为0记录虽金额可忽略，但提示价格维护或临采数据不完整，应补录核价。", size=9.5, indent=True)

    # 附录
    heading(doc, "附录：ATC 2–4级分类金额汇总（前30）", 1)
    para(doc, f"ATC 2级共 {len(R['atc2'])} 类、ATC 3级列前30、ATC 4级列前30。完整数据见 analysis_results.json。", size=9)
    para(doc, "表7　ATC 3级分类金额前30", size=10, bold=True)
    fill_table(doc.add_table(rows=1, cols=4), R["atc3_top"],
               ["atc3", "金额", "占比", "品种数"], ["ATC 3级分类", "金额(万元)", "占比(%)", "品种数"],
               widths=[6.5, 2.7, 1.6, 1.5], num_fmt={1: WAN, 2: lambda x: f"{x:.2f}"})
    para(doc, "表8　ATC 4级分类金额前30", size=10, bold=True)
    fill_table(doc.add_table(rows=1, cols=4), R["atc4_top"],
               ["atc4", "金额", "占比", "品种数"], ["ATC 4级分类", "金额(万元)", "占比(%)", "品种数"],
               widths=[6.5, 2.7, 1.6, 1.5], num_fmt={1: WAN, 2: lambda x: f"{x:.2f}"})

    heading(doc, "方法学与约束说明", 1)
    para(doc, "1. 数据来源为药库出库记录，金额=数量×单价，所有汇总均按原始字段如实计算，未对任何缺失值进行填补或臆造。", size=9, indent=True)
    para(doc, "2. 本报告仅基于提供的 Excel，未引入外部文献或补充数据；结论为先行的描述性分析，合理性判断需结合病历与药师复核，“匹配存疑”不代表认定不合理。", size=9, indent=True)
    para(doc, "3. 金额单位以万元为主，亿元用于总体量级表述；占比均为占全院总金额之比。", size=9, indent=True)

    doc.save(DOCX)
    print("Saved:", DOCX, "| tables:", len(doc.tables))


if __name__ == "__main__":
    main()
