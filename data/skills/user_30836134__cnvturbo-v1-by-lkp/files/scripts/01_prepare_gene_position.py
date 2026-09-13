#!/usr/bin/env python3

# Author: LKP <kunpeng.liao@abiosciences.com>
# Date:   2026-08-18

"""
01_prepare_gene_position.py
从 GTF 文件为 AnnData 对象添加基因染色体坐标信息。

cnvturbo 要求 adata.var 中包含 chromosome、start、end 三列，
用于在染色体级别排序和滑动窗口平滑 CNV 信号。

参考：cnvturbo SKILL.md - 数据准备章节
"""
from cnvturbo.io import genomic_position_from_gtf
import scanpy as sc


def add_genomic_position(
    h5ad_path: str,
    gtf_file: str,
    output_path: str = None,
):
    """
    从 GTF 文件提取基因坐标并写入 AnnData.var。

    参数
    ----
    h5ad_path : str
        输入 h5ad 文件路径
    gtf_file : str
        参考 GTF 文件（如 Homo_sapiens.GRCh38.110.gtf.gz）
    output_path : str, optional
        输出 h5ad 文件路径；为 None 时覆盖原文件
    """
    # 加载 AnnData 对象
    adata = sc.read_h5ad(h5ad_path)

    # 从 GTF 添加染色体坐标（chromosome/start/end）
    genomic_position_from_gtf(
        gtf_file=gtf_file,
        adata=adata,
    )

    # 保存结果
    out = output_path if output_path is not None else h5ad_path
    adata.write_h5ad(out)
    print(f"[OK] 基因坐标已添加并保存至: {out}")
    print(f"     示例: {adata.var[['chromosome','start','end']].head()}")


if __name__ == "__main__":
    # 使用示例
    add_genomic_position(
        h5ad_path="my_sample.h5ad",
        gtf_file="Homo_sapiens.GRCh38.110.gtf.gz",
    )
