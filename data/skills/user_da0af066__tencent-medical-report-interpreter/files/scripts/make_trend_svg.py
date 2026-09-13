#!/usr/bin/env python3
"""
生成内联 SVG 趋势折线图，替代 Chart.js。

为什么不用 Chart.js：
  - 走 CDN，转发后在无网环境或微信内置浏览器里图表空白
  - 外部 JS 约 200 KB，内联 SVG 约 4 KB
  - 部分邮件客户端与微信会剥离 script 标签

为什么画「相对增幅百分比」而不是原始值：
  各指标单位不同（mmol/L vs mIU/L vs U/L），无法共用 Y 轴。
  改为绘制相对首次检测的增幅百分比，纵轴统一为 %，
  三条线即可直接比较「谁恶化得更快」。
  代价是失去绝对值信息，用两种方式补偿：
    ① 折线末端标注最新实测值
    ② 图上方保留完整数据表格

用法：
  # 从 JSON 文件读取
  python3 make_trend_svg.py --data trend.json

  # 命令行直接传（可重复 --series）
  python3 make_trend_svg.py \
      --labels 2024-08,2025-08,2026-08 \
      --series "空腹血糖 mmol/L:6.0,6.7,7.4:#a32d2d" \
      --series "TSH mIU/L:2.1,3.0,4.0:#854f0b" \
      --series "LDL-C mmol/L:2.8,3.0,3.2:#185fa5"

  # 输出到文件
  python3 make_trend_svg.py --data trend.json --out trend.svg

JSON 格式：
  {
    "labels": ["2024-08", "2025-08", "2026-08"],
    "series": [
      {"name": "空腹血糖 mmol/L", "values": [6.0, 6.7, 7.4], "color": "#a32d2d"},
      {"name": "TSH mIU/L",       "values": [2.1, 3.0, 4.0], "color": "#854f0b"}
    ]
  }

配色约定（医疗场景：红=风险高，与股市涨红跌绿无关）：
  #a32d2d 红   —— 已达诊断阈值或恶化最快的指标
  #854f0b 琥珀 —— 需关注
  #185fa5 蓝   —— 一般提示
  #0f6e56 绿   —— 改善中
"""

import argparse
import json
import sys

# ── 画布与留白 ────────────────────────────────────────────────
W, H = 640, 250
PAD_L, PAD_R, PAD_T, PAD_B = 46, 16, 22, 42
PW, PH = W - PAD_L - PAD_R, H - PAD_T - PAD_B

FONT = "-apple-system,PingFang SC,sans-serif"
C_GRID = "#eeece5"
C_AXIS_TEXT = "#888780"
C_LEGEND_TEXT = "#5f5e5a"

DEFAULT_COLORS = ["#a32d2d", "#854f0b", "#185fa5", "#0f6e56", "#7f77dd"]


