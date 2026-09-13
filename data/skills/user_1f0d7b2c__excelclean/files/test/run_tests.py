#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
回归测试。纯标准库，直接 python run_tests.py 即可。

重点防两类事故：
  1. 金额算错（5.06万 必须等于 50600，不能是 50599.99999999999）
  2. 误伤（"张三""万象城" 不能被当成数字改掉）
"""

import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.join(HERE, "..", "scripts")
sys.path.insert(0, SCRIPTS)

import xlsx_lite as X
from dirty_rules import parse_number, parse_date, normalize_text

passed, failed = 0, 0


def check(name, got, want):
    global passed, failed
    if got == want and type(got) is type(want):
        passed += 1
    else:
        failed += 1
        print("  FAIL %s\n       得到 %r (%s)\n       期望 %r (%s)" % (
            name, got, type(got).__name__, want, type(want).__name__))


def check_none(name, got):
    global passed, failed
    if got is None:
        passed += 1
    else:
        failed += 1
        print("  FAIL %s  期望 None，得到 %r" % (name, got))


# ---------------------------------------------------------------- 数值
print("[1] 数值解析 —— 中文单位与精度")
check("1.2万", parse_number("1.2万")[0], 12000)
check("5.06万(浮点精度)", parse_number("5.06万")[0], 50600)
check("1.5亿", parse_number("1.5亿")[0], 150000000)
check("2.3万", parse_number("2.3万")[0], 23000)
check("8,500元", parse_number("8,500元")[0], 8500)
check("1,200.50元(保留小数)", parse_number("1,200.50元")[0], 1200.5)
check("3,200(千分位文本)", parse_number("3,200")[0], 3200)
check("15600(纯数字文本)", parse_number("15600")[0], 15600)
check("3.5千", parse_number("3.5千")[0], 3500)
check("2百万", parse_number("2百万")[0], 2000000)
check("35%(keep)", parse_number("35%")[0], 35)
check("35%(decimal)", parse_number("35%", percent="decimal")[0], 0.35)
check("(100)括号负数", parse_number("(100)")[0], -100)
check("100-200取下限", parse_number("100-200")[0], 100)
check("全角１５", parse_number("１５")[0], 15)
check("带空格 1.2 万", parse_number(" 1.2万 ")[0], 12000)
check("负号 -500", parse_number("-500")[0], -500)
check("25人(单位识别)", parse_number("25人")[0], 25)
check("单位返回值", parse_number("1.2万")[1], "万")
check("百分号单位", parse_number("35%")[1], "%")

print("[2] 数值解析 —— 不该动的")
check_none("张三", parse_number("张三")[0])
check_none("万象城(万不能当单位)", parse_number("万象城")[0])
check_none("待定", parse_number("待定")[0])
check_none("空串", parse_number("")[0])
check_none("ABC-123", parse_number("ABC-123")[0])
check_none("已通过", parse_number("已通过")[0])

# ---------------------------------------------------------------- 日期
print("[3] 日期解析")
check("2026年1月5日", parse_date("2026年1月5日"), "2026-01-05")
check("2026.1.8", parse_date("2026.1.8"), "2026-01-08")
check("2026/2/20", parse_date("2026/2/20"), "2026-02-20")
check("20260315", parse_date("20260315"), "2026-03-15")
check("3月8日(补年份)", parse_date("3月8日", default_year=2026), "2026-03-08")
check("2026年3月", parse_date("2026年3月"), "2026-03")
check("2026年Q1", parse_date("2026年Q1"), "2026-Q1")
check("2026年一季度", parse_date("2026年一季度"), "2026-Q1")
check_none("1/12(歧义不猜)", parse_date("1/12"))
check_none("3月8日无年份不猜", parse_date("3月8日"))
check_none("张三不是日期", parse_date("张三"))
check_none("2026年13月(非法月份)", parse_date("2026年13月5日"))

# ---------------------------------------------------------------- 字符
print("[4] 字符规范化")
check("全角空格", normalize_text("　15")[0], "15")
check("全角括号", normalize_text("（含退货）")[0], "(含退货)")
check("全角数字", normalize_text("１２３")[0], "123")
check("连续空格压缩", normalize_text("张  三")[0], "张 三")
check("首尾去空格", normalize_text("  张三  ")[0], "张三")
check("不改动判断", normalize_text("张三")[1], False)

# ---------------------------------------------------------------- xlsx 读写
print("[5] xlsx 零依赖读写")
with tempfile.TemporaryDirectory() as td:
    p = os.path.join(td, "t.xlsx")
    src = [["姓名", "金额", None], ["张三", 12000, "备注"], [None, "1.2万", True]]
    X.write_xlsx_lite(p, src, "中文表名", merges=["A1:A1"])
    sh = X.read_xlsx(p)[0]
    check("sheet 名", sh.name, "中文表名")
    check("读回尺寸", (sh.nrows, sh.ncols), (3, 3))
    check("读回内容", sh.values(), src)
    check("合并信息", sh.merges, ["A1:A1"])
    # 编码检测
    gp = os.path.join(td, "g.csv")
    with open(gp, "wb") as f:
        f.write("部门,姓名\n技术部,张三\n".encode("gb18030"))
    rows, enc, delim = X.read_delimited(gp)
    check("GBK 识别", enc, "gb18030")
    check("GBK 内容", rows[1][1], "张三")

# ---------------------------------------------------------------- 端到端
print("[6] 端到端：脏 xlsx -> 清洗")
sample = os.path.join(HERE, "sample_dirty.xlsx")
if os.path.exists(sample):
    with tempfile.TemporaryDirectory() as td:
        out = subprocess.run(
            [sys.executable, os.path.join(SCRIPTS, "clean_sheet.py"),
             sample, "--header-row", "3", "--drop-total",
             "--default-year", "2026", "--out", td],
            capture_output=True, text=True, encoding="utf-8")
        check("退出码", out.returncode, 0)
        csv_p = os.path.join(td, "sample_dirty_clean.csv")
        check("生成 CSV", os.path.exists(csv_p), True)
        if os.path.exists(csv_p):
            with open(csv_p, encoding="utf-8-sig") as f:
                lines = [l.rstrip("\n") for l in f if l.strip()]
            check("输出行数(表头+7)", len(lines), 8)
            check("表头", lines[0], "大区,销售员,销售额,完成率,签约日期,客户数")
            check("1.2万 -> 12000", lines[1].split(",")[2], "12000")
            check("日期转 ISO", lines[1].split(",")[4], "2026-01-05")
            check("全角空格去除", lines[3].split(",")[5], "15")
            # 合计行必须被剔除
            check("合计行已剔除", any("合计" in l for l in lines[1:]), False)
            # BOM 必须存在，否则 Excel 打开乱码
            with open(csv_p, "rb") as f:
                check("UTF-8 BOM", f.read(3), b"\xef\xbb\xbf")
        # 待确认值必须被标记出来
        rp = os.path.join(td, "sample_dirty_clean.report.md")
        if os.path.exists(rp):
            rep = open(rp, encoding="utf-8").read()
            check("标记 1/12 歧义日期", "1/12" in rep, True)
            check("标记数字列混入文本", "(含退货)" in rep, True)

print("[7] 端到端：GBK csv -> 清洗")
gsample = os.path.join(HERE, "sample_gbk.csv")
if os.path.exists(gsample):
    with tempfile.TemporaryDirectory() as td:
        out = subprocess.run(
            [sys.executable, os.path.join(SCRIPTS, "clean_sheet.py"),
             gsample, "--drop-total", "--default-year", "2026", "--out", td],
            capture_output=True, text=True, encoding="utf-8")
        check("退出码", out.returncode, 0)
        csv_p = os.path.join(td, "sample_gbk_clean.csv")
        if os.path.exists(csv_p):
            with open(csv_p, encoding="utf-8-sig") as f:
                lines = [l.rstrip("\n") for l in f if l.strip()]
            check("中文没乱码", "技术部" in lines[1], True)
            check("1,200.50元 -> 1200.5", lines[1].split(",")[2], "1200.5")
            check("2.5万 -> 25000", lines[3].split(",")[2], "25000")

# ---------------------------------------------------------------- 增强能力
print("[8] 增强能力：重复值 / 拆分 / 提取 / 同义 / 自检")
import extras as EX

H = ["客户", "联系方式", "城市", "金额"]
R = [
    ["张三", "张三 13812345678", "北京分公司", "1.2万"],
    ["李四", "李四 13900001111", "北京分公司(总部)", "3,200"],
    ["王五", "王五 13700002222", "SYD", "2.5万"],
    ["赵六", "赵六 13600003333", "Sydney", "860"],
    ["张三", "张三 13812345678", "北京分公司", "1.2万"],
]

d = EX.find_duplicates(H, R)
check("整行重复组数", d["full_row_dup_groups"], 1)
check("可删行数", d["full_row_removable"], 1)
check("重复值不是空串", d["by_column"]["金额"]["examples"][0]["value"], "1.2万")

comp = EX.detect_composite(H, R)
check("检出复合列", len(comp), 1)
check("复合列名", comp[0]["column"], "联系方式")
check("拆分段数", comp[0]["segments"], 2)

ext = EX.detect_extractable(H, R)
check("检出可提取", len(ext) >= 1, True)
check("提取类型", ext[0]["kind"], "手机号")
check("提取结果", ext[0]["extracted"], "13812345678")

syn = EX.detect_synonyms(H, R)
city = [s for s in syn if s["column"] == "城市"]
check("检出同义列", len(city), 1)
levels = [p["level"] for p in city[0]["pairs"]]
check("中置信尾缀", "中" in levels, True)
check("低置信缩写", "低" in levels, True)

# ISO 日期不能被误判成复合列——这是清洗后常见的误报
check("ISO日期不误判为复合列",
      EX.detect_composite(["日期"], [["2026-01-05"], ["2026-02-03"], ["2026-03-08"]]), [])

# 未清洗的表：类型一致但藏着数字，不能显示"全部达标"
sc_raw = EX.self_check(H, R)
check("未清洗表识别残留空间", sc_raw["columns_uncleaned"] >= 1, True)
check("未清洗表不误报达标", "全部达标" in sc_raw["verdict"], False)
# 清洗后的表：真达标
sc_ok = EX.self_check(H, [["张三", 13812345678, "北京", 12000],
                          ["李四", 13900001111, "上海", 3200]])
check("清洗后达标", sc_ok["score"], 1.0)
check("清洗后判语", sc_ok["verdict"], "全部达标，可以直接进分析")

print("[9] 端到端：--dedupe / --split-col / --extract")
msample = os.path.join(HERE, "sample_messy.xlsx")
if os.path.exists(msample):
    with tempfile.TemporaryDirectory() as td:
        out = subprocess.run(
            [sys.executable, os.path.join(SCRIPTS, "clean_sheet.py"),
             msample, "--header-row", "3", "--drop-total",
             "--default-year", "2026", "--dedupe",
             '--split-col', '联系方式', '--delim', ' ',
             '--extract', '联系方式:手机号', "--out", td],
            capture_output=True, text=True, encoding="utf-8")
        check("退出码", out.returncode, 0)
        csv_p = os.path.join(td, "sample_messy_clean.csv")
        if os.path.exists(csv_p):
            with open(csv_p, encoding="utf-8-sig") as f:
                lines = [l.rstrip("\n") for l in f if l.strip()]
            hdr = lines[0]
            check("拆出两列", "联系方式_1" in hdr and "联系方式_2" in hdr, True)
            check("提取出手机号列", "联系方式_手机号" in hdr, True)
            # 6 行原始数据(张三/李四/王五/赵六/张三/孙八) - 1 行整行重复 = 5 行，
            # 合计行在更早的剔除步骤里已经去掉了
            check("去重后行数", len(lines) - 1, 5)
            check("手机号提取正确", "13812345678" in lines[1], True)

print("")
print("通过 %d，失败 %d" % (passed, failed))
sys.exit(1 if failed else 0)
