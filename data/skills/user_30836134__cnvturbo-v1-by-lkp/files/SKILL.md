---
name: cnvturbo
description: >
  使用 cnvturbo 进行单细胞 RNA-seq 拷贝数变异（CNV）推断。
  cnvturbo 是 R inferCNV 的 Python 重实现，算法完全对齐 HMM i6 管线，
  速度比 R inferCNV 快约 100 倍，与 Scanpy/AnnData 生态无缝集成。
  支持细胞级 Tumor/Normal HMM 判定、hspike 发射参数校准、
  染色体级 Viterbi 解码、去噪及亚聚类 Tumor 鉴定。
author: LKP <kunpeng.liao@abiosciences.com>
platform: github
source: https://github.com/LogicByteCraft/cnvturbo
tags: [scRNA-seq, CNV, inferCNV, HMM, copy-number, tumor, Scanpy, AnnData, Python]
version: 1.0.0
generated: 2026-08-02T00:00:00+08:00
---

# cnvturbo — 高性能单细胞 CNV 推断工具

## 概述

**cnvturbo** 是 [R inferCNV](https://github.com/broadinstitute/inferCNV) 的纯 Python 重实现，用于单细胞 RNA-seq 拷贝数变异（CNV）分析。核心特性：

- **算法完全对齐 R inferCNV 的 HMM i6 管线**，在 40 个 PDAC 样本（99,679 个细胞）上验证：区域级 CNV 调用与 R **100% 一致**，细胞级 Tumor/Normal 调用 **F1 = 0.980**。
- **速度提升约 100 倍**：7,269 个细胞从 R 的约 5 小时降至约 86 秒（CPU + joblib 并行）。
- **与 Scanpy/AnnData 生态无缝集成**，API 与 infercnvpy 兼容。

---

## 适用场景

当用户需要执行以下任务时使用此 Skill：

- 从单细胞 RNA-seq 数据推断拷贝数变异（CNV）
- 区分肿瘤细胞（Tumor）与正常细胞（Normal）
- 使用 HMM i6 管线进行细胞级 CNV 判定
- 基于 CNV 信号进行肿瘤亚克隆分析
- 需要与 R inferCNV 结果对齐的 Python 替代方案

---

## 安装

### 从 PyPI 安装（推荐）

```bash
pip install cnvturbo
```

### 使用清华源加速安装

```bash
pip install cnvturbo -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 带加速后端安装（仅对 legacy `tl.infercnv` + `tl.hmm_call_cells` 路径生效）

```bash
# Numba CPU 加速
pip install "cnvturbo[hmm-cpu]"

# PyTorch CUDA GPU 加速
pip install "cnvturbo[hmm-gpu]"

# 全部功能（含 Baum-Welch EM 拟合）
pip install "cnvturbo[hmm]"
```

> **注意**：推荐的 R-exact 主管线（`infercnv_r_compat` + `compute_hspike_emission_params` + `hmm_call_subclusters`）完全运行在 **CPU + joblib** 上，无需安装任何加速后端。

### 系统要求

- Python >= 3.10
- scanpy >= 1.10, anndata >= 0.7.3, numpy >= 1.20, pandas >= 1
- 可选：numba >= 0.57, torch >= 2.0, hmmlearn >= 0.3

---

## 数据准备

cnvturbo 要求 AnnData 对象包含：

1. **原始整数计数矩阵**：`adata.X` 或 `adata.layers["counts"]`
2. **基因坐标信息**：`adata.var` 中包含 `chromosome`、`start`、`end` 列
3. **参考细胞注释**：`adata.obs` 中有一列标识正常细胞（如 NK / 内皮 / 成纤维细胞）

### 从 GTF 添加基因坐标

```python
from cnvturbo.io import genomic_position_from_gtf

genomic_position_from_gtf(
    gtf_file="Homo_sapiens.GRCh38.110.gtf.gz",
    adata=adata,
)
```

---

## 完整工作流（推荐 R-exact 管线）

### Quick Start 示例

```python
import scanpy as sc
import cnvturbo
from cnvturbo import tl as cnv_tl, pl as cnv_pl

# 1. 加载数据
adata = sc.read_h5ad("my_sample.h5ad")
adata.layers["counts"] = adata.X.copy()

# 2. R-exact 预处理（8 步管线，复现 R inferCNV）
cnv_tl.infercnv_r_compat(
    adata,
    raw_layer="counts",
    reference_key="cell_type",
    reference_cat=["NK", "Endothelial", "Fibroblast"],
    window_size=101,
    min_mean_expr_cutoff=0.1,    # R inferCNV 10x 默认值；Smart-seq2 用 1.0
    apply_2x_transform=True,
    n_jobs=16,
)

# 3. hspike 发射参数校准（镜像 R hidden_spike 模拟）
emit_means, emit_stds, emit_sd_intercepts, emit_sd_slopes = cnv_tl.compute_hspike_emission_params(
    adata,
    raw_layer="counts",
    reference_key="cell_type",
    reference_cat=["NK", "Endothelial", "Fibroblast"],
    min_mean_expr_cutoff=0.1,    # 必须与 infercnv_r_compat 保持一致
    output_space="copy_ratio",
    return_sd_trend=True,
)

# 4. HMM 亚聚类细胞级 Tumor 判定
cnv_tl.hmm_call_subclusters(
    adata,
    use_rep="cnv",
    reference_key="cell_type",
    reference_cat=["NK", "Endothelial", "Fibroblast"],
    precomputed_emit_means=emit_means,
    precomputed_emit_stds=emit_stds,
    precomputed_emit_sd_intercepts=emit_sd_intercepts,
    precomputed_emit_sd_slopes=emit_sd_slopes,
    leiden_resolution="auto",
    cluster_by_groups=True,
    min_segment_length=5,
    min_segments_for_tumor=1,
    key_added="cnv_call",
    n_jobs=16,
)

print(adata.obs["cnv_call"].value_counts())
```

运行后：
- `adata.obs["cnv_call"]` 包含每个细胞的 `"Tumor"` / `"Normal"` 标签
- `adata.obs["cnv_call_score"]` 存储 HMM 非中性状态比例（`proportion_cnv`）

---

## 分步详细说明

### 步骤 1：R 兼容预处理（`infercnv_r_compat`）

精确复现 R inferCNV 的 8 步管线：

0. **低表达基因过滤** — `mean(raw_count) < min_mean_expr_cutoff`
1. 文库大小归一化 → 中位深度
2. `log2(x + 1)`
3. 第一次参考减法（基因空间，"bounds" 模式）
4. 裁剪至 ±3（默认）
5. 染色体级等长金字塔平滑（window=101）
6. 细胞级中位中心化
7. 第二次参考减法（基因空间）
8. `2^x` → 拷贝比（中性 ≈ 1.0）

```python
cnv_tl.infercnv_r_compat(
    adata,
    raw_layer="counts",
    reference_key="cell_type",
    reference_cat=["NK", "Endothelial"],
    max_ref_threshold=3.0,
    window_size=101,
    exclude_chromosomes=("chrX", "chrY"),
    min_mean_expr_cutoff=0.1,
    apply_2x_transform=True,
    n_jobs=16,
    key_added="cnv",
)
```

**输出**：
- `adata.obsm["X_cnv"]` — `(n_cells × n_genes_filtered)` 拷贝比矩阵
- `adata.uns["cnv"]["chr_pos"]` — 基因级染色体偏移
- `adata.uns["cnv"]["kept_var_names"]` — 通过过滤的基因名
- `adata.uns["cnv"]["min_mean_expr_cutoff"]` — 实际应用的截断值

### 步骤 2：hspike 发射参数校准（`compute_hspike_emission_params`）

镜像 R 的 `hidden_spike` 模拟：构建合成基因组（50% CNV / 50% 中性染色体），从真实参考细胞采样模拟基底，运行完整管线，提取每个 CNV 状态的发射参数。

```python
emit_means, emit_stds, emit_sd_intercepts, emit_sd_slopes = cnv_tl.compute_hspike_emission_params(
    adata,
    raw_layer="counts",
    reference_key="cell_type",
    reference_cat=["NK", "Endothelial"],
    min_mean_expr_cutoff=0.1,
    n_sim_cells=100,
    n_genes_per_chr=400,
    output_space="copy_ratio",
    return_sd_trend=True,
)
```

### 步骤 3：HMM 细胞级 Tumor 判定（`hmm_call_subclusters`）

R 等价解码器：组内 Leiden 亚聚类 → 染色体级 Viterbi → 片段长度去噪 → "亚聚类含 ≥1 CNV 片段 ⇒ Tumor" 规则。

```python
cnv_tl.hmm_call_subclusters(
    adata,
    use_rep="cnv",
    reference_key="cell_type",
    reference_cat=["NK", "Endothelial"],
    precomputed_emit_means=emit_means,
    precomputed_emit_stds=emit_stds,
    precomputed_emit_sd_intercepts=emit_sd_intercepts,
    precomputed_emit_sd_slopes=emit_sd_slopes,
    leiden_resolution="auto",
    cluster_by_groups=True,
    z_score_filter=0.8,
    leiden_function="CPM",
    leiden_graph_method="seurat_snn",
    n_neighbors=20,
    n_pcs=10,
    min_segment_length=5,
    min_segments_for_tumor=1,
    use_r_viterbi=True,
    key_added="cnv_call",
    backend="auto",
    n_jobs=16,
)
```

**输出**（添加到 `adata.obs`）：
- `cnv_call` — 每个细胞 `"Tumor"` / `"Normal"`
- `cnv_call_score` — HMM 非中性状态比例
- `cnv_call_expr_deviation` — 原始表达偏差
- `cnv_call_subcluster` — Leiden 亚聚类 ID

### 步骤 4：严格 R 等价细胞级判定

结合 HMM burden 与连续去噪 CNV 信号，实现与 R 严格一致的判定：

```python
import numpy as np

ref_mask = adata.obs["cell_type"].isin(["NK", "Endothelial", "Fibroblast"]).to_numpy()
x_denoise = cnv_tl.denoise_r_compat(adata.obsm["X_cnv"], ref_mask)
adata.obs["cnv_score"] = np.mean(np.abs(x_denoise - 1.0), axis=1)
adata.obs["proportion_cnv"] = adata.obs["cnv_call_score"].astype(float)
adata.obs["is_obs_tumor"] = (
    (~ref_mask)
    & (adata.obs["cnv_score"] > np.percentile(adata.obs.loc[ref_mask, "cnv_score"], 95))
    & (adata.obs["proportion_cnv"] > np.percentile(adata.obs.loc[ref_mask, "proportion_cnv"], 95))
)
```

---

## 大规模数据分块处理策略（>50k 细胞 / 低内存环境）

### 内存挑战

cnvturbo 的 R-exact 管线（`infercnv_r_compat`）在处理大规模数据时内存消耗剧增。以 170k 细胞为例：
- `X_cnv` 矩阵本身: 170000 x 3000 x float32 约 2GB
- `infercnv_r_compat` 中间变量峰值可达 **32GB+**
- `compute_hspike_emission_params` 全量运行需要额外 **~32GB**
- 全量峰值合计可达 **~64GB**

针对 **32GB WSL2 / 16GB 桌面** 环境设计以下分块策略。

### 分块策略总览

| 策略 | 说明 | 内存削减效果 |
|------|------|-------------|
| **参考细胞抽样** | 每类参考细胞最多取 2000 个 | 减少 ~75% 参考细胞内存 |
| **分批 infercnv** | 每批 BATCH_SIZE 个细胞逐批运行 | 峰值内存线性可控 |
| **基因列对齐** | 用预运行固定 `kept_var_names` | 保证批次间基因集一致 |
| **批次间休眠** | `sleep(3)` + `gc.collect()` | WSL2 内存回收延迟 |
| **hspike 子集校准** | 用抽样参考细胞子集运行 hspike | 避免 hspike 内存爆炸 |
| **逐批合并+释放** | 每批合并后立即置 `None` | 避免同时持有所有批次 |

### 分块参数推荐

```python
# ========== 分块参数 ==========
BATCH_SIZE = 15000       # 每批细胞数（见下方规模推荐表）
BATCH_SLEEP = 3          # 批次间休眠秒数（让 WSL 恢复）
N_JOBS = 2               # 低并行度避免 WSL 崩溃
WINDOW_SIZE = 101        # CNV 平滑窗口
MIN_MEAN_EXPR_CUTOFF = 0.1
REF_SAMPLE_PER_TYPE = 2000  # 每类参考细胞最大抽样数
```

### 不同数据规模的参数推荐

| 细胞数量 | BATCH_SIZE | N_JOBS | REF_SAMPLE | 预估时间 | 峰值内存 |
|----------|------------|--------|------------|----------|----------|
| <50k | 全量一次 | 4 | 全量 | ~10 min | ~16GB |
| 50k-100k | 30,000 | 3 | 3000/类 | ~30 min | ~24GB |
| 100k-200k | 15,000 | 2 | 2000/类 | ~60 min | ~20GB |
| 200k-500k | 10,000 | 2 | 1500/类 | ~3 hours | ~18GB |
| >500k | 5,000 | 1 | 1000/类 | ~8 hours | ~12GB |

### 完整分块流程代码

```python
import gc
import time
import numpy as np
import scanpy as sc
import anndata as ad
from cnvturbo import tl as cnv_tl

# -- Step 1: 加载数据 + 添加基因组位置 --
adata = ad.read_h5ad("my_sample.h5ad")

# 过滤控制基因（如有）
if "is_control" in adata.var.columns:
    adata = adata[:, ~adata.var["is_control"].astype(bool)].copy()

# 添加基因组位置（从参考文件或 GTF）
ref = ad.read_h5ad("gene_position_ref.h5ad")
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

# -- Step 2: 参考细胞抽样 + 预运行（获取固定基因集）--
REFERENCE_KEY = "cell_type"
REFERENCE_CATEGORIES = ["NK", "Endothelial", "Fibroblast", "T_cell"]
available_refs = [c for c in REFERENCE_CATEGORIES
                  if c in set(adata.obs[REFERENCE_KEY].astype(str))]

# 每类参考细胞最多抽样 2000 个（控制内存）
np.random.seed(42)
ref_indices_sample = []
for cat in available_refs:
    cat_idx = np.where(adata.obs[REFERENCE_KEY].astype(str) == cat)[0]
    n_sample = min(2000, len(cat_idx))
    ref_indices_sample.extend(
        np.random.choice(cat_idx, n_sample, replace=False)
    )
ref_indices_sample = np.array(sorted(ref_indices_sample))

# 预运行：用参考子集获取基因过滤信息 + 固定基因集
adata_ref = adata[ref_indices_sample].copy()
cnv_tl.infercnv_r_compat(
    adata_ref,
    raw_layer="counts",
    reference_key=REFERENCE_KEY,
    reference_cat=available_refs,
    window_size=101,
    min_mean_expr_cutoff=0.1,
    exclude_chromosomes=("chrX", "chrY"),
    apply_2x_transform=True,
    n_jobs=2,
    key_added="cnv",
)
kept_var_names = adata_ref.uns["cnv"]["kept_var_names"]
chr_pos = adata_ref.uns["cnv"]["chr_pos"]

# 保存参考细胞 X_cnv
ref_cnv = adata_ref.obsm["X_cnv"]
if hasattr(ref_cnv, 'toarray'):
    ref_cnv = ref_cnv.toarray()
ref_cnv = ref_cnv.copy()
del adata_ref; gc.collect()

# -- Step 3: 分批 infercnv_r_compat --
BATCH_SIZE = 15000
BATCH_SLEEP = 3
N_JOBS = 2

non_sample_mask = np.ones(adata.n_obs, dtype=bool)
non_sample_mask[ref_indices_sample] = False
non_sample_indices = np.where(non_sample_mask)[0]
n_batches = (len(non_sample_indices) + BATCH_SIZE - 1) // BATCH_SIZE

all_cnv_matrices = []
for batch_idx in range(n_batches):
    start = batch_idx * BATCH_SIZE
    end = min(start + BATCH_SIZE, len(non_sample_indices))
    batch_indices = non_sample_indices[start:end]
    print(f"  Batch {batch_idx+1}/{n_batches}: {len(batch_indices)} cells")

    adata_batch = adata[batch_indices].copy()
    cnv_tl.infercnv_r_compat(
        adata_batch,
        raw_layer="counts",
        reference_key=REFERENCE_KEY,
        reference_cat=available_refs,
        window_size=101,
        min_mean_expr_cutoff=0.1,
        exclude_chromosomes=("chrX", "chrY"),
        apply_2x_transform=True,
        n_jobs=N_JOBS,
        key_added="cnv",
    )

    # 基因列对齐（关键！不同批次过滤的基因可能不同）
    batch_cnv = adata_batch.obsm["X_cnv"]
    if hasattr(batch_cnv, 'toarray'):
        batch_cnv = batch_cnv.toarray()
    batch_var_names = list(adata_batch.uns["cnv"]["kept_var_names"])

    if batch_var_names != list(kept_var_names):
        batch_var_index = {g: i for i, g in enumerate(batch_var_names)}
        col_indices = [batch_var_index[g] for g in kept_var_names
                       if g in batch_var_index]
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
    time.sleep(BATCH_SLEEP)

# -- Step 4: 合并 X_cnv 矩阵（逐批释放）--
full_cnv = np.zeros(
    (adata.n_obs, len(kept_var_names)), dtype=np.float32
)
full_cnv[ref_indices_sample] = ref_cnv
del ref_cnv; gc.collect()

batch_offset = 0
for i, batch_cnv in enumerate(all_cnv_matrices):
    n = batch_cnv.shape[0]
    full_cnv[non_sample_indices[batch_offset:batch_offset+n]] = batch_cnv
    batch_offset += n
    all_cnv_matrices[i] = None  # 立即释放
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
        reference_key=REFERENCE_KEY,
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
    reference_key=REFERENCE_KEY,
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
    n_jobs=N_JOBS,
)

