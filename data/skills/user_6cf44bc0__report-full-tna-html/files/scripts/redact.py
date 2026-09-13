#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
redact.py — 删除卖方研报中「收件人身份标识」样板文字（Cowen/TD Securities 等）。

背景：TD Cowen 研报首页固定带有三行研究团队邮箱 + 一行
"This report is intended for <收件人邮箱>. Unauthorized distribution prohibited."
这类内容暴露收件人身份，且对译文无信息价值，须在译文中删除。
后续其他 Cowen 文章沿用同一规则：本脚本直接复用。

用法（幂等，可重复运行）：
    python redact.py <文件或目录> [<文件或目录> ...] [--check]
        --check   只报告命中数量，不写盘
    目录模式下递归处理 *.md；单文件按扩展名（.md / .html / .htm）自动选规则。

删除规则（md，按行）：
  1. 含 (pharmateam|biotechteam|medtechteam)@tdsecurities.com 的行
  2. 仅由「TD Cowen 制药/生物技术/医疗技术 团队」构成的行（列表符/加粗/冒号可有）
  3. 「研究团队联系方式」之类的小标题行
  4. 收件人专属声明行：含 @ 邮箱 且含 仅供 / intended (only) for / for use only by
  5. 收尾：合并 3+ 连续空行为 2；删除因上述删除而孤立的 --- 水平线

删除规则（html，按元素）：
  <p> / <li> / <blockquote> 元素文本命中上述邮箱或收件人声明时整块删除；
  随后清空空的 <ul></ul>。

注意：法律免责声明里的功能性地址（Privacy.EAP@tdsecurities.com）与
公司网址（portal.tdsecurities.com）不属于收件人标识，保留。
"""
import re
import sys
from pathlib import Path

# ---------- 匹配规则 ----------
# 三个研究团队别名邮箱（收件人无关的退订邮箱 Privacy.EAP@ 不在其中）
RE_TEAM_EMAIL = re.compile(
    r'(pharmateam|biotechteam|medtechteam)@tdsecurities\.com', re.I)

# 「TD Cowen 制药团队」这类纯标题行（可能有 -/*/>/加粗/冒号）
RE_TEAM_TITLE = re.compile(
    r'^\s*(?:[-*+]\s*)?(?:>\s*)?(?:\*{1,2})?\s*'
    r'TD\s*Cowen\s*'
    r'(?:制药|生物技术|医疗技术|Pharma|Biotech|MedTech|Med\s*Tech)'
    r'\s*(?:团队|Team)?'
    r'\s*[:：]?\s*(?:\*{1,2})?\s*$', re.I)

# 「研究团队联系方式」小标题
RE_CONTACT_HEAD = re.compile(
    r'^\s*(?:>\s*)?(?:\*{1,2})?\s*(?:TD\s*Cowen\s*)?'
    r'(?:研究团队|团队)?联系方式\s*[:：]?\s*(?:\*{1,2})?\s*$')

# 收件人专属声明：含邮箱 @ 且含 仅供/仅拟/intended for/for use only by
RE_SOLO_USE = re.compile(
    r'@[A-Za-z0-9._-]+\.[A-Za-z]{2,}', re.I)
RE_SOLO_MARK = re.compile(
    r'(仅供|仅拟|仅提供|专用|限\b|intended\s+(?:only\s+)?for|for\s+use\s+only\s+by'
    r'|authorized\s+recipient|solely\s+for\s+the\s+use\s+of)', re.I)


def _is_solo_use(line: str) -> bool:
    """收件人专属声明行：同时含邮箱与「仅供…使用」类措辞。"""
    if '@' not in line:
        return False
    # 法律免责声明中的 Privacy.EAP@tdsecurities.com 不做删除
    if 'Privacy.EAP@' in line:
        return False
    return bool(RE_SOLO_USE.search(line) and RE_SOLO_MARK.search(line))


def _drop_line(line: str) -> bool:
    if RE_TEAM_EMAIL.search(line):
        return True
    if RE_TEAM_TITLE.match(line):
        return True
    if RE_CONTACT_HEAD.match(line):
        return True
    if _is_solo_use(line):
        return True
    return False


def redact_md(text: str):
    """返回 (新文本, 删除行数)。"""
    lines = text.split('\n')
    keep, dropped_idx, dropped = [], set(), 0
    for i, ln in enumerate(lines):
        if _drop_line(ln):
            dropped += 1
            dropped_idx.add(i)
            continue
        keep.append(ln)

    # 只清理「越过空行紧邻被删内容」的孤立 --- 水平线。
    # 注意：正文里 --- 后面紧跟 <!--PAGE:N--> 是合法用法（如分页前的分割线），
    # 不能按「下一个非空行是 PAGE 标记」误删，否则会删掉正文里真实的分隔线。
    keep_idx = [i for i in range(len(lines)) if i not in dropped_idx]

    def _adjacent_dropped(k):
        """当前位置越过空行向上/向下遇到的第一个非空行，是否是被删除的行。"""
        for step in (-1, 1):
            j = k + step
            while 0 <= j < len(lines):
                if lines[j].strip():
                    if j in dropped_idx:
                        return True
                    break
                j += step
        return False

    out = []
    for k, ln in enumerate(keep):
        if ln.strip() in ('---', '***', '___') and _adjacent_dropped(keep_idx[k]):
            dropped += 1
            continue
        out.append(ln)
    keep = out

    # 合并 3+ 连续空行
    out, blanks = [], 0
    for ln in keep:
        if not ln.strip():
            blanks += 1
            if blanks > 2:
                dropped += 1
                continue
        else:
            blanks = 0
        out.append(ln)

    return '\n'.join(out), dropped


RE_HTML_BLOCK = re.compile(
    r'<(?P<tag>p|li|blockquote|div)\b[^>]*>(?P<inner>.*?)</(?P=tag)>',
    re.S | re.I)


def redact_html(text: str):
    """返回 (新文本, 删除元素数)。"""
    dropped = 0

    def _once(s):
        nonlocal dropped
        def rep(m):
            nonlocal dropped
            inner = m.group('inner')
            plain = re.sub(r'<[^>]+>', '', inner)
            hit = (RE_TEAM_EMAIL.search(plain) or _is_solo_use(plain)
                   or (RE_TEAM_TITLE.match(plain.strip())
                       if plain.strip() else False))
            if hit:
                dropped += 1
                return ''
            return m.group(0)
        return RE_HTML_BLOCK.sub(rep, s)

    prev = None
    while prev != text:
        prev = text
        text = _once(text)

    # 清空空的 ul
    text, k = re.subn(r'<ul>\s*</ul>', '', text)
    dropped += k
    return text, dropped


def process(path: Path, check: bool):
    suf = path.suffix.lower()
    text = path.read_text(encoding='utf-8')
    if suf == '.md':
        new, n = redact_md(text)
    elif suf in ('.html', '.htm'):
        new, n = redact_html(text)
    else:
        return 0
    if not check and n and new != text:
        path.write_text(new, encoding='utf-8')
    return n


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    check = '--check' in sys.argv
    if not args:
        print(__doc__)
        return 1

    total = 0
    for a in args:
        p = Path(a)
        targets = []
        if p.is_dir():
            targets = sorted(p.rglob('*.md'))
        elif p.is_file():
            targets = [p]
        for t in targets:
            n = process(t, check)
            total += n
            if n:
                print(f'{"[check] " if check else ""}{t}: 删除 {n} 项')
    print(f'{"[check] " if check else ""}合计: {total}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
