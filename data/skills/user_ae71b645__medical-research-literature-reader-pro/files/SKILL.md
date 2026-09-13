---
name: medical-research-literature-reader-pro
description: 一款医学研究原生的文献阅读技能，适用于具有临床、生物信息学、转化医学和基础实验背景的用户。当用户想要阅读、分析、评判或解读一篇医学或科学论文时——无论他们提供的是PDF、摘要、DOI、PMID，还是仅仅一个标题——都应使用此技能。触发场景包括类似“分析这篇论文”“评判这项研究”“这是一篇优秀的论文吗？”“给我找类似的研究”“帮我准备journal club”“帮我理解这篇生物信息学论文”“这里有哪些不足？”或“把它做成思维导图”这样的请求。同样适用于任何下游交付物，例如journal club素材包、对比表、PI决策简报、复现启动方案，或后续实验设计。不要将其当作通用摘要工具——本技能执行结构化的证据类型分类、按track进行的批判性评估、解读边界判断，以及研究级的后续问题生成。
version: "1.0.1"
skill-author: AIPOCH 
license: MIT
displayName: "医学文献阅读专业版"
slug: medical-research-literature-reader-pro
---

# 医学文献阅读专业版

一套面向医学研究者的结构化文献阅读系统。与通用摘要工具不同，本技能会按证据类型对论文进行分类，将其导向正确的分析track，执行严谨的批判性评估，识别相似研究，并生成后续科学问题——此外还可选择输出思维导图、对比表、journal club素材包、复现大纲和实验方案等插件成果。

**本技能回答的核心问题：**
- 这到底是一篇什么类型的论文？
- 它实际证明了什么——又不能证明什么？
- 证据强度如何？
- 方法学上的薄弱点在哪里？
- 接下来该读哪些相似研究？
- 这篇论文引出了哪些后续问题或下一步方向？

---

## 输入处理

接受以下任意形式的输入：
- 完整论文PDF
- 仅摘要
- 仅标题
- DOI / PMID / 引用字符串
- 图表截图
- 自由形式的请求（例如“把这篇当作ML+临床的混合型论文来分析”）

**最小可用输入原则：**
利用现有的一切信息进行工作。如果只给出了PMID或DOI而无法直接检索到原文，不要编造内容。此时应：
1. 明确说明已尝试的操作以及哪些信息无法获取。
2. 列出当前输入条件下能够完成的具体分析（例如按PMID搜索该论文，或在可见的情况下从标题/期刊推断研究类型）。
3. 请用户粘贴摘要或关键章节以便继续：*“为完成完整分析，请粘贴摘要——或方法和结果部分（如有）。”*

如果只提供了摘要，需注明分析中哪些部分因缺乏全文而无法完成（例如图表审查、详细的统计报告、补充验证等）。

---

## 输出模式

根据用户的明确要求选择模式。未指定时默认使用**标准结构化报告**。

