# -*- coding: utf-8 -*-
"""
医院药品季度盘点分析流水线
==========================
将原始盘点 .xls 经过「清洗 → 实盘数量计算 → 差异分析 → 负数记录隔离 → 进销存填表」
五个阶段，产出可直接用于季度盘点报告的 Excel 文件。

运行环境：
    Python 3.11+；依赖 xlrd（读 .xls）、openpyxl（读写 .xlsx）。
    使用 WorkBuddy 自带的 managed python 即可：
    C:/Users/Yen/.workbuddy/binaries/python/versions/3.13.12/python.exe pipeline.py <stage> ...

用法：
    pipeline.py clean   <原始盘点.xls> <清洗后.xlsx> [阈值=0.01]
    pipeline.py shipan  <清洗后.xlsx>   <实盘数量.xlsx>
    pipeline.py diff    <实盘数量.xlsx>  <差异分析.xlsx>
    pipeline.py negative <实盘数量.xlsx> <负数记录.xlsx> <差异分析.xlsx>
    pipeline.py fill    <实盘数量.xlsx> <进销存.xlsx> <盘点数据模板.xlsx> <已填.xlsx>
    pipeline.py all     <原始盘点.xls> <进销存.xlsx> <盘点数据模板.xlsx> <输出目录> [阈值]

各阶段说明见 SKILL.md 与 references/schema_and_rules.md。
"""

import sys
import re
import os
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

# ============================ 可调参数 ============================
# 价格差异标红阈值（元）。仅当 |盘前进价 - 盘后进价| > 此值才整行标红。
THRESHOLD = 0.01

# 特殊药品固定包装系数（名称关键词 -> 每盒/每单位数量）
# 蛇毒血凝酶/浓氯化钠/依诺肝素钠 → 5支/盒；复方硫酸亚铁颗粒 → 10袋/盒；开塞露 → 20支/盒
NAME_COEFF = [
    ("开塞露", 20),
    ("硫酸亚铁颗粒", 10),
    ("蛇毒血凝酶", 5),
    ("浓氯化钠", 5),
    ("依诺肝素", 5),
]

# 规格中可识别的「计数单位」（用于从规格文本提取包装数量）
COUNT_UNITS = "粒|支|片|袋|包|个|枚|丸|贴|组|瓶|揿|喷|吸|板|颗|泡|张"

# 规格无包装数量时的默认每盒数量（规则5：默认每盒10支/瓶）
DEFAULT_PACK = 10

# 源表列名常量（与原始盘点表头一致，按名称匹配，允许列序变化）
COL = [
    "药品编码", "药品名称", "规格", "盘点单位", "生产企业", "供货商", "批号",
    "帐存数量", "实存库房数量", "库房单位", "实存药房数量", "药房单位",
    "盘前进价", "盘后进价",
]


# ============================ 通用工具 ============================
def num(v):
    """把单元格值转成 float；空/非数值返回 None。"""
    try:
        if v is None or (isinstance(v, str) and v.strip() == ""):
            return None
        return float(v)
    except Exception:
        return None


def is_explicit_zero(v):
    """仅当显式数值 0 才返回 True；空/非数值返回 False（视为未知，保留）。"""
    n = num(v)
    return n is not None and n == 0.0


def name_coeff(name):
    """按药品名称匹配特殊药品系数；无匹配返回 None。"""
    s = str(name or "")
    for k, c in NAME_COEFF:
        if k in s:
            return c
    return None


def extract_pack(gg):
    """从规格文本提取包装数量。
    优先级：
      1) '*' 之后的数字+单位，如 '1.74g*12粒' -> 12、'2ml:1mg*30支' -> 30、'50ug*60揿' -> 60
      2) '数字+单位+/（' 形式，如 '100片/瓶' -> 100
      3) 兜底：第一个 '数字+单位'
    体积/质量单位（ml/g）不计入，此类应由默认规则处理。
    """
    if not gg:
        return None
    s = str(gg)
    m = re.search(r"\*\s*(\d+(?:\.\d+)?)\s*(" + COUNT_UNITS + r")", s)
    if m:
        return float(m.group(1))
    m = re.search(r"(\d+(?:\.\d+)?)\s*(" + COUNT_UNITS + r")\s*[/／(（]", s)
    if m:
        return float(m.group(1))
    m = re.search(r"(\d+(?:\.\d+)?)\s*(" + COUNT_UNITS + r")", s)
    if m:
        return float(m.group(1))
    return None


