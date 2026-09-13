"""Nested 表 标准产出模板 — GraphPad Prism Nested 图模式（v2.4.6）。

使用步骤:
  1. 复制重命名(例:treatment_animal.py)
  2. 改 NAME、df（outer/inner/value 三列 long-format）；
     **inner 列的每个水平只属于一个 outer**（如 animal id 只属于一个 treatment）
  3. 跑 `python treatment_animal.py`,OUT/ 出五件套同前缀产物

v2.4.6 Prism 风格 Nested 图：每组内每个内层单元的**原始测量**聚成一簇（jitter 展开），
组均值用跨组粗黑横线（Prism mean bar）+ ±单元均值 SEM 竖线；**无柱**。
配套 nested_anova() 以单元均值为分析单元 + build_stats_report("nested")
生成完整统计报告（描述统计 / Nested ANOVA / 变异分解 / Tukey / Figure Legend）。
"""
import sys, pathlib
HERE = pathlib.Path(__file__).resolve().parent
SKILL = pathlib.Path(r"C:\Users\DELL\.workbuddy\skills\prism-style-plot")
sys.path.insert(0, str(SKILL))

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scripts.prism_theme import (
    apply_prism_theme, recommend_figsize,
    prism_nested_bars, nested_anova, add_pairwise_brackets,
    build_stats_report, write_report, save_figure, emit_run_script,
)

# === 改 1:基础名 ===
NAME = "treatment_animal"

# === 改 2:long-format 三列 outer/inner/value（inner 每水平只属一个 outer） ===
rng = np.random.default_rng(20260820)
treatments = ["Sham", "Treat-A", "Treat-B"]
rows = []
for t_i, t in enumerate(treatments):
    for ani in range(4):                              # 4 只动物/组（独立单元）
        u = rng.normal(10 + t_i * 2.5, 1.2)           # 动物间变异
        for _ in range(3):                            # 每只 3 次重复测量
            rows.append({"treatment": t,
                         "animal": f"{t}-a{ani}",
                         "value": u + rng.normal(0, 0.6)})
df = pd.DataFrame(rows)

OUT = pathlib.Path("out"); OUT.mkdir(exist_ok=True)
apply_prism_theme()
fig, ax = plt.subplots(figsize=recommend_figsize("nested"))
# v2.4.7:markers 按内层单元轮转,不同单元簇可用形状区分
res = prism_nested_bars(ax, df, "treatment", "animal", "value",
                        markers=["o", "s", "^", "D", "v"])

# 统计：Nested ANOVA（以单元均值为分析单元，避免假重复）
na = nested_anova(df, "treatment", "animal", "value")
print(f"nested F={na['F']:.2f}, df=({na['df_between']},{na['df_within']}), p={na['anova_p']:.4f}")
print("变异分解:", {k: round(v, 1) for k, v in na["variance"].items()})

# 显著性 bracket（组间比较；bracket 宽度可选组中心 ±0.2 覆盖整组）
# 注意:把**全部 pairwise** 传进 add_pairwise_brackets,内部自动过滤
# p<0.1 标出(显著→星号 / 边缘显著 [0.05,0.1)→精确 p 值)
comps = []
for i in range(len(res["outer"])):
    for j in range(i + 1, len(res["outer"])):
        m = [p for a, b, p in na["pairwise"]
             if (a, b) == (res["outer"][i], res["outer"][j])]
        if m:
            comps.append((res["positions"][i] - 0.2, res["positions"][j] + 0.2, m[0]))
add_pairwise_brackets(ax, comps)

ax.set_xlabel("Treatment")
ax.set_ylabel("Value (raw measurements)")
ax.set_title(f"{NAME}: Treatment × Animal nested (Prism style)")

save_figure(fig, NAME, str(OUT))
write_report(NAME,
    build_stats_report("nested", df=df, outer="treatment", inner="animal",
                       value="value",
                       description="Nested design: 3 treatments x 4 animals x 3 reps."),
    str(OUT))
emit_run_script(NAME, out_dir=str(OUT))
print(f"\n[Done] 五件套产物（含本脚本）已写入 {OUT.resolve()}")
