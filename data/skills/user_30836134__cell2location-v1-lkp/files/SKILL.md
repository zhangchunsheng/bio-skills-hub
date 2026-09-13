---
name: "解卷积-cell2location-HDdata"
description: "使用Cell2location对Visium HD空间转录组数据进行细胞类型反卷积分析，支持16µm、Cellbin等多种分辨率。当用户需要对Visium HD数据进行Cell2location反卷积、生成发表级空间分布图、或处理Cellbin单细胞分辨率数据时调用。"
author: LKP <kunpeng.liao@abiosciences.com>
date:   2026-08-18
platform: github
source: https://github.com/BayraktarLab/cell2location
tags: [cell2location, deconvolution, spatial-transcriptomics, Visium-HD, scRNA-seq, Python, scanpy, pyro-ppl, 16um, cellbin]
version: 1.0.0
generated: 2026-08-18T00:00:00+08:00
---

# Cell2location — 空间转录组反卷积（Visium HD）

## 概述

**Cell2location** 是基于深度学习（Pyro + PyTorch）的空间转录组反卷积方法，使用贝叶斯神经网络从空间数据中估计细胞类型丰度。本 Skill 针对 Visium HD（16µm 和 Cellbin 单细胞分辨率）进行了完整流程优化。

核心特性：
- **多分辨率支持**：Visium HD 16µm 与 Cellbin（单细胞分辨率）
- **贝叶斯深度学习**：使用 Pyro + PyTorch，输出后验分布
- **发表级可视化**：类似 RCTD 风格的综合热图、气泡图、对比图、统计图
- **Cellbin 真实坐标**：从 `cell_segmentations.geojson` 提取细胞中心
- **批量脚本化**：从训练到可视化的完整工具链

---

## 适用场景

当用户需要执行以下任务时使用此 Skill：

- 使用 Cell2location 对 Visium HD 数据进行反卷积
- 在 16µm 和 Cellbin 分辨率间比较
- 处理 cellbin 单细胞分辨率数据（含真实坐标提取与匹配）
- 生成类似 RCTD 的全套空间分布图

---

## 安装

参考 [references/安装指南.md](references/安装指南.md)。

### 环境要求

- **Python**: >= 3.8
- **GPU**: 推荐 NVIDIA GPU（>=8 GB 显存）
- **操作系统**: Linux (推荐), Windows, macOS

### 创建虚拟环境

```bash
python -m venv cell2loc_env
source cell2loc_env/bin/activate  # Linux/Mac
# 或 Windows:
cell2loc_env\Scripts\activate
```

### 安装 cell2location

```bash
pip install cell2location
# 安装 PyTorch（CUDA 版，按你的 CUDA 版本选择）
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### 安装其他依赖

```bash
pip install scanpy anndata pandas numpy matplotlib seaborn pyro-ppl
```

---

## 输入数据要求

| 数据 | 格式 | 说明 |
|---|---|---|
| scRNA-seq 表达矩阵 | AnnData (.h5ad) / 10X mtx | 行=基因，列=细胞；`obs` 中需包含细胞类型注释列 |
| 空间表达数据（16µm） | 10X h5 格式 | `binned_outputs/square_016um/` |
| 空间表达数据（Cellbin） | 10X h5 格式 | `segmented_outputs/filtered_feature_cell_matrix.h5` |
| Cellbin 真实坐标（可选） | geojson | `segmented_outputs/cell_segmentations.geojson` |

---

## 配置说明

所有脚本顶部都包含**统一配置区域**：

```python
# ========== 配置区域（请根据实际数据修改） ==========
USER_DATA_DIR      = "your/data/directory"        # 数据根目录
SC_FILENAME        = "scRNA.h5ad"                  # 单细胞 h5ad 文件名
SPATIAL_SUBDIR     = "binned_outputs/square_016um" # 空间数据子目录
SEGMENTED_SUBDIR   = "segmented_outputs"           # segmented_outputs 子目录
CELL_TYPE_COL      = "cell_type"                   # scRNA-seq obs 中细胞类型列名
OUTPUT_DIR         = "cell2location_16um_results"  # 输出目录
# =====================================================
```

### 路径兼容性

- **Windows**：`USER_DATA_DIR = "D:/your/data/dir"`
- **WSL/Linux**：`USER_DATA_DIR = "/mnt/d/your/data/dir"` 或 `"/home/user/data"`
- **macOS**：`USER_DATA_DIR = "/Users/yourname/data"`

---

## 完整脚本列表

| 脚本 | 说明 |
|---|---|
| [scripts/cell2location_visium_hd_16um.py](scripts/cell2location_visium_hd_16um.py) | Cell2location 16µm 完整反卷积：训练 RegressionModel + Cell2location + 提取结果 + 可视化 |
| [scripts/cell2location_visium_hd_cellbin.py](scripts/cell2location_visium_hd_cellbin.py) | Cell2location Cellbin 完整反卷积（含真实坐标提取与匹配） |
| [scripts/cell2location_generate_all_plots.py](scripts/cell2location_generate_all_plots.py) | 全套可视化（前 N 种细胞类型热图、综合图、气泡图、对比图、统计图） |
| [scripts/extract_cell2location_results.py](scripts/extract_cell2location_results.py) | 从训练好的 Cell2location 模型中提取结果（无需重新训练） |
| [scripts/extract_cellbin_coords.py](scripts/extract_cellbin_coords.py) | Cellbin 坐标辅助工具：extract（geojson→CSV）+ match（合并反卷积结果与坐标） |

---

## 推荐工作流

### 16µm 分辨率

```bash
# 1. 完整反卷积（训练 + 提取 + 基础可视化）
python scripts/cell2location_visium_hd_16um.py

