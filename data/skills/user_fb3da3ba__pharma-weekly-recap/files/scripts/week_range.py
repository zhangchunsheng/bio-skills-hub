#!/usr/bin/env python3
"""计算周报所需的日期变量与工作目录，输出可直接注入提示词的键值。

用法:
    python week_range.py                     # 本周（周一起算的那一周）
    python week_range.py --offset -1         # 上一周
    python week_range.py --date 2026-08-29   # 以指定日期所在的周为准
    python week_range.py --json              # 仅输出 JSON
    python week_range.py --check             # 检查今天是否为周六（定时任务前置校验）

若当天不是周六，仍会正常输出本周一/周五，但 --check 会以退出码 1 提示。
"""

import argparse
import datetime as dt
import json
import sys

WEEKDAY_CN = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]


def build(anchor: dt.date) -> dict:
    monday = anchor - dt.timedelta(days=anchor.weekday())
    friday = monday + dt.timedelta(days=4)
    saturday = monday + dt.timedelta(days=5)
    sunday = monday + dt.timedelta(days=6)
    prev_friday = monday - dt.timedelta(days=3)  # 上周五（用于计算周涨跌幅基准）
    prev_monday = monday - dt.timedelta(days=7)

    return {
        "monday": monday.isoformat(),
        "friday": friday.isoformat(),
        "saturday": saturday.isoformat(),
        "sunday": sunday.isoformat(),
        "prev_friday": prev_friday.isoformat(),
        "prev_monday": prev_monday.isoformat(),
        "today": anchor.isoformat(),
        "today_weekday_cn": WEEKDAY_CN[anchor.weekday()],
        "is_saturday": anchor.weekday() == 5,
        "week_label": f"{monday.strftime('%Y%m%d')}-{friday.strftime('%Y%m%d')}",
        "week_label_cn": f"{monday.strftime('%Y年%m月%d日')}-{friday.strftime('%m月%d日')}",
        "iso_year_week": f"{monday.isocalendar()[0]}W{monday.isocalendar()[1]:02d}",
        "session_id": saturday.strftime("%Y%m%d"),
        "report_filename": f"医药生物行业周报_{monday.strftime('%Y%m%d')}_{friday.strftime('%Y%m%d')}.md",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="计算医药周报的日期变量")
    parser.add_argument("--date", help="锚点日期 YYYY-MM-DD，默认今天")
    parser.add_argument("--offset", type=int, default=0, help="周偏移，例如 -1 表示上一周")
    parser.add_argument("--json", action="store_true", help="仅输出 JSON")
    parser.add_argument("--check", action="store_true", help="非周六时以退出码 1 退出")
    args = parser.parse_args()

    anchor = (
        dt.date.fromisoformat(args.date)
        if args.date
        else dt.date.today()
    ) + dt.timedelta(weeks=args.offset)

    data = build(anchor)

    if args.json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        width = max(len(k) for k in data)
        for key, value in data.items():
            print(f"{key.ljust(width)} = {value}")

    if args.check and not data["is_saturday"]:
        print(
            f"\n[warn] 今天是{data['today_weekday_cn']}，不是周六。"
            "定时周报通常在周六运行；若手动补跑请忽略此提示。",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