# -- Step 7: CNV score + 降维 --
cnv_tl.pca(adata, use_rep="cnv")
sc.pp.neighbors(adata, use_rep="X_cnv_pca", key_added="cnv_neighbors")
cnv_tl.leiden(adata, resolution=0.5, key_added="cnv_leiden")
cnv_tl.cnv_score(adata, use_rep="cnv", key_added="cnv_score")
cnv_tl.umap(adata)

adata.write_h5ad("output_cnv.h5ad")
print(adata.obs["cnv_call"].value_counts())
```

### 内存优化要点详解

| 技巧 | 效果 | 说明 |
|------|------|------|
| 参考细胞抽样 (78982->20000) | 减少 ~75% 参考细胞内存 | 每类最多 2000 个 |
| 分批大小 15k | 峰值内存 < 20GB | 32GB WSL2 安全 |
| 基因列对齐 | 保证批次间一致性 | 用预运行固定基因集 |
| 逐批合并+立即释放 | 避免同时持有所有批次 | `all_cnv_matrices[i] = None` |
| 批次间 `sleep(3)` | WSL2 内存回收延迟 | 防止 OOM 崩溃 |
| hspike 用子集 | 全量 hspike 需 ~32GB | 20000 细胞足够校准 |
| `N_JOBS=2` | 低并行度 | 避免 WSL 服务崩溃 |
| 及时 `del` + `gc.collect()` | 强制回收大对象 | 每步结束后调用 |

### 基因列对齐原理

分块处理的**核心技术难点**：不同批次运行 `infercnv_r_compat` 时，由于细胞表达谱差异，`min_mean_expr_cutoff` 过滤的基因集可能不完全一致。

**解决方案**：
1. **预运行**：先用参考子集运行一次，获得固定的 `kept_var_names`
2. **对齐**：每批运行后，将 X_cnv 列重排到与 `kept_var_names` 一致
3. **缺失填充**：批次中缺失的基因用 `0` 填充（表示无 CNV 信号）

```python
# 对齐核心逻辑
batch_var_index = {g: i for i, g in enumerate(batch_var_names)}
col_indices = [batch_var_index[g] for g in kept_var_names
               if g in batch_var_index]
