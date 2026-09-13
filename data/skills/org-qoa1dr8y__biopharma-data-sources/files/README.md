# 生物医药数据源接入 Skill（Biopharma Data Sources）

> **星财富（复星财富）出品** · 港股/美股生物医药公司投资分析的数据源接入方案，含 **10 个官方免费数据源**，分「基础分析层」和「上游追踪层」两层。
> 自包含、无私有依赖，可直接安装到 WorkBuddy 等 Agent skill 平台。脚本路径/配置按你的环境修改（见「配置修改」）。

---

## 开始之前：申请 API Key（必读）

本 skill 需配合 **FinTrust Skill Hub** 的 API Key 使用：

1. 前往 **https://fintrustskill.com/landing** 注册账号并申请 API Key
2. 配置环境变量：

```bash
export FINTRUST_API_KEY=你的Key
# 或写入 ~/.biopharma/.env（biopharma_tracker.py 运行时自动加载）
```

3. **模块级硬校验**：未配置 Key 时，无论命令行运行还是 `import` 库式调用都会被拒绝（退出码 2）并打印申请引导；配置后正常执行。

---

## 一、数据源总清单

### A. 基础分析层（6 源）— `scripts/biopharma_data.py`

分析生物医药公司「管线 / 审批 / 专利 / 文献」四大命门，全部官方免费源：

| # | 数据源 | 接口 | 稳定性 | 拿什么 |
|---|--------|------|--------|--------|
| 1 | ClinicalTrials.gov（NIH 全球临床） | `clinicaltrials.gov/api/v2/studies` | 高 | 全球试验阶段分布、适应症广度、NCT 状态 |
| 2 | FDA openFDA（美国审批+橙皮书） | `api.fda.gov` | 高 | FDA 批准记录 + 橙皮书成分/市场状态 |
| 3 | EMA EPAR（欧洲审批） | `ema.europa.eu` | 高 | 欧洲批准/适应症/治疗领域（带 7 天本地缓存） |
| 4 | PubMed（NCBI 文献） | `eutils.ncbi.nlm.nih.gov` | 高 | 最新临床数据首发地（ASCO/ASH、ORR/PFS/OS） |
| 5 | Google Patents（全球专利族） | `patents.google.com/xhr/query` | 中 | 专利到期、各国 active 状态（护城河） |
| 6 | NMPA 临床试验平台（中国临床） | `chinadrugtrials.org.cn` | 中 | 国内 CTR 编号/状态/适应症 |

调用入口（`biopharma_data_sources/biopharma_data.py`）：

```python
from biopharma_data_sources.biopharma_data import get_clinical_trials, get_fda_drug, get_ema_drugs, search_pubmed, get_patents
from biopharma_data_sources.nmpa_clinical_trials import search_clinical_trials  # NMPA 单独模块

get_clinical_trials("zanubrutinib")          # 全球临床
get_fda_drug("Brukinsa")                     # FDA 审批
get_ema_drugs("zanubrutinib")                # EMA 审批
search_pubmed("zanubrutinib lymphoma")       # 文献
get_patents("zanubrutinib")                  # 专利
search_clinical_trials("泽布替尼")            # 中国临床
```

### B. 上游追踪层（4 源）— `scripts/biopharma_tracker.py`

抢在「公司公告」前获知 BD / 管线审批进展，重点追踪 3 家港股创新药（康方/复宏汉霖/信达）：

| # | 数据源 | 接口 | 稳定性 | 时差价值 |
|---|--------|------|--------|----------|
| 7 | CDE 优先审评 + 突破性治疗 | `cde.org.cn` | 中 | 中国获批前哨，数月（仅做「催化剂日历」标记节点，非买入信号） |
| 8 | EMA CHMP 会议纪要 | `ema.europa.eu` | 高 | 欧盟获批前哨，4-7 天（可操作） |
| 9 | SEC 8-K（EDGAR full-text） | `efts.sec.gov` | 高 | 美股合作方先披露 BD/数据（康方合作方 Summit 美股有效） |
| 10 | 行业媒体 RSS（7 家） | 见下方 | 中 | BD 爆料，需合作方 8-K 交叉验证防假消息 |

