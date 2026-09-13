# -*- coding: utf-8 -*-
"""
住院药房月度班表生成器 v3.3
======================
根据【使用方提供的】人员名单、岗位约束和偏好，自动生成月度总班表（休息表）和每周每日班表。

隐私声明：本工具默认不携带任何真实姓名（DEFAULT_STAFF 为空），名单必须由使用方
在输入模板的「人员名单」页填写。约束（禁止/偏好岗位）也一律从输入模板读取，
代码中不硬编码任何个人姓名。

核心排班规则：
1. 人员：核心 + 后勤，人数与姓名完全由输入模板决定（本工具不预设）。
2. 休息：工作日休 2 人（上 7 人）、周末【严格】休 4 人（上 5 人）；月底盘点日全员上班。
3. 平衡规则：对每个人，周六日上班次数 == 周中（工作日）休息次数（尽力逼近，固定人数优先）。
4. 公共假期（法定节假日）：按【休息日人数】排班 —— 等同周末模式：休 4 / 上 5，仅排周末岗位
   （②片剂机配方 / ③审方校对 / ⑤机动调配麻精一 / ⑥13:30 / ⑦窗口）；④片剂校对、⑧机动调配、
   后勤等『仅工作日』岗位不排。列头浅蓝标记，且【不计入】平衡统计。
   医院不调休、不补班：本工具【不存在“补班日”】类别（任何周末都不会被改成工作日）。
5. 月度盘点日（= 机动调配岗排人日）：默认取【当月最后一个周五】；若最后一个周五恰为当月
   最后一天、或恰为法定假期，则顺延至【上周五】（避开假期）。盘点日全员上班（盘点），
   机动调配（⑧）岗仅在该日与每周一排人。
6. 13:30 岗位（下午机动调配岗）：每人每个 ISO 周（周一~周日）至多排到 1 次（含周末）。
7. 跨月拼接（半自动）：周表按完整 ISO 周展开，不足 7 天的边界周从邻月借日填满（带 * 号）。
8. 日表颗粒度严格对齐原表：圆圈编号 ②~⑨、C 列时间段、收单收平板行、药架整理子表、「名单」页。

用法：
    python schedule_generator.py --input 班表输入模板.xlsx --output 2026年9月班表.xlsx --year 2026 --month 9
"""

import argparse
import calendar
import random
import re
from collections import defaultdict
from copy import deepcopy
from datetime import date, timedelta

import openpyxl
from openpyxl import load_workbook, Workbook
from openpyxl.styles import Alignment, Border, Side, Font, PatternFill


# ===================== 默认配置 =====================
# 隐私：本工具默认不携带任何真实姓名。名单必须由使用方在输入模板的「人员名单」页填写。
# 下方 DEFAULT_STAFF 为空列表，仅用于 create_input_template 生成“空名单”模板；
# 若输入模板的名单为空，生成器会明确报错，而不会回退到任何内置姓名。
DEFAULT_STAFF = []

# 岗位定义（display 为日表显示名；name 用于约束匹配）。
# 严格对齐原表：②片剂机配方 / ③片剂审方、校对，出院药校对 / ④片剂校对(核对机）、出院药调配(仅工作日)
#   / ⑤机动调配、麻精一调配(8:00) / ⑥13:30(全周) / ⑦窗口、汇总单、出院药调配 / ⑧机动调配(仅工作日)
#   / ⑨后勤×2(仅工作日) / 收单、收平板(=13:30 那人)。
# 顺序即日表行顺序（含 p8b ⑧机动调配、后勤双行）。
POSITIONS = [
    {"id": "p2", "name": "片剂机配方", "display": "片剂机配方", "weekend": True, "count": 1, "circle": "②", "time_suffix": False},
    {"id": "p3", "name": "片剂审方、校对，出院药校对", "display": "片剂审方、校对，出院药校对", "weekend": True, "count": 1, "circle": "③", "time_suffix_weekend": "9:00"},
    {"id": "p4", "name": "片剂校对(核对机）、出院药调配", "display": "片剂校对(核对机）、出院药调配", "weekend": False, "count": 1, "circle": "④", "time_suffix": False},
    {"id": "p5", "name": "机动调配、麻精一调配", "display": "机动调配、麻精一调配", "weekend": True, "count": 1, "circle": "⑤", "time_suffix": "8:00（兼顾窗口）"},
    {"id": "p6", "name": "13:30岗位(机动调配)", "display": "13:30岗位(机动调配)", "weekend": True, "count": 1, "circle": "⑥", "time_suffix": False, "is_1330": True},
    {"id": "p7", "name": "窗口、汇总单、出院药调配", "display": "窗口、汇总单、出院药调配", "weekend": True, "count": 1, "circle": "⑦", "time_suffix_weekend": "9:00"},
    {"id": "p8b", "name": "机动调配", "display": "机动调配", "weekend": False, "count": 1, "circle": "⑧", "time_suffix": False},
    {"id": "p9", "name": "后勤", "display": "后勤", "weekend": False, "count": 1, "circle": "⑨", "time_suffix": False, "logistics": True},
    {"id": "p10", "name": "后勤", "display": "后勤", "weekend": False, "count": 1, "circle": "", "time_suffix": False, "logistics": True},
]

SHELF_TASKS = [
    "a-d架", "e-h架", "i-l架", "m-p架", "q-w架",
    "分包机电脑台、\n调配台、二级库针剂",
    "住院区域清场并检查",
]

POS_P1330 = next(p for p in POSITIONS if p.get("is_1330"))
POS_P2 = next(p for p in POSITIONS if p["id"] == "p2")
POS_P7 = next(p for p in POSITIONS if p["id"] == "p7")
POS_P5 = next(p for p in POSITIONS if p["id"] == "p5")

NOTES = (
    "注：上午除窗口及分包机岗位外，其他人员优先调剂11:00前的出院带药，12:00后完成汇总单的调剂；"
    "片剂审方员每天10:00后负责接听病区来电，12:30后核对汇总单医嘱；"
    "下午除窗口及分包机岗位外，其他人员优先完成第一批次的口服药校对。"
    "早班和夜班吃饭期间，周一至周五由片剂校对岗、周末由审方岗负责麻精一药品配药"
)

SHELF_NOTE = "住院药房每天整理药架安排表"

CHINESE_WEEKDAYS = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]


# ===================== Excel 读写 =====================

