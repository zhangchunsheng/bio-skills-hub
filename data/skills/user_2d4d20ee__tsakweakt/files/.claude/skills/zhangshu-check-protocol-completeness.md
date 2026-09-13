---
name: zhangshu-check-protocol-completeness
description: Detect whether a clinical research protocol exists, extract or accept its normalized sections, and deterministically validate required protocol components before feasibility assessment. Use when a project enters the top-level “有方案/无方案” decision, when an existing DOCX/PDF/Markdown/text protocol must be checked for completeness, or when a structured protocol JSON must be routed to feasibility assessment or returned for revision.
---

# 研究方案完整性校验

检查项目是否已有研究方案，并将方案路由到“继续可行性评估”或“返回修改”。语义模型只负责抽取候选内容；最终通过与否必须由版本化规则和确定性脚本决定。

## Resource routing

- 定义字段映射、存在性阈值或研究类型例外时读取 `references/completeness-rules.md`。
- 对接应用 Tool、编排器或前端时读取 `references/tool-contracts.md`。
- 构造或校验标准化输入输出时读取 `references/protocol-component-schema.md`。
- 生成统一校验结果时复用 `assets/validation-report-template.json`。

## Workflow

1. 调用 `detect_protocol_document` 检查项目 manifest 或 artifact 列表。需要本地确定性检查时运行 `scripts/detect_protocol_document.py`。
2. 未找到方案时输出 `NO_PROTOCOL`，路由到方案创建流程；不得把“未找到”误报为“方案不完整”。
3. 找到方案后运行 `scripts/extract_protocol_components.py`，从 DOCX、Markdown、TXT、JSON 或可解析 PDF 中提取候选组件，并记录来源位置。解析失败必须产生 `EXTRACTION_UNCERTAIN`。
4. 将抽取结果规范化为 `references/protocol-component-schema.md` 中的 JSON。不得根据标题存在就推断正文有效。
5. 调用 `validate_picos_completeness`；需要确定性执行时运行 `scripts/validate_picos_completeness.py`。P/I/C/O/S 全部是硬编码必填项，不允许豁免。
6. 调用 `validate_protocol_completeness`；需要确定性执行时运行 `scripts/validate_protocol_completeness.py`。
7. 若缺失任一必要组件，产出“完整性校验不通过”，输出分支 `M`、`RETURN_FOR_REVISION`，并生成弹窗“方案不完整，缺少：[缺失项]”。
8. 若全部必要组件齐全，产出“完整性校验通过”，输出分支 `S`、下一节点 `0.2` 和任务 `ASSESS_FEASIBILITY`。

## Tool boundaries

- `detect_protocol_document`：只判断方案产物是否存在并选择候选文档。
- `extract_protocol_components`：由 `scripts/extract_protocol_components.py` 实现，只产出候选事实和证据位置。
- `validate_picos_completeness`：确定性检查 P/I/C/O/S。
- `validate_protocol_completeness`：确定性聚合所有必填组件。
- `build_protocol_validation_message`：由主校验脚本的 `message` 字段实现。
- `route_after_protocol_validation`：属于编排步骤，直接读取主校验脚本的路由字段，不作为独立 Tool。

## Mandatory rules

默认规则集 `protocol-completeness-v1` 要求：研究背景与目的、P/I/C/O/S、研究设计类型、纳入标准、排除标准、样本量计算依据、主要终点、次要终点、统计分析方法和参考文献列表。

- 空白字符串以及递归后没有有效内容的数组、对象和 `null` 均视为缺失。
- PICOS 中每个要素必须分别报告，不能以总体 `picos` 对象存在替代子项校验。
- 样本量只写最终数字而没有方法、参数或依据时，视为“依据缺失”。
- 终点只有名称但缺少定义时可先记警告；主要或次要终点整体不存在时记为阻断项。
- 参考文献必须至少包含一条可识别条目；不得生成或补造文献。
- 本节点采用固定硬编码清单，不接受研究类型例外或调用方豁免；规则变化必须发布新的规则集版本。

## Output contract

始终输出机器可读校验报告，至少包含：

- `valid`、`status`、`validation_result`、`branch`、`rule_set`
- `protocol_artifact_id`
- `present_items`、`missing_items`、`warnings`
- `next_node`、`next_task`
- `popup_required`、`message`

当不通过时，`missing_items` 每项必须包含稳定的 `code`、中文 `label`、`field` 和 `severity`，便于前端展示与后续修改定位。

## Safety

- 不因章节标题相似就判定内容完整。
- 不生成缺失的研究设计、样本量依据、终点或参考文献以使校验通过。
- 不把完整性通过表述为科学合理性、伦理批准或可行性通过。
- 原文无法可靠解析时返回 `EXTRACTION_UNCERTAIN`，要求复核，不得静默通过。
