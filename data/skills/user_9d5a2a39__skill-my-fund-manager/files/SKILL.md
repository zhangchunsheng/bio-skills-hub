---
name: my-fund-manager
description: >
  全市场基金经理投资风格蒸馏与复刻工具。覆盖公募（东方财富4273+人）+ 私募（AMAC 24万+产品），
  支持配置最多100名基金经理，自动蒸馏投资风格DNA，以经理口吻答疑，复刻投资策略，导出结构化数据。
  内置2025-2026知名基金经理种子库（80位，公募明星/私募百亿/QDII海外/当红经理四分类）一键导入。
  支持智能增量更新（规模/重仓/季报/业绩四维度变化检测）+ 全量更新 + 过期更新三种维护模式。
  两级蒸馏引擎自动fallback：对话LLM -> 规则引擎。
  v2.0.0 新增三大能力层：言论指纹+观点时序+对话记忆 / 能力评分+业绩归因+风险指标 /
  风格雷达+漂移检测+同风格聚类+季度调仓追踪。每个经理的言论/能力/风格多维量化建模。
  触发词："配置基金经理""蒸馏经理观点""重仓股""经理业绩""名单维护""导出表格"
  "更新数据""基金经理问答""复制投资策略""张坤怎么样""萧楠最近看什么""季报说人话"
  "跟踪经理""忘记经理""我的基金经理""模仿XX配置""基金经理风格""十大重仓"
  "私募基金经理""高毅资产""AMAC搜索""私募管理人""专户经理""QDII经理"
  "导入知名经理""种子库""智能更新""增量维护""2025当红经理"
  "言论风格""观点历史""他说过啥""立场漂移""问答历史""能力评分""业绩归因"
  "风险调整收益""夏普比率""最大回撤""风格雷达""风格漂移""风格相似""换手率"
  "调仓""季度变化"。
version: 2.1.0
updated: 2026-08-23
---

# 我的基金经理 Skill

> 🎯 全市场基金经理投资风格蒸馏与复刻工具（v2.1.0 稳定性升级）
>
> 覆盖公募4273+人（东方财富）+ 私募24万+产品（AMAC），配置最多100名经理，
> 自动蒸馏投资风格DNA -> 第一人称答疑 -> 策略复刻 -> 表格导出 -> 定期刷新。
> **v2.0.0 新增**言论能力/投资能力/投资风格三大能力层，多维量化建模每个经理。
> **v2.1.0** 修复风险指标准确性、余弦判别力、KMeans 稳定性等 8 处缺陷，189 测试全通过。
> 内置2025-2026知名经理种子库（80位）一键导入，支持智能增量更新。

<!-- DATA_STATS_START -->
- 已蒸馏基金经理：58/100 人
- 最后更新：2026-07-29 16:50
- 数据来源：东方财富/天天基金
<!-- DATA_STATS_END -->

---

## Step 1: 环境检测

运行前自动检测依赖和数据源，缺什么装什么，零配置启动。

```
!`python -c "import requests; print('requests OK')" 2>/dev/null || echo "REQUESTS_MISSING"`
```
```
!`python -c "import openpyxl; print('openpyxl OK')" 2>/dev/null || echo "OPENPYXL_MISSING"`
```
```
!`python -c "import urllib.request; urllib.request.urlopen('https://fundf10.eastmoney.com/', timeout=5); print('EASTMONEY_OK')" 2>/dev/null || echo "EASTMONEY_UNREACHABLE"`
```

**决策树：**

| 检测项 | 状态 | 行为 |
|--------|------|------|
| requests | MISSING → 自动 `pip install -q requests`；失败则用 urllib fallback |
| openpyxl | MISSING → 导出时自动安装；失败则用 CSV（标准库） |
| 东方财富 | UNREACHABLE → 提示检查网络；仅用已缓存数据 |

**Skill 根目录定位：** 所有脚本位于 `scripts/` 子目录。运行时先 `cd` 到 skill 根目录（含 SKILL.md 的目录），或用绝对路径。

---

## Step 2: 路由

根据用户意图选择子流程。

