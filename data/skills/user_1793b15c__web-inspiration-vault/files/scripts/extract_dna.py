#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
extract_dna.py — 网页「视觉 DNA」提取引擎
========================================
输入：URL 或本地 HTML（含 SingleFile 单文件产物）
输出：dna.json —— 结构化描述一个页面的 配色 / 字体 / 排版节奏 / 文字内容 / 风格归属

设计原则（重要）：
1. 零重型依赖。只用 requests + beautifulsoup4 + lxml，不装无头浏览器。
2. 字段按 "computed style 语义" 命名。将来若接入 Playwright 取真实计算样式，
   只需替换 `collect_declarations()` 的数据源，下游模板不用改一行。
3. 不做截图、不做 OCR —— 全程结构化解析，可复现、可 diff、可单元测试。

用法：
    python extract_dna.py <URL 或 本地.html> [-o dna.json] [--download-images] [--no-css]
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import sys
from collections import Counter, defaultdict
from urllib.parse import urljoin, urlparse

try:
    import requests
except ImportError:  # pragma: no cover
    requests = None

from bs4 import BeautifulSoup

UA = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}

# --------------------------------------------------------------------------
# 0. 颜色基础工具
# --------------------------------------------------------------------------

NAMED_COLORS = {
    "white": "#ffffff", "black": "#000000", "red": "#ff0000", "blue": "#0000ff",
    "green": "#008000", "gray": "#808080", "grey": "#808080", "silver": "#c0c0c0",
    "navy": "#000080", "teal": "#008080", "maroon": "#800000", "purple": "#800080",
    "olive": "#808000", "lime": "#00ff00", "aqua": "#00ffff", "cyan": "#00ffff",
    "fuchsia": "#ff00ff", "magenta": "#ff00ff", "yellow": "#ffff00", "orange": "#ffa500",
    "pink": "#ffc0cb", "brown": "#a52a2a", "gold": "#ffd700", "beige": "#f5f5dc",
    "ivory": "#fffff0", "whitesmoke": "#f5f5f5", "ghostwhite": "#f8f8ff",
    "snow": "#fffafa", "linen": "#faf0e6", "seashell": "#fff5ee", "mistyrose": "#ffe4e1",
    "lavender": "#e6e6fa", "aliceblue": "#f0f8ff", "azure": "#f0ffff", "honeydew": "#f0fff0",
    "mintcream": "#f5fffa", "floralwhite": "#fffaf0", "oldlace": "#fdf5e6",
    "cornsilk": "#fff8dc", "lemonchiffon": "#fffacd", "lightyellow": "#ffffe0",
    "lightcyan": "#e0ffff", "powderblue": "#b0e0e6", "lightblue": "#add8e6",
    "skyblue": "#87ceeb", "steelblue": "#4682b4", "dodgerblue": "#1e90ff",
    "royalblue": "#4169e1", "indigo": "#4b0082", "violet": "#ee82ee", "orchid": "#da70d6",
    "plum": "#dda0dd", "tan": "#d2b48c", "salmon": "#fa8072", "tomato": "#ff6347",
    "orangered": "#ff4500", "crimson": "#dc143c", "firebrick": "#b22222",
    "darkred": "#8b0000", "darkgreen": "#006400", "darkblue": "#00008b",
    "darkgray": "#a9a9a9", "darkgrey": "#a9a9a9", "dimgray": "#696969",
    "dimgrey": "#696969", "lightgray": "#d3d3d3", "lightgrey": "#d3d3d3",
    "gainsboro": "#dcdcdc", "papayawhip": "#ffefd5", "peachpuff": "#ffdab9",
    "khaki": "#f0e68c", "wheat": "#f5deb3", "burlywood": "#deb887",
    "chocolate": "#d2691e", "sienna": "#a0522d", "peru": "#cd853f", "sandybrown": "#f4a460",
    "darkorange": "#ff8c00", "darkolivegreen": "#556b2f", "seagreen": "#2e8b57",
    "forestgreen": "#228b22", "mediumseagreen": "#3cb371", "turquoise": "#40e0d0",
    "darkcyan": "#008b8b", "slateblue": "#6a5acd", "mediumpurple": "#9370db",
    "rebeccapurple": "#663399", "hotpink": "#ff69b4", "deeppink": "#ff1493",
    "lightpink": "#ffb6c1", "thistle": "#d8bfd8", "midnightblue": "#191970",
}

SKIP_COLOR_WORDS = {"transparent", "currentcolor", "inherit", "initial", "unset", "none", "auto"}

COLOR_LITERAL_RE = re.compile(
    r"(#[0-9a-fA-F]{3,8}\b|rgba?\([^)]*\)|hsla?\([^)]*\)"
    r"|oklch\([^)]*\)|oklab\([^)]*\)|lch\([^)]*\)|lab\([^)]*\)|\b[a-zA-Z]{3,20}\b)"
)


def _oklch_to_rgb(L, C, H):
    """OKLCH -> sRGB（Tailwind v4 / shadcn 等现代站点大量使用）。"""
    hr = math.radians(H)
    a = C * math.cos(hr)
    b = C * math.sin(hr)
    l_ = L + 0.3963377774 * a + 0.2158037573 * b
    m_ = L - 0.1055613458 * a - 0.0638541728 * b
    s_ = L - 0.0894841775 * a - 1.2914855480 * b
    l3, m3, s3 = l_ ** 3, m_ ** 3, s_ ** 3
    lin = (
        +4.0767416621 * l3 - 3.3077115913 * m3 + 0.2309699292 * s3,
        -1.2684380046 * l3 + 2.6097574011 * m3 - 0.3413193965 * s3,
        -0.0041960863 * l3 - 0.7034186147 * m3 + 1.7076147010 * s3,
    )

    def enc(c):
        c = max(0.0, min(1.0, c))
        c = 12.92 * c if c <= 0.0031308 else 1.055 * (c ** (1 / 2.4)) - 0.055
        return max(0, min(255, round(c * 255)))

    return tuple(enc(c) for c in lin)


def _oklab_to_rgb(L, a, b):
    return _oklch_to_rgb(L, math.hypot(a, b), math.degrees(math.atan2(b, a)))


FUNC_COLOR_RE = re.compile(
    r"(rgba?\([^)]*\)|hsla?\([^)]*\)|oklch\([^)]*\)|oklab\([^)]*\)|lch\([^)]*\)|lab\([^)]*\))"
)
HEX_RE = re.compile(r"#[0-9a-fA-F]{3,8}\b")


def iter_color_tokens(value: str):
    """从一条 CSS 值里抽出真正的颜色 token。

    关键坑（已踩）：`var(--color-pink-500)` 里裸扫字母会命中 "pink"，
    于是 Tailwind 官网的主色被解析成粉红、文字色变成靛蓝，整张配色卡全错。
    所以必须先剔除 var()/url()，且纯色名必须"整词"匹配，不接受连字符片段。
    """
    if not value:
        return []
    v = re.sub(r"var\([^()]*\)", " ", value)
    v = re.sub(r"url\([^)]*\)", " ", v)
    v = re.sub(r"env\([^)]*\)", " ", v)
    v = re.sub(r"calc\([^()]*\)", " ", v)

    out = [m.group(1) for m in FUNC_COLOR_RE.finditer(v)]
    rest = FUNC_COLOR_RE.sub(" ", v)
    out.extend(HEX_RE.findall(rest))
    rest = HEX_RE.sub(" ", rest)
    for word in re.split(r"[^a-zA-Z]+", rest):
        if len(word) >= 3 and word.lower() in NAMED_COLORS:
            out.append(word.lower())
    return out


def resolve_vars(value: str, css_vars, depth=3):
    """把 var(--x) / var(--x, fallback) 替换成 :root 里的实际值。

    字体栈常见 `font-family: var(--font-sans)`，不解析就只剩一个
    "var(--font-sans)" 字符串，字体族判定全成 unknown。
    """
    if not value or "var(" not in value:
        return value
    for _ in range(depth):
        if "var(" not in value:
            break

        def rep(m):
            name, _, fallback = m.group(1).partition(",")
            name = name.strip()
            if name in css_vars:
                return css_vars[name]
            return fallback.strip() or " "

        value = re.sub(r"var\(([^()]*)\)", rep, value)
    return value


def merge_similar_colors(entries, threshold=14.0):
    """把视觉上几乎一样的颜色合并（#ffffff / #fefefe / #fdfdfd 应视作同一色）。

    不合并的话 palette_size 会虚高、vivid_count 失真，风格评分跟着跑偏。
    """
    merged = []
    for e in sorted(entries, key=lambda x: -x["score"]):
        rgb = parse_color(e["hex"])
        hit = None
        for m in merged:
            mrgb = parse_color(m["hex"])
            if rgb is None or mrgb is None:
                continue
            dist = math.sqrt(sum((a - b) ** 2 for a, b in zip(rgb[:3], mrgb[:3])))
            if dist <= threshold:
                hit = m
                break
        if hit:
            hit["score"] = round(hit["score"] + e["score"], 2)
            hit["hits"] += e["hits"]
            hit["roles"] = sorted(set(hit["roles"]) | set(e["roles"]))
            hit["merged"] = hit.get("merged", 1) + 1
        else:
            e = dict(e)
            e["merged"] = 1
            merged.append(e)
    return merged


