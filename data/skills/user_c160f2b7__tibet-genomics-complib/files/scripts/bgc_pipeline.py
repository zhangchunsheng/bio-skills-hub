#!/usr/bin/env python3
"""
bgc_pipeline.py — 藏药基因组学与天然多样性成分库构建辅助工具 (v1.0)

本脚本提供四个核心功能模块，覆盖从 antiSMASH 输出解析到虚拟成分库构建的
全流程数据处理。所有函数均以 pandas DataFrame 为中间桥梁，方便管道集成。

依赖环境:
    pip install biopython rdkit-pypi pandas numpy openbabel

模块与用法:
    # 1. 解析 antiSMASH 输出 → BGC 摘要 CSV
    python bgc_pipeline.py parse --gbk-dir antismash_outputs/ --output-csv bgc_summary.csv

    # 2. 提取 BGC 核心酶蛋白序列
    python bgc_pipeline.py extract --gbk-dir antismash_outputs/ --output-fasta bgc_enzymes.faa

    # 3. 构建虚拟化合物库 (基于 BGC 摘要)
    python bgc_pipeline.py build_library --bgc-csv bgc_summary.csv --output-sdf library.sdf --max 10

    # 4. 计算分子描述符与类药性
    python bgc_pipeline.py descriptors --sdf-file library.sdf --output-csv descriptors.csv
"""

import os
import sys
import re
import csv
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

# 生物信息学模块
from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord

# RDKit 化学信息学 (optional — 未安装时给出提示)
try:
    from rdkit import Chem
    from rdkit.Chem import Descriptors, AllChem, Lipinski, rdMolDescriptors
    from rdkit.Chem.Descriptors import MolWt, MolLogP, NumHAcceptors, NumHDonors
    RDKIT_AVAILABLE = True
except ImportError:
    RDKIT_AVAILABLE = False
    print("⚠️  RDKit 未安装。'build_library' 和 'descriptors' 模式不可用。", file=sys.stderr)

# ─── 日志配置 ─────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("bgc_pipeline")

# ─── 常量 ─────────────────────────────────────────────────────────────────────

KEY_ENZYME_KEYWORDS = {
    "polyketide_synthase", "pks",
    "non-ribosomal peptide synthetase", "nrps",
    "terpene_synthase", "terpene_cyclase",
    "cytochrome_p450", "cyp450",
    "udp-glycosyltransferase", "ugt",
    "methyltransferase", "o-methyltransferase",
    "acyltransferase",
    "aba_superfamily",
}

# BGC 类型 → 简化骨架 SMARTS 模板 (用于虚拟库构建)
SKELETON_TEMPLATES: Dict[str, str] = {
    "terpene": "CC(=C)C",          # 异戊二烯单元
    "sesquiterpene": "CC1=CCCC=C1",
    "diterpene": "CC1(C)CCCC1C=CC2=C(C)CCC2",
    "type_i_pks": "CC(=O)CC(=O)",  # 聚酮链
    "type_ii_pks": "C1=CC(=O)C(=O)C=C1",
    "type_iii_pks": "c1c(O)ccc(O)c1",
    "nrps": "NC(=O)CNC(=O)",       # 多肽骨架
    "nrps_like": "NC(=O)CCC(=O)N",
    "alkaloid": "c1ccncc1",        # 吡啶碱
    "tropane_alkaloid": "C1CCN2CC2C1",
    "flavonoid": "c1c(O)cc2OC(=CC(=O)c2c1)O",
    "lignan": "c1ccc(CCO)cc1",
    "saccharide": "OC1C(O)C(O)C(O)CO1",
}

# ─── 功能函数 ───────────────────────────────────────────────��─────────────────