| 用户意图 | 路由到 | 典型示例 |
|---------|--------|---------|
| 配置/新增/删除/查看经理 | **Sub-A** | "跟踪张坤""忘记萧楠""我的基金经理名单""添加高毅资产""私募经理" |
| 导入2025-2026知名经理种子库 | **Sub-A 种子库** | "导入知名经理""种子库""导入公募明星""导入高毅资产邓晓峰" |
| 蒸馏/答疑/复制策略/定制产品 | **Sub-B** | "蒸馏经理观点""张坤怎么投资的""模仿张坤配置""经理问答" |
| 重仓/业绩/投资范围 | **Sub-C** | "张坤十大重仓""经理业绩""重仓了哪些债券""投资范围" |
| 导出表格 | **Sub-D** | "导出名单""导出Excel""重仓信息表格""导出CSV" |
| 全量更新/刷新数据 | **Step 3** | "更新数据""刷新经理""定期更新""数据过期了" |
| 智能增量更新（变化检测） | **Step 3 智能更新** | "智能更新""增量维护""只更新变化的""smart_update" |
| 言论能力（指纹/时序/对话记忆） | **Sub-E** | "言论风格""口头禅""观点历史""他说过啥""立场漂移""问答历史" |
| 投资能力（评分/归因/风险） | **Sub-F** | "能力评分""业绩归因""风险调整收益""夏普比率""最大回撤""雷达图" |
| 投资风格（雷达/漂移/聚类/调仓） | **Sub-G** | "风格雷达""风格漂移""风格相似""换手率""调仓""季度变化" |
| 模糊或不确定 | **默认 Sub-B** | - |

**共享默认值：**

| 参数 | 默认值 | 理由 |
|------|--------|------|
| 经理上限 | 100 人 | 用户要求扩容（原50人） |
| 种子库容量 | 80 位知名经理 | 4分类：公募明星30/私募百亿20/QDII海外15/当红15，留20名额给用户自定义 |
| 数据源 | 东方财富公开数据 + AMAC私募 | 无需Key，覆盖全市场4273+公募+24万+私募产品 |
| 蒸馏引擎 | auto（对话LLM->规则） | 两级fallback保证可用 |
| 报告期 | 最新一期 | 用户关心当前状态 |
| 重仓聚合 | 跨所有产品去重排序 | 完整反映投资特点 |
| 导出格式 | auto（Excel优先，CSV fallback） | 最大化兼容 |
| 索引缓存 | 7天 | 平衡新鲜度和性能 |
| 并发数 | 8 | 抓取效率与反爬平衡 |
| 默认更新模式 | smart_update（智能增量） | 变化检测省时省流量，只对有变化的经理蒸馏 |

---

## Sub-Skill A: 经理配置与名单维护

**Goal:** 搜索基金经理 -> 反问确认 -> 添加/删除/查看名单（上限100人）。支持知名经理种子库一键导入。

**双源搜索，自动标注类型：**
- 🏆 **公募**：东方财富全市场4273+人（含QDII），按姓名/产品/公司搜索
- 📈 **私募**：AMAC 24万+只产品，按管理人名/基金产品名搜索
- 结果按匹配度排序，自动区分公募/私募

1. **搜索：** 用户提供姓名/产品/公司/管理人名 -> 运行 `python scripts/manager_search.py "<关键词>" [name/product/company/auto]`
   - 公募首次使用自动构建索引（约20秒），缓存7天
   - 私募通过AMAC API实时搜索（POST请求，无需Key）
2. **反问确认：** 若多个匹配 -> 展示候选列表（序号+类型标签+姓名+公司+产品+回报），请用户选择序号确认
3. **添加：** `python scripts/roster_manager.py add <ID> <姓名> <公司>` -> 校验上限100、去重
   - 公募ID：数字（如30189744）；私募ID：amac_前缀（如amac_101000002641）
4. **删除：** `python scripts/roster_manager.py remove <ID或姓名>`
5. **查看：** `python scripts/roster_manager.py list`

**反问规则：** 无法确认唯一经理时，必须反问。提示用户提供更准确的姓名/基金代码/产品名/管理人名。

**私募搜索注意：** AMAC搜索的是基金产品名和管理人名，非基金经理个人名。若用户提供私募基金经理个人名（如"邓晓峰"）未匹配，提示其提供管理人名称（如"高毅资产"）。

### Sub-A 种子库：2025-2026 知名基金经理一键导入

**Goal:** 从内置种子库（80位知名经理）一键导入到名单，免去逐个搜索的繁琐。

