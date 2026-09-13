# -*- coding: utf-8 -*-
"""Assemble translated markdown parts + extracted figures into a single-file HTML.

Layout convention (all paths relative to the working dir):
    out/full_raw.txt          source text (from extract_text.py)
    out/figs_meta.json        figure metadata (from figs_extract.py)
    out/figs/pNNN_N.jpg       rendered figures
    out/zh/part_01.md ...     translated chunks, may contain:
                                <!--PAGE:N-->          page anchor
                                @@FIG:page:index@@     figure slot

Usage:
    python build.py <meta_json> <parts_dir> <shell_html> <style_css> <out_html> "<title>"
"""
import json, re, os, base64, html, collections, sys

meta_json, parts_dir = sys.argv[1], sys.argv[2]
shell_path, css_path = sys.argv[3], sys.argv[4]
out_html = sys.argv[5]
DOC_TITLE = sys.argv[6] if len(sys.argv) > 6 else '翻译文档'

meta = json.load(open(meta_json, encoding='utf-8'))
figs = {int(k): v for k, v in meta.items()}

# `file` 字段在 figs_meta.json 里是相对生成该 meta 时的工作目录；
# 这个工作目录就是 meta_json 所在目录的上一层（例如 crc/out -> crc）。
FIG_BASE = os.path.dirname(os.path.dirname(os.path.abspath(meta_json)))


def _resolve_fig_path(p):
    if os.path.isabs(p):
        return p
    return os.path.join(FIG_BASE, p.replace('\\', '/'))


# ------------------------------------------------------------------ helpers
def esc_attr(t):
    return html.escape(t, quote=True)


def inl(t):
    t = html.escape(t, quote=False)
    t = re.sub(r'`([^`]+)`', r'<code>\1</code>', t)
    t = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', t)
    t = re.sub(r'\[([^\]]+)\]\(([^)]+)\)',
               r'<a href="\2" target="_blank" rel="noopener">\1</a>', t)
    t = re.sub(r'(?<!["=>])(https?://[^\s<）)]+)',
               r'<a href="\1" target="_blank" rel="noopener">\1</a>', t)
    return t


# ---------------------------------------------------------------- load parts
def part_key(name):
    m = re.match(r'part_(\d+)([a-z]*)\.md$', name)
    return (int(m.group(1)), m.group(2)) if m else (9999, name)


names = sorted((n for n in os.listdir(parts_dir)
                if n.startswith('part_') and n.endswith('.md')), key=part_key)
md_parts = [open(os.path.join(parts_dir, n), encoding='utf-8').read() for n in names]
print('parts:', len(names))
md = '\n\n'.join(md_parts)

# ---------------------------------------------- resolve @@FIG:p:n@@ markers
lines = md.split('\n')
mark_idx = []
for i, ln in enumerate(lines):
    s = ln.strip()
    m = re.match(r'^@@FIG:(\d+):(\d+)@@$', s)
    if m:
        mark_idx.append((i, int(m.group(1)), int(m.group(2))))
    elif '@@FIG:' in ln:
        print('!! unparsed marker:', repr(ln))

by_page = collections.defaultdict(list)
for i, p, n in mark_idx:
    by_page[p].append((i, n))

mapping = {}
for p, items in by_page.items():
    items.sort(key=lambda x: x[1])
    nf = len(figs.get(p, []))
    if nf == 0:
        for i, n in items:
            mapping[(p, n)] = None
        continue
    for j, (i, n) in enumerate(items):
        mapping[(p, n)] = figs[p][min(j, nf - 1)]['file']

img_b64 = {}


def data_uri(path):
    if path is None:
        return None
    real = _resolve_fig_path(path)
    if real not in img_b64:
        with open(real, 'rb') as f:
            img_b64[real] = base64.b64encode(f.read()).decode()
    return 'data:image/jpeg;base64,' + img_b64[real]


CAP_RE = re.compile(r'^\*\*图(?:（[左上右下]）)?[：:](.*?)\*\*$')


def find_cap(i):
    for j in range(i - 1, max(-1, i - 4), -1):
        c = CAP_RE.match(lines[j].strip())
        if c:
            return j, c.group(1).strip()
        if lines[j].strip():
            return None, None
    return None, None


# markers rendering the SAME image -> one <figure> with merged caption
groups = collections.defaultdict(list)
for i, p, n in mark_idx:
    path = mapping[(p, n)]
    if path:
        groups[(p, path)].append((i, n))

emit = {}
drop_lines = set()
for (p, path), lst in groups.items():
    lst.sort(key=lambda x: x[1])
    caps = []
    for i, n in lst:
        ci, ct = find_cap(i)
        if ci is not None:
            drop_lines.add(ci)
            if ct:
                caps.append(ct)
    emit[lst[0][0]] = (' ｜ '.join(caps) if len(lst) > 1 else caps[0]) if caps else None
    for i, n in lst[1:]:
        drop_lines.add(i)

