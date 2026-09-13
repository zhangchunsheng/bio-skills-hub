---
name: generic-drug-intel
description: "仿制药调研情报：品种档案（原研/参比制剂/国内申报）、专利布局与到期/挑战/规避、一致性评价与BE路径、市场格局与集采分析，以眼科（滴眼剂/眼用凝胶/混悬）与耳科（滴耳剂/耳用制剂）仿制为优先重点，其余治疗领域（肿瘤/自免/代谢/神经/呼吸/消化等）同样覆盖、不作排他。触发词：仿制药、仿制、一致性评价、参比制剂、RLD、BE、生物等效、专利到期、专利挑战、PIV、首访、首仿、集采、带量采购、市场格局、原研、过评、眼科仿制、耳科仿制、generic。"
---

# 仿制药调研情报 Generic Drug Intelligence

为「仿制药立项/注册/BD」岗位提供（眼科/耳科五官科为优先重点，其余治疗领域同样覆盖、不作排他）：「参比找得准、专利看得清、BE 路径判得明、市场算得清」的仿制调研抓手。覆盖五类信息域：**品种档案、专利、一致性评价与 BE、市场集采、眼科/耳科专项**。本 skill 不替代立项判断，而是把仿制调研的结构、数据源与判定逻辑固化，并随使用自我成长。

## 调用流程（Capability 路由）

1. 先判断诉求落在哪个信息域（见下「核心能力」），读取对应 `references/baseline.md`。
2. **涉及具体品种/专利/BE/市场时，先查询本地成长库**：运行 `scripts/registry_cli.py query --name X --type <bucket>`——
   - `FRESH` → 直接采用，标注「📚 本地知识库已核验(YYYY-MM-DD)」；
   - `STALE` → 提示「该条目已超 6 个月，正在刷新…」，跳到步骤 4；
   - `NOT_FOUND` → 跳到步骤 4。
3. 需要交叉核验时，优先 `regulatory-monitor` 拉取 NMPA/CDE/FDA/EMA 最新（参比目录、集采、BE guideline）。
4. **刷新/新增（自我成长）**：对 STALE/NOT_FOUND 的条目，用 WebSearch/WebFetch 或 regulatory-monitor 核实，再以 `registry_cli.py add --json '{...}'` 写回 `data/registry.json`（涉法规版本须带回最新口径）。
5. 输出统一格式（见「输出规范」），便于沉淀进项目文件夹。

## 核心能力

### 1. 品种档案（products）
目标：建立某仿制品种的「身份证」。
- 原研企业、参比制剂（RLD/官方目录）、国内上市与申报状态（已上市/在审/未进口/停止）、规格剂型、说明书与专利链接药品（PLD）。
- 输出：品种档案表（通用名/原研/参比/国内状态/专利到期/技术难度）。

### 2. 专利与规避（patents）
目标：识别壁垒与首仿窗口。
- 化合物/制剂/工艺/用途专利，到期时间，PIV 声明与专利挑战（美国 180 天独占），规避设计空间。
- 中国以 CNIPA、美国以 Orange Book/USPTO 为准；注明「中国同族待 CNIPA 核验」。
- 联动 patent-disclosure-skill 做 FTO。

### 3. 一致性评价与 BE（be_registry）
目标：判定等效证据路径。
- 口服固体制剂多需 BE；局部作用制剂（滴眼/滴耳）倾向质量一致替代证据（IVRT/IVPT/粒度/流变/无菌/抑菌效力）。
- 参比制剂目录与「可替代」判定；BE 豁免情形。

### 4. 市场与集采（market）
目标：算清商业空间。
- 国内市场规模、销量/金额、竞争格局（过评家数）、国家/省级集采中选与价格、可及性与利润空间。
- 数据源：米内网、企业年报、CDE 受理公示、集采中标公告。

