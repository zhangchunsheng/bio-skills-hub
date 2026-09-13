#!/usr/bin/env python3
"""
藏药单细胞药理学 — 分子对接分析与活性成分-靶点预测

功能：
1. 指导分子对接实验设计
2. 辅助分析对接结果
3. 预测活性成分与免疫靶点的结合模式
4. 输出结合能评估和可视化建议

用法：
    python molecular_docking_analyzer.py --target "STAT1" --ligands "ligands.sdf" --pocket "ATP-binding"

也支持交互模式：直接运行进入问答式指导。
"""

import argparse
import sys
import csv
from pathlib import Path


# ---------- 预置的藏药活性成分-靶点数据库 ----------

KNOWN_INTERACTIONS = {
    "Salidroside": {
        "targets": ["STAT3", "NFKB1", "Nrf2", "AMPK"],
        "type": "phenylethanoid glycoside",
        "source": "Rhodiola rosea (红景天)",
        "binding_notes": "可能与STAT3的SH2结构域结合，抑制二聚化",
    },
    "Crocin": {
        "targets": ["NLRP3", "NFKB1", "CASP1"],
        "type": "carotenoid glycoside",
        "source": "Crocus sativus (藏红花)",
        "binding_notes": "可能插入NLRP3的NACHT结构域，抑制炎症小体组装",
    },
    "Cordycepin": {
        "targets": ["AMPK", "mTOR", "POLR2A"],
        "type": "nucleoside analog",
        "source": "Cordyceps sinensis (冬虫夏草)",
        "binding_notes": "作为腺苷类似物竞争结合AMPK的腺苷结合位点",
    },
    "Echinacoside": {
        "targets": ["PIK3CA", "AKT1", "NFKB1"],
        "type": "phenylethanoid glycoside",
        "source": "Cistanche deserticola (肉苁蓉)",
        "binding_notes": "可能与PI3K的ATP结合口袋相互作用",
    },
    "Chebulagic acid": {
        "targets": ["STAT3", "RELA", "MMP9"],
        "type": "hydrolyzable tannin",
        "source": "Terminalia chebula (诃子)",
        "binding_notes": "与STAT3的SH2结构域具有高亲和力",
    },
    "Chebulinic acid": {
        "targets": ["RELA", "TNF", "IL6"],
        "type": "hydrolyzable tannin",
        "source": "Terminalia chebula (诃子)",
        "binding_notes": "多酚结构提供多个氢键位点与p65结合",
    },
    "Ligustilide": {
        "targets": ["Nrf2", "KEAP1", "NFKB1"],
        "type": "phthalide",
        "source": "Angelica sinensis (迷果芹/当归)",
        "binding_notes": "与KEAP1的Cys151共价修饰，释放Nrf2",
    },
    "Ellagic acid": {
        "targets": ["NFKB1", "CASP3", "TOP1"],
        "type": "ellagitannin",
        "source": "Phyllanthus emblica (余甘子), Terminalia chebula",
        "binding_notes": "多酚结构，广谱靶点结合",
    },
}


# ---------- 免疫靶点结构信息 ----------

