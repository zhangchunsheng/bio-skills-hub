# -*- coding: utf-8 -*-
"""文件加载层：多格式、多编码、脏表头、多文件合并。

兼容场景（全部来自病案首页实际导出习惯）：
- 老系统导出 gb18030/gbk 编码的 CSV；新系统 utf-8-sig（带 BOM）
- 表格前几行是报表标题 / 导出时间 / 单位名称，"真正表头"在第 N 行
- 同一批数据按年度/院区分成多个文件，需要纵向合并
- 病案号被 Excel 读成浮点数（"12345.0"），必须还原成 "12345"
"""

from __future__ import annotations

import glob
import os

import pandas as pd

from fields import ALIAS2CANON, norm_key

SUPPORTED_EXT = (".csv", ".tsv", ".txt", ".xlsx", ".xlsm", ".xls", ".json")
ENCODINGS = ("utf-8-sig", "gb18030", "utf-8", "gbk", "latin1")


class LoaderError(Exception):
    """加载失败，携带给用户/LLM 的修复建议。"""

    def __init__(self, code_name: str, message: str, suggestion: str = ""):
        super().__init__(message)
        self.code_name = code_name
        self.message = message
        self.suggestion = suggestion


def resolve_inputs(path: str) -> list[str]:
    """把「文件 / 目录 / 通配符」统一解析成文件列表。"""
    if os.path.isdir(path):
        files = []
        for ext in SUPPORTED_EXT:
            files.extend(glob.glob(os.path.join(path, f"*{ext}")))
            files.extend(glob.glob(os.path.join(path, f"*{ext.upper()}")))
        files = sorted(set(f for f in files if not os.path.basename(f).startswith("~$")))
        if not files:
            raise LoaderError("no_supported_file",
                              f"目录中未找到受支持的表格文件：{path}",
                              f"支持的扩展名：{', '.join(SUPPORTED_EXT)}")
        return files
    hits = sorted(glob.glob(path))
    if not hits:
        hits = [path] if os.path.exists(path) else []
    if not hits:
        raise LoaderError("file_not_found", f"输入路径不存在：{path}",
                          "请确认路径拼写，或把文件拖入对话框后使用其绝对路径。")
    return hits


def _read_csv_raw(path: str, encoding: str | None, sep: str | None, nrows: int | None):
    """尝试多种编码/分隔符读取 CSV 原始内容（不带表头）。"""
    last_err = None
    encodings = [encoding] if encoding else list(ENCODINGS)
    seps = [sep] if sep else [None, ",", "\t", ";", "|"]
    for enc in encodings:
        for s in seps:
            try:
                return pd.read_csv(path, dtype=str, header=None, nrows=nrows,
                                   encoding=enc, sep=s, engine="python",
                                   skip_blank_lines=False, on_bad_lines="skip")
            except Exception as exc:  # noqa: BLE001 - 逐组合降级尝试
                last_err = exc
    raise LoaderError("csv_read_failed", f"CSV 读取失败：{path}（{last_err}）",
                      "请用 --encoding 指定编码（如 gb18030），或 --sep 指定分隔符。")


def _read_excel_raw(path: str, sheet, nrows: int | None):
    ext = os.path.splitext(path)[1].lower()
    engine = "xlrd" if ext == ".xls" else "openpyxl"
    try:
        return pd.read_excel(path, sheet_name=sheet if sheet is not None else 0,
                             header=None, dtype=str, nrows=nrows, engine=engine)
    except Exception as exc:  # noqa: BLE001
        raise LoaderError("excel_read_failed", f"Excel 读取失败：{path}（{exc}）",
                          "若为 .xls 请确认已安装 xlrd；若含多个工作表请用 --sheet 指定。")


def _read_raw(path: str, sheet, encoding, sep, nrows):
    ext = os.path.splitext(path)[1].lower()
    if ext == ".json":
        df = pd.read_json(path, dtype=str)
        if nrows:
            df = df.head(nrows)
        return df, "json"
    if ext in (".xlsx", ".xlsm", ".xls"):
        return _read_excel_raw(path, sheet, nrows), "excel"
    return _read_csv_raw(path, encoding, sep, nrows), "csv"


