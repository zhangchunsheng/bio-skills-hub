---
name: biopharma-strategy
description: "港股/美股生物医药公司完整投研策略方法论。含四步分析法、BD/审批「早于公告」上游追踪 SOP、重大性过滤、新公司接入模板、事件影响实证库。分析生物医药公司投资价值、追踪 license-out/审批进展、判断追踪价值时使用。星财富出品。"
description_zh: "港股/美股生物医药投研策略方法论（四步分析 + 上游追踪 SOP + 重大性过滤 + 新公司接入模板）"
description_en: "HK/US biopharma investment research strategy: 4-step analysis, upstream BD/approval tracking SOP, materiality filter, new-company onboarding template"
version: 1.1.0
display_name: "医药投研策略"
display_name_en: "Biopharma Strategy"
visibility: "public"
author: "星财富·wilson"
license: MIT
---

# 生物医药投研策略

港股/美股生物医药（biopharma/biotech）公司的**能力、潜力、投资价值**分析，以及 **BD/审批"早于公告"上游追踪**的完整策略方法论。

> 本 skill 聚焦**策略与判断方法**；数据抓取脚本（10 个官方免费源）已内置在 `biopharma_strategy/` 包内，可与 `biopharma-data-sources` 独立共存、互不依赖（两 skill 的包命名空间已隔离）。

## 核心认知

1. **价值核心不在财务，而在「管线 + 临床 + 专利 + 监管」**，财务（SEC/HKEX）是辅助。
2. **不是所有"更早知道"都有价值**，只有对股价有重大影响的信息才值得追踪（见 `references/event-impact-stats.md`）。
3. **判断某公司追踪价值，先看它有没有重磅创新药**（first-in-class/大适应症），而非一刀切。

---

## 一、分析流程（四步法）

1. **管线盘点**（能力核心）：`get_clinical_trials` + `search_clinical_trials` → 阶段分布、适应症广度、状态。III 期数量 = 近期价值，适应症覆盖 = 长期空间。
2. **审批与催化剂**（潜力）：`get_fda_drug` + `get_ema_drugs` → 已获批市场、突破性/孤儿药/优先审评资格。
3. **专利护城河**（持续性）：`get_patents` + `get_fda_orange_book` → 专利到期、仿制冲击时间。
4. **文献与临床数据**（最新信号）：`search_pubmed` → 最新 ORR/PFS/OS、安全性、头对头优效。

## 二、上游追踪方法论（核心）

### 时差价值排序

| 信号 | 时差 | 可操作性 |
|------|------|----------|
| 学术会议摘要预披露 | 7-21 天 | ✅ 最理想 |
| FDA 批准（PDUFA 前） | 3-7 天 | ✅ 高 |
| EMA CHMP 纪要 | 4-7 天 | ✅ 高 |
| SEC 8-K（合作方） | 数小时-天 | ✅ 高 |
| CDE 优先审评 | 数月-1年 | ⚪ 仅标记节点 |

### 方向判断

**工具抓"时点"，判断"方向"靠「数据 vs 基准」——不能预测方向。**

- 数据读出时，瞬间对比实际 ORR/PFS/OS vs 同类基准：超预期（涨）/ 颠覆性头对头（大涨）/ 不及预期（跌）
- 会议摘要预披露是双向的（康方 HARMONi-A 摘要跌 20%，HARMONi-2 涨 37.5%）

### 重大性过滤（`scripts/news_materiality_filter.py`）

四道门：时间窗 72h → 主体相关性 → 噪音名单 → 重大性分级 → 事件聚类去重。只推三类：📊数据读出 / 🏛️监管批准拒批 / 💰并购授权带金额。

**重大信号是稀疏事件**（每家每月 1-2 次），多数日子静默属正常（配合静默心跳避免误判系统失灵）。

## 三、新公司接入 SOP（4 步）

1. **盘点管线**：从年报/官网/招股书整理管线分子（中英文名+商品名+代号）和 BD 合作方
2. **建配置**：复制 `templates/tracking_config_template.json` → `<公司英文名>_tracking_config.json`，填入管线/合作方/关键词
3. **建 cron**：`biopharma_tracker.py --config <配置>`，每日 2 次（盘中+盘后）
4. **验证**：跑一次 dry-run，确认关键词能命中 EMA CHMP 等源

## 四、建议 cron 配置

| 任务 | schedule | 命令 |
|------|----------|------|
| 每日上游追踪（触发信号） | `0 8,20 * * *` | `biopharma_tracker.py --skip-cde` |
| 每周 CDE 催化剂日历 | `0 8 * * 1` | `biopharma_tracker.py --only-cde` |
| 生医事件影响库刷新 | 季度 `0 3 2 1,4,7,10 *` | 知识库刷新脚本 |

> 触发信号（EMA CHMP + SEC 8-K + 行业媒体）和催化剂日历（CDE）**分开跑**：CDE Playwright 慢，单独每周一次。

## 五、注意事项

1. NMPA 爬虫需 Playwright **有头模式**（headless 被反爬），无 GUI 环境会失败；CDE 瑞数级反爬需 Playwright 绕（见 `references/data-sources.md`）
2. SEC 8-K 只搜「公司英文名+创新药 INN」；先看合作方是不是美股
3. EMA CHMP 关键词用英文 + INN 负向排除衍生药
4. 行业媒体 BD 爆料需合作方 8-K 交叉验证
5. 报告头部标注：生成时间(UTC+8) + 分析模型 + 数据源清单
6. **命名空间隔离**：脚本在 `biopharma_strategy/` 包内，运行期状态/锁/缓存目录已按包隔离（`~/.biopharma/strategy/` 与 `~/.cache/biopharma_strategy/`），与 `biopharma-data-sources` 同机并跑互不干扰

---

## 首次使用（必读 · API 申请引导）

本 skill 由星财富（复星财富）发布，使用需 FinTrust Skill Hub 的 API Key。

> **区分两类「Key」**：本 skill 的**数据源本身是官方公开免费接口**（ClinicalTrials.gov / openFDA / PubMed 等，无需向数据源申请 Key）；`FINTRUST_API_KEY` 是 **FinTrust Skill Hub 平台的使用授权**，与数据源 Key 无关。

- 申请入口：**https://fintrustskill.com/landing**（注册账号 → 申请 API Key）
- 配置方式：环境变量 `FINTRUST_API_KEY`，或写入 `~/.biopharma/.env`（本 skill 自动加载）
- **模块级硬校验**：未配置 Key 时，CLI 运行与 `import` 库式调用一律拒绝（exit code 2），并输出上述申请引导；配置后正常执行

**Agent 行为约定**：当用户首次使用本 skill、或询问「如何开通 / 申请 API / 为什么不能用」时，必须引导用户前往 https://fintrustskill.com/landing 注册并申请 API Key，配置 `FINTRUST_API_KEY` 后再继续。

## 使用方式

```bash
cd scripts

# 单公司上游追踪（通过包模块运行）
python -m biopharma_strategy.biopharma_tracker --config ../configs/akeso_tracking_config.json

# 基础分析（包命名空间导入，与 biopharma-data-sources 共存不冲突）
python -c "from biopharma_strategy.biopharma_data import get_clinical_trials; print(get_clinical_trials('zanubrutinib'))"
```

## 港股顶尖生物医药标的参考

百济神州(6160)/信达生物(1801)/康方生物(9926)/再鼎医药(9688)/药明生物(2269)/石药集团(1093)/中国生物制药(1177)/翰森制药(3692)/和黄医药(0013)/科伦博泰(6990)/荣昌生物(9995)