def compute_shipan(name, gg, ku, ya, zk, yf):
    """计算单行实盘数量。返回 (实盘数量, 规则, 系数P)。
    统一公式：实盘数量 = 实存库房数量 × P + 实存药房数量
    规则优先级：
      A 特殊药品固定系数
      B 库房单位==药房单位 -> P=1（直接取另一非零方）
      C 单位不同且规格含包装数量 -> P=提取值
      D 规格无包装数量 -> P=DEFAULT_PACK(默认10)
    """
    zk = zk or 0.0
    yf = yf or 0.0
    nc = name_coeff(name)
    if nc is not None:
        return zk * nc + yf, "special", nc
    if ku == ya:
        return zk * 1 + yf, "same_unit", 1
    p = extract_pack(gg)
    if p is not None:
        return zk * p + yf, "pack_extracted", p
    return zk * DEFAULT_PACK + yf, "default10", DEFAULT_PACK


# ============================ 样式 ============================
HEAD_FILL = PatternFill("solid", fgColor="FF4472C4")
HEAD_FONT = Font(bold=True, color="FFFFFFFF")
RED_FILL = PatternFill("solid", fgColor="FFFF9999")
RED_FONT = Font(bold=True, color="FF9C0006")
THIN = Side(style="thin", color="FFBFBFBF")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
CENTER = Alignment(horizontal="center", vertical="center")
PRICE_FMT = "0.0000"
MONEY_FMT = "#,##0.00"


def style_header(ws, row, ncol):
    for c in range(1, ncol + 1):
        cell = ws.cell(row=row, column=c)
        cell.fill = HEAD_FILL
        cell.font = HEAD_FONT
        cell.alignment = CENTER
        cell.border = BORDER


def set_widths(ws, widths):
    for i, w in enumerate(widths, start=1):
        ws.column_dimensions[get_column_letter(i)].width = w


# ============================ 阶段1：清洗 ============================
def stage_clean(src_xls, dst_xlsx, threshold=THRESHOLD):
    import xlrd
    wb = xlrd.open_workbook(src_xls, formatting_info=True)
    sh = wb.sheet_by_index(0)
    # 表头在第2行(0-based=1)，标题合并在第1行，数据从第3行(0-based=2)
    hdr = [str(sh.cell_value(1, c)).strip() for c in range(sh.ncols)]
    idx = {h: i for i, h in enumerate(hdr)}

    def col(name):
        if name not in idx:
            raise KeyError(f"清洗：源表缺少列 '{name}'，实际表头={hdr}")
        return idx[name]

    i_z, i_k, i_y = col("帐存数量"), col("实存库房数量"), col("实存药房数量")
    i_p1, i_p2 = col("盘前进价"), col("盘后进价")

    out = Workbook()
    ws = out.active
    ws.title = sh.name if hasattr(sh, "name") else "盘点明细表"
    ncol = len(hdr)

    # 标题行（合并）
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=ncol)
    t = ws.cell(row=1, column=1, value=str(sh.cell_value(0, 0)))
    t.font = Font(bold=True, size=14)
    t.alignment = CENTER
    # 表头（带序号列）
    headers = ["序号"] + hdr
    for c, h in enumerate(headers, start=1):
        ws.cell(row=2, column=c, value=h)
    style_header(ws, 2, ncol + 1)

    rownum = 0
    for r in range(2, sh.nrows):
        z = sh.cell_value(r, i_z)
        k = sh.cell_value(r, i_k)
        y = sh.cell_value(r, i_y)
        # 仅当三项均为显式数值0才删除；空白/非数值视为未知，保留
        if is_explicit_zero(z) and is_explicit_zero(k) and is_explicit_zero(y):
            continue
        rownum += 1
        row_vals = [rownum] + [sh.cell_value(r, c) for c in range(ncol)]
        # 价格差异标红
        p1, p2 = num(sh.cell_value(r, i_p1)), num(sh.cell_value(r, i_p2))
        flag = (p1 is not None and p2 is not None and abs(p1 - p2) > threshold)
        for c, v in enumerate(row_vals, start=1):
            cell = ws.cell(row=2 + rownum, column=c, value=v)
            cell.border = BORDER
            if c in (8, 9, 11):  # 帐存/库房/药房 数量列居中
                cell.alignment = CENTER
            if flag:
                cell.fill = RED_FILL
                cell.font = RED_FONT

    # 价格列精度
    for r in range(3, ws.max_row + 1):
        for c in (ncol, ncol + 1 - 1):  # 盘前/盘后进价（序号后移1列）
            pass
    # 盘前进价=原第13列 -> 现在第14列；盘后进价=第15列
    for r in range(3, ws.max_row + 1):
        ws.cell(row=r, column=ncol).number_format = PRICE_FMT   # 盘前进价
        ws.cell(row=r, column=ncol + 1).number_format = PRICE_FMT  # 盘后进价
        ws.cell(row=r, column=8).alignment = CENTER
        ws.cell(row=r, column=9).alignment = CENTER
        ws.cell(row=r, column=11).alignment = CENTER

    ws.freeze_panes = "A3"
    set_widths(ws, [6] + [16] * ncol)
    # 自动筛选
    ws.auto_filter.ref = f"A2:{get_column_letter(ncol + 1)}{ws.max_row}"
    out.save(dst_xlsx)
    print(f"[clean] 完成：删除全零行，保留 {rownum} 行 -> {dst_xlsx}")
    return dst_xlsx


