---
slug: medical-translation
displayName: 医学术语精准翻译工具
version: 1.1.0
description: 医学术语和文本的精准翻译，支持多语言医学术语互译（中英、英西、英法等），确保医学概念的准确传达。用于医学文献翻译、国际合作和多语言病历处理。触发短语："医学翻译""术语翻译""medical translation""病历翻译"。
license: MIT
author: AIPOCH
---

# 医学术语精准翻译工具

专注于医学术语和医学文本的精准翻译，确保医学概念在不同语言间准确传达。

## 快速检查

```bash
python -m py_compile scripts/main.py
python scripts/main.py --help
```

## 适用场景

- **医学文献翻译** — 期刊论文、综述、病例报告
- **国际学术合作** — 多语言团队沟通
- **临床试验文档** — 知情同意书、病例报告表翻译
- **病历翻译** — 多语言患者病历处理
- **医学教材本地化** — 教科书、培训材料翻译
- **医疗器械说明书** — 产品文档多语言版本

## 核心功能

### 1. 医学术语精准翻译

专注医学领域的术语翻译，而非通用翻译：
- 疾病名称（Disease names）
- 解剖结构（Anatomical terms）
- 药物名称（Drug names）
- 诊断程序（Diagnostic procedures）
- 手术名称（Surgical procedures）
- 实验室检查（Laboratory tests）

### 2. 多语言支持

支持主要医学语言对：
- **中文 ↔ 英文**（简体中文、繁体中文）
- **英文 ↔ 西班牙文**
- **英文 ↔ 法文**
- **英文 ↔ 德文**
- **英文 ↔ 日文**
- **英文 ↔ 阿拉伯文**

### 3. 上下文感知翻译

提供上下文可提高翻译准确性：
- 临床科室（心内科、神经科等）
- 文档类型（病历、论文、说明书）
- 目标受众（医生、患者、监管机构）

### 4. 缩写和全称处理

自动处理医学缩写：
- 保留或扩展缩写
- 提供缩写对应的全称
- 首次出现时注明

### 5. 术语一致性

确保同一术语在文档中翻译一致。

## 使用方法

```bash
# 基础翻译（英译中）
python scripts/main.py \
  --term "Acute Myocardial Infarction" \
  --source-lang en \
  --target-lang zh \
  --output translation.json

# 带上下文的翻译
python scripts/main.py \
  --term "Acute Myocardial Infarction" \
  --source-lang en \
  --target-lang zh \
  --context "cardiology, clinical diagnosis"

# 批量翻译
python scripts/main.py \
  --input terms.txt \
  --source-lang en \
  --target-lang zh \
  --output translations.json

# 段落翻译
python scripts/main.py \
  --text "Patient presents with chest pain and dyspnea..." \
  --source-lang en \
  --target-lang zh \
  --preserve-terms
```

## 命令参数

| 参数 | 类型 | 默认值 | 必需 | 说明 |
|------|------|--------|------|------|
| `--term` | string | — | 否 | 单个术语翻译 |
| `--text` | string | — | 否 | 段落文本翻译 |
| `--input` | string | — | 否 | 输入文件（批量翻译）|
| `--source-lang` | string | — | 是 | 源语言（en/zh/es/fr/de/ja/ar）|
| `--target-lang` | string | — | 是 | 目标语言 |
| `--context` | string | — | 否 | 上下文信息 |
| `--preserve-terms` | flag | false | 否 | 保留专业术语不翻译 |
| `--output` | string | stdout | 否 | 输出 JSON 文件路径 |

## 输入格式

### 单术语翻译

```bash
python scripts/main.py \
  --term "Hypertension" \
  --source-lang en \
  --target-lang zh
```

### 批量术语列表（terms.txt）

```
Acute Myeloid Leukemia
Type 2 Diabetes Mellitus
Congestive Heart Failure
Chronic Obstructive Pulmonary Disease
Rheumatoid Arthritis
```

### 医学文本段落

```bash
python scripts/main.py \
  --text "Patient is a 65-year-old male with history of hypertension and type 2 diabetes mellitus, presenting with chest pain..." \
  --source-lang en \
  --target-lang zh
```

## 输出格式

### 单术语翻译输出

```json
{
  "source_term": "Acute Myocardial Infarction",
  "source_lang": "en",
  "target_lang": "zh",
  "translations": [
    {
      "term": "急性心肌梗死",
      "abbreviation": "AMI",
      "pinyin": "Jíxìng xīnjī gěngsǐ",
      "confidence": "high",
      "category": "Cardiology/Disease",
      "synonyms": ["急性心梗", "心肌梗塞"]
    }
  ],
  "context": {
    "specialty": "Cardiology",
    "icd10": "I21",
    "mesh": "D009203"
  },
  "notes": "Standard term in Chinese cardiology literature"
}
```

