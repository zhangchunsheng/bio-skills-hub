---
name: bioinfo-differential-expression
description: >
  RNA-seq 差异表达分析全流程助手。基于 PyDESeq2 进行 count-aware 建模，
  自动完成设计矩阵验证、差异分析、火山图/MA图/PCA图绘制、结果表格导出。
  当用户提及 差异表达、DEG、DESeq2、RNA-seq差异分析、差异基因筛选、
  count矩阵分析、bulk RNA-seq 时触发。
license: MIT
metadata:
  author: yunge-ai-shengxin
  version: 1.0.0
  tags: [bioinformatics, rna-seq, differential-expression, deseq2, pydeseq2]
  original_author: Bioclaw_Skills_Hub (zongtingwei)
  modification: 中文化 + 可视化增强 + 中文触发词 + 国内环境适配
---

# RNA-seq 差异表达分析全流程助手

## 版本兼容

参考代码基于以下版本：

- `pydeseq2` 0.4+
- `pandas` 2.2+
- `numpy` 1.26+
- `matplotlib` 3.8+

使用前验证环境：

```bash
python -c "import pydeseq2, pandas; print(pydeseq2.__version__, pandas.__version__)"
```

如未安装：
```bash
pip install pydeseq2 pandas numpy matplotlib scipy
```

国内加速源：
```bash
pip install pydeseq2 pandas numpy matplotlib scipy -i https://pypi.tuna.tsinghua.edu.cn/simple
```

## 功能说明

基于 PyDESeq2（DESeq2 的 Python 实现），对 bulk RNA-seq 原始 count 矩阵进行
差异表达分析，自动完成：设计矩阵验证 → 模型拟合 → 显著性筛选 → 可视化出图 →
结果导出。输出可直接用于论文或投稿。

## 适用场景

- 有 raw count 矩阵（基因×样本）和样本元数据表
- 需要比较两组或多组之间的基因表达差异
- 条件对照、处理组 vs 对照组、不同基因型等比较
- 存在批次效应或配对设计需要校正

## 快速判断

| 重复数 | 建议 |
|--------|------|
| 每组 1 个重复 | 不建议做正式差异分析，结果不可靠 |
| 每组 2 个重复 | 可以做，但结论需保守解读 |
| 每组 ≥3 个重复 | 标准分析流程，结果可信 |

## 输入要求

### 必需输入

| 输入 | 格式 | 说明 |
|------|------|------|
| **count 矩阵** | CSV/TSV，行为基因，列为样本 | 必须是原始整数 count，不能是 TPM 或 FPKM |
| **样本元数据** | CSV/TSV | 必须包含分组列（如 condition） |

### count 矩阵示例（counts.csv）

| gene | sample_1 | sample_2 | sample_3 | sample_4 | sample_5 | sample_6 |
|------|-----------|-----------|-----------|-----------|-----------|-----------|
| ACTB | 1234 | 1156 | 1302 | 980 | 1050 | 1100 |
| IL6 | 45 | 52 | 38 | 890 | 920 | 870 |
| ... | ... | ... | ... | ... | ... | ... |

### 样本元数据示例（metadata.csv）

| sample | condition | batch |
|--------|-----------|-------|
| sample_1 | control | B1 |
| sample_2 | control | B1 |
| sample_3 | control | B2 |
| sample_4 | treated | B1 |
| sample_5 | treated | B2 |
| sample_6 | treated | B2 |

## 执行步骤

### Step 1：验证设计矩阵

在拟合模型前，必须检查：

- [ ] 每组至少 2 个重复
- [ ] 分组因子是否正确（condition 列的 level 名称）
- [ ] 批次效应是否均衡（每个 batch 里各组的样本数是否相近）
- [ ] 是否存在混杂因素（某组和某 batch 完全重叠 = 混杂，无法区分效应）
- [ ] 配对样本是否正确标注（如需要）

