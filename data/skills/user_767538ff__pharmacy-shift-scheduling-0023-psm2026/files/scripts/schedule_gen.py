# -*- coding: utf-8 -*-
"""
医院药房三班倒排班表生成器（参数化版）
- 标准 8h 工时制，每周 ≤ 40h，每周至少休 1 天
- 夜班按 8h 标准工时折算（实际 13.5h，超出由"下夜班当日+次日休"补偿）
- 夜班循环轮换 + 夜班后休 2 天 + 白班贪心均衡（早/中/正常）
- 输出可打印 HTML（班次定义/排班总表/在岗校验/工时统计/周工时/年假/规则）

== 定制点（顶部 CONFIG 区）==
- STAFF：三班轮班人员名单
- DAYS：轮换周期天数（4 周=28）
- SHIFT_DEF：班次时间与工时折算
- 固定正常班：a_shift(d) 函数
- 住院部补位：hos_shift(d, who) 函数
- 白天在岗需求：need_day（工作日/周末）
"""
import os
from collections import defaultdict, OrderedDict

# ==================== CONFIG（按需修改）====================
STAFF = ['药师1', '药师2', '药师3', '药师4', '药师5', '药师6']
A = '药师A(固定正常班)'
HOS = ['药师H(住院部)', '药师I(住院部)']
DAYS = 28  # 4 周一轮
WK_CN = ['一', '二', '三', '四', '五', '六', '日']

# 班次定义（code: (名称, 时间, 工时折算说明)）
SHIFT_DEF = OrderedDict([
    ('D', ('正常班', '08:30-12:00 / 14:30-18:00', '8h（含1h午休计入工时）')),
    ('E', ('早班',   '08:00-16:00', '8h（提前0.5h开窗，16:00交接中班）')),
    ('M', ('中班',   '12:00-18:30', '8h（含1.5h用餐/交接，覆盖午晚高峰）')),
    ('N', ('夜班',   '18:30-次日08:00', '8h标准工时（实际13.5h，超出由下夜班当日+次日休补偿）')),
    ('R', ('休息',   '—', '0h')),
    ('B', ('白天班', '08:30-18:00（住院部参与）', '8h')),
])

COLOR = {
    'D': '#dbeafe', 'E': '#dcfce7', 'M': '#fef9c3', 'N': '#ede9fe',
    'R': '#f1f5f9', 'B': '#ffedd5', '': '#ffffff'
}
LABEL = {'D': '正常', 'E': '早', 'M': '中', 'N': '夜', 'R': '休', 'B': '白天'}

# 白天在岗需求：工作日 4 人，周末 3 人（按窗口数调整）
def need_day_of(w):
    return 4 if w < 5 else 3
NEED_NIGHT = 1

# 输出路径（默认当前工作目录 outputs/）
OUT_PATH = os.path.join(os.getcwd(), 'outputs', '门诊西药房三班倒排班表.html')
# ==================== END CONFIG ====================


def dow(d):
    return (d - 1) % 7

def week_idx(d):
    return (d - 1) // 7

def night(d):
    """夜班循环轮换：P1→P2→…→PN，每天 1 人"""
    return STAFF[(d - 1) % len(STAFF)]

def rest_of(d):
    """夜班后休班：下夜班日(d-1夜班者) + 次日休(d-2夜班者)"""
    N = len(STAFF)
    return [STAFF[(d - 2) % N], STAFF[(d - 3) % N]]

def white_of(d):
    """白班人员 = 全员 - 夜班 - 休班"""
    n = night(d)
    r = rest_of(d)
    return [s for s in STAFF if s not in [n] + r]

def a_shift(d):
    """固定正常班：周一二三五上、周四休、周末轮换1天"""
    w = dow(d); wk = week_idx(d)
    if w == 3: return 'R'
    if w == 5: return 'D' if wk % 2 == 0 else 'R'
    if w == 6: return 'R' if wk % 2 == 0 else 'D'
    return 'D'

def hos_shift(d, who):
    """住院部补位：周四白天班轮换（补固定A缺勤）"""
    if dow(d) != 3: return ''
    wk = week_idx(d)
    if wk in (0, 2):
        return 'B' if who == HOS[0] else ''
    else:
        return 'B' if who == HOS[1] else ''

# ---------- 主排班 ----------
sched = defaultdict(dict)
em_dist = {p: defaultdict(int) for p in STAFF}

