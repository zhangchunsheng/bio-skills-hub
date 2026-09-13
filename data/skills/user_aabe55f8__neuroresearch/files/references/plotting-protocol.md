# 投稿级图表绘制协议（Prism 风格，纯 matplotlib 兜底实现）

本文件把 GraphPad Prism 的作图心智模型翻译为可直接落地的 **matplotlib + seaborn + scipy 规范约束**，作为 **prism-style-plot 引擎（`scripts/prism_theme.py`）不可用时的兜底实现**。

> **默认路径（推荐）**：`neuroresearch` 已内建 Prism 风格绘图引擎——`scripts/prism_theme.py`（`apply_prism_theme` / `get_figsize` / `prism_boxplot` / `prism_bars` / `prism_violin` / `prism_survival` / `add_pairwise_brackets` / `build_stats_report` / `set_nice_ylim` 等）+ `scripts/ensure_env.py` 环境引导。凡可调用 bundled 库，**一律优先走 `references/prism-style-plot.md` 的引擎流程，不要手搓**。本文件仅在 bundled 库无法运行（极端环境）时作为等效 inline 参考；其规范约束（四原则、线宽、均衡抖动、紧凑 Y 轴、精确 p 值）**始终生效**。
>
> **R 用户**：R 在技能中定位于**生信分析**（RNA-seq 差异表达 / 富集，见 `bioinformatics.md`），不再承担绘图；投稿级图统一走本技能 Python 引擎（`prism_theme.py`）。如需在 R 内出图，请直接使用 ggplot2 原生写法（通用模板见 `statistical-analysis.md` §6.2）。

---

## 核心四原则（贯穿所有绘图）

1. **数据表驱动，而非图形驱动**：先识别数据属于哪种表（8 种判别见 `table-mapping.md`），表类型决定可画什么图、做什么统计。绝不先问"要什么图"。
2. **统计与绘图联动**：误差棒与显著性星号是统计结果的视觉呈现，画图前必须先完成统计（方法见 `statistical-analysis.md §一~§四-B`）。
3. **展示原始数据点**：现代期刊（Nature / Cell 系列）要求叠加个体散点，纯空心柱状图不推荐。默认叠加散点。
4. **期刊规范优先**：L 形坐标轴、色盲友好配色、统一无衬线字体、明确标注误差线类型。

---

## Phase 0：识别数据表类型

按 `references/table-mapping.md` 的判别规则，把用户数据归类到 8 种表之一（XY / Column / Grouped / Contingency / Survival / Parts of whole / Multiple variables / Nested）。数据来源可能是 CSV/Excel、粘贴文本表、或对话描述结构。**不确定时把判别结果与依据展示给用户确认，再继续**——表类型认错后面全错。

## Phase 1：选择图形类型

按表类型查 `table-mapping.md`「图型选择速查」，默认选"推荐图型"，同时给用户 2–3 个备选确认（Column→带散点柱状图/箱线图/小提琴图；Grouped→分组柱状图/箱线图/意大利面条图；XY→散点+拟合；Survival→KM 曲线；Contingency→计数柱状图等）。涉及组间显著性展示的图（Column/Grouped）默认：个体散点 + 误差棒 + 星号；纯展示性图（Parts of whole、Contingency）不标显著性。

## Phase 2：统计-绘图联动

按决策树选方法（Python 实现见 `statistical-analysis.md §四-B`；engine 路径直接用 `prism_theme.oneway_anova_tukey` / `ttest_two_groups` 等）：

- **2 组比较** → t 检验（先判定配对/非配对，判据见 `statistical-analysis.md §二`；非正态或小样本用 Mann-Whitney / Wilcoxon 配对）
- **≥3 组、单因素** → One-way ANOVA + 事后多重比较（Tukey 默认；方差不齐用 Welch ANOVA + Games-Howell）
- **两因素** → Two-way ANOVA（含交互项，报告主效应与交互效应）
- **生存** → log-rank 检验（Kaplan-Meier）
- **计数列联** → 卡方 / Fisher 精确检验

**硬性规则**：多组比较严禁两两 t 检验（成倍放大假阳性），必须 ANOVA + 事后检验一次完成。计算每组 n、均值、误差（SEM 用于柱状图、SD 用于分布展示）。若用户提供已发表的统计结果（如 p 值表），直接使用并跳过计算，但图注注明来源。

## Phase 3：Prism 风格美化（规则要点；代码一律用 `prism_theme.py`）

> 引擎可用时直接调用 `prism_theme` 库函数；以下为必须遵守的规则约束，等效 inline 实现参考 `scripts/prism_theme.py` 源码。

### 形态预设（get_figsize 等效）

