# -*- coding: utf-8 -*-
"""
难表格坐标重建：把 PDF 里「用线条画的网格表」还原成 Markdown 表格。

适用：pdfplumber / pymupdf 的 extract_table 处理失败的表格——
      跨页大表（如 SoA 评估时间表）、多层嵌套表头、带合并格、表头分组的统计界值表。

原理：
  1) 横线：get_drawings() 中 宽>=40 且 高<=2.5 的矩形 -> 按中心 y 排序 -> 相邻两线构成「行带」
  2) 竖线：get_drawings() 中 宽<=2.5 且 高>=4 的矩形 -> 按中心 x 聚类 -> 构成「列边界」
  3) 单元格：page.get_text('words') 按中心点落入 (带, 列) 归组，带内按 y 容差分行、行内按 x 排序拼接
  4) 合并格：某条列边界在该行带内没有竖线覆盖 -> 判定左右两格合并，文本后加 〔合并格：X–Y〕
  5) 跨页：后续页中与第一页表头行文本相同的行自动跳过

用法：
  python grid_table.py <pdf> --pages 68-70 --hrows 2 --out out/soa.md
  python grid_table.py <pdf> --pages 107 --hrows 2 --top 60 --bot 700

常用参数：
  --pages     页区间，如 68-70 / 107 / 36-42
  --hrows     前几行用作表头（默认 2；后续页与之相同的行会被跳过）
  --top/--bot 表格上下边界 y（默认自动取该页最上/最下横线）
  --coltol    列边界 x 聚类容差（默认 8pt）
  --rowtol    带内分行 y 容差（默认 3pt）
  --title     输出文件首行的中文表题（如「**表 10. 评估时间表**」）
"""
import argparse
import os
import sys

import pymupdf


def cluster(vals, tol):
    """把一维数值聚成若干组，返回每组的均值。"""
    vals = sorted(vals)
    groups = []
    for v in vals:
        if groups and v - groups[-1][-1] <= tol:
            groups[-1].append(v)
        else:
            groups.append([v])
    return [sum(g) / len(g) for g in groups]


def page_lines(page, x0, x1, top, bot):
    """返回 (横线中心y列表, 竖线(x中心, y0, y1)列表, 所有线的x范围)。"""
    hs, vs = [], []
    xs = []
    for d in page.get_drawings():
        r = pymupdf.Rect(d['rect'])
        if r.x1 < x0 - 5 or r.x0 > x1 + 5:
            continue
        if r.y1 < top - 5 or r.y0 > bot + 5:
            continue
        xs.append((r.x0, r.x1))
        if r.width >= 40 and r.height <= 2.5:
            hs.append((r.y0 + r.y1) / 2)
        elif r.width <= 2.5 and r.height >= 4:
            vs.append(((r.x0 + r.x1) / 2, r.y0, r.y1))
    return hs, vs, xs


def cell_text(page, band, col_range, rowtol=3):
    """取落入 (band=(y0,y1), col_range=(x0,x1)) 的文本，带内按 y 分行、行内按 x 拼接。"""
    y0, y1 = band
    cx0, cx1 = col_range
    words = []
    for w in page.get_text('words'):
        wx0, wy0, wx1, wy1, txt = w[0], w[1], w[2], w[3], w[4]
        cy = (wy0 + wy1) / 2
        cx = (wx0 + wx1) / 2
        if y0 <= cy < y1 and cx0 <= cx < cx1:
            words.append((wy0, wx0, txt))
    if not words:
        return ''
    words.sort()
    lines, cur, cur_y = [], [], None
    for wy0, wx0, txt in words:
        if cur_y is None or abs(wy0 - cur_y) <= rowtol:
            cur.append((wx0, txt))
            cur_y = wy0 if cur_y is None else cur_y
        else:
            lines.append(cur)
            cur, cur_y = [(wx0, txt)], wy0
    if cur:
        lines.append(cur)
    return ' <br> '.join(' '.join(t for _, t in sorted(l)) for l in lines)