def parse_antismash_output(gbk_dir: str, output_csv: Optional[str] = None) -> pd.DataFrame:
    """
    批量解析 antiSMASH 输出的 GenBank (.gbk) 文件，提取 BGC 元数据。

    提取字段包括:
        - sample_id: 样本标识 (目录名)
        - cluster_number: BGC 编号
        - cluster_type: 产物类型 (antiSMASH 标注)
        - contig: 所在的 contig ID
        - start, end: BGC 在 contig 上的起止坐标
        - length: BGC 长度
        - mibig_hit: 匹配的 MIBiG 同源簇
        - similarity: 相似度百分比

    Parameters
    ----------
    gbk_dir : str
        antiSMASH 输出根目录 (包含各样本子目录内的 .gbk 文件)
    output_csv : str, optional
        输出 CSV 路径，为 None 时仅返回 DataFrame

    Returns
    -------
    pd.DataFrame
        包含 BGC 摘要信息的表格
    """
    gbk_dir = Path(gbk_dir)
    if not gbk_dir.exists():
        raise FileNotFoundError(f"目录不存在: {gbk_dir}")

    records: List[Dict] = []
    gbk_files = sorted(gbk_dir.rglob("*.gbk"))
    logger.info(f"发现 {len(gbk_files)} 个 GBK 文件")

    for gbk_file in gbk_files:
        # 采样本名称：取 GBK 文件的倒数第 3 级目录
        sample = gbk_file.parent.parent.name
        try:
            for record in SeqIO.parse(gbk_file, "genbank"):
                for feat in record.features:
                    if feat.type == "cluster":
                        cluster_num = feat.qualifiers.get("cluster_number", [""])[0]
                        cluster_type = feat.qualifiers.get("product", [""])[0]
                        mibig = feat.qualifiers.get("most_similar_mibig", [""])[0]
                        sim = feat.qualifiers.get("similarity", [""])[0]

                        records.append({
                            "sample_id": sample,
                            "cluster_number": cluster_num,
                            "cluster_type": cluster_type,
                            "contig": record.id,
                            "start": int(feat.location.start),
                            "end": int(feat.location.end),
                            "length": len(feat.location),
                            "mibig_hit": mibig.strip(),
                            "similarity": sim.strip(),
                        })
        except Exception as e:
            logger.warning(f"解析 {gbk_file.name} 失败: {e}")

    df = pd.DataFrame(records)

    # 类型统计
    type_counts = df["cluster_type"].value_counts()
    logger.info(f"提取到 {len(df)} 个 BGC 记录")
    logger.info(f"BGC 类型分布:\n{type_counts.to_string()}")

    if output_csv:
        df.to_csv(output_csv, index=False)
        logger.info(f"BGC 摘要已保存至 {output_csv}")

    return df


def extract_bgc_sequences(
    gbk_dir: str,
    output_fasta: Optional[str] = None,
    min_seq_len: int = 50,
) -> List[SeqRecord]:
    """
    从 antiSMASH GBK 文件中提取核心生物合成酶的蛋白序列。

    筛选条件: 保留功能描述中包含 KEY_ENZYME_KEYWORDS 的 CDS 特征。
    忽略长度 < min_seq_len 的短序列。

    Parameters
    ----------
    gbk_dir : str
        antiSMASH 输出的 GBK 目录
    output_fasta : str, optional
        输出 FASTA 文件路径
    min_seq_len : int
        最小蛋白序列长度，默认 50 aa

    Returns
    -------
    List[SeqRecord]
        蛋白序列的 SeqRecord 列表
    """
    gbk_dir = Path(gbk_dir)
    if not gbk_dir.exists():
        raise FileNotFoundError(f"目录不存在: {gbk_dir}")

    seq_records: List[SeqRecord] = []
    gbk_files = sorted(gbk_dir.rglob("*.gbk"))
    logger.info(f"搜索 {len(gbk_files)} 个 GBK 文件中的核心酶基因")

    for gbk_file in gbk_files:
        sample = gbk_file.parent.parent.name
        try:
            for record in SeqIO.parse(gbk_file, "genbank"):
                for feat in record.features:
                    if feat.type != "CDS":
                        continue

                    # 聚合多个描述字段
                    gene_func = feat.qualifiers.get("function", [""])[0].lower()
                    product = feat.qualifiers.get("product", [""])[0].lower()
                    gene = feat.qualifiers.get("gene", [""])[0].lower()
                    ec_num = feat.qualifiers.get("EC_number", [""])[0]
                    desc_text = f"{gene_func} {product} {gene}"

                    # 匹配关键酶关键词
                    if not any(kw in desc_text for kw in KEY_ENZYME_KEYWORDS):
                        continue
                    if "translation" not in feat.qualifiers:
                        continue

                    prot_seq = feat.qualifiers["translation"][0]
                    if len(prot_seq) < min_seq_len:
                        continue

                    locus_tag = feat.qualifiers.get(
                        "locus_tag", [f"bgc_gene_{len(seq_records)}"]
                    )[0]

                    seq_rec = SeqRecord(
                        Seq(prot_seq),
                        id=f"{sample}|{locus_tag}",
                        description=f"{gene_func[:80]} [{ec_num}]"
                    )
                    seq_records.append(seq_rec)

        except Exception as e:
            logger.warning(f"处理 {gbk_file.name} 出错: {e}")

    logger.info(f"提取到 {len(seq_records)} 条核心酶蛋白序列")

    if output_fasta:
        with open(output_fasta, "w") as f:
            SeqIO.write(seq_records, f, "fasta")
        logger.info(f"蛋白序列已保存至 {output_fasta}")

    return seq_records


