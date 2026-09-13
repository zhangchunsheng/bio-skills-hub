"""
基金经理搜索与识别模块
从东方财富获取全市场基金经理列表，支持按姓名/产品/公司模糊搜索。
无法确认时返回候选列表供反问确认。
适配全市场所有基金公司和基金经理。
"""

import os
import re
import time
from datetime import datetime, timedelta

import _common
from _common import http_get, read_json, write_json, log, DATA_DIR

# 经理索引缓存路径
INDEX_PATH = os.path.join(DATA_DIR, "manager_index.json")
INDEX_CACHE_DAYS = 7  # 缓存有效期

# 东方财富经理列表API
MANAGER_LIST_URL = "https://fund.eastmoney.com/Data/FundDataPortfolio_Interface.aspx"

# 匹配经理数据的正则（12字段：ID,姓名,公司ID,公司,基金代码,基金名称,任职天数,任职回报,代表基金代码,代表基金名称,规模,代表回报）
_MANAGER_PATTERN = re.compile(
    r'\["([^"]*)","([^"]*)","([^"]*)","([^"]*)","([^"]*)","([^"]*)",'
    r'"([^"]*)","([^"]*)","([^"]*)","([^"]*)","([^"]*)","([^"]*)"\]'
)


def build_manager_index(force_refresh=False):
    """
    构建全市场基金经理索引，缓存到 data/manager_index.json（有效期7天）。
    全市场约4000+经理，分页获取（每页500，约9页）。
    返回经理列表 [{id, name, company_id, company, fund_codes, fund_names, tenure_days, tenure_return, ...}]

    降级策略（v2.0.0）：缓存过期但 HTTP 重建失败时，回退到过期缓存，
    避免线上 silent failure（搜索返回空）。
    """
    # 检查缓存
    cached = None
    cache_is_fresh = False
    if not force_refresh:
        cached = read_json(INDEX_PATH, default=None)
        if cached and cached.get("meta", {}).get("last_update"):
            try:
                last = datetime.strptime(cached["meta"]["last_update"], "%Y-%m-%d")
                if datetime.now() - last < timedelta(days=INDEX_CACHE_DAYS):
                    log.info(f"使用缓存的经理索引（{cached['meta']['count']}人，{cached['meta']['last_update']}更新）")
                    return cached["managers"]
                cache_is_fresh = False  # 缓存存在但过期
            except (ValueError, TypeError):
                log.warning("缓存 last_update 格式异常，忽略缓存")
                cached = None

    log.info("开始构建全市场基金经理索引...")
    all_managers = []
    page_size = 500
    page_num = 1
    start_time = time.time()
    max_build_time = 120  # 最长构建时间（秒）

    try:
        while True:
            # 超时保护
            if time.time() - start_time > max_build_time:
                log.warning(f"经理索引构建超时（>{max_build_time}秒），已获取 {len(all_managers)} 人")
                break
            text = http_get(
                MANAGER_LIST_URL,
                params={
                    "dt": "14", "ft": "all",
                    "pn": str(page_size), "pi": str(page_num),
                    "sc": "abbname", "st": "asc", "mc": "returnjson",
                },
                encoding="utf-8",
            )
            if not text:
                log.warning(f"第{page_num}页请求失败")
                break

            matches = _MANAGER_PATTERN.findall(text)
            if not matches:
                break

            for m in matches:
                fund_codes = m[4].split(",") if m[4] else []
                fund_names = m[5].split(",") if m[5] else []
                all_managers.append({
                    "id": m[0],
                    "name": m[1],
                    "company_id": m[2],
                    "company": m[3],
                    "fund_codes": fund_codes,
                    "fund_names": fund_names,
                    "tenure_days": int(m[6]) if m[6].isdigit() else 0,
                    "tenure_return": m[7],
                    "rep_fund_code": m[8],
                    "rep_fund_name": m[9],
                    "scale": m[10],
                    "rep_fund_return": m[11],
                })

            log.info(f"  第{page_num}页: 获取{len(matches)}人，累计{len(all_managers)}人")

            if len(matches) < page_size:
                break  # 最后一页
            page_num += 1
            if page_num > 20:  # 安全上限
                break
    except Exception as e:
        # HTTP 异常时降级到过期缓存（v2.0.0）
        log.warning(f"经理索引重建失败（{e}），尝试降级到过期缓存")
        if cached and cached.get("managers"):
            log.info(f"使用过期缓存（{cached['meta'].get('count', 0)}人，可能略陈旧）")
            return cached["managers"]
        return []

    # 如果一条都没拿到，也尝试降级到过期缓存
    if not all_managers:
        if cached and cached.get("managers"):
            log.info("本次重建无结果，使用过期缓存兜底")
            return cached["managers"]
        log.warning("经理索引构建无结果且无过期缓存可用")
        return []

    # 写入缓存
    index_data = {
        "meta": {
            "last_update": datetime.now().strftime("%Y-%m-%d"),
            "count": len(all_managers),
            "source": "东方财富 FundDataPortfolio_Interface.aspx",
        },
        "managers": all_managers,
    }
    write_json(INDEX_PATH, index_data)
    log.info(f"经理索引构建完成：{len(all_managers)}人，已缓存到 {INDEX_PATH}")
    return all_managers