如果存在混杂因素，**必须警告用户**并建议重新设计实验。

### Step 2：拟合 count-aware 模型

```python
from pydeseq2.dds import DeseqDataSet
from pydeseq2.ds import DeseqStats

# 读取数据（自动检测分隔符）
import pandas as pd
counts_df = pd.read_csv("counts.csv", index_col=0)
metadata_df = pd.read_csv("metadata.csv", index_col=0)

# 构建 DESeq2 数据集
dds = DeseqDataSet(
    counts=counts_df,
    metadata=metadata_df,
    design_factors=["condition", "batch"],  # 根据实际设计调整
)
dds.deseq2()

# 定义比较（treated vs control）
stats = DeseqStats(dds, contrast=("condition", "treated", "control"))
stats.summary()
res = stats.results_df.sort_values("padj")
```

**重要**：必须使用 raw count，不能用 TPM / FPKM / log 转换后的值。

### Step 3：筛选显著差异基因

```python
# 默认阈值：padj < 0.05 且 |log2FC| >= 1
sig = res[(res["padj"] < 0.05) & (res["log2FoldChange"].abs() >= 1)]

# 导出完整结果
res.to_csv("results/de_results.tsv", sep="\t")

# 导出显著差异基因
sig.to_csv("results/de_significant.tsv", sep="\t")

# 导出排名基因列表（用于后续富集分析）
res.sort_values("stat", ascending=False).to_csv("results/de_ranked_genes.tsv", sep="\t")
```

用户可通过自然语言指定阈值：
- "padj 阈值用 0.01"
- "log2FC 阈值用 1.5"
- "不用校正，直接用 pvalue < 0.05"

### Step 4：绘制可视化图表

至少绘制以下三张图：

**图 1：样本 PCA 图**
```python
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt

# 使用 DESeq2 标准化后的 count
norm_counts = np.log1p(dds.obsm["design_matrix"] @ dds.varm["disp"])  # 或用 rlog/vst
pca = PCA(n_components=2)
coords = pca.fit_transform(norm_counts.T)

fig, ax = plt.subplots(figsize=(8, 6))
for cond in metadata_df["condition"].unique():
    mask = metadata_df["condition"] == cond
    ax.scatter(coords[mask, 0], coords[mask, 1], label=cond, s=80, alpha=0.7)
ax.set_xlabel(f"PC1 ({pca.explained_variance_ratio_[0]*100:.1f}%)")
ax.set_ylabel(f"PC2 ({pca.explained_variance_ratio_[1]*100:.1f}%)")
ax.legend()
ax.set_title("Sample PCA")
plt.savefig("figures/sample_pca.pdf", bbox_inches="tight")
```

**图 2：火山图（Volcano Plot）**
```python
fig, ax = plt.subplots(figsize=(8, 6))
ax.scatter(res["log2FoldChange"], -np.log10(res["padj"]),
           c="#cccccc", s=10, alpha=0.5)
sig_up = res[(res["padj"] < 0.05) & (res["log2FoldChange"] >= 1)]
sig_dn = res[(res["padj"] < 0.05) & (res["log2FoldChange"] <= -1)]
ax.scatter(sig_up["log2FoldChange"], -np.log10(sig_up["padj"]), c="#e74c3c", s=15, label="Up")
ax.scatter(sig_dn["log2FoldChange"], -np.log10(sig_dn["padj"]), c="#2980b9", s=15, label="Down")
ax.axhline(-np.log10(0.05), color="gray", linestyle="--", linewidth=0.8)
ax.axvline(-1, color="gray", linestyle="--", linewidth=0.8)
ax.axvline(1, color="gray", linestyle="--", linewidth=0.8)
ax.set_xlabel("log2 Fold Change")
ax.set_ylabel("-log10(adjusted P-value)")
ax.legend()
ax.set_title("Volcano Plot")
plt.savefig("figures/volcano.pdf", bbox_inches="tight")
```

