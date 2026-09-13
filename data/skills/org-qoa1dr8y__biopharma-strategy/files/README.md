# 生物医药投研策略 Skill（Biopharma Strategy）

> **星财富（复星财富）出品** · 港股/美股生物医药公司完整投研策略方法论，含 **四步分析法**、**BD/审批"早于公告"上游追踪 SOP**、**重大性过滤**、**新公司接入模板**、**事件影响实证库**。
> 自包含、无私有依赖，可直接安装到 WorkBuddy 等 Agent skill 平台。脚本路径/配置按你的环境修改（见「配置修改」）。

---

## 开始之前：申请 API Key（必读）

本 skill 需配合 **FinTrust Skill Hub** 的 API Key 使用：

1. 前往 **https://fintrustskill.com/landing** 注册账号并申请 API Key
2. 配置环境变量：

```bash
export FINTRUST_API_KEY=你的Key
# 或写入 ~/.biopharma/.env（脚本运行时自动加载）
```

3. **模块级硬校验**：未配置 Key 时，无论命令行运行还是 `import` 库式调用都会被拒绝（退出码 2）并打印申请引导；配置后正常执行。

---

## 一、策略总览

### 核心认知

1. **价值核心不在财务，而在「管线 + 临床 + 专利 + 监管」**，财务（SEC/HKEX）是辅助。
2. **不是所有"更早知道"都有价值**，只有对股价有重大影响的信息才值得追踪。
3. **判断追踪价值，先看有没有重磅创新药**（first-in-class/大适应症），而非一刀切。

### 分析流程（四步法）

| 步骤 | 目标 | 调用 | 判断 |
|------|------|------|------|
| 1. 管线盘点 | 能力核心 | `get_clinical_trials` + `search_clinical_trials` | III 期数量 = 近期价值；适应症覆盖 = 长期空间 |
| 2. 审批与催化剂 | 潜力 | `get_fda_drug` + `get_ema_drugs` | 已获批市场、突破性/孤儿药/优先审评资格 |
| 3. 专利护城河 | 持续性 | `get_patents` + `get_fda_orange_book` | 专利到期、仿制冲击时间 |
| 4. 文献与临床数据 | 最新信号 | `search_pubmed` | 最新 ORR/PFS/OS、安全性、头对头优效 |

---

## 二、上游追踪方法论（核心）

### 时差价值排序

**不是所有「更早知道」都有价值，只有对股价有重大影响的信息才值得追踪。**

| 信号 | 时差 | 可操作性 |
|------|------|----------|
| 学术会议摘要预披露 | 7-21 天 | ✅ 最理想 |
| FDA 批准（PDUFA 前） | 3-7 天 | ✅ 高 |
| EMA CHMP 会议纪要 | 4-7 天 | ✅ 高 |
| SEC 8-K（合作方披露） | 数小时-天 | ✅ 高 |
| CDE 优先审评 | 数月-1年 | ⚪ 仅标记节点 |

### 方向判断

**工具抓"时点"，判断"方向"靠「数据 vs 基准」——不能预测方向。**

- 数据读出时，瞬间对比实际 ORR/PFS/OS vs 同类基准：超预期（涨）/ 颠覆性头对头（大涨）/ 不及预期（跌）
- 会议摘要预披露是双向的（康方 HARMONi-A 摘要跌 20%，HARMONi-2 涨 37.5%）

### 重大性过滤（`scripts/biopharma_strategy/news_materiality_filter.py`）

四道门：时间窗 72h → 主体相关性 → 噪音名单 → 重大性分级 → 事件聚类去重。

只推三类：

| 类别 | 判据 |
|------|------|
| 📊 数据读出 | 关键临床数据、主要终点达成/失败、揭盲、OS/PFS |
| 🏛️ 监管批准/拒批 | NMPA/FDA/EMA 批准、拒批、CRL、临床暂停、撤回、PDUFA |
| 💰 并购/授权带金额 | 交易词 + 明确金额（$500M / 首付款 等） |

**重大信号是稀疏事件**（每家每月 1-2 次），多数日子静默属正常。

---

## 三、新公司接入 SOP（4 步）

1. **盘点管线**：从年报/官网/招股书整理管线分子（中英文名+商品名+代号）和 BD 合作方
2. **建配置**：复制 `templates/tracking_config_template.json` → `<公司英文名>_tracking_config.json`，填入管线/合作方/关键词
3. **建 cron**：`python -m biopharma_strategy.biopharma_tracker --config <配置>`，每日 2 次（盘中+盘后）
4. **验证**：跑一次 dry-run，确认关键词能命中 EMA CHMP 等源

---

## 四、文件结构

