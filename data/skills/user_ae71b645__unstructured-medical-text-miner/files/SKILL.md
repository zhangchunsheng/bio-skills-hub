---
slug: unstructured-medical-text-miner
displayName: 非结构化医疗文本挖掘器
version: 1.1.0
description: 从MIMIC-IV非结构化临床文本中提取诊断逻辑。适用于医疗文本挖掘、临床NLP分析、NOTEEVENTS实体识别（NER）与关系抽取任务。
license: MIT
author: AIPOCH
---
# 非结构化医疗文本挖掘器（Skill ID: 213）

## 适用场景

- 当任务需要从MIMIC-IV非结构化临床文本中挖掘诊断逻辑时，使用本技能。
- 当需要对证据洞察类任务进行明确假设、限定范围、生成可复现输出格式时使用。
- 当需要对缺失输入、执行错误或部分证据提供有文档记录的备用路径时使用。

## 核心功能

- 聚焦于以下范围的工作流：从MIMIC-IV非结构化临床文本中挖掘诊断逻辑。
- 可执行入口：`scripts/main.py`（主脚本）及 `scripts/__init__.py`（包入口）。
- `references/` 目录提供任务专项参考材料。
- 结构化执行路径，确保输出结果一致且可审查。

## 依赖项

```
pandas>=1.3.0
spacy>=3.4.0
scispacy>=0.5.1
negspacy
```

## 示例用法

```bash
cd "unstructured-medical-text-miner"
python -m py_compile scripts/main.py
python scripts/main.py --help
```

示例执行步骤：
1. 确认用户输入、输出路径及必要的配置值。
2. 如有需要，修改 `config.yaml` 中的参数设置。
3. 使用验证后的输入运行 `python scripts/main.py`。
4. 检查生成的输出，并在返回最终结果时明确说明所有假设。

## 实现细节

- 执行模型：验证请求 → 选择封装的工作流 → 生成有界可交付物。
- 输入控制：在执行任何脚本前，确认源文件、范围限制、输出格式和验收标准。
- 主要实现：`scripts/main.py` 中的 `MedicalTextMiner` 类。
- 参考指南：`references/` 包含支持规则、提示或检查清单。
- 需提前明确的参数：输入路径、输出路径、范围过滤器、阈值及领域特定约束。
- 输出规范：保持结果可复现，明确标注假设，避免未记录的副作用。

## 快速检查

使用以下命令验证脚本入口点可被解析：

```bash
python -m py_compile scripts/main.py
```

## 审计命令

以下为具体的验证命令，刻意保持自包含，避免占位符路径：

```bash
python -m py_compile scripts/main.py
python scripts/main.py --help
python scripts/main.py -h
```

## 工作流

1. 在进行详细工作前，确认用户目标、所需输入和不可妥协的约束条件。
2. 验证请求是否符合已记录的范围，若任务需要不支持的假设则提前停止。
3. 使用封装的脚本路径或有文档记录的推理路径，仅使用实际可用的输入。
4. 返回结构化结果，分别列出假设、可交付物、风险和未解决事项。
5. 若执行失败或输入不完整，切换到备用路径并明确说明阻止完成的原因。

## 概述

挖掘MIMIC-IV中长期被忽视的文本数据，提取非结构化诊断逻辑、医嘱详情和病程记录。

## 目的

MIMIC-IV数据库包含大量结构化数据（生命体征、实验室结果等），但其真正的临床价值往往隐藏在非结构化文本中：
- 出院摘要中的诊断推理链
- 影像报告中的细微发现描述
- 病程记录中的治疗决策逻辑
- 医嘱中的个性化用药考量

本技能提供完整的文本挖掘工具链，将原始医疗文本转化为可分析的结构化洞察。

## 功能特性

### 1. 文本提取
- **NOTEEVENTS**：从MIMIC-IV NOTE模块提取临床记录
- **放射报告**：提取影像诊断文本
- **ECG报告**：解析心电图解读文本
- **出院摘要**：提取完整诊断和治疗过程

### 2. 信息抽取
- **实体识别（NER）**：疾病、症状、药物、手术操作、解剖部位
- **关系抽取**：药物-疾病治疗关系、症状-疾病诊断关系
- **时间线抽取**：事件发生时间、疾病进展顺序
- **否定检测（Negation Detection）**：识别被否定的临床发现（如"no fever"无发热）

### 3. 临床逻辑解析
- **诊断推理链**：症状 → 检查 → 诊断的推理路径
- **治疗决策树**：药物选择和剂量调整的临床依据
- **疾病进展**：疾病进展和转归描述

### 4. 结构化输出
- FHIR兼容的临床文档格式
- 知识图谱友好的三元组格式
- 时序事件序列

## 用法

```python
from scripts.main import MedicalTextMiner

# 初始化挖掘器
miner = MedicalTextMiner()

# 加载MIMIC-IV记录数据
miner.load_notes(notes_path="path/to/noteevents.csv")

# 获取特定患者的所有文本记录
patient_texts = miner.get_patient_texts(subject_id=10000032)

# 执行完整的信息抽取
insights = miner.extract_insights(
    text=patient_texts[0].get('note_text', ''),
    extract_entities=True,
    extract_relations=True,
    extract_timeline=True
)
```

## 输入

### 数据来源
- MIMIC-IV NOTEEVENTS表（csv/parquet格式）
- 出院摘要文件
- 影像报告文件
- 自定义医疗文本