def search_managers(keyword, search_type="auto", company_filter=None):
    """
    搜索基金经理。支持按姓名/产品名/公司名模糊匹配。
    返回候选列表，按匹配度排序。

    参数:
        keyword: 搜索关键词（姓名/产品名/公司名）
        search_type: auto(自动) / name(姓名) / product(产品) / company(公司)
        company_filter: 可选，限定基金公司名
    返回:
        [{id, name, company, fund_names, tenure_return, scale, match_reason, match_score}]
    """
    managers = build_manager_index()
    if not managers:
        return []

    keyword = keyword.strip()
    kw_clean = keyword.replace(" ", "").replace("　", "")
    results = []

    for m in managers:
        name = m.get("name") or ""
        company = m.get("company") or ""
        fund_names = m.get("fund_names") or []
        fund_codes = m.get("fund_codes") or []

        # 公司过滤
        if company_filter and company_filter not in company:
            continue

        match_reason = None
        match_score = 0

        # 姓名匹配（最高优先级）
        if search_type in ("auto", "name"):
            if keyword == name:
                match_reason = f"姓名完全匹配"
                match_score = 100
            elif kw_clean and kw_clean in name.replace(" ", ""):
                match_reason = f"姓名包含'{keyword}'"
                match_score = 90
            elif name and name in keyword:
                match_reason = f"姓名是'{name}'"
                match_score = 85

        # 产品名匹配
        if not match_reason and search_type in ("auto", "product"):
            for fn in fund_names:
                if keyword in fn or fn in keyword:
                    match_reason = f"管理产品'{fn}'"
                    match_score = 70
                    break

        # 产品代码匹配
        if not match_reason and search_type in ("auto", "product"):
            if keyword in fund_codes:
                idx = fund_codes.index(keyword)
                match_reason = f"管理基金代码'{keyword}'({fund_names[idx] if idx < len(fund_names) else ''})"
                match_score = 75

        # 公司匹配
        if not match_reason and search_type in ("auto", "company"):
            if keyword in company or company in keyword:
                match_reason = f"所属公司'{company}'"
                match_score = 50

        if match_reason:
            results.append({
                "id": m["id"],
                "name": name,
                "company": company,
                "fund_count": len(fund_names),
                "fund_names": fund_names[:5],  # 只取前5个产品名
                "fund_codes": fund_codes[:5],
                "tenure_return": m["tenure_return"],
                "scale": m["scale"],
                "match_reason": match_reason,
                "match_score": match_score,
            })

    # 按匹配度排序
    results.sort(key=lambda x: x["match_score"], reverse=True)
    return results


def format_candidates(candidates):
    """格式化候选列表为可读文本，供反问用户确认"""
    if not candidates:
        return "未找到匹配的基金经理。请尝试提供更准确的信息（如姓名、基金代码或基金公司全称）。"

    if len(candidates) == 1:
        return f"找到唯一匹配：{candidates[0]['name']}（{candidates[0]['company']}），{candidates[0]['match_reason']}"

    lines = [f"找到 {len(candidates)} 位匹配的基金经理，请确认是哪一位：\n"]
    for i, c in enumerate(candidates[:10]):  # 最多显示10个
        mtype = c.get("manager_type", "公募")
        type_tag = {"公募": "🏆公募", "私募": "📈私募"}.get(mtype, mtype)
        lines.append(
            f"  [{i+1}] {type_tag} {c['name']} | {c['company']} | "
            f"管理{c.get('fund_count', 0)}只产品 | 任职回报{c.get('tenure_return', 'N/A')} | "
            f"规模{c.get('scale', 'N/A')} | 匹配：{c['match_reason']}"
        )
        if c["fund_names"]:
            lines.append(f"       代表产品：{', '.join(c['fund_names'][:3])}")
    if len(candidates) > 10:
        lines.append(f"\n  ...还有 {len(candidates)-10} 位，请缩小搜索范围")
    return "\n".join(lines)


