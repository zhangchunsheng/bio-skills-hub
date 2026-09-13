#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
dirty_rules —— 中文表格脏数据的识别与修复规则库。

原则：**高置信度自动改，低置信度只标记**。
宁可把可疑处列进报告交给人判断，也不静默改写数据。
所有修复都返回 (新值, 动作, 置信度)，便于生成可追溯的变更日志。
"""

import re
from decimal import Decimal, InvalidOperation

# ---------------------------------------------------------------- 字符级清洗

ZERO_WIDTH = dict.fromkeys(map(ord, "​‌‍⁠﻿"), None)
# 不可见但会破坏匹配 / 去重的字符
INVISIBLE = dict.fromkeys(map(ord, "               　"), " ")


def normalize_text(s):
    """全角转半角 + 去不可见字符 + 压缩空白。返回 (结果, 是否发生改动)。"""
    if not isinstance(s, str):
        return s, False
    orig = s
    s = s.translate(ZERO_WIDTH)
    s = s.translate(INVISIBLE)
    # 全角 !-~ -> 半角
    s = "".join(chr(ord(c) - 0xFEE0) if 0xFF01 <= ord(c) <= 0xFF5E else c for c in s)
    # 全角空格已在上一步处理，这里兜底其他 Unicode 空格
    s = re.sub(r"[　 ]", " ", s)
    s = re.sub(r"[ \t]+", " ", s)
    s = s.strip()
    return s, s != orig


def normalize_brackets(s):
    """中文括号统一成半角，避免「北京（总部）」和「北京(总部)」被当成两个值。"""
    if not isinstance(s, str):
        return s, False
    orig = s
    s = s.replace("（", "(").replace("）", ")")
    s = s.replace("【", "[").replace("】", "]")
    s = s.replace("，", ",").replace("、", ",") if False else s  # 顿号不动，可能是语义分隔符
    return s, s != orig


# ---------------------------------------------------------------- 数值解析

CN_UNIT = {
    "亿": 1e8, "万": 1e4, "千": 1e3, "百": 1e2,
    "百万": 1e6, "千万": 1e7, "十万": 1e5,
}
# 只有紧跟数字才当单位，避免把"万象城"里的"万"当单位
UNIT_RE = re.compile(
    r"^\s*([<>≥≤~≈]?)\s*([+-]?[\d,，]+(?:\.\d+)?)\s*"
    r"(亿|千万|百万|十万|万|千|百)?\s*"
    r"(%|％|元|块|人民币|美元|美金|USD|US\$|\$|¥|￥|人|个|件|台|次|吨|公斤|千克|kg|KG|米|㎡|平方米|平米|小时|天|月|年|套|箱|支|只|条|辆|家|户|笔|单|份|页|张|度|瓦|W|KW|kw)?\s*$"
)

PERCENT_RE = re.compile(r"^\s*([+-]?[\d,，]+(?:\.\d+)?)\s*(%|％)\s*$")
PAREN_NEG_RE = re.compile(r"^\s*\(([\d,，]+(?:\.\d+)?)\)\s*$")
RANGE_RE = re.compile(r"^\s*([+-]?[\d,，]+(?:\.\d+)?)\s*[-~—至到]\s*([+-]?[\d,，]+(?:\.\d+)?)\s*$")
TEXTNUM_RE = re.compile(r"^\s*([+-]?\d+(?:\.\d+)?)\s*$")


def _num(txt):
    """
    用 Decimal，不用 float。
    中文单位换算是重灾区：5.06 * 10000 用浮点会得到 50599.99999999999，
    金额差一分钱都是事故。
    """
    return Decimal(txt.replace(",", "").replace("，", ""))


def _fmt(v):
    """整数就不带小数点，避免 100 变成 100.0。"""
    if isinstance(v, Decimal):
        if v == v.to_integral_value() and abs(v) < Decimal("1e15"):
            return int(v)
        return float(v)
    if isinstance(v, float) and v.is_integer() and abs(v) < 1e15:
        return int(v)
    return v


def parse_number(s, percent="keep"):
    """
    把"带中文单位的文本"解析成真正的数字。

    返回 (value, unit, note)。value 为 None 表示没识别出数字。
    percent: 'keep' 保留 35（不除 100）；'decimal' 转成 0.35。
    """
    if not isinstance(s, str):
        if isinstance(s, (int, float)):
            return s, None, "numeric"
        return None, None, "not-text"
    t = s.strip()
    if not t:
        return None, None, "empty"

    # 纯数字文本（含千分位），Excel 里左上角带绿三角的那种
    if re.match(r"^\s*[+-]?[\d,，]+(\.\d+)?\s*$", t) and re.search(r"\d", t):
        try:
            return _fmt(_num(t)), None, "text-number"
        except (ValueError, InvalidOperation):
            pass

    m = PERCENT_RE.match(t)
    if m:
        v = _num(m.group(1))
        return (_fmt(v / Decimal(100)) if percent == "decimal" else _fmt(v)), "%", "percent"

    m = PAREN_NEG_RE.match(t)
    if m:
        return -_fmt(_num(m.group(1))), None, "paren-negative"

    m = RANGE_RE.match(t)
    if m:
        # 范围不猜中值，取下限并标记，避免制造假数据
        return _fmt(_num(m.group(1))), None, "range-take-lower"

    m = UNIT_RE.match(t)
    if m and m.group(2):
        sign, digits, unit, tail = m.groups()
        try:
            v = _num(digits)
        except (ValueError, InvalidOperation):
            return None, None, "unmatched"
        if unit:
            v = v * Decimal(str(CN_UNIT[unit]))
        if tail in ("%", "％"):
            if percent == "decimal":
                v = v / Decimal(100)
            tail = "%"
        if sign in ("-", "＜", "<"):
            # 仅 "≤/≈/~" 这类前缀保留原值，负号才取反
            if sign == "-":
                v = -v
        return _fmt(v), (unit or tail), ("unit:" + (unit or tail or "")) if (unit or tail) else "number"

    return None, None, "unmatched"


# ---------------------------------------------------------------- 日期解析

DATE_PATTERNS = [
    (re.compile(r"^(\d{4})\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})\s*[日号]$"), "ymd-cn"),
    (re.compile(r"^(\d{4})[.\-/](\d{1,2})[.\-/](\d{1,2})$"), "ymd-sep"),
    (re.compile(r"^(\d{4})\s*年\s*(\d{1,2})\s*月$"), "ym-cn"),
    (re.compile(r"^(\d{1,2})\s*月\s*(\d{1,2})\s*[日号]$"), "md-cn"),
    (re.compile(r"^(\d{4})(\d{2})(\d{2})$"), "ymd-compact"),
    (re.compile(r"^(\d{4})\s*年?\s*[Qq]([1-4])$"), "quarter"),
    (re.compile(r"^(\d{4})\s*年?\s*第?\s*([一二三四1-4])\s*季度$"), "quarter-cn"),
]


def parse_date(s, default_year=None):
    """
    中文日期文本 -> ISO 字符串。识别不了返回 None。
    无年份的（如"3月5日")必须给 default_year，否则不猜——避免跨年数据错位。
    """
    if not isinstance(s, str):
        return None
    t = normalize_text(s)[0]
    for rx, kind in DATE_PATTERNS:
        m = rx.match(t)
        if not m:
            continue
        g = m.groups()
        try:
            if kind in ("ymd-cn", "ymd-sep", "ymd-compact"):
                y, mo, d = int(g[0]), int(g[1]), int(g[2])
                if not (1 <= mo <= 12 and 1 <= d <= 31):
                    continue
                return "%04d-%02d-%02d" % (y, mo, d)
            if kind == "ym-cn":
                y, mo = int(g[0]), int(g[1])
                if not 1 <= mo <= 12:
                    continue
                return "%04d-%02d" % (y, mo)
            if kind == "md-cn":
                if default_year is None:
                    return None
                mo, d = int(g[0]), int(g[1])
                if not (1 <= mo <= 12 and 1 <= d <= 31):
                    continue
                return "%04d-%02d-%02d" % (int(default_year), mo, d)
            if kind == "quarter":
                return "%s-Q%s" % (g[0], g[1])
            if kind == "quarter-cn":
                cn = {"一": 1, "二": 2, "三": 3, "四": 4}
                q = cn.get(g[1]) or int(g[1])
                return "%s-Q%d" % (g[0], q)
        except (ValueError, TypeError):
            continue
    return None


# ---------------------------------------------------------------- 结构级诊断

TOTAL_ROW_HINT = re.compile(r"^\s*(合\s*计|总\s*计|小\s*计|总\s*和|total|sum|合\s*共|总\s*额)\s*[:：]?\s*$", re.I)
TOTAL_CELL_HINT = re.compile(r"(合\s*计|总\s*计|小\s*计|total|sum)", re.I)
NOTE_ROW_HINT = re.compile(r"^\s*(注|备注|说明|注\s*释|数据来源|填表人|制表|审核|单位[:：])", re.I)

# 中文表格里到处都是的占位符。它们看着像数据，其实表示"没有值"。
# 不自动删，只在报告里提示——有些场景"无"是有语义的。
PLACEHOLDER = re.compile(
    r"^\s*(-{1,3}|－|—|/{1,2}|N/?A|na|null|none|无|暂无|待定|待补|未知|不需|不适用|\?{1,3}|待填|尚未)\s*$",
    re.I)


def is_blank_row(row):
    return all(v is None or (isinstance(v, str) and not v.strip()) for v in row)


def is_blank_col(col):
    return all(v is None or (isinstance(v, str) and not v.strip()) for v in col)


def detect_header_row(rows, scan=15):
    """
    猜表头在哪一行。中文表常见：
      - 第 1 行是大标题（"2024年销售明细表"），第 2 行才是真表头
      - 前几行是填报说明
    打分逻辑：候选行应"几乎无空值 + 多为短文本 + 下一行类型不同 + 非空值率显著高于上一行"。
    返回 (行号 0 基, 置信度 0-1, 理由)。
    """
    if not rows:
        return 0, 0.0, "空表"
    limit = min(scan, len(rows))
    best = (0, 0.0, "默认首行")

    def nonblank(r):
        return sum(1 for v in r if v is not None and (not isinstance(v, str) or v.strip()))

    for i in range(limit):
        r = rows[i]
        if not r:
            continue
        nb = nonblank(r)
        if nb == 0:
            continue
        width = len(r)
        fill = nb / max(1, width)
        texty = sum(1 for v in r if isinstance(v, str) and v.strip() and len(v.strip()) <= 12)
        short_ratio = texty / max(1, nb)

        score = 0.0
        reasons = []
        if fill >= 0.8:
            score += 0.35
            reasons.append("该行填充率高")
        elif fill >= 0.5:
            score += 0.15
        if short_ratio >= 0.8:
            score += 0.25
            reasons.append("多为短文本(像列名)")

        # 上一行若是"大标题"（只有一个合并大格或单格文本），本行更像真表头
        if i > 0:
            prev_nb = nonblank(rows[i - 1])
            if prev_nb <= 1 and nb >= 3:
                score += 0.3
                reasons.append("上一行像大标题/说明行")
            elif prev_nb < nb:
                score += 0.1
        if i == 0:
            score += 0.05  # 轻微偏好首行，避免误判

        # 下一行如果能解析出数字/日期，说明本行确实是表头
        if i + 1 < len(rows):
            nxt = rows[i + 1]
            typed = sum(
                1 for v in nxt
                if v is not None and (
                    isinstance(v, (int, float))
                    or (isinstance(v, str) and (parse_number(v)[0] is not None or parse_date(v)))
                )
            )
            if typed >= max(1, nb // 2):
                score += 0.25
                reasons.append("下一行出现数值/日期")

        if score > best[1]:
            best = (i, min(score, 1.0), "；".join(reasons) or "综合打分")

    return best


def detect_blocks(rows, header_row):
    """
    一个 sheet 里塞了多张表时，用"空行 + 疑似小标题行"切块。
    返回 list[(start, end, 标题或 None)]。
    """
    blocks = []
    start = header_row
    i = header_row + 1
    while i < len(rows):
        if is_blank_row(rows[i]):
            j = i
            while j < len(rows) and is_blank_row(rows[j]):
                j += 1
            if j < len(rows):
                nb = sum(1 for v in rows[j] if v is not None and (not isinstance(v, str) or v.strip()))
                title = None
                if nb <= 2:
                    # 小标题行：只有一两格有内容
                    cand = [v for v in rows[j] if v is not None and str(v).strip()]
                    title = str(cand[0]).strip() if cand else None
                blocks.append((start, i, None))
                start = j + (1 if title else 0)
                i = j + (1 if title else 0)
                if title:
                    blocks[-1] = (blocks[-1][0], blocks[-1][1], None)
                continue
        i += 1
    if start < len(rows):
        blocks.append((start, len(rows), None))
    return [b for b in blocks if b[1] > b[0]]


def column_profile(rows, header_row, ci):
    """
    分析某一列的数据特征，返回 dict。用于判断类型混乱程度。
    """
    vals = []
    for r in rows[header_row + 1:]:
        if ci < len(r):
            v = r[ci]
            if v is not None and (not isinstance(v, str) or v.strip()):
                vals.append(v)
    if not vals:
        return {"n": 0, "types": {}, "numeric_ratio": 0.0, "date_ratio": 0.0, "textnum_ratio": 0.0, "unit_ratio": 0.0}

    types = {}
    numeric = datelike = textnum = unit_num = 0
    for v in vals:
        if isinstance(v, bool):
            types["bool"] = types.get("bool", 0) + 1
        elif isinstance(v, (int, float)):
            types["number"] = types.get("number", 0) + 1
            numeric += 1
        elif isinstance(v, str):
            if PLACEHOLDER.match(v):
                types["placeholder"] = types.get("placeholder", 0) + 1
                continue
            if parse_date(v):
                types["date"] = types.get("date", 0) + 1
                datelike += 1
                continue
            nv, unit, note = parse_number(v)
            if nv is not None:
                types["text-number"] = types.get("text-number", 0) + 1
                textnum += 1
                if unit:
                    unit_num += 1
            else:
                types["text"] = types.get("text", 0) + 1
        else:
            types["other"] = types.get("other", 0) + 1
    n = len(vals)
    return {
        "n": n,
        "types": types,
        "placeholder": types.get("placeholder", 0),
        "numeric_ratio": numeric / n,
        "date_ratio": datelike / n,
        "textnum_ratio": textnum / n,
        "unit_ratio": unit_num / n,
        "mixed": len([k for k in types if k != "text"]) > 1 and "text" in types,
    }