**种子库覆盖（`data/famous_managers_2025_2026.json`）：**

| 分类 | 数量 | 代表经理 | 标签特征 |
|------|------|---------|---------|
| 🏆 公募明星 | 30位 | 张坤、萧楠、刘彦春、葛兰、蔡嵩松、朱少醒、傅鹏博、谢治宇、丘栋荣、鲍无可 | 长青公募，价值/成长/均衡各风格 |
| 📈 私募百亿 | 20位 | 邓晓峰、冯柳、赵军、但斌、林园、裘国根、杨振宁、王亚伟 | 百亿私募管理人，价值/逆向/量化 |
| 🌍 QDII海外 | 15位 | 李彦、张金涛、许之彦、柳军、曹璐迪、劳杰男 | QDII/海外基金，美股/港股/黄金/债券 |
| 🔥 当红经理 | 15位 | 张城阳(AI)、韩创(价值周期)、冯明远(科技)、胡剑(债券)、赵蓓(医药) | 2025-2026当红主题经理 |

**命令：**
```bash
python scripts/famous_manager_importer.py list                       # 列出全部种子经理(按分类)
python scripts/famous_manager_importer.py list <分类>                # 列出某分类(公募明星/私募百亿/QDII海外/当红经理)
python scripts/famous_manager_importer.py import_all                 # 一键导入全部(受100人上限约束)
python scripts/famous_manager_importer.py import_category <分类>     # 按分类导入
python scripts/famous_manager_importer.py import_one <姓名>          # 导入单位经理
python scripts/famous_manager_importer.py import_and_fetch <姓名>    # 导入并立即抓取+蒸馏(新增维护)
```

**导入逻辑：**
1. 读种子条目，若 `id` 已预填则直接用，否则调 `manager_search` 按姓名+公司自动补全ID
2. 调 `roster_manager.add_manager()` 加入名单（自动校验100人上限、去重）
3. 私募经理通过 AMAC 搜索管理人名补全ID
4. 导入后可用 `import_and_fetch` 立即抓取重仓/策略/业绩+蒸馏，等价于「新增维护」

**导入后抓取全量数据：**
```bash
# 导入后对全部经理执行智能增量更新（首次会全部视为变化）
python scripts/monthly_updater.py smart_update
```

---

## Sub-Skill B: 风格蒸馏与答疑

**Goal:** 蒸馏投资风格DNA → 第一人称口吻答疑 → 复刻投资策略。

### B1. 一站式数据抓取
```bash
python scripts/monthly_updater.py update_one <经理ID> auto
```
自动完成：重仓抓取 → 投资策略 → 业绩数据 → 风格蒸馏，全程无需手动干预。

### B2. 蒸馏投资风格
两级 fallback 引擎，自动选择最佳可用（完整 prompt 见 `references/distill-prompts.md`）：

| 优先级 | 引擎 | 命令 | 依赖 |
|--------|------|------|------|
| ① | 对话LLM | `distill_manager.py task <ID>` → agent执行 → `apply_distill_result` 写回 | 零安装 |
| ② | 规则引擎 | `distill_manager.py distill <ID> rules` | 零依赖 |

- **引擎检测：** `python scripts/distill_manager.py detect`
- **规则引擎输出：** 风格码（如 `GROWTH-MED_POS-SECTOR_CONCENTRATED-LOW_TURNOVER-HK_STOCK`）+ 擅长领域 + 季报人话摘要

### B3. 经理口吻答疑
基于蒸馏档案（bio + style_dna + viewpoint_human + top_holdings），以经理第一人称口吻回答投资问题。System prompt 见 `references/distill-prompts.md` 第三节。

### B4. 策略复刻与产品定制
基于风格DNA + 重仓数据，为用户量身定制投资组合：
- 提取行业偏好、持仓集中度、风格标签
- 按用户风险偏好和资金量生成配置方案
- 自动标注"基于XX经理风格的参考配置，不构成投资建议"

---

## Sub-Skill C: 重仓与业绩

**Goal:** 十大重仓（股票/债券/基金）+ 历史业绩 + 投资策略 + 季报公告。

