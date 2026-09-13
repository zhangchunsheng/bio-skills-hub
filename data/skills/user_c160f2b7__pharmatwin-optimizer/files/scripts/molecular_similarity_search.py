#!/usr/bin/env python3
"""
PharmaTwin-Optimizer: 分子指纹相似性搜索脚本
功能：计算 ECFP / MACCS 分子指纹的 Tanimoto 相似性，用于替代物筛选 (Phase 3)

依赖：rdkit, numpy, pandas
安装：pip install rdkit-pypi numpy pandas
"""

import sys
import argparse
import json
from typing import List, Tuple, Optional

import numpy as np
import pandas as pd

try:
    from rdkit import Chem
    from rdkit.Chem import AllChem, MACCSkeys, Descriptors
    from rdkit.DataStructs import TanimotoSimilarity, BulkTanimotoSimilarity
except ImportError:
    print("ERROR: rdkit not installed. Run: pip install rdkit-pypi", file=sys.stderr)
    sys.exit(1)


# ─── 内置 FDA 已批准辅料 / 常用载体参考库（子集） ──────────────────────
# 添加更多辅料可参考 FDA IID 数据库
FDA_EXCIPIENT_LIBRARY = {
    "PEG 400": {"smiles": "C(COCCO)O", "category": "溶剂/增溶剂"},
    "Poloxamer 188": {"smiles": "CCCCO", "category": "表面活性剂"},
    "TPGS": {"smiles": "CCCCCCCCCCCCCCCC(=O)OCCOCCOCCOCCOCCO", "category": "表面活性剂"},
    "Soluplus": {"smiles": "CC(C(=O)OC(C)CO)OC(=O)C=C", "category": "增溶剂"},
    "HPMC E5": {"smiles": "CO", "category": "骨架材料"},
    "Labrasol": {"smiles": "CCCCCCCCCCCC(=O)OCCO", "category": "脂质辅料"},
    "Transcutol P": {"smiles": "CCOCCO", "category": "潜溶剂"},
    "Capryol 90": {"smiles": "CCCCCCCC(=O)O", "category": "脂质辅料"},
    "油酸 (Oleic Acid)": {"smiles": "CCCCCCCCC=CCCCCCCC(=O)O", "category": "脂质辅料"},
    "磷脂酰胆碱 (SPC)": {"smiles": "CCCCCCCCCCCCCCCC(=O)OCC(COP(=O)([O-])OCC[N+](C)(C)C)OC(=O)CCCCCCCCCCCCCCC", "category": "磷脂"},
    "胆固醇 (Cholesterol)": {"smiles": "CC(C)CCCC(C)C1CCC2C1(CCC3C2CC=C4C3(CCC(C4)O)C)C", "category": "脂质"},
    "维生素 E": {"smiles": "CC1=CC(C)=C2OCC(C)(C)C2C(C)(C)CCCC(C)CCCC(C)CCCC(C)C", "category": "抗氧化剂"},
    "PEG 3350": {"smiles": "C(COCCO)O", "category": "溶剂/增溶剂"},
    "PVP K30": {"smiles": "CC(C(=O)N1CCCC1)C", "category": "增溶剂"},
    "Kollidon VA64": {"smiles": "CC(C(=O)N1CCCC1)C(C(C(=O)OCCO)O)", "category": "增溶剂"},
    "Lutrol F127": {"smiles": "CCCCO", "category": "表面活性剂"},
}


def mol2fp(smiles: str, fp_type: str = "ecfp4", n_bits: int = 2048) -> Optional:
    """将 SMILES 转为分子指纹向量

    Args:
        smiles: 分子的 SMILES 字符串
        fp_type: 指纹类型 — "ecfp4"(默认), "ecfp6", "maccs"
        n_bits: ECFP 指纹位数（MACCS 固定 167 位）

    Returns:
        RDKit ExplicitBitVect 或 None（若解析失败）
    """
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None

    if fp_type == "maccs":
        return MACCSkeys.GenMACCSKeys(mol)
    elif fp_type == "ecfp6":
        return AllChem.GetMorganFingerprintAsBitVect(mol, radius=3, nBits=n_bits)
    else:  # ecfp4
        return AllChem.GetMorganFingerprintAsBitVect(mol, radius=2, nBits=n_bits)


