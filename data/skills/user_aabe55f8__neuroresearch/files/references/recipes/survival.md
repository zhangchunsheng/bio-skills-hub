<!-- 由本技能 SKILL.md Phase 3 迁移（token 优化）。SKILL.md 正文只留速查，
     完整模板在此。按需读取：画该图型前读本文件。 -->
### 生存曲线标准画法（Survival 表的 Kaplan-Meier 图型）

用 `prism_survival()` 一次画完 KM 生存曲线（阶梯线 + 删失短竖线 + log-rank p 值标注，内置 Peto 法 log-rank，无需 lifelines）：

```python
from prism_theme import (apply_prism_theme, recommend_figsize, prism_survival,
                         build_stats_report, write_report, save_figure)

apply_prism_theme()
fig, ax = plt.subplots(figsize=recommend_figsize("survival"))   # Survival → square
res = prism_survival(ax, time, event, group, show_median=True,
                     xlabel="Days after treatment")
# res = {"p": logrank_p, "chi2": χ², "median": {组: 中位生存}, "n": {组: 例数}}
save_figure(fig, name, out_dir)
report = build_stats_report("survival", time=time, event=event, group=group,
                            description="...")
write_report(name, report, out_dir)
```

**Cox 回归（v2.4.3 新增，HR + 95% CI + PH 检验）**：log-rank 只给 p 值；要效应量（HR）与协变量校正能力时叠加 Cox。图上标注与报告输出默认关闭，显式开启即可：

```python
# 图上标注：Cox HR (95% CI) vs 参照组（参照组自动识别对照命名，
# 如 Vehicle/Control/Sham，否则取数据中首次出现的组；也可 cox_reference="Vehicle" 指定）
res = prism_survival(ax, time, event, group, show_median=True,
                     show_cox=True, cox_reference="Vehicle")
# res["cox"] = cox_regression() 的返回 dict

# 报告附加 Cox 块（默认 add_cox=True；lifelines 未装时报告给出安装提示、不报错）
report = build_stats_report("survival", time=time, event=event, group=group,
                            description="...", add_cox=True)
```

- 独立调用：`cox_regression(time, event, group, reference=None)` 返回
  `{"reference", "comparisons": [(组, HR, ci_low, ci_high, p), ...],
    "overall_p"（似然比整体检验）, "ph_p"/"ph_ok"（Schoenfeld 残差 PH 假设检验）,
    "n_events", "used_lifelines"}`
- **lifelines 懒加载**：log-rank 零依赖不变；仅 Cox 功能需要 `pip install lifelines`（未安装时图上标红提示、报告给安装提示，均不中断）
- HR < 1 表示相对参照组死亡风险更低（生存获益）；报告自动加注解释

要点：
- 数据格式：`time`（生存时间）、`event`（1=事件，0=删失）、`group`（分组标签），三者等长；每行一个受试者
- 2 组自动标注 `log-rank p=...`（Peto 法）；≥3 组标注整体 χ² + p（`_logrank_multi`，两两比较未校正、报告注明）
- `show_median=True` 时给每组画中位生存期虚线 + 数值（数值带白底半透明 bbox，中位线接近 x 轴中部时也不会与 log-rank p 文本重叠，v2.1.1）；删失标记默认开启（`censoring=True`）
- 图例默认 `upper right`；若曲线顶部拥挤可改 `legend_loc="lower right"`
- **曲线线宽默认 0.75pt**（v2.2.1：对齐全局 0.75pt 线条约定；可传 `lw=` 调整，如 `lw=1.2` 加粗）

