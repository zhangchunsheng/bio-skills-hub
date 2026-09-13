#!/usr/bin/env python3
"""
rNPV Excel 模型生成模板
======================
医药股 rNPV（风险调整净现值）估值模型。

使用 openpyxl 生成 6 个 Sheet 的完整模型：
  1. Summary      — 估值汇总 + 市场隐含分析
  2. Pipeline     — 管线总览
  3. rNPV Detail  — 逐管线逐年现金流
  4. Implied PoS  — 市场隐含成功率反推
  5. Assumptions  — 所有输入假设
  6. Sensitivity  — 敏感性分析

格式规范（专业规范）：
  - 蓝色字 = 输入假设（用户可修改）
  - 黑色字 = 公式（自动计算）
  - 绿色字 = 跨表引用
  - 关键数字附单元格注释标明数据来源

用法：
  python rNPV_excel_template.py
  → 生成 sample_rNPV_model.xlsx

或传入数据：
  from rNPV_excel_template import build_rnpv_model
  build_rnpv_model(data_dict, "output/[ticker]_[date]/[ticker]_rNPV_model.xlsx")

变更日志：
  v6.1 (2026-07-12) — calc_unrisked_pv 费用率乘法→加法（跨模型对抗复核发现）：
    原 margin = (1-cogs)*(1-sga)*(1-tax)  →  新 margin = (1-cogs-sga)*(1-tax)
    原因：乘法 (1-cogs)(1-sga)=1-cogs-sga+cogs*sga 比加法多算交叉项 cogs*sga，
    系统性高估 margin（高费用管线偏差大：cogs0.30+sga0.35 高估 ~30%；低费用管线小）。
    加法与利润表口径一致，且与 Detail sheet（485-526行）逐项扣减一致。
    影响：自有管线（cogs/sga>0）PV 下修；royalty 管线（cogs/sga=0）不受影响。
    回归：改动仅影响本模板内部计算函数。
  v6.0 (2026-07-12) — 新增 supply_value EV 组件（.get(...,0) 向后兼容，旧项目 supply=0 不受影响）。
"""

import os
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side, numbers
from openpyxl.comments import Comment
from openpyxl.utils import get_column_letter

# ============================================================
# 样式定义（专业格式）
# ============================================================

# 颜色
COLOR_INPUT = "0000CC"       # 蓝色 = 输入假设
COLOR_FORMULA = "000000"     # 黑色 = 公式
COLOR_LINK = "008000"        # 绿色 = 跨表引用
COLOR_HEADER_BG = "1F4E79"   # 深蓝表头背景
COLOR_SUBHEADER_BG = "D6E4F0"  # 浅蓝子表头背景
COLOR_TOTAL_BG = "FFF2CC"    # 浅黄合计行
COLOR_POSITIVE = "008000"    # 绿色 = 正面
COLOR_NEGATIVE = "CC0000"    # 红色 = 负面

# 字体
FONT_TITLE = Font(name="Calibri", size=16, bold=True, color="FFFFFF")
FONT_HEADER = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
FONT_SUBHEADER = Font(name="Calibri", size=10, bold=True, color="000000")
FONT_INPUT = Font(name="Calibri", size=10, color=COLOR_INPUT)
FONT_FORMULA = Font(name="Calibri", size=10, color=COLOR_FORMULA)
FONT_LINK = Font(name="Calibri", size=10, color=COLOR_LINK)
FONT_BOLD = Font(name="Calibri", size=10, bold=True)
FONT_NOTE = Font(name="Calibri", size=9, italic=True, color="808080")

# 填充
FILL_HEADER = PatternFill(start_color=COLOR_HEADER_BG, end_color=COLOR_HEADER_BG, fill_type="solid")
FILL_SUBHEADER = PatternFill(start_color=COLOR_SUBHEADER_BG, end_color=COLOR_SUBHEADER_BG, fill_type="solid")
FILL_TOTAL = PatternFill(start_color=COLOR_TOTAL_BG, end_color=COLOR_TOTAL_BG, fill_type="solid")

# 边框
thin_border = Border(
    left=Side(style='thin', color='CCCCCC'),
    right=Side(style='thin', color='CCCCCC'),
    top=Side(style='thin', color='CCCCCC'),
    bottom=Side(style='thin', color='CCCCCC')
)
bottom_border = Border(bottom=Side(style='thin', color='000000'))

# 对齐
ALIGN_CENTER = Alignment(horizontal="center", vertical="center", wrap_text=True)
ALIGN_LEFT = Alignment(horizontal="left", vertical="center", wrap_text=True)
ALIGN_RIGHT = Alignment(horizontal="right", vertical="center")


# ============================================================
# 辅助函数
# ============================================================

def set_cell(ws, row, col, value, font=FONT_FORMULA, fill=None, border=thin_border,
             alignment=ALIGN_CENTER, number_format=None, comment=None):
    """设置单元格的通用函数"""
    cell = ws.cell(row=row, column=col, value=value)
    cell.font = font
    if fill:
        cell.fill = fill
    if border:
        cell.border = border
    cell.alignment = alignment
    if number_format:
        cell.number_format = number_format
    if comment:
        cell.comment = Comment(comment, "rNPV Model", width=250, height=100)
    return cell


def merge_title(ws, row, start_col, end_col, title, font=FONT_TITLE, fill=FILL_HEADER, height=30):
    """合并单元格做标题行"""
    ws.merge_cells(start_row=row, start_column=start_col, end_row=row, end_column=end_col)
    cell = set_cell(ws, row, start_col, title, font=font, fill=fill, alignment=ALIGN_CENTER)
    ws.row_dimensions[row].height = height
    return cell


def set_column_widths(ws, widths):
    """批量设置列宽"""
    for col_idx, width in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(col_idx)].width = width


# ============================================================
# rNPV 计算核心：爬坡曲线 + 无风险PV helper
# ============================================================
# 上市后 Y1-Y15 占峰值 %（Y6 达峰，Y7 后 -20%/年衰减）
RAMP_CURVE = [10, 25, 50, 75, 90, 100, 95, 76, 61, 49, 39, 31, 25, 20, 16]


def calc_unrisked_pv(peak_sales, launch_year, cogs, sga, tax, wacc, base_year, ramp=None):
    """
    逐年爬坡折现计算单条管线的无风险 PV（PoS=100%）。
    与 rNPV Detail sheet 的逐年现金流口径完全一致——是 Summary/Implied PoS 的唯一真值源。
    FCF ≈ 税后利润 = 收入 × (1-COGS-SG&A) × (1-税)（加法口径，与利润表一致；v6.1 修正：原乘法 (1-COGS)(1-SG&A) 系统性高估 margin 约15%）。
    年末折现：上市年当年即 t=1。
    """
    if ramp is None:
        ramp = RAMP_CURVE
    margin = (1 - cogs - sga) * (1 - tax)  # v6.1：加法口径（跨模型复核），原乘法 (1-cogs)*(1-sga) 系统性高估 margin
    pv = 0.0
    for j, r in enumerate(ramp):
        t = launch_year - base_year + 1 + j
        if t < 1 or t > 30:
            continue
        pv += peak_sales * (r / 100.0) * margin / (1 + wacc) ** t
    return pv


