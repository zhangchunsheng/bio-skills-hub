"""
search_builder.py — 百通检索计划构建器
根据参数和百通数据集映射，生成结构化的检索计划。
由SKILL.md步骤2调用，输出JSON供步骤3使用。

用法:
    python search_builder.py --provinces "广东,浙江" --sources "药监,医保" --keywords "集采" --output plan.json
"""
import argparse
import json
import yaml
import os
from datetime import datetime

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(SKILL_DIR, "references", "config.yaml")
SITES_PATH = os.path.join(SKILL_DIR, "references", "gov_sites.yaml")


def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_sites():
    with open(SITES_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_dataset_mapping():
    """从config.yaml读取百通数据集映射"""
    config = load_config()
    baitong = config.get("baitong", {})
    return baitong.get("datasets", {})


def build_search_text(province, source_type, keywords=None, sites_data=None):
    """
    构造百通 search_dataset 的检索文本。
    结合 gov_sites.yaml 的机构名称增强检索精度。
    """
    # 查找该省份该机构的具体名称
    agency_name = ""
    if sites_data:
        for site in sites_data.get("sites", []):
            if site["province"] == province:
                for agency in site.get("agencies", []):
                    if agency["type"] == source_type:
                        agency_name = agency.get("name", "")
                        break
                break

    # 机构类型对应的检索增强词
    source_keywords_map = {
        "药监": "通知 OR 公告 OR 政策 OR 法规 OR 药品 OR GMP OR GSP OR 飞行检查",
        "医保": "通知 OR 政策 OR 目录 OR 集采 OR 价格 OR DRG OR DIP OR 报销",
        "中医药": "通知 OR 政策 OR 指南 OR 中药 OR 饮片 OR 配方颗粒 OR 中医",
        "卫健委": "通知 OR 公告 OR 规范 OR 临床路径 OR 基药 OR 医院 OR 处方",
    }

    # 优先用机构全名，回退到通用描述
    if agency_name:
        search_text = f"{agency_name} {source_keywords_map.get(source_type, '')}"
    else:
        search_text = f"{province} {source_type} {source_keywords_map.get(source_type, '')}"

    if keywords:
        search_text = f"{keywords} {search_text}"

    return search_text


def resolve_provinces(province_input, sites_data):
    """解析省份参数"""
    if province_input.lower() == "all" or province_input == "全国":
        return [s["province"] for s in sites_data["sites"]]
    return [p.strip() for p in province_input.split(",")]


def resolve_sources(source_input):
    """解析机构类型参数"""
    valid = ["药监", "医保", "中医药", "卫健委"]
    if source_input.lower() == "all":
        return valid
    sources = [s.strip() for s in source_input.split(",")]
    return [s for s in sources if s in valid]


def build_plan(provinces, sources, keywords=None, date_range=7):
    """构建百通检索计划"""
    config = load_config()
    sites_data = load_sites()
    dataset_map = get_dataset_mapping()
    search_config = config.get("baitong", {}).get("search", {})

    tasks = []
    dataset_summary = {}
    task_id = 0

    for source in sources:
        dataset_id = dataset_map.get({
            "药监": "drug_safety",
            "医保": "medical_insurance",
            "中医药": "tcm",
            "卫健委": "health_commission"
        }[source], "")

        if not dataset_id:
            print(f"[WARN] {source} 的百通数据集ID未配置，请在 references/config.yaml 中设置")
            continue

        if dataset_id not in dataset_summary:
            dataset_summary[dataset_id] = {"source": source, "province_count": 0}

        for province in provinces:
            task_id += 1
            search_text = build_search_text(province, source, keywords, sites_data)
            dataset_summary[dataset_id]["province_count"] += 1

            tasks.append({
                "id": task_id,
                "province": province,
                "source_type": source,
                "dataset_id": dataset_id,
                "search_text": search_text,
                "similarity": search_config.get("default_similarity", 0.5),
                "limit": search_config.get("default_limit", 10000),
                "search_mode": search_config.get("default_mode", "mixedRecall"),
                "using_rerank": search_config.get("rerank", True),
                "date_range_days": date_range,
            })

    return {
        "meta": {
            "generated_at": datetime.now().isoformat(),
            "total_tasks": len(tasks),
            "provinces": provinces,
            "sources": sources,
            "keywords": keywords,
            "date_range_days": date_range,
            "datasets": {k: v for k, v in dataset_summary.items()}
        },
        "tasks": tasks,
        "results": []  # 步骤3中由SKILL.md填充
    }


def main():
    parser = argparse.ArgumentParser(description="构建百通数据集检索计划")
    parser.add_argument("--provinces", default="all", help="目标省份，逗号分隔或'all'")
    parser.add_argument("--sources", default="all", help="机构类型，逗号分隔或'all'")
    parser.add_argument("--date-range", type=int, default=7, help="检索时间范围（天）")
    parser.add_argument("--keywords", default=None, help="额外关键词")
    parser.add_argument("--output", default="retrieval_plan.json", help="输出文件路径")
    args = parser.parse_args()

    sites_data = load_sites()
    provinces = resolve_provinces(args.provinces, sites_data)
    sources = resolve_sources(args.sources)

    plan = build_plan(provinces, sources, args.keywords, args.date_range)

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(plan, f, ensure_ascii=False, indent=2)

    print(f"[PLAN] 检索计划已生成 → {args.output}")
    print(f"[PLAN] 省份: {len(provinces)}个 | 机构: {len(sources)}种 | 检索任务: {plan['meta']['total_tasks']}条")
    for ds_id, ds_info in plan["meta"]["datasets"].items():
        print(f"  📦 {ds_info['source']}: {ds_id} ({ds_info['province_count']}省)")

    # 检查未配置的数据集
    dataset_map = get_dataset_mapping()
    for source in sources:
        source_key = {"药监": "drug_safety", "医保": "medical_insurance", "中医药": "tcm", "卫健委": "health_commission"}[source]
        if not dataset_map.get(source_key):
            print(f"[WARN] ⚠️ {source} 数据集ID未配置，请在 config.yaml 的 baitong.datasets 中填入百通数据集ID")


if __name__ == "__main__":
    main()
