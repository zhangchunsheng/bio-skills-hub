---
name: pharma-analytical-assistant
description: 药物分析（QC/分析方法）辅助：分析方法开发（HPLC/GC/CE/UV 分离与检测策略）、方法学验证（ICH Q2(R2)/中国药典 0512 专属性/线性/准确度/精密度/LOD-LOQ/耐用性/系统适用性/稳定性指示）、药典与法规基线（ChP2025/USP/EP/JP、NMPA/CDE/FDA/EMA/ICH，联动 regulatory-monitor 自动更新）、复杂基质前处理（眼科/耳科混悬液/凝胶/乳剂/植入剂的提取·分散·均质）、稳定性与溶出/释放（IVRT/IVPT、植入剂体外释放、稳定性指示方法）、杂质谱与降解（有机杂质/降解产物/遗传毒性/残留溶剂 ICH Q3A/B/Q3C/Q3D）。当用户需要开发或评估一个药物的 HPLC/GC 含量与有关物质方法、做方法学验证方案与可接受标准、整理药典/注册申报的分析要求、处理混悬/凝胶/乳剂/植入剂的样品前处理、或审查分析方法合规性时使用。触发词包括但不限于：分析方法、方法开发、方法验证、ICH Q2、药典方法、含量测定、有关物质、杂质谱、降解产物、系统适用性、专属性、线性、准确度、精密度、LOD、LOQ、耐用性、残留溶剂、遗传毒性杂质、稳定性指示、溶出、IVRT、IVPT、体外释放、前处理、样品提取、粒径、眼科分析、耳科分析、QC、质量标准、注册检验、放行检验。适用于药物分析、QC 方法建立、制剂研发质量研究、注册申报（NMPA/CDE/FDA）、眼科/耳科局部用药的质量控制。
---

# 药物分析辅助 Pharma Analytical Assistant

为「制剂研发/注册/质量研究」岗位（兼具分析研发背景）提供「方法建得对、验证过得去、法规跟得上、基质处理得了」的分析推理抓手。聚焦**五官科（眼科/耳科）**局部用药，覆盖溶液、混悬液、凝胶、乳剂、植入剂五类剂型的质量研究。本 skill 不替代分析化学家判断，而是把方法开发套路、验证可接受标准、药典/法规基线、复杂基质前处理结构化，降低跨剂型踩坑概率。

## 调用流程（Capability 路由）

1. 先判断诉求落在哪个能力（见下「核心能力」），读取对应 `references/*.md`。
2. **涉及待测项技术选型或药典/指导原则时，先查询本地成长库**：运行 `scripts/registry_cli.py query --name X --type methods|guidances`——
   - `FRESH` → 直接采用，标注「📚 本地知识库已核验(YYYY-MM-DD)」；
   - `STALE` → 提示「该条目已超 6 个月，正在刷新…」，跳到步骤 4；
   - `NOT_FOUND` → 跳到步骤 4。
3. 涉及验证统计/粒径/释放计算时，调用 `scripts/method_metrics.py`。
4. **刷新/新增（自我成长）**：对 STALE/NOT_FOUND 的条目，用文献/药典核实，凡涉法规版本须**联动 `regulatory-monitor`** 拉取 NMPA/CDE/FDA/EMA/ICH 最新；再以 `registry_cli.py add --json '{...}'` 写回 `data/registry.json`（Guidance 类须带回最新版本号）。本 skill 的 `references/regulatory_baseline.md` 作为离线基线，须定期刷新（>6 个月提示刷新）。
5. 输出统一格式（见「输出规范」），便于沉淀进项目文件夹（RD001 / RL009 同类）。

## 核心能力

### 1. 分析方法开发（method development）
目标：针对待测物（API、有关物质、降解物、残留溶剂、元素杂质、防腐剂/抑菌剂、渗透压/黏度等非含量项）选定技术与系统。
- 技术选型：反相/正相 HPLC（主力）、GC（残留溶剂/挥发性）、CE（手性/离子化合物）、UV/荧光、ICP-MS（元素杂质 ICH Q3D）、滴定（含量，ChP 通则 0701）。
- 分离策略：色谱柱（C18/AQ/苯基/硅胶/手性）、梯度、pH、有机相、离子对；必要时用 PDA 全波长扫描确证峰纯度。
- 检测策略：UV（λmax）、CAD/ELSD（无紫外）、MS（确证/痕量）、示差（糖类）。
- 眼科/耳科重点：抑菌剂含量（苯扎氯铵等）须单独方法且做**效价/抑菌效力（USP<51>/ChP 抑菌效力）**联动；混悬液需做**混悬物相 API 含量**（避免只测上清）；植入剂需做**释放介质中 API 及降解物**。
- 详细套路见 `references/method_dev.md`。