final = []
n_img = 0
for i, ln in enumerate(lines):
    if i in drop_lines:
        continue
    m = re.match(r'^@@FIG:(\d+):(\d+)@@$', ln.strip())
    if m:
        p, n = int(m.group(1)), int(m.group(2))
        uri = data_uri(mapping[(p, n)])
        if uri is None:
            continue
        cap = emit.get(i)
        w = h = None
        for f in figs.get(p, []):
            if f['file'] == mapping[(p, n)]:
                w, h = f['w'], f['h']
                break
        cap_html = '<figcaption>%s</figcaption>' % inl(cap) if cap else ''
        final.append('<figure class="fig"><img loading="lazy" src="%s" alt="%s" '
                     'style="aspect-ratio:%d/%d">%s</figure>'
                     % (uri, esc_attr(cap or 'figure p%d' % p), w or 4, h or 3, cap_html))
        n_img += 1
        continue
    final.append(ln)

print('figures placed:', n_img, 'unique images:', len(img_b64))
md = '\n'.join(final)

# ------------------------------------------------------------------ markdown
TOC = []


def render_list(items, level):
    res, i = [], 0
    while i < len(items):
        ind, txt = items[i]
        if ind < level:
            i += 1
            continue
        if ind == level:
            sub, j = [], i + 1
            while j < len(items) and items[j][0] > level:
                sub.append(items[j]); j += 1
            res.append('<li>%s%s</li>' % (
                inl(txt),
                '<ul>%s</ul>' % render_list(sub, level + 1) if sub else ''))
            i = j
        else:
            i += 1
    return ''.join(res)


def render(mdtext):
    lines = mdtext.split('\n')
    out, buf = [], []
    i = 0

    def flush():
        if buf:
            out.append('<p>%s</p>' % inl(' '.join(buf).strip()))
            buf.clear()

    while i < len(lines):
        ln = lines[i]
        s = ln.strip()

        if s.startswith('<figure'):
            flush(); out.append(s); i += 1; continue

        m = re.match(r'^<!--PAGE:(\d+)-->$', s)
        if m:
            flush()
            p = int(m.group(1))
            out.append('<div class="pagebreak" id="page-%d">'
                       '<span class="pageno">原文第 %d 页</span></div>' % (p, p))
            i += 1; continue

        if not s:
            flush(); i += 1; continue

        if re.match(r'^(-{3,}|\*{3,}|_{3,})$', s):
            flush(); out.append('<hr>'); i += 1; continue

        m = re.match(r'^(#{1,6})\s+(.*)$', s)
        if m:
            flush()
            lvl = len(m.group(1))
            txt = m.group(2).strip()
            anc = 'h-%d' % len(TOC)
            TOC.append((lvl, txt, anc))
            out.append('<h%d id="%s">%s</h%d>' % (lvl, anc, inl(txt), lvl))
            i += 1; continue

        if s.startswith('|') and i + 1 < len(lines) and \
                re.match(r'^\|[\s:|-]+\|$', lines[i + 1].strip()):
            flush()
            rows, j = [], i
            while j < len(lines) and lines[j].strip().startswith('|'):
                rows.append(lines[j].strip()); j += 1
            cells = [[c.strip() for c in r.strip('|').split('|')] for r in rows]
            th = ''.join('<th>%s</th>' % inl(c) for c in cells[0])
            tb = ''.join('<tr>%s</tr>' % ''.join('<td>%s</td>' % inl(c) for c in r)
                         for r in cells[2:])
            out.append('<div class="tw"><table><thead><tr>%s</tr></thead>'
                       '<tbody>%s</tbody></table></div>' % (th, tb))
            i = j; continue

        if s.startswith('>'):
            flush()
            qb = []
            while i < len(lines) and lines[i].strip().startswith('>'):
                qb.append(lines[i].strip().lstrip('>').strip()); i += 1
            # render() 返回的是 list，必须 join；直接 %s 会输出 Python repr
            # （表现为页面上出现 "['<p>…']" 这种方括号+引号的字面量）
            sub = ''.join(render('\n'.join(qb)))
            out.append('<blockquote>%s</blockquote>' % sub)
            continue

        m = re.match(r'^(\s*)([-*+]|\d+\.)\s+(.*)$', ln)
        if m:
            flush()
            ordered = ln.lstrip()[0].isdigit()
            items = []
            while i < len(lines):
                mm = re.match(r'^(\s*)([-*+]|\d+\.)\s+(.*)$', lines[i])
                if not mm:
                    break
                if (lines[i].lstrip()[0].isdigit()) != ordered and items:
                    break
                items.append((len(mm.group(1)) // 2, mm.group(3)))
                i += 1
            tag = 'ol' if ordered else 'ul'
            out.append('<%s>%s</%s>' % (tag, render_list(items, 0), tag))
            continue

        buf.append(s)
        i += 1
    flush()
    return out


body_parts = []
for ch in re.split(r'(?=<!--PAGE:\d+-->)', md):
    body_parts.extend(render(ch))
body = '\n'.join(body_parts)

toc_html = '\n'.join(
    '<a class="t%d" href="#%s">%s</a>' % (lvl, anc, esc_attr(txt))
    for lvl, txt, anc in TOC if lvl <= 3)

# --------------------------------------------------------------------- shell
HTML = open(shell_path, encoding='utf-8').read()
CSS = open(css_path, encoding='utf-8').read()
HTML = HTML.replace('__CSS__', CSS)
HTML = HTML.replace('__TOC__', toc_html).replace('__BODY__', body)
HTML = HTML.replace('__TITLE__', DOC_TITLE)
with open(out_html, 'w', encoding='utf-8') as f:
    f.write(HTML)
print('html MB:', round(len(HTML.encode()) / 1048576, 2),
      'toc:', len(toc_html.split('\n')))