IMMUNE_TARGETS = {
    "STAT1": {
        "pdb_template": "1BF5 (STAT1核心片段)",
        "pocket": "SH2结构域 (Lys584, Arg602, Ser614, Glu616)",
        "therapeutic_relevance": "M1极化主调控因子，藏药抑制STAT1磷酸化可抑制M1",
        "docking_center": "x: 15.2, y: 3.8, z: 20.5 (PDB 1BF5)",
        "box_size": "25Å × 25Å × 25Å",
    },
    "STAT3": {
        "pdb_template": "6NJS (STAT3 SH2结构域与抑制剂复合物)",
        "pocket": "SH2结构域 (Arg609, Ser611, Glu612, Lys591)",
        "therapeutic_relevance": "Th17/炎症相关，藏药成分抑制STAT3可减少IL-17产生",
        "docking_center": "x: 20.5, y: 15.2, z: -5.3 (PDB 6NJS)",
        "box_size": "22Å × 22Å × 22Å",
    },
    "PPARG": {
        "pdb_template": "2PRG (PPAR-γ配体结合域)",
        "pocket": "配体结合口袋 (Ser289, His323, His449, Tyr473)",
        "therapeutic_relevance": "M2极化检查点，激活PPAR-γ促进M2极化",
        "docking_center": "x: 12.0, y: 10.5, z: 8.0 (PDB 2PRG)",
        "box_size": "20Å × 20Å × 20Å",
    },
    "NLRP3": {
        "pdb_template": "7PZD (NLRP3 NACHT结构域)",
        "pocket": "NACHT结构域 (位于ATP结合位点附近)",
        "therapeutic_relevance": "炎症小体核心，藏药成分抑制NLRP3可减少IL-1β释放",
        "docking_center": "x: 5.0, y: 8.0, z: 15.0 (PDB 7PZD)",
        "box_size": "25Å × 25Å × 25Å",
    },
    "NFKB1_p50": {
        "pdb_template": "1SVC (NF-κB p50同源二聚体与DNA复合物)",
        "pocket": "DNA结合界面 (Arg54, Arg56, Tyr57, Lys272)",
        "therapeutic_relevance": "NF-κB通路核心，抑制p50核转位阻断促炎转录",
        "docking_center": "x: 0.0, y: 18.0, z: 10.0 (PDB 1SVC)",
        "box_size": "24Å × 24Å × 24Å",
    },
    "RELA_p65": {
        "pdb_template": "2RAM (p65同源二聚体)",
        "pocket": "NLS结构域/二聚化界面",
        "therapeutic_relevance": "NF-κB亚基，p65核转位是炎症激活的标志事件",
        "docking_center": "x: 5.0, y: 12.0, z: 8.0 (PDB 2RAM)",
        "box_size": "22Å × 22Å × 22Å",
    },
    "KEAP1": {
        "pdb_template": "4CXT (KEAP1 BTB结构域)",
        "pocket": "Kelch结构域 (Arg415, Arg483, Ser508, Ser555)",
        "therapeutic_relevance": "Nrf2负调控因子，抑制KEAP1可激活抗氧化应答",
        "docking_center": "x: -10.0, y: 5.0, z: 15.0 (PDB 4CXT)",
        "box_size": "22Å × 22Å × 22Å",
    },
    "TBX21_Tbet": {
        "pdb_template": "3G5C (T-box转录因子DNA结合域)",
        "pocket": "DNA结合T-box结构域",
        "therapeutic_relevance": "Th1主转录因子，激活IFN-γ表达，调控Th1分化",
        "docking_center": "x: 8.1, y: 12.5, z: 10.8 (PDB 3G5C)",
        "box_size": "24Å × 24Å × 24Å",
    },
    "GATA3": {
        "pdb_template": "4HC7 (GATA3锌指结构域)",
        "pocket": "锌指DNA结合域",
        "therapeutic_relevance": "Th2主转录因子，调控IL-4/IL-5/IL-13转录",
        "docking_center": "x: 0.0, y: 0.0, z: 0.0 (PDB 4HC7)",
        "box_size": "20Å × 20Å × 20Å",
    },
    "RORC_RORgt": {
        "pdb_template": "4YEL (RORγt配体结合域与反向激动剂复合物)",
        "pocket": "配体结合口袋 (His323, His479, Trp502, Phe506)",
        "therapeutic_relevance": "Th17主转录因子，抑制RORγt可减少IL-17产生",
        "docking_center": "x: -5.0, y: 8.0, z: -10.0 (PDB 4YEL)",
        "box_size": "20Å × 20Å × 20Å",
    },
    "FOXP3": {
        "pdb_template": "3QRF (FoxP3叉头结构域)",
        "pocket": "叉头DNA结合域 (Arg341, Asn353, Arg382)",
        "therapeutic_relevance": "Treg主转录因子，激活FoxP3促进Treg分化",
        "docking_center": "x: 10.0, y: 5.0, z: 15.0 (PDB 3QRF)",
        "box_size": "20Å × 20Å × 20Å",
    },
}


# ---------- 分子对接指导 ----------

