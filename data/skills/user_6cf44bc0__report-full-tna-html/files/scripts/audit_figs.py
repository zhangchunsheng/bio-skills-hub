# -*- coding: utf-8 -*-
"""CRC 图片完整性全量审计。

三种独立的检查，交叉验证：
  A. 反向查图：把 PDF 每一页的**所有**矢量笔画与位图（不做尺寸过滤）聚成候选图区，
     检查 figs_meta.json 里是否有 bbox 覆盖它。未被覆盖 = 漏提取。
  B. 正向查槽：译文 md 里每个 @@FIG:p:n@@ 是否解析到真实存在的文件；
     每页槽位数 vs meta 图数；槽位编号是否连续、是否与 y 顺序一致。
  C. 产物查图：最终 HTML 里 <figure> 数量、base64 是否可解码、是否有孤儿图片文件。

用法：
    python audit_figs.py <src.pdf> <figs_meta.json> <zh_dir> <html>
"""
import json, os, re, sys, base64, collections
import pymupdf

src, meta_path, zh_dir, html_path = sys.argv[1:5]

meta = json.load(open(meta_path, encoding='utf-8'))
meta = {int(k): v for k, v in meta.items()}
doc = pymupdf.open(src)
NP = len(doc)

# ---------------------------------------------------------------- A. 反向查图
def raw_items(page):
    """所有矢量笔画 + 位图，只排除明显的分隔线与项目符号。"""
    items = []
    for d in page.get_drawings():
        r = pymupdf.Rect(d['rect'])
        w, h = r.width, r.height
        if w > 480 and h < 2.5:          # 通栏分隔线
            continue
        if w < 3 and h < 3:              # 项目符号/句点
            continue
        items.append(r)
    try:
        for i in page.get_image_info():
            items.append(pymupdf.Rect(i['bbox']))
    except Exception:
        pass
    return items


def cluster(items, gap=18):
    out = []
    for r in sorted(items, key=lambda r: (r.y0, r.x0)):
        hit = None
        for m in out:
            if (r.x0 < m.x1 + gap and r.x1 > m.x0 - gap and
                    r.y0 < m.y1 + gap and r.y1 > m.y0 - gap):
                hit = m
                break
        if hit is None:
            out.append(pymupdf.Rect(r))
        else:
            # 坑 #11：Rect 没有 __ior__，hit |= r 不会修改列表元素，
            # 聚类会静默失效。必须用 include_rect()。
            hit.include_rect(r)
    return out


def ink_count(cl, items):
    return sum(1 for r in items
               if r.x0 >= cl.x0 - 2 and r.x1 <= cl.x1 + 2
               and r.y0 >= cl.y0 - 2 and r.y1 <= cl.y1 + 2)


print('=' * 72)
print('A. 反向查图：PDF 里有图但 figs_meta 没覆盖的页面')
print('=' * 72)
missing = []
for pno in range(1, NP + 1):
    page = doc[pno - 1]
    items = raw_items(page)
    if not items:
        continue
    cands = []
    for c in cluster(items):
        if c.width < 60 or c.height < 40:
            continue
        if ink_count(c, items) < 6:      # 太稀疏，多半是表格框线
            continue
        cands.append(c)
    if not cands:
        continue
    mbs = [pymupdf.Rect(f['bbox']) for f in meta.get(pno, [])]
    for c in cands:
        best = 0.0
        for mb in mbs:
            ov = max(0.0, min(c.y1, mb.y1) - max(c.y0, mb.y0))
            best = max(best, ov / max(1.0, c.height))
        if best < 0.55:
            missing.append((pno, c, round(best, 2), len(mbs)))

if not missing:
    print('  未发现漏提取的图区')
for pno, c, ov, n in missing:
    print('  p%-3d 候选图区 y=[%7.1f,%7.1f] x=[%6.1f,%6.1f]  meta覆盖=%.2f  该页meta图数=%d'
          % (pno, c.y0, c.y1, c.x0, c.x1, ov, n))

# ---------------------------------------------------------------- B. 正向查槽
print()
print('=' * 72)
print('B. 正向查槽：@@FIG 标记 vs figs_meta')
print('=' * 72)
names = sorted(n for n in os.listdir(zh_dir)
               if n.startswith('part_') and n.endswith('.md'))
md = '\n\n'.join(open(os.path.join(zh_dir, n), encoding='utf-8').read() for n in names)
lines = md.split('\n')

