---
name: spatial-deconvolution
description: 使用带注释的单细胞 RNA 测序参考数据估计空间转录组 spot 的细胞类型丰度与相对比例；默认使用 cell2location，并通过输入质量控制、后验不确定性、marker 与空间一致性验证结果。适用于 Visium、Slide-seq 等 spot-based 空间转录组数据。
tool_type: python
primary_tool: cell2location
---

# 空间转录组细胞类型去卷积

将带细胞类型注释的 scRNA-seq 参考数据与空间转录组数据整合，估计每个 spot 中各细胞类型的**丰度（abundance）**与**相对比例（proportion）**。

> **重要限制：** 去卷积结果是统计模型的估计，不是单细胞级的真实计数。结果应结合组织学、marker、空间分布和独立数据进行解释；不要只根据每个 spot 的 dominant cell type 下结论。

## 方法选择

| 需求 | 优先方法 | 说明 |
|---|---|---|
| 估计 spot 内细胞类型丰度，并量化后验不确定性 | **cell2location** | 默认方法；适合 spot-based 数据和带较可靠注释的 scRNA-seq 参考。 |
| 将细胞或细胞群映射至空间位置 | Tangram | 适合关注细胞—空间映射；应谨慎选择 marker 并检查映射质量。 |
| 需要显式 doublet-mode 建模，且可使用 R | RCTD / `spacexr` | 适合在 R 工作流中分析；需要准备 RCTD 所需的 counts 与坐标对象。 |
| 希望提高结论稳健性 | 至少两种方法交叉检查 | 比较空间模式与相对排序，不要预期不同模型给出完全相同的绝对丰度。 |

本文档提供 **cell2location** 的完整、可审计流程；Tangram 和 RCTD 可作为独立交叉验证方案。

---

## 0. 前置条件与分析原则

### 必需输入

- `reference_scrna.h5ad`：带 `obs["cell_type"]` 的单细胞参考数据；矩阵必须是原始、非负的 counts，或能从 `layers["counts"]` 获取。
- `spatial_data.h5ad`：空间表达数据；矩阵必须是原始、非负的 counts，或能从 `layers["counts"]` 获取；需要 `obsm["spatial"]` 坐标。

### 重要前提

1. 参考与空间数据应来自相同物种，且具有可比的组织/疾病背景。
2. 基因标识符必须统一：不要混用 gene symbol 与 Ensembl ID；必要时先去除 Ensembl 版本后缀并做一对一映射。
3. 参考注释的粒度应与问题匹配。不要把技术状态、低质量细胞或 doublet 当成稳定细胞类型。
4. cell2location 使用 count 模型；**不要把 log-normalized、scaled 或 batch-corrected 矩阵作为模型输入。**
5. 所有下游操作在 `.copy()` 后的对象上完成，避免无意修改原始输入。

---

## 1. 环境、随机性与数据加载

```python
import os
import sys
import random
from pathlib import Path

import anndata as ad
import numpy as np
import pandas as pd
import scanpy as sc
import torch
from scipy import sparse

SEED = 42
random.seed(SEED)
np.random.seed(SEED)
torch.manual_seed(SEED)
if torch.cuda.is_available():
    torch.cuda.manual_seed_all(SEED)

# 若追求更严格的确定性，可启用；部分 GPU 算子可能因此报不支持或变慢。
# torch.use_deterministic_algorithms(True)

use_gpu = torch.cuda.is_available()
print({
    "python": sys.version,
    "scanpy": sc.__version__,
    "anndata": ad.__version__,
    "torch": torch.__version__,
    "device": "cuda" if use_gpu else "cpu",
    "seed": SEED,
})

adata_ref = sc.read_h5ad("reference_scrna.h5ad").copy()
adata_vis = sc.read_h5ad("spatial_data.h5ad").copy()
```

