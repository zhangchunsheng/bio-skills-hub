# pharmacy-word-report 技能说明

> 把「药库出库」Excel 一键变成**三线表、结论先行、带图**的 Word 药品使用分析报表。

## 这个技能能做什么
输入一份全院药库出库 Excel（含科室、通用名、数量、单价、金额、ATC 1–4 级等字段），自动产出一份分层级、可直接用于药学点评/汇报的 `.docx` 报表，包含：

- **总体**：金额排名前 50 药品 + 帕累托图
- **ATC 分类**：按 1 级（全部）→ 2/3/4 级汇总
- **科室**：前 30 科室 +「专科-主导药品匹配存疑」+「单药占比 >30% 高度集中」两类风险提示
- **数据概况与质量**：记录数、缺失值、金额=数量×单价 校验
- 全部为三线表（无竖线），每段【结论】先行

## 什么时候用
- 用户上传/引用一份药库出库 Excel，并要「药品使用分析报表 / Word 格式 / 三线表 / 药库出库分析 / 科室药品使用分析」。
- 不适合：纯数据探索（无交付物）、非药库出库类表格（请用通用数据分析技能）。

## 怎么用（两步）
```bash
# 1) 聚合 + 出图（输出 analysis_results.json 与 figs/）
python scripts/analyze.py <输入.xlsx> [输出目录]

# 2) 生成 Word
python scripts/build_docx.py <输出目录/analysis_results.json> <输出.docx>
```
> 依赖：`pandas openpyxl python-docx matplotlib`（建议用隔离 venv 安装，勿污染用户环境）。
> 换月份只需换输入文件；若列名不同，改 `scripts/analyze.py` 顶部的 `COLMAP` 一处即可。

## 硬性约束
- **不臆造**：仅汇总已有字段，缺失值/金额为 0 等如实标注，绝不填补。
- **结论先行 + 分层级 + 三线表**。
- **脱敏**：不出现任何患者身份信息。
- 金额单位表格用「万元」、量级用「亿元」；占比 = 占全院出库金额比。

## 可疑性判读口径
- **匹配存疑**：科室名含康复/中医/皮肤/眼科/口腔/耳鼻喉/生殖/妇产/针灸/风湿等，但其金额第一药品属「抗肿瘤药及免疫调节剂」→ 标「需药师核实」。对阿达木单抗（风湿/眼科）、环孢素（生殖）等临床合理情形，不视为不合理。
- **高度集中**：单药占本科室金额 >30% → 仅作结构性提示，不直接判定不合理。

## 两月对比与月度趋势分析（扩展）
在「单月报表」之上，本技能附带三个脚本，可把任意相邻两个月的数据合并为**月度趋势分析**报表（含环比、存疑科室逐月深挖）：

```bash
# 0) 先对两个月分别跑单月聚合（见上）
python scripts/analyze.py <202606.xlsx> out_202606
python scripts/analyze.py <202607.xlsx> out_202607

# 1) 两月环比（总额/品种/Top药品/ATC/存疑科室）
python scripts/compare.py out_202606/analysis_results.json out_202607/analysis_results.json out_compare

# 2) 存疑科室单科室明细深挖（逐月 Top药品、主导药占比）
python scripts/dept_dive.py <202606.xlsx> <202607.xlsx> \
       out_202606/analysis_results.json out_202607/analysis_results.json out_compare

# 3) 生成合并趋势报表
python scripts/build_trend_docx.py out_compare/comparison_results.json \
       out_compare/dept_dive.json out_202606/analysis_results.json \
       out_202607/analysis_results.json 全院药品使用月度趋势分析_202606-202607.docx
```
产出报表含：总体环比表 + 总额对比图、Top20 药品金额/排名环比、ATC1 占比环比、存疑科室两月对照表 + 11 个科室逐月明细表、综合结论与药学干预建议。

## 文件结构
```
pharmacy-word-report/
├── SKILL.md                  # 完整工作流与约束（给智能体读）
├── README.md                 # 本说明
├── scripts/
│   ├── analyze.py            # 单月：画像 + 聚合 + 出图
│   ├── build_docx.py         # 单月：JSON → 三线表 Word
│   ├── compare.py            # 扩展：两月环比 → comparison_results.json
│   ├── dept_dive.py          # 扩展：存疑科室逐月明细 → dept_dive.json
│   └── build_trend_docx.py   # 扩展：合并生成月度趋势分析 Word
└── references/
    └── report_template.md    # 报表章节结构、8 张表规格、判读口径
```

## 备注
单月报表与两月趋势分析共用同一套「如实汇总、不填补、结论先行、三线表」规范；202606 中 54 行 ATC 缺失已在数据质量段如实标注。换更多月份时，依样逐月跑 `analyze.py` 后再做 `compare.py` / `dept_dive.py` 即可。
