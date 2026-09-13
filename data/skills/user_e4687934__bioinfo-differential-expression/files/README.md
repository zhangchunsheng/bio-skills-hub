# BioInfo Differential Expression Skill

RNA-seq 差异表达分析全流程助手，基于 PyDESeq2，支持中文自然语言触发。

## 功能

- 自动验证设计矩阵（batch 混杂检测、重复数检查）
- PyDESeq2 count-aware 建模
- 显著差异基因筛选（可自定义 padj / log2FC 阈值）
- 火山图 / MA 图 / PCA 图自动绘制
- GSEA 格式排名基因列表导出
- 结果解读摘要自动生成

## 使用

安装此 Skill 后，用自然语言触发：

- "帮我做差异表达分析，count矩阵是 counts.csv，样本信息是 metadata.csv"
- "RNA-seq 差异分析，比较 treated 和 control"
- "DEG 分析，padj 阈值用 0.01"
- "用 DESeq2 分析这批 RNA-seq 数据"

## 依赖

```bash
pip install pydeseq2 pandas numpy matplotlib scipy -i https://pypi.tuna.tsinghua.edu.cn/simple
```

## 致谢

基于 [Bioclaw_Skills_Hub](https://github.com/zongtingwei/Bioclaw_Skills_Hub)（MIT 协议）中文化 + 可视化增强版本。