| 数据 | 命令 |
|------|------|
| 十大重仓（经理维度） | `python scripts/fetch_holdings.py manager <经理ID>` |
| 十大重仓（单基金） | `python scripts/fetch_holdings.py fund <基金代码> [stock/bond/fund]` |
| 投资策略与范围 | `python scripts/fetch_reports.py strategy <基金代码>` |
| 业绩数据 | `python scripts/fetch_performance.py fund <基金代码>` |
| 最新季报（含PDF） | `python scripts/fetch_reports.py latest <基金代码>` |
| 公告列表 | `python scripts/fetch_reports.py announce <基金代码>` |

**数据呈现：** 重仓按总占比排序，显示股票名/代码/占比/出现次数/覆盖基金数；业绩显示近1月/3月/6月/1年/3年/今年以来收益率，成立不足3年自动标注。

---

## Sub-Skill D: 表格导出

**Goal:** 一键导出名单/风格/重仓/业绩，Excel 或 CSV 自适应。

```bash
python scripts/export_table.py auto     # 自动选择（Excel优先，CSV fallback）
python scripts/export_table.py excel    # 强制 Excel（4个sheet）
python scripts/export_table.py csv      # 强制 CSV（3个文件）
```

**Excel 4个Sheet：**
1. 基金经理名单（姓名/公司/状态/风格标签/任职回报）
2. 投资风格（bio/擅长领域/风格码/思维DNA/季报观点）
3. 十大重仓（代码/名称/总占比/出现次数/持股数/市值）
4. 业绩数据（近1月/3月/6月/1年/3年/今年以来/管理费率）

---

## Step 3: 定期更新与自我迭代

**Goal:** 批量刷新数据，自动 bump 版本号，保持知识库常新。支持三种更新模式 + 新增维护。

### 三种更新模式对比

| 模式 | 命令 | 适用场景 | 耗时 | 蒸馏范围 |
|------|------|---------|------|---------|
| 🎯 智能增量（推荐） | `smart_update` | 日常定期维护 | 最短 | 仅变化经理 |
| 📦 全量更新 | `update_all` | 季度末大刷新/首次初始化 | 最长 | 全部经理 |
| ⏰ 过期更新 | `stale [天数]` | 按时间阈值兜底 | 中等 | 过期经理 |

### 智能增量更新（smart_update）—— 变化检测四维度

对名单中每位经理，抓取最新数据并与存档对比，**只对有变化的经理执行蒸馏**，无变化的仅刷新时间戳。变化日志写入 `data/change_log/YYYY-MM-DD.json`。

| 检测维度 | 阈值 | 说明 |
|---------|------|------|
| 规模变化 | ±10% | 管理规模显著变动（申购/赎回/业绩） |
| 重仓变化 | 新增/退出≥1只 或 占比变动≥3% | 持仓调整反映投资观点变化 |
| 新季报 | 报告期日期更新 | 季度报告发布（持仓/策略/观点） |
| 业绩变化 | 近1年收益率±5% | 业绩显著波动 |

**新鲜阈值：** 在 `days_threshold`（默认7天）内已刷新的经理跳过抓取，避免重复劳动。

```bash
python scripts/monthly_updater.py smart_update           # 智能增量更新（默认7天新鲜阈值）
python scripts/monthly_updater.py smart_update 14        # 14天内已刷新的跳过
```

**首次运行说明：** smart_update 首次运行时，所有经理都无"上次状态"可对比，会全部视为变化，等价于全量更新。后续运行才会真正增量。

### 全量更新（update_all）
```bash
python scripts/monthly_updater.py update_all auto       # 更新全部经理（含蒸馏）
python scripts/monthly_updater.py stale 30              # 仅更新 >30天 的过期数据
```

### 新增维护 vs 增量维护

| 维护类型 | 场景 | 命令 |
|---------|------|------|
| 🆕 新增维护 | 把新经理加入名单并初始化档案 | `famous_manager_importer.py import_and_fetch <姓名>` 或 `roster_manager.py add` + `monthly_updater.py update_one <ID>` |
| 🔄 增量维护 | 对名单中已有经理定期刷新 | `monthly_updater.py smart_update`（智能）或 `update_all`（全量） |

### 定时任务
- **ZCode：** 用户说"设置每月定时更新" -> `CronCreate` 创建 `0 9 1 * *`（每月1日9点），默认执行 `smart_update`
- **其他环境：** `python scripts/monthly_updater.py schedule` 查看设置说明（含 Linux crontab / Windows 任务计划示例）