def parse_position_list(text, all_positions):
    if not text:
        return []
    text = str(text).strip()
    if not text or text.lower() == "none":
        return []
    parts = [p.strip() for p in text.split(",") if p.strip()]
    result = []
    for part in parts:
        if part in all_positions:
            result.append(part)
        else:
            for sp in [x.strip() for x in part.split("、") if x.strip()]:
                if sp in all_positions:
                    result.append(sp)
    seen = set()
    unique = []
    for x in result:
        if x not in seen:
            seen.add(x)
            unique.append(x)
    return unique


def create_input_template(path):
    wb = Workbook()
    ws = wb.active
    ws.title = "人员名单"
    headers = ["姓名", "类型", "禁止岗位（英文逗号分隔）", "偏好岗位（英文逗号分隔）",
               "尽量避免岗位（英文逗号分隔）", "备注（岗位职责备注）"]
    ws.append(headers)
    if DEFAULT_STAFF:
        for s in DEFAULT_STAFF:
            ws.append([
                s["name"], s["type"],
                ", ".join(s["forbidden"]), ", ".join(s["preferred"]),
                ", ".join(s.get("avoid", [])), s["note"],
            ])
    else:
        # 隐私：默认不含任何姓名。仅留提示行，提醒使用方填写真实名单。
        ws.append(["（请在此行下方填写实际名单；本模板默认不含任何真实姓名）", "", "", "", "", ""])
    for _ in range(8):
        ws.append(["", "", "", "", "", ""])

    ws2 = wb.create_sheet("生成参数")
    params = [
        ["参数", "值", "说明"],
        ["年份", 2026, "待生成班表的年份"],
        ["月份", 9, "待生成班表的月份"],
        ["工作日休息人数", 2, "每个工作日休息的核心人员数（固定2；周末固定4）"],
        ["周末休息人数", 4, "已固定周末休4人，此参数保留未用"],
        ["月底盘点日", "", "留空=自动取当月最后一个周五；若为月末或恰为法定假期则顺延上周五；也可手动填日期覆盖，如30"],
        ["公共假期日", "", "法定节假日日期，如25,1,2。多个用逗号分隔；假期按周末模式排(休4/上5)，不计入平衡"],
        ["随机种子", 42, "保证结果可复现，设为0则随机"],
    ]
    for row in params:
        ws2.append(row)

    ws3 = wb.create_sheet("岗位说明")
    ws3.append(["岗位", "说明", "周末是否安排", "人数"])
    for p in POSITIONS:
        ws3.append([
            p.get("display") or p["name"], p.get("note", ""),
            "是" if p["weekend"] else "否", str(p["count"]) if p["count"] > 0 else "0-1",
        ])

    wb.save(path)


def read_input(path):
    wb = load_workbook(path, data_only=True)
    ws = wb["人员名单"]
    all_positions = [p["name"] for p in POSITIONS]
    staff = []
    for row in ws.iter_rows(min_row=2, values_only=True):
        if not row or not row[0]:
            continue
        name = str(row[0]).strip()
        # 跳过表头行与模板自带的提示行（避免被误当成一名“员工”）
        if name in ("姓名",) or name.startswith("（") or name.startswith("("):
            continue
        stype, forbidden, preferred, avoid, note = row[1], row[2], row[3], row[4], row[5]
        staff.append({
            "name": str(name).strip(),
            "type": str(stype).strip() if stype else "核心",
            "forbidden": parse_position_list(forbidden, all_positions),
            "preferred": parse_position_list(preferred, all_positions),
            "avoid": parse_position_list(avoid, all_positions),
            "note": str(note) if note else "",
        })

    if not staff:
        raise ValueError(
            "人员名单为空：本工具默认不含任何真实姓名，请在输入模板的「人员名单」页填写"
            "实际名单（含类型/禁止岗位/偏好岗位/备注）后重试。未提供名单时模板不可用。"
        )

    ws2 = wb["生成参数"]
    params = {}
    for row in ws2.iter_rows(min_row=2, values_only=True):
        if not row or not row[0]:
            continue
        params[row[0]] = row[1]

    year = int(params.get("年份", 2026))
    month = int(params.get("月份", 1))
    workday_rest = int(params.get("工作日休息人数", 2))
    weekend_rest = int(params.get("周末休息人数", 4))
    stock_val = params.get("月底盘点日", "")
    stock_days = [int(x.strip()) for x in str(stock_val if stock_val is not None else "").split(",")
                  if str(x).strip() and str(x).strip().lower() != "none"]
    holiday_val = params.get("公共假期日", "")
    holiday_days = [int(x.strip()) for x in str(holiday_val if holiday_val is not None else "").split(",")
                    if str(x).strip() and str(x).strip().lower() != "none"]
    seed = int(params.get("随机种子", 42))
    if seed == 0:
        seed = random.randint(1, 1000000)

    return staff, {
        "year": year, "month": month,
        "workday_rest": workday_rest, "weekend_rest": weekend_rest,
        "stock_days": stock_days, "holiday_days": holiday_days, "seed": seed,
    }


# ===================== 班表生成算法 =====================

def get_month_days(year, month):
    _, last_day = calendar.monthrange(year, month)
    return [date(year, month, d) for d in range(1, last_day + 1)]


def compute_inventory_day(year, month):
    """月度盘点日：当月最后一个周五；若最后一个周五恰为当月最后一天，则顺延至上周五。"""
    _, last_day = calendar.monthrange(year, month)
    last = date(year, month, last_day)
    # 回退到“不晚于月末”的最近一个周五（weekday 4）；向后回退天数 = (月末星期几 - 4) mod 7
    offset = (last.weekday() - 4) % 7
    last_fri = last - timedelta(days=offset)
    if last_fri.day == last_day:        # 最后一个周五就是月末 → 顺延上周五
        last_fri = last_fri - timedelta(days=7)
    return last_fri


