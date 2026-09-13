"""
prism_theme.py — GraphPad Prism 风格 matplotlib 主题与辅助函数
===============================================================
本脚本把 Prism 的期刊规范美学翻译成 matplotlib 可复用的工具：
1. apply_prism_theme()     全局主题：L 形坐标轴、无衬线字体、色盲友好配色、去网格
2. prism_boxplot()         箱线图（中位数/IQR 箱 + 个体散点，内置正确配色）
3. add_significance_brackets()  在两组之间画显著性连接线 + 星号
4. add_pairwise_brackets() 多组两两比较的显著性括号，自动分层防重叠
5. p_to_stars()             p 值 → 星号字符串
6. mean_sem / mean_sd      描述统计辅助
7. save_figure()            双格式输出（300dpi PNG + 矢量 PDF）

用法：
    from prism_theme import (apply_prism_theme, prism_boxplot,
                             add_pairwise_brackets, oneway_anova_tukey)
    apply_prism_theme()
    prism_boxplot(ax, groups, labels)                 # 箱线图 + 散点
    res = oneway_anova_tukey(groups, labels)
    add_pairwise_brackets(ax, res["pairwise"])        # 自动画全部两两比较
    save_figure(fig, "output/tumor_vol_box")
"""

import matplotlib

matplotlib.use("Agg")  # 无显示环境安全默认

import contextlib
import os
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats
# NOTE: scipy.optimize.curve_fit 仅 prism_xy_fit 的 4PL 分支使用，
# 改为函数内懒加载，避免柱状图/箱线图等常用路径在 import 期就被迫加载
# scipy.optimize（冷启动可省 ~1-2s）。见 prism_xy_fit 内 curve_fit 调用处。
import matplotlib.ticker as mticker
from matplotlib.colors import to_rgba
from matplotlib.collections import PathCollection

# v2.3.0 公开 API 锁定：所有稳定公开函数集中声明。
# 依赖此列表的工具（agent 静态校验、__all__-aware IDE、wildcard import）
# 都能拿到完整清单。新增函数请同步添加；标记为内部 helper 用 _ 前缀不放进列表。
__all__ = [
    # ---- 主题与配色 ----
    "apply_prism_theme",
    "get_palette",
    "palette_sequence",
    "get_figsize",
    "recommend_shape",
    "recommend_figsize",
    # ---- 散点布局 / 点大小 ----
    "jitter_offsets",
    "beeswarm_offsets",
    "add_individual_dots",
    "common_point_size",
    "common_bar_width",   # v2.3.7 NEW
    "auto_dot_size",
    "auto_point_size",
    "auto_dot_alpha",
    # ---- 显著性标注 ----
    "add_significance_brackets",
    "add_pairwise_brackets",
    "p_to_stars",
    "format_p",
    "format_legend",
    # ---- 描述统计 / 输出 ----
    "mean_sem",
    "mean_sd",
    "save_figure",
    "finish_axes",
    "set_nice_ylim",
    # ---- 数据读取（v2.6.0 NEW：读表自动设 ylabel 默认） ----
    "read_table",
    "read_excel_sheets",   # v2.7.2 NEW：单 Excel 多 sheet 一键解析
    # ---- 8 种表型封装 ----
    "prism_bars",
    "prism_grouped_bars",   # v2.3.6 NEW
    "prism_boxplot",
    "prism_violin",
    "prism_survival",
    "prism_xy_fit",
    "prism_nested_bars",  # v2.3.0 NEW
    "prism_pie",          # v2.3.0 NEW
    "prism_donut",        # v2.3.0 NEW
    "prism_pairplot",     # v2.3.0 NEW
    "prism_facet_boxplot",  # v2.3.0 NEW
    # ---- 统计检验 ----
    "ttest_two_groups",
    "oneway_anova_tukey",
    "twoway_posthoc",
    "rm_twoway_anova",
    "prism_spaghetti",
    "nested_anova",              # v2.4.5 NEW
    "cox_regression",            # v2.4.3 NEW
    "mann_whitney_u",          # v2.3.0 NEW
    "wilcoxon_signed_rank",    # v2.3.0 NEW
    # ---- 报告生成 ----
    "build_stats_report",
    "write_report",
    "write_html_report",
    # ---- 产物配套落盘（v2.3.2 NEW） ----
    "emit_run_script",
    # ---- 多数据集合并面板图 + 总报告（v2.7.0 NEW） ----
    "compose_panel_figure",
    "build_master_report",
]

# 色盲友好配色（来源：图片中收录的标准 Colorblind-safe 色板）
# Okabe-Ito（2002）——色盲安全分类色板，默认方案，Prism 官方推荐同思路
OKABE_ITO = {
    "black": "#000000",
    "bluish_green": "#009E73",
    "blue": "#0072B2",
    "sky_blue": "#56B4E9",
    "yellow": "#F0E442",
    "orange": "#E69F00",
    "vermilion": "#D55E00",
    "reddish_purple": "#CC79A7",
}
# Paul Tol Muted（Tol, 2018）——柔和、低饱和，适合多组/复杂图
PAUL_TOL_MUTED = {
    "light_grey": "#DDDDDD",
    "dark_blue": "#2E2585",
    "green": "#337538",
    "teal": "#5DA899",
    "light_blue": "#94CBEC",
    "yellow": "#DCCD7D",
    "rose": "#C26A77",
    "purple": "#9F4A96",
    "wine": "#7E2954",
}
# Paul Tol Bright（Tol, 2018）——色盲安全 + 印刷安全定性色板，
# 印刷为主/投影仪偏弱时比 Okabe-Ito 更稳
PAUL_TOL_BRIGHT = {
    "grey": "#BBBBBB",
    "dark_blue": "#2E2585",
    "green": "#337538",
    "teal": "#5DA899",
    "light_blue": "#94CBEC",
    "yellow": "#DCCD7D",
    "rose": "#C26A77",
}
# IBM Design Library——IBM 官方色盲安全配色（5 色），高对比、屏幕友好
IBM_DESIGN_LIBRARY = {
    "blue": "#648FFF",
    "purple": "#785EF0",
    "magenta": "#DC267F",
    "orange": "#FE6100",
    "yellow": "#FFB000",
}
# 单组灰度系（非荧光实验首选，Prism 用户手册建议）
GRAY_SCALE = ["#000000", "#4D4D4D", "#808080", "#B3B3B3", "#D9D9D9"]

_PALETTE_MAP = {
    "okabe_ito": OKABE_ITO,
    "paul_tol": PAUL_TOL_BRIGHT,
    "paul_tol_bright": PAUL_TOL_BRIGHT,
    "paul_tol_muted": PAUL_TOL_MUTED,
    "ibm_design": IBM_DESIGN_LIBRARY,
    "ibm_design_library": IBM_DESIGN_LIBRARY,
}

def get_palette(name="okabe_ito"):
    """
    返回色盲安全色板（dict：颜色名 → hex）。

    name 可选：
      - "okabe_ito"（默认，8 色）
      - "paul_tol" / "paul_tol_bright"（Paul Tol Bright，7 色）
      - "paul_tol_muted"（Paul Tol Muted，9 色）
      - "ibm_design" / "ibm_design_library"（IBM Design Library，5 色）
    """
    key = str(name).strip().lower().replace(" ", "_")
    if key not in _PALETTE_MAP:
        raise ValueError(
            f"未知色板: {name!r}。可用: "
            f"{', '.join(_PALETTE_MAP.keys())}"
        )
    return _PALETTE_MAP[key]

def palette_sequence(name="okabe_ito"):
    """
    返回按期刊图常用顺序排列的分组配色序列（list of hex）。

    默认 Okabe-Ito：蓝、朱红、青绿、橙、紫红、天蓝（前 3 个即三组柱状图常用搭配）。
    其他方案按色板内视觉区分度由大到小排列。
    """
    pal = get_palette(name)
    key = str(name).strip().lower().replace(" ", "_")
    if key in ("paul_tol", "paul_tol_bright"):
        order = ["dark_blue", "rose", "green", "teal",
                 "light_blue", "yellow", "grey"]
    elif key == "paul_tol_muted":
        order = ["dark_blue", "rose", "green", "teal", "purple",
                 "light_blue", "yellow", "wine", "light_grey"]
    elif key in ("ibm_design", "ibm_design_library"):
        order = ["blue", "magenta", "orange", "purple", "yellow"]
    else:  # okabe_ito
        order = ["blue", "vermilion", "bluish_green", "orange",
                 "reddish_purple", "sky_blue"]
    return [pal[k] for k in order]

# GraphPad 图形态预设（宽, 高 单位：cm，v2.0.11 由 inch 改为 cm）。
# tall 为默认——单面板期刊图最常见，高瘦构图让数据主体更突出；square 适合
# 单图均衡展示；wide 适合多组对比、时间序列或需要并排展示的面板。
# matplotlib 的 figsize 内部单位是 inch，get_figsize() 会自动换算（1 in = 2.54 cm）。
FIGURE_SHAPES = {
    "tall": (3, 5),
    "square": (5, 5),
    "wide": (7, 5),
}
_SHAPE_ALIASES = {
    "tall": "tall", "高": "tall", "高瘦": "tall", "t": "tall",
    "square": "square", "方": "square", "方形": "square", "s": "square",
    "wide": "wide", "宽": "wide", "宽扁": "wide", "w": "wide",
}

def get_figsize(shape="tall"):
    """
    解析图形态选择（tall / square / wide），返回 matplotlib figsize 元组
    (宽, 高)，**单位 inch**（matplotlib 内部约定）。

    预设以 cm 为单位（v2.0.11 起）：tall=3×5 cm、square=5×5 cm、wide=7×5 cm，
    本函数按 1 in = 2.54 cm 换算后返回。调用方（plt.subplots 等）无需感知单位，
    直接使用返回值即可得到用户指定的 cm 物理尺寸。

    支持中英文别名："tall"/"高"/"高瘦"、"square"/"方"、"wide"/"宽"/"宽扁"。
    无法识别时回退默认 tall（GraphPad 单面板图的主流形态）。
    """
    key = str(shape).strip().lower()
    cm = FIGURE_SHAPES.get(_SHAPE_ALIASES.get(key, "tall"), FIGURE_SHAPES["tall"])
    return tuple(round(v / 2.54, 3) for v in cm)


# —— 数据表类型 → 推荐画布形态（默认建议层；用户显式关键词永远优先）——
# 依据：Column/Grouped 按总分组数分档（组数少→高瘦 tall，中→方形 square，多→宽扁 wide）；
#       XY / Survival 单曲线图用 square 均衡展示；Contingency 双行计数柱用 wide 容纳并排柱。
TABLE_SHAPE_DEFAULTS = {
    "xy": "square",
    "survival": "square",
    "contingency": "wide",
    "partsofwhole": "square",       # 饼图/环形图：方形均衡
    "multiplevariables": "wide",    # 宽表多变量：需要横向空间
    "nested": "tall",               # 嵌套柱状图：高瘦突出层级
}


def _norm_table_type(tt):
    """归一化表类型字符串：小写、去空白/下划线/连字符，容忍各种写法。"""
    if tt is None:
        return ""
    s = str(tt).strip().lower().replace("_", "").replace("-", "")
    return "".join(s.split())


def recommend_shape(table_type=None, n_groups=None, shape=None):
    """
    数据表类型 → 推荐画布形态（tall / square / wide）的**默认建议层**。

    三级优先级：
      1) shape（用户显式关键词，含中文别名）——最高优先，覆盖一切默认；
      2) table_type 映射：
         - Column / Grouped：按**总分组数**分档——<5 → tall、5–8 → square、>8 → wide；
         - XY / Survival → square、Contingency → wide
           （详见 TABLE_SHAPE_DEFAULTS，另含 Parts of whole → square、
           Multiple variables → wide、Nested → tall）；
      3) 兜底 tall（与 get_figsize 原默认一致）。

    返回形态名字符串，配合 get_figsize() 使用。
    """
    # 1) 用户显式指定优先（关键词覆盖通道；未识别关键词不算覆盖，继续走默认建议）
    key = str(shape).strip().lower() if shape else ""
    if key in _SHAPE_ALIASES:
        return _SHAPE_ALIASES[key]
    # 2) Column/Grouped：按总分组数分档（缺分组数时回退 tall）
    tt = _norm_table_type(table_type)
    if tt in ("column", "grouped"):
        try:
            n = int(n_groups)
        except (TypeError, ValueError):
            n = -1
        if n < 5:
            return "tall"
        if n <= 8:
            return "square"
        return "wide"
    # 3) 其它已知表型 → 固定默认
    if tt in TABLE_SHAPE_DEFAULTS:
        return TABLE_SHAPE_DEFAULTS[tt]
    # 4) 兜底
    return "tall"


def recommend_figsize(table_type=None, n_groups=None, shape=None):
    """
    recommend_shape() 的便捷封装：直接返回 matplotlib figsize 元组（inch）。

    用法：
        plt.subplots(figsize=recommend_figsize("column", n_groups=3))   # 3 组 → tall
        plt.subplots(figsize=recommend_figsize("grouped", n_groups=6))  # 6 组 → square
        plt.subplots(figsize=recommend_figsize("xy"))                   # XY → square
        plt.subplots(figsize=recommend_figsize("contingency"))          # → wide
        # 关键词覆盖默认建议：
        plt.subplots(figsize=recommend_figsize("column", n_groups=3, shape="wide"))
    """
    return get_figsize(recommend_shape(table_type, n_groups, shape))


def _pick_font(preferred=("Arial", "Helvetica", "DejaVu Sans")):
    """选择环境中实际存在的无衬线字体；Arial 缺失时静默回退，
    避免 matplotlib 每个文本元素都打印 findfont 警告。"""
    available = {f.name for f in matplotlib.font_manager.fontManager.ttflist}
    for name in preferred:
        if name in available:
            return name
    return "DejaVu Sans"

def apply_prism_theme(font_family=None, font_scale=1.0):
    """
    应用 Prism 风格全局主题。

    要点（为什么这样设）：
    - L 形坐标轴：去掉上/右边框，科研图的主流审美，图更"干净"
    - 无衬线字体：优先 Arial/Helvetica（国际期刊通用），缺失时自动回退
    - 去网格线：Prism 默认图表不带网格，网格线会干扰数据阅读
    - 配色：色盲友好，确保所有读者（含色觉障碍审稿人）可辨
    """
    if font_family is None:
        font_family = _pick_font()
    plt.rcParams.update({
        "font.family": font_family,
        # v2.0.11：字号整体 −4（用户要求），10→6 / 12→8
        "font.size": 6 * font_scale,
        "axes.titlesize": 8 * font_scale,
        "axes.labelsize": 8 * font_scale,
        "xtick.labelsize": 6 * font_scale,
        "ytick.labelsize": 6 * font_scale,
        "axes.linewidth": 0.75,     # 默认线宽 0.75 pt（印刷/投影清晰、仍属期刊细线，对齐 neuroresearch v2.0.7）
        "lines.linewidth": 0.75,    # v2.0.37：漏设修复——matplotlib 出厂默认 1.5，
                                    # 任何未显式传 lw 的线（如 ax.bar 的 yerr 误差棒、
                                    # plt.plot）会落到 1.5，与技能 0.75 pt 规范不符
                                    # （Grouped 手写模板实测误差线 1.5 pt，已修）
        "axes.edgecolor": "#000000",
        "axes.spines.top": False,       # L 形坐标轴：去上框
        "axes.spines.right": False,     # L 形坐标轴：去右框
        "axes.grid": False,             # 去网格线
        "figure.dpi": 100,
        "savefig.dpi": 300,
        "savefig.bbox": "tight",
        "legend.frameon": False,        # 图例无边框
        "mathtext.fontset": "dejavusans",
    })

def p_to_stars(p, include_ns=True):
    """p 值 → Prism 星号。返回 (星号字符串, 是否显著)。"""
    if not np.isfinite(p):
        # NaN/±inf：无法判定显著性，返回空串（不标），避免 NaN 误落 * 分支
        return ("", False)
    if p >= 0.05:
        return ("ns" if include_ns else "", False)
    if p < 0.0001:
        return ("****", True)
    if p < 0.001:
        return ("***", True)
    if p < 0.01:
        return ("**", True)
    return ("*", True)

def add_significance_brackets(ax, x1, x2, p_value, y=None, height=0.03,
                              color="black", lw=0.75, include_ns=False,
                              fontsize=7, show_marginal_p=True, p_fontsize=6,
                              p_precision=None):
    """
    在 x1 与 x2 两个刻度之间画显著性连接线 + 标注（v2.0.17 混合标注规则）。

    标注规则（v2.0.17 用户指定，星号体系回归）：
    - **p < 0.05（显著）：星号**（*、**、***、****，按标准 p_to_stars 阈值，
      与 v2.0.16 之前一致）
    - **0.05 ≤ p < 0.1（边缘显著/趋势）：直接标注精确 p 值**（如 p=0.073、
      p=0.098，用 format_p 格式；字号 p_fontsize=6）——p 精确值标注**只**在
      此区间触发（v2.0.17 撤销了 v2.0.16 的"p<0.01 标 p 值"，用户改回星号）
    - **p ≥ 0.1：不画任何标记**（include_ns=False 默认；include_ns=True 时
      p≥0.05 显示 "ns"）
    - 标注位置（v2.0.21 按类型分开）：**p 值文本底在横线上（offset 0）**——
      'p' 的 descender 自然垂下不穿线；**星号底在横线下 0.03 span**（v2.0.25
      由 -0.02 加深）——星号主体横跨横线上下，"骑线"更深、与括号绑定更强。
      层间安全：星号 offset -0.03 时 LH ≥ BH + textH - 0.03 = 0.014+0.04-0.03
      = 0.024 ≤ LH 0.043 ✓（充裕）；p 值 offset 0 时 LH ≥ BH + textH = 0.054
      略超 0.043（0.03 单位微侵入可忽略，6pt 文本实际更矮）

    参数：
        x1, x2 : 被比较两组的 x 坐标（数值）
        p_value: 该比较的 p 值
        y      : 连接线纵坐标；None 时自动放在该区域数据最大值上方
        height : 连接线距离 y 的额外高度（相对 y 值范围的 3% 基准）
        color/lw: 线条样式
        include_ns: 是否标注 ns（默认 False，v2.0.16 起不显著不标）
        show_marginal_p: p∈[0.05,0.1) 边缘显著时标注精确 p 值（默认 True）
        p_fontsize  : p 值文本字号（默认 6，小于星号 7）
    """
    ylim = ax.get_ylim()
    span = ylim[1] - ylim[0]
    if y is None:
        # 取 x1、x2 附近数据的最大值，放到其上方 4%
        y_data = []
        for line in ax.lines:
            y_data.extend(line.get_ydata())
        for coll in ax.collections:
            if hasattr(coll, "get_offsets"):
                y_data.extend(coll.get_offsets()[:, 1])
        base = max(y_data) if y_data else ylim[0]
        y = base + 0.04 * span
    h = height * span

    stars, sig = p_to_stars(p_value, include_ns=include_ns)
    # 混合标注（v2.0.17）：边缘显著区间 [0.05, 0.1) 标精确 p 值（替代星号/ns），
    # 其他区间按原系统：显著→星号；不显著→默认不画（include_ns=True 时画 "ns"）。
    # v2.5.6 修复：此前 include_ns 仅传给 p_to_stars（只改了返回字符串），
    # 分支判定用的是 sig（p≥0.05 恒为 False），导致 include_ns=True 实际不画
    # 任何 ns 标记、与文档"可恢复 ns 文本"矛盾。现改为：sig 为真→星号；
    # sig 为假且 include_ns 为真→画 "ns"（stars 此时即 "ns"）；二者皆否→不画。
    if show_marginal_p and 0.05 <= p_value < 0.1:
        label = format_p(p_value, precision=p_precision)
        label_fontsize = p_fontsize
        label_offset = 0.0    # v2.0.21：p 值文本底在横线上（'p' descender 自然垂下，不穿线）
    elif sig:
        label = stars
        label_fontsize = fontsize
        label_offset = -0.03  # v2.0.25：星号底在横线下 0.03 span（由 -0.02 加深），
                              # 主体横跨横线"骑线"更深、与括号绑定更强
    elif include_ns:
        label = stars         # include_ns=True 时 p_to_stars 已返回 "ns"
        label_fontsize = fontsize
        label_offset = -0.03
    else:
        return ax  # p≥0.05（非边缘、非 include_ns）：不画任何标记（v2.0.16 默认）
    ax.plot([x1, x1, x2, x2], [y, y + h, y + h, y], color=color, lw=lw, clip_on=False)
    # 标注底部位置：v2.0.19-20 统一 -0.005/-0.01；v2.0.21 按类型分开——
    # p 值文本 offset=0（底在横线上），星号 offset=-0.03（底在横线下 0.03 span，
    # glyph 顶约在横线上 0.03 span，星号被横线"穿过"的骑线效果，v2.0.25 加深）
    ax.text((x1 + x2) / 2, y + h + label_offset * span, label, ha="center", va="bottom",
            fontsize=label_fontsize, color=color)
    # 给上方留出标注空间，避免文本被裁切（余量占比，越小越紧凑；
    # v2.0.16：0.04→0.03）
    top = y + h + 0.03 * span
    if top > ylim[1]:
        set_nice_ylim(ax, top)

# p 值下溢标记：当 scipy 返回 0.0（p 低于双精度可表示范围）时唯一诚实的表示
# 是 "p<1e-300"（Prism 同显示 <0.0001），对齐 neuroresearch v2.0.4 p 值格式铁律
_P_UNDERFLOW = "<1e-300"

# 全局 p 值精度开关（由 build_stats_report / format_legend 的 p_precision 参数临时设置）。
# None = 默认期刊通用写法（p≥0.001 用 3 位小数；p<0.001 用科学计数法 3 位有效数字）。
# int n = 统一 n 位精度（p≥0.001 用 n 位小数；p<0.001 用 n 位有效数字科学计数法）。
_FORMAT_P_PRECISION = None


@contextlib.contextmanager
def _fmt_p_precision(precision):
    """临时把全局 p 值精度设为 precision（None=默认），退出时还原。

    所有 _report_* / format_legend 内部均以模块全局名调用 format_p，
    故临时改写全局即可在不大改签名的前提下统一生效。
    """
    saved = _FORMAT_P_PRECISION
    if precision is not None:
        globals()["_FORMAT_P_PRECISION"] = precision
    try:
        yield
    finally:
        globals()["_FORMAT_P_PRECISION"] = saved


def format_p(p, precision=None):
    """p 值 → 图注/报告文本（输出 scipy 计算出的**实际精确值**；仅数值下溢
    时用 '<' 阈值写法，其余一律给出精确值）。

    - precision=None（默认，期刊通用）：p ≥ 0.001 用 3 位小数（如 p=0.134）；
      p < 0.001 用科学计数法并保留 3 位有效数字（如 p=2.04e-4、p=3.71e-9，
      指数去前导零）。
    - precision=n（int，如 5）：统一 n 位精度——p ≥ 0.001 用 n 位小数
      （如 p=0.20042）；p < 0.001 用科学计数法保留 n 位有效数字
      （如 p=6.6144e-4）。既保留精确值、又避免 "0.00066" 这种丢精度的假精确。
      下溢兜底（p<1e-300/非有限）不受 precision 影响，始终输出 p<1e-300。

    说明：星号（ns/*/**/***/****）照常由 p_to_stars 给出；凡出现具体 p 值处
    一律报实际计算值；precision 也可经 build_stats_report/format_legend 的
    p_precision 参数统一设置，无需逐处传参。
    """
    # 下溢兜底阈值 1e-300：覆盖 p=0 / IEEE 最小正双精度 2.225e-308 / 一切
    # 实质为零的正 p 值（v2.0.10 修复：旧版仅 p<=0 命中，导致 2.225e-308
    # 走假精度分支输出 p=2.22e-308）
    if np.isnan(p):
        return "NA"            # 不可计算（如 n<3 时 Shapiro-Wilk 返回 NaN）
    if p < 1e-300 or not np.isfinite(p):
        return f"p={_P_UNDERFLOW}"
    # 优先用显式 precision 参数，其次用全局精度开关（供报告/图注统一设置）
    prec = precision if precision is not None else _FORMAT_P_PRECISION
    # 防御：precision 必须是正整数（≥1）。0 在科学计数法分支会生成
    # f"{p:.{-1}e}" 直接抛 ValueError；显式报错比静默崩溃更利于排查。
    if prec is not None and prec < 1:
        raise ValueError(
            f"format_p precision 必须为正整数(>=1)，收到 {precision!r}")
    if prec is None:
        if p < 0.001:
            # 科学计数法保留 3 位有效数字，并去掉指数前导零（2.04e-04 → 2.04e-4）
            mantissa, exp = f"{p:.2e}".split("e")
            return f"p={mantissa}e{int(exp)}"
        return f"p={p:.3f}"
    # precision = n：≥0.001 → n 位小数；<0.001 → n 位有效数字科学计数法
    if p < 0.001:
        mantissa, exp = f"{p:.{prec - 1}e}".split("e")
        return f"p={mantissa}e{int(exp)}"
    return f"p={p:.{prec}f}"

def _auto_stat_method(test):
    """把 build_stats_report 的 test 名映射到 format_legend 默认方法文字。

    v2.6.x：format_legend 旧版把 stat_method 硬编码成
    "One-way ANOVA with Tukey's post hoc test"，2 组 t 检验若不显式传
    stat_method 就会写出错误的 ANOVA 描述（已在 2 组 LCN2 图中实测踩坑）。
    现改为：stat_method 不传时，由 test 名自动推导；都不传则回退到
    多组 ANOVA（本技能最常见图型）的干净表述。
    """
    return {
        "anova_tukey": "One-way ANOVA + Tukey",
        "anova": "One-way ANOVA + Tukey",
        "ttest": "Unpaired t-test",
        "paired_ttest": "Paired t-test",
        "welch": "Welch t-test",
        "mannwhitney": "Mann-Whitney U test",
        "survival": "log-rank test",
        "nested": "Nested ANOVA",
        "chi2": "Chi-square test",
        "twoway": "Two-way ANOVA",
    }.get(test, "One-way ANOVA + Tukey")


def format_legend(description, n, pairwise, error_type="mean ± SEM",
                  stat_method=None, test=None,
                  star_scale="*p<0.05, **p<0.01, ***p<0.001, ****p<0.0001",
                  p_precision=None):
    """
    生成投稿级 Figure Legend 文字块（含各组比较的具体 p 值）。

    为什么图注要写具体 p 值：审稿人和期刊编辑普遍要求星号之外给出精确
    数值（许多期刊明确要求正文或图注报告实际 p 值）。星号只反映阈值区间，
    具体 p 值才完整传递统计信息。

    参数：
        description : 图内容描述（如 "TNF-α secretion in control and drug-treated groups"）
        n           : 每组样本量。**各组相同时**传 int（如 6）；
                      **各组不同时传 list**（如 [8, 4, 6]），图注自动写成
                      "n=4–8 per group"（v2.0.39 体检修复：旧版传 min(n) 会
                      在 n 不等时写成 "n=4 per group"，与事实不符，属学术误导）
        pairwise    : [(label_i, label_j, p_value), ...]，与统计结果一致
        error_type  : 误差线类型说明
        stat_method : 统计方法描述（None 时由 test 推导，都不传回退 ANOVA）
        test        : 与 build_stats_report 同款 test 名（"ttest"/"anova_tukey"/
                      "survival"/...）；仅当 stat_method=None 时用于自动推导
                      方法文字，避免 2 组图写出 ANOVA 错误描述
        star_scale  : 星号阈值说明
        p_precision : p 值精度（int，如 5）→ 统一 n 位：p≥0.001 用 n 位小数，
                      p<0.001 用 n 位有效数字科学计数法；None=默认（3 位/3 sig）。

    返回：可直接粘贴进论文的图注字符串。
    """
    if stat_method is None:
        stat_method = _auto_stat_method(test) if test else "One-way ANOVA + Tukey"
    with _fmt_p_precision(p_precision):
        parts = []
        for a, b, p in pairwise:
            parts.append(f"{a} vs {b} {format_p(p)} ({p_to_stars(p)[0]})")
        comp_text = "; ".join(parts)
        if isinstance(n, (list, tuple, np.ndarray)):
            nn = [int(v) for v in n]
            if len(set(nn)) == 1:
                ntxt = f"n={nn[0]} per group"
            else:
                ntxt = f"n={min(nn)}–{max(nn)} per group"
        else:
            ntxt = f"n={int(n)} per group"
        return (
            f"Figure. {description}. Data are {error_type}, {ntxt}. "
            f"{stat_method}: {comp_text}. {star_scale}."
        )

def mean_sem(values):
    """Mean ± SEM。空数组返回 (nan, nan)。"""
    a = np.asarray(values, dtype=float)
    if a.size == 0:
        return np.nan, np.nan
    return a.mean(), a.std(ddof=1) / np.sqrt(a.size)

def mean_sd(values):
    """Mean ± SD。"""
    a = np.asarray(values, dtype=float)
    if a.size == 0:
        return np.nan, np.nan
    return a.mean(), a.std(ddof=1)

def _default_out_dir():
    """跨平台默认输出目录。

    类 Unix 沙箱环境保留 /sandbox/workspace/output（向后兼容）；Windows 等
    无该目录的平台回退到 当前工作目录/output，避免意外生成 C:\\sandbox 目录。
    """
    if os.name != "nt" and os.path.isdir("/sandbox/workspace"):
        return "/sandbox/workspace/output"
    return os.path.join(os.getcwd(), "output")

def save_figure(fig, name, out_dir=None, dpi=300, close=True, formats=("png", "pdf"),
                pad_inches=0.04):
    """
    双格式输出：PNG（预览/投稿位图）+ PDF（矢量，期刊常用）。
    文件名自动拼接：{name}.png / {name}.pdf

    out_dir=None 时自动探测：类 Unix 沙箱 → /sandbox/workspace/output；
    否则 → 当前工作目录/output（Windows 友好，避免 C:\\sandbox 意外目录）。

    pad_inches (默认 0.04)：在 bbox_inches="tight" 之外再留一道安全边距。
    显著性 bracket 用 clip_on=False 画在轴外，极个别场景下 tight 计算可能
    贴边裁掉标注；加 0.04in 余量可稳妥兜住，对成品留白影响可忽略。
    """
    if out_dir is None:
        out_dir = _default_out_dir()
    os.makedirs(out_dir, exist_ok=True)
    saved = []
    for fmt in formats:
        path = os.path.join(out_dir, f"{name}.{fmt}")
        fig.savefig(path, dpi=dpi, bbox_inches="tight", pad_inches=pad_inches)
        saved.append(path)
    if close:
        plt.close(fig)
    return saved

# ---- 常用统计封装（与 references/statistics-guide.md 对应）----

def ttest_two_groups(a, b, paired=False):
    """两组比较。返回 (statistic, p_value, 方法名)。正态性不满足时改用非参数。"""
    a, b = np.asarray(a, dtype=float).ravel(), np.asarray(b, dtype=float).ravel()
    if len(a) < 2 or len(b) < 2:
        raise ValueError("每组至少需要 2 个观测才能做 t 检验（存在 n<2 的组）")
    if paired:
        if len(a) != len(b):
            raise ValueError(
                f"配对 t 检验要求两组长度一致（实际 {len(a)} vs {len(b)}）")
        # v2.5.3 零方差防御：配对全同值数据 ttest_rel 返回 NaN → 按均值差给结论
        if np.var(a) == 0 and np.var(b) == 0:
            same = abs(float(np.mean(a)) - float(np.mean(b))) < 1e-12
            return (0.0, 1.0 if same else 0.0, "Paired t-test (degenerate)")
        stat, p = stats.ttest_rel(a, b)
        return stat, p, "Paired t-test"
    # v2.5.3 零方差防御：两组合并零方差（如归一化后全为 0/全同值）时
    # ttest_ind 除零返回 NaN → 按均值差给确定性结论，不再崩/静默 NaN
    if np.var(a) == 0 and np.var(b) == 0:
        same = abs(float(np.mean(a)) - float(np.mean(b))) < 1e-12
        return (0.0, 1.0 if same else 0.0, "t-test (degenerate: zero variance)")
    # 小样本非正态检查（n<30 时）
    if min(len(a), len(b)) < 30:
        sa = stats.shapiro(a)[1] if len(a) >= 3 else 1.0
        sb = stats.shapiro(b)[1] if len(b) >= 3 else 1.0
        if sa < 0.05 or sb < 0.05:
            stat, p = stats.mannwhitneyu(a, b, alternative="two-sided")
            return stat, p, "Mann-Whitney U"
    # 方差齐性（Levene）决定 pooled vs Welch t 检验
    lev_p = stats.levene(a, b, center="mean")[1]
    stat, p = stats.ttest_ind(a, b, equal_var=(lev_p >= 0.05))
    return stat, p, ("Welch t-test" if lev_p < 0.05 else "Unpaired t-test")

