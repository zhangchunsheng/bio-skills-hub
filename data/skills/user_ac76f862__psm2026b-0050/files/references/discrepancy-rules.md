# 差异分类与识别规则（Discrepancy Rules）

本文件定义入院前实际用药与目标时间点医嘱之间的差异分类，每一类均需附带证据、原始片段与待核实问题。**模型不得自动认定任何差异一定是医嘱错误**——所有差异均以"建议讨论"形式提交，由药师核实、责任医师确认。

## 1. 分类总表

| 编号 | category 枚举 | 含义 | 典型证据需求 |
|---|---|---|---|
| D1 | omission | 药物遗漏：患者仍在用但医嘱未体现 | 入院前用药记录 vs 当前医嘱 |
| D2 | duplication | 药物重复：同通用名出现在两个条目 | 医嘱内或医嘱间对比 |
| D3 | drug_inconsistency | 药品不一致：通用名相同但药品/厂家不同 | 名称原文比对 |
| D4 | form_or_strength | 剂型或规格不一致 | 剂型、规格字段比对 |
| D5 | dose_inconsistency | 剂量不一致 | 单次剂量字段比对 |
| D6 | frequency_inconsistency | 频次不一致 | 频次字段比对 |
| D7 | route_inconsistency | 给药途径不一致 | 给药途径字段比对 |
| D8 | start_or_stop_time | 开始/停止时间不一致 | 时间字段比对 |
| D9 | stopped_but_still_ordered | 已停药物仍出现在当前医嘱 | 停止时间 vs 当前医嘱 |
| D10 | patient_still_uses_but_not_ordered | 患者仍在使用但当前医嘱未体现 | 入院前用药 vs 当前医嘱 |
| D11 | allergy_or_contraindication | 过敏或禁忌相关 | 过敏史 vs 当前用药 |
| D12 | drug_drug_or_food_interaction | 潜在药物—药物/药物—食物相互作用 | 当前所有用药间 |
| D13 | incompatibility | 配伍问题 | 同组液体/输注顺序 |
| D14 | indication_to_verify | 适应证需核实 | 用药原因缺失或不明确 |
| D15 | renal_hepatic_risk | 肝肾功能相关风险 | 检验结果 vs 用药剂量 |
| D16 | special_population_risk | 特殊人群用药风险 | 年龄/妊娠/哺乳/肝肾功能 |
| D17 | special_form_or_device | 特殊剂型或装置使用问题 | 吸入剂、胰岛素笔等 |
| D18 | procedure_pause_resume | 特殊检查/操作前后停药与恢复 | 操作时间 vs 用药时间 |
| D19 | iv_or_defined_course | 静脉/明确疗程药物是否继续 | 医嘱疗程 vs 实际 |

## 2. 字段差异识别算法（确定性）

```text
For each drug record in pre_admission_home_med or patient_brought_med:
  For each drug record in inpatient_long_term at the target timepoint:
    if generic_name 相等:
      if form_or_strength 不同 → D4
      if dose 不同 → D5
      if frequency 不同 → D6
      if route 不同 → D7
    if generic_name 相似（如 "硝苯地平" 与 "硝苯地平控释片"）：
      触发 D3 + 上述二级差异
  if drug 出现在 pre_admission 但未出现在 inpatient_long_term:
    → D1 或 D10（视是否患者自带）
  if drug 已 stopped_med 但仍在 inpatient_long_term:
    → D9

For all inpatient_long_term drugs:
  for each pair (a, b):
    if interaction_risk(a, b) == true → D12
    if shared_route and incompatibility(a, b) == true → D13

For each drug record:
  if allergy.substance == drug.generic_name → D11
  if drug.indication 缺失或空 → D14
  if drug 需要肝/肾功能调整剂量 but latest lab 未提供 → D15
  if patient 年龄/性别/妊娠状态触发提示 → D16
  if drug.form ∈ 特殊剂型集合 → D17
  if drug 与 procedure 时间冲突 → D18
  if drug route=IV 或 course_defined 但无 stop_time → D19
```

> "interaction_risk" 等判断依赖药物知识库；本 Skill 不内置知识库，需在结构化 JSON 中显式提供 `flagged_risks` 字段，由人工标注或外部药物数据库检索结果导入。

## 3. 差异记录必备字段

每条 discrepancy 至少包含（详见 `field-schema.md` §6）：

- discrepancy_id
- drug_generic_name
- category（取值见 §1）
- source_a、source_b（原始片段 + 来源编号）
- objective_diff（模型发现的客观差异；不得写主观判断）
- evidence_status（conflict / ambiguous / cross_confirmed 等）
- needs_answer_from（patient / family / pharmacist / physician）
- open_questions
- pharmacist_verified（bool）
- physician_confirmed（bool）
- proposed_action（建议讨论 / 待医师确认 / 已确认）

## 4. 阻断条件（Hard Stops）

以下差异必须升级为阻断，不进入表 A.1 自动渲染：

1. 怀疑混入其他患者资料（`suspected_other_patient=true`）。
2. 患者 ID 号缺失或两份资料 ID 号不一致。
3. 缺失责任医师确认却被标记为 `physician_confirmed`。
4. 关键字段无来源（如凭空补全药名/剂量）。
5. 患者自带药品未正确标记 `*`。

## 5. 与重整结果的对应

| 差异类别 | 典型对应重整结果（仍需医师确认） |
|---|---|
| D1 / D10 | 加药 |
| D2 | 停药 |
| D3 | 换药 |
| D4 / D5 / D6 / D7 / D8 | 换药 或 临时调整 |
| D9 | 停药 |
| D11 / D12 / D13 | 停药 或 换药 |
| D14 | 待核实 |
| D15 / D16 / D19 | 临时调整 |
| D17 / D18 | 临时暂停 / 临时调整 |

> 表中"典型对应"仅作参考；最终结果由药师与责任医师共同确认。