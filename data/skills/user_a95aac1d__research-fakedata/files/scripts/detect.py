#!/usr/bin/env python3
"""
论文数据造假检测器 — 单篇 PDF 全自动检测管线
=============================================
输入：一篇学术论文 PDF
输出：HTML 造假嫌疑报告

流程：提取元数据 → 提取数值表格 → 运行 9 种检测器 → 生成 HTML 报告

检测器（来源：Hartgerink statcheck, Benford, 耿同学 paperconan）：
  1. 末位数字卡方检验      6. 取整异常
  2. 固定差值              7. 本福特定律
  3. 固定倍数              8. 完全重复列
  4. 等差数列/等比数列      9. 跨页同位置相同
  5. 小数位重复

GRIM 需要从表头/段落提取样本量 n，推迟到 v2.0。

用法：python detect.py path/to/paper.pdf [-o report.html]
"""

import json
import os
import sys
import warnings
import time
import math
import re
from pathlib import Path
from collections import Counter

warnings.filterwarnings("ignore")

# ── 依赖检测 ──────────────────────────────────────────────
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

try:
    import fitz  # PyMuPDF
    HAS_FITZ = True
except ImportError:
    HAS_FITZ = False

try:
    import pdfplumber
    HAS_PDFPLUMBER = True
except ImportError:
    HAS_PDFPLUMBER = False

try:
    import camelot
    HAS_CAMELOT = True
except ImportError:
    HAS_CAMELOT = False

HAS_SCIPY = True
try:
    from scipy import stats as scipy_stats
except ImportError:
    HAS_SCIPY = False

HAS_PANDAS = True
try:
    import pandas as pd
except ImportError:
    HAS_PANDAS = False


# ═══════════════════════════════════════════════════════════
# 常量
# ═══════════════════════════════════════════════════════════

MIN_ROW_COUNT = 5
CHI2_THRESHOLD = 0.05
DECIMAL_MIN_REPEATS = 3
DECIMAL_MIN_LEN = 4
RATIO_TOL = 0.001
OFFSET_TOL_REL = 0.01
CV_THRESHOLD = 0.3
SPAN_RANGE_RATIO = 0.30
BENFORD_MIN_COUNT = 20
GRID_EPSILON = 0.01
ACTIVE_DETECTOR_COUNT = 9
PIP_PACKAGE_NAMES = {
    "numpy": "numpy",
    "PyMuPDF (fitz)": "pymupdf",
    "scipy": "scipy",
    "pdfplumber": "pdfplumber",
    "pandas": "pandas",
    "camelot-py": "camelot-py",
    "opencv-python": "opencv-python",
}

# ═══════════════════════════════════════════════════════════
# 工具函数
# ═══════════════════════════════════════════════════════════

def is_numeric_col(series) -> bool:
    """判断一列是否为数值列（≥80% 可转为数字）"""
    vals = [v for v in series if v is not None and not (isinstance(v, float) and math.isnan(v))]
    if len(vals) < MIN_ROW_COUNT:
        return False
    numeric = 0
    for v in vals:
        if isinstance(v, (int, float)):
            numeric += 1
        elif isinstance(v, str):
            try:
                float(v.replace(',', '').replace(' ', ''))
                numeric += 1
            except ValueError:
                pass
    return numeric / len(vals) > 0.8


def to_numeric(v):
    """尝试转为 float，失败返回 None"""
    if v is None:
        return None
    if isinstance(v, (int, float)):
        if math.isnan(v) or math.isinf(v):
            return None
        return float(v)
    if isinstance(v, str):
        try:
            return float(v.replace(',', '').replace(' ', '').strip())
        except ValueError:
            return None
    return None


def last_significant_digit(v):
    """返回数值展示中的最后一个有效数字，避免固定小数格式补零造成误报。"""
    if v is None:
        return None
    try:
        value = abs(float(v))
    except (TypeError, ValueError):
        return None
    if math.isnan(value) or math.isinf(value):
        return None

    text = f"{value:.12g}"
    if "e" in text.lower():
        text = f"{value:.12f}"
    text = text.rstrip("0").rstrip(".")
    digits = [ch for ch in text if ch.isdigit()]
    if not digits:
        return None
    return int(digits[-1])


def build_install_hint(missing):
    packages = [PIP_PACKAGE_NAMES.get(name, name) for name in missing]
    return "pip install " + " ".join(packages)


# ═══════════════════════════════════════════════════════════
# 红旗辅助：注入定位 + 证据，方便人工回查 PDF
# ═══════════════════════════════════════════════════════════

def _enrich_flag(flag, sheet, col_name, evidence_vals=None, is_pair=False, col_name_b=None, evidence_vals_b=None):
    """为红旗注入定位信息（页码/表格序号/列名）+ 前 N 行证据样本。
    调用方保证 sheet 包含 page / table_num_on_page 字段。
    """
    flag["page"] = sheet.get("page", "?")
    flag["table_num_on_page"] = sheet.get("table_num_on_page", 1)
    flag["table_name"] = sheet.get("name", "?")
    flag["column_name"] = col_name

    # 构造人类看一眼就能定位的描述
    flag["location"] = f"Page {flag['page']}, 表格 {flag['table_num_on_page']}, 列「{col_name}」"

    if is_pair and evidence_vals is not None and evidence_vals_b is not None:
        pairs = []
        for a, b in zip(evidence_vals[:5], evidence_vals_b[:5]):
            if a is not None and b is not None:
                pairs.append(f"({round(a,4)}, {round(b,4)})")
        flag["column_name_pair"] = col_name_b
        flag["evidence_text"] = f"{col_name} ↔ {col_name_b}: {' '.join(pairs)}" if pairs else ""
    elif evidence_vals is not None:
        show = [round(v, 4) if v is not None else "—" for v in evidence_vals[:8]]
        flag["evidence_text"] = f"[{', '.join(str(x) for x in show)}]"
    else:
        flag["evidence_text"] = ""

    return flag