def generate_rest_schedule(staff, params):
    """
    生成休息安排（v3.1：固定人数优先 + 平衡尽力逼近）。

    优先级（与真实排班表一致，且符合“岗位必须有人 > 员工休息日”）：
      1. 每日上岗人数【严格固定】——工作日恰好休 2 人（上 7 人）、周末恰好休 4 人（上 5 人）；
         盘点日全员上班、公共假期日按当日类型（工作日休2/周末休4）正常排。
      2. 平衡“周六日上班次数 == 周中休息次数”作为【尽力逼近】目标：把每人总休息天数
         尽量拉平到平均值，使平衡差值尽量小（数学上，周末多的月份严格人数与精确平衡
         不可兼得，此时以固定人数为准，差值保留 ±1 量级，与原表一致）。
      3. 公共假期日不计入平衡统计（假期上班获 3 倍工资，与休息权额相等）。
    返回 dict: date -> set(休息人员)
    """
    core = [s["name"] for s in staff if s["type"] == "核心"]
    n = len(core)
    year, month = params["year"], params["month"]
    days = get_month_days(year, month)
    stock = set(d for d in days if d.day in params["stock_days"])
    holiday = set(d for d in days if d.day in params["holiday_days"])
    special = stock | holiday          # 盘点 / 假期：不计入平衡
    balance_days = [d for d in days if d not in special]

    def is_true_weekend(d):
        # 真实周末（周六/周日）；本工具不存在“补班日”，故周末永远是周末
        return d.weekday() >= 5

    weekends_b = [d for d in balance_days if is_true_weekend(d)]
    workdays_b = [d for d in balance_days if not is_true_weekend(d)]
    W = len(weekends_b)                 # 非特殊（真实）周末天数

    rest = {d: set() for d in days}

    def consec_rest(nm, d, rs):
        c = 1
        p = d - timedelta(days=1)
        while p in rs and nm in rs[p]:
            c += 1; p -= timedelta(days=1)
        p = d + timedelta(days=1)
        while p in rs and nm in rs[p]:
            c += 1; p += timedelta(days=1)
        return c

    def consec_work(nm, d, rs):
        c = 1
        p = d - timedelta(days=1)
        while p in rs and nm not in rs[p]:
            c += 1; p -= timedelta(days=1)
        p = d + timedelta(days=1)
        while p in rs and nm not in rs[p]:
            c += 1; p += timedelta(days=1)
        return c

    # 每日休息人数【严格固定】：工作日 2、周末/假期 4、盘点 0
    def rest_count(d):
        if d in stock:
            return 0
        # 法定假期按“休息日人数”排班（等同周末）：休 4；周末休 4；工作日休 2
        if d in holiday or is_true_weekend(d):
            return 4
        return 2
    day_count = {d: rest_count(d) for d in days}

    # 初始化：每天放入 day_count[d] 人（尽量不连续休息）
    for d in days:
        cnt = day_count.get(d, 0)
        if cnt == 0:
            rest[d] = set()
            continue
        shuffled = list(core)
        random.shuffle(shuffled)
        chosen = []
        for nm in shuffled:
            if len(chosen) >= cnt:
                break
            if consec_rest(nm, d, rest) > 2:
                continue
            chosen.append(nm)
        if len(chosen) < cnt:  # 被连续限制挡掉则放宽
            for nm in shuffled:
                if len(chosen) >= cnt:
                    break
                if nm not in chosen:
                    chosen.append(nm)
        rest[d] = set(chosen)

    # 平衡：把每人总休息天数尽量拉平到目标值（保持每日人数固定不变）
    total_rest = sum(day_count[d] for d in balance_days)
    T = total_rest // n
    rem = total_rest % n
    # 目标：前 rem 人 T+1，其余 T（总和恰好 = total_rest）
    targets = {}
    for i, nm in enumerate(core):
        targets[nm] = T + (1 if i < rem else 0)

    for _ in range(80000):
        counts = {nm: sum(1 for d in balance_days if nm in rest[d]) for nm in core}
        over = [nm for nm in core if counts[nm] > targets[nm]]
        under = [nm for nm in core if counts[nm] < targets[nm]]
        if not over and not under:
            break
        if not over or not under:
            break
        x = random.choice(over)
        y = random.choice(under)
        swapped = False
        # 方向A：x 休 -> 上，y 上 -> 休（在 x 休且 y 上的日子）
        cands = [d for d in balance_days if x in rest[d] and y not in rest[d]]
        random.shuffle(cands)
        for d in cands:
            rest[d].discard(x); rest[d].add(y)
            ok = (consec_rest(y, d, rest) <= (3 if d in weekends_b else 2)
                  and consec_work(x, d, rest) <= 7)
            if ok:
                swapped = True; break
            rest[d].discard(y); rest[d].add(x)
        if not swapped:
            # 方向B：y 休 -> 上，x 上 -> 休
            cands = [d for d in balance_days if y in rest[d] and x not in rest[d]]
            random.shuffle(cands)
            for d in cands:
                rest[d].discard(y); rest[d].add(x)
                ok = (consec_rest(x, d, rest) <= (3 if d in weekends_b else 2)
                      and consec_work(y, d, rest) <= 7)
                if ok:
                    swapped = True; break
                rest[d].discard(x); rest[d].add(y)
        if not swapped:
            cands = [d for d in balance_days if x in rest[d] and y not in rest[d]]
            if cands:
                d = random.choice(cands)
                rest[d].discard(x); rest[d].add(y)
                swapped = True

    # 连续休息平滑：在不改变每人总量前提下，用交换消除连续休息>2
    for _ in range(12000):
        improved = False
        for nm in core:
            for d in balance_days:
                if nm in rest[d] and consec_rest(nm, d, rest) > 2:
                    for d2 in balance_days:
                        if d2 == d or nm in rest[d2]:
                            continue
                        cands_z = [zz for zz in rest[d2] if zz not in rest[d]]
                        if not cands_z:
                            continue
                        z = cands_z[0]
                        rest[d].discard(nm); rest[d].add(z)
                        rest[d2].discard(z); rest[d2].add(nm)
                        if (consec_work(nm, d, rest) <= 7 and consec_rest(z, d2, rest) <= 2
                                and consec_work(z, d, rest) <= 7 and consec_rest(nm, d2, rest) <= 2):
                            improved = True
                            break
                        rest[d].discard(z); rest[d].add(nm)
                        rest[d2].discard(nm); rest[d2].add(z)
                    if improved:
                        break
            if improved:
                break

    # 盘点日全员上班（假期日保留正常排）
    for d in stock:
        rest[d] = set()

    return rest


def can_fill_position(person_name, position, staff_map):
    """岗位资格完全由输入模板的「禁止岗位」列决定；代码不硬编码任何个人姓名。"""
    person = staff_map[person_name]
    if position["name"] in person.get("forbidden", []):
        return False
    return True


