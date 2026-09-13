---
slug: spatial-transcriptomics-mapper
displayName: 空间转录组图谱绘制工具
version: 1.1.0
description: 将 10x Genomics Visium/Xenium 空间转录组数据投射到组织切片图像上，绘制基因表达空间分布图，支持单基因/多基因可视化和空间聚类分析。触发短语："空间转录组分析""Visium 数据可视化""基因表达空间分布""Xenium 分析"。
license: MIT
author: AIPOCH
---

# 空间转录组图谱绘制工具

将 10x Genomics Visium 或 Xenium 空间转录组数据投射到组织切片图像上，绘制基因表达的空间分布图。

## 快速检查

```bash
python -m py_compile scripts/main.py
python scripts/main.py --help
```

## 适用场景

- 空间转录组数据可视化
- 基因表达空间分布分析
- 空间聚类结果展示
- 肿瘤微环境空间异质性研究
- 组织形态学特征关联分析

## 核心功能

### 1. Visium 数据处理

支持 10x Genomics Space Ranger 输出：
- 基因表达矩阵（filtered_feature_bc_matrix.h5）
- Spot 空间坐标（tissue_positions_list.csv）
- H&E 染色组织图像（tissue_lowres_image.png）
- 缩放因子（scalefactors_json.json）

### 2. Xenium 数据处理

支持 10x Genomics Xenium Explorer 输出：
- 单细胞基因表达矩阵（cell_feature_matrix.h5）
- 转录本空间坐标（transcripts.parquet）
- 细胞核/细胞边界（nucleus_boundaries.parquet）
- 形态学图像（morphology_focus.ome.tif）

### 3. 基因表达映射

将指定基因的表达量投射到组织图像上：
- 单基因热图
- 多基因叠加图
- 表达梯度可视化

### 4. 空间聚类可视化

展示 Seurat/Scanpy 聚类结果的空间分布。

## 使用方法

### 基础用法 - Visium

```bash
# 单基因可视化
python scripts/main.py \
  --platform visium \
  --data-dir /path/to/spaceranger/outs/ \
  --gene PIK3CA \
  --output ./output/

# 多基因分析
python scripts/main.py \
  --platform visium \
  --data-dir /path/to/data/ \
  --genes PIK3CA,PTEN,EGFR \
  --mode overlay \
  --output ./output/

# 聚类结果可视化
python scripts/main.py \
  --platform visium \
  --data-dir /path/to/data/ \
  --cluster-file ./clusters.csv \
  --output ./output/
```

### 基础用法 - Xenium

```bash
# Xenium 单基因
python scripts/main.py \
  --platform xenium \
  --data-dir /path/to/xenium/outs/ \
  --gene PIK3CA \
  --output ./output/

# Xenium 多基因（亚细胞分辨率）
python scripts/main.py \
  --platform xenium \
  --data-dir /path/to/xenium/outs/ \
  --genes SFTPB,SFTPC,SCGB1A1 \
  --dpi 600 \
  --output ./output/
```

## 命令参数

| 参数 | 类型 | 默认值 | 必需 | 说明 |
|------|------|--------|------|------|
| `--platform` | str | — | 是 | 平台类型：visium 或 xenium |
| `--data-dir` | str | — | 是 | 数据目录路径 |
| `--gene` | str | — | 否 | 单个基因名称 |
| `--genes` | list | — | 否 | 多个基因，逗号分隔 |
| `--mode` | str | single | 否 | 模式：single/overlay/multi |
| `--cluster-file` | str | — | 否 | 聚类结果 CSV 文件路径 |
| `--output` | str | ./output | 否 | 输出目录 |
| `--dpi` | int | 300 | 否 | 输出图像 DPI |
| `--cmap` | str | viridis | 否 | 颜色映射方案 |
| `--spot-size` | float | 1.0 | 否 | Visium spot 大小因子 |
| `--alpha` | float | 0.8 | 否 | 透明度（0-1）|
| `--min-count` | int | 0 | 否 | 最小表达量过滤 |
| `--crop` | str | — | 否 | 裁剪区域（x1,y1,x2,y2）|

## 输入文件结构

### Visium（Space Ranger 输出）

```
outs/
├── filtered_feature_bc_matrix.h5    # 基因表达矩阵
├── raw_feature_bc_matrix.h5         # 原始计数（可选）
├── spatial/
│   ├── tissue_positions_list.csv    # Spot 位置
│   ├── tissue_lowres_image.png      # 低分辨率 H&E 图像
│   ├── tissue_hires_image.png       # 高分辨率 H&E 图像
│   └── scalefactors_json.json       # 缩放因子
└── web_summary.html
```

### Xenium

```
outs/
├── cell_feature_matrix.h5           # 细胞 × 基因矩阵
├── transcripts.parquet              # 转录本坐标
├── nucleus_boundaries.parquet       # 细胞核边界
├── cell_boundaries.parquet          # 细胞边界
├── morphology_focus.ome.tif         # 形态学图像
└── experiment.xenium
```

## 输出文件

- `{gene}_spatial_map.png` — 单基因空间表达图
- `{gene}_heatmap.png` — 基因表达热图
- `multi_gene_overlay.png` — 多基因叠加图（如使用 --mode overlay）
- `cluster_spatial_map.png` — 聚类空间分布图
- `combined_report.html` — 综合 HTML 报告

## 使用示例

### 示例 1：单基因可视化

```bash
python scripts/main.py \
  --platform visium \
  --data-dir ./visium_sample/outs/ \
  --gene EPCAM \
  --cmap Reds \
  --output ./results/
```

