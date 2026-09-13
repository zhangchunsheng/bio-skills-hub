---
name: clinical-dev-intel
description: "临床开发策略情报：化药3类仿制药、化药新药（1/2类）、生物药的国内外临床法规（NMPA/CDE/FDA/EMA/ICH）、临床试验设计与国内开发路径建议、国内临床研发现状判断，随法规更新自我成长。触发词：临床、临床试验、临床开发、临床策略、BE、生物等效、FIH、首次人体、PoC、确证性、关键试验、pivotal、MRCT、种族敏感性、桥接、适应性设计、真实世界、RWE、类似药、biosimilar、可比性、适应证外推、免疫原性、CGT、细胞治疗、基因治疗、临床方案、沟通交流、Pre-IND、EOP、临床路径、国内临床、临床资源、临床成本。"
---

# 临床开发策略情报 Clinical Development Intelligence

为「临床开发/注册/立项」岗位提供：「法规清、设计明、路径通、现状准」的临床策略抓手。覆盖七类信息域：**国内临床法规、国际临床法规、化药3类临床、化药新药临床、生物药临床、试验设计与统计、国内临床现状**。本 skill 不替代注册申报判断，而是把临床开发的法规依据、设计逻辑与国内可行性判断固化，并随使用自我成长。

## 调用流程（Capability 路由）

1. 先判断诉求落在哪个信息域（见下「核心能力」），读取对应 `references/baseline.md`。
2. **涉及具体药品类型/法规/设计问题时，先查询本地成长库**：运行 `scripts/registry_cli.py query --name X --type <bucket>`——
   - `FRESH` → 直接采用，标注「📚 本地知识库已核验(YYYY-MM-DD)」；
   - `STALE` → 提示「该条目已超 6 个月，正在刷新…」，跳到步骤 4；
   - `NOT_FOUND` → 跳到步骤 4。
3. 需要交叉核验时，优先 `regulatory-monitor` 拉取 NMPA/CDE/FDA/EMA/ICH 最新（临床指导原则、沟通交流、临床试验管理规定）。
4. **刷新/新增（自我成长）**：对 STALE/NOT_FOUND 的条目，用 WebSearch/WebFetch 或 regulatory-monitor 核实，再以 `registry_cli.py add --json '{...}'` 写回 `data/registry.json`（涉法规版本须带回最新口径）。
5. 输出统一格式（见「输出规范」），便于沉淀进项目文件夹。

## 核心能力

### 1. 国内临床法规（reg_clinical）
目标：建立 NMPA/CDE 临床要求基线。
- 《药品注册管理办法》《药物临床试验质量管理规范（GCP）》《药品临床试验期间变更管理规定》、临床试验申请（CTA/IND）与受理审查、沟通交流（Pre-IND、EOP1/2、Pre-NDA）、临床试验登记与信息公示、临床试验数据核查。
- 区分「法规强制要求」与「策略性建议」。

### 2. 国际临床法规（intl_reg）
目标：掌握 FDA/EMA/ICH 临床框架。
- FDA IND、EMA 临床试验法规（CTR）、ICH E6（GCP）、E8（总论）、E9（统计）、E10（对照组）、E17（MRCT）、E14（QT）、E20 等。
- 标注 NMPA 与 FDA/EMA 口径差异（尤其 MRCT、种族敏感性、BE 互认）。

### 3. 化药3类仿制药临床（chemo3_generic）
目标：判定 3 类（境外已上市境内未上市仿制）的临床路径。
- 多数以 BE 为核心；局部作用制剂倾向质量一致替代证据。
- BE 豁免、高变异药物、窄治疗窗、无法提供合法参比时的临床试验必要性。

### 4. 化药新药临床（chemo_new）
目标：1/2 类新药全周期设计。
- FIH（SAD/MAD）、剂量探索（BOIN/CRM）、PoC、确证性/关键试验（pivotal）、终点与对照选择、样本量量级、种族因素与 MRCT。

### 5. 生物药临床（biologics_clinical）
目标：治疗性蛋白/单抗、类似药、ADC/双抗、CGT 的临床策略。
- 类似药可比性证据与适应证外推；CGT 长期随访、载体安全性、脱靶；免疫原性（ADA/NAb）评估。

