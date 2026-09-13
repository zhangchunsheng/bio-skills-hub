# -*- coding: utf-8 -*-
"""Per-page translation-coverage check.

Compares English word count in the source text against Chinese character
count in the translated parts, page by page. Catches silently skipped or
truncated pages that page-anchor checks alone would miss.

Usage:
    python coverage.py <full_raw.txt> <out/zh dir> [lo] [hi]

Typical healthy ratio (zh chars per en word) for analyst reports: 1.1 - 1.8.
A page far below the median usually means a paragraph was dropped; far above
usually means the translator padded or a boilerplate page got misassigned.
"""
import re, sys, os

raw_path, zh_dir = sys.argv[1], sys.argv[2]
LO = float(sys.argv[3]) if len(sys.argv) > 3 else 1.0
HI = float(sys.argv[4]) if len(sys.argv) > 4 else 4.5

BOILER = re.compile(
    r'Therapeutic Categories Outlook|Oncology/[A-Za-z ]+|TD Cowen|'
    r'Global Research|October \d{4}|TDSecurities\.com')

raw = open(raw_path, encoding='utf-8').read()
parts = re.split(r'(?m)^===== PAGE (\d+) =====$', raw)
src = {}
for i in range(1, len(parts), 2):
    src[int(parts[i])] = parts[i + 1]

zh = ''
for n in sorted(os.listdir(zh_dir)):
    if n.endswith('.md'):
        zh += open(os.path.join(zh_dir, n), encoding='utf-8').read() + '\n'
blocks = re.split(r'<!--PAGE:(\d+)-->', zh)
ztxt = {}
for i in range(1, len(blocks), 2):
    ztxt[int(blocks[i])] = blocks[i + 1]


def src_words(t):
    return len(re.findall(r'[A-Za-z][A-Za-z\-\']+', BOILER.sub('', t)))


def zh_chars(t):
    return len(re.findall(r'[\u4e00-\u9fff]', t))


print(f'{"pg":>4} {"srcW":>6} {"zhC":>6} {"ratio":>6}')
ratios, flag = [], []
for p in sorted(src):
    w = src_words(src[p])
    c = zh_chars(ztxt.get(p, ''))
    r = c / w if w else 0
    ratios.append(r)
    if w > 30 and (r < LO or r > HI):
        flag.append((p, w, c, round(r, 2)))
    print(f'{p:>4} {w:>6} {c:>6} {r:>6.2f}')

print('\nmedian ratio:', round(sorted(ratios)[len(ratios) // 2], 2))
print(f'flagged (src>30 words, ratio outside {LO}-{HI}):', flag if flag else 'none')
print('\nNOTE: the last page often flags high because part_99_summary.md lands in')
print('its block (no trailing PAGE marker). Verify before treating it as a defect.')
