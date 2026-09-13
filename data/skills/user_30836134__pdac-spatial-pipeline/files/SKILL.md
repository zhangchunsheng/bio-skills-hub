---
name: "pdac-spatial-pipeline"
description: "Visium空间转录组全景复现工作流：预检→逐切片SCTransform→merge→PCA/Harmony整合→聚类→RCTD参考构建与逐片反卷积→权重合并→niche层次聚类重构→神经邻近(vicinity)分层→COMMOT/MISTy输入导出。Invoke when用户要跑空间全流程、多切片整合、空间反卷积或niche分析。"
---

> **作者 (author)**: LKP <kunpeng.liao@abiosciences.com>
> **Skill 及脚本参数来源**: Chen et al., 2025, *Cancer Cell* 43, 1656–1676, <https://doi.org/10.1016/j.ccell.2025.06.020>


# PDAC 空间转录组全景复现 Pipeline

适用于：多切片 Visium（CytAssist/fresh/FFPE 混合，本例 21 切片 81,714 spots）从 h5+tissue_positions 到 niche/邻域注释的全流程。

## 0. 全局约定

```r
Sys.setenv(PDAC_PROJECT_ROOT = "D:/项目根目录")
result_root <- file.path(Sys.getenv("PDAC_PROJECT_ROOT"), "复现分析结果")
set.seed(2023)
options(future.globals.maxSize = 100 * 1024^3)
future::plan("sequential")
```

对象演进链：`spatial_01_sct_<slide>` → `02_merged_sct` → `03_pca` → `04_harmony` → `05_clustered` → `06_rctd` → `07_niches` → `08_nerve_vicinity_proxy`，全部 `saveRDS(compress = FALSE)`。

## 1. 输入预检

```r
# 文件名解析：^(GSM[0-9]+)_(PA[0-9]+)(?:-([0-9]+))?_  → gsm/patient/replicate
# 平台推断：tar 包含 cytassist_image.tiff → "CytAssist"；
#           否则 feature_count > 25000 → "Visium_fresh"，否则 "Visium_FFPE"
# 坐标文件：优先 spatial/tissue_positions.csv，回退无表头 tissue_positions_list.csv（手动命名6列）
# 输出：tables/spatial_input_manifest.csv + SHA256 清单
```

## 2. 逐切片预处理（SCT）

```r
# 单切片读入
counts <- Read10X_h5(h5_path, use.names = TRUE, unique.features = TRUE)[["Gene Expression"]]
img <- Read10X_Image(image.dir, assay = "Spatial",
                     slice = paste0("slice_", gsub("-", "_", sample_id)),
                     image.name = "tissue_lowres_image.png", filter.matrix = TRUE)
sobj <- CreateSeuratObject(counts, assay = "Spatial", project = sample_id)
sobj <- RenameCells(sobj, add.cell.id = sample_id)  # 跨切片条码加前缀
# SCT（逐切片，关键：回归 nCount_Spatial）
sobj <- SCTransform(sobj, assay = "Spatial", new.assay.name = "SCT",
                    vars.to.regress = "nCount_Spatial", seed.use = 2023)
```

## 3. 合并与整合（Harmony）

```r
merged <- merge(x = slides[[1]], y = slides[-1], merge.data = TRUE)
DefaultAssay(merged) <- "SCT"
VariableFeatures(merged) <- Reduce(union, lapply(slides, VariableFeatures))  # 各片HVG并集
merged <- RunPCA(merged, assay = "SCT", npcs = 50, seed.use = 2023)
merged <- RunHarmony(merged, group.by.vars = c("orig.ident", "technique_type"),
                     reduction.use = "pca", dims.use = 1:30, reduction.save = "harmony")
merged <- FindNeighbors(merged, reduction = "harmony", dims = 1:30)
merged <- FindClusters(merged, resolution = 2, algorithm = 1, random.seed = 2023)
merged <- RunUMAP(merged, reduction = "harmony", dims = 1:30, seed.use = 2023)
```

## 4. RCTD 参考构建（监督标签 + spacexr）

```r
# 标签层级：作者marker表监督打分（每cluster取log2FC降序top30，过滤log2FC>=0.25且pct.1>=0.1，
#           权重=max(avg_log2FC, 0.25)），权重归一化后与RNA data层做crossprod，取最高分cluster
# 手工signature补充：Endothelial 3型（E01_Art-PECAM1等各5基因）
# 直接映射5型：Acinar→Acinar_PRSS1、Endocrine→Endocrine_CHGB、NK→NK_KLRF1、Platelet→Platelet_PPBP、Stellate→Stellate_RGS5
# 参考对象（eligible: n_umi >= 100 且标签非NA）
ref <- spacexr::Reference(counts, clusters = cell_types, nUMI = nUMI,
                          require_int = TRUE, n_max_cells = 10000, min_UMI = 100)
```

