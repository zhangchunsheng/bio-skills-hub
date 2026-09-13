"""XY 表 标准产出模板 — 4PL 剂量-响应拟合。

使用步骤:
  1. 复制重命名(例:compound_dose.py)
  2. 改 NAME、x/y 数据(可含 0 浓度,会自动过滤)
  3. 跑 `python compound_dose.py`,OUT/ 出五件套同前缀产物
"""
import sys, pathlib
HERE = pathlib.Path(__file__).resolve().parent
SKILL = pathlib.Path(r"C:\Users\DELL\.workbuddy\skills\prism-style-plot")
sys.path.insert(0, str(SKILL))

import numpy as np
import matplotlib.pyplot as plt
from scripts.prism_theme import (
    apply_prism_theme, recommend_figsize, prism_xy_fit,
    save_figure, emit_run_script,
)

# === 改 1:基础名 ===
NAME = "compound_dose"

# === 改 2:你的剂量-响应数据（0 浓度会自动过滤） ===
x = np.array([0, 0.1, 1, 10, 100, 1000, 10000, 100000])  # 浓度,单位 nM
y = np.array([1200, 1310, 1820, 4500, 8215, 9580, 10120, 10080])  # 响应

# === 改 3:轴标签 ===
xlabel = "Compound (nM)"
ylabel = "Luciferase (RLU)"

OUT = pathlib.Path("out"); OUT.mkdir(exist_ok=True)
apply_prism_theme()
fig, ax = plt.subplots(figsize=recommend_figsize("xy"))
res = prism_xy_fit(ax, x, y, model="4pl",
                   xlabel=xlabel, ylabel=ylabel)
print(f"EC50 = {res['ic50']:.3g} nM, R² = {res['r2']:.4f}, "
      f"过滤 {res['dropped']} 个 x≤0 点")
ax.set_title(f"{NAME}: 4PL dose-response (XY)")

save_figure(fig, NAME, str(OUT))
emit_run_script(NAME, out_dir=str(OUT))
print(f"\n[Done] 五件套产物（含本脚本）已写入 {OUT.resolve()}")
