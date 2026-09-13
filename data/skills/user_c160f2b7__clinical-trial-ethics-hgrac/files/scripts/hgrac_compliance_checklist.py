#!/usr/bin/env python3
"""
HGRAC 申报合规检查清单生成器
根据用户输入的试验参数，自动生成申报类型判定和合规检查清单。

用法：
  python3 scripts/hgrac_compliance_checklist.py --trial-phase III --foreign-sponsor yes \
    --sample-type blood --data-export yes --gene-sequencing yes

参数：
  --trial-phase         I | II | III | IV | BE（生物等效性）
  --foreign-sponsor     yes | no
  --sample-type         采集的样本类型（逗号分隔）
  --data-export         是否涉及数据出境 (yes | no)
  --gene-sequencing     是否涉及基因测序 (yes | no)
  --multi-center        是否多中心试验 (yes | no)
  --biobank             是否涉及样本保藏 (yes | no)
  --sample-count        计划采集样本例数
  --output              输出文件路径（可选，默认stdout）
"""

import argparse
import json
import sys
from datetime import datetime, timedelta

# ============================================================
# 申报类型判定规则
# ============================================================

def determine_application_type(args):
    """根据输入判定申报类型"""
    types = []

    # 采集审批判定
    if args.sample_count and int(args.sample_count) >= 500:
        types.append(("采集审批", "大规模采集（≥500例）"))
    elif args.sample_type and "rare" in args.sample_type.lower():
        types.append(("采集审批", "涉及重要遗传家系/特定地区"))

    # 保藏审批判定
    if args.biobank == "yes":
        types.append(("保藏审批", "建设/运营保藏设施"))

    # 国际合作审批判定
    if args.foreign_sponsor == "yes":
        types.append(("国际合作科学研究审批", "涉及外方单位参与研究"))

    # 信息对外提供备案判定
    if args.data_export == "yes" and args.foreign_sponsor != "yes":
        types.append(("信息对外提供或开放使用备案", "仅涉及数据出境，不涉及实体样本"))
    elif args.data_export == "yes" and args.foreign_sponsor == "yes":
        # 已包含在国际合作审批中
        types.append(("（已纳入国际合作审批范围）信息对外提供", "作为国际合作审批的补充要求"))

    if not types:
        types.append(("无需申报（如数据暂不明确，建议进一步确认）", "暂未匹配到法定申报类型"))

    return types


# ============================================================
# 材料清单生成
# ============================================================

MATERIALS_BY_TYPE = {
    "采集审批": [
        ("《人类遗传资源采集申请书》", "必备", "科技部标准模板"),
        ("伦理委员会批件", "必备", "须在有效期内"),
        ("知情同意书样本", "必备", "须含遗传资源相关知情选项"),
        ("试验方案", "必备", "须含版本号和日期"),
        ("申办方资质文件", "必备", ""),
        ("采集样本清单", "必备", "含样本类型、数量、来源"),
        ("采集场所设施说明", "视情形", "如涉及现场采集"),
    ],
    "保藏审批": [
        ("《人类遗传资源保藏申请书》", "必备", "科技部标准模板"),
        ("保藏设施建设/改造方案", "必备", ""),
        ("保藏管理制度文件", "必备", "含SOP、质控方案"),
        ("设施安全与生物安全评估报告", "必备", ""),
        ("伦理委员会批件", "必备", ""),
        ("知情同意书中保藏相关条款", "必备", "须含保藏知情选项"),
    ],
    "国际合作科学研究审批": [
        ("《人类遗传资源国际合作科学研究申请书》", "必备", "科技部标准模板"),
        ("合作各方协议书", "必备", "须含知识产权条款"),
        ("伦理委员会批件", "必备", "组长单位/各参加单位"),
        ("知情同意书样本", "必备", "须含遗传资源相关知情选项"),
        ("试验方案", "必备", "EC批准的最终版本"),
        ("申办方资质文件（含外方认证件）", "必备", "外方须公证+翻译+认证"),
        ("研究者资质证明", "必备", "执业资质+GCP培训证书"),
        ("数据安全与隐私保护方案", "建议准备", "涉及数据出境时必备"),
        ("样本出境清单（如有）", "视情形", ""),
    ],
    "信息对外提供或开放使用备案": [
        ("《信息对外提供备案申请表》", "必备", "科技部标准模板"),
        ("数据信息备份", "必备", "光盘或加密介质"),
        ("数据使用情况说明", "必备", "接收方、用途、安全措施"),
        ("伦理委员会批件", "建议准备", "非强制，但建议同步提交"),
        ("接收方承诺函", "建议准备", ""),
    ],
}

def generate_materials(types):
    """生成材料清单"""
    materials = []
    seen = set()
    for type_name, _ in types:
        if type_name in MATERIALS_BY_TYPE:
            for item, requirement, note in MATERIALS_BY_TYPE[type_name]:
                if item not in seen:
                    materials.append((item, requirement, note))
                    seen.add(item)
    return materials


# ============================================================
# 时限计算
# ============================================================

DEADLINES = {
    "采集审批": 20,
    "保藏审批": 20,
    "国际合作科学研究审批": 20,
    "信息对外提供或开放使用备案": 0,  # 即时备案
}

