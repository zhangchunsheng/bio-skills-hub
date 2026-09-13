# 网络药理学方法参考 (Network Pharmacology Reference)

## 1. 核心概念

### "网络靶点"假说 (Network Target Hypothesis)
- 药物不是作用于单一靶点，而是作用于一个**疾病模块（Disease Module）** 内的多个靶点
- 替代处方必须在关键模块上的"扰动向量"与原药方向一致
- **量化判据**: cosine 相似度 ≥ 0.7 或 Jaccard ≥ 0.5

### 多层网络架构
```
[药物成分] → [蛋白靶点] → [信号通路] → [生物过程] → [疾病表型]
```

---

## 2. 靶点预测数据库

### 反向对接 / 靶点预测工具

| 工具 | URL | 描述 | 输入格式 |
| :--- | :--- | :--- | :--- |
| SwissTargetPrediction | swisstargetprediction.ch | 基于 2D/3D 相似性的靶点预测 | SMILES |
| SEA (Similarity Ensemble Approach) | sea.bkslab.org | 基于化学相似性的靶点关联 | SMILES |
| STITCH | stitch.embl.de | 化合物-蛋白互作数据库 | SMILES/名称 |
| SuperPred | prediction.charite.de | 基于靶点的药物-疾病关联 | SMILES |
| PharmMapper | lilab-ecust.cn/pharmmapper | 药效团匹配反向对接 | MOL2/SDF |

### 工作流程
1. 将化合物转为规范 SMILES（用 RDKit / Open Babel）
2. 提交至 SwissTargetPrediction 获取 Top 15 预测靶点（Probability > 0.1 保留）
3. 用 UniProt ID 标准化靶点符号
4. 交叉验证靶点命中（至少两个工具共同预测到的保留）

---

## 3. 疾病靶点 / 表型数据库

| 数据库 | URL | 用途 |
| :--- | :--- | :--- |
| DisGeNET | disgenet.org | 基因-疾病关联（含证据评分） |
| OMIM | omim.org | 孟德尔疾病基因 |
| GeneCards | genecards.org | 综合基因注释 |
| TTD (Therapeutic Target Database) | db.idrblab.net/ttd | 已知药物靶点 |
| DrugBank | drugbank.com | 已上市药物靶点信息 |

---

## 4. 通路富集分析

### 常用通路数据库

| 数据库 | URL | 特点 |
| :--- | :--- | :--- |
| KEGG Pathway | genome.jp/kegg/pathway | 最常用，覆盖代谢与信号通路 |
| Reactome | reactome.org | 最详细的人类通路注释 |
| WikiPathways | wikipathways.org | 社区维护，更新快 |
| GO (Gene Ontology) | geneontology.org | 三类：BP/CC/MF |

### Fisher 精确检验 / 超几何检验公式
```
p = 1 − Σᵢ₌₀ᵏ⁻¹ C(N, i) · C(M − N, n − i) / C(M, n)

N: 通路 i 中注释基因数
M: 背景基因组大小（人类 ~20000）
n: 输入靶点基因数
k: 输入靶点中命中通路 i 的基因数
```

### 多重检验校正
- **Bonferroni**: p_corrected = p · m（过保守）
- **FDR (BH 法)**: 推荐，q < 0.05 为显著富集
- **推荐指标**: p < 0.05 且 FDR < 0.2

---

## 5. MCODE 聚类分析

### 原理
基于图的密度聚类，识别 PPI 网络中的功能模块（Clusters）。
- **K-Core 原理**: 每个节点至少有 K 个邻居在同一个子图里
- **Fluff 参数**: 允许一定比例的模糊外围节点
- **Haircut**: 剪掉度为 1 的节点

### 输出解读

| 输出项 | 含义 |
| :--- | :--- |
| Cluster Score | 密度 × 规模，越高越好 |
| Nodes / Edges | 模块节点数与内部连边数 |
| Top GO Term | 模块最显著富集的 GO BP |
| Hub Genes | Degree ≥ 10 的节点（模块核心） |

### 应用
- 原处方靶点的 MCODE 聚类 vs 替代处方靶点的 MCODE 聚类
- 若 Top 3 聚类模块的 GO Term 重叠 ≥ 60%，认为功能模块层面等效

---

## 6. 网络扰动相似性度量

### Jaccard 相似度（靶点层面）
```
J(A, B) = |T_A ∩ T_B| / |T_A ∪ T_B|
```
- J ≥ 0.5: 强重叠
- 0.3 ≤ J < 0.5: 中度重叠
- J < 0.3: 弱重叠，需额外论证

### Cosine 相似度（通路层面）
用通路富集的 −log10(p) 向量计算 cosine 相似度：
```
cos(θ) = Σ(v_A,i · v_B,i) / (||v_A|| · ||v_B||)
```
- cos(θ) ≥ 0.7: 通路扰动方向一致

### 置换检验显著性
- 随机采样 1000 次同样大小的靶点集
- 计算随机 Jaccard 分布
- 实际 Jaccard > 95% 随机值 → 显著

---

## 7. PPI 网络属性指标

| 指标 | 公式/定义 | 解读 |
| :--- | :--- | :--- |
| Degree | 节点连接数 | Hub ≥ 10 |
| Betweenness Centrality | 经过该节点的最短路径比例 | 瓶颈靶点 |
| Closeness Centrality | 1 / 到所有节点的平均最短路径 | 信息扩散的枢纽 |
| Modularity Q | 社区结构强度 | Q > 0.3 有强模块性 |
| Network Diameter | 最长最短路径长度 | 小世界 < 6 |

---

## 8. 常见信号通路与制剂等效性关系

| 信号通路 | 在制剂替代中的角色 | 扰动方向要求 |
| :--- | :--- | :--- |
| PI3K/AKT | 抗凋亡、细胞存活 | 同时激活（炎症）或抑制（肿瘤）保持方向 |
| MAPK/ERK | 细胞增殖、分化 | 保持原药的调节方向 |
| NF-κB | 炎症、免疫 | 抗炎制剂必须抑制其活性 |
| TGF-β | 纤维化、免疫抑制 | 抗纤维化需抑制共信号 |
| Nrf2/HO-1 | 氧化应激防御 | 抗氧化制剂需激活该通路 |
| Wnt/β-catenin | 干细胞更新、组织修复 | 方向取决于疾病 |
| JAK/STAT | 免疫响应 | 免疫抑制剂需抑制 STAT3/STAT5 |

### 替代处方评价标准
> 若替代处方在 Top 5 显著富集通路上的调节方向与原处方完全一致，且额外的富集通路不包含已知促癌/促炎/促纤维化风险通路，则初步判断为"功能等效"。