def detect_header_row(raw: pd.DataFrame, max_scan: int = 15) -> tuple[int, float]:
    """探测"真正表头"所在行号。

    打分思路：命中已知病案首页字段别名的单元格加分（权重高），
    非空单元格数加分；纯数值行、含大量重复值的行会被压低。
    """
    best_row, best_score = 0, float("-inf")
    scan = min(max_scan, len(raw))
    for i in range(scan):
        row = raw.iloc[i]
        cells = [c for c in row.tolist() if str(c).strip() not in ("", "nan", "None", "NaT")]
        if not cells:
            continue
        alias_hits = sum(1 for c in cells if norm_key(c) in ALIAS2CANON)
        # 表头行几乎不含纯数字
        numeric_like = sum(1 for c in cells if _is_numberish(c))
        date_like = sum(1 for c in cells if _is_datelike(c))
        score = alias_hits * 5.0 + len(cells) * 0.3 - numeric_like * 2.0 - date_like * 2.0
        if score > best_score:
            best_row, best_score = i, score
    # 置信度：命中越多越可信
    head = raw.iloc[best_row]
    hits = sum(1 for c in head.tolist()
               if str(c).strip() not in ("", "nan") and norm_key(c) in ALIAS2CANON)
    conf = min(1.0, hits / 5.0)
    return best_row, conf


def _is_numberish(v) -> bool:
    s = str(v).strip().replace(",", "")
    if not s or s.lower() in ("nan", "none"):
        return False
    try:
        float(s)
        return True
    except ValueError:
        return False


def _is_datelike(v) -> bool:
    s = str(v)
    if len(s) < 6:
        return False
    digits = sum(ch.isdigit() for ch in s)
    return digits >= 6 and ("-" in s or "/" in s or "年" in s)


def read_raw(path: str, sheet=None, encoding=None, sep=None, header_row=None) -> dict:
    """读单个文件的原始二维表，并返回表头定位信息。"""
    probe, kind = _read_raw(path, sheet, encoding, sep, nrows=30)
    if probe.empty:
        raise LoaderError("empty_file", f"文件无有效内容：{path}", "请确认文件不是空表或纯说明页。")
    detected, conf = detect_header_row(probe)
    hdr = detected if header_row is None else int(header_row)
    full, _ = _read_raw(path, sheet, encoding, sep, nrows=None)
    if hdr >= len(full):
        raise LoaderError("header_row_out_of_range",
                          f"--header-row {hdr} 超出数据范围（共 {len(full)} 行）：{path}",
                          "先用不带参数的方式跑一次，观察原始前 15 行布局再指定行号。")
    columns = []
    for j, v in enumerate(full.iloc[hdr].tolist()):
        name = str(v).strip()
        if name in ("", "nan", "None"):
            name = f"未命名列_{j + 1}"
        columns.append(name)
    body = full.iloc[hdr + 1:].reset_index(drop=True)
    body.columns = _dedupe(columns)
    body = body.dropna(how="all")
    body = body[body.apply(
        lambda r: any(str(x).strip() not in ("", "nan", "None") for x in r.tolist()), axis=1)]
    return {
        "df": body.reset_index(drop=True),
        "path": path,
        "file_name": os.path.basename(path),
        "kind": kind,
        "header_row": hdr,
        "header_confidence": round(conf, 2),
        "raw_rows": int(len(full)),
        "rows": int(len(body)),
        "columns": list(body.columns),
    }


def _dedupe(names: list[str]) -> list[str]:
    """列名去重：重复的加 _2/_3 后缀。"""
    seen: dict[str, int] = {}
    out = []
    for n in names:
        if n in seen:
            seen[n] += 1
            out.append(f"{n}_{seen[n]}")
        else:
            seen[n] = 0
            out.append(n)
    return out


