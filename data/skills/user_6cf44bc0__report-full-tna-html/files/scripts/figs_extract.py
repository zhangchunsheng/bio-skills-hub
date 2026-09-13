# -*- coding: utf-8 -*-
"""Final figure locator + renderer.

Strategy:
  1. Collect real graphic content (vector drawings + placed images) on the page.
  2. Cluster into figure blobs (gap-tolerant).
  3. Group blobs into rows (side-by-side panels share a row).
  4. Each blob's vertical span is expanded to the whitespace bounded by the
     surrounding text blocks; horizontally a row is expanded to the body width
     (or split at the midpoint when two panels sit side by side).
  5. Render at high DPI to PNG.
"""
import pymupdf, sys, json, os, re

BODY_TOP = 100.0
BODY_BOT = 744.0
X0, X1 = 12.0, 600.0


def text_blocks(page):
    """Return individual text blocks (rect, text, max_font_size)."""
    bs = []
    for b in page.get_text('dict')['blocks']:
        if b.get('type') != 0:
            continue
        r = pymupdf.Rect(b['bbox'])
        txt = ''.join(s['text'] for l in b['lines'] for s in l['spans']).strip()
        if not txt:
            continue
        if r.y1 < 40 or r.y0 > 770:
            continue
        fsize = max((s['size'] for l in b['lines'] for s in l['spans']), default=8)
        bs.append((r, txt, fsize))
    bs.sort(key=lambda x: x[0].y0)
    return bs


def gra_rects(page):
    rs = []
    for d in page.get_drawings():
        r = pymupdf.Rect(d['rect'])
        if r.width >= 5 and r.height >= 5:
            rs.append(r)
    try:
        for i in page.get_image_info():
            r = pymupdf.Rect(i['bbox'])
            if r.width >= 40 and r.height >= 25:
                rs.append(r)
    except Exception:
        pass
    return rs


def clusters(page, gap=24):
    out = []
    for r in sorted(gra_rects(page), key=lambda r: (r.y0, r.x0)):
        hit = None
        for m in out:
            if (r.x0 < m.x1 + gap and r.x1 > m.x0 - gap and
                    r.y0 < m.y1 + gap and r.y1 > m.y0 - gap):
                hit = m
                break
        if hit is not None:
            # 坑 #11：pymupdf.Rect 没有实现 __ior__，`hit |= r` 只是把新对象
            # 绑给局部变量 hit，列表 out 里的对象原封不动 —— 聚类合并会**静默失效**，
            # 由细碎笔画构成的图表（没有整块背景矩形）会被逐个判为「太小」而整体丢弃。
            # 必须用 include_rect() 原地合并。
            hit.include_rect(r)
        else:
            out.append(pymupdf.Rect(r))
    out = [c for c in out if c.width >= 45 and c.height >= 28]

    # Second pass: merge vertically stacked table fragments (background shading
    # split into header/footer strips) without merging genuinely separate charts.
    # Conditions: same column (x-overlap > 50%), vertical gap < 36 pt.
    merged = True
    while merged and len(out) > 1:
        merged = False
        out.sort(key=lambda r: (r.y0, r.x0))
        new = [out[0]]
        for c in out[1:]:
            last = new[-1]
            x_ov = max(0.0, min(c.x1, last.x1) - max(c.x0, last.x0))
            x_min = min(c.width, last.width)
            v_gap = c.y0 - last.y1
            if x_ov > 0.5 * x_min and v_gap > 0 and v_gap < 36:
                last.include_rect(c)   # 见坑 #11：不能用 |=
                merged = True
            else:
                new.append(c)
        out = new
    return out


CAPTION_RE = re.compile(r'Source:|Notes?:|Data from|AbbVie|ASCO|ASH|FDA|Journal of', re.I)


def is_caption_block(t, c, direction):
    """A caption/title block sits right next to the figure and is not a body paragraph."""
    r, txt, _ = t
    h = r.y1 - r.y0
    if h > 42:                # too tall to be a single title/source line
        return False
    # Horizontally overlap the cluster (with a small margin)
    if r.x1 < c.x0 - 60 or r.x0 > c.x1 + 60:
        return False
    if direction == 'above':
        return r.y1 <= c.y0 + 6 and c.y0 - r.y1 < 45
    else:  # below: only real source/note lines, not table rows that happen to sit close
        dist = r.y0 - c.y1
        is_cap = bool(CAPTION_RE.search(txt))
        if is_cap:
            return r.y0 >= c.y1 - 6 and dist < 70
        # Allow a short one-line note/legend directly attached to the figure.
        return r.y0 >= c.y1 - 4 and dist < 12 and h <= 16


