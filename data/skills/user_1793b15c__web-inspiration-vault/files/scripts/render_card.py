#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
render_card.py — 把 dna.json 套进指定「风格模板」，产出一张灵感卡 HTML
=====================================================================
用法：
    python render_card.py dna.json -o card.html [--style minimalist] [--force]

设计要点：
- 「风格」与「骨架」解耦。风格模板决定视觉（本文件 + styles/<id>/card.html.j2），
  骨架决定信息结构（配色卡 / 字体 / 节奏 / 评分 / 内容）。
  以后加「月度复盘一页纸」骨架时，只需再加一个 .j2，不必动风格模板。
- 页面外壳恒为浅底深字（可读性红线）；被采集页的真实底色只作色块陈列。
- 若目标风格还没有成品模板，会用现有模板渲染，但**如实标注**"该风格模板待建"，
  绝不含糊其辞地假装已支持。
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import re
import sys

from jinja2 import Environment, FileSystemLoader, select_autoescape

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL_ROOT = os.path.dirname(HERE)
STYLES_DIR = os.path.join(SKILL_ROOT, "styles")

STYLE_NAMES = {
    "minimalist": "极简风",
    "magazine": "杂志风",
    "tech": "科技风",
    "retro": "复古风",
}
STYLE_ORDER = ["minimalist", "magazine", "tech", "retro"]

# 模板文件扩展名统一走白名单（.j2/.css 不在 SkillHub 允许的扩展名里，
# 而被代码 open/include 的文本文件又不能靠打包工具自动转 .md 否则功能即断）。
# 因此统一用 .txt 后缀，并在加载处集中定义，避免散落的字符串替换。
TPL_CARD = "card.html.txt"
TPL_BODY = "body.html.txt"
TPL_CSS = "card.css.txt"


def card_css_path(tpl_card_path):
    return tpl_card_path.replace(TPL_CARD, TPL_CSS)


def available_styles():
    """返回 {style_id: 模板路径}，只收录真正带 card.html.j2 的风格。"""
    out = {}
    if not os.path.isdir(STYLES_DIR):
        return out
    for sid in sorted(os.listdir(STYLES_DIR)):
        tpl = os.path.join(STYLES_DIR, sid, TPL_CARD)
        if os.path.isfile(tpl):
            out[sid] = tpl
    return out


def _trim_stack(stack, keep=3):
    """字体栈只留前几族，避免卡片上出现一长串 fallback 噪声。"""
    if not stack:
        return "—"
    parts = [p.strip().strip('"') for p in str(stack).split(",") if p.strip()]
    head = ", ".join(parts[:keep])
    if len(parts) > keep:
        head += ", …"
    return head or "—"


def _role_label(hexv, palette):
    """给每个色块标注它在页面里担任的角色。"""
    order = ["background", "surface", "surface_alt", "text", "text_muted",
             "primary", "accent", "border"]
    zh = {
        "background": "背景", "surface": "卡片面", "surface_alt": "次级面",
        "text": "正文", "text_muted": "弱化文字", "primary": "主强调",
        "accent": "次强调", "border": "描边",
    }
    for k in order:
        if palette.get(k) and palette[k].lower() == hexv.lower():
            return zh[k]
    return "辅助色"


