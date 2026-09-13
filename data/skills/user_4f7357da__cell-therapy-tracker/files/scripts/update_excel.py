#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
细胞治疗产品 Excel 更新脚本（健壮版）

用法:
  python update_excel.py                          # 自动定位工作区里最新的追踪 xlsx 并更新
  python update_excel.py <input.xlsx>             # 指定输入文件
  python update_excel.py <input.xlsx> --products-json products.json
  python update_excel.py <input.xlsx> --output out.xlsx
  python update_excel.py <input.xlsx> --check     # 只校验/预览，不写文件
  python update_excel.py <input.xlsx> --info      # 打印文件结构与各表最新日期

健壮性设计（对应 skillhub 测评问题1）:
- 输入校验：文件不存在 / 非 zip / 缺核心部件 → 人话报错并安全退出，绝不抛堆栈
- 自动定位：未给 input 时，在 --search-dir（默认当前目录）递归搜索最新且名称最匹配的 xlsx
- XML 容错：缺失 styles.xml / sharedStrings.xml / fills / cellXfs 节点时自动补建
- 复用样式：若文件中已存在黄色填充样式则复用，避免重复追加
- 友好报错：所有异常捕获后给出明确原因与排查建议，退出码非 0
- 安全写入：永远生成 <原名>_updated_YYYYMMDD.xlsx，绝不覆盖原文件；写后做 zip 完整性校验