def load(path: str, sheet=None, encoding=None, sep=None, header_row=None) -> dict:
    """加载并纵向合并一个文件或一整个目录。

    返回 dict：df（原始合并表）、files（每文件元信息）、warnings。
    """
    files = resolve_inputs(path)
    parts, metas, warnings = [], [], []
    for idx, f in enumerate(files):
        info = read_raw(f, sheet=sheet, encoding=encoding, sep=sep,
                        header_row=header_row if len(files) == 1 else None)
        part = info["df"]
        part["__source_file__"] = info["file_name"]
        if info["header_confidence"] < 0.4:
            warnings.append(
                f"{info['file_name']}：表头自动定位置信度较低"
                f"（第 {info['header_row'] + 1} 行），请核对字段映射表。")
        parts.append(part)
        metas.append(info)
        if idx == 0 and len(files) > 1:
            pass
    if len(parts) == 1:
        merged = parts[0]
    else:
        merged = pd.concat(parts, ignore_index=True, sort=False)
        warnings.append(
            f"已合并 {len(files)} 个文件（纵向拼接，新增 __source_file__ 列）；"
            "请核对各文件列名是否一致，不一致的列会产生空值。")
    return {"df": merged, "files": metas, "warnings": warnings}


def to_numeric(s: pd.Series) -> pd.Series:
    """字符串列转数值：去千分位、去单位、全角转半角、去括号负数写法。"""
    txt = (s.astype(str)
           .str.replace(",", "", regex=False)
           .str.replace("，", "", regex=False)
           .str.replace("元", "", regex=False)
           .str.replace(" ", "", regex=False)
           .str.replace("　", "", regex=False)
           .str.strip())
    txt = txt.replace({"": None, "nan": None, "None": None, "-": None,
                       "—": None, "无": None, "NULL": None})
    # 会计负数写法 (123.45)
    neg = txt.str.match(r"^\(.*\)$", na=False)
    txt = txt.where(~neg, txt.str.strip("()"))
    out = pd.to_numeric(txt, errors="coerce")
    return out.where(~neg, -out)


def to_datetime(s: pd.Series, dayfirst: bool = False) -> pd.Series:
    """字符串列转日期。

    关键点：pandas 默认只推断**一种**日期格式，而病案首页导出里
    "2023/03/02"、"20230326"、"2023-05-12 00:00:00" 常常混在同一列，
    必须显式用 format="mixed" 逐元素解析，否则会大面积变 NaT。
    """
    txt = (s.astype(str).str.strip()
           .str.replace("年", "-", regex=False)
           .str.replace("月", "-", regex=False)
           .str.replace("日", "", regex=False)
           .str.replace("/", "-", regex=False)
           .str.replace(".", "-", regex=False)
           .str.replace("T", " ", regex=False))
    txt = txt.replace({"": None, "nan": None, "None": None, "NaT": None, "无": None, "-": None})
    # 8 位紧凑格式 -> YYYY-MM-DD
    compact = txt.str.fullmatch(r"\d{8}", na=False)
    if compact.any():
        txt = txt.where(~compact,
                        txt.str.slice(0, 4) + "-" + txt.str.slice(4, 6) + "-" + txt.str.slice(6, 8))
    try:
        out = pd.to_datetime(txt, errors="coerce", format="mixed", dayfirst=dayfirst)
    except (ValueError, TypeError):
        out = pd.to_datetime(txt, errors="coerce", dayfirst=dayfirst)
    # Excel 序列号兜底（数字型日期）
    num = pd.to_numeric(txt, errors="coerce")
    serial = num.notna() & num.between(20000, 60000)
    if serial.any():
        conv = pd.to_datetime(num[serial], unit="D", origin="1899-12-30", errors="coerce")
        out = out.where(~serial, conv.reindex(out.index))
    return out


def clean_id_string(s: pd.Series) -> pd.Series:
    """病案号洗白：去掉 Excel 浮点尾巴、前导/尾随空格、公式残留。"""
    txt = s.astype(str).str.strip()
    txt = txt.str.replace(r"^=\"?(.*?)\"?$", r"\1", regex=True)
    txt = txt.replace({"": None, "nan": None, "None": None})
    float_like = txt.str.fullmatch(r"\d+\.0+", na=False)
    txt = txt.where(~float_like, txt.str.replace(r"\.0+$", "", regex=True))
    return txt
