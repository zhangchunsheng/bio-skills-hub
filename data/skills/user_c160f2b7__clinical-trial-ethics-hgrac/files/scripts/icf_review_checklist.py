#!/usr/bin/env python3
"""
ICF（知情同意书）合规审查清单生成器
根据试验参数自动生成ICF审查要点清单，帮助快速定位常见合规缺口。

用法：
  python3 scripts/icf_review_checklist.py --target-population adult --sample-collection yes \
    --compensation yes --vulnerable-subjects no

参数：
  --target-population    adult | minor | pregnant | elderly | cognitively-impaired | general
  --sample-collection   yes | no（是否采集生物样本）
  --compensation        yes | no（是否有损害赔偿条款）
  --vulnerable-subjects yes | no（是否涉及弱势群体）
  --biobank             yes | no（是否涉及样本保藏）
  --genetic-testing     yes | no（是否涉及基因检测）
  --multi-center        yes | no（是否多中心）
  --output              输出文件路径（可选）
"""

import argparse
import sys
from datetime import datetime


def check_basic_requirements(target_population):
    """检查ICF基本要素完整性"""
    items = [
        ("试验目的、方法、预期获益和风险", "GCP 2020版第23条第1款", True),
        ("自愿参加、随时退出权利说明", "GCP 2020版第23条第2款", True),
        ("退出不影响正常诊疗", "GCP 2020版第23条第2款", True),
        ("损害赔偿条款与保险说明", "GCP 2020版第23条第3款", True),
        ("个人信息保密措施", "GCP 2020版第23条第4款", True),
        ("数据可被监查/稽查/检查说明", "GCP 2020版第23条第4款", True),
        ("研究者联系方式（24小时）", "GCP 2020版第23条第5款", True),
        ("伦理委员会联系方式", "GCP 2020版第23条第5款", True),
        ("样本采集/保存/使用/销毁说明", "GCP 2020版第23条第6款", True),
        ("语言通俗易懂，避免过于技术化的医学术语", "GCP 2020版第23条", True),
    ]
    return items


def check_population_specific(target_population):
    """检查针对特定人群的ICF要求"""
    specific = []

    if target_population == "minor":
        specific.extend([
            ("监护人签署知情同意书", "GCP 2020版第24条", True),
            ("未成年人（≥8岁）本人的知情同意（视认知能力）", "GCP 2020版第24条", True),
            ("未成年人的特别风险说明（以适合儿童的方式表述）", "ICH-GCP E6(R2) 4.8.14", True),
        ])
    elif target_population == "pregnant":
        specific.extend([
            ("对胎儿潜在风险的特别说明", "ICH-GCP E6(R2) 4.8.14", True),
            ("哺乳期婴儿暴露风险的说明", "ICH-GCP E6(R2) 4.8.14", True),
            ("妊娠期药物安全性数据的充分性说明", "CDE相关指导原则", True),
        ])
    elif target_population == "cognitively-impaired":
        specific.extend([
            ("法定代理人签署知情同意书", "GCP 2020版第24条", True),
            ("独立监查员参与审查知情同意过程", "ICH-GCP E6(R2) 4.8.14", True),
            ("在认知能力允许范围内向受试者本人解释试验信息", "赫尔辛基宣言第28条", True),
        ])
    elif target_population == "elderly":
        specific.extend([
            ("字体大小和排版适合老年人阅读", "实践建议", True),
            ("陪护人员/家属参与的说明", "实践建议", True),
            ("合并用药/并发症相关风险的特殊说明", "实践建议", True),
        ])

    return specific


def check_sample_related(sample_collection, biobank, genetic_testing):
    """检查样本相关知情选项"""
    items = []
    if sample_collection == "yes":
        items.extend([
            ("样本类型和采集量说明", "GCP 2020版第23条第6款", True),
            ("样本保存期限说明", "GCP 2020版第23条第6款", True),
            ("样本用途（主要用于本研究）", "GCP 2020版第23条第6款", True),
            ("样本二次使用的知情选项（同意/拒绝的选择框）", "《人遗条例》实施细则第12条", True),
            ("样本销毁方式的说明", "实践建议", True),
        ])
    if biobank == "yes":
        items.extend([
            ("保藏期限和条件的说明", "《人遗条例》第15条", True),
            ("保藏机构的名称和地址", "实施细则第20条", True),
            ("样本转让/共享的知情同意（是否允许）", "实施细则第22条", True),
            ("退出时样本的处理方式（销毁/继续保存）", "实践建议", True),
        ])
    if genetic_testing == "yes":
        items.extend([
            ("基因检测的具体项目和范围说明", "《人遗条例》第28条", True),
            ("基因数据是否出境及安全措施说明", "《人遗条例》第28条", True),
            ("基因检测结果的告知与否（选择项）", "实践建议", True),
            ("基因数据保密措施的特殊说明", "《个人信息保护法》第28条", True),
        ])
    return items