def oneway_anova_tukey(groups, labels, var_equal="assumed", posthoc="auto"):
    """
    多组比较：One-way ANOVA + 事后检验（纯 scipy 实现，无需 statsmodels）。

    Tukey HSD 的 p 值来自学生化极差分布：
        q = |mean_i - mean_j| / sqrt(MSE / n_harmonic)
        p = 1 - studentized_range.cdf(q, k, df_within)
    其中 MSE 为组内均方（合并方差），df_within = N - k。

    var_equal 参数（v2.5.8，方差不齐处理，对齐 GraphPad Prism 8+）：
      "assumed"（默认）：假设方差齐性 → 标准 One-way ANOVA + Tukey HSD
                （向后兼容，与旧版行为完全一致）
      "welch"  ：不假设方差齐性 → Welch ANOVA（Welch-Satterthwaite 校正 df）
                 事后检验由 posthoc 参数决定（Prism 勾选"不假设标准差相等"）
      "auto"   ：先做齐性检验（Levene center='median'，即 Brown-Forsythe，
                 Prism 推荐），p<0.05 判方差不齐 → 自动切 Welch；否则回落标准

    posthoc 参数（v2.5.9，仅对 Welch 分支生效；assumed 分支永远是 Tukey）：
      "auto"（默认）   ：max(组内 n) > 50 → "games_howell"；
                          否则 → "dunnett_t3"（Prism 推荐：<50 用 Dunnett T3）
      "games_howell"   ：Games-Howell（q 带 √((sᵢ²/nᵢ+sⱼ²/nⱼ)/2)，p 来自
                          学生化极差分布，每对独立 Welch-Satterthwaite df）
      "dunnett_t3"     ：Dunnett T3（Welch t 统计量 + 未取整 Welch-Satterthwaite
                          df，单步 Sidak 式校正 p = 1−(1−p_raw)^m，
                          m = k(k−1)/2；等价于 SMM 分布，Dunnett 1980）
      "welch_t"        ：不校正——每对直接 Welch 校正 t 检验（Prism
                          "Don't correct for multiple comparisons" 选项）

    返回 dict: {方法名, anova_p, pairwise: [(label_i, label_j, p), ...],
               f_stat, df1, df2, welch: bool, posthoc: str,
               var_test: {name, stat, p} 或 None}
    （新增字段向后兼容；默认 assumed 时 f_stat/df1/df2 也一并给出）
    """
    groups = [np.asarray(g, dtype=float).ravel() for g in groups]
    k = len(groups)
    if k < 2:
        raise ValueError("One-way ANOVA + Tukey 至少需要 2 组数据")
    if len(labels) != k:
        raise ValueError("labels 长度必须与组数一致")
    if any(len(g) == 0 for g in groups):
        raise ValueError("存在空组，ANOVA 无法计算")
    if any(len(g) < 2 for g in groups):
        raise ValueError("每组至少需要 2 个观测才能做 ANOVA + Tukey（存在 n=1 的组）")
    N = sum(len(g) for g in groups)
    df_within = N - k
    # v2.5.3 零方差防御：归一化/全同值数据（如处理组全为 0）组内合并方差为 0，
    # f_oneway 与 Tukey 的 q 值均除零崩溃 → 按均值差异给出确定性结论
    # （各组均值全同 → p=1.0；存在均值差 → p=0.0），不再抛异常/静默 NaN。
    mse = sum((len(g) - 1) * np.var(g, ddof=1) for g in groups) / df_within
    if not np.isfinite(mse) or mse <= 0:
        means = [float(np.mean(g)) for g in groups]
        same = all(abs(m - means[0]) < 1e-12 for m in means)
        pairwise = [(labels[i], labels[j],
                     (1.0 if abs(means[i] - means[j]) < 1e-12 else 0.0))
                    for i in range(k) for j in range(i + 1, k)]
        return {"method": "One-way ANOVA + Tukey (degenerate: zero within-group variance)",
                "anova_p": (1.0 if same else 0.0), "pairwise": pairwise,
                "f_stat": float("nan"), "df1": None, "df2": None,
                "welch": False, "posthoc": "tukey", "var_test": None}
    # ---- 齐性检验（v2.5.8）：供 auto 判定与报告使用 ----
    # center='median' = Brown-Forsythe 检验（对异常值更稳健，Prism 推荐；
    # 报告段落与此保持一致，见 _report_anova_tukey）。
    var_test = None
    try:
        lev_w, lev_p = stats.levene(*groups, center="median")
        if np.isfinite(lev_p):
            var_test = {"name": "Levene (Brown-Forsythe, center=median)",
                        "stat": float(lev_w), "p": float(lev_p)}
    except Exception:  # noqa: BLE001  # 齐性检验失败不影响主分析
        var_test = None
    use_welch = (var_equal == "welch") or (
        var_equal == "auto" and var_test is not None and var_test["p"] < 0.05)

    if use_welch:
        # ---- Welch ANOVA（标准 Welch 1951，纯 scipy）----
        #  w_i = n_i/s_i²,  W=Σw,  ȳ̃=Σw·ȳ/W
        #  F = [Σw(ȳ−ȳ̃)²/(k−1)] / [1 + 2(k−2)λ/(k²−1)],  λ=Σ(1−w/W)²/(n−1)
        #  df1 = k−1,  df2 = (k²−1)/(3λ)
        ns = np.array([len(g) for g in groups], dtype=float)
        means = np.array([g.mean() for g in groups])
        vv = np.array([g.var(ddof=1) for g in groups])
        wgt = ns / vv
        W = wgt.sum()
        yt = (wgt * means).sum() / W
        lam = ((1.0 - wgt / W) ** 2 / (ns - 1.0)).sum()
        df1 = float(k - 1)
        df2 = float((k * k - 1.0) / (3.0 * lam))
        f_w = float(((wgt * (means - yt) ** 2).sum() / df1)
                    / (1.0 + 2.0 * (k - 2) * lam / (k * k - 1.0)))
        p_w = float(stats.f.sf(f_w, df1, df2))
        # ---- 事后检验选择（v2.5.9，Prism 推荐）----
        if posthoc == "auto":
            ph = "games_howell" if float(ns.max()) > 50 else "dunnett_t3"
        elif posthoc in ("games_howell", "dunnett_t3", "welch_t"):
            ph = posthoc
        else:
            raise ValueError(
                f"posthoc 参数仅支持 auto/games_howell/dunnett_t3/welch_t，"
                f"收到 {posthoc!r}")
        vi = vv / ns
        m_pairs = k * (k - 1) // 2
        pairwise = []
        for i in range(k):
            for j in range(i + 1, k):
                df_ws = (vi[i] + vi[j]) ** 2 / (
                    vi[i] ** 2 / (ns[i] - 1.0) + vi[j] ** 2 / (ns[j] - 1.0))
                if ph == "games_howell":
                    # q 带 √((vᵢ+vⱼ)/2)，p 来自学生化极差分布（每对独立 df）
                    q_gh = abs(means[i] - means[j]) / np.sqrt((vi[i] + vi[j]) / 2.0)
                    p = float(1.0 - stats.studentized_range.cdf(q_gh, k, df_ws))
                else:
                    # Dunnett T3 与 welch_t 共用 Welch t 统计量（不带 /2）
                    t_w = abs(means[i] - means[j]) / np.sqrt(vi[i] + vi[j])
                    p_raw = float(2.0 * stats.t.sf(t_w, df_ws))
                    p = p_raw if ph == "welch_t" \
                        else float(1.0 - (1.0 - p_raw) ** m_pairs)
                pairwise.append((labels[i], labels[j], p))
        ph_name = {"games_howell": "Games-Howell",
                   "dunnett_t3": "Dunnett T3",
                   "welch_t": "Welch t (uncorrected)"}[ph]
        return {"method": f"Welch ANOVA + {ph_name}",
                "anova_p": p_w, "f_stat": f_w, "df1": df1, "df2": df2,
                "pairwise": pairwise, "welch": True, "posthoc": ph,
                "var_test": var_test}

    # ---- 标准 One-way ANOVA + Tukey（假设方差齐性，向后兼容）----
    f, anova_p = stats.f_oneway(*groups)
    # 组内均方 MSE。Tukey HSD 事后检验（Tukey-Kramer，纯 scipy 实现）：
    # 对每一对 (i, j) 单独用其两组样本量计算 q 统计量，
    #   q_ij = |mean_i − mean_j| / sqrt(MSE · (1/n_i + 1/n_j) / 2)
    # 这是标准 Tukey-Kramer（非均衡设计精确），与 scipy 早期 statsmodels
    # pairwise_tukeyhsd 等价的逐对公式；均衡设计 (n_i=n_j) 下退化为原
    # 调和均数写法，结果完全一致（向后兼容）。

    pairwise = []
    for i in range(k):
        for j in range(i + 1, k):
            ni, nj = len(groups[i]), len(groups[j])
            q = abs(np.mean(groups[i]) - np.mean(groups[j])) / \
                np.sqrt(mse * (1.0 / ni + 1.0 / nj) / 2.0)
            p = 1.0 - stats.studentized_range.cdf(q, k, df_within)
            pairwise.append((labels[i], labels[j], float(p)))
    return {"method": "One-way ANOVA + Tukey", "anova_p": anova_p,
            "f_stat": float(f), "df1": float(k - 1), "df2": float(df_within),
            "pairwise": pairwise, "welch": False, "posthoc": "tukey",
            "var_test": var_test}


def nested_anova(df, outer, inner, value):
    """Nested one-way ANOVA（嵌套单因素方差分析，v2.4.5 NEW）。

    **核心：以内层单元均值为分析单元**（如动物数/培养皿数，而非观测数），
    避免假重复（pseudoreplication）——同一内层单元内的多次测量不是独立样本。
    F 检验的分母用**单元间变异**（MS_unit），而非观测内变异。

    参数：
        df    : pandas DataFrame（长格式，每行一个观测）
        outer : 外层分组列名（如 "treatment" / "method"）
        inner : 内层嵌套列名（如 "mouse" / "dish"，单元=该列的每个水平）
        value : 观测值列名

    返回 dict：
        {
          "method"   : 方法描述
          "F"/"df_between"/"df_within"/"anova_p" : 组间检验（df_within=单元自由度）
          "pairwise" : [(label_i, label_j, p), ...]（Tukey，误差=单元间变异）
          "unit_means": {组: 单元均值数组}      # 分析单元
          "n_units"  : {组: 单元数}
          "n_obs"    : {组: 观测数}
          "mean"     : {组: 观测均值}（展示用，柱高）
          "sem_units": {组: 单元均值 SEM}（展示用，误差棒）
          "variance" : {"outer": %, "unit": %, "within": %} 变异分解
        }
    """
    import pandas as _pd
    df = _pd.DataFrame(df).dropna(subset=[value]).copy()
    df[outer] = df[outer].astype(str)
    df[inner] = df[inner].astype(str)
    gs = list(dict.fromkeys(df[outer]))          # 数据出现顺序
    k = len(gs)

    unit_means, n_units, n_obs, mean, sem_units = {}, {}, {}, {}, {}
    # 方差分量累加
    ss_outer = ss_unit = ss_within = 0.0
    grand = float(df[value].mean())
    N_obs = int(len(df))
    for g in gs:
        gdf = df[df[outer] == g]
        n_obs[g] = int(len(gdf))
        mean[g] = float(gdf[value].mean())
        units = []
        for u, udf in gdf.groupby(inner):
            units.append(float(udf[value].mean()))
            ss_unit += len(udf) * (float(udf[value].mean()) - mean[g]) ** 2
            ss_within += float(((udf[value] - float(udf[value].mean())) ** 2).sum())
        ss_outer += n_obs[g] * (mean[g] - grand) ** 2
        um = np.asarray(units, dtype=float)
        unit_means[g] = um
        n_units[g] = int(len(um))
        sem_units[g] = float(um.std(ddof=1) / np.sqrt(len(um))) if len(um) > 1 else 0.0

    N_unit = sum(n_units.values())
    df_between = k - 1
    df_unit = N_unit - k
    df_within = N_obs - N_unit
    ms_outer = ss_outer / df_between if df_between > 0 else 0.0
    ms_unit = ss_unit / df_unit if df_unit > 0 else 0.0
    F = ms_outer / ms_unit if ms_unit > 0 else float("nan")
    anova_p = float(1.0 - stats.f.cdf(F, df_between, df_unit)) \
        if np.isfinite(F) else float("nan")

    # Tukey 事后（误差 = 单元间变异 ms_unit；逐对 Tukey-Kramer 公式，
    # 单元数 n_i/n_j 不均衡时仍精确，与 oneway_anova_tukey 一致）
    groups = [unit_means[g] for g in gs]
    pairwise = []
    for i in range(k):
        for j in range(i + 1, k):
            ni, nj = len(groups[i]), len(groups[j])
            q = abs(groups[i].mean() - groups[j].mean()) \
                / np.sqrt(ms_unit * (1.0 / ni + 1.0 / nj) / 2.0)
            p = 1.0 - stats.studentized_range.cdf(q, k, df_unit)
            pairwise.append((gs[i], gs[j], float(p)))

    ss_tot = ss_outer + ss_unit + ss_within
    variance = {"outer": ss_outer / ss_tot * 100,
                "unit": ss_unit / ss_tot * 100,
                "within": ss_within / ss_tot * 100} if ss_tot > 0 \
        else {"outer": 0.0, "unit": 0.0, "within": 0.0}

    return {"method": "Nested one-way ANOVA (units as analysis units)",
            "F": F, "df_between": df_between, "df_within": df_unit,
            "anova_p": anova_p, "pairwise": pairwise,
            "unit_means": unit_means, "n_units": n_units, "n_obs": n_obs,
            "mean": mean, "sem_units": sem_units, "variance": variance}


# ---- 样本点大小自适应（v2.0.12 新增）----

def auto_dot_size(avg_n, n_groups=1, base=5.0, ref_n=4, ref_groups=3,
                  alpha_g=0.25, min_size=2.0, max_size=5.0):
    """
    个体散点**面积**自适应（scatter 的 s 参数，单位 points²）。

    统一规则（v2.0.33 重构，v2.0.34 加组数因子，v2.2.2 加大幅度，
    v2.2.3 重新优化：基准前移，avg_n 从 4 起即开始调小）：
    点径由「每组样品量的平均值 avg_n」与「分组数 n_groups」共同决定
    **边长**（pt），再平方为面积；边长夹在 [min_size, max_size] =
    **[2.0, 5.0] pt**（用户指定：最大 5、最小 2）：
        pt = clip(base × sqrt(ref_n / avg_n) × (ref_groups/n_groups)^alpha_g,
                  2.0, 5.0)
        s  = pt²
    - **基准 ref_n=4（v2.2.3 前移，原 8）**：avg_n=4、3 组（因子=1）时
      pt = base = 5.0 满点（上限）——**avg_n 从 4 增大即开始下降**，
      4→8 是敏感段（5.0→3.54，肉眼可见调小）；
    - 样本量项 sqrt(ref_n/avg_n)：指数 0.5，**主导**；
    - 组数项 (ref_groups/n_groups)^alpha_g：组数多（柱子多、每柱更窄）→
      点小；组数少 → 点大。alpha_g=0.25（仍小于样本量指数 0.5）；
      ref_groups=3 为基准（3 组时因子=1）。
    整体不超出 [2.0, 5.0] pt。

    本函数是 common_point_size 的**单组/默认兜底**版本：逐组调用时 avg_n 取
    本组 n（单组即平均）、n_groups 默认 1（单组语义，因子=(3/1)^0.25≈1.32，
    被 5pt 上限兜底）。**多组图务必先用 common_point_size(total_n, n_groups)
    算好统一边长、再以 dot_size=pt² 显式传入**——确保整图点径一致、严格按
    「平均每组样本量 × 组数」调节（v2.0.33 用户要求：所有样品点共用同一
    规则、最小 2.0 最大 5.0 pt）。

    示例（base=5，n_groups=3，返回面积 s）：avg_n=4→pt5→s25、
    avg_n=8→pt3.54→s12.5、avg_n=16→pt2.5→s6.25、avg_n=32→pt2→s4
    """
    avg_n = max(int(avg_n), 1)
    n_groups = max(int(n_groups), 1)
    pt = (base * np.sqrt(ref_n / avg_n)
          * (ref_groups / n_groups) ** alpha_g)
    pt = float(np.clip(pt, min_size, max_size))
    return pt ** 2

def auto_point_size(n, n_groups=1, base=5.0, ref_n=4, ref_groups=3,
                    alpha_g=0.25, min_size=2.0, max_size=5.0):
    """
    个体散点**边长**自适应（单组 / 逐组兜底版，单位 pt，s = point_size²）。

    v2.0.33 起与 common_point_size 统一公式，v2.0.34 加组数因子，
    v2.2.3 重新优化（基准 ref_n 8→4，max 5pt、min 2pt）：
        point_size = clip(base × sqrt(ref_n / n) × (ref_groups/n_groups)^alpha_g,
                          2.0, 5.0)
    n=ref_n（默认 4）、n_groups=3（基准）→ 5pt（上限）。显式传 point_size
    时永远用自己的值。组数项指数 alpha_g=0.25 小于样本量指数 0.5。

    注：多组图的标准入口是 common_point_size(total_n, n_groups)（按平均每组
    样本量 × 组数算统一值）；本函数仅作单组兜底（n_groups 默认 1），切勿在
    多组图里逐组调用导致点径不一。
    """
    n = max(int(n), 1)
    n_groups = max(int(n_groups), 1)
    s = (base * np.sqrt(ref_n / n)
         * (ref_groups / n_groups) ** alpha_g)
    return float(np.clip(s, min_size, max_size))

def common_point_size(total_n, n_groups, base=5.0, ref_n=4, ref_groups=3,
                      alpha_g=0.25, min_size=2.0, max_size=5.0):
    """
    全图统一样本点**边长**（pt，v2.0.13 用户指定规则，图型封装默认；
    v2.0.14 上限由 6 收紧到 5；v2.0.34 加组数因子；v2.2.2 加大幅度；
    v2.2.3 重新优化——基准前移，avg_n 从 4 起即开始调小）。

    由**所有样本点总数 total_n 与分组数 n_groups** 确定唯一值，整图所有
    样本点共用（用户要求：不用面积算、不看某组 n、同图必须统一）：
        avg_n = total_n / n_groups          # 平均每组样本量
        point_size = clip(base × sqrt(ref_n / avg_n)
                          × (ref_groups/n_groups)^alpha_g, 2.0, 5.0)
    - **基准 ref_n=4（v2.2.3 前移，原 8）**：avg_n=4、3 组（因子=1）→
      pt=5.0 满点（上限）——**avg_n 从 4 增大即开始下降**，4→8 是敏感段
      （5.0→3.54）；样本量项指数 0.5，**主导**；
    - 组数项 (ref_groups/n_groups)^alpha_g：组数多（柱子多、每柱更窄）→
      点小；组数少 → 点大。alpha_g=0.25（仍小于样本量指数 0.5）；
      ref_groups=3 为基准（3 组因子=1）。
    夹在 [min_size, max_size] = **[2.0, 5.0] pt**（用户指定：最大 5、
    最小 2；动态范围 2.5×）。

    示例（3 组因子=1）：avg_n=4→5.0（上限）、avg_n=8→3.54、
    avg_n=16→2.5、avg_n=32→2.0（下限）
    """
    n_groups = max(int(n_groups), 1)
    total_n = max(int(total_n), 1)
    avg_n = total_n / n_groups
    s = (base * np.sqrt(ref_n / avg_n)
         * (ref_groups / n_groups) ** alpha_g)
    return float(np.clip(s, min_size, max_size))

def auto_dot_alpha(total_n, n_groups, alpha_max=1.0, alpha_min=0.5):
    """
    按平均每组样本量自适应散点**填充透明度**（v2.0.15 新增）。

    样本多时镜像抖动下仍难免重叠，不透明点会把下层数据完全盖住；透明度
    让重叠区域呈现"越密越深"的密度感，既保留全部数据点又不掩盖信息。
    点越密 → 越透明；点少保持不透明（视觉与旧版一致）。

        alpha = clip(1.4 - 0.055 × avg_n, alpha_min, alpha_max)
        avg_n=4  → 1.0（不透明，向后兼容小样本）
        avg_n=8  → 0.96（基本不透明）
        avg_n=15 → 0.58（n=15 常规样本量，半透明）
        avg_n≥18 → 0.50（下限，样本再密也不再降）

    注意：透明度只作用于点的**填充面**（facecolor=to_rgba(color, alpha)），
    黑色描边保持不透明——重叠处可见密度，点的轮廓依然清晰（v2.0.15）。
    """
    n_groups = max(int(n_groups), 1)
    total_n = max(int(total_n), 1)
    avg_n = total_n / n_groups
    return float(np.clip(1.4 - 0.055 * avg_n, alpha_min, alpha_max))

def common_bar_width(n_subgroups, fill=0.85, gap_ratio=0.15,
                     max_width=0.62, min_width=0.06):
    """分组柱状图**子柱宽度**自适应（v2.3.7 新增，与 common_point_size 对称）。

    解决"组数多后各子柱/box 互相重叠"：固定 width（如 0.35）在 k 根子柱时
    总宽 k×width 超过 x 间距 1.0 即重叠（k=4 → 1.4 > 1.0，必叠）。

    物理约束模型（GraphPad Prism 同思路：子柱总宽受限 + 子柱间留间隙）：
        k 根子柱，单根宽 w，柱间 gap = gap_ratio × w
        总宽 = k·w + (k-1)·gap_ratio·w ≤ fill（fill 为 x 间距的可用比例）
        ⇒ w = fill / (k + (k-1)·gap_ratio)
    结果夹在 [min_width, max_width]（max_width 取单组柱宽 0.62，与 prism_bars
    默认一致；k=1 时 w = fill/(1) = 0.85 → 被 max_width 夹到 0.62）。

    示例（fill=0.85, gap_ratio=0.15）：
        k=1 → 0.62（夹 max，单柱）    k=2 → 0.395
        k=3 → 0.258                  k=4 → 0.191
        k=6 → 0.126                  k=8 → 0.094
    总宽恒 ≤ 0.85×间距，任何 k 都不重叠。

    参数：
        n_subgroups : int  每个 x 位置的子柱数（分组数）
        fill        : float  子柱总宽占 x 间距的比例上限（默认 0.85，留边距）
        gap_ratio   : float  柱间间隙 = gap_ratio × 柱宽（默认 0.15）
        max_width   : float  单根柱宽上限（默认 0.62 = prism_bars 默认单柱宽）
        min_width   : float  单根柱宽下限（默认 0.06，组数极多时不至于消失）
    返回：float  单根子柱宽度（柱宽，非半径）
    """
    k = max(int(n_subgroups), 1)
    w = fill / (k + (k - 1) * gap_ratio)
    return float(np.clip(w, min_width, max_width))

def _scatter_overlap_pairs(ax, dot_size):
    """统计图中所有散点的**实际重叠对数**（矩形判据，v2.0.30 新增，
    v2.0.34 由圆形判据改为矩形判据，与布局 `_conflict` 同口径）。

    背景：v2.0.30 起布局严格锁在柱宽/box 宽内（点绝不溢出），物理放不下
    （y 极密 / 柱窄+n 大）的重叠不再强行摊开，改由**透明度补偿**——先画点，
    再检测实际重叠，重叠越密透明度压得越低（v2.0.34：描边与填充同透明度）。

    判据与 jitter_offsets 内部的 _conflict 一致（矩形判据）：|Δx| < d_x 且
    |Δy| < d_y 视为重叠（d_x/d_y 由实际点径换算）。

    返回：(n_overlap, n_pairs, max_frac)——重叠对总数 / 全部点对数 /
    组内最大重叠密度（重叠最多那组的 pair_ov/n_pairs，供透明度映射用，
    避免被正常组摊薄——v2.0.30a 改进）。
    """
    d_x, d_y = _point_dxdy(ax, dot_size)
    n_overlap = n_pairs = 0
    max_frac = 0.0
    for coll in ax.collections:
        if not isinstance(coll, PathCollection):
            continue
        offs = coll.get_offsets()
        if len(offs) == 0:
            continue
        xs, ys = offs[:, 0], offs[:, 1]
        k = len(xs)
        n_pairs += k * (k - 1) // 2
        if k <= 1:
            continue
        # v2.5.5 性能修复：原 O(k²) 双循环（3×2000 点绘图 ~10s 中的大头，
        # 每次内层 numpy 标量运算都走 ma.core 慢路径）。改为排序 + 滑动
        # 窗口向量化——按 y 排序后，只有 y 差 < d_y 的后续点需比较 x
        # （searchsorted 一次定位窗口右边界，窗口内 numpy 向量化比较）。
        order = np.argsort(ys, kind="stable")
        xs_s, ys_s = xs[order], ys[order]
        right = np.searchsorted(ys_s, ys_s + d_y, side="right")
        pair_ov = 0
        for i in range(k):
            j_end = right[i]
            if j_end - i > 1:
                pair_ov += int(np.sum(np.abs(xs_s[i + 1:j_end] - xs_s[i]) < d_x))
        n_overlap += pair_ov
        max_frac = max(max_frac, pair_ov / (k * (k - 1) / 2))
    return n_overlap, n_pairs, max_frac

def _apply_overlap_alpha(ax, dot_size, dot_alpha, alpha_min=0.30):
    """    v2.0.30：检测散点实际重叠，按重叠密度压低填充透明度（物理放不下的补偿）。

    背景：布局已严格锁在柱宽/box 宽内（jitter_offsets v2.0.30，点绝不溢出），
    剩余重叠只可能来自 y 极密 / 柱窄+n 大的物理极限——此时摊开点会跑出 box 外
    （v2.0.29 教训：max_j 放宽到 0.9×width + x 强制分离不限宽，点溢出被用户
    否决），唯一视觉解法是**半透明**：重叠区呈现"越密越深"的密度感。
    v2.3.8：**描边始终不透明**（黑描边不跟随填充变透明，点轮廓保持清晰；
    反转 v2.0.34 的"边框跟随填充透明度"行为）。

    透明度映射：alpha_new = clip(alpha × (1 − 0.55 × 组内最大重叠密度), 0.30, alpha)。
    无重叠时返回原 alpha（常规图完全不受影响，保持不透明）。

    返回：应用后的 dot_alpha（供日志/后续使用）。
    """
    n_ov, n_pairs, max_frac = _scatter_overlap_pairs(ax, dot_size)
    if n_ov == 0 or n_pairs == 0:
        return dot_alpha
    new_alpha = max(alpha_min, dot_alpha * (1.0 - 0.55 * max_frac))
    for coll in ax.collections:
        if isinstance(coll, PathCollection) and len(coll.get_offsets()):
            fc = np.asarray(coll.get_facecolor())
            if len(fc):
                fc[:, 3] = new_alpha
                coll.set_facecolor(fc)
            # v2.3.8：描边**不跟随**填充变透明——保持不透明黑边，
            # 点的轮廓始终清晰（v2.0.34 曾同步压低，用户要求反转）
    return new_alpha

def _maybe_rotate_xticklabels(ax):
    """
    若 x 轴刻度标签放不下（文本宽度超过刻度间距），统一改为 45° 倾斜 +
    右对齐（v2.0.13）。

    判定：渲染后取每个 tick label 的文本宽度 w_i，与相邻刻度像素间距
    gap 比较；只要存在 w_i > gap × 1.0（标签宽度超过间距即算"放不下"），
    全部标签旋转 45°（ha='right'）。比"相邻 bbox 重叠"判据更稳健——
    窄画布下 matplotlib 会自动隐藏部分 tick 使 bbox 不重叠，但视觉上
    依然拥挤；文本宽度 vs 间距直接反映"放不放得下"。
    渲染失败/异常时静默跳过（不破坏出图）。
    """
    try:
        fig = ax.figure
        fig.canvas.draw()
        renderer = fig.canvas.get_renderer()
        ticks = ax.get_xticklabels()
        if len(ticks) < 2:
            return
        # 刻度像素间距（相邻 tick 的 x 坐标差的中位数）
        xs = [t.get_window_extent(renderer=renderer).x0 for t in ticks]
        gaps = [b - a for a, b in zip(xs, xs[1:]) if b - a > 0]
        if not gaps:
            return
        gap = float(np.median(gaps))
        # 文本宽度 vs 间距：任一标签放不下 → 全转 45°
        for t in ticks:
            w = renderer.get_text_width_height_descent(
                t.get_text(), t.get_fontproperties(), ismath=False)[0]
            if w > gap:
                for tt in ticks:
                    tt.set_rotation(45)
                    tt.set_horizontalalignment("right")
                return
    except Exception:
        pass   # 保守：检测失败不旋转，避免异常破坏出图

def jitter_offsets(ax, values, width=0.62, jitter_ratio=0.5, dot_size=None,
                   seed=None, min_sep=True, balanced=True, max_attempts=30):
    """
    柱宽内样本点布局——以柱中心为峰、向两侧对称衰减的自然抖动（默认带最小间距约束）。

    按 y 排序后以「0 为峰、向两侧对称衰减」的三角形分布为每个点确定初始
    水平偏移（中间密、两边疏），再叠加最小间距约束：仅当两点 y 极近且 x 过近
    （会重叠）时才做最小幅度的交替交错以分离。整体呈现"从中间向两边对称散开"
    的自然观感，且不偏一侧。

    balanced=True（默认，投稿强制规则，对齐 neuroresearch v2.0.2+）：
    改为**镜像均衡抖动**——左 n//2 点 = -uniform(0,max_j)，右 n//2 点 =
    +uniform(0,max_j)，n 奇数时 1 点**随机偏侧**（v2.0.31，左右差 ≤1）。
    左右点数**均衡**、对称不偏侧；分布为均匀而非中间密两边疏。
    v2.0.29：镜像初值之上**叠加最小间距约束**（min_sep=True 时）——n 大/
    柱窄时均匀分布点径 > 平均间距会重叠，冲突点沿 x 微调分离（左右
    归属不变）。v2.0.30：max_j 上限收紧回 width/2，**点绝不超柱/box 宽**
    （v2.0.29 的 0.9×width 曾致点溢出 box 被否决）。v2.0.31：微调改
    **随机方向+随机步长**、删除等距排开兜底（等差数列太规律），物理
    放不下的残余重叠由 _apply_overlap_alpha 透明度补偿（v2.0.30 机制）。
    min_sep=False 保持纯镜像（旧行为）。极端密集（如 n 远超柱宽可容纳）
    请用 layout="beeswarm" 多列展开、永不重叠。

    参数：
        ax          : 目标坐标轴（min_sep=True 时用于换算点直径）
        values      : 该组的原始测量值
        width       : 柱体宽度（数据坐标）
        jitter_ratio: 抖动范围占柱宽半宽的比例（0~1，默认 0.5 = 占柱宽
                      25%）。最终上限还会扣掉点半径（点径感知），保证点(含直径)
                      绝不越出所属柱/box 边界、也不溢出到相邻(紧贴)子柱；大样本量
                      时最多填满可用半宽，不再扩展到整柱宽（旧版宽度/2 扩展会导致溢出）
        dot_size    : scatter 的 s 参数（**面积，单位 points²**；min_sep 换算点径用）；
                      None = 按样本数自适应（v2.0.12，auto_dot_size）。
                      注意：此处的 dot_size 是「面积 s」，不是边长 pt；箱线/小提琴图
                      用 point_size² 转换后即为此面积值（v2.0.32 审查注记 #5）
        seed        : 随机种子（可复现）
        min_sep     : balanced=False 时有效：True=随机+最小间距（默认）；False=纯随机
        balanced    : True=镜像均衡（左右点数严格相等，默认）；False=中心为峰三角抖动
        max_attempts: 每点的随机尝试次数，超限后用空隙兜底

    返回：与 values 顺序一致的 x 偏移数组（叠加到柱中心 x 坐标上）。
    """
    values = np.asarray(values, dtype=float)
    n = len(values)
    if n == 0:
        return np.zeros(0)
    if dot_size is None:
        dot_size = auto_dot_size(n)
    max_j = width / 2 * jitter_ratio
    rng = np.random.default_rng(seed)

    if balanced:
        # 镜像均衡：左右各 n//2 点、距中心 uniform(0,max_j)；n 奇数时 1 点
        # **随机偏侧**（v2.0.31：不再强制居中，避免正中竖线感；左右差 ≤1，
        # 仍满足"左右均衡"投稿规则 v2.0.2+）。
        # v2.0.25：max_j 随 n 自适应扩展（n·d_x/2）。
        # v2.0.29：镜像初值之上**叠加最小间距约束**——冲突点**同侧内**
        # 微调分离（v2.0.29a 修正越线破坏左右均衡的 bug）。
        # v2.0.30（用户反馈"样本点跑出 box 外"）：**布局硬约束 = 点绝不超
        # 柱宽/box 宽**，max_j 上限收紧回 width/2。
        # v2.0.31（用户反馈"上一版本太有规律性很丑"）：**去规律化**——
        # ① 微调由固定交替步进（±(0.6+0.4k)·d_x 锯齿）改为**随机方向 +
        # 随机步长**，分布自然无锯齿；② **删除等距排开兜底**（等差数列
        # 最规律最丑），物理放不下时接受轻微重叠，由 _apply_overlap_alpha
        # 透明度补偿（v2.0.30 机制保留）；③ 奇数点随机偏侧不再居中；
        # ④ **初值采样避开中线带**（a ~ uniform(mid_b, max_j)），所有点
        # 与 box 中间严格分开（不贴 0、不排成正中竖线）。
        d_x, d_y = _point_dxdy(ax, dot_size)
        # v2.0.33 修复 grouped 外溢：抖动上限改为「点径感知」——扣掉点半径，
        # 保证点(含直径)绝不越出所属柱/box 边界；大样本量时只填满可用半宽
        # usable，绝不扩展到 width/2（旧版会推到柱边、直径溢出紧贴的相邻子柱）。
        # 与 beeswarm_offsets 的 max_off = width/2 - d_x/2 保持同一约束。
        half = width / 2.0
        # 用户要求：随机均匀分布锁定在柱/box 宽度的 0.75 以内（留出可见边距，
        # 且点径感知——再扣点半径保证点含直径也不越界）。大样本量时只填满
        # 该上限，绝不扩展到整柱宽（旧版 width/2 扩展会溢出紧贴的相邻子柱）。
        usable = min(half - d_x / 2.0, 0.75 * half)
        usable = max(usable, 0.0)
        max_j = min(max_j, usable)
        min_half = n * d_x / 2.0
        if min_half > max_j:
            max_j = usable
        mid_b = 0.6 * d_x                # 中线空隙：≥0.5·d_x 保证跨中线两侧
                                        # 最内侧点间距≥d_x，避免贴值簇跨侧重叠
        lo0 = mid_b if max_j > mid_b else 0.0   # 空间不足时回退到 0
        m = n // 2
        a = rng.uniform(lo0, max_j, m)
        xs0 = np.concatenate([-a, a])
        if n % 2 == 1:
            side = 1.0 if rng.random() < 0.5 else -1.0
            xs0 = np.append(xs0, side * rng.uniform(lo0, max_j))
        rng.shuffle(xs0)              # 打乱排列顺序（左/右数量不受影响）
        if not min_sep:               # min_sep=False：保持纯镜像（旧行为）
            return xs0
        # 镜像 + 最小间距（同侧内**随机**微调，v2.0.31 去锯齿规律）
        order = np.argsort(values, kind="stable")
        sv = values[order]
        xs = np.empty(n)
        placed = []
        for i, y in enumerate(sv):
            x = xs0[i]
            side = 1 if x > mid_b else (-1 if x < -mid_b else 0)
            lo, hi = ((-max_j, -mid_b) if side < 0
                      else ((mid_b, max_j) if side > 0 else (-max_j, max_j)))
            k = 0
            while _conflict(x, y, placed, d_x, d_y) and k < max_attempts:
                # v2.0.31：随机方向 + 随机步长（替代固定交替锯齿步进）
                direction = rng.choice([-1.0, 1.0])
                x = np.clip(x + direction * rng.uniform(0.6, 1.1) * d_x, lo, hi)
                k += 1
            if _conflict(x, y, placed, d_x, d_y):
                # 保证分离的兜底：在侧带[lo,hi]内扫描第一个与已放点距离≥点径
                # 的 x（样品点较少时带内必有空位，确保点间保持距离、绝不重叠；
                # 仅当物理放不下时才退回残余重叠由 _apply_overlap_alpha 补偿）
                span = max(hi - lo, 1e-9)
                n_cand = max(3, int(span / (d_x / 2.0)) + 1)
                cands = np.linspace(lo, hi, n_cand)
                rng.shuffle(cands)
                found = False
                for cand in cands:
                    if not _conflict(cand, y, placed, d_x, d_y):
                        x = cand
                        found = True
                        break
                if not found:
                    # 物理放不下：随机半点微抖兜底（残余重叠由透明度补偿）
                    x = np.clip(x + rng.uniform(-0.5, 0.5) * d_x, lo, hi)
            xs[i] = x
            placed.append((x, y))
        # v2.0.34：随机+微调仍可能失败（先放的点把侧带切成两段都 < 点径，
        # 第 3 个点扫描不到空位）。对仍冲突的侧带做"等距重排"兜底——该侧
        # 点按 y 排序后在侧带内均匀分布（±小抖动防锯齿），只要侧带放得下
        # 就绝不重叠（少量点场景必然放得下）；放不下（极端密集）才保留
        # 残余重叠由 _apply_overlap_alpha 透明度补偿。
        if mid_b > 0:
            for side_sign in (-1.0, 1.0):
                side_idx = [i for i in range(n)
                            if (xs[i] > 0) == (side_sign > 0)]
                if len(side_idx) <= 1:
                    continue
                ord_side = sorted(side_idx, key=lambda i: sv[i])
                # 检测该侧**任意点对**冲突（非相邻点也可能重叠，仅查相邻对
                # 会漏判，v2.0.34a）。
                # v2.5.5 性能修复：原实现 ia/ib 全点对 O(n²)——3×2000 点绘图
                # 30s。改为滑动窗口：按 y 排序后，只有 y 差 < d_y 的点对可能
                # 重叠，且窗口上限 64（y 窗口内点更多时物理必放不下，直接判定
                # 冲突触发等距重排兜底，重排本身 O(n log n)）。
                side_conflict = False
                for ia in range(len(ord_side)):
                    a = ord_side[ia]
                    ib = ia + 1
                    while ib < len(ord_side) and (ib - ia) <= 64 \
                            and (sv[ord_side[ib]] - sv[a]) < d_y:
                        if abs(xs[a] - xs[ord_side[ib]]) < d_x:
                            side_conflict = True
                            break
                        ib += 1
                    if side_conflict:
                        break
                if not side_conflict:
                    continue
                lo = (mid_b if side_sign > 0 else -max_j)
                hi = (max_j if side_sign > 0 else -mid_b)
                k = len(ord_side)
                step = (hi - lo) / (k - 1)
                if step < d_x:
                    continue   # 侧带放不下，保持现状（透明度兜底）
                max_jit = max(0.0, (step - d_x) / 2.0) * 0.5
                for t, i in enumerate(ord_side):
                    jit = (rng.uniform(-max_jit, max_jit)
                           if max_jit > 0 else 0.0)
                    xc = lo + t * step + jit
                    # 锁回侧带内：右侧 ≥ mid_b、左侧 ≤ -mid_b，保证跨中线
                    # 最内侧点间距 ≥ 2·mid_b ≥ d_x（抖动不得破坏中线空隙）
                    xs[i] = np.clip(xc, lo, hi)
        result = np.empty_like(xs)
        result[order] = xs
        return result

    if not min_sep:
        # 以柱中心为峰、向两侧对称衰减的三角形随机偏移（中间密、两边疏）
        return rng.triangular(-max_j, 0.0, max_j, n)

    # 随机 + 最小间距：按 y 排序逐个放置（y 接近的点优先满足间距）
    order = np.argsort(values, kind="stable")
    sv = values[order]
    d_x, d_y = _point_dxdy(ax, dot_size)

    # ---- 中心为峰：以 0 为峰、向两侧对称衰减的三角形分布做初值（中间密、两边疏）----
    if n == 1:
        base = np.array([0.0])
    else:
        base = rng.triangular(-max_j, 0.0, max_j, n)
    xs = np.empty(n)

    # ---- 最小间距修正：仅 y 极近且 x 过近时做交替小交错，保持整体对称 ----
    placed = []
    for i, y in enumerate(sv):
        x = base[i]
        k = 0
        while _conflict(x, y, placed, d_x, d_y) and k < max_attempts:
            # v2.0.31：随机方向 + 随机步长（替代固定交替锯齿步进）
            direction = rng.choice([-1.0, 1.0])
            x = np.clip(base[i] + direction * rng.uniform(0.6, 1.1) * d_x,
                        -max_j, max_j)
            k += 1
        # 极端密集仍冲突：在 [-max_j, max_j] 内扫描第一个不冲突位置兜底
        # （保证少量点分离）；仅物理放不下时退回随机半点微抖 + 透明度补偿
        if _conflict(x, y, placed, d_x, d_y):
            span = max(2.0 * max_j, 1e-9)
            n_cand = max(3, int(span / (d_x / 2.0)) + 1)
            cands = np.linspace(-max_j, max_j, n_cand)
            rng.shuffle(cands)
            found = False
            for cand in cands:
                if not _conflict(cand, y, placed, d_x, d_y):
                    x = cand
                    found = True
                    break
            if not found:
                x = np.clip(base[i] + rng.uniform(-0.5, 0.5) * d_x,
                            -max_j, max_j)
        xs[i] = x
        placed.append((x, y))

    # v2.0.34：随机+微调/扫描仍失败（先放的点把可用区间切成碎片、后续点
    # 扫描不到空位）时，做**全带等距重排**兜底——全部点按 y 排序在
    # [-max_j, max_j] 内均匀分布（±小抖动防锯齿，clip 回带内），只要带宽
    # 放得下就绝不重叠（少量点场景必然放得下）；放不下才保留残余重叠
    # 由 _apply_overlap_alpha 透明度补偿。
    if n > 1 and max_j > d_x:
        any_conflict = False
        for ia in range(n):
            for ib in range(ia + 1, n):
                a, b = ia, ib   # sv 已按 y 排序，索引即 y 序
                if (abs(sv[a] - sv[b]) < d_y
                        and abs(xs[a] - xs[b]) < d_x):
                    any_conflict = True
                    break
            if any_conflict:
                break
        if any_conflict:
            step = 2.0 * max_j / (n - 1)
            if step >= d_x:
                max_jit = max(0.0, (step - d_x) / 2.0) * 0.5
                for t in range(n):
                    jit = (rng.uniform(-max_jit, max_jit)
                           if max_jit > 0 else 0.0)
                    xs[t] = np.clip(-max_j + t * step + jit, -max_j, max_j)

    result = np.empty_like(xs)
    result[order] = xs
    return result

