#!/usr/bin/env python3
"""
time_utils.py - 医药行业晨报（学术会议版）时间工具
提供当前日期检测和 ISO 时间转人话格式的功能。
"""

import sys
import os
from datetime import datetime, timedelta, timezone

# 北京时间时区 UTC+8
BEIJING_TZ = timezone(timedelta(hours=8))


def get_today():
    """获取当前北京时间日期，格式 YYYY-MM-DD"""
    now = datetime.now(BEIJING_TZ)
    return now.strftime("%Y-%m-%d")


def get_full_date():
    """获取完整日期格式，如 2026年6月18日 星期四"""
    now = datetime.now(BEIJING_TZ)
    weekdays = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
    weekday = weekdays[now.weekday()]
    return f"{now.year}年{now.month}月{now.day}日 {weekday}"


def get_current_hour():
    """获取当前北京时间小时数，用于判断是否在08:00之前"""
    now = datetime.now(BEIJING_TZ)
    return now.hour


def format_time(iso_str):
    """
    将 ISO 时间字符串或相对时间文本转为北京时间人话格式。
    支持多种输入格式：
    - ISO 8601: 2026-06-18T09:48:00Z / 2026-06-18T17:48:00+08:00
    - 带时区的ISO: 2026-06-18T09:48:00+00:00
    - 纯日期: 2026-06-18
    - 已是人话格式: 直接返回

    返回格式:
    - 1小时内: "X分钟前"
    - 24小时内: "X小时前" 或 "今天上午/下午 HH:MM"
    - 昨天: "昨天上午/下午 HH:MM"
    - 更早: "X天前" 或 "M月D日"
    """
    if not iso_str or not iso_str.strip():
        return "时间未知"

    now = datetime.now(BEIJING_TZ)

    # 已经是人话格式的直接返回
    human_patterns = ["分钟前", "小时前", "天前", "昨天", "今天", "前天", "刚刚"]
    if any(p in iso_str for p in human_patterns):
        return iso_str.strip()

    # 尝试解析 ISO 格式
    parsed = None
    candidates = [
        iso_str.strip().replace("Z", "+00:00"),
    ]

    # 尝试带时区解析
    for candidate in candidates:
        try:
            parsed = datetime.fromisoformat(candidate)
            break
        except (ValueError, TypeError):
            continue

    # 尝试纯日期格式 YYYY-MM-DD
    if parsed is None:
        try:
            parsed = datetime.strptime(iso_str.strip()[:10], "%Y-%m-%d")
            parsed = parsed.replace(tzinfo=BEIJING_TZ)
        except (ValueError, TypeError):
            try:
                parsed = datetime.strptime(iso_str.strip()[:19], "%Y-%m-%d %H:%M:%S")
                parsed = parsed.replace(tzinfo=BEIJING_TZ)
            except (ValueError, TypeError):
                return iso_str.strip()

    if parsed is None:
        return iso_str.strip()

    # 转为北京时间
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=BEIJING_TZ)
    else:
        parsed = parsed.astimezone(BEIJING_TZ)

    diff = now - parsed
    total_seconds = diff.total_seconds()

    if total_seconds < 0:
        # 未来时间，直接返回日期
        return f"{parsed.month}月{parsed.day}日"

    if total_seconds < 60:
        return "刚刚"
    elif total_seconds < 3600:
        minutes = int(total_seconds / 60)
        return f"{minutes}分钟前"
    elif total_seconds < 86400:
        hours = int(total_seconds / 3600)
        if hours < 3:
            return f"{hours}小时前"
        else:
            hour = parsed.hour
            period = "上午" if hour < 12 else "下午"
            display_hour = hour if hour <= 12 else hour - 12
            return f"今天{period} {display_hour:02d}:{parsed.minute:02d}"
    elif total_seconds < 172800:
        # 昨天
        hour = parsed.hour
        period = "上午" if hour < 12 else "下午"
        display_hour = hour if hour <= 12 else hour - 12
        return f"昨天{period} {display_hour:02d}:{parsed.minute:02d}"
    elif total_seconds < 432000:
        # 2-5天前
        days = int(total_seconds / 86400)
        return f"{days}天前"
    else:
        return f"{parsed.month}月{parsed.day}日"


def main():
    if len(sys.argv) < 2:
        print("Usage: python time_utils.py [--today | --full | --hour | --format <iso_string>]")
        sys.exit(1)

    arg = sys.argv[1]

    if arg == "--today":
        print(get_today())
    elif arg == "--full":
        print(get_full_date())
    elif arg == "--hour":
        print(get_current_hour())
    elif arg == "--format":
        if len(sys.argv) < 3:
            print("Error: --format requires an ISO time string argument")
            sys.exit(1)
        iso_str = sys.argv[2]
        print(format_time(iso_str))
    else:
        print(f"Unknown argument: {arg}")
        print("Usage: python time_utils.py [--today | --full | --hour | --format <iso_string>]")
        sys.exit(1)


if __name__ == "__main__":
    main()
