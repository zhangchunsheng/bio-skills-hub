#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
verify8_ylim_small_allsigns.py — <1 值域修复向全图型推广回归（v2.5.2 新增）

背景（v2.5.2，用户要求"把 y 轴小于 1 的优化应用到其他绘图过程"）：
  v2.5.1 修了 `_is_half_multiple` 步长过滤与 `add_pairwise_brackets` 的
  data_max 收集（Rectangle 单位矩形污染），但 <1 值域同类坑还潜伏在：
  1. `_floor_half_step`（y 轴下限对齐）仍硬钉 0.5 倍数——seaborn
     boxplot/violin 自动 padding 出的 <1 非零下限（如 0.2~0.8 数据的
     -0.1）会被拉到 -0.5，白白浪费下方空间；所有走 finish_axes /
     set_nice_ylim 的路径（bars/box/violin/grouped/nested/xy_fit 等）都受影响；
  2. prism_boxplot 边框重绘用 patch.get_path().get_extents()——对
     seaborn 0.12 的 Rectangle 同样返回单位矩形 (0,0)-(1,1)，边框会画成
     整个轴框（当前 0.13.2 是 PathPatch 才没爆发，跨版本地雷）。

本用例断言：
  - _floor_half_step 按量级分级：0.98→0.95、-0.1→-0.1（不再到 -0.5）、
    -0.37→-0.4、44.28→44.0（>1 行为保持）、0.053→0.05、0.003→0.003；
  - prism_boxplot <1 数据：边框线框 y 范围与真实箱体一致（非单位矩形），
    ylim 顶部 ≤1.35×数据最大值；
  - prism_violin <1 数据：ylim 收尾漂亮（步长 <0.5、刻度 ≥4）；
  - prism_grouped_bars <1 数据：ylim 顶部 ≤1.35×数据最大值；
  - 负值/非零下限场景：ylim 下限不被 0.5 网格粗化（≥ 数据下限 -0.06）。
退出码：0 = 通过；1 = 失败。
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "..", "scripts"))

import numpy as np
import pandas as pd
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


print("=== verify8_ylim_small_allsigns.py（<1 值域修复全图型推广回归）===")

# ---- 1) _floor_half_step 分级 ----
print("[1] _floor_half_step 按量级分级（v2.5.2 核心修复）")
cases = [
    (0.98, 0.95, "<1 正下限对齐 0.05 网格"),
    (-0.10, -0.10, "负下限不再被 0.5 网格拉到 -0.5"),
    (-0.37, -0.40, "负下限向下对齐 0.05 网格"),
    (44.28, 44.0, ">1 行为保持（0.5 倍数，v2.0.24 兼容）"),
    (0.053, 0.05, "0.005 网格"),
    (0.003, 0.003, "10^k 网格"),
    (0.0, 0.0, "0 原样"),
]
for x, exp, note in cases:
    got = pt._floor_half_step(x)
    check(abs(got - exp) < 1e-9,
          f"floor_half_step({x}) = {got}（期望 {exp}，{note}）")

# ---- 2) prism_boxplot <1 值域：边框线框用数据坐标 ----
print("[2] prism_boxplot（<1 值域）边框线框 y 范围 = 真实箱体")
rng = np.random.default_rng(7)
data = [rng.uniform(0.20, 0.45, 8), rng.uniform(0.30, 0.55, 8),
        rng.uniform(0.18, 0.40, 8)]
allmax = max(d.max() for d in data)
allmin = min(d.min() for d in data)
pt.apply_prism_theme()
fig, ax = plt.subplots(figsize=pt.recommend_figsize("column", n_groups=3))
pt.prism_boxplot(ax, data, ["Ctrl", "Low", "High"])
y0, y1 = ax.get_ylim()
check(y1 <= allmax * 1.35,
      f"boxplot ylim 顶部 {y1:.3f} ≤ 1.35×data_max={allmax:.3f}")
# 边框线框：5 点闭合线框（x0,x1,x1,x0,x0），y 范围必须落在真实数据范围内
frame_ys = []
for line in ax.lines:
    xd, yd = line.get_xdata(), line.get_ydata()
    # 边框重绘线：[x0,x1,x1,x0,x0]×[y0,y0,y1,y1,y0] → 底/顶各两点重合
    if len(xd) == 5 and yd[0] == yd[1] and yd[2] == yd[3]:
        frame_ys.append((yd.min(), yd.max()))
