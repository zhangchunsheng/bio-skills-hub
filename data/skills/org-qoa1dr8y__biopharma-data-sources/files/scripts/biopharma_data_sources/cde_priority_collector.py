#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CDE 优先审评 + 突破性治疗 采集器
================================
数据源：国家药监局药品审评中心（CDE）官网 www.cde.org.cn
  - 纳入优先审评品种名单（信息公开 -> 优先审评公示 -> 纳入优先审评品种名单）
  - 突破性治疗品种（信息公开 -> 突破性治疗公示 -> 纳入突破性治疗品种名单）

价值：这是港股创新药"早于获批"最有价值的官方信号。
  例：信达生物替妥尤单抗 2024-05-21 承办 -> 2025-03 获批（时差约 10 个月）

反爬：CDE 官网是瑞数(RiverSecurity)级 JS 挑战反爬，requests 拿不到（返回 202 空页）。
  必须用 Playwright 真实浏览器 + 反检测参数（disable-blink-features + 隐藏 webdriver）。

用法：
  python3 cde_priority_collector.py --company "信达生物" --company "复宏汉霖"
  python3 cde_priority_collector.py --company 信达 --days 30   # 只看近30天公示
"""
import asyncio
import json
import re
import sys
import argparse
from datetime import datetime, timedelta
from pathlib import Path

from . import fintrust_onboard as _fintrust  # noqa: E402

_fintrust.require_api_key()  # 模块级硬校验：CLI 运行与 import 调用均需 Key

UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

PRIORITY_URL = 'https://www.cde.org.cn/main/xxgk/listpage/2f78f372d351c6851af7431c7710a731'  # 优先审评公示
BREAK_URL = 'https://www.cde.org.cn/main/xxgk/listpage/da6efd086c099b7fc949121166f0130c'      # 突破性治疗公示


def parse_table_rows(text, marker_start, marker_end):
    """从页面文本中解析表格行（优先审评/突破性治疗的结果表格）"""
    rows = []
    idx = text.find(marker_start)
    if idx < 0:
        return rows
    seg = text[idx: text.find(marker_end, idx) if text.find(marker_end, idx) > 0 else idx + 2000]
    # 表格行形如：序号\t受理号\t药品名称\t注册申请人\t承办日期\t申请日期\t公示日期\t状态\t是否罕见病
    lines = [l for l in seg.split('\n') if '\t' in l]
    for line in lines:
        cols = [c.strip() for c in line.split('\t')]
        if len(cols) >= 7 and cols[1] and cols[1] != '受理号':
            # 跳过表头
            if cols[1] in ('受理号',) and cols[2] == '药品名称':
                continue
            rows.append(cols)
    return rows


async def fetch_company_priority(company, days=None, kind='priority'):
    """用 Playwright 抓取某公司的优先审评/突破性治疗品种"""
    url = PRIORITY_URL if kind == 'priority' else BREAK_URL
    field_id = 'companyInclude' if kind == 'priority' else 'companyBreakInclude'
    marker = '纳入优先审评品种名单' if kind == 'priority' else '突破性治疗'

    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=['--disable-blink-features=AutomationControlled', '--no-sandbox']
        )
        ctx = await browser.new_context(user_agent=UA)
        await ctx.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined});")
        page = await ctx.new_page()
        try:
            await page.goto(url, wait_until='domcontentloaded', timeout=40000)
            await page.wait_for_timeout(6000)  # 等 JS 挑战完成
            await page.fill(f'#{field_id}', company)
            await page.evaluate(f"""() => {{
                const inp = document.getElementById('{field_id}');
                let el = inp;
                while (el && el !== document.body) {{
                    el = el.parentElement;
                    if (el) {{
                        const btn = el.querySelector('.searchBtn');
                        if (btn) {{ btn.click(); return true; }}
                    }}
                }}
                return false;
            }}""")
            await page.wait_for_timeout(4000)
            text = await page.evaluate("() => document.body.innerText")
        finally:
            await browser.close()

    rows = parse_table_rows(text, marker, '共 ')
    # 过滤：状态为"已纳入"（排除"已公示待论证"等非最终状态？实际都保留，标注状态）
    results = []
    for cols in rows:
        # cols: [序号, 受理号, 药品名称, 注册申请人, 承办日期, 申请日期, 公示日期, 状态, 是否罕见病]
        try:
            item = {
                '受理号': cols[1] if len(cols) > 1 else '',
                '药品名称': cols[2] if len(cols) > 2 else '',
                '注册申请人': cols[3] if len(cols) > 3 else '',
                '承办日期': cols[4] if len(cols) > 4 else '',
                '申请日期': cols[5] if len(cols) > 5 else '',
                '公示日期': cols[6] if len(cols) > 6 else '',
                '状态': cols[7] if len(cols) > 7 else '',
                '是否罕见病': cols[8] if len(cols) > 8 else '',
                '类型': '优先审评' if kind == 'priority' else '突破性治疗',
            }
        except IndexError:
            continue
        # 按公示日期过滤近 N 天
        if days:
            try:
                d = datetime.strptime(item['公示日期'], '%Y-%m-%d')
                if (datetime.now() - d).days > days:
                    continue
            except (ValueError, TypeError):
                pass
        results.append(item)
    return results


async def collect(companies, days=None):
    out = {}
    for company in companies:
        out[company] = {'优先审评': [], '突破性治疗': []}
        try:
            out[company]['优先审评'] = await fetch_company_priority(company, days, 'priority')
        except Exception as e:
            out[company]['优先审评_error'] = str(e)[:200]
        try:
            out[company]['突破性治疗'] = await fetch_company_priority(company, days, 'break')
        except Exception as e:
            out[company]['突破性治疗_error'] = str(e)[:200]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--company', action='append', required=True, help='公司名（可多次传入），支持模糊匹配如"信达"')
    ap.add_argument('--days', type=int, default=None, help='只看近 N 天公示（默认全部）')
    args = ap.parse_args()

    result = asyncio.run(collect(args.company, args.days))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
