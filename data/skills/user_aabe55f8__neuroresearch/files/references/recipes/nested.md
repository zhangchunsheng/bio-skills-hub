<!-- 由本技能 SKILL.md Phase 3 迁移（token 优化）。SKILL.md 正文只留速查，
     完整模板在此。按需读取：画该图型前读本文件。 -->
### Nested 表型标准画法（v2.4.6 按 GraphPad Prism Nested 图模式重写）

层级嵌套数据（外层组→内层单元→观测；如"治疗组→动物→重复测量"），用
`prism_nested_bars()` + `nested_anova()` + `build_stats_report("nested")`
一次画完 **Prism 风格 Nested 图** + 嵌套 ANOVA + 统计报告 + 显著性标注。

**v2.4.6 严格对齐 GraphPad Prism 的 Nested 图模式**：

| 元素 | Prism Nested 图 | 本函数 |
|---|---|---|
| x 轴 | 外层组 | 外层组（不变）|
| 每组内容 | 每个内层单元（animal/dish）一**簇**散点 | 簇（jitter 展开的**原始测量值**）|
| 簇数 | = 单元数 | = 单元数 |
| 组水平 | 跨组粗横线（mean bar） | 黑粗横线 + ±单元 SEM 竖线 |
| 柱 | **无** | 无（Prism 默认无柱）|

```python
from prism_theme import (apply_prism_theme, recommend_figsize,
                         prism_nested_bars, nested_anova,
                         add_pairwise_brackets, build_stats_report,
                         write_report, save_figure)
import pandas as pd

apply_prism_theme()
fig, ax = plt.subplots(figsize=recommend_figsize("nested"))
res = prism_nested_bars(ax, df, "treatment", "animal", "value")
# res = {"outer":[...], "positions":ndarray,            # 组中心（bracket 标注）
#        "cluster_positions":{组: 簇中心数组},
#        "means":ndarray, "sems":ndarray, "n":ndarray,  # n=单元数
#        "unit_means":{组: 单元均值数组}, "unit_data":{组: {单元: 原始值}}}

na = nested_anova(df, "treatment", "animal", "value")
# F 分母 = 单元间变异（避免假重复）；Tukey 误差 = 单元间 MS

# 显著性 bracket（组间比较）
comps = []
for i in range(3):
    for j in range(i+1, 3):
        m = [p for a,b,p in na["pairwise"]
             if (a,b)==(res["outer"][i],res["outer"][j])]
        if m: comps.append((res["positions"][i]-0.2,
                            res["positions"][j]+0.2, m[0]))
add_pairwise_brackets(ax, comps)

save_figure(fig, "nested_demo", out_dir)
write_report("nested_demo",
    build_stats_report("nested", df=df, outer="treatment", inner="animal",
                       value="value", description="..."), out_dir)
```

要点：
- **v2.4.7 markers 参数**：不同内层单元用不同形状（marker）轮转区分
  （如 `markers=["o","s","^","D","v"]`）—— Prism 风格的"每 subcolumn 一种形状"
- **图 = Prism Nested 模式**：每组内每个单元的**原始测量**聚成一簇（簇内 jitter 展开），
  簇间 x 偏移分隔；组均值用**跨组粗黑横线**（Prism mean bar，线宽 0.75pt 对齐
  全局约定，v2.4.7）+ ±单元均值 SEM 竖线；**无柱**。
- **统计口径正确**：nested_anova 以单元均值为分析单元，F 分母用单元间变异
  （MS_unit），Tukey 事后误差同；附变异分解（outer/unit/within 占比）。
- **p 值标注：所有 p<0.1 全部标出**（v2.4.7 回归测试锁定）—— p<0.05 星号、
  [0.05,0.1) 精确 p 值、p≥0.1 不标。
- 返回结构对齐 grouped：`positions/means/sems/n` 数组 + `unit_means` 字典
  + `unit_data` 字典（每个单元的原始测量数组）；`add_pairwise_brackets` 可直接标注。

