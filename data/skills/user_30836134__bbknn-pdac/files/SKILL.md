---
name: "tool-bbknn-integration"
description: "bbknnR批次整合工具方法：RunBBKNN替代FindNeighbors+RunUMAP一步完成，含版本锁定1.1.0、稀疏批次降neighbors_within_batch、虚拟池合并策略与断言校验。Invoke when单细胞多样本批次整合、替代Harmony、或bbknnR报错排查。"
---

> **作者 (author)**: LKP <kunpeng.liao@abiosciences.com>
> **Skill 及脚本参数来源**: Chen et al., 2025, *Cancer Cell* 43, 1656–1676, <https://doi.org/10.1016/j.ccell.2025.06.020>


# bbknnR 批次整合（BBKNN）

BBKNN（Batch Balanced KNN）：对每个 batch 分别取 K 近邻再合并建图，直接产出图 + UMAP，替代 FindNeighbors/RunHarmony 路线。

## 版本锁定

```r
# 必须 1.1.0，其他版本行为不可比，直接断言
stopifnot(as.character(packageVersion("bbknnR")) == "1.1.0")
```

安装（清华源）：

```r
install.packages("remotes", repos = "https://mirrors.tuna.tsinghua.edu.cn/CRAN/")
remotes::install_github("zhengyanan/bbknnR", ref = "v1.1.0")
```

## 标准调用

```r
# 前置：NormalizeData → FindVariableFeatures(vst, 3000) → ScaleData → RunPCA(npcs=30)
obj <- bbknnR::RunBBKNN(
  object                = obj,
  batch_key             = "orig.ident",   # 批次元数据列
  n_pcs                 = 30,             # 用前30个PC
  neighbors_within_batch = 3,             # 每批次取3近邻
  run_UMAP              = TRUE,
  seed                  = 2023
)
# 产物：obj@graphs$bbknn_snn（图）+ obj@reductions$umap
# 聚类直接用 bbknn 图：
graph_name <- grep("bbknn", names(obj@graphs), value = TRUE)[1]
obj <- FindClusters(obj, graph.name = graph_name, resolution = 1,
                    algorithm = 1, random.seed = 2023)
```

## 稀疏批次策略（关键工程细节）

```r
# 批次细胞数分布决定参数：
batch_tab <- table(obj$orig.ident)
min_batch <- min(batch_tab)
if (min_batch < 3) {
  nwb <- min(3L, as.integer(min_batch))    # 每batch近邻数不可超过该batch细胞数
}
if (min_batch < 2) {
  # 独苗批次：合并为虚拟池，仅用于BBKNN（元数据保留原值）
  small_batches <- names(batch_tab)[batch_tab < 2]
  obj$bbknn_batch_effective <- ifelse(obj$orig.ident %in% small_batches,
                                      "__blind_sparse_batch_pool__", obj$orig.ident)
  # 之后 batch_key = "bbknn_batch_effective"
}
```

## 断言校验（运行后必查）

```r
stopifnot(any(grepl("bbknn", names(obj@graphs))))     # 图已生成
stopifnot("umap" %in% names(obj@reductions))          # UMAP已生成
```

## 与其他整合方法对比

| 方法 | 适用 | 本项目用法 |
|---|---|---|
| BBKNN (bbknnR) | 样本多、速度敏感、大图谱 | 单细胞主线（30 PC / nwb=3） |
| Harmony | 连续协变量、平台差异 | 空间主线（group.by=c(orig.ident, technique_type)） |

## 常见坑

1. **不先跑 FindNeighbors**：BBKNN 直接给图，再跑 FindNeighbors 会覆盖或产生冗余图
2. **n_pcs 与 PCA 一致**：RunPCA 用 30 则 n_pcs=30，不一致导致图质量下降
3. **亚群重聚类同参数**：每个 compartment 重跑时同样 3000 HVG / 30 PC / nwb=3 / res=1，保证可比