# 2. 重新生成全套发表级可视化
python scripts/cell2location_generate_all_plots.py
```

### Cellbin 单细胞分辨率

```bash
# 1. 提取 Cellbin 真实坐标
python scripts/extract_cellbin_coords.py extract \
    --geojson data/segmented_outputs/cell_segmentations.geojson \
    --output cellbin_coordinates.csv

# 2. 完整反卷积（含真实坐标匹配）
python scripts/cell2location_visium_hd_cellbin.py

# 3. 合并反卷积结果与真实坐标
python scripts/extract_cellbin_coords.py match \
    --results cell2location_cellbin_results/proportions.csv \
    --coords cellbin_coordinates.csv \
    --output cellbin_merged.csv
```

### 已训练模型（仅提取与可视化）

```bash
python scripts/extract_cell2location_results.py
python scripts/cell2location_generate_all_plots.py
```

---

## 输出文件清单

### 数据文件
- `cell2location_16um_results/sp.h5ad`：带反卷积结果的 AnnData
- `cell2location_16um_results/proportions.csv`：细胞类型比例
- `cell2location_cellbin_results/sp.h5ad`：Cellbin 反卷积结果
- `cellbin_coordinates.csv`：从 geojson 提取的细胞中心
- `cellbin_merged.csv`：反卷积结果与坐标的合并

### 图形文件
- `cell_top_cell_types.png/pdf`：前 N 种细胞类型空间分布
- `cell_dominant_cell_types.png/pdf`：主导细胞类型空间分布
- `cell_all_cell_types.png/pdf`：所有细胞类型综合热图
- `cell_heatmap_*.png/pdf`：单细胞类型热图
- `cell_all_cell_types_bubble.png/pdf`：气泡图
- `cell_mean_proportions.png/pdf`：平均比例条形图
- `cell_cell_type_correlation.png/pdf`：相关性热图

---

## 故障排除

参考 [references/故障排除.md](references/故障排除.md)。常见问题：

- **GPU/CUDA 不匹配**：重新安装与 CUDA 版本匹配的 PyTorch
- **内存不足**：减小训练批次，使用 `use_gpu=False` 切换到 CPU
- **基因数不匹配**：确保 scRNA-seq 与空间数据的基因名一致
- **Cellbin 坐标为空**：检查 `cell_segmentations.geojson` 是否存在，使用 `extract_cellbin_coords.py` 提取

---

## 资源链接

- **Cell2location 源码**：[github.com/BayraktarLab/cell2location](https://github.com/BayraktarLab/cell2location)
- **论文**：Kleshchevnikov V, et al. *Cell2location maps fine-grained cell types in spatial transcriptomics.* Nature Biotechnology, 2022.

---

## 许可证

遵循原作者的开源许可证（详见 GitHub 仓库）。
