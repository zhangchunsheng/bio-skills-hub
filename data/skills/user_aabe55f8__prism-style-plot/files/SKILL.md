---
name: prism-style-plot
description: >
  Draw publication-grade scientific charts for biomedical / life-science papers
  following the GraphPad Prism mental model: first identify the data table type
  (XY / Column / Grouped / Contingency / Survival / Parts-of-whole / Multiple
  variables / Nested), then pick the chart and statistics, then apply Prism-style
  polish (L-shaped axes, colorblind-safe palettes, individual data points,
  significance brackets, tall/square/wide canvas). Outputs PNG (300 dpi) + PDF +
  figure legend + full statistics report. Triggers: graphpad, prism, 用 GraphPad
  画图, Prism 风格, 科研绘图, 论文配图, 散点柱状图, 箱线图, 小提琴图, 分组柱状图,
  XY 散点线图, 生存曲线, 显著性星号, 误差棒, or uploading experimental data to be
  plotted Prism-style. Not for: business reports, interactive visualization
  (Plotly/Bokeh), 3D charts, fabricated data.
description_zh: 按 GraphPad Prism 作图逻辑绘制投稿级科研图表（生物医学/生命科学论文配图）
description_en: Publication-grade scientific plots in GraphPad Prism style (Python/matplotlib)
version: 2.7.5
license: CC BY-NC-SA
agent_created: true
metadata:
  version: 2.7.5
  category: scientific-visualization
  sources:
    - GraphPad Prism user guide (graph types, error bars, statistics conventions)
    - Nature / Cell series figure guidelines (individual data points, colorblind-safe palettes)
    - matplotlib / seaborn / scipy documentation
---

# Prism Style Plot

## 概述

把 GraphPad Prism 的作图心智模型翻译成 Python（matplotlib + seaborn + scipy）：**先看数据是什么表，再决定画什么图和做什么统计**，最终输出符合期刊规范的投稿级图表。目标是让不会写代码的科研人员，说出"我要一张 Prism 那种图"，就能得到一张可以直接进论文的图。

## 你的工作方式

GraphPad 的精髓不是某个图形，而是四件事，这四件事贯穿本技能所有流程：

1. **数据表驱动，而不是图形驱动**。Prism 的第一步永远是选择数据表格式——表的类型决定了你能画什么图、能做什么统计。拿到数据后先识别它属于 8 种表里的哪一种，而不是先问用户"想要什么图"。
2. **统计与绘图联动**。图上的误差棒和显著性星号不是装饰，而是统计结果的视觉呈现。统计方法由数据结构决定（组数、因素数、是否配对），画图前必须先完成统计。
3. **展示原始数据点**。现代期刊（Nature 系列、Cell 系列）普遍要求图上叠加个体数据点，纯空心柱状图已不被推荐。本技能所有统计图默认叠加散点。
4. **期刊规范优先**。L 形坐标轴（去掉上边和右边框）、色盲友好配色、统一无衬线字体、明确标注误差线类型——这些是审稿人看得见的"专业感"。

## 环境准备（Phase 0 之前必做，防止反复重装依赖）

**每次任务第一步**：先运行 `scripts/ensure_env.py` 得到受管理 venv 解释器路径，之后**所有** `python xxx.py` 都用这个解释器，不要再回到基础解释器。

```bash
PY=$(python scripts/ensure_env.py)   # 打印 venv 解释器绝对路径
$PY your_plot.py                     # 之后一律用 $PY 运行绘图脚本
```

`ensure_env.py` 已做三件关键事（分享给他人才不会重蹈覆辙）：

1. **只用 venv 自己的解释器判定依赖是否齐全**，装过就秒退（约 3 秒、不重新下载），并打印路径。
2. **venv 路径不硬编码用户名**：从 `sys.executable` 动态推导受管理结构 `<root>/binaries/python/versions/<ver>/python[.exe]` → venv 落在 `<root>/binaries/python/envs/default`，跨机器/跨平台（Windows `Scripts`、POSIX `bin`）通用。
3. **当前解释器若已能 import 全部依赖则直接复用**（含"已身处正确 venv"的情况），绝不重复建 venv。

> ⚠️ **致命坑（务必转达给使用者）**：切勿用**基础解释器**（如 `binaries/python/versions/<ver>/python.exe`）去 `import matplotlib` 做"装没装"的判定——它看不到 venv 里的包，会误报 `ModuleNotFoundError`，从而**每次任务都触发重装**。依赖是否存在，**一律以 venv 解释器（`ensure_env.py` 的输出）为准**。

## Phase 0：识别数据表类型

这是最关键的一步，决定了后续所有动作。读取 `references/table-mapping.md`，按其中的判别规则把用户数据归类到 8 种表之一：

- **XY 表**：每个点由 X 和 Y 两个值定义（如剂量-响应、标准曲线）
- **Column 表**：一个分组变量（Control vs 处理组）
- **Grouped 表**：两个分组变量（如 时间×药物）
- **Contingency 表**：计数/频数数据（如 存活 vs 死亡的例数）
- **Survival 表**：生存时间 + 事件/删失标记
- **Parts of whole 表**：各部分占整体的比例（饼图）
- **Multiple variables 表**：每行一个观测、每列一个变量的宽表
- **Nested 表**：层级嵌套设计（如 方法→教室→学生）

数据来源可能是 CSV/Excel 文件、粘贴的文本表格，或对话中描述的结构。**不确定时，把判别结果和依据展示给用户确认，再继续**——表类型认错，后面全错。

**默认约定：读表自动设 y 轴标签** — 当数据来自 **CSV/Excel 文件**、且用户**未显式指定** y 轴标签时，**自动用数值列表头作为 ylabel 默认值**：
- `read_table(path)` 读取文件后会返回 `ylabel`（long 格式的 value 列名，已做基础清洗：去换行、合并多余空格；wide 格式无单一数值列名时 `ylabel=None`）。
- 拿到 `ylabel` 后直接 `ax.set_ylabel(res["ylabel"])` 即可，无需用户再给。
- 用户仍可随时覆盖此默认（显式给标签时优先用用户的）。
- 宽格式（每列一组）因没有"数值列名"，`ylabel` 回退 `None` → 此时沿用该图型模板默认（如 Column→`"Response (a.u.)"`）或请用户指定。
- 列名常非投稿级（缩写/缺单位），自动 ylabel 只是合理默认，**最终投稿标签建议你确认/润色**（如补 `(fold change)`）。
- 注意：仅"来自文件"时自动套用；对话里粘贴的数值表不触发此默认（按既有规则处理）。