# ═══════════════════════════════════════════════════════════
# 检测器 1-9
# ═══════════════════════════════════════════════════════════

def last_digit_chi_square(values, sheet_name, col_name):
    """末位数字卡方检验 — 均匀性偏离"""
    if not HAS_SCIPY:
        return None
    digits = []
    for v in values:
        if v is None:
            continue
        digit = last_significant_digit(v)
        if digit is not None:
            digits.append(digit)
    if len(digits) < 20:
        return None
    observed = Counter(digits)
    expected = len(digits) / 10
    chi2 = sum((observed.get(d, 0) - expected) ** 2 / expected for d in range(10))
    p_value = 1.0 - scipy_stats.chi2.cdf(chi2, df=9)
    if p_value < CHI2_THRESHOLD:
        deviations = {d: (observed.get(d, 0) - expected) / expected for d in range(10)}
        top_digits = sorted(deviations.items(), key=lambda x: abs(x[1]), reverse=True)[:3]
        detail_parts = []
        for d, dev in top_digits:
            obs_pct = observed.get(d, 0) / len(digits) * 100
            detail_parts.append(f"末位{d}: {obs_pct:.1f}% (期望10%, 偏差{dev:+.1%})")
        return {
            "type": "last_digit_anomaly", "severity": "high" if p_value < 0.001 else "medium",
            "risk_score": min(90, 50 + int(40 * (1 - p_value / 0.05))),
            "p_value": round(p_value, 6), "chi2": round(chi2, 2), "n": len(digits),
            "top_deviations": detail_parts[:3],
            "detail": f"{col_name}: χ²={chi2:.1f}, p={p_value:.4f}; " + "; ".join(detail_parts[:2]),
        }
    return None


def check_constant_offset(col_a, col_b, name_a, name_b):
    """固定差值 — 两列差值恒为常数"""
    pairs = [(a, b) for a, b in zip(col_a, col_b) if a is not None and b is not None]
    if len(pairs) < MIN_ROW_COUNT:
        return None
    offsets = [b - a for a, b in pairs]
    mean_offset = np.mean(offsets)
    if mean_offset == 0:
        return None
    max_dev = max(abs(o - mean_offset) for o in offsets)
    tol = max(abs(mean_offset) * OFFSET_TOL_REL, 0.01)
    if max_dev > tol:
        return None
    clean_a = [v for v in col_a if v is not None]
    if len(clean_a) < 2:
        return None
    range_a = max(clean_a) - min(clean_a)
    if range_a < 0.001:
        return None
    offset_std = float(np.std(offsets))
    cv = offset_std / abs(mean_offset) if abs(mean_offset) > 1e-10 else float('inf')
    if cv > CV_THRESHOLD:
        return None
    offset_span = max(offsets) - min(offsets)
    if range_a > 1e-10 and offset_span / range_a > SPAN_RANGE_RATIO:
        return None
    score = min(90, 50 + 40 * (len(pairs) / max(len(pairs), 20)))
    return {
        "type": "constant_offset", "severity": "high", "risk_score": round(score),
        "columns": [name_a, name_b], "offset": round(mean_offset, 6), "n_pairs": len(pairs),
        "max_deviation": round(max_dev, 6),
        "detail": f"{name_b} = {name_a} + {mean_offset:.4f} (n={len(pairs)}, max_dev={max_dev:.4f})",
    }


def check_constant_ratio(col_a, col_b, name_a, name_b):
    """固定倍数 — 两列比值恒为常数"""
    pairs = [(a, b) for a, b in zip(col_a, col_b) if a is not None and b is not None and abs(a) > 0.0001]
    if len(pairs) < MIN_ROW_COUNT:
        return None
    ratios = [b / a for a, b in pairs]
    mean_ratio = np.mean(ratios)
    if mean_ratio <= 0:
        return None
    deviations = [abs(r - mean_ratio) / abs(mean_ratio) for r in ratios]
    max_rel_dev = max(deviations)
    if max_rel_dev > RATIO_TOL:
        return None
    near_integer = abs(mean_ratio - round(mean_ratio)) < 0.02
    if abs(mean_ratio - 1.0) < 0.001:
        return None
    clean_a = [v for v in col_a if v is not None]
    if len(clean_a) < 2 or max(clean_a) - min(clean_a) < 0.001:
        return None
    score = min(95, 60 + 35 * near_integer + 25 * (len(pairs) / max(len(pairs), 20)))
    return {
        "type": "constant_ratio", "severity": "high", "risk_score": round(score),
        "columns": [name_a, name_b], "ratio": round(mean_ratio, 4),
        "near_integer": near_integer, "n_pairs": len(pairs), "max_rel_dev": round(max_rel_dev, 6),
        "detail": f"{name_b} = {name_a} × {mean_ratio:.4f}" + (" (接近整数)" if near_integer else "") + f" (n={len(pairs)})",
    }


