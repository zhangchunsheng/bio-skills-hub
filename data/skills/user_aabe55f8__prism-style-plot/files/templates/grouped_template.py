"""Grouped 表 标准产出模板 — 用 v2.3.6 prism_grouped_bars 整图封装。

封装自动完成:
  - 柱体(Mean±SEM)+ 误差棒(zorder 6)
  - 散点(common_point_size 统一点大小,根治"逐组自适应 2.8× 放大"坑)
  - legend 默认放 ax 外右侧(防 X≤3 时压柱)
  - xlim/ylim 画点前预设(防 jitter 漂移)
  - 返回 positions 映射供 add_pairwise_brackets 标注

使用步骤:
  1. 复制并重命名(例:time_drug.py)
  2. 改 NAME、times/drugs、df 三处数据装配
  3. 跑 `python time_drug.py`,OUT/ 出五件套同前缀产物
"""
import sys, pathlib
HERE = pathlib.Path(__file__).resolve().parent
SKILL = pathlib.Path(r"C:\Users\DELL\.workbuddy\skills\prism-style-plot")
sys.path.insert(0, str(SKILL))

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scripts.prism_theme import (
    apply_prism_theme, recommend_figsize, prism_grouped_bars,
    add_pairwise_brackets, twoway_posthoc,
    build_stats_report, write_report, save_figure, emit_run_script,
)

# === 改 1:基础名 ===
NAME = "my_3groups"

# === 改 2:水平 + 数据 ===
times = ["0h", "24h", "48h"]
drugs = ["Ctrl", "Drug"]

rng = np.random.default_rng(20260820)
rows = []
for t in times:
    for d in drugs:
        for _ in range(15):
            base = {"0h": 10., "24h": 16., "48h": 18.}[t]
            mult = 1.0 if d == "Ctrl" else 1.3
            rows.append({"time": t, "drug": d,
                         "value": base * mult + rng.normal(0, 2)})
df = pd.DataFrame(rows)

# === 改 3:轴标签 ===
xlabel = "Time after treatment"
ylabel = "Response value"

# === 以下无需改 ===
OUT = pathlib.Path("out"); OUT.mkdir(exist_ok=True)

apply_prism_theme()
fig, ax = plt.subplots(
    figsize=recommend_figsize("grouped", n_groups=len(times) * len(drugs))
)

# 一行调用:整图封装完成柱+点+legend+xlim/ylim+positions 映射
mapping = prism_grouped_bars(ax, df, "time", "drug", "value")
ax.set_xlabel(xlabel); ax.set_ylabel(ylabel)
ax.set_title(f"{NAME}: Grouped bar (Mean ± SEM)")

# 图上标注:简单效应(交互显著)或主效应(不显著)
ph = twoway_posthoc(df, "value ~ C(time)*C(drug)")
if ph.get("type") == "simple_effects":
    for t_i, t in enumerate(mapping["x_levels"]):
        key = f"time={t}: Ctrl vs Drug"
        m = [p for d, p, _ in ph["comparisons"] if d == key]
        if m:
            add_pairwise_brackets(ax, [
                (mapping["positions"]["Ctrl"][t_i],
                 mapping["positions"]["Drug"][t_i], m[0])
            ])
else:
    # 主效应:各组两两
    pos_flat = list(mapping["positions"]["Ctrl"]) + list(mapping["positions"]["Drug"])
    lab_flat = (["Ctrl-" + t for t in mapping["x_levels"]]
                + ["Drug-" + t for t in mapping["x_levels"]])
    comps_lbl = []
    for i in range(len(lab_flat)):
        for j in range(i + 1, len(lab_flat)):
            comps_lbl.append((lab_flat[i], lab_flat[j], 0.05))
    add_pairwise_brackets(ax, comps_lbl, labels=lab_flat)

save_figure(fig, NAME, str(OUT))
report = build_stats_report(
    "twoway", df=df, formula="value ~ C(time)*C(drug)",
    description=f"{times} × {drugs} two-factor experiment.",
)
write_report(NAME, report, str(OUT))
emit_run_script(NAME, out_dir=str(OUT))
print(f"\n[Done] 五件套产物(含本脚本)已写入 {OUT.resolve()}")
