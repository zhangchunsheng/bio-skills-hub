<!-- 由本技能 SKILL.md Phase 3 迁移（token 优化）。SKILL.md 正文只留速查，
     完整模板在此。按需读取：画该图型前读本文件。 -->
### 箱线图标准画法（Column / Grouped 表的"箱线图 + 散点"图型）

用 `prism_boxplot()` 画 Prism 风格箱线图（中位数/IQR 箱 + 个体散点），**已内置正确配色**——sns.boxplot 必须显式传 `palette=` 才会让每个箱体按颜色方案上色，只靠后置 `set_facecolor` 会让所有箱体变默认蓝，这是试运行发现的坑，本函数已规避。同思路的 `prism_violin()` 用于"小提琴图 + 散点"图型（Column 表常见备选），API 一致（`prism_violin(ax, groups, labels)`，密度带半透明填充 + 组色填充散点、黑描边透明度与填充一致），`inner=None` 去掉默认箱线、改叠个体点（默认显示中位数实线 + Q1/Q3 虚线），规避同款配色坑。多组两两比较用 `add_pairwise_brackets()` 自动分层防重叠。

```python
from prism_theme import (apply_prism_theme, recommend_figsize, prism_boxplot,
                         oneway_anova_tukey, add_pairwise_brackets,
                         build_stats_report, write_report, save_figure)

apply_prism_theme()
fig, ax = plt.subplots(figsize=recommend_figsize("column", n_groups=len(groups)))
# 直接画箱线图（groups=list[array]，labels=list[str]）；已内置正确配色，不会全蓝
prism_boxplot(ax, groups, labels)
# 统计：≥3 组用 oneway_anova_tukey；2 组用 ttest_two_groups(a, b)
res = oneway_anova_tukey(groups, labels)
# 显著性括号：自动按跨度分层堆叠，comparisons 直接传 (label_i, label_j, p)
add_pairwise_brackets(ax, res["pairwise"], labels=labels)
# 出图 + 同名报告（box 图 error_type 注明中位数/IQR，而非 mean±SEM）
save_figure(fig, name, out_dir)
write_report(name, build_stats_report("anova_tukey", description=...,
            groups=groups, labels=labels,
            error_type="median (IQR) shown as box; individual points overlaid"),
            out_dir)
```

要点：
- `prism_boxplot` 默认叠加**组色填充 + 黑描边**的个体散点（`show_points=True`，描边透明度与填充一致），箱体填充透明度 0.55——既显色又不抢数据；如需纯箱线图设 `show_points=False`。
- `add_pairwise_brackets` 的 `comparisons` 元素可以是 `(x1, x2, p)` 数值坐标，也可以是 `(label_i, label_j, p)` 标签——后者须同时传 `labels`，函数自动换算，与统计函数返回值无缝对接；2 组比较也适用（传单元素列表）。
- 误差线约定：柱状图用 Mean±SEM；**箱线图展示中位数/四分位距，图注须注明**（见上 `error_type` 写法），不要把 box 图误报成 Mean±SEM。

