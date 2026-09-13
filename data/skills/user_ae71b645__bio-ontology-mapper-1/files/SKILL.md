---
name: bio-ontology-mapper
description: 将非结构化生物医学文本映射到标准化本体（SNOMED CT等）
license: MIT
skill-author: AIPOCH
version: "1.0.1"
slug: bio-ontology-mapper-1
displayName: "生物本体映射器"
---
# 生物本体映射器

## 使用场景

- 当任务是将非结构化生物医学文本映射到标准化本体（SNOMED CT等）时使用此技能
- 当证据洞察任务需要明确的假设、明确的范围和可重现的输出格式时使用此技能
- 当需要针对缺失输入、执行错误或部分证据提供有记录的备用路径时使用此技能

## 核心特性

- 与以下目标一致的范围聚焦工作流：将非结构化生物医学文本映射到标准化本体（SNOMED CT等）
- 打包的可执行路径：`scripts/main.py`
- `references/` 中提供的参考材料用于任务特定指导
- 结构化的执行路径设计用于保持输出的一致性和可审查性

## 依赖项

- `Python`: `3.10+`。当前打包技能的存储库基线
- `dataclasses`: `unspecified`。在 `requirements.txt` 中声明
- `difflib`: `unspecified`。在 `requirements.txt` 中声明

## 使用示例

```bash
cd "20260318/scientific-skills/Evidence Insight/bio-ontology-mapper"
python -m py_compile scripts/main.py
python scripts/main.py --help
```

示例运行计划：
1. 确认用户输入、输出路径以及任何所需的配置值
2. 如果脚本使用固定设置，请编辑文件内的 `CONFIG` 块或记录的参数
3. 使用验证的输入运行 `python scripts/main.py`
4. 审查生成的输出并返回最终成果，并指出任何假设

## 实现细节

有关相关详细信息，请参见上面的 `## 工作流`。

- 执行模型：验证请求，选择打包的工作流，并生成有界的交付成果
- 输入控制：在运行任何脚本之前确认源文件、范围限制、输出格式和接受标准
- 主要实现界面：`scripts/main.py`
- 参考指导：`references/` 包含支持规则、提示或检查清单
- 首先需要澄清的参数：输入路径、输出路径、范围过滤器、阈值以及任何领域特定的约束
- 输出纪律：保持结果可重现，明确识别假设，并避免未记录的副作用

## 快速检查

使用此命令在深入执行之前验证打包脚本入口点是否可以解析。

```bash
python -m py_compile scripts/main.py
```

## 审计就绪命令

使用这些具体命令进行验证。它们故意是自包含的，避免占位符路径。

```bash
python -m py_compile scripts/main.py
python scripts/main.py --help
```

## 工作流

1. 在进行详细工作之前确认用户目标、所需输入和不可协商的约束
2. 验证请求是否与记录的范围匹配，如果任务需要不支持的假设则提前停止
3. 仅使用实际可用的输入使用打包的脚本路径或记录的推理路径
4. 返回一个结构化的结果，将假设、交付成果、风险和未解决的项目分开
5. 如果执行失败或输入不完整，切换到备用路径并准确说明阻止完全完成的原因

## 概述

生物医学术语标准化工具，将自由文本临床和科学概念映射到标准化本体，以实现语义互操作性和数据协调。

**核心能力：**
- **多本体支持**：SNOMED CT、MeSH、ICD-10、LOINC、RxNorm
- **实体提取**：疾病、症状、程序、药物的命名实体识别
- **模糊匹配**：处理拼写错误、缩写和同义词
- **置信度评分**：每个映射的可靠性指标
- **批处理**：高效标准化大型数据集
- **交叉映射**：在本体系统之间进行转换

## 核心功能

### 1. 实体识别与映射

提取生物医学实体并映射到本体：

```python
from scripts.mapper import BioOntologyMapper

mapper = BioOntologyMapper()

# Map clinical text
result = mapper.map_text(
    text="Patient has diabetes and hypertension, taking metformin",
    ontologies=["snomed", "mesh", "rxnorm"],
    confidence_threshold=0.7
)

for entity in result.entities:
    print(f"{entity.text} → {entity.concept_id} ({entity.ontology})")
    print(f"  Preferred: {entity.preferred_term}")
    print(f"  Confidence: {entity.confidence:.2f}")
```

**支持的本体：**
| 本体 | 领域 | 用例 |
|----------|--------|----------|
| **SNOMED CT** | 临床 | 电子健康记录互操作性 |
| **MeSH** | 文献 | PubMed索引 |
| **ICD-10** | 计费 | 诊断代码 |
| **LOINC** | 实验室 | 检测结果标准化 |
| **RxNorm** | 药物 | 药物标准化 |
| **HGNC** | 基因 | 基因名称标准化 |

### 2. 交叉本体转换

在不同本体之间映射概念：

```python

# Cross-map SNOMED to ICD-10
translation = mapper.cross_map(
    source_id="22298006",  # SNOMED: Myocardial infarction
    source_ontology="snomed",
    target_ontology="icd10"
)

print(f"ICD-10: {translation.target_id} - {translation.target_term}")

# Output: I21.9 - Acute myocardial infarction, unspecified
```

**交叉映射覆盖范围：**
- SNOMED CT ↔ ICD-10-CM（临床修订版）
- MeSH ↔ SNOMED CT（文献到临床）
- RxNorm ↔ ATC（药物分类）
- LOINC ↔ SNOMED（实验室到临床）

### 3. 批量标准化

处理大型数据集：

