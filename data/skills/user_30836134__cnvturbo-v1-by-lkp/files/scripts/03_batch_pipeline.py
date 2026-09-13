#!/usr/bin/env python3

# Author: LKP <kunpeng.liao@abiosciences.com>
# Date:   2026-08-18

"""
03_batch_pipeline.py
cnvturbo 大规模数据（>50k 细胞）分块处理流程。

针对 32GB WSL2 / 16GB 桌面环境设计，通过：
  - 参考细胞抽样（每类最多 2000）
  - 分批 infercnv_r_compat
  - 基因列对齐
  - 逐批合并+立即释放
  - hspike 子集校准
降低内存峰值至 ~20GB。

参考：cnvturbo SKILL.md - 大规模数据分块处理策略章节
"""
import gc
import time
import numpy as np
import scanpy as sc
import anndata as ad
from cnvturbo import tl as cnv_tl


def run_cnvturbo_batched(
    h5ad_path: str,
    gene_position_ref_path: str,
    output_path: str = "output_cnv_batched.h5ad",
    reference_key: str = "cell_type",
    reference_categories: list = None,
    batch_size: int = 15000,
    n_jobs: int = 2,
    ref_sample_per_type: int = 2000,
):
    """
    运行 cnvturbo 分块处理流程（适用于 >50k 细胞）。

    参数
    ----
    h5ad_path : str
        输入 h5ad 路径
    gene_position_ref_path : str
        包含基因坐标（chromosome/start/end）的参考 h5ad 路径
    output_path : str
        输出 h5ad 路径
    reference_key : str
        obs 列名标识细胞类型
    reference_categories : list of str
        参考细胞类型列表
    batch_size : int
        每批处理的细胞数
    n_jobs : int
        joblib 并行数
    ref_sample_per_type : int
        每类参考细胞最大抽样数
    """
    if reference_categories is None:
        reference_categories = ["NK", "Endothelial", "Fibroblast", "T_cell"]

    # -- Step 1: 加载数据 + 添加基因组位置 --
    adata = ad.read_h5ad(h5ad_path)

    if "is_control" in adata.var.columns:
        adata = adata[:, ~adata.var["is_control"].astype(bool)].copy()

    # 从参考 h5ad 获取基因坐标
    ref = ad.read_h5ad(gene_position_ref_path)
    gene_pos = ref.var[["chromosome", "start", "end"]].copy()
    gene_pos = gene_pos[gene_pos["chromosome"].notna()]
    gene_pos = gene_pos[~gene_pos.index.duplicated(keep="first")]
    del ref; gc.collect()

    adata.var_names = adata.var_names.astype(str)
    adata = adata[:, adata.var_names.isin(gene_pos.index)].copy()
    gp = gene_pos.loc[adata.var_names]
    adata.var["chromosome"] = gp["chromosome"].values
    adata.var["start"] = gp["start"].values
    adata.var["end"] = gp["end"].values

    # 仅保留标准染色体
    standard_chroms = [f"chr{i}" for i in range(1, 23)] + ["chrX", "chrY"]
    adata = adata[:, adata.var["chromosome"].isin(standard_chroms)].copy()
    adata.layers["counts"] = adata.X.copy()
    gc.collect()

    # -- Step 2: 参考细胞抽样 + 预运行（获取固定基因集） --
    available_refs = [
        c for c in reference_categories
        if c in set(adata.obs[reference_key].astype(str))
    ]
    np.random.seed(42)
    ref_indices_sample = []
    for cat in available_refs:
        cat_idx = np.where(adata.obs[reference_key].astype(str) == cat)[0]
        n_sample = min(ref_sample_per_type, len(cat_idx))
        ref_indices_sample.extend(
            np.random.choice(cat_idx, n_sample, replace=False)
        )
    ref_indices_sample = np.array(sorted(ref_indices_sample))

    adata_ref = adata[ref_indices_sample].copy()
    cnv_tl.infercnv_r_compat(
        adata_ref,
        raw_layer="counts",
        reference_key=reference_key,
        reference_cat=available_refs,
        window_size=101,
        min_mean_expr_cutoff=0.1,
        exclude_chromosomes=("chrX", "chrY"),
        apply_2x_transform=True,
        n_jobs=n_jobs,
        key_added="cnv",
    )
    kept_var_names = adata_ref.uns["cnv"]["kept_var_names"]
    chr_pos = adata_ref.uns["cnv"]["chr_pos"]

    ref_cnv = adata_ref.obsm["X_cnv"]
    if hasattr(ref_cnv, 'toarray'):
        ref_cnv = ref_cnv.toarray()
    ref_cnv = ref_cnv.copy()
    del adata_ref; gc.collect()

    # -- Step 3: 分批 infercnv_r_compat --
    non_sample_mask = np.ones(adata.n_obs, dtype=bool)
    non_sample_mask[ref_indices_sample] = False
    non_sample_indices = np.where(non_sample_mask)[0]
    n_batches = (len(non_sample_indices) + batch_size - 1) // batch_size

    all_cnv_matrices = []
    for batch_idx in range(n_batches):
        start = batch_idx * batch_size
        end = min(start + batch_size, len(non_sample_indices))
        batch_indices = non_sample_indices[start:end]
        print(f"  Batch {batch_idx + 1}/{n_batches}: {len(batch_indices)} cells")

        adata_batch = adata[batch_indices].copy()
        cnv_tl.infercnv_r_compat(
            adata_batch,
            raw_layer="counts",
            reference_key=reference_key,
            reference_cat=available_refs,
            window_size=101,
            min_mean_expr_cutoff=0.1,
            exclude_chromosomes=("chrX", "chrY"),
            apply_2x_transform=True,
            n_jobs=n_jobs,
            key_added="cnv",
        )

        # 基因列对齐（关键！）
        batch_cnv = adata_batch.obsm["X_cnv"]
        if hasattr(batch_cnv, 'toarray'):
            batch_cnv = batch_cnv.toarray()
        batch_var_names = list(adata_batch.uns["cnv"]["kept_var_names"])

        if batch_var_names != list(kept_var_names):
            batch_var_index = {g: i for i, g in enumerate(batch_var_names)}
            col_indices = [
                batch_var_index[g] for g in kept_var_names
                if g in batch_var_index
            ]
            if len(col_indices) != len(kept_var_names):
                # 缺失基因用 0 填充
                aligned = np.zeros(
                    (batch_cnv.shape[0], len(kept_var_names)), dtype=np.float32
                )
                present_mask = np.array(
                    [g in batch_var_index for g in kept_var_names]
                )
                present_idx = np.where(present_mask)[0]
                aligned[:, present_idx] = batch_cnv[
                    :, [batch_var_index[kept_var_names[i]] for i in present_idx]
                ]
                batch_cnv = aligned
            else:
                batch_cnv = batch_cnv[:, col_indices]

        all_cnv_matrices.append(batch_cnv)
        del adata_batch; gc.collect()
        time.sleep(3)   # WSL2 内存回收延迟

    # -- Step 4: 合并 X_cnv 矩阵（逐批释放）--
    full_cnv = np.zeros(
        (adata.n_obs, len(kept_var_names)), dtype=np.float32
    )
    full_cnv[ref_indices_sample] = ref_cnv
    del ref_cnv; gc.collect()

    batch_offset = 0
    for i, batch_cnv in enumerate(all_cnv_matrices):
        n = batch_cnv.shape[0]
        full_cnv[non_sample_indices[batch_offset:batch_offset + n]] = batch_cnv
        batch_offset += n
        all_cnv_matrices[i] = None   # 立即释放
        gc.collect()
    del all_cnv_matrices; gc.collect()

    adata.obsm["X_cnv"] = full_cnv
    adata.uns["cnv"] = {
        "chr_pos": chr_pos,
        "kept_var_names": kept_var_names,
    }
    del full_cnv
    if "counts" in adata.layers:
        del adata.layers["counts"]
        gc.collect()

    # -- Step 5: hspike HMM 校准（用参考子集）--
    adata.layers["counts"] = adata.X.copy()
    adata_hspike = adata[ref_indices_sample].copy()
    emit_means, emit_stds, emit_intercepts, emit_slopes = (
        cnv_tl.compute_hspike_emission_params(
            adata_hspike,
            raw_layer="counts",
            reference_key=reference_key,
            reference_cat=available_refs,
            window_size=101,
            min_mean_expr_cutoff=0.1,
            exclude_chromosomes=("chrX", "chrY"),
            n_sim_cells=100,
            n_genes_per_chr=400,
            output_space="copy_ratio",
            return_sd_trend=True,
        )
    )
    del adata_hspike; gc.collect()

    # -- Step 6: HMM 亚聚类 Tumor/Normal 判定（全量）--
    cnv_tl.hmm_call_subclusters(
        adata,
        use_rep="cnv",
        reference_key=reference_key,
        reference_cat=available_refs,
        precomputed_emit_means=emit_means,
        precomputed_emit_stds=emit_stds,
        precomputed_emit_sd_intercepts=emit_intercepts,
        precomputed_emit_sd_slopes=emit_slopes,
        leiden_resolution="auto",
        cluster_by_groups=True,
        min_segment_length=5,
        min_segments_for_tumor=1,
        key_added="cnv_call",
        n_jobs=n_jobs,
    )

    # -- Step 7: CNV score + 降维 --
    cnv_tl.pca(adata, use_rep="cnv")
    sc.pp.neighbors(adata, use_rep="X_cnv_pca", key_added="cnv_neighbors")
    cnv_tl.leiden(adata, resolution=0.5, key_added="cnv_leiden")
    cnv_tl.cnv_score(adata, use_rep="cnv", key_added="cnv_score")
    cnv_tl.umap(adata)

    adata.write_h5ad(output_path)
    print(f"[OK] 分块 CNV 分析完成 -> {output_path}")
    print(adata.obs["cnv_call"].value_counts())


if __name__ == "__main__":
    run_cnvturbo_batched(
        h5ad_path="my_sample.h5ad",
        gene_position_ref_path="gene_position_ref.h5ad",
        output_path="output_cnv_batched.h5ad",
    )
