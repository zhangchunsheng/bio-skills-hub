# GeneLLM 方法学精读（完整公式与配置）

来源：Deng S, Sha L, Jin Y, et al. *Decoding cancer circulating transcriptomic signatures with language models*. Nature Communications (2026) 17:8501. DOI 10.1038/s41467-026-74411-3。

## 1. 论文元信息

| 项 | 值 |
|---|---|
| 标题 | Decoding cancer circulating transcriptomic signatures with language models |
| 期刊/年份 | Nature Communications, 2026, 17:8501 |
| 模型 | GeneLLM |
| 通讯作者 | 沙磊（oxtium.com）、金永成、徐俊杰、陈善稳、王鹏远 |
| 核心单位 | 北大医院胃肠外科、北航 AI 研究院、牛信宇科技(OxTium)、清华深圳、北京医院、邵逸夫医院 |
| 数据 | BioProject PRJNA1128376 |
| 代码/权重 | Zenodo 10.5281/zenodo.18822017（MIT License） |
| 许可 | CC BY-NC-ND 4.0 |

## 2. 三阶段流水线

### 阶段1：预训练（Pretraining）
- 输入：人源 cfRNA reads 的核苷酸序列（只保留比对上人基因组的 reads，不筛比对唯一性/MAPQ，以保留重复区与未注释区信号；丢弃 unmapped 防外源污染）
- token 化：read → 7-mer（连续 7 个核苷酸为一个 token）；`[SOS]` 前置输入、`[EOS]` 后置目标、`[PAD]` 对齐批内长度
- 架构：**6 个 Transformer decoder block**（自注意力 + 前馈，标准 Vaswani 架构），三角掩码保证自回归
- 目标：标准语言建模目标（预测下一 token）
- 语料：约 **20 万亿 (20 trillion) cfRNA reads**
- 硬件：**64 张 NVIDIA A100**，每 GPU batch size=1
- 时长：约 **15 天**
- 初始化：全部随机初始化，**未用任何 DNA 语言模型权重**（明确不初始化自 DNABERT/Evo2）

### 阶段2：伪生物标志物挖掘（Pseudo-biomarker mining）
冻结预训练 encoder，把每条 read 编码为 embedding：

**Eq.(1)** `g_ij = GeneLLM(s_ij)`，g_ij 为患者 i 的第 j 条 read 的最后输出向量。

伪生物标志物是 n 个原型向量 v_1..v_n，最小化：

**Eq.(2)**
```
min_{v_1..v_n} L_pm = - Σ_k Σ_ij log p_r(g_ij | v_C) · p_m(C | g_ij, {v_1..v_n})
```

其中决策概率（软分配，soft-assignment）：

**Eq.(3)**
```
p_m(C|x) = exp(-||v_C - x||²) / Σ_k exp(-||v_k - x||²)
```

重建概率（高斯分布，v_C 为均值、σ_C 为标准差，均 trainable）：

**Eq.(4)**
```
p_r(x|v_C) = (1/(σ_C√(2π))) · exp(-(x - v_C)²/(2σ_C²))
```

- 灵感来源：Sha et al. (2021, AAAI) 的多类型解耦方法
- 本质：**高斯混合原型聚类 / LLM alignment**，把海量 read embedding 对齐到有限原型
- n 作为超参：在 {200,400,600,1000,1200} 中按验证集平均 AUC 选 **n=1000**
- 只挖训练集，防泄露

### 阶段3：疾病调优（Disease tuning）
backbone 冻结，训练下游。

**患者特征汇总**（把 4000 万 reads 压成 n 维特征）：

**Eq.(7)** `f_i(k) = Σ_j p_m(k | g_ij)`，k=1..n
**Eq.(8)** `f_i = [f_i(1), ..., f_i(n)]`

**Source bias elimination**（源偏倚消除）：
- 收集训练集所有健康样本 H，算每源（中心）均值：

**Eq.(9)** `μ_k = Σ_{i∈H, s_i=k} f_i / Σ_{i∈H, s_i=k} 1`

- 对齐到统一均值 μ*（通常取各 μ_k 的平均），per-source 平移：

**Eq.(10)** `f'_i = f_i + μ* - μ_si`

设计动机：全局批校正需要重归一化整个数据集，会作废已训权重；per-source 平移只需对新患者做 shift，无需改动历史训练数据，可扩展。

**Multi-scale feature extractor**（多尺度特征提取）：
- 受 DenseNet（Huang et al. 2017）启发，堆叠 skip-connection 层
- 每个模块：feedforward → 与输入 concat → 激活（ReLU / Tanh 混用）
- 缓解梯度消失，捕捉不同粒度的序列模式

**Calibrated multi-head classifier**（校准多分类头）：
- 每疾病一个二分类头（该疾病样本 vs 非癌对照训练）：

**Eq.(11)** `p(d_j|i) = softmax(FFN(f̃_i))`

- pivot calibration（pivot 校准）——不同分类头的概率不可直接比，按 pivot 阈值 p̂_j 与通用阈值 p_M 比例缩放：

**Eq.(12)**
```
p_cal(d_j|i) = [p(d_j|i)/p̂_j · p_M] · I(p < p̂_j)
             + [1 - (1 - p(d_j|i))/(1 - p̂_j) · (1 - p_M)] · I(p ≥ p̂_j)
```

