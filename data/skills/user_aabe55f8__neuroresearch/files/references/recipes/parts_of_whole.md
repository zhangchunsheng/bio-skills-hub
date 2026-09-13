<!-- 由本技能 SKILL.md Phase 3 迁移（token 优化）。SKILL.md 正文只留速查，
     完整模板在此。按需读取：画该图型前读本文件。 -->
### Parts of whole 表型标准画法（v2.3.0）

占比 / 组成分析（如细胞类型占比、市场份额），用 `prism_pie()` 或 `prism_donut()`：

```python
from prism_theme import apply_prism_theme, recommend_figsize, prism_pie, prism_donut

apply_prism_theme()
fig, ax = plt.subplots(figsize=recommend_figsize("parts_of_whole"))
prism_pie(ax, [10, 20, 30, 40], ["A", "B", "C", "D"])  # 饼图

fig, ax = plt.subplots(figsize=recommend_figsize("parts_of_whole"))
prism_donut(ax, [10, 20, 30, 40], ["A", "B", "C", "D"],
            center_text="n=100")                        # 环形图 + 中心文本
```

要点：色板用色盲安全 `okabe_ito`；`pct=True` 输出百分比；`center_text` 在环形中心放总数/标题。**通常不做统计检验**。

