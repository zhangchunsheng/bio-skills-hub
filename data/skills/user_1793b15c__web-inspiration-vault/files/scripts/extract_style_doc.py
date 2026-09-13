#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
extract_style_doc.py — 一个链接 -> 一份「排版风格档案」（Markdown），并纳入资产库管理
==================================================================================
用法：
    # 建档（URL 或本地 SingleFile HTML 均可）
    python extract_style_doc.py <URL 或 本地.html> --library <资产库目录>
    python extract_style_doc.py <URL> --library <dir> --style-name 赛博风   # 手动指定风格名
    python extract_style_doc.py --reindex --library <dir>                  # 从已有档案重建索引

资产库结构：
    <library>/
      INDEX.md                     人读索引：按风格分区，含体检等级与复现次数
      assets.json                  机器读清单：URL 哈希、首次/最近提取、修订次数
      <风格>-<站点>.md              风格档案（front-matter + 七节正文）
      dna/<id>.json                原始 DNA，供程序再消费
      _history/<名>.<时间戳>.md     同一 URL 重提取时，旧版自动归档到此

设计原则：
1. 档案里**不写假数字**。拿不到的项（hover 动效、渲染后几何、光学对齐）
   统一进「六、静态不可得的项」，明说为什么拿不到。
2. 风格名进文件名，便于按风格检索（杂志风-rand.org.md）。
3. 同一 URL 重复建档 = 修订，不新建重复文件；旧版进 _history，修订次数记账。
"""

from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import os
import re
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import extract_dna as E              # noqa: E402
from render_card import STYLE_NAMES  # noqa: E402

MANIFEST = "assets.json"
INDEX = "INDEX.md"
HISTORY_DIR = "_history"
DNA_DIR = "dna"

LEVEL_ZH = {"ok": "通过", "warn": "注意", "bad": "问题", "info": "提示"}
PAGE_TYPE_ZH = {
    "article": "长文页", "content_hub": "内容枢纽页",
    "listing": "索引页", "unknown": "未知",
}


# --------------------------------------------------------------------------
# 命名与元数据
# --------------------------------------------------------------------------

def domain_of(url: str, base_url: str = "") -> str:
    src = url or base_url or ""
    m = re.match(r"^https?://([^/]+)", src)
    if m:
        return re.sub(r"[^a-z0-9.-]", "-", m.group(1).lower().replace("www.", ""))
    return "local-file"


def style_label(dna, override=None):
    """风格显示名。override 允许手动指定（如"赛博风"）。"""
    if override:
        return override, "manual"
    cls = dna.get("classification") or {}
    sid = cls.get("style") or "minimalist"
    conf = float(cls.get("confidence") or 0)
    name = STYLE_NAMES.get(sid, sid)
    # 置信度太低时不硬贴标签，避免资产库里出现一堆"看似确定"的错误归类
    if conf < 0.40:
        return f"未定风({name})", sid
    return name, sid


def style_slug(label: str, sid: str) -> str:
    mapping = {"极简风": "minimalist", "杂志风": "magazine", "科技风": "tech", "复古风": "retro"}
    if label in mapping:
        return mapping[label]
    return re.sub(r"[^a-z0-9-]+", "-", (sid or "style").lower()).strip("-") or "style"


def url_hash(url: str) -> str:
    return hashlib.sha1((url or "").encode("utf-8")).hexdigest()[:10]


def now_str():
    return _dt.datetime.now().strftime("%Y-%m-%d %H:%M")


# --------------------------------------------------------------------------
# Markdown 档案生成
# --------------------------------------------------------------------------

def _kv_table(rows, head=("项", "值")):
    if not rows:
        return []
    out = [f"| {head[0]} | {head[1]} |", "|---|---|"]
    out += [f"| {a} | {b} |" for a, b in rows]
    out.append("")
    return out


def build_markdown(dna, style_name, sid, src_label, revision, meta_extra=None):
    pal = dna.get("palette", {})
    typ = dna.get("typography", {})
    rhy = dna.get("rhythm", {})
    eff = dna.get("effects", {})
    con = dna.get("content", {})
    cls = dna.get("classification", {})
    aud = dna.get("audit", {}) or {}
    meta = dna.get("meta", {})
    dom = domain_of(dna.get("meta", {}).get("source"), meta.get("base_url"))
    prefix = re.sub(r"[^a-z0-9]+", "", dom.split(".")[0]) or "site"
    url = meta.get("base_url") or ""

    title = con.get("title") or "(无标题)"
    ptype = con.get("page_type") or "unknown"
    cards = con.get("cards") or []

    L = []
    add = L.append

    # ---- front-matter（机器可读）----
    add("---")
    add(f"id: {style_slug(style_name, sid)}-{dom}")
    add(f"风格: {style_name}")
    add(f"风格ID: {sid}")
    add(f"置信度: {cls.get('confidence')}")
    add(f"页面类型: {ptype}")
    add(f"体检等级: {aud.get('grade')}")
    add(f"站点: {con.get('site') or dom}")
    add(f"标题: {json.dumps(title, ensure_ascii=False)}")
    add(f"来源: {url}")
    add(f"URL哈希: {url_hash(url)}")
    add(f"修订: {revision}")
    add(f"提取工具: web-inspiration-vault/scripts/extract_style_doc.py")
    add(f"提取时间: {now_str()}")
    if meta_extra:
        for k, v in meta_extra.items():
            add(f"{k}: {v}")
    add("---")
    add("")

    add(f"# {con.get('site') or dom} · {title}")
    add("")
    add(f"> **{style_name}**　{cls.get('evidence') or ''}")
    add("")

    # ---- 一、页面结构总览 ----
    add("## 一、页面结构总览")
    add("")
    add(f"- 页面类型：{PAGE_TYPE_ZH.get(ptype, ptype)}（`{ptype}`）")
    add(f"- 内容卡片：{len(cards)} 张")
    add(f"- 正文段落：{con.get('paragraph_count')} 段 / 约 {con.get('word_count')} 字")
    add(f"- 中文占比：{con.get('cjk_ratio')}")
    add(f"- 标题大纲：{len(con.get('headings_outline') or [])} 项（下列为真实抽取，非推断）")
    add("")
    outline = con.get("headings_outline") or []
    if outline:
        add("```text")
        for h in outline[:18]:
            add("  " * (h["level"] - 1) + f"- h{h['level']} {h['text']}")
        add("```")
        add("")

    # ---- 二、设计语言量化提取 ----
    add("## 二、设计语言量化提取")
    add("")
    add("### 2.1 色彩体系")
    add("")
    rows = [
        ("背景", f"`{pal.get('background')}`"),
        ("卡片面", f"`{pal.get('surface')}`"),
        ("正文", f"`{pal.get('text')}`"),
        ("弱化文字", f"`{pal.get('text_muted')}`"),
        ("主强调（品牌色）", f"`{pal.get('primary')}`"),
        ("次强调", f"`{pal.get('accent')}`"),
        ("描边", f"`{pal.get('border')}`"),
        ("正文/底色对比度", f"{pal.get('contrast_text_bg')}:1（WCAG 正文需 >=4.5:1）"),
        ("页面在用色数", f"{pal.get('palette_size')} 个（其中高饱和 {pal.get('vivid_count')} 个）"),
    ]
    L += _kv_table(rows)

    declared = pal.get("css_vars") or {}
    if declared:
        add(f"**站点自报设计 token**（源码 `:root` 变量，{len(declared)} 个，以下为实际被引用的）")
        add("")
        add("| 变量名 | 值 |")
        add("|---|---|")
        for k, v in list(declared.items())[:24]:
            add(f"| `{k}` | `{v}` |")
        add("")
        add("> 有自报 token 的站点，配色结论是**读出来的**而非推断的，可信度最高。")
        add("")

    brand = pal.get("brand_palette") or []
    if brand:
        add("**品牌色候选**（已排除近黑/近白：明度 0.18–0.85 且饱和度 >=0.28）")
        add("")
        add("| HEX | 色相 | 饱和度 | 明度 | 担当角色 |")
        add("|---|---|---|---|---|")
        for b in brand:
            add(f"| `{b['hex']}` | {b['hue']}° | {b['sat']} | {b['light']} | {', '.join(b['roles'][:4])} |")
        add("")

    add("### 2.2 字体层级")
    add("")
    sizes = typ.get("size_by_role") or {}
    lh_role = typ.get("line_height_by_role") or {}
    rows = [
        ("标题栈", f"`{typ.get('heading_stack')}`"),
        ("正文栈", f"`{typ.get('body_stack')}`"),
        ("标题族系", f"{typ.get('heading_char')}"
                     + ("（品牌自定义字体，族系未知，未从回退链硬猜）" if typ.get("is_custom_heading_font") else "")),
        ("正文族系", f"{typ.get('body_char')}"
                     + ("（品牌自定义字体，族系未知）" if typ.get("is_custom_body_font") else "")),
        ("正文行高", f"{typ.get('body_line_height') or '未声明'}"),
        ("字重档位", f"{typ.get('weight_count')} 档：{typ.get('weights')}"),
        ("声明字号阶梯", f"{typ.get('scale')}"),
        ("最大字号/正文比", f"{typ.get('type_ratio')}（{typ.get('max_size')}px / {typ.get('body_size')}px）"),
    ]
    L += _kv_table(rows)
    if sizes:
        add("| 元素 | 元素级字号 | 元素级行高 |")
        add("|---|---|---|")
        for role, size in sizes.items():
            add(f"| {role} | {size}px | {lh_role.get(role, '—')} |")
        add("")
        add("> 元素级字号来自 `h1/h2/p` 这类选择器；工具类站点的展示型大标题常写在 class 上，"
            "因此「声明字号阶梯」的最大值会高于元素级值，两者需分别看。")
        add("")

    add("### 2.3 栅格与版心")
    add("")
    L += _kv_table([
        ("容器宽度", f"{rhy.get('container_width')}px"),
        ("正文栏宽", f"{rhy.get('prose_width')}px" if rhy.get("prose_width")
                     else "未单独约束（段落宽度应独立于内容区宽度）"),
        ("节奏基准单位", f"{rhy.get('base_unit')}px"),
        ("圆角", f"{rhy.get('radius_style')}（{rhy.get('max_radius')}px）"),
        ("留白密度", f"{rhy.get('density')}（平均间距 {rhy.get('avg_spacing')}px）"),
        ("字距", f"{typ.get('letter_spacing')}px"),
    ])

    add("### 2.4 效果信号")
    add("")
    L += _kv_table([
        ("渐变", f"{eff.get('gradient')} 处"),
        ("阴影", f"{eff.get('shadow')} 处（向下 {eff.get('shadow_down')} / 向上 {eff.get('shadow_up')}）"),
        ("发光", f"{eff.get('glow')} 处"),
        ("模糊", f"{eff.get('blur')} 处"),
        ("背景图/纹理", f"{eff.get('pattern')} 处"),
        ("边框", f"{eff.get('border')} 处"),
    ])

    # ---- 三、内容卡片原子 ----
    add("## 三、内容卡片原子")
    add("")
    if cards:
        kinds = {}
        for c in cards:
            kinds[c.get("kind") or "未标注类型"] = kinds.get(c.get("kind") or "未标注类型", 0) + 1
        add(f"共 {len(cards)} 张。类型分布：" + "、".join(f"{k} x{v}" for k, v in kinds.items()))
        add("")
        add("| 类型 | 标题 | 日期 | 带图 |")
        add("|---|---|---|---|")
        for c in cards[:20]:
            t = (c.get("title") or "").replace("|", "/")
            add(f"| {c.get('kind') or '—'} | {t[:70]} | {c.get('date') or '—'} | {'是' if c.get('has_image') else '否'} |")
        add("")
    else:
        add("本页不是卡片矩阵型页面，未抽取到内容卡片。")
        add("")

    # ---- 四、设计体检 ----
    add("## 四、设计体检")
    add("")
    add(f"等级 **{aud.get('grade')}**　通过 {aud.get('ok')} / 注意 {aud.get('warn')} / 问题 {aud.get('bad')}")
    add("")
    if aud.get("checks"):
        add("| 级别 | 项目 | 结论 | 出处 |")
        add("|---|---|---|---|")
        for c in aud["checks"]:
            d = (c.get("detail") or "").replace("|", "/")
            add(f"| {LEVEL_ZH.get(c['level'], c['level'])} | {c['title']} | {d} | {c.get('source') or '—'} |")
        add("")
    if aud.get("note"):
        add(f"> {aud['note']}")
        add("")

    # ---- 五、可复用 CSS 变量 ----
    add("## 五、可复用 CSS 变量（可直接复制）")
    add("")
    add("```css")
    add(f"/* {con.get('site') or dom} · {style_name} · {now_str()} 提取 */")
    add(":root {")
    add(f"  /* 配色 */")
    add(f"  --{prefix}-bg: {pal.get('background')};")
    add(f"  --{prefix}-surface: {pal.get('surface')};")
    add(f"  --{prefix}-text: {pal.get('text')};")
    add(f"  --{prefix}-text-muted: {pal.get('text_muted')};")
    add(f"  --{prefix}-primary: {pal.get('primary')};")
    add(f"  --{prefix}-accent: {pal.get('accent')};")
    add(f"  --{prefix}-border: {pal.get('border')};")
    add(f"  /* 字体 */")
    add(f"  --{prefix}-font-heading: {typ.get('heading_stack')};")
    add(f"  --{prefix}-font-body: {typ.get('body_stack')};")
    add(f"  /* 字号 */")
    add(f"  --{prefix}-fs-body: {typ.get('body_size')}px;")
    if sizes.get("heading1"):
        add(f"  --{prefix}-fs-h1: {sizes['heading1']}px;")
    if sizes.get("heading"):
        add(f"  --{prefix}-fs-h2: {sizes['heading']}px;")
    add(f"  /* 行高 */")
    add(f"  --{prefix}-lh-body: {typ.get('body_line_height') or 1.5};")
    if lh_role.get("heading1"):
        add(f"  --{prefix}-lh-h1: {lh_role['heading1']};")
    add(f"  /* 版心与节奏 */")
    add(f"  --{prefix}-container: {rhy.get('container_width')}px;")
    if rhy.get("prose_width"):
        add(f"  --{prefix}-prose: {rhy.get('prose_width')}px;")
    add(f"  --{prefix}-unit: {rhy.get('base_unit')}px;")
    add(f"  --{prefix}-radius: {rhy.get('max_radius')}px;")
    add(f"  --{prefix}-max-measure: 66ch;   /* Bringhurst：66 字符为理想行宽 */")
    add("}")
    add("```")
    add("")

    # ---- 六、静态不可得的项 ----
    add("## 六、静态不可得的项（诚实边界）")
    add("")
    add("以下项目**静态解析拿不到**，不要把它们当已确认的事实：")
    add("")
    add("- 交互态：hover / focus / active 的样式变化、过渡与动画曲线")
    add("- 渲染后几何：元素真实宽高、基线对齐、光学对齐、垂直居中的实际效果")
    add("- 视口相关：响应式断点下的实际布局（CSS 里的 `@media` 只能证明写了，不能证明生效）")
    add("- 字体真实形态：只记录字体栈与族系；未内嵌字体文件，卡片样例走系统回退")
    add("- JS 注入样式：客户端渲染后新增的样式（如需此项，改走浏览器插件 SingleFile 存档再解析）")
    add("")

    # ---- 七、复用与复现 ----
    add("## 七、复用与复现")
    add("")
    add("```bash")
    add("# 复现本档案")
    add(f"python extract_style_doc.py \"{url or src_label}\" --library <本库目录>")
    add("")
    add("# 由本库生成统一风格的灵感卡与单文件灵感库")
    add("python build_vault.py <本库>/dna -o vault.html --emit-cards")
    add("```")
    add("")
    add(f"- 原始 DNA：`dna/{style_slug(style_name, sid)}-{dom}.json`")
    add(f"- 同风格其它档案：见 `INDEX.md` 的「{style_name}」分区")
    add(f"- URL 哈希：`{url_hash(url)}`（用于去重与修订追踪）")
    add("")

    return "\n".join(L)


# --------------------------------------------------------------------------
# 资产库管理
# --------------------------------------------------------------------------

def load_manifest(lib):
    p = os.path.join(lib, MANIFEST)
    if os.path.isfile(p):
        try:
            with open(p, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"version": 1, "library": lib, "entries": []}


def save_manifest(lib, man):
    man["updated"] = now_str()
    man["count"] = len(man["entries"])
    by = {}
    for e in man["entries"]:
        by[e["style"]] = by.get(e["style"], 0) + 1
    man["by_style"] = by
    with open(os.path.join(lib, MANIFEST), "w", encoding="utf-8") as f:
        json.dump(man, f, ensure_ascii=False, indent=2)


def write_index(lib, man):
    entries = man["entries"]
    lines = [
        "# 网页风格资产库",
        "",
        f"共 **{len(entries)}** 份档案　·　最后更新 {man.get('updated', '')}",
        "",
        "> 每份档案都是对原页面的**结构化理解**（配色 / 字体 / 版心 / 结构 / 体检），"
        "不是截图。可搜索、可 diff、可复用 `:root` 变量。",
        "",
    ]
    groups = {}
    for e in entries:
        groups.setdefault(e["style"], []).append(e)
    for style in sorted(groups, key=lambda s: (-len(groups[s]), s)):
        g = sorted(groups[style], key=lambda e: e.get("title") or "")
        lines.append(f"## {style}（{len(g)}）")
        lines.append("")
        lines.append("| 档案 | 站点 | 标题 | 页面类型 | 置信 | 体检 | 修订 | 最近提取 |")
        lines.append("|---|---|---|---|---|---|---|---|")
        for e in g:
            t = (e.get("title") or "").replace("|", "/")[:44]
            lines.append(
                f"| [`{e['file']}`]({e['file']}) | {e['domain']} | {t} | "
                f"{PAGE_TYPE_ZH.get(e.get('page_type'), e.get('page_type'))} | "
                f"{e.get('confidence')} | {e.get('grade')} | {e.get('revisions', 1)} | "
                f"{e.get('last_seen', '')} |")
        lines.append("")
    lines += [
        "## 说明",
        "",
        "- `assets.json` 是机器可读清单（含 URL 哈希与修订记录），供程序消费。",
        "- 同一 URL 重复建档视为**修订**：旧版自动移入 `_history/`，`修订`列记账。",
        "- 风格名由 4 类评分自动判定，置信度低于 0.40 会标为 `未定风(某风)` 而**不硬贴标签**；"
        "也可建档时用 `--style-name` 手动指定（例如 `赛博风`）。",
        "- 静态解析拿不到的项（hover 动效、渲染后几何、光学对齐）统一列在每份档案的第六节，"
        "**不编数字**。",
        "",
    ]
    with open(os.path.join(lib, INDEX), "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def archive(lib, src, out_path, style_name, sid, dna, revision):
    """建档并更新清单。返回 (md路径, manifest entry)。"""
    os.makedirs(lib, exist_ok=True)
    os.makedirs(os.path.join(lib, HISTORY_DIR), exist_ok=True)
    os.makedirs(os.path.join(lib, DNA_DIR), exist_ok=True)

    url = dna.get("meta", {}).get("base_url") or ""
    dom = domain_of(dna.get("meta", {}).get("source"), url)
    slug = f"{style_slug(style_name, sid)}-{dom}"
    md_path = os.path.join(lib, f"{style_name}-{dom}.md")

    man = load_manifest(lib)
    prev = next((e for e in man["entries"] if e.get("url_hash") == url_hash(url)), None)
    if prev and prev.get("revisions"):
        revision = prev["revisions"] + 1

    # 旧版归档（资产管理的核心：可回溯，不覆盖）
    if prev and os.path.isfile(md_path):
        ts = _dt.datetime.now().strftime("%Y%m%d-%H%M%S")
        shutil.move(md_path, os.path.join(lib, HISTORY_DIR, f"{slug}.{ts}.md"))

    md = build_markdown(dna, style_name, sid, src, revision)
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md)

    dna_path = os.path.join(lib, DNA_DIR, f"{slug}.json")
    with open(dna_path, "w", encoding="utf-8") as f:
        json.dump(dna, f, ensure_ascii=False, indent=2)

    aud = dna.get("audit") or {}
    entry = {
        "id": slug,
        "style": style_name,
        "style_id": sid,
        "domain": dom,
        "title": (dna.get("content") or {}).get("title"),
        "url": url,
        "url_hash": url_hash(url),
        "file": os.path.basename(md_path),
        "dna_file": f"{DNA_DIR}/{slug}.json",
        "page_type": (dna.get("content") or {}).get("page_type"),
        "confidence": (dna.get("classification") or {}).get("confidence"),
        "grade": aud.get("grade"),
        "cards": len((dna.get("content") or {}).get("cards") or []),
        "revisions": revision,
        "first_seen": (prev or {}).get("first_seen") or now_str(),
        "last_seen": now_str(),
    }
    man["entries"] = [e for e in man["entries"] if e.get("url_hash") != entry["url_hash"]]
    man["entries"].append(entry)
    man["entries"].sort(key=lambda e: (e.get("style") or "", e.get("domain") or ""))
    save_manifest(lib, man)
    write_index(lib, man)
    return md_path, entry


def reindex(lib):
    """从磁盘上已有的 .md 档案重建 INDEX.md 与 assets.json（档案被手工增删后使用）。"""
    man = load_manifest(lib)
    known = {e["file"] for e in man["entries"]}
    added = 0
    for fn in sorted(os.listdir(lib)):
        if not fn.endswith(".md") or fn == INDEX or fn in known:
            continue
        path = os.path.join(lib, fn)
        try:
            head = open(path, "r", encoding="utf-8").read(2000)
        except Exception:
            continue
        def fm(key):
            m = re.search(rf"^{key}:\s*(.+)$", head, re.M)
            return m.group(1).strip() if m else None
        if not fm("id"):
            continue
        man["entries"].append({
            "id": fm("id"), "style": fm("风格"), "style_id": fm("风格ID"),
            "domain": fm("站点"), "title": (fm("标题") or "").strip('"'),
            "url": fm("来源"), "url_hash": fm("URL哈希"), "file": fn,
            "page_type": fm("页面类型"), "confidence": fm("置信度"),
            "grade": fm("体检等级"), "revisions": int(fm("修订") or 1),
            "first_seen": fm("提取时间"), "last_seen": fm("提取时间"),
            "reindexed": True,
        })
        added += 1
    save_manifest(lib, man)
    write_index(lib, man)
    return len(man["entries"]), added


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description="链接 -> 风格档案（Markdown）并纳入资产库")
    ap.add_argument("src", nargs="?", help="URL 或本地 HTML 路径")
    ap.add_argument("--library", required=True, help="资产库目录")
    ap.add_argument("--style-name", default=None,
                    help="手动指定风格名（如 赛博风）；不传则用自动评分结果")
    ap.add_argument("--no-css", action="store_true", help="不抓取外链 CSS")
    ap.add_argument("--reindex", action="store_true", help="只从已有档案重建索引")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    if args.reindex:
        total, added = reindex(args.library)
        if not args.quiet:
            print(f"索引已重建：{total} 份档案（新收录 {added} 份）")
            print(f"  {os.path.join(args.library, INDEX)}")
            print(f"  {os.path.join(args.library, MANIFEST)}")
        return

    if not args.src:
        raise SystemExit("[!] 需要提供 URL 或本地 HTML 路径（或用 --reindex）")

    dna = E.extract_dna(args.src, fetch_css=not args.no_css)
    style_name, sid = style_label(dna, args.style_name)
    md_path, entry = archive(args.library, args.src, None, style_name, sid, dna, 1)

    if not args.quiet:
        print(f"档案    : {md_path}")
        print(f"风格    : {style_name}（{sid}）  置信 {entry['confidence']}")
        print(f"体检    : {entry['grade']}   页面类型 {entry['page_type']}   卡片 {entry['cards']} 张")
        print(f"修订    : 第 {entry['revisions']} 次")
        print(f"索引    : {os.path.join(args.library, INDEX)}")
    return entry


if __name__ == "__main__":
    main()
