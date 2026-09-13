---
name: excel-clean-zh
slug: excel-clean-zh
displayName: 中文脏表格清洗与修复
version: 1.1.0
summary: 把别人发来的中文 Excel/CSV 脏表洗成能直接算的数据——合并单元格、1.2万这类中文单位、GBK 乱码、数字存成文本、重复值、复合列拆分，一次搞定并给出可追溯的变更报告
license: MIT
category: office-efficiency
platforms: [windows, macos, linux]
description: |
  Use this skill whenever a spreadsheet needs to be read, cleaned, analyzed,
  merged, or converted — especially messy real-world Chinese business tables.
  Triggers on: 表格/Excel/CSV/xlsx 清洗、整理、汇总、读取、分析、转换；
  "打不开"、"乱码"、"算不出来"、"SUM 是 0"、"求和不对"、"合并单元格"、
  "数字存成文本"、"绿三角"、"1.2万"、"万/亿"、"GBK"、"表头不在第一行"、
  "合计行"、"多个 sheet"、"脏数据"、"数据清洗"、"重复值"、"去重"、
  "一列拆多列"、"分列"、"提取手机号"、"提取数字"、"VLOOKUP 匹配不上"、
  "分组统计对不上"、"公司名重复"。
  Covers merged-cell headers, multi-row headers, Chinese numeric units
  (万/亿/千/百/元/%), GBK/GB18030 mojibake, numbers stored as text,
  Chinese date formats (2026年3月5日 / 2026.3.5 / 20260315),
  full-width and invisible characters, total/subtotal rows mixed into data,
  multiple tables in one sheet, blank rows/columns, duplicate column names,
  duplicate row detection, composite column splitting (姓名手机号 in one cell),
  pattern extraction (phone/email/ID/URL from free text),
  synonym detection (北京分公司 vs 北京分公司(总部), SYD vs Sydney),
  and post-clean self-verification with a conformance score.
  Zero third-party dependencies — pure Python standard library, no pip install.
agent_created: true
---

# 中文脏表格清洗与修复

把别人发来的、导出的、系统生成的中文表格洗成能直接算的数据。

**核心主张：先体检，再动手。** 直接读脏表就像闭着眼睛做手术——你不知道表头在第几行、哪些数字其实是文本、有没有合计行混在里面。

## 何时使用

- 用户要读取 / 分析 / 汇总 / 转换一个 xlsx、csv、tsv 文件
- 表格打开乱码（多半是 GBK 编码被当 UTF-8 读）
- SUM / 排序 / 透视表结果不对，或单元格左上角有绿三角
- 表头不在第 1 行（上面压着大标题、填报说明）
- 数据里有 `1.2万`、`8,500元`、`35%`、`2026年3月5日` 这类中文写法
- 一个 sheet 里塞了多张表，或末尾混着"合计""备注"
- 怀疑有重复行要去重，但不确定会不会误删合法明细
- 姓名和手机号挤在一列、或"张三-销售部-北京"这类复合字段要拆开
- VLOOKUP 匹配不上、分组统计把一家公司拆成两行（写法不统一）

## 工作流

### 1. 体检（必做，不要跳过）

```bash
python scripts/inspect_sheet.py 文件.xlsx
python scripts/inspect_sheet.py 文件.csv --json     # 要结构化结果时
```

输出问题清单，按 P0 / P1 / P2 分级，并直接给出建议的清洗命令。
**退出码 1 表示有 P0 问题**——不修数据没法用。

### 2. 清洗

按体检报告建议的命令执行：

```bash
python scripts/clean_sheet.py 文件.xlsx --header-row 3 --drop-total
python scripts/clean_sheet.py 文件.csv --default-year 2026
python scripts/clean_sheet.py 文件.xlsx --percent decimal      # 35% -> 0.35
python scripts/clean_sheet.py 文件.xlsx --xlsx                 # 额外导出 xlsx
```

产出三个文件，**不覆盖源文件**：

| 文件 | 用途 |
|---|---|
| `*_clean.csv` | 干净数据，UTF-8-BOM，Excel/WPS 双击不乱码 |
| `*_clean.report.md` | 人看的变更报告 + **需要你确认的值** |
| `*_clean.changes.json` | 机器可读的逐处改动 |

### 3. 看报告里的「需要你确认的值」

这一步不能省。有些值**改了可能就是错的**，脚本不猜：

- `1/12` —— 是 1月12日 还是 12月1日？缺年份且分隔符有歧义
- 数字列里混进的 `(含退货)`、`待定`、`--`

报告会把它们连同行号列出来，由用户决定是置空还是改数。

## 命令参数

