"""验证 1:Column 表三大图型 — prism_bars / prism_boxplot / prism_violin + 统计"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from prism_theme import (apply_prism_theme, get_figsize, prism_bars,
                         prism_boxplot, prism_violin, ttest_two_groups,
                         oneway_anova_tukey, add_pairwise_brackets,
                         build_stats_report, write_report, save_figure,
                         format_legend, format_p)
from verify_common import make_groups, report, SEED

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
os.makedirs(OUT, exist_ok=True)
fails = []

apply_prism_theme()

# ---------- 1.1 三组柱状图(ANOVA+Tukey) ----------
try:
    groups = make_groups(n_per_group=6, n_groups=3, base=(10, 12, 16), sd=1.5)
    labels = ["Control", "Low", "High"]
    fig, ax = plt.subplots(figsize=get_figsize("tall"))
    prism_bars(ax, groups, labels)
    res = oneway_anova_tukey(groups, labels)
    assert isinstance(res, dict) and "pairwise" in res, "oneway 返回类型错误"
    assert len(res["pairwise"]) == 3, "3 组应有 3 对比较"
    add_pairwise_brackets(ax, res["pairwise"], labels=labels)
    save_figure(fig, "verify1_threegroup_bar", OUT)
    # 报告
    rep = build_stats_report("anova_tukey", description="TNF-a secretion",
                             groups=groups, labels=labels)
    write_report("verify1_threegroup_bar", rep, OUT)
    # 检查所有 p 值格式
    for a, b, p in res["pairwise"]:
        fs = format_p(p)
        assert "p=" in fs and "e-" not in fs.replace("e-", "") or fs.count("e-") <= 1
    ok = report("1.1 three-group prism_bars + ANOVA/Tukey", True,
                f"anova_p={format_p(res['anova_p'])}, "
                + "; ".join(f"{a}-{b}:{format_p(p)}" for a, b, p in res["pairwise"]))
except Exception as e:
    fails.append(("1.1 prism_bars+ANOVA", e))
    report("1.1 three-group prism_bars + ANOVA/Tukey", False, str(e))

# ---------- 1.2 两组柱状图(ttest) ----------
try:
    a = np.random.default_rng(SEED).normal(10, 1.5, 8)
    b = np.random.default_rng(SEED + 1).normal(14, 1.5, 8)
    fig, ax = plt.subplots(figsize=get_figsize("tall"))
    prism_bars(ax, [a, b], ["Ctrl", "Treated"])
    stat, p, method = ttest_two_groups(a, b)
    assert isinstance(stat, float) and isinstance(p, float), "ttest 返回类型错误"
    add_pairwise_brackets(ax, [("Ctrl", "Treated", p)], labels=["Ctrl", "Treated"])
    save_figure(fig, "verify1_twogroup_bar", OUT)
    rep = build_stats_report("ttest", description="Two-group comparison",
                             groups=[a, b], labels=["Ctrl", "Treated"])
    write_report("verify1_twogroup_bar", rep, OUT)
    report("1.2 two-group prism_bars + t-test", True,
           f"method={method}, p={format_p(p)}")
except Exception as e:
    fails.append(("1.2 ttest", e))
    report("1.2 two-group prism_bars + t-test", False, str(e))

# ---------- 1.3 三组箱线图 ----------
try:
    groups = make_groups(n_per_group=8, n_groups=3, base=(10, 12, 16), sd=2.0)
    labels = ["Control", "Low", "High"]
    fig, ax = plt.subplots(figsize=get_figsize("tall"))
    prism_boxplot(ax, groups, labels)
    res = oneway_anova_tukey(groups, labels)
    add_pairwise_brackets(ax, res["pairwise"], labels=labels)
    save_figure(fig, "verify1_threegroup_box", OUT)
    rep = build_stats_report("anova_tukey", description="Boxplot test",
                             groups=groups, labels=labels,
                             error_type="median (IQR) shown as box; individual points overlaid")
    write_report("verify1_threegroup_box", rep, OUT)
    report("1.3 three-group prism_boxplot", True)
except Exception as e:
    fails.append(("1.3 boxplot", e))
    report("1.3 three-group prism_boxplot", False, str(e))

# ---------- 1.4 三组小提琴图 ----------
try:
    groups = make_groups(n_per_group=8, n_groups=3, base=(10, 12, 16), sd=2.0)
    labels = ["Control", "Low", "High"]
    fig, ax = plt.subplots(figsize=get_figsize("tall"))
    prism_violin(ax, groups, labels)
    res = oneway_anova_tukey(groups, labels)
    add_pairwise_brackets(ax, res["pairwise"], labels=labels)
    save_figure(fig, "verify1_threegroup_violin", OUT)
    report("1.4 three-group prism_violin", True)
except Exception as e:
    fails.append(("1.4 violin", e))
    report("1.4 three-group prism_violin", False, str(e))

# ---------- 1.5 配对 t 检验报告 ----------
try:
    before = np.random.default_rng(SEED).normal(100, 10, 10)
    after = before + np.random.default_rng(SEED + 2).normal(8, 5, 10)
    fig, ax = plt.subplots(figsize=get_figsize("tall"))
    prism_bars(ax, [before, after], ["Before", "After"])
    stat, p, method = ttest_two_groups(before, after, paired=True)
    add_pairwise_brackets(ax, [("Before", "After", p)], labels=["Before", "After"])
    save_figure(fig, "verify1_paired_bar", OUT)
    rep = build_stats_report("ttest", description="Paired before-after",
                             groups=[before, after], labels=["Before", "After"],
                             paired=True)
    write_report("verify1_paired_bar", rep, OUT)
    report("1.5 paired t-test", True, f"method={method}, p={format_p(p)}")
except Exception as e:
    fails.append(("1.5 paired t", e))
    report("1.5 paired t-test", False, str(e))

print("\n===== Column 表验证完成,失败数:", len(fails), "=====")
for name, e in fails:
    print(f"  FAIL {name}: {type(e).__name__}: {e}")
sys.exit(1 if fails else 0)
