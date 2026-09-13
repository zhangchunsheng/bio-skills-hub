"""
risk_calculator.py — 风险评估计算器
基于影响程度×发生概率的风险矩阵，对每条政策进行风险打分和分级。

用法:
    python risk_calculator.py --input analyzed.json --output risk_scored.json
"""
import argparse
import json
from datetime import datetime


def calculate_risk(impact, probability):
    """
    计算风险等级
    - 影响程度 (1-5)
    - 发生概率 (1-5)
    - 风险得分 = impact × probability (1-25)
    """
    score = impact * probability

    if score >= 15:
        level = "red"
        label = "🔴 红色预警"
        action = "需立即响应，进入应急预案"
    elif score >= 8:
        level = "yellow"
        label = "🟡 黄色关注"
        action = "需纳入近期工作计划"
    else:
        level = "green"
        label = "🟢 绿色跟踪"
        action = "纳入常规监控清单"

    return {
        "impact": impact,
        "probability": probability,
        "score": score,
        "level": level,
        "label": label,
        "action": action
    }


def assess_impact(policy):
    """根据政策特征自动评估影响程度（1-5）"""
    title = policy.get("title", "")
    snippet = policy.get("snippet", "")
    policy_type = policy.get("policy_type", "")
    text = title + " " + snippet

    score = 1  # 基础分

    # 政策类型加分
    if policy_type == "法规":
        score += 2
    elif policy_type == "指南":
        score += 1
    elif policy_type == "征求意见稿":
        score += 0  # 尚未生效，影响概率高但当前影响程度中等

    # 关键词加分（直接影响）
    high_impact_keywords = [
        "禁止", "暂停", "取消", "废止", "撤销",
        "纳入医保", "调出目录", "集采", "带量采购",
        "强制", "备案", "飞行检查",
    ]
    medium_impact_keywords = [
        "调整", "修改", "新增", "增加", "试点",
        "DRG", "DIP", "价格联动", "两票制",
    ]

    for kw in high_impact_keywords:
        if kw in text:
            score += 1
            break  # 只加一次

    for kw in medium_impact_keywords:
        if kw in text:
            score += 0.5
            break

    return min(5, max(1, int(round(score))))


def assess_probability(policy):
    """根据政策特征自动评估发生概率（1-5）"""
    urgency = policy.get("urgency", "中")
    policy_type = policy.get("policy_type", "")

    # 紧急程度映射
    urgency_map = {"高": 5, "中": 3, "低": 1}
    score = urgency_map.get(urgency, 3)

    # 已发布或立即生效的政策 → 概率最高
    if policy_type in ["法规", "通知"]:
        score = max(score, 4)
    elif policy_type == "公告":
        score = max(score, 3)
    elif policy_type == "征求意见稿":
        score = min(score, 3)  # 征求意见稿存在变数

    return min(5, max(1, score))


def score_policies(policies):
    """对所有政策进行风险评估"""
    scored = []
    summary = {"total": len(policies), "red": 0, "yellow": 0, "green": 0}

    for policy in policies:
        impact = assess_impact(policy)
        probability = assess_probability(policy)
        risk = calculate_risk(impact, probability)

        policy["risk"] = risk
        summary[risk["level"]] += 1
        scored.append(policy)

    # 按风险得分降序排列
    scored.sort(key=lambda p: p["risk"]["score"], reverse=True)

    return scored, summary


def main():
    parser = argparse.ArgumentParser(description="医药政策风险评估")
    parser.add_argument("--input", required=True, help="分析后的政策JSON文件")
    parser.add_argument("--output", default="risk_scored.json", help="输出文件路径")
    args = parser.parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        data = json.load(f)

    policies = data.get("policies", [])
    scored, summary = score_policies(policies)

    output = {
        "meta": {
            "processed_at": datetime.now().isoformat(),
            "risk_summary": summary
        },
        "policies": scored
    }

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"[OK] 风险评估完成 → {args.output}")
    print(f"[SUMMARY] 🔴红色预警: {summary['red']} | 🟡黄色关注: {summary['yellow']} | 🟢绿色跟踪: {summary['green']}")


if __name__ == "__main__":
    main()