> 不同 cell2location / scvi-tools 版本的训练参数可能略有差异。若出现 `TypeError`、`ImportError` 或 `AttributeError`，先检查已安装版本和函数签名，再调整调用方式；不要盲目重复训练。

---

## 2. 选择并验证原始 counts

优先使用 `layers["counts"]` 中保存的原始矩阵，然后再进行检查。这样不会把 `adata.X` 中的 log-normalized 表达误判为模型输入。

```python
def use_counts_layer_if_available(adata, name):
    if "counts" in adata.layers:
        adata.X = adata.layers["counts"].copy()
        print(f"{name}: 使用 layers['counts'] 作为模型输入")
    else:
        print(f"{name}: 未发现 layers['counts']，使用 adata.X")
    return adata


def validate_count_matrix(adata, name):
    x = adata.X.data if sparse.issparse(adata.X) else np.asarray(adata.X)
    if x.size == 0:
        raise ValueError(f"{name}.X 为空")
    if not np.isfinite(x).all():
        raise ValueError(f"{name}.X 包含 NaN 或无穷值")
    if np.any(x < 0):
        raise ValueError(f"{name}.X 含负值，不是有效的原始 counts")
    if not np.allclose(x, np.round(x), rtol=0, atol=1e-6):
        raise ValueError(
            f"{name}.X 不是整数型 counts；请确认没有将 log-normalized 数据用于 cell2location"
        )

adata_ref = use_counts_layer_if_available(adata_ref, "adata_ref")
adata_vis = use_counts_layer_if_available(adata_vis, "adata_vis")
validate_count_matrix(adata_ref, "adata_ref")
validate_count_matrix(adata_vis, "adata_vis")
```

---

## 3. 参考与空间数据的最小质量控制

### 3.1 结构与注释检查

```python
assert "cell_type" in adata_ref.obs, "参考数据缺少 obs['cell_type']"
assert adata_ref.obs["cell_type"].notna().all(), "cell_type 含缺失值"
assert adata_ref.obs["cell_type"].nunique() >= 2, "至少需要两个细胞类型"
assert "spatial" in adata_vis.obsm, "空间数据缺少 obsm['spatial']"
assert adata_vis.obsm["spatial"].shape[0] == adata_vis.n_obs, "空间坐标与 spot 数不一致"

adata_ref.obs["cell_type"] = adata_ref.obs["cell_type"].astype("category")
adata_ref.var_names = adata_ref.var_names.astype(str)
adata_vis.var_names = adata_vis.var_names.astype(str)

# 确保基因名唯一；重复基因应在上游按规则汇总或移除，而不是静默保留。
if not adata_ref.var_names.is_unique:
    raise ValueError("参考数据 var_names 不唯一；请先处理重复基因")
if not adata_vis.var_names.is_unique:
    raise ValueError("空间数据 var_names 不唯一；请先处理重复基因")

cell_type_counts = adata_ref.obs["cell_type"].value_counts()
print("参考数据形状:", adata_ref.shape)
print("空间数据形状:", adata_vis.shape)
print("每类参考细胞数:\n", cell_type_counts)

min_cells_per_type = 5
rare_types = cell_type_counts[cell_type_counts < min_cells_per_type]
if not rare_types.empty:
    raise ValueError(
        "以下 cell type 的参考细胞数少于 "
        f"{min_cells_per_type}，估计将非常不稳定：{rare_types.to_dict()}"
    )
```

### 3.2 spot 质量检查（按数据集调整阈值）

以下检查用于**诊断**，而不是统一删除规则。应结合平台、组织、测序深度和组织掩膜决定最终阈值。

