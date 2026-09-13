"""验证 6:画布推荐层 — recommend_shape / recommend_figsize 全分支断言（v2.2.0 新增，v2.2.1 同步阈值）

覆盖:Column/Grouped 按总分组数分档(<5 tall / 5-8 square / >8 wide)、
固定表型默认、兜底 tall、关键词覆盖通道(含中文别名与未识别关键词)、
recommend_figsize 便捷封装、FIGURE_SHAPES 预设未被改动、
prism_survival 默认线宽 0.75pt。
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import matplotlib
matplotlib.use("Agg")

from prism_theme import (recommend_shape, recommend_figsize, get_figsize,
                         FIGURE_SHAPES)
from verify_common import report

fails = []


def check(case, got, want):
    try:
        assert got == want, f"期望 {want!r}, 实际 {got!r}"
        report(case, True, f"{got}")
    except Exception as e:
        fails.append((case, e))
        report(case, False, str(e))


# ---------- 6.1 Column / Grouped 按总分组数分档(v2.2.1: <5 tall / 5-8 square / >8 wide) ----------
check("6.1 Column n=1 -> tall", recommend_shape("column", n_groups=1), "tall")
check("6.1 Column n=4 -> tall", recommend_shape("column", n_groups=4), "tall")
check("6.1 Column n=5 -> square", recommend_shape("column", n_groups=5), "square")
check("6.1 Column n=8 -> square", recommend_shape("column", n_groups=8), "square")
check("6.1 Column n=9 -> wide", recommend_shape("column", n_groups=9), "wide")
check("6.1 Grouped n=6 -> square", recommend_shape("grouped", n_groups=6), "square")
check("6.1 Grouped n=12 -> wide", recommend_shape("GROUPED", n_groups=12), "wide")
check("6.1 Grouped 缺 n -> tall", recommend_shape("grouped"), "tall")

# ---------- 6.2 固定表型默认 ----------
check("6.2 XY -> square", recommend_shape("xy"), "square")
check("6.2 Survival -> square", recommend_shape("survival"), "square")
check("6.2 Contingency -> wide", recommend_shape("contingency"), "wide")
check("6.2 Parts of whole -> square", recommend_shape("parts of whole"), "square")
check("6.2 Multiple variables -> wide", recommend_shape("multiple_variables"), "wide")
check("6.2 Nested -> tall", recommend_shape("nested"), "tall")

# ---------- 6.3 兜底 ----------
check("6.3 未知表型 -> tall", recommend_shape("unknown_table"), "tall")
check("6.3 全空 -> tall", recommend_shape(), "tall")

# ---------- 6.4 关键词覆盖通道 ----------
check("6.4 覆盖: column n=3 shape=wide -> wide",
      recommend_shape("column", n_groups=3, shape="wide"), "wide")
check("6.4 覆盖: xy shape=tall -> tall",
      recommend_shape("xy", shape="tall"), "tall")
check("6.4 覆盖: 中文别名 宽 -> wide",
      recommend_shape("xy", shape="宽"), "wide")
check("6.4 覆盖: column n=9 shape=square -> square",
      recommend_shape("column", n_groups=9, shape="square"), "square")
check("6.4 未识别关键词 -> 落入数据默认",
      recommend_shape("xy", shape="big"), "square")
check("6.4 未识别关键词+无表型 -> tall",
      recommend_shape(shape="big"), "tall")

# ---------- 6.5 recommend_figsize 便捷封装 ----------
check("6.5 column n=3 == tall figsize",
      recommend_figsize("column", n_groups=3), get_figsize("tall"))
check("6.5 xy == square figsize",
      recommend_figsize("xy"), get_figsize("square"))
check("6.5 contingency == wide figsize",
      recommend_figsize("contingency"), get_figsize("wide"))
check("6.5 关键词覆盖 == wide figsize",
      recommend_figsize("column", n_groups=3, shape="wide"), get_figsize("wide"))
fs = recommend_figsize("xy")
try:
    assert isinstance(fs, tuple) and len(fs) == 2 and \
        all(isinstance(v, float) for v in fs), f"figsize 类型错误: {fs!r}"
    report("6.5 figsize 为 (float, float) 元组", True, str(fs))
except Exception as e:
    fails.append(("6.5 figsize 类型", e))
    report("6.5 figsize 为 (float, float) 元组", False, str(e))

# ---------- 6.6 既有预设未受影响 ----------
check("6.6 FIGURE_SHAPES 仍为 cm 预设",
      FIGURE_SHAPES, {"tall": (3, 5), "square": (5, 5), "wide": (7, 5)})
check("6.6 cm->inch 换算一致", get_figsize("tall")[0], round(3 / 2.54, 3))

# ---------- 6.7 prism_survival 默认线宽对齐全局 0.75pt(v2.2.1) ----------
import inspect
from prism_theme import prism_survival
check("6.7 survival 默认线宽 lw=0.75",
      inspect.signature(prism_survival).parameters["lw"].default, 0.75)

sys.exit(1 if fails else 0)