### 2. 方法学验证（method validation）—— 合规核心
目标：按用途（鉴别/含量/有关物质/残留溶剂/溶出）给出验证项目与可接受标准。
- 全项目（ICH Q2(R2) + 中国药典 9101/0512）：**专属性（含强制降解/稳定性指示）、线性与范围、准确度、精密度（重复性+中间精密度）、检测限 LOD、定量限 LOQ、耐用性、系统适用性**。
- 强制降解（stress）：酸/碱/氧化/高温/光照/湿（含水/冻干制剂），计算 mass balance，证明方法「稳定性指示」。
- 可接受标准速查（含量：准确度 98–102%、RSD≤2.0%；有关物质：LOQ≤报告阈值、准确度 80–120%、RSD≤15%）：
  - 详见 `references/validation.md`（含逐项目表格与 ChP/NMPA 差异提示）。
- 统计计算用 `scripts/method_metrics.py`。

### 3. 药典与法规基线（compendial & regulatory）—— 自动更新
目标：明确「国内报/进口/欧美」各应依从的药典与指导原则，并**保持最新**。
- 国内：中国药典 2025（四部通则 0512 HPLC、0521 GC、0513 CE、0941 释放度、0982 粒度和粒度分布、黏度 0633、0931 溶出、0105 眼用制剂、0112 耳用制剂、9001 原料药与制剂稳定性、9012 药物引湿性、抑菌效力 9206 等）+ NMPA/CDE 指导原则（化学药物质量标准建立、杂质研究、残留溶剂、元素杂质、稳定性、溶出/释放、多剂量/单剂量包装）。
- 国际：USP-NF（<51> 抑菌效力、<711> 溶出、<1724> 半固体释放、<621> 色谱）、EP、JP；FDA/EMA/ICH（Q2/Q3A/B/Q3C/Q3D/M7/Q1A-Q1E/Q6A）。
- **自动更新机制**：本 skill 不内嵌「写死」的法规版本号；每次任务前若涉及注册/合规，**先调用 `regulatory-monitor` 检索 CDE/NMPA/FDA/EMA/ICH 近期动态**，再对照 `references/regulatory_baseline.md` 基线给出结论。基线文件顶部标注上次刷新日期，过期（>6 个月）须提示用户刷新。
- 眼科/耳科专项：眼用制剂（ChP 0105）要求无菌、渗透压、pH、黏度、粒度（混悬）、金属离子、抑菌剂效力；耳用制剂（ChP 0112）类似但可抑菌/抗真菌。

### 4. 复杂基质前处理（sample prep）
目标：把「混悬/凝胶/乳剂/植入剂」真正转化成可进样溶液，避免基质效应与回收率失真。
- 混悬液：涡旋+超声充分再分散 → 溶剂溶解/萃取 API → 离心取上清；注意**不溶辅料的干扰**与回收率验证。
- 凝胶：剪切稀释/加热破胶（依基质）→ 溶剂萃取 → 必要时滤过（注意吸附）。
- 乳剂：破乳（有机溶剂破乳/离心分层）→ 取油/水相分别或合并提取。
- 植入剂：体外释放取样后取释放介质直接进样（API 已溶出），或剪碎/研磨后溶剂提取做含量均匀度/释放曲线。
- 前处理须配套**回收率/基质效应**验证（尤其 LC-MS 法）。详见 `references/sample_prep.md`。

### 5. 稳定性与溶出/释放（stability & dissolution/release）
目标：为稳定性研究与剂型释放建立正确方法。
- 稳定性指示方法：第 2 节强制降解已覆盖；长期/加速/中间条件按 ChP 9001 / ICH Q1A（注意半透性容器低湿：RL009 专题）。
- 溶出/释放：溶液/混悬液一般不溶出（做含量均匀度/装量）；**凝胶/乳膏/软膏做 IVRT（体外释放，ChP 0931/USP<1724>， Franz 扩散池）**；**植入剂做体外释放（HPLC 测累积释放%，拟合零级/一级/Higuchi/Korsmeyer-Peppas）**。
- 局部作用制剂（眼科/耳科）一般不要求全身 BA/BE，但**需证明质量一致（IVRT/IVPT/粒度/流变）**，详见注册登记基线。

### 6. 杂质谱与降解（impurity profiling）
目标：系统识别有机杂质、降解物、遗传毒性杂质、残留溶剂、元素杂质。
- 有机杂质（ICH Q3A/B + 中国药典杂质研究）：起始原料/中间体/工艺副产/降解物；用强制降解定位降解途径。
- 遗传毒性（ICH M7）：警示结构 → 含亚硝胺/酰化剂等的控制策略（限度 AIA/AI）。
- 残留溶剂（ICH Q3C）：一类禁/限、二类限度（如甲醇、乙腈、二氯甲烷）、三类低毒。
- 元素杂质（ICH Q3D + 中国药典 2321/0861）：四类元素（Cd/Pb/As/Hg + 催化剂类）。
- 眼科/耳科包装（如 LDPE 瓶、BFS，见 RL009）须评估浸出物/可提取物（E&L），联动包材相容性研究。