def search_similar(
    query_smiles: str,
    library: dict,
    fp_type: str = "ecfp4",
    min_similarity: float = 0.0,
    top_n: int = 10,
) -> List[dict]:
    """在辅料库中搜索与查询分子最相似的分子

    Args:
        query_smiles: 查询分子 SMILES
        library: 辅料库字典 {name: {"smiles": ..., "category": ...}}
        fp_type: 指纹类型
        min_similarity: 最小相似度阈值
        top_n: 返回 top N 结果

    Returns:
        [{"name": ..., "tanimoto": ..., "category": ...}, ...]
    """
    query_fp = mol2fp(query_smiles, fp_type)
    if query_fp is None:
        print(f"ERROR: 查询 SMILES 解析失败: {query_smiles}", file=sys.stderr)
        return []

    results = []
    for name, info in library.items():
        fp = mol2fp(info["smiles"], fp_type)
        if fp is None:
            continue
        sim = TanimotoSimilarity(query_fp, fp)
        if sim >= min_similarity:
            results.append({
                "name": name,
                "tanimoto": round(sim, 4),
                "category": info["category"],
                "smiles": info["smiles"],
            })

    results.sort(key=lambda x: x["tanimoto"], reverse=True)
    return results[:top_n]


def batch_search(
    library: dict,
    fp_type: str = "ecfp4",
) -> pd.DataFrame:
    """批量计算辅料库内所有分子对之间的 Tanimoto 相似度矩阵"""
    names = list(library.keys())
    fingerprints = []
    valid_names = []
    for name in names:
        sm = library[name]["smiles"]
        fp = mol2fp(sm, fp_type)
        if fp is not None:
            fingerprints.append(fp)
            valid_names.append(name)

    n = len(fingerprints)
    matrix = np.zeros((n, n))
    for i in range(n):
        similarities = BulkTanimotoSimilarity(fingerprints[i], fingerprints)
        matrix[i, :] = similarities

    df = pd.DataFrame(matrix, index=valid_names, columns=valid_names)
    return df


def main():
    parser = argparse.ArgumentParser(
        description="PharmaTwin-Optimizer: 分子指纹相似性搜索",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("smiles", help="查询分子的 SMILES 字符串")
    parser.add_argument(
        "--fp-type",
        choices=["ecfp4", "ecfp6", "maccs"],
        default="ecfp4",
        help="分子指纹类型 (默认: ecfp4)",
    )
    parser.add_argument(
        "--min-sim",
        type=float,
        default=0.3,
        help="最小 Tanimoto 相似度阈值 (默认: 0.3)",
    )
    parser.add_argument(
        "--top-n",
        type=int,
        default=10,
        help="返回排名前 N 的相似辅料 (默认: 10)",
    )
    parser.add_argument(
        "--output", "-o",
        help="输出 JSON 文件路径 (可选，默认输出到 stdout)",
    )
    parser.add_argument(
        "--batch",
        action="store_true",
        help="批量模式：输出辅料库内 Tanimoto 相似度矩阵",
    )

    args = parser.parse_args()

    if args.batch:
        df = batch_search(FDA_EXCIPIENT_LIBRARY, args.fp_type)
        if args.output:
            df.to_csv(args.output)
            print(f"相似度矩阵已写入: {args.output}")
        else:
            print(df.to_string(float_format="%.4f"))
        return

    results = search_similar(
        args.smiles,
        FDA_EXCIPIENT_LIBRARY,
        fp_type=args.fp_type,
        min_similarity=args.min_sim,
        top_n=args.top_n,
    )

    output = {
        "query_smiles": args.smiles,
        "fp_type": args.fp_type,
        "min_similarity": args.min_sim,
        "results": results,
        "total_hits": len(results),
    }

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        print(f"结果已写入: {args.output}")
    else:
        print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
