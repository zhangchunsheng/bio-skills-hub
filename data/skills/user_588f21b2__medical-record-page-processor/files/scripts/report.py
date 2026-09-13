# -*- coding: utf-8 -*-
"""自包含 HTML 报告生成：KPI 卡片 + 交互式图表 + 事实卡 + 质控诊断。

产物是单个 HTML 文件，ECharts 已内联，双击即可离线打开、可打印成 PDF。
模板用顺序 replace 而非 str.format —— CSS/JS 里大量花括号，format 会踩坑。
"""

from __future__ import annotations

import json
import os

ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")

SEV_ORDER = ["致命", "严重", "提示"]
SEV_COLOR = {"致命": "#A32D2D", "严重": "#BA7517", "提示": "#5F5E5A"}

THEMES = {
    "light": {
        "bg": "#FFFFFF", "panel": "#F7F6F2", "text": "#2C2C2A", "muted": "#5F5E5A",
        "border": "#E3E1DA", "accent": "#185FA5",
        "palette": ["#378ADD", "#1D9E75", "#EF9F27", "#D4537E", "#7F77DD", "#639922",
                    "#D85A30", "#0F6E56", "#888780", "#185FA5"],
    },
    "dark": {
        "bg": "#1F1E1D", "panel": "#2C2C2A", "text": "#F1EFE8", "muted": "#B4B2A9",
        "border": "#444441", "accent": "#85B7EB",
        "palette": ["#85B7EB", "#5DCAA5", "#EF9F27", "#ED93B1", "#AFA9EC", "#97C459",
                    "#F0997B", "#1D9E75", "#B4B2A9", "#378ADD"],
    },
}


def render(payload: dict, theme: str = "light") -> str:
    t = THEMES.get(theme, THEMES["light"])
    html = _HTML
    repl = {
        "%%TITLE%%": _esc(payload["meta"].get("title", "病案首页数据分析报告")),
        "%%SUBTITLE%%": _esc(payload["meta"].get("subtitle", "")),
        "%%HEADER%%": _render_header(payload),
        "%%KPI%%": _render_kpi(payload.get("kpis", {})),
        "%%ANNOTATION%%": _render_annotation(payload),
        "%%CHARTS%%": _render_charts(payload.get("charts", [])),
        "%%QUALITY%%": _render_quality(payload.get("quality", {})),
        "%%MAPPING%%": _render_mapping(payload.get("mapping", {}), payload.get("meta", {})),
        "%%NOTES%%": _render_notes(payload.get("meta", {})),
        "%%FOOTER%%": _render_footer(),
        "%%ECHARTS%%": _read_assets("echarts.min.js"),
        "%%CHARTS_JS%%": _charts_script(payload.get("charts", []), t),
        "%%THEME_JSON%%": json.dumps(t, ensure_ascii=False),
    }
    for key, val in repl.items():
        html = html.replace(key, val)
    return html


def _read_assets(name: str) -> str:
    with open(os.path.join(ASSETS, name), "r", encoding="utf-8") as fh:
        return fh.read()


