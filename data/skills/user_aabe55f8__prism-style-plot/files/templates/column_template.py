"""Column 表 标准产出模板 — 用户复制改 3 处即可得产物配对的脚本。

使用步骤:
  1. 把本文件复制到工作目录,重命名(例:my_3groups.py)
  2. 改 NAME、数据 groups/labels
  3. 跑 `python my_3groups.py`
  4. OUT/ 里会有 my_3groups.py / my_3groups.png / my_3groups.pdf /
     my_3groups.html / my_3groups_report.md 五个同名配对文件

其他 7 种表型(Grouped / XY / Survival / Contingency / Parts of whole /
Multiple variables / Nested)在同目录下:grouped_template.py /
xy_template.py / survival_template.py / contingency_template.py /
parts_of_whole_template.py / multiple_variables_template.py /
nested_template.py。
"""
import sys, pathlib
HERE = pathlib.Path(__file__).resolve().parent
SKILL = pathlib.Path(r"C:\Users\DELL\.workbuddy\skills\prism-style-plot")
sys.path.insert(0, str(SKILL))

import numpy as np
import matplotlib.pyplot as plt
from scripts.prism_theme import (
    apply_prism_theme, recommend_figsize, prism_bars,
    oneway_anova_tukey, add_pairwise_brackets,
    build_stats_report, write_report, save_figure,
    emit_run_script,   # v2.3.2+ 新增：落盘与产物同前缀的脚本
)

# === 第 1 处改:基础名(脚本/图/报告共用) ===
NAME = "my_3groups"

# === 第 2 处改:你的数据(独立样本一组一个数组) ===
control = np.array([2.13, 3.12, 5.21, 4.32, 5.21])    # ← 改这里
treat_a = np.array([6.32, 5.32, 9.54, 7.56, 8.65])    # ← 改这里
treat_b = np.array([6.98, 7.65, 8.25, 9.31, 8.46])    # ← 改这里
groups = [control, treat_a, treat_b]

# === 第 3 处改:组名 + 轴标签 ===
labels = ["Control", "Treat_A", "Treat_B"]
xlabel = "Treatment group"
ylabel = "Response (a.u.)"

# --- 备选:数据在 CSV/Excel 时,用 read_table 自动读 + 自动 ylabel ---
# 长格式(group 列 + 数值列)会自动拆组,并把数值列名设为 ylabel 默认;
# 宽格式(每列一组)无单一数值列名,ylabel 回退 None(沿用上方默认即可)。
# from scripts.prism_theme import read_table
# tbl = read_table(r"data.csv")          # 或 .xlsx
# groups = tbl["groups"]
# labels = tbl["labels"]
# if tbl["ylabel"] is not None:
#     ylabel = tbl["ylabel"]             # 自动用数值列表头,免手填


# === 以下无需改 ===
OUT = pathlib.Path("out")
OUT.mkdir(exist_ok=True)

apply_prism_theme()
fig, ax = plt.subplots(figsize=recommend_figsize("column", n_groups=len(groups)))
prism_bars(ax, groups, labels)

res = oneway_anova_tukey(groups, labels)
print(f"ANOVA p = {res['anova_p']:.4g}")
add_pairwise_brackets(ax, res["pairwise"], labels=labels)
ax.set_xlabel(xlabel); ax.set_ylabel(ylabel)
ax.set_title(f"{NAME}: {labels[0]} vs {labels[-1]} etc.")

save_figure(fig, NAME, str(OUT))                              # -> {NAME}.png/.pdf
report = build_stats_report(
    "anova_tukey",
    description=f"{labels} three-group comparison; one-way ANOVA + Tukey.",
    groups=groups, labels=labels, error_type="mean ± SEM",
)
write_report(NAME, report, str(OUT))                          # -> {NAME}.html/{NAME}_report.md

# === 关键一行:自动把本脚本源码落盘成 {NAME}.py，与上面产物同前缀 ===
emit_run_script(NAME, out_dir=str(OUT))
print(f"\n[Done] 全部产物（含本脚本）已写入 {OUT.resolve()}")
