---
slug: pseudotime-trajectory-viz
displayName: 伪时间轨迹可视化工具
version: 1.1.0
description: 对单细胞 RNA-seq 数据进行拟时序（pseudotime）分析，可视化细胞从干细胞向成熟细胞分化的发育轨迹。支持扩散拟时序（Diffusion Pseudotime, DPT）和 PAGA 两种轨迹推断方法，并可绘制指定基因沿轨迹的表达趋势。以下场景也会触发本技能："帮我做一下这个单细胞数据的拟时序分析""画一下这批细胞的分化轨迹图""看看这几个基因沿着分化轨迹是怎么变化的""用 PAGA 方法分析一下这个数据的细胞谱系"。
license: MIT
author: AIPOCH
---

# 伪时间轨迹可视化工具

对单细胞 RNA-seq 数据进行拟时序分析，可视化细胞从干细胞向成熟细胞分化的发育轨迹。

## 适用场景

- 从单细胞 RNA-seq 数据推断细胞分化的发育轨迹
- 计算拟时序（pseudotime）数值，表示细胞分化进程
- 可视化轨迹图、细胞簇分布与谱系分配
- 查看指定基因沿拟时序的表达变化趋势

## 依赖环境

```text
pip install -r requirements.txt
```

`requirements.txt` 内容：

```text
scanpy>=1.9.0
anndata>=0.8.0
matplotlib>=3.5.0
seaborn>=0.12.0
numpy>=1.21.0
pandas>=1.3.0
scipy>=1.7.0
scikit-learn>=1.0.0
igraph>=0.10.0
leidenalg>=0.9.0
```

> **文档修正说明**：源版本文档记录了 `scvelo`、`palantir`、`rpy2`（用于调用 R 的 `slingshot`）等一系列依赖，声称本技能支持 RNA 速度分析（RNA velocity）、Palantir 软谱系分配、Slingshot 主曲线法等多种轨迹推断方式。经核对实际脚本，这些方法均**不存在**——脚本只实现了 `diffusion`（基于 `scanpy` 的 DPT）和 `paga` 两种方法，且不涉及任何 RNA 速度相关分析（不读取 `spliced`/`unspliced` layer）。上述依赖和方法说明已从文档中移除。另外，脚本在自动计算 Leiden 聚类时依赖 `igraph`/`leidenalg`，但源版本 `requirements.txt` 未包含它们，运行时会因缺少依赖直接报错——本次本地化已补充这两个包。

## 命令行用法

```bash
# 基础轨迹分析（从 AnnData 文件开始）
python scripts/main.py --input data.h5ad --output ./results

# 指定起始细胞类型和轨迹推断方法
python scripts/main.py --input data.h5ad --start-cell-type progenitor --method diffusion --output ./results

# 绘制指定基因沿轨迹的表达趋势
python scripts/main.py --input data.h5ad --genes SOX2,OCT4,NANOG --plot-genes --output ./results

# 使用 PAGA 方法，并自定义分析参数
python scripts/main.py --input data.h5ad \
    --embedding umap \
    --method paga \
    --start-cell-type progenitor \
    --n-lineages 3 \
    --genes MARKER1,MARKER2,MARKER3 \
    --output ./results \
    --format pdf
```

## 参数

| 参数 | 类型 | 默认值 | 说明 |
|-----------|------|---------|-------------|
| `--input` / `-i` | path | 必填 | 输入 AnnData（.h5ad）文件路径 |
| `--output` / `-o` | path | ./trajectory_output | 结果输出目录 |
| `--embedding` | enum | umap | 用于可视化的 embedding：`umap`、`tsne`、`pca`、`diffmap` |
| `--method` | enum | diffusion | 轨迹推断方法：`diffusion`、`paga`（**不支持** `slingshot`、`palantir`） |
| `--start-cell` | string | 无 | 作为轨迹起点的根细胞（root cell）ID |
| `--start-cell-type` | string | 无 | 用作起点的细胞类型注释 |
| `--n-lineages` | int | 自动 | 预期的谱系分支数量 |
| `--cluster-key` | string | leiden | AnnData obs 中细胞聚类所在的字段名 |
| `--cell-type-key` | string | cell_type | AnnData obs 中细胞类型注释所在的字段名 |
| `--genes` | string | 无 | 需绘制表达趋势的基因名（英文逗号分隔） |
| `--plot-genes` | flag | false | 生成沿轨迹的基因表达热图 |
| `--plot-branch` | flag | true | 保留参数，当前脚本逻辑中**未实际使用**（见下方"已知问题"） |
| `--format` | enum | png | 输出图像格式：`png`、`pdf`、`svg` |
| `--dpi` | int | 300 | 图像分辨率 |
| `--n-pcs` | int | 30 | 分析所用主成分数量 |
| `--n-neighbors` | int | 15 | 构建邻接图时使用的邻居数量 |
| `--diffmap-components` | int | 5 | 扩散图（diffusion map）成分数量 |

