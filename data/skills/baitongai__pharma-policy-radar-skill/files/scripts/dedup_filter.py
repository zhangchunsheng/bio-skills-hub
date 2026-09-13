"""
dedup_filter.py — 去重与噪音过滤器
基于标题相似度和关键词规则对检索结果去重过滤，输出增量政策清单。

用法:
    python dedup_filter.py --input results.json --history history.json --output filtered.json
    python dedup_filter.py --input results.json --output filtered.json  # 无需历史对比
"""
import argparse
import json
import re
from datetime import datetime


# 噪音关键词 —— 命中任一即过滤
NOISE_PATTERNS = [
    r"人事任免",
    r"会议通知",
    r"节假",
    r"放假",
    r"领导.*调研",
    r"领导.*考察",
    r"党建",
    r"主题党日",
    r"工会",
    r"运动会",
    r"体检通知",
    r"招标公告.*办公",
    r"中标.*办公",
    r"信访",
    r"表彰",
    r"慰问",
]

# 政策相关关键词 —— 命中任一即保留（优先级高于噪音过滤）
POLICY_PATTERNS = [
    r"政策",
    r"通知",
    r"公告",
    r"规定",
    r"办法",
    r"方案",
    r"意见",
    r"指南",
    r"目录",
    r"标准",
    r"规范",
    r"清单",
    r"注册",
    r"审批",
    r"准入",
    r"医保",
    r"集采",
    r"招标",
    r"价格",
    r"支付",
    r"DRG",
    r"DIP",
    r"GMP",
    r"GSP",
    r"飞行检查",
    r"抽检",
    r"召回",
    r"警戒",
    r"临床",
    r"基药",
    r"处方",
    r"中成药",
    r"饮片",
    r"配方颗粒",
]


def title_similarity(t1, t2):
    """计算两个标题的Jaccard相似度（字符集）"""
    s1 = set(t1)
    s2 = set(t2)
    if not s1 or not s2:
        return 0
    intersection = s1 & s2
    union = s1 | s2
    return len(intersection) / len(union)


def is_noise(title):
    """判断是否为噪音（非政策相关）"""
    # 若标题不含任何政策关键词，判定为潜在噪音
    has_policy = any(re.search(p, title) for p in POLICY_PATTERNS)
    if not has_policy:
        return True

    # 若标题命中噪音关键词，但不同时命中政策关键词，则过滤
    for pattern in NOISE_PATTERNS:
        if re.search(pattern, title):
            return True

    return False


def deduplicate(entries, similarity_threshold=0.85):
    """基于标题相似度去重"""
    if not entries:
        return []

    unique = []
    for entry in entries:
        is_dup = False
        for existing in unique:
            sim = title_similarity(entry["title"], existing["title"])
            if sim >= similarity_threshold:
                is_dup = True
                break
        if not is_dup:
            unique.append(entry)

    return unique


def filter_noise(entries):
    """过滤非政策相关条目"""
    filtered = []
    removed = []
    for entry in entries:
        if is_noise(entry.get("title", "")):
            removed.append(entry)
        else:
            filtered.append(entry)
    return filtered, removed


def load_history(path):
    """加载历史分析记录用于去重"""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"analyzed_urls": [], "analyzed_titles": []}


def update_history(history, new_entries, path):
    """更新历史记录"""
    for entry in new_entries:
        if entry.get("url"):
            history.setdefault("analyzed_urls", []).append(entry["url"])
        if entry.get("title"):
            history.setdefault("analyzed_titles", []).append(entry["title"])

    # 保留最近1000条
    if len(history.get("analyzed_urls", [])) > 1000:
        history["analyzed_urls"] = history["analyzed_urls"][-1000:]
    if len(history.get("analyzed_titles", [])) > 1000:
        history["analyzed_titles"] = history["analyzed_titles"][-1000:]

    history["last_updated"] = datetime.now().isoformat()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


def merge_all_entries(results):
    """从results.json中提取所有检索结果的条目"""
    all_entries = []
    for result in results.get("results", []):
        for entry in result.get("entries", []):
            entry["_task_id"] = result["task_id"]
            entry["_province"] = result["province"]
            entry["_agency_type"] = result["agency_type"]
            entry["_agency_name"] = result["agency_name"]
            all_entries.append(entry)
    return all_entries


def main():
    parser = argparse.ArgumentParser(description="去重与过滤医药政策检索结果")
    parser.add_argument("--input", required=True, help="检索结果JSON文件")
    parser.add_argument("--history", default=None, help="历史分析记录JSON（可选）")
    parser.add_argument("--output", default="filtered.json", help="输出文件路径")
    parser.add_argument("--similarity", type=float, default=0.85, help="标题相似度阈值")
    args = parser.parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        results = json.load(f)

    all_entries = merge_all_entries(results)
    total_raw = len(all_entries)
    print(f"[INFO] 原始条目: {total_raw}")

    # 步骤1: 标题去重
    deduped = deduplicate(all_entries, args.similarity)
    dup_removed = total_raw - len(deduped)
    print(f"[INFO] 去重移除: {dup_removed}, 去重后: {len(deduped)}")

    # 步骤2: 噪音过滤
    filtered, noise_entries = filter_noise(deduped)
    print(f"[INFO] 噪音过滤: {len(noise_entries)}, 有效政策: {len(filtered)}")

    # 步骤3: 历史对比（如果提供历史文件）
    history_removed = 0
    history = None
    if args.history:
        history = load_history(args.history)
        analyzed_titles = set(history.get("analyzed_titles", []))
        new_filtered = []
        for entry in filtered:
            if entry["title"] in analyzed_titles:
                history_removed += 1
            else:
                new_filtered.append(entry)
        filtered = new_filtered
        print(f"[INFO] 历史去重: {history_removed}, 最终净增: {len(filtered)}")

    output = {
        "meta": {
            "processed_at": datetime.now().isoformat(),
            "total_raw": total_raw,
            "duplicates_removed": dup_removed,
            "noise_removed": len(noise_entries),
            "history_removed": history_removed,
            "final_count": len(filtered)
        },
        "policies": filtered
    }

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"[OK] 过滤完成 → {args.output}")
    print(f"[SUMMARY] 原始{total_raw} → 去重-{dup_removed} → 噪音-{len(noise_entries)} → 历史-{history_removed} → 最终{len(filtered)}条")

    # 更新历史
    if args.history and history is not None:
        update_history(history, filtered, args.history)


if __name__ == "__main__":
    main()
