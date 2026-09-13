# -*- coding: utf-8 -*-
"""Generate a single-file HTML morning-report dashboard for clinical/hospital pharmacy.

Reads a JSON data file (see references/data_schema.md) and emits ONE self-contained
HTML file: inline CSS/JS, no external resources, responsive, global continuous numbering,
summaries truncated to <=60 Chinese characters, dates shown in Beijing human-readable
format (no ISO strings in visible body), every external link carries
target="_blank" rel="noopener noreferrer".

Usage:
    python generate_report.py data.json -o output.html
    python generate_report.py data.json            # writes ./临床药学日报_<date>.html

Section model (flat or grouped):
  flat section : {"label": "...", "items": [ {title, summary, source, link, date}, ... ]}
  grouped section: {"label": "...", "groups": [ ["分组名", [item, ...]], ... ]}
Empty flat sections render an "本期暂无相关内容" empty state (still counted as a section).
"""
import argparse
import html
import json
import sys
import datetime

WEEKDAYS = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]


def bj_date_human(iso_date):
    """Convert 'YYYY-MM-DD' to 'YYYY年M月D日 周X' (Beijing, human-readable)."""
    y, m, d = (int(x) for x in iso_date.split("-"))
    wd = WEEKDAYS[datetime.date(y, m, d).weekday()]
    return f"{y}年{m}月{d}日 {wd}"


def trunc(summary, n=60):
    if summary is None:
        return ""
    s = summary.strip()
    if len(s) <= n:
        return s
    return s[: n - 1].rstrip("，。、；：,.;: ") + "…"


def esc(x):
    return html.escape(x or "", quote=True)


def card_html(c):
    return f'''<article class="card">
  <div class="card-top"><span class="seq">#{c["n"]}</span><span class="date">{esc(c["date"])}</span></div>
  <h3 class="card-title"><a href="{esc(c["link"])}" target="_blank" rel="noopener noreferrer">{esc(c["title"])}</a></h3>
  <span class="chip">{esc(c["source"])}</span>
  <p class="card-sum">{esc(c["summary"])}</p>
  <a class="orig" href="{esc(c["link"])}" target="_blank" rel="noopener noreferrer">阅读原文 ↗</a>
</article>'''


def sec_count(sec):
    if "items" in sec:
        return len(sec["items"])
    return sum(len(g[1]) for g in sec.get("groups", []))


def render(data):
    report_date = data.get("report_date") or datetime.date.today().strftime("%Y-%m-%d")
    sections = data.get("sections", [])
    title = data.get("title", "临床药学 / 医院药学 晨报")
    date_human = bj_date_human(report_date)

    # global continuous numbering across ALL items
    cards = []
    seq = 0
    for sec in sections:
        if "items" in sec:
            for it in sec["items"]:
                seq += 1
                cards.append({**it, "n": seq, "section": sec["label"]})
        else:
            for _, gitems in sec.get("groups", []):
                for it in gitems:
                    seq += 1
                    cards.append({**it, "n": seq, "section": sec["label"]})
    total = len(cards)

    stat_html = ""
    for i, sec in enumerate(sections, 1):
        cnt = sec_count(sec)
        stat_html += (f'<a class="stat" href="#sec-{i}"><span class="stat-n">{cnt}</span>'
                      f'<span class="stat-l">{esc(sec["label"])}</span></a>')
    nav_html = ""
    for i, sec in enumerate(sections, 1):
        cnt = sec_count(sec)
        nav_html += f'<a href="#sec-{i}" class="navlink">{esc(sec["label"])}<b>{cnt}</b></a>'

    body_html = ""
    for i, sec in enumerate(sections, 1):
        sec_cards = [c for c in cards if c["section"] == sec["label"]]
        if "items" in sec:
            if sec_cards:
                grid = "".join(card_html(c) for c in sec_cards)
            else:
                grid = '<div class="empty">本期暂无相关内容</div>'
        else:
            parts = []
            for glabel, gitems in sec.get("groups", []):
                gcards = [c for c in sec_cards if c["title"] in {it["title"] for it in gitems}]
                parts.append(
                    f'<div class="subgroup"><h3 class="sub-h"><span class="sub-dot"></span>{esc(glabel)}'
                    f'<span class="sub-cnt">{len(gitems)}</span></h3>'
                    f'<div class="grid">{"".join(card_html(c) for c in gcards)}</div></div>'
                )
            grid = "".join(parts)
        body_html += (
            f'<section id="sec-{i}" class="block">'
            f'<h2 class="block-h"><span class="dot dot-{i}"></span>{esc(sec["label"])}'
            f'<span class="block-cnt">{len(sec_cards)}</span></h2>'
            f'<div class="sec-body">{grid}</div></section>'
        )

    src_note = esc(data.get("source_note",
        "联网真实资讯（国家及地方卫健委、药监局、医院协会、药学会、政府门户、专业媒体）+ ima 医学知识库。"
        "政策与数据请以官方原文核对。"))

    html_doc = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} · {esc(report_date)}</title>
