#!/usr/bin/env python3
"""Score V10 visual candidates from CSV.

Scores are planning aids, not evidence that content will perform.
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path


FIELDS = [
    "candidate",
    "domain",
    "audience",
    "content_objective",
    "platform",
    "scene_moment",
    "subject",
    "action",
    "emotional_evidence",
    "visual_language",
    "delivery_variant",
    "audience_fit",
    "content_utility",
    "scene_realism",
    "visual_clarity",
    "differentiation",
    "generation_feasibility",
    "asset_reuse",
    "safety",
    "notes",
]

SCORE_FIELDS = [
    "audience_fit",
    "content_utility",
    "scene_realism",
    "visual_clarity",
    "differentiation",
    "generation_feasibility",
    "asset_reuse",
    "safety",
]


def clamp_score(value: str) -> int:
    try:
        score = int(str(value).strip())
    except (TypeError, ValueError):
        score = 1
    return max(1, min(5, score))


def tier(total: int, scores: dict[str, int], candidate: str) -> str:
    if not candidate.strip():
        return "C"
    if scores["safety"] <= 2:
        return "DROP"
    if total >= 36:
        raw = "S"
    elif total >= 31:
        raw = "A"
    elif total >= 25:
        raw = "B"
    else:
        raw = "C"
    if scores["scene_realism"] <= 2 or scores["generation_feasibility"] <= 2:
        if raw in {"S", "A"}:
            return "B"
    return raw


def score_row(row: dict[str, str]) -> dict[str, str]:
    scores = {field: clamp_score(row.get(field, "")) for field in SCORE_FIELDS}
    total = sum(scores.values())
    result = {field: row.get(field, "") for field in FIELDS}
    result.update({field: str(score) for field, score in scores.items()})
    result["total_score"] = str(total)
    result["tier"] = tier(total, scores, result["candidate"])
    if result["tier"] == "S":
        result["decision"] = "prioritize"
    elif result["tier"] == "A":
        result["decision"] = "use_after_tightening"
    elif result["tier"] == "B":
        result["decision"] = "supporting_asset"
    elif result["tier"] == "DROP":
        result["decision"] = "reject_for_safety"
    else:
        result["decision"] = "rebuild_or_drop"
    return result


def print_template() -> None:
    writer = csv.DictWriter(sys.stdout, fieldnames=FIELDS, lineterminator="\n")
    writer.writeheader()
    writer.writerow(
        {
            "candidate": "小红书通勤早餐封面",
            "domain": "家庭生活",
            "audience": "城市通勤人群",
            "content_objective": "封面停留",
            "platform": "小红书",
            "scene_moment": "出门前十分钟",
            "subject": "人物+早餐",
            "action": "装入便当盒",
            "emotional_evidence": "时间压力下的秩序",
            "visual_language": "环境近景",
            "delivery_variant": "3:4封面",
            "audience_fit": "5",
            "content_utility": "5",
            "scene_realism": "5",
            "visual_clarity": "5",
            "differentiation": "4",
            "generation_feasibility": "5",
            "asset_reuse": "5",
            "safety": "5",
            "notes": "示例",
        }
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv_path", nargs="?", help="Input CSV path.")
    parser.add_argument("--out", help="Output CSV path; defaults to stdout.")
    parser.add_argument("--template", action="store_true", help="Print an input CSV template.")
    args = parser.parse_args()

    if args.template:
        print_template()
        return 0
    if not args.csv_path:
        parser.error("csv_path is required unless --template is used")

    input_path = Path(args.csv_path)
    with input_path.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = [score_row(row) for row in csv.DictReader(handle)]

    output_fields = FIELDS + ["total_score", "tier", "decision"]
    if args.out:
        with Path(args.out).open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=output_fields, lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)
    else:
        writer = csv.DictWriter(sys.stdout, fieldnames=output_fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
