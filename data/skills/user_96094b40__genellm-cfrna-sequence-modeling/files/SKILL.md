---
name: genellm-cfrna-sequence-modeling
slug: genellm-cfrna-sequence-modeling
version: 1.0.0
displayName: GeneLLM cfRNA 序列建模方法学
summary: 从原始 cfRNA 测序 reads 直接做语言模型建模，挖掘伪生物标志物与转录组暗物质的可迁移方法学
description: 提炼自 Nature Communications 2026 论文《Decoding cancer circulating transcriptomic signatures with language models》(DOI 10.1038/s41467-026-74411-3, GeneLLM 模型)。当用户需要 (1) 理解或复现 GeneLLM / cfRNA 液体活检序列基础模型的方法学；(2) 把"绕过基因注释、直接对原始测序 reads 做 Transformer 建模 + 伪生物标志物(pseudo-biomarker)挖掘 + 转录组暗物质挖掘"的范式迁移到其他组学场景（类器官药敏、单细胞 RNA-seq、bulk RNA-seq、计算病理、靶点挖掘）；(3) 设计 read-level / k-mer 级序列模型而非基因表达矩阵分类器时使用。核心知识：7-mer token 化、自回归预训练、高斯原型伪生物标志物挖掘(类 VQ/soft-clustering)、source bias elimination、多尺度特征提取、校准多分类头。
tags: [生物信息, 液体活检, 药物研发]
license: MIT
agent_created: true
---

# GeneLLM：cfRNA 原始序列建模方法学（可迁移范式）

## Overview

本技能蒸馏自 GeneLLM 论文，沉淀一套**"不依赖基因注释、直接对原始测序 reads 做语言模型建模"**的可复用方法学，供在其他组学场景中举一反三。核心思想一句话：**不要先把测序数据压成"基因表达矩阵"再建模，而是把每条 read 当作"句子"、把 k-mer 当作"词"，让 Transformer 直接学习序列上下文，从而保留传统流程丢掉的"转录组暗物质"信号。**

## 何时使用本技能

- 用户要理解 / 复现 / 改造 GeneLLM，或做 cfRNA 液体活检 / 多癌早筛方法学设计
- 用户想从"表达矩阵 + 机器学习"升级到"原始序列 + 基础模型"的研究选题
- 用户做类器官（PDO）药敏、单细胞、bulk RNA-seq、靶点挖掘，想借鉴 read-level 建模 / 暗物质挖掘思路
- 用户问"伪生物标志物 (pseudo-biomarker)"是什么、怎么挖、与传统差异基因有何区别

## 核心方法论：三阶段流水线

```
阶段1 预训练：cfRNA reads → 7-mer token → 自回归 Transformer（无标签）
阶段2 伪生物标志物挖掘：冻结编码器 → 每条 read 出 embedding → 挖 n 个高斯原型向量
阶段3 疾病调优：伪生物标志物汇总成患者特征 → source bias 消除 → 多尺度特征 → 校准多分类头
```

关键约束：**阶段1/2 只用训练集**（防数据泄露），验证集只用于超参选择（n 值、多尺度架构、pivot 阈值、早停），测试集只在最终评估用一次。

## 关键设计决策（举一反三时可复用的"招"）

1. **绕过基因注释**：模型输入只有人源 reads 的核苷酸序列，不喂基因名/坐标/表达量。保留重复区、多比对片段、基因间区信号。
2. **k-mer token 化**：把 read 拆成 7-mer（非单碱基），既控制词表规模又保留上下文。`[SOS]`/`[EOS]` 标记起止，`[PAD]` 对齐批内长度。
3. **冻结 backbone + 轻量下游**：预训练 backbone 冻结，只训 disease head，避免小样本过拟合，也绕开"40M reads/患者"无法整批监督训练的算力墙。
4. **伪生物标志物 = 高斯原型软聚类**：把海量 read embedding 压缩成 n 个可解释原型（论文选 n=1000），本质是 LLM alignment 过程。
5. **Source bias elimination**：用每中心健康样本的均值做 per-source 平移对齐，避免全局批校正导致的历史权重失效问题。
6. **pivot calibration**：多疾病独立分类头的概率不可直接比较，用 pivot 阈值按比例缩放后再选最大。
7. **10 模型 ensemble**：推理阶段 10 个 disease head 集成降方差。

详细公式推导见 `references/paper_methods.md`。

## 举一反三：范式迁移地图

GeneLLM 的核心范式是"**read-level 序列基础模型 + 原型压缩 + 偏倚校正 + 多分类头**"，可迁移到：

| 用户场景 | 迁移方式 |
|---|---|
| **类器官（PDO）药敏** | 把类器官 bulk RNA-seq 的 reads 直接做 k-mer 建模，绕过"比对→基因计数"步骤，挖耐药/敏感相关的 read 级伪生物标志物；或用 cfRNA 预测药物响应（对应你 OrganoidAI 的 IC50 药敏分析） |
| **单细胞 RNA-seq** | 论文明确提到可迁移到 scRNA-seq，挖细胞类型特异性伪生物标志物（对应你 U-Net 分割后的细胞类型 / 死活状态判读） |
| **胆管癌靶点挖掘** | 你现有 CCA-AI 用 Welch t-test/Fisher/XGBoost 挖"已知基因差异表达"，可补充"暗物质"视角：看未注释 lncRNA / 重复元件 / 基因间区转录片段在胆管癌中的诊断价值 |
| **计算病理 / 数字病理** | 把"patch 序列化"思路类比到"read 序列化"，序列基础模型 + 原型向量 + 多分类头的架构可平移 |

详见 `references/transfer_playbook.md`。

## Resources

- `references/paper_methods.md` —— GeneLLM 完整方法学公式、算力配置、数据集、结果与局限性（精读原文提炼）
- `references/transfer_playbook.md` —— 面向类器官药敏 / 单细胞 / 靶点挖掘的具体迁移方案与落地步骤

---

## 付费 API 推理（可选）

本 skill 的**方法论指导完全免费**。当你需要「真正跑 GeneLLM 做 read-level 序列建模」时，可调用付费推理端点（模型推理按次计费）：

- **环境变量**：`SKILL_API_KEY`（用户自己的 API Key，`sk_live_` 前缀）、`SKILL_API_BASE`（默认 `http://127.0.0.1:8899`）
- **调用方式**：
  ```bash
  python scripts/call_genellm_api.py --reads <read1> <read2> ... --n-kmers 1000
  ```
- **计费**：每次推理扣 2 点，余额不足返回 402 并提示充值
- **端点**：`POST /infer/genellm`（鉴权头 `X-Api-Key`）

> 没有 API Key 时，本 skill 仍可完整输出三阶段流水线、伪生物标志物挖掘与迁移方案，供你自己本地复现。
