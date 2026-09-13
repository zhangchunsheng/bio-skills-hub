#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
xlsx_lite —— 零第三方依赖的表格读写底座。

只用 Python 标准库解析 .xlsx / .csv / .txt，不装 openpyxl / pandas / chardet。
xlsx 本质是 zip 包里的 XML，标准库 zipfile + ElementTree 足够。

设计取舍：
  - 只读数据层（值、类型、合并单元格、样式编号），不追求还原完整格式
  - 写盘只出 CSV(UTF-8-BOM) 与 JSON，保证 Excel/WPS 双击不乱码
  - 若环境里恰好有 openpyxl，clean_sheet 会额外导出 .xlsx，没有也不影响主流程
"""

import csv
import io
import os
import re
import sys
import zipfile
import xml.etree.ElementTree as ET

NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
RNS = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
PNS = "{http://schemas.openxmlformats.org/package/2006/relationships}"

# numFmtId 落在这些区间表示"这个数字其实是日期/时间"
BUILTIN_DATE_FMT = set(range(14, 23)) | set(range(45, 48)) | {27, 30, 36, 50, 57}
DATE_FMT_HINT = re.compile(r"[yYmMdDhHsS]")


# ---------------------------------------------------------------- 基础工具

def col_to_idx(ref):
    """'AB12' -> 27（0 基列号）。单元格引用去掉行号只留列字母。"""
    m = re.match(r"([A-Za-z]+)", ref or "")
    if not m:
        return 0
    n = 0
    for ch in m.group(1).upper():
        n = n * 26 + (ord(ch) - 64)
    return n - 1


def idx_to_col(idx):
    """0 -> 'A', 26 -> 'AA'"""
    s = ""
    idx += 1
    while idx:
        idx, r = divmod(idx - 1, 26)
        s = chr(65 + r) + s
    return s


def sniff_encoding(raw):
    """
    猜字节流编码。返回 (encoding, confidence)。
    国内表格的乱码绝大多数是 GBK 系被当 UTF-8 读，所以 UTF-8 解码失败后
    优先试 gb18030（它兼容 gbk 与 gb2312），而不是直接 latin-1 兜底。
    """
    if raw.startswith(b"\xef\xbb\xbf"):
        return "utf-8-sig", 1.0
    if raw.startswith(b"\xff\xfe"):
        return "utf-16", 1.0
    if raw.startswith(b"\xfe\xff"):
        return "utf-16", 1.0
    try:
        raw.decode("utf-8")
        return "utf-8", 0.95
    except UnicodeDecodeError:
        pass
    for enc in ("gb18030", "big5", "shift_jis"):
        try:
            raw.decode(enc)
            # 中文字符占比越高越可信，避免把二进制误判成 gb18030
            txt = raw.decode(enc)
            han = sum(1 for c in txt[:4000] if "\u4e00" <= c <= "\u9fff")
            if han > 0:
                return enc, min(0.95, 0.5 + han / 500.0)
            return enc, 0.4
        except UnicodeDecodeError:
            continue
    return "latin-1", 0.2


def decode_bytes(raw):
    enc, conf = sniff_encoding(raw)
    return raw.decode(enc, errors="replace"), enc, conf


def sniff_delimiter(sample_line):
    """挑出现次数最多的候选分隔符；引号内的不算。"""
    counts = {}
    for d in (",", "\t", ";", "|", "^"):
        outside = re.sub(r'"[^"]*"', "", sample_line)
        counts[d] = outside.count(d)
    best = max(counts, key=lambda k: counts[k])
    return best if counts[best] > 0 else ","


# ---------------------------------------------------------------- xlsx 读取

class Sheet:
    def __init__(self, name, rows, merges, ncols, nrows):
        self.name = name
        self.rows = rows           # list[list[cell]]，cell 为 dict
        self.merges = merges       # list[str]，如 ['A1:C1']
        self.ncols = ncols
        self.nrows = nrows

    def values(self, limit=None):
        """只取显示值的二维列表，缺失单元格补 None。"""
        out = []
        for r in self.rows[:limit] if limit else self.rows:
            out.append([c["v"] if c else None for c in r])
        return out


def _text_of_si(si):
    """sharedStrings 的 <si> 可能把一段文字拆成多个 <t>（富文本），需要拼接。"""
    parts = []
    for t in si.iter(NS + "t"):
        parts.append(t.text or "")
    # 富文本会把中文和英文拆开，直接 join 即可
    return "".join(parts)


def read_shared_strings(z):
    try:
        data = z.read("xl/sharedStrings.xml")
    except KeyError:
        return []
    root = ET.fromstring(data)
    return [_text_of_si(si) for si in root.findall(NS + "si")]


def read_date_styles(z):
    """返回 set(style_index)，这些样式编号对应的单元格要当日期看待。"""
    try:
        data = z.read("xl/styles.xml")
    except KeyError:
        return set()
    root = ET.fromstring(data)
    custom = {}
    for nf in root.iter(NS + "numFmt"):
        try:
            fid = int(nf.get("numFmtId", "-1"))
        except ValueError:
            continue
        code = nf.get("formatCode", "")
        if code and DATE_FMT_HINT.search(re.sub(r"\[[^\]]*\]|\"[^\"]*\"", "", code)):
            custom[fid] = True
    date_styles = set()
    cellxfs = root.find(NS + "cellXfs")
    if cellxfs is None:
        return date_styles
    for i, xf in enumerate(cellxfs.findall(NS + "xf")):
        try:
            fid = int(xf.get("numFmtId", "0"))
        except ValueError:
            continue
        if fid in BUILTIN_DATE_FMT or custom.get(fid):
            date_styles.add(i)
    return date_styles


def _serial_to_date(serial):
    """Excel 序列号转日期字符串。1900 闰年 bug：Excel 把 1900 当闰年，60 对应虚构的 1900-02-29。"""
    import datetime
    if serial is None or serial <= 0:
        return None
    if serial < 60:
        base = datetime.datetime(1899, 12, 31)
    else:
        base = datetime.datetime(1899, 12, 30)
    try:
        dt = base + datetime.timedelta(days=float(serial))
    except (ValueError, OverflowError):
        return None
    if dt.hour or dt.minute or dt.second:
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    return dt.strftime("%Y-%m-%d")


def read_worksheet(z, path, shared, date_styles):
    root = ET.fromstring(z.read(path))

    merges = [mc.get("ref") for mc in root.iter(NS + "mergeCell") if mc.get("ref")]

    raw_rows = {}
    max_col = -1
    for row in root.iter(NS + "row"):
        try:
            ri = int(row.get("r")) - 1
        except (TypeError, ValueError):
            continue
        cells = []
        for c in row.findall(NS + "c"):
            ref = c.get("r") or ""
            ci = col_to_idx(ref) if ref else (len(cells))
            t = c.get("t", "n")
            v = None
            is_date = False
            if t == "s":
                iv = c.find(NS + "v")
                if iv is not None and iv.text is not None:
                    try:
                        v = shared[int(iv.text)]
                    except (ValueError, IndexError):
                        v = None
            elif t == "inlineStr":
                is_el = c.find(NS + "is")
                v = _text_of_si(is_el) if is_el is not None else None
            elif t == "b":
                iv = c.find(NS + "v")
                v = (iv.text == "1") if iv is not None else None
            elif t == "e":
                iv = c.find(NS + "v")
                v = ("#ERR:" + (iv.text or "")) if iv is not None else "#ERR"
            else:
                iv = c.find(NS + "v")
                if iv is not None and iv.text not in (None, ""):
                    txt = iv.text
                    try:
                        f = float(txt)
                        try:
                            si = int(c.get("s", -1))
                        except ValueError:
                            si = -1
                        if si in date_styles:
                            v = _serial_to_date(f)
                            is_date = True
                        else:
                            v = int(f) if f.is_integer() and abs(f) < 1e15 else f
                    except ValueError:
                        v = txt
            if v is None and not is_date:
                # 空单元格不占位，后面统一按 max_col 补齐
                pass
            cells.append({"ref": ref, "ci": ci, "v": v, "t": t, "date": is_date})
            if ci > max_col:
                max_col = ci
        raw_rows[ri] = cells

    nrows = (max(raw_rows) + 1) if raw_rows else 0
    ncols = max_col + 1
    grid = []
    for ri in range(nrows):
        line = [None] * ncols
        for c in raw_rows.get(ri, []):
            if 0 <= c["ci"] < ncols:
                line[c["ci"]] = c
        grid.append(line)
    return grid, merges, ncols, nrows


def read_xlsx(path):
    """返回 list[Sheet]。sheet 顺序按 workbook.xml。"""
    sheets = []
    with zipfile.ZipFile(path) as z:
        shared = read_shared_strings(z)
        date_styles = read_date_styles(z)

        targets = []
        names = []
        try:
            wb = ET.fromstring(z.read("xl/workbook.xml"))
            rels = ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
            rel_map = {}
            for rel in rels.iter(PNS + "Relationship"):
                tgt = rel.get("Target", "")
                rel_map[rel.get("Id")] = tgt.lstrip("/") if not tgt.startswith("/") else tgt.lstrip("/")
            for sh in wb.iter(NS + "sheet"):
                rid = sh.get(RNS + "id")
                tgt = rel_map.get(rid)
                if tgt:
                    if not tgt.startswith("xl/"):
                        tgt = "xl/" + tgt
                    targets.append(tgt)
                    names.append(sh.get("name", "Sheet"))
        except KeyError:
            pass

        if not targets:
            targets = sorted(
                n for n in z.namelist()
                if re.match(r"xl/worksheets/sheet\d+\.xml$", n)
            )
            names = ["Sheet%d" % (i + 1) for i in range(len(targets))]

        for tgt, nm in zip(targets, names):
            try:
                grid, merges, ncols, nrows = read_worksheet(z, tgt, shared, date_styles)
            except KeyError:
                continue
            sheets.append(Sheet(nm, grid, merges, ncols, nrows))
    return sheets


# ---------------------------------------------------------------- 文本表格读取

def read_delimited(path):
    """读 csv / txt / tsv，自动判编码与分隔符。返回 (list[list[str]], encoding)。"""
    with open(path, "rb") as f:
        raw = f.read()
    text, enc, _conf = decode_bytes(raw)
    first_line = text.splitlines()[0] if text.splitlines() else ""
    delim = sniff_delimiter(first_line)
    rows = list(csv.reader(io.StringIO(text), delimiter=delim))
    return rows, enc, delim


def load_table(path):
    """
    统一入口。返回 dict:
      kind      : 'xlsx' | 'delimited'
      sheets    : list[Sheet]（xlsx）
      rows      : list[list[str]]（delimited）
      encoding  : 文本文件的编码
      delimiter : 文本文件的分隔符
    """
    ext = os.path.splitext(path)[1].lower()
    if ext == ".xlsx":
        return {"kind": "xlsx", "sheets": read_xlsx(path), "encoding": "zip/xml", "delimiter": None}
    if ext == ".xls":
        raise ValueError(
            ".xls 是 Office 2003 以前的二进制格式，标准库读不了。"
            "请先用 Excel/WPS 另存为 .xlsx，或用 LibreOffice 转换："
            "soffice --headless --convert-to xlsx 文件.xls"
        )
    rows, enc, delim = read_delimited(path)
    return {"kind": "delimited", "rows": rows, "encoding": enc, "delimiter": delim}


# ---------------------------------------------------------------- 写出

def write_csv(path, rows, bom=True):
    """写 UTF-8-BOM 的 CSV。带 BOM 才能让 Excel/WPS 双击正确识别中文。"""
    enc = "utf-8-sig" if bom else "utf-8"
    with open(path, "w", newline="", encoding=enc) as f:
        w = csv.writer(f)
        for r in rows:
            w.writerow(["" if v is None else v for v in r])


def write_xlsx_lite(path, rows, sheet_name="Sheet1", merges=None):
    """
    零依赖写 xlsx。手写最小合规 OOXML 包，Excel / WPS / LibreOffice 均可打开。

    OOXML 对部件顺序有严格要求（sheetData 必须在 mergeCells 之前），
    这里按 schema 顺序输出，不要随意调整。
    """
    sheet_name = (sheet_name or "Sheet1")[:31]
    rows = rows or [[]]
    ncols = max((len(r) for r in rows), default=1)

    shared, sidx = [], {}

    def sid(text):
        if text not in sidx:
            sidx[text] = len(shared)
            shared.append(text)
        return sidx[text]

    def esc(s):
        return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                 .replace('"', "&quot;"))

    def cname(ci):
        return idx_to_col(ci)

    parts = []
    for ri, r in enumerate(rows):
        cells = []
        for ci in range(len(r)):
            v = r[ci]
            if v is None or v == "":
                continue
            ref = "%s%d" % (cname(ci), ri + 1)
            if isinstance(v, bool):
                cells.append('<c r="%s" t="b"><v>%d</v></c>' % (ref, 1 if v else 0))
            elif isinstance(v, (int, float)):
                cells.append('<c r="%s"><v>%s</v></c>' % (ref, repr(v) if isinstance(v, float) else v))
            else:
                cells.append('<c r="%s" t="s"><v>%d</v></c>' % (ref, sid(str(v))))
        if cells:
            parts.append('<row r="%d">%s</row>' % (ri + 1, "".join(cells)))
    sheet_data = "<sheetData>%s</sheetData>" % "".join(parts)

    merge_xml = ""
    if merges:
        mc = "".join('<mergeCell ref="%s"/>' % m for m in merges)
        merge_xml = '<mergeCells count="%d">%s</mergeCells>' % (len(merges), mc)

    sheet_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        '<dimension ref="A1:%s%d"/>' % (cname(max(0, ncols - 1)), len(rows)) +
        sheet_data + merge_xml + '</worksheet>'
    )

    ss_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<sst xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" count="%d" uniqueCount="%d">'
        % (len(shared), len(shared))
    ) + "".join("<si><t xml:space=\"preserve\">%s</t></si>" % esc(s) for s in shared) + "</sst>"

    wb_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
        '<sheets><sheet name="%s" sheetId="1" r:id="rId1"/></sheets></workbook>' % esc(sheet_name)
    )

    wb_rels = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>'
        '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>'
        '<Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/sharedStrings" Target="sharedStrings.xml"/>'
        '</Relationships>'
    )

    root_rels = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>'
        '</Relationships>'
    )

    content_types = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
        '<Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
        '<Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>'
        '<Override PartName="/xl/sharedStrings.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sharedStrings+xml"/>'
        '</Types>'
    )

    styles = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        '<fonts count="1"><font><sz val="11"/><name val="等线"/></font></fonts>'
        '<fills count="1"><fill><patternFill patternType="none"/></fill></fills>'
        '<borders count="1"><border/></borders>'
        '<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>'
        '<cellXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/></cellXfs>'
        '</styleSheet>'
    )

    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", content_types)
        z.writestr("_rels/.rels", root_rels)
        z.writestr("xl/workbook.xml", wb_xml)
        z.writestr("xl/_rels/workbook.xml.rels", wb_rels)
        z.writestr("xl/styles.xml", styles)
        z.writestr("xl/sharedStrings.xml", ss_xml)
        z.writestr("xl/worksheets/sheet1.xml", sheet_xml)
    return True


def try_write_xlsx(path, rows, sheet_name="clean"):
    """
    导出 xlsx。优先 openpyxl；没有就用内置零依赖写入器。
    主流程不依赖它，失败只影响可选产物。
    """
    try:
        from openpyxl import Workbook
        wb = Workbook()
        ws = wb.active
        ws.title = (sheet_name or "clean")[:31]
        for r in rows:
            ws.append(["" if v is None else v for v in r])
        wb.save(path)
        return True
    except ImportError:
        return write_xlsx_lite(path, rows, sheet_name)
    except Exception:
        try:
            return write_xlsx_lite(path, rows, sheet_name)
        except Exception as e:
            print("警告: xlsx 导出失败（%s），已保留 CSV" % e, file=sys.stderr)
            return False
