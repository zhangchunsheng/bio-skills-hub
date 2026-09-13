"""Parts of whole 表 标准产出模板 — 饼图 + 环形图。

使用步骤:
  1. 复制重命名(例:cell_composition.py)
  2. 改 NAME、sizes/labels、center_text
  3. 跑 `python cell_composition.py`,OUT/ 出五件套同前缀产物
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

import matplotlib.pyplot as plt
from prism_theme import (
    apply_prism_theme, recommend_figsize,
    prism_pie, prism_donut, save_figure, emit_run_script,
)

# === 改 1:基础名 ===
NAME = "cell_composition"

# === 改 2:占比 + 标签 ===
sizes = [35, 25, 23, 17]   # 占比或计数,会被自动转 %
labels = ["Neuron", "Astrocyte", "Microglia", "Other"]

# === 改 3:环形图中心文本 ===
center_text = f"n={sum(sizes)}"

OUT = pathlib.Path("out"); OUT.mkdir(exist_ok=True)
apply_prism_theme()
fig, axes = plt.subplots(
    1, 2, figsize=(recommend_figsize("parts_of_whole")[0] * 2,
                   recommend_figsize("parts_of_whole")[1])
)
prism_pie(axes[0], sizes, labels)
prism_donut(axes[1], sizes, labels, center_text=center_text)
axes[0].set_title("Pie")
axes[1].set_title("Donut")
fig.suptitle(f"{NAME}: cell type composition", fontsize=9, y=1.02)
save_figure(fig, NAME, str(OUT))
emit_run_script(NAME, out_dir=str(OUT))
print(f"\n[Done] 五件套产物（含本脚本）已写入 {OUT.resolve()}")
