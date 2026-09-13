<!-- 由 SKILL.md Phase 3 迁移(v2.5.3 token 优化)。SKILL.md 正文只留速查，
     完整模板在此。按需读取：画该图型前读本文件。 -->
### 分组柱状图标准画法（Grouped 表的"时间×药物"图型）

**v2.3.6 起**：有 `prism_grouped_bars()` 整图封装（点大小/legend/xlim/ylim 三个手写循环
的坑全部内置根治）。Grouped 表首选封装：

```python
from prism_theme import (apply_prism_theme, recommend_figsize, prism_grouped_bars,
                         add_pairwise_brackets, twoway_posthoc,
                         build_stats_report, write_report, save_figure,
                         emit_run_script)

apply_prism_theme()
fig, ax = plt.subplots(figsize=recommend_figsize("grouped", n_groups=len(times)*len(drugs)))
mapping = prism_grouped_bars(ax, df, "time", "drug", "value")
# mapping = {"x_levels":[...], "group_levels":[...],
#            "positions":{group:[x0,x1,...]}, "means":..., "sems":..., "n":...}

# 简单效应标注(交互显著时)
ph = twoway_posthoc(df, "value ~ C(time)*C(drug)")
if ph.get("type") == "simple_effects":
    for t_i, t in enumerate(mapping["x_levels"]):
        key = f"time={t}: Ctrl vs Drug"
        m = [p for d, p, _ in ph["comparisons"] if d == key]
        if m:
            add_pairwise_brackets(ax, [(mapping["positions"]["Ctrl"][t_i],
                                        mapping["positions"]["Drug"][t_i], m[0])])
```

封装内置三件防护（根治手写循环的三个坑）：

1. **点大小全图统一**——`common_point_size(total_n, n_x×n_g)` 算统一值后逐组显式传入；不再用 `add_individual_dots` 默认 `dot_size=None`（v2.3.6 修复前坑：点面积 2.8× 放大）
2. **legend 默认 ax 外右侧**——`bbox_to_anchor=(1.02, 0.5), loc="center left"`，X≤3 时不再压柱
3. **xlim/ylim 画点前预设**——`set_xlim(-0.5, n_x-0.5)` + `set_ylim(0, max*1.15)`；返回 `positions` 映射供标注，**不再手记 ctrl_x/drug_x**

要点：

- 数据长格式（`df` 含 x_col / group_col / value_col 三列；与 `twoway_posthoc` 公式 `value ~ C(A)*C(B)` 的 A/B 列对应）
- 水平顺序自动按数据中首次出现序提取（与 `twoway_posthoc` 比较键方向一致，调用方无需关心）
- 仅适合 2×N、3×N 等"短"Grouped 设计；意大利面条图（>4 时间点）建议改用 prism_xy_fit 折线
- **手写循环**仍可走（用 `add_individual_dots` + `common_point_size`），但务必**显式传 `dot_size=pt²`**，否则 v2.3.6 修复前坑会重现
- **参考演示**：`scripts/verify/verify4_grouped_bar.py` + `verify5_grouped_annotated.py`（v2.3.6 起均改用封装）

