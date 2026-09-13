---
name: 医学分析推理
description: >-
  Aggregated medical AI skill pack for WorkBuddy. Entry point that indexes sub-skills; currently contains medgemma-medical-analysis, which performs multimodal medical analysis (chest X-ray with longitudinal comparison, CT/MRI slices, pathology WSI patches, dermatology, fundus, anatomical localization, lab report extraction, EHR interpretation, clinical reasoning, report generation) through the user's NewAPI relay serving Google MedGemma 1.5 4B. Use when the user asks to interpret medical images or clinical text, extract structured data from lab reports, or answer clinical reasoning questions, and a NewAPI endpoint serving medgemma-1.5-4b-it is available. 聚合医疗 AI 技能包（Medical Skills）：通过调用NewAPI服务调用 Google MedGemma 1.5 4B 进行多模态医疗分析，支持胸片（含纵向对比）、CT/MRI 切片、病理切片、皮肤影像、眼底影像、解剖定位、化验单结构化提取、EHR/病历解读、临床推理与医学报告生成；当用户请求解读医学影像或临床文本、提取化验单结构化数据或回答临床推理问题时使用，需要可用的 medgemma-1.5-4b-it 模型端点。
license: MIT
allowed-tools: Bash,Read,Write
metadata:
  runtime: node >= 18
---

# Medical Skills（聚合技能包）

本技能包是多个医疗 AI 子技能的聚合入口。本文件是唯一入口，WorkBuddy 只加载此 SKILL.md；子技能的指令文件已改名（非 SKILL.md），不会被重复识别为独立技能。

## 子技能索引

| 子技能 | 模块文件 | 触发条件 | 能力 |
| --- | --- | --- | --- |
| medgemma-medical-analysis | medgemma-medical-analysis/MODULE.md | 医学影像分析、化验单提取、EHR/病历解读、临床推理、医学报告生成 | 通过 NewAPI 调用 MedGemma 1.5 4B 多模态医疗分析 |

## 模型能力概述（Google MedGemma 1.5 4B）

- **多模态医学模型**：基于 Gemma 3 架构的 decoder-only Transformer，SigLIP 图像编码器经去标识化医学数据预训练（胸片、皮肤、眼底、病理等），专为医学文本与图像理解设计。
- **图像输入**：图像归一化至 896x896，每张编码为 256 tokens；单次最多 4 张（多图用于纵向对比、病理多 patch 场景）。
- **上下文与输出**：上下文 ≥128K tokens，单次输出上限 8192 tokens，足以承载整段病历或完整结构化报告。
- **医学专项能力**：3D CT/MRI 体积解读（按切片预处理传入）、全切片病理（WSI）多 patch 解读、纵向胸片对比（进展/改善/新发）、胸片解剖定位（bounding box，坐标归一化 0-1000）、化验单/检验报告结构化提取、EHR 理解、医学文本推理（MedQA ≈69.1）、医学报告生成。
- **部署形态**：4B 参数、计算高效，适合本地/私有化部署；通过用户自建 NewAPI 服务提供 OpenAI 兼容的 `medgemma-1.5-4b-it` 接口。

## 使用前提

1. 用户提供可用的 NewAPI 中转站地址（baseUrl）与 API Key，且中转站已提供 `medgemma-1.5-4b-it` 模型（模型名以中转站为准，可在配置中指定 `model` 或调用时用 `--model` 覆盖；可用 `--ping` 查看可用模型）。
2. 首次使用前运行配置脚本（见 MODULE.md「配置流程」）；API Key 保存在用户本机配置文件，不写入对话或日志。
3. 医学影像需为脚本支持的格式（PNG/JPEG/WebP/GIF/BMP/TIFF）；DICOM、视频、3D 体数据需先通过 scripts/prepare-image.js 或其他工具预处理为普通图像再传入。

## 执行流程

1. 判断用户请求属于哪个子技能（见上表触发条件）；无法确定时先询问用户。
2. Read 对应子技能的 MODULE.md 文件，按其指令执行。
3. 调用 `node scripts/medgemma.js`，传入 `--task`、图像/文本与 `--question`。
4. 脚本只输出 JSON；将其转换为简洁的中文回复给用户，并附免责声明。
5. 需要落盘报告时使用 `--output`，按 assets/medical-report-template.md 模板生成。

## 输出约定

- 回复必须报告：使用的模型、任务类型、关键发现。
- 所有结果仅供医学研究、教学与辅助参考，不可作为临床诊断依据；回复附免责声明：最终诊断请以执业医师意见为准。
- 不提供治疗建议；涉及用药、手术等决策时建议用户咨询执业医师。

## 限制说明

- 官方评测以单图任务为主；多图理解（纵向对比、WSI 多 patch）为 1.5 新增能力，未经全面评测，结果需谨慎对待。
- 模型对 prompt 较敏感，建议使用 MODULE.md 中的任务模板与内置系统提示词，避免随意改写指令。
- 图像会以 base64 或 URL 形式发送至用户配置的 NewAPI 服务；患者数据发送前请脱敏。

## 当前子技能

只有 medgemma-medical-analysis 一个子技能：通过用户自建 NewAPI 服务调用 Google MedGemma 1.5 4B 进行医疗分析，支持胸片（含纵向对比）、CT/MRI 切片、病理切片、皮肤影像、眼底影像、解剖定位、化验单结构化提取、EHR 解读、临床推理与报告生成。

For detailed instructions, refer to medgemma-medical-analysis/MODULE.md