check(len(frame_ys) == 3, f"边框线框数量 = 3（实际 {len(frame_ys)}）")
if frame_ys:
    ymin_frame = min(f[0] for f in frame_ys)
    ymax_frame = max(f[1] for f in frame_ys)
    check(ymax_frame < 1.0 and ymin_frame < allmax,
          f"边框 y 范围 {ymin_frame:.3f}~{ymax_frame:.3f} 为数据坐标"
          f"（修复前 Rectangle 单位矩形会画成 0~1 全轴框）")
fig.savefig(os.path.join(OUT, "verify8_ylim_small_box.png"), dpi=150,
            bbox_inches="tight")
plt.close(fig)

# ---- 3) prism_violin <1 值域 ----
print("[3] prism_violin（<1 值域）ylim 收尾漂亮")
fig, ax = plt.subplots(figsize=pt.recommend_figsize("column", n_groups=3))
pt.prism_violin(ax, data, ["Ctrl", "Low", "High"])
y0, y1 = ax.get_ylim()
ticks = ax.get_yticks()
step = np.diff(ticks).min() if len(ticks) > 1 else np.nan
check(y1 >= allmax, f"violin ylim 顶部 {y1:.3f} ≥ data_max（不切数据）")
check((np.isfinite(step) and step < 0.5) or len(ticks) <= 2,
      f"violin 刻度步长 {step} < 0.5（<1 值域细刻度）")
check(len(ticks) >= 4, f"violin 刻度数 {len(ticks)} ≥ 4")
fig.savefig(os.path.join(OUT, "verify8_ylim_small_violin.png"), dpi=150,
            bbox_inches="tight")
plt.close(fig)

# ---- 4) prism_grouped_bars <1 值域 ----
print("[4] prism_grouped_bars（<1 值域）ylim 顶部 ≤1.35×data_max")
df = pd.DataFrame({
    "x": ["Ctrl", "Ctrl", "TreatA", "TreatA", "TreatB", "TreatB"],
    "sub": ["M", "F", "M", "F", "M", "F"],
    "val": [0.31, 0.27, 0.52, 0.44, 0.95, 0.88],
})
fig, ax = plt.subplots(figsize=pt.recommend_figsize("column", n_groups=3))
pt.prism_grouped_bars(ax, df, "x", "sub", "val")
y0, y1 = ax.get_ylim()
gmax = df["val"].max()
check(y1 <= gmax * 1.35,
      f"grouped ylim 顶部 {y1:.3f} ≤ 1.35×data_max={gmax:.3f}")
check(y1 >= gmax, f"grouped ylim 顶部 {y1:.3f} ≥ data_max（不切数据）")
fig.savefig(os.path.join(OUT, "verify8_ylim_small_grouped.png"), dpi=150,
            bbox_inches="tight")
plt.close(fig)

# ---- 5) 负值/非零下限场景 ----
print("[5] 非零下限（负值数据）下限不被 0.5 网格粗化")
neg = [rng.uniform(-0.45, -0.05, 8), rng.uniform(-0.30, 0.10, 8),
       rng.uniform(-0.20, 0.25, 8)]
nmin = min(d.min() for d in neg)
fig, ax = plt.subplots(figsize=pt.recommend_figsize("column", n_groups=3))
pt.prism_bars(ax, neg, ["A", "B", "C"])
y0, y1 = ax.get_ylim()
check(y0 <= nmin, f"ylim 下限 {y0:.3f} ≤ 数据下限 {nmin:.3f}（不切数据）")
# 数据下限 ≈-0.44，prism_bars 先 padding 1.15× → -0.51，再向下对齐 0.05 网格
# → -0.55（修复前 0.5 网格 floor(-0.51/0.5)=-2 → -1.0，浪费整行空间）
check(y0 > -0.6,
      f"ylim 下限 {y0:.3f} 未被 0.5 网格粗化（修复前会被拉到 -1.0）")
check(abs(y0 / 0.05 - round(y0 / 0.05)) < 1e-9,
      f"ylim 下限 {y0:.3f} 落在 0.05 网格上")
fig.savefig(os.path.join(OUT, "verify8_ylim_small_neg.png"), dpi=150,
            bbox_inches="tight")
plt.close(fig)

# ---- 6) >1 旧场景回归 ----
print("[6] >1 值域下限对齐行为保持（44.28→44.0）")
check(pt._floor_half_step(44.28) == 44.0,
      "floor_half_step(44.28) = 44.0（v2.0.24 行为保持）")

print()
if fails:
    print(f"verify8 结果: {len(fails)} 项失败")
    for f in fails:
        print(f"  - {f}")
    sys.exit(1)
print("verify8 结果: 全部通过")
sys.exit(0)
