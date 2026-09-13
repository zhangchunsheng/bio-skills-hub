#!/usr/bin/env python3

# Author: LKP <kunpeng.liao@abiosciences.com>

"""
01_gpu_standard_pipeline.py
基于 rapids-singlecell (v0.15+) 的 GPU 加速单细胞 RNA-seq 标准分析流程。

适用环境：
  - Windows / Linux / macOS（Windows 推荐使用 WSL2；macOS 仅适用于 Intel + 外置 NVIDIA eGPU 场景）
  - Python 3.11+
  - 支持 CUDA 的 NVIDIA GPU（Turing → Blackwell）+ CUDA 12.x（12.2–12.9）或 13.x
  - 通过 conda / pip / Docker 安装 rapids-singlecell

性能参考（~10k 细胞，24GB GPU）：
  - PCA:       ~0.8秒  (CPU ~8秒)
  - Neighbors: ~0.3秒  (CPU ~15秒)
  - UMAP:      ~0.4秒  (CPU ~30秒)
  - Leiden:    ~2秒    (CPU ~15秒)
  - t-SNE:     ~0.5秒  (CPU ~60秒)
  - Markers:   ~2秒    (CPU ~20秒)

参考：gpu-singlecell-analysis SKILL.md

命令行使用：
    python 01_gpu_standard_pipeline.py --data /path/to/pbmc --output results.h5ad \\
        --use-harmony --sample-col sample
"""

import argparse
import os
import sys
import time
import warnings

warnings.filterwarnings("ignore")

import numpy as np
import scanpy as sc
import rapids_singlecell as rsc
import cupy as cp
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


def parse_args():
    p = argparse.ArgumentParser(
        description="GPU 加速单细胞标准分析流程 (rapids-singlecell v0.15+)"
    )
    p.add_argument(
        "--data", required=True,
        help="输入数据路径（10X mtx 目录 或 .h5ad 文件）",
    )
    p.add_argument(
        "--output", default="results.h5ad",
        help="输出 h5ad 文件路径（默认 results.h5ad）",
    )
    p.add_argument(
        "--plot-prefix", default="results",
        help="可视化图片前缀（默认 results，生成 <prefix>.png 与 <prefix>.pdf）",
    )
    p.add_argument("--n-top-genes", type=int, default=2000, help="高变基因数")
    p.add_argument("--n-comps", type=int, default=50, help="PCA 主成分数")
    p.add_argument("--n-pcs", type=int, default=30, help="用于降维/聚类的主成分数")
    p.add_argument("--n-neighbors", type=int, default=15, help="kNN 邻居数")
    p.add_argument("--leiden-resolution", type=float, default=1.0, help="Leiden 聚类分辨率")
    p.add_argument("--n-genes-max", type=int, default=2500, help="QC 中 n_genes_by_counts 上限")
    p.add_argument("--mt-pct-max", type=float, default=5.0, help="QC 中线粒体基因百分比上限")
    p.add_argument(
        "--hvg-flavor", default="seurat_v3", choices=["seurat_v3", "seurat"],
        help="HVG 选择 flavor；seurat_v3 需 counts 层",
    )
    p.add_argument(
        "--counts-layer", default="counts",
        help="counts 原始计数层名称（仅 seurat_v3 使用）",
    )
    p.add_argument(
        "--use-harmony", action="store_true",
        help="是否启用 Harmony 批次校正",
    )
    p.add_argument(
        "--sample-col", default="sample",
        help="obs 中批次/样本列名",
    )
    p.add_argument(
        "--scale-max-value", type=float, default=10.0,
        help="rsc.pp.scale 的 max_value（默认 10.0）",
    )
    p.add_argument(
        "--no-regress-out", action="store_true",
        help="跳过 rsc.pp.regress_out 步骤",
    )
    return p.parse_args()


def select_hvg(adata, args):
    """根据是否保留 counts 层选择 HVG 调用方式。"""
    if args.hvg_flavor == "seurat_v3" and args.counts_layer in adata.layers:
        print(f"  使用 rsc.pp.highly_variable_genes (seurat_v3, layer={args.counts_layer})")
        rsc.pp.highly_variable_genes(
            adata,
            n_top_genes=args.n_top_genes,
            flavor="seurat_v3",
            layer=args.counts_layer,
            batch_key=args.sample_col if (
                args.sample_col in adata.obs.columns
            ) else None,
        )
    else:
        print("  回退到 sc.pp.highly_variable_genes (seurat)")
        sc.pp.highly_variable_genes(
            adata,
            n_top_genes=args.n_top_genes,
            flavor="seurat",
            batch_key=args.sample_col if (
                args.sample_col in adata.obs.columns
            ) else None,
        )


