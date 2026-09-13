#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
搜索查询生成器（对应 skillhub 测评问题1「搜索工作流依赖人工」）

作用：把"照清单手动搜"变成"脚本生成清单、Agent 照单搜"。
输入最新追踪 xlsx（或自动定位），解析最新上市日期作为搜索起点，
输出本轮应执行的「三梯队关键词」+「watchlist 在审产品精确查询」清单。

用法:
  python gen_search_queries.py                         # 自动定位文件，输出到屏幕
  python gen_search_queries.py <input.xlsx>            # 指定文件
  python gen_search_queries.py --year 2026 --as-of 2026-07-18
  python gen_search_queries.py --output queries.txt    # 同时写文件
  python gen_search_queries.py --json                  # 以 JSON 输出（便于程序消费）

输出内容：
  - 搜索起点日期（文件中最新上市日期，或 --as-of）
  - 第一梯队：FDA / EMA 英文监管源关键词
  - 第二梯队：NMPA / PMDA / 中文行业源关键词
  - 第三梯队：行业新闻/媒体扫描关键词
  - watchlist 在审产品精确查询（来自 references/watchlist.md）

Agent 使用方式：拿到清单后，用 WebSearch 逐条（或分批）搜索，按 SKILL.md 的
交叉验证规则（≥2 个独立来源）筛选候选产品，再分类写入 products.json。
"""

import sys
import os
import re
import json
import zipfile
import argparse
from datetime import datetime, date

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
WATCHLIST_PATH = os.path.join(SCRIPT_DIR, '..', 'references', 'watchlist.md')

# 三梯队关键词模板（{Y} 会被替换为年份）
TIER1 = [
    "FDA approved CAR-T {Y}",
    "FDA approved TCR-T cell therapy {Y}",
    "FDA approved Treg cell therapy {Y}",
    "FDA approved stem cell therapy {Y}",
    "FDA approved gene therapy {Y}",
    "FDA novel drug approval cell gene tissue product {Y}",
    "EMA approved CAR-T cell therapy {Y}",
    "EMA approved gene therapy {Y}",
]
TIER2 = [
    "NMPA 获批 CAR-T {Y}",
    "NMPA 获批 干细胞 {Y}",
    "NMPA 获批 基因治疗 {Y}",
    "NMPA 附条件批准 细胞治疗 {Y}",
    "PMDA 批准 干细胞 {Y}",
    "PMDA 批准 细胞治疗 {Y}",
    "日本 干细胞 产品 获批 上市 {Y}",
    "细胞治疗 获批上市 {Y} 新产品",
    "基因治疗 获批上市 {Y} 新产品",
]
TIER3 = [
    "细胞与基因治疗 周报 {Y} FDA NMPA",
    "CGT 获批 {Y} 最新",
    "干细胞产品 获批 上市 {Y}",
    "CAR-T 新药 获批 {Y}",
    "基因疗法 新药 获批 {Y}",
    "罕见病 细胞治疗 基因治疗 获批 {Y}",
    # 补充：主要市场监管机构新闻页与周报
    "FDA CBER approvals {Y} cell gene therapy",
    "EMA human medicines highlights {Y} advanced therapy",
    "NMPA 药品批准证明文件 {Y} 治疗类生物制品",
]


def auto_detect_input(search_dir):
    import glob
    candidates = []
    for p in glob.glob(os.path.join(search_dir or '.', '**', '*.xlsx'), recursive=True):
        pl = p.lower().replace('\\', '/')
        if '/.workbuddy/' in pl and '/skills/' in pl:
            continue
        if '~$' in os.path.basename(p):
            continue
        candidates.append(p)
    if not candidates:
        return None
    scored = []
    kws = ['细胞', '治疗', '上市', 'cgt', 'cell', 'therapy', 'track', '产品']
    for p in candidates:
        try:
            mt = os.path.getmtime(p)
        except OSError:
            mt = 0
        score = sum(2 for kw in kws if kw in os.path.basename(p).lower())
        if '_updated_' in os.path.basename(p).lower():
            score -= 1
        scored.append((score, mt, p))
    scored.sort(key=lambda x: (x[0], x[1]), reverse=True)
    # 仅命中关键词的文件中挑选，避免误选无关的随机 xlsx
    matched = [s for s in scored if s[0] > 0]
    if matched:
        return matched[0][2]
    return scored[0][2]


def _read_shared_strings(z):
    """读取 sharedStrings.xml，返回 [index -> text] 列表（合并富文本多段 <t>）。"""
    if 'xl/sharedStrings.xml' not in z.namelist():
        return []
    xml = z.read('xl/sharedStrings.xml').decode('utf-8', errors='replace')
    ns = 'ns0:' if '<ns0:' in xml[:3000] else ''
    ssts = []
    for m in re.finditer(rf'<{ns}si>(.*?)</{ns}si>', xml, re.DOTALL):
        seg = m.group(1)
        texts = re.findall(rf'<{ns}t[^>]*>(.*?)</{ns}t>', seg, re.DOTALL)
        ssts.append(''.join(texts))
    return ssts


def _sheet_cell_texts(xml, ns, sst):
    """解析工作表中所有单元格文本（inlineStr + 共享字符串引用）。"""
    texts = []
    # inlineStr 单元格
    for m in re.finditer(rf'<{ns}c\b[^>]*\bt="inlineStr"[^>]*>(.*?)</{ns}c>', xml, re.DOTALL):
        seg = m.group(1)
        texts.extend(re.findall(rf'<{ns}t[^>]*>(.*?)</{ns}t>', seg, re.DOTALL))
    # 共享字符串引用单元格 <c ... t="s"><v>IDX</v></c>
    for m in re.finditer(rf'<{ns}c\b[^>]*\bt="s"[^>]*><{ns}v>(\d+)</{ns}v></{ns}c>', xml):
        idx = int(m.group(1))
        if 0 <= idx < len(sst):
            texts.append(sst[idx])
    return texts


def parse_latest_date(input_path):
    """扫描所有工作表（含共享字符串），返回最新 YYYY.MM.DD / YYYY-MM-DD，或 None。"""
    pat = re.compile(r'(20\d{2}[.\-](?:0[1-9]|1[0-2])[.\-](?:0[1-9]|[12]\d|3[01]))')
    with zipfile.ZipFile(input_path, 'r') as z:
        names = set(z.namelist())
        if 'xl/workbook.xml' not in names or 'xl/_rels/workbook.xml.rels' not in names:
            return None
        wb = z.read('xl/workbook.xml').decode('utf-8', errors='replace')
        rels = z.read('xl/_rels/workbook.xml.rels').decode('utf-8', errors='replace')
        sst = _read_shared_strings(z)
        rels_map = dict(re.findall(r'<Relationship\s+Id="([^"]+)"\s+Type="[^"]*worksheet[^"]*"\s+Target="([^"]+)"', rels))
        sheets = re.findall(r'<sheet\b[^>]*\bname="([^"]+)"[^>]*\sr:id="([^"]+)"', wb)
        if not sheets:
            sheets = [(n, r) for r, n in re.findall(r'<sheet\b[^>]*\sr:id="([^"]+)"[^>]*\bname="([^"]+)"', wb)]
        latest = None
        for name, rid in sheets:
            target = rels_map.get(rid, '')
            if not target:
                continue
            if target.startswith('/'):
                target = target.lstrip('/')
            elif not target.startswith('xl/'):
                target = 'xl/' + target
            if target not in names:
                continue
            xml = z.read(target).decode('utf-8', errors='replace')
            ns = 'ns0:' if '<ns0:' in xml[:3000] else ''
            texts = _sheet_cell_texts(xml, ns, sst)
            dates = pat.findall(' '.join(texts))
            if dates:
                cur = max(dates)
                if latest is None or cur > latest:
                    latest = cur
        return latest


def read_watchlist_products():
    """从 watchlist.md 提取『在审/临近申报』表中的产品名，返回查询模板列表。"""
    if not os.path.exists(WATCHLIST_PATH):
        return []
    text = open(WATCHLIST_PATH, 'r', encoding='utf-8').read()
    # 定位“在审/临近申报”小节
    m = re.search(r'##\s*在审/临近申报.*?(?=\n##\s|\Z)', text, re.DOTALL)
    if not m:
        return []
    section = m.group(0)
    rows = re.findall(r'^\|\s*([^|]+?)\s*\|', section, re.MULTILINE)
    products = []
    for r in rows[1:]:  # 跳过表头
        name = r.strip()
        if name.startswith('-') or name == '产品名(代号)':
            continue
        # 取产品名主名（括号内为代号/商品名）
        main = re.split(r'[（(]', name)[0].strip()
        if main:
            products.append(main)
    return products


def build_queries(year, as_of, latest_date):
    out = {
        "search_start_date": latest_date or as_of,
        "year": year,
        "tier1_fda_ema": [q.format(Y=year) for q in TIER1],
        "tier2_nmpa_pmda": [q.format(Y=year) for q in TIER2],
        "tier3_media": [q.format(Y=year) for q in TIER3],
        "watchlist_products": [],
    }
    for p in read_watchlist_products():
        out["watchlist_products"].append({
            "product": p,
            "queries": [
                f'"{p}" approved FDA {year}',
                f'"{p}" 获批 NMPA {year}',
                f'"{p}" PMDA 批准 {year}',
            ]
        })
    return out


def render_text(q):
    lines = []
    lines.append(f"# 细胞/基因治疗产品搜索清单")
    lines.append(f"搜索起点日期 : {q['search_start_date']}（仅搜此日期之后的新获批产品）")
    lines.append(f"年份         : {q['year']}")
    lines.append("")
    lines.append("## 第一梯队 — FDA / EMA 英文监管源（最高优先级）")
    for s in q['tier1_fda_ema']:
        lines.append(f"  [ ] {s}")
    lines.append("")
    lines.append("## 第二梯队 — NMPA / PMDA / 中文行业源")
    for s in q['tier2_nmpa_pmda']:
        lines.append(f"  [ ] {s}")
    lines.append("")
    lines.append("## 第三梯队 — 行业新闻/媒体扫描")
    for s in q['tier3_media']:
        lines.append(f"  [ ] {s}")
    lines.append("")
    lines.append("## 管线监控表（watchlist）在审产品精确查询")
    if q['watchlist_products']:
        for item in q['watchlist_products']:
            lines.append(f"  ▶ {item['product']}")
            for s in item['queries']:
                lines.append(f"      [ ] {s}")
    else:
        lines.append("  （watchlist 无在审产品）")
    lines.append("")
    lines.append("— 用 WebSearch 逐条/分批搜索，按 SKILL.md 交叉验证规则（≥2 独立来源）筛选后写入 products.json —")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description='生成细胞/基因治疗产品搜索查询清单')
    parser.add_argument('input', nargs='?', default=None, help='最新追踪 xlsx（缺省自动定位）')
    parser.add_argument('--year', default=None, help='搜索年份（默认取起点日期年份或当前年）')
    parser.add_argument('--as-of', default=None, help='手动指定搜索起点日期 YYYY-MM-DD（覆盖文件解析结果）')
    parser.add_argument('--search-dir', default='.', help='自动定位搜索根目录')
    parser.add_argument('--output', default=None, help='同时把清单写入该文件')
    parser.add_argument('--json', action='store_true', help='以 JSON 输出')
    args = parser.parse_args()

    input_path = args.input
    if not input_path:
        input_path = auto_detect_input(args.search_dir)
    latest_date = None
    if input_path and os.path.exists(input_path) and zipfile.is_zipfile(input_path):
        latest_date = parse_latest_date(input_path)
        print(f"已读取 {input_path}，文件内最新上市日期：{latest_date}", file=sys.stderr)

    if args.as_of:
        latest_date = args.as_of
    year = args.year or (latest_date[:4] if latest_date else str(date.today().year))

    queries = build_queries(year, args.as_of or latest_date or str(date.today()), latest_date)
    queries['input_file'] = input_path

    if args.json:
        text = json.dumps(queries, ensure_ascii=False, indent=2)
    else:
        text = render_text(queries)

    print(text)
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(text + "\n")
        print(f"\n清单已写入：{args.output}", file=sys.stderr)


if __name__ == '__main__':
    main()