# ============================ 阶段2：实盘数量 ============================
def stage_shipan(src_clean_xlsx, dst_xlsx):
    wb = load_workbook(src_clean_xlsx)
    ws = wb.active
    # 表头行（含序号）
    hdr = [ws.cell(row=2, column=c).value for c in range(1, ws.max_column + 1)]
    idx = {h: i + 1 for i, h in enumerate(hdr)}

    def col(name):
        if name not in idx:
            raise KeyError(f"实盘：缺少列 '{name}'，实际表头={hdr}")
        return idx[name]

    i_code, i_name, i_gg = col("药品编码"), col("药品名称"), col("规格")
    i_z, i_k, i_ku = col("帐存数量"), col("实存库房数量"), col("库房单位")
    i_y, i_ya = col("实存药房数量"), col("药房单位")
    i_p1, i_p2 = col("盘前进价"), col("盘后进价")
    i_mfr, i_sup, i_lot, i_pd = col("生产企业"), col("供货商"), col("批号"), col("盘点单位")

    # 输出列：按用户指定顺序（去序号）
    out_cols = ["药品编码", "药品名称", "规格", "盘点单位", "生产企业", "供货商", "批号",
                "帐存数量", "实盘数量", "实存库房数量", "库房单位", "实存药房数量",
                "药房单位", "盘前进价", "盘后进价"]
    out = Workbook()
    ws2 = out.active
    ws2.title = "盘点明细表"
    ncol = len(out_cols)
    ws2.merge_cells(start_row=1, start_column=1, end_row=1, end_column=ncol)
    tt = ws2.cell(row=1, column=1, value="盘点明细表")
    tt.font = Font(bold=True, size=14)
    tt.alignment = CENTER
    for c, h in enumerate(out_cols, start=1):
        ws2.cell(row=2, column=c, value=h)
    style_header(ws2, 2, ncol)

    methods = {}
    for r in range(3, ws.max_row + 1):
        name = ws.cell(row=r, column=i_name).value
        gg = ws.cell(row=r, column=i_gg).value
        ku = ws.cell(row=r, column=i_ku).value
        ya = ws.cell(row=r, column=i_ya).value
        zk = num(ws.cell(row=r, column=i_k).value)
        yf = num(ws.cell(row=r, column=i_y).value)
        shipan, rule, p = compute_shipan(name, gg, ku, ya, zk, yf)
        methods[rule] = methods.get(rule, 0) + 1
        vals = [
            ws.cell(row=r, column=i_code).value, name, gg,
            ws.cell(row=r, column=i_pd).value, ws.cell(row=r, column=i_mfr).value,
            ws.cell(row=r, column=i_sup).value, ws.cell(row=r, column=i_lot).value,
            num(ws.cell(row=r, column=i_z).value),
            round(shipan, 4),
            num(ws.cell(row=r, column=i_k).value), ku,
            num(ws.cell(row=r, column=i_y).value), ya,
            num(ws.cell(row=r, column=i_p1).value), num(ws.cell(row=r, column=i_p2).value),
        ]
        for c, v in enumerate(vals, start=1):
            cell = ws2.cell(row=2 + (r - 2), column=c, value=v)
            cell.border = BORDER
            if c in (8, 9, 10, 12):
                cell.alignment = CENTER
            if c in (14, 15):
                cell.number_format = PRICE_FMT
    ws2.freeze_panes = "A3"
    set_widths(ws2, [12, 22, 18, 8, 22, 18, 14, 10, 10, 12, 8, 12, 8, 11, 11])
    ws2.auto_filter.ref = f"A2:{get_column_letter(ncol)}{ws2.max_row}"
    out.save(dst_xlsx)
    print(f"[shipan] 完成：{ws2.max_row - 2} 行；规则分布={methods} -> {dst_xlsx}")
    return dst_xlsx