### 5. 眼科/耳科专项（ocular_otic）
目标：把局部用药仿制的特殊性纳入研判。
- 眼科：角膜前滞留<5min、生物利用度<5%、防腐剂（BAK）安全性、单剂量无防腐（BFS）趋势；眼用混悬/凝胶以 IVRT/流变替代 BE。
- 耳科：溶液/混悬为主，可含抗微生物成分，黏度适中利于滞留；参照 ChP 0112。

## 输出规范（统一）
- 调研报告八段：背景 / 原研参比 / 专利 / 一致性评价与 BE / 市场集采 / 竞争格局 / 风险 / 优先级建议。
- 品种用表格（通用名/原研/参比/国内状态/专利到期）。
- 专利标注不确定项（「中国同族待 CNIPA 核验」「Orange Book 待核」）。
- 结尾固定：① 推荐优先级与理由；② ⚠️ 风险（专利/集采/技术）；③ 后续建议（「建议 CDE 检索 X 参比」「建议核实 Y 专利到期」）。

## 自我成长与自动更新机制（Self-Growth & Auto-Update）——核心特色
本 skill 带一个**会随使用越来越聪明的本地知识库** `data/registry.json`，并联动 `regulatory-monitor` 保持法规/目录最新：

**知识库结构**（`data/registry.json`）：
```
{
  "meta": {"last_full_refresh": "YYYY-MM-DD", "version": 1, "freshness_months": 6},
  "products":      { "<品种>": {content, note, last_checked, source} },
  "patents":       { "<专利主题>": {content, note, last_checked, source} },
  "be_registry":   { "<BE/参比主题>": {content, note, last_checked, source} },
  "market":        { "<市场/集采主题>": {content, note, last_checked, source} },
  "ocular_otic":   { "<眼科/耳科专项>": {content, note, last_checked, source} }
}
```
- 每个桶代表一类仿制调研知识；种子基线已写入（参比评估、橙皮书/PIV、局部 BE 豁免、集采、眼科/耳科难点）。
- 每条带 `last_checked`，超 6 个月自动 STALE；查询时强制复核最新（法规/目录以 regulatory-monitor 拉取为准）。

**每次查询执行流程（必须照做）**：见「调用流程」步骤 2/4。凡涉及法规/目录版本，**不写死**，以 `regulatory-monitor` 拉取的最新为准。

**离线基线** `references/baseline.md`：顶部标注「最后刷新 YYYY-MM-DD」。**凡涉及注册/合规，若基线超 6 个月，必须先触发 `regulatory-monitor` 复核再作答**。

**周期性维护**：`scripts/registry_cli.py stale` 列过期 → 结合 `regulatory-monitor` 批量刷新；`stats` 盘点新鲜度；`list --type X` 查看某类；`seed_registry.py` 可重建基线。

## 资源
- `scripts/registry_cli.py`：自我成长引擎（query/add/list/stale/stats，6 个月新鲜度，桶动态取自 registry.json）。纯 Python，无第三方依赖。
- `scripts/seed_registry.py`：写入仿制调研基线种子；首次或重置时生成 `data/registry.json`。
- `references/baseline.md`：参比/专利/BE/集采/眼科耳科离线基线（含刷新日期，联动 regulatory-monitor 更新）。
- `data/registry.json`：成长知识库（随使用累积）。

## 注意
- 不臆造临床数据或市场数字：来源与日期须可追溯（NMPA/CDE/企业年报/米内网/Orange Book）。
- 区分「已上市/在审/终止/未进口」状态，避免过时结论。
- 专利地域性敏感：国内外分别判断，中国以 CNIPA、美国以 USPTO/Orange Book 为准。
- 与姊妹 skill 协同：`new-drug-intel`（创新药对比）、`pharma-research-frontier`（方向研判）、`drug-regulatory-expert`（注册）、`drug-project-intel-expert`（立项）、`regulatory-monitor`（法规自动更新）。
- 自我成长纪律：每次给出品种/专利/BE/市场结论后，若条目来自查询且已核实，须通过 `registry_cli.py add` 沉淀进 `data/registry.json`；涉及版本修订的以 regulatory-monitor 最新为准，不写死。
