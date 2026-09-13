---
slug: medical-scribe-dictation
displayName: 医疗口述转结构化病历
version: 1.1.0
description: 将医生口述内容转换为结构化的 SOAP（主观资料/客观资料/评估/计划）病历。适用于处理医生口述转录文本、规范医学术语、生成标准格式病历、进行病历完整性质量检查等场景。以下场景也会触发本技能："把这段口述转成 SOAP 病历""帮我整理这段问诊记录""生成结构化病历""医学术语规范化"。
license: MIT
author: AIPOCH
---

# 医疗口述转结构化病历

将非结构化的医生口述内容转换为专业格式的 SOAP（Subjective 主观资料、Objective 客观资料、Assessment 评估、Plan 计划）病历，包含医学术语规范化和临床质量检查。

## 适用场景

- 将医生口述的问诊/查体内容转换为结构化 SOAP 病历
- 需要对病历文本中的常见医学缩写进行展开规范化时
- 需要对生成的病历做完整性检查（是否缺少主诉、评估、计划等必需部分）时

## 功能特性

- **文本处理**：接收已转录的文本，或读取文本文件
- **SOAP 结构生成**：自动将临床内容归类到标准分区
- **医学术语处理**：规范化缩写、提取常见药物名称、提取生命体征
- **临床质量检查**：标记缺失的必需要素
- **多专科模板**：`references/soap-templates.md` 提供内科、急诊、心内科、儿科、外科、精神科、妇产科、骨科等专科模板参考

## 已实现能力（脚本真实行为）

脚本 `scripts/main.py` 实际实现的是**基于规则的文本解析**，并非语音识别或大语言模型智能抽取：

- 通过正则表达式从文本中提取主诉、评估/诊断、治疗计划等片段
- 通过关键词模式提取血压、心率、呼吸频率、血氧饱和度、体温
- 通过内置的约 30 条缩写词典（`MedicalTerminologyProcessor.ABBREVIATIONS`，硬编码在脚本内，与 `references/medical-abbreviations.json` 中收录的约 2000 条术语表是两套独立数据，脚本不会读取该 JSON 文件）展开文本中的常见医学缩写
- 若安装了 `openai` 或 `anthropic` 库并通过 `--llm` 指定提供方，则会调用相应大语言模型做更智能的结构化抽取；未安装或未指定时自动降级为规则解析
- 若提供 `--audio` 且已安装 `openai-whisper`，可将音频转写为文本后再处理；否则会报错并提示安装该依赖

## 命令行用法

```bash
# 处理已转录文本（直接传入字符串）
python scripts/main.py --input "患者主诉：胸痛。血压 130/85，心率 90。评估：稳定型心绞痛。计划：继续现有用药。"

# 处理文本文件
python scripts/main.py --input dictation.txt --output note.md

# 处理音频文件（需先安装 openai-whisper）
python scripts/main.py --audio consultation.wav --output note.md

# 指定专科（仅作为元数据记录在输出中，不影响解析逻辑）
python scripts/main.py --input dictation.txt --specialty cardiology

# 输出为 JSON 而非 Markdown
python scripts/main.py --input dictation.txt --format json

# 使用大语言模型进行智能抽取（需安装并配置 openai 或 anthropic）
python scripts/main.py --input dictation.txt --llm anthropic

# 从标准输入读取
cat dictation.txt | python scripts/main.py
```

## 参数说明

| 参数 | 简写 | 是否必填 | 说明 |
|------|------|----------|------|
| `--input` | `-i` | 否 | 待处理的文本，或指向文本文件的路径。与 `--audio` 二选一；两者都未提供时从标准输入读取 |
| `--audio` | `-a` | 否 | 音频文件路径（需安装 `openai-whisper`） |
| `--output` | `-o` | 否 | 输出文件路径；未提供时打印到标准输出 |
| `--specialty` | `-s` | 否 | 医学专科名称，默认 `general`，仅作元数据记录，不改变解析规则 |
| `--llm` | — | 否 | 可选值 `openai` / `anthropic`，指定后启用大语言模型智能抽取 |
| `--format` | — | 否 | 输出格式，`markdown`（默认）或 `json` |

## 前置条件

```bash
pip install -r requirements.txt
```

`requirements.txt` 中列出的 `anthropic`、`openai`、`whisper` 均为可选依赖——脚本对它们做了 try/except 优雅降级处理，未安装时基础的规则解析功能仍可正常使用；`dataclasses` 是 Python 3.7+ 标准库内置模块，无需单独安装（该文件在 Python 3.6 及更早版本上才需要回填包，正常环境下无需理会）。

若需要音频转写功能，还需另外安装 `openai-whisper`（`pip install openai-whisper`）。

## 参考文件

- `references/soap-templates.md` —— 按专科（内科、急诊、心内科、儿科、外科、精神科、妇产科、骨科）整理的 SOAP 病历模板，供人工撰写或校对时参考
- `references/example-cases.md` —— 5 个完整的"口述文本 → 期望 SOAP 输出"示例，覆盖内科随访、急诊胸痛、儿科体检、骨科运动损伤、精神科随访
- `references/terminology-sources.md` —— 医学术语标准与编码体系介绍（SNOMED CT、ICD-10、LOINC、RxNorm、CPT 等），供了解术语规范化背景时参考，脚本本身不直接调用这些外部编码系统
- `references/medical-abbreviations.json` —— 约 2000 条医学缩写对照表（按首字母分组，英文缩写 → 英文全称）。**注意：这是一份独立的参考数据文件，脚本当前不会读取或使用它**；考虑到词条数量庞大且为纯数据性质的英文术语对照，本次本地化保留其原始英文内容未做翻译，仅在此说明其用途和真实使用状态

## 安全说明

⚠️ **需要临床审核**：所有生成的病历在正式录入病历系统前，必须经主诊医师审核确认。

⚠️ **无诊断能力**：本工具只负责整理结构化临床信息，不提供诊断建议。

## 错误处理

- 若既未提供 `--input` 也未提供 `--audio`，且标准输入为空，脚本会打印 `Error: No input provided` 并以状态码 1 退出。
- 若指定了 `--audio` 但未安装 `openai-whisper`，脚本会抛出提示安装该依赖的错误。
- 若指定了 `--llm` 但对应的大语言模型调用失败（例如未配置 API key），脚本会捕获异常并自动降级为规则解析，同时打印警告信息，不会中断执行。
- 若任务超出本技能记录的范围，应停止处理并说明，而不是猜测或悄悄扩大任务范围。
- 不要编造患者数据、检验结果或病历内容。

## 已知局限

- 医学术语识别的准确性依赖于输入文本的清晰程度
- 表述含糊的口述内容可能需要人工澄清
- 建议在最终确认前对药物名称进行核实
- 不能替代医生对病历的最终审核，尤其在危重病例中