```python
# 若这些列不存在，先从 counts 计算基本 QC 指标。
if "total_counts" not in adata_vis.obs:
    adata_vis.obs["total_counts"] = np.asarray(adata_vis.X.sum(axis=1)).ravel()
if "n_genes_by_counts" not in adata_vis.obs:
    adata_vis.obs["n_genes_by_counts"] = np.asarray((adata_vis.X > 0).sum(axis=1)).ravel()

print(adata_vis.obs[["total_counts", "n_genes_by_counts"]].describe())

# 示例：仅标记低质量 spot，不在此处自动过滤。
low_count_cutoff = np.quantile(adata_vis.obs["total_counts"], 0.01)
low_gene_cutoff = np.quantile(adata_vis.obs["n_genes_by_counts"], 0.01)
adata_vis.obs["low_quality_candidate"] = (
    (adata_vis.obs["total_counts"] <= low_count_cutoff)
    | (adata_vis.obs["n_genes_by_counts"] <= low_gene_cutoff)
)
print("待人工复核的低质量候选 spot:", int(adata_vis.obs["low_quality_candidate"].sum()))
```

> 如果数据有 Visium 组织掩膜、线粒体比例或空白 spot 标记，应优先纳入 QC。低质量或组织外 spot 可能导致假阳性细胞类型信号。

---

## 4. 基因匹配与筛选

```python
from cell2location.utils.filtering import filter_genes

shared_genes = adata_ref.var_names.intersection(adata_vis.var_names)
if len(shared_genes) < 100:
    raise ValueError(
        f"共享基因仅 {len(shared_genes)} 个；请检查物种、gene symbol/Ensembl ID、大小写及 Ensembl 版本后缀"
    )

adata_ref = adata_ref[:, shared_genes].copy()
adata_vis = adata_vis[:, shared_genes].copy()

selected = np.asarray(filter_genes(
    adata_ref,
    cell_count_cutoff=5,
    cell_percentage_cutoff2=0.03,
    nonz_mean_cutoff=1.12,
))
if selected.dtype == bool:
    selected = adata_ref.var_names[selected]

if len(selected) < 100:
    raise ValueError(f"筛选后基因过少：{len(selected)}；请检查参考数据质量或适当调整筛选阈值")

adata_ref = adata_ref[:, selected].copy()
adata_vis = adata_vis[:, selected].copy()
assert adata_ref.var_names.equals(adata_vis.var_names), "筛选后基因顺序不一致"
print("用于建模的共享基因数:", adata_ref.n_vars)
```

> 不要在模型输入上执行 `normalize_total`、`log1p` 或 `scale`。marker 可视化可使用独立副本进行标准化，但 cell2location 的训练对象应保持 counts。

---

## 5. 训练参考表达签名模型

```python
from cell2location.models import RegressionModel

RegressionModel.setup_anndata(adata_ref, labels_key="cell_type")
mod_ref = RegressionModel(adata_ref)
mod_ref.train(max_epochs=250, use_gpu=use_gpu)

adata_ref = mod_ref.export_posterior(
    adata_ref,
    sample_kwargs={"num_samples": 1000},
)
ref_sig = adata_ref.varm["means_per_cluster_mu_fg"]

cell_types = list(adata_ref.obs["cell_type"].cat.categories)
assert ref_sig.shape == (adata_ref.n_vars, len(cell_types))
print("细胞类型:", cell_types)
```

训练完成后，应检查日志、ELBO/损失曲线或模型自带诊断信息是否稳定。若未收敛、出现 NaN 或损失异常波动，先检查 counts、参考注释、稀有细胞类型和软件版本。

---

## 6. 训练空间去卷积模型

`N_cells_per_location` 与 `detection_alpha` 是先验参数，不是通用常数：

- `N_cells_per_location`：应根据平台 spot 面积、组织密度和预期每 spot 细胞数设定。
- `detection_alpha`：与检测灵敏度先验有关；需结合平台与结果诊断调整。
- 建议至少运行一组合理替代参数，检查主要空间模式是否稳定。