def build_virtual_library(
    bgc_csv: str,
    output_sdf: str = "virtual_library.sdf",
    max_compounds_per_cluster: int = 10,
) -> int:
    """
    基于 BGC 摘要 CSV 构建虚拟化合物库 (SDF)。

    根据 BGC 类型从 SKELETON_TEMPLATES 中选取骨架模板生成基础分子，
    写入 SDF 文件并附带 BGC 元数据。

    Parameters
    ----------
    bgc_csv : str
        parse_antismash_output() 输出的 CSV 文件路径
    output_sdf : str
        输出 SDF 文件路径
    max_compounds_per_cluster : int
        每个 BGC 最多生成的化合物数 (用于未来扩展)

    Returns
    -------
    int
        生成的化合物总数
    """
    if not RDKIT_AVAILABLE:
        raise ImportError("需要 RDKit 支持，请执行: pip install rdkit-pypi")

    df = pd.read_csv(bgc_csv)
    writer = Chem.SDWriter(output_sdf)
    compound_count = 0

    for _, row in df.iterrows():
        bgc_type = str(row["cluster_type"]).lower().replace(" ", "_")

        # 匹配 BGC 类型与骨架模板
        template_smarts = None
        for key, smarts in SKELETON_TEMPLATES.items():
            if key in bgc_type:
                template_smarts = smarts
                break

        if template_smarts is None:
            continue

        mol = Chem.MolFromSmarts(template_smarts)
        if mol is None:
            continue

        # 转为真实分子并添加 3D 构象
        mol = Chem.AddHs(mol)
        try:
            params = AllChem.EmbedMultipleConfs(mol, numConfs=3, randomSeed=42)
            if params == 0:
                AllChem.EmbedMolecule(mol, randomSeed=42)
            AllChem.MMFFOptimizeMolecule(mol)
        except Exception:
            continue

        mol = Chem.RemoveHs(mol)

        # 写入元数据属性
        mol.SetIntProp("cluster_number", int(float(row.get("cluster_number", 0))))
        mol.SetProp("cluster_type", row.get("cluster_type", ""))
        mol.SetProp("sample_id", str(row.get("sample_id", "")))
        mol.SetProp("contig", str(row.get("contig", "")))

        cluster_num = int(float(row.get("cluster_number", 0)))
        mol.SetProp("_Name", f"TGP_{compound_count:05d}_C{cluster_num}")

        writer.write(mol)
        compound_count += 1
        compound_count += 0  # 保留 max_compounds_per_cluster 扩展点

    writer.close()
    logger.info(
        f"虚拟库已保存至 {output_sdf}，共 {compound_count} 个化合物"
    )
    return compound_count


