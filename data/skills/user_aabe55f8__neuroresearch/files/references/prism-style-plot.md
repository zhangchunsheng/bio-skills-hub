# Prism 风格绘图（集成 prism-style-plot 引擎 v2.7.4，推荐路径）

> **neuroresearch 内建 prism-style-plot 完整绘图引擎**（v2.4.0 起从独立技能同步升级，最新同步至 v2.7.4）：核心库为 `scripts/prism_theme.py`（公开 API 52 项），环境引导为 `scripts/ensure_env.py`（标记缓存 + Windows `--copies` 兜底）。本文件是该能力的**唯一入口**；纯 matplotlib 兜底实现见 `plotting-protocol.md`（仅在 bundled 库无法运行时使用）。
>
> 图型模板（完整代码）见 `references/recipes/`（10 类）；散点布局实现级细节见 `references/scatter-layout.md`；回归套件见 `tests/`（pytest 62 例）+ `scripts/verify/`（`run_all.py` 13 项）。

### 本次同步带来的新能力（v2.6.x）
- **`read_table(path)`（v2.6.0）**：从 CSV/Excel 读取数据并自动拆组；当数据来自**文件**且用户未显式指定 y 轴标签时，**自动用数值列的表头作为 ylabel 默认**（经基础清洗）。长格式（1 非数值分组列 + ≥1 数值列）→ ylabel=数值列表头；宽格式（每列一组）→ ylabel 回退 None 由图型模板默认接管。绘图前 `ax.set_ylabel(res["ylabel"])` 即可，无需用户再给。
- **`format_legend(..., test=...)`（v2.6.x）**：`stat_method` 不传时，由 `test` 名自动推导方法文字（"ttest"→Unpaired t-test、"survival"→log-rank test 等），**避免 2 组 t 检验图误写出 ANOVA 描述**。都不传则回退 One-way ANOVA + Tukey（最常见图型）。
- **`add_pairwise_brackets(..., ytick_step=...)`（v2.6.x）**：小图（如 3×4cm）想让 y 轴刻度更粗（每 0.5 一格）时显式传 `ytick_step=0.5`，自动把轴顶向上取整到该步长整数倍，保证最顶刻度带标签、等分且不悬空。

设计哲学（与 prism-style-plot 一致）：**数据表驱动 → 统计与绘图联动 → 叠加原始数据点 → 期刊规范优先**。

> **核心规则（权威源）**：本文件是以下绘图铁律的**唯一权威定义源**——p 值格式铁律（精确值 / `<1e-300` 下溢表示）、默认线宽 `0.75 pt`、紧凑 Y 轴顶部留白 `≤0.26×span`、镜像均衡抖动。其他文件（`statistical-analysis.md` / `plotting-protocol.md` / `scatter-layout.md`）仅作引用；规则变更**只在本文件修改**，再由其余文件指针同步，避免多文件各写各的导致漂移（自检见 `selfcheck.py` 权威源校验）。

---

## 一、快速上手（每次绘图脚本前必做）

```bash
# 1) 获取受管理 venv 解释器（装过依赖就秒退，不重装）
PY=$(python scripts/ensure_env.py)
# 2) 用该解释器运行绘图脚本（之后一律用 $PY，禁止回退基础解释器）
$PY your_plot.py
```

