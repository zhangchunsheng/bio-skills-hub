---
name: gpu-singlecell-analysis
description: GPU加速的单细胞RNA-seq标准分析流程，使用rapids-singlecell（v0.15+）进行PCA、UMAP、t-SNE、Leiden/Louvain聚类、差异表达、批次校正（Harmony）、GPU回归、空间分析（Squidpy兼容）、扰动分析（pertpy兼容）与通路评分（decoupler兼容）。当用户需要GPU加速单细胞分析、处理大规模单细胞数据、或需要更快的分析速度时使用。需要配备NVIDIA GPU的机器（Windows / Linux / macOS）。
author: LKP <kunpeng.liao@abiosciences.com>
---

# GPU单细胞标准分析

基于 [rapids-singlecell](https://rapids-singlecell.readthedocs.io/) 的 GPU 加速单细胞 RNA-seq 分析流程，可显著提升大规模数据集的分析速度。

rapids-singlecell 提供 AnnData-first API，与 Scanpy 大体兼容，同时纳入 Squidpy、decoupler、pertpy 的部分功能；底层通过 CuPy 与 NVIDIA RAPIDS 实现 GPU 加速。

## 环境要求

- **操作系统**: Windows / Linux / macOS（Windows 推荐 WSL2；macOS 仅适用于 Intel + 外置 NVIDIA eGPU 场景）
- **Python**: 3.11+
- **GPU**: 支持 CUDA 的 NVIDIA GPU，覆盖 **Turing → Blackwell**
  - 算力清单：`75`（Turing，T4 / RTX 2080）/ `80`（Ampere，A100）/ `86`（Ampere，RTX 3090）/ `89`（Ada Lovelace，RTX 4090）/ `90`（Hopper，H100）/ `100`/`103`/`120`（Blackwell，B200 / B300 / RTX PRO 6000）
- **CUDA**: 12.x（12.2–12.9）或 13.x
- **依赖**: `rapids-singlecell`, `cupy`, `cuml`, `scanpy`；可选 `harmonypy`、`matplotlib`

## 安装（v0.15.0+）

v0.15 起官方提供**预编译 CUDA kernel 的 wheel**（通过 nanobind），安装时无需 nvcc；可任选 conda、PyPI、Docker 中的一种。

### 方式一：Conda（官方 yaml）

```bash
# CUDA 12（Python 3.14, CUDA 12.9）
conda env create -f https://raw.githubusercontent.com/scverse/rapids-singlecell/main/conda/rsc_rapids_26.04_cuda12.yml
conda activate rsc-rapids-26.04-cuda12

# CUDA 13（Python 3.14, CUDA 13.1）
conda env create -f https://raw.githubusercontent.com/scverse/rapids-singlecell/main/conda/rsc_rapids_26.04_cuda13.yml
conda activate rsc-rapids-26.04-cuda13
```

> RAPIDS 不支持 `channel_priority: strict`，请使用 `channel_priority: flexible`。

### 方式二：PyPI 预编译 wheel（推荐用于已有 RAPIDS 环境的用户）

```bash
# CUDA 12
pip install rapids-singlecell-cu12

# CUDA 13
pip install rapids-singlecell-cu13
```

如需一并安装 RAPIDS 依赖（cupy / cuml / cudf / librmm 等）：

```bash
# CUDA 12
pip install 'rapids-singlecell-cu12[rapids]' --extra-index-url=https://pypi.nvidia.com

# CUDA 13
pip install 'rapids-singlecell-cu13[rapids]' --extra-index-url=https://pypi.nvidia.com
```

### 方式三：Docker

```bash
# CUDA 12
docker pull ghcr.io/scverse/rapids-singlecell-cu12:latest
docker run --rm --gpus all ghcr.io/scverse/rapids-singlecell-cu12:latest

# CUDA 13
docker pull ghcr.io/scverse/rapids-singlecell-cu13:latest
docker run --rm --gpus all ghcr.io/scverse/rapids-singlecell-cu13:latest
```

HPC/SLURM 场景可用 apptainer：

```bash
apptainer pull rsc.sif docker://ghcr.io/scverse/rapids-singlecell-cu13:latest
apptainer run --nv rsc.sif
```

## 验证 GPU

```python
import cupy as cp
print(f"CUDA available: {cp.cuda.is_available()}")
if cp.cuda.is_available():
    props = cp.cuda.runtime.getDeviceProperties(0)
    print(f"GPU: {props['name'].decode()}")
```

## 标准分析流程

### 1. 导入与 AnnData 迁移到 GPU

```python
import time
import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import scanpy as sc
import rapids_singlecell as rsc
import cupy as cp
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# 将 AnnData 整体迁移到 GPU（推荐）
rsc.get.anndata_to_GPU(adata)

# 或仅迁移 .X
# adata.X = cpx_sparse.csr_matrix(adata.X)

# 迁回 CPU
# rsc.get.anndata_to_CPU(adata)
```

> **重要提示**: 不要手动配置 rmm 内存管理器（如 `rmm.reinitialize()`），这可能导致内存分配冲突。让 rapids_singlecell 使用默认内存管理即可。

### 2. 读取数据

```python
# 读取10x数据
adata = sc.read_10x_mtx(data_path, var_names="gene_symbols", cache=True)

# 或读取h5ad文件
adata = sc.read_h5ad("data.h5ad")
```

### 3. 质量控制

```python
# 计算QC指标
adata.var["mt"] = adata.var_names.str.startswith("MT-")
sc.pp.calculate_qc_metrics(adata, qc_vars=["mt"], percent_top=None, log1p=False, inplace=True)

# 过滤细胞（阈值需根据数据调整）
adata = adata[adata.obs.n_genes_by_counts < 2500, :]
adata = adata[adata.obs.pct_counts_mt < 5, :]
```

### 4. 标准化与特征选择

```python
# 标准化（counts 层）
sc.pp.normalize_total(adata, target_sum=1e4)
sc.pp.log1p(adata)

# 选择高变基因（官方推荐 seurat_v3 flavor + layer + batch_key）
rsc.pp.highly_variable_genes(
    adata,
    n_top_genes=2000,
    flavor="seurat_v3",
    layer="counts",
    batch_key="sample",
)
adata_hvg = adata[:, adata.var["highly_variable"]].copy()

# GPU 回归去变量
rsc.pp.regress_out(adata_hvg, keys=["total_counts", "pct_counts_MT"])

# 缩放
rsc.pp.scale(adata_hvg, max_value=10)
```

> 如未保留 `counts` 层，可回退到 `sc.pp.highly_variable_genes(..., flavor="seurat", batch_key="sample")`。

### 5. GPU 加速降维 / 聚类 / 差异表达

```python
# GPU PCA
rsc.pp.pca(adata_hvg, n_comps=50)

# GPU 邻居计算
rsc.pp.neighbors(adata_hvg, n_neighbors=15, n_pcs=30)

# GPU UMAP
rsc.tl.umap(adata_hvg, min_dist=0.5, spread=1.0)

# GPU Leiden 聚类
rsc.tl.leiden(adata_hvg, resolution=1.0)

# GPU Louvain 聚类
rsc.tl.louvain(adata_hvg, resolution=1.0)

# GPU t-SNE
rsc.tl.tsne(adata_hvg, n_pcs=30)

# GPU 差异表达 (注意: use_raw=False)
rsc.tl.rank_genes_groups(adata_hvg, groupby="leiden", method="wilcoxon", use_raw=False)
```

### 6. Harmony 批次校正（可选）

```python
import harmonypy as hm

pca_data = np.array(adata_hvg.obsm["X_pca"])  # 转 numpy 避免 GPU 内存问题
ho = hm.run_harmony(pca_data, adata_hvg.obs, vars_use=["sample"], max_iter_harmony=20)

# 重要：ho.Z_corr 形状为 (n_cells, n_pcs)，直接赋值，**不要转置**
adata_hvg.obsm["X_pca_harmony"] = ho.Z_corr

rsc.pp.neighbors(adata_hvg, n_neighbors=15, n_pcs=30, use_rep="X_pca_harmony")
rsc.tl.umap(adata_hvg, min_dist=0.5, spread=1.0)
rsc.tl.tsne(adata_hvg, n_pcs=30, use_rep="X_pca_harmony")
```

### 7. 可视化

```python
sc.pl.umap(adata_hvg, color="leiden")
sc.pl.tsne(adata_hvg, color="leiden")

fig, axes = plt.subplots(2, 2, figsize=(12, 10))
sc.pl.umap(adata_hvg, color="leiden", ax=axes[0, 0], show=False)
sc.pl.tsne(adata_hvg, color="leiden", ax=axes[0, 1], show=False)
sc.pl.umap(adata_hvg, color="total_counts", ax=axes[1, 0], show=False)
sc.pl.umap(adata_hvg, color="pct_counts_mt", ax=axes[1, 1], show=False)
plt.tight_layout()
plt.savefig("results.png", dpi=150)
plt.savefig("results.pdf")
```

## 可用功能总览

| 模块 | 功能 | 说明 |
|------|------|------|
| `rsc.pp` | `highly_variable_genes` / `pca` / `neighbors` / `regress_out` / `scale` | GPU 预处理 |
| `rsc.tl` | `umap` / `tsne` / `leiden` / `louvain` / `rank_genes_groups` | GPU 降维 / 聚类 / 差异表达 |
| `rsc.get` | `anndata_to_GPU` / `anndata_to_CPU` | AnnData 与 GPU 互转 |
| `rsc.dcg` | `mlm` / `ulm` / `aucell` | decoupler 通路评分（GPU） |
| `rsc.ptg` | `Distance` 等 | pertpy 扰动分析（GPU） |
| `rsc.gr` | `spatial_autocorr` / `co_occurrence` / `ligrec` | Squidpy 空间分析（GPU） |
| `harmonypy` | `run_harmony` | 批次校正（CPU） |

### decoupler-GPU 通路评分示例

```python
import decoupler as dc
import rapids_singlecell as rsc

model = dc.op.resource("PanglaoDB", organism="human")
rsc.dcg.ulm(adata, model, tmin=3)
acts_ulm = dc.pp.get_obsm(adata, key="score_ulm")
sc.pl.umap(acts_ulm, color=["NK cells"], cmap="coolwarm", vcenter=0)
```

### pertpy-GPU 扰动分析示例

```python
from rapids_singlecell import ptg

distance = ptg.Distance(metric="edistance", obsm_key="X_pca")
result = distance.pairwise(adata, groupby="perturbation")
```

### Squidpy-GPU 空间分析示例

```python
rsc.gr.spatial_autocorr(adata, connectivity_key="spatial_connectivities", mode="moran", n_perms=500)
rsc.gr.co_occurrence(adata, cluster_key="labels", interval=50)
rsc.gr.ligrec(adata, cluster_key="labels", n_perms=1000)
```

## 注意事项

1. **use_raw 参数**: `rsc.tl.rank_genes_groups` 必须设置 `use_raw=False`，除非之前已设置 `adata.raw`
2. **数据路径**: 使用 Python 字符串路径即可；若在 WSL2 下访问 Windows 文件，使用 `/mnt/盘符/路径` 格式
3. **内存限制**: GPU 显存容量决定可处理的细胞规模（视具体数据与显存而定）
4. **图片输出**: 同时生成 PNG 和 PDF 两种格式

## 常见问题与解决方案

### 1. GPU 内存不足 (CUDA out of memory)

**症状**: `MemoryError: std::bad_alloc: out_of_memory: CUDA error`

**解决方案**:
- 移除 `rmm` 内存管理配置，使用简单导入
- HVG 选择使用 `flavor="seurat_v3"` + `layer="counts"`
- 确保 PCA 矩阵转换为 numpy 数组后再传给 Harmony

```python
# 错误：手动配置 rmm
import rmm
from rmm.allocators.cupy import rmm_cupy_allocator
cp.cuda.set_allocator(rmm_cupy_allocator)
rmm.reinitialize(managed_memory=True)

# 正确：简单导入
import rapids_singlecell as rsc
import cupy as cp
```

### 2. 导入 rapids_singlecell 即报 ImportError

**症状**: `ImportError: ... librmm ... rapids_logger ...` 或 `ImportError: cuml`

**原因**: RAPIDS 栈（`cupy` / `cuml` / `cudf` / `librmm` / `rapids_logger`）是**必需依赖**，缺失会在 `import rapids_singlecell` 时立即报错。

**解决方案**:
- conda 用户：使用官方 yaml（已包含 RAPIDS）
- PyPI 用户：使用带 `[rapids]` extra 的安装命令：
  ```bash
  pip install 'rapids-singlecell-cu13[rapids]' --extra-index-url=https://pypi.nvidia.com
  ```
- Docker 用户：直接使用官方镜像即可

### 3. Harmony 形状错误 (incorrect shape)

**症状**: `ValueError: Value passed for key 'X_pca_harmony' is of incorrect shape`

**原因**: `ho.Z_corr` 的形状已经是 `(n_cells, n_pcs)`，不需要转置

```python
# 错误：转置
adata.obsm["X_pca_harmony"] = ho.Z_corr.T

# 正确：直接赋值
adata.obsm["X_pca_harmony"] = ho.Z_corr
```

### 4. 容器内找不到 CUDA 库（HPC/SLURM）

**症状**: `TypeError: expected str, bytes or os.PathLike object, not NoneType`

**原因**: 通过 SLURM + apptainer 运行时未激活 conda

**解决方案**: 使用 `apptainer exec` 显式激活 base 环境：
```bash
apptainer exec --nv \
    --bind /path/to/your/data:/path/to/your/data \
    rsc.sif \
    bash -c "source /opt/conda/etc/profile.d/conda.sh && conda activate base && python"
```

## 性能对比（参考）

针对 ~10k 细胞数据集，GPU 加速相比 CPU 可达约 10–15 倍速度提升；实际提升视硬件（GPU 算力 / 显存）与数据规模而定。

| 步骤 | GPU 时间 | CPU 时间（估计） |
|------|---------|----------------|
| PCA | ~0.8秒 | ~8秒 |
| Neighbors | ~0.3秒 | ~15秒 |
| UMAP | ~0.4秒 | ~30秒 |
| Leiden | ~2秒 | ~15秒 |
| t-SNE | ~0.5秒 | ~60秒 |
| Markers | ~2秒 | ~20秒 |

## 完整示例脚本

```python
#!/usr/bin/env python3
"""GPU单细胞标准分析流程"""
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

# 数据路径（替换为你的实际路径）
DATA_PATH = "/path/to/pbmc"

# 读取数据
adata = sc.read_10x_mtx(DATA_PATH, var_names="gene_symbols", cache=True)
print(f"Loaded: {adata.n_obs} cells x {adata.n_vars} genes")

# QC
adata.var["mt"] = adata.var_names.str.startswith("MT-")
sc.pp.calculate_qc_metrics(adata, qc_vars=["mt"], inplace=True)
adata = adata[adata.obs.n_genes_by_counts < 2500, :]
adata = adata[adata.obs.pct_counts_mt < 5, :]

# 标准化
sc.pp.normalize_total(adata, target_sum=1e4)
sc.pp.log1p(adata)

# HVG（seurat_v3 + counts 层）
if "counts" in adata.layers:
    rsc.pp.highly_variable_genes(
        adata, n_top_genes=2000,
        flavor="seurat_v3", layer="counts", batch_key="sample",
    )
else:
    sc.pp.highly_variable_genes(adata, n_top_genes=2000, flavor="seurat", batch_key="sample")

adata_hvg = adata[:, adata.var["highly_variable"]].copy()
rsc.pp.regress_out(adata_hvg, keys=["total_counts", "pct_counts_MT"])
rsc.pp.scale(adata_hvg, max_value=10)

# AnnData 迁到 GPU
rsc.get.anndata_to_GPU(adata_hvg)

# GPU 分析
rsc.pp.pca(adata_hvg, n_comps=50)

# Harmony 批次校正（多批次数据时使用）
import harmonypy as hm
pca_data = np.array(adata_hvg.obsm["X_pca"])
ho = hm.run_harmony(pca_data, adata_hvg.obs, vars_use=["sample"], max_iter_harmony=20)
adata_hvg.obsm["X_pca_harmony"] = ho.Z_corr

rsc.pp.neighbors(adata_hvg, n_neighbors=15, n_pcs=30, use_rep="X_pca_harmony")
rsc.tl.umap(adata_hvg)
rsc.tl.leiden(adata_hvg, resolution=1.0)
rsc.tl.tsne(adata_hvg, n_pcs=30, use_rep="X_pca_harmony")
rsc.tl.rank_genes_groups(adata_hvg, groupby="leiden", method="wilcoxon", use_raw=False)

adata_hvg.write("results.h5ad")
print("Analysis complete!")
```