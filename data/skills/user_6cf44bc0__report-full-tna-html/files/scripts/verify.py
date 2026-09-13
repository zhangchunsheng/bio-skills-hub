# -*- coding: utf-8 -*-
"""Integrity check on the assembled single-file HTML.

Usage:
    python verify.py <out.html> <total_pdf_pages>
"""
import re, sys, collections

path = sys.argv[1]
total_pages = int(sys.argv[2])
html = open(path, encoding='utf-8').read()

pages = sorted(int(x) for x in re.findall(r'id="page-(\d+)"', html))
figs = len(re.findall(r'<img loading="lazy"', html))
stray = len(re.findall(r'<p><strong>图[：:]', html))
left = len(re.findall(r'@@FIG:', html))
imb_div = html.count('<div') - html.count('</div>')
imb_p = html.count('<p>') - html.count('</p>')

print('size MB      :', round(len(html.encode()) / 1048576, 2))
print('page anchors :', len(pages), '/', total_pages)
print('figures      :', figs)
print('stray caps   :', stray)
print('@@FIG left   :', left)
print('div / p imbal:', imb_div, '/', imb_p)

missing = [p for p in range(1, total_pages + 1) if p not in set(pages)]
dupes = [p for p, c in collections.Counter(pages).items() if c > 1]
print('missing pages:', missing if missing else 'none')
print('dup pages    :', dupes if dupes else 'none')
