---
icon: icon.png
name: glucocorticoid-prescription-review-report
description: "【世界药师节·AI药学技能大赛参赛作品】糖皮质激素处方点评分析报告（Glucocorticosteroid Prescription Review Report）。依据《糖皮质激素类药物临床应用指导原则》（2011/2023版），对医院上传的糖皮质激素专项点评 xlsx 表格（住院医嘱表 / 门急诊处方表）进行结构化数据分析，自动完成不合理判定与原因归类，并按六步强制结构输出正式医疗文书风格的处方点评分析报告。This skill should be used when a clinical pharmacist or pharmacy quality-control officer provides one or more glucocorticosteroid prescription/order review spreadsheets (.xlsx) and asks for a prescription review analysis report, 点评分析报告, 不合理统计, or quarterly 激素点评总结. 触发词：糖皮质激素点评、激素处方点评、处方点评分析报告、专项点评总结、住院医嘱点评、门急诊处方点"
agent_created: true
slug: glucocorticoid-prescription-review-report
version: 1.0.0
displayName: 糖皮质激素处方点评分析
summary: "【世界药师节·AI药学技能大赛参赛作品】糖皮质激素处方点评分析报告（Glucocorticosteroid Prescription Review Report）。依据《糖皮质激素类药物临床应用指导原则》（2011/2023版），对医院上传的糖皮质激素专项点评 xlsx 表格（住院医嘱表 / 门急诊处方表）进行结构化数据分析，自动完成不合理判定与原因归类，并按六步强制结构输出正式医疗文书风格的处方点评分析报告。This skill should be used when a clinical pharmacist or pharmacy quality-control officer provides one or more glucocorticosteroid prescription/order review spreadsheets (.xlsx) and asks for a prescription review analysis report, 点评分析报告, 不合理统计, or quarterly 激素点评总结. 触发词：糖皮质激素点评、激素处方点评、处方点评分析报告、专项点评总结、住院医嘱点评、门急诊处方点"
category: 药学服务
license: Internal
tags: [药学服务]
author: 陈文秀
---


# 糖皮质激素处方点评分析报告

## Overview

对医院临床药师上传的糖皮质激素类药物专项点评表格（住院医嘱 / 门急诊处方 xlsx）进行结构化数据分析，提取不合理记录、判定不合理类型与原因，并按六步强制结构撰写正式医疗文书风格的处方点评分析报告。适用于公立医院药事质控季度专项点评工作，结论须严谨、符合官方指导原则。

## 适用输入

- **住院医嘱点评表**（.xlsx）：表头含 `创建时间 | 点评编号 | 审核结果 | 年龄 | 性别 | 就诊/入院时间 | 出院时间 | 出院科室 | 诊断 | 出院诊断 | 总费用(元) | 药品通用名数 | 药品 | 药品总数 | 存在问题`。
- **门急诊处方点评表**（.xlsx）：表头含 `创建时间 | 处方号 | 审核结果 | 年龄 | 性别 | 就诊/入院时间 | 就诊/入院科室 | 诊断 | 费别 | 总费用(元) | 药品通用名数 | 药品 | 药品总数`。
- 表类型由列名自动识别，无需用户声明；可一次输入一份或多份（住院+门急诊）。
- 审核结果列值通常为 `合理` / `不合理`。

## 完整工作流

按以下步骤依次执行，不得跳步。

### 第 1 步：确认运行环境与依赖

- 使用受管 Python：`C:\Users\chenwenxiu\.workbuddy\binaries\python\envs\default\Scripts\python.exe`（若不存在，先用 `C:\Users\chenwenxiu\.workbuddy\binaries\python\versions\3.13.12\python.exe -m venv` 创建 venv 并 `pip install openpyxl`）。
- 分析脚本位于本 skill 目录：`scripts/analyze_gc_prescription.py`，依赖 `openpyxl`。

### 第 2 步：运行分析脚本提取数据

执行脚本，将用户上传的 xlsx 路径作为参数，结果写入临时文件以便读取：

```bash
"<venv-python>" "<skill-dir>/scripts/analyze_gc_prescription.py" "<xlsx1>" "<xlsx2>" --out "<工作区>/gc_analysis_result.txt"
```