### 批量翻译输出

```json
{
  "translation_id": "MT-20260814-001",
  "source_lang": "en",
  "target_lang": "zh",
  "total_terms": 5,
  "translations": [
    {
      "source": "Acute Myeloid Leukemia",
      "target": "急性髓系白血病",
      "abbreviation": "AML",
      "confidence": "high"
    },
    {
      "source": "Type 2 Diabetes Mellitus",
      "target": "2型糖尿病",
      "abbreviation": "T2DM",
      "confidence": "high"
    }
  ]
}
```

### 段落翻译输出

```json
{
  "source_text": "Patient is a 65-year-old male with history of hypertension...",
  "translated_text": "患者为65岁男性，有高血压病史...",
  "source_lang": "en",
  "target_lang": "zh",
  "medical_terms_identified": [
    {
      "term": "hypertension",
      "translation": "高血压",
      "position": [45, 57]
    }
  ],
  "confidence": "high"
}
```

## 翻译示例

### 示例 1：疾病名称

| 英文 | 中文 | 缩写 |
|-----|------|------|
| Acute Myocardial Infarction | 急性心肌梗死 | AMI |
| Type 2 Diabetes Mellitus | 2型糖尿病 | T2DM |
| Chronic Kidney Disease | 慢性肾脏病 | CKD |
| Rheumatoid Arthritis | 类风湿关节炎 | RA |
| Systemic Lupus Erythematosus | 系统性红斑狼疮 | SLE |

### 示例 2：解剖术语

| 英文 | 中文 |
|-----|------|
| Left Anterior Descending Artery | 左前降支 |
| Hippocampus | 海马体 |
| Coronary Sinus | 冠状窦 |
| Anterior Cruciate Ligament | 前交叉韧带 |
| Sinoatrial Node | 窦房结 |

### 示例 3：药物名称

| 通用名（英文）| 中文 | 商品名示例 |
|-------------|------|-----------|
| Atorvastatin | 阿托伐他汀 | Lipitor（立普妥）|
| Metformin | 二甲双胍 | Glucophage（格华止）|
| Lisinopril | 赖诺普利 | Zestril |
| Amlodipine | 氨氯地平 | Norvasc（络活喜）|
| Warfarin | 华法林 | Coumadin |

### 示例 4：实验室检查

| 英文 | 中文 | 缩写 |
|-----|------|------|
| Complete Blood Count | 全血细胞计数 | CBC |
| Hemoglobin A1c | 糖化血红蛋白 | HbA1c |
| Creatinine | 肌酐 | Cr |
| Alanine Aminotransferase | 丙氨酸氨基转移酶 | ALT |
| C-Reactive Protein | C反应蛋白 | CRP |

## 使用场景示例

### 场景 1：论文摘要翻译

**任务**：将英文论文摘要翻译为中文。

```bash
python scripts/main.py \
  --input abstract.txt \
  --source-lang en \
  --target-lang zh \
  --context "cardiology, clinical trial" \
  --preserve-terms \
  --output abstract_zh.json
```

**翻译策略**：
- 保留药物通用名（英文）
- 疾病名称使用标准中文术语
- 统计学术语保持一致
- 首次出现缩写时标注全称

### 场景 2：知情同意书本地化

**任务**：将临床试验知情同意书翻译为患者母语。

```bash
python scripts/main.py \
  --input consent_form_en.txt \
  --source-lang en \
  --target-lang zh \
  --context "patient-facing, regulatory" \
  --simplify-language \
  --output consent_form_zh.txt
```

**要求**：
- 使用患者友好语言
- 避免过度专业术语
- 关键术语需保留准确性
- 符合监管要求

### 场景 3：多语言病例报告表（CRF）

**任务**：为国际多中心临床试验制作多语言 CRF。

```bash
# 英译中
python scripts/main.py \
  --input crf_template_en.json \
  --source-lang en \
  --target-lang zh \
  --output crf_zh.json

# 英译西班牙文
python scripts/main.py \
  --input crf_template_en.json \
  --source-lang en \
  --target-lang es \
  --output crf_es.json
```

## 翻译质量保证

### 术语一致性检查

```python
from scripts.main import MedicalTranslator

translator = MedicalTranslator()

# 构建术语表
glossary = translator.build_glossary(
    source_documents=["doc1.txt", "doc2.txt"],
    source_lang="en",
    target_lang="zh"
)

# 使用术语表翻译
translator.set_glossary(glossary)
result = translator.translate_document("new_doc.txt")

# 检查一致性
consistency_report = translator.check_consistency(result)
```

### 回译验证（Back Translation）

