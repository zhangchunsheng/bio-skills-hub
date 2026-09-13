# -*- coding: utf-8 -*-
"""逐页体检：列出每一页的矢量/位图内容规模，找出「有视觉内容但 fig 提取为空/偏少」的页。"""
import json, sys, os
import pymupdf

src, meta_path = sys.argv[1], sys.argv[2]
meta = json.load(open(meta_path, encoding='utf-8'))
meta = {int(k): v for k, v in meta.items()}
doc = pymupdf.open(src)
print('PDF 总页数:', len(doc))
print()
print('%-5s %6s %6s %6s %6s  %s' % ('page', 'draw', 'img', 'clust', 'meta', '候选图区(y区间, 尺寸)'))
print('-' * 100)

suspicious = []
for pno in range(1, len(doc) + 1):
    page = doc[pno - 1]
    dr = page.get_drawings()
    try:
        ims = page.get_image_info()
    except Exception:
        ims = []
    items = []
    for d in dr:
        r = pymupdf.Rect(d['rect'])
        if r.width > 480 and r.height < 2.5:
            continue
        if r.width < 3 and r.height < 3:
            continue
        items.append(r)
    for i in ims:
        items.append(pymupdf.Rect(i['bbox']))

    cls = []
    for r in sorted(items, key=lambda r: (r.y0, r.x0)):
        hit = None
        for m in cls:
            if (r.x0 < m[0].x1 + 18 and r.x1 > m[0].x0 - 18 and
                    r.y0 < m[0].y1 + 18 and r.y1 > m[0].y0 - 18):
                hit = m
                break
        if hit is None:
            cls.append([pymupdf.Rect(r), 1])
        else:
            # 统一用 include_rect，避免 PyMuPDF Rect 的 |= 行为陷阱
            hit[0].include_rect(r)
            hit[1] += 1

    big = [(c, n) for c, n in cls if c.width >= 40 and c.height >= 25]
    nm = len(meta.get(pno, []))
    desc = '; '.join('y[%.0f-%.0f] %.0fx%.0f ink%d' % (c.y0, c.y1, c.width, c.height, n)
                     for c, n in big)
    print('%-5d %6d %6d %6d %6d  %s' % (pno, len(dr), len(ims), len(big), nm, desc[:70]))
    if len(big) > nm:
        suspicious.append((pno, len(big), nm))

print()
print('可疑页（视觉图区数 > meta 图数）:', len(suspicious))
for p, a, b in suspicious:
    print('   p%-3d 视觉图区=%d  meta图=%d' % (p, a, b))
