# 差异表达分析 - 命令与阈值参考

## PyDESeq2 完整示例代码

```python
from pydeseq2.dds import DeseqDataSet
from pydeseq2.ds import DeseqStats
import pandas as pd
import numpy as np
import os

# ========== 1. 读取数据 ==========
counts_df = pd.read_csv("counts.csv", index_col=0)
metadata_df = pd.read_csv("metadata.csv", index_col=0)

# 确保样本顺序一致
metadata_df = metadata_df.loc[counts_df.columns]

# 创建输出目录
os.makedirs("results", exist_ok=True)
os.makedirs("figures", exist_ok=True)

# ========== 2. 构建 DESeq2 数据集 ==========
dds = DeseqDataSet(
    counts=counts_df,
    metadata=metadata_df,
    design_factors=["condition", "batch"],  # 根据实际设计调整
)
dds.deseq2()

# ========== 3. 差异分析 ==========
stats = DeseqStats(dds, contrast=("condition", "treated", "control"))
stats.summary()
res = stats.results_df

# ========== 4. 筛选与导出 ==========
# 显著差异基因
sig = res[(res["padj"] < 0.05) & (res["log2FoldChange"].abs() >= 1)]

# 完整结果
res.to_csv("results/de_results.tsv", sep="\t")
sig.to_csv("results/de_significant.tsv", sep="\t")
res.sort_values("stat", ascending=False).to_csv("results/de_ranked_genes.tsv", sep="\t")

# GSEA 格式
ranked = res.sort_values("stat", ascending=False)
ranked.to_csv("results/ranked_genes_for_GSEA.tsv", sep="\t", columns=["stat"])

print(f"显著差异基因: {len(sig)} 个")
print(f"  上调: {(sig['log2FoldChange'] >= 1).sum()} 个")
print(f"  下调: {(sig['log2FoldChange'] <= -1).sum()} 个")
```

## 推荐阈值

| 参数 | 默认值 | 常用替代值 |
|------|--------|-----------|
| padj | < 0.05 | < 0.01（更严格）、< 0.1（更宽松） |
| \|log2FC\| | >= 1 | >= 0.5（更宽松）、>= 1.5/2（更严格） |
| 最小重复数 | >= 2 | >= 3（推荐） |

## 输出文件约定

```
results/
├── de_results.tsv           # 完整结果
├── de_significant.tsv       # 显著差异
├── de_ranked_genes.tsv      # 排序列表
└── ranked_genes_for_GSEA.tsv # GSEA格式
figures/
├── sample_pca.pdf
├── volcano.pdf
└── ma_plot.pdf
```

## 国内加速安装

```bash
pip install pydeseq2 pandas numpy matplotlib scipy -i https://pypi.tuna.tsinghua.edu.cn/simple
```