def check_arithmetic_progression(values, col_name):
    """等差/等比数列 — 完美规律性"""
    vals = [v for v in values if v is not None]
    if len(vals) < 8:
        return None
    # 检查等差
    diffs = [vals[i + 1] - vals[i] for i in range(len(vals) - 1)]
    if len(set(round(d, 6) for d in diffs)) == 1 and diffs[0] != 0:
        step = diffs[0]
        if step == 1.0:  # 页码
            return None
        if step == 5.0 and all(v == int(v) and v > 0 for v in vals):  # 行号
            return None
        if all(v == int(v) for v in vals):
            er = (len(vals) - 1) * abs(step)
            ar = max(vals) - min(vals)
            if abs(ar - er) < 0.01 and min(vals) < 20:  # 序列号
                return None
        return {
            "type": "arithmetic_progression", "severity": "high", "risk_score": 85,
            "column": col_name, "step": round(step, 4), "n": len(vals),
            "detail": f"{col_name}: 完美等差数列, step={step:.4f}, n={len(vals)}",
        }
    # 检查等比
    ratios = [vals[i + 1] / vals[i] for i in range(len(vals) - 1) if vals[i] != 0 and vals[i + 1] != 0]
    if len(ratios) == len(vals) - 1:
        ur = set(round(r, 6) for r in ratios)
        if len(ur) == 1 and abs(ratios[0] - 1) > 0.01:
            return {
                "type": "geometric_progression", "severity": "high", "risk_score": 85,
                "column": col_name, "ratio": round(ratios[0], 6), "n": len(vals),
                "detail": f"{col_name}: 完美等比数列, ratio={ratios[0]:.6f}, n={len(vals)}",
            }
    return None


def check_decimal_repetition(values, col_name):
    """小数位重复 — 小数点后几位批量重复"""
    decimals = []
    for v in values:
        if v is None:
            continue
        s = f"{abs(v):.10f}"
        if '.' in s:
            dec = s.split('.')[1].rstrip('0')
            if len(dec) >= DECIMAL_MIN_LEN:
                decimals.append(dec[:DECIMAL_MIN_LEN])
    if len(decimals) < 10:
        return None
    counter = Counter(decimals)
    repeated = [(d, c) for d, c in counter.items() if c >= DECIMAL_MIN_REPEATS]
    if not repeated:
        return None
    repeated.sort(key=lambda x: -x[1])
    top = repeated[:3]
    ratio = top[0][1] / len(decimals)
    if ratio < 0.15:
        return None
    return {
        "type": "decimal_repetition", "severity": "high" if ratio > 0.3 else "medium",
        "risk_score": round(min(80, 40 + 40 * ratio)),
        "column": col_name, "top_repeats": [f"'{d}' ×{c}" for d, c in top],
        "n_total": len(decimals),
        "detail": f"{col_name}: 小数位重复, " + ", ".join(f"'{d}'×{c}" for d, c in top),
    }


def check_rounded_to_grid(values, col_name):
    """取整异常 — 数据过度落在某网格上"""
    vals = [v for v in values if v is not None]
    if len(vals) < 10:
        return None
    for grid in [0.5, 0.25, 0.2, 0.1]:
        on_grid = sum(1 for v in vals if abs(v - round(v / grid) * grid) < GRID_EPSILON * grid)
        ratio = on_grid / len(vals)
        if ratio > 0.95:
            return {
                "type": "rounded_to_grid", "severity": "medium",
                "risk_score": round(60 + 40 * ratio),
                "column": col_name, "grid": grid, "on_grid_ratio": round(ratio, 3), "n": len(vals),
                "detail": f"{col_name}: {ratio*100:.1f}% 数据精确落在 {grid} 网格上 (n={len(vals)})",
            }
    return None


def check_benford(values, col_name):
    """本福特定律 — 首位数字分布偏离"""
    if not HAS_SCIPY:
        return None
    first_digits = []
    for v in values:
        if v is None or v == 0:
            continue
        s = f"{abs(v):.10e}"
        for ch in s:
            if ch in '123456789':
                first_digits.append(int(ch))
                break
    if len(first_digits) < BENFORD_MIN_COUNT:
        return None
    benford_expected = {d: math.log10(1 + 1 / d) for d in range(1, 10)}
    observed = Counter(first_digits)
    total = len(first_digits)
    chi2 = 0
    deviations = []
    for d in range(1, 10):
        ec = benford_expected[d] * total
        oc = observed.get(d, 0)
        chi2 += (oc - ec) ** 2 / ec
        deviations.append((d, (oc - ec) / ec))
    p_value = 1.0 - scipy_stats.chi2.cdf(chi2, df=8)
    if p_value < 0.05:
        top_dev = sorted(deviations, key=lambda x: abs(x[1]), reverse=True)[:3]
        dd = "; ".join(f"首位{d}: {observed.get(d,0)/total:.1%}" for d, _ in top_dev)
        return {
            "type": "benford_violation", "severity": "medium",
            "risk_score": min(80, 40 + int(40 * (1 - p_value))),
            "p_value": round(p_value, 6), "chi2": round(chi2, 2), "n": total,
            "detail": f"{col_name}: 本福特偏离, χ²={chi2:.1f}, p={p_value:.4f}; {dd}",
        }
    return None


def check_identical_columns(col_a, col_b, name_a, name_b):
    """完全重复列 — 两列数据相同"""
    pairs = [(a, b) for a, b in zip(col_a, col_b) if a is not None and b is not None]
    if len(pairs) < MIN_ROW_COUNT:
        return None
    identical = sum(1 for a, b in pairs if abs(a - b) < 1e-10)
    ratio = identical / len(pairs)
    if ratio > 0.9 and len(pairs) >= 5:
        clean_a = [v for v in col_a if v is not None]
        if len(clean_a) < 2 or max(clean_a) - min(clean_a) < 0.001:
            return None
        return {
            "type": "identical_columns", "severity": "high" if ratio > 0.99 else "medium",
            "risk_score": round(70 + 30 * ratio),
            "columns": [name_a, name_b], "identical_ratio": round(ratio, 3), "n": len(pairs),
            "detail": f"{name_a} ≡ {name_b}: {identical}/{len(pairs)} ({ratio*100:.1f}%) 完全一致",
        }
    return None


def sheet_numeric_signature(sheet):
    signature = []
    for col in sheet.get("columns", []):
        signature.append(tuple(None if v is None else round(float(v), 8) for v in col))
    return tuple(signature)