| 形态 | figsize（宽×高 cm，引擎换算 inch） | 场景 |
|---|---|---|
| **tall（默认）** | 3 × 5 | 单面板期刊图、柱/箱线图，高瘦构图突出数据主体 |
| square | 5 × 5 | 单图均衡、散点相关图 |
| wide | 7 × 5 | 多组对比、时间序列、并排多面板 |

用户未提形态时**默认 tall**，不必询问。

### 统一美化清单（强制）

- **L 形坐标轴**：隐藏上、右边框，仅留左、下（`ax.spines['top'/'right'].set_visible(False)`）。
- **线条粗细总则（默认 0.75 pt，强制）**：所有线条统一默认 `LW = 0.75` pt——柱/箱描边、errorbar（`elinewidth`/`capthick`）、显著性 bracket、折线、散点描边。**禁止**柱描边 1.0+ 而 errorbar/bracket 用别的粗细；用户明确指定线宽时以其为准。
- **样本点布局（强制，所有叠加样本散点的图通用）**：每点 x = 组中心 `cx` + 抖动，要求①**左右对称均匀分布**（uniform 抖动、不偏向一侧）；②**左右侧点数均衡**（以 `cx` 为轴，左 n//2 点 = 右 n//2 点；n 奇数时余 1 点居中）。抖动半幅 max_j = `0.25 × 柱/箱宽 w`（默认 jitter_ratio=0.5，即占柱宽半宽的 50%；再扣除点半径，点绝不越界）。**统一用镜像均衡抖动函数 `jitter_offsets(...)`**（实现见 `scripts/prism_theme.py`，勿重复手写）。**禁止 `sns.stripplot(jitter=True)`**（无法保证左右均衡与对称）；点密集或审稿敏感时切 **beeswarm**（多列展开、不重叠）。
- **配色**：色盲安全色板，**默认 Okabe-Ito（8 色）**：`#E69F00/#56B4E9/#009E73/#F0E442/#0072B2/#D55E00/#CC79A7/#000000`；印刷可切 Paul Tol；单组优先灰度。
- **字体**：Arial/Helvetica 类无衬线，轴标题 12–14pt，刻度 10–12pt。
- **误差线**：柱状图默认 **Mean±SEM**；箱线图展示**中位数/四分位距**，图注须注明（勿把箱线图误报为 Mean±SEM）。
- **显著性标注**：星号 + 连接 bracket（bracket 线高不超过图区 95%）。星号分级**必须从最严阈值往下判断**（否则 p<0.05 全变 `*`）：p≥0.05 不标 ns（默认，见下）；**0.05 ≤ p < 0.1 边缘显著直接标精确 p 值**（如 `p=0.073`）；p<0.05→`*`、p<0.01→`**`、p<0.001→`***`、p<0.0001→`****`。多组两两比较 bracket 按跨度分层堆叠防重叠（参考 `prism_theme.add_pairwise_brackets`）。
- **y 轴收尾（强制，紧凑方案）**：以数据跨度 `span = y_max − y_min` 为基准，防止顶端刻度被裁 + 防止星号标注后顶部留白过多：
  1. **bracket 紧凑布局**：`y_base = y_max + 0.03*span`（bracket 底部紧贴数据最高点上方 3% 跨度）；层高 `H_LAYER = 0.05*span`；竖线 `0.015*span`；星号 `y + 0.018*span`（`va='bottom'`）。
  2. **步长三阶段选择**（50→20→10→5→2→1 从粗到细）：优先第一个同时满足 **4 ≤ 刻度数 ≤ 9 且 取整损失 ≤ 20% 跨度** 的步长；全不满足则在同密度候选中取损失最小者。`y_top = ceil(top_raw/step)*step`，`y_bot = floor(y_min/step)*step`，**显式** `set_ylim` + `set_yticks(arange(...))`——顶端刻度必落在 y_top 且不被裁。**不要用** `MaxNLocator`（可能超上限裁刻度）。
  3. **savefig 一律加 `pad_inches`**：`bbox_inches='tight', pad_inches=0.15`。
  4. **顶部留白量化验证**：`(ylim_top − max(bracket_tops)) / span ≤ 0.26`（设计余量 0.08 + 取整损失 ≤ 0.18）。

