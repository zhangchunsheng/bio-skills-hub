"""Survival 表 标准产出模板 — Kaplan-Meier + log-rank（可选 Cox 回归）。

使用步骤:
  1. 复制重命名(例:treatment_survival.py)
  2. 改 NAME、time/event/group 数据
  3. 跑 `python treatment_survival.py`,OUT/ 出五件套同前缀产物

Cox 回归（v2.4.3）:
  - 图上:prism_survival(..., show_cox=True) 标注 HR + 95% CI（vs 参照组）
  - 报告:build_stats_report(..., add_cox=True) 附加 Cox 块
  - 需 `pip install lifelines`;log-rank 本身不依赖 lifelines
"""
import sys, pathlib
HERE = pathlib.Path(__file__).resolve().parent
SKILL = pathlib.Path(r"C:\Users\DELL\.workbuddy\skills\prism-style-plot")
sys.path.insert(0, str(SKILL))

import numpy as np
import matplotlib.pyplot as plt
from scripts.prism_theme import (
    apply_prism_theme, recommend_figsize, prism_survival,
    build_stats_report, write_report, save_figure, emit_run_script,
)

# === 改 1:基础名 ===
NAME = "treatment_survival"

# === 改 2:生存数据:time / event (1=事件, 0=删失) / group 三列等长 ===
rng = np.random.default_rng(20260820)
def gen(median_days, n=15):
    times, events = [], []
    for _ in range(n):
        t = float(np.ceil(rng.exponential(median_days / np.log(2))))
        t = min(t, 25)
        events.append(int(rng.random() > 0.10))
        times.append(t)
    return np.array(times), np.array(events)

t_v, e_v = gen(8.0, 15)
t_d, e_d = gen(14.0, 15)
time  = np.concatenate([t_v, t_d])
event = np.concatenate([e_v, e_d])
group = np.array(["Vehicle"] * 15 + ["Drug"] * 15)

# === 改 3:轴标签 ===
xlabel = "Days after treatment"
ylabel = "Survival probability"

OUT = pathlib.Path("out"); OUT.mkdir(exist_ok=True)
apply_prism_theme()
fig, ax = plt.subplots(figsize=recommend_figsize("survival"))
res = prism_survival(ax, time, event, group, show_median=True,
                     show_cox=True, cox_reference="Vehicle",  # Cox 标注（可选）
                     xlabel=xlabel, ylabel=ylabel)
print(f"log-rank p = {res['p']:.4g}, chi2 = {res['chi2']:.3f}")
print(f"中位生存: {res['median']}")
if res.get("cox"):
    for g, hr, lo, hi, p in res["cox"]["comparisons"]:
        print(f"Cox  {g:8s} HR={hr:.2f} 95%CI=[{lo:.2f},{hi:.2f}] p={p:.4g}")
ax.set_title(f"{NAME}: Kaplan-Meier survival")

save_figure(fig, NAME, str(OUT))
report = build_stats_report("survival", time=time, event=event, group=group,
        description="Vehicle vs Drug: log-rank test of survival difference.",
        add_cox=True)   # Cox 块（可选）
write_report(NAME, report, str(OUT))
emit_run_script(NAME, out_dir=str(OUT))
print(f"\n[Done] 五件套产物（含本脚本）已写入 {OUT.resolve()}")