def run_gpu_pipeline(args):
    """
    运行 GPU 加速单细胞标准分析流程。
    """
    # ===== 1. 验证 GPU =====
    print(f"CUDA available: {cp.cuda.is_available()}")
    if cp.cuda.is_available():
        props = cp.cuda.runtime.getDeviceProperties(0)
        print(f"GPU: {props['name'].decode()}")

    # ===== 2. 读取数据 =====
    print(f"\n[Step 1] 读取数据: {args.data}")
    if args.data.endswith(".h5ad"):
        adata = sc.read_h5ad(args.data)
    else:
        adata = sc.read_10x_mtx(args.data, var_names="gene_symbols", cache=True)
    print(f"  Loaded: {adata.n_obs} cells x {adata.n_vars} genes")

    # ===== 3. 质量控制 =====
    print("\n[Step 2] 质量控制")
    adata.var["mt"] = adata.var_names.str.startswith("MT-")
    sc.pp.calculate_qc_metrics(
        adata, qc_vars=["mt"], percent_top=None,
        log1p=False, inplace=True,
    )
    n_before = adata.n_obs
    adata = adata[adata.obs.n_genes_by_counts < args.n_genes_max, :].copy()
    adata = adata[adata.obs.pct_counts_mt < args.mt_pct_max, :].copy()
    print(f"  过滤后: {adata.n_obs} cells (移除 {n_before - adata.n_obs})")

    # ===== 4. 标准化 + 特征选择 + 缩放 =====
    print("\n[Step 3] 标准化与特征选择")
    sc.pp.normalize_total(adata, target_sum=1e4)
    sc.pp.log1p(adata)
    select_hvg(adata, args)
    adata_hvg = adata[:, adata.var["highly_variable"]].copy()
    print(f"  HVG: {adata_hvg.n_vars} genes")

    if not args.no_regress_out:
        print("  rsc.pp.regress_out (total_counts, pct_counts_MT)")
        rsc.pp.regress_out(adata_hvg, keys=["total_counts", "pct_counts_MT"])

    print(f"  rsc.pp.scale (max_value={args.scale_max_value})")
    rsc.pp.scale(adata_hvg, max_value=args.scale_max_value)

    # ===== 5. AnnData 迁移到 GPU =====
    print("\n[Step 4] AnnData 迁移到 GPU (rsc.get.anndata_to_GPU)")
    rsc.get.anndata_to_GPU(adata_hvg)

    # ===== 6. GPU 加速分析 =====
    print("\n[Step 5] GPU 加速分析")
    t0 = time.time()
    rsc.pp.pca(adata_hvg, n_comps=args.n_comps)
    print(f"  PCA: {time.time() - t0:.2f}秒")

    # ===== 7. Harmony 批次校正（可选）=====
    use_rep = "X_pca"
    if args.use_harmony:
        if args.sample_col not in adata_hvg.obs.columns:
            print(
                f"  [WARN] --use-harmony 已开启，但 obs 中找不到 '{args.sample_col}' 列；"
                "跳过 Harmony。"
            )
        else:
            print(f"\n[Step 6] Harmony 批次校正（按 {args.sample_col}）")
            import harmonypy as hm
            # 确保 PCA 矩阵是 numpy 数组（避免 GPU 内存问题）
            pca_data = np.array(adata_hvg.obsm["X_pca"])
            meta_data = adata_hvg.obs
            ho = hm.run_harmony(
                pca_data, meta_data,
                vars_use=[args.sample_col],
                max_iter_harmony=20,
            )
            # 注意：ho.Z_corr 形状为 (n_cells, n_pcs)，不要转置
            adata_hvg.obsm["X_pca_harmony"] = ho.Z_corr
            use_rep = "X_pca_harmony"

    # ===== 8. 邻居 + 降维 + 聚类 =====
    print("\n[Step 7] 邻居图、降维与聚类")
    rsc.pp.neighbors(
        adata_hvg,
        n_neighbors=args.n_neighbors,
        n_pcs=args.n_pcs,
        use_rep=use_rep,
    )
    rsc.tl.umap(adata_hvg, min_dist=0.5, spread=1.0)
    rsc.tl.leiden(adata_hvg, resolution=args.leiden_resolution)
    rsc.tl.tsne(adata_hvg, n_pcs=args.n_pcs, use_rep=use_rep)
    rsc.tl.rank_genes_groups(
        adata_hvg,
        groupby="leiden",
        method="wilcoxon",
        use_raw=False,   # 必须设置 use_raw=False
    )

    # ===== 9. 可视化 =====
    print("\n[Step 8] 可视化输出")
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    sc.pl.umap(adata_hvg, color="leiden", ax=axes[0, 0], show=False)
    sc.pl.tsne(adata_hvg, color="leiden", ax=axes[0, 1], show=False)
    sc.pl.umap(adata_hvg, color="total_counts", ax=axes[1, 0], show=False)
    sc.pl.umap(adata_hvg, color="pct_counts_mt", ax=axes[1, 1], show=False)
    plt.tight_layout()
    png_path = f"{args.plot_prefix}.png"
    pdf_path = f"{args.plot_prefix}.pdf"
    plt.savefig(png_path, dpi=150)
    plt.savefig(pdf_path)
    plt.close()
    print(f"  已保存: {png_path} / {pdf_path}")

    # ===== 10. 迁回 CPU 并保存结果 =====
    print("\n[Step 9] 保存结果 (迁回 CPU 后写盘)")
    rsc.get.anndata_to_CPU(adata_hvg)
    out_dir = os.path.dirname(os.path.abspath(args.output))
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    adata_hvg.write(args.output)
    print(f"\n[OK] GPU 单细胞分析完成 -> {args.output}")
    print(f"  细胞数: {adata_hvg.n_obs}, 基因数: {adata_hvg.n_vars}")
    print(f"  聚类分布:")
    print(adata_hvg.obs["leiden"].value_counts())


def main():
    args = parse_args()
    try:
        run_gpu_pipeline(args)
    except Exception as e:
        print(f"\n[ERROR] 分析失败: {e}", file=sys.stderr)
        raise


if __name__ == "__main__":
    main()