```python
from cell2location.models import Cell2location

N_CELLS_PER_LOCATION = 10
DETECTION_ALPHA = 20
SPATIAL_MAX_EPOCHS = 3000

Cell2location.setup_anndata(adata_vis)
mod_spatial = Cell2location(
    adata_vis,
    cell_state_df=ref_sig,
    N_cells_per_location=N_CELLS_PER_LOCATION,
    detection_alpha=DETECTION_ALPHA,
)
mod_spatial.train(max_epochs=SPATIAL_MAX_EPOCHS, use_gpu=use_gpu)

adata_vis = mod_spatial.export_posterior(
    adata_vis,
    sample_kwargs={"num_samples": 1000},
)
```

---

## 7. 提取丰度、比例与后验不确定性

`q05_cell_abundance_w_sf` 是后验丰度的第 5 百分位，属于较保守估计。若对象中也提供 `q50` 与 `q95`，应同时导出以刻画不确定性。

```python
def get_abundance_quantile(adata, key):
    if key not in adata.obsm:
        return None
    value = np.asarray(adata.obsm[key], dtype=float)
    if value.shape != (adata.n_obs, len(cell_types)):
        raise ValueError(f"{key} 的形状为 {value.shape}，与预期不符")
    if not np.isfinite(value).all() or np.any(value < 0):
        raise ValueError(f"{key} 含无效或负的 abundance")
    return value

abundance_q05 = get_abundance_quantile(adata_vis, "q05_cell_abundance_w_sf")
abundance_q50 = get_abundance_quantile(adata_vis, "q50_cell_abundance_w_sf")
abundance_q95 = get_abundance_quantile(adata_vis, "q95_cell_abundance_w_sf")

# 若没有 q50，使用 q05 作为保守主估计，并在报告中明确说明。
abundances = abundance_q50 if abundance_q50 is not None else abundance_q05
if abundances is None:
    available = [k for k in adata_vis.obsm.keys() if "cell_abundance" in k]
    raise KeyError(f"未找到 cell abundance 结果；可用相关键：{available}")

row_sums = abundances.sum(axis=1, keepdims=True)
proportions = np.divide(
    abundances,
    row_sums,
    out=np.zeros_like(abundances, dtype=float),
    where=row_sums > 0,
)

adata_vis.obsm["cell_type_abundances"] = abundances
adata_vis.obsm["cell_type_proportions"] = proportions
adata_vis.obs["estimated_total_cells"] = row_sums[:, 0]
adata_vis.obs["dominant_cell_type"] = pd.Categorical(
    np.asarray(cell_types, dtype=object)[proportions.argmax(axis=1)],
    categories=cell_types,
)

if abundance_q05 is not None:
    adata_vis.obsm["cell_type_abundances_q05"] = abundance_q05
if abundance_q50 is not None:
    adata_vis.obsm["cell_type_abundances_q50"] = abundance_q50
if abundance_q95 is not None:
    adata_vis.obsm["cell_type_abundances_q95"] = abundance_q95
    lower = abundance_q05 if abundance_q05 is not None else abundances
    adata_vis.obsm["cell_type_abundance_interval_width"] = abundance_q95 - lower

zero_sum = int((row_sums[:, 0] == 0).sum())
if zero_sum:
    print(f"警告：{zero_sum} 个 spot 的总 abundance 为 0；其比例已设置为 0，应单独复核")
```

> 将 abundance 转为比例会丢失“该 spot 总细胞量”的信息。报告时应同时保留 abundance、proportion 和 `estimated_total_cells`。

---

## 8. 结果验证：使用多条相互独立的证据

不要将单一数值阈值作为通用的“成功/失败”判据。优先评估以下证据是否共同支持结论：

1. **Marker 一致性**：多个特异 marker 与对应 abundance/proportion 的关系是否为预期方向；
2. **空间合理性**：空间分布是否与组织结构、病理区域或组织学标记一致；
3. **丰度合理性**：是否存在某类型在几乎所有 spot 中异常占优；
4. **质量关联**：异常信号是否集中于低 UMI、低基因数或组织外 spot；
5. **不确定性**：关键结论是否来自后验区间很宽的估计；
6. **稳健性**：调整合理的先验参数或采用第二种方法后，主要空间模式是否保持一致。