行业媒体 RSS 清单：Endpoints / Fierce Biotech / Fierce Pharma / PharmaTimes / BioPharma Dive / STAT / GEN + Google News。

调用入口：

```bash
cd scripts
python -m biopharma_data_sources.biopharma_tracker --config ../configs/akeso_tracking_config.json   # 单公司
python -m biopharma_data_sources.biopharma_tracker --skip-cde                                        # 每日触发信号（跳过慢的 CDE）
python -m biopharma_data_sources.biopharma_tracker --only-cde                                        # 每周 CDE 催化剂日历
```

> 10 个数据源的完整元数据（URL / 稳定性 / 入口函数）已登记在 `source_universe.json`。

---

## 二、时差价值排序（关键认知）

**不是所有「更早知道」都有价值，只有对股价有重大影响的信息才值得追踪。**

| 信号 | 时差 | 可操作性 |
|------|------|----------|
| 学术会议摘要预披露 | 7-21 天 | ✅ 最理想 |
| FDA 批准（PDUFA 前） | 3-7 天 | ✅ 高 |
| EMA CHMP 会议纪要 | 4-7 天 | ✅ 高 |
| SEC 8-K（合作方披露） | 数小时-天 | ✅ 高 |
| CDE 优先审评 | 数月-1年 | ⚪ 仅标记节点 |

**方向判断靠「数据 vs 基准」**：会议摘要上线本身不告诉你涨跌，要看数据是否超预期/颠覆性（头对头战胜标准疗法 = 大涨，数据不及预期 = 暴跌）。

---

## 三、文件结构

```
biopharma-data-sources/
├── SKILL.md                           # skill 入口（frontmatter + 使用说明）
├── README.md                          # 本文件（完整文档）
├── source_universe.json               # 10 个数据源登记表
├── requirements.txt                   # Python 依赖
├── scripts/
│   └── biopharma_data_sources/        # 包命名空间（与 biopharma-strategy 隔离，可共存）
│       ├── __init__.py
│       ├── biopharma_data.py          # 基础分析 6 源入口
│       ├── biopharma_tracker.py       # 上游追踪 4 源入口
│       ├── nmpa_clinical_trials.py    # NMPA 爬虫（Playwright）
│       ├── cde_priority_collector.py  # CDE 爬虫（Playwright 绕反爬）
│       ├── news_materiality_filter.py # 重大性过滤（4 道门）
│       ├── task_guard.py              # Cron 稳定性框架（重试/锁/熔断，跨平台）
│       ├── fintrust_onboard.py        # FinTrust API Key 加载与硬校验
│       ├── pipeline_config.py         # 统一配置读取
│       └── pipeline_config.json       # 路径/超时配置（已脱敏精简）
├── configs/                           # 配置样例
│   ├── hk_biotech_watchlist.json      # 追踪清单（3 重点 + 7 备选）
│   ├── <公司>_tracking_config.json     # 每家公司管线/BD 合作方/关键词配置（10 份）
│   ├── biopharma_trial_calendar.json  # 试验日历（预期基准+判断框架）
│   └── biopharma_conference_calendar.json  # 学术会议日历（摘要上线日）
└── docs/
    └── event_impact_stats.md          # 事件类型影响力排行（实证）
```

---

## 四、依赖安装

```bash
pip install -r requirements.txt
playwright install chromium   # NMPA/CDE 爬虫需要
```

> 依赖仅 3 个：`requests`（HTTP）、`pandas`（EMA Excel 解析）、`playwright`（NMPA/CDE 反爬）。

---

## 五、配置修改（必读）

以下内容按你的环境修改：