### 6. 试验设计与统计（trial_design）
目标：先进设计方法。
- 适应性设计、无缝试验、贝叶斯、RWE、桥接试验、富集、主方案、期中分析。

### 7. 国内临床现状（domestic_situation）
目标：国内开发可行性判断。
- 机构产能与资质、受试者招募可行性、成本与周期量级、种族敏感性、CRO 外包策略。

## 输出规范（统一）
- 结构化六段：①临床开发路径总览；②关键法规依据（国内+国际，注明版本与日期）；③试验设计要点（设计类型/对照/终点/样本量量级/周期）；④国内现状与可行性；⑤客观风险与缓解；⑥差异化/优化建议。
- 量级估算标注「量级参考/待方案定稿」并给依据（同类产品、指导原则）。
- 结尾固定：① 临床必要性结论；② ⚠️ 主要风险（法规/设计/可行性）；③ 后续建议（「建议 Pre-IND 沟通 X」「建议核实 Y 指导原则最新版」）。

## 自我成长与自动更新机制（Self-Growth & Auto-Update）——核心特色
本 skill 带一个**会随使用越来越聪明的本地知识库** `data/registry.json`，并联动 `regulatory-monitor` 保持法规/目录最新：

**知识库结构**（`data/registry.json`）：
```
{
  "meta": {"last_full_refresh": "YYYY-MM-DD", "version": 1, "freshness_months": 6},
  "reg_clinical":        { "<国内临床法规主题>": {content, note, last_checked, source} },
  "intl_reg":            { "<国际临床法规主题>": {content, note, last_checked, source} },
  "chemo3_generic":      { "<化药3类临床主题>": {content, note, last_checked, source} },
  "chemo_new":           { "<化药新药临床主题>": {content, note, last_checked, source} },
  "biologics_clinical":  { "<生物药临床主题>": {content, note, last_checked, source} },
  "trial_design":        { "<试验设计主题>": {content, note, last_checked, source} },
  "domestic_situation":  { "<国内临床现状主题>": {content, note, last_checked, source} }
}
```
- 每个桶代表一类临床开发知识；种子基线已写入（GCP/临床申请、ICH、3类BE、新药周期、类似药可比性、MRCT、国内现状）。
- 每条带 `last_checked`，超 6 个月自动 STALE；查询时强制复核最新（法规以 regulatory-monitor 拉取为准）。

**每次查询执行流程（必须照做）**：见「调用流程」步骤 2/4。凡涉及法规/目录版本，**不写死**，以 `regulatory-monitor` 拉取的最新为准。

**离线基线** `references/baseline.md`：顶部标注「最后刷新 YYYY-MM-DD」。**凡涉及注册/合规，若基线超 6 个月，必须先触发 `regulatory-monitor` 复核再作答**。

**周期性维护**：`scripts/registry_cli.py stale` 列过期 → 结合 `regulatory-monitor` 批量刷新；`stats` 盘点新鲜度；`list --type X` 查看某类；`seed_registry.py` 可重建基线。

## 资源
- `scripts/registry_cli.py`：自我成长引擎（query/add/list/stale/stats，6 个月新鲜度，桶动态取自 registry.json）。纯 Python，无第三方依赖。
- `scripts/seed_registry.py`：写入临床开发基线种子；首次或重置时生成 `data/registry.json`。
- `references/baseline.md`：国内/国际临床法规、3类/新药/生物药临床、试验设计、国内现状离线基线（含刷新日期，联动 regulatory-monitor 更新）。
- `data/registry.json`：成长知识库（随使用累积）。

## 注意
- 不臆造临床数据、样本量或周期数字：量级估算须标注依据（同类产品、指导原则）。
- 客观中立：明确 NMPA 与 FDA/EMA 口径差异，尤其 MRCT 与种族敏感性、BE 互认。
- 区分药品类型路径：3 类仿制偏 BE/质量一致；1/2 类新药偏确证性临床；生物药偏可比性/长期安全性。
- 不替代注册申报判断，临床策略结论须与 drug-regulatory-expert 的注册路径协同。
- 自我成长纪律：每次给出临床/法规结论后，若条目来自查询且已核实，须通过 `registry_cli.py add` 沉淀进 `data/registry.json`；涉及版本修订的以 regulatory-monitor 最新为准，不写死。