def get_manager_detail(manager_id):
    """
    获取基金经理详情（从东方财富经理详情页解析投资理念、简历等）。
    返回 {id, name, company, invest_idea, resume, ...}。失败返回基本信息。
    """
    from _common import strip_html

    url = f"https://fundf10.eastmoney.com/Manager/MangerInfo/{manager_id}"
    text = http_get(url, encoding="utf-8")
    if not text:
        return {"id": manager_id, "name": "", "company": ""}

    detail = {"id": manager_id}

    # 姓名
    m = re.search(r'<a[^>]*class="bold"[^>]*>([^<]+)</a>', text)
    if m:
        detail["name"] = m.group(1).strip()

    # 公司
    m = re.search(r'所在公司[^<]*<[^>]*>([^<]+)<', text)
    if not m:
        m = re.search(r'基金公司[^<]*<[^>]*>([^<]+)<', text)
    if m:
        detail["company"] = m.group(1).strip()

    # 投资理念
    m = re.search(r'投资理念[^<]*</[^>]+>(.*?)(?:<div|</td|</section)', text, re.DOTALL)
    if m:
        idea = strip_html(m.group(1))
        if idea and len(idea) > 5:
            detail["invest_idea"] = idea[:500]

    # 简历
    m = re.search(r'个人简历[^<]*</[^>]+>(.*?)(?:<div|</td|</section)', text, re.DOTALL)
    if m:
        resume = strip_html(m.group(1))
        if resume and len(resume) > 5:
            detail["resume"] = resume[:1000]

    # 任职时间
    m = re.search(r'任职时间[^<]*<[^>]*>([^<]+)<', text)
    if m:
        detail["tenure"] = m.group(1).strip()

    return detail


# ============================================================
# AMAC 私募基金搜索（中国证券投资基金业协会）
# 覆盖私募基金管理人和私募基金产品，全市场约24万+只产品
# ============================================================
AMAC_FUND_API = "https://gs.amac.org.cn/amac-infodisc/api/pof/fund"
AMAC_REFERER = "https://gs.amac.org.cn/amac-infodisc/res/pof/fund/fundList.html"


def search_amac_funds(keyword, page_size=20):
    """
    搜索 AMAC 私募基金产品。
    返回: [{fund_name, manager_name, manager_id, fund_no, working_state, ...}]
    """
    from _common import http_post
    import json as _json

    body = {"keyword": keyword, "primaryInvestType": "ALL", "page": 1, "size": page_size}
    text = http_post(AMAC_FUND_API, json_body=body, referer=AMAC_REFERER, timeout=15)
    if not text:
        return []

    try:
        data = _json.loads(text)
    except _json.JSONDecodeError:
        return []

    results = []
    for item in data.get("content", []):
        managers_info = item.get("managersInfo", [])
        mgr_id = ""
        if managers_info and isinstance(managers_info, list) and len(managers_info) > 0:
            mgr_id = str(managers_info[0].get("managerId", ""))

        results.append({
            "fund_name": item.get("fundName", ""),
            "manager_name": item.get("managerName", ""),
            "manager_id": mgr_id,
            "fund_no": item.get("fundNo", ""),
            "working_state": item.get("workingState", ""),
            "establish_date": item.get("establishDate", ""),
        })

    log.info(f"AMAC 搜索「{keyword}」: 找到 {data.get('totalElements', 0)} 只私募基金，返回 {len(results)} 条")
    return results


def search_private_managers(keyword):
    """
    从 AMAC 搜索结果中提取私募基金管理人，去重。
    返回: [{id, name, company, fund_count, fund_names, manager_type, match_reason, match_score}]
    """
    funds = search_amac_funds(keyword)
    if not funds:
        return []

    mgr_map = {}
    kw_clean = keyword.replace(" ", "").replace("　", "")

    for f in funds:
        name = f.get("manager_name", "")
        if not name:
            continue

        if name not in mgr_map:
            # 匹配度评估
            score = 50
            reason = "私募基金管理人（AMAC登记）"
            if kw_clean and kw_clean in name.replace(" ", ""):
                score = 80
                reason = f"管理人名包含「{keyword}」"
            elif keyword in name:
                score = 75
                reason = f"管理人名包含「{keyword}」"

            mgr_map[name] = {
                "id": f"amac_{f.get('manager_id', '')}" if f.get("manager_id") else f"amac_{name}",
                "name": name,
                "company": name,
                "fund_count": 0,
                "fund_names": [],
                "fund_codes": [],
                "tenure_return": "",
                "scale": "",
                "manager_type": "私募",
                "match_reason": reason,
                "match_score": score,
            }

        mgr_map[name]["fund_count"] += 1
        if f.get("fund_name"):
            mgr_map[name]["fund_names"].append(f["fund_name"])

    return list(mgr_map.values())


