# -*- coding: utf-8 -*-
"""
工业质检数据审核脚本
用法: python audit.py <输入目录> <输出目录>
"""
import pandas as pd
import numpy as np
import re
import os
import sys

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

# 默认合理物理范围（当标准要求列为空时使用）
DEFAULT_RANGES = {
    '抗拉强度':       (450, 650),
    '屈服强度':       (280, 450),
    '延伸率':         (15,  35),
    '断面收缩率':     (45,  70),
    '冲击功(常温)':   (20,  50),
    '冲击功':         (20,  50),
    '布氏硬度':       (140, 220),
    '布氏硬度(HRB)':  (140, 220),
    '化学成分-C含量':  (0.12, 0.25),
    '化学成分-S含量':  (None, 0.035),
}

# 样式
RED_FILL = PatternFill(start_color="FFCCCC", end_color="FFCCCC", fill_type="solid")
RED_FONT = Font(color="FF0000", bold=True)
HEADER_FILL = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
HEADER_FONT = Font(color="FFFFFF", bold=True, size=11)
SUMMARY_FILL = PatternFill(start_color="2F5496", end_color="2F5496", fill_type="solid")
SUMMARY_FONT = Font(color="FFFFFF", bold=True, size=12)
BLUE_FILL = PatternFill(start_color="D6E4F0", end_color="D6E4F0", fill_type="solid")
NORMAL_FONT = Font(size=10)
BORDER_THIN = Border(
    left=Side(style='thin'), right=Side(style='thin'),
    top=Side(style='thin'), bottom=Side(style='thin')
)

# 列位置（产品编号、检测项目、检测标准、实测值、标准要求、单位、偏差率、判定结果、检测日期、测试员）
IDX_PRODUCT, IDX_ITEM, IDX_STANDARD = 0, 1, 2
IDX_VALUE, IDX_REQUIREMENT, IDX_UNIT = 3, 4, 5
IDX_DEVIATION, IDX_RESULT, IDX_DATE, IDX_TESTER = 6, 7, 8, 9


def load_excel(filepath):
    """加载Excel，智能跳过标题行和表头行"""
    df_raw = pd.read_excel(filepath, header=None)
    skip_rows = 0
    for check_idx in range(min(5, len(df_raw))):
        str_vals = [str(df_raw.iloc[check_idx, j]) for j in range(df_raw.shape[1])]
        first_col_has_chinese = bool(re.search(r'[\u4e00-\u9fff]', str_vals[0]))
        non_empty = sum(1 for v in str_vals if v.lower() not in ['nan', '', 'none'])
        chinese_count = sum(1 for v in str_vals if re.search(r'[\u4e00-\u9fff]', v))
        if non_empty == 0:
            skip_rows += 1; continue
        if non_empty <= 2 and first_col_has_chinese:
            skip_rows += 1; continue
        if first_col_has_chinese and chinese_count >= 3:
            skip_rows += 1; continue
        break
    result = df_raw.iloc[skip_rows:].reset_index(drop=True)
    result.columns = range(result.shape[1])
    return result


def find_header_row(filepath):
    """定位原始文件的中文表头行"""
    df_raw = pd.read_excel(filepath, header=None)
    for ri in range(min(3, len(df_raw))):
        str_vals = [str(df_raw.iloc[ri, j]) for j in range(df_raw.shape[1])]
        first_col_has_chinese = bool(re.search(r'[\u4e00-\u9fff]', str_vals[0]))
        chinese_count = sum(1 for v in str_vals if re.search(r'[\u4e00-\u9fff]', v))
        if first_col_has_chinese and chinese_count >= 3:
            return [str(h) if pd.notna(h) else f'列{i+1}' for i, h in enumerate(df_raw.iloc[ri])]
    return [f'列{i+1}' for i in range(df_raw.shape[1])]


def parse_range(req_str):
    """解析标准要求字符串，返回 (下限, 上限)"""
    req_str = str(req_str).strip().replace(' ', '')
    if not req_str or req_str.lower() in ['nan', 'none', '']:
        return None, None
    m = re.match(r'^([\d.]+)[~\-—]([\d.]+)$', req_str)
    if m: return float(m.group(1)), float(m.group(2))
    m = re.match(r'^[>=≥]\s*([\d.]+)$', req_str)
    if m: return float(m.group(1)), None
    m = re.match(r'^[<=≤]\s*([\d.]+)$', req_str)
    if m: return None, float(m.group(1))
    return None, None


def get_default_range(item_name):
    """根据检测项目名获取默认合理范围"""
    for key in sorted(DEFAULT_RANGES.keys(), key=len, reverse=True):
        if key in item_name or item_name in key:
            return DEFAULT_RANGES[key]
    return None, None


def format_cell(val):
    """格式化单元格值"""
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return ''
    if isinstance(val, float) and val == int(val):
        return int(val)
    return val


