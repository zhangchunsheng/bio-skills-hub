---
name: med-literature-tracker
description: 医学文献自动追踪与速读。从NEJM、Lancet、JAMA、BMJ、Nature Medicine等国际顶级期刊及中华系列国内核心期刊检索最新文献，支持PubMed和Web of Science双源检索，自动翻译摘要为中文，生成结构化文献简报（对话展示+Markdown文件保存）。支持按关键词或专业领域检索，可配置每日/每周/每月自动更新。Use when user mentions 医学文献、文献追踪、文献速读、期刊追踪、文献更新、PubMed、Web of Science、医学前沿、文献周报、文献月报、最新研究进展, or when user wants to track latest medical research or stay updated on medical literature.
---

# 医学文献追踪与速读 (Med-Literature Tracker)

## Quick start

用户说"追踪糖尿病最新文献，每周更新"即可启动。Skill 自动完成：确认参数 → PubMed+WoS 双源检索 → 按期刊等级和相关性排序筛选 → 抓取摘要 → 翻译提炼 → 生成简报 → 可选定时任务。

## Workflow

### Step 1: 收集检索参数

与用户确认以下参数（未明确时使用默认值）：

| 参数 | 默认值 | 说明 |
|------|--------|------|
| 关键词/专业 | 必须提供 | 英文关键词效果更好；中文关键词自动翻译为英文再检索 |
| 期刊范围 | Tier 1 + Tier 2 | 可选：仅顶刊 / 含国内核心 / 全部 |
| 更新频率 | 每周 | 每日 / 每周 / 每月 / 仅本次 |
| 时间范围 | 近 30 天 | 可指定天数或日期范围 |
| 输出方式 | 对话 + 文件 | 对话展示 + 保存 Markdown 到 output 目录 |

### Step 2: 构建检索策略

**PubMed 检索**（优先，公开免费）：
使用 web_search，按期刊等级分两批检索：

第一批 - Tier 1 顶刊：
```
site:pubmed.ncbi.nlm.nih.gov (keyword) AND (N Engl J Med[Journal] OR Lancet[Journal] OR JAMA[Journal] OR BMJ[Journal] OR Nat Med[Journal])
```

第二批 - Tier 2 重要期刊：
```
site:pubmed.ncbi.nlm.nih.gov (keyword) AND (Science[Journal] OR Cell[Journal] OR Nature[Journal] OR JAMA Intern Med[Journal] OR Lancet Oncol[Journal] OR ...)
```

期刊 PubMed 标准缩写见 REFERENCE.md。

**Web of Science 补充检索**：
```
site:webofscience.com (keyword) (journal_name)
```
注意：WoS 为付费数据库，可能无法直接获取全文。若 WoS 访问受限，以 PubMed 结果为主，在简报中注明数据来源。

**国内核心期刊补充**（如用户选择包含国内核心）：
使用 web_search 检索中华系列期刊官网或中国知网。

### Step 3: 文献排序与筛选

按以下优先级排序，取前 10-15 篇：

1. **期刊等级**：Tier 1 > Tier 2 > 国内核心
2. **关键词匹配度**：标题中含关键词优先
3. **时效性**：越新越优先
4. **研究设计等级**：RCT > Meta分析/系统综述 > 队列研究 > 病例对照 > 综述 > 病例报告

对每篇候选文献，使用 web_fetch 抓取 PubMed 详情页，提取：
- Title / Authors（第一作者 + 通讯作者） / Journal / Publication Date / Abstract / DOI / PMID

### Step 4: 翻译与关键结论提炼

对每篇最终入选文献：

**翻译规则**：
- 医学术语使用中文通用译名（参考人民卫生出版社术语标准）
- 药物名优先使用国际非专利名（INN）
- 保持原文语义完整，不添加主观评价
- 统计学结果完整保留（OR/RR/HR + 95%CI + p值）

**关键结论提炼**：
- 1-2 句话概括核心发现
- 标注证据等级和研究设计类型
- 如为 RCT，标注样本量和主要终点

### Step 5: 生成文献简报

**对话中展示**：

```
## [关键词] 文献简报 | YYYY-MM-DD

> 检索范围：[期刊范围] | 时间：[时间范围] | 共筛选 [N] 篇

### 1. [中文标题]
- **原文标题**：[English Title]
- **作者**：[First Author et al., Corresponding Author]
- **期刊**：[Journal Name] | [Publication Date]
- **DOI**：[DOI]
- **摘要原文**：[English Abstract]
- **中文摘要**：[Chinese Translation]
- **关键结论**：[1-2 sentences] | 证据等级：[RCT / Meta / Observational / ...]

---
```

**保存文件**：
同时将完整简报写入 `output/[关键词]_文献简报_[YYYY-MM-DD].md`。

### Step 6: 设置定时更新

若用户要求定期更新，使用 create_scheduled_task：

- **每日更新**：`type=cron, cron_expr="0 8 * * *"`（每天早上 8 点）
- **每周更新**：`type=cron, cron_expr="0 8 * * 1"`（每周一早 8 点）
- **每月更新**：`type=cron, cron_expr="0 8 1 * *"`（每月 1 号早 8 点）

prompt 中必须包含：关键词、期刊范围、时间范围、输出路径等完整上下文。

## 期刊与检索细节

详见 [REFERENCE.md](REFERENCE.md)。

## 使用示例

详见 [EXAMPLES.md](EXAMPLES.md)。