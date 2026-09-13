"""verify9_deep_matrix.py — 析因分析(Grouped 表)组数矩阵深验。

针对 v2.3.4~v2.3.8 系列修复的回归验证,覆盖 18 种析因设计:
  组数组合: 2×2 / 2×3 / 3×2 / 2×4 / 4×2 / 3×3 / 3×4 / 4×3 / 4×4 /
           2×5 / 2×6 / 6×2 (A 水平 × B 水平, 含对称/非对称/奇偶)
  每格样本: n = 3(极小) / 4 / 5 / 6 / 8 / 10 / 12 / 20(大样本)
  交互形态: 交互显著(→简单效应) 与 纯加性(→主效应) 两类
  特殊场景: 负值数据(ylim 自适应)

每设计断言(v2.3.4~v2.3.8 修复点):
  A1  prism_grouped_bars 出图不崩, positions/means/sems/n 映射完整
  A2  子柱总宽 ≤ 0.85×间距 (v2.3.7 common_bar_width 防重叠)
  A3  全图散点大小唯一 (v2.3.6 common_point_size 统一)
  A4  legend 颜色 handle 数 = 组数, 且 handle 为不透明 Patch (v2.3.8)
  A5  无 1×1 可见锚点方块残留在数据区 (v2.3.8)
  A6  twoway_posthoc 分支类型 == 设计预期 (交互显著/不显著)
  A7  比较键方向与数据水平顺序一致, 键合法可匹配 (v2.3.4 核心回归)
  A8  图上显著性标注不丢: 实际 bracket 标注数 == p<0.1 的简单效应数
      (v2.3.4 修复前 2×3 图上 6 个组内比较只画 2 个)

产物: scripts/verify/output/deep9/ 下代表性设计图 + 本脚本同名报告。
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
    apply_prism_theme, recommend_figsize, prism_grouped_bars,
    twoway_posthoc, add_pairwise_brackets, common_bar_width,
    common_point_size, save_figure,
)

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "output", "deep9")
os.makedirs(OUT, exist_ok=True)

SEED_BASE = 20260821
fails = []
results = []  # 每设计一条 {id, design, n, expect, p_inter, ...}


def check(name, ok, detail=""):
    status = "PASS" if ok else "FAIL"
    print(f"[{status}] {name}" + (f" — {detail}" if detail else ""))
    if not ok:
        fails.append(name)
    return ok


def make_factorial(a_levels, b_levels, n, interaction=True, seed=0,
                   noise=1.5, base0=10.0):
    """生成 Grouped 表长格式数据。

    interaction=True  → 交互项 4.0*ai*bi 制造显著交互(简单效应分支;
                       2×2 时 df_inter=1, 系数必须够大才能显著)
    interaction=False → 纯加性模型(主效应分支)
    """
    r = np.random.default_rng(seed)
    a_eff = np.linspace(0, 4.0, len(a_levels))
    rows = []
    for ai, a in enumerate(a_levels):
        for bi, b in enumerate(b_levels):
            base = base0 + a_eff[ai] + 2.0 * bi
            if interaction:
                base += 4.0 * ai * bi
            for v in r.normal(base, noise, n):
                rows.append((a, b, v))
    return pd.DataFrame(rows, columns=["A", "B", "value"])


def parse_comp(desc):
    """'A=0h: Ctrl vs Drug' → ('A', '0h', 'Ctrl', 'Drug')
    'A: 0h vs 24h' (主效应, 无 =) → ('A', None, '0h', '24h')
    """
    head, _, tail = desc.partition(": ")
    if "=" in head:
        fac, _, lv = head.partition("=")
    else:
        fac, lv = head, None
    g1, _, g2 = tail.partition(" vs ")
    return fac, lv, g1, g2


def draw_all_comparisons(ax, mapping, comparisons):
    """把 twoway_posthoc 返回的**简单效应**比较画成 bracket。

    这是 v2.3.4 修复的核心调用路径: 键方向必须与数据水平顺序一致,
    否则 desc 解析出的组名在 positions 中找不到 → bracket 丢失。
    主效应比较(lv=None)跨多个 x 位置, 不在分组柱状图上画 bracket。
    """
    drawn = []
    for desc, p, _ in comparisons:
        fac, lv, g1, g2 = parse_comp(desc)
        if lv is None:
            continue  # 主效应比较不画
        try:
            if fac == "A":
                xi = mapping["x_levels"].index(lv)
                x1 = float(mapping["positions"][g1][xi])
                x2 = float(mapping["positions"][g2][xi])
            else:
                bi = mapping["group_levels"].index(lv)
                a1i = mapping["x_levels"].index(g1)
                a2i = mapping["x_levels"].index(g2)
                x1 = float(mapping["positions"][lv][a1i])
                x2 = float(mapping["positions"][lv][a2i])
        except (KeyError, ValueError) as e:
            # 键不可匹配 = v2.3.4 修复前的丢 bracket 场景
            return drawn, f"KEY_UNMATCHED:{e}"
        drawn.append((x1, x2, p))
    if drawn:
        add_pairwise_brackets(ax, drawn)
    return drawn, "ok"


# ---- 18 种设计 ----
DESIGNS = [
    # id, A 水平数, B 水平数, n/格, 交互, 说明
    ("G01", 2, 2, 6, True,  "2×2 对称, 交互显著"),
    ("G02", 2, 3, 5, True,  "2×3 非对称, 交互显著 (v2.3.4 用户 bug 场景)"),
    ("G03", 3, 2, 8, True,  "3×2 非对称, 交互显著"),
    ("G04", 2, 4, 6, True,  "2×4, 交互显著"),
    ("G05", 4, 2, 4, True,  "4×2 小样本, 交互显著"),
    ("G06", 3, 3, 5, True,  "3×3 对称, 交互显著"),
    ("G07", 3, 4, 6, True,  "3×4, 交互显著"),
    ("G08", 4, 3, 5, True,  "4×3, 交互显著"),
    ("G09", 4, 4, 3, True,  "4×4 最大格子, n=3 极小样本, 交互显著"),
    ("G10", 2, 5, 6, False, "2×5, 纯加性 → 主效应"),
    ("G11", 2, 2, 12, False, "2×2 大样本, 纯加性 → 主效应"),
    ("G12", 3, 3, 20, False, "3×3 大样本, 纯加性 → 主效应"),
    ("G13", 2, 3, 3, True,  "2×3 n=3 极小样本, 交互显著"),
    ("G14", 3, 4, 10, False, "3×4 大样本, 纯加性 → 主效应"),
    ("G15", 2, 6, 4, True,  "2×6 子柱 6 根, 交互显著"),
    ("G16", 6, 2, 5, True,  "6×2 横轴 6 水平, 交互显著"),
    ("G17", 4, 4, 8, False, "4×4, 纯加性 → 主效应"),
    ("G18", 2, 2, 6, True,  "2×2 负值数据, 交互显著 (ylim 自适应)"),
]

SAVE = {"G02", "G07", "G09", "G15", "G17", "G18"}  # 代表性设计出图
apply_prism_theme()


def run_one(gid, n_a, n_b, n, interaction, note):
    a_levels = [f"T{i}" for i in range(n_a)]
    b_levels = [f"G{i}" for i in range(n_b)]
    df = make_factorial(a_levels, b_levels, n,
                        interaction=interaction,
                        seed=SEED_BASE + int(gid[1:]),
                        base0=(-5.0 if gid == "G18" else 10.0))
    r = {"id": gid, "design": f"{n_a}×{n_b}", "n": n,
         "expect": "simple_effects" if interaction else "main_effects",
         "note": note}

    # ---- 画图 ----
    n_groups = n_a * n_b
    fig, ax = plt.subplots(
        figsize=recommend_figsize("grouped", n_groups=n_groups))
    try:
        mapping = prism_grouped_bars(ax, df, "A", "B", "value")
        r["plot_ok"] = True
    except Exception as e:
        r["plot_ok"] = False
        r["plot_err"] = str(e)
        check(f"{gid} {n_a}×{n_b} n={n} A1 出图不崩", False, str(e))
        plt.close(fig)
        return r
    check(f"{gid} {n_a}×{n_b} n={n} A1 出图不崩/映射完整",
          all(k in mapping for k in ("x_levels", "group_levels", "positions",
                                     "means", "sems", "n"))
          and len(mapping["x_levels"]) == n_a
          and len(mapping["group_levels"]) == n_b,
          f"x={len(mapping['x_levels'])} g={len(mapping['group_levels'])}")

    # ---- A2 子柱总宽 ≤ 0.85 (v2.3.7) ----
    from matplotlib.patches import Rectangle
    widths = [p.get_width() for p in ax.patches if isinstance(p, Rectangle)
              and p.get_width() > 0.01 and p.get_width() < 0.9]
    if widths:
        w = np.median(widths)
        total = n_b * w + (n_b - 1) * 0.15 * w
        gap = 0.15 * w
        check(f"{gid} A2 子柱总宽≤0.85 (w={w:.3f})",
              abs(np.max(widths) - np.min(widths)) < 1e-9
              and total <= 0.85 + 1e-9,
              f"w={w:.3f} total={total:.3f} ≤0.85")
    else:
        check(f"{gid} A2 子柱总宽≤0.85", False, "未找到柱 patch")

    # ---- A3 点大小全图唯一 (v2.3.6) ----
    from matplotlib.collections import PathCollection
    sizes = []
    for c in ax.collections:
        if isinstance(c, PathCollection) and len(c.get_offsets()):
            sizes.append(float(c.get_sizes()[0]))
    check(f"{gid} A3 散点大小全图唯一", len(set(sizes)) == 1,
          f"size={set(sizes)} n_coll={len(sizes)}")

    # ---- A4 legend 颜色 handle 数 = 组数 (v2.3.8) ----
    leg = ax.get_legend()
    if leg is None:
        check(f"{gid} A4 legend 颜色 handle", False, "无 legend")
    else:
        handles = list(leg.legend_handles) or list(leg.get_children())
        from matplotlib.patches import Patch as MPatch
        ok_handle = all(isinstance(h, MPatch) for h in handles)
        alphas = []
        for h in handles:
            try:
                alphas.append(matplotlib.colors.to_rgba(h.get_facecolor())[3])
            except Exception:
                alphas.append(-1)
        check(f"{gid} A4 legend 颜色 handle 数={n_b}",
              ok_handle and len(handles) == n_b and all(a == 1.0 for a in alphas),
              f"handles={len(handles)} alphas={set(alphas)}")

    # ---- A5 无 1×1 可见锚点方块 (v2.3.8) ----
    anchors = [p for p in ax.patches if isinstance(p, Rectangle)
               and p.get_width() >= 0.9 and p.get_height() >= 0.9
               and p.get_visible()]
    check(f"{gid} A5 无 1×1 可见锚点方块", len(anchors) == 0, f"anchors={len(anchors)}")

    # ---- A6/A7/A8 统计 + 标注 ----
    try:
        ph = twoway_posthoc(df, "value ~ C(A)*C(B)")
        r["p_inter"] = round(float(ph["interaction_p"]), 6)
        r["posthoc_type"] = ph["type"]
        r["n_comps"] = len(ph["comparisons"])
    except Exception as e:
        r["stats_err"] = str(e)
        check(f"{gid} A6 twoway_posthoc 运行", False, str(e))
        plt.close(fig)
        return r

    check(f"{gid} A6 分支类型==设计预期",
          ph["type"] == r["expect"],
          f"p_inter={r['p_inter']} got={ph['type']} expect={r['expect']}")

    # ---- A7 键方向 + 合法性 (v2.3.4) ----
    a_order = {lv: i for i, lv in enumerate(
        dict.fromkeys(df["A"].astype(str)))}
    b_order = {lv: i for i, lv in enumerate(
        dict.fromkeys(df["B"].astype(str)))}
    dir_ok, legal_ok, n_unmatched = True, True, 0
    for desc, p, _ in ph["comparisons"]:
        fac, lv, g1, g2 = parse_comp(desc)
        if lv is None:      # 主效应比较: g1/g2 属于 fac 因子自身水平
            order = a_order if fac == "A" else b_order
            if not (g1 in order and g2 in order):
                legal_ok, n_unmatched = False, n_unmatched + 1
            elif order[g1] > order[g2]:
                dir_ok = False
        elif fac == "A":    # 简单效应: 每个 A 水平内 B 两两
            if not (lv in a_order and g1 in b_order and g2 in b_order):
                legal_ok, n_unmatched = False, n_unmatched + 1
            elif b_order[g1] > b_order[g2]:
                dir_ok = False
        else:               # 简单效应: 每个 B 水平内 A 两两
            if not (lv in b_order and g1 in a_order and g2 in a_order):
                legal_ok, n_unmatched = False, n_unmatched + 1
            elif a_order[g1] > a_order[g2]:
                dir_ok = False
    r["key_dir_ok"] = dir_ok
    r["key_legal_ok"] = legal_ok
    check(f"{gid} A7 比较键方向/合法 (v2.3.4)",
          dir_ok and legal_ok,
          f"dir_ok={dir_ok} legal_ok={legal_ok} unmatched={n_unmatched} "
          f"comps={len(ph['comparisons'])}")

    # ---- A8 标注不丢: 画全部简单效应比较, 数 bracket 文本增量 ----
    n_text0 = len(ax.texts)
    drawn, msg = draw_all_comparisons(ax, mapping, ph["comparisons"])
    n_text1 = len(ax.texts)
    # 注意解包: 元素是 (x1, x2, p), 用不重名变量避免 `_` 复用错位
    expect_text = sum(1 for _x1, _x2, p in drawn if p < 0.1)
    got_text = n_text1 - n_text0
    r["expect_brackets"] = expect_text
    r["got_brackets"] = got_text
    if r["expect"] == "simple_effects":
        check(f"{gid} A8 标注不丢 (bracket={got_text}/{expect_text})",
              msg == "ok" and got_text == expect_text and expect_text > 0,
              f"expect={expect_text} got={got_text} msg={msg}")
    else:
        # main_effects: 主效应比较跨 x 位置, 不在分组柱状图上画 bracket
        check(f"{gid} A8 主效应不画 bracket (0/0)",
              msg == "ok" and got_text == expect_text == 0,
              f"expect={expect_text} got={got_text} msg={msg}")

    # ---- 保存代表性图 ----
    if gid in SAVE:
        ax.set_title(f"{gid}: {n_a}×{n_b} design, n={n}/cell, "
                     f"{ph['type']} (p_inter={r['p_inter']})", fontsize=8)
        name = f"deep9_{gid}_{n_a}x{n_b}_n{n}"
        # 验证产物默认会被 run_all 清理,150dpi 足够人工复查,省 ~1/2 渲染时间
        save_figure(fig, name, OUT, dpi=150)
        results.append(r)
        results[-1]["figure"] = name + ".png"
    plt.close(fig)
    return r


def main():
    print(f"=== verify9_deep_matrix: 析因分析组数矩阵深验 (18 设计) ===")
    total_a8 = 0
    for gid, n_a, n_b, n, inter, note in DESIGNS:
        r = run_one(gid, n_a, n_b, n, inter, note)
        if r not in results:  # 未保存图的设计也要进结果表
            results.append(r)
    n_pass = len(results) - len(fails)
    print(f"\n=== 结果: {len(results)} 设计, 失败断言 {len(fails)} 条 ===")
    for f in fails:
        print(f"  FAIL: {f}")

    # 写 JSON 汇总(供 run10 / 报告合并)
    with open(os.path.join(OUT, "verify9_summary.json"), "w",
              encoding="utf-8") as fh:
        json.dump(results, fh, ensure_ascii=False, indent=1)

    # 写报告 md
    lines = ["# verify9_deep_matrix — 析因分析组数矩阵深验报告\n",
             "| id | 设计 | n/格 | 预期分支 | p_inter | 实际分支 | 比较数 | "
             "键方向 | 标注数(应/实) | 图 |",
             "|---|---|---|---|---|---|---|---|---|---|"]
    for r in results:
        lines.append(
            f"| {r['id']} | {r['design']} | {r['n']} | {r['expect']} | "
            f"{r.get('p_inter', '-')} | {r.get('posthoc_type', '-')} | "
            f"{r.get('n_comps', '-')} | {'✓' if r.get('key_dir_ok') else '✗'} | "
            f"{r.get('got_brackets', '-')}/{r.get('expect_brackets', '-')} | "
            f"{r.get('figure', '—')} |")
    lines.append(f"\n失败断言: {len(fails)} 条" + ("" if not fails else
                 "\n" + "\n".join(f"- {f}" for f in fails)))
    with open(os.path.join(OUT, "verify9_deep_matrix_report.md"), "w",
              encoding="utf-8") as fh:
        fh.write("\n".join(lines))

    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
