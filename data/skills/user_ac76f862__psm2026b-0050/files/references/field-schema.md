# 字段模式（Field Schema）

本文件定义本 Skill 所使用的全部结构化字段。字段命名采用 JSON Key + 中文含义双轨；JSON Key 用于程序校验，中文含义用于药师与医师阅读。所有字段均需携带证据状态。

## 1. 全局证据状态枚举

```text
direct_visible          直接可见（来源资料中字面可读）
cross_confirmed         交叉确认（多份资料互证）
conflict                存在冲突（多份资料不一致）
ambiguous               模糊不清（OCR/手写难以判读）
missing                 未提供（资料中无该字段）
pharmacist_verified     人工核实（药师已确认）
physician_confirmed     医师确认（责任医师已签字或口头确认）
```

## 2. 患者与就诊事件

| 字段 | JSON Key | 类型 | 必填 | 说明 |
|---|---|---|---|---|
| 患者姓名 | patient_name | string | 是 | 来自入院记录/腕带/身份证件 |
| 年龄 | patient_age | string\|int | 是 | 可为 "65 岁" 或 65 |
| 性别 | patient_gender | string | 是 | 男/女/其他 |
| 联系方式 | patient_contact | string | 否 | 电话/紧急联系人 |
| ID 号 | patient_id | string | 是 | 住院号/病历号 |
| 入院时间 | admission_time | string | 视情 | ISO 8601 日期时间 |
| 转入时间 | transfer_in_time | string | 视情 | ISO 8601 日期时间 |
| 出院时间 | discharge_time | string | 视情 | ISO 8601 日期时间 |
| 转出时间 | transfer_out_time | string | 视情 | ISO 8601 日期时间 |
| 主要诊断 | primary_diagnosis | string[] | 是 | 数组，按主次排列 |
| 过敏史 | allergies | array | 否 | 见 §3 |
| 信息来源 | info_sources | string[] | 是 | 患者/家属 / 病历资料 / 其他 |
| 就诊事件标识 | encounter_id | string | 是 | Skill 内部为本次合并分配的唯一 ID |
| 怀疑混入其他患者 | suspected_other_patient | bool | 是 | true 时阻断合并 |

## 3. 过敏史对象

```json
{
  "substance": "青霉素",
  "category": "药物",
  "manifestation": "皮疹",
  "source_id": "src-001",
  "page_or_image": "p.2",
  "evidence_status": "direct_visible"
}
```

- 缺少过敏表现（manifestation）时，必须保留 substance 但 manifestation 写"待核实"。
- 已知过敏但缺失物质名 → 直接阻断并提示人工补充。

## 4. 证据台账字段

每一份资料对应一个 `source` 对象，全部结构化字段均挂接 source。

```json
{
  "source_id": "src-001",
  "file_name": "入院记录.pdf",
  "file_type": "pdf",
  "patient_or_encounter": "本次患者 / 本次就诊",
  "doc_date": "2026-08-01",
  "clinical_timepoint": "入院当天",
  "page_or_image": "p.1",
  "raw_text": "原文片段",
  "evidence_status": "direct_visible",
  "conflict_with": ["src-003"],
  "pharmacist_verified_by": null,
  "pharmacist_verified_at": null,
  "physician_confirmed_by": null,
  "physician_confirmed_at": null
}
```

## 5. 用药记录（Drug Record）

每条用药至少包含以下字段。**禁止缺字段降级为整条删除**——若关键字段缺失，整条标记 `evidence_status=missing` 并写入 `open_questions`。

```json
{
  "record_id": "drug-001",
  "original_name": "波立维",
  "generic_name": "硫酸氢氯吡格雷",
  "brand_name": "波立维",
  "dosage_form": "片剂",
  "strength": "75 mg",
  "route": "口服",
  "dose": "75 mg",
  "frequency": "每日 1 次",
  "administration_time": "早餐后",
  "indication": "冠心病 二级预防",
  "start_time": "2025-03-12",
  "stop_time": null,
  "stop_reason": null,
  "patient_brought": true,
  "adherence": "良好",
  "source_id": "src-002",
  "page_or_image": "p.3",
  "category": "inpatient_long_term",
  "current_status": "继续用药",
  "evidence_status": "direct_visible",
  "open_questions": []
}
```

### 5.1 category 枚举

```text
pre_admission_home_med     入院前患者实际用药
inpatient_long_term        住院长期医嘱
inpatient_temp_order       住院临时医嘱
pre_transfer_med           转科前用药
post_transfer_med          转科后用药
discharge_med              出院医嘱
stopped_med                已停止药物
patient_brought_med        患者自带药物
otc_supplement             非处方药/中药/保健品
unconfirmed_med            资料出现但无法确认当前是否使用
```

### 5.2 current_status 枚举

```text
继续用药 / 停药 / 加药 / 恢复用药 / 换药 / 临时暂停 / 临时调整
```

### 5.3 必须保留字段规则

- original_name 必须始终保留，不得被 generic_name 覆盖。
- 商品名 → 通用名 的转换仅在证据明确时执行；存疑时保留两者并存。
- 关键字段（药品名称、用法用量、用药原因、开始/停止时间）任一为空 → 整条标记 missing 并加入 open_questions，禁止删除。

## 6. 差异记录（Discrepancy）

```json
{
  "discrepancy_id": "disc-001",
  "drug_generic_name": "硝苯地平",
  "category": "dose_inconsistency",
  "source_a": {"source_id": "src-002", "raw_text": "硝苯地平控释片 30 mg qd"},
  "source_b": {"source_id": "src-005", "raw_text": "硝苯地平缓释片 20 mg bid"},
  "objective_diff": "同一通用名，剂型与剂量、频次均不同",
  "evidence_status": "conflict",
  "needs_answer_from": ["patient", "physician"],
  "open_questions": ["请问患者实际在家服用的是控释片 30 mg qd 还是缓释片 20 mg bid？"],
  "pharmacist_verified": false,
  "physician_confirmed": false,
  "proposed_action": "建议讨论"
}
```

完整差异分类见 `discrepancy-rules.md`。

## 7. 重整结果（Reconciliation Outcome）

每条药物记录可附带一个 outcome 对象：

```json
{
  "drug_record_id": "drug-001",
  "result": "继续用药",
  "reason": "患者长期服用，本次住院继续维持",
  "decided_at": null,
  "decided_by_role": "pharmacist_suggestion | physician_confirmed",
  "source_id": "src-002"
}
```

- `decided_by_role=physician_confirmed` 仅在输入资料明确含医师确认意见时设置；否则只能是 `pharmacist_suggestion`。
- `result` 取值见 §5.2。