### 自我迭代
每次更新完成后自动执行：
1. `version` 小版本号 +1
2. `updated` 日期刷新
3. `<!-- DATA_STATS_START -->` 统计区块同步更新（含 count/100）

**v2.0.0 自动快照：** `update_single_manager` 完成后自动调用 `_post_update_hooks`：

- 持仓快照 → `data/track_records/{id}.jsonl`
- 观点时序 → `data/viewpoints_history/{id}.jsonl`
- 风格雷达 → `data/style_history/{id}.jsonl`
- 能力评分/归因/风险/言论指纹 → 写回 `managers/{id}.json`

任一 hook 失败不影响其他 hook。

---

## Sub-Skill E: 言论能力（v2.0.0 新增）

**Goal:** 把每位经理的言论量化成 6 维指纹 + 时序观点 + 对话记忆，让 skill 能"听懂"经理在说什么、立场是否漂移、之前讨论过什么。

| 数据 | 命令 |
|------|------|
| 言论指纹（句长/第一人称密度/数据驱动/确定性） | `python scripts/speech_fingerprint.py <经理ID> --save` |
| 观点时序记录 | `python scripts/viewpoint_tracker.py record <经理ID> --date YYYY-MM-DD --text "..."` |
| 查看观点历史 | `python scripts/viewpoint_tracker.py history <经理ID> --limit 8` |
| 立场漂移检测 | `python scripts/viewpoint_tracker.py drift <经理ID>` |
| 渲染时间线 | `python scripts/viewpoint_tracker.py timeline <经理ID>` |
| 问答追加 | `python scripts/qa_memory.py record <经理ID> --question "..." --answer "..."` |
| 检索相似历史问答 | `python scripts/qa_memory.py search <经理ID> --question "..."` |
| 按主题汇总 | `python scripts/qa_memory.py summarize <经理ID>` |

**自动化：** `monthly_updater.smart_update` 每次更新自动追加 `viewpoints_history/{id}.jsonl`。

**存储：** `data/viewpoints_history/{id}.jsonl` + `data/qa_history/{id}.jsonl`（每期一行 JSONL）。

---

## Sub-Skill F: 投资能力（v2.0.0 新增）

**Goal:** 把每位经理的业绩量化成 4 维评分 + 业绩归因 + 风险调整指标，回答"这个经理厉害在哪里？"

| 数据 | 命令 |
|------|------|
| 能力评分（选股/择时/风控/稳定） | `python scripts/capability_score.py <经理ID> --save` |
| 批量评估名单 | `python scripts/capability_score.py --all --save` |
| 业绩归因（简化 Brinson） | `python scripts/performance_attribution.py <经理ID> --save` |
| 风险调整指标（最大回撤/夏普/Calmar/Sortino） | `python scripts/risk_metrics.py <经理ID> --save` |

**评分权重：** 选股 35% + 择时 25% + 风控 20% + 稳定 20% → composite (0-100)。

**归因拆解：** 行业暴露 + 选股超额 + 择时 三项贡献。

**存储：** `managers/{id}.json` 新增 `capability_scores` / `attribution` / `risk_metrics` 字段。

---

## Sub-Skill G: 投资风格（v2.0.0 新增）

**Goal:** 把每位经理的风格量化成 6 维雷达 + 漂移检测 + 同风格聚类 + 季度调仓，回答"这位经理风格最近怎么演化？谁跟他最像？"

| 数据 | 命令 |
|------|------|
| 6 维风格雷达 + ASCII 图 | `python scripts/style_radar.py <经理ID> --save` |
| 风格漂移检测 | `python scripts/style_drift.py drift <经理ID>` |
| 风格漂移轨迹报告 | `python scripts/style_drift.py report <经理ID>` |
| 找相似风格经理 top-k | `python scripts/style_cluster.py similar <经理ID> --top-k 5` |
| 全部经理聚类 | `python scripts/style_cluster.py cluster_all --k 4` |
| 季度调仓变化 | `python scripts/turnover_tracker.py changes <经理ID>` |
| 换手率 | `python scripts/turnover_tracker.py turnover <经理ID>` |
| 手动快照持仓 | `python scripts/turnover_tracker.py snapshot <经理ID>` |

**风格 6 维：** 价值/成长 · 大盘/中小盘 · 高动量/低动量 · 质量 · 集中度 · 换手率

