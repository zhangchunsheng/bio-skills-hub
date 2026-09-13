#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_extract_dna.py — 视觉 DNA 提取引擎的回归测试
=================================================
把踩过的坑固化成断言，避免以后改代码时重犯：

1. `sans-serif` 不能被判成衬线体（否则杂志风分数被带偏）
2. `var(--color-pink-500)` 不能把 "pink" 当颜色（否则主色变粉红）
3. 有 data:image 的现代站点不能被误判成 SingleFile（否则整站 CSS 被跳过）
4. 暗色主题的 @media 块必须被剔除（否则暗色配色污染亮色配色）
5. oklch() 必须能解析（Tailwind v4 / shadcn 全靠它）
6. 列表型页面（正文在 <li>）必须能抽到内容
7. 老式 HTML 标签要能被识别为复古信号

运行：python -m pytest tests/ -q   或   python tests/test_extract_dna.py
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))

import extract_dna as E  # noqa: E402


def test_sans_serif_not_serif():
    assert E.classify_stack("system-ui, sans-serif") == "sans"
    assert E.classify_stack("-apple-system, BlinkMacSystemFont, Segoe UI, sans-serif") == "sans"
    assert E.classify_stack("Georgia, 'Times New Roman', serif") == "serif"
    assert E.classify_stack("ui-monospace, Menlo, monospace") == "mono"


def test_hex_and_func_colors():
    assert E.parse_color("#fff") == (255, 255, 255, 1.0)
    assert E.parse_color("#000000") == (0, 0, 0, 1.0)
    assert E.parse_color("rgb(255,0,0)") == (255, 0, 0, 1.0)
    assert E.parse_color("rgba(0,0,0,0.5)")[3] == 0.5
    assert E.parse_color("rebeccapurple") == (102, 51, 153, 1.0)
    assert E.parse_color("transparent") is None
    assert E.parse_color("not-a-color") is None


def test_oklch_parses_to_sane_srgb():
    rgb = E.parse_color("oklch(0.7 0.15 250)")
    assert rgb is not None and len(rgb) == 4
    r, g, b, _ = rgb
    assert all(0 <= v <= 255 for v in (r, g, b))
    assert b > r, "色相 250° 应该是偏蓝的"
    rgb0 = E.parse_color("oklch(0 0 0)")
    assert rgb0[:3] == (0, 0, 0)
    rgb1 = E.parse_color("oklch(1 0 0)")
    assert rgb1[:3] == (255, 255, 255)


def test_var_names_do_not_leak_colors():
    """曾把 var(--color-pink-500) 里的 pink 解析成粉红，污染整张配色卡。"""
    toks = E.iter_color_tokens("var(--color-pink-500)")
    assert toks == [], f"变量名不该产出颜色 token，实际: {toks}"
    toks2 = E.iter_color_tokens("1px solid var(--color-red-300)")
    assert toks2 == []
    # 但真正的颜色名要保留
    assert "pink" in E.iter_color_tokens("pink")
    assert "#ff0000" in E.iter_color_tokens("1px solid #ff0000")


def test_singlefile_detection_is_strict():
    modern = '<html><head></head><body>' + "data:image/png;base64,AAAA" * 20 + "</body></html>"
    assert not E.is_singlefile(modern), "内联图片多的现代站点不该被判成 SingleFile"
    sf = '<html><!-- saved from url=(0031)https://example.com --><body>data:font/woff2;base64,AA</body></html>'
    assert E.is_singlefile(sf)


def test_dark_media_stripped():
    css = """
    :root { --bg: #ffffff; --fg: #111111; }
    .card { background: #fff; color: #111; }
    @media (prefers-color-scheme: dark) {
      :root { --bg: #0b0b0b; --fg: #eeeeee; }
      .card { background: #101010; color: #eee; }
    }
    """
    out = E.strip_dark_media(css)
    assert "#0b0b0b" not in out and "#101010" not in out
    assert "#ffffff" in out


