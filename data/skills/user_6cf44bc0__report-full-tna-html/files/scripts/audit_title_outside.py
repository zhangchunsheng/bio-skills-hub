# -*- coding: utf-8 -*-
"""审计：图框「上方 20–75pt」是否存在看起来像展陈标题、却没被裁进图里的文本块。

check_crop.py 只查「骑边被切一半」，抓不到「标题整块被留在框外」这一类。
本脚本补这个洞：对每个图框，向上找 20–75pt 内、且不在任何图框内的文本块，
若它满足标题特征（短、首字母大写、不以句点结尾、非页眉页脚），就报出来。

用法： python audit_title_outside.py <src.pdf> <figs_meta.json>
"""
import re
import sys
import json

import pymupdf  # noqa

PDF, META = sys.argv[1], sys.argv[2]
meta = json.load(open(META, encoding='utf-8'))
figs = {}
if isinstance(meta, dict):
    for p, v in meta.items():
        figs[int(p)] = v if isinstance(v, list) else [v]
else:
    for f in meta:
        figs.setdefault(int(f['page']), []).append(f)

SKIP = re.compile(r'^(October\s|TD Cowen Global Research|Therapeutic Categories Outlook|'
                  r'TDSecurities|Source:|Note:|www\.|http)', re.I)
doc = pymupdf.open(PDF)
hits = []
for pg in sorted(figs):
    page = doc[pg - 1]
    blocks = []
    for bl in page.get_text('dict')['blocks']:
        if bl['type'] != 0:
            continue
        t = ' '.join(s['text'] for ln in bl['lines'] for s in ln['spans']).strip()
        if t:
            blocks.append((bl['bbox'], ' '.join(t.split())))
    boxes = [f['bbox'] for f in figs[pg]]

    def inside(r):
        return any(r[1] >= b[1] and r[3] <= b[3] for b in boxes)

    for b in boxes:
        for r, t in blocks:
            if inside(r):
                continue
            gap = b[1] - r[3]          # 块底 -> 图顶
            if not (20 <= gap <= 75):
                continue
            if SKIP.match(t) or len(t) < 8 or len(t) > 110:
                continue
            if t.endswith('.') and len(t.split()) > 12:
                continue
            hits.append((pg, gap, t))
            break
doc.close()

print('图框上方 20–75pt 处疑似未被裁入的标题：%d 处' % len(hits))
for pg, gap, t in hits:
    print('  p%-4d 上方%5.1fpt  %s' % (pg, gap, t[:100]))