```python
# your_plot.py —— 开头统一自检 + Agg 后端
import importlib.util, subprocess, sys
for m in ["numpy","pandas","scipy","statsmodels","matplotlib","seaborn"]:
    if importlib.util.find_spec(m) is None:
        subprocess.check_call([sys.executable, "-m", "pip", "install", m])

import matplotlib
matplotlib.use("Agg")                  # 无显示环境必须
import matplotlib.pyplot as plt
import sys, os
sys.path.insert(0, os.path.dirname(__file__))   # 让 import prism_theme 命中 bundled 库
from prism_theme import (
    apply_prism_theme, recommend_figsize, prism_boxplot, prism_bars, prism_violin,
    add_pairwise_brackets, oneway_anova_tukey, build_stats_report,
    write_report, save_figure, set_nice_ylim, format_legend,
)

apply_prism_theme()                    # L 形轴、无衬线字体、色盲友好配色
fig, ax = plt.subplots(figsize=recommend_figsize("column", n_groups=3))  # 表类型→形态

groups = [ctrl, low, high]             # 每组原始观测值 list/array
labels = ["Control", "Drug-Low", "Drug-High"]
prism_boxplot(ax, groups, labels)      # 箱线图 + 个体散点（内置正确配色/点大小/透明度）

res = oneway_anova_tukey(groups, labels)   # 返回 dict：{"method","anova_p","pairwise",...}
add_pairwise_brackets(ax, res["pairwise"], labels=labels)   # comparisons 用标签必传 labels=
set_nice_ylim(ax)                      # 紧凑 Y 轴收尾（防顶端留白）

save_figure(fig, "targetx_wb_box", out_dir="output")   # 300dpi PNG + 矢量 PDF
write_report("targetx_wb_box",
             build_stats_report("anova_tukey", groups=groups, labels=labels,
                                description="关键分子X 表达（WB, n=6/组）"),
             out_dir="output")         # 自动生成 _report.md + 同名自包含 HTML 总览
```

> ⚠️ **致命坑（务必转达使用者）**：切勿用**基础解释器**去 `import matplotlib` 判"装没装"——它看不到 venv 里的包会误报，导致每次重装。依赖是否齐全一律以 `ensure_env.py` 输出的 venv 解释器为准。

---

## 二、Phase 工作流（四步走，错一步后面全错）

### Phase 0：识别数据表类型（详见 `table-mapping.md`）
先问 4 个问题归类到 8 种 Prism 表之一（XY / Column / Grouped / Contingency / Survival / Parts-of-whole / Multiple-variables / Nested）。**识别结果先给用户确认再继续**——表类型认错则后续全错。

> **v2.6.0 默认约定（文件来源自动设 y 轴标签）**：若数据来自 CSV/Excel 且用户未显式指定 y 轴标签，`read_table(path)` 返回 dict 中的 `ylabel`（长格式=数值列表头，经基础清洗）可直接 `ax.set_ylabel(res["ylabel"])`；宽格式无单一数值列名时 `ylabel=None`，沿用图型模板默认（如 Column→`"Response (a.u.)"`）或请用户指定。列名常非投稿级（缩写/缺单位），最终投稿标签建议润色（如补 `(fold change)`）。

### Phase 1：选图型（详见 `table-mapping.md` + `references/recipes/` 模板）
| 表类型 | 默认图型 | 引擎函数 | 模板 |
|---|---|---|---|
| Column | 带散点柱状图（Mean±SEM） | `prism_bars` / `prism_boxplot` / `prism_violin` | `recipes/bar.md` / `box.md` |
| Grouped | 分组柱状图+散点 | `prism_grouped_bars` | `recipes/grouped.md` |
| Grouped（重复测量） | 意大利面条图 | `prism_spaghetti`（**默认 wide 画板**） | `recipes/repeated_measures.md` |
| XY | 散点+拟合 | `prism_xy_fit`（4pl/linear） | `recipes/xy_fit.md` |
| Survival | Kaplan-Meier 曲线 | `prism_survival`（log-rank + 可选 Cox HR） | `recipes/survival.md` |
| Contingency | 分组计数柱状图 | `prism_bars`（计数）+ χ²/Fisher | `recipes/contingency.md` |
| Nested | 嵌套柱状图 | `prism_nested_bars`（单元为分析单元） | `recipes/nested.md` |
| Parts of whole | 饼图/环形图 | `prism_pie` / `prism_donut` | `recipes/parts_of_whole.md` |
| Multiple variables | pairplot / 分面箱线 | `prism_pairplot` / `prism_facet_boxplot` | `recipes/multiple_variables.md` |

**画图前先读对应模板文件**（含完整代码、参数细节、统计写法）；SKILL 速查表仅作索引。

