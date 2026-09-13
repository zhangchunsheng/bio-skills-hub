# 生物医药数据源详细文档

> 10 个专用数据源，分「基础分析层」（6 源）和「上游追踪层」（4 源）。全部官方免费，已登记 source_universe.json。

---

## 基础分析层（6 源）— `scripts/biopharma_data.py`

### 1. ClinicalTrials.gov（NIH 全球临床）

- **接口**：`https://clinicaltrials.gov/api/v2/studies`
- **函数**：`get_clinical_trials(kw)` / `get_trial_detail(nct)`
- **拿什么**：全球试验的阶段分布（Phase I/II/III）、适应症广度、状态（recruiting/completed）、NCT 编号
- **稳定性**：high
- **用途**：管线盘点——III 期数量 = 近期价值，适应症覆盖 = 长期空间

### 2. FDA openFDA（美国审批 + 橙皮书）

- **接口**：`https://api.fda.gov`
- **函数**：`get_fda_drug(brand)` / `get_fda_orange_book(ingredient)`
- **拿什么**：FDA 批准记录、橙皮书成分/市场状态（是否已上市、仿制药竞争）
- **稳定性**：high
- **坑**：Orange Book 不含专利到期时间（只有批准+成分），专利到期需用 Google Patents 的 priority_date 推算

### 3. EMA EPAR（欧洲审批）

- **接口**：`https://www.ema.europa.eu/en/documents/report`
- **函数**：`get_ema_drugs(active_substance)`
- **拿什么**：欧洲批准/适应症/治疗领域
- **稳定性**：high
- **缓存**：Excel 下载（约 2700 条），带 7 天本地缓存，避免每次下 898KB

### 4. PubMed（NCBI 文献）

- **接口**：`https://eutils.ncbi.nlm.nih.gov/entrez/eutils`
- **函数**：`search_pubmed(kw)` / `get_pubmed_summaries(pmids)`
- **拿什么**：最新临床数据首发地（ASCO/ASH 发表、ORR/PFS/OS、头对头优效、安全性信号）
- **稳定性**：high

### 5. Google Patents（全球专利族）

- **接口**：`https://patents.google.com/xhr/query`（非官方但公开）
- **函数**：`get_patents(kw)`
- **拿什么**：专利族、各国 active 状态、priority_date（推算专利到期）
- **稳定性**：medium
- **坑**：失败可退回 web_search

### 6. NMPA 临床试验平台（中国临床）

- **接口**：`https://www.chinadrugtrials.org.cn`
- **函数**：`search_clinical_trials(kw)`（`nmpa_clinical_trials.py`）
- **拿什么**：国内 CTR 编号/状态/适应症
- **稳定性**：medium
- **坑**：Playwright **有头模式**（headless 被反爬检测），无 GUI 环境会失败

---

## 上游追踪层（4 源）— `scripts/biopharma_tracker.py`

> 抢在「公司公告」前获知 BD / 审批进展，时差「几天到几周」。

### 7. CDE 优先审评 + 突破性治疗（中国获批前哨）

- **接口**：`https://www.cde.org.cn/main/xxgk/listpage/...`（优先审评/突破性治疗两个公示页）
- **函数**：`cde_priority_collector.py: collect([公司名])`
- **时差**：早于 NMPA 获批 **数月-1年**（信达替妥尤单抗 2024-05 优先审评 → 2025-03 获批）
- **稳定性**：medium
- **定位**：**催化剂日历**（标记"未来会获批"节点），**不是买入信号**（时差太长无法布局）
- **坑**：瑞数级反爬，requests 返回空页 + JS 挑战，必须 Playwright（headless=True + disable-blink-features + 隐藏 webdriver），等 JS 挑战约 6 秒后填查询框

### 8. EMA CHMP 会议纪要（欧盟批准前哨）

- **接口**：`https://www.ema.europa.eu/en/homepage`（抓 meeting-highlights 链接）
- **函数**：`check_ema_chmp()`
- **时差**：早于 EC 正式批准/公司公告 **4-7 天**（复宏汉霖 H药 2026-03-30 公告，EMA 3-23/26 已发）
- **稳定性**：high
- **坑**：页面英文，关键词用 `name_en`/`brand_eu`；INN 负向排除衍生药（trastuzumab 会误命中 Enhertu/Kadcyla 等 ADC）

### 9. SEC 8-K（美股合作方披露）

- **接口**：`https://efts.sec.gov/LATEST/search-index`（EDGAR full-text search）
- **函数**：`check_partner_sec()`
- **时差**：数小时-天（BD 交易另一方先披露）
- **稳定性**：high
- **坑**：只搜「公司英文名 + 创新药 INN」，生物类似药 INN（trastuzumab/rituximab 等）是通用名会命中几十家无关药企；**先看合作方是不是美股**（美股合作方才有效，非美股无效）

### 10. 行业媒体 RSS（7 家）

- **接口**：Endpoints / Fierce Biotech / Fierce Pharma / PharmaTimes / BioPharma Dive / STAT / GenEngNews + Google News
- **函数**：`check_industry_news()`
- **用途**：BD 爆料（Endpoints/Fierce 常首发）
- **稳定性**：medium
- **坑**：有假消息风险，BD 爆料必须用合作方 8-K/官方披露交叉验证；Fierce RSS title 嵌套 `<a>` 标签，需 `"".join(el.itertext())` 提取

---

## 重大性过滤（`scripts/news_materiality_filter.py`）

只推三类（四道门：时间窗 72h → 主体相关性 → 噪音名单 → 重大性分级 → 事件聚类去重）：

| 类别 | 判据 |
|------|------|
| 📊 数据读出 | 关键临床数据、主要终点达成/失败、揭盲、OS/PFS |
| 🏛️ 监管批准/拒批 | NMPA/FDA/EMA 批准、拒批、CRL、临床暂停、撤回、PDUFA |
| 💰 并购/授权带金额 | 交易词 + 明确金额（$500M / 首付款 等） |

**重大信号是稀疏事件**（每家每月 1-2 次），多数日子静默属正常。

> 新闻标题中文翻译为可选增强：脚本默认输出原文标题；如需接入翻译，自行实现 `translate_batch` 并在 `biopharma_tracker.py` 的 `_translate_hits` 中调用。
