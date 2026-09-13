#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
把医疗险方案 HTML 渲染为手机/横版 PNG。
无需 Safari，使用 Playwright（Chromium）无头渲染。

用法：
    python html_to_png.py <输入.html> <输出.png> [宽度=480]

说明：
    - 首次运行会自动安装 Playwright 与 Chromium（约 150MB，需联网一次）。
    - 宽度 480 为竖版手机图，960 为横版网页图。
    - 输出为视网膜 2x 高清 PNG，竖版 full_page 整图。
"""
import sys
import os
import subprocess


def ensure_playwright():
    """确保 playwright 与 chromium 已安装（首次自动装）。"""
    try:
        import playwright  # noqa: F401
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "playwright"])
    # 检查 chromium 是否已下载
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            p.chromium.launch(args=["--no-sandbox"])
    except Exception:
        subprocess.check_call([sys.executable, "-m", "playwright", "install", "chromium"])


def main():
    if len(sys.argv) < 3:
        print("用法: python html_to_png.py <输入.html> <输出.png> [宽度=480]")
        sys.exit(1)

    inp = sys.argv[1]
    out = sys.argv[2]
    width = int(sys.argv[3]) if len(sys.argv) > 3 else 480

    if not os.path.exists(inp):
        print("输入文件不存在:", inp)
        sys.exit(1)

    ensure_playwright()

    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(args=["--no-sandbox"])
        page = browser.new_page(
            viewport={"width": width, "height": 1200},
            device_scale_factor=2,
        )
        page.goto("file://" + os.path.abspath(inp), wait_until="networkidle")
        page.wait_for_timeout(500)  # 等字体/布局稳定
        page.screenshot(path=out, full_page=True)
        browser.close()

    print("PNG 已生成:", out)


if __name__ == "__main__":
    main()