### Phase 2：统计-绘图联动（详见 `statistical-analysis.md §一~§四-B`）
方法由数据结构决定，不是由用户偏好决定：
- 2 组 → `ttest_two_groups`（自动 shapiro→非参数/Welch）；非参数用 `mann_whitney_u` / `wilcoxon_signed_rank`
- ≥3 组单因素 → `oneway_anova_tukey`：`var_equal="assumed"`（默认，标准 ANOVA+Tukey）/ `"welch"`（Welch ANOVA，事后 `posthoc`：`games_howell` / `dunnett_t3` / `welch_t`）/ `"auto"`（Levene 检验自动切换）。⚠️ n 小时 Levene 检验力低，先验方差不齐应显式 `var_equal="welch"`
- 两因素 → `build_stats_report("twoway", ...)`（交互显著→简单效应，否则主效应）
- 重复测量两因素 → `build_stats_report("twoway_rm", ...)`（GG 球形性校正 + 简单效应 Sidak）
- 生存 → `prism_survival` log-rank；`add_cox=True` 附加 Cox HR + PH 检验（需 lifelines）
- 列联 → χ² / Fisher；嵌套 → `nested_anova`（单元均值防假重复）
- **硬性规则**：≥3 组严禁两两 t 检验；必须 ANOVA+事后检验一次完成。

### Phase 3：Prism 风格美化（`prism_theme.py` 已内置全部规范）
- **形态预设（cm）**：`get_figsize("tall")`→3×5 / `square`→5×5 / `wide`→7×5；**推荐用 `recommend_figsize(table_type, n_groups)`**——Column/Grouped 按分组数分档（<5→tall、5–8→square、>8→wide），XY/Survival→square、Contingency→wide，**重复测量/时间轨迹类→一律 wide**；用户关键词（"高瘦/方/宽"）最高优先
- **点大小全图统一**：`common_point_size(总数, 组数)` 自适应（窗口 2.0–5.0 pt，样本量主导）；透明度 `auto_dot_alpha` 按 n 自适应
- **镜像均衡抖动**：默认 `layout="jitter"` + `balanced=True`（左右 n//2 点镜像、n 奇数随机偏侧）；点密集切 `layout="beeswarm"`。实现细节见 `scatter-layout.md`
- **误差线最顶层**：误差棒/中位线/箱体边框 zorder 高于散点，不被样本点覆盖
- **配色**：Okabe-Ito 默认（`get_palette`/`palette_sequence`）；印刷可切 Paul Tol Bright/Muted、IBM Design
- **显著性标注**：显著→星号、边缘显著 [0.05,0.1)→精确 p 值、p≥0.1 不标；bracket 自动分层；`ylim<1` 值域细粒度刻度（v2.5.1）
- **p 值铁律**：精确值，禁 `<` 阈值写法；下溢 `p=<1e-300`；`format_p(p, precision=n)` 可控精度

### Phase 4：交付物
1. **五件套同前缀**（可复现）：`{name}.py`（`emit_run_script` 自动落盘调用方源码）+ `.png` + `.pdf` + `.html`（自包含总览）+ `_report.md`
2. **图注**：`format_legend(description, n, pairwise, p_precision=...)` 生成——含每组精确 p 值（`n` 可传 list 自动写 `n=4–8 per group`，严禁用 min(n) 冒充）
3. **统计报告**：`build_stats_report(test, ...)` 覆盖 `anova_tukey/ttest/twoway/twoway_rm/survival/nested/contingency`；`write_report` 自动附带同名 HTML（内嵌 base64 图，用户双击即看）
4. **y 轴收尾**：`set_nice_ylim`/`_nice_ylim_top`（max_ticks=9）自动补顶部刻度；`save_figure` 默认 `pad_inches=0.04` 防轴外 bracket 被裁

---

## 三、`prism_theme.py` API 速查（直接调用，不必重写；完整 52 项见脚本 `__all__`）

> **【TOKEN 红线 · 查 API 唯一规则】** 凡需确认 `prism_theme.py` 的公开 API，永远只读本速查表（或 `grep "^def "` 看函数签名 + `__all__`），**严禁 `file_read` / 整文件读取 `scripts/prism_theme.py`**——该文件 270KB / 5350 行 ≈ 9 万 token，单次读取即灌爆上下文、浪费巨额 token。本文件是 API 的权威索引；引擎内部实现细节不进 LLM 上下文。