def _conflict(x, y, placed, d_x, d_y):
    """矩形判据：y 差 < 点径 且 x 差 < 点径 视为冲突（点圆接触）。

    v2.5.5 性能修复：所有调用方都按 y **升序**放置（sv 排序后逐个 append），
    placed 尾部 y 最大。从尾部向前扫：
      - 一旦 `y - py >= d_y`（更早的 py 更小、差更大），必不冲突 → 提前终止；
      - 窗口上限 64 防退化（全同 y 的极端密集场景，物理上点必重叠，漏判由
        等距重排兜底 + _apply_overlap_alpha 透明度补偿，不影响正确性）。
    原实现遍历整个 placed（O(n) 纯 Python），3×1000 点绘图 17s → 亚秒。
    """
    n = len(placed)
    for k in range(n - 1, max(n - 65, -1), -1):
        px, py = placed[k]
        if y - py >= d_y:      # 单调性：更早的点 y 更小，差更大，必不冲突
            break
        if abs(x - px) < d_x:
            return True
    return False

def beeswarm_offsets(ax, values, width=0.62, dot_size=None, seed=None):
    """
    Prism 风格样本点布局：按 y 值排序后轮转分配到多列，永远水平展开。

    为什么必须"永远展开"而不是"重叠时才错开"（蜂群贪心判据）：
    当数据在 y 方向足够分散（相邻点 y 差 > 点直径）时，蜂群判据认为无需
    错开，所有点会堆在柱中心成一条竖线——这是用户最容易嫌弃的观感。
    Prism 的实际行为是点始终在柱宽内展开成整齐多列。本函数按 y 排序后
    轮转（round-robin）分配到 2-4 列，列间距远大于点直径，因此视觉上
    稳定展开、永不退化为竖线，且列内点间距天然错开（同列点是隔列选取的）。

    参数：
        ax      : 目标坐标轴（用于换算点直径的数据单位）
        values  : 该组的原始测量值
        width   : 柱体宽度（数据坐标）
        dot_size: scatter 的 s 参数（点面积，points²）；
                  None = 按样本数自适应（v2.0.12，auto_dot_size）
        seed    : 保留参数（交替布局确定性展开，无需随机）

    返回：与 values 顺序一致的 x 偏移数组（叠加到柱中心 x 坐标上）。
    """
    values = np.asarray(values, dtype=float)
    order = np.argsort(values, kind="stable")
    sv = values[order]
    n = len(sv)
    xs = np.zeros(n)
    if n <= 1:
        result = np.empty_like(xs)
        result[order] = xs
        return result
    if dot_size is None:
        dot_size = auto_dot_size(n)

    # 点直径（英寸）→ x/y 方向的数据单位（基于 axes 实际显示尺寸）
    ax.figure.canvas.draw()
    d_inch = np.sqrt(dot_size) / 72.0
    bbox = ax.get_window_extent()
    dpi = ax.figure.dpi
    xlim, ylim = ax.get_xlim(), ax.get_ylim()
    d_x = d_inch * (xlim[1] - xlim[0]) / (bbox.width / dpi)
    d_y = d_inch * (ylim[1] - ylim[0]) / (bbox.height / dpi)
    max_off = width / 2 - d_x / 2
    if max_off <= 0:
        result = np.empty_like(xs)
        result[order] = xs
        return result

    # 列数：点少用 2 列，常规 3 列，点多最多 5 列（受柱宽限制）
    max_cols = max(1, int(width / d_x))
    if n <= 4:
        n_cols = 2
    elif n <= 10:
        n_cols = 3
    else:
        n_cols = min(5, max_cols)
    n_cols = min(n_cols, n)
    col_centers = np.linspace(-max_off, max_off, n_cols)

    placed = []
    for i, y in enumerate(sv):
        col = i % n_cols
        x = col_centers[col]
        # 冲突兜底：该列放不下（y 差过近）时顺移到下一空闲列
        k = 1
        while _conflict(x, y, placed, d_x, d_y) and k < n_cols * 2:
            x = col_centers[(col + k) % n_cols]
            k += 1
        xs[i] = x
        placed.append((x, y))
    result = np.empty_like(xs)
    result[order] = xs
    return result

def add_individual_dots(ax, x, values, color=None, width=0.62, dot_size=None,
                        edgecolor="black", linewidth=0.75, seed=None,
                        layout="jitter", jitter_ratio=0.5, min_sep=True,
                        balanced=True, alpha=None, marker="o"):
    """
    在柱状图上叠加个体样本点。

    主题一致性原则：样本点颜色默认取自对应柱体（color=None 时从
    ax.patches 自动匹配第 x 根柱子的颜色），保证"点即柱"的视觉统一。

    点大小（v2.0.12）：**整图必须统一**（期刊规范）——同一张图的样本点
    必须同大。dot_size=None 时按本组 n 自适应（auto_dot_size，单组图适用）；
    多组柱状图请用 prism_bars()（自动以全图最大 n 统一）或先算好统一值
    `dot_size=auto_dot_size(max(len(g) for g in groups))` 再逐组传入，
    **切勿逐组默认自适应导致整图点大小不一**。

    布局选择（layout 参数）：
    - "jitter"（默认）：**镜像均衡抖动**（balanced=True，投稿强制规则，对齐
      neuroresearch v2.0.2+）——左 n//2 点 = 中心 - uniform，右 n//2 点 =
      中心 + uniform，n 奇数时 1 点居中；**左右点数严格均衡**、左右对称不偏侧；
      balanced=False 则退回中心为峰的三角抖动（中间密两边疏）。
    - "beeswarm"：按 y 排序轮转分配到多列，规整展开、永不重叠。
    用 jitter_ratio 控制抖动范围占柱宽比例（0~1，默认 0.5 更紧凑，防点溢出相邻组）。

    注意：调用前必须已设置好 ylim（间距约束/蜂群布局需要正确的坐标换算）。

    参数：
        ax           : 目标坐标轴
        x            : 该组柱子的 x 坐标（数值）
        values       : 该组的原始测量值
        color        : 点填充色；None 时自动取柱体颜色
        alpha        : 点填充面透明度（0~1，1=不透明）。None 时默认 1.0
                       （单组调用不知道全图 n，不自动透明）；多组柱状图请用
                       prism_bars(dot_alpha=...) 传入 auto_dot_alpha 全图统一值。
                       描边**始终不透明**（v2.3.8：反转 v2.0.34，黑描边不再跟随
                       填充变透明——点轮廓清晰可辨）
        layout       : "jitter"（镜像均衡抖动，默认）或 "beeswarm"（多列展开）
        min_sep      : balanced=False 时有效（是否启用最小间距约束）
        balanced     : layout="jitter" 时是否强制左右点数均衡（默认 True）
        marker       : 点形状（matplotlib marker，默认 "o" 圆点；
                       nested 图可按内层单元轮转 marker 区分簇，v2.4.7）
        其余参数     : 见 jitter_offsets / beeswarm_offsets / scatter
    """
    if color is None:
        # 从已绘制的柱体 patch 中匹配该 x 位置的柱子颜色
        color = "black"
        for patch in ax.patches:
            cx = patch.get_x() + patch.get_width() / 2
            if abs(cx - x) < 1e-6:
                color = patch.get_facecolor()
                break
    if dot_size is None:
        dot_size = auto_dot_size(len(values))
    if alpha is None:
        alpha = 1.0
    if layout == "beeswarm":
        offsets = beeswarm_offsets(ax, values, width=width,
                                   dot_size=dot_size, seed=seed)
    else:  # 默认 jitter：镜像均衡抖动（左右点数严格均衡）
        offsets = jitter_offsets(ax, values, width=width,
                                 jitter_ratio=jitter_ratio, dot_size=dot_size,
                                 seed=seed, min_sep=min_sep, balanced=balanced)
    ax.scatter(x + offsets, values, s=dot_size,
               facecolor=to_rgba(color, alpha),
               edgecolor=to_rgba(edgecolor, 1.0),
               linewidth=linewidth, zorder=5, marker=marker)

# ---- 箱线图 / 小提琴图 + 多组显著性括号 ----

# ---- 文件读取层（v2.7.5 健壮性）：编码/分隔符自动回退 + 中文可行动报错 ----

_ENCODINGS = ("utf-8-sig", "utf-8", "gbk", "gb18030", "big5", "latin-1")
_SEPARATORS = (",", "\t", ";", "|")
_NA_TOKENS = {"", "-", "--", "—", "nd", "n/a", "na", "nan", "null", "none",
              "无", "缺失", ".", "/"}
_EXCEL_EXTS = (".xlsx", ".xls", ".xlsm")


def _to_numeric(series):
    """把任意列尽量转成 float（转不动的条目 → NaN，绝不抛异常）。

    处理：首尾空格；千分位逗号（仅"数字,三位数字"形态，避免误伤 1,5
    这类欧式小数）；常见缺失占位符（ND / — / 缺失 / NA / null 等）。
    """
    import pandas as pd
    s = series.astype(str).str.strip()
    s = s.str.replace(r"(?<=\d),(?=\d{3}(\D|$))", "", regex=True)  # 1,234 → 1234
    s = s.mask(s.str.lower().isin(_NA_TOKENS))                     # 占位符 → NaN
    return pd.to_numeric(s, errors="coerce")


def _sep_name(sep):
    return {",": "逗号", "\t": "制表符 Tab", ";": "分号",
            "|": "竖线"}.get(sep, repr(sep))


def _friendly_missing(path):
    """文件不存在时的统一中文提示（替代裸 FileNotFoundError）。"""
    return (f"找不到数据文件：{path}\n"
            f"请检查：① 路径拼写是否正确 ② 文件是否已被移动或重命名 "
            f"③ 路径含中文或空格时是否加了引号 ④ 当前工作目录是否符合预期")


def _read_csv_robust(path, header=0):
    """读文本表格：先试探编码（兼容中文 GBK），再嗅探分隔符（兼容 Tab 导出）。

    返回 (DataFrame, note_or_None)。失败时抛**中文可行动**错误，
    而不是 pandas 的原始 traceback。
    """
    import pandas as pd
    last_err = None
    for enc in _ENCODINGS:
        try:
            df = pd.read_csv(path, header=header, encoding=enc)
        except UnicodeDecodeError as e:
            last_err = e                                   # 换一种编码重试
            continue
        except pd.errors.EmptyDataError as e:
            raise ValueError(
                f"文件是空的、或不含任何数据行：{path}\n"
                f"请检查文件是否被意外清空；若数据并非从第 1 行开始，"
                f"请确认表头行设置（当前 header={header}）。"
            ) from e
        except Exception as e:                             # noqa: BLE001
            last_err = e
            continue
        # 只解析出 1 列 → 多半分隔符不对，嗅探其它分隔符
        if df.shape[1] == 1:
            for sep in _SEPARATORS[1:]:
                try:
                    cand = pd.read_csv(path, header=header,
                                       encoding=enc, sep=sep)
                except Exception:                          # noqa: BLE001
                    continue
                if cand.shape[1] > 1:
                    return cand, f"分隔符已自动识别为 {_sep_name(sep)}"
        return df, None
    raise ValueError(
        f"无法读取文件：{path}\n"
        f"已尝试 {len(_ENCODINGS)} 种常见编码（含中文 GBK / GB18030）均失败。\n"
        f"建议：用 Excel 打开后「另存为」CSV UTF-8 格式再试。\n"
        f"最后错误：{type(last_err).__name__}: {last_err}"
    )


def _read_excel_robust(path, sheet=0, header=0):
    """读 Excel：缺 openpyxl / 格式不符（如 CSV 改名 .xlsx）都给可行动提示。"""
    import pandas as pd
    try:
        return pd.read_excel(path, sheet_name=sheet, header=header), None
    except ImportError as e:                               # 缺 openpyxl
        raise ImportError(
            "读取 Excel 需要 openpyxl；请在隔离 venv 中执行 "
            "`python -m pip install openpyxl`"
        ) from e
    except ValueError as e:                                # CSV 改名成 .xlsx
        raise ValueError(
            f"无法把 {path} 识别为 Excel 文件（多半是 CSV/TXT 直接改了扩展名）。\n"
            f"请确认文件真实格式；若实为文本表格，把扩展名改回 .csv 或 .txt 再读。\n"
            f"原始错误：{e}"
        ) from e
    except Exception as e:                                 # noqa: BLE001
        raise ValueError(
            f"读取 Excel 失败：{path}\n{type(e).__name__}: {e}"
        ) from e


def _read_any(path, sheet=0, header=0):
    """统一读取入口：先确认文件存在，再按扩展名分流 Excel / 文本表格。"""
    p = str(path)
    if not os.path.exists(p):
        raise FileNotFoundError(_friendly_missing(p))
    if p.lower().endswith(_EXCEL_EXTS):
        return _read_excel_robust(p, sheet=sheet, header=header)
    return _read_csv_robust(p, header=header)