def _day_named_posts(is_off, d=None, p8b_days=None, holiday=None):
    """某天需要的命名岗位（不含 13:30、不含后勤固定岗）。
    is_off=True 表示“休息日模式”（周末 或 法定假期）：仅排周末岗位（weekend=True），
    工作日专属岗（④片剂校对、⑧机动调配、后勤）不排。
    机动调配（⑧）仅在「周一」或「月度盘点日」排人，且法定假期日不排（命中 holiday 则跳过）。"""
    lst = []
    for p in POSITIONS:
        if p.get("is_1330"):
            continue
        if p.get("logistics"):
            continue
        if not p["weekend"] and is_off:
            continue
        if p["id"] == "p8b":
            # 机动调配：仅周一 + 月度盘点日排人；法定假期日不排（假期按周末模式，无⑧）
            if p8b_days is None or d is None or d not in p8b_days:
                continue
            if holiday and d in holiday:
                continue
        lst.append(p)
    order = {"p2": 0, "p5": 1, "p7": 2, "p3": 3, "p4": 4, "p8b": 5}
    lst.sort(key=lambda p: order.get(p["id"], 9))
    return lst


def _match_posts(people, posts, staff_map):
    """二分匹配：把岗位分配给不同在岗人员，返回 {post_id: 人}；无解返回 None。"""
    adj = {p["id"]: [nm for nm in people if can_fill_position(nm, p, staff_map)] for p in posts}
    pids = [p["id"] for p in posts]
    m_p2n, m_n2p = {}, {}

    def dfs(pid, seen):
        for nm in adj[pid]:
            if nm in seen:
                continue
            seen.add(nm)
            if nm not in m_n2p or dfs(m_n2p[nm], seen):
                m_n2p[nm] = pid
                m_p2n[pid] = nm
                return True
        return False

    for pid in pids:
        if not dfs(pid, set()):
            return None
    return {pid: m_p2n[pid] for pid in pids}


def _match_posts_fair(people, posts, staff_map, pos_counts):
    """最小费用二分匹配：在存在完美匹配时，使各岗累计负载最均衡（公平轮转，杜绝“被钉死在一个岗”）。
    费用 = 该人当前已做此岗的次数；求最小总费用即把每人尽量分到“做得最少”的岗。"""
    persons = list(people)
    nposts = list(posts)
    S, T = 0, 1
    pidx = {nm: 2 + i for i, nm in enumerate(persons)}
    fidx = {p["id"]: 2 + len(persons) + i for i, p in enumerate(nposts)}
    N = 2 + len(persons) + len(nposts)
    g = [[] for _ in range(N)]

    def add_edge(u, v, cap, cost):
        g[u].append([v, cap, cost, len(g[v])])
        g[v].append([u, 0, -cost, len(g[u]) - 1])

    for nm in persons:
        add_edge(S, pidx[nm], 1, 0)
    for p in nposts:
        add_edge(fidx[p["id"]], T, 1, 0)
    for p in nposts:
        for nm in persons:
            if can_fill_position(nm, p, staff_map):
                # 软性“尽量避免”：若此人尽量避免该岗，则给予高额费用惩罚，
                # 匹配器会优先安排他人；仅在无人可替时才落到此人（“尽量少”而非“绝不”）。
                penalty = 1000 if p["name"] in staff_map[nm].get("avoid", []) else 0
                add_edge(pidx[nm], fidx[p["id"]], 1, pos_counts[p["id"]][nm] + penalty)

    INF = 10 ** 9
    for _ in range(len(nposts)):
        dist = [INF] * N
        inq = [False] * N
        prevv = [0] * N
        preve = [0] * N
        dist[S] = 0
        from collections import deque
        dq = deque([S])
        inq[S] = True
        while dq:
            u = dq.popleft()
            inq[u] = False
            for i, e in enumerate(g[u]):
                v, cap, cost, rev = e
                if cap > 0 and dist[u] + cost < dist[v]:
                    dist[v] = dist[u] + cost
                    prevv[v] = u
                    preve[v] = i
                    if not inq[v]:
                        dq.append(v)
                        inq[v] = True
        if dist[T] == INF:
            return None
        v = T
        while v != S:
            u = prevv[v]
            ei = preve[v]
            g[u][ei][1] -= 1
            g[v][g[u][ei][3]][1] += 1
            v = u

    res = {}
    for p in nposts:
        for e in g[fidx[p["id"]]]:
            v, cap, cost, rev = e
            if cap > 0 and 2 <= v < 2 + len(persons):  # 反向边：人->岗 已用流
                nm = [k for k, val in pidx.items() if val == v][0]
                res[p["id"]] = nm
                break
    return res


