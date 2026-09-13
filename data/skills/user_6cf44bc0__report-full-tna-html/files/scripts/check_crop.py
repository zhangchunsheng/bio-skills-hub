# -*- coding: utf-8 -*-
"""Verify no rendered figure crop clips a text line.

For each figure bbox in figs_meta.json, look at text blocks within 22pt above
and below the crop. A block whose rect vertically straddles the crop edge means
that line was cut in half — i.e. a chart title or "Source:" line got sliced.

This is the automated replacement for eyeballing every image (which is slow and
impossible when the model in use cannot view images).

Usage:
    python check_crop.py <src.pdf> <figs_meta.json>
"""
import json, sys, re
import fitz

pdf_path, meta_path = sys.argv[1], sys.argv[2]
NEAR = 22.0

doc = fitz.open(pdf_path)
meta = json.load(open(meta_path, encoding='utf-8'))

bad = []
for pstr, figs in sorted(meta.items(), key=lambda x: int(x[0])):
    p = int(pstr)
    page = doc[p - 1]
    tb = []
    for b in page.get_text('dict')['blocks']:
        if b['type'] != 0:
            continue
        txt = ' '.join(s['text'] for l in b['lines'] for s in l['spans']).strip()
        if txt:
            tb.append((fitz.Rect(b['bbox']), txt))
    for f in figs:
        fx0, fy0, fx1, fy1 = f['bbox']
        above = [t for t in tb if 0 <= (fy0 - t[0].y1) < NEAR]
        below = [t for t in tb if 0 <= (t[0].y0 - fy1) < NEAR]
        print(f"p{p:>4} {f['file']:<24} y=[{fy0:6.1f},{fy1:6.1f}] "
              f"above={len(above)} below={len(below)}")
        for rect, txt in above:
            if rect.y1 > fy0 + 0.5 and rect.y0 < fy0 - 0.5:
                bad.append((p, f['file'], 'ABOVE', txt[:60]))
        for rect, txt in below:
            if rect.y0 < fy1 - 0.5 and rect.y1 > fy1 + 0.5:
                bad.append((p, f['file'], 'BELOW', txt[:60]))

print('\nstraddling (clipped) text lines:', len(bad))
for b in bad:
    print('  ', b)
sys.exit(1 if bad else 0)
