#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
零依赖 DOCX 解析器（medical-journal-copyediting）

DOCX 本质是 OOXML 包（zip + XML）。本模块仅用标准库 zipfile + xml 解析
word/document.xml，提取正文与表格文本，并保留每个字符区间的「是否斜体 /
是否上标下标」格式信息——这是自动检查统计学符号正斜体的前提。

返回:
    (lines, image_count)
    lines: list[dict]
        {"text": str, "source": "正文"|"表格",
         "runs": [{"start":int, "end":int, "italic":bool, "vertAlign":str|None}]}
        其中 start/end 为字符索引区间 [start, end)。
    image_count: int  文档内图片（word/media/*）数量

注意：图片像素、嵌入公式（OMML）、脚注、修订痕迹等不可在纯 XML 文本层可靠
获取，仅统计数量并提示人工核对，不做自动检查。
"""

import zipfile
import xml.etree.ElementTree as ET

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
WORD_NS = "{%s}" % W


def _get_run_info(r):
    """提取单个 w:r 的斜体/上下标属性与文本内容。"""
    italic = False
    vert = None
    rpr = r.find(WORD_NS + "rPr")
    if rpr is not None:
        # 仅当 w:i / w:iCs 未显式关闭（val 不为 off/false/0/none）时才视为斜体；
        # 修复「w:i 即使 val=0 仍被当成斜体」的误判。
        for tag in ("i", "iCs"):
            node = rpr.find(WORD_NS + tag)
            if node is not None:
                val = node.get(WORD_NS + "val")
                if val not in ("off", "false", "0", "none"):
                    italic = True
        va = rpr.find(WORD_NS + "vertAlign")
        if va is not None:
            vert = va.get(WORD_NS + "val")
    texts = []
    for t in r.findall(WORD_NS + "t"):
        texts.append(t.text or "")
    for _ in r.findall(WORD_NS + "tab"):
        texts.append("\t")
    for _ in r.findall(WORD_NS + "br"):
        texts.append("\n")
    return italic, vert, "".join(texts)


def _extract_para(p):
    """从 w:p 提取 (text, runs)。"""
    runs = []
    parts = []
    pos = 0

    def consume(r):
        nonlocal pos
        italic, vert, txt = _get_run_info(r)
        if txt:
            start = pos
            parts.append(txt)
            end = pos + len(txt)
            runs.append({"start": start, "end": end,
                         "italic": italic, "vertAlign": vert})
            pos = end

    for child in p:
        if child.tag == WORD_NS + "r":
            consume(child)
        elif child.tag == WORD_NS + "hyperlink":
            for r in child.findall(WORD_NS + "r"):
                consume(r)
    return "".join(parts), runs


def _walk(elem, in_table, lines):
    for child in elem:
        tag = child.tag
        if tag == WORD_NS + "p":
            text, runs = _extract_para(child)
            if text.strip() or runs:
                lines.append({
                    "text": text,
                    "source": "表格" if in_table else "正文",
                    "runs": runs,
                })
        elif tag == WORD_NS + "tbl":
            for tr in child.findall(WORD_NS + "tr"):
                for tc in tr.findall(WORD_NS + "tc"):
                    _walk(tc, True, lines)
        elif tag == WORD_NS + "tr":
            for tc in child.findall(WORD_NS + "tc"):
                _walk(tc, True, lines)
        elif tag == WORD_NS + "tc":
            _walk(child, True, lines)


def parse_docx(path):
    """解析 .docx，返回 (lines, image_count)。"""
    with zipfile.ZipFile(path) as z:
        names = z.namelist()
        try:
            xml = z.read("word/document.xml")
        except KeyError:
            return [], 0
        image_count = len([n for n in names
                           if n.startswith("word/media/")])

    try:
        root = ET.fromstring(xml)
    except ET.ParseError:
        return [], image_count

    body = root.find(WORD_NS + "body")
    lines = []
    if body is not None:
        _walk(body, False, lines)
    return lines, image_count


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        ls, imgs = parse_docx(sys.argv[1])
        print(f"段落/表格文本行数: {len(ls)}，图片数: {imgs}")
        for idx, ln in enumerate(ls[:10], 1):
            print(f"[{idx}][{ln['source']}] {ln['text'][:60]!r}")