输出：EPCAM 基因在组织切片上的空间表达分布。

### 示例 2：肿瘤标记物组合

```bash
python scripts/main.py \
  --platform visium \
  --data-dir ./breast_cancer/outs/ \
  --genes PIK3CA,ERBB2,ESR1,PGR \
  --mode multi \
  --cmap plasma \
  --output ./tumor_markers/
```

输出：四个乳腺癌标记物的空间表达图（分格显示）。

### 示例 3：Xenium 亚细胞分辨率

```bash
python scripts/main.py \
  --platform xenium \
  --data-dir ./xenium_lung/outs/ \
  --genes SFTPB,SFTPC,SCGB1A1 \
  --dpi 600 \
  --output ./xenium_results/
```

输出：肺组织特异性标记物的单细胞分辨率空间分布。

### 示例 4：空间聚类可视化

```bash
python scripts/main.py \
  --platform visium \
  --data-dir ./sample/outs/ \
  --cluster-file ./seurat_clusters.csv \
  --output ./clusters/
```

输出：Seurat 聚类结果在组织空间的分布图。

## Python API 调用

```python
from scripts.main import SpatialMapper

# 初始化
mapper = SpatialMapper(
    platform="visium",
    data_dir="/path/to/data",
    output_dir="./output"
)

# 加载数据
mapper.load_data()

# 绘制单基因图
mapper.plot_gene_spatial(
    gene="PIK3CA",
    cmap="viridis",
    save_path="./output/pik3ca.png"
)

# 绘制多基因图
mapper.plot_multi_genes(
    genes=["PIK3CA", "PTEN", "EGFR"],
    mode="grid",
    save_path="./output/multi.png"
)

# 获取空间统计
stats = mapper.get_spatial_stats(gene="PIK3CA")
print(f"平均表达量: {stats['mean']}")
print(f"空间自相关系数: {stats['morans_i']}")
```

## 颜色映射方案

| 色板名称 | 适用场景 |
|---------|---------|
| viridis | 通用，色盲友好 |
| plasma | 高对比度，适合发表 |
| Reds/Blues/Greens | 单色渐变 |
| coolwarm | 双向变化（上调/下调）|
| RdYlBu | 分组对比 |

完整色板参考：https://matplotlib.org/stable/tutorials/colors/colormaps.html

## 空间统计分析

### Moran's I 空间自相关

评估基因表达的空间聚集模式：
- Moran's I > 0：空间聚集（相似表达倾向聚集）
- Moran's I ≈ 0：随机分布
- Moran's I < 0：空间离散（不同表达倾向相邻）

```python
from scripts.main import SpatialMapper

mapper = SpatialMapper(platform="visium", data_dir="./data")
mapper.load_data()

stats = mapper.calculate_spatial_autocorrelation(gene="PIK3CA")
print(f"Moran's I: {stats['morans_i']}")
print(f"P-value: {stats['p_value']}")
```

## 最佳实践

1. **数据质量检查**：使用 Space Ranger/Xenium Explorer 的 QC 报告确认数据质量
2. **基因选择**：优先可视化中高表达基因（避免噪声）
3. **颜色方案**：为发表选择色盲友好色板（viridis、cividis）
4. **分辨率设置**：
   - 屏幕预览：dpi=150
   - 发表质量：dpi=300-600
   - 海报打印：dpi=600
5. **大数据集处理**：使用 --crop 参数聚焦感兴趣区域

## 常见问题

**Q: Visium 和 Xenium 的主要区别？**  
A: Visium 空间分辨率约 55μm（每个 spot 包含多个细胞），Xenium 达到单细胞/亚细胞分辨率。

**Q: 如何处理大型 Xenium 数据集？**  
A: 使用 --crop 参数指定感兴趣区域，或使用 --downsample 降低分辨率。

**Q: 输出图像模糊怎么办？**  
A: 增加 --dpi 参数（例如 600），或使用高分辨率 H&E 图像（--hires 参数）。

**Q: 如何与 Seurat/Scanpy 结果整合？**  
A: 导出聚类结果为 CSV 格式（barcode, cluster），使用 --cluster-file 参数加载。

## 风险评估

| 风险指标 | 评估 | 级别 |
|---------|------|------|
| 代码执行 | Python 脚本本地执行 | 中 |
| 网络访问 | 无外部 API 调用 | 低 |
| 文件系统访问 | 读取输入，写入输出 | 中 |
| 指令篡改 | 标准提示指南 | 低 |
| 数据暴露 | 输出文件保存至工作区 | 低 |

## 先决条件

```bash
pip install -r requirements.txt
```

依赖包：
- scanpy
- squidpy
- matplotlib
- seaborn
- pillow
- numpy
- pandas
- h5py
- pyarrow（Xenium 数据）
- dask（可选，大数据集）

## 生命周期状态

- **当前阶段**：Draft
- **下次审查日期**：2026-03-06
- **已知问题**：无
- **计划改进**：
  - 支持更多空间转录组平台
  - 空间统计分析功能增强
  - 交互式可视化（Plotly）
  - 3D 重建支持

## 相关资源

- [10x Genomics Visium](https://www.10xgenomics.com/products/spatial-gene-expression)
- [10x Genomics Xenium](https://www.10xgenomics.com/platforms/xenium)
- [Scanpy 文档](https://scanpy.readthedocs.io/)
- [Squidpy 文档](https://squidpy.readthedocs.io/)
