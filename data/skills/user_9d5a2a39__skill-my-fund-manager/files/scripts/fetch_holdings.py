"""
基金十大重仓数据抓取模块
从东方财富获取基金重仓股（股票/债券/基金），聚合经理所有管理产品的重仓。
支持跨所有基金公司和全市场基金经理。
"""

import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

import _common
from _common import http_get, strip_html, log, load_manager, save_manager

# 东方财富持仓API
HOLDINGS_URL = "https://fundf10.eastmoney.com/FundArchivesDatas.aspx"

# 表格行正则
_TR_PATTERN = re.compile(r"<tr[^>]*>(.*?)</tr>", re.DOTALL)
_TD_PATTERN = re.compile(r"<td[^>]*>(.*?)</td>", re.DOTALL)


def _parse_holdings_table(html_text, holding_type="stock"):
    """
    解析持仓HTML表格，返回重仓列表。
    holding_type: stock/bond/fund
    返回: [{rank, code, name, ratio, market_value, quantity, ...}]
    """
    rows = _TR_PATTERN.findall(html_text)
    holdings = []

    for row in rows:
        cells = _TD_PATTERN.findall(row)
        if len(cells) < 4:
            continue
        cells_clean = [strip_html(c).strip() for c in cells]

        # 跳过表头行（第一个单元格不是数字）
        if not cells_clean[0].isdigit():
            continue

        rank = int(cells_clean[0])

        # 只取最新报告期：遇到序号重新从1开始（说明进入了下一期表格）则停止
        if holdings and rank == 1:
            break
        code = cells_clean[1] if len(cells_clean) > 1 else ""
        name = cells_clean[2] if len(cells_clean) > 2 else ""

        if not name:
            continue

        # 提取占净值比例/持股数/持仓市值：ratio=含%的单元格；
        # ratio 之后的数值列顺序为 持股数(万股)、持仓市值(万元)（股票表）；
        # 债券/基金表通常只有持仓市值一列
        ratio = ""
        numeric_after = []
        for cell in cells_clean[3:]:
            if not ratio and "%" in cell:
                ratio = cell
                continue
            if ratio and cell and cell.replace(",", "").replace(".", "").replace("-", "").isdigit():
                numeric_after.append(cell)
        # 兜底：如果没找到ratio，搜索所有单元格
        if not ratio:
            for cell in cells_clean:
                if "%" in cell:
                    ratio = cell
                    break
        market_value = ""
        quantity = ""
        if len(numeric_after) >= 2:
            quantity, market_value = numeric_after[0], numeric_after[1]
        elif numeric_after:
            market_value = numeric_after[0]

        holdings.append({
            "rank": rank,
            "code": code,
            "name": name,
            "ratio": ratio,
            "market_value": market_value,
            "quantity": quantity,
            "type": holding_type,
        })

    return holdings


def fetch_fund_holdings(fund_code, holding_type="stock"):
    """
    获取单只基金最新报告期的十大重仓。
    holding_type: stock(股票) / bond(债券) / fund(基金)
    返回: {fund_code, report_date, holdings: [...]}
    """
    type_map = {"stock": "jjcc", "bond": "zqcc", "fund": "jjcc_2"}
    apitype = type_map.get(holding_type, "jjcc")

    text = http_get(
        HOLDINGS_URL,
        params={"type": apitype, "code": fund_code, "topline": "10"},
        encoding="utf-8",
    )
    if not text:
        return {"fund_code": fund_code, "report_date": "", "holdings": [], "error": "请求失败"}

    # 提取报告期（arryear）
    report_date = ""
    arryear_m = re.search(r'arryear\s*[:=]\s*\["([^"]+)"', text)
    if arryear_m:
        report_date = arryear_m.group(1)

    # 提取content中的HTML表格
    content_m = re.search(r'content\s*[:=]\s*"(.*?)"\s*[,;}]', text, re.DOTALL)
    if content_m:
        html_content = content_m.group(1)
        # 反转义
        html_content = html_content.replace("\\/", "/").replace('\\"', '"').replace("\\n", "")
    else:
        # 尝试直接从全文解析表格
        html_content = text

    holdings = _parse_holdings_table(html_content, holding_type)

    # 如果没有报告期，尝试从持仓数据中推断
    if not report_date:
        date_m = re.search(r'(\d{4}-\d{2}-\d{2})', text)
        if date_m:
            report_date = date_m.group(1)

    return {
        "fund_code": fund_code,
        "report_date": report_date,
        "holdings": holdings,
    }


