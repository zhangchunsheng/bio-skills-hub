#!/usr/bin/env python3
"""
藏药3D打印参数参考脚本
用于快速查询推荐工艺参数

使用方法：
  python3 param-ref.py         → 显示所有工艺的推荐参数
  python3 param-ref.py SSE     → 仅显示SSE工艺参数
  python3 param-ref.py --compare → 显示四种工艺对比表

⚠️ 本脚本仅提供参考参数范围，实际应用需通过实验验证。
"""

import sys

# ============================================================
# 工艺参数数据库
# ============================================================

SSE_PARAMS = {
    "工艺": "半固态挤出 (SSE)",
    "适用场景": "热敏性藏药活性成分、缓释多室制剂",
    "适合的藏药类型": "含挥发油、蛋白类、热不稳定成分的藏药方剂",
    "喷嘴直径(mm)": {"min": 0.2, "recommended": "0.4-0.6", "max": 1.0},
    "打印温度(℃)": {"min": "室温(15-25)", "recommended": "25-35", "max": 40},
    "气压(kPa)": {"min": 10, "recommended": "30-60", "max": 100},
    "打印速度(mm/s)": {"min": 2, "recommended": "6-12", "max": 20},
    "层厚(mm)": {"min": 0.1, "recommended": "0.2-0.3", "max": 0.5},
    "平台温度(℃)": {"min": 15, "recommended": "20-28", "max": 40},
    "填充密度(%)": {"min": 10, "recommended": "50-80", "max": 100},
    "墨水黏度(Pa·s)": {"min": 50, "recommended": "100-1000", "max": 3000},
    "后处理方式": "CaCl₂交联 / 低温干燥 / 冷却固化",
}

FDM_PARAMS = {
    "工艺": "熔融沉积成型 (FDM)",
    "适用场景": "热稳定成分的长效缓释植入剂",
    "适合的藏药类型": "经高温处理仍稳定的矿物药、煅制药材",
    "喷嘴直径(mm)": {"min": 0.2, "recommended": "0.3-0.5", "max": 0.6},
    "打印温度(℃)": {"min": 120, "recommended": "160-200", "max": 220},
    "平台温度(℃)": {"min": 30, "recommended": "40-60", "max": 80},
    "打印速度(mm/s)": {"min": 10, "recommended": "30-60", "max": 100},
    "层厚(mm)": {"min": 0.05, "recommended": "0.1-0.2", "max": 0.4},
    "填充密度(%)": {"min": 10, "recommended": "60-100", "max": 100},
    "丝材MFI(g/10min)": {"min": 1, "recommended": "3-10", "max": 20},
    "冷却风扇": "建议低风扇或关闭，防止翘曲",
    "后处理方式": "退火处理 / 表面抛光",
}

INKJET_PARAMS = {
    "工艺": "喷墨打印 (Inkjet)",
    "适用场景": "低剂量高活性成分的速溶制剂",
    "适合的藏药类型": "贵细药材（牛黄、麝香等微量高效成分）",
    "喷嘴直径(μm)": {"min": 20, "recommended": "40-80", "max": 100},
    "打印温度": "室温",
    "液滴体积(pL)": {"min": 1, "recommended": "10-50", "max": 200},
    "打印速度(mm/s)": {"min": 1, "recommended": "3-8", "max": 15},
    "墨水表面张力(mN/m)": {"min": 25, "recommended": "30-40", "max": 50},
    "墨水黏度(cP)": {"min": 1, "recommended": "3-15", "max": 30},
    "干燥方式": "红外干燥 / 暖风干燥",
    "后处理方式": "复卷 / 分切 / 包装",
}

POWDER_BED_PARAMS = {
    "工艺": "粉末粘结 (Powder Bed)",
    "适用场景": "多孔速溶制剂、复杂几何结构",
    "适合的藏药类型": "大量常规藏药材粉末",
    "粉末粒径(μm)": {"min": 20, "recommended": "50-150", "max": 300},
    "粘结剂流速": "按设备要求调整",
    "饱和度(%)": {"min": 50, "recommended": "80-120", "max": 200},
    "层厚(mm)": {"min": 0.05, "recommended": "0.1-0.2", "max": 0.4},
    "干燥温度(℃)": {"min": 25, "recommended": "35-50", "max": 60},
    "后处理方式": "真空干燥 / 气流除粉 / 浸渍增强",
}

ALL_PARAMS = {
    "SSE": SSE_PARAMS,
    "FDM": FDM_PARAMS,
    "Inkjet": INKJET_PARAMS,
    "PowderBed": POWDER_BED_PARAMS,
}


def print_param_table(params, title):
    """打印单个工艺的参数表"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")
    for key, value in params.items():
        if isinstance(value, dict) and "min" in value:
            print(f"  {key:20s} : {value['min']} ~ {value['recommended']} ~ {value['max']}")
        else:
            print(f"  {key:20s} : {value}")


def print_comparison():
    """打印四种工艺对比表"""
    print(f"\n{'='*100}")
    print(f"  四种3D打印制药工艺参数对比")
    print(f"{'='*100}")
    print(f"  {'参数':20s} {'SSE':25s} {'FDM':25s} {'Inkjet':20s}")
    print(f"  {'-'*20} {'-'*25} {'-'*25} {'-'*20}")
    
    comparisons = [
        ("喷嘴直径", "0.4-0.6mm", "0.3-0.5mm", "40-80μm"),
        ("打印温度", "室温-40℃", "160-200℃", "室温"),
        ("打印速度", "6-12mm/s", "30-60mm/s", "3-8mm/s"),
        ("层厚", "0.2-0.3mm", "0.1-0.2mm", "—"),
        ("后处理", "CaCl₂交联/干燥", "退火/抛光", "红外干燥"),
    ]
    
    for row in comparisons:
        print(f"  {row[0]:20s} {row[1]:25s} {row[2]:25s} {row[3]:20s}")


def main():
    args = sys.argv[1:]
    
    if not args:
        # 无参数：打印所有工艺
        for key in ["SSE", "FDM", "Inkjet", "PowderBed"]:
            print_param_table(ALL_PARAMS[key], ALL_PARAMS[key]["工艺"])
    elif args[0] == "--compare":
        print_comparison()
    elif args[0].upper() in ALL_PARAMS:
        key = args[0].upper()
        print_param_table(ALL_PARAMS[key], ALL_PARAMS[key]["工艺"])
    else:
        print(f"未知参数: {args[0]}")
        print("用法: python3 param-ref.py [SSE|FDM|Inkjet|PowderBed|--compare]")
        sys.exit(1)
    
    print(f"\n{'='*60}")
    print("  ⚠️  以上参数为参考范围，实际需通过实验优化")
    print("  藏药3D打印是前沿交叉领域，请始终将患者安全与药物法规置于首位。")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
