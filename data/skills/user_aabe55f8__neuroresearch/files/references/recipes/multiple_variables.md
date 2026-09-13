<!-- 由本技能 SKILL.md Phase 3 迁移（token 优化）。SKILL.md 正文只留速查，
     完整模板在此。按需读取：画该图型前读本文件。 -->
### Multiple variables 表型标准画法（v2.3.0）

多变量探索（散点矩阵看两两关系 + 分面箱线图看"按子集切分的分布"）：

```python
from prism_theme import (prism_pairplot, prism_facet_boxplot)

# 散点矩阵——下三角散点 + 对角线 KDE
fig, axes = prism_pairplot(df, cols=["a", "b", "c"], hue="group")  # hue 着色列
# 也可 diag_kind="hist" 用直方图代替 KDE

# 分面箱线图——按 facet 列每个水平画一个子图
fig, axes = prism_facet_boxplot(df, x="gene", y="expr", facet="sample", ncols=3)
```

要点：`prism_pairplot` 对角线自动用色板第 2 色画 KDE 曲线；无 hue 时单一灰度；`prism_facet_boxplot` 复用 `prism_boxplot` 的色盲友好配色与散点叠加。
**v2.3.1 文档警示**：这两个函数内部 plt.subplots() 自建 figure 并直接 return (fig, axes)。
调用方**不要** plt.figure() / plt.clf() 预建 figure,否则 fig.savefig() 保存的是调用方空 figure、所有 panels 丢失。
正确写法：`fig, axes = prism_pairplot(df, ...); fig.suptitle(...); save_figure(fig, name, out_dir)`。回归示例见 `scripts/verify/verify10_deep_others.py` 的 `run_multivar()`。

