# 数据表映射表：8 种 Prism 表格式

GraphPad Prism 的每种数据表格式决定了"能画什么图、能做什么分析"。本文件是 Phase 0（识别）和 Phase 1（选图）的完整依据。

## 判别流程

拿到数据后，按以下顺序问 4 个问题，逐一排除：

1. **每行是不是一个独立的观测个体，列是不是变量？** → 是 → Multiple variables 表
2. **数据是计数（人数/例数/次数）还是测量值？** → 计数且行列交叉成组 → Contingency 表
3. **有没有"时间 + 事件/删失"结构？** → 有 → Survival 表
4. **剩下按分组变量数量分：**
   - 无分组变量，只有各部分占整体比例 → Parts of whole 表
   - 1 个分组变量 → Column 表
   - 2 个分组变量 → 检查是否嵌套 → Nested 表；否则 Grouped 表
   - 每个点有 X、Y 两个数值坐标 → XY 表

**常见陷阱：**
- 分组变量是"类别"（Control/Treated/时间点），不是数值——先确认数据结构再分类
- 重复测量（同一批样本测多次）≠ 嵌套——重复测量是 Grouped/XY 表的特性，嵌套是层级结构
- 数据已经是"均值±SD"的汇总值：仍按分组结构分类，但图上无法叠加原始散点，需告知用户

## 8 种表格式详表

> **v2.3.0 状态**：8 种表已全部具备整图封装（Column/Grouped/XY/Survival/Contingency 沿用；**Nested/Parts of whole/Multiple variables 本轮新加 5 个**：`prism_nested_bars`/`prism_pie`/`prism_donut`/`prism_pairplot`/`prism_facet_boxplot`）。统计决策树保持完整。

### 1. XY 表（XY table）

| 项 | 说明 |
|---|---|
| 数据结构 | 每行一个点：X 数值列 + 一个或多个 Y 数值列（重复测量时 Y 为并列子列） |
| 典型场景 | 剂量-响应曲线、标准曲线、时间进程曲线、散点相关 |
| 支持的图型 | 散点图、散点+连线、折线图、非线性回归拟合曲线、相关图（r） |
| 统计方法 | 非线性回归（剂量-响应：log(agonist) vs response）、线性回归、Pearson/Spearman 相关 |
| 识别要点 | 有明确的连续 X 轴数值，不是类别标签 |
| seaborn/matplotlib | `sns.scatterplot` / `sns.lineplot` / `plt.plot` / `sns.regplot`；拟合用 `scipy.optimize.curve_fit` |

### 2. Column 表（Column table）

| 项 | 说明 |
|---|---|
| 数据结构 | 每列一个组（同一分组变量的一个水平），列内是原始重复测量值；可含并列子列（重复测量） |
| 典型场景 | Control vs 处理组；Control vs 低/高剂量多组比较 |
| 支持的图型 | 带散点柱状图、箱线图+散点、小提琴图+散点、柱状图（Mean±SD/SEM） |
| 统计方法 | 2 组：非配对/配对 t 检验、Mann-Whitney/Wilcoxon；≥3 组：One-way ANOVA + Tukey（或 Welch ANOVA + Games-Howell） |
| 识别要点 | 1 个分组变量；每组有多个重复测量值（或已汇总的均值±误差） |
| seaborn/matplotlib | `sns.barplot`（errorbar）/ `sns.boxplot` / `sns.violinplot` / `sns.stripplot` 叠加；统计用 `scipy.stats` |

### 3. Grouped 表（Grouped table）

| 项 | 说明 |
|---|---|
| 数据结构 | 两个分组变量：一个定义行（如时间点），一个定义列（如药物）；每个单元格是重复测量值（或均值） |
| 典型场景 | 时间×药物、性别×处理、剂量×时间 |
| 支持的图型 | 分组柱状图+散点、分组箱线图、意大利面条图（重复测量：每个受试者一条折线） |
| 统计方法 | Two-way ANOVA（报告主效应 ×2 + 交互效应）；重复测量设计用重复测量 Two-way ANOVA |
| 识别要点 | 两个分组变量交叉成网格；可含重复测量（同一受试者跨时间） |
| seaborn/matplotlib | `sns.barplot(x, hue)` / `sns.boxplot(x, hue)` / `sns.lineplot`（意大利面图）；统计用 `statsmodels.stats.anova` 或 `scipy.stats.f_oneway` 变体 |

### 4. Contingency 表（Contingency table）