### 8.1 Marker 相关性诊断

在 counts 上计算 marker 平均表达仅作诊断；若需可视化表达，可在独立副本中做归一化。

```python
marker_genes = {
    "T_cell": ["CD3D", "CD3E", "TRBC1"],
    "Macrophage": ["CD68", "LST1", "C1QC"],
    "Epithelial": ["EPCAM", "KRT8", "KRT18"],
}


def mean_expression(adata, genes):
    available = [gene for gene in genes if gene in adata.var_names]
    if not available:
        return None, []
    x = adata[:, available].X
    return np.asarray(x.mean(axis=1)).ravel(), available

validation_rows = []
for cell_type, markers in marker_genes.items():
    if cell_type not in cell_types:
        continue
    marker_expr, available = mean_expression(adata_vis, markers)
    if marker_expr is None:
        validation_rows.append({
            "cell_type": cell_type,
            "markers_used": "",
            "marker_abundance_correlation": np.nan,
            "note": "无可用 marker",
        })
        continue

    abundance = abundances[:, cell_types.index(cell_type)]
    if np.std(marker_expr) == 0 or np.std(abundance) == 0:
        corr = np.nan
        note = "表达或丰度无变异，无法计算相关性"
    else:
        corr = float(np.corrcoef(marker_expr, abundance)[0, 1])
        note = "相关性仅作诊断；应结合多个 marker 与空间分布解释"

    validation_rows.append({
        "cell_type": cell_type,
        "markers_used": ",".join(available),
        "marker_abundance_correlation": corr,
        "note": note,
    })

validation_df = pd.DataFrame(validation_rows)
print(validation_df)
```

### 8.2 异常主导与低质量 spot 检查

```python
dominant_fraction = (
    adata_vis.obs["dominant_cell_type"]
    .value_counts(normalize=True)
    .rename("dominant_spot_fraction")
)
print("各类型成为 dominant spot 的比例:\n", dominant_fraction)

# 检查 dominant type 是否与低质量候选 spot 过度重叠。
qc_crosstab = pd.crosstab(
    adata_vis.obs["dominant_cell_type"],
    adata_vis.obs["low_quality_candidate"],
    normalize="index",
)
print("各 dominant type 中低质量候选 spot 的比例:\n", qc_crosstab)
```

---

## 9. 空间可视化

```python
import matplotlib.pyplot as plt

cell_types_to_plot = ["T_cell", "Macrophage", "Epithelial"]
for cell_type in cell_types_to_plot:
    if cell_type not in cell_types:
        continue
    key = f"{cell_type}_proportion"
    adata_vis.obs[key] = proportions[:, cell_types.index(cell_type)]
    sc.pl.spatial(
        adata_vis,
        color=key,
        title=f"{cell_type} proportion",
        cmap="Reds",
        vmin=0,
        vmax="p99",
        show=False,
    )
    plt.savefig(f"{cell_type}_proportion_spatial.png", dpi=180, bbox_inches="tight")
    plt.close()
```

> 不同 cell type 的空间图如需进行绝对强度比较，应使用统一色阶；若主要观察每个类型的空间模式，可采用各图独立的稳健上限（如 `p99`），但必须在图注中说明。

---

## 10. 导出结果、参数与审计信息

