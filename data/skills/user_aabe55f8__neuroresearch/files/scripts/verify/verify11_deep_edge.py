#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
verify11_deep_edge.py — 深度边界/性能回归（v2.5.5 新增）

背景（v2.5.5 深度测试，warnings-as-errors 轰击全部绘图函数）：
  1. prism_bars/boxplot/violin 数据含 NaN/Inf → set_ylim 崩溃
     （"Axis limits cannot be NaN or Inf"）→ 入口统一过滤非有限值；
  2. 空组 → "Mean of empty slice"；n=1 组 → std(ddof=1)=NaN 警告
     → 空组跳过、n=1 误差棒 0；
  3. prism_grouped_bars 子格 n=1 → 同上警告 → n=1 误差棒 0；
  4. prism_pie/donut 全零/负值 → 上游英文 ValueError → 预检中文提示；
  5. prism_xy_fit 全同 y/x → scipy OptimizeWarning → 预检中文提示；
  6. palette=[] → IndexError → 空列表回退默认色板；
  7. 性能：_conflict O(n) 遍历 placed → 尾部窗口 O(64)；
     _scatter_overlap_pairs O(k²) → 排序+滑动窗口向量化；
     3×2000 点绘图 30s → ~2s。

本用例断言（锁定以上修复点，防回归）：
  - bars/boxplot 含 NaN/inf 不崩、ylim 有限；
  - bars 空组/单点组不抛 RuntimeWarning（过滤后跳过/误差棒 0）；
  - grouped 子格 n=1 不警告；
  - pie 全零/负值抛中文 ValueError；
  - xy_fit 全同 y 抛中文 ValueError；
  - palette 空列表回退默认色板不崩；
  - _conflict 窗口化后仍能检出已知冲突（构造点对）；
  - 性能冒烟：3×1000 点 best-of-3 < 8s（原 ~9s 起，防 O(n²) 回归）。
