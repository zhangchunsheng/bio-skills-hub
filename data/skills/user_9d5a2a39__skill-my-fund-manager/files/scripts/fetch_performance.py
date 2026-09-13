"""
基金业绩数据获取模块
从东方财富 pingzhongdata 获取基金收益率、净值走势、同类排名等业绩数据。
聚合经理所有管理产品的业绩表现。
"""

import re
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

import _common
from _common import http_get, log, load_manager, save_manager

# pingzhongdata URL
PINGZHONGDATA_URL = "https://fund.eastmoney.com/pingzhongdata/{code}.js"

# 收益率变量名映射（pingzhongdata 实际只提供这4个 syl 变量）
RETURN_VARS = {
    "syl_1y": "近1月",
    "syl_3y": "近3月",
    "syl_6y": "近6月",
    "syl_1n": "近1年",
}


def _extract_js_var(text, var_name, as_float=True):
    """从JS文件中提取变量值"""
    # 匹配 var name = "value"; 或 var name = value;
    pattern = rf'{var_name}\s*=\s*"([^"]*)"'
    m = re.search(pattern, text)
    if m:
        val = m.group(1)
        if as_float:
            try:
                return float(val)
            except ValueError:
                return val
        return val
    # 尝试无引号
    pattern2 = rf'{var_name}\s*=\s*([^;]+);'
    m = re.search(pattern2, text)
    if m:
        val = m.group(1).strip()
        if as_float:
            try:
                return float(val)
            except ValueError:
                return val
        return val
    return None


def fetch_fund_performance(fund_code):
    """
    获取单只基金的业绩数据。
    返回: {fund_code, fund_name, returns: {...}, scale, fee_rate, ...}
    """
    url = PINGZHONGDATA_URL.format(code=fund_code)
    text = http_get(url, encoding="utf-8")
    if not text:
        return {"fund_code": fund_code, "error": "请求失败"}

    result = {"fund_code": fund_code}

    # 基金名称
    name = _extract_js_var(text, "fS_name", as_float=False)
    if name:
        result["fund_name"] = name

    # 基金代码
    code = _extract_js_var(text, "fS_code", as_float=False)
    if code:
        result["fund_code"] = code

    # 收益率数据
    returns = {}
    for var, label in RETURN_VARS.items():
        val = _extract_js_var(text, var)
        if val is not None:
            returns[label] = val
    result["returns"] = returns

    # 管理费率
    fee = _extract_js_var(text, "fund_sourceRate")
    if fee is not None:
        result["fee_rate"] = fee

    # 基金规模
    scale = _extract_js_var(text, "fundShares", as_float=False)
    if scale:
        result["fund_shares"] = scale

    # 基金类型
    ftype = _extract_js_var(text, "fund_type", as_float=False)
    if ftype:
        result["fund_type"] = ftype

    # 最新净值
    # Data_netWorthTrend = [{x: timestamp, y: nav, equityReturn: ..., unitMoney: ...}, ...]
    networth_m = re.search(r'Data_netWorthTrend\s*=\s*(\[.*?\]);', text, re.DOTALL)
    if networth_m:
        try:
            # 这是一个JS对象数组，不是标准JSON，需要简单清理
            nw_text = networth_m.group(1)
            # 提取最后几个净值点
            points = re.findall(r'\{[^}]*"y"\s*:\s*([\d.]+)[^}]*"equityReturn"\s*:\s*([\-\d.]+)[^}]*\}', nw_text)
            if points:
                latest_nav = points[-1][0]
                latest_return = points[-1][1]
                result["latest_nav"] = float(latest_nav)
                result["latest_daily_return"] = float(latest_return)
                # 取最近5个净值点
                recent = points[-5:] if len(points) >= 5 else points
                result["recent_navs"] = [{"nav": float(p[0]), "daily_return": float(p[1])} for p in recent]
        except Exception:
            pass

    # 同类排名百分比（近1年）
    rank_m = re.search(r'Data_rateInSimilarPersent\s*=\s*(\[.*?\]);', text, re.DOTALL)
    if rank_m:
        try:
            rank_text = rank_m.group(1)
            # 提取最近的排名百分比
            ranks = re.findall(r'"x"\s*:\s*(\d+)[^}]*"y"\s*:\s*(\d+)', rank_text)
            if ranks:
                result["latest_rank_percent"] = int(ranks[-1][1])
        except Exception:
            pass

    # 长期收益（近3年/今年以来）：pingzhongdata 的 syl 变量不含这两项，
    # 基于累计净值序列 Data_ACWorthTrend = [[timestamp, 累计净值], ...] 计算（含分红，近似复权）
    ac_m = re.search(r'Data_ACWorthTrend\s*=\s*(\[.*?\]);', text, re.DOTALL)
    if ac_m:
        try:
            import json as _json
            ac = _json.loads(ac_m.group(1))
            if ac and len(ac) >= 2:
                latest_ts, latest_val = ac[-1][0], ac[-1][1]
                if latest_val:
                    result["latest_acc_nav"] = latest_val

                    def _return_since(target_ts):
                        """找到不晚于 target_ts 的最后一个净值点，计算至今收益率(%)"""
                        base = None
                        for ts, val in ac:
                            if ts <= target_ts:
                                base = val
                            else:
                                break
                        if base:
                            return round((latest_val / base - 1) * 100, 2)
                        return None

                    # 近3年（成立不足3年时从首个净值点起算，并标注）
                    r3 = _return_since(latest_ts - int(3 * 365.25 * 86400 * 1000))
                    if r3 is not None:
                        result["returns"]["近3年"] = r3
                        if ac[0][0] > latest_ts - int(3 * 365.25 * 86400 * 1000):
                            result["returns_note"] = "基金成立不足3年，近3年收益为成立以来累计"

                    # 今年以来：以上年最后一个净值点为基准
                    latest_dt = datetime.fromtimestamp(latest_ts / 1000)
                    year_start_ts = datetime(latest_dt.year, 1, 1).timestamp() * 1000
                    ry = _return_since(year_start_ts - 1)
                    if ry is not None:
                        result["returns"]["今年以来"] = ry
        except Exception:
            pass

    return result