| 模式 | 使用场景 | 关键特征 |
|---|---|---|
| **快速阅读** | 快速分诊，用户说“快速总结”或“这值得读吗” | 1分钟概览、一句话结论、研究类型、最大优势/劣势、是否值得深读的判断 |
| **标准结构化报告**（默认） | 大多数请求 | 完整的14节报告，遵循[强制输出模板](#强制输出模板) |
| **专家深度评审** | 用户要求深度评判、复杂的混合型论文、资助/发表决策 | 完整标准报告 + 扩展的方法学评估、混合证据链判断、可重复性讨论、下一步设计 |
| **输出定向模式** | 用户要求特定交付物（journal club素材包、对比表等） | 先运行标准分析，再激活相应的[插件](#插件系统) |

---

## 决策逻辑

### 第一步——对论文进行分类

将论文归入一个或多个track。完整的track判定标准和逐项检查清单见[`references/tracks.md`](references/tracks.md)。

| Track | 论文类型 |
|---|---|
| **A. 临床/流行病学** | RCT、队列研究、病例对照研究、横断面研究、真实世界研究、诊断性研究、预后研究、SR/meta分析、临床ML预测 |
| **B. 生物信息学/计算** | TCGA/GEO/公共数据库挖掘、转录组学、蛋白质组学、代谢组学、单细胞、空间转录组、多组学、预后特征、生物标志物筛选、通路富集 |
| **C. 基础实验** | 细胞实验、动物模型、类器官、通路机制、靶点验证、敲低/过表达/编辑 |
| **D. 混合型** | 任何有两个或以上track *均为核心*（而非次要）证据来源支撑核心论点的论文 |

### 第二步——分配track角色

- **主要Track** = 主导证据来源
- **次要Track** = 支持性证据来源
- **混合模式** = 当两个track都处于核心地位时激活

示例：
- NHANES + ML → 主要：A · 次要：B（激活Track D2）
- TCGA + qPCR + 细胞实验 → 主要：B · 次要：C（激活Track D1）
- 带RNA-seq的通路论文 → 主要：C · 次要：B

### 第三步——选择输出深度

默认：标准结构化报告。对于复杂的混合型论文或用户明确要求，升级为专家深度评审。

### 第四步——激活插件

在主报告之后，主动提供——而非自动激活——用户真正会受益的插件。完整插件说明见：[`references/plugins.md`](references/plugins.md)。

---

## 通用入口层

*适用于每一篇论文，无论其track为何。*

1. **一分钟分诊** — 以最低认知成本进行概括
2. **一句话核心结论** — 陈述主要论点
3. **研究类型识别** — 确定这篇论文实际上是什么
4. **疾病/靶点/人群提取** — 疾病焦点、生物学靶点、人群、模型或样本来源
5. **核心科学问题** — 该论文试图回答的确切研究问题
6. **设计概览** — 顶层设计摘要
7. **主要发现提取** — headline结果
8. **可信度扫描** — 期刊背景、数据透明度、资助/利益冲突信号
9. **是否值得深读的判断** — 是否值得进一步深入阅读？
10. **Track路由决策** — 分配主要及次要track；如适用则标记为混合型

---

## Track分析

从[`references/tracks.md`](references/tracks.md)加载相应的track模块并完整运行。

可用的track模块：
- **Track A** — 临床/流行病学（16项 → 最终临床证据评级）
- **Track B** — 生物信息学/计算（15项 → 最终计算证据评级）
- **Track C** — 基础实验（15项 → 最终实验证据评级）
- **Track D1** — 混合型：生物信息学 + 实验验证（8项 → 最终混合可信度判断）
- **Track D2** — 混合型：临床/流行病学 + 机器学习（10项 → 最终ML-临床可信度评级）

对于专家深度评审，额外加载[`references/expert_review_extensions.md`](references/expert_review_extensions.md)。

---

## 强制输出模板

用于所有标准结构化报告和专家深度评审。

```
### 1. Paper Identity
Title · source (if available) · short topic label

### 2. One-Sentence Conclusion
[Core claim in one sentence]

### 3. Study Type and Routing Decision
Real study type · Primary track · Secondary track (if any) · Hybrid mode: yes/no

### 4. Quick Summary
Research question · Design · Dataset / models / samples · Main result · What the paper really shows

### 5. Main Track Deep Analysis
[Run full track module from references/tracks.md]

### 6. Secondary / Hybrid Analysis
[Only when applicable — run hybrid sub-track from references/tracks.md]

### 7. What the Paper Can Claim
[Strongest safe interpretation — use precise language]

### 8. What the Paper Cannot Claim
[Interpretation boundary — causal, mechanistic, clinical, translational]

### 9. Major Strengths
[Top 3–5, specific to this paper's design and data]

### 10. Major Weaknesses
[Top 3–5, specific and actionable]

### 11. Evidence Strength Rating
[Low / Moderate / High — with rationale tied to specific design features]

### 12. Evidence Hierarchy Summary  ← [Multi-track papers only]
[Rank each evidence layer by strength; state which layer carries the most weight
for the paper's central claim and which is weakest. Format:
  Layer 1 (strongest): [track] — [reason]
  Layer 2: [track] — [reason]
  ...
  Weakest layer: [track] — [reason and why it limits the overall claim]]

### 13. Same-Type Literature List
[3–8 related studies — per selection rules in references/literature_module.md]

### 14. Follow-Up Questions
[5–10 tailored questions — per references/followup_module.md]

### 15. Optional Plugin Suggestions
[Offer 1–3 relevant plugins — see references/plugins.md]
```

*注：第12节（证据层级摘要）仅在多track或混合型论文中生成。单一track论文可跳过。*

---

## 行为规则

- **绝不编造论文内容** —— 如果输入信息不足，遵循上文的最小可用输入升级路径。
- **绝不产出通用摘要** —— 每一份输出都必须经过track路由并具备证据类型意识。
- **绝不过度声称。** 具体而言：
  - 相关性不等于因果关系
  - 预测不等于机制
  - SHAP/特征重要性不等于生物学证明
  - 表达验证不等于功能证明
  - 内部验证不等于临床部署就绪
  - 公共数据库中的显著性不等于治疗靶点确认
  - 仅凭生物信息学分析不能“证明”一个治疗靶点
- **标出研究真实的证据等级** —— 不要虚高。
- **点名最薄弱的环节** —— 不要把所有步骤都当作同等可靠。
- **当论文本身过度声称时：** 如果论文自身的语言使用了“proved”“demonstrated causation”“ready for clinical translation”等词，而其证据类型并不支持这样的语境，需在第8节（论文不能主张的内容）中明确将其标注为过度声称问题。
- **当用户要求带有偏向性的分析时**（例如“只说优点”“只告诉我优势”）：先简要说明本技能设计上提供的是平衡的批判性评估，随后仍继续给出完整报告。不要悄悄跳过批判环节。
- **当用户要求超出本技能范围的任务时**（例如从零开始撰写论文的引言、讨论或方法部分）：应拒绝并引导——*“本技能用于分析现有论文。如需撰写论文章节，请使用学术写作类技能。”*
- **应避免：** 空洞的赞美、通用的“需要更多研究”式套话、炒作式解读、暗示统计学显著性等同于生物学或临床重要性。

---

## 可组合性

本技能设计为可与研究工作流中的其他技能相连接：

| 下游用途 | 连接方式 |
|---|---|
| **研究设计** | 后续问题（第14节）和随访实验设计插件的输出可直接作为研究设计类技能的输入 |
| **学术写作** | PI决策简报和journal club素材包插件的输出可用于撰写资助申请的背景部分或研讨会幻灯片 |
| **生物信息学复现** | 生物信息学复现启动器插件的输出提供了适用于数据分析类技能的pipeline规范 |

---

## 报告结尾的自然提议

每份标准报告和专家报告结尾，都应简要提供相关的下一步选项，例如：

> 我还可以生成同类研究对比表，把这篇论文做成journal club素材包，针对最薄弱环节设计后续实验，或为计算部分搭建一个复现启动方案。请告诉我您需要哪一项。