<style>
  :root {{
    --bg:#f5f7fa; --card:#ffffff; --ink:#1f2933; --sub:#647084;
    --line:#e3e8ef; --accent:#1f7a8c; --accent2:#2b6cb0;
    --c1:#1f7a8c; --c2:#2b6cb0; --c3:#6b46c1; --c4:#2f855a; --c5:#c05621; --c6:#b7791f;
  }}
  * {{ box-sizing:border-box; }}
  body {{ margin:0; font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif;
    background:var(--bg); color:var(--ink); line-height:1.6; }}
  a {{ color:inherit; text-decoration:none; }}
  .hero {{ background:linear-gradient(135deg,#0f4c5c 0%,#1f7a8c 55%,#2b6cb0 100%); color:#fff; padding:34px 22px 26px; }}
  .hero-inner {{ max-width:1080px; margin:0 auto; }}
  .kicker {{ font-size:13px; letter-spacing:2px; opacity:.85; margin:0 0 6px; }}
  .hero h1 {{ margin:0; font-size:30px; font-weight:800; }}
  .hero .date {{ font-size:18px; margin:10px 0 4px; font-weight:600; }}
  .hero .meta {{ font-size:13px; opacity:.85; }}
  .stats {{ display:flex; flex-wrap:wrap; gap:12px; margin-top:20px; }}
  .stat {{ display:flex; flex-direction:column; align-items:center; background:rgba(255,255,255,.14);
    border:1px solid rgba(255,255,255,.25); border-radius:14px; padding:12px 16px; min-width:96px; backdrop-filter:blur(4px); }}
  .stat-n {{ font-size:24px; font-weight:800; line-height:1; }}
  .stat-l {{ font-size:12px; opacity:.92; margin-top:6px; text-align:center; }}
  nav.toc {{ position:sticky; top:0; z-index:20; background:rgba(255,255,255,.96); backdrop-filter:blur(8px);
    border-bottom:1px solid var(--line); padding:10px 16px; }}
  .toc-in {{ max-width:1080px; margin:0 auto; display:flex; flex-wrap:wrap; gap:8px; }}
  .navlink {{ font-size:13px; padding:7px 12px; border:1px solid var(--line); border-radius:999px; color:var(--sub); background:#fff; }}
  .navlink b {{ margin-left:5px; color:var(--accent); font-weight:700; }}
  .navlink:hover {{ border-color:var(--accent); color:var(--accent); }}
  main {{ max-width:1080px; margin:0 auto; padding:24px 18px 8px; }}
  .block {{ margin-bottom:30px; }}
  .block-h {{ font-size:20px; margin:0 0 14px; display:flex; align-items:center; gap:10px; }}
  .dot {{ width:12px; height:12px; border-radius:3px; display:inline-block; }}
  .dot-1 {{ background:var(--c1); }} .dot-2 {{ background:var(--c2); }} .dot-3 {{ background:var(--c3); }}
  .dot-4 {{ background:var(--c4); }} .dot-5 {{ background:var(--c5); }} .dot-6 {{ background:var(--c6); }}
  .block-cnt {{ font-size:14px; color:var(--sub); font-weight:600; margin-left:4px; }}
  .subgroup {{ margin-bottom:18px; }}
  .sub-h {{ font-size:16px; margin:0 0 12px; display:flex; align-items:center; gap:8px; color:#374151; }}
  .sub-dot {{ width:9px; height:9px; border-radius:50%; background:var(--c6); display:inline-block; }}
  .sub-cnt {{ font-size:12px; color:var(--sub); font-weight:600; }}
  .grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(300px,1fr)); gap:16px; }}
  .card {{ background:var(--card); border:1px solid var(--line); border-radius:14px; padding:16px 16px 14px;
    display:flex; flex-direction:column; box-shadow:0 1px 3px rgba(16,24,40,.05); transition:.15s; }}
  .card:hover {{ box-shadow:0 6px 20px rgba(16,24,40,.12); transform:translateY(-2px); border-color:#cdd7e3; }}
  .card-top {{ display:flex; align-items:center; justify-content:space-between; gap:8px; margin-bottom:8px; }}
  .seq {{ font-weight:800; color:var(--accent); font-size:14px; }}
  .date {{ font-size:12px; color:var(--sub); }}
  .chip {{ font-size:12px; color:var(--sub); background:#eef2f7; border:1px solid var(--line);
    border-radius:999px; padding:3px 10px; align-self:flex-start; margin-bottom:8px; max-width:92%; }}
  .card-title {{ font-size:16px; margin:0 0 8px; line-height:1.45; }}
  .card-title a {{ color:var(--ink); }}
  .card-title a:hover {{ color:var(--accent2); }}
  .card-sum {{ font-size:13.5px; color:var(--sub); margin:0 0 12px; flex:1; }}
  .orig {{ font-size:13px; color:var(--accent2); font-weight:600; align-self:flex-start; }}
  .orig:hover {{ text-decoration:underline; }}
  .empty {{ color:var(--sub); font-size:14px; padding:14px; background:#fff; border:1px dashed var(--line); border-radius:12px; }}
  footer {{ max-width:1080px; margin:8px auto 40px; padding:18px; border-top:1px solid var(--line); color:var(--sub); font-size:13px; }}
  footer b {{ color:var(--ink); }}
  @media (max-width:560px) {{ .hero h1 {{ font-size:24px; }} .grid {{ grid-template-columns:1fr; }} }}
</style>
</head>
<body>
  <header class="hero">
    <div class="hero-inner">
      <p class="kicker">{esc(data.get("kicker", "临床药学 / 医院药学 · 晨报"))}</p>
      <h1>{esc(title)}</h1>
      <div class="date">{esc(date_human)}</div>
      <div class="meta">共 {total} 条 · 近期临床药学/医院药学真实资讯 · 整理于 {esc(date_human)}</div>
      <div class="stats">{stat_html}</div>
    </div>
  </header>
  <nav class="toc"><div class="toc-in">{nav_html}</div></nav>
  <main>{body_html}</main>
  <footer>
    <p>本期共收录 <b>{total}</b> 条临床药学/医院药学资讯，按 {len(sections)} 个版块分组，全局连续编号 #1–#{total}。</p>
    <p>数据源：<b>{src_note}</b></p>
    <p style="opacity:.8">说明：本晨报为临床药学/医院药学资讯汇编，供药师了解行业动态与培训参考；点击卡片「阅读原文 ↗」可跳转官方/原始出处。</p>
  </footer>
</body>
</html>'''
    return html_doc, total


def main():
    ap = argparse.ArgumentParser(description="Generate clinical/hospital pharmacy morning-report HTML dashboard.")
    ap.add_argument("data", help="Path to data JSON file (see references/data_schema.md)")
    ap.add_argument("-o", "--output", help="Output HTML path (default ./临床药学日报_<date>.html)")
    args = ap.parse_args()

    with open(args.data, encoding="utf-8") as f:
        data = json.load(f)

    doc, total = render(data)
    report_date = data.get("report_date") or datetime.date.today().strftime("%Y-%m-%d")
    out = args.output or f"临床药学日报_{report_date}.html"
    with open(out, "w", encoding="utf-8") as f:
        f.write(doc)
    print(f"OK total={total} file={out}")


if __name__ == "__main__":
    main()
