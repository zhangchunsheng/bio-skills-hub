#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gen_drug_target_report.py  —  oncology-lit-search 技能配套脚本
===============================================================

功能：将「药物 / 靶点专题综合检索」结果，按 SKILL V1.1.2 固定报告格式
      生成标准 .docx 报告。

这是「多源综合检索流程」的封装终点：
    检索 (PubMed + WebSearch + 五大会议 site: 搜索 + 管线核查)
        -> 将结果填充为 data.json (遵循本脚本 schema)
        -> 运行本脚本生成固定格式 Word 报告

────────────────────────────────────────────────────────────
固定报告结构（与 references/drug-target-report-template.md V1.1.1 一致）：

  首页(封面) : 6 个固定要素
               ①检索主题 ②检索时间 ③检索数据库及数据源范围
               ④文献或数据发表的时间范围 ⑤检索工具 ⑥检索关键词
  一、背景与流行病学
  二、临床数据汇总表（按临床阶段降序；多瘤种时按瘤种分表）
  三、重点药物临床数据详情（按临床阶段降序；III期布局固定；含耐药机制研究）
  四、非主流开发方向（不作重点）
  五、会议数据汇总（ASCO/ESMO/CSCO/AACR/WCLC 分组）
  六、总结与趋势判断（7 个固定子目录：治疗格局 / 疗效梯队 / 竞争态势 /
                          差异化策略 / 耐药挑战与应对 / 监管进展(注册策略) /
                          临床意义与展望）
  参考文献（置于报告最后；原 PubMed 核心文献列表以参考文献方式列出）

────────────────────────────────────────────────────────────
用法：
  # 生成报告
  python gen_drug_target_report.py --input data.json --output report.docx

  # 导出一份带示例数据的 JSON 骨架（照此填充即可）
  python gen_drug_target_report.py --sample sample_data.json

  # 仅校验 JSON 是否符合 schema（不生成文件）
  python gen_drug_target_report.py --input data.json --validate

