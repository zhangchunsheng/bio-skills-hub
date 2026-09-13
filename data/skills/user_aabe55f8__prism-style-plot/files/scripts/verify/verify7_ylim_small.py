#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
verify7_ylim_small.py — ylim 值 <1 时的绘图回归（v2.5.1 新增）

背景（v2.5.1 修复）：
  用户验证 ylim<1（归一化/比例数据，值域 0~0.x）时发现两个 bug 叠加：
  1. _is_half_multiple 的 0.5 倍数过滤误杀 0.05/0.1/0.2/0.25 等 <1 值域
     漂亮步长 → _nice_ylim_top 只能给 0.5 步长，数据 0.6 被顶到 1.0
     （1.67×，远超 1.3× 约束），数据 0.08 顶到 0.5（刻度只剩 2 个）；
  2. add_pairwise_brackets 收集 data_max 用 patch.get_path().get_extents()，
     对 ax.bar 的 Rectangle 返回**单位矩形 (0,0)-(1,1)**（真实坐标在
     transform 里）→ data_max 被污染成 1.0 → base=1.02、bracket 画在
     y≈1.07、ylim 顶到 1.5（数据>1 时被真实值盖过不显现，<1 时爆发）。

本用例断言：
  - _nice_ylim_top 对 <1 target 给出细粒度步长（0.05/0.1/0.2...），
    顶部/数据 ≤ 1.3×（1.3× 约束）；
  - prism_bars / prism_boxplot 在 <1 数据下 ylim 顶部贴近数据最大值的
    1.0~1.3×（不再被顶到 1.0 / 0.5 的粗刻度）；
  - add_pairwise_brackets 后 ylim 不再被 Rectangle 单位矩形污染
    （bracket 基线与数据最大值同量级，ylim 顶部 ≤ 1.5×data_max）。
退出码：0 = 通过；1 = 失败。
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "..", "scripts"))

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import prism_theme as pt

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
os.makedirs(OUT, exist_ok=True)
fails = []


def check(cond, msg):
    print(f"  [{'OK' if cond else 'FAIL'}] {msg}")
    if not cond:
        fails.append(msg)


print("=== verify7_ylim_small.py（ylim<1 值域回归）===")

# ---- 1) _nice_ylim_top 对 <1 target 的步长粒度 ----
print("[1] _nice_ylim_top 细粒度步长（顶部 ≤ 1.3×target 且步长 <0.5）")
for target in [0.6, 0.33, 0.08]:
    top, step = pt._nice_ylim_top(target)
    ratio = top / target
    check(0 < step < 0.5 or abs(step - 0.5) < 1e-9,
          f"target={target}: step={step}（<1 值域应给出 0.05/0.1/0.2 级细步长）")
    check(ratio <= 1.31, f"target={target}: top={top}, 顶部/数据={ratio:.2f}（≤1.3×）")

# ---- 2) prism_bars <1 数据 ----
print("[2] prism_bars（数据 0.2~0.6）ylim 顶部贴近 1.3×")
rng = np.random.default_rng(42)
data = [rng.uniform(0.25, 0.55, 8), rng.uniform(0.30, 0.60, 8),
        rng.uniform(0.20, 0.42, 8)]
allmax = max(d.max() for d in data)
pt.apply_prism_theme()
fig, ax = plt.subplots(figsize=pt.recommend_figsize("column", n_groups=3))
pt.prism_bars(ax, data, ["Ctrl", "Low", "High"])
y0, y1 = ax.get_ylim()
check(y1 <= allmax * 1.35, f"ylim 顶部 {y1:.3f} ≤ 1.35×data_max={allmax:.3f}")
check(y1 >= allmax, f"ylim 顶部 {y1:.3f} ≥ data_max={allmax:.3f}（不切数据）")

# ---- 3) add_pairwise_brackets 不被 Rectangle 单位矩形污染 ----
print("[3] add_pairwise_brackets 后 ylim 不再被顶到 ~1.5")
res = pt.oneway_anova_tukey(data, ["Ctrl", "Low", "High"])
pt.add_pairwise_brackets(ax, res["pairwise"], labels=["Ctrl", "Low", "High"])
y0, y1 = ax.get_ylim()
check(y1 <= allmax * 1.5,
      f"bracket 后 ylim 顶部 {y1:.3f} ≤ 1.5×data_max={allmax:.3f}"
      f"（修复前被污染为 1.0+，顶到 1.5）")
fig.savefig(os.path.join(OUT, "verify7_ylim_small_bars.png"), dpi=150,
            bbox_inches="tight")
plt.close(fig)

# ---- 4) 更小量级 0.01~0.08 ----
print("[4] 更小量级（0.01~0.08）刻度不被粗化成 0.5")
data2 = [rng.uniform(0.01, 0.05, 6), rng.uniform(0.02, 0.06, 6),
         rng.uniform(0.01, 0.08, 6)]
allmax2 = max(d.max() for d in data2)
fig, ax = plt.subplots(figsize=pt.recommend_figsize("column", n_groups=3))
pt.prism_bars(ax, data2, ["A", "B", "C"])
y0, y1 = ax.get_ylim()
ticks = ax.get_yticks()
check(y1 <= allmax2 * 1.35, f"ylim 顶部 {y1:.3f} ≤ 1.35×data_max={allmax2:.3f}")
check(len(ticks) >= 4, f"刻度数 {len(ticks)} ≥ 4（修复前仅 2 个：0/0.5）")
fig.savefig(os.path.join(OUT, "verify7_ylim_small_tiny.png"), dpi=150,
            bbox_inches="tight")
plt.close(fig)

# ---- 5) 箱线图 <1 值域 ----
print("[5] prism_boxplot（<1 值域）")
fig, ax = plt.subplots(figsize=pt.recommend_figsize("column", n_groups=3))
pt.prism_boxplot(ax, data, ["Ctrl", "Low", "High"])
y0, y1 = ax.get_ylim()
check(y1 <= allmax * 1.35, f"boxplot ylim 顶部 {y1:.3f} ≤ 1.35×data_max={allmax:.3f}")
fig.savefig(os.path.join(OUT, "verify7_ylim_small_box.png"), dpi=150,
            bbox_inches="tight")
plt.close(fig)

# ---- 6) >1 旧场景回归（必须保持 v2.0.22 行为）----
print("[6] >1 值域回归（44.28/173.4 等大值仍走 0.5 倍数刻度）")
for target, exp_ok in [(44.28, True), (173.4, True), (27.5, True)]:
    top, step = pt._nice_ylim_top(target)
    check(pt._is_half_multiple(step),
          f"target={target}: step={step} 仍为 0.5 倍数（v2.0.22 行为保持）")

print()
if fails:
    print(f"verify7 结果: {len(fails)} 项失败")
    for f in fails:
        print(f"  - {f}")
    sys.exit(1)
print("verify7 结果: 全部通过")
sys.exit(0)
