#!/usr/bin/env python3
"""Build a compact V10 visual-fission seed matrix.

This helper creates planning vocabulary only. It never calls an image model.
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path


DEFAULTS = {
    "domain": ["人物生活", "产品品牌", "职场商业", "空间建筑", "旅行自然"],
    "audience": ["城市消费者", "家庭用户", "职场人", "行业从业者", "内容创作者"],
    "content_objective": ["封面停留", "场景解释", "过程证明", "结果展示", "对比选择"],
    "platform": ["小红书", "抖音", "视频号", "公众号", "电商详情页"],
    "scene_moment": ["到达", "准备", "关键动作", "完成", "使用后痕迹"],
    "subject": ["人物", "产品", "空间", "工具设备", "群体活动"],
    "action": ["使用", "操作", "互动", "工作", "比较"],
    "emotional_evidence": ["秩序与专业", "时间压力", "松弛与留白", "关系温度", "完成感"],
    "visual_language": ["纪实观察", "环境肖像", "过程近景", "空间建立", "材质特写"],
    "delivery_variant": ["封面", "场景页", "过程页", "证据页", "结果页"],
}


def merge(primary: str, defaults: list[str]) -> list[str]:
    values: list[str] = []
    if primary.strip():
        values.append(primary.strip())
    for item in defaults:
        if item not in values:
            values.append(item)
    return values[:5]


def build_rows(seed: str, audience: str, platform: str, objective: str) -> list[dict[str, str]]:
    dimensions = {
        "domain": merge(seed, DEFAULTS["domain"]),
        "audience": merge(audience, DEFAULTS["audience"]),
        "content_objective": merge(objective, DEFAULTS["content_objective"]),
        "platform": merge(platform, DEFAULTS["platform"]),
        "scene_moment": DEFAULTS["scene_moment"],
        "subject": DEFAULTS["subject"],
        "action": DEFAULTS["action"],
        "emotional_evidence": DEFAULTS["emotional_evidence"],
        "visual_language": DEFAULTS["visual_language"],
        "delivery_variant": DEFAULTS["delivery_variant"],
    }
    return [
        {"dimension": dimension, "words": "、".join(words)}
        for dimension, words in dimensions.items()
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", required=True, help="Seed topic, industry, product, or content direction.")
    parser.add_argument("--audience", default="", help="Target viewer or buyer.")
    parser.add_argument("--platform", default="", help="Target publishing platform.")
    parser.add_argument("--objective", default="", help="Primary content objective.")
    parser.add_argument("--out", help="Output CSV path; defaults to stdout.")
    args = parser.parse_args()

    rows = build_rows(args.seed, args.audience, args.platform, args.objective)
    fieldnames = ["dimension", "words"]
    if args.out:
        output_path = Path(args.out)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)
    else:
        writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
