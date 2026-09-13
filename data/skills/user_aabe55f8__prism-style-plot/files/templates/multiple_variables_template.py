"""Multiple variables 表 标准产出模板 — pairplot + facet boxplot。

注意:v2.3.1 起,prism_pairplot / prism_facet_boxplot 内部 plt.subplots() 自建 figure,
**不要**再预先 plt.figure()。直接接 fig, axes = ... 即可。

使用步骤:
  1. 复制重命名(例:biomarker_panel.py)
  2. 改 NAME、df 数据
  3. 跑 `python biomarker_panel.py`,OUT/ 出五件套同前缀产物
"""
import sys, pathlib
HERE = pathlib.Path(__file__).resolve().parent
SKILL = pathlib.Path(r"C:\Users\DELL\.workbuddy\skills\prism-style-plot")
sys.path.insert(0, str(SKILL))

import numpy as np
import pandas as pd
from scripts.prism_theme import (
    apply_prism_theme, prism_pairplot, prism_facet_boxplot,
    save_figure, emit_run_script,
)

# === 改 1:基础名 ===
NAME = "biomarker_panel"

# === 改 2:wide-format 数据 ===
rng = np.random.default_rng(20260820)
rows = []
for cohort in ["WT", "KO-A", "KO-B"]:
    mu = {"WT": 50, "KO-A": 65, "KO-B": 40}[cohort]
    for _ in range(20):
        a = rng.normal(mu, 8)
        b = 0.7 * a + rng.normal(0, 5)
        c = -0.4 * a + rng.normal(0, 6)
        rows.append({"cohort": cohort, "a": a, "b": b, "c": c})
df = pd.DataFrame(rows)

OUT = pathlib.Path("out"); OUT.mkdir(exist_ok=True)
apply_prism_theme()

# Pairplot (do NOT pre-create figure)
fig, _ = prism_pairplot(df, cols=["a", "b", "c"], hue="cohort")
fig.suptitle(f"{NAME}: pairplot (lower-tri + KDE diag)",
             fontsize=9, y=1.02)
save_figure(fig, f"{NAME}_pairplot", str(OUT))

# Facet boxplot
df_long = df.melt(id_vars=["cohort"],
                  value_vars=["a", "b", "c"],
                  var_name="gene", value_name="expr")
fig, _ = prism_facet_boxplot(df_long, x="gene", y="expr",
                             facet="cohort", ncols=3)
fig.suptitle(f"{NAME}: facet boxplot per cohort",
             fontsize=9, y=1.02)
save_figure(fig, f"{NAME}_facet", str(OUT))

# 一个脚本可产出多组产物;emit_run_script 把脚本按 NAME.py 落盘（与主名一致）
emit_run_script(NAME, out_dir=str(OUT))
print(f"\n[Done] 产物（含 {NAME}.py）已写入 {OUT.resolve()}")
