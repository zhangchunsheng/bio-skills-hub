#!/usr/bin/env python3
"""
药用辅料分类判断与资料清单生成器 (Classification Checklist Generator)

功能：
1. 根据用户输入的辅料基本信息,自动判断登记分类（1.1-1.4 / 2.1-2.4 / 3.1-3.2 / 4）
2. 根据分类结果，生成对应的登记资料清单模板
3. 标记高风险辅料的特殊要求

用法：
    python classification_checklist.py

该脚本通过交互式问答收集辅料信息，输出分类结果和资料清单。
"""

import sys
import json
from datetime import datetime


def classify_excipient(answers: dict) -> dict:
    """
    根据用户输入判断辅料登记分类

    answers 应包含以下键：
        - used_in_drug: bool, 境内外已上市药品中是否有使用历史
        - drug_history_detail: str, 使用历史详情 ("domestic" / "import" / "foreign" / "none")
        - had_food_use: bool, 食品中是否有使用历史
        - had_cosmetic_use: bool, 化妆品中是否有使用历史
        - chemical_modification: str, 化学修饰情况 ("natural" / "single_entity" / "mixture" / "other")
        - route_of_admin: str, 给药途径 ("oral" / "topical" / "injection" / "ophthalmic" / "inhalation" / "implant" / "other")
        - source_type: str, 来源 ("plant" / "animal" / "mineral" / "synthetic" / "fermentation" / "recombinant" / "other")
    """

    classification = {}
    high_risk_reasons = []

    # ---------- 分类判断 ----------
    if not answers.get("used_in_drug", False):
        # 第1类：药品中未有使用历史
        mod = answers.get("chemical_modification", "other")
        if mod == "natural":
            classification["category"] = "1.1"
            classification["name"] = "未经化学修饰的天然来源提取物或发酵产物"
        elif mod == "single_entity":
            classification["category"] = "1.2"
            classification["name"] = "通过化学修饰或合成得到的单一实体"
        elif mod == "mixture":
            classification["category"] = "1.3"
            classification["name"] = "通过化学修饰或合成得到的混合物"
        else:
            classification["category"] = "1.4"
            classification["name"] = "其他（药品中未有使用历史）"

        classification["desc"] = "全新辅料"
        classification["module_8_depth"] = "全面开展药理毒理研究"
    else:
        # 第2类：药品中已有使用历史
        detail = answers.get("drug_history_detail", "foreign")
        if detail == "domestic":
            classification["category"] = "2.1"
            classification["name"] = "在国产上市药品中已使用"
        elif detail == "import":
            classification["category"] = "2.2"
            classification["name"] = "在进口上市药品中已使用"
        elif detail == "foreign":
            classification["category"] = "2.3"
            classification["name"] = "在境外已上市药品中使用"
        else:
            classification["category"] = "2.4"
            classification["name"] = "已有食用历史"

        classification["desc"] = "已有使用历史"
        classification["module_8_depth"] = "提供已有安全性文献/可选择简化研究"

    # ---------- 特殊处理：在药品中未使用但食品/化妆品中有的 ----------
    if not answers.get("used_in_drug", False):
        if answers.get("had_food_use", False):
            classification["category"] = "3.1"
            classification["name"] = "在食品中已有使用历史"
            classification["desc"] = "可参考食品毒理学数据"
            classification["module_8_depth"] = "食品毒理数据参考 + 补充必要的安全性研究"
        elif answers.get("had_cosmetic_use", False):
            classification["category"] = "3.2"
            classification["name"] = "在化妆品中已有使用历史"
            classification["desc"] = "需提供化妆品用途安全性证据"
            classification["module_8_depth"] = "化妆品安全性数据 + 补充必要的毒理研究"

    # ---------- 高风险判断 ----------
    route = answers.get("route_of_admin", "oral")

    high_risk_routes = {
        "injection": "注射剂用辅料",
        "ophthalmic": "眼用制剂用辅料",
        "inhalation": "吸入制剂用辅料",
        "implant": "植入剂用辅料",
    }

    if route in high_risk_routes:
        high_risk_reasons.append(high_risk_routes[route])

    if answers.get("source_type") == "animal":
        high_risk_reasons.append("动物来源（BSE/TSE风险）")
    elif answers.get("source_type") == "recombinant":
        high_risk_reasons.append("转基因/重组来源")

    classification["is_high_risk"] = len(high_risk_reasons) > 0
    classification["high_risk_reasons"] = high_risk_reasons
    classification["route_of_admin"] = route

    return classification


