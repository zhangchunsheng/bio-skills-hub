#!/usr/bin/env python3
"""
临床数据清洗工具
清洗并标准化原始临床试验数据以符合 SDTM 规范。

用法：
    python main.py --input <file> --domain <DM|LB|VS> --output <file>
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
import warnings

import pandas as pd
import numpy as np

# 尝试导入 scipy，如果不可用则回退到 numpy
try:
    from scipy import stats
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False
    stats = None

warnings.filterwarnings('ignore')


class ClinicalDataCleaner:
    """用于清洗临床试验数据的主类。"""

    # SDTM 领域必需字段
    DOMAIN_FIELDS = {
        'DM': ['STUDYID', 'USUBJID', 'SUBJID', 'RFSTDTC', 'RFENDTC', 'SITEID', 'AGE', 'SEX', 'RACE'],
        'LB': ['STUDYID', 'USUBJID', 'LBTESTCD', 'LBCAT', 'LBORRES', 'LBORRESU', 'LBSTRESC', 'LBDTC'],
        'VS': ['STUDYID', 'USUBJID', 'VSTESTCD', 'VSORRES', 'VSORRESU', 'VSSTRESC', 'VSDTC']
    }

    # 临床参数的标准异常值阈值
    OUTLIER_THRESHOLDS = {
        'LB': {
            'GLUC': {'min': 50, 'max': 500, 'unit': 'mg/dL'},
            'HGB': {'min': 5, 'max': 20, 'unit': 'g/dL'},
            'WBC': {'min': 1000, 'max': 50000, 'unit': 'cells/uL'},
            'PLAT': {'min': 20000, 'max': 1000000, 'unit': 'cells/uL'},
            'CREAT': {'min': 0.3, 'max': 15, 'unit': 'mg/dL'},
            'ALT': {'min': 5, 'max': 500, 'unit': 'U/L'},
            'AST': {'min': 5, 'max': 500, 'unit': 'U/L'},
        },
        'VS': {
            'SYSBP': {'min': 70, 'max': 220, 'unit': 'mmHg'},
            'DIABP': {'min': 40, 'max': 140, 'unit': 'mmHg'},
            'PULSE': {'min': 40, 'max': 180, 'unit': 'beats/min'},
            'TEMP': {'min': 94, 'max': 108, 'unit': 'F'},
            'WEIGHT': {'min': 50, 'max': 500, 'unit': 'kg'},
            'HEIGHT': {'min': 100, 'max': 250, 'unit': 'cm'},
        }
    }

    def __init__(self, domain: str, missing_strategy: str = 'median',
                 outlier_method: str = 'iqr', outlier_action: str = 'flag',
                 config_path: Optional[str] = None):
        """
        初始化清洗器。

        Args:
            domain: SDTM 领域（DM、LB、VS）
            missing_strategy: 缺失值处理方式
            outlier_method: 异常值检测方法
            outlier_action: 异常值处理方式
            config_path: 自定义配置文件的路径
        """
        self.domain = domain.upper()
        self.missing_strategy = missing_strategy
        self.outlier_method = outlier_method
        self.outlier_action = outlier_action
        self.config = self._load_config(config_path)
        self.cleaning_log = []

    def _load_config(self, config_path: Optional[str]) -> Dict:
        """如果提供了自定义配置，则加载它。"""
        if config_path and Path(config_path).exists():
            with open(config_path, 'r') as f:
                return json.load(f)
        return {}

    def load_data(self, input_path: str) -> pd.DataFrame:
        """从 CSV 或 Excel 文件加载数据。"""
        path = Path(input_path)
        if not path.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")

        if path.suffix.lower() == '.csv':
            return pd.read_csv(input_path)
        elif path.suffix.lower() in ['.xlsx', '.xls']:
            return pd.read_excel(input_path)
        else:
            raise ValueError(f"Unsupported file format: {path.suffix}")

    def validate_domain(self, df: pd.DataFrame) -> Tuple[bool, List[str]]:
        """
        验证是否存在所有必需的 SDTM 字段。

        Returns:
            (is_valid, missing_fields) 元组
        """
        required = set(self.DOMAIN_FIELDS.get(self.domain, []))
        available = set(df.columns)
        missing = list(required - available)

        return len(missing) == 0, missing

    def handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        根据策略处理缺失值。

        策略：
        - drop: 删除包含任何缺失值的行
        - mean: 使用均值填补（仅数值型）
        - median: 使用中位数填补（仅数值型）
        - mode: 使用众数填补
        - forward: 向前填充
        """
        df_clean = df.copy()
        numeric_cols = df_clean.select_dtypes(include=[np.number]).columns

        missing_before = df_clean.isnull().sum().sum()

        if self.missing_strategy == 'drop':
            df_clean = df_clean.dropna()
        elif self.missing_strategy == 'mean':
            for col in numeric_cols:
                if df_clean[col].isnull().any():
                    mean_val = df_clean[col].mean()
                    df_clean[col] = df_clean[col].fillna(mean_val)
                    self.cleaning_log.append({
                        'action': 'impute_mean',
                        'column': col,
                        'value': mean_val,
                        'timestamp': datetime.now().isoformat()
                    })
        elif self.missing_strategy == 'median':
            for col in numeric_cols:
                if df_clean[col].isnull().any():
                    median_val = df_clean[col].median()
                    df_clean[col] = df_clean[col].fillna(median_val)
                    self.cleaning_log.append({
                        'action': 'impute_median',
                        'column': col,
                        'value': median_val,
                        'timestamp': datetime.now().isoformat()
                    })
        elif self.missing_strategy == 'mode':
            for col in df_clean.columns:
                if df_clean[col].isnull().any():
                    mode_val = df_clean[col].mode()
                    if len(mode_val) > 0:
                        df_clean[col] = df_clean[col].fillna(mode_val[0])
                        self.cleaning_log.append({
                            'action': 'impute_mode',
                            'column': col,
                            'value': mode_val[0],
                            'timestamp': datetime.now().isoformat()
                        })
        elif self.missing_strategy == 'forward':
            df_clean = df_clean.fillna(method='ffill')
            self.cleaning_log.append({
                'action': 'forward_fill',
                'columns': list(df_clean.columns),
                'timestamp': datetime.now().isoformat()
            })

        missing_after = df_clean.isnull().sum().sum()
        print(f"Missing values: {missing_before} → {missing_after}")

        return df_clean

    def detect_outliers(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        使用指定方法检测异常值。

        方法：
        - iqr: 四分位距法
        - zscore: Z 分数法（|z| > 3）
        - domain: 领域特定的临床阈值
        """
        df_flagged = df.copy()
        outlier_col = f"{self.domain}_OUTLIER_FLAG"
        df_flagged[outlier_col] = 0

        numeric_cols = df.select_dtypes(include=[np.number]).columns

        outlier_count = 0

        for col in numeric_cols:
            if col in ['STUDYID', 'USUBJID', 'SUBJID']:
                continue

            outliers = pd.Series([False] * len(df))

            if self.outlier_method == 'iqr':
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower = Q1 - 1.5 * IQR
                upper = Q3 + 1.5 * IQR
                outliers = (df[col] < lower) | (df[col] > upper)

            elif self.outlier_method == 'zscore':
                # 手动计算 z 分数，或使用 scipy
                col_data = df[col].dropna()
                if len(col_data) > 1:
                    mean_val = col_data.mean()
                    std_val = col_data.std()
                    if std_val > 0:
                        z_scores = np.abs((df[col] - mean_val) / std_val)
                        outliers = z_scores > 3

            elif self.outlier_method == 'domain':
                # 检查领域特定的阈值
                test_code_col = f"{self.domain}TESTCD"
                if test_code_col in df.columns and self.domain in self.OUTLIER_THRESHOLDS:
                    thresholds = self.OUTLIER_THRESHOLDS[self.domain]
                    for test_code, limits in thresholds.items():
                        mask = df[test_code_col] == test_code
                        if col.endswith('ORRES') or col.endswith('STRESC'):
                            val_outliers = (df[col] < limits['min']) | (df[col] > limits['max'])
                            outliers = outliers | (mask & val_outliers)

            outlier_count += outliers.sum()
            df_flagged.loc[outliers, outlier_col] = 1

            if outliers.any():
                self.cleaning_log.append({
                    'action': 'outlier_detected',
                    'column': col,
                    'method': self.outlier_method,
                    'count': int(outliers.sum()),
                    'timestamp': datetime.now().isoformat()
                })

        print(f"Outliers detected: {outlier_count}")
        return df_flagged

    def handle_outliers(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        根据处理策略处理异常值。

        操作：
        - flag: 仅标记（在检测阶段已完成）
        - remove: 删除异常值所在行
        - cap: 将数值限制在阈值范围内
        """
        outlier_col = f"{self.domain}_OUTLIER_FLAG"

        if self.outlier_action == 'flag':
            return df
        elif self.outlier_action == 'remove':
            if outlier_col in df.columns:
                before = len(df)
                df_clean = df[df[outlier_col] == 0].copy()
                after = len(df_clean)
                removed = before - after
                print(f"Removed {removed} outlier rows")
                self.cleaning_log.append({
                    'action': 'remove_outliers',
                    'rows_removed': removed,
                    'timestamp': datetime.now().isoformat()
                })
                return df_clean
        elif self.outlier_action == 'cap':
            # 限制在第 1 和第 99 百分位数之间
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            for col in numeric_cols:
                if col not in ['STUDYID', 'USUBJID', outlier_col]:
                    lower = df[col].quantile(0.01)
                    upper = df[col].quantile(0.99)
                    df[col] = df[col].clip(lower, upper)
            self.cleaning_log.append({
                'action': 'cap_outliers',
                'timestamp': datetime.now().isoformat()
            })
            return df

        return df

    def standardize_dates(self, df: pd.DataFrame) -> pd.DataFrame:
        """将日期格式统一为 ISO 8601。"""
        df_clean = df.copy()
        date_cols = [col for col in df.columns if 'DTC' in col or 'DT' in col]

        for col in date_cols:
            if col in df_clean.columns:
                try:
                    df_clean[col] = pd.to_datetime(df_clean[col], errors='coerce')
                    df_clean[col] = df_clean[col].dt.strftime('%Y-%m-%dT%H:%M:%S')
                    self.cleaning_log.append({
                        'action': 'standardize_date',
                        'column': col,
                        'timestamp': datetime.now().isoformat()
                    })
                except Exception as e:
                    print(f"Warning: Could not standardize {col}: {e}")

        return df_clean

    def clean(self, df: pd.DataFrame) -> pd.DataFrame:
        """执行完整的清洗流程。"""
        print(f"\n{'='*60}")
        print(f"Clinical Data Cleaner - {self.domain} Domain")
        print(f"{'='*60}")
        print(f"Input rows: {len(df)}")
        print(f"Input columns: {len(df.columns)}")

        # 验证领域
        is_valid, missing_fields = self.validate_domain(df)
        if not is_valid:
            print(f"\nWarning: Missing required fields: {missing_fields}")
            print("Continuing with available fields...")

        # 步骤 1：处理缺失值
        print(f"\n[Step 1] Handling missing values (strategy: {self.missing_strategy})")
        df = self.handle_missing_values(df)

        # 步骤 2：检测异常值
        print(f"\n[Step 2] Detecting outliers (method: {self.outlier_method})")
        df = self.detect_outliers(df)

        # 步骤 3：处理异常值
        print(f"\n[Step 3] Handling outliers (action: {self.outlier_action})")
        df = self.handle_outliers(df)

        # 步骤 4：统一日期格式
        print(f"\n[Step 4] Standardizing dates")
        df = self.standardize_dates(df)

        print(f"\n{'='*60}")
        print(f"Output rows: {len(df)}")
        print(f"Cleaning actions logged: {len(self.cleaning_log)}")
        print(f"{'='*60}\n")

        return df

    def save_report(self, output_path: str):
        """将清洗报告保存为 JSON。"""
        report = {
            'domain': self.domain,
            'timestamp': datetime.now().isoformat(),
            'parameters': {
                'missing_strategy': self.missing_strategy,
                'outlier_method': self.outlier_method,
                'outlier_action': self.outlier_action
            },
            'actions': self.cleaning_log
        }

        report_path = Path(output_path).with_suffix('.report.json')
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"Cleaning report saved: {report_path}")


