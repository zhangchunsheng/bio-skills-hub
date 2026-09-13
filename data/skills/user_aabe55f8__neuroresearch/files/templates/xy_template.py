"""XY 表 标准产出模板 — 4PL 剂量-响应拟合。

使用步骤:
  1. 复制重命名(例:compound_dose.py)
  2. 改 NAME、x/y 数据(可含 0 浓度,会自动过滤)
  3. 跑 `python compound_dose.py`,OUT/ 出五件套同前缀产物
"""
import sys, pathlib
HERE = pathlib.Path(__file__).resolve().parent

def _engine_dir():
    # 引擎定位（自包含，不依赖外部 prism-style-plot 技能——引擎就内建在本技能
    # scripts/prism_theme.py，别人只装本技能即可用）：
    # 1) 模板仍在技能目录内 → 技能根/scripts；
    # 2) 模板被复制到工作目录 → 回退到用户级 (~/.workbuddy/skills) 与
    #    项目级 (工作目录向上找 .workbuddy/skills) 的技能安装位置。
    cands = [HERE.parent / "scripts", HERE / "scripts",
             pathlib.Path.home() / ".workbuddy" / "skills" / "neuroresearch" / "scripts"]
    _cwd = pathlib.Path.cwd()
    cands += [p / ".workbuddy" / "skills" / "neuroresearch" / "scripts"
              for p in [_cwd] + list(_cwd.parents)[:6]]
    for cand in cands:
        if (cand / "prism_theme.py").exists():
            return cand
    raise SystemExit("未找到 neuroresearch 绘图引擎 scripts/prism_theme.py（技能未安装或已移动）")

SKILL = _engine_dir()
sys.path.insert(0, str(SKILL))

import numpy as np
import matplotlib.pyplot as plt
from prism_theme import (
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
