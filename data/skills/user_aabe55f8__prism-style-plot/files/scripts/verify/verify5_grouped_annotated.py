"""验证 5:Grouped 图 + 简单效应图上显著性标注(正确打开方式)

v2.3.0 增厚为 7 项断言，覆盖：
- twoway_posthoc 返回 type 为 simple_effects（交互显著）
- comps_xy 长度 = 3（每时点一对）
- 0h/24h 不显著（无 **** 标注）
- 48h 显著（至少一个 **** 标注）
- ax.patches 数量 = 6（3 时点 × 2 药物）
- 图例 label = {Ctrl, Drug}
- error bar zorder > scatter zorder（zorder 拓扑全局规则）
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import to_rgba
from matplotlib.collections import PathCollection

from prism_theme import (apply_prism_theme, get_figsize, add_individual_dots,
                         add_pairwise_brackets, twoway_posthoc, finish_axes,
                         palette_sequence, save_figure, format_p)
from verify_common import report, SEED

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
os.makedirs(OUT, exist_ok=True)
fails = []
apply_prism_theme()

# ---- 构造交互数据:药物仅在 48h 起效 ----
r = np.random.default_rng(SEED + 100)
rows = []
for t in ["0h", "24h", "48h"]:
    for drug in ["Ctrl", "Drug"]:
        base = {"0h": 10, "24h": 10, "48h": 10}[t]
        eff = 6.0 if (t == "48h" and drug == "Drug") else 0.0
        for _ in range(6):
            rows.append({"time": t, "drug": drug,
                         "value": base + eff + r.normal(0, 1.2)})
df = pd.DataFrame(rows)

# ---- 1. 分组柱状图(手写,同标准画法) ----
times = ["0h", "24h", "48h"]
fig, ax = plt.subplots(figsize=get_figsize("wide"))
cols = palette_sequence("okabe_ito")[:2]
x = np.arange(len(times)); w = 0.35
ax.set_xlim(-0.5, len(times) - 0.5)
ax.set_ylim(min(0, df["value"].min()) * 1.15,
            max(0, df["value"].max()) * 1.15)

ctrl_x, drug_x = [], []
for d_i, (drug, c) in enumerate(zip(["Ctrl", "Drug"], cols)):
    means, sems, vals = [], [], []
    for t in times:
        g = df[(df["time"] == t) & (df["drug"] == drug)]["value"].values
        means.append(g.mean()); sems.append(g.std(ddof=1) / np.sqrt(len(g)))
        vals.append(g)
    xs = x + (d_i - 0.5) * w
    (ctrl_x if drug == "Ctrl" else drug_x).extend(xs)
    ax.bar(xs, means, width=w, yerr=sems,
           facecolor=to_rgba(c, 0.55), edgecolor="black", linewidth=0.75,
           label=drug, zorder=2, capsize=3,
           error_kw=dict(zorder=6, lw=0.75, capthick=0.75))
    for xi, g in zip(xs, vals):
        add_individual_dots(ax, xi, g, color=c, width=w, dot_size=None)
ax.set_xticks(x); ax.set_xticklabels(times)
ax.set_xlabel("Time after treatment")
ax.set_ylabel("Response value")
ax.legend(frameon=False, fontsize=7)


# ---------- 5.1 twoway_posthoc 返回 type 为 simple_effects ----------
try:
    ph = twoway_posthoc(df, "value ~ C(time)*C(drug)")
    ok = ph.get("type") == "simple_effects"
    report("5.1 twoway_posthoc identifies interaction", ok,
           f"type={ph.get('type')!r} (期望 simple_effects)")
    if not ok:
        raise AssertionError("type mismatch")
except Exception as e:
    fails.append(("5.1 posthoc type", e))


# ---- 2. 简单效应映射到柱子 x 坐标 ----
comps_xy = []
for t_i, t in enumerate(times):
    key = f"time={t}: Ctrl vs Drug"
    match = [(d, p) for d, p, s in ph["comparisons"] if d == key]
    if match:
        comps_xy.append((ctrl_x[t_i], drug_x[t_i], match[0][1]))
        print(f"  annotate {key} -> p={format_p(match[0][1])}")

add_pairwise_brackets(ax, comps_xy)
finish_axes(ax, data_max=float(df["value"].max()))
save_figure(fig, "verify5_grouped_annotated", OUT)


# ---------- 5.2 comps_xy 长度 = 3（每个时点一对对比） ----------
try:
    ok = len(comps_xy) == 3
    report("5.2 comps_xy covers all 3 time points", ok,
           f"comps_xy={len(comps_xy)} (期望 3)")
    if not ok:
        raise AssertionError(f"len={len(comps_xy)}")
except Exception as e:
    fails.append(("5.2 comps len", e))


# ---------- 5.3 0h/24h 不显著（p≥0.1，无 **** 标注） ----------
try:
    comps_early = [(x1, x2, p) for (x1, x2, p), t in zip(comps_xy, times)
                   if t in ("0h", "24h")]
    early_all_ns = all(p >= 0.1 for (x1, x2, p) in comps_early)
    texts = [t.get_text() for t in ax.texts]
    star_texts = [t for t in texts if "*" in t and t not in ("*",)]
    has_4star = any("****" in t for t in star_texts)
    ok = early_all_ns
    report("5.3 0h/24h no significance (consistent with early p)", ok,
           f"early_ps={[round(p, 4) for (_,_,p) in comps_early]}; 4*标注={has_4star}")
    if not ok:
        raise AssertionError("early time significant unexpectedly")
except Exception as e:
    fails.append(("5.3 early ns", e))


# ---------- 5.4 48h 显著（p<0.05，至少一个 **** 标注） ----------
try:
    late = [(x1, x2, p) for (x1, x2, p), t in zip(comps_xy, times) if t == "48h"]
    late_p = late[0][2] if late else 1.0
    texts = [t.get_text() for t in ax.texts]
    n_4star = sum(1 for t in texts if "****" in t)
    ok = late_p < 0.0001 and n_4star >= 1
    report("5.4 48h significant (**** annotation on figure)", ok,
           f"48h p={late_p:.2e}; 4*标注数={n_4star}")
    if not ok:
        raise AssertionError(f"late_p={late_p} n_4star={n_4star}")
except Exception as e:
    fails.append(("5.4 late sig", e))


# ---------- 5.5 ax.patches 数量 = 6（3 时点 × 2 药物） ----------
try:
    n_bars = len(ax.patches)
    ok = n_bars == 6
    report("5.5 grouped bars count = 6", ok, f"bars={n_bars} (期望 6)")
    if not ok:
        raise AssertionError(f"bars={n_bars}")
except Exception as e:
    fails.append(("5.5 bar count", e))


# ---------- 5.6 图例 label = {Ctrl, Drug} ----------
try:
    handles, lbls = ax.get_legend_handles_labels()
    ok = set(lbls) == {"Ctrl", "Drug"}
    report("5.6 legend labels = {Ctrl, Drug}", ok, f"labels={lbls}")
    if not ok:
        raise AssertionError(f"labels={lbls}")
except Exception as e:
    fails.append(("5.6 legend", e))


# ---------- 5.7 error bar zorder > scatter zorder（zorder 拓扑全局规则） ----------
try:
    line_zo = [getattr(l, 'zorder', None) for l in ax.lines
               if getattr(l, 'zorder', None) is not None]
    pc_zo = [getattr(c, 'zorder', None) for c in ax.collections
             if isinstance(c, PathCollection)
             and getattr(c, 'zorder', None) is not None]
    eb_max = max(line_zo) if line_zo else 0
    pt_min = min(pc_zo) if pc_zo else 0
    ok = eb_max > pt_min
    report("5.7 error bar zorder > scatter zorder", ok,
           f"line_max_z={eb_max}, point_min_z={pt_min}")
    if not ok:
        raise AssertionError(f"line_max_z={eb_max}, point_min_z={pt_min}")
except Exception as e:
    fails.append(("5.7 zorder topology", e))


print("\n===== Grouped 图 + 简单效应验证完成,失败数:", len(fails), "=====")
for name, e in fails:
    print(f"  FAIL {name}: {type(e).__name__}: {e}")
sys.exit(1 if fails else 0)