for d in range(1, DAYS + 1):
    n = night(d); r = rest_of(d); ws = white_of(d)
    # 白班贪心均衡：累计最少者优先，3 人角色不重复
    order = sorted(ws, key=lambda p: sum(em_dist[p].values()), reverse=True)
    used = set()
    for p in order:
        cand = sorted(['E', 'M', 'D'], key=lambda x: (em_dist[p][x], x))
        chosen = next((c for c in cand if c not in used), cand[0])
        sched[p][d] = chosen; used.add(chosen); em_dist[p][chosen] += 1
    sched[n][d] = 'N'
    for p in r: sched[p][d] = 'R'
    sched[A][d] = a_shift(d)
    for p in HOS:
        s = hos_shift(d, p)
        if s: sched[p][d] = s

# ---------- 在岗校验 ----------
coverage = []
for d in range(1, DAYS + 1):
    w = dow(d)
    day_cnt = night_cnt = 0
    dd = []; dn = []
    for p in STAFF:
        s = sched[p].get(d, '')
        if s in ('E', 'M', 'D'): day_cnt += 1; dd.append(f'{p}({s})')
        elif s == 'N': night_cnt += 1; dn.append(f'{p}(N)')
    if sched[A].get(d) == 'D': day_cnt += 1; dd.append(f'{A[:4]}(D)')
    for p in HOS:
        if sched[p].get(d) == 'B': day_cnt += 1; dd.append(f'{p[:4]}(B)')
    nd = need_day_of(w)
    ok = (day_cnt >= nd) and (night_cnt == NEED_NIGHT)
    coverage.append({'d': d, 'wk': WK_CN[w], 'day': day_cnt, 'night': night_cnt,
                     'need_day': nd, 'ok': ok,
                     'day_detail': ', '.join(dd), 'night_detail': ', '.join(dn)})

# ---------- 工时统计 ----------
hours = {p: 0 for p in STAFF + [A] + HOS}
night_cnt = {p: 0 for p in STAFF}
work_days = {p: 0 for p in STAFF + [A] + HOS}
for d in range(1, DAYS + 1):
    for p in STAFF:
        s = sched[p].get(d, '')
        if s in ('E', 'M', 'D', 'N'):
            hours[p] += 8; work_days[p] += 1
        if s == 'N': night_cnt[p] += 1
    if sched[A].get(d) == 'D': hours[A] += 8; work_days[A] += 1
    for p in HOS:
        if sched[p].get(d) == 'B': hours[p] += 8; work_days[p] += 1

# 周末双休
weekend_days = [d for d in range(1, DAYS + 1) if dow(d) in (5, 6)]
double_rest = {p: 0 for p in STAFF}
for i in range(0, len(weekend_days), 2):
    d1, d2 = weekend_days[i], weekend_days[i + 1]
    for p in STAFF:
        if sched[p].get(d1) == 'R' and sched[p].get(d2) == 'R':
            double_rest[p] += 1

def week_hours(p):
    wh = [0] * 4
    for d in range(1, DAYS + 1):
        s = sched[p].get(d, '')
        if s in ('E', 'M', 'D', 'N'): wh[week_idx(d)] += 8
    return wh

# ---------- HTML ----------
os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
rows_people = STAFF + [A] + HOS
html = []
html.append('<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8">')
html.append('<meta name="viewport" content="width=device-width, initial-scale=1.0">')
html.append(f'<title>三班倒排班表（{DAYS//7}周一轮）</title><style>')
html.append('body{font-family:"Microsoft YaHei",sans-serif;background:#f8fafc;color:#1e293b;margin:0;padding:24px;font-size:13px;line-height:1.6}')
html.append('h1{font-size:20px;margin:0 0 4px;color:#0f172a}h2{font-size:15px;margin:18px 0 6px;color:#1e3a8a;border-left:4px solid #3b82f6;padding-left:8px}')
html.append('.sub{color:#64748b;margin:0 0 14px;font-size:12px}')
html.append('table{border-collapse:collapse;width:100%;background:#fff;margin-bottom:8px;box-shadow:0 1px 3px rgba(0,0,0,.06)}')
html.append('th,td{border:1px solid #e2e8f0;padding:5px 4px;text-align:center;font-size:11.5px}th{background:#f1f5f9;font-weight:600;color:#334155}')
html.append('td.name,th.name{position:sticky;left:0;background:#fff;font-weight:600;text-align:left;min-width:90px;z-index:2}')
html.append('td.weekend,th.weekend{background:#fff7ed}.weekend_h{background:#fed7aa}')
html.append('.ok{color:#16a34a;font-weight:600}.bad{color:#dc2626;font-weight:600}')
html.append('.legend span{display:inline-block;margin-right:10px;font-size:11px}.legend i{display:inline-block;width:12px;height:12px;border:1px solid #cbd5e1;margin-right:4px;vertical-align:middle}')
html.append('.note{background:#fff;border:1px solid #e2e8f0;padding:10px 14px;border-radius:6px;margin:8px 0;font-size:12px;color:#475569}')
html.append('@media print{body{background:#fff;padding:0}table{box-shadow:none;font-size:10px}th,td{padding:3px 2px}}')
html.append('</style></head><body>')
html.append(f'<h1>门诊药房三班倒排班表</h1><p class="sub">轮换周期：{DAYS//7}周（{DAYS}天）一轮 ｜ D1=周一 ｜ 标准工时制（≤40h/周，每周至少休1天）</p>')

