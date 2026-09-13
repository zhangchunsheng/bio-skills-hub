#!/usr/bin/env python3
"""
中心药房排班表 CSV 生成与验证工具

用法:
  python3 generate_schedule.py generate   # 生成排班CSV
  python3 generate_schedule.py validate   # 验证排班规则

生成模式会输出一个可直接写入 Excel 的 CSV 文件。
验证模式会检查夜班循环、恢复周期、休息天数等约束。
"""

import csv
import sys
import json
from datetime import datetime, timedelta

# ============================================================
# 配置区：排班规则参数
# ============================================================

# 16人名单（顺序固定）
STAFF = [
    "李舒婕", "冯亮", "钟庆强", "薛书华", "李晓舒",
    "覃夏汐", "吴敬嫦", "何炳洪", "张垚", "林清雯",
    "詹诗琦", "黄玉婷", "杨茜", "何乐为", "黄万巧", "黎燕萍"
]

# 夜班循环顺序（10人）
NIGHT_SHIFT_ORDER = [
    "詹诗琦", "黄玉婷", "钟庆强", "李晓舒", "覃夏汐",
    "吴敬嫦", "张垚", "何乐为", "冯亮", "杨茜"
]

# 双周五夜班固定人员
BIWEEKLY_FRIDAY_NIGHT = "林清雯"

# 恢复周期：夜班后的5天固定班次
RECOVERY_CYCLE = ["夜班", "夜休", "休", "休", "小夜"]

# 班次时间说明
SHIFT_DESCRIPTION = (
    "说明 ：A班8:00-15:00； A半天班8:30-12:00； B班9:00-16:00； "
    "C班10:00-17:00；  静A班8:00-15:00； 静B班8:30-15:30； "
    "小夜：14:00-21:00；当天临时负责人为 A班药师 ；"
)

DAYS = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]


def get_next_night_shift_person(last_person):
    """根据上一位夜班人，返回循环中的下一位"""
    if last_person not in NIGHT_SHIFT_ORDER:
        raise ValueError(f"{last_person} 不在夜班循环名单中")
    idx = NIGHT_SHIFT_ORDER.index(last_person)
    next_idx = (idx + 1) % len(NIGHT_SHIFT_ORDER)
    return NIGHT_SHIFT_ORDER[next_idx]


def is_biweekly_friday(friday_date, known_dates=None):
    """判断某个周五是否为双周五（林清雯夜班日）"""
    if known_dates is None:
        known_dates = ["2026-08-14", "2026-08-28", "2026-09-11", "2026-09-25"]
    known = [datetime.strptime(d, "%Y-%m-%d") for d in known_dates]
    target = datetime.strptime(friday_date, "%Y-%m-%d")
    for base in known:
        diff = (target - base).days
        if diff >= 0 and diff % 14 == 0:
            return True
    return False


def generate_schedule_csv(week_start_date, last_night_person, carryovers=None,
                          custom_assignments=None):
    """
    生成一周排班表的 CSV 数据

    参数:
        week_start_date: 周一日期，格式 "YYYY-MM-DD" 或 "M月D日"
        last_night_person: 上周最后一位夜班人（用于确定循环起点）
        carryovers: 跨周恢复期数据，格式:
            {"杨茜": {"days": ["夜休", "休", "休", "小夜"], "start": 0}, ...}
            start=0 表示从周一开始
        custom_assignments: 自定义固定分配，格式:
            {"李舒婕": {1: "医嘱审核", 2: "医嘱审核", ...}, ...}
            键为星期几(0=周一), 值为班次

    返回: CSV 字符串
    """
    if carryovers is None:
        carryovers = {}
    if custom_assignments is None:
        custom_assignments = {}

    # 初始化排班矩阵: staff -> [day0..day6]
    schedule = {name: [""] * 7 for name in STAFF}

    # 1. 填入跨周恢复期
    for person, info in carryovers.items():
        days = info["days"]
        start = info["start"]
        for i, shift in enumerate(days):
            day_idx = start + i
            if day_idx < 7:
                schedule[person][day_idx] = shift

    # 2. 计算本周夜班人
    night_people = []
    current = last_night_person
    friday_date_str = None  # 需要外部传入周五日期

    for day_idx in range(7):
        next_person = get_next_night_shift_person(current)
        # 检查是否为双周五
        if day_idx == 4 and friday_date_str and is_biweekly_friday(friday_date_str):
            night_people.append(BIWEEKLY_FRIDAY_NIGHT)
            # 循环不跳过，下一天继续从 next_person 的下一位
            current = next_person
        else:
            night_people.append(next_person)
            current = next_person

    # 3. 填入夜班和恢复周期
    for day_idx, person in enumerate(night_people):
        # 夜班当天
        schedule[person][day_idx] = "夜班"
        # 后续4天恢复
        for recovery_offset in range(1, 5):
            recovery_day = day_idx + recovery_offset
            if recovery_day < 7:
                schedule[person][recovery_day] = RECOVERY_CYCLE[recovery_offset]
            # 跨周恢复天数不写入本周（由下周处理）

    # 4. 填入自定义分配（固定角色）
    for person, assignments in custom_assignments.items():
        for day_idx, shift in assignments.items():
            if not schedule[person][day_idx]:  # 不覆盖已锁定的恢复期
                schedule[person][day_idx] = shift

    # 5. 构建 CSV
    rows = []
    # 标题行
    rows.append(["2026年南医三院中心药房排班表"] + [""] * 10)
    # 表头
    rows.append([""] + DAYS + ["积扣假（天）", "总积假（天）", "备注"])
    # 日期行
    date_labels = [f"{week_start_date}+{i}日" for i in range(7)]  # 简化
    rows.append([""] + date_labels + ["", "", ""])
    # 16人
    for name in STAFF:
        row = [name] + schedule[name] + ["", "", ""]
        rows.append(row)
    # 说明
    rows.append([SHIFT_DESCRIPTION] + [""] * 10)
    # 备注
    rows.append([""] + [""] * 10)

    return rows, schedule, night_people