| 函数 | 作用 |
|---|---|
| `apply_prism_theme(font_family=None, font_scale=1.0)` | 全局主题：L 形轴、无衬线字体、色盲友好配色、去网格 |
| `get_figsize(shape="tall")` | 形态预设（cm→inch）：`tall`(3×5) / `square`(5×5) / `wide`(7×5) |
| `recommend_shape(table_type, n_groups=None, shape=None)` / `recommend_figsize(...)` | **表类型→形态三级推荐**（用户关键词>表类型建议>兜底 tall）；重复测量→wide |
| `read_table(path, group_col=None, value_col=None, sheet=0, header=0)` | 从 CSV/Excel 读数据并自动拆组，**自动返回建议 y 轴标签 ylabel**（v2.6.0：文件来源且用户未指定时，用数值列表头作默认）|
| `common_point_size(total_n, n_groups)` / `auto_dot_alpha(...)` | 点大小自适应（2.0–5.0 pt）+ 透明度（同图统一） |
| `prism_bars(ax, data, labels, error_type="sem", ...)` | 带散点柱状图（Mean±SEM）+ 个体点 + 误差线最顶层 |
| `prism_boxplot(ax, data, labels, ...)` | 箱线图（中位数/IQR）+ 个体散点 |
| `prism_violin(ax, data, labels, ...)` | 小提琴图 + 散点 |
| `prism_grouped_bars(ax, df, x_col, group_col, value_col, ...)` | Grouped 分组柱状图（twoway） |
| `prism_spaghetti(ax, df, x_col, group_col, value_col, subject_col, ...)` | 重复测量意大利面条图（个体轨迹+均值±SEM，**默认 wide**） |
| `prism_survival(ax, time, event, group, add_cox=False, ...)` | KM 生存曲线（内置 log-rank；`add_cox=True` 附 Cox HR，需 lifelines） |
| `prism_xy_fit(ax, x, y, model="4pl", ...)` | XY 散点+拟合（仅 `"4pl"` / `"linear"`） |
| `prism_nested_bars(ax, df, outer, inner, value, ...)` | Nested 嵌套柱状图（单元级防假重复） |
| `prism_pie(ax, sizes, labels, ...)` / `prism_donut(...)` | Parts of whole 饼图/环形图 |
| `prism_pairplot(df, cols=None, hue=None, ...)` / `prism_facet_boxplot(...)` | Multiple variables 散点矩阵 / 分面箱线 |
| `add_significance_brackets(ax, x1, x2, p_value, ...)` | 两组间显著性连接线 + 星号 |
| `add_pairwise_brackets(ax, comparisons, labels=None, ytick_step=None, ...)` | 多组两两比较 bracket，自动分层；**comparisons 用标签时必传 `labels=`**；`ytick_step`（v2.6.x）可显式设 y 轴刻度步长（小图每 0.5 一格更清晰）|
| `ttest_two_groups(a, b, paired=False)` | 两组 t 检验（自动 shapiro→非参数/Welch），返回 `(stat, p, 方法名)` |
| `mann_whitney_u(a, b)` / `wilcoxon_signed_rank(a, b)` | 非参数两组（独立/配对），返回 `(stat, p, 方法名)` |
| `oneway_anova_tukey(groups, labels, var_equal="assumed", posthoc="auto")` | 单因素 ANOVA（`var_equal`：assumed/welch/auto；Welch 分支事后 games_howell/dunnett_t3/welch_t），返回 dict（含 pairwise） |
| `build_stats_report(test="anova_tukey", ...)` | 完整统计报告（anova_tukey/ttest/twoway/twoway_rm/survival/nested/contingency），支持 `var_equal`/`p_precision`/`add_cox` |
| `format_legend(description, n, pairwise, p_precision=..., test=None)` | 生成 Figure Legend（精确 p 值 + n 可 list）；`test=`（v2.6.x）自动推导统计方法文字（如 "ttest"→Unpaired t-test），避免 2 组图误写 ANOVA |
| `write_report(name, report_md, out_dir, html=True)` | 落 `_report.md` + 同名自包含 HTML 总览 |
| `emit_run_script(name, out_dir=...)` | 把调用方脚本源码按 `{name}.py` 落盘（五件套闭环） |
| `save_figure(fig, name, out_dir=None, dpi=300, formats=("png","pdf"), pad_inches=0.04)` | 双格式输出，tight bbox + 安全边距 |
| `set_nice_ylim(ax, top=None)` | 紧凑 Y 轴收尾，顶部留白 ≤0.26×数据跨度（max_ticks=9）。⚠️ 预置 ylim 过高会早退→顶端无刻度，见 `plotting-protocol.md`「y 轴收尾已知坑」 |
| `p_to_stars(p, include_ns=True)` / `format_p(p, precision=None)` | p→星号；精确 p 值格式化（下溢→`p=<1e-300`） |

