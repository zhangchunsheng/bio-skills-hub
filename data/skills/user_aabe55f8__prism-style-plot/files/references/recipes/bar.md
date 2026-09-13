<!-- 由 SKILL.md Phase 3 迁移(v2.5.3 token 优化)。SKILL.md 正文只留速查，
     完整模板在此。按需读取：画该图型前读本文件。 -->
### 柱状图标准画法（Column 表的"带散点柱状图"图型）

用 `prism_bars()` 一次画完分组柱状图（Mean±SEM/SD + 个体散点），**点大小全图统一**（以全图最大 n 计算一次，同图所有样本点必须同大，期刊规范；绝不逐组各算各的）：

```python
from prism_theme import (apply_prism_theme, recommend_figsize, prism_bars,
                         oneway_anova_tukey, add_pairwise_brackets,
                         build_stats_report, write_report, save_figure)

apply_prism_theme()
fig, ax = plt.subplots(figsize=recommend_figsize("column", n_groups=len(groups)))
prism_bars(ax, groups, labels)                    # 分组柱状图 + 散点（自动统一大小）
res = oneway_anova_tukey(groups, labels)          # ≥3 组；2 组用 ttest_two_groups(a, b)
add_pairwise_brackets(ax, res["pairwise"], labels=labels)
save_figure(fig, name, out_dir)
write_report(name, build_stats_report("anova_tukey", description=...,
            groups=groups, labels=labels, error_type="mean ± SEM"), out_dir)
```

要点：
- `prism_bars(ax, groups, labels)` 可选 `error_type="sem"/"sd"`（默认 SEM）、`dot_size=数字`（显式指定则不再自适应，永远优先）、`palette=...`
- 散点默认**组色填充 + 黑描边**（描边透明度与填充一致）；如需手动画柱+散点（细粒度控制），用 `add_individual_dots(ax, i, g, dot_size=...)`——**多组时务必先算统一值** `dot_size=common_point_size(total_n, n_groups)**2` 再逐组传入，勿默认逐组自适应

