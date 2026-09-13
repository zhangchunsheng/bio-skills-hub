# Tool contracts

## `detect_protocol_document`

输入项目 `artifacts` 或 `manifest.artifacts`；输出 `exists`、`branch`、`protocol_artifact_id`、`document_path`。

## `extract_protocol_components`

输入 `document_path`；运行 `scripts/extract_protocol_components.py`。支持 DOCX、Markdown、TXT、JSON；安装 `pypdf` 后支持文本型 PDF。输出符合组件 Schema 的 `components`、证据位置和 `extraction_warnings`。该 Tool 不输出最终通过结论；解析器不可用、文件不可访问或无文本时返回 `EXTRACTION_UNCERTAIN`。

## `validate_picos_completeness`

输入标准化 PICOS；按硬编码 P/I/C/O/S 清单输出 `valid`、`status`、`missing_items`，不接受豁免。

## `validate_protocol_completeness`

输入标准化方案组件；按固定必要组件清单输出完整校验报告。退出码 `0` 表示“完整性校验通过”，`1` 表示“完整性校验不通过”。

## `build_protocol_validation_message`

由 `validate_protocol_completeness.py` 的 `message` 字段提供。若不通过，按去重后的 `missing_items[].label` 生成“方案不完整，缺少：A、B”。不得更改校验结论。

## `route_after_protocol_validation`

这是编排步骤而非独立 Tool。直接使用校验报告中的 `branch`、`next_node` 和 `next_task`：`valid=true` 路由 `S → 0.2/ASSESS_FEASIBILITY`；否则路由 `M → 0.1/RETURN_FOR_REVISION`。