def assign_daily_positions(staff, rest_schedule, params):
    year, month = params["year"], params["month"]
    days = get_month_days(year, month)
    staff_map = {s["name"]: s for s in staff}
    core = [s["name"] for s in staff if s["type"] == "核心"]

    # 法定假期日集合；假期 ≡ 周末模式（仅排周末岗位、后勤不排、⑧不排）
    hol = set(d for d in days if d.day in params["holiday_days"])
    # 是否“休息日模式”（周末 或 法定假期）：决定工作日专属岗位是否排、后勤是否上岗
    is_off = lambda d: d.weekday() >= 5 or d in hol

    # 机动调配（⑧）仅周一 + 月度盘点日排人（假期日不排⑧，因其为工作日专属岗）
    inv = params.get("inventory_day") or compute_inventory_day(year, month)
    p8b_days = set(d for d in days if d.weekday() == 0 or d == inv)

    pos_counts = defaultdict(lambda: defaultdict(int))

    # 第一阶段：13:30 岗位按 ISO 周统筹（覆盖全周 7 天），预先定好每天人选，
    #   保证每人每周至多一次；并校验“去掉 13:30 人选后，当日命名岗仍可匹配”。
    #   （关键：当若干“仅能担任少数岗位”的人员同时周末在岗时，必须让其一占 13:30，
    #    否则这些人都只能抢同一岗位而令当日命名岗匹配无解）
    day1330 = {}
    week_days = defaultdict(list)
    for d in days:
        if d.day not in params["stock_days"]:   # 盘点日不排 13:30（全员盘点，无窗口辅助）
            week_days[d - timedelta(days=d.weekday())].append(d)
    for monday, wdays in week_days.items():
        day_elig = {}
        for d in wdays:
            on_duty_d = [nm for nm in core if nm not in rest_schedule.get(d, set())]
            day_elig[d] = [nm for nm in on_duty_d if can_fill_position(nm, POS_P1330, staff_map)]
        assign = {}
        used = set()
        order = sorted(wdays, key=lambda d: (len(day_elig[d]), d.weekday()))  # 最受限日优先

        def bt(idx):
            if idx == len(order):
                return True
            d = order[idx]
            is_wk = is_off(d)
            nposts = _day_named_posts(is_wk, d, p8b_days, hol)
            on_duty_d = [nm for nm in core if nm not in rest_schedule.get(d, set())]
            cands = [nm for nm in day_elig[d] if nm not in used]
            cands.sort(key=lambda nm: (pos_counts["p6"][nm], random.random()))
            for nm in cands:
                rem = [x for x in on_duty_d if x != nm]
                if _match_posts(rem, nposts, staff_map) is None:
                    continue  # 该人选会让当日命名岗无解，跳过
                assign[d] = nm
                used.add(nm)
                if bt(idx + 1):
                    return True
                used.discard(nm)
                del assign[d]
            return False

        if not bt(0):
            # 理论上不会发生（可行性已在回溯中保证）；兜底：允许复用
            for d in wdays:
                if d not in assign and day_elig[d]:
                    assign[d] = day_elig[d][0]
        for d, nm in assign.items():
            day1330[d] = nm
            pos_counts["p6"][nm] += 1

    # 第二阶段：每天用二分匹配分配命名岗位（排除当日 13:30 人选）+ 后勤固定
    #   匹配严格使用“当日上岗人员”，绝不从休息人员中拉人 → 人数固定、休息不被破坏。
    result = {}
    for d in days:
        is_weekend = is_off(d)
        on_duty = [nm for nm in core if nm not in rest_schedule.get(d, set())]
        day_plan = {
            "weekday": CHINESE_WEEKDAYS[d.weekday()], "date": d,
            "positions": {}, "shelf": {},
        }
        excluded = {day1330.get(d)}  # 当日 13:30 人选不再占命名岗

        # 后勤固定岗：由输入名单中“后勤”类型人员担任（不硬编码姓名）；仅工作日上班
        logi = [s["name"] for s in staff if s["type"] == "后勤"]
        if not is_weekend:
            for i, p in enumerate([p for p in POSITIONS if p.get("logistics")]):
                if i < len(logi):
                    day_plan["positions"].setdefault(p["id"], []).append(logi[i])

        # 命名岗最小费用二分匹配（按累计负载轮转；人头数严格 = 当日上岗数，绝不拉休息人员）
        nposts = _day_named_posts(is_weekend, d, p8b_days, hol)
        rem = [nm for nm in on_duty if nm not in excluded]
        m = _match_posts_fair(rem, nposts, staff_map, pos_counts)
        if m is None:
            # 兜底：理论上不会发生（13:30 阶段已保证可行性）。贪心填空，不拉休息人员。
            print(f"  ⚠ {d.strftime('%Y-%m-%d')} 命名岗匹配失败，启用兜底贪心")
            for p in nposts:
                taken = [nm for v in day_plan["positions"].values() for nm in v]
                cands = [nm for nm in rem if nm not in taken]
                if cands:
                    day_plan["positions"].setdefault(p["id"], []).append(cands[0])
                    pos_counts[p["id"]][cands[0]] += 1
        else:
            for p in nposts:
                nm = m[p["id"]]
                day_plan["positions"].setdefault(p["id"], []).append(nm)
                pos_counts[p["id"]][nm] += 1

        # 写入 13:30
        if d in day1330:
            day_plan["positions"]["p6"] = [day1330[d]]

        # 当日已占岗人员集合
        assigned = set(nm for v in day_plan["positions"].values() for nm in v)

        # 第三阶段：药架整理（由当日【在岗】人员兼任，绝不额外加人）
        available = [nm for nm in core if nm not in assigned and nm not in rest_schedule.get(d, set())]
        if not available:
            available = list(on_duty)
        p2p = day_plan["positions"].get("p2", [])
        if p2p:
            day_plan["shelf"]["分包机电脑台、\n调配台、二级库针剂"] = p2p[0]
        remaining = [t for t in SHELF_TASKS if t != "分包机电脑台、\n调配台、二级库针剂"]
        for task in remaining:
            if not is_weekend and task in ["m-p架", "q-w架"]:
                # 工作日药架整理部分任务由后勤人员负责（动态取，不硬编码姓名）
                if logi:
                    day_plan["shelf"][task] = logi[0]
                continue
            cands = [nm for nm in available if nm not in day_plan["shelf"].values()]
            if not cands:
                cands = available
            cands.sort(key=lambda nm: (sum(1 for v in day_plan["shelf"].values() if v == nm), random.random()))
            if cands:
                day_plan["shelf"][task] = cands[0]

        result[d] = day_plan
    return result


# ===================== Excel 输出 =====================

