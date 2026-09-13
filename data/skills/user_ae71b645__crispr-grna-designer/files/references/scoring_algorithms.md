# CRISPR 评分算法参考

## 概述

本文档总结了用于预测 gRNA 效率和特异性的主要算法。

## 在靶效率预测

### 1. Doench 等人 2014 年（Azimuth/Rule Set 2）

**发表文献**：Doench 等人，"Rational design of highly active sgRNAs for CRISPR-Cas9-mediated gene inactivation"，Nature Biotechnology 2014

**使用特征**：
- 位置特异性核苷酸偏好性（20 个位置）
- 向导 RNA 的熔解温度
- GC 含量
- 自身互补结构
- 位置依赖性二核苷酸特征

**性能**：与实验数据的皮尔逊相关系数约为 0.6

**实现说明**：
```python
score = intercept + sum(position_weights[i] * features[i])
```

### 2. Doench 等人 2016 年（Rule Set 3）

**改进点**：
- L2 正则化逻辑回归
- 在更大数据集上训练（n=2,389）
- 包含染色质可及性特征

**性能**：皮尔逊相关系数约为 0.71

### 3. DeepCRISPR

**发表文献**：Chuai 等人，"DeepCRISPR: optimized CRISPR guide RNA design by deep learning"，Genome Biology 2018

**架构**：
- 卷积神经网络（CNN）
- 混合输入：序列 + 表观遗传特征
- 5 个卷积层 + 2 个全连接层

**特征**：
- 独热编码序列（20bp）
- 染色质可及性（DNase-seq）
- 组蛋白修饰（H3K4me3、H3K27ac）

**性能**：AUROC 约为 0.86

### 4. CRISPRon

**发表文献**：Hsu 等人，"CRISPRon: a logistic regression model for predicting gRNA activity"

**关键创新**：考虑染色质状态和 DNA 可及性

**输入特征**：
- 向导序列（20mer + PAM）
- 染色质可及性（ATAC-seq/DNase-seq）
- DNA 甲基化水平

### 5. Elevation（微软研究院）

**发表文献**：Listgarten 等人，"Prediction of off-target activities for the end-to-end design of CRISPR guide RNAs"

**两阶段模型**：
1. **Elevation-AGG**：预测所有向导的活性
2. **Elevation-CFD**：预测脱靶效应

## 脱靶预测

### 1. CFD（切割频率决定系数）

**方法**：量化每个错配位置对切割频率的影响

**关键发现**：PAM 附近（种子区）的错配影响更大

**计算方式**：
```
CFD_score = product(mismatch_penalties[position])
```

**位置权重**：
- 第 18-20 位（PAM 近端）：高惩罚（每个错配 0.1-0.2）
- 第 1-12 位（PAM 远端）：低惩罚（每个错配 0.5-0.8）

### 2. MIT 评分

**发表文献**：Hsu 等人，"DNA targeting specificity of RNA-guided Cas9 nucleases"，Nature Biotechnology 2013

**公式**：
```
score = 1 / (1 + exp(-(intercept + sum(mismatch_scores))))
```

**局限性**：未考虑染色质背景

### 3. CCTop

**发表文献**：Stemmer 等人，"CCTop: An intuitive, flexible and reliable CRISPR/Cas9 target prediction tool"

**特征**：
- 错配位置权重
- 种子区强调（第 12-20 位）
- 凸起 RNA/DNA 处理

### 4. CRISPOR

**发表文献**：Concordet & Haeussler，"CRISPOR: intuitive guide selection for CRISPR/Cas9 genome editing experiments and screens"

**集成内容**：
- 多种效率评分（Doench '16、Moreno-Mateos 等）
- 结合基因组比对的脱靶预测
- 常见 SNP 注释

## 对比表

| 算法 | 类型 | 相关性 | 速度 | 染色质 | 最佳适用场景 |
|-----------|------|-------------|-------|-----------|----------|
| Doench '14 | 线性 | 0.60 | 快 | 否 | 快速筛选 |
| Doench '16 | 逻辑回归 | 0.71 | 快 | 否 | 通用 |
| DeepCRISPR | CNN | 0.86 | 慢 | 是 | 高精度 |
| CRISPRon | 逻辑回归 | 0.75 | 中 | 是 | 细胞特异性 |
| Azimuth | 回归 | 0.72 | 快 | 否 | Python 流程 |

## 位置特异性评分矩阵

### 核苷酸偏好性（Doench '16）

| 位置 | G | A | C | T |
|----------|---|---|---|---|
| 20（PAM 近端） | +0.20 | -0.10 | -0.05 | -0.05 |
| 19 | +0.10 | -0.05 | +0.15 | -0.10 |
| 18 | +0.15 | -0.05 | +0.05 | -0.05 |
| 1-17 | 参见完整矩阵 | | | |

### 错配惩罚（CFD）

| 位置 | 权重 |
|----------|--------|
| 20 | 0.10 |
| 19 | 0.15 |
| 18 | 0.20 |
| 17 | 0.25 |
| 16 | 0.30 |
| 15-13 | 0.40 |
| 12-1 | 0.60 |

## 建议

1. **筛选阶段**：使用 Doench '16 追求速度
2. **验证阶段**：对候选靠前的向导使用 DeepCRISPR
3. **脱靶评估**：始终使用 CFD 或 CCTop 评分
4. **细胞特异性**：在可用时纳入染色质数据

## 参考文献

1. Doench JG et al. (2014) Nature Biotechnology 32:1262-1267
2. Doench JG et al. (2016) Nature Biotechnology 34:184-191
3. Chuai G et al. (2018) Genome Biology 19:80
4. Hsu PD et al. (2013) Nature Biotechnology 31:827-832
5. Listgarten J et al. (2018) Nature Biomedical Engineering 2:38-47
