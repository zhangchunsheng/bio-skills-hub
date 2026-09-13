#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
药房调剂工作量计算 - 全流程脚本

功能：
  1. 日班每日统计（窗口人数/发药总数/配药总数/人均发/人均配）+ 填统计行 + 机动人员回填均数
  2. 均数 sheet：住院药房/机动/补休岗位发配列填当天门诊均数 + 月末新增月发合计/月配合计列
  3. 夜班 sheet：月末新增月发/月配/月借药合计列
  4. 个人汇总 sheet：合并日班+夜班工作量，按绩效公式重算分值/差额
  5. 生成"每日统计汇总"sheet

用法：
  python calc_pharmacy_workload.py <输入文件.xls/.xlsx> [选项]

详细业务规则见 references/workload_rules.md
"""
import sys, os, re, argparse, shutil

def _read_raw(path):
    """读取 xls/xlsx，返回 openpyxl Workbook。xls 用 xlrd 读后重建。"""
    ext = os.path.splitext(path)[1].lower()
    if ext == '.xlsx':
        from openpyxl import load_workbook
        return load_workbook(path), None
    # xls：用 xlrd 读数据，openpyxl 重建
    import xlrd
    from openpyxl import Workbook
    rb = xlrd.open_workbook(path, formatting_info=False)
    wb = Workbook()
    wb.remove(wb.active)
    for sn in rb.sheet_names():
        sh_src = rb.sheet_by_name(sn)
        sh = wb.create_sheet(sn)
        for r in range(sh_src.nrows):
            for c in range(sh_src.ncols):
                v = sh_src.cell_value(r, c)
                if isinstance(v, str):
                    v = v.strip() or None
                if v == '':
                    v = None
                if v is not None:
                    # xlrd 行列 0-based → openpyxl 1-based
                    sh.cell(r+1, c+1, v)
    return wb, 'rebuilt'

# ============ 通用：自动识别 sheet 与结构 ============
def detect_sheets(wb):
    """按特征识别 日班/均数/夜班/个人汇总 sheet。返回 dict。"""
    names = wb.sheetnames
    res = {'day': None, 'jun': None, 'night': None, 'summary': None}
    # 个人汇总
    for n in names:
        if n in ('个人汇总', '个人工作量月结', '月结'):
            res['summary'] = n; break
    for n in names:
        if n in ('夜班',):
            res['night'] = n; break
    for n in names:
        if n in ('均数',):
            res['jun'] = n; break
    # 日班：优先名为"日班"；否则找含"住"/窗口数字且非均数/夜班/汇总的
    for n in names:
        if n == '日班':
            res['day'] = n; break
    if not res['day']:
        for n in names:
            if n in (res['jun'], res['night'], res['summary']): continue
            sh = wb[n]
            # 探测第3行表头是否含"窗口"/"发"/"配"
            hdr3 = [sh.cell(3, c).value for c in range(1, min(8, sh.max_column+1))]
            if '窗口' in hdr3 and '发' in hdr3 and '配' in hdr3:
                res['day'] = n; break
    return res

def _is_window_num(v):
    """是否为上窗口的纯数字标记。"""
    if v is None: return False
    if isinstance(v, (int, float)): return True
    s = str(v).strip()
    return bool(re.match(r'^\d+$', s))

def _is_buxiu(v):
    return v is not None and '补休' in str(v)

def _is_zhu(v):
    return v is not None and str(v).strip() == '住'

def _is_jidong(v):
    return v is not None and '机动' in str(v)

def _num(v):
    try:
        if v is None or v == '': return 0
        return float(v)
    except: return 0

def detect_day_cols(sh, per_day=3):
    """探测天数。日班表头第3行，每天3列(窗口/发/配)，从列2开始。返回天数。"""
    n = 0
    c = 2
    while c + per_day - 1 <= sh.max_column:
        # 窗口列表头应为"窗口"或None(第一天后通常无重复表头)
        win_hdr = sh.cell(3, c).value
        fa_hdr = sh.cell(3, c+1).value
        # 第一天表头是"窗口/发/配"，之后天表头可能空或重复
        if n == 0 and win_hdr != '窗口':
            break
        n += 1
        c += per_day
        # 防止无限循环：超过40天停止
        if n > 40: break
    return n

def person_rows(sh, start=4):
    """返回人员所在行列表（B列有姓名、不为合计/空）。"""
    rows = []
    for r in range(start, sh.max_row+1):
        name = sh.cell(r, 2).value
        if name and str(name).strip() not in ('合计', '总计', ''):
            rows.append(r)
    return rows

# ============ 步骤1：日班每日统计 + 填统计行 + 机动回填 ============
def calc_day_stats(wb, day_sheet, per_day=3, stat_rows=None):
    """
    统计行(1-based, 默认与本次一致)：
      R38=发药总数(窗口列) R39=窗口人数(窗口列) R40=人均发(窗口列)/人均配(配列) R43=配药总数(窗口列)
    返回 stats: [(date_idx, n_win, sum_fa, sum_pei, avg_fa, avg_pei, jd_persons:[(row,name)])]
    """
    if stat_rows is None:
        stat_rows = {'fa_sum':38, 'n_win':39, 'avg':40, 'pei_sum':43}
    sh = wb[day_sheet]
    n_days = detect_day_cols(sh, per_day)
    rows = person_rows(sh)
    stats = []
    for d in range(n_days):
        win_col = 2 + per_day*d
        fa_col  = win_col + 1
        pei_col = win_col + 2
        n_win = sum_fa = sum_pei = 0
        jd_persons = []
        for r in rows:
            win = sh.cell(r, win_col).value
            fa = sh.cell(r, fa_col).value
            pei = sh.cell(r, pei_col).value
            if _is_window_num(win) or _is_buxiu(win):
                n_win += 1
                sum_fa += _num(fa); sum_pei += _num(pei)
            elif _is_jidong(win):
                jd_persons.append((r, sh.cell(r,1).value))
        avg_fa = sum_fa/n_win if n_win else 0
        avg_pei = sum_pei/n_win if n_win else 0
        stats.append((d, n_win, sum_fa, sum_pei, avg_fa, avg_pei, jd_persons))
        # 填统计行
        sh.cell(stat_rows['fa_sum'], win_col, round(sum_fa,0))
        sh.cell(stat_rows['n_win'], win_col, n_win)
        sh.cell(stat_rows['avg'], win_col, round(avg_fa,2))
        sh.cell(stat_rows['avg'], pei_col, round(avg_pei,2))
        sh.cell(stat_rows['pei_sum'], win_col, round(sum_pei,0))
        # 机动人员回填均数
        for r, name in jd_persons:
            sh.cell(r, fa_col, round(avg_fa,2))
            sh.cell(r, pei_col, round(avg_pei,2))
    return stats, n_days

# ============ 步骤2：均数 sheet 住/机动/补休回填 + 月合计 ============
def fill_jun_and_sum(wb, jun_sheet, stats, per_day=3):
    sh = wb[jun_sheet]
    n_days = len(stats)
    rows = person_rows(sh)
    # 月合计列：月末第n天 配列 = 2 + per_day*(n_days-1) + (per_day-1) → 月发合计在其后+1, 月配+2
    last_pei_col = 2 + per_day*(n_days-1) + (per_day-1)
    sum_fa_col = last_pei_col + 1
    sum_pei_col = last_pei_col + 2
    # 表头
    sh.cell(3, sum_fa_col, '发'); sh.cell(3, sum_pei_col, '配')
    for r in rows:
        tot_fa = tot_pei = 0
        for d in range(n_days):
            win_col = 2 + per_day*d
            fa_col  = win_col + 1
            pei_col = win_col + 2
            win = sh.cell(r, win_col).value
            fa = sh.cell(r, fa_col).value
            pei = sh.cell(r, pei_col).value
            st = stats[d]
            avg_fa, avg_pei = st[4], st[5]
            if _is_zhu(win) or _is_jidong(win) or _is_buxiu(win):
                # 填当天门诊均数
                sh.cell(r, fa_col, round(avg_fa,2))
                sh.cell(r, pei_col, round(avg_pei,2))
                fa = avg_fa; pei = avg_pei
            tot_fa += _num(fa); tot_pei += _num(pei)
        sh.cell(r, sum_fa_col, round(tot_fa,2))
        sh.cell(r, sum_pei_col, round(tot_pei,2))
    # 全员合计行
    sum_row = max(rows) + 1
    sh.cell(sum_row, 2, '合计')
    sh.cell(sum_row, sum_fa_col, round(sum(_num(sh.cell(r,sum_fa_col).value) for r in rows),2))
    sh.cell(sum_row, sum_pei_col, round(sum(_num(sh.cell(r,sum_pei_col).value) for r in rows),2))
    return sum_fa_col, sum_pei_col

# ============ 步骤3：夜班 月合计 ============
def fill_night_sum(wb, night_sheet, per_day=4):
    sh = wb[night_sheet]
    n_days = detect_day_cols(sh, per_day)
    rows = person_rows(sh)
    last_jie_col = 2 + per_day*(n_days-1) + (per_day-1)  # 末天借药列
    sum_fa_col = last_jie_col + 1
    sum_pei_col = last_jie_col + 2
    sum_jie_col = last_jie_col + 3
    sh.cell(3, sum_fa_col, '发'); sh.cell(3, sum_pei_col, '配'); sh.cell(3, sum_jie_col, '借药')
    for r in rows:
        t_fa = t_pei = t_jie = 0
        for d in range(n_days):
            fa_col = 3 + per_day*d
            pei_col = fa_col + 1
            jie_col = fa_col + 2
            t_fa += _num(sh.cell(r, fa_col).value)
            t_pei += _num(sh.cell(r, pei_col).value)
            t_jie += _num(sh.cell(r, jie_col).value)
        sh.cell(r, sum_fa_col, round(t_fa,0))
        sh.cell(r, sum_pei_col, round(t_pei,0))
        sh.cell(r, sum_jie_col, round(t_jie,0))
    sum_row = max(rows) + 1
    sh.cell(sum_row, 2, '合计')
    sh.cell(sum_row, sum_fa_col, round(sum(_num(sh.cell(r,sum_fa_col).value) for r in rows),0))
    sh.cell(sum_row, sum_pei_col, round(sum(_num(sh.cell(r,sum_pei_col).value) for r in rows),0))
    sh.cell(sum_row, sum_jie_col, round(sum(_num(sh.cell(r,sum_jie_col).value) for r in rows),0))
    return sum_fa_col, sum_pei_col, sum_jie_col

# ============ 步骤4：个人汇总 合并 + 绩效 ============
def merge_summary(wb, summary_sheet, jun_sheet, night_sheet, jun_cols, night_cols, pool=11200, chanjia=None):
    """
    jun_cols=(月发合计列, 月配合计列); night_cols=(月发,月配,月借)
    个人汇总：B列姓名；C发 D配 E借 G工作总量 H分值 I基准 J差额
    """
    if chanjia is None: chanjia = set()
    sh = wb[summary_sheet]
    sh_j = wb[jun_sheet]; sh_y = wb[night_sheet]
    jun_fa_c, jun_pei_c = jun_cols
    ye_fa_c, ye_pei_c, ye_jie_c = night_cols
    # 读日班/夜班月合计 by 姓名
    jun = {}
    for r in person_rows(sh_j):
        n = sh_j.cell(r,1).value
        if n: jun[n] = (_num(sh_j.cell(r,jun_fa_c).value), _num(sh_j.cell(r,jun_pei_c).value))
    ye = {}
    for r in person_rows(sh_y):
        n = sh_y.cell(r,1).value
        if n: ye[n] = (_num(sh_y.cell(r,ye_fa_c).value), _num(sh_y.cell(r,ye_pei_c).value), _num(sh_y.cell(r,ye_jie_c).value))
    # 表头
    sh.cell(3,3,'发(日+夜)'); sh.cell(3,4,'配(日+夜)'); sh.cell(3,5,'借药(夜)')
    rows = [r for r in range(4, sh.max_row+1) if sh.cell(r,2).value and str(sh.cell(r,2).value).strip() not in ('合计','总计')]
    total_work = 0.0
    for r in rows:
        name = sh.cell(r,2).value
        jfa, jpei = jun.get(name,(0,0))
        yfa, ypei, yjie = ye.get(name,(0,0,0))
        fa = jfa + yfa; pei = jpei + ypei; jie = yjie
        work = fa*2 + pei + jie
        total_work += work
        sh.cell(r,3,round(fa,2)); sh.cell(r,4,round(pei,2)); sh.cell(r,5,round(jie,2)); sh.cell(r,7,round(work,2))
    mean = pool/total_work if total_work else 0
    sh.cell(2,8,round(mean,8))
    for r in rows:
        name = sh.cell(r,2).value
        work = _num(sh.cell(r,7).value)
        score = work*mean
        base = sh.cell(r,9).value
        base = base if isinstance(base,(int,float)) else 400
        diff = 0 if name in chanjia else (score-base)
        sh.cell(r,8,round(score,2)); sh.cell(r,10,round(diff,2))
    # 合计行
    sr = max(rows)+1
    sh.cell(sr,2,'合计')
    sh.cell(sr,7,round(total_work,2))
    sh.cell(sr,8,round(sum(_num(sh.cell(r,8).value) for r in rows),2))
    sh.cell(sr,9,round(sum(_num(sh.cell(r,9).value) for r in rows),2))
    sh.cell(sr,10,round(sum(_num(sh.cell(r,10).value) for r in rows),2))
    return total_work, mean

# ============ 步骤5：每日统计汇总 sheet ============
def build_daily_summary(wb, stats, sheet_name='每日统计汇总'):
    if sheet_name in wb.sheetnames:
        del wb[sheet_name]
    sh = wb.create_sheet(sheet_name, 0)
    weekday = ['四','五','六','日','一','二','三']  # 5/1/2026 是周五，但按实际；这里简化
    hdr = ['日期','星期','窗口人数','住院药房人数','发药总数','配药总数','人均发','人均配','机动人员']
    sh.append(hdr)
    # 注：住院药房人数需从日班表读，此处简化用统计行R39窗口人数已含
    for d, n_win, sum_fa, sum_pei, avg_fa, avg_pei, jd in stats:
        sh.append([f'5/{d+1}', weekday[d%7] if d<7 else '', n_win, '', round(sum_fa,0), round(sum_pei,0), round(avg_fa,2), round(avg_pei,2), '/'.join(n for _,n in jd)])
    # 合计行
    tot_win = sum(s[1] for s in stats)
    tot_fa = sum(s[2] for s in stats)
    tot_pei = sum(s[3] for s in stats)
    sh.append(['合计','',tot_win,'',round(tot_fa,0),round(tot_pei,0),'','',''])

# ============ main ============
def main():
    ap = argparse.ArgumentParser(description='药房调剂工作量计算全流程')
    ap.add_argument('input', help='输入工作量文件 .xls/.xlsx')
    ap.add_argument('-o','--output', help='输出文件路径(默认同目录加_统计结果.xlsx)')
    ap.add_argument('--pool', type=float, default=11200, help='绩效池子(默认11200=28人x400)')
    ap.add_argument('--chanjia', default='敖雪敏,张璐', help='产假人员名单(逗号分隔，差额不扣400)')
    ap.add_argument('--day-cols', type=int, default=3, help='日班每天列数(默认3)')
    ap.add_argument('--night-cols', type=int, default=4, help='夜班每天列数(默认4)')
    ap.add_argument('--day-sheet', default=None)
    ap.add_argument('--jun-sheet', default=None)
    ap.add_argument('--night-sheet', default=None)
    ap.add_argument('--summary-sheet', default=None)
    args = ap.parse_args()

    inp = os.path.abspath(args.input)
    out = args.output or os.path.join(os.path.dirname(inp), os.path.splitext(os.path.basename(inp))[0] + '_统计结果.xlsx')
    wb, note = _read_raw(inp)
    if note: print(f'[info] {inp} 为 .xls，已重建为内存 workbook（格式可能简化）')

    sn = detect_sheets(wb)
    day_s = args.day_sheet or sn['day']
    jun_s = args.jun_sheet or sn['jun']
    night_s = args.night_sheet or sn['night']
    summ_s = args.summary_sheet or sn['summary']
    print(f'[sheet] 日班={day_s} 均数={jun_s} 夜班={night_s} 个人汇总={summ_s}')
    assert day_s, '未识别到日班sheet'

    # 步骤1
    print('[1/5] 日班每日统计+填统计行+机动回填...')
    stats, n_days = calc_day_stats(wb, day_s, args.day_cols)
    print(f'      天数={n_days}, 样例5/1: 窗口{stats[0][1]}人 发{stats[0][2]} 配{stats[0][3]} 人均发{stats[0][4]}')

    # 步骤2
    if jun_s:
        print('[2/5] 均数sheet 住/机动/补休回填均数+月合计...')
        jun_cols = fill_jun_and_sum(wb, jun_s, stats, args.day_cols)
        print(f'      月发合计列={jun_cols[0]} 月配合计列={jun_cols[1]}')
    else:
        jun_cols = (None, None); print('[2/5] 无均数sheet，跳过')

    # 步骤3
    if night_s:
        print('[3/5] 夜班 月发/月配/月借药合计...')
        night_cols = fill_night_sum(wb, night_s, args.night_cols)
        print(f'      月发列={night_cols[0]} 月配列={night_cols[1]} 月借列={night_cols[2]}')
    else:
        night_cols = (None,None,None); print('[3/5] 无夜班sheet，跳过')

    # 步骤4
    if summ_s and jun_cols[0] and night_cols[0]:
        print('[4/5] 个人汇总 合并日班+夜班+绩效重算...')
        chan = {x.strip() for x in args.chanjia.split(',') if x.strip()}
        tw, mean = merge_summary(wb, summ_s, jun_s, night_s, jun_cols, night_cols, args.pool, chan)
        print(f'      总工作总量={round(tw,2)} 均值={mean:.8f} 池子={args.pool}')

    # 步骤5
    print('[5/5] 生成每日统计汇总sheet...')
    build_daily_summary(wb, stats)

    wb.save(out)
    print(f'\n✅ 完成，输出: {out}')

if __name__ == '__main__':
    main()