```python
prop_df = pd.DataFrame(proportions, index=adata_vis.obs_names, columns=cell_types)
abundance_df = pd.DataFrame(abundances, index=adata_vis.obs_names, columns=cell_types)

prop_df.to_csv("cell_type_proportions.csv")
abundance_df.to_csv("cell_type_abundances.csv")
validation_df.to_csv("deconvolution_marker_validation.csv", index=False)

if abundance_q05 is not None:
    pd.DataFrame(abundance_q05, index=adata_vis.obs_names, columns=cell_types).to_csv(
        "cell_type_abundances_q05.csv"
    )
if abundance_q95 is not None:
    pd.DataFrame(abundance_q95, index=adata_vis.obs_names, columns=cell_types).to_csv(
        "cell_type_abundances_q95.csv"
    )

adata_vis.uns["deconvolution_parameters"] = {
    "method": "cell2location",
    "seed": SEED,
    "n_shared_genes_before_filtering": int(len(shared_genes)),
    "n_genes_used": int(adata_vis.n_vars),
    "n_spots": int(adata_vis.n_obs),
    "cell_types": cell_types,
    "use_gpu": bool(use_gpu),
    "reference_max_epochs": 250,
    "spatial_max_epochs": SPATIAL_MAX_EPOCHS,
    "N_cells_per_location": N_CELLS_PER_LOCATION,
    "detection_alpha": DETECTION_ALPHA,
    "scanpy_version": sc.__version__,
    "anndata_version": ad.__version__,
    "torch_version": torch.__version__,
}
adata_vis.write_h5ad("spatial_deconvolved.h5ad")

with open("deconvolution_parameters.txt", "w", encoding="utf-8") as f:
    for key, value in adata_vis.uns["deconvolution_parameters"].items():
        f.write(f"{key}={value}\n")
```

---

## 11. 建议交付与复核清单

完成后应交付：

1. `cell_type_abundances.csv`：每 spot 的估计丰度；
2. `cell_type_proportions.csv`：每 spot 的相对比例；
3. `spatial_deconvolved.h5ad`：包含全部模型结果与审计参数；
4. `deconvolution_marker_validation.csv`：marker 诊断结果；
5. 每个关键细胞类型的空间分布图；
6. `deconvolution_parameters.txt`：软件版本、随机种子、输入规模及模型参数；
7. 一份简短结果说明，明确：主要空间模式、证据、限制、不确定性和异常 spot 处理。

在报告结论前确认：

- [ ] 参考与空间数据使用一致的物种和基因 ID 类型；
- [ ] 模型输入是原始 counts，而不是归一化/对数转换矩阵；
- [ ] 每个目标 cell type 有足够的参考细胞，且参考注释可信；
- [ ] 关键细胞类型有多个 marker 与空间结构共同支持；
- [ ] 异常结果未主要由低质量或组织外 spot 驱动；
- [ ] 关键结论未完全依赖后验区间很宽的估计；
- [ ] 改变合理先验或采用独立方法后，主要空间模式仍大致一致。

---

## 常见问题与排查

| 问题 | 优先排查 |
|---|---|
| 共享基因过少 | 物种、gene symbol/Ensembl ID、大小写、Ensembl 版本后缀、重复基因处理。 |
| 模型提示 counts 错误 | 先使用 `layers['counts']`；确认没有将 normalized/log-transformed 数据放入 `X`。 |
| GPU 或 CUDA 报错 | 使用 `torch.cuda.is_available()` 自动降级；检查 PyTorch、CUDA、cell2location/scvi-tools 版本兼容性。 |
| 内存不足 | 减少基因数、posterior sample 数或 batch size；不要在模型输入上创建不必要的稠密矩阵。 |
| 单一细胞类型几乎占满所有 spot | 检查参考注释与细胞数、marker 特异性、基因匹配、环境 RNA、低质量/组织外 spot 和先验参数。 |
| abundance/proportion 出现 NaN | 检查模型输出是否包含无效值、行和是否为零、输入 counts 是否正确。 |
| marker 相关性低或为负 | 不要只看单个 marker；检查 marker 可用性、组织特异性、参考与空间平台差异、空间结构和 posterior 不确定性。 |
| 多方法结果不一致 | 比较空间模式、相对排序和高置信区域；不同模型的绝对丰度通常不可直接等同。 |

