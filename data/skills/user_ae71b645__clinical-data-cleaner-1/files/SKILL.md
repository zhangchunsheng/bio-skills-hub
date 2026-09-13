---
name: clinical-data-cleaner
description: 用于清洗临床试验数据、准备提交给 FDA/EMA 的数据、标准化 SDTM 数据集、处理临床研究中的缺失值、检测实验室结果中的异常值，或将原始 CRF 数据转换为 CDISC 格式。清洗并标准化临床试验数据，以满足带审计轨迹的监管合规要求。
license: MIT
skill-author: AIPOCH
displayName: "临床数据清洗"
version: "1.0.2"
slug: clinical-data-cleaner-1
---
# 临床数据清洗

清洗、验证并标准化临床试验数据，以满足向 FDA 或 EMA 监管申报所需的 CDISC SDTM 标准。

## 何时使用

- 当任务需要清洗临床试验数据、准备提交给 FDA/EMA 的数据、标准化 SDTM 数据集、处理临床研究中的缺失值、检测实验室结果中的异常值，或将原始 CRF 数据转换为 CDISC 格式时使用本技能。清洗并标准化临床试验数据，以满足带审计轨迹的监管合规要求。
- 用于需要明确假设、边界范围和可重现输出格式的数据分析任务。
- 当需要为缺失输入、执行错误或部分证据提供有文档记录的备用方案时使用本技能。

## 主要特性

- 围绕以下范围聚焦的工作流：用于清洗临床试验数据、准备提交给 FDA/EMA 的数据、标准化 SDTM 数据集、处理临床研究中的缺失值、检测实验室结果中的异常值，或将原始 CRF 数据转换为 CDISC 格式。清洗并标准化临床试验数据，以满足带审计轨迹的监管合规要求。
- 打包的可执行路径：`scripts/main.py`。
- `references/` 中提供了任务专用的参考资料。
- 结构化的执行路径，确保输出结果一致且可审查。

## 依赖项

- `Python`: `3.10+`。当前打包技能的仓库基线版本。
- `numpy`: `unspecified`。在 `requirements.txt` 中声明。
- `pandas`: `unspecified`。在 `requirements.txt` 中声明。
- `scipy`: `unspecified`。在 `requirements.txt` 中声明。

## 使用示例

```bash
cd "20260318/scientific-skills/Data Analytics/clinical-data-cleaner"
python -m py_compile scripts/main.py
python scripts/main.py --help
```

示例运行计划：
1. 确认用户输入、输出路径以及任何必需的配置值。
2. 如果脚本使用固定设置，编辑文件内的 `CONFIG` 块或文档中记录的参数。
3. 使用经过验证的输入运行 `python scripts/main.py`。
4. 检查生成的输出，并返回最终产物，同时说明所做的任何假设。

## 实施细节

相关细节参见上方的 `## Workflow`。

- 执行模型：验证请求、选择打包的工作流，并产出边界明确的可交付成果。
- 输入控制：在运行任何脚本之前，确认源文件、范围限制、输出格式和验收标准。
- 主要实现入口：`scripts/main.py`。
- 参考指导：`references/` 包含支持性的规则、提示或检查清单。
- 需要首先明确的参数：输入路径、输出路径、范围过滤条件、阈值以及任何领域特定的约束。
- 输出规范：保持结果可重现，明确说明假设，并避免未记录的副作用。

## 快速检查

在进行更深入的执行之前，使用此命令验证打包的脚本入口点是否可以被解析。

```bash
python -m py_compile scripts/main.py
```

## 审计就绪命令

使用以下具体命令进行验证。这些命令是自包含的，特意避免了占位路径。

```bash
python -m py_compile scripts/main.py
python scripts/main.py --help
python scripts/main.py --input "Audit validation sample with explicit symptoms, history, assessment, and next-step plan."
```

## 工作流程

1. 在进行详细工作之前，确认用户目标、必需输入以及不可协商的约束条件。
2. 验证请求是否符合已记录的范围，如果任务需要不受支持的假设，则提前停止。
3. 仅使用实际可用的输入，采用打包的脚本路径或文档记录的推理路径。
4. 返回一个结构化结果，将假设、可交付成果、风险和未解决事项分开列出。
5. 如果执行失败或输入不完整，切换到备用路径，并明确说明具体是什么阻碍了任务的完全完成。

## 快速开始

```python
from scripts.main import ClinicalDataCleaner

# Initialize for Demographics domain
cleaner = ClinicalDataCleaner(domain='DM')

# Clean data with default settings
cleaned = cleaner.clean(raw_data)

# Save with audit trail
cleaner.save_report('output.csv')
```

## 核心能力

### 1. SDTM 领域验证

```python
cleaner = ClinicalDataCleaner(domain='DM')  # or 'LB', 'VS'
is_valid, missing = cleaner.validate_domain(data)
```

