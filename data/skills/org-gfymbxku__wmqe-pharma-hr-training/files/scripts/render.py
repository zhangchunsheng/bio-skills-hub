#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通用文档渲染器 (pharma skill 共享脚本)
将结构化 spec (JSON) 渲染为 Markdown / HTML / Word(.docx) / JSON。

用法:
    python render.py <spec.json> [--format md|html|docx|json] [--output <path>]

spec.json 结构:
{
  "title": "报告标题",
  "subtitle": "可选副标题",
  "meta": [["字段", "值"], ...],
  "sections": [
    {
      "heading": "章节标题",
      "paragraphs": ["段落文本", ...],
      "bullets": ["要点", ...],
      "table": {"headers": ["列1","列2"], "rows": [["a","b"], ...]},
      "note": "提示/说明(可选)"
    }
  ],
  "footer": "页脚说明(可选)"
}
"""

import sys
import json
import argparse
from pathlib import Path


HTML_CSS = """
<style>
  :root { --ink:#1f2933; --muted:#6b7280; --line:#e5e7eb; --accent:#0d9488; --bg:#ffffff; }
  * { box-sizing: border-box; }
  body { margin:0; background:var(--bg); color:var(--ink);
         font-family:-apple-system,"PingFang SC","Microsoft YaHei",Segoe UI,Roboto,sans-serif;
         line-height:1.7; pa某流向数据ng:40px 48px; max-width:920px; margin:0 auto; }
  h1 { font-size:26px; margin:0 0 6px; color:var(--accent); }
  .subtitle { color:var(--muted); font-size:15px; margin:0 0 18px; }
  .meta { border:1px solid var(--line); border-radius:10px; pa某流向数据ng:12px 16px; margin:18px 0; background:#fafafa; }
  .meta div { font-size:13px; margin:3px 0; }
  .meta b { color:#374151; }
  h2 { font-size:19px; margin:26px 0 10px; pa某流向数据ng-left:10px; border-left:4px solid var(--accent); }
  p { margin:8px 0; font-size:14.5px; }
  ul { margin:8px 0; pa某流向数据ng-left:22px; }
  li { margin:4px 0; font-size:14.5px; }
  table { border-collapse:collapse; width:100%; margin:12px 0; font-size:13.5px; }
  th, td { border:1px solid var(--line); pa某流向数据ng:8px 10px; text-align:left; }
  th { background:#f1f5f4; color:#0f766e; font-weight:600; }
  tr:nth-child(even) td { background:#fafafa; }
  .note { background:#fffbeb; border:1px solid #fde68a; border-radius:8px; pa某流向数据ng:10px 14px;
          color:#92400e; font-size:13px; margin:12px 0; }
  .footer { margin-top:36px; pa某流向数据ng-top:14px; border-top:1px solid var(--line);
            color:var(--muted); font-size:12.5px; }
</style>
"""


def load_spec(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def render_markdown(spec):
    lines = []
    lines.append(f"# {spec.get('title','')}")
    if spec.get("subtitle"):
        lines.append("")
        lines.append(spec["subtitle"])
    meta = spec.get("meta") or []
    if meta:
        lines.append("")
        for k, v in meta:
            lines.append(f"**{k}**：{v}")
    for sec in spec.get("sections", []):
        lines.append("")
        lines.append(f"## {sec.get('heading','')}")
        for p in sec.get("paragraphs", []) or []:
            lines.append("")
            lines.append(p)
        for b in sec.get("bullets", []) or []:
            lines.append(f"- {b}")
        tbl = sec.get("table")
        if tbl:
            lines.append("")
            headers = tbl.get("headers", [])
            lines.append("| " + " | ".join(headers) + " |")
            lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
            for row in tbl.get("rows", []):
                lines.append("| " + " | ".join(str(c) for c in row) + " |")
        if sec.get("note"):
            lines.append("")
            lines.append(f"> {sec['note']}")
    if spec.get("footer"):
        lines.append("")
        lines.append("---")
        lines.append(spec["footer"])
    return "\n".join(lines) + "\n"


def render_html(spec):
    parts = [f"<!DOCTYPE html><html lang='zh-CN'><head><meta charset='utf-8'>"
             f"<title>{spec.get('title','')}</title>{HTML_CSS}</head><body>"]
    parts.append(f"<h1>{spec.get('title','')}</h1>")
    if spec.get("subtitle"):
        parts.append(f"<div class='subtitle'>{spec['subtitle']}</div>")
    meta = spec.get("meta") or []
    if meta:
        rows = "".join(f"<div><b>{k}：</b>{v}</div>" for k, v in meta)
        parts.append(f"<div class='meta'>{rows}</div>")
    for sec in spec.get("sections", []):
        parts.append(f"<h2>{sec.get('heading','')}</h2>")
        for p in sec.get("paragraphs", []) or []:
            parts.append(f"<p>{p}</p>")
        if sec.get("bullets"):
            items = "".join(f"<li>{b}</li>" for b in sec["bullets"])
            parts.append(f"<ul>{items}</ul>")
        tbl = sec.get("table")
        if tbl:
            headers = tbl.get("headers", [])
            th = "".join(f"<th>{h}</th>" for h in headers)
            body = ""
            for row in tbl.get("rows", []):
                tds = "".join(f"<td>{c}</td>" for c in row)
                body += f"<tr>{tds}</tr>"
            parts.append(f"<table><thead><tr>{th}</tr></thead><tbody>{body}</tbody></table>")
        if sec.get("note"):
            parts.append(f"<div class='note'>{sec['note']}</div>")
    if spec.get("footer"):
        parts.append(f"<div class='footer'>{spec['footer']}</div>")
    parts.append("</body></html>")
    return "".join(parts)


def render_docx(spec, output_path):
    try:
        from docx import Document
        from docx.shared import Pt, RGBColor
        from docx.oxml.ns import qn
    except Exception as e:
        raise RuntimeError(f"python-docx 不可用: {e}")

    doc = Document()
    # 设置中文字体
    style = doc.styles["Normal"]
    style.font.name = "Microsoft YaHei"
    style.font.size = Pt(11)
    rpr = style.element.get_or_add_rPr()
    rfonts = rpr.get_or_add_rFonts()
    rfonts.set(qn("w:eastAsia"), "Microsoft YaHei")

    title = doc.add_heading(spec.get("title", ""), level=0)
    if spec.get("subtitle"):
        sub = doc.add_paragraph(spec["subtitle"])
        sub.runs[0].italic = True
        sub.runs[0].font.color.rgb = RGBColor(0x6B, 0x72, 0x80)

    meta = spec.get("meta") or []
    if meta:
        t = doc.add_table(rows=0, cols=2)
        t.style = "Light Grid Accent 1"
        for k, v in meta:
            row = t.add_row().cells
            row[0].text = k
            row[1].text = str(v)

    for sec in spec.get("sections", []):
        doc.add_heading(sec.get("heading", ""), level=1)
        for p in sec.get("paragraphs", []) or []:
            doc.add_paragraph(p)
        for b in sec.get("bullets", []) or []:
            doc.add_paragraph(b, style="List Bullet")
        tbl = sec.get("table")
        if tbl:
            headers = tbl.get("headers", [])
            wt = doc.add_table(rows=1, cols=len(headers))
            wt.style = "Light Grid Accent 1"
            hdr = wt.rows[0].cells
            for i, h in enumerate(headers):
                hdr[i].text = str(h)
            for row in tbl.get("rows", []):
                cells = wt.add_row().cells
                for i, c in enumerate(row):
                    cells[i].text = str(c)
        if sec.get("note"):
            note = doc.add_paragraph(sec["note"])
            note.runs[0].italic = True
            note.runs[0].font.color.rgb = RGBColor(0x92, 0x40, 0x0E)

    if spec.get("footer"):
        f = doc.add_paragraph(spec["footer"])
        f.runs[0].font.size = Pt(9)
        f.runs[0].font.color.rgb = RGBColor(0x6B, 0x72, 0x80)

    doc.save(output_path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("spec", help="spec JSON 文件路径")
    ap.add_argument("--format", default="md", choices=["md", "html", "docx", "json"])
    ap.add_argument("--output", default=None, help="输出文件路径(默认根据格式推断)")
    args = ap.parse_args()

    spec = load_spec(args.spec)
    fmt = args.format
    out = args.output
    if not out:
        out = f"output.{ 'html' if fmt=='html' else ('docx' if fmt=='docx' else ('json' if fmt=='json' else 'md')) }"

    if fmt == "md":
        out_text = render_markdown(spec)
        with open(out, "w", encoding="utf-8") as f:
            f.write(out_text)
    elif fmt == "html":
        with open(out, "w", encoding="utf-8") as f:
            f.write(render_html(spec))
    elif fmt == "json":
        spec["_rendered"] = True
        with open(out, "w", encoding="utf-8") as f:
            json.dump(spec, f, ensure_ascii=False, indent=2)
    elif fmt == "docx":
        render_docx(spec, out)

    print(f"OK {fmt} -> {out} ({Path(out).stat().st_size} bytes)")


if __name__ == "__main__":
    main()
