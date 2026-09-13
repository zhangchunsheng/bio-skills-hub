#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_vault.py — 把一批 dna.json 汇总成一份「网页灵感库」（单文件、离线永久可看）
=============================================================================
用法：
    python build_vault.py <含 dna_*.json 的目录或若干文件> -o vault.html [--emit-cards]

产出：
    vault.html        —— 单文件灵感库，按风格分区，自带筛选导航
    cards/*.html      —— （加 --emit-cards 时）每张卡的独立页面

为什么要单文件：收藏夹的终局痛点是"死链接"。灵感库必须能离线打开、
不依赖原站存活、不依赖网络。所以样式内联、无外部请求、无构建步骤。
"""

from __future__ import annotations

import argparse
import datetime as _dt
import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from jinja2 import Environment, FileSystemLoader, select_autoescape  # noqa: E402

import render_card as RC  # noqa: E402

VAULT_CHROME_CSS = """
/* 灵感库外壳：浅底深字，与卡片同样克制 */
* { box-sizing: border-box; }
body {
  margin: 0; background: #f7f7f5; color: #1a1a1a;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC",
               "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
  font-size: 15px; line-height: 1.7; -webkit-font-smoothing: antialiased;
}
.vault-head { max-width: 1060px; margin: 0 auto; padding: 64px 24px 28px; }
.vault-head h1 { font-size: 34px; letter-spacing: -0.02em; margin: 0 0 10px; font-weight: 600; }
.vault-head p { color: #7a7a74; margin: 0 0 6px; font-size: 14px; }
.vault-stat { font-variant-numeric: tabular-nums; }
.vault-nav {
  position: sticky; top: 0; z-index: 20;
  background: rgba(247,247,245,.92); backdrop-filter: blur(8px);
  border-bottom: 1px solid #e8e8e4;
}
.vault-nav .inner {
  max-width: 1060px; margin: 0 auto; padding: 12px 24px;
  display: flex; flex-wrap: wrap; gap: 8px 18px; align-items: center; font-size: 13px;
}
.vault-nav a { color: #5a5a55; text-decoration: none; padding: 3px 0; border-bottom: 1px solid transparent; }
.vault-nav a:hover { color: #111; border-bottom-color: #bbb; }
.vault-nav .count { color: #b4b4ae; font-variant-numeric: tabular-nums; }
.vault-nav .sep { flex: 1 1 auto; }
.vault-nav .right { color: #b4b4ae; font-size: 12px; }

.vault-body { max-width: 1060px; margin: 0 auto; padding: 0 24px 120px; }
.group { margin-top: 64px; }
.group-head {
  display: flex; align-items: baseline; gap: 14px;
  border-bottom: 1px solid #e0e0da; padding-bottom: 12px; margin-bottom: 8px;
}
.group-head h2 { font-size: 15px; letter-spacing: .1em; text-transform: uppercase; color: #6b6b66; margin: 0; font-weight: 600; }
.group-head .n { font-size: 12px; color: #b4b4ae; font-variant-numeric: tabular-nums; }
.group-head .hint { margin-left: auto; font-size: 12px; color: #b4b4ae; }

.item {
  background: #fff; border: 1px solid #ececE8; border-radius: 4px;
  margin-top: 28px; overflow: hidden;
}
.item > .wrap { padding: 40px 40px 48px; max-width: none; }
.item .toc-note { font-size: 11px; color: #a8a8a2; padding: 10px 40px 0; letter-spacing: .04em; }
@media (max-width: 640px) { .item > .wrap { padding: 28px 20px 36px; } }
"""


def scope_css(css, cls):
    """把一份风格 CSS 限定到 .cls 作用域内。

    多风格汇总到同一个 HTML 时，两套模板都定义了 .wrap/.rule/.label 等同名类，
    直接拼接会互相覆盖 —— 汇总库里所有卡片就变成同一种长相，风格区隔在最后一步功亏一篑。
    """
    css = re.sub(r"@media[^{]*\{(?:[^{}]|\{[^{}]*\})*\}", "", css)
    out = []
    for m in re.finditer(r"([^{}]+)\{([^{}]*)\}", css):
        sel, body = m.group(1).strip(), m.group(2)
        if not sel or sel.startswith("@"):
            continue
        parts = []
        for p in sel.split(","):
            p = p.strip()
            if not p:
                continue
            if p in ("body", "html"):
                parts.append("." + cls)
            elif p.startswith(("body ", "html ")):
                parts.append("." + cls + p[4:])
            elif p.startswith("." + cls):
                parts.append(p)
            else:
                parts.append("." + cls + " " + p)
        if parts:
            out.append(", ".join(parts) + " {" + body + "}")
    return "\n".join(out)


def collect_dna(targets):
    files = []
    for t in targets:
        if os.path.isdir(t):
            files += sorted(glob.glob(os.path.join(t, "dna_*.json")))
            files += sorted(glob.glob(os.path.join(t, "**", "dna_*.json"), recursive=True))
            # 资产库把 DNA 存成 <风格>-<域名>.json（含 dna/ 子目录），
            # 只认 dna_*.json 会让「档案库直接生成灵感库」这条链路断掉。
            files += sorted(glob.glob(os.path.join(t, "*.json")))
            files += sorted(glob.glob(os.path.join(t, "**", "*.json"), recursive=True))
        else:
            files += sorted(glob.glob(t))
    seen, out = set(), []
    for f in files:
        rp = os.path.realpath(f)
        if rp in seen:
            continue
        seen.add(rp)
        try:
            with open(f, "r", encoding="utf-8") as fh:
                data = json.load(fh)
        except Exception as e:
            print(f"[skip] 读取失败 {f}: {e}", file=sys.stderr)
            continue
        # 只收真正的 DNA（标题/清单类 json 由内容特征过滤，不靠文件名）
        if not isinstance(data, dict) or "palette" not in data or "classification" not in data:
            continue
        out.append((f, data))
    return out


def slugify(text, fallback="item"):
    s = re.sub(r"[^\w\u4e00-\u9fff-]+", "-", (text or "").lower()).strip("-")
    return (s or fallback)[:48]


def build_vault(targets, out_path, emit_cards=False, cards_dir=None, title=None):
    styles = RC.available_styles()
    if not styles:
        raise SystemExit("[!] styles/ 下没有任何成品模板，无法建库。")

    items = collect_dna(targets)
    if not items:
        raise SystemExit(f"[!] 没找到 dna_*.json。请先跑 extract_dna.py（目标：{targets}）")

    fallback_tpl = sorted(styles)[0]
    rendered = []
    used_slugs = {}

    for i, (path, dna) in enumerate(items, 1):
        cls_style = (dna.get("classification") or {}).get("style", "minimalist")
        tpl_style = cls_style if cls_style in styles else fallback_tpl
        tpl_dir = os.path.dirname(styles[tpl_style])
        env = Environment(loader=FileSystemLoader(tpl_dir),
                          autoescape=True,
                          trim_blocks=True, lstrip_blocks=True)
        ctx = RC.build_context(dna, style_id=cls_style, style_tpl_id=tpl_style)
        body = env.get_template(RC.TPL_BODY).render(c=ctx)

        base = slugify(ctx["title"] or ctx["source_host"], f"item{i}")
        n = used_slugs.get(base, 0) + 1
        used_slugs[base] = n
        slug = base if n == 1 else f"{base}-{n}"

        rendered.append({"ctx": ctx, "body": body, "slug": slug,
                         "tpl_style": tpl_style, "true_style": cls_style,
                         "dna_path": path})

        if emit_cards:
            cdir = cards_dir or os.path.join(os.path.dirname(os.path.abspath(out_path)), "cards")
            os.makedirs(cdir, exist_ok=True)
            full = env.get_template(RC.TPL_CARD).render(c=ctx)
            with open(os.path.join(cdir, f"{slug}.html"), "w", encoding="utf-8") as fh:
                fh.write(full)

    # 按真实风格分组（模板待建的风格也如实显示，并说明用了哪套模板兜底）
    groups = {}
    for r in rendered:
        groups.setdefault(r["true_style"], []).append(r)
    order = [s for s in RC.STYLE_ORDER if s in groups] + \
            [s for s in groups if s not in RC.STYLE_ORDER]

    css_parts = []
    for sid, sp in sorted(styles.items()):
        css_alt = RC.card_css_path(sp)
        if os.path.isfile(css_alt):
            css_parts.append("/* ==== style: %s ==== */\n" % sid
                             + scope_css(open(css_alt, encoding="utf-8").read(), "style-" + sid))
    css = "\n".join(css_parts)

    now = _dt.datetime.now().strftime("%Y-%m-%d %H:%M")
    site_count = len({r["ctx"]["source_host"] for r in rendered})
    tpl_pending = [s for s in order if s not in styles]

    parts = []
    parts.append("<!DOCTYPE html>\n<html lang=\"zh-CN\">\n<head>\n<meta charset=\"utf-8\">")
    parts.append('<meta name="viewport" content="width=device-width,initial-scale=1">')
    parts.append(f"<title>{title or '网页灵感风格模板库'}</title>")
    parts.append("<style>\n" + css + "\n" + VAULT_CHROME_CSS + "\n</style>\n</head>\n<body>")

    parts.append('<div class="vault-head">')
    parts.append(f"<h1>{title or '网页灵感风格模板库'}</h1>")
    parts.append(f'<p class="vault-stat">{len(rendered)} 张灵感卡 · {site_count} 个站点 · '
                 f'{len(order)} 类风格 · 生成于 {now}</p>')
    parts.append('<p>每张卡都是对原页面的<b>结构化理解</b>（配色 / 字体 / 排版节奏 / 文字内容），'
                 '不是截图 —— 可搜索、可 diff、可离线永久查看。</p>')
    if tpl_pending:
        names = "、".join(RC.STYLE_NAMES.get(s, s) for s in tpl_pending)
        parts.append(f'<p>[!] 待补模板：{names} —— 这些卡片暂用'
                     f'「{RC.STYLE_NAMES.get(fallback_tpl, fallback_tpl)}」模板呈现，'
                     f'配色与字体参数仍是原页真实值。</p>')
    parts.append("</div>")

    parts.append('<nav class="vault-nav"><div class="inner">')
    for s in order:
        g = groups[s]
        nm = RC.STYLE_NAMES.get(s, s)
        parts.append(f'<a href="#g-{s}">{nm} <span class="count">{len(g)}</span></a>')
    parts.append('<span class="sep"></span>')
    parts.append(f'<span class="right">web-inspiration-vault</span>')
    parts.append("</div></nav>")

    parts.append('<div class="vault-body">')
    for s in order:
        g = groups[s]
        nm = RC.STYLE_NAMES.get(s, s)
        hint = "已有成品模板" if s in styles else "模板待建 · 兜底呈现"
        parts.append(f'<div class="group" id="g-{s}">')
        parts.append('<div class="group-head">')
        parts.append(f"<h2>{nm}</h2><span class=\"n\">{len(g)} 张</span>")
        parts.append(f'<span class="hint">{hint}</span>')
        parts.append("</div>")
        for r in g:
            c = r["ctx"]
            parts.append(f'<article class="item" id="{r["slug"]}">')
            parts.append(f'<div class="toc-note">{c["source_host"]} · {c["extracted_at"]} · '
                         f'置信度 {c["confidence"]}</div>')
            parts.append(f'<div class="style-{r["tpl_style"]}">')
            parts.append(r["body"])
            parts.append("</div>")
            parts.append("</article>")
        parts.append("</div>")
    parts.append("</div>\n</body>\n</html>")

    html = "\n".join(parts)
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)

    return {
        "out": out_path,
        "count": len(rendered),
        "groups": {RC.STYLE_NAMES.get(s, s): len(g) for s, g in groups.items()},
        "styles_missing": tpl_pending,
        "bytes": len(html.encode("utf-8")),
    }


def main():
    ap = argparse.ArgumentParser(description="把 dna.json 汇总成单文件灵感库")
    ap.add_argument("targets", nargs="+", help="目录或 dna_*.json 文件（支持通配）")
    ap.add_argument("-o", "--out", required=True, help="输出 vault.html")
    ap.add_argument("--emit-cards", action="store_true", help="同时输出每张卡的独立 HTML")
    ap.add_argument("--title", default=None)
    args = ap.parse_args()

    res = build_vault(args.targets, args.out, emit_cards=args.emit_cards, title=args.title)
    print(f"灵感库 : {res['out']}")
    print(f"卡片数 : {res['count']}   体积 {res['bytes'] / 1024:.1f} KB（单文件、零外部请求）")
    print(f"分组   : {res['groups']}")
    if res["styles_missing"]:
        print(f"待补模板: {res['styles_missing']}")
    return res


if __name__ == "__main__":
    main()
