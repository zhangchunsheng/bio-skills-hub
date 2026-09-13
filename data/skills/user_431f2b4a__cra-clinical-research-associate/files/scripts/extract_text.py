#!/usr/bin/env python3
"""网页 / PDF 正文抽取助手（CRA 指南采集时用）。

只读工具：不写文件、不联网、不解析登录态内容。用于把抓下来的公开页面转成纯文本，
或列出页面里的链接（便于定位子栏目、附件 PDF 直链）。

用法：
    python3 extract_text.py page.html                 # 输出正文
    python3 extract_text.py page.html --links          # 列出全部链接
    python3 extract_text.py page.html --links pdf      # 只列 .pdf 链接
    python3 extract_text.py guide.pdf                  # 抽取 PDF 文本
    python3 extract_text.py page.html --after 正文      # 只输出"正文"出现之后的片段

中文站点常见编码为 utf-8-sig / gbk，脚本会按 utf-8-sig -> gbk -> utf-8 依次尝试。
依赖：仅标准库；抽 PDF 优先用系统 pdftotext，缺失时回退 pypdf（可选）。
"""
from __future__ import annotations

import argparse
import html
import re
import shutil
import subprocess
import sys
from pathlib import Path

# 需要转成换行的块级标签
BLOCK_TAGS = "p|div|li|tr|h1|h2|h3|h4|h5|h6|section|article|table|ul|ol|td|th"


def read_text(path: Path) -> tuple[str, str]:
    """按常见中文编码依次尝试解码，返回 (文本, 编码名)。"""
    raw = path.read_bytes()
    for enc in ("utf-8-sig", "gbk", "utf-8"):
        try:
            return raw.decode(enc), enc
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="ignore"), "utf-8(ignore)"


def html_to_text(source: str) -> str:
    t = re.sub(r"(?is)<(script|style|noscript).*?</\1>", " ", source)
    t = re.sub(r"(?is)<br\s*/?>", "\n", t)
    t = re.sub(rf"(?is)</(?:{BLOCK_TAGS})>", "\n", t)
    t = re.sub(r"(?s)<[^>]+>", " ", t)
    t = html.unescape(t)
    t = re.sub(r"[ \t\u3000\u00a0]+", " ", t)
    t = "\n".join(line.strip() for line in t.split("\n"))
    t = re.sub(r"\n\s*\n+", "\n", t)
    return t.strip()


def list_links(source: str, keyword: str | None) -> list[tuple[str, str]]:
    out = []
    seen = set()
    for m in re.finditer(r'(?is)<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>', source):
        href = html.unescape(m.group(1)).strip()
        text = html.unescape(re.sub(r"<[^>]+>", "", m.group(2))).strip()
        if keyword and keyword.lower() not in href.lower() and keyword.lower() not in text.lower():
            continue
        key = (text, href)
        if key in seen:
            continue
        seen.add(key)
        out.append((text, href))
    return out


def pdf_to_text(path: Path) -> str:
    exe = shutil.which("pdftotext")
    if exe:
        # 先试 -layout（保留版式），抽不出文字再退回无参模式（公文体 PDF 常见）
        for extra in (["-layout"], []):
            proc = subprocess.run(
                [exe, *extra, str(path), "-"],
                capture_output=True,
                text=True,
                errors="ignore",
            )
            if proc.returncode == 0 and proc.stdout.strip():
                return proc.stdout
    try:
        import pypdf  # type: ignore
    except ImportError:
        print(
            "未能抽取 PDF：未找到 pdftotext，且未安装 pypdf。\n"
            "可安装：pip install pypdf",
            file=sys.stderr,
        )
        return ""
    reader = pypdf.PdfReader(str(path))
    return "\n".join((page.extract_text() or "") for page in reader.pages)


def main() -> int:
    ap = argparse.ArgumentParser(description="网页 / PDF 正文抽取助手（只读）")
    ap.add_argument("path", help="本地文件路径（.html / .htm / .pdf / .txt）")
    ap.add_argument("--links", nargs="?", const="", default=None,
                    metavar="关键词", help="列出链接；可给关键词过滤，如 --links pdf")
    ap.add_argument("--after", metavar="锚点", default=None,
                    help="只输出该锚点出现之后的片段（如 --after 正文）")
    args = ap.parse_args()

    path = Path(args.path).expanduser()
    if not path.is_file():
        print(f"文件不存在：{path}", file=sys.stderr)
        return 1

    if path.suffix.lower() == ".pdf":
        text = pdf_to_text(path)
        enc = "pdf"
    else:
        source, enc = read_text(path)
        if args.links is not None:
            for text_, href in list_links(source, args.links or None):
                print(f"{text_}\n    {href}")
            return 0
        text = html_to_text(source)

    if args.after:
        idx = text.find(args.after)
        if idx > 0:
            text = text[idx:]

    print(f"# 文件：{path.name}（编码：{enc}）", file=sys.stderr)
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
