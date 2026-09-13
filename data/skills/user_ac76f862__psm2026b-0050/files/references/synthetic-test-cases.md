# 虚构测试病例（Synthetic Test Cases）

本文件定义 Skill 自我验证所用的虚构病例。**任何真实患者数据严禁进入测试集**。所有姓名、ID、联系方式均为虚构。

## 病例 1：综合压力测试（建议用于端到端验证）

### 1.1 患者基本信息（虚构）

```json
{
  "patient_name": "测试患者A",
  "patient_age": "72 岁",
  "patient_gender": "男",
  "patient_contact": "13800000001",
  "patient_id": "TEST-2026-001",
  "admission_time": "2026-08-01T08:30:00",
  "transfer_in_time": null,
  "discharge_time": null,
  "transfer_out_time": null,
  "primary_diagnosis": ["急性冠脉综合征", "2 型糖尿病", "慢性肾脏病 3a 期"],
  "allergies": [
    {
      "substance": "青霉素",
      "category": "药物",
      "manifestation": "皮疹",
      "source_id": "src-001",
      "page_or_image": "p.1",
      "evidence_status": "direct_visible"
    },
    {
      "substance": "海鲜",
      "category": "食物",
      "manifestation": "待核实",
      "source_id": "src-002",
      "page_or_image": "img-2",
      "evidence_status": "ambiguous"
    }
  ],
  "info_sources": ["患者/家属", "病历资料"],
  "encounter_id": "ENC-TEST-001",
  "suspected_other_patient": false
}
```

### 1.2 输入资料清单

| source_id | 文件 | 类型 | 临床时间点 | 用途 |
|---|---|---|---|---|
| src-001 | 入院记录.pdf | pdf | 2026-08-01 入院当天 | 患者基本信息、过敏史 |
| src-002 | 患者自带药照片.jpg | image | 入院当天 | 自带药物 |
| src-003 | 入院前门诊病历.pdf | pdf | 2026-07-25 | 入院前用药 |
| src-004 | 长期医嘱单.pdf | pdf | 2026-08-02 | 入院后长期医嘱 |
| src-005 | 临时医嘱单.pdf | pdf | 2026-08-03 | 临时医嘱（含重复剂量） |
| src-006 | 检验报告.pdf | pdf | 2026-08-02 | 肝肾功能（用于剂量调整判断） |
| src-007 | 转科记录（污染）.pdf | pdf | 2026-08-05 | **混入另一患者**（用于触发阻断） |

### 1.3 用药记录（覆盖差异分类）

| drug_record_id | 原始药名 | 通用名 | 类别 | 关键差异点 |
|---|---|---|---|---|
| drug-001 | 波立维 | 硫酸氢氯吡格雷 | pre_admission_home_med | 商品名 → 通用名 |
| drug-002 | 阿司匹林肠溶片 | 阿司匹林 | pre_admission_home_med | 入院前 100 mg qd |
| drug-003 | 二甲双胍片 | 盐酸二甲双胍 | patient_brought_med | 自带药，需标 `*`；eGFR 偏低待核实 |
| drug-004 | 硝苯地平控释片 30 mg | 硝苯地平 | pre_admission_home_med | 与住院医嘱剂量冲突（D5） |
| drug-005 | 阿托伐他汀钙片 | 阿托伐他汀钙 | stopped_med | 已停 6 个月，依从性差 |
| drug-006 | 硝苯地平缓释片 20 mg | 硝苯地平 | inpatient_long_term | 与 drug-004 同通用名不同剂型/剂量（D3+D4+D5） |
| drug-007 | 阿司匹林肠溶片 100 mg | 阿司匹林 | inpatient_long_term | 与 drug-002 重复（D2） |
| drug-008 | "X?? 片" | 待核实 | inpatient_long_term | OCR 模糊（ambiguous） |
| drug-009 | 万古霉素 | 盐酸万古霉素 | inpatient_temp_order | IV 明确疗程（D19） |
| drug-010 | 中药汤剂 | 待核实 | otc_supplement | 中药/保健品（otc_supplement） |
| drug-011 | 头孢氨苄 | 头孢氨苄 | stopped_med | 与青霉素过敏存在交叉过敏风险（D11） |

