# QSAR 毒性预测参考 (QSAR & Toxicity Prediction Reference)

## 1. T.E.S.T. (Toxicity Estimation Software Tool)

**来源**: EPA (US Environmental Protection Agency)
**URL**: epa.gov/chemical-research/toxicity-estimation-software-tool-test

### 预测模型方法

| 方法 | 原理 | 推荐场景 |
| :--- | :--- | :--- |
| Hierarchical Method | 基于 fragmental 层次聚类 | 优先推荐，中低通量 |
| FDA Method | 基于最相似化合物加权平均 | 高通量筛选 |
| Neural Network | 三层前馈神经网 | 非线性格局 |
| Group Contribution | 分子片段加和法 | 结构简单的分子 |
| Consensus Method | 上述四种模型平均 | 最准确（推荐使用） |

### 预测终点 (Endpoints)

| 终点 | 输出类型 | 单位/类别 | 用途 |
| :--- | :--- | :--- | :--- |
| Oral Rat LD50 | 连续值 | mg/kg | 急性毒性分级 |
| Developmental Toxicity | 二分类 | toxic / non-toxic | 发育毒性筛查 |
| Ames Mutagenicity | 二分类 | positive / negative | 基因突变风险 |
| Fathead Minnow LC50 | 连续值 | mg/L | 生态毒性 |
| Bioaccumulation Factor | 连续值 | log BCF | 累积风险 |
| Estrogen Receptor RBA | 连续值 | log RBA | 内分泌干扰 |

### 急性毒性分级 (GHS Category based on LD50)

| 级别 | 口服 LD50 (mg/kg) | 描述 |
| :--- | :--- | :--- |
| Category 1 | ≤ 5 | 剧毒 |
| Category 2 | 5 < LD50 ≤ 50 | 高毒 |
| Category 3 | 50 < LD50 ≤ 300 | 中等毒性 |
| Category 4 | 300 < LD50 ≤ 2000 | 低毒 |
| Category 5 | 2000 < LD50 ≤ 5000 | 微毒 |
| Unclassified | > 5000 | 实际无毒 |

---

## 2. ProTox-II

**URL**: tox.charite.de/protox_II

### 预测内容

| 类别 | 具体项目 |
| :--- | :--- |
| **肝毒性 (Hepatotoxicity)** | 药物诱导肝损伤概率 |
| **细胞毒性 (Cytotoxicity)** | 化合物破坏细胞膜完整性概率 |
| **致癌性 (Carcinogenicity)** | 长期暴露致癌风险 |
| **致突变性 (Mutagenicity)** | Ames 试验结果预测 |
| **免疫毒性 (Immunotoxicity)** | 免疫响应的激活/抑制 |
| **不良结局通路 (AOP)** | 相关的分子起始事件 (MIE) |

### 输出解读

| 指标 | 范围 | 解读 |
| :--- | :--- | :--- |
| Probability Score | 0-1 | ≥ 0.7 为高置信度预测 |
| Average Similarity | 0-1 | 训练集中相似化合物的平均相似度 |
| Confidence Level | Low / Medium / High | 基于片段覆盖率 |

---

## 3. ADMETlab / ADMETSAR 2.0

**URL**: admetmesh.scbdd.com

### 补充预测维度

| 终点 | 输出 | 用途 |
| :--- | :--- | :--- |
| hERG 阻断 | 二分类 + pIC50 | 心脏毒性风险 |
| CYP 抑制 | 1A2/2C9/2C19/2D6/3A4 | 药物相互作用（DDI）风险 |
| P-gp 底物判断 | 二分类 | 肠吸收/脑屏障外排 |
| PPB (血浆蛋白结合率) | % bound | 游离药物浓度预判 |
| BBB (血脑屏障) | 二分类 + 概率 | CNS 暴露 |

### 关键阈值

| 参数 | 安全区间 | 警戒区间 |
| :--- | :--- | :--- |
| hERG pIC50 | ≤ 5.0 | ≥ 5.5 (高风险) |
| CYP 抑制概率 | ≤ 0.3 | ≥ 0.7 (高风险) |
| P-gp 底物概率 | — | ≥ 0.8 (可能的吸收限制) |

---

## 4. 替代物毒性评估标准操作规程 (SOP)

### Step 1: 输入准备
将候选替代物的 SMILES 标准化（RDKit: `MolFromSmiles` → `MolToSmiles(canonical=True)`）。

### Step 2: T.E.S.T. Consensus 预测
获取 LD50 + Ames + DevTox 的 Consensus 值。记录每个预测值的 95% 置信区间。

### Step 3: ProTox-II 复核
获取肝毒性、细胞毒性、致癌性概率。Probability > 0.7 且训练集相似度 > 0.4 → 高风险。

### Step 4: ADMETlab hERG + CYP + DDI
评估心脏毒性与代谢相互作用风险。hERG pIC50 ≥ 5.5 或 CYP 抑制 ≥ 3 个同工酶 → 高风险。

### Step 5: 综合风险评级

| 评级 | 条件 | 行动 |
| :--- | :--- | :--- |
| **安全 (Safe)** | LD50 > 2000, Ames 阴性, 肝毒性 < 0.5 | 可推进 Phase 5 优化 |
| **需关注 (Caution)** | 任一预测指标为中等风险 | 标注关注项，推进但需湿实验验证 |
| **高风险 (High Risk)** | LD50 < 300 或 Ames 阳性或肝毒性 > 0.7 | 直接替换候选，不推进 |

---

## 5. 定量构效关系 (QSAR) 基本原则

### OECD 验证原则
1. **明确的预测终点** —— 必须知道在预测什么毒理学终点
2. **明确、无歧义的算法** —— 模型透明可复现
3. **定义应用域 (AD)** —— 仅在化学相似空间内使用
4. **适当的拟合优度** —— R² > 0.6（训练集），Q² > 0.5（交叉验证）
5. **机械论解释** —— 如有必要，提供结构-活性关系解释

### 应用域预警 (Applicability Domain)
- 使用 Tanimoto 相似度评估查询分子与训练集的距离
- Tanimoto to nearest neighbor < 0.3 → 在应用域外，预测不可靠
- 标注: "预测值在 QSAR 应用域外，仅作参考"

---

## 6. 替代物毒性对比矩阵格式

| 项目 | 原成分 / API | 替代候选 A | 替代候选 B | 备注 |
| :--- | :--- | :--- | :--- | :--- |
| **Oral LD50 (mg/kg)** | 120 | 2300 | 1850 | B 与 A 均显著优于原成分 |
| **Ames 致突变性** | Positive | Negative | Negative | A/B 均消除了致突变风险 |
| **肝毒性概率** | 0.85 | 0.32 | 0.45 | A 肝毒性风险最低 |
| **hERG pIC50** | 4.2 | 4.8 | 5.6 | B 有心脏毒性风险 |
| **CYP Inhibition Count** | 3 | 1 | 2 | A 的 DDI 风险最低 |
| **综合评级** | **高风险** | **安全** | **需关注** | — |