def generate_checklist(classification: dict) -> dict:
    """根据分类结果生成资料清单模板"""

    category = classification["category"]
    is_high_risk = classification["is_high_risk"]
    route = classification["route_of_admin"]

    modules = {
        "1. 登记人基本信息": [
            "登记人名称、注册地址、生产地址",
            "营业执照复印件",
            "药品生产许可证（如有）",
            "授权委托书（如委托代理）",
            "联系人信息",
        ],
        "2. 辅料基本信息": [
            "辅料名称（中文/英文/化学名/CAS号）",
            "结构信息（结构式/分子式/分子量）",
            "理化性质（性状、溶解度、pH、熔点等）",
            "用途信息（功能类别、用量范围、给药途径）",
            "药典收载情况",
            "已有使用历史证据",
        ],
        "3. 生产信息": [
            "工艺流程图",
            "工艺详述（参数控制）",
            "物料控制清单",
            "关键步骤控制",
            "工艺验证方案与报告（至少三批）" if category.startswith(("1.", "2.")) else "工艺验证方案与报告",
            "生产设备清单",
        ],
        "4. 特性鉴定": [
            "结构确证（IR/UV/NMR/MS/XRD等）",
        ],
    }

    # 根据给药途径补充特性鉴定项目
    route_specific = {
        "injection": ["细菌内毒素检查", "无菌检查", "不溶性微粒", "渗透压"],
        "ophthalmic": ["无菌检查", "渗透压", "pH值", "黏度"],
        "inhalation": ["粒径分布", "递送剂量均一性"],
        "oral": ["粒度/粒度分布（如适用）"],
        "topical": ["黏度/流变特性", "pH值"],
    }
    modules["4. 特性鉴定"].extend(route_specific.get(route, []))

    modules["4. 特性鉴定"].extend([
        "杂质研究（有机/无机/残留溶剂/元素杂质）",
        "功能特性（流动性/可压性/粒径/黏度等）",
        "微生物限度",
    ])

    if is_high_risk:
        modules["4. 特性鉴定"].append("**高风险：增加元素杂质（ICH Q3D）评估**")

    modules["5. 质量控制"] = [
        "质量标准草案",
        "方法学验证资料",
        "标准制定依据",
        "对照品来源与标定",
    ]

    modules["6. 批检验报告"] = [
        "不少于连续三批检验报告（全项）",
        "批间一致性评估",
    ]

    modules["7. 稳定性研究"] = [
        "稳定性研究方案",
        "长期稳定性数据",
        "加速稳定性数据",
        "影响因素试验",
        "内包材相容性信息",
        "包装完整性验证",
    ]

    # 模块8 根据分类决定深度
    module8_items = []
    if category.startswith("1."):
        module8_items = [
            "急性毒性试验",
            "重复给药毒性试验",
            "遗传毒性试验",
            "生殖毒性试验（视情况）",
            "局部耐受性试验",
            "过敏/刺激/溶血试验",
            "药代动力学（视情况）",
        ]
    elif category.startswith("2."):
        module8_items = [
            "已有安全性文献综述",
            "过敏/刺激/溶血试验（视给药途径）",
            "酌情补充其他毒理研究",
        ]
    elif category.startswith("3."):
        module8_items = [
            "食品/化妆品已有安全性数据评估",
            "补充必要的毒理研究（视给药途径）",
        ]
    else:
        module8_items = ["按风险确定（建议与CDE沟通交流）"]

    if route in ("injection", "ophthalmic", "inhalation", "implant"):
        module8_items.append(f"**高风险提示：{route}给药途径，建议加强局部耐受性和全身毒性研究**")

    modules["8. 药理毒理研究"] = module8_items

    return modules


def print_report(classification: dict, checklist: dict):
    """打印分类结果和资料清单"""

    sep = "=" * 68

    print(f"""
{sep}
  药用辅料登记分类判断与资料清单
  生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}
{sep}

【分类结果】
  类别：{classification['category']} — {classification['name']}

  判定依据：{classification['desc']}
  给药途径：{classification['route_of_admin']}
  资料要求深度：{classification['module_8_depth']}
""")

    if classification["is_high_risk"]:
        print(f"  ⚠️  高风险辅料！原因：")
        for r in classification["high_risk_reasons"]:
            print(f"      • {r}")
        print(f"  ⚠️  建议：加强质量研究，必要时开展毒理学补充研究")

    print(f"\n{sep}")
    print("【登记资料清单模板】")
    print(sep)

    for module_name, items in checklist.items():
        print(f"\n■ {module_name}")
        for item in items:
            is_special = item.startswith("**") and item.endswith("**")
            if is_special:
                print(f"    ⚠️ {item.strip('*')}")
            else:
                print(f"    □ {item}")

    print(f"""
{sep}
【使用说明】
1. 带"□"的项目为通用要求，请根据辅料实际情况确认是否需要调整
2. 带"⚠️"的项目为特殊要求或风险提示，请重点关注
3. 对于第1类（全新辅料）建议与CDE进行Pre-IND沟通交流
4. 本清单仅供参考，具体以CDE反馈意见为准
{sep}
""")