def nearest_text_block_edge(tb, y0_cand, y1_cand, c):
    """Cap padding by the nearest body text block above/below.

    Caption blocks (title/source) identified by is_caption_block are allowed to
    be included in the crop; any other text block in the padding zone acts as a
    hard boundary (with a 2 pt safety margin).
    """
    top_cap, bot_cap = BODY_TOP - 8, BODY_BOT + 8
    for t in tb:
        r, txt, _ = t
        if is_caption_block(t, c, 'above') or is_caption_block(t, c, 'below'):
            continue
        h = r.y1 - r.y0
        if h < 10:
            continue
        # Block above the figure candidate region
        if r.y1 <= c.y0 + 4 and r.y1 > y0_cand:
            top_cap = max(top_cap, r.y1 + 2)
        # Block below the figure candidate region
        if r.y0 >= c.y1 - 4 and r.y0 < y1_cand:
            bot_cap = min(bot_cap, r.y0 - 2)
    return top_cap, bot_cap


def y_expand(page, c, tb):
    # Default: small padding around the raw graphic cluster
    y0, y1 = c.y0 - 10, c.y1 + 10

    above = below = None
    for t in tb:
        if is_caption_block(t, c, 'above'):
            above = t
        if below is None and is_caption_block(t, c, 'below'):
            below = t

    if above is not None:
        y0 = min(y0, above[0].y0)
    if below is not None:
        y1 = max(y1, below[0].y1)

    # Padding candidates: include the caption block plus 8 pt whitespace, but
    # do not cross into the next body paragraph.
    top_cap, bot_cap = nearest_text_block_edge(tb, y0 - 8, y1 + 8, c)
    y0 = max(y0 - 8, top_cap)
    y1 = min(y1 + 8, bot_cap)

    # Guard against runaway crops
    if y1 - y0 > 650:
        y0, y1 = c.y0 - 10, c.y1 + 10
        top_cap, bot_cap = nearest_text_block_edge(tb, y0 - 8, y1 + 8, c)
        y0 = max(y0 - 8, top_cap)
        y1 = min(y1 + 8, bot_cap)
    return max(BODY_TOP - 8, y0), min(BODY_BOT + 8, y1)


def figure_regions(page):
    tb = text_blocks(page)
    cls = clusters(page)
    if not cls:
        return []
    rows = []
    for c in sorted(cls, key=lambda r: (r.y0, r.x0)):
        placed = False
        for row in rows:
            ry0 = min(x.y0 for x in row)
            ry1 = max(x.y1 for x in row)
            ov = max(0.0, min(ry1, c.y1) - max(ry0, c.y0))
            if ov > 0.45 * min(c.height, ry1 - ry0):
                row.append(c)
                placed = True
                break
        if not placed:
            rows.append([c])
    out = []
    for row in rows:
        row.sort(key=lambda r: r.x0)
        y0 = min(y_expand(page, c, tb)[0] for c in row)
        y1 = max(y_expand(page, c, tb)[1] for c in row)
        if len(row) == 1:
            out.append(pymupdf.Rect(X0, y0, X1, y1))
        else:
            bounds = []
            for i, c in enumerate(row):
                left = X0 if i == 0 else (row[i - 1].x1 + c.x0) / 2
                right = X1 if i == len(row) - 1 else (c.x1 + row[i + 1].x0) / 2
                bounds.append((left, right))
            for left, right in bounds:
                out.append(pymupdf.Rect(max(X0, left - 4), y0, min(X1, right + 4), y1))
    out.sort(key=lambda r: (round(r.y0 / 12), r.x0))
    return out


if __name__ == '__main__':
    src = sys.argv[1]
    dpi = int(sys.argv[2]) if len(sys.argv) > 2 else 150
    doc = pymupdf.open(src)
    outdir = 'out/figs'
    os.makedirs(outdir, exist_ok=True)
    meta = {}
    total = 0
    for pno, page in enumerate(doc, start=1):
        rs = figure_regions(page)
        if not rs:
            continue
        meta[str(pno)] = []
        for i, r in enumerate(rs, start=1):
            pm = page.get_pixmap(dpi=dpi, clip=r, colorspace=pymupdf.csRGB)
            fn = os.path.join(outdir, 'p%03d_%d.jpg' % (pno, i))
            pm.save(fn, jpg_quality=88)
            total += os.path.getsize(fn)
            meta[str(pno)].append({'file': fn, 'bbox': [round(v, 1) for v in
                                   (r.x0, r.y0, r.x1, r.y1)],
                                   'w': pm.width, 'h': pm.height,
                                   'bytes': os.path.getsize(fn)})
    json.dump(meta, open('out/figs_meta.json', 'w'), indent=1)
    n = sum(len(v) for v in meta.values())
    print('pages:', len(meta), 'figures:', n, 'total MB:', round(total / 1048576, 2))
