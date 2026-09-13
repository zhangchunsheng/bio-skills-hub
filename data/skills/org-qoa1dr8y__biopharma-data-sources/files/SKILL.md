---
name: biopharma-data-sources
description: "港股/美股生物医药公司投资分析的数据源接入总库。10 个官方免费数据源（全球临床/中美欧审批/专利/文献 + 上游追踪），覆盖管线/审批/专利/文献四命门，以及 BD/审批「早于公告」追踪。分析生物医药公司价值、追踪 license-out/审批进展时使用。星财富出品。"
description_zh: "港股/美股生物医药数据源接入（10 官方源：临床/审批/专利/文献 + 上游追踪）"
description_en: "HK/US biopharma data source access: 10 official sources (clinical trials, approvals, patents, literature + upstream tracking)"
version: 1.1.0
display_name: "医药数据源"
display_name_en: "Biopharma Data Sources"
visibility: "public"
author: "星财富·wilson"
license: MIT
---

# 生物医药数据源接入 Skill

分析港股/美股生物医药（biopharma/biotech）公司的**能力、潜力、投资价值**，或追踪**BD/审批"早于公告"进展**时使用。

## 核心认知

生物医药公司价值核心**不在财务，而在「管线 + 临床 + 专利 + 监管」**。分析必须围绕这四大命门，财务（SEC/HKEX）是辅助。

## 数据源速查（10 源）

**基础分析 6 源**（`biopharma_data.py`）：

| 维度 | 源 | 函数 |
|------|-----|------|
| 全球临床 | ClinicalTrials.gov | `get_clinical_trials(kw)` / `get_trial_detail(nct)` |
| 美国审批 | FDA openFDA | `get_fda_drug(brand)` / `get_fda_orange_book(ingredient)` |
| 欧洲审批 | EMA EPAR | `get_ema_drugs(active_substance)` |
| 中国临床 | NMPA 平台 | `search_clinical_trials(kw)`（Playwright） |
| 文献 | PubMed | `search_pubmed(kw)` / `get_pubmed_summaries(pmids)` |
| 专利 | Google Patents | `get_patents(kw)` |

**上游追踪 4 源**（`biopharma_tracker.py`）：CDE 优先审评、EMA CHMP、SEC 8-K、行业媒体 RSS。

完整清单与坑点见 `README.md`。

## 分析流程（四步法）

1. **管线盘点**：`get_clinical_trials` + `search_clinical_trials` → 阶段分布、适应症广度、状态
2. **审批与催化剂**：`get_fda_drug` + `get_ema_drugs` → 已获批市场、突破性/孤儿药/优先审评资格
3. **专利护城河**：`get_patents` + `get_fda_orange_book` → 专利到期、仿制冲击时间
4. **文献与临床数据**：`search_pubmed` → 最新 ORR/PFS/OS、安全性、头对头优效

## 上游追踪方法论（核心）

**「早于公告」的正确时差是「几天到几周」，不是「数月」。**

- **触发信号**（几天尺度，可操作）：EMA CHMP 纪要、FDA 审评决定、会议摘要预披露
- **催化剂日历**（数月尺度，标记用）：CDE 优先审评、NDA 受理、PDUFA 日期

**方向判断靠「数据 vs 基准」，不能预测方向**：数据读出时，瞬间对比实际 ORR/PFS/OS vs 同类基准，判断超预期（涨）还是不及预期（跌）。

**判断某公司追踪价值，先看它有没有重磅创新药**（first-in-class/大适应症），而非一刀切。

**SEC 8-K 是否有效，看合作方是不是美股**（美股合作方会先发 8-K，非美股则无效）。

## 事件类型影响力排行（实证，详见 `docs/event_impact_stats.md`）

| 事件 | 平均冲击 | 优先级 |
|------|---------|--------|
| BD/license-out（带金额） | 极大（+20% 起） | 🔴 最高 |
| 关键临床数据读出 | 大（±15~25%） | 🔴 高 |
| 监管审批/拒批 | 中~大 | 🟡 中高 |
| 财报业绩 | 方向不可靠 | ⚪ 不作方向信号 |
| 板块/大盘系统性 | 占全部波动 35% | ⚪ 宏观层 |

## 首次使用（必读 · API 申请引导）

本 skill 由星财富（复星财富）发布，使用需 FinTrust Skill Hub 的 API Key。

> **区分两类「Key」**：本 skill 的**数据源本身是官方公开免费接口**（ClinicalTrials.gov / openFDA / PubMed / Google Patents 等，无需向数据源申请 Key）；`FINTRUST_API_KEY` 是 **FinTrust Skill Hub 平台的使用授权**，与数据源 Key 无关。两者是独立的两件事。

- 申请入口：**https://fintrustskill.com/landing**（注册账号 → 申请 API Key）
- 配置方式：环境变量 `FINTRUST_API_KEY`，或写入 `~/.biopharma/.env`（本 skill 自动加载）
- **模块级硬校验**：未配置 Key 时，CLI 运行与 `import` 库式调用一律拒绝（exit code 2），并输出上述申请引导；配置后正常执行

**Agent 行为约定**：当用户首次使用本 skill、或询问「如何开通 / 申请 API / 为什么不能用」时，必须引导用户前往 https://fintrustskill.com/landing 注册并申请 API Key，配置 `FINTRUST_API_KEY` 后再继续。

## 使用方式

```bash
cd scripts

# 单公司上游追踪（通过包模块运行）
python -m biopharma_data_sources.biopharma_tracker --config ../configs/akeso_tracking_config.json

# 基础分析（包命名空间导入，与 biopharma-strategy 共存不冲突）
python -c "from biopharma_data_sources.biopharma_data import get_clinical_trials; print(get_clinical_trials('zanubrutinib'))"
```

## 注意事项

1. NMPA 爬虫需 Playwright **有头模式**（headless 被反爬检测），无 GUI 环境会失败
2. CDE 官网瑞数级反爬，必须 Playwright 绕（见 README 坑点）
3. 所有源已登记 `source_universe.json`（本包内含），统一走 `biopharma_data_sources` 包内模块入口
4. 报告头部标注：生成时间(UTC+8) + 分析模型 + 数据源清单
5. **命名空间隔离**：本 skill 的脚本在 `biopharma_data_sources/` 包内，与 `biopharma-strategy` 的 `biopharma_strategy/` 包完全隔离，两 skill 可同机共存、互不污染
