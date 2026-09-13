"""
基金定期报告与投资策略获取模块
从东方财富获取基金投资策略、投资目标、投资范围，以及最新季报公告信息。
用于蒸馏基金经理投资风格的核心素材。
"""

import re
import json
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

import _common
from _common import http_get, strip_html, log, load_manager, save_manager

# 东方财富页面URL模板
JBGK_URL = "https://fundf10.eastmoney.com/jbgk_{code}.html"  # 基金基本概况
ANNOUNCE_API = "https://api.fund.eastmoney.com/f10/JJGG"  # 公告API

# 章节关键词
SECTION_KEYWORDS = ["投资目标", "投资范围", "投资策略", "投资理念", "业绩比较基准", "风险收益特征"]


def _extract_section(html, section_name):
    """从HTML中提取指定章节内容"""
    # jbgk 页面两种结构：
    # ① 顶部信息表 <th>业绩比较基准</th><td>内容</td>
    # ② 章节块 <label class="left">投资目标</label>...</h4>...<p>内容</p>
    # 注意：th/td 模式必须放在通用 </[^>]+> 模式之前，否则业绩比较基准会错位匹配到投资目标的 <p>
    patterns = [
        rf'{section_name}\s*</th>\s*<td[^>]*>(.*?)</td>',
        rf'{section_name}</label>.*?<p>(.*?)</p>',
        rf'{section_name}</h4>.*?<p>(.*?)</p>',
        rf'{section_name}</[^>]+>.*?<p>(.*?)</p>',
        rf'{section_name}[:：]\s*(.*?)(?:<|$)',
    ]
    for pattern in patterns:
        m = re.search(pattern, html, re.DOTALL | re.IGNORECASE)
        if m:
            text = strip_html(m.group(1)).strip()
            if text and len(text) > 3:
                return text
    return ""


def fetch_fund_strategy(fund_code):
    """
    获取基金基本概况中的投资策略、投资目标、投资范围等。
    返回: {fund_code, fund_name, invest_target, invest_scope, invest_strategy, ...}
    """
    url = JBGK_URL.format(code=fund_code)
    html = http_get(url, encoding="utf-8")
    if not html:
        return {"fund_code": fund_code, "error": "请求失败"}

    result = {"fund_code": fund_code}

    # 基金名称
    m = re.search(r'<h4[^>]*>([^<]*基金[^<]*)</h4>', html)
    if not m:
        m = re.search(r'class="fundname"[^>]*>([^<]+)<', html)
    if m:
        result["fund_name"] = m.group(1).strip()

    # 提取各章节
    for section in SECTION_KEYWORDS:
        content = _extract_section(html, section)
        if content:
            key_map = {
                "投资目标": "invest_target",
                "投资范围": "invest_scope",
                "投资策略": "invest_strategy",
                "投资理念": "invest_idea",
                "业绩比较基准": "benchmark",
                "风险收益特征": "risk_feature",
            }
            key = key_map.get(section, section)
            result[key] = content

    return result


def fetch_fund_announcements(fund_code, page_size=10, ann_type="3"):
    """
    获取基金定期报告公告列表。
    ann_type: 3=定期报告
    返回: [{title, date, id, fund_code}]
    """
    text = http_get(
        ANNOUNCE_API,
        params={
            "fundcode": fund_code,
            "pageIndex": "1",
            "pageSize": str(page_size),
            "type": ann_type,
        },
        encoding="utf-8",
        referer="https://fundf10.eastmoney.com/",
    )
    if not text:
        return []

    m = re.search(r"\{.*\}", text, re.DOTALL)
    if not m:
        return []

    try:
        data = json.loads(m.group(0))
    except json.JSONDecodeError:
        return []

    announcements = []
    for item in data.get("Data", []):
        announcements.append({
            "fund_code": fund_code,
            "title": item.get("TITLE", ""),
            "date": item.get("PUBLISHDATEDesc", ""),
            "id": item.get("ID", ""),
            "pdf_url": f"https://pdf.dfcfw.com/pdf/H2_{item.get('ID','')}_1.pdf",
        })

    return announcements


def fetch_latest_quarterly_report(fund_code):
    """
    获取最新季报公告信息（标题、日期、PDF链接）。
    注意：季报正文为PDF格式，agent可直接访问pdf_url获取正文内容。
    """
    anns = fetch_fund_announcements(fund_code, page_size=5)
    for ann in anns:
        title = ann.get("title", "")
        # 季度报告
        if "季度报告" in title and "摘要" not in title:
            return ann
    # 如果没有季报，返回最新的
    return anns[0] if anns else None


