# -*- coding: utf-8 -*-
"""核对 @@FIG 槽位映射：图注内容是否真的属于该槽位取到的那张图。

背景：图表提取器会把「并排的两张小图」合并成一张宽图，导致该页实际图数少于
    页面上的展陈（exhibit）数。若译文里仍按展陈顺序写 @@FIG:p:1@@ / :2@@ / :3@@，
    build.py 会把后一个槽位映射到**下一张真实图**，于是图注与图错位
    （例：p29 的「图（右）心脏特征」被挂到了 OS 曲线图上）。

算法：
  1. 从 md 里按页取出 (图注行, @@FIG:p:n@@ 槽位) 序列
  2. 槽位 n 实际取到的图 = figs_meta[p][min(n, 该页图数) - 1]
  3. 取图注里的英文原文（最后一个全角括号内的内容，或整行）
  4. 用 PDF 文本块坐标判断该英文落在哪个图 bbox 内
  5. 若落点与槽位取到的图不一致 -> 报错并给出应改成的 n

用法：
    python figmap_check.py <src.pdf> <figs_meta.json> <zh目录>
"""
import re
import sys
import json
import glob
import os

import pymupdf  # noqa

PDF, META, ZHDIR = sys.argv[1], sys.argv[2], sys.argv[3]

meta = json.load(open(META, encoding='utf-8'))
figs = {}
if isinstance(meta, dict):
    for p, v in meta.items():
        figs[int(p)] = v if isinstance(v, list) else [v]
else:
    for f in meta:
        figs.setdefault(int(f['page']), []).append(f)

md = ''
for f in sorted(glob.glob(os.path.join(ZHDIR, 'part_*.md'))):
    md += open(f, encoding='utf-8').read()

# 收集 (page, caption, slot_idx)
slots = []
lines = md.split('\n')
for i, ln in enumerate(lines):
    m = re.match(r'^@@FIG:(\d+):(\d+)@@$', ln.strip())
    if not m:
        continue
    p, n = int(m.group(1)), int(m.group(2))
    cap = ''
    for j in range(i - 1, max(-1, i - 4), -1):
        s = lines[j].strip()
        if not s:
            continue
        if s.startswith('**图') or s.startswith('**图表'):
            cap = s
        break
    slots.append((p, n, cap, i + 1))

doc = pymupdf.open(PDF)
cache = {}


def blocks_in(pg, bbox):
    """返回落在 bbox 内的文本（小写、压缩空白）。"""
    key = pg
    if key not in cache:
        page = doc[pg - 1]
        d = page.get_text('dict')
        out = []
        for bl in d['blocks']:
            if bl['type'] != 0:
                continue
            txt = ' '.join(s['text'] for ln in bl['lines'] for s in ln['spans'])
            out.append((bl['bbox'], ' '.join(txt.split()).lower()))
        cache[key] = out
    res = []
    for r, txt in cache[key]:
        if r[1] >= bbox[1] - 2 and r[3] <= bbox[3] + 2:
            res.append(txt)
    return ' || '.join(res)


def english_of(cap):
    """取图注里的英文原文。"""
    if not cap:
        return ''
    m = re.findall(r'（([^（）]*[A-Za-z][^（）]*)）', cap)
    if m:
        return m[-1].strip().lower()
    return ''


bad = 0
checked = 0
for p, n, cap, lineno in slots:
    fl = figs.get(p, [])
    if not fl:
        print('⚠ 第%d页 无图，却有槽位 @@FIG:%d:%d@@' % (p, p, n))
        bad += 1
        continue
    eng = english_of(cap)
    if not eng:
        continue
    # 取 3 个以上的英文词作为指纹
    toks = [t for t in re.findall(r'[a-z0-9]{3,}', eng)][:6]
    if len(toks) < 2:
        continue
    checked += 1
    eff = min(n, len(fl)) - 1
    hit_eff = all(t in blocks_in(p, fl[eff]['bbox']) for t in toks)
    if hit_eff:
        continue
    # 找真正的归属
    target = None
    for k, f in enumerate(fl):
        if all(t in blocks_in(p, f['bbox']) for t in toks):
            target = k + 1
            break
    bad += 1
    print('✗ 行%d  @@FIG:%d:%d@@  实际取到第%d张，但图注属于第%d张'
          % (lineno, p, n, eff + 1, target if target else -1))
    print('     图注: %s' % cap[:110])
    print('     指纹: %s' % ' | '.join(toks))

doc.close()
print('\n检查 %d 个带英文图注的槽位，错位 %d 个' % (checked, bad))
