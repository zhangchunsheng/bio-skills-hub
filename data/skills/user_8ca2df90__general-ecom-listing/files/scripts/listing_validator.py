#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通用电商 Listing 合规体检脚本（纯标准库）。

功能：
  1. 标题长度 vs 平台上限
  2. 关键词堆砌检测（2/3-gram 频率 >= 3）
  3. 极限词 / 违禁词扫描（内置词库）
输出 Markdown 体检报告。红项（违禁词命中）退出码 1，其余退出码 0。

用法：
  python listing_validator.py --title "保温杯 316不锈钢 500ml" --bullets "12小时保温\n单手开盖" --platform 淘宝
"""
import argparse
import re
import sys

# 各平台标题字数上限（以通用约定为准，非平台官方文档）
PLATFORM_LIMIT = {
    "淘宝": 30, "天猫": 30, "taobao": 30, "tmall": 30,
    "京东": 30, "jd": 30, "jingdong": 30,
    "拼多多": 60, "pdd": 60, "pinduoduo": 60,
    "抖音小店": 30, "抖店": 30, "douyin": 30,
    "小红书": 20, "xhs": 20, "red": 20,
}

# 极限词 / 违禁词库（红项，命中必须改）
FORBIDDEN = [
    "最", "最佳", "最优", "最强", "最大", "最美", "最省", "最便宜",
    "第一", "销量第一", "行业第一", "no.1", "no1", "top1", "top1",
    "顶级", "极品", "极致", "王牌", "冠军",
    "国家级", "国字号", "国家免检",
    "绝对", "百分百", "100%", "一定", " guaranteed", "一定有效",
    "唯一", "独家", "仅有",
    "全网最低", "全网首发", "全网第一",
    "永久", "终生", "永远有效",
    "第一品牌", "领导品牌", "世界领先",
]

# 类目敏感功效词（需资质，无资质不写）
SENSITIVE = [
    "治疗", "防癌", "抗癌", "减肥", "瘦身", "生发", "祛斑", "美白", "消炎",
    "药用", "疗效", "治愈", "包治", "根治",
]


def char_len(s):
    """按字符数（中文 1 字 = 1）"""
    return len(s.strip())


def ngram_freq(text, n):
    """返回 text 中长度为 n 的连续子串频次 dict（仅中文）"""
    cnt = {}
    # 仅取连续中文段做 n-gram
    for seg in re.findall(r"[一-鿿]+", text):
        if len(seg) < n:
            continue
        for i in range(len(seg) - n + 1):
            gram = seg[i:i + n]
            cnt[gram] = cnt.get(gram, 0) + 1
    return cnt


def detect_stuffing(text):
    """堆砌检测：2/3-gram 出现 >= 3 次"""
    hits = []
    for n in (2, 3):
        for gram, c in ngram_freq(text, n).items():
            if c >= 3 and len(gram) >= 2:
                hits.append((gram, c))
    return hits


def scan_words(text, wordlist):
    """扫描命中词"""
    found = []
    low = text.lower()
    for w in wordlist:
        if w.lower() in low:
            found.append(w)
    return found


def validate(title, bullets, platform):
    platform = platform.strip()
    limit = PLATFORM_LIMIT.get(platform, 30)
    lines = re.split(r"[\n;；]+", bullets or "")
    lines = [x.strip() for x in lines if x.strip()]

    red = []      # 必须改
    yellow = []   # 建议改

    # 1. 标题长度
    tlen = char_len(title)
    if tlen > limit:
        yellow.append(f"标题 {tlen} 字，超 {platform} 上限 {limit} 字，需删修饰词保核心词")
    elif tlen == 0:
        red.append("标题为空")

    # 2. 堆砌
    stuff = detect_stuffing(title)
    if stuff:
        for gram, c in stuff:
            yellow.append(f"标题疑似堆砌：「{gram}」出现 {c} 次，建议保留 1 次")

    # 3. 违禁词（红）
    forbid_hits = scan_words(title, FORBIDDEN)
    for ln in lines:
        forbid_hits += scan_words(ln, FORBIDDEN)
    forbid_hits = list(dict.fromkeys(forbid_hits))
    if forbid_hits:
        red.append("极限词/违禁词命中：" + "、".join(forbid_hits) + "（必须改）")

    # 4. 敏感功效词（黄，需资质）
    sens = scan_words(title, SENSITIVE)
    for ln in lines:
        sens += scan_words(ln, SENSITIVE)
    sens = list(dict.fromkeys(sens))
    if sens:
        yellow.append("类目敏感功效词命中：" + "、".join(sens) + "（需有资质，无资质不写）")

    # 报告
    print(f"# Listing 合规体检报告（{platform}）")
    print()
    print(f"- 标题长度：{tlen} 字 / 上限 {limit} 字 → {'✅' if tlen <= limit else '⚠️ 超长'}")
    print(f"- 五点条数：{len(lines)} 条")
    print()
    if red:
        print("## ❌ 红项（必须改）")
        for r in red:
            print(f"  - {r}")
        print()
    if yellow:
        print("## ⚠️ 黄项（建议改）")
        for y in yellow:
            print(f"  - {y}")
        print()
    if not red and not yellow:
        print("## ✅ 体检通过，无明显违规")
        print()
    print("> 发布前以各平台最新规则复核。")
    return len(red) > 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--title", required=True, help="标题文本")
    ap.add_argument("--bullets", default="", help="五点卖点，换行或分号分隔")
    ap.add_argument("--platform", default="淘宝", help="平台名")
    args = ap.parse_args()
    has_red = validate(args.title, args.bullets, args.platform)
    sys.exit(1 if has_red else 0)


if __name__ == "__main__":
    main()