# ============================ 阶段3：差异分析 ============================
DIFF_COLS = ["药品编码", "药品名称", "规格", "盘点单位", "批号",
             "帐存数量", "实盘数量", "差异数量", "差异金额"]


def _build_diff_rows(src_shipan_xlsx, include_neg=True):
    wb = load_workbook(src_shipan_xlsx)
    ws = wb.active
    hdr = [ws.cell(row=2, column=c).value for c in range(1, ws.max_column + 1)]
    idx = {h: i + 1 for i, h in enumerate(hdr)}

    def col(name):
        if name not in idx:
            raise KeyError(f"差异：缺少列 '{name}'")
        return idx[name]

    i_code, i_name, i_gg = col("药品编码"), col("药品名称"), col("规格")
    i_pd, i_lot = col("盘点单位"), col("批号")
    i_z, i_sp, i_p2 = col("帐存数量"), col("实盘数量"), col("盘后进价")
    rows = []
    for r in range(3, ws.max_row + 1):
        sp = num(ws.cell(row=r, column=i_sp).value)
        if sp is None:
            continue
        if not include_neg and sp < 0:
            continue
        z = num(ws.cell(row=r, column=i_z).value) or 0.0
        price = num(ws.cell(row=r, column=i_p2).value) or 0.0
        dq = round(sp - z, 4)
        da = round(dq * price, 2)
        rows.append({
            "药品编码": ws.cell(row=r, column=i_code).value,
            "药品名称": ws.cell(row=r, column=i_name).value,
            "规格": ws.cell(row=r, column=i_gg).value,
            "盘点单位": ws.cell(row=r, column=i_pd).value,
            "批号": ws.cell(row=r, column=i_lot).value,
            "帐存数量": z, "实盘数量": sp, "差异数量": dq, "差异金额": da,
        })
    return rows