def fetch_manager_reports(manager_id, fund_codes=None, max_workers=8):
    """
    获取经理所有管理产品的投资策略和最新季报公告。
    返回: {manager_id, strategies: [...], latest_reports: [...]}
    """
    if not fund_codes:
        mgr = load_manager(manager_id)
        if mgr and mgr.get("products"):
            fund_codes = [p.get("code") for p in mgr["products"] if p.get("code")]
        elif mgr and mgr.get("fund_codes"):
            fund_codes = mgr["fund_codes"]
        else:
            log.warning(f"经理 {manager_id} 无管理产品信息")
            return {"manager_id": manager_id, "strategies": [], "latest_reports": []}

    log.info(f"抓取经理 {manager_id} 的 {len(fund_codes)} 只产品的投资策略和季报...")

    strategies = []
    latest_reports = []

    def _fetch_strategy(code):
        return fetch_fund_strategy(code)

    def _fetch_report(code):
        return fetch_latest_quarterly_report(code)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 并发获取投资策略
        future_map = {executor.submit(_fetch_strategy, code): code for code in fund_codes if code}
        for future in as_completed(future_map):
            code = future_map[future]
            try:
                result = future.result()
                if result and not result.get("error"):
                    strategies.append(result)
                    log.info(f"  {code}: 投资策略获取成功")
            except Exception as e:
                log.warning(f"  {code}: 投资策略获取失败 - {e}")

    # 获取最新季报公告（串行，数量少）
    for code in fund_codes[:5]:  # 只取前5只产品的季报
        if not code:
            continue
        report = _fetch_report(code)
        if report:
            latest_reports.append(report)

    return {
        "manager_id": manager_id,
        "strategies": strategies,
        "latest_reports": latest_reports,
    }


def update_manager_reports(manager_id):
    """抓取并更新经理档案中的投资策略和季报信息"""
    result = fetch_manager_reports(manager_id)
    mgr = load_manager(manager_id)
    if not mgr:
        mgr = {"id": manager_id}

    # 合并投资策略文本（用于蒸馏）
    strategy_texts = []
    for s in result["strategies"]:
        parts = []
        if s.get("fund_name"):
            parts.append(f"【{s['fund_name']}】")
        if s.get("invest_target"):
            parts.append(f"投资目标：{s['invest_target']}")
        if s.get("invest_strategy"):
            parts.append(f"投资策略：{s['invest_strategy']}")
        if s.get("invest_scope"):
            parts.append(f"投资范围：{s['invest_scope']}")
        if s.get("invest_idea"):
            parts.append(f"投资理念：{s['invest_idea']}")
        if parts:
            strategy_texts.append("\n".join(parts))

    mgr["strategy_texts"] = strategy_texts
    mgr["latest_reports"] = result["latest_reports"]
    mgr["reports_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M")

    save_manager(manager_id, mgr)
    log.info(f"经理 {manager_id} 投资策略已更新：{len(strategy_texts)} 只产品")
    return result


# ============================================================
# CLI 入口
# ============================================================
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("用法:")
        print("  python fetch_reports.py strategy <基金代码>    # 获取投资策略")
        print("  python fetch_reports.py announce <基金代码>    # 获取季报公告列表")
        print("  python fetch_reports.py latest <基金代码>      # 获取最新季报")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "strategy":
        code = sys.argv[2]
        result = fetch_fund_strategy(code)
        print(f"\n基金 {code} 投资策略：")
        for k, v in result.items():
            if k != "fund_code" and v:
                print(f"  {k}: {v[:200]}")

    elif cmd == "announce":
        code = sys.argv[2]
        anns = fetch_fund_announcements(code)
        print(f"\n基金 {code} 定期报告公告：")
        for ann in anns:
            print(f"  {ann['date']} | {ann['title']}")

    elif cmd == "latest":
        code = sys.argv[2]
        report = fetch_latest_quarterly_report(code)
        if report:
            print(f"\n基金 {code} 最新季报：")
            print(f"  标题: {report['title']}")
            print(f"  日期: {report['date']}")
            print(f"  PDF:  {report.get('pdf_url','')}")
        else:
            print(f"未找到季报公告")
