"""验证 12(v2.7.0 新增):多数据集合并面板图 + 总报告
覆盖:compose_panel_figure(自动网格 + A/B/C 标注 + 独立原图/统计报告)
      build_master_report(合并图置顶 + 各面板独立统计依次列出)。
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from prism_theme import (
    apply_prism_theme, get_figsize, prism_bars,
    oneway_anova_tukey, ttest_two_groups, add_pairwise_brackets,
    build_stats_report, write_report, compose_panel_figure,
)
from verify_common import make_groups, report, SEED

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
os.makedirs(OUT, exist_ok=True)
fails = []
apply_prism_theme()


def _panel(draw_fn, name, stats_md, title):
    return {"draw": draw_fn, "name": name, "stats_md": stats_md, "title": title}


# ---------- 12.1 三面板自动 1×3 网格 + 统计 ----------
try:
    panels = []
    # A: 三组 ANOVA
    gA = make_groups(n_per_group=6, n_groups=3, base=(10, 12, 16), sd=1.5)
    labA = ["Control", "Low", "High"]
    resA = oneway_anova_tukey(gA, labA)

    def draw_A(ax):
        prism_bars(ax, gA, labA)
        add_pairwise_brackets(ax, resA["pairwise"], labels=labA)
    repA = build_stats_report("anova_tukey", description="Cytokine A (3-group)",
                              groups=gA, labels=labA)
    panels.append(_panel(draw_A, "verify12_pA", repA, "Cytokine A"))

    # B: 两组 t-test
    a = np.random.default_rng(SEED).normal(10, 1.5, 8)
    b = np.random.default_rng(SEED + 1).normal(14, 1.5, 8)

    def draw_B(ax):
        prism_bars(ax, [a, b], ["Ctrl", "Treated"])
        add_pairwise_brackets(ax, [("Ctrl", "Treated", pB)], labels=["Ctrl", "Treated"])
    _, pB, _ = ttest_two_groups(a, b)
    repB = build_stats_report("ttest", description="Cytokine B (2-group)",
                              groups=[a, b], labels=["Ctrl", "Treated"])
    panels.append(_panel(draw_B, "verify12_pB", repB, "Cytokine B"))

    # C: 另一组三组数据(差异明确,确保 Tukey 后出现显著性 bracket)
    gC = make_groups(n_per_group=6, n_groups=3, base=(2.0, 2.8, 3.8), sd=0.35, seed=7)
    labC = ["Sham", "TBI", "TBI+Treat"]
    resC = oneway_anova_tukey(gC, labC)

    def draw_C(ax):
        prism_bars(ax, gC, labC)
        add_pairwise_brackets(ax, resC["pairwise"], labels=labC)
    repC = build_stats_report("anova_tukey", description="Cytokine C (3-group, small range)",
                              groups=gC, labels=labC)
    panels.append(_panel(draw_C, "verify12_pC", repC, "Cytokine C"))

    res = compose_panel_figure(panels, out_dir=OUT, name="verify12_combined",
                               panel_titles=["Cytokine A", "Cytokine B", "Cytokine C"],
                               panel_shape="square")
    # 校验合并产物
    assert os.path.exists(res["combined_png"]), "合并 PNG 未生成"
    assert os.path.exists(res["combined_pdf"]), "合并 PDF 未生成"
    assert os.path.exists(res["master_html"]), "总 HTML 报告未生成"
    # 校验每面板独立产物(原图 + 统计报告 md/html)
    # 注意: report_md 是 Markdown 内容字符串(直接内嵌总报告),非文件路径;
    #        png/pdf/report_html 才是落盘文件路径。
    for p in res["panels"]:
        assert isinstance(p["report_md"], str) and p["report_md"].strip(), \
            f"面板 {p['name']} 的 report_md 应为非空字符串内容"
        for key in ("png", "pdf", "report_html"):
            assert p[key] and os.path.exists(p[key]), f"面板 {p['name']} 缺 {key}"
    assert len(res["panels"]) == 3, "面板数应为 3"
    assert [p["label"] for p in res["panels"]] == ["A", "B", "C"], "面板标注应为 A/B/C"
    report("12.1 三面板 compose_panel_figure(1×3 自动网格 + 独立原图/统计)",
           True, f"合并图: {os.path.basename(res['combined_png'])}")
except Exception as e:
    fails.append(("12.1 compose 3-panel", e))
    report("12.1 三面板 compose_panel_figure", False, str(e))


# ---------- 12.2 四面板自动 2×2 网格 ----------
try:
    panels2 = []
    for i, base in enumerate([(8, 10), (5, 6.5), (3, 4), (12, 15)]):
        x = np.random.default_rng(SEED + i).normal(base[0], 1.0, 7)
        y = np.random.default_rng(SEED + 100 + i).normal(base[1], 1.0, 7)

        def _draw(ax, x=x, y=y):
            prism_bars(ax, [x, y], ["Veh", "Drug"])
            add_pairwise_brackets(ax, [("Veh", "Drug", _p)], labels=["Veh", "Drug"])
        _, _p, _ = ttest_two_groups(x, y)
        rep = build_stats_report("ttest", description=f"Metric {i+1}",
                                 groups=[x, y], labels=["Veh", "Drug"])
        panels2.append(_panel(_draw, f"verify12_q{i+1}", rep, f"Metric {i+1}"))

    res2 = compose_panel_figure(panels2, out_dir=OUT, name="verify12_combined4",
                                panel_titles=[f"Metric {i+1}" for i in range(4)],
                                panel_shape="square")
    assert os.path.exists(res2["combined_png"]), "四面板合并 PNG 未生成"
    assert len(res2["panels"]) == 4, "四面板应为 4 个"
    report("12.2 四面板 compose_panel_figure(2×2 自动网格)", True,
           f"合并图: {os.path.basename(res2['combined_png'])}")
except Exception as e:
    fails.append(("12.2 compose 4-panel", e))
    report("12.2 四面板 compose_panel_figure", False, str(e))


# ---------- 12.3 自定义 layout 覆盖 + 空 panels 报错 ----------
try:
    # 自定义 1×2 布局放 2 个面板
    sub = []
    for i in range(2):
        x = np.random.default_rng(SEED + 200 + i).normal(10, 1, 7)
        y = np.random.default_rng(SEED + 300 + i).normal(13, 1, 7)

        def _draw(ax, x=x, y=y):
            prism_bars(ax, [x, y], ["A", "B"])
        _, _p, _ = ttest_two_groups(x, y)
        rep = build_stats_report("ttest", description=f"Custom {i+1}",
                                 groups=[x, y], labels=["A", "B"])
        sub.append(_panel(_draw, f"verify12_c{i+1}", rep, f"Custom {i+1}"))
    res3 = compose_panel_figure(sub, out_dir=OUT, name="verify12_custom",
                                layout=(1, 2), panel_shape="square")
    assert os.path.exists(res3["combined_png"])

    # 空 panels 应抛 ValueError
    raised = False
    try:
        compose_panel_figure([], out_dir=OUT, name="verify12_empty")
    except ValueError:
        raised = True
    assert raised, "空 panels 未抛 ValueError"
    report("12.3 layout 覆盖(1×2) + 空 panels 报错", True, "自定义布局与异常校验通过")
except Exception as e:
    fails.append(("12.3 layout + empty", e))
    report("12.3 layout 覆盖 + 空 panels 报错", False, str(e))


if fails:
    print("\n[FAIL] 失败项:")
    for name, e in fails:
        print(f"  - {name}: {e}")
    sys.exit(1)
print("\n[PASS] verify12 全部通过")
sys.exit(0)