def interactive_mode():
    """交互式问答"""

    print("\n" + "=" * 68)
    print("  药用辅料分类判断工具 v1.0")
    print("  请提供辅料基本信息以进行自动分类\n")

    answers = {}

    # 使用历史
    print("[问题1/7] 该辅料在境内外上市药品中是否有使用历史？")
    resp = input("  (y/n): ").strip().lower()
    answers["used_in_drug"] = resp in ("y", "yes", "是")

    if answers["used_in_drug"]:
        print("  选择使用历史详情：")
        print("    1) 在国产上市药品中已使用")
        print("    2) 在进口上市药品中已使用")
        print("    3) 在境外已上市药品中使用")
        print("    4) 已有食用历史")
        detail_map = {"1": "domestic", "2": "import", "3": "foreign", "4": "food"}
        resp = input("  请输入编号 (1-4): ").strip()
        answers["drug_history_detail"] = detail_map.get(resp, "foreign")
    else:
        answers["drug_history_detail"] = "none"

    # 食品/化妆品使用历史（仅当药品中使用历史为否时）
    if not answers["used_in_drug"]:
        print("\n[问题2/7] 该辅料在食品中是否有使用历史？ (y/n): ", end="")
        answers["had_food_use"] = input().strip().lower() in ("y", "yes", "是")

        print("[问题3/7] 该辅料在化妆品中是否有使用历史？ (y/n): ", end="")
        answers["had_cosmetic_use"] = input().strip().lower() in ("y", "yes", "是")
    else:
        answers["had_food_use"] = False
        answers["had_cosmetic_use"] = False

    # 化学修饰情况（仅第1类需要详细判断）
    print("\n[问题4/7] 该辅料的化学修饰情况：")
    if not answers["used_in_drug"]:
        print("    1) 天然来源提取物/发酵产物（未经化学修饰）")
        print("    2) 化学合成/修饰的单一实体")
        print("    3) 化学合成/修饰的混合物")
        print("    4) 其他")
        mod_map = {"1": "natural", "2": "single_entity", "3": "mixture", "4": "other"}
        resp = input("  请输入编号 (1-4): ").strip()
        answers["chemical_modification"] = mod_map.get(resp, "natural")
    else:
        answers["chemical_modification"] = "other"

    # 给药途径
    print("\n[问题5/7] 该辅料计划用于的给药途径：")
    print("    1) 口服")
    print("    2) 外用")
    print("    3) 注射")
    print("    4) 眼用")
    print("    5) 吸入")
    print("    6) 植入")
    print("    7) 其他")
    route_map = {
        "1": "oral", "2": "topical", "3": "injection",
        "4": "ophthalmic", "5": "inhalation", "6": "implant", "7": "other"
    }
    resp = input("  请输入编号 (1-7): ").strip()
    answers["route_of_admin"] = route_map.get(resp, "oral")

    # 来源类型
    print("\n[问题6/7] 该辅料的来源类型：")
    print("    1) 植物来源")
    print("    2) 动物来源")
    print("    3) 矿物来源")
    print("    4) 化学合成")
    print("    5) 微生物发酵")
    print("    6) 重组/转基因")
    print("    7) 其他")
    source_map = {
        "1": "plant", "2": "animal", "3": "mineral",
        "4": "synthetic", "5": "fermentation", "6": "recombinant", "7": "other"
    }
    resp = input("  请输入编号 (1-7): ").strip()
    answers["source_type"] = source_map.get(resp, "synthetic")

    # 执行分类
    classification = classify_excipient(answers)
    checklist = generate_checklist(classification)
    print_report(classification, checklist)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--json":
        # JSON 模式：从 stdin 读取参数
        import sys
        input_data = json.loads(sys.stdin.read())
        classification = classify_excipient(input_data)
        checklist = generate_checklist(classification)
        output = {
            "classification": classification,
            "checklist": {k: [i.strip("*") for i in v] for k, v in checklist.items()}
        }
        print(json.dumps(output, ensure_ascii=False, indent=2))
    else:
        interactive_mode()
