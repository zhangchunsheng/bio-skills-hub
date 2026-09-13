---
name: pharma-research-frontier
description: "医药行业最新研究方向追踪：新兴技术方向、突破文献、递送平台、赛道热点与投资/立项信号，以眼科（基因治疗/视网膜疾病/人工视觉/干眼机制）与耳科（听力修复/毛细胞再生/眩晕机制）前沿为优先重点，其余赛道（肿瘤/自免/代谢/神经等）同样覆盖、不作排他。触发词：前沿、研究方向、技术热点、突破、文献、递送平台、基因治疗、细胞治疗、核酸递送、AI药物设计、赛道、研发布局、trend、frontier、眼科前沿、耳科前沿、最新进展、ARVO、AAO、TRIO。"
---

# 医药前沿研究追踪 Pharma Research Frontier

为「战略立项/方向研判/BD」岗位提供（眼科/耳科五官科为优先重点，其余赛道同样覆盖、不作排他）：「方向看得准、信号辨得清、转化判得明」的前沿情报抓手。覆盖四类信息域：**技术方向、突破文献、递送平台、眼科/耳科专项**。本 skill 不替代决策，而是把前沿情报的采集、信号分级与转化判断结构化，并随使用自我成长。

## 调用流程（Capability 路由）

1. 先判断诉求落在哪个信息域（见下「核心能力」），读取对应 `references/baseline.md`。
2. **涉及具体方向/文献/平台时，先查询本地成长库**：运行 `scripts/registry_cli.py query --name X --type <bucket>`——
   - `FRESH` → 直接采用，标注「📚 本地知识库已核验(YYYY-MM-DD)」；
   - `STALE` → 提示「该条目已超 6 个月，正在刷新…」，跳到步骤 4；
   - `NOT_FOUND` → 跳到步骤 4。
3. 需要交叉核验时，优先 `regulatory-monitor` 拉取 NMPA/FDA/EMA 最新（突破性疗法/孤儿药等监管信号）。
4. **刷新/新增（自我成长）**：对 STALE/NOT_FOUND 的条目，用 WebSearch/WebFetch（顶刊/会议/管线/资本）或 regulatory-monitor 核实，再以 `registry_cli.py add --json '{...}'` 写回 `data/registry.json`。
5. 输出统一格式（见「输出规范」），便于沉淀进项目文件夹。

## 核心能力

### 1. 技术方向（trends）
目标：识别值得跟的模态与成熟度。
- 基因治疗（AAV/CRISPR）、RNA 药物、细胞治疗、核酸与新型递送、AI 药物设计、微生物组。
- 按 TRL 分层（概念验证/临床前/临床/已上市），避免把论文当产品。

### 2. 突破文献（papers）
目标：提炼「科研→管线」信号。
- 信号源：NEJM/Nature/Science/Cell 及子刊、Ophthalmology、JARO；会议 ARVO/AAO/TRIO。
- 标注期刊/会议、年份、阶段（已发表/摘要）；区分机制突破与临床读出。

### 3. 递送与技术平台（platforms）
目标：研判可行性壁垒。
- 眼部：玻璃体腔/结膜下/角膜前/视网膜下；纳米粒、原位凝胶、AAV、植入缓释。
- 耳部：鼓室/耳蜗；纳米、基因/细胞递送、缓释；内耳靶向是核心难点。

### 4. 眼科/耳科专项（ocular_otic）
目标：把专科前沿单列研判。
- 眼科：基因治疗（RPE65 赛道已验证）、抗 VEGF 新机制/更长间隔、视网膜色素变性/AMD 基因与细胞治疗、人工视觉/光遗传、干眼新靶点、青光眼神经保护。
- 耳科：感音神经性聋毛细胞再生（Notch/Atoh1）、耳蜗基因/细胞治疗、眩晕（梅尼埃）新机制、中耳炎局部新疗法。

## 输出规范（统一）
- 前沿报告七段：方向概述 / 关键突破 / 代表玩家与管线 / 技术成熟度(TRL) / 眼科耳科专项 / 风险与窗口 / 布局建议。
- 玩家管线用表格（机构/技术/阶段/差异化）。
- 明确「科研信号」与「已立项管线」的差距，避免把论文当产品。

## 自我成长与自动更新机制（Self-Growth & Auto-Update）——核心特色
本 skill 带一个**会随使用越来越聪明的本地知识库** `data/registry.json`，并联动 `regulatory-monitor` 保持监管信号最新：

**知识库结构**（`data/registry.json`）：
```
{
  "meta": {"last_full_refresh": "YYYY-MM-DD", "version": 1, "freshness_months": 6},
  "trends":        { "<技术方向>": {content, note, last_checked, source} },
  "papers":        { "<突破文献/信号>": {content, note, last_checked, source} },
  "platforms":     { "<递送/技术平台>": {content, note, last_checked, source} },
  "ocular_otic":   { "<眼科/耳科专项>": {content, note, last_checked, source} }
}
```
- 每个桶代表一类前沿知识；种子基线已写入（前沿模态、信号源、眼/耳递送、AAV/脂质体、眼科/耳科前沿）。
- 每条带 `last_checked`，超 6 个月自动 STALE；查询时强制复核最新（监管信号以 regulatory-monitor 拉取为准）。

**每次查询执行流程（必须照做）**：见「调用流程」步骤 2/4。凡涉及监管/获批状态，**不写死**，以 `regulatory-monitor` 拉取的最新为准。

**离线基线** `references/baseline.md`：顶部标注「最后刷新 YYYY-MM-DD」。**凡涉及监管/合规，若基线超 6 个月，必须先触发 `regulatory-monitor` 复核再作答**。

**周期性维护**：`scripts/registry_cli.py stale` 列过期 → 结合 `regulatory-monitor` 批量刷新；`stats` 盘点新鲜度；`list --type X` 查看某类；`seed_registry.py` 可重建基线。

## 资源
- `scripts/registry_cli.py`：自我成长引擎（query/add/list/stale/stats，6 个月新鲜度，桶动态取自 registry.json）。纯 Python，无第三方依赖。
- `scripts/seed_registry.py`：写入前沿研究基线种子；首次或重置时生成 `data/registry.json`。
- `references/baseline.md`：前沿模态/信号源/递送/眼科耳科离线基线（含刷新日期，联动 regulatory-monitor 更新）。
- `data/registry.json`：成长知识库（随使用累积）。

## 注意
- 不臆造数据：顶刊结论须标注期刊/年份/样本量，会议数据标注会议与年份。
- 区分 TRL：概念验证/临床前/临床/已上市。
- 警惕「过热赛道」与「伪需求」，用未满足需求与支付能力交叉验证。
- 与姊妹 skill 协同：`new-drug-intel`（前沿转立项）、`generic-drug-intel`（仿制对比）、`drug-project-intel-expert`（立项）、`regulatory-monitor`（法规自动更新）。
- 自我成长纪律：每次给出方向/文献/平台结论后，若条目来自查询且已核实，须通过 `registry_cli.py add` 沉淀进 `data/registry.json`；涉及版本修订的以 regulatory-monitor 最新为准，不写死。
