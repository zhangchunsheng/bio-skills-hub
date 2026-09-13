#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成中文脏表格测试样本。

覆盖真实职场表格最常见的坑：
  大标题占首行、合并单元格表头、数字存成文本、中文单位（万/亿/元）、
  百分号、中文日期、全角空格、合计行、备注行、GBK 编码 CSV。

用法: python make_samples.py [输出目录]
"""

import csv
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
import xlsx_lite as X


def build_dirty_xlsx(path):
    # 第 1 行是大标题（A1:F1 合并），第 2 行空，第 3 行才是真表头
    rows = [
        ["2026年第一季度销售明细表", None, None, None, None, None],
        [None, None, None, None, None, None],
        ["大区", "销售员", "销售额", "完成率", "签约日期", "客户数"],
        ["华东", "张三", "1.2万", "35%", "2026年1月5日", "12"],
        ["华东", "李四", "8,500元", "42%", "2026.1.8", "8"],
        ["华东", "王五", "2.3万", "88%", "1/12", "　15"],          # 全角空格 + 无年份日期
        ["华南", "赵六", "3,200", "76%", "2026年2月3日", "20"],
        ["华南", "钱七", "1.8万", "91%", "2026/2/20", "（含退货）"],  # 全角括号
        ["华北", "孙八", "15600", "64%", "3月8日", "9"],
        ["华北", "周九", "9,800元", "55%", "20260315", "11"],
        ["合计", None, "9.6万", None, None, "75"],
        [None, None, None, None, None, None],
        ["注：数据截至3月31日，含税", None, None, None, None, None],
        ["制表人：小李　　审核：老王", None, None, None, None, None],
    ]
    merges = ["A1:F1", "A5:A6", "A8:A9"]
    return X.write_xlsx_lite(path, rows, sheet_name="销售明细", merges=merges)


def build_messy_xlsx(path):
    """
    复合列 + 重复行 + 同义写法 + 可提取手机号 + 占位符，用来验证五个增强能力。
    """
    rows = [
        ["客户信息登记表（2026年一季度）", None, None, None, None],
        [None, None, None, None, None],
        ["客户", "联系方式", "城市", "金额", "提交日期"],
        ["张三", "张三 13812345678", "北京分公司", "1.2万", "2026年1月5日"],
        ["李四", "李四 13900001111", "北京分公司(总部)", "3,200", "2026.1.8"],
        ["王五", "王五 13700002222", "SYD", "2.5万", "1/12"],
        ["赵六", "赵六 13600003333", "Sydney", "860", "2026年3月18日"],
        ["张三", "张三 13812345678", "北京分公司", "1.2万", "2026年1月5日"],
        ["孙八", "孙八 13500004444", "上海", "--", "2026年3月20日"],
        ["合计", None, None, "5.06万", None],
    ]
    return X.write_xlsx_lite(path, rows, sheet_name="客户信息", merges=["A1:E1"])


def build_gbk_csv(path):
    rows = [
        ["部门", "姓名", "报销金额", "提交日期", "状态"],
        ["技术部", "张三", "1,200.50元", "2026年3月1日", "已通过"],
        ["技术部", "李四", "3,800元", "2026/3/5", "待审批"],
        ["市场部", "王五", "2.5万", "3月10日", "已通过"],
        ["市场部", "赵六", "860", "2026年3月18日", "已驳回"],
        ["合计", None, "5.06万", None, None],
    ]
    with open(path, "w", newline="", encoding="gb18030") as f:
        csv.writer(f).writerows(rows)
    return True


def main():
    outdir = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.abspath(__file__))
    os.makedirs(outdir, exist_ok=True)
    p1 = os.path.join(outdir, "sample_dirty.xlsx")
    p2 = os.path.join(outdir, "sample_gbk.csv")
    p3 = os.path.join(outdir, "sample_messy.xlsx")
    build_dirty_xlsx(p1)
    build_gbk_csv(p2)
    build_messy_xlsx(p3)
    print("已生成:")
    print("  %s  (合并表头/中文单位/文本数字/合计行/备注行)" % p1)
    print("  %s  (GBK 编码，直接双击打开会乱码)" % p2)
    print("  %s  (复合列/重复行/同义写法/可提取手机号/占位符)" % p3)


if __name__ == "__main__":
    main()