完整函数列表与参数见 `scripts/prism_theme.py`（可直接 `grep "^def "` / 查看 `__all__`）。

---

## 四、与其它模块的衔接

- **统计实现**：`statistical-analysis.md §四-B` 与引擎函数互补；**库函数优先**（已封装 Tukey/Welch/Dunnett T3/twoway_rm/log-rank/Cox/nested）。
- **图型模板**：`references/recipes/`（10 类，画图前按速查表读取）。
- **散点布局细节**：`references/scatter-layout.md`（抖动公式、透明度补偿、接口签名）。
- **运行前提**：任何绘图脚本前先按 `python-runtime.md` 自检（或本文件 §一的 `ensure_env.py` 流程）。
- **回归验证**：改引擎后跑 `PY -m pytest tests/`（62 例）+ `PY scripts/verify/run_all.py --quick`（快速档）。
- **中文期刊**：图注/报告表述按 `citation-formatting.md` 调整，统计呈现规则不变。
- **纯 matplotlib 兜底**：若 bundled 库不可用（极端环境），`plotting-protocol.md` 提供等效 inline 实现；默认优先本引擎。

---

## 五、机制通路图 / Graphical Abstract 生成协议（matplotlib 可复现）

> 统计图用 Prism 引擎（§二~§四）；**机制示意图/通路图是另一类产物**，需可复现脚本而非手绘。规范与工具选择见 `plotting-protocol.md Phase 6`；本节省提供 matplotlib 骨架，复用已装 `prism_theme` 主题（L 形轴、配色、字体一致）。

### 5.1 框-箭头骨架（因果链）
```python
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from prism_theme import apply_prism_theme, save_figure
apply_prism_theme()

fig, ax = plt.subplots(figsize=(6.2, 3.6))  # 机制图为自由画布，figsize 单位 inch，不受形态预设限制
ax.axis("off")

def box(x, y, text, color):
    ax.add_patch(plt.Rectangle((x, y), 2.4, 0.9, fc=color, ec="black", lw=0.75))
    ax.text(x + 1.2, y + 0.45, text, ha="center", va="center", fontsize=10)

# 因果链（CNS 损伤课题示例）
box(0.5, 3.0, "细胞A 激活", "#E69F00")
box(0.5, 1.8, "分子X 下调\n(细胞B)", "#56B4E9")
box(0.5, 0.6, "细胞B 死亡表型\n关键执行分子", "#009E73")
for (x, y1, y2) in [(1.7, 3.45, 2.25), (1.7, 2.25, 1.05)]:
    ax.annotate("", xy=(x, y2), xytext=(x, y1),
                arrowprops=dict(arrowstyle="->", lw=1.2, color="black"))
ax.text(3.2, 1.8, "损伤继发性病理↑", fontsize=10, color="#D55E00")
ax.annotate("", xy=(4.8, 1.8), xytext=(3.6, 1.8),
            arrowprops=dict(arrowstyle="->", lw=1.2, color="#D55E00"))
save_figure(fig, "mechanism_generic", out_dir="output")
```
- 激活/抑制用箭头样式区分（`arrowstyle="->"` 激活；抑制可改虚线/加终止杠）。
- 配色复用 `prism_theme` 的 Okabe-Ito，保证与统计图一致。
- 复杂图（多细胞类型、旁分泌）优先 BioRender（见 `plotting-protocol.md Phase 6`）；matplotlib 骨架适合快速可复现草稿与简单链路。