def is_duplicate_extraction(sheet_a, sheet_b):
    """判断两张 sheet 是否更像同页同表的重复抽取，而不是跨表复用。"""
    if sheet_a.get("page") != sheet_b.get("page"):
        return False
    return sheet_numeric_signature(sheet_a) == sheet_numeric_signature(sheet_b)


def check_cross_sheet_identical(all_sheets, file_name):
    """跨表同位置相同 — 不同表格数据重复"""
    flags = []
    for i in range(len(all_sheets)):
        for j in range(i + 1, len(all_sheets)):
            s_a, s_b = all_sheets[i], all_sheets[j]
            if is_duplicate_extraction(s_a, s_b):
                continue
            cols_a, cols_b = s_a["columns"], s_b["columns"]
            min_rows = min(len(c) for c in cols_a + cols_b) if cols_a and cols_b else 0
            min_cols = min(len(cols_a), len(cols_b))
            matched_cells = []  # 收集匹配的单元格用于证据
            identical_count, total_checked = 0, 0
            for ci in range(min_cols):
                for ri in range(min(min_rows, len(cols_a[ci]), len(cols_b[ci]))):
                    va, vb = cols_a[ci][ri], cols_b[ci][ri]
                    if va is not None and vb is not None:
                        total_checked += 1
                        if abs(va - vb) < 1e-10:
                            identical_count += 1
                            if len(matched_cells) < 5:
                                matched_cells.append((ci, ri, round(va, 4)))
            if total_checked > 10 and identical_count / total_checked > 0.7:
                evidence = ", ".join(f"[c{ci},r{ri}]={v}" for ci, ri, v in matched_cells)
                flags.append({
                    "type": "cross_sheet_identical", "severity": "high", "risk_score": 80,
                    "sheet_a": s_a["name"], "sheet_b": s_b["name"],
                    "identical_ratio": round(identical_count / total_checked, 3), "n": total_checked,
                    "detail": f"Sheet '{s_a['name']}' vs '{s_b['name']}': {identical_count}/{total_checked} 同位置相同",
                    "evidence_text": f"匹配单元格: {evidence}" if evidence else "",
                })
    return flags


# 检测器注册表
DETECTOR_FUNCS = {
    "last_digit_chi_square": last_digit_chi_square,
    "check_constant_offset": check_constant_offset,
    "check_constant_ratio": check_constant_ratio,
    "check_arithmetic_progression": check_arithmetic_progression,
    "check_decimal_repetition": check_decimal_repetition,
    "check_rounded_to_grid": check_rounded_to_grid,
    "check_benford": check_benford,
    "check_identical_columns": check_identical_columns,
    "check_cross_sheet_identical": check_cross_sheet_identical,
}


# ═══════════════════════════════════════════════════════════
# 第一步：PDF 元数据提取
# ═══════════════════════════════════════════════════════════

def extract_pdf_meta(pdf_path):
    """从 PDF 提取标题、作者、DOI、PMID"""
    meta = {"title": "", "authors": [], "doi": "", "pmid": "", "pages": 0}
    try:
        doc = fitz.open(pdf_path)
        meta["pages"] = len(doc)
        text = ""
        for page_num in range(min(2, len(doc))):
            text += doc[page_num].get_text()
        lines = [l.strip() for l in text.split("\n") if l.strip()]

        # DOI
        for pattern in [
            r'(?:DOI|doi)[:\s]*(10\.\d{4,}/[^\s]+)',
            r'doi\.org/(10\.\d{4,}/[^\s]+)',
            r'(?:^|\n)\s*(10\.\d{4,}/[^\s]{10,})\s*(?:\n|$)',
        ]:
            m = re.search(pattern, text)
            if m:
                meta["doi"] = m.group(1).rstrip('.')
                break

        # PMID
        m = re.search(r'PMID:\s*(\d+)', text)
        if m:
            meta["pmid"] = m.group(1)

        # Title — 支持 "Title:" 前缀和常规格式
        title_lines = []
        collecting_title = False
        title_candidates = []
        for l in lines[:30]:
            l = l.strip()
            if not l or len(l) < 5:
                continue
            if l.lower().startswith("title:") or l.lower().startswith("title "):
                collecting_title = True
                rest = re.sub(r'^[Tt]itle\s*:\s*', '', l)
                if rest:
                    title_lines.append(rest)
                continue
            if collecting_title:
                if any(l.startswith(kw) for kw in ["Authors:", "Affiliations:", "Abstract:", "†", "‡"]):
                    collecting_title = False
                    continue
                if re.match(r'^\d{1,3}$', l):
                    continue
                title_lines.append(l)
                if sum(len(t) for t in title_lines) > 300:
                    collecting_title = False
                continue
            if len(l) < 40 or l.startswith("http") or l.startswith("DOI") or l.startswith("PMID"):
                continue
            if l.count(",") > 5 and len(l.split(",")[0]) < 15:
                continue
            if re.search(r'^\d|[@#]|University|Institute|College|Laboratory|Department|Hospital|Center|Centre|School|Academy', l):
                continue
            title_candidates.append(l)

        if title_lines:
            meta["title"] = " ".join(title_lines)[:300]
        elif title_candidates:
            meta["title"] = max(title_candidates, key=len)[:300]
        elif lines:
            for l in lines:
                if len(l) > 40:
                    meta["title"] = l[:300]
                    break

        # Authors
        for line in lines[:20]:
            if "," in line and 20 < len(line) < 500:
                if re.search(r'[A-Z][a-z]+,\s*[A-Z]', line):
                    parts = line.split(";")
                    for part in parts[:10]:
                        name = part.strip().split(",")[0].strip()
                        if 3 < len(name) < 30:
                            meta["authors"].append(name)
                    break

        doc.close()
    except Exception as e:
        print(f"  [警告] PDF 元数据提取失败: {e}", file=sys.stderr)
    return meta