def build_context(dna, style_id=None, style_tpl_id=None, extracted_at=None, note_extra=None):
    pal = dna.get("palette", {})
    typ = dna.get("typography", {})
    rhy = dna.get("rhythm", {})
    con = dna.get("content", {})
    meta = dna.get("meta", {})
    cls = dna.get("classification", {})

    true_style = (style_id or cls.get("style") or "minimalist")
    tpl_style = (style_tpl_id or true_style)

    seen = []
    for k in ("background", "surface", "text", "text_muted", "primary", "accent", "border"):
        v = pal.get(k)
        if v and v.lower() not in [s.lower() for s in seen]:
            seen.append(v)
    swatches = [{"hex": h, "role": _role_label(h, pal), "usage": ""} for h in seen[:7]]

    scores = []
    raw_scores = cls.get("scores", {})
    for sid in STYLE_ORDER:
        pct = int(round(float(raw_scores.get(sid, 0)) * 100))
        scores.append({
            "id": sid, "name": STYLE_NAMES[sid], "pct": pct,
            "win": sid == true_style,
        })
    scores.sort(key=lambda s: -s["pct"])

    notes = list(cls.get("notes") or [])
    if tpl_style != true_style:
        notes.insert(0, f"页面归属「{STYLE_NAMES.get(true_style, true_style)}」，"
                        f"但该风格模板尚未建成 —— 本卡暂用「{STYLE_NAMES[tpl_style]}」模板呈现，"
                        f"配色与字体参数仍是原页真实值。")
    if note_extra:
        notes.append(note_extra)

    outline = [s["heading"] for s in (con.get("sections") or []) if s.get("heading")]

    src_url = meta.get("base_url") or dna.get("meta", {}).get("source") or ""
    if src_url.startswith("file:///"):
        src_url = ""
    host = ""
    m = re.match(r"^https?://([^/]+)", src_url or "")
    if m:
        host = m.group(1)

    return {
        "title": con.get("title") or "(无标题)",
        "dek": con.get("dek") or "",
        "site": con.get("site") or host,
        "source_host": host or "本地文件",
        "author": con.get("author") or "",
        "date": con.get("date") or "",
        "url": src_url,
        "extracted_at": extracted_at or _dt.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "extracted_from": meta.get("extracted_from", ""),
        "style_name": STYLE_NAMES.get(true_style, true_style),
        "style_id": true_style,
        "template_style": tpl_style,
        "confidence": f"{float(cls.get('confidence', 0)):.2f}",
        "primary": pal.get("primary") or pal.get("text") or "#333",
        "text_color": pal.get("text") or "#1a1a1a",
        "swatches": swatches,
        "contrast": pal.get("contrast_text_bg", "—"),
        "palette_size": pal.get("palette_size", 0),
        "vivid_count": pal.get("vivid_count", 0),
        "heading_stack": _trim_stack(typ.get("heading_stack")),
        "body_stack": _trim_stack(typ.get("body_stack")),
        "heading_char": typ.get("heading_char", "—"),
        "body_char": typ.get("body_char", "—"),
        "weight_count": typ.get("weight_count", 0),
        "body_size": typ.get("body_size", 16),
        "max_size": typ.get("max_size", 32),
        "type_ratio": typ.get("type_ratio", 1),
        "base_unit": rhy.get("base_unit", 8),
        "radius_style": rhy.get("radius_style", "sharp"),
        "max_radius": rhy.get("max_radius", 0),
        "container_width": rhy.get("container_width", 1200),
        "density": rhy.get("density", "normal"),
        "avg_spacing": rhy.get("avg_spacing", 0),
        "letter_spacing": typ.get("letter_spacing", 0),
        "scores": scores,
        "evidence": cls.get("evidence", ""),
        "signal_strength": cls.get("signal_strength", ""),
        "template_ready": bool(available_styles().get(true_style)),
        "notes": notes,
        "lead": con.get("lead") or "",
        "outline": outline[:6],
        "quotes": (con.get("quotes") or [])[:2],
        "numbers": (con.get("key_numbers") or [])[:8],
        "paragraph_count": con.get("paragraph_count", 0),
        "word_count": con.get("word_count", 0),
        # 新增：卡片网格页（内容枢纽/索引页）与体检结果
        "page_type": con.get("page_type", "unknown"),
        "cards": (con.get("cards") or [])[:9],
        "card_count": len(con.get("cards") or []),
        "prose_width": rhy.get("prose_width"),
        "heading_line_height": typ.get("heading_line_height"),
        "is_custom_heading_font": typ.get("is_custom_heading_font", False),
        "audit": dna.get("audit", {}),
        "audit_checks": (dna.get("audit") or {}).get("checks", []),
        "brand_palette": (pal.get("brand_palette") or [])[:4],
    }


def render_card(dna, out_path, style_id=None, force=False, encoding="utf-8"):
    styles = available_styles()
    cls_style = (dna.get("classification") or {}).get("style", "minimalist")

    if style_id and style_id not in styles:
        raise SystemExit(
            f"[!] 风格 '{style_id}' 尚无成品模板。现有：{sorted(styles) or '无'}\n"
            f"    可先用 --style {'/'.join(sorted(styles))} 之一，或去 styles/{style_id}/ 建模板。"
        )

    if style_id:
        tpl_style = style_id
    elif cls_style in styles:
        tpl_style = cls_style
    else:
        tpl_style = sorted(styles)[0] if styles else None
        if tpl_style is None:
            raise SystemExit(f"[!] styles/ 下没有任何 {TPL_CARD}，无法渲染。")

    tpl_path = styles[tpl_style]
    tpl_dir = os.path.dirname(tpl_path)
    env = Environment(
        loader=FileSystemLoader(tpl_dir),
        autoescape=True,  # 全部模板均为 HTML 片段，统一开启更安全（.txt 后缀不会被扩展名规则识别）
        trim_blocks=True, lstrip_blocks=True,
    )
    template = env.get_template(TPL_CARD)
    ctx = build_context(dna, style_id=cls_style, style_tpl_id=tpl_style)

    html = template.render(c=ctx)
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    with open(out_path, "w", encoding=encoding) as f:
        f.write(html)
    return {"out": out_path, "true_style": cls_style, "template_style": tpl_style,
            "context": ctx}


def main():
    ap = argparse.ArgumentParser(description="把 dna.json 渲染成风格化灵感卡")
    ap.add_argument("dna", help="dna.json 路径")
    ap.add_argument("-o", "--out", required=True, help="输出 HTML 路径")
    ap.add_argument("--style", default=None,
                    help=f"强制指定风格模板，可选 {STYLE_ORDER}")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    with open(args.dna, "r", encoding="utf-8") as f:
        dna = json.load(f)

    res = render_card(dna, args.out, style_id=args.style)
    if not args.quiet:
        print(f"已渲染 : {res['out']}")
        print(f"页面风格: {res['true_style']}  ->  使用模板: {res['template_style']}")
        print(f"标题    : {res['context']['title']}")
    return res


if __name__ == "__main__":
    main()
