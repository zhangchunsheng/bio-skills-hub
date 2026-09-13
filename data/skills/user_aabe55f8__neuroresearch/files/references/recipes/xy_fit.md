<!-- 由本技能 SKILL.md Phase 3 迁移（token 优化）。SKILL.md 正文只留速查，
     完整模板在此。按需读取：画该图型前读本文件。 -->
### XY 拟合曲线标准画法（XY 表的剂量-响应/标准曲线图型）

用 `prism_xy_fit()` 一次画完散点 + 拟合曲线（4PL 剂量-响应或线性回归 + 拟合优度 R² + IC50 标注）：

```python
from prism_theme import (apply_prism_theme, recommend_figsize, prism_xy_fit,
                         save_figure)

apply_prism_theme()
fig, ax = plt.subplots(figsize=recommend_figsize("xy"))   # XY → square
res = prism_xy_fit(ax, x, y, model="4pl",
                   xlabel="Agonist concentration (μM)",
                   ylabel="Response (% max)")
# res = {"model": "4pl", "popt": 拟合参数, "ic50": IC50, "r2": 决定系数,
#        "dropped": 因 x<=0 被过滤的点数}
save_figure(fig, name, out_dir)
```

要点：
- `model="4pl"`（默认）四参数 logistic（y = bottom + (top−bottom)/(1+10^((logEC50−log10(x))·hill))），x 轴自动设 log 刻度，`show_ic50=True` 标注 IC50 虚线+文本；`model="linear"` 用一阶线性回归
- **x≤0 自动过滤（v2.1.1）**：剂量-响应数据常含 0 剂量组，`log10(0)` 会崩溃——4PL 拟合前自动排除 x≤0 的点并打印警告（GraphPad Prism 同此处理，只在正浓度上拟合），返回 dict 里 `dropped` 字段记录过滤点数；过滤后不足 4 个正 x 点会抛明确错误
- **默认 p0 数据驱动（v2.3.1 修复）**：旧版硬编码 `p0=[0, 100, 0, 1.0]` 当 logEC50 远离 0（真实剂量-响应常见情况）时陷局部极小、R²≈0。改为 `p0 = [5% 分位, 95% 分位, log10(median(x)), 1.0]`,鲁棒通过绝大多数 S 形曲线。**高级用法**：先验已知 logEC50 时用 `fit_kws={"p0": [bottom, top, log10(EC50_guess), hill]}` 显式锁定起点。返回 dict 新增 `"p0"` 字段记录实际使用的初值,方便诊断。
- **图例默认 `upper left`**——S 形曲线左上角为平台空白区，不会压到曲线（修复项，见 CHANGELOG）；曲线形态不同时改 `legend_loc`（如 `"lower right"`）
- 散点用色板第 2 色、拟合线用第 1 色；`fit_kws` 透传给 `curve_fit`/`np.polyfit`