def read_table(path, group_col=None, value_col=None, sheet=0, header=0):
    """从 CSV / Excel 读取数据，自动拆分组并返回建议的 y 轴标签。

    用于"用户上传文件 → 直接绘图"的场景，落实技能约定：
    **当数据来自文件、且用户未显式指定 y 轴标签时，自动用数值列的
    表头作为 ylabel 默认值**（经基础清洗），用户仍可在绘图时覆盖。

    健壮性（v2.7.5，针对"坏输入直接崩、不够傻瓜化"的评估意见）：
      - 编码自动回退：utf-8-sig / utf-8 / gbk / gb18030 / big5 / latin-1
        （Windows 版 Excel 另存的中文 CSV 默认 GBK，不再直接崩）
      - 分隔符嗅探：逗号 / 制表符 / 分号 / 竖线（Tab 导出的 .txt 直接可用）
      - 文件缺失 / 空文件 / 格式不符 / 列名写错 → 中文可行动报错，
        并列出可用列，而非裸 traceback
      - 数值清洗：去首尾空格、去千分位逗号、ND/—/缺失 等占位符 → NaN
      - **绝不静默产出错误数据**：无法转数值的列会被忽略并写进 notes

    自动判别表型：
      - 长格式（long）：恰好一列"合理的"分组文本列 + ≥1 列数值。
        例：group=Control/Treated，值为 Relative LCN2 expression
        → groups 按分组列拆分；ylabel = 数值列表头（清洗后）。
      - 宽格式（wide）：每列即一个组（如 Control / Treated 两列）。
        → 每列一组；无单一"数值列名"，ylabel 回退为 None，
          由调用方沿用图型模板默认或请用户指定。

    **分组列判定（防止静默错误，v2.7.5 关键修复）**：文本列只有在去重取值
    数落在 [2, max(2, 行数//2)] 区间内才被当作分组变量——否则像"备注"
    "编号"这类自由文本/常量列会被误判成分组列，导致整张表被错误重塑
    （旧版会把含备注列的宽表误判为长表，静默丢掉真正的分组）。

    参数：
        path       : CSV / TXT 或 Excel（.xlsx/.xls/.xlsm）文件路径
        group_col  : 长格式的分组列名/索引；None = 自动选唯一合理分组列
        value_col  : 长格式的数值列名/索引；None = 自动选第一个数值列
        sheet      : Excel 工作表（名或索引），默认 0
        header     : 表头行，默认 0

    返回 dict：
        {"groups": list[list[float]], "labels": list[str],
         "ylabel": str | None, "format": "long" | "wide",
         "source": str, "notes": list[str]}
        notes：读取过程中的提示（自动识别的分隔符、被忽略的列等）。
        **画图前应把 notes 展示给用户**——被忽略的列可能意味着
        数据没被完整使用，属学术严谨性范畴，不可静默吞掉。
    """
    import pandas as pd

    df, read_note = _read_any(path, sheet=sheet, header=header)

    # 丢弃全空行、pandas 自动生成的 "Unnamed: 0" 索引列
    df = df.dropna(how="all").reset_index(drop=True)
    df = df.loc[:, ~df.columns.astype(str).str.startswith("Unnamed")]

    if df.shape[1] == 0:
        raise ValueError(
            f"文件 {path} 没有解析出任何可用列。\n"
            f"可能原因：文件只有表头没有数据、整表为空、"
            f"或表头行设置不对（当前 header={header}）。"
        )

    cols = list(df.columns)

    def _clean(s):
        return " ".join(str(s).split())               # 去换行、合并多空格

    def _resolve(col, what):
        """列名或列索引 → 列名；找不到时列出可用列（替代裸 KeyError）。"""
        if isinstance(col, int) and col not in cols:
            if 0 <= col < len(cols):
                return cols[col]
            raise ValueError(
                f"{what} 列索引 {col} 越界：文件只有 {len(cols)} 列 {cols}"
            )
        if col not in cols:
            raise ValueError(
                f"找不到{what}列 {col!r}；文件可用列：{cols}\n"
                f"注意列名区分大小写，且会被自动清洗（多余空格已合并）。"
            )
        return col

    notes = [read_note] if read_note else []

    # 逐列尝试转数值：能转出 ≥1 个有效数字的是数据列，否则是文本列
    num_map, text_cols = {}, []
    for c in cols:
        conv = _to_numeric(df[c])
        if conv.notna().sum() >= 1:
            num_map[c] = conv
        else:
            text_cols.append(c)

    # 分组列候选：取值数太少（常量列）或太多（ID / 自由文本）都不算分组变量
    n_rows = len(df)
    group_candidates = [
        c for c in text_cols
        if 2 <= df[c].nunique(dropna=True) <= max(2, n_rows // 2)
    ]

    # 用户显式指定分组列 / 数值列 → 无条件服从（并做存在性校验）
    gcol = _resolve(group_col, "分组") if group_col is not None else (
        group_candidates[0] if len(group_candidates) == 1 else None)
    if value_col is not None:
        value_col = _resolve(value_col, "数值")
        num_map[value_col] = _to_numeric(df[value_col])
        num_cols = [value_col]
    else:
        num_cols = list(num_map.keys())

    # 长格式：有分组列 + ≥1 数值列
    if gcol is not None and len(num_cols) >= 1:
        vcol = num_cols[0]
        vals = num_map.get(vcol, _to_numeric(df[vcol]))
        work = pd.DataFrame({"__g__": df[gcol].astype(str), "__v__": vals})
        groups = [g["__v__"].dropna().astype(float).tolist()
                  for _, g in work.groupby("__g__", sort=False)]
        labels = [str(l) for l in df[gcol].drop_duplicates().tolist()]
        ylabel = _clean(vcol)
        fmt = "long"
        dropped = [c for c in cols if c not in num_cols and c != gcol]
    else:
        # 宽格式：每个可转数值的列即一组
        if not num_cols:
            raise ValueError(
                f"文件 {path} 中没有任何一列能转成数值。\n"
                f"请检查数据列是否混入了单位（如 '1.2 mg'）或文字说明；"
                f"若有，请拆成纯数值列后再读。"
            )
        groups = [num_map[c].dropna().astype(float).tolist() for c in num_cols]
        labels = [_clean(c) for c in num_cols]
        ylabel = None
        fmt = "wide"
        dropped = [c for c in cols if c not in num_cols]

    if dropped:
        notes.append(
            f"已忽略无法转成数值的列 {dropped}——若它们是有效数据，"
            f"请检查是否混入了单位或文字说明。"
        )

    return {
        "groups": groups,
        "labels": labels,
        "ylabel": ylabel,
        "format": fmt,
        "source": str(path),
        "notes": notes,
    }


def read_excel_sheets(path, header=0, sheets=None, skip_empty=True):
    """读取单个 Excel 文件的多个工作表，逐表按 Prism 规则解析。

    **用于"用户把多组数据放在同一 Excel 的不同 sheet"的场景**：一次调用
    即可把所有 sheet 解析成与 read_table 完全一致的 dict 结构，直接
    喂给 compose_panel_figure 做合并面板图。

    每个 sheet 独立走 read_table 的表型自动判别（长/宽格式、ylabel 默认
    取数值列表头）；sheet 名作为面板标题建议（info["sheet"]），source
    改写为 "文件名::Sheet名" 以便溯源。

    健壮性（v2.7.5）：文件缺失、缺 openpyxl、CSV 改名成 .xlsx、
    sheet 名/索引写错 → 均抛中文可行动错误并列出可用 sheet 名，
    不再抛 pandas 原始 traceback。

    参数：
        path       : .xlsx/.xls/.xlsm 文件路径
        header     : 表头行，默认 0
        sheets     : 要读取的 sheet（名/索引列表）；None（默认）= 全部
        skip_empty : True（默认）跳过全空 sheet

    返回 list[dict]：每个元素 = read_table 返回值 + 额外字段
        "sheet"  : 该工作表名（str）
        "source" : "路径::Sheet名"（便于面板标题/溯源）
    顺序与 Excel 中 sheet 顺序一致（或 sheets 指定顺序）。
    """
    import pandas as pd
    p = str(path)
    if not os.path.exists(p):
        raise FileNotFoundError(_friendly_missing(p))
    try:
        xls = pd.ExcelFile(p)
    except ImportError as e:                           # 缺 openpyxl
        raise ImportError(
            "读取 Excel 需要 openpyxl；请在隔离 venv 中执行 "
            "`python -m pip install openpyxl`"
        ) from e
    except ValueError as e:                            # CSV 改名成 .xlsx
        raise ValueError(
            f"无法把 {p} 识别为 Excel 文件（多半是 CSV/TXT 直接改了扩展名）。\n"
            f"请确认文件真实格式后再读。\n原始错误：{e}"
        ) from e
    except Exception as e:                             # noqa: BLE001
        raise ValueError(f"打开 Excel 失败：{p}\n{type(e).__name__}: {e}") from e

    raw = xls.sheet_names if sheets is None else list(sheets)
    # 索引 → 真实 sheet 名（越界/写错都给可行动提示）
    names = []
    for s in raw:
        if isinstance(s, int) and s not in xls.sheet_names:
            if 0 <= s < len(xls.sheet_names):
                names.append(xls.sheet_names[s])
            else:
                raise ValueError(
                    f"工作表索引 {s} 越界：文件只有 "
                    f"{len(xls.sheet_names)} 个工作表 {xls.sheet_names}"
                )
        else:
            if s not in xls.sheet_names:
                raise ValueError(
                    f"找不到工作表 {s!r}；文件可用工作表：{xls.sheet_names}"
                )
            names.append(s)

    out = []
    for sname in names:
        df = pd.read_excel(xls, sheet_name=sname, header=header)
        if skip_empty and df.dropna(how="all").empty:
            continue
        info = read_table(p, sheet=sname, header=header)
        info["sheet"] = sname
        info["source"] = f"{p}::{sname}"
        out.append(info)
    return out


def prism_bars(ax, data, labels, palette="okabe_ito", width=0.62,
               error_type="sem", show_points=True, point_size=None,
               alpha=0.55, capsize=3, dot_alpha=None):
    """
    Prism 风格**分组柱状图**（Mean±SEM/SD + 个体散点），整图封装。

    v2.0.12 起为 Column/Grouped 表"带散点柱状图"的标准画法：
    - **点大小全图统一**：point_size=None 时用 `common_point_size(total_n,
      n_groups)` 计算唯一值——由所有样本点总数与分组数确定（平均每组
      样本量），夹在 [2.0, 5.0] pt；整图所有散点同大，绝不逐组各算各的
    - 误差线：Mean±SEM（默认）或 Mean±SD，柱体半透明 + 黑描边；
      **error bar 单独绘制且 zorder=6 > 散点 zorder=5**，保证误差线
      始终位于样本点图层之上、不被散点遮盖（v2.0.14 用户指定）
    - 配色：色盲安全色板，逐柱上色
    - x 轴刻度标签若重叠，自动旋转 45°（v2.0.13）

    参数：
        ax          : matplotlib Axes（建议先 apply_prism_theme()）
        data        : list[array-like]，每组原始观测值（与 labels 一一对应）
        labels      : list[str]，分组标签
        palette     : 色板名（"okabe_ito" 默认）或直接传颜色列表
        error_type  : "sem"（默认，均值标准误）或 "sd"（标准差）
        show_points : 是否叠加个体散点（默认 True，期刊规范）
        point_size  : 散点边长（pt）；None = common_point_size 统一计算（默认）
        alpha       : 柱体填充透明度（默认 0.55，与 prism_boxplot 的 box_alpha
                      一致，半透明；降低以露出背景网格、与箱线/小提琴保持统
                      一视觉重量。黑描边不受影响，始终不透明）
        dot_alpha   : 散点填充面透明度（0~1）；None = 按全图平均每组样本量
                      自适应（auto_dot_alpha：n 大 → 越透明，防重叠掩盖；
                      n 小 → 不透明）。边框同样跟随该透明度（v2.0.34）
        capsize     : 误差棒 cap 长度
    返回：ax
    """
    data = [np.asarray(g, dtype=float) for g in data]
    # v2.5.5：过滤非有限值（NaN/Inf 测量缺失）——否则 allv.min()/max() 为
    # NaN/Inf → set_ylim 崩溃（"Axis limits cannot be NaN or Inf"）。
    data = [g[np.isfinite(g)] for g in data]
    n_groups = len(data)
    if len(labels) != n_groups:
        raise ValueError(
            f"labels 数量（{len(labels)}）与组数（{n_groups}）不一致——"
            "每个数据组需要对应一个组名")
    if isinstance(palette, (list, tuple)) and len(palette) > 0:
        colors = list(palette)[:n_groups]
    else:
        seq = palette_sequence(palette if isinstance(palette, str) else "okabe_ito")
        colors = (seq * ((n_groups // len(seq)) + 1))[:n_groups]  # 组数超色板时循环取色
    # 全图统一点大小：由总样本数÷分组数确定唯一值（同一张图必须统一，
    # 范围 [2.0, 5.0] pt，v2.0.13 规则；上限 v2.0.14 由 6 收紧到 5）
    if point_size is None:
        point_size = common_point_size(sum(len(g) for g in data), n_groups)
    dot_size = point_size ** 2   # scatter 的 s 参数（面积 = 边长²）
    # 散点填充透明度：n 大 → 越透明（防重叠掩盖数据），n 小 → 不透明（v2.0.15）
    if dot_alpha is None:
        dot_alpha = auto_dot_alpha(sum(len(g) for g in data), n_groups)
    # v2.0.29 关键修复：**先固定 xlim 与 ylim 再画点**——此前逐柱绘制时
    # xlim/ylim 随柱体与数据逐步扩展（第 1 根柱画点时 xlim 仅单柱宽、ylim
    # 仅该组数据高），jitter 的点径换算 d_x/d_y 按当时的窄范围算小 → 前几组
    # 点挤在一起、最后一组才正常。统一范围后所有组共享一致的 d_x/d_y。
    # v2.0.39（体检发现）：ylim 下限不再硬编码 0——fold change / ΔCt 等
    # 含负值的数据柱体会被切底；下限取 min(0, 数据最小值×1.15)，全负数据
    # 上限回落到 0 附近，正负混合时双向留白。全正数据行为与旧版完全一致。
    allv = np.concatenate(data) if len(data) and sum(len(g) for g in data) \
        else np.array([0.0])
    ax.set_xlim(-0.5, n_groups - 0.5)
    ax.set_ylim(min(0.0, allv.min() * 1.15), max(0.0, allv.max() * 1.15))
    for i, g in enumerate(data):
        if len(g) == 0:
            continue   # v2.5.5：空组（过滤后全 NaN/Inf）跳过，不画柱，位置保留
        m = g.mean()
        if len(g) == 1:
            err = 0.0   # v2.5.5：n=1 组无变异，误差棒 0（此前 std(ddof=1)=NaN）
        elif error_type == "sd":
            err = g.std(ddof=1)
        else:
            err = g.std(ddof=1) / np.sqrt(len(g))
        # 仅填充半透明、黑描边保持完全不透明（alpha 整体生效会让边框也变灰）
        ax.bar(i, m, width=width, facecolor=to_rgba(colors[i], alpha),
               edgecolor="black", linewidth=0.75, zorder=2)
        if show_points:
            add_individual_dots(ax, i, g, color=colors[i], width=width,
                                dot_size=dot_size, alpha=dot_alpha)
        # error bar 单独绘制且 zorder=6 > 散点 zorder=5，确保误差线位于
        # 样本点图层之上，不被散点遮盖（v2.0.14 用户指定）
        ax.errorbar(i, m, yerr=err, fmt="none", ecolor="black",
                    capsize=capsize, lw=0.75, capthick=0.75, zorder=6)
    # v2.0.30：布局锁在柱宽内后，物理放不下的重叠用透明度补偿（只改填充面，
    # 黑描边不透明；零重叠时原样返回，常规图不受影响）
    if show_points:
        dot_alpha = _apply_overlap_alpha(ax, dot_size, dot_alpha)
    # 组名刻度（v2.0.13：之前漏设导致 x 轴显示默认数值刻度、无组名标签）
    ax.set_xticks(range(n_groups))
    ax.set_xticklabels(labels)
    _maybe_rotate_xticklabels(ax)
    # v2.4.2：y 轴统一收尾（0.5 倍数刻度 + 顶部 ≤1.3×data_max + 顶标签），
    # 与 prism_boxplot/violin 一致——此前只 set_ylim(1.15×max) 导致顶刻度
    # 超出轴范围无标签（如 ylim=18.21、顶刻度 20 悬空）。
    finish_axes(ax, data_max=float(allv.max()))
    return ax


def prism_grouped_bars(ax, df, x_col, group_col, value_col,
                       palette="okabe_ito", width=None,
                       error_type="sem", show_points=True,
                       point_size=None, alpha=0.55, capsize=3,
                       dot_alpha=None, legend_outside=True,
                       legend_loc=None):
    """Prism 风格**分组柱状图整图封装**（Grouped 表：时间×药物 / 基因型×处理）。

    v2.3.6 新增——根治手写 Grouped 的三坑：
      ① 点大小全图统一（内置 common_point_size，不再依赖调用方手传 dot_size）
      ② legend 默认移到 ax 外右侧（`legend_outside=True`），不压柱子
      ③ xlim/ylim 画点前预设 + x 坐标映射返回（图上标注不再手记 ctrl_x/drug_x）
    v2.3.7 新增：子柱宽度自适应（`width=None` 时按 `common_bar_width(n_g)`
    自动算，组数多→柱窄，杜绝子柱重叠；显式传 width 仍可覆盖）。

    参数：
        ax          : matplotlib Axes（建议先 apply_prism_theme()）
        df          : pandas DataFrame，long-format（每行一个观测）
        x_col       : 横轴因子列名（如 "time"；其水平决定 x 刻度）
        group_col   : 分组因子列名（如 "drug"；其水平决定子柱颜色/图例）
        value_col   : 响应值列名（连续数值）
        palette     : 色板名或颜色列表
        width       : 子柱宽度；None = common_bar_width(n_groups) 自动算
                      （v2.3.7 默认，组数多自动变窄防重叠）
        error_type  : "sem"（默认）或 "sd"
        show_points : 是否叠加个体散点（默认 True）
        point_size  : 散点边长 pt；None = common_point_size 统一计算
        alpha       : 柱体填充透明度（默认 0.55）
        capsize     : 误差棒 cap 长度
        dot_alpha   : 散点填充透明度；None = 按样本量自适应
        legend_outside : legend 放 ax 外右侧（默认 True；False 则放图内右上）
        legend_loc     : 手动指定 legend 位置（覆盖 legend_outside）

    返回 dict（供 add_pairwise_brackets 标注用）：
        {"x_levels": list[str],          # x 轴因子水平（顺序=数据出现序）
         "group_levels": list[str],      # 分组因子水平（顺序=数据出现序）
         "positions": {group: np.ndarray},  # 每个分组在各 x 位置的柱中心 x
         "means": {group: np.ndarray},      # 每格均值
         "sems": {group: np.ndarray},       # 每格 SEM
         "n": {group: np.ndarray}}          # 每格样本数

    Example
    -------
    >>> import pandas as pd, numpy as np
    >>> import matplotlib.pyplot as plt
    >>> from scripts.prism_theme import (
    ...     apply_prism_theme, prism_grouped_bars, twoway_posthoc,
    ...     add_pairwise_brackets, save_figure)
    >>> rng = np.random.default_rng(0)
    >>> df = pd.DataFrame({"time": ["0h"]*12 + ["24h"]*12 + ["48h"]*12,
    ...                    "drug": ["Ctrl", "Drug"]*18,
    ...                    "value": rng.normal(10, 2, 36)})
    >>> apply_prism_theme()
    >>> fig, ax = plt.subplots()
    >>> res = prism_grouped_bars(ax, df, "time", "drug", "value")
    >>> ph = twoway_posthoc(df, "value ~ C(time)*C(drug)")
    >>> # 交互显著时:每个时间点内 Ctrl vs Drug 简单效应
    >>> if ph.get("type") == "simple_effects":
    ...     comps = []
    ...     for t_i, t in enumerate(res["x_levels"]):
    ...         key = f"time={t}: Ctrl vs Drug"
    ...         m = [p for d, p, _ in ph["comparisons"] if d == key]
    ...         if m:
    ...             comps.append((res["positions"]["Ctrl"][t_i],
    ...                           res["positions"]["Drug"][t_i], m[0]))
    ...     add_pairwise_brackets(ax, comps)
    >>> fig.savefig("grouped.png", dpi=300, bbox_inches="tight")
    """
    import pandas as _pd
    df = _pd.DataFrame(df)
    df = df.dropna(subset=[value_col]).copy()
    # 水平顺序 = 数据首次出现顺序（与 twoway_posthoc 比较键方向一致）
    x_levels = list(dict.fromkeys(df[x_col].astype(str)))
    g_levels = list(dict.fromkeys(df[group_col].astype(str)))
    n_x = len(x_levels)
    n_g = len(g_levels)

    # v2.3.7:子柱宽度自适应——width=None 时按组数自动算(组多→柱窄,防重叠)
    if width is None:
        width = common_bar_width(n_g)

    if isinstance(palette, (list, tuple)) and len(palette) > 0:
        colors = list(palette)[:n_g]
    else:
        seq = palette_sequence(palette if isinstance(palette, str) else "okabe_ito")
        colors = (seq * ((n_g // len(seq)) + 1))[:n_g]

    total_n = int(len(df))
    if point_size is None:
        point_size = common_point_size(total_n, n_x * n_g)
    dot_size = point_size ** 2
    if dot_alpha is None:
        dot_alpha = auto_dot_alpha(total_n, n_x * n_g)

    x = np.arange(n_x)
    # 画点前预设 xlim/ylim（防 jitter 的 d_x/d_y 漂移；负值数据下限自适应）
    ax.set_xlim(-0.5, n_x - 0.5)
    allv = df[value_col].to_numpy(dtype=float)
    allv = allv[np.isfinite(allv)]   # v2.5.5：inf 防御（NaN 已 dropna）
    if len(allv) == 0:
        allv = np.array([0.0])
    ax.set_ylim(min(0.0, allv.min() * 1.15), max(0.0, allv.max() * 1.15))

    positions = {g: np.full(n_x, np.nan) for g in g_levels}
    means = {g: np.full(n_x, np.nan) for g in g_levels}
    sems = {g: np.full(n_x, np.nan) for g in g_levels}
    ns = {g: np.full(n_x, np.nan) for g in g_levels}

    for g_i, g in enumerate(g_levels):
        xs = x + (g_i - (n_g - 1) / 2) * width
        positions[g] = xs.copy()
        for x_i, xv in enumerate(x_levels):
            sub = df[(df[x_col].astype(str) == xv)
                     & (df[group_col].astype(str) == g)][value_col]
            sub = sub.to_numpy(dtype=float)
            if len(sub) == 0:
                continue
            m = sub.mean()
            if len(sub) == 1:
                err = 0.0   # v2.5.5：n=1 子格无变异，误差棒 0（此前 std(ddof=1)=NaN）
            elif error_type == "sem":
                err = sub.std(ddof=1) / np.sqrt(len(sub))
            else:
                err = sub.std(ddof=1)
            means[g][x_i] = m
            sems[g][x_i] = err
            ns[g][x_i] = len(sub)
            ax.bar(xs[x_i], m, width=width,
                   facecolor=to_rgba(colors[g_i], alpha),
                   edgecolor="black", linewidth=0.75, zorder=2)
            if show_points:
                add_individual_dots(ax, xs[x_i], sub, color=colors[g_i],
                                    width=width, dot_size=dot_size,
                                    alpha=dot_alpha)
            ax.errorbar(xs[x_i], m, yerr=err, fmt="none", ecolor="black",
                        capsize=capsize, lw=0.75, capthick=0.75, zorder=6)

    # 图例:用**独立 Patch handle**显式传给 legend(v2.3.8 修复)。
    # 旧方案:往 ax.add_artist 塞 Rectangle 锚点 → ①没加 visible=False 时方块
    # 画在图上(x 轴上方),②加了 visible=False 后 legend 把不可见 artist 的
    # handle 整个丢弃 → 只剩文字没图示。显式 handles= 彻底解决:handle 是
    # 独立构造的 Patch,不沾 ax、不影响点大小检测、图例有颜色块。
    from matplotlib.patches import Patch as _Patch
    legend_handles = [_Patch(facecolor=c, edgecolor="black",
                             linewidth=0.75, label=g)
                      for g, c in zip(g_levels, colors)]

    if show_points:
        dot_alpha = _apply_overlap_alpha(ax, dot_size, dot_alpha)

    ax.set_xticks(x)
    ax.set_xticklabels(x_levels)
    _maybe_rotate_xticklabels(ax)
    # v2.4.2：y 轴统一收尾（同 prism_bars，顶刻度不再悬空）
    finish_axes(ax, data_max=float(allv.max()))
    if legend_outside and legend_loc is None:
        ax.legend(handles=legend_handles, frameon=False, fontsize=7,
                  bbox_to_anchor=(1.02, 0.5), loc="center left")
    elif legend_loc is not None:
        ax.legend(handles=legend_handles, frameon=False, fontsize=7,
                  loc=legend_loc)
    else:
        ax.legend(handles=legend_handles, frameon=False, fontsize=7)
    return {"x_levels": x_levels, "group_levels": g_levels,
            "positions": positions, "means": means,
            "sems": sems, "n": ns}


def prism_spaghetti(ax, df, x_col, group_col, value_col, subject_col,
                    palette="okabe_ito", error_type="sem", alpha=0.22,
                    lw_trace=0.7, lw_mean=1.6, ms=5, capsize=3,
                    colors=None, markers=None, legend=True,
                    legend_loc="upper right"):
    """Prism 风格**意大利面条图**（重复测量/时间轨迹，v2.5.12 新增）。

    同一受试者（subject_col）在不同时间点/处理水平（x_col）的观测连成一条
    半透明轨迹线，组均值（group_col）± 误差棒叠加在最顶层——重复测量数据
    的标准展示（个体轨迹 + 组趋势一目了然）。

    画布约定：重复测量/时间轨迹类图**默认用 wide 画板**（SKILL.md 画布
    规则 v2.5.11 用户偏好；横向更适合多时间点轨迹）。

    参数：
        ax          : matplotlib Axes（建议先 apply_prism_theme()）
        df          : pandas DataFrame，long-format
        x_col       : 横轴因子列（如 "time"，其水平决定 x 刻度）
        group_col   : 分组因子列（如 "group"，其水平决定颜色/图例）
        value_col   : 响应值列（连续数值）
        subject_col : 受试者 ID 列（同 ID 的观测连成一条轨迹）
        palette     : 色板名（"okabe_ito" 默认）或显式颜色列表
        error_type  : "sem"（默认）或 "sd"
        alpha       : 个体轨迹线透明度（默认 0.22，保证均值线可辨）
        lw_trace    : 个体轨迹线宽（默认 0.7）
        lw_mean     : 组均值线宽（默认 1.6）
        ms          : 组均值标记大小
        capsize     : 误差棒 cap 长度
        colors      : {group: color} 显式覆盖组颜色（None = 色板按序）
        markers     : {group: marker} 显式覆盖组标记（None = 默认循环）
        legend      : 是否画图例（默认 True）
        legend_loc  : 图例位置（默认 "upper right"）

    返回 dict：
        {"x_levels": list[str],        # x 轴水平（数据出现序）
         "group_levels": list[str],    # 分组水平（数据出现序）
         "means": {group: np.ndarray}, # 各组各时间点均值
         "sems": {group: np.ndarray},
         "n": {group: np.ndarray},     # 每组受试者数
         "colors": {group: str}}       # 组 → 颜色

    Example
    -------
    >>> rng = np.random.default_rng(0)
    >>> df = pd.DataFrame({
    ...     "group": ["WT"]*24 + ["KO"]*24,
    ...     "time": (["0h"]*8 + ["24h"]*8 + ["48h"]*8) * 2,
    ...     "subject": [f"WT-{i%8}" for i in range(24)] + [f"KO-{i%8}" for i in range(24)],
    ...     "value": rng.normal(10, 2, 48)})
    >>> apply_prism_theme()
    >>> fig, ax = plt.subplots(figsize=get_figsize("wide"))
    >>> res = prism_spaghetti(ax, df, "time", "group", "value", "subject")
    """
    d = df[[x_col, group_col, value_col, subject_col]].dropna().copy()
    d["_v"] = d[value_col].astype(float)
    x_levels = list(dict.fromkeys(d[x_col].astype(str)))
    g_levels = list(dict.fromkeys(d[group_col].astype(str)))
    colors_seq = palette_sequence(palette) if isinstance(palette, str) \
        else list(palette)
    markers_seq = ["o", "s", "^", "D", "v", "P", "X", "*"]
    colors = colors if colors is not None \
        else {g: colors_seq[i % len(colors_seq)] for i, g in enumerate(g_levels)}
    markers = markers if markers is not None \
        else {g: markers_seq[i % len(markers_seq)] for i, g in enumerate(g_levels)}
    x_pos = np.arange(len(x_levels))
    # 1) 个体轨迹（半透明细线，zorder 低）
    for g in g_levels:
        sub = d[d[group_col].astype(str) == g]
        for subj in dict.fromkeys(sub[subject_col].astype(str)):
            s = sub[sub[subject_col].astype(str) == subj]
            ys = [s.loc[s[x_col].astype(str) == t, "_v"].mean()
                  for t in x_levels]
            ax.plot(x_pos, ys, color=colors[g], alpha=alpha, lw=lw_trace,
                    zorder=1, solid_capstyle="round")
    # 2) 组均值 ± 误差棒（最顶层）
    means, sems, ns = {}, {}, {}
    for g in g_levels:
        sub = d[d[group_col].astype(str) == g]
        m_arr, e_arr, n_arr = [], [], []
        for t in x_levels:
            v = sub.loc[sub[x_col].astype(str) == t, "_v"]
            m_arr.append(float(v.mean()))
            n_arr.append(float(v.size))
            sd_v = float(v.std(ddof=1)) if v.size > 1 else 0.0
            e_arr.append(sd_v / np.sqrt(v.size) if error_type == "sem"
                         else sd_v)
        means[g] = np.array(m_arr)
        sems[g] = np.array(e_arr)
        ns[g] = np.array(n_arr)
        ax.errorbar(x_pos, means[g], yerr=sems[g], fmt="", ecolor="black",
                    elinewidth=1.0, capsize=capsize, zorder=5)
        ax.plot(x_pos, means[g], marker=markers[g], color=colors[g],
                lw=lw_mean, ms=ms, zorder=4, label=g)
    ax.set_xticks(x_pos)
    ax.set_xticklabels(x_levels)
    _maybe_rotate_xticklabels(ax)
    if legend:
        ax.legend(frameon=False, fontsize=8, loc=legend_loc)
    return {"x_levels": x_levels, "group_levels": g_levels,
            "means": means, "sems": sems, "n": ns, "colors": colors}

def prism_boxplot(ax, data, labels, palette="okabe_ito", width=0.55,
                  show_points=True, jitter=0.18, point_size=None,
                  box_alpha=0.55, showfliers=False, fliersize=4,
                  dot_alpha=None):
    """
    Prism 风格箱线图：中位数/IQR 箱 + whisker + 个体差异点（组色填充 + 黑描边）。

    封装 seaborn 的"正确用法"，规避试运行发现的坑：sns.boxplot 必须显式传
    palette= 才会让每个箱体按颜色方案上色；只靠后置 set_facecolor 会让所有
    箱体变成默认蓝。本函数已内置正确做法，调用方无需再管配色。

    参数（对应 Column / Grouped 表的"箱线图 + 散点"图型）：
        ax          : matplotlib Axes（建议先 apply_prism_theme()）
        data        : list[array-like]，每组原始观测值（与 labels 一一对应）
        labels      : list[str]，分组标签
        palette     : 色板名（"okabe_ito" 默认 / "paul_tol"）或直接传颜色列表
        show_points : 是否叠加个体散点（Prism 风格：组色填充 + 黑描边）
        jitter/point_size : 散点抖动比例 / 点大小（边长 pt）；
                            point_size=None（默认）用 common_point_size
                            （总样本数÷分组数，范围 [2.5,5] pt，v2.0.13；上限 v2.0.14 收紧到 5）
        dot_alpha   : 散点填充面透明度（0~1）；None = 按全图平均每组样本量
                      自适应（n 大 → 越透明，防重叠掩盖；v2.0.15）
        box_alpha   : 箱体填充透明度（默认 0.55，既显色又不抢数据）
        showfliers  : 是否画离群点（默认 False，离群点已由 show_points 散点呈现）
    返回：ax

    图层层级（v2.0.27-28 明确，防"线被点盖"）：箱体填充 zorder=2 < 个体散点
    zorder=3 < **中位线/须线/帽线/箱体边框 zorder=4**——箱线图的 whisker/
    median/cap 在语义上就是"误差范围与中心线"，加上 v2.0.28 重绘到顶层的
    箱体边框，全部最顶层可见，不被散点覆盖。
    """
    import pandas as pd
    import seaborn as sns
    data = [np.asarray(g, dtype=float) for g in data]
    # v2.5.5：过滤非有限值（NaN/Inf 测量缺失）——与 prism_bars 一致
    data = [g[np.isfinite(g)] for g in data]
    if len(labels) != len(data):
        raise ValueError(
            f"labels 数量（{len(labels)}）与组数（{len(data)}）不一致——"
            "每个数据组需要对应一个组名")
    n = len(data)
    if isinstance(palette, (list, tuple)) and len(palette) > 0:
        colors = list(palette)[:n]
    else:
        seq = palette_sequence(palette if isinstance(palette, str) else "okabe_ito")
        colors = (seq * ((n // len(seq)) + 1))[:n]  # 组数超色板时循环取色
    df = pd.DataFrame({"Group": np.repeat(labels, [len(g) for g in data]),
                       "Value": np.concatenate(data)})
    sns.boxplot(data=df, x="Group", y="Value", hue="Group", order=labels,
                width=width, showfliers=showfliers, palette=colors,
                fliersize=fliersize, legend=False,
                boxprops=dict(edgecolor="black", linewidth=0.75, zorder=2),
                medianprops=dict(color="black", linewidth=0.75, zorder=4),
                whiskerprops=dict(color="black", linewidth=0.75, zorder=4),
                capprops=dict(color="black", linewidth=0.75, zorder=4), ax=ax)
    # 兼容 seaborn 版本差异：0.12 的箱体在 ax.artists（Rectangle），
    # 0.13+ 的箱体是 PathPatch 存在 ax.patches（ax.artists 为空）。
    # 只靠 set_alpha 循环一个容器会静默失效（v2.0.8 修复）。
    box_patches = list(getattr(ax, "artists", []))
    box_patches += [p for p in ax.patches
                    if getattr(p, "get_facecolor", None) is not None]
    for patch in box_patches:
        patch.set_alpha(box_alpha)
    # v2.0.28（用户要求"box 的 border 也放最顶层"）：seaborn 的 boxprops 同时
    # 控制填充与边框（同一个 patch），无法单独把边框提到散点之上。方案：
    # 箱体填充保持 zorder=2（散点 3 之下、半透明不抢数据），边框用独立线框
    # **重绘到 zorder=4**——与 median/whisker/cap 同级且最后绘制（在最顶）。
    # 层级：箱体填充 2 < 散点 3 < 中位/须/帽/边框 4
    # 兼容：seaborn 0.12 箱体是 Rectangle（ax.artists）、0.13+ 是 PathPatch
    # （ax.patches）。v2.5.2：Rectangle 必须用 get_bbox()（返回数据坐标；
    # 其 get_path() 是单位矩形 (0,0)-(1,1)，get_extents() 恒为 1.0，会把边框
    # 画成整个轴框——与 v2.5.1 修 add_pairwise_brackets 同款坑，0.12 版本
    # 下 <1 数据必然爆发）；PathPatch 无 get_bbox，其 get_path() 即数据坐标
    for patch in box_patches:
        try:
            if hasattr(patch, "get_bbox"):
                ext = patch.get_bbox()                # Rectangle：数据坐标
            else:
                ext = patch.get_path().get_extents()  # PathPatch：path 即数据坐标
        except Exception:
            continue
        x0, y0, x1, y1 = ext.x0, ext.y0, ext.x1, ext.y1
        ax.plot([x0, x1, x1, x0, x0], [y0, y0, y1, y1, y0],
                color="black", lw=0.75, zorder=4)
    # v2.0.29：先固定 xlim 再画点（seaborn 的 xlim 无 padding 较窄，
    # 会导致 d_x 换算偏小、点挤在一起）
    ax.set_xlim(-0.5, len(data) - 0.5)
    if show_points:
        # 个体散点：手动 scatter + 镜像均衡抖动（左右点数严格均衡，投稿强制规则，
        # 对齐 neuroresearch v2.0.2+）；组色填充 + 黑描边（描边始终不透明，v2.3.8
        # 反转 v2.0.34 跟随填充行为）；线宽统一 0.75 pt
        # v2.0.13：点大小**全图统一**——由总样本数÷分组数确定唯一值（范围 [2.5,5]，
        # v2.0.14 上限由 6 收紧到 5）；v2.0.15：填充面透明度按 n 自适应防重叠
        jr = min(0.5, 2.0 * jitter / width) if width > 0 else 0.5   # jitter 参数映射到 jitter_ratio
        if point_size is None:
            point_size = common_point_size(sum(len(g) for g in data), len(data))
        if dot_alpha is None:
            dot_alpha = auto_dot_alpha(sum(len(g) for g in data), len(data))
        for gi, g in enumerate(data):
            offsets = jitter_offsets(ax, g, width=width, jitter_ratio=jr,
                                     dot_size=point_size ** 2, balanced=True)
            ax.scatter(gi + offsets, g, s=point_size ** 2,
                       facecolor=to_rgba(colors[gi], dot_alpha),
                       edgecolor=to_rgba("black", 1.0),
                       linewidth=0.75, zorder=3)
        # v2.0.30：物理放不下的重叠用透明度补偿（点锁在 box 宽内，绝不溢出）
        dot_alpha = _apply_overlap_alpha(ax, point_size ** 2, dot_alpha)
    # v2.0.32（审查修复 #3）：无显著性 bracket 时也要 y 轴收尾（与柱状图/bracket
    # 统一），保证刻度等分、下限对齐 0.5 倍数；不传 data_max（用当前 ylim 顶端为
    # 上限基准，cap=1.3×顶端，永不裁切须线/散点）
    finish_axes(ax)
    _maybe_rotate_xticklabels(ax)
    return ax

def prism_violin(ax, data, labels, palette="okabe_ito", width=0.8,
                 show_points=True, jitter=0.12, point_size=None,
                 viol_alpha=0.5, line_width=0.75, cut=3,
                 show_quartiles=True, dot_alpha=None):
    """
    Prism 风格小提琴图：核密度估计轮廓(半透明填充)+ 个体散点(组色填充 + 黑描边)。

    与 prism_boxplot 同一思路——封装 seaborn 正确用法：sns.violinplot 必须显式传
    palette= 才会按颜色方案上色(否则全蓝,同 box 的坑);inner=None 去掉默认箱线,
    改由 stripplot 叠加个体点 + 手动中位数/四分位参考线,符合"展示原始数据点"
    且标注关键统计量(中位数 + Q1/Q3)的期刊规范。

    本函数在 Phase 5 自我优化复盘中由真实使用(小提琴图任务)触发新增——技能越用越全。

    参数（对应 Column / Grouped 表的"小提琴图 + 散点"图型）：
        ax/ data/ labels/ palette : 同 prism_boxplot
        show_points : 叠加个体散点(组色填充 + 黑描边)
        jitter/ point_size/ viol_alpha/ line_width : 散点抖动/点大小/填充透明度/描边宽
            point_size=None（默认）用 common_point_size（总样本数÷分组数，
            范围 [2.5,5] pt，v2.0.13；上限 v2.0.14 收紧到 5）
        cut         : 核密度曲线向数据极值之外延伸的带宽倍数（seaborn 语义）。
                      默认 3（用户指定，较 seaborn 默认 2 延伸更明显）；设 0
                      则截断在最小/最大值（顶端/底端为平头）。
        show_quartiles : 是否在每组叠加中位数(实线)+ Q1/Q3(虚线)参考线。
                      True（默认）符合"标注关键统计量"的期刊规范；线段置于
                      散点之上(zorder 5/6)，黑描边清晰，不被个体点遮盖。
        dot_alpha   : 散点填充面透明度（0~1）；None = 按全图平均每组样本量
                      自适应（n 大 → 越透明，防重叠掩盖；v2.0.15）
    返回：ax
    """
    import pandas as pd
    import seaborn as sns
    from matplotlib.colors import to_rgba
    data = [np.asarray(g, dtype=float) for g in data]
    # v2.5.5：过滤非有限值（NaN/Inf 测量缺失）——与 prism_bars 一致
    data = [g[np.isfinite(g)] for g in data]
    if len(labels) != len(data):
        raise ValueError(
            f"labels 数量（{len(labels)}）与组数（{len(data)}）不一致——"
            "每个数据组需要对应一个组名")
    n = len(data)
    if isinstance(palette, (list, tuple)) and len(palette) > 0:
        colors = list(palette)[:n]
    else:
        seq = palette_sequence(palette if isinstance(palette, str) else "okabe_ito")
        colors = (seq * ((n // len(seq)) + 1))[:n]  # 组数超色板时循环取色
    df = pd.DataFrame({"Group": np.repeat(labels, [len(g) for g in data]),
                       "Value": np.concatenate(data)})
    sns.violinplot(data=df, x="Group", y="Value", hue="Group", order=labels,
                   width=width, palette=colors, legend=False,
                   inner=None, cut=cut, linewidth=line_width, ax=ax)
    # 半透明填充 + 黑色描边(逐组着色)
    for coll, color in zip(ax.collections[:n], colors):
        coll.set_facecolor(to_rgba(color, viol_alpha))
        coll.set_edgecolor("black")
        coll.set_linewidth(line_width)
    # v2.0.29：先固定 xlim 再画点（seaborn 的 xlim 无 padding 较窄，
    # 会导致 d_x 换算偏小、点挤在一起）
    ax.set_xlim(-0.5, len(data) - 0.5)
    if show_points:
        # 个体散点：手动 scatter + 镜像均衡抖动（左右点数严格均衡，投稿强制规则，
        # 对齐 neuroresearch v2.0.2+）；组色填充 + 黑描边（描边始终不透明，v2.3.8
        # 反转 v2.0.34 跟随填充行为）；线宽统一 0.75 pt
        # v2.0.13：点大小**全图统一**——由总样本数÷分组数确定唯一值（范围 [2.5,5]，
        # v2.0.14 上限由 6 收紧到 5）；v2.0.15：填充面透明度按 n 自适应防重叠
        jr = min(0.5, 2.0 * jitter / width) if width > 0 else 0.5   # jitter 参数映射到 jitter_ratio
        if point_size is None:
            point_size = common_point_size(sum(len(g) for g in data), len(data))
        if dot_alpha is None:
            dot_alpha = auto_dot_alpha(sum(len(g) for g in data), len(data))
        for gi, g in enumerate(data):
            offsets = jitter_offsets(ax, g, width=width, jitter_ratio=jr,
                                     dot_size=point_size ** 2, balanced=True)
            ax.scatter(gi + offsets, g, s=point_size ** 2,
                       facecolor=to_rgba(colors[gi], dot_alpha),
                       edgecolor=to_rgba("black", 1.0),
                       linewidth=0.75, zorder=3)
        # v2.0.30：物理放不下的重叠用透明度补偿（点锁在 box 宽内，绝不溢出）
        dot_alpha = _apply_overlap_alpha(ax, point_size ** 2, dot_alpha)
    # 中位数 + 四分位(Q1/Q3)参考线：手动绘制以精确控制层级与配色
    # (zorder 5/6 > 散点 3，确保关键统计量不被个体点遮盖; 遵循 v2.0.27/28 规则)
    if show_quartiles:
        for gi, g in enumerate(data):
            q1, med, q3 = np.percentile(g, [25, 50, 75])
            x0, x1 = gi - width / 2.0, gi + width / 2.0
            ax.hlines([q1, q3], x0, x1, color="black", linestyles="--",
                      linewidth=0.6, zorder=5)
            ax.hlines(med, x0, x1, color="black", linewidth=1.1, zorder=6)
    # v2.0.32（审查修复 #3）：无显著性 bracket 时也要 y 轴收尾（与柱状图/bracket
    # 统一），保证刻度等分、下限对齐 0.5 倍数；不传 data_max（用当前 ylim 顶端为
    # 上限基准，cap=1.3×顶端，永不裁切须线/散点）
    finish_axes(ax)
    _maybe_rotate_xticklabels(ax)
    return ax

def add_pairwise_brackets(ax, comparisons, labels=None, base=None, level_height=None,
                          color="black", lw=0.75, fontsize=7, include_ns=False,
                          sort_by_span=True, show_marginal_p=True, p_fontsize=6,
                          p_precision=None, ytick_step=None):
    """
    在多个比较对上自动画显著性括号，按 x 跨度分层堆叠，避免相互重叠。

    解决试运行痛点：3 组及以上两两比较时，手动给每个括号定 y 高度极易重叠；
    本函数自动分层——跨度大的括号放顶层，跨度小的放底层，互不交叠。

    参数：
        ax          : matplotlib Axes（建议先画好图）
        comparisons : [(x1, x2, p_value), ...]。x1/x2 可直接传分组 x 坐标
                      （整数/浮点），也可传分组标签字符串——此时必须同时传入
                      labels，函数按 labels.index() 自动换算成 x 坐标（与
                      oneway_anova_tukey / ttest_two_groups 返回的 (label_i,
                      label_j, p) 直接对接，无需手动编号）。
        labels      : 分组标签序列；comparisons 用标签字符串时必填
        base        : 最底层括号基线 y；None 时取图上数据最大值 × 1.03
        level_height: 每层额外高度（默认 y 轴可见跨度的 6%）
        include_ns  : 是否标注 ns（默认 False，v2.0.16 起不显著不标，
                      同时显著对层数减少 → ylim 顶部更贴近数据最大值）
        show_marginal_p: p∈[0.05,0.1) 边缘显著时标注精确 p 值（默认 True，
                      v2.0.17：p 精确值标注**只**在此区间触发，显著用星号），
                      透传给 add_significance_brackets
        p_fontsize  : p 值文本字号（默认 6）
        color/lw/fontsize: 透传给 add_significance_brackets
        ytick_step  : y 轴刻度步长（None=自动漂亮步长）。小图（如 3×4cm）
                      想要更粗刻度（每 0.5 一格）时显式传 0.5 即可，避免
                      默认 10 个刻度偏密（v2.6.x 新增）。
    返回：ax
    """
    def _to_x(v):
        if isinstance(v, str) and labels is not None:
            return labels.index(v)
        return v

    y0, y1 = ax.get_ylim()
    # 自动取数据最大值（优先散点集合，其次箱体 patch 顶）
    ys = []
    for coll in ax.collections:
        if hasattr(coll, "get_offsets"):
            offs = coll.get_offsets()
            if len(offs):
                ys.extend(offs[:, 1])
    # 兼容 seaborn 版本差异：0.12 箱体在 ax.artists，0.13+ 在 ax.patches（PathPatch）
    # v2.5.1 修复（ylim<1 时 bracket 超高）：Rectangle 的 get_path() 返回
    # **单位矩形 (0,0)-(1,1)**（真实坐标在 transform 里），get_path().get_extents()
    # 恒为 1.0 → data_max 被污染成 1.0（数据>1 时被真实值盖过不显现，<1 时爆发，
    # base=1.02、bracket 画在 y≈1.07、ylim 顶到 1.5）。Rectangle 必须用 get_bbox()
    # （返回数据坐标）；PathPatch 无 get_bbox，其 get_path() 即数据坐标，可直用。
    for patch in list(getattr(ax, "artists", [])) + list(ax.patches):
        try:
            if hasattr(patch, "get_bbox"):
                ys.append(patch.get_bbox().y1)          # Rectangle：数据坐标
            else:
                ys.append(patch.get_path().get_extents().y1)  # PathPatch：path 即数据坐标
        except Exception:
            pass
    data_max = max(ys) if ys else y1
    if base is None:
        base = data_max * 1.02

    # v2.0.17：保留 p<0.1 的比较（显著 p<0.05 → 星号；边缘显著 [0.05,0.1)
    # → 精确 p 值）。p≥0.1 不标——不标 ns，且层数减少让 ylim 顶部贴近
    # "1.3×数据最大值"（用户约束）
    kept = []
    for c in comparisons:
        if c[2] < 0.1 or include_ns:
            kept.append(c)
    if not kept:
        return ax

    # 分层：跨度大的先放，放到最低可用层（区间不交叠即不冲突）
    def overlap(a, b):
        # 仅在"内部重叠"时判为冲突（边界 x 处相切不算），这样相邻但只
        # 在共享组处相切的括号可共用一层，压缩纵向堆叠、减少上端留白
        return a[0] < b[1] and b[0] < a[1]
    items = [(_to_x(c[0]), _to_x(c[1]), c[2]) for c in kept]
    items.sort(key=lambda c: abs(c[1] - c[0]), reverse=sort_by_span)
    placed = []  # (lo, hi, level)
    for x1, x2, p in items:
        lo, hi = (x1, x2) if x1 <= x2 else (x2, x1)
        level = 0
        while any(overlap((lo, hi), (a, b)) and lv == level
                  for a, b, lv in placed):
            level += 1
        placed.append((lo, hi, level))

    span = y1 - y0
    max_level = max(lv for _, _, lv in placed)
    # 先求"容纳最高括号+标注文字"所需的最小顶端（自洽迭代，与
    # add_significance_brackets 内部顶端公式一致：y + height*span + GUARD*span）
    # v2.0.16（用户指定：ylim 顶部尽量贴近 1.3×数据最大值，压缩标注区）：
    #   层高 LH 0.075→0.055（容纳 BH 0.014 + 标注偏移 + 文字高 ~0.04，
    #     层间安全（v2.0.21 分类型）：星号 offset -0.02 → -0.02+0.04+0.014=0.034 ✓；
    #     p 值 offset 0 → 0+0.035+0.014=0.049 ✓）
    #   v2.0.23（用户再要求"ylim ≤ 1.3×样本最大值，可更小"）：LH 0.055→0.043——
    #     n=15/4 组 6 对 4 层时 top_bracket 从 28.7 降到 27.4，配合尾部
    #     "超 1.3× 放宽 max_ticks=11"取整到 27.5（1.31×），此前 30（1.42×）。
    #     层间安全重核：星号需 LH ≥ 0.014+0.04-0.02=0.034 ✓；p 值(6pt)需
    #     LH ≥ 0.014+0.03=0.044 ≈ 0.043（0.03 单位微侵入可忽略）
    #   标注偏移（用户要求"星号尽量靠近括号"）：v2.0.16 0.008 → v2.0.18 0.003
    #     → v2.0.19 -0.005（负值骑线）→ v2.0.20 -0.01 → v2.0.21 分类型：
    #     p 值 0、星号 -0.02
    #   文字余量 GUARD 0.04→0.03、竖线 BH 0.018→0.014
    BH, GUARD, LH = 0.014, 0.03, 0.043   # 括号竖线长度 / 文字上方余量 / 每层高度（均占 span 比例）
    S = base + (max_level + 1) * (LH * span) + (BH + GUARD) * span
    for _ in range(16):
        span_s = S - y0
        top = base + (max_level + 1) * (LH * span_s) + (BH + GUARD) * span_s
        if abs(top - S) < 1e-4:
            break
        S = top
    top_bracket = S
    level_height = LH * (top_bracket - y0)   # 用最终 span 确定层高

    # 先把 ylim 设为所需最小顶端，再画括号（括号坐标据此定位）
    ax.set_ylim(y0, top_bracket)

    pmap = {}
    for x1, x2, p in items:
        lo, hi = (x1, x2) if x1 <= x2 else (x2, x1)
        pmap[(lo, hi)] = p
    for lo, hi, level in placed:
        y = base + (level + 1) * level_height
        add_significance_brackets(ax, lo, hi, pmap[(lo, hi)], y=y,
                                  height=BH, color=color, lw=lw,
                                  include_ns=include_ns, fontsize=fontsize,
                                  show_marginal_p=show_marginal_p,
                                  p_fontsize=p_fontsize,
                                  p_precision=p_precision)

    # 收尾：把轴顶向上取整到最近的"漂亮等分刻度"，既保证 y 轴刻度等分、
    # 最顶刻度带标签，又不过度留白（替代旧版硬钉非整刻度 173.4 的写法）
    # v2.0.23（用户约束"ylim ≤ 1.3×样本最大值，可更小"）：默认取整后若顶部
    # 仍超 1.3×data_max，放宽 max_ticks 到 11 重算（step 2.5×11=27.5 可替代
    # step 5×6=30），让顶部尽量贴近 1.3×。受刻度粒度（0.5 倍数，v2.0.22）
    # 与 bracket 层数物理限制，个别场景（显著对≥3 且需细刻度）仍可能略超
    # v2.0.24（修复 44.28/54.28/... 丑刻度）：y 轴下限先向下对齐到 0.5 倍数
    # （_floor_half_step）再生成刻度——seaborn 箱线图自动 padding 出的下限
    # 44.28 非 0.5 倍数，arange 起点 .28 导致整条刻度网格带 .28 尾数
    cap = data_max * 1.3
    y0a = _floor_half_step(y0)
    final_top, step = _nice_ylim_top(top_bracket, y0a)
    if final_top > cap:
        t2, s2 = _nice_ylim_top(top_bracket, y0a, max_ticks=11)
        if t2 < final_top:
            final_top, step = t2, s2
    # v2.6.x：显式 ytick_step 时覆盖自动步长，并把轴顶向上取整到该步长
    # 的整数倍（从 y0a 起算），保证最顶刻度带标签、刻度等分且不悬空。
    if ytick_step is not None:
        step = float(ytick_step)
        n_steps = int(np.ceil((top_bracket - y0a) / step))
        final_top = y0a + n_steps * step
    ticks = np.arange(y0a, final_top + step * 0.5, step)
    ax.set_ylim(y0a, final_top)
    ax.set_yticks(ticks)
    _maybe_sci_yticks(ax, step)   # v2.5.3：极小刻度科学计数法
    return ax

# ---- 坐标轴收尾 + 统计报告生成 ----

def _is_half_multiple(x):
    """x 是否为"漂亮刻度"步长（v2.5.1 按量级分级，修复 <1 值域刻度过粗）。

    v2.0.22 原规则：刻度须取整或 0.5 的倍数——对 >1 数据（如 44.28）正确，
    但把 0.05/0.1/0.2/0.25 等 **<1 值域的漂亮步长** 全部误杀：数据最大
    0.6 时 `_nice_ylim_top` 只能给出 0.5 步长 → 轴顶被顶到 1.0（1.67×，
    远超 1.3× 约束），数据 0.08 时轴顶 0.5、刻度只剩 2 个。

    分级规则（对齐 GraphPad Prism 刻度习惯）：
    - x >= 1        ：取整或 0.5 的倍数（0.5/1/1.5/2/2.5/5/10...，保留 v2.0.22 约束）
    - 0.05<=x<1     ：0.05 的整数倍（0.05/0.1/0.15/0.2/0.25/.../0.95）
    - 0.005<=x<0.05 ：0.005 的整数倍（0.005/0.01/0.015/...）
    - 更小           ：按 10^k 网格对齐（0.001/0.002/...）

    效果：候选步长 {1,2,2.5,5,10}×10^k 中 0.025/0.0025/0.00025（m=2.5, k<=-2）
    等中间丑值被拒，0.01/0.02/0.05/0.1/0.2/0.25/0.5 等漂亮刻度全通过。
    用浮点容差 1e-9 避免 10^k 舍入误差误判。
    """
    if x <= 0:
        return True
    if x >= 1:
        unit = 0.5                       # v2.0.22：>=1 保持"取整或 0.5 倍数"
    elif x >= 0.05:
        unit = 0.05                      # <1 常用：0.05 网格（0.05~0.95）
    elif x >= 0.005:
        unit = 0.005                     # 0.005~0.05：0.005 网格
    else:
        unit = 10.0 ** np.floor(np.log10(x))   # 更小量级：10^k 网格
    r = x / unit
    return abs(r - round(r)) < 1e-9

def _floor_half_step(x):
    """把 x **向下**对齐到最近的"漂亮网格"点（v2.0.24 引入，v2.5.2 分级）。

    用途：y 轴下限对齐。seaborn 箱线图/小提琴图自动 padding 出的 ylim 下限
    （如 44.28）不是漂亮网格点时，`np.arange(y0, top, step)` 的刻度会从 .28
    起步（44.28/54.28/...）——向下对齐后起点为整数（44.0），刻度网格立刻
    变干净。**向下**取整保证不高于数据下限，永不切掉数据。

    v2.5.2：按量级分级（与 `_is_half_multiple` 同款网格）——|x|>=1 对齐 0.5
    倍数，0.05<=|x|<1 对齐 0.05 倍数，0.005<=|x|<0.05 对齐 0.005 倍数，更小
    用 10^k 网格。此前硬钉 0.5 倍数：对 <1 值域的非零下限（如 violin 对
    0.2~0.8 数据 padding 出的 -0.1）粒度太粗，-0.1 会被拉到 -0.5、白白浪费
    下方空间（与 v2.5.1 修 `_is_half_multiple` 同源的下限方向漏网）。
    """
    a = abs(x)
    if a >= 1:
        unit = 0.5
    elif a >= 0.05:
        unit = 0.05
    elif a >= 0.005:
        unit = 0.005
    elif a > 0:
        unit = 10.0 ** np.floor(np.log10(a))
    else:
        return 0.0
    return np.floor(x / unit) * unit   # 负数：向下=更负，同样不切数据

def _maybe_sci_yticks(ax, step):
    """极小刻度（step<1e-3）改用科学计数法，避免 0.0000001 这类长标签（v2.5.3）。

    scilimits=(-3, 3)：指数超出 [-3,3] 才用科学计数——常规刻度（step≥1e-3）
    不受影响，仅极小值轴的标签变紧凑（0, 2e-6, 4e-6, ...）。
    """
    if step < 1e-3:
        ax.ticklabel_format(axis="y", style="sci", scilimits=(-3, 3))


def _nice_ylim_top(target, y0=0.0, min_ticks=4, max_ticks=9):
    """
    求 (top, step)：在 [y0, top] 上取等间隔"漂亮"刻度——top 为 >= target 的
    最小漂亮整数倍（步长取自 1/2/2.5/5/10 × 10^k），且区间数落在
    [min_ticks, max_ticks] 内。

    目的：让 y 轴刻度**等分且为整刻度**、最顶一个刻度带标签，同时把轴顶压到
    刚好包住显著性标注的最小漂亮值，避免大段留白或刻度网格断裂（如旧版把轴顶
    硬钉成 173.4 这类非整刻度，会导致最顶整刻度缺失、网格不闭合）。

    v2.0.16：max_ticks 8→11 允许 step=2.5（final_top 更贴近 top_bracket，
    满足"ylim ≤ 1.3×数据最大值"）。
    v2.0.17（用户反馈"ticks 太多显得拥挤"）：max_ticks 11→9——候选仍按
    **top 最小**选择，但 step=2.5 的方案在区间数 >9 时被拒（如 27.5/2.5=11
    个区间 → 被拒），自动退回 step=5（6 个区间，7 个刻度标签），避免细密刻度。
    v2.0.22（用户反馈"ticks 要取整或 0.5 的倍数"）：候选 step 必须通过
    `_is_half_multiple` 过滤（step/0.5 为整数）——淘汰 0.25/0.1/0.2/0.05 等
    非 0.5 倍数步长（此前 step=2.5×10^-1=0.25 会产生 0,0.25,0.5... 的丑刻度）。
    兜底分支同样把 step 对齐到最近的 0.5 倍数。
    """
    target = max(target, y0 + 1e-6)
    best = None
    for k in range(-4, 7):
        mag = 10.0 ** k
        for m in (1.0, 2.0, 2.5, 5.0, 10.0):
            step = m * mag
            if step <= 0:
                continue
            if not _is_half_multiple(step):
                continue   # v2.0.22：刻度须为整数或 0.5 的倍数，过滤 0.25/0.1/0.2 等
            n = max(1, int(np.ceil((target - y0) / step)))
            if min_ticks <= n <= max_ticks:
                top = y0 + n * step
                if best is None or top < best[0]:
                    best = (top, step, n)
    if best is None:   # 兜底：取最接近的漂亮步长（v2.5.1 分级对齐，不再硬钉 0.5）
        step = 10.0 ** round(np.log10((target - y0) / 5.0))
        # v2.0.22 原兜底 max(0.5, ...) 对 <1 值域误伤（数据 0.08 → 步长 0.5）；
        # v2.5.1：与 _is_half_multiple 同款分级——>=1 对齐 0.5 倍数，
        # <1 对齐 0.05/0.005/10^k 网格，保证兜底步长与主循环口径一致。
        if step >= 1:
            step = max(0.5, round(step / 0.5) * 0.5)
        elif step >= 0.05:
            step = round(step / 0.05) * 0.05
        elif step >= 0.005:
            step = round(step / 0.005) * 0.005
        else:
            unit = 10.0 ** np.floor(np.log10(step))
            step = max(unit, round(step / unit) * unit)
        n = max(1, int(np.ceil((target - y0) / step)))
        best = (y0 + n * step, step, n)
    return best[0], best[1]

def set_nice_ylim(ax, top=None):
    """
    把 y 轴上限收尾到一个**漂亮等分刻度**（>= 当前/目标顶端），保证：
      - y 轴刻度等分、均为整刻度，最顶一个刻度带标签；
      - 不会向上取整出大片空白，也不会硬钉非整刻度导致网格断裂。

    top=None：以当前轴上限为基准；否则以 top 为基准向上收尾。
    仅在需要扩展（target > 当前轴顶）时才改动坐标轴。
    v2.0.24：y 轴下限先向下对齐（v2.5.2 起按量级分级，<1 值域 0.05 网格；
    v2.0.24 原为 0.5 倍数）再生成刻度，修复 seaborn 箱线图 padding 出的
    .28 下限导致整条刻度带 .28 尾数的问题。
    """
    y0, y1 = ax.get_ylim()
    target = top if top is not None else y1
    if target <= y1:
        return   # 已有足够空间，保留当前刻度网格
    y0a = _floor_half_step(y0)
    final_top, step = _nice_ylim_top(target, y0a)
    ticks = np.arange(y0a, final_top + step * 0.5, step)
    ax.set_ylim(y0a, final_top)
    ax.set_yticks(ticks)
    _maybe_sci_yticks(ax, step)   # v2.5.3：极小刻度科学计数法

def _point_dxdy(ax, dot_size):
    """单个散点直径换算成 (d_x, d_y)——数据坐标下的点宽与点高（v2.0.29）。

    最小间距约束（min_sep）做碰撞检测时需要两个方向的点径：
    矩形判据"|Δy| < d_y 且 |Δx| < d_x 视为重叠"。
    """
    # 直径近似：scatter 的 s 为面积，真实直径 = 2·√(s/π)/72 ≈ 1.128·√(s)/72。
    # 此处按 √(s)/72 取直径（约 0.886×真实直径），碰撞阈值略偏保守（点允许更近），
    # 但全图统一且由 _apply_overlap_alpha 透明度兜底重叠，视觉偏差可忽略（v2.0.32 审查注记 #6）。
    d_inch = np.sqrt(dot_size) / 72.0
    ax.figure.canvas.draw()
    bbox = ax.get_window_extent()
    dpi = ax.figure.dpi
    xlim, ylim = ax.get_xlim(), ax.get_ylim()
    d_x = d_inch * (xlim[1] - xlim[0]) / (bbox.width / dpi)
    d_y = d_inch * (ylim[1] - ylim[0]) / (bbox.height / dpi)
    return d_x, d_y

def finish_axes(ax, top=None, data_max=None):
    """
    v2.0.25：**全图型统一 y 轴收尾**——把 y 轴上限收尾到"漂亮等分刻度"
    （`_nice_ylim_top`，分级步长，v2.5.1 起 <1 值域用 0.05 网格）、下限向下
    对齐到同款分级网格（`_floor_half_step`，v2.5.2），并尽量贴近 1.3×data_max。

    这是 `add_pairwise_brackets` 尾部收尾逻辑的**公开通用版本**，供所有图型
    统一调用（prism_xy_fit / 手写 Grouped 图 / 任意需要干净 y 轴的图），
    避免"柱状图 y 轴漂亮、其他图顶端脏/刻度乱/顶部标签缺失"的不一致。

    参数：
        ax       : 目标坐标轴
        top      : 期望的轴顶；None 时取当前 ylim 顶端（只对齐刻度、不抬顶）
        data_max : 数据最大值（1.3× 约束用）；None 时用 top/当前顶端代替
    返回：ax
    """
    y0, y1 = ax.get_ylim()
    target = max(top if top is not None else y1, y1)
    y0a = _floor_half_step(y0)
    dmax = data_max if data_max is not None else y1
    # v2.5.3：全零数据（data_max==0）→ 直接 [0,1] 刻度 0.2，避免
    # `_nice_ylim_top(0)` 给出 1e-6 顶 + 1e-7 步长的怪刻度（视觉异常、标签过长）
    if dmax == 0:
        ax.set_ylim(0, 1.0)
        ax.set_yticks(np.arange(0, 1.0001, 0.2))
        return ax
    cap = dmax * 1.3
    final_top, step = _nice_ylim_top(target, y0a)
    if final_top > cap:
        t2, s2 = _nice_ylim_top(target, y0a, max_ticks=11)
        if t2 < final_top:
            final_top, step = t2, s2
    ticks = np.arange(y0a, final_top + step * 0.5, step)
    ax.set_ylim(y0a, final_top)
    ax.set_yticks(ticks)
    _maybe_sci_yticks(ax, step)   # v2.5.3：极小刻度科学计数法
    return ax

def prism_survival(ax, time, event, group, palette="okabe_ito", lw=0.75,
                   censoring=True, show_logrank=True, show_median=False,
                   show_cox=False, cox_reference=None,
                   xlabel="Time", ylabel="Survival probability",
                   legend_loc="upper right"):
    """
    Prism 风格 Kaplan-Meier 生存曲线（Survival 表标准画法，v2.0.24 新增）。

    - 每组一条 KM 阶梯曲线（plt.step, where='post'），色盲安全配色；
    - 删失事件用短竖线（marker='|'）标在对应生存概率处；
    - log-rank 检验（内置 Peto 法，无需 lifelines）：2 组给 p 值；
      ≥3 组给整体 χ² + p 值，p 值文本自动放图内（右下角，不挡曲线）；
    - show_median=True 时给每组画中位生存期虚线 + 数值标注。

    参数：
        ax        : matplotlib Axes（建议先 apply_prism_theme()）
        time      : array-like，生存时间（可含删失）
        event     : array-like，事件标记（1=事件发生，0=删失）
        group     : array-like，分组标签（与 time/event 等长）
        palette   : 色板名（"okabe_ito" 默认）或直接传颜色列表
        lw        : 曲线线宽（默认 0.75，对齐全局 0.75pt 线条约定；可传 lw= 调整）
        censoring : 是否画删失短竖线（默认 True）
        show_logrank: 是否在图内标注 log-rank 检验 p 值（默认 True）
        show_median: 是否画中位生存期虚线（默认 False）
        show_cox  : 是否标注 Cox 回归 HR（默认 False，需 lifelines；
                    自动取参照组，可用 cox_reference= 指定）
        cox_reference: Cox 回归参照组名（默认自动识别对照命名，
                       否则取数据中首次出现的组）
        xlabel/ylabel: 轴标签
        legend_loc: 图例位置（默认 upper right；曲线顶部为空时可调 lower right）
    返回 dict：
        {"p": logrank p（2 组）或整体 p（≥3 组）, "chi2": χ² 统计量,
         "median": {组名: 中位生存期（未达到为 nan）}, "n": {组名: 例数},
         "cox": show_cox 时的 Cox 回归结果 dict（cox_regression 的返回，
                失败时为 None）}
    """
    time = np.asarray(time, dtype=float)
    event = np.asarray(event, dtype=int)
    group = np.asarray(group)
    gs = list(np.unique(group))
    if isinstance(palette, (list, tuple)) and len(palette) > 0:
        colors = list(palette)[:len(gs)]
    else:
        seq = palette_sequence(palette if isinstance(palette, str) else "okabe_ito")
        colors = (seq * ((len(gs) // len(seq)) + 1))[:len(gs)]

    res = {"p": None, "chi2": None, "median": {}, "n": {}}
    # v2.4.3：先算 x 轴漂亮上限（顶刻度=轴顶，杜绝 xticks 悬空）——
    # 曲线最后一段水平延伸到观察期结束（Prism 标准），右边界 = x_top。
    t_max_all = float(np.max(time))
    x_top, x_step = _nice_ylim_top(t_max_all * 1.08, 0.0,
                                   min_ticks=3, max_ticks=9)
    for g_i, g in enumerate(gs):
        mask = group == g
        tg, eg = time[mask], event[mask]
        res["n"][g] = int(mask.sum())
        order = np.argsort(tg)
        tg, eg = tg[order], eg[order]
        # KM 估计（Kaplan-Meier 乘积限估计）
        # v2.4.2 修复（v2.4.1 回归）：删失点**必须保留在阶梯坐标中**——
        # 它们是不下降的水平段节点，若剔除，删失点位于最后一个事件之后时
        # 曲线中断、删失标记悬空 → 线条不连续。正确画法：所有时间点都进
        # t_at/surv（起点 (0, 1.0)），仅事件点更新生存概率（删失点 surv
        # 不变 = 水平段），曲线连续延伸到最后一个观测点。
        # v2.4.3：t_at 末尾追加 x_top（观察期右边界），曲线水平延伸到轴
        # 边缘（Prism 标准画法），不再右侧留白。
        s, t_at, surv = 1.0, [0.0], [1.0]
        for i, t in enumerate(tg):
            n_at = int((tg >= t).sum())
            if eg[i] == 1 and n_at > 0:
                s *= (1 - 1 / n_at)
            t_at.append(t)
            surv.append(s)
        if t_at[-1] < x_top:
            t_at.append(x_top)
            surv.append(s)
        # step 画阶梯曲线：where='post' 表示每个区间取右端点的 y 值
        ax.step(t_at, surv, where="post", color=colors[g_i], lw=lw,
                label=g, zorder=4)
        # 删失标记：直接画在该点生存概率处（t_at/surv 已含删失点）。
        # v2.4.3：clip_on=False —— y=1.0 处的删失标记若被轴裁剪会变成
        # "半截短线"（v2.4.2 改 ylim(0,1.0) 后出现，用户第一轮就反馈过
        # "线条上有短线"）。顶部 ylim 留白 + clip_on=False 双保险。
        if censoring:
            for t_c, s_c, e in zip(tg, surv[1:], eg):
                if e == 0:
                    ax.plot(t_c, s_c, marker="|", ls="none",
                            color=colors[g_i], ms=5, mew=1.0, zorder=5,
                            clip_on=False)
        if show_median:
            med = _km_median(tg, eg)
            res["median"][g] = med
            if np.isfinite(med):
                ax.axvline(med, ls="--", lw=0.75, color=colors[g_i], alpha=0.7,
                           zorder=3)
                # v2.0.39（learnings #23 修复）：中位生存期数值加白底半透明
                # bbox——竖排数值跨 y=0~0.05 区域，与右下角 log-rank p 文本
                # 在中位线接近 x 轴 50% 时重叠；白底可读性兜底，不再与
                # p 文本互相干扰。
                ax.text(med, 0.03, f"{med:.1f}", fontsize=6, color=colors[g_i],
                        rotation=90, va="bottom", ha="center",
                        bbox=dict(boxstyle="round,pad=0.12", fc="white",
                                  ec="none", alpha=0.75))

    # log-rank 检验：2 组 Peto 法；≥3 组整体 χ² + 两两（未校正，报告注明）
    if show_logrank:
        # v2.3.2（learnings #13 修复补强）：p 文本移到轴外右上（bbox 白底），
        # 与 show_median 竖排数值解耦——旧位置 (0.98, 0.08) 在中位生存期接近
        # 右边界时与竖排数值文本重叠（复现：中位数 60/上限 60 → '60.0' 与
        # 'log-rank p=...' 双 bbox 交叉）。轴外右上 + bbox_inches='tight'
        # 自动扩顶部画布（与 contingency 轴外文本同款处理）。
        p_style = dict(transform=ax.transAxes, ha="right", va="bottom",
                       fontsize=7,
                       bbox=dict(boxstyle="round,pad=0.25", fc="white",
                                 ec="none", alpha=0.9))
        if len(gs) == 2:
            _, _, z, p = _logrank_two(time, event, group, gs[0], gs[1])
            res["p"], res["chi2"] = p, z ** 2
            ax.text(0.99, 1.02, f"log-rank {format_p(p)}", **p_style)
        else:
            multi = _logrank_multi(time, event, group)
            chi2, df, p = multi["overall"]
            res["p"], res["chi2"] = p, chi2
            ax.text(0.99, 1.02,
                    f"log-rank \u03c7\u00b2({df}) = {chi2:.2f}, "
                    f"{format_p(p)}", **p_style)

    # Cox 比例风险回归标注（v2.4.3 NEW）：HR + 95% CI（vs 参照组）
    res["cox"] = None
    if show_cox:
        cox_txt, cox_ok = "", False
        try:
            cr = cox_regression(time, event, group, reference=cox_reference)
            res["cox"] = cr
            parts = []
            for gname, hr, lo, hi, p in cr["comparisons"]:
                if gname == cr["reference"]:
                    continue
                st_c, _ = p_to_stars(p)
                parts.append(f"{gname} HR={hr:.2f} [{lo:.2f},{hi:.2f}]{st_c}")
            cox_txt = f"Cox vs {cr['reference']}: " + "; ".join(parts)
            cox_ok = True
        except ImportError as e:
            cox_txt = f"Cox: 需要 lifelines（pip install lifelines）"
        except Exception as e:
            cox_txt = f"Cox: 计算失败（{type(e).__name__}）"
        if cox_ok:
            ax.text(0.99, 1.14, cox_txt, **p_style)
        else:
            ax.text(0.99, 1.14, cox_txt, color="#A32D2D", **p_style)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    # v2.4.3：y 轴 0-1.05（生存概率 0~100% + 顶部留白）——
    # 顶刻度 1.0 < ylim 1.05 是 Prism 标准（顶部空间容纳删失标记/图例），
    # **不是**悬空。v2.4.2 改成 (0,1.0) 反而导致 y=1.0 处删失标记被轴
    # 裁剪成半截短线（用户第一轮就反馈的"线条上有短线"）。
    ax.set_ylim(0, 1.05)
    ax.set_yticks(np.arange(0, 1.001, 0.25))
    # v2.4.3：x 轴范围紧贴数据 + 刻度显式收尾（顶刻度=轴顶，不再悬空）。
    # 旧版 set_xlim(0, t_max*1.08) 不设 xticks，matplotlib 自动刻度末项常
    # 超出轴范围（如 xlim=10.8 但刻度到 12）→ 顶刻度悬空在轴外。
    ax.set_xlim(0, x_top)
    ax.set_xticks(np.arange(0, x_top + x_step * 0.5, x_step))
    # L 形坐标轴 + 刻度线约束（v2.4.0 修复：tick lines 向上穿透 KM 曲线）
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.xaxis.set_ticks_position("bottom")
    ax.yaxis.set_ticks_position("left")
    ax.legend(frameon=False, fontsize=7, loc=legend_loc)
    return res

def prism_xy_fit(ax, x, y, model="4pl", palette="okabe_ito",
                 fit_kws=None, show_ic50=True, legend_loc="upper left",
                 xlabel="X", ylabel="Y"):
    """
    Prism 风格 XY 散点 + 拟合曲线（XY 表标准画法，v2.0.24 新增）。

    model 可选：
      - "4pl"（默认）：四参数 logistic 剂量-响应拟合
            y = bottom + (top - bottom) / (1 + 10^((logEC50 - log10(x)) · hill))
        x 轴自动设为 log 刻度；show_ic50=True 时画 IC50 垂直虚线 + 文本标注。
      - "linear"    ：一阶线性回归（y = a + b·x）。
    fit_kws：透传给 scipy.optimize.curve_fit（4pl）或 np.polyfit（linear）。

    参数：
        ax         : matplotlib Axes（建议先 apply_prism_theme()）
        x/y        : array-like，等长的观测点
        model      : "4pl"（默认）或 "linear"
        palette    : 色板名或颜色列表；散点用色板第 2 色、拟合线用第 1 色
        show_ic50  : 4pl 时是否标注 IC50（默认 True）
        legend_loc : 图例位置（默认 upper left——S 形曲线左上角为空白平台区，
                     不会压到曲线；若曲线形态不同可改 "lower right" 等）
        xlabel/ylabel: 轴标签
    返回 dict：
        {"model": ..., "popt": 拟合参数数组, "ic50": IC50（4pl）或 None,
         "r2": 决定系数, "p0": 实际使用的初值（v2.3.1+）,
         "dropped": x≤0 被过滤的点数}

    Example
    -------
    >>> import numpy as np
    >>> import matplotlib.pyplot as plt
    >>> from scripts.prism_theme import (
    ...     apply_prism_theme, recommend_figsize, prism_xy_fit)
    >>>
    >>> # 8 个浓度梯度(可含 0,会自动过滤)+ 24 响应观测
    >>> x = np.array([0, 0.1, 1, 10, 100, 1000, 10000, 100000])  # nM
    >>> y = np.array([1200, 1310, 1820, 4500, 8215, 9580, 10120, 10080])
    >>>
    >>> apply_prism_theme()
    >>> fig, ax = plt.subplots(figsize=recommend_figsize("xy"))
    >>> res = prism_xy_fit(ax, x, y, model="4pl",
    ...                    xlabel="Compound (nM)", ylabel="RLU")
    >>> print(f"EC50 = {res['ic50']:.3g} nM, R² = {res['r2']:.4f}")
    >>> fig.savefig("dose_response.png", dpi=300, bbox_inches="tight")
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    if isinstance(palette, (list, tuple)) and len(palette) > 0:
        seq = list(palette)
    else:
        seq = palette_sequence(palette if isinstance(palette, str) else "okabe_ito")
    c_dot, c_line = seq[1], seq[0]

    if model == "4pl":
        # v2.0.39（体检发现）：剂量-响应数据几乎必有 0 剂量组，log10(0) → -inf
        # → curve_fit 直接 ValueError 崩溃。拟合前过滤 x<=0 并打印警告
        # （GraphPad Prism 同此处理：4PL 只在正浓度上拟合）。
        pos = x > 0
        n_drop = int((~pos).sum())
        if n_drop:
            print(f"[prism_xy_fit] 警告: 4PL 需 x>0，已排除 {n_drop} 个非正 x 数据点")
        if pos.sum() < 4:
            raise ValueError(
                f"4PL 拟合至少需要 4 个 x>0 的数据点，当前仅 {int(pos.sum())} 个"
            )
        xf, yf = x[pos], y[pos]
        # v2.5.5 退化预检：全同 y / 全同 x 时 4PL 无意义，scipy 只给
        # OptimizeWarning（协方差不可估）→ 改为明确中文提示
        if np.ptp(yf) < 1e-12:
            raise ValueError(
                "y 值全相同（剂量-响应无变化），无法拟合 4PL 曲线——请检查数据")
        if np.ptp(xf) < 1e-12:
            raise ValueError(
                "x 值全相同（浓度无梯度），无法拟合 4PL 曲线——请检查数据")
        # 散点只画参与拟合的正 x 点（log 刻度下 x<=0 本就无法显示，一并排除）
        ax.scatter(xf, yf, s=4 ** 2, facecolor=c_dot, edgecolor="black",
                   linewidth=0.5, zorder=5, label="Observed")
        def f(lx, bottom, top, logec50, hill):
            return bottom + (top - bottom) / (1 + 10 ** ((logec50 - lx) * hill))
        lx = np.log10(xf)
        # v2.1.1：curve_fit 默认 maxfev=1000 对剂量-响应数据（x 跨越多个
        # 数量级、y 陡峭跳变）常迭代不足抛 RuntimeError；合并 fit_kws 时
        # 默认提到 10000，用户传 maxfev 则优先。
        # v2.3.1：默认 p0 改数据驱动估算——硬编码 [0,100,0,1.0] 当 logEC50
        # 远离 0（即真实剂量-响应数据常见情况）时陷局部极小，R²≈0。
        # 改为 5%/95% 分位 + log10(median(x))，优于"扁平 S 曲线居中"假设。
        fk = dict(fit_kws or {})
        default_p0 = [
            float(np.percentile(yf, 5)),
            float(np.percentile(yf, 95)),
            float(np.log10(np.median(xf))),
            1.0,
        ]
        if "p0" in fk:
            user_p0 = np.asarray(fk.pop("p0"), dtype=float)
            p0_used = user_p0.tolist()
        else:
            p0_used = default_p0
        fk.setdefault("maxfev", 10000)
        from scipy.optimize import curve_fit  # 懒加载：仅 4PL 拟合需要
        popt, _ = curve_fit(f, lx, yf, p0=p0_used, **fk)
        xs = np.logspace(np.log10(xf.min()), np.log10(xf.max()), 200)
        ax.plot(xs, f(np.log10(xs), *popt), color=c_line, lw=1.2, zorder=4,
                label="4PL fit")
        ax.set_xscale("log")
        ic50 = 10 ** popt[2]
        r2 = 1 - np.sum((yf - f(lx, *popt)) ** 2) / np.sum((yf - yf.mean()) ** 2)
        if show_ic50 and np.isfinite(ic50) and ic50 > 0:
            ax.axvline(ic50, ls="--", lw=0.75, color="grey", zorder=3)
            ax.text(ic50 * 1.15, 12, f"IC50 = {ic50:.2g}", fontsize=6,
                    color="grey")
        result = {"model": "4pl", "popt": popt, "ic50": ic50, "r2": r2,
                  "dropped": n_drop, "p0": p0_used}
    elif model == "linear":
        ax.scatter(x, y, s=4 ** 2, facecolor=c_dot, edgecolor="black",
                   linewidth=0.5, zorder=5, label="Observed")
        popt = np.polyfit(x, y, 1, **fit_kws or {})
        xs = np.linspace(x.min(), x.max(), 200)
        ax.plot(xs, np.polyval(popt, xs), color=c_line, lw=1.2, zorder=4,
                label="Linear fit")
        r2 = 1 - np.sum((y - np.polyval(popt, x)) ** 2) / np.sum((y - y.mean()) ** 2)
        result = {"model": "linear", "popt": popt, "ic50": None, "r2": r2,
                  "dropped": 0}
    else:
        raise ValueError(f"未知 model={model!r}，可选 '4pl' 或 'linear'")
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    # v2.0.25：统一 y 轴收尾（漂亮等分刻度 + 下限对齐 + 顶部 ≤ ~1.3×数据最大值），
    # 与柱状图/箱线图的 y 轴规范一致——修复 XY 图顶端刻度脏/缺失标签的问题
    ymax_plot = yf.max() if model == "4pl" else y.max()
    finish_axes(ax, data_max=float(ymax_plot))
    ax.legend(frameon=False, fontsize=7, loc=legend_loc)
    return result

def write_report(name, report_md, out_dir, suffix="_report", fmt="md",
                 html=True):
    """
    保存统计报告，**文件名与统计图完全一致**（仅副名/后缀不同）。

    例：图 tnfa_dose_column_bar.png / .pdf
        → 报告 tnfa_dose_column_bar_report.md
    用相同的 name 调用 save_figure() 与 write_report() 即可保证对应。

    html=True（默认）时，额外自动生成同名自包含 HTML 总览报告：
        → tnfa_dose_column_bar.html
    内嵌 base64 PNG（300dpi 预览，单文件自包含，双击即看）+ PDF 下载链接 +
    Markdown 报告正文（标题/表格/列表/引用/代码块渲染为 HTML）。
    HTML 生成失败不影响 .md 写入（静默降级并打印警告）。
    """
    import os
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, f"{name}{suffix}.{fmt}")
    with open(path, "w", encoding="utf-8") as f:
        f.write(report_md)
    if html:
        try:
            write_html_report(name, report_md, out_dir,
                              png_path=os.path.join(out_dir, f"{name}.png"),
                              pdf_path=os.path.join(out_dir, f"{name}.pdf"))
        except Exception as e:  # noqa: BLE001
            print(f"[write_report] 警告: HTML 总览生成失败(已跳过): {e}")
    return path


def _md_escape(text):
    """转义 HTML 特殊字符(& < >)，防 Markdown 原文里的 < > 破坏 HTML 结构。"""
    import html as _html
    return _html.escape(str(text), quote=False)


def _md_to_html(md):
    """轻量 Markdown → HTML 渲染器（仅支持报告实际用到的语法）。

    支持：# 标题 / ## 小节 / **粗体** / `行内代码` / - 无序列表 /
    | 表格 | / > 引用 / ``` 代码块 / 空行分段。
    这是技能内部渲染，不需要引入第三方 markdown 库（零新增依赖）。
    """
    lines = (md or "").split("\n")
    out = []
    i, n = 0, len(lines)
    import re as _re

    def inline(s):
        # 先保护"显著性星号"(括号内 (*)~ (****) 与 *p<0.05 星号前缀),
        # 避免被下面的 Markdown 粗体正则 **...** 误伤（v2.0.38 实测 bug:
        # "p=0.010 (**)" 被渲染成 <strong> 破坏 p 值展示）。
        stars = []
        def save_star(m):
            stars.append(m.group(0))
            return f"\u00a7S{len(stars) - 1}\u00a7"
        s = _re.sub(r"\((\*+)\)", save_star, s)          # (**) (***) (****)
        s = _re.sub(r"(?<!\w)\*+(?=p<)", save_star, s)   # *p<0.05 **p<0.01 ...
        s = _md_escape(s)
        s = _re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
        s = _re.sub(r"\*\*([^*]+?)\*\*", r"<strong>\1</strong>", s)
        def restore(m):
            return stars[int(m.group(1))]
        s = _re.sub(r"\u00a7S(\d+)\u00a7", restore, s)
        return s

    def flush_paragraph(buf):
        if buf:
            out.append("<p>" + " ".join(buf) + "</p>")
            buf.clear()

    buf = []
    while i < n:
        line = lines[i]
        stripped = line.strip()
        # 代码块
        if stripped.startswith("```"):
            flush_paragraph(buf)
            block = []
            i += 1
            while i < n and not lines[i].strip().startswith("```"):
                block.append(lines[i])
                i += 1
            i += 1  # 跳过结束 ```
            out.append("<pre><code>" + _md_escape("\n".join(block)) + "</code></pre>")
            continue
        # 标题
        if stripped.startswith("#"):
            flush_paragraph(buf)
            level = len(stripped) - len(stripped.lstrip("#"))
            text = stripped[level:].strip()
            # 正文 h1 降级为 h2：页面级 <h1> 已展示标题，避免层级重复
            level = 2 if level <= 1 else min(level, 4)
            out.append(f"<h{level}>{inline(text)}</h{level}>")
            i += 1
            continue
        # 表格: 连续两行且第二行是分隔线 |---|---|
        if stripped.startswith("|") and i + 1 < n and "---" in lines[i + 1]:
            flush_paragraph(buf)
            header = [c.strip() for c in stripped.strip("|").split("|")]
            i += 2
            rows = []
            while i < n and lines[i].strip().startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            tb = ["<table>"]
            tb.append("<thead><tr>" + "".join(f"<th>{inline(h)}</th>" for h in header) + "</tr></thead>")
            tb.append("<tbody>")
            for r_ in rows:
                tb.append("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r_) + "</tr>")
            tb.append("</tbody></table>")
            out.append("".join(tb))
            continue
        # 无序列表
        if stripped.startswith("- ") or stripped.startswith("* "):
            flush_paragraph(buf)
            items = []
            while i < n and (lines[i].strip().startswith("- ") or lines[i].strip().startswith("* ")):
                items.append(inline(lines[i].strip()[2:].strip()))
                i += 1
            out.append("<ul>" + "".join(f"<li>{it}</li>" for it in items) + "</ul>")
            continue
        # 引用块
        if stripped.startswith(">"):
            flush_paragraph(buf)
            quotes = []
            while i < n and lines[i].strip().startswith(">"):
                quotes.append(lines[i].strip().lstrip(">").strip())
                i += 1
            out.append("<blockquote>" + " ".join(inline(q) for q in quotes) + "</blockquote>")
            continue
        # 空行 → 分段
        if not stripped:
            flush_paragraph(buf)
            i += 1
            continue
        buf.append(inline(stripped))
        i += 1
    flush_paragraph(buf)
    return "\n".join(out)


def write_html_report(name, report_md, out_dir, png_path=None, pdf_path=None,
                      title=None, extra_footer=None):
    """
    生成**与统计图同名**的自包含 HTML 总览报告：{name}.html
    （图是 {name}.png / {name}.pdf，报告 {name}_report.md，HTML 与之并列）。

    内容结构：
      - 头部：标题（默认取报告第一行 # 之后的描述）+ 生成时间
      - Figure 预览：内嵌 base64 PNG（300dpi，单文件自包含，双击即可查看，
        无需同目录图片也能完整呈现——发给同事/贴进投稿记录都方便）
      - PDF 下载按钮：链接同目录 {name}.pdf（相对路径，随目录整体转移有效）
      - 正文：Markdown 统计报告渲染为 HTML（描述统计表 / 前提检验 /
        检验统计量 / 事后比较 / 效应量 / Figure Legend）
      - 页脚：图注 + 复现提示

    参数：
        name        : 与 save_figure() 相同的 name（HTML 文件名 = {name}.html）
        report_md   : build_stats_report() 返回的 Markdown 字符串
        out_dir     : 输出目录（与图/报告同目录）
        png_path    : 预览 PNG 绝对路径；缺省尝试 {out_dir}/{name}.png，不存在则跳过图片区
        pdf_path    : PDF 绝对路径；缺省尝试 {out_dir}/{name}.pdf，不存在则隐藏下载按钮
        title       : HTML <title> 与页头标题；缺省从 report_md 第一行提取
        extra_footer: 附加页脚 HTML（可选，如数据来源说明）

    返回：HTML 文件绝对路径。
    """
    import os
    import base64
    import datetime as _dt
    os.makedirs(out_dir, exist_ok=True)

    if png_path is None:
        png_path = os.path.join(out_dir, f"{name}.png")
    if pdf_path is None:
        pdf_path = os.path.join(out_dir, f"{name}.pdf")

    # —— 标题：优先显式 title，其次报告首行 "# 统计报告：XXX" ——
    if not title:
        first_line = (report_md or "").strip().split("\n")[0]
        if first_line.startswith("#"):
            title = first_line.lstrip("#").strip()
        else:
            title = name
        # 去掉常见的 "统计报告：" 前缀，让页头更简洁
        title = title.replace("统计报告：", "").replace("统计报告:", "")

    # —— Figure 预览：base64 内嵌 PNG ——
    fig_html = ""
    if os.path.exists(png_path):
        with open(png_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("ascii")
        fig_html = (
            f'<div class="figure"><img src="data:image/png;base64,{b64}" '
            f'alt="{name}.png"></div>'
        )

    # —— PDF 下载按钮（v2.3.8 修复：base64 内嵌 + JS Blob 下载）——
    # 旧实现用相对链接 href="{name}.pdf"——HTML 报告是单文件自包含设计，
    # 预览/拷贝/分享时 PDF 常不在同目录，点击 404 或下载到错误文件。
    # 现改为把 PDF 也 base64 内嵌进 HTML，按钮点击时 JS 解码生成 Blob
    # 触发下载——任何环境下（本地双击 / 预览面板 / 邮件附件）都能正确下载。
    pdf_html = ""
    if os.path.exists(pdf_path):
        with open(pdf_path, "rb") as f:
            pdf_b64 = base64.b64encode(f.read()).decode("ascii")
        pdf_html = (
            f'<a class="dl" href="#" id="dl-pdf" '
            f'onclick="dlPdf(event)">Download PDF (vector)</a>\n'
            f'<script>\n'
            f'function dlPdf(e) {{\n'
            f'  e.preventDefault();\n'
            f'  var b64 = "{pdf_b64}";\n'
            f'  var bin = atob(b64);\n'
            f'  var bytes = new Uint8Array(bin.length);\n'
            f'  for (var i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);\n'
            f'  var blob = new Blob([bytes], {{type: "application/pdf"}});\n'
            f'  var url = URL.createObjectURL(blob);\n'
            f'  var a = document.createElement("a");\n'
            f'  a.href = url; a.download = "{name}.pdf";\n'
            f'  document.body.appendChild(a); a.click();\n'
            f'  document.body.removeChild(a);\n'
            f'  URL.revokeObjectURL(url);\n'
            f'}}\n'
            f'</script>'
        )

    # —— 正文 Markdown → HTML ——
    body_html = _md_to_html(report_md)

    # —— 页脚 ——
    footer_html = ""
    if extra_footer:
        footer_html = f'<div class="footer-extra">{extra_footer}</div>'
    now = _dt.datetime.now().strftime("%Y-%m-%d %H:%M")

    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{_md_escape(title)} · Prism-style Report</title>
<style>
  * {{ box-sizing: border-box; }}
  body {{
    font-family: "Arial", "Helvetica", "DejaVu Sans", sans-serif;
    margin: 0; padding: 28px 20px; background: #fafafa; color: #1a1a1a;
    line-height: 1.6; font-size: 14px;
  }}
  .wrap {{ max-width: 920px; margin: 0 auto; }}
  h1 {{ font-size: 20px; margin: 0 0 4px; font-weight: 600; }}
  .meta {{ color: #888; font-size: 12px; margin-bottom: 18px;
           border-bottom: 2px solid #1a1a1a; padding-bottom: 10px; }}
  .figure {{ background: #fff; border: 1px solid #e0e0e0; border-radius: 4px;
             padding: 12px; margin: 0 0 16px; text-align: center; }}
  .figure img {{ max-width: 100%; height: auto; }}
  .dl {{ display: inline-block; background: #0072B2; color: #fff; text-decoration: none;
         padding: 6px 14px; border-radius: 3px; font-size: 12px; margin-bottom: 18px; }}
  .dl:hover {{ background: #005a91; }}
  .report {{ background: #fff; border: 1px solid #e0e0e0; border-radius: 4px;
             padding: 20px 24px; }}
  .report h2 {{ font-size: 16px; margin: 22px 0 10px; padding-bottom: 5px;
                border-bottom: 1px solid #eee; }}
  .report h3 {{ font-size: 14px; margin: 18px 0 8px; }}
  .report h4 {{ font-size: 13px; margin: 14px 0 6px; }}
  .report p {{ margin: 8px 0; }}
  .report table {{ border-collapse: collapse; width: 100%; margin: 10px 0 14px;
                   font-size: 12.5px; }}
  .report th, .report td {{ border: 1px solid #ddd; padding: 5px 9px; text-align: left; }}
  .report th {{ background: #f2f2f2; font-weight: 600; }}
  .report tr:nth-child(even) td {{ background: #fafafa; }}
  .report ul {{ margin: 8px 0 14px; padding-left: 22px; }}
  .report li {{ margin: 3px 0; }}
  .report blockquote {{ margin: 12px 0; padding: 10px 14px; background: #f4f9f4;
                        border-left: 3px solid #009E73; color: #333; font-size: 12.5px; }}
  .report code {{ background: #f4f4f4; padding: 1px 4px; border-radius: 2px;
                  font-size: 12px; border: 1px solid #e8e8e8; }}
  .report pre {{ background: #f7f7f7; border: 1px solid #e0e0e0; border-radius: 4px;
                 padding: 10px 14px; overflow-x: auto; }}
  .report pre code {{ background: none; border: none; padding: 0; }}
  .footer-extra {{ margin-top: 16px; padding: 10px 14px; background: #f0f6fb;
                   border-left: 3px solid #0072B2; font-size: 12px; color: #555; }}
  .foot {{ margin-top: 20px; color: #aaa; font-size: 11px; text-align: right; }}
</style>
</head>
<body>
<div class="wrap">
  <h1>{_md_escape(title)}</h1>
  <div class="meta">Generated {now} · prism-style-plot · <code>{name}</code></div>
  {fig_html}
  {pdf_html}
  <div class="report">{body_html}</div>
  {footer_html}
  <div class="foot">Report generated by prism-style-plot (workbuddy skill)</div>
</div>
</body>
</html>"""

    html_path = os.path.join(out_dir, f"{name}.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(page)
    return html_path

def build_stats_report(test="anova_tukey", *, description="", groups=None,
                       labels=None, df=None, formula=None, time=None,
                       event=None, group=None, table=None, paired=False,
                       posthoc=True,
                       outer=None, inner=None, value=None,
                       rm_subject=None, rm_within=None, rm_between=None,
                       add_cox=True, cox_reference=None,
                       error_type="mean ± SEM",
                       p_precision=None,
                       var_equal="assumed",
                       anova_posthoc="auto",
                       star_scale="*p<0.05, **p<0.01, ***p<0.001, ****p<0.0001"):
    """
    生成投稿级 Markdown 统计报告（与统计图配套）。覆盖技能支持的表型：

      - "anova_tukey" : Column 表 ≥3 组（One-way ANOVA + Tukey 事后；
                        var_equal="assumed"|"welch"|"auto" 控制方差不齐处理，
                        v2.5.8：auto 时 Levene(Brown-Forsythe) p<0.05 自动切
                        Welch ANOVA；事后由 anova_posthoc 决定，v2.5.9：
                        auto=按 n 选 Dunnett T3(<50)/Games-Howell(>50)，
                        也可显式 games_howell/dunnett_t3/welch_t(不校正)）
      - "ttest"       : 2 组比较（自动 t / Mann-Whitney / Wilcoxon 配对）
                        paired=True → 配对设计（同一批样本前后测）；
                        默认 False = 自动 Student / Welch / Mann-Whitney。
      - "twoway"      : Grouped 表（Two-way ANOVA，含事后比较：交互显著→
                        简单效应 simple effects，不显著→主效应 Tukey；
                        posthoc=False 可关闭，v2.0.35）
      - "twoway_rm"   : 重复测量 Two-way ANOVA（v2.5.11 新增，混合设计
                        between × within，subject 嵌套在 between 组内且
                        测量 within 全部水平）。需传 df + rm_subject /
                        rm_within / rm_between / rm_value（列名）。含
                        Greenhouse-Geisser 球形性校正（ε + Mauchly）、
                        Subjects(matching) 行、简单效应/主效应事后
                        （per-subject 配对 t + Sidak）。
      - "survival"    : Survival 表（log-rank 检验；add_cox=True 时附加
                        Cox 回归 HR + 95% CI + PH 检验，需 lifelines，
                        v2.4.3 默认开启）
      - "nested"      : Nested 表（嵌套 ANOVA，以单元均值为分析单元，
                        避免假重复；v2.4.5 新增）。需 df/outer/inner/value
      - "contingency" : Contingency 表（卡方 / Fisher 精确）

    返回 Markdown 字符串；用 write_report() 写成与图同名的文件。
    报告含：描述统计、前提检验（正态/方差齐）、检验统计量+自由度、事后比较、
    效应量、Figure Legend——满足 statistics-guide.md 第五节"结果展示规则"。
    """
    L = []
    add = L.append
    # v2.0.39（learnings #22 修复）：description 语义 = 纯图内容描述。
    # 若调用方误传了 format_legend() 的完整输出（以 "Figure. " 开头），
    # 剥离前缀，避免 _report_* 拼 Figure Legend 时出现 "Figure. Figure." 双前缀。
    if description.startswith("Figure. "):
        description = description[len("Figure. "):]
    add(f"# 统计报告{('：' + description) if description else ''}\n")
    add(f"**表型统计方法**：`{test}`\n")

    with _fmt_p_precision(p_precision):
        if test == "anova_tukey":
            return _report_anova_tukey(groups, labels, description, error_type,
                                       star_scale, L, add, var_equal=var_equal,
                                       posthoc=anova_posthoc)
        if test == "twoway_rm":
            if df is None or not all((rm_subject, rm_within, rm_between, value)):
                add("\n（twoway_rm 需传 df + rm_subject/rm_within/rm_between/"
                    "rm_value 列名）\n")
                return "\n".join(L)
            return _report_twoway_rm(df, rm_subject, rm_within, rm_between,
                                     value, description, error_type, star_scale,
                                     L, add)
        if test == "ttest":
            return _report_ttest(groups, labels, description, error_type,
                                 star_scale, L, add, paired=paired)
        if test == "twoway":
            return _report_twoway(df, formula, description, error_type,
                                  star_scale, L, add, posthoc=posthoc)
        if test == "survival":
            return _report_survival(time, event, group, description, L, add,
                                    add_cox=add_cox, cox_reference=cox_reference)
        if test == "nested":
            return _report_nested(df, outer, inner, value, description, L, add,
                                  star_scale=star_scale)
        if test == "contingency":
            return _report_contingency(table, description, L, add, star_scale)
    add(f"\n（暂不支持 test={test!r}，请手动补充统计细节。）\n")
    return "\n".join(L)


# =====================================================================
# § 结果解读生成（v2.3.5 NEW）
def _report_anova_tukey(groups, labels, description, error_type, star_scale, L, add,
                        var_equal="assumed", posthoc="auto"):
    groups = [np.asarray(g, dtype=float) for g in groups]
    n = [len(g) for g in groups]
    N = sum(n)

    add("\n## 1. 描述统计\n")
    add("| 组别 | n | Mean | SD | SEM | 95% CI |")
    add("|---|---|---|---|---|---|")
    for lab, g in zip(labels, groups):
        m, sem = mean_sem(g)
        sd = g.std(ddof=1)
        ci = stats.t.ppf(0.975, len(g) - 1) * sem
        add(f"| {lab} | {len(g)} | {m:.2f} | {sd:.2f} | {sem:.2f} | "
            f"[{m-ci:.2f}, {m+ci:.2f}] |")

    add("\n## 2. 前提检验\n")
    add("### 正态性（Shapiro-Wilk，每组）\n")
    add("| 组别 | W | p | 结论 |")
    add("|---|---|---|---|")
    for lab, g in zip(labels, groups):
        if len(g) < 3:
            add(f"| {lab} | — | NA | "
                f"样本量不足（n<3），Shapiro-Wilk 不适用，未检验 |")
            continue
        w, p = stats.shapiro(g)
        add(f"| {lab} | {w:.3f} | {format_p(p).replace('p=', '')} | "
            f"{'正态' if p >= 0.05 else '偏离正态'} |")
    # v2.5.8：统一用 center='median'（= Brown-Forsythe，Prism 推荐），
    # 与 oneway_anova_tukey(var_equal='auto') 的切换判定完全一致。
    lev_w, lev_p = stats.levene(*groups, center="median")
    lev_ok = np.isfinite(lev_p)
    lev_concl = ("方差齐" if lev_p >= 0.05 else "方差不齐") if lev_ok \
        else "无法计算（样本量过小）"
    add(f"\n### 方差齐性（Levene = Brown-Forsythe，center=median）\n"
        f"- W = {lev_w:.3f}, {format_p(lev_p)} → {lev_concl}")

    res = oneway_anova_tukey(groups, labels, var_equal=var_equal, posthoc=posthoc)
    k = len(groups)
    df_within = N - k
    mm = {lab: g.mean() for lab, g in zip(labels, groups)}
    # 实际走哪个分支（var_equal='auto' 时由 Levene 决定）
    used_welch = bool(res["welch"])
    ph_zh = {"games_howell": "Games-Howell", "dunnett_t3": "Dunnett T3",
             "welch_t": "Welch t（不校正）", "tukey": "Tukey"}.get(
        res.get("posthoc", "tukey"), "事后检验")

    if lev_ok:
        if lev_p < 0.05:
            if used_welch:
                add(f"- 结论：方差不齐 → 已自动/显式切换 **Welch ANOVA + "
                    f"{ph_zh} 事后**（下方结果即 Welch 口径）\n")
            else:
                # L1 一致性修复（v2.5.8）：不再"建议切换却给标准值"，
                # 明确标注下方数值的假设口径。
                add("- 结论：方差不齐；**下方 F/p 为假设方差齐性的标准 ANOVA 结果，"
                    "p 值可能失真**。如需 Welch 口径，请用 "
                    "`build_stats_report(..., var_equal='auto'|'welch')`\n")
        else:
            add("- 结论：满足方差齐性前提，标准 ANOVA + Tukey 适用\n")
    else:
        add("- 结论：方差齐性无法判定（样本量过小致检验不可计算），"
            "建议结合分布可视化与 Welch 口径（var_equal='welch'）稳健性评估\n")

    if used_welch:
        # ---- Welch ANOVA + 方差不齐事后（v2.5.9 支持三种）----
        stars, _ = p_to_stars(res["anova_p"])
        add("## 3. Welch ANOVA（不假设方差齐性，v2.5.8）\n")
        add(f"- **F({res['df1']:.2f}, {res['df2']:.2f}) = {res['f_stat']:.2f}, "
            f"{format_p(res['anova_p'])} ({stars})**")
        add("- 效应量：Welch ANOVA 不适用 η²（未合并组内方差），"
            "建议以事后均值差与 95% CI 报告\n")
        vv = [g.var(ddof=1) / len(g) for g in groups]
        # v2.5.10：校正表格额外附"未校正 Welch t"p 值列（参考对照，
        # 审稿人常要求同时看到校正前/后；welch_t 分支本身即未校正，不重复）
        show_uncorr = res["posthoc"] in ("games_howell", "dunnett_t3")
        if res["posthoc"] == "games_howell":
            add("## 4. Games-Howell 事后多重比较（每组 n>50 时 Prism 推荐）\n")
            add("| 比较 | Mean Diff | q | df | p | p (Welch t, uncorr) | 显著性 |")
            add("|---|---|---|---|---|---|---|")
        elif res["posthoc"] == "dunnett_t3":
            add("## 4. Dunnett T3 事后多重比较（每组 n<50 时 Prism 推荐）\n")
            add("| 比较 | Mean Diff | t | df | p | p (Welch t, uncorr) | 显著性 |")
            add("|---|---|---|---|---|---|---|")
        else:
            add("## 4. 事后比较：Welch 校正 t 检验（未做多重比较校正，"
                "Prism 'Don't correct for multiple comparisons'）\n")
            add("| 比较 | Mean Diff | t | df | p | 显著性 |")
            add("|---|---|---|---|---|---|")
        for a, b, p in res["pairwise"]:
            ia, ib = labels.index(a), labels.index(b)
            df_ws = (vv[ia] + vv[ib]) ** 2 / (
                vv[ia] ** 2 / (len(groups[ia]) - 1)
                + vv[ib] ** 2 / (len(groups[ib]) - 1))
            t_w = abs(mm[a] - mm[b]) / np.sqrt(vv[ia] + vv[ib])
            if res["posthoc"] == "games_howell":
                stat_v = abs(mm[a] - mm[b]) / np.sqrt((vv[ia] + vv[ib]) / 2.0)
            else:
                stat_v = t_w
            st, _ = p_to_stars(p)
            p_unc = float(2.0 * stats.t.sf(t_w, df_ws))
            if show_uncorr:
                add(f"| {a} vs {b} | {mm[b]-mm[a]:+.2f} | {stat_v:.2f} | "
                    f"{df_ws:.1f} | {format_p(p).replace('p=', '')} | "
                    f"{format_p(p_unc).replace('p=', '')} | {st} |")
            else:
                add(f"| {a} vs {b} | {mm[b]-mm[a]:+.2f} | {stat_v:.2f} | "
                    f"{df_ws:.1f} | {format_p(p).replace('p=', '')} | {st} |")
        if res["posthoc"] == "games_howell":
            add("\n注：Games-Howell 每对使用独立 Welch-Satterthwaite 自由度，"
                "p 值已做家族错误率校正。\n")
        elif res["posthoc"] == "dunnett_t3":
            add("\n注：Dunnett T3 基于 studentized maximum modulus 分布（等价于"
                "单步 Sidak 校正 p=1−(1−p_raw)^m, m=k(k−1)/2），"
                "每对使用未取整 Welch-Satterthwaite 自由度。\n")
        else:
            add("\n注：每对为独立 Welch 校正 t 检验，p 值**未**做多重比较校正，"
                "解释时需注意家族错误率。\n")
        if show_uncorr:
            add("注：`p (Welch t, uncorr)` 列为未做多重比较校正的参考值"
                "（Prism 'Don't correct' 口径），结论以校正 p 列为准。\n")
        stat_method = {
            "games_howell": "Welch ANOVA with Games-Howell post hoc test",
            "dunnett_t3": "Welch ANOVA with Dunnett T3 post hoc test",
            "welch_t": "Welch ANOVA with uncorrected Welch t tests",
        }[res["posthoc"]]
    else:
        # ---- 标准 One-way ANOVA + Tukey 报告（向后兼容）----
        f_ = res["f_stat"]
        anova_p = res["anova_p"]
        allv = np.concatenate(groups)
        gm = allv.mean()
        ss_b = sum(len(g) * (g.mean() - gm) ** 2 for g in groups)
        ss_t = ((allv - gm) ** 2).sum()
        eta2 = ss_b / ss_t
        stars, _ = p_to_stars(anova_p)
        add("## 3. One-way ANOVA\n")
        add(f"- **F({k - 1}, {df_within}) = {f_:.2f}, {format_p(anova_p)} ({stars})**")
        add(f"- 效应量：η² = {eta2:.3f}（>0.14 为大效应）\n")

        mse = sum((len(g) - 1) * np.var(g, ddof=1) for g in groups) / df_within
        add("## 4. Tukey 事后多重比较\n")
        add("| 比较 | Mean Diff | q | p | 显著性 |")
        add("|---|---|---|---|---|")
        for a, b, p in res["pairwise"]:
            ia, ib = labels.index(a), labels.index(b)
            q = abs(mm[a] - mm[b]) / np.sqrt(
                mse * (1.0 / len(groups[ia]) + 1.0 / len(groups[ib])) / 2.0)
            st, _ = p_to_stars(p)
            add(f"| {a} vs {b} | {mm[b]-mm[a]:+.2f} | {q:.2f} | "
                f"{format_p(p).replace('p=', '')} | {st} |")
        add("\n注：p 值已做 Tukey 家族错误率校正，无需再次校正。\n")
        stat_method = "One-way ANOVA with Tukey's post hoc test"

    legend = format_legend(description, n=n, pairwise=res["pairwise"],
                           error_type=error_type, star_scale=star_scale,
                           stat_method=stat_method)
    add("## 5. Figure Legend\n> " + legend + "\n")
    return "\n".join(L)

def _report_ttest(groups, labels, description, error_type, star_scale, L, add, paired=False):
    a, b = (np.asarray(g, dtype=float) for g in groups)
    stat, p, method = ttest_two_groups(a, b, paired=paired)
    use_nonparam = False

    # 1. 描述统计（含 95% CI）
    add("\n## 1. 描述统计\n")
    add("| 组别 | n | Mean | SD | SEM | 95% CI |")
    add("|---|---|---|---|---|---|")
    for lab, g in zip(labels, (a, b)):
        m, sem = mean_sem(g)
        sd = g.std(ddof=1)
        ci = stats.t.ppf(0.975, len(g) - 1) * sem
        add(f"| {lab} | {len(g)} | {m:.2f} | {sd:.2f} | {sem:.2f} | "
            f"[{m-ci:.2f}, {m+ci:.2f}] |")

    # 2. 前提检验（正态性 + 方差齐性）
    add("\n## 2. 前提检验\n")
    add("### 正态性（Shapiro-Wilk，每组）\n")
    add("| 组别 | W | p | 结论 |")
    add("|---|---|---|---|")
    shapiro_results = []
    for lab, g in zip(labels, (a, b)):
        if len(g) < 3:
            add(f"| {lab} | — | NA | "
                f"样本量不足（n<3），Shapiro-Wilk 不适用，未检验 |")
            shapiro_results.append(np.nan)
            continue
        w, sp_ = stats.shapiro(g)
        shapiro_results.append(sp_)
        add(f"| {lab} | {w:.3f} | {format_p(sp_).lstrip('p=')} | "
            f"{'正态' if sp_ >= 0.05 else '偏离正态'} |")
    lev_w, lev_p = stats.levene(a, b, center="mean")
    lev_ok = np.isfinite(lev_p)
    lev_concl = ("方差齐" if lev_p >= 0.05 else "方差不齐") if lev_ok \
        else "无法计算（样本量过小）"
    add(f"\n### 方差齐性（Levene 检验，center=mean）\n"
        f"- W = {lev_w:.3f}, {format_p(lev_p)} → {lev_concl}"
        f"（方差不齐时 t 检验自动采用 Welch 校正）\n")

    # 2b. 非参数补充检验（v2.3.0）：
    # 若任一组偏离正态（Shapiro p<0.05）或样本量较小（min(n)<30），
    # 追加 Mann-Whitney U（独立）或 Wilcoxon 符号秩（配对）作为补充证据——
    # 不替换主检验结论，审稿人既看 t 又看非参更稳妥。
    min_n = min(len(a), len(b))
    any_non_normal = any(np.isfinite(sp_) and sp_ < 0.05 for sp_ in shapiro_results)
    if any_non_normal or min_n < 30:
        use_nonparam = True
        if paired:
            np_stat, np_p, np_method = wilcoxon_signed_rank(a, b)
        else:
            np_stat, np_p, np_method = mann_whitney_u(a, b)
        add(f"\n### 非参数补充检验（{'Wilcoxon 符号秩' if paired else 'Mann-Whitney U'}）\n"
            f"- 触发：{'至少一组偏离正态（Shapiro p<0.05）' if any_non_normal else '样本量较小（min(n)<30）'}"
            f"{'或样本量较小' if any_non_normal and min_n < 30 else ''}\n"
            f"- 统计量 = {np_stat:.3f}, {format_p(np_p)} "
            f"({p_to_stars(np_p)[0]})\n")

    # 3. 两组比较
    add("\n## 3. 两组比较\n")
    add(f"- 方法：**{method}**")
    add(f"- 统计量 = {stat:.3f}, {format_p(p)} ({p_to_stars(p)[0]})")
    sp = np.sqrt(((len(a) - 1) * a.var(ddof=1) +
                  (len(b) - 1) * b.var(ddof=1)) / (len(a) + len(b) - 2))
    d = (a.mean() - b.mean()) / sp
    add(f"- 效应量：Cohen's d = {d:.3f}\n")
    if use_nonparam and not paired:
        # 计算 rank-biserial correlation 作为非参数效应量
        n1, n2 = len(a), len(b)
        rb = 1 - 2 * np_stat / (n1 * n2)
        add(f"- 补充效应量：rank-biserial r = {rb:.3f}\n")
    res = {"pairwise": [(labels[0], labels[1], p)]}
    legend = format_legend(description, n=[len(a), len(b)],
                           pairwise=res["pairwise"], error_type=error_type,
                           stat_method=method, star_scale=star_scale)
    add("## 4. Figure Legend\n> " + legend + "\n")
    return "\n".join(L)

def _parse_twoway_formula(formula):
    """解析 'value ~ C(A)*C(B)' → (yname, A, B)。格式不符返回 None。

    v2.0.35 抽出（原 _report_twoway 内联逻辑），供 _report_twoway 与
    twoway_posthoc 共用，避免两处解析不一致。
    """
    import re
    m = re.match(r"\s*(\w+)\s*~\s*(.+)", formula)
    if not m:
        return None
    yname = m.group(1).strip()
    factors = []
    for f in re.findall(r"C\((\w+)\)", m.group(2)):
        if f not in factors:
            factors.append(f)
    if len(factors) != 2:
        return None
    return yname, factors[0], factors[1]


def twoway_posthoc(df, formula, alpha=0.05):
    """Two-way ANOVA 事后比较（v2.0.35 新增）。

    决策规则（对齐 GraphPad Prism 的 Two-way ANOVA 事后逻辑）：
    - **交互显著** (p_inter < alpha) → **简单效应（simple effects）分析**：
      对全部 A×B 单元格均值做**全量 Tukey HSD**（校正范围 = 所有单元格两两
      比较，最保守，与 Prism 的 Tukey 校正同思路），再筛选出"固定一个因子
      水平、比较另一个因子"的对比——
        · 每个 A 水平内：B 各水平两两比较（如每个时间点内 Ctrl vs Drug）
        · 每个 B 水平内：A 各水平两两比较（如每组药物下 0h vs 24h vs 48h）
      审稿人最常见的要求（交互显著时"在各时间点分别比较处理组"）由此覆盖。
    - **交互不显著** → **主效应事后比较**：对每个因子，直接对该因子水平
      分组做 Tukey HSD（近似做法，报告注明未按 Two-way 模型调整方差）。
    参数：
        df      : pandas DataFrame，含响应列与两个因子列
        formula : "value ~ C(A)*C(B)" 格式（响应变量为连续值）
        alpha   : 显著性阈值（默认 0.05，决定简单效应/主效应分支与星号）
    返回 dict：
        {"interaction_p": float,
         "type": "simple_effects" | "main_effects",
         "comparisons": [(对比描述 str, p float, 星号 str), ...]}
    对比描述示例：'time=0h: Ctrl vs Drug'（简单效应）、'time: 0h vs 24h'（主效应）
    """
    import statsmodels.api as sm
    from statsmodels.formula.api import ols
    # v2.5.7: 不再用 statsmodels.stats.multicomp.pairwise_tukeyhsd——它每个比较
    # 都要做 q 临界值 brentq 求根 + studentized_range 的 nquad 数值积分,
    # 深度回归(18 设计)实测占 27.9s/47s。改复用 oneway_anova_tukey 的纯 scipy
    # Tukey-Kramer 引擎(同一 studentized_range 分布,数学等价,p 值精度一致),
    # 仅省掉 statsmodels 的 q-crit 求根与进程内开销,统计结果不变。

    parsed = _parse_twoway_formula(formula)
    if parsed is None:
        raise ValueError(
            f"无法解析 formula={formula!r}，请用 'value ~ C(A)*C(B)' 格式"
        )
    yname, A, B = parsed

    # v2.5.3 防御：单元格 n<2 或零方差 → 参数化 Two-way 不可行，给出明确报错
    # （此前单观测格/格内全同值会在 ols/anova_lm 中除零，静默输出 NaN 或崩溃）
    dff = df[[A, B, yname]].dropna()
    cell_counts = dff.groupby([A, B], observed=True).size()
    bad_cnt = cell_counts[cell_counts < 2]
    if len(bad_cnt):
        raise ValueError(
            f"Two-way ANOVA 每格至少需要 2 个观测（存在单观测格："
            f"{bad_cnt.to_dict()}，请检查数据是否完整）")
    cell_var = dff.groupby([A, B], observed=True)[yname].var(ddof=0)
    bad_var = cell_var[cell_var <= 0]
    if len(bad_var):
        raise ValueError(
            f"Two-way ANOVA 存在零方差单元格（格内所有值相同："
            f"{list(bad_var.index)}），无法做参数检验")

    model = ols(formula, data=df).fit()
    tab = sm.stats.anova_lm(model, typ=2)
    inter_idx = [i for i in tab.index
                 if ":" in str(i) and str(i) != "Residual"]
    p_inter = float(tab.loc[inter_idx[0], "PR(>F)"]) if inter_idx else 1.0

    comparisons = []
    if p_inter < alpha:
        # ---- 简单效应：全量单元格 Tukey，再筛选固定因子的对比 ----
        df2 = df[[A, B, yname]].dropna().copy()
        df2["_cell"] = df2[A].astype(str) + "\u2502" + df2[B].astype(str)
        # v2.3.3（learnings 修复）：比较键方向标准化——按因子水平在数据中
        # 首次出现的顺序排列（与调用方构造数据的水平顺序一致），
        # 避免 pairwise_tukeyhsd 按字典序枚举导致 "Drug vs Sham" 而调用方
        # 期望 "Sham vs Drug" 匹配失败（2×3 析因图上 6 个组内比较丢 4 个）。
        a_order = {lv: i for i, lv in enumerate(
            dict.fromkeys(df2[A].astype(str)))}
        b_order = {lv: i for i, lv in enumerate(
            dict.fromkeys(df2[B].astype(str)))}
        # v2.5.7: 全量单元格 Tukey 改用 oneway_anova_tukey(纯 scipy Tukey-Kramer,
        # 与 statsmodels 数学等价)替代 pairwise_tukeyhsd,省 q-crit 求根开销。
        cell_labels = list(dict.fromkeys(df2["_cell"].astype(str)))
        cell_groups = [df2.loc[df2["_cell"] == c, yname].to_numpy(dtype=float)
                       for c in cell_labels]
        for g1, g2, p in oneway_anova_tukey(cell_groups, cell_labels)["pairwise"]:
            a1, b1 = g1.split("\u2502")
            a2, b2 = g2.split("\u2502")
            if a1 == a2:      # 同一 A 水平内：B 各水平比较
                if b_order[b1] > b_order[b2]:
                    b1, b2 = b2, b1
                comparisons.append(
                    (f"{A}={a1}: {b1} vs {b2}", p, p_to_stars(p)[0]))
            elif b1 == b2:    # 同一 B 水平内：A 各水平比较
                if a_order[a1] > a_order[a2]:
                    a1, a2 = a2, a1
                comparisons.append(
                    (f"{B}={b1}: {a1} vs {a2}", p, p_to_stars(p)[0]))
        ctype = "simple_effects"
    else:
        # ---- 主效应事后：对每个因子水平分组做 Tukey（近似） ----
        for fac in (A, B):
            fac_order = {lv: i for i, lv in enumerate(
                dict.fromkeys(df[fac].astype(str)))}
            fvals = df[fac].astype(str)
            fac_labels = list(dict.fromkeys(fvals))
            fac_groups = [df.loc[fvals == lv, yname].to_numpy(dtype=float)
                          for lv in fac_labels]
            for g1, g2, p in oneway_anova_tukey(fac_groups, fac_labels)["pairwise"]:
                if fac_order[g1] > fac_order[g2]:
                    g1, g2 = g2, g1
                comparisons.append(
                    (f"{fac}: {g1} vs {g2}", p, p_to_stars(p)[0]))
        ctype = "main_effects"
    return {"interaction_p": p_inter, "type": ctype,
            "comparisons": comparisons}


def rm_twoway_anova(df, subject, within, between, value, alpha=0.05,
                    sphericity="gg"):
    """重复测量 Two-way ANOVA（混合设计：between × within，v2.5.11 新增）。

    对齐 GraphPad Prism 的 Repeated measures two-way ANOVA 设计：
    - 数据：长格式，subject 嵌套在 between 组内，每个 subject 测量 within 的
      全部水平（**平衡设计**，缺失值不支持——Prism 同样要求 RM 无缺失）。
    - ANOVA 表四行：between / within / Interaction / **Subjects(matching)**。
      · between 的误差 = 受试者间变异 MS_subject(A)（df = N − a）；
      · within 与交互的误差 = MS_within×subject(A)（受试者内残差，df = (b−1)(N−a)）；
      · Subjects(matching) 行 P 检验"受试者间是否相同"（匹配有效性，
        F = MS_subject(A)/MS_within×subject(A)）。
    - 球形性：within 因子 >2 水平时按 Prism 默认**不假设球形性**，
      用 Greenhouse-Geisser 校正（sphericity="gg"），报告 epsilon 并用
      校正 df 计算 within / Interaction 的 p；within 仅 2 水平时 epsilon=1
      （球形性不适用）。Mauchly 检验（W + p）一并报告。
    - 事后：交互显著（p<alpha）→ **简单效应**（固定 between 组内比较 within
      水平，per-subject 配对 t + Sidak 校正，与 pingouin pairwise_tests 一致）；
      交互不显著 → 主效应两两比较。Prism 用合并误差项的另一种口径未采用。
    返回 dict: {method, aov, sphericity, pairwise, type}
      aov 每行 {source, ss, df1, df2, ms, f, p, p_gg(校正后或 None), eps}
    """
    d = df[[subject, between, within, value]].dropna().copy()
    d["_v"] = d[value].astype(float)
    a_levels = list(dict.fromkeys(d[between].astype(str)))
    b_levels = list(dict.fromkeys(d[within].astype(str)))
    a, b = len(a_levels), len(b_levels)
    # ---- 平衡设计校验 ----
    subj_levels = d.groupby(subject)[within].nunique()
    if (subj_levels != b).any():
        raise ValueError(
            "重复测量 two-way 要求每个 subject 测量 within 因子的全部水平"
            f"（存在缺失：{subj_levels[subj_levels != b].to_dict()}）")
    n_a = d.groupby(between)[subject].nunique()
    if (n_a < 2).any():
        raise ValueError("每个 between 组至少需要 2 个 subject")
    N = d[subject].nunique()
    # ---- SS 分解（Glantz & Slinker 标准方法）----
    grand = d["_v"].mean()
    subj_mean = d.groupby(subject)["_v"].mean()
    grp_mean = d.groupby(between)["_v"].mean()
    w_mean = d.groupby(within)["_v"].mean()
    cell = d.groupby([between, within])["_v"].mean()
    subj2grp = d.groupby(subject)[between].first()
    ss_tot = float(((d["_v"] - grand) ** 2).sum())
    ss_a = float(b * sum(n_a[x] * (grp_mean[x] - grand) ** 2 for x in a_levels))
    ss_subj = float(b * sum(
        (subj_mean[s_] - grp_mean[subj2grp[s_]]) ** 2 for s_ in subj_mean.index))
    ss_w = float(N * sum((w_mean[x] - grand) ** 2 for x in b_levels))
    ss_ab = float(sum(
        n_a[x] * (cell.loc[x, y] - grp_mean[x] - w_mean[y] + grand) ** 2
        for x in a_levels for y in b_levels))
    ss_wsubj = ss_tot - ss_a - ss_subj - ss_w - ss_ab
    df_a, df_subj, df_w, df_ab, df_wsubj = a - 1, N - a, b - 1, (a - 1) * (b - 1), (b - 1) * (N - a)
    ms_a = ss_a / df_a
    ms_subj = ss_subj / df_subj
    ms_w = ss_w / df_w
    ms_ab = ss_ab / df_ab
    ms_wsubj = ss_wsubj / df_wsubj
    F_a = ms_a / ms_subj
    F_w = ms_w / ms_wsubj
    F_ab = ms_ab / ms_wsubj
    F_subj = ms_subj / ms_wsubj
    p_a = float(stats.f.sf(F_a, df_a, df_subj))
    p_w = float(stats.f.sf(F_w, df_w, df_wsubj))
    p_ab = float(stats.f.sf(F_ab, df_ab, df_wsubj))
    p_subj = float(stats.f.sf(F_subj, df_subj, df_wsubj))
    # ---- 球形性：GG epsilon + Mauchly（宽格式原始协方差，闭合公式）----
    spher = {"factor": within, "levels": b, "epsilon_gg": 1.0,
             "mauchly_w": None, "mauchly_p": None}
    p_w_gg, p_ab_gg = p_w, p_ab
    if b > 2:
        wide = d.pivot_table(index=subject, columns=within, values="_v")
        S = wide.cov().to_numpy()
        mean_var = float(np.diag(S).mean())
        S_mean = float(S.mean())
        ss_mat = float((S ** 2).sum())
        ss_rows = float((S.mean(axis=1) ** 2).sum())
        num = (b * (mean_var - S_mean)) ** 2
        den = (b - 1) * (ss_mat - 2 * b * ss_rows + b ** 2 * S_mean ** 2)
        eps = min(num / den, 1.0)
        spher["epsilon_gg"] = eps
        if sphericity == "gg":
            df_w_gg = eps * (b - 1)
            df_wsubj_gg = eps * (b - 1) * (N - a)
            p_w_gg = float(stats.f.sf(F_w, df_w_gg, df_wsubj_gg))
            p_ab_gg = float(stats.f.sf(F_ab, df_ab * eps, df_wsubj_gg))
        # Mauchly（照 pingouin 的 double-centered 特征值法；d = 水平数−1 =
        # 正交对比数。GG 校正 p 用**混合设计** df2=(b−1)(N−a)，与 Prism 标准
        # 一致；pingouin 的 p_GG_corr 内部混用了单因子 rm_anova df，不采纳）
        n_s = wide.shape[0]
        S_pop = S - S.mean(0)[:, None] - S.mean(1)[None, :] + S.mean()
        eig = np.linalg.eigvalsh(S_pop)[1:]
        d_m = b - 1
        tol = np.finfo(float).eps * eig.max() * d_m
        eig = eig[eig > tol]
        if eig.size:
            Wm = float(np.prod(eig) / (eig.sum() / d_m) ** d_m)
            logW = np.log(Wm)
            f_ = 1 - (2 * d_m ** 2 + d_m + 2) / (6 * d_m * (n_s - 1))
            w2 = ((d_m + 2) * (d_m - 1) * (d_m - 2)
                  * (2 * d_m ** 3 + 6 * d_m ** 2 + 3 * b + 2)
                  / (288 * ((n_s - 1) * d_m * f_) ** 2))
            chi_sq = -(n_s - 1) * f_ * logW
            ddof_m = max(d_m * (d_m + 1) // 2 - 1, 1)
            p1 = stats.chi2.sf(chi_sq, ddof_m)
            p2 = stats.chi2.sf(chi_sq, ddof_m + 4)
            spher["mauchly_w"] = Wm
            spher["mauchly_p"] = float(p1 + w2 * (p2 - p1))
    # ---- ANOVA 表 ----
    aov = [
        {"source": f"{between} (between)", "ss": ss_a, "df1": df_a, "df2": df_subj,
         "ms": ms_a, "f": F_a, "p": p_a, "p_gg": None, "eps": None},
        {"source": f"{within} (within)", "ss": ss_w, "df1": df_w, "df2": df_wsubj,
         "ms": ms_w, "f": F_w, "p": p_w, "p_gg": p_w_gg, "eps": spher["epsilon_gg"]},
        {"source": "Interaction", "ss": ss_ab, "df1": df_ab, "df2": df_wsubj,
         "ms": ms_ab, "f": F_ab, "p": p_ab, "p_gg": p_ab_gg, "eps": spher["epsilon_gg"]},
        {"source": "Subjects (matching)", "ss": ss_subj, "df1": df_subj, "df2": df_wsubj,
         "ms": ms_subj, "f": F_subj, "p": p_subj, "p_gg": None, "eps": None},
    ]
    # ---- 事后：简单效应（交互显著）或主效应 ----
    pairwise = {"main_effects": [], "simple_effects": [], "type": ""}
    # 主效应 within 两两（全 subject 配对 t，Sidak m=C(b,2)）
    m_w = b * (b - 1) // 2
    wide = d.pivot_table(index=subject, columns=within, values="_v")
    for i in range(b):
        for j in range(i + 1, b):
            bi, bj = b_levels[i], b_levels[j]
            t_, p_raw = stats.ttest_rel(wide[bi], wide[bj])
            p_corr = 1.0 - (1.0 - float(p_raw)) ** m_w
            pairwise["main_effects"].append(
                (f"{within}: {bi} vs {bj}", float(t_), int(len(wide) - 1),
                 float(p_raw), float(p_corr)))
    # between 主效应两两（独立 t，合并方差；>2 组时 Tukey 简化用独立 t + Sidak）
    if a > 1:
        m_a = a * (a - 1) // 2
        for i in range(a):
            for j in range(i + 1, a):
                ai, aj = a_levels[i], a_levels[j]
                g1 = d.loc[d[between].astype(str) == ai, "_v"].to_numpy()
                g2 = d.loc[d[between].astype(str) == aj, "_v"].to_numpy()
                t_, p_raw = stats.ttest_ind(g1, g2, equal_var=True)
                p_corr = 1.0 - (1.0 - float(p_raw)) ** m_a
                pairwise["main_effects"].append(
                    (f"{between}: {ai} vs {aj}", float(t_),
                     int(len(g1) + len(g2) - 2), float(p_raw), float(p_corr)))
    # 简单效应：固定 between 组内比较 within（配对 t，df=n_a−1，Sidak m=a·C(b,2)）
    m_se = a * b * (b - 1) // 2
    for x in a_levels:
        g = d.loc[d[between].astype(str) == x]
        gw = g.pivot_table(index=subject, columns=within, values="_v")
        for i in range(b):
            for j in range(i + 1, b):
                bi, bj = b_levels[i], b_levels[j]
                t_, p_raw = stats.ttest_rel(gw[bi], gw[bj])
                p_corr = 1.0 - (1.0 - float(p_raw)) ** m_se
                pairwise["simple_effects"].append(
                    (f"{between}={x}: {bi} vs {bj}", float(t_),
                     int(len(gw) - 1), float(p_raw), float(p_corr)))
    pairwise["type"] = "simple_effects" if p_ab < alpha else "main_effects"
    return {"method": "Repeated measures two-way ANOVA (mixed design)",
            "aov": aov, "sphericity": spher, "pairwise": pairwise,
            "interaction_p": p_ab, "type": pairwise["type"]}


def _report_twoway_rm(df, subject, within, between, value, description,
                      error_type, star_scale, L, add):
    """重复测量 Two-way ANOVA 报告（v2.5.11，混合设计）。"""
    res = rm_twoway_anova(df, subject, within, between, value)
    d = df[[subject, between, within, value]].copy()
    d["_v"] = d[value].astype(float)
    # 1. 描述统计（A×B 单元格）
    add("\n## 1. 描述统计（A×B 交叉单元格）\n")
    add("| 组别 | n | Mean | SD | SEM | 95% CI |")
    add("|---|---|---|---|---|---|")
    for a_l in dict.fromkeys(d[between].astype(str)):
        for b_l in dict.fromkeys(d[within].astype(str)):
            sub = d[(d[between].astype(str) == a_l)
                    & (d[within].astype(str) == b_l)]["_v"]
            if sub.empty:
                continue
            m_, sem_ = mean_sem(sub)
            sd_ = sub.std(ddof=1)
            ci_ = stats.t.ppf(0.975, len(sub) - 1) * sem_
            add(f"| {a_l} · {b_l} | {len(sub)} | {m_:.2f} | {sd_:.2f} | "
                f"{sem_:.2f} | [{m_-ci_:.2f}, {m_+ci_:.2f}] |")
    # 2. ANOVA 表
    add("\n## 2. 重复测量 Two-way ANOVA（混合设计，v2.5.11）\n")
    add("| 来源 | SS | df | MS | F | p | p (GG 校正) | 显著性 |")
    add("|---|---|---|---|---|---|---|---|")
    for row in res["aov"]:
        st, _ = p_to_stars(row["p"])
        p_gg = format_p(row["p_gg"]).replace("p=", "") if row["p_gg"] else "—"
        df_txt = f"{row['df1']}, {row['df2']}"
        add(f"| {row['source']} | {row['ss']:.3f} | {df_txt} | {row['ms']:.3f} "
            f"| {row['f']:.3f} | {format_p(row['p']).replace('p=', '')} "
            f"| {p_gg} | {st} |")
    add("- Subjects (matching) 行 P 小 → 受试者间差异显著，重复测量设计"
        "匹配有效（Prism 同此解读）\n")
    # 3. 球形性
    sp = res["sphericity"]
    add("## 3. 球形性（Greenhouse-Geisser，Prism 默认不假设球形性）\n")
    if sp["levels"] <= 2:
        add(f"- 重复测量因子 {sp['factor']!r} 仅 {sp['levels']} 个水平，"
            "球形性概念不适用，ε = 1\n")
    else:
        add(f"- ε (Greenhouse-Geisser) = {sp['epsilon_gg']:.3f}；"
            f"Mauchly's W = {sp['mauchly_w']:.3f}, "
            f"{format_p(sp['mauchly_p'])}"
            f"（{'p<0.05 → 违反球形性，已用 GG 校正 df' if sp['mauchly_p'] is not None and sp['mauchly_p'] < 0.05 else '未违反或样本量不足'}）\n")
        add("- within 与 Interaction 行的 p (GG 校正) 即 ε 校正 df 后的结果"
            "（df2 用混合设计误差项 (b−1)(N−a)）\n")
    # 4. 事后
    ptype = res["type"]
    add(f"## 4. 事后比较（交互 {'显著 → 简单效应' if ptype == 'simple_effects' else '不显著 → 主效应'}）\n")
    comps = res["pairwise"]["simple_effects"] if ptype == "simple_effects" \
        else res["pairwise"]["main_effects"]
    add("| 比较 | t | df | p (uncorrected) | p (Sidak) | 显著性 |")
    add("|---|---|---|---|---|---|")
    for desc, t_, df_, p_raw, p_corr in comps:
        st, _ = p_to_stars(p_corr)
        add(f"| {desc} | {t_:.2f} | {df_} | "
            f"{format_p(p_raw).replace('p=', '')} | "
            f"{format_p(p_corr).replace('p=', '')} | {st} |")
    add("\n注：简单效应/主效应的两两比较为 per-subject 配对 t（between 组间为"
        "独立 t）+ Sidak 家族校正。\n")
    # 5. Figure Legend
    n_per = d.groupby(between)[subject].nunique().min()
    stat_method = (f"Two-way repeated measures ANOVA (mixed design, "
                   f"between={between}, within={within}, n={int(n_per)} "
                   f"subjects per group) with Greenhouse-Geisser correction; "
                   f"{'simple effects' if ptype == 'simple_effects' else 'main effects'} "
                   f"compared by paired t tests with Sidak correction")
    legend = (f"Figure. {description}. Data are {error_type}, n={int(n_per)} "
              f"subjects per group. {stat_method}. {star_scale}.")
    add("## 5. Figure Legend\n> " + legend + "\n")
    return "\n".join(L)


def _report_twoway(df, formula, description, error_type, star_scale, L, add,
                   posthoc=True):
    import statsmodels.api as sm
    from statsmodels.formula.api import ols

    parsed = _parse_twoway_formula(formula)
    if parsed is None:
        add("\n（无法解析 formula，请用 'value ~ C(A)*C(B)' 格式）\n")
        return "\n".join(L)
    yname, A, B = parsed

    # 1. 描述统计：A×B 交叉单元格
    add("\n## 1. 描述统计（A×B 交叉单元格）\n")
    add("| 组别 | n | Mean | SD | SEM | 95% CI |")
    add("|---|---|---|---|---|---|")
    n_cells = []
    for a_val in sorted(df[A].dropna().unique(), key=str):
        for b_val in sorted(df[B].dropna().unique(), key=str):
            sub = df[(df[A] == a_val) & (df[B] == b_val)][yname].dropna().astype(float)
            if sub.empty:
                continue
            m_, sem = mean_sem(sub)
            sd_ = sub.std(ddof=1)
            ci = stats.t.ppf(0.975, len(sub) - 1) * sem
            add(f"| {A}={a_val}, {B}={b_val} | {len(sub)} | {m_:.2f} | {sd_:.2f} | "
                f"{sem:.2f} | [{m_-ci:.2f}, {m_+ci:.2f}] |")
            n_cells.append(len(sub))
    n_min = min(n_cells) if n_cells else 0

    # 2. Two-way ANOVA（Type II）+ partial η²
    model = ols(formula, data=df).fit()
    tab = sm.stats.anova_lm(model, typ=2)
    ss_resid = tab.loc["Residual", "sum_sq"] if "Residual" in tab.index else np.nan
    add("\n## 2. Two-way ANOVA（Type II）\n")
    add("| 项 | sum_sq | df | F | p | partial η² | 显著性 |")
    add("|---|---|---|---|---|---|---|")
    for idx, row in tab.iterrows():
        st, _ = p_to_stars(row["PR(>F)"])
        if idx != "Residual" and ss_resid > 0 and np.isfinite(ss_resid):
            peta = row["sum_sq"] / (row["sum_sq"] + ss_resid)
            peta_txt = f"{peta:.3f}"
        else:
            peta_txt = "—"
        if idx == "Residual":
            # Residual 行无 F / p 值，不输出假数值
            add(f"| {idx} | {row['sum_sq']:.2f} | {int(row['df'])} | — | — | {peta_txt} | — |")
            continue
        add(f"| {idx} | {row['sum_sq']:.2f} | {int(row['df'])} | {row['F']:.2f} | "
            f"{format_p(row['PR(>F)']).lstrip('p=')} | {peta_txt} | {st} |")
    add("")

    # 3. 事后比较（v2.0.35 新增）：交互显著 → 简单效应；不显著 → 主效应 Tukey
    post_txt = ""
    ph_type = ""
    if posthoc:
        try:
            ph = twoway_posthoc(df, formula)
            ph_type = ph["type"]
            add("\n## 3. 事后比较（Two-way ANOVA 后）\n")
            if ph["type"] == "simple_effects":
                add("- 交互效应显著，采用**简单效应（simple effects）**分析："
                    "对全部 A×B 单元格均值做全量 Tukey HSD（校正范围 = 所有"
                    "单元格两两比较，最保守），以下仅列出固定一个因子水平的比较。\n")
                add("| 简单效应比较 | p | 显著性 |")
            else:
                add("- 交互效应不显著（"
                    + format_p(ph["interaction_p"]).lstrip("p=")
                    + "），采用**主效应事后比较**：对每个因子水平分组做 "
                    "Tukey HSD（近似，未按 Two-way 模型调整方差）。\n")
                add("| 主效应比较 | p | 显著性 |")
            add("|---|---|---|")
            for desc, p, stars in ph["comparisons"]:
                add(f"| {desc} | {format_p(p).lstrip('p=')} | {stars} |")
            add("\n注：简单效应校正范围 = 全部 A×B 单元格两两比较（最保守）；"
                "主效应事后为近似（未按 Two-way 模型调整方差）。\n")
            post_txt = "; ".join(
                f"{d} {format_p(p)} ({st})" for d, p, st in ph["comparisons"])
        except Exception as e:  # 事后比较失败不影响主体报告
            add(f"\n（事后比较计算失败：{type(e).__name__}: {e}）\n")

    # 4. Figure Legend（主效应 + 交互 + 事后比较，含具体 p 值）
    comps = []
    for idx, row in tab.iterrows():
        if idx != "Residual":
            comps.append(f"{idx} {format_p(row['PR(>F)'])} ({p_to_stars(row['PR(>F)'])[0]})")
    comp_text = "; ".join(comps)
    ntxt = f"n={n_min} per cell" if n_min else "n per cell varies"
    legend = (f"Figure. {description}. Data are {error_type}, {ntxt}. "
              f"Two-way ANOVA (Type II): {comp_text}.")
    if post_txt:
        legend += f" Post hoc ({'simple effects' if ph_type == 'simple_effects' else 'main effects'} Tukey HSD): {post_txt}."
    legend += f" {star_scale}."
    add("## 4. Figure Legend\n> " + legend + "\n")
    return "\n".join(L)

def _report_nested(df, outer, inner, value, description, L, add,
                   star_scale="*p<0.05, **p<0.01, ***p<0.001, ****p<0.0001"):
    """Nested 表统计报告（v2.4.5 NEW）：以单元均值为分析单元的嵌套 ANOVA。

    报告含：描述统计（组/单元数/观测数/单元均值±SEM）、Nested one-way ANOVA
    （F 分母=单元间变异）、Tukey 事后（误差=单元间变异）、变异分解
    （outer/unit/within 占比）、Figure Legend。
    """
    import pandas as _pd
    df = _pd.DataFrame(df).dropna(subset=[value]).copy()
    df[outer] = df[outer].astype(str)
    df[inner] = df[inner].astype(str)
    gs = list(dict.fromkeys(df[outer]))
    k = len(gs)

    res = nested_anova(df, outer, inner, value)

    # 1. 描述统计
    add("\n## 1. 描述统计（外层组）\n")
    add("| 组 | 单元数 n_units | 观测数 n_obs | 单元均值±SEM |")
    add("|---|---|---|---|")
    for g in gs:
        um = res["unit_means"][g]
        m_u = um.mean()
        sem_u = res["sem_units"][g]
        add(f"| {g} | {res['n_units'][g]} | {res['n_obs'][g]} | "
            f"{m_u:.2f} ± {sem_u:.2f} |")
    add("\n> 注：**单元 = {inner} 列的每个水平**（如动物/培养皿）。"
        "统计推断以单元均值为分析单元，避免假重复；"
        "观测数仅供展示，不等于有效样本量 n。\n")

    # 2. Nested one-way ANOVA
    st, _ = p_to_stars(res["anova_p"])
    add(f"\n## 2. Nested one-way ANOVA（F 分母 = 单元间变异）\n")
    add(f"- **F({res['df_between']}, {res['df_within']}) = {res['F']:.2f}, "
        f"{format_p(res['anova_p'])} ({st})**")
    add(f"- 变异分解：外层组间 {res['variance']['outer']:.1f}% / "
        f"单元间（嵌套）{res['variance']['unit']:.1f}% / "
        f"观测内 {res['variance']['within']:.1f}%\n")

    # 3. Tukey 事后（误差 = 单元间变异）
    add("\n### Tukey 事后多重比较（误差 = 单元间变异）\n")
    add("| 比较 | p | 显著性 |")
    add("|---|---|---|")
    for a, b, p in res["pairwise"]:
        st_, _ = p_to_stars(p)
        add(f"| {a} vs {b} | {format_p(p).lstrip('p=')} | {st_} |")
    add("\n注：p 值已做 Tukey 家族错误率校正（校正范围 = 单元数）。\n")

    # 4. Figure Legend
    comp_text = "; ".join(
        f"{a} vs {b} {format_p(p)} ({p_to_stars(p)[0]})"
        for a, b, p in res["pairwise"])
    n_units_min = min(res["n_units"].values())
    ntxt = (f"n={n_units_min} units per group" if len(set(res["n_units"].values())) == 1
            else f"n={min(res['n_units'].values())}-{max(res['n_units'].values())} units per group")
    legend = (f"Figure. {description}. Data are unit means ± SEM, {ntxt}. "
              f"Nested one-way ANOVA (units as analysis units): "
              f"F({res['df_between']}, {res['df_within']})={res['F']:.2f}, "
              f"{format_p(res['anova_p'])} ({st})"
              + (f"; Tukey post hoc: {comp_text}." if comp_text else ".")
              + f" {star_scale}.")
    add("\n## 4. Figure Legend\n> " + legend + "\n")
    return "\n".join(L)

def _logrank_two(time, event, group, g1, g2):
    """两组 log-rank 检验（Peto 法），无需 lifelines 依赖。"""
    time = np.asarray(time, dtype=float)
    event = np.asarray(event, dtype=int)
    group = np.asarray(group)
    times = np.unique(time)
    O1 = E1 = 0.0
    var = 0.0
    for t in times:
        at_risk = time >= t
        n_t = at_risk.sum()
        d_t = int(((time == t) & (event == 1)).sum())
        n1 = int(((time >= t) & (group == g1)).sum())
        d1 = int(((time == t) & (event == 1) & (group == g1)).sum())
        if n_t > 0:
            E1 += d_t * n1 / n_t
            O1 += d1
        if n_t > 1:
            var += d_t * (n1 / n_t) * (1 - n1 / n_t) * (n_t - d_t) / (n_t - 1)
    z = (O1 - E1) / np.sqrt(var) if var > 0 else 0.0
    p = 2 * (1 - stats.norm.cdf(abs(z)))
    return O1, E1, z, p

def _km_median(time, event):
    """Kaplan-Meier 中位生存时间：S(t) 首次 ≤ 0.5 时的时间点；未达到中位返回 nan。"""
    time = np.asarray(time, dtype=float)
    event = np.asarray(event, dtype=int)
    S = 1.0
    for t in sorted(np.unique(time)):
        n_at_risk = int((time >= t).sum())
        d = int(((time == t) & (event == 1)).sum())
        if n_at_risk > 0 and d > 0:
            S *= (1 - d / n_at_risk)
            if S <= 0.5:
                return t
    return np.nan

def _logrank_multi(time, event, group):
    """多组 log-rank 检验（Peto 法扩展，无需 lifelines 依赖）。

    返回 dict：
      - overall : (chi2, df, p)  整体检验（自由度为 k-1，χ² 分布）
      - pairwise: [(g1, g2, z, p), ...] 两两比较（未做多重比较校正，报告注明）
      - median  : {group: 中位生存期}
      - groups/k: 组列表 / 组数
    """
    time = np.asarray(time, dtype=float)
    event = np.asarray(event, dtype=int)
    group = np.asarray(group)
    gs = list(np.unique(group))
    k = len(gs)

    # 两两比较（复用两组实现）
    pairwise = []
    for i in range(k):
        for j in range(i + 1, k):
            O1, E1, z, p = _logrank_two(time, event, group, gs[i], gs[j])
            pairwise.append((gs[i], gs[j], z, p))

    # 整体检验：U = O - E，V 为协方差矩阵（每行和为 0 → 奇异，用广义逆）
    O = np.zeros(k)
    E = np.zeros(k)
    V = np.zeros((k, k))
    for t in np.unique(time):
        n_t = int((time >= t).sum())
        d_t = int(((time == t) & (event == 1)).sum())
        if n_t <= 1 or d_t == 0:
            continue
        for a in range(k):
            n_a = int(((time >= t) & (group == gs[a])).sum())
            d_a = int(((time == t) & (event == 1) & (group == gs[a])).sum())
            O[a] += d_a
            E[a] += d_t * n_a / n_t
            for b in range(k):
                n_b = int(((time >= t) & (group == gs[b])).sum())
                V[a, b] += (d_t * (n_t - d_t) / (n_t - 1) *
                            ((1.0 if a == b else 0.0) * n_a / n_t -
                             n_a * n_b / (n_t * n_t)))
    U = O - E
    chi2 = float(U @ np.linalg.pinv(V) @ U) if k > 1 else 0.0
    df = k - 1
    p = float(1.0 - stats.chi2.cdf(chi2, df)) if df > 0 else 1.0
    medians = {g: _km_median(time[group == g], event[group == g]) for g in gs}
    return {"overall": (chi2, df, p), "pairwise": pairwise,
            "median": medians, "groups": gs, "k": k}

def _ensure_lifelines():
    """确保 lifelines 可用；缺失时惰性安装到当前环境（Cox 回归专用）。

    返回已 import 的 lifelines 模块。安装失败（无网络/无权限）时抛出 ImportError，
    提示用户手动安装——绝不静默吞掉。log-rank 检验路径不调用本函数，保持零依赖。

    v2.7.4 NEW：原先仅在缺失时报错让用户手动 `pip install lifelines`；
    现改为按需自动安装（写入当前解释器所在环境），与 ensure_env.py 的 REQUIRED 双保险。
    """
    try:
        import lifelines  # noqa: F401
        return lifelines
    except ImportError:
        pass
    import subprocess
    import sys
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "--quiet", "lifelines"],
            check=True,
        )
    except Exception as e:  # 网络/镜像/权限等导致安装失败
        raise ImportError(
            f"cox_regression() 需要 lifelines，但自动安装失败（{type(e).__name__}: {e}）。"
            "请手动安装：pip install lifelines。"
            "（log-rank 检验本身不依赖 lifelines，只有 Cox 功能需要。）")
    import lifelines  # 安装成功，重导入
    return lifelines


def cox_regression(time, event, group, reference=None):
    """Cox 比例风险回归：多组生存数据 → 各组 vs 参照组的 HR + 95% CI + Wald p。

    v2.4.3 NEW。lifelines 按需自动安装——log-rank 检验保持零依赖；仅 Cox 功能
    需要 lifelines，调用本函数时若缺失会自动 pip 安装到当前环境（无需手动）。
    参照组默认取组列表中第一个
    （np.unique 排序结果），可用 reference= 显式指定。

    返回 dict：
      - "reference"  : 参照组名
      - "comparisons": [(组名, HR, ci_low, ci_high, p), ...]
                       （参照组自身为 (ref, 1.0, 1.0, 1.0, nan)）
      - "overall_p"  : 整体检验 p（似然比检验，LR test）
      - "ph_p"       : 比例风险（PH）假设检验 p（Schoenfeld 残差，取各变量最小
                       p；无法检验时为 nan）
      - "n_events"   : 事件总数
      - "used_lifelines": True
    """
    _ensure_lifelines()              # 缺失则按需自动安装；失败抛清晰 ImportError
    from lifelines import CoxPHFitter
    import pandas as pd

    time = np.asarray(time, dtype=float)
    event = np.asarray(event, dtype=int)
    group = np.asarray(group)
    gs_sorted = list(np.unique(group))
    # 组列表按数据出现顺序（不排序），保持用户数据排列
    gs = []
    for g in group:
        if g not in gs:
            gs.append(g)
    if len(gs) < 2:
        raise ValueError("Cox 回归至少需要 2 组。")
    if reference is None:
        # 优先识别对照组常见命名；否则取数据中首次出现的组
        ctrl_kw = ("control", "ctrl", "vehicle", "sham", "wt", "nc", "con",
                   "对照", "假手术")
        for g in gs:
            gl = str(g).lower()
            if gl in ctrl_kw or any(k in gl for k in ctrl_kw):
                reference = g
                break
        if reference is None:
            reference = gs[0]
    if reference not in gs:
        raise ValueError(f"reference={reference!r} 不在组列表中：{gs}")

    # 哑变量编码（drop_first=False 保留全组，建模前剔除参照列——
    # 不用 formula 字符串，避免组名含连字符/空格时被 formulaic 误解析为运算）
    df = pd.DataFrame({"T": time, "E": event, "grp": group})
    df = pd.get_dummies(df, columns=["grp"], prefix="grp", drop_first=False)
    ref_col = f"grp_{reference}"
    cols = [c for c in df.columns if c.startswith("grp_") and c != ref_col]
    if not cols:
        raise ValueError("除参照组外无其他组，无法建模。")

    cph = CoxPHFitter()
    cph.fit(df.drop(columns=[ref_col]), duration_col="T", event_col="E")
    sm = cph.summary

    comparisons = [(reference, 1.0, 1.0, 1.0, float("nan"))]
    for c in cols:
        gname = c[len("grp_"):]
        hr = float(np.exp(sm.loc[c, "coef"]))
        ci_lo = float(np.exp(sm.loc[c, "coef lower 95%"]))
        ci_hi = float(np.exp(sm.loc[c, "coef upper 95%"]))
        p = float(sm.loc[c, "p"])
        comparisons.append((gname, hr, ci_lo, ci_hi, p))

    overall_p = float(cph.log_likelihood_ratio_test().p_value)
    ph_p = float("nan")
    ph_ok = False
    try:
        res = cph.check_assumptions(df.drop(columns=[ref_col]), show_plots=False)
        # lifelines 0.30.x：无违例时返回空 list；有违例时返回
        # (violations, test_statistics)，test_statistics 含 "p" 列
        if isinstance(res, (tuple, list)) and len(res) > 1 \
                and res[1] is not None:
            test_stat = res[1]
            if hasattr(test_stat, "columns") \
                    and "p" in getattr(test_stat, "columns", []):
                ph_p = float(np.asarray(test_stat["p"], dtype=float).min())
                ph_ok = True
        elif isinstance(res, (tuple, list)) and len(res) == 0:
            # 无违例 → 比例风险假设成立
            ph_p, ph_ok = 1.0, True
    except Exception:
        ph_p, ph_ok = float("nan"), False

    return {"reference": reference, "comparisons": comparisons,
            "overall_p": overall_p, "ph_p": ph_p, "ph_ok": ph_ok,
            "n_events": int(event.sum()), "used_lifelines": True}


def _report_survival(time, event, group, description, L, add,
                     add_cox=True, cox_reference=None):
    time = np.asarray(time, dtype=float)
    event = np.asarray(event, dtype=int)
    group = np.asarray(group)
    gs = list(np.unique(group))
    k = len(gs)

    add("\n## 1. Kaplan-Meier 生存分析\n")
    add("| 组 | n | 事件 | 删失 | 中位生存期 |")
    add("|---|---|---|---|---|")
    for g in gs:
        mask = group == g
        n = int(mask.sum())
        n_ev = int((event[mask] == 1).sum())
        n_cn = n - n_ev
        med = _km_median(time[mask], event[mask])
        med_txt = f"{med:.1f}" if np.isfinite(med) else "未达到"
        add(f"| {g} | {n} | {n_ev} | {n_cn} | {med_txt} |")

    cox_block = ""
    if add_cox:
        cox_block = _cox_report_md(time, event, group, cox_reference)

    if k >= 2:
        res = _logrank_multi(time, event, group)
        chi2, df, p = res["overall"]
        st, _ = p_to_stars(p)
        add(f"\n### 整体 log-rank 检验（Peto 法，{k} 组）")
        add(f"- **χ²({df}) = {chi2:.2f}, {format_p(p)} ({st})**")
        if k > 2:
            add("\n### 两两比较（未做多重比较校正，参考用）")
            add("| 比较 | z | p | 显著性 |")
            add("|---|---|---|---|")
            for g1, g2, z, pp in res["pairwise"]:
                st_, _ = p_to_stars(pp)
                add(f"| {g1} vs {g2} | {z:.2f} | {format_p(pp).lstrip('p=')} | {st_} |")
        comp_text = "; ".join(
            f"{g1} vs {g2} {format_p(pp)} ({p_to_stars(pp)[0]})"
            for g1, g2, z, pp in res["pairwise"])
        legend = (
            f"Figure. {description}. Kaplan-Meier survival curves; log-rank test "
            f"(Peto): overall χ²({df})={chi2:.2f}, {format_p(p)} ({st})"
            + (f"; pairwise: {comp_text}." if comp_text else ".")
            + " *p<0.05, **p<0.01, ***p<0.001, ****p<0.0001."
        )
        add("\n## 2. Figure Legend\n> " + legend + "\n")
    else:
        add("\n- 仅一组，无法做 log-rank 比较。\n")

    # v2.4.3 NEW：Cox 回归块插在 Figure Legend 之后（序号顺延为 3）
    if cox_block:
        add(cox_block)
    return "\n".join(L)

def _cox_report_md(time, event, group, cox_reference=None):
    """生成 Cox 比例风险回归的 Markdown 报告块（v2.4.3 NEW）。

    lifelines 未安装或计算失败时输出提示性文本，不中断主报告。
    返回含 "\n" 前缀的完整块；无需 Cox 时返回空串（由调用方决定是否插入）。
    """
    try:
        cr = cox_regression(time, event, group, reference=cox_reference)
    except ImportError:
        return ("\n## 3. Cox 比例风险回归\n"
                "- （lifelines 自动安装失败，跳过；请手动 `pip install lifelines` "
                "以启用 HR + 95% CI 输出）\n")
    except Exception as e:
        return (f"\n## 3. Cox 比例风险回归\n"
                f"- （计算失败：{type(e).__name__}: {e}）\n")

    ref = cr["reference"]
    ph_note = ("成立" if cr["ph_ok"] else "不成立（Schoenfeld 残差检验提示违反）") \
        if cr["ph_ok"] else "未通过检验（建议谨慎解释 HR）"
    if np.isfinite(cr["ph_p"]):
        ph_txt = (f"PH 假设检验（Schoenfeld 残差）p={cr['ph_p']:.3f} → "
                  f"比例风险假设{ph_note}")
    else:
        ph_txt = "PH 假设未能检验"
    lines = [
        "\n## 3. Cox 比例风险回归",
        f"- 参照组：**{ref}**；事件数：{cr['n_events']}；",
        f"- 整体检验（似然比）：{format_p(cr['overall_p'])}",
        f"- {ph_txt}",
        "",
        "| 组 vs 参照 | HR | 95% CI | p | 显著性 |",
        "|---|---|---|---|---|",
    ]
    for gname, hr, lo, hi, p in cr["comparisons"]:
        if gname == ref:
            lines.append(f"| {gname}（参照） | 1.00 | — | — | — |")
            continue
        st_, _ = p_to_stars(p)
        lines.append(f"| {gname} vs {ref} | {hr:.2f} | "
                     f"[{lo:.2f}, {hi:.2f}] | "
                     f"{format_p(p).lstrip('p=')} | {st_} |")
    lines.append("")
    lines.append("注：HR < 1 表示相对参照组死亡风险更低（生存获益）。"
                 "HR 的 95% CI 跨 1 时通常视为无统计学意义。\n")
    return "\n".join(lines)

def _report_contingency(table, description, L, add,
                       star_scale="*p<0.05, **p<0.01, ***p<0.001, ****p<0.0001"):
    table = np.asarray(table, dtype=float)
    table_int = table.astype(int)
    chi2, p, dof, exp = stats.chi2_contingency(table_int)

    # 1. 数据矩阵回显 + 行/列百分比（与 Prism 的 Contingency tab 同构）
    add("\n## 1. 数据矩阵（观察频数 + 行 %）\n")
    n_rows, n_cols = table_int.shape
    row_totals = table_int.sum(axis=1, keepdims=True)
    # 表头
    head = "| 类别 | " + " | ".join(f"列{j+1}" for j in range(n_cols)) + " | 行合计 |"
    sep = "|---" * (n_cols + 2) + "|"
    add(head)
    add(sep)
    for i in range(n_rows):
        cells = [f"{int(table_int[i, j])} ({table_int[i, j] / row_totals[i, 0] * 100:.1f}%)"
                 for j in range(n_cols)]
        add(f"| 行{i+1} | " + " | ".join(cells) + f" | {int(row_totals[i, 0])} |")
    col_totals = table_int.sum(axis=0)
    add(f"| 列合计 | " + " | ".join(f"{int(c)}" for c in col_totals) + f" | {int(table_int.sum())} |\n")

    # 2. 期望频数检查（决定是否能用卡方 vs 是否切 Fisher）
    min_exp = float(exp.min())
    add("## 2. 期望频数检查\n")
    add(f"- 最小期望频数 = {min_exp:.2f}"
        + ("（≥5：卡方检验有效）" if min_exp >= 5
           else "（<5：考虑用 Fisher 精确检验或合并行/列）"))

    # 3. 检验结果
    add("\n## 3. 检验结果\n")
    add(f"- **卡方检验：χ²({dof}) = {chi2:.2f}, {format_p(p)} "
        f"({p_to_stars(p)[0]})**")
    if n_rows == 2 and n_cols == 2 and min_exp < 5:
        odds, fp = stats.fisher_exact(table_int)
        add(f"- 小样本 2×2（期望频数<5）：Fisher 精确检验 "
            f"odds ratio = {odds:.3f}, {format_p(fp)}")
    add("")

    # 4. Figure Legend（与其它四类报告结构对齐；v2.0.10 补齐）
    stat_method = ("Fisher's exact test"
                   if (n_rows == 2 and n_cols == 2 and min_exp < 5)
                   else "Pearson's chi-squared test")
    legend = (f"Figure. {description}. Two-way contingency table; n={int(table_int.sum())}. "
              f"{stat_method}: χ²={chi2:.2f} (dof={dof}), {format_p(p)} "
              f"({p_to_stars(p)[0]}). {star_scale}.")
    add("## 4. Figure Legend\n> " + legend + "\n")
    return "\n".join(L)


# =====================================================================
# § Nested / Parts of whole / Multiple variables 三表型封装（v2.3.0）
# =====================================================================

def prism_nested_bars(ax, df, outer, inner, value, palette="okabe_ito",
                      width=0.7, dot_size=None, error_type="sem",
                      show_mean_bar=True, show_unit_sem=True,
                      markers=None,
                      legend_outside=True, legend_loc=None):
    """GraphPad Prism 风格 Nested 图（v2.4.6 按 Prism Nested 图模式重写）。

    **Prism Nested 图的标志性特征（对齐 GraphPad Prism 9/10）**：
      - x 轴 = 外层组（每组一个位置）；
      - 每组内：**每个内层单元（animal/dish）的原始测量聚成一簇**
        （簇内 jitter 展开，展示单元内变异），簇间 x 分隔；
      - 组均值（= 单元均值平均）用**跨组粗横线**（mean bar）标出，
        附 ±单元均值 SEM 竖线；
      - **无柱**——Prism nested 图默认不带柱，组水平用横线表达。

    统计口径见 nested_anova()（以单元均值为分析单元，避免假重复）。

    Parameters
    ----------
    ax : matplotlib.axes.Axes
    df : pd.DataFrame 长格式数据
    outer : str  外层分组列名（如 "treatment"；每水平一组）
    inner : str  内层单元列名（如 "animal"/"dish"；每水平一个独立单元）
    value : str  观测值列名
    palette : str | Sequence[color]
    width : float  每组总宽（簇分布范围）
    dot_size : float | None  显式指定则不再自适应
    error_type : "sem" | "sd"  组均值横线的误差类型（默认 sem，单元均值口径）
    show_mean_bar : bool  是否画组均值横线（Prism 默认画）
    show_unit_sem : bool  是否在组均值线上画 ±SEM 竖线（默认画）
    markers      : Sequence[str] | None  按内层单元轮转的点形状列表
                   （如 ["o","s","^","D"]；默认 None 全部圆点）
    legend_outside : legend 放 ax 外右侧（保留参数兼容；簇=组色，无需 legend）
    legend_loc     : 手动指定 legend 位置（覆盖 legend_outside）

    Returns
    -------
    dict  {
        "outer": list[str],                    # 外层组（= x 刻度）
        "positions": np.ndarray,               # 每组中心 x（供 bracket 标注）
        "cluster_positions": {outer: np.ndarray},  # 每组各单元簇中心 x
        "means": np.ndarray,                   # 组均值（单元均值平均）
        "sems": np.ndarray,                    # 单元均值 SEM/SD（横线误差）
        "n": np.ndarray,                       # 每组单元数（独立样本 n）
        "unit_means": {outer: np.ndarray},     # 每组各单元均值
        "unit_data": {outer: {unit: np.ndarray}},  # 每组各单元原始测量
    }
    """
    import pandas as _pd
    df = _pd.DataFrame(df).dropna(subset=[value]).copy()
    df[outer] = df[outer].astype(str)
    df[inner] = df[inner].astype(str)
    outer_cats = list(dict.fromkeys(df[outer]))
    n_outer = len(outer_cats)
    if isinstance(palette, (list, tuple)) and len(palette) > 0:
        colors = list(palette)[:n_outer]
    else:
        seq = palette_sequence(palette if isinstance(palette, str) else "okabe_ito")
        colors = (seq * ((n_outer // len(seq)) + 1))[:n_outer]

    # 按单元聚合：单元均值（统计）与原始测量（绘图）
    unit_means = {}
    unit_data = {}
    cluster_positions = {}
    n_units_arr = np.zeros(n_outer, dtype=int)
    means = np.zeros(n_outer)
    sems = np.zeros(n_outer)
    raw_all = df[value].to_numpy(dtype=float)
    for oi, oc in enumerate(outer_cats):
        gdf = df[df[outer] == oc]
        units = []
        data = {}
        for u, udf in gdf.groupby(inner):
            vals = udf[value].to_numpy(dtype=float)
            data[str(u)] = vals
            units.append(float(vals.mean()))
        um = np.asarray(units, dtype=float)
        unit_means[oc] = um
        unit_data[oc] = data
        n_units_arr[oi] = len(um)
        means[oi] = um.mean()
        sems[oi] = (um.std(ddof=1) / np.sqrt(len(um)) if error_type == "sem"
                    else um.std(ddof=1)) if len(um) > 1 else 0.0
        # 簇中心：组宽内均分
        n_u = max(len(um), 1)
        step = width / n_u
        cluster_positions[oc] = x_grp = \
            (np.arange(n_u) - (n_u - 1) / 2) * step

    # v2.4.6：ylim 以**所有原始测量**为数据范围（散点=原始值，非均值）
    if dot_size is None:
        ds_pt = common_point_size(len(raw_all), max(1, n_outer))
        dot_size = ds_pt ** 2
    x = np.arange(n_outer)
    ax.set_xlim(-0.5, n_outer - 0.5)
    ymin = min(0.0, raw_all.min() * 1.15)
    ymax = max(0.0, raw_all.max() * 1.15)
    if show_mean_bar:
        ymax = max(ymax, float(means.max()) * 1.3)
    ax.set_ylim(ymin, ymax)

    # v2.4.7：不同内层单元用不同形状（marker 轮转），同组内簇可区分
    _marker_pool = list(markers) if markers else ["o"]
    for oi, oc in enumerate(outer_cats):
        cxs = cluster_positions[oc]
        for u_i, (u_name, vals) in enumerate(unit_data[oc].items()):
            add_individual_dots(ax, x[oi] + cxs[u_i], vals, color=colors[oi],
                                width=width / max(len(unit_data[oc]), 1) * 0.85,
                                dot_size=dot_size,
                                marker=_marker_pool[u_i % len(_marker_pool)])
        # Prism mean bar：跨组粗横线 + ±SEM 竖线（线宽对齐全局 0.75，v2.4.7）
        if show_mean_bar:
            ax.plot([x[oi] - width / 2, x[oi] + width / 2],
                    [means[oi], means[oi]], color="black", lw=0.75, zorder=6)
        if show_unit_sem and sems[oi] > 0:
            ax.errorbar(x[oi], means[oi], yerr=sems[oi], fmt="none",
                        ecolor="black", elinewidth=0.75, capsize=3.0,
                        capthick=0.75, zorder=6)
    ax.set_xticks(x)
    ax.set_xticklabels([str(o) for o in outer_cats])
    finish_axes(ax, data_max=float(raw_all.max()))
    return {"outer": [str(o) for o in outer_cats],
            "positions": x, "cluster_positions": cluster_positions,
            "means": means, "sems": sems, "n": n_units_arr,
            "unit_means": unit_means, "unit_data": unit_data}


def prism_pie(ax, sizes, labels, palette="okabe_ito", startangle=90,
              counterclock=False, pct=True, **kwargs) -> list:
    """饼图（Parts of whole 表）—— matplotlib.pie 直接封装，配色用色盲安全色板。

    Parameters
    ----------
    sizes : array-like  各部分数值（自动归一化为比例）
    labels : list[str]
    pct : bool | str  True → "%1.1f%%"；字符串用作文本格式；False/None → 不显示

    Returns
    -------
    list[matplotlib.patches.Wedge]  各扇形 patch（可后续设属性）
    """
    sizes = np.asarray(sizes, float)
    # v2.5.5 预检（此前上游 matplotlib 抛英文 ValueError 无指引）：
    # 全零 → "All wedge sizes are zero"；负值 → "Wedge sizes must be non negative"
    if len(sizes) == 0:
        raise ValueError("饼图/环形图需要至少 1 个数据")
    if np.any(sizes < 0):
        raise ValueError(
            f"饼图/环形图数据不能为负（存在负值: {sizes[sizes < 0].tolist()}）")
    if np.sum(sizes) <= 0:
        raise ValueError(
            "饼图/环形图数据总和必须 > 0（当前全为零或非正，无法绘制）")
    colors = palette_sequence(palette)[:len(sizes)]
    fmt = ("%1.1f%%" if pct is True else pct) if pct else None
    wedges, texts, autotexts = ax.pie(
        sizes, labels=labels, colors=colors, startangle=startangle,
        counterclock=counterclock, autopct=fmt,
        wedgeprops={"edgecolor": "black", "linewidth": 0.5},
        textprops={"fontsize": 7},
        **kwargs,
    )
    return list(wedges)


def prism_donut(ax, sizes, labels, center_text=None, palette="okabe_ito", **kwargs) -> list:
    """环形图（Parts of whole 表）—— 饼图中心挖空，可放总数/总计/标题。

    Parameters
    ----------
    center_text : str | None  中心文本（如 "n=120"）

    Returns
    -------
    list  饼图 wedges
    """
    wedges = prism_pie(ax, sizes, labels, palette=palette, **kwargs)
    ax.add_artist(plt.Circle((0, 0), 0.55, fc="white", ec="black", linewidth=0.75))
    if center_text:
        ax.text(0, 0, center_text, ha="center", va="center", fontsize=8)
    ax.axis("equal")
    return list(wedges)


def prism_pairplot(df, cols=None, hue=None, palette="okabe_ito", diag_kind="kde"):
    """散点矩阵（Multiple variables 表）—— 下三角散点+对角线 KDE/直方图。

    Parameters
    ----------
    df : pd.DataFrame
    cols : list[str] | None  数值列；None = df.select_dtypes("number").columns
    hue : str | None  分类着色列
    diag_kind : {"kde", "hist"}

    Returns
    -------
    (fig, axes) : function **内部 plt.subplots() 自建 figure**——调用方
    **不要** plt.figure() / plt.clf() 预建 figure，否则 fig.savefig() 保存的是
    调用方空 figure，所有 panels 丢失。直接接收返回值：
        fig, axes = prism_pairplot(df, cols=..., hue=...)
        fig.suptitle(...)
        save_figure(fig, name, out_dir)

    Example
    -------
    >>> import numpy as np
    >>> import pandas as pd
    >>> from scripts.prism_theme import (
    ...     apply_prism_theme, prism_pairplot)
    >>>
    >>> # 60 行:3 cohort × 20 重复 × 3 个数值变量
    >>> rng = np.random.default_rng(0)
    >>> rows = [{"cohort": c, "a": rng.normal(m, 8),
    ...          "b": rng.normal(m*0.7, 5),
    ...          "c": rng.normal(m*1.3, 6)}
    ...         for c in ["WT", "KO-A", "KO-B"]
    ...         for m in [50, 65, 40] for _ in range(20)]
    >>> df = pd.DataFrame(rows)
    >>>
    >>> apply_prism_theme()
    >>> fig, axes = prism_pairplot(df, cols=["a", "b", "c"], hue="cohort")
    >>> fig.suptitle("Pairplot (lower-triangle + KDE diag)")
    >>> fig.savefig("pairplot.png", dpi=300, bbox_inches="tight")
    """
    import pandas as _pd
    df = _pd.DataFrame(df)
    if cols is None:
        cols = df.select_dtypes(include="number").columns.tolist()
    n = len(cols)
    fig, axes = plt.subplots(n, n, figsize=(2.2 * n, 2.2 * n))
    if n == 1:
        axes = np.array([[axes]])
    hue_cats = (df[hue].unique() if hue else [None])
    colors = palette_sequence(palette)[:max(1, len(hue_cats))]
    for i in range(n):
        for j in range(n):
            ax = axes[i, j]
            if i == j:
                for c, cat in zip(colors, hue_cats):
                    sub = df[df[hue] == cat] if hue else df
                    vals = sub[cols[i]].dropna().values
                    if len(vals) == 0:
                        continue
                    if diag_kind == "kde" and len(vals) > 1:
                        kde = stats.gaussian_kde(vals)
                        xs = np.linspace(vals.min(), vals.max(), 200)
                        ax.plot(xs, kde(xs), color=c, lw=0.75)
                        ax.fill_between(xs, kde(xs), color=c, alpha=0.25)
                    else:
                        ax.hist(vals, bins=15, color=c, alpha=0.55,
                                edgecolor="black", linewidth=0.5)
                ax.set_yticks([])
            elif i > j:
                for c, cat in zip(colors, hue_cats):
                    sub = df[df[hue] == cat] if hue else df
                    ax.scatter(sub[cols[j]], sub[cols[i]], s=15, color=c,
                               edgecolor="black", linewidth=0.3, alpha=0.7)
                # v2.4.2：散点面板 y 轴统一收尾（顶刻度不再悬空）；
                # 对角线 KDE 面板保持无刻度（密度轴无意义，标准做法）
                try:
                    finish_axes(ax)
                except Exception:
                    pass
            else:
                ax.axis("off")
            ax.tick_params(labelsize=5)
            for s in ["top", "right"]:
                ax.spines[s].set_visible(False)
            if i == n - 1:
                ax.set_xlabel(cols[j], fontsize=7)
            if j == 0:
                ax.set_ylabel(cols[i], fontsize=7)
    plt.tight_layout()
    return fig, axes


def prism_facet_boxplot(data, x, y, facet, hue=None, palette="okabe_ito",
                        ncols=3, dot_size=None):
    """按 facet 分面的箱线图（Multiple variables 表）—— 类似 seaborn catplot kind="box"。

    Parameters
    ----------
    data : pd.DataFrame
    x, y, facet : str  列名
    hue : str | None  嵌套分类
    ncols : int  每行分面数

    Returns
    -------
    (fig, axes_flat) : function **内部 plt.subplots() 自建 figure**——调用方
    **不要** plt.figure() / plt.clf() 预建 figure，否则 fig.savefig() 保存的是
    调用方空 figure，所有 subplots 丢失。直接接收返回值：
        fig, axes = prism_facet_boxplot(data, x=..., y=..., facet=..., ncols=3)
        fig.suptitle(...)
        save_figure(fig, name, out_dir)

    Example
    -------
    >>> import numpy as np
    >>> import pandas as pd
    >>> from scripts.prism_theme import (
    ...     apply_prism_theme, prism_facet_boxplot)
    >>>
    >>> # 宽表 90 行:3 sample × 3 gene × 10 技术重复
    >>> rng = np.random.default_rng(0)
    >>> rows = [{"sample": s, "gene": g,
    ...          "expr": rng.normal(m, 2)}
    ...         for s in ["WT", "KO-A", "KO-B"]
    ...         for g in ["GAPDH", "ACTB", "TUBA"]
    ...         for m, _ in zip([10, 15, 8, 12, 18, 9], range(60))]
    >>> df = pd.DataFrame(rows)
    >>>
    >>> apply_prism_theme()
    >>> fig, axes = prism_facet_boxplot(
    ...     df, x="gene", y="expr", facet="sample", ncols=3)
    >>> fig.suptitle("Expression per gene, faceted by sample")
    >>> fig.savefig("facet.png", dpi=300, bbox_inches="tight")
    """
    import pandas as _pd
    data = _pd.DataFrame(data)
    cats = data[facet].dropna().unique()
    nrows = (len(cats) + ncols - 1) // ncols
    fig, axes = plt.subplots(nrows, ncols, figsize=(3 * ncols, 2.5 * nrows),
                             sharey=True)
    axes_flat = np.array(axes).reshape(-1)
    n_per = max(1, len(data) // max(1, len(cats)))
    if dot_size is None:
        dot_size = common_point_size(n_per, 1) ** 2
    for ax, cat in zip(axes_flat, cats):
        sub = data[data[facet] == cat]
        if len(sub) == 0 or sub[x].nunique() == 0:
            ax.axis("off")
            continue
        x_cats = sub[x].dropna().unique()
        groups = [sub[sub[x] == xi][y].dropna().values for xi in x_cats]
        labels = [str(xi) for xi in x_cats]
        prism_boxplot(ax, groups, labels, palette=palette)
        ax.set_title(str(cat), fontsize=8)
    for ax in axes_flat[len(cats):]:
        ax.axis("off")
    plt.tight_layout()
    return fig, axes_flat


# =====================================================================
# § Mann-Whitney U / Wilcoxon 符号秩非参数检验（v2.3.0）
# =====================================================================

def mann_whitney_u(a, b, alternative="two-sided"):
    """Mann-Whitney U 双侧非参数独立样本比较（小样本/非正态时替代 t test）。

    接口对齐 `ttest_two_groups`：返回 (statistic, p_value, method)。

    Parameters
    ----------
    a, b : array-like
    alternative : {"two-sided", "less", "greater"}

    Returns
    -------
    tuple[float, float, str]
        (U_statistic, p_value, "Mann-Whitney U")
    """
    a = np.asarray(a, float).ravel()
    b = np.asarray(b, float).ravel()
    if len(a) < 1 or len(b) < 1:
        raise ValueError("Mann-Whitney U 至少需要每组 1 个观测")
    res = stats.mannwhitneyu(a, b, alternative=alternative, use_continuity=True)
    return (float(res.statistic), float(res.pvalue), "Mann-Whitney U")


def wilcoxon_signed_rank(a, b, zero_method="wilcox", alternative="two-sided"):
    """Wilcoxon 符号秩检验（配对样本；非正态时替代 paired t test）。

    接口对齐 `ttest_two_groups`：返回 (statistic, p_value, method)。

    Parameters
    ----------
    a, b : array-like  长度相同（配对）
    zero_method : {"wilcox", "pratt", "zsplit"}  scipy.stats.wilcoxon 选项
    alternative : {"two-sided", "less", "greater"}

    Returns
    -------
    tuple[float, float, str]
        (W_statistic, p_value, "Wilcoxon signed-rank")

    Raises
    ------
    ValueError  长度不等 / 少于 1 对
    """
    a = np.asarray(a, float).ravel()
    b = np.asarray(b, float).ravel()
    if len(a) != len(b):
        raise ValueError(f"Wilcoxon 配对检验要求长度相同，got {len(a)} vs {len(b)}")
    if len(a) < 1:
        raise ValueError("Wilcoxon 至少需要 1 对观测")
    res = stats.wilcoxon(a, b, zero_method=zero_method, alternative=alternative)
    return (float(res.statistic), float(res.pvalue), "Wilcoxon signed-rank")


# =====================================================================
# § 产物配套脚本落盘（v2.3.2 NEW）
# =====================================================================

def emit_run_script(name, out_dir=None, source=None, header=True):
    """把"产出当前图/报告的同一份脚本"按 ``{name}.py`` 落盘,与
    ``save_figure(name=...)`` / ``write_report(name=...)`` 的图/报告**同前缀配套**。

    解决"图命名一致、但忘了给脚本也起同名"的痛点——脚本里末尾加一行
    ``emit_run_script("foo", out_dir="out")``,会在 out/ 里同时出现
    ``foo.py`` / ``foo.png`` / ``foo.pdf`` / ``foo.html`` / ``foo_report.md``。

    Parameters
    ----------
    name : str   同前缀基础名（生成 ``{name}.py``）
    out_dir : str | None  落盘目录；``None`` = 当前工作目录
    source : str | None  自定义源码；默认用 ``inspect`` 抓调用栈顶层 user 脚本
    header : bool  是否在落盘文件最上方加备注（默认 True）

    Returns
    -------
    pathlib.Path  实际写入的 .py 路径

    Notes
    -----
    默认行为依赖于调用脚本**有可读的磁盘文件**（标准 .py 启动方式）。
    - Jupyter 单元/IPython REPL 调用：``__file__`` 不存在时,会回退到把传入的
      ``source`` 落盘(若 source=None 则报错)。
    - 不会修改/重写 `name.png` 等产物,只新增一个 ``name.py``,**幂等**。

    Example
    -------
    标准用法（脚本末尾加一行即可）::

        from scripts.prism_theme import (
            apply_prism_theme, prism_bars, save_figure, write_report,
            emit_run_script, build_stats_report,
        )
        # ... 画图 + save_figure(fig, "my_3groups", OUT) ...
        # ... write_report("my_3groups", report_md, OUT) ...
        emit_run_script("my_3groups", out_dir="out")   # 自动落盘 my_3groups.py
    """
    import inspect as _inspect
    import os as _os
    from pathlib import Path as _Path

    if out_dir is None:
        out_dir = "."
    out_dir_path = _Path(out_dir)
    out_dir_path.mkdir(parents=True, exist_ok=True)

    caller_name = ""
    if source is None:
        # 走调用栈,找出第一个非 prism_theme.py 的 .py 用户脚本
        frame = _inspect.currentframe()
        while frame is not None:
            f_path = frame.f_globals.get("__file__")
            norm = _os.path.normpath(f_path).replace("\\", "/") if f_path else ""
            if f_path and "scripts/prism_theme.py" not in norm:
                caller_name = _Path(f_path).name
                try:
                    with open(f_path, "r", encoding="utf-8") as fh:
                        source = fh.read()
                except OSError:
                    source = None
                break
            frame = frame.f_back

        if source is None:
            raise RuntimeError(
                "emit_run_script 自动定位 caller 失败——可能从 Jupyter/REPL 调用。"
                "请显式传 source= 你的脚本源码字符串。"
            )

    if header:
        # 仅当首行不是 auto-emitted 标记时,添加一行注释
        first = source.split("\n", 1)[0] if source else ""
        if "Auto-emitted by prism-style-plot" not in first:
            stamp = (
                f"# Auto-emitted by prism-style-plot (v2.3.2) — "
                f"reproducibility companion of {name}.{{png|html|pdf}}\n"
                f"# Source: {caller_name or '<inline>'}\n\n"
            )
            source = stamp + source

    target = out_dir_path / f"{name}.py"
    target.write_text(source, encoding="utf-8")
    print(f"[emit_run_script] {caller_name} -> {target} "
          f"({len(source)} 字符)")
    return target


# ===========================================================================
# 多数据集合并面板图 + 总报告（v2.7.0 新增）
# 参考 nature-figure 的 multi-panel 组合思路：每张数据独立成面板、自动网格
# 排布、A/B/C 字母标注；统计报告各自独立，总 HTML 报告"图合并 + 统计依次给出"。
# 输入契约：每张数据提供一个 draw(ax) 回调 + 独立 stats_md，由本模块负责
# 拼图、标字母、并（默认）保留独立原图与独立统计报告。
# ===========================================================================

def _auto_panel_grid(n):
    """根据面板数 n 返回 (rows, cols) 自动网格。

    对齐用户约定：2→1×2, 3→1×3, 4→2×2, 5–6→2×3, 7–9→3×3, >9→4 列。
    """
    if n <= 1:
        return (1, 1)
    if n == 2:
        return (1, 2)
    if n == 3:
        return (1, 3)
    if n == 4:
        return (2, 2)
    if n <= 6:
        return (2, 3)
    if n <= 9:
        return (3, 3)
    cols = 4
    return ((n + cols - 1) // cols, cols)


def _b64_bytes(path):
    """读文件返回 base64 字符串；文件不存在返回空字符串。"""
    import os as _os
    import base64 as _b64
    if not (path and _os.path.exists(path)):
        return ""
    with open(path, "rb") as fh:
        return _b64.b64encode(fh.read()).decode("ascii")


def _b64_img(path):
    """读 PNG 返回内嵌用 data URI；文件不存在返回空字符串。"""
    b = _b64_bytes(path)
    return ("data:image/png;base64," + b) if b else ""


def compose_panel_figure(panels, out_dir=None, name="combined_figure",
                         layout="auto", panel_labels=None,
                         panel_titles=None, suptitle=None, dpi=300,
                         standalone=True, wspace=None, hspace=None,
                         panel_shape="tall", panel_size_cm=None,
                         panel_w=None, panel_h=None,
                         font_scale=1.0,
                         panel_label_fontsize=None,
                         suptitle_fontsize=None):
    """
    多张独立数据集 → 一张 Nature 风格多面板合并图（A/B/C… 标注），
    并（默认）同时保留每张数据的独立原图与独立统计报告。

    参数
    ----
    panels : list[dict]，每张面板一个元素，字段：
        draw     : callable(ax) —— 把该面板画到给定 ax（用 prism_bars /
                   prism_survival / prism_xy_fit 等；必须接受 ax 作首个参数）
        name     : str          —— 该面板的独立文件名（无后缀），如 "tnfa"
        stats_md : str          —— 该面板的独立统计报告 Markdown
                                    （build_stats_report 返回值）
        title    : str, 可选    —— 面板小标题，与字母标注同行显示
    out_dir : 输出目录（缺省 _default_out_dir）
    name    : 合并大图文件名（无后缀），如 "figure1"
    layout  : "auto" 或 (rows, cols) 元组
    panel_labels : list[str]，自定义标注；缺省 A,B,C…
    panel_titles : list[str]，便捷批量设 title（等同逐面板 title）
    suptitle : 合并图总标题（可选）
    standalone : True（默认）时为每个面板再生成独立原图 PNG/PDF +
                 独立统计报告 {name}_report.md / .html
    wspace/hspace : 子图间距（相对轴宽/高的比例，用于容纳显著性 bracket 与字母）；
                   None 时按 panel_shape 自动选（tall/square 留适中，wide 更宽）
    panel_shape : 单面板形态（"tall"/"square"/"wide"，支持中文别名"高"/"方"/"宽"），
                  默认 "tall"；按技能约定的 cm 尺寸（tall 3×5 cm、square 5×5 cm、
                  wide 7×5 cm）换算成 matplotlib inch 后决定合并图总尺寸
    panel_size_cm : 直接指定单面板宽高（cm），如 (6, 5)；传入时覆盖 panel_shape
    panel_w/panel_h : 兼容旧参，显式指定单面板 inch 尺寸；传入时最高优先级覆盖
                      panel_shape / panel_size_cm
    font_scale : 字体缩放因子（默认 1.0），最终字号在 apply_prism_theme 的
                 "基线 −4" 基础上再缩放；<1 更小，>1 更大
    panel_label_fontsize / suptitle_fontsize : 面板字母标注与总标题字号；
                                               None 时自动从当前主题取值

    返回：dict
        {"combined_png","combined_pdf","master_html",
         "panels":[{"name","png","pdf","report_md","report_html","label","title"}]}
    """
    import os as _os
    import matplotlib.pyplot as plt

    if not panels:
        raise ValueError("panels 不能为空——至少需要一张面板数据")
    n = len(panels)

    # —— 布局 ——
    if layout == "auto":
        rows, cols = _auto_panel_grid(n)
    else:
        rows, cols = layout
        if rows * cols < n:
            raise ValueError(
                f"layout={layout} 只有 {rows*cols} 个格子，放不下 {n} 张面板；"
                "请调大 rows/cols 或用 layout='auto'")

    if out_dir is None:
        out_dir = _default_out_dir()
    _os.makedirs(out_dir, exist_ok=True)

    # 先应用主题（含字体缩放），后续字号均从主题派生，不再硬编码
    apply_prism_theme(font_scale=font_scale)

    labels = panel_labels or [chr(65 + i) for i in range(n)]  # A,B,C...
    if panel_titles is not None:
        for i, t in enumerate(panel_titles):
            if i < n:
                panels[i]["title"] = t
    titles = [p.get("title", "") or "" for p in panels]

    # —— 单面板尺寸：优先级 panel_w/panel_h inch > panel_size_cm > panel_shape ——
    if panel_w is not None and panel_h is not None:
        pw_in, ph_in = float(panel_w), float(panel_h)
    elif panel_size_cm is not None:
        pw_in = float(panel_size_cm[0]) / 2.54
        ph_in = float(panel_size_cm[1]) / 2.54
    else:
        pw_in, ph_in = get_figsize(panel_shape)

    # 子图间距：未指定时按形态自动选，给 bracket/标签留足够呼吸空间
    if wspace is None:
        wspace = 0.42 if panel_shape == "wide" else 0.32
    if hspace is None:
        hspace = 0.42 if panel_shape == "wide" else 0.32

    # —— 合并图尺寸：以单面板尺寸 + 间距推算 ——
    ws_in = wspace * pw_in
    hs_in = hspace * ph_in
    W = cols * pw_in + (cols - 1) * ws_in
    H = rows * ph_in + (rows - 1) * hs_in
    fig = plt.figure(figsize=(W, H))
    gs = fig.add_gridspec(rows, cols, wspace=wspace, hspace=hspace)

    # 字号从当前主题取值，尊重"基线 −4"约定；用户可显式覆盖
    _label_fs = panel_label_fontsize if panel_label_fontsize is not None \
                else plt.rcParams["axes.titlesize"]
    _title_fs = suptitle_fontsize if suptitle_fontsize is not None \
                else plt.rcParams["axes.titlesize"] + 2

    for i in range(n):
        ax = fig.add_subplot(gs[i])
        panels[i]["draw"](ax)
        # Nature 风格字母标注：ax 左上角，粗体
        tag = labels[i]
        if titles[i]:
            tag = f"{labels[i]}. {titles[i]}"
        ax.text(-0.12, 1.04, tag, transform=ax.transAxes,
                fontsize=_label_fs, fontweight="bold", va="bottom", ha="left")

    if suptitle:
        fig.suptitle(suptitle, fontsize=_title_fs, fontweight="bold", y=0.99)

    save_figure(fig, name, out_dir, dpi=dpi, close=True,
                formats=("png", "pdf"))
    combined_png = _os.path.join(out_dir, f"{name}.png")
    combined_pdf = _os.path.join(out_dir, f"{name}.pdf")

    # —— 独立原图 + 独立统计报告 ——
    panels_info = []
    for i in range(n):
        pname = panels[i]["name"]
        png = pdf = rhtml = None
        if standalone:
            fig2 = plt.figure(figsize=(pw_in, ph_in))
            ax2 = fig2.add_subplot(111)
            panels[i]["draw"](ax2)
            save_figure(fig2, pname, out_dir, dpi=dpi, close=True,
                        formats=("png", "pdf"))
            write_report(pname, panels[i]["stats_md"], out_dir)
            png = _os.path.join(out_dir, f"{pname}.png")
            pdf = _os.path.join(out_dir, f"{pname}.pdf")
            rhtml = _os.path.join(out_dir, f"{pname}.html")
        panels_info.append({
            "name": pname,
            "png": png, "pdf": pdf,
            "report_md": panels[i]["stats_md"],
            "report_html": rhtml,
            "label": labels[i],
            "title": titles[i],
        })

    master_html = build_master_report(
        name, panels_info, out_dir=out_dir,
        combined_png=combined_png, combined_pdf=combined_pdf,
        suptitle=suptitle, title=suptitle or name)

    return {
        "combined_png": combined_png,
        "combined_pdf": combined_pdf,
        "master_html": master_html,
        "panels": panels_info,
    }


def build_master_report(name, panels_info, out_dir=None,
                        combined_png=None, combined_pdf=None,
                        suptitle=None, title=None, extra_footer=None):
    """
    生成**合并总报告**（HTML）：顶部为合并面板大图，下方依次列出每张面板
    的独立统计报告（图 + 统计表 + 图注），并附各自独立报告链接。
    同时写出轻量 _report.md 索引（列出各面板及其独立报告）。

    参数
    ----
    name         : 合并大图同名基础名（HTML = {name}_report.html）
    panels_info  : list[dict]，每面板：
                   {"name","png","pdf","report_md","report_html","label","title"}
    combined_png : 合并图 PNG 路径（用于内嵌预览）
    combined_pdf : 合并图 PDF 路径（用于下载按钮）
    suptitle/title : 报告标题
    extra_footer : 附加页脚 HTML（可选）

    返回：HTML 文件绝对路径
    """
    import os as _os
    import datetime as _dt

    if out_dir is None:
        out_dir = _default_out_dir()
    _os.makedirs(out_dir, exist_ok=True)

    if combined_png is None:
        combined_png = _os.path.join(out_dir, f"{name}.png")
    if combined_pdf is None:
        combined_pdf = _os.path.join(out_dir, f"{name}.pdf")

    title = title or suptitle or name

    # —— 合并图预览 + PDF 下载 ——
    combined_img = _b64_img(combined_png)
    combined_html = ""
    if combined_img:
        combined_html = (
            f'<div class="figure"><img src="{combined_img}" '
            f'alt="{name}.png"></div>'
        )
    pdf_html = ""
    pdf_b64 = _b64_bytes(combined_pdf)
    if pdf_b64:
        pdf_html = (
            f'<a class="dl" href="#" id="dl-pdf" '
            f'onclick="dlPdf(event)">Download combined PDF (vector)</a>\n'
            f'<script>\n'
            f'function dlPdf(e) {{\n'
            f'  e.preventDefault();\n'
            f'  var b64 = "{pdf_b64}";\n'
            f'  var bin = atob(b64);\n'
            f'  var bytes = new Uint8Array(bin.length);\n'
            f'  for (var i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);\n'
            f'  var blob = new Blob([bytes], {{type: "application/pdf"}});\n'
            f'  var url = URL.createObjectURL(blob);\n'
            f'  var a = document.createElement("a");\n'
            f'  a.href = url; a.download = "{name}.pdf";\n'
            f'  document.body.appendChild(a); a.click();\n'
            f'  document.body.removeChild(a);\n'
            f'  URL.revokeObjectURL(url);\n'
            f'}}\n'
            f'</script>'
        )

    # —— 各面板独立统计报告（依次）——
    sections = []
    for p in panels_info:
        head = f"Panel {p['label']}"
        if p.get("title"):
            head += f" — {p['title']}"
        img = _b64_img(p.get("png"))
        fig_html = (
            f'<div class="figure"><img src="{img}" alt="{p["name"]}.png"></div>'
        ) if img else ""
        body = _md_to_html(p.get("report_md") or "")
        link = ""
        if p.get("report_html") and _os.path.exists(p["report_html"]):
            link = (f'<p class="panel-link"><a href="{p["name"]}.html">'
                    f'查看 {p["name"]} 独立报告 ↗</a></p>')
        sections.append(
            f'<section class="panel">\n'
            f'  <h2>{_md_escape(head)}</h2>\n'
            f'  {fig_html}\n'
            f'  <div class="report">{body}</div>\n'
            f'  {link}\n'
            f'</section>'
        )
    sections_html = "\n".join(sections)

    footer_html = ""
    if extra_footer:
        footer_html = f'<div class="footer-extra">{extra_footer}</div>'
    now = _dt.datetime.now().strftime("%Y-%m-%d %H:%M")

    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{_md_escape(title)} · Combined Prism Report</title>
<style>
  * {{ box-sizing: border-box; }}
  body {{
    font-family: "Arial", "Helvetica", "DejaVu Sans", sans-serif;
    margin: 0; padding: 28px 20px; background: #fafafa; color: #1a1a1a;
    line-height: 1.6; font-size: 14px;
  }}
  .wrap {{ max-width: 960px; margin: 0 auto; }}
  h1 {{ font-size: 20px; margin: 0 0 4px; font-weight: 600; }}
  .meta {{ color: #888; font-size: 12px; margin-bottom: 18px;
           border-bottom: 2px solid #1a1a1a; padding-bottom: 10px; }}
  .figure {{ background: #fff; border: 1px solid #e0e0e0; border-radius: 4px;
             padding: 12px; margin: 0 0 14px; text-align: center; }}
  .figure img {{ max-width: 100%; height: auto; }}
  .dl {{ display: inline-block; background: #0072B2; color: #fff; text-decoration: none;
         padding: 6px 14px; border-radius: 3px; font-size: 12px; margin-bottom: 18px; }}
  .dl:hover {{ background: #005a91; }}
  .panel {{ background: #fff; border: 1px solid #e0e0e0; border-radius: 4px;
            padding: 18px 22px; margin: 16px 0; }}
  .panel h2 {{ font-size: 16px; margin: 0 0 12px; padding-bottom: 6px;
               border-bottom: 1px solid #0072B2; color: #0072B2; }}
  .panel-link {{ margin: 10px 0 0; font-size: 12px; }}
  .panel-link a {{ color: #0072B2; }}
  .report h3 {{ font-size: 14px; margin: 18px 0 8px; }}
  .report h4 {{ font-size: 13px; margin: 14px 0 6px; }}
  .report p {{ margin: 8px 0; }}
  .report table {{ border-collapse: collapse; width: 100%; margin: 10px 0 14px;
                   font-size: 12.5px; }}
  .report th, .report td {{ border: 1px solid #ddd; padding: 5px 9px; text-align: left; }}
  .report th {{ background: #f2f2f2; font-weight: 600; }}
  .report tr:nth-child(even) td {{ background: #fafafa; }}
  .report ul {{ margin: 8px 0 14px; padding-left: 22px; }}
  .report li {{ margin: 3px 0; }}
  .report blockquote {{ margin: 12px 0; padding: 10px 14px; background: #f4f9f4;
                        border-left: 3px solid #009E73; color: #333; font-size: 12.5px; }}
  .report code {{ background: #f4f4f4; padding: 1px 4px; border-radius: 2px;
                  font-size: 12px; border: 1px solid #e8e8e8; }}
  .report pre {{ background: #f7f7f7; border: 1px solid #e0e0e0; border-radius: 4px;
                 padding: 10px 14px; overflow-x: auto; }}
  .report pre code {{ background: none; border: none; padding: 0; }}
  .footer-extra {{ margin-top: 16px; padding: 10px 14px; background: #f0f6fb;
                   border-left: 3px solid #0072B2; font-size: 12px; color: #555; }}
  .foot {{ margin-top: 20px; color: #aaa; font-size: 11px; text-align: right; }}
</style>
</head>
<body>
<div class="wrap">
  <h1>{_md_escape(title)}</h1>
  <div class="meta">Generated {now} · prism-style-plot · 合并面板图 <code>{name}</code></div>
  {combined_html}
  {pdf_html}
  {sections_html}
  {footer_html}
  <div class="foot">Combined report generated by prism-style-plot (workbuddy skill)</div>
</div>
</body>
</html>"""

    html_path = _os.path.join(out_dir, f"{name}_report.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(page)

    # —— 轻量 _report.md 索引（不重复统计正文，只列面板与独立报告链接）——
    lines = [f"# 合并总报告：{title}", "",
             f"合并面板图：`{name}.png` / `{name}.pdf`", "",
             "## 面板清单", ""]
    for p in panels_info:
        t = f" — {p['title']}" if p.get("title") else ""
        link = f" [独立报告]({p['name']}.html)" if p.get("report_html") else ""
        lines.append(f"- **Panel {p['label']}{t}**：`{p['name']}.png`{link}")
    lines.append("")
    md_path = _os.path.join(out_dir, f"{name}_report.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return html_path