```bash
# 正向翻译：英 → 中
python scripts/main.py \
  --input original_en.txt \
  --source-lang en \
  --target-lang zh \
  --output translated_zh.txt

# 回译：中 → 英
python scripts/main.py \
  --input translated_zh.txt \
  --source-lang zh \
  --target-lang en \
  --output back_translated_en.txt

# 比较原文和回译
diff original_en.txt back_translated_en.txt
```

## 翻译最佳实践

### 1. 提供上下文

**不佳**：
```bash
--term "cold"
```

**良好**：
```bash
--term "cold" --context "common cold, upper respiratory infection"
# 输出：感冒（而非"冷"）
```

### 2. 保留关键术语

对于药物通用名、基因名、蛋白质名，建议保留原文：

```bash
--preserve-terms "TP53,BRCA1,pembrolizumab"
```

### 3. 使用标准术语库

- **ICD-10** — 疾病分类
- **MeSH** — 医学主题词表
- **SNOMED CT** — 系统化医学术语
- **WHO-DD** — 药物术语

### 4. 专家审校

机器翻译后需要医学专家审校：
- 术语准确性
- 语法流畅性
- 文化适应性
- 监管合规性

## 常见翻译陷阱

### 1. 假朋友词（False Friends）

| 术语 | 易错翻译 | 正确翻译 |
|-----|---------|---------|
| Constipation | 便秘 | ✓ |
| （非"限制"） | ✗ |  |
| Stroke | 中风、卒中 | ✓ |
| （非"打击"） | ✗ |  |

### 2. 缩写歧义

| 缩写 | 可能含义 | 需上下文 |
|-----|---------|---------|
| MS | Multiple Sclerosis / Mitral Stenosis | ✓ |
| AS | Ankylosing Spondylitis / Aortic Stenosis | ✓ |
| RA | Rheumatoid Arthritis / Right Atrium | ✓ |

### 3. 方言差异

| 术语 | 大陆 | 台湾 | 香港 |
|-----|------|------|------|
| Chromosome | 染色体 | 染色體 | 染色體 |
| Virus | 病毒 | 病毒 | 病毒 |
| Diabetes | 糖尿病 | 糖尿病 | 糖尿病 |

## 监管合规性

### 临床试验翻译要求

- **ICH E6 GCP**：翻译文档需经验证
- **FDA**：关键文档需回译验证
- **EMA**：患者材料需母语审校

### 翻译文档记录

需保存：
- 原文版本
- 翻译版本
- 翻译人员资质
- 审校记录
- 版本变更历史

## 常见问题

**Q: 是否支持医学图像中的文字翻译？**  
A: 本工具处理文本翻译。图像中的文字需先 OCR 提取。

**Q: 如何处理罕见病名称？**  
A: 建议保留英文原名，括号内注明中文释义或音译。

**Q: 药物商品名是否翻译？**  
A: 建议保留原商品名，注明通用名的中文翻译。

**Q: 如何确保术语翻译符合当地医学习惯？**  
A: 需要本地医学专家审校，参考当地医学文献和指南。

## 注意事项

1. **机器翻译限制**：专业医学翻译仍需人工审校
2. **术语标准化**：优先使用权威术语库
3. **隐私保护**：翻译患者病历需去标识化
4. **文化适应**：注意不同地区的医学习惯差异
5. **法律责任**：翻译错误可能导致医疗风险

## 风险评估

| 风险指标 | 评估 | 级别 |
|---------|------|------|
| 代码执行 | Python 脚本本地执行 | 中 |
| 网络访问 | 可能调用外部翻译 API | 中 |
| 文件系统访问 | 读取输入，写入输出 | 中 |
| 指令篡改 | 标准提示指南 | 低 |
| 数据暴露 | 患者信息需去标识化 | 高 |

## 先决条件

无需安装额外依赖（仅使用 Python 标准库）。

可选增强：
```bash
pip install -r requirements.txt
```

可选依赖：
- googletrans（Google Translate API）
- openai（GPT 翻译）
- deep-translator（多翻译引擎）

## 生命周期状态

- **当前阶段**：Draft
- **下次审查日期**：2026-03-06
- **已知问题**：无
- **计划改进**：
  - 集成 MeSH 和 SNOMED CT 术语库
  - 支持更多语言对
  - 术语一致性自动检查
  - 翻译记忆库功能

## 相关资源

- [MeSH（Medical Subject Headings）](https://www.ncbi.nlm.nih.gov/mesh/)
- [SNOMED CT](https://www.snomed.org/)
- [ICD-10](https://www.who.int/standards/classifications/classification-of-diseases)
- [WHO Drug Dictionary](https://www.who.int/tools/atc-ddd-toolkit)
- [ICH E6(R2) GCP Guidelines](https://www.ich.org/page/efficacy-guidelines)

---

**⚠️ 医学免责声明：本工具仅供参考，专业医学翻译仍需人工审校。翻译错误可能导致医疗风险，使用者需自行承担责任。**