**读表健壮性（v2.7.5，坏输入不再直接崩）** — `read_table` / `read_excel_sheets` 已内建以下容错，**不要**再手写临时补丁去预处理用户文件：

- **编码自动回退**：`utf-8-sig → utf-8 → gbk → gb18030 → big5 → latin-1`。Windows 版 Excel「另存为 CSV」默认 GBK，中文表头不再抛 `UnicodeDecodeError`。
- **分隔符自动嗅探**：逗号 → 制表符 → 分号 → 竖线。仪器/统计软件导出的 Tab 分隔 `.txt` 可直接读，无需先转 CSV。
- **数值清洗**：去首尾空格；千分位 `"1,234"` → `1234`（仅"数字,三位数字"形态，不误伤 `1,5` 这类欧式小数）；`ND` / `—` / `缺失` / `NA` / `null` 等占位符 → NaN 自动剔除。
- **友好报错**（替代裸 traceback）：文件不存在、空文件、CSV 改名成 `.xlsx`、列名/sheet 名写错 → 均抛**中文可行动**错误，并在提示里列出可用列 / 可用 sheet 名。
- **绝不静默产出错误数据**（关键）：分组列必须满足"去重取值数 ∈ [2, max(2, 行数//2)]"才算分组变量——否则像「备注」「编号」这类常量/自由文本列会被误判为分组列，**静默丢掉真正的实验组**（v2.7.4 及更早的真实 bug：含备注列的宽表被误判为长表，Model 组整列消失且无任何报错）。
- **被忽略的列写进 `notes`**：`read_table` 返回值新增 `"notes": list[str]`（自动识别的分隔符、被忽略的列名等）。**拿到 `notes` 后必须原样转述给用户**——被忽略的列可能意味着数据没被完整使用，属学术严谨性范畴，严禁静默吞掉。典型写法：
  ```python
  res = read_table(path)
  for n in res.get("notes", []):
      print("提示:", n)          # 或拼进给用户的回复里
  ```

## Phase 1：选择图形类型

按表类型查 `references/table-mapping.md` 的映射表，得到该表支持的图型列表。默认选择推荐的"Prism 默认图型"，同时给用户 2-3 个备选让其确认：

| 表类型 | 默认图型 | 常见备选 |
|---|---|---|
| Column | 带散点的柱状图（Mean±SEM） | 箱线图+散点、小提琴图+散点、带散点的线图 |
| Grouped | 分组柱状图+散点 | 分组箱线图、意大利面条图（重复测量时） |
| XY | 散点+连线 | 仅散点、折线图、拟合曲线 |
| Survival | Kaplan-Meier 曲线 | — |
| Contingency | 分组柱状图（计数） | 堆叠柱状图 |
| Parts of whole | 饼图/环形图 | 堆叠柱状图 |
| Nested | 嵌套柱状图 | — |
| Multiple variables | 按用户意图选图 | 散点矩阵、箱线图分面 |

涉及"统计显著性展示"的图（Column/Grouped）默认展示个体散点 + 误差棒 + 星号；纯展示性的图（Parts of whole、Contingency）不标注显著性。

## Phase 2：统计分析

读取 `references/statistics-guide.md`，按决策树选择统计方法：

- **2 组比较** → t 检验（先判定配对/非配对；非正态或小样本考虑 Mann-Whitney / Wilcoxon 配对检验）
- **≥3 组、单因素** → One-way ANOVA + 事后多重比较（Tukey 默认，方差不齐时用 Welch ANOVA + Games-Howell）
- **两个因素** → Two-way ANOVA（含交互作用项，报告主效应与交互效应）
- **生存数据** → log-rank 检验（Kaplan-Meier 曲线；≥3 组自动含整体 χ² 检验 + 两两比较）
- **计数列联** → 卡方检验 / Fisher 精确检验

硬性规则：**多组比较严禁两两 t 检验**（成倍放大假阳性），必须 ANOVA + 事后检验一次完成。计算每组 n、均值、误差（SD 或 SEM，默认 SEM 用于柱状图、SD 用于箱线图外的分布展示），生成显著性标注（混合规则，见 Phase 3 标注细节）：
- p < 0.05（显著）：星号 `*`（p<0.05）、`**`（p<0.01）、`***`（p<0.001）、`****`（p<0.0001）
- **0.05 ≤ p < 0.1（边缘显著）：直接标注精确 p 值**（如 `p=0.073`、`p=0.098`）
- **p ≥ 0.1：不标注**（默认不标 ns；`include_ns=True` 可恢复 "ns" 文本）