def compute_descriptors(
    sdf_file: str,
    output_csv: Optional[str] = None,
) -> pd.DataFrame:
    """
    计算化合物库 (SDF) 的分子描述符与类药性评估。

    计算描述符:
        - MW, logP, HBA, HBD, TPSA
        - RotatableBonds, RingCount, AromaticRings
        - Lipinski 五规则违反数 (Ro5_Violations)

    Parameters
    ----------
    sdf_file : str
        输入 SDF 文件路径
    output_csv : str, optional
        输出 CSV 路径

    Returns
    -------
    pd.DataFrame
        包含所有化合物描述符的表格
    """
    if not RDKIT_AVAILABLE:
        raise ImportError("需要 RDKit 支持，请执行: pip install rdkit-pypi")

    suppl = Chem.SDMolSupplier(sdf_file)
    descriptors: List[Dict] = []

    for mol in suppl:
        if mol is None:
            continue

        mw = MolWt(mol)
        logp = MolLogP(mol)
        hba = NumHAcceptors(mol)
        hbd = NumHDonors(mol)
        tpsa = Descriptors.TPSA(mol)

        ro5_violations = sum([
            mw > 500,
            logp > 5,
            hba > 10,
            hbd > 5,
        ])

        desc = {
            "compound_id": mol.GetProp("_Name") if mol.HasProp("_Name") else "unknown",
            "MW": round(mw, 2),
            "logP": round(logp, 2),
            "HBA": hba,
            "HBD": hbd,
            "TPSA": round(tpsa, 2),
            "RotBonds": Descriptors.NumRotatableBonds(mol),
            "RingCount": Descriptors.RingCount(mol),
            "AromaticRings": Descriptors.NumAromaticRings(mol),
            "HeavyAtomCount": mol.GetNumHeavyAtoms(),
            "FractionSp3": round(
                rdMolDescriptors.CalcFractionCSP3(mol), 3
            ),
            "Ro5_Violations": ro5_violations,
            "Passes_Ro5": ro5_violations <= 1,
        }

        # 保留 SDF 中的源属性
        for prop_name in ("sample_id", "cluster_type", "cluster_number", "contig"):
            if mol.HasProp(prop_name):
                desc[prop_name] = mol.GetProp(prop_name)

        descriptors.append(desc)

    df = pd.DataFrame(descriptors)
    logger.info(f"计算了 {len(df)} 个化合物的描述符")
    logger.info(f"Ro5 通过率: {df['Passes_Ro5'].mean():.1%}")

    if output_csv:
        df.to_csv(output_csv, index=False)
        logger.info(f"描述符表已保存至 {output_csv}")

    return df


# ─── 简易新奇度评分 ──────────────────────────────────────────────────────────

def calculate_novelty_score(
    df_bgc: pd.DataFrame,
    output_csv: Optional[str] = None,
) -> pd.DataFrame:
    """
    计算 BGC 的新奇度分数 (0–1)。

    基于 MIBiG 相似度计算: novelty = 1 - similarity_normalized
    当无 MIBiG hit 时赋予最高新奇度 (1.0)。

    Parameters
    ----------
    df_bgc : pd.DataFrame
        包含 'similarity' 列的 BGC 摘要表
    output_csv : str, optional
        输出路径

    Returns
    -------
    pd.DataFrame
        新增 'novelty_score' 和 'priority' 列的 BGC 表
    """
    def _parse_sim(val):
        """将 '100%' 或 '0.75' 转为浮点"""
        if pd.isna(val) or val == "":
            return 0.0
        val = str(val).strip().replace("%", "")
        try:
            return float(val) / 100 if float(val) > 1 else float(val)
        except ValueError:
            return 0.0

    df = df_bgc.copy()
    df["_sim"] = df["similarity"].apply(_parse_sim)
    df["novelty_score"] = (1.0 - df["_sim"]).clip(0, 1)

    # 优先级分类
    def _priority(score):
        if score >= 0.7:
            return "高 (High)"  # 最可能产生新颖化合物
        elif score >= 0.3:
            return "中 (Medium)"
        else:
            return "低 (Low)"   # 已知簇，优先度低

    df["priority"] = df["novelty_score"].apply(_priority)
    df = df.drop(columns=["_sim"])

    logger.info(
        f"新奇度分布: 高 {sum(df['priority'] == '高 (High)')} | "
        f"中 {sum(df['priority'] == '中 (Medium)')} | "
        f"低 {sum(df['priority'] == '低 (Low)')}"
    )

    if output_csv:
        df.to_csv(output_csv, index=False)
        logger.info(f"新奇度评分已保存至 {output_csv}")

    return df