slots = []          # (line_no, page, idx)
for i, ln in enumerate(lines):
    m = re.match(r'^@@FIG:(\d+):(\d+)@@$', ln.strip())
    if m:
        slots.append((i, int(m.group(1)), int(m.group(2))))
print('槽位总数:', len(slots))

# 解析出每个槽位实际会取到哪张图（复刻 build.py 的映射逻辑）
resolved = {}
by_page = collections.defaultdict(list)
for i, p, n in slots:
    by_page[p].append((i, n))
for p, items_ in by_page.items():
    items_.sort(key=lambda x: x[1])
    nf = len(meta.get(p, []))
    if nf == 0:
        for i, n in items_:
            resolved[(p, n)] = None
        continue
    for j, (i, n) in enumerate(items_):
        resolved[(p, n)] = meta[p][min(j, nf - 1)]['file']

# 1) 槽位数 vs meta 图数
print()
print('每页 槽位数 / meta图数：')
bad_count = []
for p in sorted(set(list(by_page.keys()) + list(meta.keys()))):
    ns = len(by_page.get(p, []))
    nf = len(meta.get(p, []))
    flag = ''
    if ns != nf:
        flag = '   <-- 不一致'
        bad_count.append((p, ns, nf))
    if ns or nf:
        print('  p%-3d  槽位=%d  meta图=%d%s' % (p, ns, nf, flag))

# 2) 文件是否存在
work = os.path.dirname(os.path.dirname(os.path.abspath(meta_path)))
missing_file = []
for (p, n), f in sorted(resolved.items()):
    if f is None:
        continue
    ap = f if os.path.isabs(f) else os.path.join(work, f.replace('\\', '/'))
    if not os.path.exists(ap) or os.path.getsize(ap) == 0:
        missing_file.append(((p, n), ap))
print()
print('解析到的图片文件缺失/为空:', len(missing_file))
for k, ap in missing_file:
    print('   ', k, ap)

# 3) 槽位编号连续性 + 顺序是否与阅读顺序一致（同一页 :1 必须早于 :2）
print()
print('槽位编号检查：')
bad_idx = []
for p, items_ in sorted(by_page.items()):
    idxs = [n for _, n in sorted(items_, key=lambda x: x[0])]
    if idxs != sorted(idxs):
        bad_idx.append((p, idxs))
        print('  p%-3d 编号未按阅读顺序出现: %s' % (p, idxs))
    if sorted(idxs) != list(range(1, len(idxs) + 1)):
        bad_idx.append((p, idxs))
        print('  p%-3d 编号不连续: %s' % (p, sorted(idxs)))
if not bad_idx:
    print('  全部页面槽位编号连续且顺序正确')

# 4) 一张图被多个槽位引用（并排图合并，属正常，但需确认是同一页）
dup = collections.defaultdict(list)
for (p, n), f in resolved.items():
    if f:
        dup[f].append((p, n))
print()
print('同一张图被多个槽位引用（并排合并，正常但需核对）：')
for f, ks in sorted(dup.items()):
    if len(ks) > 1:
        print('  %s  <- %s' % (f, ks))

# ---------------------------------------------------------------- C. 产物查图
print()
print('=' * 72)
print('C. 产物检查：HTML 里的 <figure> 与 base64')
print('=' * 72)
H = open(html_path, encoding='utf-8').read()
figs_html = re.findall(r'<figure class="fig">.*?</figure>', H, re.S)
print('HTML 中 <figure> 数量:', len(figs_html))
bad_b64 = 0
sizes = []
for f in figs_html:
    m = re.search(r'src="data:image/(\w+);base64,([^"]+)"', f)
    if not m:
        bad_b64 += 1
        continue
    try:
        raw = base64.b64decode(m.group(2), validate=True)
        sizes.append(len(raw))
    except Exception as e:
        bad_b64 += 1
        print('  base64 解码失败:', str(e)[:60])
print('base64 解码失败数:', bad_b64)
if sizes:
    print('图片字节数 min/max/合计: %d / %d / %.2f MB'
          % (min(sizes), max(sizes), sum(sizes) / 1048576))
    print('小于 5KB 的可疑图片数:', sum(1 for s in sizes if s < 5120))

# 孤儿图片：磁盘上有、但没有任何槽位用到
used = set(resolved.values())
allf = []
for p, lst in meta.items():
    for f in lst:
        allf.append(f['file'])
orphan = [f for f in allf if f not in used]
print()
print('meta 中的图未被任何槽位引用（孤儿）:', len(orphan))
for f in orphan:
    print('  ', f)
