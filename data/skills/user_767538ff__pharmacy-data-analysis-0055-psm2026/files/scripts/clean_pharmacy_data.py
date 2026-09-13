#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
药事数据清洗脚本 (Pharmacy Data Cleaning Script)
==========================================
功能：对 Excel/CSV 格式的药事数据（调剂差错、盘点、前置审方）执行自动化检测，
      输出问题报告（不自动修改数据），供用户确认后再执行清洗。

使用方法：
    python clean_pharmacy_data.py <input_file> [--output-dir <dir>]

参数：
    input_file    : 输入数据文件路径（.xlsx / .csv / .xls）
    --output-dir  : 报告输出目录（默认与输入文件同目录）
    --data-type   : 数据类型提示（dispensing_error / inventory / prescription_review）
                    帮助脚本应用药事场景特定的检测规则

输出：
    1. 数据画像报告 (data_profile.txt)
    2. 问题检测报告 (issue_report.xlsx) — 含5个Sheet：重复行、缺失值、格式问题、异常值、字段一致性
    3. 清洗规则汇总 (cleaning_rules_summary.txt) — 列出规则编号、受影响行数、处置建议

依赖：
    pip install pandas openpyxl xlrd
"""

import os
import sys
import re
import argparse
from datetime import datetime, date
from collections import Counter

try:
    import pandas as pd
    import numpy as np
    from openpyxl import Workbook
    from openpyxl.utils.dataframe import dataframe_to_rows
except ImportError as e:
    print(f"缺少依赖库: {e}")
    print("请运行: pip install pandas openpyxl xlrd numpy")
    sys.exit(1)


# ============================================================
#  数据读取
# ============================================================

def read_data(filepath):
    """读取 Excel 或 CSV 文件，自动检测编码"""
    ext = os.path.splitext(filepath)[1].lower()

    if ext == '.csv':
        # 尝试多种编码
        for encoding in ['utf-8', 'gbk', 'gb18030', 'latin-1']:
            try:
                df = pd.read_csv(filepath, encoding=encoding)
                print(f"CSV 编码: {encoding}")
                break
            except (UnicodeDecodeError, Exception):
                continue
        else:
            raise ValueError("无法解码 CSV 文件，请检查文件编码")
    elif ext in ('.xlsx', '.xls'):
        df = pd.read_excel(filepath)
    else:
        raise ValueError(f"不支持的文件格式: {ext}，仅支持 .xlsx / .csv / .xls")

    return df


# ============================================================
#  数据画像
# ============================================================

def generate_profile(df, filepath):
    """生成数据画像报告"""
    lines = []
    lines.append("=" * 60)
    lines.append("数据画像报告 (Data Profile)")
    lines.append("=" * 60)
    lines.append(f"文件: {filepath}")
    lines.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"总行数: {len(df)}")
    lines.append(f"总列数: {len(df.columns)}")
    lines.append("")

    lines.append("-" * 60)
    lines.append("字段明细")
    lines.append("-" * 60)
    lines.append(f"{'序号':<5} {'字段名':<30} {'数据类型':<15} {'非空数':<10} {'缺失数':<10} {'缺失率':<10}")
    lines.append("-" * 60)

    for i, col in enumerate(df.columns, 1):
        non_null = df[col].notna().sum()
        null_count = df[col].isna().sum()
        null_rate = f"{null_count / len(df) * 100:.1f}%"
        dtype = str(df[col].dtype)
        lines.append(f"{i:<5} {str(col):<30} {dtype:<15} {non_null:<10} {null_count:<10} {null_rate:<10}")

    lines.append("")
    lines.append("-" * 60)
    lines.append("前5行预览")
    lines.append("-" * 60)
    preview = df.head().to_string()
    lines.append(preview)

    return "\n".join(lines)


# ============================================================
#  检测1: 重复行
# ============================================================

def detect_duplicates(df):
    """检测完全重复行和关键字段重复行"""
    issues = []

    # 完全重复
    full_dups = df.duplicated(keep='first')
    full_dup_count = full_dups.sum()
    if full_dup_count > 0:
        dup_rows = df[full_dups].index.tolist()
        issues.append({
            '规则编号': 'R-DUP-01',
            '问题类型': '完全重复行',
            '规则描述': '所有列值完全一致的行',
            '受影响行数': full_dup_count,
            '受影响行号': ', '.join(str(i + 2) for i in dup_rows[:20]),  # +2 for header + 1-based
            '处置建议': '删除重复行，保留首次出现',
            '严重程度': '中' if full_dup_count > 5 else '低'
        })

    # 关键字段重复（尝试识别可能的唯一标识列）
    potential_id_cols = [col for col in df.columns if any(
        keyword in str(col).lower() for keyword in ['编号', 'id', '序号', 'record', '处方号', '医嘱号']
    )]

    if potential_id_cols:
        for id_col in potential_id_cols:
            if df[id_col].notna().sum() > 0:
                key_dups = df.duplicated(subset=[id_col], keep=False)
                key_dup_count = key_dups.sum()
                if key_dup_count > 0:
                    dup_rows = df[key_dups].index.tolist()
                    issues.append({
                        '规则编号': 'R-DUP-02',
                        '问题类型': f'关键字段重复 [{id_col}]',
                        '规则描述': f'字段 [{id_col}] 存在重复值',
                        '受影响行数': key_dup_count,
                        '受影响行号': ', '.join(str(i + 2) for i in dup_rows[:20]),
                        '处置建议': '人工确认是否为独立记录',
                        '严重程度': '高'
                    })

    return pd.DataFrame(issues) if issues else pd.DataFrame(
        columns=['规则编号', '问题类型', '规则描述', '受影响行数', '受影响行号', '处置建议', '严重程度']
    )


# ============================================================
#  检测2: 缺失值
# ============================================================

# 药事关键字段（禁止自动填充）
KEY_FIELDS_PATTERNS = [
    '药品', 'drug', '规格', 'spec', '剂型', 'dosage_form',
    '批号', 'batch', '数量', 'quantity', '金额', 'amount',
    '差错', 'error', '等级', 'level', '类型', 'type',
    '处方', 'prescription', '医嘱', 'order', '用法', 'usage',
    '用量', 'dosage', '结论', 'result', '结论', 'review',
    '有效期', 'expiry', '效期'
]


def is_key_field(col_name):
    """判断是否为关键字段"""
    col_lower = str(col_name).lower()
    return any(pat in col_lower for pat in KEY_FIELDS_PATTERNS)


def detect_missing(df):
    """检测缺失值并分类"""
    issues = []

    for col in df.columns:
        null_count = df[col].isna().sum()
        if null_count == 0:
            continue

        null_rate = null_count / len(df) * 100
        is_key = is_key_field(col)

        if null_rate < 5:
            severity = '低'
            level = '轻微'
        elif null_rate < 20:
            severity = '中'
            level = '中度'
        else:
            severity = '高'
            level = '严重'

        if is_key:
            suggestion = '关键字段，不自动填充，待人工确认'
            rule_id = 'R-MIS-01'
        else:
            suggestion = '非关键字段，可用众数/中位数填充'
            rule_id = 'R-MIS-02'

        issues.append({
            '规则编号': rule_id,
            '字段名': str(col),
            '字段类型': '关键字段' if is_key else '非关键字段',
            '缺失数量': null_count,
            '缺失率': f"{null_rate:.1f}%",
            '缺失级别': level,
            '处置建议': suggestion,
            '严重程度': severity
        })

    return pd.DataFrame(issues) if issues else pd.DataFrame(
        columns=['规则编号', '字段名', '字段类型', '缺失数量', '缺失率', '缺失级别', '处置建议', '严重程度']
    )


# ============================================================
#  检测3: 日期与数字格式
# ============================================================

DATE_COL_PATTERNS = ['日期', 'date', '时间', 'time', '有效期', 'expiry', '效期']
NUM_COL_PATTERNS = ['数量', 'quantity', '金额', 'amount', '价格', 'price', '率', 'rate', 'age', '年龄']


def is_date_field(col_name):
    col_lower = str(col_name).lower()
    return any(pat in col_lower for pat in DATE_COL_PATTERNS)


def is_num_field(col_name):
    col_lower = str(col_name).lower()
    return any(pat in col_lower for pat in NUM_COL_PATTERNS)


def detect_format_issues(df):
    """检测日期和数字格式问题"""
    issues = []

    for col in df.columns:
        col_data = df[col].dropna()
        if col_data.empty:
            continue

        # 日期格式检测
        if is_date_field(col):
            # 检查是否存在文本型日期
            non_datetime = col_data.apply(
                lambda x: not isinstance(x, (datetime, date, pd.Timestamp))
                          and not pd.isna(x)
            )
            text_dates = col_data[non_datetime]

            if len(text_dates) > 0:
                # 检查日期格式多样性
                formats_found = set()
                for val in text_dates.head(50):
                    val_str = str(val).strip()
                    if re.match(r'\d{4}[-/]\d{1,2}[-/]\d{1,2}', val_str):
                        if '/' in val_str:
                            formats_found.add('YYYY/MM/DD')
                        else:
                            formats_found.add('YYYY-MM-DD')
                    elif re.match(r'\d{1,2}[-/]\d{1,2}[-/]\d{4}', val_str):
                        formats_found.add('DD/MM/YYYY 或 MM/DD/YYYY')
                    elif re.match(r'\d{4}年\d{1,2}月\d{1,2}日', val_str):
                        formats_found.add('中文日期')
                    elif re.match(r'^\d{5}$', val_str):
                        formats_found.add('Excel序列号')
                    else:
                        formats_found.add(f'其他: {val_str[:20]}')

                if len(formats_found) > 1:
                    issues.append({
                        '规则编号': 'R-FMT-01',
                        '字段名': str(col),
                        '问题类型': '日期格式不统一',
                        '问题描述': f'发现多种日期格式: {", ".join(formats_found)}',
                        '受影响行数': len(text_dates),
                        '处置建议': '统一为 YYYY-MM-DD 格式',
                        '严重程度': '中'
                    })
                elif len(text_dates) > 0 and len(formats_found) == 1:
                    issues.append({
                        '规则编号': 'R-FMT-02',
                        '字段名': str(col),
                        '问题类型': '日期存为文本',
                        '问题描述': f'文本型日期，格式: {", ".join(formats_found)}',
                        '受影响行数': len(text_dates),
                        '处置建议': '转换为日期类型并标准化为 YYYY-MM-DD',
                        '严重程度': '中'
                    })

        # 数字格式检测
        if is_num_field(col):
            # 检查数字是否存为文本
            text_nums = col_data.apply(
                lambda x: isinstance(x, str) and not pd.isna(x)
            )
            text_num_count = text_nums.sum()

            if text_num_count > 0:
                # 进一步分析文本型数字
                has_unit = False
                has_comma = False
                has_fullwidth = False
                has_scientific = False

                for val in col_data[text_nums].head(50):
                    val_str = str(val)
                    if re.search(r'[a-zA-Z\u4e00-\u9fff]+', val_str):
                        has_unit = True
                    if ',' in val_str:
                        has_comma = True
                    if any('\uff10' <= c <= '\uff19' for c in val_str):
                        has_fullwidth = True
                    if re.search(r'[eE][+\-]?\d', val_str):
                        has_scientific = True

                problems = []
                if has_unit:
                    problems.append('混入单位文字')
                if has_comma:
                    problems.append('千分位逗号')
                if has_fullwidth:
                    problems.append('全角数字')
                if has_scientific:
                    problems.append('科学计数法')

                issues.append({
                    '规则编号': 'R-FMT-03',
                    '字段名': str(col),
                    '问题类型': '数字存为文本',
                    '问题描述': f'文本型数字{"，含: " + "、".join(problems) if problems else ""}',
                    '受影响行数': text_num_count,
                    '处置建议': '提取纯数值部分，单位单独处理，全角转半角',
                    '严重程度': '中'
                })

    return pd.DataFrame(issues) if issues else pd.DataFrame(
        columns=['规则编号', '字段名', '问题类型', '问题描述', '受影响行数', '处置建议', '严重程度']
    )


# ============================================================
#  检测4: 异常值
# ============================================================

def detect_outliers(df):
    """检测数值异常和逻辑矛盾"""
    issues = []

    for col in df.columns:
        col_data = df[col]
        numeric_data = pd.to_numeric(col_data, errors='coerce').dropna()

        if numeric_data.empty or len(numeric_data) < 10:
            continue

        col_lower = str(col).lower()

        # 负值检测（数量、金额等不应为负）
        if any(kw in col_lower for kw in ['数量', 'quantity', '金额', 'amount', '价格', 'price']):
            negatives = numeric_data[numeric_data < 0]
            if len(negatives) > 0:
                issues.append({
                    '规则编号': 'R-OUT-01',
                    '字段名': str(col),
                    '问题类型': '负值异常',
                    '问题描述': f'发现 {len(negatives)} 个负值',
                    '受影响行数': len(negatives),
                    '受影响行号': ', '.join(str(i + 2) for i in negatives.index[:20]),
                    '处置建议': '人工确认负值是否合理（如盘点差异可能为负）',
                    '严重程度': '高'
                })

        # IQR 离群点检测
        q1 = numeric_data.quantile(0.25)
        q3 = numeric_data.quantile(0.75)
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr

        outliers = numeric_data[(numeric_data < lower_bound) | (numeric_data > upper_bound)]
        if len(outliers) > 0:
            issues.append({
                '规则编号': 'R-OUT-02',
                '字段名': str(col),
                '问题类型': '统计离群点 (IQR)',
                '问题描述': f'Q1={q1:.2f}, Q3={q3:.2f}, IQR={iqr:.2f}, 范围=[{lower_bound:.2f}, {upper_bound:.2f}]',
                '受影响行数': len(outliers),
                '受影响行号': ', '.join(str(i + 2) for i in outliers.index[:20]),
                '处置建议': '标记离群点，不自动删除，供人工判断',
                '严重程度': '中'
            })

    # 逻辑矛盾检测：日期列比较
    date_cols = [col for col in df.columns if is_date_field(col)]
    if len(date_cols) >= 2:
        for i in range(len(date_cols)):
            for j in range(i + 1, len(date_cols)):
                col1, col2 = date_cols[i], date_cols[j]
                d1 = pd.to_datetime(df[col1], errors='coerce')
                d2 = pd.to_datetime(df[col2], errors='coerce')

                # 检测结束<开始的逻辑矛盾
                # 尝试根据字段名判断先后关系
                col1_lower = str(col1).lower()
                col2_lower = str(col2).lower()

                # 如果col2看起来是"结束/发现/上报"而col1是"开始/发生"
                start_keywords = ['发生', 'start', '处方', '开具', 'open']
                end_keywords = ['发现', '结束', '上报', '完成', '审方', 'end', 'review', 'report', 'detect']

                col1_is_start = any(kw in col1_lower for kw in start_keywords)
                col2_is_end = any(kw in col2_lower for kw in end_keywords)

                if col1_is_start and col2_is_end:
                    invalid = d2 < d1
                    invalid_count = invalid.sum()
                    if invalid_count > 0:
                        issues.append({
                            '规则编号': 'R-OUT-03',
                            '字段名': f'{col1} vs {col2}',
                            '问题类型': '日期逻辑矛盾',
                            '问题描述': f'[{col2}] 早于 [{col1}]',
                            '受影响行数': invalid_count,
                            '受影响行号': ', '.join(str(i + 2) for i in df[invalid].index[:20]),
                            '处置建议': '人工确认日期记录是否错误',
                            '严重程度': '高'
                        })

    return pd.DataFrame(issues) if issues else pd.DataFrame(
        columns=['规则编号', '字段名', '问题类型', '问题描述', '受影响行数', '受影响行号', '处置建议', '严重程度']
    )


# ============================================================
#  检测5: 字段一致性
# ============================================================

def detect_consistency(df):
    """检测文本规范性和字段一致性"""
    issues = []

    for col in df.columns:
        col_data = df[col].dropna()
        if col_data.empty:
            continue

        # 仅检测字符串类型列
        str_data = col_data[col_data.apply(lambda x: isinstance(x, str))]
        if str_data.empty:
            continue

        # 首尾空格
        has_leading_trailing = str_data.apply(
            lambda x: x != x.strip() if isinstance(x, str) else False
        )
        space_count = has_leading_trailing.sum()
        if space_count > 0:
            issues.append({
                '规则编号': 'R-CON-01',
                '字段名': str(col),
                '问题类型': '首尾空格',
                '问题描述': f'{space_count} 个值含首尾空格',
                '受影响行数': space_count,
                '处置建议': '去除首尾空格',
                '严重程度': '低'
            })

        # 全角字符
        has_fullwidth = str_data.apply(
            lambda x: any('\uff10' <= c <= '\uff19' or '\uff21' <= c <= '\uff5a' or c == '\u3000' for c in x) if isinstance(x, str) else False
        )
        fullwidth_count = has_fullwidth.sum()
        if fullwidth_count > 0:
            issues.append({
                '规则编号': 'R-CON-02',
                '字段名': str(col),
                '问题类型': '全角字符',
                '问题描述': f'{fullwidth_count} 个值含全角数字/字母/空格',
                '受影响行数': fullwidth_count,
                '处置建议': '全角转半角',
                '严重程度': '低'
            })

        # 大小写不一致（对英文/拼音字段）
        unique_vals = str_data.unique()
        if len(unique_vals) <= 50:  # 仅对低基数字段检测
            lower_map = {}
            case_inconsistent = 0
            for val in unique_vals:
                val_lower = val.lower().strip()
                if val_lower != val:
                    case_inconsistent += 1

            if case_inconsistent > 0:
                # 检查是否存在仅大小写不同的"重复"
                lower_counter = Counter(str_data.str.lower().str.strip())
                case_dups = {k: v for k, v in lower_counter.items() if v > 1 and k != str_data.str.strip().iloc[0]}
                if case_dups:
                    issues.append({
                        '规则编号': 'R-CON-03',
                        '字段名': str(col),
                        '问题类型': '大小写不一致',
                        '问题描述': f'存在仅大小写不同的值: {list(case_dups.keys())[:5]}',
                        '受影响行数': sum(case_dups.values()),
                        '处置建议': '统一大小写规范',
                        '严重程度': '低'
                    })

        # 枚举值校验（对分类字段）
        enum_fields = {
            '差错类型': ['药品差错', '数量差错', '剂型差错', '规格差错', '标签差错',
                         '用法用量差错', '效期差错', '漏发差错', '重复发药'],
            '差错等级': ['轻微', '一般', '严重', '致命'],
            '差错环节': ['收方', '调配', '核对', '发药', '运输'],
            '审方结论': ['通过', '修改后通过', '驳回', '转人工审', '警示后通过'],
            '盘点类型': ['全盘', '抽盘', '日盘', '月盘', '季盘'],
            '药品分类': ['西药', '中成药', '中药饮片', '生物制品'],
            '患者性别': ['男', '女'],
            '是否高警示药品': ['是', '否'],
        }

        for enum_field, valid_values in enum_fields.items():
            if str(col).strip() == enum_field or str(col).strip() == enum_field.replace('差错', '差错'):
                invalid_vals = str_data[~str_data.isin(valid_values)]
                if len(invalid_vals) > 0:
                    unique_invalid = invalid_vals.unique()
                    issues.append({
                        '规则编号': 'R-CON-04',
                        '字段名': str(col),
                        '问题类型': '枚举值异常',
                        '问题描述': f'非法取值: {list(unique_invalid)[:10]}，合法值: {valid_values}',
                        '受影响行数': len(invalid_vals),
                        '处置建议': '人工确认并映射到合法枚举值',
                        '严重程度': '中'
                    })

    return pd.DataFrame(issues) if issues else pd.DataFrame(
        columns=['规则编号', '字段名', '问题类型', '问题描述', '受影响行数', '处置建议', '严重程度']
    )


# ============================================================
#  汇总报告
# ============================================================

def generate_summary(dup_df, mis_df, fmt_df, out_df, con_df):
    """生成清洗规则汇总"""
    lines = []
    lines.append("=" * 60)
    lines.append("清洗规则汇总 (Cleaning Rules Summary)")
    lines.append("=" * 60)
    lines.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")

    total_issues = 0
    total_affected = 0

    sections = [
        ("一、重复行检测", dup_df),
        ("二、缺失值检测", mis_df),
        ("三、日期与数字格式", fmt_df),
        ("四、异常值检测", out_df),
        ("五、字段一致性", con_df),
    ]

    for title, issue_df in sections:
        lines.append("-" * 60)
        lines.append(title)
        lines.append("-" * 60)

        if issue_df.empty:
            lines.append("  未检测到问题")
        else:
            for _, row in issue_df.iterrows():
                rule_id = row.get('规则编号', '')
                desc = row.get('问题描述', row.get('规则描述', row.get('问题类型', '')))
                affected = row.get('受影响行数', row.get('缺失数量', 0))
                suggestion = row.get('处置建议', '')
                severity = row.get('严重程度', '')

                lines.append(f"  [{rule_id}] {desc}")
                lines.append(f"    受影响: {affected} 行/个 | 严重程度: {severity}")
                lines.append(f"    建议: {suggestion}")
                lines.append("")

                total_issues += 1
                total_affected += int(affected) if isinstance(affected, (int, float)) else 0

        lines.append("")

    lines.append("=" * 60)
    lines.append(f"总计: {total_issues} 类问题，涉及约 {total_affected} 行/个数据点")
    lines.append("=" * 60)
    lines.append("")
    lines.append("请确认以上清洗方案。确认后将执行清洗并输出：")
    lines.append("  1. 清洗后数据文件 (cleaned_data.xlsx)")
    lines.append("  2. 修改日志 (modification_log.xlsx)")
    lines.append("  3. 无法处理项 (unresolved_items.xlsx)")

    return "\n".join(lines)


# ============================================================
#  主函数
# ============================================================

def main():
    parser = argparse.ArgumentParser(description='药事数据清洗检测脚本')
    parser.add_argument('input_file', help='输入数据文件路径 (.xlsx / .csv / .xls)')
    parser.add_argument('--output-dir', default=None, help='报告输出目录（默认与输入文件同目录）')
    parser.add_argument('--data-type', default=None,
                       choices=['dispensing_error', 'inventory', 'prescription_review'],
                       help='数据类型提示')

    args = parser.parse_args()

    # 验证输入文件
    if not os.path.exists(args.input_file):
        print(f"错误: 文件不存在 - {args.input_file}")
        sys.exit(1)

    # 设置输出目录
    output_dir = args.output_dir or os.path.dirname(os.path.abspath(args.input_file))
    os.makedirs(output_dir, exist_ok=True)

    # 读取数据
    print(f"正在读取文件: {args.input_file}")
    df = read_data(args.input_file)
    print(f"读取完成: {len(df)} 行 × {len(df.columns)} 列")

    # 生成数据画像
    print("正在生成数据画像...")
    profile = generate_profile(df, args.input_file)
    profile_path = os.path.join(output_dir, 'data_profile.txt')
    with open(profile_path, 'w', encoding='utf-8') as f:
        f.write(profile)
    print(f"数据画像已保存: {profile_path}")

    # 执行5维检测
    print("正在检测重复行...")
    dup_df = detect_duplicates(df)

    print("正在检测缺失值...")
    mis_df = detect_missing(df)

    print("正在检测格式问题...")
    fmt_df = detect_format_issues(df)

    print("正在检测异常值...")
    out_df = detect_outliers(df)

    print("正在检测字段一致性...")
    con_df = detect_consistency(df)

    # 输出问题报告 (Excel)
    print("正在生成问题检测报告...")
    report_path = os.path.join(output_dir, 'issue_report.xlsx')
    with pd.ExcelWriter(report_path, engine='openpyxl') as writer:
        dup_df.to_excel(writer, sheet_name='重复行', index=False)
        mis_df.to_excel(writer, sheet_name='缺失值', index=False)
        fmt_df.to_excel(writer, sheet_name='格式问题', index=False)
        out_df.to_excel(writer, sheet_name='异常值', index=False)
        con_df.to_excel(writer, sheet_name='字段一致性', index=False)
    print(f"问题检测报告已保存: {report_path}")

    # 输出清洗规则汇总
    print("正在生成清洗规则汇总...")
    summary = generate_summary(dup_df, mis_df, fmt_df, out_df, con_df)
    summary_path = os.path.join(output_dir, 'cleaning_rules_summary.txt')
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write(summary)
    print(f"清洗规则汇总已保存: {summary_path}")

    print("\n" + "=" * 60)
    print("检测完成！请查看以下文件：")
    print(f"  1. 数据画像: {profile_path}")
    print(f"  2. 问题报告: {report_path}")
    print(f"  3. 规则汇总: {summary_path}")
    print("=" * 60)
    print("\n请确认清洗方案后将执行清洗操作。")


if __name__ == '__main__':
    main()
