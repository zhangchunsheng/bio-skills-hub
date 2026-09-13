# 文献检索指南

## 目录
- [1. 检索策略](#1-检索策略)
  - [1.1 PubMed强制检索要求](#11-pubmed强制检索要求)
  - [1.2 检索维度分解](#12-检索维度分解)
  - [1.3 检索范围](#13-检索范围)
  - [1.4 时间范围](#14-时间范围)
- [2. 子代理指令模板](#2-子代理指令模板)
- [3. 文献汇总与分类](#3-文献汇总与分类)
- [4. 注意事项](#4-注意事项)

## 1. 检索策略

### 1.1 PubMed强制检索要求

**PubMed检索为本技能的强制要求，不可跳过。** 研究背景撰写阶段所引用的文献必须包含PubMed检索结果，以确保国际文献不被遗漏。

**操作规范**：

1. **构建PubMed检索式**：
   - 将研究药物英文名、适应症英文名、研究设计类型组合为检索式
   - 示例：`"{药物英文名}" AND "{适应症英文名}" AND ("randomized controlled trial" OR "RCT")`
   - 使用WebSearch工具检索：`site:pubmed.ncbi.nlm.nih.gov {检索式}`

2. **最低检索量要求**：
   - PubMed检索结果应≥5篇相关文献
   - 若结果<5篇，需扩大检索范围（去掉研究设计限制、使用更宽泛的关键词）
   - 若扩大后仍<5篇，需在方案中明确标注"该领域PubMed文献较少，证据基础以中文文献为主"

3. **文献质量要求**：
   - 优先纳入：Meta分析 > 大样本RCT（≥200例）> 小样本RCT > 观察性研究
   - 必须记录每篇文献的PMID或DOI
   - 对仅获取摘要的文献，标注"未获取正文全文"

4. **检索结果验证**：
   - 在向用户输出文献汇总时，单独列出"PubMed检索结果"部分
   - 包含检索式、检索日期、命中文献数量、核心文献列表

### 1.2 检索维度分解

将用户输入的研究主题分解为3-5个独立检索维度，每个维度由一个Explore子代理负责。常见分解模式：

**模式A：药物 vs 对照在目标人群中的应用**
- 维度1：研究药物的药理学特性与机制
- 维度2：研究药物在目标适应症中的临床研究
- 维度3：对照药物在目标人群中的有效性与安全性

**模式B：特定人群的诊疗需求**
- 维度1：目标人群的特殊临床需求与安全性顾虑
- 维度2：研究药物在特定人群中的证据
- 维度3：相关领域的最新指南与专家共识

**模式C：新适应症/新用法拓展**
- 维度1：研究药物已有适应症的证据基础
- 维度2：目标适应症的标准治疗现状与不足
- 维度3：研究药物在目标适应症中的探索性研究

### 1.3 检索范围

| 来源 | 优先级 | 说明 |
|------|--------|------|
| PubMed | **P0（强制）** | 英文原始研究、Meta分析 |
| Cochrane Library | P0 | 系统综述 |
| Web of Science | P1 | 英文原始研究 |
| CNKI/知网 | P0 | 中文原始研究 |
| 万方数据 | P1 | 中文原始研究 |
| ClinicalTrials.gov | P0 | 在研临床试验 |
| ChiCTR | P0 | 中国临床试验注册中心 |
| NMPA/FDA说明书 | P0 | 药品官方信息 |
| 最新临床指南 | P0 | 权威推荐意见 |

### 1.4 时间范围
- 默认检索近5年文献（如2021-2026）
- 经典里程碑研究不受时间限制
- 指南/共识检索最新版本

## 2. 子代理指令模板

向每个Explore子代理发送的指令应包含以下要素：

```
Search for the latest literature ({年份范围}) on:
{具体检索维度描述}

IMPORTANT: You MUST search PubMed (pubmed.ncbi.nlm.nih.gov) as the primary source.
Also search CNKI/Wanfang for Chinese literature and ClinicalTrials.gov for ongoing trials.

I need:
1. {具体信息需求1}
2. {具体信息需求2}
3. {具体信息需求3}

Search both English (PubMed/Google Scholar) and Chinese sources.
Provide specific study details: authors, journal, year, sample size, key findings.
For each PubMed result, include the PMID or DOI.
Do NOT fabricate any references - only report what you actually find.
Report all findings with source URLs.
```

## 3. 文献汇总与分类

检索完成后，将文献按以下维度分类整理：

### 3.1 按证据等级
- Meta分析/系统综述
- 大样本RCT（≥200例）
- 小样本RCT
- 观察性研究
- 病例报告/系列
- 指南/共识
- 药品说明书/官方信息

### 3.2 按主题
- 药理学研究
- 有效性研究
- 安全性研究
- 特殊人群研究
- 剂量探索研究
- 指南/共识

### 3.3 文献信息表

每篇文献记录：

| 字段 | 说明 |
|------|------|
| 编号 | [1], [2], ... |
| 来源 | PubMed / CNKI / 其他 |
| 作者 | 第一作者 et al. |
| 期刊 | 全称 |
| 年份 | 发表年份 |
| 卷期页 | 卷(期):页码 |
| 研究设计 | RCT/Meta/观察性等 |
| 样本量 | 纳入人数 |
| 关键发现 | 1-2句话概括 |
| PMID/DOI | 如有（PubMed文献必须提供） |
| URL | 源链接 |

### 3.4 PubMed检索结果单独报告

在文献汇总时，必须单独列出PubMed检索结果摘要：

```
## PubMed检索结果
- 检索式：{实际使用的检索式}
- 检索日期：{YYYY-MM-DD}
- 命中文献数：{N}篇
- 核心文献（按证据等级排序）：
  1. [PMID: xxxxxxx] Author et al., Journal, Year - 关键发现
  2. [PMID: xxxxxxx] Author et al., Journal, Year - 关键发现
  ...
```

## 4. 注意事项

1. **PubMed检索不可跳过**：即使研究药物是中文特有品种，也必须尝试PubMed检索（使用英文名或通用名）
2. **严禁编造文献**：只报告实际检索到的文献，无法获取全文的标注"未获取正文全文"
3. **交叉验证**：关键数据（如发生率、效应量）尽量有≥2个来源
4. **矛盾处理**：如不同研究结果矛盾，均报告并分析可能原因
5. **阴性结果**：不要只报告阳性结果，阴性结果同样重要
6. **在研项目**：检索ClinicalTrials.gov和ChiCTR，了解是否有同类在研项目
