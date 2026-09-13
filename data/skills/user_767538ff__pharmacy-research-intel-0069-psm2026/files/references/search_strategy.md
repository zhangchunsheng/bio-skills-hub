# 检索策略构建与去重

本文件指导如何为您（医院药学教授）构建高查全/查准的检索式，并在多源结果中去重。

## 1. 通用流程

1. 用 PICO 拆题（见 `evidence_grading.md`）。
2. 将每个维度映射到**主题词 + 自由词**组合。
3. 英文优先用 **MeSH**（PubMed），中文用 **主题词/关键词**（CNKI）。
4. 用布尔逻辑（AND/OR/NOT）与各字段标签组装。
5. 加**限定过滤器**（文献类型、日期、 Humans、语种）。
6. 多源检索后**去重合并**。

## 2. PubMed 检索式写法

- 字段标签：`[Title/Abstract]`、`[MeSH]`、`[Author]`、`[Journal]`、`[Affiliation]`。
- 日期过滤：`&datetype=pdat&mindate=2025/01&maxdate=2026/08`（由脚本支持）。
- 文献类型：`"Randomized Controlled Trial"[Publication Type]`、`"Review"[Publication Type]`、`"Meta-Analysis"[Publication Type]`。
- 示例（抗肿瘤药物个体化治疗 + 药物基因组学）：
  ```
  ("Antineoplastic Agents"[MeSH] OR "antineoplastic"[Title/Abstract])
  AND ("Precision Medicine"[MeSH] OR "personalized"[Title/Abstract] OR "pharmacogenomics"[Title/Abstract])
  AND "Humans"[MeSH]
  AND ("Randomized Controlled Trial"[Publication Type] OR "Clinical Trial"[Publication Type])
  ```
- 可直接传给 `scripts/pubmed_search.py --query "..."`。

## 3. CNKI 检索式写法

- 用主题/关键词/篇关摘字段，布尔同 PubMed。
- 示例：`SU='抗肿瘤药物' AND SU='个体化用药' AND SU='药物基因组学'`。
- 高级检索页更易操作；WebSearch 时可用 `site:cnki.net "关键词1" "关键词2"`。

## 4. 查全 vs 查准的平衡

- 追踪第一线（速递）：偏查准，近期 + 高相关 + 高质量期刊。
- 综述/立项：偏查全，放宽类型、加同义词、跨库（PubMed + CNKI + Cochrane）。
- 记录所用检索式，保证可复现（写进产出报告的"方法"小节）。

## 5. 去重与合并

- 跨源结果以 **DOI** 为主键去重；无 DOI 用（标题归一化 + 第一作者 + 年）。
- 保留最完整记录（优先有摘要/全文的源）。
- 去重后按相关度或时效性排序呈现。

## 6. 检索式迭代

- 初检后看命中文献的 MeSH / 关键词，反补同义词。
- 用"滚雪球"：从高质量综述的参考文献与被引文献拓展。
- 每次调整记录版本，便于向用户说明查全率变化。