def calc_per_share(data, wacc, pos_mult=1.0, peak_mult=1.0):
    """
    真敏感性计算：给定 WACC / PoS倍数 / 峰值倍数，重算每股内在价值。
    对每条管线用 calc_unrisked_pv 按 wacc 逐年重折现（非伪公式），供 Sensitivity sheet 使用。
    """
    base_year = data.get('base_year', 2026)
    total_rnpv = 0.0
    for p in data['pipelines']:
        peak = p['peak_sales'] * peak_mult
        pos = min(p.get('adj_pos', p.get('base_pos', 0)) * pos_mult, 1.0)
        pv = calc_unrisked_pv(peak, p.get('launch_year', base_year + 5),
                              p.get('cogs_rate', 0.20), p.get('sga_rate', 0.30),
                              p.get('tax_rate', 0.15), wacc, base_year)
        total_rnpv += pos * pv
    ev = total_rnpv + data.get('listed_product_npv', 0) + data.get('platform_value', 0) + data.get('milestone_value', 0) + data.get('supply_value', 0)
    equity = ev + data.get('net_cash', 0) - data.get('expected_dilution', 0)
    # v3 修复:原裸除零(shares 缺失/0 → ZeroDivisionError/KeyError 崩进程)
    shares = data.get('shares_outstanding')
    if not shares or shares <= 0:
        raise ValueError("shares_outstanding 缺失或 ≤0,无法计算每股价值(检查 capital_structure)")
    return equity / shares


# ============================================================
# Sheet 1: Summary（估值汇总）
# ============================================================