def inspect_data(input_dir, output_dir):
    """
    主函数：审查输入目录下所有Excel文件
    返回: [(文件名, 数据行数, 异常行数), ...]
    """
    excel_files = sorted([
        os.path.join(input_dir, f) for f in os.listdir(input_dir)
        if f.endswith(('.xlsx', '.xls', '.xlsm')) and not f.startswith('~$')
    ])

    if not excel_files:
        print("未找到Excel文件。")
        return []

    os.makedirs(output_dir, exist_ok=True)
    file_results = []

    for filepath in excel_files:
        filename = os.path.basename(filepath)
        print(f"审查: {filename}")

        df = load_excel(filepath)
        headers = find_header_row(filepath)[:10]

        # 逐行审查
        all_red_cells = {}  # {excel_row: set of col_indices}
        valid_rows = 0
        excel_row_num = 2

        for _, row in df.iterrows():
            product = str(row[IDX_PRODUCT])
            if not product or product.lower() == 'nan':
                excel_row_num += 1; continue
            if any(kw in product for kw in ['产品编号', '检测报告']):
                excel_row_num += 1; continue

            valid_rows += 1
            red_cells = check_row(row)

            if red_cells:
                all_red_cells[excel_row_num] = red_cells
                item = str(row[IDX_ITEM]).strip()
                cell_names = {0: '产品编号', 1: '检测项目', 2: '检测标准', 3: '实测值',
                              4: '标准要求', 5: '单位', 6: '偏差率', 7: '判定结果', 8: '检测日期', 9: '测试员'}
                red_names = [cell_names.get(c, str(c)) for c in sorted(red_cells)]
                print(f"  第{excel_row_num}行 [{product}] {item}: 标红 {', '.join(red_names)}")

            excel_row_num += 1

        unique_anomaly_rows = len(all_red_cells)
        file_results.append((filename, valid_rows, unique_anomaly_rows))

        # 生成单文件报告
        output_path = os.path.join(output_dir, f"质检报告_{filename}")
        generate_single_report(df, all_red_cells, filepath, output_path)

    # 生成汇总报告
    summary_path = os.path.join(output_dir, "质检汇总报告.xlsx")
    generate_summary_report(file_results, summary_path)

    print(f"\n完成: {len(file_results)}个文件审查完毕。")
    return file_results


def check_row(row):
    """
    审查单行数据
    返回: 需要标红的列索引集合
    """
    item_name = str(row[IDX_ITEM]).strip()
    req_str = str(row[IDX_REQUIREMENT]).strip()
    result_str = str(row[IDX_RESULT]).strip()
    dev_str = str(row[IDX_DEVIATION]).strip()

    try:
        value = float(row[IDX_VALUE])
    except (ValueError, TypeError):
        return set()

    red_cells = set()

    # 获取标准范围（优先标准要求列，其次默认合理范围）
    lower, upper = parse_range(req_str)
    if lower is None and upper is None:
        lower, upper = get_default_range(item_name)

    # 规则1: 实测值超出标准/合理范围 → 标红实测值列
    if (lower is not None and value < lower) or (upper is not None and value > upper):
        red_cells.add(IDX_VALUE)

    # 规则2: 不该为负/零的指标出现负值或零值 → 标红实测值列
    if ('延伸率' in item_name or '断面收缩率' in item_name) and value < 0:
        red_cells.add(IDX_VALUE)
    if '冲击功' in item_name and (value < 0 or value == 0):
        red_cells.add(IDX_VALUE)
    for kw in ['抗拉强度', '屈服强度', '硬度', '布氏硬度']:
        if kw in item_name and (value < 0 or value == 0):
            red_cells.add(IDX_VALUE)
            break

    # 规则3: 偏差率绝对值>100% → 标红偏差率列
    has_data_anomaly = len(red_cells) > 0
    if dev_str and dev_str.lower() != 'nan' and dev_str != '':
        try:
            dev_val = float(dev_str.replace('%', '').strip())
            if abs(dev_val) > 100:
                red_cells.add(IDX_DEVIATION)
                has_data_anomaly = True
        except:
            pass

    # 规则4: 数据异常但判定"合格" → 标红判定结果列
    is_qualified = ('合格' in result_str and '不' not in result_str)
    if has_data_anomaly and is_qualified:
        red_cells.add(IDX_RESULT)

    return red_cells