> **说明**：`--embedding pca` 依赖 `adata.obsm['X_pca']` 字段，该字段通常需要预先运行 `sc.tl.pca()` 生成；如果输入数据没有预先计算好 PCA，脚本不会自动补算，后续绘图步骤会因缺少该字段而报错。建议在预处理阶段先运行 `sc.tl.pca(adata)`。

## 输入格式

需要一个 AnnData（.h5ad）文件，建议已完成标准化和 log 变换：

```
AnnData object with n_obs × n_vars = n_cells × n_genes
    obs: 'leiden', 'cell_type'  # 聚类与细胞类型注释（缺失时脚本会自动计算聚类）
    var: 'highly_variable'       # 高变基因标记（缺失时脚本会自动计算）
    obsm: 'X_umap', 'X_pca'      # 预计算的 embedding（可选，缺失部分 embedding 会自动计算）
```

## 输出文件

```
输出目录/
├── trajectory_plot.{格式}            # 主轨迹可视化图（拟时序/细胞簇/谱系/分布，四联图）
├── paga_graph.{格式}                 # PAGA 连通图（仅 --method paga 时生成）
├── gene_expression_heatmap.{格式}    # 基因表达热图（指定 --genes 或 --plot-genes 时生成）
├── gene_trends/
│   ├── {基因名}_trend.{格式}         # 单个基因的表达趋势图
│   └── ...
├── pseudotime_values.csv             # 逐细胞的拟时序数值、聚类与谱系分配
├── analysis_report.json              # 分析参数与统计摘要
└── trajectory_data.h5ad              # 附带分析结果的 AnnData 对象
```

> **文档修正说明**：源版本文档还声称会输出 `pseudotime_distribution.{format}`、`lineage_tree.{format}`、`lineage_assignments.csv` 三个文件，经核对实际脚本，这三个文件**均不会生成**——拟时序分布图已合并进 `trajectory_plot` 的第四个子图，谱系分配结果已合并进 `pseudotime_values.csv` 的 `lineage` 列，脚本中不存在独立的谱系树绘图或单独的谱系分配 CSV 导出逻辑。上述内容已从文档中移除。

## 方法说明

### 扩散拟时序（Diffusion Pseudotime, DPT）
- 基于 `scanpy` 的扩散图（diffusion map）计算细胞间的非线性关系
- 对噪声和数据规模有较好的鲁棒性
- 默认方法

### PAGA（Partition-based Graph Abstraction，基于分区的图抽象）
- 基于细胞簇间转录组相似性构建连通图
- 提供粗粒度的轨迹概览
- 计算速度快，适合大数据集

> 谱系分配（`assign_lineages()`）目前是一种简化的启发式方法：只是把拟时序取值范围 `[0, 1]` 按谱系数量等分成若干区间，再按细胞的拟时序值落入哪个区间来打标签，并不基于真正的分支拓扑结构（如 PAGA 连通图或扩散图上的分叉点）。对于存在多个真实分支、且不同分支在相近拟时序值上都有细胞的轨迹，这种分箱方式可能会把它们错误地划入同一谱系。如需更严谨的谱系推断，需要结合额外的分析工具，本脚本不提供该能力。

## 已知问题

