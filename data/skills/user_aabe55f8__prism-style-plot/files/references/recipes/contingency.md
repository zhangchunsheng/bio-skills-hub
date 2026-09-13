<!-- 由 SKILL.md Phase 3 迁移(v2.5.3 token 优化)。SKILL.md 正文只留速查，
     完整模板在此。按需读取：画该图型前读本文件。 -->
### Contingency 计数柱状图标准画法（Contingency 表的"分组计数柱状图"图型）

计数柱状图（每根柱顶有数字标注）有 3 个**高频踩坑**：图内文字与柱/数字覆盖、y 轴未统一规范。**强制规范**（v2.0.26 自测）：

1. **y 轴统一收尾**：`finish_axes(ax, data_max=float(table.max()))`——0.5 倍数刻度 + 顶部 ≤1.3×data_max
2. **χ²/Fisher 文本放轴外右上**：长文本（`"χ²(2) = 31.41, p=1.51e-7"`）在窄图内必压柱/数字；轴外由 `bbox_inches='tight'` 扩顶部画布；p 值用 `format_p(p)`
3. **图例放轴外左上**（**不**用 `loc="upper right"`/`"upper left"`）：`bbox_to_anchor=(0.01, 1.02), loc="lower left", ncol=1`——与统计文本分占轴外左右两角

```python
fig, ax = plt.subplots(figsize=recommend_figsize("contingency"))   # Contingency → wide
colors = palette_sequence("okabe_ito")[:2]
x = np.arange(n_groups); width = min(0.38, 0.8 / table.shape[0])  # 行数自适应（v2.4.0：≥3 行时防柱子重叠）
for r_i, (row, c, lab) in enumerate(zip(table, colors, ["No response", "Response"])):
    ax.bar(x + (r_i - 0.5)*width, row, width=width, color=c, alpha=0.85,
           edgecolor="black", linewidth=0.75, label=lab, zorder=2)
    for xi, v in zip(x + (r_i - 0.5)*width, row):
        ax.text(xi, v + 1.0, str(int(v)), ha="center", va="bottom", fontsize=6)
ax.set_xticks(x); ax.set_xticklabels(labels)
ax.set_xlabel("Treatment group"); ax.set_ylabel("Number of mice")
finish_axes(ax, data_max=float(table.max()))                  # y 轴统一
ax.text(0.99, 1.02, f"\u03c7\u00b2({dof}) = {chi2:.2f}, {format_p(p)}",
        transform=ax.transAxes, ha="right", va="bottom", fontsize=6,
        bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="none", alpha=0.9))
ax.legend(frameon=False, fontsize=7, loc="lower left",
          bbox_to_anchor=(0.01, 1.02), ncol=1)                # legend 轴外左上
```

报告：`build_stats_report("contingency", table=table, description="...")` 自动含卡方/Fisher 检验、期望频数、效应量（2×2 odds ratio）、Figure Legend。