1. **FinTrust API Key（必需，先做这一步）**
   - 前往 **https://fintrustskill.com/landing** 注册并申请 API Key
   - 配置环境变量 `FINTRUST_API_KEY`（或写入 `~/.biopharma/.env`，本 skill 自动加载）
   - 模块级硬校验：未配置时，CLI 运行与 `import` 调用均拒绝（exit code 2）并打印申请引导

2. **`scripts/pipeline_config.json`**
   - `paths.workspace_root` → 你的工作区根目录
   - `timeouts.*` → 各接口超时（可按需调整）
   - `alerts.telegram_target` / `alerts.email_default` → 你的推送目标

3. **推送密钥（环境变量，不落盘，可写入 `~/.biopharma/.env`）**
   - Telegram：`TELEGRAM_BOT_TOKEN` + `TELEGRAM_CHAT_ID`
   - 邮件（标准 SMTP）：`SMTP_HOST` / `SMTP_PORT`（默认 587）/ `SMTP_USER` / `SMTP_PASS` / `ALERT_EMAIL`
   - 无推送需求可跳过，脚本仍会输出命中结果到 stdout。

4. **追踪公司配置**：`configs/<公司>_tracking_config.json` 里的管线分子名/BD 合作方/关键词，按你要追踪的公司替换。

5. **本地缓存/状态目录**：默认写 `~/.cache/biopharma_data_sources/` 和 `~/.biopharma/data_sources/`（已按包命名空间隔离，与 `biopharma-strategy` 同机并跑互不干扰；可用环境变量 `BIOPHARMA_ROOT` 覆盖根目录）。

---

## 六、关键坑点（务必知道）

1. **NMPA / CDE 两个爬虫**用 Playwright，NMPA 需**有头模式**（headless 会被反爬检测），无 GUI 的服务器/cron 无头环境会失败。
2. **CDE 官网是瑞数级反爬**：requests 直接抓返回空页，必须 Playwright + 隐藏 `navigator.webdriver`，等 JS 挑战完成（约 6 秒）后填查询框。
3. **Google Patents 用非官方 xhr 接口**，stability=medium，失败可退回 web_search。
4. **SEC 8-K 只搜「公司英文名 + 创新药 INN」**：生物类似药 INN（trastuzumab/rituximab 等）是通用名，会命中几十家无关药企。
5. **EMA CHMP 关键词用英文**（name_en/brand_eu），且 INN 负向排除衍生药（trastuzumab 会误命中 Enhertu/Kadcyla 等 ADC）。
6. **行业媒体有假消息风险**，BD 爆料必须用合作方 8-K/官方披露交叉验证。
7. **重大性过滤四道门**（时间窗 72h → 主体相关性 → 噪音名单 → 重大性分级 → 事件聚类去重），只推三类：数据读出 / 监管批准拒批 / 并购授权带金额。
8. **重大信号是稀疏事件**（每家每月 1-2 次），多数日子静默属正常。
9. **文件锁依赖 `fcntl`**（`task_guard.py`），Unix/macOS 用排他锁，Windows 自动降级为无锁运行（跨平台安全）。

---

## 七、报告头部规范

分析报告头部必须标注：生成时间（UTC+8）+ 分析模型 + 数据源清单。

---

## 八、平台适配说明

- 本包为**自包含的独立 skill 目录**，仅依赖 `requests` / `pandas` / `playwright` 三个公开库，无任何私有依赖。
- 安装到 WorkBuddy 或其他 Agent skill 平台时，将整个目录放入平台的 skills 目录即可；`SKILL.md` 的 frontmatter 已符合通用 skill 规范（name / description / version / display_name / visibility）。
- 新闻标题中文翻译为可选增强：如需接入，自行实现 `translate_batch` 并在 `biopharma_tracker.py` 的 `_translate_hits` 中调用；未接入时脚本自动输出原文标题，不影响数据采集。

---

*发布版本：v1.1.0 · 星财富（复星财富）· 数据源均已登记 `source_universe.json`（本包内含）*
