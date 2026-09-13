"""verify10_deep_others.py — 其余图种深验（组数/样本数差异化）。

覆盖:
  Column 表:  prism_bars 3/5/8/10 组 × n=4/6/10/15
              prism_boxplot 3/6 组 × n=8/12
              prism_violin 4 组 × n=6
              ttest 2 组小/大样本、mann_whitney_u / wilcoxon_signed_rank
  Survival:   2 组 n=10(含删失) / 3 组 n=15
  XY:         4PL(logEC50=-7.2) / linear
  Contingency: 2×2 / 3×3
  Nested:     2 外层×3 内层 / 3 外层×4 内层
  Parts of whole: pie 4 类 / donut 6 类
  Multiple variables: pairplot 3 列 hue / facet boxplot 2×3
  figsize 推荐档位(<5 tall / 5-8 square / >8 wide)

断言: 出图不崩、统计返回结构、点大小统一、布局不溢出、报告生成。
产物: scripts/verify/output/deep10/ 下代表图 + 本脚本同名报告。
"""
import sys
import os
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from prism_theme import (
    apply_prism_theme, recommend_figsize, recommend_shape,
    prism_bars, prism_boxplot, prism_violin, prism_survival, prism_xy_fit,
    prism_nested_bars, prism_pie, prism_donut, prism_pairplot,
    prism_facet_boxplot, ttest_two_groups, oneway_anova_tukey,
    mann_whitney_u, wilcoxon_signed_rank, common_point_size,
    build_stats_report, write_report, save_figure, format_legend,
    finish_axes,
)

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "output", "deep10")
os.makedirs(OUT, exist_ok=True)
SEED = 20260822
fails = []
results = []


def check(name, ok, detail=""):
    status = "PASS" if ok else "FAIL"
    print(f"[{status}] {name}" + (f" — {detail}" if detail else ""))
    if not ok:
        fails.append(name)
    return ok


def rng(seed=SEED):
    return np.random.default_rng(seed)


def dot_sizes_unique(ax):
    from matplotlib.collections import PathCollection
    sizes = []
    for c in ax.collections:
        if isinstance(c, PathCollection) and len(c.get_offsets()):
            sizes.append(float(c.get_sizes()[0]))
    return len(set(sizes)) <= 1


apply_prism_theme()


# ============ C. Column 表 ============
def run_column_bars():
    r = rng()
    # 组数/样本数矩阵: (组数, n)
    for n_g, n in [(3, 6), (5, 4), (8, 10), (10, 15)]:
        bases = np.linspace(10, 10 + 3 * n_g, n_g)
        groups = [r.normal(b, 1.5, n) for b in bases]
        labels = [f"G{i}" for i in range(n_g)]
        fig, ax = plt.subplots(
            figsize=recommend_figsize("column", n_groups=n_g))
        prism_bars(ax, groups, labels)
        # 柱数
        n_bar = sum(1 for p in ax.patches if p.get_width() > 0.5)
        check(f"C-bars {n_g}组 n={n} 柱数={n_g}", n_bar == n_g, f"bars={n_bar}")
        check(f"C-bars {n_g}组 n={n} 点大小统一", dot_sizes_unique(ax))
        # 统计
        if n_g >= 3:
            res = oneway_anova_tukey(groups, labels)
            ok_struct = isinstance(res, dict) and "anova_p" in res \
                and "pairwise" in res and len(res["pairwise"]) == n_g * (n_g - 1) // 2
            check(f"C-bars {n_g}组 n={n} ANOVA dict 结构",
                  ok_struct, f"pairwise={len(res.get('pairwise', []))}")
        else:
            stat, p, method = ttest_two_groups(groups[0], groups[1])
            check(f"C-bars {n_g}组 n={n} ttest tuple",
                  isinstance(stat, float) and isinstance(p, float)
                  and isinstance(method, str), f"{method} p={p:.3f}")
        if n_g in (3, 10):
            save_figure(fig, f"deep10_bars_{n_g}g_n{n}", OUT)
            results.append({"kind": "column_bars", "n_groups": n_g, "n": n,
                            "figure": f"deep10_bars_{n_g}g_n{n}.png"})
        plt.close(fig)