**图 3：MA Plot**
```python
fig, ax = plt.subplots(figsize=(8, 6))
ax.scatter(res["baseMean"], res["log2FoldChange"], c="#cccccc", s=10, alpha=0.5)
sig = res[res["padj"] < 0.05]
ax.scatter(sig["baseMean"], sig["log2FoldChange"], c="#e74c3c", s=15)
ax.set_xscale("log")
ax.axhline(0, color="gray", linewidth=0.5)
ax.set_xlabel("Mean of normalized counts")
ax.set_ylabel("log2 Fold Change")
ax.set_title("MA Plot")
plt.savefig("figures/ma_plot.pdf", bbox_inches="tight")
```

### Step 5：导出通路分析就绪文件

生成排序基因列表，可直接用于：
- GO/KEGG 富集分析
- GSEA 基因集富集分析
- DAVID/clusterProfiler 等工具

```python
ranked = res.sort_values("stat", ascending=False)
ranked["gene"] = ranked.index
ranked[["gene", "stat"]].to_csv("results/ranked_genes_for_GSEA.tsv", sep="\t", header=False, index=False)
```

## 输出文件

```
results/
├── de_results.tsv           # 全部基因的完整结果
├── de_significant.tsv       # 显著差异基因（padj < 0.05 & |log2FC| >= 1）
├── de_ranked_genes.tsv      # 按统计量排序的基因列表
└── ranked_genes_for_GSEA.tsv # GSEA 格式（基因 + 统计量）
figures/
├── sample_pca.pdf           # 样本 PCA 图
├── volcano.pdf              # 火山图
└── ma_plot.pdf              # MA 图
```

## 结果解读模板

分析完成后，输出以下摘要：

```
=== 差异表达分析摘要 ===
数据集：X 个基因 × Y 个样本
比较组：treated vs control
模型：~ condition + batch

显著差异基因（padj < 0.05 & |log2FC| >= 1）：Z 个
  上调：A 个 | 下调：B 个

Top 5 上调基因：
  Gene1 (log2FC=+3.2, padj=1.2e-10)
  Gene2 (log2FC=+2.8, padj=5.6e-08)
  ...

Top 5 下调基因：
  Gene3 (log2FC=-3.5, padj=2.1e-12)
  Gene4 (log2FC=-2.9, padj=8.7e-09)
  ...
```

## 质量检查清单

分析完成后，逐项确认：

- [ ] 使用的是 raw count（非 TPM/FPKM/log 值）
- [ ] 没有完全混杂的因子（batch 和 condition 不完全重叠）
- [ ] 异常样本已检查并标注
- [ ] 最终表格包含 baseMean、log2FoldChange、pvalue、padj 四列
- [ ] PCA 图中同组样本聚类合理
- [ ] 火山图上调和下调基因数量在合理范围内

## 常见错误（避坑）

| 错误 | 后果 | 正确做法 |
|------|------|---------|
| 用 TPM 代替 raw count 做差异分析 | 结果不可靠 | 必须用原始整数 count |
| 忽略 batch 效应 | 假阳性增多 | 在 design 中加入 batch |
| 只展示显著基因，隐藏完整表 | 无法评估分析质量 | 同时导出全表和显著基因表 |
| 只看 pvalue 不看 log2FC | 选出大量差异很小但显著的基因 | 必须同时考虑效应量 |

## 相关技能

- [差异基因报告生成器](bioinfo-deg-report)：分析完成后自动生成可视化 HTML 报告
- [bulk-rna-expression]：RNA-seq 定量分析上游流程
- [pathway-analysis]：GO/KEGG 通路富集分析

## 致谢

原始技能来源：[Bioclaw_Skills_Hub](https://github.com/zongtingwei/Bioclaw_Skills_Hub)（MIT 协议）
本版本在原始基础上进行了中文化、可视化增强和国内环境适配。