def parse_color(token: str):
    """把 CSS 颜色字面量转成 (r,g,b,a)，失败返回 None。"""
    if not token:
        return None
    t = token.strip().lower()
    if t in SKIP_COLOR_WORDS:
        return None
    if t.startswith("#"):
        h = t[1:]
        if len(h) == 3:
            h = "".join(c * 2 for c in h)
        elif len(h) == 4:
            h = "".join(c * 2 for c in h[:3])
        elif len(h) == 8:
            h = h[:6]
        if len(h) != 6:
            return None
        try:
            return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), 1.0)
        except ValueError:
            return None
    if t.startswith(("rgb(", "rgba(")):
        nums = re.findall(r"[-+]?[\d.]+%?", t)
        if len(nums) < 3:
            return None
        vals = []
        for n in nums[:3]:
            if n.endswith("%"):
                vals.append(round(float(n[:-1]) * 2.55))
            else:
                vals.append(round(float(n)))
        alpha = 1.0
        if len(nums) >= 4:
            try:
                a = nums[3]
                alpha = float(a[:-1]) / 100 if a.endswith("%") else float(a)
            except ValueError:
                alpha = 1.0
        return (vals[0], vals[1], vals[2], alpha)
    if t.startswith("oklch("):
        nums = re.findall(r"[-+]?[\d.]+%?", t)
        if len(nums) < 3:
            return None
        try:
            L = float(nums[0].rstrip("%"))
            if nums[0].endswith("%"):
                L /= 100.0
            C = float(nums[1].rstrip("%"))
            if nums[1].endswith("%"):
                C = C / 100.0 * 0.4
            H = float(nums[2].rstrip("%").rstrip("deg"))
        except ValueError:
            return None
        alpha = 1.0
        if len(nums) >= 4:
            try:
                alpha = float(nums[3].rstrip("%")) / 100.0 if nums[3].endswith("%") else float(nums[3])
            except ValueError:
                alpha = 1.0
        rgb = _oklch_to_rgb(L, C, H)
        return (rgb[0], rgb[1], rgb[2], alpha)
    if t.startswith("oklab("):
        nums = re.findall(r"[-+]?[\d.]+%?", t)
        if len(nums) < 3:
            return None
        try:
            L = float(nums[0].rstrip("%"))
            if nums[0].endswith("%"):
                L /= 100.0
            a, b = float(nums[1]), float(nums[2])
        except ValueError:
            return None
        rgb = _oklab_to_rgb(L, a, b)
        return (rgb[0], rgb[1], rgb[2], 1.0)
    if t.startswith(("hsl(", "hsla(")):
        nums = re.findall(r"[-+]?[\d.]+%?", t)
        if len(nums) < 3:
            return None
        try:
            h = float(nums[0]) % 360 / 360.0
            s = float(nums[1].rstrip("%")) / 100.0
            l = float(nums[2].rstrip("%")) / 100.0
        except ValueError:
            return None
        r, g, b = _hsl_to_rgb(h, s, l)
        return (r, g, b, 1.0)
    if t in NAMED_COLORS:
        return parse_color(NAMED_COLORS[t])
    return None


def _hsl_to_rgb(h, s, l):
    if s == 0:
        v = round(l * 255)
        return v, v, v
    q = l * (1 + s) if l < 0.5 else l + s - l * s
    p = 2 * l - q

    def hue(t):
        t = t % 1
        if t < 1 / 6:
            return p + (q - p) * 6 * t
        if t < 1 / 2:
            return q
        if t < 2 / 3:
            return p + (q - p) * (2 / 3 - t) * 6
        return p

    return tuple(round(x * 255) for x in (hue(h + 1 / 3), hue(h), hue(h - 1 / 3)))


def to_hex(rgb):
    return "#%02x%02x%02x" % (rgb[0], rgb[1], rgb[2])


def rgb_to_hsl(rgb):
    r, g, b = [x / 255.0 for x in rgb[:3]]
    mx, mn = max(r, g, b), min(r, g, b)
    l = (mx + mn) / 2
    if mx == mn:
        return 0.0, 0.0, l
    d = mx - mn
    s = d / (2 - mx - mn) if l > 0.5 else d / (mx + mn)
    if mx == r:
        h = ((g - b) / d) % 6
    elif mx == g:
        h = (b - r) / d + 2
    else:
        h = (r - g) / d + 4
    return h * 60.0, s, l


def is_neutral(rgb):
    _, s, l = rgb_to_hsl(rgb)
    return s < 0.13 or l < 0.07 or l > 0.94


def contrast_ratio(c1, c2):
    def lum(c):
        vals = []
        for x in c[:3]:
            x = x / 255.0
            vals.append(x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4)
        return 0.2126 * vals[0] + 0.7152 * vals[1] + 0.0722 * vals[2]

    l1, l2 = lum(c1), lum(c2)
    if l1 < l2:
        l1, l2 = l2, l1
    return (l1 + 0.05) / (l2 + 0.05)


# --------------------------------------------------------------------------
# 1. 载入 HTML + 收集 CSS
# --------------------------------------------------------------------------

def load_html(src: str):
    """返回 (html_text, base_url)。src 可以是 URL 或本地文件路径。"""
    if re.match(r"^https?://", src, re.I):
        if requests is None:
            raise RuntimeError("需要 requests 才能抓取 URL")
        r = requests.get(src, headers=UA, timeout=30)
        r.raise_for_status()
        if not r.encoding or r.encoding.lower() in ("iso-8859-1", "ascii"):
            r.encoding = r.apparent_encoding or "utf-8"
        return r.text, src
    with open(src, "rb") as f:
        raw = f.read()
    for enc in ("utf-8", "utf-8-sig", "gb18030", "big5", "latin-1"):
        try:
            return raw.decode(enc), "file:///" + os.path.abspath(src).replace("\\", "/")
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", "ignore"), "file:///" + os.path.abspath(src).replace("\\", "/")


def is_singlefile(html: str) -> bool:
    """判断是不是 SingleFile 产物（样式/字体/图片已内联）。

    只认显式标记。早期版本用 `data:image/ 出现次数>5` 判断，
    结果把 Tailwind 官网（15 处内联 data:image）误判成 SingleFile，
    导致整站 CSS 被跳过、DNA 全废 —— 这个坑已经踩过，别再回去。
    """
    head = html[:300000]
    markers = (
        "SingleFile",
        "single-file",
        "saved from url=",
        "data:font/",
        "data:application/font",
    )
    return any(m in head for m in markers)


def _match_brace(css: str, open_idx: int) -> int:
    """返回与 css[open_idx]=='{' 配对的 '}' 之后的位置。"""
    depth = 0
    for i in range(open_idx, len(css)):
        if css[i] == "{":
            depth += 1
        elif css[i] == "}":
            depth -= 1
            if depth == 0:
                return i + 1
    return len(css)


def strip_dark_media(css: str) -> str:
    """删掉 `@media (prefers-color-scheme: dark)` 整块。

    否则暗色主题的配色会混进亮色配色里，把主色/底色彻底污染 ——
    Tailwind 系站点尤其严重（暗色变量占比极高）。
    """
    out, i = [], 0
    while True:
        m = re.search(r"@media[^{]*\{", css[i:])
        if not m:
            out.append(css[i:])
            break
        start, brace = i + m.start(), i + m.end() - 1
        cond = re.sub(r"\s+", "", css[start:brace].lower())
        end = _match_brace(css, brace)
        out.append(css[i:start])
        if not re.search(r"prefers-color-scheme:dark", cond):
            out.append(css[start:end])
        i = end
    return "".join(out)



def collect_css(soup: BeautifulSoup, base_url: str, fetch_remote=True, max_css=6):
    """收集页面所有 CSS 文本：<style>、外链 stylesheet、@import 一层。"""
    chunks = []
    for st in soup.find_all("style"):
        txt = st.string or st.get_text() or ""
        if txt.strip():
            chunks.append(txt)

    links = []
    for ln in soup.find_all("link"):
        rels = " ".join(ln.get("rel") or []).lower()
        if "stylesheet" in rels and ln.get("href"):
            links.append(urljoin(base_url, ln["href"]))

    fetched = 0
    for href in links[:max_css]:
        if not fetch_remote:
            break
        try:
            if href.startswith("file:///"):
                path = href[8:]
                with open(path, "rb") as f:
                    chunks.append(f.read().decode("utf-8", "ignore"))
            else:
                r = requests.get(href, headers=UA, timeout=20)
                if r.status_code == 200 and r.text:
                    chunks.append(r.text)
            fetched += 1
        except Exception:
            continue

    # 内联 style 属性也是信号（Tailwind / 单页常常靠它）
    inline = []
    for el in soup.find_all(style=True):
        inline.append(el["style"])
    return "\n".join(chunks), inline, len(links), fetched


def split_rules(css: str):
    """把 CSS 拆成 [(selector, declarations_text)]，会剥掉注释并把 @media 内层摊平。"""
    css = strip_dark_media(css)
    css = re.sub(r"/\*.*?\*/", " ", css, flags=re.S)
    # 去掉 @import / @charset / @layer 声明
    css = re.sub(r"@(import|charset|layer|namespace)[^;{]*;", " ", css)
    rules = []
    for m in re.finditer(r"([^{}]+)\{([^{}]*)\}", css):
        sel = m.group(1).strip()
        decl = m.group(2).strip()
        if not decl or sel.startswith("@"):
            continue
        rules.append((sel, decl))
    return rules


DECL_RE = re.compile(r"([-a-zA-Z]+)\s*:\s*([^;]+)")

PROP_WEIGHT = {
    "background-color": 3.0, "background": 2.4, "background-image": 1.4,
    "color": 2.6, "border-color": 1.0, "border": 0.9, "border-top": 0.5,
    "border-bottom": 0.5, "border-left": 0.5, "outline-color": 0.6,
    "fill": 1.2, "stroke": 1.0, "box-shadow": 1.3, "text-decoration-color": 0.8,
    "caret-color": 0.3, "accent-color": 1.0, "text-shadow": 0.6,
    "border-radius": 1.0, "font-family": 2.0, "font-size": 1.6,
    "font-weight": 1.0, "letter-spacing": 1.0, "line-height": 1.4,
    "margin": 1.0, "margin-top": 1.0, "margin-bottom": 1.0, "margin-left": 1.0,
    "padding": 1.0, "padding-top": 1.0, "padding-bottom": 1.0, "padding-left": 1.0,
    "gap": 1.0, "row-gap": 1.0, "column-gap": 1.0, "max-width": 1.4, "width": 0.8,
}