def stage_diff(src_shipan_xlsx, dst_xlsx, include_neg=True):
    rows = _build_diff_rows(src_shipan_xlsx, include_neg=include_neg)
    total = len(rows)
    gain = [r for r in rows if r["差异数量"] > 0]
    loss = [r for r in rows if r["差异数量"] < 0]
    match = [r for r in rows if r["差异数量"] == 0]
    gain.sort(key=lambda x: x["差异金额"], reverse=True)   # 盘盈：金额降序
    loss.sort(key=lambda x: x["差异金额"])                  # 盘亏：金额升序

    out = Workbook()
    sheets = {
        "盘点差异总表": rows,
        "盘盈表": gain,
        "盘亏表": loss,
        "相符表": match,
    }
    ncol = len(DIFF_COLS)
    for name, data in sheets.items():
        ws = out.create_sheet(title=name)
        for c, h in enumerate(DIFF_COLS, start=1):
            ws.cell(row=2, column=c, value=h)
        style_header(ws, 2, ncol)
        for ri, rec in enumerate(data, start=3):
            for c, h in enumerate(DIFF_COLS, start=1):
                v = rec[h]
                cell = ws.cell(row=ri, column=c, value=v)
                cell.border = BORDER
                if h in ("帐存数量", "实盘数量", "差异数量"):
                    cell.alignment = CENTER
                if h == "差异金额":
                    cell.number_format = MONEY_FMT
        ws.freeze_panes = "A3"
        set_widths(ws, [12, 22, 18, 8, 14, 10, 10, 10, 12])
        ws.auto_filter.ref = f"A2:{get_column_letter(ncol)}{ws.max_row}"

    # 汇总
    ws_sum = out.create_sheet(title="盘点汇总")
    ws_sum.cell(row=1, column=1, value="指标").font = Font(bold=True)
    ws_sum.cell(row=1, column=2, value="数值").font = Font(bold=True)
    acc = round(len(match) / total * 100, 2) if total else 0.0
    summary = [
        ("总品种数", total),
        ("盘盈（差异数量>0）", len(gain)),
        ("盘亏（差异数量<0）", len(loss)),
        ("相符（差异数量=0）", len(match)),
        ("盘点准确率(%)", acc),
    ]
    for i, (k, v) in enumerate(summary, start=3):
        ws_sum.cell(row=i, column=1, value=k)
        c = ws_sum.cell(row=i, column=2, value=v)
        if k.endswith("(%)"):
            c.number_format = "0.00"
    set_widths(ws_sum, [22, 14])

    # 删除默认空表，调整顺序：总表在前
    if "Sheet" in out.sheetnames:
        del out["Sheet"]
    order = ["盘点差异总表", "盘盈表", "盘亏表", "相符表", "盘点汇总"]
    out._sheets.sort(key=lambda s: order.index(s.title) if s.title in order else 99)
    out.save(dst_xlsx)
    print(f"[diff] 完成：总{total} 盈{len(gain)} 亏{len(loss)} 符{len(match)} 准确率{acc}% -> {dst_xlsx}")
    return dst_xlsx


# ============================ 阶段4：负数记录隔离 ============================
def stage_negative(src_shipan_xlsx, dst_neg_xlsx, dst_diff_xlsx):
    wb = load_workbook(src_shipan_xlsx)
    ws = wb.active
    hdr = [ws.cell(row=2, column=c).value for c in range(1, ws.max_column + 1)]
    idx = {h: i + 1 for i, h in enumerate(hdr)}
    # 取全量原始列 + 差异数量 + 差异金额
    out_cols = hdr + ["差异数量", "差异金额"]
    neg_rows = []
    for r in range(3, ws.max_row + 1):
        sp = num(ws.cell(row=r, column=idx["实盘数量"]).value)
        if sp is not None and sp < 0:
            z = num(ws.cell(row=r, column=idx["帐存数量"]).value) or 0.0
            price = num(ws.cell(row=r, column=idx["盘后进价"]).value) or 0.0
            dq = round(sp - z, 4)
            da = round(dq * price, 2)
            row = [ws.cell(row=r, column=c).value for c in range(1, len(hdr) + 1)] + [dq, da]
            neg_rows.append(row)

    out = Workbook()
    nws = out.active
    nws.title = "负数实盘记录"
    ncol = len(out_cols)
    nws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=ncol)
    note = nws.cell(row=1, column=1, value="负数实盘记录（已隔离待核对，未计入差异分析）")
    note.font = Font(bold=True, color="FF9C0006")
    note.alignment = CENTER
    for c, h in enumerate(out_cols, start=1):
        nws.cell(row=2, column=c, value=h)
    style_header(nws, 2, ncol)
    for ri, row in enumerate(neg_rows, start=3):
        for c, v in enumerate(row, start=1):
            cell = nws.cell(row=ri, column=c, value=v)
            cell.border = BORDER
            cell.fill = RED_FILL
            cell.font = RED_FONT
    nws.freeze_panes = "A3"
    set_widths(nws, [12, 22, 18, 8, 22, 18, 14, 10, 10, 12, 8, 12, 8, 11, 11, 10, 12])
    out.save(dst_neg_xlsx)
    print(f"[negative] 隔离 {len(neg_rows)} 行负数实盘记录 -> {dst_neg_xlsx}")
    # 重算差异分析（剔除负数）
    stage_diff(src_shipan_xlsx, dst_diff_xlsx, include_neg=False)
    return dst_neg_xlsx, dst_diff_xlsx


