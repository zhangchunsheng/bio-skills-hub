#!/usr/bin/env python3
"""
check_html_divs.py — 校验 HTML 文件中 <div> 开闭标签是否平衡。

批量编辑 index.html（如增减「常见误区」卡片）时容易多写一个 </div>，
导致页面结构破裂。改完跑此脚本确认平衡（opens == closes）再 present。

用法：
  python check_html_divs.py <file.html>
退出码：0=平衡，1=不平衡。
"""
import re
import sys


def check(path: str) -> bool:
    html = open(path, encoding="utf-8").read()
    opens = len(re.findall(r"<div\b", html))
    closes = len(re.findall(r"</div>", html))
    ok = opens == closes
    print(f"div open: {opens}  div close: {closes}  balanced: {ok}")
    return ok


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: python check_html_divs.py <file.html>")
        sys.exit(1)
    ok = check(sys.argv[1])
    sys.exit(0 if ok else 1)