| 参数 | 作用 |
|---|---|
| `--header-row N` | 表头在原始文件第 N 行（1 基）。体检会自动猜，猜不准就手动指定 |
| `--sheet N` / `--sheet "名字"` | 选工作表，序号 0 基 |
| `--drop-total` | 剔除合计/小计行（不剔除会让求和翻倍） |
| `--tag-total` | 保留合计行但打 `__合计行__` 标记 |
| `--split-blocks` | 检测一个 sheet 内的多个数据块 |
| `--percent keep\|decimal` | `35%` → `35`（默认）还是 `0.35` |
| `--default-year YYYY` | 无年份日期（`3月8日`）的年份。**不给就不补，避免跨年错位** |
| `--no-number` / `--no-date` | 关掉数值 / 日期转换，只做字符规范化 |
| `--dedupe` | 删除整行完全重复的行。**默认只报告不删**，一张单据常有多个明细行 |
| `--dedupe-by 列名,列名` | 按指定列去重，比整行去重激进，慎用 |
| `--split-col 列名 --delim " "` | 拆复合列：`张三 13812345678` → 两列。原列保留 |
| `--extract "列名:手机号"` | 从文本提取：手机号/邮箱/身份证/URL/日期串，追加新列 |
| `--out 目录` | 输出目录，默认与源文件同目录 |

## 能修什么

| 脏数据 | 处理 |
|---|---|
| 合并单元格表头 | 向下向右填充，pandas 读入变 NaN 的问题一并解决 |
| 表头不在首行（大标题占位） | 打分识别，也可用 `--header-row` 指定 |
| `1.2万` `1.5亿` `3.5千` | 剥单位换算成数字，**用 Decimal 保证金额精度** |
| `8,500元` `1,200.50元` | 去千分位与货币符号，保留小数 |
| `35%` | 默认转 `35`，加 `--percent decimal` 转 `0.35` |
| `(100)` | 括号负数 → `-100` |
| 数字存成文本（绿三角） | 转成真数字，SUM/排序恢复 |
| `2026年3月5日` `2026.3.5` `20260315` `3月8日` | 统一转 ISO `2026-03-08` |
| GBK / GB18030 编码 | 自动识别解码，输出统一 UTF-8-BOM |
| 全角字符、不可见字符、全角空格 | 规范化，`（含退货）` → `(含退货)` |
| 合计 / 小计 / 备注 / 制表人行 | 识别并剔除（或标记） |
| 空行、空列、重复列名、空列名 | 删除或补全 |
| 整行重复 | 报告后可用 `--dedupe` 删；按列重复只提示，**可能是合法明细行** |
| 复合列（姓名手机号挤一格） | 体检识别分隔符与段数，`--split-col` 拆分 |
| 文本里藏着手机号/邮箱/身份证 | `--extract` 提取成新列，对应 Excel 的快速填充 |
| 同一实体多种写法（公司名/缩写） | 三档置信度报告，**不自动合并** |
| 清洗后是否真的干净 | 自检给出逐列达标率与总完成度，识别"假达标" |

## 安全边界

- **不覆盖源文件**，一律输出到新文件
- **不把空值填成 0**——`无`、`待定`、`--` 不等于 0，不制造假数据
- **不猜范围值的中值**——`100-200` 只取下限 100 并在报告里标记
- **不猜歧义日期**——`1/12` 保持原样并列入待确认
- **重复值默认不删**——一张发票常有多个明细行，看着像重复其实是合法数据。
  体检会区分"整行完全重复"（可用 `--dedupe` 删）和"按列重复"（只提示）
- **同义写法不自动合并**——"北京分公司(总部)"可能是独立统计主体，
  只按置信度报告，合并与否由人定
- **每处改动可追溯**，changes.json 记录行、列、原值、新值、规则
- 纯本地计算，不联网、不上传

## 依赖

**零第三方依赖**，只用 Python 标准库（zipfile / ElementTree / csv / decimal）。
不需要 `pip install openpyxl pandas chardet`——xlsx 本质是 zip 里的 XML。

若环境里恰好有 openpyxl，`--xlsx` 会用它导出；没有则回退到内置的零依赖 xlsx 写入器，Excel / WPS / LibreOffice 均可打开。

## 限制

- **不支持 `.xls`**（Office 2003 二进制格式）。先用 Excel/WPS 另存为 xlsx，或 `soffice --headless --convert-to xlsx 文件.xls`
- 只读数据层（值、类型、合并单元格），不还原单元格配色、条件格式、图表
- 数值一律按十进制解析，不处理 Excel 里"显示为整数实为浮点"的显示格式差异
- 特大文件（10 万行以上）建议先 `--no-date --no-number` 试跑，看规模再全量清洗

## 配套文件

- `scripts/xlsx_lite.py` — 零依赖 xlsx 读写 + 编码嗅探
- `scripts/dirty_rules.py` — 脏数据识别与修复规则库
- `scripts/extras.py` — 五个增强能力（重复值/拆分/提取/同义/自检）
- `scripts/inspect_sheet.py` — 体检（只读）
- `scripts/clean_sheet.py` — 清洗（写文件）
- `references/dirty-patterns.md` — 中文脏数据模式手册，含每种坑的原理与人工修法
- `test/make_samples.py` — 生成脏表样本
- `test/run_tests.py` — 回归测试，`python test/run_tests.py`