# ============================ 阶段5：进销存填表 ============================
def _find_jxc_col(sh, keyword, header_rows=(6, 7, 8)):
    """在进销存表的分组表头(多行)中按关键词定位列。"""
    for c in range(1, sh.max_column + 1):
        txt = "".join(str(sh.cell(row=r, column=c).value or "") for r in header_rows)
        if keyword in txt:
            return c
    return None


def _find_total_row(sh):
    for r in range(1, sh.max_row + 1):
        v = sh.cell(row=r, column=1).value
        if v is not None and "合计" in str(v):
            return r
    return None


def _col_sum(sh, col_idx, start_row, end_row):
    s = 0.0
    for r in range(start_row, end_row + 1):
        v = sh.cell(row=r, column=col_idx).value
        if isinstance(v, (int, float)):
            s += float(v)
    return round(s, 2)


def _parse_pandian_time(sh):
    """取盘点时间：优先找'盘点时间'字段；否则从'统计时间 ...至 YYYY-MM-DD'提取截止日。"""
    for r in range(1, min(10, sh.max_row + 1)):
        for c in range(1, sh.max_column + 1):
            v = sh.cell(row=r, column=c).value
            if v is not None and "盘点时间" in str(v):
                val = sh.cell(row=r, column=c + 1).value
                if val is not None:
                    return val
    # 统计时间兜底
    for r in range(1, min(10, sh.max_row + 1)):
        for c in range(1, sh.max_column + 1):
            v = sh.cell(row=r, column=c).value
            if v is not None and "统计时间" in str(v):
                m = re.search(r"至\s*(\d{4}[-/]\d{1,2}[-/]\d{1,2})", str(v))
                if m:
                    return m.group(1)
    return None