# ═══════════════════════════════════════════════════════════
# 第二步：表格提取（双引擎）
# ═══════════════════════════════════════════════════════════

def extract_tables_camelot(pdf_path):
    """Camelot 提取表格（lattice + stream）"""
    if not HAS_CAMELOT:
        return []
    tables = []
    try:
        for t in camelot.read_pdf(pdf_path, pages="all", flavor="lattice"):
            tables.append({"source": "camelot_lattice", "page": t.page, "shape": t.shape,
                           "df": t.df, "accuracy": t.parsing_report.get("accuracy", 0)})
    except Exception:
        pass
    try:
        for t in camelot.read_pdf(pdf_path, pages="all", flavor="stream", edge_tol=50, row_tol=10):
            # 去重：page + shape 相同 且 首格内容一致 → 判为重复
            dup = False
            for s in tables:
                if s["page"] == t.page and s["shape"] == t.shape:
                    try:
                        if s["df"].iloc[0, 0] == t.df.iloc[0, 0]:
                            dup = True
                            break
                    except Exception:
                        pass
            if not dup:
                tables.append({"source": "camelot_stream", "page": t.page, "shape": t.shape,
                               "df": t.df, "accuracy": t.parsing_report.get("accuracy", 0)})
    except Exception as e:
        print(f"  Camelot stream 失败: {e}", file=sys.stderr)
    return tables


def extract_tables_pdfplumber(pdf_path):
    """pdfplumber 提取表格（补充 Camelot 漏掉的）"""
    if not HAS_PDFPLUMBER or not HAS_PANDAS:
        return []
    tables = []
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                for t in page.extract_tables():
                    if not t or len(t) < 2:
                        continue
                    headers = t[0] if t else []
                    rows = t[1:] if len(t) > 1 else []
                    ncols = len(headers)
                    df = pd.DataFrame(rows, columns=headers if ncols and rows and len(rows[0]) == ncols else None)
                    tables.append({
                        "source": "pdfplumber", "page": page_num,
                        "shape": (len(rows), ncols), "df": df, "accuracy": 0.7,
                    })
    except Exception as e:
        print(f"  pdfplumber 失败: {e}", file=sys.stderr)
    return tables


def table_to_sheet(table, page=None, table_num_on_page=1):
    """表格转检测器 sheet 格式。文本占比<15% 的纯文本块返回 None

    page, table_num_on_page: 由 main() 传入，用于精确定位（"Page X, 第 Y 个表格"）。
    """
    df = table["df"]
    n_rows, n_cols = table["shape"]
    pg = page or table.get("page", "?")

    # 过滤纯文本块（Camelot 误抓的正文段落）
    numeric_cells, total_cells = 0, 0
    for r in range(min(20, n_rows)):
        for c in range(n_cols):
            val = df.iloc[r, c] if r < len(df) else None
            total_cells += 1
            if to_numeric(val) is not None:
                numeric_cells += 1
    if total_cells > 0 and numeric_cells / total_cells < 0.15:
        return None

    headers = [str(df.iloc[0, c]).strip() if n_rows > 0 and str(df.iloc[0, c]) else f"col_{c}"
               for c in range(n_cols)]

    columns = []
    for c in range(n_cols):
        col_vals = [to_numeric(df.iloc[r, c]) for r in range(1, n_rows) if r < len(df)]
        columns.append(col_vals)

    return {
        "name": f"Page{pg}_Table{table_num_on_page}_{table['source']}",
        "page": pg,
        "table_num_on_page": table_num_on_page,
        "headers": headers,
        "columns": columns,
    }


# ═══════════════════════════════════════════════════════════
# 第三步：运行检测器
# ═══════════════════════════════════════════════════════════

def run_detectors(sheets):
    """对所有 sheet 运行全部检测器，每个 flag 注入定位 + 证据"""
    all_flags = []
    for sheet in sheets:
        cols, headers = sheet["columns"], sheet["headers"]
        numeric_cols = []
        for ci, col in enumerate(cols):
            nv = [v for v in col if v is not None]
            if is_numeric_col(nv):
                numeric_cols.append((ci, col, headers[ci] if ci < len(headers) else f"col_{ci}"))

        if len(numeric_cols) < 1:
            continue

        for ci, col, name in numeric_cols:
            vals = [v for v in col if v is not None]

            r = DETECTOR_FUNCS["last_digit_chi_square"](vals, sheet["name"], name)
            if r: all_flags.append(_enrich_flag(r, sheet, name, vals))
            r = DETECTOR_FUNCS["check_arithmetic_progression"](vals, name)
            if r: all_flags.append(_enrich_flag(r, sheet, name, vals))
            r = DETECTOR_FUNCS["check_decimal_repetition"](vals, name)
            if r: all_flags.append(_enrich_flag(r, sheet, name, vals))
            r = DETECTOR_FUNCS["check_rounded_to_grid"](vals, name)
            if r: all_flags.append(_enrich_flag(r, sheet, name, vals))
            r = DETECTOR_FUNCS["check_benford"](vals, name)
            if r: all_flags.append(_enrich_flag(r, sheet, name, vals))

        for i in range(len(numeric_cols)):
            for j in range(i + 1, len(numeric_cols)):
                ci_a, col_a, name_a = numeric_cols[i]
                ci_b, col_b, name_b = numeric_cols[j]
                r = DETECTOR_FUNCS["check_constant_offset"](col_a, col_b, name_a, name_b)
                if r: all_flags.append(_enrich_flag(r, sheet, name_a, col_a, is_pair=True, col_name_b=name_b, evidence_vals_b=col_b))
                r = DETECTOR_FUNCS["check_constant_ratio"](col_a, col_b, name_a, name_b)
                if r: all_flags.append(_enrich_flag(r, sheet, name_a, col_a, is_pair=True, col_name_b=name_b, evidence_vals_b=col_b))
                r = DETECTOR_FUNCS["check_identical_columns"](col_a, col_b, name_a, name_b)
                if r: all_flags.append(_enrich_flag(r, sheet, name_a, col_a, is_pair=True, col_name_b=name_b, evidence_vals_b=col_b))

    if len(sheets) >= 2:
        cross = DETECTOR_FUNCS["check_cross_sheet_identical"](sheets, "pdf")
        for f in cross:
            sa = next((s for s in sheets if s["name"] == f["sheet_a"]), None)
            sb = next((s for s in sheets if s["name"] == f["sheet_b"]), None)
            if sa and sb:
                f["location"] = f"跨表 — Page {sa['page']} 表格 {sa['table_num_on_page']} vs Page {sb['page']} 表格 {sb['table_num_on_page']}"
                f["page"] = f"{sa['page']}/{sb['page']}"
            else:
                f["location"] = f"跨表 — {f['sheet_a']} vs {f['sheet_b']}"
                f["page"] = "?"
            # evidence_text 已在 check_cross_sheet_identical 中设置
        all_flags.extend(cross)

    return all_flags


