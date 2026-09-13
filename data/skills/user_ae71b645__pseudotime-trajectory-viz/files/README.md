# 伪时间轨迹可视化工具（Pseudotime Trajectory Visualization）

可视化单细胞发育轨迹，展示细胞从干细胞向成熟细胞分化的过程。

## 快速开始

```bash
# 安装依赖
pip install -r requirements.txt

# 运行分析
python scripts/main.py --input data.h5ad --output ./results

# 指定具体参数
python scripts/main.py \
    --input data.h5ad \
    --start-cell-type Stem \
    --method diffusion \
    --genes SOX2,NANOG,POU5F1 \
    --plot-genes \
    --output ./results
```

> **修正说明**：原文档在此处提到 `python examples/generate_example_data.py example_data.h5ad` 这一步，用于生成示例数据；但仓库中并不存在 `examples/` 目录或该脚本，已在本次改写中移除。若需要示例数据，请参考下方"输入数据格式"一节，用 scanpy 自行准备一个符合要求的 `.h5ad` 文件。

## 功能特性

- **扩散拟时序（Diffusion Pseudotime, DPT）**：基于扩散图的稳健轨迹推断方法
- **PAGA**：基于分区的图抽象（Partition-based Graph Abstraction），用于轨迹可视化
- **基因表达趋势**：追踪标记基因沿拟时序的表达变化
- **谱系分配**：自动或用户指定的谱系分支划分（简化启发式方法，非真实分支拓扑推断，详见 `SKILL.md` 中的说明）
- **发表级图像**：支持多种格式的高分辨率图像输出

> **修正说明**：原文档没有提及本工具实际只支持 `diffusion` 和 `paga` 两种方法（`--method` 参数），不支持 Slingshot、Palantir 或 RNA velocity 分析；这些方法在源文档其他章节中被提及，但脚本本身并未实现，已在 `SKILL.md` 中详细说明。

## 输出文件

```
results/
├── trajectory_plot.png           # 主轨迹可视化图
├── paga_graph.png                # PAGA 连通图（仅 method=paga 时生成）
├── gene_expression_heatmap.png   # 基因表达动态热图
├── gene_trends/
│   ├── SOX2_trend.png           # 单个基因的表达趋势图
│   └── ...
├── pseudotime_values.csv         # 细胞级拟时序数据
├── analysis_report.json          # 分析元数据
└── trajectory_data.h5ad          # 更新后的 AnnData 对象
```

## 输入数据格式

本工具需要一个已预处理的 AnnData（.h5ad）文件：

```python
import scanpy as sc

# 加载数据
adata = sc.read_h5ad('your_data.h5ad')

# 所需的注释字段：
# - adata.obs['leiden'] 或其他聚类标签
# - adata.obs['cell_type']（可选，用于根细胞检测）

# 预处理步骤（如尚未完成）：
sc.pp.normalize_total(adata)
sc.pp.log1p(adata)
sc.pp.highly_variable_genes(adata, n_top_genes=2000)
sc.tl.pca(adata)
sc.pp.neighbors(adata)
sc.tl.umap(adata)
sc.tl.leiden(adata)

# 保存以供分析使用
adata.write('preprocessed_data.h5ad')
```

## 命令行参数

```
--input, -i              输入 AnnData 文件路径（必填）
--output, -o             输出目录（默认：./trajectory_output）
--embedding              可视化所用 embedding：umap、tsne、pca、diffmap（默认：umap）
--method                 轨迹推断方法：diffusion、paga（默认：diffusion）
--start-cell             轨迹起点的根细胞 ID
--start-cell-type        作为起点的细胞类型
--n-lineages             预期的谱系分支数量
--cluster-key            聚类字段列名（默认：leiden）
--cell-type-key          细胞类型字段列名（默认：cell_type）
--genes                  需绘图的基因名（英文逗号分隔）
--plot-genes             生成基因表达图
--format                 输出格式：png、pdf、svg（默认：png）
--dpi                    图像分辨率（默认：300）
```

## 示例

### 基础用法
```bash
python scripts/main.py --input data.h5ad --output ./results
```

### 指定根细胞类型
```bash
python scripts/main.py \
    --input data.h5ad \
    --start-cell-type "Progenitor" \
    --output ./results
```

### 可视化标记基因
```bash
python scripts/main.py \
    --input data.h5ad \
    --genes SOX2,OCT4,NANOG,NESTIN \
    --plot-genes \
    --output ./results
```

### 使用 PAGA 方法
```bash
python scripts/main.py \
    --input data.h5ad \
    --method paga \
    --embedding umap \
    --output ./results
```

### 生成 PDF 图像
```bash
python scripts/main.py \
    --input data.h5ad \
    --format pdf \
    --dpi 600 \
    --output ./results
```

## 故障排查

**问题**："未检测到根细胞"
**解决方法**：显式指定 `--start-cell` 或 `--start-cell-type`

**问题**：处理大型数据集时内存不足
**解决方法**：对细胞抽样，或增加系统内存

**问题**：轨迹结果与生物学认知不符
**解决方法**：检查根细胞的选择是否合理，并尝试不同的推断方法

## 参考文献

- Haghverdi et al. (2016) - Diffusion pseudotime robustly reconstructs lineage branching
- Wolf et al. (2019) - PAGA: graph abstraction reconciles clustering with trajectory inference

## 许可证

MIT License