def fetch_manager_performance(manager_id, fund_codes=None, max_workers=8):
    """
    获取经理所有管理产品的业绩数据。
    返回: {manager_id, funds: [...], summary: {...}}
    """
    if not fund_codes:
        mgr = load_manager(manager_id)
        if mgr and mgr.get("products"):
            fund_codes = [p.get("code") for p in mgr["products"] if p.get("code")]
        elif mgr and mgr.get("fund_codes"):
            fund_codes = mgr["fund_codes"]
        else:
            log.warning(f"经理 {manager_id} 无管理产品信息")
            return {"manager_id": manager_id, "funds": [], "summary": {}}

    log.info(f"抓取经理 {manager_id} 的 {len(fund_codes)} 只产品业绩数据...")

    funds = []

    def _fetch_one(code):
        return fetch_fund_performance(code)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_map = {executor.submit(_fetch_one, code): code for code in fund_codes if code}
        for future in as_completed(future_map):
            code = future_map[future]
            try:
                result = future.result()
                if result and not result.get("error"):
                    funds.append(result)
                    name = result.get("fund_name", code)
                    r1y = result.get("returns", {}).get("近1年", "N/A")
                    log.info(f"  {code} {name}: 近1年 {r1y}%")
            except Exception as e:
                log.warning(f"  {code}: 业绩获取失败 - {e}")

    # 汇总
    summary = _summarize_performance(funds)

    return {
        "manager_id": manager_id,
        "fund_count": len(funds),
        "funds": funds,
        "summary": summary,
    }