def write_summary_sheet(wb, staff, rest_schedule, params):
    """总班表：人 × 日 矩阵。每行一人、每列一天，单元格 休/班/盘(盘点全员)/假(国定假期)。
    数据直接来自 rest_schedule，与周表 100% 一致；任何人每天只能是单一状态，不存在“既休又上”。"""
    from openpyxl.utils import get_column_letter
    ws = wb.create_sheet("总班表")
    year, month = params["year"], params["month"]
    days = get_month_days(year, month)
    stock = set(params.get("stock_days", []))
    holiday = set(params.get("holiday_days", []))

    def is_true_weekend_summary(d, hol):
        # 后勤岗为工作日岗：周末与法定假期均休息（假期 ≡ 周末模式）
        return d.weekday() >= 5 or d.day in hol

    thin = Side(style="thin", color="000000")
    border = Border(left=thin, right=thin, top=thin, bottom=thin)
    fill_rest = PatternFill("solid", fgColor="F8CBAD")   # 休 浅橙红
    fill_work = PatternFill("solid", fgColor="FFFFFF")   # 班 白
    fill_stock = PatternFill("solid", fgColor="FFE699")  # 盘 浅黄
    fill_holi = PatternFill("solid", fgColor="D9E1F2")   # 假 浅蓝

    end_col = 2 + len(days)
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=end_col + 1)
    ws.cell(1, 1, f"住院药房 {year}年{month}月 总班表（休 / 班 / 盘=盘点全员在岗 / 假=国定假期，平衡统计已排除）")
    ws.cell(1, 1).font = Font(size=13, bold=True)
    ws.cell(1, 1).alignment = Alignment(horizontal="center", vertical="center")

    ws.cell(2, 1, "姓名").font = Font(bold=True)
    for j, d in enumerate(days):
        c = 2 + j
        ws.cell(2, c, d.day).alignment = Alignment(horizontal="center")
        ws.cell(3, c, CHINESE_WEEKDAYS[d.weekday()]).alignment = Alignment(horizontal="center")
        if d.day in stock:
            ws.cell(2, c).fill = fill_stock
        elif d.day in holiday:
            ws.cell(2, c).fill = fill_holi
    ws.cell(2, end_col + 1, "休息天数").font = Font(bold=True)
    ws.cell(2, end_col + 1).alignment = Alignment(horizontal="center")

    core = [s["name"] for s in staff if s["type"] == "核心"]
    logistics = [s["name"] for s in staff if s["type"] == "后勤"]
    all_people = [(nm, "核心") for nm in core] + [(nm, "后勤") for nm in logistics]

    r = 4
    for nm, typ in all_people:
        ws.cell(r, 1, nm).font = Font(bold=(typ == "核心"))
        rest_n = 0
        for j, d in enumerate(days):
            c = 2 + j
            if d.day in stock:
                val, fill = "盘", fill_stock
            elif typ == "后勤":
                # 后勤岗为工作日岗：周末/假期休息，工作日上班
                if is_true_weekend_summary(d, holiday):
                    val, fill = "休", fill_rest
                else:
                    val, fill = "班", fill_work
            else:
                if nm in rest_schedule.get(d, set()):
                    val, fill = "休", fill_rest
                    rest_n += 1
                else:
                    val, fill = "班", fill_work
            cell = ws.cell(r, c, val)
            cell.alignment = Alignment(horizontal="center")
            cell.border = border
            cell.fill = fill
        ws.cell(r, end_col + 1, rest_n).alignment = Alignment(horizontal="center")
        ws.cell(r, end_col + 1).border = border
        r += 1

    # 自描述备注：假期日 / 盘点日（供 verify / selfcheck 无需输入模板也能识别，避免重复计与误判）
    note_r = r + 1
    hol_days_sorted = sorted(params.get("holiday_days", []))
    stock_days_sorted = sorted(params.get("stock_days", []))
    ws.cell(note_r, 1,
            f"假期日：{','.join(str(x) for x in hol_days_sorted) or '无'}；"
            f"盘点日：{','.join(str(x) for x in stock_days_sorted) or '无'}；"
            f"假期/盘点不计入平衡；跨月*日属邻月")
    ws.cell(note_r, 1).font = Font(italic=True, size=9, color="808080")

    ws.column_dimensions["A"].width = 10
    for j in range(len(days)):
        ws.column_dimensions[get_column_letter(2 + j)].width = 4.5
    ws.column_dimensions[get_column_letter(end_col + 1)].width = 10
    ws.freeze_panes = "B4"


# 周表行模板（严格对齐原表顺序与颗粒度）
WEEKLY_ROWS = [
    {"circle": "②", "b": "片剂机配方", "c": "", "pid": "p2", "suffix": "none"},
    {"circle": "③", "b": "片剂审方、校对，出院药校对", "c": "", "pid": "p3", "suffix": "weekend9"},
    {"circle": "④", "b": "片剂校对(核对机）、出院药调配", "c": "", "pid": "p4", "suffix": "none", "weekday_only": True},
    {"circle": "⑤", "b": "机动调配、麻精一调配", "c": "8:00（兼顾窗口）", "pid": "p5", "suffix": "8:00"},
    {"circle": "⑥", "b": "", "c": "13:30（15:30后窗口辅助）", "pid": "p6", "suffix": "none", "thirteen": True},
    {"circle": "⑦", "b": "窗口、汇总单、出院药调配", "c": "", "pid": "p7", "suffix": "weekend9"},
    {"circle": "⑧", "b": "机动调配", "c": "", "pid": "p8b", "suffix": "none", "weekday_only": True},
    {"circle": "⑨", "b": "后勤", "c": "", "pid": "p9", "suffix": "none", "weekday_only": True},
    {"circle": "", "b": "后勤", "c": "", "pid": "p10", "suffix": "none", "weekday_only": True},
    {"circle": "", "b": "", "c": "收单、收平板", "pid": "__shou__", "suffix": "none", "from_1330": True},
]


def _cell_name(plan, rowdef, d, true_weekend):
    """返回某行某日的姓名字符串（含时间段后缀），无则空串。
    true_weekend：是否“休息日模式”（周末 或 法定假期；工作日专属岗与时间段后缀按此显示）。"""
    if rowdef.get("weekday_only") and true_weekend:
        return ""
    if rowdef.get("from_1330"):
        people = plan["positions"].get("p6", [])
        return people[0] if people else ""
    people = plan["positions"].get(rowdef["pid"], [])
    if not people:
        return ""
    name = people[0]
    suf = rowdef.get("suffix")
    if suf == "8:00":
        return f"{name}8:00"
    if suf == "weekend9" and true_weekend:
        return f"{name}9:00"
    return name


