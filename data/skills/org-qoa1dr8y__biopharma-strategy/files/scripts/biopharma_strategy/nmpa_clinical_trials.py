#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""NMPA 临床试验登记平台爬虫 — 中国临床数据源

数据源: https://www.chinadrugtrials.org.cn/ (国家药监局药品审评中心 CDE)
用途: 国内临床试验(对应 ClinicalTrials.gov 的中国版)，港股生物医药分析必查。
反爬: 网站有 JS 混淆 + WAF 反爬，需 Playwright 无头浏览器执行 JS。

用法:
    from nmpa_clinical_trials import search_clinical_trials
    results = search_clinical_trials("泽布替尼")
"""
import sys
import time
from pathlib import Path

from . import fintrust_onboard as _fintrust  # noqa: E402

_fintrust.require_api_key()  # 模块级硬校验：CLI 运行与 import 调用均需 Key

BASE_URL = "https://www.chinadrugtrials.org.cn/"


def _new_page():
    """启动 Playwright 浏览器（headed + 反检测），返回 page。

    chinadrugtrials 有 headless 检测反爬，必须：
    1. headless=False（真实浏览器窗口）
    2. --disable-blink-features=AutomationControlled
    3. 覆盖 navigator.webdriver
    """
    from playwright.sync_api import sync_playwright
    p = sync_playwright().start()
    browser = None
    try:
        browser = p.chromium.launch(
            headless=False,
            args=["--disable-blink-features=AutomationControlled"],
        )
        ctx = browser.new_context(
            user_agent=("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/120.0.0.0 Safari/537.36"),
            locale="zh-CN",
            viewport={"width": 1280, "height": 800},
        )
        ctx.add_init_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )
        page = ctx.new_page()
        return p, browser, ctx, page
    except Exception:
        # 启动过程中出错时确保释放已创建的资源，避免僵尸浏览器进程
        if browser is not None:
            browser.close()
        p.stop()
        raise


def search_clinical_trials(keyword, max_results=20, timeout=30000):
    """搜索 NMPA 临床试验（按药物名/适应症/公司名）。

    返回 list[dict]：registration_no(CTR编号) / status(试验状态) /
    drug_name(药物名称) / indication(适应症) / title(试验题目)
    """
    p, browser, ctx, page = _new_page()
    results = []
    try:
        page.goto(BASE_URL + "index.html", timeout=timeout,
                  wait_until="domcontentloaded")
        time.sleep(4)  # 等待 JS 执行

        # 首页搜索框 name=keywords
        inp = page.locator("input[name='keywords']").first
        try:
            inp.fill(keyword)
        except Exception as e:
            raise RuntimeError(f"未找到搜索输入框，页面结构可能已变化: {e}")
        inp.press("Enter")
        page.wait_for_load_state("domcontentloaded", timeout=timeout)
        time.sleep(4)  # 等待结果表格渲染

        # 结果表格字段: 序号|登记号|试验状态|药物名称|适应症|试验通俗题目
        rows = page.locator("table tr").all()
        for row in rows[1:max_results + 1]:
            cells = [c.strip() for c in row.locator("td").all_inner_texts()]
            if len(cells) >= 6 and cells[1].startswith("CTR"):
                results.append({
                    "registration_no": cells[1],
                    "status": cells[2],
                    "drug_name": cells[3],
                    "indication": cells[4],
                    "title": cells[5],
                })
    finally:
        browser.close()
        p.stop()
    return results


if __name__ == "__main__":
    kw = sys.argv[1] if len(sys.argv) > 1 else "泽布替尼"
    print(f"=== NMPA 临床试验搜索: {kw} ===")
    for r in search_clinical_trials(kw, max_results=10):
        print(r)