def stage_fill(src_shipan_xlsx, src_jxc_xlsx, tpl_xlsx, dst_xlsx):
    # ---- 5.1 进销存汇总 ----
    jwb = load_workbook(src_jxc_xlsx, data_only=True)
    jsh = jwb[jwb.sheetnames[0]]
    total_row = _find_total_row(jsh)
    data_start = 9  # 表头结束后的数据起始行（典型结构）
    data_end = (total_row - 1) if total_row else jsh.max_row
    # 优先用合计行校验；若合计行存在则直接取合计行对应列
    def money(field_kw):
        ci = _find_jxc_col(jsh, field_kw)
        if ci is None:
            return None
        if total_row:
            tv = jsh.cell(row=total_row, column=ci).value
            if isinstance(tv, (int, float)):
                return round(float(tv), 2)
        return _col_sum(jsh, ci, data_start, data_end)

    期初 = money("期初")
    入库 = money("申领入库")
    销售 = money("销售")
    调拨入 = money("调拨入库")
    调拨出 = money("调拨出库")
    报损 = money("报损")
    调拨金额 = round((调拨入 or 0) - (调拨出 or 0), 2)
    盘点时间 = _parse_pandian_time(jsh)

    # ---- 5.2 盘点最终数据 ----
    rows = _build_diff_rows(src_shipan_xlsx, include_neg=False)
    total = len(rows)
    book_amt = round(sum(r["帐存数量"] * (r.get("盘后进价") or 0) for r in rows), 2)
    # 注意：_build_diff_rows 未带盘后进价，改用下方直接计算
    # 重新读取盘后进价
    sb = load_workbook(src_shipan_xlsx)
    sws = sb.active
    shdr = [sws.cell(row=2, column=c).value for c in range(1, sws.max_column + 1)]
    sidx = {h: i + 1 for i, h in enumerate(shdr)}
    book_amt = real_amt = 0.0
    match_cnt = 0
    for r in range(3, sws.max_row + 1):
        sp = num(sws.cell(row=r, column=sidx["实盘数量"]).value)
        if sp is None or sp < 0:
            continue
        z = num(sws.cell(row=r, column=sidx["帐存数量"]).value) or 0.0
        price = num(sws.cell(row=r, column=sidx["盘后进价"]).value) or 0.0
        book_amt += z * price
        real_amt += sp * price
        if sp - z == 0:
            match_cnt += 1
    book_amt, real_amt = round(book_amt, 2), round(real_amt, 2)
    diff_amt = round(real_amt - book_amt, 2)
    match_rate = round(match_cnt / total * 100, 2) if total else 0.0
    diff_rate = round(diff_amt / book_amt * 100, 2) if book_amt else 0.0

    # ---- 5.3 写入模板 ----
    tpl = load_workbook(tpl_xlsx)
    tws = tpl[tpl.sheetnames[0]]

    def set_field(label_sub, value, fmt=None):
        for r in range(1, tws.max_row + 1):
            a = tws.cell(row=r, column=1).value
            if a is not None and label_sub in str(a):
                c = tws.cell(row=r, column=2, value=value)
                if fmt:
                    c.number_format = fmt
                return True
        print(f"  [warn] 模板未找到字段包含 '{label_sub}'")
        return False

    set_field("盘点时间", 盘点时间)
    set_field("期初金额", 期初, "¥#,##0.00")
    set_field("入库金额", 入库, "¥#,##0.00")
    set_field("销售金额", 销售, "¥#,##0.00")
    set_field("调拨金额", 调拨金额, "¥#,##0.00")
    set_field("报损金额", 报损, "¥#,##0.00")
    set_field("盘点品种总数", total, "#,##0")
    set_field("账面总金额", book_amt, "¥#,##0.00")
    set_field("实盘总金额", real_amt, "¥#,##0.00")
    set_field("账实相符品种数", match_cnt, "#,##0")
    set_field("账实相符率", match_rate, "0.00")
    set_field("差异金额", diff_amt, "¥#,##0.00")
    set_field("差异率", diff_rate, "0.00")
    tpl.save(dst_xlsx)
    print(f"[fill] 完成：盘点时间={盘点时间} 准确率={match_rate}% 差异金额={diff_amt} -> {dst_xlsx}")
    return dst_xlsx


# ============================ 命令行入口 ============================
def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    stage = sys.argv[1]
    if stage == "clean":
        src, dst = sys.argv[2], sys.argv[3]
        th = float(sys.argv[4]) if len(sys.argv) > 4 else THRESHOLD
        stage_clean(src, dst, th)
    elif stage == "shipan":
        stage_shipan(sys.argv[2], sys.argv[3])
    elif stage == "diff":
        stage_diff(sys.argv[2], sys.argv[3])
    elif stage == "negative":
        stage_negative(sys.argv[2], sys.argv[3], sys.argv[4])
    elif stage == "fill":
        stage_fill(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
    elif stage == "all":
        src_xls, jxc, tpl, outdir = sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5]
        th = float(sys.argv[6]) if len(sys.argv) > 6 else THRESHOLD
        os.makedirs(outdir, exist_ok=True)
        p1 = os.path.join(outdir, "2026Q2盘点_清洗后.xlsx")
        p2 = os.path.join(outdir, "2026Q2盘点_实盘数量.xlsx")
        p3 = os.path.join(outdir, "2026Q2盘点_负数实盘记录.xlsx")
        p4 = os.path.join(outdir, "2026Q2盘点_差异分析.xlsx")
        p5 = os.path.join(outdir, "盘点数据_已填.xlsx")
        stage_clean(src_xls, p1, th)
        stage_shipan(p1, p2)
        stage_negative(p2, p3, p4)
        stage_fill(p2, jxc, tpl, p5)
        print("[all] 全流程完成。")
    else:
        print("未知阶段：", stage)
        print(__doc__)


if __name__ == "__main__":
    main()