**统计函数返回值类型（调用时最容易踩的坑）**：
- `ttest_two_groups(a, b)`（2 组）返回 **tuple** `(statistic, p_value, 方法名)`，如 `stat, p, method = ttest_two_groups(a, b)`；`paired=True` 时同样返回 tuple
- `mann_whitney_u(a, b)`（非参数独立样本）返回 **tuple** `(stat, p, "Mann-Whitney U")`
- `wilcoxon_signed_rank(a, b)`（非参数配对）返回 **tuple** `(stat, p, "Wilcoxon signed-rank")`
- `oneway_anova_tukey(groups, labels, var_equal="assumed", posthoc="auto")`（≥3 组）返回 **dict** `{"method", "anova_p", "pairwise": [(label_i, label_j, p), ...], "f_stat", "df1", "df2", "welch": bool, "posthoc": str, "var_test"}`。`var_equal`（方差不齐处理，对齐 GraphPad Prism 8+）：
  - `"assumed"`（默认，向后兼容）：假设方差齐 → 标准 One-way ANOVA + Tukey HSD
  - `"welch"`：不假设方差齐 → **Welch ANOVA**（Welch-Satterthwaite 校正 df），事后由 `posthoc` 决定
  - `"auto"`：先做 Levene（center='median'，即 Brown-Forsythe，Prism 推荐）检验，p<0.05 自动切 Welch，否则回落标准 ANOVA
  - `posthoc`（仅 Welch 分支生效；assumed 分支永远是 Tukey）：`"auto"`（默认，按 Prism 推荐：**max(组内 n) > 50 → Games-Howell，≤50 → Dunnett T3**）、`"games_howell"`（q 统计量 + 学生化极差分布）、`"dunnett_t3"`（Welch t + 未取整 df + 单步 Sidak 校正，等价 SMM 分布，Dunnett 1980）、`"welch_t"`（**不校正**，每对直接 Welch 校正 t 检验 = Prism "Don't correct for multiple comparisons"）
  - ⚠️ 小样本（如 n=3）下 Levene 检验力极低、几乎检不出方差不齐——**auto 模式在 n 小时通常不切换**；若实验设计或先验知识提示方差不齐（如处理组方差系统性更大），应显式用 `var_equal="welch"`，不要依赖 auto 自动判定
  - `build_stats_report(..., var_equal=..., anova_posthoc=...)` 同样支持该参数；方差不齐但未切 Welch 时报告会明确标注"下方为假设方差齐性的标准 ANOVA 结果"，不再自相矛盾；Welch 分支的校正表（Dunnett T3 / Games-Howell）**额外附一列 `p (Welch t, uncorr)`**（未做多重比较校正的参考值，审稿人对照友好；`anova_posthoc="welch_t"` 本身即未校正，不重复加列）
- `build_stats_report("ttest")` 若 Shapiro p<0.05 或 min(n)<30，**自动追加** Mann-Whitney U / Wilcoxon 符号秩补充检验 + rank-biserial r 效应量；不替换主 t 检验结论
- 一组返回值可直接喂给 `add_pairwise_brackets(ax, res["pairwise"], labels=...)`（后者接收 `(label_i, label_j, p)` 元组列表）

若用户提供了自己的统计结果（如已发表的 p 值表），直接使用并跳过本阶段计算，但要在图注中注明统计方法来源。

## Phase 3：Prism 风格美化

导入 `scripts/prism_theme.py`，使用其中封装的主题和辅助函数：

```python
from prism_theme import (apply_prism_theme, recommend_figsize, prism_boxplot,
                         prism_violin, add_significance_brackets,
                         add_pairwise_brackets)
```

**第一步：确定图形态（GraphPad 的 tall / square / wide 预设）**

用 `recommend_figsize(table_type, n_groups, shape)` 确定画布，**三级优先级**（预设以 **cm** 为单位；函数内部已换算成 matplotlib 的 inch，调用方无需关心）：

1. **用户显式关键词最高优先**——说"高/高瘦/tall"、"方/square"、"宽/wide"（中英文别名均可识别）→ 直接用该形态，覆盖一切默认建议；
2. **数据表类型默认建议**（用户没提形态时自动生效，不必询问）——`recommend_shape(table_type, n_groups)`：
   - **Column / Grouped**：按**总分组数**分档——**<5 组 → tall**、**5–8 组 → square**、**>8 组 → wide**；
   - **XY → square**、**Survival → square**、**Contingency → wide**；
   - 补充默认：Parts of whole → square、Multiple variables → wide、Nested → tall；
   - **重复测量/时间轨迹类（意大利面条图等，用户偏好）→ 一律 wide**（横向更适合多时间点轨迹，覆盖上述分档建议）
3. **兜底 tall**：表类型未识别、或 Column/Grouped 缺分组数时回退 tall（与原 `get_figsize` 默认一致）。

| 形态 | 画布尺寸（cm，宽×高） | 适合场景 |
|---|---|---|
| tall | 3 × 5 | 单面板期刊图、柱状图/箱线图等统计图，高瘦构图让数据主体突出 |
| square | 5 × 5 | 单图均衡展示、散点相关图 |
| wide | 7 × 5 | 多组对比、时间序列、需要并排的多面板图 |

```python
from prism_theme import recommend_figsize
fig, ax = plt.subplots(figsize=recommend_figsize("column", n_groups=3))   # 3 组 → tall
fig, ax = plt.subplots(figsize=recommend_figsize("grouped", n_groups=6))  # 6 组 → square
fig, ax = plt.subplots(figsize=recommend_figsize("xy"))                   # XY → square
fig, ax = plt.subplots(figsize=recommend_figsize("contingency"))          # → wide
fig, ax = plt.subplots(figsize=recommend_figsize("column", n_groups=3,
                                                 shape="wide"))           # 关键词覆盖
```

统一执行以下美化（这是 Prism 用户手册和期刊规范的交集）：

- **L 形坐标轴**：隐藏上边框和右边框，只保留左、下
- **样本点布局**（**镜像均衡抖动，投稿强制规则**）：默认 `layout="jitter"` + `balanced=True`，左右各取 `n//2` 点镜像分布，**初值采样就避开中线带**保证左右对称不偏侧，n 奇数时 1 点**随机偏侧**（左右差 ≤1）。**去规律化**：min_sep 微调改用**随机方向 + 随机步长**（`rng.choice([-1,1]) × rng.uniform(0.6,1.1)·d_x`），删除等距排开兜底，物理放不下时接受轻微重叠 + **透明度补偿**（`_apply_overlap_alpha` 按组内最大重叠密度压低填充透明度至 ≥0.30，无重叠时原样返回）。**布局硬约束**：`max_j ≤ width/2`（点绝不溢出 box/柱外）；**画点前必先设 xlim/ylim**（`prism_bars`/boxplot/violin 内部已预设；手写多组循环务必 `set_xlim(-0.5, n-0.5)` + `set_ylim(...)` 置于画点前，否则点径换算 `d_x/d_y` 漂移导致前几组挤在一起）。点密集或审稿敏感可切 `layout="beeswarm"` 多列展开。**实现级细节**（mid_b/rng.uniform 公式、`_apply_overlap_alpha` 判据与公式、`jitter_ratio` 取值、接口签名）：见 `references/scatter-layout.md`。**已覆盖所有叠加散点的图型**：`prism_bars`/`prism_boxplot`/`prism_violin`/`add_individual_dots`
- **散点大小与透明度**（**同图所有样本点同大**，期刊规范）：`common_point_size(总数, 组数)` 自适应——公式 `pt = clip(5·√(4/avg_n)·(3/组数)^0.25, 2.0, 5.0)` pt（窗口 2.0–5.0，组数指数 0.25 < 样本量指数 0.5，样本量主导）。**关键档位**：

  | avg_n | 组数 | pt | 场景 |
  |---|---|---|---|
  | 4 | 3 | 5.0 | 小样本满点（上限）|
  | 8 | 3 | 3.54 | 敏感段（明显缩小）|
  | ≥32 | — | 2.0 | 大样本（下限）|

  **透明度**：填充与描边统一；`auto_dot_alpha` 按 n 自适应（n 大→越透明防重叠掩盖），含 `_apply_overlap_alpha` 同步压低。
