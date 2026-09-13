"""
policy_fetcher.py — 百通数据集检索执行器
通过百通MCP的 search_dataset 接口检索政策内容，替代原来的WebSearch方案。

用法（由SKILL.md中的步骤3驱动）:
    此脚本由SKILL.md在工作流中调用，实际检索通过 mcp__baitong__search_dataset 执行。
    脚本负责：
    1. 解析参数→确定目标数据集
    2. 构造检索文本
    3. 标准化检索返回结果
"""
import argparse
import json
import yaml
import os
from datetime import datetime

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(SKILL_DIR, "references", "config.yaml")


def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_dataset_id(source_type):
    """
    根据机构类型获取对应的百通数据集ID。
    优先读取 config.yaml 中的 baitong.datasets 配置。
    """
    config = load_config()
    baitong_config = config.get("baitong", {})
    datasets = baitong_config.get("datasets", {})

    dataset_name_map = {
        "药监": datasets.get("drug_safety", ""),
        "医保": datasets.get("medical_insurance", ""),
        "中医药": datasets.get("tcm", ""),
        "卫健委": datasets.get("health_commission", ""),
    }
    return dataset_name_map.get(source_type, "")


def build_search_text(province, source_type, keywords=None):
    """
    构造百通检索文本。
    格式：省份 + 机构类型 + 政策关键词组合
    """
    base_text = f"{province} {source_type}"

    # 机构类型对应的检索增强词
    source_keywords = {
        "药监": "通知 OR 公告 OR 政策 OR 法规 OR 药品 OR GMP OR GSP OR 飞行检查",
        "医保": "通知 OR 政策 OR 目录 OR 集采 OR 价格 OR DRG OR DIP OR 报销",
        "中医药": "通知 OR 政策 OR 指南 OR 中药 OR 饮片 OR 配方颗粒 OR 中医",
        "卫健委": "通知 OR 公告 OR 规范 OR 临床路径 OR 基药 OR 医院 OR 处方",
    }

    search_text = f"{base_text} {source_keywords.get(source_type, '')}"

    if keywords:
        search_text = f"{keywords} {search_text}"

    return search_text


def generate_retrieval_plan(provinces, sources, keywords=None):
    """
    生成检索计划：每个省份×每个机构类型 = 一条检索任务。
    返回检索任务列表。
    """
    tasks = []
    task_id = 0

    for province in provinces:
        for source in sources:
            task_id += 1
            dataset_id = get_dataset_id(source)
            search_text = build_search_text(province, source, keywords)

            tasks.append({
                "id": task_id,
                "province": province,
                "source_type": source,
                "dataset_id": dataset_id,
                "search_text": search_text,
                "similarity": 0.5,
                "limit": 10000,
                "search_mode": "mixedRecall",
                "using_rerank": True
            })

    return tasks


def format_search_result(task, raw_response):
    """
    将百通 search_dataset 返回的原始结果标准化。
    百通返回格式预期：{ chunks: [{ text: "...", metadata: {...}, similarity: ... }, ...] }
    """
    entries = []
    chunks = raw_response.get("chunks", raw_response.get("results", []))

    for chunk in chunks:
        entry = {
            "title": chunk.get("metadata", {}).get("title", chunk.get("text", "")[:80]),
            "url": chunk.get("metadata", {}).get("url", chunk.get("metadata", {}).get("source", "")),
            "snippet": chunk.get("text", "")[:500],
            "full_text": chunk.get("text", ""),
            "similarity": chunk.get("similarity", 0),
            "date": chunk.get("metadata", {}).get("date", chunk.get("metadata", {}).get("发布日期", "")),
            "source": f"{task['province']}-{task['source_type']}",
        }
        entries.append(entry)

    return {
        "task_id": task["id"],
        "province": task["province"],
        "source_type": task["source_type"],
        "dataset_id": task["dataset_id"],
        "search_text": task["search_text"],
        "search_time": datetime.now().isoformat(),
        "status": "success" if entries else "empty",
        "hits": len(entries),
        "entries": entries,
        "error": None
    }


def main():
    parser = argparse.ArgumentParser(description="百通数据集检索计划生成器")
    parser.add_argument("--provinces", required=True, help="省份列表，逗号分隔")
    parser.add_argument("--sources", required=True, help="机构类型，逗号分隔")
    parser.add_argument("--keywords", default=None, help="额外关键词")
    parser.add_argument("--output", default="retrieval_plan.json", help="检索计划输出文件")
    args = parser.parse_args()

    provinces = [p.strip() for p in args.provinces.split(",")]
    sources = [s.strip() for s in args.sources.split(",")]

    tasks = generate_retrieval_plan(provinces, sources, args.keywords)

    plan = {
        "meta": {
            "generated_at": datetime.now().isoformat(),
            "total_tasks": len(tasks),
            "provinces": provinces,
            "sources": sources,
            "keywords": args.keywords
        },
        "tasks": tasks,
        "results": []  # 由SKILL.md填充实际检索结果
    }

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(plan, f, ensure_ascii=False, indent=2)

    # 输出MCP调用提示，供SKILL.md步骤3使用
    print(f"[PLAN] 检索计划已生成 → {args.output}")
    print(f"[PLAN] 共 {len(tasks)} 条检索任务")
    print(f"[PLAN] 数据集ID：")
    seen_ids = set()
    for t in tasks:
        if t["dataset_id"] not in seen_ids:
            seen_ids.add(t["dataset_id"])
            print(f"  - {t['source_type']}: {t['dataset_id']}")


if __name__ == "__main__":
    main()
