#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
药房差错统计与趋势分析脚本
================================
读取差错登记 CSV（表头见 references/grading_standard.md），输出：
  1. 月度频次趋势折线图
  2. 差错类型分布条形图
  3. 差错分级分布
  4. 部门/小组对比条形图
  5. 帕累托图（定位累计占比>=80% 的重点差错类型）
  6. Markdown 汇总报告

依赖: pandas, matplotlib
中文字体: 自动探测 macOS PingFang / 系统字体；乱码时在 FONT_PATH 手动指定。

用法:
  python error_stats.py --input 差错记录.csv --outdir ./差错分析输出
  python error_stats.py --input data.csv --outdir out --start 2026-01 --end 2026-08
"""

import argparse
import os
import sys
import platform
from datetime import datetime

import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

# ---------- 中文字体 ----------
FONT_PATH = ""  # 留空自动探测；如需手动指定填绝对路径，如 "/System/Library/Fonts/STHeiti Light.ttc"

def setup_cjk_font():
    if FONT_PATH and os.path.exists(FONT_PATH):
        font_manager.fontManager.addfont(FONT_PATH)
        return font_manager.FontProperties(fname=FONT_PATH).get_name()
    candidates = [
        "PingFang SC", "PingFang HK", "Heiti SC", "STHeiti", "SimHei",
        "Microsoft YaHei", "Noto Sans CJK SC", "Source Han Sans SC",
    ]
    available = {f.name for f in font_manager.fontManager.ttflist}
    for c in candidates:
        if c in available:
            return c
    # 兜底：扫描常见 macOS 字体文件
    if platform.system() == "Darwin":
        for p in [
            "/System/Library/Fonts/PingFang.ttc",
            "/System/Library/Fonts/STHeiti Light.ttc",
            "/System/Library/Fonts/Hiragino Sans GB.ttc",
        ]:
            if os.path.exists(p):
                font_manager.fontManager.addfont(p)
                return font_manager.FontProperties(fname=p).get_name()
    return None

CJK = setup_cjk_font()
if CJK:
    plt.rcParams["font.family"] = CJK
plt.rcParams["axes.unicode_minus"] = False

PARETO_THRESHOLD = 0.80


def load_data(path):
    df = pd.read_csv(path)
    # 统一关键列名（兼容中英文表头）
    rename = {}
    for col in df.columns:
        c = str(col).strip()
        if c in ("发生日期", "日期", "date", "发生时间"):
            rename[col] = "发生日期"
        elif c in ("差错类型", "type", "error_type"):
            rename[col] = "差错类型"
        elif c in ("差错分级", "分级", "level", "grade"):
            rename[col] = "差错分级"
        elif c in ("部门", "药房", "dept", "department"):
            rename[col] = "部门"
        elif c in ("药房小组", "小组", "group", "team"):
            rename[col] = "药房小组"
        elif c in ("是否造成伤害", "伤害", "harm"):
            rename[col] = "是否造成伤害"
        elif c in ("根本原因分类", "根因分类", "root_cause"):
            rename[col] = "根本原因分类"
    df = df.rename(columns=rename)
    if "发生日期" not in df.columns:
        raise SystemExit("错误：未找到日期列（需含 '发生日期'/'日期'/'date'）")
    df["发生日期"] = pd.to_datetime(df["发生日期"], errors="coerce")
    df = df.dropna(subset=["发生日期"])
    df["月份"] = df["发生日期"].dt.to_period("M").astype(str)
    return df


def savefig(fig, outdir, name):
    path = os.path.join(outdir, name)
    fig.savefig(path, dpi=130, bbox_inches="tight")
    plt.close(fig)
    return path


def chart_trend(df, outdir):
    counts = df.groupby("月份").size()
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(counts.index, counts.values, marker="o", color="#c0392b", linewidth=2)
    ax.set_title("药房差错月度频次趋势")
    ax.set_xlabel("月份"); ax.set_ylabel("差错条数")
    ax.grid(alpha=0.3)
    for x, y in zip(counts.index, counts.values):
        ax.annotate(str(y), (x, y), textcoords="offset points", xytext=(0, 6), ha="center")
    return savefig(fig, outdir, "趋势_月度频次.png")


def chart_bar(df, col, title, fname, outdir, top=None):
    vc = df[col].fillna("未填写").value_counts()
    if top:
        vc = vc.head(top)
    fig, ax = plt.subplots(figsize=(8, max(3, 0.4 * len(vc) + 1)))
    ax.barh(vc.index[::-1], vc.values[::-1], color="#2980b9")
    ax.set_title(title); ax.set_xlabel("条数")
    for i, v in enumerate(vc.values[::-1]):
        ax.text(v + 0.1, i, str(v), va="center")
    return savefig(fig, outdir, fname)


def chart_pareto(df, outdir):
    vc = df["差错类型"].fillna("未填写").value_counts()
    cum = vc.cumsum() / vc.sum()
    fig, ax1 = plt.subplots(figsize=(9, 4.5))
    ax1.bar(vc.index, vc.values, color="#2980b9", label="差错条数")
    ax1.set_ylabel("差错条数"); ax1.set_xlabel("差错类型")
    plt.setp(ax1.get_xticklabels(), rotation=30, ha="right")
    ax2 = ax1.twinx()
    ax2.plot(vc.index, cum.values * 100, color="#c0392b", marker="o", label="累计占比%")
    ax2.set_ylabel("累计占比 (%)"); ax2.set_ylim(0, 105)
    ax2.axhline(PARETO_THRESHOLD * 100, color="#e67e22", linestyle="--", linewidth=1)
    # 标注重点类型（累计跨过阈值前的类型）
    focus = vc[cum <= PARETO_THRESHOLD].index.tolist()
    if cum.iloc[len(focus)] > PARETO_THRESHOLD and len(vc) > len(focus):
        focus.append(vc.index[len(focus)])
    ax1.set_title("差错类型帕累托分析（重点类型见红虚线前）")
    txt = "重点差错类型（累计≥80%）: " + "、".join(map(str, focus)) if focus else "—"
    fig.text(0.01, -0.18, txt, wrap=True, fontsize=9, color="#c0392b")
    return savefig(fig, outdir, "帕累托_类型分析.png"), focus


def build_report(df, outdir, focus_types, paths, start=None, end=None):
    total = len(df)
    by_month = df.groupby("月份").size()
    by_type = df["差错类型"].fillna("未填写").value_counts()
    by_level = df["差错分级"].fillna("未填写").value_counts()
    by_dept = df.groupby("部门").size().sort_values(ascending=False) if "部门" in df else None
    harm = df["是否造成伤害"].fillna("未填写").value_counts() if "是否造成伤害" in df else None

    lines = []
    lines.append("# 药房差错统计分析报告\n")
    lines.append(f"- 数据区间：{start or df['月份'].min()} ~ {end or df['月份'].max()}")
    lines.append(f"- 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append(f"- 差错总条数：**{total}**\n")

    lines.append("## 一、月度趋势")
    if len(by_month) > 1:
        first, last = by_month.iloc[0], by_month.iloc[-1]
        delta = last - first
        trend = "上升" if delta > 0 else ("下降" if delta < 0 else "持平")
        lines.append(f"- 起止月份：{by_month.index[0]}（{first}条）→ {by_month.index[-1]}（{last}条），整体{trend}（{delta:+d}条）。")
    else:
        lines.append(f"- 仅 {by_month.index[0]} 一个月数据：{total} 条。")
    lines.append("![趋势](趋势_月度频次.png)\n")

    lines.append("## 二、差错类型分布（Top）")
    for t, n in by_type.head(8).items():
        lines.append(f"- {t}：{n} 条（{n/total*100:.1f}%）")
    lines.append("![类型](类型_差错类型分布.png)\n")

    lines.append("## 三、差错分级分布")
    for t, n in by_level.items():
        lines.append(f"- {t}：{n} 条（{n/total*100:.1f}%）")
    lines.append("![分级](类型_差错分级分布.png)\n")

    if by_dept is not None and len(by_dept):
        lines.append("## 四、部门 / 小组对比")
        for t, n in by_dept.head(8).items():
            lines.append(f"- {t}：{n} 条（{n/total*100:.1f}%）")
        lines.append("![部门](类型_部门分布.png)\n")

    if harm is not None:
        lines.append("## 五、伤害情况")
        for t, n in harm.items():
            lines.append(f"- {t}：{n} 条")
        lines.append("")

    lines.append("## 六、帕累托重点分析")
    if focus_types:
        lines.append(f"- 累计占比≥80% 的**重点差错类型**：{'、'.join(map(str, focus_types))}。")
        lines.append("- 改进资源应优先投向上述类型（80/20 原则）。")
    lines.append("![帕累托](帕累托_类型分析.png)\n")

    lines.append("## 七、改进建议")
    lines.append("- 对重点差错类型，按 references/rca_guide.md 做根因分析（鱼骨图+5Why）。")
    lines.append("- 每条改进措施需可量化，下一周期用本脚本复核前后差错率。")
    lines.append("- 涉及真实患者信息的数据请先脱敏。")

    report = "\n".join(lines)
    rpath = os.path.join(outdir, "差错统计分析报告.md")
    with open(rpath, "w", encoding="utf-8") as f:
        f.write(report)
    return rpath


def main():
    ap = argparse.ArgumentParser(description="药房差错统计与趋势分析")
    ap.add_argument("--input", required=True, help="差错登记 CSV 路径")
    ap.add_argument("--outdir", default="./差错分析输出", help="输出目录")
    ap.add_argument("--start", default=None, help="起始月份过滤，如 2026-01")
    ap.add_argument("--end", default=None, help="结束月份过滤，如 2026-08")
    args = ap.parse_args()

    os.makedirs(args.outdir, exist_ok=True)
    df = load_data(args.input)
    if args.start:
        df = df[df["月份"] >= args.start]
    if args.end:
        df = df[df["月份"] <= args.end]
    if df.empty:
        raise SystemExit("过滤后无数据，请检查 --start/--end。")

    paths = []
    paths.append(chart_trend(df, args.outdir))
    paths.append(chart_bar(df, "差错类型", "差错类型分布", "类型_差错类型分布.png", args.outdir, top=12))
    if "差错分级" in df:
        paths.append(chart_bar(df, "差错分级", "差错分级分布", "类型_差错分级分布.png", args.outdir))
    if "部门" in df:
        paths.append(chart_bar(df, "部门", "部门/小组差错分布", "类型_部门分布.png", args.outdir, top=12))
    pareto_path, focus = chart_pareto(df, args.outdir)
    paths.append(pareto_path)

    rpath = build_report(df, args.outdir, focus, paths, args.start, args.end)
    print("✅ 分析完成，输出：")
    for p in paths + [rpath]:
        print("  -", os.path.abspath(p))


if __name__ == "__main__":
    main()
