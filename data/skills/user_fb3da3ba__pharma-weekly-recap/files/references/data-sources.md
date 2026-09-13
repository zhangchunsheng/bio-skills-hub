# 数据源映射与降级策略

原规格文档中的 `doc_searcher` / `data_analyst` / `search_paipai` / `analyst_report` 均为外部平台专属能力，
在本机不存在。本文件定义它们在 WorkBuddy 中的等价实现与降级顺序。

## 调用节奏（重要，2026-09-12 实测）

`mx-ds-mcp` 有频率限制，**同一批并发发起 3~4 个 MCP 调用会返回「操作过于频繁」**。
实测稳定做法是**每批最多 2 个并行 MCP 调用**，逐批推进（A/B → C/D → E）。
失败的调用直接原样重试即可，通常第二次成功。

## 总原则：MCP 优先，联网兜底

每一路采集按以下顺序尝试，成功即停；前一级失败或返回空，才进入下一级：

1. **已连接的金融数据 MCP**（进门投研 `comein-mcp-all`、东方财富妙想 `mx-ds-mcp`）
2. **联网检索**（`WebSearch` / `WebFetch`）
3. **判定为无数据** —— 在该模块下如实写「本周无相关信息」，**禁止编造**

任何一级返回的结果，都必须落盘为中间文件，再交给 Step 3 汇总。

## 行业范围（全局筛选口径）

申万一级行业 **医药生物**，含以下子行业与主题：

- 申万二级：化学制药、中药Ⅱ、生物制品、医药商业、医疗器械、医疗服务
- 常见主题：CXO/CRO/CDMO、创新药、仿制药、疫苗、血制品、体外诊断(IVD)、高值耗材、
  医疗设备、原料药、医美、连锁药店、互联网医疗、中药配方颗粒、基因测序、GLP-1/减重产业链

跨行业公司（如做医美的化工股）**不纳入**，除非其医药业务收入占比 > 50%。

## 路径 A：本周卖方深度报告

| 级别 | 工具 | 调用要点 |
|---|---|---|
| 1 | `mcp__comein-mcp-all__searchDomesticReports` | `query` 用完整自然语言，如「创新药出海授权对行业估值的影响 医药生物行业深度研究」；`start_time={monday}`；`topK=50`；`filterImage=true` |
| 2 | `mcp__mx-ds-mcp__mx_finance_search_news` | `query` 写明「医药生物 行业 深度研报 {monday} 至 {friday}」 |
| 3 | `WebSearch` | 查询式：`医药生物 券商 深度报告 {monday}..{friday} site:research.*`、`首次覆盖 医药 研报 {monday}` 等 |

> **页数 ≥ 15 是唯一硬性筛选条件。** 大量高质量深度报告（首次覆盖、专题研究、行业复盘）
> 标题里并不含「深度」二字，**严禁把「深度」当正向筛选词**，否则会造成系统性遗漏。
>
> MCP 结果通常不直接给页数字段，按以下方式判定：
> 1. 若返回体含 `page` / `page_count` 字段 → 直接比较；
> 2. 若无页数字段 → 用 `get_stock_kline` 无关，改用**正文片段长度 + 报告类型**推断：
>    摘要/正文超过约 800 字、或标注为「公司深度」「行业专题」「首次覆盖」的，视为深度；
> 3. 仍无法判定的，**保留并在报告中标注「页数未知」**，不要直接丢弃。

**排除类型**（命中任一即剔除）：点评、简评、快评、周报、日报、晨报、数据跟踪、行业动态、
会议纪要、业绩预览（篇幅 < 15 页时）。

返回字段：`title` / `date` / `institution` / `stock_name` / `stock_code` / `page_count` / `content`(≤200字)。
最多 30 条，按日期降序。落盘 `01_deep_reports.md`。

## 路径 B：新推荐 / 首次覆盖

| 级别 | 工具 | 调用要点 |
|---|---|---|
| 1 | `mcp__comein-mcp-all__searchDomesticReports` | `query` 聚焦「首次覆盖 首次评级 首次推荐 评级上调 目标价上调 医药」，可拆成 3 个子 query 分别检索 |
| 2 | `mcp__mx-ds-mcp__mx_finance_search_news` | `query` 同上，附时间范围 |
| 3 | `WebSearch` | `医药 首次覆盖 {monday}..{friday}`、`医药 评级上调 目标价上调 {monday}` |

**优先级排序**：首次覆盖 > 评级上调 > 目标价上调 > 维持评级重申推荐。
返回字段：`title` / `date` / `institution` / `stock_name` / `stock_code` / `rating` / `target_price` / `content`。
最多 30 条，按日期降序。落盘 `02_new_coverage.md`。

## 路径 C：增减持 / 回购 / 股权激励公告