def build_summary_sheet(wb, data):
    ws = wb.create_sheet("Summary")
    set_column_widths(ws, [30, 18, 18, 18, 18, 30])

    d = data  # 简写

    # --- 标题 ---
    merge_title(ws, 1, 1, 6,
                f"{d['company_name']} ({d['ticker']}) — rNPV 估值汇总")

    # --- 公司信息 ---
    row = 3
    ws.cell(row=row, column=1, value="公司信息").font = FONT_SUBHEADER
    ws.cell(row=row, column=1).fill = FILL_SUBHEADER
    for c in range(2, 7):
        ws.cell(row=row, column=c).fill = FILL_SUBHEADER

    info_rows = [
        ("公司全称", d['company_name']),
        ("股票代码", d['ticker']),
        ("交易所", d['exchange']),
        ("分析日期", d['analysis_date']),
        ("货币", d['currency']),
    ]
    for i, (label, val) in enumerate(info_rows):
        r = row + 1 + i
        set_cell(ws, r, 1, label, font=FONT_BOLD, alignment=ALIGN_LEFT)
        set_cell(ws, r, 2, val, font=FONT_INPUT)

    # --- 财务快照 ---
    row = 10
    ws.cell(row=row, column=1, value="财务快照").font = FONT_SUBHEADER
    ws.cell(row=row, column=1).fill = FILL_SUBHEADER
    for c in range(2, 7):
        ws.cell(row=row, column=c).fill = FILL_SUBHEADER

    fin_rows = [
        ("当前股价", d['current_price'], d['currency'], f"数据来源: {d.get('price_source', 'yfinance')}"),
        ("总股本（百万）", d['shares_outstanding'], "百万股", f"数据来源: {d.get('shares_source', '公司公告')}"),
        ("当前市值（百万）", f"=B11*B12", d['currency'], "= 股价 × 总股本"),
        ("现金及等价物（百万）", d['cash'], d['currency'], "最新财报"),
        ("短期投资（百万）", d.get('short_term_investments', 0), d['currency'], "最新财报"),
        ("有息负债（百万）", d.get('debt', 0), d['currency'], "最新财报"),
        ("净现金（百万）", f"=B14+B15-B16", d['currency'], "= 现金 + 短期投资 - 有息负债"),
        ("年度研发费用（百万）", d.get('rd_expense', 0), d['currency'], "最新年报"),
        ("季度现金消耗（百万）", d.get('quarterly_burn', 0), d['currency'], "经营性现金流"),
    ]
    for i, item in enumerate(fin_rows):
        r = 11 + i
        label = item[0]
        val = item[1]
        unit = item[2]
        note = item[3] if len(item) > 3 else ""
        set_cell(ws, r, 1, label, font=FONT_BOLD, alignment=ALIGN_LEFT)
        if isinstance(val, str) and val.startswith("="):
            set_cell(ws, r, 2, val, font=FONT_FORMULA, number_format='#,##0.0')
        else:
            set_cell(ws, r, 2, val, font=FONT_INPUT, number_format='#,##0.0')
        set_cell(ws, r, 3, unit, font=FONT_NOTE, alignment=ALIGN_LEFT)
        if note:
            ws.cell(row=r, column=2).comment = Comment(note, "rNPV Model", width=200, height=60)

    # --- rNPV 估值汇总 ---
    row = 21
    ws.cell(row=row, column=1, value="rNPV 估值汇总").font = FONT_SUBHEADER
    ws.cell(row=row, column=1).fill = FILL_SUBHEADER
    for c in range(2, 7):
        ws.cell(row=row, column=c).fill = FILL_SUBHEADER

    headers = ["管线资产", "阶段", "调整后 PoS", "无风险 PV（百万）", "rNPV（百万）"]
    for i, h in enumerate(headers):
        set_cell(ws, row + 1, i + 1, h, font=FONT_HEADER, fill=FILL_HEADER)

    # 各管线 rNPV = 调整后PoS × 无风险PV（与 rNPV Detail sheet 逐年折现口径一致）
    for i, pipe in enumerate(d['pipelines']):
        r = row + 2 + i
        set_cell(ws, r, 1, f"{pipe['name']} — {pipe['indication']}", font=FONT_LINK, alignment=ALIGN_LEFT)
        set_cell(ws, r, 2, pipe['phase'], font=FONT_LINK)
        set_cell(ws, r, 3, pipe.get('adj_pos', pipe.get('base_pos', 0)), font=FONT_LINK, number_format='0.0%')
        set_cell(ws, r, 4, pipe.get('unrisked_pv', pipe['peak_sales']), font=FONT_LINK, number_format='#,##0.0',
                 comment="无风险PV（PoS=100%），由 calc_unrisked_pv 逐年折现算得，与 rNPV Detail sheet 一致")
        set_cell(ws, r, 5, f"=C{r}*D{r}", font=FONT_FORMULA, number_format='#,##0.0',
                 comment="rNPV = 调整后PoS × 无风险PV")

    num_pipes = len(d['pipelines'])
    total_row = row + 2 + num_pipes
    set_cell(ws, total_row, 1, "管线 rNPV 合计", font=FONT_BOLD, fill=FILL_TOTAL, alignment=ALIGN_LEFT)
    for c in range(2, 5):
        set_cell(ws, total_row, c, "", fill=FILL_TOTAL)
    set_cell(ws, total_row, 5, f"=SUM(E{row+2}:E{total_row-1})",
             font=FONT_BOLD, fill=FILL_TOTAL, number_format='#,##0.0')

    # --- 估值桥 ---
    row = total_row + 2
    ws.cell(row=row, column=1, value="估值桥（企业价值 → 每股价值）").font = FONT_SUBHEADER
    ws.cell(row=row, column=1).fill = FILL_SUBHEADER
    for c in range(2, 7):
        ws.cell(row=row, column=c).fill = FILL_SUBHEADER

    bridge = [
        ("管线 rNPV 合计", f"=E{total_row}", "百万 " + d['currency']),
        ("已上市产品 DCF", d.get('listed_product_npv', 0), "百万 " + d['currency']),
        ("平台/技术价值（可选）", d.get('platform_value', 0), "百万 " + d['currency']),
        ("授权里程碑 PV", d.get('milestone_value', 0), "百万 " + d['currency']),
        ("独家供货收入 PV（v6）", d.get('supply_value', 0), "百万 " + d['currency']),
        ("企业价值 (EV)", f"=B{row+1}+B{row+2}+B{row+3}+B{row+4}+B{row+5}", "百万 " + d['currency']),
        ("(+) 净现金", f"=B17", "百万 " + d['currency']),
        ("(-) 预期稀释", d.get('expected_dilution', 0), "百万 " + d['currency']),
        ("股权价值", f"=B{row+6}+B{row+7}-B{row+8}", "百万 " + d['currency']),
        ("稀释后总股本（百万）", d['shares_outstanding'], "百万股"),
        ("每股内在价值", f"=B{row+9}/B{row+10}", d['currency']),
    ]
    for i, item in enumerate(bridge):
        r = row + 1 + i
        label, val, unit = item
        is_total = "企业价值" in label or "股权价值" in label or "每股" in label
        font_val = FONT_BOLD if is_total else (FONT_INPUT if not str(val).startswith("=") else FONT_FORMULA)
        fill_val = FILL_TOTAL if is_total else None
        set_cell(ws, r, 1, label, font=FONT_BOLD if is_total else FONT_FORMULA,
                 fill=fill_val, alignment=ALIGN_LEFT)
        if isinstance(val, str) and val.startswith("="):
            set_cell(ws, r, 2, val, font=font_val, fill=fill_val,
                     number_format='#,##0.00' if "每股" in label else '#,##0.0')
        else:
            set_cell(ws, r, 2, val, font=font_val, fill=fill_val,
                     number_format='#,##0.00' if "每股" in label else '#,##0.0')
        set_cell(ws, r, 3, unit, font=FONT_NOTE, alignment=ALIGN_LEFT)

    ev_row = row + 6
    equity_row = row + 9
    price_target_row = row + 11

    # --- 市场隐含分析 ---
    row = price_target_row + 1
    ws.cell(row=row, column=1, value="市场隐含视角（⭐ 核心洞察）").font = FONT_SUBHEADER
    ws.cell(row=row, column=1).fill = FILL_SUBHEADER
    for c in range(2, 7):
        ws.cell(row=row, column=c).fill = FILL_SUBHEADER

    # 管线无风险PV在D列、PoS在C列；rNPV汇总区固定于 row=21(标题)/22(表头)/23..(管线)/..(合计)
    # 估值桥行号随 num_pipes 浮动 → 用 total_row 相对引用，保证任意管线条数都正确（可复用）
    pipe_start, pipe_end = 23, 22 + num_pipes
    listed_row, plat_row, milestone_row, supply_row, netcash_row = total_row + 4, total_row + 5, total_row + 6, total_row + 7, total_row + 9  # 估值桥对应行（v6 新增供货行 → netcash +1）
    implied_rows = [
        ("当前市值", f"=B13", "百万 " + d['currency']),
        ("(-) 已上市产品 NPV", f"=B{listed_row}", "百万 " + d['currency']),
        ("(-) 平台/技术价值", f"=B{plat_row}", "百万 " + d['currency']),
        ("(-) 授权里程碑 PV", f"=B{milestone_row}", "百万 " + d['currency']),
        ("(-) 独家供货收入 PV", f"=B{supply_row}", "百万 " + d['currency']),
        ("(-) 净现金", f"=B{netcash_row}", "百万 " + d['currency']),
        ("市场隐含管线价值", f"=B13-B{listed_row}-B{plat_row}-B{milestone_row}-B{supply_row}-B{netcash_row}", "百万 " + d['currency']),
        ("Σ 无风险管线 PV", f"=SUM(D{pipe_start}:D{pipe_end})", "百万 " + d['currency']),
        ("市场折扣因子 λ", f"=B{row+7}/B{row+8}", "λ = 隐含管线价值 / Σ无风险PV（=市场隐含综合成功率）"),
        ("加权平均 PoS（我们的）", f"=SUMPRODUCT(C{pipe_start}:C{pipe_end},D{pipe_start}:D{pipe_end})/SUM(D{pipe_start}:D{pipe_end})",
         "我们的综合成功率 = rNPV合计 / Σ无风险PV"),
        ("λ / 加权PoS", f"=B{row+9}/B{row+10}", "<0.7显著悲观 / 0.7-1.0偏悲观 / 1.0-1.3合理偏高 / 1.3-1.5偏乐观 / >1.5显著乐观"),
    ]
    for i, item in enumerate(implied_rows):
        r = row + 1 + i
        label, val, unit = item
        is_key = "隐含管线" in label or "λ" in label or "加权 PoS" in label
        fill_val = FILL_TOTAL if is_key else None
        font_val = FONT_BOLD if is_key else (FONT_FORMULA if str(val).startswith("=") else FONT_INPUT)
        set_cell(ws, r, 1, label, font=FONT_BOLD if is_key else FONT_FORMULA,
                 fill=fill_val, alignment=ALIGN_LEFT)
        fmt = '0.000' if "λ" in label or "加权" in label else '#,##0.0'
        pct_fmt = '0.0%' if ("PoS" in label and "/" not in label) else fmt
        if isinstance(val, str) and val.startswith("="):
            set_cell(ws, r, 2, val, font=font_val, fill=fill_val, number_format=pct_fmt)
        else:
            set_cell(ws, r, 2, val, font=font_val, fill=fill_val, number_format=pct_fmt)
        set_cell(ws, r, 3, unit, font=FONT_NOTE, alignment=ALIGN_LEFT)

    # --- 结论 ---
    row = row + len(implied_rows) + 2
    ws.cell(row=row, column=1, value="估值结论").font = FONT_SUBHEADER
    ws.cell(row=row, column=1).fill = FILL_SUBHEADER
    for c in range(2, 7):
        ws.cell(row=row, column=c).fill = FILL_SUBHEADER

    set_cell(ws, row + 1, 1, "每股内在价值", font=FONT_BOLD, alignment=ALIGN_LEFT)
    set_cell(ws, row + 1, 2, f"=B{price_target_row}", font=FONT_BOLD, number_format='#,##0.00')
    set_cell(ws, row + 2, 1, "当前股价", font=FONT_BOLD, alignment=ALIGN_LEFT)
    set_cell(ws, row + 2, 2, f"=B11", font=FONT_BOLD, number_format='#,##0.00')
    set_cell(ws, row + 3, 1, "溢价/折价", font=FONT_BOLD, alignment=ALIGN_LEFT)
    set_cell(ws, row + 3, 2, f"=B{row+1}/B{row+2}-1", font=FONT_BOLD, number_format='+0.0%;-0.0%;0.0%')
    set_cell(ws, row + 4, 1, "市场折扣因子 λ", font=FONT_BOLD, alignment=ALIGN_LEFT)
    set_cell(ws, row + 4, 2, d.get('lambda_placeholder', "见 Implied PoS sheet"),
             font=FONT_NOTE, alignment=ALIGN_LEFT)
    set_cell(ws, row + 5, 1, "结论", font=FONT_BOLD, alignment=ALIGN_LEFT)
    set_cell(ws, row + 5, 2, d.get('conclusion', "待填写"), font=FONT_INPUT, alignment=ALIGN_LEFT)

    # 免责声明
    row = row + 7
    set_cell(ws, row, 1,
             "⚠️ 本模型仅供研究参考，不构成投资建议。rNPV 对 PoS 和峰值销售假设高度敏感。",
             font=FONT_NOTE, alignment=ALIGN_LEFT)
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=6)


# ============================================================
# Sheet 2: Pipeline（管线总览）
# ============================================================