**必需字段：**
- **DM**：STUDYID、USUBJID、SUBJID、RFSTDTC、RFENDTC、SITEID、AGE、SEX、RACE
- **LB**：STUDYID、USUBJID、LBTESTCD、LBCAT、LBORRES、LBORRESU、LBSTRESC、LBDTC
- **VS**：STUDYID、USUBJID、VSTESTCD、VSORRES、VSORRESU、VSSTRESC、VSDTC

### 2. 缺失值处理

```python
cleaner = ClinicalDataCleaner(
    domain='DM',
    missing_strategy='median'  # mean, median, mode, forward, drop
)
cleaned = cleaner.handle_missing_values(data)
```

### 3. 异常值检测

```python
cleaner = ClinicalDataCleaner(
    domain='LB',
    outlier_method='domain',  # iqr, zscore, domain
    outlier_action='flag'     # flag, remove, cap
)
flagged = cleaner.detect_outliers(data)
```

**临床阈值：**
| 参数 | 范围 | 单位 |
|-----------|-------|------|
| Glucose | 50-500 | mg/dL |
| Hemoglobin | 5-20 | g/dL |
| Systolic BP | 70-220 | mmHg |

### 4. 日期标准化

```python
standardized = cleaner.standardize_dates(data)

# Converts to ISO 8601: 2023-01-15T09:30:00
```

### 5. 完整流程

```python
cleaner = ClinicalDataCleaner(
    domain='DM',
    missing_strategy='median',
    outlier_method='iqr',
    outlier_action='flag'
)
cleaned_data = cleaner.clean(data)
cleaner.save_report('output.csv')
```

**输出文件：**
- `output.csv` - 清洗后的 SDTM 数据
- `output.report.json` - 用于监管申报的审计轨迹

## 命令行用法

```text

# Clean demographics
python scripts/main.py \
  --input dm_raw.csv \
  --domain DM \
  --output dm_clean.csv \
  --missing-strategy median \
  --outlier-method iqr \
  --outlier-action flag

# Clean lab data with clinical thresholds
python scripts/main.py \
  --input lb_raw.csv \
  --domain LB \
  --output lb_clean.csv \
  --outlier-method domain
```

## 常见模式

详细示例参见 [references/common-patterns.md](references/common-patterns.md)：
- 监管申报准备
- 中期分析数据准备
- 数据库迁移清理
- 外部实验室数据整合

## 故障排除

解决方案参见 [references/troubleshooting.md](references/troubleshooting.md)：
- 验证失败
- 日期解析错误
- 大型数据集的内存错误
- 异常值检测问题

## 质量检查清单

**清洗前：**
- [ ] 已获得 IACUC 批准（动物研究）
- [ ] 样本量具备充分的把握度
- [ ] 随机化方法已有文档记录

**清洗后：**
- [ ] 根据 CDISC SDTM IG 进行验证
- [ ] 查阅审计轨迹中的所有清洗操作
- [ ] 测试导入分析软件

## 参考资料

- `references/sdtm_ig_guide.md` - CDISC SDTM 实施指南
- `references/domain_specs.json` - 领域特定字段要求
- `references/outlier_thresholds.json` - 临床异常值阈值
- `references/common-patterns.md` - 详细使用模式
- `references/troubleshooting.md` - 问题解决指南

---

**Skill ID**: 189 | **Version**: 2.0 | **License**: MIT

## 输出要求

每个最终回复在相关时都应明确包含以下内容：

- 目标或所需的可交付成果
- 使用的输入及引入的假设
- 工作流程或决策路径
- 核心结果、建议或产物
- 约束条件、风险、注意事项或验证需求
- 未解决事项及后续检查

## 错误处理

- 如果缺少必需输入，明确说明具体缺少哪些字段，并仅请求所需的最少额外信息。
- 如果任务超出文档记录的范围，应停止，而不是猜测或悄悄扩大任务范围。
- 如果 `scripts/main.py` 执行失败，报告失败点，总结仍可安全完成的部分，并提供手动备用方案。
- 不要编造文件、引用、数据、搜索结果或执行结果。

## 输入验证

本技能接受符合 `clinical-data-cleaner` 文档记录用途,并包含足够上下文以安全完成工作流的请求。

当请求超出范围、缺少关键输入,或需要不受支持的假设时,不要继续执行工作流。而应回复：

> `clinical-data-cleaner` 仅处理其文档记录的工作流。请提供缺失的必需输入,或切换到更合适的技能。

## 回复模板

对于非简单请求，使用以下固定结构：

1. 目标
2. 收到的输入
3. 假设
4. 工作流程
5. 可交付成果
6. 风险与限制
7. 后续检查

如果请求较简单，可以压缩结构，但在影响正确性时仍需明确说明假设和限制。