SELECTOR_ROLE_WEIGHT = [
    (re.compile(r"(^|[\s,>])(html|:root|body)\b"), 3.0, "base"),
    (re.compile(r"(^|[\s,>])(h1)\b"), 2.2, "heading1"),
    (re.compile(r"(^|[\s,>])(h2|h3)\b"), 1.8, "heading"),
    (re.compile(r"(^|[\s,>])(h4|h5|h6)\b"), 1.2, "heading"),
    (re.compile(r"(^|[\s,>])(p|li|blockquote)\b"), 1.5, "body"),
    (re.compile(r"(^|[\s,>])(a|button|\.btn|\.button)\b"), 2.0, "action"),
    (re.compile(r"(nav|header|footer|aside)\b"), 1.3, "chrome"),
    (re.compile(r"(code|pre|kbd|samp|\.mono)\b"), 1.5, "code"),
    (re.compile(r"(\.card|\.box|\.panel|\.container|\.wrapper|main|article|section)\b"), 1.2, "surface"),
]


def selector_role(sel: str):
    for rx, w, role in SELECTOR_ROLE_WEIGHT:
        if rx.search(sel):
            return w, role
    return 1.0, "generic"


def collect_declarations(rules, inline_styles):
    """把 CSS 摊平成 [(prop, value, weight, role, selector)]。

     升级口：接 Playwright 时，只需改成遍历真实 DOM 的
      getComputedStyle(el)，按 el.tagName/class 生成同样的四元组即可。
    """
    out = []
    for sel, decl in rules:
        sw, role = selector_role(sel)
        # 多选择器拆开取最高权重
        for part in sel.split(","):
            w2, r2 = selector_role(part.strip())
            if w2 > sw:
                sw, role = w2, r2
        # 两类"脏选择器"必须降级为 generic，否则会污染按角色取值的判据：
        # ① 原生嵌套 CSS 被正则切碎后产生的残片（含 ; { } &）
        # ② 伪元素选择器 —— :where(ul>li)::marker{line-height:1} 描述的是列表标记，
        #    不是正文行高。RAND 就因此被误报"正文行高 1.0，行距过紧"。
        if any(ch in sel for ch in ";{}&") or "::" in sel:
            role = "generic"
        for m in DECL_RE.finditer(decl):
            prop = m.group(1).lower().strip()
            val = m.group(2).strip()
            if prop.startswith("--") or prop in ("transition", "animation", "cursor", "z-index"):
                continue
            pw = PROP_WEIGHT.get(prop)
            if pw is None:
                # 处理 padding-top / margin-left 等
                base = re.sub(r"-(top|bottom|left|right)$", "", prop)
                pw = PROP_WEIGHT.get(base, 0.0)
            if pw <= 0:
                continue
            out.append((prop, val, pw * sw, role, sel))
    for st in inline_styles:
        for m in DECL_RE.finditer(st):
            prop = m.group(1).lower().strip()
            val = m.group(2).strip()
            if prop.startswith("--"):
                continue
            pw = PROP_WEIGHT.get(prop, 0.4)
            out.append((prop, val, pw * 1.1, "inline", "style="))
    return out


# --------------------------------------------------------------------------
# 2. 视觉 DNA 各维度提取
# --------------------------------------------------------------------------

def extract_palette(decls, css_vars, used_vars=None):
    """按 属性权重 × 选择器角色权重 × 频次 给颜色打分，再分派语义角色。"""
    used_vars = used_vars or set()
    score = defaultdict(float)
    roles_of = defaultdict(set)
    count = Counter()
    for prop, val, w, role, sel in decls:
        if prop in ("box-shadow", "text-shadow"):
            continue  # 阴影里的颜色多为装饰噪点，不算进主配色
        resolved = resolve_vars(val, css_vars)
        for tok in iter_color_tokens(resolved):
            rgb = parse_color(tok)
            if not rgb or rgb[3] < 0.15:
                continue
            key = to_hex(rgb) if rgb[3] >= 0.99 else to_hex(rgb) + f"@{rgb[3]:.2f}"
            score[key] += w
            count[key] += 1
            roles_of[key].add(role)

    # :root 自定义属性：只有"被真正 var() 引用过"的才算页面在用的颜色。
    # 现代站点（Tailwind / shadcn / Flexoki）会一次性定义上百个色板变量，
    # 全量计入会把 palette_size 撑到 100+、主色被没用的变量挤掉 —— 大坑。
    var_colors = {}
    for name, val in css_vars.items():
        rgb = parse_color(resolve_vars(val.strip().rstrip(";"), css_vars))
        if not rgb:
            continue
        key = to_hex(rgb)
        used = name in used_vars
        w = 2.6 if used else 0.10
        score[key] += w
        count[key] += 1
        roles_of[key].add("var" if used else "var-unused")
        if used:
            var_colors[name] = key

    ranked = sorted(score.items(), key=lambda kv: -kv[1])
    entries = []
    for key, sc in ranked:
        raw = key.split("@")[0]
        rgb = parse_color(raw)
        if not rgb:
            continue
        h, s, l = rgb_to_hsl(rgb)
        entries.append({
            "hex": raw, "score": round(sc, 2), "hits": count[key],
            "hue": round(h, 1), "sat": round(s, 3), "light": round(l, 3),
            "neutral": is_neutral(rgb), "roles": sorted(roles_of[key]),
        })
    entries = merge_similar_colors(entries)

    # 只有"得分够高"的颜色才算页面真正在用的色。低分项多为未使用的
    # 色板变量和一次性噪点，计入会让 palette_size / vivid_count 虚高。
    significant = [e for e in entries if e["score"] >= 1.0] or entries[:6]

    light = [e for e in significant if e["light"] > 0.86 and not e["sat"] > 0.35]
    dark = [e for e in significant if e["light"] < 0.35]

    # 品牌色候选必须"足够彩 + 中等明度"。
    # 踩坑（RAND 暴露）：RAND 的墨色 --black90 #2d2b19 明度仅 0.137，
    # 却因饱和度 0.286 被判成 vivid，抢走真品牌紫 #751ddb 的位置，
    # 导致风格评分读到"暖色相 54° 饱和 0.29" -> 误判复古风。
    # 近黑/近白永远不是品牌色：这是硬约束。
    brand = [e for e in significant if e["sat"] >= 0.28 and 0.18 <= e["light"] <= 0.85]
    brand.sort(key=lambda e: -(e["score"] + (3.0 if "action" in e["roles"] else 0)))
    vivid = brand

    background = light[0]["hex"] if light else "#ffffff"
    surface = None
    for e in light[1:]:
        if e["hex"] != background:
            surface = e["hex"]
            break
    text = dark[0]["hex"] if dark else "#1a1a1a"

    primary = brand[0]["hex"] if brand else text
    accent = None
    for e in brand[1:]:
        if abs(e["hue"] - (brand[0]["hue"] if brand else 0)) > 25:
            accent = e["hex"]
            break
    if accent is None and len(brand) > 1:
        accent = brand[1]["hex"]

    muted = None
    for e in significant:
        if e["neutral"] and 0.35 <= e["light"] <= 0.72:
            muted = e["hex"]
            break

    return {
        "background": background,
        "surface": surface or _shift(background, -0.035),
        "surface_alt": _shift(background, -0.07),
        "text": text,
        "text_muted": muted or _shift(text, 0.42),
        "primary": primary,
        "accent": accent or primary,
        "border": _shift(background, -0.12),
        "palette_size": len(significant),
        "vivid_count": len(vivid),
        "raw_color_count": len(entries),
        "contrast_text_bg": round(contrast_ratio(parse_color(text), parse_color(background)), 2),
        "top_colors": entries[:10],
        "brand_palette": [
            {"hex": e["hex"], "hue": e["hue"], "sat": e["sat"], "light": e["light"],
             "score": e["score"], "roles": e["roles"]}
            for e in brand[:6]
        ],
        "css_vars": var_colors,
        "declared_token_count": len(var_colors),
    }


def _shift(hex_color, amount):
    """按亮度平移生成派生色（amount>0 变亮，<0 变暗）。"""
    rgb = parse_color(hex_color)
    if not rgb:
        return hex_color
    out = []
    for x in rgb[:3]:
        v = x / 255.0
        v = v + amount if amount < 0 else v + (1 - v) * amount
        out.append(max(0, min(255, round(v * 255))))
    return to_hex(out)


GENERIC_SERIF = ("serif", "times", "georgia", "garamond", "songti", "stsong", "宋体",
                 "仿宋", "楷体", "kaiti", "book antiqua", "palatino", "baskerville", "mincho")
GENERIC_SANS = ("sans-serif", "helvetica", "arial", "system-ui", "-apple-system", "segoe",
                "roboto", "inter", "pingfang", "苹方", "microsoft yahei", "微软雅黑",
                "noto sans", "lato", "open sans", "poppins", "circular", "sf pro")
GENERIC_MONO = ("mono", "menlo", "consolas", "courier", "fira code", "jetbrains",
                "sfmono", "source code", "inconsolata", "cascadia")


def classify_stack(stack: str):
    """判定字体栈的族系。

    注意顺序：必须先 mono -> 再 sans -> 最后 serif。
    因为 "sans-serif" 本身包含子串 "serif"，早期顺序把
    "system-ui, sans-serif" 判成了衬线体，直接带偏 magazine 评分。
    """
    s = stack.lower()
    if any(k in s for k in GENERIC_MONO):
        return "mono"
    if "sans-serif" in s or "sans serif" in s or any(k in s for k in GENERIC_SANS):
        return "sans"
    if any(k in s for k in GENERIC_SERIF):
        return "serif"
    return "unknown"


def trusted_char(stack):
    """判定字体族系——但只在第一族"是已知字体"时才敢下结论。

    同一个坑出现了三次，这里一次性根治：
      · RAND 标题栈 fraktion, Lucida Console, Monaco, monospace -> 误读成等宽
      · RAND 正文栈 suisse, Times New Roman, Georgia, serif -> 误读成衬线
    品牌自定义字体的回退链只是"兜底方案"，不代表设计意图。
    第一族不认识时，诚实的答案是"族系未知"，而不是从兜底链里硬猜一个。
    """
    ff = first_family(stack)
    if looks_custom_font(ff):
        return "unknown"
    return classify_stack(stack)