| 级别 | 工具 | 调用要点 |
|---|---|---|
| 1 | `mcp__comein-mcp-all__searchAnnouncementReport` | `query` 用多个 15~20 字独立子问题空格分隔，如「股东增持计划 减持预披露 权益变动」；`topK=50`。**公司名称用 `fullCode` 指定，不要写进 query** |
| 2 | `mcp__mx-ds-mcp__mx_finance_search_notice` | `query` 写明公告类型 + 时间范围，如「医药生物 上市公司 增持 减持 回购 股权激励 公告 {monday} 至 {friday}」 |
| 3 | `WebSearch` | `医药 回购公告 {monday}..{friday}`、`医药 股权激励 限制性股票 {monday}` 等 |

三类分头检索，每类最多 20 条：

1. **股东增减持**：增持、减持、权益变动、持股变动、增持计划、减持预披露
2. **回购**：回购、回购进展、回购实施、回购方案
3. **股权激励**：股权激励、限制性股票、股票期权、员工持股计划

返回字段：`title` / `date` / `stock_name` / `stock_code` / `category` / `content`。
落盘 `03_announcements.md`。

## 路径 D：周涨跌幅 Top10

| 级别 | 工具 | 调用要点 |
|---|---|---|
| 1 | `mcp__comein-mcp-all__screenerStock` | `enumConditions=[{key:"marketType",values:["sh","sz","bj"]}]`；`sort=[{field:"changePctWeek",order:"desc"}]`；`size=100`；`page=1`。再从结果中筛出医药生物个股取前 10；跌幅榜把 `order` 改成 `asc` |
| 2 | `mcp__mx-ds-mcp__mx_stocks_screener` | 自然语言：`申万医药生物行业 A股 本周（{monday} 至 {friday}）涨跌幅前10名 含股票代码 名称 周涨跌幅 所属三级行业` |
| 3 | `WebSearch` + `WebFetch` | 搜索「申万医药生物 周涨跌幅 排行 {monday}」，抓取行情站点页面 |

> **口径必须写清楚**：周涨跌幅 = `{friday}` 收盘价相对 `{prev_friday}` 收盘价的变动。
> `screenerStock` 的 `changePctWeek` 是「近一周」滚动口径，与「本周一至周五」可能不一致；
> 采用它时需在报告中注明口径，或对 Top10 个股用 `get_stock_kline`
> （`freq="1d"`，`startDateTime={prev_friday}`，`endDateTime={friday}`）手工复核。
>
> `concept` 枚举值不保证包含「医药生物」。若 concept 过滤返回空，**退回按结果人工筛行业**，
> 不要因此判定为无数据。
>
> **实测技巧（2026-09-12）**：用自然语言问句并写明起止日期，例如
> 「申万医药生物行业 A股 2026年9月7日至2026年9月11日 本周涨跌幅前10名 含股票代码、股票名称、周涨跌幅、所属细分行业」，
> 返回体会直接带 `区间涨跌幅(%)-{monday} - {friday}` 列（跌幅榜追加「区间涨跌幅升序」即可），
> 且已按申万医药生物过滤好，并附 `申万行业分类` 三级分类字段。
> 这种情况下**口径与周报定义天然一致，无需再用 kline 手工复核**，可直接落 CSV。
> 返回体同时含总市值、换手率、市盈率、量比等，写「异动点评」时可直接引用。

输出四列：`股票代码` / `股票名称` / `周涨跌幅(%)` / `所属申万三级行业`。落盘 `04_top_movers.csv`。

## 路径 E：涨跌原因（依赖路径 D 结果）

对路径 D 得到的涨幅前 10 + 跌幅前 10，逐只检索本周消息面：

| 级别 | 工具 | 调用要点 |
|---|---|---|
| 1 | `mcp__mx-ds-mcp__mx_finance_search_news` | `query` = `{股票名} {monday} 至 {friday} 上涨/下跌 原因 点评` |
| 1 | `mcp__comein-mcp-all__searchAnnouncementReport` | 用 `fullCode` 定位个股，查本周是否有重大公告 |
| 2 | `WebSearch` | `{股票名} 本周 涨停 大跌 原因 {monday}`，可带 `topic="finance"` |

**多源交叉验证**：同一只股票的原因需至少 2 个独立来源支持才能写入报告；
只有单一来源的，标注「据 XX 报道」；查不到原因的，写「本周未检索到明确催化事件」，**不要臆测**。

落盘 `05_movers_reasons.md`。

## 并发执行约定

路径 A、B、C、D 四条互不依赖，用 Agent 工具**在同一条消息里发起多个调用**实现并发，
每条 `run_in_background` 视负载决定。路径 E 必须等路径 D 产出 Top10 之后才能开始。

子 agent 的产出统一写到 `tmp/{session_id}/` 下，命名固定为
`01_deep_reports.md` / `02_new_coverage.md` / `03_announcements.md` /
`04_top_movers.csv` / `05_movers_reasons.md`，避免汇总阶段再去找文件。
