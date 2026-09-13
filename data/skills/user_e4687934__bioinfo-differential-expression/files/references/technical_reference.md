# 差异表达分析 - 技术参考

## 设计公式说明

DESeq2 的设计公式（design formula）决定了哪些因素会被纳入模型。

### 常用设计公式

| 实验设计 | design_factors | 说明 |
|---------|---------------|------|
| 两组比较（无 batch） | `["condition"]` | 最简单的情况 |
| 两组比较 + batch 校正 | `["condition", "batch"]` | 最常见，推荐 |
| 三组比较 | `["condition"]` | condition 列有 3 个 level |
| 配对设计 | `["patient", "condition"]` | patient 为配对因子 |

### Contrast 写法

```python
# 两组比较
contrast=("condition", "treated", "control")

# 三组中两两比较
contrast=("condition", "groupA", "groupB")

# 截距对比（所有组 vs 参考组）
contrast=["condition", "treated", "control"]
```

## 混杂因素检测

**什么是混杂？** 当两个因素完全重叠时，无法区分各自效应。

示例：如果所有 control 样本都在 batch=1，所有 treated 样本都在 batch=2，
那么 batch 和 condition 完全混杂。

### 检测方法

```python
import pandas as pd

# 交叉表检查
ct = pd.crosstab(metadata_df["condition"], metadata_df["batch"])
print(ct)

# 如果某行或某列为 0，说明存在混杂
```

### 解决方案

- 重新安排实验（最佳方案）
- 如果轻度混杂，在结果解读时注明局限性
- 如果完全混杂，无法校正，结果不可靠

## 标准化方法对比

| 方法 | 适用场景 | 输出 |
|------|---------|------|
| **DESeq2 内置**（size factor） | 差异分析建模 | 模型内部使用 |
| **rlog / vst** | 可视化（PCA、热图） | log2 转换后的矩阵 |
| **TPM / FPKM** | 仅用于展示，**不能用于 DE** | 不适合 count-based DE |

```python
# vst 标准化（用于 PCA）
vst = dds.vst()
vst_df = pd.DataFrame(vst, index=dds.var_names, columns=dds.obs_names)
```

## 多重检验校正方法

| 方法 | 说明 | 推荐度 |
|------|------|--------|
| **BH (FDR)** | DESeq2 默认，控制错误发现率 | ⭐⭐⭐⭐⭐ |
| Bonferroni | 极其严格，假阴性高 | 仅用于少量检验 |
| BY | 考虑依赖性，比 BH 略严格 | 特殊场景 |
| IHW | 加权 FDR，利用协变量 | 高级用法 |

## 效应量 vs 显著性

| 情况 | 判断 | 建议 |
|------|------|------|
| padj < 0.05 且 \|log2FC\| >= 1 | 真正的差异基因 | 报告 |
| padj < 0.05 但 \|log2FC\| < 0.5 | 统计显著但效应小 | 谨慎报告，可能无生物学意义 |
| padj > 0.1 但 \|log2FC\| > 3 | 效应大但样本量不足 | 提示可能需要增加样本量 |

## 低 count 基因过滤

DESeq2 内部会自动处理低 count 基因，但可以手动预过滤加速：

```python
# 保留至少在 N 个样本中 count >= 10 的基因
keep = (counts_df >= 10).sum(axis=1) >= 3
counts_filtered = counts_df[keep]
```
