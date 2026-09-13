"""验证 3b：散点布局与 zorder 层级（抖动均衡 + 标签旋转 + error bar 永远最顶层）

v2.3.0 拆分自 verify3_edge.py；保留 3.3 / 3.6 / 3.7 三个原用例。
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import PathCollection

from prism_theme import (
    apply_prism_theme, get_figsize, prism_bars,
    save_figure, jitter_offsets,
)
from verify_common import report, SEED

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
os.makedirs(OUT, exist_ok=True)
fails = []
apply_prism_theme()


# ---------- 3.3 奇数 n 抖动均衡(左右点数差 ≤1) ----------
try:
    r = np.random.default_rng(SEED + 20)
    for n in (3, 5, 7, 9):
        vals = r.normal(0, 1, n)
        fig, ax = plt.subplots(figsize=get_figsize("tall"))
        ax.set_xlim(-0.5, 0.5); ax.set_ylim(-3, 3)
        offs = jitter_offsets(ax, vals, width=0.62, dot_size=25, balanced=True)
        n_left = (offs < 0).sum()
        n_right = (offs > 0).sum()
        assert abs(n_left - n_right) <= 1, f"n={n}: left={n_left}, right={n_right}"
    report("3.3 odd-n balanced jitter", True, "n=3,5,7,9 全部左右差 ≤1")
except Exception as e:
    fails.append(("3.3 odd", e))
    report("3.3 odd-n balanced jitter", False, str(e))


# ---------- 3.6 x 轴长标签旋转检测 ----------
try:
    r = np.random.default_rng(SEED + 40)
    long_labels = ["Very-Long-Label-A", "Very-Long-Label-B", "Very-Long-Label-C"]
    groups = [r.normal(10, 1, 5), r.normal(12, 1, 5), r.normal(14, 1, 5)]
    fig, ax = plt.subplots(figsize=get_figsize("tall"))
    prism_bars(ax, groups, long_labels)
    save_figure(fig, "verify3b_long_labels", OUT)
    rot = ax.get_xticklabels()[0].get_rotation()
    ok = rot != 0
    report("3.6 long label rotation", ok, f"x label rotation = {rot}°")
except Exception as e:
    fails.append(("3.6 rotation", e))
    report("3.6 long label rotation", False, str(e))


# ---------- 3.7 prism_bars error bar zorder 检查 ----------
try:
    r = np.random.default_rng(SEED + 50)
    groups = [r.normal(10, 2, 6), r.normal(12, 2, 6)]
    fig, ax = plt.subplots(figsize=get_figsize("tall"))
    prism_bars(ax, groups, ["A", "B"])
    line_zo = [getattr(l, 'zorder', None) for l in ax.lines
               if getattr(l, 'zorder', None) is not None]
    pc_zo = [getattr(c, 'zorder', None) for c in ax.collections
             if isinstance(c, PathCollection)
             and getattr(c, 'zorder', None) is not None]
    eb_max = max(line_zo) if line_zo else 0
    pt_min = min(pc_zo) if pc_zo else 0
    ok = eb_max > pt_min
    save_figure(fig, "verify3b_zorder", OUT)
    report("3.7 error bar zorder > points", ok,
           f"line_max_z={eb_max}, point_min_z={pt_min}")
except Exception as e:
    fails.append(("3.7 zorder", e))
    report("3.7 error bar zorder > points", False, str(e))


print("\n===== 3b（布局+zorder）完成,失败数:", len(fails), "=====")
for name, e in fails:
    print(f"  FAIL {name}: {type(e).__name__}: {e}")
sys.exit(1 if fails else 0)