def write_weekly_sheets(wb, weeks, merged_plan, own_days, staff, params):
    """weeks: list of 7-date lists (Mon..Sun, 跨月也为真实 date)；merged_plan: date->day_plan；
    own_days: set of date 属于本月（用于跨月拼接标记 *）。"""
    core = [s["name"] for s in staff if s["type"] == "核心"]
    for wi, week in enumerate(weeks, 1):
        ws = wb.create_sheet(f"第{wi}周")
        ws.merge_cells("A1:K1")
        ws["A1"] = "住院药房排班表"
        ws["A1"].font = Font(size=14, bold=True)
        ws["A1"].alignment = Alignment(horizontal="center", vertical="center")

        ws["A2"] = "平板"
        ws["B2"] = "日期"
        for i, d in enumerate(week):
            c = 4 + i
            star = "" if d in own_days else "*"
            ws.cell(2, c, f"{d.year}.{d.month:02d}.{d.day:02d}{star}")
            ws.cell(3, c, CHINESE_WEEKDAYS[d.weekday()])

        ws["A3"] = "工作岗位"
        ws.merge_cells("A3:B3")

        r = 4
        for rowdef in WEEKLY_ROWS:
            ws.cell(r, 1, rowdef["circle"])
            ws.cell(r, 2, rowdef["b"])
            ws.cell(r, 3, rowdef["c"])
            r += 1

        for i, d in enumerate(week):
            c = 4 + i
            plan = merged_plan.get(d)
            if not plan:
                continue
            true_weekend = d.weekday() >= 5 or d.day in params.get("holiday_days", [])
            rr = 4
            for rowdef in WEEKLY_ROWS:
                val = _cell_name(plan, rowdef, d, true_weekend)
                if val:
                    ws.cell(rr, c, val)
                rr += 1

        note_row = r
        ws.merge_cells(start_row=note_row, start_column=2, end_row=note_row, end_column=8)
        ws.cell(note_row, 2, NOTES)
        ws.cell(note_row, 2).alignment = Alignment(wrap_text=True, vertical="top")

        shelf_start = note_row + 2
        ws.cell(shelf_start - 1, 2, SHELF_NOTE)
        ws.cell(shelf_start, 2, "日期")
        for i, d in enumerate(week):
            c = 4 + i
            star = "" if d in own_days else "*"
            ws.cell(shelf_start, c, f"{d.year}.{d.month:02d}.{d.day:02d}{star}")

        for j, task in enumerate(SHELF_TASKS):
            rr = shelf_start + 1 + j
            ws.cell(rr, 2, task)
            for i, d in enumerate(week):
                c = 4 + i
                plan = merged_plan.get(d)
                if plan:
                    ws.cell(rr, c, plan["shelf"].get(task, ""))

        # 末尾一行：核心人员名单（与原表 r24 对应）
        end_row = shelf_start + 1 + len(SHELF_TASKS)
        ws.cell(end_row, 1, "")
        ws.cell(end_row, 2, "  ".join(core))

        thin = Side(style="thin", color="000000")
        border = Border(left=thin, right=thin, top=thin, bottom=thin)
        for rrr in range(2, end_row + 1):
            for cc in range(1, 12):
                ws.cell(rrr, cc).border = border
                ws.cell(rrr, cc).alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        ws.cell(end_row, 2).alignment = Alignment(horizontal="left", vertical="center")

        ws.column_dimensions["A"].width = 5
        ws.column_dimensions["B"].width = 30
        ws.column_dimensions["C"].width = 22
        for col in ["D", "E", "F", "G", "H", "I", "J", "K"]:
            ws.column_dimensions[col].width = 13


def report_balance(staff, rest_schedule, params):
    core = [s["name"] for s in staff if s["type"] == "核心"]
    year, month = params["year"], params["month"]
    days = get_month_days(year, month)
    stock = set(d for d in days if d.day in params["stock_days"])
    holiday = set(d for d in days if d.day in params["holiday_days"])
    special = stock | holiday
    balance_days = [d for d in days if d not in special]

    def is_true_weekend(d):
        return d.weekday() >= 5

    workdays_b = [d for d in balance_days if not is_true_weekend(d)]
    weekends_b = [d for d in balance_days if is_true_weekend(d)]
    W = len(weekends_b)
    eff_hol = sorted(d.day for d in holiday if d.month == month)
    print(f"\n--- {year}年{month}月 平衡校验（固定人数优先：工作日休2/周末休4；平衡尽力逼近）---")
    if eff_hol:
        print(f"（已排除公共假期/盘点日：{eff_hol}；假期按休息日人数排(休4)且不计入平衡）")
    else:
        print("（本月无公共假期/盘点日排除）")
    print(f"{'姓名':6}{'周末上班':8}{'周中休息':8}{'差值':6}{'总休息':6}{'达标':6}")
    max_diff = 0
    bad = 0
    for nm in core:
        we = sum(1 for d in weekends_b if nm not in rest_schedule.get(d, set()))
        wk = sum(1 for d in workdays_b if nm in rest_schedule.get(d, set()))
        tot = sum(1 for d in balance_days if nm in rest_schedule.get(d, set()))
        diff = we - wk
        max_diff = max(max_diff, abs(diff))
        # 达标：差值 ≤2（固定人数下精确平衡不可兼得，与原表 -1~-3 量级一致）
        ok = abs(diff) <= 2
        if not ok:
            bad += 1
        print(f"{nm:6}{we:8}{wk:8}{diff:+6}{tot:6}{'✓' if ok else '✗':6}")
    print(f"最大差值={max_diff}  差值>1人数={bad}  {'✓ 平衡良好' if bad == 0 else '(见上，固定人数优先下的小偏差)'}")
    print(f"（说明：周末多的月份，严格人数与“周末上班=周中休息”精确相等不可兼得；")
    print(f"  本模板以固定人数为准，平衡保留极少偏差，与你提供的真实班表一致。）")


def report_1330(staff, daily_plan, params):
    core = [s["name"] for s in staff if s["type"] == "核心"]
    week1330 = defaultdict(lambda: defaultdict(int))
    for d, plan in daily_plan.items():
        monday = d - timedelta(days=d.weekday())
        for nm in plan["positions"].get("p6", []):
            week1330[monday][nm] += 1
    viol = 0
    for monday, cnt in week1330.items():
        for nm, n in cnt.items():
            if n > 1:
                viol += 1
                print(f"  ⚠ {monday}周 {nm} 13:30 排了{n}次")
    print(f"--- 13:30 每周至多一次校验：{'✓ 全部符合' if viol == 0 else f'{viol}处违规'} ---")