| 项 | 说明 |
|---|---|
| 数据结构 | 行×列的计数表（每个单元格是人数/例数/次数，不是测量值） |
| 典型场景 | 处理组 vs 对照组的"存活/死亡"例数；某特征的"有/无"人数 |
| 支持的图型 | 分组柱状图（计数）、堆叠柱状图、百分比堆积图 |
| 统计方法 | 卡方检验；2×2 小样本用 Fisher 精确检验 |
| 识别要点 | 单元格是整数计数；行列交叉定义分组 |
| seaborn/matplotlib | `sns.barplot` / `plt.bar`；统计用 `scipy.stats.chi2_contingency` / `fisher_exact` |

### 5. Survival 表（Survival table）

| 项 | 说明 |
|---|---|
| 数据结构 | 每行一个受试者：X=生存时间，Y=事件发生（1）或删失（0），不同组用不同 Y 列（或分组列） |
| 典型场景 | 小鼠生存实验、患者生存随访 |
| 支持的图型 | Kaplan-Meier 生存曲线（阶梯状），删失用短竖线标记 |
| 统计方法 | log-rank 检验、Gehan-Wilcoxon；多变量用 Cox 回归（需 Multiple variables 表） |
| 识别要点 | 存在"时间 + 二值事件/删失"结构 |
| 实现 | 内置 Peto 法 log-rank 检验（无需 lifelines 依赖）；KM 曲线用 `plt.step`，删失标记 `plt.plot(..., marker='|')` |

### 6. Parts of whole 表（Parts of whole table）

| 项 | 说明 |
|---|---|
| 数据结构 | 一列数值（各部分大小），总和有意义（占整体的比例） |
| 典型场景 | 细胞群体占比、成绩分布、资金构成 |
| 支持的图型 | 饼图、环形图、堆叠柱状图 |
| 统计方法 | 通常不检验；如需要可做卡方拟合优度 |
| 识别要点 | 所有值加起来=整体 100% 或总量 |
| seaborn/matplotlib | `plt.pie` / 环形图 / `plt.bar`（stacked） |

### 7. Multiple variables 表（Multiple variables table）

| 项 | 说明 |
|---|---|
| 数据结构 | 每行一个观测（case），每列一个变量；变量类型：连续/分类/标签 |
| 典型场景 | 临床数据表、组学元数据、含协变量的分析 |
| 支持的图型 | 按意图选择：箱线图分面、散点矩阵、回归图、森林图、热图 |
| 统计方法 | 多元回归、Cox 回归、广义线性模型、主成分分析 |
| 识别要点 | 标准"行=样本、列=特征"宽表 |
| seaborn/matplotlib | `sns.pairplot` / `sns.FacetGrid` / `sns.heatmap`；统计用 `statsmodels` / `sklearn` |

### 8. Nested 表（Nested table）

| 项 | 说明 |
|---|---|
| 数据结构 | 两层嵌套复制：组（水平 1）内再分亚组（水平 2），亚组内是测量值 |
| 典型场景 | 两种教学方法 × 每法 3 个教室 × 每室若干学生 |
| 支持的图型 | 嵌套柱状图（每个亚组一根柱，同组颜色一致） |
| 统计方法 | 嵌套 t 检验 / 嵌套 ANOVA（用均值而非个体值做检验，避免伪重复） |
| 识别要点 | 亚组之间不相交（每个亚组只属于一个组）；"教室"嵌套于"教学方法" |
| 实现 | 先按亚组聚合 → 组间做 t 检验/ANOVA；伪重复是致命错误，务必聚合 |

## 图型选择速查（Phase 1 用）

| 用户意图关键词 | 建议图型 | 表类型 |
|---|---|---|
| "带散点的柱状图" | 散点柱状图（Mean±SEM） | Column / Grouped |
| "箱线图" | 箱线图+散点（柱外） | Column / Grouped |
| "小提琴图" | 小提琴图+散点 | Column |
| "分组柱状图" | 分组柱状图 | Grouped |
| "生存曲线" | Kaplan-Meier 曲线 | Survival |
| "剂量-响应/标准曲线" | XY 散点+拟合线 | XY |
| "占比/饼图" | 饼图/环形图 | Parts of whole |
| "计数对比" | 分组计数柱状图 | Contingency |
| "每个人一条线" | 意大利面条图 | Grouped（重复测量） |

## 数据表识别后的确认

识别出表类型后，向用户输出一行摘要并请求确认，例如：

> 识别为 **Grouped 表**（两个分组变量：时间 3 水平 × 药物 2 水平，每格 n=4）。将绘制分组柱状图并做 Two-way ANOVA。确认继续？如需调整（如改用箱线图），请说明。

这是本技能的确认门——表类型是后续一切的基础，识别错误会浪费用户一轮完整出图时间。