def fetch_manager_holdings(manager_id, fund_codes=None, max_workers=8):
    """
    获取经理所有管理产品的十大重仓，聚合去重。
    参数:
        manager_id: 经理ID
        fund_codes: 可选，指定基金代码列表。不传则从经理档案加载
        max_workers: 并发数
    返回: 聚合后的重仓数据
    """
    # 获取基金代码列表
    if not fund_codes:
        mgr = load_manager(manager_id)
        if mgr and mgr.get("products"):
            fund_codes = [p.get("code") for p in mgr["products"] if p.get("code")]
        elif mgr and mgr.get("fund_codes"):
            fund_codes = mgr["fund_codes"]
        else:
            log.warning(f"经理 {manager_id} 无管理产品信息")
            return {"manager_id": manager_id, "top_holdings": [], "report_date": ""}

    log.info(f"抓取经理 {manager_id} 的 {len(fund_codes)} 只产品重仓...")

    all_results = []

    def _fetch_one(code):
        return fetch_fund_holdings(code, "stock")

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(_fetch_one, code): code for code in fund_codes if code}
        for future in as_completed(futures):
            code = futures[future]
            try:
                result = future.result()
                if result.get("holdings"):
                    all_results.append(result)
                    log.info(f"  {code}: {len(result['holdings'])} 只重仓股（{result.get('report_date','')}）")
                elif result.get("error"):
                    log.warning(f"  {code}: {result['error']}")
                else:
                    log.warning(f"  {code}: 无重仓数据（可能已清盘、转型或非股票持仓型基金）")
            except Exception as e:
                log.warning(f"  {code}: 抓取失败 - {e}")

    # 聚合去重
    aggregated = _aggregate_holdings(all_results)

    return {
        "manager_id": manager_id,
        "fund_count": len(all_results),
        "report_date": aggregated.get("latest_date", ""),
        "top_holdings": aggregated["holdings"],
        "raw_results": all_results,
    }


def _aggregate_holdings(results):
    """
    聚合多只基金的重仓数据，去重并按总占比排序。
    返回: {latest_date, holdings: [...]}
    """
    stock_map = {}  # name -> {code, name, funds, ratios, total_ratio}
    latest_date = ""

    for result in results:
        report_date = result.get("report_date", "")
        if report_date and report_date > latest_date:
            latest_date = report_date

        fund_code = result.get("fund_code", "")
        for h in result.get("holdings", []):
            name = h["name"]
            if not name:
                continue

            # 占比转浮点数
            ratio_str = h.get("ratio", "").replace("%", "").replace(" ", "")
            try:
                ratio = float(ratio_str) if ratio_str else 0
            except ValueError:
                ratio = 0

            key = f"{h.get('code','')}_{name}"
            if key not in stock_map:
                stock_map[key] = {
                    "code": h.get("code", ""),
                    "name": name,
                    "funds": [],
                    "ratios": [],
                    "total_ratio": 0,
                    "appear_count": 0,
                }

            stock_map[key]["funds"].append(fund_code)
            stock_map[key]["ratios"].append(ratio)
            stock_map[key]["total_ratio"] += ratio
            stock_map[key]["appear_count"] += 1

    # 转列表并排序
    holdings = list(stock_map.values())
    for h in holdings:
        h["avg_ratio"] = round(h["total_ratio"] / h["appear_count"], 2) if h["appear_count"] else 0
        h["total_ratio"] = round(h["total_ratio"], 2)
        h["fund_count"] = len(set(h["funds"]))

    holdings.sort(key=lambda x: x["total_ratio"], reverse=True)

    return {"latest_date": latest_date, "holdings": holdings}


def update_manager_holdings(manager_id):
    """抓取并更新经理档案中的重仓数据"""
    result = fetch_manager_holdings(manager_id)
    mgr = load_manager(manager_id)
    if not mgr:
        mgr = {"id": manager_id}

    mgr["top_holdings"] = result["top_holdings"][:30]  # 保留前30
    mgr["holdings_report_date"] = result["report_date"]
    mgr["holdings_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M")

    save_manager(manager_id, mgr)
    log.info(f"经理 {manager_id} 重仓数据已更新：{len(mgr['top_holdings'])} 只，报告期 {result['report_date']}")
    return result


# ============================================================
# CLI 入口
# ============================================================
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("用法:")
        print("  python fetch_holdings.py fund <基金代码> [stock/bond/fund]  # 单基金重仓")
        print("  python fetch_holdings.py manager <经理ID>                   # 经理所有产品重仓")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "fund":
        if len(sys.argv) < 3:
            print("用法: python fetch_holdings.py fund <基金代码> [stock/bond/fund]")
            sys.exit(1)
        code = sys.argv[2]
        htype = sys.argv[3] if len(sys.argv) > 3 else "stock"
        result = fetch_fund_holdings(code, htype)
        print(f"\n基金 {code} 重仓（{htype}）- 报告期: {result['report_date']}")
        print(f"{'序号':<4} {'代码':<10} {'名称':<12} {'占比':<8} {'持股数(万股)':<14} {'市值(万元)':<12}")
        print("-" * 60)
        for h in result["holdings"]:
            print(f"{h['rank']:<4} {h['code']:<10} {h['name']:<12} {h['ratio']:<8} {h['quantity']:<14} {h['market_value']:<12}")

    elif cmd == "manager":
        if len(sys.argv) < 3:
            print("用法: python fetch_holdings.py manager <经理ID>")
            sys.exit(1)
        mgr_id = sys.argv[2]
        result = fetch_manager_holdings(mgr_id)
        print(f"\n经理 {mgr_id} 聚合重仓 - 报告期: {result['report_date']}")
        print(f"覆盖 {result['fund_count']} 只产品，共 {len(result['top_holdings'])} 只重仓")
        print(f"\n{'排名':<4} {'代码':<10} {'名称':<12} {'总占比':<8} {'出现次数':<8} {'覆盖基金数':<8}")
        print("-" * 60)
        for i, h in enumerate(result["top_holdings"][:20]):
            print(f"{i+1:<4} {h['code']:<10} {h['name']:<12} {h['total_ratio']:<8} {h['appear_count']:<8} {h['fund_count']:<8}")