### 字段要求
| 字段名 | 描述 | 是否必填 |
|--------|------|----------|
| subject_id | 患者唯一标识符 | 是 |
| hadm_id | 住院记录标识符 | 否 |
| note_type | 记录类型（DS/RR/ECG等） | 是 |
| note_text | 记录文本内容 | 是 |
| charttime | 记录时间 | 否 |

## 输出

### 实体抽取结果
```json
{
  "entities": [
    {
      "text": "acute myocardial infarction",
      "type": "DISEASE",
      "start": 156,
      "end": 183,
      "confidence": 0.94
    },
    {
      "text": "aspirin 81mg",
      "type": "MEDICATION",
      "start": 245,
      "end": 257,
      "attributes": {
        "dose": "81mg",
        "frequency": "daily"
      }
    }
  ]
}
```

### 临床逻辑图
```json
{
  "clinical_logic": {
    "presenting_complaint": "chest pain",
    "differential_diagnoses": ["ACS", "PE", "aortic dissection"],
    "workup": ["ECG", "troponin", "CTA chest"],
    "final_diagnosis": "STEMI",
    "treatment_plan": ["PCI", "dual antiplatelet"]
  }
}
```

### 时序事件
```json
{
  "timeline": [
    {
      "time": "2020-03-15 08:30",
      "event": "admission",
      "description": "presented with chest pain"
    },
    {
      "time": "2020-03-15 09:15",
      "event": "ECG",
      "description": "ST elevation in V1-V4"
    }
  ]
}
```

## 配置

```yaml
# config.yaml
extraction:
  entity_types: ["DISEASE", "SYMPTOM", "MEDICATION", "PROCEDURE", "ANATOMY"]
  relation_types: ["TREATS", "CAUSES", "CONTRAINDICATED_WITH"]
  enable_negation_detection: true
  
models:
  ner_model: "en_core_sci_lg"  # 或 "en_core_sci_scibert"
  relation_model: null
  
output:
  format: "json"  # json/fhir/kg
  include_raw_text: false
```

## CLI 用法

```text
# 处理单个文件
python scripts/main.py \
  --input notes.csv \
  --output extracted.json \
  --extract all

# 处理特定患者
python scripts/main.py \
  --subject-id 10000032 \
  --input mimic_noteevents.csv \
  --output patient_insights.json

# 直接处理文本片段
python scripts/main.py \
  --sample-text "Patient presented with chest pain. No fever."
```

## 参考资料

1. MIMIC-IV临床数据库：https://physionet.org/content/mimiciv/
2. scispaCy（医疗NLP库）：https://allenai.github.io/scispacy/
3. NegEx/negspacy（否定检测）
4. FHIR临床文档规范

## 作者信息

Skill ID: 213
类别：医疗数据挖掘
复杂度：高级

## 风险评估

| 风险指标 | 评估 | 级别 |
|----------|------|------|
| 代码执行 | 本地执行Python脚本 | 中 |
| 网络访问 | 无外部API调用 | 低 |
| 文件系统访问 | 读取输入文件，写入输出文件 | 中 |
| 指令篡改 | 标准提示词指南 | 低 |
| 数据暴露 | 输出文件保存至工作区 | 低 |

## 安全检查清单

- [ ] 无硬编码凭据或API密钥
- [ ] 无未授权的文件系统访问（../）
- [ ] 输出不暴露敏感信息
- [ ] 已部署提示词注入防护
- [ ] 输入文件路径已验证（无../遍历）
- [ ] 输出目录限制在工作区内
- [ ] 脚本在沙盒环境中执行
- [ ] 错误消息已清理（不暴露堆栈跟踪）
- [ ] 依赖项已审计

## 前置条件

```text
# Python依赖安装
pip install -r requirements.txt
```

## 评估标准

### 成功指标
- [ ] 成功执行主要功能
- [ ] 输出符合质量标准
- [ ] 优雅处理边界情况
- [ ] 性能可接受

### 测试用例
1. **基本功能**：标准输入 → 预期输出
2. **边界情况**：无效输入 → 优雅错误处理
3. **性能测试**：大数据集 → 可接受的处理时间

## 输出要求

每个最终响应在相关时应明确以下内容：

- 目标或请求的可交付物
- 使用的输入和引入的假设
- 工作流或决策路径
- 核心结果、建议或工件
- 约束条件、风险、注意事项或验证需求
- 未解决事项和下一步检查

## 错误处理

- 若缺少必要输入，明确说明缺少哪些字段，并仅请求最少量的额外信息。
- 若任务超出已记录的范围，停止执行而非猜测或静默扩展任务范围。
- 若 `scripts/main.py` 失败，报告失败点，总结仍可安全完成的内容，并提供手动备用方案。
- 不得伪造文件、引用、数据、搜索结果或执行结果。

## 输入验证

本技能接受符合 `unstructured-medical-text-miner` 已记录用途且包含足够上下文可安全完成工作流的请求。

当请求超出范围、缺少关键输入或需要不支持的假设时，不得继续工作流。请回复：

> `unstructured-medical-text-miner` 仅处理其已记录的工作流。请提供缺失的必要输入或切换至更合适的技能。

## 参考文档

- [references/audit-reference.md](references/audit-reference.md) - 支持的范围、审计命令和备用边界

## 响应模板

对非简单请求使用以下固定结构：

1. 目标
2. 收到的输入
3. 假设
4. 工作流
5. 可交付物
6. 风险与限制
7. 后续检查

对于简单请求，可以压缩结构，但在影响正确性时仍需明确说明假设和限制。