def _esc(text) -> str:
    return (str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


# ---------------------------------------------------------------------------
# 各区块渲染
# ---------------------------------------------------------------------------
def _render_header(p: dict) -> str:
    m = p["meta"]
    items = [
        ("数据来源", m.get("source", "—")),
        ("记录条数", f"{m.get('rows', 0):,}"),
        ("文件数", str(m.get("file_count", 1))),
        ("时间跨度", m.get("span", "—")),
        ("识别字段", f"{m.get('mapped_count', 0)} / {m.get('column_count', 0)}"),
        ("质量评分", str(p.get("quality", {}).get("score", "—"))),
    ]
    cells = "".join(
        f'<div class="hcell"><div class="hk">{_esc(k)}</div><div class="hv">{_esc(v)}</div></div>'
        for k, v in items)
    return f'<div class="hstrip">{cells}</div>'


def _render_kpi(kpis: dict) -> str:
    if not kpis:
        return ""
    cards = []
    for name, item in kpis.items():
        num, den = item.get("分子"), item.get("分母")
        detail = (f'<div class="kpi-frac">{_fmt_num(num)} ÷ {_fmt_num(den)}</div>'
                  if num is not None and den is not None else "")
        cards.append(
            f'<div class="kpi"><div class="kpi-n">{_esc(name)}</div>'
            f'<div class="kpi-v">{_fmt_num(item.get("值"))}'
            f'<span class="kpi-u">{_esc(item.get("单位", ""))}</span></div>'
            f'{detail}<div class="kpi-c">{_esc(item.get("口径", ""))}</div></div>')
    return f'<h2>核心指标</h2><div class="kpis">{"".join(cards)}</div>'


def _render_annotation(p: dict) -> str:
    text = p.get("annotation")
    if not text:
        return ""
    body = "".join(f"<p>{_esc(x)}</p>" for x in str(text).split("\n") if x.strip())
    return f'<div class="annot"><h2>解读</h2>{body}</div>'


def _render_charts(charts: list[dict]) -> str:
    if not charts:
        return '<h2>图表</h2><p class="muted">未生成图表：数据中没有可用于绘图的字段。</p>'
    blocks = []
    for ch in charts:
        facts = "".join(f"<li>{_esc(f)}</li>" for f in ch.get("facts", []))
        blocks.append(f"""
<div class="card">
  <div class="card-h"><h3>{_esc(ch['title'])}</h3>
  <div class="sub">{_esc(ch.get('subtitle', ''))}</div></div>
  <div class="chart" id="{_esc(ch['id'])}"></div>
  <div class="facts"><div class="facts-t">事实（可溯源，写报告引用此处的数字）</div>
  <ul>{facts}</ul></div>
</div>""")
    return f'<h2>图表</h2>{"".join(blocks)}'


def _render_quality(q: dict) -> str:
    issues = q.get("issues", [])
    if not issues:
        return '<h2>数据质量诊断</h2><p class="ok">未发现质控问题。</p>'
    s = q.get("summary", {})
    head = ('<h2>数据质量诊断</h2><div class="qsum">'
            + "".join(f'<span class="badge" style="border-color:{SEV_COLOR[k]}">'
                      f'{k}问题 {s.get(k, 0)} 条</span>' for k in SEV_ORDER)
            + f'<span class="badge">质量评分 {q.get("score", "—")} / 100</span></div>')
    rows = []
    for sev in SEV_ORDER:
        group = [i for i in issues if i["severity"] == sev]
        if not group:
            continue
        rows.append(f'<h3 class="sev" style="color:{SEV_COLOR[sev]}">{sev}问题（{len(group)} 类）</h3>')
        for i in group:
            samples = ""
            if i.get("samples"):
                lines = []
                for s_ in i["samples"]:
                    detail = "，".join(f"{k}={v}" for k, v in (s_.get("明细") or {}).items())
                    lines.append(f'<li>{_esc(s_["记录标识"])}'
                                 f'{"：" + _esc(detail) if detail else ""}</li>')
                samples = f'<ul class="samples">{"".join(lines)}</ul>'
            rows.append(f"""
<div class="issue">
  <div class="issue-h"><span class="rule">{_esc(i['rule'])}</span>
    <span class="iname">{_esc(i['name'])}</span>
    <span class="icnt">{i['count']} 条 · {i['rate'] * 100:.2f}%</span></div>
  <div class="advice">{_esc(i.get('advice', ''))}</div>{samples}
</div>""")
    return head + "".join(rows)


def _render_mapping(mapping: dict, meta: dict) -> str:
    pairs = mapping.get("pairs", [])
    unmapped = meta.get("unmapped", [])
    rows = "".join(
        f'<tr><td>{_esc(p["原始列名"])}</td><td>{_esc(p["标准字段"])}</td>'
        f'<td><span class="conf c-{p["置信度"]}">{p["置信度"]}</span></td></tr>'
        for p in pairs)
    un = "".join(f"<li>{_esc(x)}</li>" for x in unmapped) or "<li>无</li>"
    return (f'<h2>字段识别结果</h2>'
            f'<div class="two-col"><div><table class="tbl"><thead><tr><th>原始列名</th>'
            f'<th>标准字段</th><th>置信度</th></tr></thead><tbody>{rows}</tbody></table></div>'
            f'<div><div class="note-t">未识别列（{len(unmapped)}）——不进图表，仅提示核对</div>'
            f'<ul class="unmapped">{un}</ul></div></div>')


def _render_notes(meta: dict) -> str:
    blocks = []
    privacy = meta.get("privacy_cols", [])
    if privacy:
        items = "".join(f"<li>{_esc(x)}</li>" for x in privacy)
        blocks.append(f'<div class="alert"><div class="note-t">隐私字段已剔除（{len(privacy)}）'
                      f'——以下字段未参与任何计算，也未写入任何输出文件</div>'
                      f'<ul class="unmapped">{items}</ul></div>')
    if meta.get("header_rows"):
        blocks.append('<div class="note-t">表头定位：' + "；".join(
            f"{_esc(k)} 第 {v + 1} 行" for k, v in meta["header_rows"].items()) + "</div>")
    if meta.get("warnings"):
        items = "".join(f"<li>{_esc(x)}</li>" for x in meta["warnings"])
        blocks.append(f'<div class="note-t">运行提示</div><ul class="unmapped">{items}</ul>')
    return f'<h2>数据说明</h2>{"".join(blocks)}' if blocks else ""


def _render_footer() -> str:
    return """
<div class="disc">
  <div class="disc-t">免责与合规声明</div>
  <p>1. 本报告由「病案首页数据处理器」在使用者本机离线生成，原始数据与中间结果均未离开本机。</p>
  <p>2. 报告中所有指标为病案首页填报数据的统计描述，用于数据治理、质控与科研探索，
  不作为临床诊疗依据，也不直接等同于院内上报口径（上报口径以国家/省市平台规范为准）。</p>
  <p>3. 病案首页属健康医疗数据，使用须遵守《个人信息保护法》《数据安全法》及本院数据管理制度。
  对外提供、论文发表或跨机构共享前，请完成去标识化与伦理审查（回顾性研究多可申请知情同意豁免）。</p>
</div>"""


def _fmt_num(v) -> str:
    if v is None:
        return "—"
    if isinstance(v, float) and v == int(v) and abs(v) < 1e15:
        v = int(v)
    if isinstance(v, int):
        return f"{v:,}"
    try:
        return f"{float(v):,.2f}"
    except (TypeError, ValueError):
        return _esc(v)


# ---------------------------------------------------------------------------
# ECharts 初始化脚本
# ---------------------------------------------------------------------------
def _charts_script(charts: list[dict], t: dict) -> str:
    if not charts:
        return ""
    blocks = []
    for ch in charts:
        opt = _option(ch, t)
        blocks.append(
            f'<script>(function(){{var el=document.getElementById("{ch["id"]}");'
            f'if(!el)return;var c=echarts.init(el,null,{{renderer:"canvas"}});'
            f'c.setOption({json.dumps(opt, ensure_ascii=False)});'
            f'window.addEventListener("resize",function(){{c.resize();}});}})();</script>')
    return "\n".join(blocks)


def _option(ch: dict, t: dict) -> dict:
    base = {
        "color": t["palette"],
        "backgroundColor": "transparent",
        "textStyle": {"fontFamily": "Microsoft YaHei, PingFang SC, sans-serif",
                      "color": t["text"]},
        "grid": {"left": 70, "right": 60, "top": 46, "bottom": 96, "containLabel": True},
        "tooltip": {"trigger": "axis", "backgroundColor": t["panel"],
                    "borderColor": t["border"], "textStyle": {"color": t["text"]}},
        "legend": {"top": 6, "textStyle": {"color": t["muted"]}},
    }
    if ch["type"] == "pie":
        base["tooltip"] = {"trigger": "item", "backgroundColor": t["panel"],
                           "borderColor": t["border"], "textStyle": {"color": t["text"]}}
        base["series"] = [{
            "type": "pie", "radius": ["42%", "70%"], "center": ["50%", "52%"],
            "avoidLabelOverlap": True,
            "itemStyle": {"borderColor": t["bg"], "borderWidth": 2},
            "label": {"color": t["text"], "formatter": "{b}\n{d}%"},
            "data": ch.get("data", []),
        }]
        base["legend"] = {"bottom": 0, "type": "scroll", "textStyle": {"color": t["muted"]}}
        base.pop("grid", None)
        return base

    units = []
    for s in ch["series"]:
        u = s.get("unit", "")
        if u and u not in units:
            units.append(u)
    dual = len(units) > 1
    base["xAxis"] = {
        "type": "category", "data": ch["categories"],
        "name": ch.get("x_name", ""), "nameLocation": "middle", "nameGap": 66,
        "axisLabel": {"color": t["muted"], "rotate": _rotate(ch["categories"]),
                      "interval": 0, "fontSize": 11},
        "axisLine": {"lineStyle": {"color": t["border"]}},
    }
    base["yAxis"] = [{
        "type": "value", "name": units[0] if units else "",
        "axisLabel": {"color": t["muted"]},
        "splitLine": {"lineStyle": {"color": t["border"]}},
        "nameTextStyle": {"color": t["muted"]},
    }]
    if dual:
        base["yAxis"].append({
            "type": "value", "name": units[1], "splitLine": {"show": False},
            "axisLabel": {"color": t["muted"]}, "nameTextStyle": {"color": t["muted"]},
        })
    series = []
    for s in ch["series"]:
        yidx = 1 if (dual and units[0] and s.get("unit") == units[1]) else 0
        series.append({
            "name": s["name"], "type": ch["type"], "data": s["data"], "yAxisIndex": yidx,
            "smooth": ch["type"] == "line", "symbolSize": 7, "barMaxWidth": 34,
            "emphasis": {"focus": "series"},
        })
    base["series"] = series
    return base


def _rotate(cats: list) -> int:
    longest = max((len(str(c)) for c in cats), default=0)
    return 32 if (longest > 10 or len(cats) > 10) else 0


_HTML = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%%TITLE%%</title>
<style>
* { box-sizing: border-box; }
body { margin:0; padding:32px 28px 64px; background:#FFFFFF; color:#2C2C2A;
  font-family:"Microsoft YaHei","PingFang SC","Hiragino Sans GB",sans-serif;
  font-size:14px; line-height:1.65; -webkit-font-smoothing:antialiased; }
.wrap { max-width:1100px; margin:0 auto; }
h1 { font-size:22px; font-weight:500; margin:0 0 6px; }
h2 { font-size:17px; font-weight:500; margin:36px 0 14px; padding-bottom:8px;
  border-bottom:1px solid #E3E1DA; }
h3 { font-size:15px; font-weight:500; margin:0 0 4px; }
.muted { color:#5F5E5A; }
.sub { font-size:12px; color:#5F5E5A; margin-bottom:12px; line-height:1.5; }
.hstrip { display:grid; grid-template-columns:repeat(auto-fit,minmax(140px,1fr)); gap:10px;
  background:#F7F6F2; border:1px solid #E3E1DA; border-radius:12px; padding:16px; margin:18px 0 8px; }
.hk { font-size:12px; color:#5F5E5A; }
.hv { font-size:14px; font-weight:500; margin-top:2px; word-break:break-all; }
.kpis { display:grid; grid-template-columns:repeat(auto-fit,minmax(210px,1fr)); gap:12px; }
.kpi { border:1px solid #E3E1DA; border-radius:12px; padding:14px 16px; background:#FFFFFF; }
.kpi-n { font-size:12px; color:#5F5E5A; }
.kpi-v { font-size:24px; font-weight:500; margin:4px 0 2px; color:#185FA5; }
.kpi-u { font-size:12px; font-weight:400; color:#5F5E5A; margin-left:4px; }
.kpi-frac { font-size:11px; color:#888780; }
.kpi-c { font-size:11px; color:#888780; margin-top:6px; line-height:1.5; }
.card { border:1px solid #E3E1DA; border-radius:12px; padding:18px 20px 14px; margin-bottom:18px; }
.chart { width:100%; height:340px; }
.facts { background:#F7F6F2; border-left:3px solid #185FA5; border-radius:0 8px 8px 0;
  padding:10px 14px; margin-top:10px; }
.facts-t { font-size:12px; color:#5F5E5A; margin-bottom:4px; }
.facts ul { margin:0; padding-left:18px; font-size:13px; }
.facts li { margin:2px 0; }
.annot { background:#F1F7FF; border:1px solid #B5D4F4; border-radius:12px; padding:14px 20px;
  margin:18px 0; }
.annot h2 { margin:0 0 8px; border:none; padding:0; font-size:15px; color:#0C447C; }
.annot p { margin:6px 0; }
.qsum { display:flex; gap:8px; flex-wrap:wrap; margin-bottom:12px; }
.badge { border:1px solid #888780; border-radius:999px; padding:3px 12px; font-size:12px;
  color:#444441; }
.sev { margin:20px 0 8px; font-size:14px; font-weight:500; }
.issue { border:1px solid #E3E1DA; border-radius:10px; padding:12px 14px; margin-bottom:10px; }
.issue-h { display:flex; flex-wrap:wrap; gap:10px; align-items:baseline; }
.rule { font-family:Consolas,Monaco,monospace; font-size:12px; color:#888780; }
.iname { font-weight:500; }
.icnt { font-size:12px; color:#993C1D; margin-left:auto; }
.advice { font-size:12px; color:#5F5E5A; margin-top:6px; }
.samples { margin:6px 0 0; padding-left:18px; font-size:12px; color:#5F5E5A; }
.two-col { display:grid; grid-template-columns:1.2fr 1fr; gap:20px; }
.tbl { border-collapse:collapse; width:100%; font-size:12px; }
.tbl th, .tbl td { border-bottom:1px solid #E3E1DA; padding:6px 8px; text-align:left; }
.tbl th { color:#5F5E5A; font-weight:500; }
.conf { font-size:11px; padding:1px 6px; border-radius:4px; }
.c-high { background:#E1F5EE; color:#0F6E56; }
.c-medium { background:#FAEEDA; color:#854F0B; }
.c-low { background:#FCEBEB; color:#A32D2D; }
.note-t { font-size:12px; color:#5F5E5A; margin:12px 0 6px; }
.unmapped { margin:0; padding-left:18px; font-size:12px; color:#5F5E5A; max-height:260px;
  overflow:auto; }
.alert { background:#FDF6EC; border:1px solid #FAC775; border-radius:10px; padding:10px 14px;
  margin-bottom:12px; }
.ok { color:#0F6E56; }
.disc { margin-top:40px; border-top:1px solid #E3E1DA; padding-top:14px; font-size:12px;
  color:#5F5E5A; line-height:1.7; }
.disc-t { font-weight:500; color:#444441; margin-bottom:6px; }
@media (max-width:820px) { .two-col { grid-template-columns:1fr; } }
@media print { .card, .kpi, .issue { break-inside:avoid; } body { padding:0; } }
</style>
</head>
<body>
<div class="wrap">
<h1>%%TITLE%%</h1>
<div class="sub">%%SUBTITLE%%</div>
%%HEADER%%
%%ANNOTATION%%
%%KPI%%
%%CHARTS%%
%%QUALITY%%
%%MAPPING%%
%%NOTES%%
%%FOOTER%%
</div>
<script>%%ECHARTS%%</script>
<script>window.__THEME__ = %%THEME_JSON%%;</script>
%%CHARTS_JS%%
</body>
</html>
"""