- `--plot-branch` 参数会被 argparse 解析，但在脚本主流程中从未被读取或使用，是遗留的无效参数，传入与否都不影响实际输出。
- 使用 `--method paga` 时，PAGA 图的绘制已改为并排展示"PAGA 连通图"与"embedding 按簇着色图"两个子图；源脚本设计中原本还会尝试用 `sc.pl.paga_compare()` 叠加一张对比图，但该函数会自建双子图且不接受外部传入 `ax` 参数，与脚本的子图布局冲突会直接报错，本次修复已将其移除，改为更简单可靠的双图布局。
- `compute_paga_trajectory()` 中原本还有一段调用 `sc.tl.draw_graph(adata, init_pos=args.embedding)` 的死代码：`init_pos` 期望的是 `'paga'`、布尔值或某个真实存在的 `.obsm` 键（如 `'X_umap'`），而不是裸的 embedding 名字字符串（如 `'umap'`）；传入字符串会被当作真值处理，走入需要先调用 `sc.pl.paga()` 生成 `adata.uns['paga']['pos']` 的分支，若未先绘图会直接报错，且其计算结果在后续代码中也从未被使用。本次修复已将这段代码整体移除。

## 局限性

- 需要有较好细胞类型覆盖度的高质量单细胞数据
- 假设细胞分化是数据变异的主要来源
- 罕见的中间过渡状态（细胞数很少）可能无法被很好地捕捉
- 环状或周期性的生物学过程不适合用线性拟时序表示
- 不支持 RNA 速度（RNA velocity）分析

## 安全与最佳实践

- 建议结合已知的标记基因和生物学知识对轨迹结果进行验证
- 对于关键分析，建议同时尝试 diffusion 和 paga 两种方法互相印证
- 批次效应（batch effect）应在轨迹推断之前先做校正
- 细胞周期效应可能会混淆真实的分化轨迹信号
- 不要把拟时序数值直接当作绝对时间来解读

## 示例工作流

```python
# 使用 scanpy 预处理数据（在使用本工具之前完成）
import scanpy as sc

adata = sc.read_h5ad('raw_data.h5ad')
sc.pp.normalize_total(adata)
sc.pp.log1p(adata)
sc.pp.highly_variable_genes(adata, n_top_genes=2000)
sc.pp.scale(adata)
sc.tl.pca(adata)
sc.pp.neighbors(adata)
sc.tl.umap(adata)
sc.tl.leiden(adata)
adata.write('data.h5ad')

# 然后运行本技能：
# python scripts/main.py --input data.h5ad --start-cell-type progenitor
```

## 参考文献

- Haghverdi et al. (2016) — 扩散拟时序（Diffusion pseudotime）
- Wolf et al. (2019) — PAGA

> 源版本文档中还列出了 Street et al. (2018)（Slingshot）、Setty et al. (2019)（Palantir）、La Manno et al. (2018)（RNA velocity）三篇参考文献，由于脚本并不实现这些方法，已从参考文献列表中移除，避免误导。

## 快速检查

```bash
python -m py_compile scripts/main.py
python scripts/main.py --help
```

## 参考资料

- `references/runtime_checklist.md` —— 执行前的最小验证清单

## 错误处理

- 如果必需输入缺失，明确说明具体缺少哪些字段，只索取最少的补充信息。
- 如果任务超出文档化的范围，应停止执行，而不是猜测或擅自扩大任务范围。
- 如果 `scripts/main.py` 执行失败，报告失败发生的具体位置，总结哪些部分仍可安全完成，并提供人工回退方案。
- 不得编造文件、引用、数据、检索结果或执行结果。

## 输入校验

本技能接受与 `pseudotime-trajectory-viz` 文档化用途相符、且包含足够上下文以安全完成工作流的请求。

当请求超出范围、缺少关键输入，或需要引入未经确认的假设时，不要继续执行工作流，应回复：

> `pseudotime-trajectory-viz` 只处理其文档化的工作流。请补充缺失的必需输入，或改用更合适的工具。

## 回复模板

对于非简单请求，使用以下固定结构：

1. 目标
2. 收到的输入
3. 假设
4. 处理方式
5. 交付物
6. 风险与限制
7. 下一步核查事项

如果请求较为简单，可以精简结构，但仍需在影响正确性时明确说明假设和限制。
