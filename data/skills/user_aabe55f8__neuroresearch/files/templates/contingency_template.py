"""Contingency 表 标准产出模板 — 计数 × 卡方/Fisher。

使用步骤:
  1. 复制重命名(例:response_by_arm.py)
  2. 改 NAME、2D 计数 table 与组名 labels
  3. 跑 `python response_by_arm.py`,OUT/ 出五件套同前缀产物
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
from scipy.stats import chi2_contingency
from prism_theme import (
    apply_prism_theme, recommend_figsize, palette_sequence,
    format_p, build_stats_report, write_report, save_figure,
    emit_run_script, finish_axes,
)

# === 改 1:基础名 ===
NAME = "response_by_arm"

# === 改 2:2D 计数表（行：响应类别，列：组） ===
table = np.array([
    [25, 18, 8],   # Non-responder
    [ 5, 12, 22],  # Responder
])

# === 改 3:列名 + 行名 ===
labels = ["Placebo", "Drug-Low", "Drug-High"]
row_labels = ["Non-responder", "Responder"]

chi2, p, dof, expected = chi2_contingency(table)
print(f"χ²({dof}) = {chi2:.3f}, p = {p:.4g}")

OUT = pathlib.Path("out"); OUT.mkdir(exist_ok=True)
apply_prism_theme()
fig, ax = plt.subplots(figsize=recommend_figsize("contingency"))
colors = palette_sequence("okabe_ito")[:table.shape[0]]
x = np.arange(len(labels)); width = 0.38

for r_i, (row, c, lab) in enumerate(zip(table, colors, row_labels)):
    xs = x + (r_i - 0.5) * width
    ax.bar(xs, row, width=width, color=c, alpha=0.85,
           edgecolor="black", linewidth=0.75, label=lab, zorder=2)
    for xi, v in zip(xs, row):
        ax.text(xi, v + 0.8, str(int(v)), ha="center", va="bottom", fontsize=6)
ax.set_xticks(x); ax.set_xticklabels(labels)
ax.set_xlabel("Treatment arm"); ax.set_ylabel("Number of subjects")
finish_axes(ax, data_max=float(table.max()))
ax.text(0.99, 1.02, f"χ²({dof}) = {chi2:.2f}, {format_p(p)}",
        transform=ax.transAxes, ha="right", va="bottom", fontsize=6,
        bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="none", alpha=0.9))
ax.legend(frameon=False, fontsize=7, loc="lower left",
          bbox_to_anchor=(0.01, 1.02), ncol=1)
ax.set_title(f"{NAME}: chi-square test of independence")

save_figure(fig, NAME, str(OUT))
report = build_stats_report("contingency", table=table,
        description=f"Response distribution across {labels}; chi-square test.")
write_report(NAME, report, str(OUT))
emit_run_script(NAME, out_dir=str(OUT))
print(f"\n[Done] 五件套产物（含本脚本）已写入 {OUT.resolve()}")