**漂移算法：** 两期 style_radar 12 维向量 Euclidean 距离 > 15 报警。

**存储：** `data/style_history/{id}.jsonl` + `data/track_records/{id}.jsonl`（每期一行 JSONL）。

---

## Final Step: 输出模板

回答用户时，按以下结构组织输出（按需裁剪，不必每项都有）：

1. **📋 经理档案** — 姓名、公司、管理产品数、任职回报、管理规模
2. **🧬 投资风格DNA** — 决策框架、风格标签、行业偏好、风格码
3. **💬 季报人话观点** — 蒸馏后的第一人称投资观点
4. **📊 十大重仓** — 排名/代码/名称/占比/出现次数（表格）
5. **📈 业绩数据** — 近1月/3月/6月/1年/3年/今年以来收益率
6. **⚠️ 免责声明** — "以上数据仅供辅助参考，不构成投资建议。数据可能滞后1-2天，持仓每季度更新。"

**答疑/定制产品时：** 以经理第一人称口吻回答，结合具体持仓和风格DNA，结尾加免责声明。

---

## 参考文档

| 文件 | 内容 |
|------|------|
| `references/distill-prompts.md` | 蒸馏 prompt（季报转人话 + 思维DNA提炼）+ 答疑 system prompt + 规则引擎关键词 |
| `references/data-sources.md` | 东方财富/天天基金 API 端点详解、反爬处理、编码处理 |
| `references/roster-schema.md` | roster.json 与经理档案 JSON 结构、种子库结构、change_log 结构、字段说明、数据时效 |
| `references/troubleshooting.md` | 常见错误速查表、环境适配、数据质量提示 |

## 关键脚本与数据文件

| 文件 | 作用 |
|------|------|
| `scripts/roster_manager.py` | 名单管理（上限100人，新增/删除/查看/状态） |
| `scripts/famous_manager_importer.py` | 2025-2026知名经理种子库导入器（list/import_all/import_category/import_one/import_and_fetch） |
| `scripts/monthly_updater.py` | 定期更新（smart_update智能增量 / update_all全量 / stale过期 / update_one单经理） + v2.0.0 自动调用 `_post_update_hooks` |
| `scripts/manager_search.py` | 经理搜索（公募东方财富 + 私募AMAC） |
| `scripts/fetch_holdings.py` | 十大重仓抓取（股票/债券/基金，跨产品聚合） |
| `scripts/fetch_reports.py` | 投资策略与季报抓取 |
| `scripts/fetch_performance.py` | 业绩数据抓取 |
| `scripts/distill_manager.py` | 蒸馏引擎（对话LLM + 规则引擎两级fallback） |
| `scripts/export_table.py` | 表格导出（Excel 4sheet / CSV 3文件） |
| `scripts/speech_fingerprint.py` | **v2.0.0 新增** 言论指纹（句长/第一人称密度/数据驱动/确定性） |
| `scripts/viewpoint_tracker.py` | **v2.0.0 新增** 观点时序追踪（追加JSONL + 立场漂移检测） |
| `scripts/qa_memory.py` | **v2.0.0 新增** 多轮对话记忆（Jaccard 检索相似问答） |
| `scripts/capability_score.py` | **v2.0.0 新增** 4 维能力评分（选股/择时/风控/稳定 + composite） |
| `scripts/performance_attribution.py` | **v2.0.0 新增** 简化 Brinson 业绩归因 |
| `scripts/risk_metrics.py` | **v2.0.0 新增** 风险调整收益（最大回撤/夏普/Calmar/Sortino） |
| `scripts/style_radar.py` | **v2.0.0 新增** 6 维风格雷达（价值/成长/大盘/中小盘/动量/质量/集中度/换手率） |
| `scripts/style_drift.py` | **v2.0.0 新增** 风格漂移检测（Euclidean 距离阈值 15） |
| `scripts/style_cluster.py` | **v2.0.0 新增** 同风格经理聚类（纯 Python KMeans + 余弦相似） |
| `scripts/turnover_tracker.py` | **v2.0.0 新增** 季度调仓追踪（快照/新增退出/换手率） |
| `data/roster.json` | 已蒸馏经理名单（上限100人） |
| `data/famous_managers_2025_2026.json` | 2025-2026知名经理种子库（80位，4分类） |
| `data/managers/{id}.json` | 单经理完整档案（重仓/策略/业绩/风格DNA + v2.0.0 新增：speech_fingerprint/capability_scores/attribution/risk_metrics/style_radar） |
| `data/change_log/YYYY-MM-DD.json` | smart_update 变化日志（记录每次变化的经理与原因） |
| `data/viewpoints_history/{id}.jsonl` | **v2.0.0 新增** 观点时序（每期一行） |
| `data/qa_history/{id}.jsonl` | **v2.0.0 新增** 问答历史（每条一问一答） |
| `data/style_history/{id}.jsonl` | **v2.0.0 新增** 风格雷达时序（每期一行） |
| `data/track_records/{id}.jsonl` | **v2.0.0 新增** 持仓快照（每期一行） |