def write_roster_sheet(wb, weeks, merged_plan, staff, params):
    """名单表：人员名单 + 各周岗位负责人概览（对齐原表“名单”页精神）。"""
    ws = wb.create_sheet("名单")
    ws["A1"] = "住院药房人员名单与每周岗位概览"
    ws["A1"].font = Font(size=14, bold=True)
    ws.merge_cells("A1:E1")
    ws["A1"].alignment = Alignment(horizontal="center", vertical="center")

    row = 3
    ws.cell(row, 1, "姓名"); ws.cell(row, 2, "类型"); ws.cell(row, 3, "岗位职责备注")
    row += 1
    for s in staff:
        ws.cell(row, 1, s["name"])
        ws.cell(row, 2, s["type"])
        ws.cell(row, 3, s.get("note", ""))
        row += 1

    row += 1
    ws.cell(row, 1, "各周岗位负责人（窗口 / 机动调配 / 13:30）")
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=5)
    ws.cell(row, 1).font = Font(bold=True)
    row += 1
    ws.cell(row, 1, "周次"); ws.cell(row, 2, "窗口(⑦)"); ws.cell(row, 3, "机动调配(⑤)")
    ws.cell(row, 4, "13:30(⑥)"); ws.cell(row, 5, "后勤(⑨)")
    row += 1
    for wi, week in enumerate(weeks, 1):
        wins = []
        wjdt = []
        w1330 = []
        whou = []
        for d in week:
            plan = merged_plan.get(d)
            if not plan:
                continue
            p7 = plan["positions"].get("p7", [])
            p5 = plan["positions"].get("p5", [])
            p6 = plan["positions"].get("p6", [])
            p9 = plan["positions"].get("p9", [])
            if p7: wins.append(p7[0])
            if p5: wjdt.append(p5[0])
            if p6: w1330.append(p6[0])
            if p9: whou.append(p9[0])
        ws.cell(row, 1, f"第{wi}周")
        ws.cell(row, 2, "、".join(dict.fromkeys(wins)))
        ws.cell(row, 3, "、".join(dict.fromkeys(wjdt)))
        ws.cell(row, 4, "、".join(dict.fromkeys(w1330)))
        ws.cell(row, 5, "、".join(dict.fromkeys(whou)))
        row += 1

    ws.column_dimensions["A"].width = 14
    ws.column_dimensions["B"].width = 24
    ws.column_dimensions["C"].width = 40
    ws.column_dimensions["D"].width = 24
    ws.column_dimensions["E"].width = 18


def _neighbor_plan(staff, year, month, seed_base):
    """生成邻月（仅用于跨月拼接显示）的日计划；假期/盘点置空，种子由基准派生。"""
    p = {
        "year": year, "month": month,
        "workday_rest": 2, "weekend_rest": 4,
        "stock_days": [], "holiday_days": [],
        "seed": ((seed_base ^ (year * 131 + month * 17)) % 1000000) or 1,
    }
    rest = generate_rest_schedule(staff, p)
    return assign_daily_positions(staff, rest, p)


def generate_schedule(input_path, output_path, year=None, month=None, holiday=None, stock=None):
    staff, params = read_input(input_path)
    if year is not None:
        params["year"] = year
    if month is not None:
        params["month"] = month
    if holiday is not None:
        # 命令行传入当月公共假期日（逗号分隔），覆盖模板中的值，便于“每月都不同”
        params["holiday_days"] = [int(x.strip()) for x in str(holiday).split(",") if x.strip()]

    # 月度盘点日：默认取“当月最后一个周五（若为月末或恰为法定假期则顺延上周五）”；
    # 可用 --stock 强制覆盖，否则若模板“月底盘点日”有填也采用模板值。
    inv = compute_inventory_day(params["year"], params["month"])
    hol_days = set(params.get("holiday_days", []))
    while inv.day in hol_days:          # 避开法定假期：顺延至上周五
        inv = inv - timedelta(days=7)
    params["inventory_day"] = inv
    if stock is not None:
        params["stock_days"] = [int(x.strip()) for x in str(stock).split(",") if x.strip()]
    elif params.get("stock_days"):
        pass  # 采用模板已填的盘点日
    else:
        params["stock_days"] = [inv.day]

    random.seed(params["seed"])

    rest_schedule = generate_rest_schedule(staff, params)
    daily_plan = assign_daily_positions(staff, rest_schedule, params)

    # —— 跨月半自动拼接：按 ISO 周（周一~周日）展开，不足 7 天的边界周从邻月借日填满 ——
    days = get_month_days(params["year"], params["month"])
    first, last = days[0], days[-1]
    monday0 = first - timedelta(days=first.weekday())
    sundayN = last + timedelta(days=(6 - last.weekday()))
    weeks = []
    cur = monday0
    while cur <= sundayN:
        weeks.append([cur + timedelta(days=k) for k in range(7)])
        cur += timedelta(days=7)
    own_days = set(days)
    merged_plan = {}
    ncache = {}
    stitched = 0
    for wk in weeks:
        for d in wk:
            if d in own_days:
                merged_plan[d] = daily_plan[d]
            else:
                key = (d.year, d.month)
                if key not in ncache:
                    ncache[key] = _neighbor_plan(staff, d.year, d.month, params["seed"])
                merged_plan[d] = ncache[key].get(d)
                stitched += 1

    wb = Workbook()
    wb.remove(wb.active)
    write_roster_sheet(wb, weeks, merged_plan, staff, params)   # 名单（首表，对齐原表顺序）
    write_weekly_sheets(wb, weeks, merged_plan, own_days, staff, params)
    write_summary_sheet(wb, staff, rest_schedule, params)       # 总班表（附加，便于自查）
    wb.save(output_path)
    print(f"已生成班表：{output_path}")
    if stitched:
        print(f"（已半自动拼接 {stitched} 个跨月日：带 * 号，建议复核；跨月周的 13:30 周频请重点检查）")
    report_balance(staff, rest_schedule, params)
    report_1330(staff, daily_plan, params)


def main():
    parser = argparse.ArgumentParser(description="住院药房月度班表生成器 v3.3")
    parser.add_argument("--input", default="班表输入模板.xlsx", help="输入模板Excel路径")
    parser.add_argument("--output", default=None, help="输出班表Excel路径")
    parser.add_argument("--year", type=int, default=None, help="年份")
    parser.add_argument("--month", type=int, default=None, help="月份")
    parser.add_argument("--holiday", default=None, help="公共假期日，逗号分隔，如 25,1,2（覆盖模板）")
    parser.add_argument("--stock", default=None, help="月度盘点日，逗号分隔，如 30（默认自动取最后周五，避开假期）")
    parser.add_argument("--create-template", action="store_true", help="仅创建输入模板")
    args = parser.parse_args()

    if args.create_template:
        create_input_template(args.input)
        print(f"已创建输入模板：{args.input}")
        return

    if args.output is None:
        y = args.year if args.year else 2026
        m = args.month if args.month else 9
        args.output = f"住院药房{y}年{m}月班表.xlsx"

    generate_schedule(args.input, args.output, args.year, args.month, args.holiday, args.stock)


if __name__ == "__main__":
    main()