脚本自动完成：
- 表类型识别（住院 / 门急诊）
- 总记录数、审核结果分布、时间范围
- 科室分布
- 涉及糖皮质激素药品清单（去重）与通用名使用频次
- 不合理记录逐条明细（ID、科室、年龄、性别、诊断、激素药品、存在问题原文）
- 不合理记录科室分布
- 多表合并汇总（总条数、不合理条数、不合理率）

执行后用 Read 工具读取 `gc_analysis_result.txt` 获取全部结果。

### 第 3 步：不合理判定与原因归类

加载参考文件 `references/gc_judgment_rules.md`，对每条不合理记录判定不合理类型与原因：

- 若原表已填写"存在问题"原文（住院表常有），直接引用原文并归类为对应类型（适应症不适宜 / 无适应症用药 / 用法用量不适宜 / 联合用药不适宜 / 禁忌症用药 / 特殊人群用药不适宜）。
- 若原表未填写（门急诊表常无"存在问题"列），依据患者诊断 + 激素品种，对照 `gc_judgment_rules.md` 第三部分"常见超适应症场景判定规则"进行判定，并在报告第二步表格上方注明"经药师依据《糖皮质激素类药物临床应用指导原则》判定"。
- 高频超适应症场景：感染性发热用地塞米松退热、术后用甲泼尼龙消肿、门诊慢性疼痛口服泼尼松止痛、肿瘤无指征用甲泼尼龙、腹泻/胃肠功能紊乱用泼尼松——均判定为适应症不适宜或无适应症用药。

### 第 4 步：按六步结构撰写报告

加载参考文件 `references/report_template.md`，严格按其六步结构撰写。六步为：

1. **基础概况**：点评月份、抽查总条数、涉及药品清单（按给药途径分类）、涉及科室分布、激素通用名使用频次。
2. **逐条问题医嘱不合理判定与原因**：结构化表格（序号 / 用药科室 / 患者年龄 / 诊断 / 不合理原因），住院与门急诊分表。
3. **各类不合理问题数量、占比、科室分布统计表**。
4. **高频问题深度分析**：从医师认知、科室习惯、应急滥用、专科宣教缺失四个维度剖析现实痛点。
5. **分层整改对策**：药师干预、专项培训、科室质控约谈、后续常态化筛查方案，含时间节点表。
6. **可直接复制上交的季度糖皮质激素专项点评工作总结**：正式医疗文书风格，五段结构（工作开展 / 点评结果 / 主要问题 / 整改措施 / 下一步工作）。

撰写要求：
- 表题在表上方，图题在图下方（默认无图，全结构化表格）。
- 所有数字须与脚本输出一致，不得臆造。
- 语言正式医疗文书风格，结论严谨，符合指导原则。
- 报告抬头固定要素见 `references/report_template.md`。

### 第 5 步：输出报告文件

将完整报告写入工作区，文件名格式：`{年份}年{季度}糖皮质激素专项点评分析报告.md`。用 present_files 呈现给用户。若用户要求 Word 版，再按本地 DOCX 创建流程转换。

## 专项筛查（可选）

当用户提供筛选条件时（如"针对骨科""针对口服泼尼松""针对急诊"），在运行脚本后、撰写报告前，按条件过滤不合理记录与统计口径，输出专项子报告，并在报告抬头注明筛查范围。

## 资源说明

- `scripts/analyze_gc_prescription.py`：通用数据分析脚本，命令行接收 xlsx 路径，输出结构化文本结果。内建糖皮质激素通用名识别关键词表（覆盖甲泼尼龙、地塞米松、泼尼松、布地奈德、倍氯米松、氟替卡松、莫米松、氢化可的松、倍他米松、曲安奈德等），自动从"药品"字段提取激素品种。
- `references/gc_judgment_rules.md`：糖皮质激素适应症清单、不合理问题分类标准、常见超适应症场景判定规则、制剂特性与风险提示、特殊人群关注、判定工作流。
- `references/report_template.md`：六步报告强制结构骨架与撰写要求。

## 注意事项

- 不得臆造数据：所有统计数字、不合理条数均须来源于脚本输出。
- 门急诊表无"存在问题"列时，须如实说明并依据指导原则补充判定，保持质控可追溯性。
- 报告须引用《糖皮质激素类药物临床应用指导原则》2011版与2023版作为依据。
- 输出为 Markdown 便于直接复制上交；如需正式 Word 文档按用户要求转换。