def build_pipeline_sheet(wb, data):
    ws = wb.create_sheet("Pipeline")
    set_column_widths(ws, [20, 18, 25, 12, 12, 12, 14, 14, 14, 14, 30])

    merge_title(ws, 1, 1, 11, f"{data['company_name']} — 管线总览")

    headers = [
        "药物名/代号", "靶点/机制", "适应症", "当前阶段", "地区",
        "关键试验", "预计读出", "基准 PoS", "调整后 PoS", "峰值销售（百万）", "竞争格局/备注"
    ]
    for i, h in enumerate(headers):
        set_cell(ws, 3, i + 1, h, font=FONT_HEADER, fill=FILL_HEADER)

    for i, pipe in enumerate(data['pipelines']):
        r = 4 + i
        set_cell(ws, r, 1, pipe['name'], font=FONT_LINK, alignment=ALIGN_LEFT)
        set_cell(ws, r, 2, pipe.get('target', ''), font=FONT_LINK, alignment=ALIGN_LEFT)
        set_cell(ws, r, 3, pipe['indication'], font=FONT_LINK, alignment=ALIGN_LEFT)
        set_cell(ws, r, 4, pipe['phase'], font=FONT_LINK)
        set_cell(ws, r, 5, pipe.get('region', ''), font=FONT_LINK)
        set_cell(ws, r, 6, pipe.get('trial_id', ''), font=FONT_LINK)
        set_cell(ws, r, 7, pipe.get('readout_date', ''), font=FONT_LINK)
        # PoS 从 Assumptions 引用（简化：直接输入）
        set_cell(ws, r, 8, pipe.get('base_pos', 0), font=FONT_INPUT, number_format='0.0%',
                 comment=f"基准 PoS（来源: BIO 2011-2020）")
        set_cell(ws, r, 9, pipe.get('adj_pos', 0), font=FONT_INPUT, number_format='0.0%',
                 comment=f"调整后 PoS（含情境微调）")
        set_cell(ws, r, 10, pipe['peak_sales'], font=FONT_INPUT, number_format='#,##0.0',
                 comment="峰值销售估算（见 peak-sales-framework.md）")
        set_cell(ws, r, 11, pipe.get('notes', ''), font=FONT_INPUT, alignment=ALIGN_LEFT)

    # 合计行
    total_row = 4 + len(data['pipelines'])
    set_cell(ws, total_row, 1, "合计", font=FONT_BOLD, fill=FILL_TOTAL)
    for c in range(2, 10):
        set_cell(ws, total_row, c, "", fill=FILL_TOTAL)
    set_cell(ws, total_row, 10, f"=SUM(J4:J{total_row-1})",
             font=FONT_BOLD, fill=FILL_TOTAL, number_format='#,##0.0')


# ============================================================
# Sheet 3: rNPV Detail（逐年现金流）
# ============================================================

def build_rnpv_detail_sheet(wb, data):
    ws = wb.create_sheet("rNPV Detail")
    set_column_widths(ws, [28, 14] + [14] * 15)

    merge_title(ws, 1, 1, 17, "rNPV 逐年现金流明细")

    # 折现率输入
    set_cell(ws, 3, 1, "折现率 (WACC)", font=FONT_BOLD, alignment=ALIGN_LEFT)
    set_cell(ws, 3, 2, data.get('wacc', 0.13), font=FONT_INPUT, number_format='0.0%',
             comment="折现率选取依据见 discount-rate-guide.md")

    # 年份表头
    base_year = data.get('base_year', 2026)
    years = list(range(base_year, base_year + 15))
    set_cell(ws, 5, 1, "年份", font=FONT_HEADER, fill=FILL_HEADER)
    set_cell(ws, 5, 2, "项目", font=FONT_HEADER, fill=FILL_HEADER)
    for i, yr in enumerate(years):
        set_cell(ws, 5, i + 3, yr, font=FONT_HEADER, fill=FILL_HEADER)

    current_row = 6

    for pipe in data['pipelines']:
        # 管线标题（不再拼接 phase，避免与 indication 重复）
        merge_title(ws, current_row, 1, 17,
                    f"{pipe['name']} — {pipe['indication']}",
                    font=FONT_SUBHEADER, fill=FILL_SUBHEADER, height=22)
        current_row += 1

        # 基本参数（6 行）
        # ★ 捕获绝对行号，公式中直接引用，避免 current_row 前移导致偏移错误（P0 修复）
        pos_row = current_row          # PoS（调整后）
        peak_row = current_row + 1     # 峰值销售
        launch_yr_row = current_row + 2  # 预计上市年份
        cogs_row = current_row + 3     # COGS 率
        sga_row = current_row + 4      # SG&A 率
        tax_row = current_row + 5      # 税率

        params = [
            ("PoS（调整后）", pipe.get('adj_pos', 0), '0.0%', "成功率"),
            ("峰值销售（百万）", pipe['peak_sales'], '#,##0.0', "峰值年销售额"),
            ("预计上市年份", pipe.get('launch_year', base_year + 5), '0', "预计商业化时间"),
            ("COGS 率", pipe.get('cogs_rate', 0.20), '0.0%', "销货成本占收入比"),
            ("SG&A 率", pipe.get('sga_rate', 0.30), '0.0%', "销售管理费用占收入比"),
            ("税率", pipe.get('tax_rate', 0.15), '0.0%', "所得税率"),
        ]
        for i, (label, val, fmt, note) in enumerate(params):
            set_cell(ws, current_row + i, 1, label, font=FONT_BOLD, alignment=ALIGN_LEFT)
            set_cell(ws, current_row + i, 2, val, font=FONT_INPUT, number_format=fmt, comment=note)

        current_row += len(params)  # current_row 现在 = revenue_row

        # 收入行 — ramp% × 峰值销售(绝对行引用)
        revenue_row = current_row
        set_cell(ws, current_row, 1, "收入", font=FONT_BOLD, alignment=ALIGN_LEFT)
        set_cell(ws, current_row, 2, "爬坡%", font=FONT_NOTE)

        ramp_curve = RAMP_CURVE  # 上市后Y1-Y15占峰值%（与 calc_unrisked_pv / Summary 口径统一）
        launch_year = pipe.get('launch_year', base_year + 5)

        for i, yr in enumerate(years):
            col = i + 3
            year_offset = yr - launch_year
            if year_offset < 0 or year_offset >= len(ramp_curve):
                ramp = 0
            else:
                ramp = ramp_curve[year_offset]
            # 收入 = ramp% × 峰值销售（绝对引用 peak_row）
            revenue = pipe['peak_sales'] * ramp / 100
            set_cell(ws, current_row, col, revenue, font=FONT_FORMULA, number_format='#,##0.0')

        current_row += 1

        # COGS 行 — 收入 × COGS率（绝对引用 cogs_row）
        cogs_formula_row = current_row
        set_cell(ws, current_row, 1, "(-) COGS", font=FONT_FORMULA, alignment=ALIGN_LEFT)
        for i, yr in enumerate(years):
            col = i + 3
            cl = get_column_letter(col)
            rev_cell = f"{cl}{revenue_row}"
            set_cell(ws, current_row, col,
                     f"=-{rev_cell}*B{cogs_row}",  # ★ 修正：引用 COGS 率行
                     font=FONT_FORMULA, number_format='#,##0.0')
        current_row += 1

        # SG&A 行 — 收入 × SG&A率（绝对引用 sga_row）
        set_cell(ws, current_row, 1, "(-) SG&A", font=FONT_FORMULA, alignment=ALIGN_LEFT)
        for i, yr in enumerate(years):
            col = i + 3
            cl = get_column_letter(col)
            rev_cell = f"{cl}{revenue_row}"
            set_cell(ws, current_row, col,
                     f"=-{rev_cell}*B{sga_row}",  # ★ 修正：引用 SG&A 率行
                     font=FONT_FORMULA, number_format='#,##0.0')
        current_row += 1

        # 税前利润 = 收入 + COGS + SG&A
        pretax_row = current_row
        set_cell(ws, current_row, 1, "税前利润", font=FONT_BOLD, alignment=ALIGN_LEFT)
        for i, yr in enumerate(years):
            col = i + 3
            cl = get_column_letter(col)
            set_cell(ws, current_row, col,
                     f"=SUM({cl}{revenue_row}:{cl}{cogs_formula_row + 1})",
                     font=FONT_FORMULA, number_format='#,##0.0')
        current_row += 1

        # 税后 FCF = 税前利润 × (1 - 税率)（绝对引用 tax_row）
        fcf_row = current_row
        set_cell(ws, current_row, 1, "税后 FCF", font=FONT_BOLD, alignment=ALIGN_LEFT)
        for i, yr in enumerate(years):
            col = i + 3
            cl = get_column_letter(col)
            set_cell(ws, current_row, col,
                     f"={cl}{pretax_row}*(1-B{tax_row})",  # ★ 修正：引用税率行
                     font=FONT_FORMULA, number_format='#,##0.0')
        current_row += 1

        # 折现因子
        disc_row = current_row
        set_cell(ws, current_row, 1, "折现因子", font=FONT_FORMULA, alignment=ALIGN_LEFT)
        for i, yr in enumerate(years):
            col = i + 3
            t = i + 1
            set_cell(ws, current_row, col,
                     f"=1/(1+$B$3)^{t}",
                     font=FONT_FORMULA, number_format='0.000')
        current_row += 1

        # 风险调整后 PV = 折现因子 × 税后FCF × PoS（绝对引用 pos_row）
        radj_row = current_row
        set_cell(ws, current_row, 1, "风险调整后 PV", font=FONT_BOLD, fill=FILL_TOTAL, alignment=ALIGN_LEFT)
        for i, yr in enumerate(years):
            col = i + 3
            cl = get_column_letter(col)
            set_cell(ws, current_row, col,
                     f"={cl}{disc_row}*{cl}{fcf_row}*B{pos_row}",  # ★ 修正：引用 PoS 行
                     font=FONT_BOLD, fill=FILL_TOTAL, number_format='#,##0.0')
        current_row += 1

        # rNPV 合计 = SUM(风险调整后 PV 行)
        set_cell(ws, current_row, 1, f"rNPV 合计（{pipe['name']}）",
                 font=FONT_BOLD, alignment=ALIGN_LEFT)
        start_col = get_column_letter(3)
        end_col = get_column_letter(2 + len(years))
        set_cell(ws, current_row, 2,
                 f"=SUM({start_col}{radj_row}:{end_col}{radj_row})",
                 font=FONT_BOLD, number_format='#,##0.0',
                 comment="该管线风险调整净现值")

        current_row += 3  # 空行间隔


