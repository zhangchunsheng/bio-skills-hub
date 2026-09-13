"""验证 3a：散点尺寸与配色（点径算法 + 大样本透明度 + 多组循环色）

v2.3.0 拆分自 verify3_edge.py；保留 3.1 / 3.5 / 3.15 三个原用例外，新增：
- 3.16  mann_whitney_u 返回值类型 + 边界触发
- 3.17  wilcoxon_signed_rank 配对检验 + 长度不一致报错
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from prism_theme import (
    apply_prism_theme, get_figsize, prism_bars,
    save_figure, add_pairwise_brackets,
    common_point_size, auto_dot_alpha,
    _apply_overlap_alpha,
    mann_whitney_u, wilcoxon_signed_rank,
)
from verify_common import report, SEED

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
os.makedirs(OUT, exist_ok=True)
fails = []
apply_prism_theme()


# ---------- 3.1 大样本 n=40 散点透明度补偿 ----------
try:
    r = np.random.default_rng(SEED + 10)
    groups = [r.normal(m, 2, 40) for m in (10, 12, 16)]
    labels = ["C", "L", "H"]
    fig, ax = plt.subplots(figsize=get_figsize("tall"))
    prism_bars(ax, groups, labels)
    dot_size = common_point_size(120, 3)
    alpha_before = auto_dot_alpha(120, 3)
    alpha_after = _apply_overlap_alpha(ax, dot_size ** 2, alpha_before)
    add_pairwise_brackets(ax,
        [("C","L",0.05),("C","H",1e-6),("L","H",1e-4)], labels=labels)
    save_figure(fig, "verify3a_largen_bar", OUT)
    ok = alpha_after < alpha_before
    report("3.1 large-n prism_bars", ok,
           f"alpha {alpha_before:.2f}→{alpha_after:.2f}, dot={dot_size:.2f}pt")
except Exception as e:
    fails.append(("3.1 largen", e))
    report("3.1 large-n prism_bars", False, str(e))


# ---------- 3.5 10 组 > 色板容量(循环取色) ----------
try:
    r = np.random.default_rng(SEED + 30)
    groups = [r.normal(m, 1, 5) for m in range(10)]
    labels = [f"G{i}" for i in range(10)]
    fig, ax = plt.subplots(figsize=get_figsize("wide"))
    prism_bars(ax, groups, labels)
    bars = ax.patches
    colors = {tuple(p.get_facecolor()) for p in bars}
    assert len(colors) >= 6
    add_pairwise_brackets(ax, [(labels[i], labels[i+1], 0.01) for i in range(9)],
                          labels=labels)
    save_figure(fig, "verify3a_manygroups_bar", OUT)
    report("3.5 10 groups color cycling", True,
           f"bars={len(bars)}, distinct_colors={len(colors)}")
except Exception as e:
    fails.append(("3.5 color cycle", e))
    report("3.5 10 groups color cycling", False, str(e))


# ---------- 3.15 点径算法关键点（v2.2.3：max 5 / min 2，avg_n 从 4 起调小） ----------
try:
    p4 = common_point_size(4 * 3, 3)
    p8 = common_point_size(8 * 3, 3)
    p32 = common_point_size(32 * 3, 3)
    p100 = common_point_size(100 * 3, 3)
    p10g = common_point_size(8 * 10, 10)
    ok = (p4 == 5.0
          and p8 < 4.5 and p8 > 3.0
          and p32 == 2.0 and p100 == 2.0
          and p10g < p8)
    report("3.15 dot-size algorithm key points", ok,
           f"avg_n4={p4:.2f} avg_n8={p8:.2f} avg_n32={p32:.2f} "
           f"avg_n100={p100:.2f} 10g={p10g:.2f}")
except Exception as e:
    fails.append(("3.15 dot size", e))
    report("3.15 dot-size algorithm key points", False, str(e))


# ---------- 3.16 mann_whitney_u 返回值类型 + 行为 (v2.3.0) ----------
try:
    # 大样本清晰分离 → p<0.05
    a = list(range(1, 11))
    b = list(range(11, 21))
    u_stat, p_val, method = mann_whitney_u(a, b)
    assert isinstance(u_stat, float) and isinstance(p_val, float), "stat/p 应为 float"
    assert method == "Mann-Whitney U", f"method={method!r}"
    assert p_val < 0.05, f"完全分离的 U 应显著,p={p_val}"
    # 边界：空数组应抛错
    try:
        mann_whitney_u([], [1, 2, 3])
        raise AssertionError("空数组应抛 ValueError 但未抛")
    except ValueError:
        pass
    report("3.16 mann_whitney_u", True,
           f"U={u_stat:.2f} p={p_val:.4f}; 空数组正确报错")
except Exception as e:
    fails.append(("3.16 MWU", e))
    report("3.16 mann_whitney_u", False, str(e))


# ---------- 3.17 wilcoxon_signed_rank 配对检验 (v2.3.0) ----------
try:
    a = np.array([5, 6, 7, 8, 9, 10, 11])
    b = np.array([6, 7, 8, 9, 10, 11, 12])
    w_stat, p_val, method = wilcoxon_signed_rank(a, b)
    assert method == "Wilcoxon signed-rank", f"method={method!r}"
    assert isinstance(w_stat, float) and isinstance(p_val, float)
    # 长度不等应抛错
    try:
        wilcoxon_signed_rank([1, 2, 3], [1, 2])
        raise AssertionError("长度不等应抛 ValueError 但未抛")
    except ValueError:
        pass
    report("3.17 wilcoxon_signed_rank", True,
           f"W={w_stat:.2f} p={p_val:.4f}; 长度不等正确报错")
except Exception as e:
    fails.append(("3.17 Wilcoxon", e))
    report("3.17 wilcoxon_signed_rank", False, str(e))


print("\n===== 3a（点径+配色+非参数）完成,失败数:", len(fails), "=====")
for name, e in fails:
    print(f"  FAIL {name}: {type(e).__name__}: {e}")
sys.exit(1 if fails else 0)