def _summarize_performance(funds):
    """汇总多只基金的业绩"""
    if not funds:
        return {}

    # 计算平均收益率（只统计数值型数据，避免解析失败的字符串污染均值）
    avg_returns = {}
    for label in ["近1月", "近3月", "近6月", "近1年", "近3年", "今年以来"]:
        vals = []
        for f in funds:
            v = f.get("returns", {}).get(label)
            if isinstance(v, (int, float)):
                vals.append(v)
            elif isinstance(v, str):
                try:
                    vals.append(float(v))
                except ValueError:
                    pass
        if vals:
            avg_returns[label] = round(sum(vals) / len(vals), 2)

    # 找最佳和最差产品
    best_fund = None
    worst_fund = None
    for f in funds:
        r1y = f.get("returns", {}).get("近1年")
        if r1y is not None and not isinstance(r1y, (int, float)):
            try:
                r1y = float(r1y)
            except (ValueError, TypeError):
                r1y = None
        if r1y is not None:
            if best_fund is None or r1y > best_fund.get("returns", {}).get("近1年", -9999):
                best_fund = f
            if worst_fund is None or r1y < worst_fund.get("returns", {}).get("近1年", 9999):
                worst_fund = f

    return {
        "avg_returns": avg_returns,
        "fund_count": len(funds),
        "best_fund": {"name": best_fund.get("fund_name"), "code": best_fund.get("fund_code"),
                       "return_1y": best_fund.get("returns", {}).get("近1年")} if best_fund else None,
        "worst_fund": {"name": worst_fund.get("fund_name"), "code": worst_fund.get("fund_code"),
                        "return_1y": worst_fund.get("returns", {}).get("近1年")} if worst_fund else None,
    }


def update_manager_performance(manager_id):
    """抓取并更新经理档案中的业绩数据"""
    result = fetch_manager_performance(manager_id)
    mgr = load_manager(manager_id)
    if not mgr:
        mgr = {"id": manager_id}

    mgr["performance"] = {
        "summary": result["summary"],
        "funds": [{"fund_code": f.get("fund_code"), "fund_name": f.get("fund_name"),
                    "returns": f.get("returns"), "latest_nav": f.get("latest_nav"),
                    "fee_rate": f.get("fee_rate")} for f in result["funds"]],
    }
    mgr["performance_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M")

    save_manager(manager_id, mgr)
    log.info(f"经理 {manager_id} 业绩数据已更新：{len(result['funds'])} 只产品")
    return result


# ============================================================
# CLI 入口
# ============================================================
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("用法:")
        print("  python fetch_performance.py fund <基金代码>     # 单基金业绩")
        print("  python fetch_performance.py manager <经理ID>   # 经理所有产品业绩")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "fund":
        code = sys.argv[2]
        result = fetch_fund_performance(code)
        print(f"\n基金 {result.get('fund_name', code)} 业绩数据：")
        print(f"  最新净值: {result.get('latest_nav', 'N/A')}")
        print(f"  管理费率: {result.get('fee_rate', 'N/A')}%")
        print(f"\n  收益率:")
        for label, val in result.get("returns", {}).items():
            print(f"    {label}: {val}%")
        if result.get("returns_note"):
            print(f"    注: {result['returns_note']}")
        if result.get("latest_rank_percent"):
            print(f"\n  同类排名百分位: {result['latest_rank_percent']}%")

    elif cmd == "manager":
        mgr_id = sys.argv[2]
        result = fetch_manager_performance(mgr_id)
        print(f"\n经理 {mgr_id} 业绩汇总（{result['fund_count']}只产品）：")
        summary = result.get("summary", {})
        print(f"\n  平均收益率:")
        for label, val in summary.get("avg_returns", {}).items():
            print(f"    {label}: {val}%")
        if summary.get("best_fund"):
            bf = summary["best_fund"]
            print(f"\n  最佳产品: {bf['name']}（{bf['code']}）近1年 {bf['return_1y']}%")
        if summary.get("worst_fund"):
            wf = summary["worst_fund"]
            print(f"  最差产品: {wf['name']}（{wf['code']}）近1年 {wf['return_1y']}%")