def generate_single_report(df, all_red_cells, raw_filepath, output_path):
    """生成单文件质检报告：仅标红问题单元格，无标题/汇总/异常列"""
    wb = Workbook()
    ws = wb.active
    ws.title = "质检审查报告"

    headers = find_header_row(raw_filepath)[:10]

    # 表头
    for ci, h in enumerate(headers, 1):
        cell = ws.cell(row=1, column=ci, value=str(h))
        cell.fill = HEADER_FILL; cell.font = HEADER_FONT
        cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
        cell.border = BORDER_THIN

    # 数据行
    excel_row = 2
    for _, row in df.iterrows():
        product = str(row[IDX_PRODUCT])
        if not product or product.lower() == 'nan':
            continue
        if any(kw in product for kw in ['产品编号', '检测报告']):
            continue

        red_cells = all_red_cells.get(excel_row, set())

        for ci in range(10):
            val = format_cell(row[ci])
            cell = ws.cell(row=excel_row, column=ci + 1, value=val)
            cell.border = BORDER_THIN
            cell.alignment = Alignment(vertical='center', wrap_text=True)
            if ci in red_cells:
                cell.fill = RED_FILL; cell.font = RED_FONT
            else:
                cell.font = NORMAL_FONT

        excel_row += 1

    for ci, w in enumerate([18, 16, 14, 12, 24, 8, 12, 12, 14, 10], 1):
        ws.column_dimensions[get_column_letter(ci)].width = w

    wb.save(output_path)


def generate_summary_report(file_results, output_path):
    """生成汇总Excel（总体概况 + 文件级汇总）"""
    wb = Workbook()
    total_files = len(file_results)
    problem_files = sum(1 for r in file_results if r[2] > 0)
    total_rows = sum(r[1] for r in file_results)
    total_anomaly_rows = sum(r[2] for r in file_results)

    # Sheet 1: 总体概况
    ws1 = wb.active
    ws1.title = "总体概况"
    overview = [
        ('质检项目', '数值'),
        ('审查Excel文件总数', total_files),
        ('有问题的文件数', problem_files),
        ('正常文件数', total_files - problem_files),
        ('总数据行数', total_rows),
        ('总异常行数', total_anomaly_rows),
        ('整体合格率', f"{(1 - total_anomaly_rows / total_rows) * 100:.1f}%" if total_rows > 0 else "N/A"),
        ('', ''),
        ('审查标准说明', ''),
        ('规则1', '实测值超出标准/合理范围'),
        ('规则2', '不该为负数的指标出现负值或零值'),
        ('规则3', '偏差率绝对值超过100%'),
        ('规则4', '数据明显异常但判定结果为合格（判定矛盾）'),
        ('', ''),
        ('审查时间', pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')),
    ]
    for ri, (label, value) in enumerate(overview, 1):
        ca = ws1.cell(row=ri, column=1, value=label); cb = ws1.cell(row=ri, column=2, value=value)
        ca.border = BORDER_THIN; cb.border = BORDER_THIN
        if ri == 1:
            ca.fill = SUMMARY_FILL; ca.font = SUMMARY_FONT
            cb.fill = SUMMARY_FILL; cb.font = SUMMARY_FONT
        elif ri in [2, 9]:
            ca.font = Font(bold=True)
    ws1.column_dimensions['A'].width = 30
    ws1.column_dimensions['B'].width = 55

    # Sheet 2: 文件级汇总
    ws2 = wb.create_sheet("文件级汇总")
    fh = ['文件名', '总数据行数', '异常行数', '合格率', '状态']
    for ci, h in enumerate(fh, 1):
        cell = ws2.cell(row=1, column=ci, value=h)
        cell.fill = SUMMARY_FILL; cell.font = SUMMARY_FONT
        cell.alignment = Alignment(horizontal='center', vertical='center')
        cell.border = BORDER_THIN

    for ri, (fn, dr, ar) in enumerate(file_results, 2):
        pass_rate = f"{(1 - ar / dr) * 100:.1f}%" if dr > 0 else "N/A"
        status = "有问题" if ar > 0 else "正常"
        data = [fn, dr, ar, pass_rate, status]
        for ci, val in enumerate(data, 1):
            cell = ws2.cell(row=ri, column=ci, value=val)
            cell.border = BORDER_THIN; cell.alignment = Alignment(horizontal='center', vertical='center')
            cell.font = Font(color="FF0000", bold=True) if ar > 0 else NORMAL_FONT

    sr = len(file_results) + 2
    summary = ['总计', total_rows, total_anomaly_rows,
               f"{(1 - total_anomaly_rows / total_rows) * 100:.1f}%" if total_rows > 0 else "N/A",
               f"问题: {problem_files}/{total_files}"]
    for ci, val in enumerate(summary, 1):
        cell = ws2.cell(row=sr, column=ci, value=val)
        cell.font = Font(bold=True, size=11); cell.fill = BLUE_FILL
        cell.border = BORDER_THIN; cell.alignment = Alignment(horizontal='center', vertical='center')

    for ci, w in enumerate([35, 14, 12, 10, 15], 1):
        ws2.column_dimensions[get_column_letter(ci)].width = w

    wb.save(output_path)


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("用法: python audit.py <输入目录> <输出目录>")
        sys.exit(1)
    inspect_data(sys.argv[1], sys.argv[2])