- **配色**：色盲安全色板（来源：图片中收录的标准 Colorblind-safe 方案）——默认 **Okabe-Ito**（8 色，分类图首选）；印刷场景可切 **Paul Tol Bright**（7 色）；多组/复杂图可选 **Paul Tol Muted**（9 色）；高对比屏幕图可选 **IBM Design Library**（5 色）；单组时优先灰度系。用 `get_palette("okabe_ito")` / `get_palette("paul_tol_bright")` / `get_palette("paul_tol_muted")` / `get_palette("ibm_design")` 获取，`palette_sequence()` 取分组配色序列。用户指定配色方案时按需切换。**接口提示**：`get_palette(name)` 返回 **dict**（颜色名→hex，如 `{"blue": "#0072B2", ...}`），不能直接 `[:n]` 切片；要按期刊常用顺序取颜色序列，用 `palette_sequence(name)`（返回 **list**，如 `palette_sequence("okabe_ito")[:2]` 取前两组色）。给 `prism_bars`/`prism_boxplot`/`prism_survival`/`prism_xy_fit` 的 `palette=` 参数传色板名字符串或颜色列表均可
- **字体**：Arial/Helvetica 类无衬线，坐标轴标题 8pt，刻度数字 6pt（整体 −4）
- **误差线**：柱状图默认 Mean±SEM（**error bar 单独绘制且 zorder=6 > 散点 5**，防散点遮盖）；箱线图展示中位数/四分位距，须注明。**"误差线永远最顶层"全局规则（覆盖所有图型）**：柱状图误差棒 zorder=6 > 散点 5；箱线图 median/whisker/cap zorder=4 > 散点 3 > 箱体填充 2；**箱体边框也重绘到 zorder=4**（seaborn boxprops 同时控制填充与边框无法单独提层，方案是填充留 2 + 边框独立线框重绘到 4）——任何图型的误差范围线/中心线/箱体边框都不被样本点覆盖
- **显著性标注**（混合规则）：星号/精确 p 值 + 连接线（bracket）标注组间比较。规则：显著 p<0.05 → 星号；边缘显著 [0.05,0.1) → 精确 p 值（`p=0.073`）；p≥0.1 → 不标。bracket 自动分层防重叠（层高 LH 0.055），**标注底部分类型偏移**（星号 -0.03 span 骑线、p 值 0 在横线），ylim 顶部收尾 ≤ ~1.3×数据最大值（`_nice_ylim_top` max_ticks=9 防刻度拥挤）。**ylim<1 值域**：刻度按量级分级（≥1 保持 0.5 倍数；<1 用 0.05/0.005/10^k 网格），0.1/0.2/0.25 等细刻度可用、不再被粗化成 0.5 顶高轴顶；bracket 数据最大值收集优先 `get_bbox()`（Rectangle 单位矩形坑，勿用 `get_path().get_extents()` 对柱子取值）
- **输出**：PNG（300 dpi）+ PDF（矢量）双格式，`bbox_inches='tight'`

### 图型模板速查（9 类，完整模板在 references/recipes/）

**画图前先读对应模板文件**（含完整代码、参数细节、统计写法）；下表为速查：

| 表型 → 图型 | 主函数（关键参数） | 统计 | 模板 |
|---|---|---|---|
| Column → 带散点柱状图 | `prism_bars(ax, groups, labels)`（`error_type="sem"/"sd"`） | ≥3 组 `oneway_anova_tukey`；2 组 `ttest_two_groups` | `recipes/bar.md` |
| Column/Grouped → 箱线图+散点 | `prism_boxplot(ax, groups, labels)`；小提琴 `prism_violin(...)` | 同上 | `recipes/box.md` |
| Grouped → 分组柱状图 | `prism_grouped_bars(ax, df, x_col, group_col, value_col)` | `twoway_posthoc`（交互显著→简单效应；否则主效应） | `recipes/grouped.md` |
| Grouped（重复测量）→ 意大利面条图 | `prism_spaghetti(ax, df, x_col, group_col, value_col, subject_col)`（个体轨迹+均值±SEM；**默认 wide 画板**） | `build_stats_report("twoway_rm", df=..., rm_subject=..., rm_within=..., rm_between=..., value=...)`（混合设计 RM two-way，GG 球形性校正+Subjects(matching)+简单效应 Sidak） | `recipes/repeated_measures.md` |
| Survival → Kaplan-Meier | `prism_survival(ax, time, event, group)` | log-rank + Cox HR（可选） | `recipes/survival.md` |
| XY → 剂量-响应/标准曲线 | `prism_xy_fit(ax, x, y, model="4pl")`（`linear`/`4pl`） | 拟合 R²、IC50 | `recipes/xy_fit.md` |
| Contingency → 分组计数柱状图 | `prism_bars`（计数）+ χ² 检验 | Fisher/χ² | `recipes/contingency.md` |
| Nested → 嵌套柱状图 | `prism_nested_bars(ax, df, outer, inner, value)` | `nested_anova`（单元为分析单元防假重复） | `recipes/nested.md` |
| Parts of whole → 饼图/环形图 | `prism_pie` / `prism_donut` | — | `recipes/parts_of_whole.md` |
| Multiple variables → 散点矩阵/分面箱线 | `prism_pairplot(df)` / `prism_facet_boxplot(...)` | 按需 | `recipes/multiple_variables.md` |