- 最终预测：取 p_cal 最大的疾病；若全部低于 p_M 则判为非癌

### 推理（Inference）
- 单条 read 编码：约 2.16×10⁻⁵ s
- 单患者（4000 万 reads）编码：约 14.4 分钟
- 10 个 ensemble 模型的 disease head：约 5.6 分钟/患者

## 3. 数据预处理流水线

1. 采血：肘正中静脉，EDTA 抗凝管，颠倒 8-10 次
2. 血浆分离：采血后 2 小时内离心，分装 -80℃ 冻存
3. cfRNA 提取：200 μL 血浆 + miRNeasy Serum/Plasma Advanced Kit (Qiagen)（可提约 18 nt 以上 RNA）
4. DNase I (NEB) 去 DNA
5. 建库：SMARTer Stranded Total RNA-Seq Kit v2-Pico Input Mammalian (Takara)，CRISPR/DASH 去核糖体 cDNA
6. 测序：Illumina NovaSeq 6000，PE150，约 4000 万 reads/样本（约 6 GB）
7. 质控：fastp v0.23.3（默认参数去接头去低质量）；STAR v2.7.10b（ENCODE 标准参数）比对到 GENCODE human release 43；SAMtools v1.17 flagstat 统计

## 4. 数据集与划分

| 项 | 值 |
|---|---|
| 总样本 | 496 例 |
| 癌症 | 332 例：结直肠癌 102、胃癌 102、肝癌 81、肺癌 47 |
| 非癌对照 | 164 例（按中心匹配） |
| 入组中心 | 北大医院（结直肠/胃癌）、邵逸夫（肝癌）、北京医院（肺癌） |
| 早期比例 | I/II 期占癌症 67.8% |
| 划分 | 5:1:4 训练/验证/测试，中心内按疾病状态分层 |
| 外部队列 | Yu 2020 PDAC（PRJNA552230）、Chen 2022 泛癌（PRJNA729258） |

## 5. 结果速查

### 主队列测试集 AUC
| 癌种 | AUC |
|---|---|
| 胃癌 | 0.996 |
| 肺癌 | 0.993 |
| 结直肠癌 | 0.986 |
| 泛癌 | 0.976 |
| 肝癌 | 0.924（最难） |
| 单癌种平均准确率 | 83.0% |

### 1 GB 低深度（约标准 1/6）
肝癌 0.994 / 肺癌 0.976 / 结直肠 0.965 / 胃癌 0.945 / 泛癌 0.978；20% 深度时各癌种仍 >0.96。

### 与传统 ML 对比（同一表达矩阵输入，测试集 AUC）
| 方法 | 泛癌 AUC |
|---|---|
| SVM | 0.836 |
| Random Forest | 0.850 |
| XGBoost | 0.887 |
| Logistic Regression | 0.863 |
| Elastic Net | 0.871 |
| Plain NN | 0.908 |
| **GeneLLM** | **0.976** |

领先 6-15 个百分点。注意：**RF 用 GeneLLM 伪生物标志物特征时泛癌 AUC=0.936，显著优于 RF 用表达矩阵(0.850)**，证明增益来自特征表示而非分类器。

### 外部队列（de novo 重训）
| 数据集 | 原研究 AUC | GeneLLM AUC | p |
|---|---|---|---|
| Yu 2020 PDAC (n=160) | 0.95 | 0.99 | 3.6×10⁻⁶ |
| Chen 2022 泛癌 (n=92) | 0.91 | 0.96 | 0.001 |
| Yu + SVM（换头） | 0.936 | 0.957 | — |
| Chen + RF（换头） | 0.910 | 0.934 | — |

### 暗物质贡献消融
用 BLASTn（NT 库 2024-06-23）把 1000 个伪生物标志物分"基因内/基因外"两组：
- 非基因组泛癌 AUC **0.889** vs 基因组 **0.792** —— 证明暗物质是主要贡献来源

## 6. 关键局限（务必在引用/借鉴时提及）

1. 样本量小（496 例），方法学验证而非临床早筛产品验证
2. 癌种↔中心强相关，source-bias 消除不能完全排除残留混杂
3. 跨队列 raw-read 迁移差：在 Chen 数据集上初始化自预训练 backbone 未超过 de novo 训练
4. 伪生物标志物生物学意义未验证（来源：癌细胞/免疫/血小板/测序 artifact 未知），需 qPCR/ISH/长读长/功能实验
5. 预训练算力门槛高（20T reads + 64 A100 + 15 天），难以完整复现
6. 只报 AUC，未充分报告固定特异度下早期灵敏度、PPV/NPV、癌种定位准确率
7. 低测序深度≠低总成本：预训练算力未计入

## 7. 统计方法

- 外部队列 AUC 对比：two-sided Wilcoxon signed-rank test，效应量 Rosenthal's r（0.1/0.3/0.5 = 小/中/大）
- 消融：percentile bootstrap 95% CI
- α=0.05，benchmark 对比未做多重比较校正

## 8. 伦理与经费

- 伦理：北大医院 2022-132、北京医院 2022BJYYEC-420-02、邵逸夫 2023-0300
- 经费：国家重点研发计划 2022ZD0117700、深圳科创委 KQTD20240729102051061、国自然 82271767 等