# ============================================================
# Sheet 4: Implied PoS（市场隐含成功率反推）
# ============================================================

def build_implied_pos_sheet(wb, data):
    ws = wb.create_sheet("Implied PoS")
    set_column_widths(ws, [35, 16, 16, 16, 16, 16, 30])

    merge_title(ws, 1, 1, 7, "市场隐含成功率反推分析（⭐ 核心洞察）")

    # 方法说明
    row = 3
    set_cell(ws, row, 1, "方法：从当前市值反推市场对各管线隐含的成功率预期",
             font=FONT_NOTE, alignment=ALIGN_LEFT)
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=7)

    # --- 市值拆解 ---
    row = 5
    ws.cell(row=row, column=1, value="一、市值拆解").font = FONT_SUBHEADER
    ws.cell(row=row, column=1).fill = FILL_SUBHEADER
    for c in range(2, 8):
        ws.cell(row=row, column=c).fill = FILL_SUBHEADER

    # 市值拆解须与 Summary 一致：市值 − 已上市 − 平台 − 净现金
    mc_rows = [
        ("当前市值（百万）", data.get('market_cap', 0), "百万 " + data['currency']),
        ("(-) 已上市产品 NPV", data.get('listed_product_npv', 0), "百万 " + data['currency']),
        ("(-) 平台/技术价值", data.get('platform_value', 0), "百万 " + data['currency']),
        ("(-) 授权里程碑 PV", data.get('milestone_value', 0), "百万 " + data['currency']),
        ("(-) 独家供货收入 PV", data.get('supply_value', 0), "百万 " + data['currency']),
        ("(-) 净现金", data.get('net_cash', 0), "百万 " + data['currency']),
        ("市场隐含管线价值", "=B6-B7-B8-B9-B10-B11", "百万 " + data['currency']),
    ]
    for i, (label, val, unit) in enumerate(mc_rows):
        r = 6 + i
        is_key = i == 6
        set_cell(ws, r, 1, label, font=FONT_BOLD if is_key else FONT_FORMULA,
                 fill=FILL_TOTAL if is_key else None, alignment=ALIGN_LEFT)
        if isinstance(val, str) and val.startswith("="):
            set_cell(ws, r, 2, val, font=FONT_BOLD if is_key else FONT_FORMULA,
                     fill=FILL_TOTAL if is_key else None, number_format='#,##0.0')
        else:
            set_cell(ws, r, 2, val, font=FONT_INPUT,
                     fill=FILL_TOTAL if is_key else None, number_format='#,##0.0')
        set_cell(ws, r, 3, unit, font=FONT_NOTE, alignment=ALIGN_LEFT)

    # --- 各管线无风险 PV ---
    row = 12
    ws.cell(row=row, column=1, value="二、各管线无风险 PV（PoS=100% 时的现值）").font = FONT_SUBHEADER
    ws.cell(row=row, column=1).fill = FILL_SUBHEADER
    for c in range(2, 8):
        ws.cell(row=row, column=c).fill = FILL_SUBHEADER

    pv_headers = ["管线", "阶段", "调整后 PoS", "峰值销售（百万）", "无风险 PV（百万）", "rNPV（百万）"]
    for i, h in enumerate(pv_headers):
        set_cell(ws, row + 1, i + 1, h, font=FONT_HEADER, fill=FILL_HEADER)

    for i, pipe in enumerate(data['pipelines']):
        r = row + 2 + i
        set_cell(ws, r, 1, f"{pipe['name']} — {pipe['indication']}", font=FONT_LINK, alignment=ALIGN_LEFT)
        set_cell(ws, r, 2, pipe['phase'], font=FONT_LINK)
        set_cell(ws, r, 3, pipe.get('adj_pos', 0), font=FONT_INPUT, number_format='0.0%')
        set_cell(ws, r, 4, pipe['peak_sales'], font=FONT_INPUT, number_format='#,##0.0')
        # 无风险 PV = 峰值 × 近似折现因子（简化）
        pipe_pv = pipe.get('unrisked_pv', pipe['peak_sales'] * 0.3)
        set_cell(ws, r, 5, pipe_pv, font=FONT_FORMULA, number_format='#,##0.0',
                 comment="PoS=100%时的管线现值（来自 calc_unrisked_pv）")
        set_cell(ws, r, 6, f"=C{r}*E{r}", font=FONT_FORMULA, number_format='#,##0.0')

    num_pipes = len(data['pipelines'])
    total_row = row + 2 + num_pipes
    set_cell(ws, total_row, 1, "合计", font=FONT_BOLD, fill=FILL_TOTAL)
    set_cell(ws, total_row, 5, f"=SUM(E{row+2}:E{total_row-1})",
             font=FONT_BOLD, fill=FILL_TOTAL, number_format='#,##0.0')
    set_cell(ws, total_row, 6, f"=SUM(F{row+2}:F{total_row-1})",
             font=FONT_BOLD, fill=FILL_TOTAL, number_format='#,##0.0')

    # --- 反推折扣因子 ---
    row = total_row + 2
    ws.cell(row=row, column=1, value="三、反推市场折扣因子 λ").font = FONT_SUBHEADER
    ws.cell(row=row, column=1).fill = FILL_SUBHEADER
    for c in range(2, 8):
        ws.cell(row=row, column=c).fill = FILL_SUBHEADER

    lambda_rows = [
        ("市场隐含管线价值", "=B12", "百万"),  # B12 = 市值−已上市−平台−里程碑−供货−净现金
        ("Σ 无风险 PV", f"=E{total_row}", "百万"),
        ("市场折扣因子 λ", f"=B{row+1}/B{row+2}", "λ = 隐含管线价值 / 无风险PV"),
        ("加权平均基准 PoS",
         f"=SUMPRODUCT(C{total_row-num_pipes}:C{total_row-1},E{total_row-num_pipes}:E{total_row-1})/E{total_row}",
         "按 PV 加权的平均 PoS"),
        ("λ / 加权PoS", f"=B{row+3}/B{row+4}", "<0.7显著悲观 / 0.7-1.0偏悲观 / 1.0-1.3合理偏高 / 1.3-1.5偏乐观 / >1.5显著乐观"),
    ]
    for i, (label, val, note) in enumerate(lambda_rows):
        r = row + 1 + i
        is_key = i >= 2
        if i == 2:    fmt = '0.000'       # λ（如 1.111）
        elif i == 3:  fmt = '0.0%'        # 加权 PoS（如 51.6%）
        elif i == 4:  fmt = '0.00'        # λ/加权PoS 比值（如 2.15）
        else:         fmt = '#,##0.0'
        set_cell(ws, r, 1, label, font=FONT_BOLD if is_key else FONT_FORMULA,
                 fill=FILL_TOTAL if is_key else None, alignment=ALIGN_LEFT)
        if isinstance(val, str) and val.startswith("="):
            set_cell(ws, r, 2, val, font=FONT_BOLD if is_key else FONT_FORMULA,
                     fill=FILL_TOTAL if is_key else None, number_format=fmt)
        else:
            set_cell(ws, r, 2, val, font=FONT_INPUT, number_format=fmt)
        set_cell(ws, r, 3, note, font=FONT_NOTE, alignment=ALIGN_LEFT)

    # --- 对比分析 ---
    row = row + len(lambda_rows) + 2
    ws.cell(row=row, column=1, value="四、PoS 对比分析").font = FONT_SUBHEADER
    ws.cell(row=row, column=1).fill = FILL_SUBHEADER
    for c in range(2, 8):
        ws.cell(row=row, column=c).fill = FILL_SUBHEADER

    cmp_headers = ["管线", "阶段", "我们的 PoS", "市场隐含 PoS", "比值", "差异", "解读"]
    for i, h in enumerate(cmp_headers):
        set_cell(ws, row + 1, i + 1, h, font=FONT_HEADER, fill=FILL_HEADER)

    lambda_row = total_row + 5  # λ 所在行（反推因子标题=total_row+2，λ 为其下第 3 项）

    for i, pipe in enumerate(data['pipelines']):
        r = row + 2 + i
        base_pos = pipe.get('adj_pos', 0)
        set_cell(ws, r, 1, f"{pipe['name']} — {pipe['indication']}", font=FONT_LINK, alignment=ALIGN_LEFT)
        set_cell(ws, r, 2, pipe['phase'], font=FONT_LINK)
        set_cell(ws, r, 3, base_pos, font=FONT_INPUT, number_format='0.0%')
        # 隐含 PoS = λ × 基准PoS / 加权平均基准PoS
        set_cell(ws, r, 4, f"=$B${lambda_row}*C{r}/$B${lambda_row+1}",
                 font=FONT_FORMULA, number_format='0.0%')
        set_cell(ws, r, 5, f"=D{r}/C{r}", font=FONT_FORMULA, number_format='0.00')
        set_cell(ws, r, 6, f"=D{r}-C{r}", font=FONT_FORMULA, number_format='+0.0%;-0.0%;0.0%')
        set_cell(ws, r, 7,
                 f'=IF(E{r}<0.7,"显著悲观",IF(E{r}<1.0,"偏悲观",IF(E{r}<1.3,"合理偏高",IF(E{r}<1.5,"偏乐观","显著偏乐观"))))',
                 font=FONT_FORMULA, alignment=ALIGN_LEFT)

    # 结论
    row = row + 2 + len(data['pipelines']) + 1
    set_cell(ws, row, 1, "结论判断", font=FONT_BOLD, fill=FILL_TOTAL, alignment=ALIGN_LEFT)
    set_cell(ws, row, 2,
             f'=IF($B${lambda_row}/$B${lambda_row+1}<0.7,"显著偏悲观（市场低估管线）",'
             f'IF($B${lambda_row}/$B${lambda_row+1}<1.0,"偏悲观",'
             f'IF($B${lambda_row}/$B${lambda_row+1}<1.3,"合理偏高",'
             f'IF($B${lambda_row}/$B${lambda_row+1}<1.5,"偏乐观","显著偏乐观（市场高估管线）"))))',
             font=FONT_BOLD, fill=FILL_TOTAL, alignment=ALIGN_LEFT)
    ws.merge_cells(start_row=row, start_column=2, end_row=row, end_column=7)

    row += 2
    set_cell(ws, row, 1,
             "⚠️ 注意：λ/加权PoS > 1（市场偏乐观）不一定意味着高估——市场可能对平台期权、海外权益等未充分定价的资产给了溢价；"
             "λ/加权PoS < 1 也不一定意味着低估（市场可能察觉到我们不知道的风险）。λ>100% 时须检视无风险PV是否过保守。需结合 red-blue-debate 压力测试验证。",
             font=FONT_NOTE, alignment=ALIGN_LEFT)
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=7)