# 缺失基因 -> 0 填充
if len(col_indices) != len(kept_var_names):
    aligned = np.zeros(
        (batch_cnv.shape[0], len(kept_var_names)), dtype=np.float32
    )
    # ... 填充 present 基因 ...
```

---

## 可视化

```python
# PCA + UMAP 降维
cnv_tl.pca(adata, use_rep="cnv")
cnv_tl.umap(adata)

# 染色体热图
cnv_pl.chromosome_heatmap(adata, groupby="cnv_call")

# 使用 Scanpy 绘图
import scanpy as sc
sc.pl.embedding(adata, basis="cnv_umap", color=["cnv_call", "cnv_call_score"])
```

---

## API 概览

```text
cnvturbo
├── tl                              # 工具函数
│   ├── infercnv                    # 原始滑窗打分（legacy）
│   ├── infercnv_r_compat           # R-exact 8 步管线（推荐）
│   ├── compute_hspike_emission_params  # hspike HMM 发射参数校准
│   ├── hmm_call_subclusters        # 亚聚类级 R 等价 HMM 调用
│   ├── hmm_call_cells              # 细胞级 HMM 调用（无亚聚类）
│   ├── cnv_score, cnv_score_cell   # CNV burden 评分
│   ├── ithcna, ithgex              # 瘤内异质性指标
│   ├── pca, umap, tsne, leiden     # CNV 空间嵌入（Scanpy 封装）
│   └── copykat                     # CopyKAT 集成（可选，需 R）
├── pp                              # 预处理工具
├── pl                              # 绘图
│   └── chromosome_heatmap          # 染色体热图
├── io                              # GTF / 基因位置辅助工具
│   └── genomic_position_from_gtf   # 从 GFT 添加基因坐标
└── datasets                        # 内置教程数据
```

---

## 后端覆盖

| 函数 | Numba CPU | PyTorch CUDA | 说明 |
|---|---|---|---|
| `tl.infercnv`（legacy 滑窗打分） | ✓ | ✓ | `backend="auto"` 自动选 GPU |
| `tl.hmm_call_cells`（细胞级 HMM，无亚聚类） | ✓ | ✓ | 同上 |
| `tl.infercnv_r_compat`（**R-exact 8 步管线**） | — | — | CPU + `joblib`（`n_jobs`） |
| `tl.compute_hspike_emission_params` | — | — | 同上 |
| `tl.hmm_call_subclusters`（**R-exact 亚聚类 HMM**） | — | — | `use_r_viterbi=True` 硬连线 CPU |

> **实际建议**：使用推荐的 `infercnv_r_compat` + `hmm_call_subclusters` 工作流时，无需安装加速器，通过调整 `n_jobs` / `OMP_NUM_THREADS` 优化 CPU 吞吐量。

---

## 关键参数说明

| 参数 | 默认值 | 说明 |
|---|---|---|
| `min_mean_expr_cutoff` | `0.1` | 低表达基因过滤阈值；10x 数据用 0.1，Smart-seq2 用 1.0 |
| `window_size` | `101` | 金字塔平滑窗口大小 |
| `max_ref_threshold` | `3.0` | 参考减法后裁剪范围 |
| `exclude_chromosomes` | `("chrX", "chrY")` | 排除的染色体 |
| `apply_2x_transform` | `True` | 是否进行 `2^x` 拷贝比转换 |
| `leiden_resolution` | `"auto"` | Leiden 亚聚类分辨率 |
| `min_segment_length` | `5` | HMM 片段最小长度（去噪） |
| `min_segments_for_tumor` | `1` | 判定 Tumor 所需的最小 CNV 片段数 |

---

## 性能基准

PDAC 基准（40 样本，99,679 个观测细胞，参考组 = NK / T-like 正常细胞）：

| 指标 | 结果 |
|---|---:|
| 区域级 CNV 调用准确率 vs R | **1.000** |
| 区域级 CNV 调用 F1 vs R | **1.000** |
| 细胞级 Tumor/Normal 准确率 vs R | **0.986** |
| 细胞级 Tumor/Normal F1 vs R | **0.980** |
| 细胞级 `cnv_score` 平均 Pearson vs R | **0.99997** |
| 运行时间（7,269 细胞） | **~86 秒**（R 约 5 小时） |

---

## 故障排除

### 常见问题

1. **`X_cnv not in adata.obsm`**
   - 确保先运行 `tl.infercnv_r_compat` 再运行降维或 HMM

2. **参考细胞为空**
   - 检查 `reference_key` 和 `reference_cat` 是否匹配 `adata.obs` 中的实际值

3. **结果与 R 不一致**
   - 确保 `min_mean_expr_cutoff`、`window_size`、`exclude_chromosomes` 与 R 参数一致
   - Smart-seq2 数据使用 `min_mean_expr_cutoff=1.0`

4. **内存不足（Out of Memory）**
   - **首选方案**：使用本文档「大规模数据分块处理策略」中的分批流程
   - 减少 `n_jobs`（如 `n_jobs=2`）
   - 参考细胞抽样：每类最多 2000 个
   - 分批处理：`BATCH_SIZE=15000`（32GB 内存推荐）
   - hspike 校准用参考子集而非全量细胞
   - 每步结束后 `del` 大对象 + `gc.collect()`
   - WSL2 环境添加批次间 `time.sleep(3)`
   - 极端情况可使用 legacy `tl.infercnv`（支持 GPU 加速）
   - 不同数据规模参数：<50k 全量 | 50-100k 批30k | 100-200k 批15k | >200k 批10k

---

## 引用

```bibtex
@software{cnvturbo,
  title  = {cnvturbo: A high-performance scRNA-seq CNV inference toolkit with R inferCNV-compatible HMM i6},
  url    = {https://github.com/LogicByteCraft/cnvturbo},
  year   = {2026}
}
```

---

## 许可证

BSD 3-Clause License

---

## 资源链接

- **源码仓库**：[github.com/LogicByteCraft/cnvturbo](https://github.com/LogicByteCraft/cnvturbo)
- **PyPI**：[pypi.org/project/cnvturbo](https://pypi.org/project/cnvturbo/)
- **R inferCNV（上游参考）**：[github.com/broadinstitute/inferCNV](https://github.com/broadinstitute/inferCNV)
- **infercnvpy（灵感来源）**：[github.com/icbi-lab/infercnvpy](https://github.com/icbi-lab/infercnvpy)
- **Scanpy 文档**：[scanpy.readthedocs.io](https://scanpy.readthedocs.io/)