def main():
    parser = argparse.ArgumentParser(
        description='Clean and standardize clinical trial data for SDTM compliance'
    )
    parser.add_argument('--input', '-i', required=True, help='Input data file (CSV/Excel)')
    parser.add_argument('--domain', '-d', required=True, choices=['DM', 'LB', 'VS'],
                        help='SDTM domain')
    parser.add_argument('--output', '-o', required=True, help='Output file path')
    parser.add_argument('--missing-strategy', default='median',
                        choices=['drop', 'mean', 'median', 'mode', 'forward'],
                        help='Missing value handling strategy')
    parser.add_argument('--outlier-method', default='iqr',
                        choices=['iqr', 'zscore', 'domain'],
                        help='Outlier detection method')
    parser.add_argument('--outlier-action', default='flag',
                        choices=['flag', 'remove', 'cap'],
                        help='Outlier handling action')
    parser.add_argument('--config', '-c', help='Custom configuration JSON file')

    args = parser.parse_args()

    # 初始化清洗器
    cleaner = ClinicalDataCleaner(
        domain=args.domain,
        missing_strategy=args.missing_strategy,
        outlier_method=args.outlier_method,
        outlier_action=args.outlier_action,
        config_path=args.config
    )

    # 加载数据
    df = cleaner.load_data(args.input)

    # 清洗数据
    df_cleaned = cleaner.clean(df)

    # 保存输出
    output_path = Path(args.output)
    if output_path.suffix.lower() == '.csv':
        df_cleaned.to_csv(args.output, index=False)
    elif output_path.suffix.lower() in ['.xlsx', '.xls']:
        df_cleaned.to_excel(args.output, index=False)
    else:
        # 默认使用 CSV
        df_cleaned.to_csv(args.output, index=False)

    print(f"Cleaned data saved: {args.output}")

    # 保存报告
    cleaner.save_report(args.output)


if __name__ == '__main__':
    main()