def calculate_timeline(types):
    """生成申报倒计时时间轴"""
    today = datetime.now().date()
    timeline = []
    for type_name, reason in types:
        if type_name.startswith("（"):
            # 子项，跳过
            continue
        days = DEADLINES.get(type_name)
        if days and days > 0:
            estimated_date = today + timedelta(days=days)
            timeline.append((type_name, days, estimated_date, reason))
        elif days == 0:
            timeline.append((type_name, "即时", today, reason))
        else:
            timeline.append((type_name, "待确认", "待确认", reason))
    return timeline


# ============================================================
# 风险预警
# ============================================================

def generate_risk_warnings(args):
    """生成合规风险预警"""
    warnings = []

    if args.foreign_sponsor == "yes":
        warnings.append(("🔴 外方单位风险",
            "涉及外资申办方，需精确排查外方实际控制关系（含VIE架构）。"
            "建议获取申办方、CRO、中心实验室的股权结构图及实际控制人说明。"))

    if args.gene_sequencing == "yes":
        warnings.append(("🔴 基因测序数据出境风险",
            "涉及基因测序数据，属于重要遗传资源信息。"
            "若向境外提供，须进行安全审查（实施细则第38条）。"))

    if args.data_export == "yes" and args.foreign_sponsor == "yes":
        warnings.append(("🟡 数据出境路径确认",
            "国际合作审批中已涵盖数据出境，但需额外检查："
            "①数据传输加密标准 ②接收方数据处理范围限制 ③数据删除时间节点"))

    if args.multi_center == "yes":
        warnings.append(("🟡 多中心伦理协调",
            "多中心试验须取得组长单位伦理批件，"
            "并汇总各参加单位EC批件。建议提前与各中心EC沟通审查周期。"))

    if not warnings:
        warnings.append(("🟢 暂未发现明显合规风险", "建议仍按要求逐项核对申报材料"))

    return warnings


# ============================================================
# 主函数
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="HGRAC 申报合规检查清单生成器")
    parser.add_argument("--trial-phase", choices=["I", "II", "III", "IV", "BE"],
                        help="试验阶段")
    parser.add_argument("--foreign-sponsor", choices=["yes", "no"],
                        help="是否涉及外资申办方")
    parser.add_argument("--sample-type", default="",
                        help="采集的样本类型（逗号分隔）")
    parser.add_argument("--data-export", choices=["yes", "no"],
                        help="是否涉及数据出境")
    parser.add_argument("--gene-sequencing", choices=["yes", "no"],
                        help="是否涉及基因测序")
    parser.add_argument("--multi-center", choices=["yes", "no"],
                        help="是否多中心试验")
    parser.add_argument("--biobank", choices=["yes", "no"],
                        help="是否涉及样本保藏")
    parser.add_argument("--sample-count", default="",
                        help="计划采集样本例数")
    parser.add_argument("--output", default="",
                        help="输出文件路径（可选）")
    args = parser.parse_args()

    # 检查关键参数
    missing = []
    for attr, name in [("foreign_sponsor", "是否涉及外资申办方(--foreign-sponsor)"),
                       ("data_export", "是否涉及数据出境(--data-export)")]:
        if getattr(args, attr) is None:
            missing.append(name)
    if missing:
        print("❌ 缺少关键参数:"), print(f"   {', '.join(missing)}")
        print("   请补充后再运行。")
        sys.exit(1)

    # 生成结果
    types = determine_application_type(args)
    materials = generate_materials(types)
    timeline = calculate_timeline(types)
    warnings = generate_risk_warnings(args)

    # 输出
    output_lines = []
    output_lines.append("=" * 60)
    output_lines.append("  人类遗传资源申报合规检查报告")
    output_lines.append(f"  生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}")
    output_lines.append("=" * 60)
    output_lines.append("")

    # 申报类型
    output_lines.append("【申报类型判定】")
    for type_name, reason in types:
        output_lines.append(f"  📋 {type_name}")
        output_lines.append(f"     依据：{reason}")
    output_lines.append("")

    # 合规风险
    output_lines.append("【合规风险预警】")
    for severity, desc in warnings:
        output_lines.append(f"  {severity}")
        output_lines.append(f"     {desc}")
    output_lines.append("")

    # 材料清单
    output_lines.append("【材料准备清单】")
    for item, req, note in materials:
        req_flag = "✅" if req == "必备" else "📎"
        output_lines.append(f"  {req_flag} {item} ({req})")
        if note:
            output_lines.append(f"     备注：{note}")
    output_lines.append("")

    # 时限
    output_lines.append("【时限与里程碑】")
    for type_name, days, estimated, reason in timeline:
        if isinstance(days, int):
            output_lines.append(f"  ⏱ {type_name}：法定审核{days}个工作日")
        else:
            output_lines.append(f"  ⏱ {type_name}：{days}")
        output_lines.append(f"     预计完成日期：{estimated}")
    output_lines.append("")

    # 输出
    result = "\n".join(output_lines)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(result)
        print(f"报告已保存至：{args.output}")
    else:
        print(result)


if __name__ == "__main__":
    main()
