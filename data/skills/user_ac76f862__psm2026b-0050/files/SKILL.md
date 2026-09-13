---
name: psm2026b-0050
description: "【世界药师节·AI药学技能大赛参赛作品】This skill should be used when pharmacists or clinical pharmacists need to organize patient medication evidence (images, PDFs, prescriptions, medical records, long-term and temporary orders, lab reports, patient-brought drug photos, and interview notes) into a Best Possible Medication History (BPMH), identify discrepancies between pre-admission/home medications and inpatient orders, and produce a draft for review prior to generating the 表 A.1 医疗机构药物重整记录表 Word document required by the Chinese hospital pharmacy standard T/CHAS 20-2-3—2021. Triggered by requests involving admission/transfer/discharge medication reconciliation, BPMH construction, order discrepancy detection, pharmacist review drafts, or 表 A.1 generation. Final adjustments require human confirmation by a pharmacist and the responsible physician before any signature; the skill never auto-signs, auto-decides on medication changes, or fabricates drug names, doses, or frequencies."
slug: psm2026b-0050
displayName: "药物重整"
summary: "【世界药师节·AI药学技能大赛参赛作品】This skill should be used when pharmacists or clinical pharmacists need to organize patient medication evidence (images, PDFs, prescriptions, medical records, long-term and temporary orders, lab reports, patient-brought drug photos, and interview notes) into a Best Possible Medication History (BPMH), identify discrepancies between pre-admission/home medications and inpatient orders, and produce a draft for review prior to generating the 表 A.1 医疗机构药物重整记录表 Word document required by the Chinese hospital pharmacy standard T/CHAS 20-2-3—2021. Triggered by requests involving admission/transfer/discharge medication reconciliation, BPMH construction, order discrepancy detection, pharmacist review drafts, or 表 A.1 generation. Final adjustments require human confirmation by a pharmacist and the responsible physician before any signature; the skill never auto-signs, auto-decides on medication changes, or fabricates drug names, doses, or frequencies."
author: "刘慧"
version: 1.0.0
category: 药学服务
license: Internal
tags: [药学服务]
---

# Medication Reconciliation Record

## Purpose

辅助药师在住院患者入院、转科或出院等重要环节完成药物重整文书和证据整理：建立证据台账、最佳可能用药史、识别医嘱差异、生成药师复核稿，最终在医师确认后输出符合 T/CHAS 20-2-3—2021 的《表 A.1 医疗机构药物重整记录表》Word 待签字版，同时附带质控报告。

## Hard Boundaries

- 本 Skill **不是**自动处方或自动治疗决策系统。所有调整建议必须由药师与责任医师人工确认。
- 不得猜测药名、剂型、规格、剂量、频次、途径、日期、检验单位、过敏表现。
- 不得把 OCR 结果直接视为已核实事实；不得伪造任何签名。
- 真实患者资料仅在经医疗机构批准的本地或受控环境中处理；Skill 包、示例与测试数据严禁包含真实 PHI。
- 任何缺失字段保留为"待核实"，不得删除整条记录。
- 上述规则详见 `references/privacy-and-safety.md`，**每次执行都必须先读取**。

## Authoritative Source

权威依据是 `references/medication-reconciliation-standard.md`（摘自 T/CHAS 20-2-3—2021）。字段定义、差异分类、输出契约均不得与该文件冲突。**执行前必须先读取该文件**。

## Workflow (Do Not Skip Phases)

按以下六阶段顺序执行，不得跳过。每一阶段的产出都必须能追溯到原始资料。

### Phase 1 — 资料接收与索引

1. 列出全部输入文件，为每个文件分配唯一 `source_id`（如 `src-001`）。
2. 识别文件类型、资料日期、医嘱日期、临床时间点。
3. 判断资料是否属于同一患者与同一就诊事件；如怀疑混入其他患者或其他就诊批次 → 在 `encounter.suspected_other_patient=true` 后立即停止合并并提示人工确认。
4. 检查关键字段（patient_id、admission_time、primary_diagnosis）是否齐备；否则停止并提示。

读取 `references/medication-reconciliation-standard.md` 与 `references/field-schema.md` 的 §2。