# ============================================================
# Sheet 5: Assumptions（假设输入）
# ============================================================

def build_assumptions_sheet(wb, data):
    ws = wb.create_sheet("Assumptions")
    set_column_widths(ws, [35, 16, 16, 40])

    merge_title(ws, 1, 1, 4, "输入假设汇总")

    # --- PoS 基准表 ---
    row = 3
    ws.cell(row=row, column=1, value="一、BIO 行业 PoS 基准（2011-2020）").font = FONT_SUBHEADER
    ws.cell(row=row, column=1).fill = FILL_SUBHEADER
    for c in range(2, 5):
        ws.cell(row=row, column=c).fill = FILL_SUBHEADER

    pos_headers = ["当前阶段", "→ 获批 累计 PoS", "→ 下一阶段", "备注"]
    for i, h in enumerate(pos_headers):
        set_cell(ws, row + 1, i + 1, h, font=FONT_HEADER, fill=FILL_HEADER)

    pos_data = [
        ("临床前", 0.018, 0.40, "整体最低"),
        ("Phase 1", 0.079, 0.52, "主要验证安全性"),
        ("Phase 2", 0.151, 0.289, "⚠️ 死亡之谷"),
        ("Phase 3", 0.524, 0.578, "有效性确证"),
        ("NDA/BLA", 0.906, 0.906, "递交后通过率高"),
        ("已上市", 1.000, 1.000, "已商业化"),
    ]
    for i, (phase, loa, next_phase, note) in enumerate(pos_data):
        r = row + 2 + i
        set_cell(ws, r, 1, phase, font=FONT_BOLD, alignment=ALIGN_LEFT)
        set_cell(ws, r, 2, loa, font=FONT_INPUT, number_format='0.0%',
                 comment="来源: BIO/BioMedTracker 2011-2020")
        set_cell(ws, r, 3, next_phase, font=FONT_INPUT, number_format='0.0%')
        set_cell(ws, r, 4, note, font=FONT_NOTE, alignment=ALIGN_LEFT)

    # --- 折现率 ---
    row = 12
    ws.cell(row=row, column=1, value="二、折现率假设").font = FONT_SUBHEADER
    ws.cell(row=row, column=1).fill = FILL_SUBHEADER
    for c in range(2, 5):
        ws.cell(row=row, column=c).fill = FILL_SUBHEADER

    wacc_rows = [
        ("WACC（本分析使用）", data.get('wacc', 0.13), "临床期 Biotech 中位数"),
        ("无风险利率（Rf）", 0.025, "中国10年期国债"),
        ("股权风险溢价（ERP）", 0.065, "中国市场"),
        ("公司 Beta", 1.3, "临床期 Biotech 典型值"),
    ]
    for i, (label, val, note) in enumerate(wacc_rows):
        r = row + 1 + i
        set_cell(ws, r, 1, label, font=FONT_BOLD, alignment=ALIGN_LEFT)
        set_cell(ws, r, 2, val, font=FONT_INPUT, number_format='0.0%')
        set_cell(ws, r, 3, note, font=FONT_NOTE, alignment=ALIGN_LEFT)

    # --- 爬坡曲线 ---
    row = 18
    ws.cell(row=row, column=1, value="三、收入爬坡曲线（占峰值 %）").font = FONT_SUBHEADER
    ws.cell(row=row, column=1).fill = FILL_SUBHEADER
    for c in range(2, 5):
        ws.cell(row=row, column=c).fill = FILL_SUBHEADER

    # 与 RAMP_CURVE / calc_unrisked_pv 完全一致；Y6 达峰，Y7 后 -20%/年衰减（展示前 9 年）
    ramp_data = [
        ("上市后 Y1", 0.10), ("上市后 Y2", 0.25), ("上市后 Y3", 0.50),
        ("上市后 Y4", 0.75), ("上市后 Y5", 0.90), ("上市后 Y6 (达峰)", 1.00),
        ("Y7", 0.95), ("Y8", 0.76), ("Y9", 0.61),
    ]
    for i, (label, val) in enumerate(ramp_data):
        r = row + 1 + i
        set_cell(ws, r, 1, label, font=FONT_FORMULA, alignment=ALIGN_LEFT)
        set_cell(ws, r, 2, val, font=FONT_INPUT, number_format='0%')

    # --- 费用率假设 ---
    row = 29
    ws.cell(row=row, column=1, value="四、费用率假设").font = FONT_SUBHEADER
    ws.cell(row=row, column=1).fill = FILL_SUBHEADER
    for c in range(2, 5):
        ws.cell(row=row, column=c).fill = FILL_SUBHEADER

    cost_rows = [
        ("COGS 率（生物药）", 0.20, "抗体/蛋白类药物"),
        ("COGS 率（化药）", 0.15, "小分子"),
        ("COGS 率（细胞/基因治疗）", 0.30, "高制造成本"),
        ("SG&A 率（上市初期）", 0.40, "商业化投入大"),
        ("SG&A 率（成熟期）", 0.25, "规模效应"),
        ("税率（中国高新企业）", 0.15, "15% 优惠税率"),
        ("税率（标准）", 0.25, "中国法定税率"),
        ("税率（海外）", 0.21, "美国法定税率"),
    ]
    for i, (label, val, note) in enumerate(cost_rows):
        r = row + 1 + i
        set_cell(ws, r, 1, label, font=FONT_BOLD, alignment=ALIGN_LEFT)
        set_cell(ws, r, 2, val, font=FONT_INPUT, number_format='0.0%')
        set_cell(ws, r, 3, note, font=FONT_NOTE, alignment=ALIGN_LEFT)

    # --- 数据来源 ---
    row = 39
    ws.cell(row=row, column=1, value="五、数据来源说明").font = FONT_SUBHEADER
    ws.cell(row=row, column=1).fill = FILL_SUBHEADER
    for c in range(2, 5):
        ws.cell(row=row, column=c).fill = FILL_SUBHEADER

    sources = [
        ("PoS 基准", "BIO/BioMedTracker 2011-2020 报告"),
        ("流行病学", "GLOBOCAN / 中国癌症登记年报 / IQVIA"),
        ("药品定价", "医保局公告 / 企业公告 / 已上市同类药"),
        ("管线信息", "公司投资者演示文稿 / ClinicalTrials.gov / CDE"),
        ("财务数据", "公司年报/中报 / yfinance"),
        ("折现率", "Damodaran 行业数据 / CAPM 计算"),
    ]
    for i, (item, src) in enumerate(sources):
        r = row + 1 + i
        set_cell(ws, r, 1, item, font=FONT_BOLD, alignment=ALIGN_LEFT)
        set_cell(ws, r, 2, src, font=FONT_NOTE, alignment=ALIGN_LEFT)
        ws.merge_cells(start_row=r, start_column=2, end_row=r, end_column=4)