def validate_schedule(schedule, night_people):
    """验证排班表是否满足所有约束"""
    errors = []
    warnings = []

    # 检查1: 每人恰好2天休
    for name in STAFF:
        rest_count = schedule[name].count("休")
        if rest_count != 2:
            errors.append(f"{name}: 休息天数={rest_count}（应为2）")

    # 检查2: 夜班→恢复周期
    for day_idx, person in enumerate(night_people):
        for offset in range(5):
            check_day = day_idx + offset
            if check_day < 7:
                expected = RECOVERY_CYCLE[offset]
                actual = schedule[person][check_day]
                if actual != expected:
                    errors.append(
                        f"{person}: 第{check_day}天应为{expected}，实际为{actual}"
                    )

    # 检查3: 无冲突（每人每天最多1个班次）
    # （矩阵结构本身保证了这一点，跳过）

    # 检查4: 每天合计16人
    for day_idx in range(7):
        count = sum(1 for name in STAFF if schedule[name][day_idx])
        if count != 16:
            errors.append(f"第{day_idx}天: 在岗+休息={count}（应为16）")

    # 检查5: 夜班循环顺序
    order_idx = []
    for person in night_people:
        if person in NIGHT_SHIFT_ORDER:
            order_idx.append(NIGHT_SHIFT_ORDER.index(person))
        elif person == BIWEEKLY_FRIDAY_NIGHT:
            order_idx.append(-1)  # 双周五特殊

    # 验证非双周五的夜班是否连续递增
    prev = -1
    for i, idx in enumerate(order_idx):
        if idx == -1:
            continue  # 跳过双周五
        if prev >= 0:
            expected_next = (prev + 1) % len(NIGHT_SHIFT_ORDER)
            if idx != expected_next:
                errors.append(
                    f"夜班循环: 第{i}天{night_people[i]}(序号{idx}) "
                    f"应为序号{expected_next}（前一位序号{prev}）"
                )
        prev = idx

    return errors, warnings


def main():
    if len(sys.argv) < 2:
        print("用法: python3 generate_schedule.py [generate|validate]")
        print("  generate  - 生成示例排班CSV")
        print("  validate  - 验证示例排班规则")
        sys.exit(1)

    mode = sys.argv[1]

    if mode == "generate":
        # 示例：生成一周排班
        rows, schedule, night_people = generate_schedule_csv(
            week_start_date="8月31日",
            last_night_person="杨茜",  # 上周最后一位
            carryovers={
                "杨茜": {"days": ["夜休", "休", "休", "小夜"], "start": 0},
                "冯亮": {"days": ["休", "休", "小夜"], "start": 0},
                "林清雯": {"days": ["休", "小夜"], "start": 0},
                "何乐为": {"days": ["小夜"], "start": 0},
            },
            custom_assignments={
                "李舒婕": {0: "休", 1: "医嘱审核", 2: "医嘱审核",
                          3: "医嘱审核", 4: "医嘱审核", 5: "C", 6: "休"},
            }
        )

        # 输出 CSV
        output_file = "schedule_output.csv"
        with open(output_file, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerows(rows)

        print(f"CSV 已生成: {output_file}")
        print(f"夜班序列: {night_people}")
        print(f"行数: {len(rows)}")

        # 同时输出 JSON 供调试
        print("\n排班矩阵:")
        print(f"{'姓名':<8}", end="")
        for d in DAYS:
            print(f"{d:<8}", end="")
        print()
        for name in STAFF:
            print(f"{name:<8}", end="")
            for shift in schedule[name]:
                print(f"{shift:<8}", end="")
            print()

    elif mode == "validate":
        # 验证示例排班
        rows, schedule, night_people = generate_schedule_csv(
            week_start_date="8月31日",
            last_night_person="杨茜",
            carryovers={
                "杨茜": {"days": ["夜休", "休", "休", "小夜"], "start": 0},
                "冯亮": {"days": ["休", "休", "小夜"], "start": 0},
                "林清雯": {"days": ["休", "小夜"], "start": 0},
                "何乐为": {"days": ["小夜"], "start": 0},
            },
            custom_assignments={
                "李舒婕": {0: "休", 1: "医嘱审核", 2: "医嘱审核",
                          3: "医嘱审核", 4: "医嘱审核", 5: "C", 6: "休"},
            }
        )

        errors, warnings = validate_schedule(schedule, night_people)

        if errors:
            print("验证失败:")
            for e in errors:
                print(f"  ✗ {e}")
        else:
            print("验证通过 ✓")

        if warnings:
            print("\n警告:")
            for w in warnings:
                print(f"  ⚠ {w}")

    else:
        print(f"未知模式: {mode}")


if __name__ == "__main__":
    main()