**通用骨架**（所有图型一致，差异只在主函数与统计调用）：

```python
from prism_theme import (apply_prism_theme, recommend_figsize, prism_bars,
                         oneway_anova_tukey, add_pairwise_brackets,
                         build_stats_report, write_report, save_figure)
apply_prism_theme()
fig, ax = plt.subplots(figsize=recommend_figsize("column", n_groups=len(groups)))
prism_bars(ax, groups, labels)                # 主函数按图型替换
res = oneway_anova_tukey(groups, labels)      # 统计按图型替换
add_pairwise_brackets(ax, res["pairwise"], labels=labels)
save_figure(fig, name, out_dir)
write_report(name, build_stats_report("anova_tukey", description=...,
            groups=groups, labels=labels), out_dir)
```
`save_figure` 默认 `pad_inches=0.04`（在 tight bbox 外加安全边距，
防止 clip_on=False 的轴外显著性 bracket 在极端场景被裁）；`format_p(precision=...)`
对 precision<1 显式抛 ValueError（不再 f"{p:.{-1}e}" 崩溃）。

**跨图型硬规则**（模板里不再重复，此处统一）：
- 点大小**全图统一**：`dot_size=common_point_size(total_n, n_groups)**2`——柱/箱/小提琴函数默认已统一，手画散点才需显式传
- box/violin 必须显式 `palette=` 才上色（函数已内置，勿后置 `set_facecolor` 会全蓝）
- 显著性 bracket：`add_pairwise_brackets(ax, res["pairwise"], labels=labels)` 自动分层防重叠
- 统计选择：≥3 组 `oneway_anova_tukey`；2 组 `ttest_two_groups`（自动 shapiro→非参数/Welch）
- 退化数据防御：组内零方差（归一化全同值）→ 确定性 p 值不崩；n=1 组 / 配对长度不等 → 明确报错提示
## Phase 4：输出交付

1. 图表保存到 `/sandbox/workspace/output/`，命名 `{描述}_{表类型}_{图型}.png/.pdf`（用同一个 `name` 同时驱动 PNG/PDF 与统计报告，保证同名对应）
2. 用 provide_file 交付 PNG（预览用）和 PDF（投稿用）
3. 附赠图注（Figure Legend）文字块，**必须包含每组比较的具体 p 值**（星号之外给出精确数值，多数期刊要求）——用 `format_legend()` 生成：

