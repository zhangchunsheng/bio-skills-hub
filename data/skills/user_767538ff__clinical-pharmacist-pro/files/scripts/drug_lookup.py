#!/usr/bin/env python3
"""
药品说明书查询脚本
数据源：中山大学附属第三医院药学部药品说明书查询系统 (https://www.gzpykj.com/zssyall)
作用：按药品名称（通用名/商品名/其他名称）搜索，返回匹配药品的说明书摘要与详情页链接。

用法：
    python3 drug_lookup.py search <药品名>          # 全站搜索药品，返回匹配列表
    python3 drug_lookup.py detail <mainId>          # 查看某药品的完整说明书
    python3 drug_lookup.py categories               # 列出所有药品分类

输出：JSON 格式，便于 Agent 解析。
"""

import sys
import re
import json
import urllib.request
import urllib.parse
from html import unescape

BASE_URL = "https://www.gzpykj.com/zssyall/wap"
HOSPITAL_NO = "2"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15"
}


def fetch_html(url):
    """抓取页面 HTML"""
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=15) as resp:
        raw = resp.read()
        for enc in ("utf-8", "gbk", "gb2312"):
            try:
                return raw.decode(enc)
            except UnicodeDecodeError:
                continue
        return raw.decode("utf-8", errors="replace")


def fetch_html_post(url, data_dict):
    """通过 POST 提交表单抓取页面"""
    data = urllib.parse.urlencode(data_dict).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=HEADERS, method="POST")
    with urllib.request.urlopen(req, timeout=15) as resp:
        raw = resp.read()
        for enc in ("utf-8", "gbk", "gb2312"):
            try:
                return raw.decode(enc)
            except UnicodeDecodeError:
                continue
        return raw.decode("utf-8", errors="replace")


def strip_tags(html_fragment):
    """去除 HTML 标签，保留纯文本"""
    text = re.sub(r"<[^>]+>", " ", html_fragment)
    text = unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def list_categories():
    """获取所有药品分类"""
    url = f"{BASE_URL}/drug_type.jsp?hospitalNo={HOSPITAL_NO}"
    html = fetch_html(url)

    categories = []
    pattern = re.compile(
        r'href="drug_instruction\.jsp\?typeNo=(\d+)&hospitalNo=\d+&parentId=0"[^>]*>([^<]+)</a>'
    )
    for m in pattern.finditer(html):
        type_no = m.group(1)
        name = strip_tags(m.group(2))
        if name and type_no:
            categories.append({"typeNo": type_no, "name": name})

    return categories


def parse_drug_items(html):
    """从列表页 HTML 中解析药品条目"""
    items = []
    # 匹配 onclick + 标题 + 摘要文本（摘要只取到下一个 onclick 或 div.m-item 之前）
    pattern = re.compile(
        r"onclick=\"location\.href='drug_instruction_view\.jsp\?mainId=([a-f0-9]+)'\""
        r".*?<a class=\"m-item-title\">(.*?)</a>"
        r".*?<p class=\"m-item-summary\"[^>]*>(.*?)</p>",
        re.DOTALL,
    )
    for m in pattern.finditer(html):
        main_id = m.group(1)
        title = strip_tags(m.group(2))
        summary = strip_tags(m.group(3))[:300]
        items.append(
            {
                "mainId": main_id,
                "title": title,
                "preview": summary,
                "detailUrl": f"{BASE_URL}/drug_instruction_view.jsp?mainId={main_id}",
            }
        )
    return items


def search_drug(query):
    """全站搜索药品（利用网站自带的 keyword 搜索功能）"""
    keyword = urllib.parse.quote(query)
    results = []
    page = 1
    max_pages = 10

    while page <= max_pages:
        if page == 1:
            url = f"{BASE_URL}/drug_instruction.jsp?hospitalNo={HOSPITAL_NO}&keyword={keyword}"
            html = fetch_html(url)
        else:
            url = f"{BASE_URL}/drug_instruction.jsp?hospitalNo={HOSPITAL_NO}&keyword={keyword}"
            html = fetch_html_post(
                url,
                {
                    "hospitalNo": HOSPITAL_NO,
                    "keyword": query,
                    "pageNum": str(page),
                },
            )

        items = parse_drug_items(html)
        if not items:
            break

        # 去重
        new_items = [it for it in items if it["mainId"] not in {r["mainId"] for r in results}]
        if not new_items:
            break
        results.extend(new_items)

        # 检查是否还有下一页
        pages = re.findall(r"goPage\((\d+)\)", html)
        page_nums = [int(p) for p in pages if p.isdigit()]
        max_page = max(page_nums) if page_nums else 1
        if page >= max_page:
            break
        page += 1

    return results


def get_drug_detail(main_id):
    """获取某药品的完整说明书"""
    url = f"{BASE_URL}/drug_instruction_view.jsp?mainId={main_id}"
    html = fetch_html(url)
    text = strip_tags(html)

    # 去掉开头的 JS 变量声明等
    js_end = text.find("USER = null;")
    if js_end != -1:
        text = text[js_end + len("USER = null;") :].strip()

    detail = {
        "mainId": main_id,
        "detailUrl": url,
        "rawText": text,
    }

    # 药品名：取文本开头到第一个【之前
    name_match = re.match(r"([^\s【]+)", text)
    if name_match:
        detail["drugName"] = name_match.group(1).strip()

    # 结构化字段提取
    field_patterns = {
        "otherNames": r"【其他名称】(.*?)(?=【|$)",
        "indication": r"【作用与用途】(.*?)(?=【|$)",
        "dosage": r"【(?:用法|用量|用法用量)】(.*?)(?=【|$)",
        "precautions": r"【注意事项】(.*?)(?=【|$)",
        "formulation": r"【制剂】(.*?)(?=【|$)",
        "adverseReactions": r"【不良反应】(.*?)(?=【|$)",
        "contraindications": r"【禁忌】(.*?)(?=【|$)",
        "storage": r"【贮藏】(.*?)(?=【|$)",
    }

    for key, pattern in field_patterns.items():
        m = re.search(pattern, text, re.DOTALL)
        if m:
            detail[key] = m.group(1).strip()

    return detail


def main():
    if len(sys.argv) < 2:
        print(
            json.dumps(
                {"error": "用法: drug_lookup.py search <药品名> | detail <mainId> | categories"},
                ensure_ascii=False,
            )
        )
        sys.exit(1)

    action = sys.argv[1]

    if action == "categories":
        result = list_categories()
        print(json.dumps({"count": len(result), "categories": result}, ensure_ascii=False, indent=2))

    elif action == "search":
        if len(sys.argv) < 3:
            print(json.dumps({"error": "请提供药品名"}, ensure_ascii=False))
            sys.exit(1)
        query = sys.argv[2]
        result = search_drug(query)
        print(
            json.dumps(
                {"query": query, "count": len(result), "results": result},
                ensure_ascii=False,
                indent=2,
            )
        )

    elif action == "detail":
        if len(sys.argv) < 3:
            print(json.dumps({"error": "请提供 mainId"}, ensure_ascii=False))
            sys.exit(1)
        main_id = sys.argv[2]
        result = get_drug_detail(main_id)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    else:
        print(
            json.dumps(
                {"error": f"未知操作: {action}。支持: search, detail, categories"},
                ensure_ascii=False,
            )
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
