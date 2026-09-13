---
icon: icon.png
name: pharmacy-shift-scheduler-2
description: 住院药房月度班表自动生成器（v3.4，隐私优先）。This skill should be used when a hospital inpatient pharmacy (or any fixed-position rotating shift team) needs to generate a monthly duty roster that assigns named positions (片剂机配方/审方校对/窗口/13:30机动调配/后勤等) to staff while enforcing rest-day rules (weekend strictly 4 rest / weekday 2 rest / stock-take all-on), treating public holidays as WEEKEND MODE (rest 4 / on-duty 5, only weekend posts staffed, excluded from balance), staffing 机动调配(⑧) only on Mondays and the monthly stock-take day (never on holidays), auto-computing the stock-take day as the last Friday (or prior Friday if month-end or if it collides with a statutory holiday), capping each person's 13:30 shift to once per ISO week, and guaranteeing no empty post. Hospital policy: NO 调休 / NO 补班日 — there is no "makeup workday" category at all. PRIVACY: the skill ships with NO names — the roster must be supplied by the user in the input template; it is unusable without one and leaks no PII. Trigger when the user asks to 生成/排班/做月度班表/值班表, supplies pharmacy staff and position constraints, or wants to audit an existing schedule for rest-day conflicts (一人既休又上) or position-pinning (某人永远钉在一个岗).
agent_created: true
slug: pharmacy-shift-scheduler-2
version: 1.0.0
displayName: 住院药房班表生成助手
summary: 住院药房月度班表自动生成器（v3.4，隐私优先）。This skill should be used when a hospital inpatient pharmacy (or any fixed-position rotating sh…
category: 药学服务
license: Internal
tags: [药学服务]
author: 宋钰龙
---


# 住院药房月度班表生成器（v3.4 · 隐私优先）

## 用途

根据**使用方提供**的人员名单、岗位约束与偏好，自动生成一份住院药房（或同类固定岗位轮转班组）的月度班表 Excel，包含：

- **名单** sheet：人员清单 + 各周岗位概览（窗口/机动调配/13:30/后勤）。
- **总班表** sheet：人 × 日矩阵，每个单元格为单一状态「休 / 班 / 盘」（假期日列以浅蓝标记 + 末尾自描述备注“假期日：…；盘点日：…”，不强制全班）；末列附每人当月休息天数。
- **每周每日班表**（第一周、第二周…）：按完整 ISO 周（周一~周日 7 列）展开，含圆圈编号 ②~⑨、C 列时间段（8:00 / 13:30）、收单/收平板行、药架整理子表，颗粒度对齐真实排班表。

## 隐私（设计即合规）

- 本 skill **不内置任何真实姓名**：`DEFAULT_STAFF` 为空，两份 `assets/班表输入模板*.xlsx` 均为**空名单**（仅一条提示行）。
- 姓名、类型、禁止/偏好/**尽量避免**岗位、备注，**全部**由使用方在输入模板填写。
- 模板名单为空时，生成器直接 `ValueError` 退出，**不会**回退到任何内置姓名。
- 代码与文档不出现任何个人姓名（仅用「药师一…药师九 / 后勤一、后勤二」作占位示例）。

## 何时使用

- 用户提出「帮我排下 X 月的班」「生成月度班表 / 值班表」。
- 用户给了药房人员名单、岗位禁止/偏好约束，要求自动排班。
- 用户想核对一张已有班表是否「有人既休息又上班」「有人永远不休息」「某人一直被钉在一个岗」。
- 任何涉及住院药房固定岗位轮转排班的场景。

## 文件结构

```
pharmacy-shift-scheduler/
├── SKILL.md
├── scripts/
│   ├── schedule_generator.py   # 核心生成器（CLI：--input/--output/--year/--month/--holiday/--stock）
│   ├── verify_output.py        # 弱校验：岗位约束 / 13:30 周频 / 每日人数（周末必须恰好 5 人在岗）
│   └── selfcheck.py            # 强自检：总表↔周表一致性 / 每人休息天数 / 岗位是否被钉死
├── assets/
│   ├── 班表输入模板.xlsx          # 空名单标准模板（含生成参数 sheet，盘点日留空=自动）
│   ├── 班表输入模板_10月盘点.xlsx  # 空名单模板（盘点日参数占位示例）
│   └── 生成班表.bat             # Windows 双击入口（交互输年份/月份/假期日）
└── references/
    └── rules.md                # 岗位定义、约束算法、已知陷阱与排错，使用前务必通读
```

使用前先阅读 `references/rules.md`，其中详细说明了岗位定义、平衡算法、跨月拼接与历史 bug 的根因，避免在生成后再次引入同类问题。

## 运行约定

1. 复制 `assets/` 下的输入模板到工作目录，**先填好「人员名单」页**（否则生成器报错退出）。
2. 用本机 Python（需安装 `openpyxl`）运行 `scripts/` 下的脚本。

**生成（推荐命令行，最通用）：**

```
python scripts/schedule_generator.py --input 班表输入模板.xlsx --output 住院药房2026年9月班表.xlsx --year 2026 --month 9 --holiday "25"
```

- 不传 `--holiday` → 该月按无国定假期处理（注：医院不调休不补班，**不存在任何补班日**）。
- 盘点日：默认自动取当月最后一个周五；若恰为月末、或恰为法定假期，则顺延至上周五（避开假期）。可用 `--stock 30` 或模板「月底盘点日」覆盖。
- 不传 `--output` → 默认输出 `住院药房{year}年{month}月班表.xlsx`。
- 也可运行 `assets/生成班表.bat` 交互输入（若提示找不到 python，按机器实际路径修改 bat 顶部 `PY=` 一行）。

**校验（交付前必须通过两层）：**

```
python scripts/verify_output.py 住院药房2026年9月班表.xlsx --input 班表输入模板.xlsx
python scripts/selfcheck.py     住院药房2026年9月班表.xlsx
```

校验脚本会从输出「总班表」末尾的自描述备注自动解析假期日 / 盘点日，**无需**再传 `--makeup` 等参数。

`selfcheck.py` 不传参数时，会扫描当前目录下所有含「班表」且不含「输入模板」的 .xlsx 文件逐一自检。

## 关键约束（摘要；完整版见 references/rules.md）

1. **人头数神圣**：周末严格休 4（在岗 5）、工作日休 2（在岗 7）、盘点日全员（休 0）、**法定假期按「休息日人数」= 周末模式（休 4 / 上 5，仅排周末岗位）**。绝不浮动、绝不出现空岗。
2. **岗位必须有人 ＞ 员工休息**：固定人头优先；用二分匹配分配每日命名岗，**绝不**把休息的人拉来顶岗破坏休息规则。
3. **公共假期（法定节假日）= 周末模式**：休 4 / 上 5，仅排周末岗位（②片剂机配方 / ③审方校对 / ⑤机动调配麻精一 / ⑥13:30 / ⑦窗口）；④片剂校对、⑧机动调配、后勤等「仅工作日」岗位不排；列头浅蓝标记，且**排除在平衡统计之外**。
4. **无补班日**：医院不调休、不补班，本工具**不存在「补班日」类别**——任何周末都不会被改成工作日，生成器也无 `--makeup` 参数。
5. **机动调配（⑧）限制**：⑧机动调配**仅在每周一与月度盘点日**排人，且**法定假期日不排**（假期按周末模式）；其余日格留空属正确状态。
6. **盘点日自动**：默认当月最后一个周五；若恰为月末、或恰为法定假期，则顺延至上周五（避开假期）。可用 `--stock` / 模板覆盖。
7. **13:30**：每人每个 ISO 周（周一~周日）至多排 1 次（含周末），用回溯保证每周 7 天由不同人员担任（盘点日全员盘点，当日不单列 13:30）。
8. **平衡 best-effort**：在固定人头下，平衡差值 ≤ 2 属正常（与真实班表 −1~−3 量级一致），并非 bug。尽量避免岗位以软罚分实现「尽量少排」。
9. **跨月不完整周（半自动）**：周表按 ISO 周展开，边界日自动从邻月生成结果借来填充满（带 `*` 标记）；跨月周的 13:30 周频与边界日建议人工复核（校验工具已自动跳过跨月日）。

## 自检门槛（交付前强制）

任何生成的班表在交给用户前，必须同时跑通：

- `verify_output.py` → 岗位约束 / 每日人数 / 13:30 全部 0 违规。
- `selfcheck.py` → **[A] 总表「休」与周表真实休息 100% 一致**（杜绝「既休又上」错觉）、**[B] 每人最少休息 ≥ 2 天**（杜绝「永远不休息」）、**[C] 无任何一人主岗占比 ≥ 70% 且总次数 ≥ 5**（杜绝「被钉死在一个岗」）。

若任一门槛未过，回到 `schedule_generator.py` 修复后重新生成，不得把半成品交给用户。

## Resources

- **scripts/**：可执行生成与校验代码，可直接运行，亦可被读取后按需修补。
- **references/rules.md**：岗位定义、约束算法、已知陷阱与排错指南，生成或排错前必读。
- **assets/**：**空名单**输入模板与 Windows 批处理入口，复制到工作目录、填好名单后使用。