def build_svg(labels, series):
    """labels: list[str]；series: list[dict(name, values, color)]"""
    if len(labels) < 2:
        raise ValueError("趋势图至少需要 2 个时间点，单份报告不应生成趋势图")
    for s in series:
        if len(s["values"]) != len(labels):
            raise ValueError(
                f"「{s['name']}」有 {len(s['values'])} 个值，"
                f"但时间点有 {len(labels)} 个，数量必须一致"
            )
        if s["values"][0] == 0:
            raise ValueError(f"「{s['name']}」首个值为 0，无法计算相对增幅")

    # 各指标换算为相对首值的增幅百分比
    lines = []
    for i, s in enumerate(series):
        vals = s["values"]
        base = vals[0]
        pcts = [(v / base - 1) * 100 for v in vals]
        color = s.get("color") or DEFAULT_COLORS[i % len(DEFAULT_COLORS)]
        lines.append({"name": s["name"], "values": vals, "pcts": pcts, "color": color})

    all_pcts = [p for ln in lines for p in ln["pcts"]]
    p_min = min(0, min(all_pcts))
    p_max = max(all_pcts) * 1.15 if max(all_pcts) > 0 else 10
    if p_max - p_min < 1:          # 全平时给个最小跨度，避免除零
        p_max = p_min + 10

    def x(i):
        return PAD_L + PW * i / (len(labels) - 1)

    def y(p):
        return PAD_T + PH * (1 - (p - p_min) / (p_max - p_min))

    out = [
        f'<svg viewBox="0 0 {W} {H}" width="100%" style="display:block" '
        f'xmlns="http://www.w3.org/2000/svg" role="img" '
        f'aria-label="各指标相对首次检测的变化趋势图">'
    ]

    # 网格线与 Y 轴刻度：每 25% 一条
    t = 0 if p_min >= 0 else int(p_min // 25) * 25
    while t <= p_max:
        yy = round(y(t), 1)
        out.append(
            f'<line x1="{PAD_L}" y1="{yy}" x2="{W-PAD_R}" y2="{yy}" '
            f'stroke="{C_GRID}" stroke-width="1"/>'
        )
        sign = "+" if t > 0 else ""
        out.append(
            f'<text x="{PAD_L-7}" y="{yy+4}" text-anchor="end" font-size="11" '
            f'fill="{C_AXIS_TEXT}" font-family="{FONT}">{sign}{int(t)}%</text>'
        )
        t += 25

    # X 轴标签
    for i, lb in enumerate(labels):
        out.append(
            f'<text x="{round(x(i),1)}" y="{H-PAD_B+20}" text-anchor="middle" '
            f'font-size="11.5" fill="{C_AXIS_TEXT}" font-family="{FONT}">{lb}</text>'
        )

    # 折线 + 数据点 + 末端实测值
    for ln in lines:
        pts = " ".join(
            f"{round(x(i),1)},{round(y(p),1)}" for i, p in enumerate(ln["pcts"])
        )
        out.append(
            f'<polyline points="{pts}" fill="none" stroke="{ln["color"]}" '
            f'stroke-width="2.5" stroke-linejoin="round" stroke-linecap="round"/>'
        )
        for i, p in enumerate(ln["pcts"]):
            out.append(
                f'<circle cx="{round(x(i),1)}" cy="{round(y(p),1)}" r="4" '
                f'fill="#fff" stroke="{ln["color"]}" stroke-width="2.5"/>'
            )
        # 末端标注最新实测值，补偿失去的绝对值信息
        out.append(
            f'<text x="{round(x(len(ln["pcts"])-1),1)}" '
            f'y="{round(y(ln["pcts"][-1]),1)-11}" text-anchor="end" font-size="11.5" '
            f'font-weight="600" fill="{ln["color"]}" font-family="{FONT}">'
            f'{ln["values"][-1]}</text>'
        )

    # 图例
    lx, ly = PAD_L, H - 8
    for ln in lines:
        out.append(
            f'<rect x="{lx}" y="{ly-8}" width="11" height="3" rx="1.5" '
            f'fill="{ln["color"]}"/>'
        )
        out.append(
            f'<text x="{lx+16}" y="{ly-3}" font-size="11.5" fill="{C_LEGEND_TEXT}" '
            f'font-family="{FONT}">{ln["name"]}</text>'
        )
        lx += 16 + len(ln["name"]) * 7.2 + 22

    out.append("</svg>")
    return "\n      ".join(out)


def parse_series_arg(raw):
    """解析 "名称:值1,值2,值3:#色号" 格式"""
    parts = raw.split(":")
    if len(parts) < 2:
        raise ValueError(f"--series 格式应为 「名称:值1,值2:#色号」，收到：{raw}")
    name = parts[0].strip()
    values = [float(v) for v in parts[1].split(",")]
    color = parts[2].strip() if len(parts) > 2 else None
    return {"name": name, "values": values, "color": color}


def main():
    ap = argparse.ArgumentParser(
        description="生成内联 SVG 趋势折线图（相对增幅百分比口径）"
    )
    ap.add_argument("--data", help="JSON 文件路径")
    ap.add_argument("--labels", help="时间点，逗号分隔，如 2024-08,2025-08,2026-08")
    ap.add_argument(
        "--series", action="append", default=[],
        help='数据系列，可重复。格式：「名称:值1,值2,值3:#色号」'
    )
    ap.add_argument("--out", help="输出文件路径；省略则打印到 stdout")
    args = ap.parse_args()

    if args.data:
        with open(args.data, encoding="utf-8") as f:
            cfg = json.load(f)
        labels, series = cfg["labels"], cfg["series"]
    elif args.labels and args.series:
        labels = [x.strip() for x in args.labels.split(",")]
        series = [parse_series_arg(r) for r in args.series]
    else:
        ap.error("需提供 --data，或同时提供 --labels 与至少一个 --series")

    try:
        svg = build_svg(labels, series)
    except ValueError as e:
        print(f"错误：{e}", file=sys.stderr)
        sys.exit(1)

    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(svg)
        print(f"已写入 {args.out}（{len(svg)} 字符）")
    else:
        print(svg)


if __name__ == "__main__":
    main()