KNOWN_FONTS = {
    "helvetica", "helvetica neue", "arial", "arial black", "georgia", "verdana", "tahoma",
    "trebuchet ms", "times", "times new roman", "courier", "courier new", "impact",
    "comic sans ms", "palatino", "garamond", "book antiqua", "calibri", "cambria",
    "candara", "corbel", "consolas", "constantia", "segoe ui", "segoe ui variable",
    "franklin gothic", "gill sans", "optima", "futura", "avenir", "din", "myriad pro",
    "roboto", "roboto mono", "open sans", "lato", "montserrat", "poppins", "inter",
    "nunito", "raleway", "source sans pro", "work sans", "dm sans", "manrope",
    "ibm plex sans", "ibm plex mono", "ibm plex serif", "space grotesk", "space mono",
    "jetbrains mono", "fira sans", "fira code", "fira mono", "noto sans", "noto serif",
    "noto sans sc", "noto serif sc", "pt sans", "pt serif", "ubuntu", "ubuntu mono",
    "karla", "rubik", "barlow", "archivo", "public sans", "figtree", "outfit",
    "playfair display", "merriweather", "lora", "crimson text", "eb garamond",
    "libre baskerville", "source serif pro", "bitter", "domine", "spectral",
    "pingfang sc", "pingfang", "hiragino sans gb", "microsoft yahei", "microsoft jhenghei",
    "simsun", "simhei", "songti sc", "stsong", "heiti sc", "heiti", "kaiti", "fangsong",
    "system-ui", "-apple-system", "blinkmacsystemfont", "ui-monospace", "ui-sans-serif",
    "ui-serif", "ui-rounded", "sans-serif", "serif", "monospace", "cursive", "fantasy",
    "emoji", "apple color emoji", "segoe ui emoji", "menlo", "monaco", "lucida console",
    "lucida grande", "lucida sans unicode", "ms sans serif", "ms serif", "tahoma",
    "geneva", "candara", "charter", "iowan old style", "seravek", "san francisco",
}


def first_family(stack):
    """取字体栈的第一族 —— 它才代表设计意图，后面都是 fallback。"""
    if not stack:
        return None
    for part in str(stack).split(","):
        p = part.strip().strip('"').strip("'").strip()
        if p:
            return p
    return None


def looks_custom_font(name):
    """判断第一族是不是"品牌自定义字体"。

    为什么要单独判：RAND 的标题栈是 `fraktion, Lucida Console, Monaco, monospace`。
    按整串找通用族会命中 Monaco/monospace，于是把品牌展示字体误读成"等宽"，
    进而给科技风加分。自定义字体应当明确标记为"族系未知"，而不是硬套一个错的。
    """
    if not name:
        return False
    n = name.lower().strip()
    if n in ("inherit", "initial", "unset", "auto"):
        return False
    if n in KNOWN_FONTS:
        return False
    for k in GENERIC_MONO + GENERIC_SERIF + GENERIC_SANS:
        if k in n and len(k) > 4:
            return False
    return True


def extract_typography(decls, css_vars):
    fam = defaultdict(float)
    fam_role = defaultdict(set)
    sizes = defaultdict(float)
    sizes_core = defaultdict(float)
    weights = Counter()
    sizes_role = defaultdict(lambda: defaultdict(float))
    spacing = defaultdict(float)
    lh = defaultdict(float)
    lh_role = defaultdict(lambda: defaultdict(float))

    for prop, val, w, role, sel in decls:
        if prop == "font-family":
            clean = _clean_family(resolve_vars(val, css_vars))
            if clean:
                fam[clean] += w
                fam_role[clean].add(role)
        elif prop == "font-size":
            for p in _px_values(resolve_vars(val, css_vars)):
                sizes[p] += w
                if 8 <= p <= 200:
                    sizes_role[role][round(p)] += w
                if role in ("heading1", "heading", "body", "base"):
                    sizes_core[p] += w
        elif prop == "font-weight":
            v = resolve_vars(val, css_vars).strip()
            if re.fullmatch(r"\d{3}", v):
                weights[v] += 1
            elif v in ("bold", "bolder"):
                weights["700"] += 1
            elif v == "normal":
                weights["400"] += 1
        elif prop == "letter-spacing":
            for p in _px_values(resolve_vars(val, css_vars), allow_em=True):
                spacing[p] += w
        elif prop == "line-height":
            rv = resolve_vars(val, css_vars).strip()
            ratios = []
            if rv.endswith("%"):
                try:
                    ratios = [round(float(rv[:-1]) / 100, 3)]
                except ValueError:
                    ratios = []
            elif re.fullmatch(r"\d*\.?\d+", rv):
                ratios = [float(rv)]
            else:
                ratios = [round(p / 16, 3) for p in _px_values(rv) if p >= 8]
            for r in ratios:
                lh[r] += w
                lh_role[role][r] += w

    for name, val in css_vars.items():
        if "font" in name and ("sans" in name or "serif" in name or "mono" in name):
            clean = _clean_family(val)
            if clean:
                fam[clean] += 2.2

    stacks = sorted(fam.items(), key=lambda kv: -kv[1])
    heading_stack = body_stack = code_stack = None
    for stack, sc in stacks:
        kind = classify_stack(stack)
        roles = fam_role[stack]
        if code_stack is None and kind == "mono":
            code_stack = stack
        if heading_stack is None and ("heading" in roles or "heading1" in roles):
            heading_stack = stack
        if body_stack is None and ("body" in roles or "base" in roles):
            body_stack = stack

    top_kind = classify_stack(stacks[0][0]) if stacks else "sans"
    body_stack = body_stack or (stacks[0][0] if stacks else "system-ui, sans-serif")
    if heading_stack is None:
        serif_alt = [s for s, _ in stacks if classify_stack(s) == "serif"]
        heading_stack = serif_alt[0] if (top_kind == "serif" and serif_alt) else body_stack
    if code_stack is None:
        code_stack = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"

    size_list = sorted(p for p in sizes if 8 <= p <= 200)
    core_list = sorted(p for p in sizes_core if 8 <= p <= 200)
    if len(core_list) >= 3:
        # 优先用 html/body/h1-h6/p 这些"结构性选择器"上的字号。
        # 直接用全量字号会被工具类字号阶梯（text-9xl 之类）拉爆，
        # Tailwind 官网的字号比因此虚高到 8.0，被误判成杂志风。
        size_list = core_list
    body_size = min(size_list, key=lambda p: abs(p - 16)) if size_list else 16
    biggest = max(size_list) if size_list else 32
    ratio = round(min(biggest / max(body_size, 1), 4.0), 2)

    ls_sorted = sorted(spacing.items(), key=lambda kv: -kv[1])

    def _pick_lh(roles):
        """按角色取行高，而不是取全站最大值。

        踩坑（RAND 暴露）：全局最高权重行高是 h1 的 line-height:1（大标题本就该 1），
        结果体检报告指责"正文行高 1.0，行距过紧" —— 纯属误报。
        必须按选择器角色区分正文与标题。
        """
        pool = defaultdict(float)
        for r in roles:
            for v, w in lh_role.get(r, {}).items():
                pool[v] += w
        if not pool:
            return None
        v = max(pool, key=lambda k: pool[k])
        return round(v, 2) if 0.9 <= v <= 2.6 else None

    # 顺序要紧：优先 html/body 上的声明（那才是全局正文行高），
    # 再退到 p/li 等元素级声明。
    lh_ratio = _pick_lh(("base",)) or _pick_lh(("body",))
    lh_heading = _pick_lh(("heading1", "heading"))

    head_first = first_family(heading_stack)
    body_first = first_family(body_stack)
    return {
        "heading_stack": heading_stack,
        "body_stack": body_stack,
        "code_stack": code_stack,
        "heading_char": trusted_char(heading_stack),
        "body_char": trusted_char(body_stack),
        "heading_char_raw": classify_stack(heading_stack),
        "first_family_heading": head_first,
        "first_family_body": body_first,
        "is_custom_heading_font": looks_custom_font(head_first),
        "is_custom_body_font": looks_custom_font(body_first),
        # 只看"标题字体/正文字体是不是衬线"，不看 CSS 里有没有出现过衬线族。
        # 否则带了一个没用上的 font-serif 工具类的站点会被误判成杂志风。
        "has_serif": (trusted_char(heading_stack) == "serif"
                      or trusted_char(body_stack) == "serif"),
        "has_mono": any(classify_stack(s) == "mono" for s, _ in stacks[:6]),
        # 等宽信号必须来自"第一族就是等宽"，而不是回退链里恰好有个 monospace。
        # RAND 的标题栈 fraktion, Lucida Console, Monaco, monospace 就是反例。
        "has_mono_primary": any(classify_stack(first_family(s) or "") == "mono"
                                for s, _ in stacks[:8]),
        "weights": sorted(weights, key=lambda k: int(k)),
        "weight_count": len(weights),
        "body_size": round(body_size, 1),
        "body_line_height": lh_ratio,
        "heading_line_height": lh_heading,
        "max_size": round(biggest, 1),
        "type_ratio": ratio,
        "scale": size_list[:14],
        "size_by_role": {r: max(d, key=lambda k: d[k])
                         for r, d in sizes_role.items() if d},
        "line_height_by_role": {r: round(max(d, key=lambda k: d[k]), 2)
                                for r, d in lh_role.items() if d},
        "letter_spacing": round(ls_sorted[0][0], 3) if ls_sorted else 0,
        "all_families": [s for s, _ in stacks[:6]],
    }


def _clean_family(val: str):
    v = (val or "").strip().strip('"').rstrip("!important").strip()
    if not v or len(v) > 200:
        return None
    if "var(" in v or "{" in v or "}" in v:
        return None  # 未解析成功的变量，宁缺毋滥
    v = re.sub(r"\s+", " ", v)
    # 去掉字体名两侧的引号。只 strip 首尾会留下 `Georgia",serif` 这种残缺串
    # （前引号被去掉、后引号还在），既难看又会破坏 style 属性。
    # CSS 允许不带引号的多词族名，去掉引号后仍可直接回填到 font-family。
    v = re.sub(r"[\"']", "", v)
    v = re.sub(r"\s*,\s*", ", ", v).strip(", ")
    if not v:
        return None
    # 只有通用关键字（如单独一个 "inherit"）没有信息量
    if v.lower() in ("inherit", "initial", "unset", "revert", "auto"):
        return None
    return v