### Phase 2 — 逐份提取与证据台账

1. 每份图片或文档独立提取，不跨文件猜测。
2. 同时保存原始文字与规范化字段。
3. 每个字段必须挂接 `source_id`、`page_or_image` 与 `evidence_status`（枚举见 `field-schema.md` §1）。
4. 关键药物字段（药品名称、用法用量、用药原因、开始/停止时间）任一存在歧义 → 标 `ambiguous` 或 `missing` 并加入 `open_questions`，**不得删除整条记录**。

读取 `references/field-schema.md` 全文。

### Phase 3 — 用药时间线与最佳可能用药史

为每条药物记录分配 `category` 枚举（见 `field-schema.md` §5.1），覆盖：
- 入院前患者实际用药
- 入院后长期医嘱、临时医嘱
- 转科前后医嘱、出院医嘱
- 已停止药物、患者自带药物、非处方药/中药/保健品
- 资料中出现但无法确认当前是否使用的药物（`unconfirmed_med`）

每条 drug_record 字段定义见 `field-schema.md` §5。

### Phase 4 — 医嘱差异识别

按 `references/discrepancy-rules.md` 的 D1–D19 分类逐项扫描。每条差异必须含：差异类别、两个来源的原始片段、客观差异描述、证据状态、待核实问题、是否药师核实、是否医师确认。**模型不得自动认定任何差异一定是医嘱错误**。

读取 `references/discrepancy-rules.md` 全文。

### Phase 5 — 人工确认与重整结果

只允许如下 7 种重整结果：`继续用药 / 停药 / 加药 / 恢复用药 / 换药 / 临时暂停 / 临时调整`。

`decided_by_role` 仅可为 `pharmacist_suggestion` 或 `physician_confirmed`。**只有输入资料明确含责任医师确认意见时才能设为 `physician_confirmed`**，否则一律保持 `pharmacist_suggestion` 并在文案中标记"建议讨论 / 待医师确认"。

读取 `references/output-contract.md` §2.3。

### Phase 6 — 输出与质控

1. 输出 1：药师复核稿（Markdown）— 顶部加"药师复核草稿 / 待医师确认"。
2. 输出 2：表 A.1 待签字版（Word）— 通过 `scripts/render_form_a1.py` 渲染。
3. 输出 3：质控报告（Markdown）。
4. 三个脚本均必须通过：`scripts/validate_evidence.py`、`scripts/validate_form_a1.py`、`scripts/render_form_a1.py`。

读取 `references/output-contract.md` 全文后再执行脚本。

## Scripts

- `scripts/validate_evidence.py <input.json>` — 校验证据台账、混患、字段补全、医师确认标记。
- `scripts/validate_form_a1.py <input.json>` — 校验表 A.1 结构、签字栏空白、自带药 `*`、未经确认不得标已执行。
- `scripts/render_form_a1.py <input.json> <output.docx>` — 从 IR JSON 渲染 Word 待签字版，含水印与醒目标记。

## Assets

- `assets/form-a1-template.docx` — 表 A.1 模板骨架（依据标准 PDF 表 A.1）。
- `assets/form-a1-schema.json` — 结构化 IR JSON 的 JSON Schema 定义。

## Test Data

- `assets/test_data/case_1.json` — 综合压力测试病例（含混患、自带药、重复、冲突、模糊 OCR、缺医师确认）。
- `assets/test_data/case_2.json` — 最小冒烟病例。
- `assets/test_data/case_3.json` — 含医师确认意见的病例。

## Reference Index (Read On Demand)

| 场景 | 必读文件 |
|---|---|
| 任何执行 | `references/privacy-and-safety.md` |
| 字段命名/JSON 结构 | `references/field-schema.md` |
| 标准定义/表 A.1 字段 | `references/medication-reconciliation-standard.md` |
| 差异分类 D1–D19 | `references/discrepancy-rules.md` |
| 输出格式/签字栏/水印 | `references/output-contract.md` |
| 自检与测试 | `references/synthetic-test-cases.md` |

## Invocation Template

> 使用药物重整记录 Skill 处理我上传的资料。先建立证据台账和缺失清单，未经药师及责任医师确认，不得把建议写成已执行调整。