# 批次校正方法比较

## 概述

在整合来自多个实验、供体或测序批次的数据时，批次校正至关重要。本指南比较了适用于单细胞 RNA-seq 数据的各种方法。

## 方法比较

| 方法 | 最适用于 | Seurat | Scanpy | 速度 | 准确性 |
|--------|----------|--------|--------|-------|----------|
| **Harmony** | 小批次（<5），变异简单 | ✅ | ✅ | 快 | 高 |
| **RPCA** | 大型数据集，多个批次 | ✅ | ❌ | 中 | 非常高 |
| **CCA** | 复杂变异，不同组织 | ✅ | ❌ | 慢 | 非常高 |
| **Scanorama** | 跨平台整合 | ✅ | ✅ | 快 | 高 |
| **scVI** | 深度学习方法，大数据 | ✅ | ✅ | 慢 | 非常高 |
| **BBKNN** | 基于图的快速替代方案 | ✅ | ✅ | 非常快 | 中 |
| **ComBat** | 简单线性校正 | ❌ | ✅ | 快 | 中 |

## 按场景给出的建议

### 小型研究（<5 个批次）
```
Recommended: Harmony
Reason: Fast, accurate, preserves biological variation
```

### 大型研究（>10 个批次）
```
Recommended: RPCA (Seurat) or scVI (Scanpy)
Reason: Scalable, handles complex batch structures
```

### 跨平台整合
```
Recommended: Scanorama or scVI
Reason: Designed for platform-specific technical effects
```

### 不同组织/条件
```
Recommended: CCA or scVI
Reason: Preserves cell type differences while removing technical effects
```

### 快速探索
```
Recommended: BBKNN
Reason: Fastest method, good for initial analysis
```

## 整合后的质量控制

1. **可视化检查**：按批次查看 UMAP
2. **kBET**：量化每种细胞类型的批次混合程度
3. **LISI**：局部逆辛普森指数（Local Inverse Simpson's Index）
4. **轮廓系数（Silhouette score）**：聚类紧密度
5. **标志基因保留情况**：检查已知标志基因是否仍能识别细胞类型

## 代码示例

### Seurat - Harmony
```r
library(harmony)
seurat_obj <- RunHarmony(seurat_obj, group.by.vars = "batch")
seurat_obj <- RunUMAP(seurat_obj, reduction = "harmony", dims = 1:30)
```

### Seurat - RPCA
```r
seurat_list <- SplitObject(seurat_obj, split.by = "batch")
seurat_list <- lapply(seurat_list, NormalizeData)
seurat_list <- lapply(seurat_list, FindVariableFeatures)
features <- SelectIntegrationFeatures(seurat_list)
seurat_list <- lapply(seurat_list, ScaleData)
seurat_list <- lapply(seurat_list, RunPCA, features = features)
anchors <- FindIntegrationAnchors(seurat_list, reduction = "rpca")
seurat_integrated <- IntegrateData(anchorset = anchors)
```

### Scanpy - Harmony
```python
import scanpy.external as sce
sce.pp.harmony_integrate(adata, key='batch')
adata.obsm['X_pca'] = adata.obsm['X_pca_harmony']
```

### Scanpy - scVI
```python
import scvi
scvi.model.SCVI.setup_anndata(adata, batch_key='batch')
vae = scvi.model.SCVI(adata, n_layers=2, n_latent=30)
vae.train()
adata.obsm["X_scVI"] = vae.get_latent_representation()
sc.pp.neighbors(adata, use_rep="X_scVI")
```

## 常见陷阱

1. **过度校正**：在去除批次效应的同时也去除了生物学信号
   - 解决方案：比较校正前后的标志基因表达

2. **校正不足**：批次仍然分离
   - 解决方案：尝试更强的方法（scVI、CCA）

3. **混杂因素**：批次与条件相关联
   - 解决方案：使用能够对条件建模的方法（scVI）

4. **细胞类型比例不均**：不同批次间比例差异较大
   - 解决方案：在整合前对丰富的细胞类型进行下采样

## 参考文献

- Harmony: Korsunsky et al. (2019) Nature Methods
- RPCA: Stuart & Butler et al. (2019) Cell
- Scanorama: Hie et al. (2019) Nature Biotechnology
- scVI: Lopez et al. (2018) Nature Methods