def parse_pages(spec, total):
    res = []
    for seg in spec.split(','):
        seg = seg.strip()
        if '-' in seg:
            a, b = seg.split('-', 1)
            res.extend(range(int(a), int(b) + 1))
        else:
            res.append(int(seg))
    return [p for p in res if 1 <= p <= total]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('pdf')
    ap.add_argument('--pages', required=True)
    ap.add_argument('--hrows', type=int, default=2)
    ap.add_argument('--top', type=float, default=None)
    ap.add_argument('--bot', type=float, default=None)
    ap.add_argument('--x0', type=float, default=0.0)
    ap.add_argument('--x1', type=float, default=10000.0)
    ap.add_argument('--coltol', type=float, default=8.0)
    ap.add_argument('--rowtol', type=float, default=3.0)
    ap.add_argument('--mincol', type=float, default=8.0,
                    help='列宽小于该值（pt）的伪列会被合并，默认 8；双线边框的表建议保持默认')
    ap.add_argument('--title', default='')
    ap.add_argument('--out', default='')
    args = ap.parse_args()

    doc = pymupdf.open(args.pdf)
    pages = parse_pages(args.pages, doc.page_count)
    if not pages:
        print('no pages'); sys.exit(1)

    # --- 1) 全表列边界：汇总所有页竖线 x ---
    all_vx = []
    per_page = {}
    for pno in pages:
        page = doc[pno - 1]
        top = args.top if args.top is not None else 0
        bot = args.bot if args.bot is not None else page.rect.height
        hs, vs, xs = page_lines(page, args.x0, args.x1, top, bot)
        hys = cluster(hs, 3)
        if args.top is not None:
            hys = [y for y in hys if y >= args.top - 3]
        if args.bot is not None:
            hys = [y for y in hys if y <= args.bot + 3]
        per_page[pno] = (hys, vs, xs)
        all_vx.extend(v[0] for v in vs)

    if not all_vx:
        print('未检测到竖线，本表可能不是网格表'); sys.exit(1)

    col_edges = cluster(all_vx, args.coltol)
    # 用横线端点补齐首尾边界
    xmins = [x[0] for _, _, xs in per_page.values() for x in xs] or [min(all_vx)]
    xmaxs = [x[1] for _, _, xs in per_page.values() for x in xs] or [max(all_vx)]
    left, right = min(xmins), max(xmaxs)
    bounds = [left] + [c for c in col_edges if left + 2 < c < right - 2] + [right]
    # 去掉「双线边框/内外框之间」产生的极窄伪列（实测会把 15 列撑成 17 列）
    pruned = [bounds[0]]
    for b in bounds[1:-1]:
        if b - pruned[-1] >= args.mincol:
            pruned.append(b)
    while len(pruned) > 1 and bounds[-1] - pruned[-1] < args.mincol:
        pruned.pop()
    pruned.append(bounds[-1])
    if len(pruned) != len(bounds):
        print(f'（已合并 {len(bounds) - len(pruned)} 个窄于 {args.mincol}pt 的伪列）')
    bounds = pruned
    ncol = len(bounds) - 1

    def col_name(i):
        return f'列{i + 1}'

    print(f'列数: {ncol}')
    print('列边界: ' + ', '.join(f'{b:.1f}' for b in bounds))

    # --- 2) 逐页逐带构建行 ---
    rows_out = []
    header_keys = set()

    for pno in pages:
        page = doc[pno - 1]
        hys, vs, _ = per_page[pno]
        for bi in range(len(hys) - 1):
            band = (hys[bi], hys[bi + 1])
            if band[1] - band[0] < 6:
                continue
            bc = (band[0] + band[1]) / 2
            # 该带内存在的竖线（聚类到列边界）
            present = set()
            for vx, vy0, vy1 in vs:
                if vy0 - 1 <= bc <= vy1 + 1:
                    cx = min(col_edges, key=lambda c: abs(c - vx))
                    if abs(cx - vx) <= args.coltol:
                        present.add(round(cx, 2))
            # 分段：相邻两段之间若无竖线 -> 合并
            segs = [[0]]
            for i in range(ncol - 1):
                edge = round(bounds[i + 1], 2)
                if any(abs(e - edge) <= 1.0 for e in present):
                    segs.append([i + 1])
                else:
                    segs[-1].append(i + 1)
            cells = []
            for seg in segs:
                cx0, cx1 = bounds[seg[0]], bounds[seg[-1] + 1]
                txt = cell_text(page, band, (cx0, cx1), args.rowtol).strip()
                if len(seg) > 1 and txt:
                    txt += f'〔合并格：{col_name(seg[0])}–{col_name(seg[-1])}〕'
                cells.append(txt)
            if not any(cells):
                continue
            key = '|'.join(cells)
            if pno == pages[0] and len(rows_out) < args.hrows:
                # 首页前 hrows 行 = 表头：记录其 key 供后续页去重，**并照常 append**
                header_keys.add(key)
            elif key in header_keys:
                continue  # 跨页重复出现的表头行
            rows_out.append(cells)

    if not rows_out:
        print('未构建出任何行'); sys.exit(1)

    # 补齐列数（合并格会减少单元格数 -> 用空串补齐到 ncol）
    fixed = []
    for cells in rows_out:
        if len(cells) < ncol:
            # 合并格行：把带 〔合并格：A–B〕 的单元格按跨度展开
            expanded = []
            for c in cells:
                expanded.append(c)
                if '〔合并格：' in c:
                    tag = c.split('〔合并格：')[1].rstrip('〕')
                    a, b = tag.split('–')
                    span = int(b.replace('列', '')) - int(a.replace('列', ''))
                    expanded.extend([''] * span)
            cells = expanded
        fixed.append(cells[:ncol] + [''] * max(0, ncol - len(cells)))

    md = []
    if args.title:
        md.append(args.title)
        md.append('')
    header = fixed[:args.hrows]
    body = fixed[args.hrows:] if len(fixed) > args.hrows else []
    for h in header:
        md.append('| ' + ' | '.join(h) + ' |')
    if header:
        md.append('|' + '---|' * ncol)
    for r in body:
        md.append('| ' + ' | '.join(r) + ' |')
    md.append('')
    out = '\n'.join(md)

    if args.out:
        os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
        with open(args.out, 'w', encoding='utf-8') as f:
            f.write(out)
        print(f'已写入 {args.out}（{len(body) + len(header)} 行 × {ncol} 列）')
    else:
        print(out)


if __name__ == '__main__':
    main()