def test_resolve_vars():
    vars_ = {"--brand": "#ff5500", "--deep": "var(--brand)"}
    assert E.resolve_vars("1px solid var(--brand)", vars_) == "1px solid #ff5500"
    assert "#ff5500" in E.resolve_vars("var(--deep)", vars_)
    assert "fallback" in E.resolve_vars("var(--missing, fallback)", vars_)


def test_merge_similar_colors():
    entries = [
        {"hex": "#ffffff", "score": 10, "hits": 3, "roles": ["base"]},
        {"hex": "#fefefe", "score": 2, "hits": 1, "roles": ["body"]},
        {"hex": "#ff0000", "score": 5, "hits": 2, "roles": ["action"]},
    ]
    merged = E.merge_similar_colors(entries)
    hexes = {e["hex"] for e in merged}
    assert "#ffffff" in hexes and "#ff0000" in hexes
    assert len(merged) == 2, f"近白色应被合并，实际 {merged}"


def test_split_rules_flattens_and_skips_at_rules():
    css = "@import url(x.css); @charset 'utf-8'; a{color:red} @media (min-width:600px){b{color:blue}}"
    rules = dict(E.split_rules(css))
    assert rules.get("a") == "color:red"
    assert "b" in rules and "blue" in rules["b"]


def test_list_page_content_is_extracted():
    """阮一峰式列表页：正文全在 <li> 里，只看 <p> 会得到 0 段。"""
    html = """<html><body><div id="main"><ul>""" + \
        "".join(f"<li><a href='/x{i}'>这是一条足够长的条目内容第{i}项</a></li>" for i in range(12)) + \
        "</ul></div></body></html>"
    from bs4 import BeautifulSoup
    con = E.extract_content(BeautifulSoup(html, "lxml"), "https://example.com/")
    assert con["paragraph_count"] > 0, "列表型页面必须能抽到内容"
    assert con["word_count"] > 0


def test_old_school_html_signals():
    html = """<html><body bgcolor="#ffffff"><center><font size="3" color="red">hi</font></center>
    <marquee>scroll</marquee><table border="1" cellpadding="2"><tr><td>x</td></tr></table></body></html>"""
    from bs4 import BeautifulSoup
    sig = E.extract_html_signals(BeautifulSoup(html, "lxml"))
    assert sig["old_school"] >= 2, f"应识别出老式 HTML 痕迹，实际 {sig}"
    assert sig["font_tag"] == 1 and sig["center_tag"] == 1 and sig["marquee_tag"] == 1


def test_retro_wins_on_oldschool_page():
    """纯 CSS 视角下 1996 年的站看起来'很干净'，但它其实是复古风。"""
    dna = {
        "palette": {"background": "#ffffff", "text": "#000000", "primary": "#e80000",
                    "accent": "#e80000", "vivid_count": 1, "contrast_text_bg": 21.0},
        "typography": {"has_serif": False, "body_char": "sans", "heading_char": "sans",
                       "has_mono": False, "type_ratio": 1.2, "weight_count": 2,
                       "letter_spacing": 0},
        "rhythm": {"max_radius": 0, "container_width": 1200, "density": "dense"},
        "effects": {"gradient": 0, "shadow": 0, "glow": 0, "blur": 0, "pattern": 0},
        "html_signals": {"old_school": 14, "font_tag": 6, "frameset": 0},
        "content": {"quotes": [], "key_numbers": []},
        "meta": {"style_signal_strength": "weak"},
    }
    cls = E.classify_style(dna)
    assert cls["style"] == "retro", f"应判为复古风，实际 {cls['style']} {cls['scores']}"