> **⚠️ 已知坑（v2.0.40+ 实战）：`set_nice_ylim()` 早退导致顶端刻度缺失**
> - **现象**：先预置过高 ylim（如 `ax.set_ylim(0, ymax*1.35)`）再调 `set_nice_ylim(ax)`，Y 轴顶端无刻度标签、留白一大段——刻度停在 matplotlib 默认值（如 200）而 `ylim_top=229.5`。
> - **根因**：`set_nice_ylim` 在 `target ≤ 当前 y1` 时直接 `return`，**不重设刻度网格**；预置 ylim 越高越容易触发早退，刻度永远不刷新。
> - **对策（多组显著性 bracket 图标准流程，已实测）**：
>   1. 初始 ylim 贴近数据：`ax.set_ylim(0, ymax*1.05)`（bracket 布局按数据跨度 `span=ymax−ymin` 计算，不依赖初始 ylim）；
>   2. 手动画 bracket（替代 `add_significance_brackets` 的自动扩展）：`y_base = 该组 y_max + 0.03*span`，`H_LAYER = 0.05*span`，星号 `va='bottom'` 于 `y_base + H_LAYER + 0.018*span`；
>   3. 收尾用引擎函数求漂亮步长：`final_top, step = _nice_ylim_top(top_raw, 0.0)`，其中 `top_raw = max(bracket 顶部) + 0.018*span`（p≥0.05 的不画 bracket，勿计入）；
>   4. **显式** `ax.set_ylim(0, final_top)` + `ax.set_yticks(np.arange(0, final_top + step*0.5, step))`——顶端刻度必等于 `ylim_top` 且带标签；
>   5. 程序化验证：`(final_top − top_raw)/span ≤ 0.26`，并在脚本中 `print` 出来。
> - **要点**：`add_significance_brackets` 仅在 bracket 超出当前 ylim 时才自动收尾；不超出时（预置过高/显式传 `y` 偏低）刻度就停在旧网格。因此**凡预先设置过 ylim 的图，最后都必须显式 `set_yticks` 收尾一次**。
- **输出**：PNG（300 dpi）+ PDF（矢量）双格式。

### 箱线图 / 分组柱状图标准画法（要点）

- **箱线图（Column/Grouped）**：`sns.boxplot` 画箱体 + 手动 `scatter` 叠加个体点。**必须显式传 `palette=` + `hue`** 让每个箱体按色板上色（只后置 `set_facecolor` 会让所有箱体变默认蓝，这是已知坑）；箱体填充透明度 0.55；散点必须用 `jitter_offsets` 镜像均衡抖动（**禁止 `sns.stripplot`**）。**⚠️ 个体散点必须跟随组别颜色**（不得用 `color='black'`，否则无法区分组）+ 黑色描边（`edgecolor='black'`, `linewidth=LW`）。完整代码见 `scripts/prism_theme.py` 的 `prism_boxplot`。
- **分组柱状图（Grouped 表，三条强制规则）**：
  - **规则 A：柱间留 25% 距离**——同组内相邻柱间距 = `0.25 × 柱宽`（柱宽 w≈0.20–0.25，相邻柱中心距 = 1.25w），matplotlib 手动布局，勿用 seaborn `dodge`（无法精确控制）。
  - **规则 B：散点柱内左右均匀分布且左右点数均衡**——抖动用统一 `jitter_offsets(...)`（实现见 `scripts/prism_theme.py`）；y 为真实观测值；颜色跟随组别（hue 色板）+ 黑色描边。
  - **规则 C：errorbar 线宽与柱描边一致**——`elinewidth`/`capthick` 必须等于柱 `edgecolor='black'` 对应的 `linewidth`（默认均取 `LW = 0.75`）。
  - 完整代码见 `scripts/prism_theme.py` 的 `prism_bars`。

---

## Phase 4：交付物规范

1. **图表保存**：`{描述}_{表类型}_{图型}.png` 与同名 `.pdf`，命名具体（如 `tnfa_dose_column_bar.png`）。
2. **图注（Figure Legend）必须含精确 p 值**（除星号外给数值，多数期刊要求）：
   > Data are mean ± SEM, n=6 per group. One-way ANOVA with Tukey's post hoc test: Control vs Drug-Low p=0.134 (ns); Control vs Drug-High p=1.04e-5 (****).
   - **p 值格式铁律**（权威定义见 `prism-style-plot.md`「核心规则（权威源）」）：一律输出 scipy 计算出的**实际精确值**，禁止 `<` 阈值写法（`p<1e-6`、`p<0.001` 均禁止）。p≥0.001 写 3 位小数 `p=0.134`；p<0.001 用科学计数法保留 3 位有效数字 `p=2.04e-4`（指数去前导零）。星号照常给出。
   - **下溢边界**：当 p 值低于双精度可表示范围（软件返回 `0.0`，常见于 Tukey 等极显著比较）时，唯一诚实的表示是 `p=<1e-300`（Prism 同显示 `<0.0001`）；这不违反上条铁律。实现：`fmt_p` 开头判 `if p <= 0 or p < 1e-300: return '<1e-300'`。
