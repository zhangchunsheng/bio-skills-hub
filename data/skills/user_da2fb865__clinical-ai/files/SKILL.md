---
name: medical-ai-intel
description: 该技能用于搭建并运营一个「医疗AI情报台」：每天从 PubMed（或官网AI产品公告）检索 AI 相关医学文献/产品，按影响因子与引用数筛选高质量条目，生成结构化解读（背景/方法/测试验证/临床与商业化现状/相似/优势/局限），自动存档为 JSON、形成知识图谱，并生成可发布的单文件 HTML 看板（含内联力导知识图谱），再部署到云端实现「采集产出即云端同步」（云端同步自动化采用采集驱动 + 5 分钟守卫）。当用户需要「每天了解一个医疗AI项目」「做医学AI文献情报汇总/知识库」「把文献解读做成可分享看板」时触发本技能。
agent_created: true
---

# 医疗AI情报台（Medical AI Intel）

## Overview

本技能把「每日医疗AI情报」做成一套可复用的流水线：检索 → 筛选 → 结构化解读 → 存档(JSON) → 知识图谱 → 单文件 HTML 看板 → 云端部署同步。打包为模板后，他人可一键初始化自己的情报台目录并复用完整脚手架（看板渲染代码 + 重建脚本 + 字段规范 + 检索/部署经验）。

## 何时使用

- 用户想「每天自动跟踪医疗AI文献/产品，达到每天了解一个项目」。
- 用户要做医学AI文献的情报汇总、解读库、知识图谱。
- 用户要把文献解读做成可分享/可发布的看板（本地 + 云端链接）。
- 用户已有类似需求，需要一套字段规范与可运行模板。

## 快速开始（为他人初始化一份情报台）

将本技能的 `assets/dashboard-template/` 整体复制到目标工作目录（如 `medical-ai-intel/`），即得到可运行脚手架：

```
medical-ai-intel/
├── medical-ai-intel.html      # 单文件看板（数据已内联，直接双击可看）
├── build.js                   # 从 archive 重建看板内嵌数据
└── archive/
    ├── entries.json           # 条目数组（唯一数据源）
    └── graph.json             # 知识图谱 nodes/edges（唯一数据源）
```

运行与刷新：
1. 用真实数据替换 `archive/entries.json`、`archive/graph.json`（字段规范见 `references/interpretation-schema.md`）。
2. 执行 `node build.js` → 重建 `medical-ai-intel.html` 内嵌数据（本地看板即时更新）。
3. 发布到云端：准备 `deploy/` 目录（`mkdir -p deploy && cp medical-ai-intel.html deploy/index.html`），调用 `workbuddy_cloudstudio_deploy`（action=deploy, directory=部署目录, port=3000）得到分享链接。详见 `references/cloud-deploy-sync.md`。

> 模板内置 1 条公开示例（IDx-DR），结构与真实条目一致，仅用于演示渲染，不依赖任何私人数据。

## 工作流

### 1. 检索候选
- 论文：PubMed E-utilities（esearch/efetch）。检索式与参数见 `references/pubmed-europepmc.md`。
- 产品：官网 / FDA / NMPA / 厂商新闻稿。
- **限流 fallback**：NCBI efetch 被临时限流时，立即改用 Europe PMC 主题+日期检索取摘要与引用数，不要重试 efetch。

### 2. 质量筛选
- 综合「相关性 + IF（期刊映射近似） + 引用数（Europe PMC）」挑 1 条作为「今日项目」，其余入库为历史。
- IF 为近似值，在输出中注明。

### 3. 结构化解读（严格遵守字段规范）
- 每条 `interpretation` 必须为嵌套对象，渲染顺序：`background → method(算法/数据集/数据量/流程/测试验证) → clinicalStatus(阶段/审批/商业化) → advantages → limitations → similar`。
- `method` 是**对象**（5 子项），`evaluation`（测试/验证）在 method 内，不是顶层字段。
- `clinicalStatus` 是**对象**（3 子项）；已进入商业化的条目，`commercial` 须给公司/融资/销售/营收医保等可查证信息。
- 完整 schema 见 `references/interpretation-schema.md`。

### 4. 存档 + 知识图谱
- 追加到 `archive/entries.json`（保持 id 唯一，无重复 pmid）。
- 在 `archive/graph.json` 新增节点（entry/method/scene/org/dataset/metric/approval）与边；两条目共享 method/org 节点时自动形成「相似」边。

### 5. 生成看板并发布
- `node build.js` 从 archive 重建 `medical-ai-intel.html`（也可顺带写 `deploy/index.html`）。
- 部署到云端（见 `references/cloud-deploy-sync.md`）。
- 设置两个自动化：A「每日入库」（只写 `archive/*.json`）+ B「云端同步」。**B 必须用「采集驱动」模式**——高频轮询 + 条件守卫（读 `archive.updatedAt` 是否为今天、距产出是否满 5 分钟、当日是否已同步标记），只有采集已产出且满 5 分钟才 build + 重新部署；没采集就绝不同步。完整 rrule、守卫逻辑与同步 SOP 见 `references/cloud-deploy-sync.md`。

## 关键坑（务必遵守）

- **build.js 不得拼接重复声明**：用正则重写内嵌 JS 数据块时，替换串只替换「自身声明」，严禁拼进下一个声明名（如 `const DEMO_GRAPH = ` 或 `let DATA = `），否则会产生 `const DEMO_GRAPH = const DEMO_GRAPH = …` 这类重复声明，导致整段脚本语法错误、页面空白。正确写法见 `references/cloud-deploy-sync.md`。
- **校验用 `node --check` 跑整段脚本**，不能只 `JSON.parse` 抽取的数据——后者漏报重复声明类语法错误。
- 看板为单文件、数据内联，无需后端；云端是静态快照，必须靠 build.js + 重新部署保持同步。

## Resources

### assets/dashboard-template/
可直接复制运行的可复用脚手架：`medical-ai-intel.html`（完整渲染代码 + 内联力导知识图谱，含独立分栏滚动、拖拽/缩放/高亮交互）、`build.js`（从 archive 重建看板）、`archive/`（entries.json + graph.json 样本）。

### references/interpretation-schema.md
解读字段规范：entry 顶层字段、interpretation 嵌套结构（method 5 子项、clinicalStatus 3 子项、advantages/limitations/similar）、渲染顺序、图谱节点类型与边关系。

### references/pubmed-europepmc.md
文献检索要点：PubMed E-utilities 用法、Europe PMC fallback（主题+日期检索 / 单篇引用数）、IF 近似、质量筛选建议、商业产品条目来源。

### references/cloud-deploy-sync.md
云端部署与「采集产出即云端同步」闭环：单一数据源架构、CloudStudio 部署步骤、**采集驱动同步自动化（轮询+守卫+当日标记，主推方案）**、固定时间同步的反模式、build.js 致命坑与正确写法、被污染后的修复方法、七步同步 SOP。

## 版本变更记录
- **v2.0（2026-08-27）**：云端同步自动化由「固定时间（每日 09:10）」改为「**采集驱动**」——高频轮询（每 5 分钟）+ 三级守卫（当日已同步标记 / `updatedAt` 非今天则跳过 / 距产出未满 5 分钟则等下次）+ 同步后写当日标记。解决「采集延迟导致同步漏数据」的实战问题。同步 SOP 固化为 `cloud-deploy-sync.md` 的七步清单。
- **v1.0**：初版，单文件看板 + 双 JSON 数据源 + 固定时间同步。