---

## 维护与更新日志

- **当前版本**：2.1.0（2026-08-23）— 稳定性升级：修复 8 处计算/解析缺陷 + 原子写入加固
- **测试覆盖**：189 个测试全部通过（含 18 个 v2.1 回归测试）
- **v2.1.0（2026-08-23）**：BUG 修复 + 算法质量升级（详见 `tests/test_v210_fixes.py`）
  - **BUG 修复**：
    1. `risk_metrics` 滚动窗口收益量纲错误：近1月/3月/6月/1年为重叠窗口，旧版直接累加构造净值/混合算标准差；改为累计增长因子反推不重叠区间收益并按 `(30/区间天数)` 幂次月化，回撤/波动率/下行波动率全部修正。
    2. `_common.http_get_jsonp` 盲目 `replace("'", '"')` 破坏值内合法撇号（如 "O'Hara"）；改为先尝试原文解析，失败后用状态机转换单引号定界符。
    3. `style_cluster._cosine` 对 0-100 全正雷达向量恒 ~0.99+ 无判别力；改为中心化余弦（减 50），返回 -1~1。
    4. `style_cluster._kmeans` 前 k 点重复时产生重复中心；改为 kmeans++ lite 确定性初始化，代表成员改选组内最接近中心者。
    5. `distill_manager` 持仓代码为空串时误判海外市场；加空值守卫。
  - **优化升级**：`qa_memory` 相似度从纯 Jaccard 升级为 0.6×Jaccard + 0.4×包含度混合（对后缀追加/重述型问题更敏感）；`monthly_updater.bump_skill_version` 改原子写入（临时文件 + `os.replace`）；`viewpoint_tracker.render_timeline` 省略号仅在截断时添加；`style_radar` 删除死代码。
  - **测试 148→189**：新增 `test_v210_fixes.py`（18 用例覆盖全部修复点），零回归。
- **v2.0.0（2026-08-07）**：言论/能力/风格 三大能力层 + BUG 修复
  - **BUG 修复**：`manager_search.build_manager_index()` 缓存过期但 HTTP 失败时不再返回空 list（silent failure），降级到过期缓存。同时 `tests/test_bug_fixes.py` 5 个失败用例的硬编码日期 `2026-07-29` 改为动态 `_today()`，避免下次过期。
  - **言论能力 3 模块**：speech_fingerprint（6 维关键词字典）/ viewpoint_tracker（JSONL 时序+漂移检测）/ qa_memory（Jaccard 检索）
  - **投资能力 3 模块**：capability_score（4 维 0-100 评分）/ performance_attribution（简化 Brinson 归因）/ risk_metrics（最大回撤+夏普+Calmar+Sortino）
  - **投资风格 4 模块**：style_radar（6 维 0-100 雷达图）/ style_drift（Euclidean 漂移检测）/ style_cluster（KMeans+余弦相似聚类）/ turnover_tracker（持仓快照+换手率）
  - **自动化**：`monthly_updater._post_update_hooks` 在每次 update_one 后自动调用：写 capability_scores/attribution/risk_metrics/speech_fingerprint/style_radar 到 manager.json，追加 viewpoints_history/style_history/track_records 三份 JSONL。
  - **测试 92→148**：新增 58 个测试覆盖 10 个新模块 + 2 个回归测试。
- **v1.2.28 历史**：97 测试 / v1.2.26 历史：86 测试
- **git log**：见 `git log -- SKILL.md`（每次运行 `monthly_updater.smart_update` 都会在 `data/change_log/YYYY-MM-DD.json` 追加 runs 数组）