说明:
- 自动检测并兼容默认命名空间与 ns0: 前缀命名空间
- 文本写入 sharedStrings.xml 并通过 t="s" 引用，确保中文与特殊字符正确显示
- 空值生成空单元格，数字生成普通数值单元格
"""

import sys
import os
import re
import json
import glob
import zipfile
import argparse
from datetime import datetime

MAIN_NS = 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'

# ── 默认产品数据（仅用于 --check / 演示）────────────────────────────────────────
DEFAULT_PRODUCTS = {
    "基因疗法": [],
    "干细胞上市产品": [],
    "干细胞治疗产品": [],
    "免疫细胞上市产品": [],
    "免疫细胞上市产品-已合并": [],
    "其他上市细胞治疗产品": [],
}

# 文件名关键词（用于自动定位时打分）
TRACKER_KEYWORDS = ['细胞', '治疗', '上市', 'cgt', 'cell', 'therapy', 'track', '产品']

# 修复日志：记录本次对文件做了哪些“自动修复”，供报告展示
REPAIR_LOG = []


def log_repair(msg):
    REPAIR_LOG.append(msg)


# ── 命名空间工具 ────────────────────────────────────────────────────────────────
def get_namespace_prefix(content):
    """检测 XML 内容使用的命名空间前缀（'' 或 'ns0:'）"""
    if '<ns0:' in content[:3000]:
        return 'ns0:'
    return ''


def xml_escape(s):
    if not isinstance(s, str):
        return s
    return (s.replace('&', '&amp;')
            .replace('<', '&lt;')
            .replace('>', '&gt;')
            .replace('"', '&quot;')
            .replace("'", '&apos;'))


def has_ns0_in_package(all_files):
    """检查整个包是否普遍使用 ns0: 前缀（用于补建节点时保持一致）"""
    for name in ['xl/workbook.xml', 'xl/worksheets/sheet1.xml',
                 'xl/styles.xml', 'xl/sharedStrings.xml']:
        if name in all_files and '<ns0:' in all_files[name].decode('utf-8', errors='replace')[:3000]:
            return True
    return False


# ── 输入校验与自动定位 ───────────────────────────────────────────────────────────
def validate_input(path):
    """校验输入文件；返回 (ok, error_msg)"""
    if not os.path.exists(path):
        return False, f"找不到文件：{path}\n  请确认路径是否正确，或用 --search-dir 指定搜索目录。"
    if not zipfile.is_zipfile(path):
        return False, (f"文件不是合法的 xlsx（zip）格式：{path}\n"
                       f"  可能是损坏的下载文件、被改了扩展名，或根本不是 Excel 文件。\n"
                       f"  建议：重新从来源导出 .xlsx，或手动确认文件完整性。")
    with zipfile.ZipFile(path, 'r') as z:
        names = set(z.namelist())
        missing = []
        for required in ['xl/workbook.xml', 'xl/_rels/workbook.xml.rels']:
            if required not in names:
                missing.append(required)
    if missing:
        return False, (f"xlsx 缺少核心部件：{', '.join(missing)}\n"
                       f"  该文件结构异常，无法正常解析。建议重新生成该 Excel 文件。")
    return True, ""


def auto_detect_input(search_dir):
    """在工作区递归搜索最合适的追踪 xlsx。返回 (path_or_None, reason)"""
    search_dir = search_dir or '.'
    candidates = []
    for p in glob.glob(os.path.join(search_dir, '**', '*.xlsx'), recursive=True):
        # 不把技能自身目录或临时目录纳入
        pl = p.lower().replace('\\', '/')
        if '/.workbuddy/' in pl and '/skills/' in pl:
            continue
        if '~$' in os.path.basename(p):   # 跳过 Excel 临时锁文件
            continue
        candidates.append(p)

    if not candidates:
        return None, f"在 {search_dir} 及其子目录下未找到任何 .xlsx 文件。"

    scored = []
    for p in candidates:
        try:
            mtime = os.path.getmtime(p)
        except OSError:
            mtime = 0
        base = os.path.basename(p).lower()
        score = 0
        for kw in TRACKER_KEYWORDS:
            if kw in base:
                score += 2
        # 已是 _updated_ 派生文件的优先级略降（我们想找“源/最新”文件）
        if '_updated_' in base:
            score -= 1
        scored.append((score, mtime, p))

    # 先按关键词得分，再按修改时间倒序
    scored.sort(key=lambda x: (x[0], x[1]), reverse=True)
    # 仅当存在命中关键词的文件时，才在它们之中挑选（避免误选无关的随机 xlsx）
    matched = [s for s in scored if s[0] > 0]
    if matched:
        best = matched[0][2]
        return best, (f"已自动选定：{best}\n"
                      f"  （关键词匹配得分 {matched[0][0]}，修改时间 {datetime.fromtimestamp(matched[0][1]).strftime('%Y-%m-%d %H:%M')}）")
    # 无任何关键词命中：退而求其次取最新文件，并明确警告
    best = scored[0][2]
    return best, (f"已自动选定：{best}\n"
                  f"  （⚠️ 该文件名未命中任何关键词 细胞/治疗/上市/CGT，请确认是否为目标追踪表；"
                  f"修改时间 {datetime.fromtimestamp(scored[0][1]).strftime('%Y-%m-%d %H:%M')}）")


# ── 缺失节点补建 ─────────────────────────────────────────────────────────────────
def ensure_styles_xml(all_files):
    """确保 styles.xml 存在且包含 fills / cellXfs 节点，缺失则补建。"""
    ns_prefix = 'ns0:' if has_ns0_in_package(all_files) else ''
    if 'xl/styles.xml' not in all_files:
        fonts = f'<{ns_prefix}fonts count="1"><{ns_prefix}font><{ns_prefix}sz val="11"/><{ns_prefix}name val="Calibri"/></{ns_prefix}font></{ns_prefix}fonts>'
        fills = f'<{ns_prefix}fills count="2"><{ns_prefix}fill><{ns_prefix}patternFill patternType="none"/></{ns_prefix}fill><{ns_prefix}fill><{ns_prefix}patternFill patternType="gray125"/></{ns_prefix}fill></{ns_prefix}fills>'
        borders = f'<{ns_prefix}borders count="1"><{ns_prefix}border/></{ns_prefix}borders>'
        csxfs = f'<{ns_prefix}cellStyleXfs count="1"><{ns_prefix}xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></{ns_prefix}cellStyleXfs>'
        cxfs = f'<{ns_prefix}cellXfs count="1"><{ns_prefix}xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/></{ns_prefix}cellXfs>'
        root = (f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
                f'<{ns_prefix}styleSheet xmlns="{MAIN_NS}">'
                f'{fonts}{fills}{borders}{csxfs}{cxfs}</{ns_prefix}styleSheet>')
        all_files['xl/styles.xml'] = root.encode('utf-8')
        log_repair("styles.xml 缺失 → 已补建最小化样式表（含默认 fills/cellXfs）")
    else:
        # 确保包含 fills 与 cellXfs 节点
        styles_xml = all_files['xl/styles.xml'].decode('utf-8', errors='replace')
        if get_namespace_prefix(styles_xml):
            ns_prefix = get_namespace_prefix(styles_xml)
        changed = False
        if f'<{ns_prefix}fills' not in styles_xml:
            styles_xml = styles_xml.replace(f'</{ns_prefix}styleSheet>',
                                            f'<{ns_prefix}fills count="2"><{ns_prefix}fill><{ns_prefix}patternFill patternType="none"/></{ns_prefix}fill><{ns_prefix}fill><{ns_prefix}patternFill patternType="gray125"/></{ns_prefix}fill></{ns_prefix}fills></{ns_prefix}styleSheet>')
            changed = True
        if f'<{ns_prefix}cellXfs' not in styles_xml:
            styles_xml = styles_xml.replace(f'</{ns_prefix}styleSheet>',
                                            f'<{ns_prefix}cellXfs count="1"><{ns_prefix}xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/></{ns_prefix}cellXfs></{ns_prefix}styleSheet>')
            changed = True
        if changed:
            all_files['xl/styles.xml'] = styles_xml.encode('utf-8')
            log_repair("styles.xml 缺 fills/cellXfs 节点 → 已补建")


def ensure_shared_strings(all_files):
    if 'xl/sharedStrings.xml' not in all_files:
        ns_prefix = 'ns0:' if has_ns0_in_package(all_files) else ''
        root = (f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
                f'<{ns_prefix}sst xmlns="{MAIN_NS}" count="0" uniqueCount="0"></{ns_prefix}sst>')
        all_files['xl/sharedStrings.xml'] = root.encode('utf-8')
        log_repair("sharedStrings.xml 缺失 → 已补建空共享字符串表")


# ── 样式处理 ────────────────────────────────────────────────────────────────────
YELLOW_RGB = 'FFFFFF00'


def find_existing_yellow_style(styles_xml):
    """若已存在黄色填充样式则返回其 cellXfs 索引，否则返回 None。"""
    ns_prefix = get_namespace_prefix(styles_xml)
    # 找 fgColor rgb="FFFFFF00"（大小写不敏感）
    fill_m = re.search(rf'<{ns_prefix}fgColor rgb="?{YELLOW_RGB}"?', styles_xml, re.IGNORECASE)
    if not fill_m:
        return None
    # 从该 fill 向前找其 fillId
    fill_block = styles_xml[:fill_m.start()]
    fills_section = re.search(rf'<{ns_prefix}fills\b', fill_block)
    if not fills_section:
        return None
    # 计算该 fill 在 fills 列表中的 index（按出现顺序）
    fill_tags = re.findall(rf'<{ns_prefix}fill\b', styles_xml)
    # 找到黄色 fill 是第几个
    idx = None
    for i, m in enumerate(re.finditer(rf'<{ns_prefix}fill\b', styles_xml)):
        if m.start() < fill_m.start():
            idx = i
    # 重新精确计数：黄色 fill 的 fillId
    fill_ids = list(re.finditer(rf'<{ns_prefix}fill\b', styles_xml))
    yellow_fill_id = None
    for fid, m in enumerate(fill_ids):
        seg = styles_xml[m.start(): fill_ids[fid + 1].start() if fid + 1 < len(fill_ids) else len(styles_xml)]
        if YELLOW_RGB.lower() in seg.lower():
            yellow_fill_id = fid
            break
    if yellow_fill_id is None:
        return None
    # 找引用该 fillId 的 cellXfs xf
    xf_m = re.search(rf'<{ns_prefix}xf\b[^>]*\bfillId="{yellow_fill_id}"', styles_xml)
    if not xf_m:
        return None
    # 计算该 xf 在 cellXfs 中的索引
    cxfs_m = re.search(rf'<{ns_prefix}cellXfs\b', styles_xml)
    if not cxfs_m:
        return None
    xfs_in = styles_xml[cxfs_m.start():]
    xf_list = list(re.finditer(rf'<{ns_prefix}xf\b', xfs_in))
    for xi, xm in enumerate(xf_list):
        seg = xfs_in[xm.start(): xf_list[xi + 1].start() if xi + 1 < len(xf_list) else len(xfs_in)]
        if f'fillId="{yellow_fill_id}"' in seg:
            return xi
    return None


def add_yellow_style(styles_xml):
    """向 styles.xml 添加（或复用）黄色填充样式，返回 (new_styles_xml, style_index)"""
    ns_prefix = get_namespace_prefix(styles_xml)
    existing = find_existing_yellow_style(styles_xml)
    if existing is not None:
        return styles_xml, existing

    fill_xml = (f'<{ns_prefix}fill><{ns_prefix}patternFill patternType="solid">'
                f'<{ns_prefix}fgColor rgb="{YELLOW_RGB}"/><{ns_prefix}bgColor rgb="00000000"/>'
                f'</{ns_prefix}patternFill></{ns_prefix}fill>')

    fills_tag = f'<{ns_prefix}fills'
    close_fills = f'</{ns_prefix}fills>'
    m = re.search(rf'{re.escape(fills_tag)}\s+count="(\d+)"[^>]*>(.*?){re.escape(close_fills)}', styles_xml, re.DOTALL)
    if not m:
        raise RuntimeError("无法解析 styles.xml 的 fills 节点（已尝试补建仍失败）")
    fills_count = int(m.group(1))
    fills_content = m.group(2)
    new_fill_index = fills_count

    new_fills_content = fills_content + fill_xml
    new_fills_count = fills_count + 1
    new_styles = re.sub(
        rf'{re.escape(fills_tag)}\s+count="{fills_count}"[^>]*>(.*?){re.escape(close_fills)}',
        f'{fills_tag} count="{new_fills_count}">{new_fills_content}{close_fills}',
        styles_xml, count=1, flags=re.DOTALL
    )

    cellxfs_tag = f'<{ns_prefix}cellXfs'
    close_cellxfs = f'</{ns_prefix}cellXfs>'
    m2 = re.search(rf'{re.escape(cellxfs_tag)}\s+count="(\d+)"[^>]*>(.*?){re.escape(close_cellxfs)}', new_styles, re.DOTALL)
    if not m2:
        raise RuntimeError("无法解析 styles.xml 的 cellXfs 节点（已尝试补建仍失败）")
    cellxfs_count = int(m2.group(1))
    cellxfs_content = m2.group(2)
    new_style_index = cellxfs_count

    new_xf = (f'<{ns_prefix}xf numFmtId="0" fontId="0" fillId="{new_fill_index}" '
              f'borderId="0" xfId="0" applyFill="1"/>')
    new_cellxfs_content = cellxfs_content + new_xf
    new_cellxfs_count = cellxfs_count + 1
    new_styles = re.sub(
        rf'{re.escape(cellxfs_tag)}\s+count="{cellxfs_count}"[^>]*>(.*?){re.escape(close_cellxfs)}',
        f'{cellxfs_tag} count="{new_cellxfs_count}">{new_cellxfs_content}{close_cellxfs}',
        new_styles, count=1, flags=re.DOTALL
    )

    log_repair(f"已新增黄色填充样式 cellXfs 索引 {new_style_index}")
    return new_styles, new_style_index


# ── 共享字符串处理 ──────────────────────────────────────────────────────────────
def add_string_to_shared_strings(ss_xml, text):
    """添加字符串到 sharedStrings.xml，返回 (new_ss_xml, index)"""
    if not text:
        return ss_xml, None

    ns_prefix = get_namespace_prefix(ss_xml)
    sst_tag = f'<{ns_prefix}sst' if ns_prefix else '<sst'
    close_sst = f'</{ns_prefix}sst>' if ns_prefix else '</sst'
    m = re.search(rf'{re.escape(sst_tag)}([^>]*)>', ss_xml)
    if not m:
        raise RuntimeError("无法找到 sst 元素")
    attrs_str = m.group(1)

    count_m = re.search(r'\bcount="(\d+)"', attrs_str)
    unique_m = re.search(r'\buniqueCount="(\d+)"', attrs_str)
    count = int(count_m.group(1)) if count_m else 0
    unique_count = int(unique_m.group(1)) if unique_m else 0

    new_index = unique_count
    escaped = xml_escape(text)
    if ns_prefix:
        new_si = f'<ns0:si><ns0:t xml:space="preserve">{escaped}</ns0:t></ns0:si>'
    else:
        new_si = f'<si><t xml:space="preserve">{escaped}</t></si>'

    new_ss = ss_xml.replace(close_sst, new_si + close_sst, 1)

    def update_attrs(m):
        a = m.group(0)
        a = re.sub(r'\bcount="\d+"', f'count="{count + 1}"', a)
        a = re.sub(r'\buniqueCount="\d+"', f'uniqueCount="{unique_count + 1}"', a)
        return a

    new_ss = re.sub(rf'{re.escape(sst_tag)}([^>]*)>', update_attrs, new_ss, count=1)
    return new_ss, new_index


# ── 工作表处理 ──────────────────────────────────────────────────────────────────
def col_to_index(col_letter):
    result = 0
    for c in col_letter.upper():
        result = result * 26 + (ord(c) - ord('A') + 1)
    return result


def find_max_row(sheet_xml):
    rows = re.findall(r'<(?:ns0:)?row r="(\d+)"', sheet_xml)
    if not rows:
        return 1
    return max(int(r) for r in rows)


def update_dimension(sheet_xml, new_max_row):
    dim_pattern = r'<(?:ns0:)?dimension ref="([^"]+)"'
    m = re.search(dim_pattern, sheet_xml)
    if not m:
        return sheet_xml
    old_ref = m.group(1)
    col_match = re.match(r'([A-Z]+)', old_ref)
    if not col_match:
        return sheet_xml
    col_part = col_match.group(1)
    new_ref = f"{col_part}{new_max_row}"
    ns_prefix = 'ns0:' if '<ns0:dimension' in sheet_xml else ''
    if ns_prefix:
        return re.sub(rf'<ns0:dimension ref="{re.escape(old_ref)}"', f'<ns0:dimension ref="{new_ref}"', sheet_xml, count=1)
    return re.sub(rf'<dimension ref="{re.escape(old_ref)}"', f'<dimension ref="{new_ref}"', sheet_xml, count=1)


def add_row_to_sheet(sheet_xml, row_num, cells, style_index, string_indices):
    ns_prefix = get_namespace_prefix(sheet_xml)
    if ns_prefix:
        row_tag = f'<ns0:row r="{row_num}" spans="1:30" customFormat="1" ht="35.25" customHeight="1">'
        close_data = '</ns0:sheetData>'
        c_tag = '<ns0:c'
        t_tag = '<ns0:t'
        is_tag = '<ns0:is>'
        close_is = '</ns0:is>'
        close_row = '</ns0:row>'
    else:
        row_tag = f'<row r="{row_num}" spans="1:30" customFormat="1" ht="35.25" customHeight="1">'
        close_data = '</sheetData>'
        c_tag = '<c'
        t_tag = '<t'
        is_tag = '<is>'
        close_is = '</is>'
        close_row = '</row>'

    cell_elements = []
    sorted_cols = sorted(cells.keys(), key=col_to_index)
    for col_letter in sorted_cols:
        cell_ref = f"{col_letter.upper()}{row_num}"
        value = cells[col_letter]

        if value == '' or value is None:
            cell = f'{c_tag} r="{cell_ref}" s="{style_index}"/>'
        elif isinstance(value, (int, float)) and not isinstance(value, bool):
            cell = f'{c_tag} r="{cell_ref}" s="{style_index}"><v>{value}</v></{c_tag[1:]}>'
        elif col_letter.upper() in string_indices and string_indices[col_letter.upper()] is not None:
            ss_idx = string_indices[col_letter.upper()]
            if ns_prefix:
                cell = f'{c_tag} r="{cell_ref}" s="{style_index}" t="s"><ns0:v>{ss_idx}</ns0:v></{c_tag[1:]}>'
            else:
                cell = f'{c_tag} r="{cell_ref}" s="{style_index}" t="s"><v>{ss_idx}</v></{c_tag[1:]}>'
        else:
            escaped = xml_escape(str(value))
            if ns_prefix:
                cell = f'{c_tag} r="{cell_ref}" s="{style_index}" t="inlineStr">{is_tag}{t_tag} xml:space="preserve">{escaped}</{t_tag[1:]}>{close_is}</{c_tag[1:]}>'
            else:
                cell = f'{c_tag} r="{cell_ref}" s="{style_index}" t="inlineStr">{is_tag}{t_tag} xml:space="preserve">{escaped}</{t_tag[1:]}>{close_is}</{c_tag[1:]}>'
        cell_elements.append(cell)

    new_row = row_tag + ''.join(cell_elements) + close_row
    new_sheet = sheet_xml.replace(close_data, new_row + close_data, 1)
    new_sheet = update_dimension(new_sheet, row_num)
    return new_sheet


# ── 文件结构解析 ─────────────────────────────────────────────────────────────────
def get_sheet_paths(wb_xml, rels_xml):
    """返回 {sheet_name: 'xl/...path'}。兼容不同属性顺序与相对/绝对 Target。"""
    rels = re.findall(r'<Relationship\s+Id="([^"]+)"\s+Type="[^"]*worksheet[^"]*"\s+Target="([^"]+)"', rels_xml)
    if not rels:
        rels = re.findall(r'<Relationship\s+Id="([^"]+)"\s+Target="([^"]+)"\s+Type="[^"]*worksheet[^"]*"', rels_xml)
    rels_map = {rid: target for rid, target in rels}
    sheets = re.findall(r'<sheet\b[^>]*\bname="([^"]+)"[^>]*\sr:id="([^"]+)"', wb_xml)
    if not sheets:
        sheets = re.findall(r'<sheet\b[^>]*\sr:id="([^"]+)"[^>]*\bname="([^"]+)"', wb_xml)
        sheets = [(n, r) for r, n in sheets]
    result = {}
    for name, rid in sheets:
        target = rels_map.get(rid, '')
        if not target:
            continue
        if target.startswith('/'):
            target = target.lstrip('/')
        elif not target.startswith('xl/'):
            target = 'xl/' + target
        result[name] = target
    return result


def collect_repairs_for_missing_parts(all_files):
    ensure_styles_xml(all_files)
    ensure_shared_strings(all_files)


# ── 信息/校验（--info / --check）────────────────────────────────────────────────
def _read_shared_strings_files(all_files):
    """从内存包读取 sharedStrings，返回 [index -> text]。"""
    if 'xl/sharedStrings.xml' not in all_files:
        return []
    xml = all_files['xl/sharedStrings.xml'].decode('utf-8', errors='replace')
    ns = 'ns0:' if '<ns0:' in xml[:3000] else ''
    ssts = []
    for m in re.finditer(rf'<{ns}si>(.*?)</{ns}si>', xml, re.DOTALL):
        seg = m.group(1)
        texts = re.findall(rf'<{ns}t[^>]*>(.*?)</{ns}t>', seg, re.DOTALL)
        ssts.append(''.join(texts))
    return ssts


def _sheet_cell_texts_files(xml, ns, sst):
    """解析工作表中所有单元格文本（inlineStr + 共享字符串引用）。"""
    texts = []
    for m in re.finditer(rf'<{ns}c\b[^>]*\bt="inlineStr"[^>]*>(.*?)</{ns}c>', xml, re.DOTALL):
        seg = m.group(1)
        texts.extend(re.findall(rf'<{ns}t[^>]*>(.*?)</{ns}t>', seg, re.DOTALL))
    for m in re.finditer(rf'<{ns}c\b[^>]*\bt="s"[^>]*><{ns}v>(\d+)</{ns}v></{ns}c>', xml):
        idx = int(m.group(1))
        if 0 <= idx < len(sst):
            texts.append(sst[idx])
    return texts


def parse_latest_dates(all_files):
    """扫描所有工作表（含共享字符串），提取 YYYY.MM.DD / YYYY-MM-DD，返回最新与各表行数。"""
    date_pat = re.compile(r'(20\d{2}[.\-](?:0[1-9]|1[0-2])[.\-](?:0[1-9]|[12]\d|3[01]))')
    wb_xml = all_files['xl/workbook.xml'].decode('utf-8', errors='replace')
    rels_xml = all_files['xl/_rels/workbook.xml.rels'].decode('utf-8', errors='replace')
    sst = _read_shared_strings_files(all_files)
    sheet_paths = get_sheet_paths(wb_xml, rels_xml)
    info = {}
    latest = None
    for name, path in sheet_paths.items():
        if path not in all_files:
            continue
        xml = all_files[path].decode('utf-8', errors='replace')
        ns = 'ns0:' if '<ns0:' in xml[:3000] else ''
        max_row = find_max_row(xml)
        dates = date_pat.findall(' '.join(_sheet_cell_texts_files(xml, ns, sst)))
        sheet_latest = max(dates) if dates else '—'
        info[name] = {'rows': max_row, 'latest_date': sheet_latest}
        if dates:
            norm = max(dates)
            if latest is None or norm > latest:
                latest = norm
    return info, latest


# ── 主流程 ──────────────────────────────────────────────────────────────────────
def update_excel(input_path, output_path, products_by_sheet, dry_run=False):
    with zipfile.ZipFile(input_path, 'r') as zin:
        all_files = {}
        for name in zin.namelist():
            all_files[name] = zin.read(name)

    # 补建缺失节点（各部件自行检测命名空间前缀）
    collect_repairs_for_missing_parts(all_files)

    # 1. styles.xml + 黄色样式
    styles_xml = all_files['xl/styles.xml'].decode('utf-8', errors='replace')
    new_styles, yellow_style_idx = add_yellow_style(styles_xml)
    all_files['xl/styles.xml'] = new_styles.encode('utf-8')

    # 2. sharedStrings.xml
    ss_xml = all_files['xl/sharedStrings.xml'].decode('utf-8', errors='replace')
    all_strings = {}
    for sheet_name, products in products_by_sheet.items():
        for product in products:
            for col, val in product.items():
                if val and val != '' and not isinstance(val, (int, float)):
                    if val not in all_strings:
                        ss_xml, idx = add_string_to_shared_strings(ss_xml, val)
                        all_strings[val] = idx
    all_files['xl/sharedStrings.xml'] = ss_xml.encode('utf-8')

    # 3. 工作表
    wb_xml = all_files['xl/workbook.xml'].decode('utf-8', errors='replace')
    rels_xml = all_files['xl/_rels/workbook.xml.rels'].decode('utf-8', errors='replace')
    sheet_paths = get_sheet_paths(wb_xml, rels_xml)

    applied = {}
    for sheet_name, products in products_by_sheet.items():
        if not products:
            continue
        if sheet_name not in sheet_paths:
            print(f"  ⚠️ 未找到工作表「{sheet_name}」，已跳过（请检查 products.json 的表名）")
            continue
        sheet_path = sheet_paths[sheet_name]
        sheet_xml = all_files[sheet_path].decode('utf-8', errors='replace')
        max_row = find_max_row(sheet_xml)
        for product in products:
            new_row = max_row + 1
            cells_value, cells_index = {}, {}
            for col, val in product.items():
                col = col.upper()
                cells_value[col] = val
                if val and val != '' and not isinstance(val, (int, float)) and val in all_strings:
                    cells_index[col] = all_strings[val]
                else:
                    cells_index[col] = None
            sheet_xml = add_row_to_sheet(sheet_xml, new_row, cells_value, yellow_style_idx, cells_index)
            max_row = new_row
        all_files[sheet_path] = sheet_xml.encode('utf-8')
        applied[sheet_name] = len(products)

    # 4. 写入（dry_run 不写）
    if dry_run:
        print("\n[--check] 预览完成，未写入任何文件。")
        return applied

    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zout:
        for name, data in all_files.items():
            zout.writestr(name, data)

    # 5. 写后完整性校验
    bad = zipfile.ZipFile(output_path).testzip()
    if bad is not None:
        raise RuntimeError(f"输出文件损坏，部件 {bad} 校验失败。原文件未受影响。")
    return applied


def validate_products(products_by_sheet):
    """校验 products 结构，返回 (ok, error_msg, normalized)"""
    if not isinstance(products_by_sheet, dict):
        return False, "products.json 顶层必须是 {工作表名: [产品行...]} 的对象。", None
    norm = {}
    for sheet, products in products_by_sheet.items():
        if not isinstance(products, list):
            return False, f"工作表「{sheet}」的值必须是产品行列表（数组）。", None
        rows = []
        for i, p in enumerate(products):
            if not isinstance(p, dict):
                return False, f"工作表「{sheet}」第 {i + 1} 行不是对象（列字母→值）。", None
            rows.append({str(k).upper(): v for k, v in p.items()})
        norm[sheet] = rows
    return True, "", norm


def main():
    parser = argparse.ArgumentParser(
        description='更新细胞治疗产品 Excel 文件（健壮版：自动修复+容错+自动定位）',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="未指定 input 时，会自动在工作区搜索最新的追踪 xlsx。始终生成 _updated_YYYYMMDD.xlsx，不覆盖原文件。"
    )
    parser.add_argument('input', nargs='?', default=None, help='输入 xlsx 文件路径（缺省则自动定位）')
    parser.add_argument('--output', default=None, help='输出路径（默认 <input>_updated_YYYYMMDD.xlsx）')
    parser.add_argument('--products-json', default=None, help='新产品数据 JSON 文件')
    parser.add_argument('--search-dir', default='.', help='自动定位时的搜索根目录（默认当前目录）')
    parser.add_argument('--check', action='store_true', help='只校验/预览，不写文件')
    parser.add_argument('--info', action='store_true', help='打印文件结构与各表最新日期后退出')
    args = parser.parse_args()

    # 1) 定位输入
    if args.info or (not args.products_json and args.input is None):
        # 仍需一个文件用于 info；若没给则尝试自动定位
        pass
    input_path = args.input
    if not input_path:
        detected, reason = auto_detect_input(args.search_dir)
        print(reason)
        if not detected:
            print("\n无法自动定位追踪文件。请显式传入路径，例如：")
            print("  python update_excel.py 细胞产品上市情况汇总.xlsx --products-json products.json")
            sys.exit(2)
        input_path = detected

    ok, err = validate_input(input_path)
    if not ok:
        print(f"\n❌ 输入文件校验失败：\n{err}")
        sys.exit(1)

    # 2) 读入并解析为内存包
    with zipfile.ZipFile(input_path, 'r') as zin:
        all_files = {n: zin.read(n) for n in zin.namelist()}

    # --info
    if args.info:
        info, latest = parse_latest_dates(all_files)
        print(f"\n文件：{input_path}")
        print(f"全表最新上市日期（用于搜索起点）：{latest}")
        print("各工作表：")
        for name, d in info.items():
            print(f"  - {name}: 最大行={d['rows']}, 最新日期={d['latest_date']}")
        sys.exit(0)

    # 3) 读 products
    if args.products_json:
        try:
            with open(args.products_json, 'r', encoding='utf-8') as f:
                products_raw = json.load(f)
        except FileNotFoundError:
            print(f"\n❌ 找不到 products JSON：{args.products_json}")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"\n❌ products JSON 解析失败：{e}\n  请检查 JSON 格式（引号、逗号、括号）。")
            sys.exit(1)
        ok, err, products_by_sheet = validate_products(products_raw)
        if not ok:
            print(f"\n❌ products 数据结构错误：{err}")
            sys.exit(1)
    else:
        products_by_sheet = {k: [] for k in DEFAULT_PRODUCTS}
        print("⚠️ 未提供 --products-json，无可写入的新产品（仅做结构校验/演示）。")

    total = sum(len(v) for v in products_by_sheet.values())
    if total == 0 and not args.check:
        print("\nℹ️ 没有需要追加的新产品。若本周确无新产品，可不生成文件，仅汇报『无更新』。")
        sys.exit(0)

    if args.output is None:
        base, ext = os.path.splitext(input_path)
        args.output = f"{base}_updated_{datetime.now().strftime('%Y%m%d')}{ext}"

    print(f"输入 : {input_path}")
    print(f"输出 : {args.output}")
    print(f"待更新工作表与行数: " + ", ".join(f"{k}×{len(v)}" for k, v in products_by_sheet.items() if v))

    try:
        applied = update_excel(input_path, args.output, products_by_sheet, dry_run=args.check)
    except Exception as e:
        print(f"\n❌ 更新失败：{e}")
        print("   原文件未被修改。请根据上述信息排查；如仍无法解决，可把报错贴回给我。")
        sys.exit(1)

    print("\n✅ 完成！")
    for k, v in applied.items():
        print(f"   - {k}: 追加 {v} 行（黄色高亮）")
    if REPAIR_LOG:
        print("\n本次自动修复：")
        for r in REPAIR_LOG:
            print(f"   • {r}")
    if args.check:
        print(f"\n[--check] 未生成文件。确认无误后去掉 --check 重新运行。")
    else:
        print(f"\n输出文件：{args.output}（原文件已保留，未覆盖）")


if __name__ == '__main__':
    main()