3. **完整统计报告（与图同名）**：生成 Markdown 报告（含描述统计、前提检验、检验统计量+自由度、事后比较、效应量、Figure Legend），保存为 `{图名}_report.md`。覆盖：anova_tukey（≥3 组）、ttest（2 组）、twoway（Grouped）、survival（生存）、contingency（列联）。报告结构对齐 `statistical-analysis.md §五` 七要素。**描述统计须给出每组 n、均值、SD 与 SEM（SEM = SD/√n，切勿误用 Mean/√n）**；箱线图图注注明"中位数 (IQR)"，柱状图注明"Mean ± SEM"。
4. 后续修改（换图型、误差线、配色、形态）回到对应 Phase 调整后重出图。

---

## 与其他模块的衔接

- 表类型判别：`table-mapping.md`（8 种表判别 + 图型选择速查）。
- 统计实现：复用 `statistical-analysis.md §四-B` 的 Python 代码（t 检验 / ANOVA+Tukey / 双因素 / 生存 / 功效）。
> 依赖：matplotlib / seaborn / scipy / statsmodels / lifelines / pandas；缺失按 `python-runtime.md` 自动安装。engine 路径用 `scripts/ensure_env.py` 引导。
- 中文期刊：图注与报告可按 `citation-formatting.md` 的中文规范调整表述，但统计呈现规则不变。

---

## Phase 5：期刊 preflight 检查表（出图前必过）

> 借鉴 qinyan-nature-figures 的 *preflight validation* 理念：图交付前逐项核对，**任一不过则返工**，避免投稿后因格式被技术性退稿（desk reject / 返修补图）。

| 检查项 | 标准 | 不合格示例 |
|--------|------|-----------|
| 分辨率 | 位图 ≥300 dpi（线图/电镜 ≥600） | 72 dpi 截图 |
| 色彩空间 | 屏幕用 RGB；印刷刊要求 CMYK 时转；**色盲安全** | 红绿对比（非色盲安全） |
| 字体 | 无衬线（Arial/Helvetica）；嵌入；≥6 pt | 宋体/未嵌入字体缺失 |
| 线宽 | 主线条 ≥0.5 pt，坐标轴线 ≥1 pt | 0.2 pt 细线印刷消失 |
| 面板标注 | 多面板图 A/B/C 左上角统一字号 | 缺面板字母 |
| 尺寸 | 单栏 ≤85 mm / 双栏 ≤170 mm（按刊）；版心留白 | 超版心被压缩 |
| 文件格式 | TIFF/EPS/PDF（按刊）；避免 JPEG 有损 | 投稿要求 TIFF 却交 PNG |
| 图内文字 | 轴标题/图例 ≥8 pt，不与数据重叠 | 文字压在线条上 |
| 图注自足 | 看图文不读正文能懂（含统计、n、缩写） | 图注缺 n/统计 |

**交付门禁**：PNG（300dpi）+ PDF（矢量）双格式齐备 + 上述 9 项全过 → 才算交付（与 Phase 4 第 1 条呼应）。

## Phase 6：机制通路图 / Graphical Abstract 协议

> 针对"机制解释"（Discussion/立项依据）与期刊 Graphical Abstract 需求。统计图走 Prism 引擎；**机制示意图是另一类产物**，按本 Phase 规范。

### 6.1 工具选择
| 工具 | 适用 | 备注 |
|------|------|------|
| **BioRender** | 专业机制/通路图（期刊级） | 最快、图标库全；注意授权与导出格式 |
| matplotlib 手绘 | 需**可复现脚本**、简单框图/箭头链 | 见 `prism-style-plot.md §五` 代码骨架 |
| graphviz / mermaid | 流程/因果链快速草稿 | 非出版级，仅内部 |

### 6.2 内容规范
- **因果链单向清晰**：上游 → 下游（如 细胞A 激活 → 分子X↓ → 细胞B 死亡表型 → 损伤病理），不画循环论证。
- **分子/细胞类型标注**：每个节点标分子名 + 细胞定位（如 "分子X (细胞B)"）。
- **统一配色 + 图例**：与正文统计图配色一致（Okabe-Ito）；激活/抑制用箭头样式区分（→ 激活，⊣ 抑制）。
- **引用标注**：机制图中直接引用的关键结论标文献序号。
- **Graphical Abstract**：≤1 图概括核心发现，不堆数据；含研究模型（如 TBI 脑挫伤）。

### 6.3 课题示例（CNS 损伤机制轴）
```
[细胞A 激活]
      │ 分泌因子/外囊泡
      ▼
[分子X 表达下调]  (细胞B, 条件培养基→靶细胞 验证)
      │
      ▼
[细胞B 死亡表型]  (关键执行分子 活化)
      │
      ▼
[损伤继发性病理加重]
```
- 落地：用 BioRender 出出版级图；或 matplotlib 画框+箭头（见 `prism-style-plot.md §五`）。