def check_compensation(compensation):
    """检查赔偿条款"""
    items = []
    items.append(("赔偿条款的有无", "基本要求", compensation == "yes"))
    if compensation == "yes":
        items.extend([
            ("与试验相关的损害（包括非侵权损害）补偿说明", "GCP 2020版第23条第3款", True),
            ("保险覆盖范围说明（临床试验责任险）", "GCP 2020版第33条", True),
            ("赔偿流程和时限说明", "实践建议", True),
            ("免费医疗/补偿的联系方式和负责人", "实践建议", True),
            ("非侵权损害的补偿范围（医疗费+误工费+伤残/死亡赔偿金）", "《民法典》第1219条", True),
        ])
    return items


def check_vulnerable(vulnerable_subjects):
    """检查弱势群体保护"""
    items = []
    if vulnerable_subjects == "yes":
        items.extend([
            ("弱势群体类型的明确标识", "ICH-GCP E6(R2) 4.8.14", True),
            ("额外的保护措施说明", "ICH-GCP E6(R2) 4.8.14", True),
            ("独立监查员的任命和监督说明", "ICH-GCP E6(R2) 4.8.14", True),
            ("退出机制的特殊安排（如需）", "实践建议", True),
        ])
    return items


def main():
    parser = argparse.ArgumentParser(description="ICF知情同意书合规审查清单生成器")
    parser.add_argument("--target-population",
                        choices=["adult", "minor", "pregnant", "elderly",
                                 "cognitively-impaired", "general"],
                        default="adult", help="目标受试者人群")
    parser.add_argument("--sample-collection", choices=["yes", "no"], default="no")
    parser.add_argument("--compensation", choices=["yes", "no"], default="no")
    parser.add_argument("--vulnerable-subjects", choices=["yes", "no"], default="no")
    parser.add_argument("--biobank", choices=["yes", "no"], default="no")
    parser.add_argument("--genetic-testing", choices=["yes", "no"], default="no")
    parser.add_argument("--multi-center", choices=["yes", "no"], default="no")
    parser.add_argument("--output", default="")
    args = parser.parse_args()

    # 组装所有审查项
    all_items = []
    all_items.extend([("", "", False)])  # spacer
    all_items.append(("【ICF基本要素审查】", "", True))
    all_items.extend(check_basic_requirements(args.target_population))

    all_items.append(("", "", False))
    all_items.append(("【目标人群特殊要求】", "", True))
    specific_items = check_population_specific(args.target_population)
    if specific_items:
        all_items.extend(specific_items)
    else:
        all_items.append(("（常规成人试验，无特殊要求）", "", True))

    all_items.append(("", "", False))
    all_items.append(("【生物样本相关审查】", "", True))
    sample_items = check_sample_related(args.sample_collection, args.biobank, args.genetic_testing)
    if sample_items:
        all_items.extend(sample_items)
    else:
        all_items.append(("（不涉及生物样本采集，跳过此部分）", "", True))

    all_items.append(("", "", False))
    all_items.append(("【赔偿条款审查】", "", True))
    all_items.extend(check_compensation(args.compensation))

    all_items.append(("", "", False))
    all_items.append(("【弱势群体保护审查】", "", True))
    all_items.extend(check_vulnerable(args.vulnerable_subjects))

    # 输出
    output_lines = []
    output_lines.append("=" * 60)
    output_lines.append("  知情同意书（ICF）合规审查清单")
    output_lines.append(f"  生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}")
    output_lines.append(f"  目标人群：{args.target_population}")
    output_lines.append("=" * 60)
    output_lines.append("")

    for item, source, _ in all_items:
        if item.startswith("【"):
            output_lines.append(item)
            output_lines.append("-" * 40)
        elif item == "":
            output_lines.append("")
        else:
            output_lines.append(f"  □ {item}")
            if source:
                output_lines.append(f"    依据：{source}")

    output_lines.append("")
    output_lines.append("说明：□ = 待确认 ✓ = 已合规 ✗ = 缺失")
    output_lines.append("请逐项核实后替换标记。")

    result = "\n".join(output_lines)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(result)
        print(f"审查清单已保存至：{args.output}")
    else:
        print(result)


if __name__ == "__main__":
    main()