```python
from prism_theme import format_legend
legend = format_legend(
    "TNF-α secretion in control and drug-treated groups",
    n=6, pairwise=pairs_list,   # n 为 int(各组相同) 或 list(各组不同,自动写 n=4–8 per group)
    p_precision=5,              # 可选：统一 n 位精度（见下方"p 值格式规则"）
)
# 产出示例（p_precision=5）：
# Figure. TNF-α secretion in control and drug-treated groups. Data are mean ± SEM,
# n=6 per group. One-way ANOVA with Tukey's post hoc test: Control vs Drug-Low
# p=0.13400 (ns); Control vs Drug-High p=1.0000e-5 (****); Drug-High vs Drug-Low
# p=2.0000e-4 (***). *p<0.05, **p<0.01, ***p<0.001, ****p<0.0001.
```

   p 值格式规则：**一律输出 scipy 计算出的实际精确值，绝不使用 `<` 阈值写法**（如 `p<1e-6`、`p<0.001` 均禁止）。默认（期刊通用）：p≥0.001 写 3 位小数 `p=0.134`；p<0.001 用科学计数法保留 3 位有效数字 `p=2.04e-4`、`p=3.71e-9`（指数去前导零）。星号（ns/*/**/***/****）照常给出，但凡出现具体 p 值处均为精确数值。用户可直接粘进论文。
   **`p_precision` 参数（可选）**：`build_stats_report(..., p_precision=n)` 与 `format_legend(..., p_precision=n)`、`add_pairwise_brackets(..., p_precision=n)` 均支持，统一把 p 值精度设为 n 位——p≥0.001 用 n 位小数（如 `p=0.20042`），p<0.001 用科学计数法保留 n 位有效数字（如 `p=6.6144e-4`）。**小 p 值仍走科学计数法、只增加有效数字位数**，既保留精确值、又避免 `p=0.00066` 这类丢精度的"假精确"。下溢兜底 `p<1e-300` 不受 precision 影响。
   **n 参数**：各组样本量相同时传 int（如 `n=6`）；各组不同时传 list（如 `n=[8,4,6]`），图注自动写成 `n=4–8 per group`——**严禁传 min(n) 假装各组同 n**（旧版 `_report_anova_tukey` 曾如此，n 不等时图注写 "n=4 per group" 与事实不符，属学术误导，已修复）。
4. **完整统计报告**：用 `build_stats_report(test, ...)` 生成 Markdown 报告（含描述统计、前提检验、检验统计量+自由度、事后比较、效应量、Figure Legend），再用 `write_report(name, report_md, out_dir)` 保存——**文件名与统计图完全一致**，仅后缀为 `_report.md`，如 `tnfa_dose_column_bar.png` ↔ `tnfa_dose_column_bar_report.md`。覆盖以下 test 类型：

   | test | 表类型 | 输入 |
   |---|---|---|
   | `anova_tukey` | Column（≥3 组） | `groups=[...], labels=[...]` |
   | `ttest` | Column（2 组） | `groups=[a, b], labels=[...]` |
   | `twoway` | Grouped | `df=dataframe, formula="value ~ C(A)*C(B)"`（含事后比较：交互显著→简单效应 simple effects，不显著→主效应 Tukey；`posthoc=False` 可关闭） |
   | `twoway_rm` | Grouped（重复测量） | `df=dataframe, rm_subject, rm_within, rm_between, value`（混合设计 between×within，subject 嵌套在 between 组内且测量 within 全部水平；含 Greenhouse-Geisser 球形性校正 ε+Mauchly、Subjects(matching) 匹配有效性行、简单效应/主效应事后 per-subject 配对 t + Sidak。对齐 Prism Repeated measures two-way） |
   | `survival` | Survival | `time, event, group`（log-rank 内置 Peto 法无需 lifelines；`add_cox=True` 附加 Cox HR + 95% CI + PH 检验，lifelines 按需自动安装） |
   | `nested` | Nested | `df, outer, inner, value`（以单元均值为分析单元，避免假重复） |
   | `contingency` | Contingency | `table=2D-array` |

5. **HTML 总览报告（自动附带，用户可双击即看）**：`write_report()` 现在默认 `html=True`，除 `.md` 外**自动额外生成一个与图同名的自包含 HTML 总览** `{name}.html`（如 `tnfa_dose_column_bar.html`）——内嵌 base64 PNG（300dpi 图直接预览，单文件自包含、无需同目录图片）、PDF 下载按钮（相对链接）、以及 Markdown 报告正文渲染为整洁 HTML（描述统计表/前提检验/事后比较/Figure Legend 均成表格）。**该文件是给用户查看的首选交付物**：交付时把它和 PNG 一起用 present_files 呈现，用户双击即可完整查看图 + 统计 + 图注。若只需纯 md，传 `html=False`。
   ```python
   write_report(name, rep, out_dir)          # 自动生成 {name}.html + {name}_report.md
   # 也可手动只调 HTML 生成器（若你想自定义 png/pdf 路径或页脚）：
   write_html_report(name, rep, out_dir,
                     png_path=..., pdf_path=..., extra_footer="Data: ...")
   ```
6. **多数据集合并面板图与总报告**：把多张独立数据集并成一张 Nature 风格多面板大图（自动 A/B/C 标注、独立原图 + 独立统计报告、合并总报告 HTML）。当用户说“把多张图画在一起”“像 Nature 那样 A/B/C”“汇总成一个报告文档”时使用。完整调用契约、示例代码、关键约定见 **`references/panel-figures.md`**（含多 Excel/CSV 循环、`read_excel_sheets()` 单文件多 sheet 一键成面板）。核心函数：`compose_panel_figure(panels, out_dir, name, ...)` + `build_master_report(...)`；`read_excel_sheets(path)` 一次读出所有 sheet 各成一个面板。
7. **y 轴收尾**：`add_significance_brackets()` 在需要顶高轴边界时会自动调用 `set_nice_ylim(ax, top)`，把轴上限收尾到一个"漂亮"刻度并补足顶部刻度标签——避免 bracket 把图顶高后出现无刻度标签的空白。
8. 如果用户后续要求修改（换图型、换误差线、换颜色、换 tall/square/wide 形态），回到对应 Phase 调整后重新出图

### 产物配对模板

**约定**:`{name}.py` / `{name}.png` / `{name}.pdf` / `{name}.html` / `{name}_report.md` **五件套全部同前缀** —— 让"图"与"出图的脚本"永远能互查（满足科研可复现要求）。

`emit_run_script(name, out_dir=...)` 在你的脚本末尾加一行,自动把"当前调用方脚本源码"按 `name.py` 落盘到 `out_dir`,与上面 `save_figure` / `write_report` 的图/报告**同前缀**:

```python
# ... 画图 ...
save_figure(fig, NAME, OUT)         # -> {NAME}.png / {NAME}.pdf
write_report(NAME, report, OUT)      # -> {NAME}.html / {NAME}_report.md
emit_run_script(NAME, out_dir=OUT)  # -> {NAME}.py（自动从调用栈抓 caller 源码）
```

调用栈原理:`inspect.currentframe()` 一路向上找,直到 `__file__` 不在 `scripts/prism_theme.py` 内,把那个 .py 读出来落盘——只读不改,幂等。

**8 种表型标准模板**在 `templates/` 目录,用户复制改 3 处即可:
- `column_template.py` —— Column 表(prism_bars, ≥3 组)
- `grouped_template.py` —— Grouped 表(时间×药物,twoway ANOVA)
- `xy_template.py` —— XY 拟合(prism_xy_fit, 4PL/linear)
- `survival_template.py` —— Survival 表(KM 曲线 + log-rank)
- `contingency_template.py` —— Contingency 计数(χ²/Fisher)
- `parts_of_whole_template.py` —— 占比饼图/环形图
- `multiple_variables_template.py` —— pairplot/facet boxplot
- `nested_template.py` —— 嵌套柱状图

**回退路径**:从 Jupyter / IPython REPL 调用 `emit_run_script()` 时无 `__file__`,自动改成要求 `source=` 显式传源码字符串 — 不会静默失败。

## Phase 5：自我优化复盘（每次任务后自动执行）

本技能具备**自我优化能力**：每次完成 Phase 4 交付后,无条件进入本阶段,复盘本轮使用过程、
把踩过的坑/被纠正点/能力缺口固化回技能自身,形成"越用越好"的闭环。完整规则见
`references/self-optimization.md`(智能体每次执行本阶段前应读它),要点如下：

**复盘信号源(逐项回顾本轮)**：① 脚本是否报错/Warning ② 用户是否纠正过 ③ 是否手写临时补丁绕过坑
④ 用户想要但脚本没有的能力 ⑤ 是否因文档不清而误解。

**分类与处置**(本模式 = 安全修复自动改)：
- `bug`/`convention`/`doc`：满足"安全修复闸门"(可复现、局部、可验证、非破坏性、可回退)则**自动改**并记日志；
- `gap`：清晰低风险的加法(新函数)自动加,否则记日志待确认；
- `ambiguous`：不确定是否为真问题/怎么修 → **只写日志、不动文件、向用户展示待确认**。

**闭环动作**：
1. 用 `scripts/log_learning.py` 把每条发现记入技能根目录 `learnings.jsonl`(append-only,含 type/status/files_changed/verified_by)；
2. 决定自动改的条目 → 改 `SKILL.md`/`scripts`/`references` → **立刻回归验证**(先 `python -c "import prism_theme"` 确保不崩,再跑一个 verify 脚本确认图形/统计正确)；
3. 回归通过记 `status=applied`；**回归失败立即还原改动并记 `status=reverted`**,绝不带病交付；
4. 改动后务必 Read 复查确实落盘(trust-but-verify)；用户级与项目副本保持同步。

**验证分级策略（用户约定，按改动类型选档，不必次次全套）**：

| 改动类型 | 验证级别 | 实测开销 |
|---|---|---|
| 小改动（文案/参数默认值/注释） | `python -c "import prism_theme"` 冒烟 + 相关单测 1–2 个 | ~1s |
| 中改动（加函数/改统计逻辑） | **pytest 全套**（最划算的统计正确性保险） | ~10s |
| 大改动（新 API/重构/绘图封装） | pytest + `scripts/verify/run_all.py` 全套 | 并行 ~107s / 串行 ~188s |

- 日常修改**默认只跑 pytest 全套**；仅动到绘图封装或公共 API 时才跑 verify 全套；
- verify 输出已精简：清理失败只打一行汇总（Windows 回收站不可用时不再 87 行逐文件噪声）；
- verify 全套默认**并行**执行 15 个脚本（worker=min(CPU核心,脚本数)），墙钟 ~101s；含墙钟耗时断言的 `verify11` 强制最后串行独占 CPU（见 `run_all.py` 顶部说明）；
- **按改动类型选档（不必次次全套）**：
  - `run_all.py --quick` 快速档：跳过 3 个深度脚本（verify9/10/11），浅层 10 个并行 **~54s** —— 只改文案/参数默认值/注释时用；
  - `run_all.py --only stats` 统计档（verify1/2/4/9/10/11，~80s）：改了统计逻辑（ttest/ANOVA/twoway/深度矩阵/边界）时用；
  - `run_all.py --only plot` 绘图档（verify3a/3b/3c/5/6/7/8/**verify12**）：改了绘图封装/布局/点径/ylim/合并面板图 时用；
  - `run_all.py --only edge` 边界档（verify11）：单独跑深度边界/性能；
  - 默认（无参数）= 全套 15 个，改动公共 API/大重构时用；
- pytest 实测 62 用例 ~12s / 输出 1 行；时间成本主要在 verify，token 成本可忽略。

**护栏**：公开 API 稳定优先——新能力用"加法"(新函数)而非改旧签名;日志只追加、可还原;
超过约 50 条时按 `self-optimization.md` 瘦身协议归档：旧条目移入 `references/learnings-archive-<日期>.jsonl`,
`learnings.jsonl` 保留最近 20 条,并同步更新历史案例区。

## 工作流示例

### 示例 1：三组药物剂量实验（Column 表）

用户说："我有个 Control、低剂量、高剂量三组的细胞活力数据，想画 Prism 那种带散点的柱状图，标显著性。"

1. **识别**：一个分组变量、三组独立样本 → Column 表
2. **选图**：默认带散点柱状图（Mean±SEM），确认箱线图/小提琴图备选
3. **统计**：3 组独立样本 → One-way ANOVA + Tukey 事后检验；生成 Control vs 低剂量、Control vs 高剂量、低 vs 高的星号
4. **美化**：L 形坐标轴 + 色盲友好配色 + 散点叠加 + 星号 bracket
5. **交付**：PNG + PDF + 图注 "Data are mean ± SEM, n=6 per group. One-way ANOVA with Tukey's post hoc test."

### 示例 2：时间×药物双因素实验（Grouped 表）

用户说："有 0h/24h/48h 三个时间点和 Control/Drug 两组，要做分组柱状图。"

1. **识别**：两个分组变量（时间、药物）→ Grouped 表
2. **选图**：分组柱状图（X 轴=时间，分组=药物），叠加散点
3. **统计**：Two-way ANOVA，报告时间主效应、药物主效应、交互项；图内标注药物组间显著性
4. **美化**：同示例 1，分组用色盲友好两色
5. **交付**：图注 "Data are mean ± SEM, n=4. Two-way ANOVA; *p<0.05, **p<0.01 vs Control at same time point."

### 示例 3：小鼠生存实验（Survival 表）

用户说："两组小鼠的生存天数，Conventional vs Experimental，画生存曲线。"

1. **识别**：时间 + 事件/删失 → Survival 表
2. **选图**：Kaplan-Meier 曲线，阶梯状，删失标记为短竖线
3. **统计**：log-rank 检验，P 值标在图上
4. **美化**：两组对比色、风险表（number at risk）可选
5. **交付**：图注 "Kaplan-Meier survival curves; log-rank test, p=0.03, n=10 per group."

## 资源目录

- `scripts/prism_theme.py` — 可执行的主题脚本：Prism 风格 matplotlib 主题、显著性标注函数、统计封装、**完整统计报告生成（`build_stats_report`）和与图同名的报告写入（`write_report`，自动附带同名自包含 HTML 总览 `write_html_report`，用户双击即看）、y 轴收尾（`set_nice_ylim`/`_nice_ylim_top`，max_ticks=9 防刻度拥挤）、分组柱状图整图封装（`prism_bars`，点大小全图统一）、画布推荐（`recommend_shape`/`recommend_figsize`，数据表类型→tall/square/wide 默认建议、用户关键词覆盖）、样本点自适应（`common_point_size` [2.0,5.0]pt / `auto_dot_alpha` 透明度 / `auto_dot_size`/`auto_point_size` 兼容保留）、**8 种表型整图封装**（`prism_bars`/`prism_boxplot`/`prism_violin`/`prism_survival`/`prism_xy_fit`/`prism_nested_bars`/`prism_pie`/`prism_donut`/`prism_pairplot`/`prism_facet_boxplot`，补齐 Nested/Parts of whole/Multiple variables 三个表型）、**非参数检验**（`mann_whitney_u`/`wilcoxon_signed_rank`，接口对齐 `ttest_two_groups`）、读表辅助（**v2.7.5 健壮化**：编码/分隔符自动回退、数值清洗、中文可行动报错、分组列合理性校验（杜绝静默错判）、`notes` 字段；自动拆组 + 返回数值列表头作为 ylabel 默认；`read_excel_sheets` 支持单 Excel 多 sheet 一键读取，`"sheet"` 字段可作面板标题）、**多数据集合并面板图 + 总报告**（`compose_panel_figure` 自动网格/A/B/C 标注/同时保留独立原图与独立统计报告，`build_master_report` 合并图置顶 + 各面板独立统计依次列出的总 HTML 报告）、**`__all__` 52 项公开 API 锁定**（agent/IDE 可静态校验）**。绘图时直接导入使用，无需加载全文。
- `references/table-mapping.md` — 8 种数据表 ↔ 数据结构特征 ↔ 图型列表 ↔ 统计方法的完整映射表（Phase 0/1 必读）。
- `references/statistics-guide.md` — 统计方法选择决策树、配对判定、显著性星号规范、误差线规范（Phase 2 必读）。
- `references/scatter-layout.md` — **散点布局实现级细节**（镜像均衡抖动公式、去规律化随机步长、`_apply_overlap_alpha` 判据与公式、`max_j ≤ width/2` 硬约束、画点前 xlim/ylim 硬约束、接口签名）；Phase 3"样本点布局"段引用本文件，避免主入口冗长
- `references/user-guide.md` — 面向终端用户的使用指南：数据上传格式（8 种表各自的 CSV 示例）、可选参数、FAQ。用户询问"怎么用/传什么数据"时，把此文档内容提供给用户（或告知完整文档路径）。
- `references/self-optimization.md` — **自我优化协议**：每次任务后如何复盘、问题分类与处置规则、安全修复闸门、闭环工作流、护栏、学习日志格式与历史案例。Phase 5 必读。
- `references/recipes/` — **10 类图型完整模板**（自 SKILL.md Phase 3 迁移，原文零丢失；另含 `repeated_measures.md`）：`bar/box/grouped/survival/xy_fit/contingency/nested/parts_of_whole/multiple_variables/repeated_measures.md`，每文件含完整代码、参数细节、统计写法。**画图前按速查表读取对应文件**；SKILL.md 正文只留速查表 + 跨图型硬规则，避免每次全量加载。
- `scripts/verify/` — **回归验证套件**（随技能包分发）：verify1~6 覆盖 Column 三大图型 / 其他表型 / 边界场景 / Two-way 事后比较 / Grouped 简单效应标注 / 画布推荐；**verify7** 覆盖 ylim<1 值域（细粒度步长 + bracket 数据最大值不被 Rectangle 单位矩形污染）；**verify8** 覆盖 ylim<1 修复全图型推广（下限分级 + boxplot 边框数据坐标 + violin/grouped <1 收尾 + 负值下限不被粗化）；**verify9/10** 覆盖析因矩阵深度回归与其他表型深度回归；**verify11** 覆盖深度边界/性能（NaN/inf 过滤、空组、n=1、pie/xy_fit 预检、palette 空列表、_conflict/overlap 向量化、3×1000 点 best-of-3 <8s）；**verify12** 覆盖多数据集合并面板图与总报告（compose_panel_figure / build_master_report，自动网格 1×3/2×2/自定义、A/B/C 标注、独立原图与报告、空 panels 报错）；`run_all.py` 一键回归（15 项，含 verify13 单 Excel 多 sheet 读取、默认并行、plot 档含 verify12、`--only` 按需子集、含耗时断言的 verify11 自动串行隔离，用法见 `scripts/verify/README.md`）。改动 `prism_theme.py` 后必跑。
- `tests/test_prism_stats.py` — **pytest 正式单测（与 `test_read_table.py` 合计 69 例）**：覆盖 ttest / 非参数（Mann-Whitney、Wilcoxon）/ ANOVA / Two-way / 重复测量 two-way / log-rank / contingency / nested bars / 意大利面条图冒烟 / `read_table` 长·宽·脏表头·xlsx / **坏输入健壮性 7 例（v2.7.5：文件缺失·GBK 编码·Tab 分隔·宽表混入文本列静默错判回归·空文件·列名写错·占位符与千分位）** / `format_legend` 自动推导方法文字 / `add_pairwise_brackets` `ytick_step`，每类含**阳性+阴性双对照 + scipy 交叉验证**；回归 bug 场景（p0 数据驱动 R²>0.9、x≤0 自动过滤、退化输入防御 6 例、Tukey-Kramer 逐对公式 + include_ns 生效、twoway 与 statsmodels 等价 + format_p precision 守卫、Welch/Dunnett T3/rm_twoway 固定参考值）。改动统计逻辑后跑：
  ```bash
  PY=$(python scripts/ensure_env.py)
  $PY -m pytest tests/ -v     # 期望 69 passed（须从技能根目录运行）
  ```
- `scripts/log_learning.py` — 学习日志辅助脚本：把每条复盘发现以结构化 JSON 行追加进技能根目录 `learnings.jsonl`，支持 `--list N` 查看最近条目、`--check` 全文件体检（报告坏行）。
- `scripts/ensure_env.py` — **环境引导器（每次任务第一步必跑）**：可移植、幂等地确保受管理 venv 中装有 matplotlib/scipy/numpy/pandas/seaborn，并打印 venv 解释器路径。**关键：依赖判定只用 venv 解释器，绝不依赖基础解释器**（基础解释器看不到 venv 包，误判未安装会导致每次任务重复装包）。venv 路径从 `sys.executable` 动态推导，跨机器/跨平台通用。用法：`PY=$(python scripts/ensure_env.py)` 后一律用 `$PY` 运行绘图脚本。
- 学习日志（`learnings.jsonl`）由 `scripts/log_learning.py` 按需生成并自动重建；历史归档与版本日志已外移存档，不随技能包分发。

## 变更日志

历次版本更新说明已外移存档，不随技能包分发。最后复核：v2.7.4。正文只描述**当前规则**，不保留历史版本号。