def recommend_docking_software():
    """推荐分子对接软件"""
    print("\n  🖥 推荐分子对接软件：")
    print("  ┌─────────────────────────────────────────────────────────────┐")
    print("  │ 软件          │ 类型        │ 适用场景              │ 难度  │")
    print("  ├─────────────────────────────────────────────────────────────┤")
    print("  │ AutoDock Vina │ 免费/开源   │ 大多数中药材-蛋白对接  │ ★★   │")
    print("  │ AutoDock GPU  │ 加速版      │ 虚拟筛选大量配体      │ ★★   │")
    print("  │ Glide (SP)    │ 商业(Sch.)  │ 高精度对接            │ ★★★  │")
    print("  │ MOE           │ 商业        │ 一体化药物设计        │ ★★★  │")
    print("  │ Rosetta       │ 学术免费    │ 蛋白-蛋白/肽对接      │ ★★★★ │")
    print("  └─────────────────────────────────────────────────────────────┘")
    print("  推荐：AutoDock Vina（开源、精准度高、社区活跃）\n")


def analyze_binding_energy(energy):
    """评估结合能"""
    if energy <= -10.0:
        return "强结合（Excellent）"
    elif energy <= -8.0:
        return "良好结合（Good）"
    elif energy <= -6.0:
        return "中等结合（Moderate）"
    elif energy <= -4.0:
        return "弱结合（Weak）"
    else:
        return "无显著结合（Poor）"


# ---------- 交互模式 ----------

def interactive_mode():
    """问答式分子对接指导"""
    print("\n" + "=" * 60)
    print("  藏药分子对接分析 — 交互式指导")
    print("=" * 60)

    # 选择靶点
    print("\n  目标免疫靶点列表：")
    targets = list(IMMUNE_TARGETS.keys())
    for i, t in enumerate(targets, 1):
        print(f"  [{i}] {t} — {IMMUNE_TARGETS[t]['therapeutic_relevance'][:60]}...")
    print(f"  [{len(targets)+1}] 手动输入靶点名称")

    try:
        choice = input("\n  请选择靶点编号 (1-{}): ".format(len(targets)+1)).strip()
        idx = int(choice) - 1
        if 0 <= idx < len(targets):
            target = targets[idx]
        else:
            target = input("  请输入靶点名称: ").strip()
    except (ValueError, IndexError):
        target = input("  请输入靶点名称: ").strip()

    if target.upper() in {k.upper() for k in IMMUNE_TARGETS}:
        # 归一化大小写匹配
        target_key = next(k for k in IMMUNE_TARGETS if k.upper() == target.upper())
        info = IMMUNE_TARGETS[target_key]
        print(f"\n  🎯 靶点: {target_key}")
        print(f"     PDB模板: {info['pdb_template']}")
        print(f"     关键口袋: {info['pocket']}")
        print(f"     对接中心: {info['docking_center']}")
        print(f"     盒子大小: {info['box_size']}")
        print(f"     药理意义: {info['therapeutic_relevance']}")
    else:
        print(f"\n  🎯 靶点: {target}")
        print("     自定义靶点，建议您准备PDB结构文件并自行确定口袋位置。")
        print("     推荐软件: AutoDock Vina")

    # 选择配体
    print("\n  💊 藏药活性成分候选列表：")
    herbs = list(KNOWN_INTERACTIONS.keys())
    for i, h in enumerate(herbs, 1):
        print(f"  [{i}] {h} (来源: {KNOWN_INTERACTIONS[h]['source']})")
    print(f"  [{len(herbs)+1}] 自定义SMILES/配体")
    print(f"  [{len(herbs)+2}] 跳过（仅查看靶点信息）")

    try:
        choice2 = input(f"\n  选择配体 (1-{len(herbs)+2}): ").strip()
        idx2 = int(choice2) - 1
        if 0 <= idx2 < len(herbs):
            ligand = herbs[idx2]
            lig_info = KNOWN_INTERACTIONS[ligand]
            print(f"\n  💊 配体: {ligand}")
            print(f"     类型: {lig_info['type']}")
            print(f"     来源: {lig_info['source']}")
            print(f"     已知预测靶点: {', '.join(lig_info['targets'])}")
            print(f"     结合提示: {lig_info['binding_notes']}")

            if target.upper() in {k.upper() for k in IMMUNE_TARGETS}:
                target_key = next(k for k in IMMUNE_TARGETS if k.upper() == target.upper())
                if target_key.upper() in {t.upper() for t in lig_info['targets']}:
                    print(f"\n  ✅ 该配体与靶点存在已知/预测相互作用！")
                else:
                    print(f"\n  ⚠️ 该配体尚未报道与{target_key}的直接作用，值得探索。")
    except (ValueError, IndexError):
        ligand = None
        print("  跳过配体选择。")

    # 推荐对接流程
    print(f"\n{'=' * 60}")
    print("  📋 推荐对接流程：")
    print("=" * 60)
    print("""
  1. 准备蛋白结构：从PDB下载 → 去除水分子/配体 → 加氢 → 分配电荷
  2. 定义对接口袋：
     - 基于已知活性位点（如上所示），或
     - 使用Fpocket/PocketFinder预测
  3. 准备配体结构：SMILES → 3D构象 → 能量最小化(MMFF94)
  4. 运行对接 (AutoDock Vina):
     vina --receptor target.pdbqt --ligand ligand.pdbqt
          --center_x 15.2 --center_y 3.8 --center_z 20.5
          --size_x 25 --size_y 25 --size_z 25
          --exhaustiveness 16 --num_modes 9
  5. 结果分析：
     - 结合能 (Affinity kcal/mol): < -7.0 为良好
     - 结合模式：氢键、疏水作用、π-π堆积
     - 聚类分析：确认结合模式的可靠性
  """)
    print(f"{'=' * 60}")


