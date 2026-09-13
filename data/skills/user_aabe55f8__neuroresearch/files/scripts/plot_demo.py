# -*- coding: utf-8 -*-
# ============================================================================
# plot_demo.py — neuroresearch Python 绘图引擎验证脚本
# ----------------------------------------------------------------------------
# 用途：用合成数据演示技能「普通科研绘图」的 5 个标准入口，跑通后产出：
#   output/demo_box.png/.pdf   箱线图 + 个体散点 + ANOVA/Tukey 显著性括号
#   output/demo_bar.png/.pdf   带散点柱状图（Mean±SEM）+ 括号
#   output/demo_violin.png/.pdf 小提琴图 + 个体散点
#   output/demo_xy.png/.pdf    XY 散点 + 4PL 剂量-响应拟合
#   output/demo_survival.png/.pdf  KM 生存曲线 + log-rank
#   output/demo_box_report.md  投稿级统计报告（与图同名，图注含精确 p 值）
#
# 运行：$PY plot_demo.py   （$PY = python scripts/ensure_env.py）
# 数据安全：合成数据，不涉及任何真实样本。
# ============================================================================
import importlib.util, subprocess, sys, os

# ---- 依赖自检 + Agg 后端（技能规范：脚本开头必做）----
for m in ["numpy", "pandas", "scipy", "statsmodels", "matplotlib", "seaborn"]:
    if importlib.util.find_spec(m) is None:
        subprocess.check_call([sys.executable, "-m", "pip", "install", m])

import matplotlib
matplotlib.use("Agg")                       # 无显示环境必须
import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # 命中 bundled 引擎
from prism_theme import (
    apply_prism_theme, prism_boxplot, prism_bars, prism_violin,
    prism_survival, prism_xy_fit,
    add_pairwise_brackets, oneway_anova_tukey, build_stats_report,
    write_report, save_figure, get_figsize,
)

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
os.makedirs(OUT, exist_ok=True)
rng = np.random.default_rng(42)             # 固定种子，可复现
apply_prism_theme()

# ===========================================================================
# 1) 箱线图（3 组）+ One-way ANOVA/Tukey + 显著性括号 + 统计报告
# ===========================================================================
ctrl  = rng.normal(5.0, 1.0, 10)
low   = rng.normal(6.8, 1.2, 10)
high  = rng.normal(8.5, 1.4, 10)
groups = [ctrl, low, high]
labels = ["Control", "Drug-Low", "Drug-High"]

fig, ax = plt.subplots(figsize=get_figsize("tall"))
prism_boxplot(ax, groups, labels)
res = oneway_anova_tukey(groups, labels)
add_pairwise_brackets(ax, res["pairwise"], labels=labels)   # 自动分层防重叠
ax.set_ylabel("Expression (a.u.)")
ax.set_title("Boxplot + pairwise brackets")
save_figure(fig, "demo_box", out_dir=OUT)
report_md = build_stats_report("anova_tukey", groups=groups, labels=labels,
                               description="TargetX expression (boxplot demo, n=10 per group)")
write_report("demo_box", report_md, OUT)   # 生成 demo_box_report.md + demo_box.html 总览
print("[demo_box] OK")

# ===========================================================================
# 2) 带散点柱状图（Mean±SEM）+ 括号
# ===========================================================================
bar_groups = [rng.normal(5.0, 1.0, 12), rng.normal(6.5, 1.0, 12),
              rng.normal(4.6, 1.2, 12), rng.normal(7.8, 1.1, 12)]
bar_labels = ["Ctrl", "DrugA", "DrugB", "DrugC"]
fig, ax = plt.subplots(figsize=get_figsize("tall"))
prism_bars(ax, bar_groups, bar_labels, error_type="sem")
res2 = oneway_anova_tukey(bar_groups, bar_labels)
add_pairwise_brackets(ax, res2["pairwise"], labels=bar_labels)
ax.set_ylabel("Mean ± SEM")
ax.set_title("Bar plot + error bars + dots")
save_figure(fig, "demo_bar", out_dir=OUT)
print("[demo_bar] OK")

# ===========================================================================
# 3) 小提琴图 + 显著性括号（复用上方 ANOVA/Tukey 结果）
# ===========================================================================
fig, ax = plt.subplots(figsize=get_figsize("tall"))
prism_violin(ax, groups, labels)
add_pairwise_brackets(ax, res["pairwise"], labels=labels)   # 与箱线图一致标显著性
ax.set_ylabel("Expression (a.u.)")
ax.set_title("Violin + individual dots + brackets")
save_figure(fig, "demo_violin", out_dir=OUT)
print("[demo_violin] OK")

# ===========================================================================
# 4) XY 散点 + 4PL 剂量-响应拟合
# ===========================================================================
x = np.array([0.1, 0.3, 1, 3, 10, 30, 100, 300, 1000, 3000, 10000.])
bottom, top, ec50, hill = 10, 100, 30, 1.0
y = bottom + (top - bottom) / (1 + 10 ** ((np.log10(ec50) - np.log10(x)) * hill))
y = y + rng.normal(0, 3, size=len(x))       # 加噪声
fig, ax = plt.subplots(figsize=get_figsize("wide"))
prism_xy_fit(ax, x, y, model="4pl", xlabel="Concentration (nM)",
             ylabel="Response (%)")
ax.set_title("XY fit: 4PL dose-response")
save_figure(fig, "demo_xy", out_dir=OUT)
print("[demo_xy] OK")

# ===========================================================================
# 5) KM 生存曲线 + log-rank（含两两比较显著性标注）
# ===========================================================================
def _km_data(n, med, seed, censor=0.10):
    r = np.random.default_rng(seed)
    t = r.exponential(med, n)
    e = r.uniform(0, 1, n) > censor            # 10% 删失
    return t, e.astype(int)

t1, e1 = _km_data(40, 6, 1)                    # Ctrl 中位 ~6
t2, e2 = _km_data(40, 9, 2)                    # DrugA 中位 ~9
t3, e3 = _km_data(40, 18, 3)                   # DrugB 中位 ~18（明显更长）
fig, ax = plt.subplots(figsize=get_figsize("square"))
sr = prism_survival(ax, np.concatenate([t1, t2, t3]),
                    np.concatenate([e1, e2, e3]),
                    np.repeat(["Ctrl", "DrugA", "DrugB"], [40, 40, 40]),
                    xlabel="Time (d)", ylabel="Survival probability")
ax.set_title("Kaplan-Meier + log-rank (pairwise annotated)")
save_figure(fig, "demo_survival", out_dir=OUT)
print(f"[demo_survival] OK  overall p={sr['p']:.3g}, "
      f"pairwise={[(a, b, round(p, 3)) for a, b, p, _ in sr['pairwise']]}")

print(f"\n全部 5 类图 + 统计报告已生成：{OUT}")
