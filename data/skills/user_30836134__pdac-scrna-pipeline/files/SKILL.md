---
name: "pdac-scrna-pipeline"
description: "单细胞RNA-seq(sc+snRNA)全景复现工作流：预检→加载→Normalize/HVG/PCA→BBKNN批次整合→Louvain聚类→marker→盲打分注释→解盲验证→7 compartment亚群重聚类→下游子分析(Milo/TCR/CNV/SCENIC等)。Invoke when用户要跑单细胞全流程、复现大图谱注释流程、或询问各步参数。"
---

> **作者 (author)**: LKP <kunpeng.liao@abiosciences.com>
> **Skill 及脚本参数来源**: Chen et al., 2025, *Cancer Cell* 43, 1656–1676, <https://doi.org/10.1016/j.ccell.2025.06.020>


# PDAC 单细胞全景复现 Pipeline

适用于：GEO 发布的 scRNA+snRNA 混合大图谱（本例 231,189 细胞 = sc 199,184 + sn 32,005），从原始 matrix.mtx 到亚群注释冻结的全流程。

## 0. 全局约定

```r
# 项目根路径解析（环境变量 > 命令行参数 > getwd()）
Sys.setenv(PDAC_PROJECT_ROOT = "D:/项目根目录")
result_root <- file.path(Sys.getenv("PDAC_PROJECT_ROOT"), "复现分析结果")
set.seed(2023L)   # 全局种子，贯穿所有步骤
```

目录约定：`tables/`（表）、`objects/`（RDS 检查点）、`figures/`、`logs/`、`config/`。

检查点续算模式（强烈建议，大对象防中断）：

```r
# 断点续算：存在即读，不存在则计算并原子写（拒绝覆盖旧检查点）
load_or_compute <- function(stage, path, compute, compress = "gzip") {
  if (file.exists(path)) return(readRDS(path))
  obj <- force(compute())
  tmp <- paste0(path, ".tmp"); saveRDS(obj, tmp, compress = compress)
  file.rename(tmp, path); obj
}
```

## 1. 预检（preflight）

- 输入四件套：`matrix.mtx.gz / barcodes.tsv.gz / features.tsv.gz / metadata.csv`（sc、sn 各一套）
- 校验：基因数、细胞数、nnzero 与 GEO 说明一致；条码顺序 = 矩阵列顺序
- 输出：`tables/input_manifest.csv`（全部源文件 SHA256）、`tables/preflight_summary.csv`

## 2. 加载与盲化合并

```r
# 读 mtx（10x 三件套）
mat <- Seurat::ReadMtx(mtx, cells, features,
                       cell.column = 1L, feature.column = 2L, unique.features = TRUE)
# 元数据只取前 3 列（cell_id/tissue/patients），orig.ident 由条码正则派生
# 禁止读入作者标签列（保证盲法）
sobj <- Seurat::CreateSeuratObject(counts = mat, meta.data = blind_meta,
                                   min.cells = 0, min.features = 0)  # 输入已过滤，不再QC
# 多模态合并
merged <- Reduce(function(x, y) merge(x, y), seurat_list) |>
  SeuratObject::JoinLayers()
stopifnot(ncol(merged) == 231189)  # 细胞数不变量断言
```

## 3. 标准化 / HVG / 缩放 / PCA

```r
obj <- NormalizeData(obj, verbose = FALSE)                                  # 默认 LogNormalize, 1e4
obj <- FindVariableFeatures(obj, selection.method = "vst", nfeatures = 3000)
obj <- ScaleData(obj, features = VariableFeatures(obj))                    # 仅 3000 HVG
obj <- RunPCA(obj, features = VariableFeatures(obj), npcs = 30, seed.use = 2023)
```

## 4. 批次整合（BBKNN，非 Harmony）

```r
# 必须校验 bbknnR == 1.1.0（行为差异敏感）
stopifnot(as.character(packageVersion("bbknnR")) == "1.1.0")
obj <- bbknnR::RunBBKNN(obj, batch_key = "orig.ident", n_pcs = 30,
                        neighbors_within_batch = 3, run_UMAP = TRUE, seed = 2023)
# 直接生成 bbknn 图 + umap，跳过 FindNeighbors
```

稀疏批次处理：最小批次 <3 细胞 → `neighbors_within_batch` 降至 `min(3, min(table(batch)))`；最小批次 <2 → 合并为虚拟池 `__blind_sparse_batch_pool__`。

## 5. 主聚类与 marker

```r
graph_name <- grep("bbknn", names(obj@graphs), value = TRUE)[1]
obj <- FindClusters(obj, graph.name = graph_name, resolution = 1,
                    algorithm = 1, random.seed = 2023)  # Louvain
markers <- FindAllMarkers(obj, logfc.threshold = 0.25, min.pct = 0.25, densify = FALSE)
```

## 6. 盲打分注释（核心方法）

```r
# 簇级汇总：data 层稀疏矩阵 × one-hot 得平均表达与检出比例
# 打分 = 0.7 × z标准化平均表达均值 + 0.3 × 检出比例均值（仅统计表达矩阵中存在的marker）
scores <- score_marker_sets(avg_expr, pct_expr, marker_sets,
                            expression_weight = 0.7, detection_weight = 0.3)
# 赋标签：top分≥0 且领先第二名≥0.15，否则 "Ambiguous"
labels <- assign_blind_labels(scores, min_margin = 0.15, min_score = 0)
```

marker 配置表：`config/major_markers_paper.csv`，列 `level/compartment/label/gene/source`。

## 7. 解盲验证（预注册门槛）

```r
# 作者标签 vs 盲标签：accuracy/balanced_accuracy/macro_f1/cohen_kappa/混淆矩阵
# 门槛：macro_f1 >= 0.80，不达标终止下游
# 亚群匹配：marker top100 加权秩Jaccard + RBO(p=0.9) + Spearman(共享>=5基因)
composite_similarity <- mean(weighted_jaccard, RBO, (spearman + 1) / 2)
```

## 8. 亚群重聚类（7 compartment 各自重跑）

compartment：`CD4T, CD8T, B, Myeloid, CAF, Ductal, Schwann`。每个 compartment 重复 3-5 步全套（nfeatures=3000 / npcs=30 / bbknn / res=1），marker 与打分参数不变。输出 `objects/subcluster_checkpoints/<compartment>_blind_subcluster.rds` + 全部标签表，最后 SHA256 冻结（`logs/blind_freeze_sha256.csv`）。

## 9. 下游子分析（各自独立 skill）

| 分析 | Skill |
|---|---|
| Milo 差异丰度 | `tool-milo-da` |
| TCR 重建 + Startrac | `tool-tcr-startrac` |
| inferCNV 恶性判定 | `tool-cnvturbo-infercnv` |
| scMetabolism 代谢 | `tool-scmetabolism` |
| SCENIC 调控 | `tool-scenic` |
| CytoSig 细胞因子 | `tool-cytosig` |
| 基因程序打分 | `tool-gene-program` |
| GO 富集 | `tool-go-enrichment` |
| 组成/共现 | `tool-composition-cooccurrence` |

## 常见坑

1. **Seurat 5 分层**：merge 后必须 `JoinLayers()`，否则 FindAllMarkers 报错
2. **bbknnR 版本**：非 1.1.0 直接停，结果不可比
3. **Windows 大内存**：`future::plan("sequential")` + `future.globals.maxSize = Inf`，避免 fork 问题
4. **下划线基因名**：`CreateAssayObject` 会把 feature 名下划线静默替换为连字符，需要保留原名的 assay 用 `new(Class="Assay", ...)` 手工构建