# ---------- 命令行分析模式 ----------

def analyze_docking(args):
    """命令行对接分析"""
    print("\n" + "=" * 60)
    print("  藏药分子对接分析")
    print("=" * 60)

    target = args.target.upper()
    if target in {k.upper() for k in IMMUNE_TARGETS}:
        target_key = next(k for k in IMMUNE_TARGETS if k.upper() == target)
        info = IMMUNE_TARGETS[target_key]
        print(f"\n  🎯 靶点: {target_key}")
        print(f"     对接口袋: {info['pocket']}")
        print(f"     对接中心: {info['docking_center']}")
        print(f"     盒子大小: {info['box_size']}")
        print(f"     提示: {info['therapeutic_relevance']}")
    else:
        print(f"\n  🎯 靶点: {args.target}")
        print("  ⚠️ 未在预置库中找到该靶点信息")
        print("     请准备PDB结构文件，使用Fpocket检测口袋。")

    if args.ligands:
        print(f"\n  💊 配体文件: {args.ligands}")
    
    if args.pocket:
        print(f"  指定口袋: {args.pocket}")

    if args.energy:
        try:
            energy = float(args.energy)
            assessment = analyze_binding_energy(energy)
            print(f"\n  ⚡ 结合能: {energy:.2f} kcal/mol → {assessment}")
        except ValueError:
            pass

    recommend_docking_software()


# ---------- 主入口 ----------

def main():
    parser = argparse.ArgumentParser(description="藏药分子对接分析助手")
    parser.add_argument("--target", default=None, help="目标蛋白名称")
    parser.add_argument("--ligands", default=None, help="配体文件路径 (如 .sdf / .pdbqt)")
    parser.add_argument("--pocket", default=None, help="口袋描述 (如 'ATP-binding')")
    parser.add_argument("--energy", default=None, help="已获得的结合能值 (kcal/mol)")
    parser.add_argument("--interactive", "-i", action="store_true",
                        help="启动交互模式")
    args = parser.parse_args()

    if args.interactive or not (args.target or args.ligands or args.energy):
        interactive_mode()
    else:
        analyze_docking(args)

    print(f"\n{'=' * 60}")
    print("  💡 分子对接仅为预测工具，结果需结合实验验证")
    print("  推荐下游实验：SPR表面等离子体共振 / MST微量热泳动 / ITC")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