# ─── CLI 入口 ──────────────────────────────────────────────────────────────────

def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="藏药基因组学成分库构建工具 v1.0",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
用法示例:
  %(prog)s parse --gbk-dir ./antismash_outputs/ --output-csv bgc_summary.csv
  %(prog)s extract --gbk-dir ./antismash_outputs/ --output-fasta enzymes.faa
  %(prog)s build_library --bgc-csv bgc_summary.csv --output-sdf lib.sdf
  %(prog)s descriptors --sdf-file lib.sdf --output-csv desc.csv
        """,
    )

    subparsers = parser.add_subparsers(dest="mode", help="运行模式")

    # parse
    p_parse = subparsers.add_parser("parse", help="解析 antiSMASH 输出 → BGC 摘要 CSV")
    p_parse.add_argument("--gbk-dir", required=True, help="antiSMASH GBK 目录")
    p_parse.add_argument("--output-csv", default="bgc_summary.csv", help="输出 CSV 路径")

    # extract
    p_extract = subparsers.add_parser("extract", help="提取 BGC 核心酶蛋白序列")
    p_extract.add_argument("--gbk-dir", required=True, help="antiSMASH GBK 目录")
    p_extract.add_argument("--output-fasta", default="bgc_enzymes.faa", help="输出 FASTA 路径")
    p_extract.add_argument("--min-len", type=int, default=50, help="最小氨基酸长度")

    # build_library
    p_lib = subparsers.add_parser("build_library", help="构建虚拟化合物库 (SDF)")
    p_lib.add_argument("--bgc-csv", required=True, help="BGC 摘要 CSV (parse 输出)")
    p_lib.add_argument("--output-sdf", default="virtual_library.sdf", help="输出 SDF")
    p_lib.add_argument("--max", type=int, default=10, help="每 BGC 最多化合物数")

    # descriptors
    p_desc = subparsers.add_parser("descriptors", help="计算分子描述符")
    p_desc.add_argument("--sdf-file", default="virtual_library.sdf", help="输入 SDF")
    p_desc.add_argument("--output-csv", default="descriptors.csv", help="输出 CSV")

    # novelty
    p_nov = subparsers.add_parser("novelty", help="BGC 新奇度评分")
    p_nov.add_argument("--bgc-csv", required=True, help="BGC 摘要 CSV")
    p_nov.add_argument("--output-csv", default="novelty_scores.csv", help="输出 CSV")

    args = parser.parse_args()

    if args.mode is None:
        parser.print_help()
        sys.exit(1)

    # 执行对应的功能函数
    mode_dispatcher = {
        "parse": lambda: parse_antismash_output(args.gbk_dir, args.output_csv),
        "extract": lambda: extract_bgc_sequences(args.gbk_dir, args.output_fasta, args.min_len),
        "build_library": lambda: build_virtual_library(args.bgc_csv, args.output_sdf, args.max),
        "descriptors": lambda: compute_descriptors(args.sdf_file, args.output_csv),
        "novelty": lambda: calculate_novelty_score(
            parse_antismash_output(args.bgc_csv.replace("_summary", "_raw").replace(".csv", "")),
            # 使用已存在的 bgc_csv
        ),
    }

    if args.mode == "novelty":
        df_bgc = pd.read_csv(args.bgc_csv) if os.path.exists(args.bgc_csv) else None
        if df_bgc is None:
            logger.error(f"文件不存在: {args.bgc_csv}")
            sys.exit(1)
        calculate_novelty_score(df_bgc, args.output_csv)
    else:
        mode_dispatcher[args.mode]()


if __name__ == "__main__":
    main()