## 输出规范（统一）
- 方法开发建议用「技术选型表」：待测项 | 推荐技术 | 色谱/检测条件要点 | 注意。
- 验证方案用「验证项目表」：项目 | 做法 | 可接受标准 | 是否适用。
- 药典/法规结论固定三段：① 国内依从（ChP/NMPA/CDE）；② 国际依从（USP/EP/FDA/EMA/ICH）；③ ⚠️ 法规更新提示（注明基线刷新日期，建议 regulatory-monitor 复核）。
- 结尾固定：① 推荐方法与理由；② ⚠️ 合规/安全风险（无则写「未识别」）；③ 后续建议（如「建议 CDE 检索 X 指导原则最新版」「建议小试验证 Y 回收率」）。

## 自我成长与自动更新机制（Self-Growth & Auto-Update）——核心特色
本 skill 带一个**会随使用越来越聪明的本地知识库** `data/registry.json`，并联动 `regulatory-monitor` 保持法规最新：

**知识库结构**（`data/registry.json`）：
```
{
  "meta": {"last_full_refresh": "YYYY-MM-DD", "version": 1, "freshness_months": 6},
  "methods":   { "<待测项>": {analyte, technique, conditions, validation, note, last_checked, source} },
  "guidances": { "<ICH Q2(R2)/ChP 0512...>": {scope, applicability, note, last_checked, source} }
}
```
- `methods`：稳定的待测项→分析技术选型（兼容性、验证策略）。种子已写入含量/有关物质/手性/残留溶剂/元素杂质/抑菌剂/混悬含量/植入释放/粒度等。
- `guidances`：国内外药典通则与 ICH 指导原则基线，**版本会修订**——每条带 `last_checked`，超 6 个月自动 STALE，查询时强制以 `regulatory-monitor` 复核最新版本号。

**每次查询执行流程（必须照做）**：见「调用流程」步骤 2/4。凡涉及法规版本，**不写死**，以 `regulatory-monitor` 拉取的最新为准。

**离线基线** `references/regulatory_baseline.md`：顶部标注「最后刷新 YYYY-MM-DD」。**凡涉及注册/合规，若基线超 6 个月，必须先触发 `regulatory-monitor` 复核再作答**。

**周期性维护**：`scripts/registry_cli.py stale` 列过期 → 结合 `regulatory-monitor` 批量刷新；`stats` 盘点新鲜度；`list --type X` 查看某类。

## 资源
- `scripts/registry_cli.py`：自我成长引擎（query/add/list/stale/stats，6 个月新鲜度）。纯 Python，无第三方依赖。
- `scripts/seed_registry.py`：写入稳定方法选型与药典/指导原则种子基线；首次运行生成 `data/registry.json`。
- `references/regulatory_baseline.md`：ChP2025/USP/EP/NMPA/CDE/FDA/EMA/ICH 基线（含刷新日期，联动 regulatory-monitor 更新；含本地库成长说明）。
- `references/method_dev.md`：技术选型、色谱条件、检测策略、眼科/耳科专项。
- `references/validation.md`：ICH Q2(R2)/ChP 验证项目与可接受标准逐表。
- `references/sample_prep.md`：混悬/凝胶/乳剂/植入剂前处理与回收率验证。
- `references/regulatory_baseline.md`：ChP2025/USP/EP/NMPA/CDE/FDA/EMA/ICH 基线（含刷新日期，联动 regulatory-monitor 更新）。
- `scripts/method_metrics.py`：输入线性/准确度/精密度数据，输出 r、斜率、截距、回收率、RSD 与可接受判定。纯 Python，无第三方依赖。

## 注意
- 不臆造标准：不确定某药典具体通则号或限度，标注「待核实（建议 regulatory-monitor/CNIPA-ChP 复核）」，不给出看似权威但未经证实的数值。
- 涉及结构/谱图：优先 SMILES/IUPAC；图谱说明由用户侧 ChemDraw/色谱软件生成。
- 与注册/立项联动：分析方法若绑定化合物专利或关键质量属性（CQA），提醒先做 FTO/CMC 评估（联动 patent-disclosure-skill / regulatory-monitor）。
- 与姊妹 skill 协同：`synthesis-route-assistant`（杂质溯源）、`formulation-dev-assistant`（CQA 来源）、`regulatory-monitor`（法规自动更新）。
- 自我成长纪律：每次给出方法/通则结论后，若条目来自查询且已核实，须通过 `registry_cli.py add` 沉淀进 `data/registry.json`；涉及版本修订的（如 ICH Q2(R2)、ChP 通则），以 `regulatory-monitor` 拉取的最新为准，不写死版本号。