def search_all_managers(keyword, search_type="auto", company_filter=None):
    """
    同时搜索公募和私募基金经理/管理人，标注类型。
    公募：东方财富全市场（4273+人）
    私募：AMAC 中国证券投资基金业协会（24万+只产品）
    海外/QDII：东方财富已覆盖 QDII 基金经理
    返回合并后的候选列表，按匹配度排序。
    """
    results = []

    # 1. 搜索公募（东方财富）
    try:
        public = search_managers(keyword, search_type, company_filter)
        for m in public:
            m["manager_type"] = "公募"
            results.append(m)
    except Exception as e:
        log.warning(f"公募搜索失败: {e}")

    # 2. 搜索私募（AMAC）- 当关键词可能是管理人名或基金产品名时
    if search_type in ("auto", "company", "product"):
        try:
            private = search_private_managers(keyword)
            results.extend(private)
        except Exception as e:
            log.warning(f"私募搜索失败: {e}")

    # 按匹配度排序
    results.sort(key=lambda x: x.get("match_score", 0), reverse=True)
    return results


def find_and_confirm(keyword, search_type="auto", company_filter=None):
    """
    完整的搜索+确认流程（支持公募+私募多数据源）。
    返回:
        - 唯一匹配: 经理信息 dict
        - 多个匹配: {"candidates": [...], "prompt": "反问文本"}
        - 无匹配: {"candidates": [], "prompt": "提示文本"}
    """
    candidates = search_all_managers(keyword, search_type, company_filter)

    if not candidates:
        return {
            "candidates": [],
            "prompt": (
                f"未找到与「{keyword}」匹配的基金经理。\n"
                "请尝试：\n"
                "  1. 提供更准确的姓名（如「张坤」而非「张」）\n"
                "  2. 提供基金代码（如「110011」）\n"
                "  3. 提供基金产品名（如「易方达蓝筹精选」）\n"
                "  4. 提供基金公司名（如「易方达基金」）\n"
                "  5. 私募基金请提供管理人名称（如「高毅资产」）\n"
                "  注：本skill支持公募、私募（AMAC登记）、QDII三类基金经理"
            ),
        }

    if len(candidates) == 1:
        c = candidates[0]
        mtype = c.get("manager_type", "公募")
        log.info(f"唯一匹配：{c['name']}（{c['company']}）[{mtype}]")
        return c

    return {
        "candidates": candidates,
        "prompt": format_candidates(candidates),
    }


# ============================================================
# CLI 入口
# ============================================================
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("用法: python manager_search.py <关键词> [搜索类型:name/product/company/auto]")
        sys.exit(1)

    keyword = sys.argv[1]
    stype = sys.argv[2] if len(sys.argv) > 2 else "auto"

    print(f"搜索基金经理: '{keyword}' (类型: {stype})\n")

    result = find_and_confirm(keyword, search_type=stype)

    if "candidates" in result and not result["candidates"]:
        print(result["prompt"])
    elif "candidates" in result and result["candidates"]:
        print(result["prompt"])
        print(f"\n请选择序号（1-{len(result['candidates'])}）来确认具体经理")
    else:
        # 唯一匹配
        c = result
        mtype = c.get("manager_type", "公募")
        # 私募管理人的 name 与 company 相同，避免重复显示
        comp = f"（{c['company']}）" if c.get("company") and c["company"] != c["name"] else ""
        print(f"✅ 确认：{c['name']}{comp}[{mtype}]")
        print(f"  ID: {c['id']}")
        print(f"  管理产品: {c.get('fund_count', 0)}只")
        print(f"  任职回报: {c.get('tenure_return', 'N/A')}")
        print(f"  管理规模: {c.get('scale', 'N/A')}")
        if c.get("fund_names"):
            print(f"  代表产品: {', '.join(c['fund_names'][:5])}")