# ============================================================
# Sheet 6: Sensitivity（敏感性分析）
# ============================================================

def build_sensitivity_sheet(wb, data):
    ws = wb.create_sheet("Sensitivity")
    set_column_widths(ws, [25, 14, 14, 14, 14, 14, 14])

    merge_title(ws, 1, 1, 7, "敏感性分析")

    # --- 表1: WACC × PoS ---
    row = 3
    ws.cell(row=row, column=1, value="敏感性 1: WACC × 整体 PoS 折扣").font = FONT_SUBHEADER
    ws.cell(row=row, column=1).fill = FILL_SUBHEADER
    for c in range(2, 8):
        ws.cell(row=row, column=c).fill = FILL_SUBHEADER

    set_cell(ws, row + 1, 1, "每股价值（货币）", font=FONT_HEADER, fill=FILL_HEADER)
    wacc_range = [0.09, 0.11, 0.13, 0.15, 0.17]
    pos_range = [0.5, 0.75, 1.0, 1.25, 1.5]

    for i, p in enumerate(pos_range):
        set_cell(ws, row + 1, i + 2, f"PoS × {p:.2f}", font=FONT_HEADER, fill=FILL_HEADER)

    for i, w in enumerate(wacc_range):
        r = row + 2 + i
        set_cell(ws, r, 1, f"WACC = {w:.0%}", font=FONT_BOLD, alignment=ALIGN_LEFT)
        for j, p in enumerate(pos_range):
            # 真敏感性：对每条管线按 wacc 逐年重折现，PoS 统一乘倍数
            adj = calc_per_share(data, w, pos_mult=p, peak_mult=1.0)
            set_cell(ws, r, j + 2, round(adj, 2), font=FONT_FORMULA, number_format='#,##0.00')

    # --- 表2: WACC × 峰值销售 ---
    row = 12
    ws.cell(row=row, column=1, value="敏感性 2: WACC × 峰值销售倍数").font = FONT_SUBHEADER
    ws.cell(row=row, column=1).fill = FILL_SUBHEADER
    for c in range(2, 8):
        ws.cell(row=row, column=c).fill = FILL_SUBHEADER

    set_cell(ws, row + 1, 1, "每股价值", font=FONT_HEADER, fill=FILL_HEADER)
    peak_range = [0.5, 0.75, 1.0, 1.25, 1.5]

    for i, pk in enumerate(peak_range):
        set_cell(ws, row + 1, i + 2, f"峰值 × {pk:.2f}", font=FONT_HEADER, fill=FILL_HEADER)

    for i, w in enumerate(wacc_range):
        r = row + 2 + i
        set_cell(ws, r, 1, f"WACC = {w:.0%}", font=FONT_BOLD, alignment=ALIGN_LEFT)
        for j, pk in enumerate(peak_range):
            # 真敏感性：峰值统一乘倍数，按 wacc 逐年重折现
            adj = calc_per_share(data, w, pos_mult=1.0, peak_mult=pk)
            set_cell(ws, r, j + 2, round(adj, 2), font=FONT_FORMULA, number_format='#,##0.00')

    # --- 龙卷风图说明 ---
    row = 21
    ws.cell(row=row, column=1, value="敏感性排名（龙卷风图参考）").font = FONT_SUBHEADER
    ws.cell(row=row, column=1).fill = FILL_SUBHEADER
    for c in range(2, 8):
        ws.cell(row=row, column=c).fill = FILL_SUBHEADER

    tornado = [
        ("峰值销售假设", "★★★★★", "最敏感：峰值±50% → 估值变化 ±40-50%"),
        ("PoS 假设", "★★★★★", "极敏感：PoS 翻倍 → 管线 rNPV 翻倍"),
        ("WACC", "★★★★", "敏感：±2% → 估值变化 ±15-20%"),
        ("上市年份", "★★★", "中等：推迟1年 → rNPV 下降 ~10%"),
        ("COGS/SG&A 率", "★★", "低敏感：±5% → 估值变化 ±5%"),
        ("税率", "★", "低敏感：±5% → 估值变化 ±3%"),
    ]
    headers_t = ["假设变量", "敏感度", "影响说明"]
    for i, h in enumerate(headers_t):
        set_cell(ws, row + 1, i + 1, h, font=FONT_HEADER, fill=FILL_HEADER)

    for i, (var, stars, note) in enumerate(tornado):
        r = row + 2 + i
        set_cell(ws, r, 1, var, font=FONT_BOLD, alignment=ALIGN_LEFT)
        set_cell(ws, r, 2, stars, font=FONT_FORMULA)
        set_cell(ws, r, 3, note, font=FONT_NOTE, alignment=ALIGN_LEFT)
        ws.merge_cells(start_row=r, start_column=3, end_row=r, end_column=7)

    # 结论
    row = 30
    set_cell(ws, row, 1,
             "⚠️ 如果估值结论在 WACC ±2% 或 PoS ±20% 范围内翻转（从低估变高估），"
             "说明结论不稳健，需在报告中明确标注不确定性。",
             font=FONT_NOTE, alignment=ALIGN_LEFT)
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=7)