依赖：pip install python-docx  (国内: -i https://pypi.tuna.tsinghua.edu.cn/simple)
"""

import argparse
import json
import os
import re
import sys
from docx import Document
from docx.shared import Pt, RGBColor, Cm
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT

# ----------------------------------------------------------------------------
# 字体与排版工具
# ----------------------------------------------------------------------------
CN_FONT = "宋体"
EN_FONT = "Calibri"
HEAD_FONT = "黑体"
COVER_TITLE_FONT = "微软雅黑"

HEADER_FILL = "2F5496"   # 表头深蓝
HEADER_TXT = "FFFFFF"
SUBHEAD_FILL = "D9E2F3"  # 子表头浅蓝
ALT_FILL = "F2F6FC"      # 隔行浅色


def _set_run_font(run, name=CN_FONT, size=11, bold=False, color=None):
    run.font.name = name
    run.font.size = Pt(size)
    run.font.bold = bold
    if color is not None:
        run.font.color.rgb = color
    rpr = run._element.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rpr.append(rfonts)
    rfonts.set(qn("w:eastAsia"), name)
    rfonts.set(qn("w:ascii"), EN_FONT if name == CN_FONT else name)
    rfonts.set(qn("w:hAnsi"), EN_FONT if name == CN_FONT else name)


def _shade_cell(cell, fill):
    if not fill:
        return
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), fill)
    tcPr.append(shd)


def _set_cell_text(cell, text, bold=False, size=10, fill=None, align=None):
    """写入单元格文本，支持 \n 换行；可选底色。"""
    cell.text = ""
    lines = str(text).split("\n")
    for i, line in enumerate(lines):
        p = cell.paragraphs[0] if i == 0 else cell.add_paragraph()
        p.paragraph_format.space_after = Pt(1)
        p.paragraph_format.space_before = Pt(1)
        if align is not None:
            p.alignment = align
        run = p.add_run(line)
        _set_run_font(run, name=CN_FONT, size=size, bold=bold)
    if fill is not None:
        _shade_cell(cell, fill)


def add_heading(doc, text, level=1):
    h = doc.add_heading(level=level)
    run = h.add_run(text)
    _set_run_font(run, name=HEAD_FONT, size=16 if level == 1 else 13, bold=True)
    return h


def add_para(doc, text, size=11, bold=False, color=None, space_after=4, indent=None):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(space_after)
    if indent:
        p.paragraph_format.left_indent = Pt(indent)
    run = p.add_run(text)
    _set_run_font(run, name=CN_FONT, size=size, bold=bold, color=color)
    return p


def add_bullet(doc, text, size=11, level=0):
    p = doc.add_paragraph(style="List Bullet")
    p.paragraph_format.left_indent = Pt(18 + level * 14)
    p.paragraph_format.space_after = Pt(2)
    run = p.add_run(text)
    _set_run_font(run, name=CN_FONT, size=size)
    return p


def make_table(doc, headers, rows, widths=None, header_fill=HEADER_FILL):
    table = doc.add_table(rows=1, cols=len(headers))
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = True
    # 表头
    for ci, htext in enumerate(headers):
        _set_cell_text(table.rows[0].cells[ci], htext, bold=True, size=10,
                       fill=header_fill, align=WD_ALIGN_PARAGRAPH.CENTER)
        run = table.rows[0].cells[ci].paragraphs[0].runs[0]
        run.font.color.rgb = RGBColor.from_string(HEADER_TXT)
    # 数据行
    for ri, row in enumerate(rows):
        cells = table.add_row().cells
        for ci, val in enumerate(row):
            fill = ALT_FILL if (ri % 2 == 1) else None
            _set_cell_text(cells[ci], val, size=10, fill=fill)
    # 列宽
    if widths:
        for ci, w in enumerate(widths):
            for r in table.rows:
                r.cells[ci].width = Cm(w)
    return table


# ----------------------------------------------------------------------------
# 临床阶段排序 & 瘤种分组
# ----------------------------------------------------------------------------
# 阶段越高，排序越靠前（降序）。返回数值：已上市=8, III期=7, ..., 临床前=1, 未知=0
_PHASES = ["已上市", "III期", "注册性临床", "II期", "I/II期", "I期", "IND", "临床前"]


def phase_rank(phase):
    p = (phase or "").replace(" ", "")
    for idx, key in enumerate(_PHASES):
        if key in p:
            return 8 - idx
    return 0


def primary_tumor(tumor_field):
    """取瘤种字段的第一个瘤种（用于分表）。"""
    if not tumor_field:
        return "其他"
    t = re.split(r"[\n,，、/]", str(tumor_field).strip())[0].strip()
    # 去掉括号备注
    t = re.sub(r"[（(].*?[)）]", "", t).strip()
    return t or "其他"


# ----------------------------------------------------------------------------
# 封面页（6 个固定要素）
# ----------------------------------------------------------------------------
COVER_ELEMENTS = [
    "检索主题", "检索时间", "检索数据库及数据源范围",
    "文献或数据发表的时间范围", "检索工具", "检索关键词",
]


def _as_text(v):
    if isinstance(v, list):
        return "；".join(str(x) for x in v)
    return str(v)


def build_cover(doc, meta):
    # 大标题
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(60)
    run = p.add_run(_as_text(meta.get("topic", "肿瘤靶点临床文献检索报告")))
    _set_run_font(run, name=COVER_TITLE_FONT, size=22, bold=True,
                  color=RGBColor.from_string("1F3864"))
    p2 = doc.add_paragraph()
    p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p2.add_run("（药物 / 靶点专题 · 固定格式 V1.1.2）")
    _set_run_font(run, name=COVER_TITLE_FONT, size=12, bold=False,
                  color=RGBColor.from_string("808080"))

    doc.add_paragraph()
    meta_rows = [
        ("检索主题", _as_text(meta.get("topic", ""))),
        ("检索时间", _as_text(meta.get("search_date", ""))),
        ("检索数据库及数据源范围", _as_text(meta.get("search_scope", ""))),
        ("文献或数据发表的时间范围", _as_text(meta.get("date_range", ""))),
        ("检索工具", _as_text(meta.get("tools", ""))),
        ("检索关键词", _as_text(meta.get("keywords", ""))),
    ]
    make_table(doc, ["检索元数据", "内容"], [[k, v] for k, v in meta_rows],
               widths=[3.6, 12.4])
    doc.add_page_break()


# ----------------------------------------------------------------------------
# 各章节
# ----------------------------------------------------------------------------
SUMMARY_HEADERS = ["品种", "开发企业", "最新进展", "瘤种", "主要有效性结果", "主要安全性结果"]
CONF_HEADERS = ["摘要编号", "药物/疗法", "瘤种", "关键数据", "专场"]
PUBMED_HEADERS = ["PMID", "DOI", "文献类型", "英文标题", "第一作者", "期刊", "年份"]


def build_background(doc, data):
    add_heading(doc, "一、背景与流行病学", level=1)
    bg = data.get("background", "")
    if not bg:
        add_para(doc, "（暂无背景与流行病学信息）", size=10,
                 color=RGBColor.from_string("808080"))
        return
    for para in re.split(r"\n\s*\n", bg.strip()):
        para = para.strip()
        if para:
            add_para(doc, para, size=11, space_after=6)


def _summary_rows(rows):
    out = []
    for d in rows:
        out.append([
            d.get("drug", ""), d.get("company", ""), d.get("progress", ""),
            d.get("tumor", d.get("tumors", "")), d.get("efficacy", ""),
            d.get("safety", ""),
        ])
    return out


def build_summary(doc, data):
    target = data.get("meta", {}).get("target") or data.get("meta", {}).get("topic", "该靶点")
    add_heading(doc, "二、临床数据汇总表", level=1)
    add_para(doc, f"检索主题：{target}", size=10, bold=True,
             color=RGBColor.from_string("595959"), space_after=4)

    rows = data.get("summary_table", {}).get("rows", [])
    if not rows:
        add_para(doc, "（暂无临床数据汇总）", size=10,
                 color=RGBColor.from_string("808080"))
        return

    def sort_key(r):
        ph = r.get("phase") or r.get("progress", "")
        return phase_rank(ph)

    # 主表：全部品种，按临床阶段降序
    ordered = sorted(rows, key=sort_key, reverse=True)
    add_para(doc, "（一）总体汇总（按临床阶段降序）", size=11, bold=True, space_after=3)
    make_table(doc, SUMMARY_HEADERS, _summary_rows(ordered),
               widths=[2.6, 2.4, 2.8, 2.0, 3.0, 3.0])

    # 多瘤种时，按瘤种分别再增加列表
    tumors = {}
    for r in ordered:
        t = primary_tumor(r.get("tumor", r.get("tumors", "")))
        tumors.setdefault(t, []).append(r)
    if len(tumors) >= 2:
        doc.add_paragraph()
        add_para(doc, "（二）按瘤种分列", size=11, bold=True, space_after=3)
        for t, trs in tumors.items():
            add_para(doc, f"{t}（按临床阶段降序，{len(trs)} 个品种）",
                     size=10.5, bold=True, color=RGBColor.from_string("2F5496"),
                     space_after=2)
            make_table(doc, SUMMARY_HEADERS, _summary_rows(trs),
                       widths=[2.6, 2.4, 2.8, 2.0, 3.0, 3.0])

    add_para(doc,
             "注：不同品种数据来源试验、基线、联合方案各异，不可直接横向比较；"
             "有效性保留原始数字（ORR/DCR/mPFS/mOS 等），安全性以 ≥3 级 TRAE 发生率及主要 AE 类型为主。",
             size=9, color=RGBColor.from_string("808080"), space_after=6)


def _drug_sort_key(d):
    ph = d.get("phase") or ""
    if not ph:
        # 尝试从名称后缀匹配
        pass
    return phase_rank(ph)


def build_drug_details(doc, data):
    add_heading(doc, "三、重点药物临床数据详情", level=1)
    add_para(doc, "（按临床阶段降序排列；已进入 / 计划 III 期者固定呈现 III 期 / 注册临床设计）",
             size=9.5, color=RGBColor.from_string("808080"), space_after=4)
    details = data.get("drug_details", [])
    if not details:
        add_para(doc, "（暂无重点药物详情）", size=10,
                 color=RGBColor.from_string("808080"))
        return
    details = sorted(details, key=_drug_sort_key, reverse=True)

    for d in details:
        add_heading(doc, f"{d.get('name','')} — {d.get('company','')}", level=2)
        if d.get("mechanism"):
            add_para(doc, f"机制：{d['mechanism']}", size=10.5, space_after=3)
        if d.get("pi"):
            add_para(doc, f"主要研究者（PI）：{d['pi']}", size=10.5, space_after=3)
        if d.get("trial_reg"):
            add_para(doc, f"试验注册：{d['trial_reg']}", size=10.5, space_after=3)
        for block in d.get("content", []):
            if "h" in block and block["h"]:
                add_para(doc, block["h"], size=10.5, bold=True, space_after=2)
            for b in block.get("bullets", []):
                add_bullet(doc, b, size=10.5)
            if "p" in block and block["p"]:
                add_para(doc, block["p"], size=10.5, space_after=3)

    # 耐药机制研究（保留该部分内容，作为本节子项）
    res = data.get("resistance_mechanisms", [])
    if res:
        doc.add_paragraph()
        add_heading(doc, "耐药机制研究", level=2)
        for it in res:
            add_bullet(doc, it, size=11)


def build_non_mainstream(doc, data):
    add_heading(doc, "四、非主流开发方向（不作为重点）", level=1)
    nm = data.get("non_mainstream", {})
    analysis = nm.get("analysis", "") if isinstance(nm, dict) else ""
    if analysis:
        for para in re.split(r"\n\s*\n", analysis.strip()):
            para = para.strip()
            if para:
                add_para(doc, para, size=11, space_after=6)
    rows = nm.get("rows", []) if isinstance(nm, dict) else []
    if rows:
        doc.add_paragraph()
        add_para(doc, "非小分子模态在研汇总", size=11, bold=True, space_after=3)
        make_table(doc, SUMMARY_HEADERS, _summary_rows(rows),
                   widths=[2.6, 2.4, 2.8, 2.0, 3.0, 3.0])


def build_conference(doc, data):
    add_heading(doc, "五、会议数据汇总", level=1)
    confs = data.get("conference_data", [])
    if not confs:
        add_para(doc, "（本次检索未覆盖相关会议数据）", size=10,
                 color=RGBColor.from_string("808080"))
        return
    for c in confs:
        title = c.get("conf", "会议")
        add_heading(doc, title, level=2)
        if c.get("note"):
            add_para(doc, c["note"], size=10,
                     color=RGBColor.from_string("808080"), space_after=3)
        items = c.get("items", [])
        if items:
            rows = [[it.get("abstract", ""), it.get("drug", ""), it.get("tumor", ""),
                     it.get("key_data", ""), it.get("session", "")] for it in items]
            make_table(doc, CONF_HEADERS, rows, widths=[2.2, 3.0, 2.0, 6.0, 1.8])
        else:
            add_para(doc, "（该会议暂无结构化摘要数据）", size=10,
                     color=RGBColor.from_string("808080"))


# 六、总结与趋势判断 —— 7 个固定子目录（按用户指定顺序与标题）
# 每项内容需在 data.json 的 conclusion[<key>] 中以 {paras:[段落], bullets:[要点]} 提供，
# 段落应体现归纳概括能力（与标准疗法对照、梯队、态势、差异化、耐药、注册、展望）。
CONCLUSION_SECTIONS = [
    ("treatment_landscape", "1、治疗格局"),
    ("efficacy_tiers", "2、疗效梯队"),
    ("competitive", "3、竞争态势"),
    ("differentiation", "4、差异化策略"),
    ("resistance", "5、耐药挑战与应对"),
    ("regulatory", "6、监管进展（注册策略）"),
    ("outlook", "7、临床意义与展望"),
]


def _render_conclusion_item(doc, item):
    if not isinstance(item, dict):
        return
    for p in item.get("paras", []) or []:
        add_para(doc, p, size=11, space_after=5)
    for b in item.get("bullets", []) or []:
        add_bullet(doc, b, size=11)


def build_conclusion(doc, data):
    add_heading(doc, "六、总结与趋势判断", level=1)
    conclusion = data.get("conclusion", {})
    if not conclusion:
        add_para(doc, "（暂无）", size=10, color=RGBColor.from_string("808080"))
        return
    # 兼容旧版 [{title, points}] / [str] 形态
    if isinstance(conclusion, list):
        for item in conclusion:
            if isinstance(item, dict):
                add_para(doc, item.get("title", ""), size=11, bold=True, space_after=2)
                for pt in item.get("points", []):
                    add_bullet(doc, pt, size=11)
            else:
                add_bullet(doc, str(item), size=11)
        return
    # 新版：7 个固定子目录
    for key, title in CONCLUSION_SECTIONS:
        item = conclusion.get(key)
        if not item:
            continue
        add_heading(doc, title, level=2)
        _render_conclusion_item(doc, item)


def build_references(doc, data):
    """原 PubMed 核心文献列表，置于报告最后，以参考文献（编号）方式列出。"""
    add_heading(doc, "参考文献", level=1)
    refs = data.get("pubmed_refs", [])
    if not refs:
        add_para(doc, "（暂无 PubMed 核心文献）", size=10,
                 color=RGBColor.from_string("808080"))
        return
    for i, r in enumerate(refs, start=1):
        parts = [
            f"[{i}] {r.get('first_author','')} 等.",
            r.get("title", ""),
            f"{r.get('journal','')}, {r.get('year','')}.",
        ]
        if r.get("doi"):
            parts.append(f"DOI: {r['doi']}.")
        if r.get("pmid"):
            parts.append(f"PMID: {r['pmid']}.")
        if r.get("type"):
            parts.append(f"（{r['type']}）")
        add_para(doc, " ".join(p for p in parts if p), size=10, space_after=3)


# ----------------------------------------------------------------------------
# 主流程
# ----------------------------------------------------------------------------
def generate(data, output_path):
    doc = Document()
    # 默认正文字体
    style = doc.styles["Normal"]
    style.font.name = CN_FONT
    style.font.size = Pt(11)
    rpr = style.element.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rpr.append(rfonts)
    rfonts.set(qn("w:eastAsia"), CN_FONT)

    build_cover(doc, data.get("meta", {}))
    build_background(doc, data)
    build_summary(doc, data)
    build_drug_details(doc, data)
    build_non_mainstream(doc, data)
    build_conference(doc, data)
    build_conclusion(doc, data)
    build_references(doc, data)   # 报告最后

    out_dir = os.path.dirname(os.path.abspath(output_path))
    os.makedirs(out_dir, exist_ok=True)
    doc.save(output_path)
    return output_path


# ----------------------------------------------------------------------------
# 校验
# ----------------------------------------------------------------------------
REQUIRED_TOP = ["meta", "background", "summary_table", "drug_details",
                "non_mainstream", "conference_data",
                "resistance_mechanisms", "pubmed_refs", "conclusion"]
META_REQUIRED = ["topic", "search_date", "search_scope",
                 "date_range", "tools", "keywords"]


def validate(data):
    errors = []
    for k in REQUIRED_TOP:
        if k not in data:
            errors.append(f"缺少顶层字段: {k}")
    meta = data.get("meta", {})
    for k in META_REQUIRED:
        if k not in meta:
            errors.append(f"meta 缺少字段: {k}")
    # 章节二至少一张表非空
    st = data.get("summary_table", {})
    if not isinstance(st, dict) or not st.get("rows"):
        errors.append("临床数据汇总表为空（summary_table.rows 无数据）")
    # 参考文献至少 1 篇
    if not data.get("pubmed_refs"):
        errors.append("参考文献（PubMed 核心文献）为空")
    return errors


# ----------------------------------------------------------------------------
# 示例数据
# ----------------------------------------------------------------------------
def sample_json():
    return {
        "meta": {
            "topic": "示例：KRAS G12D 靶点药物在胰腺癌的临床数据",
            "target": "KRAS G12D",
            "search_date": "2026-07-17",
            "search_scope": "PubMed (NCBI E-utilities)；ASCO 2026 年会摘要库；AACR 2026；ESMO 2025；CSCO 2025；WebSearch 检索",
            "date_range": "2023-01-01 至 2026-07-17",
            "tools": "PubMed E-utilities API；WebSearch；WebFetch",
            "keywords": "KRAS G12D；pancreatic cancer；inhibitor；clinical trial；胰腺癌；临床试验"
        },
        "background": "KRAS G12D 是胰腺癌（PDAC）中最常见的驱动突变，约 40% 的 PDAC 携带该突变……\n\n目前 PDAC 五年生存率不足 13%，后线治疗 ORR 常低于 10%、mOS 约 6 个月，存在巨大未满足需求。",
        "summary_table": {
            "rows": [
                {"drug": "示例药A\n(RMC-xxx)", "company": "示例公司", "progress": "III 期\n(2026.06 启动)",
                 "phase": "III期", "tumor": "PDAC", "efficacy": "ORR 63.3%\nDCR 93.3%",
                 "safety": "≥3级TRAE 87.1%\n无停药/死亡"}
            ]
        },
        "drug_details": [
            {
                "name": "示例药A", "company": "示例公司", "phase": "III期",
                "mechanism": "高选择性 KRAS G12D 抑制剂，结合 Switch-II 口袋，作用于 ON/OFF 双态。",
                "pi": "某某医院 某某教授",
                "trial_reg": "CTR2024xxxx / NCT06xxxxxx",
                "content": [
                    {"h": "ASCO 2026 口头报告（Abstract xxxx，数据截止 2026-04-05）",
                     "bullets": ["入组情况：56 例，66% 胰腺癌",
                                 "有效性：ORR 41.9%，DCR 93.5%",
                                 "安全性：≥3级 TRAE 32.8%，无 4-5 级"]},
                    {"h": "III 期临床试验（2026 年启动）",
                     "bullets": ["设计：单药 vs 化疗，2L+ PDAC", "计划入组 360 例", "主要终点：PFS 和 OS"]},
                    {"p": "要点概括：示例药A 是全球第 N 个进入 III 期的 KRAS G12D 抑制剂……"}
                ]
            }
        ],
        "non_mainstream": {
            "analysis": "非小分子模态（TCR-T / siRNA / 疫苗 / 外泌体 / 抗体等）多为辅助或维持治疗场景，不作本次重点。",
            "rows": [
                {"drug": "示例疫苗", "company": "某机构", "progress": "I 期",
                 "tumor": "PDAC（术后）", "efficacy": "T细胞应答 11/12", "safety": "G1-2"}
            ]
        },
        "conference_data": [
            {"conf": "ASCO 2026", "note": "美国临床肿瘤学会年会，2026 年 6 月",
             "items": [{"abstract": "3007", "drug": "示例药A", "tumor": "PDAC",
                        "key_data": "ORR 41.9%, DCR 93.5%", "session": "Oral"}]}
        ],
        "resistance_mechanisms": [
            "旁路激活：RTK / MAPK 再激活导致继发性耐药。",
            "二次突变：KRAS 代偿性突变或等位基因转换。",
            "表型转化：EMT 与谱系可塑性。",
            "监测手段：ctDNA 动态监测用于早期耐药预警。"
        ],
        "pubmed_refs": [
            {"pmid": "38123456", "doi": "10.1200/JCO.2024.001", "type": "Clinical Trial",
             "title": "Example phase III trial of KRAS G12D inhibitor in PDAC", "first_author": "Smith J",
             "journal": "J Clin Oncol", "year": "2026"}
        ],
        "conclusion": {
            "treatment_landscape": {
                "paras": ["G12D 是胰腺癌（PDAC）最常见驱动突变（约 40%），而 PDAC 后线治疗 ORR 常 <10%、mOS 约 6 个月，长期缺乏靶向治疗。",
                          "KRAS G12D 抑制剂直接靶向主导驱动变异：后线单药 ORR 达 20-42%（历史化疗 <10%），联合化疗一线 ORR 61-82%（化疗单药约 30-40%），后线 mOS 从约 6.7 个月延长至 13.2 个月（HR 0.40），实现从「仅化疗」到「靶向+化疗」的范式转变。"],
                "bullets": ["对照标准疗法：2L+ 单药 ORR 20-42% vs 化疗 <10%；1L 联合 ORR 61-82% vs 化疗单药 30-40%。",
                            "尚未获批、跨试验不可直接横比，长期获益与耐药仍需验证。"]
            },
            "efficacy_tiers": {
                "paras": ["按疗效梯队划分：一线联合化疗为第一梯队（ORR 60-82%），后线单药为第二梯队（ORR 37-52%），早期单药为第三梯队（ORR 20-37%）。"],
                "bullets": ["NSCLC 单药 ORR：GFH375 68.8% > Zoldonrasib 61% > RNK08954 42.9% > Setidegrasib 36% > HRS-4642 23.7%（基线不同，不可横比）。",
                            "PDAC（核心适应症）：HRS-4642+GA 一线 ORR 63.3% > GFH375 二线 52% > DN022150 二线 41.9% > Daraxonrasib 二线 mOS 13.2m > Zoldonrasib 30% > HRS-4642 单药 20.8%。"]
            },
            "competitive": {
                "paras": ["全球至少 8 款 KRAS G12D 小分子抑制剂已公开临床数据，中国原研（恒瑞、科睿、劲方）占据近半席位；截至 2026-07 已有 3 款进入 III 期，但全球尚无获批药物。"],
                "bullets": ["中美双轨：美国（Revolution/Daraxonrasib 泛RAS、Astellas/Zoldonrasib、Incyte/INCB161734） vs 中国（恒瑞、科睿、劲方）。",
                            "模态分野：G12D 选择性小分子（主流）、泛 RAS（Daraxonrasib）、PROTAC 降解剂（Setidegrasib/ASP3082）、非小分子（TCR-T/siRNA/疫苗）。"]
            },
            "differentiation": {
                "paras": ["差异化来自选择性、给药方式、联合定位与注册地理布局。"],
                "bullets": ["选择性：G12D 选择性 vs 泛 RAS（更广谱但毒性更高）；ON/OFF 双态结合（DN022150）vs Switch-II 口袋。",
                            "给药：每周一次 IV（DN022150）vs 口服（多数）；便捷性差异。",
                            "定位：1L 化疗联合（HRS-4642+GA）vs 2L 单药 vs 维持；适应症优先 PDAC / NSCLC(BTD) / CCA。",
                            "注册：中国 NMPA 快速跟进（大 PDAC 人群）+ 美国 FDA BTD/快速通道，双轨加速全球可及。"]
            },
            "resistance": {
                "paras": ["耐药是 G12D 靶向长期获益的主要威胁，机制研究正加速以指导联合方案设计。"],
                "bullets": ["机制：旁路激活（RTK/MAPK 再激活）、二次 KRAS 突变/等位基因转换、表型可塑性（EMT）。",
                            "新发现：CDK8、UPR/MEK-ERK、EGFR/HER2 反馈、USP20 去泛素化酶。",
                            "应对：联合下游（MEK/ERK）或上游（EGFR/HER2）抑制剂；ctDNA 动态监测早期预警；序贯/轮换联合；PROTAC 降解剂克服部分耐药。"]
            },
            "regulatory": {
                "paras": ["注册策略呈中美双轨推进，多项突破性/快速通道认定加速上市路径。"],
                "bullets": ["Daraxonrasib（泛RAS）：III 期已完成，NEJM 同步发表，FDA 申报准备中。",
                            "Zoldonrasib：FDA 突破性疗法（2026.01，NSCLC），注册性临床推进；NSCLC ORR 61% 远超标准治疗 10-15%，mPFS 11.1 个月巩固注册路径优势。",
                            "HRS-4642：中国 III 期启动（2025.11，一线 PDAC），NMPA 路径；联合 GA 一线 ORR 63.3%。",
                            "DN022150：中国 III 期启动（2026.06，NCT07689539，2L+ PDAC，360 例，PFS+OS 双主要终点）。",
                            "GFH375/VS-7375：中国 III 期「麒麟-翼01」（后线），美国 I/IIa；Setidegrasib（PROTAC）NEJM 发表、注册性临床推进。"]
            },
            "outlook": {
                "paras": ["KRAS G12D 抑制剂是 PDAC 精准治疗的首个靶向突破口，临床意义显著。"],
                "bullets": ["2L mOS 翻倍（Daraxonrasib 13.2 vs 6.7m）具临床意义；推动 PDAC 从「仅化疗」迈向精准肿瘤学。",
                            "展望：预计 2027-2028 年首个 G12D 靶向药获批；1L 联合化疗有望成新标准；ctDNA 生物标志物指导患者筛选；合理联合管理耐药；向 NSCLC/CCA 拓展；中国原研全球领跑。"]
            }
        }
    }


# ----------------------------------------------------------------------------
# CLI
# ----------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description="生成药物/靶点专题固定格式检索报告 (SKILL V1.1.2)")
    ap.add_argument("--input", help="数据 JSON 路径")
    ap.add_argument("--output", default="report.docx", help="输出 docx 路径")
    ap.add_argument("--sample", help="导出示例 JSON 骨架到指定路径")
    ap.add_argument("--validate", action="store_true", help="仅校验 JSON，不生成文件")
    args = ap.parse_args()

    if args.sample:
        with open(args.sample, "w", encoding="utf-8") as f:
            json.dump(sample_json(), f, ensure_ascii=False, indent=2)
        print(f"[OK] 示例数据已写入: {args.sample}")
        return 0

    if not args.input:
        print("[用法] --input data.json --output report.docx  或  --sample sample.json", file=sys.stderr)
        return 2

    with open(args.input, "r", encoding="utf-8") as f:
        data = json.load(f)

    errors = validate(data)
    if errors:
        print("[校验失败]", file=sys.stderr)
        for e in errors:
            print("  - " + e, file=sys.stderr)
        if not args.validate:
            print("（使用 --validate 仅校验；如需强制生成请补全上述字段）", file=sys.stderr)
        return 1
    if args.validate:
        print("[OK] JSON 校验通过，符合 V1.1.2 schema。")
        return 0

    out = generate(data, args.output)
    print(f"[OK] 报告已生成: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
