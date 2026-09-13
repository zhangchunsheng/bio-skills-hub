---
icon: icon.png
name: skill-9dd4e461-9
description: 医嘱点评助手（Medical Order Review Assistant）：面向临床药师，接收任意一份或多份住院病例 docx 文档（含病程记录、出院记录、用药明细），自动提取内容、学习所给点评模板的写法，并依据 NCCN / CSCO / IDSA / ASCO 等真实指南对化疗方案、抗感染、预防用药、对症支持逐项做用药合理性点评，最终一步生成结构化的 Word 点评报告。当用户说"点评这份病例""做医嘱点评""分析用药合理性""给病例文档生成点评报告"时触发。
agent_created: true
slug: skill-9dd4e461-9
version: 1.0.0
displayName: 医嘱点评
summary: 医嘱点评助手（Medical Order Review Assistant）：面向临床药师，接收任意一份或多份住院病例 docx 文档（含病程记录、出院记录、用药明细），自动提取内容、学习所给点评模板的写法，并依据 NCCN / CSCO …
category: 药学服务
license: Internal
tags: [药学服务]
author: 刘明群
---
# 医嘱点评助手（Medical Order Review Assistant）

把"读病例 → 学模板 → 按指南做用药合理性点评 → 生成 Word 报告"的重复工作流封装为可复用流程。用户只要丢进来一份（或几份）病例 .docx，即可一步产出标准化的医嘱点评报告。

## 何时使用
- 用户提供 1 份或多份住院病例文档（.docx，含入院记录、病程记录、出院记录、用药明细/医嘱单）。
- 要求：点评用药合理性、做医嘱点评、生成点评报告。
- 通常还会给一份"点评结论模板"（示例病例），需要先学习其写法再套用到新病例。

## 核心工作流
1. **提取内容**：用 `scripts/read_docx.py` 把每份 docx 的段落与表格文本导出（命令见下）。重点抓取：主诉/入院原因、出院诊断、抗肿瘤治疗方案（方案名+药物剂量+疗程+给药顺序）、抗感染时间线与依据、预防用药、对症支持、出院带药、关键检验指标（CRP/PCT/培养/血药浓度/肝肾功能）。
2. **学模板（若有）**：若用户给了模板病例，提炼其结构——通常是「①主诉/入院 → ②出院诊断 → ③抗肿瘤方案(名称+剂量+疗程) → ④抗感染经过(按时间线记录换药及依据，附培养/炎症指标) → ⑤对症支持 → ⑥结论(合理/不合理)」。本助手沿用「时间线 + 指征 + 剂量 + 监测」写法。
3. **逐例分析**（核心，详见 references/review_framework.md）：按"抗肿瘤方案 / 抗感染 / 预防用药 / 对症支持 / 监测 / 书写质量 / 相互作用"七个维度，结合真实指南逐条评价，区分"合理"与"需关注/需纠正"。拿不准的指南先用 WebSearch 核实，**严禁编造指南或凭空下结论**。
4. **生成报告**：把分析结果写成 JSON（schema 见 references/json_schema.md），用 `scripts/build_report.py` 生成 Word。报告含：封面总论（点评依据）、每份病例「病例摘要 → 主要用药情况 → 用药合理性点评(合理/需关注) → 点评结论」、末页六例（或多例）汇总表。
5. **验证**：读回生成的 docx 确认结构完整、章节齐全、汇总表与正文一致。

## 运行环境
- 使用托管 Python：`C:\Users\14446\.workbuddy\binaries\python\versions\3.13.12\python.exe`
- 需要 `python-docx`：若未安装，先建 venv 并安装
  ```
  C:\Users\14446\.workbuddy\binaries\python\versions\3.13.12\python.exe -m venv C:\Users\14446\.workbuddy\binaries\python\envs\default
  C:\Users\14446\.workbuddy\binaries\python\envs\default/Scripts/pip install python-docx
  ```
- 运行脚本用：`C:\Users\14446\.workbuddy\binaries\python\envs\default/Scripts/python <script>`

## 命令示例
```bash
# 1) 提取（支持多文件，可选 --out 输出到文件，默认 stdout）
python scripts/read_docx.py "病例1.docx" "病例2.docx" --out extracted.txt

# 2) 生成报告（输入 JSON 规格，输出 docx）
python scripts/build_report.py --json review_spec.json --out 医嘱点评报告.docx
```

## 三条硬约束（务必遵守）
1. **引用真实、禁止编造**：凡涉及指南/共识/说明书的结论，必须写出具体可查的名称（如《NCCN B-cell Lymphomas v2026》《IDSA 粒缺伴发热指南》《ASCO/COSO 肿瘤VTE预防指南》《CSCO 指南》）；拿不准先 WebSearch 核实后在文中明示。
2. **结论分档**：用「合理 / 基本合理（含需关注点）/ 不合理（含需纠正点）」三档，每一条"需关注/不合理"都必须对应具体的、可执行的改进建议。
3. **中立审慎**：点评基于所提供病历文本；标注"需纠正/不合理"的须为有较明确依据的可优化点，其余为质量改进建议。文末加说明：临床决策须结合患者实时体征、检验动态及本院处方集。

## 资源索引
- `scripts/read_docx.py`：docx 段落+表格提取器（支持多文件、--out）。
- `scripts/build_report.py`：JSON 驱动的 Word 报告生成器（封面+逐例章节+汇总表）。
- `references/review_framework.md`：七维度点评框架 + 常用真实指南清单与检索词。
- `references/json_schema.md`：传给 build_report.py 的 JSON 规格说明与示例。

## 注意事项
- 文件名/患者姓名脱敏（如"蔡XX"）保持原样，不要在报告中还原真实姓名。
- 多份病例时，汇总表列数固定为 4 列（病例 / 主要诊断 / 点评结论 / 主要改进或关注点）。
- 若病例缺少关键字段（如无出院诊断、无用药明细），在对应章节如实标注"病历未提供"，不要臆造。
