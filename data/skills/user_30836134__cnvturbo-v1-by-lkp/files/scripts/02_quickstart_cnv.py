#!/usr/bin/env python3

# Author: LKP <kunpeng.liao@abiosciences.com>
# Date:   2026-08-18

"""
02_quickstart_cnv.py
cnvturbo 推荐 R-exact 主管线 Quick Start。

完整流程：
  1. 加载数据
  2. infercnv_r_compat（8 步 R 等价预处理）
  3. compute_hspike_emission_params（hspike HMM 发射参数校准）
  4. hmm_call_subclusters（亚聚类细胞级 Tumor/Normal 判定）
  5. 可视化

参考：cnvturbo SKILL.md - 完整工作流（推荐 R-exact 管线）章节
"""
import scanpy as sc
import cnvturbo
from cnvturbo import tl as cnv_tl, pl as cnv_pl


def run_cnvturbo_quickstart(
    h5ad_path: str,
    output_path: str = "output_cnv.h5ad",
    reference_key: str = "cell_type",
    reference_cat: list = None,
    n_jobs: int = 16,
):
    """
    运行 cnvturbo R-exact 主管线（适用于 <50k 细胞的全量一次运行）。

    参数
    ----
    h5ad_path : str
        输入 h5ad 文件路径（adata.X 为原始整数计数）
    output_path : str
        输出 h5ad 文件路径
    reference_key : str
        obs 列名，标识细胞类型
    reference_cat : list of str
        参考细胞类型列表（用于参考减法）
    n_jobs : int
        joblib 并行数
    """
    if reference_cat is None:
        reference_cat = ["NK", "Endothelial", "Fibroblast"]

    # 1. 加载数据并保存原始计数
    adata = sc.read_h5ad(h5ad_path)
    adata.layers["counts"] = adata.X.copy()

    # 2. R-exact 8 步预处理（复现 R inferCNV 管线）
    cnv_tl.infercnv_r_compat(
        adata,
        raw_layer="counts",
        reference_key=reference_key,
        reference_cat=reference_cat,
        window_size=101,
        min_mean_expr_cutoff=0.1,   # R inferCNV 10x 默认值；Smart-seq2 用 1.0
        apply_2x_transform=True,
        n_jobs=n_jobs,
    )

    # 3. hspike 发射参数校准（镜像 R hidden_spike 模拟）
    emit_means, emit_stds, emit_sd_intercepts, emit_sd_slopes = (
        cnv_tl.compute_hspike_emission_params(
            adata,
            raw_layer="counts",
            reference_key=reference_key,
            reference_cat=reference_cat,
            min_mean_expr_cutoff=0.1,    # 必须与 infercnv_r_compat 保持一致
            output_space="copy_ratio",
            return_sd_trend=True,
        )
    )

    # 4. HMM 亚聚类细胞级 Tumor 判定
    cnv_tl.hmm_call_subclusters(
        adata,
        use_rep="cnv",
        reference_key=reference_key,
        reference_cat=reference_cat,
        precomputed_emit_means=emit_means,
        precomputed_emit_stds=emit_stds,
        precomputed_emit_sd_intercepts=emit_sd_intercepts,
        precomputed_emit_sd_slopes=emit_sd_slopes,
        leiden_resolution="auto",
        cluster_by_groups=True,
        min_segment_length=5,
        min_segments_for_tumor=1,
        key_added="cnv_call",
        n_jobs=n_jobs,
    )

    # 5. 严格 R 等价细胞级判定（可选）
    import numpy as np
    ref_mask = adata.obs[reference_key].isin(reference_cat).to_numpy()
    x_denoise = cnv_tl.denoise_r_compat(adata.obsm["X_cnv"], ref_mask)
    adata.obs["cnv_score"] = np.mean(np.abs(x_denoise - 1.0), axis=1)
    adata.obs["proportion_cnv"] = adata.obs["cnv_call_score"].astype(float)
    adata.obs["is_obs_tumor"] = (
        (~ref_mask)
        & (adata.obs["cnv_score"] > np.percentile(
            adata.obs.loc[ref_mask, "cnv_score"], 95))
        & (adata.obs["proportion_cnv"] > np.percentile(
            adata.obs.loc[ref_mask, "proportion_cnv"], 95))
    )

    # 6. 可视化（PCA + UMAP + 染色体热图）
    cnv_tl.pca(adata, use_rep="cnv")
    cnv_tl.umap(adata)
    cnv_tl.leiden(adata, resolution=0.5, key_added="cnv_leiden")
    cnv_tl.cnv_score(adata, use_rep="cnv", key_added="cnv_score")

    # 染色体热图
    cnv_pl.chromosome_heatmap(adata, groupby="cnv_call")

    # Scanpy 绘图（CNV UMAP）
    sc.pl.embedding(
        adata, basis="cnv_umap",
        color=["cnv_call", "cnv_call_score"],
        save="_cnv_umap.png",
    )

    # 7. 保存
    adata.write_h5ad(output_path)
    print(f"[OK] CNV 分析完成，结果保存至: {output_path}")
    print(f"     Tumor/Normal 分布:")
    print(adata.obs["cnv_call"].value_counts())


if __name__ == "__main__":
    run_cnvturbo_quickstart(
        h5ad_path="my_sample.h5ad",
        output_path="output_cnv.h5ad",
    )