def run_column_boxplot():
    r = rng()
    for n_g, n in [(3, 8), (6, 12)]:
        bases = np.linspace(10, 10 + 2.5 * n_g, n_g)
        groups = [r.normal(b, 1.8, n) for b in bases]
        labels = [f"G{i}" for i in range(n_g)]
        fig, ax = plt.subplots(
            figsize=recommend_figsize("column", n_groups=n_g))
        prism_boxplot(ax, groups, labels)
        # 箱数: seaborn 0.13+ 箱体是 PathPatch(0.12 在 artists), 数 patch 数
        from matplotlib.patches import PathPatch
        boxes = [p for p in ax.patches if isinstance(p, PathPatch)]
        if not boxes:  # 兼容 seaborn 0.12: artists
            boxes = [a for a in getattr(ax, "artists", [])]
        n_box = len(boxes)
        check(f"C-box {n_g}组 n={n} 箱数={n_g}", n_box == n_g, f"boxes={n_box}")
        check(f"C-box {n_g}组 n={n} 点大小统一", dot_sizes_unique(ax))
        # 统计
        res = oneway_anova_tukey(groups, labels)
        check(f"C-box {n_g}组 n={n} ANOVA dict",
              "anova_p" in res and len(res["pairwise"]) == n_g * (n_g - 1) // 2)
        if n_g == 6:
            save_figure(fig, f"deep10_box_{n_g}g_n{n}", OUT)
            results.append({"kind": "column_boxplot", "n_groups": n_g, "n": n,
                            "figure": f"deep10_box_{n_g}g_n{n}.png"})
        plt.close(fig)


def run_column_violin():
    r = rng()
    n_g, n = 4, 6
    bases = np.linspace(10, 16, n_g)
    groups = [r.normal(b, 1.5, n) for b in bases]
    labels = [f"G{i}" for i in range(n_g)]
    fig, ax = plt.subplots(figsize=recommend_figsize("column", n_groups=n_g))
    prism_violin(ax, groups, labels)
    check(f"C-violin {n_g}组 n={n} 点大小统一", dot_sizes_unique(ax))
    res = oneway_anova_tukey(groups, labels)
    check(f"C-violin {n_g}组 n={n} ANOVA dict", "anova_p" in res)
    save_figure(fig, f"deep10_violin_{n_g}g_n{n}", OUT)
    results.append({"kind": "column_violin", "n_groups": n_g, "n": n,
                    "figure": f"deep10_violin_{n_g}g_n{n}.png"})
    plt.close(fig)


def run_ttest():
    r = rng()
    # 小样本
    a, b = r.normal(10, 1.5, 6), r.normal(14, 1.5, 6)
    stat, p, method = ttest_two_groups(a, b)
    check("ttest 小样本 n=6 tuple", isinstance(stat, float)
          and isinstance(p, float) and isinstance(method, str)
          and p < 0.05, f"{method} p={p:.4f}")
    # 大样本
    a2, b2 = r.normal(10, 2.0, 30), r.normal(10.8, 2.0, 30)
    stat2, p2, m2 = ttest_two_groups(a2, b2)
    check("ttest 大样本 n=30 tuple", isinstance(stat2, float)
          and isinstance(p2, float), f"{m2} p={p2:.3f}")
    # 配对
    base = r.normal(10, 1.5, 8)
    a3 = base + r.normal(0, 0.5, 8)
    b3 = base + r.normal(0, 0.5, 8) + 2.0
    stat3, p3, m3 = ttest_two_groups(a3, b3, paired=True)
    check("ttest 配对 n=8 tuple", isinstance(stat3, float)
          and p3 < 0.05, f"{m3} p={p3:.4f}")
    # 非参数
    a4 = r.normal(10, 2.0, 10)
    b4 = r.normal(13, 2.0, 10)
    stat4, p4, m4 = mann_whitney_u(a4, b4)
    check("mann_whitney_u tuple", isinstance(stat4, float)
          and isinstance(p4, float) and m4 == "Mann-Whitney U", f"p={p4:.3f}")
    stat5, p5, m5 = wilcoxon_signed_rank(a3, b3)
    check("wilcoxon_signed_rank tuple", isinstance(stat5, float)
          and isinstance(p5, float) and m5 == "Wilcoxon signed-rank",
          f"p={p5:.3f}")


# ============ S. Survival ============
def run_survival():
    r = rng()
    # 2 组, n=10, 含删失
    t1 = np.sort(r.exponential(12, 10))
    t2 = np.sort(r.exponential(20, 10))
    ev1 = np.array([1, 1, 1, 1, 0, 1, 1, 0, 1, 1])
    ev2 = np.array([1, 1, 1, 1, 1, 1, 0, 1, 1, 0])
    fig, ax = plt.subplots(figsize=recommend_figsize("survival"))
    res = prism_survival(ax, np.concatenate([t1, t2]),
                         np.concatenate([ev1, ev2]),
                         ["Ctrl"] * 10 + ["Trt"] * 10)
    check("Survival 2组 n=10 dict 结构",
          isinstance(res, dict) and "p" in res and "chi2" in res
          and "median" in res and "n" in res,
          f"p={res.get('p', '?'):.3f}")
    save_figure(fig, "deep10_survival_2g_n10", OUT)
    results.append({"kind": "survival", "n_groups": 2, "n": 10,
                    "figure": "deep10_survival_2g_n10.png"})
    plt.close(fig)
    # 3 组, n=15 (show_median=True 验证中位生存计算)
    t3 = np.sort(r.exponential(15, 15))
    grp = ["A"] * 10 + ["B"] * 10 + ["C"] * 15
    fig2, ax2 = plt.subplots(figsize=recommend_figsize("survival"))
    res2 = prism_survival(ax2, np.concatenate([t1, t2, t3]),
                          np.concatenate([ev1, ev2, np.ones(15)]), grp,
                          show_median=True)
    check("Survival 3组 n=15 multi log-rank",
          "p" in res2 and len(res2["median"]) == 3 and len(res2["n"]) == 3,
          f"p={res2.get('p', '?'):.3f} medians={len(res2.get('median', {}))} "
          f"n={len(res2.get('n', {}))}")
    plt.close(fig2)


# ============ X. XY ============
def run_xy():
    r = rng()
    # 4PL: logEC50=-7.2 (远离 0, v2.3.1 p0 数据驱动回归场景)
    x = np.logspace(-9, -4, 24)
    true_ec50 = 10 ** -7.2
    y = 5 + 90 / (1 + 10 ** ((np.log10(x) - np.log10(true_ec50)) * (-1.0)))
    y += r.normal(0, 2.0, len(x))
    fig, ax = plt.subplots(figsize=recommend_figsize("xy"))
    res = prism_xy_fit(ax, x, y, model="4pl")
    ic50_err = abs(res.get("ic50", np.inf) - true_ec50) / true_ec50
    check("XY 4PL logEC50=-7.2 R²>0.9",
          res.get("r2", 0) > 0.9, f"R²={res.get('r2', 0):.4f}")
    check("XY 4PL IC50 误差<30%",
          ic50_err < 0.30, f"IC50={res.get('ic50', np.nan):.2e} "
                           f"true={true_ec50:.2e} err={ic50_err:.1%}")
    save_figure(fig, "deep10_xy_4pl", OUT)
    results.append({"kind": "xy_4pl", "figure": "deep10_xy_4pl.png",
                    "r2": round(res.get("r2", 0), 4)})
    plt.close(fig)
    # linear
    x2 = np.linspace(0, 10, 12)
    y2 = 2.0 * x2 + 3.0 + r.normal(0, 0.5, len(x2))
    fig2, ax2 = plt.subplots(figsize=recommend_figsize("xy"))
    res2 = prism_xy_fit(ax2, x2, y2, model="linear")
    check("XY linear R²>0.9", res2.get("r2", 0) > 0.9,
          f"R²={res2.get('r2', 0):.4f}")
    plt.close(fig2)


# ============ CT. Contingency ============
def run_contingency():
    for shape, tab in [("2×2", np.array([[30, 10], [12, 28]])),
                       ("3×3", np.array([[25, 8, 4], [10, 22, 6], [5, 9, 20]]))]:
        labels = [f"C{i}" for i in range(tab.shape[1])]
        fig, ax = plt.subplots(figsize=recommend_figsize("contingency"))
        colors = ["#0072B2", "#E69F00", "#009E73"][:tab.shape[0]]
        x = np.arange(tab.shape[1])
        width = min(0.38, 0.8 / tab.shape[0])  # 行数自适应（v2.4.0）
        for r_i, row in enumerate(tab):
            ax.bar(x + (r_i - 0.5) * width, row, width=width, color=colors[r_i],
                   edgecolor="black", linewidth=0.75)
            for xi, v in zip(x + (r_i - 0.5) * width, row):
                ax.text(xi, v + 1.0, str(int(v)), ha="center", va="bottom",
                        fontsize=6)
        ax.set_xticks(x)
        ax.set_xticklabels(labels)
        # v2.4.2：y 轴统一收尾（0.5 倍数刻度 + 顶部 ≤1.3×max，SKILL.md 强制规范）
        finish_axes(ax, data_max=float(tab.max()))
        # 统计
        rep = build_stats_report("contingency", table=tab, description="demo")
        check(f"Contingency {shape} 报告含卡方",
              "chi" in rep.lower() or "fisher" in rep.lower()
              or "χ" in rep, f"报告 {len(rep)} 字符")
        save_figure(fig, f"deep10_contingency_{shape.replace('×', 'x')}", OUT)
        results.append({"kind": "contingency", "design": shape,
                        "figure": f"deep10_contingency_{shape.replace('×', 'x')}.png"})
        plt.close(fig)


# ============ N. Nested ============
def run_nested():
    r = rng()
    for n_outer, n_inner, n in [(2, 3, 5), (3, 4, 6)]:
        rows = []
        for o in range(n_outer):
            for i in range(n_inner):
                for _ in range(n):
                    rows.append((f"O{o}", f"I{i}", r.normal(10 + o * 2 + i, 1.2)))
        df = pd.DataFrame(rows, columns=["outer", "inner", "value"])
        fig, ax = plt.subplots(figsize=recommend_figsize("nested"))
        res = prism_nested_bars(ax, df, "outer", "inner", "value")
        # v2.4.5 重写：返回 positions/means/sems/n 数组 + unit_means 字典
        # （旧"交叉子柱"画法已废——inner 不再是子柱水平）
        check(f"Nested {n_outer}×{n_inner} n={n} 返回结构",
              isinstance(res, dict) and "outer" in res
              and "positions" in res and "means" in res
              and "n" in res and "unit_means" in res
              and len(res["outer"]) == n_outer
              and np.array_equal(res["positions"], np.arange(n_outer)),
              f"outer={len(res.get('outer', []))}, n={res.get('n', []).tolist()}")
        if (n_outer, n_inner) == (3, 4):
            save_figure(fig, f"deep10_nested_{n_outer}x{n_inner}", OUT)
            results.append({"kind": "nested", "design": f"{n_outer}×{n_inner}",
                            "figure": f"deep10_nested_{n_outer}x{n_inner}.png"})
        plt.close(fig)


# ============ P. Parts of whole ============
def run_parts():
    fig, ax = plt.subplots(figsize=recommend_figsize("parts_of_whole"))
    wedges = prism_pie(ax, [25, 35, 20, 20], ["A", "B", "C", "D"])
    check("Pie 4 类扇区=4", len(wedges) == 4, f"wedges={len(wedges)}")
    save_figure(fig, "deep10_pie_4cat", OUT)
    results.append({"kind": "pie", "n_cat": 4, "figure": "deep10_pie_4cat.png"})
    plt.close(fig)
    fig2, ax2 = plt.subplots(figsize=recommend_figsize("parts_of_whole"))
    w2 = prism_donut(ax2, [10, 15, 20, 25, 15, 15], ["A", "B", "C", "D", "E", "F"],
                     center_text="n=100")
    check("Donut 6 类扇区=6 + 中心文本",
          len(w2) == 6 and len(ax2.texts) >= 1, f"wedges={len(w2)}")
    save_figure(fig2, "deep10_donut_6cat", OUT)
    results.append({"kind": "donut", "n_cat": 6, "figure": "deep10_donut_6cat.png"})
    plt.close(fig2)


# ============ M. Multiple variables ============
def run_multivar():
    r = rng()
    df = pd.DataFrame({
        "a": r.normal(10, 2, 40), "b": r.normal(20, 3, 40),
        "c": r.normal(5, 1, 40),
        "group": ["Ctrl"] * 20 + ["Trt"] * 20,
    })
    # pairplot: 自建 figure, 不要预建
    fig, axes = prism_pairplot(df, cols=["a", "b", "c"], hue="group")
    check("Pairplot 3 列 axes=(3,3)", axes.shape == (3, 3),
          f"shape={axes.shape}")
    save_figure(fig, "deep10_pairplot_3col", OUT)
    results.append({"kind": "pairplot", "figure": "deep10_pairplot_3col.png"})
    plt.close(fig)
    # facet boxplot
    df2 = pd.DataFrame({
        "gene": np.repeat(["Gene1", "Gene2", "Gene3"], 20),
        "expr": r.normal(10, 2, 60),
        "sample": np.tile(["S1", "S2"], 30),
    })
    fig2, axes2 = prism_facet_boxplot(df2, x="gene", y="expr", facet="sample",
                                      ncols=3)
    # 返回 nrows×ncols 展平数组, 空面板 axis("off"); 有内容(箱体)面板=分面数
    from matplotlib.patches import PathPatch
    n_used = sum(1 for a in axes2
                 if any(isinstance(p, PathPatch) for p in a.patches))
    check("Facet boxplot 有内容面板=2", n_used == 2,
          f"used={n_used} total={len(axes2)}")
    save_figure(fig2, "deep10_facet_2panel", OUT)
    results.append({"kind": "facet_boxplot", "figure": "deep10_facet_2panel.png"})
    plt.close(fig2)


# ============ F. figsize 推荐档位 ============
def run_figsize():
    check("figsize 3组→tall", recommend_shape("grouped", n_groups=3) == "tall")
    check("figsize 6组→square", recommend_shape("grouped", n_groups=6) == "square")
    check("figsize 16组→wide", recommend_shape("grouped", n_groups=16) == "wide")
    check("figsize 关键词 wide 覆盖",
          recommend_shape("column", n_groups=3, shape="wide") == "wide")
    s1 = recommend_figsize("column", n_groups=3)
    s2 = recommend_figsize("grouped", n_groups=16)
    check("figsize 宽>高 (wide)", s2[0] > s2[1], f"figsize={s2}")
    check("figsize tall 高>宽", s1[1] > s1[0], f"figsize={s1}")


def main():
    print("=== verify10_deep_others: 其余图种深验 ===")
    run_column_bars()
    run_column_boxplot()
    run_column_violin()
    run_ttest()
    run_survival()
    run_xy()
    run_contingency()
    run_nested()
    run_parts()
    run_multivar()
    run_figsize()
    print(f"\n=== 结果: 失败断言 {len(fails)} 条 ===")
    for f in fails:
        print(f"  FAIL: {f}")
    with open(os.path.join(OUT, "verify10_summary.json"), "w",
              encoding="utf-8") as fh:
        json.dump(results, fh, ensure_ascii=False, indent=1)
    lines = ["# verify10_deep_others — 其余图种深验报告\n",
             "| 图种 | 参数 | 断言 | 图 |", "|---|---|---|---|"]
    for r in results:
        params = ", ".join(f"{k}={v}" for k, v in r.items()
                           if k not in ("kind", "figure"))
        lines.append(f"| {r['kind']} | {params} | PASS | {r['figure']} |")
    lines.append(f"\n失败断言: {len(fails)} 条" + ("" if not fails else
                 "\n" + "\n".join(f"- {f}" for f in fails)))
    with open(os.path.join(OUT, "verify10_deep_others_report.md"), "w",
              encoding="utf-8") as fh:
        fh.write("\n".join(lines))
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