```
biopharma-strategy/
├── SKILL.md                           # skill 入口（frontmatter + 策略方法论）
├── README.md                          # 本文件（完整文档）
├── source_universe.json               # 10 个数据源登记表
├── requirements.txt                   # Python 依赖
├── scripts/
│   └── biopharma_strategy/            # 包命名空间（与 biopharma-data-sources 隔离，可共存）
│       ├── __init__.py
│       ├── biopharma_data.py          # 基础分析 6 源入口
│       ├── biopharma_tracker.py       # 上游追踪 4 源入口
│       ├── nmpa_clinical_trials.py    # NMPA 爬虫（Playwright）
│       ├── cde_priority_collector.py  # CDE 爬虫（Playwright 绕反爬）
│       ├── news_materiality_filter.py # 重大性过滤（4 道门）
│       ├── task_guard.py              # Cron 稳定性框架（重试/锁/熔断，跨平台）
│       ├── fintrust_onboard.py        # FinTrust API Key 引导与硬校验
│       ├── pipeline_config.py         # 统一配置读取
│       └── pipeline_config.json       # 路径/超时配置（已脱敏精简）
├── configs/                           # 配置样例
│   ├── hk_biotech_watchlist.json      # 追踪清单（3 重点 + 7 备选）
│   ├── <公司>_tracking_config.json     # 每家公司管线/BD 合作方/关键词配置（10 份）
│   ├── biopharma_trial_calendar.json  # 试验日历（预期基准+判断框架）
│   └── biopharma_conference_calendar.json  # 学术会议日历（摘要上线日）
├── templates/
│   └── tracking_config_template.json  # 新公司接入配置模板（核心资产）
└── references/
    ├── data-sources.md                # 10 源详细文档（接口/字段/缓存/坑点）
    └── event-impact-stats.md          # 事件类型影响力排行（实证）
```

---

## 五、依赖安装

```bash
pip install -r requirements.txt
playwright install chromium   # NMPA/CDE 爬虫需要
```

> 依赖仅 3 个：`requests`（HTTP）、`pandas`（EMA Excel 解析）、`playwright`（NMPA/CDE 反爬）。

---

## 六、配置修改（必读）

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

4. **追踪公司配置**：`configs/<公司>_tracking_config.json` 里的管线分子名/BD 合作方/关键词，按你要追踪的公司替换（模板见 `templates/tracking_config_template.json`）。

5. **本地缓存/状态目录**：默认写 `~/.cache/biopharma_strategy/` 和 `~/.biopharma/strategy/`（已按包命名空间隔离，与 `biopharma-data-sources` 同机并跑互不干扰；可用环境变量 `BIOPHARMA_ROOT` 覆盖根目录）。

---

## 七、关键坑点（务必知道）

1. **NMPA / CDE 两个爬虫**用 Playwright，NMPA 需**有头模式**（headless 会被反爬检测），无 GUI 的服务器/cron 无头环境会失败。
2. **CDE 官网是瑞数级反爬**：requests 直接抓返回空页，必须 Playwright + 隐藏 `navigator.webdriver`，等 JS 挑战完成（约 6 秒）后填查询框。
3. **Google Patents 用非官方 xhr 接口**，stability=medium，失败可退回 web_search。
4. **SEC 8-K 只搜「公司英文名 + 创新药 INN」**：生物类似药 INN（trastuzumab/rituximab 等）是通用名，会命中几十家无关药企。
5. **EMA CHMP 关键词用英文**（name_en/brand_eu），且 INN 负向排除衍生药（trastuzumab 会误命中 Enhertu/Kadcyla 等 ADC）。
6. **行业媒体有假消息风险**，BD 爆料必须用合作方 8-K/官方披露交叉验证。
7. **重大性过滤四道门**（时间窗 72h → 主体相关性 → 噪音名单 → 重大性分级 → 事件聚类去重），只推三类：数据读出 / 监管批准拒批 / 并购授权带金额。
8. **重大信号是稀疏事件**（每家每月 1-2 次），多数日子静默属正常。
9. **已跨平台兼容**：`task_guard.py` 的文件锁（`fcntl`）与超时（`signal.SIGALRM`）在 Windows 上自动降级为「无锁 + 无超时」运行，不影响数据采集；macOS/Linux 保留完整的文件锁 + 超时能力。

---

## 八、报告头部规范

分析报告头部必须标注：生成时间（UTC+8）+ 分析模型 + 数据源清单。

---

## 九、平台适配说明

- 本包为**自包含的独立 skill 目录**，仅依赖 `requests` / `pandas` / `playwright` 三个公开库，无任何私有依赖。
- 安装到 WorkBuddy 或其他 Agent skill 平台时，将整个目录放入平台的 skills 目录即可；`SKILL.md` 的 frontmatter 已符合通用 skill 规范（name / description / version / display_name / visibility）。
- 新闻标题中文翻译为可选增强：如需接入，自行实现 `translate_batch` 并在 `biopharma_tracker.py` 的 `_translate_hits` 中调用；未接入时脚本自动输出原文标题，不影响数据采集。

---

*发布版本：v1.1.0 · 星财富（复星财富）· 数据源均已登记 `source_universe.json`（本包内含）*