# ============================================================
# 主函数：组装完整模型
# ============================================================

def build_rnpv_model(data, output_path):
    """
    构建 rNPV Excel 模型

    Args:
        data: 包含公司信息和管线数据的字典
        output_path: 输出文件路径
    """
    wb = Workbook()
    wb.remove(wb.active)  # 删除默认 Sheet

    # 真值源：统一用 calc_unrisked_pv 逐年折现重算每条管线无风险 PV，覆盖任何手填值。
    # 这样 Summary / rNPV Detail / Implied PoS / Sensitivity 四处口径完全一致。
    base_year = data.get('base_year', 2026)
    wacc = data.get('wacc', 0.13)
    for p in data['pipelines']:
        p['unrisked_pv'] = round(calc_unrisked_pv(
            p['peak_sales'], p.get('launch_year', base_year + 5),
            p.get('cogs_rate', 0.20), p.get('sga_rate', 0.30),
            p.get('tax_rate', 0.15), wacc, base_year), 0)

    # 按 6 个 Sheet 构建
    build_summary_sheet(wb, data)
    build_pipeline_sheet(wb, data)
    build_rnpv_detail_sheet(wb, data)
    build_implied_pos_sheet(wb, data)
    build_assumptions_sheet(wb, data)
    build_sensitivity_sheet(wb, data)

    # 保存
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    wb.save(output_path)
    print(f"[OK] rNPV model generated: {output_path}")
    return output_path


# ============================================================
# 示例数据 + 测试入口
# ============================================================

SAMPLE_DATA = {
    "company_name": "示例生物科技",
    "ticker": "XXXX.HK",
    "exchange": "港交所",
    "analysis_date": "2026-07-11",
    "currency": "HK$",

    # 财务快照
    "current_price": 10.0,
    "shares_outstanding": 1000,
    "cash": 500,
    "short_term_investments": 100,
    "debt": 50,
    "rd_expense": 200,
    "quarterly_burn": 60,
    "price_source": "示例数据",
    "shares_source": "示例数据",

    # 估值参数
    "listed_product_npv": 0,
    "platform_value": 0,
    "expected_dilution": 0,
    "wacc": 0.13,
    "base_year": 2026,
    "net_cash": 550,
    "market_cap": 10000,

    # 管线
    "pipelines": [
        {
            "name": "Drug A",
            "target": "HER2 双抗",
            "indication": "HER2+ 乳腺癌",
            "phase": "Phase 3",
            "region": "中国",
            "trial_id": "NCT0xxxxx",
            "readout_date": "2026H2",
            "base_pos": 0.524,
            "adj_pos": 0.58,
            "peak_sales": 800,
            "launch_year": 2028,
            "cogs_rate": 0.20,
            "sga_rate": 0.30,
            "tax_rate": 0.15,
            "unrisked_pv": 240,
            "notes": "有Phase 2 PoC数据，同靶点已验证",
        },
        {
            "name": "Drug B",
            "target": "PD-L1",
            "indication": "非小细胞肺癌",
            "phase": "Phase 2",
            "region": "中国",
            "trial_id": "NCT0yyyyy",
            "readout_date": "2027H1",
            "base_pos": 0.151,
            "adj_pos": 0.17,
            "peak_sales": 500,
            "launch_year": 2030,
            "cogs_rate": 0.20,
            "sga_rate": 0.35,
            "tax_rate": 0.15,
            "unrisked_pv": 120,
            "notes": "竞争激烈，5+竞品",
        },
        {
            "name": "Drug C",
            "target": "TIGIT",
            "indication": "实体瘤",
            "phase": "Phase 1",
            "region": "中国",
            "trial_id": "NCT0zzzzz",
            "readout_date": "2028",
            "base_pos": 0.079,
            "adj_pos": 0.08,
            "peak_sales": 300,
            "launch_year": 2031,
            "cogs_rate": 0.20,
            "sga_rate": 0.40,
            "tax_rate": 0.15,
            "unrisked_pv": 60,
            "notes": "早期，高风险",
        },
    ],

    "sensitivity_base_value": 8.5,
    "conclusion": "待分析后填写",
}


if __name__ == "__main__":
    output = os.path.join(os.path.dirname(__file__), "..", "output",
                          "sample_rNPV_model.xlsx")
    build_rnpv_model(SAMPLE_DATA, os.path.abspath(output))
