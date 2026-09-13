#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fetch_page.py — 入口一：把在线页面抓到本地，并**如实告知这次抓取的可信度**
==========================================================================
用法：
    python fetch_page.py <URL> [-o saved.html] [--dir raw/]

为什么需要这一步：抽取质量取决于"拿到的 HTML 里到底有没有样式和正文"。
纯静态站一次就能拿全；SPA / 需登录 / 反爬站会拿到一个空壳 ——
此时应改用浏览器插件 SingleFile 存成单文件 HTML，再交给 extract_dna.py。
本脚本会明确告诉你落在哪种情况，而不是让你拿到烂数据却不知道。

SingleFile：https://github.com/gildas-lormeau/SingleFile
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from urllib.parse import urlparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from extract_dna import UA, is_singlefile  # noqa: E402

try:
    import requests
except ImportError:
    requests = None
from bs4 import BeautifulSoup


def assess(html: str):
    """判断这次抓取是否"抓全了"。"""
    soup = BeautifulSoup(html, "lxml")
    for t in soup(["script", "style", "noscript"]):
        t.decompose()
    text_len = len(re.sub(r"\s+", "", soup.get_text(" ", strip=True)))
    n_style = len(re.findall(r"<style", html, re.I))
    n_link = len(re.findall(r'rel=["\']?stylesheet', html, re.I))
    n_p = len(soup.find_all("p"))
    has_body_content = text_len > 800

    if not has_body_content and len(html) > 60_000:
        verdict = "js-shell"
        advice = ("疑似 SPA / 客户端渲染，或内容需登录。请用浏览器插件 SingleFile 存成单页 HTML "
                  "后再跑 extract_dna.py。")
    elif n_style == 0 and n_link == 0:
        verdict = "no-css"
        advice = ("页面没有内联样式也没有外链样式表，视觉 DNA 只能靠 HTML 标签推断"
                  "（如老式 <font>/bgcolor），配色/节奏结论可信度低。建议改用 SingleFile 留档。")
    else:
        verdict = "ok"
        advice = "抓取完整，可直接进入 extract_dna.py。"
    return {
        "verdict": verdict, "advice": advice, "text_len": text_len,
        "style_tags": n_style, "css_links": n_link, "paragraphs": n_p,
    }


def fetch(url, out_path=None, out_dir="raw"):
    if requests is None:
        raise SystemExit("[!] 需要 requests。")
    r = requests.get(url, headers=UA, timeout=40)
    r.raise_for_status()
    if not r.encoding or r.encoding.lower() in ("iso-8859-1", "ascii"):
        r.encoding = r.apparent_encoding or "utf-8"
    html = r.text

    if not out_path:
        os.makedirs(out_dir, exist_ok=True)
        host = urlparse(url).netloc.replace(":", "_")
        name = re.sub(r"[^\w-]+", "_", urlparse(url).path).strip("_")[:60] or "index"
        out_path = os.path.join(out_dir, f"{host}__{name}.html")
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)

    info = assess(html)
    info.update({"url": url, "status": r.status_code, "bytes": len(html.encode("utf-8")),
                 "saved": out_path, "looks_singlefile": is_singlefile(html)})
    return info


def main():
    ap = argparse.ArgumentParser(description="抓取页面到本地并评估可信度")
    ap.add_argument("url")
    ap.add_argument("-o", "--out", default=None)
    ap.add_argument("--dir", default="raw")
    args = ap.parse_args()

    info = fetch(args.url, args.out, args.dir)
    print(f"状态      : {info['status']}   {info['bytes'] / 1024:.1f} KB")
    print(f"已保存    : {info['saved']}")
    print(f"正文长度  : {info['text_len']} 字（{info['paragraphs']} 个 <p>）")
    print(f"样式来源  : <style> {info['style_tags']} 个 / 外链 CSS {info['css_links']} 个")
    print(f"抓取结论  : {info['verdict']}")
    print(f"下一步    : {info['advice']}")
    if info["looks_singlefile"]:
        print("提示      : 这个文件自带 SingleFile 标记，样式/字体/图片已内联，抽取质量最高。")
    return info


if __name__ == "__main__":
    main()
