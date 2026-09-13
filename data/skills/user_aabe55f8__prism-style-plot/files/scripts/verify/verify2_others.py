"""验证 2:Survival / XY / Contingency / Grouped 图型"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import to_rgba

from prism_theme import (apply_prism_theme, get_figsize, prism_survival,
                         prism_xy_fit, build_stats_report, write_report,
                         save_figure, format_p, finish_axes, palette_sequence,
                         add_individual_dots)
from verify_common import report, SEED

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
os.makedirs(OUT, exist_ok=True)
fails = []

apply_prism_theme()

# ---------- 2.1 两组生存曲线 ----------
try:
    r = np.random.default_rng(SEED)
    n = 12
    time_c = r.exponential(20, n);  time_t = r.exponential(40, n)
    event_c = r.binomial(1, 0.9, n); event_t = r.binomial(1, 0.6, n)
    time = np.concatenate([time_c, time_t])
    event = np.concatenate([event_c, event_t])
    group = np.concatenate([["Control"] * n, ["Treated"] * n])
    fig, ax = plt.subplots(figsize=get_figsize("tall"))
    res = prism_survival(ax, time, event, group, show_median=True)
    assert res["p"] is not None, "log-rank p 缺失"
    save_figure(fig, "verify2_survival_2group", OUT)
    rep = build_stats_report("survival", time=time, event=event, group=group,
                             description="Survival of control vs treated mice")
    write_report("verify2_survival_2group", rep, OUT)
    report("2.1 two-group KM survival", True,
           f"log-rank {format_p(res['p'])}, medians={ {k: round(v,1) for k,v in res['median'].items()} }")
except Exception as e:
    fails.append(("2.1 survival 2g", e))
    report("2.1 two-group KM survival", False, str(e))

# ---------- 2.2 三组生存曲线(多组 log-rank) ----------
try:
    r = np.random.default_rng(SEED + 1)
    n = 10
    gs, ts, es = [], [], []
    for mu, pe in [(15, 0.9), (30, 0.7), (50, 0.5)]:
        gs += [f"G{mu}"] * n
        ts += list(r.exponential(mu, n))
        es += list(r.binomial(1, pe, n))
    fig, ax = plt.subplots(figsize=get_figsize("wide"))
    res = prism_survival(ax, np.array(ts), np.array(es), np.array(gs),
                         show_median=False, legend_loc="lower right")
    assert res["chi2"] is not None, "整体 chi2 缺失"
    save_figure(fig, "verify2_survival_3group", OUT)
    rep = build_stats_report("survival", time=np.array(ts), event=np.array(es),
                             group=np.array(gs), description="Three-group survival")
    write_report("verify2_survival_3group", rep, OUT)
    report("2.2 three-group KM survival", True,
           f"chi2={res['chi2']:.2f}, p={format_p(res['p'])}")
except Exception as e:
    fails.append(("2.2 survival 3g", e))
    report("2.2 three-group KM survival", False, str(e))

# ---------- 2.3 XY 4PL 剂量-响应 ----------
try:
    r = np.random.default_rng(SEED + 2)
    x = np.logspace(-2, 2, 12)
    true = 100 / (1 + 10 ** ((0.0 - np.log10(x)) * 1.0))
    y = true + r.normal(0, 3, len(x))
    fig, ax = plt.subplots(figsize=get_figsize("square"))
    res = prism_xy_fit(ax, x, y, model="4pl",
                       xlabel="Agonist (uM)", ylabel="Response (% max)")
    assert res["ic50"] is not None and res["ic50"] > 0, "IC50 无效"
    assert 0 <= res["r2"] <= 1, "R2 越界"
    save_figure(fig, "verify2_xy_4pl", OUT)
    report("2.2".replace("2.2", "2.3"), True,
           f"XY 4PL: IC50={res['ic50']:.3g}, R2={res['r2']:.3f}")
except Exception as e:
    fails.append(("2.3 xy 4pl", e))
    report("2.3 XY 4PL dose-response", False, str(e))

# ---------- 2.4 XY 线性回归 ----------
try:
    r = np.random.default_rng(SEED + 3)
    x = np.linspace(0, 10, 10)
    y = 2.0 * x + 1.0 + r.normal(0, 0.8, len(x))
    fig, ax = plt.subplots(figsize=get_figsize("square"))
    res = prism_xy_fit(ax, x, y, model="linear")
    assert res["ic50"] is None
    assert res["r2"] > 0.9, f"线性拟合 R2 应接近 1,实际 {res['r2']:.3f}"
    save_figure(fig, "verify2_xy_linear", OUT)
    report("2.4 XY linear regression", True, f"slope={res['popt'][0]:.2f}, R2={res['r2']:.3f}")
except Exception as e:
    fails.append(("2.4 xy linear", e))
    report("2.4 XY linear regression", False, str(e))

# ---------- 2.5 Contingency 计数柱状图 ----------
try:
    table = np.array([[40, 8], [28, 20], [12, 34]])  # 3 行(组) × 2 列(No/Yes)
    labels = ["Ctrl", "Drug-L", "Drug-H"]
    fig, ax = plt.subplots(figsize=get_figsize("wide"))
    colors = palette_sequence("okabe_ito")[:2]
    x = np.arange(len(labels)); width = 0.38
    for r_i, (row, c, lab) in enumerate(zip(table.T, colors, ["No response", "Response"])):
        ax.bar(x + (r_i - 0.5) * width, row, width=width, color=c, alpha=0.85,
               edgecolor="black", linewidth=0.75, label=lab, zorder=2)
        for xi, v in zip(x + (r_i - 0.5) * width, row):
            ax.text(xi, v + 1.0, str(int(v)), ha="center", va="bottom", fontsize=6)
    ax.set_xticks(x); ax.set_xticklabels(labels)
    ax.set_xlabel("Treatment group"); ax.set_ylabel("Number of mice")
    finish_axes(ax, data_max=float(table.max()))
    from scipy import stats as sst
    chi2, p, dof, exp = sst.chi2_contingency(table)
    ax.text(0.99, 1.02, f"\u03c7\u00b2({dof}) = {chi2:.2f}, {format_p(p)}",
            transform=ax.transAxes, ha="right", va="bottom", fontsize=6,
            bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="none", alpha=0.9))
    ax.legend(frameon=False, fontsize=7, loc="lower left",
              bbox_to_anchor=(0.01, 1.02), ncol=1)
    save_figure(fig, "verify2_contingency", OUT)
    rep = build_stats_report("contingency", table=table,
                             description="Response counts across treatments")
    write_report("verify2_contingency", rep, OUT)
    report("2.5 contingency bar + chi2", True, f"chi2={chi2:.2f}, p={format_p(p)}")
except Exception as e:
    fails.append(("2.5 contingency", e))
    report("2.5 contingency bar + chi2", False, str(e))

# ---------- 2.6 Grouped 分组柱状图(two-way) ----------
try:
    import pandas as pd
    r = np.random.default_rng(SEED + 4)
    rows = []
    for t in ["0h", "24h", "48h"]:
        for drug in ["Ctrl", "Drug"]:
            base = {"0h": 10, "24h": 20, "48h": 30}[t] + (5 if drug == "Drug" else 0)
            for _ in range(4):
                rows.append({"time": t, "drug": drug,
                             "value": base + r.normal(0, 2)})
    df = pd.DataFrame(rows)
    # 手写分组柱状图
    times = ["0h", "24h", "48h"]
    fig, ax = plt.subplots(figsize=get_figsize("wide"))
    cols = palette_sequence("okabe_ito")[:2]
    x = np.arange(len(times)); w = 0.35
    ax.set_xlim(-0.5, len(times) - 0.5)
    ax.set_ylim(0, df["value"].max() * 1.15)
    for d_i, (drug, c) in enumerate(zip(["Ctrl", "Drug"], cols)):
        means, sems, vals = [], [], []
        for t in times:
            g = df[(df["time"] == t) & (df["drug"] == drug)]["value"].values
            means.append(g.mean()); sems.append(g.std(ddof=1) / np.sqrt(len(g)))
            vals.append(g)
        ax.bar(x + (d_i - 0.5) * w, means, width=w, yerr=sems,
               facecolor=to_rgba(c, 0.55), edgecolor="black", linewidth=0.75,
               label=drug, zorder=2, capsize=3,
               error_kw=dict(zorder=6, lw=0.75, capthick=0.75))  # v2.0.37:显式 0.75 pt
        for xi, g, m in zip(x + (d_i - 0.5) * w, vals, means):
            add_individual_dots(ax, xi, g, color=c, width=w, dot_size=None)
    ax.set_xticks(x); ax.set_xticklabels(times)
    ax.set_xlabel("Time"); ax.set_ylabel("Value")
    finish_axes(ax, data_max=float(df["value"].max()))
    ax.legend(frameon=False, fontsize=7)
    save_figure(fig, "verify2_grouped_bar", OUT)
    rep = build_stats_report("twoway", df=df, formula="value ~ C(time)*C(drug)",
                             description="Two-way grouped design")
    write_report("verify2_grouped_bar", rep, OUT)
    report("2.6 grouped bar + two-way ANOVA", True)
except Exception as e:
    fails.append(("2.6 grouped", e))
    report("2.6 grouped bar + two-way ANOVA", False, str(e))

print("\n===== 第二组验证完成,失败数:", len(fails), "=====")
for name, e in fails:
    print(f"  FAIL {name}: {type(e).__name__}: {e}")
sys.exit(1 if fails else 0)