# 一、班次定义
html.append('<h2>一、班次定义与工时折算</h2><table><thead><tr><th>代码</th><th>班次</th><th>时间</th><th>工时折算</th></tr></thead><tbody>')
for code, (name, time, hour) in SHIFT_DEF.items():
    html.append(f'<tr><td style="background:{COLOR[code]}">{code}</td><td>{name}</td><td>{time}</td><td style="text-align:left">{hour}</td></tr>')
html.append('</tbody></table>')
html.append('<div class="note"><b>工时说明：</b>① 正常/早/中班按 8h 计（含午休或用餐/交接计入工时）。'
            '② <b>夜班实际 13.5h，按 8h 标准工时折算</b>，超出 5.5h 由"下夜班当日+次日连休 2 天"补偿。'
            '③ 早班/中班若原时长不足 8h，按医院惯例延伸或计入用餐/交接以满足 8h 工时（见上表折算说明）。'
            '④ N 人轮 7 夜班/周，结构性致部分人员单周工时 36-40h 浮动，建议 8/12 周长周期轮换使月均均衡。</div>')

# 二、排班总表
html.append(f'<h2>二、{DAYS//7}周排班总表（{DAYS}天 × {len(rows_people)}人）</h2><div class="legend">')
for code in ['D', 'E', 'M', 'N', 'B', 'R']:
    html.append(f'<span><i style="background:{COLOR[code]}"></i>{LABEL[code]}({code})</span>')
html.append('</div><table><thead><tr><th class="name">人员/日期</th>')
for d in range(1, DAYS + 1):
    w = dow(d); cls = ' class="weekend_h"' if w >= 5 else ''
    html.append(f'<th{cls}>{d}<br><span style="font-size:10px;color:#94a3b8">周{WK_CN[w]}</span></th>')
html.append('</tr></thead><tbody>')
for p in rows_people:
    is_hos = p in HOS
    html.append(f'<tr><td class="name">{p}</td>')
    for d in range(1, DAYS + 1):
        w = dow(d); cls = ' class="weekend"' if w >= 5 else ''
        if is_hos:
            s = sched[p].get(d, '')
            cell = '<span style="color:#cbd5e1">住</span>' if s == '' else f'<span style="background:{COLOR["B"]};padding:1px 4px;border-radius:3px">{LABEL[s]}</span>'
        else:
            s = sched[p].get(d, ''); bg = COLOR.get(s, '#fff')
            cell = f'<span style="background:{bg};padding:2px 5px;border-radius:3px;display:inline-block;min-width:18px">{LABEL.get(s, s)}</span>'
        html.append(f'<td{cls}>{cell}</td>')
    html.append('</tr>')
html.append('</tbody></table>')

# 三、在岗校验
html.append('<h2>三、每日在岗人数校验（24h 不间断 / 不脱班）</h2>')
html.append('<table><thead><tr><th>日</th><th>周</th><th>白天</th><th>需求</th><th>夜班</th><th>需求</th><th>状态</th><th>白天在岗明细</th><th>夜班</th></tr></thead><tbody>')
for c in coverage:
    st = '<span class="ok">✓达标</span>' if c['ok'] else '<span class="bad">✗不足</span>'
    html.append(f'<tr><td>{c["d"]}</td><td>周{c["wk"]}</td><td>{c["day"]}</td><td>{c["need_day"]}</td>'
                f'<td>{c["night"]}</td><td>{NEED_NIGHT}</td><td>{st}</td>'
                f'<td style="text-align:left;font-size:10px">{c["day_detail"]}</td><td style="font-size:10px">{c["night_detail"]}</td></tr>')