# ═══════════════════════════════════════════════════════════
# 第四步：生成 HTML 报告
# ═══════════════════════════════════════════════════════════

def generate_report(meta, tables, flags, pdf_path, numeric_table_count=None):
    """生成完整 HTML 报告数据"""
    table_count = len(tables) if numeric_table_count is None else numeric_table_count
    high_flags = [f for f in flags if f.get("severity") == "high"]
    medium_flags = [f for f in flags if f.get("severity") == "medium"]
    by_type = Counter(f["type"] for f in flags)

    if flags:
        scores = [f.get("risk_score", 50) for f in flags]
        avg_risk = sum(scores) / len(scores)
        max_risk = max(scores)
    else:
        avg_risk, max_risk = 0, 0

    if table_count == 0:
        risk_level, risk_color = "⚪ 证据不足", "#7f8c8d"
    elif len(high_flags) >= 3 or max_risk >= 80:
        risk_level, risk_color = "🔴 高风险", "#e74c3c"
    elif len(high_flags) >= 1 or len(medium_flags) >= 3:
        risk_level, risk_color = "🟡 中风险", "#f39c12"
    elif flags:
        risk_level, risk_color = "🟢 低风险", "#27ae60"
    else:
        risk_level, risk_color = "✅ 未发现异常", "#2ecc71"

    tables_info = [{"page": t.get("page", "?"), "source": t.get("source", "?"),
                     "shape": f"{t.get('shape', (0,0))[0]}行 × {t.get('shape', (0,0))[1]}列"}
                   for t in tables]

    return {
        "meta": meta, "pdf_path": pdf_path,
        "data_status": "insufficient_data" if table_count == 0 else "ok",
        "risk_level": risk_level, "risk_color": risk_color,
        "avg_risk": round(avg_risk, 1), "max_risk": max_risk,
        "flags": flags, "high_count": len(high_flags),
        "medium_count": len(medium_flags), "total_flags": len(flags),
        "tables": tables_info, "table_count": table_count,
        "by_type": [{"type": t, "count": c} for t, c in by_type.most_common()],
    }


HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>论文造假嫌疑检测报告</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;background:#f5f6fa;color:#2d3436;line-height:1.6;padding:20px}
.container{max-width:960px;margin:0 auto}
.header{background:white;border-radius:12px;padding:32px;margin-bottom:20px;box-shadow:0 2px 12px rgba(0,0,0,.08)}
.header h1{font-size:24px;margin-bottom:8px}
.header .subtitle{color:#636e72;font-size:14px}
.risk-badge{display:inline-block;padding:8px 20px;border-radius:20px;font-size:18px;font-weight:700;margin:12px 0;color:white}
.meta-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px;margin-top:16px}
.meta-item{background:#f8f9fa;padding:12px 16px;border-radius:8px}
.meta-item .label{font-size:11px;color:#636e72;text-transform:uppercase;letter-spacing:.5px}
.meta-item .value{font-size:14px;font-weight:600;margin-top:4px;word-break:break-all}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:16px;margin-bottom:20px}
.card{background:white;border-radius:12px;padding:20px;box-shadow:0 2px 12px rgba(0,0,0,.08);text-align:center}
.card .number{font-size:36px;font-weight:800}
.card .label{font-size:12px;color:#636e72;margin-top:4px}
.card.high .number{color:#e74c3c}
.card.medium .number{color:#f39c12}
.card.info .number{color:#3498db}
.section{background:white;border-radius:12px;padding:24px;margin-bottom:20px;box-shadow:0 2px 12px rgba(0,0,0,.08)}
.section h2{font-size:18px;margin-bottom:16px;padding-bottom:8px;border-bottom:2px solid #f0f0f0}
.flag-list{list-style:none}
.flag-item{padding:12px 16px;margin-bottom:8px;border-radius:8px;border-left:4px solid #ddd;background:#fafafa}
.flag-item.severity-high{border-left-color:#e74c3c;background:#fdf0ed}
.flag-item.severity-medium{border-left-color:#f39c12;background:#fef9e7}
.flag-item .flag-type{font-weight:700;font-size:13px;color:#555;text-transform:uppercase;letter-spacing:.5px}
.flag-item .flag-location{font-size:12px;color:#e67e22;margin-top:4px;font-family:monospace}
.flag-item .flag-detail{font-size:13px;color:#2d3436;margin-top:4px}
.flag-item .flag-evidence{font-size:11px;color:#7f8c8d;margin-top:4px;font-family:monospace;word-break:break-all;max-height:40px;overflow:hidden;text-overflow:ellipsis}
.flag-item .flag-meta{font-size:11px;color:#999;margin-top:4px}
.chart-row{display:flex;flex-wrap:wrap;gap:16px}
.chart-card{flex:1;min-width:280px;background:#f8f9fa;border-radius:8px;padding:16px}
.chart-card h3{font-size:14px;margin-bottom:12px;color:#636e72}
.chart-bar{display:flex;align-items:center;margin-bottom:8px}
.chart-bar .bar-label{width:160px;font-size:12px;color:#555;text-align:right;padding-right:8px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.chart-bar .bar-track{flex:1;height:20px;background:#e9ecef;border-radius:4px;overflow:hidden}
.chart-bar .bar-fill{height:100%;border-radius:4px;transition:width .3s}
table{width:100%;border-collapse:collapse;font-size:13px}
th,td{padding:10px 12px;text-align:left;border-bottom:1px solid #eee}
th{background:#f8f9fa;font-weight:600;color:#555}
.explanation{font-size:12px;color:#999;margin-top:16px;padding:12px;background:#f0f7ff;border-radius:8px;border-left:3px solid #3498db}
</style>
</head>
<body>
<div class="container">
<div class="header">
  <p class="subtitle">论文数据造假检测报告</p>
  <h1>__TITLE__</h1>
  <div class="risk-badge" style="background:__RISK_COLOR__">__RISK_LEVEL__</div>
  <div class="meta-grid">
    <div class="meta-item"><div class="label">DOI</div><div class="value">__DOI__</div></div>
    <div class="meta-item"><div class="label">PMID</div><div class="value">__PMID__</div></div>
    <div class="meta-item"><div class="label">页数</div><div class="value">__PAGES__</div></div>
    <div class="meta-item"><div class="label">平均风险评分</div><div class="value">__AVG_RISK__/100</div></div>
  </div>
</div>

<div class="cards">
  <div class="card high"><div class="number">__HIGH__</div><div class="label">高风险红旗</div></div>
  <div class="card medium"><div class="number">__MEDIUM__</div><div class="label">中风险红旗</div></div>
  <div class="card info"><div class="number">__TABLES__</div><div class="label">提取表格</div></div>
  <div class="card info"><div class="number">__FLAGS__</div><div class="label">总红旗数</div></div>
</div>

<div class="section">
  <h2>🔍 红旗详情</h2>
  __FLAGS_LIST__
</div>

<div class="chart-row">
  <div class="chart-card">
    <h3>检测器分布</h3>
    __TYPE_CHART__
  </div>
  <div class="chart-card">
    <h3>评分分布</h3>
    __SCORE_CHART__
  </div>
</div>

<p class="explanation">
  ⚠️ 本报告基于统计检测器自动生成，仅供筛查参考。<strong>红旗 ≠ 确认造假</strong>——高评分可能由数据收集方式、四舍五入惯例、或小样本噪声导致。
  最终判断需人工核实原始数据和实验记录。检测器来源：Brown & Heathers (2017), GRIM; Hartgerink et al. (2016), statcheck; 耿同学/paperconan 实践。
</p>
</div>
</body>
</html>"""


def render_html(report):
    """将报告数据渲染为 HTML 字符串"""
    m = report["meta"]
    title = (m.get("title") or "未知标题").replace("<", "&lt;").replace(">", "&gt;")

    # 红旗列表
    if report["flags"]:
        items = []
        for f in report["flags"]:
            sev = f.get("severity", "medium")
            t = f.get("type", "").replace("_", " ").upper()
            d = f.get("detail", "").replace("<", "&lt;").replace(">", "&gt;")
            rs = f.get("risk_score", "?")
            loc = f.get("location", "").replace("<", "&lt;").replace(">", "&gt;")
            ev = f.get("evidence_text", "").replace("<", "&lt;").replace(">", "&gt;")
            loc_html = f'<div class="flag-location">📍 {loc}</div>' if loc else ""
            ev_html = f'<div class="flag-evidence">📊 {ev}</div>' if ev else ""
            items.append(f'<li class="flag-item severity-{sev}"><div class="flag-type">[{rs}分] {t}</div>{loc_html}<div class="flag-detail">{d}</div>{ev_html}</li>')
        flags_html = '<ul class="flag-list">' + "\n".join(items) + "</ul>"
    elif report.get("data_status") == "insufficient_data":
        flags_html = '<p style="color:#7f8c8d;font-size:15px;padding:16px">⚪ 未提取到可检测的数值表格，当前证据不足，不能判断是否存在统计异常。建议提供 Supplementary PDF、Excel 或 CSV 数据。</p>'
    else:
        flags_html = f'<p style="color:#27ae60;font-size:15px;padding:16px">✅ 未发现任何数据异常信号。该论文的数值数据通过了全部 {ACTIVE_DETECTOR_COUNT} 种检测器。</p>'

    # 检测器分布柱状图
    if report["by_type"]:
        mc = max(int(entry["count"]) for entry in report["by_type"])
        bars = []
        for entry in report["by_type"]:
            t = entry["type"].replace("_", " ")
            c = int(entry["count"])
            pct = int(c / mc * 100) if mc else 0
            bars.append(f'<div class="chart-bar"><span class="bar-label">{t}</span><div class="bar-track"><div class="bar-fill" style="width:{pct}%;background:#3498db"></div></div><span style="font-size:12px;margin-left:8px;color:#555">{c}</span></div>')
        type_chart = "\n".join(bars)
    else:
        type_chart = '<p style="color:#999">无数据</p>'

    # 评分分布（高/中/低）
    hc, mc, lc = report["high_count"], report["medium_count"], report["total_flags"] - report["high_count"] - report["medium_count"]
    total = max(report["total_flags"], 1)
    score_bars = [
        f'<div class="chart-bar"><span class="bar-label">高风险 (≥75)</span><div class="bar-track"><div class="bar-fill" style="width:{int(hc/total*100)}%;background:#e74c3c"></div></div><span style="font-size:12px;margin-left:8px">{hc}</span></div>',
        f'<div class="chart-bar"><span class="bar-label">中风险 (50-74)</span><div class="bar-track"><div class="bar-fill" style="width:{int(mc/total*100)}%;background:#f39c12"></div></div><span style="font-size:12px;margin-left:8px">{mc}</span></div>',
        f'<div class="chart-bar"><span class="bar-label">低风险 (&lt;50)</span><div class="bar-track"><div class="bar-fill" style="width:{int(lc/total*100)}%;background:#27ae60"></div></div><span style="font-size:12px;margin-left:8px">{lc}</span></div>',
    ]
    score_chart = "\n".join(score_bars)

    html = HTML_TEMPLATE
    html = html.replace("__TITLE__", title)
    html = html.replace("__RISK_COLOR__", report["risk_color"])
    html = html.replace("__RISK_LEVEL__", report["risk_level"])
    html = html.replace("__DOI__", m.get("doi") or "—")
    html = html.replace("__PMID__", m.get("pmid") or "—")
    html = html.replace("__PAGES__", str(m.get("pages", 0)))
    html = html.replace("__AVG_RISK__", str(report["avg_risk"]))
    html = html.replace("__HIGH__", str(report["high_count"]))
    html = html.replace("__MEDIUM__", str(report["medium_count"]))
    html = html.replace("__TABLES__", str(report["table_count"]))
    html = html.replace("__FLAGS__", str(report["total_flags"]))
    html = html.replace("__FLAGS_LIST__", flags_html)
    html = html.replace("__TYPE_CHART__", type_chart)
    html = html.replace("__SCORE_CHART__", score_chart)

    return html


# ═══════════════════════════════════════════════════════════
# 主入口
# ═══════════════════════════════════════════════════════════

def _check_deps():
    """检查依赖并返回报告"""
    missing = []
    if not HAS_NUMPY: missing.append("numpy")
    if not HAS_FITZ: missing.append("PyMuPDF (fitz)")
    if not HAS_SCIPY: missing.append("scipy")
    if not HAS_PDFPLUMBER: missing.append("pdfplumber")
    if not HAS_PANDAS: missing.append("pandas")
    return missing


def main():
    try:
        import argparse
        parser = argparse.ArgumentParser(description="论文数据造假检测器")
        parser.add_argument("pdf_path", help="论文 PDF 文件路径")
        parser.add_argument("-o", "--output", default=None, help="输出 HTML 路径（默认 outputs/check_<pmid>.html）")
        args = parser.parse_args()

        pdf_path = args.pdf_path
        if not os.path.exists(pdf_path):
            return {"ok": False, "error": f"文件不存在: {pdf_path}"}

        # 依赖检查
        missing = _check_deps()
        if missing:
            return {
                "ok": False, "error": f"缺少依赖: {', '.join(missing)}",
                "hint": build_install_hint(missing)
            }

        print(f"📄 加载 PDF: {pdf_path}")
        t0 = time.time()

        # Step 1: 元数据
        print("  [1/4] 提取元数据...")
        meta = extract_pdf_meta(pdf_path)
        print(f"  标题: {meta['title'][:80]}...")
        print(f"  DOI: {meta['doi'] or '未找到'}, PMID: {meta['pmid'] or '未找到'}")

        # Step 2: 表格
        print("  [2/4] 提取表格...")
        tables = extract_tables_camelot(pdf_path)
        tables.extend(extract_tables_pdfplumber(pdf_path))
        print(f"  原始提取: {len(tables)} 个表格")

        sheets = []
        page_table_counter = {}
        for t in tables:
            pg = t.get("page", "?")
            page_table_counter[pg] = page_table_counter.get(pg, 0) + 1
            s = table_to_sheet(t, page=pg, table_num_on_page=page_table_counter[pg])
            if s:
                sheets.append(s)
        print(f"  有效数值表: {len(sheets)} 个（过滤纯文本块后）")

        # Step 3: 检测
        print(f"  [3/4] 运行 {ACTIVE_DETECTOR_COUNT} 种检测器...")
        flags = run_detectors(sheets)
        high = sum(1 for f in flags if f.get("severity") == "high")
        med = sum(1 for f in flags if f.get("severity") == "medium")
        print(f"  红旗: {len(flags)} 条 (高风险 {high}, 中风险 {med})")

        # Step 4: 报告
        print("  [4/4] 生成报告...")
        report = generate_report(meta, tables, flags, pdf_path, numeric_table_count=len(sheets))

        # 确定输出路径
        if args.output:
            out_path = args.output
        else:
            os.makedirs("outputs", exist_ok=True)
            pid = meta.get("pmid", "")
            if pid:
                out_path = f"outputs/check_{pid}.html"
            else:
                ts = time.strftime("%Y%m%d-%H%M%S")
                out_path = f"outputs/check_{ts}.html"

        # 渲染并写入
        html = render_html(report)
        os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(html)

        elapsed = time.time() - t0
        print(f"\n✅ 完成! 耗时 {elapsed:.1f}s")
        print(f"📊 风险等级: {report['risk_level']}")
        print(f"📁 报告: {os.path.abspath(out_path)}")

        return {
            "ok": True,
            "data": {
                "risk_level": report["risk_level"],
                "high_flags": report["high_count"],
                "medium_flags": report["medium_count"],
                "total_flags": report["total_flags"],
                "avg_risk": report["avg_risk"],
                "max_risk": report["max_risk"],
                "table_count": report["table_count"],
                "report_path": os.path.abspath(out_path),
                "elapsed_s": round(elapsed, 1),
            }
        }

    except Exception as e:
        return {"ok": False, "error": str(e)}


if __name__ == "__main__":
    result = main()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    sys.exit(0 if result.get("ok") else 1)