### 1.4 期望触发的差异

- D1（drug-001、drug-002）：入院前用药未出现在长期医嘱 → 触发遗漏
- D2（drug-002 vs drug-007）：阿司匹林重复
- D3+D4+D5（drug-004 vs drug-006）：硝苯地平剂型/规格/剂量不一致
- D10（drug-003）：自带二甲双胍未在长期医嘱体现
- D11（drug-011）：头孢氨苄与青霉素过敏交叉风险（已停，但仍需标注）
- D14（drug-008）：适应证/药名均需核实
- D19（drug-009）：万古霉素 IV 疗程需核查是否完成

### 1.5 期望触发的硬阻断

- src-007（混入其他患者）→ `suspected_other_patient=true` 时阻断渲染。
- drug-010 中药汤剂通用名缺失 → 整条 missing，不删除。

### 1.6 期望的医师确认状态

- 全部 reconciliation_outcomes 的 `decided_by_role=pharmacist_suggestion`。
- 任何 `physician_confirmed=true` 必须有"医师确认意见"原文片段作为 source_a。

### 1.7 完整 IR JSON 文件

实际测试时使用 `assets/test_data/case_1.json`（在测试阶段生成）。

## 病例 2：最小冒烟测试

仅含 1 条用药，无差异，用于验证渲染管线连通性。

```json
{
  "encounter": {
    "patient_name": "测试患者B",
    "patient_age": "45 岁",
    "patient_gender": "女",
    "patient_contact": "13800000002",
    "patient_id": "TEST-2026-002",
    "admission_time": "2026-08-10T10:00:00",
    "primary_diagnosis": ["高血压"],
    "allergies": [],
    "info_sources": ["病历资料"],
    "encounter_id": "ENC-TEST-002",
    "suspected_other_patient": false
  },
  "sources": [{"source_id": "src-001", "file_name": "入院记录.pdf"}],
  "drug_records": [
    {
      "record_id": "drug-001",
      "original_name": "苯磺酸氨氯地平片",
      "generic_name": "氨氯地平",
      "brand_name": null,
      "dosage_form": "片剂",
      "strength": "5 mg",
      "route": "口服",
      "dose": "5 mg",
      "frequency": "每日 1 次",
      "administration_time": "固定时间",
      "indication": "高血压",
      "start_time": "2026-08-10",
      "stop_time": null,
      "stop_reason": null,
      "patient_brought": false,
      "adherence": "良好",
      "source_id": "src-001",
      "page_or_image": "p.1",
      "category": "inpatient_long_term",
      "current_status": "继续用药",
      "evidence_status": "direct_visible",
      "open_questions": []
    }
  ],
  "discrepancies": [],
  "reconciliation_outcomes": [
    {
      "drug_record_id": "drug-001",
      "result": "继续用药",
      "reason": "高血压基础治疗，入院后继续",
      "decided_at": null,
      "decided_by_role": "pharmacist_suggestion",
      "source_id": "src-001"
    }
  ],
  "open_questions": []
}
```

## 病例 3：医师确认存在（用于验证签字栏处理）

与病例 1 类似，但 `reconciliation_outcomes[0].decided_by_role="physician_confirmed"` 且 `decided_at` 与 `decided_by_role` 与原始医师意见片段一致。

## 测试执行清单

- [ ] validate_evidence.py 病例 1 → 应在 src-007 阻断（退出码 4）
- [ ] validate_evidence.py 病例 1（移除 src-007 后） → 应通过（退出码 0）
- [ ] validate_form_a1.py 病例 1 → 应通过且签字栏空白
- [ ] render_form_a1.py 病例 2 → 应生成 .docx，含表格与水印
- [ ] 病例 3 → 应通过 validate_form_a1.py
- [ ] PHI 模式检查 → 不得出现真实姓名/电话/身份证号