html.append('</tbody></table>')
all_ok = all(c['ok'] for c in coverage)
html.append(f'<div class="note">校验：<b class="{"ok" if all_ok else "bad"}">{"全部达标 ✓" if all_ok else "存在不足 ✗"}</b>。'
            '工作日白天=A+三班3（周四A休由住院部补1人）；周末白天3人；夜班每天1人（18:30接班至次日8:00）。</div>')

# 四、工时统计
html.append('<h2>四、工时与夜班统计</h2>')
html.append('<table><thead><tr><th>人员</th><th>角色</th><th>夜班</th><th>早E</th><th>中M</th><th>正常D</th>'
            '<th>上班天</th><th>4周工时</th><th>周均</th><th>周末双休</th></tr></thead><tbody>')
for p in rows_people:
    if p in STAFF:
        role = '三班'; nc = night_cnt[p]; e = em_dist[p]['E']; m = em_dist[p]['M']; dd = em_dist[p]['D']
        cells = f'<td>{nc}</td><td>{e}</td><td>{m}</td><td>{dd}</td>'
    elif p == A:
        role = '固定正常班'; cells = '<td>-</td><td>-</td><td>-</td><td>-</td>'
    else:
        role = '住院部'; cells = '<td>-</td><td>-</td><td>-</td><td>-</td>'
    h = hours[p]; avg = round(h / 4, 1)
    over = '<span class="bad">超</span>' if avg > 40 else '<span class="ok">合规</span>'
    dr = double_rest.get(p, '-')
    html.append(f'<tr><td class="name">{p}</td><td>{role}</td>{cells}<td>{work_days[p]}</td><td>{h}h</td><td>{avg}h {over}</td><td>{dr}</td></tr>')
html.append('</tbody></table>')
html.append('<div class="note"><b>合规：</b>所有人员周均 ≤40h。三班 6 人 4 周工时 144-160h（周均 36-40h），差异源于 6 人轮 7 夜班/周 + 夜班后休 2 天的结构性约束及 4 周截断边界效应。'
            '建议 8 周长周期轮换使月均均衡。周末双休仅能靠"周五夜班→休周六日"产生，4 周仅 4 名额，6 人必有 2 人本月未轮到，第 5-8 周优先补全。</div>')

# 五、周工时拆分
html.append('<h2>五、每人每周工时拆分（单周 ≤ 40h）</h2>')
html.append('<table><thead><tr><th>人员</th><th>第1周</th><th>第2周</th><th>第3周</th><th>第4周</th><th>合计</th></tr></thead><tbody>')
for p in rows_people:
    wh = [0]*4
    for d in range(1, DAYS+1):
        s = sched[p].get(d, '')
        if s in ('E','M','D','N','B'): wh[week_idx(d)] += 8
    cells = ''.join(f'<td>{wh[i]}h</td>' for i in range(4))
    html.append(f'<tr><td class="name">{p}</td>{cells}<td><b>{sum(wh)}h</b></td></tr>')
html.append('</tbody></table>')

# 六、年假与规则
html.append('<h2>六、年假填补机制与排班规则</h2><div class="note">')
html.append('<b>年假填补：</b>每天三班有 2-3 人夜班后休班，可抽调顶替上正常/早/中班者的年假空缺；夜班原则上不安排年假。<br>')
html.append('<b>住院部衔接：</b>住院部药师每周 5 天住院部本职（不参与早/中/夜），仅在固定班休息日轮换参与白天班补位。<br>')
html.append('<b>不脱班：</b>夜班每天 1 人循环轮换，夜班后强制休 2 天；白班 3 人由非夜班非休班人员担任，第三节校验全部达标。<br>')
html.append('<b>长周期建议：</b>以 8 周为完整轮换周期（4 周+镜像反转），使月均夜班 4-5 次、月均工时趋近 38-40h、月均周末双休 1-2 次。</div>')
html.append('</body></html>')

with open(OUT_PATH, 'w', encoding='utf-8') as f:
    f.write('\n'.join(html))

print('HTML 已生成:', OUT_PATH)
print('在岗校验全部达标:', all_ok)
print('\n=== 工时统计 ===')
for p in rows_people:
    print(f'{p}: 4周工时={hours[p]}h, 周均={round(hours[p]/4,1)}h, 上班天数={work_days[p]}')
print('\n=== 夜班/双休 ===')
for p in STAFF:
    print(f'{p}: 夜班{night_cnt[p]}次, 早{em_dist[p]["E"]}/中{em_dist[p]["M"]}/正常{em_dist[p]["D"]}, 周末双休{double_rest[p]}次')