基因名修复：marker 不在矩阵行名时逐个剥离尾部数字直到命中（解决 10x 基因名重复后缀）。

## 5. 逐片 RCTD 反卷积

```r
# 稀有型过滤：spacexr create.RCTD 要求每型 >= 25 细胞，不足的型剔除后重建 Reference
counts_slice <- LayerData(spatial, assay = "Spatial",
                          layer = paste0("counts.", sample_id))  # Seurat5 分层关键！
coords <- GetTissueCoordinates(sobj, image = slice_name)[, 1:2]  # 取前2数值列为 x/y
puck <- spacexr::SpatialRNA(coords, counts, nUMI = colSums(counts), require_int = TRUE)
rctd <- spacexr::create.RCTD(puck, ref, max_cores = 8, keep_reference = FALSE)
rctd <- spacexr::run.RCTD(rctd, doublet_mode = "full")  # 论文式全模式
# 权重行归一化（强制行和>0）
```

## 6. 权重合并注入 Seurat

```r
# 各片权重列并集对齐、缺失补0、rbind 后整体行归一化
# major 层 = 亚型按 (cell_type→major) 映射列求和
# 注入 assay：手工 new(Class="Assay", counts=权重转置, key="rctd_") 保留下划线feature名
spatial[["RCTD"]]  <- 手工Assay(亚型权重)   # 之后 ScaleData(assay="RCTD")
spatial[["RCTD2"]] <- 手工Assay(major权重)
```

## 7. Niche 重构（层次聚类 + 一一指派）

```r
# 组成矩阵：RCTD counts 转置按行归一化（每spot亚型比例和=1），按 Louvain 簇求 colMeans
comp_scaled <- scale(composition)
hc <- hclust(dist(comp_scaled), method = "ward.D2")
groups <- cutree(hc, k = 12)  # 12组固定
# Archetype打分：config/spatial_niche_archetypes.csv（niche, feature_regex, weight），
#   分数 = 组内匹配regex的亚型比例之和 × weight 累加
# 一一指派：分数矩阵整体减全局最小值后 clue::solve_LSAP(shifted, maximum=TRUE) 匈牙利算法
spatial$niche3 <- assigned_niche  # factor 按名称排序
```

## 8. 神经邻近（vicinity）分层

```r
# Visium 图：FNN::get.knn(coords, k=12) 候选边；
#   边保留阈值 = median(第1近邻距离) × 1.25；igraph 无向图 simplify
# 种子：niche3 == "N12_Nerve" 的 spots
# 恶性分数：恶性ductal亚型(D02/D04/D07/D08/D09)比例之和
# 侵袭二分类：kmeans(malignant_fraction, centers=2, nstart=50)，中心高者=invaded_proxy
# 图距离：BFS 距离（虚拟超节点连全部种子后 distances()-1），max_layer=5
# 区域：layer 0=nerve；1:2=juxta-neural_1-2；3:5=peri-neural_3-5
```

## 9. 下游输入导出

```r
# COMMOT 元数据：spot_id/orig.ident/patient/NI/niche3(+nerve_proxy_class/nerve_layer/nerve_region)
# barcode 还原：substring(spot_id, nchar(orig.ident)+2)  # 去掉 sample_id_ 前缀
```

## 10. 下游子分析

| 分析 | Skill |
|---|---|
| COMMOT 空间通讯 | `tool-commot` |
| MISTy 多视图 | `tool-misty` |
| niche/vicinity 详参 | `tool-spatial-niche` |
| CellChat / NicheNet | `tool-cellchat` / `tool-nichenet` |

## 常见坑

1. **Seurat 5 分层取数**：merged 对象 Spatial counts 按 `counts.<sample_id>` 分层，必须 `LayerData(layer=...)` 指定
2. **RCTD 稀有型**：每型 <25 细胞导致 create.RCTD 崩溃，先剔除并记录审计表
3. **下划线 assay**：`CreateAssayObject` 会把 `_` 换成 `-`，RCTD 亚型名含下划线必须手工 `new("Assay")`
4. **niche 是层次聚类**不是 KMeans（ward.D2 + cutree k=12）；KMeans 仅用于侵袭二分类
5. **vicinity 半径是图跳数**（BFS 层）而非欧氏微米