def _px_values(val: str, allow_em=False, allow_unitless=False):
    out = []
    for m in re.finditer(r"([-+]?\d*\.?\d+)(px|rem|em|%)?", val.replace("!important", "")):
        num, unit = float(m.group(1)), m.group(2) or ""
        if unit == "px":
            out.append(num)
        elif unit == "rem" or unit == "em":
            if allow_em:
                out.append(round(num, 3))
            else:
                out.append(num * 16)
        elif unit == "" and allow_unitless:
            out.append(num)
    return out


def extract_rhythm(decls):
    """提取间距节奏 / 圆角 / 容器宽度 / 密度感。"""
    spacings = Counter()
    radii = Counter()
    maxw = Counter()
    prose = Counter()
    prose_fallback = Counter()
    weights = defaultdict(float)

    for prop, val, w, role, sel in decls:
        if prop.startswith(("margin", "padding")) or prop in ("gap", "row-gap", "column-gap"):
            for p in _px_values(val):
                if 1 <= p <= 200:
                    spacings[round(p)] += 1
                    weights[round(p)] += w
        elif prop == "border-radius":
            for p in _px_values(val):
                if 0 <= p <= 400:
                    radii[round(p)] += 1
        elif prop in ("max-width", "width"):
            for p in _px_values(val):
                if 400 <= p <= 2200:
                    maxw[round(p)] += 1
                    # 正文栏宽：只认"看起来就是给正文用的"宽度约束。
                    # 踩坑（RAND）：&>li{width:55.5rem}=888px 被当成正文栏宽 -> 111 字符 ->
                    # 误报"行宽过宽"。而真正的正文约束是 .constrain-width{width:41rem}=656px，
                    # 约 74 字符，完全舒适。用列表项/卡片/图片的宽度估行宽，结论必错。
                    # 用户实际阅读感受是"舒服"，这一条与他的体感冲突时就该回头查代码，而不是改判据。
                    sl = sel.lower()
                    # 类名本身就是明示（.constrain-width / .prose / .measure）时，
                    # 标签层面的 role 判定不该把它一票否决 —— 关键词比标签更有信息量。
                    strong_name = any(g in sl for g in ("constrain", "prose", "measure",
                                                        "measure-width", "reading", "text-width"))
                    if role in ("body", "base") or strong_name:
                        if any(b in sl for b in (" li", ">li", "ul", "ol", "nav", "card",
                                                 "thumb", "img", "aside", "footer",
                                                 "header", "menu", "tab", "chip")):
                            continue
                        if role == "base" or strong_name or any(g in sl for g in (
                                "text", "rich", "content",
                                "article", "entry", "copy", "paragraph", "lead", "intro",
                                "summary", "body")):
                            prose[p] += w * 3
                        else:
                            prose_fallback[p] += w

    # 基准单位：取最高频间距值的众数公约数
    common = [v for v, _ in spacings.most_common(12)]
    base_unit = 8
    if common:
        cands = [u for u in (4, 5, 6, 8, 10, 12, 16) if sum(1 for c in common if c % u == 0) >= max(2, len(common) // 2)]
        if cands:
            base_unit = sorted(cands, key=lambda u: -sum(weights[c] for c in common if c % u == 0))[0]

    radius_vals = sorted(radii)
    max_radius = max(radius_vals) if radius_vals else 0
    container = maxw.most_common(1)[0][0] if maxw else 1200
    _pw = prose.most_common(1) or prose_fallback.most_common(1)
    prose_width = _pw[0][0] if _pw else None

    top_space = [v for v, _ in spacings.most_common(10)]
    avg = sum(top_space) / len(top_space) if top_space else base_unit * 2
    density = "airy" if avg >= 28 else ("dense" if avg <= 12 else "normal")

    return {
        "base_unit": base_unit,
        "common_spacings": top_space,
        "max_radius": max_radius,
        "radius_style": ("pill" if max_radius >= 999 else
                         "rounded" if max_radius >= 12 else
                         "subtle" if max_radius >= 4 else "sharp"),
        "container_width": container,
        "prose_width": prose_width,
        "radius_values": radius_vals[:8],
        "avg_spacing": round(avg, 1),
        "density": density,
    }


def extract_effects(decls):
    """渐变 / 阴影 / 描边 / 背景图等风格强信号。"""
    gradient = 0
    shadow = 0
    glow = 0
    blur = 0
    pattern = 0
    border = 0
    shadow_down = 0
    shadow_up = 0
    for prop, val, w, role, sel in decls:
        low = val.lower()
        if prop in ("background-image", "background") or "background" in val.lower():
            if "gradient" in low:
                gradient += 1
            if "url(" in low:
                pattern += 1
        if prop.startswith("border") and not prop.startswith("border-radius"):
            if low.strip() not in ("none", "0", "0px"):
                border += 1
        if prop in ("box-shadow", "text-shadow"):
            if low.strip() not in ("none", "0", ""):
                shadow += 1
                # 真正的"发光"= 零偏移 + 带色阴影。原来只要出现 rgba() 就算发光，
                # 普通灰色投影全被误判成霓虹，科技风分数虚高。
                zero_offset = bool(re.match(r"\s*(inset\s+)?0(px)?\s+0(px)?(\s|,|$)", low))
                colored = bool(re.search(r"#[0-9a-f]{3,8}", low)) or bool(
                    re.search(r"rgba?\(\s*(?!0\s*,\s*0\s*,\s*0\s*[,)])", low))
                if zero_offset and colored:
                    glow += 1
                # 光源方向：Refactoring UI——"光来自上方"，投影应向下偏移。
                # 负向 y 偏移（阴影朝上）是违背物理直觉的，值得单独记录。
                nums = re.findall(r"(-?\d*\.?\d+)(?:px)?", re.sub(r"rgba?\([^)]*\)", "", low))
                if len(nums) >= 2:
                    try:
                        y = float(nums[1])
                        if y < 0:
                            shadow_up += 1
                        elif y > 0:
                            shadow_down += 1
                    except ValueError:
                        pass
        if "blur(" in low or "backdrop-filter" in prop:
            blur += 1
    return {"gradient": gradient, "shadow": shadow, "glow": glow,
            "blur": blur, "pattern": pattern, "border": border,
            "shadow_down": shadow_down, "shadow_up": shadow_up}


def extract_html_signals(soup: BeautifulSoup):
    """检测"前 CSS 时代"的 HTML 痕迹。

    1996 年的 Space Jam 官网、老企业站这类页面几乎不用 CSS，
    只看 CSS 会把它判成"极简风"。但它的复古感是真实存在的 ——
    藏在 <font>/<center>/<marquee>/bgcolor 这些早已废弃的标签里。
    """
    html_low = str(soup)[:400000].lower()
    sig = {
        "font_tag": len(soup.find_all("font")),
        "center_tag": len(soup.find_all("center")),
        "marquee_tag": len(soup.find_all("marquee")),
        "blink_tag": len(soup.find_all("blink")),
        "frameset": len(soup.find_all("frameset")) + len(soup.find_all("frame")),
        "bgcolor_attr": html_low.count("bgcolor="),
        "table_count": len(soup.find_all("table")),
        "spacer_gifs": sum(1 for i in soup.find_all("img")
                           if "spacer" in (i.get("src") or "").lower()),
        "table_attrs": len(soup.select("table[border],table[cellpadding],table[cellspacing]")),
        "html4_doctype": 1 if re.search(r"html 4\.0|html 4\.01|xhtml 1", html_low) else 0,
    }
    sig["old_school"] = (sig["font_tag"] + sig["center_tag"] + sig["marquee_tag"]
                         + sig["blink_tag"] + sig["frameset"]
                         + (1 if sig["bgcolor_attr"] >= 2 else 0)
                         + sig["table_attrs"] + sig["spacer_gifs"])
    return sig


# --------------------------------------------------------------------------
# 3. 正文提取（readability-lite）
# --------------------------------------------------------------------------

DROP_TAGS = ["script", "style", "noscript", "nav", "header", "footer", "aside",
             "form", "iframe", "svg", "canvas", "template", "button", "select"]


CARD_KINDS = ("Research", "Expert Insights", "Podcast", "Press", "Blog", "Commentary",
              "Report", "Article", "Video", "Brief", "Testimony", "Event")
DATE_RE = re.compile(
    r"\b(\d{4}[-/]\d{1,2}[-/]\d{1,2}|[A-Z][a-z]{2}\s+\d{1,2},\s+\d{4}|"
    r"\d{1,2}\s+[A-Z][a-z]{2}\s+\d{4})\b")


def extract_cards(soup: BeautifulSoup, base_url: str):
    """抽取"内容卡片"型页面（主题枢纽页 / 索引页）的卡片单元。

    盲区修复：RAND 的 AI 主题页正文段落只有 3 段，但页面上有 20+ 张内容卡片。
    纯文章抽取器会产出一张几乎为空的 DNA —— 而这类页面恰恰是"排版好看"的典型。
    卡片是这类页面的原子单元，不抽它就等于什么都没抽到。
    """
    cards, seen = [], set()
    sel = ("article, li, [class*=card], [class*=teaser], [class*=promo], "
           "[class*=result], [class*=item], [class*=entry]")
    for el in soup.select(sel):
        h = el.find(["h2", "h3", "h4", "h5"])
        if not h:
            continue
        title = re.sub(r"\s+", " ", h.get_text(" ", strip=True))
        if len(title) < 8 or title in seen:
            continue
        text = re.sub(r"\s+", " ", el.get_text(" ", strip=True))
        if len(text) > 900:
            continue  # 多半是外层容器而非单张卡
        link = el.find("a", href=True)
        m = DATE_RE.search(text)
        kind = None
        for k in CARD_KINDS:
            if re.search(r"\b" + re.escape(k) + r"\b", text, re.I):
                kind = k
                break
        seen.add(title)
        cards.append({
            "title": title[:160],
            "kind": kind,
            "date": m.group(1) if m else None,
            "href": urljoin(base_url, link["href"]) if link else None,
            "excerpt": text[:200],
            "has_image": bool(el.find("img") or el.find("picture")),
        })
    return cards[:40]


def extract_content(soup: BeautifulSoup, base_url: str):
    title = None
    for sel, attr in (('meta[property="og:title"]', "content"),
                      ('meta[name="twitter:title"]', "content")):
        el = soup.select_one(sel)
        if el and el.get(attr):
            title = el[attr].strip()
            break
    if not title and soup.h1:
        title = soup.h1.get_text(" ", strip=True)
    if not title and soup.title:
        title = soup.title.get_text(strip=True)

    dek = None
    for sel in ('meta[property="og:description"]', 'meta[name="description"]',
                'meta[name="twitter:description"]'):
        el = soup.select_one(sel)
        if el and el.get("content", "").strip():
            dek = el["content"].strip()
            break

    site = None
    el = soup.select_one('meta[property="og:site_name"]')
    if el and el.get("content"):
        site = el["content"].strip()
    if not site:
        host = urlparse(base_url).netloc
        site = host.replace("www.", "") if host else None

    cover = None
    el = soup.select_one('meta[property="og:image"]')
    if el and el.get("content"):
        cover = urljoin(base_url, el["content"])
    favicon = None
    for sel in ('link[rel~="icon"]', 'link[rel="shortcut icon"]',
                'link[rel="apple-touch-icon"]'):
        el = soup.select_one(sel)
        if el and el.get("href"):
            favicon = urljoin(base_url, el["href"])
            break

    author = None
    for sel in ('meta[name="author"]', 'meta[property="article:author"]'):
        el = soup.select_one(sel)
        if el and el.get("content"):
            author = el["content"].strip()
            break

    date = None
    for sel in ('meta[property="article:published_time"]', 'meta[name="date"]',
                'time[datetime]'):
        el = soup.select_one(sel)
        if el:
            date = el.get("content") or el.get("datetime")
            if date:
                date = date[:10]
                break

    work = BeautifulSoup(str(soup), "lxml")
    for tag in DROP_TAGS:
        for el in work.find_all(tag):
            el.decompose()
    for el in work.select("[class*=comment],[class*=sidebar],[class*=advert],[id*=comment]"):
        el.decompose()

    best, best_score = None, 0.0
    for el in work.find_all(["article", "main", "div", "section", "body"]):
        # 同时看 <p> 和 <li>：纯列表型页面（导航页/索引页/周报目录）
        # 正文全在 <li> 里，只看 <p> 会得到 0 段、DNA 直接空掉。
        blocks = el.find_all(["p", "li"], recursive=False) or el.find_all(["p", "li"])
        text_len = sum(len(b.get_text(" ", strip=True)) for b in blocks)
        if text_len < 60:
            continue
        link_len = sum(len(a.get_text(" ", strip=True)) for a in el.find_all("a"))
        score = text_len / (1 + len(el.find_all(True)) * 0.25)
        score *= 1 - min(0.6, link_len / max(text_len, 1))
        if el.name in ("article", "main"):
            score *= 1.35
        if score > best_score:
            best, best_score = el, score

    # 兜底 1：老式表格布局 / 图片型页面可能一个 <p>/<li> 都没有
    if best is None:
        best = work.body or work

    sections = []
    quotes = []
    numbers = []
    if best is not None:
        cur = {"heading": None, "texts": []}
        for node in best.find_all(["h2", "h3", "h4", "p", "blockquote", "li"], recursive=True):
            txt = node.get_text(" ", strip=True)
            txt = re.sub(r"\s+", " ", txt)
            if not txt:
                continue
            if node.name in ("h2", "h3", "h4"):
                if cur["heading"] or cur["texts"]:
                    sections.append(cur)
                cur = {"heading": txt[:120], "texts": []}
                for n in re.findall(r"\d[\d,.]*\s*(?:%|亿|万|倍|美元|元|个|家|年|天|bps|pp)?", txt):
                    if len(n) > 1:
                        numbers.append(n.strip())
            elif node.name == "blockquote":
                quotes.append(txt[:220])
            else:
                if len(txt) > 18:
                    cur["texts"].append(txt)
                for n in re.findall(r"\d[\d,.]*\s*(?:%|亿|万|倍|美元|元|个|家|年|天|bps|pp)", txt):
                    numbers.append(n.strip())
        if cur["heading"] or cur["texts"]:
            sections.append(cur)

    sections = [s for s in sections if s["texts"] or s["heading"]][:8]
    paragraphs = [t for s in sections for t in s["texts"]]

    # 兜底：完全没抓到时，退化成按长度切分纯文本，保证卡片永远有内容可排版
    if not paragraphs and best is not None:
        blob = re.sub(r"\s+", " ", best.get_text(" ", strip=True)).strip()
        if len(blob) > 60:
            chunks = [blob[i:i + 180] for i in range(0, min(len(blob), 900), 180)]
            sections = [{"heading": None, "texts": chunks}]
            paragraphs = chunks

    outline = []
    for h in work.find_all(["h1", "h2", "h3"]):
        t = re.sub(r"\s+", " ", h.get_text(" ", strip=True))
        if not t or len(t) < 2:
            continue
        # 紧邻重复行去噪：站点常把同一标题同时放进导航与正文（如 RAND 的两个 h1）
        if outline and outline[-1]["text"] == t[:100]:
            continue
        outline.append({"level": int(h.name[1]), "text": t[:100]})
    outline = outline[:22]

    all_text = " ".join(paragraphs)
    cjk = sum(1 for ch in all_text if "\u4e00" <= ch <= "\u9fff")
    cjk_ratio = round(cjk / max(len(all_text), 1), 3)

    cards = extract_cards(soup, base_url)
    if cards and len(cards) >= 6 and len(paragraphs) <= 8:
        page_type = "content_hub"
    elif len(paragraphs) >= 5:
        page_type = "article"
    elif cards:
        page_type = "listing"
    else:
        page_type = "unknown"

    return {
        "title": (title or "").strip()[:200],
        "dek": (dek or "").strip()[:300],
        "site": site,
        "author": author,
        "date": date,
        "cover": cover,
        "favicon": favicon,
        "sections": sections,
        "quotes": quotes[:4],
        "key_numbers": list(dict.fromkeys(numbers))[:12],
        "paragraph_count": len(paragraphs),
        "word_count": sum(len(p) for p in paragraphs),
        "lead": paragraphs[0][:400] if paragraphs else "",
        "cjk_ratio": cjk_ratio,
        "headings_outline": outline,
        "page_type": page_type,
        "cards": cards,
    }


# --------------------------------------------------------------------------
# 4. 风格归类（4 风格评分）
# --------------------------------------------------------------------------

STYLES = ("minimalist", "magazine", "tech", "retro")


def _adjacent_ratios(values):
    vs = sorted({v for v in values if v and v > 0})
    return [round(b / a, 3) for a, b in zip(vs, vs[1:])] if len(vs) > 1 else []


def audit_design(dna):
    """按四本书的可计算判据给页面做一次"排版 + 配色体检"。

    判据来源与出处：
    - Refactoring UI：行宽 45–75 字符、间距/字号阶梯相邻差不小于约 25%、
      字重不超过 2 档且不低于 400、灰阶需要带色温、光来自上方（阴影向下偏移）
    - Bringhurst《The Elements of Typographic Style》2.1.2 / 2.2.3：
      45–75 字符可接受、66 字符为理想行宽；无衬线字体需要更大行距或更短行宽
    - WCAG：正文（<18px）对比度 >= 4.5:1，大字号 >= 3:1

    诚实边界：光学对齐、基线对齐、留白心理感受这类需要渲染才能判断的项，
    静态解析无法验证，这里是"结构体检"而非"审美终审"。
    """
    pal, typ, rhy, eff = dna["palette"], dna["typography"], dna["rhythm"], dna["effects"]
    con = dna.get("content", {})
    checks = []

    def add(area, level, title, detail, source=""):
        checks.append({"area": area, "level": level, "title": title,
                       "detail": detail, "source": source})

    cjk = con.get("cjk_ratio") or 0

    # ---- 1. 行宽 measure ----
    pw = rhy.get("prose_width")
    cw, bs = rhy.get("container_width") or 0, typ.get("body_size") or 16
    if pw and bs and cjk < 0.3:
        # 西文平均字宽约 0.45–0.6em，随字面差异很大。用单点 0.5em 会在临界值上
        # 制造假警报（RAND 的 656px 正文栏就被误报过"过宽"）。改用区间判断。
        lo, hi = round(pw / (bs * 0.58)), round(pw / (bs * 0.50))
        if 45 <= lo and hi <= 75:
            add("排版", "ok", f"行宽约 {lo}–{hi} 字符（正文栏 {pw}px）",
                "落在 45–75 的最佳区间（理想 66 字符，Bringhurst 2.1.2）",
                "Bringhurst 2.1.2 / Refactoring UI")
        elif hi >= 45 and lo <= 75:
            add("排版", "ok", f"行宽约 {lo}–{hi} 字符（正文栏 {pw}px）",
                f"与 45–75 舒适区基本吻合，上限略高；实际取决于字体平均字宽"
                f"（此处按 0.45–0.6em 估算）。Bringhurst：66 字符为理想",
                "Bringhurst 2.1.2 / Refactoring UI")
        else:
            add("排版", "warn", f"行宽约 {lo}–{hi} 字符（正文栏 {pw}px）",
                "45–75 为安全区，66 为理想值；过窄频繁换行，过宽容易读串行",
                "Bringhurst 2.1.2")
    elif cw and bs and cjk < 0.3:
        # 诚实处理：拿不到正文栏宽就不要硬编一个数字。
        # RAND 第一次跑给出了"行宽 180 字符" —— 那是按页面容器 1440px 算的，
        # 而 Refactoring UI 明确说"段落宽度 ≠ 内容区宽度"。宁可说不知道。
        add("排版", "info", "行宽无法静态确定",
            f"页面容器 {cw}px，但未找到作用在 p/li/blockquote 上的宽度约束。"
            f"若按容器估算会得到 {round(cw / (bs * 0.5))} 字符 —— 该数字不可信，不予采信。"
            f"请在浏览器实测正文栏宽度", "Bringhurst 2.1.2 的适用边界")
    elif cw and bs and cjk >= 0.3:
        add("排版", "info", "中文页面，行宽判据需另行校准",
            f"西文 45–75 字符的规则不能直接套中文。中文单字即一个字符，"
            f"舒适区间通常 25–40 字/行。当前容器 {cw}px / 字号 {bs}px",
            "Bringhurst 2.1.2 的适用边界")

    # ---- 2. 行高 leading ----
    lh = typ.get("body_line_height")
    if lh:
        if lh < 1.35:
            lvl, msg = "bad", "行距过紧，长文易读串行"
        elif lh < 1.5:
            lvl, msg = "warn", "行距偏紧；无衬线字体比衬线字体更需要余量"
        elif lh <= 1.9:
            lvl, msg = "ok", "行距在舒适区间"
        else:
            lvl, msg = "warn", "行距过大，段落会散"
        extra = "（正文为无衬线，建议不低于 1.5）" if typ.get("body_char") == "sans" else ""
        add("排版", lvl, f"行高 {lh}", msg + extra, "Refactoring UI / Bringhurst")

    # ---- 3. 字号阶梯 ----
    gaps = _adjacent_ratios(typ.get("scale") or [])
    if gaps:
        tight = [g for g in gaps if g < 1.25]
        if tight:
            add("排版", "warn", f"字号阶梯有 {len(tight)} 处相邻差 <25%",
                "相邻字号如果看不出明显差别，就会变成'纠结 12px 还是 13px'。"
                "建议拉开到 1.25 倍以上", "Refactoring UI · Establish a type scale")
        else:
            add("排版", "ok", f"字号阶梯 {len(gaps)} 档，相邻差均 >=25%",
                "阶梯分段清晰，决策成本低", "Refactoring UI")

    # ---- 4. 字重档位 ----
    ws = [int(w) for w in (typ.get("weights") or []) if str(w).isdigit()]
    wc = typ.get("weight_count") or 0
    too_light = [w for w in ws if w < 400]
    if wc > 3 or too_light:
        add("排版", "warn", f"字重用了 {wc} 档" + (f"，含过轻字重 {too_light}" if too_light else ""),
            "界面通常 2 档就够（400/500 + 600/700）；低于 400 的字重在正文尺寸下难读，"
            "想弱化请改用更浅的颜色或更小的字号", "Refactoring UI · Size isn't everything")
    elif wc:
        add("排版", "ok", f"字重 {wc} 档", "克制得当", "Refactoring UI")

    # ---- 5. 间距阶梯 ----
    sgaps = _adjacent_ratios(rhy.get("common_spacings") or [])
    if sgaps:
        stight = [g for g in sgaps if g < 1.25]
        if stight:
            add("间距", "warn", f"间距阶梯有 {len(stight)} 处相邻差 <25%",
                "间距系统的意义在于'不用纠结'；相邻值太接近就失去意义",
                "Refactoring UI · Establish a spacing and sizing system")
        else:
            add("间距", "ok", f"间距阶梯相邻差均 >=25%", "可快速决策", "Refactoring UI")

    # ---- 6. 对比度 ----
    cr = pal.get("contrast_text_bg") or 0
    if cr >= 4.5:
        add("配色", "ok", f"正文对比度 {cr}:1", "达到 WCAG 正文标准（>=4.5:1）", "WCAG")
    elif cr >= 3:
        add("配色", "warn", f"正文对比度 {cr}:1",
            "只满足大字号标准（>=3:1）；正文尺寸下不足", "WCAG")
    else:
        add("配色", "bad", f"正文对比度 {cr}:1", "低于可读性下限，正文会很难读", "WCAG")

    # ---- 7. 灰阶色温 ----
    neutrals = [e for e in (pal.get("top_colors") or []) if e.get("neutral")]
    if neutrals:
        tinted = [e for e in neutrals if e.get("sat", 0) > 0.02]
        if not tinted:
            add("配色", "info", f"{len(neutrals)} 个中性色都是纯灰（饱和度 0）",
                "纯灰会显得生硬；给灰阶加 2–5% 的同色相饱和度即可获得冷/暖倾向",
                "Refactoring UI · Greys don't have to be grey")
        else:
            add("配色", "ok", f"{len(tinted)}/{len(neutrals)} 个中性色带色温",
                f"例如 {tinted[0]['hex']}（饱和度 {tinted[0].get('sat')}），灰阶有冷暖倾向",
                "Refactoring UI")

    # ---- 8. 品牌色 ----
    if pal.get("primary") == pal.get("text"):
        add("配色", "warn", "未检出品牌色",
            "整页只有墨色与灰阶，没有可识别的强调色；也可能是信号不足", "—")
    else:
        bp = pal.get("brand_palette") or []
        add("配色", "ok", f"品牌色 {pal.get('primary')}",
            f"检出 {len(bp)} 个候选品牌色（已排除近黑/近白：明度 0.18–0.85 且饱和度 >=0.28）",
            "Refactoring UI · Don't let lightness kill your saturation")

    if (pal.get("vivid_count") or 0) > 6:
        add("配色", "warn", f"高饱和色 {pal['vivid_count']} 个",
            "彩色过多会互相争夺注意力，层级会被稀释", "Refactoring UI · 层级优先")

    # ---- 9. 光影方向 ----
    if eff.get("shadow_up"):
        add("阴影", "warn", f"{eff['shadow_up']} 处阴影向上偏移",
            "光来自上方，投影应向下；向上偏移会违背直觉",
            "Refactoring UI · Emulate a light source")
    elif eff.get("shadow"):
        add("阴影", "ok", f"{eff['shadow']} 处阴影，方向一致向下",
            "光源方向统一", "Refactoring UI")

    # ---- 10. 边框使用 ----
    if eff.get("border", 0) > 0 and eff.get("border", 0) > eff.get("shadow", 0) * 3:
        add("分隔", "info", f"{eff['border']} 处边框、{eff.get('shadow', 0)} 处阴影",
            "边框偏多时可考虑改用阴影 / 两个层次的底色 / 直接加大间距来分隔",
            "Refactoring UI · Use fewer borders")

    ok = sum(1 for c in checks if c["level"] == "ok")
    warn = sum(1 for c in checks if c["level"] == "warn")
    bad = sum(1 for c in checks if c["level"] == "bad")
    judged = ok + warn + bad
    return {
        "checks": checks,
        "ok": ok, "warn": warn, "bad": bad,
        "grade": ("A" if judged and ok / judged >= 0.8 else
                  "B" if judged and ok / judged >= 0.6 else
                  "C" if judged and ok / judged >= 0.4 else "D") if judged else "—",
        "note": ("结构体检，非审美终审。两条边界：① 光学对齐、基线对齐、留白心理感受需渲染后才能判断；② 字号阶梯/字重档位/彩色数等项读的是 CSS 声明，设计系统完备的站点（如 RAND）会声明比页面实际使用更多的值，这类告警应按'站点可选范围偏宽'理解，而非'页面用得很乱'。"),
    }


def classify_style(dna):
    pal, typ, rhy, eff = dna["palette"], dna["typography"], dna["rhythm"], dna["effects"]
    bg = parse_color(pal["background"]) or (255, 255, 255)
    bg_h, bg_s, bg_l = rgb_to_hsl(bg)
    prim = parse_color(pal["primary"]) or (0, 0, 0)
    p_h, p_s, p_l = rgb_to_hsl(prim)
    n_vivid = pal["vivid_count"]

    ev = defaultdict(lambda: 0.05)  # 每项给一点基础分，避免全零导致归一化失真

    # --- 极简风 ---
    if n_vivid <= 3:
        ev["minimalist"] += 0.28
    if rhy["max_radius"] <= 6:
        ev["minimalist"] += 0.18
    if eff["gradient"] == 0:
        ev["minimalist"] += 0.14
    if eff["shadow"] <= 2:
        ev["minimalist"] += 0.12
    if bg_l > 0.9 and pal["contrast_text_bg"] >= 12:
        ev["minimalist"] += 0.20
    if p_s < 0.35:
        ev["minimalist"] += 0.12
    if typ["weight_count"] <= 3:
        ev["minimalist"] += 0.08
    if typ["has_serif"] and typ["body_char"] == "sans":
        ev["minimalist"] += 0.06
    if rhy["density"] == "airy":
        ev["minimalist"] += 0.08
    if eff["gradient"] > 0:
        ev["minimalist"] -= 0.22
    if n_vivid >= 6:
        ev["minimalist"] -= 0.18
    if bg_l < 0.3:
        ev["minimalist"] -= 0.30

    # --- 杂志风 ---
    if typ["has_serif"]:
        ev["magazine"] += 0.30
    if typ["type_ratio"] >= 2.4:
        ev["magazine"] += 0.24
    elif typ["type_ratio"] >= 1.9:
        ev["magazine"] += 0.12
    if pal["contrast_text_bg"] >= 14:
        ev["magazine"] += 0.16
    if dna["content"]["quotes"]:
        ev["magazine"] += 0.16
    if rhy["container_width"] >= 1100:
        ev["magazine"] += 0.08
    if typ["letter_spacing"] < 0:
        ev["magazine"] += 0.08
    if typ["body_char"] == "serif":
        ev["magazine"] += 0.14
    # 图片驱动的大图卡片矩阵是编辑型版面的强信号，但**必须绑定页面类型**。
    # 第一版只按"图多"给分，结果 Tailwind 文档页（大量截图）也被推成杂志风，
    # 造成回归。真正的区分点是"内容枢纽页 vs 长文页"，不是图片数量：
    #   RAND 主题页 = 3 段正文 + 20 张卡片 -> 编辑型枢纽
    #   Tailwind 博客 = 52 段正文 + 卡片配图 -> 长文页
    ptype = dna["content"].get("page_type")
    if eff.get("pattern", 0) >= 8 and ptype in ("content_hub", "listing"):
        ev["magazine"] += 0.24
    if ptype == "content_hub":
        ev["magazine"] += 0.12
    if typ.get("is_custom_heading_font"):
        ev["magazine"] += 0.10
    if bg_l < 0.35:
        ev["magazine"] -= 0.24
    if eff["gradient"] > 1:
        ev["magazine"] -= 0.12

    # --- 科技风 ---
    if bg_l < 0.28:
        ev["tech"] += 0.34
    if bg_l < 0.15:
        ev["tech"] += 0.10
    # 科技感的强调色集中在蓝/青/紫/绿区间。
    # 原写法 (p_h < 260 or p_h > 190) 是恒真条件 —— 等于给所有高饱和色加分，
    # 亮底杂志站会被误判成科技风。已修为明确的色相区间判断。
    tech_hue = (190 <= p_h <= 300) or (90 <= p_h <= 185)
    if p_s >= 0.4 and tech_hue:
        ev["tech"] += 0.26
    elif p_s >= 0.4:
        ev["tech"] += 0.04
    if eff["gradient"] >= 1:
        ev["tech"] += 0.14
    if eff["gradient"] >= 3:
        ev["tech"] += 0.10
    if eff["glow"] >= 1:
        ev["tech"] += 0.16
    if typ.get("has_mono_primary"):
        ev["tech"] += 0.14
    if 6 <= rhy["max_radius"] <= 20:
        ev["tech"] += 0.10
    if eff["blur"] >= 1:
        ev["tech"] += 0.08
    if bg_l > 0.9 and eff["gradient"] == 0 and p_s < 0.4:
        ev["tech"] -= 0.26
    if typ["body_char"] == "serif":
        ev["tech"] -= 0.14

    # --- 复古风 ---
    warm = (p_h <= 70 or p_h >= 345) and p_s <= 0.65
    if warm and n_vivid >= 1:
        ev["retro"] += 0.26
    # 米黄/奶咖这类"纸感底色"是复古信号，但现代极简站也爱用，
    # 所以只在色相偏暖时给分，并把权重从 0.26 降到 0.18，避免抢答。
    if 0.86 <= bg_l <= 0.97 and bg_s > 0.04 and (bg_h <= 90 or bg_h >= 330):
        ev["retro"] += 0.18
    if typ["has_serif"] and typ["body_char"] == "serif":
        ev["retro"] += 0.22
    if eff["pattern"] >= 1:
        ev["retro"] += 0.20
    if rhy["max_radius"] <= 4:
        ev["retro"] += 0.10
    if abs(typ["letter_spacing"]) >= 0.4:
        ev["retro"] += 0.10
    if p_s > 0.7:
        ev["retro"] -= 0.16
    if bg_l < 0.4:
        ev["retro"] -= 0.26
    # 前 CSS 时代的 HTML 痕迹（<font>/<center>/<marquee>/bgcolor）是复古风的铁证
    hs = dna.get("html_signals") or {}
    if hs.get("old_school", 0) >= 2:
        ev["retro"] += 0.55
        ev["minimalist"] -= 0.45
        ev["tech"] -= 0.35
    if hs.get("font_tag", 0) >= 3:
        ev["retro"] += 0.12
    if hs.get("frameset", 0) >= 1:
        ev["retro"] += 0.10

    # 亮底页面不该被判成科技风（科技感通常来自暗底 + 高饱和强调色 + 发光）
    if bg_l > 0.85:
        ev["tech"] -= 0.22

    # CSS 信号稀薄时（页面靠图片/外链样式成型），基于 CSS 的推断全部打折，
    # 只让 HTML 痕迹类证据（复古）保留强度 —— 否则 1996 年的图片站会被判成极简风。
    strength = (dna.get("meta") or {}).get("style_signal_strength", "moderate")
    if strength == "weak":
        for s in ("minimalist", "magazine", "tech"):
            ev[s] = 0.05 + (ev[s] - 0.05) * 0.5

    # 归一化成概率感（softmax-ish，便于阅读而非严格数学）
    raw = {k: max(0.01, min(1.0, v)) for k, v in ev.items()}
    total = sum(raw.values())
    probs = {k: round(v / total, 3) for k, v in raw.items()}
    winner = max(probs, key=probs.get)

    reasons = {
        "minimalist": f"{n_vivid}个彩色 / 圆角{rhy['max_radius']}px / 渐变{eff['gradient']}处 / 留白{rhy['density']}",
        "magazine": f"衬线{typ['has_serif']} / 字号比{typ['type_ratio']} / 引语{len(dna['content']['quotes'])}条",
        "tech": f"底色亮度{bg_l:.2f} / 强调色饱和{p_s:.2f} / 渐变{eff['gradient']} / 等宽{typ['has_mono']}",
        "retro": f"主色相{p_h:.0f}° 饱和{p_s:.2f} / 纸色底{bg_s > 0.04} / "
                 f"老式标签{(dna.get('html_signals') or {}).get('old_school', 0)}个",
    }
    strength = (dna.get("meta") or {}).get("style_signal_strength", "moderate")
    notes = []
    if strength == "weak":
        notes.append("该页 CSS 信号稀薄（可能靠外部样式表/图片成型），风格判定置信度按实际打折")
    if (dna.get("html_signals") or {}).get("old_school", 0) >= 2:
        notes.append("检测到前 CSS 时代的标签（<font>/<center>/bgcolor），风格判定以 HTML 痕迹为主")
    return {
        "style": winner,
        "confidence": probs[winner],
        "scores": probs,
        "evidence": reasons[winner],
        "all_evidence": reasons,
        "signal_strength": strength,
        "notes": notes,
        "template_ready": winner == "minimalist",
    }


# --------------------------------------------------------------------------
# 5. 主流程
# --------------------------------------------------------------------------

def extract_dna(src, fetch_css=True, download_images=False, out_dir=None):
    html, base_url = load_html(src)
    soup = BeautifulSoup(html, "lxml")

    sf = is_singlefile(html)
    css_text, inline_styles, n_links, n_fetched = collect_css(
        soup, base_url, fetch_remote=fetch_css and not sf and base_url.startswith("http")
    )
    rules = split_rules(css_text)
    decls = collect_declarations(rules, inline_styles)

    css_vars = {}
    for sel, decl in rules:
        if ":root" in sel or "html" in sel:
            for m in re.finditer(r"(--[-a-zA-Z0-9_]+)\s*:\s*([^;]+)", decl):
                css_vars[m.group(1)] = m.group(2).strip()

    # 统计"被真正引用过"的变量，并沿变量链传递两层
    # （--brand: var(--blue-500)，--blue-500 也要算用过）
    used_vars = set()
    for prop, val, w, role, sel in decls:
        used_vars.update(re.findall(r"var\(\s*(--[\w-]+)", val))
    for _ in range(2):
        for name in list(used_vars):
            for ref in re.findall(r"var\(\s*(--[\w-]+)", css_vars.get(name, "")):
                used_vars.add(ref)

    dna = {
        "meta": {
            "source": src,
            "base_url": base_url,
            "site": None,
            "title": None,
            "extracted_from": "singlefile" if sf else "live-html",
            "css_rules": len(rules),
            "css_declarations": len(decls),
            "external_css_found": n_links,
            "external_css_fetched": n_fetched,
        },
        "palette": extract_palette(decls, css_vars, used_vars),
        "typography": extract_typography(decls, css_vars),
        "rhythm": extract_rhythm(decls),
        "effects": extract_effects(decls),
        "html_signals": extract_html_signals(soup),
        "content": extract_content(soup, base_url),
    }
    dna["meta"]["site"] = dna["content"]["site"]
    dna["meta"]["title"] = dna["content"]["title"]
    dna["meta"]["style_signal_strength"] = (
        "strong" if len(decls) >= 400 else ("moderate" if len(decls) >= 40 else "weak")
    )
    dna["classification"] = classify_style(dna)
    dna["audit"] = audit_design(dna)
    return dna


def main():
    ap = argparse.ArgumentParser(description="提取网页视觉 DNA")
    ap.add_argument("src", help="URL 或本地 HTML 路径")
    ap.add_argument("-o", "--out", default=None, help="输出 dna.json 路径")
    ap.add_argument("--no-css", action="store_true", help="不抓取外链 CSS")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    dna = extract_dna(args.src, fetch_css=not args.no_css)

    if args.out:
        os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
        with open(args.out, "w", encoding="utf-8") as f:
            json.dump(dna, f, ensure_ascii=False, indent=2)

    if not args.quiet:
        p, t, r, c = dna["palette"], dna["typography"], dna["rhythm"], dna["classification"]
        print(f"来源      : {dna['meta']['extracted_from']}  ({dna['meta']['css_rules']} 条 CSS 规则)")
        print(f"标题      : {dna['content']['title']}")
        print(f"配色      : 底 {p['background']} / 字 {p['text']} / 主 {p['primary']} / 辅 {p['accent']}")
        print(f"          对比度 {p['contrast_text_bg']}:1, 彩色数 {p['vivid_count']}")
        print(f"字体      : 标题[{t['heading_char']}] {t['heading_stack'][:60]}")
        print(f"          正文[{t['body_char']}] {t['body_stack'][:60]}")
        print(f"排版节奏  : 基准 {r['base_unit']}px, 圆角 {r['radius_style']}({r['max_radius']}px), "
              f"容器 {r['container_width']}px, 密度 {r['density']}")
        print(f"风格归属  : {c['style']}  置信 {c['confidence']}   {c['scores']}")
        print(f"          依据: {c['evidence']}   [样式信号:{c['signal_strength']}]")
        for note in c["notes"]:
            print(f"          注意: {note}")
        print(f"内容      : {dna['content']['paragraph_count']} 段 / {dna['content']['word_count']} 字 / "
              f"{len(dna['content']['sections'])} 个小节 / 关键数字 {len(dna['content']['key_numbers'])} 个")
        print(f"页面类型  : {dna['content'].get('page_type')}  "
              f"(卡片 {len(dna['content'].get('cards') or [])} 张, 中文占比 {dna['content'].get('cjk_ratio')})")
        a = dna.get("audit") or {}
        if a:
            print(f"体检      : 等级 {a['grade']}  [OK]{a['ok']} [!]{a['warn']} [X]{a['bad']}")
            for c in a["checks"]:
                if c["level"] in ("warn", "bad"):
                    mark = "[!]" if c["level"] == "warn" else "[X]"
                    print(f"            {mark} [{c['area']}] {c['title']} — {c['detail']}")
    return dna


if __name__ == "__main__":
    main()
