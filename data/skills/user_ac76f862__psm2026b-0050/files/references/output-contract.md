# 输出契约（Output Contract）

本文件定义 Skill 的两类正式输出：① **药师复核稿**（JSON + Markdown 报告）；② **表 A.1 待签字版**（Word .docx）。所有输出必须通过 `validate_evidence.py` 与 `validate_form_a1.py` 的校验。

## 1. 输入：结构化 JSON（Intermediate Representation, IR）

```json
{
  "schema_version": "1.0",
  "encounter": { ... 见 references/field-schema.md §2 ... },
  "sources": [ { ... }, ... ],
  "evidence": [
    {
      "field_path": "patient.name",
      "value": "张某某",
      "raw_text": "患者：张某某",
      "source_id": "src-001",
      "page_or_image": "p.1",
      "evidence_status": "direct_visible",
      "conflict_with": [],
      "pharmacist_verified": false,
      "physician_confirmed": false
    }
  ],
  "drug_records": [ ... ],
  "discrepancies": [ ... ],
  "reconciliation_outcomes": [ ... ],
  "open_questions": [ ... ],
  "qc_report": { ... }
}
```

完整字段定义见 `field-schema.md`。

## 2. 输出 1：药师复核稿

### 2.1 文件名

- `<patient_id>_<encounter_id>_reconciliation_review.md`
- 例：`H2026001_ENC001_reconciliation_review.md`

### 2.2 必备小节

1. **患者与就诊摘要**——姓名/ID/主要诊断/就诊时间窗/信息来源/怀疑混入其他患者（必须明确 false 才继续）。
2. **过敏史**——过敏物质、过敏表现、来源、是否待核实。
3. **入院前用药**——表格列出全部入院前用药与自带药。
4. **住院长期医嘱**——表格列出目标时间点长期医嘱。
5. **临时医嘱**——按时间顺序列出。
6. **已停止药物**——含停止时间与原因（如有）。
7. **差异识别结果**——按 D1–D19 分类汇总，每条含客观差异与待核实问题。
8. **重整建议（草稿）**——每条药物的当前状态、建议动作、依据。
9. **待核实问题清单**——聚合 evidence 与 discrepancies 中的 open_questions。
10. **签字栏**——明示"本稿为药师复核草稿，未经责任医师确认前不得作为执行依据"。

### 2.3 强制标记

- 顶部必须有醒目标记：**"药师复核草稿 / 待医师确认"**。
- 任何 `decided_by_role=pharmacist_suggestion` 的调整都必须标记"建议讨论"。

## 3. 输出 2：表 A.1 待签字版（Word）

### 3.1 文件名

- `<patient_id>_<encounter_id>_form_A1.docx`
- 例：`H2026001_ENC001_form_A1.docx`

### 3.2 表头字段（顺序与命名遵循标准 PDF）

| 表头单元格 | 取值来源 |
|---|---|
| 患者姓名 | encounter.patient_name（仅当 evidence_status∈{direct_visible, cross_confirmed, pharmacist_verified, physician_confirmed}） |
| 年龄 | encounter.patient_age |
| 性别 | encounter.patient_gender |
| 联系方式 | encounter.patient_contact 或"待核实" |
| ID 号 | encounter.patient_id |
| 入院时间/转入时间 | encounter.admission_time / transfer_in_time；两者至少其一 |
| 出院时间/转出时间 | encounter.discharge_time / transfer_out_time；可空 |
| 主要诊断 | encounter.primary_diagnosis 拼接（多诊断用"、"分隔） |
| 过敏史 | encounter.allergies 汇总；缺失表现写"待核实" |
| 信息来源 | encounter.info_sources 拼接 |

### 3.3 药物列表列（顺序与命名遵循标准 PDF）

1. 药品名称（通用名）——patient_brought=true 时名称后追加 `*`
2. 用法用量
3. 用药原因
4. 开始时间
5. 停止时间
6. 备注（药物重整建议及理由）

### 3.4 必备表下注释（不得删除）

> 注 1.列表中应列出患者全部用药，开展重整的药物请注明重整建议及重整理由。
> 注 2.如有患者自带药品，请在药品名称后加"\*"。
> 注 3.如因转科需要暂停或调整用药，请注明。

### 3.5 签字栏

```
药师签字：_______________   医师签字：______________   日期：_________________
```

- 三个下划线段必须保持空白（仅空白字符）。
- 不得把模型名称、AI 标识填入任何字段。

### 3.6 草稿/待确认醒目标记

- 在表格上方打印一行红字加粗：**"药师复核草稿 / 待医师确认"**（医师确认后应去除本行，由人工切换为正式版）。
- 表格底部添加水印：**"DRAFT - PHARMACIST REVIEW / AWAITING PHYSICIAN CONFIRMATION"**。

### 3.7 渲染规格

- 页面：A4，方向纵向
- 页边距：上下 2.0 cm，左右 2.5 cm
- 中文字体：宋体（正文）/ 黑体（标题）
- 英文字体：Times New Roman
- 表格边框：全部实线 0.5 pt
- 行数：根据 `drug_records` 数量动态扩展，最少预留 10 行（标准要求"列出患者全部用药"）
- 分页：表头跨页时自动重复
- 字号：表头 12 pt 加粗；药物列表 11 pt；注释 10 pt 斜体

## 4. 输出 3：质控报告（QC Report）

### 4.1 文件名

- `<patient_id>_<encounter_id>_qc_report.md`

### 4.2 必备小节

1. **完整性检查**——必填字段缺失清单（应为 0）
2. **证据追溯检查**——无来源字段数量（应为 0）
3. **冲突字段清单**
4. **疑似补全字段清单**（应为 0）
5. **混患检查结果**
6. **自带药品标记检查**
7. **签字栏空白检查**
8. **统计**：录入药物条数、差异条数、待核实问题条数
9. **渲染文件清单与字节数**

## 5. 调用入口

- `scripts/render_form_a1.py <input.json> <output.docx>`：渲染表 A.1
- `scripts/validate_evidence.py <input.json>`：校验证据台账
- `scripts/validate_form_a1.py <input.json>`：校验表 A.1 结构与签字栏
- 三个脚本可串联：`validate_evidence.py && validate_form_a1.py && render_form_a1.py`

## 6. 失败模式与退出码

| 脚本 | 退出码 | 含义 |
|---|---|---|
| validate_evidence.py | 0 | 通过 |
| validate_evidence.py | 2 | 必填字段缺失 |
| validate_evidence.py | 3 | 关键药物字段无来源或疑似补全 |
| validate_evidence.py | 4 | 混患阻断 |
| validate_evidence.py | 5 | physician_confirmed 标记冲突 |
| validate_form_a1.py | 0 | 通过 |
| validate_form_a1.py | 2 | 表 A.1 结构不完整 |
| validate_form_a1.py | 3 | 签字栏非空 |
| validate_form_a1.py | 4 | 患者自带药品未标 * |
| validate_form_a1.py | 5 | 未经医师确认被标记为已执行 |
| render_form_a1.py | 0 | 成功 |
| render_form_a1.py | 2 | 渲染输入校验失败 |