退出码：0 = 通过；1 = 失败。
"""
import sys, os, time, warnings
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "..", "scripts"))

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import prism_theme as pt

fails = []


def check(cond, msg):
    print(f"  [{'OK' if cond else 'FAIL'}] {msg}")
    if not cond:
        fails.append(msg)


def probe_no_warn(name, fn):
    """warnings-as-errors 下运行,任何警告/异常都算失败。"""
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            fn()
        print(f"  [OK] {name}")
        return True
    except Exception as e:
        print(f"  [FAIL] {name} → {type(e).__name__}: {str(e)[:70]}")
        fails.append(name)
        return False
    finally:
        plt.close("all")


print("=== verify11_deep_edge.py（深度边界/性能回归 v2.5.5）===")

# ---- 1) NaN / Inf 过滤 ----
print("[1] NaN/Inf 数据不再崩 ylim")
ok = probe_no_warn("bars NaN 混入", lambda: (lambda f, a: (
    pt.prism_bars(a, [[1, 2, np.nan], [3, 4, 5], [2, 3, 4]], ["A", "B", "C"]),
    plt.close(f)))(*plt.subplots()))
ok &= probe_no_warn("bars Inf 混入", lambda: (lambda f, a: (
    pt.prism_bars(a, [[1, 2, np.inf], [3, 4, 5], [2, 3, 4]], ["A", "B", "C"]),
    plt.close(f)))(*plt.subplots()))
ok &= probe_no_warn("bars Inf 混入", lambda: (lambda f, a: (
    pt.prism_bars(a, [[1, 2, np.inf], [3, 4, 5], [2, 3, 4]], ["A", "B", "C"]),
    plt.close(f)))(*plt.subplots()))
# boxplot：seaborn 0.13.2 + matplotlib 3.11 内部 vert= 弃用警告（环境层，
# 3.13 才移除）会误伤 warnings-as-errors——这里只断言不抛业务异常
try:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        fig, ax = plt.subplots()
        pt.prism_boxplot(ax, [[1, 2, np.nan], [3, 4, 5], [2, 3, 4]],
                         ["A", "B", "C"])
    plt.close(fig)
    print("  [OK] boxplot NaN（NaN 已过滤，DeprecationWarning 忽略）")
except Exception as e:
    print(f"  [FAIL] boxplot NaN → {type(e).__name__}: {str(e)[:70]}")
    fails.append("boxplot NaN")
ok &= True
# 过滤后 ylim 必须有限
fig, ax = plt.subplots()
pt.prism_bars(ax, [[1, 2, np.nan], [3, 4, 5], [2, 3, 4]], ["A", "B", "C"])
y0, y1 = ax.get_ylim()
check(np.isfinite(y0) and np.isfinite(y1),
      f"NaN 数据 ylim 有限（{y0:.2f}~{y1:.2f}）")
plt.close(fig)

# ---- 2) 空组 / 单点组 ----
print("[2] 空组跳过 / n=1 误差棒 0")
probe_no_warn("bars 空组", lambda: (lambda f, a: (
    pt.prism_bars(a, [[], [1, 2], [3, 4]], ["A", "B", "C"]),
    plt.close(f)))(*plt.subplots()))
probe_no_warn("bars 单点组", lambda: (lambda f, a: (
    pt.prism_bars(a, [[1.0], [2.0], [3.0]], ["A", "B", "C"]),
    plt.close(f)))(*plt.subplots()))

# ---- 3) grouped 子格 n=1 ----
print("[3] grouped 子格 n=1 不警告")
df1 = pd.DataFrame({"x": ["A", "A", "B", "B"], "g": ["M", "F", "M", "F"],
                    "v": [1.0, 2.0, 3.0, 4.0]})
probe_no_warn("grouped 子格 n=1", lambda: (lambda f, a: (
    pt.prism_grouped_bars(a, df1, "x", "g", "v"),
    plt.close(f)))(*plt.subplots()))

# ---- 4) pie/donut 预检 ----
print("[4] pie/donut 全零/负值中文提示")
for sizes, label in [([0, 0, 0], "全零"), ([-1, 2, 3], "负值")]:
    try:
        pt.prism_pie(plt.subplots()[1], sizes, ["A", "B", "C"])
        check(False, f"pie {label} 应报错")
    except ValueError as e:
        check("饼图" in str(e), f"pie {label} → 中文 ValueError: {str(e)[:30]}...")
    plt.close("all")

# ---- 5) xy_fit 退化预检 ----
print("[5] xy_fit 全同 y 中文提示")
try:
    fig, ax = plt.subplots()
    pt.prism_xy_fit(ax, np.linspace(0.1, 10, 8), np.ones(8))
    check(False, "xy_fit 全同 y 应报错")
except ValueError as e:
    check("全相同" in str(e), f"xy_fit 全同 y → 中文 ValueError: {str(e)[:30]}...")
plt.close("all")

# ---- 6) palette 空列表 ----
print("[6] palette 空列表回退默认")
ok = probe_no_warn("bars palette=[]", lambda: (lambda f, a: (
    pt.prism_bars(a, [[1, 2, 3], [2, 3, 4]], ["A", "B"], palette=[]),
    plt.close(f)))(*plt.subplots()))
fig, ax = plt.subplots()
pt.prism_bars(ax, [[1, 2, 3], [2, 3, 4]], ["A", "B"], palette=[])
bars = [p for p in ax.patches if p.get_width() > 0.1]
check(len(bars) == 2 and len({p.get_facecolor() for p in bars}) == 2,
      "空 palette 回退默认色板（2 根柱、2 种颜色）")
plt.close(fig)

# ---- 7) _conflict 窗口化正确性 ----
print("[7] _conflict 尾部窗口仍检出已知冲突")
placed = [(0.0, 0.0), (0.02, 0.01), (0.05, 0.5), (0.06, 0.52)]
check(pt._conflict(0.03, 0.02, placed, 0.05, 0.05), "y 窗口内冲突检出（窗口 64 内）")
check(not pt._conflict(0.5, 2.0, placed, 0.05, 0.05), "y 差 ≥ d_y 不冲突（提前终止）")

# ---- 8) 性能冒烟（防 O(n²) 回归）----
# 墙钟断言对瞬时负载敏感(v2.5.7 并行化回归曾 5.4s 误报 3.4s 的正常结果)。
# 改 best-of-3 取最小值 + 阈值放宽到 8s:正常 ~3.4s 稳过,修复前 ~9s 起、
# 30s 级的真回归(三取一最小值仍 ≥9s)依旧会被抓住,且不再被负载波动误伤。
print("[8] 性能冒烟：3×1000 点 best-of-3 < 8s")
rng = np.random.default_rng(0)
big = [rng.normal(10, 2, 1000) for _ in range(3)]
dt_min = float("inf")
for _ in range(3):
    t0 = time.perf_counter()
    fig, ax = plt.subplots(figsize=(3, 3))
    pt.prism_bars(ax, big, ["A", "B", "C"])
    dt = time.perf_counter() - t0
    plt.close(fig)
    dt_min = min(dt_min, dt)
check(dt_min < 8.0,
      f"3×1000 点绘图 best-of-3 {dt_min:.1f}s < 8s（修复前 ~9s 起，30s 级）")

print()
if fails:
    print(f"verify11 结果: {len(fails)} 项失败: {fails}")
    sys.exit(1)
print("verify11 结果: 全部通过")
sys.exit(0)
