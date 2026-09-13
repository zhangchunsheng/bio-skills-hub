"""read_table + format_legend 自动推导 的 pytest 单测（v2.6.x 新增）。

覆盖：
1. read_table 长格式 → 自动拆组 + ylabel = 清洗后的数值列表头
2. read_table 宽格式 → 每列一组，ylabel 回退 None
3. read_table 脏表头（单行多空格/首尾空格）→ 清洗生效
4. read_table 读 Excel（.xlsx，需 openpyxl）
5. format_legend 不传 stat_method 时由 test 名自动推导方法文字
   （2 组 t 检验不再写出错误的 ANOVA 描述）
6. format_legend stat_method 显式传入时仍优先（向后兼容）

运行：PY=$(python ../../scripts/ensure_env.py) && $PY -m pytest tests/ -v
"""
import sys, pathlib, tempfile, os
import numpy as np
import pytest

# 技能根目录：由本文件位置推导，**禁止硬编码用户名**（旧版写死 C:\Users\DELL
# 导致换机器/换用户后 import 失败 —— v2.7.5 修复）
SKILL = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL))

from scripts.prism_theme import read_table, format_legend  # noqa: E402


# =====================================================================
# § 1. read_table 长格式
# =====================================================================

def test_read_table_long_returns_clean_ylabel_and_groups():
    """长格式：ylabel = 数值列表头（清洗后），按分组列拆好各组。"""
    csv = ("group,Relative LCN2 expression\n"
           "Control,0.96\nControl,0.78\nControl,1.21\nControl,1.09\n"
           "Treated,1.56\nTreated,1.87\nTreated,1.63\nTreated,1.57\n")
    p = os.path.join(tempfile.gettempdir(), "_rt_long.csv")
    open(p, "w").write(csv)
    r = read_table(p)
    assert r["format"] == "long"
    assert r["ylabel"] == "Relative LCN2 expression"
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
    csv = ("group,  Relative   LCN2   expression   \n"
           "Control,1.0\nTreated,2.0\n")
    p = os.path.join(tempfile.gettempdir(), "_rt_dirty.csv")
    open(p, "w").write(csv)
    r = read_table(p)
    assert r["ylabel"] == "Relative LCN2 expression"


# =====================================================================
# § 4. read_table 读 Excel（xlsx）
# =====================================================================

def test_read_table_xlsx_long(tmp_path=None):
    """Excel 长格式读取（需 openpyxl；缺失则跳过）。"""
    pytest.importorskip("openpyxl")
    import pandas as pd
    p = os.path.join(tempfile.gettempdir(), "_rt_long.xlsx")
    df = pd.DataFrame({
        "group": ["Control"] * 4 + ["Treated"] * 4,
        "Relative LCN2 expression":
            [0.96, 0.78, 1.21, 1.09, 1.56, 1.87, 1.63, 1.57],
    })
    df.to_excel(p, index=False)
    r = read_table(p)
    assert r["format"] == "long"
    assert r["ylabel"] == "Relative LCN2 expression"
    assert r["groups"][0] == [0.96, 0.78, 1.21, 1.09]
    assert r["groups"][1] == [1.56, 1.87, 1.63, 1.57]


# =====================================================================
# § 4b. read_table 坏输入健壮性（v2.7.5 —— 针对"坏输入直接崩、不够傻瓜化"评估）
# =====================================================================

def _w(name, text, encoding="utf-8"):
    """写临时数据文件，返回路径。"""
    p = os.path.join(tempfile.gettempdir(), name)
    with open(p, "w", encoding=encoding, newline="") as f:
        f.write(text)
    return p


def test_read_table_missing_file_gives_actionable_message():
    """文件不存在 → 中文可行动提示，而非裸 FileNotFoundError 路径串。"""
    with pytest.raises(FileNotFoundError) as ei:
        read_table(os.path.join(tempfile.gettempdir(), "_rt_no_such_file.csv"))
    assert "找不到数据文件" in str(ei.value)


def test_read_table_gbk_csv_autodetected():
    """Windows Excel 另存的 GBK 中文 CSV → 自动回退编码读出（不再 UnicodeDecodeError）。"""
    p = _w("_rt_gbk.csv", "组别,相对表达量\nControl,1.0\nModel,3.4\n",
           encoding="gbk")
    r = read_table(p)
    assert r["format"] == "long"
    assert r["labels"] == ["Control", "Model"]
    assert r["ylabel"] == "相对表达量"


def test_read_table_tab_separated_txt_autodetected():
    """制表符分隔的 .txt → 自动嗅探分隔符，按宽格式正确读出两组。"""
    p = _w("_rt_tab.txt", "Control\tModel\n1.0\t3.4\n1.2\t3.1\n")
    r = read_table(p)
    assert r["format"] == "wide"
    assert r["labels"] == ["Control", "Model"]
    assert r["groups"] == [[1.0, 1.2], [3.4, 3.1]]
    assert any("制表符" in n for n in r["notes"])


def test_read_table_wide_with_text_col_not_silently_misread():
    """回归（最危险失败模式）：宽表混入文本列"备注"→ 不得误判为长表而静默丢组。

    旧版把"备注"当分组列，静默产出 groups=[[1.0,1.2]] / labels=['ok']，
    整列 Model 被丢弃且不报错 —— 不崩但结果是错的，可直接导致错误图表。
    """
    p = _w("_rt_textcol.csv", "Control,Model,备注\n1.0,3.4,ok\n1.2,3.1,ok\n")
    r = read_table(p)
    assert r["format"] == "wide"
    assert r["labels"] == ["Control", "Model"]
    assert r["groups"] == [[1.0, 1.2], [3.4, 3.1]]
    # 被忽略的列必须写进 notes，绝不可静默吞掉
    assert any("备注" in n for n in r["notes"])


def test_read_table_empty_file_gives_actionable_message():
    """空文件 → 中文提示，而非 pandas EmptyDataError 裸异常。"""
    p = _w("_rt_empty.csv", "")
    with pytest.raises(ValueError) as ei:
        read_table(p)
    assert "空的" in str(ei.value)


def test_read_table_wrong_col_name_lists_available_cols():
    """列名写错 → 提示中列出可用列，而非裸 KeyError。"""
    p = _w("_rt_wide2.csv", "Control,Treated\n1.0,2.0\n")
    with pytest.raises(ValueError) as ei:
        read_table(p, group_col="Group")          # 实际列名是 Control/Treated
    assert "Control" in str(ei.value) and "Treated" in str(ei.value)


def test_read_table_na_tokens_and_thousands_separator():
    """占位符（ND / —）→ NaN 剔除；千分位 "1,234" → 1234（不误伤欧式小数）。"""
    p = _w("_rt_na.csv", 'Control,Model\n1.0,"1,234"\nND,2.0\n—,3.0\n')
    r = read_table(p)
    assert r["groups"] == [[1.0], [1234.0, 2.0, 3.0]]


# =====================================================================
# § 5. format_legend 由 test 名自动推导方法文字
# =====================================================================

def test_format_legend_auto_method_from_ttest():
    """2 组 t 检验：不传 stat_method、传 test='ttest' → 写出 Unpaired t-test。"""
    legend = format_legend(
        "LCN2 expression in Control and Treat groups (Western Blot)",
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
    matplotlib_use()
    import matplotlib.pyplot as plt
    from scripts.prism_theme import (
        apply_prism_theme, prism_bars, ttest_two_groups, add_pairwise_brackets,
    )
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


def matplotlib_use():
    import matplotlib
    matplotlib.use("Agg")