def test_low_signal_weakens_css_based_verdicts():
    base = {
        "palette": {"background": "#ffffff", "text": "#111111", "primary": "#111111",
                    "accent": "#111111", "vivid_count": 1, "contrast_text_bg": 18.0},
        "typography": {"has_serif": False, "body_char": "sans", "heading_char": "sans",
                       "has_mono": False, "type_ratio": 1.4, "weight_count": 2,
                       "letter_spacing": 0},
        "rhythm": {"max_radius": 0, "container_width": 900, "density": "airy"},
        "effects": {"gradient": 0, "shadow": 0, "glow": 0, "blur": 0, "pattern": 0},
        "html_signals": {"old_school": 0},
        "content": {"quotes": [], "key_numbers": []},
    }
    strong = dict(base, meta={"style_signal_strength": "strong"})
    weak = dict(base, meta={"style_signal_strength": "weak"})
    cs, cw = E.classify_style(strong), E.classify_style(weak)
    assert cs["style"] == "minimalist"
    # 信号弱时，CSS 类结论必须被压低（置信度下降或让位给有 HTML 证据的风格）
    assert cw["scores"]["minimalist"] <= cs["scores"]["minimalist"]


def test_end_to_end_on_local_html(tmpdir=None):
    """用本地 HTML 走完整链路，不依赖网络。"""
    import tempfile
    html = """<!DOCTYPE html><html lang="zh"><head><meta charset="utf-8">
    <title>测试页</title><meta name="description" content="一个用于测试的页面">
    <meta property="og:site_name" content="TestSite">
    <style>
      :root{--brand:#2f6fed;--paper:#faf9f6;--ink:#16181d;--pad:24px}
      body{background:var(--paper);color:var(--ink);font-family:"Georgia",serif;line-height:1.8;
           margin:0;padding:var(--pad);max-width:680px;border-radius:2px}
      h1{font-family:"Georgia",serif;font-size:44px;font-weight:400;letter-spacing:-0.02em;margin:0 0 24px}
      p{font-size:17px;margin:0 0 20px}
      a{color:var(--brand);text-decoration:underline}
      blockquote{border-left:2px solid var(--brand);padding-left:16px}
      @media (prefers-color-scheme: dark){ body{background:#101010;color:#eee} }
    </style></head><body>
    <h1>标题要足够大</h1>
    <p>第一段正文，用来验证正文抽取是否工作。这段话需要超过六十个字符才会被算法认为是有意义的段落内容。</p>
    <p>第二段提到 2024 年增长 37% 以及 128 亿元这样的关键数字，用于验证数字抽取。</p>
    <blockquote>这是一句引语，属于杂志风的典型排版手法。</blockquote>
    <h2>小节标题</h2>
    <p>小节下面的正文段落，同样需要足够长以便被识别为有效段落内容，这里再多写一些字凑长度。</p>
    </body></html>"""
    d = tempfile.mkdtemp()
    p = os.path.join(d, "t.html")
    with open(p, "w", encoding="utf-8") as f:
        f.write(html)
    dna = E.extract_dna(p, fetch_css=False)

    # 标题优先级：og:title -> <h1> -> <title>。这里有 <h1>，所以取 h1 是正确的。
    assert dna["content"]["title"] == "标题要足够大", dna["content"]["title"]
    assert dna["palette"]["primary"].lower() == "#2f6fed", dna["palette"]["primary"]
    assert dna["palette"]["background"].lower() == "#faf9f6"
    assert dna["typography"]["body_char"] == "serif"
    assert dna["typography"]["body_stack"] == "Georgia, serif", dna["typography"]["body_stack"]
    assert dna["rhythm"]["base_unit"] in (2, 4, 8, 24, 12), dna["rhythm"]["base_unit"]
    assert dna["content"]["paragraph_count"] >= 2
    assert dna["classification"]["style"] in E.STYLES
    # 暗色媒体查询里的 #101010 不该出现在底色里
    assert dna["palette"]["background"] != "#101010"


def _run_all():
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    failed = 0
    for fn in fns:
        try:
            fn()
            print(f"  PASS  {fn.__name__}")
        except AssertionError as e:
            failed += 1
            print(f"  FAIL  {fn.__name__}: {e}")
        except Exception as e:
            failed += 1
            print(f"  ERROR {fn.__name__}: {type(e).__name__}: {e}")
    print(f"\n{len(fns) - failed}/{len(fns)} 通过")
    return failed


if __name__ == "__main__":
    sys.exit(1 if _run_all() else 0)
