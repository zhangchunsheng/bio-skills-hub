"""read_table + format_legend 自动推导 的 pytest 单测（v2.6.x 新增，同步自 prism-style-plot）。

覆盖：
1. read_table 长格式 → 自动拆组 + ylabel = 清洗后的数值列表头
2. read_table 宽格式 → 每列一组，ylabel 回退 None
3. read_table 脏表头（单行多空格/首尾空格）→ 清洗生效
4. read_table 读 Excel（.xlsx，需 openpyxl）
5. format_legend 不传 stat_method 时由 test 名自动推导方法文字
   （2 组 t 检验不再写出错误的 ANOVA 描述）
6. format_legend stat_method 显式传入时仍优先（向后兼容）
7. add_pairwise_brackets ytick_step 覆盖自动步长

运行：PY=$(python scripts/ensure_env.py) && $PY -m pytest tests/ -v
（本文件用 __file__ 推导技能根目录，跨机器/跨用户名可移植，不硬编码用户目录）
"""
import sys, pathlib, tempfile, os
import numpy as np
import pytest

SKILL = pathlib.Path(__file__).resolve().parent.parent  # tests/.. = 技能根
sys.path.insert(0, str(SKILL))

from scripts.prism_theme import (  # noqa: E402
    read_table, format_legend, prism_bars, ttest_two_groups,
    add_pairwise_brackets, apply_prism_theme,
)


# =====================================================================
# § 1. read_table 长格式
# =====================================================================

def test_read_table_long_returns_clean_ylabel_and_groups():
    """长格式：ylabel = 数值列表头（清洗后），按分组列拆好各组。"""
    csv = ("group,Relative TargetX expression\n"
           "Control,0.96\nControl,0.78\nControl,1.21\nControl,1.09\n"
           "Treated,1.56\nTreated,1.87\nTreated,1.63\nTreated,1.57\n")
    p = os.path.join(tempfile.gettempdir(), "_rt_long.csv")
    open(p, "w").write(csv)
    r = read_table(p)
    assert r["format"] == "long"
    assert r["ylabel"] == "Relative TargetX expression"
    assert r["labels"] == ["Control", "Treated"]
    assert r["groups"][0] == [0.96, 0.78, 1.21, 1.09]
    assert r["groups"][1] == [1.56, 1.87, 1.63, 1.57]


# =====================================================================
# § 2. read_table 宽格式
# =====================================================================

def test_read_table_wide_returns_none_ylabel_each_col_a_group():
    """宽格式：每列一组，无单一数值列名 → ylabel=None。"""
    csv = ("Control,Treated\n"
           "0.96,1.56\n0.78,1.87\n1.21,1.63\n1.09,1.57\n")
    p = os.path.join(tempfile.gettempdir(), "_rt_wide.csv")
    open(p, "w").write(csv)
    r = read_table(p)
    assert r["format"] == "wide"
    assert r["ylabel"] is None
    assert r["labels"] == ["Control", "Treated"]
    assert r["groups"][0] == [0.96, 0.78, 1.21, 1.09]
    assert r["groups"][1] == [1.56, 1.87, 1.63, 1.57]


# =====================================================================
# § 3. read_table 脏表头清洗
# =====================================================================

def test_read_table_dirty_header_is_cleaned():
    """单行带多余空格/首尾空格的脏表头 → 合并为单空格。"""
    csv = ("group,  Relative   TargetX   expression   \n"
           "Control,1.0\nTreated,2.0\n")
    p = os.path.join(tempfile.gettempdir(), "_rt_dirty.csv")
    open(p, "w").write(csv)
    r = read_table(p)
    assert r["ylabel"] == "Relative TargetX expression"


# =====================================================================
# § 4. read_table 读 Excel（xlsx）
# =====================================================================

def test_read_table_xlsx_long():
    """Excel 长格式读取（需 openpyxl；缺失则跳过）。"""
    pytest.importorskip("openpyxl")
    import pandas as pd
    p = os.path.join(tempfile.gettempdir(), "_rt_long.xlsx")
    df = pd.DataFrame({
        "group": ["Control"] * 4 + ["Treated"] * 4,
        "Relative TargetX expression":
            [0.96, 0.78, 1.21, 1.09, 1.56, 1.87, 1.63, 1.57],
    })
    df.to_excel(p, index=False)
    r = read_table(p)
    assert r["format"] == "long"
    assert r["ylabel"] == "Relative TargetX expression"
    assert r["groups"][0] == [0.96, 0.78, 1.21, 1.09]
    assert r["groups"][1] == [1.56, 1.87, 1.63, 1.57]


# =====================================================================
# § 5. format_legend 由 test 名自动推导方法文字
# =====================================================================

def test_format_legend_auto_method_from_ttest():
    """2 组 t 检验：不传 stat_method、传 test='ttest' → 写出 Unpaired t-test。"""
    legend = format_legend(
        "TargetX expression in Control and Treat groups (Western Blot)",
        n=[4, 4],
        pairwise=[("Control", "Treat", 0.00364)],
        test="ttest",
    )
    assert "Unpaired t-test" in legend
    assert "ANOVA" not in legend


def test_format_legend_auto_method_anova_default():
    """多组、不传 stat_method/test → 回退 One-way ANOVA + Tukey（非旧版怪异措辞）。"""
    legend = format_legend(
        "Three-group comparison",
        n=[5, 5, 5],
        pairwise=[("A", "B", 0.1), ("A", "C", 0.001), ("B", "C", 0.01)],
    )
    assert "One-way ANOVA + Tukey" in legend


def test_format_legend_explicit_stat_method_preserved():
    """显式传 stat_method 仍优先（向后兼容）。"""
    legend = format_legend(
        "desc", n=4, pairwise=[("A", "B", 0.01)],
        stat_method="Welch t-test",
    )
    assert "Welch t-test" in legend


# =====================================================================
# § 6. add_pairwise_brackets ytick_step 覆盖自动步长
# =====================================================================

def test_add_pairwise_brackets_ytick_step():
    """显式 ytick_step=0.5 → 轴顶为 0.5 整数倍、刻度每 0.5 一格。"""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    groups = [[0.96, 0.78, 1.21, 1.09], [1.56, 1.87, 1.63, 1.57]]
    labels = ["Control", "Treated"]
    _, p, _ = ttest_two_groups(*groups)
    apply_prism_theme()
    fig, ax = plt.subplots(figsize=(3 / 2.54, 4 / 2.54))
    prism_bars(ax, groups, labels, error_type="sem")
    add_pairwise_brackets(ax, [(labels[0], labels[1], p)], labels=labels,
                          ytick_step=0.5)
    ticks = list(ax.get_yticks())
    # 每 0.5 一格
    assert all(abs((t * 2) - round(t * 2)) < 1e-6 for t in ticks)
    # 轴顶是 0.5 整数倍
    top = ax.get_ylim()[1]
    assert abs((top * 2) - round(top * 2)) < 1e-6
