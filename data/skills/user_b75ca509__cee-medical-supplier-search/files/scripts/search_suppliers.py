#!/usr/bin/env python3
"""
宁波中东欧医药交易(集采)平台 - 供应商搜索脚本

直接请求开放的店铺列表接口并解析 HTML，输出结构化 JSON 数据。

Usage:
    python search_suppliers.py <keyword> [limit]

Examples:
    python search_suppliers.py 美生
    python search_suppliers.py "medical" 10

Output (stdout):
    {
      "code": 0,
      "data": {
        "matched": true,
        "keyword": "美生",
        "total": 1,
        "suppliers": [
          {
            "user_id": 3667,
            "company_name": "NINGBO MEDSUN MEDICAL CO., LTD.",
            "company_name_zh": null,
            "store_logo_url": "https://ceeimg.cbnb.cn/...",
            "contact_number": "0574-86301708",
            "contact_email": "RICHARD@NB-MEDSUN.COM",
            "contact_address": "No. 298 Huangjipu Road, ...",
            "store_intro": "...",
            "goods": [
              {
                "goods_id": 32975,
                "goods_name": "ADJUSTABLE PUSHBUTTON ACTIVATED SAFETY LANCET (MODEL XA)",
                "image_url": "https://ceeimg.cbnb.cn/...",
                "goods_url": "/mall/MallGoods/goodDetail?goods_id=32975"
              }
            ]
          }
        ]
      }
    }
"""

import json
import re
import sys
import urllib.parse
import urllib.request

BASE_URL = "https://globalmedsource.cn/mall/MallStores/storeList"

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
)


def fetch_page(keyword, limit=5):
    """Request the store list page and return HTML text."""
    params = urllib.parse.urlencode(
        {"page": 1, "limit": limit, "keyword": keyword, "search_type": "Supplier"}
    )
    url = f"{BASE_URL}?{params}"
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        },
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        return resp.read().decode("utf-8", errors="ignore")


def clean_html(text):
    """Strip HTML tags, keep <br> as newlines, normalize whitespace."""
    if text is None:
        return None
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", "", text)
    text = text.replace("&nbsp;", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n", text)
    return text.strip()


def extract_value(item_html, label):
    """Extract a labeled value from the intro_box list, e.g. 'Contact number: VALUE'."""
    m = re.search(
        label
        + r":\s*</span>\s*<span class=\"value_box col-xs-8\">\s*(.*?)\s*</span>",
        item_html,
        re.S,
    )
    return clean_html(m.group(1)) if m else None


def parse_suppliers(html):
    """Parse store list HTML into structured supplier data."""
    # Total result count
    m = re.search(r'id="totalGoodCount"\s+value="(\d+)"', html)
    total = int(m.group(1)) if m else 0

    suppliers = []
    # Each supplier entry: <li class="store_item">...</li>
    # Use lookahead to avoid cutting at nested <li> inside goods list;
    # store_list section ends at </section>
    items = re.findall(
        r'<li\s+class="store_item">(.*?)(?=<li\s+class="store_item">|</section>)',
        html,
        re.S,
    )

    for item in items:
        supplier = {}

        # user_id from link: /mall/MallStores/home?userSupplier_id=3667
        m = re.search(r"userSupplier_id=(\d+)", item)
        if m:
            supplier["user_id"] = int(m.group(1))

        # company name from title link (tags may contain newlines)
        m = re.search(
            r'mall_subtitle">\s*<a href="[^"]*">\s*(.*?)\s*</a>', item, re.S
        )
        if m:
            supplier["company_name"] = clean_html(m.group(1))

        # store logo (img tag may wrap lines)
        m = re.search(r'logo_box"><img\s+src="([^"]+)"', item, re.S)
        if m:
            supplier["store_logo_url"] = m.group(1)

        # labeled fields
        supplier["contact_number"] = extract_value(item, "Contact number")
        supplier["contact_email"] = extract_value(item, "E-mail")
        supplier["contact_address"] = extract_value(item, "Address")

        # goods
        goods = []
        goods_matches = re.findall(
            r'<a href="/mall/MallGoods/goodDetail\?goods_id=(\d+)">\s*'
            r'<div class="img_box"><img\s+src="([^"]+)"[^>]*>\s*</div>\s*'
            r'<div class="name_box">\s*(.*?)\s*</div>',
            item,
            re.S,
        )
        for gid, img, name in goods_matches:
            goods.append(
                {
                    "goods_id": int(gid),
                    "goods_name": clean_html(name),
                    "image_url": img,
                    "goods_url": f"/mall/MallGoods/goodDetail?goods_id={gid}",
                }
            )
        supplier["goods"] = goods

        # store intro
        m = re.search(r'store_intro_box">.*?intro_text">(.*?)</div>', item, re.S)
        if m:
            supplier["store_intro"] = clean_html(m.group(1))

        suppliers.append(supplier)

    return total, suppliers


def main():
    if len(sys.argv) < 2:
        print(json.dumps({
            "code": 1,
            "msg": "请提供企业名称关键词，例如：python search_suppliers.py 美生",
            "success": False,
        }, ensure_ascii=False))
        sys.exit(1)

    keyword = sys.argv[1].strip()
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else 5

    try:
        html = fetch_page(keyword, limit)
    except Exception as exc:
        print(json.dumps({
            "code": 1,
            "msg": f"请求平台页面失败：{exc}",
            "success": False,
        }, ensure_ascii=False))
        sys.exit(1)

    total, suppliers = parse_suppliers(html)

    result = {
        "code": 0,
        "data": {
            "matched": total > 0 and len(suppliers) > 0,
            "keyword": keyword,
            "total": total,
            "suppliers": suppliers,
        },
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
