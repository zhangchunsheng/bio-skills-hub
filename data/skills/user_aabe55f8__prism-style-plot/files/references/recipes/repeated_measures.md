<!-- 由 SKILL.md Phase 3 迁移(v2.5.12 token 优化)。SKILL.md 正文只留速查，
     完整模板在此。按需读取：画重复测量图前读本文件。 -->
### 重复测量完整流程（Grouped 表 + subject 重复测量，v2.5.11/2.5.12）

**图型**：意大利面条图（`prism_spaghetti`，个体轨迹 + 组均值±SEM）。
**画布**：**默认 wide**（SKILL.md 画布规则 v2.5.11 用户偏好）。
**统计**：`build_stats_report("twoway_rm", ...)`（混合设计 RM two-way，
GG 球形性校正 + Subjects(matching) + 简单效应 Sidak）。

```python
from prism_theme import (apply_prism_theme, get_figsize, prism_spaghetti,
                         build_stats_report, write_report, save_figure,
                         emit_run_script)

apply_prism_theme()
# 数据长格式: 每行 = subject 在 (between×within) 一次测量
#   df 列: group(between), time(within), subject(ID), value
# 同一 subject 必须测量 within 的全部水平(平衡设计, 缺失会报错)
fig, ax = plt.subplots(figsize=get_figsize("wide"))   # 轨迹图 → wide
res = prism_spaghetti(ax, df, x_col="time", group_col="group",
                      value_col="value", subject_col="subject")
# res = {"x_levels":[...], "group_levels":[...],
#        "means":{g:array}, "sems":{g:array}, "n":{g:array}, "colors":{g:hex}}
ax.set_xlabel("Time after ischemia"); ax.set_ylabel("mNSS score")
fig.tight_layout()
save_figure(fig, NAME, OUT)          # 图名与报告同名(HTML 内嵌图依赖)

rep = build_stats_report("twoway_rm", description="...",
                         df=df, rm_subject="subject", rm_within="time",
                         rm_between="group", value="value", p_precision=5)
write_report(NAME, rep, OUT)         # -> {NAME}.html + {NAME}_report.md
emit_run_script(NAME, OUT)
```

**统计结果解读**（报告结构）：
- ANOVA 表四行：between / within / **Interaction** / **Subjects(matching)**；
  within 与交互的 p (GG 校正) 是违反球形性时的正式结论（ε + Mauchly 见第 3 节）；
  Subjects(matching) 行 P 小 → 受试者间差异显著，重复测量匹配有效。
- 事后：交互显著 → 简单效应（各组内时间点两两，per-subject 配对 t + Sidak）；
  交互不显著 → 主效应两两。
- 图注已自动生成：`Two-way repeated measures ANOVA (mixed design, ...)
  with Greenhouse-Geisser correction; simple effects compared by paired
  t tests with Sidak correction`。
