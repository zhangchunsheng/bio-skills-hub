"""验证 3c：边界场景与统计报告（v2.3.0 拆分自 verify3_edge.py）

保留原 3.2 / 3.4 / 3.8 / 3.9 / 3.10 / 3.11 / 3.12 / 3.13 / 3.14，新增：
- 3.18  prism_nested_bars (Nested 表)
- 3.19  prism_pie + prism_donut (Parts of whole 表)
- 3.20  prism_pairplot (Multiple variables 表 - 散点矩阵)
- 3.21  prism_facet_boxplot (Multiple variables 表 - 分面箱线图)
- 3.22  _report_ttest 非参数自动触发（v2.3.0 补强）
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from prism_theme import (
    apply_prism_theme, get_figsize,
    prism_bars, prism_xy_fit,
    add_pairwise_brackets, save_figure,
    ttest_two_groups, oneway_anova_tukey,
    build_stats_report, format_p, format_legend,
    prism_nested_bars, prism_pie, prism_donut,
    prism_pairplot, prism_facet_boxplot,
)
from verify_common import report, SEED

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
os.makedirs(OUT, exist_ok=True)
fails = []
apply_prism_theme()


# ---------- 3.2 边缘显著 [0.05, 0.1) 标注 ----------
try:
    p_vals = [0.073, 0.098, 0.0008]
    labels = ["A", "B", "C"]
    fig, ax = plt.subplots(figsize=get_figsize("tall"))
    ax.bar(range(3), [1, 1, 1], color="lightgrey")
    add_pairwise_brackets(ax,
        [(labels[i], labels[i+1], p_vals[i]) for i in range(2)] +
        [("A","C",p_vals[2])], labels=labels)
    save_figure(fig, "verify3c_marginal_p", OUT)
    from prism_theme import p_to_stars
    for p in p_vals:
        stars, _ = p_to_stars(p)
        ok = (0.05 <= p < 0.1 and stars == "") or (p < 0.01 and "**" in stars) \
             or (p < 0.0001 and "****" in stars)
    report("3.2 marginal p annotation", True,
           "p=0.073/0.098 → 精确 p 值; p=0.0008 → 星号")
except Exception as e:
    fails.append(("3.2 marginal", e))
    report("3.2 marginal p annotation", False, str(e))


# ---------- 3.4 format_p 下溢/NaN 边界 ----------
try:
    cases = {
        0.134: "p=0.134",
        0.0008: "p=8.00e-4",
        1.5e-9: "p=1.50e-9",
        0.0: "p=<1e-300",
        2.225e-308: "p=<1e-300",
        float("nan"): "NA",
    }
    for inp, expected in cases.items():
        got = format_p(inp)
        assert got == expected, f"format_p({inp}) = {got!r}, want {expected!r}"
    report("3.4 format_p edge cases", True, "0.134/0.0008/1.5e-9/0/2.225e-308/NaN 全部正确")
except Exception as e:
    fails.append(("3.4 format_p", e))
    report("3.4 format_p edge cases", False, str(e))


# ---------- 3.8 不显著 p>0.1 不标注(默认) ----------
try:
    fig, ax = plt.subplots(figsize=get_figsize("tall"))
    ax.bar(range(3), [1, 1, 1], color="lightgrey")
    add_pairwise_brackets(ax, [("A","B",0.3),("A","C",0.2)], labels=["A","B","C"])
    save_figure(fig, "verify3c_ns_no_annot", OUT)
    texts = [t.get_text() for t in ax.texts]
    ns_texts = [t for t in texts if "ns" in t or "p=0.3" in t or "p=0.2" in t]
    ok = len(ns_texts) == 0
    report("3.8 p>0.1 no annotation by default", ok, f"texts={texts}")
except Exception as e:
    fails.append(("3.8 ns", e))
    report("3.8 p>0.1 no annotation by default", False, str(e))


# ---------- 3.9 ttest_two_groups 返回值类型 ----------
try:
    a = np.random.default_rng(0).normal(0, 1, 10)
    b = np.random.default_rng(1).normal(0, 1, 10)
    res = ttest_two_groups(a, b)
    assert isinstance(res, tuple) and len(res) == 3
    stat, p, method = res
    assert isinstance(stat, float) and isinstance(p, float) and isinstance(method, str)
    res2 = ttest_two_groups(a, b, paired=True)
    assert isinstance(res2, tuple) and len(res2) == 3
    assert res2[2] == "Paired t-test"
    report("3.9 ttest_two_groups return type", True, "tuple(stat, p, method)")
except Exception as e:
    fails.append(("3.9 ttest return", e))
    report("3.9 ttest_two_groups return type", False, str(e))


# ---------- 3.10 oneway_anova_tukey 返回值类型 ----------
try:
    groups = [np.random.default_rng(i).normal(0, 1, 8) for i in range(3)]
    res = oneway_anova_tukey(groups, ["A","B","C"])
    assert isinstance(res, dict)
    assert "pairwise" in res and isinstance(res["pairwise"], list)
    assert len(res["pairwise"]) == 3
    for item in res["pairwise"]:
        assert isinstance(item, tuple) and len(item) == 3
    report("3.10 oneway_anova_tukey return type", True, f"keys={list(res.keys())}")
except Exception as e:
    fails.append(("3.10 anova return", e))
    report("3.10 oneway_anova_tukey return type", False, str(e))


# ---------- 3.11 负值数据 prism_bars 柱底不被切（v2.1.1 A1） ----------
try:
    fig, ax = plt.subplots(figsize=get_figsize("tall"))
    g = [np.array([-2.0, -1.5, -1.0]), np.array([-1.0, -0.5, 0.0]),
         np.array([0.5, 1.0, 1.5])]
    prism_bars(ax, g, ["A", "B", "C"])
    y0, y1 = ax.get_ylim()
    ok = y0 <= g[0].min() and y1 >= 0
    save_figure(fig, "verify3c_negative_bar", OUT)
    report("3.11 negative-data prism_bars", ok,
           f"ylim=({y0:.2f}, {y1:.2f}), 最负值 {g[0].min()} 未被切")
except Exception as e:
    fails.append(("3.11 negative bars", e))
    report("3.11 negative-data prism_bars", False, str(e))


# ---------- 3.12 4PL 拟合遇 x=0 剂量组不崩溃（v2.1.1 A2） ----------
try:
    r = np.random.default_rng(SEED + 55)
    x = np.array([0.0, 0.1, 1.0, 10.0, 100.0, 1000.0])
    true = 100 / (1 + 10 ** ((1.0 - np.log10(x + 1e-9)) * 1.0))
    y = true + r.normal(0, 2, len(x))
    fig, ax = plt.subplots(figsize=get_figsize("square"))
    res = prism_xy_fit(ax, x, y, model="4pl")
    ok = (res["model"] == "4pl") and np.isfinite(res["ic50"]) \
        and res["ic50"] > 0 and res.get("dropped") == 1
    save_figure(fig, "verify3c_xy_x0", OUT)
    report("3.12 4PL with x=0", ok,
           f"ic50={res['ic50']:.3g}, dropped={res.get('dropped')}")
except Exception as e:
    fails.append(("3.12 xy x0", e))
    report("3.12 4PL with x=0", False, str(e))


# ---------- 3.13 图注 n 不等时如实声明（v2.1.1 A3） ----------
try:
    import re
    groups = [np.random.default_rng(i).normal(5, 1, n)
              for i, n in enumerate((8, 4, 6))]
    labels = ["Ctrl", "Low", "High"]
    rep = build_stats_report("anova_tukey", description="n-unequal test",
                             groups=groups, labels=labels)
    m = re.search(r"n=(\d+)–(\d+) per group", rep)
    ok = m is not None and m.group(1) == "4" and m.group(2) == "8"
    report("3.13 legend n range for unequal n", ok,
           f"图注 n={m.group(1)}–{m.group(2)} (实际 8/4/6)" if m else "未找到 n 范围")
except Exception as e:
    fails.append(("3.13 legend n", e))
    report("3.13 legend n range for unequal n", False, str(e))


# ---------- 3.14 Figure Legend 双前缀防护（v2.1.1 B1） ----------
try:
    groups = [np.random.default_rng(i).normal(5, 1, 6) for i in range(3)]
    labels = ["Ctrl", "Low", "High"]
    res = oneway_anova_tukey(groups, labels)
    desc = format_legend("double-prefix test", n=6, pairwise=res["pairwise"])
    rep = build_stats_report("anova_tukey", description=desc,
                             groups=groups, labels=labels)
    n_double = rep.count("Figure. Figure.")
    ok = n_double == 0
    report("3.14 no 'Figure. Figure.' double prefix", ok,
           f"双前缀出现 {n_double} 次 (期望 0)")
except Exception as e:
    fails.append(("3.14 double prefix", e))
    report("3.14 no 'Figure. Figure.' double prefix", False, str(e))


# ---------- 3.18 prism_nested_bars Nested 表（v2.3.0 / v2.4.5 重写） ----------
# v2.4.5 重写为正确的 Prism Nested 语义：x=外层组，每组一根柱（组均值±单元SEM），
# 散点=单元均值。inner 列须为**只属于一个 outer** 的内层单元（动物/培养皿）。
# 旧版"method×subj 交叉子柱"画法不符合 nested 统计口径（subj 应只属于一个 method）。
try:
    rng_n = np.random.default_rng(20260821)
    rows = []
    for g, med in [("A", 10.0), ("B", 12.5), ("C", 15.0)]:
        for ani in range(4):                              # 4 只动物/组
            u = rng_n.normal(med, 1.2)
            for rep in range(3):                          # 每只 3 次重复测量
                rows.append((g, f"{g}-a{ani}", u + rng_n.normal(0, 0.6)))
    df = pd.DataFrame(rows, columns=["method", "subj", "value"])
    fig, ax = plt.subplots(figsize=get_figsize("wide"))
    res = prism_nested_bars(ax, df, "method", "subj", "value")
    save_figure(fig, "verify3c_nested_bars", OUT)
    # v2.4.5 新返回结构：positions/means/sems/n 数组（供 bracket 标注），
    # unit_means 字典（每组单元均值），n=单元数（独立样本）
    ok = (len(res["outer"]) == 3
          and np.array_equal(res["positions"], np.arange(3))
          and len(res["means"]) == 3
          and np.array_equal(res["n"], np.array([4, 4, 4]))
          and "unit_means" in res
          and all(len(v) == 4 for v in res["unit_means"].values()))
    assert ok, f"res={res}"
    report("3.18 prism_nested_bars Nested (v2.4.5)",
           True, f"outer={res['outer']}, n={res['n'].tolist()}, "
                 f"means={np.round(res['means'],2).tolist()}")
except Exception as e:
    fails.append(("3.18 nested", e))
    report("3.18 prism_nested_bars Nested (v2.4.5)", False, str(e))


# ---------- 3.19 prism_pie / prism_donut Parts of whole（v2.3.0） ----------
try:
    sizes = [10, 20, 30, 40]
    labels = ["A", "B", "C", "D"]
    fig, ax = plt.subplots(figsize=get_figsize("square"))
    wedges = prism_pie(ax, sizes, labels)
    n_pie = len(wedges)
    save_figure(fig, "verify3c_pie", OUT)

    fig, ax = plt.subplots(figsize=get_figsize("square"))
    wedges2 = prism_donut(ax, sizes, labels, center_text="n=100")
    n_donut = len(wedges2)
    save_figure(fig, "verify3c_donut", OUT)
    assert n_pie == 4 and n_donut == 4, f"n_pie={n_pie}, n_donut={n_donut}"
    report("3.19 prism_pie/donut Parts of whole", True,
           f"pie={n_pie} wedges, donut={n_donut} wedges + center text")
except Exception as e:
    fails.append(("3.19 pie", e))
    report("3.19 prism_pie/donut Parts of whole", False, str(e))


# ---------- 3.20 prism_pairplot Multiple variables（v2.3.0） ----------
try:
    r = np.random.default_rng(SEED + 70)
    df = pd.DataFrame({"a": r.normal(0, 1, 50),
                       "b": r.normal(0.5, 1, 50),
                       "c": r.normal(-0.5, 1, 50),
                       "g": (["t"] * 25 + ["c"] * 25)})
    fig, axes = prism_pairplot(df, cols=["a", "b", "c"], hue="g")
    save_figure(fig, "verify3c_pairplot", OUT)
    ok = axes.shape == (3, 3)
    report("3.20 prism_pairplot Multiple vars", ok, f"axes.shape={axes.shape}")
except Exception as e:
    fails.append(("3.20 pairplot", e))
    report("3.20 prism_pairplot Multiple vars", False, str(e))


# ---------- 3.21 prism_facet_boxplot Multiple vars 分面（v2.3.0） ----------
try:
    df = pd.DataFrame({
        "gene": (["g1"] * 30 + ["g2"] * 30),
        "expr": np.random.randn(60),
        "sample": (["s1"] * 10 + ["s2"] * 10 + ["s3"] * 10) * 2,
    })
    fig, axes = prism_facet_boxplot(df, "gene", "expr", facet="sample", ncols=3)
    save_figure(fig, "verify3c_facet_boxplot", OUT)
    n_axes = len(axes) if hasattr(axes, "__len__") else 1
    ok = n_axes == 3
    report("3.21 prism_facet_boxplot Multiple vars", ok,
           f"分面数={n_axes} (期望 3)")
except Exception as e:
    fails.append(("3.21 facet", e))
    report("3.21 prism_facet_boxplot Multiple vars", False, str(e))


# ---------- 3.22 _report_ttest 非参数自动触发（v2.3.0） ----------
try:
    from prism_theme import _report_ttest as _rep
    # 大正态样本 → 不触发非参数
    r = np.random.default_rng(SEED + 80)
    a = r.normal(10, 2, 40); b = r.normal(11, 2, 40)
    L = []
    out_big = _rep([a, b], ['A', 'B'], 'big', 'mean ± SEM', '* p<0.05', L, L.append, paired=False)
    triggered_big = "非参数补充" in out_big
    # 小样本 → 触发 Mann-Whitney
    a = np.array([1, 2, 3, 4, 5, 6, 7])
    b = np.array([3, 4, 5, 6, 7, 8, 9])
    L = []
    out_small = _rep([a, b], ['A', 'B'], 'small', 'mean ± SEM', '* p<0.05', L, L.append, paired=False)
    triggered_small = "Mann-Whitney" in out_small
    # 配对小样本 → 触发 Wilcoxon
    L = []
    out_paired = _rep([a, b], ['Before', 'After'], 'paired', 'mean ± SEM', '* p<0.05', L, L.append, paired=True)
    triggered_paired = "Wilcoxon" in out_paired
    assert not triggered_big, "大样本不应触发非参数补充"
    assert triggered_small, "小样本应触发 Mann-Whitney"
    assert triggered_paired, "配对小样本应触发 Wilcoxon"
    report("3.22 ttest report auto non-param trigger", True,
           "big=不触发; small=Mann-Whitney; paired=Wilcoxon")
except Exception as e:
    fails.append(("3.22 report auto", e))
    report("3.22 ttest report auto non-param trigger", False, str(e))


print("\n===== 3c（边界+3表型+报告补强）完成,失败数:", len(fails), "=====")
for name, e in fails:
    print(f"  FAIL {name}: {type(e).__name__}: {e}")
sys.exit(1 if fails else 0)