```python

# Batch process CSV
results = mapper.batch_map(
    input_file="clinical_terms.csv",
    text_column="diagnosis_description",
    ontologies=["snomed", "icd10"],
    output_format="csv",
    max_workers=4
)

# Results include:

# - Original term

# - Mapped concept ID

# - Confidence score

# - Alternative mappings (if ambiguous)
```

**性能：**
- 约100个术语/秒（带缓存）
- 约20个术语/秒（API查询）
- 大型数据集的并行处理

### 4. 置信度评分与验证

评估映射可靠性：

```python
scoring = mapper.score_mapping(
    term="heart attack",
    candidate="22298006",  # Myocardial infarction
    factors=["string_similarity", "context_match", "frequency"]
)

print(f"Overall confidence: {scoring.confidence:.2f}")
print(f"Breakdown: {scoring.factors}")
```

**评分因素：**
- **字符串相似度**：Levenshtein距离、n-gram
- **上下文匹配**：周围词对齐
- **频率**：语料库中的常见用法
- **语义相似度**：向量嵌入

## 质量检查清单

**映射前：**
- [ ] 文本已预处理（小写、标点符号已处理）
- [ ] 尽可能扩展缩写
- [ ] 已识别语言（多语言支持）

**映射期间：**
- [ ] 置信度阈值适当（临床应用>0.7）
- [ ] 对于歧义术语考虑多个候选项
- [ ] 使用上下文进行消歧

**映射后：**
- [ ] 标记低置信度映射以供审查
- [ ] 记录未映射的术语
- [ ] **关键**：对于高风险使用进行临床专家验证

**生产前：**
- [ ] 在黄金标准上验证映射准确性
- [ ] 假阳性率可接受（<5%）
- [ ] 召回率对于用例可接受（>90%）
- [ ] 遵守API速率限制

## 常见陷阱

**映射错误：**
- ❌ **缩写歧义** → "MI" = 心肌梗死或密歇根州
  - ✅ 使用上下文；标记以供人工审查

- ❌ **过时术语** → 旧术语不在当前本体中
  - ✅ 使用历史映射；更新术语

- ❌ **错误置信度** → 错误概念的高分数
  - ✅ 始终审查前3个候选项

**技术问题：**
- ❌ **API失败** → 没有本地备用
  - ✅ 实现缓存；使用本地参考文件

- ❌ **版本不匹配** → 不同的本体版本
  - ✅ 跟踪使用的本体版本

- ❌ **PHI暴露** → 将患者数据发送到外部API
  - ✅ API调用前去标识化；尽可能使用本地处理

## 参考资料

`references/` 目录中提供：

- `snomed_ct_guide.md` - SNOMED CT层次结构和关系
- `mesh_structure.md` - MeSH树结构和限定符
- `ontology_mappings.md` - 系统之间的交叉引用
- `nlp_best_practices.md` - 生物医学文本处理
- `api_documentation.md` - 外部服务集成
- `validation_datasets.md` - 黄金标准测试集

## 脚本

位于 `scripts/` 目录：

- `main.py` - 映射的命令行界面
- `mapper.py` - 核心本体映射引擎
- `extractor.py` - 命名实体识别
- `cross_mapper.py` - 本体到本体的转换
- `scorer.py` - 置信度计算
- `batch_processor.py` - 大型数据集处理
- `validator.py` - 映射质量检查
- `caching.py` - 频繁查询的本地存储

## 限制

- **歧义性**：多对多映射很常见；需要上下文
- **覆盖范围**：罕见疾病和新概念可能不在本体中
- **版本控制**：本体更新可能随时间改变映射
- **语言**：对英语支持最好；其他语言有限
- **实时性**：不适用于时间关键的临床应用
- **API依赖**：大多数查询需要互联网（缓存有帮助）

---

**⚠️ 关键提示：本体映射用于研究和数据整合，而非临床决策。在患者护理环境中使用之前，始终与领域专家验证映射。未经适当的去标识化和合规措施，切勿处理PHI。**

## 参数

| 参数 | 类型 | 默认值 | 描述 |
|-----------|------|---------|-------------|
| `--term` | str | 必需 | 要映射的单个术语 |
| `--input` | str | 必需 | 输入文件路径 |
| `--output` | str | 必需 | 输出文件路径 |
| `--ontology` | str | 'both' |  |
| `--threshold` | float | 0.7 |  |
| `--format` | str | 'json' |  |
| `--use-api` | str | 必需 | 使用UMLS/MeSH API |
| `--api-key` | str | 必需 |  |

## 输出要求

当相关时，每个最终响应都应明确这些项目：

- 目标或请求的交付成果
- 使用的输入和引入的假设
- 工作流或决策路径
- 核心结果、建议或成果
- 约束、风险、警告或验证需求
- 未解决的项目和下一步检查

## 错误处理

- 如果缺少必需的输入，请准确说明缺少哪些字段，并仅请求最少的附加信息
- 如果任务超出记录的范围，请停止而不是猜测或悄悄扩大任务
- 如果 `scripts/main.py` 失败，报告失败点，总结仍然可以安全完成的内容，并提供手动备用方案
- 不要伪造文件、引用、数据、搜索结果或执行结果

## 输入验证

此技能接受与 `bio-ontology-mapper` 记录的目的相匹配并包含足够上下文以安全完成工作流的请求。

当请求超出范围、缺少关键输入或需要不支持的假设时，不要继续工作流。而是响应：

> `bio-ontology-mapper` 仅处理其记录的工作流。请提供缺少的必需输入或切换到更合适的技能。

## 响应模板

对于非平凡的请求，使用以下固定结构：

1. 目标
2. 接收的输入
3. 假设
4. 工作流
5. 交付成果
6. 风险和限制
7. 下一步检查

如果请求很简单，您可以压缩结构，但在影响正确性时仍然明确说明假设和限制。
